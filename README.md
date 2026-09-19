# Garmin-Dashboard

> An AI-agent-driven running-training dashboard, built on your Garmin Connect data.
> 一个由 AI agent 驱动的跑步训练看板，数据源自你的 Garmin Connect。

**Humans don't write code here. Agents do.** This repo is a playbook + a few stable
scripts. A runner only maintains their own `runner_profile` and says **one sentence per
week**; an AI agent reads the docs, pulls Garmin data through MCP, summarizes training,
and generates / maintains a personalized HTML training-plan dashboard.

**这里不要求人写代码，干活的是 AI agent。** 跑者只维护自己的 runner profile、每周说
一句话；AI agent 读文档、经 MCP 拉 Garmin 数据、总结训练，并生成/维护一份个人 HTML
训练计划看板。

## What you get / 它能做什么

- **Plan generation framework** — 由 `runner_profile` 驱动：多个比赛选一个 A 赛、自定义每周
  训练次数/长距离日/强度日、VDOT 表定各强度配速、教练理念以 `.agents/skills/` 下的
  Markdown skill 即插即用（首批：丹尼尔斯 VDOT / 80-20 / 汉森 / Advanced Marathoning /
  莱迪亚德，可被 Claude Code / Copilot / Codex 等发现）。
  Profile-driven plan generation with one A race, custom weekly structure, VDOT paces and
  plug-in coach skills under `.agents/skills/` (initial: Daniels VDOT, 80/20, Hanson,
  Advanced Marathoning, Lydiard).
- **Weekly review loop** — 每周复盘：四段式复盘、三趋势、黄/红灯安全判定、动态调整课表并
  在版本表递增 `vN`。每周复盘闭环：周复盘、红黄灯、改计划、版本记录。
- **Garmin data, hands-free** — `scripts/garmin_pull.py` 通过 garmin-mcp（stdio）自动拉全量
  活动并重建规范主表，逐次明细自动进 inbox；`scripts/garmin_wellness.py` 另拉每周健康基线
  （静息心率 / 睡眠 / HRV / 体重 / 训练状态）。数据自动拉取，无需手动导出。
  Failed fetches never silently truncate the master table.
- **Push workouts to your watch** — `scripts/garmin_schedule.py` 把连续跑课按周排进 Garmin
  日历；`scripts/garmin_track_workout.py` 处理操场/间歇课（计圈键：每次按键记标称 400 m）。
  两者都按**课名 + 内容指纹**幂等，改处方后重跑即可。把课表推到手表。
- **VDOT tables & paces** — `scripts/vdot.py` 由 PR 求 VDOT、给各强度配速、做年龄/性别修正。

## Quickstart / 快速开始

1. Fork 这份仓库，把它变成你自己的私有工作区（真实档案与数据放 gitignored 的 `workspace/`）。
2. 填 `runner_profile` —— 三种入口任选：让 agent 逐题访谈（`prompts/collect_profile`）、
   自己填空白问卷 `examples/runner_profile.questionnaire.yaml`、或跑交互式向导
   `python scripts/profile_wizard.py`（填完都跑一次
   `python scripts/profile_wizard.py --check <档案>`，0 error 才算过；参考 `docs/08`）。
3. 让一个 AI agent 打开 `AGENTS.md` 开始干活——它能自己完成其余步骤。
4. 人类每周只需要说一句话（模板见 `docs/03`）。

一个 AI agent 打开 `AGENTS.md` 即可自动完成其余步骤；跑者每周只回报一句话
（模板在 `docs/03_personal_state`）。

## Repository map / 仓库地图

```
AGENTS.md            agent 入口（先读这个）· universal entry for agents
docs/                写给 agent 的规则文档 00–10（每篇 _zh/_en 双语）· the playbooks
.agents/skills/       教练理念技能包 ＋ 能力技能（Agent Skills）· coach & capability skills
prompts/             可直接发给 agent 的提示词 · copy-paste prompts
scripts/             Python 工具（零第三方运行时依赖）· stable scripts
data/vdot/            VDOT 规范表（GPL-3.0 派生）· canonical VDOT tables
examples/            虚构示例跑者的全套产物（CC0）· synthetic examples
workspace/           跑者私有产物（gitignored）· private runner workspace
```

## License / 许可

MIT。示例数据全部虚构（CC0）。第三方依赖仅外部引用未内置（见 `NOTICE.md`）。
