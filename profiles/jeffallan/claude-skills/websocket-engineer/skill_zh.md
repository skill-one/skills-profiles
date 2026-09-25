# WebSocket 工程师

## 核心工作流程

1. **分析需求** — 确定连接规模、消息量、延迟需求
2. **设计架构** — 规划集群、发布/订阅、状态管理、故障转移
3. **实现** — 构建带认证、房间、事件的 WebSocket 服务器
4. **本地验证** — 在扩展前测试连接处理、认证和房间行为（例如，`npx wscat -c ws://localhost:3000`）；确认缺少/无效令牌时的认证拒绝、房间加入/离开事件和消息传递
5. **扩展** — 在启用适配器前验证 Redis 连接和发布/订阅往返；配置会话粘性并跨多个实例进行测试连接确认；设置负载均衡
6. **监控** — 追踪连接数、延迟、吞吐量、错误率；为连接数峰值和错误率阈值添加告警

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|----------|
| 协议 | `references/protocol.md` | WebSocket 握手、帧、ping/pong、关闭代码 |
| 扩展 | `references/scaling.md` | 水平扩展、Redis 发布/订阅、会话粘性 |
| 模式 | `references/patterns.md` | 房间、命名空间、广播、确认 |
| 安全 | `references/security.md` | 认证、授权、速率限制、CORS |
| 替代方案 | `references/alternatives.md` | SSE、长轮询、何时选择 WebSocket |

## 代码示例

### 服务器设置（带认证和房间管理的 Socket.IO）

```js
import { createServer } from "http";
import { Server } from "socket.io";
import { createAdapter } from "@socket.io/redis-adapter";
import { createClient } from "redis";
import jwt from "jsonwebtoken";

const httpServer = createServer();
const io = new Server(httpServer, {
  cors: { origin: process.env.ALLOWED_ORIGIN, credentials: true },
  pingTimeout: 20000,
  pingInterval: 25000,
});

// 认证中间件 — 在建立连接前运行
io.use((socket, next) => {
  const token = socket.handshake.auth.token;
  if (!token) return next(new Error("需要认证"));
  try {
    socket.data.user = jwt.verify(token, process.env.JWT_SECRET);
    next();
  } catch {
    next(new Error("无效的令牌"));
  }
});

// Redis 适配器用于水平扩展
const pubClient = createClient({ url: process.env.REDIS_URL });
const subClient = pubClient.duplicate();
await Promise.all([pubClient.connect(), subClient.connect()]);
io.adapter(createAdapter(pubClient, subClient));

io.on("connection", (socket) => {
  const { userId } = socket.data.user;
  console.log(`已连接: ${userId} (${socket.id})`);

  // 存在性：标记用户在线
  pubClient.hSet("presence", userId, socket.id);

  socket.on("join-room", (roomId) => {
    socket.join(roomId);
    socket.to(roomId).emit("user-joined", { userId });
  });

  socket.on("message", ({ roomId, text }) => {
    io.to(roomId).emit("message", { userId, text, ts: Date.now() });
  });

  socket.on("disconnect", () => {
    pubClient.hDel("presence", userId);
    console.log(`已断开: ${userId}`);
  });
});

httpServer.listen(3000);
```

### 客户端带指数退避的重连

```js
import { io } from "socket.io-client";

const socket = io("wss://api.example.com", {
  auth: { token: getAuthToken() },
  reconnection: true,
  reconnectionAttempts: 10,
  reconnectionDelay: 1000,       // 初始延迟 (ms)
  reconnectionDelayMax: 30000,   // 最大 30 秒
  randomizationFactor: 0.5,      // 避免雷鸣效应的抖动
});

// 断开连接时暂存消息
let messageQueue = [];

socket.on("connect", () => {
  console.log("已连接:", socket.id);
  // 发送暂存的消息
  messageQueue.forEach((msg) => socket.emit("message", msg));
  messageQueue = [];
});

socket.on("disconnect", (reason) => {
  console.warn("已断开:", reason);
  if (reason === "io server disconnect") socket.connect(); // 手动重连
});

socket.on("connect_error", (err) => {
  console.error("连接错误:", err.message);
});

function sendMessage(roomId, text) {
  const msg = { roomId, text };
  if (socket.connected) {
    socket.emit("message", msg);
  } else {
    messageQueue.push(msg); // 暂存直到重连
  }
}
```

## 限制条件

### 必须做
- 使用会话粘性进行负载均衡（WebSocket 连接是状态化的 — 请求必须路由到相同的服务器实例）
- 实现心跳/ping-pong 以检测无效连接（仅 TCP 保持活动是不够的）
- 使用房间/命名空间进行消息作用域，而不是在应用逻辑中过滤
- 在断开连接期间暂存消息，以避免静默数据丢失
- 在水平扩展前规划每个实例的连接限制

### 必须不做
- 在没有集群策略的情况下将大状态存储在内存中（使用 Redis 或外部存储）
- 在同一端口上混合 WebSocket 和 HTTP，而没有显式的升级处理
- 忘记处理连接清理（存在性记录、房间成员资格、在途计时器）
- 在生产前跳过负载测试 — 连接数峰值与 HTTP 流量峰值表现不同

## 输出模板

在实现 WebSocket 功能时提供：
1. 服务器设置（Socket.IO/ws 配置）
2. 事件处理器（连接、消息、断开连接）
3. 客户端库（连接、事件、重连）
4. 扩展策略的简要说明

## 知识参考

Socket.IO、ws、uWebSockets.js、Redis 适配器、会话粘性、nginx WebSocket 代理、WebSocket 上的 JWT、房间/命名空间、确认、二进制数据、压缩、心跳、背压、水平 Pod 自动扩展

[文档](https://jeffallan.github.io/claude-skills/skills/api-architecture/websocket-engineer/)
