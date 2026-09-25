# Microsoft Foundry Skill

本技能帮助开发者使用 Microsoft Foundry 资源，涵盖模型发现与部署、AI agent 完整开发生命周期、评估工作流以及故障排查。

## 执行前要求

在开始其对应的操作或工作流之前，请遵循以下每个适用小节。

### 依赖检查与设置

**强制性：** 在此技能加载后，作为第一步，运行本技能根目录下的依赖检查与设置脚本，并等待其完成后再继续。该脚本会先进行检查，仅安装缺失的依赖；不会重新安装已可用的依赖。

**您必须在阅读或进入任何子技能、工作流或工作流特定参考之前完成此检查。**

```bash
./scripts/check-and-setup-dependencies.sh     # macOS / Linux
./scripts/check-and-setup-dependencies.ps1    # Windows (pwsh)
```

请严格遵循脚本输出，并据此执行后续操作。

### 工作流指导

**强制性：** 在执行任何工作流特定步骤之前，您 MUST 阅读对应的子技能文档。在未阅读其技能文档的情况下，不得为工作流调用工作流特定的 MCP 工具。即使您已了解 MCP 工具参数，该规则仍然适用——技能文档包含必须遵循的工作流步骤、预检查与验证逻辑。此规则适用于每一个触发不同工作流的新用户消息，即使技能已加载。

### Foundry MCP

**强制性：** 在使用 Foundry MCP 操作之前，调用 Azure MCP 的 `foundry` 工具，并检查可用的 Foundry MCP 工具及相关参数。将其视为 MCP 工作流的基础发现/帮助步骤。

### azd

**强制性：** 在执行任何 `azd` 命令之前，您 MUST 阅读 [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md)，并严格遵循其中定义的共享规则，特别是 `AZURE_DEV_USER_AGENT` 设置规则。

## 子技能

本技能包含用于特定工作流的专用子技能。**当某个子技能匹配任务时，请严格遵循其工作流：**

