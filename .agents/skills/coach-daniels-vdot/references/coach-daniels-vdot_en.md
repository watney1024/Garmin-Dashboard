# Daniels VDOT `daniels_vdot`

> ⚠ **Provenance & copyright**: this file is this repo's **summary + application guide**
> of the ideas in Jack Daniels' *Daniels' Running Formula*, not a copy/excerpt of the
> book. Pace numbers come from the tables in `data/vdot/` (a GPL-3.0-derived VDOT
> export — see `data/vdot/README.md`; not a verbatim copy of the book). This
> package drives the example runner's plan.

## 1. Origin & fit

- Source: Jack Daniels, *Daniels' Running Formula* (3rd/4th editions)
- Core idea: describe current ability with **one VDOT score**, then derive **every
  training intensity's pace** from it; training is "quality (Q) sessions + lots of easy
  (E)"; ability iterates as VDOT rises.
- **Good for**: runners with a clear goal distance who can calibrate with an all-out
  result; runners who like paces being traceable to data.
- **Not for**: runners unwilling/unable to race or do maximal time trials (no result → no
  VDOT updates); pace-anxious runners (E days get run too fast).

## 2. Intensity system & pace source

| type | code | basis | typical session |
|---|---|---|---|
| Easy | E | VDOT E band + conversational feel; HR as alarm | `E 40–60 min` / `E 8 km` |
| Marathon | M | VDOT M pace | `M segment 10–14 km` at the end of a long run |
| Threshold | T | VDOT T pace | `2×20 min T + 5 min jog`, or cruise intervals |
| Interval | I | VDOT I pace | `5×1000 I, rest ≈ rep time` / `8×400` |
| Repetition | R | VDOT R (200–400 m, full recovery) | `8×200 R` for form/cadence |

- Pace source: **always look up `data/vdot/`** (`scripts/vdot.py`); never
  guess paces.
- Shape: **E runs are the volume backbone** (≥70% of time); 1–2 Q sessions per week
  (T/I/R and long runs containing M segments); R keeps form & neural speed, low volume.

## 3. Weekly skeleton construction

Given the profile's `runs_per_week / long_run_day / quality_days`:

1. `quality_days` (default 1) gets the **Q session**: if short Q (T or I), cap the day at
   60–70 min; if the runner has only one quality day, prefer T / long-with-M over
   squeezing in I.
2. `long_run_day` gets the **long run**: M segments at target pace for the last third;
   pure-E long runs follow "HR + feel".
3. Remaining runnable days get E; work backwards from the long-run day to offset quality
   (no long session or heavy lower-body work the day before a Q day).
4. Weekly volume increases ≤10% by default in this package (conservative); never above the
   generic safety cap.
5. Long single starts near 20–30% of weekly volume; peaks stay under the generic safety
   ceiling (and under the 55% red line). For VDOT<40 runners cap peak long runs at
   24–26 km.

## 4. Periodization & volume ramp

- Reference structure (this repo's operationalisation): **foundation** (3–6 weeks, E +
   long only, low side of the VDOT bands) → **quality** (introduce Q; M segments enter the
   long run) → **peak/taper phase** (peak week with the longest run) → **taper** (2–3
   weeks before the race: volume down, intensity kept).
- Every 4–6 weeks or after a test race: re-test VDOT and refresh the whole pace table.
- Hot weather / poor form: switch everything to "HR + feel" (docs/03); E pace is only a
   reference.

## 5. Tests & gates

- Use the profile's non-A races as tests (attempt = committed; training = not all-out).
- **This package's gates** (add to the generic gates in docs/06, may be stricter):
  - Gate A: a mid-cycle 5K/10K test sets the VDOT; if it is ≥2 below the plan's
    assumption → lower the target & all paces.
  - Gate B: the longest "long run with M segments" (two weeks before peak) — is the last
    third M segment stable? If not, race-day starts conservative (**one-vote veto**, same
    as the docs/06 gate).
- For race-day target conversion, avoid pure Riegel extrapolation: for runners with
   unbalanced speed/endurance, VDOT equivalent times are closer to reality.

## 6. Red lines & cautions

- **Never train at an aspirational VDOT**: paces always come from the current VDOT.
- Running E too fast is this school's #1 mistake: the E ceiling is a ceiling, don't chase
  "faster easy runs".
- I workouts must be "fast but not too much": fewer reps beats sloppy ones; stop the set
  the moment form breaks.
- May only be stricter than the generic safety layer, never looser (docs/03/06).

## 7. Strength / auxiliary advice

- Strength is a supplement: 1–2 sessions/week; lower-body main lifts + calf/glute-medius/
  core as the floor (respect the profile's strength field).
- No heavy lower-body work within ±24 h of an I/T quality day (same as the generic red
  line).

## 8. Worked example

Example runner (VDOT≈40): `W1 Tue E5 · Thu E5 · Fri E5 recovery · Sun Long 13 (E)`;
quality-phase week looks like: `Tue T 4×6 min · Thu E · Fri E · Sun Long 18 (E + M4)`.

## 9. Mandatory checks (post-generation self-check)

1. **Intensity composition**: E ≥70% of time; ≤2 Q sessions/week (an M segment inside the
   long run counts as half a Q); R stays small, form-only. When over the cap, cut R/I
   first, then T — never touch E or the long run.
2. **Fatigue quantification & management**: fatigue is read from "Q-session quality + HR
   drift on E runs"; re-test VDOT every 4–6 weeks; the day before a Q is always E/rest;
   two consecutive weeks of failed Q → drop to a single Q that week.
3. **Micro/macro cycles**: micro = 1–2 Q + plenty of E + long run; macro = base → quality →
   peak → taper; a recovery week every 4 weeks (volume −20–30%, keep one short Q).
4. **Easy-run doctrine**: E sessions are judged by **HR and time** — being slower than the
   E pace is fine, being faster is the error; the VDOT E value is a fast-end reference
   ceiling, not a target.
