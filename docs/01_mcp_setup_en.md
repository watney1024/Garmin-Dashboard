# 01 · MCP & the Garmin data pipeline (for AI agents)

Pipeline: **Garmin Connect → garmin-mcp (MCP stdio) → this repo's scripts → canonical
files** (master `Activities.csv` + per-session `inbox/activity_<id>.csv`). This document
shows agents/users how to install garmin-mcp and configure the scripts.

## 1. Dependency: garmin-mcp (referenced externally, not vendored)

- Upstream: `Taxuspt/garmin_mcp` (MIT License). The `scripts/*.py` launch it in a child
  process via `uvx --from <source> garmin-mcp` and talk **MCP over stdio** JSON-RPC
  (initialize → notifications/initialized → tools/call). This repo **does not contain**
  garmin_mcp code.
- `uv`/`uvx` must be installed (scripts call `uvx` from PATH by default; override with
  `UVX_BIN`).

### A. Garmin Connect China account (CN, no proxy)

> Upstream PR #249 (`fix(auth): support Garmin Connect China accounts`, author lewobx) is
> the **required fix for no-proxy CN authentication** until it is merged. `main` hard-codes
> `*.com` endpoints for token exchange, which gets TLS-reset in China.

Install (local clone, stay on pr-249):
```bash
git clone https://github.com/Taxuspt/garmin_mcp.git
cd garmin_mcp
git fetch origin pull/249/head:pr-249
git checkout pr-249            # needs Python 3.12+ (this PR pulls garminconnect 0.3.4)
```

First-time auth (terminal, interactive: email code/password):
```bash
# run from the garmin_mcp directory, using this clone as the uvx source
uvx --python 3.12 --from <garmin_mcp dir> garmin-mcp-auth --is-cn
```
- Tokens live in `~/.garminconnect`, valid ~6 months; re-run auth to refresh.
- If upstream later merges PR #249, switch back to the official release — this file /
  `NOTICE.md` will point out the check.

### B. International account (non-CN)

Same clone, but stay on `main` (or the official release); authenticate **without**
`--is-cn` and leave `GARMIN_IS_CN` unset.

## 2. Script environment variables (`scripts/garmin_*.py`)

| variable | meaning | default |
|---|---|---|
| `GARMIN_MCP_SRC` | garmin-mcp source (local clone path or package spec); **required** | none (exit with error pointing here) |
| `UVX_BIN` | path to the uvx executable | `uvx` (from PATH) |
| `GARMIN_MCP_PYTHON` | python version for the uvx env | `3.12` |
| `GARMIN_IS_CN` | set `true` for China accounts | inherited from env |
| `UV_DEFAULT_INDEX` | optional pip index for CN networks | inherited from env |
| `GARMIN_DATA_DIR` | output dir (master/inbox/registry/wellness live under it) | `./data` |

A `.env` file at the repo root or next to the script is auto-loaded (see
`.env.example`); **real tokens/passwords never go into `.env` or git.**

Usage:
```bash
export GARMIN_MCP_SRC=/path/to/garmin_mcp
export GARMIN_IS_CN=true            # China account
python scripts/garmin_pull.py --master-only          # rebuild the master only
python scripts/garmin_schedule.py scripts/week_spec.example.json --dry-run
python scripts/garmin_wellness.py --since 2026-09-14 --until 2026-09-20   # wellness baseline
```

## 3. MCP tools (agents may call them directly, or via the scripts)

> **Note: the tool count is far larger than this list.** On the PR #249 branch, `tools/list` returns **100+ tools**, plus 5
> `resources` (`workout://templates/*` and `workout://reference/structure` — the latter
> carries the full workout-DTO id mapping, e.g. `endCondition` 1=lap.button / 2=time /
> 7=iterations). The table below is what this repo **actually depends on**; **call `tools/list`
> yourself for anything else** rather than assuming there are only a few.

| tool | params (example) | purpose |
|---|---|---|
| `get_activities` | `{start, limit:100}` (paginate full list) | rebuild the master table |
| `download_activity_file` | `{activity_id, format:"csv", output_dir}` | download per-session detail |
| `set_activity_name` | `{activity_id, activity_name}` | batch-rename Garmin titles (title governance) |
| `create_run_workout` | `{name, run_seconds, warmup_min, cooldown_min, hr_min, hr_max}` | create a **continuous** run workout |
| `upload_workout` | `{workout_data}` | create a workout of **any structure** (intervals, lap-button steps; DTO see `workout://reference/structure`) |
| `get_workouts` / `get_workout_by_id` | `{}` / `{workout_id}` | list the library / read one workout's structure |
| `schedule_workout` | `{workout_id, calendar_date}` | schedule onto a date |
| `unschedule_workout` | `{scheduled_workout_id}` | remove from the calendar (**use `scheduled_workout_id`, not `workout_id`**) |
| `delete_workout` | `{workout_id}` | delete a workout; its calendar entry disappears with it |
| `get_scheduled_workouts` | `{start_date, end_date}` | read the calendar |
| `get_rhr_day` / `get_sleep_summary` / `get_hrv_data` / `get_training_status` / `get_training_readiness` | `{date}` (**single date**; loop per day for a range) | wellness baseline: resting HR · sleep · HRV · training status. Wrapped by `scripts/garmin_wellness.py`; output schema in `docs/02 §4b` |
| `get_body_composition` | `{start_date, end_date}` (**a range**, unlike the row above) | weight / body composition |
| `get_lactate_threshold` | `{start_date, end_date}` | lactate threshold (for the profile and the safety layer) |
| `get_user_profile` | `{}` | runner profile (sex · birthday · height/weight, …) |

If you configure MCP in a desktop agent (Claude Desktop / CodeBuddy, …), point that
server at the same garmin-mcp source (pr-249 branch for CN) with `GARMIN_IS_CN=true`; the
config only affects that client — token location is unchanged.

## 4. Security

- Run locally only; the MCP server does not expose a port.
- Tokens (`~/.garminconnect`), any `mcp.json` approval files and passwords never enter the
  repo (already in `.gitignore`).
- Scripts are read-only against the account except explicit write ops the runner asked for
  (create/schedule workouts, rename titles).

## 5. Troubleshooting

- **CN auth fails / TLS reset**: confirm the pr-249 branch + Python ≥3.12; auth succeeded
  but later calls return 401 → the token may be an old format; delete `~/.garminconnect`
  and re-authenticate.
- **`uvx` not found**: install uv, or point `UVX_BIN` at it.
- **Slow installs**: on CN networks set `UV_DEFAULT_INDEX` to a mirror (optional).
- **Token expiry**: ~6 months; re-run the auth command.
- **Scripts hang**: try `--dry-run` / `--master-only` first, then run
  `uvx ... garmin-mcp` manually and watch stderr.
