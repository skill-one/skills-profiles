# Cargo CLI — 连接

连接器和集成管理：列出连接器、发现可用的集成以及管理经过身份验证的连接器实例。

> 参考文档 `references/response-shapes.md` 获取完整的 JSON 响应结构。
> 参考文档 `references/troubleshooting.md` 获取常见错误及其解决方法。
> 参考文档 `references/examples/connectors.md` 获取连接器 CRUD 和发现示例。
> 参考文档 `references/examples/integrations.md` 获取列出可用集成和 OAuth 流程示例。
> 工作流中第三方连接器的速率限制处理和重试配置，请参考 `cargo-orchestration/references/polling.md` 和 `cargo-orchestration/references/troubleshooting.md`。原生集成没有速率限制。

## 初始化

已经登录 (`cargo-ai whoami` 返回工作区)？跳到下一节。

```bash
npm install -g @cargo-ai/cli            # 没有全局安装？为每个命令前缀 `npx @cargo-ai/cli`
cargo-ai login --email you@company.com  # 发送邮件代码，无需浏览器；首次使用时创建账户
                                        # 替代方案：--oauth (浏览器) · --token <api-token> (CI)
cargo-ai whoami                         # 在任何写入操作前确认活动工作区
```

每个命令都会将 JSON 打印到标准输出；失败时以非零状态退出并打印 `{"errorMessage": "..."}`。创建运行或批处理操作都是异步的 — 传递 `--wait-until-finished` 或轮询匹配的 `get`。当完整技能包安装后，`[../cargo/references/prerequisites.md](../cargo/references/prerequisites.md)` 会添加 CLI 版本固定、令牌范围和管理员专用的界面。

## 关键概念

**集成**：外部服务类型（例如 HubSpot、Clearbit、Salesforce）。集成定义了可用的操作。

**连接器**：集成的经过身份验证的实例。一个集成可以有多个连接器（例如两个不同的 HubSpot 账户）。连接器是在工作流节点图中引用的对象。

## 先发现资源

**查找操作？搜索它，不要浏览目录。** 两个关键词搜索覆盖整个界面，并且都比分页 `integration list` 或读取整个 `integration get` 负载更有效：

```bash
cargo-ai orchestration action list <query>                # 从这里开始 — 连接器 + 原生 + 工具 + 代理。
                                                          # 返回一个可运行的 action 对象（已解析 connectorUuid）和操作的信用成本。
cargo-ai connection action search <query> --credits-only  # 仅连接器目录，但按类别过滤
                                                          # 并按“是否付费”过滤 — `action list` 无法做到。
```

当你需要集成而不是操作时，使用目录命令 — 它的身份验证字段、它的提取器或你已经选择的操作的完整输入模式：

```bash
cargo-ai connection connector list                        # 所有经过身份验证的连接器
cargo-ai connection integration list                      # 所有可用的集成类型
cargo-ai connection integration list --search "hubspot"   # 按名称搜索
cargo-ai connection integration get <slug>                # 一个集成的操作 + 输入模式
cargo-ai connection native-integration get                # 仅内置 Cargo 操作（不是第三方）
```

> **已弃用的集成仍然出现在目录中。** `integration list` 会以 `isDeprecated: true` 和以 `(deprecated)` 结尾的显示名称返回它们。现有的连接器仍然可以工作 — 弃用不会破坏任何功能 — 但永远不要将新工作流连接到其中一个。CLI 1.0.92 中弃用了两个，其中一个是自引用的 `cargo` 集成。检查标志而不是保持列表：在浏览而不是通过 `action list` 找到任何集成之前检查 `isDeprecated`。

### 哪个操作搜索？

| | `orchestration action list` | `connection action search` |
|---|---|---|
| 覆盖 | 连接器、原生、**工具、代理** | 仅连接器目录 |
| 返回 | 可运行的 `action` 对象，包含 `connectorUuid`、工作区连接器、`credits`、自动完成 | `integrationSlug` + `actionSlug`、类别、`credits` — 你自己组装操作 |
| 过滤 | `--kind`、`--integration-slug`、`--limit` | `--category`、`--integration`、**`--credits-only`**、`--limit` |
| 需要 | CLI ≥ 1.0.66 | CLI ≥ 1.0.36 |

默认使用 `action list` — 它会给你一个可以执行的对象。对于它唯一能回答的两个问题切换到 `action search`：*哪些付费操作匹配这个？* (`--credits-only`) 和 *这个类别提供什么？* (`--category`)。两者都会将 action-slug 或名称的匹配项排在集成匹配项之上，并且要求**所有**查询词都匹配。

### `integration get` vs `native-integration get`

这两个命令返回**不同的操作集**，并且不能互换使用：

| 命令 | 第三方服务操作（HubSpot、Salesforce、Clearbit、…） | 内置 Cargo 操作（HTTP、转换、工具） | 使用时机 |
|---|---|---|---|
| `integration get <slug>` | ✓ | ✗ | 你需要特定第三方服务的操作 — **用于 HubSpot、Salesforce、Clearbit 等。** |
| `native-integration get` | ✗ | ✓ | 你需要 Cargo 原生功能，这些功能不属于任何特定第三方连接器 |

**示例**：要查找 HubSpot 特定操作，使用 `integration get hubspot` — `native-integration get` 不会返回它们。

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

连接器是到外部服务的经过身份验证的连接。

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

**注意**：创建连接器需要 `--slug`（唯一标识符）以及 `--name`（显示名称）和 `--integration-slug`。对于基于 OAuth 的集成，身份验证流程通过 `connection integration complete-oauth` 另行完成。

## 集成

集成定义了可用的服务及其连接器操作。

