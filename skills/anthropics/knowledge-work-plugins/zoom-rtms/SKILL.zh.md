---
name: zoom-rtms
description: Zoom RTMS的参考技能。在处理实时音频、视频、聊天、字幕、屏幕共享或呼叫中心语音流时，用于在路由到实时媒体工作流之后。
---

# Zoom 实时媒体流 (RTMS)

实时 Zoom 媒体流管道的背景参考。建议先使用 `build-zoom-bot`，然后使用此技能来处理流类型、功能和 RTMS 特定的实现限制。

# Zoom 实时媒体流 (RTMS)

访问 Zoom 会议、网络研讨会、Video SDK 会话和 Zoom 语音联络中心的实时音频、视频、字幕、聊天和屏幕共享数据的专家指南。RTMS 使用基于 WebSocket 的协议，采用开放标准，并且不需要会议机器人来捕获媒体平面。

## 首先阅读（关键）

RTMS 主要是一个 **后端媒体摄取服务**。

- 您的后端接收并处理实时媒体：**音频、视频、屏幕共享、聊天、字幕**。
- RTMS 本身不是一个前端 UI SDK。
- 处理是 **事件触发的**：后端等待 RTMS 开始 webhook 事件后才会开始流处理。

可选架构（常见）：

- 添加一个 **Zoom 应用程序 SDK** 前端用于客户端 UI/控件。
- 通过 **WebSocket**（或 SSE、gRPC、队列工作器等）将后端 RTMS 输出到前端。

使用 RTMS 作为媒体/数据平面，使用前端框架/Zoom 应用程序进行呈现 + 用户交互。

**官方文档**：https://developers.zoom.us/docs/rtms/
**SDK 参考 (JS)**：https://zoom.github.io/rtms/js/
**SDK 参考 (Python)**：https://zoom.github.io/rtms/py/
**示例存储库**：https://github.com/zoom/rtms-samples

## 快速链接

**新接触 RTMS？请遵循此路径：**

1. **[连接架构](concepts/connection-architecture.md)** - 两阶段 WebSocket 设计
2. **[SDK 快速入门](examples/sdk-quickstart.md)** - 接收媒体最快的方式（推荐）
3. **[手动 WebSocket](examples/manual-websocket.md)** - 无需 SDK 的完整协议控制
4. **[媒体类型](references/media-types.md)** - 音频、视频、字幕、聊天、屏幕共享

**完整实现：**
- **[RTMS 机器人](examples/rtms-bot.md)** - 端到端机器人实现指南

**参考：**
- **[生命周期流](concepts/lifecycle-flow.md)** - 完整的 webhook 到流式传输流程
- **[数据类型](references/data-types.md)** - 所有枚举和常量
- **[Webhooks](references/webhooks.md)** - 事件订阅详细信息
- **[环境变量](references/environment-variables.md)** - 凭据模式和运行时调节
- **[快速入门说明](references/quickstart.md)** - 次要快速入门指南
- **集成索引** - 查看此文件中的下一节

