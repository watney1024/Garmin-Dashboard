# Arthur Lydiard system `lydiard`

> ⚠ **Provenance & copyright**: this file is this repo's **summary + application guide**
> of Arthur Lydiard's training ideas, not a copy/excerpt of his books (e.g. *Running to
> the Top*) or other sources.

## 1. Origin & fit

- Source: Arthur Lydiard (New Zealand coach whose athletes dominated middle/long distance
  in the 1950s–60s); books such as *Running to the Top*.
- Core idea: **build the aerobic base as large as possible first, then add speed**. A
  typical macro-cycle: a ~4-month base/conditioning phase (lots of easy running and LSD,
  volume builds aerobic adaptations) → **hill work** (strength + aerobic power) →
  **track speed/sharpening** (400–800 m intervals) → racing; for the marathon, long
  "marathon-conditioning" runs (roughly 20–35 km aerobic) run through the cycle.
- **Good for**: runners with plenty of time (≥6–8 h/week) who can sustain high volume;
  half/marathon-focused runners with 3–6 months of patience.
- **Not for**: runners limited to 3–4 runs/week or <5 h; the impatient (this system is
  "slow first, fast later" — almost no speed work early on).

## 2. Intensity system & pace source

| type | code | basis | typical session |
|---|---|---|---|
| Easy / base | E | HR/feel, conversational; LSD long | `E 40–90 min`, weekend `LSD 16–30 km` |
| Hill running | H | uphill "strength running" | `5–10×200–400 m uphill` + jog down |
| Speed / interval | I | 400–800 m reps (sharpening) | `6–10×400` (full recovery) |
| Fartlek | F | surges inside easy runs | `E run with 8×1 min pick-ups` |

- Pace source: **base and LSD are all "HR/feel + time", not pace** (the biggest difference
  from the VDOT school); hill and interval sessions may reference the matching zones of the
  `data/vdot/` tables (docs/09).
- Shape: ≥90% of time at low intensity in the base phase; grouped speed sessions only
  appear in the sharpening phase.

## 3. Weekly skeleton construction

Given the profile's `runs_per_week / long_run_day / quality_days`:

1. Base phase (recommend ≥6–8 weeks): almost all E/LSD — every runnable day is E;
   `long_run_day` gets the biggest LSD; **no T/I**. If the profile lists one quality day,
   treat it as E for now.
2. Hill phase (4–6 weeks): `quality_days` hosts 1–2 hill sessions (instead of speed work);
   the rest stays E/LSD.
3. Sharpening/race phase: `quality_days` host I intervals (400–800 m) or fartlek; the long
   run becomes a goal-specific endurance run.
4. A single LSD starts near 25–30% of weekly volume; peaks stay within the generic safety
   layer. **Volume ramps more conservatively in base (≤10%) because the load is time, not
   intensity**.
5. Push only E/LSD/long runs to the watch; hill/interval sessions are route-based self
   workouts and don't need to be scheduled into Garmin.

## 4. Periodization & volume ramp

- Reference structure (operationalised here): **base 6–8 weeks** (all E, LSD progressively
  longer) → **hill 4–6 weeks** (keep volume; hills replace part of E time) →
  **sharpening ~4 weeks** (I intervals in, volume slightly down) → **race/taper 2–3 weeks**
  (volume −30–50%, keep one short speed session for the nervous system).
- Marathon-specific: keep the weekend LSD in the 24–32 km range across hill/sharpening;
  never exceed the safety layer's single-run cap chasing one very long run.
- Hot weather / poor form: retreat to "HR mode" E — this system is mostly E anyway, so
  retreating costs little.

## 5. Tests & gates

- Use the profile's non-A races: a 5K/10K at the *end of base* tests whether the base is
  truly built (no all-out effort required — look for natural aerobic-pace improvement); a
  half marathon 6–8 weeks out serves as a specific session.
- **This package's gates** (stack on top of the generic docs/06 gates, may be stricter):
  - Gate A: did the end-of-base 10K or weekend LSD pace-drift improve? If yes, enter the
    hill phase; if not, extend the base.
  - Gate B: in late sharpening, can `8×400` be held near the target pace without falling
    apart? This decides the race-day target band.
- For marathon goals, judge by long-run quality first, not interval speed.

## 6. Red lines & cautions

- **No early speed sessions in the base phase**: the #1 way this system fails is adding
  them too soon.
- Hill/interval quality work is "little but sharp": no back-to-back quality days; the
  yellow/red & injury rules still apply (docs/03/06).
- High volume ≠ unlimited volume: weekly increases, single-run share and recovery weeks all
  stay inside the generic safety layer.
- May only be stricter than the generic layer, never looser.

## 7. Strength / auxiliary advice

- This system prizes overall physical conditioning beyond running: 2×/week strength /
  core / flexibility coexist with the base phase; hill running itself is the best
  "strength running", so it can absorb part of the lower-body strength session volume.

## 8. Worked example

If the example runner picked this system with 6 runs/week: base phase
`Mon E60 · Tue E50 · Wed E60+ST · Fri E50 · Sat E40 recovery · Sun LSD 16–24`; the hill
phase swaps Wednesday for `uphill 8×200 m`, and the sharpening phase swaps it for
`6–8×400`.

## 9. Mandatory checks (post-generation self-check)

1. **Intensity composition**: verify against the current phase — base phase ≥90% low
   intensity with **zero T/I**; hill phase 1–2 hill sessions + the rest E/LSD; grouped
   intervals only in the sharpening phase. A phase mismatch (speed work inside base) means
   rebuild the week.
2. **Fatigue quantification & management**: quantify fatigue via weekend-LSD pace drift +
   morning HR/HRV; base-phase ramps stay ≤10%; on fatigue signals retreat the whole block to
   "HR-mode E" — this system has the cheapest retreat of all.
3. **Micro/macro cycles**: micro = all E (base) or 1–2 hill/interval sessions (matching
   phase) + weekend LSD; macro = base 6–8 weeks → hill 4–6 weeks → sharpening ~4 weeks →
   taper 2–3 weeks; phases are joined by Gates A/B.
4. **Easy-run doctrine**: the strictest of all four — base phase and LSD use **HR and time
   only**, with no pace targets at all and no judgment by distance/speed; pace is referenced
   against the VDOT tables only in hill/interval sessions.
