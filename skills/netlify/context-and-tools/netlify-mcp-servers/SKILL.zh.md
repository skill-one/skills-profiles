---
name: netlify-mcp-servers
description: 在 Netlify 上构建、部署和保障 Model Context Protocol (MCP) 服务器。每当任务涉及创建 MCP 服务器、将应用程序或 API 作为 MCP 工具暴露给 AI 代理、让 Claude / Cursor / Claude Code 调用自定义远程服务器，或向现有 Netlify 网站添加 MCP 工具时，均可使用。涵盖 MCP SDK + Streamable HTTP 传输在 Netlify Function 上的实现、认证（共享密钥与 Netlify Identity 的用户级 API 密钥）、读写安全、文件上传以及客户端连接。即使用户仅说“MCP”、“为代理创建工具服务器”或“让 AI 使用我的 API”时，也可使用。
---

# Netlify MCP 服务器

MCP 服务器会暴露**工具**（以及可选的资源/提示），AI 客户端（Claude Desktop、Claude Code、Cursor）可以调用这些工具。在 Netlify 上，一个远程 MCP 服务器只是一个在 HTTP 上使用 MCP 协议通信的**Netlify 函数**。这项技能会为你提供一个可工作、安全的服务器，并将客户端连接到它。

**"Netlify MCP" 意味着两件不同的事情——确保你正在构建正确的东西。** Netlify 发布了它自己的托管 MCP 服务器，允许 AI 客户端代表你在**Netlify 平台**上操作——创建项目、触发部署、管理环境变量和基础设施通过你的 Netlify 账户。你不需要编写这个；你根据 Netlify 的 MCP-server 文档将客户端指向 Netlify 的托管 MCP 服务器（并查看**netlify-agent-runner**技能来运行针对你站点的代理）。这项技能是另一件东西：构建**你自己的**MCP 服务器——一个暴露*你*应用的工具和数据的端点——托管在 Netlify 函数上。如果要求是“让我的代理管理我的 Netlify 网站/部署/环境变量”，那么那是托管的 Netlify MCP 服务器，而不是你编写的函数。

同样的设置有两种用法：

- **独立服务器**——一个只有 MCP 端点工作的仓库（例如，封装第三方 API）。
- **添加到现有应用**——与你的网站并列的一个更多函数。让它的工具调用**与你的 UI 和 REST 路由已经使用的相同服务/数据层**，这样逻辑就不会重复。

## 构建前

事先决定一件事，因为它会影响认证代码：

- **谁调用这个服务器？** 只有你（个人/单用户服务器）→ 使用**单个共享密钥**。多个人，各自以自己的身份行动 → 使用**按用户 API 密钥**，由 Netlify Identity 支持。参见 [认证](references/authentication.md)。

如果你不确定，从单个共享密钥开始——它只有几行，你可以稍后添加按用户密钥。除非你另有说明，否则我会默认使用这个。

## 技术栈

使用官方 MCP SDK 及其 Web 标准的 Streamable HTTP 传输，在 Netlify 函数中无状态运行。

```bash
npm install @modelcontextprotocol/sdk zod
```

Netlify 函数已经可以与 Web 平台通信——它接收一个 `Request` 并返回一个 `Response`。SDK 提供了一个基于这些原始数据的传输，`WebStandardStreamableHTTPServerTransport`（这是 SDK 内部使用的相同核心，也是 Cloudflare Workers / Deno / Bun 使用的）：你把它交给 `Request` 并返回它产生的 `Response`——不需要适配器，不需要版本固定。旧的指南会使用 Node 风味的 `StreamableHTTPServerTransport` 加上 `fetch-to-node` 桥接来合成 Node `req`/`res` 对象，它在 Netlify 上既不需要它们，跳过它们也更简单，并且在这里已被验证可以工作。

