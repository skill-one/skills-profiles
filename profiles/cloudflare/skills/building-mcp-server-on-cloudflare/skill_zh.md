# 在 Cloudflare 上构建 MCP 服务器

您对 MCP SDK 和 Cloudflare Workers 集成的了解可能已经过时了。**对于任何 MCP 服务器任务，请优先考虑检索而非预训练**。

## 检索来源

| 来源 | 检索方式 | 用途 |
|------|----------|------|
| MCP 文档 | `https://developers.cloudflare.com/agents/mcp/` | 服务器设置、认证、部署 |
| MCP 规范 | `https://modelcontextprotocol.io/` | 协议规范、工具/资源定义 |
| Workers 文档 | 搜索工具或 `https://developers.cloudflare.com/workers/` | 运行时 API、绑定、配置 |

## 使用场景

- 用户想要构建一个远程 MCP 服务器
- 用户需要通过 MCP 暴露工具
- 用户询问关于 MCP 认证或 OAuth 的问题
- 用户想要将 MCP 部署到 Cloudflare Workers

## 前置条件

- 带有启用 Workers 的 Cloudflare 账户
- Node.js 18+ 以及 npm/pnpm/yarn
- Wrangler CLI (`npm install -g wrangler`)

## 快速入门

### 选项 1：公开服务器（无认证）

```bash
npm create cloudflare@latest -- my-mcp-server \
  --template=cloudflare/ai/demos/remote-mcp-authless
cd my-mcp-server
npm start
```

服务器运行在 `http://localhost:8788/mcp`

### 选项 2：认证服务器（OAuth）

```bash
npm create cloudflare@latest -- my-mcp-server \
  --template=cloudflare/ai/demos/remote-mcp-github-oauth
cd my-mcp-server
```

需要设置 OAuth 应用。参见 [references/oauth-setup.md](references/oauth-setup.md)。

## 核心工作流

### 第 1 步：定义工具

工具是 MCP 客户端可以调用的函数。使用 `server.tool()` 定义它们：

```typescript
import { McpAgent } from "agents/mcp";
import { z } from "zod";

export class MyMCP extends McpAgent {
  server = new Server({ name: "my-mcp", version: "1.0.0" });

  async init() {
    // 简单带参数的工具
    this.server.tool(
      "add",
      { a: z.number(), b: z.number() },
      async ({ a, b }) => ({
        content: [{ type: "text", text: String(a + b) }],
      })
    );

    // 调用外部 API 的工具
    this.server.tool(
      "get_weather",
      { city: z.string() },
      async ({ city }) => {
        const response = await fetch(`https://api.weather.com/${city}`);
        const data = await response.json();
        return {
          content: [{ type: "text", text: JSON.stringify(data) }],
        };
      }
    );
  }
}
```

### 第 2 步：配置入口点

**公开服务器** (`src/index.ts`)：

```typescript
import { MyMCP } from "./mcp";

export default {
  fetch(request: Request, env: Env, ctx: ExecutionContext) {
    const url = new URL(request.url);
    if (url.pathname === "/mcp") {
      return MyMCP.serveSSE("/mcp").fetch(request, env, ctx);
    }
    return new Response("MCP Server", { status: 200 });
  },
};

export { MyMCP };
```

**认证服务器** — 参见 [references/oauth-setup.md](references/oauth-setup.md)。

### 第 3 步：本地测试

```bash
# 启动服务器
npm start

# 在另一个终端中，使用 MCP Inspector 测试
npx @modelcontextprotocol/inspector@latest
# 打开 http://localhost:5173，输入 http://localhost:8788/mcp
```

### 第 4 步：部署

```bash
npx wrangler deploy
```

服务器可在 `https://[worker-name].[account].workers.dev/mcp` 访问

### 第 5 步：连接客户端

**Claude 桌面版** (`claude_desktop_config.json`)：

```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["mcp-remote", "https://my-mcp.workers.dev/mcp"]
    }
  }
}
```

更新配置后重启 Claude 桌面版。

## 工具模式

### 返回类型

```typescript
// 文本响应
return { content: [{ type: "text", text: "result" }] };

// 多个内容项
return {
  content: [
    { type: "text", text: "Here's the data:" },
    { type: "text", text: JSON.stringify(data, null, 2) },
  ],
};
```

### 使用 Zod 进行输入验证

```typescript
this.server.tool(
  "create_user",
  {
    email: z.string().email(),
    name: z.string().min(1).max(100),
    role: z.enum(["admin", "user", "guest"]),
    age: z.number().int().min(0).optional(),
  },
  async (params) => {
    // params 完全类型化并验证
  }
);
```

### 访问环境/绑定

```typescript
export class MyMCP extends McpAgent<Env> {
  async init() {
    this.server.tool("query_db", { sql: z.string() }, async ({ sql }) => {
      // 访问 D1 绑定
      const result = await this.env.DB.prepare(sql).all();
      return { content: [{ type: "text", text: JSON.stringify(result) }] };
    });
  }
}
```

## 认证

对于受 OAuth 保护的服务器，参见 [references/oauth-setup.md](references/oauth-setup.md)。

支持的提供者：
- GitHub
- Google
- Auth0
- Stytch
- WorkOS
- 任何符合 OAuth 2.0 的提供者

## Wrangler 配置

最小的 `wrangler.toml`：

```toml
name = "my-mcp-server"
main = "src/index.ts"
compatibility_date = "2024-12-01"

[durable_objects]
bindings = [{ name = "MCP", class_name = "MyMCP" }]

[[migrations]]
tag = "v1"
new_classes = ["MyMCP"]
```

带绑定（D1、KV 等）：

```toml
[[d1_databases]]
binding = "DB"
database_name = "my-db"
database_id = "xxx"

[[kv_namespaces]]
binding = "KV"
id = "xxx"
```

## 常见问题

### 客户端中显示“工具未找到”

1. 验证工具名称是否完全匹配（区分大小写）
2. 确保 `init()` 在连接前注册工具
3. 检查服务器日志：`wrangler tail`

### 连接失败

1. 确认端点路径是 `/mcp`
2. 如果是浏览器客户端，检查 CORS
3. 验证 Worker 是否已部署：`wrangler deployments list`

### OAuth 重定向错误

1. 回调 URL 必须与 OAuth 应用配置完全匹配
2. 检查 `GITHUB_CLIENT_ID` 和 `GITHUB_CLIENT_SECRET` 是否已设置
3. 本地开发时，使用 `http://localhost:8788/callback`

## 参考

- [references/examples.md](references/examples.md) — 官方模板和生产示例
- [references/oauth-setup.md](references/oauth-setup.md) — OAuth 提供者配置
- [references/tool-patterns.md](references/tool-patterns.md) — 高级工具示例
- [references/troubleshooting.md](references/troubleshooting.md) — 错误代码和修复
