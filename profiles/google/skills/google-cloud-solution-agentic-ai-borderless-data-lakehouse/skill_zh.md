# 无边界开放数据湖屋智能AI系统

遵循以下工作流程，帮助用户为给定的业务负载、用例或需求，在云端设计和实施定制的多产品解决方案。

## 产品重命名与术语

在生成解决方案设计、架构图和文档时，请使用更新的Google Cloud产品名称。有关旧版与更新版产品名称和术语的详细信息，请参阅[references/product_renaming.md](references/product_renaming.md)。

## 工作流程

解决方案设计与实施工作流程包括以下阶段：

- **阶段1：需求发现与分析**：分析业务负载的需求、约束、依赖关系和当前状态。
- **阶段2：解决方案设计**：基于Google Cloud设计最佳实践和建议，为业务负载构建技术栈、架构和部署配置。
- **阶段3：实施计划**：生成自动化和说明以部署解决方案。
- **阶段4：解决方案验证**：验证部署是否满足业务负载的需求。

### 阶段1：需求发现与分析

- [ ] **步骤1：发现需求**：了解业务负载的功能和非功能需求、业务目标以及当前状态（如有），包括其架构、依赖关系和约束。使用以下问题指导需求发现过程：
   - 你的主要数据源是什么？
   - 你如何跨数据源管理和联邦元数据？
   - 你的安全和凭证管理需求是什么？
   - 对此无边界数据进行连接和转换需要哪些分析和计算需求？
   - 你期望AI代理或最终用户针对此数据执行哪些自然语言提示或用户查询？

- [ ] **步骤2：识别组件**：根据需求分析，识别业务负载的组件及其关系。同时识别解决方案需要集成的任何无边界组件、混合组件或本地组件。

- [ ] **步骤3：生成组件分解**：生成业务负载组件的技术分解。

- [ ] **步骤4：请求确认**：请用户确认生成的技术分解是否满足其业务负载需求。

- [ ] **步骤5：迭代**：如果用户请求更改，则生成更新的技术分解，并请用户确认更改。继续迭代，直到用户确认技术分解。

### 阶段2：解决方案设计

