# 配置嵌入式消息部署

配置 Salesforce 消息服务的 `EmbeddedServiceConfig` 元数据，用于 In-App 和 Web (MIAW) 的嵌入式服务。支持两种不同的工作流程：通过 Connect API 创建新部署，以及通过元数据 API 更新现有部署。

## 范围

- **在范围内**：通过 Connect API 创建新的嵌入式服务部署（API、移动、Web 类型）；通过元数据 API 更新现有部署的表单、品牌、渠道设置和功能；生成用于更新的 `EmbeddedServiceConfig` XML
- **超出范围**：创建消息渠道本身（使用 `service-digital-engagement-channel-configure`），发布部署（Connect API 后置步骤），创建体验站点（Web 类型部署的 Connect API 前置条件）

---

## 澄清问题

在生成之前，如果尚未明确，请询问用户：

- **创建或更新？** 您是创建新部署还是更新现有部署？
- **部署类型？** API（无头）、移动（原生应用）或 Web（浏览器小部件）？
- **渠道名称？** 要关联的消息渠道的 `channelPlatformKey` 是什么？
- 对于 **创建**：部署的名称应该是什么？
- 对于 **更新**：要配置哪些功能？（预聊天表单、业务时间、条款和条件、UI 开关）
- 对于 **更新（Web）**：体验站点的名称是什么？需要品牌覆盖吗？

---

## 必须输入

在进行下一步之前收集或推断：

- **操作**：`create` 或 `update`
- **部署类型**：`API`、`Mobile` 或 `Web`
- **部署名称**：用于 `masterLabel` 和 API 名称
- **渠道名称**：关联消息渠道的 `channelPlatformKey`

对于 **更新** 操作，此外：
- **站点名称**（Web 仅限）：体验站点的名称（格式 `ESW_<name>_<timestamp>`）
- **品牌名称**（可选）：引用现有的 `BrandingSet`
- **预聊天表单字段**（可选）：字段名称和必填状态
- **业务时间**（可选）：现有 `BusinessHours` 记录的名称

默认值（除非指定）：
- `isEnabled`：`true`
- `deploymentFeature`：`EmbeddedMessaging`

---

## 工作流程

所有步骤都是按顺序执行的。不要跳过或重新排序。根据操作类型进行分支。

### 第一阶段 — 收集上下文

1. **验证组织 API 版本** — 运行 `scripts/check-api-version.sh 67.0 <org-alias>` 并报告它返回的任何错误。如果脚本失败，请在元数据输出文件夹中生成 `sfdx-project.json`，其中 `"sourceApiVersion"` 设置为 `"67.0"`。

2. **确定操作** — 询问用户是否希望创建新部署或更新现有部署。

3. **收集输入** — 根据上述澄清问题收集部署名称、类型和渠道名称。

4. **读取部署设置参考** — 加载 `references/deployment_settings.md` 以了解所有可用的配置选项。

### 第二阶段 A — 创建新部署

当操作为 `create` 时，使用此路径。

5. **根据类型确定 API 方法**：

   | 部署类型 | 创建方法 | 前置条件 |
   |----------|----------|----------|
   | API | 元数据 API 部署 | 渠道必须存在 |
   | 移动 | 元数据 API 部署 | 渠道必须存在 |
   | Web | Connect API | 渠道必须存在 + 需要体验站点 |

6. **对于 API/移动类型** — 读取模板 `assets/esd_api_mobile_template.xml` 并生成 `EmbeddedServiceConfig` XML，使用：
   - `deploymentType` 设置为 `API` 或 `Mobile`
   - `deploymentFeature` 设置为 `EmbeddedMessaging`
   - 应用所有默认值

7. **对于 Web 类型** — 告知用户 Web 部署需要 Connect API 进行初始创建，因为网络和 CustomSite 之间存在循环依赖。读取 `references/connect_api_creation.md` 获取 Connect API 负载和说明。

8. **生成输出** — 生成 `.EmbeddedServiceConfig-meta.xml` 文件（用于 API/Mobile）或 Connect API 说明（用于 Web）。

9. **显示输出和下一步** — 显示生成的文件并总结已配置的内容。建议下一步：
   - **发布** 部署通过 Connect API 以使其生效：
     ```bash
     sf api request rest "/services/data/v67.0/connect/embeddedservice/embeddedserviceconfig/publish/<EMBEDDED_SERVICE_CONFIG_ID>" -X POST -o <org-alias>
     ```
     要获取 `EMBEDDED_SERVICE_CONFIG_ID`：
     ```bash
     sf data query --query "SELECT Id FROM EmbeddedServiceConfig WHERE DeveloperName = '<DEPLOYMENT_NAME>'" --target-org <org-alias>
     ```
   - **生成代码片段** 用于集成 — 见 `references/code_snippet.md`

### 第二阶段 B — 更新现有部署（元数据 API）

当操作为 `update` 时，使用此路径。

