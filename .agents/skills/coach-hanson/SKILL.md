---
name: coach-hanson
description: >-
  汉森马拉松法教练方法论包。仅当跑者档案 runner_profile.yaml 的 coach 字段为
  hanson、且需要生成或更新训练计划时加载；随后按档案 language 字段读取
  references/coach-hanson_zh.md（或 _en.md）全文并遵守。
  Coach methodology for Hanson's Marathon Method. Load ONLY when the runner
  profile's `coach` field is `hanson` and a plan is being generated or updated;
  then read the matching language reference and obey it.
---

# coach-hanson（汉森马拉松法）

本技能是被跑者档案**显式选定**的方法论包（profile.coach == hanson），
不是通用自动触发工具；不要在未确认档案与计划场景时使用。

执行步骤：
1. 按档案 `language`（zh/en）读取 `references/coach-hanson_<lang>.md` 全文。
2. 照其中 8 个固定章节执行（强度体系/周骨架/周期化/闸门/红线/力量等）。
3. 需每周 ≥5 跑；跑者档案 runs_per_week <5 时先建议换包并征得确认。
4. 配速取自 `data/vdot_table.csv`（docs/09）或 ST 的"半马–马配区间/体感"。
5. 疲劳累积是特性，但黄/红灯与伤病规则照常（docs/03、docs/06），安全层不可移除。
6. 该文件为"概括 + 应用指南"，非原书复制（版权声明在文件头）。

Docs: `docs/05` 生成流程、`docs/10` 新增技能指南。
