# -*- coding: utf-8 -*-
"""
garmin_wellness.py — pull wellness/baseline metrics for a date range.

Acquisition only. This script records what Garmin measured; it does NOT compute
red/yellow training lights, thresholds, deltas or advice. The safety layer lives in
docs/03 / docs/06 and may only ever be made stricter — see docs/02 §4b.

Usage:
  python scripts/garmin_wellness.py                        # last 14 days
  python scripts/garmin_wellness.py --since 2026-09-14 --until 2026-09-19

Config (CLI flags take precedence over env vars), same as garmin_pull.py:
  --src / GARMIN_MCP_SRC   path or package spec of garmin-mcp (REQUIRED)
  --uvx / UVX_BIN          uvx executable (default: "uvx" from PATH)
  GARMIN_MCP_PYTHON        python version for the uvx env (default 3.12)
  GARMIN_IS_CN             account region; set "true" for Garmin Connect China
  --data-dir / GARMIN_DATA_DIR   output dir (default ./data)

Output: <data_dir>/garmin_wellness.json  (schema: docs/02 §4b)

Dates are Garmin account calendar days (Asia/Hong_Kong = UTC+8, same as the
runner's Asia/Shanghai). Sleep is attributed to the date you woke up on.
"""
import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
import time

SCHEMA_VERSION = 1

# These MCP tools take a single date -> one call per day. get_body_composition is
# range-based, so it is called once outside the loop.
TOOL = {
    "resting_hr": "get_rhr_day",
    "sleep": "get_sleep_summary",
    "hrv": "get_hrv_data",
    "training_status": "get_training_status",
    "training_readiness": "get_training_readiness",
}
DAILY = ("resting_hr", "sleep", "hrv", "training_status", "training_readiness")
RANGE_TOOL = "get_body_composition"
RESTING_HR_KEY = "WELLNESS_RESTING_HEART_RATE"


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
# MCP stdio client (same shape as garmin_pull.py)
# ---------------------------------------------------------------------------
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
            "clientInfo": {"name": "garmin-wellness", "version": "1.0"}}})
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
# response classification — an absent measurement is never a zero
# ---------------------------------------------------------------------------
def classify(resp):
    """-> (state, payload, detail) with state in {"ok", "no_data", "error"}.

    Garmin signals "nothing recorded" as {"error": false, "raw": "No ... data found ..."},
    and the MCP client signals a transport failure as {"error": true, "raw": ...}.
    Neither is a measurement: strip the envelope keys, and if nothing real is left,
    this is not data — never write a fabricated 0.
    """
    if not isinstance(resp, dict):
        return "error", None, "non-dict response: %r" % (resp,)
    payload = {k: v for k, v in resp.items() if k not in ("raw", "error", "_isError")}
    if payload:
        return "ok", payload, None
    raw = str(resp.get("raw", ""))[:300]
    if resp.get("error"):
        return "error", None, raw or "request failed"
    if "data" in raw.lower():
        return "no_data", None, raw
    return "error", None, raw or "empty response"


def _rhr_bpm(payload):
    """Lift the value out of {"allMetrics":{"metricsMap":{RESTING_HR_KEY:[{"value":44.0}]}}}."""
    try:
        rows = payload["allMetrics"]["metricsMap"][RESTING_HR_KEY]
    except (KeyError, TypeError):
        return None
    for row in rows or []:
        if isinstance(row, dict) and row.get("value") is not None:
            return row["value"]
    return None


def _record(name, resp):
    """-> (record, error_detail_or_None). Only resting_hr is normalised; every other
    payload is stored verbatim so upstream field renames cannot silently change meaning."""
    state, payload, detail = classify(resp)
    if state != "ok":
        return {"state": state, "detail": detail}, detail
    if name == "resting_hr":
        bpm = _rhr_bpm(payload)
        if bpm is None:
            msg = "resting HR not present in response"
            return {"state": "no_data", "detail": msg}, msg
        return {"state": "ok", "bpm": bpm}, None
    return {"state": "ok", "data": payload}, None


def fetch_day(mcp, date):
    rec, errors = {"date": date}, []
    for name in DAILY:
        record, detail = _record(name, mcp.call(TOOL[name], {"date": date}))
        rec[name] = record
        if detail:
            errors.append({"date": date, "metric": name,
                           "state": record["state"], "detail": detail})
        time.sleep(0.3)
    return rec, errors


def fetch_body_composition(mcp, since, until):
    """Weight/body composition. The runner has never logged any, so an empty
    dateWeightList is a normal outcome: state ok, logged_days 0 — not a zero weight."""
    resp = mcp.call(RANGE_TOOL, {"start_date": since, "end_date": until})
    state, payload, detail = classify(resp)
    if state != "ok":
        return {"state": state, "detail": detail,
                "start_date": since, "end_date": until}, detail
    listed = payload.get("dateWeightList") or []
    logged = [d for d in listed if isinstance(d, dict) and d.get("weight") is not None]
    return ({"state": "ok", "start_date": since, "end_date": until,
             "logged_days": len(logged), "data": payload},
            None if logged else "no weight record in range")


