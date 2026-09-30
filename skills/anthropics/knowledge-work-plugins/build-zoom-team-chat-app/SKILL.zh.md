---
name: build-zoom-team-chat-app
description: Zoom 团队聊天参考技能。在构建用户范围的消息集成、聊天机器人体验、丰富卡片、按钮、斜杠命令或聊天网络钩子时，用于路由到聊天工作流之后。
---

# /构建-zoom团队聊天应用

用于 Zoom 团队聊天集成的背景参考。在流程清晰后使用此文档，尤其是在团队聊天 API 与聊天机器人 API 的区别很重要时。

## 首先阅读（关键）

有两种不同的集成类型，它们不能互换：

1. **团队聊天 API（用户类型）**
   - 以真实认证用户身份发送消息
   - 使用 **用户 OAuth** (`authorization_code`)
   - 端点系列：`/v2/chat/users/...`

2. **聊天机器人 API（机器人类型）**
   - 以您的机器人身份发送消息
   - 使用 **客户端凭证** (`client_credentials`)
   - 端点系列：`/v2/im/chat/messages`

如果早期选择了错误的类型，认证/范围/端点都会不匹配，导致实现失败。

**官方文档**：[https://developers.zoom.us/docs/team-chat/](https://developers.zoom.us/docs/team-chat/)  
**聊天机器人文档**：[https://developers.zoom.us/docs/team-chat/chatbot/extend/](https://developers.zoom.us/docs/team-chat/chatbot/extend/)  
**API 参考**：[https://developers.zoom.us/docs/api/rest/reference/chatbot/](https://developers.zoom.us/docs/api/rest/reference/chatbot/)

## 快速链接

**新接触团队聊天？请遵循此路径：**

1. **[入门](get-started.md)** - 端到端快速路径（用户类型与机器人类型）
2. **[选择您的 API](concepts/api-selection.md)** - 团队聊天 API 与 Chatbot API
3. **[环境设置](concepts/environment-setup.md)** - 凭证、范围、应用配置
4. **[OAuth 设置](examples/oauth-setup.md)** - 完整的认证流程
5. **[发送第一条消息](examples/send-message.md)** - 用于发送消息的工作代码

**参考：**
- **[聊天机器人消息卡片](references/message-cards.md)** - 完整的卡片组件参考
- **[Webhook 事件](references/webhook-events.md)** - 所有 webhook 事件类型
- **[API 参考](references/api-reference.md)** - 端点、方法、参数
- **[示例应用](references/samples.md)** - 10+ 官方示例应用
- **集成索引** - 查看本文件下方的本节

**遇到问题？**
- 认证错误 → [OAuth 故障排除](troubleshooting/oauth-issues.md)
- Webhook 未接收事件 → [Webhook 设置指南](troubleshooting/webhook-issues.md)
- 消息未发送 → [常见问题](troubleshooting/common-issues.md)
- 从快速检查开始 → [5 分钟运行手册](RUNBOOK.md)

**OAuth 端点检查：**
- 授权 URL：`https://zoom.us/oauth/authorize`
- 令牌 URL：`https://zoom.us/oauth/token`
- 如果 `/oauth/token` 返回 404/HTML，请使用 `https://zoom.us/oauth/token`。

**构建交互式机器人？**
- [按钮操作](examples/button-actions.md) - 处理按钮点击
- [表单提交](examples/form-submissions.md) - 处理表单数据
- [斜杠命令](examples/slash-commands.md) - 创建自定义命令

## 快速决策：使用哪个 API？

| 使用场景 | 应用的 API |
|----------|------------|
| 从脚本/CI/CD 发送通知 | **团队聊天 API** |
| 以用户身份自动发送消息 | **团队聊天 API** |
| 构建交互式聊天机器人 | **聊天机器人 API** |
| 响应斜杠命令 | **聊天机器人 API** |
| 创建带按钮/表单的消息 | **聊天机器人 API** |
| 处理用户交互 | **聊天机器人 API** |

### 团队聊天 API（用户级）
- 消息显示为由 **认证用户** 发送
- 需要 **用户 OAuth** (authorization_code 流程)
- 端点：`POST https://api.zoom.us/v2/chat/users/me/messages`
- 范围：`chat_message:write`, `chat_channel:read`

### 聊天机器人 API（机器人级）
- 消息显示为由您的 **机器人** 发送
- 需要 **客户端凭证** 授权
- 端点：`POST https://api.zoom.us/v2/im/chat/messages`
- 范围：`imchat:bot` (自动添加)
- **富卡片**：按钮、表单、下拉菜单、图片

## 前提条件

### 系统要求

- Zoom 账户
- 账户所有者、管理员或 **Zoom for developers** 角色已启用
  - 启用方式：**用户管理** → **角色** → **角色设置** → **高级功能** → 启用 **Zoom for developers**

### 创建 Zoom 应用

1. 前往 [Zoom 应用市场](https://marketplace.zoom.us/)
2. 点击 **开发** → **构建应用**
3. 选择 **通用应用** (OAuth)

> ⚠️ **不要使用 Server-to-Server OAuth** - S2S 应用没有聊天机器人/团队聊天功能。只有通用应用 (OAuth) 支持聊天机器人。

### 必要凭证

从 Zoom 市场place → 您的应用：

| 凭证 | 位置 | 使用 |
|------------|----------|---------|
| Client ID | 应用凭证 → 开发 | 两个 API |
| Client Secret | 应用凭证 → 开发 | 两个 API |
| Account ID | 应用凭证 → 开发 | 聊天机器人 API |
| Bot JID | 功能 → 聊天机器人 → 机器人凭证 | 聊天机器人 API |
| Secret Token | 功能 → 团队聊天订阅 | 聊天机器人 API |

**参考**：[环境设置指南](concepts/environment-setup.md) 获取完整的配置步骤。

## 快速入门：团队聊天 API

以用户身份发送消息：

```javascript
// 1. 通过 OAuth 获取访问令牌
const accessToken = await getOAuthToken(); // 参考 examples/oauth-setup.md

// 2. 发送消息到频道
const response = await fetch('https://api.zoom.us/v2/chat/users/me/messages', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: '来自 CI/CD 管道的问候！',
    to_channel: 'CHANNEL_ID'
  })
});

const data = await response.json();
// { "id": "msg_abc123", "date_time": "2024-01-15T10:30:00Z" }
```

**完整示例**：[发送消息指南](examples/send-message.md)

## 快速入门：聊天机器人 API

构建交互式聊天机器人：

```javascript
// 1. 获取聊天机器人令牌 (client_credentials)
async function getChatbotToken() {
  const credentials = Buffer.from(
    `${CLIENT_ID}:${CLIENT_SECRET}`
  ).toString('base64');
  
  const response = await fetch('https://zoom.us/oauth/token', {
    method: 'POST',
    headers: {
      'Authorization': `Basic ${credentials}`,
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: 'grant_type=client_credentials'
  });
  
  return (await response.json()).access_token;
}

// 2. 发送带按钮的聊天机器人消息
const response = await fetch('https://api.zoom.us/v2/im/chat/messages', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    robot_jid: process.env.ZOOM_BOT_JID,
    to_jid: payload.toJid,           // 从 webhook 获取
    account_id: payload.accountId,   // 从 webhook 获取
    content: {
      head: {
        text: '构建通知',
        sub_head: { text: 'CI/CD 管道' }
      },
      body: [
        { type: 'message', text: '部署成功！' },
        {
          type: 'fields',
          items: [
            { key: '分支', value: 'main' },
            { key: '提交', value: 'abc123' }
          ]
        },
        {
          type: 'actions',
          items: [
            { text: '查看日志', value: 'view_logs', style: 'Primary' },
            { text: '关闭', value: 'dismiss', style: 'Default' }
          ]
        }
      ]
    }
  })
});
```

**完整示例**：[聊天机器人设置指南](examples/chatbot-setup.md)

## 关键功能

### 团队聊天 API

| 功能 | 描述 |
|---------|-------------|
| **发送消息** | 发布消息到频道或直接消息 |
| **列出频道** | 获取用户频道及其元数据 |
| **创建频道** | 程序化创建公共/私有频道 |
| **线程回复** | 回复特定消息中的线程 |
| **编辑/删除** | 修改或删除消息 |

### 聊天机器人 API

| 功能 | 描述 |
|---------|-------------|
| **富消息卡片** | 标题、图片、字段、按钮、表单 |
| **斜杠命令** | 自定义 `/commands` 触发 webhook |
| **按钮操作** | 带 webhook 回调的交互式按钮 |
| **表单提交** | 使用表单收集用户输入 |
| **下拉选择** | 频道、成员、日期/时间选择器 |
| **LLM 集成** | 轻松集成 Claude、GPT 等 |

## Webhook 事件（聊天机器人 API）

| 事件 | 触发 | 使用场景 |
|-------|---------|----------|
| `bot_notification` | 用户与机器人交互或使用斜杠命令 | 处理命令、集成 LLM |
| `bot_installed` | 机器人添加到账户 | 初始化机器人状态 |
| `interactive_message_actions` | 按钮被点击 | 处理按钮操作 |
| `chat_message.submit` | 表单提交 | 处理表单数据 |
| `app_deauthorized` | 机器人被移除 | 清理 |

**参考**：[Webhook 事件参考](references/webhook-events.md)

## 消息卡片组件

使用这些组件构建丰富的交互式消息：

| 组件 | 描述 |
|-----------|-------------|
| **header** | 标题和副标题 |
| **message** | 纯文本 |
| **fields** | 键值对 |
| **actions** | 按钮（Primary、Danger、Default 样式） |
| **section** | 带颜色的侧边栏分组 |
| **attachments** | 带链接的图片 |
| **divider** | 水平线 |
| **form_field** | 文本输入 |
| **dropdown** | 选择菜单 |
| **date_picker** | 日期选择 |

**参考**：[消息卡片参考](references/message-cards.md) 获取完整的组件目录

## 架构模式

### 聊天机器人生命周期

```
用户输入 /command → Webhook 接收 bot_notification
                            ↓
                     payload.cmd = "用户的输入"
                            ↓
                     处理命令
                            ↓
                     通过 sendChatbotMessage() 发送响应
```

### LLM 集成模式

```javascript
case 'bot_notification': {
  const { toJid, cmd, accountId } = payload;
  
  // 1. 调用您的 LLM
  const llmResponse = await callClaude(cmd);
  
  // 2. 发送响应回
  await sendChatbotMessage(toJid, accountId, {
    body: [{ type: 'message', text: llmResponse }]
  });
}
```

**参考**：[LLM 集成指南](examples/llm-integration.md)

## 示例应用

| 示例 | 描述 | 链接 |
|--------|-------------|------|
| **Chatbot 快速入门** | 官方教程（推荐开始） | [GitHub](https://github.com/zoom/chatbot-nodejs-quickstart) |
| **Claude 聊天机器人** | 带有 Anthropic Claude 的 AI 聊天机器人 | [GitHub](https://github.com/zoom/zoom-chatbot-claude-sample) |
| **Unsplash 聊天机器人** | 带数据库的图片搜索 | [GitHub](https://github.com/zoom/unsplash-chatbot) |
| **ERP 聊天机器人** | 带有计划警报的 Oracle ERP | [GitHub](https://github.com/zoom/zoom-erp-chatbot-sample) |
| **任务管理器** | 完整的 CRUD 应用 | [GitHub](https://github.com/zoom/task-manager-sample) |

**参考**：[示例应用指南](references/samples.md) 获取所有 10 个示例的分析

## 常见操作

### 向频道发送消息

```javascript
// 团队聊天 API
await fetch('https://api.zoom.us/v2/chat/users/me/messages', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: JSON.stringify({
    message: '你好！',
    to_channel: 'CHANNEL_ID'
  })
});
```

### 处理按钮点击

```javascript
// Webhook 处理程序
case 'interactive_message_actions': {
  const { actionItem, toJid, accountId } = payload;
  
  if (actionItem.value === 'approve') {
    await sendChatbotMessage(toJid, accountId, {
      body: [{ type: 'message', text: '✅ 已批准!' }]
    });
  }
}
```

### 验证 Webhook 签名

```javascript
function verifyWebhook(req) {
  const message = `v0:${req.headers['x-zm-request-timestamp']}:${JSON.stringify(req.body)}`;
  const hash = crypto.createHmac('sha256', process.env.ZOOM_VERIFICATION_TOKEN)
    .update(message)
    .digest('hex');
  return req.headers['x-zm-signature'] === `v0=${hash}`;
}
```

## 部署

### ngrok 用于本地开发

```bash
# 安装 ngrok
npm install -g ngrok

# 暴露本地服务器
ngrok http 4000

# 将 HTTPS URL 作为 Zoom 市场place 中的 Bot 端点 URL
# 示例：https://abc123.ngrok.io/webhook
```

### 生产部署

**参考**：[部署指南](concepts/deployment.md) 获取：
- Nginx 反向代理设置
- 基路径配置
- OAuth 重定向 URI 设置

## 限制

| 限制 | 值 |
|-------|-------|
| 消息长度 | 4,096 个字符 |
| 文件大小 | 512 MB |
| 每个频道的成员数 | 10,000 |
| 每个用户的频道数 | 500 |

## 安全最佳实践

1. **验证 webhook 签名** - 始终使用 `x-zm-signature` 头进行验证
2. **清理消息** - 限制为 4096 个字符，移除控制字符
3. **验证 JIDs** - 检查格式：`user@domain` 或 `channel@domain`
4. **环境变量** - 不要硬编码凭证
5. **使用 HTTPS** - 生产 webhook 所需

**参考**：[安全最佳实践](concepts/security.md)

## 完整文档库

### 核心概念（从这里开始！）
- **[API 选择指南](concepts/api-selection.md)** - 确认使用团队聊天 API 还是 Chatbot API
- **[环境设置](concepts/environment-setup.md)** - 完整凭证指南
- **[认证流程](concepts/authentication.md)** - OAuth 与客户端凭证
- **[Webhook 架构](concepts/webhooks.md)** - webhook 的工作原理
- **[消息卡片结构](concepts/message-structure.md)** - 卡片组件层次结构

### 完整示例
- **[OAuth 设置](examples/oauth-setup.md)** - 完整 OAuth 实现
- **[发送消息](examples/send-message.md)** - 团队聊天 API 消息发送
- **[聊天机器人设置](examples/chatbot-setup.md)** - 带有 webhook 的完整聊天机器人
- **[按钮操作](examples/button-actions.md)** - 处理交互式按钮
- **[表单提交](examples/form-submissions.md)** - 处理表单数据
- **[斜杠命令](examples/slash-commands.md)** - 创建自定义命令
- **[LLM 集成](examples/llm-integration.md)** - Claude/GPT 集成
- **[计划警报](examples/scheduled-alerts.md)** - Cron + incoming webhooks
- **[频道管理](examples/channel-management.md)** - 创建/管理频道

### 参考
- **[API 参考](references/api-reference.md)** - 所有端点和方法
- **[Webhook 事件](references/webhook-events.md)** - 完整事件参考
- **[消息卡片](references/message-cards.md)** - 所有卡片组件
- **[示例应用](references/samples.md)** - 10 个官方示例分析
- **[错误代码](references/error-codes.md)** - 错误处理指南

### 故障排除
- **[OAuth 问题](troubleshooting/oauth-issues.md)** - 认证失败
- **[Webhook 问题](troubleshooting/webhook-issues.md)** - webhook 调试
- **[常见问题](troubleshooting/common-issues.md)** - 快速诊断

## 资源

- **官方文档**：[https://developers.zoom.us/docs/team-chat/](https://developers.zoom.us/docs/team-chat/)
- **API 参考**：[https://developers.zoom.us/docs/api/rest/reference/chatbot/](https://developers.zoom.us/docs/api/rest/reference/chatbot/)
- **开发者论坛**：[https://devforum.zoom.us/](https://devforum.zoom.us/)
- **应用市场**：[https://marketplace.zoom.us/](https://marketplace.zoom.us/)

---

**需要帮助？** 从下方集成索引部分开始，获取完整导航。

---

## 集成索引

本节从 `SKILL.md` 迁移而来。

Zoom 团队聊天技能的完整导航指南。

## 快速入门路径

- 从这里开始：[入门](get-started.md)
- 首先进行快速故障排除：[5 分钟运行手册](RUNBOOK.md)

### 路径 1：团队聊天 API（用户级消息）

用于以用户账户身份发送消息。

1. [API 选择指南](concepts/api-selection.md) - 确认使用团队聊天 API
2. [环境设置](concepts/environment-setup.md) - 获取凭证
3. [OAuth 设置示例](examples/oauth-setup.md) - 实现认证
4. [发送消息示例](examples/send-message.md) - 发送第一条消息

### 路径 2：聊天机器人 API（交互式机器人）

用于构建带富消息的交互式聊天机器人。

1. [API 选择指南](concepts/api-selection.md) - 确认使用 Chatbot API
2. [环境设置](concepts/environment-setup.md) - 获取凭证（包括 Bot JID）
3. [Webhook 架构](concepts/webhooks.md) - 理解 webhook 事件
4. [聊天机器人设置示例](examples/chatbot-setup.md) - 构建您的第一个机器人
5. [消息卡片参考](references/message-cards.md) - 创建富消息

## 核心概念

两个 API 的基本理解。

| 文档 | 描述 |
|------|------|
| [API 选择指南](concepts/api-selection.md) | 选择团队聊天 API 还是聊天机器人 API |
| [环境设置](concepts/environment-setup.md) | 完成凭证和应用配置 |
| [认证流程](concepts/authentication.md) | OAuth 与客户端凭证 |
| [Webhook 架构](concepts/webhooks.md) | Webhook 的工作原理（聊天机器人 API） |
| [消息卡片结构](concepts/message-structure.md) | 卡片组件层级 |
| [部署指南](concepts/deployment.md) | 生产部署策略 |
| [安全最佳实践](concepts/security.md) | 保护您的集成 |

## 完整示例

常见场景的代码示例。

### 认证
| 示例 | 描述 |
|------|------|
| [OAuth 设置](examples/oauth-setup.md) | 用户 OAuth 流实现 |
| [令牌管理](examples/token-management.md) | 刷新令牌、过期处理 |

### 基本操作
| 示例 | 描述 |
|------|------|
| [发送消息](examples/send-message.md) | 团队聊天 API 消息发送 |
| [聊天机器人设置](examples/chatbot-setup.md) | 完整带 Webhook 的聊天机器人 |
| [列出频道](examples/channel-management.md) | 获取用户频道 |
| [创建频道](examples/channel-management.md) | 创建公共/私有频道 |

### 交互功能（聊天机器人 API）
| 示例 | 描述 |
|------|------|
| [按钮操作](examples/button-actions.md) | 处理按钮点击 |
| [表单提交](examples/form-submissions.md) | 处理表单数据 |
| [斜杠命令](examples/slash-commands.md) | 创建自定义命令 |
| [下拉选择](examples/dropdown-selects.md) | 频道/成员选择器 |

### 高级集成
| 示例 | 描述 |
|------|------|
| [LLM 集成](examples/llm-integration.md) | 集成 Claude/GPT |
| [计划警报](examples/scheduled-alerts.md) | Cron + 入站 Webhook |
| [数据库集成](examples/database-integration.md) | 存储会话状态 |
| [多步工作流](examples/multi-step-workflows.md) | 复杂用户交互 |

## 参考

### API 文档
| 参考 | 描述 |
|------|------|
| [API 参考](references/api-reference.md) | 指针和常见端点 |
| [Webhook 事件](references/webhook-events.md) | 事件类型和处理清单 |
| [消息卡片](references/message-cards.md) | 所有卡片组件 |
| [错误代码](references/error-codes.md) | 错误处理指南 |

### 示例应用
| 参考 | 描述 |
|------|------|
| [示例应用](references/samples.md) | 示例应用索引/笔记 |

### 字段指南
| 参考 | 描述 |
|------|------|
| [JID 格式](references/jid-formats.md) | 理解 JID 标识符 |
| [范围参考](references/scopes.md) | 常见范围 |
| [速率限制](references/rate-limits.md) | 节流指导 |

## 故障排除

| 指南 | 描述 |
|------|------|
| [常见问题](troubleshooting/common-issues.md) | 快速诊断和解决方案 |
| [OAuth 问题](troubleshooting/oauth-issues.md) | 认证失败 |
| [Webhook 问题](troubleshooting/webhook-issues.md) | Webhook 调试 |
| [消息问题](troubleshooting/message-issues.md) | 消息发送问题 |
| [部署问题](troubleshooting/deployment-issues.md) | 生产问题 |

## 架构模式

### 聊天机器人生命周期

```
用户操作 → Webhook → 处理 → 响应
```

### LLM 集成模式

```
用户输入 → 聊天机器人接收 → 调用 LLM → 发送响应
```

### 审批工作流模式

```
请求 → 发送带按钮的卡片 → 用户点击 → 更新状态 → 通知
```

## 常见用例

### 通知
- CI/CD 构建通知
- 服务器监控警报
- 计划报告
- 系统健康检查

### 工作流
- 审批请求
- 任务分配
- 状态更新
- 表单提交

### 集成
- LLM 驱动的助手
- 数据库查询
- 外部 API 集成
- 文件/图片共享

### 自动化
- 计划消息
- 自动回复
- 数据收集
- 报告生成

## 资源链接

### 官方文档
- **[团队聊天文档](https://developers.zoom.us/docs/team-chat/)** - 官方概述
- **[聊天机器人文档](https://developers.zoom.us/docs/team-chat/chatbot/extend/)** - 聊天机器人指南
- **[API 参考](https://developers.zoom.us/docs/api/rest/reference/chatbot/)** - REST API 文档
- **[应用市场](https://marketplace.zoom.us/)** - 创建和管理应用

### 示例代码
- **[聊天机器人快速入门](https://github.com/zoom/chatbot-nodejs-quickstart)** - 官方教程
- **[Claude 聊天机器人](https://github.com/zoom/zoom-chatbot-claude-sample)** - AI 集成
- **[Unsplash 聊天机器人](https://github.com/zoom/unsplash-chatbot)** - 图片搜索机器人
- **[ERP 聊天机器人](https://github.com/zoom/zoom-erp-chatbot-sample)** - 企业集成
- **[任务管理器](https://github.com/zoom/task-manager-sample)** - 完整 CRUD 应用

### 工具
- **[应用卡片构建器](https://appssdk.zoom.us/cardbuilder/)** - 可视化卡片设计器
- **[ngrok](https://ngrok.com/)** - 本地 Webhook 测试
- **[Postman](https://www.postman.com/)** - API 测试

### 社区
- **[开发者论坛](https://devforum.zoom.us/)** - 提问
- **[GitHub 讨论区](https://github.com/zoom)** - 社区支持
- **[开发者支持](https://devsupport.zoom.us)** - 官方支持

## 文档状态

### ✅ 完成
- 主 skill.md 入口
- API 选择指南
- 环境设置
- Webhook 架构
- 聊天机器人设置示例（完整可运行代码）
- 消息卡片参考
- 常见问题故障排除

### 📝 待办（高优先级）
- OAuth 设置示例
- 发送消息示例
- 按钮操作示例
- LLM 集成示例
- Webhook 事件参考
- API 参考
- 示例应用分析

### 📋 计划（低优先级）
- 表单提交示例
- 频道管理示例
- 数据库集成示例
- 错误代码参考
- 速率限制指南
- 部署故障排除

## 入门检查清单

### 对于团队聊天 API

- [ ] 阅读 [API 选择指南](concepts/api-selection.md)
- [ ] 完成 [环境设置](concepts/environment-setup.md)
- [ ] 获取 Client ID, Client Secret
- [ ] 添加所需范围
- [ ] 实现OAuth 流
- [ ] 发送第一条消息

### 对于聊天机器人 API

- [ ] 阅读 [API 选择指南](concepts/api-selection.md)
- [ ] 完成 [环境设置](concepts/environment-setup.md)
- [ ] 获取 Client ID, Client Secret, Bot JID, Secret Token, Account ID
- [ ] 在功能中启用团队聊天
- [ ] 配置 Bot 端点 URL 和斜杠命令
- [ ] 设置 ngrok 用于本地测试
- [ ] 实现webhook 处理器
- [ ] 发送第一条聊天机器人消息

## 版本历史

- **v1.0** (2026-02-09) - 初始全面文档
  - 核心概念（API 选择、环境设置、Webhooks）
  - 完整聊天机器人设置示例
  - 消息卡片参考
  - 常见问题故障排除

## 支持

将此 SKILL.md 作为团队聊天 API 选择、设置、示例和故障排除的导航中心。

## 环境变量

- 参考 [references/environment-variables.md](references/environment-variables.md) 获取标准化的 `.env` 键和每个值的来源。
