# n8n 凭证和安全

## 必须遵守的规则

1. **通过凭证系统处理秘密，绝不在文本字段或 SDK 代码中直接存储。** API 密钥、令牌、OAuth 秘密、密码：所有内容都应通过 `newCredential()` 或节点的 `credentials` 参数处理。使用 Set 节点硬编码令牌并通过 `{{$json.token}}` 读取，相当于在文本字段中执行额外步骤。
2. **先列出凭证，再通过 ID 绑定。** 在配置需要认证的节点之前，调用 `list_credentials({type})`。如果匹配到一个：在创建时通过 2 参数 `newCredential('Label', 'credId')` 绑定，或在 `update_workflow` 操作上使用 `setNodeCredential`。如果匹配多个：询问用户选择哪个。1 参数 `newCredential('Label')` 是占位符；n8n 会自动分配最近编辑的该类型凭证，并在用户有多个时静默选择错误的凭证。
3. **凭证创建是用户的责任，不是你的。** n8n MCP 不暴露凭证创建功能。在 UI 中告知用户需要创建的确切凭证 *类型*，然后在节点配置中通过标签引用。不要尝试以编程方式创建凭证，也不要在聊天中接收秘密以“稍后设置”。

## 强制性默认设置

- **在可用时使用原生凭证。** 每个原生节点（Slack、Gmail、Postgres、OpenAI 等）都有一个凭证类型。当存在原生选项时，不要使用通用凭证类型。
- **对于多头部或头部加查询参数的认证结构**，使用 `httpCustomAuth` 凭证类型。参考 `references/CUSTOM_CREDENTIALS.md`。

## 凭证系统

在 n8n 中，凭证是一等对象：

- 加密存储在 n8n 数据库中。
- 由需要它们的节点通过 ID 引用。
- 限定在项目（云和企业版）或全局共享（某些自托管设置）。
- 通过类型缩写（googleSheetsOAuth2Api、slackApi、httpHeaderAuth）标识。缩写是节点引用的内容，并决定凭证收集的认证字段。

需要认证的节点有一个指向凭证 ID + 类型的 `credentials` 参数。秘密值永远不会出现在工作流 JSON 中。导出工作流会泄露 *引用*，而不是秘密。

有关完整模型（SDK 解析、轮换、项目范围），参考 `references/CREDENTIAL_SYSTEM.md`。

## 决策树：如何认证这个服务

```
需要调用外部服务？
├── 存在原生凭证（Slack、Gmail、OpenAI、Postgres、...）？
│   └── 使用原生节点 + 其凭证类型。完成。
│
├── 服务是“标准结构”（REST + Bearer/Basic/OAuth）？
│   ├── 使用内置认证类型配置 HTTP 请求：
│   │   - 通用 OAuth2
│   │   - 头部认证
│   │   - Bearer 认证（仅令牌字段为实际令牌）
│   │   - Basic 认证
│   │   - 自定义认证
│   └── 参考 `references/HTTP_REQUEST_WITH_AUTH.md`
│
└── 服务需要多个静态头部，或头部加查询参数？
    └── 使用 httpCustomAuth 凭证类型。
        参考 `references/CUSTOM_CREDENTIALS.md`
```

## 当用户在聊天中粘贴秘密时

这种情况会发生。用户输入类似：

> "设置一个工作流来调用 Acme API，使用 Bearer 令牌 `sk-abc123def456`"

该怎么做：

1. **不要将令牌放在文本字段中，即使是临时性的。** 使用硬编码值的 Set 节点并通过 `{{$json.token}}` 引用，相当于在文本字段中执行额外步骤。
2. **如果可能，绑定到现有凭证。** 先调用 `list_credentials({type})`；如果存在匹配项，通过 `setNodeCredential` 绑定，并告知用户使用了哪个。如果没有，告知用户在 UI 中创建一个凭证（Bearer 认证用于 Bearer 令牌，Header 认证用于自定义头部等）。凭证创建仍然是 UI 操作。
3. **将粘贴的秘密视为已泄露，并告知用户轮换它。** 不要淡化这一点。令牌已传输给 LLM 提供商，可能存在于聊天历史记录、转录和缓存层中。告知他们："在新凭证设置完成后立即轮换此令牌。将其视为已泄露。"

## 当不存在原生节点时

常见情况：用户希望使用 n8n 没有节点的服务。使用 HTTP 请求并配合适当的认证。

- `references/FINDING_API_DOCS.md`：发现认证方案、基本 URL、常见结构。
- `references/HTTP_REQUEST_WITH_AUTH.md`：将 HTTP 请求连接到凭证。
- `references/CUSTOM_CREDENTIALS.md`：内置认证类型不适用时。

## 参考文件

| 文件 | 何时阅读 |
|---|---|
| `references/CREDENTIAL_SYSTEM.md` | 您需要了解凭证如何存储、引用、限定范围或轮换 |
| `references/CUSTOM_CREDENTIALS.md` | 在一个凭证中处理多头部 / 头部加查询参数认证，或请求级签名模式（HMAC、JWT、webhook 验证） |
| `references/HTTP_REQUEST_WITH_AUTH.md` | 配置带认证的 HTTP 请求：Bearer、Basic、OAuth、Header 认证 |
| `references/FINDING_API_DOCS.md` | 用户提到了您不了解节点级知识的服务 |

## 反模式

| 反模式 | 问题所在 | 解决方法 |
|---|---|---|
| 将 `sk-...` 粘贴到 HTTP 请求的 `Authorization` 头部值字段 | 令牌以明文形式出现在工作流 JSON 中，导出、复制、截图时泄露 | 使用凭证：`Bearer 认证` 用于 Bearer 令牌，`Header 认证` 用于其他自定义认证方案 |
| 在 Set 节点中存储令牌并通过表达式引用 | 同样的问题，值存在于工作流 JSON 中 | 同样解决方法：凭证，而不是 Set 节点 |
| 在 `$vars.X` 中存储秘密，并作为认证值读取 | 存储时未加密，导出时泄露，无法轮换 | 使用正确的凭证类型（`httpBearerAuth`、`httpHeaderAuth`、`httpCustomAuth` 或原生类型）。对于入站 webhook 认证，使用触发器的 `authentication` 字段，而不是 `$vars.token` 上的 IF 条件 |
| 在自定义认证设置期间使用 `$env.X` 读取秘密 | 不起作用，运行时抛出错误 | 使用适当类型的凭证 |
| 当存在原生节点时使用 HTTP 请求 | 失去 OAuth 自动刷新，失去原生错误处理，代码更多 | 使用原生节点 |
| 在 SDK 代码中硬编码凭证（`new HttpRequest({ headers: { Authorization: 'Bearer xxx' } })`） | 同样泄露面 | 在 SDK 代码中使用 `newCredential()` |
| 未指定凭证 *类型* 而要求用户创建凭证 | 用户选择了错误类型，认证失败且令人困惑 | 始终指定："创建一个类型为 `<确切类型名称>` 的凭证" |
