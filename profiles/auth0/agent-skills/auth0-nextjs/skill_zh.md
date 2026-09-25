# Auth0 Next.js 集成

使用 @auth0/nextjs-auth0 为 Next.js 应用添加身份验证。支持 App Router 和 Pages Router。

---

## 前置条件

- Next.js 13+ 应用（App Router 或 Pages Router）
- 已配置 Auth0 账户和应用
- 如果您尚未设置 Auth0，请先使用 `auth0-quickstart` 功能

## 不应使用的情况

- **仅客户端的 React 应用** - 对于 Vite/CRA SPAs，请使用 `auth0-react`
- **React Native 移动应用** - 对于 iOS/Android，请使用 `auth0-react-native`
- **非 Next.js 框架** - 请使用特定框架的 SDK（Express、Vue、Angular 等）
- **仅状态less API** - 如果不需要会话管理，请使用 JWT 验证中间件

---

## 快速入门工作流

### 1. 安装 SDK

```bash
npm install @auth0/nextjs-auth0
```

### 2. 配置环境

**对于使用 Auth0 CLI 的自动设置**，请参阅 [设置指南](references/setup.md) 获取完整脚本。

**对于手动设置**：

创建 `.env.local`：

```bash
AUTH0_SECRET=<生成一个32字符的密钥>
APP_BASE_URL=http://localhost:3000
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
```

生成密钥：`openssl rand -hex 32`

**重要提示**：将 `.env.local` 添加到 `.gitignore`

### 3. 创建 Auth0 客户端和中间件

**首先检测项目结构**：检查项目是否使用 `src/` 目录（即是否存在 `src/app/` 或 `src/pages/`）。这决定了文件放置的位置：
- **使用 `src/`**：`src/lib/auth0.ts`、`src/middleware.ts`（或 `src/proxy.ts` 对于 Next.js 16）
- **不使用 `src/`**：`lib/auth0.ts`、`middleware.ts`（或 `proxy.ts` 对于 Next.js 16）

创建 `lib/auth0.ts`（如果使用 `src/` 规范，则为 `src/lib/auth0.ts`）：

```typescript
import { Auth0Client } from '@auth0/nextjs-auth0/server';

export const auth0 = new Auth0Client({
  domain: process.env.AUTH0_DOMAIN!,
  clientId: process.env.AUTH0_CLIENT_ID!,
  clientSecret: process.env.AUTH0_CLIENT_SECRET!,
  secret: process.env.AUTH0_SECRET!,
  appBaseUrl: process.env.APP_BASE_URL!,
});
```

**中间件配置（Next.js 15 与 16）**：

**Next.js 15** - 创建 `middleware.ts`（在项目根目录，或如果使用 `src/`，则为 `src/middleware.ts`）：

```typescript
import { NextRequest } from 'next/server';
import { auth0 } from '@/lib/auth0';

export async function middleware(request: NextRequest) {
  return await auth0.middleware(request);
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt).*)',
  ],
};
```

**Next.js 16** - 您有两个选项：

**选项 1**：使用 `middleware.ts`（与 Next.js 15 相同，相同的 `src/` 放置规则）：

```typescript
import { NextRequest } from 'next/server';
import { auth0 } from '@/lib/auth0';

export async function middleware(request: NextRequest) {
  return await auth0.middleware(request);
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt).*)',
  ],
};
```

**选项 2**：使用 `proxy.ts`（在项目根目录，或如果使用 `src/`，则为 `src/proxy.ts`）：

```typescript
import { NextRequest } from 'next/server';
import { auth0 } from '@/lib/auth0';

export async function proxy(request: NextRequest) {
  return await auth0.middleware(request);
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt).*)',
  ],
};
```

这会自动创建端点：
- `/auth/login` - 登录
- `/auth/logout` - 退出登录
- `/auth/callback` - OAuth 回调
- `/auth/profile` - 用户资料

### 4. 添加用户上下文（可选）

**注意**：在 v4 中，使用 `<Auth0Provider>` 进行包装是可选的。只有当您希望在服务器渲染期间向 `useUser()` 传递初始用户时才需要。

**App Router** - 可选地，在 `app/layout.tsx` 中包装应用：

```typescript
import { Auth0Provider } from '@auth0/nextjs-auth0/client';
import { auth0 } from '@/lib/auth0';

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const session = await auth0.getSession();

  return (
    <html>
      <body>
        <Auth0Provider user={session?.user}>{children}</Auth0Provider>
      </body>
    </html>
  );
}
```

**Pages Router** - 可选地，在 `pages/_app.tsx` 中包装应用：

```typescript
import { Auth0Provider } from '@auth0/nextjs-auth0/client';
import type { AppProps } from 'next/app';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <Auth0Provider user={pageProps.user}>
      <Component {...pageProps} />
    </Auth0Provider>
  );
}
```

### 5. 添加身份验证 UI

