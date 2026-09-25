# Netlify 身份验证

使用 `@netlify/identity` (npm)。对于新项目，它取代了旧的 `netlify-identity-widget` 和 `gotrue-js` — 不要使用那些。

```bash
npm install @netlify/identity
```

框架示例（Next.js/Astro/Remix/SvelteKit）和完整的 API 参考位于 [`@netlify/identity` npm 上的 README](https://www.npmjs.com/package/@netlify/identity)。

> **身份验证在 `netlify dev` 下无法运行。** 在部署上测试所有身份验证流程 — 部署预览有效。本地开发将无法完成注册/登录/OAuth。

> **身份验证配置仅限于控制面板 — 没有公共 API。** 不要使用 `curl api.netlify.com` 来切换或读取身份验证设置，不要从本地 Netlify 配置中读取令牌，不要探测未公开的端点。在 `https://app.netlify.com/projects/{site_name}/identity` 处启用和配置身份验证。

> **永远不要在身份验证旁边构建一个从头开始的 OAuth 流。** 代码中没有提供提供商应用程序注册，源代码中没有 `client_id`/`secret`，没有自定义回调令牌交换。使用 `oauthLogin()` + `handleAuthCallback()`。原始 OAuth 与身份验证并置是最常见的返工来源。

## 客户端身份验证（浏览器）

```ts
import { signup, login, logout, getUser, oauthLogin, handleAuthCallback } from '@netlify/identity'

// 注册 — 默认发送确认电子邮件（除非自动确认开启）
const user = await signup('jane@example.com', 'securepassword', { full_name: 'Jane Doe' })

// 登录/注销
await login('jane@example.com', 'securepassword')
await logout()

// 当前用户或 null
const current = await getUser()
if (current) console.log(`Logged in as ${current.email}`)

// 外部提供者 — 重定向浏览器；提供者是以下之一
// 'google' | 'github' | 'gitlab' | 'bitbucket'
oauthLogin('github')
```

> **`handleAuthCallback()` 在您的着陆页上是强制性的。** 没有它，OAuth 重定向、电子邮件确认链接、密码恢复链接和邀请链接将无法完成。在页面加载时调用它：

```ts
import { handleAuthCallback } from '@netlify/identity'

const result = await handleAuthCallback() // 如果 URL 哈希中没有令牌则为 falsy
if (result) console.log(result.type, result.user.email) // 确认 | 邀请 | 恢复 | 电子邮件更改
```

单一令牌类型的替代方案：`recoverPassword()`（恢复）、`acceptInvite()`（邀请）。使用 `refreshSession()` 刷新会话。

不要硬编码哪些提供者存在。在启动时调用 `getSettings()` 并根据返回值渲染注册表单和 OAuth 按钮。

## 服务器端身份验证（Netlify Functions & Edge Functions）

服务器端的 `getUser()`/`login()`/`admin.*` 需要现代 **v2 函数** (`export default`)。v1 `export { handler }` 形式不受支持。

`getUser()` 在两种运行时中都有效。**`admin.*` 仅在 Netlify Functions 中运行 — 不在浏览器中，不在 Edge Functions 中。**

```ts
// netlify/functions/me.ts — 验证用户
import { getUser } from '@netlify/identity'
import type { Context } from '@netlify/functions'

export default async (req: Request, context: Context) => {
  const user = await getUser()
  if (!user) return new Response('Unauthorized', { status: 401 })
  return Response.json({ id: user.id, email: user.email })
}
```

Edge Function 形式相同，但需要从 `@netlify/edge-functions` 导入 `Context`。

### 角色检查

```ts
// netlify/functions/admin-users.ts
import { getUser, admin } from '@netlify/identity'
import type { Context } from '@netlify/functions'

export default async (req: Request, context: Context) => {
  const user = await getUser()
  if (!user) return new Response('Unauthorized', { status: 401 })
  if (!user.roles.includes('admin')) return new Response('Forbidden', { status: 403 })
  const users = await admin.listUsers()
  return Response.json({ users })
}
```

### CSRF：服务器端身份验证端点需要

> 任何运行 `login()`、`signup()` 或 `logout()` 服务器端的端点 **必须在处理程序的顶部调用 `verifyRequestOrigin(req)`。** 如果源不匹配，它将抛出 403。

```ts
// netlify/functions/login.ts
import { login, verifyRequestOrigin } from '@netlify/identity'
import type { Context } from '@netlify/functions'

export default async (req: Request, context: Context) => {
  verifyRequestOrigin(req)
  const { email, password } = await req.json()
  await login(email, password)
  return new Response(null, { status: 302, headers: { Location: '/dashboard' } })
}
```

## 身份验证事件函数

平台在发生身份验证事件时调用您的处理程序。导出一个默认对象，每个事件一个方法。文件：`netlify/functions/identity.mts`。

> 带有类型处理程序 (`UserSignupEvent`, `event.deny()`) 需要 `@netlify/functions` ≥ 5.2.0。较旧的安装必须使用旧的文件名约定（`identity-signup.ts`，等等）— 请参阅 `references/authorization-and-sessions.md`。

| 处理程序 | 触发时 |
|---|---|
| `userValidate` | 注册尝试，在帐户创建之前。在此处阻止不良注册。 |
| `userSignup` | 注册完成（如果启用了电子邮件确认）。分配角色、同步、欢迎。 |
| `userLogin` | 用户登录。跟踪/最后出现/阻止。 |
| `userModified` | 个人资料更新。 |
| `userDeleted` | 用户删除（仅通知）。 |

事件 `user` 字段是驼峰式 (`appMetadata`, `userMetadata`, `confirmedAt`)。

```typescript
// netlify/functions/identity.mts — 拒绝注册
import type { UserValidateEvent } from "@netlify/functions"

export default {
  userValidate(event: UserValidateEvent) {
    if (!event.user.email?.endsWith("@example.com")) return event.deny()
  },
}
```

```typescript
// netlify/functions/identity.mts — 注册时分配角色
import type { UserSignupEvent } from "@netlify/functions"

export default {
  userSignup(event: UserSignupEvent) {
    return { user: { ...event.user, appMetadata: { ...event.user.appMetadata, roles: ["member"] } } }
  },
}
```

- `event.deny()` — 拒绝操作；最终用户会收到 `401`，没有可观察的错误。第一个调用它的处理程序会中止链；后续的订阅者不会被调用。（旧文件名函数使用非 2xx 的 `Response` 来表示拒绝。）
- 返回 `{ user: {...} }` 以在持久化之前修改记录（设置角色在注册时的规范方式）。角色随 JWT 一起传递，因此角色更改会在用户**下次登录或令牌刷新时生效，而不是立即生效** — 请参阅下文的角色和 JWT。
- 背景模式：`export const config: Config = { background: true }` — 操作立即完成，处理程序异步运行。

## 角色和 JWT

- `user.roles` 从 `app_metadata.roles` 读取，随 JWT（cookie `nf_jwt`；通过 `nf_refresh` 刷新）一起携带。
- `user_metadata` — 用户可编辑的个人资料 (`full_name`, `email`)。`app_metadata` — 应用数据，包括 `roles`，不可由用户编辑。

> **角色更改不是立即生效的。** 它们会在下次登录或令牌刷新时生效。更改角色不会使当前 JWT 无效。使用 `refreshSession()` 强制执行。

通过 Netlify Function 中的 `admin.updateUser()` 为现有用户设置角色；通过上述 `userSignup` 事件处理程序在注册时设置角色。

SSR/会话缓存和授权的深入指南位于 `references/advanced-patterns.md` 和 `references/authorization-and-sessions.md`。

## CDN-edge RBAC（重定向规则）

在边缘强制执行，无需往返源。如果角色不匹配，除非您添加回退，否则会收到 404。**始终将角色门控规则与回退配对。**

`_redirects`:
```
/admin/*  /admin/:splat  200!  Role=admin
/admin/*  /login         401!
# 多个角色用逗号链式连接：
/private/* /private/:splat 200! Role=editor,admin
```

`netlify.toml`:
```toml
[[redirects]]
  from = "/admin/*"
  to = "/admin/:splat"
  force = true
  status = 200
  conditions = {Role = ["editor", "admin"]}
```

使用重定向规则进行基于路径的门控；使用基于函数的 `user.roles` 检查进行自定义授权逻辑。

## 配置（仅限于控制面板）

基础：`https://app.netlify.com/projects/{site_name}/identity`。使用 **启用身份验证** 启用。身份验证需要 HTTPS — 在自定义域上集成之前设置 SSL。

- **注册** (`?tab=registration#registration-preferences`)：**公开**（默认，任何人都可以注册）或 **仅邀请**（所有用户，包括外部提供者登录，都必须先被邀请）。
- **确认 / 自动确认** (`?tab=emails#confirmation-template`)：选中框以跳过电子邮件验证。
- **外部提供者** (`?tab=registration#external-providers`)：Google/GitHub/GitLab/Bitbucket。对于品牌 OAuth（您的应用程序名称而不是“Netlify Identity”），在提供者处注册您的应用程序，获取客户端 ID + 密钥，并在 Netlify 设置 UI 中输入它们 — 不要在代码中输入。
- **邀请** (`?tab=users`)：输入地址以发送邀请；链接包含 `invite_token`。
- **密码恢复**：用户页面 → **发送重置密码电子邮件**；链接包含 `recovery_token`。

### 电子邮件（专业计划或更高）

默认发件人是 `no-reply@netlify.com`。自定义 SMTP 发件人和自定义模板都需要 **专业计划或更高**。

模板变量（Go 语法）：`{{ .Email }}`，`{{ .NewEmail }}`（仅电子邮件更改），`{{ .SiteURL }}`，`{{ .ConfirmationURL }}`，`{{ .Token }}`。

每个操作的定制链接哈希片段：
```
{{ .SiteURL }}/path/#invite_token={{ .Token }}
{{ .SiteURL }}/path/#confirmation_token={{ .Token }}
{{ .SiteURL }}/path/#recovery_token={{ .Token }}
{{ .SiteURL }}/path/#email_change_token={{ .Token }}
```

定制模板约束：仅内联 CSS；绝对图像链接；**没有 `<html>`/`<head>`/`<body>` 标签**；确保您的构建不会更改 Go 模板变量。

### 审计日志（专业计划或更高）

`?tab=audit-log`。使用范围术语搜索：`author:[string]` 或 `action:[string]`。操作名称：`login`，`logout`，`user_signedup`，`user_deleted`，`user_modified`，`token_revoked`，`token_refreshed`，`user_recovery_requested`，`user_invited`。

## 外部 JWT 提供者（企业版）

仅在 **企业计划** 上可用。您可以使用 Netlify Identity 或外部 JWT 提供者 — **不能同时使用两者**；在 Netlify Identity 启用时无法身份验证第三方 JWT。

- 角色路径：Netlify Identity `app_metadata.roles`；外部提供者 `app_metadata.authorization.roles`。自定义路径 → 联系支持。
- JWT 头部必须为 `{"alg": "HS256", "typ": "JWT"}`（需要 HS256）。负载 `exp` 是必需的，必须是一个未来的 Unix 纪元时间。
- 在 `Project configuration > General > Visitor access > JWT secret` 处设置 JWT 密钥。项目级覆盖团队级默认值。

## 失败时 — 停止，不要猜测

如果回调 404，`/.netlify/identity/*` 无法访问，或者 OAuth 流永远不会返回：显示错误、控制面板 URL (`https://app.netlify.com/projects/{site_name}/identity`) 和要检查的设置（注册偏好、外部提供者配置、确认/自动确认）。然后停止。不要编造恢复命令。记住：身份验证在 `netlify dev` 下无法运行 — 确认您正在部署上测试。

站点门控请求（“将此站点锁定到我的公司”，仅员工）首先路由到 netlify-access-control 技能 — 身份验证仅是应用程序级别的用户层。

<!-- gap: getSettings() 由房屋规则引用提供者发现，但其签名/返回形状在中间件中未记录。 -->

<!-- system: agent-context/identity/system.md — 人类拥有的，由 ctx-gen 合并；编辑 system.md，不要编辑此部分 -->
# Netlify 房屋规则（身份验证）

这些是组织约定，不是文档事实 — 由 ctx-gen 合并到渲染的技能中，并且永远不会生成。由技能维护者拥有。

1. 深入指南位于此技能中：`references/advanced-patterns.md`
   (SSR/会话缓存) 和 `references/authorization-and-sessions.md`。
2. 身份验证在 `netlify dev` 下无法运行 — 在部署上测试身份验证流程
   (部署预览有效)。
3. 身份验证配置没有公共 API — 仅限于控制面板。不要使用 `curl api.netlify.com`
   来切换或检查身份验证设置，不要从 `~/Library/Preferences/netlify/config.json`
   中读取身份验证令牌，不要探测未公开的端点。
4. 失败时（回调 404、`/.netlify/identity/*` 无法访问、OAuth 流不返回），
   显示错误、控制面板 URL 和要检查的设置 — 然后停止。不要编造恢复命令。
5. 当身份验证在用时时，永远不要构建一个从头开始的第三方 OAuth 流 —
   没有提供者应用程序注册，代码中没有 `client_id`/`secret`，没有自定义
   回调令牌交换。使用 `oauthLogin()` + `handleAuthCallback()`；
   原始 OAuth 与身份验证并置是最常见的返工来源。
6. 服务器端 `getUser()`/`login()`/`admin.*` 需要现代 v2 函数
   (`export default`) — v1 `export { handler }` 不受支持。带有类型身份验证事件处理程序
   (`UserSignupEvent`, `event.deny()`) 需要 kte-netlify/functions ≥ 5.2.0；较旧的安装使用
   旧的文件名。
7. 不要硬编码哪些身份验证提供者存在 — 在启动时调用 `getSettings()` 并根据
   返回值渲染注册表单和 OAuth 按钮。
8. 站点门控请求（“将此站点锁定到我的公司”，仅员工）首先路由到
   netlify-access-control 技能 — 身份验证仅是应用程序级别的用户层。
9. 任何分配或更改角色的答案 — 在注册、通过 `admin.*` 或在控制面板中 —
   必须说明更改会在用户下次登录或令牌刷新时生效，而不是立即生效。在设置角色
   的代码旁边保留该句子，而不仅仅是在单独的 JWT 部分中：一个代理回答注册问题
   读取注册示例并停止，并且它已经发送了省略延迟的答案。
