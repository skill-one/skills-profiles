# 配置增强聊天通道

为 Salesforce 消息传递创建 `MessagingChannel` 元数据 XML，用于 In-App 和 Web (MIAW) 的 Salesforce 消息传递。此技能将创建一个完全配置的增强聊天通道，包括路由、用户验证、聊天前操作和自动回复设置，准备好用于元数据 API 部署。

## 范围

- **在范围内**：创建具有 Omni-Channel Flow 路由、Omni-Channel 队列路由或 Agentforce 服务代理 (ASA) 路由的 `MessagingChannel` 元数据；启用用户验证；配置所有通道设置（聊天前表单、自动回复、同意关键字、文件附件、自定义参数）
- **超出范围**：创建引用的 Omni-Channel Flow/队列定义（使用 `automation-flow-generate`）、创建嵌入式服务部署（单独的元数据类型——使用 `service-digital-engagement-deployment-configure`）、为消息传递创建权限集（使用 `platform-permission-set-generate`）、配置嵌入式服务代码片段

---

## 澄清问题

在生成之前，如果尚未明确，请向用户询问：

- 通道名称/标签是什么？（用于 `masterLabel` 和文件名）
- 路由类型是什么？（Omni-Channel Flow、Omni-Channel Queue、用户或 Agentforce 服务代理）
- 路由目标是什么？（Flow API 名称、队列开发者名称、用户 ID 或 ASA 机器人名称）
- 对于 Flow、User 或 ASA 路由：回退队列名称是什么？
- 是否启用用户验证？（此技能默认为 `true`）
- 是否需要聊天前表单字段？如果是，哪些字段和类型？

---

## 必需输入

在继续之前收集或推断：

- **通道名称**：用于 `masterLabel` 和文件名（`<Name>.messagingChannel-meta.xml`）
- **路由类型**：`Queue`、`Flow`、`User` 或 `AgentforceServiceAgent` 之一
- **路由目标**：队列、Flow、用户或 ASA 机器人的开发者名称
- **回退队列**（Flow、User 和 ASA）：升级用的回退队列的开发者名称
- **用户验证**：是否需要基于 JWT 的身份验证（默认：`true`）

默认值（除非指定）：
- `messagingChannelType`：`EmbeddedMessaging`
- `authMode`：`Auth`
- `chatAbandonmentTimeout`：`5`（分钟）
- `endUserIdleTimeOut`：`5`（分钟）
- `isAttachmentUploadEnabled`：`true`
- `maxFileSize`：`5`（MB）
- `allowedFileTypes`：`bmp,csv,doc,docx,gif,jpg,pdf,png,tiff,txt,xls,xml`
- `anonymousUserJwtExpirationTime`：`360`（分钟，用于 UnAuth，范围 60-4320）
- `verifiedUserJwtExpirationTime`：`60`（分钟，用于 Auth，范围 60-240）
- `isAbandonedChatsEnabled`：`false`
- `isSaveTranscriptEnabled`：`false`
- `isFallbackMessageEnabled`：`false`
- `isEstimatedWaitTimeEnabled`：`false`
- `isFileAttachmentExtUnrestricted`：`false`
- `isQueuePositionEnabled`：`false`
- `isSynchronousChatEnabled`：`false`
- `isVoiceModeEnabled`：`false`

---

## 工作流

所有步骤都是按顺序执行的。不要跳过或重新排序。

### 第一阶段——收集上下文

1. **验证组织 API 版本** — 运行 `scripts/check-api-version.sh 67.0 <org-alias>` 并报告它返回的任何错误。如果脚本失败，请在元数据输出文件夹中生成 `sfdx-project.json`，其中 `"sourceApiVersion"` 设置为 `"67.0"`。

2. **收集输入** — 根据上述澄清问题，从用户确认通道标签、路由类型、路由目标和验证设置。

3. **确定文件名** — 运行 `scripts/normalize-channel-name.sh "<LABEL>"` 并显示它返回的任何错误。

