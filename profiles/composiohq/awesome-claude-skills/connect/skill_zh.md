# 连接

将 Claude 连接到任何应用程序。停止生成关于你能做什么的文本——实际上去做。

## 何时使用此技能

当你需要 Claude 执行以下操作时，请使用此技能：

- **发送那封邮件** 而不是起草它
- **创建那个问题** 而不是描述它
- **发布那条消息** 而不是建议它
- **更新那个数据库** 而不是解释如何操作

## 变化

| 无连接 | 带连接 |
|--------|--------|
| "这是一封邮件草稿..." | 发送邮件 |
| "你应该创建一个问题..." | 创建问题 |
| "将此内容发布到 Slack..." | 发布内容 |
| "将此内容添加到 Notion..." | 添加内容 |

## 支持的应用

**1000+ 集成应用**，包括：

- **邮件:** Gmail, Outlook, SendGrid
- **聊天:** Slack, Discord, Teams, Telegram
- **开发:** GitHub, GitLab, Jira, Linear
- **文档:** Notion, Google Docs, Confluence
- **数据:** Sheets, Airtable, PostgreSQL
- **CRM:** HubSpot, Salesforce, Pipedrive
- **存储:** Drive, Dropbox, S3
- **社交:** Twitter, LinkedIn, Reddit

## 设置

### 1. 获取 API 密钥

在 [platform.composio.dev](https://platform.composio.dev/?utm_source=Github&utm_content=AwesomeSkills) 获取你的免费密钥

### 2. 设置环境变量

```bash
export COMPOSIO_API_KEY="your-key"
```

### 3. 安装

```bash
pip install composio          # Python
npm install @composio/core    # TypeScript
```

完成。现在 Claude 可以连接到任何应用程序。

## 示例

### 发送邮件
```
Email sarah@acme.com - Subject: "已发货!" Body: "v2.0 已上线，如有问题请告知"
```

### 创建 GitHub 问题
```
在 my-org/repo 中创建问题: "移动端超时问题" 标签:bug
```

### 发布到 Slack
```
发布到 #engineering: "部署完成 - v2.4.0 已上线"
```

### 链式操作
```
查找本周标记为 "bug" 的 GitHub 问题，总结，发布到 #bugs on Slack
```

## 工作原理

使用 Composio 工具路由器：

1. **你让 Claude 做某事**
2. **工具路由器找到** 正确的工具（1000+ 选项）
3. **OAuth 自动处理**
4. **执行操作并返回结果**

### 代码

```python
from composio import Composio
from claude_agent_sdk.client import ClaudeSDKClient
from claude_agent_sdk.types import ClaudeAgentOptions
import os

composio = Composio(api_key=os.environ["COMPOSIO_API_KEY"])
session = composio.create(user_id="user_123")

options = ClaudeAgentOptions(
    system_prompt="你可以在外部应用程序中执行操作。",
    mcp_servers={
        "composio": {
            "type": "http",
            "url": session.mcp.url,
            "headers": {"x-api-key": os.environ["COMPOSIO_API_KEY"]},
        }
    },
)

async with ClaudeSDKClient(options) as client:
    await client.query("发送 Slack 消息到 #general: Hello!")
```

## 认证流程

首次使用应用程序时：
```
为了发送邮件，我需要访问 Gmail。
在此处授权：https://...
完成后说 "connected"。
```

连接后可持久保存。

## 支持的框架

| 框架 | 安装 |
|------|------|
| Claude Agent SDK | `pip install composio claude-agent-sdk` |
| OpenAI Agents | `pip install composio openai-agents` |
| Vercel AI | `npm install @composio/core @composio/vercel` |
| LangChain | `pip install composio-langchain` |
| 任何 MCP 客户端 | 使用 `session.mcp.url` |

## 故障排除

- **需要认证** → 点击链接，授权，说 "connected"
- **操作失败** → 检查目标应用程序的权限
- **找不到工具** → 请具体说明："Slack #general" 而不是 "发送消息"

---

<p align="center">
  <b>加入 20,000+ 开发者，构建可上线的智能代理</b>
</p>

<p align="center">
  <a href="https://platform.composio.dev/?utm_source=Github&utm_content=AwesomeSkills">
    <img src="https://img.shields.io/badge/开始免费-4F46E5?style=for-the-badge" alt="开始使用"/>
  </a>
</p>
