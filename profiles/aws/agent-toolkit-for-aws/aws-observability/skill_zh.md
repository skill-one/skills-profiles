# AWS 可观测性

## 概述

针对 AWS 可观测性在指标、日志和追踪方面的领域专业知识，适用于两个共享 CloudWatch 名称但为独立服务、具有独立控制平面、数据模型和 API 的产品：

| | CloudWatch | CloudWatch Omni |
|---|---|---|
| **是什么** | 日志组、指标命名空间、警报、Log Insights、X-Ray、Application Signals | 应用可观测性 / 代理可观测性。每个账户每个区域一个 **Space** 是账户 CloudWatch **Dataset**（OpenTelemetry 日志、追踪和指标）的访问边界；Dataset 是 Space 读取的 CloudWatch 资源，而不是 Space 包含的内容 |
| **控制平面** | `aws cloudwatch`、`aws logs`、`aws xray`、`aws application-signals` | `aws cloudwatch-omni`（端点前缀 `cloudwatch-omni`，签名名称 `cloudwatch`） |
| **查询** | Log Insights 查询语言；GetMetricData | SQL over `logs.default` / `traces.default`；PromQL over metrics；命名视图 |
| **通知** | 警报（指标、组合、异常） | **Alerts**（SQL/PromQL 规则、贡献者、OK/WARNING/CRITICAL/NODATA） |
| **拓扑** | Application Signals 服务地图 | **上下文图**（GetContextGraph） |
| **访问** | 仅 IAM | 域 → Space → **访问授权**和**访问配置文件**（在 `setting-up-cloudwatch-observability` 中设置） |
| **仅限此处** | 动态仪器、Synthetics canaries、CloudTrail 审计、EMF | 代理质量评估、视图、上下文图 |
| **参考资料** | `references/cloudwatch/` | `references/cloudwatch-omni/` |

启用 Omni 不会替换 CloudWatch；日志组、指标和警报仍然有效，大多数客户使用两者。