4. **验证路由目标是否存在** — 查询组织以确认引用的路由目标是否存在：
   - 对于队列：`sf data query --query "SELECT Id, DeveloperName FROM Group WHERE Type='Queue' AND DeveloperName='<QUEUE_NAME>'" --target-org <org-alias>`
   - 对于 Flow：`sf data query --query "SELECT Id, ApiName FROM FlowDefinitionView WHERE ApiName='<FLOW_NAME>' AND IsActive=true" --target-org <org-alias>`
   - 对于用户：`sf data query --query "SELECT Id, Username FROM User WHERE Id='<USER_ID>' AND IsActive=true" --target-org <org-alias>`
   - 对于 ASA：`sf data query --query "SELECT Id, DeveloperName FROM BotDefinition WHERE DeveloperName='<BOT_NAME>'" --target-org <org-alias>`
   - 还需验证回退队列是否存在（Flow、User 和 ASA 路由所需）

   如果任何目标未找到，请告知用户并询问是否要创建它。如果用户确认：
   - 对于队列：生成一个 `.queue-meta.xml`，其中 `queueSobject` 类型为 `MessagingSession`，并在通道之前部署它。**没有 `QueueRoutingConfig` 的新队列无法用于路由——针对没有 `QueueRoutingConfig` 的队列部署的通道在会话开始时失败，显示 "Agents are not available. Try again later"，即使通道本身部署和激活正常。** 队列部署后立即，通过遵循 `service-agentforce-channel-configure` 的 `references/queue-resolution.md` 第 4 步来解析或创建其路由配置。不要将其推迟到后续技能调用，因为这是新创建的队列可能唯一被触及的地方。
   - 对于 Flow/User/ASA：告知用户必须单独创建 Flow、用户或机器人（此技能的范围之外）

5. **阅读通道设置参考** — 加载 `references/channel_settings.md` 以了解所有可用配置选项及其有效值。

### 第二阶段——生成元数据

6. **读取元数据模板** — 加载 `assets/messaging_channel_template.xml` 作为起始结构。

7. **应用路由配置** — 设置 `sessionHandlerType` 和相应的处理字段：

   | 路由类型       | `sessionHandlerType` | 必填字段         |
   |---------------|---------------------|----------------|
   | Omni-Channel Queue | `Queue` | `sessionHandlerQueue` |
   | Omni-Channel Flow | `Flow` | `sessionHandlerFlow` + `sessionHandlerQueue`（回退） |
   | User          | `User` | `sessionHandlerUser` + `sessionHandlerQueue`（回退） |
   | Agentforce Service Agent | `AgentforceServiceAgent` | `sessionHandlerQueue`（回退） + `sessionHandlerAsa`（机器人开发者名称——必需，见 v67 注释） |

   > **v67 注释——`<sessionHandlerAsa>` 在 XML 中是必需的，而不是被拒绝。** 在 v67.0 组织上确认：省略 `<sessionHandlerAsa>` 会导致部署失败，错误信息为 "Missing required Agentforce Service Agent." 包含它并自动绑定 `SessionHandlerId`——不需要部署后的 Data API PATCH。
   > 1. **在通道创建之前验证机器人处于活动状态。** 元数据 API 拒绝绑定，错误信息为 "Only active Agentforce Service Agents are supported." 首先运行 `sf agent activate -o <org> --api-name <BotDevName>` 并确认 `BotVersion.Status = Active`。
   > 2. 部署 XML，其中 `<sessionHandlerType>` 设置为 `AgentforceServiceAgent`，`<sessionHandlerQueue>`（回退），以及 `<sessionHandlerAsa>{BotDevName}</sessionHandlerAsa>`。
   > 3. 验证：`sf data query -o <org> -q "SELECT SessionHandlerId, FallbackQueueId FROM MessagingChannel WHERE DeveloperName='<ChannelDevName>'" --json` — 两者都必须在部署后非空，无需单独的 PATCH 步骤。

8. **应用用户验证** — 如果启用，将 `embeddedConfig.authMode` 设置为 `Auth` 并包含 `<messagingAuthorizations>`。如果未启用，将 `embeddedConfig.authMode` 设置为 `UnAuth` 并省略 `<messagingAuthorizations>`。

