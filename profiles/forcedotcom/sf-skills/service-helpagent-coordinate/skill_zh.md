# service-helpagent-coordinate: Service Cloud Help Agent, guided setup

使用此技能在 Salesforce 组织中从 Claude Code 站立一个 **Service Cloud Help Agent**（一个 Agentforce Service Agent），遵循与 Help Agent 快速设置向导相同的引导流程。这是一个 **协调** 技能：它协调现有技能针对规范规范——它**不**创建一个新的代理原语。

## 此技能存在的原因

Salesforce 的官方 Help Agent 模板创建 API 尚未发布。没有它，Claude 没有内置的“Help Agent”概念，否则会生成一个通用代理。`assets/help-agent-spec.md` 代替了缺失的 API：其代理脚本是最终快速启动 UI 将生成的规范模板。将规范视为代理谱系（主题、操作、说明）的来源。

## 范围

**在范围内：**
- 引导式、四个检查点的 Help Agent 设置（身份 → 基础 → 渠道 → 正式上线）
- 通过 Agentforce 数据库库 (ADL) 进行知识基础
- Web Chat / Help Portal 渠道设置和 Experience Cloud 站点嵌入
- 准备检查（许可证、Einstein Agent 用户、数据云权限集）

**不在范围内——委托给其他地方：**
- OAuth / 外部客户端应用程序设置 → [integration-connectivity-connected-app-configure](../integration-connectivity-connected-app-configure/SKILL.md)
- 没有Help Agent谱系的原始代理创建 → `agentforce-generate`
- 元数据部署/检索 → `platform-metadata-deploy`

## 前提条件

- 已安装 Claude Code + Salesforce CLI 并有一个经过身份验证的组织（参见存储库 `README.md`）
- 已注册 MCP 服务器：`salesforce-api-context`、`metadata-experts`、`sobject-reads`
- Salesforce 技能已安装到 `.agents/skills/`（或 `.claude/skills/`）
- **一个启用了所需功能的 Salesforce 组织（或可以通过元数据启用）：** Agentforce、Einstein 生成式 AI、知识、Experience Cloud 和数据云。任何满足此标准的组织形状都可以工作——生产、沙盒、草稿或开发者版。`assets/help-agent-spec.md` §4.0 中的就绪检查检测每个功能并启用可以启用的内容；如果缺少必需的功能且无法打开，则显示清晰的提示信息。

## 此技能协调的技能

规范提供这些现有技能——不要创建新的 Help Agent 技能：

| 技能 | 角色 |
|---|---|
| `agentforce-generate` | 代理创建 + ADL 预配/基础（参见其 `references/data-library-reference.md`、`references/org-setup-for-adl.md`） |
| `dx-org-permission-set-assign` | 数据云权限集分配 |
| `service-digital-engagement-channel-configure` + `service-agentforce-channel-configure` | 部署渠道（队列路由），然后 PATCH `SessionHandlerId` 以绑定代理（参见 `references/channel-web-chat.md`） |
| `service-digital-engagement-deployment-configure` | 嵌入式服务部署——支持 LWR (`ChatterNetworkPicasso`) 和 Aura (`ChatterNetwork`) 网站 |
| `experience-lwr-site-generate` | Experience Cloud (LWR) 网站——当组织还没有 Live LWR 网站时使用 |
| `service-digital-engagement-messaging-site-integrate` | 小部件放置 + 嵌入（检查点 4） |

## 技能清单预飞行（建议——永远不会是硬停止）

此技能委托给几个兄弟技能。根据运行时，这些依赖关系以两种方式之一解决：作为 `.claude/skills/` 下面的目录，**或者**通过 harness 在需要时解析的运行时技能目录（没有本地目录）。因此，缺少 `.claude/skills/<name>` 目录**并不**证明依赖项不可用——当 harness 在调用时解析技能时，这是正常的。

运行此检查**一次，无声地，仅用于您自己的意识**——永远不会作为运行的第一用户界面输出：

```bash
for skill in agentforce-generate dx-org-permission-set-assign service-digital-engagement-channel-configure service-digital-engagement-deployment-configure experience-lwr-site-generate service-digital-engagement-messaging-site-integrate service-concierge-portal-generate service-agentforce-channel-configure; do
  [ -d ".claude/skills/$skill" ] && echo "OK: $skill" || echo "resolve-at-runtime: $skill"
done
```

