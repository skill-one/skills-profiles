---
name: service-digital-engagement-channel-configure
description: 配置和部署增强型聊天消息通道，用于应用内和网页消息（MIAW）。当用户需要创建、部署并激活一个通过全渠道流程（Omni-Channel Flow）、全渠道队列（Omni-Channel Queue）、用户或代理服务（Agentforce Service Agent）路由配置的消息通道时使用。通过元数据API生成消息通道元数据，将其部署到目标组织，并通过用户验证、预聊天表单、自动回复、同意设置以及所有可自定义的通道选项来激活通道。当用户提及消息通道、MIAW、增强型聊天、应用内消息、网页消息设置或引用.messagingChannel-meta.xml文件时触发。当用户正在配置传统Live Agent聊天、无消息功能的嵌入式服务部署或无消息通道的标准全渠道路由规则时不触发。
---

# 配置增强聊天通道

为 Salesforce 消息传递创建 `MessagingChannel` 元数据 XML，用于 In-App 和 Web (MIAW)。此技能将创建一个完全配置的增强聊天通道，包括路由、用户验证、聊天前设置和自动回复设置，准备好进行 Metadata API 部署。

## 范围

- **在范围内**：创建具有 Omni-Channel Flow 路由、Omni-Channel 队列路由或 Agentforce Service Agent (ASA) 路由的 `MessagingChannel` 元数据；启用用户验证；配置所有通道设置（聊天前表单、自动回复、同意关键字、文件附件、自定义参数）
- **超出范围**：创建引用的 Omni-Channel Flow/队列定义（使用 `automation-flow-generate`）、创建嵌入式服务部署（单独的元数据类型 — 使用 `service-digital-engagement-deployment-configure`）、为消息创建权限集（使用 `platform-permission-set-generate`）、配置嵌入式服务代码片段

---

## 澄清问题

在生成之前，如果尚未明确，请向用户询问：

- 通道名称/标签是什么？（用于 `masterLabel` 和文件名）
- 路由类型是什么？（Omni-Channel Flow、Omni-Channel Queue、用户或 Agentforce Service Agent）
- 路由目标是什么？（Flow API 名称、队列开发者名称、用户 ID 或 ASA 机器人名称）
- 对于 Flow、用户或 ASA 路由：回退队列名称是什么？
- 是否启用用户验证？（此技能默认为 `true`）
- 是否需要聊天前表单字段？如果是，哪些字段和类型？

---

## 必须输入

在继续之前收集或推断：

- **通道名称**：用于 `masterLabel` 和文件名（`<Name>.messagingChannel-meta.xml`）
- **路由类型**：`Queue`、`Flow`、`User` 或 `AgentforceServiceAgent` 之一
- **路由目标**：队列、Flow、用户或 ASA 机器人的开发者名称
- **回退队列**（Flow、用户和 ASA）：升级用的回退队列的开发者名称
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

### 第一阶段 — 收集上下文

1. **验证组织 API 版本** — 运行 `scripts/check-api-version.sh 67.0 <org-alias>` 并报告它返回的任何错误。如果脚本失败，请在元数据输出文件夹中生成 `sfdx-project.json`，其中 `"sourceApiVersion"` 设置为 `"67.0"`。

2. **收集输入** — 根据上述澄清问题，从用户确认通道标签、路由类型、路由目标和验证设置。

3. **确定文件名** — 运行 `scripts/normalize-channel-name.sh "<LABEL>"` 并显示它返回的任何错误。

