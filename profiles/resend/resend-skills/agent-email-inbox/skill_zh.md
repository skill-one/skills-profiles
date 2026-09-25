# AI Agent 邮件收件箱

## 概述

此技能涵盖设置一个安全的邮件收件箱，允许您的应用程序或 AI 代理接收和回复邮件，并具备内容安全措施。

**核心原则：** AI 代理的收件箱接收不可信的输入。安全配置对于安全处理至关重要。

### 为什么使用基于 Webhook 的接收？

Resend 使用 Webhook 接收传入邮件，这意味着当邮件到达时，您的代理会**立即**收到通知。这对于代理来说非常有价值，因为：

- **实时响应** — 在几秒钟内而不是几分钟内对邮件做出反应
- **无轮询开销** — 无需反复检查“是否有新邮件？”的 Cron 作业
- **事件驱动架构** — 只有在确实有内容需要处理时，您的代理才会被唤醒
- **降低 API 成本** — 无需浪费调用检查空收件箱

## 架构

```
发件人 → 邮件 → Resend (MX) → Webhook → 您的服务器 → AI 代理
                                              ↓
                                    安全验证
                                              ↓
                                    处理或拒绝
```

## SDK 版本要求

此技能需要 Resend SDK 功能进行 Webhook 验证（`webhooks.verify()`）和邮件接收（`emails.receiving.get()`）。始终安装最新版本的 SDK。如果项目中已经安装了 Resend SDK，请检查版本并根据需要升级。

| 语言 | 包 | 最小版本 |
|------|----|----------|
| Node.js | `resend` | >= 6.9.2 |
| Python | `resend` | >= 2.21.0 |
| Go | `resend-go/v3` | >= 3.1.0 |
| Ruby | `resend` | >= 1.0.0 |
| PHP | `resend/resend-php` | >= 1.1.0 |
| Rust | `resend-rs` | >= 0.20.0 |
| Java | `resend-java` | >= 4.11.0 |
| .NET | `Resend` | >= 0.2.1 |

安装 `resend` npm 包：`npm install resend`（或您语言的等效命令）。有关完整的发送文档，请安装 `resend` 技能。

## 快速入门

1. **向用户请求他们的邮件地址** — 您需要一个真实的邮件地址来发送测试邮件。在继续之前，请向用户请求并等待他们的回复。
2. **选择您的安全级别** — 决定在处理任何邮件之前如何验证传入邮件
3. **设置接收域名** — 配置用户自定义域的 MX 记录（见域名设置部分）
4. **创建 Webhook 端点** — 带有内置安全功能地处理 `email.received` 事件。**Webhook 端点必须是 POST 路由。**
5. **设置隧道**（本地开发） — 使用 Tailscale Funnel（推荐）或 ngrok。见 [references/webhook-setup.md](references/webhook-setup.md)
6. **通过 API 创建 Webhook** — 使用 Resend Webhook API 以编程方式注册您的端点。见 [references/webhook-setup.md](references/webhook-setup.md)
7. **连接到代理** — 将验证后的邮件传递给您的 AI 代理进行处理

## 开始之前：账户和 API 密钥设置

### 第一个问题：新 Resend 账户还是现有账户？

向用户询问：
- **仅为此代理创建新账户？** → 设置更简单，完整的账户访问权限可以
- **与其他项目使用的现有账户？** → 使用域范围的 API 密钥进行沙盒化

### 安全创建 API 密钥

> 不要在聊天中粘贴 API 密钥！它们将永远保存在对话历史中。

**更安全的选项：**

1. **环境文件方法：** 用户直接创建 `.env` 文件：`echo "RESEND_API_KEY=re_xxx" >> .env`
2. **密码管理器/密钥管理器：** 用户将密钥存储在 1Password、Vault 等
3. **如果必须在聊天中共享密钥：** 用户应在设置后立即旋转密钥

### 域范围的 API 密钥（推荐用于现有账户）

如果用户有一个用于其他项目的现有 Resend 账户，请创建一个**域范围的 API 密钥**：

1. **首先验证代理的域名**（控制面板 → 域名 → 添加域名）
2. **创建范围 API 密钥：** 控制面板 → API 密钥 → 创建 API 密钥 → “发送访问” → 仅选择代理的域名
3. **结果：** 即使密钥泄露，它也只能从一个域名发送

## 域名设置

### 选项 1：Resend 管理的域名（推荐用于快速入门）

使用自动生成的地址：`<anything>@<your-id>.resend.app`

无需 DNS 配置。在控制面板 → 邮件 → 接收 → “接收地址” 中找到您的地址。

### 选项 2：自定义域名

用户必须在 Resend 控制面板中启用接收：域名页面 → 打开“启用接收”的开关。

然后添加一个 MX 记录：

