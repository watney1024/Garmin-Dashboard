# 提示词 · 每周更新 `weekly_update`

> 作用：复盘过去一周（周一至周日）+ 把结果写回训练日志/周报复盘/计划。默认每周一执行；
> 也可手动发。把 `<...>` 换成实际路径。

```
[每周更新] 今天是 <月/日>。请完成上一训练周（周一到周日）的记录更新与计划调整：

1. 刷新客观数据：若已加载 garmin_mcp 工具，用 get_activities 分页拉全量重建 <DATA_DIR>/Activities.csv（保持 16 列规范与倒序，见 docs/02）；对上周新增活动用 download_activity_file(activity_id, format="csv") 补下载到 <DATA_DIR>/inbox/activity_<id>.csv。工具不可用就只读现有文件并在结论里注明数据截止日期，绝不要让我手动导出。
2. 读跑者档案 <RUNNER_PROFILE.yaml> 与计划 <PLAN_HTML>，确认当前 A 赛/所在周（W__）。
3. 填主观 6 项：把上周晨起静息心率/体重/睡眠/RPE/伤病四部位/偏差原因填进 <TRAINING_LOG> 对应 W 节；缺就写"主观数据缺失"，伤病信号行优先。
4. 出复盘：按 docs/06 四段式把一节追加到 <WEEKLY_REVIEW>，并更新顶部闸门进度表；判断按通用安全层引用具体规则。
5. 判灯并按需改计划：黄/红触发或闸门结果需调整时，改 <PLAN_HTML> 逐周课表、计划 vs 实际（canvas id=trk 的实际值数组），版本记录追加 vN 行并递增；比赛成绩更新则同步 runner_profile 与 VDOT。
6. 回复 ≤400 字：上周跑量/完成度、风险颜色、下周改了什么、需要我注意的一件事。
```
