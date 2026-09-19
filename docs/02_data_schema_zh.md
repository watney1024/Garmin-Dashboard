# 02 · 数据格式与 schema（写给 AI agent）

本文件定义仓库/工作区里的数据文件格式。**格式一旦确定就是约定，改格式必须连代码和文档一起改。** agent 处理数据时严格按本文件执行。

## 1. 主表 `Activities.csv`（规范 16 列）

全量活动主表，由 `scripts/garmin_pull.py` 每周从 Garmin 重建。作用：完整性核对 + 标题存储 + 快速趋势（周跑量/次数/时长/心率）。

表头**逐字**如下（中文列名，编码 `utf-8-sig` 带 BOM）：

```csv
活动类型,类型Key,日期,标题,距离km,时长,移动时长,平均配速min/km,热量,平均心率,最大心率,步数,累计爬升m,累计下降m,事件类型,活动ID
```

| 列 | 含义 | 规则 |
|---|---|---|
| 活动类型 | 中文类型名 | 由类型Key映射，见下 |
| 类型Key | Garmin 类型 key | 稳定枚举 |
| 日期 | ISO `YYYY-MM-DD HH:MM:SS` | 按此**倒序**排序 |
| 标题 | Garmin 端标题 | 默认常为"XX区 跑步"零信息；agent 知道课名时用 `set_activity_name` 批量改 Garmin 端 |
| 距离km | 公里数 | **四舍五入 2 位小数**；非跑量类型（力量/抱石/攀岩/游泳等）留空 |
| 时长 | 总时长 `HH:MM:SS` | 整段（含休息） |
| 移动时长 | 移动时长 `HH:MM:SS` | 纯移动 |
| 平均配速min/km | `MM:SS` | **用移动时长计算**；非跑步类型或速度不在合理范围（>20:00/km）留空 |
| 热量 | kcal | |
| 平均心率 | bpm | 非跑步类型可能为空 |
| 最大心率 | bpm | |
| 步数 | | |
| 累计爬升m / 累计下降m | 米 | |
| 事件类型 | Garmin 事件类型 | 保留原值 |
| 活动ID | Garmin 活动 ID | **主键**，与 inbox 文件名关联 |

### 类型Key → 中文映射（保持不变）

```python
TYPE_CN = {
 "running":"跑步","track_running":"操场跑步","trail_running":"越野跑",
 "treadmill_running":"跑步机跑步","strength_training":"力量训练",
 "bouldering":"抱石","indoor_climbing":"室内攀岩","badminton":"羽毛球",
 "cycling":"骑行","indoor_cardio":"室内有氧","breathwork":"呼吸训练",
 "pilates":"普拉提","lap_swimming":"游泳","hiking":"徒步",
 "ultimate_disc":"极限飞盘","other":"其他"}
```

未知类型保留原 key 作为"活动类型"显示。判定"跑步课"（用于算配速）的范围：
`running / track_running / trail_running / treadmill_running`。

### 生成/校验规则

- 一行一条活动，日期倒序（最新在上）。
- 只有值含逗号或引号才加双引号包裹；空值输出空。
- 历史脏数据守卫：个别历史行距离是**米**而非公里（数值 >100 视为米 → `/1000`）。
- **inbox 是"单次明细"、主表是"应有清单"**——单次 CSV 里没有日期/标题，关联靠活动 ID。

## 2. 单次明细 `data/inbox/activity_<id>.csv`

每次活动的佳明原生中文单次 CSV，自动下载，文件名 `activity_<id>.csv`（`<id>` = 主表活动ID）。内容因类型而异：

| 类型 | 明细内容 | 主要用途 |
|---|---|---|
| 跑步/操场跑 | 分圈明细（时间/距离/配速/心率/步频/步长/升降） | 还原分段执行：`300/100×18` 跑了几个、快段配速、休息段污染判断 |
| 力量训练 | 动作/组/次数/重量/组间休息 | 核对组数与负荷 |
| 抱石 | 线路明细 | 还原线路数/难度尝试 |

约定：
- 该目录是**自动生成区**，人不要手动改名/丢文件；唯一例外是补旧数据时丢入并说明，agent 合并。
- 只读、按 ID 匹配，**不要用文件时间戳或三元组匹配**（v13 协议以来改为按 ID）。

## 3. 周排课 spec JSON（`scripts/week_spec.example.json`）

由 agent 按教练包 + 跑者档案生成某一周的跑步课，供 `scripts/garmin_schedule.py` 使用：

