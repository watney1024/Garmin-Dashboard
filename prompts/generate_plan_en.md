# Prompt · Generate a plan `generate_plan`

> Purpose: profile + chosen coach package + VDOT → generate/regenerate an HTML training
> plan. Send the whole block to the agent (replace `<...>` with actual paths).

```
[generate_plan] Today is <month/day>. Please generate/regenerate a training plan
(HTML dashboard) for the runner:

1. Read the runner profile <RUNNER_PROFILE.yaml>; confirm the A race, non-A races and
   roles, available days / runs per week / long-run day / quality days, and PRs
   (schema: docs/08).
2. Load the chosen coach skill: read .agents/skills/coach-<profile.coach>/SKILL.md, then
   the full method references/coach-<coach>_<lang>.md (lang = profile language) and obey
   it; if the profile doesn't fit, explain and propose a switch, continue only after I confirm.
3. Derive the current VDOT from the profile PRs (docs/09 / scripts/vdot.py) and write the
   E/M/T/I/R paces into plan chapter 7 "paces & HR zones".
4. Count the cycle backwards from the A race; build the weekly skeleton and week-by-week
   schedule (base → build → peak → taper), obeying the coach and the generic safety layer
   (docs/03/05/06): non-A races fold into that week per their role; exactly one all-out A.
5. **The week-by-week schedule must be a calendar**: grouped by phase, one row per week,
   with fixed columns "week | Mon…Sun (all 7 days) | total" — list **all seven days,
   rest days included as "休息"/rest**; never show only the days that have a session. Each
   cell starts with the date (e.g. `8/4`) followed by that day's content; strength days name
   the body part and phase (build/convert/taper); races and gates get a tag. The total column
   counts running distance only (strength and rest excluded).
6. Land the gates and red lines on concrete dates, including the veto "if the peak long
   run fails, race-day starts conservative".
7. Produce a self-contained HTML (10 chapters, chapter/naming per examples/plan.example.html;
   no external references, charts drawn on plain canvas). **Charts must show the per-week
   values on mouse hover** (a self-contained `.ctip` tooltip, no external library, hidden when
   not hovering). Chapter 10 carries the "this file is the constitution" sentence and the
   known-deviations table; the version table gets v1 with its basis.
8. In your output list the self-check: profile-consistent, no invented paces, one A,
   volume within caps, all seven days present in the weekly table, the volume array matching
   the total column, **charts readable on hover**, version recorded.
9. Reply in ≤400 characters: A race & goal, VDOT, weekly skeleton, peak week volume,
   1-2 things for me to watch.
```
