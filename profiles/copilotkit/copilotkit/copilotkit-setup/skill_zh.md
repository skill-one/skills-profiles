# CopilotKit 安装设置

## 前置条件

### 活动文档 (MCP)

此插件包含一个 MCP 服务器 (`copilotkit-docs`)，它提供 `search-docs` 和 `search-code` 工具，用于查询活动 CopilotKit 文档和源代码。

- **Claude 代码：** 由插件的 `.mcp.json` 自动配置 -- 无需设置。
- **Codex：** 需要手动配置。请参阅 [copilotkit-debug 技能](../copilotkit-debug/SKILL.md#mcp-setup) 获取设置说明。

### 环境

在开始设置之前，请验证：

1. **Node.js >= 18** (由运行时使用的 `fetch` 全局变量要求)
2. **AI 提供商 API 密钥** (以下之一：`OPENAI_API_KEY`、`ANTHROPIC_API_KEY`、`GOOGLE_API_KEY`)
3. **基于 React 的前端** (Next.js App Router、Next.js Pages Router、Vite + React 或 Angular)
4. **能够运行运行时的后端** (通过 API 路由的相同 Next.js 应用程序，或一个独立的 Express/Hono 服务器)

## 框架检测

在生成任何代码之前，通过检查项目根目录中的文件来检测项目的框架。有关完整的决策树，请参阅 `references/framework-detection.md`。

**简要总结：**

| 信号文件                                        | 框架            |
| -------------------------------------------------- | -------------------- |
| `next.config.{js,ts,mjs}` + `app/` 目录       | Next.js App Router   |
| `next.config.{js,ts,mjs}` + `pages/` 目录     | Next.js Pages Router |
| `angular.json`                                     | Angular              |
| `vite.config.{js,ts}` + package.json 中的 React 依赖 | Vite + React         |

## 设置工作流程

### 第 1 步：安装包

所有包都使用 `@copilotkit` 命名空间。v2 API 作为已发布包的子路径导出。

**前端和后端在同一 Next.js 应用程序中：**

```bash
npm install @copilotkit/react-core @copilotkit/runtime hono
```

**仅前端：**

```bash
npm install @copilotkit/react-core
```

**仅后端运行时：**

```bash
npm install @copilotkit/runtime hono
```

对于独立的 Express 后端，请安装 Express 适配器依赖项而不是 `hono`：

```bash
npm install @copilotkit/runtime express dotenv zod
npm install -D @types/express tsx typescript
```

(`createCopilotExpressHandler` 内部启用 CORS，因此您不需要自己安装 `cors`。`dotenv` 和 `zod` 由示例资源使用。)

### 第 2 步：选择运行时模式，然后配置运行时

运行时是管理代理执行的服务器端组件。有关详细信息，请参阅 `references/runtime-architecture.md`。

**在编写任何运行时代码之前决定模式。** 模式会改变运行时的构建方式，因此后期重构它意味着重写此文件。

| 模式                                   | 线程状态               | 选择它时                                                                     |
| -------------------------------------- | -------------------------- | ---------------------------------------------------------------------------------- |
| **管理智能** (推荐)                   | 持久、托管            | 您希望线程在重新启动后存活、托管入口、仪表板或 Channels |
| 自托管 SSE                        | 内存中、重新启动时丢失 | 您不想有托管依赖项，并且愿意自己拥有持久性    |

询问用户他们想要什么，默认为管理智能。明确说明先决条件，以便做出明智的选择：

**管理智能需要** CopilotKit 账户（免费；`npx copilotkit login` 打开浏览器）和项目 API 密钥。作为交换，线程在重新启动和部署之间是持久的，您会获得仪表板，Slack/Teams Channels 会变得可用 -- Channels 在 SSE 模式下完全不可用。

**自托管 SSE 需要** 超过 AI 提供商密钥的任何东西。线程状态存储在处理请求的进程的内存中，因此在重新启动时丢失，并且不会在副本之间共享。此技能中的所有内容在 SSE 模式下都有效；它是一个受支持的路径，而不是一个死胡同。

如果用户选择管理智能，请使用下面的智能运行时块，然后完成第 6 步。如果他们选择 SSE，请使用 SSE 块并跳过第 6 步的服务器端连接。

有两种端点样式：

1. **多路由 (Hono)** -- 使用 `createCopilotHonoHandler`。需要捕获所有路由 (`[[...slug]]` 在 Next.js 中)。每个操作（运行、连接、停止、信息、转录、线程）都获得自己的 HTTP 路径。
2. **单路由 (Hono 或 Express)** -- 使用 `createCopilotHonoHandler({ ..., mode: "single-route" })` 或 `createCopilotExpressHandler({ ..., mode: "single-route" })`。所有操作都通过单个 POST 端点进行，使用方法复用。

#### Next.js App Router (推荐：使用 Hono 的多路由)

创建 `src/app/api/copilotkit/[[...slug]]/route.ts`：

```typescript
import {
  CopilotRuntime,
  createCopilotHonoHandler,
  InMemoryAgentRunner,
  BuiltInAgent,
} from "@copilotkit/runtime/v2";
import { handle } from "hono/vercel";

const agent = new BuiltInAgent({
  model: "openai/gpt-4o",
  prompt: "You are a helpful AI assistant.",
});

const runtime = new CopilotRuntime({
  agents: {
    default: agent,
  },
  runner: new InMemoryAgentRunner(),
});

const app = createCopilotHonoHandler({
  runtime,
  basePath: "/api/copilotkit",
});

export const GET = handle(app);
export const POST = handle(app);
// PATCH/DELETE 由 thread operations (useThreads) 使用；导出它们，以便多路由处理器在启用 Intelligence/threads 时可以服务它们
export const PATCH = handle(app);
export const DELETE = handle(app);
```

#### Next.js App Router 与管理智能

相同的文件和相同的处理器，只有运行时构建不同。`intelligence` 是选择智能模式，`identifyUser` 在使用它时是必需的。

```typescript
import {
  CopilotRuntime,
  CopilotKitIntelligence,
  createCopilotHonoHandler,
  BuiltInAgent,
} from "@copilotkit/runtime/v2";
import { handle } from "hono/vercel";

const agent = new BuiltInAgent({
  model: "openai/gpt-4o",
  prompt: "You are a helpful AI assistant.",
});

const intelligence = new CopilotKitIntelligence({
  // 服务器端密钥。`apiUrl`/`wsUrl` 默认为 CopilotKit 的托管平台，因此大多数项目只设置密钥。
  apiKey: process.env.CPK_INTELLIGENCE_API_KEY!,
});

const runtime = new CopilotRuntime({
  agents: { default: agent },
  intelligence,
  // 在智能模式下必需：它决定这些线程属于谁。从请求中解析一个真实的认证用户 -- 使用硬编码的 id，每个访客共享一个线程历史记录。
  identifyUser: (request) => resolveUserFromSession(request),
});

const app = createCopilotHonoHandler({
  runtime,
  basePath: "/api/copilotkit",
});

export const GET = handle(app);
export const POST = handle(app);
export const PATCH = handle(app);
export const DELETE = handle(app);
```

需要注意的事项：

- **不要传递 `runner`。** 智能模式提供 `IntelligenceAgentRunner` 本身；传递 `InMemoryAgentRunner` 会导致线程保存在内存中。
- **`identifyUser` 不是可选的。** 它是线程所有权边界。像 `() => ({ id: "demo", name: "Demo" })` 这样的存根对于本地快速启动是好的，但对于任何多用户都是错误的。
- **`apiUrl` 和 `wsUrl` 是不同的主机。** 它们默认为 `https://api.intelligence.copilotkit.ai` 和 `wss://realtime.intelligence.copilotkit.ai`。实时平面不能通过交换方案从 API 平面派生，因此必须同时覆盖或都不覆盖 -- 覆盖其中一个会将两个平面指向不同的部署。

#### Next.js App Router (替代方案：单路由)

创建 `src/app/api/copilotkit/route.ts`：

```typescript
import {
  CopilotRuntime,
  createCopilotHonoHandler,
  InMemoryAgentRunner,
  BuiltInAgent,
} from "@copilotkit/runtime/v2";
import { handle } from "hono/vercel";

const agent = new BuiltInAgent({
  model: "openai/gpt-4o",
  prompt: "You are a helpful AI assistant.",
});

const runtime = new CopilotRuntime({
  agents: {
    default: agent,
  },
  runner: new InMemoryAgentRunner(),
});

const app = createCopilotHonoHandler({
  runtime,
  basePath: "/api/copilotkit",
  mode: "single-route",
});

export const POST = handle(app);
```

前端提供程序会自动协商此内容；仅在明确固定单路由传输时才设置 `useSingleEndpoint`（见第 3 步）。

#### 独立 Express 服务器

创建 `src/index.ts`：

```typescript
import express from "express";
import { CopilotRuntime, BuiltInAgent } from "@copilotkit/runtime/v2";
import { createCopilotExpressHandler } from "@copilotkit/runtime/v2/express";

const agent = new BuiltInAgent({
  model: "openai/gpt-4o",
});

const runtime = new CopilotRuntime({
  agents: {
    default: agent,
  },
});

const app = express();

app.use(
  "/api/copilotkit",
  createCopilotExpressHandler({
    runtime,
    basePath: "/",
    mode: "single-route",
  }),
);

const port = Number(process.env.PORT ?? 4000);
app.listen(port, () => {
  console.log(
    `CopilotKit runtime listening at http://localhost:${port}/api/copilotkit`,
  );
});
```

对于多路由 Express，省略 `mode` 选项（多路由是默认值）-- `createCopilotExpressHandler` 是两种样式的相同工厂（从 `@copilotkit/runtime/v2/express` 导入）。

#### 独立 Hono 服务器（非 Vercel）

```typescript
import {
  CopilotRuntime,
  createCopilotHonoHandler,
  BuiltInAgent,
} from "@copilotkit/runtime/v2";
import { serve } from "@hono/node-server";

