# Base44 编码器

使用 Base44 JavaScript SDK 在 Base44 平台上构建应用程序。

## ⚡ 立即采取行动 - 首先阅读此内容

当提及 "base44" 或存在 `base44/` 文件夹时，此技能将激活。**在采取行动之前，请勿阅读文档文件或搜索网络。**

**您的第一个行动必须是：**
1. 检查当前目录中是否存在 `base44/config.jsonc`
2. 如果 **是**（现有项目场景）：
   - 此技能（base44-sdk）将处理请求
   - 使用 Base44 SDK 实现功能
   - 除非用户明确要求 CLI 命令，否则**不要**使用 base44-cli
3. 如果 **否**（新项目场景）：
   - 转移到 base44-cli 技能进行项目初始化
   - 此技能在项目初始化之前无法提供帮助

## 何时使用此技能与 base44-cli

**使用 base44-sdk 时：**
- 在**现有**的 Base44 项目中构建功能
- 项目中已存在 `base44/config.jsonc`
- 存在 Base44 SDK 导入（`@base44/sdk`）
- 使用 JavaScript/TypeScript 代码编写 Base44 SDK 模块
- 实现功能、组件或特性
- 用户提及："实现"、"构建功能"、"添加功能"、"为...编写代码"
- 用户说 "创建一个 [类型] 应用"**并且**已存在 Base44 项目

**不要使用 base44-sdk：**
- ❌ 初始化新的 Base44 项目（请使用 `base44-cli`）
- ❌ 空目录且没有 Base44 配置
- ❌ 用户说 "创建一个新的 Base44 项目/应用/网站" 且不存在项目
- ❌ CLI 命令，如 `npx base44 create`、`npx base44 deploy`、`npx base44 login`（请使用 `base44-cli`）

**技能依赖关系：**
- `base44-sdk` 假设 Base44 项目**已初始化**
- `base44-cli` 是 `base44-sdk` 在新项目中的**先决条件**
- 如果用户想要 "创建应用" 且不存在 Base44 项目，请首先使用 `base44-cli`

**状态检查逻辑：**
在选择此技能之前，请验证：
- IF (用户提及 "创建/构建应用" 或 "创建项目")：
  - IF (目录为空 或 不存在 `base44/config.jsonc`)：
    → 使用 **base44-cli**（需要项目初始化）
  - ELSE：
    → 使用 **base44-sdk**（项目存在，构建功能）

## 快速入门

```javascript
// 在 Base44 生成的应用中，base44 客户端已预配置并可用

// CRUD 操作
const task = await base44.entities.Task.create({ title: "新任务", status: "pending" });
const tasks = await base44.entities.Task.list();
await base44.entities.Task.update(task.id, { status: "done" });

// 获取当前用户
const user = await base44.auth.me();
```

```javascript
// 外部应用
import { createClient } from "@base44/sdk";

// 重要提示：使用 'appId'（不要使用 'clientId' 或 'id'）
const base44 = createClient({ appId: "your-app-id" });
await base44.auth.loginViaEmailPassword("user@example.com", "password");
```

## ⚠️ 关键：不要凭空想象 API

**在编写任何 Base44 代码之前，请对照此表格或 [QUICK_REFERENCE.md](references/QUICK_REFERENCE.md) 验证方法名称。**

Base44 SDK 具有独特的方法名称。**不要**假设来自 Firebase、Supabase 或其他 SDK 的模式。

### 认证 - 错误与正确

| ❌ 错误（凭空想象） | ✅ 正确 |
|-------------------|--------|
| `signInWithGoogle()` | `loginWithProvider('google')` |
| `signInWithProvider('google')` | `loginWithProvider('google')` |
| `auth.google()` | `loginWithProvider('google')` |
| `signInWithEmailAndPassword(email, pw)` | `loginViaEmailPassword(email, pw)` |
| `signIn(email, pw)` | `loginViaEmailPassword(email, pw)` |
| `createUser()` / `signUp()` | `register({email, password})` |
| `onAuthStateChanged()` | `me()`（无需监听，按需调用） |
| `currentUser` | `await auth.me()` |

### 函数 - 错误与正确

