---
name: google-cloud-solution-hybrid-search-alloydb
description: 通过结合语义搜索和关键词搜索，发现需求并生成动态混合搜索系统的架构、设计和部署指南。专为 Google Cloud 中的 AlloyDB 混合搜索用例进行优化。当用户需要将向量搜索与结构化 SQL 过滤、分面属性、语义重新排序、数据库内 AI 验证或跨事务关系数据库、分析数据仓库或托管数据库引擎的服务器less托管相结合时，请使用此技能。不应用于简单的关键词搜索，或在需要独立非关系向量数据库时使用。
---

# 使用 AlloyDB 进行动态混合搜索

这项技能提供了一个工作流程，用于设计和实现安全、低延迟和高精度的混合搜索解决方案，结合了结构化数据集过滤、向量搜索索引、分面元数据过滤、语义重新排序、召回评估、数据库内 AI 验证、数据库抽象层和服务器less 应用托管。

## 工作流程概述

该工作流程包含以下阶段：

1. **需求发现**。收集与用户需要协助的云工作负载或用例相关的详细需求。
2. **解决方案架构**。使用在阶段 1 中收集的需求，为云工作负载或用例生成详细的解决方案架构。
3. **解决方案验证**。创建一个验证生成解决方案的计划，生成验证说明和脚本，并运行验证。
4. **解决方案打包和展示**。整合生成的内容，并展示解决方案。

**关于工作流程的重要说明**：

- **严格的阶段分离**：在阶段 1（需求发现）中，当您向用户询问澄清问题时，**不要**推荐、提出或概述任何架构设计、云服务或组件映射。这可以防止在完全了解范围之前过早做出架构承诺或产生幻觉。
- **暂停以获取批准**：对于任何指示“在继续之前获取批准”的步骤，您**必须**停止执行，向用户展示已完成的任务，并等待他们的明确批准。您**必须**不执行任何后续任务或在该响应中生成任何进一步指导。
- **所有生成内容均需基于事实**：对于所有阶段的所有任务，您**必须**首先查阅以下资源：
  - [产品映射](references/product-mapping.md)，
  - [设计建议](references/design-recommendations.md)以获取所需指导。如果指导没有提供所需信息，您**必须**使用以下资源来使生成的内容基于事实：

  - Google 开发者知识 MCP 服务器：
    https://developers.google.com/knowledge/mcp.md.txt
    - 服务器：https://developerknowledge.googleapis.com/mcp
      - 工具：
        - `developerknowledge:search_documents`
        - `developerknowledge:get_documents`
        - `developerknowledge:answer_query`
  - 来自 https://github.com/google/skills 的相关技能
  - 官方 Google Cloud 文档，位于
    [相关指导](references/related-guidance.md)

## 产品重命名和术语

在生成解决方案设计、架构图和文档时，请查阅最新的 Google Cloud 文档以获取最准确的产品名称。下表提供了需要注意的名称映射示例。请注意，底层 API、Terraform 资源和 IAM 角色可能保留其传统标识符。

<table>
  <thead>
    <tr>
      <th>传统名称</th>
      <th>更新名称</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Vertex AI</td>
      <td>Gemini Enterprise Agent Platform</td>
      <td>Gemini Enterprise Agent Platform 在首次提及后可以简称为 Agent Platform</td>
    </tr>
    <tr>
      <td>Vertex AI Embedding</td>
      <td>Text embedding on Gemini Enterprise Agent Platform</td>
      <td>这指的是 Gemini Enterprise Agent Platform 上可用的文本嵌入模型</td>
    </tr>
    <tr>
      <td>Vertex AI Matching Engine</td>
      <td>Vector Search</td>
      <td></td>
    </tr>
  </tbody>
</table>

## 阶段 1：需求发现

在此阶段，您必须收集与用户希望在 Google Cloud 中设计和部署的混合搜索工作负载相关的详细需求。

**确认提供的需求**：如果用户的提示中已经包含了一些需求（功能或非功能性，例如目录大小、搜索模态、分面属性或延迟目标），您**必须**明确确认并在您的响应中重述所有这些需求。**不要**要求用户描述或重新描述他们在提示中已经提供的需求。

严格按照指定顺序完成以下步骤：

- [ ] **步骤 1**：要求用户描述工作负载的功能需求，包括目录数据集详细信息（例如，电子商务服装、零售产品、专利数据库）、搜索模态（自然语言文本、视觉搜索、属性过滤器）、用于分面过滤的元数据属性（例如，`category`、`sub_category`、`color`、`gender`、`price`）和质量检查（重新排序、LLM 验证）。
- [ ] **步骤 2**：您**必须**明确要求用户描述以下六个类别的所有非功能性需求。您需要这些信息，因为每个类别都代表一个关键架构支柱，忽略任何一个类别都可能导致解决方案不安全、不可靠或效率低下（**不要**遗漏任何一个类别）：
  - **安全、隐私和合规性**：例如，私有 VPC 端点、Private Service Connect、Direct VPC Egress 和访问控制。
  - **可靠性**：例如，高可用性、故障转移、灾难恢复目标（RTO/RPO）、区域与多区域 AlloyDB 架构。
  - **成本**：例如，计算、数据库实例和 Gemini Enterprise Agent Platform API 调用的预算限制。
  - **运营卓越**：例如，监控、日志记录、仪表板和自动化部署。
  - **性能**：例如，目标 P95 查询延迟（例如，< 100ms）、向量搜索召回目标（例如，> 95%）、目录项目规模和 QPS 预期。
  - **可持续性**：例如，碳足迹、低碳区域选择。
- [ ] **步骤 3**：询问工作负载当前是否在运行于其他云服务提供商或本地。
  - 如果用户的答案是“是”，则要求用户描述当前部署的架构。
  - 如果用户的答案是“否”，则继续下一步。
- [ ] **步骤 4**：询问用户是否有任何对其他工作负载、产品或工具（例如，现有库存数据库、ERP 系统、应用程序运行时语言如 Java 或 Python）的依赖。

- [ ] **步骤 5**：审查用户到目前为止提供的输入，并检查功能需求、非功能性需求和依赖项中是否存在任何歧义、冲突或矛盾。您**必须**将所有需求相互比较以识别任何冲突。

  如果您在用户提供的需
