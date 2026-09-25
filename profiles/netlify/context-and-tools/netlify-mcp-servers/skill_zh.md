# Netlify MCP 服务器

MCP 服务器会暴露**工具**（以及可选的资源/提示），AI 客户端（如 Claude Desktop、Claude Code、Cursor）可以调用这些工具。在 Netlify 上，一个远程 MCP 服务器就是一个会通过 HTTP 说话 MCP 协议的**Netlify 函数**。这项技能会为你提供一个可工作、安全的服务器，并将客户端连接到它。

**"Netlify MCP" 意味着两件不同的事情——确保你正在构建正确的那一个。** Netlify 发布了它自己的托管 MCP 服务器，允许 AI 客户端代表你操作 **Netlify 平台**——创建项目、触发部署、管理环境变量和基础设施，通过你的 Netlify 账户。你不需要编写这个；你应按照 Netlify 的 MCP-server 文档将客户端指向 Netlify 的托管 MCP 服务器（并查看 **netlify-agent-runner** 技能来运行针对你站点的代理）。这项技能是另一件事：构建你自己的 MCP 服务器——一个暴露你应用工具和数据的端点——托管在 Netlify 函数上。如果要求是“让我的代理管理我的 Netlify 网站/部署/环境变量”，那应该是托管在 Netlify 的 MCP 服务器，而不是你编写的函数。

同样的设置有两种用法：

- **独立服务器**——一个只有 MCP 端点工作的仓库（例如，封装第三方 API）。
- **添加到现有应用**——与你的站点并列的一个额外函数。让它的工具调用你 UI 和 REST 路由已经使用的**相同服务/数据层**，这样逻辑就不会重复。

## 构建前准备

事先确定一件事，因为它会决定认证代码：

- **谁调用这个服务器？** 只有你（个人/单用户服务器）→ 使用**单个共享密钥**。多个人，各自以自己的身份行动 → 使用**按用户分发的 API 密钥**，由 Netlify Identity 支持。参见 [认证](references/authentication.md)。

如果你不确定，可以从单个共享密钥开始——它只有几行代码，你可以在以后添加按用户密钥。除非你另有说明，否则我会默认使用这个。

## 技术栈

使用官方的 MCP SDK 及其 Web 标准的 Streamable HTTP 传输，在 Netlify 函数中无状态运行。

```bash
npm install @modelcontextprotocol/sdk zod
```

Netlify 函数已经会讲 Web 平台——它接收一个 `Request` 并返回一个 `Response`。SDK 提供了一个基于这些原始数据的传输 `WebStandardStreamableHTTPServerTransport`（这是 SDK 内部使用的相同核心，也是 Cloudflare Workers / Deno / Bun 使用的）：你把它交给 `Request` 并返回它产生的 `Response`——不需要适配器，不需要版本固定。旧的指南会使用 Node 风味的 `StreamableHTTPServerTransport` 加上 `fetch-to-node` 桥接器来合成 Node 的 `req`/`res` 对象，它在 Netlify 上既不需要这些，跳过它们也更简单，并且在这里已被验证可行。

一个需要注意的地方，与所有这些无关：传输会对任何缺少 `application/json` 和 `text/event-stream` 的 `Accept` 头的 POST 请求返回 **HTTP 406**。这是一个 MCP 规范要求客户端必须满足的——406 表示需要修复客户端的 `Accept` 头，而不是服务器。让 SDK 拥有协议也意味着你不需要手动维护 JSON-RPC 帧或协议版本握手。

## 服务器函数

有了 Web 标准传输，这只有几行代码——旧指南显示的大部分内容是 Node 桥接器，你不需要它。把它放在 `netlify/functions/mcp.ts` 中：

