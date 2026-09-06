# -*- coding: utf-8 -*-
"""
vdot.py — VDOT calculator backed by the official-style VDOT tables (stdlib only).

Two canonical tables live under data/vdot/ (see data/vdot/README.md):
  - vdot_races.csv : (vdot, distance_m, seconds)  race-time equivalents per VDOT
  - vdot_paces.csv : (vdot, intensity, distance_m, seconds) training paces/times

What it does:
  - race result over a STANDARD distance  -> VDOT  (from the races table)
  - VDOT score                            -> training pace/times (E/M/T/I/R) + race
                                             equivalents  (from the tables)
  - a NON-standard distance still works via the classic running-economy equations
    (used only as a fallback to estimate VDOT; training paces always come from the
    tables, interpolated between integer VDOT rows).

⚠ LICENSE / 许可：the two tables are derived from a GPL-3.0-licensed export (see
NOTICE.md and data/vdot/README.md). Interpolation/estimation code below is our own.

Examples:
  python scripts/vdot.py --race-time 40:00 --distance 10k
  python scripts/vdot.py --vdot 48
  python scripts/vdot.py --5k 21:00
"""
import argparse
import csv
import json
import math
import os
import sys

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "vdot")
PACES_CSV = os.path.join(DATA_DIR, "vdot_paces.csv")
RACES_CSV = os.path.join(DATA_DIR, "vdot_races.csv")

# --- race-distance helpers ----------------------------------------------------
DIST = {"1500": 1500, "1mile": 1609.34, "3000": 3000, "2mile": 3218.69,
        "5k": 5000, "8k": 8000, "5mile": 8045.47, "10k": 10000,
        "15k": 15000, "10mile": 16093.4, "20k": 20000, "half": 21097.5,
        "25k": 25000, "30k": 30000, "marathon": 42195, "full": 42195}


