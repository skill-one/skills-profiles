# RivetKit JavaScript 客户端

在构建连接到 Rivet Actors 的 JavaScript 客户端（浏览器、Node.js 或 Bun）时使用此技能，使用 `rivetkit/client`。

## 初步步骤

1.  安装客户端（最新版本：2.3.7）
   ```bash
   npm install rivetkit@2.3.7
   ```
2.  使用 `createClient()` 创建客户端并调用 actor 动作。

## 错误处理策略

-  默认情况下优先采用快速失败行为。
-  除非绝对必要，否则避免使用 `try/catch`。
-  如果使用 `catch`，应显式处理错误，至少记录错误。

## 入门指南

参见 [后端快速入门指南](/docs/actors/quickstart/backend) 获取入门指南。

## 最小客户端

## 无状态与有状态

## 获取 Actors

## 连接参数

使用 `params` 用于静态连接参数。当值可能在连接尝试之间变化时（例如，在每次 `.connect()` 或重连之前刷新 JWT）使用 `getParams`。

## 订阅事件

## 连接生命周期

## 低级 HTTP 与 WebSocket

对于实现 `onRequest` 或 `onWebSocket` 的 Actors，直接调用它们：

```ts @nocheck
import { createClient } from "rivetkit/client";

const client = createClient();
const handle = client.chatRoom.getOrCreate(["general"]);

const response = await handle.fetch("history");
const history = await response.json();

const ws = await handle.webSocket("stream");
ws.addEventListener("message", (event) => {
  console.log("message:", event.data);
});
ws.send("hello");
```

## 后端调用

## 错误处理

## 概念

### 键

键唯一标识 actor 实例。使用复合键（数组）进行分层寻址：

不要使用字符串插值（如 `"org:${userId}"`）构建键，当 `userId` 包含用户数据时。使用数组代替以防止键注入攻击。

### 环境变量

`createClient()` 自动读取：

- `RIVET_ENDPOINT`（端点）
- `RIVET_NAMESPACE`
- `RIVET_TOKEN`
- `RIVET_POOL`

未设置时默认为 `http://localhost:6420`。RivetKit 默认在端口 6420 上运行。

### 端点格式

端点支持 URL 认证语法：

```
https://namespace:token@api.rivet.dev
```

您也可以传递不带认证的端点，并单独提供 `RIVET_NAMESPACE` 和 `RIVET_TOKEN`。对于无服务器部署，使用您的应用的 `/api/rivet` URL。详情请参阅 [端点](/docs/general/endpoints#url-auth-syntax)。

## 高级用法

### 跳过就绪等待

请求通常在网关处等待，直到 actor 准备好接受流量。actor 在启动时（`onWake` 完成之前）或处于 [睡眠宽限期](/docs/actors/lifecycle#shutdown-sequence)（运行 `onSleep`、`waitUntil` 并等待断开连接）时未就绪。

在 [低级 HTTP 和 WebSocket API](#low-level-http--websocket) 中传递 `skipReadyWait: true` 以立即发送，并在任一窗口中到达 actor 的 `onRequest` / `onWebSocket` 处理程序：

```ts @nocheck
import { createClient } from "rivetkit/client";

const client = createClient();
const handle = client.chatRoom.getOrCreate(["general"]);

const response = await handle.fetch("/healthz", {
  skipReadyWait: true,
});

const ws = await handle.webSocket("probe", undefined, {
  skipReadyWait: true,
});
```

请求仍然可能返回瞬态生命周期或网关错误。actor 再次可用时重试。

- `actor.stopping`：actor 已完全停止，即睡眠宽限期已结束，但尚未重启。
- `guard.actor_stopped_while_waiting`：请求到达 actor 隧道，但 actor 在网关收到响应之前停止。
- `guard.tunnel_request_aborted`：actor 隧道在响应开始之前中止了请求。
- `guard.tunnel_message_timeout`：网关在其隧道消息超时后丢弃了正在进行的隧道请求。
- `guard.tunnel_response_closed`：actor 隧道在发送响应之前关闭。
- `guard.gateway_response_start_timeout`：网关超时等待 actor 响应开始。

## API 参考

**包：** [rivetkit](https://www.npmjs.com/package/rivetkit)

参见 [RivetKit 客户端概述](/docs/clients)。

- [`createClient`](/typedoc/functions/rivetkit.client_mod.createClient.html) - 创建客户端
- [`Client`](/typedoc/types/rivetkit.mod.Client.html) - 客户端类型

## 需要更多客户端以外的功能？

如果您需要更多关于 Rivet Actors、注册中心或服务器端 RivetKit 的信息，请添加主技能：

```bash
npx skills add rivet-dev/skills
```

然后使用 `rivetkit` 技能获取后端指导。
