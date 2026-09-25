# Cloudflare Email Service

您对 Cloudflare Email Service、Email Routing 或 Email Sending 的知识可能已过时。**对于任何 Cloudflare Email Service 任务，请优先采用检索而非预训练。**

Cloudflare Email Service 允许您在全 Cloudflare 平台内发送事务性邮件并路由收件邮件。您对该产品的知识可能已过时——它于 2025 年推出，并正在快速演进。**对于任何 Email Service 任务，请优先采用检索而非预训练。**

**若本技能与下方来源存在任何差异，始终以原始来源为准。** Cloudflare 文档、REST API 规范、`@cloudflare/workers-types` 以及 Agents SDK 仓库是权威来源。本技能仅为便捷指南——可能滞后于最新变更。如有疑问，请从下方来源检索并使用其内容。

## 检索来源

| 来源 | 如何检索 | 用途 |
|--------|----------------|---------|
| Cloudflare 文档 | Cloudflare MCP `docs` 工具或网址 `https://developers.cloudflare.com/email-service/` | API 参考、限制、定价、最新功能 |
| REST API 规范 | `https://developers.cloudflare.com/api/resources/email_sending` | Email Sending REST API 的 OpenAPI 规范 |
| Workers types | `https://www.npmjs.com/package/@cloudflare/workers-types` | 类型签名、绑定形状 |
| Agents SDK 文档 | [Email agent 指南](https://developers.cloudflare.com/agents/examples/email-agent/) | Agents SDK 中的邮件处理 |

## 第一步：检查前置条件

在编写任何邮件代码之前，请确认基础条件已就绪：

1. **域名是否已接入？** 运行 `npx wrangler email sending list` 查看哪些域名已启用邮件发送。若域名未列出，请运行 `npx wrangler email sending enable userdomain.com`，或参阅 [cli-and-mcp.md](references/cli-and-mcp.md) 获取完整设置说明。
2. **绑定是否已配置？** 在 `wrangler.jsonc`（针对 Workers）中查找 `send_email`
3. **postal-mime 是否已安装？** 运行 `npm ls postal-mime`（仅用于接收/解析邮件时需要）

## 您需要什么？

从此处开始。找到您的情况，然后点击链接获取详细内容。

| 我想要…… | 路径 | 参考 |
|--------------|------|-----------|
| **从 Cloudflare Worker 发送邮件** | Workers 绑定（无需 API 密钥） | [sending.md](references/sending.md) |
| **从基于 [Cloudflare Agents SDK](https://developers.cloudflare.com/agents/) 构建的 AI 智能体发送邮件** | Agent 类中的 `onEmail()` + `replyToEmail()` | [sending.md](references/sending.md) |
| **从外部应用或智能体发送邮件**（Node.js、Go、Python 等） | 使用 Bearer token 的 REST API | [rest-api.md](references/rest-api.md) |
| **从编码智能体发送邮件**（Claude Code、Cursor、Copilot 等） | MCP 工具、wrangler CLI 或 REST API | [cli-and-mcp.md](references/cli-and-mcp.md) |
| **接收并处理收件邮件**（Email Routing） | Workers 的 `email()` 处理器 | [routing.md](references/routing.md) |
| **设置 Email Sending 或 Email Routing** | `wrangler email sending enable` / `wrangler email routing enable`，或仪表盘 | [cli-and-mcp.md](references/cli-and-mcp.md) |
| **提升送达率、避免进入垃圾文件夹** | 认证、内容、合规性 | [deliverability.md](references/deliverability.md) |

## 发送工作流程

优先使用 Workers 绑定；对外部应用或在明确要求时使用 REST。在编写代码前，请阅读 [sending.md](references/sending.md) 或 [rest-api.md](references/rest-api.md) 以检索所选任务的文档。这些指南涵盖设置、收件人、附件、头部、限制、响应处理及错误；Workers 指南还涵盖 Agents SDK 集成以及与项目配置匹配的类型。

## 常见错误

| 错误 | 原因 | 修复方法 |
|---------|---------------|-------------|
| 在 wrangler 配置中遗漏 `send_email` 绑定 | Email Service 使用绑定而非 API 密钥 | 在 wrangler.jsonc 中添加 `"send_email": [{ "name": "EMAIL" }]` |
| 从未验证的域名发送 | 首次发送前必须将域名接入 Email Sending | 运行 `wrangler email sending enable yourdomain.com` 或在仪表盘进行接入 |
| 在邮件处理器中两次读取 `message.raw` | raw 流仅可使用一次——第二次读取返回空内容 | 先进行缓冲：`const raw = await new Response(message.raw).arrayBuffer()` |
| 遗漏 `text` 字段（仅 HTML 时） | 某些邮件客户端仅显示纯文本；也有助于提升垃圾评分 | 始终同时包含 `html` 和 `text` 版本 |
| 使用邮件发送营销/批量邮件 | Email Service 仅用于事务性邮件 | 请为新闻通讯和活动使用专门的营销邮件平台 |
| 转发至未验证的接收方 | `message.forward()` 仅适用于已验证的地址 | 运行 `wrangler email routing addresses create user@gmail.com` 或在仪表盘添加 |
| 使用假地址测试 | 来自不存在的地址的退信会损害发件方声誉 | 开发期间使用您可控的真实地址 |
| 在源代码中硬编码 API token | 代码中的 token 会被提交并泄露 | 使用环境变量或 Cloudflare 密钥 |
| 忽略 `from` 域名要求 | `from` 地址必须使用已接入 Email Service 的域名 | 先验证域名，然后从 `anything@that-domain.com` 发送 |
| 在 REST API 的 `from` 对象中使用 `email` 键 | REST API 在 `from` 对象中使用的是 `address` 而非 `email` | REST 使用 `{ "address": "...", "name": "..." }`，Workers 使用 `{ "email": "...", "name": "..." }` |
| 在 REST API 中使用 `replyTo` | REST API 使用 snake_case 字段名 | REST API 使用 `reply_to`，Workers 绑定使用 `replyTo` |

## 参考

阅读与您情况匹配的参考文档。无需阅读全部。

- **[references/sending.md](references/sending.md)** — Workers 绑定、附件及 Agents SDK 邮件的文档映射。
- **[references/rest-api.md](references/rest-api.md)** — HTTP 发送、请求模式、响应及错误的文档映射。
- **[references/routing.md](references/routing.md)** — 入站 `email()` 处理器、转发、回复、解析。用于接收邮件。
- **[references/cli-and-mcp.md](references/cli-and-mcp.md)** — 域名设置、wrangler 命令、MCP 工具。用于首次设置。
- **[references/deliverability.md](references/deliverability.md)** — SPF/DKIM/DMARC、退信、抑制、最佳实践。
