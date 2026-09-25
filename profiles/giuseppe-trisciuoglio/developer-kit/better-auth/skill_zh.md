# 更好的认证集成指南

## 概述

Better Auth 是一个支持 TypeScript 的类型安全认证框架，支持多种提供者、双因素认证 (2FA)、单点登录 (SSO)、组织机构以及密钥。本指南涵盖了将 NestJS 后端与 Drizzle ORM + PostgreSQL 和 Next.js App Router 前端集成的模式。

## 何时使用

- 使用 NestJS 后端设置 Better Auth
- 集成 Next.js App Router 前端
- 使用 PostgreSQL 配置 Drizzle ORM 模式
- 实现社交登录（GitHub、Google、Facebook、Microsoft）
- 添加 MFA/2FA，支持 TOTP、无密码密钥认证或魔法链接
- 管理受信任的设备以及用于账户恢复的备用代码
- 使用组织机构或 SSO 构建多租户应用
- 创建受保护的路由并管理会话

## 快速入门

### 安装

```bash
# 后端 (NestJS)
npm install better-auth @auth/drizzle-adapter drizzle-orm pg
npm install -D drizzle-kit

# 前端 (Next.js)
npm install better-auth
```

### 四步设置

1. **数据库**：安装 Drizzle，配置模式，运行迁移
2. **后端**：使用 NestJS 模块创建 Better Auth 实例
3. **前端**：配置认证客户端，创建页面，添加中间件
4. **插件**：按需添加 2FA、密钥、组织机构

参考 `references/nestjs-setup.md` 获取完整的后端设置，参考 `references/plugins.md` 获取插件配置。

## 指南

### 第 1 步：数据库设置

1. **安装依赖项**
   ```bash
   npm install drizzle-orm pg @auth/drizzle-adapter better-auth
   npm install -D drizzle-kit
   ```

2. **创建 Drizzle 配置** (`drizzle.config.ts`)
   ```typescript
   import { defineConfig } from 'drizzle-kit';
   export default defineConfig({
     schema: './src/auth/schema.ts',
     out: './drizzle',
     dialect: 'postgresql',
     dbCredentials: { url: process.env.DATABASE_URL! },
   });
   ```

3. **生成并运行迁移**
   ```bash
   npx drizzle-kit generate
   npx drizzle-kit migrate
   ```

   **检查点**：验证已创建的表：`psql $DATABASE_URL -c "\dt"` 应显示 `user`、`account`、`session`、`verification_token` 表。

### 第 2 步：后端设置 (NestJS)

1. **创建数据库模块** - 设置 Drizzle 连接服务

2. **配置 Better Auth 实例**
   ```typescript
   // src/auth/auth.instance.ts
   import { betterAuth } from 'better-auth';
   import { drizzleAdapter } from '@auth/drizzle-adapter';
   import * as schema from './schema';

   export const auth = betterAuth({
     database: drizzleAdapter(schema, { provider: 'postgresql' }),
     emailAndPassword: { enabled: true },
     socialProviders: {
       github: {
         clientId: process.env.AUTH_GITHUB_CLIENT_ID!,
         clientSecret: process.env.AUTH_GITHUB_CLIENT_SECRET!,
       }
     }
   });
   ```

3. **创建认证控制器**
   ```typescript
   @Controller('auth')
   export class AuthController {
     @All('*')
     async handleAuth(@Req() req: Request, @Res() res: Response) {
       return auth.handler(req);
     }
   }
   ```

   **检查点**：当未认证时，测试端点 `GET /auth/get-session` 返回 `{ session: null }`（无错误）。

### 第 3 步：前端设置 (Next.js)

1. **配置认证客户端** (`lib/auth.ts`)
   ```typescript
   import { createAuthClient } from 'better-auth/client';
   export const authClient = createAuthClient({
     baseURL: process.env.NEXT_PUBLIC_APP_URL!
   });
   ```

2. **添加中间件** (`middleware.ts`)
   ```typescript
   import { auth } from '@/lib/auth';
   export default auth((req) => {
     if (!req.auth && req.nextUrl.pathname.startsWith('/dashboard')) {
       return Response.redirect(new URL('/sign-in', req.nextUrl.origin));
     }
   });
   export const config = { matcher: ['/dashboard/:path*'] };
   ```

3. **创建登录页面** - 使用表单或社交按钮

   **检查点**：未登录时访问 `/dashboard` 应重定向到 `/sign-in`。

### 第 4 步：高级功能

从 `references/plugins.md` 添加插件：

- **2FA**：`twoFactor({ issuer: 'AppName', otpOptions: { sendOTP } })`
- **密钥**：`passkey({ rpID: 'domain.com', rpName: 'App' })`
- **组织机构**：`organization({ avatar: { enabled: true } })`
- **魔法链接**：`magicLink({ sendMagicLink })`
- **SSO**：`sso({ saml: { enabled: true } })`

   **检查点**：添加插件后，重新运行迁移并验证新表是否存在。