**最佳搭配** [AWS MCP 服务器](https://docs.aws.amazon.com/aws-mcp/) — 可启用运行 CLI 命令、查询 CloudWatch 和直接验证配置。所有指南也适用于标准 AWS CLI 访问。

**注意**：参考文件包含特定运行时版本、配额值和功能矩阵，这些内容可能会发生变化。当精确度很重要时（例如，部署到生产环境、选择运行时或检查配额），请根据当前 AWS 文档确认值，而不是依赖这些文件中的值。

## 第 0 步 — CloudWatch 还是 CloudWatch Omni？

在路由之前决定。自然的措辞（“为高延迟设置警报”、“构建仪表板”、“查询我的日志”）并没有说明客户指的是哪个产品。

1. **客户命名产品** — "Omni"、"Application Observability"、"Agent Observability"、"Space"、"域"、"Dataset"、"访问授权"、"spaceId"、"cloudwatch-omni"、"Omni SQL"、"PromQL"、"视图"、"上下文图"、"评估器" → **Omni**。"Log Insights"、"日志组"、"指标命名空间"、"CloudWatch 警报"、"指标警报"、"组合警报"、"异常警报"、"X-Ray"、"Application Signals"、"canary"、"CloudTrail"、"动态仪器" → **CloudWatch**。一个没有其他产品信号的“警报”（或“告警”）是模糊的 — 转到规则 3 并探测：有 Space → Omni 警报（[alerts.md](references/cloudwatch-omni/alerts.md)）；无 Space → CloudWatch 警报（[cloudwatch/alarms.md](references/cloudwatch/alarms.md)）。例外：一个“PromQL **警报**”是 OpenTelemetry 指标的 CloudWatch 警报（[cloudwatch/alarms.md](references/cloudwatch/alarms.md)）— "警报" 优先于 "PromQL"。
2. **知识或操作问题**（“什么是 Omni 警报”、“Omni 是否有 API”、“警报和警报有何不同”）→ 直接从参考文件中回答。不要探测账户，也不要转向其他产品。功能是否存在是关于产品的属性，而不是账户的属性。
   [concepts.md](references/cloudwatch-omni/concepts.md) 包含完整的功能等效矩阵。
3. **必须对实时数据执行的操作，且措辞模糊的请求** → 在执行前探测目标区域：

   ```
   aws___call_aws → aws cloudwatch-omni list-domains
   aws___call_aws → aws cloudwatch-omni list-spaces        # 限定到目标区域
   ```

   - 该区域存在域和 Space → **Omni**。
   - 无 Space → **CloudWatch**：警报 → [cloudwatch/alarms.md](references/cloudwatch/alarms.md)，仪表板 → [cloudwatch/dashboards.md](references/cloudwatch/dashboards.md)，查询 → [cloudwatch/log-insights.md](references/cloudwatch/log-insights.md)，指标 → [cloudwatch/metrics.md](references/cloudwatch/metrics.md)。如果客户明确要求 Omni 且没有 Space，那是一次性设置 — 见步骤 4。
   - 探测本身出错（“尚未支持”、“未知服务”、“端点无法解析”）→ 正在使用的 CLI/SDK 模型缺少 `cloudwatch-omni`。这 **不是** Omni 缺失的证据，不得报告为“Omni 不可用”。客户的 AWS CLI/SDK 最可能早于该服务。如果请求包含 **任何** Omni 信号，请让他们升级（AWS CLI v2 重新安装或 `brew upgrade awscli`；`pip install -U boto3 botocore`）并重新运行 `aws cloudwatch-omni list-domains` — 具体步骤在
     [programmatic-access.md](references/cloudwatch-omni/programmatic-access.md)；永远不要用 CloudWatch 或 X-Ray 命令替代 Omni 请求。如果请求包含 **没有** Omni 信号，不要阻塞升级：继续 CloudWatch 路径（预 Omni 默认）并在提及升级时提及。
   - 仍然不确定 → 询问客户。
4. **首次 Omni 设置** — 创建域或 Space、授权访问、配置摄取、将日志组转发到 Dataset、连接 Slack、为应用程序或 AI 代理进行仪器以使追踪到达 Space → **停止并路由到 `setting-up-cloudwatch-observability` 技能**。此技能涵盖已有数据的 Space。仪器 / ADOT / OTel-collector 请求未命名 Application Signals、ServiceEvents 或 `amazon-cloudwatch-observability` 插件，也未提及 Omni 或 Space 是模糊的 — 探测目标区域的 `list-spaces`：有 Space → 路由到 `setting-up-cloudwatch-observability` 技能的应用仪器参考（纯 ADOT SDK，无插件）；无 Space →
     [cloudwatch/application-signals-onboarding.md](references/cloudwatch/application-signals-onboarding.md)。

Space 是 **每个账户每个区域一个** — 探测请求的目标区域。在错误区域对 Omni 进行查询将返回空结果，容易被误读为“无数据”。

## 路由 — CloudWatch (`references/cloudwatch/`)

| 用户需求 | 操作 |
|-----------|--------|
| 启用/引导服务到 Application Signals（自动仪器） | 阅读 [application-signals-onboarding.md](references/cloudwatch/application-signals-onboarding.md) |
| 通过 CI/CD 传播 ServiceEvents git/deployment 元数据 | 阅读 [application-signals-cicd-metadata.md](references/cloudwatch/application-signals-cicd-metadata.md) |
| 每平台/每语言 Application Signals 启用步骤 | 阅读 `references/cloudwatch/appsignals-guides/<platform>-<language>.md` 匹配的（例如 [eks-python.md](references/cloudwatch/appsignals-guides/eks-python.md)） |
| 编写 Log Insights 查询（管道分隔符语法：字段、过滤、统计、排序、解析、显示） | 阅读 [log-insights.md](references/cloudwatch/log-insights.md) |
| 配置警报（指标、组合、异常） | 阅读 [alarms.md](references/cloudwatch/alarms.md)。Omni **警报** 请参阅 Omni 表 |
| 发布自定义指标或使用 EMF | 阅读 [metrics.md](references/cloudwatch/metrics.md) |
| 设置 X-Ray 追踪或 ADOT | 阅读 [tracing.md](references/cloudwatch/tracing.md) |
| 构建 CloudWatch 仪表板 | 阅读 [dashboards.md](references/cloudwatch/dashboards.md) |
| 调试可观测性问题 | 阅读 [troubleshooting.md](references/cloudwatch/troubleshooting.md) — 从 5 个最常见修复开始 |
| 调试 canary 失败 | 阅读 [synthetics.md](references/cloudwatch/synthetics.md) — 查看常见失败表 |
| CloudTrail 运营审计 | 阅读 [cloudtrail.md](references/cloudwatch/cloudtrail.md) |
| 使用 CDK 设置 Lambda 监控 | 使用 [alarm-template.ts](assets/cloudwatch/alarm-template.ts) 作为起点 |
| 创建合成 canary | 阅读 [synthetics.md](references/cloudwatch/synthetics.md) |
| 配置 ADOT 收集器 | 使用 [otel-config.yaml](assets/cloudwatch/otel-config.yaml) 作为起点 |
| 使用断点/快照调试运行中的服务 — 动态仪器（**修改实时服务并捕获实时数据**） | 在采取行动前完整阅读 [dynamic-instrumentation.md](references/cloudwatch/dynamic-instrumentation.md)。在创建/删除前与用户确认，并在重大操作前进行说明：观察 → 假设 → 提出操作 → 预期结果。仅源代码检查可识别假设，不能确认根本原因；在运行时证据确认之前，将疑似原因保持为假设状态。 |

## 路由 — CloudWatch Omni (`references/cloudwatch-omni/`)

对实时 Space 数据的操作假设 Step 0 找到了 Space。知识问题直接从文件中回答。

| 用户需求 | 操作 |
|-----------|--------|
| **概念。** Omni 是什么，什么是域 / Space / Dataset / 授权 / 配置文件 / 视图 / 警报 / 上下文图，功能是 Omni 还是 CloudWatch，设置从哪里开始 | 阅读 [concepts.md](references/cloudwatch-omni/concepts.md) |
| **查询日志或追踪** — SQL (`SELECT … FROM logs.default / traces.default / default`), 字段访问, 模式发现, 跨度持续时间, TABLESAMPLE | 阅读 [query/sql-logs-traces.md](references/cloudwatch-omni/query/sql-logs-traces.md) |
| **查询指标** — PromQL, 哪个指标回答哪个 AWS 服务症状, 为什么指标缺失, 计数器 vs 计数器 | 阅读 [query/promql-metrics.md](references/cloudwatch-omni/query/promql-metrics.md)。指标是 PromQL，不是 SQL |
| **视图** — 创建、管理或查询命名可重用的 SQL (`FROM view.<name>`) | 阅读 [query/views.md](references/cloudwatch-omni/query/views.md) |
| **Omni 中的仪表板** — 组合、接地面板查询、编写 `panels[]`、布局网格、API 保存语义（任何可解析的正文上的 HTTP 200；保存前验证）、修复空或空白面板、`*OmniDashboard` API | 阅读 [dashboards.md](references/cloudwatch-omni/dashboards.md) |
| **Omni 中的警报** — 任何提及 Omni **警报**、`CreateAlert` / `GetAlert` / `ListAlerts` / `UpdateAlert` / `DeleteAlert`、`profileId`、警报 ARN 或警报与警报的区别；创建、调整、标记、列出、删除；通知 | 阅读 [alerts.md](references/cloudwatch-omni/alerts.md)。警报 API 是真实且一流的 — **不要**重定向到 CloudWatch 警报。Omni 未启用时的 CloudWatch 警报，请阅读 [cloudwatch/alarms.md](references/cloudwatch/alarms.md) |
| **上下文图** — 为什么服务 X 慢或失败，什么依赖它，上游/下游，爆炸半径，从洞察或异常逐跳到根本原因，`GetContextGraph` | 阅读 [context-graph.md](references/cloudwatch-omni/context-graph.md) |
| **代理评估** — 按需评分追踪，选择评估器，读取存储的 `gen_ai.evaluation.*` 分数（“哪些评估器表现最差”、“哪些在线评估器不健康/表现不佳”），从追踪构建数据集，设置在线评估，编写自定义评估器，审计代理的追踪是否正在流动 | 阅读 [agent-evaluation.md](references/cloudwatch-omni/agent-evaluation.md) |
| **程序化访问** — “Omni 是否有 API 或 SDK”、从代码、CI、IaC 或 AI 编码代理调用 Omni | 阅读 [programmatic-access.md](references/cloudwatch-omni/programmatic-access.md)。Omni 有一个真实的公共 SigV4 API；永远不要回答它没有，永远不要用 CloudWatch 或 X-Ray CLI/SDK 替代，并在不探测 Space 的情况下回答 |
| **谁有权访问 Space**、授予权限或撤销权限、访问配置文件、创建 Space 或域、摄取、转发、Slack、Azure、为应用程序或 AI 代理进行仪器 | 路由到 **`setting-up-cloudwatch-observability`** 技能 |
| 跨多个区域 | 首先阅读最具体的参考，然后根据需要咨询其他内容 |

## 文件

### `references/cloudwatch/`

| 文件 | 内容 |
|------|---------|
| [application-signals-onboarding.md](references/cloudwatch/application-signals-onboarding.md) | 启用 Application Signals 自动仪器：EKS 插件、CloudWatch Agent IAM、OTLP 端点、ServiceEvents 环境变量、动态仪器 — 按平台/语言两级范围 |
| [application-signals-cicd-metadata.md](references/cloudwatch/application-signals-cicd-metadata.md) | 通过 CI/CD 传播 ServiceEvents git & 部署元数据（5 个 `OTEL_AWS_SERVICE_EVENTS_*` 变量） |
| `appsignals-guides/`（例如 [eks-python.md](references/cloudwatch/appsignals-guides/eks-python.md)） | 16 个按平台/语言划分的 Application Signals 启用指南（EC2/ECS/EKS/Lambda × Python/Node.js/Java/.NET） |
| [alarms.md](references/cloudwatch/alarms.md) | 指标、组合、异常检测警报 — 配置、约束、推荐默认值 |
| [log-insights.md](references/cloudwatch/log-insights.md) | 完整查询语法、命令、函数、已知问题、可重用查询库 |
| [metrics.md](references/cloudwatch/metrics.md) | 自定义指标、EMF 规范、指标过滤器、高分辨率、保留 |
| [tracing.md](references/cloudwatch/tracing.md) | X-Ray → ADOT 迁移、采样规则、注释 vs 元数据、收集器配置 |
| [dashboards.md](references/cloudwatch/dashboards.md) | 小部件类型、跨账户/区域、动态标签、共享 |
| [troubleshooting.md](references/cloudwatch/troubleshooting.md) | 错误 → 原因 → 修复所有可观测性服务 |
| [cloudtrail.md](references/cloudwatch/cloudtrail.md) | 运营审计、事件类型、S3+Athena 查询 |
| [synthetics.md](references/cloudwatch/synthetics.md) | Canary 运行时/blueprint 约束、VPC 网络配置、常见失败 |
| [dynamic-instrumentation.md](references/cloudwatch/dynamic-instrumentation.md) | 动态仪器调试循环 — 实时代码上的断点/探测、快照捕获 + 相关分析、创建/删除控制、快照 PII 处理。通过 `scripts/cloudwatch/di_instrumentation.py` + `scripts/cloudwatch/di_snapshots.py` 运行；详情在 `dynamic-instrumentation/` |
| [alarm-template.ts](assets/cloudwatch/alarm-template.ts) | 最佳实践 CDK Lambda 监控（警报 + 仪表板） |
| [otel-config.yaml](assets/cloudwatch/otel-config.yaml) | X-Ray 追踪 + CloudWatch EMF 指标的 ADOT 收集器配置 |

### `references/cloudwatch-omni/`

| 文件 | 内容 |
|------|---------|
| [concepts.md](references/cloudwatch-omni/concepts.md) | Omni 是什么和不是什么；术语表（域、Space、Dataset、授权、配置文件、视图、警报、仪表板、上下文图、评估器）；Omni 与 CloudWatch 功能等效矩阵；如何判断客户指的是哪个产品；设置顺序及其位置 |
| [context-graph.md](references/cloudwatch-omni/context-graph.md) | Omni 从追踪和指标构建的服务/资源拓扑；`GetContextGraph` 请求/响应和 CLI；读取上游 vs 下游和爆炸半径；从洞察或异常逐跳到根本原因，然后转向查询 |
| [programmatic-access.md](references/cloudwatch-omni/programmatic-access.md) | 公共 SigV4 API（`cloudwatch-omni` 端点前缀，`cloudwatch` 签名名称），程序化调用者如何授权，CLI/SDK 访问（以及不支持的服务的错误是客户端版本问题），CloudFormation/CDK，AI 编码代理，以及要避免的错误答案 |
| [query/sql-logs-traces.md](references/cloudwatch-omni/query/sql-logs-traces.md) | 日志和追踪上的 SQL — 表地址、所需时间范围、系统字段、字段访问和引号、模式发现、支持的操作、函数、常见模式（包括 `durationNano` 跨度持续时间）、约束、TABLESAMPLE |
| [query/promql-metrics.md](references/cloudwatch-omni/query/promql-metrics.md) | Omni 中的指标是 PromQL — 可查询的内容（OTLP、span RED、OpenTelemetry 增强的 vended 指标）和不可查询的内容，标签约定、`__name__` 匹配器、rate() 在计数器上、每个 AWS 服务指标目录，包括派生公式和维度陷阱 |
| [query/views.md](references/cloudwatch-omni/query/views.md) | 命名 SQL 视图：CreateView / UpdateView / DeleteView / ListViews，`FROM view.<name>`，命名和定义规则，组合模式 |
| [dashboards.md](references/cloudwatch-omni/dashboards.md) | Omni 仪表板 — 组合配方、接地面板查询、`panels[]` 正文和面板类型、可视化、60 列网格、API 保存语义（任何可解析的正文上的 200；保存前验证）、空/空白面板调试、Create/Get/List/Update/DeleteOmniDashboard API、原型模板 |
| [alerts.md](references/cloudwatch-omni/alerts.md) | Omni 警报 — 警报 vs 警报，评估（FIELD_VALUE / COUNT_OF_RESULTS，贡献者），状态和无数据处理，通知规则，逐步创建 / 更新 / 删除 / 标记 / 获取，以及警报 API |
| [agent-evaluation.md](references/cloudwatch-omni/agent-evaluation.md) | OpenTelemetry 追踪上的代理质量评估 — 仪器健康审计，评估器选择，按需评分，在线评估，自定义评估器，从追踪构建数据集，以及读取存储的 `gen_ai.evaluation.*` 分数（检索计划 + SQL 机制）。使用 `scripts/cloudwatch-omni/evaluate_traces.py` 和 `scripts/cloudwatch-omni/capture_dataset_from_traces.py` |
