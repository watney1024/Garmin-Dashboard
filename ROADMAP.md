# ROADMAP · 路线图

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

## 近期 / Near term

- [ ] **VDOT 多成绩加权**：跑者输入多份成绩时，按目标距离加权选当前 VDOT（如目标全马 →
      全马成绩权重更高），其余成绩作交叉验证；规则写入 `docs/09` 与 `scripts/vdot.py`。
- [ ] **真实设备冒烟**：在真实 Garmin 环境跑通 `garmin_pull.py` / `garmin_schedule.py`
      （`GARMIN_MCP_SRC`，CN 网络用 `Taxuspt/garmin_mcp` PR #249 分支，见 `docs/01`）。

## 中期 / Mid term

- [ ] **VDOT 年龄/性别修正**：按跑者档案的年龄/性别对 VDOT 与配速做修正，使训练配速更准确
      （丹尼尔斯表 5-6/5-7/5-8）。代码与文档已就绪（`scripts/vdot.py --age/--sex`、
      `--selfcheck` B 组校验、docs/09 §8、档案字段 `identity.birth_year/sex`）；
      待把书中三张年龄表重新提取并通过数据校验门槛后入库即可启用。

## 持续 / Ongoing

- [ ] 跟踪上游 `Taxuspt/garmin_mcp`：PR #249 合并后，`docs/01` 改回官方 main 安装方式。
- [ ] 各 coach references 持续打磨：原书数据已落地，下一步随实际使用反馈验证配速/周期
      的可操作性，补充边界案例（低跑量、高龄、伤病恢复期等）。

## 约定 / Conventions

- 改动 VDOT 相关内容必须三者一致：`data/vdot/` schema ↔ `scripts/vdot.py` ↔ `docs/09`。
- 新增 coach 走 `docs/10`；通用安全层（`docs/03`/`docs/06`）不可被任何 coach 放宽。