```typescript
import type { Config, Context } from "@netlify/functions";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { WebStandardStreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js";
import { z } from "zod";
import { checkBearer } from "../lib/mcp/bearer"; // 见认证

function buildServer() {
  const server = new McpServer({ name: "my-mcp", version: "0.1.0" });

  server.tool(
    "get_item",
    "通过 id 获取单个项目。只读。",
    { id: z.string().describe("项目的唯一 id") },
    async ({ id }) => ({
      content: [{ type: "text", text: JSON.stringify(await getItem(id)) }],
    }),
  );

  return server;
}

export default async (req: Request, _context: Context) => {
  if (!checkBearer(req)) return new Response("Unauthorized", { status: 401 });

  // 无状态 JSON 服务器：它只通过 POST 做请求/响应。拒绝其他方法——GET 会使传输打开一个永不关闭的 SSE 流，无状态函数无法服务（你会得到 502）。
  if (req.method !== "POST") return new Response("Method not allowed", { status: 405 });

  // 每次请求都创建一个新鲜的服务器和传输，任何调用都可能落在**不同的**——或冷启动的——函数实例上。模块级内存不在实例之间共享，也不在冷启动之间持久化。所以你需要在调用之间持久化状态**不能**存放在模块范围的 `Set`/`Map`/变量中：上面 presigned 上传的单一使用/重放跟踪、幂等性键、已处理此 id 的保护、手动跟踪的按用户计数器。内存保护在本地和单个热实例上看起来是正确的，但一旦另一个实例服务请求，它就会无声地让重放上传通过（或重复处理调用）。将这种状态保存在**持久化存储**中——Netlify Blobs 或你的数据库——键由上传/请求 id，并在那里检查和标记。（这也是为什么服务器本身是无状态的，`sessionIdGenerator: undefined`。）

  // 新鲜服务器 + 传输，没有会话要持久化。enableJsonResponse 返回一个 application/json 正文，而不是 SSE 流——这是这里的合适选择。
  const server = buildServer();
  const transport = new WebStandardStreamableHTTPServerTransport({
    sessionIdGenerator: undefined,
    enableJsonResponse: true,
  });

  // 交出 Web 请求，返回 Web 响应。传输拥有 JSON-RPC 帧和正文解析（一个格式错误的正文会返回一个干净的 400），以及握手。
  await server.connect(transport);
  return transport.handleRequest(req);
};

export const config: Config = { path: "/mcp" };
```

这是一个完整、可部署的服务器。其他所有内容都是工具、认证和安全。

## 基于浏览器的客户端和 CORS

Netlify 函数不会为你添加 CORS 头，上面的服务器会对每个非 POST 方法返回 405——包括浏览器发送的 `OPTIONS` 预检。对于正常情况这是没问题的：原生 MCP 客户端（Claude Code、Cursor、Claude Desktop、`mcp-remote` 桥接器）**不是**浏览器，它们不强制同源策略，所以它们不需要 CORS——这就是为什么那些客户端可以工作，而浏览器调用却不能的原因。

只有当你的 MCP 客户端在**浏览器**中运行时——一个调用服务器的跨域 Web 应用——才重要。然后浏览器会阻止请求，除非响应包含 `Access-Control-Allow-Origin`，并且它首先发送一个 `OPTIONS` 预检，必须返回 `2xx` 并包含 `Access-Control-Allow-Methods`（包括 `POST`）和 `Access-Control-Allow-Headers`（包括 `Authorization` 和 `Content-Type`）。浏览器控制台中的“被 CORS 政策阻止：没有 Access-Control-Allow-Origin 头”错误就是这种情况——不是服务器损坏或平台错误。在函数本身中回答预检，**在** 405 检查之前，并在 POST 响应中重复 CORS 头：

```typescript
const CORS = {
  "Access-Control-Allow-Origin": Netlify.env.get("MCP_ALLOWED_ORIGIN") ?? "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Authorization, Content-Type, Mcp-Session-Id",
};

// 在处理器中，在 405 检查之前：
if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });
// ...然后拒绝其他非 POST 方法返回 405，并在传输的 Response 中添加 CORS。
```

函数必须自己设置这些头——不要将浏览器 CORS 错误视为需要升级到 Netlify 或通过放宽认证来路由的问题。

## 定义工具

