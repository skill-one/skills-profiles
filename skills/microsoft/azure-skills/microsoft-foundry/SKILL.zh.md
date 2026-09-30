---
name: microsoft-foundry
description: 构建、部署、评估、优化、微调和管理 Microsoft Foundry 代理、模型和资源。用途：Foundry、azd AI 代理、azd 创建/部署、托管代理脚手架/开发/运行/部署/排错、提示代理创建、创建代理、更新代理、向代理添加工具、调用代理、agent.yaml、代理洞察、拉取代理洞察、评估代理、批量评估、持续评估、持续监控、代理 CI/CD、优化提示、改进提示、提示优化器、优化代理指令、Agent Optimizer 脚手架、从跟踪中管理数据集、部署模型、模型微调（SFT/DPO/RFT）、Foundry 项目、RBAC、角色分配、权限、配额、容量、区域、部署失败、AI 服务、创建 Foundry 资源、知识索引、定制部署、入职、可用性、训练数据、评分器、蒸馏、大文件上传。不适用：Azure Functions、App Service、一般 Azure 部署（使用 azure-deploy）、一般 Azure 准备（使用 azure-prepare）。
---

# Microsoft Foundry 技能

此技能帮助开发者使用 Microsoft Foundry 资源，涵盖模型发现和部署、AI 代理的完整开发生命周期、评估工作流和故障排除。

## 执行前要求

在开始相应的操作或工作流之前，请遵循以下每个适用的子部分。

### 依赖项检查和设置

**必须执行：** 此技能加载后的第一步，请从技能的根目录运行以下依赖项检查和设置脚本，并等待其完成后再继续。该脚本会先检查并仅安装缺失的依赖项；不会重新安装已可用的依赖项。

**您必须在阅读或进入任何子技能、工作流或工作流特定参考之前完成此检查。**

```bash
./scripts/check-and-setup-dependencies.sh     # macOS / Linux
./scripts/check-and-setup-dependencies.ps1    # Windows (pwsh)
```

严格遵循脚本输出以进行后续操作。

### 工作流指南

**必须执行：** 在执行任何工作流特定步骤之前，您**必须**阅读相应子技能文档。不要在没有阅读其技能文档的情况下调用工作流特定的 MCP 工具。即使您已经知道 MCP 工具参数，也必须遵循此规则。此规则适用于每个触发不同工作流的新用户消息，即使技能已经加载。

### Foundry MCP

**必须执行：** 在使用 Foundry MCP 操作之前，请调用 Azure MCP `foundry` 工具并检查可用的 Foundry MCP 工具和相关参数。将其视为基于 MCP 的工作流发现/帮助步骤。

### azd

**必须执行：** 在执行任何 azd 命令之前，您**必须**阅读 [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) 并严格遵守其中定义的共享规则，特别是 `AZURE_DEV_USER_AGENT` 设置规则。

## 子技能

此技能包含针对特定工作流的专用子技能。**当子技能与任务匹配时，请严格遵循其工作流：**