10. **检索现有部署** — 在进行更改之前，从组织中检索当前的 `EmbeddedServiceConfig` 元数据：
    ```bash
    sf project retrieve start --metadata EmbeddedServiceConfig:<DEPLOYMENT_NAME> --target-org <org-alias>
    ```
    将检索到的文件用作起始结构。如果检索不可行，则加载 `assets/esd_web_update_template.xml` 作为备用参考。

11. **应用消息渠道设置** — 配置 `<embeddedServiceMessagingChannel>`，使用：
    - `messagingChannel` — 渠道的 `channelPlatformKey`
    - `shouldShowAgentforceTagline` — Agentforce 品牌
    - `shouldShowDeliveryReceipts` — 交付收据
    - `shouldShowEmojiSelection` — 表情选择器
    - `shouldShowReadReceipts` — 阅读收据
    - `shouldShowTypingIndicators` — 打字指示器
    - `shouldStartNewLineOnEnter` — Enter 键行为
    - `isChatInvitationCustomizable` / `isInvitationEnabled` — 聊天邀请设置

12. **应用预聊天表单** — 如果用户需要收集预聊天数据，生成 `<embeddedServiceForms>`，其中包含 `<embeddedServiceFormFields>` 元素，包含 `embeddedServiceFormFieldName` 和 `isRequired`。

13. **应用品牌自定义**（Web 仅限）— 当通过 Connect API 创建部署时，会自动创建带有默认值的 BrandingSet。如果用户想要覆盖特定的品牌属性（颜色、字体、尺寸），请阅读 `references/branding_and_tooling.md` 获取 Tooling API 步骤以更新单个属性。

14. **应用邀请**（Web 仅限）— 如果用户希望小部件根据条件主动邀请访客：
    - 在 `<embeddedServiceMessagingChannel>` 中将 `isInvitationEnabled` 设置为 `true`
    - 生成可重复的 `<embdMsgChannelInvitationConditions>` 元素，包含 `sequence`、`conditionType`、`operand`、`value`，以及可选的 `customVariableName`
    - 更新 `<embeddedServiceMessagingChannel>` 中的 `formula` 字段以引用条件序列（例如，`1 AND 2`，`1 OR 2`）。每当添加或删除条件时，必须更新公式以与 `sequence` 编号保持同步
    - 见 `references/deployment_settings.md` 获取可用的条件类型和运算符

15. **应用其他设置**：
    - `isTermsAndConditionsEnabled` / `isTermsAndConditionsRequired` — 预聊天的条款和条件
    - **不要更新 `site`** — 站点名称在创建时自动生成，绝不能修改

16. **生成文件** — 在用户指定的路径生成 `.EmbeddedServiceConfig-meta.xml` 文件，或默认为项目元数据源路径中的 `EmbeddedServiceConfig/`。

17. **显示输出和下一步** — 显示生成的文件并总结已配置的内容。建议下一步：
   - **发布** 部署通过 Connect API 以使更改生效：
     ```bash
     sf api request rest "/services/data/v67.0/connect/embeddedservice/embeddedserviceconfig/publish/<EMBEDDED_SERVICE_CONFIG_ID>" -X POST -o <org-alias>
     ```
     要获取 `EMBEDDED_SERVICE_CONFIG_ID`：
     ```bash
     sf data query --query "SELECT Id FROM EmbeddedServiceConfig WHERE DeveloperName = '<DEPLOYMENT_NAME>'" --target-org <org-alias>
     ```
   - **生成代码片段** 用于集成 — 见 `references/code_snippet.md`

### 第三阶段 — 验证

18. **对照检查清单** — 确认以下检查清单中的所有项目都通过。

---

## 规则 / 限制

| 限制 | 理由 |
|------|------|
| 始终在更新前检索现有部署 | 确保保留当前设置，并仅应用预期更改 |
| `deploymentType` 必须为 `API`、`Mobile` 或 `Web` | 平台拒绝其他值 |
| 永远不要更新 Web 部署的 `site` 字段 | 站点名称在创建时自动生成，绝不能修改 |
| Web 部署不能通过元数据 API 创建 | 网络和 CustomSite 之间存在循环依赖 — 使用 Connect API |
| `embeddedServiceMessagingChannelName` 必须引用现有渠道 | 如果渠道不存在，部署将失败 |
| Web 类型更新需要 `site` 字段 | Web 小部件必须与体验站点关联 |
| Connect API 在创建部署时自动创建 BrandingSet | 要覆盖品牌属性，请使用 Tooling API — 见 `references/branding_and_tooling.md` |
| 预聊天表单字段必须引用有效的渠道自定义参数 | ChoiceList 字段需要在渠道上首先部署参数 |
| 文件扩展名为 `.EmbeddedServiceConfig-meta.xml` | 元数据 API 使用此特定扩展名 |
| 不要硬编码文件路径 — 尊重 `sfdx-project.json` 包目录 | 客户组织自定义源路径 |
| 永远不要在生成输出中包含部署/推送命令 | 此技能仅生成工件 |
| Web ESD 更新后需要 Connect API 发布 | 更改不会生效，直到发布 |

