# 可观测性指南

> **Cloud Trace** 可开箱即用——无需基础设施。**Prompt-response logging** 和 **BigQuery Agent Analytics** 需要 Terraform 预配的基础设施（服务账户、GCS 存储桶、BigQuery 数据集）。运行 `agents-cli infra single-project --project PROJECT_ID` 来预配这些资源。Go 项目也会获得 BigQuery telemetry 堆栈；prompt-response logging 背后的 GCS 完成上传和 BigQuery Agent Analytics 插件仅支持 Python。有关详细信息、环境变量和验证命令，请参阅 `references/cloud-trace-and-logging.md`。如果您的项目尚未搭建，请先查看 `/google-agents-cli-scaffold`。

### `agent_runtime` 部署的操作顺序

对于 `deployment_target = agent_runtime`，在第一次 `agents-cli deploy` 之前运行 `agents-cli infra single-project`。Terraform 模块拥有整个 Reasoning Engine 资源（服务账户、部署规范、环境变量），因此在该 SDK 基于的部署之后应用它会导致 Terraform 无法在不拥有整个资源的情况下解决状态不匹配。

已经运行了 `agents-cli deploy`？有两种选择：

1. **切换到 Terraform 管理模式**——删除 SDK 部署的 Reasoning Engine，然后运行 `agents-cli infra single-project` 和 `agents-cli deploy`（会话和正在进行的会话状态将丢失）。
2. **保留 SDK 部署的实例**——跳过 `infra single-project` 并通过重新运行 `agents-cli deploy --update-env-vars "KEY=VALUE,..."` 来设置可观测性环境变量；部署将根据现有 Reasoning Engine 的显示名称进行匹配，并在原地更新它，同时保留部署外设置的环境变量。您还必须授予其服务账户 Telemetry IAM 角色，这些角色本应由 Terraform 模块预配：`roles/storage.admin`（写入日志存储桶）、`roles/logging.logWriter`、`roles/cloudtrace.agent`，并且在使用 `--bq-analytics` 搭建时还需要 `roles/bigquery.dataOwner` + `roles/bigquery.jobUser`。完整集位于 `deployment/terraform/single-project/iam.tf`（来自 `app_sa_roles`）和 `telemetry.tf` 中。在此模式下，Terraform 管理的环境变量不可用。

### 参考文件

| 文件 | 内容 |
|------|----------|
| `references/cloud-trace-and-logging.md` | 搭建项目详情——Terraform 预配的资源、环境变量、验证命令、本地启用/禁用 |
| `references/bigquery-agent-analytics.md` | BQ Agent Analytics 插件——启用、关键特性、GCS 卸载、工具来源 |
| `references/adk-docs.md` | **ADK：** adk.dev 页面，用于获取此技能之外的详细信息 |
| `references/feedback-mechanism.md` | 添加用户反馈端点——请求模型、结构化日志、日志存储桶 → BigQuery |

---

## 可观测性级别

根据您的需求选择合适的可观测性级别：

| 级别 | 功能 | 范围 | 默认状态 | 适用于 |
|------|-------------|-------|---------------|----------|
| **Cloud Trace** | 分布式追踪——执行流程、延迟、错误通过 OpenTelemetry spans | 所有模板、所有环境 | 总是启用 | 调试延迟、理解代理执行流程 |
| **Prompt-Response Logging** | GenAI 交互导出到 GCS、BigQuery 和 Cloud Logging | 搭建的 ADK Python 项目 | 本地禁用，部署时启用 | 审计 LLM 交互、合规性 |
| **BigQuery Agent Analytics** | 结构化代理事件（LLM 调用、工具使用、结果）到 BigQuery | 带有插件启用的 ADK Python 代理 | 选择性启用（搭建时使用 `--bq-analytics`） | 对话分析、自定义仪表板、LLM-as-judge 评估 |
| **第三方集成** | 外部可观测性平台（AgentOps、Phoenix、MLflow 等） | 任何 OpenTelemetry 代理 | 选择性启用，按提供者设置 | 团队协作、专业可视化、提示管理 |

