# 添加 Clerk

> **版本**: 查看在 `package.json` 中的 SDK 版本 — 参考在 `clerk` 技能中的版本表。核心 2 的差异在 `> **Core 2 ONLY (skip if current SDK):**` 提示中内联注明。

此技能通过遵循官方快速入门文档来设置 Clerk 以进行身份验证。对于代理，`clerk` CLI 处理了大部分端到端工作 — 见下一节。

## 代理优先：通过 CLI 提供服务

`clerk` CLI 替换了大多数控制面板的点击操作。三种场景几乎涵盖了所有情况：

### 场景 A — 新项目，新 Clerk 应用

```bash
clerk init --framework <next|react|vue|nuxt|astro|react-router|tanstack-react-start|expressjs|fastify|expo> -y
```

`clerk init` 安装 SDK，将项目连接起来，并将特定于框架的发布密钥和秘密密钥写入正确的环境文件（例如 Next.js 的 `.env.local`，基于 Vite 的项目的 `.env`）。

#### 无需账户的入门指南

**无需登录。** 在支持的框架上，未身份验证的 `clerk init` 会提供可认领的无账户应用，并将临时开发密钥写入项目的环境文件 — 无需账户，无需浏览器，无需标志。不要先运行 `clerk auth login`。认证（或使用 `--app` / `--login`）它会通过 PLAPI 创建并链接一个真实的应用。

