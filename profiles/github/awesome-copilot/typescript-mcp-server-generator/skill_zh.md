# 生成 TypeScript MCP 服务器

使用 **MCP TypeScript SDK v2** 按照以下规范创建完整的模型上下文协议 (MCP) 服务器：

## 要求

1. **项目结构**：创建具有正确目录结构的 TypeScript/Node.js 项目
2. **NPM 包**：v1 单体 `@modelcontextprotocol/sdk` 包已停用。使用 v2 的聚焦包：
   - `@modelcontextprotocol/server` — 服务器实现（通过 `@modelcontextprotocol/server/stdio` 子路径的 stdio 传输）
   - `@modelcontextprotocol/node` — Node HTTP 传输 (`NodeStreamableHTTPServerTransport`), 或框架适配器：`@modelcontextprotocol/express`, `@modelcontextprotocol/hono`, `@modelcontextprotocol/fastify` — 每个适配器都需要与其配套框架一起安装（例如 `@modelcontextprotocol/express` + `express`）
   - `@modelcontextprotocol/core` — 共享协议模式（从这里导入 `*Schema` 常量，而不是从 `sdk/types.js` 导入）
   - `zod@^4.2` — v2 需要 Zod 4.2+；不要使用 zod@3
3. **运行时**：Node.js 20+（v2 最小要求）；ESM 首选，package.json 中 `"type": "module"`（也附带 CommonJS 构建，因此如果需要 `require()` 也有效）
4. **服务器类型**：选择 HTTP（流式 HTTP 传输）或基于 stdio 的服务器。v2 中已移除 SSE 和 WebSocket 传输 — 不要生成它们。
5. **工具**：创建至少一个具有正确模式验证的有用工具
6. **错误处理**：包含全面的错误处理和验证

## 实现细节

### 项目设置
- 使用 `npm init` 初始化并创建 package.json
- 安装依赖项：`@modelcontextprotocol/server`, `zod@^4.2`，以及传输包 — `@modelcontextprotocol/node` 用于纯 Node HTTP，或框架适配器与其配套框架一起（例如 `npm install @modelcontextprotocol/express express`）
- 使用 ES 模块配置 TypeScript：package.json 中的 `"type": "module"`
- 添加 dev 依赖项：`tsx` 或 `ts-node` 用于开发
- 创建正确的 .gitignore 文件

### 服务器配置
- 使用 `@modelcontextprotocol/server` 中的 `McpServer` 类进行高级实现
- 设置服务器名称和版本
- 选择适当的传输：
  - HTTP (Node): 来自 `@modelcontextprotocol/node` 的 `NodeStreamableHTTPServerTransport`
  - HTTP (Web 标准运行时): 来自 `@modelcontextprotocol/server` 的 `WebStandardStreamableHTTPServerTransport`
  - stdio: 来自 `@modelcontextprotocol/server/stdio` 的 `StdioServerTransport`
- 对于 HTTP：优先使用框架适配器（`@modelcontextprotocol/express` 等）配合适当的中间件和错误处理
- 注意 v2 使用 Web 标准 `Headers`/`Request` 类型；使用 `ctx.http?.req?.headers.get('x-custom')` 读取头部

### 工具实现
- 使用 `registerTool()` 配置对象 — v1 可变参数 `.tool()` 签名已消失：
  ```typescript
  server.registerTool('greet', {
    description: '问候用户',
    inputSchema: z.object({ name: z.string() })
  }, async ({ name }, ctx) => {
    return { content: [{ type: 'text', text: `Hello, ${name}!` }] };
  });
  ```
- 模式必须是完整的 Zod 对象 (`z.object({...})`) — 原始形状对象 (`{ name: z.string() }`) 已弃用
- 提供 `title` 和 `description` 字段
- 在结果中返回 `content` 和 `structuredContent`
- 处理器的第二个参数是结构化的 `ctx` 对象（替换 v1 `extra`）：`ctx.mcpReq.signal`, `ctx.mcpReq.id`, `ctx.mcpReq.send(...)`, `ctx.mcpReq.notify(...)`
- 使用 try-catch 块实现适当的错误处理；使用 v2 错误层次结构（`ProtocolError`, `SdkError`, `SdkHttpError` 带有 `.status`）而不是 v1 `McpError`/`StreamableHTTPError`
- 在适当的地方支持异步操作

### 资源/提示设置（可选）
- 使用 `registerResource()` 配合 ResourceTemplate 添加资源以实现动态 URI
- 使用 `registerPrompt()` 配合参数模式（与 `registerTool()` 相同的配置对象样式）
- 考虑添加完成支持以改善用户体验；注意 v2 `completable()` 包装器顺序：`completable(z.string(), callback).optional()`（可选应用在外部）

### 代码质量
- 使用 TypeScript 进行类型安全
- 一致遵循 async/await 模式
- 在传输关闭事件上实现适当的清理
- 使用环境变量进行配置
- 为复杂逻辑添加行内注释
- 使用清晰的关注点分离结构化代码

## 值得考虑的示例工具类型
- 数据处理和转换
- 外部 API 集成
- 文件系统操作（读取、搜索、分析）
- 数据库查询
- 文本分析或摘要（通过多轮 `input_required` 模式 LLM 辅助）
- 系统信息检索

## 配置选项
- **对于 HTTP 服务器**：
  - 通过环境变量配置端口
  - 为浏览器客户端设置 CORS
  - 会话管理（无状态 vs 有状态）
  - 本地服务器的 DNS 反向绑定保护
  - 严格的 `Content-Type` 处理：v2 拒绝非 `application/json` 的 POST 正文
  
- **对于 stdio 服务器**：
  - 适当的 stdin/stdout 处理
  - 基于环境的配置
  - 进程生命周期管理

## 迁移现有 v1 服务器
- 首先运行官方 codemod：`npx @modelcontextprotocol/codemod@latest v1-to-v2 .`
- 然后搜索 `@mcp-codemod-error` 标记以进行需要人工判断的部分（传输选择、头部读取、错误分类）
- 交换 `McpError + ErrorCode` 检查以使用新的错误类；HTTP 状态现在存在于 `error.status`，而不是 `error.code`
- `Server.createMessage()`, `listRoots()`, `sendLoggingMessage()` 以及 `roots`/`sampling`/`logging` 能力字段在 v2 中已弃用 — 新代码中避免使用它们

## 测试指南
- 说明如何运行服务器（`npm start` 或 `npx tsx server.ts`）
- 提供 MCP Inspector 命令：`npx @modelcontextprotocol/inspector`
- 对于 HTTP 服务器，包括连接 URL：`http://localhost:PORT/mcp`
- 包括示例工具调用
- 添加常见问题的故障排除提示

## 值得考虑的附加功能
- 使用多轮 `input_required` 模式的 LLM 工具（v2 替代已弃用的采样子系统）
- 用户输入提示以实现交互式工作流
- 动态工具注册与启用/禁用功能
- 批量更新的通知去抖动
- 资源链接以高效引用数据

生成一个完整的、生产就绪的 MCP 服务器，包含全面的文档、类型安全和错误处理。
