# service-agentforce-channel-configure: 将Agentforce代理连接到渠道

在现有渠道和现有Agentforce代理之间添加入站路由。代理从渠道接收工作项；当代理不可用时，备用队列处理溢出。

这项技能是通用的——它适用于任何Agentforce代理，而不仅仅是Help Agent模板。

## 范围

**在范围内：**
- 解决或创建具有正确`QueueSobject` SobjectType的备用队列
- 分支A（增强聊天 / 增强消息）：在现有MessagingChannel上部署`sessionHandlerType=AgentforceServiceAgent` + `sessionHandlerQueue`，然后通过Data API PATCH绑定`SessionHandlerId`
- 分支B（语音）：假设电话号码和`PstnVoice` MessagingChannel已经存在（由调用者配置，例如`service-helpagent-coordinate`），然后创建一个入站RoutingFlow（`routingType: Copilot`）将流量路由到代理，并将队列作为备用
- 分支C（邮件到案例）：通过直接案例所有者分配或Omni-Channel RoutingFlow进行入站路由，并部署`BotEmailDefinition`（邮件配置），将其链接到服务邮件并绑定到路由地址
- 可选的出站升级：将验证的代理到人工手交合同委托给`service-agentforce-human-escalation-configure`

**超出范围：**
- 创建代理——使用`agentforce-generate`或`service-helpagent-coordinate`
- 创建MessagingChannel——使用`service-digital-engagement-channel-configure`
- 创建嵌入式服务部署——使用`service-digital-engagement-deployment-configure`
- 创建语音或邮件到案例渠道基础设施

---

## 必须的输入

- **代理`DeveloperName`**和**代理标签**（`MasterLabel`）——必须是现有、活跃的代理
- **渠道类型**——之一：增强聊天、增强消息（第三方）、语音、邮件到案例
- **渠道标识符**——MessagingChannel `DeveloperName`（分支A），或渠道名称/上下文（分支B/C）
- **目标组织别名**

---

## 工作流程

步骤是按顺序执行的。在进行下一步之前，请先阅读`references/channel-types.md`以确认路由分支。

### 阶段 0 — 生产写保护（强制，任何写操作之前）

这项技能执行**元数据/数据写操作**（MessagingChannel编辑、RoutingFlow部署、代理重新发布）。在进行任何写操作之前，对目标组织进行分类并拒绝真实生产：

```bash
sf data query --target-org $ORG --json \
  --query "SELECT Id, IsSandbox, TrialExpirationDate, OrganizationType FROM Organization LIMIT 1"
```

- `safe_to_write`仅在`IsSandbox=true`时为**true**，或者`TrialExpirationDate`非空（试用/CDO），或者`OrganizationType`为`Developer Edition` / `Base Edition`。
- 如果`safe_to_write`为false，**停止**——明确说明这是一个真实的生产客户组织，不会应用升级/渠道连接。不要进行任何写操作。
- 如果`safe_to_write`为true，显示写计划（哪些MessagingChannel/RoutingFlow/代理将更改），并在继续之前获得用户对目标组织的明确确认。

永远不要绕过这个关卡——在此处错误的 生产写操作会重新路由实时客户流量。

### 阶段 1 — 验证代理并解决队列

1. **确认代理存在并具有活跃版本：**
   ```bash
   # 获取定义
   sf data query --target-org $ORG --json \
     --query "SELECT Id, DeveloperName, MasterLabel FROM BotDefinition WHERE DeveloperName='{AGENT_DEVELOPER_NAME}'"

   # 检查活跃版本
   sf data query --target-org $ORG --json \
     --query "SELECT Id, Status FROM BotVersion WHERE BotDefinitionId='{BOT_DEFINITION_ID}' AND Status='Active' LIMIT 1"
   ```
   如果定义未找到或没有版本具有`Status = Active`，请停止并显示明确消息。

   > **分支A的注意事项——一个活跃的BotVersion是必要的，但不足以绑定作为`sessionHandlerAsa`。** 平台只接受作为*可部署的Agentforce Service Agent*（通常是`ExternalCopilot`）配置/连接的代理。绑定一个仅仅是活跃的代理会导致Phase 2部署失败，错误信息为`Only active Agentforce Service Agents are supported for a Messaging Channel`。在进行写操作之前，确认可绑定性：如果组织上已经使用`sessionHandlerType=AgentforceServiceAgent`的MessagingChannel，请检索它（`sf project retrieve start --metadata "MessagingChannel:{EXISTING}" --target-org $ORG`）并读取其`<sessionHandlerAsa>`——该集合是组织可证明可绑定的ASAs。如果所选代理不是已配置的ASA且没有可绑定的ASA，请停止并报告`BLOCKED`：*提供一个已配置为Agentforce Service Agent的代理。*

