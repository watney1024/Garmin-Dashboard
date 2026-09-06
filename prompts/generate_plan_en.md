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
   E/M/T/I/R paces into plan chapter 3.
4. Count the cycle backwards from the A race; build the weekly skeleton and week-by-week
   schedule (base → build → peak → taper), obeying the coach and the generic safety layer
   (docs/03/05/06): non-A races fold into that week per their role; exactly one all-out A.
5. Land the gates and red lines on concrete dates, including the veto "if the peak long
   run fails, race-day starts conservative".
6. Produce a self-contained HTML (chapter/naming per examples/plan.example.html); the
   version table gets v1 with its basis.
7. In your output list the self-check: profile-consistent, no invented paces, one A,
   volume within caps, version recorded.
8. Reply in ≤400 characters: A race & goal, VDOT, weekly skeleton, peak week volume,
   1-2 things for me to watch.
```
