---
name: service-helpagent-coordinate
description: 用于通过引导式四步流程设置、配置、接地或启用 Salesforce 帮助代理（在服务云中为 Agentforce 服务代理）。在用户说出以下任何指令时使用：设置/创建/构建/添加帮助代理、服务代理或支持聊天代理；在网站或 Experience Cloud/LWR 站点上添加或嵌入聊天小部件；将帮助代理放置到渠道（网页聊天、语音、电话、帮助门户）；将帮助代理接地到 Salesforce 知识库；或希望 AI 回答客户问题、管理支持案例并升级至人工。即使请求名称仅包含一部分或引用 help-agent-spec.md 或 Agentforce 快速设置向导，此技能也适用。在以下情况下不触发：创建全新的、无帮助代理谱系的代理（使用 agentforce-adlc:agentforce-generate）、配置 OAuth/ECAs（使用 integration-connectivity-connected-app-configure）或仅部署元数据（使用 platform-metadata-deploy）。
---

# service-helpagent-coordinate: Service Cloud Help Agent, guided setup

使用此技能从 Claude Code 在 Salesforce 组织中创建一个 **Service Cloud Help Agent**（Agentforce Service Agent），并遵循与 Help Agent 快速设置向导相同的引导流程。这是一个 **coordinate** 技能：它协调现有技能以符合规范规范——它 **不** 编写新的代理原语。

## 此技能存在的原因

Salesforce 的官方 Help Agent 模板创建 API 尚未发布。如果没有它，Claude 没有内置的“Help Agent”概念，否则会生成一个通用代理。`assets/help-agent-spec.md` 补充了缺失的 API：其代理脚本是最终快速启动 UI 将生成的规范模板。将规范视为代理谱系（主题、操作、说明）的来源。

## 范围

**在范围内：**
- 引导式、四个检查点的 Help Agent 设置（身份 → 基础 → 渠道 → 正式上线）
- 通过 Agentforce 数据库库 (ADL) 进行知识基础
- Web Chat / Help Portal 渠道设置和 Experience Cloud 站点嵌入
- 准备情况检查（许可证、Einstein Agent 用户、Data Cloud 权限集）

**超出范围——委托给其他地方：**
- OAuth / 外部客户端应用设置 → [integration-connectivity-connected-app-configure](../integration-connectivity-connected-app-configure/SKILL.md)
- 无 Help Agent 谱系的原始代理编写 → `agentforce-adlc:agentforce-generate`
- 元数据部署/检索 → `platform-metadata-deploy`

## 前置条件

- 已安装 Claude Code + Salesforce CLI 并有一个经过身份验证的组织（参见存储库 `README.md`）
- 已注册 MCP 服务器：`salesforce-api-context`、`metadata-experts`、`sobject-reads`
- Salesforce 技能已安装到 `.agents/skills/`（或 `.claude/skills/`）
- **一个启用了所需功能（或可通过元数据启用）的 Salesforce 组织：** Agentforce、Einstein 生成式 AI、知识、Experience Cloud 和 Data Cloud。任何满足此条件的组织形状都可以工作——生产、沙盒、草稿或开发者版。`assets/help-agent-spec.md` §4.0 中的准备情况检查检测每个功能并启用可以启用的内容；如果缺少必需的功能且无法打开，则它会停止并显示清晰的提示信息。

## 此技能协调的技能

规范会提供这些现有技能——**不要** 编写新的 Help Agent 技能：

| 技能 | 角色 |
|---|---|
| `agentforce-adlc:agentforce-generate` | 代理编写 + ADL 预配/基础（参见其 `references/data-library-reference.md`、`references/org-setup-for-adl.md`） |
| `dx-org-permission-set-assign` | Data Cloud 权限集分配 |
| `service-digital-engagement-channel-configure` + `service-agentforce-channel-configure` | 部署渠道（队列路由），然后 PATCH `SessionHandlerId` 以绑定代理（参见 `references/channel-web-chat.md`） |
| `service-digital-engagement-deployment-configure` | 嵌入式服务部署——支持 LWR（`ChatterNetworkPicasso`）和 Aura（`ChatterNetwork`）站点 |
| `experience-lwr-site-generate` | Experience Cloud (LWR) 站点——当组织还没有 Live LWR 站点时使用 |
| `service-digital-engagement-messaging-site-integrate` | 小部件放置 + 嵌入（检查点 4） |

## Agentforce 编写安全预检（强制执行，硬性门槛）