**客户端组件**（在两个路由器中均适用）：

```typescript
'use client'; // 仅 App Router 需要此标记

import { useUser } from '@auth0/nextjs-auth0/client';

export default function Profile() {
  const { user, isLoading } = useUser();

  if (isLoading) return <div>加载中...</div>;

  if (user) {
    return (
      <div>
        <img src={user.picture} alt={user.name} />
        <h2>欢迎，{user.name}！</h2>
        <a href="/auth/logout">退出登录</a>
      </div>
    );
  }

  return <a href="/auth/login">登录</a>;
}
```

### 6. 测试身份验证

启动开发服务器：

```bash
npm run dev
```

访问 `http://localhost:3000` 并测试登录流程。

---

## 详细文档

- **[设置指南](references/setup.md)** - 自动设置脚本、环境配置、Auth0 CLI 使用
- **[集成指南](references/integration.md)** - 服务器端身份验证、受保护路由、API 路由、中间件
- **[API 参考](references/api.md)** - 完整 SDK API、钩子、辅助函数、会话管理

---

## 常见错误

| 错误 | 修复 |
|------|------|
| 使用 v3 环境变量 | v4 使用 `APP_BASE_URL` 和 `AUTH0_DOMAIN`（不是 `AUTH0_BASE_URL` 或 `AUTH0_ISSUER_BASE_URL`） |
| 忘记在 Auth0 控制台添加回调 URL | 将 `/auth/callback` 添加到允许的回调 URL（例如，`http://localhost:3000/auth/callback`） |
| 缺少中间件配置 | v4 需要中间件来挂载身份验证路由 - 创建 `middleware.ts`（Next.js 15+16）或 `proxy.ts`（Next.js 16 仅）并包含 `auth0.middleware()` |
| 路由路径错误 | v4 使用 `/auth/login`，而不是 `/api/auth/login` - 路由会删除 `/api` 前缀 |
| 缺少或弱 AUTH0_SECRET | 使用 `openssl rand -hex 32` 生成安全密钥，并存储在 .env.local 中 |
| 使用 .env 而不是 .env.local | Next.js 需要 .env.local 用于本地密钥，且 .env.local 应该在 .gitignore 中 |
| 在 Auth0 中将应用创建为 SPA 类型 | 必须为 Next.js 创建常规 Web 应用类型 |
| 使用已移除的 v3 辅助函数 | v4 移除了 `withPageAuthRequired` 和 `withApiAuthRequired` - 使用 `getSession()` 代替 |
| 在服务器组件中使用 useUser | useUser 仅客户端可用，服务器组件应使用 `auth0.getSession()` |
| AUTH0_DOMAIN 包含 https:// | v4 `AUTH0_DOMAIN` 应该只是域名（例如，`example.auth0.com`），不包括方案 |

---

## 相关功能

- `auth0-quickstart` - 基本 Auth0 设置
- `auth0-migration` - 从其他身份验证提供者迁移
- `auth0-mfa` - 添加多因素身份验证
- `auth0-cli` - 从终端管理 Auth0 资源

---

## 快速参考

**v4 设置**：
- 检测 `src/` 规范：检查是否存在 `src/app/` 或 `src/pages/` - 如果存在，将所有文件放在 `src/` 中
- 创建 `lib/auth0.ts`（或 `src/lib/auth0.ts`）并包含 `Auth0Client` 实例
- 创建中间件配置（必需）：
  - Next.js 15：`middleware.ts`（或 `src/middleware.ts`）包含 `middleware()` 函数
  - Next.js 16：使用 `middleware.ts` 包含 `middleware()` 函数，或使用 `proxy.ts` 包含 `proxy()` 函数（遵循相同的 `src/` 规则）
- 可选：使用 `<Auth0Provider>` 包装以进行服务器端用户传递

**客户端钩子**：
- `useUser()` - 在客户端组件中获取用户
- `user` - 用户资料对象
- `isLoading` - 加载状态

**服务器端方法**：
- `auth0.getSession()` - 在服务器组件/API 路由/中间件中获取会话
- `auth0.getAccessToken()` - 获取用于调用 API 的访问令牌

**常见用例**：
- 登录/退出链接 → 使用 `/auth/login` 和 `/auth/logout` 路径（见第 5 步）
- 受保护页面（App Router）→ [集成指南](references/integration.md#protected-pages-app-router)
- 受保护页面（Pages Router）→ [集成指南](references/integration.md#protected-pages-pages-router)
- 带身份验证的 API 路由 → [集成指南](references/integration.md#protected-api-routes)
- 中间件保护 → [集成指南](references/integration.md#middleware)

---

## 参考

- [Auth0 Next.js SDK 文档](https://auth0.com/docs/libraries/nextjs)
- [Auth0 Next.js 快速入门](https://auth0.com/docs/quickstart/webapp/nextjs)
- [SDK GitHub 仓库](https://github.com/auth0/nextjs-auth0)
