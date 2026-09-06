# scripts / 脚本

Stdlib-only Python utilities. Configure via CLI flags / env vars — never edit the
scripts to change behaviour. 纯标准库；通过命令行参数或环境变量配置，不要改代码。

| Script | Purpose | 用途 |
|---|---|---|
| `garmin_pull.py` | rebuild the 16-column master CSV + download per-activity detail CSVs through garmin-mcp | 拉数据重建主表与单次明细 |
| `garmin_schedule.py` | create & schedule a week's run workouts to Garmin (idempotent) | 把周课表排进 Garmin 日历 |
| `vdot.py` | race result → VDOT → training pace bands; also regenerates `data/vdot_table.csv` | 成绩转 VDOT 与各强度配速 |

Environment variables (see `.env.example` and `docs/01_mcp_setup_zh.md`):
`GARMIN_MCP_SRC` (required for the two Garmin scripts), `UVX_BIN`,
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

# VDOT lookups
python scripts/vdot.py --5k 23:45
python scripts/vdot.py --race-time 1:52:30 --distance half
python scripts/vdot.py --gen-csv data/vdot_table.csv   # regenerate the table
```

Data schemas are documented in `docs/02_data_schema_zh.md`. The files produced
under the data dir (master CSV, inbox CSVs, registry JSON) are runtime artifacts
for the runner's private workspace and must not be committed.