4. **验证路由目标是否存在** — 查询组织以确认引用的路由目标是否存在：
   - 对于队列：`sf data query --query "SELECT Id, DeveloperName FROM Group WHERE Type='Queue' AND DeveloperName='<QUEUE_NAME>'" --target-org <org-alias>`
   - 对于 Flow：`sf data query --query "SELECT Id, ApiName FROM FlowDefinitionView WHERE ApiName='<FLOW_NAME>' AND IsActive=true" --target-org <org-alias>`
   - 对于用户：`sf data query --query "SELECT Id, Username FROM User WHERE Id='<USER_ID>' AND IsActive=true" --target-org <org-alias>`
   - 对于 ASA：`sf data query --query "SELECT Id, DeveloperName FROM BotDefinition WHERE DeveloperName='<BOT_NAME>'" --target-org <org-alias>`
   - 还需验证回退队列是否存在（Flow、用户和 ASA 路由需要）

   如果任何目标未找到，请通知用户并询问是否要创建它。如果用户确认：
   - 对于队列：生成 `.queue-meta.xml`，将 `MessagingSession` 作为 `queueSobject` 类型，并在通道部署之前部署它。**没有 `QueueRoutingConfig` 的新队列无法用于路由 — 部署针对没有 `QueueRoutingConfig` 的队列的通道会在会话开始时失败，显示 "Agents are not available. Try again later."，即使通道本身部署和激活正常。** 队列部署后立即，通过 `service-agentforce-channel-configure` 的 `references/queue-resolution.md` 第 4 步解决或创建其路由配置 — 不要将其推迟到后续技能调用，因为这是新创建的队列可能唯一被触达的地方。
   - 对于 Flow/User/ASA：通知用户必须单独创建 Flow、用户或机器人（此技能的范围之外）

5. **阅读通道设置参考** — 加载 `references/channel_settings.md` 以了解所有可用的配置选项及其有效值。

### 第二阶段 — 生成元数据

6. **读取元数据模板** — 加载 `assets/messaging_channel_template.xml` 作为起始结构。

7. **应用路由配置** — 设置 `sessionHandlerType` 和相应的处理字段：

   | 路由类型       | `sessionHandlerType` | 必填字段         |
   |---------------|---------------------|----------------|
   | Omni-Channel Queue | `Queue` | `sessionHandlerQueue` |
   | Omni-Channel Flow | `Flow` | `sessionHandlerFlow` + `sessionHandlerQueue`（回退） |
   | User          | `User` | `sessionHandlerUser` + `sessionHandlerQueue`（回退） |
   | Agentforce Service Agent | `AgentforceServiceAgent` | `sessionHandlerQueue`（回退） + `sessionHandlerAsa`（机器人开发者名称 — 需要，见 v67 注意） |

   > **v67 注意 — `<sessionHandlerAsa>` 在 XML 中是必需的，而不是被拒绝。** 在 v67.0 组织上确认：省略 `<sessionHandlerAsa>` 会导致部署失败，显示 "Missing required Agentforce Service Agent。" 包含它，部署会自动绑定 `SessionHandlerId` — 无需部署后的 Data API PATCH。
   > 1. **在通道创建之前验证机器人处于活动状态。** Metadata API 拒绝绑定，显示 "Only active Agentforce Service Agents are supported." 运行 `sf agent activate -o <org> --api-name <BotDevName>` 并确认 `BotVersion.Status = Active`。
   > 2. 部署 XML，包含 `<sessionHandlerType>AgentforceServiceAgent</sessionHandlerType>`、`<sessionHandlerQueue>`（回退）和 `<sessionHandlerAsa>{BotDevName}</sessionHandlerAsa>`。
   > 3. 验证：`sf data query -o <org> -q "SELECT SessionHandlerId, FallbackQueueId FROM MessagingChannel WHERE DeveloperName='<ChannelDevName>'" --json` — 两者在部署后都必须非空，无需单独的 PATCH 步骤。

8. **应用用户验证** — 如果启用，将 `embeddedConfig.authMode` 设置为 `Auth` 并包含 `<messagingAuthorizations>`。如果未启用，将 `embeddedConfig.authMode` 设置为 `UnAuth` 并省略 `<messagingAuthorizations>`。

