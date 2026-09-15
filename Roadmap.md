# Roadmap · 路线图

> 本文件是项目公开路线图（双语）。跑者私人待办不在这里；个人数据永远不进仓库。
> This is the project's public roadmap (bilingual). Private runner notes stay out; personal
> data never enters the repo.

## 已完成 / Done

- [x] 仓库开源：写给 AI agent 的规则文档（docs 00–10，双语）+ 纯标准库脚本
- [x] 教练方法论落地为 Agent Skills（`.agents/skills/`），现有 5 个：
      `daniels_vdot` / `polarized_80_20` / `hanson` / `advanced_marathoning` / `lydiard`
- [x] VDOT 数据 GPL-3.0 化（`data/vdot/`，源自 Zac Blanco VDOT Calculator），配速换算统一走 `scripts/vdot.py`
- [x] coach 必检项框架：每个 coach 包含固定第 9 节"必检项"（强度构成、疲劳量化与管理、
      大小周期、轻松跑口径），生成计划后逐项自检（见 `docs/10`）
- [x] 5 个教练包 references 全部基于原书精读重写（中英双语同步）：
      丹尼尔斯《Daniels' Running Formula》、Pfitzinger《Advanced Marathoning》（你可以跑得更快）、
      Lydiard《Healthy Intelligent Training》、Hansons《Marathon Method》、
      Fitzgerald《80/20 Running》；Hal Higdon《马拉松终极训练指南》作交叉验证参考。
      每包含原书精确数据：训练类型上限、心率区间、周期时长、配速定义、疲劳管理、闸门标准。
- [x] 训练强度量化（load）：丹尼尔斯点数表（表 5-4）与 N 分课上限表（表 5-5）入库
      （`data/vdot/intensity_points.csv`、`session_prescriptions.csv`）；`vdot.py --points /
      --session / --selfcheck`；排计划与周复盘接入（docs/05/06/09 §7）。load 为建议性指标：
      只做趋势与量调节，不触发、不放宽任何红黄灯。
- [x] 计划 HTML 规格升级为**十章结构**（第十章＝执行追踪与每周复盘＝"宪法"），自包含、
      零外链、数据卡 + 周历格 + 色块行文；`examples/plan.example.html` 按新形态重制，
      `docs/05` §4/§5 同步。
- [x] **真实设备冒烟通过**（2026-09-14）：在中国大陆账户上跑通全流程——`garmin_pull.py`
      重建主表（992 行）＋ inbox 明细、`garmin_schedule.py` 幂等排课、`garmin_track_workout.py`
      建结构化操场课并排期。过程中修掉两个必崩 bug（见下）。
- [x] **操场/间歇课建课能力**：`scripts/garmin_track_workout.py` + `scripts/track_spec.example.json`。
      核心是 Garmin 的 **计圈键**（step `endCondition = lap.button`）——**每次按键记一个标称 400 m，
      与跑道实际圈长解耦**；`week_spec` + `garmin_schedule.py` 只能表达连续跑课，间歇课必须走这条路。
      配套 `docs/02` §3b（schema）、能力技能包 `.agents/skills/track-workout/`（中英 references，
      **不是教练包**、不经 `profile.coach` 选择）。
- [x] **计划里程碑成为必备槽位**：第四章里程碑表（编号/名称/目标周与日期/可核验判定标准/达成列）。
      与闸门做性质区分——闸门＝决策点（可改计划），里程碑＝成就点（**未达成只记录、不自动改计划**）。
      `docs/05` §2/§4/§5/§6、`docs/06` §1/§4、`examples/plan.example.html` 同步。
- [x] **图表可悬停读值**：两张 canvas 的柱状/折线支持鼠标悬停显示当周具体数值（`.ctip` 自包含
      tooltip，零外部库、打印时隐藏）；`docs/05` §4/§5 与 `prompts/generate_plan_{zh,en}` 同步。
- [x] **数据坑补记**：`docs/02` §6.9——力量日的跑步机热身**没有距离字段**，不会以跑步活动落到
      Garmin，周跑量会系统性少算（本案 ≈4 km/周）。该值只能由跑者口述，是**估算而非测量**，
      不得用于 VDOT 反推/配速统计/心率漂移对比。

## 近期 / Near term

- [ ] **runner profile 问卷化**：把"跑者自己写 YAML"变成三种填写入口——可填写的问卷模板
      `examples/runner_profile.questionnaire.yaml`、agent 逐题访谈提示词
      `prompts/collect_profile_{zh,en}.md`、交互式向导 `scripts/profile_wizard.py`
      （纯标准库，含 `--check` 校验与 `--selfcheck` 一致性自检）。
- [ ] **VDOT 多成绩加权**：跑者输入多份成绩时，按目标距离加权选当前 VDOT（如目标全马 →
      全马成绩权重更高），其余成绩作交叉验证；规则写入 `docs/09` 与 `scripts/vdot.py`。
- [ ] **低跑量 vs 教练包量上限的冲突**：周量 <64 km 时，丹尼尔斯原书的 L ≤30%／T ≤10%／
      I ≤8%（教练包 §2/§9）与"以全马为目标"无法同时成立。需要一个正式口径（提高周量 /
      换目标距离 / 明确"低跑量改编"并在计划第十章留痕），目前示例计划采用的是第三条。

## 中期 / Mid term

- [ ] **VDOT 年龄/性别修正**：按跑者档案的年龄/性别对 VDOT 与配速做修正，使训练配速更准确
      （丹尼尔斯表 5-6/5-7/5-8）。代码与文档已就绪（`scripts/vdot.py --age/--sex`、
      `--selfcheck` B 组校验、docs/09 §8、档案字段 `identity.birth_year/sex`）；
      待把书中三张年龄表重新提取并通过数据校验门槛后入库即可启用。

- [ ] **生理指标驱动的疲劳/状态评估**：把**睡眠、HRV、训练负荷**等客观生理指标纳入
      疲劳指数与身体状态判定，作为主观 6 项（`docs/03` §2）之外的**补充输入**。
      现状：红黄灯由"主观 6 项 + 静息心率"驱动，睡眠只作信息项、不参与判定；MCP 侧
      `get_hrv_data` / `get_sleep_summary` / `get_training_status` 已可读（见 `docs/01` §3）。
      待定项：HRV 基线口径（7 日 / 30 日滚动均值？）、客观与主观冲突时如何取舍、
      以及**是否只做"提示"而不直接触发红黄灯**。
      **硬约束**：通用安全层只允许**加严**、不允许放松（`docs/03`/`docs/06` 铁律）——
      新指标可以让判定更保守，不能替代或稀释现有的主观 6 项与静息心率规则。

## 持续 / Ongoing

- [ ] 跟踪上游 `Taxuspt/garmin_mcp`：PR #249 合并后，`docs/01` 改回官方 main 安装方式。
- [ ] 各 coach references 持续打磨：原书数据已落地，下一步随实际使用反馈验证配速/周期
      的可操作性，补充边界案例（低跑量、高龄、伤病恢复期等）。

## 约定 / Conventions

- 改动 VDOT 相关内容必须三者一致：`data/vdot/` schema ↔ `scripts/vdot.py` ↔ `docs/09`。
- 新增 coach 走 `docs/10`；通用安全层（`docs/03`/`docs/06`）不可被任何 coach 放宽。
