# Daniels VDOT `daniels_vdot`

> ⚠ **Source & Copyright Notice**: This file is the repository's **summary + application guide**
> of Jack Daniels' *Daniels' Running Formula* philosophy, NOT a copy or excerpt of the original
> book. Pace values are derived from `data/vdot/` (GPL-3.0 exported VDOT data, see
> `data/vdot/README.md`, not a direct reproduction of the book).

## 1. Source & Applicability

- Source: Jack Daniels, *Daniels' Running Formula* (3rd/4th ed.)
- Core thesis: Use **one VDOT score** to uniformly describe current ability, from which every
  training intensity gets a direct pace prescription. Training revolves around "quality sessions
  (Q) +大量 easy runs (E)"; ability improves as VDOT rises and the table iterates.
- **Suitable for**: Runners with a clear target distance and an all-out race result for calibration;
  those who prefer "paces backed by data."
- **Not suitable for**: Runners unable/unwilling to do time trials or all-out races (no result =
  no VDOT update); pace-anxious runners (E runs get run too fast).

## 2. Intensity System & Pace Sources

| Type | Abbr | Intensity Basis | Typical Session |
|---|---|---|---|
| Easy | E | VDOT E pace range, conversational; HR as alert | `E40–60min` / `E8km` |
| Marathon | M | VDOT M pace | Last 1/3 of long run `M 10–14km` |
| Threshold | T | VDOT T pace | `2×20min T + 5min jog` or cruise intervals |
| Interval | I | VDOT I pace | `5×1000 I, rest≈work time` / `8×400` |
| Repetition | R | VDOT R (200–400m, full recovery) | `8×200 R` for form & leg speed |

- Pace source: **always consult `data/vdot/`** (`scripts/vdot.py`), never guess.
- Structure: **E runs dominate volume** (≥70% by time); 1–2 Q sessions/week (including T/I/R
  and long runs with M segments); R is small-volume, for maintaining form and speed neuromuscular
  patterning.
- **8 training principles** (Daniels): (1) train the weakest link, (2) specific training,
  (3) moderate stress → positive adaptation, (4) stress is cumulative, (5) adaptation is
  individualized, (6) break systems selectively, (7) maintain core fitness, (8) hard/easy
  day alternation.
- **Training type ceilings**: E max 150 min; T ≤10% of weekly volume; I ≤min(10km, 8% weekly
  volume); R ≤min(8km, 5% weekly volume).
- **Intensity scoring** (points per minute): E=0.2, M=0.4, T=0.6, I=1.0, R=1.5 — used to
  quantify weekly load (beginners ~50 points/week, advanced ~100, elite 200+).
  **Records use the full graded table** (per-%VDOT points from the same book Table 5-4):
  `vdot.py --points` (data: `data/vdot/intensity_points.csv`; doctrine & distortion
  handling in docs/09 §7); the anchors are mental-math only. Quality-session amount caps
  come from Table 5-5: `vdot.py --session N` (data: `data/vdot/session_prescriptions.csv`).
- **6-second rule**: if you can't speak a 6-word sentence, you're above E intensity.
- **Phase progression order**: E → R → I → T (build easy base first, then speed, then VO2max,
  then threshold).

## 3. Weekly Skeleton Construction

Input from runner profile: `runs_per_week / long_run_day / quality_days`:

1. `quality_days` (default 1) holds **Q sessions**: if short Q (T or I), session ≤60–70 min;
   if runner has only 1 quality day, prioritize T/long-run-with-M, don't force I.
2. `long_run_day` holds **long run**: with M segments, run last 1/3 at target pace; pure E long
   run uses "HR + perceived effort."
3. Other available days get E runs; stagger intensity backward from long run day (no long/heavy
   strength day before Q).
4. Weekly volume increase ≤10% (this package is more conservative); when exceeding general safety
   layer caps, safety layer prevails.
5. Single long run ≈20–30% of weekly volume to start, peak ≤ general safety cap; for VDOT<40
   runners, peak long run ≤24–26km.

## 4. Periodization & Volume Progression

- Reference structure (repository implementation): **Base phase** (3–6 weeks, pure E + long runs,
  lower VDOT range) → **Quality phase** (add Q sessions, M segments enter long runs) →
  **Peak/Sharpening phase** (peak week includes longest distance) → **Taper** (2–3 weeks
  pre-race, reduce volume maintain intensity).
- Four named phases: B/FIP (Base/Foundation & Initial Preparation) → IQ (Intensity Quality) →
  TQ (Threshold Quality) → FQ (Final Quality / sharpening).
- Every 4–6 weeks or after a time trial: retest VDOT, update all paces.
- **2Q marathon plan VDOT progression**: target−2 → +1 → +1 across phases.
- Hot weather / poor form: switch entirely to "HR + perceived effort" (docs/03), E pace only
  as reference.
- Post-race recovery: every 3km raced = 1 E day of recovery.
- Half marathon pace ≈ T pace.

## 5. Test Races & Gates

- Use non-A races in profile as tests (role=attempt all-out; training not all-out).
- **Package gates** (combined with docs/06 general gates, may be stricter):
  - Gate A: Mid-cycle 5K/10K test → sets VDOT; if ≥2 lower than plan assumption → lower
    target/paces globally.
  - Gate B: Longest "long run with M segment" (2 weeks before peak) → can last 1/3 M segment
    hold pace? If not → conservative race start (**veto power**, consistent with docs/06).
- Race-day target conversion: avoid pure Riegel; runners with uneven speed/endurance use VDOT
  equivalent performance for closer estimates.

## 6. Red Lines & Cautions

- **Never run with target VDOT today**: paces always come from current VDOT.
- **Running E too fast is the #1 mistake** in this system: E upper pace is a ceiling, don't
  chase "faster easy runs."
- **I sessions: fast enough but not too much**: fewer reps is better than too many; stop when
  form breaks down.
- Can only be stricter than general safety layer, never relax (docs/03/06).

## 7. Strength & Auxiliary Recommendations

- Strength is supplementary by default: 1–2×/week, lower-body main lifts + calf raises/glute
  medius/core as baseline (matching runner profile strength field).
- No heavy lower-body lifting within ≥24h before/after I/T sessions (consistent with general
  red lines).

## 8. Application Example

Sample runner (VDOT≈40): `W1 Tue E5 · Thu E5 · Fri E5 recovery · Sun Long13(E)`;
quality phase week: `Tue T 4×6min · Thu E · Fri E · Sun Long18(E+last 4km M)`.

## 9. Mandatory Checks (Post-Generation Self-Test)

1. **Intensity composition**: By time E ≥70%; Q ≤2 sessions/week (M segment in long run counts
   as half Q); R volume small, form only. When exceeding caps, delete R/I first, then reduce T,
   never touch E or long runs.
2. **Fatigue quantification & management**: Measure via "Q session completion quality + E run
   HR drift + weekly intensity-points total" (weekly total computed with `vdot.py --points`
   on the full graded table); retest VDOT every 4–6 weeks; day before Q must be E/rest; if Q
   cannot be completed 2 consecutive weeks → reduce to single Q that week.
3. **Macro/micro cycles**: Micro = 1–2 Q + lots of E + long run; Macro = Base → Quality →
   Peak → taper; recovery week every 4 weeks (volume down ~20–30%, keep 1 short Q).
4. **Easy run standard**: E runs judged by **HR and time only**; pace not meeting target is not
   an error, running too fast is; VDOT E value is a fast-end reference ceiling, not a target.