| ❌ 错误（凭空想象） | ✅ 正确 |
|-------------------|--------|
| `functions.call('name', data)` | `functions.invoke('name', data)` |
| `functions.run('name', data)` | `functions.invoke('name', data)` |
| `callFunction('name', data)` | `functions.invoke('name', data)` |
| `httpsCallable('name')(data)` | `functions.invoke('name', data)` |

### 集成 - 错误与正确

| ❌ 错误（凭空想象） | ✅ 正确 |
|-------------------|--------|
| `ai.generate(prompt)` | `integrations.Core.InvokeLLM({prompt})` |
| `openai.chat(prompt)` | `integrations.Core.InvokeLLM({prompt})` |
| `llm(prompt)` | `integrations.Core.InvokeLLM({prompt})` |
| `sendEmail(to, subject, body)` | `integrations.Core.SendEmail({to, subject, body})` |
| `email.send()` | `integrations.Core.SendEmail({to, subject, body})` |
| `uploadFile(file)` | `integrations.Core.UploadFile({file})` |
| `storage.upload(file)` | `integrations.Core.UploadFile({file})` |

> **例外：** 当指向 `base44.aiGateway.connection()` 的 OpenAI 兼容客户端（例如 Vercel AI SDK）是正确的——那是构建代码代理（代理循环与工具）的方式。仅用于无工具的单次调用时使用 `InvokeLLM`。参见 [ai-gateway.md](references/ai-gateway.md)。

### 实体 - 错误与正确

| ❌ 错误（凭空想象） | ✅ 正确 |
|-------------------|--------|
| `actors.connect('ChatRoom', roomId)` | `actors.ChatRoom(roomId).connect()` |
| `actors.ChatRoom.connect(roomId)` | `actors.ChatRoom(roomId).connect()` |
| `actors.ChatRoom(roomId).subscribe(cb)` | 在连接上订阅（`const conn = actors.ChatRoom(roomId).connect(); conn.subscribe(cb)`） |
| `room.on('message', cb)` | `room.subscribe(cb)`（一个回调接收每条消息） |
| `room.emit(data)` | `room.send(data)` |
| `new WebSocket(...)` 用于应用实时 | `base44.actors.<Name>(id).connect()` |
| `const unsub = room.subscribe(cb); unsub()` | `const sub = room.subscribe(cb); sub.unsubscribe()` |

> **两种 `subscribe()` 方法返回不同形状。** `Connection.subscribe()`（实体）返回一个对象——`sub.unsubscribe()`。`entities.<Name>.subscribe()` 返回取消订阅的**函数本身**——`unsub()`。不要将一种约定带到另一种约定中。

### 实体 - 错误与正确

| ❌ 错误（凭空想象） | ✅ 正确 |
|-------------------|--------|
| `entities.Task.find({...})` | `entities.Task.filter({...})` |
| `entities.Task.findOne(id)` | `entities.Task.get(id)` |
| `entities.Task.insert(data)` | `entities.Task.create(data)` |
| `entities.Task.remove(id)` | `entities.Task.delete(id)` |
| `entities.Task.onChange(cb)` | `entities.Task.subscribe(cb)` |

## SDK 模块

| 模块 | 目的 | 参考 |
|------|------|------|
| `entities` | 对数据模型进行 CRUD 操作 | [entities.md](references/entities.md) |
| `auth` | 登录、注册、用户管理 | [auth.md](references/auth.md) |
| `agents` | AI 对话和消息 | [base44-agents.md](references/base44-agents.md) |
| `functions` | 后端函数调用 | [functions.md](references/functions.md) |
| `actors` | 基于 WebSockets 的实时房间（多人、协作、在线状态） | [actors.md](references/actors.md) |
| `integrations` | AI、电子邮件、文件上传、自定义 API | [integrations.md](references/integrations.md) |
| `aiGateway` | 将 OpenAI 兼容 SDK 连接到 Base44 的 AI 网关 | [ai-gateway.md](references/ai-gateway.md) |
| `analytics` | 跟踪自定义事件和用户活动 | [analytics.md](references/analytics.md) |
| `appLogs` | 记录应用中的用户活动 | [app-logs.md](references/app-logs.md) |
| `users` | 邀请用户加入应用 | [users.md](references/users.md) |
| `asServiceRole.connectors` | 应用范围的 OAuth 令牌（仅服务角色） | [connectors.md](references/connectors.md) |
| `asServiceRole.sso` | SSO 令牌生成（仅服务角色） | [sso.md](references/sso.md) |

