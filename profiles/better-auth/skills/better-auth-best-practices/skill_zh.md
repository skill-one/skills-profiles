# Better Auth 集成指南

## 文档版本

使用与项目安装版本匹配的 Better Auth 文档。维护版本线的 API 和插件名称可能有所不同。

1. 优先使用用户明确指定的版本。
2. 否则，检查锁文件中解析出的 `better-auth` 版本；若无锁文件，则回退到包清单文件。
3. 当可用 Better Auth MCP 时，使用 `/llms.txt` 调用 `get_doc` 来将该包版本解析为文档标识符。将标识符传递给每次 `search_docs` 调用，并将结果路径原样传递给 `get_doc`。
4. 若无 MCP，从 [better-auth.com/llms.txt](https://better-auth.com/llms.txt) 开始，并跟随匹配的版本索引。
5. 仅在无法确定项目版本，或用户明确要求了解最新发布版本或升级时，使用最新文档。

在规划升级时，将当前已安装版本的指引与目标版本的指引分开。

---

## 设置工作流

1. 安装：`npm install better-auth`
2. 设置环境变量：`BETTER_AUTH_SECRET` 和 `BETTER_AUTH_URL`
3. 创建包含数据库和配置的 `auth.ts`
4. 为您的框架创建路由处理器
5. 运行迁移：
   - **内置适配器：** `npx auth@latest migrate`
   - **Drizzle：** `npx auth@latest generate --output src/db/auth-schema.ts`，然后 `npx drizzle-kit push`（开发环境），或 `npx drizzle-kit generate && npx drizzle-kit migrate`（生产环境）
   - **Prisma：** `npx auth@latest generate --output prisma/schema.prisma`，然后 `npx prisma migrate dev`
6. 验证：调用 `GET /api/auth/ok` — 应返回 `{ status: "ok" }`

---

## 快速参考

### 环境变量
- `BETTER_AUTH_SECRET` - 加密密钥（最少 32 个字符）。生成：`openssl rand -base64 32`
- `BETTER_AUTH_URL` - 基础 URL（例如 `https://example.com`）

仅当未设置环境变量时，才在配置中定义 `baseURL`/`secret`。

### 文件位置
CLI 在以下位置查找 `auth.ts`：`./`、`./lib`、`./utils` 或 `./src` 下。使用 `--config` 指定自定义路径。

### CLI 命令
- `npx auth@latest migrate` - 应用模式（内置适配器）
- `npx auth@latest generate` - 为 Prisma/Drizzle 生成模式
- `npx auth@latest mcp --cursor` - 将 MCP 添加到 AI 工具

**在添加或修改插件后重新运行。**

---

## 核心配置选项

| Option | Notes |
|--------|-------|
| `appName` | 可选显示名称 |
| `baseURL` | 仅当 `BETTER_AUTH_URL` 未设置时使用 |
| `basePath` | 默认 `/api/auth`。根路径设置为 `/`。 |
| `secret` | 仅当 `BETTER_AUTH_SECRET` 未设置时使用 |
| `database` | 大多数功能必需。详见适配器文档。 |
| `secondaryStorage` | Redis/KV，用于会话与限流 |
| `emailAndPassword` | 通过 `{ enabled: true }` 启用 |
| `socialProviders` | `{ google: { clientId, clientSecret }, ... }` |
| `plugins` | 插件数组 |
| `trustedOrigins` | CSRF 白名单 |

---

## 数据库

**直接连接：** 传入 `pg.Pool`、`mysql2` 连接池、`better-sqlite3` 或 `bun:sqlite` 实例。对于 Postgres，还支持 `postgres`（postgres.js）和 `@neondatabase/serverless`。

**ORM 适配器：** 从 `better-auth/adapters/drizzle`、`better-auth/adapters/prisma`、`better-auth/adapters/mongodb` 导入。

**Drizzle provider 值：** `"pg"`（PostgreSQL）、`"mysql"`（MySQL）、`"sqlite"`（SQLite）。必须与使用的驱动匹配。

**重要：** Better Auth 使用适配器模型名称，而非底层表名。如果 Prisma 模型 `User` 映射到表 `users`，则使用 `modelName: "user"`（Prisma 引用），而非 `"users"`。

---

## 会话管理

**存储优先级：**
1. 若定义了 `secondaryStorage` → 会话存储在该处（而非数据库）
2. 设置 `session.storeSessionInDatabase: true` 以同时持久化到数据库
3. 无数据库且使用 `cookieCache` → 完全无状态模式

**Cookie 缓存策略：**
- `compact`（默认） - Base64url + HMAC。最小。
- `jwt` - 标准 JWT。可读取但已签名。
- `jwe` - 加密。最高安全性。

**关键选项：** `session.expiresIn`（默认 7 天）、`session.updateAge`（刷新间隔）、`session.cookieCache.maxAge`、`session.cookieCache.version`（修改以失效所有会话）。

---

## 用户与账户配置

**用户：** `user.modelName`、`user.fields`（列映射）、`user.additionalFields`、`user.changeEmail.enabled`（默认禁用）、`user.deleteUser.enabled`（默认禁用）。

**账户：** `account.modelName`、`account.accountLinking.enabled`、`account.storeAccountCookie`（用于无状态 OAuth）。

**注册所需：** `email` 和 `name` 字段。

---

## 邮件流程

- `emailVerification.sendVerificationEmail` - 必须定义才能工作
- `emailVerification.sendOnSignUp` / `sendOnSignIn` - 自动发送触发
- `emailAndPassword.sendResetPassword` - 密码重置邮件处理器

---

## 安全

**在 `advanced` 中：**
- `useSecureCookies` - 强制使用 HTTPS Cookie
- `disableCSRFCheck` - ⚠️ 安全风险
- `disableOriginCheck` - ⚠️ 安全风险
- `crossSubDomainCookies.enabled` - 跨子域名共享 Cookie
- `ipAddress.ipAddressHeaders` - 代理的自定义 IP 请求头
- `database.generateId` - 自定义 ID 生成，或 `"serial"`/`"uuid"`/`false`

**限流：** `rateLimit.enabled`、`rateLimit.window`、`rateLimit.max`、`rateLimit.storage`（"memory" | "database" | "secondary-storage"）。

---

## Hooks

**端点 Hook：** `hooks.before` / `hooks.after` - 包含 `{ matcher, handler }` 的数组。使用 `createAuthMiddleware`。访问 `ctx.path`、`ctx.context.returned`（之后）、`ctx.context.session`。

**数据库 Hook：** `databaseHooks.user.create.before/after`，`session` 和 `account` 同理。可用于添加默认值或创建后操作。

**Hook 上下文（`ctx.context`）：** `session`、`secret`、`authCookies`、`password.hash()`/`verify()`、`adapter`、`internalAdapter`、`generateId()`、`tables`、`baseURL`。

---

## 插件

**为使用 tree-shaking 从专用路径导入：**
```
import { twoFactor } from "better-auth/plugins/two-factor"
```
而非 `from "better-auth/plugins"`。

**常用插件：** `twoFactor`、`organization`、`passkey`、`magicLink`、`emailOtp`、`username`、`phoneNumber`、`admin`、`apiKey`、`bearer`、`jwt`、`multiSession`、`sso`、`oauthProvider`、`oidcProvider`、`openAPI`、`genericOAuth`。

客户端插件放入 `createAuthClient({ plugins: [...] })` 中。

---

## 客户端

从以下导入：`better-auth/client`（原生）、`better-auth/react`、`better-auth/vue`、`better-auth/svelte`、`better-auth/solid`。

**关键方法：** `signUp.email()`、`signIn.email()`、`signIn.social()`、`signOut()`、`useSession()`、`getSession()`、`revokeSession()`、`revokeSessions()`。

---

## 类型安全

推断类型：`typeof auth.$Infer.Session`、`typeof auth.$Infer.Session.user`。

对于独立的客户端/服务端项目：`createAuthClient(typeof auth())`。

---

## 常见注意事项

1. **模型与表名** - 配置使用 ORM 模型名称，而非数据库表名
2. **插件模式** - 添加插件后重新运行 CLI
3. **二级存储** - 会话默认存储在该处，而非数据库
4. **Cookie 缓存** - 自定义会话字段不会被缓存，始终重新获取
5. **无状态模式** - 无数据库 = 会话仅存储在 Cookie 中，缓存过期时退出登录
6. **更换邮箱流程** - 先发送至当前邮箱，再发送至新邮箱
7. **Drizzle：未初始化 db** - `drizzleAdapter(db, ...)` 需要来自 `drizzle()` 的 `db` 实例。参见 `create-auth` 技能以获取设置示例（node-postgres、postgres.js、Neon）。
8. **Drizzle：缺少 drizzle.config.ts** - `drizzle-kit` 命令需要 `drizzle.config.ts`，该文件指向生成的模式文件并包含数据库凭据。

---

## 资源

- [文档](https://better-auth.com/docs)
- [选项参考](https://better-auth.com/docs/reference/options)
- [LLMs.txt](https://better-auth.com/llms.txt)
- [GitHub](https://github.com/better-auth/better-auth)
- [初始化选项来源](https://github.com/better-auth/better-auth/blob/main/packages/core/src/types/init-options.ts)
