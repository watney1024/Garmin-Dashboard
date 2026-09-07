# data/vdot — VDOT 规范数据表 / canonical VDOT tables

Two tidy tables used by `scripts/vdot.py`, docs/09 and the coach skills for pace
prescription. Tidy (long) format is friendly to scripts, agents and diffs.

两份长表，供 `scripts/vdot.py`、docs/09 与教练 skill 查配速用。

| file | schema | purpose |
|---|---|---|
| `vdot_races.csv` | `vdot,distance_m,seconds` | equivalent race time per VDOT → derive VDOT from a result |
| `vdot_paces.csv` | `vdot,intensity,distance_m,seconds` | training time per VDOT per intensity (E/M/T/I/R) per distance |

- VDOT rows 20–85 (integers). `vdot.py` linearly interpolates for non-integer VDOT.
- Half/marathon distances are stored as metres (`21097.5` / `42195`).
- A missing (intensity, distance) cell in the source simply has no row (low-VDOT rows carry
  fewer cells — long I/R reps are not prescribed to beginners).

## Provenance of the VDOT 20–29 rows / 低分段（VDOT 20–29）的来源

The GPL-3.0 export upstream covers VDOT 30–85 only. The beginner rows (20–29) were added
locally:

- `vdot_paces.csv` — R/I/T/M cells follow the beginner table in the Chinese edition of
  Daniels' *Running Formula* (its Table 5-3, "适用于初跑者"); at low VDOT that table uses
  deliberately gentler I/R intensities (≈93–95% instead of 97–100%), which we keep for
  beginner safety. Cells the book does not print (E, T/800) were computed from the classic
  Daniels running-economy equations (the same formulas in `scripts/vdot.py`); M per-mile is
  the book M/km pace scaled.
- `vdot_races.csv` — computed from the classic equations, anchored to the existing VDOT-30
  row of each distance (`t(V,d) = t(30,d) × T_formula(V,d) / T_formula(30,d)`) so the table
  stays continuous at VDOT 30. Cross-checked against the beginner table (mile within 0–2 s;
  5k within 14 s at VDOT 20, i.e. the integer-VDOT point of the formula).

The scanned xlsx used as cross-check is **not committed** (copyrighted book content; kept
out of the repo via `.gitignore`).

## Origin & license / 来源与许可

These data files were converted from the VDOT tables of

> **VDOT Calculator** by Zac Blanco — https://github.com/ZacBlanco/vdot ·
> https://vdot.blanco.io — **GPL-3.0**

They were re-shaped from wide to tidy (column names, distances normalised to metres,
times to seconds); numeric values are unchanged. Redistribution follows the GPL-3.0
terms; a full copy is in `GPL-3.0.txt` in this directory. See also `NOTICE.md`.

本数据派生自上述 GPL-3.0 项目的表格，仅重排格式、数值未改；再分发须遵守 GPLv3（本目录
`GPL-3.0.txt` 为完整许可文本）。

## Regenerating / 复现

The export files (`tables/{paces,races}.{csv,json}`) live upstream. If you re-pull them,
convert with the same normalisation (see the conversion notes above) and keep this
README's attribution current. Do not change the tidy schema without updating
`scripts/vdot.py` and docs/09.