**遇到问题？**
- 连接失败 -> [常见问题](troubleshooting/common-issues.md)
- 重复连接 -> [Webhook 注意事项](troubleshooting/common-issues.md#webhook-response-timing)
- 无音频/视频 -> [媒体配置](references/media-types.md)
- 从预检检查开始 -> [5 分钟运行手册](RUNBOOK.md)

## 支持的产品

| 产品 | Webhook 事件 | 载荷 ID | 应用程序类型 |
|------|--------------|------------|----------|
| **会议** | `meeting.rtms_started` / `meeting.rtms_stopped` | `meeting_uuid` | 普通应用程序 |
| **网络研讨会** | `webinar.rtms_started` / `webinar.rtms_stopped` | `meeting_uuid` (相同!) | 普通应用程序 |
| **Video SDK** | `session.rtms_started` / `session.rtms_stopped` | `session_id` | Video SDK 应用程序 |
| **Zoom 语音联络中心** | 产品特定的 RTMS/ZCC 语音事件 | 产品特定的流/会话标识符 | 联络中心 / 授权的 RTMS 集成 |

连接后，核心信令/媒体套接字模型在所有产品中共享。会议、网络研讨会和 Video SDK 会话使用熟悉的开始/停止 webhook。Zoom 语音联络中心添加了自己的 RTMS/ZCC 语音事件系列，应被视为相同的传输模型，但具有产品特定的事件载荷。

## RTMS 概述

RTMS 是一个数据管道，它为您的应用程序提供从 Zoom 会议、网络研讨会和 Video SDK 会话获取实时媒体的能力，而无需参与者机器人。与其让自动客户端加入会议，不如使用 RTMS 直接从 Zoom 基础设施收集媒体数据。

### RTMS 提供的内容

| 媒体类型 | 格式 | 用例 |
|------------|--------|-----------|
| **音频** | PCM (L16), G.711, G.722, Opus | 字幕、语音分析、录音 |
| **视频** | H.264, JPG, PNG | 录制、AI 视觉、缩略图、活动参与者选择 |
| **屏幕共享** | H.264, JPG, PNG | 内容捕获、幻灯片提取 |
| **字幕** | JSON 文本 | 会议笔记、搜索、合规性 |
| **聊天** | JSON 文本 | 归档、情感分析 |

### 2026 年 3 月协议变更

- **Zoom 语音联络中心支持**：RTMS 现在涵盖联络中心语音音频和字幕场景。
- **字幕语言识别控制**：字幕媒体握手现在支持 `src_language` 和 `enable_lid`。默认行为是启用 LID。设置 `enable_lid: false` 以强制固定语言。
- **单个个人视频流订阅**：当 `data_opt` 设置为 `VIDEO_SINGLE_INDIVIDUAL_STREAM` 时，RTMS 现在可以流式传输一个参与者的摄像头源。
- **客户端发起的优雅关闭**：后端可以通过信令套接字发送 `STREAM_CLOSE_REQ` 并等待 `STREAM_CLOSE_RESP`。
- **媒体保持活动状态容忍度增加**：媒体套接字保持活动状态超时现在是 **65 秒**，不是 35 秒。

### 两种方法

| 方法 | 适用于 | 复杂性 |
|----------|----------|------------|
| **SDK** (`@zoom/rtms`) | 大多数用例 | 低 - 处理 WebSocket 复杂性 |
| **手动 WebSocket** | 自定义协议、其他语言 | 高 - 完整协议实现 |

## 前置条件

- **Node.js 20.3.0+** (24 LTS 推荐) 用于 JavaScript SDK
- **Python 3.10+** 用于 Python SDK
- Zoom 普通应用程序（用于会议/网络研讨会）或 Video SDK 应用程序（用于 Video SDK）并启用 RTMS 功能
- 用于 RTMS 事件的 webhook 端点
- 用于接收 WebSocket 流的服务器

> **需要 RTMS 访问权限？** 在 [Zoom 开发者论坛](https://devforum.zoom.us/) 中发布，说明您的用例以请求 RTMS 访问权限。

## 快速入门 (SDK - 推荐)

```javascript
import rtms from "@zoom/rtms";

// 所有产品的 RTMS 开始/停止事件
const RTMS_EVENTS = ["meeting.rtms_started", "webinar.rtms_started", "session.rtms_started"];

// 处理 webhook 事件
rtms.onWebhookEvent(({ event, payload }) => {
  if (!RTMS_EVENTS.includes(event)) return;

  const client = new rtms.Client();

  client.onAudioData((data, timestamp, metadata) => {
    console.log(`来自 ${metadata.userName} 的音频: ${data.length} 字节`);
  });

  client.onTranscriptData((data, timestamp, metadata) => {
    const text = data.toString('utf8');
    console.log(`${metadata.userName}: ${text}`);
  });

  client.onJoinConfirm((reason) => {
    console.log(`加入会话: ${reason}`);
  });

  // SDK 自动处理所有 WebSocket 连接
  // 透明地接受 meeting_uuid 和 session_id
  client.join(payload);
});
```

## 快速入门 (手动 WebSocket)

对于完整控制或非 SDK 语言，实现两阶段 WebSocket 协议：

```javascript
const WebSocket = require('ws');
const crypto = require('crypto');

const RTMS_EVENTS = ['meeting.rtms_started', 'webinar.rtms_started', 'session.rtms_started'];

// 1. 生成签名
// 对于会议/网络研讨会: 使用 meeting_uuid。对于 Video SDK: 使用 session_id。
function generateSignature(clientId, idValue, streamId, clientSecret) {
  const message = `${clientId},${idValue},${streamId}`;
  return crypto.createHmac('sha256', clientSecret).update(message).digest('hex');
}

// 2. 处理 webhook
app.post('/webhook', (req, res) => {
  res.status(200).send();  // 关键：立即响应！
  
  const { event, payload } = req.body;
  if (RTMS_EVENTS.includes(event)) {
    connectToRTMS(payload);
  }
});

// 3. 连接到信令 WebSocket
function connectToRTMS(payload) {
  const { server_urls, rtms_stream_id } = payload;
  // 会议/网络研讨会的 meeting_uuid，Video SDK 的 session_id
  const idValue = payload.meeting_uuid || payload.session_id;
  const signature = generateSignature(CLIENT_ID, idValue, rtms_stream_id, CLIENT_SECRET);
  
  const signalingWs = new WebSocket(server_urls);
  
  signalingWs.on('open', () => {
    signalingWs.send(JSON.stringify({
      msg_type: 1,  // 握手请求
      protocol_version: 1,
      meeting_uuid: idValue,
      rtms_stream_id,
      signature,
      media_type: 9  // AUDIO(1) | TRANSCRIPT(8)
    }));
  });
  
  // ... 处理响应，连接到媒体 WebSocket
}
```

**参见**：[手动 WebSocket 指南](examples/manual-websocket.md) 以获取完整实现。

## 媒体类型位掩码

使用按位或组合类型：

| 类型 | 值 | 描述 |
|------|-------|-------------|
| 音频 | 1 | PCM 音频样本 |
| 视频 | 2 | H.264/JPG 视频帧 |
| 屏幕共享 | 4 | **与视频分开！** |
| 字幕 | 8 | 实时语音转文本 |
| 聊天 | 16 | 会议聊天消息 |
| 所有 | 32 | 所有媒体类型 |

**示例**：音频 + 字幕 = `1 | 8` = `9`

## 关键注意事项

| 问题 | 解决方案 |
|-------|----------|
| **只允许 1 个连接** | 新连接会踢出现有连接。跟踪活动会话！ |
| **立即响应 200** | 如果 webhook 延迟，Zoom 会重试创建重复连接 |
| **心跳强制** | 响应 msg_type 12 以 msg_type 13，否则连接会断开 |
| **重新连接是您的工作** | RTMS 不自动重新连接。媒体保持活动状态容忍度现在是大约 **65 秒**；信令保持大约 **60 秒** |
| **字幕语言漂移** | 使用 `src_language` 加上 `enable_lid: false`，当您想要固定语言字幕而不是自动语言切换时 |
| **单个参与者视频** | `VIDEO_SINGLE_INDIVIDUAL_STREAM` 支持一次一个参与者。新的 `VIDEO_SUBSCRIPTION_REQ` 会覆盖先前的选择 |
| **优雅关闭现在是显式的** | 当您的后端想要干净地终止流时，使用 `STREAM_CLOSE_REQ` / `STREAM_CLOSE_RESP` |

## 环境变量

### SDK 环境变量

```bash
# 必需的 - 身份验证
ZM_RTMS_CLIENT=your_client_id          # Zoom OAuth 客户端 ID
ZM_RTMS_SECRET=your_client_secret      # Zoom OAuth 客户端密钥

# 可选的 - webhook 服务器
ZM_RTMS_PORT=8080                      # 默认：8080
ZM_RTMS_PATH=/webhook                  # 默认：/

# 可选的 - 日志记录
ZM_RTMS_LOG_LEVEL=info                 # error, warn, info, debug, trace
ZM_RTMS_LOG_FORMAT=progressive         # progressive 或 json
ZM_RTMS_LOG_ENABLED=true
```

### 手动实现变量

```bash
ZOOM_CLIENT_ID=your_client_id
ZOOM_CLIENT_SECRET=your_client_secret
ZOOM_SECRET_TOKEN=your_webhook_token   # 用于 webhook 验证
```

## Zoom 应用程序设置

### 用于会议和网络研讨会（普通应用程序）

1. 前往 [marketplace.zoom.us](https://marketplace.zoom.us) -> Develop -> Build App
2. 选择 **普通应用程序** -> **User-Managed**
3. 功能 -> 访问 -> **启用事件订阅**
4. 添加事件 -> 搜索 "rtms" -> 选择：
   - `meeting.rtms_started`
   - `meeting.rtms_stopped`
   - `webinar.rtms_started`（如果使用网络研讨会）
   - `webinar.rtms_stopped`（如果使用网络研讨会）
5. 权限 -> 添加权限 -> 搜索 "rtms" -> 添加：
   - `meeting:read:meeting_audio`
   - `meeting:read:meeting_video`
   - `meeting:read:meeting_transcript`
   - `meeting:read:meeting_chat`
   - `webinar:read:webinar_audio`（如果使用网络研讨会）
   - `webinar:read:webinar_video`（如果使用网络研讨会）
   - `webinar:read:webinar_transcript`（如果使用网络研讨会）
   - `webinar:read:webinar_chat`（如果使用网络研讨会）

### 用于 Video SDK（Video SDK 应用程序）

1. 前往 [marketplace.zoom.us](https://marketplace.zoom.us) -> Develop -> Build App
2. 选择 **Video SDK 应用程序**
3. 使用您的 SDK Key 和 SDK Secret（不是 OAuth 客户端 ID/密钥）
4. 添加事件：
   - `session.rtms_started`
   - `session.rtms_stopped`

## 示例存储库

### 官方示例

| 存储库 | 描述 |
|------------|-------------|
| [rtms-samples](https://github.com/zoom/rtms-samples) | RTMSManager、基础模板、AI 示例 |
| [rtms-quickstart-js](https://github.com/zoom/rtms-quickstart-js) | JavaScript SDK 快速入门 |
| [rtms-quickstart-py](https://github.com/zoom/rtms-quickstart-py) | Python SDK 快速入门 |
| [rtms-sdk-cpp](https://github.com/zoom/rtms-sdk-cpp) | C++ SDK |
| [zoom-rtms](https://github.com/zoom/rtms) | 主要 SDK 存储库 |

### AI 集成示例

| 示例 | 描述 |
|--------|-------------|
| [rtms-meeting-assistant-starter-kit](https://github.com/zoom/rtms-meeting-assistant-starter-kit) | 具有摘要的 AI 会议助手 |
| [arlo-meeting-assistant](https://github.com/zoom/arlo-meeting-assistant) | 具有数据库的生产会议助手 |
| [videosdk-rtms-transcribe-audio](https://github.com/zoom/videosdk-rtms-transcribe-audio) | Whisper 字幕 |

## 完整文档

### 概念
- **[连接架构](concepts/connection-architecture.md)** - 两阶段 WebSocket 设计
- **[生命周期流](concepts/lifecycle-flow.md)** - webhook 到流式传输流

### 示例
- **[SDK 快速入门](examples/sdk-quickstart.md)** - 使用 @zoom/rtms SDK
- **[手动 WebSocket](examples/manual-websocket.md)** - 原始协议实现
- **[RTMS 机器人](examples/rtms-bot.md)** - 完整机器人实现指南
- **[AI 集成](examples/ai-integration.md)** - 字幕和分析模式

### 参考
- **[媒体类型](references/media-types.md)** - 音频、视频、字幕、聊天、屏幕共享
- **[数据类型](references/data-types.md)** - 所有枚举和常量
- **[连接](references/connection.md)** - WebSocket 协议详细信息
- **[Webhooks](references/webhooks.md)** - 事件订阅

### 故障排除
- **[常见问题](troubleshooting/common-issues.md)** - 常见问题解答和解决方案

## 资源

- **官方文档**：https://developers.zoom.us/docs/rtms/
- **数据类型**：https://developers.zoom.us/docs/rtms/data-types/
- **媒体参数**：https://developers.zoom.us/docs/rtms/media-parameter-definition/
- **开发者论坛**：https://devforum.zoom.us/

---

**需要帮助？** 从下方的集成索引部分开始，以获取完整导航。

---

## 集成索引

本节从 `SKILL.md` 迁移而来。

RTMS 提供实时访问 Zoom 会议、网络研讨会和 Video SDK 会话的实时音频、视频、字幕、聊天和屏幕共享的能力。

## 关键定位

将 RTMS 视为 **后端服务**，用于接收和处理媒体流。

- 后端角色：摄取音频/视频/共享/聊天/字幕，运行 AI/分析，持久化/转发数据。
- 可选前端角色：Zoom 应用程序 SDK 或 Web 仪表板，从后端传输（WebSocket/SSE/其他）消耗处理后的流数据。
- 启动模型：后端等待 RTMS 开始 webhook 事件，然后开始流处理。

不要将 RTMS 模型化为仅限前端 SDK。

## 快速入门路径

**如果您是 RTMS 新手，请按此顺序操作：**

1. **首先运行预检检查** -> [RUNBOOK.md](RUNBOOK.md)
2. **了解架构** -> [concepts/connection-architecture.md](concepts/connection-architecture.md)
   - 两阶段 WebSocket：信令 + 媒体
   - 为什么 RTMS 不使用机器人

3. **选择您的方案** -> SDK 或手动
   - SDK（推荐）：[examples/sdk-quickstart.md](examples/sdk-quickstart.md)
   - 手动 WebSocket：[examples/manual-websocket.md](examples/manual-websocket.md)

4. **了解生命周期** -> [concepts/lifecycle-flow.md](concepts/lifecycle-flow.md)
   - Webhook -> 信令 -> 媒体 -> 流式传输

5. **配置媒体类型** -> [references/media-types.md](references/media-types.md)
   - 音频、视频、字幕、聊天、屏幕共享

6. **解决问题** -> [troubleshooting/common-issues.md](troubleshooting/common-issues.md)
   - 连接问题、重复 webhook、缺失数据

---

## 文档结构

```
rtms/
├── SKILL.md                           # 主要技能概述
├── SKILL.md                           # 本文件 - 导航指南
│
├── concepts/                          # 核心架构模式
│   ├── connection-architecture.md     # 两阶段 WebSocket 设计
│   └── lifecycle-flow.md              # 从 Webhook 到流媒体处理流程
│
├── examples/                          # 完整可用的代码示例
│   ├── sdk-quickstart.md              # 使用 @zoom/rtms SDK
│   ├── manual-websocket.md            # 原始协议实现
│   ├── rtms-bot.md                    # 完整的 RTMS 机器人实现
│   └── ai-integration.md              # 语音转录与分析
│
├── references/                        # 参考文档
│   ├── media-types.md                 # 音频、视频、文字记录、聊天、屏幕共享
│   ├── data-types.md                  # 所有枚举和常量
│   ├── connection.md                  # WebSocket 协议细节
│   └── webhooks.md                    # 事件订阅
│
└── troubleshooting/                   # 问题解决指南
    └── common-issues.md               # 常见问题及解决方案
```

---

## 按使用场景

### 我想获取会议转录文本
1. [SDK 快速入门](examples/sdk-quickstart.md) - 最快的方式
2. [媒体类型](references/media-types.md#transcript) - 转录配置
3. [AI 集成](examples/ai-integration.md) - Whisper、Deepgram、AssemblyAI

### 我想录制会议
1. [媒体类型](references/media-types.md) - 音频 + 视频配置
2. [SDK 快速入门](examples/sdk-quickstart.md) - 接收媒体流
3. [AI 集成](examples/ai-integration.md#audio-recording) - 间隙填充录制

### 我想构建 AI 会议助手
1. [AI 集成](examples/ai-integration.md) - 完整模式
2. [SDK 快速入门](examples/sdk-quickstart.md) - 媒体摄入
3. [生命周期流程](concepts/lifecycle-flow.md) - 事件处理

### 我想构建完整的 RTMS 机器人
1. [RTMS 机器人](examples/rtms-bot.md) - **完整实现指南**
2. [生命周期流程](concepts/lifecycle-flow.md) - 从 Webhook 到流媒体处理流程
3. [连接架构](concepts/connection-architecture.md) - 两阶段设计

### 我需要完全控制协议
1. [手动 WebSocket](examples/manual-websocket.md) - **从这里开始**
2. [连接架构](concepts/connection-architecture.md) - 两阶段设计
3. [数据类型](references/data-types.md) - 所有消息类型和枚举
4. [连接](references/connection.md) - 协议细节

### 我遇到连接错误
1. [常见问题](troubleshooting/common-issues.md) - 诊断清单
2. [连接架构](concepts/connection-architecture.md) - 验证流程
3. [Webhooks](references/webhooks.md) - 验证与时序

### 我想理解架构
1. [连接架构](concepts/connection-architecture.md) - 两阶段 WebSocket
2. [生命周期流程](concepts/lifecycle-flow.md) - 完整流程图
3. [数据类型](references/data-types.md) - 协议常量

---

## 按产品

### 我为 Zoom 会议构建
- 标准 RTMS 设置。Webhook 事件：`meeting.rtms_started`。使用带有 OAuth 的通用应用。
- 从 [SDK 快速入门](examples/sdk-quickstart.md) 或 [手动 WebSocket](examples/manual-websocket.md) 开始。

### 我为 Zoom 网络研讨会构建
- 与会议相同，但 Webhook 事件为 `webinar.rtms_started`。载荷仍使用 `meeting_uuid`（而非 `webinar_uuid`）。
- 添加网络研讨会作用域和事件订阅。参见 [Webhooks](references/webhooks.md)。
- 仅确认 **panelist（主持人/嘉宾）** 流可用。与会者流可能不是独立的。

### 我为 Zoom Video SDK 构建
- Webhook 事件：`session.rtms_started`。载荷使用 `session_id`（而非 `meeting_uuid`）。
- 需要一个 **Video SDK 应用**，包含 SDK Key/Secret（而非 OAuth Client ID/Secret）。
- 连接建立后，协议与会议 **完全相同**。
- 载荷详情请参见 [Webhooks](references/webhooks.md)。

---

## 关键文档

### 1. 连接架构（至关重要）
**[concepts/connection-architecture.md](concepts/connection-architecture.md)**

RTMS 使用 **两个独立的 WebSocket 连接**：
- **信令 WebSocket**：身份验证、控制、心跳
- **媒体 WebSocket**：实际的音频/视频/文字记录数据

### 2. SDK 与手动（决策点）
**[examples/sdk-quickstart.md](examples/sdk-quickstart.md)** 对比 **[examples/manual-websocket.md](examples/manual-websocket.md)**

| SDK | 手动 |
|-----|--------|
| 处理 WebSocket 复杂性 | 完全控制协议 |
| 自动重连 | 自行实现重连 |
| 代码更少 | 代码更多 |
| 最适合大多数使用场景 | 最适合自定义需求 |

### 3. 关键陷阱（最常见的问题）
**[troubleshooting/common-issues.md](troubleshooting/common-issues.md)**

1. **立即响应 200** - 延迟的 Webhook 响应会导致重复
2. **每个流仅限 1 个连接** - 新连接会踢出已有连接
3. **需要心跳** - 必须响应保活机制，否则连接会断开
4. **跟踪活跃会话** - 防止重复加入尝试

---

## 关键经验

### 重要发现：

1. **两阶段 WebSocket 设计**
   - 信令：控制平面（握手、心跳、开始/停止）
   - 媒体：数据平面（音频、视频、文字记录、聊天、共享）
   - 参见：[连接架构](concepts/connection-architecture.md)

2. **Webhook 响应时序**
   - 必须在任何处理之前响应 200
   - 延迟响应 -> Zoom 重试 -> 连接重复
   - 参见：[常见问题](troubleshooting/common-issues.md#webhook-response-timing)

3. **心跳是强制的**
   - 信令：接收 msg_type 12，使用 msg_type 13 响应
   - 媒体：相同模式
   - 未响应 = 连接关闭
   - 参见：[连接](references/connection.md#heartbeat)

4. **签名生成**
   - 格式：`HMAC-SHA256(clientSecret, "clientId,meetingUuid,streamId")`
   - 对于 Video SDK，使用 `session_id` 替代 `meetingUuid`
   - 网络研讨会仍使用 `meeting_uuid`（而非 `webinar_uuid`）
   - 信令和媒体握手均需要此签名
   - 参见：[手动 WebSocket](examples/manual-websocket.md#signature-generation)

5. **媒体类型是位掩码**
   - 音频=1，视频=2，共享=4，文字记录=8，聊天=16，全部=32
   - 使用 OR 组合：音频+文字记录 = 1|8 = 9
   - 参见：[媒体类型](references/media-types.md)

6. **屏幕共享与视频是分开的**
   - 不同的 msg_type（16 对比 15）
   - 不同的媒体标志（4 对比 2）
   - 必须分别订阅
   - 参见：[媒体类型](references/media-types.md#screen-share)

---

## 快速参考

### "连接失败"
-> [常见问题](troubleshooting/common-issues.md)

### "连接重复"
-> [Webhook 时序](troubleshooting/common-issues.md#webhook-response-timing)

### "没有音频/视频数据"
-> [媒体类型](references/media-types.md) - 检查配置

### "如何手动实现？"
-> [手动 WebSocket](examples/manual-websocket.md)

### "存在哪些消息类型？"
-> [数据类型](references/data-types.md)

### "如何集成 AI？"
-> [AI 集成](examples/ai-integration.md)

---

## 文档版本

基于 **Zoom RTMS SDK v1.x** 以及截至 2026 年的官方文档。

---

**祝你编码愉快！**

记住：从 [SDK 快速入门](examples/sdk-quickstart.md) 开始以获取最快路径，或者如果你需要完全控制，请使用 [手动 WebSocket](examples/manual-websocket.md)。