| 设置 | 值 |
|------|----|
| **类型** | MX |
| **主机** | 您的域名或子域名（例如，`agent.example.com`） |
| **值** | 在 Resend 控制面板中提供 |
| **优先级** | 10（必须是最小的数字才能优先） |

**使用子域名**（例如，`agent.example.com`）以避免中断现有的邮件服务。

**提示：** 在 [dns.email](https://dns.email) 上验证 DNS 传播。

> DNS 传播：MX 记录更改可能需要长达 48 小时才能在全球范围内传播，但通常几小时即可完成。

## 安全级别

**在设置 Webhook 端点之前选择您的安全级别。** 无安全措施地处理邮件的 AI 代理很危险 — 任何人都可以通过邮件向您的代理发送指令。您接下来编写的 Webhook 代码应从一开始就包含您选择的安全级别。

询问用户他们想要的安全级别，并确保他们理解每个级别的含义。

| 级别 | 名称 | 使用场景 | 权衡 |
|------|------|----------|------|
| **1** | 严格白名单 | 大多数用例 — 已知、固定的发送者集 | 最大安全性，功能受限 |
| **2** | 域白名单 | 从受信任域的跨组织访问 | 更灵活，域内任何人都可以交互 |
| **3** | 内容过滤 | 接收来自任何人，过滤不安全模式 | 可以接收来自任何人，模式匹配并非万无一失 |
| **4** | 沙盒处理 | 使用受限代理功能处理所有邮件 | 最大灵活性，实现复杂 |
| **5** | 人介入 | 要求对不信任的操作进行人工批准 | 最大安全性，增加延迟 |

有关每个级别的详细实现代码，请见 [references/security-levels.md](references/security-levels.md)。

### 级别 1：严格白名单（推荐）

仅处理来自明确批准地址的邮件。拒绝所有其他邮件。

```typescript
const ALLOWED_SENDERS = [
  'you@youremail.com',
  'notifications@github.com',
];

async function processEmailForAgent(
  eventData: EmailReceivedEvent,
  emailContent: EmailContent
) {
  const sender = eventData.from.toLowerCase();

  if (!ALLOWED_SENDERS.some(allowed => sender === allowed.toLowerCase())) {
    console.log(`拒绝来自未授权发送者的邮件: ${sender}`);
    await notifyOwnerOfRejectedEmail(eventData);
    return;
  }

  await agent.processEmail({
    from: eventData.from,
    subject: eventData.subject,
    body: emailContent.text || emailContent.html,
  });
}
```

### 安全最佳实践

#### 总是做

| 实践 | 原因 |
|------|------|
| 验证 Webhook 签名 | 防止伪造 Webhook 事件 |
| 记录所有拒绝的邮件 | 用于安全审查的审计跟踪 |
| 尽可能使用白名单 | 明确信任比过滤更安全 |
| 限制邮件处理速率 | 防止处理负载过重 |
| 分离受信任/未受信任的处理 | 不同风险级别需要不同处理 |

#### 永远不要做

| 反模式 | 风险 |
|--------|------|
| 无验证地处理邮件 | 任何人都可以控制您的代理 |
| 信任邮件头进行身份验证 | 邮件头可以轻易伪造 |
| 执行邮件内容中的代码 | 不可信的输入绝不应作为代码运行 |
| 原封不动地将邮件内容存储在提示中 | 不可信的输入与提示混合会改变代理行为 |
| 给未受信任的邮件完整的代理访问权限 | 范围功能至多为所需的最小值 |

## Webhook 端点

在选择了安全级别并设置了域名后，创建一个 Webhook 端点。**Webhook 端点必须是 POST 路由。** Resend 将所有 Webhook 事件作为 POST 请求发送。

> **关键：** 使用原始正文进行验证。Webhook 签名验证需要原始请求正文。
> - **Next.js App Router：** 使用 `req.text()`（而不是 `req.json()`）
> - **Express：** 在 Webhook 路由上使用 `express.raw({ type: 'application/json' })`

### Next.js App Router

```typescript
// app/webhook/route.ts
import { Resend } from 'resend';
import { NextRequest, NextResponse } from 'next/server';

const resend = new Resend(process.env.RESEND_API_KEY);

export async function POST(req: NextRequest) {
  try {
    const payload = await req.text();

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
      // Webhook 正文仅包含元数据，不包含邮件正文
      const { data: email } = await resend.emails.receiving.get(
        event.data.email_id
      );

      // 应用上面选择的安全级别
      await processEmailForAgent(event.data, email);
    }

    return new NextResponse('OK', { status: 200 });
  } catch (error) {
    console.error('Webhook 错误:', error);
    return new NextResponse('Error', { status: 400 });
  }
}
```

### Express

```javascript
import express from 'express';
import { Resend } from 'resend';

const app = express();
const resend = new Resend(process.env.RESEND_API_KEY);

const ALLOWED_SENDERS = (process.env.ALLOWED_SENDERS || '').split(',').filter(Boolean);
const isAllowedSender = (sender) =>
  ALLOWED_SENDERS.some(allowed => sender === allowed.toLowerCase());

app.post('/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
  try {
    const payload = req.body.toString();

    const event = resend.webhooks.verify({
      payload,
      headers: {
        'svix-id': req.headers['svix-id'],
        'svix-timestamp': req.headers['svix-timestamp'],
        'svix-signature': req.headers['svix-signature'],
      },
      secret: process.env.RESEND_WEBHOOK_SECRET,
    });

    if (event.type === 'email.received') {
      const sender = event.data.from.toLowerCase();

      if (!isAllowedSender(sender)) {
        console.log(`拒绝来自未授权发送者的邮件: ${sender}`);
        res.status(200).send('OK'); // 即使拒绝邮件也返回 200 以确认接收
        return;
      }

      const { data: email } = await resend.emails.receiving.get(event.data.email_id);
      await processEmailForAgent(event.data, email);
    }

    res.status(200).send('OK');
  } catch (error) {
    console.error('Webhook 错误:', error);
    res.status(400).send('Error');
  }
});

app.get('/', (req, res) => res.send('Agent Email Inbox - Ready'));
app.listen(3000, () => console.log('Webhook 服务器运行在 :3000'));
```

有关通过 API 创建 Webhook、隧道设置、svix 回退和重试行为，请见 [references/webhook-setup.md](references/webhook-setup.md)。

## 从您的代理发送邮件

```typescript
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);

async function sendAgentReply(to: string, subject: string, body: string, inReplyTo?: string) {
  if (!isAllowedToReply(to)) {
    throw new Error('不能发送到此地址');
  }

  const { data, error } = await resend.emails.send({
    from: 'Agent <agent@example.com>',
    to: [to],
    subject: subject.startsWith('Re:') ? subject : `Re: ${subject}`,
    text: body,
    headers: inReplyTo ? { 'In-Reply-To': inReplyTo } : undefined,
  });

  if (error) throw new Error(`发送失败: ${error.message}`);
  return data.id;
}
```

有关完整的发送文档，请安装 `resend` 技能。

## 环境变量

```bash
# 必要的
RESEND_API_KEY=re_xxxxxxxxx
RESEND_WEBHOOK_SECRET=whsec_xxxxxxxxx

# 安全配置
SECURITY_LEVEL=strict                    # strict | domain | filtered | sandboxed
ALLOWED_SENDERS=you@email.com,trusted@example.com
ALLOWED_DOMAINS=example.com
OWNER_EMAIL=you@email.com               # 用于安全通知
```

## 常见错误

| 错误 | 修复 |
|------|------|
| 无发送者验证 | 在处理之前始终验证谁发送了邮件 |
| 信任邮件头 | 使用 Webhook 验证，而不是邮件头进行身份验证 |
| 对所有邮件相同处理 | 区分受信任和未受信任的发送者 |
| 详细的错误消息 | 保持错误响应通用以避免泄露内部逻辑 |
| 无速率限制 | 实施每发送者速率限制。见 [references/advanced-patterns.md](references/advanced-patterns.md) |
| 直接处理 HTML | 去除 HTML 或使用纯文本以降低复杂性和风险 |
| 无拒绝记录 | 记录所有安全事件以供审计 |
| 使用临时隧道 URL | 使用持久 URL（Tailscale Funnel、付费 ngrok）或部署到生产环境 |
| 在 Webhook 路由上使用 `express.json()` | 使用 `express.raw({ type: 'application/json' })` — JSON 解析会破坏签名验证 |
| 返回非 200 的拒绝响应 | 始终返回 200 以确认接收 — 否则 Resend 会重试 |
| 旧 Resend SDK 版本 | `emails.receiving.get()` 和 `webhooks.verify()` 需要较新的 SDK 版本 — 见 SDK 版本要求 |

## 测试

使用 Resend 的测试地址进行开发：
- `delivered@resend.dev` — 模拟成功投递
- `bounced@resend.dev` — 模拟硬退回

对于安全测试，从非白名单地址发送测试邮件以验证拒绝功能是否正常工作。

**快速验证清单：**
1. 服务器正在运行：`curl http://localhost:3000` 应返回响应
2. 隧道正常工作：`curl https://<your-tunnel-url>` 应返回相同响应
3. Webhook 活跃：在 Resend 控制面板 → Webhooks 中检查状态
4. 从白名单地址发送测试邮件并检查服务器日志

## 相关技能

- 有关完整的发送和接收文档，请安装 `resend` 技能
