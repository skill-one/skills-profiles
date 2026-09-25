# 重新发送

## 快速发送 — Node.js

```typescript
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);

const { data, error } = await resend.emails.send(
  {
    from: 'Acme <onboarding@resend.dev>',
    to: ['delivered@resend.dev'],
    subject: 'Hello World',
    html: '<p>Email body here</p>',
  },
  { idempotencyKey: `welcome-email/${userId}` }
);

if (error) {
  console.error('Failed:', error.message);
  return;
}
console.log('Sent:', data.id);
```

**关键点提示**：Resend Node.js SDK 不会抛出异常 — 它会返回 `{ data, error }`。始终显式检查 `error` 而不是使用 try/catch 处理 API 错误。

## 快速发送 — Python

```python
import resend
import os

resend.api_key = os.environ["RESEND_API_KEY"]

email = resend.Emails.send({
    "from": "Acme <onboarding@resend.dev>",
    "to": ["delivered@resend.dev"],
    "subject": "Hello World",
    "html": "<p>Email body here</p>",
}, idempotency_key=f"welcome-email/{user_id}")
```

### 单发与批量发送决策

| 选择 | 条件 |
|------|------|
| **单发** (`POST /emails`) | 1 封邮件，需要附件，需要调度 |
| **批量** (`POST /emails/batch`) | 2-100 封独立邮件，不需要附件，不需要调度 |

批量操作是原子性的 — 如果其中一封邮件验证失败，整个批量都会失败。发送前务必进行验证。批量发送不支持附件或 `scheduled_at`。

### 不可重复性密钥（重试的关键）

防止重试失败请求时发送重复邮件：

| 关键事实 | |
|-----------|---|
| **格式（单发）** | `<事件类型>/<实体ID>`（例如，`welcome-email/user-123`） |
| **格式（批量）** | `batch-<事件类型>/<批量ID>`（例如，`batch-orders/batch-456`） |
| **过期时间** | 24 小时 |
| **最大长度** | 256 个字符 |
| **相同密钥 + 相同负载** | 返回原始响应，无需重新发送 |
| **相同密钥 + 不同负载** | 返回 409 错误 |

## 快速接收（Node.js）

```typescript
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);

export async function POST(req: Request) {
  const payload = await req.text(); // 必须使用原始文本，不能使用 req.json()

  const event = resend.webhooks.verify({
    payload,
    headers: {
      'svix-id': req.headers.get('svix-id'),
      'svix-timestamp': req.headers.get('svix-timestamp'),
      'svix-signature': req.headers.get('svix-signature'),
    },
    secret: process.env.RESEND_WEBHOOK_SECRET,
  });

  if (event.type === 'email.received') {
    // Webhook 只包含元数据 — 需要调用 API 获取邮件正文
    const { data: email } = await resend.emails.receiving.get(
      event.data.email_id
    );
    console.log(email.text);
  }

  return new Response('OK', { status: 200 });
}
```

**关键点提示**：Webhook 负载不包含邮件正文。必须单独调用 `resend.emails.receiving.get()` 获取正文内容。

## 您需要什么？

