# 06 · Weekly review: the loop & the lights (for AI agents)

The review is what keeps a plan alive: **after each completed week, turn objective data +
the runner's one sentence into (a) a record, (b) a judgement, (c) next-week
adjustments.** Default cadence: every Monday covering the previous Mon–Sun week; the
runner may trigger it any time.

Inputs: the rebuilt `Activities.csv` + `inbox/activity_<id>.csv` (new downloads) + the
runner's one sentence + `runner_profile.yaml` + the plan HTML.

## 1. Review steps (fixed order)

1. Refresh objective data (pull via MCP when available, docs/01; otherwise state the
   data-cutoff date).
2. Match this week's activities (by activity ID), compute weekly volume / completion;
   download any missing detail CSVs.
3. Fill the six subjective metrics into the training log for the matching W section
   (docs/03 §2; missing → "主观数据缺失", injury line first).
4. Write the four-section review (§2 below) appended to the rolling weekly-review doc.
5. Judge the light (§3) and adjust the plan if needed (§5).
6. Update the gate-progress table (§4).
7. Reply to the runner in ≤400 characters: last week's volume/completion, risk colour,
   what changed next week, one thing for the runner to watch.

## 2. Four-section review template (copy each week)

```
① Last week actual vs plan — session by session: done / not done / what changed (cite the
   deviation reason)
② Three trends — weekly volume · long-run completion · E-run HR drift at same pace
③ Risk judgement — green / yellow / red + the specific rule triggered
④ Next-week adjustments — which sessions changed and why
```

- **E-run HR drift** = HR trend at the same pace: rising means insufficient recovery /
  fading form; falling means good adaptation.
- Non-A / test-race weeks: treat "how the race was run" as that week's long-run session in
  the comparison (training = not all-out, attempt = committed, A = all-out) and record the
  result.

## 3. Judging the light (generic safety layer, decided up front)

| level | trigger (any) | auto action |
|---|---|---|
| 🟡 Yellow | resting HR > baseline **+8 bpm** for 2 consecutive days; any site injury **3–4**; weekly volume done **<80%**; two consecutive weeks RPE≥8 | drop the week's easy/recovery run; long run **-20%**; no quality segments that week |
| 🔴 Red | any site injury **≥5**; **unilateral** pain (the key one); two consecutive weeks done **<70%** | **stop 3 days**; lower the target band; keep strength (halve lower body); after recovery restart from the current week — **never make up missed volume** |

- Bilateral soreness = fatigue, you may run; **unilateral pain = structural, the runner does
  not self-judge it** (docs/03 §3).
- Coach red lines may only tighten; always **cite the rule** (e.g. `Yellow: left achilles 3`).
- On conflict with the plan's chapter 10 / coach gates: take the stricter option that
  respects the safety layer.

## 4. Gate-progress table

The gates defined in the plan's chapter 7 land on concrete dates; fill them in during the
review:

| gate | date/week | content | threshold | actual | verdict |
|---|---|---|---|---|---|
| 1 | ... | structural tolerance (no abnormal soreness/HR after the double-hard week) | see plan | — | pending |
| 2 | ... | test-race → target (10K/half) | see plan | — | pending |
| 3 | ... | peak long run (~30 km) meets target | see plan | — | pending |

**Gate 3 (peak long run) = one-vote veto**: however fast the test race was, an unmet peak
long run means a conservative race-day start. If the A race has no matching test, the
coach package/profile generate an equivalent gate.

## 5. Plan-change mechanics (after yellow/red or a gate result)

1. Edit the relevant rows of the plan HTML's week-by-week schedule (this/later weeks).
2. Update the `canvas id="trk"` actual-value array (actual weekly volume as weeks pass).
3. Append a `vN` row to the version table: what changed + why; increment, never skip.
4. If a race result updates a PR → sync `runner_profile.yaml` and recompute VDOT
   (docs/08/09).

## 6. Non-A races & post-race weeks

- **Week before a race**: taper per the plan (coach rules); treat the race as that week's
  "long-run session".
- **After a race**:
  - A race: cut volume ~50–60% for one week, record the result → decide next cycle/rest.
  - attempt race that beat a PR: update the PR per docs/08 §2; log results even when no PR.
  - training race: it was a completed quality session; proceed normally.
- **Missed volume**: active cutback (travel/illness, then cut) → return to normal, do not
  make up; passive drops two weeks running → act per the yellow light.

## 7. Boundaries of the lights

- Trigger ⇒ act, **even if the week is already light** — but an already-planned recovery
  week proceeds as planned (it already satisfies the yellow actions).
- Stricter coach gates/red lines win.
- The light table may be **pre-tightened per individual** in the profile's `constraints`
  (e.g. an old injury site triggers earlier), but the defaults can never be loosened.
