# 08 · Runner profile: the input to plan generation (for AI agents)

`runner_profile` is the **runner's profile** — a YAML file holding goals and the A race,
trainable days, PRs, constraints and baselines. **It drives all plan generation**: no
profile, no plan — interview the runner and complete it first.

- The real profile is a private runtime file (gitignored; put it at
  `workspace/runner_profile.yaml`).
- The repo only ships a fabricated example: `examples/runner_profile.example.yaml`.
- On first contact, copy the example as a skeleton and fill it in through one structured
  Q&A round; afterwards maintain it weekly.

## 1. Field reference

```yaml
identity:
  alias:           # alias/handle (never a real name)
  language:        # docs language: zh | en
  timezone:        # affects week boundaries, e.g. Asia/Shanghai
races:
  - name:          # race name (anonymised, e.g. "示例国际马拉松")
    date: YYYY-MM-DD
    distance: marathon | half | 10k | 5k | ...
    role: A | attempt | training   # see "multiple races & the A race"
    note:          # optional: fuelling/course notes
weekly:
  runs_per_week: N
  days:            # weekday -> role map (sparse ok)
    Tuesday: quality
    Thursday: easy
    Friday: easy
    Sunday: long
  long_run_day: Sunday
  quality_days: [Tuesday]     # may be several; "quality" defined by the coach package
  max_run_min:     # optional: single-session time cap (constrains the weekly skeleton)
pr:
  5k: MM:SS        # best results (>=1 needed to derive VDOT)
  10k: MM:SS
  half: H:MM:SS
  marathon: H:MM:SS
coach: daniels_vdot            # chosen coach package id, see coaches/
strength:          # optional
  sessions_per_week: N
  days: { Wednesday: lower, Saturday: "upper/core/calf" }
constraints: []    # free text: injury history, schedule, travel, recovery preferences
metric_baselines:  # baselines for yellow/red decisions (docs/03)
  resting_hr: 50
  weight_kg: 62.0
  sleep_h: 7.2
```

## 2. Multiple races & the A-race model

A runner may have several races. **Every race must carry a `role`**; the three are
mutually exclusive:

| role | meaning | how to run it | does the result update PR/VDOT |
|---|---|---|---|
| `A` | the **only** race you run all-out for a result; end of the cycle | all-out; taper the preceding two weeks; the whole cycle serves it | yes (after the race) |
| `attempt` | a try/test that approaches a result but is still part of the training plan | committed but not do-or-die (e.g. half marathon treated as a long run whose last third picks up) | yes (if it beats a PR) |
| `training` | part of a training session | not all-out: run as MP segments / strides / negative-split long run | no |

Rules:
1. **Only one `A` per cycle.** If two appear → confirm with the runner and downgrade one
   to attempt/training, recording the reason.
2. **Changing the A race must be recorded** (lottery miss / injury / fitness) and the cycle
   & taper recomputed.
3. Non-A races **must not wreck the A race**: when one conflicts with that week's long run,
   it *is* that week's long run (run the `role=training` way) instead of adding volume.
4. Scheduling, reviews and gates are anchored backwards from the **next A race**; non-A
   races only change that week's content.

## 3. VDOT and PRs (details in docs/09)

- Derive VDOT from the **most recent (<6 months) and most trustworthy** PR; validate it
  against other distances (should agree within ~1).
- Stale or cross-cycle results → run a recent A/attempt race first, then set paces.
- After a race: write the new result into `pr` (keep the date), trigger a VDOT update; if
  VDOT changes by ≥1, propose a plan update through the weekly-review flow.

## 4. Choosing the coach package (see docs/10 / coaches/)

- `coach` stores a package id that **must match a directory `coaches/<id>/`**.
- Before generating a plan: read the selected package in full and obey it. If the profile
  and package clearly mismatch (target distance / weekly volume / ability band), explain
  and propose a switch; only switch after the runner confirms.
- Switching coach = regenerate the plan = a new major version entry.

## 5. How the weekly skeleton is built (consumed by docs/05)

1. Take the weekday→role map from `weekly.days`; unmapped days default to "optional/rest".
2. The coach package's skeleton rules distribute E / Q / long across the available days
   using `runs_per_week`, `long_run_day` and `quality_days`.
3. Generic constraints apply: no heavy lower-body work the day before a long run or a Q
   day (safety layer, docs/03); `max_run_min` (if set) caps single sessions.
4. Session naming in the per-week table: `W<n> <weekday> <type> <key info>` (e.g.
   `W1 Tue E5`, `W6 Sun Tune10K(training)`).

## 6. Maintenance cadence

- The runner may change things any time: race calendar (entries/cancellations/A-switch),
   trainable days, injury constraints.
- After each weekly review, if a race result / PR changed → update this file and mention it
   in the review's "next-week adjustments".
- Versioning: the runner profile is not code; changes are explained in the weekly review
   and do not enter the plan's version table.
