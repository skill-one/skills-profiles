# /build-zoom-team-chat-app

Zoom 团队聊天集成的背景参考。在流程清晰后使用此文档，尤其是在团队聊天 API 与聊天机器人 API 区分很重要时。

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

如果早期选择了错误的类型，认证/范围/端点都会不匹配，实现会失败。

**官方文档**：https://developers.zoom.us/docs/team-chat/  
**聊天机器人文档**：https://developers.zoom.us/docs/team-chat/chatbot/extend/  
**API 参考**：https://developers.zoom.us/docs/api/rest/reference/chatbot/

## 快速链接

**新接触团队聊天？请遵循此路径：**

1. **[入门](get-started.md)** - 端到端快速路径（用户类型与机器人类型）
2. **[选择您的 API](concepts/api-selection.md)** - 团队聊天 API 与聊天机器人 API
3. **[环境设置](concepts/environment-setup.md)** - 凭证、范围、应用程序配置
4. **[OAuth 设置](examples/oauth-setup.md)** - 完整的认证流程
5. **[发送第一条消息](examples/send-message.md)** - 用于发送消息的工作代码

**参考：**
- **[聊天机器人消息卡片](references/message-cards.md)** - 完整的卡片组件参考
- **[Webhook 事件](references/webhook-events.md)** - 所有 webhook 事件类型
- **[API 参考](references/api-reference.md)** - 端点、方法、参数
- **[示例应用程序](references/samples.md)** - 10+ 官方示例应用程序
- **集成索引** - 查看此文件中的下一段内容

**遇到问题？**
- 认证错误 → [OAuth 问题排查](troubleshooting/oauth-issues.md)
- Webhook 未接收事件 → [Webhook 设置指南](troubleshooting/webhook-issues.md)
- 消息未发送 → [常见问题](troubleshooting/common-issues.md)
- 从快速检查开始 → [5 分钟运行手册](RUNBOOK.md)

**OAuth 端点合理性检查：**
- 授权 URL：`https://zoom.us/oauth/authorize`
- 令牌 URL：`https://zoom.us/oauth/token`
- 如果 `/oauth/token` 返回 404/HTML，请使用 `https://zoom.us/oauth/token`。

**构建交互式机器人？**
- [按钮操作](examples/button-actions.md) - 处理按钮点击
- [表单提交](examples/form-submissions.md) - 处理表单数据
- [斜杠命令](examples/slash-commands.md) - 创建自定义命令

## 快速决策：使用哪个 API？

| 使用场景 | 使用 API |
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
- 需要 **客户端凭证** 授予
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

> ⚠️ **不要使用服务器到服务器 OAuth** - S2S 应用没有聊天机器人/团队聊天功能。只有通用应用 (OAuth) 支持聊天机器人。

### 必需的凭证

从 Zoom 市场台 → 您的应用：

| 凭证 | 位置 | 使用 |
|------------|----------|---------|
| 客户端 ID | 应用凭证 → 开发 | 两个 API |
| 客户端密钥 | 应用凭证 → 开发 | 两个 API |
| 账户 ID | 应用凭证 → 开发 | 聊天机器人 API |
| 机器人 JID | 功能 → 聊天机器人 → 机器人凭证 | 聊天机器人 API |
| 密钥令牌 | 功能 → 团队聊天订阅 | 聊天机器人 API |

**参考**：[环境设置指南](concepts/environment-setup.md) 完整配置步骤。

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
            { text: '忽略', value: 'dismiss', style: 'Default' }
          ]
        }
      ]
    }
  })
);
```

**完整示例**：[聊天机器人设置指南](examples/chatbot-setup.md)

## 关键功能

### 团队聊天 API

| 功能 | 描述 |
|---------|-------------|
| **发送消息** | 发送消息到频道或直接消息 |
| **列出频道** | 获取用户的频道及其元数据 |
| **创建频道** | 程序化创建公共/私有频道 |
| **线程回复** | 在特定消息的线程中回复 |
| **编辑/删除** | 修改或删除消息 |

### 聊天机器人 API

| 功能 | 描述 |
|---------|-------------|
| **富消息卡片** | 标题、图片、字段、按钮、表单 |
| **斜杠命令** | 自定义 `/commands` 触发 webhook |
| **按钮操作** | 带 webhook 回调的交互式按钮 |
| **表单提交** | 使用表单收集用户输入 |
| **下拉选择** | 频道、成员、日期/时间选择器 |
| **LLM 集成** | 易于与 Claude、GPT 等集成 |

## Webhook 事件（聊天机器人 API）

| 事件 | 触发 | 使用场景 |
|-------|---------|----------|
| `bot_notification` | 用户向机器人发送消息或使用斜杠命令 | 处理命令，集成 LLM |
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
| **actions** | 按钮（主要、危险、默认样式） |
| **section** | 带颜色的侧边栏分组 |
| **attachments** | 带链接的图片 |
| **divider** | 水平线 |
| **form_field** | 文本输入 |
| **dropdown** | 选择菜单 |
| **date_picker** | 日期选择 |

**参考**：[消息卡片参考](references/message-cards.md) 完整组件目录

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
- 定时报告
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
- 定时消息
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
- **[ngrok](https://ngrok.com/)** - 本地 webhook 测试
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
- 聊天机器人设置示例（完整可工作代码）
- 消息卡片参考
- 常见问题排查

### 📝 待更新（高优先级）
- OAuth 设置示例
- 发送消息示例
- 按钮操作示例
- LLM 集成示例
- Webhook 事件参考
- API 参考
- 示例应用程序分析

### 📋 计划（低优先级）
- 表单提交示例
- 频道管理示例
- 数据库集成示例
- 错误代码参考
- 速率限制指南
- 部署问题排查

## 入门检查清单

### 对于团队聊天 API

- [ ] 阅读 [API 选择指南](concepts/api-selection.md)
- [ ] 完成 [环境设置](concepts/environment-setup.md)
- [ ] 获取客户端 ID、客户端密钥
- [ ] 添加所需范围
- [ ] 实现OAuth流程
- [ ] 发送第一条消息

### 对于聊天机器人 API

- [ ] 阅读 [API 选择指南](concepts/api-selection.md)
- [ ] 完成 [环境设置](concepts/environment-setup.md)
- [ ] 获取客户端 ID、客户端密钥、机器人 JID、密钥令牌、账户 ID
- [ ] 在功能中启用团队聊天
- [ ] 配置机器人端点 URL 和斜杠命令
- [ ] 设置 ngrok 进行本地测试
- [ ] 实现webhook 处理程序
- [ ] 发送第一条聊天机器人消息

## 版本历史

- **v1.0** (2026-02-09) - 初步全面文档
  - 核心概念（API 选择、环境设置、webhooks）
  - 完整聊天机器人设置示例
  - 消息卡片参考
  - 常见问题排查

## 支持

将此 SKILL.md 作为团队聊天 API 选择、设置、示例和问题排查的导航中心。

## 环境变量

- 参考 [references/environment-variables.md](references/environment-variables.md) 获取标准化的 `.env` 键以及每个值的位置。
