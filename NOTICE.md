# NOTICE

This project includes or references the following third-party material. All trademarks and
book titles belong to their respective owners.

## External dependency (referenced, not vendored / 外部依赖，未内置)

- **garmin-mcp** — [`Taxuspt/garmin_mcp`](https://github.com/Taxuspt/garmin_mcp),
  MIT License (c) 2025 Alexandre Domingues. The scripts in `scripts/` spawn it over MCP
  stdio; no code from it is copied into this repository. For Garmin Connect **China**
  accounts (no proxy), upstream open PR
  [`#249`](https://github.com/Taxuspt/garmin_mcp/pull/249) "fix(auth): support Garmin
  Connect China accounts" by lewobx is required until merged — see `docs/01_mcp_setup_zh.md`.

## Coach methodology packages (summaries only / 教练理念包，仅概括)

The skills under `.agents/skills/` are **our own summaries and application guides** written from
public descriptions of well-known training methodologies. They are not reproductions of the
source books. Where applicable the source of inspiration is credited in each package:

- Jack Daniels, *Daniels' Running Formula* (丹尼尔斯经典跑步训练法)
- Matt Fitzgerald, *80/20 Running*（80/20 跑步法）
- Luke Humphrey / Hanson's Marathon Method（汉森马拉松训练法）
- Pete Pfitzinger & Scott Douglas, *Advanced Marathoning*（中文版《你可以跑得更快》）
- Arthur Lydiard, *Running to the Top*（莱迪亚德训练体系）

## VDOT tables data / VDOT 表数据（GPL-3.0）

`data/vdot/vdot_paces.csv` and `data/vdot/vdot_races.csv` are converted from the VDOT
tables of

> **VDOT Calculator** by Zac Blanco — <https://github.com/ZacBlanco/vdot> ·
> <https://vdot.blanco.io> — **GPL-3.0**

We only re-shaped the export (wide → tidy, distances to metres, times to seconds); the
numeric values are unchanged. Redistribution of these files follows the GPL-3.0 terms
(full text: `data/vdot/GPL-3.0.txt`; notes: `data/vdot/README.md`).

## Book-table-derived data / 书表衍生数据

`data/vdot/intensity_points.csv` and `data/vdot/session_prescriptions.csv` transcribe
functional tables from the Chinese edition of Jack Daniels' *Daniels' Running Formula*
(Table 5-4 "训练强度记录表" and Table 5-5 "不同分数的训练记录表"). They are factual
points/caps tables transcribed by hand; the scanned book pages stay out of the repository.
All trademarks and book titles belong to their respective owners.

## Examples / 示例

Everything under `examples/` is **fabricated** synthetic data about a fictional runner
("Example Runner / 示例跑者"). It is released CC0 and contains no real person's data.

## No warranty / 免责

Training advice in this repository is informational only and does not replace professional
medical advice. Running can cause injury; the red-line and injury rules exist to reduce
risk, not to guarantee safety. Consult a doctor for persistent or unilateral pain.
