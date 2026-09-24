# 可观测性指南

> **Cloud Trace** 开箱即用 — 无需基础设施。**Prompt-response logging** 和 **BigQuery Agent Analytics** 需要由 Terraform 搭建的基础设施（服务账户、GCS 存储桶、BigQuery 数据集）。运行 `agents-cli infra single-project --project PROJECT_ID` 来部署这些资源。Go 项目也包含 BigQuery 遥测栈；Prompt-response logging 背后的 GCS 完成上传以及 BigQuery Agent Analytics 插件仅支持 Python。详见 `references/cloud-trace-and-logging.md`，了解详情、环境变量和验证命令。如果您的项目尚未搭建，请先查看 `/google-agents-cli-scaffold`。

### `agent_runtime` 部署的操作顺序

对于 `deployment_target = agent_runtime`，在首次运行 `agents-cli deploy` 之前，运行 `agents-cli infra single-project`。Terraform 模块拥有完整的 Reasoning Engine 资源（服务账户、部署规格、环境变量），因此应用该模块后执行基于 SDK 的部署会创建 Terraform 无法调和的状态不一致，若需自行接管整个资源，需满足相应条件。

已经运行过 `agents-cli deploy`？有两个选择：

1. **切换到由 Terraform 管理** — 删除由 SDK 部署的 Reasoning Engine，然后运行 `agents-cli infra single-project` 和 `agents-cli deploy`（会话和进行中的状态将会丢失）。
2. **保留 SDK 部署的实例** — 跳过 `infra single-project`，通过重新运行 `agents-cli deploy --update-env-vars "KEY=VALUE,..."` 设置可观测性环境变量；部署会根据显示名称匹配现有 Reasoning Engine，并原地更新，保留部署外部设置的环境变量。您还必须为其服务账户授予其他情况下 Terraform 模块会配置的遥测 IAM 角色：`roles/storage.admin`（将完成上传写入日志存储桶）、`roles/logging.logWriter`、`roles/cloudtrace.agent`，以及当使用 `--bq-analytics` 搭建时还需要 `roles/bigquery.dataOwner` + `roles/bigquery.jobUser`。完整角色列表位于 `deployment/terraform/single-project/iam.tf`（来自 `app_sa_roles`）和 `telemetry.tf` 中。此模式下不可用 Terraform 管理环境变量。

### 参考文件

| 文件 | 内容 |
|------|----------|
| `references/cloud-trace-and-logging.md` | 搭建后的项目详情 — 由 Terraform 配置的资源、环境变量、验证命令、本地启用/禁用 |
| `references/bigquery-agent-analytics.md` | BQ Agent Analytics 插件 — 启用、关键功能、GCS 卸载、工具来源 |
| `references/adk-docs.md` | **ADK：** 获取该技能更多详细内容所需的 adk.dev 页面 |
| `references/feedback-mechanism.md` | 添加用户反馈端点 — 请求模型、结构化日志、日志汇集 → BigQuery |

---

## 可观测性层级

根据您的需求选择合适的可观测性层级：

| 层级 | 功能 | 范围 | 默认状态 | 适用场景 |
|------|-------------|-------|------------|----------|
| **Cloud Trace** | 分布式跟踪 — 通过 OpenTelemetry span 跟踪执行流程、延迟和错误 | 所有模板、所有环境 | 始终开启 | 调试延迟、理解代理执行流程 |
| **Prompt-Response Logging** | GenAI 交互导出至 GCS、BigQuery 和 Cloud Logging | 搭建后的 ADK Python 项目 | 本地关闭，部署时开启 | 审计 LLM 交互、合规要求 |
| **BigQuery Agent Analytics** | 结构化代理事件（LLM 调用、工具使用、结果）写入 BigQuery | 启用插件的 ADK Python 代理 | Opt-in（搭建时通过 `--bq-analytics` 启用） | 对话式分析、自定义仪表盘、LLM-as-judge 评估 |
| **Third-Party Integrations** | 外部可观测性平台（AgentOps、Phoenix、MLflow 等） | 任意经 OpenTelemetry 插桩的代理 | Opt-in，按提供商设置 | 团队协作、专用可视化、提示管理 |

