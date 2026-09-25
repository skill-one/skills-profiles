# /build-zoom-rest-api-app

确定性服务器端 Zoom 自动化和资源管理的背景参考。优先考虑 `plan-zoom-product`、`plan-zoom-integration` 或 `debug-zoom`，然后在此处路由以获取端点级别的详细信息。

# Zoom REST API

使用 Zoom REST API 构建服务器端集成的专家指南。此 API 提供 600 多个端点，用于以编程方式管理会议、用户、网络研讨会、录制、报告和所有 Zoom 平台资源。

**官方文档**：https://developers.zoom.us/api-hub/
**API Hub 参考**：https://developers.zoom.us/api-hub/meetings/
**OpenAPI 清单**：`https://developers.zoom.us/api-hub/<domain>/methods/endpoints.json`

## 快速链接

**新接触 Zoom REST API？请遵循此路径：**

1. **[API 架构](concepts/api-architecture.md)** - 基础 URL、区域 URL、`me` 关键字、ID 与 UUID、时间格式
2. **[认证流程](concepts/authentication-flows.md)** - OAuth 设置（S2S、用户、PKCE、设备代码）
3. **[会议 URL 与会议 SDK](concepts/meeting-urls-and-sdk-joining.md)** - 停止将 `join_url` 与会议 SDK 混用
4. **[会议生命周期](examples/meeting-lifecycle.md)** - 创建 → 更新 → 开始 → 结束 → 删除，并使用 webhook
5. **[速率限制策略](concepts/rate-limiting-strategy.md)** - 计划层级、每个用户的限制、重试模式

**参考：**
- **[会议](references/meetings.md)** - 会议 CRUD、类型、设置
- **[用户](references/users.md)** - 用户配置和管理
- **[录制](references/recordings.md)** - 云录制访问和下载
- **[AI 服务](references/ai-services.md)** - Scribe 端点清单和当前 AI 服务路径表面
- **[GraphQL 查询](examples/graphql-queries.md)** - 可选查询 API（测试版）
- **集成索引** - 查看此文件中的下方部分

大多数 `references/` 下的域文件都与官方 API Hub `endpoints.json` 清单对齐。将那些文件视为方法/路径发现的本地真实来源。

**遇到问题？**
- 从预检开始 → [5-Minute Runbook](RUNBOOK.md)
- 401 未授权 → [认证流程](concepts/authentication-flows.md)（检查令牌过期、范围）
- 429 请求过多 → [速率限制策略](concepts/rate-limiting-strategy.md)
- 错误代码 → [常见错误](troubleshooting/common-errors.md)
- 分页混淆 → [常见问题](troubleshooting/common-issues.md)
- Webhook 未到达 → [Webhook 服务器](examples/webhook-server.md)
- 论坛派生的常见问题 → [论坛顶级问题](troubleshooting/forum-top-questions.md)
- 令牌/范围失败 → [令牌 + 范围演练](troubleshooting/token-scope-playbook.md)

**构建事件驱动集成？**
- [Webhook 服务器](examples/webhook-server.md) - 带有 CRC 验证的 Express.js 服务器
- [录制管道](examples/recording-pipeline.md) - 通过 webhook 事件自动下载

## 快速入门

### 获取访问令牌（服务器到服务器 OAuth）

```bash
curl -X POST "https://zoom.us/oauth/token" \
  -H "Authorization: Basic $(echo -n 'CLIENT_ID:CLIENT_SECRET' | base64)" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=account_credentials&account_id=ACCOUNT_ID"
```

响应：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "scope": "meeting:read meeting:write user:read"
}
```

### 创建会议

```bash
curl -X POST "https://api.zoom.us/v2/users/HOST_USER_ID/meetings" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "团队站会",
    "type": 2,
    "start_time": "2025-03-15T10:00:00Z",
    "duration": 30,
    "settings": {
      "join_before_host": false,
      "waiting_room": true
    }
  }'
```

对于 S2S OAuth，在路径中使用显式的主持人用户 ID 或电子邮件。不要使用 `me`。

### 列出用户并分页

```bash
curl "https://api.zoom.us/v2/users?page_size=300&status=active" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

## 基础 URL

```
https://api.zoom.us/v2
```

### 区域基础 URL

OAuth 令牌响应中的 `api_url` 字段指示用户的区域。为数据驻留合规性使用区域 URL：

