# Microsoft Graph Agent Skill

搜索、查找和调用 27,700 多个 Microsoft Graph API — 所有操作均在本地进行，无需网络调用。使用三个搜索命令查找正确的端点、检查权限和参数，然后可选择直接执行调用或将任务转交给 Graph MCP 服务器。

## 包含内容

Microsoft Graph API 每周更新 **27,700 多个端点** — 远超 LLM 训练的截止点。此技能将完整的 API 表面打包为本地索引，您无需网络调用即可即时搜索。

| 索引 | 数量 | 包含内容 |
|---|---|---|
| OpenAPI 端点 | 27,700+ | 路径、方法、摘要、描述、权限范围 |
| 端点文档 | 6,200+ | 权限（委托/应用程序）、查询参数、必需的标头、默认值与 `$select` 仅属性 |
| 资源模式 | 4,200+ | 所有属性及其类型、支持的 `$filter` 运算符、默认/`$select` 仅标志 |
| 社区示例 | 正在增长 | 经手动验证的查询，将自然语言任务映射到精确的 API 调用 |

## 如何运行

`msgraph` CLI 随此技能捆绑。通过此技能目录中的启动器脚本运行所有命令：

- **macOS / Linux**: `bash <此技能路径>/scripts/run.sh <命令> [参数...]`
- **Windows**: `powershell <此技能路径>/scripts/run.ps1 <命令> [参数...]`

例如，在 macOS 上搜索与邮件相关的 API：

```
bash /home/user/.opencode/skills/msgraph/scripts/run.sh openapi-search --query "发送邮件"
```

在以下所有示例中，`msgraph` 是完整启动器调用的简称。

## 查找正确的 API

这是此技能的主要用途。遵循以下渐进式查找策略 — 每个级别都会增加详细信息：

1. **您自己的知识** — 首先尝试查找众所周知的端点（`/me`、`/users`、`/groups`）。
2. **`sample-search`** — 精选的、经手动验证的示例。最高质量。用于常见任务和多步骤工作流。
3. **`api-docs-search`** — 每个端点的权限、支持的查询参数、必需的标头、默认值与 `$select` 仅属性，以及资源属性详细信息（包括 `$filter` 运算符）。
4. **`openapi-search`** — 27,700 个 Graph API 的完整目录。当您无法以其他方式找到端点时使用。
5. **参考文件** — 查询参数、高级查询、分页、批处理、速率限制、错误和最佳实践的概念文档。仅在需要特定指导时阅读。

此顺序是指导 — 根据任务进行调整。例如，如果您已知端点但需要其权限，则直接跳转到 `api-docs-search`。

### sample-search

搜索精选的社区示例，这些示例将自然语言任务映射到精确的 Microsoft Graph API 查询：

```
msgraph sample-search --query "条件访问策略"
msgraph sample-search --product entra
msgraph sample-search --query "受管理的设备" --product intune
```

| 标志 | 描述 |
|---|---|
| `--query` | 自由文本搜索（搜索意图和查询字段） |
| `--product` | 按产品筛选：`entra`、`intune`、`exchange`、`teams`、`sharepoint`、`security`、`general` |
| `--limit` | 最大结果数（默认为 10） |

至少需要 `--query` 或 `--product` 中的一个。结果包括多步骤工作流。

### api-docs-search

查找特定端点或资源类型的详细文档：

```
msgraph api-docs-search --endpoint /users --method GET
msgraph api-docs-search --resource user
msgraph api-docs-search --query "ConsistencyLevel"
```

| 标志 | 描述 |
|---|---|
| `--endpoint` | 通过端点路径搜索（例如 `/users`、`/me/messages`） |
| `--resource` | 通过资源类型名称搜索（例如 `user`、`group`、`message`） |
| `--method` | 按 HTTP 方法筛选：`GET`、`POST`、`PUT`、`PATCH` |
| `--query` | 跨所有字段进行自由文本搜索 |
| `--limit` | 最大结果数（默认为 10） |

至少需要 `--endpoint`、`--resource` 或 `--query` 中的一个。

**端点结果** 包括：必需的权限（委托工作/学校、委托个人、应用程序）、支持的 OData 查询参数、必需的标头、默认属性和端点特定说明。

**资源结果** 包括：所有属性及其类型、支持的 `$filter` 运算符（eq、ne、startsWith 等），以及每个属性是默认返回还是需要 `$select`。

### openapi-search

搜索 27,700 个 Microsoft Graph API 的完整 OpenAPI 目录：

