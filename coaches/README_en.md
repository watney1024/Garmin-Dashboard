# coaches/ — coach methodology packages

> Before generating a plan, an agent MUST load the chosen coach's `README` in full and obey it.
> 生成计划前，agent 必须整包加载所选教练的 `README` 并照它执行。

## Index

| id | methodology | one-liner | good for |
|---|---|---|---|
| `daniels_vdot` | Jack Daniels VDOT | one score sets every zone's paces; cycles driven by VDOT progress & tests | runners with a clear goal distance who can calibrate via 5K/10K (used by the example plan) |
| `polarized_80_20` | Matt Fitzgerald 80/20 | ~80% of time easy + ~20% hard | volume-hungry, injury-prone or high-mileage amateurs |
| `hanson` | Hanson's Marathon Method | cumulative fatigue; mid-week quality + weekend medium-long runs | marathoners who dislike very long singles and prefer accumulated load |
| `advanced_marathoning` | Pfitzinger & Douglas *Advanced Marathoning* | long cycles, higher mileage, Sunday long runs with MP segments + mid-week tempo/intervals | experienced runners preparing systematically for a marathon |

**All packages are this repo's own "summary + application guide", not copies of the source
books (see NOTICE.md).**

## Which when?

1. Read `docs/08_runner_profile_en.md` and the runner's profile → judge goal distance,
   runs per week, ability band, time budget.
2. Match at least **goal distance** and **weekly volume budget**; otherwise explain and
   propose a switch, changing only after the runner confirms.
3. There is no single "right" answer — a coach package is a **philosophy choice** made by
   the runner; the agent's job is to present the differences honestly.

## Loading rules

- Read only `coaches/<id>/README_{lang}.md` (language from the profile's `language`).
- The file is self-contained: intensity definitions, weekly-skeleton rules,
   periodization, gates, red lines, strength advice.
- Where a package conflicts with the **generic safety layer** (docs/03, docs/06), the
   stricter one wins; the generic safety layer **cannot be removed**.

## Adding a package

Write a new directory `coaches/<new_id>/README_{zh,en}.md` following the fixed sections in
`coaches/_TEMPLATE_{zh,en}.md`, then add one row to the index table above. Full guide:
`docs/10_adding_a_coach_skill_en.md`.
