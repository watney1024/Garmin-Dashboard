---
name: coach-daniels-vdot
description: >-
  Jack Daniels VDOT 教练方法论包。仅当跑者档案 runner_profile.yaml 的 coach 字段为
  daniels_vdot、且需要生成或更新训练计划时加载；随后按档案 language 字段读取
  references/coach-daniels-vdot_zh.md（或 _en.md）全文并遵守。
  Coach methodology for Jack Daniels VDOT. Load ONLY when the runner profile's
  `coach` field is `daniels_vdot` and a plan is being generated or updated; then
  read references/coach-daniels-vdot_zh.md or _en.md per the profile language and obey it.
---

# coach-daniels-vdot（丹尼尔斯 VDOT）

本技能是被跑者档案**显式选定**的方法论包（profile.coach == daniels_vdot），
不是通用自动触发工具；不要在未确认档案与计划场景时使用。

执行步骤：
1. 按档案 `language`（zh/en）读取 `references/coach-daniels-vdot_<lang>.md` 全文。
2. 照其中 8 个固定章节执行（强度体系/周骨架/周期化/闸门/红线/力量等）。
3. 数值型配速一律取自 `data/vdot/`（scripts/vdot.py，docs/09），不自行发明。
4. 与通用安全层（docs/03、docs/06）冲突时取更严；安全层不可移除。
5. 该文件为"概括 + 应用指南"，非原书复制（版权声明在文件头）。

Docs: `docs/05` 生成流程、`docs/10` 新增技能指南。