此插件本地预检会覆盖 `assets/help-agent-spec.md` 中任何冲突的顺序或直接的 Agentforce CLI 示例。在创建 Einstein Agent 用户、启用功能、生成元数据、创建或检查 Agentforce 数据库库、加载 `references/agent-script.md` 或开始任何编写、预配、部署、发布或激活操作之前，针对选定的组织和实时插件会话**运行一次**。解决目标组织别名是此门槛前唯一允许的工作。

承重顺序是：

```text
agentforce-adlc:agentforce-generate 能力检查
                    ↓
非破坏性组织编写能力探测
                    ↓
agentforce-adlc:agentforce-generate 编写委托
                    ↓
后续准备情况、生成、ADL 和生命周期操作
```

### 第 1 步 — 解析所有者能力

`agentforce-adlc:agentforce-generate` 是由单独的 `agentforce-adlc` 插件拥有的 `agentforce-generate` 技能的插件限定标识。Salesforce CLI 的可用性**不能**证明插件或技能可用。

1. 执行一个无操作 Skill-tool 调用来 `agentforce-adlc:agentforce-generate`，其请求说明：`仅进行能力可用性探测；不读取项目文件、运行 CLI 命令或更改本地或组织状态。` 此限定调度是权威的实时会话能力检查；**不要** 探测或委托给未限定的 `agentforce-generate`，因为不同的工作区或扁平技能可能满足该名称。调度仅检查注册，并且不是开始所有者工作流的权限。`Unknown skill: agentforce-adlc:agentforce-generate` 结果表示所有者能力在此会话中未注册。任何正常技能响应，包括使用/参数响应，都表示它是可调用的。
2. 仅当限定调度未知时，运行插件本地、只读的已安装插件注册表检查：

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/helpagent_dependency_preflight.py"
   ```

   帮助程序内部调用文档中记录的 `claude plugin list --json` 注册表操作，验证组件 `@` 之前为 `agentforce-adlc` 的确切插件 ID，并仅发出清理的分类；**不要** 打印或转发原始注册表 JSON，因为不相关的插件配置可能包含敏感值。此注册表结果是指导性的：缓存目录、已安装条目或 `installed_enabled` 不能替代限定技能调度作为实时会话可用性的证明。**不要** 从相对缓存路径推断安装；已安装插件路径取决于市场和技术版本。
3. 停在 **Help Agent — Agentforce 依赖预检**，然后精确地遵循帮助程序的 `registryState`：
   - `installed_enabled`：解释 `agentforce-adlc` 已安装并启用，但在此会话中其技能未注册。告诉用户运行 `/reload-plugins`（或如果重新加载仍然无法暴露它，则重新启动主机），然后继续此 Help Agent 任务。
   - `installed_disabled`：解释 `agentforce-adlc` 已安装但已禁用。建议启用帮助程序返回的确切清理 `pluginId`（通常为 `claude plugin enable agentforce-adlc@claude-plugins-official`），等待明确批准后再更改插件状态，然后告诉用户运行 `/reload-plugins` 并继续此 Help Agent 任务。
   - `missing`：解释 Agentforce 编写需要缺失的 `agentforce-adlc` 插件。建议 `/salesforce-development:plugin-install agentforce-adlc`，等待明确批准后再调用该受保护的安装流程，并精确遵循其源/nonce 确认。安装后，告诉用户在继续之前运行 `/reload-plugins`。**不要** 将成功的安装视为同一会话技能可用性。
   - `inconclusive`：报告无法解决安装状态。提供安装/启用 + 重新加载指导作为替代方案，但**不要** 变更插件状态或猜测能力存在。

在此停止时，保留并报告选定的组织、用户进入的检查点、确认的身份/基础/渠道选择、本地项目路径以及早期运行产生的每个持久标识符（Einstein Agent 用户、Agentforce 数据库库/库 ID、`rag_feature_config_id`、代理/包 DeveloperName、渠道、部署和站点 ID）。**不要** 删除、重新创建、回滚或丢弃有效的先决条件工作。预检本身不会创建持久状态，因此继续时从命名的依赖检查点开始，并保留这些事实。

**没有协调器回退。** 当 `agentforce-adlc:agentforce-generate` 不可用时，**不要** 手动编写或重建 `.agent` YAML、运行原始 `sf agent adl` 预配命令、调用 `sf agent generate authoring-bundle` 或重现所有者技能的任何部分。停止并使所有者可用。

### 第 2 步 — 无更改地探测选定组织

仅在步骤 1 证明 `agentforce-adlc:agentforce-generate` 可调用时，运行插件本地探测：

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/helpagent_authoring_preflight.py" --target-org "$ORG"
```