| 区域 | URL |
|--------|-----|
| 全球（默认） | `https://api.zoom.us/v2` |
| 澳大利亚 | `https://api-au.zoom.us/v2` |
| 加拿大 | `https://api-ca.zoom.us/v2` |
| 欧洲联盟 | `https://api-eu.zoom.us/v2` |
| 印度 | `https://api-in.zoom.us/v2` |
| 沙特阿拉伯 | `https://api-sa.zoom.us/v2` |
| 新加坡 | `https://api-sg.zoom.us/v2` |
| 英国 | `https://api-uk.zoom.us/v2` |
| 美国 | `https://api-us.zoom.us/v2` |

**注意：** 无论 `api_url` 值如何，您始终可以使用全球 URL `https://api.zoom.us`。

## 关键功能

| 功能 | 描述 |
|---------|-------------|
| **会议管理** | 具有完整调度控制的创建、读取、更新、删除会议 |
| **用户配置** | 自动化用户生命周期（创建、更新、停用、删除） |
| **网络研讨会操作** | 网络研讨会 CRUD、注册者管理、主持人控制 |
| **云录制** | 带文件类型过滤的列出、下载、删除录制 |
| **报告和分析** | 使用情况报告、参与者数据、每日统计数据 |
| **团队聊天** | 频道管理、消息传递、聊天机器人集成 |
| **Zoom 电话** | 电话管理、语音留言、呼叫路由 |
| **Zoom 会议室** | 会议室管理、设备控制、调度 |
| **Webhooks** | 100 多种事件类型的实时事件通知 |
| **WebSockets** | 无公共端点的持久事件流 |
| **GraphQL（测试版）** | `v3/graphql` 的单端点灵活查询 |
| **AI 伴侣** | 会议摘要、文本记录、AI 生成内容 |
| **AI 服务 / Scribe** | 通过 Build 平台 JWT 认证端点进行文件和存档转录 |

## 前提条件

