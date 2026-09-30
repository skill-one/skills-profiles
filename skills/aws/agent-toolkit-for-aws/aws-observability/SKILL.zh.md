---
name: aws-observability
description: 构建、配置、调试和优化 AWS 可观测性——操作员症状问题以及检测 Omni 与经典 CloudWatch 的差异。CloudWatch：日志洞察、告警、动态 instrumentation 和应用信号——将服务通过 ADOT 在 EC2/ECS/EKS/Lambda 上进行 instrumentation/onboarding：自动 instrumentation、监控服务、报告遥测数据、ServiceEvents、CI/CD 元数据、Terraform/清单。还包括舰队健康状况视图。在现有 Space 上使用 CloudWatch Omni：对日志和追踪进行 SQL 查询，对指标进行 PromQL 查询，Omni 仪表板，Omni 告警，用于根本原因分析的上下文图，程序化/IaC 访问（API/SDK/CLI/CloudFormation），以及通过编码代理或技能驱动 Omni，并从追踪中评估 AI 代理质量——对实时代理流量、回放和自定义追踪评估器进行按需和持续在线评分。对于首次设置 Omni——创建 Space、授权访问、数据摄取或 ADOT instrumentation——请使用 setting-up-cloudwatch-observability。不适用于应用日志记录或威胁检测。
---

# AWS 可观测性

## 概述

针对 AWS 可观测性，涵盖指标、日志和追踪的领域专业知识，适用于两个共享 CloudWatch 名称但分别为独立服务的产品，它们拥有独立的控制平面、数据模型和 API：

| | CloudWatch | CloudWatch Omni |
|---|---|---|
| **是什么** | 日志组、指标命名空间、警报、Log Insights、X-Ray、Application Signals | 应用可观测性 / 代理可观测性。每个账户每个区域一个 **空间** 作为访问边界，覆盖账户的 CloudWatch **数据集**（OpenTelemetry 日志、追踪和指标）；数据集是空间读取的 CloudWatch 资源，而非空间包含的内容 |
| **控制平面** | `aws cloudwatch`，`aws logs`，`aws xray`，`aws application-signals` | `aws cloudwatchomni`（端点前缀 `cloudwatch-omni`，签名名称 `cloudwatch`） |
| **查询** | Log Insights 查询语言；GetMetricData | SQL 查询 `logs.default` / `traces.default`；PromQL 查询指标；命名视图 |
| **通知** | 警报（指标、组合、异常） | **告警**（SQL/PromQL 规则、贡献者、OK/WARNING/CRITICAL/NODATA） |
| **拓扑** | Application Signals 服务地图 | **上下文图**（GetContextGraph） |
| **访问** | 仅 IAM | 域 → 空间 → **访问授权** 和 **访问配置文件**（在 `setting-up-cloudwatch-observability` 中设置） |
| **仅限此处** | 动态代理、合成金丝雀、CloudTrail 审计、EMF | 代理质量评估、视图、上下文图 |
| **参考资料** | `references/cloudwatch/` | `references/cloudwatch-omni/` |

启用 Omni 不会替换 CloudWatch；日志组、指标和警报仍然有效，大多数客户同时使用两者。

