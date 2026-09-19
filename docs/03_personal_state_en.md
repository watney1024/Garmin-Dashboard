# 03 · Personal state: subjective data & safety baseline (for AI agents)

Training-state judgement = **objective data (Garmin, docs/02) + subjective feedback
(the runner's one sentence) + a fixed set of decision rules**. The subjective layer exists
to catch early signals the objective data misses: resting HR, sleep, injury sensation,
fatigue. **The injury line has top priority.**

## 1. The runner's only weekly job: one sentence

> Template: `date(day-direction) + weekday + session name + completion + what tired first
> + reason for deviation`
> Example: `8/10 Tue E5, done. Lungs tired first, legs fine.`

- **What tired first** is the key subjective signal: `legs first` = peripheral fatigue
  (muscles/tendons); `lungs first` = central/cardio fatigue. Different responses.
- **Reason for deviation** lets the agent tell «**active cutback**» (fine, adjust as
  planned) from «**passive drop**» (work/illness/injury — watch, re-check next week).
- Injury signals can be reported **any time on their own** (four sites, 0–10; unilateral
  ≥5 must be said immediately, never wait for Monday).

## 2. The six subjective metrics (one weekly block in the training log, filled by the agent)

Exact format, copy verbatim:

```
## W__  __/__ – __/__
- resting HR weekly avg: __ bpm
- weight weekly avg: __ kg
- sleep weekly avg: __ h
- overall fatigue RPE: __ /10
- injury signals 0–10 (0=none): shin front __ / achilles __ / knee __ / plantar __
- volume deviation reason:
- notes:
```

### Field anchors (decision criteria, fixed)

| Field | How to measure / read | Trigger |
|---|---|---|
| Resting HR | watch reading **before getting out of bed** (daily); record weekly avg | **+8 bpm above the runner's baseline**: **1 day ⇒ 🟡 yellow** (watch + the yellow actions); **2 consecutive days ⇒ 🔴 red, but the action is only "rest that day"** (**do not** apply red's default "stop running 3 days"), and it also triggers the yellow-light weekly adjustment (docs/06) |
| Weight | morning, fasted, weekly avg | not a hard rule; large unexplained swing (>±2 kg) prompts a check (oedema/dehydration/appetite) |
| Sleep | weekly avg hours | <5 h repeatedly or clearly below personal norm ⇒ cut the week's quality-session load |
| RPE | whole-week fatigue, 1=very easy 10=exhausted | **two consecutive weeks ≥8** ⇒ agent proactively cuts volume |
| Injury signals | four sites scored separately: `0` none · `3` felt but doesn't affect running · `5` affects form / forces slowing · `7+` stop | any site **3–4** ⇒ yellow; any site **≥5** ⇒ red; **unilateral and ≥5** ⇒ red, act immediately, no debate |
| Volume deviation reason | one line | distinguishes active cutback vs passive drop |
| Notes | free | race results, special situations |

**The four sites: shin front (tibia) / achilles / knee / plantar.** Untested sites are
written `_`; a fully missing block is written "主观数据缺失" (subjective data missing).

## 3. Why "unilateral" matters

Bilateral symmetric soreness is fatigue — rest fixes it; **unilateral pain is structural** —
tibial stress reactions, Achilles tendinopathy and IT-band syndrome all start one-sided.
The runner does not self-judge this: when the agent sees unilateral ≥5 it acts as red.

## 4. Default safety baseline (yellow/red, decided up front so nobody argues weekly)

A training plan should carry a table like this one (concrete actions in docs/06; coach
packages may only tighten it, never relax it):

| Level | Trigger (any) | Auto action |
|---|---|---|
| 🟡 Yellow | resting HR **+8 bpm above baseline for 1 day**; any site injury **3–4**; weekly volume done **<80%**; two consecutive weeks RPE≥8 | drop the week's easy/recovery run; long run **-20%**; no quality segments that week |
| 🔴 Red | **resting HR +8 bpm above baseline for 2 consecutive days**; any site injury **≥5**; **unilateral** pain (the key one); two consecutive weeks done **<70%** | injury/completion triggers: **stop running 3 days**; **resting-HR trigger: rest that day only** (**do not** apply "stop running 3 days"); lower the target band; keep strength (halve the lower-body part); after recovery restart from the current week — **never make up missed volume** |

**The resting-HR +8 bpm rule has two tiers** (the only "red but not a stop-running" rule):
**1 day = 🟡**, **2 consecutive days = 🔴 with the action "rest that day"** — never carry over
red's default "stop running 3 days".

**Always cite the exact triggered rule**, e.g.: `Red: left achilles injury 5, unilateral`.

## 5. Missing data

- A metric not reported → write "subjective data missing"; **never fabricate or guess**.
- Computations that only need objective data (volume done, E-run HR drift) proceed normally.
- When the injury line is missing and unverifiable, err on the conservative side.

## 6. When the agent proactively asks the runner

- Objective data looks abnormal but no subjective report came in (volume crash/spike, HR
  trend anomaly).
- After a non-A race / test (to record the result into the profile's PRs → update VDOT).
- A yellow light fired but the runner's sentence had no deviation reason.
