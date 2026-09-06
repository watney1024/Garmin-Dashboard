# Prompt · Push the schedule to Garmin `schedule_to_watch`

> Purpose: push this week's pushable run sessions into Garmin (the watch calendar shows
> the day's workout). Send the whole block, replace `<...>`.

```
[schedule_to_watch] Please push this week's (starting today, W__) pushable run sessions
to my Garmin:
1. Read this week's schedule in <PLAN_HTML> and the runner profile <RUNNER_PROFILE.yaml>;
   identify session kinds this package allows (e.g. E / recovery / LSD / long run). Kinds
   the coach package or profile excludes are never scheduled.
2. Follow the training doctrine (docs/05 §3): E/recovery = time + HR cap; name workouts
   with the date and session name (e.g. W1 Tue E5).
3. Use garmin-mcp's create_run_workout + schedule_workout (or run
   scripts/garmin_schedule.py <week_spec>) onto the right dates; keep it idempotent
   (reuse the registry).
4. When done, tell me which sessions were scheduled (date + name) and remind me to sync
   the watch. If a non-A race falls this week, say how it appears on Garmin.
```
