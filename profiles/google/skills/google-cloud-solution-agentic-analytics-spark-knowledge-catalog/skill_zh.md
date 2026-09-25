# 跨云服务提供商和数据类型的代理式分析

此技能提供了一个工作流程，用于设计和实施一个受管理的、安全的管道，用于跨结构化和非结构化数据（这些数据分布在 Google Cloud、本地系统和其他云服务提供商上）的代理式分析解决方案。

## 工作流程概述

该工作流程由以下阶段组成：
*   **阶段 1：需求发现**。收集与用户需要协助的云工作负载或用例相关的详细需求。
*   **阶段 2：解决方案架构**。使用阶段 1 中收集的需求，为云工作负载或用例生成详细的解决方案架构。
*   **阶段 3：解决方案验证**。创建一个计划来验证生成的解决方案，生成验证说明和脚本，并运行验证。
*   **阶段 4：解决方案打包和展示**。整合生成的内容并展示解决方案。

**关于工作流程的重要说明**：
*   **严格的阶段分离**：在阶段 1（需求发现）期间，当您向用户询问澄清问题时，**不要**推荐、提出或概述任何架构设计、技术分解、云服务或组件映射。
*   **何时可以跳过某些阶段**：如果用户的提示表明此工作流程中的特定阶段或任务已经完成或已批准（例如，“需求发现阶段已完成”、“产品选择已批准”或“架构已确认”），**不要**重复该阶段或任务。相反，直接跳转到请求的任务（例如，生成技术分解、推荐产品或编制解决方案指南）。

## 阶段 1：需求发现和分析

1.  要求用户描述其工作负载的功能需求（业务流程、活动和用例）。一次问一个问题，要求用户回答以下问题：
    -   您的主要库存数据源是什么？它们是非结构化的（例如，PDF 风格的配方、发票）还是结构化的（例如，Iceberg 中的历史销售数据）？
    -   这些源在哪里托管？它们是否分布在 AWS S3、Azure Blob、Google Cloud Storage 或 AlloyDB 等数据库中？
    -   您如何在 Google Cloud 和外部位置（如其他云服务提供商）内管理和联邦跨数据源元数据？
    -   您在跨大规模分布式数据上执行连接、清理和运行预测模型所需的分析和计算需求是什么？
    -   您的数据科学家或操作代理在他们的代理式 IDE（VS Code 或 Antigravity IDE）中期望执行哪些类型的自然语言提示？
2.  要求用户描述其工作负载的非功能性需求。

    以下是一些收集非功能性需求时可问问题的示例：
    -   **安全、隐私和合规性**：系统必须遵守哪些数据隐私规则、监管合规性（例如，GDPR、HIPAA）或数据治理要求？
    -   **可靠性**：您的可用性、高可用性、容错性和灾难恢复目标（RTO/RPO）是什么？
    -   **性能**：您的工作负载需要哪些目标查询延迟和 SLA 期望？
    -   **运营**：您的数据科学家和工程师需要哪些运营监控指标？
    -   **成本与可持续性**：您是否有特定的预算限制和数据出口/传输成本要求？
3.  询问用户当前的工作负载是否运行在其他云服务提供商或本地。
    *   如果用户回答“是”，则要求用户描述当前部署的架构。
    *   如果用户回答“否”，则继续下一步。
4.  要求用户描述对其他工作负载、产品或工具的任何依赖关系。以下是一些获取依赖关系信息时可问问题的示例：
    *   您对外部系统（例如，身份提供程序、数据管理平台、CI/CD 管道或活动数据目录）是否有任何上游或下游依赖关系？
    *   您的一般数据工程软件交付生命周期是否有任何要求（例如，版本控制、测试、数据质量保证）？提供目录路径或这些工件的示例。
5.  审查用户迄今为止提供的输入，并检查是否存在任何歧义或矛盾。

    如果您在用户提供的需求数据中识别到任何歧义或矛盾（例如，零拷贝与将数据复制到存储库），则针对您识别的每个歧义或矛盾执行以下操作：
    *   描述歧义或矛盾（例如，解释为什么复制数据与零拷贝要求矛盾，并且还会产生数据传输成本）。
    *   询问用户他们希望如何解决歧义或矛盾。
        *   如果用户将选择权委托给您（例如，用户回复“做你认为最好的”或“你决定”），则提供一个清晰的建议来解决歧义或矛盾（例如，建议优先考虑零拷贝远程查询），解释您的理由（例如，以消除多云费用和数据重复），并要求用户批准您的建议。

    **关键**：直到您识别的所有歧义和矛盾都按照前面的指导得到解决，您**必须**不得推荐或生成任何架构设计、技术分解或 Google Cloud 产品推荐。

