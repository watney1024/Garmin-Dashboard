# Advanced Marathoning `advanced_marathoning`

> ⚠ **Source & Copyright Notice**: This file is the repository's **summary + application guide**
> of Pete Pfitzinger & Scott Douglas' *Advanced Marathoning* (2nd ed. 2019, Human Kinetics)
> philosophy, NOT a copy or excerpt of the original book. Pace values are derived from
> `data/vdot/` (GPL-3.0 exported VDOT data, see `data/vdot/README.md`, not a direct
> reproduction of the book).

## 1. Source & Applicability

- Source: Pete Pfitzinger (former US Olympic marathoner, M.S. exercise physiology) & Scott
  Douglas, *Advanced Marathoning* (2001 original / 2019 2nd ed.).
- Core thesis: The marathon is an **aerobic endurance event**; success comes from the systematic
  combination of "high mileage base + mid-week Medium-Long Run (MLR) + specific marathon-pace
  training." MLR distributes endurance stimulus across two runs per week instead of cramming it
  all into one weekend ultra-long run. Training priority: **endurance > lactate threshold >
  VO2max**; long runs and tempo runs correlate most directly with marathon performance.
- **Suitable for**: Runners with 1–2+ years of systematic training, current stable weekly
  mileage ≥40 km, clear marathon target, willing to invest 6–10+ hrs/week; can accept ≥5
  runs/week (including 2–3 quality days); prefer structured, logical schedules.
- **Not suitable for**: First-time marathoners or those with insufficient mileage base (plans
  start high); <6 hrs/week available; specialists in 5K/10K/half marathon (this system is
  marathon-specific); injury-prone runners under high mileage; when profile `runs_per_week <5`
  or `quality_days <2`, first suggest a gentler package and get confirmation.

## 2. Intensity System & Pace Sources

The book defines **8 training types** (Ch.7), each with precise HR ranges:

| Type | Distance | Pace Basis | HR Range | Typical Session |
|---|---|---|---|---|
| Long Run | >26 km | 10–20% slower than target MP | HRmax 74–84% / HRR 65–78% | `Long 28–35km`, last 8–16km at MP+10% |
| Medium-Long Run (MLR) | 18–26 km | Same as long run pace | HRmax 74–84% / HRR 65–78% | Mid-week `MLR 18–24km` |
| MP Run | within MLR/long | Target marathon pace for 13–22 km | HRmax 79–88% / HRR 73–84% | `25km with 19km at M` |
| General Aerobic (GA) | ≤16 km | 15–25% slower than MP | HRmax 70–81% / HRR 62–75% | `GA 10–14km` |
| Lactate Threshold (LT) | ≥20 min T segment | Current 15K–HM pace | HRmax 82–91% / HRR 77–88% | Warmup 5km + `T 6–11km` + cooldown 3km |
| Recovery | Short | 75 s/km slower than 16K–HM pace | HRmax ≤76% / HRR ≤70% | `Recovery 5–10km`, very slow |
| VO2max Intervals | 600–1600 m/reps | **5K race pace** (not 3K) | HRmax 93–95% / HRR 91–94% | `5×1200`, rest=50–90% of work time |
| Speed/Strides | 50–150 m/reps | Accelerate 70%, cruise 30% | Not HR-monitored | `10×100m`, jog 100–200m recovery |

- Pace source: Quality sessions (M/T/I) always consult `data/vdot/` (`scripts/vdot.py`), never
  guess; E/MLR/GA/recovery use HR/perceived effort, VDOT E only as fast-end reference.
- **VO2max intervals use 5K pace, not 3K pace**: For marathoners, I training is secondary; more
  conservative 5K pace provides VO2max stimulus while shortening recovery, without compromising
  other key sessions. Total interval volume 5000–10000m (typically 6000–8000m).
- **Recovery runs must be "embarrassingly slow"**: 75 s/km slower than 16K–HM pace, or HRmax
  ≤76%; purpose is blood flow and glycogen conservation, not added load.