| Sub-Skill | 使用场景 | 参考 |
|-----------|-------------|-----------|
| **deploy** | 将托管 agent 部署到 Foundry、对部署进行冒烟测试、创建或更新 prompt agent，以及管理 agent 版本与多环境部署。 | [deploy](foundry-agent/deploy/deploy.md) |
| **cicd** | 为 Foundry agent 设置 CI/CD 部署流水线。 | [cicd](foundry-agent/cicd/cicd.md) |
| **invoke** | 向 agent 发送消息，执行单轮或多轮对话 | [invoke](foundry-agent/invoke/invoke.md) |
| **routine** | 使用 routine 排程或事件触发 Foundry agent；使用 `azd` 执行 CRUD、启用/禁用、手动派发以及查看历史运行，或在 `azure.yaml` 中定义 routine。 | [routine](foundry-agent/routine/routine.md) |
| **invocations-ws** | 构建、部署并与以 `invocations_ws` duplex WebSocket 协议进行通信的托管 agent 连接——语音 agent、实时流，以及用于非在途媒体传输的信令。 | [invocations-ws](foundry-agent/invocations-ws/invocations-ws.md) |
| **observe** | 评估 agent 质量、运行批量评估、分析失败、优化提示词、改进 agent 指令、对比版本、设置 CI/CD 监控，以及启用持续生产评估 | [observe](foundry-agent/observe/observe.md) |
| **insights** | 从现有监控中拉取生成的 agent 洞察、证据与建议；为只读检索，并非新的分析运行。 | [insights](foundry-agent/insights/insights.md) |
| **trace** | 查询 trace、分析延迟/失败，通过 App Insights `customEvents` 将评估结果与具体响应关联。 | [trace](foundry-agent/trace/trace.md) |
| **troubleshoot** | 查看托管 agent 日志、查询遥测、诊断失败。 | [troubleshoot](foundry-agent/troubleshoot/troubleshoot.md) |
| **validate** | 仅当用户明确要求使用此验证子技能，或要求验证 Microsoft Foundry 托管 agent 代码是否符合最佳实践时使用。切勿主动调用，也勿将其加入其他工作流。 | [validate](foundry-agent/validate/validate.md) |
| **create (quick start)** | 从零端到端创建新的托管 Foundry agent——脚手架、提供或复用现有 Foundry 项目、部署并冒烟测试。不用于任何现有代码工作。对于 quickstart 未覆盖的内容，使用 **create**。 | [create/quick-start-hosted.md](foundry-agent/create/quick-start-hosted.md) |
| **create** | 当标准端到端 happy path（quick start）不适用时使用。创建新的 Foundry agent、更新现有 agent 的代码、继续现有 agent 的开发、在脚手架阶段连接、使用高级设置或 A2A（Agent2Agent），或从失败的 quickstart 运行中恢复。 | [create](foundry-agent/create/create-hosted.md) |
| **agent-optimizer** | 使现有 Python 托管 agent 代码具备优化能力、配置 `eval.yaml`、运行 Agent Optimizer 任务、本地应用候选方案，并在审查后通过 azd 部署。 | [agent-optimizer](foundry-agent/agent-optimizer/agent-optimizer.md) |
| **eval-datasets** | 将生产 trace 收割为评估数据集、管理数据集版本与划分、跟踪随时间变化的评估指标、检测回归、并从 trace 到部署维护完整的血缘。用于：从 trace 创建数据集、数据集版本化、评估趋势跟踪、回归检测、数据集对比、评估血缘。 | [eval-datasets](foundry-agent/eval-datasets/eval-datasets.md) |
| **project/create** | 为托管 agent 和模型创建新的 Microsoft Foundry 项目。当开始加入 Foundry 或设置新基础设施时使用。 | [project/create/create-foundry-project.md](project/create/create-foundry-project.md) |
| **resource/create** | 使用 Azure CLI 创建 Azure AI Services 多服务资源（Foundry 资源）。当需要手动配置 AI Services 资源并获得精细控制时使用。 | [resource/create/create-foundry-resource.md](resource/create/create-foundry-resource.md) |
| **private-network** | 回答有关 Foundry 网络隔离的疑问，并将采用 VNet 隔离的 Foundry 进行部署（BYO VNet、Managed VNet、混合模式）。涵盖架构概念、模板选择、部署与部署后验证。 | [resource/private-network/private-network.md](resource/private-network/private-network.md) |
| **models/deploy-model** | 智能路由的统一模型部署。处理快速预设部署、完全定制的部署（版本/SKU/容量/RAI），以及跨区域的容量发现。路由至子技能：`preset`（快速部署）、`customize`（完全控制）、`capacity`（查找可用性）。 | [models/deploy-model/SKILL.md](models/deploy-model/SKILL.md) |
| **quota** | 管理 Microsoft Foundry 资源的配额与容量。当需要检查配额使用量、排查因配额不足导致的部署失败、申请配额增加或规划容量时使用。 | [quota/quota.md](quota/quota.md) |
| **rbac** | 管理 Microsoft Foundry 资源的 RBAC 权限、角色分配、托管标识（managed identities）与服务主体（service principals）。用于访问控制、权限审计以及 CI/CD 设置。 | [rbac/rbac.md](rbac/rbac.md) |
| **finetuning** | 在 Microsoft Foundry 上微调模型——SFT 蒸馏、DPO 偏好优化、带评分器与工具调用的 RFT。数据集准备、评分器校准、训练、检查点选择、部署、评估。用于：微调、SFT、DPO、RFT、训练数据、评分器、蒸馏、微调后模型、大文件上传。 | [finetuning/SKILL.md](finetuning/SKILL.md) |
| **azd-guidance** | 为管理 Foundry agent 提供共享的 azd 知识与指导。对于任何与 azd 相关的工作流，请首先阅读此文档。 | [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) |

> 💡 **提示：** 完整的入门流程：`project/create`（公开）或 `private-network`（VNet 隔离）→ `models/deploy-model` → agent 工作流（`create` → `deploy` → `invoke`）。

> 💡 **微调：** 使用 `finetuning` 进行所有模型定制——SFT 蒸馏、DPO 偏好优化以及带评分器的 RFT。包含 quickstart、评分器校准与训练曲线分析。

> 💡 **模型部署：** 使用 `models/deploy-model` 处理所有部署场景——它智能地在快速预设部署、完全定制的部署以及跨区域容量发现之间进行路由。

