# 80/20 Polarized `polarized_80_20`

> ⚠ **Source & Copyright Notice**: This file is the repository's **summary + application guide**
> of Matt Fitzgerald's *80/20 Running: Run Stronger, Race Faster by Training Slower* (2014,
> Penguin; based on Stephen Seiler's polarized training research) philosophy, NOT a copy or
> excerpt of the original book. Pace values are derived from `data/vdot/` (GPL-3.0 exported
> VDOT data, see `data/vdot/README.md`, not a direct reproduction).

## 1. Source & Applicability

- Source: Matt Fitzgerald, *80/20 Running* (2014); scientific foundation is Norwegian exercise
  scientist **Stephen Seiler's** series of studies on elite endurance athlete intensity
  distribution (from 1990s onward), and controlled experiments by Jonathan Esteve-Lanao in
  collaboration with Seiler (2005, 2007, 2014).
- Core thesis: Approximately **80% of total training time** at low intensity (below ventilatory
  threshold), approximately **20%** at moderate-to-high intensity (above ventilatory threshold).
  Intensity distribution matters more than "how hard any single session is" for long-term
  progress. Moderate intensity is the training "black hole" — almost as stressful as high
  intensity but far less stimulative of aerobic development.
- **Scientific evidence**:
  - Seiler's research: elite athletes across all endurance sports spend ~80% of training time at
    low intensity; cross-country skiers 91%, rowers 88/12, elite Kenyan runners 85% below
    lactate threshold (Billat 2003).
  - Esteve-Lanao & Seiler 2007: 12 runners (10K 30–35 min), equal volume (50–55 mi/wk), 80/20
    group significantly outperformed 65/35 group.
  - Stöggl & Sperlich: Polarized group (80% low + 20% high + 0% moderate) performed best;
    threshold group (54% moderate intensity) actually decreased VO2max by 4.1%.
  - Recreational runners' actual distribution ~46% low / 46% moderate / 9% high (Gilman 1993) —
    "intensity blindness" causes them to believe they're running easy when actually at moderate.
- **Suitable for**: Volume-focused recreational runners prone to overtraining or with injury
  history; those wanting to build weekly mileage without breaking down; runners whose "easy runs
  are always too fast."
- **Not suitable for**: Very limited time (<3.5h/week) wanting quick results — the method's
  advantage is unclear when volume can't accumulate; runners who hate slow running.

## 2. Intensity System & Pace Sources

### Scientific Three-Zone Model (Seiler)

| Intensity | Boundary | HR (% of max) | Description |
|---|---|---|---|
| Low | Below ventilatory threshold (VT) | <82% HRmax | Fully aerobic, full sentences |
| Moderate | VT → lactate threshold (LT) | 82–94% HRmax | "Black hole" — high stress, low stimulus |
| High | Above lactate threshold (LT) | >94% HRmax | Produces significant adaptation, but large volume is harmful |

### Fitzgerald Five-Zone System (based on Lactate Threshold Heart Rate, LTHR)

| Zone | Name | % LTHR | Scientific Equivalent | Purpose |
|---|---|---|---|---|
| Z1 | Low Aerobic | 75–80% | Low | Warmup/cooldown/recovery runs/interval recovery |
| Z2 | Moderate Aerobic | 81–89% | Low | Foundation runs / long runs |
| Z3 | Threshold | 96–100% | Moderate | Tempo runs / cruise intervals / fast finish |
| Z4 | VO2max | 102–105% | High | Long intervals (2–8min) / fartlek |
| Z5 | Speed | 106%+ | High | Short intervals (30–90s) / hill reps |

- **Key**: Buffer gap between Z2 upper (89%) and Z3 lower (96%) ensures low-intensity efforts
  don't "ride the fence" into moderate. Small gap also between Z3 upper (100%) and Z4 lower
  (102%).
- **Low intensity = Z1+Z2; Moderate = Z3; High intensity = Z4+Z5**. 80/20 measured by **time**,
  not distance.
