---
name: cargo-connection
description: 将 Cargo 连接到外部系统，了解它能够做什么——验证连接器、浏览集成目录，并解决工作流节点所需的 `connectorUuid` 和 `actionSlug`。触发器："连接我的 HubSpot"、"Salesforce 是否已连接"、"您支持哪些集成"、"Cargo 能否与 <工具> 通信"、"<提供者> 有哪些操作"、"我需要连接器 UUID"、"为 设置 API 密钥"、"它又在请求凭证"、"这个连接器为什么认证失败"、"列出我的连接器"。集成：amplemarket、amplitude、attio、bigQuery、calendly、closecom、contrast、csv、customerio、dbt、emailBison、expandi、googleAds、googleSheets、heyReach、http、hubspot、hubspotMcp、instantly、instantlyV2、intercom、jira、kitt、lemlist、lgm、linkedinAds、linkedinMatchedAudience、livestorm、manus、marketo、metabase、microsoftTeams、mixpanel、netsuite、netsuiteSoap、notionMcp、octave、onesignal、outreach、pipedrive、postgresql、redshift、resend、rift、salesforce、salesforceMcp、salesloft、Sendgrid、sillage、slack、smartlead、snowflake、sql、stripe，以及 82 个更多。选择时跳过：在为 GTM 工作选择丰富提供者时——使用 cargo-gtm 及其提供者剧本。
---

# Cargo CLI — 连接

连接器和集成管理：列出连接器、发现可用集成以及管理已认证的连接器实例。

> 参考 `references/response-shapes.md` 获取完整的 JSON 响应结构。
> 参考 `references/troubleshooting.md` 获取常见错误及其解决方法。
> 参考 `references/examples/connectors.md` 获取连接器 CRUD 和发现示例。
> 参考 `references/examples/integrations.md` 获取列出可用集成和 OAuth 流程。
> 对于工作流中的第三方连接器速率限制处理和重试配置，请参考 `cargo-orchestration/references/polling.md` 和 `cargo-orchestration/references/troubleshooting.md`。原生集成没有速率限制。

## 初始化

已经登录 (`cargo-ai whoami` 返回工作区)？跳到下一节。

```bash
npm install -g @cargo-ai/cli            # 没有全局安装？为每个命令前缀 `npx @cargo-ai/cli`
cargo-ai login --email you@company.com  # 发送邮件代码，无需浏览器；首次使用时创建账户
                                        # 替代方案：--oauth (浏览器) · --token <api-token> (CI)
cargo-ai whoami                         # 在进行任何写入操作前确认活动工作区
```

每个命令都会将 JSON 打印到标准输出；失败时以非零状态退出并打印 `{"errorMessage": "..."}`。创建运行或批处理操作的是异步的 — 传递 `--wait-until-finished` 或轮询匹配的 `get`。当完整技能包安装完成后，[`../cargo/references/prerequisites.md`](../cargo/references/prerequisites.md) 会添加 CLI 版本固定、令牌作用域和管理员专用的界面。

## 关键概念

**集成**：外部服务类型（例如 HubSpot、Clearbit、Salesforce）。集成定义了可用的操作。

**连接器**：集成的已认证实例。一个集成可以有多个连接器（例如两个不同的 HubSpot 账户）。连接器是在工作流节点图中引用的对象。

## 先发现资源

**寻找操作？搜索它——不要浏览目录。** 两次关键字搜索覆盖整个界面，并且都比分页 `integration list` 或读取整个 `integration get` 负载更高效：

```bash
cargo-ai orchestration action list <query>                # 从这里开始 — 连接器 + 原生 + 工具 + 代理。
                                                          # 返回一个可运行的 action 对象（已解析的 connectorUuid）和操作的信用成本。
cargo-ai connection action search <query> --credits-only  # 仅连接器目录，但按类别过滤
                                                          # 并按“是否付费”过滤——`action list` 无法做到。
```

当你需要 *集成* 而不是操作时，使用目录命令——它的认证字段、它的提取器或你已经选择的操作的完整输入模式：

```bash
cargo-ai connection connector list                        # 所有已认证的连接器
cargo-ai connection integration list                      # 所有可用的集成类型
cargo-ai connection integration list --search "hubspot"   # 按名称搜索
cargo-ai connection integration get <slug>                # 一个集成的操作 + 输入模式
cargo-ai connection native-integration get                # 仅内置的 Cargo 操作（不是第三方）
```