> 💡 **提示词优化：** 针对"优化我的提示词"或"改进我的 agent 指令"等请求，请加载 [observe](foundry-agent/observe/observe.md) 并通过该评估驱动的工作流使用 `prompt_optimize` MCP 工具。

## 基础设施生命周期

将用户意图匹配到正确的基础设施工作流。

| 用户意图 | 工作流 |
|-------------|---------|
| "创建 Foundry" / "设置 Foundry"（模糊） | 使用 `AskUserQuestion`： (a) 仅 AI Services 资源， (b) 包含公共访问的项目，或 (c) 包含网络隔离的项目？路由： (a) → [resource/create](resource/create/create-foundry-resource.md)， (b) → [project/create](project/create/create-foundry-project.md)， (c) → [private-network](resource/private-network/private-network.md) |
| 以 VNet 隔离设置 Foundry | [private-network](resource/private-network/private-network.md) |
| 创建公开 Foundry 项目 | [project/create](project/create/create-foundry-project.md) |
| 创建裸 Foundry 资源 | [resource/create](resource/create/create-foundry-resource.md) |

## Agent 开发生命周期

将用户意图匹配到正确的 agent 工作流。按顺序阅读每个子技能后再执行。

| 用户意图 | 工作流（按顺序阅读） |
|-------------|------------------------|
| 端到端创建新的托管 agent（脚手架 + 部署 + 测试） | [依赖检查与设置](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → [quick-start-hosted](foundry-agent/create/quick-start-hosted.md)（自包含端到端） |
| 超出标准 quickstart 的任意内容（现有代码、迁移、重新托管、部署定制、脚手架阶段连接、A2A（Agent2Agent）、恢复） | [依赖检查与设置](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → [create](foundry-agent/create/create-hosted.md) → [deploy](foundry-agent/deploy/deploy.md) → [invoke](foundry-agent/invoke/invoke.md) |
| 优化现有 Python 托管 agent | [依赖检查与设置](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → [agent-optimizer](foundry-agent/agent-optimizer/agent-optimizer.md) → 脚手架/审查 → eval.yaml → 优化 → 应用候选方案 → 部署 → 调用 |
| 部署 agent（代码已存在） | [依赖检查与设置](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → deploy（包含评估套件设置）→ invoke → observe（评估/优化） |
| 代码变更后更新/重新部署 agent | [依赖检查与设置](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → deploy（包含评估套件设置）→ invoke → observe（评估/优化） |
| 为托管 agent 设置 CI/CD 部署流水线 | [依赖检查与设置](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → cicd |
| 调用/测试/与 agent 聊天 | [依赖检查与设置](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → invoke |
| 排程/事件触发 agent，或执行 routine 的 CRUD、启用/禁用、派发 | [依赖检查与设置](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → routine |
| 优化/改进 agent 提示词或指令 | observe（第 4 步：优化） |
| 评估并优化 agent（完整循环） | observe |
| 启用持续评估监控 | observe（第 6 步：CI/CD 与监控） |
| 拉取 agent 洞察/列出生成的议题与建议 | [依赖检查与设置](#dependency-check-and-setup) → [insights](foundry-agent/insights/insights.md)（所有页面均含展开证据；只读） |
| 排查 agent 问题 | [依赖检查与设置](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → invoke → troubleshoot |
| 修复损坏的 agent（排查 + 重新部署） | [依赖检查与设置](#dependency-check-and-setup) → [azd-guidance](foundry-agent/azd-guidance/azd-guidance.md) → invoke → troubleshoot → 应用修复 → deploy → invoke |

## Agent：.foundry 工作区标准

每个 agent 源文件夹都可以在 `.foundry/` 下保留 Foundry 特定的缓存与覆盖状态：

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

- 在 azd 项目中，从 `azure.yaml` 与 `azd env get-values` 推导部署上下文（项目端点、agent 名称/版本、ACR、App Insights）；当 azd 已提供这些值时，不要将其重复写入元数据。
- `agent-metadata.yaml` 是非 azd 值的本地/开发覆盖、远程 Foundry 套件引用、本地缓存路径、结果摘要以及明确覆盖的首选本地/开发覆盖文件。`agent-metadata.prod.yaml` 等旁路文件为可选 sidecar 文件，可承载单一生产或 CI 目标覆盖，无需在一个文件中混合多个环境。
- `suites/`、`datasets/` 与 `evaluators/` 是本地缓存文件夹。在它们仍然有效时复用，在刷新或覆盖前请先确认。
- 参见 [Agent Metadata Contract](references/agent-metadata-contract.md) 了解规范模式与工作流规则。

## Agent：设置参考

- [标准 Agent 设置](references/standard-agent-setup.md) — 针对需要数据驻留控制的生产工作负载的高级设置（通过 Foundry 能力主机引入自有 Cosmos DB / Storage / AI Search）。默认的 `azd ai agent` 流程使用 **Basic Agent Setup**，且不配置 `capabilityHosts/agents` —— 不要将其缺失标记为 Bug。对于默认的后配置状态，参见 [foundry-agent/create/create-hosted.md](foundry-agent/create/create-hosted.md) 中 "Expected env-var fingerprint"（预期环境变量指纹）部分。

## Agent：项目上下文解析的通用规则

Agent 技能应仅在此步骤需要已不存在的配置值时运行此步骤。若某个值（例如，agent 根目录、环境、项目端点、agent 名称）已由用户消息或会话中先前加载的技能所知晓，则应跳过该值的解析。

### 第 1 步：发现 agent 根目录与 azd 上下文

首先检查工作区是否存在包含使用 `host: azure.ai.agent` 服务的 `azure.yaml`。

- **一个 azd agent 服务** -> 使用该服务的 `project` 文件夹作为 agent 根目录。
- **多个 azd agent 服务** -> 要求用户选择目标服务/文件夹。
- **无 azd agent 服务** -> 在工作区中搜索包含 `agent-metadata.yaml` 或 `agent-metadata.<env>.yaml` 的 `.foundry/` 文件夹。
  - **匹配到一个** -> 使用该 agent 根目录。
  - **匹配到多个** -> 要求用户选择目标 agent 文件夹。
  - **无匹配** -> 对于 [insights](foundry-agent/insights/insights.md)，仅询问缺失的远程输入，无需初始化本地文件；对于 create/deploy 工作流，在设置过程中初始化新的 `.foundry/` 文件夹；对于其他工作流，停止并向用户询问需初始化的 agent 源文件夹。

选定 agent 根目录后，所有本地 `.foundry` 缓存检查、源检查、评估器建议、数据集建议与提示词优化上下文均限定在该文件夹内。除非用户明确切换根目录，否则**不得**扫描兄弟 agent 文件夹。

### 第 2 步：解析环境与部署上下文

若存在 `azure.yaml`，首先解析 azd 环境：

1. 用户明确指定的环境
2. 来自 `azd env get-values` 的 `AZURE_ENV_NAME`
3. 来自 `.azure/config.json` 的 azd 默认环境
4. 会话中先前已选定的环境

当项目/部署值尚未知时，为选定环境运行 `azd env get-values`。优先使用 azd 值作为部署上下文：

| azd 变量 | 解析结果 |
|-------------|-------------|
| `AZURE_AI_PROJECT_ENDPOINT` 或 `AZURE_AIPROJECT_ENDPOINT` | 项目端点 |
| `AGENT_<SERVICE>_NAME` | 选定 azd 服务的 agent 名称 |
| `AGENT_<SERVICE>_VERSION` | 选定 azd 服务的 agent 版本 |
| `AZURE_CONTAINER_REGISTRY_NAME` 或 `AZURE_CONTAINER_REGISTRY_ENDPOINT` | ACR 注册表名称 / 镜像 URL 前缀 |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | 用于 trace 工作流的 App Insights 连接字符串 |
| `AZURE_SUBSCRIPTION_ID`、`AZURE_RESOURCE_GROUP`、`AZURE_AI_ACCOUNT_NAME`、`AZURE_AI_PROJECT_NAME` | Azure 资源查询与 Playground 链接 |

当 azd 提供这些值时，以此作为事实来源，勿在元数据写入时将它们复制到 `.foundry/agent-metadata*.yaml` 中。

### 第 3 步：选择元数据覆盖并解析环境

在选定的 agent 根目录内，按以下顺序选择元数据文件：

1. 用户或工作流明确提供的元数据文件名或路径
2. 若已知明确环境，且 `.foundry/agent-metadata.<env>.yaml` 存在，则使用该文件
3. `.foundry/agent-metadata.yaml`
4. 若仍有多个元数据文件且上述规则未选定其中之一，则要求用户选择

阅读选定的元数据文件，并按以下顺序解析剩余的环境选择：

1. 用户明确指定的环境
2. 若选定元数据文件仅定义了一个环境，则使用它
3. 会话中先前已选定的环境
4. 元数据中的 `defaultEnvironment`

若选定元数据文件仍包含多个环境，且上述规则未选定其中之一，则要求用户选择。在每个工作流摘要中，保持选定 agent 根目录、元数据文件、环境以及上下文来源（来自 azd 或元数据）可见。

若选定的环境暴露较旧的 `testSuites[]` 元数据但未暴露 `evaluationSuites[]`，则将此会话以 `testSuites[]` 作为数据源，并在继续前于内存中将每个条目规范化为 `evaluationSuites[]` 形状。若元数据更旧，仅暴露遗留的 `testCases[]`，则同样以该列表进行规范化。保留数据集与评估器字段，保留任何现有 `tags`，仅在 `tags.tier` 缺失时映射遗留的 `priority` 至 `tags.tier`：`P0` -> `smoke`，`P1` -> `regression`，`P2` -> `coverage`。

### 第 4 步：解析 eval.yaml 本地评估意图

若选定 agent 根目录中存在 `eval.yaml`，在生成新套件之前解析它：

- `agent.name` -> 目标 agent 候选；使用前验证其是否与选定的 azd/元数据 agent 匹配。
- `dataset.local_uri` -> 本地种子数据集候选；遗留的 `dataset_file` 可在内存中规范化。
- `dataset.name` / `dataset.version` -> 已注册数据集候选。
- `validation_dataset` -> 可选验证数据集候选。
- `evaluators[]` -> 候选 Foundry 评估器名称；在将其视为远程评估器之前，需用 `evaluator_catalog_get` 验证。
- `name` -> 本地评估/套件候选；持久化为 `suiteName` 前需远程验证。
- `options.eval_model`、`options.optimization_model`、`options.max_candidates`、`options.optimization_config.model_search_space`、`options.pass_threshold`、`max_samples`、`trace_days` 与 `generation_instruction` -> 设置默认值。

将 `eval.yaml` 视为本地评估意图，而非存在 Foundry 套件的证明。仅在远程查询或注册成功后，才将同步的套件/数据集/评估器引用持久化到 `.foundry`。

### 第 5 步：解析通用配置

按以下顺序分层来源：

1. 用户的明确输入与已在会话中选定的值
2. azd 环境值用于部署上下文
3. `.foundry/agent-metadata*.yaml` 覆盖值与远程套件/缓存引用
4. `azure.yaml` 与 `eval.yaml` 本地源配置
5. 用户针对仍缺失内容的提示

若 azd 与元数据均提供同一值且二者不同，则停止并询问哪个来源具有权威性。若二者一致，则使用 azd 值，并避免在未来的元数据写入中重复改写该值。

| 生效值 | 首选来源 | 使用者 |
|-----------------|------------------|---------|
| 项目端点 | azd 环境 | deploy、invoke、observe、trace、troubleshoot |
| Agent 名称/版本 | azd agent 变量，其次 `azure.yaml` | invoke、observe、trace、troubleshoot |
| ACR | azd 环境 | deploy |
| 评估套件与缓存路径 | `.foundry/agent-metadata*.yaml` | observe、eval-datasets |
| 本地种子数据集/评估器意图 | `eval.yaml` | observe、eval-datasets |

### 第 6 步：写入元数据覆盖（仅创建/部署/观察）

在任何元数据写入（deploy、自动设置、数据集刷新或 trace 到数据集更新）时，仅在选定的元数据文件中持久化不可推导的覆盖/缓存状态：

- azd 绑定（`azd.environmentName`、`azd.service`），在有利于后续解析时
- 携带远程套件/数据集/评估器引用与本地缓存路径的 `evaluationSuites[]`
- `lastEval`、结果文件、对比摘要或明确的非 azd 覆盖

当 azd 已提供这些值，勿将其复制到元数据。若选定文件为首选的单一环境文件，则仅重写该环境块。若选定文件为遗留的多环境文件，则仅重写选定环境块。切勿自动跨兄弟元数据文件复制或合并环境。若选定环境仍使用较旧的 `testSuites[]` 或遗留 `testCases[]`，则将其改写为 `evaluationSuites[]`，并从改写条目中移除迁移的 `priority` 字段。

### 第 7 步：收集缺失值

仅使用 `ask_user` 或 `askQuestions` 工具收集用户消息、会话上下文、元数据或 azd 引导中已无法解析的值。技能可能需要以下常见值：

- **Agent 根目录** — 目标 azd 服务 project 文件夹，或包含 `.foundry/agent-metadata*.yaml` 的文件夹
- **元数据文件** — 用于本地/开发的 `agent-metadata.yaml`，或明确的旁路文件如 `agent-metadata.prod.yaml`
- **环境** — azd 环境、`dev`、`prod`，或元数据中的其他环境键
- **项目端点** — Microsoft Foundry 项目端点 URL
- **Agent 名称** — 目标 agent 的名称

> 💡 **提示：** 若用户已提供 agent 路径、环境、项目端点或 agent 名称，请直接提取，无需再次询问。

## Agent：Agent 类型

所有 agent 技能均支持两种 agent 类型：

| 类型 | 种类 | 描述 |
|------|------|-------------|
| **Prompt** | `"prompt"` | 由模型部署支持的基于 LLM 的 agent |
| **Hosted** | `"hosted"` | 运行自定义代码的容器型 agent |

将带有 `host: azure.ai.agent` 的 `azure.yaml` 服务视为 Hosted。当类型无法从项目上下文解析时，使用 `agent_get`。

## 工具使用约定

- 收集用户信息时，使用 `ask_user` 或 `askQuestions` 工具
- 使用 `task` 或 `runSubagent` 工具委托长期运行或独立的子任务（例如，环境变量扫描、状态轮询、Dockerfile 生成）
- 对于 Hosted Agents 优先使用 azd，对于 Prompt Agents 优先使用 Foundry MCP。
- 参考官方 Microsoft 文档 URL，而非嵌入 CLI 命令语法

## Azure 认证

- [Azure 认证最佳实践](references/auth-best-practices.md)

## 额外资源

- [Foundry Hosted Agents](https://learn.microsoft.com/azure/ai-foundry/agents/concepts/hosted-agents?view=foundry)
- [Foundry Agent Runtime Components](https://learn.microsoft.com/azure/ai-foundry/agents/concepts/runtime-components?view=foundry)

## 网络隔离错误

适用于**任何**对 Foundry 项目或其父 Foundry 账户的调用 —— Foundry MCP 工具、`azd`、`az` CLI、`curl`、REST 或 SDK。

若错误匹配 `Public access is disabled` / `PublicNetworkAccessDisabled` / `403 Forbidden`（来自私有端点/连接超时/项目端点 FQDN 解析为公网 IP），通常意味着父 Foundry 账户设置了 `publicNetworkAccess=Disabled` 或 `Enabled from selected IP addresses`，且当前 shell 位于其 VNet 之外。

仅当错误模糊时，通过管理平面调用（在具备读者访问权限时可在任何位置执行）与 Foundry 账户确认：

```bash
az cognitiveservices account show \
  --name <account> --resource-group <rg> \
  --query "properties.{publicNetworkAccess:publicNetworkAccess, networkAcls:networkAcls, privateEndpointConnections:privateEndpointConnections[].properties.privateLinkServiceConnectionState.status}"
```

`publicNetworkAccess: "Disabled"` —— 或 `"Enabled"` 且 `networkAcls.ipRules` / `virtualNetworkRules` 非空 —— 确认了隔离。若 `publicNetworkAccess: "Enabled"` 且 `networkAcls` 为空，则该失败是调用方侧的网络问题（例如，在具有私有端点的 VNet 内部，Private DNS 将 FQDN 解析为公网 IP），而非账户配置问题。

若确为网络隔离问题，支持的连接选项在 [Choose a secure connection method to Foundry](https://learn.microsoft.com/azure/foundry/how-to/configure-private-link#choose-a-secure-connection-method-to-foundry) 中文档说明。

> ℹ️ Foundry MCP 工具即使从 VNet 内部也无法访问受 VNet 隔离的项目。
