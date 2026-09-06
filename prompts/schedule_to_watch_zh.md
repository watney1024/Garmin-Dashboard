# 提示词 · 排课到 Garmin `schedule_to_watch`

> 作用：把本周的跑步课表生成到 Garmin（手表日历显示当天课）。整段发给 AI，替换 `<...>`。

```
[排课] 请把本周（从今天起的那一周，W__）可推到 Garmin 的跑步课排到我的手表：
1. 读 <PLAN_HTML> 该周课表与跑者档案 <RUNNER_PROFILE.yaml>，识别本包允许的课型（如 E/恢复/LSD/长距离；教练包与档案排除的课型一律不排）。
2. 按训练口径（docs/05 §3）生成：E/恢复 = 时间 + 心率上限；课名带日期和课名（如 W1 Tue E5）。
3. 用 garmin_mcp 的 create_run_workout + schedule_workout 创建并排到对应日期（或直接跑 scripts/garmin_schedule.py <week_spec>），保持幂等（registry 复用）。
4. 排完告诉我：排了哪几趟、日期和课名；提醒我同步手表。若本周有非 A 赛，说明它在 Garmin 里按什么课呈现。
```