有关客户端设置和认证模式，请参阅 [client.md](references/client.md)。

### TypeScript 和类型注册表

每个参考文件都包含一个 "类型定义" 部分与 TypeScript 接口和类型，用于模块的方法、参数和返回值。

**获取带类型的实体、函数、实体和代理：** Base44 CLI 从您的项目资源（实体、函数、实体、代理）生成类型，包括对 `EntityTypeRegistry`、`FunctionNameRegistry`、`ActorNameRegistry` 和 `AgentNameRegistry` 的增强，并将它们连接到您的项目中，以便您无需手动设置即可获得自动完成和类型检查。有关如何生成类型的说明，请使用 **base44-cli** 技能。

**手动增强：** 您也可以在 `.d.ts` 文件中自行增强注册表；参见 [entities.md](references/entities.md)、[functions.md](references/functions.md)、[actors.md](references/actors.md) 和 [base44-agents.md](references/base44-agents.md) 中的类型定义部分。实体的**消息**类型始终是手动编写的——增强 `ActorRegistry` 以使实体及其客户端共享一个定义。

## 安装

安装 Base44 SDK：

```bash
npm install @base44/sdk
```

**重要提示：** 始终不指定版本号来安装，以获取最新版本。

## 创建客户端（外部应用）

在创建外部应用的客户端时，**始终使用 `appId` 作为参数名称**：

```javascript
import { createClient } from "@base44/sdk";

// ✅ 正确
const base44 = createClient({ appId: "your-app-id" });

// ❌ 错误 - 不要使用这些：
// const base44 = createClient({ clientId: "your-app-id" });  // 错误
// const base44 = createClient({ id: "your-app-id" });        // 错误
```

**必需参数：** `appId`（字符串）- 您的 Base44 应用程序 ID

**可选参数：**
- `token`（字符串）- 预认证用户令牌
- `options`（对象）- 配置选项
  - `options.onError`（函数）- 全局错误处理程序

**带错误处理器的示例：**
```javascript
const base44 = createClient({
  appId: "your-app-id",
  options: {
    onError: (error) => {
      console.error("Base44 错误:", error);
    }
  }
});
```

## 模块选择

**处理应用数据？**
- 创建/读取/更新/删除记录 → `entities`
- 从文件导入数据 → `entities.importEntities()`
- 实时更新 → `entities.EntityName.subscribe()`

**用户管理？**
- 登录/注册/登出 → `auth`
- 获取当前用户 → `auth.me()`
- 更新用户资料 → `auth.updateMe()`
- 邀请用户 → `users.inviteUser()`

**AI 功能？**
- 与 AI 代理聊天 → `agents`（需要登录用户）
- 创建新对话 → `agents.createConversation()`
- 管理对话 → `agents.getConversations()`
- 使用 AI 生成文本/JSON → `integrations.Core.InvokeLLM()`
- 生成图像 → `integrations.Core.GenerateImage()`
- 使用工具构建自定义代理（后端、AI 网关上的代理 SDK）→ `aiGateway`（参见 [ai-gateway.md](references/ai-gateway.md)）

**自定义后端逻辑？**
- 运行服务器端代码 → `functions.invoke()`
- 需要管理员访问 → `base44.asServiceRole.functions.invoke()`

**实时共享会话？**
- 多人、协作板/文档、在线状态、实时光标、房间内聊天 → `actors.<Name>(roomId).connect()`（参见 [actors.md](references/actors.md)）
- 仅在屏幕上保持记录列表实时更新 → `entities.EntityName.subscribe()`，**不是**实体

**外部服务？**
- 发送电子邮件 → `integrations.Core.SendEmail()`
- 上传文件 → `integrations.Core.UploadFile()`
- 自定义 API → `integrations.custom.call()`
- 应用范围的 OAuth（应用构建者的帐户）→ `asServiceRole.connectors.getConnection()`（仅后端）

