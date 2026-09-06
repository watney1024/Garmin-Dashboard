# coaches/ — 教练理念文档包

> 生成计划前，agent 必须**整包加载**所选教练的 `README` 并照它执行。
> Before generating a plan, an agent MUST load the chosen coach's `README` in full and obey it.

## 目录

| id | 理念 | 一句话 | 适合 |
|---|---|---|---|
| `daniels_vdot` | 丹尼尔斯 VDOT | 单分数定全分区配速，周期围绕 VDOT 进步与测试赛 | 目标距离明确、能用 5K/10K 成绩校准的跑者（示例计划即用它） |
| `polarized_80_20` | 80/20 极化 | 约 80% 时间低强度 + 20% 高强度 | 以量取胜、易伤或高跑量的业余跑者 |
| `hanson` | 汉森 | 连续奔跑 + 疲劳累积，周中质量跑 + 周末中长距离 | 讨厌"单次超长"、用总累积量练耐力的马拉松跑者 |
| `advanced_marathoning` | 高级马拉松（Pfitzinger & Douglas，《你可以跑得更快》） | 长周期高跑量、周日长距离含马配段 + 周中 Tempo/间歇 | 有一定基础、准备系统备赛马拉松的跑者 |

**以上包内容均为本仓库撰写的"概括 + 应用指南"，非原书复制（见 NOTICE.md）。**

## 何时选哪个 / which when?

1. 读 `docs/08_runner_profile_zh.md` 与跑者档案 → 判断目标距离、周次数、能力段、时间预算。
2. 至少匹配 **目标距离** 与 **周跑量预算**；不符就向跑者解释并建议换包，得到确认才换。
3. 没有明显的"正确"答案——教练包是**哲学选择**，由跑者拍板；agent 负责如实呈现差异。

## 加载规则 / loading rules

- 只看 `coaches/<id>/README_{lang}.md`（语言取跑者档案的 `language`）。
- 该文件已自包含：强度定义、周骨架规则、周期化、闸门、红线、力量建议。
- 若教练包与 docs 中的**通用安全层**（docs/03、docs/06）冲突，以更严者为准；通用安全层**不可移除**。

## 如何新增一个包 / adding a package

按 `coaches/_TEMPLATE_{zh,en}.md` 的固定章节写，放进新目录 `coaches/<new_id>/README_{zh,en}.md`，
并在此 README 的索引表加一行。完整指南见 `docs/10_adding_a_coach_skill_zh.md`。