**不要停止，并且不要以缺少依赖项的清单开头运行。** 继续进行检查点；仅在流程实际到达它时才委托给每个兄弟技能。如果——并且只有如果——一个委托步骤实际到达且该特定技能在该时刻无法解析，则在该点通过名称显示*该特定技能*。永远不要将完整的八个技能清单作为交付成果；用户不拥有这个决定，它也不是报告。

---

## 工作流

首先阅读 `assets/help-agent-spec.md`——它是权威流程，并且有意保持较小。**不要预先加载其余内容。** 重或条件性材料被拆分为 `references/`，并且仅在流程到达它时才读取（渐进式披露——这是故意的，以保持令牌使用率低）：

- **`references/agent-script.md`** — 约 500 行的规范代理脚本 + 占位符列表。仅在您准备好创建代理后加载它，即在检查点 2 之后——不要在检查点 1、3 或 4 期间加载。
- **`references/channel-web-chat.md`** — Web Chat 预配细节。仅在用户在检查点 3 选择 Web Chat 时加载。
- **`service-concierge-portal-generate`** — Help Portal / Agentforce Concierge 门户部署。**如果用户在检查点 3 选择 Help Portal，则委托给此技能**——不要在此处内联门户运行说明。将 `$ORG`、`$BOT_ID` 和 `$BOT_DEV_NAME` 作为上下文传递，以便该技能可以跳过其自身的入口点问题。
- **`references/channel-voice.md`** — 语音渠道连接细节（仅限现有号码）。仅在用户选择语音时加载。

读取与用户选择匹配的一个渠道文件——永远不要全部三个。然后运行交互式设置**不要一次性处理**：按顺序引导用户通过四个检查点，在每个回复点等待。

### 就绪检查（无声、强制、不要重新排序）
顺序是负载的——在步骤 3 之前运行步骤 2 会失败，因为数据云权限集在组织本身打开之前不存在：
1. **验证 PSL 座位可用性，然后为该代理创建一个专用的 Einstein Agent 用户。** 首先确认三个必需的 PSL 有可用的座位：
   ```bash
   sf data query --target-org $ORG --json \
     --query "SELECT MasterLabel, TotalLicenses, UsedLicenses FROM PermissionSetLicense WHERE DeveloperName IN ('AgentforceServiceAgentUserPsl', 'GenieDataPlatformStarterPsl', 'EinsteinGPTPromptTemplatesPsl')"
   ```
   对于每个，`UsedLicenses < TotalLicenses` 必须为真。如果任何 PSL 已满，请停止并显示哪个已用尽——PSG 分配将失败，并且技能在座位被释放或配置之前无法做任何事情。

   如果所有三个都有容量，请创建用户。不要重用任何现有的 Einstein Agent 用户——每个 Help Agent 都有自己的。用户名：`{agentDevName}_user@{orgId}.ext`（15 个字符的组织 ID 从 `sf org display`）。电子邮件：`noreply@salesforce.com`。配置文件：`Einstein Agent User`（查询 `SELECT Id FROM Profile WHERE Name = 'Einstein Agent User'` 以获取配置文件 ID，然后 `sf data create record --sobject User`）。如果已经存在一个完全相同的用户名，请重用它（idempotent）。然后在进行代理发布之前分配以下四个：
   - `AgentforceServiceAgentUserPsg`（权限集组）——一次调用三个 PSL：`Agentforce Service Agent User`、`Data Cloud` 和 `Einstein Prompt Templates`。使用 `sf org assign permsetgroup`。
   - `AgentforceServiceAgentSecureBase`（权限集）——所有服务代理都需要。使用 `sf org assign permset`。
   - `AgentforceKnowledgeUser`（权限集，`force` 命名空间）——因为 Help Agent 使用 `knowledge:` 块，所以需要。使用 `sf org assign permset`。
   - `{AgentName}_Access`（自定义权限集）——由 `agentforce-generate` 为代理特定的 Apex/对象访问创建。

   验证 PSL 分配已到达：`SELECT PermissionSetLicense.DeveloperName FROM PermissionSetLicenseAssign WHERE Assignee.Username = '{agentDevName}_user@{orgId}.ext'` — 期望 `AgentforceServiceAgentUser`、`DataCloud`、`EinsteinPromptTemplates`。

   **捕获用户名**（`{agentDevName}_user@{orgId}.ext`）——它是代理脚本中 `<default_agent_user_placeholder>` 的值。代理在运行时作为此用户运行。

   **发布前门禁——在每次调用 `sf agent publish authoring-bundle` 之前验证。** 跳过此步骤会导致掩码的 401→404：当 Einstein Agent 用户缺少 `AgentforceServiceAgentUserPsg` 时，SFAP 返回 HTTP 401 "User doesn't have access to agent"，而 jsforce 的会话刷新重试会将其静默转换为 `ERROR_HTTP_404`。在调用 CLI 之前验证所有四个分配是否存在：

   ```bash
   AGENT_USER_ID=$(sf data query --target-org $ORG --json \
     --query "SELECT Id FROM User WHERE Username='{agentDevName}_user@{orgId}.ext'" \
     | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['records'][0]['Id'])")

   # 必须返回正好 1 行——如果为 0，则继续分配之前
   sf data query --target-org $ORG --json \
     --query "SELECT PermissionSetGroup.DeveloperName FROM PermissionSetAssignment \
              WHERE AssigneeId='${AGENT_USER_ID}' \
              AND PermissionSetGroup.DeveloperName='AgentforceServiceAgentUserPsg'"

   # 必须返回 2 行——如果任何缺失，则继续分配之前
   sf data query --target-org $ORG --json \
     --query "SELECT PermissionSet.Name FROM PermissionSetAssignment \
              WHERE AssigneeId='${AGENT_USER_ID}' \
              AND PermissionSet.Name IN ('AgentforceServiceAgentSecureBase','AgentforceKnowledgeUser')"
   ```

   在所有四个分配返回非空结果之前，不要调用 `sf agent publish authoring-bundle`。

