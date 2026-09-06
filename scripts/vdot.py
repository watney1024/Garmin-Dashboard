# -*- coding: utf-8 -*-
"""
vdot.py — approximate Jack Daniels VDOT calculator (stdlib only).

What it does:
  - race result -> VDOT score
  - VDOT score  -> training pace bands (E / M / T / I / R) + equivalent race times
  - can regenerate data/vdot_table.csv from the same formulas
    (single source of truth: python scripts/vdot.py --gen-csv data/vdot_table.csv)

⚠ APPROXIMATE / 近似实现
The VO2 economy and %VO2max curves used below are the classic public-domain style
relationships reproduced by many community calculators (see docs/09_vdot_paces_zh.md).
The intensity percentages are our own calibration; exact numbers can differ from
the official printed Daniels' tables. Replace with an authoritative table when one
is available (TODO in data/vdot_table.csv).

Examples:
  python scripts/vdot.py --race-time 40:00 --distance 10k
  python scripts/vdot.py --vdot 48
  python scripts/vdot.py --5k 21:00
"""
import argparse
import json
import math
import os
import sys

# --- oxygen demand of running: VO2(ml/kg/min) from velocity v (m/min) ---------
def vo2_of_velocity(v_mmin):
    return -4.60 + 0.182258 * v_mmin + 0.000104 * v_mmin ** 2


# --- fraction of VO2max sustainable for a race of t minutes -------------------
def pct_vo2max(t_min):
    return (0.8
            + 0.1894393 * math.exp(-0.012778 * t_min)
            + 0.2989558 * math.exp(-0.1932605 * t_min))


def _solve_velocity(vo2):
    """Velocity (m/min) that demands a given VO2; quadratic solved for positive root."""
    # 0.000104 v^2 + 0.182258 v + (-4.60 - vo2) = 0
    a, b, c = 0.000104, 0.182258, -4.60 - vo2
    disc = b * b - 4 * a * c
    if disc < 0:
        return None
    return (-b + math.sqrt(disc)) / (2 * a)


# --- race distances (metres) --------------------------------------------------
DIST = {"1mile": 1609.34, "5k": 5000, "10k": 10000, "half": 21097.5,
        "marathon": 42195, "full": 42195}


def parse_time(s):
    """'H:MM:SS', 'MM:SS', 'M:SS' or plain seconds -> seconds."""
    if isinstance(s, (int, float)):
        return float(s)
    parts = [p for p in s.strip().split(":") if p != ""]
    if not parts:
        raise ValueError(f"bad time: {s!r}")
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    return float(parts[0])