6.  **重要**：如果阶段 5 中存在未解决的矛盾或歧义，**不要**开始此步骤。

    生成工作负载组件的技术分解。
    *   技术分解必须将解决方案分解为逻辑组件。
    *   分解**必须**解决相关层中的基于角色的安全性和凭证。
    *   分解**必须**按以下四个层组织，这些层代表代理式分析解决方案的标准架构模式，从用户交互流经数据上下文和治理到核心数据处理：
        *   **用户交互层（IDE）**：例如，代理式开发环境。
        *   **基础和可信数据**：例如，云中的基础模型、MCP 服务器和数据仓库。
        *   **元数据管理**：例如，元数据扫描。
        *   **数据处理和分析**：例如，分析工作流、Spark 数据处理和外部数据存储。
7.  要求用户批准生成的技术分解。
8.  如果用户请求更改，则生成更新的技术分解。
9.  重复步骤 5 至 8，直到用户批准生成的技术分解。
10. 用户批准技术分解后，继续阶段 2。
    **重要**：在用户批准工作负载的技术分解之前，**不要**进入下一阶段。

## 阶段 2：解决方案架构

### 基于生成的所有内容

为了确保此阶段中生成的所有内容与最新的官方 Google Cloud 指南保持一致，请使用以下资源对生成的所有内容进行基础：

*   Google Developer Knowledge MCP 服务器
    *   连接到 MCP 服务器的说明：
        https://developers.google.com/knowledge/mcp.md.txt
    *   服务器：https://developerknowledge.googleapis.com/mcp
        *   工具：
            *   `developerknowledge:search_documents`
            *   `developerknowledge:get_documents`
            *   `developerknowledge:answer_query`
*   https://github.com/google/skills 中的相关技能
*   官方 Google Cloud 文档，包括以下内容：
    *   跨多云数据湖、结构化数据仓库和非结构化数据存储的代理式跨云分析工作流的参考架构：
        https://docs.cloud.google.com/architecture/agentic-ai-cross-cloud-analytics.md.txt
    *   与工作负载相关的产品和主题的决策指南：
        https://github.com/google/skills/blob/main/skills/cloud/google-cloud-solution-architecture/references/decision-making-guides.md
    *   与工作负载相关的产品和主题的最佳实践指南：
        https://github.com/google/skills/blob/main/skills/cloud/google-cloud-solution-architecture/references/best-practices-guides.md

### 任务 2.1：确定工作负载所需的 Google Cloud 产品和功能

1.  对于确认技术分解中的每个组件，根据以下资源中的指导并根据批准的技术分解适当地识别适当的 Google Cloud 产品和功能：
    *   `references/product-selection-guidance.md`
    *   `https://github.com/google/skills/blob/main/skills/cloud/google-cloud-solution-architecture/references/decision-making-guides.md`
2.  展示生成的产品推荐，并要求用户批准推荐。
3.  如果用户请求更改，则进行必要的更改。
4.  重复步骤 2 和 3，直到用户批准产品推荐。
5.  用户批准产品推荐后，继续任务 2.2。

### 任务 2.2：生成架构图

1.  使用 Mermaid 格式生成架构图：
    https://github.com/mermaid-js/mermaid
2.  向用户展示生成的图，并要求用户批准架构图。
3.  如果用户请求更改，则进行必要的更改。
4.  重复步骤 2 和 3，直到用户批准架构图。
5.  用户批准架构图后，继续任务 2.3。

### 任务 2.3：生成架构描述

1.  生成一个描述，解释每个组件的用途、组件之间的关系以及任务流或数据流。
2.  向用户展示生成的架构描述，并要求用户批准描述。
3.  如果用户请求任何更改，则进行必要的更改。
4.  重复步骤 2 和 3，直到用户批准架构描述。
5.  用户批准架构描述后，继续任务 2.4。

### 任务 2.4：生成设计建议