**询问用户**需要哪一层级（或哪几层）——可以组合使用。Cloud Trace 始终开启；其他层级为附加项。

---

## Cloud Trace

搭建的代理使用 OpenTelemetry 发出分布式跟踪。每次代理调用都会产生跟踪完整执行流程的 span。

### Span 层级

> **ADK 项目。** 这些是 ADK 的 span 名称；其他框架会发出自己的（`generate_content` 无论哪种情况都来自共享的 google-genai 插桩器）。

```
invoke_workflow (top-level run)
  └── invoke_agent (one per agent in the chain)
        ├── call_llm (model request)
        │     └── generate_content (underlying GenAI model call)
        └── execute_tool (tool execution)
```

### 按部署类型设置

| 部署 | 设置 |
|-----------|-------|
| **Agent Runtime** | 自动 — 启动时连接导出器，由 `GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY` 控制（由部署设置）；导出至 Cloud Trace/Logging + Agent Engine 控制台 |
| **Cloud Run / GKE (scaffolded)** | 自动 — 启动时连接导出器，导出至 Cloud Trace/Logging |
| **Cloud Run / GKE (manual)** | 在应用中配置 OpenTelemetry 导出器 |
| **Local dev** | 可与 `agents-cli playground` 配合使用；跟踪信息可在 Cloud Console 中查看 |

应用启动时连接导出器 — **ADK Python：** 在 `app/fast_api_app.py` 中使用 `get_fast_api_app(otel_to_cloud=True)`；**ADK Go：** 在 `observability.go` 中使用 `setupObservability()`；其他模板调用自身的代码。`references/cloud-trace-and-logging.md` 包含详情。

查看跟踪：**Cloud Console → Trace → Trace explorer**

**ADK：** 获取详细的设置说明（Agent Runtime CLI/SDK、Cloud Run、自定义部署），请获取 `https://adk.dev/integrations/cloud-trace/index.md`。

---

## Prompt-Response 日志

捕获 GenAI 交互并导出至 GCS（JSONL）和 BigQuery（通过日志汇集 + 外部表）。内容受**两个独立层级**的约束；Terraform 部署的整体默认设置是**在 GCS/BigQuery 中包含完整内容，在跟踪中不包含任何内容**：

| 层级 | 捕获内容 | 由...控制 | 默认（Terraform 部署） |
|------|----------|---------------|----------------------------|
| **GCS/BigQuery 完成内容** | 完整的提示/响应（提示-响应日志功能） | `OTEL_INSTRUMENTATION_GENAI_COMPLETION_HOOK=upload` + `LOGS_BUCKET_NAME` | **开启** — 完整内容 |
| **跟踪 span / Cloud Logging 事件** | Span/事件内容 | `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`（以及 `ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS=false`，**仅 ADK Python**） | **关闭** — `NO_CONTENT` |

这些层级相互独立：只要设置了上传变量，GCS/BigQuery 上传就会捕获完整内容，且**不遵循** `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`，后者仅控制跟踪/事件层级。

**ADK Python** 将其作为实验性 semconv 枚举进行读取：

- `NO_CONTENT` — span/事件中不包含内容（搭建默认值）
- `EVENT_ONLY` — Cloud Logging 事件中包含内容
- `SPAN_ONLY` / `SPAN_AND_EVENT` — 内容在跟踪 span 中
- `true` / `false` — **无效**；回退到 `NO_CONTENT`

**ADK Go** 将该变量作为**布尔值**读取：`"1"` 或 `"true"` 捕获内容，上述包括枚举成员在内的任何其他值都会将其省略。

有关完整机制（semconv 开启、声明式 Terraform 配置、环境变量表、启用/禁用、验证命令），请参阅 `references/cloud-trace-and-logging.md`。有关 ADK 日志文档（日志级别、配置、调试），请获取 `https://adk.dev/observability/logging/index.md`。

---

## BigQuery Agent Analytics 插件

> **ADK 项目。** 可选的 ADK 插件，将结构化代理事件记录到 BigQuery。在搭建时通过 `--bq-analytics` 启用。详见 `references/bigquery-agent-analytics.md`。

