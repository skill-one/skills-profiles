## 兄弟技能（仅本地）

兄弟 CloudBase 技能将与此技能一起提供。使用本地相对路径，例如 `../auth-tool-cloudbase/SKILL.md`。

如果此环境中缺少引用的兄弟技能文件，请要求用户安装完整的 CloudBase 插件（或缺失的技能）。不要将远程技能或协议 Markdown 通过 HTTP 获取到代理上下文中。

**跨领域协议**（代码更改或部署之前需要）：
- 更改安全协议：`../cloudbase-platform/references/protocols/change-safety-protocol.md`
- 部署网关：`../cloudbase-platform/references/protocols/deployment-gate.md`
- 敏感运行时数据保护：`../cloudbase-platform/references/protocols/sensitive-runtime-data-protection.md`

# Cloud Functions 开发

## 激活合同

### 首次使用时

- 任务是创建、更新、部署、检查或调试 CloudBase 事件函数或 HTTP 函数，该函数用于应用程序运行时逻辑。
- 请求中提到函数运行时、函数日志、`scf_bootstrap`、函数触发器或函数网关暴露。

### 写代码之前需要阅读

- 您仍然需要在事件函数和 HTTP 函数之间做出选择。
- 任务提到 `manageFunctions`、`queryFunctions`、`manageGateway` 或旧函数工具名称。
- 任务可能需要 `callCloudApi` 作为日志或网关设置的回退。
- HTTP 函数将通过 `@cloudbase/node-sdk` 或 `@cloudbase/manager-node` 调用 CloudBase 资源，请阅读 `./references/http-function-credentials.md`。HTTP 函数必须使用显式凭证；不要依赖事件函数的无密码运行时路径。

### 仅例外（默认不阅读）

- 迁移现有的应用程序，该应用程序已经使用经典 TCP 数据库客户端（`DATABASE_URL` / Prisma / `mysql2` / `pg` / Redis）→ 通过 `./references.md` 阅读 `./references/vpc-and-tcp-database.md`。新的业务 CRUD 必须优先使用 CloudBase 原生 SDK（`app.database()` / `app.rdb()`）或 MCP SQL 工具，而不是 TCP。

### 然后还需要阅读

- 详细参考路由 -> `./references.md`
- 认证设置或提供程序相关的后端工作 -> `../auth-tool-cloudbase/SKILL.md`
- CloudBase 集成中心生成的微信支付或公众号函数 -> `../cloudbase-wechat-integration/SKILL.md`（官方文档：`https://docs.cloudbase.net/integration/introduce.md`）
- 函数中的 AI -> `../ai-model-nodejs/SKILL.md`
- 长寿命容器服务或 Agent 运行时 -> `../cloudrun-development/SKILL.md`
- 从客户端或脚本调用 CloudBase 官方平台 API -> `../http-api-cloudbase/SKILL.md`

### 不要用于

- CloudRun 容器服务。
- Web 认证 UI 实现。
- 数据库模式设计或一般数据模型工作。
- CloudBase 官方平台 API 客户端或仅消费平台端点的原始 HTTP 集成。
- 通过猜测 API 创建集成中心实例。对于微信支付或公众号生成的函数，使用 `cloudbase-wechat-integration` 作为业务合同，仅使用此技能进行函数操作。
- **CloudBase JS SDK 可以直接处理的任务** — 简单的数据读取/写入、排行榜、文件上传、实时查询。在编写函数之前，先使用匹配的 SDK 界面：`db.collection(...).get/add/update` 仅用于确认 NoSQL 集合，并且 `app.rdb().from(...)` 用于 CloudBase PG 表。函数会增加部署复杂性、CORS 配置和 HTTP 网关绑定，而 SDK 完全消除了这些。

### 常见错误/注意事项