```json
{ "name": "W1",
  "days": [
    {"date": "YYYY-MM-DD", "name": "W1 Tue E5", "kind": "easy",
     "distance_km": 5, "pace_min_km": 6.9, "hr_min": 125, "hr_max": 150}
  ]}
```

字段：
- `kind`: `easy | recovery | lsd`（由跑者档案/计划允许的课型限定；教练课、力量等不排在此文件）
- `distance_km` 与 `pace_min_km`：仅为**命名与时长兜底**（E/恢复课执行口径＝时间＋心率）
- `minutes` 可选；缺省 `round(distance_km × pace_min_km)`（无距离时默认 30）
- `hr_min/hr_max`：心率区间（默认 120/150）


### 3b. 操场（间歇）课 spec JSON（`scripts/track_spec*.json`）

**为什么单独一套**：普通跑步课按 GPS/时间度量，但真实跑道的单圈**并非恰好 400 m**，
"2 圈 = 800 m" 会与实际距离持续漂移。Garmin 的解法是**计圈键**——把步骤的结束条件设为
`lap.button`，**每次按键即记一个标称距离**。跑者只需在表上"每 400 m 按一次、休息结束再按一次"，
复盘时**只比段内时间，不做 GPS 距离换算**（§6 第 2/9 条）。

`scripts/garmin_track_workout.py` 把下面这份"人话处方"转成 Garmin 的结构化课并排期：

```json
{ "name": "W2 Thu Track 6x1.2k",
  "date": "2027-08-05",
  "lap_meters": 400,             // 计圈键代表的标称距离
  "rest_style": "rest",          // rest = 完全休息（静止） | recovery = 活动恢复（慢跑）
  "warmup":    {"laps": 5},                    // 5 × 400m = 2 km（热身不带心率靶，见下）
  "pre_rest_min": 6,
  "sets": 6, "laps_per_set": 3,  // 6 组 × 3 × 400m = 7.2 km（每组 3 次计圈）
  "set_rest_min": 3,
  "cooldown":  {"laps": 2}       // 可选
}
```

生成的结构（与手建的"操场跑步"课一致）：

```
repeat 5×  [ warmup · lap.button ]
rest 6 min
repeat 6×  [ interval · lap.button ×3 , rest 3 min ]
```

字段说明：

| 字段 | 必填 | 说明 |
|---|---|---|
| `name` | 是 | 课名，同时是 registry 幂等键 |
| `date` | 否 | 有则排到该日；也可用 `--date` 覆盖 |
| `lap_meters` | 否 | 默认 400；仅用于生成描述文字与摘要 |
| `rest_style` | 否 | 默认 `rest`（**静止**）。若组间是慢跑，必须显式写 `recovery` |
| `warmup.laps` / `cooldown.laps` | 否 | 按计圈键做几圈热身/冷身 |
| ~~`warmup.hr_min/hr_max`~~ | — | **已废弃**：热身**不设心率靶**。写了也只打一行 WARNING 并忽略 |
| `pre_rest_min` / `set_rest_min` | 否 | 前置休息 / 组间休息（分钟） |
| `sets` / `laps_per_set` | 否 | 组数与每组圈数 |

**热身/冷身一律不带心率靶**（2026-09-19 跑者明确要求）。理由：热身期心率本来就从静息往上爬，
挂一个区间只会**全程触发下限告警**，把热身变成"追心率"。冷身本来就无靶，热身现已对齐。
`warmup.hr_min/hr_max` 是历史字段，仍兼容读取但不再生效。

**注意**：`week_spec` + `garmin_schedule.py` **只能表达连续跑课**，无法表达间歇结构；
间歇课必须走本节的 track spec。两者共用同一个 registry（幂等键＝课名 ＋ **内容指纹**，
所以改了内容而名字没变也会重建；见 §4）。

## 4. 已建训练 registry `garmin_workout_registry.json`

`garmin_schedule.py`（连续跑课）与 `garmin_track_workout.py`（操场间歇课）**共用**的幂等缓存。
格式 v2：

```json
{ "schema_version": 2,
  "workouts": {
    "W1 周二 E5":        {"id": 12345678, "kind": "run",   "fp": "a1b2c3d4e5f60718"},
    "W1 周四 操场 6×1.2k": {"id": 12345679, "kind": "track", "fp": "0f1e2d3c4b5a6978"}
  }}
```

- `kind`：`run` = `create_run_workout` 建的；`track` = `upload_workout` 传的结构化课。
  两个脚本共用一个文件，靠它区分同名课。
