# 在云沙盒中编写 Base44

使用您自己的编码代理在 Base44 的云沙盒中编写 Base44 应用程序代码。无需本地检出：您通过沙盒工具（通过 MCP 或 `base44 sandbox` CLI）读取、写入和运行文件，该平台从您编写的内容构建和部署。

有关如何连接到沙盒（MCP 端点或 `base44 sandbox` CLI、`read_file` / `write_file` / `edit_file` / `run_command` / `grep` / `list_directory` / `create_checkpoint` 工具——CLI 在较短的名称下公开这些工具，`sandbox read` / `sandbox write` / `sandbox edit` / `sandbox run` / `sandbox grep` / `sandbox ls` / `sandbox checkpoint`）、编辑→预览→验证循环、持久性和并发性，请使用 **`base44-remote-dev`** 技能。此技能涵盖您连接后可以编写的内容和方式。

> **首先查看这些参考。** 此技能及其兄弟技能（`base44-remote-dev`、`base44-sdk`）是事实来源——在搜索网络之前请参考它们。参见 [参考顺序和完整的 README](#reference-order--the-complete-readme)。

## ⚡ 心智模型：编写文件就是部署

您正在处理一个**远程**应用程序，而不是本地检出。项目级 CLI 工作流不适用——永远不要运行 `base44 deploy`、`base44 functions deploy`、`base44 actors deploy`、`base44 actors delete`、`base44 ... push`、`base44 create` 或 `base44 scaffold`。它们假设本地项目和手动部署步骤，而这里不存在这些步骤。

相反：**一旦您将资源文件写入沙盒——后端函数、执行者、实体或代理——平台就会从那里部署/同步它。** 您的写入是自动提交的（约 5 秒去抖），并立即生效。您不需要运行，也不应等待任何 `deploy` / `push` 命令。

**一个例外——连接器。** OAuth 连接器不是作为文件编写的；它们通过其 ID 对远程应用程序进行设置，可以使用 MCP 连接器工具或使用专门的、无项目的 `base44 connectors` 命令（这些命令需要 `--app-id` 且无需本地项目）。参见下文的 [连接器](#connectors-oauth-integrations)。

您仍然可以使用 `run_command`（CLI 中的 `sandbox run`）进行普通检查（例如 `npm run build`、`npx tsc --noEmit`、`npm run lint`）和预览——那是验证，不是部署。参见 `base44-remote-dev` 中的编辑→预览→验证循环。

## 您今天可以编写的内容

| 资源 | 沙盒中的状态 |
|------|-------------|
| **后端函数** (`base44/functions/`) | ✅ 支持——编写文件；它们从沙盒部署。 |
| **执行者** (`base44/actors/`) | ✅ 支持——编写 `entry.ts`；执行者从沙盒部署。删除条目文件会将其销毁。 |
| **实体** (`base44/entities/`) | ✅ 支持——编写 `.jsonc` 模式文件；它自动同步。没有 `entities push`。 |
| **代理** (`base44/agents/`) | ✅ 支持——编写 `.jsonc` 配置文件；它自动同步。没有 `agents push`。 |
| **前端代码** (`src/…`) | ✅ 支持——正常编辑；HMR/预览反映它。使用 **`base44-sdk`** 技能进行 SDK API 使用。 |
| **连接器**（OAuth 集成） | ✅ 支持——通过下文的连接流程设置（MCP 工具或 `base44 connectors`），**不是**通过编写文件。 |

## 后端函数

后端函数位于 `base44/functions/`，每个函数一个目录（使用连字符命名）。在沙盒中，您只需要在 `base44/functions/<name>/` 下直接创建 **`entry.ts`** 文件——**不需要 `function.jsonc`**（沙盒从目录中推断函数；在此模式下忽略配置文件）：

```
base44/functions/
  process-order/
    entry.ts
```

条目文件——导出默认的异步请求处理程序，并使用 `npm:` 前缀引用 npm 包：
```typescript
import { createClientFromRequest } from "npm:@base44/sdk";

export default async function (req) {
  const base44 = createClientFromRequest(req);   // 继承调用者的认证
  const { orderId } = await req.json();
  const order = await base44.entities.Orders.get(orderId);
  return Response.json({ success: true, order });
}
```
约定：
- **连字符命名** 目录和函数名；条目通常是 `entry.ts`。
- `createClientFromRequest(req)` 用于调用者认证上下文中的客户端；`base44.asServiceRole.…` 用于管理员级操作。
- 使用 `secrets.get("KEY")` 从 `base44:runtime`（`import { secrets } from "base44:runtime"`；在应用程序设置中配置）读取密钥。
- 使用 `Response.json(body, { status })` 返回；处理错误并设置适当的状态代码。

编写函数正确即可。有关更多详细信息和示例（服务角色、密钥、常见错误），请参阅 `base44-cli` 技能的参考：[`functions-create.md`](../base44-cli/references/functions-create.md)——但**忽略其“部署函数”/CLI 部分**及其**`function.jsonc`** 指导，这些假设本地项目，在沙盒中不适用（这里您只需编写 `entry.ts`）。

> **从前端调用函数：** `base44.functions.invoke(name, data)` 返回**原始 axios 响应**——您的函数的 JSON 位于 **`.data`**（`const result = res.data`），而不是顶层对象，并且在**非 2xx** 时抛出（错误正文位于 `err.response.data`）。有关详细信息，请参阅 `base44-sdk` 技能的 [`functions.md`](../base44-sdk/references/functions.md)。

## 执行者（实时）

执行者是 WebSocket 上的有状态实时服务器房间——每个房间 ID 一个活动实例，由所有连接到此 ID 的人共享。当用户在一个共享会话中**实时交互**时，请使用它们：多人游戏、协作板/文档、存在和实时光标、房间内聊天、实时拍卖。仅列出实时记录的页面不需要执行者（`base44.entities.Thing.subscribe()` 覆盖该功能）。

`base44/actors/` 中的每个执行者一个文件夹，包含 `entry.ts`。只需编写文件即可——它会部署；**不要运行 `base44 actors deploy` 或 `deploy`**。编写**纯 JavaScript**，就像后端函数一样——没有类型注解；文件是 `.ts` 只是因为那是入口合同。没有执行者的测试工具（它提供 WebSocket，而不是请求）——在预览中验证它。

```
base44/actors/
  ChatRoom/
    entry.ts
```

```javascript
// base44/actors/ChatRoom/entry.ts
import { Actor } from "base44:runtime/actors";   // 唯一解析的基类导入

export default class ChatRoom extends Actor {
  async handleStart() {
    // 每次唤醒时运行——当房间进入休眠状态时实例字段会丢失。
    this.history = (await this.storage.get("history")) ?? [];
  }
  handleConnect(conn) {
    conn.send({ type: "history", messages: this.history });   // 仅此客户端
  }
  async handleMessage(conn, msg) {
    if (msg?.type !== "message" || typeof msg.text !== "string") return;   // 验证所有内容
    const authorUserId = conn.identity?.type === "authenticated" ? conn.identity.userId : null;
    const entry = { authorUserId, text: msg.text.slice(0, 2000) };
    this.history = [...this.history, entry].slice(-100);
    await this.storage.put("history", this.history);
    this.broadcast({ type: "message", ...entry });            // 整个房间
  }
  handleClose(conn) {}
}
```

约定：
- **PascalCase** 文件夹名——它成为 JavaScript 类绑定，因此只能使用 `[A-Za-z_][A-Za-z0-9_]*`（不能有 `-`、`.`、`/`），没有 JavaScript 保留字，并且**没有嵌套文件夹**。
- 入口必须**默认导出**一个扩展 `Actor` 的类；类名本身是装饰性的。
- 处理程序：`handleConnect(conn)` / `handleMessage(conn, msg)` / `handleClose(conn)`，以及可选的 `handleStart()` 和 `handleWake(key)`。对于必须在自身上推进的房间（游戏循环、可见倒计时），覆盖 `shouldTick()`，平台在返回 true 时每 `tickIntervalMs`（默认 100）调用 `handleTick()`。永远不要覆盖 `onStart`/`onAlarm`。
- 在 `this.storage` 中持久化任何您不能丢失的内容，并在 `handleStart()` 中重新水化它——当房间进入休眠状态时实例字段会重置。
- `this.broadcast(...)` 用于房间范围状态；`conn.send(...)` 用于关于一个客户端的事件。
- 执行者使用直接连接；SDK 处理令牌铸造和连接认证。`conn.identity` 包含经过验证的认证 `userId` 或匿名 `anonymousId` 并在休眠期间存活。用于归因和权限；访客聊天消息使用 `authorUserId: null`。
- 保持客户端选择的 `conn.id` 内部用于重新连接记录。使用服务器分配的参与者 ID 用于公共存在；永远不要广播重新连接 ID，也不要将它们视为作者身份或权限的证据。
- `this.client` 使用**匿名**角色（RLS 保护）。`this.client.asServiceRole` 提供管理员级实体访问、函数调用和验证的房间拥有的工作集成。它们都不模拟用户：使用从认证的 `conn.identity.userId` 显式字段归因记录。
- 执行者是权威的：客户端发送输入，执行者验证并广播。永远不要信任客户端计算的结果。
- 持久化结果（完成的绘画、聊天记录）：**执行者**在 `this.storage` 中存储经过验证的结果，并通过 `this.client.asServiceRole` 持久化规范实体记录，键由房间的实例 ID 键控。保留挂起的写入并在需要时使用计划的唤醒重试。向（重新）连接的客户端广播和重新发送结果以进行显示；前端只编写用户拥有的记录。将规范结果实体写入限制为服务器。
- 执行者不接收应用程序密钥或私有数据源绑定。将需要它们的操作放入后端函数并在执行者中调用它。`ACTOR_TOKEN_SECRET` 会自动提供；在设置期间不要创建或覆盖它，因为更改它会旋转执行者的密钥。
- 不支持在执行者上的自动化。

有关完整的编写参考（命名、生命周期、存储/休眠、计划的唤醒、房间和发现），请参阅 `base44-cli` 技能的 [`actors-create.md`](../base44-cli/references/actors-create.md)——但**忽略其“部署执行者”/CLI 部分**，这些假设本地项目。

> **从前端连接：** `base44.actors.ChatRoom(roomId).connect()` 返回一个具有 `.subscribe(cb)`、`.send(data)` 和 `.close()` 的连接。在 `useEffect` 内部连接并清理两者。参见 `base44-sdk` 技能的 [`actors.md`](../base44-sdk/references/actors.md)。

## 实体

`base44/entities/` 中的每个实体一个 `.jsonc` 文件。只需编写文件即可——它会自动同步；**不要运行 `base44 entities push` 或 `deploy`**。

- **文件名：** `{连字符命名}.jsonc`——例如 `team-member.jsonc` 用于名为 `TeamMember` 的实体。
- **实体 `name`：** PascalCase，仅限字母数字（`/^[a-zA-Z0-9]+$/`）。
- **字段名：** `snake_case`。

```jsonc
// base44/entities/task.jsonc
{
  "name": "Task",
  "type": "object",
  "properties": {
    "title": { "type": "string", "description": "任务标题" },
    "status": { "type": "string", "enum": ["todo", "doing", "done"], "default": "todo" },
    "due_date": { "type": "string", "format": "date" },
    "board_id": { "type": "string", "description": "所属看板" }
  },
  "required": ["title"]
}
```

字段类型：`string`、`number`、`integer`、`boolean`、`array`、`object`、`binary`。字符串格式包括 `date`、`date-time`、`email`、`uri`、`uuid`、`file`、`richtext`。有关完整模式详细信息和行级安全（RLS），请参阅 `base44-cli` 参考的 [`entities-create.md`](../base44-cli/references/entities-create.md) 和 [`rls-examples.md`](../base44-cli/references/rls-examples.md)——但**忽略它们的 `entities push` / 部署部分**；沙盒同步文件为您。