**最佳搭配** [AWS MCP 服务器](https://docs.aws.amazon.com/aws-mcp/) — 可启用运行 CLI 命令、查询 CloudWatch 和直接验证配置。所有指南也适用于标准 AWS CLI 访问。

**注意**：参考文件包含特定运行时版本、配额值和功能矩阵，这些值可能会更改。当精确度很重要时（例如，部署到生产环境、选择运行时或检查配额），请与当前 AWS 文档确认值，而不是仅依赖这些文件中的值。

## 范围保护 — 这是可观测性请求吗？

此技能拥有所有路由到它的请求的范围决策，本节是其唯一家园。

**如果请求不是关于使用 CloudWatch 或 CloudWatch Omni 的 AWS 可观测性（天气、琐事、一般闲聊、非可观测性编码），请用一句话拒绝它：明确说明其超出范围，不要编造答案，不要声称虚假的能力限制（没有“无互联网访问”，没有“无天气数据”）——原因仅仅是其超出范围。然后通过命名此技能涵盖的内容来重定向：查询 CloudWatch 和 CloudWatch Omni 的日志、追踪和指标，构建仪表板，配置警报，调查服务或代理评估。**

不要尝试处理离题的任务，不要调用工具或运行查询来追求它。保持简短：不要讲大道理，不要长篇拒绝。

## 第 0 步 — CloudWatch 还是 CloudWatch Omni？

在路由之前做出决定。自然的措辞（“为高延迟设置警报”、“构建仪表板”、“查询我的日志”）并没有说明客户指的是哪个产品。

1. **客户指明了产品** — "Omni"、"应用可观测性"、"代理可观测性"、"空间"、"域"、"数据集"、"访问授权"、"`spaceId`"、"`cloudwatch-omni`"、Omni SQL、PromQL、视图、上下文图、评估器、代理评估/评分追踪/在线或持续评估/`gen_ai.evaluation`、以及 OTel 跨度词汇（`traces.default`、`logs.default`、跨度、`durationNano`、`status.code`、资源属性、`service.name`）→ **Omni**。"Log Insights"、"日志组"、"指标命名空间"、"CloudWatch 警报"、"指标警报"、"组合警报"、"异常警报"、"X-Ray"、"Application Signals"、"金丝雀"、"CloudTrail"、"动态代理" → **CloudWatch**。在代理评估请求中命名的“日志组”是用于验证的在线评估数据源，而不是 CloudWatch 信号。没有其他产品信号的“警报”（或“告警”）是模糊的——通过规则 3 探测：空间 → Omni 告警（[alerts.md](references/cloudwatch-omni/alerts.md)）；无空间 → CloudWatch 警报（[cloudwatch/alarms.md](references/cloudwatch/alarms.md)）。例外："PromQL **警报**" 是 OpenTelemetry 指标的 CloudWatch 警报（[cloudwatch/alarms.md](references/cloudwatch/alarms.md)）——"警报" 优先于 "PromQL"。
2. **知识或操作问题**（“Omni 告警是什么”、“Omni 是否有 API”、“警报和告警有何不同”）→ 直接从参考文件中回答。不要探测账户，也不要转向其他产品。功能是否存在是关于产品的客观事实，而不是账户。
   [concepts.md](references/cloudwatch-omni/concepts.md) 包含完整的功能等效矩阵。
2a. **编写/操作告警请求** — "创建/设置/编写一个当 X 时触发的 Omni 告警"、"如何对 Y 进行告警"——没有提供空间或区域，也没有允许实际创建，这是一个 **操作指南** 请求。首先提供编写指导（警报编写必须陈述的清单，然后
   [alerts.md](references/cloudwatch-omni/alerts.md)），不要在区域/空间澄清问题上停滞，也不要为明确说明“Omni 告警”的请求回退到 CloudWatch 警报。只有在用户提供空间/区域或要求您创建它后，才探测账户。
2b. **提示中已经存在遥测对象** — 用户粘贴的，或 UI 作为上下文传递的跨度、追踪、日志记录或查询结果，并询问其含义、错误或持续时间。这不是实时数据请求：不要探测账户、运行查询或要求用户再次获取它。根据
   [query/sql-logs-traces.md](references/cloudwatch-omni/query/sql-logs-traces.md) 的“已拥有的跨度或追踪的读取”部分读取，并陈述其必须陈述列表中的每一项。
2c. **查询请求的实时结果为空或无法访问**（“显示最慢的跨度”、“哪些追踪失败”）仍然用 **方法** 回答——正确的查询和使它正确的字段规则（参见
   [query/sql-logs-traces.md](references/cloudwatch-omni/query/sql-logs-traces.md) 中的必须陈述调用）。零行、错误的区域空间或无法访问的端点报告为发现，而不是整个答案。
3. **必须对实时数据采取行动，而措辞模糊的请求**（不是 0.5 步内容问题，该问题从目录中回答）→ 首先探测目标区域：

   ```
   aws___call_aws → aws cloudwatchomni list-domains
   aws___call_aws → aws cloudwatchomni list-spaces        # 聚焦到目标区域
   ```

   - 您必须在解决歧义或询问用户时明确说明，空间是 **每个账户每个区域一个**，因此探测（以及任何 Omni 查询）针对的是请求相关的区域——不仅仅是默认区域——因为针对错误区域的 Omni 查询会返回容易误解为“无数据”的空结果。
   - 该区域存在域和空间 → **Omni**。
   - 无空间 → **CloudWatch**：警报 → [cloudwatch/alarms.md](references/cloudwatch/alarms.md)，仪表板 → [cloudwatch/dashboards.md](references/cloudwatch/dashboards.md)，查询 →
     [cloudwatch/log-insights.md](references/cloudwatch/log-insights.md)，指标 →
     [cloudwatch/metrics.md](references/cloudwatch/metrics.md)。如果客户明确要求 Omni 且没有空间，那是首次设置——参见步骤 4。
   - 探测本身出错（“尚未支持”、“未知服务”、“端点无法解析”）→ 使用的 CLI/SDK 模型缺少 `cloudwatchomni`。这 **不是** Omni 缺失的证据，不应报告为“Omni 不可用”。客户的 AWS CLI/SDK 最可能早于该服务。如果请求包含 **任何** Omni 信号，请让客户运行升级命令（AWS CLI v2 重新安装或 `brew upgrade awscli`；`pip install -U boto3 botocore`），并让他们重新运行 `aws cloudwatchomni list-domains`——确切步骤在
     [programmatic-access.md](references/cloudwatch-omni/programmatic-access.md)。**切勿在主机上自行运行包管理器升级或安装程序**（`brew`、`pip install -U`、`.pkg`/MSI）；它会改变客户机器，超出请求范围，并可能破坏其他工具——交出命令并继续指导。永远不要用 CloudWatch 或 X-Ray 命令替换 Omni 请求。如果请求包含 **无** Omni 信号，不要在升级上阻塞：继续 CloudWatch 路径（Omni 之前的默认路径），仅在顺便提及时提及升级。
   - 仍然无法确定 → 询问客户。
4. **首次 Omni 设置** — 创建域或空间、授予权限、配置摄取、将日志组转发到数据集、连接 Slack、或为应用程序或 AI 代理代理化以使追踪到达空间 → **停止并路由到 `setting-up-cloudwatch-observability` 技能**。此技能涵盖已包含数据的空间。命名 Application Signals、ServiceEvents 或 `amazon-cloudwatch-observability` 插件，或 Omni 或空间的仪器化/ADOT/OTel-collector 请求是模糊的——在目标区域探测 `list-spaces`：空间 → 路由到 `setting-up-cloudwatch-observability` 技能的应用程序仪器化参考（纯 ADOT SDK，无插件）；无空间 →
     [cloudwatch/application-signals-onboarding.md](references/cloudwatch/application-signals-onboarding.md)。

**定义不足的告警请求**：当告警或警报请求命名要监视的内容（症状或服务），但没有需要输入的阈值值和评估周期时，请求那些而不是编造它们。通知是可选的（根据 alerts.md），只有在用户想要接收通知时才询问通知目的地。这在两条路径上（Omni 告警或 CloudWatch 警报）都适用。

**定义不足的仪表板请求**：当仪表板请求命名要显示的内容，但没有指标、面板或布局时，根据数据和确认面板集，而不是编造面板；仪表板没有阈值、周期或通知。对于任何仪表板编写/保存请求，还应打开 [dashboards.md](references/cloudwatch-omni/dashboards.md) 并展示其“构建或保存 Omni 仪表板时必须展示的事实”清单（见仪表板必须陈述部分）。命名资源类型需要哪些信号或面板是 0.5 步目录问题，而不是仪表板文件问题。

### 第 0.5 步 — 服务健康调查（路由）

大部分真实问题是作为操作员症状提出的，而不是作为工具： "我的 `<服务>` 是否被限流/缓慢/出错/不健康"、"我的 `<服务>` 中哪些是 `<症状>`"、"我的 `<服务>` 的健康状况如何"、"`<服务>` 依赖什么以及什么已损坏"、"`<服务>` 的信号/应该在 `<服务>` 的仪表板或视图上显示什么"。这些都是 **可观测性数据问题——从遥测表面回答，而不是从资源控制平面回答**，即使您也拉取实时数字，即使账户中不存在匹配的资源，也要用 *方法*（正确的信号、聚合、范围和注意事项）回答。

按症状路由，然后 **打开参考并展示其“必须展示的事实”清单中的每一项**——清单是输出合同，它存在于参考文件中，而不是这里：

- 关于单个 AWS 服务的 **指标症状**（限流、延迟、错误率、重启、饱和、"它应该接收哪些信号"、"命名资源类型在仪表板或视图上需要哪些信号或面板）→ [query/promql-metrics.md](references/cloudwatch-omni/query/promql-metrics.md)。打开其 **"服务健康问题——必须展示的事实"** 部分，并展示每一项适用的内容。仪表板或视图措辞不会将其发送到任何仪表板文件（两者都不包含信号事实），也不会发送到规则 3 的探测——这是一个内容问题。
- **"`<服务>` 依赖什么/下游什么已损坏" / 爆炸半径 / 谁受到影响 / 我该向哪个方向走图 / `CALLS`、`ACCESSES`、`RUNS_ON` 意思是什么** → [context-graph.md](references/cloudwatch-omni/context-graph.md)。打开其
  **"依赖关系/爆炸半径问题——必须展示的事实"** 部分，并展示每一项适用的内容。以图、依赖关系或边缘类型表述的症状或错误症状路由至此，而不是上述指标点。
- **单个缓慢或失败的跨度/追踪**（"`<服务>` 最慢的跨度"、"哪些追踪失败"）是追踪 **SQL**，而不是指标聚合 →
  [query/sql-logs-traces.md](references/cloudwatch-omni/query/sql-logs-traces.md)。打开其
  **"跨度持续时间"** 和 **"查找失败的跨度"** 部分，并陈述其必须陈述调用中的每一项——关于服务的延迟或错误 *率*（聚合信号）的请求是上述 PromQL 点。

### 编写 Omni 告警——展示必须陈述的清单

当您编写或建议 Omni 告警时，打开
[alerts.md](references/cloudwatch-omni/alerts.md) 并从其 **"编写告警时必须展示的事实"** 部分展示与任务相关的项。该部分包含每项的详细信息，是事实来源，因此根据请求陈述适合的内容，而不是在此处重述。

### 代理评估——展示必须陈述的调用

当请求涉及评分追踪、选择评估器、读取存储的分数、在线/持续评估或评估数据集时，打开
[agent-evaluation.md](references/cloudwatch-omni/agent-evaluation.md) 并陈述其 **"告诉用户所有这些"** 调用中的每一项适用项——级别规则（每个调用一个级别、三个级别语义、工具调用级别需要工具跨度）、评估器重定向和真实情况、分数存储位置和错误表格读取、以及在线评估数据源验证。调用是输出合同；答案文本必须包含它们，而不仅仅是计划。

### 构建或保存 Omni 仪表板——展示必须陈述的事实

当您编写、保存、读取回或调试 Omni 仪表板时，打开
[dashboards.md](references/cloudwatch-omni/dashboards.md) 并从其 **"构建或保存 Omni 仪表板时必须展示的事实"** 清单中展示与任务相关的项。该清单包含每项的详细信息，是事实来源。

## 路由 — CloudWatch (`references/cloudwatch/`)

| 用户需求 | 操作 |
|---------|------|
| 将服务启用/接入 Application Signals（自动代理） | 阅读 [application-signals-onboarding.md](references/cloudwatch/application-signals-onboarding.md) |
| 通过 CI/CD 传播 ServiceEvents git/部署元数据 | 阅读 [application-signals-cicd-metadata.md](references/cloudwatch/application-signals-cicd-metadata.md) |
| 各平台/各语言的 Application Signals 启用步骤 | 阅读 `references/cloudwatch/appsignals-guides/<platform>-<language>.md` 匹配的文档（例如 [eks-python.md](references/cloudwatch/appsignals-guides/eks-python.md)） |
| 编写 Log Insights 查询（管道分隔符语法：字段、过滤、统计、排序、解析、显示） | 阅读 [log-insights.md](references/cloudwatch/log-insights.md) |
| 配置警报（指标、组合、异常） | 阅读 [alarms.md](references/cloudwatch/alarms.md)。Omni **警报** 请参阅 Omni 表格 |
| 发布自定义指标或使用 EMF | 阅读 [metrics.md](references/cloudwatch/metrics.md) |
| 设置 X-Ray 追踪或 ADOT | 阅读 [tracing.md](references/cloudwatch/tracing.md) |
| 构建 CloudWatch 仪表板（小部件机制；给定 AWS 服务需要哪些信号是第 0.5 步） | 阅读 [dashboards.md](references/cloudwatch/dashboards.md) |
| 调试可观察性问题 | 阅读 [troubleshooting.md](references/cloudwatch/troubleshooting.md) — 从 5 个最常见的修复措施开始 |
| 调试金丝雀失败 | 阅读 [synthetics.md](references/cloudwatch/synthetics.md) — 查看常见失败表格 |
| CloudTrail 运营审计 | 阅读 [cloudtrail.md](references/cloudwatch/cloudtrail.md) |
| 使用 CDK 设置 Lambda 监控 | 使用 [alarm-template.ts](assets/cloudwatch/alarm-template.ts) 作为起点 |
| 创建合成金丝雀 | 阅读 [synthetics.md](references/cloudwatch/synthetics.md) |
| 配置 ADOT 收集器 | 使用 [otel-config.yaml](assets/cloudwatch/otel-config.yaml) 作为起点 |
| 使用断点/快照调试正在运行的服务 — 动态代理（**修改实时服务并捕获实时数据**） | 在采取行动前完整阅读 [dynamic-instrumentation.md](references/cloudwatch/dynamic-instrumentation.md)。在创建/删除任何操作前与用户确认，并在重大操作前进行说明：观察 → 假设 → 提出行动 → 预期结果。仅源代码检查可识别假设，不能确认根本原因；在运行时证据确认之前，将疑似原因保持为假设状态。 |

## 路由 — CloudWatch Omni (`references/cloudwatch-omni/`)

对**实时 Space 数据执行操作**的行假设第 0 步找到了一个 Space。知识问题直接从文件中回答。

| 用户需求 | 操作 |
|---------|------|
| **概念。** Omni 是什么，域 / Space / 数据集 / 授权 / 配置文件 / 查看器 / 警报 / 上下文图是什么，某个功能是 Omni 还是 CloudWatch，设置从哪里开始 | 阅读 [concepts.md](references/cloudwatch-omni/concepts.md) |
| **查询日志或追踪** — SQL (`SELECT … FROM logs.default / traces.default / default`), 字段访问, 模式发现, 最慢 / 失败的跨度 (`durationNano`, `status.code`), TABLESAMPLE | 阅读 [query/sql-logs-traces.md](references/cloudwatch-omni/query/sql-logs-traces.md)。对于最慢或失败的跨度，必须声明其 "Span Duration" / "Finding failed spans" 必须调用项，即使实时结果为空 |
| **提示中提供的跨度、追踪或日志记录** — "我有一个打开的跨度，里面有哪些错误"，粘贴的遥测对象 | 阅读 [query/sql-logs-traces.md](references/cloudwatch-omni/query/sql-logs-traces.md) 的 **"阅读您已经拥有的跨度或追踪"** 部分。从对象自己的字段回答；不要探测、查询或要求用户获取它 |
| **查询指标** — PromQL, 哪个指标回答 AWS 服务的哪个症状，为什么指标缺失，计量 vs 计数器 | 阅读 [query/promql-metrics.md](references/cloudwatch-omni/query/promql-metrics.md)。指标是 PromQL，不是 SQL |
| **查看器** — 创建、管理或查询命名可重用的 SQL (`FROM view.<name>`) | 阅读 [query/views.md](references/cloudwatch-omni/query/views.md) |
| **Omni 中的仪表板** — 组合、固定面板查询、编写 `panels[]`、布局网格、API 保存语义（未知的根或面板级键、缺少 `type`/`layout` 或不良变体在保存时以 400 ValidationException 拒绝；不良枚举值、`x+w>60` 或未知 `config` 内键在保存时返回 200 并失败或被忽略；保存前验证），修复空或空白面板，`*OmniDashboard` API | 阅读 [dashboards.md](references/cloudwatch-omni/dashboards.md) |
| **Omni 中的警报** — 任何提及 Omni **警报**、`CreateAlert` / `GetAlert` / `ListAlerts` / `UpdateAlert` / `DeleteAlert`、`profileId`、警报 ARN 或警报与警报的区别；创建、调整、标记、列出、删除；通知 | 阅读 [alerts.md](references/cloudwatch-omni/alerts.md)。警报 API 是真实且一流的 — **不要**重定向到 CloudWatch 警报。Omni 未启用时，CloudWatch 警报请阅读 [cloudwatch/alarms.md](references/cloudwatch/alarms.md) |
| **上下文图** — 为什么服务 X 慢或失败，什么依赖它，上游/下游，哪个方向行走，边缘类型 `CALLS` / `ACCESSES` / `RUNS_ON`，爆炸半径，从洞察或异常逐跳走到根本原因，`GetContextGraph` | 阅读 [context-graph.md](references/cloudwatch-omni/context-graph.md) 并声明其 "你必须呈现的事实" 部分中的每个适用项 |
| **代理评估** — 按需评分追踪，选择评估器，读取存储的 `gen_ai.evaluation.*` 分数（"哪些评估器表现最差"，"哪些在线评估器不健康 / 表现不佳"），从追踪构建数据集，设置在线评估，编写自定义评估器，审计代理的追踪是否正在流动 | 阅读 [agent-evaluation.md](references/cloudwatch-omni/agent-evaluation.md) 并声明其 "告诉用户所有这些" 调用项中的每个适用项 |
| **程序化访问** — "是否有 Omni 的 API 或 SDK"，从代码、CI、IaC 或 AI 编码代理调用 Omni | 阅读 [programmatic-access.md](references/cloudwatch-omni/programmatic-access.md)。Omni 有一个真实的公共 SigV4 API；**永远不要**回答它没有，**永远不要**用 CloudWatch 或 X-Ray CLI/SDK 替代，并且无需探测 Space 就回答 |
| **谁有权访问 Space**，授予权限或撤销权限，访问配置文件，创建 Space 或域，摄取，转发，Slack，Azure，代理应用程序或 AI 代理 | 路由到 **`setting-up-cloudwatch-observability`** 技能 |
| 跨多个区域 | 首先阅读最具体的参考，然后根据需要咨询其他内容 |

## 文件

### `references/cloudwatch/`

| 文件 | 内容 |
|------|------|
| [application-signals-onboarding.md](references/cloudwatch/application-signals-onboarding.md) | 启用 Application Signals 自动代理：EKS 插件、CloudWatch Agent IAM、OTLP 端点、ServiceEvents 环境变量、动态代理 — 平台/语言双层范围 |
| [application-signals-cicd-metadata.md](references/cloudwatch/application-signals-cicd-metadata.md) | 通过 CI/CD 传播 ServiceEvents git & 部署元数据（5 个 `OTEL_AWS_SERVICE_EVENTS_*` 变量） |
| `appsignals-guides/`（例如 [eks-python.md](references/cloudwatch/appsignals-guides/eks-python.md)） | 16 个平台 × 语言 Application Signals 启用指南（EC2/ECS/EKS/Lambda × Python/Node.js/Java/.NET） |
| [alarms.md](references/cloudwatch/alarms.md) | 指标、组合、异常检测警报 — 配置、约束、推荐默认值 |
| [log-insights.md](references/cloudwatch/log-insights.md) | 完整查询语法、命令、函数、已知问题、可重用查询库 |
| [metrics.md](references/cloudwatch/metrics.md) | 自定义指标、EMF 规范、指标过滤器、高分辨率、保留 |
| [tracing.md](references/cloudwatch/tracing.md) | X-Ray → ADOT 迁移、采样规则、注释 vs 元数据、收集器配置 |
| [dashboards.md](references/cloudwatch/dashboards.md) | 小部件类型、跨账户/区域、动态标签、共享 |
| [troubleshooting.md](references/cloudwatch/troubleshooting.md) | 所有可观察性服务的错误 → 原因 → 修复 |
| [cloudtrail.md](references/cloudwatch/cloudtrail.md) | 运营审计、事件类型、S3+Athena 查询 |
| [synthetics.md](references/cloudwatch/synthetics.md) | 金丝雀运行时/蓝图约束、VPC 网络配置、常见失败 |
| [dynamic-instrumentation.md](references/cloudwatch/dynamic-instrumentation.md) | 动态代理调试循环 — 实时代码上的断点/探针，快照捕获 + 相关性分析，创建/删除门控，快照 PII 处理。通过 `scripts/cloudwatch/di_instrumentation.py` + `scripts/cloudwatch/di_snapshots.py` 运行；详细信息在 `dynamic-instrumentation/` |
| [alarm-template.ts](assets/cloudwatch/alarm-template.ts) | 最佳实践 CDK Lambda 监控（警报 + 仪表板） |
| [otel-config.yaml](assets/cloudwatch/otel-config.yaml) | ADOT 收集器配置用于 X-Ray 追踪 + CloudWatch EMF 指标 |

### `references/cloudwatch-omni/`

| 文件 | 内容 |
|------|------|
| [concepts.md](references/cloudwatch-omni/concepts.md) | Omni 是什么和不是什么；术语表（域、Space、数据集、授权、配置文件、查看器、警报、仪表板、上下文图、评估器）；Omni vs CloudWatch 功能等效矩阵；如何判断客户指的是哪个产品；设置顺序及其位置 |
| [context-graph.md](references/cloudwatch-omni/context-graph.md) | Omni 从追踪和指标构建的服务/资源拓扑；`GetContextGraph` 请求/响应和 CLI；读取上游 vs 下游和爆炸半径；从洞察或异常逐跳走到根本原因，然后转向查询 |
| [programmatic-access.md](references/cloudwatch-omni/programmatic-access.md) | 公共 SigV4 API（`cloudwatch-omni` 端点前缀、`cloudwatch` 签署名称），程序化调用者的授权方式，CLI/SDK 访问（以及为什么不支持服务错误是客户端版本问题），CloudFormation/CDK，AI 编码代理，以及要避免的错误答案 |
| [query/sql-logs-traces.md](references/cloudwatch-omni/query/sql-logs-traces.md) | 日志和追踪上的 SQL — 表格寻址、所需时间范围、系统字段、字段访问和引号、模式发现、支持的操作、函数、常见模式（包括 `durationNano` 跨度持续时间），约束，TABLESAMPLE |
| [query/promql-metrics.md](references/cloudwatch-omni/query/promql-metrics.md) | Omni 中的指标是 PromQL — 可查询的内容（OTLP、span RED、OTel 增强的销售指标）和不可查询的内容，标签约定，`__name__` 匹配器，计数器上的 rate()，每个 AWS 服务的指标目录，衍生公式和维度陷阱 |
| [query/views.md](references/cloudwatch-omni/query/views.md) | 命名 SQL 查看器：CreateView / UpdateView / DeleteView / ListViews，`FROM view.<name>`，命名和定义规则，组合模式 |
| [dashboards.md](references/cloudwatch-omni/dashboards.md) | Omni 仪表板 — 组合配方、固定面板查询、`panels[]` 身体和面板类型、可视化、60 列网格、API 保存语义（未知的根/面板键被拒绝 400；`config` 内未知键保存 200 并在渲染时被忽略；保存前验证），修复空/空白面板，创建/获取/列出/更新/删除 OmniDashboard API，原型模板 |
| [alerts.md](references/cloudwatch-omni/alerts.md) | Omni 警报 — 警报 vs 警报，评估（FIELD_VALUE / COUNT_OF_RESULTS，贡献者），状态和无数据处理，通知规则，逐步创建/更新/删除/标记/获取，以及警报 API |
| [agent-evaluation.md](references/cloudwatch-omni/agent-evaluation.md) | OTel 追踪上的代理质量评估 — 代理健康审计，评估器选择，按需评分，在线评估，自定义评估器，从追踪构建数据集，以及读取存储的 `gen_ai.evaluation.*` 分数（检索计划 + SQL 机制）。使用 `scripts/cloudwatch-omni/evaluate_traces.py` 和 `scripts/cloudwatch-omni/capture_dataset_from_traces.py` |
