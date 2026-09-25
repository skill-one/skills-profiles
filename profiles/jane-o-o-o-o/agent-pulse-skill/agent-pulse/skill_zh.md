# Agent Pulse

## 目的

使用已安装的 `agent-pulse` CLI 作为本地 AI 代理活动的事实来源。PyPI 包名为 `agentpulse-cli`，而命令保持为 `agent-pulse`。优先运行命令并总结其输出，而不是阅读 Agent Pulse 的源代码。

在运行命令之前，始终在 Windows 上启用 UTF-8，因为 Agent Pulse 输出包含表情符号和框线绘制：

```powershell
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'
```

如果 `agent-pulse` 不在 PATH 中，则在安装依赖项之前询问用户。如果用户同意，则安装 PyPI 包或尝试从本地项目检出运行：

```powershell
pip install agentpulse-cli
```

```powershell
python -m agent_pulse.cli --version
```

## 源键

当用户询问关于单个代理工具而不是所有本地数据时，使用 `-P/--platform`：

```text
hermes, claude, codex, deepseek, openclaw, copilot, aider, qwen,
opencode, goose, cursor, antigravity, amp
```

## 选择命令

首先使用此命令选择表：

| 用户希望 | 运行 |
|---|---|
| 当前状态 | `agent-pulse status --json` |
| 完整仪表板 | `agent-pulse --json` 或 `agent-pulse --no-banner` |
| 演示数据 | `agent-pulse demo --json` |
| 设置诊断 | `agent-pulse doctor --json` |
| 最近会话 | `agent-pulse --json --hours 24 --limit 20` |
| 顶级会话 | `agent-pulse top --sort tokens --json` |
| 最昂贵的会话 | `agent-pulse top --sort cost --json --hours 168` |
| 模型成本分析 | `agent-pulse models --json` |
| 模型排名 | `agent-pulse leaderboard --json --rank-by efficiency` |
| 成本节省 | `agent-pulse optimize --json` |
| 预算状态 | `agent-pulse budget --json` |
| 成本预测 | `agent-pulse forecast --json` |
| 成本异常检查 | `agent-pulse anomaly --json` |
| 健康/CI 检查 | `agent-pulse health --json` |
| 综合评分 | `agent-pulse score --json` |
| 搜索会话 | `agent-pulse search "<query>" --json` |
| 比较时间段 | `agent-pulse compare --json` |
| 比较项目 | `agent-pulse compare-projects --json` |
| 活动日历 | `agent-pulse heatmap --json` |
| 智能推荐 | `agent-pulse insights --json` |
| Prometheus 指标 | `agent-pulse metrics --format prometheus` |
| 导出报告 | `agent-pulse export -f markdown` 或 `agent-pulse export-html` |
| Web 仪表板 | `agent-pulse web --port 8765` |
| REST API | `agent-pulse api --port 8766` |
| MCP 工具 | `agent-pulse mcp --list-tools` |

如果安装的命令缺少选项，请运行 `agent-pulse <command> --help` 并进行调整。

## 工作流程

1. 仅当用户询问为什么数据缺失、需要设置帮助或正常数据命令返回无会话时，才使用 `agent-pulse doctor --json`。
2. 尽可能使用 JSON 输出。总结重要字段：会话、令牌、工具、搜索调用、模型分解、源分解、估计成本、警告。
3. 使用时间过滤器进行范围性问题。默认情况下，将“最近”设置为 24 小时，“本周”设置为 168 小时：

```powershell
agent-pulse status --json --hours 24
agent-pulse --json --hours 168 --limit 50
```

4. 当用户询问关于特定代理系统时，使用平台过滤器：

```powershell
agent-pulse --json -P codex --hours 24
agent-pulse --json -P claude --hours 24
agent-pulse top --json -P aider --sort cost
agent-pulse status --json -P cursor
```

5. 对于成本问题，组合总结、模型和顶级会话视图：

```powershell
agent-pulse status --json --hours 24
agent-pulse models --json --hours 24
agent-pulse top --sort cost --json --hours 24
agent-pulse optimize --json --hours 168
```

6. 对于趋势和风险问题，使用预测/历史/比较/异常：

```powershell
agent-pulse forecast --json
agent-pulse history --json
agent-pulse compare --json
agent-pulse anomaly --json
```

7. 对于设置，在使用路径猜测之前使用发现命令：

```powershell
agent-pulse doctor --json
agent-pulse scan --json --details
agent-pulse config show
```

## 解释结果

- 将 `total_cost_usd` 视为基于 Agent Pulse 本地模型定价表的估计。
- 报告成本和令牌量；低成本模型仍然可能具有非常高的令牌使用量。
- 区分会话来源，如 `codex`、`claude`、`hermes`、`deepseek`、`openclaw`、`aider`、`cursor`、`opencode` 和 `goose`。
- 如果 `doctor` 报告缺失可选源、缺失 `dev_root` 或可选的 Web 依赖项，请提及。
- 如果没有会话出现，请检查 `doctor`，然后尝试更宽的时间窗口，例如 `--hours 168`。
- 在给出总体总计之前，检查用户是否请求了源（`-P`）过滤器、模型过滤器或项目比较。
- 如果命令发出纯文本而不是 JSON 或因为安装的版本过旧而失败，请运行 `agent-pulse <command> --help` 并使用最接近的受支持选项。

## 报告

对于简短的人类可读答案，请运行 JSON 命令并总结。

对于工件，优先使用：

```powershell
agent-pulse report --period daily
agent-pulse export -f markdown
agent-pulse export-html
```

不要编造确切的节省或成本。使用 CLI 输出。

## 集成

仅在用户请求浏览器仪表板或程序化服务器时使用 Web 和 API 附加功能。在安装缺失的附加功能之前询问用户：

```powershell
pip install "agentpulse-cli[web]"
agent-pulse web --port 8765
agent-pulse api --port 8766
```

对于监控管道：

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

在解释 MCP 时，提及它公开了状态、预测、顶级会话、模型分析、优化、健康、搜索和排行榜等工具。

## 本地助手

此技能包括 `scripts/run_agent_pulse_snapshot.py`，它运行一组紧凑的、JSON 友好的 Agent Pulse 检查并打印综合摘要：

```powershell
python scripts/run_agent_pulse_snapshot.py --hours 24 --days 7
```
