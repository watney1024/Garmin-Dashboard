# Prompt · Weekly update `weekly_update`

> Purpose: review the past week (Mon–Sun) and write results back into the training log /
> weekly review / plan. Usually run every Monday; can be sent manually. Replace `<...>`.

```
[weekly_update] Today is <month/day>. Please complete the update & adjustment for the
previous training week (Monday–Sunday):

1. Refresh objective data: if garmin_mcp tools are loaded, paginate get_activities to
   rebuild <DATA_DIR>/Activities.csv (keep the 16-column canonical format & ordering,
   docs/02); for new activities call download_activity_file(activity_id, format="csv")
   into <DATA_DIR>/inbox/activity_<id>.csv. If tools are unavailable, read the existing
   files and state the data-cutoff date in your conclusion — never ask me to export.
2. Read the runner profile <RUNNER_PROFILE.yaml> and the plan <PLAN_HTML>; confirm the
   current A race / week (W__).
3. Fill the 6 subjective metrics: resting HR / weight / sleep / RPE / injury 4 sites /
   deviation reason into <TRAINING_LOG> for the matching W section; write "主观数据缺失"
   where missing; the injury line has priority.
4. Write the review: append a four-section entry (docs/06) to <WEEKLY_REVIEW> and update
   the gate-progress table; the light judgement cites the exact generic-safety rule.
5. Judge the light and adjust the plan if needed: on yellow/red or a gate result, edit
   <PLAN_HTML> (week tables, plan-vs-actual `canvas id=trk` actual array), append a vN row
   to the version table and bump; on a race result sync the runner profile & VDOT.
6. Reply in ≤400 characters: last week's volume/completion, risk colour, next-week
   changes, and one thing for me to watch.
```
