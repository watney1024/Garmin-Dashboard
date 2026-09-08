# Hansons Marathon Method `hanson`

> ⚠ **Source & Copyright Notice**: This file is the repository's **summary + application guide**
> of Luke Humphrey, Kevin Hanson & Keith Hanson's *Hansons Marathon Method: Run Your Fastest
> Marathon the Hansons Way* (2016, VeloPress; 2nd ed.) philosophy, NOT a copy or excerpt of the
> original book. Pace values are derived from `data/vdot/` (GPL-3.0 exported VDOT data, see
> `data/vdot/README.md`, not a direct reproduction).

## 1. Source & Applicability

- Source: Kevin & Keith Hanson brothers (developed marathon training plans for Detroit Marathon
  from 1992), systematized by Luke Humphrey (joined Hansons-Brooks elite team in 2004).
  Methodological foundation is Arthur Lydiard's **cumulative fatigue** concept.
- Core thesis: **Cumulative fatigue is a feature, not a bug** — through 6 running days/week, 3
  SOS (Something of Substance) sessions, and incomplete recovery, train the body to run while
  "carrying fatigue in the legs," simulating the **last 16 miles** of the marathon (not the first
  16). Long run capped at 16 miles (25.7km), no 20-mile "survival runs." "We want to simulate
  the last 16 miles of the marathon in training, not the first 16."
- **Suitable for**: Runners who can guarantee ≥5–6 runs/week; those pursuing marathon PRs willing
  to accept "always a bit tired in training"; runners whose previous low-mileage + ultra-long-run
  plans underperformed.
- **Not suitable for**: Only 3–4 running days/week (cumulative fatigue cannot be established);
  <12-week prep cycle. When profile `runs_per_week <5`, first suggest a gentler package and get
  confirmation.

## 2. Intensity System & Pace Sources

All paces in the Hansons system are **defined relative to target marathon pace (MP)**:

| Type | Abbr | Intensity Basis | Pace Definition | Typical Session |
|---|---|---|---|---|
| Easy | E | 1–2 min/mi slower than MP | 55–75% VO2max | `E5–10mi` / recovery |
| Long | L | Easy–moderate, sub-MP | Not exceeding MP, beginners偏E | `10–16mi` (cap 16mi) |
| Tempo | T | **= target marathon pace MP** | Above aerobic threshold, below anaerobic | `T5–10mi @ MP` |
| Strength | St | MP − 10 sec/mi | Just below AT, 60–80% VO2max | `6×1mi @ MP−10s` |
| Speed | Sp | 5K/10K pace | 80–95% VO2max (never >100%) | `6×800 @ 5K pace` |

- **Pace source**: Anchor to target marathon pace; speed session paces consult `data/vdot/`
  for 5K/10K equivalents (`scripts/vdot.py`), never guess. **HR is only a secondary monitoring
  tool for trends**, not a prescription basis (Hansons: "pace, not heart rate, is key").
- **Key distinction**: Hansons tempo = marathon pace, NOT "threshold pace" as in other systems.
  Near-threshold training is called strength (MP−10s/mi).
- Easy runs分 "fast easy" (1 min/mi slower than MP, used day after tempo, second easy day before
  long run) and "slow easy" (2 min/mi slower than MP, warmup/cooldown, day after SOS, beginner
  transition).
- **Speed sessions never exceed 100% VO2max**: 100% VO2max can only be sustained 3–8 minutes;
  exceeding causes structural muscle breakdown and anaerobic overload, negating aerobic adaptation.

## 3. Weekly Skeleton Construction

Standard week structure (SOS = Tuesday / Thursday / Sunday):

| Day | Content | Notes |
|---|---|---|
| Mon | Easy | Recovery after long run,偏slow easy |
| Tue | Speed or Strength | First SOS, warmup 1.5–3mi |
| Wed | Off or Easy (when adding volume) | Recovery day between two SOS |
| Thu | Tempo @ MP | Second SOS, pre-fatigues for Sunday long run |
| Fri | Easy | Recovery after tempo,偏slow easy |
| Sat | Easy | Before long run, may be fast easy |
| Sun | Long run | Third SOS, cap 16mi |

- **6 runs/week** (Just Finish plan may be 5); SOS sessions must be separated by Easy or Off,
  never back-to-back SOS.
