# 00 · Overview: what this is & how to collaborate (for AI agents and runners)

## 1. One-liner

An "**AI training companion**": an agent reads the rules in this repo and turns a runner's
Garmin data into a training plan that is **executable and keeps evolving by itself**. The
runner does two things only: maintain the `runner_profile` + say one sentence a week.
**Humans don't write code.**

## 2. Division of labour

| who | what | frequency |
|---|---|---|
| runner | one sentence (body + session names, docs/03); maintain profile (docs/08); follow yellow/red actions | ~30 s/week |
| agent · data | pull Garmin (docs/01), rebuild master/inbox, match, compute completion | Monday |
| agent · plan | summarise the past (docs/04) → generate/update the HTML plan (docs/05) | first/on demand |
| agent · review | fill 6 metrics → 4-section review → judge yellow/red → edit plan → version `vN` (docs/06) | weekly |

## 3. Data flow

```
Garmin Connect ──MCP stdio──> scripts/garmin_pull.py ──> Activities.csv + inbox/activity_<id>.csv
        runner_profile.yaml + coach package(coaches/) + VDOT(09) ──> plan HTML(05)
        weekly review(06) ──> edit plan + version vN + update profile
```

## 4. Repo map

| path | role | read by |
|---|---|---|
| `AGENTS.md` | agent entry point | agent first stop |
| `docs/00–10` | rule docs (bilingual _zh/_en) | agents, all |
| `coaches/` | coach methodology packages (4 initial + template) | agents, loaded fully before plan generation |
| `prompts/` | copy-paste prompts for the agent | runners |
| `scripts/` | data / schedule / VDOT tools (stdlib only) | run directly |
| `data/vdot_table.csv` | approximate VDOT pace table (TODO authoritative) | lookups |
| `examples/` | fabricated example-runner set (CC0) | study by analogy |
| `LICENSE / NOTICE.md` | MIT + third-party notices | — |

## 5. Core conventions (everyone obeys)

- **Versioning**: any plan edit appends a `vN` row to the plan's version table (what +
   why), incrementing, never skipping.
- **Fresh data**: with MCP tools available, pull & rebuild first; otherwise state the
   data-cutoff date.
- **Title governance**: rename information-free Garmin default titles to real session
   names via `set_activity_name` when the name is known.
- The authoritative definitions of **light rules / three-tier data protocol / one-sentence
   template** live in the *constitution chapter* of the runner's plan HTML; where this
   repo's docs disagree, the plan wins.
- **Training doctrine** (docs/05 §3): low intensity = HR authority + time fallback; quality
   = pace band + distance load + HR as alarm; cadence first in the late long run where the
   coach/plan requires it; everything by HR in hot weather.
- **The generic safety layer cannot be loosened** (docs/03/06): unilateral injury ≥5 = red,
   resting HR +8, the yellow/red action table… coach packages may only tighten it.

## 6. Doc map

| doc | contents |
|---|---|
| 01 | garmin-mcp install/auth (CN = PR #249 / intl = main), script envs, tool list |
| 02 | data formats: 16-col master, inbox, week-spec, registry, pitfalls |
| 03 | six subjective metrics, one-sentence template, injury scale, yellow/red safety baseline |
| 04 | summarising past training (comparability discipline, outputs, known mistakes) |
| 05 | plan generation: profile + coach + VDOT → HTML plan (chapter slots, doctrine, self-check) |
| 06 | weekly review: four sections, the lights, gates, plan-change mechanics, post-race handling |
| 07 | runner playbook (human view: how to ask, three red lines) |
| 08 | runner profile schema: multiple races & the A race, fields, maintenance |
| 09 | VDOT: concept, tooling, conversions, approximation statement |
| 10 | adding a new coach skill |