2. **解决备用队列和路由配置**——遵循`references/queue-resolution.md`：
   - 根据渠道类型确定SobjectType（见`references/channel-types.md`）
   - 查询现有兼容的队列；通过`AskUserQuestion`呈现或创建新队列
   - 查询现有的`QueueRoutingConfig`；如果不存在，则创建具有正确容量百分比的配置
   - 捕获`QUEUE_DEVELOPER_NAME`、`QUEUE_NAME`和`QUEUE_ID`

---

### 阶段 2 — 连接入站路由

#### 实时流量警告关卡（在任何分支之前运行）

在进行任何路由更改之前，检测渠道是否已经具有活跃的入站路由（分支A：`SessionHandlerType`非空；分支B/C：任何分配给服务渠道的活跃RoutingFlow）。如果是，首先检查用户的提示是否已经回答了时间选择（“不要切换” / “手动连接” / “先查看”→ 沉默处理；“立即切换” / “立即激活”→ 沉默处理）。只有当提示为沉默时，才通过`AskUserQuestion`警告并让用户选择**“立即重新路由”**或**“设置后手动连接”**——对于任何模糊或无选择响应，默认为沉默路径（永远不会进行实时重新路由）。当延迟时，设置`DEFER_INBOUND_ROUTING=true`，跳过所选分支中的渠道激活步骤，并在Phase 2结束时打印手动连接说明。

如果渠道没有现有路由，则完全跳过此关卡，并直接进行。

完整的检测查询、确切的`AskUserQuestion`块、每个分支的延迟流规则和手动连接说明：`references/live-traffic-gate.md`。

---

#### 分支A — 增强聊天 / 增强消息（第三方）

不需要RoutingFlow。仅部署具有`sessionHandlerType` + `sessionHandlerQueue`的MessagingChannel，然后通过Data API PATCH绑定机器人。`sessionHandlerAsa`在v67的Metadata API中不被接受——部署会默默地丢弃它，因此机器人绑定必须在部署后通过Data API PATCH进行。机器人必须在PATCH之前处于活跃状态（否则会显示“Only active Agentforce Service Agents are supported”）。

按顺序运行所有五个步骤。执行检索和编辑必须在**当前SFDX项目**中，以便部署从`force-app`读取编辑后的`.messagingChannel-meta.xml`；不要使用临时目录。

1. **将当前MessagingChannel元数据检索到工作目录项目：**
   ```bash
   sf project retrieve start \
     --metadata "MessagingChannel:{CHANNEL_DEVELOPER_NAME}" \
     --target-org $ORG
   ```

2. **就地编辑检索到的`.messagingChannel-meta.xml`** — 设置正好这两个字段（不要添加`<sessionHandlerAsa>`）：
   ```xml
   <sessionHandlerType>AgentforceServiceAgent</sessionHandlerType>
   <sessionHandlerQueue>{QUEUE_DEVELOPER_NAME}</sessionHandlerQueue>
   ```
   使用文件编辑工具（编辑/写入）应用此编辑，以便更改保存到检索到的文件中`force-app/main/default/messagingChannels/{CHANNEL_DEVELOPER_NAME}.messagingChannel-meta.xml`在当前工作目录中——**不要**通过内联`sed`/`cat` heredoc将其手动编辑到临时路径中。步骤3中的部署必须读取同一磁盘文件。

