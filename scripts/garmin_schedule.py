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
Idempotency: created workouts are cached name->workout_id in
<data_dir>/garmin_workout_registry.json.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time


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
    pyver = args.python or os.environ.get("GARMIN_MCP_PYTHON") or "3.12"
    data_dir = args.data_dir or os.environ.get("GARMIN_DATA_DIR") or os.path.join(
        os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    reg_path = os.path.join(data_dir, "garmin_workout_registry.json")

    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)
    reg = load_reg(reg_path)
    cfg = argparse.Namespace(src=src, uvx=uvx, pyver=pyver)

    print(f"== {spec.get('name', '')} -> Garmin ==")
    if args.dry_run:
        print("(dry-run) no changes will be made")

    m = MCP(cfg)
    m.connect()
    try:
        for d in spec.get("days", []):
            date, name = d["date"], d["name"]
            km = d.get("distance_km", 0)
            pace = d.get("pace_min_km", 6.5)
            mins = d.get("minutes") or (int(round(km * pace)) if km else 30)
            hr_min, hr_max = d.get("hr_min", 120), d.get("hr_max", 150)
            print(f"- {date} {name}  ({mins}min, HR{hr_min}-{hr_max})")
            if args.dry_run:
                continue
            wid = reg.get(name)
            if not wid:
                res = m.call("create_run_workout", {
                    "name": name, "run_seconds": mins * 60,
                    "warmup_min": 0, "cooldown_min": 0,
                    "hr_min": hr_min, "hr_max": hr_max})
                wid = parse_id(res)
                if not wid:
                    print("   !! create failed:",
                          json.dumps(res, ensure_ascii=False)[:300])
                    continue
                reg[name] = wid
                save_reg(reg_path, reg)
                print(f"   created id={wid}")
            s = m.call("schedule_workout", {"workout_id": wid, "calendar_date": date})
            msg = s.get("message") if isinstance(s, dict) else json.dumps(
                s, ensure_ascii=False)[:200]
            print("   schedule:", msg)
            time.sleep(0.3)
    finally:
        m.close()
    print("done")


if __name__ == "__main__":
    main()
