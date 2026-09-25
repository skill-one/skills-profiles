# Agent Pulse

## Purpose

以已安装的 `agent-pulse` CLI 作为本地 AI 代理活动的权威来源。PyPI 包名为 `agentpulse-cli`，命令仍为 `agent-pulse`。优先通过执行命令并总结其输出，而非阅读 Agent Pulse 源代码。

在 Windows 上运行命令前，请务必启用 UTF-8，因为 Agent Pulse 的输出包含 emoji 和方框绘制字符：

```powershell
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'
```

如果 `agent-pulse` 不在 PATH 中，请在安装依赖前先询问用户。若用户同意，可安装 PyPI 包，或尝试从本地项目仓库运行：

```powershell
pip install agentpulse-cli
```

```powershell
python -m agent_pulse.cli --version
```

## Source Keys

当用户询问某个代理工具而非全部本地数据时，使用 `-P/--platform` 选项：

```
hermes, claude, codex, deepseek, openclaw, copilot, aider, qwen,
opencode, goose, cursor, antigravity, amp
```

## Choose Commands

首先使用以下命令选择表：

| 用户需求 | 执行命令 |
|---|---|
| 查看当前状态 | `agent-pulse status --json` |
| 查看完整面板 | `agent-pulse --json` 或 `agent-pulse --no-banner` |
| 获取演示数据 | `agent-pulse demo --json` |
| 设置诊断 | `agent-pulse doctor --json` |
| 查看最近会话 | `agent-pulse --json --hours 24 --limit 20` |
| 会话排行 | `agent-pulse top --sort tokens --json` |
| 查看最昂贵的会话 | `agent-pulse top --sort cost --json --hours 168` |
| 模型成本分析 | `agent-pulse models --json` |
| 模型排名 | `agent-pulse leaderboard --json --rank-by efficiency` |
| 成本优化 | `agent-pulse optimize --json` |
| 预算状态 | `agent-pulse budget --json` |
| 成本预测 | `agent-pulse forecast --json` |
| 成本异常检查 | `agent-pulse anomaly --json` |
| 健康/CI 检查 | `agent-pulse health --json` |
| 综合评分 | `agent-pulse score --json` |
| 会话搜索 | `agent-pulse search "<query>" --json` |
| 周期对比 | `agent-pulse compare --json` |
| 项目对比 | `agent-pulse compare-projects --json` |
| 活动日历 | `agent-pulse heatmap --json` |
| 智能建议 | `agent-pulse insights --json` |
| Prometheus 指标 | `agent-pulse metrics --format prometheus` |
| 导出报告 | `agent-pulse export -f markdown` 或 `agent-pulse export-html` |
| Web 面板 | `agent-pulse web --port 8765` |
| REST API | `agent-pulse api --port 8766` |
| MCP 工具 | `agent-pulse mcp --list-tools` |

若已安装的命令缺少选项，请运行 `agent-pulse <command>` `--help` 并进行适配。

## Workflow

1. 仅当用户询问数据缺失的原因、请求设置帮助，或普通数据命令返回无会话时，才以 `agent-pulse doctor --json` 开始。
2. 尽可能使用 JSON 输出。总结重要的字段：会话、代币（tokens）、工具、搜索调用、模型细分、来源细分、估算成本、警告信息。
3. 针对限定范围的问题，使用时间过滤器。对于“最近”，默认使用 24 小时；“本周”默认使用 168 小时：

```powershell
agent-pulse status --json --hours 24
agent-pulse --json --hours 168 --limit 50
```

4. 当用户询问特定代理系统时，使用平台过滤器：

```powershell
agent-pulse --json -P codex --hours 24
agent-pulse --json -P claude --hours 24
agent-pulse top --json -P aider --sort cost
agent-pulse status --json -P cursor
```

5. 针对成本问题，结合摘要、模型和会话排行视图：

```powershell
agent-pulse status --json --hours 24
agent-pulse models --json --hours 24
agent-pulse top --sort cost --json --hours 24
agent-pulse optimize --json --hours 168
```

6. 针对趋势和风险问题，使用预测/历史/对比/异常检查：

```powershell
agent-pulse forecast --json
agent-pulse history --json
agent-pulse compare --json
agent-pulse anomaly --json
```

7. 针对设置，在猜测路径之前，使用发现命令：

```powershell
agent-pulse doctor --json
agent-pulse scan --json --details
agent-pulse config show
```

## Interpreting Results

- 将 `total_cost_usd` 视为基于 Agent Pulse 本地模型定价表估算的成本。
- 同时报告成本和代币用量；低成本模型仍可能有极高的代币使用量。
- 区分 `codex`、`claude`、`hermes`、`deepseek`、`openclaw`、`aider`、`cursor`、`opencode` 和 `goose` 等来源。
- 若 `doctor` 报告存在缺失的可选来源、缺失的 `dev_root`，或可选的网页依赖，请予以提及。
- 如果没有出现任何会话，请检查 `doctor`，然后尝试更宽的时间窗口，如 `--hours 168`。
- 在给出总体总计之前，先检查用户是否要求了来源（`-P`）过滤器、模型过滤器或项目对比。
- 如果命令输出纯文本而非 JSON，或因已安装版本过旧而失败，请运行 `agent-pulse <command>` `--help`，并使用最接近的受支持选项。

## Reports

对于简短的人类可读回答，运行 JSON 命令并加以总结。

对于生成产物，优先使用：

```powershell
agent-pulse report --period daily
agent-pulse export -f markdown
agent-pulse export-html
```

不要虚构具体的节省金额或成本。请使用 CLI 输出。

## Integrations

仅在用户要求浏览器面板或程序化服务器时，才使用 web 和 API 额外功能。在安装缺失的额外功能前请先询问用户：

```powershell
pip install "agentpulse-cli[web]"
agent-pulse web --port 8765
agent-pulse api --port 8766
```

用于监控流水线：

```powershell
agent-pulse metrics --format prometheus
agent-pulse health --cost-limit 100 --token-limit 1000000 --json
```

## MCP

当用户希望其他 AI 客户端查询 Agent Pulse 时，使用 MCP 模式：

```powershell
agent-pulse mcp --list-tools
agent-pulse mcp
```

在解释 MCP 时，提及它暴露了如 status、forecast、top sessions、model analytics、optimization、health、search 和 leaderboard 等工具。

## Local Helper

本技能包含 `scripts/run_agent_pulse_snapshot.py`，用于运行一组精简的、易于输出 JSON 的 Agent Pulse 检查，并打印合并的总结：

```powershell
python scripts/run_agent_pulse_snapshot.py --hours 24 --days 7
```
