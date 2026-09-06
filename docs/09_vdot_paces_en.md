# 09 · VDOT: race results → training paces (for AI agents)

## 1. Concept

**VDOT** (from Jack Daniels' system) is a "running ability index": it is derived from one
all-out race performance and its unit ≈ VO₂max. It collapses a runner's ability into a
single number, then that number maps to **target paces for each training intensity**.
Source: Jack Daniels, *Daniels' Running Formula* — this repo only summarises it and ships
tools; it does not copy the original tables (see "approximation statement" below).

Uses:
- Take ≥1 PR (5K/10K/half/marathon) → VDOT → **E/M/T/I/R paces**.
- On easy/recovery days the execution doctrine stays **HR/perceived-effort first**
  (safety layer & doctrine in docs/03/06); VDOT's E pace is a reference floor. **Quality
  sessions (T/I/R and M segments) are prescribed by VDOT paces.**
- Test-race results → conversion → target updates (gates in docs/06).

## 2. Intensity zones (approximate; what each is for)

| Zone | full name | purpose | VO2 fraction (this tool, approx) |
|---|---|---|---|
| E | Easy | aerobic base, largest share | ≈52–62% |
| M | Marathon | marathon-pace segments | ≈80% |
| T | Threshold | lactate threshold (continuous 20–40 min or cruise reps) | ≈88% |
| I | Interval | VO2max intervals (3–5 min reps) | ≈100% |
| R | Repetition | short speed/form work (200–400 m, full recovery) | ≈104% |

Example (VDOT 40 row from `data/vdot_table.csv`):

```
E  6:44 – 7:42 /km     M  5:30 /km     T  5:06 /km
I  4:36 /km            R 400m ≈ 107 s
```

## 3. Tooling & data

- `scripts/vdot.py`: `--5k 23:45` / `--race-time 1:52:30 --distance half` / `--vdot 40`;
  `--json` output; `--gen-csv` regenerates the table.
- `data/vdot_table.csv`: rows = VDOT 30–85 (step 1), columns =
  `e_slow_minkm, e_fast_minkm, m_minkm, t_minkm, i_minkm, r_400m_sec`.

### Conversion method (transparent & reproducible)

The tool uses the widely shared running-oxygen and race-duration-fraction relationships
used by many community calculators, plus this repo's calibrated intensity fractions:

```
running VO2 cost: VO2 = -4.60 + 0.182258·v + 0.000104·v²     (v in m/min)
race sustainable fraction: %VO2max = 0.8 + 0.1894393·e^(-0.012778·t)
                                  + 0.2989558·e^(-0.1932605·t)   (t in minutes)
race VDOT = VO2 ÷ %VO2max
intensity pace = solve VO2(v) = fraction × VDOT for speed v
```

## 4. ⚠ Approximation statement (must be conveyed to users)

- `data/vdot_table.csv` and `vdot.py` are an **approximation**: the intensity fractions
  are our calibration against public descriptions, not book-perfect values; individual
  rows may differ from the official printed tables by up to ~10–20 s/km.
- The official Jack Daniels tables are copyrighted; this repo **does not copy them**. The
  CSV header carries `TODO: replace with an authoritative table when available` — with
  licensed authoritative data, either regenerate via
  `python scripts/vdot.py --gen-csv data/vdot_table.csv` or replace the CSV directly
  (when `vdot.py` reads the table, the table wins).
- When reporting paces, agents state: "approximate VDOT paces, roughly ±10–20 s/km".

## 5. How to use it

### Deriving VDOT from the profile
1. Read `pr` from `runner_profile.yaml`.
2. Run each result through `vdot.py`; **use the most trustworthy/recent as the VDOT**, the
   others as cross-checks (should agree within ~1).
3. If results differ by >1: prefer the most recent all-out effort; explain the gap to the
   runner (cycle phase / form differences).

### Consistency rules
- PRs carry dates; **results older than 6 months are not the sole basis**.
- After an A/attempt race: record the new time → recompute VDOT; a change of ≥1 warrants
  proposing a pace update through the weekly review.
- Always prescribe from the **current** VDOT, never an aspirational target VDOT.

### When generating a plan
- Write the resolved E/M/T/I/R paces into the plan's "intensity system & paces" chapter
  (slot defined in docs/05).
- In hot weather / poor form, switch everything to "HR + feel" (E pace is only a
  reference), consistent with docs/03.
