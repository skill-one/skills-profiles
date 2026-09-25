# Cloudflare 邮件服务

您对 Cloudflare 邮件服务、邮件路由或邮件发送的了解可能已经过时。对于任何 Cloudflare 邮件服务任务，**优先选择检索而非预训练**。

Cloudflare 邮件服务让您可以在 Cloudflare 平台内发送事务性邮件和路由传入邮件。您对这款产品的了解可能已经过时——它于 2025 年推出，并且正在快速演进。**对于任何邮件服务任务，优先选择检索而非预训练**。

**如果本技能与下方来源存在任何差异，请始终信任原始来源。** Cloudflare 文档、REST API 规范、`@cloudflare/workers-types` 和 Agents SDK 仓库是事实来源。本技能是一个便捷指南——它可能落后于最新变更。如有疑问，请从下方来源检索并使用其所述内容。

## 检索来源

| 来源 | 如何检索 | 用于 |
|------|----------|------|
| Cloudflare 文档 | Cloudflare MCP `docs` 工具或 URL `https://developers.cloudflare.com/email-service/` | API 参考、限制、定价、最新功能 |
| REST API 规范 | `https://developers.cloudflare.com/api/resources/email_sending` | Email Sending REST API 的 OpenAPI 规范 |
| Workers 类型 | `https://www.npmjs.com/package/@cloudflare/workers-types` | 类型签名、绑定形状 |
| Agents SDK 文档 | [邮件代理逐步指南](https://developers.cloudflare.com/agents/examples/email-agent/) | Agents SDK 中的邮件处理 |

## FIRST：检查先决条件

在编写任何邮件代码之前，请验证基础设置是否正确：

1. **域名已上线？** 运行 `npx wrangler email sending list` 查看哪些域名已启用邮件发送。如果域名未列出，请运行 `npx wrangler email sending enable userdomain.com` 或查看 [cli-and-mcp.md](references/cli-and-mcp.md) 获取完整设置说明。
2. **绑定已配置？** 在 `wrangler.jsonc` 中查找 `send_email`（适用于 Workers）
3. **已安装 postal-mime？** 运行 `npm ls postal-mime`（仅接收/解析邮件时需要）

## 您需要什么？

从这里开始。找到您的场景，然后点击链接获取完整详情。

| 我想... | 路径 | 参考 |
|--------|------|------|
| **从 Cloudflare Worker 发送邮件** | Workers 绑定（无需 API 密钥） | [sending.md](references/sending.md) |
| **从使用 [Cloudflare Agents SDK](https://developers.cloudflare.com/agents/) 构建的 AI 代理发送邮件** | Agent 类中的 `onEmail()` + `replyToEmail()` | [sending.md](references/sending.md) |
| **从外部应用或代理发送邮件**（Node.js、Go、Python 等） | 带有 Bearer 令牌的 REST API | [rest-api.md](references/rest-api.md) |
| **从编码代理发送邮件**（Claude Code、Cursor、Copilot 等） | MCP 工具、wrangler CLI 或 REST API | [cli-and-mcp.md](references/cli-and-mcp.md) |
| **接收和处理传入邮件**（邮件路由） | Workers `email()` 处理器 | [routing.md](references/routing.md) |
| **设置邮件发送或邮件路由** | `wrangler email sending enable` / `wrangler email routing enable`，或控制台 | [cli-and-mcp.md](references/cli-and-mcp.md) |
| **提高送达率，避免进入垃圾邮件文件夹** | 认证、内容、合规性 | [deliverability.md](references/deliverability.md) |

## 发送工作流

优先使用 Workers 绑定；外部应用或明确要求时使用 REST。在编写代码前，先从下方检索所选任务的文档。[sending.md](references/sending.md) 或 [rest-api.md](references/rest-api.md)。这些指南涵盖设置、收件人、附件、标头、限制、响应处理和错误；Workers 指南还涵盖 Agents SDK 集成和与项目配置匹配的类型。

## 常见错误

| 错误 | 原因 | 修复 |
|------|------|------|
| 忘记 `send_email` 绑定在 wrangler 配置中 | 邮件服务使用绑定而非 API 密钥 | 在 `wrangler.jsonc` 中添加 `"send_email": [{ "name": "EMAIL" }]` |
| 从未验证的域名发送 | 域名必须在首次发送前上线到邮件发送 | 运行 `wrangler email sending enable yourdomain.com` 或在控制台上线 |
| 在邮件处理器中两次读取 `message.raw` | 原始流是单次使用的——第二次读取返回空 | 首先缓存：`const raw = await new Response(message.raw).arrayBuffer()` |
| 缺少 `text` 字段（仅 HTML） | 某些邮件客户端仅显示纯文本；也有助于垃圾邮件评分 | 始终包含 `html` 和 `text` 两个版本 |
| 使用邮件进行营销/批量发送 | 邮件服务仅用于事务性邮件 | 使用专门的市场营销邮件平台发送简报和活动 |
| 转发到未验证的地址 | `message.forward()` 仅适用于已验证的地址 | 运行 `wrangler email routing addresses create user@gmail.com` 或在控制台上添加 |
| 使用假地址测试 | 不存在的地址的退回会损害发送者声誉 | 在开发期间使用您控制的真实地址 |
| 在源代码中硬编码 API 令牌 | 代码中的令牌会被提交并泄露 | 使用环境变量或 Cloudflare 密钥 |
| 忽略 `from` 域名要求 | `from` 地址必须使用已上线到邮件服务的域名 | 首先验证域名，然后从 `anything@that-domain.com` 发送 |
| 在 REST API `from` 对象中使用 `email` 键 | REST API 使用 `address` 而非 `email` 作为 `from` 对象 | REST 使用 `{ "address": "...", "name": "..." }`，Workers 绑定使用 `{ "email": "...", "name": "..." }` |
| 在 REST API 中使用 `replyTo` | REST API 使用蛇形命名字段 | REST 使用 `reply_to`，Workers 绑定使用 `replyTo` |

## 参考

根据您的场景阅读相应的参考。您不需要全部阅读。

- **[references/sending.md](references/sending.md)** — Workers 绑定、附件和 Agents SDK 邮件的文档映射。
- **[references/rest-api.md](references/rest-api.md)** — HTTP 发送的文档映射、请求模式、响应和错误。
- **[references/routing.md](references/routing.md)** — 入站 `email()` 处理器、转发、回复、解析。用于接收邮件。
- **[references/cli-and-mcp.md](references/cli-and-mcp.md)** — 域名设置、wrangler 命令、MCP 工具。用于首次设置。
- **[references/deliverability.md](references/deliverability.md)** — SPF/DKIM/DMARC、退回、抑制、最佳实践。