一个需要注意的地方，与所有这些无关：传输向任何缺少 *两者* 的 POST 的 `Accept` 头的 HTTP 返回 **406**：`application/json` 和 `text/event-stream`。这是一个 MCP 规格要求，客户端必须满足——406 表示修复客户端的 `Accept` 头，而不是服务器。让 SDK 拥有协议也意味着你不需要手动维护 JSON-RPC 帧定和协议版本握手。

## 服务器函数

有了 Web 标准传输，这只有几行——旧指南显示的大多数内容是 Node 桥接，你不需要它。把它放在 `netlify/functions/mcp.ts` 中：

```typescript
import type { Config, Context } from "@netlify/functions";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { WebStandardStreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js";
import { z } from "zod";
import { checkBearer } from "../lib/mcp/bearer"; // 参见认证

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

  // 新服务器 + 传输每个请求，没有会话要持久化。enableJsonResponse 返回一个 application/json 正文，而不是 SSE 流——这是合适的。
  const server = buildServer();
  const transport = new WebStandardStreamableHTTPServerTransport({
    sessionIdGenerator: undefined,
    enableJsonResponse: true,
  });

  // 交出 Web 请求，返回 Web 响应。传输拥有 JSON-RPC 帧定、正文解析（一个格式错误的正文会返回一个干净的 400），和握手。
  await server.connect(transport);
  return transport.handleRequest(req);
};

export const config: Config = { path: "/mcp" };
```

这是一个完整、可部署的服务器。其他一切都是工具、认证和安全。

## 基于浏览器的客户端和 CORS

Netlify 函数**不会**为你添加 CORS 头，上面的服务器对每个非 POST 方法返回 405——包括浏览器发送的 `OPTIONS` 预检。这对正常情况来说很好：原生 MCP 客户端（Claude Code、Cursor、Claude Desktop、`mcp-remote` 桥接）**不是**浏览器，它们不强制执行同源策略，所以它们不需要 CORS——这就是为什么那些客户端可以工作，而浏览器调用却不能的原因。

只有当你的 MCP 客户端在**浏览器**中运行时——一个调用服务器的跨域 Web 应用——才重要。然后浏览器会阻止请求，除非响应包含 `Access-Control-Allow-Origin`，并且它首先发送一个 `OPTIONS` 预检，必须返回 `2xx` 并带有 `Access-Control-Allow-Methods`（包括 `POST`）和 `Access-Control-Allow-Headers`（包括 `Authorization` 和 `Content-Type`）。浏览器控制台中“被 CORS 政策阻止：没有 Access-Control-Allow-Origin 头”错误就是这种情况——不是服务器损坏或平台错误。在函数本身中回答预检**之前** 405 检查，并在 POST 响应中重复 CORS 头：

```typescript
const CORS = {
  "Access-Control-Allow-Origin": Netlify.env.get("MCP_ALLOWED_ORIGIN") ?? "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Authorization, Content-Type, Mcp-Session-Id",
};

// 在处理器中，在 405 检查之前：
if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });
// ...然后拒绝其他非 POST 方法为 405，并将 CORS 添加到传输的 Response。
```

函数必须自己设置这些头——不要将浏览器 CORS 错误视为升级到 Netlify 或通过放宽认证来路由的问题。

## 定义工具

每个工具是一个 `name`、一个单行的 `description`、一个 `zod` 输入模式，以及一个返回 `{ content: [...] }` 的处理器。描述和参数 `.describe()` 文本是模型看到的唯一东西——像为代理编写 API 文档一样写：说明工具做什么，何时使用它，并指出任何不可逆的操作。

随着数量增加，给每个工具自己的模块，并在 `buildServer()` 中注册它们。具有许多工具的服务器通常会保留一个注册表（一个 `{ name, description, inputSchema, handler }` 数组）并一次连接 `tools/list` + `tools/call`——上面的传输设置无论哪种方式都是相同的。

## 认证