每个工具是一个 `name`、一个单行 `description`、一个 `zod` 输入模式，以及一个返回 `{ content: [...] }` 的处理器。描述和参数 `.describe()` 文本是模型唯一看到的东西——像为代理编写 API 文档一样编写它们：说明工具做什么，何时使用它，并指出任何不可逆的内容。

随着数量增加，给每个工具自己的模块，并在 `buildServer()` 中注册它们。具有许多工具的服务器通常会保留一个注册表（一个 `{ name, description, inputSchema, handler }` 数组）并一次连接 `tools/list` + `tools/call`——上面的传输设置无论哪种方式都是相同的。

## 认证

MCP 客户端必须证明它被允许调用你的服务器。每个请求都带有 `Authorization: Bearer <token>`；用 401 拒绝任何其他内容。

**单个共享密钥**（个人/单用户）。一个环境变量，以常量时间进行比较。把它放在 `netlify/lib/mcp/bearer.ts` 中：

```typescript
import { timingSafeEqual } from "node:crypto";

export function checkBearer(req: Request): boolean {
  const expected = Netlify.env.get("MCP_BEARER_TOKEN");
  if (!expected) return false;
  const match = req.headers.get("authorization")?.match(/^Bearer\s+(.+)$/i);
  if (!match) return false;
  const a = Buffer.from(match[1]);
  const b = Buffer.from(expected);
  // 首先进行长度检查，因为 timingSafeEqual 在长度不等的缓冲区上会抛出（RangeError）。令牌是固定长度的，所以提前返回不会泄露任何有用的信息。
  return a.length === b.length && timingSafeEqual(a, b);
}
```

用 `openssl rand -hex 32` 生成令牌，并将其作为秘密环境变量存储。

**按用户分发的 API 密钥**（多用户）。Netlify Identity 控制一个 Web UI，每个用户都可以铸造自己的密钥；你只存储每个密钥的**哈希**（从不存储明文），并将其与该用户关联，在每次请求上解析密钥以用户，并将该用户传递到你的工具处理器，以便工具作为正确的人行动。完整模式——模式、生成、哈希、撤销、解析用户——在 [认证](references/authentication.md) 中。

**从范围开始简单。** 最简单的模型是全有或全无：一个有效的密钥可以调用属于它的用户的所有工具——这通常是合适的起点。当出现具体需求时（例如，一个只读密钥），添加按密钥范围，如果应用确实需要它们，则扩展到按工具范围或角色层。如果请求更完整的 RBAC 设计，请从简单的基线开始，并在其上分层范围，而不是一开始就处理完整层次结构。

## 安全和权限

工具是一个公开 API，交给一个自主代理。要深思熟虑：

- **只暴露能完成工作的最少内容。** 将读取与写入分开，并在暴露破坏性工具之前认真思考。一个常见、合理的做法是**完全省略删除工具**，并将破坏性行动保留在人类操作的 UI 中。
- **通过在工具描述中添加明确指示来保护不可逆或公开行动**——例如，“在发布之前向用户显示确切文本并获取确认。”这是一种软的、模型级别的保护，所以要有一个真正的关闭开关：一个你可以立即撤销的令牌。
- **将客户端的凭证与你的后端分离。** 客户端向你服务器认证（bearer/API 密钥）；你的服务器用它自己的秘密向数据库或第三方 API 认证。永远不要将你的后端神钥交给客户端。
- **使用最低权限后端凭证**——应用密码或范围令牌，而不是账户级令牌，这样泄漏会被限制并可撤销。
- **验证输入**（你的 `zod` 模式会这样做）并**记录每个工具调用**，以便你可以看到代理做了什么——`console.info` 会出现在 Netlify 函数日志中。

## 速率限制

MCP 服务器是一个自主代理可以紧密循环调用的公开端点——限制它。Netlify 函数有**内置的声明式速率限制**，所以不要手工制作计数器（在函数实例之间不会持久的内存计数器——见下一节）。在函数的 `config` 导出中添加一个 `rateLimit` 块：