`--template <b2b-saas|b2c-saas|native|waitlist>` 会预配置临时应用。注意事项 — 在*现有*项目中注销的人类仍然会获得登录流程，除非他们通过 `--accountless`；`--keyless` 仍然是一个已弃用的兼容性别名。`--template`/`--fresh` 在任何目标真实应用时都会出错；登录仅自动认领 `clerk init` 创建的内容。见 [clerk-cli](../clerk-cli/references/auth.md#accountless-operating-without-an-account)。

### 场景 B — 现有项目，现有 Clerk 应用

```bash
clerk auth login                      # 一次性 OAuth (如果已登录则跳过)
clerk link                            # 如果在 .env 中存在 CLERK_PUBLISHABLE_KEY 则自动链接
clerk link --app app_xxx              # 显式表单，在代理模式下需要
clerk env pull                        # 写入检测到的框架环境变量
```

### 场景 C — 现有项目，新 Clerk 应用

```bash
clerk auth login
clerk apps create "My App" --json     # 返回新的 app_id
clerk link --app app_xxx
clerk env pull
```

### 日常操作

```bash
clerk env pull                        # 刷新密钥 (使用链接的配置文件)
clerk env pull --instance prod        # 生产密钥
clerk doctor --json                   # 框架集成健康检查
```

### 旋转秘密密钥（替换控制面板旋转）

PLAPI 直接暴露了秘密密钥旋转。在友好的包装器推出之前，请使用原始 `clerk api`：

```bash
clerk api --platform POST /v1/platform/applications/<app_id>/rotate_secret_keys \
  -d '{"delay_old_secrets_expiration_hours": 24, "reason": "scheduled rotation"}'
```

`delay_old_secrets_expiration_hours` 使旧密钥在宽限期有效，以便部署可以无停机时间向前推进。

### 代理的注意事项

- `clerk init` 创建的无认领无账户应用可以在无需账户的情况下配置 — 见 [无账户命令表](../clerk-cli/references/auth.md#accountless-operating-without-an-account) 了解哪些命令可用，哪些需要已认领的应用。
- `clerk link`（无标志）仅在 `.env` / `.env.local` 中已存在 `CLERK_PUBLISHABLE_KEY` 时才自动链接。如果没有，代理模式会出错： "Cannot select an application in agent mode." 发生这种情况时，运行 `clerk apps list --json`，并询问用户要链接哪个 `app_id` 而不是猜测。
- 在 `apps list/create`、`users create` 和 `doctor` 上传递 `--json` 以获取可解析的输出。
- CLI 会自动检测框架环境变量名称（Vite 的 `VITE_CLERK_PUBLISHABLE_KEY`，Next.js 的 `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` 等）和目标文件（`.env.development.local` > `.env.local` > `.env`）。

## 快速参考（控制面板回退）

如果 CLI 不是选项（沙盒环境，文档演练），这里提供手动控制面板路径：

| 步骤 | 操作 |
|------|------|
| 1. 检测框架 | 查看 `package.json` 依赖项 |
| 2. 获取快速入门 | 在适当的文档 URL 上使用 WebFetch |
| 3. 按说明操作 | 执行步骤；创建 `proxy.ts` (Next.js <=15: `middleware.ts`) |
| 4. 获取 API 密钥 | 从 [dashboard.clerk.com](https://dashboard.clerk.com/~/api-keys) |

> 如果项目有 `components.json` (shadcn/ui)，在设置后应用 shadcn 主题。见 `clerk-custom-ui` 技能 → shadcn 主题。

## 框架检测

检查 `package.json` 以识别框架：

| 依赖项 | 框架 | 快速入门 URL |
|------------|-----------|----------------|
| `next` | Next.js | `https://clerk.com/docs/nextjs/getting-started/quickstart` |
| `@remix-run/react` | Remix (已弃用) | 迁移到 React Router v7 — 使用下面的 React Router 快速入门 |
| `react-router` | React Router (v7+) | `https://clerk.com/docs/react-router/getting-started/quickstart` |
| `astro` | Astro | `https://clerk.com/docs/astro/getting-started/quickstart` |
| `nuxt` | Nuxt | `https://clerk.com/docs/nuxt/getting-started/quickstart` |
| `@tanstack/react-start` | TanStack Start | `https://clerk.com/docs/tanstack-react-start/getting-started/quickstart` |
| `react` (无框架) | React SPA | `https://clerk.com/docs/react/getting-started/quickstart` |
| `vue` | Vue | `https://clerk.com/docs/vue/getting-started/quickstart` |
| `express` | Express | `https://clerk.com/docs/expressjs/getting-started/quickstart` |
| `fastify` | Fastify | `https://clerk.com/docs/fastify/getting-started/quickstart` |
| `expo` | Expo | `https://clerk.com/docs/expo/getting-started/quickstart` |

对于其他平台：
- **Chrome 扩展**: `https://clerk.com/docs/chrome-extension/getting-started/quickstart`
- **Android**: `https://clerk.com/docs/android/getting-started/quickstart`
- **iOS**: `https://clerk.com/docs/ios/getting-started/quickstart`
- **纯 JavaScript**: `https://clerk.com/docs/js-frontend/getting-started/quickstart`

## 决策树

```
用户请求: "添加 Clerk" / "添加身份验证"
    │
    ├─ 读取 package.json
    │
    ├─ 检测到现有身份验证？
    │   ├─ 是 → 审计 → 迁移计划
    │   └─ 否 → 新安装
    │
    ├─ 识别框架 → WebFetch 快速入门 → 按说明操作
    │   └─ Next.js？ → 创建 proxy.ts (Next.js <=15: middleware.ts)
    │
    └─ 存在 components.json？ → 是 → 应用 shadcn 主题 (见 clerk-custom-ui)
```

## 设置过程

### 1. 检测框架

读取项目的 `package.json` 并将依赖项与上表匹配。

### 2. 获取快速入门指南

使用 WebFetch 获取检测到的框架的官方快速入门：

```
WebFetch: https://clerk.com/docs/{framework}/getting-started/quickstart
提示: "提取包括所有代码片段、文件路径和配置步骤的完整设置说明。"
```

### 3. 按说明操作

执行快速入门指南中的每个步骤：
- 安装所需的包
- 设置环境变量
- 添加提供程序和代理/中间件
- 如有必要，创建登录/注册路由
- 测试集成

> **Next.js:** 创建 `proxy.ts` (Next.js <=15: `middleware.ts`)。见 `clerk-nextjs-patterns` 技能了解中间件策略。

> **shadcn/ui 检测** (`components.json` 存在): 始终应用 shadcn 主题。见 `clerk-custom-ui` 技能 → shadcn 主题部分。

### 4. 获取 API 密钥

开发 API 密钥的两种路径：

**CLI (自动)**
- `clerk init` 将临时开发密钥写入项目的环境文件 — 无需 Clerk 账户
- 准备好时，运行 `clerk auth login`，应用会自动认领到您的 Clerk 账户，以便您可以从控制面板编辑它
- 新项目最简单的路径

**手动 (控制面板)**
- 从 [dashboard.clerk.com](https://dashboard.clerk.com/~/api-keys) 获取密钥
- **发布密钥**: 以 `pk_test_` 或 `pk_live_` 开头
- **秘密密钥**: 以 `sk_test_` 或 `sk_live_` 开头
- 设置为环境变量: `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` 和 `CLERK_SECRET_KEY`

## 从其他身份验证提供程序迁移

如果项目已经具有身份验证，则在替换它之前创建迁移计划。

### 检测现有身份验证

检查 `package.json` 中的现有身份验证库：
- `next-auth` / `@auth/core` → NextAuth/Auth.js
- `@supabase/supabase-js` → Supabase Auth
- `firebase` / `firebase-admin` → Firebase Auth
- `@aws-amplify/auth` → AWS Cognito
- `auth0` / `@auth0/nextjs-auth0` → Auth0
- `passport` → Passport.js
- 自定义 JWT/会话实现

### 迁移过程

1. **审计当前身份验证** - 识别所有身份验证触点：
   - 登录/注册页面
   - 会话/令牌处理
   - 受保护的路由和中间件
   - 用户数据存储（数据库表，外部 ID）
   - 配置的 OAuth 提供程序

2. **创建迁移计划** - 考虑：
   - **用户数据导出** - 导出用户并通过 Clerk 的 Backend API 导入
   - **密码哈希** - Clerk 可以透明地将哈希升级为 Bcrypt
   - **外部 ID** - 将旧用户 ID 存储为 Clerk 中的 `external_id`
   - **会话处理** - 现有会话在切换时将终止

3. **选择迁移策略**：
   - **一次性切换** - 一次性切换所有用户（更简单，需要维护窗口）
   - **逐步迁移** - 暂时运行两个系统（风险较低，复杂性较高）

### 迁移参考

- **迁移概述**: https://clerk.com/docs/guides/development/migrating/overview

## SDK 注意事项

### 包名称

| 包 | 安装 |
|---------|---------|
| Next.js | `@clerk/nextjs` |
| React | `@clerk/react` |
| Expo | `@clerk/expo` |
| React Router | `@clerk/react-router` |
| TanStack Start | `@clerk/tanstack-react-start` |

> **Core 2 ONLY (skip if current SDK):** React 和 Expo 包的名称不同: `@clerk/clerk-react` 和 `@clerk/clerk-expo`（带有 `clerk-` 前缀）。

### ClerkProvider 位置 (Next.js)

`ClerkProvider` 必须放置在 **`<body>` 内部**，而不是包装 `<html>`：

```tsx
// root layout.tsx
export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <ClerkProvider>{children}</ClerkProvider>
      </body>
    </html>
  )
}
```

> **Core 2 ONLY (skip if current SDK):** `ClerkProvider` 可以直接包装 `<html>`。

### 动态渲染 (Next.js)

对于带有身份验证数据的动态渲染，使用 `dynamic` 属性：

```tsx
<ClerkProvider dynamic>{children}</ClerkProvider>
```

### Node.js 要求

需要 **Node.js 20.9.0** 或更高版本。

> **Core 2 ONLY (skip if current SDK):** 最小 Node.js 18.17.0。

### 主题包

主题从 `@clerk/ui` 安装：

```bash
npm install @clerk/ui
```

> **Core 2 ONLY (skip if current SDK):** 主题来自 `@clerk/themes` 而不是 `@clerk/ui`。

### shadcn 主题

如果项目使用 shadcn/ui（在项目根目录中检查 `components.json`），应用 shadcn 主题，以便 Clerk 组件与应用的设计系统匹配：

```bash
npm install @clerk/ui
```

```tsx
import { shadcn } from '@clerk/ui/themes'

<ClerkProvider appearance={{ theme: shadcn }}>{children}</ClerkProvider>
```

也在您的全局样式中导入 shadcn CSS：
```css
@import 'tailwindcss';
@import '@clerk/ui/themes/shadcn.css';
```

> **Core 2 ONLY (skip if current SDK):** 从 `@clerk/themes` 和 `@clerk/themes/shadcn.css` 导入。

## 常见陷阱

> **首先运行 `clerk doctor`。** 它检查框架集成、环境变量、中间件存在和 SDK 安装状态。一次解决很多问题。

| 问题 | 解决方案 |
|-------|----------|
| `auth()` 缺少 `await` | 在 Next.js 15+ 中，`auth()` 是异步的: `const { userId } = await auth()` |
| 暴露 `CLERK_SECRET_KEY` | 不要在客户端代码中使用秘密密钥；只有 `NEXT_PUBLIC_*` 密钥是安全的 |
| 缺少中间件匹配器 | 包括 API 路由: `matcher: ['/((?!.*\\..*|_next).*)', '/']` |
| ClerkProvider 位置 | 必须在根布局的 `<body>` 内部（Core 2: 可以包装 `<html>`） |
| 身份验证路由不是公开的 | 在中间件配置中允许 `/sign-in`，`/sign-up` |
| 登录页面需要身份验证 | 为了保持 "/" 公开，排除它: `matcher: ['/((?!.*\\..*|_next|^/$).*)', '/api/(.*)']` |
| 错误的导入路径 | 服务器代码使用 `@clerk/nextjs/server`，客户端使用 `@clerk/nextjs` |
| 错误的包名称 | 使用 `@clerk/react` 而不是 `@clerk/clerk-react` (Core 2 命名) |

## 参考资料见

- `clerk-custom-ui` - 自定义登录/注册组件
- `clerk-nextjs-patterns` - 高级 Next.js 模式
- `clerk-react-patterns` - React SPA 模式
- `clerk-react-router-patterns` - React Router 模式
- `clerk-vue-patterns` - Vue 模式
- `clerk-nuxt-patterns` - Nuxt 模式
- `clerk-astro-patterns` - Astro 模式
- `clerk-tanstack-patterns` - TanStack Start 模式
- `clerk-chrome-extension-patterns` - Chrome 扩展模式
- `clerk-orgs` - B2B 多租户组织
- `clerk-webhooks` - Webhook → 数据库同步
- `clerk-testing` - E2E 测试设置
- `clerk-swift` - 原生 iOS 身份验证
- `clerk-android` - 原生 Android 身份验证
- `clerk-expo` - Expo / React Native 身份验证
- `clerk-backend-api` - Backend REST API 探索器

## 文档

- **快速入门概述**: https://clerk.com/docs/getting-started/quickstart/overview
- **迁移指南**: https://clerk.com/docs/guides/development/migrating/overview
- **完整文档**: https://clerk.com/docs