| 子技能 | 使用场景 | 参考 |
|-----------|-------------|-----------|
| **deploy** | 部署托管代理到 Foundry、对部署进行冒烟测试、创建或更新提示代理、管理代理版本和多环境部署。 | [deploy](foundry-agent/deploy/deploy.md) |
| **cicd** | 为 Foundry 代理设置 CI/CD 部署管道。 | [cicd](foundry-agent/cicd/cicd.md) |
| **invoke** | 向代理发送消息、单轮或多轮对话 | [invoke](foundry-agent/invoke/invoke.md) |
| **routine** | 使用例程计划或事件触发 Foundry 代理；使用 `azd` 进行 CRUD、启用/禁用、手动调度和查看历史运行，或在 `azure.yaml` 中定义例程。 | [routine](foundry-agent/routine/routine.md) |
| **invocations-ws** | 构建、部署和连接到使用 `invocations_ws` 双向 WebSocket 协议的托管代理——语音代理、实时流和用于带外媒体传输的信令。 | [invocations-ws](foundry-agent/invocations-ws/invocations-ws.md) |
| **observe** | 评估代理质量、运行批量评估、分析失败、优化提示、改进代理指令、比较版本、设置 CI/CD 监控、启用持续生产评估 | [observe](foundry-agent/observe/observe.md) |
| **insights** | 从现有监控器中提取生成的代理洞察、证据和建议；仅读检索，不是新的分析运行 | [insights](foundry-agent/insights/insights.md) |
| **trace** | 查询跟踪、分析延迟/失败、通过 App Insights `customEvents` 将评估结果关联到特定响应 | [trace](foundry-agent/trace/trace.md) |
| **troubleshoot** | 查看托管代理日志、查询遥测数据、诊断失败 | [troubleshoot](foundry-agent/troubleshoot/troubleshoot.md) |
| **validate** | 仅在用户明确要求使用此验证子技能或验证 Microsoft Foundry 托管代理代码是否符合最佳实践时使用。切勿主动调用它或将其添加到其他工作流。 | [validate](foundry-agent/validate/validate.md) |
| **create (quick start)** | 从头开始端到端创建新的托管 Foundry 代理——创建脚手架、使用现有 Foundry 项目或创建新项目、部署和冒烟测试。不要用于任何现有代码的工作。对于快速启动未涵盖的内容，使用 **create**。 | [create/quick-start-hosted.md](foundry-agent/create/quick-start-hosted.md) |
| **create** | 当标准端到端快乐路径（快速启动）不适用时使用。创建新的 Foundry 代理、更新现有代理的代码、继续开发现有代理、在脚手架时间进行连接、使用高级设置或 A2A（Agent2Agent）、从失败的快速启动运行中恢复。 | [create](foundry-agent/create/create-hosted.md) |
| **agent-optimizer** | 使现有的 Python 托管代理代码优化就绪、配置 eval.yaml、运行 Agent Optimizer 任务、本地应用候选者、通过 azd 审查后部署。 | [agent-optimizer](foundry-agent/agent-optimizer/agent-optimizer.md) |
| **eval-datasets** | 将生产跟踪收集到评估数据集中、管理数据集版本和拆分、跟踪评估指标随时间变化、检测回归、维护从跟踪到部署的完整谱系。用于：从跟踪创建数据集、数据集版本控制、评估趋势、回归检测、数据集比较、评估谱系。 | [eval-datasets](foundry-agent/eval-datasets/eval-datasets.md) |
| **project/create** | 创建用于托管代理和模型的 Microsoft Foundry 项目。在 Foundry onboarding 或设置新基础设施时使用。 | [project/create/create-foundry-project.md](project/create/create-foundry-project.md) |
| **resource/create** | 使用 Azure CLI 创建 Azure AI Services 多服务资源（Foundry 资源）。在手动配置 AI Services 资源并需要细粒度控制时使用。 | [resource/create/create-foundry-resource.md](resource/create/create-foundry-resource.md) |
| **private-network** | 回答有关 Foundry 网络隔离的问题**并且**使用 VNet 隔离部署 Foundry（自备 VNet、托管 VNet、混合）。涵盖架构概念、模板选择、部署和部署后验证。 | [resource/private-network/private-network.md](resource/private-network/private-network.md) |
| **models/deploy-model** | 统一模型部署，具有智能路由。处理快速预设部署、完全自定义部署（版本/SKU/容量/RAI），以及跨区域的容量发现。路由到子技能：`preset`（快速部署）、`customize`（完全控制）、`capacity`（查找可用性）。 | [models/deploy-model/SKILL.md](models/deploy-model/SKILL.md) |
| **quota** | 管理Microsoft Foundry资源的配额和容量。在检查配额使用情况、由于配额不足导致部署失败时进行故障排除、请求配额增加或规划容量时使用。 | [quota/quota.md](quota/quota.md) |
| **rbac** | 管理Microsoft Foundry资源的 RBAC 权限、角色分配、托管身份和服务主体。用于访问控制、审计权限和 CI/CD 设置。 | [rbac/rbac.md](rbac/rbac.md) |
| **finetuning** | 在 Microsoft Foundry 上微调模型——SFT 摘要、DPO 偏好优化、带有评分器和工具调用的 RFT。数据集准备、评分器校准、训练、检查点选择、部署、评估。用于：微调、SFT、DPO、RFT、训练数据、评分器、摘要、微调模型、大文件上传。 | [finetuning/SKILL.md](finetuning/SKILL.md) |
| **azd-guidance** | 提供有关管理 Foundry 代理的共享 azd 知识和指导。对于任何与 azd 相关的工作流，请首先阅读此文档。 | [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) |