> **已弃用的集成仍然会出现在目录中。** `integration list` 会以 `isDeprecated: true` 和以 `(deprecated)` 结尾的显示名称返回它们。现有的连接器仍然可以工作——弃用不会破坏任何功能——但永远不要将 *新的* 工作流连接到其中一个。CLI 1.0.92 中弃用了两个，其中一个是自引用的 `cargo` 集成。检查标志而不是保持列表：在通过浏览而不是 `action list` 找到集成之前，检查 `isDeprecated`。

### 哪个操作搜索？

| | `orchestration action list` | `connection action search` |
|---|---|---|
| 覆盖 | 连接器、原生、**工具、代理** | 仅连接器目录 |
| 返回 | 可运行的 `action` 对象，包含 `connectorUuid`、工作区连接器、`credits`、自动完成 | `integrationSlug` + `actionSlug`、类别、`credits` — 你需要自己组装操作 |
| 过滤 | `--kind`、`--integration-slug`、`--limit` | `--category`、`--integration`、**`--credits-only`**、`--limit` |
| 需要 | CLI ≥ 1.0.66 | CLI ≥ 1.0.36 |

默认使用 `action list`——它是唯一能给你可执行内容的一个。切换到 `action search` 以回答它唯一能回答的两个问题：*哪些付费操作匹配这个？* (`--credits-only`) 和 *这个类别提供什么？* (`--category`)。两者都会将 action-slug 或名称的命中排名高于集成命中，高于描述命中，并且需要 **所有** 查询词匹配。

### `integration get` vs `native-integration get`

这两个命令返回 **不同的操作集**，并且不能互换使用：

| 命令 | 第三方服务操作（HubSpot、Salesforce、Clearbit、…） | 内置的 Cargo 操作（HTTP、转换、工具） | 使用时机 |
|---|---|---|---|
| `integration get <slug>` | ✓ | ✗ | 你需要特定第三方服务的操作——**用于 HubSpot、Salesforce、Clearbit 等。** |
| `native-integration get` | ✗ | ✓ | 你需要 Cargo 原生功能，这些功能不属于任何特定第三方连接器 |

**示例**：要查找 HubSpot 特定的操作，使用 `integration get hubspot`——`native-integration get` 不会返回它们。

## 快速参考

```bash
cargo-ai connection connector list --integration-slug <slug>
cargo-ai connection connector create --integration-slug <slug> --slug <slug> --name <name>
cargo-ai connection connector update --uuid <uuid> --name <name>
cargo-ai connection connector remove <connector-uuid>
cargo-ai connection connector get <connector-uuid>
cargo-ai connection connector autocomplete --connector-uuid <uuid> --slug <slug> --params '<json>'
cargo-ai connection integration list
cargo-ai connection integration get <slug>
cargo-ai connection integration get-documentation <slug>
cargo-ai connection native-integration get
```

## 连接器

连接器是外部服务的已认证连接。

```bash
# 列出所有连接器
cargo-ai connection connector list

# 创建连接器
cargo-ai connection connector create \
  --integration-slug clearbit \
  --slug clearbit_production \
  --name "Clearbit - Production"

# 更新连接器
cargo-ai connection connector update --uuid <connector-uuid> --name "Clearbit - Staging"

# 删除连接器
cargo-ai connection connector remove <connector-uuid>

# 检查连接器 slug 是否已被占用
cargo-ai connection connector exists-by-slug --slug clearbit_production
```

**注意**：创建连接器需要 `--slug`（唯一标识符）以及 `--name`（显示名称）和 `--integration-slug`。对于基于 OAuth 的集成，认证流程通过 `connection integration complete-oauth` 另行完成。

## 集成

集成定义了可用服务及其连接器操作。

```bash
# 列出所有可用集成
cargo-ai connection integration list

# 按类别过滤
cargo-ai connection integration list --category enrichment

# 按名称搜索
cargo-ai connection integration list --search "hubspot"

# 按确切的 slug(s) 查找
cargo-ai connection integration list --slugs clearbit

# 仅具有操作的集成（可在工作流节点中使用）
cargo-ai connection integration list --has-actions true

# 仅具有提取器的集成（可以将数据同步到模型）
cargo-ai connection integration list --has-extractors true

# 获取内置的 Cargo 操作和提取器（不是第三方连接器操作）
cargo-ai connection native-integration get
```