**询问用户** 他们需要哪些级别——可以组合使用。Cloud Trace 总是启用；其他级别是可叠加的。

---

## Cloud Trace

搭建的代理使用 OpenTelemetry 发送分布式追踪。每个代理调用都会产生 spans，跟踪完整的执行流程。

### Span 层级结构

> **ADK 项目。** 这些是 ADK 的 span 名称；其他框架会发出自己的 spans（`generate_content` 来自共享的 google-genai 仪器器）。

```
invoke_workflow (顶层运行)
  └── invoke_agent (链中每个代理一个)
        ├── call_llm (模型请求)
        │     └── generate_content (底层 GenAI 模型调用)
        └── execute_tool (工具执行)
```

### 按部署类型设置

| 部署 | 设置 |
|-----------|-------|
| **Agent Runtime** | 自动——启动时连接导出器，由 `GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY`（部署时设置）控制；导出到 Cloud Trace/Logging + Agent Engine 控制台 |
| **Cloud Run / GKE (搭建)** | 自动——启动时连接导出器，导出到 Cloud Trace/Logging |
| **Cloud Run / GKE (手动)** | 配置应用程序中的 OpenTelemetry 导出器 |
| **本地开发** | 与 `agents-cli playground` 兼容；在 Cloud Console 中可见追踪 |

连接到应用程序启动时——**ADK Python：** `get_fast_api_app(otel_to_cloud=True)` 在 `app/fast_api_app.py` 中；**ADK Go：** `setupObservability()` 在 `observability.go` 中；其他模板调用自己的。`references/cloud-trace-and-logging.md` 有详细信息。

查看追踪：**Cloud Console → Trace → Trace explorer**

**ADK：** 详细设置说明（Agent Runtime CLI/SDK、Cloud Run、自定义部署），请获取 `https://adk.dev/integrations/cloud-trace/index.md`。

---

## Prompt-Response Logging

捕获 GenAI 交互并导出到 GCS（JSONL）和 BigQuery（通过日志存储桶 + 外部表）。内容受 **两个独立级别** 管理；Terraform 部署的默认净结果是 **GCS/BigQuery 中的完整内容，无追踪内容**：

| 级别 | 捕获 | 控制 | Terraform 部署默认 |
|------|----------|---------------|----------------------------|
| **GCS/BigQuery 完成内容** | 完整提示/响应（prompt-response logging 功能） | `OTEL_INSTRUMENTATION_GENAI_COMPLETION_HOOK=upload` + `LOGS_BUCKET_NAME` | **开启**——完整内容 |
| **追踪 spans / Cloud Logging 事件** | Span/事件内容 | `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`（加上 `ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS=false`，**ADK Python 仅限**） | **关闭**——`NO_CONTENT` |

这两个级别是独立的：只要 GCS/BigQuery 上传变量的上传变量设置，就会捕获完整内容，并且**不会**尊重 `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`，后者仅控制追踪/事件级别。

**ADK Python** 将其作为实验性 semconv 枚举读取：

- `NO_CONTENT` — 追踪/事件中无内容（搭建默认）
- `EVENT_ONLY` — Cloud Logging 事件中包含内容
- `SPAN_ONLY` / `SPAN_AND_EVENT` — 追踪 spans 中包含内容
- `true` / `false` — **无效**；回退到 `NO_CONTENT`

**ADK Go** 将其作为布尔值读取相同的变量：`"1"` 或 `"true"` 捕获内容，任何其他值——包括上述枚举成员——都会忽略它。

有关完整机制（semconv 选择性加入、声明性 Terraform 配置、环境变量表、启用/禁用、验证命令），请参阅 `references/cloud-trace-and-logging.md`。有关 ADK 日志文档（日志级别、配置、调试），请获取 `https://adk.dev/observability/logging/index.md`。

---

## BigQuery Agent Analytics 插件

> **ADK 项目。** 可选的 ADK 插件，将结构化代理事件记录到 BigQuery。在搭建时使用 `--bq-analytics` 启用。有关详细信息，请参阅 `references/bigquery-agent-analytics.md`。

---