- `fp` = **内容指纹**：对「实际传给工具的参数字典」做规范化 JSON 后取 sha256 前 16 位
  （`minutes` 这类派生值先解析再算）。**名字不是身份**——改名不重要，改内容才重要。
- **v1 迁移**：v1 是扁平的 `课名 → id`。加载时按值类型识别并归一化为 `fp=None`。
  `fp=None` 的条目**不会盲目重建**：脚本会去 Garmin 取回那节课，**内容对得上就照收**
  （并补写指纹），对不上才重建。所以升级不会白折腾一遍手表。

**每次推送的行为**（`--dry-run` 只打印、不写）：

| 判定 | 条件 |
|---|---|
| `create` | registry 里没有这节课 |
| `reuse` | 课还在 Garmin 上，**且内容与本次要建的一致** |
| `replace` | 课不在 Garmin 了，**或内容不一致**（含"手表上被手工改过"） |

`replace` 的顺序是 **建新课 → 排新课 → 删旧课**（先建后删，中途失败也不会把手表弄空；
旧课被删时其日历条目自动消失）。**只比语义**（时长、心率靶、步骤结构），
**不比 description**——描述由服务端生成，比它会导致每次推送都重建。

排期后脚本会**回读日历**校验（`get_scheduled_workouts`）——这是"改动真的到手上了"的证据。
Garmin 日历是**最终一致**的，紧随一次"建+删"之后可能仍显示旧课，所以回读带重试。

- 运行时产物，**只存在于跑者私有工作区**（gitignored），仓库只放虚构示例。
- 任何一课失败（建课/排期/删旧课）都会让脚本**非零退出**，并逐条列出。
- 实现见 `scripts/workout_registry.py`。

## 4b. 健康基线 `garmin_wellness.json`

`scripts/garmin_wellness.py` 的产物：把周复盘要用的**客观基线**一次拉齐——
静息心率 · 睡眠 · HRV · 体重/体成分 · 训练状态。

```json
{
  "schema_version": 1,
  "generated_at": "2026-09-19T16:00:00",
  "range": {"start": "2026-09-14", "end": "2026-09-19", "days": 6},
  "advisory": "纯客观取数：本文件不含任何红黄灯判定、阈值或建议。",
  "days": [
    {"date": "2026-09-16",
     "resting_hr":         {"state": "ok", "bpm": 44.0},
     "sleep":              {"state": "ok", "data": { }},
     "hrv":                {"state": "ok", "data": { }},
     "training_status":    {"state": "ok", "data": { }},
     "training_readiness": {"state": "no_data", "detail": "No training readiness data found for 2026-09-16"}}
  ],
  "body_composition": {"state": "ok", "start_date": "…", "end_date": "…",
                       "logged_days": 0, "data": { }},
  "errors": [{"date": "…", "metric": "training_readiness",
              "state": "no_data", "detail": "…"}]
}
```

**读法（三条硬约定）**：

1. **`state` 是取数状态，不是跑者状态**：`ok` / `no_data` / `error`。
   **`no_data` ≠ 0** —— Garmin 对"当天没记录"返回 `{"error": false, "raw": "No … data found …"}`，
   脚本记为 `no_data` 并保留原文，**绝不写 0 冒充测量值**。`body_composition.logged_days: 0`
   同理（本案跑者从未称重）。
2. **`state` 这个名字是故意的**：Garmin 自己的 hrv / training_status 载荷里**自带 `status` 字段**
   （如 `BALANCED`），原样透传在 `data` 里，不能被覆盖。
3. **只归一化静息心率**（`resting_hr.bpm`，从 `WELLNESS_RESTING_HEART_RATE` 提出来）；
   其余 payload **原样透传**，上游改字段名不会静默改变语义。

**这份文件不判灯。** 静息心率是**目前唯一**进了安全层的生理客观指标（docs/06 §3：连续 2 天比
基线 +8 bpm → 黄灯）；睡眠 / HRV / 训练负荷**目前只是信息项**。是否让它们参与判定是 Roadmap
的未决项，硬约束是**只许加严**——在定案前，agent 不得据此触发或放宽任何红黄灯。

- 运行时产物，**只存在于跑者私有工作区**（gitignored）；且**含健康数据**：
  `.gitignore` 已单列 `data/garmin_wellness.json`，不要把它当可提交的示例。
- 日期是 Garmin 账户本地日历日（UTC+8，与跑者时区一致）；**睡眠归属醒来的那天**。

## 5. 私有 vs 仓库