const runtime = new CopilotRuntime({
  agents: {
    default: new BuiltInAgent({ model: "openai/gpt-4o" }),
  },
});

const app = createCopilotHonoHandler({
  runtime,
  basePath: "/api/copilotkit",
});

serve({ fetch: app.fetch, port: 8787 });
```

需要 `@hono/node-server`：

```bash
npm install hono @hono/node-server
```

### 第 3 步：设置前端提供程序

用 `@copilotkit/react-core/v2` 中的 `CopilotKit` 包裹您的应用程序。

> **使用哪个提供程序组件？** 始终使用从 `@copilotkit/react-core/v2` 导入的 `CopilotKit`。它是跨 v1 和 v2 的兼容性桥梁，并且是其他提供程序 API 的严格超集。**不要**使用从包根目录 (`@copilotkit/react-core`，遗留 v1) 或 `/v2` 中的 `CopilotKitProvider`（功能子集）。

**重要：** 在您的根布局中导入样式表：

```typescript
import "@copilotkit/react-core/v2/styles.css";
```

#### Next.js App Router

在 `src/app/page.tsx`（或客户端组件）中：

```tsx
"use client";

import { CopilotKit, CopilotChat } from "@copilotkit/react-core/v2";

export default function Home() {
  return (
    // 无 useSingleEndpoint：提供程序协商传输，因此它匹配上面的多路由后端（默认）或单路由后端。仅当故意固定一种模式时才传递此属性。
    <CopilotKit runtimeUrl="/api/copilotkit">
      <div style={{ height: "100vh" }}>
        <CopilotChat />
      </div>
    </CopilotKit>
  );
}
```

#### 连接到外部运行时

当运行时在单独的服务器上运行时（例如，端口 4000 上的 Express）：

```tsx
<CopilotKit runtimeUrl="http://localhost:4000/api/copilotkit" useSingleEndpoint>
  {children}