2. **启用数据云**——必须在步骤 3 之前完成（权限集在数据云打开之前不存在）。如果数据云尚未配置，请提前向用户提供选择——启用并稍后回来，或者现在等待。
3. **关键——启用后立即分配数据云权限集。** 非谈判——跳过它将导致一个代理，其基础在运行时返回空的 `knowledgeSummary`，即使 ADL 索引报告 SUCCESS。步骤 1 中分配的 PSG 一旦数据云打开就会覆盖这一点。

### 识别用户正在输入的位置

**检查点 1（代理身份）和检查点 3（渠道）必须始终在当前对话中确认用户——永远不要从先前会话、紧凑摘要或技能参数中推断。** 这些是用户拥有的决定；对先前运行中的上下文采取行动将配置错误的代理或错误的渠道。

如果用户在当前对话回合中的开篇消息明确命名了代理和/或渠道（例如，“在 Web Chat 上设置 Master Yoda”），请接受这些作为输入并在继续之前确认它们。如果没有在当前回合中声明，请询问。

对于组织别名：如果用户在当前会话中一直针对特定组织工作，请使用该组织。否则请询问。

**不要假设每个运行都从检查点 1 开始。** 读取开篇提示，并在正确的检查点输入：身份决定 → 检查点 2（基础）；基础完成 → 检查点 3（渠道）。当提示明确命名或暗示了后续检查点（例如，“设置基础”、“连接 Web Chat 渠道”）——并且声明或明确暗示先前检查点已经完成——接受先前检查点已确定，在命名检查点范围内输入，并为它生成一个已确定的事实报告。**不要强制重新确认引导式身份**，**不要从检查点 1 重新开始**，**不要要求在对话中重新确认先前的决定。** 提示为输入的检查点（受众 → `authMode`、命名站点、类别）提供的值是决定，而不是要重新询问的问题。

如果开篇提示命名 **语音/电话/电话/IVR**，读取 `references/channel-voice.md` 并从检查点 3 的顶部作为语音分支完全遵循它。

### 检查点 1 — 认识你的代理
询问四个问题（提供这些确切默认值，以便引导式决策报告可以无需加载 `assets/help-agent-spec.md` 而枚举它们）：
1. **代理名称** — 默认 `Help Agent`（开发者名称 `Help_Agent`）。
2. **语言** — 默认 `en_US`。
3. **欢迎问候** — 默认 `"Hi, I'm {Agent Name}. How can I help you today?"`。
4. **语气** — 默认 `"calm, patient, friendly service agent — warm but professional, short sentences, never robotic."`。

当开篇提示 Q&A / 案例管理 / 人工升级时，明确指出这些映射到规范的四子代理形状（代理路由器 → 一般 FAQ、服务客户验证、案例管理、升级）——不要发明不同的设计。

