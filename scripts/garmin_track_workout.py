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

Idempotent: <data_dir>/garmin_workout_registry.json caches the workout id AND a fingerprint
of the built DTO. If the spec changes — even when the name does not — the workout is rebuilt
(upload new -> schedule -> delete old), so the watch cannot silently keep a stale version.
See scripts/workout_registry.py and docs/02 §4.

Conventions:
- The warm-up carries NO heart-rate target, on purpose: during a warm-up the heart rate
  climbs from resting, so a band on that step just fires low-HR alerts. `warmup.hr_min/hr_max`
  in a spec is ignored, with a warning (docs/02 §3b).

Config: same env vars as garmin_pull.py / garmin_schedule.py (see docs/01).
Exit codes: 0 ok · 1 the session did not reach Garmin · 2 config error.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

# Shared with garmin_schedule.py: registry format, fingerprinting, drift detection.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import workout_registry as wrg  # noqa: E402

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
        if warm.get("hr_min") or warm.get("hr_max"):
            print("WARNING: warmup.hr_min/hr_max ignored — the warm-up of a track session "
                  "carries no heart-rate target, on purpose (docs/02 §3b). Remove them.")
        grp = nxt()
        inner = _lap_step(nxt(), "warmup",
                          "%dm 计圈（%d × %dm 热身）" % (lap, warm["laps"], lap))
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

    reg = wrg.load_reg(reg_path)
    cfg = argparse.Namespace(src=src, uvx=uvx, pyver=pyver)

    name = spec["name"]
    session = {
        "date": spec.get("date"), "name": name, "kind": wrg.KIND_TRACK,
        "expect": {"dto": workout},
        "fp": wrg.fingerprint(wrg.KIND_TRACK, {"workout_data": workout}),
        "call": ("upload_workout", {"workout_data": workout}),
    }

    failures = []
    m = MCP(cfg)
    m.connect()
    try:
        # read-only: is the cached copy still the one we would build?
        try:
            action = wrg.plan_actions([session], reg, wrg.make_remote_get(m.call))[0]
        except wrg.RemoteLookupError as e:
            print("ERROR: %s" % e, file=sys.stderr)
            sys.exit(2)

        print("- %s" % (spec.get("date") or "(no date)"))
        print("    %-7s %s%s" % (action["action"], action["reason"],
                                 "" if action["old_id"] is None
                                 else "  [old id=%s]" % action["old_id"]))

        if args.dry_run:
            print("(dry-run) nothing was written")
            print("done")
            return

        wid = action["old_id"]
        if action["action"] != "reuse":
            res = m.call(*action["call"])
            wid = parse_id(res)
            if not wid:
                print("   !! upload failed: %s"
                      % json.dumps(res, ensure_ascii=False)[:300])
                print("done")
                sys.exit(1)

        scheduled = {}
        if spec.get("date") and not args.no_schedule:
            sres = m.call("schedule_workout", {"workout_id": wid,
                                               "calendar_date": spec["date"]})
            if wrg.write_landed(sres):
                scheduled[spec["date"]] = wid
            else:
                print("   !! schedule failed: %s"
                      % json.dumps(sres, ensure_ascii=False)[:300])
                failures.append("%s: could not schedule" % spec["date"])

        note = ""
        if action["action"] == "replace" and action["old_id"]:
            dres = m.call("delete_workout", {"workout_id": action["old_id"]})
            if wrg.write_landed(dres):
                note = "  (old id=%s deleted)" % action["old_id"]
            else:
                print("   !! delete of old id=%s failed: %s"
                      % (action["old_id"], json.dumps(dres, ensure_ascii=False)[:200]))
                failures.append("old workout %s not deleted" % action["old_id"])

        reg[name] = {"id": wid, "kind": wrg.KIND_TRACK, "fp": action["fp"]}
        wrg.save_reg(reg_path, reg)
        print("   %-7s id=%s -> %s%s"
              % (action["action"], wid, spec.get("date") or "-", note))

        if scheduled:
            vfails, summary = wrg.verify_schedule(m.call, scheduled)
            print("   " + summary)
            failures.extend(vfails)
    finally:
        m.close()

    if failures:
        print("\nFAILED (%d):" % len(failures), file=sys.stderr)
        for f in failures:
            print("  - %s" % f, file=sys.stderr)
        sys.exit(1)
    print("done")


if __name__ == "__main__":
    main()