</CopilotKit>
```

省略 `useSingleEndpoint` 允许提供程序协商传输，这适用于任何处理器模式。将其设置为 `true` 仅当固定单路由传输（`createCopilotHonoHandler` 或 `createCopilotExpressHandler` 与 `mode: "single-route"`）时，或设置为 `false` 以固定多路由 REST 路由。

#### CopilotKit 关键属性

| 属性                | 类型                                                       | 描述                                                                                                          |
| ------------------- | ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `runtimeUrl`        | `string`                                                   | CopilotKit 运行时端点的 URL                                                                               |
| `useSingleEndpoint` | `boolean`                                                  | 省略以协商传输（适用于任何处理器模式）；`true` 固定单路由，`false` 固定多路由 |
| `headers`           | `Record<string, string> \| (() => Record<string, string>)` | 每个请求发送的自定义标头。函数形式按请求评估（用于动态身份验证令牌）。 |
| `credentials`       | `RequestCredentials`                                       | Fetch 凭据模式（例如，`"include"` 用于 cookies）                                                               |
| `showDevConsole`    | `boolean`                                                  | 显示开发控制台。省略它以获得默认行为（仅在 `localhost` 上显示）                                |
| `renderToolCalls`   | `ReactToolCallRenderer[]`                                  | 工具调用 UI 的自定义渲染器                                                                                    |
| `frontendTools`     | `ReactFrontendTool[]`                                      | 前端定义的工具（声明式替代 `useFrontendTool`）                                                                |
| `onError`           | `(event) => void`                                          | 全局错误处理程序                                                                                                 |

### 第 4 步：添加一个聊天 UI 组件

CopilotKit 提供三个预构建的聊天布局（全部从 `@copilotkit/react-core/v2` 导入）：

| 组件        | 用法                            |
| ---------------- | -------------------------------- |
| `CopilotChat`    | 内联聊天，填充其容器             |
| `CopilotSidebar` | 可折叠的侧边栏面板                |
| `CopilotPopup`   | 浮动的弹出小部件            |

使用侧边栏的示例：

```tsx
import { CopilotKit, CopilotSidebar } from "@copilotkit/react-core/v2";

