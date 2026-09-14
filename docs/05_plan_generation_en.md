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
   - Age/sex correction: when the profile has `identity.birth_year`+`identity.sex` and the
     runner's age falls outside 18–38, derive the **age-graded VDOT** (docs/09 §8) and
     prescribe from it.
   - A-race goal: start from the VDOT equivalent for the race distance, then make a
     conservative correction for endurance gaps/history;
   - Paces always come from the **current VDOT** — never from an aspirational target.
4. **Period**: count N weeks **backwards from the A race** (length set by the coach
   package, e.g. 16/18 weeks); mark where the non-A races fall (role decides how they run).
5. **Weekly skeleton**: coach §3 assembles the weekly shape from the profile's
   `runs_per_week / long_run_day / quality_days`.
6. **Fill the week-by-week schedule**: a base→build→peak→taper volume curve (coach §4 plus
   the generic safety layer); sessions named `W<n> <weekday> <type> <key info>`. Emit the
   schedule as a **calendar** (grouped by phase, one row per week, all seven Mon–Sun columns,
   rest days shown). Points-based coach packages (e.g. daniels_vdot) also set a **weekly point
   target**; quality-session amount caps come from `vdot.py --session N` (book Table 5-5,
   docs/09 §7).
7. **Add the guardrails**: coach §6 red lines + the generic safety layer (docs/03) merged
   into the "red lines & gates" chapter; the three gates land on concrete weeks/dates using
   the A race and the non-A tests.
8. **Add milestones**: put a **milestone table** inside chapter 4 (cycle structure), see §4.
   A milestone is an **achievement marker**, unlike a gate, which is a **decision point** — a gate
   result may change the plan, whereas a missed milestone is **recorded only and never changes the
   plan by itself**. Each milestone needs a target week/date and a criterion **directly verifiable
   from the data**; the lower the starting volume, the more **front-loaded** the milestones must be.
9. **Produce the HTML** (structure in §4); the version table records `v1` and its basis.
10. **Self-check** (§5) before delivery.

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

Each plan is a **self-contained HTML file**: inline `<style>` + inline `<script>`, exactly two
`<canvas>` (`id="vol"` / `id="trk"`), and **no external dependencies whatsoever** (no CDN, no
web fonts, no external scripts/stylesheets — the plan must open offline and print directly).
Charts are drawn on plain canvas.
**Chapter slots are fixed; the content is filled from the coach package + profile:**

| chapter | content | data source |
|---|---|---|
| header | five stat cards (weeks to race / cycle volume / peak week / longest run / quality-session frequency) + one-line lede (dates, goal pace, weekly skeleton, coach package, VDOT, version) | profile / VDOT / coach |
| 1 Weekly skeleton | 7-day `weekgrid` (role + intensity colour per day) + why the strength/key days sit where they do | coach §3 |
| 2 How the key session is run | the session this runner is most likely to get wrong, in full ("Q→A→why" block `.ans` + a standard-execution table) | coach §2 + profile |
| 3 Working with others / constraints | external coach sessions, run clubs, strength days, cross-training (climbing, cycling…) and how they yield to running | profile `constraints`/`strength` |
| 4 Cycle structure & volume curve | phase table (phase / weeks / dates / volume / core task) + **milestone table** (id / name / target week & date / verifiable criterion / achieved column) + `<canvas id="vol">`: stacked bars = weekly volume (race stacked on top) + line = that week's long run; **must show the per-week values on mouse hover** (a self-contained `.ctip` tooltip with the week, date range and each series value); legend via `.lg` | coach §4 + profile |
| 5 Week-by-week schedule | **calendar form**: grouped by phase, one row per week, columns fixed as `week ｜ Mon…Sun (all 7 days) ｜ total`; each cell starts with the date then that day's content, **rest days shown as "休息"/rest**; the total column counts running distance only | flow §6 |
| 6 Recovery weeks & holiday plans | what the recovery week is for (and why that week); holiday/travel triage order; race-week taper | coach §4 + generic |
| 7 Paces & HR zones | zone table (zone / pace / HR use / where used) + "how this session is run" doctrine + age-grading status statement | docs/09 + coach §2 |
| 8 Strength & auxiliary | weekly placement, exercise floor, spacing from runs, periodisation; auxiliary sessions (strides etc.) | coach §7 + profile |
| 9 Red lines & decision gates | generic safety layer + coach red lines; `.gates` cards (gates 1/2/3 on concrete dates with thresholds) | docs/03/06 + coach §5/§6 |
| 10 Tracking & weekly review (**the constitution**) | collaboration protocol, **known-deviations table** (where the plan departs from docs/coach + re-check condition), plan-vs-actual table + `<canvas id="trk">`, version table | docs/06 |