def _load_tables():
    """Returns paces[(vdot, intensity, dist_m)]->sec and races[(vdot, dist_m)]->sec."""
    paces, races = {}, {}
    if not (os.path.exists(PACES_CSV) and os.path.exists(RACES_CSV)):
        raise SystemExit(
            f"ERROR: missing VDOT tables under {DATA_DIR}. See data/vdot/README.md "
            "(LICENSE: GPL-3.0 export, see NOTICE.md).")
    with open(PACES_CSV, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            paces[(int(float(r["vdot"])), r["intensity"], float(r["distance_m"]))] = \
                float(r["seconds"])
    with open(RACES_CSV, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            races[(int(float(r["vdot"])), float(r["distance_m"]))] = float(r["seconds"])
    return paces, races


def _pacerow(paces, vd, zone):
    """All present (dist_m, sec) rows for a (vd, zone), dist asc."""
    out = [((d), paces[(vd, zone, d)]) for (v, z, d) in paces
           if v == vd and z == zone]
    return sorted(out)


def _pace_per_km(paces, vd, zone):
    """Seconds per km for a zone at integer vdot (scale from any present row)."""
    rows = _pacerow(paces, vd, zone)
    if not rows:
        return None
    # prefer an actual 1 km row, otherwise scale from the shortest available
    for d, s in rows:
        if abs(d - 1000.0) < 0.01:
            return s
    d, s = rows[0]
    return s * 1000.0 / d


def _interp(f, x):
    """Linear interpolation of f over integer VDOT rows around float x."""
    lo, hi = int(math.floor(x)), int(math.ceil(x))
    if lo == hi:
        v = f(lo)
        return v
    v_lo, v_hi = f(lo), f(hi)
    if v_lo is None and v_hi is None:
        return None
    if v_lo is None:
        return v_hi
    if v_hi is None:
        return v_lo
    t = (x - lo) / (hi - lo)
    return v_lo + (v_hi - v_lo) * t


def paces_at(paces, vdot):
    """zone -> (slow_km, fast_km) not meaningful from single table values; instead
    return dict zone -> seconds/km reference plus R-400 seconds."""
    out = {}
    for zone in ("E", "M", "T", "I", "R"):
        per_km = _interp(lambda v: _pace_per_km(paces, v, zone), vdot)
        if per_km is not None:
            out[zone] = {"km_s": per_km}
    r400 = _interp(lambda v: _pick(paces, v, "R", 400.0), vdot)
    out.setdefault("R", {})["r400_s"] = r400
    return out


def _pick(paces, vd, zone, want_d):
    rows = _pacerow(paces, vd, zone)
    if not rows:
        return None
    for d, s in rows:
        if abs(d - want_d) < 0.01:
            return s
    # nearest present distance, scaled linearly to the wanted distance
    d, s = min(rows, key=lambda t: abs(t[0] - want_d))
    return s * want_d / d


def race_equiv(races, vdot, dist_m):
    return _interp(lambda v: races.get((v, dist_m)), vdot)


# --- fallback: classic running-economy equations (non-standard distances only) ---
def _vo2(v_mmin):
    return -4.60 + 0.182258 * v_mmin + 0.000104 * v_mmin ** 2


def _pct(t_min):
    return (0.8 + 0.1894393 * math.exp(-0.012778 * t_min)
            + 0.2989558 * math.exp(-0.1932605 * t_min))


def _vdot_formula(dist_m, time_s):
    return _vo2(dist_m / time_s * 60.0) / _pct(time_s / 60.0)


def _parse_time(s):
    if isinstance(s, (int, float)):
        return float(s)
    parts = [p for p in s.strip().split(":") if p != ""]
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    return float(parts[0])


def _fmt_time(sec):
    sec = max(0.0, float(sec))
    h = int(sec // 3600)
    m = int((sec - h * 3600) // 60)
    s = int(round(sec - h * 3600 - m * 60))
    if s == 60:
        s = 0
        m += 1
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def _fmt_pace(sec_per_km):
    return _fmt_time(sec_per_km)


# ---------------------------------------------------------------------------
def _vdot_from_race(paces, races, dist_m, time_s):
    """VDOT from a race time. Standard distances use the races table (interpolated);
    non-standard distances fall back to the classic equations."""
    keys = sorted({d for (_, d) in races})
    match = min(keys, key=lambda d: abs(d - dist_m))
    if abs(match - dist_m) < max(1.0, dist_m * 0.001):
        # bracket by vdot: higher vdot -> shorter time
        vdots = sorted({v for (v, _) in races})
        times = [(v, races[(v, match)]) for v in vdots if (v, match) in races]
        lo_i = None
        for i in range(len(times) - 1):
            if times[i + 1][1] <= time_s < times[i][1] or \
               (times[i][1] == time_s):
                lo_i = i
                break
        if lo_i is None:
            if time_s >= times[0][1]:
                # slower than the lowest vdot row: extrapolate below vdot 30
                (v0, t0), (v1, t1) = times[0], times[1]
            elif time_s <= times[-1][1]:
                # faster than the highest row: extrapolate above vdot 85
                (v0, t0), (v1, t1) = times[-2], times[-1]
            else:
                raise RuntimeError("unreachable")
            return v0 + (t0 - time_s) / (t0 - t1) * (v1 - v0)
        (v0, t0), (v1, t1) = times[lo_i], times[lo_i + 1]
        if t0 == t1:
            return float(v0)
        return v0 + (t0 - time_s) / (t0 - t1) * (v1 - v0)
    return _vdot_formula(dist_m, time_s)


def cli():
    ap = argparse.ArgumentParser(
        description="VDOT calculator backed by data/vdot/*.csv "
                    "(GPL-3.0-derived tables; see NOTICE.md).",
        epilog="Examples:\n"
               "  python scripts/vdot.py --race-time 40:00 --distance 10k\n"
               "  python scripts/vdot.py --vdot 48\n"
               "  python scripts/vdot.py --5k 21:00")
    ap.add_argument("--race-time", type=_parse_time, default=None,
                    help="all-out race time, e.g. 40:00 or 1:23:45")
    ap.add_argument("--distance", default=None,
                    help="race distance: 1500/1mile/3k/5k/8k/10k/15k/10mile/20k/half/"
                         "25k/30k/marathon (or metres for a non-standard distance)")
    ap.add_argument("--vdot", type=float, default=None,
                    help="direct VDOT score (skip the race conversion)")
    for dist, flag in (("5k", "--5k"), ("10k", "--10k"),
                       ("half", "--half"), ("marathon", "--marathon")):
        ap.add_argument(flag, type=_parse_time, default=None,
                        help=f"shortcut: race time over {dist}")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    a = ap.parse_args()

    paces, races = _load_tables()

    if a.vdot is None:
        if a.race_time is not None and a.distance:
            dist_m = DIST.get(a.distance)
            dist_m = float(a.distance) if dist_m is None else dist_m
            vdot = _vdot_from_race(paces, races, dist_m, a.race_time)
            src = f"race {a.distance} {_fmt_time(a.race_time)}"
        else:
            pairs = [(k, a.__dict__.get(k)) for k in ("5k", "10k", "half", "marathon")]
            pairs = [(k, v) for k, v in pairs if v is not None]
            if not pairs:
                ap.error("provide --race-time + --distance, --vdot, or a --<dist> shortcut")
            dist_m = DIST[pairs[0][0]]
            vdot = _vdot_from_race(paces, races, dist_m, pairs[0][1])
            src = f"race {pairs[0][0]} {_fmt_time(pairs[0][1])}"
    else:
        vdot = a.vdot
        src = "given directly"

    zones = paces_at(paces, vdot)
    eq = {d: race_equiv(races, vdot, DIST[d]) for d in ("5k", "10k", "half", "marathon")}
    eq = {d: v for d, v in eq.items() if v is not None}

    if a.json:
        out = {
            "vdot": round(vdot, 1), "source": src,
            "paces": {z: {"km": _fmt_pace(v["km_s"]) if "km_s" in v else None,
                          "r400_s": v.get("r400_s")} for z, v in zones.items()},
            "equivalent": {d: _fmt_time(eq[d]) for d in eq},
            "table": "data/vdot/ (GPL-3.0-derived, see NOTICE.md)"}
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    print(f"VDOT  {vdot:.1f}  (from {src})")
    print("-" * 46)
    for z in ("E", "M", "T", "I", "R"):
        v = zones.get(z)
        if not v:
            continue
        if v.get("km_s"):
            print(f"  {z:<2}  {_fmt_pace(v['km_s'])} /km")
    if zones.get("R") and zones["R"].get("r400_s"):
        print(f"  R   400m ≈ {zones['R']['r400_s']:.0f} s")
    print("-" * 46)
    for d in ("5k", "10k", "half", "marathon"):
        if d in eq:
            print(f"  {d:<9} equiv {_fmt_time(eq[d])}")
    print("\nPaces/times from data/vdot/ tables (GPL-3.0-derived; see NOTICE.md).")
    print("E/recovery execution is HR/feel first — the E pace is a reference floor.")
    return 0


if __name__ == "__main__":
    sys.exit(cli())
