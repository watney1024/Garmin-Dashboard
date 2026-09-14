# Track interval sessions: rationale and doctrine (`track-workout` skill reference)

> This is a **capability** document, not a training methodology. Methodology comes from the
> coach package selected in the runner profile. Builder script:
> `scripts/garmin_track_workout.py`; data format: `docs/02` §3b.

## 1. Why an ordinary run workout will not do

Ordinary run workouts measure by **GPS / time**. A real track lap is **not exactly 400 m** —
commonly 390–420 m, and the measured length varies by lane. So:

- a "2 laps = 800 m" step accumulates error every lap;
- the watch's **pace** is therefore systematically wrong (one of the docs/02 §6 pitfalls);
- a jogging rest gets mixed into distance and pace statistics.

Garmin's answer is the **lap button**: set a step's end condition to `lap.button`, and
**each press records a nominal distance**.

```
{ "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
  "endCondition": {"conditionTypeId": 1, "conditionTypeKey": "lap.button"},
  "endConditionValue": 1000.0 }
```

`endConditionValue` carries no meaning for `lap.button` (Garmin stores 1000); the distance is
whatever the press count says.

## 2. The only thing the runner has to remember on the watch

> **Press the lap key once per 400 m, and once more when the rest ends.**

So 5 warm-up presses = 2 km; 3 presses per set = 1.2 km; one press = a nominal 400 m.
The real lap length never enters the arithmetic.

## 3. Step types and end conditions (DTO mapping)

The ids come from `workout://reference/structure` (an MCP resource). Do not guess them:

| stepTypeId | key | use |
|---|---|---|
| 1 | `warmup` | warm-up |
| 2 | `cooldown` | cool-down |
| 3 | `interval` | main / repetition step |
| 4 | `recovery` | **active** recovery (slow jog) |
| 5 | `rest` | **complete rest** (standing still) |
| 6 | `repeat` | repeat group (`RepeatGroupDTO`) |

| conditionTypeId | key | use |
|---|---|---|
| 1 | `lap.button` | **press the lap key** (the whole point here) |
| 2 | `time` | seconds |
| 7 | `iterations` | repeat count (required on `RepeatGroupDTO`) |

A `RepeatGroupDTO` needs **both** `numberOfIterations` and
`endCondition{7, iterations}` — omitting `conditionTypeId` makes Garmin silently corrupt the
repeat count.

## 4. Rest style: the easiest thing to get wrong

| Reality | Use | Note |
|---|---|---|
| standing still, a few steps, stretching | `rest` (5) | **the default**; most interval sessions are this |
| slow jog to bring HR down | `recovery` (4) | only when the runner explicitly says "jog between reps" |

Getting it backwards means the watch nags you to run during the rest — or makes you stand
still when you should be jogging.

**Also ask separately about the rest *after the warm-up* versus *between sets*** — they are
often different values (e.g. 6 min after warm-up, 3 min between sets).

## 5. Parsing past track sessions (analysis doctrine)

Work from the activity detail, **never from the whole-session average**:

1. **A segment = one lap press**, ≈ one nominal 400 m. Historic data may show 0.41 km
   (a GPS reading) — **ignore that number**; only the segment time matters.
2. **Spot rest segments**: distance collapses to 0.02–0.15 km **and** moving time is far
   below elapsed time (essentially standing). If the rest is a jog the distance is visibly
   larger — which is also how you can tell `rest` from `recovery` after the fact.
3. **Group them**: 1.2 km per set = 3 consecutive segments; 800 m per set = 2.
4. **Judge by segment time** against the nominal distance (e.g. 1:52–2:02 per 400 m).
   **Never convert GPS distance to pace.**
5. **Read HR within the repetition segments only** — rest-segment HR is not part of the verdict.

## 6. Replacing and idempotency

- The script is idempotent by **workout name**: re-running the same name only re-schedules.
- **Changed the prescription? Change the name** (e.g. `6×1.2k` → `5×1.2k`). The same name does
  not overwrite — `upload_workout` always creates a new workout, and the old one just clutters
  the library.
- Clean-up order: schedule the new one first, then `delete_workout` the old one. **A deleted
  workout's calendar entry disappears with it**, so there is no need to call
  `unschedule_workout` (which, confusingly, wants `scheduled_workout_id`, not `workout_id`).
- Read back with `get_workouts` / `get_workout_by_id` / `get_scheduled_workouts` — **always
  verify after creating**, to confirm Garmin did not rewrite `lap.button` or the rest style.