| 任务 | 参考 |
|------|------|
| **发送单封邮件** | [发送/概述.md](references/sending/overview.md) — 参数、送达率、测试 |
| **发送批量邮件** | [发送/概述.md](references/sending/overview.md) → [发送/批量邮件示例.md](references/sending/batch-email-examples.md) |
| **完整 SDK 示例**（Node.js、Python、Go、cURL） | [发送/单封邮件示例.md](references/sending/single-email-examples.md) |
| **不可重复性、重试、错误处理** | [发送/最佳实践.md](references/sending/best-practices.md) |
| **获取、列出、重新调度、取消邮件、获取指标** | [发送/邮件管理.md](references/sending/email-management.md) |
| **接收入站邮件** | [接收.md](references/receiving.md) — 域名设置、Webhook、附件 |
| **管理模板**（创建、删除、变量） | [模板.md](references/templates.md) — 生命周期、别名、分页 |
| **设置 Webhook**（事件、验证） | [Webhook.md](references/webhooks.md) — 验证、创建、删除、重试计划、IP 允许列表 |
| **管理域名**（创建、验证、申领、DNS） | [域名.md](references/domains.md) — 区域、TLS、跟踪、申领、功能 |
| **管理联系人**（创建、删除、属性） | [联系人.md](references/contacts.md) — 分段、主题、自定义属性、批量 CSV 导入 |
| **发送广播**（营销活动） | [广播.md](references/broadcasts.md) — 生命周期、调度、模板变量 |
| **管理 API 密钥** | [API-密钥.md](references/api-keys.md) — 权限范围、域名限制 |
| **查看 API 请求日志** | [日志.md](references/logs.md) — 列出和获取 API 调用历史、调试 |
| **定义联系人属性** | [联系人属性.md](references/contact-properties.md) — 联系人的自定义字段 |
| **管理分段**（联系人分组） | [分段.md](references/segments.md) — 广播定位、联系人分组 |
| **管理主题**（订阅） | [主题.md](references/topics.md) — 订阅/退订偏好、广播过滤 |
| **创建自动化**（事件驱动工作流） | [自动化.md](references/automations.md) — 步骤、连接、运行、条件 |
| **定义和发送事件**（自动化触发） | [事件.md](references/events.md) — 模式、负载、联系人关联 |
| **安装 SDK**（8+ 种语言） | [安装.md](references/installation.md) |
| **设置 AI 代理收件箱** | 安装 `agent-email-inbox` 技能 — 涵盖对不可信输入的安全级别 |

## SDK 版本要求

始终安装最新版本的 SDK。以下是完整功能（发送、接收、Webhook 验证）所需的最小版本：

| 语言 | 包 | 最小版本 | 安装 |
|------|------|-------------|---------|
| Node.js | `resend` | >= 6.14.0 | `npm install resend` |
| Python | `resend` | >= 2.34.0 | `pip install resend` |
| Go | `resend-go/v3` | >= 3.11.0 | `go get github.com/resend/resend-go/v3` |
| Ruby | `resend` | >= 1.6.0 | `gem install resend` |
| PHP | `resend/resend-php` | >= 1.1.0 | `composer require resend/resend-php` |
| Rust | `resend-rs` | >= 0.26.1 | `cargo add resend-rs` |
| Java | `resend-java` | >= 4.16.0 | 查看 [安装.md](references/installation.md) |
| .NET | `Resend` | >= 0.2.1 | `dotnet add package Resend` |

> **如果项目已安装 Resend SDK**，请检查版本并升级（如果低于最小版本）。旧版 SDK 可能缺少 `webhooks.verify()`、`emails.receiving.get()` 或 `domains.claims.*` 功能。

查看 [安装.md](references/installation.md) 获取完整安装命令、语言检测和 cURL 降级方案。

## 常见设置

### API 密钥

存储在环境变量中 — 不要硬编码：
```bash
export RESEND_API_KEY=re_xxxxxxxxx
```