3. **部署：**
   ```bash
   sf project deploy start \
     --metadata "MessagingChannel:{CHANNEL_DEVELOPER_NAME}" \
     --target-org $ORG
   ```
   如果部署失败，错误信息为`Only active Agentforce Service Agents are supported for a Messaging Channel`，则表示该代理在此组织中不是可绑定的ASA（见Phase 1的注意事项）。**不要**使用相同的代理重试——渠道将保持不变（失败的部署是原子的）。报告`BLOCKED`并附带补救措施：绑定一个已配置为Agentforce Service Agent的代理，或配置此代理，然后重新运行。

4. **通过Data API PATCH绑定机器人：**
   ```bash
   CHAN_ID=$(sf data query --target-org $ORG --json \
     --query "SELECT Id FROM MessagingChannel WHERE DeveloperName='{CHANNEL_DEVELOPER_NAME}'" \
     | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['records'][0]['Id'])")
   BOT_ID=$(sf data query --target-org $ORG --json \
     --query "SELECT Id FROM BotDefinition WHERE DeveloperName='{AGENT_DEVELOPER_NAME}'" \
     | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['records'][0]['Id'])")
   QUEUE_ID=$(sf data query --target-org $ORG --json \
     --query "SELECT Id FROM Group WHERE Type='Queue' AND DeveloperName='{QUEUE_DEVELOPER_NAME}'" \
     | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['records'][0]['Id'])")

   sf api request rest --method PATCH -o $ORG \
     "/services/data/v67.0/sobjects/MessagingChannel/${CHAN_ID}" \
     --body "{\"SessionHandlerId\":\"${BOT_ID}\",\"FallbackQueueId\":\"${QUEUE_ID}\"}"
   # 预期：HTTP 204
   ```

5. **验证：**
   ```bash
   sf data query --target-org $ORG --json \
     --query "SELECT SessionHandlerId, FallbackQueueId FROM MessagingChannel WHERE Id='${CHAN_ID}'"
   ```
   `SessionHandlerId`和`FallbackQueueId`都必须非空。

不需要代理文件更改——不需要重新发布。继续到Phase 3（可选）。

---

#### 分支B — 语音

通过带有队列作为备用的入站`Copilot` RoutingFlow连接`PstnVoice` MessagingChannel，并在重新发布代理之前添加必要的`modality voice:`块。

按顺序阅读`references/channel-branch-voice.md`。重点：

- 步骤 0 — 重用现有的`PstnVoice` MessagingChannel，或使用`service-helpagent-coordinate`技能的语音渠道引用先使用该技能配置一个；如果组织使用合作伙伴电话提供商（见`references/channel-types.md`），则中止。
- 步骤 1–3 — 使用`references/routing-flow.md`中的模板编写和部署入站RoutingFlow，验证`ActiveVersionId`非空。
- 步骤 4 — 部署一个`MessagingChannel`元数据文件，其中`sessionHandlerType=Flow`、`sessionHandlerFlow={FLOW_DEVELOPER_NAME}`、`sessionHandlerQueue={QUEUE_DEVELOPER_NAME}`。没有这个，流量永远不会执行并且会挂断。验证`SessionHandlerId`以`300`开头。
- 步骤 5 — 如果缺少平台默认的`modality voice:`块（语音ID `UgBBYS2sOqTuMpoF3BR0`，"Mark"，en_US），则将其附加到`.agent`文件中；不要询问用户。按`references/agent-wiring.md`重新发布。

继续到Phase 3（可选）。

---

#### 分支C — 邮件到案例

让用户选择直接案例所有者分配或Omni-Channel `Copilot` RoutingFlow。此分支需要API v68.0+、`connection service_email:`表面和BotEmailDefinition。

按顺序阅读`references/channel-branch-email.md`。承重陷阱（该文件中有完整说明）：

- 步骤 1 — 通过Tooling-API PATCH或`Settings:Case`的`--metadata-dir`部署绑定路由地址字段，**永远**不要使用源`--metadata Settings:Case`部署（它会读取`sourceApiVersion`并修改用户的项目）。
- 步骤 2 — 选择入站路由（`AskUserQuestion`）：**案例所有者**（`caseOwner` = 代理的bot用户）或**Omni-Channel流**（`Copilot` RoutingFlow + `routingFlow`/`fallbackQueue`）。无论哪种方式，都要解析bot用户；路由字段放在步骤4d部署中。
- 步骤 3 — 代理已经活跃，因此添加强制性的`connection service_email:`表面，通过**停用→发布→激活**（普通的发布会失败，错误信息为`couldn't find the default agent user`）。如果想要升级，也在此处批量路由。
- 步骤 4 — BotEmailDefinition：预检保存时的关卡，验证回复模板，通过`--metadata-dir`部署，然后在一个`Settings:Case`部署中绑定路由地址（`botEmailDefinition` + 步骤2路由字段 + 必要的`casePriority`）。失败时停止。