帮助程序首先使用 `sf org display --json` 验证访问权限，然后针对临时本地 DX 项目中的固定最小包运行文档中的 `sf agent validate authoring-bundle --json` 操作。验证调用代理脚本编译器，但不会部署或创建/更新组织元数据；临时项目会被删除。这是目前可用的最强支持的非破坏性检查，因为 CLI 没有独立的代理脚本权限检查命令。

精确地遵循其 JSON `outcome`：

| 结果 | 协调器操作 |
|---|---|
| `ready` | 此组织的会话中可以访问通用代理脚本编译器。继续到步骤 3。**不要**声称 Service Agent、Data Cloud、知识、许可证座位、权限或渠道已验证；所有者技能仍然会检查这些。 |
| `authentication_or_org_access_failure` | 停在 **Help Agent — Agentforce 编写能力预检**。重新身份验证或选择可访问的组织，然后重新运行此探测。 |
| `agentforce_authoring_unavailable_or_not_entitled` | 停在同一检查点。记录的编译器 `AgentApiNotFound` / `ERROR_HTTP_404` 表示此组织或区域中无法访问代理脚本编写端点；请组织管理员或 Salesforce 支持启用/上载代理脚本编写，然后重新运行。**不要**将其标记为本地权限集或 CLI 问题。 |
| `transient_cli_or_service_failure` | 停在同一检查点。保留状态并在 CLI/网络/服务健康恢复后重试探测；等待时**不要**轮询、生成或预配。 |
| `capability_cannot_be_conclusively_verified` | 停在同一检查点。修复/更新 Salesforce CLI 和 `agentforce-adlc` 环境，或获得权威的组织上载确认，然后重新运行。**永远不要**使用版本、许可证查询、现有 Bot/Agentforce 记录、Data Cloud 可用性或另一个代理来声称权限通过。 |

对于每个非就绪结果，报告帮助程序的简洁修复措施、选定的组织、步骤 1 中保留的恢复状态列表（Einstein Agent 用户、Agentforce 数据库库/库 ID、`rag_feature_config_id`、代理/包 DeveloperName、渠道、部署和站点 ID），并且探测未更改组织状态。**不要**在返回 `ready` 之前继续；不确定的结果是保守的停止，**不是**忽略警告。组织类型暴露不同的功能和许可证表面，因此直接编译器结果——而不是假设的生产/沙盒/草稿/开发者版功能集——对此狭窄的门槛具有权威性。

### 第 3 步 — 委托给所有者

仅在步骤 1 和 2 通过后，将 Agentforce 特定的准备情况、Agentforce 数据库库工作、代理元数据生成、验证、发布和激活委托给 `agentforce-adlc:agentforce-generate`。传递选定的组织、规范 Help Agent 路径、当前检查点、确认的输入和保留的标识符，以便它重用有效的工作。Help Agent 技能仍然是检查点和渠道协调器；它消耗所有者技能的结果，并且**永远不会**替代协调器编写的 `.agent` YAML 或原始 ADL 预配。

---

## 工作流

首先运行上述强制执行的 Agentforce 编写安全预检。只有在它返回 `ready` 后，才读取 `assets/help-agent-spec.md`——在插件本地安全覆盖后，它是权威的流程，并且有意保持简短。**不要**预加载其余部分。重或条件性材料被拆分为 `references/`，并且仅在流程到达它时才读取（渐进式披露——这是故意的，以保持令牌使用率低）：

- **`references/agent-script.md`** — 约 500 行的规范代理脚本 + 占位符列表。仅在您准备好创建代理后加载它，**不是**在检查点 1、3 或 4 期间——加载它。
- **`references/channel-web-chat.md`** — Web Chat 预配细节。仅在用户在检查点 3 选择 Web Chat 时加载。
- **`service-concierge-portal-generate`** — Help Portal / Agentforce Concierge 门户部署。**如果用户在检查点 3 选择 Help Portal，则委托给此技能**——**不要**在此处内联门户运行手册步骤。传递 `$ORG`、`$BOT_ID` 和 `$BOT_DEV_NAME` 作为上下文，以便该技能跳过其自己的入口点问题。
- **`references/channel-voice.md`** — 语音渠道连接细节（仅限现有号码）。仅在用户选择语音时加载。

读取与用户选择匹配的一个渠道文件——**永远不要**读取所有三个。然后运行交互式设置**不要**一次性执行：按顺序引导用户完成四个检查点，并在每个检查点等待回复。