---

## 注意事项

| 问题 | 解决方案 |
|------|----------|
| Web ESD 通过元数据 API 创建失败 | Web 类型需要 Connect API 进行初始创建；仅使用元数据 API 进行更新 |
| 站点名称未找到 | 在 Web ESD 更新之前必须存在站点；格式为 `ESW_<name>_<timestamp>` |
| 品牌覆盖未应用 | 使用 Tooling API 在部署创建后更新单个 BrandingSet 属性 |
| 预聊天 ChoiceList 未显示 | ChoiceList 需要两步部署：首先创建 ChoiceList，然后分配给表单字段 |
| 更改未在小部件中显示 | Web ESD 必须通过 Connect API 在任何更新后发布 |
| `embeddedServiceFlowConfig.enabled` 错误 | 除非您确实需要嵌入式流程（而不是路由流程），否则将其设置为 `false` |
| reCAPTCHA 配置被拒绝 | reCAPTCHA 是 `@HideInWsdl` — 必须使用 Tooling API |
| 业务时间未生效 | 仅更新现有业务时间有效；创建由单独管理 |
| 部署失败，显示“缺少必需字段”或“upsert failed null” | 所有属性都是必需的：`embeddedServiceMessagingChannel` 中的布尔字段（即使默认为 `false` 也应包含所有字段），以及所有表单字段属性（`formField`、`formFieldType`、`isHidden`、`isRequired`、`displayOrder`、`messagingChannelParameterType`） |
| 标准预聊天字段未找到 | 在 `formField` 中使用 `_` 前缀表示标准字段：`_FirstName`、`_LastName`、`_Email`、`_Subject` |

---

## 验证检查清单

### 通用检查
- [ ] `deploymentType` 是否为 `API`、`Mobile` 或 `Web`？
- [ ] `masterLabel` 是否已填充且唯一？
- [ ] `messagingChannel` 是否引用现有渠道？
- [ ] `deploymentFeature` 是否设置为 `EmbeddedMessaging`？
- [ ] `isEnabled` 是否设置为 `true`？

### Web 类型检查
- [ ] `site` 是否填充了体验站点的名称？
- [ ] 如果配置了品牌，`embeddedServiceBrandingName` 是否引用了现有的 BrandingSet？
- [ ] 预聊天表单字段名称是否有效（与渠道自定义参数匹配）？
- [ ] 如果 `isInvitationEnabled` 为 `true`，`formula` 是否已填充且与 `<embdMsgChannelInvitationConditions>` 中的所有 `sequence` 编号一致？

### API/Mobile 类型检查
- [ ] `siteUrl` 是否为空（不需要站点）？
- [ ] `deploymentType` 是否正确设置为 `API` 或 `Mobile`？

### 部署后检查
- [ ] 是否提醒用户发布（Connect API）以使 Web 部署生效？
- [ ] 如果部署了消息组件，是否提醒用户激活组件（Tooling API）？

---

## 输出预期

交付物：
- **对于 API/Mobile 创建**：`<source-path>/EmbeddedServiceConfig/<DeploymentName>.EmbeddedServiceConfig-meta.xml`
- **对于 Web 创建**：Connect API 负载和说明（没有 XML 文件）
- **对于更新**：`<source-path>/EmbeddedServiceConfig/<DeploymentName>.EmbeddedServiceConfig-meta.xml`

文件结构遵循 `assets/` 中的模板。

---

## 跨技能集成

| 需要 | 委托给 |
|------|----------|
| 创建消息渠道 | `service-digital-engagement-channel-configure` 技能 |
| 创建 Omni-Channel 路由流程 | `automation-flow-generate` 技能 |
| 为代理创建权限集 | `platform-permission-set-generate` 技能 |

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|----------|
| `assets/esd_api_mobile_template.xml` | 在生成 API 或 Mobile 类型部署之前 |
| `assets/esd_web_update_template.xml` | 在生成 Web 类型更新之前 |
| `references/deployment_settings.md` | 当配置默认值之外的部署选项时 |
| `references/connect_api_creation.md` | 在创建 Web 类型部署时（需要 Connect API） |
| `references/branding_and_tooling.md` | 当用户询问品牌配置时 |
| `references/code_snippet.md` | 当用户需要网站集成的 JavaScript 嵌入代码片段时 |
| `scripts/check-api-version.sh` | 第一阶段 — 验证组织 API 版本是否满足传递的最低版本（67.0） |
| `examples/esd_api.xml` | 验证 API 类型部署的输出 |
| `examples/esd_mobile.xml` | 验证 Mobile 类型部署的输出 |
| `examples/esd_web_full.xml` | 验证完全配置的 Web 部署的输出 |