def fmt_time(sec):
    sec = max(0, round(sec))
    h, r = divmod(sec, 3600)
    m, s = divmod(r, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def fmt_pace(sec_per_km):
    return fmt_time(sec_per_km)


def vdot_from_race(dist_m, time_s):
    """VDOT from an all-out race performance over a known distance."""
    v = dist_m / time_s * 60.0           # m/min
    t_min = time_s / 60.0
    return vo2_of_velocity(v) / pct_vo2max(t_min)


def equivalent_time(vdot, dist_m, lo=60, hi=6 * 3600, tol=0.05):
    """Bisect: the race time at this distance that yields `vdot`."""
    for _ in range(80):
        mid = (lo + hi) / 2.0
        if vdot_from_race(dist_m, mid) > vdot:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return (lo + hi) / 2.0


# --- intensity percentages of VDOT (our calibration, approximate) --------------
# E = easy range (slow bound .. fast bound), M = marathon, T = threshold,
# I = interval, R = repetition (short, faster than I).
PCT = {"E": (0.52, 0.62), "M": (0.80, 0.80), "T": (0.88, 0.88),
       "I": (1.00, 1.00), "R": (1.04, 1.04)}


def training_paces(vdot):
    """Return dict zone -> (low_s_per_km, high_s_per_km) where low <= high."""
    out = {}
    for zone, (lo_pct, hi_pct) in PCT.items():
        v_hi = _solve_velocity(lo_pct * vdot)   # slower speed -> slow bound
        v_lo = _solve_velocity(hi_pct * vdot)   # faster speed -> fast bound
        if v_hi is None or v_lo is None:
            continue
        slow = 1000.0 / v_hi * 60.0             # seconds per km
        fast = 1000.0 / v_lo * 60.0
        out[zone] = (slow, fast)
    return out


def cli():
    ap = argparse.ArgumentParser(
        description="Approximate Jack Daniels VDOT calculator (see module docstring).",
        epilog="Examples:\n"
               "  python scripts/vdot.py --race-time 40:00 --distance 10k\n"
               "  python scripts/vdot.py --vdot 48\n"
               "  python scripts/vdot.py --5k 21:00")
    ap.add_argument("--race-time", type=parse_time, default=None,
                    help="all-out race time, e.g. 40:00 or 1:23:45")
    ap.add_argument("--distance", default=None,
                    help="race distance: 5k, 10k, half, marathon (or metres)")
    ap.add_argument("--vdot", type=float, default=None,
                    help="direct VDOT score (skip the race conversion)")
    for dist, label in (("5k", "--5k"), ("10k", "--10k"),
                        ("half", "--half"), ("marathon", "--marathon")):
        ap.add_argument(label, type=parse_time, default=None,
                        help=f"shortcut: race time over {dist}")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--gen-csv", metavar="OUT.csv", default=None,
                    help="regenerate the vdot pace table CSV and exit")
    ap.add_argument("--min-vdot", type=float, default=30.0)
    ap.add_argument("--max-vdot", type=float, default=85.0)
    a = ap.parse_args()

    if a.gen_csv:
        gen_csv(a.gen_csv, a.min_vdot, a.max_vdot)
        return 0

    if a.vdot is None:
        if a.race_time and a.distance:
            dist_m = DIST.get(a.distance) or float(a.distance)
            vdot = vdot_from_race(dist_m, a.race_time)
            src = f"race {a.distance} {fmt_time(a.race_time)}"
        else:
            pairs = [(k, v) for k, v in
                     (("5k", a.__dict__.get("5k")), ("10k", a.__dict__.get("10k")),
                      ("half", a.__dict__.get("half")), ("marathon", a.__dict__.get("marathon")))]
            pairs = [(k, v) for k, v in pairs if v]
            if not pairs:
                ap.error("provide --race-time + --distance, --vdot, or a --<dist> shortcut")
            dist_m, t = DIST[pairs[0][0]], pairs[0][1]
            vdot = vdot_from_race(dist_m, t)
            src = f"race {pairs[0][0]} {fmt_time(t)}"
    else:
        vdot = a.vdot
        src = "given directly"

    zones = training_paces(vdot)
    eq = {d: equivalent_time(vdot, DIST[d]) for d in ("5k", "10k", "half", "marathon")}

    if a.json:
        print(json.dumps({
            "vdot": round(vdot, 1), "source": src,
            "paces": {z: [fmt_pace(zones[z][0]), fmt_pace(zones[z][1])]
                      for z in zones},
            "equivalent": {d: fmt_time(eq[d]) for d in eq},
        }, ensure_ascii=False, indent=2))
        return 0

    print(f"VDOT  {vdot:.1f}  (from {src})")
    print("-" * 46)
    for z in ("E", "M", "T", "I", "R"):
        if z in zones:
            lo, hi = fmt_pace(zones[z][0]), fmt_pace(zones[z][1])
            print(f"  {z:<2}  {lo} - {hi} /km")
    print("-" * 46)
    for d in ("5k", "10k", "half", "marathon"):
        print(f"  {d:<9} equiv {fmt_time(eq[d])}")
    print("\nApproximate values only (see scripts/vdot.py docstring + docs/09).")
    return 0


# ---------------------------------------------------------------------------
# regenerate the pace-table CSV
# ---------------------------------------------------------------------------
def gen_csv(path, vmin=30.0, vmax=85.0):
    header = "vdot,e_slow_minkm,e_fast_minkm,m_minkm,t_minkm,i_minkm,r_400m_sec"
    rows = [header]
    for v in range(int(round(vmin)), int(round(vmax)) + 1):
        z = training_paces(float(v))
        e_slow, e_fast = z["E"]
        vals = [
            str(v),
            f'{fmt_pace(e_slow)}',
            f'{fmt_pace(e_fast)}',
            fmt_pace(z["M"][0]),
            fmt_pace(z["T"][0]),
            fmt_pace(z["I"][0]),
            str(int(round(z["R"][0] * 0.4))),
        ]
        rows.append(",".join(vals))
    with open(path, "w", encoding="utf-8") as f:
        f.write("# approximate VDOT pace table (see scripts/vdot.py + docs/09).\n")
        f.write("# TODO: replace with an authoritative table when available.\n")
        f.write("\n".join(rows) + "\n")
    print("wrote", path, "rows", len(rows) - 1)


if __name__ == "__main__":
    sys.exit(cli())