```typescript
export const config: Config = {
  path: "/mcp",
  rateLimit: {
    windowSize: 60,               // 时间窗口（秒）；最多 180
    windowLimit: 100,             // 每个窗口的最大请求量
    aggregateBy: ["ip", "domain"], // 按 ip、domain 或两者分组
  },
};
```

超过限制时平台默认返回 HTTP `429`（或设置 `action: "rewrite"` 并带有 `to` 路径将多余流量发送到专用页面）。函数速率限制**仅**存在于函数的 `config` 导出中——它们**不能**在 `netlify.toml` 中定义。

## 文件上传

当工具需要代理提供文件（例如要发布的图像、要附加的文档）时，不要将字节作为 base64 推过工具调用——它会增加模型的上下文大小并遇到有效载荷限制。相反，给代理一个短时效、单用的**预签名 URL**来 `PUT` 原始字节，将它们存储在 **Netlify Blobs** 中，并从你其他的工具通过一个稳定的键来引用文件。用**HMAC-SHA256**对上传 id、内容类型、大小和过期进行签名，键由一个**秘密环境变量**，并在上传端点**以常量时间验证它**——签名就是授权，所以 `PUT` 不带 bearer 令牌。在上传端点，强制声明的内容类型和大小，并拒绝重放。完整的三步流程（`prepare_upload` → `PUT` → `finalize_upload`）和代码：[文件上传](references/file-uploads.md)。

## 请求之间状态不会存活

每次请求都会构建一个新鲜的服务器和传输，任何调用都可能落在**不同的**——或冷启动的——函数实例上。模块级内存不在实例之间共享，也不在冷启动之间持久化。所以你需要在调用之间持久化状态**不能**存放在模块范围的 `Set`/`Map`/变量中：上面 presigned 上传的单一使用/重放跟踪、幂等性键、“已处理此 id”保护、手动跟踪的按用户计数器。内存保护在本地和单个热实例上看起来是正确的，但一旦另一个实例服务请求，它就会无声地让重放上传通过（或重复处理调用）。将这种状态保存在一个**持久化存储**中——Netlify Blobs 或你的数据库——键由上传/请求 id，并在那里检查和标记。（这也是为什么服务器本身是无状态的，`sessionIdGenerator: undefined`。）

## 连接客户端

原生远程-MCP 支持现在已是常态；仅在后备情况下才使用 `mcp-remote` 桥接器。

- **Claude Code** — `claude mcp add --transport http my-mcp https://<site>.netlify.app/mcp --header "Authorization: Bearer <token>"`
- **Cursor** — 将服务器添加到 `mcp.json` 中，提供 URL 和一个 `Authorization` 头。
- **Claude Desktop / claude.ai** — 添加一个**自定义连接器**（设置 → 连接器）。连接器是 OAuth 导向的；对于静态 bearer 服务器，`mcp-remote` 桥接器是可靠路径。
- **后备（旧版/仅 stdio 客户端）** — `npx mcp-remote https://<site>.netlify.app/mcp --header "Authorization: Bearer <token>"`

完整客户端矩阵和 OAuth / 自定义连接器深入探讨：[连接客户端](references/connecting-clients.md)。

## 本地开发和部署

- **运行它：** `netlify dev` 在 `http://localhost:8888/mcp` 上提供函数。
- **测试它：** MCP 检查器——`npx @modelcontextprotocol/inspector`——通过 Streamable HTTP 连接到你的 URL 并带有 `Authorization: Bearer` 头列出/调用工具。或者将 `claude mcp add --transport http` 指向本地 URL。
- **身份问题：** Netlify Identity 在 `netlify dev` 下**不工作**，所以按用户密钥认证必须在部署预览上测试。参见 **netlify-identity** 技能。
- **部署：** 推送到 Git，或 `netlify deploy --build --prod`。
- **秘密：** 将令牌/密钥作为环境变量设置（`netlify env:set MCP_BEARER_TOKEN <value> --secret`）——永远不要在代码中。
