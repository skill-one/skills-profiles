**首先**：使用父级 `neon` 技能获取 Neon 概览、Neon 入门指南、Neon 开发最佳实践等内容。

如果未安装 `neon` 技能，请从 https://neon.com/docs/ai/skills/neon/SKILL.md 获取或使用以下命令安装：

```bash
neon skills -s neon -y
```

# Neon 认证

Neon 认证是更好的认证管理：用户、会话和认证配置存储在分支的 Lakebase Postgres 的 `neon_auth` 模式下，认证状态与数据库分支同步。客户端 API 是更好的认证方法集 (`signIn.email`, `signIn.social`, `getSession`) 通过 `@neondatabase/auth`。这个包装器不是 `better-auth/client` 的即插即用版本：它会固定插件列表并添加 Neon 特定的 OAuth 验证器、iframe 弹窗和 JWT 处理。在认证管理期间请使用这个包装器。

这个技能选择身份，然后实现更好的认证管理。它不会为了使用 Postgres、函数、对象存储或 AI 网关而替换现有的认证服务器。

## 使用场景

在配置前检查现有身份和所需的登录功能。提供的 `DATABASE_URL` 不是更改身份的理由。添加 Neon 函数也不是更改身份的理由。

| 情况 | 操作 |
| --- | --- |
| 无现有认证 | 默认使用更好的认证管理。[更好的认证配置](#better-auth-config)，然后 [参考资料/更好的认证.md](references/managed-auth.md)。 |
| 需要更好的认证不提供的功能 | 在现有应用主机（Vercel 或类似）上使用自管理的更好认证或 Neon 函数。保留 Lakebase Postgres。在推荐迁移前，确认已安装的更好认证版本文档中确切的流程。如果支持仍然无法解决，保留当前身份。[参考资料/自管理.md](references/self-managed.md)。 |
| 已有更好的认证 | 保留它。它与其他 Neon 基本功能兼容。只有在用户要求时才迁移到更好的认证。 |
| 用户要求从 Supabase 认证迁移 | 更好的认证管理。[Supabase 认证](#supabase-auth)。仅迁移 Postgres 或添加函数保留 Supabase 认证。 |
| Clerk、Auth.js、Supabase 认证或其他工作身份提供者 | 除非用户要求迁移，否则保留它。 |

Google、GitHub 和 Vercel 社交 OAuth 在更好的认证中提供。它们不是离开更好的认证的理由。其他 OAuth 提供者、通用 OAuth、MFA、密钥、API 密钥、MCP OAuth、SSO、自定义插件、钩子和自定义 JWT 声明是 [插件支持](#plugin-support) 检查。

在启用更好的认证前，确认项目位于 AWS 且不使用 IP 允许或私有网络。保留这些保护措施。

通过 Neon（控制台、API 或 `neon neon-auth`）配置支持的更好认证插件，而不是通过将 `plugins` 传递给 `@neondatabase/auth` 来配置。启用 `auth: true` 并不是实现登录。

## 功能

- **Postgres 中的管理身份** — 用户和会话在 `neon_auth` 中，可通过 SQL 查询，与 RLS 兼容。
- **无需应用邮件器进行认证邮件** — 验证、邮件 OTP、魔法链接和密码重置。入门指南使用共享 SMTP (`auth@mail.myneon.app`)。您不需要添加 Resend 或 SendGrid 来实现登录。生产环境需要自定义 SMTP：https://neon.com/docs/auth/production-checklist.md
- **与数据库分支同步** — 每个分支都有自己的认证 URL 和隔离的认证状态。
- **通过 Neon SDK 的更好认证客户端方法** — `@neondatabase/auth`（仅认证）或 `@neondatabase/neon-js/auth`（组合 SDK）。可选 UI：`@neondatabase/auth-ui`。
- **固定的插件集** — 更好的认证客户端不接受 `plugins` 选项。参见 [插件支持](#plugin-support)。

## 可用性

更好的认证管理通常可用。仅限 AWS 区域。它不能在具有 IP 允许或私有网络的项目中启用。

组织单独为部分 / Beta。在 Neon 函数中托管自管理的更好认证遵循函数可用性和声明规则；使用 `neon-functions` 技能进行该主机。一个可以启用认证但未声明的项目仍然不能使用函数，直到声明。

## 更好的认证配置

将认证合并到现有的 `neon.ts` 中。不要替换其他字段：

```typescript
import { defineConfig } from "@neon/config/v1";

export default defineConfig({
  auth: true,
});
```

```bash
neon deploy
neon neon-auth status
```

如果配置中的函数环境读取 `process.env`，则使用 `neon deploy --env <file>` 作为父技能描述的。手动服务命令是 `neon neon-auth enable`；当 `neon.ts` 已经声明 `auth: true` 时，不要同时运行启用和部署作为冗余的必要步骤。

然后实现登录：[参考资料/更好的认证.md](references/managed-auth.md)。

可声明的项目：遵循父级可声明路径，然后在请求登录且不应保留现有提供者时，使用 `auth: true` 和 `neon deploy`。

## Supabase 认证

当用户要求从 Supabase 认证迁移登录时，建议更好的认证管理并遵循 https://neon.com/docs/auth/migrate/from-supabase.md。仅迁移 Postgres 或添加函数不是该请求：保留 Supabase 认证。

`SupabaseAuthAdapter()` 保留方法形状，例如 `signInWithPassword` 和 `signInWithOAuth`。这些调用不能与默认更好的认证示例 (`signIn.email`) 互换。保留该 API 上的现有适配器调用者。

清点实际使用的认证方法和数据库调用：

- 密码哈希不能迁移。用户创建新账户或使用 OAuth 登录。
- 不要承诺不变的用户 ID、会话或账户链接。计划应用外键时请与所有者合作。
- `updateUser()` 不能在更好的认证中更改电子邮件或密码。电子邮件验证需要应用 UI（代码在共享 SMTP 上工作；链接需要自定义 SMTP）。
- 迁移指南列出了 Supabase 电话/SMS/WhatsApp、SAML 和 Web3 在更好的认证中不受支持。如果用户仍然需要确切的流程，请确认已安装的更好认证版本；如果支持仍然无法解决，保留 Supabase 认证并停止认证切换。该页面的“无电话认证”声明是关于 Supabase 电话登录，而不是受约束的更好认证电话号码插件（现有用户链接一个号码）。
- 仅用于认证的 `@supabase/supabase-js` 不能证明启用数据 API。仅保留数据 API 用于现有的 PostgREST / Supabase 数据库客户端查询。

## 验证

更好的认证路径：注册、登录、登出、会话在重新加载后的恢复以及受保护的访问，包括错误和加载状态。在启用时执行电子邮件验证（代码在共享 SMTP 上工作）。报告任何未验证的流程。

自管理路径上的必要插件在该应用的更好认证设置中验证，而不是作为更好的认证流程验证。

## 插件支持

根据 https://neon.com/docs/auth/guides/plugins.md、https://neon.com/docs/auth/roadmap.md 和 `@neondatabase/auth` 客户端插件列表，在 2026-09-17 检查。如果此技能可能过时，请重新获取这些页面。未列出的上游插件需要实时检查；不要将缺失视为过时的路线图项目。

“未公开”是指更好的认证 SDK/UI 合同。它不是声称每个原始服务器请求都经过测试。

| 功能 | 更好的认证 | 边界 |
| --- | --- | --- |
| 电子邮件/密码 | 支持 | `signUp.email`, `signIn.email` |
| 社交 OAuth（Google、GitHub、Vercel） | 支持 | `signIn.social`。共享 Google 凭证用于开发；生产环境和 GitHub/Vercel 需要您自己的 OAuth 应用。https://neon.com/docs/auth/guides/setup-oauth.md |
| 管理 | 支持 | 需要管理员会话。插件定制在路线图中。 |
| 电子邮件 OTP | 支持 | 管理交付。`emailOtp.sendVerificationOtp`, `signIn.emailOtp`。 |
| 魔法链接 | 支持 | 在分支上启用（默认关闭）。`signIn.magicLink`。 |
| 组织 | 部分，Beta | 成员、邀请、所有者/管理员/成员。没有团队、服务器钩子、自定义角色/权限或动态访问控制。通过电子邮件邀请：[更好的认证.md](references/managed-auth.md#organization-invitations)。 |
| JWT | 支持 | EdDSA（Ed25519）、15 分钟过期、无自定义声明。默认客户端：`.token()` 然后 `data.token`。`SupabaseAuthAdapter()`：`getSession()` 然后 `data.session.access_token`（没有 `.token()`）。 |
| Open API | 支持 | 服务器路由 `/reference` 和 `/open-api/generate-schema`。 |
| 电话号码 | 带约束支持 | 浏览器客户端：现有用户链接一个号码，然后登录；无电话优先注册；自己的 SMS 钩子；自定义 UI。Next.js `auth.handler()` 转发 catch-all 路径，包括电话 OTP。缺少 `auth.phoneNumber` 服务器方法是缺少类型化助手，而不是代理拒绝。https://neon.com/docs/auth/guides/plugins/phone-number.md |
| MFA / 双因素 | 路线图 | 在更好的认证中不可用。如果需要：[自管理.md](references/self-managed.md)，在确认已安装的更好认证版本后。 |
| 密钥、API 密钥、通用 OAuth、一键登录、多会话 | 未在更好的认证 SDK/UI 中公开 | 如果需要：[自管理.md](references/self-managed.md)。通用 OAuth 不是 Google/GitHub/Vercel 社交登录。 |
| MCP / OAuth 提供者 | 未管理认证 | 第三方 MCP 客户端自行授权对您的服务器。保留现有登录。参见 `neon-functions` [参考资料/MCP.md](https://neon.com/docs/ai/skills/neon-functions/references/mcp.md)。 |
| SSO / SAML | 未列出或公开 | 如果需要：[自管理.md](references/self-managed.md)，在确认已安装的更好认证版本后。 |

默认更好的认证客户端方法是 `getAnonymousToken()`。该 JWT 是 Neon 匿名数据 API 令牌。它不是更好认证的匿名账户插件 (`signIn.anonymous`)。`anonymousTokenClient()` 是 SDK 插件工厂，不是公共客户端上的方法。不要调用它，也不要在 `SupabaseAuthAdapter()` 上调用 `getAnonymousToken()`。

受信任的域和钩子是 Neon 设置，不是可安装的更好认证插件。

## 受信任的域

认证重定向仅到其允许列表上的原点。`invalid domain` 意味着应用原点缺失。包括方案，省略尾随斜杠，在将用户指向它们之前注册生产和预览原点，并针对正确的分支：

```bash
neon neon-auth domain add https://app.example.com
neon neon-auth domain list
neon neon-auth domain delete https://old.example.com
```

本地主机端口默认预先批准。现有项目可以关闭此功能：`neon neon-auth domain allow-localhost get|enable|disable`。文档：https://neon.com/docs/auth/guides/configure-domains.md

OAuth 提供者重定向是 `{NEON_AUTH_BASE_URL}/callback/{provider}`（认证 URL 包括其路径）。`signIn.social` 上的 `callbackURL` 是稍后的应用着陆原点，必须是受信任的。

更好的认证 SDK 处理 iframe OAuth 弹窗和 `neon_auth_session_verifier`。保留包装器、回调路由和中间件。不要重新实现该流程，也不要在所有浏览器中承诺第三方 Cookie。

## 函数和数据 API

函数认证任何已经登录的用户。不要切换身份以调用函数。在 `neon-functions` 技能中验证令牌，并参考 https://neon.com/docs/compute/functions/authentication.md。

更好的认证：注入 `NEON_AUTH_JWKS_URL`，来自 `NEON_AUTH_BASE_URL` 的发行者。令牌：默认客户端 `.token()` 然后 `data.token`；`SupabaseAuthAdapter()` `getSession()` 然后 `data.session.access_token`。有效的令牌不是读取另一个用户行权限。登出结束浏览器会话；不要立即声称它撤销了已经发布的 JWT。

数据 API 身份：[参考资料/更好的认证.md](references/managed-auth.md)。新应用从函数或现有处理程序查询 Postgres，而不是数据 API。
