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
4. Fill the 6 subjective metrics: resting HR / weight / sleep / RPE / injury 4 sites /
   deviation reason into <TRAINING_LOG> for the matching W section; write "主观数据缺失"
   where missing; the injury line has priority.
5. Write the review: append a four-section entry (docs/06) to <WEEKLY_REVIEW> and update
   the gate-progress table; the light judgement cites the exact generic-safety rule.
6. Judge the light and adjust the plan if needed: on yellow/red or a gate result, edit
   <PLAN_HTML> (week tables, plan-vs-actual `canvas id=trk` actual array), append a vN row
   to the version table and bump; on a race result sync the runner profile & VDOT.
7. Reply in ≤400 characters: last week's volume/completion, risk colour, next-week
   changes, and one thing for me to watch (include any newly detected sensor / data break).
```