**集成类别**：`engagement`、`marketing`、`sales`、`finance`、`analytics`、`freeform`、`success`、`support`、`enrichment`、`storage`、`custom`。

使用 `integration get <slug>` 发现特定第三方服务（例如 HubSpot、Salesforce）的所有操作。仅使用 `native-integration get` 获取内置的 Cargo 操作——它**不**返回 HubSpot 或其他服务特定的操作。操作在工作流节点图中由 `actionSlug` 引用（见 `cargo-orchestration` 技能的 `references/nodes.md`）。

## 连接器自动完成——获取操作字段的可用值

某些操作字段不接受自由输入——它们的允许值必须动态从连接器获取。当你检查操作的配置（通过 `integration get <slug>` 或 `native-integration get`）时，查看 `uiSchema` 以及 `jsonSchema`。如果某个字段的 `uiSchema` 包含 `"ui:widget": "IntegrationAutocompleteWidget"`，则该字段的**有效值**必须使用 `connector autocomplete` 获取。

### 如何检测自动完成字段

当操作配置看起来像这样时：

```json
{
  "jsonSchema": {
    "type": "object",
    "properties": {
      "objectType": { "type": "string", "description": "The object type" }
    }
  },
  "uiSchema": {
    "objectType": {
      "ui:widget": "IntegrationAutocompleteWidget",
      "ui:options": {
        "slug": "listObjects",
        "allowRefresh": true
      }
    }
  }
}
```

`objectType` 字段需要自动完成。`ui:options.slug` (`"listObjects"`) 是传递给 `connector autocomplete` 的自动完成 slug。

### 如何调用连接器自动完成

```bash
cargo-ai connection connector autocomplete \
  --connector-uuid <connector-uuid> \
  --slug <autocomplete-slug> \
  --params '{}'
```

| 标志               | 必需 | 描述                                                       |
| ------------------ | -------- | ----------------------------------------------------------------- |
| `--connector-uuid` | 是      | 要自动完成的连接器的 UUID                                 |
| `--slug`           | 是      | 从 `uiSchema[field]["ui:options"].slug` 获取的自动完成 slug   |
| `--params`         | 是      | 参数 JSON 对象（不需要时使用 `{}`）                     |
| `--value`          | 否       | 过滤结果的搜索字符串                                       |
| `--refresh`        | 否       | 跳过缓存并获取最新结果                              |

### 带参数的自动完成

某些自动完成字段依赖于另一个字段的值。这由 `ui:options` 中的 `params` 对象指示：

```json
{
  "uiSchema": {
    "objectType": {
      "ui:widget": "IntegrationAutocompleteWidget",
      "ui:options": { "slug": "listObjects" }
    },
    "propertyName": {
      "ui:widget": "IntegrationAutocompleteWidget",
      "ui:options": {
        "slug": "listObjectProperties",
        "params": { "objectType": "$this.$parent.objectType" }
      }
    }
  }
}
```

这里，`propertyName` 依赖于选定的 `objectType`。将 `$this.$parent...` 表达式替换为你实际选择的值：

```bash
# 1. 首先，获取对象类型的列表
cargo-ai connection connector autocomplete \
  --connector-uuid <uuid> --slug listObjects --params '{}'

# 2. 然后，获取选定对象类型的属性
cargo-ai connection connector autocomplete \
  --connector-uuid <uuid> --slug listObjectProperties \
  --params '{"objectType": "contacts"}'
```

### 响应格式

```json
{
  "results": [
    { "label": "Contacts", "value": "contacts" },
    { "label": "Companies", "value": "companies" },
    { "label": "Deals", "value": "deals" }
  ]
}
```

在节点配置中使用 `value` 字段。`label` 是人类可读的显示名称。结果还可能包括可选的 `description` 和 `parent` 字段。

### 端到端示例：配置一个 HubSpot 操作