Layout elements (class names per `examples/plan.example.html`): `.cards/.card` stat cards,
`.weekgrid/.wday` week grid, `.tw` horizontally scrolling table shell, five callout styles
`.note/.warn/.key/.ok/.ans`, `.ask` collaboration items, `.phase` phase headings,
`.gates/.gate` gate cards, `.chart` chart container, `.ctip` chart hover tooltip, `.foot` footer.
- **Chart read-out rule**: both canvases must let you **hover to read the per-week values** — the
  static picture only shows shape. The tooltip must be **self-contained** (plain DOM + inline CSS,
  zero external libraries) and **hidden when printing**
  (`@media print{ .ctip{display:none !important;} }`) so it never covers the chart.

Conventions:
- **Chapters 2 and 3 are named per runner** (replace with this runner's key session / real
  constraints; a runner with no external coach may merge them). All other slots are fixed.
- For naming, charts, and the review protocol, **follow `examples/plan.example.html` as the
  structural reference** (copy its skeleton and CSS variables, then fill in content).
- **Chapter 10 (tracking & weekly review) is that runner's "constitution"**: when it and the
  docs disagree, the plan chapter wins (write that sentence into the plan at generation time).
- The version table sits at the end of chapter 10: every change appends a `vN` row (what
  changed + why + trigger), incrementing without gaps.
- **A gate is not a milestone**: a gate is a **decision point** (its outcome may change the plan,
  see chapter 9); a milestone is an **achievement marker** (missed = recorded only, never an automatic
  plan change, see chapter 4). They do not substitute for each other: gates are few and heavy,
  milestones are front-loaded.
- If the plan **deliberately deviates** from a coach cap (e.g. long-run share at low volume),
  it must be logged in chapter 10's known-deviations table with the reason and the re-check
  condition — **deviations must leave a trace, never silent**.

## 5. Self-check before delivery

- [ ] Every session pace traces back to `data/vdot/` or to the "HR/feel" doctrine;
      no invented numbers.
- [ ] The weekly skeleton matches the profile: session count, long-run day, quality days.
- [ ] The volume curve obeys the coach and the generic safety layer (increase %, single-run
      share, recovery weeks); recovery-week rebound and race weeks are excluded from the
      increase comparison, and that rule is stated in the plan.
- [ ] Exactly one A race; non-A races do not threaten it (folded into that week's long run
      or a separate cut-back week).
- [ ] Gates/red lines state both trigger and action, and include a veto such as
      "conservative start on race day".
- [ ] The version table records this generation's basis.
- [ ] **Self-contained**: no external references at all (CDN/fonts/images), exactly two
      canvases (`vol`/`trk`), no BOM.
- [ ] **All chapters present**: 1–10 in place; chapter 10 carries the "this file is the
      constitution" sentence and the known-deviations table.
- [ ] **The weekly table is a full calendar**: one row per week, all seven Mon–Sun columns
      present, **rest days shown as well** (never list only the days with sessions), each
      cell dated.
- [ ] **Numbers agree**: the `#vol` volume array == the schedule table's total column; the
      `#trk` plan array matches it and the actual array is the same length and initially
      empty.
- [ ] **Charts are hoverable**: both canvases' `draw()` stores its geometry on the element and
      binds `mousemove`/`mouseleave` (values on hover, hidden on leave); the tooltip is
      self-contained and hidden in print.
- [ ] **The milestone table is present**: every entry has a target week/date and a criterion
      **verifiable from the data** (no "feels stronger" style entries); and milestones are kept
      separate from gates — a milestone must never read as a condition that changes the plan.
- [ ] Any deliberate deviation from a coach cap is traced in chapter 10's
      known-deviations table (reason + re-check condition).

## 6. Don't, when generating

- Don't invent PRs/results the profile lacks; ask for a test or use the most recent
  available with its date.
- Don't prescribe using an aspirational VDOT; don't use paces contradicting the VDOT table.
- Don't write hard numbers like "week X is always Y km" that conflict with the coach or
  profile.
- Don't leak more identifiable detail than the runner's alias allows.
- Don't write **milestones as gates** (a missed milestone must not auto-change the plan); don't set
  milestones that cannot be verified from data (e.g. "better form").
- Don't make every milestone a performance number — a runner starting from a low base needs
  **consistency / health** milestones too (e.g. "3 straight weeks at ≥90% completion", "weekly
  average resting HR does not rise"), otherwise the first weeks show nothing achieved.
