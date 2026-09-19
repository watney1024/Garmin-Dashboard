# 07 · Runner playbook: you only do two things (for the human runner)

This manual is **for you (the runner)**. You don't need to learn or manage anything the
agent does; you only:

1. Say **one sentence** about your body each week (or whenever you want).
2. Maintain your `runner_profile.yaml` (change it when races/available days/PRs change).

## 1. The weekly one sentence

Fill in this template:

> `8/10 Tue E5, done. Lungs tired first, legs fine.`
> Six elements: date(day-direction) + weekday + session name + completion + what tired
> first + reason for deviation.

- **What tired first** matters most: `legs first` = leg fatigue, `lungs first` = cardio.
- **Reason for deviation** decides whether the agent treats it as an "active cutback
  (fine)" or a "passive drop (manage it)".
- Injuries can be reported **on their own, no need to wait for Monday** — especially
  unilateral pain ≥5 (0–10): say it immediately.
- Data (master + per-session detail) is pulled automatically: **you don't export CSVs,
  don't drop files, don't rename anything.**

## 2. Common requests

| you want | send | result |
|---|---|---|
| **first time: build a profile** | `prompts/collect_profile` | the agent interviews you question by question (reading what Garmin can already answer) → `runner_profile.yaml`, validated at 0 errors |
| generate/re-plan (new goal/coach) | `prompts/generate_plan` | a new HTML plan (calendar/A race/paces/gates/version) |
| weekly update (usually Monday, automatic) | `prompts/weekly_update` | log + review + light + plan changes + ≤400-char summary |
| this week's schedule | `prompts/current_week_schedule` | the 7-day schedule + key-session notes |
| push the schedule to your watch | `prompts/schedule_to_watch` | workouts appear in Garmin calendar; sync the watch |

Copy the text from the `prompts/` directory and replace `<placeholders>` with your actual
paths/profile. If you would rather not be interviewed, fill in the blank questionnaire at
`examples/runner_profile.questionnaire.yaml` or run the interactive wizard
`python scripts/profile_wizard.py` — all three collect exactly the same fields.

## 3. When to look at the plan, when not

- **Daily**: check resting HR on the watch before getting up; glance at the day's session
  before heading out.
- **Monday**: say your sentence, then skim the agent's ≤400-char summary (colour +
  next-week changes).
- When a yellow/red light fires, just follow the actions in the summary — don't research
  how much you "should" run.
- Feel off or suspect an injury → say so and let the agent judge; don't tough it out.

## 4. Races

- Only one A race is all-out; **every other race is training or an attempt** (role lives
  in the profile) — run them the way the plan says.
- After the A race: tell the agent the time; it updates PR & VDOT and plans post-race
  recovery.

## 5. Three red lines you must follow

1. Unilateral persistent pain / night pain / pain that worsens while running → stop for
   48 h; don't "run it out".
2. Resting HR >8 bpm above normal: **1 day → flag it (yellow)**; **2 consecutive days → rest
   that day** (that day only — not a 3-day layoff).
3. Want to change the plan ad hoc? Say it first (let the agent judge whether it harms the
   A race).

## 6. Reminders

- **Not finishing is not the problem; not reporting is.** Even if you ran half, say so.
- The agent reads paces/HR from the data; you only own the "how does my body feel" half.
- Coach packages are generic summaries and the VDOT tables come from a GPL-3.0 export;
  see a doctor for any medical/injury questions.
