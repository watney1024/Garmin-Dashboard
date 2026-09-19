# 01 · MCP 与 Garmin 数据管道（写给 AI agent）

数据管道：**Garmin Connect → garmin-mcp（MCP stdio）→ 本仓库脚本 → 规范文件**
（主表 `Activities.csv` + 单次明细 `inbox/activity_<id>.csv`）。本文档教 agent/用户装好
garmin-mcp 并配置脚本。

## 1. 依赖：garmin-mcp（外部引用，未内置）

- 上游：`Taxuspt/garmin_mcp`（MIT License）。`scripts/*.py` 通过 `uvx --from <源> garmin-mcp`
  在子进程里启动它并走 **MCP over stdio** 的 JSON-RPC 通信（initialize →
  notifications/initialized → tools/call）。仓库**不含** garmin_mcp 代码。
- 需要本机有 `uv`/`uvx`（脚本默认调 PATH 里的 `uvx`，可用 `UVX_BIN` 覆盖）。

### A. 中国大陆账户（CN，免代理）

> 上游 PR #249（`fix(auth): support Garmin Connect China accounts`，作者 lewobx）在合并前
> 是 **CN 免代理登录的必要修复**。main 分支的 token 交换固定走 `*.com` 端点，在国内会被
> TLS 重置而无法鉴权/续期。

安装（本地 clone，保持 pr-249）：
```bash
git clone https://github.com/Taxuspt/garmin_mcp.git
cd garmin_mcp
git fetch origin pull/249/head:pr-249
git checkout pr-249            # 需要 Python 3.12+（该 PR 会拉取 garminconnect 0.3.4）
```

首次鉴权（终端交互：邮箱验证码/密码）：
```bash
# 在 garmin_mcp 目录内，用该 clone 作为 uvx 源
uvx --python 3.12 --from <garmin_mcp 目录> garmin-mcp-auth --is-cn
```
- token 存 `~/.garminconnect`，约 6 个月有效，到期重跑一次即可。
- 上游若后续合并了 PR #249，可切回官方 release；本文件/`NOTICE.md` 会提示检查。

### B. 国际账户（非 CN）

同上 clone，但留在 `main`（或官方 release），鉴权**不带** `--is-cn`，且不设
`GARMIN_IS_CN=true`。

## 2. 脚本环境变量（`scripts/garmin_*.py`）

| 变量 | 说明 | 默认 |
|---|---|---|
| `GARMIN_MCP_SRC` | garmin-mcp 源（本地 clone 路径或包 spec）；**必需** | 无（缺则报错退出并指向本文档） |
| `UVX_BIN` | uvx 可执行文件路径 | `uvx`（PATH） |
| `GARMIN_MCP_PYTHON` | uvx 环境的 Python 版本 | `3.12` |
| `GARMIN_IS_CN` | CN 账户设 `true` | 继承自环境 |
| `UV_DEFAULT_INDEX` | 可选：中国大陆 pip 镜像 | 继承自环境 |
| `GARMIN_DATA_DIR` | 输出目录（主表/inbox/registry/健康基线 都在其下） | `./data` |

也可在仓库根或脚本旁放 `.env`（参考 `.env.example`）自动加载；**真实 token/密码永不进
`.env` 文件与 git**。

用法：
```bash
export GARMIN_MCP_SRC=/path/to/garmin_mcp
export GARMIN_IS_CN=true            # CN 账户
python scripts/garmin_pull.py --master-only          # 只重建主表
python scripts/garmin_schedule.py scripts/week_spec.example.json --dry-run
python scripts/garmin_wellness.py --since 2026-09-14 --until 2026-09-20   # 健康基线
```

## 3. MCP 工具（agent 可能直接调，或由脚本代调）

> **注意：工具数量远超本文所列。**实测 PR #249 分支的 `tools/list` 返回 **100+ 个**工具，另有 5 个
> `resources`（`workout://templates/*` 与 `workout://reference/structure`——后者含建课 DTO 的
> 完整 ID 映射，如 `endCondition` 1=lap.button / 2=time / 7=iterations）。
> 本仓库**实际依赖**的是下表；**需要什么就自己调 `tools/list` 查**，不要假设只有这几个。

| 工具 | 参数（示例） | 用途 |
|---|---|---|
| `get_activities` | `{start, limit:100}`（分页拉全量） | 重建主表 |
| `download_activity_file` | `{activity_id, format:"csv", output_dir}` | 下载单次明细 |
| `set_activity_name` | `{activity_id, activity_name}` | 批量改 Garmin 端标题（标题治理） |
| `create_run_workout` | `{name, run_seconds, warmup_min, cooldown_min, hr_min, hr_max}` | 建**连续**跑步课 |
| `upload_workout` | `{workout_data}` | 建**任意结构**课（间歇、计圈键等；DTO 见 `workout://reference/structure`） |
| `get_workouts` / `get_workout_by_id` | `{}` / `{workout_id}` | 查课库 / 读单课结构 |
| `schedule_workout` | `{workout_id, calendar_date}` | 排到某天 |
| `unschedule_workout` | `{scheduled_workout_id}` | 撤排（**注意用 `scheduled_workout_id`，不是 `workout_id`**） |
| `delete_workout` | `{workout_id}` | 删课；课被删后其日历条目会自动消失 |
| `get_scheduled_workouts` | `{start_date, end_date}` | 读日历 |
| `get_rhr_day` / `get_sleep_summary` / `get_hrv_data` / `get_training_status` / `get_training_readiness` | `{date}`（**单个日期**；要区间得按天循环） | 健康基线：静息心率·睡眠·HRV·训练状态。`scripts/garmin_wellness.py` 已封装，输出 schema 见 `docs/02 §4b` |
| `get_body_composition` | `{start_date, end_date}`（**区间**，与上一行不同） | 体重/体成分 |
| `get_lactate_threshold` | `{start_date, end_date}` | 乳酸阈（供档案与安全层用） |
| `get_user_profile` | `{}` | 跑者档案（性别·生日·身高体重等） |

若在桌面 agent（Claude Desktop/CodeBuddy 等）里配置 MCP，让该 server 指向同一 garmin_mcp
源（CN 用 pr-249 分支）与 `GARMIN_IS_CN=true`；配置只影响该客户端，token 位置不变。

## 4. 安全

- 只在本机运行；MCP server 不暴露端口。
- token（`~/.garminconnect`）、任何 `mcp.json` 审批文件、密码都不进仓库（.gitignore 已列）。
- 脚本对远端只读（除建课/排课/改标题这类跑者主动要求的写操作）。

## 5. 故障排查

- **CN 鉴权失败/TLS reset**：确认用的是 pr-249 分支 + Python ≥3.12；`--is-cn` 鉴权成功但
  后续调用 401 → token 可能是旧格式，删 `~/.garminconnect` 重鉴权。
- **`uvx` 找不到**：装 uv 或用 `UVX_BIN` 指定。
- **拉取慢**：CN 网络设 `UV_DEFAULT_INDEX` 指向镜像（可选）。
- **token 过期**：约 6 个月；重跑鉴权命令即可。
- **脚本无响应**：先跑 `--dry-run` / `--master-only`，再手动 `uvx ... garmin-mcp` 看 stderr。