9. **配置嵌入式设置** — 用以下内容填充 `<embeddedConfig>`：
   - `allowedFileTypes` — 用逗号分隔的文件扩展名（无空格）
   - `anonymousUserJwtExpirationTime` — JWT 过期时间（分钟，UnAuth 所需）
   - `verifiedUserJwtExpirationTime` — JWT 过期时间（分钟，Auth 所需）
   - `chatAbandonmentTimeout` — 清理空闲对话的分钟数
   - `isAbandonedChatsEnabled` — 启用空闲聊天检测
   - `isAttachmentUploadEnabled` — 文件上传支持
   - `isEstimatedWaitTimeEnabled` — 显示预计等待时间
   - `isFallbackMessageEnabled` — 代理不可用时回退
   - `isFileAttachmentExtUnrestricted` — 允许任何文件扩展名
   - `isSaveTranscriptEnabled` — 保存对话记录
   - `maxFileSize` — 附件最大大小（MB）

10. **配置消息传递关键字** — 生成 `<messagingKeywords>` 元素：
    - `OptOut` 类型，包含单独的 `<keyword>` 元素：cancel、end、quit、stop、stopall、unsubscribe
    - `Help` 类型，包含 `<keyword>`：help

11. **应用标准参数** — 如果用户需要标准聊天前字段，生成带有 `parameterType` 的 `<standardParameters>` 元素。如果通道使用基于 Flow 的路由，并且用户指定了 Flow 变量映射，请包含 `<actionParameterMappings>`，使用 `actionParameterName` 将每个参数映射到 Flow 输入变量。

12. **应用自定义参数** — 如果用户需要聊天前数据收集，生成带有 `name`、`masterLabel`、`parameterDataType`、`externalParameterName` 和 `maxLength` 的 `<customParameters>` 元素。如果通道使用基于 Flow 的路由，并且用户指定了 Flow 变量映射，请包含 `<actionParameterMappings>`，使用 `actionParameterName` 将每个参数映射到 Flow 输入变量。

13. **生成文件** — 按照模板结构生成 `.messagingChannel-meta.xml` 文件。放置在用户指定的路径，或默认为项目的元数据源路径下的 `messagingChannels/`。

### 第三阶段——部署和激活

14. **部署通道** — 将生成的 `.messagingChannel-meta.xml` 文件部署到目标组织：
    ```bash
    sf project deploy start --source-dir <path-to-messagingChannels-folder> --target-org <org-alias>
    ```

15a. **仅 ASA 路由——验证绑定是否成功。** 对于队列、Flow 和用户路由类型，跳过此步骤。因为 `<sessionHandlerAsa>` 包含在部署的 XML 中（步骤 7），部署本身绑定 `SessionHandlerId`——不需要单独的 Data API PATCH。

    ```bash
    sf data query -o <org> --json \
      -q "SELECT SessionHandlerId, FallbackQueueId FROM MessagingChannel WHERE DeveloperName='<CHANNEL_DEV_NAME>'"
    ```

    `SessionHandlerId` 和 `FallbackQueueId` 都必须非空。如果任何一个为空，请确认 `<sessionHandlerAsa>` 和 `<sessionHandlerQueue>` 都包含在部署的 XML 中，并且部署前机器人处于活动状态。

15. **激活通道** — 部署成功后，激活消息传递通道：
    ```bash
    sf data update record --sobject MessagingChannel --where "DeveloperName='<CHANNEL_NAME>'" --values "IsActive=true" --target-org <org-alias>
    ```

### 第四阶段——验证

16. **对照检查清单** — 在展示输出之前，确认清单中的所有项目都通过。

17. **展示输出** — 向用户展示生成的文件，并总结配置的设置和确认激活状态。提供下一步操作：
    - **自动回复** — 询问用户是否要配置 `<automatedResponses>`（OptOutConfirmation、HelpResponse）。如果同意，生成带有 `autoResponseContentType: TextResponse`、`language` 和 XML 转义 `response` 文本的元素，然后重新部署。

---

## 规则/约束

