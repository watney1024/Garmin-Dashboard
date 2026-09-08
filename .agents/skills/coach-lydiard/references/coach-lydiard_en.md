# Lydiard System `lydiard`

> ⚠ **Source & Copyright Notice**: This file is the repository's **summary + application guide**
> of Arthur Lydiard's training system philosophy, NOT a copy or excerpt of original works.
> Primary sources: Keith Livingstone *Healthy Intelligent Training* (2006, systematic
> interpretation with physiological analysis), Lydiard's own *Running to the Top* (1989),
> *Running with Lydiard* (2000, with Garth Gilmour). Pace values are derived from `data/vdot/`
> (GPL-3.0 exported VDOT data, see `data/vdot/README.md`, not a direct reproduction).

## 1. Source & Applicability

- Source: Arthur Lydiard (legendary New Zealand coach, developed Olympic champions Peter Snell,
  Murray Halberg, Barry Magee), founder of modern endurance periodization.
- Core thesis: **Sequence matters more than effort** — the training pyramid has aerobic base at
  the foundation and anaerobic capacity at the peak; must build layer by layer from bottom up,
  "always push up an energy system from below." Golden rule: "Train, don't strain."
- **Suitable for**: Runners with ≥16 weeks (ideally 20+) available, willing to build base, not
  eager for intensity; marathon/HM targeters with weak aerobic base; injury-prone runners needing
  low-intensity rebuild.
- **Not suitable for**: <12-week prep (base phase alone is insufficient); very limited time
  unable to guarantee ≥5 runs/week; runners who hate slow running and rush to intervals.
  When profile `runs_per_week` and available time are insufficient, first suggest a gentler
  package and get confirmation.

## 2. Intensity System & Pace Sources

Lydiard does not use a fixed five-zone system; instead it uses **effort fractions**:

| Effort Fraction | Corresponding Intensity | HR (HRR/Karvonen) | Purpose |
|---|---|---|---|
| 1/4 effort | General aerobic / long run | Low–moderate | Daily recovery runs, long run主体 |
| 3/4 effort | Strong aerobic (sub-threshold) | ≈75% MHR | Base-phase "effort run," ≈MP, pushes AT from below |
| 7/8 effort | All-out time trial | Near max | Pre-race test / competition |

- **HR calculated via HRR (Karvonen)**: (HRmax − resting HR) × % + resting HR; **do NOT use
  220−age**.
- Anaerobic threshold (AT) ≈85% HRR ≈15K race pace; 3/4 effort (sub-threshold) ≈90–95% AT
  speed ≈marathon pace — the "magic" cornerstone session of the base phase.
- Pace source: Base and hill phases use **HR/perceived effort**, no pace table; track/anaerobic
  phase interval paces consult `data/vdot/` (`scripts/vdot.py`), never guess.
- Lydiard's original system predates VDOT (Daniels' contribution); this repository uses VDOT
  tables for anaerobic-phase pace reference, while base phase坚持 "HR + perceived effort."

### Three Types of Anaerobic Exercise (physiological foundation)

| Type | Duration | Energy System | Training Method |
|---|---|---|---|
| Alactic | <10 sec | Phosphocreatine | Short sprints, strides, hill springing — safe, year-round |
| Glycolytic | 10 sec–2 min | Lactate system | 1500/800m pace short reps, full recovery — only pre-race for middle distance |
| VO2max | 2–8 min | Aerobic+anaerobic mixed | 5000/3000m pace long intervals, equal or shorter recovery |

- **Key distinction**: Speed training (alactic, <10 sec sprints) ≠ anaerobic training
  (glycolytic, produces acidosis). Lydiard: "Repetition/interval runs develop anaerobic
  capacity, not speed; develop speed with short sprints in a relaxed, unfatigued state."

## 3. Weekly Skeleton Construction

The weekly skeleton **varies by phase**, not a fixed template:

### Base Phase (Aerobic Base / Marathon Conditioning)

1. 6–7 runs/week (may include doubles), aerobic endurance focus; `long_run_day` on weekend.
2. **Mon & Fri**: 1-hour "steady state" effort runs (3/4 effort, sub-threshold, ≈MP) — the
   core session, not LSD. Naturally gets faster as base progresses (e.g., 65 min for 10 miles
   → 55 min), but always "solid training, not racing."
3. **Tue & Thu**: Longer but easier aerobic runs.
4. **Wed**: ~1 hour fartlek — with multiple short sprints (<10 sec, alactic) interspersed with
   full aerobic recovery, maintaining fast-twitch stimulation and form without entering lactate
   zone.
5. **Weekend**: 22-mile (35km) long run with hills (~5km climb + rolling terrain), run to "heavy
   tired legs" (glycogen depletion) then a few more miles — key for fat oxidation training.
