# 10 · 新增一个教练 skill（写给 agent 与维护者）

教练 skill 让计划生成可以**即插即用不同教练理念**。任何人（通常是一个 agent 与跑者协作）
都可以按本文件新增一个。**新增 skill 不需要改任何代码。**

## 位置与命名（Agent Skills 标准）

```
.agents/skills/
  README.md                                   # 索引：加一行
  coach-<new_id>/                             # 目录名 = "coach-" + id（id 的 _ → -）
    SKILL.md                                  # frontmatter name/description + 加载指引
    references/
      coach-<new_id>_zh.md                    # 完整方法论正文（8 固定章节）
      coach-<new_id>_en.md
```

跑者档案 `coach: <id>`（如 `daniels_vdot`）映射到 `coach-daniels-vdot`。生成计划时 agent
先读 `SKILL.md`，再按档案 `language` 读对应 references 全文（docs/05 §2）。

## 工作流

1. 确认理念来源有**可引用的公开出处**（书目/文章/人物）。正文必须是**你自己写的概括与
   应用指南**，不复制原文——每个 references 文件第 1 节都要有版权声明。
2. 创建 `coach-<new_id>/SKILL.md`，frontmatter 需含：

   ```yaml
   ---
   name: coach-<new_id>
   description: >-
     <理念名> 教练方法论包。仅当跑者档案 coach 字段为 <new_id>、且需要生成或更新训练计划
     时加载；随后按档案 language 读取 references/coach-<new_id>_zh.md（或 _en.md）全文并遵守。
     <English one-line trigger>...
   ---
   ```

   SKILL.md 正文写加载步骤与三条铁律：按语言读全文、配速不自行发明（查 data/vdot_table.csv
   或心率/体感口径）、与通用安全层冲突取更严。
3. 在 `references/` 放 `coach-<new_id>_{zh,en}.md`，按下方"正文模板"填 8 节。
4. 在 `.agents/skills/README.md` 索引表加一行（含 coach id 与触发条件）。
5. 若该理念会改变计划 HTML 某章节内容，在 references 内给出模板/示例片段；不改变文档结构。

## 正文模板（references/coach-<id>_<lang>.md 固定 8 节）

每节都须有内容；不适用处写"（本流派不涉及）"：

```
# <教练名> <new_id>
## 1. 出处与适用   ← 必含版权声明；书目/人物出处；适合/不适合画像
## 2. 强度体系与配速来源 ← 各区定位、配速落到 VDOT 表/心率/体感
## 3. 周骨架构造规则     ← 能被 runs_per_week/long_run_day/quality_days 参数化
## 4. 周期化与跑量爬升   ← 阶段、爬升上限、恢复周、taper
## 5. 测试赛与闸门       ← 非 A 赛用法、本派关键闸门
## 6. 红线与注意点       ← 只可严于通用安全层(docs/03/06)
## 7. 力量/辅助建议
## 8. 应用示例（可选）
```

## 质量门槛（agent 自检）

- [ ] 一个 agent 只读该 skill（SKILL.md + 对应语言 references）就能生成符合理念的周骨架与课表。
- [ ] 每节有内容（不适用处明确写"不涉及"）。
- [ ] 与通用安全层无冲突，或冲突处取更严并注明。
- [ ] references 第 1 节版权声明；正文是转写非引用。
- [ ] 明确"适合/不适合"画像，避免误用。
- [ ] `.agents/skills/README.md` 索引已更新。

## 与 docs/05 的对接

`docs/05` 描述通用生成流程：读档案 → 读所选 skill（SKILL.md + references）→ 生成 HTML
计划。每个 skill 相当于为流程提供"方法论参数"；若所有 skill 都需要某个新参数，把它提升
为本文档的公共约定，而不是只写在一个 skill 里。

## 测试

- 用 `examples/runner_profile.example.yaml` + 新 skill 跑一次 docs/05 流程，人工/agent 校验
  产出的周骨架自洽（次数、长距离日、强度日符合档案）。
- 检查配速落在合理区间（与公开资料差不大于 ~10–20 s/km）。
