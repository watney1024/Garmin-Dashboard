# 提示词 · 排课到 Garmin `schedule_to_watch`

> 作用：把本周的跑步课表生成到 Garmin（手表日历显示当天课）。整段发给 AI，替换 `<...>`。

```
[排课] 请把本周（从今天起的那一周，W__）可推到 Garmin 的跑步课排到我的手表：
1. 读 <PLAN_HTML> 该周课表与跑者档案 <RUNNER_PROFILE.yaml>，识别本包允许的课型（如 E/恢复/LSD/长距离；教练包与档案排除的课型一律不排）。
2. **先分流课型**：
   - **连续跑课**（E/恢复/LSD/长距离）→ 走第 4 步的周课表路径；
   - **操场/间歇课**（含组数、每组距离、单圈目标，如跑团课 6×1.2k）→ **必须**走
     `scripts/garmin_track_workout.py` ＋ 先加载 `.agents/skills/track-workout/` 的 SKILL.md
     （`endCondition = lap.button`：每次按键记标称 400 m，与跑道实际圈长解耦）。
     组间**站着不动**写 `"rest"`、**慢跑**写 `"recovery"`，**默认 `rest`**——写错手表会在休息段催我跑起来。
     热身步骤**不设心率靶**（`warmup.hr_min/hr_max` 已废弃，写了只打 WARNING）。
     **不许**用 `create_run_workout` 去"近似"间歇课：它只能建连续跑课，会丢掉全部结构。
3. 连续跑课按训练口径（docs/05 §3）生成：E/恢复 = 时间 + 心率上限；课名带日期和课名（如 W1 Tue E5）。
4. **一律先 `--dry-run`**，看清逐课判定（`create` / `reuse` / `replace` ＋原因）再真跑。两个脚本都按
   **课名 ＋ 内容指纹**幂等：处方改了**直接重跑就行**，脚本会自动走"建新课 → 排新课 → 删旧课"
   （先建后删，中途失败不会把手表弄空）。**不要再手工换课名去规避复用**（那是旧版本的坑），
   也别以为"名字没变"改动就到不了手表。用 garmin_mcp 的 create_run_workout + schedule_workout
   创建并排到对应日期（或直接跑 `scripts/garmin_schedule.py <week_spec>`）。
5. **标题治理**：把本周已跑完的活动标题用 `set_activity_name` 改成有意义的课名（Garmin 默认标题如
   "XX区 跑步"是垃圾信息）。
6. 排完告诉我：排了哪几趟、日期和课名；提醒我同步手表。若本周有非 A 赛，说明它在 Garmin 里按什么课呈现。
```