1.  根据工作负载的需求，生成设计建议和最佳实践，以优化架构中每个组件的配置。

    **重要**：
    *   在生成设计建议时，请考虑以下内容：
        *   在阶段 1 中收集的功能需求。
        *   在阶段 1 中收集的非功能性需求。
    *   将生成的设计建议与 `references/design-recommendations.md` 中的建议保持一致。
    *   要为 Knowledge Catalog 生成设计建议，请使用以下资源：
        `references/knowledge-catalog-documentation.md`
    *   要为非功能性需求生成指导，请使用以下技能：
        *   `google-cloud-waf-security`
        *   `google-cloud-waf-reliability`
        *   `google-cloud-waf-cost-optimization`
        *   `google-cloud-waf-operational-excellence`
        *   `google-cloud-waf-performance-optimization`
        *   `google-cloud-waf-sustainability`
2.  向用户展示生成的设计建议，并询问用户是否需要任何更改。
3.  如果用户需要更改，则进行必要的更改。
4.  重复步骤 2 和 3，直到用户确认生成的设计建议满足其需求。
5.  继续任务 2.5。

### 任务 2.5：生成部署指南

1.  生成部署指南，包括代码和说明，以使用户能够部署解决方案。

    **重要**：
    *   指南必须提供部署先决条件的步骤，包括设置 Google Cloud 项目、启用计费、启用所需的 API 以及设置所需的角色和权限。
    *   使用以下资源作为生成部署指南的技术基础：
        -   https://github.com/gemini-cli-extensions/data-agent-kit-starter-pack/tree/main/skills：
            一个插件，提供了一套专门的技能和 MCP 工具，让您可以使用首选的编码代理来设计复杂的数据管道，使用 dbt 转换数据，编写 Spark 和 BigQuery SQL 笔记本，创建和排错 Dataflow 管道，并在 Google Cloud 数据生态系统内编排端到端工作流。
        -   https://codelabs.developers.google.com/next26/gen-keynote/raw-data-forecasting#0：
            一个 codelab，提供使用 Data Agent Kit 扩展在首选的代理式开发环境中高效分析跨云数据拓扑的说明。
        -   https://codelabs.developers.google.com/governance-context-part1#0： 一个 codelab，提供使用 Gemini CLI 在 BigQuery 中构建数据基础、应用严格的元数据标签（Knowledge Catalog Aspects）以区分有效数据与噪声，并本地测试 LLM 是否严格遵循您的治理规则的说明。
        -   https://docs.cloud.google.com/dataplex/docs/establish-foundational-data-context.md.txt：
            一个教程，展示了如何在 Knowledge Catalog 中建立数据上下文。
        -   https://docs.cloud.google.com/dataplex/docs/ingest-custom-sources.md.txt：
            一个指南，解释了如何将有关您独特、自定义数据源的信息带入 Knowledge Catalog。
2.  向用户展示生成的部署指南，并询问用户是否需要任何更改。
3.  如果用户请求更改，则进行必要的更改。
4.  重复步骤 2 和 3，直到用户确认生成的部署指南满足其需求。
5.  继续阶段 3。

## 阶段 3：解决方案验证

1.  创建一个计划来验证生成的解决方案。该计划必须概述验证生成的解决方案是否符合工作负载需求的步骤。
2.  向用户展示验证计划并请求反馈或批准。
3.  如果用户请求更改，则按需更新计划。
4.  重复步骤 2 和 3，直到用户批准验证计划。
5.  使用 `curl` 或 `gcloud` 等工具生成脚本或命令来执行批准的验证计划中的步骤。
6.  请求用户允许执行验证检查。
7.  如果用户给予许可，则运行验证检查并排错任何部署问题。
8.  当所有验证检查通过时，继续阶段 4。

## 阶段 4：解决方案打包和展示

1.  将阶段 2 和阶段 3 中生成的文本工件整合到一个名为 `solution-architecture-guide.md` 的 Markdown 文件中，基于 `assets/output-template.md` 中的模板。
2.  向用户展示整合的 `solution-architecture-guide.md`。
3.  请求用户允许在用户的工作区中写入代码文件。
4.  用户给予许可后，在用户的工作区中写入代码文件。

## 支持资源

*   https://docs.cloud.google.com/data-cloud-extension/antigravity/transform-data.md.txt：
    Data Agent Kit 扩展如何使用笔记本进行数据转换和分析的指南。
*   https://docs.cloud.google.com/dataplex/docs/use-cases.md.txt： Knowledge Catalog 的用例。
*   https://docs.cloud.google.com/managed-spark/docs/guides/lightning-engine.md.txt：
    使用 Lightning Engine 加速 Apache Spark 工作负载的指南。
*   https://docs.cloud.google.com/bigquery/docs/use-knowledge-catalog.md.txt：
    指南，说明如何将 Knowledge Catalog 作为 BigQuery 的治理和代理式层使用。