MCP 客户端必须证明它被允许调用你的服务器。每个请求都带有 `Authorization: Bearer <token>`；用 401 拒绝任何其他东西。

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
  // 首先进行长度检查，因为 timingSafeEqual 在长度不相等的缓冲区上会抛出（RangeError）。令牌是固定长度的，所以提前返回不会泄露任何有用的信息。
  return a.length === b.length && timingSafeEqual(a, b);
}
```

使用 `openssl rand -hex 32` 生成令牌，并将其存储为秘密环境变量。

**按用户 API 密钥**（多用户）。Netlify Identity 在一个 Web 界面中为每个用户铸造自己的密钥；你只存储每个密钥的**哈希**（从不存储明文）与该用户相关联，在每次请求上解析密钥以用户，并将该用户传递到你的工具处理器，以便工具作为正确的人行动。完整模式——模式、生成、哈希、吊销、解析用户——在 [认证](references/authentication.md) 中。

**从范围开始简单。** 最简单的模型是全有或全无：一个有效密钥可以调用属于它的用户的所有工具——通常是正确的起点。当出现具体需求时（例如，一个只读密钥），添加按密钥范围，如果应用确实需要它们，可以扩展到按工具范围或角色层。如果请求更完整的 RBAC 设计，请从简单的基线开始，并在其上分层范围，而不是一开始就处理完整层次结构。

## 安全和权限

工具是一个公开 API 交给一个自主代理。要深思熟虑：

- **只暴露完成工作所需的最少内容。** 将读取与写入分开，并在在暴露破坏性工具之前认真思考。一个常见、合理的做法是**完全省略删除工具**，并将破坏性行动保留在人类操作的 UI 中。
- **通过在工具的描述中添加明确指示来保护不可逆或公开的操作**——例如，“显示用户确切的文本并在发布前获取确认。” 这是一个软的、模型级别的保护，所以用你可以立即吊销的真实开关来支持它：一个你可以吊销的令牌。
- **将客户端的凭证与你的后端分离。** 客户端认证你的服务器（bearer/API 密钥）；你的服务器用它自己的秘密认证数据库或第三方 API。永远不要将你的后端神钥交给客户端。
- **使用最低权限后端凭证**——应用密码或范围令牌，而不是账户级别的，这样泄漏是可包含和可撤销的。
- **验证输入**（你的 `zod` 模式会这样做）并**记录每个工具调用**，以便你可以看到代理做了什么——`console.info` 会出现在 Netlify 函数日志中。

## 速率限制

MCP 服务器是一个自主代理可以紧密循环访问的公共端点——限制它。Netlify 函数有**内置的声明式速率限制**，所以不要手写计数器（一个实例化的内存计数器无论如何都不会跨函数实例保留——参见下一节）。将 `rateLimit` 块添加到函数的 `config` 导出中：

```typescript
export const config: Config = {
  path: "/mcp",
  rateLimit: {
    windowSize: 60,               // 时间窗口（秒）；最多 180
    windowLimit: 100,             // 每个窗口的最大请求
    aggregateBy: ["ip", "domain"], // 按 ip、domain 或两者分组
  },
};
```

超过限制时，平台默认返回 HTTP `429`（或设置 `action: "rewrite"` 并带有 `to` 路径将多余流量发送到专用页面）。函数速率限制**仅**存在于函数的 `config` 导出中——它们**不能**在 `netlify.toml` 中定义。

## 文件上传

当工具需要代理提供文件（要发布的图像、要附加的文档）时，不要将字节通过工具调用作为 base64 推送——它会增加模型的上下文大小并遇到有效载荷限制。相反，给代理一个短时效的、单用途的**预签名 URL**来 `PUT` 原始字节，将它们存储在 **Netlify Blobs** 中，并从你的其他工具通过一个稳定的密钥引用文件。使用**HMAC-SHA256**对上传 id、内容类型、大小和过期进行签名，以**秘密环境变量**为密钥，并在**常量时间内验证它**——签名就是授权，所以 `PUT` 不带 bearer 令牌。在上传端点，强制声明的内容类型和大小，并拒绝重放。完整的三步流程（`prepare_upload` → `PUT` → `finalize_upload`）和代码：[文件上传](references/file-uploads.md)。

## 请求之间状态不会存活

每个请求构建一个新鲜的服务器和传输，并且任何调用都可能落在**不同**的——或冷启动的——函数实例上。模块级内存不在实例之间共享，并且在冷启动之间不可持久。所以你需要持久化调用之间的状态**不能**存在于模块范围的 `Set`/`Map`/变量中：预签名上传上方的单次使用/重放跟踪、幂等性键、“已经处理了这个 id”保护、手动跟踪的按用户计数器。内存保护看起来在本地和一个热实例上正确，然后当另一个实例服务请求时，它会无声地让重放的上传通过（或双处理调用）。将这个状态保存在**持久化存储**中——Netlify Blobs 或你的数据库——以上传/请求 id 为键，并在那里检查和标记它。（这也是为什么服务器本身是无状态的，`sessionIdGenerator: undefined`。）

## 连接客户端

原生远程-MCP 支持现在是常态；只有在备用情况下才使用 `mcp-remote` 桥接。

- **Claude Code** — `claude mcp add --transport http my-mcp https://<site>.netlify.app/mcp --header "Authorization: Bearer <token>"`
- **Cursor** — 将服务器添加到 `mcp.json` 中，并带有 URL 和一个 `Authorization` 头。
- **Claude Desktop / claude.ai** — 添加一个**自定义连接器**（设置 → 连接器）。连接器是 OAuth 导向的；对于静态 bearer 服务器，`mcp-remote` 桥接是可靠的路径。
- **备用（旧版/仅 stdio 客户端）** — `npx mcp-remote https://<site>.netlify.app/mcp --header "Authorization: Bearer <token>"`