- Advanced peak week 63 mi/wk (~101km), 49% easy running; beginner peak ~50s mi/wk.
- Volume increases优先 by extending easy days (to 10mi+), **not by lengthening long runs**;
  secondarily add 4–8mi easy on rest day (Wed); doubles only considered when daily average
  ~12mi (~80mi/wk).
- Acceptable alternative arrangements (must shift consistently across cycle, not weekly):
  - Plan A: Mon Easy · Tue Speed/St · Wed Off · Thu Easy · Fri Tempo · Sat Easy · Sun Long
  - Plan B: Mon Speed/St · Tue Easy · Wed Off · Thu Tempo · Fri Easy · Sat Long · Sun Easy

### Precise Rules by Session Type

**Long Run**:
- Cap **16 miles (25.7km)** — the signature Hansons number.
- Scientific basis: long run ≤25–30% of weekly volume (Daniels guideline); optimal duration
  2:00–3:00; beyond 3 hours muscle/mitochondrial/capillary damage begins (studies show damage
  still present 8 weeks later).
- Runners slower than 9:00/mi (5:36/km) **should not do 20 miles** (16mi already approaches
  3 hours).
- In advanced plans, long runs occur **every other week** (alternating with long tempo weeks),
  avoiding 3 long sessions within 8 days.
- Long run is not a "pre-race 20-mile survival run," but controlled adaptation under cumulative
  fatigue.

**Speed**:
- Placed **early** in the training cycle (marathon prep doesn't need late fast intervals).
- Pace = 5K or 10K target pace (80–95% VO2max).
- Single rep duration 2–8 minutes optimal; recovery = 50–100% of rep duration (jog recovery,
  never walking).
- Total fast running per session = **3 miles** (excluding warmup/cooldown/recovery).
- Progression sequence: 12×400 → 8×600 → 6×800 → 5×1000 → 4×1200 → Ladder → 3×1600, then
  may repeat in reverse. Warmup/cooldown 1.5–3mi each.
- Judgment criterion: "If you're too tired to jog during recovery intervals, you're going too
  fast."

**Strength**:
- Introduced after speed phase, the core of marathon-specific training.
- Pace = **MP − 10 sec/mi** (just below anaerobic threshold).
- Total high-intensity running = **6 miles** (double speed session volume), recovery very short
  (e.g., 1/4mi jog after 1mi repeat, less than 50% of rep duration).
- Purpose: maintain pace under moderate lactate accumulation, improve lactate clearance, fractional
  utilization, and anaerobic threshold.

**Tempo**:
- Pace = **target marathon pace MP** (Hansons definition, not threshold).
- Distance progression: beginners 4mi → 10mi; advanced 6mi → 7 → 8 → 9 → 10mi (+1mi each).
- Total with warmup/cooldown up to 12–14mi, ~90 min.
- **Key gate**: If long tempo cannot hold MP, marathon target is too aggressive — speed/strength
  sessions can be "fudged," tempo has no interval rest to hide behind.
- Also serves as fueling/gear dress rehearsal.

## 4. Periodization & Volume Progression

### Beginner Plan (16 weeks)

| Phase | Weeks | Content | Weekly Volume |
|---|---|---|---|
| Base | W1–5 | All easy running, build volume | 15 → 25 mi |
| Speed+Tempo | W6–13 | Introduce speed (5K/10K pace) + tempo (MP), volume continues | ~35 → 50s mi |
| Strength+Peak | W14+ | Speed → strength, tempo lengthens, long run peaks | Peak ~50s mi |
| Taper | Final 10 days | Reduce volume maintain frequency | Down ~55% |

- W5→W6 has significant jump (~25→41mi) due to SOS introduction and removing Monday rest; if
  too large, add 4–5mi easy on Monday and reduce speed reps on Tuesday.
- Long run starts at 10mi, +≤2mi/week, ~25% of weekly volume; when alternating with long tempo
  weeks, 15–16mi → 10mi fluctuation occurs.

### Advanced Plan (16 weeks)

- Speed begins Week 1, tempo Week 2 (advanced runners often race multiple marathons/year and
  neglect speed).
- Longer speed segment: forward ladder progression then reverse repeat.
- Peak >60 mi/wk (cap 63mi), increases come from extending easy days, not SOS volume.
- Long run every other week (16mi alternating with tempo total 14–16mi).
- Tempo increases by 1mi (6→7→8→9→10mi) as experienced runners improve slowly, needing finer
  stimulus.

### Taper

- **Only 10 days** (not 2–4 weeks), last SOS 10 days before race.
- Final 7 days volume down ~**55%**, but **maintain running day count** (sudden frequency
  reduction makes the body "foggy," like sleeping 12 hours when used to 6).
- Scientific basis: SOS sessions require 10 days to manifest physiological benefit; taper can
  yield up to **3%** performance improvement (e.g., 4:00 → 3:53).
- Reduce volume and intensity only, not frequency.

### Cumulative Fatigue vs. Overtraining Continuum

| Stage | Recovery Time | State |
|---|---|---|
| 1. Fatigue | 24–48h | Normal post-session feeling, easy running recovers |
| 2. Functional Overreaching | ≤2 weeks | **= Cumulative fatigue, where the plan aims** |
| 3. Nonfunctional Overreaching | Weeks | Crossed the line, performance declines |
| 4. Overtraining Syndrome | Months | Training nearly impossible |

- **Key criterion**: Only "performance decline" means crossing from cumulative fatigue into
  overtraining. Feeling tired but hitting paces = normal cumulative fatigue; feeling tired AND
  paces dropping = danger signal.
- Volume increases through easy days, small climb every 4 weeks; no crude "weekly +10%."

## 5. Test Races & Gates

- At end of speed phase (beginner W8, advanced W4/W6), may schedule **5K/10K test race** to
  calibrate marathon target pace and speed session paces.
- In-season race replacement: Replace that week's tempo with Saturday race (both stimulate
  anaerobic threshold), Sunday long run becomes a longer easy run; resume plan following week.