分支C完成后，一旦验证了路由地址绑定，即可继续到Phase 3。

---

### 阶段 3 — 出站升级（可选）

> **权威所有者：**完整的代理到人工升级由**`service-agentforce-human-escalation-configure`**负责。这包括升级主题、规划器耦合、人工队列、出站流、失败阈值指令、重新发布和确定性验证。

在确认入站路由后，询问用户：

> *"入站路由现在已设置——渠道将路由到[代理名称]。您是否还想配置出站升级，以便当请求时代理可以转交给人工？"*

如果同意，则委托给`service-agentforce-human-escalation-configure`。传递解析的代理、渠道类型、上下文对象和备用队列作为已知输入。不要在此处重复该技能的写或验证步骤。

---

## 规则 / 限制

| 规则 | 理由 |
|---|---|
| 在进行任何更改之前验证代理存在且为Active | 将渠道连接到不存在或非活跃的代理会导致运行时失败 |
| 如果渠道已经具有活跃的入站路由，则在不询问的情况下尊重明确的延迟/切换意图；否则通过`AskUserQuestion`警告，并在模糊或无选择响应时默认为延迟 | 重新路由会立即生效并影响实时流量——队列和RoutingFlow创建始终进行；只有激活步骤受限制，安全的默认值是非破坏性的 |
| 延迟时，在Phase 3之前打印确切的 手动连接说明 | 操作员需要知道他们准备切换时确切要运行的内容 |
| 永远不要在不检索当前元数据的情况下修改MessagingChannel | 没有检索就会丢弃现有设置 |
| 分支A：不需要RoutingFlow，不需要代理重新发布；通过元数据部署`sessionHandlerType` + `sessionHandlerQueue`，然后通过Data API PATCH绑定`SessionHandlerId` | `sessionHandlerAsa`在v67的Metadata API中不被接受——部署会默默地丢弃它，因此机器人绑定必须在部署后通过Data API PATCH进行。机器人必须在PATCH之前处于活跃状态 |
| 分支B/C：始终创建新的RoutingFlow——永远不要重用现有的组织流 | OOB平台流通常具有`ActiveVersionId: null`并且不能被引用 |
| 分支B/C：使用`routingType: Copilot`和`copilotLabel`——不是`QueueBased` | `QueueBased`直接路由到队列；`Copilot`首先路由到代理，然后队列作为备用 |
| 队列`Id`必须查询并嵌入到RoutingFlow XML中 | `queueId`参数需要一个硬编码的18字符记录Id——不要将其留空 |
| 队列命名：`{ChannelTypeLabel} Queue` | 根据渠道类型命名，而不是代理 |
| 出站升级是可选的——永远不要因为它而阻塞入站路由完成 | 入站和出站是独立的；入站路由完成时不需要出站步骤 |
| 分支C：通过`--metadata-dir`部署BotEmailDefinition，永远不要`--metadata BotEmailDefinition:<name>` | 不在CLI的SDR注册表中，因此命名类型部署会失败；元数据格式工作 |
| 分支C：不要将带有`ServiceCustomerVerification`主题的代理连接到邮件 | 检测并停止——不要自动移除（可能对多表面代理是合法的）。见`channel-branch-email.md` Step 4a |

---

## 验证清单

### 队列
- [ ] 队列有一个`QueueSobject`记录，其`SobjectType`与渠道类型正确
- [ ] 运行用户是队列的成员（如果新创建）
- [ ] 队列有一个`QueueRoutingConfig`，其`CapacityPercentage`正确（聊天 / 语音 / 邮件为50 / 100 / 25）

