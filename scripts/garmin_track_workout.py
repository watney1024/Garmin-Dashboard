# -*- coding: utf-8 -*-
"""
garmin_track_workout.py — build & schedule a TRACK (操场) interval session on
Garmin, where **the watch distance is decoupled from the lap button**.

Why this exists
---------------
Garmin's normal running workouts measure by GPS/time. On a real track that is
wrong: the physical lap is not exactly 400 m, so a "2 laps = 800 m" step drifts
from the actual distance. Garmin's own answer is the **lap button**: a step whose
end condition is ``lap.button`` ends when you press the lap key, and the step is
treated as a nominal distance. That is what this script builds.

So the runner's only job on the watch is: **press the lap key once per 400 m,
and once more when the rest is over.** The session is then judged by lap *times*,
never by GPS distance (see docs/02 §6 for the analysis pitfall).

Session model (see scripts/track_spec.example.json)
---------------------------------------------------
  warmup        : N laps of 400 m    (lap.button)  [+ optional HR target]
  pre-rest      : time               (e.g. 6 min)
  sets          : S times [ K laps of 400 m (lap.button) + rest ]
  cooldown      : N laps of 400 m    (optional)

Rest style matters: ``rest`` = complete rest (standing still), ``recovery`` =
active recovery (slow jog). Pick the one the session actually uses.

Idempotent: created workouts are cached name -> workout_id in
<data_dir>/garmin_workout_registry.json, so re-running only re-schedules.

Config: same env vars as garmin_pull.py / garmin_schedule.py (see docs/01).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

# Garmin DTO ids (workout API, NOT the activity API). See docs/01 §3.
STEP = {"warmup": 1, "cooldown": 2, "interval": 3, "recovery": 4, "rest": 5, "repeat": 6}
END = {"lap.button": 1, "time": 2, "distance": 3, "iterations": 7}
TARGET = {"no.target": 1, "heart.rate.zone": 4}
SPORT_RUNNING = {"sportTypeId": 1, "sportTypeKey": "running"}
NO_TARGET = {"workoutTargetTypeId": TARGET["no.target"], "workoutTargetTypeKey": "no.target"}


def load_dotenv():
    for path in (os.path.join(os.getcwd(), ".env"),
                 os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")):
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                k, v = k.strip(), v.strip().strip("\"'")
                os.environ.setdefault(k, v)


def load_reg(path):
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_reg(path, reg):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=1)
        f.write("\n")


class MCP:
    """Minimal MCP-over-stdio client (same shape as garmin_pull.py)."""

    def __init__(self, cfg):
        cmd = [cfg.uvx, "--python", cfg.pyver, "--from", cfg.src, "garmin-mcp"]
        env = dict(os.environ)
        env.update({"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"})
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, env=env, text=True,
                                  bufsize=1, encoding="utf-8", errors="replace")
        self._rid = [0]

    def _send(self, o):
        self.p.stdin.write(json.dumps(o) + "\n")
        self.p.stdin.flush()

    def _recv(self, timeout):
        deadline = time.time() + timeout
        while time.time() < deadline:
            line = self.p.stdout.readline()
            if not line:
                break
            try:
                return json.loads(line)
            except Exception:
                continue
        return None

    def connect(self):
        self._send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "2024-11-05", "capabilities": {},
            "clientInfo": {"name": "garmin-track", "version": "1.0"}}})
        self._recv(150)
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})

    def call(self, name, args, timeout=150):
        self._rid[0] += 1
        self._send({"jsonrpc": "2.0", "id": self._rid[0], "method": "tools/call",
                    "params": {"name": name, "arguments": args}})
        r = self._recv(timeout)
        if not r or "result" not in r:
            return {"error": True, "raw": "no response from server"}
        c = r["result"].get("content", [])
        txt = c[0]["text"] if c else ""
        try:
            return json.loads(txt)
        except Exception:
            return {"error": bool(r["result"].get("isError")), "raw": txt[:300]}

    def close(self):
        try:
            self.p.kill()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# spec -> Garmin DTO
# ---------------------------------------------------------------------------
def _lap_step(order, step_key, desc, hr=None):
    st = {"type": "ExecutableStepDTO", "stepOrder": order,
          "stepType": {"stepTypeId": STEP[step_key], "stepTypeKey": step_key},
          "description": desc,
          "endCondition": {"conditionTypeId": END["lap.button"],
                           "conditionTypeKey": "lap.button"},
          "endConditionValue": 1000.0,
          "targetType": NO_TARGET}
    if hr:
        st["description"] = "%s（HR %d–%d）" % (desc, hr[0], hr[1])
        st["targetType"] = {"workoutTargetTypeId": TARGET["heart.rate.zone"],
                            "workoutTargetTypeKey": "heart.rate.zone"}
        st["targetValueOne"] = float(hr[0])
        st["targetValueTwo"] = float(hr[1])
    return st


def _time_step(order, step_key, minutes, desc):
    return {"type": "ExecutableStepDTO", "stepOrder": order,
            "stepType": {"stepTypeId": STEP[step_key], "stepTypeKey": step_key},
            "description": desc,
            "endCondition": {"conditionTypeId": END["time"], "conditionTypeKey": "time"},
            "endConditionValue": float(minutes) * 60.0,
            "targetType": NO_TARGET}


def _repeat(order, n, steps, desc=None):
    d = {"type": "RepeatGroupDTO", "stepOrder": order,
         "stepType": {"stepTypeId": STEP["repeat"], "stepTypeKey": "repeat"},
         "numberOfIterations": int(n),
         "endCondition": {"conditionTypeId": END["iterations"],
                          "conditionTypeKey": "iterations"},
         "endConditionValue": float(n),
         "workoutSteps": steps}
    if desc:
        d["description"] = desc
    return d


def build(spec):
    """Turn a human track spec into Garmin workout JSON.

    stepOrder must be strictly increasing across the whole segment: a repeat
    group takes one slot, then its children take the following slots.
    """
    lap = int(spec.get("lap_meters", 400))
    rest_style = spec.get("rest_style", "rest")
    if rest_style not in ("rest", "recovery"):
        raise SystemExit("rest_style must be 'rest' (standing) or 'recovery' (jog)")

    steps = []
    c = [0]

    def nxt():
        c[0] += 1
        return c[0]

    warm = spec.get("warmup") or {}
    if warm.get("laps"):
        hr = ((warm["hr_min"], warm["hr_max"])
              if warm.get("hr_min") and warm.get("hr_max") else None)
        grp = nxt()
        inner = _lap_step(nxt(), "warmup",
                          "%dm 计圈（%d × %dm 热身）" % (lap, warm["laps"], lap), hr)
        steps.append(_repeat(grp, warm["laps"], [inner],
                             desc="热身 = %d × %dm = %.2f km"
                                  % (warm["laps"], lap, warm["laps"] * lap / 1000.0)))

    if spec.get("pre_rest_min"):
        steps.append(_time_step(nxt(), "rest", spec["pre_rest_min"],
                                "休息 %s min（%s）"
                                % (spec["pre_rest_min"],
                                   "静止" if rest_style == "rest" else "慢跑")))

    if spec.get("sets"):
        k = int(spec["laps_per_set"])
        grp = nxt()
        inner = [_lap_step(nxt(), "interval", "%dm 计圈 · 第%d圈" % (lap, i + 1))
                 for i in range(k)]
        if spec.get("set_rest_min"):
            inner.append(_time_step(
                nxt(), rest_style, spec["set_rest_min"],
                "组间%s %s min" % ("静止休息" if rest_style == "rest" else "慢跑",
                                 spec["set_rest_min"])))
        steps.append(_repeat(grp, spec["sets"], inner,
                             desc="%d 组 × %d × %dm" % (spec["sets"], k, lap)))

    cool = spec.get("cooldown") or {}
    if cool.get("laps"):
        grp = nxt()
        steps.append(_repeat(grp, cool["laps"],
                             [_lap_step(nxt(), "cooldown", "%dm 计圈（冷身）" % lap)],
                             desc="冷身 = %d × %dm" % (cool["laps"], lap)))

    return {"workoutName": spec["name"],
            "description": spec.get("note", ""),
            "sportType": SPORT_RUNNING,
            "workoutSegments": [{"segmentOrder": 1, "sportType": SPORT_RUNNING,
                                 "workoutSteps": steps}]}


def summarize(spec):
    lap = int(spec.get("lap_meters", 400))
    w = (spec.get("warmup") or {}).get("laps", 0)
    s, k = spec.get("sets", 0), spec.get("laps_per_set", 0)
    tr = 0.0
    if w:
        tr += w * lap / 1000.0
    if s and k:
        tr += s * k * lap / 1000.0
    out = ["%s  @ %s" % (spec["name"], spec.get("date", "(no date)")),
           "  热身      %d × %dm = %.2f km（按计圈键）" % (w, lap, w * lap / 1000.0)]
    if spec.get("pre_rest_min"):
        out.append("  前置休息  %s min" % spec["pre_rest_min"])
    if s:
        out.append("  主课      %d 组 × %d × %dm = %.2f km（每组 %d 次计圈）"
                   % (s, k, lap, s * k * lap / 1000.0, k))
    if spec.get("set_rest_min"):
        out.append("  组间休息  %s min · %s" % (spec["set_rest_min"],
                   "完全休息（静止）" if spec.get("rest_style", "rest") == "rest" else "活动恢复（慢跑）"))
    out.append("  跑步距离  ≈ %.2f km（不含冷身）" % tr)
    out.append("  计圈口径  每次按键 = %d m，与跑道实际圈长解耦；复盘只比段内时间" % lap)
    return "\n".join(out)


def parse_id(res):
    if not isinstance(res, dict):
        return None
    for k in ("workout_id", "id", "workoutId"):
        if res.get(k):
            return res[k]
    w = res.get("workout")
    if isinstance(w, dict):
        return w.get("workoutId") or w.get("id")
    return None


def main():
    ap = argparse.ArgumentParser(
        description="Build & schedule a track (操场) interval workout on Garmin, "
                    "with lap-button end conditions (watch distance decoupled from "
                    "the 400 m lap). See docs/02 for the track-spec schema.")
    ap.add_argument("spec", help="track-spec JSON (see scripts/track_spec.example.json)")
    ap.add_argument("--dry-run", action="store_true", help="preview only, no writes")
    ap.add_argument("--print-json", action="store_true", help="print the Garmin DTO too")
    ap.add_argument("--date", default=None, help="override the spec's date")
    ap.add_argument("--no-schedule", action="store_true",
                    help="create/upload but do not put it on the calendar")
    args = ap.parse_args()

    load_dotenv()
    src = os.environ.get("GARMIN_MCP_SRC")
    if not src:
        print("ERROR: no garmin-mcp source. Set GARMIN_MCP_SRC (see docs/01).",
              file=sys.stderr)
        sys.exit(2)
    uvx = os.environ.get("UVX_BIN") or shutil.which("uvx") or "uvx"
    pyver = os.environ.get("GARMIN_MCP_PYTHON") or "3.12"
    data_dir = os.environ.get("GARMIN_DATA_DIR") or os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    reg_path = os.path.join(data_dir, "garmin_workout_registry.json")

    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)
    if args.date:
        spec["date"] = args.date

    workout = build(spec)
    print(summarize(spec))
    if args.print_json:
        print(json.dumps(workout, ensure_ascii=False, indent=1))
    if args.dry_run:
        print("\n(dry-run) no changes will be made")
        return

    reg = load_reg(reg_path)
    cfg = argparse.Namespace(src=src, uvx=uvx, pyver=pyver)
    m = MCP(cfg)
    m.connect()
    try:
        name = spec["name"]
        wid = reg.get(name)
        if not wid:
            res = m.call("upload_workout", {"workout_data": workout})
            wid = parse_id(res)
            if not wid:
                print("   !! upload failed:", json.dumps(res, ensure_ascii=False)[:300])
                return
            reg[name] = wid
            save_reg(reg_path, reg)
            print("   uploaded id=%s" % wid)
        else:
            print("   reuse id=%s (registry)" % wid)
        if spec.get("date") and not args.no_schedule:
            s = m.call("schedule_workout", {"workout_id": wid,
                                            "calendar_date": spec["date"]})
            print("   schedule:", s.get("message") if isinstance(s, dict) else s)
    finally:
        m.close()
    print("done")


if __name__ == "__main__":
    main()