### 准备情况检查（静默、强制执行、不要重新排序）
此检查仅在编写安全预检返回 `ready` 后开始。Agentforce 特定的检测、启用、Agentforce 用户设置、Data Cloud 访问、ADL 工作 和 编写仍然由 `agentforce-adlc:agentforce-generate` 拥有；委托这些要求并验证其返回结果。下面的命令定义了必需的结果和后续预发布验证，而不是当所有者技能缺失时协调器的一个后备授权。

顺序是承重的——在步骤 3 运行步骤 2 失败是因为 Data Cloud 权限集在组织中直到 Data Cloud 本身打开后才存在：
1. **验证 PSL 座位可用性，然后为该代理创建一个专用的 Einstein Agent 用户。** 首先确认三个必需的 PSL 有可用座位：
   ```bash
   sf data query --target-org $ORG --json \
     --query "SELECT MasterLabel, TotalLicenses, UsedLicenses FROM PermissionSetLicense WHERE DeveloperName IN ('AgentforceServiceAgentUserPsl', 'GenieDataPlatformStarterPsl', 'EinsteinGPTPromptTemplatesPsl')"
   ```
   对于每个，`UsedLicenses < TotalLicenses` 必须为真。如果任何 PSL 已满，停止并显示哪个已用完——PSG 分配将失败，并且技能在座位被释放或预配之前无法做任何事。

   如果所有三个都有座位，则创建用户。**不要**重用任何现有的 Einstein Agent 用户——每个 Help Agent 都有自己的。用户名：`{agentDevName}_user@{orgId}.ext`（15 个字符的组织 ID 从 `sf org display`）。电子邮件：`noreply@salesforce.com`。配置文件：`Einstein Agent User`（查询 `SELECT Id FROM Profile WHERE Name = 'Einstein Agent User'` 以获取 ProfileId，然后 `sf data create record --sobject User`）。如果用户名与完全相同的用户已存在，则重用它（idempotent）。然后分配以下四个**在发布代理之前**：
   - `AgentforceServiceAgentUserPsg`（权限集组）——一次调用分配三个 PSL：`Agentforce Service Agent User`、`Data Cloud` 和 `Einstein Prompt Templates`。使用 `sf org assign permsetgroup`。
   - `AgentforceServiceAgentSecureBase`（权限集）——所有服务代理都需要。使用 `sf org assign permset`。
   - `AgentforceKnowledgeUser`（权限集，`force` 命名空间）——因为 Help Agent 使用 `knowledge:` 块。使用 `sf org assign permset`。
   - `{AgentName}_Access`（自定义权限集）——由 `agentforce-adlc:agentforce-generate` 为代理特定 Apex/对象访问创建。

   验证 PSL 分配已落地：`SELECT PermissionSetLicense.DeveloperName FROM PermissionSetLicenseAssign WHERE Assignee.Username = '{agentDevName}_user@{orgId}.ext'` — 期望 `AgentforceServiceAgentUser`、`DataCloud`、`EinsteinPromptTemplates`。

**捕获用户名** (`{agentDevName}_user@{orgId}.ext`) — 它是代理脚本中 `<default_agent_user_placeholder>` 的值。代理在运行时以该用户身份运行。

**预发布门禁 — 在每次 `sf agent publish authoring-bundle` 调用之前进行验证。** 跳过此步骤会导致被屏蔽的 401→404：当缺少 `AgentforceServiceAgentUserPsg` 时，SFAP 返回 HTTP 401 "用户没有访问代理的权限"，而 jsforce 的会话刷新重试将 401 静默转换为 `ERROR_HTTP_404`。在调用 CLI 之前，请验证所有四个分配是否存在：

```bash
AGENT_USER_ID=$(sf data query --target-org $ORG --json \
  --query "SELECT Id FROM User WHERE Username='{agentDevName}_user@{orgId}.ext'" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['records'][0]['Id'])")

# 必须返回恰好 1 行 — 如果为 0，则在继续之前进行分配
sf data query --target-org $ORG --json \
  --query "SELECT PermissionSetGroup.DeveloperName FROM PermissionSetAssignment \
           WHERE AssigneeId='${AGENT_USER_ID}' \
           AND PermissionSetGroup.DeveloperName='AgentforceServiceAgentUserPsg'"

# 必须返回 2 行 — 如果任何缺失，则在继续之前进行分配
sf data query --target-org $ORG --json \
  --query "SELECT PermissionSet.Name FROM PermissionSetAssignment \
           WHERE AssigneeId='${AGENT_USER_ID}' \
           AND PermissionSet.Name IN ('AgentforceServiceAgentSecureBase','AgentforceKnowledgeUser')"
```

在所有四个分配都返回非空结果之前，不要调用 `sf agent publish authoring-bundle`。