**跟踪和分析？**
- 跟踪自定义事件 → `analytics.track()`
- 记录页面视图/活动 → `appLogs.logUserInApp()`

## 常见模式

### 过滤和排序数据

```javascript
const pendingTasks = await base44.entities.Task.filter(
  { status: "pending", assignedTo: userId },  // 查询
  "-created_date",                             // 排序（降序）
  10,                                          // 限制
  0                                            // 跳过
);
```

### 受保护的路由（检查认证）

```javascript
const user = await base44.auth.me();
if (!user) {
  // 导航到您的自定义登录页面
  navigate('/login', { state: { returnTo: window.location.pathname } });
  return;
}
```

### 后端函数调用

```javascript
// 前端
// ⚠️ invoke() 返回原始 axios 响应——您的函数的 JSON 在 `.data` 中，
//    不是顶层对象。它还在非 2xx 时抛出（错误体在 err.response.data）。
const res = await base44.functions.invoke("processOrder", {
  orderId: "123",
  action: "ship"
});
const result = res.data; // ✅ e.g. res.data.success  (res 本身是 { data, status, headers, … })

// 后端函数
import { createClientFromRequest } from "npm:@base44/sdk";

export default async function (req) {
  const base44 = createClientFromRequest(req);
  const { orderId, action } = await req.json();
  // 使用服务角色进行管理员访问
  const order = await base44.asServiceRole.entities.Orders.get(orderId);
  return Response.json({ success: true });
}
```

### 实时房间（实体）

```javascript
// 前端——在 useEffect 中连接并始终清理
useEffect(() => {
  const room = base44.actors.ChatRoom(roomId).connect();
  const sub = room.subscribe((msg) => {
    if (msg.type === "message") setMessages((prev) => [...prev, msg]);   // 根据类型切换；丢弃未知项
  });
  return () => { sub.unsubscribe(); room.close(); };   // 注意：实体返回 { unsubscribe() },
}, [roomId]);                                          // entities.subscribe() 返回取消订阅的函数本身

// 实体——base44/actors/ChatRoom/entry.ts
import { Actor } from "base44:runtime/actors";

export default class ChatRoom extends Actor {
  handleConnect(conn) { conn.send({ type: "welcome" }); }        // 一个客户端
  handleMessage(conn, msg) {
    // 始终验证：有效载荷是攻击者控制的，msg 甚至可能为 null。
    if (msg?.type !== "message" || typeof msg.text !== "string") return;
    this.broadcast({ type: "message", text: msg.text.slice(0, 2000) });   // 每个人
  }
  handleClose(conn) {}
}
```

### 服务角色访问

在后台函数中使用 `asServiceRole` 进行管理员级操作。实体通过 `this.client.asServiceRole` 暴露以进行验证、房间拥有的工作（例如持久化规范结果）；使用从认证连接中验证的 `conn.identity.userId` 进行明确的用户归因。参见 [actors.md](references/actors.md)。

```javascript
// 用户模式 - 尊重权限
const myTasks = await base44.entities.Task.list();

// 服务角色 - 完全访问（仅后端）
const allTasks = await base44.asServiceRole.entities.Task.list();
const token = await base44.asServiceRole.connectors.getAccessToken("slack");
```

## 前端与后端

| 功能 | 前端 | 后端 |
|------|------|------|
| `entities`（用户数据） | 是 | 是 |
| `auth` | 是 | 是 |
| `agents` | 是 | 是 |
| `functions.invoke()` | 是 | 是 |
| `functions.fetch()` | 是 | 是 |
| `actors`（连接到房间） | 是 | 否 — 实体是服务器端 |
| `integrations` | 是 | 是 |
| `aiGateway` | 否 | 是 |
| `analytics` | 是 | 是 |
| `appLogs` | 是 | 是 |
| `users` | 是 | 是 |
| `asServiceRole.*` | 否 | 是 |
| `asServiceRole.connectors`（应用 OAuth） | 否 | 是 |
| `asServiceRole.sso` | 否 | 是 |

后台函数 `export default` 一个异步请求处理程序，并使用 `createClientFromRequest(req)` 获取正确认证的客户端。
