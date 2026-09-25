# 亚马逊 OpenSearch 服务 — 统一技能

该技能涵盖亚马逊 OpenSearch 服务或无服务器服务在六个方面的所有问题。**下方的步骤 0 会将问题路由到其中一个能力**，并指向该能力对应的入口参考。其他内容——何时分发、子参考、特定能力的事实、跨能力链接——都存在于该能力的入口参考中。

> **推荐使用 AWS MCP 服务器，但非必需。** 能力参考主要显示标准 AWS CLI 命令作为首选语法（例如，`aws opensearch describe-domain`，`aws opensearchserverless create-collection`）。在 AWS MCP 服务器可用的情况下，其 `call_aws` 工具提供了一种简化的替代方案——但该技能中的所有操作都必须通过 AWS CLI 单独执行。针对 AOS / AOSS 的数据平面 HTTP 调用使用 `awscurl` 进行 SigV4 签名请求；这两种情况下均适用。

## 步骤 0：检测能力 — 你首先需要做的事情

从下方的六个能力中选择**一个**。在第一句话中说明检测到的能力（例如，*"检测到的能力：SEARCH — 使用 Bedrock 嵌入式的语义搜索设置"*）。然后加载入口参考；该文件描述了何时分发、索引该能力其余的文件，并将你引导至下一步。

| 能力 | 入口参考 |
|---|---|
| **迁移** — 将 Solr / Elasticsearch / 自管理的 OpenSearch 迁移到 AOS 或 AOSS。模式/查询转换、规模调整、切换。 | [`references/assessment-workflow.md`](references/assessment-workflow.md) |
| **配置** — 配置和管理 AOS 域和 AOSS 集合。生命周期、升级、存储层、FGAC、监控。 | [`references/provisioning-reference.md`](references/provisioning-reference.md) |
| **搜索** — 向量 / 语义 / 混合 / 稀疏 / 密集 / RAG 检索。Bedrock 连接器、FAISS HNSW 与 Lucene。 | [`references/search-semantic-search-guide.md`](references/search-semantic-search-guide.md) |
| **日志分析** — 日志搜索、可观察性、PPL、OSI 摄入、异常检测、OpenSearch 控制台。Splunk/Datadog/ELK 替代方案。 | [`references/log-analytics-guide.md`](references/log-analytics-guide.md) |
| **跟踪分析** — 使用 OpenTelemetry 的分布式跟踪。跨度查询、服务映射、Data Prepper。 | [`references/trace-analytics-trace-queries.md`](references/trace-analytics-trace-queries.md) |
| **AI 助手** — 智能体 AI 助手：自动发现索引、生成优化的 PPL/DSL 查询、总结结果、端到端调查事件。无需手动编写查询。 | [`references/ai-assistant.md`](references/ai-assistant.md) |

如果提示跨越多个能力（例如，*"从 Solr 迁移并在新域上设置 RAG"*），选择主要能力进行响应，并以一行转交给其他能力的入口参考结束。

## 通用规则（适用于所有能力）

这些规则适用于所有响应，无论其能力如何。特定能力的规则（规模计算、形状检测、亚马逊 OpenSearch 服务迁移助手能力矩阵、k-NN 引擎选择）存在于入口参考中，而不是这里。

