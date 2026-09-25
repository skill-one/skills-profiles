# 连接应用

将 Claude 连接到 1000 多个应用。真正发送邮件、创建问题、发布消息——而不仅仅是生成关于它们的文本。

## 快速入门

### 第 1 步：安装插件

```
/plugin install composio-toolrouter
```

### 第 2 步：运行设置

```
/composio-toolrouter:setup
```

这将：
- 请求您的免费 API 密钥（在 [platform.composio.dev](https://platform.composio.dev/?utm_source=Github&utm_content=AwesomeSkills) 获取）
- 配置 Claude 与 1000 多个应用的连接
- 大约需要 60 秒

### 第 3 步：试试看！

设置完成后，重启 Claude Code 并尝试：

```
向我发送一封测试邮件到 YOUR_EMAIL@example.com
```

如果成功，您就连接成功了！

## 您能做什么

| 请 Claude 执行... | 会发生什么 |
|------------------|--------------|
| "向 sarah@acme.com 发送关于发布的邮件" | 真正发送邮件 |
| "创建 GitHub 问题：修复登录错误" | 创建问题 |
| "在 Slack #general 发布：部署完成" | 发布消息 |
| "将会议笔记添加到 Notion" | 添加到 Notion |

## 支持的应用

**邮件：** Gmail、Outlook、SendGrid
**聊天：** Slack、Discord、Teams、Telegram
**开发：** GitHub、GitLab、Jira、Linear
**文档：** Notion、Google Docs、Confluence
**数据：** Sheets、Airtable、PostgreSQL
**以及 1000 多个其他应用...**

## 工作原理

1. 您请求 Claude 做某事
2. Composio Tool Router 找到正确的工具
3. 首次使用？您将通过 OAuth 授权（一次性）
4. 执行操作并返回结果

## 故障排除

- **"插件未找到"** → 确保您运行了 `/plugin install composio-toolrouter`
- **"需要授权"** → 点击 Claude 提供的 OAuth 链接，然后说 "done"
- **操作失败** → 检查您在目标应用中是否有权限

---

<p align="center">
  <b>加入 20,000+ 开发者，构建可部署的智能体</b>
</p>

<p align="center">
  <a href="https://platform.composio.dev/?utm_source=Github&utm_content=AwesomeSkills">
    <img src="https://img.shields.io/badge/开始免费-4F46E5?style=for-the-badge" alt="开始使用"/>
  </a>
</p>