### 检查点 2 — 为你的代理提供上下文（基础）
询问哪个知识源（Salesforce Knowledge / 文件 / 网站同步）。基础是**预配一个 Agentforce 数据库库**，而不是设计搜索——代理的 `knowledge:` 块在运行时执行检索。此检查点**必须**产生所有五个：
1. **将预配委托给 `agentforce-generate`** — 它拥有 ADL 创建/索引/发布。不要手工制作数据库元数据。
2. **一个专用的命名库** — 创建 `Help_Agent_Knowledge`。**永远不要连接到标准的 `All_Records_and_Fields_Default`**（它位于 `NOT_SCHEDULED` 中，在试用或预加载样本数据组织中，并且返回空的 `knowledgeSummary` 而没有任何错误）。
3. **类别选择** — 对于 Salesforce Knowledge，查询组织的数据库类别组。仅在交互式运行中询问要基础哪些类别；对于非交互式/范围运行，决定合理的默认值（**组织的默认数据库类别组**，或者如果没有指定则为所有组）并在已确定的事实报告的阻塞问题行中明确默认值（例如，"Knowledge 数据类别未指定——选择了组织的默认组"）。不要停滞报告询问。
4. **等待索引门禁** — 检查并只有在 `indexingStatus.status ∈ {COMPLETED, READY, SUCCESS}` 时才继续。`NOT_SCHEDULED` 不是成功。
5. **捕获 `rag_feature_config_id`**（格式 `ARFPC_<libraryId>`）并将其连接到代理脚本中的 `knowledge:` 块——永远不要硬编码。

**反规则：** 永远不要通过设计 Knowledge 文章的 SOQL/SOSL/GraphQL/Apex 搜索来响应基础请求。基础是 ADL 预配；检索是代理在运行时的任务。

### 检查点 3 — 添加到渠道

**首先，始终发现已存在的——永远不要仅呈现 Web Chat / Help Portal / Voice，好像它们是唯一选项。** 完全遵循 `assets/help-agent-spec.md` §4.3 步骤 1：查询每个 `MessagingChannel`，按 `<messagingChannelType>` 对每个进行分类，并显示每个类型（WhatsApp、SMS 等）都存在（而不是仅显示以下三个分支），跳过此发现是防止此部分出现的错误。

使用队列路由 (`service-digital-engagement-channel-configure`) 部署新渠道，然后委托代理连接到 `service-agentforce-channel-configure`。按渠道类型分支：

- **Web Chat** → 读取 `references/channel-web-chat.md`。创建消息渠道 + 嵌入式服务部署。**首先询问部署目标，然后再查询任何内容**： "自己的（非 Salesforce）网站"（推荐默认值——直接跳转到嵌入代码路径）或 "一个 Salesforce Experience Cloud 站点"。只有如果用户选择 Experience Cloud，请运行**查询优先模式**：

  ```sql
  SELECT Id, Name, UrlPathPrefix, SiteType, Status
  FROM Site
  WHERE SiteType IN ('ChatterNetworkPicasso', 'ChatterNetwork') AND Status = 'Active'
  ```

  两种 LWR (`ChatterNetworkPicasso`) 和 Aura (`ChatterNetwork`) 站点都支持 `experience_messaging:embeddedMessaging` 小部件。过滤掉 `ESW_` 前缀的站点（内部 ESD 端点脚手架，不是真正的 Experience Cloud 站点）。在**同一回合**中解析站点，不要延迟：
  - **没有真实站点** → 通过 `experience-lwr-site-generate` 创建一个（推荐 Help Center 模板），或者回退到 "在我的自己的网站上部署（获取代码）"。
  - **正好一个** → 在使用之前与用户确认它（可能为不同的受众服务不同的站点）；不要默默采用它。
  - **多个** → 在**同一回合**中，显示执行的 SOQL，将结果作为表格列出 (`Name | Type | UrlPathPrefix`)，说明 "在您选择之前，没有站点被创建或修改"，然后询问要针对的目标（提供 "创建一个新的 LWR 站点" 和 "在我的自己的网站上部署"）。不要用 "我稍后回复" 来延迟——现在就显示结果。

  不要通过硬编码的名称或 URL 路径前缀过滤——正确的目标取决于客户的组织。

- **Help Portal** → 委托给 `service-concierge-portal-generate`（在 LWR 站点上部署 Agentforce Concierge 体验）。传递解析的 `$ORG`、`$BOT_ID` 和 `$BOT_DEV_NAME` 以便它跳过其自身的入口点问题。

