# 提示词 · 收集跑者档案 `collect_profile`

> 作用：首次接触一个跑者时，用**一轮结构化访谈**把 `runner_profile.yaml` 建起来（schema 见 docs/08）。
> 前置：还没有档案，或档案缺字段。整段发给 AI 即可（把 `<...>` 换成实际路径）。

```
[收集档案] 请访谈我，把 runner profile 建起来（目标路径 <workspace/runner_profile.yaml>）。

1. **先拿题序**：跑 `python scripts/profile_wizard.py --questions --lang zh` —— 这是唯一权威的题表
   （由 `scripts/profile_wizard.py` 的 `FIELDS` 派生）。**别自己另列一份题表**，会跟 schema 漂移。
2. **按题表顺序、分组来问**：identity → races → weekly → pr → coach → strength → constraints →
   metric_baselines → devices。问法用题表的「问」，「说明」用来解释为什么问，「示例」只在我卡住时给。
   **不要一次把 29 道题甩给我**——一组问完、我答完，再进下一组。
3. **能自己查的先查**：有 MCP 工具时，静息心率基线 / 体重 / 睡眠基线 / 已有 VO2max 先去 Garmin 读
   （`scripts/garmin_wellness.py`、`get_user_profile`），**读到就把数报给我确认**，别让我凭记忆答；
   查不到才问。缺的写「待补」，**不要替我编数值**。
4. **必填与互斥**：一个周期内**只能有一场 `role: A`**；每场比赛都必须标 role（`A` / `attempt` /
   `training`，三者互斥）。PR 四项**至少填一项**——那是 VDOT 的唯一来源（docs/09）。
5. **配件要问到底**：戴不戴心率带 / 跑步豆 / 功率计、**从哪天起出现**（`since` 就是数据断点，
   docs/02 §6.10）、哪几次漏戴。没有配件就整块留空。
6. **写成档案**：按 docs/08 的 schema 写到 <workspace/runner_profile.yaml>。**只用块状 YAML**——
   不要 flow map（`{...}`）、不要块标量（`|` / `>`）、不要 tab 缩进。
   这些写法 `profile_wizard.py` 会直接拒绝，不是风格洁癖——是解析器只认这个子集。
7. **自检**：跑 `python scripts/profile_wizard.py --check <workspace/runner_profile.yaml>`，
   **必须 0 error**（warning 允许，但要逐条告诉我是什么意思、要不要改）。有 error 就改到过为止。
8. 回复 ≤400 字：档案里我最该确认的 1-2 件事、还缺哪些字段（「待补」清单）、以及下一步能不能生成计划。
```

备选入口（跑者自己动手时）：`examples/runner_profile.questionnaire.yaml` 是同一套字段的**空白问卷**，
跑者填完再让 agent 跑第 7 步的 `--check`；交互式向导 `python scripts/profile_wizard.py` 也能逐题问、
并会**原样保留**档案里 schema 之外的扩展块（如实测锚点 `measured:`）。
