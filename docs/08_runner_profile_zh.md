# 08 · Runner profile：计划生成的输入（写给 AI agent）

`runner_profile` 是**跑者档案**——一份 YAML，包含目标与 A 赛、可训练日、PR 成绩、约束与基线。
**它驱动一切计划生成**：没有档案就不生成计划，先访谈补全档案。

- 真实档案是私有运行文件（gitignored，建议放 `workspace/runner_profile.yaml`）。
- 仓库只带虚构示例：`examples/runner_profile.example.yaml`（**填好的**虚构档案）。
- **三种填写入口，任选一种**（字段定义同一份，别自己另列）：
  1. **agent 逐题访谈** —— 用 `prompts/collect_profile_zh.md`（推荐；agent 会先去 Garmin 把能查的查掉）；
  2. **空白问卷** —— 跑者自己填 `examples/runner_profile.questionnaire.yaml`；
  3. **交互式向导** —— `python scripts/profile_wizard.py`（纯标准库，逐题问、可带默认值改写既有档案）。
- **写完必须校验**：`python scripts/profile_wizard.py --check <档案路径>`，**0 error 才算过**
  （warning 允许，但要看懂）。校验器只认受限 YAML 子集：**拒绝** flow map `{...}`、块标量 `|`/`>`、
  tab 缩进、锚点/别名；**接受**内联序列 `[a, b]`、跨行标量、行首 `---`。
- 档案里可以有 schema 之外的**扩展块**（如本仓跑者的实测锚点 `measured:`）：校验器只对它告警、
  不报错，向导也会**原样逐字保留**它。
- agent 首次接触一个跑者时，用一轮结构化问答补全档案；之后维护即按周更新。

## 1. 字段总表

```yaml
identity:
  alias:           # 化名/称呼（不使用真实姓名）
  language:        # 文档语言: zh | en
  timezone:        # 影响周界定的时区，如 Asia/Shanghai
  birth_year:      # 可选：出生年；与 sex 一起启用年龄/性别修正 VDOT（docs/09 §8）
  sex:             # 可选：F | M
races:
  - name:          # 赛事名（脱敏描述，如"示例国际马拉松"）
    date: YYYY-MM-DD
    distance: marathon | half | 10k | 5k | ...
    role: A | attempt | training   # 见"多比赛与 A 赛模型"
    note:          # 可选：补给/赛道备注
weekly:
  runs_per_week: N
  days:            # 一周每天的角色映射（可省略天）
    Tuesday: quality
    Thursday: easy
    Friday: easy
    Sunday: long
  long_run_day: Sunday
  quality_days: [Tuesday]     # 可多个；quality 由教练包定义
  max_run_min:     # 可选：单课时间上限（约束周骨架）
pr:
  5k: MM:SS        # 最好成绩（填 ≥1 即可推导 VDOT）
  10k: MM:SS
  half: H:MM:SS
  marathon: H:MM:SS
coach: daniels_vdot            # 所选教练 id -> .agents/skills/coach-<id>/
strength:          # 可选
  sessions_per_week: N
  days:                       # 用块状写法（不要 { Wednesday: lower, ... } 这种 flow map）
    Wednesday: lower
    Saturday: "upper/core/calf"
constraints: []    # 自由文本约束：伤病史、作息、出差频率、恢复偏好
metric_baselines:  # 给黄红灯判定的基线（docs/03）
  resting_hr: 50
  weight_kg: 62.0
  sleep_h: 7.2
devices:           # 可选：额外传感器/配件 —— 决定有哪些高阶数据可用（docs/02 §6 第 10 条）
  - kind: hr_strap        # hr_strap | running_pod | power_meter
    since: YYYY-MM-DD     # 数据里首次出现的日期（**也就是曲线断点**，必须记）
    note:                 # 可选：型号、哪几次漏戴
```