> 💡 **提示：** 对于完整的 onboarding 流程：`project/create`（公共）或 `private-network`（VNet 隔离）→ `models/deploy-model` → 代理工作流 (`create` → `deploy` → `invoke`)。

> 💡 **微调：** 使用 `finetuning` 进行所有模型定制——SFT 摘要、DPO 偏好优化和带有评分器的 RFT。包括快速启动、评分器校准和训练曲线分析。

> 💡 **模型部署：** 使用 `models/deploy-model` 进行所有部署场景——它智能地在快速预设部署、具有完全控制的定制部署和跨区域容量发现之间进行路由。

> 💡 **提示优化：** 对于“优化我的提示”或“改进我的代理指令”等请求，加载 [observe](foundry-agent/observe/observe.md) 并通过该评估驱动的工作流使用 `prompt_optimize` MCP 工具。

## 基础设施生命周期

将用户意图匹配到正确的基础设施工作流。

| 用户意图 | 工作流 |
|-------------|---------|
| "创建 Foundry" / "设置 Foundry"（模糊） | 使用 `AskUserQuestion`：(a) 仅 AI Services 资源，(b) 具有公共访问权限的项目，或 (c) 具有网络隔离的项目？路由：(a) → [resource/create](resource/create/create-foundry-resource.md)，(b) → [project/create](project/create/create-foundry-project.md)，(c) → [private-network](resource/private-network/private-network.md) |
| 使用 VNet 隔离设置 Foundry | [private-network](resource/private-network/private-network.md) |
| 创建 Foundry 项目（公共） | [project/create](project/create/create-foundry-project.md) |
| 创建裸 Foundry 资源 | [resource/create](resource/create/create-foundry-resource.md) |

## 代理开发生命周期

将用户意图匹配到正确的代理工作流。执行前请按顺序阅读每个子技能。