```bash
# 列出所有可用的集成
cargo-ai connection integration list

# 按类别过滤
cargo-ai connection integration list --category enrichment

# 按名称搜索
cargo-ai connection integration list --search "hubspot"

# 按精确的 slug(s) 查找
cargo-ai connection integration list --slugs clearbit

# 仅具有操作的集成（可在工作流节点中使用）
cargo-ai connection integration list --has-actions true

# 仅具有提取器的集成（可以将数据同步到模型）
cargo-ai connection integration list --has-extractors true

# 获取内置 Cargo 操作和提取器（不是第三方连接器操作）
cargo-ai connection native-integration get
```

**集成类别**：`engagement`、`marketing`、`sales`、`finance`、`analytics`、`freeform`、`success`、`support`、`enrichment`、`storage`、`custom`。

使用 `integration get <slug>` 发现特定第三方服务（例如 HubSpot、Salesforce）的所有操作。仅用于内置 Cargo 操作的 `native-integration get` — 它**不会**返回 HubSpot 或其他服务特定操作。操作在工作流节点图中由 `actionSlug` 引用（见 `cargo-orchestration` 技能的 `references/nodes.md`）。

## 连接器自动完成 — 获取操作字段的可用值

某些操作字段不接受自由输入 — 它们的允许值必须动态从连接器获取。当你检查操作的配置（通过 `integration get <slug>` 或 `native-integration get`）时，查看 `uiSchema` 以及 `jsonSchema`。如果某个字段的 `uiSchema` 包含 `"ui:widget": "IntegrationAutocompleteWidget"`，则该字段的**有效值**必须使用 `connector autocomplete` 获取。

### 如何检测自动完成字段

当操作配置看起来像这样：

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

`objectType` 字段需要自动完成。`ui:options.slug` (`"listObjects"`) 是你传递给 `connector autocomplete` 的自动完成 slug。

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
| `--value`          | 否       | 用于过滤结果的搜索字符串                                   |
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

这里，`propertyName` 依赖于选择的 `objectType`。将 `$this.$parent...` 表达式替换为你实际选择的值：

```bash
# 1. 首先，获取对象类型的列表
cargo-ai connection connector autocomplete \
  --connector-uuid <uuid> --slug listObjects --params '{}'

# 2. 然后，获取所选对象类型的属性
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
# 1. 查找你的 HubSpot 连接器 UUID
cargo-ai connection connector list --integration-slug hubspot

# 2. 获取 HubSpot 操作并检查其配置 + uiSchema
cargo-ai connection integration get hubspot
# → "findRecords" 操作的 objectType 具有自动完成 slug "listObjects"

# 3. 获取可用的对象类型
cargo-ai connection connector autocomplete \
  --connector-uuid <hubspot-connector-uuid> \
  --slug listObjects --params '{}'
# → 返回：contacts、companies、deals、tickets、等。

# 4. 获取所选对象类型的属性
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
# 1. 查找你的连接器 UUID
cargo-ai connection connector list
# → 通过 integrationSlug 过滤输出以找到正确的连接器

# 2. 发现操作 — 首先搜索，然后读取其模式
cargo-ai orchestration action list <keywords> --integration-slug <integration-slug>
cargo-ai connection integration get <integration-slug>
# → 操作按 actionSlug 键值对，每个都有 config.jsonSchema (输入)
# → 许多操作还携带 output.schema — 操作发出的 JSON Schema；使用它来连接下游节点，而不是猜测（某些操作没有）
# → 或使用 get-documentation 获取纯文本概述
# → 或使用 native-integration get 获取内置 Cargo 操作（不是第三方）

# 3. 在节点图中引用连接器和操作
# 见 cargo-orchestration references/nodes.md 获取完整节点语法
```

### 读取操作的输入模式 — 输入在哪里

操作的**输入**字段位于 `actions.<slug>.config.schema` 中，这是 `integration get <slug>` 输出 (`config.jsonSchema` 是为表单 UI 装饰的相同模式)。在调用操作前读取它 — 不要猜测字段名称。

```bash
# 操作的必需输入字段：
cargo-ai connection integration get linkedin \
  | jq '.integration.actions.connectProfile.config.schema'
# → 必需：linkedinProfileUrl、identityIds
```

两个陷阱：

- **对于顶层操作 (`action execute` / `execute-batch`)，输入值放在 `--data` 中，而不是在操作的 `config` 中。** `config.schema` 描述的字段是 `--data` 负载；操作定义本身不携带 `config` 键。**放置错误不再是明显的失败**：旧的后端会以 `A top-level action does not use action.config; pass the action's inputs via data instead.` 拒绝调用，新后端在进入时丢弃 `config` 并以**没有输入**运行操作 — 你会从提供者那里收到缺少必需字段的错误，或者得到空结果，而不是关于 `config` 的消息。如果操作没有明显原因返回空值，请检查输入是否在 `--data` 中。（在工作流**节点图**中，相同的字段放在节点的 `config` 中 — 见 `cargo-orchestration/references/nodes.md`。`"--data`，不是 `config` 的规则是特定于 `action execute`/`execute-batch` 的。）
- **某些输入必须先通过自动完成解析。** 如果字段的 `uiSchema` 携带 `IntegrationAutocompleteWidget`，使用 `connector autocomplete` 获取其值（如上所述）。值得注意的是，LinkedIn engagement/extraction 操作 (`connectProfile`、`visitProfile`、`extractEventAttendees`、`extractProfileViewers`) 需要的 `identityIds` — 连接的账户（执行者）— 通过 `listIdentityIds` 自动完成解析。`must match format "uuid"` 错误意味着缺少身份。

示例连接器节点（Clearbit 公司丰富）：

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

每个命令支持 `--help`：

```bash
cargo-ai connection connector list --help
cargo-ai connection connector create --help
cargo-ai connection integration list --help
```
