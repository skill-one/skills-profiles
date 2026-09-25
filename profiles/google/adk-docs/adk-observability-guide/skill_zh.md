# ADK 可观测性指南

> **已搭建项目？** Terraform 已预配置云追踪和提示-响应日志。有关基础设施详情、环境变量和验证命令，请参阅 `references/cloud-trace-and-logging.md`。
>
> **未搭建项目？** 请按照下方的 ADK 文档链接进行手动设置。对于生产基础设施，请使用 `/adk-scaffold` 进行搭建。

### 参考文件

| 文件 | 内容 |
|------|----------|
| `references/cloud-trace-and-logging.md` | 搭建项目详情 — Terraform 预配置的资源、环境变量、验证命令、本地启用/禁用 |
| `references/bigquery-agent-analytics.md` | BQ Agent Analytics 插件 — 启用、关键特性、GCS 卸载、工具溯源 |

---

## 可观测性层级

根据您的需求选择合适的可观测性层级：

| 层级 | 功能 | 范围 | 默认状态 | 适用于 |
|------|-------------|-------|---------------|----------|
| **云追踪** | 分布式追踪 — 通过 OpenTelemetry 跨度跟踪执行流程、延迟、错误 | 所有模板、所有环境 | 始终启用 | 调试延迟、理解代理执行流程 |
| **提示-响应日志** | 将 GenAI 交互导出到 GCS、BigQuery 和 Cloud Logging | 仅 ADK 代理 | 本地禁用、部署时启用 | 审计 LLM 交互、合规性 |
| **BigQuery Agent Analytics** | 将结构化代理事件（LLM 调用、工具使用、结果）导出到 BigQuery | 启用插件的 ADK 代理 | 选择性启用（搭建时使用 `--bq-analytics`） | 对话分析、自定义仪表盘、LLM 作为裁判评估 |
| **第三方集成** | 外部可观测性平台（AgentOps、Phoenix、MLflow 等） | 任何 ADK 代理 | 选择性启用、按提供者设置 | 团队协作、专业可视化、提示管理 |

**询问用户** 他们需要哪些层级 — 可以组合使用。云追踪始终启用；其他层级是可叠加的。

---

## 云追踪

ADK 使用 OpenTelemetry 发送分布式追踪。每个代理调用都会生成跟踪完整执行流程的跨度。

### 跨度层级

```
invocation
  └── agent_run (链中每个代理一个)
        ├── call_llm (模型请求/响应)
        └── execute_tool (工具执行)
```

### 按部署类型设置

| 部署 | 设置 |
|-----------|-------|
| **代理引擎** | 自动 — 默认将追踪导出到 Cloud Trace |
| **Cloud Run (已搭建)** | 自动 — FastAPI 应用中 `otel_to_cloud=True` |
| **GKE (已搭建)** | 自动 — FastAPI 应用中 `otel_to_cloud=True` |
| **Cloud Run / GKE (手动)** | 在您的应用中配置 OpenTelemetry 导出器 |
| **本地开发** | 与 `make playground` 兼容；在 Cloud Console 中可见追踪 |

查看追踪：**Cloud Console → Trace → Trace explorer**

有关详细设置说明（代理引擎 CLI/SDK、Cloud Run、自定义部署），请获取 `https://adk.dev/integrations/cloud-trace/index.md`。

---

## 提示-响应日志

捕获 GenAI 交互（模型名称、令牌、时间）并导出到 GCS（JSONL）、BigQuery（外部表）和 Cloud Logging（专用桶）。默认情况下保护隐私 — 除非明确配置，否则仅记录元数据。

关键环境变量：`OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` — 设置为 `NO_CONTENT`（仅元数据，部署环境默认）、`true`（完整内容）或 `false`（禁用）。除非设置了 `LOGS_BUCKET_NAME`，否则本地禁用日志记录。

有关已搭建项目的详情（Terraform 资源、环境变量、隐私模式、启用/禁用、验证命令），请参阅 `references/cloud-trace-and-logging.md`。

