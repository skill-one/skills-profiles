# RivetKit React 客户端

在构建连接到 Rivet Actors 的 React 应用程序时，请使用此技能，并使用 `@rivetkit/react`。

## 初步步骤

1.  安装 React 客户端（最新版本：2.3.7）
   ```bash
   npm install @rivetkit/react@2.3.7
   ```
2.  使用 `createRivetKit()` 创建钩子，并使用 `useActor()` 进行连接。

## 错误处理策略

-  默认情况下优先采用快速失败行为。
-  除非绝对必要，否则避免使用 `try/catch`。
-  如果使用 `catch`，应明确处理错误，至少应记录错误。

## 入门指南

请参阅 [React 快速入门指南](/docs/actors/quickstart/react) 以开始使用。

## 安装

## 最小客户端

## 无状态与有状态

## 获取 Actors

## 连接参数

## 订阅事件

## 连接生命周期

## 低级 HTTP 与 WebSocket

使用 JavaScript 客户端进行原始 HTTP 和 WebSocket 访问：

```tsx @nocheck
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

在您的后端（Node.js/Bun）上使用 JavaScript 客户端。请参阅 [JavaScript 客户端文档](/docs/clients/javascript)。

## 错误处理

## 概念

### 键

键唯一标识 Actor 实例。使用复合键（数组）进行分层寻址：

不要使用字符串插值（如 `"org:${userId}"`）构建键，其中 `userId` 包含用户数据。应使用数组来防止键注入攻击。

### 环境变量

`createRivetKit()`（以及底层的 `createClient()` 实例）会自动读取：

- `RIVET_ENDPOINT`
- `RIVET_NAMESPACE`
- `RIVET_TOKEN`
- `RIVET_POOL`

如果未设置，默认为 `http://localhost:6420`。RivetKit 默认在端口 6420 上运行。

### 端点格式

端点支持 URL 认证语法：

```
https://namespace:token@api.rivet.dev
```

您也可以不传递带认证的端点，而单独提供 `RIVET_NAMESPACE` 和 `RIVET_TOKEN`。对于无服务器部署，请使用您的应用程序的 `/api/rivet` URL。有关详细信息，请参阅 [端点](/docs/general/endpoints#url-auth-syntax)。

## API 参考

**包：** [@rivetkit/react](https://www.npmjs.com/package/@rivetkit/react)

- [`createRivetKit`](/docs/clients/react) - 为 React 创建钩子
- [`useActor`](/docs/clients/react) - Actor 实例的钩子

## 需要超出客户端之外的功能？

如果您需要更多关于 Rivet Actors、注册中心或服务器端 RivetKit 的信息，请添加主技能：

```bash
npx skills add rivet-dev/skills
```

然后使用 `rivetkit` 技能获取后端指导。
