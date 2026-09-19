---
name: track-workout
description: >-
  操场（跑道）间歇课的建课能力：把跑者给的"人话处方"（组数、每组距离、单圈目标、组间休息方式）
  转成 Garmin 结构化课并排到日历。核心机制是**计圈键**（step endCondition = lap.button）——
  每次按键记一个标称 400 m，**与跑道实际圈长解耦**。当跑者给出操场/间歇课处方、要求把间歇课
  排进手表、或需要解析历史操场课的分段时加载本技能。
  Capability skill for building a track interval session on Garmin where the watch distance is
  decoupled from the lap button. Load when a runner gives a track/interval prescription, asks to
  put an interval session on the watch, or when parsing past track sessions.
---

# track-workout（操场间歇课）

> **这是"能力技能"，不是"教练理念包"。** 它不通过 `runner_profile.coach` 选择，
> 也不提供训练方法论；它只解决一件事：**怎么把间歇课正确地建到 Garmin 上**。
> 教练方法论的选包规则见 `.agents/skills/README.md`。

## 执行步骤

1. **拿到跑者的处方**。需要五项：**组数**、**每组距离或圈数**、**单圈目标**（时间或配速）、
   **组间休息的时长与方式**、**热身/冷身的量**。缺哪项就问，不要猜——尤其"休息是静止还是慢跑"。

2. **判断 `rest_style`**（本技能最容易错的一步）：
   - 组间**站着不动** → `"rest"`（Garmin `stepTypeId 5`，完全休息）
   - 组间**慢跑** → `"recovery"`（`stepTypeId 4`，活动恢复）
   - **默认 `rest`**。写错会让手表在休息段催你跑起来。跑者说"组间慢跑"才用 `recovery`。

3. **写成 track spec JSON**（schema 见 `docs/02` §3b，示例 `scripts/track_spec.example.json`）。

4. **先 dry-run 预览，再执行**：
   ```bash
   python scripts/garmin_track_workout.py <spec.json> --dry-run     # 预览
   python scripts/garmin_track_workout.py <spec.json> --print-json  # 看生成的 DTO
   python scripts/garmin_track_workout.py <spec.json>               # 上传并排期
   ```
   脚本按 **课名 ＋ 内容指纹** 做幂等（registry 在 `GARMIN_DATA_DIR/garmin_workout_registry.json`）。
   `--dry-run` 会逐课打印判定：`create` / `reuse` / `replace` ＋原因，**先看差异再推**。

5. **替换旧课由脚本自动处理**：改了处方（组数 / 休息方式 / 热身…）直接重跑即可 ——
   脚本比对内容指纹发现不一致，自动走 **建新课 → 排新课 → 删旧课**
   （先建后删，中途失败也不会把手表弄空；旧课被删后其日历条目自动消失，不必手动
   `unschedule`）。**不要再靠手工换课名去规避复用** —— 那正是旧版本的坑。

6. **复盘按计圈口径**：一段 = 一次按键；**只比段内时间，不做 GPS 距离→配速换算**
   （见 `references/track-workout_zh.md` 的解析规则）。

## 不许做

- 不许在没有 dry-run 的情况下直接上传。
- 不许把 `rest_style` 留空却假定是慢跑——**静止是默认，慢跑必须显式说明**。
- 不许用 `create_run_workout` 去"近似"间歇课（它只能建连续跑课，会丢掉所有结构）。
- 不许在复盘里用整场平均配速评价间歇课（休息段会严重污染均值）。
- **不许给热身步骤设心率靶**：`warmup.hr_min/hr_max` 已废弃，写了也只会被忽略并打
  WARNING。热身期心率从静息往上爬，挂区间只会全程报下限（docs/02 §3b）。
