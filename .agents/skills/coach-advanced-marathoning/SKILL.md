---
name: coach-advanced-marathoning
description: >-
  Advanced Marathoning（Pfitzinger & Douglas，中文版《你可以跑得更快》）教练方法论包。
  仅当跑者档案 runner_profile.yaml 的 coach 字段为 advanced_marathoning、且需要生成或
  更新训练计划时加载；随后按档案 language 字段读取 references/coach-advanced-marathoning_zh.md
  （或 _en.md）全文并遵守。
  Coach methodology for Advanced Marathoning. Load ONLY when the runner profile's
  `coach` field is `advanced_marathoning` and a plan is being generated or updated;
  then read the matching language reference and obey it.
---

# coach-advanced-marathoning（高级马拉松 · 你可以跑得更快）

本技能是被跑者档案**显式选定**的方法论包（profile.coach == advanced_marathoning），
不是通用自动触发工具；不要在未确认档案与计划场景时使用。

执行步骤：
1. 按档案 `language`（zh/en）读取 `references/coach-advanced-marathoning_<lang>.md` 全文。
2. 照其中 8 个固定章节执行（强度体系/周骨架/周期化/闸门/红线/力量等）。
3. 需每周 ≥5 跑且质量日 ≥2；跑量较小时先建议更温和的包并征得确认。
4. 配速取自 `data/vdot/`（docs/09）；E/GA 用心率/体感。
5. 与通用安全层（docs/03、docs/06）冲突时取更严；高跑量不豁免红黄灯。
6. 该文件为"概括 + 应用指南"，非原书复制（版权声明在文件头）。

Docs: `docs/05` 生成流程、`docs/10` 新增技能指南。