- **Long runs are not jogging**: 10–20% slower than target MP, start at slow end, last 8–16km
  accelerate to MP+10%; a 35km long run takes about as long as the marathon, providing pace
  mental training.
- **HR formulas**: HRmax = 207 − 0.7×age (individual variation ±10 bpm, recommend field test);
  HRR = HRmax − resting HR; training HR = resting HR + HRR×target%.
- **Hot-weather HR adjustment**: 20–25°C low humidity +2–4 bpm; 20–25°C high humidity or
  25–35°C low humidity +5–8 bpm; high heat+humidity → take it easy.

## 3. Weekly Skeleton Construction

Input from runner profile: `runs_per_week / long_run_day / quality_days`:

1. **Must have ≥5 runs and ≥2 quality days** (book standard is 3 intensity sessions/week, the
   upper limit most runners can handle); if not met, first suggest switching package and get
   confirmation.
2. Two endurance runs fixed weekly: weekend long run (`long_run_day`, >26km) + mid-week MLR
   (18–26km, usually Tue/Wed). MLR = 60–75% of long run distance, same pace — the signature
   element of this system.
3. `quality_days` (default 2–3): tempo (T) + VO2max intervals (I) + MP runs (embedded in long
   run or MLR). At least 1 recovery day between two quality days; max 3 intensity sessions/week.
4. Other available days: recovery runs (very slow) or GA runs; 1 rest day/week (2 for low-mileage
   plans).
5. **MLR cumulative fatigue design**: MLR placed 2–3 days before long run so legs are not fully
   recovered when weekend long run starts — simulating "running on tired legs" in the marathon's
   second half. This is intentional, not a scheduling error.
6. Typical 6-run week (88 km peak plan):
   `Mon rest · Tue MLR 18–22km · Wed recovery 8–10km · Thu T or I · Fri recovery 8km · Sat Long 28–34km · Sun recovery 8–10km`
7. **Double runs**: No fixed doubles when weekly <121 km; >121 km introduce gradually (1×/week
   then 2×); second session minimum 25 min; never double on long run day; recovery day >13km
   may be split.
8. Weekly mileage progression: hold 2–3 weeks after an increase before next; no speed work
   during mileage-building phase; slightly reduce overall intensity when adding volume.
9. Long run peak 34–35 km (optimal); experienced injury-resistant runners may add one 39km;
   >35km compromises other session quality and increases injury risk.

## 4. Periodization & Volume Progression

The book uses a **five-phase macrocycle** (4–6 months, 1–2 macrocycles/year):

- **Mesocycle 1: Endurance (longest, 4–8 weeks)**
  - Goal: increase mileage, pure endurance building; long runs and MLR gradually extend; little
    or no intensity work.
  - Long run starts 18–22km, +2km every 1–2 weeks; MLR starts 12–15km.

- **Mesocycle 2: LT + Endurance (4–6 weeks)**
  - Goal: raise lactate threshold while continuing endurance; add weekly tempo (T), long runs
    continue to peak. VO2max intervals begin in small doses; mileage reaches peak.

- **Mesocycle 3: Race Preparation (4–6 weeks)**
  - Goal: marathon-specific stimulus; introduce MP runs (M segments 13–22km) and progressive
    long runs; schedule 1–2 tune-up races (8–25km); long run peaks (32–35km), MLR peaks
    (19–26km).
  - Half marathon tune-up usually in first half of this phase as a gate; tune-up requires 4–6
    days taper + race + 5 days recovery.

- **Mesocycle 4: Taper + Race (3 weeks)**
  - 3 weeks out: volume −20–25%
  - 2 weeks out: volume −40%
  - Race week (6 days out): volume −60%
  - **Maintain intensity**: keep one quality session every few days (I intervals or strides),
    no pure-rest taper; 8–10km tune-up race 2 weeks out; last I session 10 days out; dress
    rehearsal run 3 days out (5km E + 3km M + 3km E).
  - Taper can improve performance 2–4% (3-hour marathon gains 3.5–7 min).

