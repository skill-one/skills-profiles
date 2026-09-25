# Webhooks

输出带有 `verifyWebhook(req)` 验证的完整、可工作的 webhook 处理程序。

## 何时使用 Webhooks

Webhooks 是**异步的**并且**最终一致性**的。传输速度快，但不保证立即到达，偶尔可能会失败（Svix 按固定计划重试）。使用它们来：

- 数据库同步（一个独立的用户 / 组织表，遵循 Clerk）
- 通知（欢迎邮件、Slack 提醒、内部警报）
- 由生命周期事件触发的集成

**不要**依赖 webhook 传输作为同步流程的一部分，例如用户入职流程（“用户注册，然后我们从我们的数据库中读取 X”）。对于用户刚刚创建的数据，请从 [Clerk 会话令牌](https://clerk.com/docs/guides/sessions/session-tokens) 或直接调用 Backend API。当您需要有关会话令牌不携带的*其他用户或事件*的数据时，webhooks 填补了这一空白。

## 验证每个 Webhook

使用来自特定框架的包中的 `verifyWebhook(req)`（例如 `@clerk/nextjs/webhooks`、`@clerk/express/webhooks` 等）。它自动读取 `CLERK_WEBHOOK_SIGNING_SECRET` 并在签名无效时抛出错误。跳过验证，即使对于仅用于通知的处理程序，也会使端点暴露于伪造的事件。

## 将 Webhook 路由设为公开

Webhook 路由必须排除 Clerk 中间件的保护。如果没有这样做，Clerk 会返回 401。

```typescript
// proxy.ts (Next.js <=15: middleware.ts)
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isPublicRoute = createRouteMatcher(['/api/webhooks(.*)'])

export default clerkMiddleware(async (auth, req) => {
  if (!isPublicRoute(req)) await auth.protect()
})
```

## 完整的 Webhook 处理程序（Next.js App Router）

```typescript
// app/api/webhooks/route.ts
import { verifyWebhook } from '@clerk/nextjs/webhooks'
import { NextRequest } from 'next/server'
import { db } from '@/lib/db'

export async function POST(req: NextRequest) {
  // 始终验证 - 永远不要跳过，即使对于仅用于通知的处理程序
  let evt
  try {
    evt = await verifyWebhook(req) // 自动使用 CLERK_WEBHOOK_SIGNING_SECRET 环境变量
  } catch (err) {
    console.error('Webhook 验证失败:', err)
    return new Response('验证失败', { status: 400 })
  }

  if (evt.type === 'user.created') {
    const { id, email_addresses, first_name, last_name } = evt.data
    const email = email_addresses[0]?.email_address
    const name = `${first_name ?? ''} ${last_name ?? ''}`.trim()
    await db.users.create({ data: { clerkId: id, email, name } })
  }

  if (evt.type === 'user.updated') {
    const { id, email_addresses, first_name, last_name } = evt.data
    const email = email_addresses[0]?.email_address
    await db.users.update({ where: { clerkId: id }, data: { email, first_name, last_name } })
  }

  if (evt.type === 'user.deleted') {
    const { id } = evt.data
    await db.users.delete({ where: { clerkId: id } })
  }

  if (evt.type === 'organizationMembership.created') {
    const { organization, public_user_data, role } = evt.data
    const orgId = organization.id
    const userId = public_user_data.user_id
    await db.teamMembers.create({ data: { orgId, userId, role } })
  }

  if (evt.type === 'organizationMembership.deleted') {
    const { organization, public_user_data } = evt.data
    const orgId = organization.id
    const userId = public_user_data.user_id
    await db.teamMembers.delete({ where: { orgId_userId: { orgId, userId } } })
  }

  return new Response('OK', { status: 200 })
}
```

## 完整示例：用户创建时发送欢迎邮件（Resend）+ Slack 通知

仅用于通知的处理程序仍然验证签名。与数据库同步处理程序的模式相同：

```typescript
// app/api/webhooks/route.ts
import { verifyWebhook } from '@clerk/nextjs/webhooks'
import { NextRequest } from 'next/server'
import { Resend } from 'resend'

const resend = new Resend(process.env.RESEND_API_KEY)

export async function POST(req: NextRequest) {
  // 第一步：始终验证 webhook 签名 - 绝对不要跳过
  let evt
  try {
    evt = await verifyWebhook(req) // 使用 CLERK_WEBHOOK_SIGNING_SECRET 环境变量
  } catch (err) {
    console.error('Webhook 验证失败:', err)
    return new Response('验证失败', { status: 400 })
  }

  // 第二步：监听 user.created 事件
  if (evt.type === 'user.created') {
    // 第三步：从 webhook 负载中提取用户邮箱和姓名
    const { id, email_addresses, first_name, last_name } = evt.data
    const email = email_addresses[0]?.email_address
    const name = `${first_name ?? ''} ${last_name ?? ''}`.trim()

    // 第四步：调用 Resend API 发送欢迎邮件
    await resend.emails.send({
      from: 'noreply@yourdomain.com',
      to: email,
      subject: '欢迎!',
      html: `<p>Hi ${name}, 欢迎使用我们的应用!</p>`,
    })

    // 第五步：向 Slack 频道发布通知
    await fetch(process.env.SLACK_WEBHOOK_URL!, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: `新用户注册: ${name} (${email})`,
      }),
    })
  }

  // 始终返回 200 以确认接收
  return new Response('OK', { status: 200 })
}
```

**同时包含 proxy.ts（Next.js <=15: middleware.ts）以使路由公开：**
```typescript
// proxy.ts (Next.js <=15: middleware.ts)
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'
const isPublicRoute = createRouteMatcher(['/api/webhooks(.*)'])
export default clerkMiddleware(async (auth, req) => {
  if (!isPublicRoute(req)) await auth.protect()
})
```

## 完整示例：组织成员同步到数据库

```typescript
// app/api/webhooks/route.ts
import { verifyWebhook } from '@clerk/nextjs/webhooks'
import { NextRequest } from 'next/server'
import { db } from '@/lib/db' // 您的数据库客户端

export async function POST(req: NextRequest) {
  // 始终验证签名 - 永远不要跳过，即使对于简单的处理程序
  let evt
  try {
    evt = await verifyWebhook(req) // 使用 CLERK_WEBHOOK_SIGNING_SECRET 环境变量
  } catch (err) {
    console.error('Webhook 验证失败:', err)
    return new Response('验证失败', { status: 400 })
  }

  if (evt.type === 'organization.created') {
    const { id, name } = evt.data
    await db.workspaces.create({
      data: { orgId: id, name, createdAt: new Date() },
    })
  }

  if (evt.type === 'organizationMembership.created') {
    // 从负载中提取组织 ID、用户 ID 和角色
    const { organization, public_user_data, role } = evt.data
    const orgId = organization.id
    const userId = public_user_data.user_id

    // 添加到 team_members 表
    await db.team_members.create({
      data: { orgId, userId, role },
    })

    // 为新成员创建工作区记录
    await db.workspaces.create({
      data: { orgId, userId, createdAt: new Date() },
    })
  }

  if (evt.type === 'organizationMembership.deleted') {
    // 从负载中提取组织 ID 和用户 ID
    const { organization, public_user_data } = evt.data
    const orgId = organization.id
    const userId = public_user_data.user_id

    // 从 team_members 表中删除
    await db.team_members.delete({
      where: { orgId, userId },
    })

    // 删除工作区记录
    await db.workspaces.deleteMany({
      where: { orgId, userId },
    })
  }

  // 成功时返回 200 状态
  return new Response('OK', { status: 200 })
}
```

## 其他框架

对于 Express、Astro、Fastify、Nuxt、React Router 和 TanStack Start，使用特定于框架的 `verifyWebhook` 适配器。每个 Clerk SDK 包都包含自己的 (`@clerk/express/webhooks`、`@clerk/astro/webhooks`、`@clerk/fastify/webhooks` 等)。

有关每个框架的完整处理程序示例，请参阅 `references/frameworks.md`。

## `evt.data` 的类型缩小

`verifyWebhook` 返回 `WebhookEvent`，它是所有事件类型的区分联合。使用 `evt.type` 缩小以安全地访问 `evt.data`：

```typescript
const evt = await verifyWebhook(req)

if (evt.type === 'user.created') {
  // evt.data 现在是 UserJSON，自动补全 id、email_addresses 等
  console.log(evt.data.id)
}
```

对于手动输入嵌套负载，请从您框架的 webhook 子路径导入 JSON 类型：`DeletedObjectJSON`、`EmailJSON`、`OrganizationInvitationJSON`、`OrganizationJSON`、`OrganizationMembershipJSON`、`SessionJSON`、`SMSMessageJSON`、`UserJSON`。

## 负载字段参考

### 用户事件 (`user.created`、`user.updated`、`user.deleted`)
```typescript
const {
  id,                  // Clerk 用户 ID
  email_addresses,     // 数组；[0].email_address 是主要邮箱
  first_name,
  last_name,
  image_url,
  public_metadata,
} = evt.data
```

### 组织事件 (`organization.created`、`organization.updated`、`organization.deleted`)
```typescript
const {
  id,    // org ID
  name,  // org 名称
  slug,
} = evt.data
```

### 组织成员事件 (`organizationMembership.created`、`organizationMembership.updated`、`organizationMembership.deleted`)
```typescript
const {
  organization,        // { id, name, ... }
  public_user_data,    // { user_id, first_name, last_name, ... }
  role,                // 例如 'org:admin'、'org:member'
} = evt.data
// 访问：organization.id、public_user_data.user_id、role
```

## 支持的事件（完整目录）

**用户**: `user.created` `user.updated` `user.deleted`

**会话**: `session.created` `session.ended` `session.removed` `session.revoked`

**组织**: `organization.created` `organization.updated` `organization.deleted`

**组织成员**: `organizationMembership.created` `organizationMembership.updated` `organizationMembership.deleted`

**组织域**: `organizationDomain.created` `organizationDomain.updated` `organizationDomain.deleted`

**组织邀请**: `organizationInvitation.accepted` `organizationInvitation.created` `organizationInvitation.revoked`

**通信**: `email.created` `sms.created`

**候补名单**: `waitlistEntry.created` `waitlistEntry.updated`

**权限**: `permission.created` `permission.updated` `permission.deleted`

**角色**: `role.created` `role.updated` `role.deleted`

**订阅**: `subscription.created` `subscription.updated` `subscription.active` `subscription.pastDue`

**订阅项**: `subscriptionItem.created` `subscriptionItem.active` `subscriptionItem.updated` `subscriptionItem.canceled` `subscriptionItem.upcoming` `subscriptionItem.ended` `subscriptionItem.abandoned` `subscriptionItem.incomplete` `subscriptionItem.pastDue` `subscriptionItem.freeTrialEnding`

**支付**: `paymentAttempt.created` `paymentAttempt.updated`

## Webhook 可靠性

**重试**: Svix 按固定计划重试失败的 webhook（请参阅 [Svix 重试计划](https://docs.svix.com/retries)）。返回 2xx 以成功，4xx/5xx 以重试。使用 `svix-id` 头作为幂等性键来去重重试的事件。

**重放**: 失败的 webhook 可以从控制台重放。

## 常见陷阱

| 症状 | 原因 | 修复 |
|-------|-------|-----|
| 验证失败（Next.js） | 错误的导入或使用 | 使用 `@clerk/nextjs/webhooks`，直接传递 `req` |
| 验证失败（Express） | 使用 `express.json()` | 使用 `express.raw({ type: 'application/json' })` 对于 webhook 路由 |
| 路由未找到（404） | 路径错误 | 使用 `/api/webhooks` 或保留现有路径 |
| 未授权（401） | 路由受中间件保护 | 在 `clerkMiddleware()` 中使路由公开 |
| 数据库中无数据 | 异步任务挂起 | 等待/检查日志 |
| 重复条目 | 仅处理 `user.created` | 还要处理 `user.updated` |
| 超时 | 处理程序太慢 | 队列异步工作，首先返回 200 |

## 测试与部署

**本地**: 使用 Clerk CLI 的第一方隧道——无需认证或关联项目：

```sh
clerk webhooks listen --token "$(clerk webhooks token)" --forward-to http://localhost:3000/api/webhooks
```

将打印的转发 URL（`https://webhooks.clerk.com/in/c_.../`）作为 webhook 端点添加到控制台——事件不会流动，直到您这样做。`svix-*` 头被保留，因此 `verifyWebhook()` 可以像往常一样针对该端点的签名密钥工作。标志、离线签名检查（`clerk webhooks verify`）和代理模式行为在 `clerk-cli` 技能中。没有 CLI，请自己隧道 `localhost:3000`（`ngrok`、`localtunnel`、`Cloudflare Tunnel`）并将公共 URL 添加到控制台端点。

**生产**: 将 webhook 端点 URL 更新为生产域名。将 `CLERK_WEBHOOK_SIGNING_SECRET` 复制到生产环境变量。

## 参考

| 参考 | 描述 |
|-------|-------------|
| `references/frameworks.md` | Express、Astro、Fastify、Nuxt、React Router、TanStack Start 的 webhook 处理程序示例 |

## 另请参阅

- `clerk-cli` - `clerk webhooks listen`/`verify` 用于本地 webhook 测试
- `clerk-setup` - 初始 Clerk 安装
- `clerk-orgs` - 组织成员事件
- `clerk-billing` - 订阅、订阅项和支付尝试事件
- `clerk-backend-api` - 通过直接 API 调用同步