2. **启用数据云** — 必须在步骤 3 之前完成（权限集在数据云开启之前不存在）。如果数据云尚未配置，请从一开始就向用户提供选择 — 开启并稍后回来，或者现在等待。
3. **关键 — 启用后立即分配数据云权限集。** 不可协商 — 跳过它会导致代理在运行时返回空的 `knowledgeSummary`，即使 ADL 索引报告 SUCCESS。步骤 1 中分配的 PSG 在数据云开启后涵盖此问题。

### 识别用户输入的位置

**检查点 1（代理身份）和检查点 3（渠道）必须始终在当前对话中与用户确认 — 永远不要从先前会话、压缩摘要或技能参数中推断。** 这些是用户拥有的决策；基于先前运行的过时上下文将配置错误的代理或错误的渠道。

如果用户在当前对话回合中的开场消息明确指明了代理和/或渠道（例如 "在 Web Chat 上设置 Master Yoda"），则将其作为输入并确认后再继续。如果没有在当前回合中说明，则询问。

对于组织别名：如果用户在当前会话中一直在针对特定的组织工作，则使用该组织。否则询问。

**不要假设每次运行都从检查点 1 开始。** 阅读开场提示并在正确的检查点输入：身份决定后 → 检查点 2（基础）；基础完成后 → 检查点 3（渠道）。当提示明确命名或暗示后续检查点（例如 "设置基础"、"连接 Web Chat 渠道"） — 并且说明或明确暗示先前检查点已经完成时 — 接受先前检查点为既定，在命名的检查点范围内输入，并为它生成已确定的报告。不要强制重新确认完整的引导身份，不要从检查点 1 重新开始，不要要求在对话中重新确认先前的决策。提示为输入的检查点提供的值（受众 → `authMode`、命名站点、类别）是决策，而不是要重新询问的问题。

如果开场提示命名 **语音/电话/电话/IVR**，请阅读 `references/channel-voice.md` 并从检查点 3 的顶部作为语音分支开始遵循。

### 检查点 1 — 认识你的代理
请求四个信息（提供这些确切默认值，以便引导决策报告可以无需加载 `assets/help-agent-spec.md` 列出它们）：
1. **代理名称** — 默认 `Help Agent`（DeveloperName `Help_Agent`）。
2. **语言** — 默认 `en_US`。
3. **欢迎问候** — 默认 `"Hi, I'm {Agent Name}. How can I help you today?"`。
4. **语气** — 默认 `"calm, patient, friendly service agent — warm but professional, short sentences, never robotic."`。

当开场提示命名 Q&A / 案例管理 / 人工升级时，明确指出这些映射到标准的四代理形状（代理路由器 → 通用 FAQ、服务客户验证、案例管理、升级） — 不要发明不同的设计。

### 检查点 2 — 为你的代理提供上下文（基础）
询问哪个知识源（Salesforce Knowledge / 文件 / 网站同步）。基础是 **配置一个 Agentforce 数据库**，而不是设计搜索 — 代理的 `knowledge:` 块在运行时执行检索。此检查点必须产生所有五个：
1. **将委托配置给 `agentforce-adlc:agentforce-generate`** — 它拥有 ADL 创建/索引/发布。不要手工制作数据库元数据。
2. **一个专用的命名库** — 创建 `Help_Agent_Knowledge`。**永远不要连接标准的 `All_Records_and_Fields_Default`**（它在试用或预加载样本数据组织中位于 `NOT_SCHEDULED` 并返回空的 `knowledgeSummary` 而没有任何错误）。
3. **类别选择** — 对于 Salesforce Knowledge，查询组织的数据库类别组。仅在交互式运行中询问要基于哪些类别；对于非交互式/范围运行，决定合理的默认值（**组织的默认数据库类别组**，或者如果没有指定则为所有组）并在已确定的报告中明确注明默认值（例如 "知识数据类别未指定 — 选择了组织的默认组"）。不要在报告中停顿询问。
4. **等待索引门禁** — 检查并只有在 `indexingStatus.status ∈ {COMPLETED, READY, SUCCESS}` 时才继续。`NOT_SCHEDULED` 不是成功。
5. **捕获 `rag_feature_config_id`**（格式 `ARFPC_<libraryId>`）并将其连接到代理脚本中的 `knowledge:` 块 — 永远不要硬编码。

**反规则：** 永远不要通过设计对知识文章进行 SOQL/SOSL/GraphQL/Apex 搜索来响应基础请求。基础是 ADL 配置；检索是代理在运行时的任务。

### 检查点 3 — 添加到渠道