<CopilotKit runtimeUrl="/api/copilotkit" useSingleEndpoint={false}>
  <YourApp />
  <CopilotSidebar
    defaultOpen
    width="420px"
    labels={{
      modalHeaderTitle: "AI 助手",
      chatInputPlaceholder: "问我任何问题...",
    }}
  />
</CopilotKit>;
```

### 第 5 步：设置环境变量

提供程序 API 密钥是机密。将它们存储在环境变量中 -- 永远不要在源代码中硬编码它们或将它们提交到版本控制。创建一个 `.env.local`（Next.js）或 `.env` 文件：

```
OPENAI_API_KEY=<your-openai-api-key>
```

确保您的 `.gitignore` 排除环境文件（`.env`、`.env.local`、`.env*.local`），这样密钥就不会被提交。在生产环境中，通过您平台的密钥管理器（Vercel/Netlify 环境变量、AWS Secrets Manager 等）提供密钥，而不是通过检查的文件。

`BuiltInAgent` 会根据模型前缀自动从这些环境变量中解析 API 密钥：

- `openai/*` 模型读取 `OPENAI_API_KEY`
- `anthropic/*` 模型读取 `ANTHROPIC_API_KEY`
- `google/*` 模型读取 `GOOGLE_API_KEY`

如果您需要显式传递 `apiKey`，请始终从环境变量中获取它（`apiKey: process.env.OPENAI_API_KEY`）-- 永远不要内联一个字面量密钥。

### 第 6 步：连接到 CopilotKit Intelligence

仅在用户在第 2 步中选择自托管 SSE 时才跳过此步骤。

Intelligence 只需要一个凭证，它是服务器端的。关于它，没有任何内容到达浏览器，并且没有提供程序属性配置它。

| 凭证                  | 存放位置 | 密码? | 目的                                   |
| --------------------------- | -------------- | ------- | ----------------------------------------- |
| 项目 API 密钥 (`cpk-...`) | 仅服务器     | **是** | 运行时向 Intelligence 进行身份验证 |

不要寻求 `publicApiKey` 或 `publicLicenseKey`。这些将一个没有运行时的客户端路由到 CopilotKit Cloud，这是一个不同的产品。

1. **登录并创建一个项目。**

   ```bash
   npx copilotkit login
   npx copilotkit project select
   ```

   `login` 打开浏览器并存储本地 CLI 会话。`project select` 选择或创建托管项目，并在 `.copilotkit/project.json` 中记录它。如果版本不同，请使用 `npx copilotkit --help` 验证可用的命令。

2. **设置服务器端项目 API 密钥。** `project select` 提供一个；你也可以从仪表板复制它。

   ```
   # .env.local (Next.js) 或 .env
   CPK_INTELLIGENCE_API_KEY=cpk-...
   ```

   这是一个密钥。它没有 `NEXT_PUBLIC_`/`VITE_` 前缀，这是故意为之的 -- 前缀会将它发送到浏览器。它由你在第 2 步中连接的 `CopilotKitIntelligence` 客户端读取。

   `CPK_INTELLIGENCE_API_KEY` 是规范名称——它是 `copilotkit project select` 提供的，并且是每个 CopilotKit 表面文档的。`COPILOTKIT_API_KEY` 是一个已弃用的别名，一些旧示例仍然读取它。

3. **确认接线。**

   ```bash
   npx copilotkit verify
   ```

   它报告项目是否已选择、密钥是否加载并认证、运行时是否实际使用凭证，以及运行时是否确实提供保存线程所需的线程路由。

4. **确认持久线程确实工作。** 发送一条消息，重新启动开发服务器，然后重新加载。线程应该仍然存在。如果不存在，运行时仍然处于 SSE 模式——检查 `intelligence` 是否传递，以及是否没有 `runner` 覆盖它。

有关 Intelligence 启用的内容、连接它的 CLI 流程以及如何选择退出，请参阅 `references/telemetry-setup.md`。

#### 连接到 Slack 或 Microsoft Teams

Channels 允许代理在 Slack 或 Teams 中回答。它们需要 Intelligence 运行时——`channels` 在 SSE 模式下不可用——并且需要一个长时间运行的托管实例，因为激活会打开一个持久连接。

使用 **copilotkit-channels** 技能。它涵盖了声明 Channel、长时间运行的托管要求，以及哪些挂载自行启动激活，哪些等待显式的 `channels.ready()` 调用。它建立在从本步骤继承的接线之上。

对于新的托管 Teams 应用程序，首先在 Intelligence 中创建 Channel 草稿，然后使用推荐的浏览器颁发的 Fast CLI 命令 (`channels add --project-id … --channel-id … --adapter teams --provision`) 或对等的 Guided 手动路径。不要创建 Azure Bot 资源、放置 Microsoft 凭证、自定义图标或生成的包在项目中。提供程序的 **Created and installed** 结果与代码部分是分开的；只有运行的托管实例加上真实的 Teams 交互才能端到端验证集成。

### 第 7 步：验证设置

1. 启动开发服务器
2. 在浏览器中打开应用程序
3. 聊天 UI 应该渲染并连接到运行时
4. 发送一条测试消息——你应该收到一个 AI 响应
5. 检查运行时的信息端点以确认它报告可用的代理。对于多路由处理器，这是 `GET /api/copilotkit/info`；对于单路由处理器（`mode: "single-route"`，例如 Express 示例）是基本路径的 POST 请求，正文为 `{ "method": "info" }`（普通的 GET 不会返回代理信息——Hono 单路由处理器回答 `405`，并且 Express 单路由路由器没有 `GET` 路由，因此会回落到 `404`）

## 安全注意事项

在您将真实部署接线的整个过程中，请记住以下几点：

- **密钥保持服务器端和环境变量中。** 提供程序 API 密钥 (`OPENAI_API_KEY` 等) 由服务器上的运行时/代理读取。永远不要将它们暴露给浏览器、硬编码它们或提交它们——将它们存储在环境变量或密钥管理器中（见第 5 步）。CopilotKit Intelligence 添加不了客户端价值：它的凭证在服务器上的运行时读取。
- **将所有聊天输入视为不受信任。** 聊天消息从前端流经 `CopilotRuntime` 端点进入代理的 LLM 上下文。它们是用户控制的，并且可以尝试提示注入——包括通过代理获取的内容（网页、文档、工具结果）的间接注入。不要假设模型只会做你系统提示意图的事情。
- **为服务器端工具提供最低权限。** `defineTool` 的 `execute` 函数以您服务器的权限运行。验证每个参数（`zod` `parameters` 模式是您的第一个关卡），将每个工具的范围限制在它需要的最窄操作，并在 `execute` 函数中执行您自己的授权，而不是信任模型正确调用它。
- **对运行时端点进行身份验证。** 运行时路由默认是公共 HTTP 端点。将您应用程序的身份验证放在它前面，以便只有授权用户才能驱动代理并消耗提供程序积分。

## 快速参考

### 包映射

| 包                  | 目的                                                                                                         |
| ------------------------ | --------------------------------------------------------------------------------------------------------------- |
| `@copilotkit/react-core` | React 组件、钩子、提供程序（从 `@copilotkit/react-core/v2` 导入）                                     |
| `@copilotkit/runtime`    | 运行时、端点工厂、代理运行器、`BuiltInAgent`、`defineTool` (从 `@copilotkit/runtime/v2` 导入) |
| `@copilotkit/shared`     | 共享实用程序、日志记录器、类型                                                                                 |

### 端点工厂函数

| 函数                      | 导入                           | 框架                           | 模式                                                |
| ----------------------------- | -------------------------------- | ----------------------------------- | --------------------------------------------------- |
| `createCopilotHonoHandler`    | `@copilotkit/runtime/v2`         | Next.js App Router, Hono standalone | `"multi-route"` (默认) 或 `mode: "single-route"` |
| `createCopilotExpressHandler` | `@copilotkit/runtime/v2/express` | Express standalone                  | `"multi-route"` (默认) 或 `mode: "single-route"` |

> `createCopilotEndpoint`、`createCopilotEndpointSingleRoute`、`createCopilotEndpointExpress` 和 `createCopilotEndpointSingleRouteExpress` 的名称是上面两个工厂的已弃用别名。优先使用带有 `mode` 选项的处理器工厂。

### 运行时类

| 类                        | 用法                                                       |
| ---------------------------- | -------------------------------------------------------------- |
| `CopilotRuntime`             | 兼容性桥接；自动选择 SSE 或 Intelligence 模式      |
| `CopilotSseRuntime`          | 显式 SSE 模式 (默认，内存中线程)                 |
| `CopilotIntelligenceRuntime` | Intelligence 模式 (持久线程、实时事件、Channels) |

Channels 需要Intelligence 运行时和一个长时间运行的托管实例。请参阅
**copilotkit-channels** 技能。

### 代理运行器

| 运行器                    | 描述                                                                                               |
| ------------------------- | --------------------------------------------------------------------------------------------------------- |
| `InMemoryAgentRunner`     | 默认。将线程状态存储在进程内存中。适用于开发和单实例部署。 |
| `IntelligenceAgentRunner` | 自动与 `CopilotIntelligenceRuntime` 使用。通过 WebSocket 连接到 CopilotKit Intelligence.  |

### 支持的模型 (BuiltInAgent)

格式：`"provider/model-name"` 字符串或 Vercel AI SDK `LanguageModel` 实例。

**OpenAI:** `openai/gpt-5`, `openai/gpt-5-mini`, `openai/gpt-4.1`, `openai/gpt-4.1-mini`, `openai/gpt-4.1-nano`, `openai/gpt-4o`, `openai/gpt-4o-mini`, `openai/o3`, `openai/o3-mini`, `openai/o4-mini`

**Anthropic:** `anthropic/claude-sonnet-4-6`, `anthropic/claude-sonnet-4-5`, `anthropic/claude-opus-4-8`, `anthropic/claude-haiku-4-5`

**Google:** `google/gemini-2.5-pro`, `google/gemini-2.5-flash`, `google/gemini-2.5-flash-lite`

任何 `string` 都被接受（用于自定义/未列出模型）；在 `/` 之前解析提供程序。
