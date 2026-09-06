---
name: coach-polarized-80-20
description: >-
  80/20 极化教练方法论包。仅当跑者档案 runner_profile.yaml 的 coach 字段为
  polarized_80_20、且需要生成或更新训练计划时加载；随后按档案 language 字段读取
  references/coach-polarized-80-20_zh.md（或 _en.md）全文并遵守。
  Coach methodology for 80/20 polarized training. Load ONLY when the runner
  profile's `coach` field is `polarized_80_20` and a plan is being generated or
  updated; then read the matching language reference and obey it.
---

# coach-polarized-80-20（80/20 极化）

本技能是被跑者档案**显式选定**的方法论包（profile.coach == polarized_80_20），
不是通用自动触发工具；不要在未确认档案与计划场景时使用。

执行步骤：
1. 按档案 `language`（zh/en）读取 `references/coach-polarized-80-20_<lang>.md` 全文。
2. 照其中 8 个固定章节执行（强度体系/周骨架/周期化/闸门/红线/力量等）。
3. 强度分布按**时间**计量并核算 80/20，低强度用心率/体感；少数质量课配速取自
   `data/vdot_table.csv`（docs/09）。
4. 与通用安全层（docs/03、docs/06）冲突时取更严；安全层不可移除。
5. 该文件为"概括 + 应用指南"，非原书复制（版权声明在文件头）。

Docs: `docs/05` 生成流程、`docs/10` 新增技能指南。
