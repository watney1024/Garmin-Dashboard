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

Intensity points (Daniels book Table 5-4, data/vdot/intensity_points.csv):
  python scripts/vdot.py --points --vdot 48 --time 48:30 --distance 10k
  python scripts/vdot.py --points --vdot 48 --pace 4:00 --minutes 40

Session construction caps (book Table 5-5, data/vdot/session_prescriptions.csv):
  python scripts/vdot.py --session 15 --vdot 52 [--json]

Validate every table against its book anchors:
  python scripts/vdot.py --selfcheck
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
POINTS_CSV = os.path.join(DATA_DIR, "intensity_points.csv")
SESSION_CSV = os.path.join(DATA_DIR, "session_prescriptions.csv")

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


def _load_points():
    """[(pct_vdot, points_per_min)] sorted, from intensity_points.csv (book Table 5-4)."""
    if not os.path.exists(POINTS_CSV):
        raise SystemExit(f"ERROR: missing {POINTS_CSV}. See data/vdot/README.md.")
    rows = []
    with open(POINTS_CSV, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            rows.append((float(r["pct_vdot"]), float(r["points_per_min"])))
    return sorted(rows)


def _load_sessions():
    """List of dict rows from session_prescriptions.csv (book Table 5-5)."""
    if not os.path.exists(SESSION_CSV):
        raise SystemExit(f"ERROR: missing {SESSION_CSV}. See data/vdot/README.md.")
    with open(SESSION_CSV, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


# --- Daniels intensity points (book Table 5-4) ---------------------------------
# %VDOT of an effort = VO2(its velocity) / VDOT x 100, i.e. how much of the
# runner's VO2max the pace consumes. Points = points_per_min(%VDOT) x minutes.

def _points_rate(rows, pct):
    """Linear interpolation over integer %VDOT rows; clamps outside the table
    and interpolates across the book's unprinted 101-104 gap."""
    if pct <= rows[0][0]:
        return rows[0][1]
    if pct >= rows[-1][0]:
        return rows[-1][1]
    for (p0, r0), (p1, r1) in zip(rows, rows[1:]):
        if p0 <= pct <= p1:
            if p1 == p0:
                return r0
            return r0 + (r1 - r0) * (pct - p0) / (p1 - p0)
    return rows[-1][1]


def _zone_label(pct):
    """Zone name for a %VDOT, per the book's Table 5-4 brackets
    (E 59-74 / M 75-84 / T 83-88 / 10K 89-94 / I 95-100 / R 105-120). Shared
    edges: 83-84 is printed as both M and T -> shown as T; the table's own T
    paces back-solve to 88.1-89.0 %VDOT, so T extends to 89 (10K's lower edge);
    101-104 is not printed -> 'I+'."""
    if pct < 75:
        return "E"
    if pct < 83:
        return "M"
    if pct <= 89:
        return "T"
    if pct <= 94:
        return "10K"
    if pct <= 100:
        return "I"
    if pct <= 104:
        return "I+"
    return "R"


def points_for(points_rows, vdot, dist_m, seconds):
    """Points earned by one effort of dist_m metres in seconds at a given VDOT."""
    v_mmin = dist_m / (seconds / 60.0)
    pct = _vo2(v_mmin) / float(vdot) * 100.0
    rate = _points_rate(points_rows, pct)
    minutes = seconds / 60.0
    return {"pct_vdot": pct, "zone": _zone_label(pct),
            "rate_per_min": rate, "minutes": minutes, "points": rate * minutes}


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


# --- CLI modes: points / session / selfcheck -----------------------------------

def _resolve_effort(a, ap):
    """Effort spec -> (dist_m, seconds). Either --time + --distance, or
    --pace (min/km) + --minutes."""
    if a.time is not None and a.distance:
        dist_m = DIST.get(a.distance)
        dist_m = float(a.distance) if dist_m is None else dist_m
        return dist_m, float(a.time)
    if a.pace and a.minutes:
        sec_per_km = _parse_time(a.pace)
        dist_m = 1000.0 * (a.minutes * 60.0) / sec_per_km
        return dist_m, a.minutes * 60.0
    ap.error("give an effort as --time + --distance, or --pace + --minutes")


def _cmd_points(a, ap, points_rows, vdot, as_json):
    dist_m, seconds = _resolve_effort(a, ap)
    r = points_for(points_rows, vdot, dist_m, seconds)
    effort = f"{a.distance or ''} {_fmt_time(seconds)}".strip()
    if as_json:
        print(json.dumps({
            "vdot": round(vdot, 1), "effort": effort,
            "pct_vdot": round(r["pct_vdot"], 1), "zone": r["zone"],
            "rate_per_min": round(r["rate_per_min"], 3),
            "minutes": round(r["minutes"], 1),
            "points": round(r["points"], 1),
            "table": "data/vdot/intensity_points.csv (book Table 5-4)"},
            ensure_ascii=False, indent=2))
        return 0
    print(f"VDOT {vdot:.1f}  effort {effort}  (moving time)")
    print(f"  %VDOT {r['pct_vdot']:.1f}  ({r['zone']} zone)")
    print(f"  {r['rate_per_min']:.3f} points/min x {r['minutes']:.1f} min "
          f"= {r['points']:.1f} points")
    print("\nNotes: pace from MOVING time; walk breaks/stoplights inflate %VDOT - "
          "for interval sessions prefer the planned-session point target.")
    return 0


def _cmd_session(a, sessions, vdot, as_json):
    lo = max((int(r["vdot_lo"]) for r in sessions
              if int(r["vdot_lo"]) <= vdot), default=None)
    rows = [r for r in sessions
            if int(r["vdot_lo"]) == lo and int(r["points"]) == a.session]
    if not rows:
        raise SystemExit(f"no session bracket covers VDOT {vdot}")
    hi = int(rows[0]["vdot_hi"])
    order = {"L": 0, "M": 1, "T": 2, "I": 3, "R": 4}
    rows.sort(key=lambda r: (order[r["quality"]], float(r["amount"])))
    if as_json:
        out = {}
        for r in rows:
            out.setdefault(r["quality"], []).append(
                {"presc_key": r["presc_key"], "amount": float(r["amount"])})
        print(json.dumps({"points": a.session, "vdot_bracket": [lo, hi],
                          "caps": out}, ensure_ascii=False, indent=2))
        return 0
    print(f"Book Table 5-5: a {a.session}-point session, VDOT {vdot:.0f} "
          f"(bracket {lo}~{hi}) - max per quality:")
    for r in rows:
        amt = float(r["amount"])
        key = r["presc_key"]
        unit = "km total" if key == "km" else f"reps of {key[5:]}"
        print(f"  {r['quality']:<2} {amt:>6g} {unit}")
    print("\nAmounts are CAPS per quality; L/M/T(km) are total km, others are rep "
          "counts.\nScale with current weekly volume; warm-up/cool-down E running "
          "adds points too.")
    return 0


def _selfcheck():
    """Validate every table against the book's printed anchors. Exits non-zero
    on any failure so agents can gate commits on it."""
    fails = []

    def check(name, ok, detail=""):
        print(f"{'PASS' if ok else 'FAIL'}  {name}"
              + (f" - {detail}" if detail and not ok else ""))
        if not ok:
            fails.append(name)

    paces, races = _load_tables()
    pvd = {v for (v, _, _) in paces}
    rvd = {v for (v, _) in races}
    check("races/paces vdot range", pvd == rvd and min(pvd) == 20 and max(pvd) == 85)
    check("paces zones", {z for (_, z, _) in paces} == {"E", "M", "T", "I", "R"})

    pts = _load_points()
    check("intensity_points range", all(59 <= p <= 120 for p, _ in pts))
    check("intensity_points unique", len({p for p, _ in pts}) == len(pts))
    rates = [r for _, r in pts]
    check("intensity_points monotone", all(b >= a for a, b in zip(rates, rates[1:])))
    check("intensity_points 101-104 gap",
          not any(101 <= p <= 104 for p, _ in pts))
    anchors = {66: 0.200, 74: 0.333, 75: 0.350, 84: 0.583, 85: 0.600, 88: 0.683,
               92: 0.800, 100: 1.000, 105: 1.250, 120: 2.100}
    bad = [(q, v) for q, v in anchors.items()
           if abs(dict(pts).get(q, -1) - v) > 0.0005]
    check("intensity_points book anchors", not bad, str(bad))

    sess = _load_sessions()
    check("session points values",
          {int(r["points"]) for r in sess} == {10, 15, 20, 25, 30})
    grp = {}
    for r in sess:
        grp.setdefault((r["points"], r["quality"], r["presc_key"]), []).append(r)
    mono_bad = []
    for k, rs in grp.items():
        rs.sort(key=lambda r: int(r["vdot_lo"]))
        amts = [float(r["amount"]) for r in rs]
        if any(b < a for a, b in zip(amts, amts[1:])):
            mono_bad.append(k)
    check("session amounts monotone in vdot bracket", not mono_bad, str(mono_bad))
    book = {("10", "51", "L", "km"): 10.4, ("10", "51", "T", "km"): 4.0,
            ("20", "0", "T", "km"): 6.0, ("10", "0", "I", "reps_400m"): 5.0}
    bad = []
    for (pts_, lo, q, key), want in book.items():
        got = [float(r["amount"]) for r in sess
               if r["points"] == pts_ and r["vdot_lo"] == lo
               and r["quality"] == q and r["presc_key"] == key]
        if len(got) != 1 or abs(got[0] - want) > 1e-9:
            bad.append((pts_, lo, q, key, got))
    check("session book anchors", not bad, str(bad))

    # functional smoke: a VDOT-50 T-pace effort must read ~T zone
    r = points_for(pts, 50.0, 1000.0, _pace_per_km(paces, 50, "T"))
    check("points_for T-pace zone", r["zone"] == "T", f"got {r['zone']}")

    if fails:
        print(f"\nselfcheck FAILED: {len(fails)} group(s)")
        return 1
    print("\nselfcheck PASSED")
    return 0


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
    ap.add_argument("--points", action="store_true",
                    help="intensity-points mode: points earned by one effort "
                         "(needs --vdot or a race result, plus --time+--distance "
                         "or --pace+--minutes)")
    ap.add_argument("--time", type=_parse_time, default=None,
                    help="effort moving time, e.g. 48:30 (with --points)")
    ap.add_argument("--pace", default=None,
                    help="effort pace min/km, e.g. 4:00 (with --points --minutes)")
    ap.add_argument("--minutes", type=float, default=None,
                    help="effort moving minutes (with --points --pace)")
    ap.add_argument("--session", type=int, default=None, choices=[10, 15, 20, 25, 30],
                    help="session mode: max amounts per quality for an N-point "
                         "session (book Table 5-5), needs --vdot")
    ap.add_argument("--selfcheck", action="store_true",
                    help="validate all data/vdot tables against book anchors; "
                         "non-zero exit on failure")
    a = ap.parse_args()

    if a.selfcheck:
        return _selfcheck()

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

    if a.session is not None:
        return _cmd_session(a, _load_sessions(), vdot, a.json)
    if a.points:
        return _cmd_points(a, ap, _load_points(), vdot, a.json)

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