- Pace source: Low intensity (Z1/Z2) primarily HR/perceived effort; Z3 tempo runs use HR+pace
  dual control; Z4/Z5 intervals primarily pace/perceived effort (due to cardiac lag, HR doesn't
  reach target in short intervals). Quality session paces may consult `data/vdot/` (Z3≈T pace,
  Z4≈I pace, Z5≈R pace).
- **Lactate threshold heart rate determination**: 30-minute all-out time trial, average HR during
  minutes 20–30 ≈ LTHR.
- Cross-training note: Lactate threshold HR in non-impact activities (cycling/elliptical) is
  ~10 bpm lower than running.

## 3. Weekly Skeleton Construction

1. Weekly skeleton built around **lots of Z2 foundation runs + long runs**; 1 quality session
   per week (Z3 tempo OR Z4/Z5 intervals, choose one, rotate on different weeks).
2. `long_run_day` is the largest Z2 long run; **intensity days separated by ≥48h**.
3. 12 workout types in three categories:
   - **Low-intensity runs** (entirely Z1/Z2): Recovery run (Z1), Foundation run (Z1 warmup→Z2→Z1
     cooldown), Long run (Z2 primary).
   - **Moderate-intensity runs** (with Z3 segments): Fast finish run (foundation run + 5–15min
     Z3 at end), Tempo run (15–45min continuous Z3), Cruise intervals (multiple Z3 + Z1
     recovery), Long run with speed play (Z2 with short Z3 bursts), Long run with fast finish
     (Z3 at end).
   - **High-intensity runs** (Z4/Z5): VO2max intervals (2–8min reps, Z4), Speed intervals
     (30–90s reps, Z5), Mixed intervals (Z4+Z5), Speed-play/fartlek.
4. Each week, calculate intensity distribution by **time**, target 80/20; if drift is severe
   (high intensity >25% or moderate >20%), delete a quality session — **never "compensate by
   running easy runs faster."**
5. First step for newcomers: **"Week of Slow"** — first week all runs slower than target easy
   pace, ignore HR and pace, find the "completely strain-free" feeling, break the habit of
   habitual moderate intensity.
6. Progression ≤10–15%/week, subject to general safety layer.

## 4. Periodization & Volume Progression

- Cycle structured around **volume climbing** as main line: Base phase (all Z1/Z2 low intensity)
  → Volume-building phase → Limited quality phase (Z3 tempo primary) → Peak phase (add Z4/Z5
  intervals) → Taper (reduce volume maintain "training frequency," may retain small Z3/Z4
  stimuli).
- This method does not use "consecutive multi-week high-quality peaks"; relies on **long-term
  stable high-volume low-intensity accumulation**.
- Polarized variant: Strictly 80% low + 20% high + **0% moderate** (no Z3 at all), suitable for
  runners with some base; standard 80/20 allows limited Z3 (counted in the 20%).
- Recovery week every 3–4 weeks (volume down 20–30%, keep 1 short quality session or pure low
  intensity).
- Begin taper 2–3 weeks before race: reduce volume not frequency, retain small stimuli at each
  intensity to ensure every energy system is "online."

## 5. Test Races & Gates

- Use non-A races/time trials as tests (attempt all-out); **test results determine VDOT and
  targets, but do not change the 80/20 distribution**.
- Lactate threshold HR test (30min time trial) is the baseline for setting five zones; recommend
  retest every 8–12 weeks.
- **Package gates** (combined with docs/06, may be stricter):
  - Gate A: 2 consecutive weeks high-intensity time >25% → cut to ≤20%, delete one quality
    session.
  - Gate B: 2 consecutive weeks moderate-intensity (Z3) time >20% → indicates easy runs are too
    fast, lower Z2 pace/HR, don't delete sessions.
  - Gate C: Peak-phase Z4 interval quality → if paces cannot be maintained → lower pace or reduce
    reps, conservative race start (**veto power**, consistent with docs/06).
- Race-day target conversion: Use VDOT table (docs/09) to reverse-calculate marathon target from
  recent 5K/10K/HM results, avoid pure Riegel.