- Zoom 账户（免费层具有 API 访问权限，但速率限制较低）
- 在 [Zoom 应用市场](https://marketplace.zoom.us/) 上注册的应用
- OAuth 凭据（服务器到服务器 OAuth 或用户 OAuth）
- 目标端点的适当范围

> **需要帮助进行认证？** 查看 **[zoom-oauth](../oauth/SKILL.md)** 技能以获取完整的 OAuth 流程实现。

## 重大注意事项和最佳实践

### ⚠️ JWT 应用类型已弃用

JWT 应用类型已弃用。迁移到 **服务器到服务器 OAuth**。这不会影响视频 SDK 中使用的 JWT 令牌签名——仅适用于 Marketplace 的“JWT”应用类型，用于 REST API 访问。

```javascript
// 旧版（JWT 应用类型 - 已弃用）
const token = jwt.sign({ iss: apiKey, exp: expiry }, apiSecret);

// 新版（服务器到服务器 OAuth）
const token = await getServerToServerToken(accountId, clientId, clientSecret);
```

### ⚠️ `me` 关键字规则

- **用户级 OAuth 应用**：必须使用 `me` 而不是 `userId`（否则：无效令牌错误）
- **服务器到服务器 OAuth 应用**：必须不使用 `me`——提供实际的 `userId` 或电子邮件
- **帐户级 OAuth 应用**：可以使用 `me` 或 `userId`

### ⚠️ 会议 ID 与 UUID——双重编码

以 `/` 开头或包含 `//` 的 UUID 必须**双重 URL 编码**：

```javascript
// UUID: /abc==
// 单次编码: %2Fabc%3D%3D
// 双次编码: %252Fabc%253D%253D  ← 使用这个

const uuid = '/abc==';
const encoded = encodeURIComponent(encodeURIComponent(uuid));
const url = `https://api.zoom.us/v2/meetings/${encoded}`;
```

### ⚠️ 时间格式

- `yyyy-MM-ddTHH:mm:ssZ` — **UTC 时间**（注意 `Z` 后缀）
- `yyyy-MM-ddTHH:mm:ss` — **本地时间**（无 `Z`，使用 `timezone` 字段）
- 一些报告 API 仅接受 UTC。检查每个端点的 API 参考。

### ⚠️ 速率限制是按帐户而不是按应用

同一 Zoom 帐户上的所有应用都**共享**速率限制。一个重量级应用可能会影响其他应用。主动监控 `X-RateLimit-Remaining` 标头。

### ⚠️ 每个用户的每日限制

会议/网络研讨会创建/更新操作限制为**每天每个用户 100 次**（在 00:00 UTC 重置）。在执行批量操作时，将操作分布在不同的主持人用户之间。

### ⚠️ 下载 URL 需要认证并跟随重定向

录制 `download_url` 值需要 Bearer 令牌认证，并且可能会重定向。始终跟随重定向：

```bash
curl -L -H "Authorization: Bearer ACCESS_TOKEN" "https://zoom.us/rec/download/..."
```

### 使用 Webhooks 而不是轮询

```javascript
// 不要：每分钟轮询（浪费 API 配额）
setInterval(() => getMeetings(), 60000);

// 要：实时接收 webhook 事件
app.post('/webhook', (req, res) => {
  if (req.body.event === 'meeting.started') {
    handleMeetingStarted(req.body.payload);
  }
  res.status(200).send();
});
```

> **Webhook 设置详细信息：** 查看 **[zoom-webhooks](../webhooks/SKILL.md)** 技能以获取全面 webhook 实现。

## 完整文档库

此技能包括按类别组织的全面指南：

### 核心概念
- **[API 架构](concepts/api-architecture.md)** - REST 设计、基础 URL、区域路由、`me` 关键字、ID 与 UUID、时间格式
- **[认证流程](concepts/authentication-flows.md)** - 所有 OAuth 流程（S2S、用户、PKCE、设备）
- **[速率限制策略](concepts/rate-limiting-strategy.md)** - 按计划限制、重试模式、请求排队

### 完整示例
- **[会议生命周期](examples/meeting-lifecycle.md)** - 创建→更新→开始→结束→删除
- **[用户管理](examples/user-management.md)** - CRUD 用户、分页、批量操作
- **[录制管道](examples/recording-pipeline.md)** - 通过 webhooks 下载录制
- **[Webhook 服务器](examples/webhook-server.md)** - 带有 CRC + 签名验证的 Express.js 服务器
- **[GraphQL 查询](examples/graphql-queries.md)** - 查询、变异、分页

### 故障排除
- **[常见错误](troubleshooting/common-errors.md)** - HTTP 状态代码、Zoom 错误代码表
- **[常见问题](troubleshooting/common-issues.md)** - 速率限制、令牌、分页陷阱

### 参考（39 个文件涵盖所有 Zoom API 域）

#### 核心 API
- **[references/meetings.md](references/meetings.md)** - 会议 CRUD、类型、设置
- **[references/users.md](references/users.md)** - 用户配置、类型、范围
- **[references/webinars.md](references/webinars.md)** - 网络研讨会管理、注册者
- **[references/recordings.md](references/recordings.md)** - 云录制
- **[references/reports.md](references/reports.md)** - 使用报告、分析
- **[references/accounts.md](references/accounts.md)** - 帐户管理

#### 通信
- **[references/team-chat.md](references/team-chat.md)** - 团队聊天
- **[references/chatbot.md](references/chatbot.md)** - 聊天机器人
- **[references/phone.md](references/phone.md)** - Zoom 电话
- **[references/mail.md](references/mail.md)** - Zoom 邮件
- **[references/calendar.md](references/calendar.md)** - Zoom 日历

#### 基础设施
- **[references/rooms.md](references/rooms.md)** - Zoom 会议室
- **[references/scim2.md](references/scim2.md)** - SCIM 2.0 配置 API
- **[references/rate-limits.md](references/rate-limits.md)** - 速率限制详细信息
- **[references/qss.md](references/qss.md)** - 服务质量管理订阅

#### 高级
- **[references/graphql.md](references/graphql.md)** - GraphQL API（测试版）
- **[references/ai-companion.md](references/ai-companion.md)** - AI 功能
- **[references/authentication.md](references/authentication.md)** - 认证参考
- **[references/openapi.md](references/openapi.md)** - OpenAPI 规范、Postman、代码生成

#### 其他 API 域
- **[references/events.md](references/events.md)** - 事件和事件平台 API
- **[references/scheduler.md](references/scheduler.md)** - Zoom 调度器 API
- **[references/tasks.md](references/tasks.md)** - 任务 API
- **[references/whiteboard.md](references/whiteboard.md)** - 白板 API
- **[references/video-management.md](references/video-management.md)** - 视频管理 API
- **[references/video-sdk-api.md](references/video-sdk-api.md)** - 视频 SDK REST API
- **[references/marketplace-apps.md](references/marketplace-apps.md)** - 市场place 应用管理
- **[references/commerce.md](references/commerce.md)** - 商务和计费 API
- **[references/contact-center.md](references/contact-center.md)** - 客服 API
- **[references/quality-management.md](references/quality-management.md)** - 质量管理 API
- **[references/workforce-management.md](references/workforce-management.md)** - 劳动力管理 API
- **[references/healthcare.md](references/healthcare.md)** - 医疗保健 API
- **[references/auto-dialer.md](references/auto-dialer.md)** - 自动拨号器 API
- **[references/number-management.md](references/number-management.md)** - 电话管理 API
- **[references/revenue-accelerator.md](references/revenue-accelerator.md)** - 收入加速器 API
- **[references/virtual-agent.md](references/virtual-agent.md)** - 虚拟代理 API
- **[references/cobrowse-sdk-api.md](references/cobrowse-sdk-api.md)** - Cobrowse SDK API
- **[references/crc.md](references/crc.md)** - 云会议室连接器 API
- **[references/clips.md](references/clips.md)** - Clips API
- **[references/zoom-docs.md](references/zoom-docs.md)** - Zoom 文档和源参考

## 示例存储库

### 官方（由 Zoom 提供）

| 类型 | 存储库 |
|------|------------|
| OAuth 示例 | [oauth-sample-app](https://github.com/zoom/oauth-sample-app) |
| S2S OAuth 启动器 | [server-to-server-oauth-starter-api](https://github.com/zoom/server-to-server-oauth-starter-api) |
| 用户 OAuth | [user-level-oauth-starter](https://github.com/zoom/user-level-oauth-starter) |
| S2S 令牌 | [server-to-server-oauth-token](https://github.com/zoom/server-to-server-oauth-token) |
| Rivet 库 | [rivet-javascript](https://github.com/zoom/rivet-javascript) |
| WebSocket 示例 | [websocket-js-sample](https://github.com/zoom/websocket-js-sample) |
| Webhook 示例 | [webhook-sample-node.js](https://github.com/zoom/webhook-sample-node.js) |
| Python S2S | [server-to-server-python-sample](https://github.com/zoom/server-to-server-python-sample) |

## 资源

- **API 参考**：https://developers.zoom.us/api-hub/
- **GraphQL Playground**：https://nws.zoom.us/graphql/playground
- **Postman 集合**：https://marketplace.zoom.us/docs/api-reference/postman
- **开发者论坛**：https://devforum.zoom.us/
- **版本更新日志**：https://developers.zoom.us/changelog/
- **状态页面**：https://status.zoom.us/

---

**需要帮助？** 从下方此文件的集成索引部分开始以获取完整导航。

---

## 集成索引

_此部分从 `SKILL.md` 迁移而来。_

## 快速入门路径

**如果您是 Zoom REST API 的新手，请按此顺序操作：**

1. **首先运行预检** → [RUNBOOK.md](RUNBOOK.md)

2. **了解 API 设计** → [concepts/api-architecture.md](concepts/api-architecture.md)
   - 基础 URL、区域端点、`me` 关键字规则
   - 会议 ID 与 UUID、双重编码、时间格式

3. **设置认证** → [concepts/authentication-flows.md](concepts/authentication-flows.md)
   - 服务器到服务器 OAuth（后端自动化）
   - 用户 OAuth with PKCE（面向用户的 App）
   - 交叉参考：[zoom-oauth](../oauth/SKILL.md)

4. **创建您的第一个会议** → [examples/meeting-lifecycle.md](examples/meeting-lifecycle.md)
   - 完整 CRUD，使用 curl 和 Node.js 示例
   - webhook 事件集成

5. **处理速率限制** → [concepts/rate-limiting-strategy.md](concepts/rate-limiting-strategy.md)
   - 按计划限制、重试模式、请求排队

6. **设置 webhook** → [examples/webhook-server.md](examples/webhook-server.md)
   - CRC 验证、签名验证、事件处理

7. **解决问题** → [troubleshooting/common-issues.md](troubleshooting/common-issues.md)
   - 令牌刷新、分页陷阱、常见陷阱

---

## 文档结构

```
rest-api/
├── SKILL.md                              # 主技能概述 + 快速入门
├── SKILL.md                              # 此文件 - 导航指南
│
├── concepts/                             # 核心架构概念
│   ├── api-architecture.md              # REST 设计、URL、ID、时间格式
│   ├── authentication-flows.md          # OAuth 流程 (S2S, User, PKCE, Device)
│   └── rate-limiting-strategy.md        # 按计划限制、重试、排队
│
├── examples/                             # 完整工作代码
│   ├── meeting-lifecycle.md             # 创建→更新→开始→结束→删除
│   ├── user-management.md              # CRUD 用户、分页、批量操作
│   ├── recording-pipeline.md           # 通过 webhooks 下载录制
│   ├── webhook-server.md               # Express.js CRC + 签名验证
│   └── graphql-queries.md              # GraphQL 查询、变异、分页
│
├── troubleshooting/                      # 问题解决
│   ├── common-errors.md                # HTTP 代码、Zoom 错误代码表
│   └── common-issues.md               # 速率限制、令牌、分页陷阱
│
└── references/                           # 39 个域特定参考文件
    ├── authentication.md                # 认证方法参考
    ├── meetings.md                      # 会议端点
    ├── users.md                         # 用户管理端点
    ├── webinars.md                      # 网络研讨会端点
    ├── recordings.md                    # 云录制端点
    ├── reports.md                       # 报告和分析
    ├── accounts.md                      # 帐户管理
    ├── rate-limits.md                   # 速率限制详细信息
    ├── graphql.md                       # GraphQL API (测试版)
    ├── zoom-team-chat.md                     # 团队聊天消息传递
    ├── chatbot.md                       # 聊天机器人集成
    ├── phone.md                         # Zoom 电话
    ├── rooms.md                         # Zoom 会议室
    ├── calendar.md                      # Zoom 日历
    ├── mail.md                          # Zoom 邮件
    ├── ai-companion.md                  # AI 功能
    ├── openapi.md                       # OpenAPI 规范
    ├── qss.md                           # 服务质量管理
    ├── contact-center.md                # 客服 API
    ├── events.md                        # Zoom 事件
    ├── whiteboard.md                    # 白板
    ├── clips.md                         # Zoom Clips
    ├── scheduler.md                     # 调度器
    ├── scim2.md                         # SCIM 2.0
    ├── marketplace-apps.md              # 应用管理
    ├── zoom-video-sdk-api.md                 # 视频 SDK REST
    └️ ... (39 个文件)
```

---

## 按用例划分

### 我想创建和管理会议
1. [API 架构](concepts/api-architecture.md) - 基础 URL、时间格式
2. [会议生命周期](examples/meeting-lifecycle.md) - 完整 CRUD + webhook 事件
3. [会议参考](references/meetings.md) - 所有端点、类型、设置

### 我想以编程方式管理用户
1. [用户管理](examples/user-management.md) - CRUD、分页、批量操作
2. [用户参考](references/users.md) - 端点、用户类型、范围

### 我想自动下载录制
1. [录制管道](examples/recording-pipeline.md) - webhook 触发的下载
2. [录制参考](references/recordings.md) - 文件类型、下载认证

### 我想接收实时事件
1. [Webhook 服务器](examples/webhook-server.md) - CRC 验证、签名检查
2. 交叉参考：[zoom-webhooks](../webhooks/SKILL.md) 以获取全面的 webhook 文档
3. 交叉参考：[zoom-websockets](../websockets/SKILL.md) 以获取 WebSocket 事件

### 我想使用 GraphQL 而不是 REST
1. [GraphQL 查询](examples/graphql-queries.md) - 查询、变异、分页
2. [GraphQL 参考](references/graphql.md) - 可用实体、范围、速率限制

### 我想设置认证
1. [认证流程](concepts/authentication-flows.md) - 所有 OAuth 方法
2. 交叉参考：[zoom-oauth](../oauth/SKILL.md) 以获取完整的 OAuth 实现

### 我遇到了速率限制
1. [速率限制策略](concepts/rate-limiting-strategy.md) - 按计划限制、策略
2. [速率限制参考](references/rate-limits.md) - 详细表格
3. [常见问题](troubleshooting/common-issues.md) - 实用解决方案

### 我遇到了错误
1. [常见错误](troubleshooting/common-errors.md) - 错误代码表
2. [常见问题](troubleshooting/common-issues.md) - 诊断工作流

### 我想构建网络研讨会
1. [网络研讨会参考](references/webinars.md) - 端点、类型、注册者
2. [会议生命周期](examples/meeting-lifecycle.md) - 类似模式适用

### 我想集成 Zoom 电话
1. [电话参考](references/phone.md) - 电话 API 端点
2. [速率限制策略](concepts/rate-limiting-strategy.md) - 电话速率限制
