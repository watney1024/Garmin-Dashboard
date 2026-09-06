# 09 · VDOT：成绩 → 训练配速（写给 AI agent）

## 1. 概念与数据

**VDOT**（Jack Daniels 体系）把一次全力以赴的成绩换算成"跑步能力指数"，再用它查**各训练
强度的配速/时间**。来源：Jack Daniels, *Daniels' Running Formula*。

本仓库使用**两张规范数据表**（位于 `data/vdot/`，均为 tidy 长表）：

| 文件 | 行格式 | 用途 |
|---|---|---|
| `data/vdot/vdot_races.csv` | `vdot, distance_m, seconds` | **成绩 → VDOT**：在标准距离列里找等效成绩 |
| `data/vdot/vdot_paces.csv` | `vdot, intensity, distance_m, seconds` | **VDOT → 训练时间/配速**（E/M/T/I/R × 各距离） |

- VDOT 30–85，整数行；非整数由 `scripts/vdot.py` 在相邻行间**线性插值**。
- 半马/马拉松距离以米存（`21097.5` / `42195`）。
- ⚠ **许可**：表数据派生自一个 **GPL-3.0 授权**的 VDOT 导出（项目名/链接待补，见
  `data/vdot/README.md` 与 `NOTICE.md`，完整文本 `data/vdot/GPL-3.0.txt`）。再分发须遵守
  GPLv3；不是直接影印原书表格。

## 2. 强度分区

| 区 | 全名 | 定位 | VDOT40 示例（/km 或 ×距离） |
|---|---|---|---|
| E | Easy | 有氧基础，最大占比 | `6:19`/km（快端参考；跑慢不限） |
| M | Marathon | 马配段 | `5:29`/km |
| T | Threshold | 乳酸阈值（巡航间歇/持续） | `5:06`/km（T/1000 = 1km） |
| I | Interval | VO2max 间歇（3–5min 组） | `4:42`/km（I/1000 = 1km） |
| R | Repetition | 短速度/跑姿（200–400m，充分恢复） | 400m ≈ `1:46` |

> 表中"R/km"由 R 距离换算仅为展示；课表引用 R 时用**对应距离时间**（如 R/400 106s）。

## 3. 执行口径（重要）

- **低强度（E/恢复）**：心率/体感是唯一权威，时间兜底。`E/km` 表值只是**快端参考下限**，
  轻松跑跑得更慢永远允许。天热/没睡好/疲劳全切"心率模式"。
- **高质量（M/T/I/R/比赛段）**：以表值为准给区间；距离定负荷，心率当警报。
- VDOT 更新前，训练配速一律用**当前** VDOT 的查表值，不用目标 VDOT。

## 4. 怎么用（`scripts/vdot.py`）

```bash
# 成绩 → VDOT（标准距离：查 vdot_races 表）
python scripts/vdot.py --5k 23:45
python scripts/vdot.py --race-time 1:52:30 --distance half
# VDOT → 训练配速/时间 + 等效成绩（vdot_paces / vdot_races）
python scripts/vdot.py --vdot 40
python scripts/vdot.py --vdot 40 --json
```

- 标准距离名：`1500 1mile 3000 2mile 5k 8k 5mile 10k 15k 10mile 20k half 25k 30k marathon`。
- 非标准距离（如 6k）走**经典跑氧公式兜底估 VDOT**；训练配速仍来自表（插值）。
- 例（VDOT≈40）：E 6:19 / M 5:29 / T 5:06 / I 4:42 / R400≈106s；等效 5K 24:08 / 10K 50:03 /
  半马 1:50:59 / 全马 3:49:45。

## 5. 从档案 PR 推 VDOT（docs/08 的配套规则）

1. 取 `pr` 中最近 6 个月、最可信的成绩，用 `vdot.py` 求 VDOT。
2. 其余成绩交叉验证：应相差 ≤1；差 >1 以最近且全力以赴者为准，向跑者说明。
3. 多个不同距离成绩可选**按目标加权**（如以全马为目标时全马权重更高）——这是 TODO 项，
   当前取"最可信最近一个"。
4. A/attempt 赛后写回新成绩 → 重算 VDOT；变化 ≥1 经周复盘提议更新配速。

## 6. 备注

- 表格数值来自第三方 GPL-3.0 导出，个别行可能与 Daniels 原书印刷表有 1–2 s 级差异；若你
  拿到可直接授权/公有领域的权威版本，替换 `data/vdot/*.csv` 即可（格式保持 tidy）。
- agent 报告配速时注明出处（如"data/vdot 表，VDOT40"），不要声称是原书逐值。
