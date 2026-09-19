# -*- coding: utf-8 -*-
"""
garmin_schedule.py — push a week of planned running sessions into Garmin so the
watch calendar shows the day's workout. Idempotent: re-running never duplicates.

Usage:
  python scripts/garmin_schedule.py scripts/week_spec.example.json            # schedule for real
  python scripts/garmin_schedule.py scripts/week_spec.example.json --dry-run  # preview only

Week-spec JSON schema (see scripts/week_spec.example.json and docs/02):
  { "name": "W1",
    "days": [
      {"date": "2026-09-08", "name": "W1 Tue E5", "kind": "easy",
       "distance_km": 5, "pace_min_km": 6.4, "hr_min": 125, "hr_max": 150}, ...
    ]}

Conventions:
- Easy / recovery sessions are prescribed as time + HR (pace is for naming only).
- minutes defaults to round(distance_km * pace_min_km); HR bounds default 120-150.
- Only schedule session kinds allowed by the runner profile / plan. Coach-run or
  strength sessions that the runner manages separately must NOT be scheduled here.

Config: same env vars as garmin_pull.py (see its header or docs/01).

Idempotency: <data_dir>/garmin_workout_registry.json caches each session's workout id AND
a fingerprint of the arguments that created it. A session whose NAME is unchanged but whose
CONTENT changed is rebuilt (create new -> schedule -> delete old), so the watch can never
silently keep a stale version. See scripts/workout_registry.py and docs/02 §4.

Exit codes: 0 ok · 1 one or more sessions did not reach Garmin · 2 config error.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

# Shared with garmin_track_workout.py: registry format, fingerprinting, drift detection.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import workout_registry as wrg  # noqa: E402


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
    def __init__(self, cfg):
        cmd = [cfg.uvx, "--python", cfg.pyver, "--from", cfg.src, "garmin-mcp"]
        env = dict(os.environ)
        env.update({"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"})
        self.p = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, env=env, text=True, bufsize=1,
            encoding="utf-8", errors="replace")
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
            "clientInfo": {"name": "garmin-schedule", "version": "1.0"}}})
        self._recv(150)
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})

    def call(self, name, args, timeout=90):
        self._rid[0] += 1
        self._send({"jsonrpc": "2.0", "id": self._rid[0], "method": "tools/call",
                    "params": {"name": name, "arguments": args}})
        r = self._recv(timeout)
        if not r or "result" not in r:
            return {"error": True, "detail": r}
        c = r["result"].get("content", [])
        txt = c[0]["text"] if c else ""
        try:
            d = json.loads(txt)
            d["_isError"] = bool(r["result"].get("isError"))
            return d
        except Exception:
            return {"error": bool(r["result"].get("isError")), "detail": txt[:300]}

    def close(self):
        try:
            self.p.kill()
        except Exception:
            pass


def parse_id(res):
    return res.get("workout_id") or res.get("id")


def main():
    load_dotenv()
    ap = argparse.ArgumentParser(
        description="Create & schedule a week of run workouts to Garmin via "
                    "garmin-mcp (stdio). Idempotent (name->id registry).",
        epilog="See docs/01_mcp_setup_zh.md for install/auth. Never schedule "
               "session kinds the profile/plan excludes.")
    ap.add_argument("spec", help="week-spec JSON file")
    ap.add_argument("--dry-run", action="store_true", help="print only; no Garmin changes")
    ap.add_argument("--src", default=None,
                    help="garmin-mcp source (path or package spec); default $GARMIN_MCP_SRC")
    ap.add_argument("--uvx", default=None, help="uvx executable (default: uvx on PATH)")
    ap.add_argument("--python", dest="pyver", default=None,
                    help="python version for the uvx env (default 3.12)")
    ap.add_argument("--data-dir", default=None,
                    help="data dir holding the registry (default ./data)")
    args = ap.parse_args()

    src = args.src or os.environ.get("GARMIN_MCP_SRC")
    if not src:
        print("ERROR: no garmin-mcp source. Pass --src or set GARMIN_MCP_SRC "
              "(see docs/01_mcp_setup_zh.md).", file=sys.stderr)
        sys.exit(2)
    uvx = args.uvx or os.environ.get("UVX_BIN") or shutil.which("uvx") or "uvx"
    pyver = args.pyver or os.environ.get("GARMIN_MCP_PYTHON") or "3.12"
    data_dir = args.data_dir or os.environ.get("GARMIN_DATA_DIR") or os.path.join(
        os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    reg_path = os.path.join(data_dir, "garmin_workout_registry.json")

    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)
    reg = wrg.load_reg(reg_path)
    cfg = argparse.Namespace(src=src, uvx=uvx, pyver=pyver)

    # What SHOULD be on the watch — resolved values, so the fingerprint means something.
    sessions = []
    for d in spec.get("days", []):
        km = d.get("distance_km", 0)
        pace = d.get("pace_min_km", 6.5)
        mins = d.get("minutes") or (int(round(km * pace)) if km else 30)
        hr_min, hr_max = d.get("hr_min", 120), d.get("hr_max", 150)
        cargs = {"name": d["name"], "run_seconds": mins * 60, "warmup_min": 0,
                 "cooldown_min": 0, "hr_min": hr_min, "hr_max": hr_max}
        sessions.append({
            "date": d["date"], "name": d["name"], "kind": wrg.KIND_RUN,
            "expect": {"duration": mins * 60, "hr": (hr_min, hr_max)},
            "fp": wrg.fingerprint(wrg.KIND_RUN, cargs),
            "call": ("create_run_workout", cargs),
            "summary": "%dmin, HR%d-%d" % (mins, hr_min, hr_max),
        })

    print(f"== {spec.get('name', '')} -> Garmin ==")
    if not sessions:
        print("no sessions in this spec")
        print("done")
        return

    failures = []
    m = MCP(cfg)
    m.connect()
    try:
        # --- read-only phase: decide create / reuse / replace for every session ---
        try:
            actions = wrg.plan_actions(sessions, reg, wrg.make_remote_get(m.call))
        except wrg.RemoteLookupError as e:
            print("ERROR: %s" % e, file=sys.stderr)
            sys.exit(2)

        for a in actions:
            print("- %s %s  (%s)" % (a["date"], a["name"], a["summary"]))
            print("    %-7s %s%s" % (a["action"], a["reason"],
                                     "" if a["old_id"] is None
                                     else "  [old id=%s]" % a["old_id"]))

        if args.dry_run:
            print("(dry-run) nothing was written")
            print("done")
            return

        # --- write phase ---
        scheduled = {}
        for a in actions:
            name, date = a["name"], a["date"]
            wid = a["old_id"]
            if a["action"] != "reuse":
                tool, tool_args = a["call"]
                res = m.call(tool, tool_args)
                wid = parse_id(res)
                if not wid:
                    print("   !! %s failed: %s"
                          % (tool, json.dumps(res, ensure_ascii=False)[:300]))
                    failures.append("%s %s: could not create the workout" % (date, name))
                    continue

            sres = m.call("schedule_workout", {"workout_id": wid, "calendar_date": date})
            if not wrg.write_landed(sres):
                print("   !! schedule failed: %s"
                      % json.dumps(sres, ensure_ascii=False)[:300])
                failures.append("%s %s: could not schedule" % (date, name))
                continue
            scheduled[date] = wid

            note = ""
            if a["action"] == "replace" and a["old_id"]:
                # The new one is already scheduled, so a failed delete cannot leave the
                # watch empty — but it must still be reported.
                dres = m.call("delete_workout", {"workout_id": a["old_id"]})
                if wrg.write_landed(dres):
                    note = "  (old id=%s deleted)" % a["old_id"]
                else:
                    print("   !! delete of old id=%s failed: %s"
                          % (a["old_id"], json.dumps(dres, ensure_ascii=False)[:200]))
                    failures.append("%s %s: old workout %s not deleted"
                                    % (date, name, a["old_id"]))

            if a["action"] != "reuse" or reg.get(name, {}).get("fp") != a["fp"]:
                reg[name] = {"id": wid, "kind": a["kind"], "fp": a["fp"]}
                wrg.save_reg(reg_path, reg)

            print("   %-7s id=%s -> %s%s" % (a["action"], wid, date, note))
            time.sleep(0.3)

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
