# scripts / 脚本

Stdlib-only Python utilities. Configure via CLI flags / env vars — never edit the
scripts to change behaviour. 纯标准库；通过命令行参数或环境变量配置，不要改代码。

| Script | Purpose | 用途 |
|---|---|---|
| `garmin_pull.py` | rebuild the 16-column master CSV + download per-activity detail CSVs through garmin-mcp | 拉数据重建主表与单次明细 |
| `garmin_schedule.py` | create & schedule a week's run workouts to Garmin (idempotent) | 把周课表排进 Garmin 日历 |
| `garmin_track_workout.py` | build & schedule a **track/interval** session with lap-button steps (watch distance decoupled from the 400 m lap) | 建并排**操场间歇课**（计圈键＝标称距离） |
| `vdot.py` | race result → VDOT → training pace/times; intensity points & N-point session caps (docs/09 §7); `--selfcheck` | 成绩转 VDOT 与配速；强度点数与 N 分课上限；数据自检 |
| `garmin_wellness.py` | pull the **wellness baseline** for a date range (resting HR · sleep · HRV · body composition · training status) — acquisition only, it computes no light/threshold (docs/02 §4b) | 拉**健康基线**（静息心率·睡眠·HRV·体重·训练状态）；只取数、不判灯 |

Environment variables (see `.env.example` and `docs/01_mcp_setup_zh.md`):
`GARMIN_MCP_SRC` (required for the Garmin scripts), `UVX_BIN`,
`GARMIN_MCP_PYTHON` (default 3.12), `GARMIN_IS_CN` (set `true` for China
accounts), optional `UV_DEFAULT_INDEX`, `GARMIN_DATA_DIR` (default `./data`).
A `.env` file in the repo root or next to the script is read if present.

Examples:

```bash
# pull data (needs garmin-mcp installed + authenticated, see docs/01)
python scripts/garmin_pull.py --master-only

# schedule week 1, preview first
python scripts/garmin_schedule.py scripts/week_spec.example.json --dry-run
python scripts/garmin_schedule.py scripts/week_spec.example.json

# track / interval session (lap-button steps), preview first
python scripts/garmin_track_workout.py scripts/track_spec.example.json --dry-run
python scripts/garmin_track_workout.py scripts/track_spec.example.json --print-json

# wellness baseline for the weekly review (default: last 14 days)
python scripts/garmin_wellness.py --since 2026-09-14 --until 2026-09-20

# VDOT lookups (data from data/vdot/; GPL-3.0-derived, see NOTICE.md)
python scripts/vdot.py --5k 23:45
python scripts/vdot.py --race-time 1:52:30 --distance half
python scripts/vdot.py --vdot 40 --json

# intensity points for one effort (moving time; docs/09 §7)
python scripts/vdot.py --points --vdot 48 --time 48:30 --distance 10k
python scripts/vdot.py --points --vdot 48 --pace 4:00 --minutes 40

# per-quality caps for an N-point session (book Table 5-5)
python scripts/vdot.py --session 15 --vdot 52

# validate all data/vdot tables against book anchors
python scripts/vdot.py --selfcheck
```

Data schemas are documented in `docs/02_data_schema_zh.md`. The files produced
under the data dir (master CSV, inbox CSVs, registry JSON, wellness JSON) are runtime
artifacts for the runner's private workspace and must not be committed.