- **Mesocycle 5: Recovery (5 weeks)**
  - 2 full rest days post-race; week 1 cross-training/walking; running days increase from 3/week
    to 5/week; training ≤HRmax 76%.

- **Mileage tiers** (peak weekly volume, by target and current base):

| Tier | Peak Weekly | Longest Run | Entry Requirement | Doubles |
|---|---|---|---|---|
| 53–88 km | 88 km | 32 km | ≥40 km/wk | No |
| 88–113 km | 113 km | 34 km | ≥72 km/wk | No |
| 113–137 km | 140 km | 35 km | ≥88 km/wk | Introduce |
| >137 km | ≥170 km | 35–39 km | ≥113–121 km/wk | Fixed |

- Choose tier by **current stable weekly mileage**, not ambition; starting plan volume ≤110–120%
  of current stable volume.
- Recovery week after every 3 intensity weeks (volume down to ~70%, reduce quality count and
  intensity); base phase may use 4 big weeks then 1 recovery.
- Hot season / poor form: switch entirely to "HR + perceived effort" (docs/03), pace only as
  reference.

## 5. Test Races & Gates

- **Tune-up races** (Ch.1): distance 8–25km, must be all-out:
  - 15–25km type: requires 4–6 days taper + ≥5 days recovery, provides fullest physiological
    and psychological benefit.
  - 8–12km type: only 2 days prep, can be raced fatigued as training stimulus.
  - Evaluate tune-up results in context of overall training state; don't get discouraged or add
    volume due to a slow result in a fatigued state.
- **VDOT calibration**: Use tune-up result (within 6 weeks) → VDOT → update all paces; lactate
  threshold pace ≈ current 15K–HM race pace; experienced runners' MP = LT pace −2–3%.
- **Package gates** (combined with docs/06, may be stricter):
  - Gate A: HM tune-up (first half of mesocycle 3) → if HM VDOT ≥2 lower than plan assumption →
    lower marathon target pace globally.
  - Gate B: Longest MP run in mesocycle 3 (25–35km, with 13–22km M segment) → can M segment
    hold pace? If not → conservative race start (**veto power**, consistent with docs/06).
  - Gate C (Pfitzinger-specific): MLR completion quality — if 2 consecutive weeks recovery-run
    HR is abnormally elevated after MLR, or legs too heavy to complete weekend long run → shorten
    MLR by 20% that week, don't push through peak.
- **Missed training adjustments** (book Table 7-2): <10 days missed → resume plan; missed 1 I
  session → subsequent I at lower pace; <8 weeks before race with ≥10 days missed → must adjust
  race target.
- Race-day target conversion: HM result → VDOT → marathon equivalent, then conservatively
  adjusted by "MP run completion quality."

## 6. Red Lines & Cautions

- **MLR cannot be skipped**: It's as important as the weekend long run, the core innovation of
  this system; don't cut MLR because "no time today."
- **Recovery runs must be truly slow**: HRmax ≤76% or 75 s/km slower than 16K–HM pace; running
  too fast steals recovery and compromises quality sessions.
- **Don't replace recovery days with quality**: ≤3 quality days/week is the ceiling; extra
  quality breaks recovery balance.
- **VO2max intervals not too fast**: Marathoners use 5K pace (not 3K/1500m pace); exceeding
  optimal intensity range accumulates lactate, shortens training time, and is marathon-irrelevant.
- **Long run ≤35 km** (optimal), 39km absolute ceiling; >35km compromises other session quality
  and increases injury risk.
- **Be honest about mileage tier**: Choose plan by current stable weekly volume, don't jump to
  higher tier; high-mileage plans require months or years of base.
- **No doubles below 121 km/week**: Splitting runs before single-run volume reaches limit
  reduces glycogen-depletion stimulus.
- **Maintain intensity during taper**: No pure-rest taper; keep quality sessions every few days;
  stop strength/core 10 days before race, stop cross-training a few days before.
