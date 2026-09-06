# 05 · Plan generation: profile + coach package + VDOT → HTML plan (for AI agents)

This document defines the generic flow for **generating/regenerating a training plan** and
the HTML output structure. The methodology "parameters" come from the runner profile
(docs/08) and the chosen coach skill (`.agents/skills/coach-<id>/`, Agent Skills
standard); the numbers come from VDOT
(docs/09). Worked output: `examples/plan.example.html`.

## 1. When to generate / regenerate

- **First time**: profile + coach package ready (version table gets `v1`).
- **A-race switch / coach switch**: full re-plan (new major version).
- **VDOT drift ≥1**: after confirmation in the weekly review, update only the paces (minor
  version, no cycle re-layout).

## 2. Generation flow (fixed order)

1. **Read the profile**: `runner_profile.yaml` (interview first if absent, see docs/08).
2. **Load the coach skill**: read `.agents/skills/coach-<coach>/SKILL.md`, then the full
   method `references/coach-<coach>_<lang>.md` (`<coach>` = profile's `coach`, `_`→`-`;
   `<lang>` = profile `language`); if the fit is
   poor, propose a switch and get consent before changing.
3. **Level & goal**: derive VDOT from the profile `pr` (docs/09 §5) → E/M/T/I/R pace bands.
   - A-race goal: start from the VDOT equivalent for the race distance, then make a
     conservative correction for endurance gaps/history;
   - Paces always come from the **current VDOT** — never from an aspirational target.
4. **Period**: count N weeks **backwards from the A race** (length set by the coach
   package, e.g. 16/18 weeks); mark where the non-A races fall (role decides how they run).
5. **Weekly skeleton**: coach §3 assembles the weekly shape from the profile's
   `runs_per_week / long_run_day / quality_days`.
6. **Fill the week-by-week schedule**: a base→build→peak→taper volume curve (coach §4 plus
   the generic safety layer); sessions named `W<n> <weekday> <type> <key info>`.
7. **Add the guardrails**: coach §6 red lines + the generic safety layer (docs/03) merged
   into the "red lines & gates" chapter; the three gates land on concrete weeks/dates using
   the A race and the non-A tests.
8. **Produce the HTML** (structure in §4); the version table records `v1` and its basis.
9. **Self-check** (§5) before delivery.

## 3. Training doctrine (deciding "how a session is run"; every coach must comply)

- **Low intensity (E/recovery)**: HR/feel is the only authority, time is the fallback;
   pace is only a reference (VDOT E band as a floor). Hot weather / poor sleep / fatigue →
   switch fully to "HR mode".
- **Quality (T/I/M segments/tests)**: pace given as a band, distance sets the load, HR is
   an alarm (unusually high or drifting → slow down).
- **Late long-run**: if the coach/plan asks for cadence priority (e.g. ≥170), cadence > pace
   > HR.
- **Strength**: by reps×weight; unrelated to running-intensity doctrine.
- One-liner: **main work is load-by-distance and checked-by-pace; in recovery or degraded
  conditions switch everything to time + HR.**

## 4. HTML output structure (the "dashboard" slots)

Each plan is a self-contained HTML file (inline CSS + two `<canvas>`). **Chapter slots are
fixed; the content is filled from the coach package + profile:**

| chapter | content | data source |
|---|---|---|
| header | runner alias, A race & goal, VDOT, coach package, plan length | profile / VDOT / coach |
| 1 Goals & calendar | the A/attempt/training races with roles; how non-A races are run | profile `races` |
| 2 Weekly skeleton & phases | the 7-day role map, base/build/peak/taper phases | coach §3/§4 |
| 3 Intensity system & paces | zone table: zone / pace / HR use / typical session; paces from the data/vdot tables | docs/09 + coach §2 |
| 4 Week-by-week schedule | `week｜dates｜each day｜weekly volume`; non-A-race & recovery weeks flagged | flow §6 |
| 5 Volume curve | `<canvas id="vol">` weekly-volume bars + long-run line | flow §6 |
| 6 Recovery / holiday / race-week plans | purpose of recovery weeks; frequency rules for holidays/travel; race-week taper | coach §4 + generic |
| 7 Red lines & decision gates | generic safety layer + coach red lines; gate table (gates 1/2/3 on concrete dates) | docs/03/06 + coach §5/§6 |
| 8 Tracking & weekly review | Monday actions, review template, plan-vs-actual + `<canvas id="trk">`, version table | docs/06 |
| 9 Strength & auxiliary (if the profile has strength) | weekly placement and exercise floor | coach §7 + profile |

Conventions:
- For naming, charts, and the review protocol, **follow `examples/plan.example.html` as the
  structural reference** (copy its skeleton, then fill in content).
- `版本记录` (version table) sits at the end: every change appends a `vN` row (what
  changed + why), incrementing without gaps.
- The plan's tracking chapter (or last chapter) acts as that runner's "constitution": when
  it and the docs disagree, the plan chapter wins (this sentence is written into the plan
  at generation time).

## 5. Self-check before delivery

- [ ] Every session pace traces back to `data/vdot/` or to the "HR/feel" doctrine;
      no invented numbers.
- [ ] The weekly skeleton matches the profile: session count, long-run day, quality days.
- [ ] The volume curve obeys the coach and the generic safety layer (increase %, single-run
      share, recovery weeks).
- [ ] Exactly one A race; non-A races do not threaten it (folded into that week's long run
      or a separate cut-back week).
- [ ] Gates/red lines state both trigger and action, and include a veto such as
      "conservative start on race day".
- [ ] The version table records this generation's basis.

## 6. Don't, when generating

- Don't invent PRs/results the profile lacks; ask for a test or use the most recent
  available with its date.
- Don't prescribe using an aspirational VDOT; don't use paces contradicting the VDOT table.
- Don't write hard numbers like "week X is always Y km" that conflict with the coach or
  profile.
- Don't leak more identifiable detail than the runner's alias allows.
