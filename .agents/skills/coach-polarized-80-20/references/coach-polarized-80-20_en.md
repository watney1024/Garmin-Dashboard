# Polarized 80/20 `polarized_80_20`

> ⚠ **Provenance & copyright**: this file is this repo's **summary + application guide**
> of the ideas in Matt Fitzgerald's *80/20 Running*, not a copy/excerpt of the book. The
> "20%" refers to moderate+high intensity and is expressed here with a three-zone model.

## 1. Origin & fit

- Source: Matt Fitzgerald, *80/20 Running* (building on Stephen Seiler's polarized
  training research)
- Core idea: most elite runners spend **~80% of training time at low intensity and ~20% at
  moderate+high intensity**; the *distribution* of intensity matters more for long-term
  progress and injury trade-offs than how hard any single session is.
- **Good for**: volume-oriented amateurs, over-training-prone or injury-prone runners; those
  who want to build mileage without wrecking themselves.
- **Not for**: runners with very little time (<3.5 h/week) chasing fast results — without
  volume this school's edge disappears; runners who hate running slowly.

## 2. Intensity system & pace source

| type | code | basis | typical session |
|---|---|---|---|
| low | Z1/Z2 | **HR/feel first**; can speak in full sentences | `E 40–70 min` / long run |
| moderate | mid Z2/Z3 | near threshold, no peaking | rare `T segment 15–20 min` (≤1/week) |
| high | Z3 | I or race pace | rare `6–8×400 I` (≤1/week, alternate weeks with T) |

- Pace source: low intensity uses **HR zones + feel** (VDOT E pace only as a reference
  floor, see docs/09); the few quality sessions use VDOT T/I paces.
- **Three-zone model** (Fitzgerald's 3-zone variant): Zone 1 = low (≈E), Zone 2 = medium
  (≈M/low T), Zone 3 = high (≈upper T/I). **80/20 is measured in TIME**, not distance.

## 3. Weekly skeleton construction

1. The skeleton is mostly **E/long runs**; `quality_days` gets that week's single quality
   session (T or I, not both).
2. `long_run_day` is the biggest E/long run; **keep ≥48 h between hard days**.
3. After each week, roughly check the intensity split **by time** and steer toward 80/20;
   if it drifts (hard >25%) drop a quality session rather than speeding up E runs.
4. Volume +10–15%/week max, obeying the generic safety layer.

## 4. Periodization & volume ramp

- The cycle's main line is the **volume ramp**: base phase (low intensity) → build →
  occasional quality → taper (drop volume, keep frequency, a little intensity may stay).
- This school does not rely on several consecutive high-quality peak weeks; it banks
  **sustained high-volume low-intensity** training instead.

## 5. Tests & gates

- Use non-A races/time trials as tests (attempt = committed); **the result sets the VDOT
  and goal but does not change the 80/20 split**.
- This package's gate: if the hard-intensity share exceeds 25% of time for two consecutive
  weeks → cut it back to ≤20%. Combines with the generic gates in docs/06; the stricter
  one wins.

## 6. Red lines & cautions

- **Don't let 20% quietly become 40%**: the value of moderate/high sessions lives in the
  ratio, not in the effort itself.
- Low-intensity days are not "filler jogs": record them, keep the duration.
- May only be stricter than the generic safety layer (docs/03/06).

## 7. Strength / auxiliary advice

- 2×/week strength coexists naturally with low-intensity volume; keep it through volume
  peak weeks but cut sets.

## 8. Worked example

Example runner, 4 runs/week: `Tue E (Z1)` · `Thu E (Z1)` · `Fri E short recovery` ·
`Sun Long (Z1/Z2)`, and every 2–3 weeks one Tuesday becomes `T 15–20 min` or `400 m
intervals` — the time-based split stays ≈80/20.

## 9. Mandatory checks (post-generation self-check)

1. **Intensity composition**: the core metric is the **time split** — low intensity
   (Z1/Z2) ≥80%, moderate+high ≤20%; T and I never in the same week. If hard time exceeds
   25% for two consecutive weeks → drop a quality session; never compensate by speeding up
   E runs.
2. **Fatigue quantification & management**: quantify fatigue via the weekly time-based
   intensity split plus whether HR drifts high on low-intensity runs; distribution drift is
   the fatigue/loss-of-control signal — respond by cutting quality, keeping volume, not by
   stopping running.
3. **Micro/macro cycles**: micro = mostly E + one quality session every 2–3 weeks; macro is
   a volume-ramp main line (base → build → occasional quality → taper) with a recovery week
   every 3–4 weeks.
4. **Easy-run doctrine**: low-intensity sessions are judged by **HR and time** — full
   sentences are the test; the VDOT E pace is only a reference floor. Pace and distance are
   not chased.