**首先，始终发现已经存在的内容 — 永远不要只呈现 Web Chat / 帮助门户 / 语音，好像它们是唯一选项。** 完整遵循 `assets/help-agent-spec.md` §4.3 步骤 1：查询每个 `MessagingChannel`，按 `<messagingChannelType>` 对每个进行分类，并显示每种类型存在的内容（WhatsApp、SMS 等），而不仅仅是下面的三个分支。跳过此发现是本节防止的错误。

使用队列路由（`service-digital-engagement-channel-configure`）部署新渠道，然后将代理连接委托给 `service-agentforce-channel-configure`。按渠道类型分支：

- **Web Chat** → 阅读 `references/channel-web-chat.md`。创建消息渠道 + 嵌入式服务部署。**首先询问部署目标，在查询任何内容之前**："自己的（非 Salesforce）网站"（推荐默认值 — 短路到嵌入片段路径）或 "一个 Salesforce Experience Cloud 站点"。只有在用户选择 Experience Cloud 时，才运行 **查询优先模式**：

  ```sql
  SELECT Id, Name, UrlPathPrefix, SiteType, Status
  FROM Site
  WHERE SiteType IN ('ChatterNetworkPicasso', 'ChatterNetwork') AND Status = 'Active'
  ```

  两者 LWR (`ChatterNetworkPicasso`) 和 Aura (`ChatterNetwork`) 站点都支持 `experience_messaging:embeddedMessaging` 小部件。过滤掉以 `ESW_` 开头的站点（内部 ESD 框架，不是真正的 Experience Cloud 站点）。在同一回合中解决站点**，不要推迟**：
  - **零个真实站点** → 通过 `experience-lwr-site-generate` 创建一个（推荐帮助中心模板），或者回退到 "在我的自己的网站上部署（获取片段）"。
  - **恰好一个** → 在使用之前与用户确认（可能有一个不同的受众的现有站点）；不要无声地采用它。
  - **多个** → 在同一回合中，显示执行的 SOQL，将结果作为表格（`Name | Type | UrlPathPrefix`）列出，说明 "直到您选择之前，不会创建或修改任何站点"，然后询问要针对哪个目标（提供 "创建一个新的 LWR 站点" 和 "在我的自己的网站上部署"）。不要推迟到 "我稍后会回来" — 现在显示结果。

  不要通过硬编码的名称或 URL 路径前缀进行过滤 — 正确的站点取决于客户的组织。

- **帮助门户** → 委托给 `service-concierge-portal-generate`（在 LWR 站点上部署 Agentforce Concierge 体验）。传递解析的 `$ORG`、`$BOT_ID` 和 `$BOT_DEV_NAME`，以便它可以跳过其入口点问题。

- **语音** → 阅读 `references/channel-voice.md` 并完全遵循。语音通过 `service-agentforce-channel-configure` 分支 B 连接现有的 `PstnVoice` 消息渠道 — 它不会配置电话号码。

- **任何其他现有渠道（WhatsApp、SMS、Facebook、Apple Business Chat、Line、电子邮件到案例、自定义）** → 没有专门的参考文件。列出发现的该类型渠道，让用户选择一个（`"将代理添加到: {MasterLabel}"`），然后直接委托给 `service-agentforce-channel-configure`，并传递代理和渠道 DeveloperNames — 它自己解析回退队列并选择路由分支（增强聊天/消息为分支 A，电子邮件到案例为分支 C）。此技能仅将代理连接到已存在的渠道；它从不配置底层的第三方/电子邮件基础设施。

**每个渠道分支完成后，循环 — 询问用户是否要添加另一个渠道。** 一次一个渠道分支完成（成功或失败），通过 `AskUserQuestion` 呈现：

- **添加另一个 [相同类型] 渠道** — 提供该类型剩余未连接的渠道；重新运行分支，跳过本会话已连接的渠道。
- **添加不同类型的渠道** — 返回到检查点 3 的顶部（重新查询 `MessagingChannel`，重建类型列表，从选项中省略已连接的渠道）。
- **完成 — 继续上线** — 退出循环并进入检查点 4。

跟踪已连接的渠道，以免重新提供；循环继续，直到用户选择 "完成" 或所有渠道都已连接。

**出站升级在此处连接，在入站路由之后，而不是在检查点 4。** 对于 Web Chat/语音分支，在入站路由的同一委托调用中调用 `service-agentforce-channel-configure` 阶段 3（解析升级队列 → 创建/重用路由流程 → 添加连接块 → 发布）。推迟连接块连接到检查点 4 重复了阶段 3 的原子序列，并强制执行额外的发布。