- May schedule 10-mile race (4–6 weeks out) as long run replacement; **in-season half marathon
  not recommended** (too close to marathon, excessive fatigue).
- **Package gates** (combined with docs/06, may be stricter):
  - Gate A: Long tempo (8–10mi @ MP) sustainability → if cannot maintain → lower marathon target,
    the most reliable target feasibility test (**veto power**, consistent with docs/06).
  - Gate B: Speed session 3mi fast volume completion at target pace → 2 consecutive failures →
    lower pace or reduce reps.
  - Gate C: Peak week long run (16mi) quality under cumulative fatigue → last segment pace drop
    >30s/mi → conservative race start.
- Marathon target pace derived from 5K/10K performance via VDOT table, final confirmation by
  tempo completion quality.

## 6. Red Lines & Cautions

- **Long run never exceeds 16 miles**: Core Hansons red line. Long runs beyond 3 hours cause
  mitochondrial/capillary damage (8 weeks non-recovery), and 20mi in low-mileage plans = 50%
  of weekly volume, violating the 25–30% guideline.
- **Easy runs must be truly easy**: 1–2 min/mi slower than MP. Beginners often run too fast due
  to low volume feeling fresh, compromising SOS-day recovery. "If easy days become tempo, tempo
  becomes strength, strength becomes speed, every session loses its target adaptation."
- **SOS never back-to-back**: Tue/Thu/Sun SOS must be separated by Easy or Off.
- **Speed sessions never exceed 100% VO2max**: Running too fast means first reps above VO2max
  producing lactate, later reps slow down, no rep at target pace — wasted effort plus damage.
- **Do not prescribe by HR**: HR only for trend monitoring; pace is core (because marathon
  target is time/pace, not HR).
- **Don't pursue "freshness" in training**: Cumulative fatigue requires never fully recovering;
  only taper period achieves full recovery. "You never want to hit your best performance in
  training."
- Ice baths only occasionally (after long runs for reset), not regular use — blocking
  inflammation = blocking adaptation signals.
- Can only be stricter than general safety layer, never relax (docs/03/06).

## 7. Strength & Auxiliary Recommendations

