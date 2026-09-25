# Microsoft Foundry 技能

此技能帮助开发者使用 Microsoft Foundry 资源，涵盖模型发现和部署、AI 代理的完整开发生命周期、评估工作流以及故障排除。

## 执行前要求

在开始相应的操作或工作流之前，请遵循以下适用子部分的每一项。

### 依赖项检查和设置

**强制要求：** 在此技能加载后的第一步，从该技能的根目录运行以下依赖项检查和设置脚本，并在继续之前等待其完成。该脚本首先检查并仅安装缺失的依赖项；它不会重新安装已经可用的依赖项。

**您必须在阅读或进入任何子技能、工作流或工作流特定参考之前完成此检查。**

```bash
./scripts/check-and-setup-dependencies.sh     # macOS / Linux
./scripts/check-and-setup-dependencies.ps1    # Windows (pwsh)
```

严格遵循脚本输出以进行后续操作。

### 工作流指导

**强制要求：** 在执行任何特定于工作流步骤之前，您**必须**阅读相应的子技能文档。不要在没有阅读其技能文档的情况下调用特定于工作流的 MCP 工具。即使您已经知道 MCP 工具参数，也适用此规则——技能文档包含必须遵循的所需工作流步骤、预检查和验证逻辑。此规则适用于触发不同工作流的每个新用户消息，即使技能已经加载。

### Foundry MCP

**强制要求：** 在使用 Foundry MCP 操作之前，调用 Azure MCP `foundry` 工具并检查可用的 Foundry MCP 工具和相关参数。将其视为基于 MCP 的工作流的发现/帮助步骤。

### azd

**强制要求：** 在执行任何 azd 命令之前，您**必须**阅读 [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) 并严格遵循其中定义的共享规则，特别是 `AZURE_DEV_USER_AGENT` 设置规则。

## 子技能

此技能包括针对特定工作流的专用子技能。**当子技能与任务匹配时，请严格遵循其工作流：**

