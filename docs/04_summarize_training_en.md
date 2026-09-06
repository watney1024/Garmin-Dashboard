# 04 · Summarising past training (for AI agents)

Before generating/updating a plan or writing a weekly review, build a **reliable summary
of the past**. Goal: use objective data to answer "where is this runner now, what worked /
went wrong in the last block".

## 1. Data prep (make sure the master is fresh first)

1. With MCP tools: paginate `get_activities` (start/limit=100, stop when <100 or empty,
   ~0.3 s between pages) → rebuild `Activities.csv` (canonical 16-column format).
2. For new activities: `download_activity_file` by ID into `inbox/activity_<id>.csv`
   (the script handles this, see docs/01).
3. Without tools: read existing files and state the data-cutoff date in the conclusion.

## 2. Computing objective metrics (methods)

- **Weekly volume**: sum `距离km` from the master (running types only). Unit guard: rows
  >100 are in metres → divide by 1000.
- **Intensity uses moving pace**: the master's "平均配速" is already moving-time based;
   when using lap detail still exclude rest laps (docs/02 §6).
- **E-run HR drift**: pick E sessions of the same kind/distance/temperature and compare the
  average HR trend week to week.
- **Long-run completion**: actual distance/pace vs the plan's long-run target.

## 3. Classification & comparability (key discipline)

- **Continuous vs interval runs must be separated**: whole-run averages only compare
  within the same kind.
- Interval rest laps pollute — use moving pace / split data to judge "completion quality".
- Equal-conditions rule: only **same distance + same temperature + similar average HR**
  continuous runs are comparable.
- "Continuous run" test: average pace within ~100 s/km of the fastest pace AND distance
  ≥4 km.
- Don't conclude from tiny samples: one or two sessions prove nothing; use ≥3-week windows.

## 4. Outputs (as needed)

| scenario | output |
|---|---|
| before plan generation | last 8–12 weeks: weekly volume, session-type mix, intensity trend, long-run/recovery execution, strength frequency; then set VDOT & starting volume |
| weekly review | see the four sections in docs/06 (three trends) |
| coach / A-race switch | an ability profile (speed end vs endurance end) justifying the choice/adjustment |

## 5. Historical-data pitfalls (self-check before concluding)

- Averaging interval sessions into "pace/cadence" stats → wrong.
- Attributing a low recovery week simply to holidays → cross-check the deviation reason and
  the injury log first.
- Projecting stale results into a new cycle → state the date; >6 months doesn't count
  (docs/09).
- Ignoring how strength supports volume tolerance → include strength frequency in the
  profile.

## 6. Known-mistake list (fix on sight)

1. Metres vs km unit confusion.
2. Average HR inflated by short surges, misread as "too intense".
3. Using an aspirational VDOT to decide "how fast I should run".
4. Concluding "undertrained" without separating active cutback from passive drop.