仓库只提交：schema、`week_spec.example.json`、虚构示例。任何**真实**的 `Activities.csv`、`inbox/*.csv`、registry、健康基线 JSON、runner profile 都在跑者私有工作区（建议放 `workspace/`，已 gitignore），绝不进 git。

## 6. 数据坑清单（分析时必须遵守）

1. **米 vs 公里**：历史行可能有距离以米为单位（>100 判为米）→ `/1000`。
2. **判强度用"移动配速"，不用整场平均**：间歇课的休息 lap（可慢到 45:10/km）会严重拉低均值。
3. **区间课 vs 连续跑不可直接比**：整场平均值只在同类型课之间比较。
4. **对比要同条件**：同距离 + 同温度 + 相近心率、且为连续跑，才有意义。
5. **步频看单圈**，不看整场"平均步频"（休息段被一起平均）；FIT 文件里 cadence 是单腿数值 → ×2。
6. **力量 CSV 有幽灵行/组**：用"次数×重量 + 组间休息列"交叉校验，别直接数行。
7. **抱石/攀岩**：`时长`＝整场；`移动时长`＝0（明细不含观察/休息）。
8. 主表是"应有清单"：分析周完成度时以主表为真值来源，逐次明细只用于还原执行细节。
9. **力量日的跑步机热身没有距离**：跑步机的锻炼模式**不提供距离字段**，热身跑不会以
   "跑步"活动的形式落到 Garmin（只会留下一条"力量训练"记录，`距离km` 为空）。
   - **后果**：Garmin 侧的周跑量**系统性少算**这个固定量（本案为每次 2 km × 每周 2 次 ≈ **4 km**）。
   - **口径**：该值**只能由跑者口述**，是**估算而非测量**。写进计划/日志时必须标注「口述估算」，
     且**不得参与任何精确计算**（VDOT 反推、配速统计、心率漂移对比）。
   - **复盘**：算周完成度时把口述量**单列一行**，不要直接并进 Garmin 求和——
     否则"计划 vs 实际"两侧口径不一致（计划含它、实际不含它，或反之）。
10. **换传感器 = 换标尺；混来源时信配件**：触地时间 / 垂直振幅 / 步长 / 步频 这类字段**腕式手表自己也产**——
    字段"有值"**不等于**跑者戴了配件。配件（心率带 / 跑步动态传感器·跑步豆 / 功率计）与腕式的
    **读数标尺不同**，实测同一跑者、同配速、同心率下两者可差 **5–10%**（触地时间、垂直振幅都是）。
    - **后果**：**配件启用的那一天是曲线的断点**，跨断点画趋势会凭空看出"跑姿突变"。
      做趋势只能**组内比较**（同为腕式、或同为配件），并把断点日期写进日志/复盘留痕。
    - **混来源怎么取舍**（**只在跑者"有配件、且数据里带/不带混着"时才需要判断**；**只有手表**
      或**只有配件**的跑者**不适用**——全程单一来源，偏差恒定，趋势照样成立，
      不要给它加"低置信"之类的噪音标注）：
      - **跨来源不做对比**：趋势、心率漂移、效率一律只在**同来源**的活动之间比（同上一条）；
      - 两者冲突、必须取舍时，**倾向相信带配件的那份**——**心率**尤其如此（光电腕式在间歇/高强度、
        心率快速变化时不可靠）；
      - **HR 锚点（HRmax、乳酸阈心率）用带测**；已有锚点若来自无带数据 → 算**待复核**，
        不能当成既成事实去定区间。
    - **怎么判断有没有戴配件**（别只看字段有无）：
      - **配件独有字段**：心率带 → `groundContactBalanceLeft`（左右平衡）· `avgRespirationRate`
        （呼吸率）· `avg_stance_time_percent`（着地时间占比）；这三项腕式不产生，是最省事的判据。
      - **FIT `device_info` 里出现 `source_type=antplus` 的配对设备**（带 `serial_number`）——
        这是**最硬的证据**，比 summary 字段可靠（第三方 ANT+ 带也认得出）。
      - 两者都拿不到时**直接问跑者**：戴了什么配件、从哪天开始、哪几次漏戴。
    - **用法**：左右平衡盯**单侧**伤病信号（两侧差值 ≥1pp 才提示不对称）；触地时间/垂直振幅看
      **疲劳末段**的跑姿漂移；呼吸率看通气适应。一律**分段（前/中/后 1/3）**比，
      整场均值会被间歇课的休息段污染（见第 2 条）。
    - 该配件信息应记在跑者档案的 `devices` 字段（docs/08 §1）。