---

## Third-Party Integrations

许多第三方可观测性平台可以通过 OpenTelemetry 或自定义插桩接收代理遥测。下表涵盖常见平台；完整列表更长（参见其下方的指向）。

| 平台 | 关键优势 | 设置复杂度 | 自建选项 |
|----------|-------------------|-----------------|-------------------|
| **AgentOps** | 会话回放、两行代码设置、替代原生遥测 | 最少 | 否（SaaS） |
| **Arize AX** | 商业平台、生产监控、评估仪表盘 | 低 | 否（SaaS） |
| **Phoenix** | 开源、自定义评估器、实验测试 | 低 | 是 |
| **MLflow** | OTel 跟踪至 MLflow 跟踪服务、span 树可视化 | 中等（需要 SQL 后端） | 是 |
| **Monocle** | 一次调用设置、VS Code 甘特图可视化器 | 最少 | 是（本地文件） |
| **Weave** | W&B 平台、团队协作、时间线视图 | 低 | 否（SaaS） |
| **Freeplay** | 统一平台，提供提示管理、评估和可观测性 | 低 | 否（SaaS） |

**询问用户**偏好哪个平台 — 呈现权衡选项，让用户选择。**ADK：** 在 `https://adk.dev/integrations/<slug>/index.md` 获取对应平台的设置页面（表格中的 slug：`agentops`、`arize-ax`、`phoenix`、`mlflow-tracing`、`monocle`、`weave`、`freeplay`）；ADK 还有更多可观测性集成（Datadog、Galileo、LangWatch、Latitude、Future AGI、Respan、Zespan 等）— 在 `https://adk.dev/integrations/`（可观测性主题）浏览完整、当前的列表。其他框架的基于 OpenTelemetry 的平台依然适用，但需遵循各平台的自身设置文档。

---

## 故障排除

| 问题 | 解决方案 |
|-------|----------|
| Cloud Trace 中无跟踪 | 验证遥测设置是否在启动时运行，且服务账户拥有 `cloudtrace.agent` 角色。**ADK Python：** `fast_api_app.py` 使用 `get_fast_api_app(otel_to_cloud=True)`；**ADK Go：** 手动构建 `observability.go` 中的导出器。Agent Runtime 还会根据 `GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY` 对该项进行门控。 |
| Prompt-响应数据未显示 | 检查 `LOGS_BUCKET_NAME` 是否已设置；验证服务账户拥有存储桶上的 `storage.objectCreator`；检查应用日志中的遥测设置警告 |
| 跟踪/事件中包含内容（不希望如此） | **ADK Python：** 通过设置 `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT` 可防止内容进入 span/事件。**ADK Go：** 除 `1`/`true` 外的任何值都会做到这一点，因此将其取消设置或设置为 `false`。注意：GCS/BigQuery 完成内容仍会捕获完整内容 — 若要停止该操作，请移除 `LOGS_BUCKET_NAME`/`OTEL_INSTRUMENTATION_GENAI_COMPLETION_HOOK`（在 `service.tf` 中移除上传块） |
| BigQuery 分析未记录 | **ADK Python：** 验证插件已在 `app/agent.py` 中配置；检查 `BQ_ANALYTICS_DATASET_ID` 环境变量是否已设置 |
| 第三方集成未捕获 span | 检查提供商特定的环境变量（API 密钥、端点）；某些提供商（AgentOps）会替代原生遥测 |
| 缺少工具 span 跟踪 | **ADK：** 工具执行 span 出现在 `execute_tool` 下（其他框架使用其自己的 span 名称）— 检查跟踪浏览器过滤器 |
| 遥测成本过高 | 关闭内容捕获（Python 中使用 `NO_CONTENT`，Go 中使用 `false`）；减少 BigQuery 保留期；禁用未使用的层级 |

---

## 相关技能

- `/google-agents-cli-deploy` — 部署目标、CI/CD 流水线和生产工作流
- `/google-agents-cli-workflow` — 开发工作流、编码指南和运营规则
- `/google-agents-cli-adk-code` — ADK API 快速参考，用于编写 Python 和 Go 代理代码
