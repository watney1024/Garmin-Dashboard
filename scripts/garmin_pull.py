# -*- coding: utf-8 -*-
"""
garmin_pull.py — bridge to garmin-mcp (MCP over stdio) to pull Garmin data.

Rebuilds the canonical master CSV (16 columns) from the full activity list and
downloads per-activity detail CSVs (running laps, strength sets, bouldering
routes, ...) into the inbox directory.

Usage:
  python scripts/garmin_pull.py                 # rebuild master + download recent 14 days
  python scripts/garmin_pull.py --since 2026-01-01   # rebuild master + download since that date
  python scripts/garmin_pull.py --master-only   # only rebuild the master CSV

Config (CLI flags take precedence over env vars):
  --src / GARMIN_MCP_SRC   path or package spec of garmin-mcp (REQUIRED)
  --uvx / UVX_BIN          uvx executable (default: "uvx" from PATH)
  GARMIN_MCP_PYTHON        python version for the uvx env (default 3.12)
  GARMIN_IS_CN             account region; set "true" for Garmin Connect China
  UV_DEFAULT_INDEX         optional pip index (e.g. a mirror), inherited from env
  --data-dir / GARMIN_DATA_DIR   output dir (default ./data)

Dependencies: an authenticated token at ~/.garminconnect (produced once by
`garmin-mcp-auth`; valid ~6 months). See docs/01_mcp_setup_zh.md, including the
PR #249 requirement for China accounts.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

# ---------------------------------------------------------------------------
# Canonical master schema (16 columns). Preserve exactly; see docs/02.
# ---------------------------------------------------------------------------
TYPE_CN = {
    "running": "跑步", "track_running": "操场跑步", "trail_running": "越野跑",
    "treadmill_running": "跑步机跑步", "strength_training": "力量训练",
    "bouldering": "抱石", "indoor_climbing": "室内攀岩", "badminton": "羽毛球",
    "cycling": "骑行", "indoor_cardio": "室内有氧", "breathwork": "呼吸训练",
    "pilates": "普拉提", "lap_swimming": "游泳", "hiking": "徒步",
    "ultimate_disc": "极限飞盘", "other": "其他",
}
HDR = [
    "活动类型", "类型Key", "日期", "标题", "距离km", "时长", "移动时长",
    "平均配速min/km", "热量", "平均心率", "最大心率", "步数", "累计爬升m",
    "累计下降m", "事件类型", "活动ID",
]
RUN_TYPES = ("running", "track_running", "trail_running", "treadmill_running")


# ---------------------------------------------------------------------------
# tiny .env loader (optional convenience; real env always wins)
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def hms(sec):
    if sec in (None, ""):
        return ""
    s = int(round(float(sec)))
    h, r = divmod(s, 3600)
    m, s2 = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s2:02d}"


def pace(msec, dist_m, is_run):
    """MM:SS per km computed from moving time; empty when meaningless."""
    if not is_run or not dist_m:
        return ""
    try:
        spd = float(msec) / 60.0 / (float(dist_m) / 1000.0)
        if spd <= 0 or spd > 1200:
            return ""
        mm = int(spd)
        ss = int(round((spd - mm) * 60))
        if ss == 60:
            mm += 1
            ss = 0
        return f"{mm:02d}:{ss:02d}"
    except Exception:
        return ""


def _csv_cell(v):
    if v == "":
        return ""
    s = str(v)
    return f'"{s}"' if ("," in s or '"' in s) else s


# ---------------------------------------------------------------------------
# MCP stdio client (stdlib only)
# ---------------------------------------------------------------------------
class MCP:
    def __init__(self, cfg, client_name):
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
            "clientInfo": {"name": "garmin-pull", "version": "1.0"}}})
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
            return {"error": bool(r["result"].get("isError")), "raw": txt[:200]}

    def close(self):
        try:
            self.p.kill()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# pull logic
# ---------------------------------------------------------------------------
def fetch_all(cfg):
    m = MCP(cfg, "garmin-pull")
    m.connect()
    out, start = [], 0
    try:
        while True:
            res = m.call("get_activities", {"start": start, "limit": 100})
            items = res if isinstance(res, list) else (
                res.get("activities") if isinstance(res, dict) else [])
            if not items:
                break
            out.extend(items)
            start += len(items)
            if len(items) < 100:
                break
            time.sleep(0.3)
    finally:
        m.close()
    return out


def rebuild_master(cfg, acts):
    master = os.path.join(cfg.data_dir, "Activities.csv")
    acts_sorted = sorted(acts, key=lambda x: x["start_time"], reverse=True)
    with open(master, "w", encoding="utf-8-sig", newline="") as f:
        f.write(",".join(HDR) + "\n")
        for a in acts_sorted:
            t = a.get("type", "")
            is_run = t in RUN_TYPES
            dm = a.get("distance_meters") or 0
            vals = [
                TYPE_CN.get(t, t), t, a.get("start_time", ""), a.get("name", ""),
                round(dm / 1000.0, 2) if dm else "",
                hms(a.get("duration_seconds")),
                hms(a.get("moving_duration_seconds")),
                pace(a.get("moving_duration_seconds"), dm, is_run),
                a.get("calories", ""), a.get("avg_hr_bpm", ""), a.get("max_hr_bpm", ""),
                a.get("steps", ""), a.get("elevation_gain_meters", ""),
                a.get("elevation_loss_meters", ""), a.get("event_type", ""), a.get("id", ""),
            ]
            f.write(",".join(_csv_cell(v) for v in vals) + "\n")
    print("master:", master, "rows", len(acts_sorted))


def download_since(cfg, acts, since):
    inbox = os.path.join(cfg.data_dir, "inbox")
    os.makedirs(inbox, exist_ok=True)
    todo = sorted(
        a["id"] for a in acts
        if a["start_time"] >= since
        and not os.path.exists(os.path.join(inbox, f"activity_{a['id']}.csv")))
    print("download todo:", len(todo))
    ok, fail = [], []
    for ci in range(0, len(todo), 35):
        m = MCP(cfg, "garmin-pull")
        m.connect()
        try:
            for i in todo[ci:ci + 35]:
                try:
                    r = m.call("download_activity_file", {
                        "activity_id": i, "format": "csv", "output_dir": inbox})
                    if isinstance(r, dict) and r.get("error"):
                        fail.append((i, r.get("raw", "")[:120]))
                        continue
                    ok.append(i)
                    src = os.path.join(inbox, f"{i}.csv")
                    if os.path.exists(src):
                        os.rename(src, os.path.join(inbox, f"activity_{i}.csv"))
                except Exception as e:
                    fail.append((i, str(e)[:120]))
                time.sleep(0.35)
        finally:
            m.close()
    print("download ok", len(ok), "fail", len(fail))
    for f in fail:
        print("  fail:", f)


# ---------------------------------------------------------------------------
def main():
    load_dotenv()
    ap = argparse.ArgumentParser(
        description="Pull Garmin activities through garmin-mcp (stdio) and rebuild "
                    "the canonical master CSV + download per-activity detail CSVs.",
        epilog="See docs/01_mcp_setup_zh.md for garmin-mcp install/auth (PR #249 "
               "required for Garmin China accounts).")
    ap.add_argument("--since", default=None,
                    help="download detail CSVs from this YYYY-MM-DD (default: last 14 days)")
    ap.add_argument("--master-only", action="store_true",
                    help="only rebuild the master CSV, skip inbox downloads")
    ap.add_argument("--src", default=None,
                    help="garmin-mcp source (path or package spec); default $GARMIN_MCP_SRC")
    ap.add_argument("--uvx", default=None, help="uvx executable (default: uvx on PATH)")
    ap.add_argument("--python", dest="pyver", default=None,
                    help="python version for the uvx env (default 3.12)")
    ap.add_argument("--data-dir", default=None,
                    help="output data dir (default ./data); inbox = <data>/inbox")
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

    os.makedirs(os.path.join(data_dir, "inbox"), exist_ok=True)
    cfg = argparse.Namespace(src=src, uvx=uvx, pyver=pyver, data_dir=data_dir)

    acts = fetch_all(cfg)
    if not acts:
        print("WARNING: get_activities returned nothing. Check token/auth (docs/01).")
    rebuild_master(cfg, acts)
    if not args.master_only:
        since = args.since or time.strftime(
            "%Y-%m-%d", time.localtime(time.time() - 14 * 86400))
        download_since(cfg, acts, since)
    print("done")


if __name__ == "__main__":
    main()