**当开场提示命名两个或多个渠道时**（例如 "添加 Web Chat，然后也添加语音 — 添加两者"），提示授权了每个命名的渠道 — 将它们全部视为已完成的任务。不需要新的用户回复即可从一个命名的渠道转移到下一个；开场请求本身*就是*授权。跳过分支之间的 `AskUserQuestion` 对于提示命名的渠道，连接每个命名的渠道按声明顺序，并且仅在提示未命名的渠道时才回退到循环的 `AskUserQuestion`。报告必须显示每个命名的渠道已连接 — 永远不要只显示第一个，其余的作为意图或 "下一步"（即使第一个渠道完美，这也算作不完整的循环）。在已确定的检查点 3 行（或在表格下方短跟踪中），按顺序明确所有这些：
1. **第一个渠道完成**作为已确定的事实（渠道类型、Web Chat 的 `authMode`、解析的站点/号码、ESD 状态） — 不是 "将要添加"。
2. **继续授权**：提示命名的下一个渠道，因此流程在没有分支提示的情况下继续。永远不要报告未发生的用户回复 — 声称用户 "在 AskUserQuestion 后继续" 对于提示命名的渠道虚构了交互并破坏了合同。
3. **后续渠道入口**：流程重新进入检查点 3 以每个命名的渠道，每个都带到自己的已确定结果。如果确实运行了分支提示（提示未命名的渠道），则报告分支提示的选项和选择；否则不报告。
4. 只有在所有命名的渠道都已连接（或用一句话原因阻止）后，流程才会达到上线。

### 检查点 4 — 审核并上线
一旦渠道循环退出（"完成"），运行两个阶段（下面的 Phase A 是以前作为独立的 "Checkpoint 3.5" 存在的阶段）：

**Phase A — 静默预飞行（内部 — 永远不要宣布）。** 静默运行；仅在失败时显示输出。每个检查都必须在 Phase B 之前通过：
1. 运行用户和 Einstein Agent User 的数据云访问（委托给 `agentforce-adlc:agentforce-generate`）。
2. ADL 已激活**并且**已基础化 — 运行一个 canary 检索，使用捕获的 `rag_feature_config_id`；如果尽管报告 SUCCESS 为空，则显示 **已知的手动步骤**（权限集上的数据空间范围）原文，等待确认，重新运行。
3. 消息渠道是 **Active**（断言；初始激活是渠道配置技能的工作，不是站点集成技能的工作）。这是流程检查或设置渠道活动状态的唯一地方 — Phase B 不重复它。

**Phase B — 明确上线步骤（向用户说明）。** 验证小部件是否已部署到站点（LWR + Aura）— 部署已经发生在检查点 3 步骤 C.5 通过 `service-digital-engagement-messaging-site-integrate`；如果验证失败，则重新运行注入。然后：(a) 确认 **升级流程** 已连接（在检查点 3 通过 Phase 3 配置 — 验证，不要重新连接）；(b) **在 Setup → Embedded Service Deployments 中发布嵌入式服务部署**；然后提供一起测试的机会。未发布的部署会静默发送一个死小部件。

## 规则 / 约束

## 长列表呈现规则

`AskUserQuestion` 最多 4 个选项。对于用户选择一个的发现项目列表（站点、渠道、队列、ADL）**1–6 项** — 每页 3 项，"显示更多 (N 剩余)" 作为选项 4，固定选项（创建新的等）仅在最后一页。**7+ 项** — 以纯文本列出名称，让用户键入他们的选择，不区分大小写进行验证，确认后再继续。

**例外 — 多选列表（例如检查点 3 的渠道类型选择器）永远不会分页。** 分页假设单选。对于任何多选列表，一旦选项超过 4 个，直接跳转到纯文本列表和键入模式，无论数量如何 — 见 `assets/help-agent-spec.md` §4.3 步骤 1。