## 6. Red Lines & Cautions

- **Don't let 20% quietly become 40%**: The value of moderate-high intensity sessions lies in
  proportion control, not intensity itself. Typical recreational runner error is 46/46/9
  distribution (believing it's 80/20).
- **Moderate intensity is the "black hole"**: Z3 is almost as stressful as Z4/Z5 but far less
  stimulative of aerobic development. Either run slow enough (Z2) or fast enough (Z4/Z5), don't
  get stuck in the middle.
- Low-intensity runs are not "junk miles": equally record HR, ensure duration; Z2 is "foundation
  running," not filler.
- **Short intervals show cardiac lag**: 30s Z5 sprint HR may only reach target at the end — this
  is normal, judge by pace/perceived effort.
- "Week of Slow" is not a permanent state: just a habit-breaking tool, afterward return to normal
  Z1/Z2 ranges.
- Can only be stricter than general safety layer (docs/03/06).

## 7. Strength & Auxiliary Recommendations

- 2×/week strength naturally compatible with low-intensity days (doesn't steal recovery);
  continue during peak volume weeks but reduce sets.
- Cross-training may replace some low-intensity running volume (cycling/elliptical/swimming), but
  lactate threshold HR is ~10bpm lower than running, needs separate determination. Incline
  treadmill walking is the most running-specific cross-training.
- Achilles/hamstring-prone runners: concentrate Z4/Z5 high-intensity training in cross-training,
  running only Z1–Z3.
- Static stretching done hours after running (not immediately post), 20 sec × 1–3 sets each.

## 8. Application Example

Sample runner (4 runs/week, target marathon 4:00):

- **Base phase**: `Tue Z2 40min` · `Thu Z2 50min` · `Fri Z1 recovery 30min` ·
  `Sun Long Z2 70–90min`
- **Quality phase** (one quality session every 2–3 weeks):
  - Tempo week: `Tue Z3 tempo 20min (+10min warmup/cooldown each)` · `Thu Z2 50min` ·
    `Fri Z1 30min` · `Sun Long Z2 90min`
  - Interval week: `Tue Z4 5×3min (equal recovery)` · `Thu Z2 50min` · `Fri Z1 30min` ·
    `Sun Long Z2 90min`
- Time-based accounting: Z1+Z2 ≥80%, Z3+Z4+Z5 ≤20%.

## 9. Mandatory Checks (Post-Generation Self-Test)

1. **Intensity composition**: Core metric is **time proportion** — low intensity (Z1+Z2) ≥80%,
   moderate-high (Z3+Z4+Z5) ≤20%; Z3 and Z4/Z5 do not appear in the same week (polarized variant
   has Z3=0). High intensity >25% for 2 consecutive weeks → delete one quality session, never
   "compensate by running easy runs faster." Moderate (Z3) >20% for 2 consecutive weeks → easy
   runs too fast, lower Z2 HR/pace.
2. **Fatigue quantification & management**: Measure via weekly time-based intensity distribution +
   whether low-intensity run HR drifts high; distribution drift is a fatigue/loss-of-control
   signal, handled by reducing quality sessions and maintaining total volume, not by stopping
   running. Retest lactate threshold HR every 8–12 weeks, update five zones as fitness improves.
3. **Macro/micro cycles**: Micro = lots of Z2 + one quality session every 2–3 weeks (Z3 or
   Z4/Z5, choose one); Macro = volume climbing as main line (Base → Volume build → Limited
   quality → Peak → Taper), recovery week every 3–4 weeks. Taper reduces volume not frequency,
   retains small stimuli at each intensity.
4. **Easy run standard**: Low-intensity runs judged by **HR (% of LTHR) and time only**; Z1=75–80%
   LTHR (recovery/warmup), Z2=81–89% LTHR (foundation/long run); able to speak in full sentences.
   VDOT E pace only as lower-bound reference, don't judge by pace speed or chase distance.
   Newcomers first do a "Week of Slow" to break habitual moderate intensity.