6. Non-long-run days may add 30–60 min very easy morning jog (~60% MHR) as supplement.
7. **Base phase never exceeds anaerobic threshold**; no structured intervals.

### Hill Phase (Hill Resistance, 4 weeks)

1. **2–3 hill sessions/week** (original 6 days/week, modern adaptation 2–3), other days maintain
   aerobic running, long run continues.
2. Three hill exercises (introduced in "longer/slower first, then shorter/faster" order):
   - **Steep Hill Running**: slow jog up steep grade, emphasize high knee lift, upright arm drive,
     strengthens quads and hip flexors; don't run too fast (too fast = anaerobic, loses resistance
     effect).
   - **Hill Bounding**: exaggerated long-stride bounding uphill, emphasize full rear-leg extension,
     develops power; slightly gentler grade than steep hill running.
   - **Hill Springing**: short-stride high-vertical bouncing, emphasize ankle elasticity, develops
     speed; steeper and shorter, best on grass with spikes.
3. Original Hill Circuit: 800m uphill (springing/bounding) → 800m jog recovery at top → 700m
   downhill relaxed striding (lean forward, freewheel) → 800m wind sprints at bottom
   (4×100 / 8×50 / 2×200, equal-distance jog recovery). 4 laps + warmup/cooldown = 12–14 miles.
4. Week 1 total hill exercise 15 min (excl. warmup/cooldown), then 30 min, 45 min progression;
   "real effects felt two weeks later."
5. Hill sessions **do not produce sustained anaerobic** — work bouts very short, recovery ample;
   considered an extension of the final 4 weeks of aerobic base.
6. No-hill alternatives: stadium steps, parking ramp slopes, gym plyometrics (need extra calf
   stretching + strides).

### Anaerobic Phase 1 (VO2max / Anaerobic Capacity, 4–5 weeks)

1. **1 VO2max long-interval session/week** as main quality: 800–1000m @ 5000m pace (95% VO2max),
   equal or shorter recovery; mature athletes total up to 6000m.
2. Work bouts 2–5 minutes optimal (>5 min too close to race intensity, <2 min HR doesn't reach
   max zone).
3. Early phase may use "20×400 @ 1/4 effort" (one-lap jog recovery) — naturally approaches VO2max
   pace.
4. Morning of interval day may add 6–8km easy run ("wake-up" + maintain aerobic stimulus).
5. Other days: easy aerobic + 1 sub-threshold run/week (45–60 min embedded in 80min run) + long
   run (retained through season until ~2 weeks before race, may be 1 min/km slower than base).
6. **No short fast intervals at this stage** — goal is systemic acidosis; short fast reps only
   cause local leg acidosis, missing the training target.

### Anaerobic Phase 2 (Glycolytic / Anaerobic Power, final weeks pre-race)

1. Only for middle-distance (800/1500m) runners; **marathon/long-distance runners skip this
   phase**.
2. Short reps @ realistic achievable 1500m or 800m pace, **full recovery (minutes walk/jog)**:
   - 800m pace session total ≤1600m (e.g., 4×400 or 8×200)
   - 1500m pace session total ≤3200m (e.g., 8×400)
3. Paces must be based on current aerobic capacity (VDOT-realistic), never faster than current
   potential.
4. Peak-season maintenance: 50m all-out sprint + 50m float, 5 laps around track (20 sprints) —
   creates local leg acidosis without systemic impact, recovers fast.
5. Taper begins 10 days before major competition: lots of easy jogging, low anaerobic volume,
   full recovery, race-specific paces.

### Marathon-Specific Prep (final 4 weeks, after 10-week base)