```
msgraph openapi-search --query "发送邮件"
msgraph openapi-search --resource messages --method GET
```

| 标志 | 描述 |
|---|---|
| `--query` | 自由文本搜索（搜索路径、摘要、描述） |
| `--resource` | 按资源名称筛选（例如 `users`、`groups`、`messages`） |
| `--method` | 按 HTTP 方法筛选 |
| `--limit` | 最大结果数（默认为 20） |

至少需要 `--query`、`--resource` 或 `--method` 中的一个。

## 与 MCP 服务器的使用

如果代理可以访问 Microsoft Graph MCP 服务器（例如 [lokka.dev](https://lokka.dev) 或任何其他 Microsoft Graph MCP 服务器），请使用上述搜索工具查找正确的端点、权限和请求语法，然后使用这些信息与 MCP 服务器执行操作。

在此模式下，**无需通过此技能进行身份验证**。此技能纯粹作为知识层 — MCP 服务器处理身份验证和 API 执行。

## 直接 Microsoft Graph API 执行

当没有 Graph MCP 服务器可用时，此技能可以身份验证到 Microsoft 365 并直接执行 Microsoft Graph API 调用。

### 身份验证

该工具支持 **委托（用户）** 和 **应用程序（仅应用程序）** 身份验证，自动从环境变量中检测。

**快速入门**：

```
msgraph auth status          # 检查是否已登录
msgraph auth signin          # 登录（打开浏览器）- 推荐
msgraph auth signin --device-code  # 通过设备代码登录（无头环境）
msgraph auth signout         # 清除会话
```

- **委托身份验证**（默认）：交互式浏览器登录，对于无头环境使用设备代码回退。支持增量同意 — 在 403 时，工具使用所需范围重新身份验证并自动重试。
- **应用程序身份验证**：当设置 `MSGRAPH_CLIENT_SECRET`、`MSGRAPH_CLIENT_CERTIFICATE_PATH`、`MSGRAPH_FEDERATED_TOKEN_FILE` 或 `MSGRAPH_AUTH_METHOD=managed-identity` 时自动检测。需要 `MSGRAPH_TENANT_ID`。

有关详细身份验证配置（包括证书、托管身份、工作负载身份联合和所有环境变量），请参阅 [references/docs/authentication.md](references/docs/authentication.md)。

### 执行 Graph API 调用

**重要提示**：在会话中第一次 `graph-call` 之前运行 `msgraph auth status` 以验证身份验证。

```
msgraph graph-call <METHOD> <URL> [标志]
```

#### 读取操作

```
msgraph graph-call GET /me
msgraph graph-call GET /users --select "displayName,mail" --top 10
msgraph graph-call GET /me/messages --filter "isRead eq false" --top 5 --select "subject,from,receivedDateTime"
msgraph graph-call GET /users --filter "startsWith(displayName,'John')"
```

#### 写入操作

**重要提示**：在执行任何写入操作之前，必须先向用户确认。写入操作需要 `--allow-writes` 标志。

```
msgraph graph-call POST /me/sendMail --body '{"message":{"subject":"Hello","body":{"content":"Hi"},"toRecipients":[{"emailAddress":{"address":"user@example.com"}}]}}' --allow-writes
msgraph graph-call PATCH /me --body '{"jobTitle":"Engineer"}' --allow-writes
```

**DELETE 始终被阻止**，无论标志如何。

#### graph-call 标志

| 标志 | 描述 | 示例 |
|---|---|---|
| `--select` | OData $select | `--select "displayName,mail"` |
| `--filter` | OData $filter | `--filter "isRead eq false"` |
| `--top` | OData $top（限制结果） | `--top 10` |
| `--expand` | OData $expand | `--expand "members"` |
| `--orderby` | OData $orderby | `--orderby "displayName desc"` |
| `--api-version` | `v1.0` 或 `beta`（默认：beta） | `--api-version v1.0` |
| `--scopes` | 请求附加权限范围 | `--scopes "Mail.Read"` |
| `--headers` | 自定义 HTTP 标头 | `--headers "ConsistencyLevel:eventual"` |
| `--body` | 请求正文（JSON） | `--body '{"key":"value"}'` |
| `--output` | `json`（默认）或 `raw` | `--output raw` |
| `--allow-writes` | 允许 POST/PUT/PATCH（需要用户确认） | |

## 严格规则

### 总是（搜索和知识）

1. **切勿猜测或编造 Microsoft Graph 端点** — 在调用之前始终通过搜索进行验证。此技能的存在是因为代理会“幻觉”端点；使用它。
2. **使用渐进式查找策略** — 从您所知的内容开始，然后按需使用 sample-search、api-docs-search、openapi-search。
3. **使用 `--select`** 来减少响应大小 — 仅请求您需要的字段。
4. **使用 `--top`** 来限制结果 — 避免获取数千条记录。
5. **ConsistencyLevel 标头** 对于目录对象（用户、组等）上的 `$count` 和 `$search` 是必需的。使用 `--headers "ConsistencyLevel:eventual"`。
6. **默认 API 版本为 beta** — 使用 `--api-version v1.0` 用于生产稳定的端点。

### 使用直接执行（graph-call）

7. **在会话中第一次 `graph-call` 之前检查 auth 状态**。
8. **GET 是默认值** — 无需特殊标志。
9. **写入操作需要 `--allow-writes`** — 您必须先向用户确认。
10. **DELETE 始终被阻止** — 告知用户此操作不受支持。
11. **403 触发自动重新身份验证** — 工具请求附加范围并重试（仅委托身份验证）。
12. **所有输出都是 JSON** — 从响应中解析 `statusCode` 和 `body` 字段。

## 错误处理

| 状态 | 含义 | 操作 |
|---|---|---|
| 401 | 令牌过期 | 再次运行 `msgraph auth signin` |
| 403 | 权限不足 | 工具自动使用增量同意重试。如果仍然失败，用户需要管理员同意。 |
| 404 | 资源未找到 | 验证端点路径 |
| 429 | 速率限制 | 等待 Retry-After 持续时间，然后重试 |

## 环境变量

| 变量 | 描述 | 默认值 |
|---|---|---|
| `MSGRAPH_CLIENT_ID` | 自定义 Entra ID 应用程序客户端 ID | Microsoft Graph CLI 工具应用 |
| `MSGRAPH_TENANT_ID` | 目标租户 ID（仅应用程序需要） | `common` |
| `MSGRAPH_API_VERSION` | 默认 API 版本 | `beta` |
| `MSGRAPH_INDEX_DB_PATH` | OpenAPI 索引数据库路径 | 自动检测 |
| `MSGRAPH_SAMPLES_DB_PATH` | 示例索引数据库路径 | 自动检测 |
| `MSGRAPH_API_DOCS_DB_PATH` | API 文档索引数据库路径 | 自动检测 |
| `MSGRAPH_NO_TOKEN_CACHE` | 禁用持久令牌缓存（仅内存） | `false` |

有关所有身份验证环境变量的完整列表，请参阅 [references/docs/authentication.md](references/docs/authentication.md)。

## 兼容性

搜索工具完全离线运行，无需网络访问。直接 API 执行需要网络访问 `login.microsoftonline.com` 和 `graph.microsoft.com`。使用系统浏览器进行交互式身份验证；在无头环境中回退到设备代码流程。

## 参考文件

在需要特定指导时按需加载。切勿预先加载。

| 文件 | 何时阅读 | 大小 |
|---|---|---|
| [references/REFERENCE.md](references/REFERENCE.md) | 常见资源路径、OData 模式、权限范围 | ~230 行 |
| [references/docs/authentication.md](references/docs/authentication.md) | 详细身份验证配置：证书、托管身份、工作负载身份联合、所有环境变量 | ~200 行 |
| [references/docs/query-parameters.md](references/docs/query-parameters.md) | OData $select、$filter、$expand、$top、$orderby、$search 语法和注意事项 | ~300 行 |
| [references/docs/advanced-queries.md](references/docs/advanced-queries.md) | ConsistencyLevel 标头、$count、$search、目录对象上的 ne/not/endsWith | ~190 行 |
| [references/docs/paging.md](references/docs/paging.md) | @odata.nextLink 分页、服务器端与客户端分页 | ~50 行 |
| [references/docs/batching.md](references/docs/batching.md) | $batch 端点、组合多个请求、dependsOn 顺序 | ~280 行 |
| [references/docs/throttling.md](references/docs/throttling.md) | 429 处理、Retry-After、回退策略 | ~90 行 |
| [references/docs/errors.md](references/docs/errors.md) | HTTP 状态码、错误响应格式、错误代码 | ~105 行 |
| [references/docs/best-practices.md](references/docs/best-practices.md) | $select 用于性能、分页、增量查询、批处理 | ~155 行 |