- [ ] **步骤1：检索相关Google Cloud文档**：使用可用的搜索或获取工具，在继续执行本阶段剩余步骤之前，阅读以下Google Cloud文档的内容，以将你生成的指导与Google Cloud设计最佳实践相结合。
   - [使用Google Cloud构建混合和无边界架构](https://docs.cloud.google.com/architecture/hybrid-multicloud-patterns/one-page-view.md.txt)
   - [构建无边界开放数据湖屋](https://docs.cloud.google.com/architecture/agentic-ai-build-multicloud-open-data-lakehouse.md.txt)
   - [为分布式数据实现智能分析工作流](https://docs.cloud.google.com/architecture/agentic-ai-cross-cloud-analytics.md.txt)
   - [分析混合和多云模式](https://docs.cloud.google.com/architecture/hybrid-multicloud-patterns-and-practices/analytics-hybrid-multicloud-pattern.md.txt)
   - [Google Cloud多区域部署原型](https://docs.cloud.google.com/architecture/deployment-archetypes/multiregional.md.txt)
   - [跨云网络中分布式应用程序的网络分段和连接](https://docs.cloud.google.com/architecture/ccn-distributed-apps-design/connectivity.md.txt)
   - [连接其他云服务提供商与Google Cloud的模式](https://docs.cloud.google.com/architecture/patterns-for-connecting-other-csps-with-gcp.md.txt)

  *重要*：使用从Google Cloud文档中检索的内容，以将你生成的指导与本阶段剩余步骤相结合。

- [ ] **步骤2：将组件映射到Google Cloud产品**：对于确认的技术分解中的每个组件，根据[references/product_mapping.md](references/product_mapping.md)中的指南，识别适当的Google Cloud产品和功能。

- [ ] **步骤3：创建架构图**：创建一个显示组件、其关系和数据/控制流的架构图。
   - 图表必须使用Mermaid格式：https://github.com/mermaid-js/mermaid。
   - 图表必须清晰地区分数据摄取子系统和服务子系统中的产品。
   - 图表必须将Managed Service for Apache Spark显示为ETL/摄取处理的共享组件，连接数据摄取和服务子系统（不同于交互式IDE分析工作流）。

- [ ] **步骤4：生成设计建议**：根据[references/design_recommendations.md](references/design_recommendations.md)中的指南，生成设计指导。

- [ ] **步骤5：草拟解决方案架构**：根据[assets/output-template.md](assets/output-template.md)中的模板，将需求、技术分解、产品映射、架构图和设计建议汇编到一个名为`solution-architecture-guide.md`的Markdown文件中。

- [ ] **步骤6：请求评审**：向用户展示生成的解决方案架构，并请求他们的反馈或批准。

- [ ] **步骤7：迭代**：如果用户请求更改，则生成更新的解决方案架构，并重复步骤2-6，直到用户批准解决方案架构。

### 阶段3：实施计划

- [ ] **步骤1：检索相关实施资源**：
   - [使用智能AI构建多云开放数据湖屋](https://codelabs.developers.google.com/next26/multicloud-lakehouse)
   - [biglake_iceberg_catalog的Terraform Registry文档](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/biglake_iceberg_catalog)
   - [在Lakehouse运行时目录中创建具有元数据的Apache Iceberg表](https://docs.cloud.google.com/managed-spark/docs/guides/spark-workloads-with-bigquery-metastore.md.txt)
   - [使用Lightning Engine加速Spark批处理工作负载和会话](https://docs.cloud.google.com/managed-spark/docs/guides/lightning-engine-serverless.md.txt)
   - [创建数据代理](https://docs.cloud.google.com/bigquery/docs/create-data-agents.md.txt)

  *重要*：使用这些资源作为本阶段剩余步骤中生成的IaC和部署说明的技术基础。

- [ ] **步骤2：识别部署先决条件**：记录部署的先决条件，包括以下内容：
   - 项目和计费关联
   - 所需的Google Cloud API
   - 所需的IAM权限
   - 任何其他先决条件

- [ ] **步骤3：生成基础设施即代码（IaC）**：生成代码（例如，Terraform）和部署脚本，以自动化提议的Google Cloud资源的配置。

- [ ] **步骤4：编写部署说明**：草拟按顺序、分步骤的部署说明，以执行IaC并初始化业务负载组件。

- [ ] **步骤5：请求评审**：向用户展示生成的部署说明，以供反馈和确认。

- [ ] **步骤6：迭代**：如果用户请求更改，则生成更新的实施计划，并重复步骤2-5，直到用户批准实施计划。

### 阶段4：解决方案验证

- [ ] **步骤1：检索相关验证资源（可选）**：如果第3阶段的资源尚未在您的上下文中，请检索相同的实施资源，作为本阶段生成的验证检查和验证脚本的基础。

- [ ] **步骤2：定义验证检查**：概述验证步骤，以验证部署的基础设施是否满足业务负载需求：
   - **部署干运行**：如`terraform plan`等命令，以预览更改。
   - **连接性和路由**：验证网络路径、负载均衡器路由和服务端点。
   - **安全策略**：验证受限访问、防火墙规则和IAM强制执行。

- [ ] **步骤3：生成验证脚本**：草拟轻量级脚本或命令行说明（例如，使用`curl`或`gcloud`），用户可以运行这些脚本来执行这些验证检查。

- [ ] **步骤4：汇编验证报告**：将验证步骤、验证脚本和预期结果记录在一个Markdown文件中。

- [ ] **步骤5：执行验证并最终确定**：协助用户执行验证检查并排除任何部署问题。解决方案验证成功后，请求用户最终批准。

- [ ] **步骤6：迭代**：如果用户请求更改，则生成更新的验证计划，并重复步骤2-5，直到用户批准验证计划。
