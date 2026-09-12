# Prompt · This week's schedule `current_week_schedule`

> Purpose: quickly know what this (or some) week contains. Send the whole block, replace
> `<...>`.

```
[current_week_schedule] Today is <month/day>. Please locate this week's schedule in
<PLAN_HTML> (mark it as W__) and output:
- A Monday–Sunday 7-day list (**rest and full-rest days included**, marked "rest"):
  date(weekday) · session · pace/sets/distance target · estimated time;
- The key sessions this week (quality / long run; if a non-A race falls this week, state
  its role and how to run it);
- Planned weekly volume vs last week's actual (compute if data exists, otherwise say so);
- End with one reminder: over the weekend or on Monday, report your body in one sentence
  (template in docs/03/07).
```