完整客户端矩阵和 OAuth / 自定义连接器深入探讨：[连接客户端](references/connecting-clients.md)。

## 本地开发和部署

- **运行它：** `netlify dev` 在 `http://localhost:8888/mcp` 上提供函数。
- **测试它：** MCP 检查器——`npx @modelcontextprotocol/inspector`——通过 Streamable HTTP 连接到你的 URL 并带有 `Authorization: Bearer` 头列出/调用工具。或者指向 `claude mcp add --transport http` 本地 URL。
- **身份问题：** Netlify Identity 在 `netlify dev` 下**不**工作，所以按用户密钥认证必须在部署预览上测试。参见**netlify-identity** 技能。
- **部署：** 推送到 Git，或 `netlify deploy --build --prod`。
- **秘密：** 将令牌/密钥作为环境变量设置（`netlify env:set MCP_BEARER_TOKEN <value> --secret`）——永远不要在代码中。

## 跨领域规则

- 永远不要硬编码秘密。将令牌、API 密钥和签名秘密存储为 Netlify 环境变量（将它们标记为秘密）。除了泄漏风险外，写入源代码（或任何构建发布的文件）的 bearer 令牌或签名秘密会触发**Netlify 的秘密扫描并导致部署失败**，即使构建其他方面是绿色的——修复方法是将它移动到秘密环境变量并在运行时使用 `Netlify.env.get(...)` 读取它，如果它被提交了，旋转令牌，*不是*禁用扫描器。参见**netlify-deploy** 以获取扫描控制。
- 在函数中，使用 `Netlify.env.get("VAR")` 读取环境变量，而不是 `process.env`。
- 将 `.netlify` 添加到 `.gitignore`。

## 相关技能和参考资料

- [认证](references/authentication.md) — 单一密钥与用户级 API 密钥（身份）的深入比较。
- [连接客户端](references/connecting-clients.md) — 完整客户端矩阵、OAuth 和自定义连接器。
- [文件上传](references/file-uploads.md) — 允许代理通过预签名 URL 上传图像/文件到 Netlify Blobs。
- **netlify-functions** — 函数语法、路由、限制。**netlify-identity** — 身份设置。**netlify-database** / **netlify-blobs** — 存储密钥和文件的位置。**netlify-deploy** — 部署。**netlify-config** — 环境变量。