- 选择错误的函数类型并试图事后弥补。
- 混淆官方 CloudBase API 客户端工作与构建自己的 HTTP 函数。
- 混合事件函数代码结构（`exports.main(event, context)`）与 HTTP 函数代码结构（`req` / `res` 在端口 `9000` 上）。
- 将 HTTP Access 视为 HTTP 函数的实现模型。HTTP Access 是事件函数的网关配置，而不是 HTTP 函数的运行时模型。
- 假设 `db.collection("name").add(...)` 将自动创建缺失的文档数据库集合。集合创建是一个单独的管理步骤。
- 忘记创建后无法更改运行时。
- 将云函数作为 Web 登录的第一答案。
- 忘记 HTTP 函数必须提供 `scf_bootstrap`、监听端口 `9000` 并包含依赖项。
- 假设 HTTP 函数可以使用 CloudBase SDK 而无需显式凭证。默认的临时凭证路径对 HTTP 函数不可靠，凭证轮换可能会中断正在运行的服务。使用 CloudBase 服务器 API 密钥或腾讯云密钥对为 `@cloudbase/node-sdk`；使用腾讯云密钥对为 `@cloudbase/manager-node`。参见 `references/http-function-credentials.md`。
- 创建 HTTP 函数后忘记配置函数安全规则。默认规则拒绝匿名调用者，带有 `EXCEED_AUTHORITY`。注意：新环境默认禁用匿名登录 — 如果函数需要无需认证的公共访问，请配置安全规则以允许所有调用者，而不是依赖匿名登录。
- 混淆 `scf_bootstrap` Node.js 二进制路径与函数运行时（例如，使用 `/var/lang/node18/bin/node` 但设置 `runtime: "Nodejs16.13"`）。
- 对于自定义图像 HTTP 函数：忘记 TCR、CloudApp 构建 和 SCF 必须在同一区域；使用 `:latest` 而不是唯一标签；或将请求驱动的端口-`9000` 图像模型与监听注入 `PORT` 的长寿命 CloudRun 容器混淆。
- 假设 MCP 覆盖整个图像管道。`manageFunctions` 通过 `runtime: "CustomImage"` + `imageConfig` 覆盖 SCF 图像部署（阶段 B），但 CloudApp 自定义构建 → TCR 推送（阶段 A）是一个原始腾讯云 API 路径 — 在任何 `callCloudApi` 回退之前，请从官方文档确认操作名称和参数。
- 在遵循更改安全协议（`cloudbase-platform/references/protocols/change-safety-protocol.md`）之前，不要进行代码或配置更改。
- 在完成 `cloudbase-platform/references/protocols/deployment-gate.md` 中的检查之前，不要公开函数或部署。
- **整块返回 `req.headers`、`process.env`、`event` 或 `context`** — 网关可能会注入 `x-cloudbase-context`（base64 临时凭证）。永远不要回显该头部或将凭证环境变量输出到客户端。遵循 `../cloudbase-platform/references/protocols/sensitive-runtime-data-protection.md`。
- **跨环境使用裸层名称（例如 `common`）**。SCF 层名称是一个帐户范围的共享命名空间：相同名称 → 共享版本序列。使用固定格式的 `{layerName}_{当前envId}` 创建新层（例如 `common_cloud1-d9ghadgak3edf6b36`）。将完整名称作为 `layerName` 传递 — 不要发明自动后缀。将 MCP 层 `warnings` 视为软建议（操作仍然成功）。详细信息：`./references/operations-and-config.md`。
- **长寿命 MCP 图像部署必须完成完整的工作流程**：当使用 `manageFunctions` 与 `deployFunction` 进行真实的 `cloud` 或 `local` 部署时，优先使用 `wait=false` 以避免长时间阻塞单个 Tool Call。如果工具返回 `taskId`，请不要结束工作流程，报告成功，或要求用户等待状态为 `running` 时。自动调用 `queryFunctions(action="getFunctionDeployStatus", taskId="...")` 并根据报告的进度继续轮询，直到状态变为 `succeeded` 或 `failed`。只有在达到合理的轮询限制后，您才能报告部署仍在进行中；包括 `taskId`、当前状态、当前阶段和最新进度。成功后，报告图像 URI 或构建 ID、函数状态和网关 URL。失败时，报告失败阶段、错误代码、请求 ID 和诊断步骤。如果状态是 `expired`，解释本地任务记录超出了保留窗口；云部署可能仍在运行，因此调用 `getFunctionDetail` 以确认实际的云端状态，而不是将其视为失败。

### 最小清单

- 部署或运行时更改之前，请阅读 [Cloud Functions 执行清单](checklist.md)。
- 确定任务是否为事件函数、HTTP 函数或实际上是 CloudRun。
- 在编写实现代码之前，选择 [references.md](references.md) 中的详细参考文件。

## MCP 图像部署与轮询

