# examples/ — 虚构示例跑者全套（CC0）

Everything in this directory is **fabricated** around a fictional runner, "示例跑者 /
Example Runner". No real person's data is used. You may copy and adapt these files freely
(CC0). See `docs/` for the schema each file follows.

本目录所有数据为**虚构**（示例跑者"示例跑者"），无任何真实个人数据，可自由复制改编（CC0）。
各文件对应的 schema 见 `docs/`。

## Files / 文件

| file | 说明 | 关联文档 |
|---|---|---|
| `runner_profile.example.yaml` | 虚构跑者档案：3 场赛（训练 10K / 尝试 半马 / **A** 全马）、每周 4 跑、PR、教练=daniels_vdot | docs/08 |
| `activities.example.csv` | 规范 16 列主表示例（含跑/操场/力量/抱石/骑行） | docs/02 |
| `inbox/activity_900000001.example.csv` | 单次明细示例：区间课的休息段污染演示（走休 lap 14:xx/km） | docs/02 §2/§6 |
| `registry.example.json` | 排课幂等 registry 的格式示例（ID 虚构） | docs/02 §4 |
| `plan.example.html` | **主示例成品**：16 周丹尼尔斯 VDOT 计划（中文，十章结构，自包含无外链）。跑者=示例跑者，A 赛 2027-11-21 目标 4:00，VDOT 39.4 | docs/05 |
| `training_log.example_zh.md` | 训练日志主观 6 项示例（填好 W1） | docs/03 |
| `weekly_review.example_zh.md` | 每周复盘四段式 + 闸门表示例（填好 W1） | docs/06 |

## The flow, demonstrated / 流程演示

1. 读 `runner_profile.example.yaml` → docs/08
2. 加载 `.agents/skills/coach-daniels-vdot/SKILL.md` 与 `references/coach-daniels-vdot_zh.md`（或 _en）
3. 由 PR 求 VDOT：`python scripts/vdot.py --half 1:52:30` → 39.4（三份 PR 互验，取最近且全力的半马）
4. 得到配速表并写进 `plan.example.html` 第七章（查 `data/vdot/` 表，见 docs/09）
5. 跑脚本演示：`python scripts/garmin_schedule.py scripts/week_spec.example.json --dry-run`

```bash
python scripts/vdot.py --5k 23:45
python scripts/garmin_pull.py --help          # 连真实数据前先看参数
```

> 注：`scripts/week_spec.example.json` 与 `examples/plan.example.html` 的 W1 对齐
> （2027-08-02 起那周）；数值均虚构。