# ---------------------------------------------------------------------------
# console summary
# ---------------------------------------------------------------------------
def _cell(rec, name):
    r = rec.get(name) or {}
    state = r.get("state")
    if state != "ok":
        return "<%s>" % (state or "?")
    if name == "resting_hr":
        return "%s bpm" % r.get("bpm")
    d = r.get("data") or {}
    if name == "sleep":
        sec = d.get("sleep_seconds")
        return "%.1f h" % (sec / 3600.0) if sec else "-"
    if name == "hrv":
        v = d.get("last_night_avg_hrv_ms")
        return "%s ms %s" % (v if v is not None else "-", d.get("status") or "")
    if name == "training_status":
        return str(d.get("training_status_feedback") or d.get("training_status") or "-")
    return "-"


def _parse_date(value, flag):
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        print("ERROR: %s expects YYYY-MM-DD, got %r" % (flag, value), file=sys.stderr)
        sys.exit(2)


# ---------------------------------------------------------------------------
def main():
    load_dotenv()
    ap = argparse.ArgumentParser(
        description="Pull Garmin wellness/baseline metrics (resting HR, sleep, HRV, "
                    "body composition, training status) for a date range. Acquisition "
                    "only — no lights, thresholds or advice.",
        epilog="Output schema: docs/02 §4b. See docs/01 for garmin-mcp install/auth.")
    ap.add_argument("--since", default=None,
                    help="start date YYYY-MM-DD (default: 13 days before --until)")
    ap.add_argument("--until", default=None,
                    help="end date YYYY-MM-DD, inclusive (default: today)")
    ap.add_argument("--src", default=None, help="garmin-mcp source; default $GARMIN_MCP_SRC")
    ap.add_argument("--uvx", default=None, help="uvx executable (default: uvx on PATH)")
    ap.add_argument("--python", dest="pyver", default=None,
                    help="python version for the uvx env (default 3.12)")
    ap.add_argument("--data-dir", default=None,
                    help="output dir (default ./data)")
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

    until = _parse_date(args.until, "--until") if args.until else datetime.date.today()
    since = (_parse_date(args.since, "--since") if args.since
             else until - datetime.timedelta(days=13))
    if since > until:
        print("ERROR: --since %s is after --until %s" % (since, until), file=sys.stderr)
        sys.exit(2)

    os.makedirs(data_dir, exist_ok=True)
    cfg = argparse.Namespace(src=src, uvx=uvx, pyver=pyver, data_dir=data_dir)
    days = [since + datetime.timedelta(days=i) for i in range((until - since).days + 1)]

    print("range %s .. %s (%d days)" % (since, until, len(days)))
    print("  %-12s %-11s %-8s %-16s %s" %
          ("date", "resting HR", "sleep", "HRV", "training status"))

    m = MCP(cfg)
    m.connect()
    day_recs, errors = [], []
    try:
        for d in days:
            rec, errs = fetch_day(m, d.isoformat())
            day_recs.append(rec)
            errors.extend(errs)
            print("  %-12s %-11s %-8s %-16s %s" % (
                d.isoformat(), _cell(rec, "resting_hr"), _cell(rec, "sleep"),
                _cell(rec, "hrv"), _cell(rec, "training_status")))
        body, body_note = fetch_body_composition(m, since.isoformat(), until.isoformat())
    finally:
        m.close()

    out = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "range": {"start": since.isoformat(), "end": until.isoformat(), "days": len(days)},
        "advisory": "纯客观取数：本文件不含任何红黄灯判定、阈值或建议。"
                    "安全层见 docs/03 / docs/06，只允许加严。",
        "days": day_recs,
        "body_composition": body,
        "errors": errors,
    }
    path = os.path.join(data_dir, "garmin_wellness.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")

    # Availability per metric: "no data" is a normal outcome, not a failure, so collapse
    # it into one line instead of one warning per day. Genuine failures still shout.
    availability = []
    for name in DAILY:
        states = [d[name]["state"] for d in day_recs]
        if all(s == "ok" for s in states):
            availability.append("%s %d/ok" % (name, len(states)))
            continue
        bits = ", ".join("%d %s" % (states.count(s), s)
                         for s in ("no_data", "error") if states.count(s))
        availability.append("%s %d ok (%s)" % (name, states.count("ok"), bits))
    print("availability: " + " | ".join(availability))

    for e in errors:
        if e["state"] == "error":
            print("WARNING  %s %s: %s" % (e["date"], e["metric"], e["detail"]))
    print("body composition: %s day(s) with a weight record%s"
          % (body.get("logged_days", 0),
             "  (%s)" % body_note if body_note else ""))
    print("wrote", path)
    print("done")


if __name__ == "__main__":
    main()