- **Voice** → 读取 `references/channel-voice.md` 并完全遵循它。通过 `service-agentforce-channel-configure` 分支 B 连接一个 `PstnVoice` 消息渠道；如果不存在，则参考文件委托采购给 `service-agentforce-contact-center-coordinate`。

- **任何其他现有渠道（WhatsApp、SMS、Facebook、Apple Business Chat、Line、Email-to-Case、自定义）** → 没有专门的参考文件。列出该类型的渠道，让用户选择一个 (`"Add agent to: {MasterLabel}"`)，然后直接委托给 `service-agentforce-channel-configure`，并提供代理和渠道开发者名称——它解析回退队列并选择路由分支本身（分支 A 用于增强聊天/消息，分支 C 用于 Email-to-Case）。此技能仅将代理连接到已存在的渠道；它永远不会预配底层的第三方/电子邮件基础设施。

**每个渠道分支完成后，循环——询问用户是否要添加另一个渠道。** 一旦一个渠道分支完成（成功或失败），通过 `AskUserQuestion` 显示：
- **添加另一个[相同类型]渠道** — 提供剩余未连接的该类型渠道；重新运行该分支，跳过本会话已连接的渠道。
- **添加不同类型的渠道** — 返回到检查点 3 的顶部（重新查询 `MessagingChannel`，重建类型列表，从选项中省略已连接的渠道）。
- **完成——继续正式上线** — 退出循环并进入检查点 4。

跟踪已连接的渠道，以便它们不会被重新提供；循环继续，直到用户选择 "完成" 或所有渠道都已连接。

**出站升级在此处连接，立即在入站路由之后，而不是在检查点 4。** 对于 Web Chat/Voice 分支，在委托调用中调用 `service-agentforce-channel-configure` 阶段 3（解析升级队列 → 创建/重用 RoutingFlow → 添加连接块 → 重新发布）。将连接块连接延迟到检查点 4 重复了阶段 3 的原子序列，并强制执行额外的重新发布。

**当开篇提示命名两个或多个渠道时**（例如，“添加 Web Chat，然后也 Voice — 添加两者”），提示授权了每个命名的渠道——将它们全部视为已完成的任务。不需要新的用户回复即可从第一个命名渠道到下一个命名渠道；开篇请求*就是*授权。跳过分支之间的 `AskUserQuestion`，按声明顺序连接每个渠道，并且仅在提示未命名的渠道时，才回退到循环的 `AskUserQuestion`。报告必须显示每个命名的渠道已连接——永远不会只有第一个，其余的则被框架为意图或“下一步”（即使第一个渠道完美无缺，这也算作一个不完整的循环）。在已确定的检查点 3 行（或短跟踪在表格下方），明确列出所有这些，按顺序：
1. **第一个渠道完成**作为一个已确定的事实（渠道类型，`authMode` 对于 Web Chat，解析的站点/号码，ESD 状态）——不是 "将要添加"。
2. **继续授权**：提示命名了下一个渠道，因此流程在不需要任何用户回复的情况下前进。永远不要报告用户回复未发生——声称用户 "在 AskUserQuestion 后继续" 对于提示命名的渠道会编造交互并破坏合同。
3. **后续渠道输入**：流程重新进入 Checkpoint 3 以每个下一个命名的渠道，每个都带有自己的已确定结果。仅当确实运行了分支（提示未命名的渠道）时，才报告分支提示的选项和选择。
4. 只有在所有命名的渠道都已连接（或用一行简短的原因阻止）后，流程才会达到正式上线。

### 检查点 4 — 审查 & 正式上线
一旦渠道循环退出（“完成”），运行两个阶段（Phase A 以下是以前作为独立 "Checkpoint 3.5" 存在的内容）：

**Phase A — 无声预飞行（内部——永远不会宣布）。** 无声运行；仅在失败时显示输出。每个检查都必须通过才能进入 Phase B:
1. 运行时用户和数据云用户（Einstein Agent User）都有数据云访问权限（委托给 `agentforce-generate`）。
2. ADL 已激活**并且**已基础——使用捕获的 `rag_feature_config_id` 运行一个 canary 检索；如果为空，尽管 SUCCESS，请显示**已知的手动步骤**（数据空间权限集上的范围）原文，等待确认，重新运行。
3. 消息渠道处于 **Active** 状态（断言；初始激活是渠道配置技能的工作，而不是站点集成技能的工作）。这是流程检查或设置渠道活动状态的唯一地方——Phase B 不重复它。