9. **配置嵌入式设置** — 用以下内容填充 `<embeddedConfig>`：
   - `allowedFileTypes` — 以逗号分隔的文件扩展名（无空格）
   - `anonymousUserJwtExpirationTime` — JWT 过期时间（分钟，用于 UnAuth，必需，范围 60-4320）
   - `verifiedUserJwtExpirationTime` — JWT 过期时间（分钟，用于 Auth，必需，范围 60-240）
   - `chatAbandonmentTimeout` — 清理未参与对话前的分钟数
   - `isAbandonedChatsEnabled` — 启用未参与对话检测
   - `isAttachmentUploadEnabled` — 文件上传支持
   - `isEstimatedWaitTimeEnabled` — 显示预计等待时间
   - `isFallbackMessageEnabled` — 代理不可用时显示回退消息
   - `isFileAttachmentExtUnrestricted` — 允许任何文件扩展名
   - `isSaveTranscriptEnabled` — 保存对话记录
   - `maxFileSize` — 最大附件大小（MB）

10. **配置消息关键字** — 生成 `<messagingKeywords>` 元素：
    - `OptOut` 类型，包含单独的 `<keyword>` 元素：cancel、end、quit、stop、stopall、unsubscribe
    - `Help` 类型，包含 `<keyword>`：help

11. **应用标准参数** — 如果用户需要标准聊天前字段，生成带有 `parameterType` 的 `<standardParameters>` 元素。如果通道使用基于 Flow 的路由，并且用户指定了 Flow 变量映射，请包含 `<actionParameterMappings>`，用 `actionParameterName` 将每个参数映射到 Flow 输入变量。

12. **应用自定义参数** — 如果用户需要聊天前数据收集，生成带有 `name`、`masterLabel`、`parameterDataType`、`externalParameterName` 和 `maxLength` 的 `<customParameters>` 元素。如果通道使用基于 Flow 的路由，并且用户指定了 Flow 变量映射，请包含 `<actionParameterMappings>`，用 `actionParameterName` 将每个参数映射到 Flow 输入变量。

13. **生成文件** — 按照模板结构生成 `.messagingChannel-meta.xml` 文件。放置在用户指定的路径，或默认为项目的元数据源路径下的 `messagingChannels/`。

### 第三阶段 — 部署和激活

14. **部署通道** — 将生成的 `.messagingChannel-meta.xml` 文件部署到目标组织：
    ```bash
    sf project deploy start --source-dir <path-to-messagingChannels-folder> --target-org <org-alias>
    ```

15a. **仅 ASA 路由 — 验证绑定是否成功。** 对于 Queue、Flow 和 User 路由类型，跳过此步骤。由于部署的 XML 中包含 `<sessionHandlerAsa>`（步骤 7），部署本身会绑定 `SessionHandlerId` — 无需单独的 Data API PATCH。

    ```bash
    sf data query -o <org> --json \
      -q "SELECT SessionHandlerId, FallbackQueueId FROM MessagingChannel WHERE DeveloperName='<CHANNEL_DEV_NAME>'"
    ```

    `SessionHandlerId` 和 `FallbackQueueId` 都必须非空。如果任何一个为空，请确认部署的 XML 中同时存在 `<sessionHandlerAsa>` 和 `<sessionHandlerQueue>`，并且部署前机器人处于活动状态。

15. **激活通道** — 部署成功后，激活消息通道：
    ```bash
    sf data update record --sobject MessagingChannel --where "DeveloperName='<CHANNEL_NAME>'" --values "IsActive=true" --target-org <org-alias>
    ```

### 第四阶段 — 验证

16. **对照检查清单验证** — 在展示输出之前，确认清单中的所有项目都通过。

17. **展示输出** — 向用户展示生成的文件，并总结配置的设置和确认激活状态。提供下一步操作：
    - **自动回复** — 询问用户是否要配置 `<automatedResponses>`（OptOutConfirmation、HelpResponse）。如果同意，生成带有 `autoResponseContentType: TextResponse`、`language` 和 XML 转义 `response` 文本的元素，然后重新部署。

---

## 规则 / 限制