**`devices` 说明**：只记**额外的传感器/配件**，手表本身不用写。它有三个作用：
① 告诉 agent **哪些高阶数据本来存在**（心率带 → 左右平衡/呼吸率/着地时间占比；跑步豆/功率计 →
垂直振幅/触地时间/步长/功率），没有对应配件就不要在计划里引用这些指标；
② `since` 记录了**数据断点**——配件启用前后同名字段的**标尺不同**，不能跨断点画趋势（docs/02 §6 第 10 条）；
③ 配件新增/停用/漏戴时不必猜，直接问跑者并回写这里。

## 2. 多比赛与 A 赛模型

跑者可能有多场比赛。**每场比赛必须标 `role`，三者互斥：**

| role | 含义 | 跑法 | 成绩是否进 PR/更新 VDOT |
|---|---|---|---|
| `A` | **唯一**的"跑成绩"赛，周期终点 | 全力；前两周 tapering；所有周期化为之服务 | 是（比赛后） |
| `attempt` | 尝试赛/自测，逼近成绩但仍是训练的一环 | 认真但不孤注一掷（如半马当长距离最后 1/3 提速） | 是（若超过 PR 可更新） |
| `training` | 训练课的一部分 | 不全力：当马配段/变速课/负分段长距离跑 | 否 |

规则：
1. **一个周期内只能有 1 个 A。** 出现两个 → 与跑者确认降级一个为 attempt/training，并记录原因。
2. **换 A 赛必须记录原因**（中签失败/伤病/状态），并整体重排周期与 taper。
3. 非 A 赛**不允许毁掉 A 赛**：它与当周长距离冲突时，作为"那周的长距离课"并入（用 `role=training` 的写法跑），而不是额外加量。
4. 排课/复盘/闸门均以"**下一场 A 赛**"为准倒退定位周号；非 A 赛只影响当周内容。

## 3. VDOT 与 PR 的关系（详见 docs/09）

- 用 `pr` 里**最近 6 个月内、最可信的成绩**推导 VDOT；多个距离结果互相验证（应相差 ≤1）。
- 成绩陈旧或来自不同训练周期 → 用最近一次 A/attempt 赛更新后再定配速。
- 比赛后：把新成绩写入 `pr`（保留日期），触发 VDOT 更新；若 VDOT 变化 ≥1，通过周复盘流程提出计划更新。

## 4. 教练 skill 选择（详见 docs/10 / .agents/skills/）

- `coach` 存教练 id，**必须能映射到 `.agents/skills/coach-<id>/` 目录**（id 的 `_`→`-`），
  如 `daniels_vdot` → `coach-daniels-vdot`。
- 生成计划前：agent 读取所选包全文并遵守它；如档案与包明显不适配（目标距离/周次数/能力段），先向跑者解释并建议换包，得到确认才换。
- 换包 = 重新生成计划 = 版本表新大版本。

## 5. 周骨架如何被构造（由 docs/05 的流程消费）

1. 从 `weekly.days` 拿每天角色；未列出的天默认"可选/休息"。
2. 教练包的"周骨架构造规则"用 `runs_per_week`、`long_run_day`、`quality_days` 把"E / Q / long"分布到可用日。
3. 通用约束生效：长距离前一天无下肢大重量（docs/03 安全层）；`max_run_min`（若有）限制单课时间。
4. 逐周课表里的**命名格式**：`W<n> <星期> <课型> <关键信息>`（如 `W1 Tue E5`、`W6 Sun Tune10K(训练)`）。

## 6. 维护节奏

- 跑者随时改：赛历（新报名/取消/改 A）、可用日、伤病约束、**新增/停用配件（`devices`）**。
- agent 每周复盘后如有比赛结果/PR 变化 → 更新本文件并写入周复盘"下周调整"。
- **配件变化要主动记**：识别到新的 `source_type=antplus` 设备（或原有设备消失）→ 更新 `devices.since`，
  并在该周日志/复盘里标注这就是**数据断点**（docs/02 §6 第 10 条）。
- 版本：`runner_profile` 不是代码；改动在周复盘中说明即可，不进计划版本表。