**Phase B — 明确正式上线步骤（向用户叙述）。** 验证小部件已部署到网站（LWR + Aura）——放置已经在检查点 3 Step C.5 通过 `service-digital-engagement-messaging-site-integrate` 完成；如果验证失败，请重新运行注入。然后： (a) 确认**升级流程**已连接（在检查点 3 通过 Phase 3 配置——验证，不要重新连接）；(b) **在 Setup → Embedded Service Deployments 中发布嵌入式服务部署**；然后提供一起测试。如果未发布的部署会静默地发送一个无法工作的代码块。

## 规则/约束

## 长列表呈现规则

`AskUserQuestion` 限制为 4 个选项。对于用户选择**一个**的发现项目列表（站点、渠道、队列、ADL）——**1–6 个项目**——每页分页 3 个，"显示更多 (N 剩余)" 作为选项 4，最后一页仅显示固定选项（创建新的等）。**7+ 个项目**——以纯文本列出名称，让用户键入他们的选择，不区分大小写，确认后再继续。

**例外——多选列表（例如，检查点 3 的渠道类型选择器）永远不会分页。** 分页假设是单选。对于任何多选列表，一旦选项超过 4 个，直接跳转到纯文本列表和类型模式，无论计数如何——参见 `assets/help-agent-spec.md` §4.3 步骤 1。

| 规则 | 理由 |
|---|---|
| 永远不要一次性完成设置 | 它是一个引导式对话；在每个检查点等待用户输入 |
| 永远不要跳过或重新排序就绪步骤 | 权限集在数据云启用之前不存在——你会看到 `PermissionSet not found: GenieUserEnhancedSecurity` |
| 永远不要在检查点 4 Phase A 时 ADL 检索为空 | 发送一个无声损坏的代理 |
| 永远不要硬编码站点名称或 URL 路径前缀 | 正确的目标 LWR 站点取决于客户的组织——首先查询，然后决定 |
| 永远不要将 ESW 前缀的站点作为小部件部署目标 | `ESW_*` 站点是内部 ESD 端点脚手架——在呈现站点选项给用户之前，在后处理中过滤掉它们 |
| 通过 Connect API 创建嵌入式服务部署作为 V2，永远不要裸露元数据部署——并且通过 `experience_messaging:embeddedMessaging` LWR 组件嵌入 V2 ESD | 元数据 API 默认为遗留 V1 (`WebV1`, *"Web (v1)"* 在 Setup) 会破坏增强型 Web Chat；通过 Connect API 在 v67.0+ 创建，`clientVersion: WebV2`。客户小部件通过键为 `deploymentName` 的 LWR 组件挂载。完整的六个属性形状、工具 API 补丁路径和访客浏览器验证在 `references/channel-web-chat.md` |
| 始终为 Help Agent 创建一个专用的 ADL——永远不要连接到标准的 `All_Records_and_Fields_Default` 库 | 在试用或预加载样本数据组织中，标准库卡在 `NOT_SCHEDULED` 中，永远不会索引；将代理连接到它会在运行时返回空的 `knowledgeSummary` 考虑到没有明显的错误。在检查点 2 中创建 `Help_Agent_Knowledge` 并等待 `indexingStatus ∈ {COMPLETED, READY, SUCCESS}` 才能连接 |
| 永远不要在检查点 4 时不发布嵌入式服务部署并激活渠道 | 两者都是小部件服务所必需的。如果 ESD 通过 Connect API `deployment/setup` 调用创建，则它已经发布——验证 *"Published on:"* 是否盖章，标题没有 `(v1)` 后缀 |
| Web Chat、Help Portal 和 Voice 有专门的分支；任何其他现有渠道类型（WhatsApp、SMS、Facebook、Apple Business Chat、Line、Email-to-Case、自定义）通过 `service-agentforce-channel-configure` 通用连接 | 发现（§4.3 步骤 1）必须显示每个渠道类型——当存在其他渠道时，仅提供三个专用分支是此检查点保护的错误。对于 Web Chat，始终运行部署后断言（重新检索 MessagingChannel，断言 `embeddedConfig.authMode`；默认 `UnAuth`) — 一个错误的选项会静默地发送一个无法渲染的代码块。报告 `authMode` 作为裸值 (`authMode: UnAuth`)；不要叙述。永远不要发出 `esw.min.js` / Live Agent V1 小片段 |