| 限制       | 理由 |
|-----------|-----------|
| 文件名作为通道 API 名称 | XML 主体中没有 `channelPlatformKey` 字段 |
| `sessionHandlerType` 必须与存在的处理字段匹配 | 设置 `Queue` 但填充 `sessionHandlerFlow` 会导致部署错误 |
| Flow 路由需要 `sessionHandlerFlow` 和 `sessionHandlerQueue` | 队列是人工升级的强制回退 |
| 用户路由需要 `sessionHandlerUser` 和 `sessionHandlerQueue` | 用户不可用时，队列是强制回退 |
| ASA 路由：XML 中包含 `sessionHandlerQueue` 和 `sessionHandlerAsa` | `sessionHandlerAsa` 在 v67 中是必需的 — 如果省略，部署会失败，显示 "Missing required Agentforce Service Agent"；部署本身会绑定 `SessionHandlerId`，无需 POST 部署 Data API PATCH |
| 机器人必须在绑定 `SessionHandlerId` 的元数据部署前处于活动状态 | 如果机器人未激活，API 会拒绝，显示 "Only active Agentforce Service Agents are supported" |
| `masterLabel` 最大 40 个字符 | 平台对通道标签的限制 |
| 文件名必须匹配 `^[a-zA-Z][a-zA-Z0-9_]*$` | Metadata API 强制的 API 名称格式 |
| `allowedFileTypes` 是以逗号分隔的字符串，无空格 | 不是嵌套列表或数组 |
| `keyword` 元素是单个的 — 每个触发词一个 | 不是逗号分隔的列表 |
| `customParameters` 需要 `name`、`masterLabel`、`parameterDataType` 和 `externalParameterName` | 不完整的参数会静默失败 |
| 文件扩展名是 `.messagingChannel-meta.xml` | Metadata API 使用此特定扩展名 |
| 不要硬编码文件路径 — 尊重 `sfdx-project.json` 包目录 | 客户组织的源路径自定义 |
| 通道必须在部署后激活 | 通道默认为未激活状态 — 消息不会路由，直到激活 |
| `isSynchronousChatEnabled` 默认为 `false`；Auth 通道只能由用户请求设置为 `true` | 平台会拒绝 "You can't enable Session-Based Chat for verified users" for Auth 通道 |

---

## 注意事项

| 问题       | 解决方案 |
|-----------|------------|
| 通道名称与现有通道冲突 | 检查组织中是否存在现有通道；文件名必须唯一 |
| 部署时未找到队列 | 确保引用的队列存在，并将 `MessagingSession` 作为 `queueSobject` 类型 |
| 通道部署和激活正常，但会话开始时小部件显示 "Agents are not available. Try again later." | 队列没有 `QueueRoutingConfig` — 部署时是静默的。检查 `SELECT QueueRoutingConfigId FROM Group WHERE Id='<QUEUE_ID>'`；如果为空，按照 `queue-resolution.md` 第 4 步解决或创建 |
| 部署时找不到 Omni-Channel Flow | 确保引用的 Flow 存在，并且在部署通道之前处于活动状态 |
| ASA 机器人引用无效 | 机器人必须发布并处于活动状态；使用 BotDefinition 元数据的精确开发者名称 |
| ASA 通道部署失败，显示 "Missing required Agentforce Service Agent" | `<sessionHandlerAsa>{BotDevName}</sessionHandlerAsa>` 缺失于 XML — 在 v67 中是必需的，不是可选的 |
| ASA 通道部署成功，但部署后 `SessionHandlerId` 为空 | 部署时机器人未激活 — 运行 `sf agent activate`，确认 `BotVersion.Status = Active`，然后重新部署 |
| 部署时显示 "Only active Agentforce Service Agents are supported" | 机器人未激活 — 在部署前运行 `sf agent activate` |
| Flow 或 ASA 路由没有回退队列失败 | `sessionHandlerQueue` 是 `sessionHandlerType` 为 `Flow` 或 `AgentforceServiceAgent` 时必需的 |
| JWT 验证不起作用 | 组织必须配置连接应用程序和证书 |
| 未收集自定义参数 | 每个通道的 `name` 必须唯一；`parameterDataType` 默认为 `Text` |
| 自动回复未显示 | 使用确切的 `type` 值（`OptOutConfirmation`、`HelpResponse`）；XML 转义特殊字符 |
| 通道部署，但消息未路由 | 通道必须在部署后激活 — 默认为未激活 |
| 显示 "You can't enable Session-Based Chat for verified users" | 将 `isSynchronousChatEnabled` 设置为 `false` for Auth 通道 — 只有 UnAuth 通道才有效 session-based chat |