在 [resend.com/api-keys](https://resend.com/api-keys) 获取您的密钥。

### 检测项目语言

检查以下文件：`package.json`（Node.js）、`requirements.txt`/`pyproject.toml`（Python）、`go.mod`（Go）、`Gemfile`（Ruby）、`composer.json`（PHP）、`Cargo.toml`（Rust）、`pom.xml`/`build.gradle`（Java）、`*.csproj`（.NET）。

## 常见错误

| # | 错误 | 修复 |
|---|---------|-----|
| 1 | **无不可重复性密钥的重试** | 始终包含不可重复性密钥 — 防止重试时发送重复邮件。格式：`<事件类型>/<实体ID>` |
| 2 | **未验证 Webhook 签名** | 始终使用 `resend.webhooks.verify()` 验证 — 未验证的事件不可信 |
| 3 | **模板变量名不匹配** | 变量名区分大小写 — 必须与模板定义完全匹配。使用三重花括号 `{{{VAR}}}` 语法 |
| 4 | **期待 Webhook 负载包含邮件正文** | Webhooks 只包含元数据 — 需要单独调用 `resend.emails.receiving.get()` 获取正文内容 |
| 5 | **使用 try/catch 处理 Node.js SDK 错误** | SDK 返回 `{ data, error }` — 显式检查 `error`，不要用 try/catch 包裹 |
| 6 | **使用批量发送带附件的邮件** | 批量发送不支持附件 — 使用单发替代 |
| 7 | **使用假邮件（test@gmail.com）测试** | 使用 `delivered@resend.dev` — 假地址会退回并损害发送者声誉 |
| 8 | **使用草稿模板发送** | 模板必须先发布才能发送 — 先调用 `.publish()` |
| 9 | **同一发送调用中同时使用 `html` + `template`** | 互斥 — 使用模板时移除 `html`/`text`/`react` |
| 10 | **入站 MX 记录不是最低优先级** | 确保 Resend 的 MX 记录具有最低编号（最高优先级），否则邮件不会路由 |
| 11 | **从 `resend.dev` 发送时返回 403** | 默认的 `onboarding@resend.dev` 是沙盒 — 只能发送到您的 Resend 账户邮箱。先验证您的域名 |
| 12 | **403 域名不匹配** | `from` 地址域名必须与已验证域名完全匹配。已验证 `send.acme.com` 但从 `user@acme.com` 发送会失败 |
| 13 | **从浏览器调用 Resend API（CORS）** | API 不支持 CORS — 这是故意的，以保护您的 API 密钥。始终从服务器端（API 路由、服务器函数）调用 |
| 14 | **401 `restricted_api_key`** | 使用了仅发送功能的 API 密钥，但在非发送端点（域名、联系人等）调用。创建全权限密钥替代 |

## 跨领域问题

### 发送 + 接收一起使用

自动回复、邮件转发或任何接收后发送的工作流需要这两种功能：
1. 先设置入站域名（见 [接收.md](references/receiving.md)）
2. 设置发送功能（见 [发送/概述.md](references/sending/overview.md)）
3. 注意：批量发送不支持附件或调度 — 附件转发时使用单发发送

### AI 代理收件箱

如果您的系统处理不可信的邮件内容并执行操作（退款、数据库更改、转发），安装 `agent-email-inbox` 技能。无论是否使用 AI，任何解释外部发送者自由形式邮件内容的系统都需要安全措施。

### 营销邮件

此技能中的发送功能用于 **事务性邮件**（收据、确认、通知）。对于具有退订链接和参与跟踪的大规模订阅者列表的营销活动，请使用 Resend 广播 — 查看 [广播.md](references/broadcasts.md) 获取 API。

### 域名预热

新域名必须逐步增加发送量。第一天限制：新域名约 150 封邮件，现有域名约 1,000 封。查看 [发送/概述.md](references/sending/overview.md) 中的预热计划。

### 测试

**永远不要在真实邮件提供商上使用假地址**（test@gmail.com、fake@outlook.com） — 它们会退回并损害发送者声誉。

| 地址 | 结果 |
|---------|--------|
| `delivered@resend.dev` | 模拟成功送达 |
| `bounced@resend.dev` | 模拟硬退回 |
| `complained@resend.dev` | 模拟垃圾邮件投诉 |

### 退订列表

Resend 自动退订硬退回和垃圾邮件投诉的地址。向退订地址发送会触发 `email.suppressed` Webhook 事件而不是尝试投递。在 Dashboard → Suppressions 中管理。

### Webhook 事件类型

| 事件 | 触发 |
|-------|---------|
| `email.sent` | API 请求成功 |
| `email.delivered` | 到达收件人邮件服务器 |
| `email.bounced` | 永久拒绝（硬退回） |
| `email.complained` | 收件人标记为垃圾邮件 |
| `email.opened` / `email.clicked` | 收件人参与 |
| `email.delivery_delayed` | 软退回，Resend 重试 |
| `email.received` | 入站邮件到达 |
| `domain.*` / `contact.*` | 域名/联系人更改 |

查看 [webhooks.md](references/webhooks.md) 获取完整详情、签名验证和重试计划。

## 错误处理快速参考

| 代码 | 操作 |
|------|--------|
| 400, 422 | 修复请求参数，不要重试 |
| 401 | 检查 API 密钥 — `restricted_api_key` 表示使用仅发送功能的密钥在非发送端点 |
| 403 | 验证域名所有权 — 常见原因：`resend.dev` 沙盒、`from` 域名不匹配、未验证域名 |
| 409 | 不可重复性冲突 — 使用新密钥或修复负载 |
| 429 | 被限流 — 使用指数退避重试（默认速率限制：2 req/s） |
| 500 | 服务器错误 — 使用指数退避重试 |

## 资源

- [Resend 文档](https://resend.com/docs)
- [API 参考](https://resend.com/docs/api-reference)
- [控制台](https://resend.com/emails)
