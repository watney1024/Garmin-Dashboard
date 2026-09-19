# Prompt · Push the schedule to Garmin `schedule_to_watch`

> Purpose: push this week's pushable run sessions into Garmin (the watch calendar shows
> the day's workout). Send the whole block, replace `<...>`.

```
[schedule_to_watch] Please push this week's (starting today, W__) pushable run sessions
to my Garmin:
1. Read this week's schedule in <PLAN_HTML> and the runner profile <RUNNER_PROFILE.yaml>;
   identify session kinds this package allows (e.g. E / recovery / LSD / long run). Kinds
   the coach package or profile excludes are never scheduled.
2. **Split the session kinds first**:
   - **Continuous runs** (E / recovery / LSD / long run) → the week-spec route in step 4;
   - **Track / interval sessions** (sets, per-rep distance, a lap target — e.g. a club
     session of 6×1.2k) → **must** go through `scripts/garmin_track_workout.py` plus the
     `.agents/skills/track-workout/` SKILL.md (read it first)
     (`endCondition = lap.button`: each press records a nominal 400 m, decoupled from the
     real lap length). Between reps, **standing still** is `"rest"` and **jogging** is
     `"recovery"` — **the default is `rest`**; get it wrong and the watch nags me to run
     during the rest. The warm-up step carries **no HR target**
     (`warmup.hr_min/hr_max` is deprecated; it only logs a WARNING).
     **Never** approximate an interval session with `create_run_workout`: it can only build
     continuous runs and throws away all the structure.
3. Follow the training doctrine (docs/05 §3) for continuous runs: E/recovery = time + HR cap;
   name workouts with the date and session name (e.g. W1 Tue E5).
4. **Always `--dry-run` first** and read the per-session verdict (`create` / `reuse` /
   `replace` + reason) before doing it for real. Both scripts are idempotent by **name + content
   fingerprint**: when the prescription changes, just **re-run** — the script rebuilds as
   create new → schedule new → delete old (create before delete, so a mid-way failure never
   empties the watch). **Stop hand-renaming workouts to dodge reuse** (that was the old trap),
   and don't assume a change can't reach the watch just because the name stayed the same. Use
   garmin-mcp's create_run_workout + schedule_workout onto the right dates (or run
   `scripts/garmin_schedule.py <week_spec>`).
5. **Title governance**: rename this week's already-recorded activities with
   `set_activity_name` to meaningful session names (Garmin's default titles like
   "XX district Running" are noise).
6. When done, tell me which sessions were scheduled (date + name) and remind me to sync
   the watch. If a non-A race falls this week, say how it appears on Garmin.
```