---

## 验证清单

### 通用检查
- [ ] 文件名是否匹配 `^[a-zA-Z][a-zA-Z0-9_]*$`？
- [ ] `masterLabel` 是否 40 个字符或更少？
- [ ] `messagingChannelType` 是否设置为 `EmbeddedMessaging`？

### 路由检查
- [ ] 是否设置了一个 `sessionHandlerType` 值 (`Queue`, `Flow`, `User` 或 `AgentforceServiceAgent`)？
- [ ] 对于队列路由：`sessionHandlerQueue` 是否在 XML 中？
- [ ] 对于流程路由：`sessionHandlerFlow` 是否在 XML 中，并且 `sessionHandlerQueue` 作为后备？
- [ ] 对于用户路由：`sessionHandlerUser` 是否在 XML 中，并且 `sessionHandlerQueue` 作为后备？
- [ ] 对于 ASA 路由：`sessionHandlerQueue` 和 `sessionHandlerAsa` 是否都在 XML 中？
- [ ] 对于 ASA 路由：是否运行了步骤 15a？部署后 `SessionHandlerId` 和 `FallbackQueueId` 是否非空？
- [ ] 路由目标是否引用了组织中现有的实体？

### 用户验证检查
- [ ] 如果验证已启用，`embeddedConfig.authMode` 是否设置为 `Auth`？
- [ ] 如果验证已禁用，`embeddedConfig.authMode` 是否设置为 `UnAuth`？

### 嵌入式配置检查
- [ ] `chatAbandonmentTimeout` 是否为正整数（分钟）？
- [ ] `allowedFileTypes` 是否为不带空格的逗号分隔字符串？
- [ ] `maxFileSize` 是否在 1-5 MB 之间？
- [ ] 如果是 UnAuth，`anonymousUserJwtExpirationTime` 是否已设置（默认 360，范围 60-4320）？
- [ ] 如果是 Auth，`verifiedUserJwtExpirationTime` 是否已设置（默认 60，范围 60-240）？

### 自动回复检查（仅当用户请求时）
- [ ] 所有 `type` 值是否使用有效的 ID (`OptOutConfirmation`, `HelpResponse`)？
- [ ] `response` 文本中的特殊字符是否进行了 XML 转义？

### 关键词检查
- [ ] 是否至少定义了一种 `OptOut` 关键词类型？
- [ ] 关键词是否为单独的 `<keyword>` 元素（不是逗号分隔的）？
- [ ] 每个关键词块是否设置了 `language`？

### 激活检查
- [ ] 频道是否成功部署？
- [ ] 部署后频道是否激活 (`IsActive=true`)？

---

## 输出预期

交付物：
- **消息频道元数据**：`<source-path>/messagingChannels/<ChannelName>.messagingChannel-meta.xml`

文件结构遵循 `assets/messaging_channel_template.xml` 中的模板。

---

## 跨技能集成

| 需求 | 委托给 |
|------|-------------|
| 创建用于路由的 Omni-Channel 流程 | `automation-flow-generate` 技能 |
| 创建消息代理的权限集 | `platform-permission-set-generate` 技能 |
| 创建嵌入式服务部署 | `service-digital-engagement-deployment-configure` 技能 |

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `assets/messaging_channel_template.xml` | 生成前 — 用作起始结构 |
| `references/channel_settings.md` | 配置频道选项超出默认值时 |
| `scripts/check-api-version.sh` | 第一阶段 — 验证组织 API 版本是否满足传入的最小值（67.0） |
| `scripts/normalize-channel-name.sh` | 第一阶段 — 从频道标签派生文件 API 名称 |
| `examples/omni_flow_channel.xml` | 验证 Omni-Channel 流程路由输出 |
| `examples/omni_queue_channel.xml` | 验证 Omni-Channel 队列路由输出 |
| `examples/asa_agent_channel.xml` | 验证 Agentforce Service Agent 路由输出 |