- Hansons "strength" has three layers:
  1. **Dynamic Warm-Up (DWU)**: Pre-run, two levels. DWU1 (6 exercises: arm circles / side
     bends / hip circles / half squats / front-back leg swings / side leg swings, ≤10 min)
     before daily runs; DWU2 (adds 6: slow skips / high knees / butt kicks / carioca / bounding
     / 4–6× 75–100m sprints, ≤20 min) before SOS sessions.
  2. **Body Weight Maintenance (BWM)**: Crunch / Back Extension / Superman / Squat / Bridge /
     Side Plank, 3 sets × 10–25 reps, after easy runs or on rest days, do at least 2 weeks first.
  3. **Resistance Training (RT)**: After BWM proficiency, 1–3 sets × 10–12 reps, 1–2×/week on
     easy days; not recommended beyond BWM stage <10 weeks before race.
- Cross-training: **don't start new activities during training**; existing habits (e.g., bike
  commute) may continue but avoid long rides on SOS days; injury recovery may use elliptical/
  stationary bike (closest to running motion).
- Static stretching: **hours after running** (not immediately post), 20 sec × 1–3 sets each;
  for tissues needing real lengthening (Achilles/hip flexors/hamstrings), hold 3–5 min,
  ~12 weeks to see effect.
- Sleep: 8h baseline + 1h/day per 10h weekly training (e.g., 15h/week training → 9.5h/night).
- Post-session recovery: 1.2g carbs/kg body weight within 30 min; replace 150% of fluid loss
  within 5 hours (in divided doses).

## 8. Application Example

Sample runner (target marathon 3:30, MP = 4:58/km, transitioning 5→6 runs/week, advanced plan):

- **W1–2 (early speed)**:
  - `Mon E8km` · `Tue Speed 12×400 @ 5K pace (+warmup3km+cooldown3km)` · `Wed Off`
  - `Thu Tempo 6km @ MP (+warmup3km)` · `Fri E6km` · `Sat E8km` · `Sun Long 14km`
- **W6–8 (speed peak + tempo lengthening)**:
  - `Mon E10km` · `Tue Speed 5×1000 @ 10K pace` · `Wed E5km (volume day)`
  - `Thu Tempo 8km @ MP (+warmup3km)` · `Fri E6km` · `Sat E10km` · `Sun Long 22km`
- **W10–12 (strength + peak)**:
  - `Mon E10km` · `Tue Strength 6×1mi @ MP−10s/mi (1/4mi jog recovery)` · `Wed Off`
  - `Thu Tempo 14km @ MP (+warmup3km)` · `Fri E6km` · `Sat E10km` · `Sun Long 26km`
- **Taper (final 10 days)**:
  - Last SOS 10 days before race; thereafter run daily but distances halved, race week total =
    45% of peak.

## 9. Mandatory Checks (Post-Generation Self-Test)

1. **Intensity composition**: Easy running (including easy segments in long runs) ≥60% by time;
   SOS ≤3 sessions/week (Tue speed/strength + Thu tempo + Sun long); SOS must be separated by
   Easy/Off. Speed session fast volume = 3mi, strength high-intensity volume = 6mi, tempo
   progressive ≤10mi. Long run ≤16mi and ≤25–30% weekly volume and ≤3 hours. When exceeding,
   first reduce SOS intensity/reps, never touch easy runs.
2. **Fatigue quantification & management**: Measure via "SOS pace achievement rate + easy-run HR
   drift + morning resting HR + subjective mood"; cumulative fatigue is the plan's goal (feeling
   tired but hitting paces = normal); **pace decline is the only reliable crossing signal** —
   when it appears, lower pace/reduce SOS, add recovery if needed. Overtraining continuum:
   Fatigue (24–48h) → Functional overreaching (≤2 weeks = target) → Nonfunctional (weeks) →
   Syndrome (months).
3. **Macro/micro cycles**: Micro = Tue speed/strength + Thu tempo + Sun long, rest Easy;
   Macro = Base (all E) → Speed+Tempo → Strength+Peak → Taper (10 days). Speed sessions early
   in cycle, strength in mid-late, tempo throughout and progressively lengthening. Long runs
   alternate with long tempo weeks (advanced plans), avoiding 3 long sessions in 8 days.
4. **Easy run standard**: Easy = 1–2 min/mi slower than target marathon pace (~55–75% VO2max),
   pace as primary criterion (not HR); day after SOS / beginner transition use slow end
   (−2 min/mi), day after tempo / before long run use fast end (−1 min/mi). Easy runs are not
   "junk miles" — 49% of peak weekly volume, responsible for slow-twitch fiber development, fat
   oxidation, capillary proliferation, and heart enlargement.
