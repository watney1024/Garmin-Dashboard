# Prompt · Generate a plan `generate_plan`

> Purpose: profile + chosen coach package + VDOT → generate/regenerate an HTML training
> plan. Send the whole block to the agent (replace `<...>` with actual paths).

```
[generate_plan] Today is <month/day>. Please generate/regenerate a training plan
(HTML dashboard) for the runner:

1. Read the runner profile <RUNNER_PROFILE.yaml>; confirm the A race, non-A races and
   roles, available days / runs per week / long-run day / quality days, and PRs
   (schema: docs/08).
2. Confirm **which extra sensors the runner has** (HR strap / running-dynamics pod /
   power meter) — that decides which advanced metrics are available (GCT balance,
   respiration rate, ground contact time, vertical oscillation, power). **Work it out from
   the Garmin data first** (HR-strap-only: GCT balance, respiration rate, stance-time
   percentage; the FIT file also gains a paired `source_type=antplus` device) and **ask me
   directly when you can't**. Record the result in the profile and let it decide which
   metrics the plan tracks — **if a sensor isn't there, don't reference its metrics**.
   If the runner **owns an accessory but the history mixes "with" and "without"**: the HR
   zones in chapter 7 must be built on **strap** data; if HRmax / lactate threshold come from
   strap-less data, mark them **pending re-check** and state in the plan that a strap-based
   calibration is needed — don't treat them as settled anchors. (**Watch-only** runners are
   unaffected: one source throughout, a constant bias, so trends still hold.)
3. Load the chosen coach skill: read .agents/skills/coach-<profile.coach>/SKILL.md, then
   the full method references/coach-<coach>_<lang>.md (lang = profile language) and obey
   it; if the profile doesn't fit, explain and propose a switch, continue only after I confirm.
4. Derive the current VDOT from the profile PRs (docs/09 / scripts/vdot.py) and write the
   E/M/T/I/R paces into plan chapter 7 "paces & HR zones".
5. Count the cycle backwards from the A race; build the weekly skeleton and week-by-week
   schedule (base → build → peak → taper), obeying the coach and the generic safety layer
   (docs/03/05/06): non-A races fold into that week per their role; exactly one all-out A.
6. **The week-by-week schedule must be a calendar**: grouped by phase, one row per week,
   with fixed columns "week | Mon…Sun (all 7 days) | total" — list **all seven days,
   rest days included as "休息"/rest**; never show only the days that have a session. Each
   cell starts with the date (e.g. `8/4`) followed by that day's content; strength days name
   the body part and phase (build/convert/taper); races and gates get a tag. The total column
   counts running distance only (strength and rest excluded).
7. Land the gates and red lines on concrete dates, including the veto "if the peak long
   run fails, race-day starts conservative".
8. **Add a "milestones" table inside chapter 4 (cycle structure)** (docs/05 §2 step 8, §4):
   milestones are **achievements**, unlike gates (**decision points**) — missing one is
   **recorded only and never changes the plan on its own**. Each needs a target week/date
   plus a criterion **verifiable from the data** (no "feels stronger"); **dense early,
   sparse late** (the lower the starting mileage, the denser); a low-mileage runner needs
   **consistency/health** milestones (e.g. "3 straight weeks ≥90% completion"), not an
   all-results list.
9. Produce a self-contained HTML (10 chapters, chapter/naming per examples/plan.example.html;
   no external references, charts drawn on plain canvas). **Charts must show the per-week
   values on mouse hover** (a self-contained `.ctip` tooltip, no external library, hidden when
   not hovering). Chapter 10 carries the "this file is the constitution" sentence and the
   known-deviations table; the version table gets v1 with its basis.
10. In your output list the self-check: profile-consistent, no invented paces, one A,
   volume within caps, all seven days present in the weekly table, the volume array matching
   the total column, **charts readable on hover**, **the milestone table present (every entry
   data-verifiable and kept separate from gates)**, version recorded.
11. Reply in ≤400 characters: A race & goal, VDOT, weekly skeleton, peak week volume,
    sensor findings, 1-2 things for me to watch.
```