| 规则 | 理由 |
|---|---|
| 在两个创作安全门都通过之前，永远不要运行就绪检查、元数据生成、ADL 或 Agentforce 生命周期工作 | 能力所有权必须首先解决；然后，直接的非修改编译器探测必须为选定的组织返回 `ready` |
| 永远不要用 `.agent` YAML 或原始 `sf agent` 创作/ADL 命令替换缺失的 `agentforce-adlc:agentforce-generate` 技能 | `agentforce-adlc` 拥有此行为；安装/启用它，重新加载会话，并从命名的依赖检查点恢复，保留先前的状态 |
| 永远不要一次性设置 | 这是一个引导式对话；在每个检查点等待用户输入 |
| 永远不要跳过或重新排序就绪步骤 | 在数据云启用之前不存在权限集 — 你会看到 `PermissionSet not found: GenieUserEnhancedSecurity` |
| 永远不要在 Checkpoint 4 阶段 A 之前用空的 ADL 检索推进 | 发送一个无声损坏的代理 |
| 永远不要硬编码站点名称或 URL 路径前缀 | 正确的目标 LWR 站点取决于客户的组织 — 首先查询，然后决定 |
| 永远不要将 ESW 前缀的站点作为小部件部署目标 | `ESW_*` 站点是内部 ESD 端点脚手架 — 在向用户展示站点选项之前，在后处理中过滤掉它们 |
| 通过 Connect API 创建嵌入式服务部署作为 V2，永远不要裸露元数据部署 — 并通过 `experience_messaging:embeddedMessaging` LWR 组件嵌入 V2 ESD | 元数据 API 默认为旧版 V1 (`WebV1`，*“Web (v1)”* 在设置中)，这会破坏增强型网页聊天；在 v67.0+ 上通过 Connect API 创建，使用 `clientVersion: WebV2`。客户小部件通过键为 `deploymentName` 的 LWR 组件挂载。完整的六属性形状、工具-API 补丁路径和访客浏览器验证在 `references/channel-web-chat.md` 中 |
| 始终为帮助代理创建一个专用的 ADL — 永远不要连接到标准的 `All_Records_and_Fields_Default` 库 | 在试用或预加载样本数据组织中，标准库卡在 `NOT_SCHEDULED` 中，永远不会索引；将代理连接到它会在运行时产生空的 `knowledgeSummary`，没有可见错误。在 Checkpoint 2 创建 `Help_Agent_Knowledge`，等待 `indexingStatus ∈ {COMPLETED, READY, SUCCESS}` 之后再连接 |
| 永远不要在 Checkpoint 4 中不发布嵌入式服务部署并激活通道 | 两者都是小部件服务所必需的。如果 ESD 通过 Connect API `deployment/setup` 调用创建，它已经发布 — 验证 *"Published on:"* 是否有戳记，标题没有 `(v1)` 后缀 |
| Web Chat、Help Portal 和 Voice 有专用分支；任何其他现有通道类型（WhatsApp、SMS、Facebook、Apple Business Chat、Line、邮件到案例、自定义）都通过 `service-agentforce-channel-configure` 通用连接 | 发现（§4.3 步骤 1）必须显示所有通道类型 — 当存在其他通道时只提供三个专用分支是此检查点防止的 Bug。对于 Web Chat，始终运行部署后断言（重新获取 MessagingChannel，断言 `embeddedConfig.authMode`；默认 `UnAuth`）— 错误选择会无声地发送一个无法为访客渲染的小部件。报告 `authMode` 作为纯值（`authMode: UnAuth`）；不要叙述断言。永远不要发出旧版 `esw.min.js` / Live Agent V1 片段 |

## 输出预期

唯一的可交付成果是单个 `report.md`：一个**决定和完成的状态报告**，而不是设计文档。存在两种形状 — **已确定的报告**（当流程执行了步骤时，表格中有具体确定的值），和**引导式决策报告**（当流程处于用户拥有的决策点时，展示选择，不要虚构）。决策单元格内永远不要犹豫（“待捕获”、“待定”、“将创建”）；永远不要虚构不透明的 ID；永远不要制造请求未针对的检查点上的阻塞。完整模板、每形状规则、单决策推理调用（就绪顺序、`authMode`），以及“永远不包含”的评分失败列表在 **`references/output-report-format.md`** 中 — 写报告前先阅读它。

## 参考文件索引

| 文件 | 何时阅读 |
|---|---|
| `assets/help-agent-spec.md` | 在创作安全预检返回 `ready` 后 — 插件本地安全覆盖后的规范流程；设计上很小。指向下面的文件 |
| `references/agent-script.md` | 仅在代理创建时（在 Checkpoint 2 之后） — 规范代理脚本 + 占位符 |
| `references/channel-web-chat.md` | 仅在用户在 Checkpoint 3 选择 Web Chat 时 |
| `service-concierge-portal-generate`（外部技能） | 仅在用户在 Checkpoint 3 选择 Help Portal 时 — 委托，不要内联 |
| `references/channel-voice.md` | 仅在用户选择 Voice（连接到一个现有的 `PstnVoice` 通道；没有号码配置）时 |
| `references/output-report-format.md` | 在编写最终 `report.md` 之前 — 两种报告形状、模板和评分失败列表 |