- Can only be stricter than general safety layer, never relax (docs/03/06); high mileage does
  not exempt from yellow/red lights.

## 7. Strength & Auxiliary Recommendations

- Default strength 1–2×/week, placed after E runs or day before rest day; lower-body main lifts
  + core + single-leg stability as baseline.
- High-mileage phase strength is **maintenance** (light load, high reps), not strength gain;
  base phase may increase strength intensity, specific phase reduces to activation maintenance.
- **Strides (Speed)** are important auxiliary: add 8–10×100m to at least 2 E/recovery days
  weekly, accelerate first 70m, cruise last 30m, jog 100–200m recovery; improves cadence and
  running economy.
- No heavy lower-body lifting within ≥24h before/after I/T sessions.
- Recovery aids: 300–400 calories within 1 hour post-session (carb:protein=4:1); contrast
  showers; massage; compression socks; 10–20 min cooldown jog (HRmax 60–75%).

## 8. Application Example

Sample runner (6 runs/week, VDOT≈44, marathon target 3:15, 88 km peak plan):
- Mesocycle 1 (Endurance): `Mon rest · Tue MLR14(E) · Wed recovery8 · Thu GA12 · Fri recovery6 · Sat Long20(E) · Sun recovery6`
- Mesocycle 2 (LT+Endurance): `Mon rest · Tue MLR18(E) · Wed recovery10 · Thu T 8km · Fri recovery8 · Sat Long26(E) · Sun recovery8`
- Mesocycle 3 (Race Prep): `Mon rest · Tue MLR22(E) · Wed recovery10 · Thu I 5×1200 · Fri recovery8 · Sat Long32(last 10km M) · Sun recovery10`
- Mesocycle 4 (Taper):
  - 3 weeks out (−20%): `Mon rest · Tue MLR16(E) · Wed recovery8 · Thu T 6km · Fri recovery6 · Sat Long27(last 6km M) · Sun recovery8`
  - 2 weeks out (−40%): `Mon recovery6 · Tue recovery6+ST · Wed MLR19(E) · Thu rest · Fri recovery6 · Sat 10K tune-up · Sun Long21(E)`
  - Race week (−60%): `Mon recovery5 · Tue recovery5+ST · Wed dress rehearsal 5E+3M+3E · Thu recovery5 · Fri rest · Sat rest · Sun marathon`

## 9. Mandatory Checks (Post-Generation Self-Test)

1. **Intensity composition**: By time E (incl. MLR, GA, recovery) ≥75%; quality ≤3 sessions/week
   (M segment in long run counts as half); I total ≤10km and ≤8% weekly volume; T ≥20min/segment,
   total ≤10% weekly volume; M segment ≤22km; long run ≤35km (39km absolute ceiling). When
   exceeding, delete I first, then reduce T, never touch MLR, long run, or recovery.
2. **Fatigue quantification & management**: Measure via "quality session completion + recovery-run
   HR after MLR + HR drift at standard pace (+7bpm = not recovered) + morning resting HR (+5bpm =
   insufficient recovery)"; MLR cumulative fatigue is by design, but if it prevents quality
   session pace completion → shorten MLR or add recovery day; recovery week after every 3
   intensity weeks (volume ~70%); mild overtraining → reducing intensity matters more than
   reducing volume, cut volume 50%, 3–5 weeks recovery.
3. **Macro/micro cycles**: Micro = MLR + long run + 2–3 quality + recovery runs; Macro =
   Endurance → LT+Endurance → Race Prep → Taper+Race → Recovery (5 mesocycles); taper three
   weeks −20/−40/−60%, maintain intensity; mileage tier matches current base, no jumping; no
   doubles below 121 km/week.
4. **Easy run standard**: Recovery HRmax ≤76% (or 75s/km slower than 16K–HM pace); GA 15–25%
   slower than MP; long run/MLR 10–20% slower than MP; pace not meeting target is not an error,
   running too fast is; VDOT E value is fast-end reference ceiling, not target.
