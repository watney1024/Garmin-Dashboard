# Prompt · Weekly update `weekly_update`

> Purpose: review the past week (Mon–Sun) and write results back into the training log /
> weekly review / plan. Usually run every Monday; can be sent manually. Replace `<...>`.

```
[weekly_update] Today is <month/day>. Please complete the update & adjustment for the
previous training week (Monday–Sunday):

1. Refresh objective data:
   (a) **Wellness baseline**: run `python scripts/garmin_wellness.py --since <last Mon> --until <last Sun>`, producing `<DATA_DIR>/garmin_wellness.json` (resting HR / sleep / HRV / weight / training status; schema in docs/02 §4b). **Resting HR, sleep and weight all live in this file — do not hand-roll MCP calls for them.**
   (b) **Activities**: paginate get_activities to rebuild <DATA_DIR>/Activities.csv (keep the 16-column canonical format & ordering, docs/02); for new activities call download_activity_file(activity_id, format="csv") into <DATA_DIR>/inbox/activity_<id>.csv. If tools are unavailable, read the existing files and state the data-cutoff date in your conclusion — never ask me to export.
2. Detect sensors & advanced data: besides the watch the runner may wear an **HR strap**,
   a **running-dynamics pod**, or a power meter (Stryd, …). **Work it out from the data
   first; only ask me when you can't**:
   - HR-strap-only: **ground-contact-time balance** (groundContactBalanceLeft) ·
     **respiration rate** · stance-time percentage — a wrist sensor produces none of these;
     the FIT file also gains a paired `source_type=antplus` device (**serial number** is a
     harder tell than field presence).
   - Running pod / power meter: vertical oscillation · ground contact time · step length · power.
   - ⚠ Same-named fields may come from **different sensors** (the wrist also reports GCT/VO)
     with **different scales**: the week the sensor changes is a **break point** — comparing
     across it reads "new device" as "better form". Note the break date in the log & review.
   - **Mixed sources — whose numbers win** (applies **only when the runner owns an accessory
     and the data mixes "with" and "without"**; a **watch-only** runner is unaffected — do not
     add "low confidence" noise labels for them):
     · **Never compare across sources** — trends, HR drift and efficiency only within one source;
     · When the two conflict and you must pick, **trust the accessory** — **heart rate**
       especially (optical wrist HR is unreliable during intervals / high intensity);
     · **Measure HR anchors (HRmax, lactate threshold) with the strap**; if an existing anchor
       came from strap-less data, treat it as **pending re-check**, not as fact.
   - Use the advanced data: balance for **unilateral** injury signals, GCT/VO for form drift
     in the **fatigued last third**, respiration for ventilatory adaptation; always compare
     **by segment (first/middle/last third)**, never whole-session averages (interval rest
     laps pollute them).
   - Record the conclusion (device, first-seen date, which activities) in the <TRAINING_LOG>
     W section. **If you genuinely can't tell, ask me**: which accessory, since when, and
     which sessions it was left off.
3. Read the runner profile <RUNNER_PROFILE.yaml> and the plan <PLAN_HTML>; confirm the
   current A race / week (W__); sync any sensor change (added/retired) back to the profile.
4. Fill the 6 subjective metrics: **read morning resting HR / weight / sleep straight out of
   `<DATA_DIR>/garmin_wellness.json`** (resting HR = `days[].resting_hr.bpm`, sleep =
   `days[].sleep.data.sleep_seconds`, weight = `body_composition`), then put them with
   RPE / injury 4 sites / deviation reason into <TRAINING_LOG> for the matching W section.
   Write "主观数据缺失" where missing; the injury line has priority; entries whose `state` is
   `no_data`/`error` must be flagged as such — **never substitute a 0 or an estimate**. ⚠ Inside
   that file, **sleep / HRV / training status do not take part in judging the light**
   (docs/06 §3); only **resting HR** is judged, by the existing +8 bpm rule.
5. **Also compute "strength-session density" (informational, judges nothing)**: for master-CSV
   rows with activity type `力量训练`, take **`moving time ÷ total time`**, list each session and
   the weekly mean, and put it in the review. How to read it is in the last bullet of docs/06 §3:
   low density means a high share of rest between sets — less actual stimulus per hour, but also
   **less interference with running recovery** (20–40% with an average HR clearly below the E band
   is what a *supplementary* strength session should look like). ⚠ **Bouldering does not apply**
   (Garmin produces no moving time for it; always 0). ⚠ **Loads and reps per set do not exist in
   Garmin data at all**, so load can only be judged if I write it down — **never infer "add more
   load" from density**.
6. Write the review: append a four-section entry (docs/06) to <WEEKLY_REVIEW> and update
   the gate-progress table; the light judgement cites the exact generic-safety rule.
7. Judge the light and adjust the plan if needed: on yellow/red or a gate result, edit
   <PLAN_HTML> (week tables, plan-vs-actual `canvas id=trk` actual array), append a vN row
   to the version table and bump; on a race result sync the runner profile & VDOT.
8. Reply in ≤400 characters: last week's volume/completion, risk colour, next-week
   changes, and one thing for me to watch (include any newly detected sensor / data break).
```
