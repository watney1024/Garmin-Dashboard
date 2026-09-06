---
name: coach-lydiard
description: >-
  亚瑟·莱迪亚德（Lydiard）训练体系教练方法论包。仅当跑者档案 runner_profile.yaml 的
  coach 字段为 lydiard、且需要生成或更新训练计划时加载；随后按档案 language 字段读取
  references/coach-lydiard_zh.md（或 _en.md）全文并遵守。
  Coach methodology for Arthur Lydiard's training system. Load ONLY when the runner
  profile's `coach` field is `lydiard` and a plan is being generated or updated; then
  read the matching language reference and obey it.
---

# coach-lydiard（莱迪亚德体系）

本技能是被跑者档案**显式选定**的方法论包（profile.coach == lydiard），
不是通用自动触发工具；不要在未确认档案与计划场景时使用。

执行步骤：
1. 按档案 `language`（zh/en）读取 `references/coach-lydiard_<lang>.md` 全文。
2. 照其中 8 个固定章节执行（强度体系/周骨架/周期化/闸门/红线/力量等）。
3. 本体系强烈依赖**大跑量基础期**：档案 `runs_per_week` 与可用时间不足时先建议更温和的包并征得确认。
4. 低强度期配速用心率/体感；山坡/间歇等质量课配速可参考 `data/vdot/` 表（docs/09）。
5. 与通用安全层（docs/03、docs/06）冲突时取更严；安全层不可移除。
6. 该文件为"概括 + 应用指南"，非原书复制（版权声明在文件头）。

Docs: `docs/05` 生成流程、`docs/10` 新增技能指南。