### 分支A — MessagingChannel
- [ ] 部署后`SessionHandlerType = AgentforceServiceAgent`
- [ ] 机器人在进行Data API PATCH之前是活跃的
- [ ] Data API PATCH后`SessionHandlerId`非空（与机器人的`BotDefinition.Id`匹配，以`0Xx`开头）
- [ ] Data API PATCH后`FallbackQueueId`非空（与解析的队列Id匹配）

### 分支B/C — RoutingFlow
- [ ] RoutingFlow `ActiveVersionId`非空
- [ ] 流中的`routeWork`动作使用`routingType = Copilot`
- [ ] `copilotLabel`与代理的`MasterLabel`完全匹配
- [ ] `queueId`已填充（非空）

### 分支C — 邮件路由地址
- [ ] 如果新建：创建`EmailRoutingAddress`记录，具有正确的`PersonalName`和`Address`
- [ ] 如果新建：修补CaseSettings，`caseOrigin`、`saveEmailHeaders: true`、`addressType: EmailToCase`
- [ ] 如果新建：通知用户已向支持地址发送了验证邮件（非阻塞）

### 分支C — BotEmailDefinition
- [ ] 预检通过：代理是`EinsteinServiceAgent`，bot用户持有`agentforceServiceAgentUser`；活跃版本携带`ServiceEmail`表面；邮件代理上没有`ServiceCustomerVerification`主题
- [ ] 回复`EmailTemplate`是SFX、HTML、公开的，并包含`[[[GENERATED_CONTENT]]]` + `[[[LEGAL_DISCLOSURE]]]`
- [ ] Headless路径（API ≥68）：通过`--metadata-dir`部署`BotEmailDefinition`，`success: true`；`legalDisclaimer`/`signature` ≥10个字符
- [ ] 路由地址的`botEmailDefinition`子元素设置为部署组件的`fullName`
- [ ] 入站路由设置在相同的路由地址上：`caseOwner`+`caseOwnerType`或`routingFlow`+`fallbackQueue`，并带有`casePriority`存在

### 可选Phase 3 — 出站升级
- [ ] `service-agentforce-human-escalation-configure`返回`CONFIGURED`或`ALREADY-CONFIGURED`

---

## 参考文件索引

| 文件 | 何时阅读 |
|---|---|
| `references/channel-types.md` | Phase 1 — 确定SobjectType和路由分支 |
| `references/queue-resolution.md` | Phase 1 — 队列查询、创建和Id捕获 |
| `references/live-traffic-gate.md` | Phase 2 — 实时流量警告关卡的检测查询、延迟流规则和手动连接说明 |
| `references/channel-branch-voice.md` | 分支B — 完整语音入站连接：PstnVoice渠道选择、RoutingFlow、MessagingChannel分配、`modality voice:`重新发布 |
| `references/channel-branch-email.md` | 分支C — 完整邮件到案例连接：API v68.0+前提条件关卡、CaseSettings标志、EmailRoutingAddress + 读取修改写入修补、入站RoutingFlow、强制性的`connection service_email:`表面块、headless BotEmailDefinition部署、路由地址绑定 |
| `references/botemaildefinition.md` | 分支C Step 4 — BotEmailDefinition字段、保存时验证顺序、ASA模板规则、`--metadata-dir`部署配方、`ServiceEmail`表面先决条件、复合组织关卡 |
| `references/routing-flow.md` | 分支B/C — 入站RoutingFlow XML模板、部署、验证 |
| `references/agent-wiring.md` | Phase 3 (可选) — 出站升级`connection`块 |
| `assets/BotEmailDefinition.botEmailDefinition-meta.xml` | 分支C Step 4c — BotEmailDefinition源文件的起始模板 |
| `assets/mdapi-package.xml` | 分支C Step 4c — 元数据格式`package.xml`用于`--metadata-dir`部署 |
| `assets/email/unfiled$public/AgentforceForServiceEmailTemplate.email` + `.email-meta.xml` | 分支C Step 4b (备用) — 当用户没有时，一个符合ASA规范的SFX回复模板 |
| `scripts/validate-botemaildefinition.py` | 分支C Step 4c — 在部署前验证BotEmailDefinition文件 |
| `scripts/validate-emailtemplate.py` | 分支C Step 4b (备用) — 在部署前验证SFX模板 |