对于真实的 `cloud` 或 `local` 自定义图像部署，请优先使用：

```json
{
  "action": "deployFunction",
  "dryRun": false,
  "confirm": true,
  "wait": false,
  "deployConfig": {}
}
```

`wait` 字段控制当前 MCP Tool 调用是否等待完整部署：

- `wait=true`：等待管理器部署达到终端结果并返回它。
- `wait=false`：立即返回 `taskId`，同时部署在 MCP 背景中继续。

当 `wait=false` 返回 `taskId` 时，部署工作流程并不完整。自动调用 `queryFunctions` 并使用 `action="getFunctionDeployStatus"` 和该 `taskId`；继续轮询，直到状态为 `running`，然后仅在 `succeeded` 或 `failed` 时停止。在第一次后续查询之前等待大约 5 秒，并使用返回的进度/`nextActions` 继续轮询，不要进行激进轮询。在终端状态返回之前，不要告诉用户再次询问或暗示成功。`expired` 状态意味着任务超出了最大保留窗口并被本地强制终止 — 云部署可能仍在运行，因此使用 `getFunctionDetail` 确认实际状态，而不是报告失败。

如果达到合理的轮询限制，请仅报告任务仍在运行，包括 `taskId`、当前状态、当前阶段和最新进度。对于终端结果，报告部署策略、操作、图像 URI/摘要、构建 ID、函数状态和网关 URL，或失败阶段、错误代码、请求 ID 和下一步诊断。

### 个人层级 TCR 凭证 — 永远不要将密码放在工具参数中

个人层级图像构建（`imageConfig.imageType="personal"` 与 `local` / `cloud`）需要一个 TCR 推送凭证。从 MCP 进程环境读取，而不是从工具参数读取：

- 当 `TCB_TCR_USERNAME` 和 `TCB_TCR_PASSWORD` 在 MCP 服务器 `env` 块中设置时，将 `func.imageConfig.build.registryCredential` **从请求中排除** — MCP 会自动填充它们，就像 `TENCENTCLOUD_SECRETID` 一样。
- **永远不要要求用户将密码粘贴到聊天中，也永远不要将其写入工具参数。** 放在参数中的任何内容都会进入模型上下文和工具调用历史。
- 如果部署失败，显示 `CLOUD_REGISTRY_CREDENTIAL_MISSING` 或 `CLOUD_REGISTRY_CREDENTIAL_INVALID`，请指示用户将这两个变量添加到其 MCP 配置的 `env` 块中并重新启动 MCP 服务器。不要通过内联传递凭证来解决这个问题。
- 用户名是腾讯云帐户 UIN，本身不是秘密；如果需要，可以显式传递。显式参数按字段优先，因此用户名-参数加上从环境获取的密码是一个有效的组合。

**知道环境通道不存在的时间。** 它仅适用于本地 stdio MCP 服务器，其客户端配置暴露了自定义 `env` 块。某些 GUI 客户端不会继承 shell 导出，并且 IDE 嵌入的 MCP 服务器通常从硬编码的允许列表中注入凭证（通常只有 `TENCENTCLOUD_*`），让用户无法设置任意变量。告诉那些用户“在 MCP `env` 块中设置它”是一个他们无法执行的指令。将他们路由到企业注册表（`imageType="enterprise"`，它生成一个短命的 TCR 令牌，而不是使用固定密码）或 `buildStrategy="image"` 与已推送的图像。

### 企业层级构建需要具有 CAM 权限的登录状态

针对企业注册表的 `cloud` / `local` 构建通过 CAM 生成 TCR 令牌（`autoGrant` 也是这样）。环境级 API 密钥和 OAuth 发布的 STS 凭证不携带 CAM 策略，因此这些调用会显示 `UnauthorizedOperation`。MCP 在开始真正的企业构建之前会探测登录状态并 upfront 拒绝；将此错误视为路由信号，而不是可重试的故障：

- 使用帐户级别的 `TENCENTCLOUD_SECRETID` / `TENCENTCLOUD_SECRETKEY` 对进行登录，**或者**
- 切换到 `buildStrategy="image"` 并部署一个在别处推送的图像，**或者**
- 使用个人层级注册表 — 其静态密码直接传递给 `docker login` 而不接触 CAM，这使得它是 API 密钥用户可以工作的唯一构建路径。
