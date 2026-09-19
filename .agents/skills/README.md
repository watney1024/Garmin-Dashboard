# .agents/skills — 教练理念技能包（Agent Skills 标准）

> 正源所在。生成计划前，agent 必须**整包加载**所选教练的技能并按语言读其全文。
> Canonical location. Before generating a plan, an agent MUST load the chosen coach's
> skill in full (per the profile language) and obey it.

采用跨工具 **Agent Skills** 约定：每个技能一个目录，含 `SKILL.md`
（YAML frontmatter `name` + `description`）+ `references/<zh|en>.md` 全文。
适配 Claude Code / GitHub Copilot / OpenAI Codex / Goose 等（Claude 项目级也可放
`.claude/skills/`，此处以 `.agents/` 为唯一正源，避免双份维护）。

## 索引 / index

| coach id（profile 字段） | skill 目录 | 触发 |
|---|---|---|
| `daniels_vdot` | `.agents/skills/coach-daniels-vdot/` | profile.coach == daniels_vdot 且生成/更新计划 |
| `polarized_80_20` | `.agents/skills/coach-polarized-80-20/` | profile.coach == polarized_80_20 且生成/更新计划 |
| `hanson` | `.agents/skills/coach-hanson/` | profile.coach == hanson 且生成/更新计划 |
| `advanced_marathoning` | `.agents/skills/coach-advanced-marathoning/` | profile.coach == advanced_marathoning 且生成/更新计划 |
| `lydiard` | `.agents/skills/coach-lydiard/` | profile.coach == lydiard 且生成/更新计划 |

每个 skill 的 `references/coach-<id>_zh.md` / `_en.md` 是**完整方法论正文**（9 固定章节：
1 出处与适用 … 8 应用示例、9 必检项），
`SKILL.md` 负责精确触发与加载指引。**内容均为"概括 + 应用指南"，非原书复制（版权声明在
各 references 文件头）**。

## 索引 B · 能力技能 / index B - capability skills

> 与上面的教练包**不同**：能力技能不提供训练方法论、**不经 `profile.coach` 选择**，
> 而是在对应场景出现时加载（把某件事做对）。

| 技能目录 | 何时加载 |
|---|---|
| `.agents/skills/track-workout/` | 要建/改**操场（跑道）间歇课**、把间歇课排进 Garmin，或要解析历史操场课时 |

`track-workout` 的核心机制：步骤结束条件设为 `lap.button` ⇒ **每次按键记一个标称 400 m，
与跑道实际圈长解耦**。写法与脚本见其 `SKILL.md`、`references/track-workout_{zh,en}.md`，
以及 `docs/02` §3b 与 `scripts/garmin_track_workout.py`。

## 加载规则 / loading rules

1. 读 `runner_profile.yaml` 的 `coach` → 定位对应 skill 目录（见上表）。
2. 先读 `SKILL.md`，再按档案 `language` 读 `references/coach-<id>_<lang>.md` 全文。
3. 与通用安全层（docs/03、docs/06）冲突时取更严；安全层不可移除。

## 新增一个技能 / adding a skill

按 `.agents/skills/coach-<new_id>/SKILL.md` + `references/coach-<new_id>_{zh,en}.md`
的形态新建目录，并在此 README 索引表加一行。完整指南见 `docs/10_adding_a_coach_skill_zh.md`。