| 约束               | 理由                                                         |
|-------------------|--------------------------------------------------------------|
| 文件名作为通道 API 名称 | XML 主体中没有 `channelPlatformKey` 字段                   |
| `sessionHandlerType` 必须与存在的处理字段匹配 | 设置 `Queue` 但填充 `sessionHandlerFlow` 导致部署错误       |
| Flow 路由需要 `sessionHandlerFlow` 和 `sessionHandlerQueue` | 队列是人工升级的强制回退                                     |
| 用户路由需要 `sessionHandlerUser` 和 `sessionHandlerQueue` | 用户不可用时，队列是强制回退                                 |
| ASA 路由：XML 中包含 `sessionHandlerQueue` 和 `sessionHandlerAsa` | `sessionHandlerAsa` 在 v67 中是必需的——省略它会导致部署失败，错误信息为 "Missing required Agentforce Service Agent"；部署本身绑定 `SessionHandlerId`，不需要 POST 部署的 Data API PATCH |
| 机器人必须在绑定 `SessionHandlerId` 的元数据部署前处于活动状态 | 如果机器人未激活，API 会拒绝，错误信息为 "Only active Agentforce Service Agents are supported" |
| `masterLabel` 最大 40 个字符 | 平台对通道标签的限制                                         |
| 文件名必须匹配 `^[a-zA-Z][a-zA-Z0-9_]*$` | 元数据 API 强制的 API 名称格式                               |
| `allowedFileTypes` 是用逗号分隔的字符串，无空格 | 不是嵌套列表或数组                                           |
| `keyword` 元素是单独的——每个触发词一个 | 不是用逗号分隔的列表                                         |
| `customParameters` 需要 `name`、`masterLabel`、`parameterDataType` 和 `externalParameterName` | 不完整的参数会静默失败                                       |
| 文件扩展名是 `.messagingChannel-meta.xml` | 元数据 API 使用此特定扩展名                                   |
| 不要硬编码文件路径——尊重 `sfdx-project.json` 包含目录 | 客户组织的源路径自定义                                       |
| 通道必须在部署后激活 | 通道默认为未激活状态——直到激活后消息才不会路由             |
| `isSynchronousChatEnabled` 默认为 `false`；对于 Auth 通道，只能由用户请求设置为 `true` | 平台会拒绝 "You can't enable Session-Based Chat for verified users" 对于 Auth 通道 |

---

## 注意事项

| 问题                                                         | 解决方案                                                         |
|--------------------------------------------------------------|--------------------------------------------------------------|
| 通道名称与现有通道冲突                                       | 检查组织中是否存在现有通道；文件名必须唯一                   |
| 部署时未找到队列                                             | 确保引用的队列存在，并且 `queueSobject` 类型为 `MessagingSession` |
| 通道部署和激活正常，但会话开始时小部件显示 "Agents are not available. Try again later." | 队列没有 `QueueRoutingConfig`——在部署时是静默的。检查 `SELECT QueueRoutingConfigId FROM Group WHERE Id='<QUEUE_ID>'`；如果为空，按照 `queue-resolution.md` 第 4 步解析或创建一个 |
| 部署时未找到 Omni-Channel Flow                               | 确保引用的 Flow 存在，并且在部署通道之前处于活动状态         |
| ASA 机器人引用无效                                           | 机器人必须发布并处于活动状态；使用 BotDefinition 元数据的精确开发者名称 |
| ASA 通道部署失败，错误信息为 "Missing required Agentforce Service Agent" | `<sessionHandlerAsa>{BotDevName}</sessionHandlerAsa>` 在 XML 中缺失——它在 v67 中是必需的，不是可选的 |
| ASA 通道部署成功，但部署后 `SessionHandlerId` 为空             | 部署时机器人未处于活动状态——运行 `sf agent activate`，确认 `BotVersion.Status = Active`，然后重新部署 |
| 部署时显示 "Only active Agentforce Service Agents are supported" | 机器人未激活——在部署前运行 `sf agent activate`               |
| Flow 或 ASA 路由失败，没有回退队列                           | 当 `sessionHandlerType` 为 `Flow` 或 `AgentforceServiceAgent` 时，`sessionHandlerQueue` 是必需的 |
| JWT 验证不起作用                                             | 组织必须配置连接应用程序和证书                                 |
| 未收集自定义参数                                             | 每个通道的 `name` 必须唯一；`parameterDataType` 默认为 `Text` |
| 自动回复未显示                                                 | 使用有效的 `type` 值（`OptOutConfirmation`、`HelpResponse`）；在 `response` 文本中 XML 转义特殊字符 |
| 通道部署成功，但消息未路由                                   | 通道必须在部署后激活——它默认为未激活状态                     |
| 显示 "You can't enable Session-Based Chat for verified users" | 对于 Auth 通道，将 `isSynchronousChatEnabled` 设置为 `false`——只有 UnAuth 通道才支持会话式聊天 |