| 子技能 | 使用场景 | 参考 |
|-----------|-------------|-----------|
| **deploy** | 将托管代理部署到 Foundry、对部署进行烟雾测试、创建或更新提示代理、管理代理版本和多环境部署。 | [deploy](foundry-agent/deploy/deploy.md) |
| **cicd** | 为 Foundry 代理设置 CI/CD 部署管道。 | [cicd](foundry-agent/cicd/cicd.md) |
| **invoke** | 向代理发送消息、单轮或多轮对话 | [invoke](foundry-agent/invoke/invoke.md) |
| **routine** | 使用例行程序计划或事件触发 Foundry 代理；使用 `azd` 进行 CRUD、启用/禁用、手动调度和查看过去的运行，或在 `azure.yaml` 中定义例行程序。 | [routine](foundry-agent/routine/routine.md) |
| **invocations-ws** | 构建、部署和连接到使用 `invocations_ws` 双工 WebSocket 协议的托管代理——语音代理、实时流和用于带外媒体传输的信令。 | [invocations-ws](foundry-agent/invocations-ws/invocations-ws.md) |
| **observe** | 评估代理质量、运行批量评估、分析失败、优化提示、改进代理指令、比较版本、设置 CI/CD 监控并启用持续生产评估 | [observe](foundry-agent/observe/observe.md) |
| **insights** | 从现有监控器中提取生成的代理洞察、证据和建议；仅限只读检索，不是新的分析运行 | [insights](foundry-agent/insights/insights.md) |
| **trace** | 查询跟踪、分析延迟/失败、通过 App Insights `customEvents` 将评估结果关联到特定响应 | [trace](foundry-agent/trace/trace.md) |
| **troubleshoot** | 查看托管代理日志、查询遥测数据、诊断失败 | [troubleshoot](foundry-agent/troubleshoot/troubleshoot.md) |
| **validate** | 仅在用户明确要求使用此验证子技能或验证 Microsoft Foundry 托管代理代码是否符合最佳实践时使用。切勿主动调用它或将其添加到其他工作流。 | [validate](foundry-agent/validate/validate.md) |
| **create (quick start)** | 从头开始端到端创建新的托管 Foundry 代理——创建脚手架、提供或使用现有的 Foundry 项目、部署和烟雾测试。不要用于对现有代码的任何工作。对于快速启动未涵盖的内容，使用 **create**。 | [create/quick-start-hosted.md](foundry-agent/create/quick-start-hosted.md) |
| **create** | 当标准的端到端快乐路径（快速启动）不适用时使用。创建新的 Foundry 代理、更新现有代理的代码、继续开发现有代理、在脚手架时间连接、使用高级设置或 A2A（Agent2Agent）或从失败的快速启动运行中恢复。 | [create](foundry-agent/create/create-hosted.md) |
| **agent-optimizer** | 使现有的 Python 托管代理代码准备好进行优化、配置 eval.yaml、运行 Agent Optimizer 任务、本地应用候选者并通过 azd 审查后部署。 | [agent-optimizer](foundry-agent/agent-optimizer/agent-optimizer.md) |
| **eval-datasets** | 将生产跟踪收集到评估数据集、管理数据集版本和分割、跟踪评估指标随时间变化、检测回归并维护从跟踪到部署的完整谱系。用于：从跟踪创建数据集、数据集版本控制、评估趋势、回归检测、数据集比较、评估谱系。 | [eval-datasets](foundry-agent/eval-datasets/eval-datasets.md) |
| **project/create** | 创建新的 Microsoft Foundry 项目以托管代理和模型。在 Foundry onboarding 或设置新基础设施时使用。 | [project/create/create-foundry-project.md](project/create/create-foundry-project.md) |
| **resource/create** | 使用 Azure CLI 创建 Azure AI Services 多服务资源（Foundry 资源）。在手动提供 AI Services 资源并需要细粒度控制时使用。 | [resource/create/create-foundry-resource.md](resource/create/create-foundry-resource.md) |
| **private-network** | 回答有关 Foundry 网络隔离的问题**并且**使用 VNet 隔离部署 Foundry（自带 VNet、托管 VNet、混合）。涵盖架构概念、模板选择、部署和部署后验证。 | [resource/private-network/private-network.md](resource/private-network/private-network.md) |
| **models/deploy-model** | 统一模型部署，具有智能路由。处理快速预设部署、完全自定义部署（版本/SKU/容量/RAI）以及跨区域的容量发现。路由到子技能：`preset`（快速部署）、`customize`（完全控制）、`capacity`（查找可用性）。 | [models/deploy-model/SKILL.md](models/deploy-model/SKILL.md) |
| **quota** | 管理 Microsoft Foundry 资源的配额和容量。在检查配额使用情况、由于配额不足导致部署失败、请求配额增加或规划容量时使用。 | [quota/quota.md](quota/quota.md) |
| **rbac** | 管理 Microsoft Foundry 资源的 RBAC 权限、角色分配、托管标识符和服务主体。用于访问控制、审计权限和 CI/CD 设置。 | [rbac/rbac.md](rbac/rbac.md) |
| **finetuning** | 在 Microsoft Foundry 上微调模型——SFT 蒸馏、DPO 偏好优化、带有评分器和工具调用的 RFT。数据集准备、评分器校准、训练、检查点选择、部署、评估。用于：微调、SFT、DPO、RFT、训练数据、评分器、蒸馏、微调模型、大文件上传。 | [finetuning/SKILL.md](finetuning/SKILL.md) |
| **azd-guidance** | 提供 azd 管理 Foundry 代理的共享知识和指导。对于任何与 azd 相关的工作流，请首先阅读此内容。 | [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) |

> 💡 **提示：** 对于完整的 onboarding 流程：`project/create`（公共）或 `private-network`（VNet 隔离）→ `models/deploy-model` → 代理工作流 (`create` → `deploy` → `invoke`)。

> 💡 **微调：** 使用 `finetuning` 进行所有模型定制——SFT 蒸馏、DPO 偏好优化和带有评分器的 RFT。包括快速启动、评分器校准和训练曲线分析。