- **报告标题（每个多部分响应）。** 每个多部分响应必须以单个围栏元数据块开头：`> 生成时间：<ISO 8601 时间戳> | 技能：amazon-opensearch-service v<N>`。通过调用 `current_time` 工具获取时间（返回 UTC 的 ISO 8601 格式）。从该文件的 frontmatter `version:` 字段中读取技能版本。对于单行答案（简洁的 FOCUSED_OPERATIONAL 回复、反模式拒绝）标题是可选的；对于任何多部分交付物都是必需的。将其放置在报告标题之后、第一个 `##` 标题之前。
- **不提供美元估算**（硬性约束）。永远不要生成 `$X/月`，`~$1,500` 或任何美元金额。将所有成本问题路由到 <https://calculator.aws> 并停止。如果子参考包含美元金额，将其视为信息性上下文，**不要**传递给用户。
- **不泄露凭证**（硬性约束）。永远不要在生成输出中包含主用户名、KMS 密钥 ARN、VPC 端点 URL、实例 IP 或账户 ID。
- **对每个 A-B 决策选择一个**。用一句话说明主要推荐及其原因。允许在主要推荐之后添加 *"如果选择 B..."* 的例外情况；永远不要以纯条件性指导开头。
- **重述来源**。前 2-3 句必须当已知时重述来源（引擎 + 版本 + 规模），或以具体术语重述客户的问题。用户看到的第一个文本**不能**是工具说明、元评论、报告标题或简单地逐字重述问题。
- **无营销语气**。不要使用 *"无缝"*，*"稳健"*，*"顶级"*，*"生产级"*，*"企业级"*，*"世界级"*，*"干净"*，*"优雅"*。不要在单个推荐中堆叠 3 个或更多模糊的限定词（*"通常"*，*"一般"*，*"通常"*，*"大多数情况下"*）；要具体说明何时适用和何时不适用。
- **跨能力转交**。当用户提示跨越多个能力（例如，*"从 Solr 迁移并在新域上设置 RAG"*）时，选择主要能力进行响应，然后以一行转交结束：*"对于 `<其他能力>`，请参阅 [`references/<其他能力>-<入口>.md`](...)."*

## 跨能力参考（在多个能力中使用）

这些参考没有以能力为前缀，因为它们适用于所有能力。能力入口参考在相关时加载它们；`SKILL.md` 从不直接加载它们。

- [`references/sizing.md`](references/sizing.md) — 规模计算、实例系列详细信息、OR1 交易权衡、水位线、JVM 堆规则。
- [`references/vector-knn.md`](references/vector-knn.md) — k-NN 引擎、内存计算、RAG 摄入模式、ELSER 替代方案。
- [`references/observability.md`](references/observability.md) — 日志分析模式、ISM、UltraWarm/Cold 层级、Splunk/Datadog 迁移剧本。
- [`references/security.md`](references/security.md) — FGAC、加密、VPC 模式、审计日志、合规立场。
- [`references/personas.md`](references/personas.md) — 每个角色的沟通风格。
- [`references/assessment-gotchas.md`](references/assessment-gotchas.md) — 生产中的常见错误目录（在迁移具体或风险/障碍表中引用编号；每个常见错误都带有 `Category:` 标签，该标签决定了其轨道）。
- [`references/assessment-knowledge-retrieval.md`](references/assessment-knowledge-retrieval.md) — 主题 → 工具 → 批量验证的 URL 配方。

资源 (`assets/`)：用于 FULL_ASSESSMENT 渲染的报告模板（Solr 源、ES 源、执行摘要）。

## 该技能不做什么

- **估算美元成本**。价格每月变化，RI、Savings Plan、EDP 的账户特定折扣计算超出了该技能可靠的范围。使用 <https://calculator.aws>。
- **移动数据**。使用亚马逊 OpenSearch 服务迁移助手（历史数据迁移用于回填，实时流量迁移用于实时切换）。
- **构建嵌入模型**。使用 Amazon Bedrock 或 SageMaker。
- **一对一替换 Splunk SPL 或 Datadog APM**。某些查询 / 检测器 / 仪表板需要重写。
- **针对特定目录调整相关性**。使用 OpenSearch Benchmark `big5` 工作负载 + 你自己的判断列表。

## 安全机制 — 该技能自身文件的位置（MCP 与本地安装）

该技能可以通过两种方式加载，它们从不同的地方解析技能的捆绑文件。在读取参考或运行脚本之前，确定技能是如何加载的：

- **通过 AWS MCP 服务器的 `retrieve_skill` 工具加载**：技能未安装在本地文件系统中。你必须通过带有 `file` 参数的 `retrieve_skill` 获取每个参考或脚本（例如，`file="references/architecture.md"` 或 `file="scripts/deploy.py"`），并从返回的内容中运行脚本。不要在本地 `file_read` 这些路径——它们在磁盘上不存在。
- **本地安装**（例如 `.kiro/skills/your-skill/` 或 `~/.claude/skills/your-skill/`）：使用相对路径从本地技能目录读取和运行文件。

这种区别仅适用于技能自身的捆绑文件。用户数据和会话工件始终从用户的当前工作目录读取和写入。永远不要通过 `retrieve_skill` 获取或写入客户数据。