```bash
# 1. 找到你的 HubSpot 连接器 UUID
cargo-ai connection connector list --integration-slug hubspot

# 2. 获取 HubSpot 操作并检查其配置 + uiSchema
cargo-ai connection integration get hubspot
# → "findRecords" 操作的 objectType 字段具有自动完成 slug "listObjects"

# 3. 获取可用对象类型
cargo-ai connection connector autocomplete \
  --connector-uuid <hubspot-connector-uuid> \
  --slug listObjects --params '{}'
# → 返回：contacts、companies、deals、tickets、等。

# 4. 获取选定对象类型的属性
cargo-ai connection connector autocomplete \
  --connector-uuid <hubspot-connector-uuid> \
  --slug listObjectProperties \
  --params '{"objectType": "contacts"}'
# → 返回：email、firstname、lastname、phone、等。

# 5. 在你的工作流节点配置中使用这些值
```

## 在工作流中使用连接器操作

连接器操作作为工作流图中的节点使用。要使用操作：

```bash
# 1. 找到你的连接器 UUID
cargo-ai connection connector list
# → 通过 integrationSlug 过滤输出以找到正确的连接器

# 2. 发现操作——首先搜索，然后读取其模式
cargo-ai orchestration action list <keywords> --integration-slug <integration-slug>
cargo-ai connection integration get <integration-slug>
# → 操作按 actionSlug 键值对存储，每个操作都有 config.jsonSchema（输入）
# → 许多操作还携带 output.schema——操作的 JSON Schema，用于连接下游节点而不是猜测（某些操作没有）
# → 或使用 get-documentation 获取纯文本概述
# → 或使用 native-integration get 获取内置的 Cargo 操作（不是第三方）

# 3. 在节点图中引用连接器和操作
# 见 cargo-orchestration references/nodes.md 获取完整的节点语法
```

### 读取操作的输入模式——输入在哪里

操作的**输入**字段位于 `actions.<slug>.config.schema` 中，这是 `integration get <slug>` 输出的 (`config.jsonSchema` 是为表单 UI 装饰的相同模式)。在调用操作之前读取它——不要猜测字段名称。

```bash
# 操作的必需输入字段：
cargo-ai connection integration get linkedin \
  | jq '.integration.actions.connectProfile.config.schema'
# → required: linkedinProfileUrl, identityIds
```

两个陷阱：

- **对于顶层操作 (`action execute` / `execute-batch`)，输入值放在 `--data` 中，而不是操作的 `config` 中。** `config.schema` 描述的字段是 `--data` 负载；操作定义本身不携带 `config` 键。**错误放置它们不再导致大声失败**：旧的后端会拒绝调用并显示 `A top-level action does not use action.config; pass the action's inputs via data instead.`，新的后端在进入时丢弃 `config` 并以**没有输入**运行操作——你会从提供者那里收到缺失必需字段的错误，或空结果，而不是关于 `config` 的消息。如果操作以没有明显原因返回空值，请检查输入是否在 `--data` 中。（在工作流**节点图中**，这些相同的字段放在节点的 `config` 中——见 `cargo-orchestration/references/nodes.md`。`"--data`，不是 `config` 的规则是特定于 `action execute`/`execute-batch` 的。）
- **某些输入必须先通过自动完成解析。** 如果字段的 `uiSchema` 携带 `IntegrationAutocompleteWidget`，使用 `connector autocomplete` 获取其值（如上所述）。值得注意的是，LinkedIn engagement/extraction 操作 (`connectProfile`、`visitProfile`、`extractEventAttendees`、`extractProfileViewers`) 需要的 `identityIds`——连接的账户（执行者）——通过 `listIdentityIds` 自动完成解析。一个 `must match format "uuid"` 错误意味着缺少身份。

```json
{
  "uuid": "node-uuid",
  "slug": "enrich",
  "kind": "connector",
  "integrationSlug": "clearbit",
  "actionSlug": "enrichCompany",
  "connectorUuid": "<clearbit-connector-uuid>",
  "config": {
    "domain": {
      "kind": "templateExpression",
      "expression": "{{nodes.start.domain}}",
      "instructTo": "none",
      "fromRecipe": false
    }
  },
  "childrenUuids": ["end-node-uuid"],
  "fallbackOnFailure": false,
  "position": { "x": 0, "y": 166 }
}
```

## 帮助

每个命令都支持 `--help`：

```bash
cargo-ai connection connector list --help
cargo-ai connection connector create --help
cargo-ai connection integration list --help
```