---

## 验证检查清单

### 通用检查
- [ ] 文件名是否匹配 `^[a-zA-Z][a-zA-Z0-9_]*$`？
- [ ] `masterLabel` 是否 40 个字符或更少？
- [ ] `messagingChannelType` 是否设置为 `EmbeddedMessaging`？

### 路由检查
- [ ] 是否设置了一个 `sessionHandlerType` 值（`Queue`、`Flow`、`User` 或 `AgentforceServiceAgent`）？
- [ ] 对于队列路由：`sessionHandlerQueue` 是否在 XML 中？
- [ ] 对于 Flow 路由：`sessionHandlerFlow` 是否在 XML 中，并且 `sessionHandlerQueue` 作为回退？
- [ ] 对于用户路由：`sessionHandlerUser` 是否在 XML 中，并且 `sessionHandlerQueue` 作为回退？
- [ ] 对于 ASA 路由：`sessionHandlerQueue` 和 `sessionHandlerAsa` 是否都在 XML 中？
- [ ] 对于 ASA 路由：是否运行了步骤 15a？部署后 `SessionHandlerId` 和 `FallbackQueueId` 是否都非空？
- [ ] 路由目标是否引用了组织中存在的实体？

### 用户验证检查
- [ ] 如果验证启用，`embeddedConfig.authMode` 是否设置为 `Auth`？
- [ ] 如果验证禁用，`embeddedConfig.authMode` 是否设置为 `UnAuth`？

### 嵌入式配置检查
- [ ] `chatAbandonmentTimeout` 是否为正整数（分钟）？
- [ ] `allowedFileTypes` 是否为用逗号分隔的字符串，无空格？
- [ ] `maxFileSize` 是否为 1-5 MB 的值？
- [ ] 如果 UnAuth，是否设置了 `anonymousUserJwtExpirationTime`（默认 360，范围 60-4320）？
- [ ] 如果 Auth，是否设置了 `verifiedUserJwtExpirationTime`（默认 60，范围 60-240）？

### 自动回复检查（仅当用户请求时）
- [ ] 所有 `type` 值是否使用有效的 ID（`OptOutConfirmation`、`HelpResponse`）？
- [ ] `response` 文本中的特殊字符是否 XML 转义？

### 关键字检查
- [ ] 是否至少定义了 `OptOut` 关键字类型？
- [ ] 关键字是否是单独的 `<keyword>` 元素（不是用逗号分隔的）？
- [ ] 每个关键字块是否设置了 `language`？

### 激活检查
- [ ] 是否成功部署了通道？
- [ ] 部署后通道是否激活（`IsActive=true`）？

---

## 输出预期

交付物：
- **消息传递通道元数据**：`<source-path>/messagingChannels/<ChannelName>.messagingChannel-meta.xml`

文件结构遵循 `assets/messaging_channel_template.xml` 中的模板。

---

## 跨技能集成

| 需要               | 委托给                                                         |
|-------------------|--------------------------------------------------------------|
| 创建用于路由的 Omni-Channel Flow | `automation-flow-generate` 技能                             |
| 为消息传递代理创建权限集     | `platform-permission-set-generate` 技能                     |
| 创建嵌入式服务部署         | `service-digital-engagement-deployment-configure` 技能       |

---

## 参考文件索引

| 文件                          | 何时阅读                                                         |
|-----------------------------|--------------------------------------------------------------|
| `assets/messaging_channel_template.xml` | 在生成之前——用作起始结构                                       |
| `references/channel_settings.md` | 配置通道选项（超出默认值）时                                       |
| `scripts/check-api-version.sh`   | 第一阶段——验证组织 API 版本是否满足传递的最小值（67.0）         |
| `scripts/normalize-channel-name.sh` | 第一阶段——从通道标签派生文件 API 名称                           |
| `examples/omni_flow_channel.xml`  | 验证 Omni-Channel Flow 路由的输出                               |
| `examples/omni_queue_channel.xml`  | 验证 Omni-Channel Queue 路由的输出                               |
| `examples/asa_agent_channel.xml`  | 验证 Agentforce Service Agent 路由的输出                         |
