# /setup-zoom-websockets

持久化 Zoom 事件流的后台参考。优先考虑工作流路由，当 WebSockets 可能比 webhook 更好时使用此文件。

## WebSockets 与 Webhooks

| 方面 | WebSockets | Webhooks |
|------|------------|----------|
| **连接** | 持久化，双向 | 一次性 HTTP POST |
| **延迟** | 较低（无 HTTP 开销） | 较高（每个事件建立新连接） |
| **安全性** | 直接连接，不暴露端点 | 需要端点验证，IP 白名单 |
| **模型** | 拉取（你连接到 Zoom） | 推送（Zoom 连接到你） |
| **状态** | 有状态（维护连接） | 无状态（每个事件独立） |
| **设置** | 更复杂（访问令牌，连接） | 更简单（只需端点 URL） |

**选择 WebSockets 当：**
- 实时、低延迟更新至关重要
- 安全性最高（银行、医疗保健、金融）
- 不想暴露公共端点
- 需要双向通信

**选择 Webhooks 当：**
- 优先考虑简单设置
- 事件通知数量较少
- 现有 HTTP 基础设施

## 前置条件

- Zoom 市场中的服务器到服务器 OAuth 应用程序 [Zoom Marketplace](https://marketplace.zoom.us/)
- 账户 ID、客户端 ID 和客户端密钥
- 启用事件的 WebSocket 订阅

> **需要帮助使用 S2S OAuth？** 查看 **[zoom-oauth](../oauth/SKILL.md)** 技能以获取完整的身份验证流程。

> **快速开始故障排除：** 在深入调试之前使用 **[5 分钟运行手册](RUNBOOK.md)**。

## 快速入门

### 1. 创建服务器到服务器 OAuth 应用程序

1. 前往 [Zoom 市场place](https://marketplace.zoom.us/develop/create)
2. 创建 **服务器到服务器 OAuth** 应用程序
3. 复制账户 ID、客户端 ID、客户端密钥

### 2. 启用 WebSocket 订阅

1. 在你的应用程序中，前往 **功能** → **事件订阅**
2. 添加事件订阅
3. 选择 **WebSockets** 作为方法类型
4. 选择要订阅的事件（例如，`meeting.created`、`meeting.started`）
5. 保存 - 将生成端点 URL

### 3. 通过 WebSocket 连接

```javascript
const WebSocket = require('ws');
const axios = require('axios');

// 第 1 步：获取访问令牌
async function getAccessToken() {
  const credentials = Buffer.from(`${CLIENT_ID}:${CLIENT_SECRET}`).toString('base64');
  
  const response = await axios.post(
    'https://zoom.us/oauth/token',
    new URLSearchParams({
      grant_type: 'account_credentials',
      account_id: ACCOUNT_ID
    }),
    {
      headers: {
        'Authorization': `Basic ${credentials}`,
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    }
  );
  
  return response.data.access_token;
}

// 第 2 步：连接到 WebSocket
async function connectWebSocket() {
  const accessToken = await getAccessToken();
  
  // 从你的订阅设置中获取 WebSocket URL
  const wsUrl = `wss://ws.zoom.us/ws?subscriptionId=${SUBSCRIPTION_ID}&access_token=${accessToken}`;
  
  const ws = new WebSocket(wsUrl);
  
  ws.on('open', () => {
    console.log('WebSocket 连接已建立');
  });
  
  ws.on('message', (data) => {
    const event = JSON.parse(data);
    console.log('收到事件:', event.event);
    
    // 处理不同的事件类型
    switch (event.event) {
      case 'meeting.started':
        console.log(`会议开始: ${event.payload.object.topic}`);
        break;
      case 'meeting.ended':
        console.log(`会议结束: ${event.payload.object.uuid}`);
        break;
      case 'meeting.participant_joined':
        console.log(`参与者加入: ${event.payload.object.participant.user_name}`);
        break;
    }
  });
  
  ws.on('close', (code, reason) => {
    console.log(`连接关闭: ${code} - ${reason}`);
    // 实现重连逻辑
  });
  
  ws.on('error', (error) => {
    console.error('WebSocket 错误:', error);
  });
  
  return ws;
}

connectWebSocket();
```

## 事件格式

通过 WebSocket 接收的事件与 webhook 事件具有相同的格式：

```json
{
  "event": "meeting.started",
  "event_ts": 1706123456789,
  "payload": {
    "account_id": "abcD3ojkdbjfg",
    "object": {
      "id": 1234567890,
      "uuid": "abcdefgh-1234-5678-abcd-1234567890ab",
      "host_id": "xyz789",
      "topic": "团队例会",
      "type": 2,
      "start_time": "2024-01-25T10:00:00Z",
      "timezone": "America/Los_Angeles"
    }
  }
}
```

## 常见事件

| 事件 | 描述 |
|------|-------------|
| `meeting.created` | 会议已安排 |
| `meeting.updated` | 会议设置已更改 |
| `meeting.deleted` | 会议已删除 |
| `meeting.started` | 会议开始 |
| `meeting.ended` | 会议结束 |
| `meeting.participant_joined` | 参与者加入会议 |
| `meeting.participant_left` | 参与者离开会议 |
| `recording.completed` | 云录制已准备好 |
| `user.created` | 新用户已添加 |
| `user.updated` | 用户详细信息已更改 |

## 连接管理

### 心跳

WebSocket 连接需要定期发送心跳。Zoom 将关闭空闲连接。

```javascript
// 每 30 秒发送一次 ping
setInterval(() => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.ping();
  }
}, 30000);
```

### 重连

实现自动重连以提高可靠性：

```javascript
function connectWithReconnect() {
  const ws = connectWebSocket();
  
  ws.on('close', () => {
    console.log('连接丢失。5 秒后重连...');
    setTimeout(connectWithReconnect, 5000);
  });
  
  return ws;
}
```

### 单个连接限制

**重要提示：** 每个订阅一次只能打开一个 WebSocket 连接。打开新连接将关闭现有连接。

## 详细参考

- **[references/connection.md](references/connection.md)** - 连接生命周期、身份验证、错误处理
- **[references/events.md](references/events.md)** - 完整事件类型参考

## 故障排除

- **[troubleshooting/common-issues.md](troubleshooting/common-issues.md)** - 订阅 URL 混淆、断开连接、无事件调试

## 示例存储库

### 官方 / 社区

| 类型 | 存储库 | 描述 |
|------|------------|-------------|
| Node.js | [just-zoomit/zoom-websockets](https://github.com/just-zoomit/zoom-websockets) | 使用 S2S OAuth 的 WebSocket 示例 |

## WebSockets 与 RTMS

不要将 WebSockets 与 RTMS（实时媒体流）混淆：

| 功能 | WebSockets | RTMS |
|------|------------|------|
| **目的** | 事件通知 | 媒体流 |
| **数据** | 会议事件、用户事件 | 音频、视频、字幕 |
| **用例** | 响应 Zoom 事件 | AI/ML、实时字幕 |
| **技能** | 此技能 | **rtms** |

对于实时音频/视频/字幕数据，请使用 **rtms** 技能。

## 资源

- **WebSockets 文档**: https://developers.zoom.us/docs/api/websockets/
- **Webhooks 对比**: https://www.zoom.com/en/blog/a-guide-to-webhooks-and-websockets/
- **开发者论坛**: https://devforum.zoom.us/

## 环境变量

- 查看 [references/environment-variables.md](references/environment-variables.md) 以获取标准化的 `.env` 键以及每个值的位置。