有关 ADK 日志文档（日志级别、配置、调试），请获取 `https://adk.dev/observability/logging/index.md`。

---

## BigQuery Agent Analytics 插件

可选插件，将结构化代理事件记录到 BigQuery。使用搭建时 `--bq-analytics` 启用。详情请参阅 `references/bigquery-agent-analytics.md`。

---

## 第三方集成

ADK 支持多个第三方可观测性平台。每个平台使用 OpenTelemetry 或自定义仪器捕获代理行为。

| 平台 | 关键差异化 | 设置复杂度 | 自托管选项 |
|----------|-------------------|-----------------|-------------------|
| **AgentOps** | 会话回放、2 行设置、替换原生遥测 | 极低 | 否（SaaS） |
| **Arize AX** | 商业平台、生产监控、评估仪表盘 | 低 | 否（SaaS） |
| **Phoenix** | 开源、自定义评估器、实验测试 | 低 | 是 |
| **MLflow** | OpenTelemetry 追踪到 MLflow 跟踪服务器、跨度树可视化 | 中等（需要 SQL 后端） | 是 |
| **Monocle** | 1 次调用设置、VS Code Gantt 图可视化器 | 极低 | 是（本地文件） |
| **Weave** | W&B 平台、团队协作、时间线视图 | 低 | 否（SaaS） |
| **Freeplay** | 提示管理 + 评估 + 可观测性一站式平台 | 低 | 否（SaaS） |

**询问用户** 他们更倾向于哪个平台 — 呈现权衡并让他们选择。有关设置详情，请从下方深入探讨表格中获取相关的 ADK 文档页面。

---

## 故障排除

| 问题 | 解决方案 |
|-------|----------|
| Cloud Trace 中无追踪 | 验证 FastAPI 应用中 `otel_to_cloud=True`；检查服务账户具有 `cloudtrace.agent` 角色 |
| 提示-响应数据未出现 | 检查 `LOGS_BUCKET_NAME` 是否设置；验证 SA 对桶具有 `storage.objectCreator` 权限；检查应用日志中的遥测设置警告 |
| 隐私模式配置错误 | 检查 `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` 值 — 使用 `NO_CONTENT` 仅记录元数据，`false` 以禁用 |
| BigQuery 分析未记录 | 验证 `app/agent.py` 中插件配置；检查 `BQ_ANALYTICS_DATASET_ID` 环境变量是否设置 |
| 第三方集成未捕获跨度 | 检查提供者特定的环境变量（API 密钥、端点）；某些提供者（AgentOps）替换原生遥测 |
| 追踪缺少工具跨度 | 工具执行跨度位于 `execute_tool` 下 — 检查追踪浏览器过滤器 |
| 遥测成本过高 | 切换到 `NO_CONTENT` 模式；减少 BigQuery 保留期；禁用未使用的层级 |

---

## 深入探讨：ADK 文档（WebFetch URL）

对于本指南涵盖范围之外的详细文档，请获取这些页面：

| 主题 | URL |
|-------|-----|
| 可观测性概述 | `https://adk.dev/observability/index.md` |
| 代理活动日志 | `https://adk.dev/observability/logging/index.md` |
| 云追踪集成 | `https://adk.dev/integrations/cloud-trace/index.md` |
| BigQuery Agent Analytics | `https://adk.dev/integrations/bigquery-agent-analytics/index.md` |
| AgentOps | `https://adk.dev/integrations/agentops/index.md` |
| Arize AX | `https://adk.dev/integrations/arize-ax/index.md` |
| Phoenix (Arize) | `https://adk.dev/integrations/phoenix/index.md` |
| MLflow 追踪 | `https://adk.dev/integrations/mlflow/index.md` |
| Monocle | `https://adk.dev/integrations/monocle/index.md` |
| W&B Weave | `https://adk.dev/integrations/weave/index.md` |
| Freeplay | `https://adk.dev/integrations/freeplay/index.md` |
