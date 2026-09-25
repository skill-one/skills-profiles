# 更好的身份验证集成指南

## 文档版本

使用与项目中安装的 Better Auth 版本匹配的文档。API 和插件名称可能因维护版本线而有所不同。

1. 优先使用用户显式命名的版本。
2. 否则，检查 lockfile 中的解析 `better-auth` 版本，如果没有 lockfile 则回退到包清单。
3. 当 Better Auth MCP 可用时，调用 `get_doc` 并传入 `/llms.txt` 来将包版本解析为文档标识符。将标识符传递给每个 `search_docs` 调用，并将结果路径原封不动地传递给 `get_doc`。
4. 没有 MCP 时，从 [better-auth.com/llms.txt](https://better-auth.com/llms.txt) 开始，并遵循匹配的版本索引。
5. 仅在无法确定项目版本或用户明确询问最新版本或升级时使用最新文档。

在计划升级时，将当前安装版本的指导与目标版本的指导分开。

---

## 设置流程

1. 安装：`npm install better-auth`
2. 设置环境变量：`BETTER_AUTH_SECRET` 和 `BETTER_AUTH_URL`
3. 创建 `auth.ts` 并包含数据库 + 配置
4. 为您的框架创建路由处理器
5. 运行迁移：
   - **内置适配器**：`npx auth@latest migrate`
   - **Drizzle**：`npx auth@latest generate --output src/db/auth-schema.ts` 然后 `npx drizzle-kit push`（开发）或 `npx drizzle-kit generate && npx drizzle-kit migrate`（生产）
   - **Prisma**：`npx auth@latest generate --output prisma/schema.prisma` 然后 `npx prisma migrate dev`
6. 验证：调用 `GET /api/auth/ok` — 应返回 `{ status: "ok" }`

---

## 快速参考

### 环境变量
- `BETTER_AUTH_SECRET` - 加密密钥（最小 32 个字符）。生成：`openssl rand -base64 32`
- `BETTER_AUTH_URL` - 基础 URL（例如，`https://example.com`）

仅在环境变量未设置时，在配置中定义 `baseURL`/`secret`。

### 文件位置
CLI 在以下位置查找 `auth.ts`：`./`、`./lib`、`./utils` 或在 `./src` 下。使用 `--config` 指定自定义路径。

### CLI 命令
- `npx auth@latest migrate` - 应用模式（内置适配器）
- `npx auth@latest generate` - 为 Prisma/Drizzle 生成模式
- `npx auth@latest mcp --cursor` - 向 AI 工具添加 MCP

**添加/更改插件后重新运行。**

---

## 核心配置选项

| 选项 | 备注 |
|------|------|
| `appName` | 可选的显示名称 |
| `baseURL` | 仅当 `BETTER_AUTH_URL` 未设置时 |
| `basePath` | 默认 `/api/auth`。设置为 `/` 表示根路径。 |
| `secret` | 仅当 `BETTER_AUTH_SECRET` 未设置时 |
| `database` | 大多数功能所需。查看适配器文档。 |
| `secondaryStorage` | 用于会话和速率限制的 Redis/KV |
| `emailAndPassword` | `{ enabled: true }` 以启用 |
| `socialProviders` | `{ google: { clientId, clientSecret }, ... }` |
| `plugins` | 插件数组 |
| `trustedOrigins` | CSRF 白名单 |

---

## 数据库

**直接连接**：传递 `pg.Pool`、`mysql2` 连接池、`better-sqlite3` 或 `bun:sqlite` 实例。对于 Postgres，还支持 `postgres`（postgres.js）和 `@neondatabase/serverless`。

**ORM 适配器**：从 `better-auth/adapters/drizzle`、`better-auth/adapters/prisma`、`better-auth/adapters/mongodb` 导入。

**Drizzle 提供者值**：`"pg"`（PostgreSQL）、`"mysql"`（MySQL）、`"sqlite"`（SQLite）。必须与使用的驱动程序匹配。

**关键**：Better Auth 使用适配器模型名称，而不是底层表名称。如果 Prisma 模型是 `User` 映射到表 `users`，请使用 `modelName: "user"`（Prisma 引用），而不是 `"users"`。

---

## 会话管理

**存储优先级**：
1. 如果定义了 `secondaryStorage` → 会话存储在那里（不存储在数据库中）
2. 设置 `session.storeSessionInDatabase: true` 以同时持久化到数据库
3. 无数据库 + `cookieCache` → 完全无状态模式

**Cookie 缓存策略**：
- `compact`（默认）- Base64url + HMAC。最小。
- `jwt` - 标准 JWT。可读但已签名。
- `jwe` - 加密的。最高安全性。

**关键选项**：`session.expiresIn`（默认 7 天）、`session.updateAge`（刷新间隔）、`session.cookieCache.maxAge`、`session.cookieCache.version`（更改以使所有会话失效）。

---

## 用户和账户配置

**用户**：`user.modelName`、`user.fields`（列映射）、`user.additionalFields`、`user.changeEmail.enabled`（默认禁用）、`user.deleteUser.enabled`（默认禁用）。

**账户**：`account.modelName`、`account.accountLinking.enabled`、`account.storeAccountCookie`（用于无状态 OAuth）。

**注册所需**：`email` 和 `name` 字段。

---

## 邮件流程

- `emailVerification.sendVerificationEmail` - 必须定义以使验证工作
- `emailVerification.sendOnSignUp` / `sendOnSignIn` - 自动发送触发
- `emailAndPassword.sendResetPassword` - 密码重置邮件处理器

---

## 安全

**在 `advanced` 中**：
- `useSecureCookies` - 强制 HTTPS cookie
- `disableCSRFCheck` - ⚠️ 安全风险
- `disableOriginCheck` - ⚠️ 安全风险  
- `crossSubDomainCookies.enabled` - 跨子域共享 cookie
- `ipAddress.ipAddressHeaders` - 代理的自定义 IP 头
- `database.generateId` - 自定义 ID 生成或 `"serial"`/`"uuid"`/`false`

**速率限制**：`rateLimit.enabled`、`rateLimit.window`、`rateLimit.max`、`rateLimit.storage`（"memory" | "database" | "secondary-storage"）。

---

## 钩子

**端点钩子**：`hooks.before` / `hooks.after` - `{ matcher, handler }` 数组。使用 `createAuthMiddleware`。访问 `ctx.path`、`ctx.context.returned`（之后）、`ctx.context.session`。

**数据库钩子**：`databaseHooks.user.create.before/after`，同样适用于 `session`、`account`。用于添加默认值或创建后操作。

**钩子上下文 (`ctx.context`)**：`session`、`secret`、`authCookies`、`password.hash()`/`verify()`、`adapter`、`internalAdapter`、`generateId()`、`tables`、`baseURL`。

---

## 插件

**从专用路径导入以进行树摇动**：
```
import { twoFactor } from "better-auth/plugins/two-factor"
```
不是 `from "better-auth/plugins"`。

**流行插件**：`twoFactor`、`organization`、`passkey`、`magicLink`、`emailOtp`、`username`、`phoneNumber`、`admin`、`apiKey`、`bearer`、`jwt`、`multiSession`、`sso`、`oauthProvider`、`oidcProvider`、`openAPI`、`genericOAuth`。

客户端插件放在 `createAuthClient({ plugins: [...] })` 中。

---

## 客户端

从以下路径导入：`better-auth/client`（原味）、`better-auth/react`、`better-auth/vue`、`better-auth/svelte`、`better-auth/solid`。

关键方法：`signUp.email()`、`signIn.email()`、`signIn.social()`、`signOut()`、`useSession()`、`getSession()`、`revokeSession()`、`revokeSessions()`。

---

## 类型安全

推断类型：`typeof auth.$Infer.Session`、`typeof auth.$Infer.Session.user`。

对于分离的客户端/服务器项目：`createAuthClient<typeof auth>()`。

---

## 常见陷阱

1. **模型与表名** - 配置使用 ORM 模型名称，不是数据库表名称
2. **插件模式** - 添加插件后重新运行 CLI
3. **二级存储** - 会话默认存储在那里，不是数据库
4. **Cookie 缓存** - 自定义会话字段不缓存，总是重新获取
5. **无状态模式** - 无数据库 = 仅 cookie 中的会话，缓存过期时注销
6. **更改邮件流程** - 首先发送到当前邮件，然后发送到新邮件
7. **Drizzle：数据库未初始化** - `drizzleAdapter(db, ...)` 需要 `drizzle()` 提供的 `db` 实例。查看 `create-auth` 技能以获取设置示例（node-postgres、postgres.js、Neon）。
8. **Drizzle：缺少 drizzle.config.ts** - `drizzle-kit` 命令需要一个指向生成的模式文件和数据库凭证的 `drizzle.config.ts`。

---

## 资源

- [文档](https://better-auth.com/docs)
- [选项参考](https://better-auth.com/docs/reference/options)
- [LLMs.txt](https://better-auth.com/llms.txt)
- [GitHub](https://github.com/better-auth/better-auth)
- [初始化选项源](https://github.com/better-auth/better-auth/blob/main/packages/core/src/types/init-options.ts)
