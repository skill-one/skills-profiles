# 创建认证技能

使用 Better Auth 为 TypeScript/JavaScript 应用添加认证的指南。

**有关代码示例和语法，请参阅 [better-auth.com/docs](https://better-auth.com/docs)。**

---

## 第一阶段：规划（实施前必须）

在编写任何代码之前，通过扫描项目并向用户提出结构化问题来收集需求。这确保了实施符合他们的需求。

### 第一步：扫描项目

分析代码库以自动检测：
- **框架** — 查找 `next.config`、`svelte.config`、`nuxt.config`、`astro.config`、`vite.config` 或 Express/Hono 入口文件。
- **数据库/ORM** — 查找 `prisma/schema.prisma`、`drizzle.config.ts`、`package.json` 依赖 (`pg`、`postgres`、`@neondatabase/serverless`、`mysql2`、`better-sqlite3`、`mongoose`、`mongodb`)。如果存在 `drizzle.config.ts`，请读取其 `dialect` 字段以确定数据库类型（例如，`"postgresql"` → Drizzle + Postgres）。还检查安装了哪个 Drizzle 驱动程序（`drizzle-orm/node-postgres` → `pg`、`drizzle-orm/postgres-js` → `postgres`、`drizzle-orm/neon-http` → Neon）。
- **现有认证** — 在 `package.json` 或导入中查找现有认证库（`next-auth`、`lucia`、`clerk`、`supabase/auth`、`firebase/auth`）。
- **包管理器** — 检查 `pnpm-lock.yaml`、`yarn.lock`、`bun.lockb` 或 `package-lock.json`。

使用您发现的内容预填默认值，并跳过您可以已经自信回答的问题。

### 第二步：提出规划问题

使用 `AskQuestion` 工具在单个调用中向用户提出**所有适用的问题**。跳过您从扫描中已经有一个自信答案的问题。将它们分组在标题下，例如“认证设置规划”。

**要提出的问题：**

1. **项目类型**（如果已检测则跳过）
   - 提示：“这是什么类型的项目？”
   - 选项：从零开始的新项目 | 向现有项目添加认证 | 从另一个认证库迁移

2. **框架**（如果已检测则跳过）
   - 提示：“您使用哪个框架？”
   - 选项：Next.js (App Router) | Next.js (Pages Router) | SvelteKit | Nuxt | Astro | Express | Hono | SolidStart | 其他

3. **数据库 & ORM**（如果已检测则跳过）
   - 提示：“您将使用哪种数据库设置？”
   - 选项：PostgreSQL (Prisma) | PostgreSQL (Drizzle) | PostgreSQL (pg 驱动程序) | MySQL (Prisma) | MySQL (Drizzle) | MySQL (mysql2 驱动程序) | SQLite (Prisma) | SQLite (Drizzle) | SQLite (better-sqlite3 驱动程序) | MongoDB (Mongoose) | MongoDB (原生驱动程序)

4. **认证方法**（始终询问，允许多选）
   - 提示：“您需要哪些登录方法？”
   - 选项：电子邮件和密码 | 社交 OAuth（Google、GitHub 等） | 魔法链接（无密码电子邮件） | Passkey（WebAuthn） | 电话号码
   - `allow_multiple: true`

5. **社交提供者**（仅当他们在上面选择了社交 OAuth 时——在后续调用中询问）
   - 提示：“您需要哪些社交提供者？”
   - 选项：Google | GitHub | Apple | Microsoft | Discord | Twitter/X
   - `allow_multiple: true`

6. **电子邮件验证**（仅当上面选择了电子邮件和密码时——在后续调用中询问）
   - 提示：“您是否需要要求电子邮件验证？”
   - 选项：是 | 否

7. **电子邮件提供者**（仅当电子邮件验证为是，或如果功能中选择了密码重置——在后续调用中询问）
   - 提示：“您希望如何发送电子邮件？”
   - 选项：Resend | 暂时模拟（console.log）

8. **功能 & 插件**（始终询问，允许多选）
   - 提示：“您需要哪些附加功能？”
   - 选项：双因素认证 (2FA) | 组织/团队 | 管理员仪表板 | API 带宽令牌 | 密码重置 | 以上都不是
   - `allow_multiple: true`

9. **认证页面**（始终询问，允许多选——根据先前的答案预选）
   - 提示：“您需要哪些认证页面？”
   - 选项因先前的答案而异：
     - 始终可用：登录 | 注册
     - 如果选择了电子邮件和密码：忘记密码 | 重置密码
     - 如果启用了电子邮件验证：电子邮件验证
   - `allow_multiple: true`

10. **认证 UI 风格**（始终询问）
    - 提示：“您希望认证页面的风格是什么？选择一个或描述您自己的。”
    - 选项：简约干净 | 带背景的中心卡片 | 分割布局（表单 + 英雄图片） | 漂浮/玻璃形态 | 其他（我将描述）

### 第三步：总结计划

收集答案后，以 Markdown 清单的形式呈现简洁的实施计划。示例：

```
## 认证实施计划

- **框架**：Next.js (App Router)
- **数据库**：通过 Prisma 的 PostgreSQL
- **认证方法**：电子邮件/密码、Google OAuth、GitHub OAuth
- **插件**：2FA、组织、电子邮件验证
- **UI**：自定义表单

### 步骤
1. 安装 `better-auth` 和 `@better-auth/cli`
2. 创建 `lib/auth.ts` 并配置服务器
3. 创建 `lib/auth-client.ts` 并配置 React 客户端
4. 在 `app/api/auth/[...all]/route.ts` 设置路由处理器
5. 配置 Prisma 适配器并生成模式
6. 添加 Google 和 GitHub OAuth 提供者
7. 启用 `twoFactor` 和 `organization` 插件
8. 设置电子邮件验证处理器
9. 运行迁移
10. 创建登录/注册页面
```

在继续第二阶段之前，请要求用户确认该计划。

---

## 第二阶段：实施

只有在用户确认了第一阶段的计划后，才继续此处。

按照以下决策树进行操作，该决策树由上面收集的答案指导。

```
这是一个新/空项目吗？
├─ 是 → 新项目设置
│   1. 安装 better-auth (+ 根据计划配置的包)
│   2. 创建 auth.ts 并配置所有计划的设置
│   3. 创建 auth-client.ts 并配置框架客户端
│   4. 设置路由处理器
│   5. 设置环境变量
│   6. 运行 CLI migrate/generate
│   7. 添加计划中的插件
│   8. 创建认证 UI 页面
│
├─ 迁移 → 从现有认证迁移
│   1. 审计当前认证的差距
│   2. 规划增量迁移
│   3. 安装 better-auth 并与现有认证一起使用
│   4. 迁移路由，然后会话逻辑，然后 UI
│   5. 移除旧的认证库
│   6. 查看文档中的迁移指南
│
└─ 添加 → 向现有项目添加认证
    1. 分析项目结构
    2. 安装 better-auth
    3. 创建与计划匹配的认证配置
    4. 添加路由处理器
    5. 运行模式迁移
    6. 集成到现有页面
    7. 添加计划中的插件和功能
```

在实施结束时，指导用户彻底了解剩余的下一步（例如，设置 OAuth 应用凭据、部署环境变量、测试流程）。

---

## 安装

**核心**：`npm install better-auth`

**按需配置的包**：
| 包 | 用途 |
|---------|----------|
| `@better-auth/passkey` | WebAuthn/Passkey 认证 |
| `@better-auth/sso` | SAML/OIDC 企业 SSO |
| `@better-auth/stripe` | Stripe 支付 |
| `@better-auth/scim` | SCIM 用户配置 |
| `@better-auth/expo` | React Native/Expo |

---

## 环境变量

```env
BETTER_AUTH_SECRET=<32+ 字符, 使用 openssl rand -base64 32 生成>
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=<您的数据库连接字符串>
```

按需添加 OAuth 密钥：`GITHUB_CLIENT_ID`、`GITHUB_CLIENT_SECRET`、`GOOGLE_CLIENT_ID` 等。

---

## 服务器配置（auth.ts）

**位置**：`lib/auth.ts` 或 `src/lib/auth.ts`

**最小配置需求**：
- `database` - 连接或适配器
- `emailAndPassword: { enabled: true }` - 用于电子邮件/密码认证

**标准配置添加**：
- `socialProviders` - OAuth 提供者（google、github 等）
- `emailVerification.sendVerificationEmail` - 电子邮件验证处理器
- `emailAndPassword.sendResetPassword` - 密码重置处理器

**完整配置添加**：
- `plugins` - 功能插件数组
- `session` - 过期、cookie 缓存设置
- `account.accountLinking` - 多提供者链接
- `rateLimit` - 速率限制配置

**导出类型**：`export type Session = typeof auth.$Infer.Session`

---

## 客户端配置（auth-client.ts）

**按框架导入**：
| 框架 | 导入 |
|-----------|--------|
| React/Next.js | `better-auth/react` |
| Vue | `better-auth/vue` |
| Svelte | `better-auth/svelte` |
| Solid | `better-auth/solid` |
| 纯 JavaScript | `better-auth/client` |

**客户端插件** 放在 `createAuthClient({ plugins: [...] })` 中。

**常见导出**：`signIn`、`signUp`、`signOut`、`useSession`、`getSession`

---

## 路由处理器设置

| 框架 | 文件 | 处理器 |
|-----------|------|---------|
| Next.js App Router | `app/api/auth/[...all]/route.ts` | `toNextJsHandler(auth)` → 导出 `{ GET, POST }` |
| Next.js Pages | `pages/api/auth/[...all].ts` | `toNextJsHandler(auth)` → 默认导出 |
| Express | 任何文件 | `app.all("/api/auth/*", toNodeHandler(auth))` |
| SvelteKit | `src/hooks.server.ts` | `svelteKitHandler(auth)` |
| SolidStart | 路由文件 | `solidStartHandler(auth)` |
| Hono | 路由文件 | `auth.handler(c.req.raw)` |

**Next.js 服务器组件**：在认证配置中添加 `nextCookies()` 插件。

---

## 数据库迁移

| 适配器 | 命令 |
|---------|---------|
| 内置 Kysely | `npx @better-auth/cli@latest migrate` (直接应用) |
| Prisma | `npx @better-auth/cli@latest generate --output prisma/schema.prisma` 然后 `npx prisma migrate dev` |
| Drizzle (开发) | `npx @better-auth/cli@latest generate --output src/db/auth-schema.ts` 然后 `npx drizzle-kit push` |
| Drizzle (生产) | `npx @better-auth/cli@latest generate --output src/db/auth-schema.ts` 然后 `npx drizzle-kit generate` 然后 `npx drizzle-kit migrate` |

> **注意**：`drizzle-kit push` 跳过迁移文件，仅适用于开发。在生产中使用 `drizzle-kit generate` + `drizzle-kit migrate`。

**添加插件后重新运行。**

---

## 数据库适配器

| 数据库 | 设置 |
|----------|-------|
| SQLite | 直接传递 `better-sqlite3` 或 `bun:sqlite` 实例 |
| PostgreSQL | 直接传递 `pg.Pool` 实例 |
| MySQL | 直接传递 `mysql2` 池 |
| Prisma | `prismaAdapter(prisma, { provider: "postgresql" })` 从 `better-auth/adapters/prisma` |
| Drizzle (pg) | `drizzleAdapter(db, { provider: "pg" })` 从 `better-auth/adapters/drizzle` |
| Drizzle (mysql) | `drizzleAdapter(db, { provider: "mysql" })` 从 `better-auth/adapters/drizzle` |
| Drizzle (sqlite) | `drizzleAdapter(db, { provider: "sqlite" })` 从 `better-auth/adapters/drizzle` |
| MongoDB | `mongodbAdapter(db)` 从 `better-auth/adapters/mongodb` |

### Drizzle + PostgreSQL 设置

在使用 `drizzleAdapter` 之前，初始化 `db` 实例：

```ts
// 选项 1: node-postgres (pg)
import { drizzle } from "drizzle-orm/node-postgres"
import { Pool } from "pg"
import * as schema from "./auth-schema"

const pool = new Pool({ connectionString: process.env.DATABASE_URL })
export const db = drizzle(pool, { schema })
```

```ts
// 选项 2: postgres.js
import { drizzle } from "drizzle-orm/postgres-js"
import postgres from "postgres"
import * as schema from "./auth-schema"

const client = postgres(process.env.DATABASE_URL!)
export const db = drizzle(client, { schema })
```

```ts
// 选项 3: Neon serverless
import { drizzle } from "drizzle-orm/neon-http"
import { neon } from "@neondatabase/serverless"
import * as schema from "./auth-schema"

const sql = neon(process.env.DATABASE_URL!)
export const db = drizzle(sql, { schema })
```

然后传递给 Better Auth：

```ts
import { betterAuth } from "better-auth"
import { drizzleAdapter } from "better-auth/adapters/drizzle"
import { db } from "./db"

export const auth = betterAuth({
  database: drizzleAdapter(db, { provider: "pg" }),
  // ...
})
```

### Drizzle 配置 (`drizzle.config.ts`)

对于 `drizzle-kit` 命令查找模式是必需的：

```ts
import { defineConfig } from "drizzle-kit"

export default defineConfig({
  schema: "./src/db/auth-schema.ts",
  out: "./drizzle",
  dialect: "postgresql",
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
})
```

---

## 常见插件

| 插件 | 服务器导入 | 客户端导入 | 目的 |
|--------|---------------|---------------|---------|
| `twoFactor` | `better-auth/plugins` | `twoFactorClient` | TOTP/OTP 的 2FA |
| `organization` | `better-auth/plugins` | `organizationClient` | 团队/组织 |
| `admin` | `better-auth/plugins` | `adminClient` | 用户管理 |
| `bearer` | `better-auth/plugins` | - | API 令牌认证 |
| `openAPI` | `better-auth/plugins` | - | API 文档 |
| `passkey` | `@better-auth/passkey` | `passkeyClient` | WebAuthn |
| `sso` | `@better-auth/sso` | - | 企业 SSO |

**插件模式**：服务器插件 + 客户端插件 + 运行迁移。

---

## 认证 UI 实现

**登录流程**：
1. `signIn.email({ email, password })` 或 `signIn.social({ provider, callbackURL })`
2. 在响应中处理 `error`
3. 成功时重定向

**会话检查（客户端）**：`useSession()` 钩子返回 `{ data: session, isPending }`

**会话检查（服务器）**：`auth.api.getSession({ headers: await headers() })`

**受保护路由**：检查会话，如果为空则重定向到 `/sign-in`。

---

## 安全检查清单

- [ ] `BETTER_AUTH_SECRET` 设置（32+ 字符）
- [ ] 生产中 `advanced.useSecureCookies: true`
- [ ] 配置 `trustedOrigins`
- [ ] 启用速率限制
- [ ] 启用电子邮件验证
- [ ] 实现密码重置
- [ ] 敏感应用的 2FA
- [ ] CSRF 保护未禁用
- [ ] 审查 `account.accountLinking`

---

## 故障排除

| 问题 | 解决方法 |
|-------|-----|
| “Secret not set” | 添加 `BETTER_AUTH_SECRET` 环境变量 |
| “Invalid Origin” | 将域名添加到 `trustedOrigins` |
| Cookies 未设置 | 检查 `baseURL` 匹配域名；在生产中启用安全 Cookies |
| OAuth 回调错误 | 在提供者控制台中验证重定向 URI |
| 添加插件后的类型错误 | 重新运行 CLI generate/migrate |

---

## 资源

- [文档](https://better-auth.com/docs)
- [示例](https://github.com/better-auth/examples)
- [插件](https://better-auth.com/docs/concepts/plugins)
- [CLI](https://better-auth.com/docs/concepts/cli)
- [迁移指南](https://better-auth.com/docs/guides)