1. Weeks 1–2: Weekly 1 threshold run replacing sub-threshold — warmup 20min + AT 20min +
   cooldown 20min (don't exceed; threshold depletes glycogen + residual fatigue).
2. Weeks 3–4: 2–3 VO2max sessions @ 5000m pace (e.g., 5×1000m equal recovery), spaced ≥1 week.
3. **Never glycolytic training** (damages aerobic enzymes, glycogen, fat utilization).
4. Max 2 hard sessions/week.
5. **No energy gels in long run training** — purpose is glycogen depletion to force fat
   adaptation.

## 4. Periodization & Volume Progression

Strict four-phase periodization, order cannot be reversed or skipped:

### Phase 1: Aerobic Base

- **Duration**: 8 weeks for track/middle distance; 10 weeks for marathon/road; elites up to
  12–16 weeks (Dick Quax used 12–16). Longer is better when time allows.
- **Goal**: Push aerobic system to maximum possible in given time — left ventricle enlargement,
  increased stroke volume, lower resting HR, capillary proliferation, mitochondrial density &
  oxidative enzymes, enhanced fat oxidation.
- **Volume**: Elites ~100 miles/week (160km), 10–12 hrs/week; recreational runners increase
  from current level at ≤10%/week, target long run ≥2h30–40 + two mid-week 1h30 runs.
- **Core method**: Not LSD, but "as much strong aerobic running as possible without producing
  systemic fatigue." Balance weekly load through varying distance and intensity.
- **Effort run progression**: Mon/Fri 1-hour sub-threshold runs start at manageable level,
  naturally get faster each week; visible change after 8–12 weeks. "Patience is everything."
- **Long run**: Weekly, run to "heavy legs" (glycogen depletion) then a few more miles; no gels.
- Can be done twice a year (winter cross-country/road season + summer track season).

### Phase 2: Hill Resistance (4 weeks)

- **Goal**: Bridge from aerobic to speed; strengthen prime movers for fast running (quads, hip
  flexors, calf/ankle elasticity), preferentially recruit IIb fast-twitch fibers via plyometric
  contractions.
- Aerobic volume maintained, long run continues; hill sessions 2–3 days/week with easy recovery
  runs between.
- Downhill striding is excellent eccentric resistance training, but knee-injured runners may skip.

### Phase 3: Anaerobic Phase 1 (VO2max / Anaerobic Capacity, 4–5 weeks)

- **Goal**: Develop systemic acidosis tolerance and chemical buffering; push circulation and
  aerobic capacity to maximum.
- This capacity reaches physiological limit in 4–5 weeks (confirmed by Lydiard's collaboration
  with East German sports scientists), but Lydiard preferred a more gradual spread.
- Long intervals @ 5000m pace (95% VO2max) primary; safer than 100% VO2max (3000m pace) and
  accumulates more time in target zone.

### Phase 4: Anaerobic Phase 2 (Glycolytic / Anaerobic Power, final weeks)

- **Goal**: Develop local leg acidosis tolerance needed for middle-distance racing.
- Only middle-distance runners need this; marathon runners go directly from VO2max phase to taper.
- Small volume, full recovery; paces based on current aerobic capacity realistic race pace.

### Taper

- Begin withdrawing from all hard training 10 days before competition, maintain easy jogging.
- Marathon taper: Week 11 (2 weeks out) = 80% of week 10 volume; race week = 60%.
  Example: Sunday long run 20mi → 16mi → 12mi. **Must be gradual, never sudden** (sudden
  reduction causes race-day lethargy).
- Keep small stimuli at each intensity (threshold, VO2max) in final 2 weeks, ensuring every
  energy system is "online."

### Recovery Management

- **Active recovery superior to complete rest**: Easy aerobic running returns metabolic products
  to liver for recycling, reversing blood acidosis; complete rest barely flushes muscles.
- Blood markers return to normal 24–96h after hard glycolytic work; aerobic system may take
  longer.
- Two consecutive long easy aerobic runs can "forgive" many overtraining problems.
- Fatigue signals: feeling flat after training, acidic urine (test with strips) → increase easy
  running, reduce intensity.
- Volume increase ≤10%/week (running time measure).

## 5. Test Races & Gates

- Lydiard uses **track time trials + races** as checkpoints:
  - 800m runners average ~5 races before seasonal best; 1500m ~4 races (British Milers Club
    research).
  - Time trials (1600m/3000m/5000m) every 2–3 weeks in track phase, focus on even pace and
    consistent lap times.
- **Aerobic Profile**: Plot performances across distances on VDOT table; ideal is a "flat line."
  If a distance is notably weak, that energy system is undertrained — supplement with
  corresponding pace training, not blindly add volume.
- **Package gates** (combined with docs/06, may be stricter):
  - Gate A: End-of-base long run completion → if cannot complete ≥2h30 long run (to heavy legs)
    under HR control → extend base 2 weeks, don't enter hill phase.
  - Gate B: VO2max phase interval quality → if 5×1000m @ 5000m pace cannot be maintained (last
    rep >5 sec slow) → reduce reps or lower pace, don't enter glycolytic phase.
  - Gate C: Marathon final 4 weeks threshold/VO2 sessions → if threshold 20min cannot hold →
    conservative race start (**veto power**, consistent with docs/06).
- Race-day strategy: Marathon "begins at 32km"; hold steady through 32km, conserve glycogen;
  start slightly slower than target pace.

## 6. Red Lines & Cautions

- **Never skip base phase**: The soul of Lydiard's system; without 8–10 weeks of pure aerobic
  base, subsequent hill/anaerobic work is built on sand. Insufficient prep cycle → switch
  package, don't compress base.
- **Base phase never exceeds anaerobic threshold**: Lydiard insisted on this until the week he
  died. Base "effort runs" are sub-threshold (3/4 effort), not threshold runs.
- **Never mix phases**: No intervals in base, no track intervals in hill phase, glycolytic only
  in final weeks. "Training everything at once = training nothing well."
- **Long run never cut**: Even in anaerobic phases retain (may shorten, may slow 1 min/km),
  "never lose the foundation you built."
- **Marathoners never do glycolytic training**: Acidosis damages aerobic enzymes, glycogen, and
  fat utilization — counterproductive.
- **No gels in long run training**: Purpose is glycogen depletion to force fat adaptation; gels
  may be used in final race kilometers (but must be tested in training at least once).
- **Speed training ≠ anaerobic training**: Develop speed with <10 sec short sprints in relaxed,
  unfatigued state; fast running when fatigued only tightens form and impairs speed.
- **Hill sessions are not hill time trials**: Emphasize bounce and relaxation; stop when form
  breaks. Knee-injured skip downhill striding.
- Can only be stricter than general safety layer, never relax (docs/03/06).

## 7. Strength & Auxiliary Recommendations

- Lydiard "strength" is primarily achieved through **hill training** (hill phase), not gym heavy
  lifting.
- Three hill exercises are themselves sport-specific strength: Steep Hill Running (quads/hip
  flexors), Hill Bounding (rear-leg extension/power), Hill Springing (ankle elasticity/vertical
  force).
- Base phase may include 1–2 general strength sessions/week (core, lower body, single-leg
  stability), reduced after hill phase.
- This system strongly depends on foot and calf elasticity; calf raises and tibialis anterior
  work are baseline. Lydiard: "I never had an athlete with Achilles or hamstring problems
  because hill training extremely stretches the ankles and naturally strengthens front and back
  muscles/ligaments."
- No-hill alternatives: stadium step running (Lydiard-approved), parking ramp slopes, gym
  plyometrics.

## 8. Application Example

Sample runner (5 runs/week, marathon prep 14 weeks from existing aerobic base):

- **Base Phase (W1–10)**:
  - `Mon E60min (3/4 effort, sub-threshold)`
  - `Tue E70min (easy)`
  - `Wed Fartlek 60min (with <10s short sprints)`
  - `Thu E70min (easy)`
  - `Fri E60min (3/4 effort, sub-threshold)`
  - `Sat rest`
  - `Sun Long 18→28km (E, to heavy legs, no gels)`
- **Hill Phase (W11–14, 4 weeks)**:
  - `Tue Hill 30min (steep hill running + bounding)`
  - `Thu E70min + 8×120m strides`
  - `Fri E60min`
  - `Sat Hill 30min (springing + downhill striding)`
  - `Sun Long 26km (E)`
  - Mon/Wed add E runs, total volume maintained
- **Marathon final 4 weeks (alternative W11–14 if skipping hill phase)**:
  - W11–12: `Tue AT 20min (warmup20+AT20+cooldown20)` · `Thu E` · `Sun Long 30km`
  - W13: `Tue VO2max 5×1000 @ 5000m pace` · `Thu E` · `Sun Long 26km (80%)`
  - W14 (race week): `Tue VO2max 3×1000` · `Thu E 30min` · `Sun race`
  - Volume W13=80%, W14=60%

## 9. Mandatory Checks (Post-Generation Self-Test)

1. **Intensity composition**: Base phase 100% aerobic (including 3/4 effort sub-threshold, still
   aerobic, below AT); hill phase low intensity ≥80% (hill counts as quality, but work bouts
   short with no sustained anaerobic); VO2max phase low intensity ≥70%, quality ≤2 sessions/week
   (including hard segments in long run); glycolytic phase only middle-distance runners and
   quality ≤2 sessions/week. Marathon prep has zero glycolytic throughout. When exceeding,
   reduce quality first, never touch aerobic runs or long runs.
2. **Fatigue quantification & management**: Measure via "quality session completion + long-run
   HR drift + morning resting HR + urine acidity"; Lydiard fatigue management relies mainly on
   **phase transitions** (base→hill itself is stimulus change) + active recovery (easy aerobic
   flushes acidosis); if quality cannot be completed 2 consecutive weeks in a phase → extend
   current phase 1–2 weeks, don't advance; no second hard session within 24–96h after hard
   glycolytic work.
3. **Macro/micro cycles**: Micro varies by phase (base: 2 effort runs + fartlek + long run;
   hill: 2–3 hill + maintain aerobic; VO2max: 1 long interval + sub-threshold + long run;
   glycolytic: short reps + full recovery); Macro = Base → Hill → VO2max → Glycolytic
   (marathon skips glycolytic) → Taper, order cannot be reversed; natural volume reduction at
   each phase transition, long run always retained. Volume increase ≤10%/week.
4. **Easy run standard**: Base/hill/recovery runs judged by **HR (HRR method) and time only**;
   3/4 effort = sub-threshold ≈MP ≈75% MHR; 1/4 effort = general aerobic. Don't judge by pace
   speed or chase distance. VDOT E only as reference, no pace table in base phase. Base is not
   LSD — effort runs must be productive, but never exceed AT.
