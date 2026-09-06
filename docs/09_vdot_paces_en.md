# 09 · VDOT: race results → training paces (for AI agents)

## 1. Concept & data

**VDOT** (Jack Daniels' system) turns one all-out performance into a "running ability
score", then maps it to **training paces/times** per intensity. Source concept: Jack
Daniels, *Daniels' Running Formula*.

This repo uses **two canonical tables** under `data/vdot/` (both tidy long format):

| file | row format | purpose |
|---|---|---|
| `data/vdot/vdot_races.csv` | `vdot, distance_m, seconds` | **result → VDOT**: find the equivalent race time |
| `data/vdot/vdot_paces.csv` | `vdot, intensity, distance_m, seconds` | **VDOT → training time/pace** (E/M/T/I/R × distances) |

- VDOT 30–85 in integer rows; non-integer VDOT is **linearly interpolated** by
  `scripts/vdot.py`.
- Half/marathon distances are stored in metres (`21097.5` / `42195`).
- ⚠ **License**: the table values derive from a **GPL-3.0** export — Zac Blanco's
  *VDOT Calculator* (see `data/vdot/README.md`, `NOTICE.md`, full text
  `data/vdot/GPL-3.0.txt`). Redistribution follows GPLv3; this is not a verbatim copy of
  the printed book tables.

## 2. Intensity zones

| zone | full name | purpose | VDOT 40 example (/km or ×distance) |
|---|---|---|---|
| E | Easy | aerobic base, largest share | `6:19`/km (fast-end reference; slower is fine) |
| M | Marathon | marathon-pace segments | `5:29`/km |
| T | Threshold | lactate threshold (cruise reps/continuous) | `5:06`/km (T/1000 = 1 km) |
| I | Interval | VO2max intervals (3–5 min reps) | `4:42`/km (I/1000 = 1 km) |
| R | Repetition | short speed/form (200–400 m, full recovery) | 400 m ≈ `1:46` |

> "R/km" shown by the tool is a per-km projection; when prescribing R, use the
> **time for the actual distance** (e.g. R/400 = 106 s).

## 3. Execution doctrine (important)

- **Low intensity (E/recovery)**: HR/feel is the only authority, time is the fallback. The
  `E/km` table value is only the **fast-end reference floor** — running easy slower is
  always allowed. In hot weather / poor form, switch fully to "HR mode".
- **Quality (M/T/I/R/race segments)**: prescribe from the table values (band); distance
  sets the load, HR is an alarm.
- Always prescribe from the **current** VDOT, never an aspirational target.

## 4. How to use it (`scripts/vdot.py`)

```bash
# result → VDOT (standard distances: from the vdot_races table)
python scripts/vdot.py --5k 23:45
python scripts/vdot.py --race-time 1:52:30 --distance half
# VDOT → training paces/times + race equivalents (vdot_paces / vdot_races)
python scripts/vdot.py --vdot 40
python scripts/vdot.py --vdot 40 --json
```

- Standard distance names: `1500 1mile 3000 2mile 5k 8k 5mile 10k 15k 10mile 20k half 25k
  30k marathon`.
- Non-standard distances (e.g. 6k) fall back to the classic running-economy equations only
  to estimate VDOT; training paces still come from the tables (interpolated).
- Example (VDOT≈40): E 6:19 / M 5:29 / T 5:06 / I 4:42 / R400≈106 s; equivalents 5K 24:08 /
  10K 50:03 / half 1:50:59 / marathon 3:49:45.

## 5. Deriving VDOT from the profile's PRs (see also docs/08)

1. Take the most recent (<6 months), most trustworthy result from `pr` and run it through
   `vdot.py`.
2. Cross-check the other PRs: they should agree within ~1. If they differ by more, use the
   most recent all-out effort and explain the gap to the runner.
3. Optional TODO: when several distances exist, weight by the goal distance (marathon goal
   → marathon PR weighted higher). Currently the single most trustworthy/recent is used.
4. After an A/attempt race, write the new time into `pr`, recompute VDOT; a change of ≥1
   warrants proposing a pace update through the weekly review.

## 6. Notes

- Values come from a third-party GPL-3.0 export; individual rows may differ from the
  printed book by ~1–2 s. If you obtain a directly licensable/public-domain authoritative
  version, replace the files under `data/vdot/` (keep the tidy schema).
- When reporting paces, agents cite the source (e.g. "data/vdot tables, VDOT 40") rather
  than claiming book-perfect values.
