# data/vdot — VDOT 规范数据表 / canonical VDOT tables

Two tidy tables used by `scripts/vdot.py`, docs/09 and the coach skills for pace
prescription. Tidy (long) format is friendly to scripts, agents and diffs.

两份长表，供 `scripts/vdot.py`、docs/09 与教练 skill 查配速用。

| file | schema | purpose |
|---|---|---|
| `vdot_races.csv` | `vdot,distance_m,seconds` | equivalent race time per VDOT → derive VDOT from a result |
| `vdot_paces.csv` | `vdot,intensity,distance_m,seconds` | training time per VDOT per intensity (E/M/T/I/R) per distance |
| `intensity_points.csv` | `pct_vdot,points_per_min` | Daniels intensity points (book Table 5-4): points per minute at a given %VDOT |
| `session_prescriptions.csv` | `points,vdot_lo,vdot_hi,quality,presc_key,amount` | Daniels session construction (book Table 5-5): max amount per quality in a session worth N points |

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

## Provenance of the intensity-points and session tables / 强度点数表与课表来源

`intensity_points.csv` transcribes the training-intensity scoring table (Chinese edition
Table 5-4, "训练强度记录表"): points earned per minute of running at each %VDOT.
`session_prescriptions.csv` transcribes the session-construction table (Chinese edition
Table 5-5, "不同分数的训练记录表"): for a session worth 10/15/20/25/30 points, the maximum
amount (km for L/M/T/I, rep count for R) of each quality a runner of a given VDOT bracket
should attempt. Zone brackets of Table 5-4 for reference: E 59–74, M 75–84, T 83–88,
10K 89–94, I 95–100, R 105–120 (%VDOT; M/T overlap 83–84 with identical values).
%VDOT 101–104 is not printed in the book — `vdot.py` interpolates across the gap and
clamps outside 59–120.

Both files were transcribed from the user's local xlsx of the book's tables; the scanned
xlsx is **not committed** (copyrighted book content, `.gitignore`d). The simplified
per-minute anchors quoted in the book (E 0.2 / M 0.4 / T 0.6 / 10K 0.8 / I 1.0 / R 1.5)
remain valid quick estimates — the graded table is authoritative.

### `session_prescriptions.csv` column semantics / 课表列语义

The book column header is `quality + shared time cap + rep distance`; in the source
image the time caps are merged cells spanning several columns (same intensity ⇒ same
time), so per-column caps are NOT authoritative and are deliberately not encoded here.
A row's `amount` is:

- `quality=L|M`, `presc_key=km` — total kilometres of a continuous run;
- `quality=T`, `presc_key=km` — total T kilometres (≈ 1 km reps);
- every other row — **maximum repetition count** of the distance named in `presc_key`
  (`reps_400m`, `reps_800m`, `reps_1000m`, `reps_1200m`, `reps_1600m`, `reps_200m`,
  `reps_600m`) at that quality's pace. The 15/20/25/30-point tables include an
  `R`/`reps_1600m` column that the 10-point table does not have.

Verified against the book's worked example: VDOT 52 → 10-point L run = 10.4 km
(bracket `51,55`), T total 4 km = 10 points; and for each rep column,
`amount × rep distance × pace ≈ the column's shared time cap`, which is how the column
layout (including the extra `R`/`reps_1600m` column) was reconstructed.

Source quirks (transcribed verbatim, do not "fix"): two cells printed as `5+` / `6+`
(meaning "at least") are stored as `5` / `6`; the M column is non-monotone across point
levels (e.g. 15-point cap 12 km > 20-point cap 10.4 km at VDOT 51–55) exactly as printed
in the source table.

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