| 用户意图 | 工作流（按顺序阅读） |
|-------------|------------------------|
| 端到端创建新的托管代理（创建脚手架 + 部署 + 测试） | [dependency check and setup](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → [quick-start-hosted](foundry-agent/create/quick-start-hosted.md) (自包含端到端) |
| 超出标准快速启动的任何内容（现有代码、迁移、重新托管、部署自定义、脚手架时间连接、A2A（Agent2Agent）、恢复） | [dependency check and setup](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → [create](foundry-agent/create/create-hosted.md) → [deploy](foundry-agent/deploy/deploy.md) → [invoke](foundry-agent/invoke/invoke.md) |
| 优化现有的 Python 托管代理 | [dependency check and setup](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → [agent-optimizer](foundry-agent/agent-optimizer/agent-optimizer.md) → 脚手架/审查 → eval.yaml → 优化 → 本地应用候选者 → 部署 → invoke |
| 部署代理（代码已存在） | [dependency check and setup](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → 部署（包括 eval-suite 设置）→ invoke → observe (评估/优化) |
| 代码更改后更新/重新部署代理 | [dependency check and setup](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → 部署（包括 eval-suite 设置）→ invoke → observe (评估/优化) |
| 为托管代理设置 CI/CD 部署管道 | [dependency check and setup](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → cicd |
| 与代理 invoke/测试/聊天 | [dependency check and setup](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → invoke |
| 调度/事件触发代理，或 CRUD/启用/禁用/调度例程 | [dependency check and setup](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → routine |
| 优化/改进代理提示或指令 | observe (步骤 4：优化) |
| 评估和优化代理（完整循环） | observe |
| 启用持续评估监控 | observe (步骤 6：CI/CD & 监控) |
| 提取代理洞察/列出生成的问题和建议 | [dependency check and setup](#dependency-check-and-setup) → [insights](foundry-agent/insights/insights.md) (所有带有展开证据的页面；仅读) |
| 故障排除代理问题 | [dependency check and setup](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → invoke → troubleshoot |
| 修复损坏的代理（故障排除 + 重新部署） | [dependency check and setup](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → invoke → troubleshoot → 应用修复 → 部署 → invoke |

## 代理：.foundry 工作区标准

每个代理源文件夹可以在 `.foundry/` 下保留 Foundry 特定的缓存和覆盖状态：

```text
<agent-root>/
  .foundry/
    agent-metadata.yaml
    agent-metadata.prod.yaml
    suites/
    datasets/
    evaluators/
    results/
```

- 在 azd 项目中，从 `azure.yaml` 加 `azd env get-values` 衍生出部署上下文（项目端点、代理名称/版本、ACR、App Insights）；当 azd 已经提供这些值时，不要在元数据中重复这些值。
- `agent-metadata.yaml` 是非 azd 值、远程 Foundry 套件引用、本地缓存路径、结果摘要和显式覆盖的首选本地/开发覆盖文件。可选的边车文件（如 `agent-metadata.prod.yaml`）可以包含单个生产或 CI 目标覆盖，而不会在一个文件中混合多个环境。
- `suites/`、`datasets/` 和 `evaluators/` 是本地缓存文件夹。当它们是最新时，请重用它们，并在刷新或覆盖它们之前询问。
- 参考 [Agent Metadata Contract](references/agent-metadata-contract.md) 以获取规范模式和流程规则。

## 代理：设置参考

- [Standard Agent Setup](references/standard-agent-setup.md) — 用于需要数据驻留控制（自备 Cosmos DB / 存储 / AI 搜索通过 Foundry 能力主机）的生产工作负载的高级设置。默认的 `azd ai agent` 流使用 **基本代理设置**，并且**不会**配置 `capabilityHosts/agents` — 不要将其缺失标记为错误。对于默认的后期配置状态，请参阅 [foundry-agent/create/create-hosted.md](foundry-agent/create/create-hosted.md) 中的“Expected env-var fingerprint”部分。

## 代理：常见项目上下文解析

代理技能应仅在它们需要配置值而未已有这些值时运行此步骤。如果某个值（例如代理根、环境、项目端点或代理名称）已经从用户消息或同一会话中的先前技能中知道，请跳过该值的解析。

### 步骤 1：发现代理根和 azd 上下文

首先检查工作区是否具有使用 `host: azure.ai.agent` 的 `azure.yaml`。

- **一个 azd 代理服务** -> 使用该服务的 `project` 文件夹作为代理根。
- **多个 azd 代理服务** -> 要求用户选择目标服务/文件夹。
- **没有 azd 代理服务** -> 在工作区中搜索包含 `agent-metadata.yaml` 或 `agent-metadata.<env>.yaml` 的 `.foundry/` 文件夹。
  - **一个匹配** -> 使用该代理根。
  - **多个匹配** -> 要求用户选择目标代理文件夹。
  - **没有匹配** -> 对于 [insights](foundry-agent/insights/insights.md)，仅请求缺失的远程输入而无需初始化本地文件；对于 create/deploy 工作流，在设置期间种子一个新的 `.foundry/` 文件夹；对于其他工作流，停止并询问用户要初始化哪个代理源文件夹。

选择代理根后，将所有本地 `.foundry` 缓存检查、源检查、评估器建议、数据集建议和提示优化上下文仅保留在该文件夹内。**除非用户明确切换根，否则不要扫描兄弟代理文件夹。**

### 步骤 2：解析环境和部署上下文

如果存在 `azure.yaml`，则首先解析 azd 环境：

1. 用户显式命名的环境
2. 来自 `azd env get-values` 的 `AZURE_ENV_NAME`
3. 来自 `.azure/config.json` 的 azd 默认环境
4. 会话中先前选择的环境

当项目/部署值尚未已知时，运行 `azd env get-values` 以获取选定环境的值。优先使用 azd 值作为部署上下文：

| azd 变量          | 解析为           |
|-------------------|------------------|
| `AZURE_AI_PROJECT_ENDPOINT` 或 `AZURE_AIPROJECT_ENDPOINT` | 项目端点         |
| `AGENT_<SERVICE>_NAME` | 选定 azd 服务的代理名称 |
| `AGENT_<SERVICE>_VERSION` | 选定 azd 服务的代理版本 |
| `AZURE_CONTAINER_REGISTRY_NAME` 或 `AZURE_CONTAINER_REGISTRY_ENDPOINT` | ACR 注册库名称 / 图像 URL 前缀 |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | 跟踪工作流的 App Insights 连接字符串 |
| `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, `AZURE_AI_ACCOUNT_NAME`, `AZURE_AI_PROJECT_NAME` | Azure 资源查找和 Playground 链接 |

当 azd 提供这些值时，将其用作事实来源，并在元数据写入时不要将它们复制到 `.foundry/agent-metadata*.yaml` 中。

### 第 3 步：选择元数据覆盖并解析环境

在选定的代理根目录内，按此顺序选择元数据文件：
1. 用户或工作流程显式提供的元数据文件名或路径
2. 如果已知显式环境且存在 `.foundry/agent-metadata.<env>.yaml`，则使用该文件
3. `.foundry/agent-metadata.yaml`
4. 如果存在多个元数据文件且上述规则未选择一个，则提示用户选择

读取选定的元数据文件，并按此顺序解析任何剩余的环境选择：
1. 用户显式命名的环境
2. 如果选定的元数据文件定义了确切一个环境，则使用它
3. 会话中先前选择的环境
4. 来自元数据的 `defaultEnvironment`

如果选定的元数据文件仍包含多个环境且上述规则未选择一个，则提示用户选择。在每个工作流程摘要中保持选定的代理根目录、元数据文件、环境和上下文来源（来自 azd 或元数据）可见。

如果选定的环境暴露了较旧的 `testSuites[]` 元数据但未暴露 `evaluationSuites[]`，则将 `testSuites[]` 视为此会话的来源，并在继续之前将内存中的每个条目规范化为 `evaluationSuites[]` 的形状。如果元数据仍然较旧且仅暴露了遗留的 `testCases[]`，则以相同方式规范化该列表。保留数据集和评估器字段，保留任何现有的 `tags`，并且仅在 `tags.tier` 缺失时将遗留的 `priority` 映射到 `tags.tier`：`P0` -> `smoke`，`P1` -> `regression`，`P2` -> `coverage`。

### 第 4 步：解析 `eval.yaml` 本地评估意图

如果选定的代理根目录中存在 `eval.yaml`，则在生成新套件之前解析它：

- `agent.name` -> 目标代理候选；在使用它之前，验证它是否与选定的 azd/元数据代理匹配。
- `dataset.local_uri` -> 本地种子数据集候选；遗留的 `dataset_file` 可能会在内存中规范化。
- `dataset.name` / `dataset.version` -> 注册的数据集候选。
- `validation_dataset` -> 可选的验证数据集候选。
- `evaluators[]` -> 候选 Foundry 评估器名称；在使用它们之前，使用 `evaluator_catalog_get` 进行验证。
- `name` -> 本地评估/套件候选；在使用前进行远程验证，然后持久化为 `suiteName`。
- `options.eval_model`, `options.optimization_model`, `options.max_candidates`, `options.optimization_config.model_search_space`, `options.pass_threshold`, `max_samples`, `trace_days`, 和 `generation_instruction` -> 设置默认值。

将 `eval.yaml` 视为本地评估意图，而不是 Foundry 套件存在的证明。仅在远程查找或注册成功后，将同步的套件/数据集/评估器引用持久化到 `.foundry`。

### 第 5 步：解析通用配置

按此顺序层叠来源：

1. 显式用户输入和会话中已选择的值
2. azd 环境值用于部署上下文
3. `.foundry/agent-metadata*.yaml` 覆盖值和远程套件/缓存引用
4. `azure.yaml` 和 `eval.yaml` 本地源配置
5. 用户提示以获取任何仍缺失的信息

如果 azd 和元数据都提供相同的值且它们不同，则停止并询问哪个来源是权威的。如果它们匹配，则使用 azd 值，并在未来的元数据写入中避免重写重复的值。

| 有效值          | 优先来源       | 使用者         |
|-------------------|----------------|----------------|
| 项目端点         | azd env        | 部署、调用、观察、跟踪、排错 |
| 代理名称/版本     | azd 代理变量，然后 `azure.yaml` | 调用、观察、跟踪、排错 |
| ACR               | azd env        | 部署 |
| 评估套件和缓存路径 | `.foundry/agent-metadata*.yaml` | 观察、eval-datasets |
| 本地种子数据集/评估器意图 | `eval.yaml` | 观察、eval-datasets |

### 第 6 步：写入元数据覆盖（仅创建/部署/观察）

在任何元数据写入（部署、自动设置、数据集刷新或跟踪到数据集更新）时，仅在选定的元数据文件中持久化非派生覆盖/缓存状态：

- 有用的 azd 绑定 (`azd.environmentName`, `azd.service`)，以便于未来的解析
- `evaluationSuites[]`，包含远程套件/数据集/评估器引用和本地缓存路径
- `lastEval`，结果文件、比较摘要或显式的非 azd 覆盖

当 azd 已提供它们时，不要将 azd 拥有的部署值复制到元数据中。如果选定的文件是首选的单环境文件，则仅重写该环境块。如果选定的文件是遗留的多环境文件，则仅重写选定的环境块。永远不会自动复制或合并兄弟元数据文件中的环境。如果选定的环境仍使用较旧的 `testSuites[]` 或遗留的 `testCases[]`，则将其重写为 `evaluationSuites[]`，并从重写的条目中删除迁移的 `priority` 字段。

### 第 7 步：收集缺失值

仅当从用户的消息、会话上下文、元数据或 azd 引导中未解析出值时，使用 `ask_user` 或 `askQuestions` 工具。常见值技能可能需要：
- **代理根目录** — 目标 azd 服务项目文件夹或包含 `.foundry/agent-metadata*.yaml` 的文件夹
- **元数据文件** — 本地/开发用的 `agent-metadata.yaml`，或显式的边车，如 `agent-metadata.prod.yaml`
- **环境** — azd 环境、`dev`、`prod` 或来自元数据的另一个环境键
- **项目端点** — Microsoft Foundry 项目端点 URL
- **代理名称** — 目标代理的名称

> 💡 **提示：** 如果用户已提供代理路径、环境、项目端点或代理名称，则直接提取它——不要再次询问。

## 代理：代理类型

所有代理技能支持两种代理类型：

| 类型   | 种类   | 描述         |
|--------|--------|--------------|
| **Prompt** | `"prompt"` | 基于 LLM 的代理，由模型部署支持 |
| **Hosted** | `"hosted"` | 基于容器的代理，运行自定义代码 |

将具有 `host: azure.ai.agent` 的 `azure.yaml` 服务视为 Hosted。仅在类型无法从项目上下文中解析时使用 `agent_get`。

## 工具使用约定

- 每次从用户收集信息时，使用 `ask_user` 或 `askQuestions` 工具
- 使用 `task` 或 `runSubagent` 工具委派长时间运行或独立的子任务（例如，环境变量扫描、状态轮询、Dockerfile 生成）
- 优先使用 azd 为 Hosted 代理，使用 Foundry MCP 为 Prompt 代理。
- 引用官方 Microsoft 文档 URL 而不是嵌入 CLI 命令语法

## Azure 身份验证

- [Azure 身份验证最佳实践](references/auth-best-practices.md)

## 其他资源

- [Foundry Hosted 代理](https://learn.microsoft.com/azure/ai-foundry/agents/concepts/hosted-agents?view=foundry)
- [Foundry 代理运行时组件](https://learn.microsoft.com/azure/ai-foundry/agents/concepts/runtime-components?view=foundry)

## 网络隔离错误

适用于对 Foundry 项目或其父 Foundry 账户进行的**任何**调用——Foundry MCP 工具、`azd`、`az` CLI、`curl`、REST 或 SDK。

如果错误匹配 `Public access is disabled` / `PublicNetworkAccessDisabled` / `403 Forbidden` 来自私有端点 / 连接超时 / 项目端点 FQDN 解析为公共 IP，这通常意味着父 Foundry 账户具有 `publicNetworkAccess=Disabled` 或 `Enabled from selected IP addresses`，并且当前 shell 在其 VNet 之外。

只有在错误含糊不清时，才使用管理平面调用（从任何具有读取访问权限的地方都可以工作）进行确认：

```bash
az cognitiveservices account show \
  --name <account> --resource-group <rg> \
  --query "properties.{publicNetworkAccess:publicNetworkAccess, networkAcls:networkAcls, privateEndpointConnections:privateEndpointConnections[].properties.privateLinkServiceConnectionState.status}"
```

`publicNetworkAccess: "Disabled"` — 或 `"Enabled"` 与非空的 `networkAcls.ipRules` / `virtualNetworkRules` 一起 — 确认隔离。如果 `publicNetworkAccess: "Enabled"` 且 `networkAcls` 为空，则失败是调用者端的网络问题（例如，私有 DNS 从 VNet 内部将 FQDN 解析为具有私有端点的公共 IP），而不是账户配置问题。

如果确实存在网络隔离问题，支持的连接选项在 [选择到 Foundry 的安全连接方法](https://learn.microsoft.com/azure/foundry/how-to/configure-private-link#choose-a-secure-connection-method-to-foundry) 中有说明。

> ℹ️ Foundry MCP 工具即使在 VNet 内部也无法连接到 VNet 隔离的项目。