## 第三方集成

许多第三方可观测性平台可以摄取代理 telemetry（通过 OpenTelemetry 或自定义仪器）。下表涵盖了常见的平台；完整列表更大（见下方的指针）。

| 平台 | 关键差异 | 设置复杂度 | 自托管选项 |
|------|-------------------|-----------------|-------------------|
| **AgentOps** | 会话回放、2 行设置、替换原生 telemetry | 极低 | 否（SaaS） |
| **Arize AX** | 商业平台、生产监控、评估仪表板 | 低 | 否（SaaS） |
| **Phoenix** | 开源、自定义评估器、实验测试 | 低 | 是 |
| **MLflow** | OpenTelemetry 追踪到 MLflow Tracking Server、span 树可视化 | 中等（需要 SQL 后端） | 是 |
| **Monocle** | 1 次调用设置、VS Code Gantt 图表可视化器 | 极低 | 是（本地文件） |
| **Weave** | W&B 平台、团队协作、时间线视图 | 低 | 否（SaaS） |
| **Freeplay** | 提示管理 + 评估 + 可观测性在一个平台 | 低 | 否（SaaS） |

**询问用户** 他们更喜欢哪个平台——说明权衡并让他们选择。**ADK：** 获取平台的设置页面，格式为 `https://adk.dev/integrations/<slug>/index.md`（上表中的 slugs：`agentops`、`arize-ax`、`phoenix`、`mlflow-tracing`、`monocle`、`weave`、`freeplay`）；ADK 有更多可观测性集成（Datadog、Galileo、LangWatch、Latitude、Future AGI、Respan、Zespan、…）——浏览完整、最新的列表，请访问 `https://adk.dev/integrations/`（可观测性主题）。在其他框架上，基于 OpenTelemetry 的平台仍然可用，但请遵循平台自己的设置文档。

---

## 故障排除

| 问题 | 解决方案 |
|-------|----------|
| Cloud Trace 中无追踪 | 验证 telemetry 设置在启动时运行，并且服务账户具有 `cloudtrace.agent` 角色。**ADK Python：** `fast_api_app.py` 使用 `get_fast_api_app(otel_to_cloud=True)`；**ADK Go：** `observability.go` 手动构建导出器。Agent Runtime 额外基于 `GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY` 控制此功能。 |
| Prompt-response 数据未出现 | 检查 `LOGS_BUCKET_NAME` 是否设置；验证服务账户对存储桶具有 `storage.objectCreator` 权限；检查应用程序日志中的 telemetry 设置警告 |
| 追踪/事件中存在内容（不希望） | **ADK Python：** `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT` 将内容从 spans/事件中排除。**ADK Go：** 任何值不是 `1`/`true` 都会排除，因此将其清除或设置为 `false`。注意：GCS/BigQuery 完成内容仍然捕获完整内容——要停止，请删除 `LOGS_BUCKET_NAME`/`OTEL_INSTRUMENTATION_GENAI_COMPLETION_HOOK`（在 `service.tf` 中删除上传块） |
| BigQuery 分析未记录 | **ADK Python：** 验证 `app/agent.py` 中插件配置正确；检查 `BQ_ANALYTICS_DATASET_ID` 环境变量是否设置 |
| 第三方集成未捕获 spans | 检查提供者特定的环境变量（API 密钥、端点）；某些提供者（AgentOps）会替换原生 telemetry |
| 追踪中缺少工具 spans | **ADK：** 工具执行 spans 出现在 `execute_tool` 下（其他框架使用自己的 span 名称）——检查追踪浏览器过滤器 |
| Telemetry 成本过高 | 关闭内容捕获（Python 中的 `NO_CONTENT`，Go 中的 `false`）；减少 BigQuery 保留期；禁用未使用的级别 |

---

## 相关技能

- `/google-agents-cli-deploy` — 部署目标、CI/CD 管道和生产工作流
- `/google-agents-cli-workflow` — 开发工作流、编码规范和操作规则
- `/google-agents-cli-adk-code` — ADK API 快速参考，用于编写代理代码，Python 和 Go
