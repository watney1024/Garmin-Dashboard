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

The packages under `coaches/` are **our own summaries and application guides** written from
public descriptions of well-known training methodologies. They are not reproductions of the
source books. Where applicable the source of inspiration is credited in each package:

- Jack Daniels, *Daniels' Running Formula* (丹尼尔斯经典跑步训练法)
- Matt Fitzgerald, *80/20 Running*（80/20 跑步法）
- Luke Humphrey / Hanson's Marathon Method（汉森马拉松训练法）
- Pete Pfitzinger & Scott Douglas, *Advanced Marathoning*（中文版《你可以跑得更快》）
- Jack Daniels' **VDOT** concept and pace tables — the table shipped at
  `data/vdot_table.csv` is an **approximation** derived from publicly described relations,
  *not* the copyrighted original tables (see `docs/09_vdot_paces_zh.md`, marked TODO to be
  replaced by an authoritative source supplied by a contributor).

## Examples / 示例

Everything under `examples/` is **fabricated** synthetic data about a fictional runner
("Example Runner / 示例跑者"). It is released CC0 and contains no real person's data.

## No warranty / 免责

Training advice in this repository is informational only and does not replace professional
medical advice. Running can cause injury; the red-line and injury rules exist to reduce
risk, not to guarantee safety. Consult a doctor for persistent or unilateral pain.