> 💡 **模型部署：** 使用 `models/deploy-model` 进行所有部署场景——它智能地在快速预设部署、完全控制的自定义部署和跨区域容量发现之间进行路由。

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

将用户意图匹配到正确的代理工作流。在执行之前按顺序阅读每个子技能。

| 用户意图 | 工作流（按顺序阅读） |
|-------------|------------------------|
| 端到端创建新的托管代理（创建脚手架 + 部署 + 测试） | [dependency check and setup](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → [quick-start-hosted](foundry-agent/create/quick-start-hosted.md) (自包含端到端) |
| 标准快速启动之外的内容（现有代码、迁移、重新托管、部署自定义、脚手架时间连接、A2A（Agent2Agent）、恢复） | [dependency check and setup](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → [create](foundry-agent/create/create-hosted.md) → [deploy](foundry-agent/deploy/deploy.md) → [invoke](foundry-agent/invoke/invoke.md) |
| 优化现有的 Python 托管代理 | [dependency check and setup](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → [agent-optimizer](foundry-agent/agent-optimizer/agent-optimizer.md) → 脚手架/审查 → eval.yaml → 优化 → 应用候选者 → 部署 → invoke |
| 部署代理（代码已存在） | [dependency check and setup](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → 部署（包括 eval-suite 设置）→ invoke → observe (评估/优化) |
| 代码更改后更新/重新部署代理 | [dependency check and setup](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → 部署（包括 eval-suite 设置）→ invoke → observe (评估/优化) |
| 为托管代理设置 CI/CD 部署管道 | [dependency check and setup](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → cicd |
| 与代理交互/测试/聊天 | [dependency check and setup](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → invoke |
| 调度/事件触发代理，或 CRUD/启用/禁用/调度例行程序 | [dependency check and setup](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → routine |
| 优化/改进代理提示或指令 | observe (步骤 4：优化) |
| 评估和优化代理（完整循环） | observe |
| 启用持续评估监控 | observe (步骤 6：CI/CD & 监控) |
| 提取代理洞察/列出生成的问题和建议 | [dependency check and setup](#dependency-check-and-setup) → [insights](foundry-agent/insights/insights.md) (所有带有展开证据的页面；只读) |
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

- 在 azd 项目中，从 `azure.yaml` 加 `azd env get-values` 衍生部署上下文（项目端点、代理名称/版本、ACR、App Insights）；当 azd 已经提供这些值时，不要在元数据中重复这些值。
- `agent-metadata.yaml` 是非 azd 值、远程 Foundry 套件引用、本地缓存路径、结果摘要和显式覆盖的首选本地/开发覆盖。可选的边车文件（如 `agent-metadata.prod.yaml`）可以包含单个生产或 CI 目标覆盖，而不会在一个文件中混合多个环境。
- `suites/`、`datasets/` 和 `evaluators/` 是本地缓存文件夹。当它们是最新的时，重用它们，并在刷新或覆盖它们之前询问。
- 参考 [Agent Metadata Contract](references/agent-metadata-contract.md) 获取规范模式和流程规则。

## 代理：设置参考

- [标准代理设置](references/standard-agent-setup.md) — 高级设置，适用于需要数据驻留控制（自带 Cosmos DB / 存储 / AI 搜索通过 Foundry 能力主机）的生产工作负载。默认的 `azd ai agent` 流使用 **基本代理设置**，并且**不**提供 `capabilityHosts/agents` — 不要将其缺失标记为错误。对于默认的后期提供状态，请参阅 [foundry-agent/create/create-hosted.md](foundry-agent/create/create-hosted.md) 中的“预期 env-var 指纹”部分。

## 代理：通用项目上下文解析

代理技能应仅在它们需要配置值而尚未拥有时运行此步骤。如果值（例如代理根、环境、项目端点或代理名称）已经从用户消息或同一会话中的先前技能中知道，请跳过该值的解析。

### 步骤 1：发现代理根和 azd 上下文

首先检查工作区是否具有使用 `host: azure.ai.agent` 的 `azure.yaml`。

- **一个 azd 代理服务** -> 使用该服务的 `project` 文件夹作为代理根。
- **多个 azd 代理服务** -> 要求用户选择目标服务/文件夹。
- **没有 azd 代理服务** -> 在工作区中搜索包含 `agent-metadata.yaml` 或 `agent-metadata.<env>.yaml` 的 `.foundry/` 文件夹。
  - **一个匹配** -> 使用该代理根。
  - **多个匹配** -> 要求用户选择目标代理文件夹。
  - **没有匹配** -> 对于 [insights](foundry-agent/insights/insights.md)，仅请求缺失的远程输入，而无需初始化本地文件；对于 create/deploy 工作流，在设置期间种子一个新的 `.foundry/` 文件夹；对于其他工作流，停止并询问用户要初始化哪个代理源文件夹。

选择代理根后，仅在该文件夹内保留所有本地 `.foundry` 缓存检查、源检查、评估器建议、数据集建议和提示优化上下文。**不要**扫描兄弟代理文件夹，除非用户明确切换根目录。

### 步骤 2：解析环境和部署上下文

如果存在 `azure.yaml`，则首先解析 azd 环境：

1. 用户明确命名的环境
2. `AZURE_ENV_NAME` 从 `azd env get-values`
3. azd 默认环境从 `.azure/config.json`
4. 会话中先前选择的 环境

当项目/部署值尚不知道时，为选定的环境运行 `azd env get-values`。优先使用 azd 值进行部署上下文：

| azd 变量 | 解析为 |
|-------------|-------------|
| `AZURE_AI_PROJECT_ENDPOINT` 或 `AZURE_AIPROJECT_ENDPOINT` | 项目端点 |
| `AGENT_<SERVICE>_NAME` | 为选定的 azd 服务选择的代理名称 |
| `AGENT_<SERVICE>_VERSION` | 为选定的 azd 服务选择的代理版本 |
| `AZURE_CONTAINER_REGISTRY_NAME` 或 `AZURE_CONTAINER_REGISTRY_ENDPOINT` | ACR 注册库名称/图像 URL 前缀 |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | 用于跟踪工作流的 App Insights 连接字符串 |
| `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, `AZURE_AI_ACCOUNT_NAME`, `AZURE_AI_PROJECT_NAME` | Azure 资源查找和 Playground 链接 |

当 azd 提供这些值时，将其用作真实来源，并且在元数据写入时**不要**将它们复制到 `.foundry/agent-metadata*.yaml`。

### 步骤 3：选择元数据覆盖并解析环境

在选定的代理根内，按以下顺序选择元数据文件：

1. 用户或工作流明确提供的元数据文件名或路径
2. 如果已经知道明确的环境并且存在 `.foundry/agent-metadata.<env>.yaml`，则使用该文件
3. `.foundry/agent-metadata.yaml`
4. 如果多个元数据文件仍然存在并且上述规则未选择任何文件，提示用户选择

读取选定的元数据文件并按以下顺序解析任何剩余的环境选择：

1. 用户明确命名的环境
2. 如果选定的元数据文件定义了确切一个环境，则使用它
3. 会话中先前选择的 环境
4. `defaultEnvironment` 从元数据

如果选定的元数据文件仍然包含多个环境并且上述规则未选择任何文件，提示用户选择。在每个工作流摘要中保留选定的代理根、元数据文件、环境和上下文是否来自 azd 或元数据。

如果选定的环境暴露了较旧的 `testSuites[]` 元数据但没有 `evaluationSuites[]`，则将 `testSuites[]` 视为此会话的源，并在继续之前将内存中的每个条目规范化为 `evaluationSuites[]` 的形状。如果元数据仍然较旧并且仅暴露遗留的 `testCases[]`，则以相同的方式规范化该列表。保留数据集和评估器字段，保留任何现有的 `tags`，并且仅在 `tags.tier` 缺失时将遗留的 `priority` 映射到 `tags.tier`：`P0` -> `smoke`, `P1` -> `regression`, `P2` -> `coverage`。

### 步骤 4：解析 eval.yaml 本地评估意图

如果选定的代理根中存在 `eval.yaml`，则在生成新套件之前解析它：

- `agent.name` -> 目标代理候选；在使用它之前，请验证它是否与选定的 azd/元数据代理匹配。
- `dataset.local_uri` -> 本地种子数据集候选；遗留的 `dataset_file` 可能会在内存中规范化。
- `dataset.name` / `dataset.version` -> 注册数据集候选。
- `validation_dataset` -> 可选的验证数据集候选。
- `evaluators[]` -> 候选 Foundry 评估器名称；在使用它们作为远程评估器之前，请与 `evaluator_catalog_get` 进行验证。
- `name` -> 本地评估/套件候选；在使用它之前，请远程验证。
- `options.eval_model`, `options.optimization_model`, `options.max_candidates`, `options.optimization_config.model_search_space`, `options.pass_threshold`, `max_samples`, `trace_days`, 和 `generation_instruction` -> 设置默认值。

将 `eval.yaml` 视为本地评估意图，而不是 Foundry 套件存在的证明。仅在远程查找或注册成功后，才将同步的套件/数据集/评估器引用持久化到 `.foundry`。

### 步骤 5：解析常见配置

按以下顺序分层来源：

1. 明确的用户输入和会话中已选择的值
2. azd 环境值用于部署上下文
3. `.foundry/agent-metadata*.yaml` 覆盖值和远程套件/缓存引用
4. `azure.yaml` 和 `eval.yaml` 本地源配置
5. 用户提示以获取任何仍然缺失的内容

如果 azd 和元数据都提供相同的值并且它们不同，则停止并询问哪个来源具有权威性。如果它们匹配，则使用 azd 值，并且在未来的元数据写入中避免重写重复的值。

| 有效值 | 首选来源 | 使用 |
|-----------------|------------------|---------|
| 项目端点 | azd env | deploy, invoke, observe, trace, troubleshoot |
| 代理名称/版本 | azd 代理变量，然后 `azure.yaml` | invoke, observe, trace, troubleshoot |
| ACR | azd env | deploy |
| 评估套件和缓存路径 | `.foundry/agent-metadata*.yaml` | observe, eval-datasets |
| 本地种子数据集/评估器意图 | `eval.yaml` | observe, eval-datasets |

### 步骤 6：写入元数据覆盖（仅创建/部署/观察）

在任何元数据写入（部署、自动设置、数据集刷新或跟踪到数据集更新）中，仅在选定的元数据文件中持久化非派生覆盖/缓存状态：

- azd 绑定 (`azd.environmentName`, `azd.service`) 当它对未来的解析有用时
- `evaluationSuites[]` 具有远程套件/数据集/评估器引用和本地缓存路径
- `lastEval`, 结果文件, 比较摘要或显式的非 azd 覆盖

当 azd 已经提供它们时，不要将 azd 拥有的部署值复制到元数据。如果选定的文件是首选的单环境文件，则仅重写该环境块。如果选定的文件是遗留的多环境文件，则仅重写选定的环境块。永远不要自动复制或合并兄弟元数据文件中的环境。如果选定的环境仍然使用较旧的 `testSuites[]` 或遗留的 `testCases[]`，则将其重写为 `evaluationSuites[]` 并从重写的条目中删除已迁移的 `priority` 字段。

### 步骤 7：收集缺失的值

仅当从用户消息、会话上下文、元数据或 azd 引导中未解析值时，使用 `ask_user` 或 `askQuestions` 工具。常见值技能可能需要的值：

- **代理根** — 目标 azd 服务项目文件夹或包含 `.foundry/agent-metadata*.yaml` 的文件夹
- **元数据文件** — `agent-metadata.yaml` 用于本地/开发，或显式的边车文件，例如 `agent-metadata.prod.yaml`
- **环境** — azd 环境、`dev`、`prod` 或来自元数据的另一个环境键
- **项目端点** — Microsoft Foundry 项目端点 URL
- **代理名称** — 目标代理的名称

> 💡 **提示：** 如果用户已经提供代理路径、环境、项目端点或代理名称，请直接提取——不要再次询问。
