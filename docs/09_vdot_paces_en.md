# 09 · VDOT: race results → training paces (for AI agents)

## 1. Concept & data

**VDOT** (Jack Daniels' system) turns one all-out performance into a "running ability
score", then maps it to **training paces/times** per intensity. Source concept: Jack
Daniels, *Daniels' Running Formula*.

This repo uses **four canonical tables** under `data/vdot/` (all tidy long format):

| file | row format | purpose |
|---|---|---|
| `data/vdot/vdot_races.csv` | `vdot, distance_m, seconds` | **result → VDOT**: find the equivalent race time |
| `data/vdot/vdot_paces.csv` | `vdot, intensity, distance_m, seconds` | **VDOT → training time/pace** (E/M/T/I/R × distances) |
| `data/vdot/intensity_points.csv` | `pct_vdot, points_per_min` | **intensity points** (book Table 5-4): points earned per minute at a given %VDOT — see §7 |
| `data/vdot/session_prescriptions.csv` | `points, vdot_lo, vdot_hi, quality, presc_key, amount` | **N-point session caps** (book Table 5-5): max amount per quality in a session worth N points — see §7 |

- VDOT 20–85 in integer rows; non-integer VDOT is **linearly interpolated** by
  `scripts/vdot.py`. VDOT 20–29 is the beginner band (see `data/vdot/README.md`: R/I/T/M
  cells follow the beginner table of Daniels' book; unprinted cells such as E are
  formula-derived).
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
# intensity points: points earned by one effort at its actual pace (see §7)
python scripts/vdot.py --points --vdot 48 --time 48:30 --distance 10k
python scripts/vdot.py --points --vdot 48 --pace 4:00 --minutes 40
# per-quality caps for an N-point session (Table 5-5, see §7)
python scripts/vdot.py --session 15 --vdot 52
# validate every table against the book's anchors (run after touching data/vdot)
python scripts/vdot.py --selfcheck
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

## 7. Training intensity points (load; book Tables 5-4 / 5-5)

Daniels quantifies training load with **points**: the higher an effort's %VDOT and the
longer it lasts, the more points it earns.

- **%VDOT definition**: `%VDOT = VO2(actual pace) / current VDOT x 100`. VO2 comes from the
  classic running-economy equations (`_vo2` in `vdot.py`). Calibrated against our own
  tables: the E/M/T/I/R paces back-solve to ≈67% / 78–84% / ≈88–89% / ≈97–99% / ≈104%+,
  matching Table 5-4's brackets.
- **Points table** (`intensity_points.csv`, transcribed from Table 5-4): points per minute
  at each integer %VDOT. Brackets: E 59–74, M 75–84, T 83–88 (identical values where it
  overlaps M), 10K 89–94, I 95–100, R 105–120. 101–104 is not printed in the book — the
  script interpolates across the gap and clamps outside 59–120.
- **Simplified anchors** (given in the same book section for quick math): E 0.2 / M 0.4 /
  T 0.6 / 10K 0.8 / I 1.0 / R 1.5 points per minute. Use anchors for mental estimates;
  the graded table (`--points`) is authoritative for records.
- **Weekly anchors** (book): beginners ~50 points/week, after a year or two ~100,
  university level ~150, beyond that 200+. Raise the weekly target gradually, like mileage.
- **Computation procedure (weekly review, see docs/06)**:
  1. Per activity: pace always from **moving time** (docs/02 pitfall) →
     `--points --vdot <current VDOT> --time <moving time> --distance <metres or name>`;
  2. Weekly total = sum over activities; also record the per-zone (E/M/T/I/R) split;
  3. Compare against the plan's weekly point target (if the coach package sets one) and
     write it into the review's "trends" section.
- **Distortion warning (read this)**: stoplights / walk breaks / hills inflate the average
  pace → inflate %VDOT → inflate points. Doctrine: cap a walk-break session's %VDOT at the
  planned zone's upper edge (an E run earns at most E-top points); an **interval session's
  whole-session average pace is meaningless** — record the planned session's point target
  (look it up with `--session`, Table 5-5), or compute per-lap from the inbox CSV when
  precision matters. Points always yield to HR/feel and the safety layer (docs/03/06);
  they inform trends and within-coach volume tuning only and **never relax any
  yellow/red rule**.
- **Session construction (Table 5-5, `--session N`)**: given a target score and VDOT
  bracket, prints each quality's amount cap (L/M/T(km) are total km; `reps_*` are rep
  counts). The daniels coach uses it to bound "how much fits in one quality session",
  then scales to the current weekly volume. Column semantics and source quirks:
  `data/vdot/README.md`.
- Provenance: both tables are transcribed from the Chinese edition's Tables 5-4/5-5 (the
  local scan stays out of the repo); the simplified and weekly anchors are the book's own
  printed numbers.

## 8. Age/sex correction (book Tables 5-6 / 5-7 / 5-8)

- **Data** (data gate: enabled only once `--selfcheck` group B passes):
  - `vdot_levels.csv` (`sex,level,vdot`): the Table 5-6 mapping of levels 1–10 to VDOT,
    different per sex;
  - `vdot_age_grades.csv` (`sex,age,level,pace_1609_s`): Tables 5-7 (ages 6–17) and 5-8
    (ages 18–58) merged; the value is the 1.6 km time for that sex/age/level. Ages 18–38
    are constant (the base); from 39 on, one row per year of age.
- **Algorithm** (`--age N --sex F|M`): raw VDOT → 1.6 km equivalent time (races table) →
  locate the level within the (sex, age) row by time (linear interpolation between levels,
  extrapolation at the edges) → base VDOT from the level table = the **age-graded VDOT**.
- **Pace policy (repo convention)**: when the age-graded VDOT differs from the raw one,
  **training paces come from the age-graded VDOT**; both values are printed for reference.
- **When to apply**: the profile has `identity.birth_year` + `identity.sex` and the
  computed age falls outside 18–38 (6–17 use the youth table, 39–58 the masters table);
  below 6 or above 58 there is no adjustment (stated in the output).
- **Limits**: this is a population-statistical grading, not a personal measurement; E/recovery
  runs remain HR/feel-first (§3); interval/repetition amount caps are looked up at the
  age-graded VDOT. Multi-result weighting (§5 item 3 TODO) is out of scope here.
- **Validation anchors** (selfcheck group B): 10-year-old F 1.6 km 7:18 = level 6;
  18-year-old F 5:28 = level 6; 18-year-old M 4:55 = level 6; 58-year-old F 7:00 ≈ young-F
  5:04; level table back-solves to 1.6 km: F L1=8:49, M L1=8:01 (±3 s).
