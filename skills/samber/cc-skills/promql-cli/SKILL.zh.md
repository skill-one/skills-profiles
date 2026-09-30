---
name: promql-cli
description: 用于查询 Prometheus 及 PromQL 兼容引擎（Thanos、Cortex、VictoriaMetrics、Grafana Mimir、Grafana Tempo 等）的命令行工具——即时查询、范围查询、指标发现（指标/标签/元数据子命令）、输出格式（表格/CSV/JSON/图形）。适用于执行 PromQL 查询、排查具有可观测性的软件性能问题、调查延迟/错误率/饱和度，或分析时间序列数据。
---

# promql-cli — Prometheus 查询 CLI 技能

`promql-cli` (github.com/nalbury/promql-cli) 是一个用于查询、分析和可视化 Prometheus 指标的 Go CLI 工具，同时包含 PromQL 基础知识。

## 参考文件

在执行任务之前，请阅读相关的参考文件：

| 文件 | 何时阅读 |
| --- | --- |
| `references/installation.md` | 用户需要安装 promql-cli 或配置（主机、认证、令牌、密码、多主机） |
| `references/usage.md` | 用户想要发现指标/导出器/标签、运行查询或选择输出格式 |
| `references/graphing.md` | 用户希望将 Prometheus 数据可视化为终端中的 ASCII 图表 |
| `references/debugging.md` | 用户正在调查性能问题、延迟、错误、饱和度、数据缺失或查询成本问题 |
| `references/promql-reference.md` | 用户需要帮助编写 PromQL、理解指标类型、函数或聚合 |

对于大多数任务，请阅读 `references/usage.md`。对于 PromQL 帮助，请阅读 `references/promql-reference.md`。在调试时，请同时阅读 `references/debugging.md` 和 `references/promql-reference.md`。

## 配置检查

在运行任何查询之前，请验证是否已配置主机：

```bash
promql 'up'   # 如果主机可访问则成功；如果未配置则因连接错误而失败
# 或
promql --host xxx 'up'
```

将以下错误识别为配置/认证问题，并参考 `references/installation.md`：

| 错误 | 原因 |
| --- | --- |
| `dial tcp ... connection refused` | 配置地址处没有运行的主机 |
| `dial tcp ... no such host` | 主机名无法解析 — 配置中的主机名错误 |
| `error querying prometheus: ...401...` | 缺少或无效的 Bearer 令牌 |
| `error querying prometheus: ...403...` | 令牌有效但权限不足 |
| `please specify an authentication type` | 部分设置了认证标志 — 使用配置文件 |

如果出现任何这些错误，**不要替用户创建配置文件** — 配置文件可能包含凭证（令牌、密码），这些凭证绝不能通过 LLM 传递。相反，请指导用户自行设置：

> "请手动创建 `~/.promql-cli.yaml`，并填入您的 Prometheus 主机（如果需要，则包含凭证）。参考 `references/installation.md` 了解确切格式。配置完成后告诉我。"

只有在用户确认配置就绪后，您才能继续执行查询。

## 快速命令参考

```bash
promql 'up'                                          # 即时查询
promql 'rate(http_requests_total[5m])' --start 1h    # 范围查询（ASCII 图表）
promql 'up' --output csv                             # CSV 输出
promql 'up' --output json                            # JSON 输出
promql metrics                                       # 列出所有指标名称
promql labels <metric>                               # 列出指标的标签
promql meta <metric>                                 # 显示指标类型和帮助
promql --config ~/.promql-cli-prod.yaml 'up'         # 目标特定主机
```

## 关键原则

1. **对计数器使用 `rate()`，永远不要使用原始值** — 原始计数器只会增加；绝对值没有意义。`rate()` 提供每秒的变化率，这才是您真正关心的。
2. **调试时，隔离单个实例** — 跨副本聚合会掩盖每个实例的异常。一个被健康副本隐藏的过载 Pod 不会出现在平均值中。
3. **在最内层的选择器中使用标签匹配器进行早期过滤** — Prometheus 在函数之前评估选择器，因此晚期过滤意味着扫描所有时间序列。早期过滤器可以减少扫描的数据量和查询延迟。
4. **对于直方图，在 `histogram_quantile()` 之前在 `by` 子句中保留 `le** — 该函数需要所有 `le` 桶来插值百分位数；提前删除 `le` 会导致 `NaN` 或错误结果。
5. **对于范围查询，优先使用 `--output graph** — ASCII 火花线以紧凑格式传达趋势方向（上升、下降、峰值），LLM 很容易解析；原始时间戳表需要心理建模。永远不要将数千行原始 JSON/CSV 行发送到 LLM 上下文中 — 使用 `--output graph`，或者先运行 `--output graph`，然后仅使用 `--output table` 检查狭窄的时间窗口。
6. **将凭证存储在 `~/.promql-cli.yaml` 和 `~/.promql_token`，并设置权限为 600** — 将令牌作为 CLI 参数传递会在 shell 历史记录和进程列表中暴露它们。

## 查询成本规则

在查询会话之前和期间，始终应用以下规则：

0. **始终使用 promql CLI** — 从不调用 Python 脚本或 shell `curl` 中的 Prometheus HTTP API。CLI 处理认证、格式化和输出，始终如一；Python API 调用会绕过所有这些步骤，并产生必须解析的原始 JSON，这会膨胀上下文并掩盖模型解释最佳的图表输出。
1. **首先检查基数** — 在查询不熟悉的指标之前，计算其时间序列数量 (`count(metric_name)`)。没有标签过滤的高基数指标会导致超时或输出淹没。参考 `references/debugging.md` 了解模式。
2. **提前确认时间窗口** — 运行范围查询前，始终询问。大间隔很昂贵；优先选择多个短间隔查询，而不是一个长间隔查询。
3. **明确过去与最近** — 对于新的调查，询问用户是否想要过去的事件（特定时间戳）还是最近的趋势。如果是最近，提供具体选项：过去一小时、过去一天、过去一周、过去一个月。
4. **在 Prometheus 中聚合** — 从不将原始序列拉取到 Python 或 shell 中进行聚合。将 `sum by(...)`, `avg by(...)`, 或 `topk()` 推入 PromQL 表达式 — Prometheus 在服务器端折叠序列。
5. **超时 = 查询范围太广** — 如果查询时间 >15 秒，请缩小范围：添加标签过滤、缩短 `--start` 或添加聚合包装。将相同的缩窄范围应用于会话中的所有后续查询。
6. **数据缺失 → 检查 `up** — 当指标显示缺失数据时，在诊断应用程序之前运行 `up{job="...", instance="..."}`。`0` 值确认导出器已宕机。参考 `references/debugging.md`。

此技能并非详尽无遗。请参考 [官方 promql-cli 文档](https://github.com/nalbury/promql-cli) 和示例获取最新信息。Context7 可以作为可发现性平台提供帮助。

如果您在 promql-cli 本身中遇到 bug 或意外行为，请通过 [https://github.com/nalbury/promql-cli/issues](https://github.com/nalbury/promql-cli/issues) 打开问题。