## 示例

### 示例 1：带会话的服务器组件

**输入**：在 Next.js 服务器组件中显示用户数据。

```tsx
// app/dashboard/page.tsx
import { auth } from '@/lib/auth';
import { redirect } from 'next/navigation';

export default async function DashboardPage() {
  const session = await auth();

  if (!session) {
    redirect('/sign-in');
  }

  return (
    <div>
      <h1>欢迎，{session.user.name}</h1>
      <p>邮箱：{session.user.email}</p>
    </div>
  );
}
```

**输出**：为认证用户渲染用户信息；未认证用户重定向到登录页面。

### 示例 2：带受信任设备的 2FA TOTP 验证

**输入**：用户已启用 2FA 并希望登录，将设备标记为受信任。

```typescript
// 服务器：配置 2FA 并发送 OTP
export const auth = betterAuth({
  plugins: [
    twoFactor({
      issuer: 'MyApp',
      otpOptions: {
        async sendOTP({ user, otp }, ctx) {
          await sendEmail({
            to: user.email,
            subject: '您的验证码',
            body: `代码：${otp}`
          });
        }
      }
    })
  ]
});

// 客户端：验证 TOTP 并信任设备
const verify2FA = async (code: string) => {
  const { data } = await authClient.twoFactor.verifyTotp({
    code,
    trustDevice: true  // 设备受信任 30 天
  });

  if (data) {
    router.push('/dashboard');
  }
};
```

**输出**：用户认证；设备受信任 30 天，无需 2FA 提示。

### 示例 3：密钥注册和登录

**输入**：为无密码登录启用密钥（WebAuthn）认证。

```typescript
// 服务器
import { passkey } from '@better-auth/passkey';
export const auth = betterAuth({
  plugins: [
    passkey({
      rpID: 'example.com',
      rpName: '我的应用',
    })
  ]
});

// 客户端：注册密钥
const registerPasskey = async () => {
  const { data } = await authClient.passkey.register({
    name: '我的设备'
  });
};

// 客户端：使用自动填充登录
const signInWithPasskey = async () => {
  await authClient.signIn.passkey({
    autoFill: true,  // 浏览器建议密钥
  });
};
```

**输出**：用户可以通过生物识别、PIN 或安全密钥进行注册和认证。

更多示例（备用代码、组织机构、魔法链接、条件 UI），参考 `references/plugins.md` 和 `references/passkey.md`。

## 最佳实践

1. **环境变量**：将所有密钥存储在 `.env` 中，添加到 `.gitignore`
2. **密钥生成**：使用 `openssl rand -base64 32` 生成 `BETTER_AUTH_SECRET`
3. **HTTPS 必须启用**：OAuth 回调需要 HTTPS（本地测试可使用 `ngrok`）
4. **会话过期**：根据安全需求配置（默认 7 天）
5. **数据库索引**：为 `email`、`userId` 添加索引以提高性能
6. **错误处理**：返回通用错误，不暴露敏感信息
7. **速率限制**：为认证端点添加限制，防止暴力攻击
8. **类型安全**：使用 `npx better-auth typegen` 获取完整的 TypeScript 覆盖

## 限制和警告

### 安全注意事项

- **切勿提交密钥**：将 `.env` 添加到 `.gitignore`；切勿提交 OAuth 密钥或数据库凭证
- **验证重定向 URL**：始终验证 OAuth 重定向 URL，防止开放重定向
- **哈希密码**：Better Auth 自动处理密码哈希；切勿实现自定义哈希
- **会话存储**：生产环境使用 Redis 或其他可扩展的会话存储
- **仅 HTTPS**：生产环境始终使用 HTTPS 进行认证
- **邮箱验证**：密码认证始终需要邮箱验证

### 已知限制

- Better Auth 需要 Node.js 18+ 才支持 Next.js App Router
- 某些 OAuth 提供者需要特定的重定向 URL 格式
- 密钥需要 HTTPS 和兼容的浏览器
- 组织机构功能需要额外的数据库表

## 资源

### 文档

- [Better Auth](https://www.better-auth.com) - 官方文档
- [Drizzle ORM](https://orm.drizzle.team) - 数据库 ORM
- [NestJS](https://docs.nestjs.com) - 后端框架
- [Next.js](https://nextjs.org/docs/app) - 前端框架

### 参考实现

- `references/nestjs-setup.md` - 完整的 NestJS 后端设置
- `references/nextjs-setup.md` - 完整的 Next.js 前端设置
- `references/plugins.md` - 插件配置（2FA、密钥、组织机构、SSO、魔法链接）
- `references/mfa-2fa.md` - 详细的 MFA/2FA 指南
- `references/passkey.md` - 详细的密钥实现
- `references/schema.md` - Drizzle 模式参考
- `references/social-providers.md` - 社交提供者配置
