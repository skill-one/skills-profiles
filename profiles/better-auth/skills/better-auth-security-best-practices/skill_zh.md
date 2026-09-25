## 密钥管理

### 配置密钥

```ts
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET, // 或通过 `BETTER_AUTH_SECRET` 环境变量
});
```

Better Auth 按以下顺序查找密钥：
1. 配置中的 `options.secret`
2. `BETTER_AUTH_SECRET` 环境变量
3. `AUTH_SECRET` 环境变量

### 密钥要求

- 在生产环境中拒绝默认/占位符密钥
- 如果长度小于 32 个字符或熵低于 120 位，则发出警告
- 生成：`openssl rand -base64 32`
- 不要将密钥提交到版本控制

## 速率限制

默认在生产环境中启用。适用于所有端点。插件可以覆盖每个端点的设置。

### 默认配置

```ts
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  rateLimit: {
    enabled: true, // 生产环境默认为 true
    window: 10, // 时间窗口（秒）（默认：10）
    max: 100, // 每个窗口的最大请求次数（默认：100）
  },
});
```

### 存储选项

选项：`"memory"`（重启时重置，避免在无服务器环境中使用）、`"database"`（持久化）、`"secondary-storage"`（Redis，可用时默认）。

```ts
rateLimit: {
  storage: "database",
}
```

### 自定义存储

实现自己的速率限制存储：

```ts
rateLimit: {
  customStorage: {
    get: async (key) => {
      // 返回 { count: number, expiresAt: number } 或 null
    },
    set: async (key, data) => {
      // 存储速率限制数据
    },
  },
}
```

### 每个端点的规则

敏感端点默认为每 10 秒 3 次请求（`/sign-in`、`/sign-up`、`/change-password`、`/change-email`）。覆盖：

```ts
rateLimit: {
  customRules: {
    "/api/auth/sign-in/email": {
      window: 60, // 1 分钟窗口
      max: 5, // 5 次尝试
    },
    "/api/auth/some-safe-endpoint": false, // 禁用速率限制
  },
}
```

## CSRF 保护

多层保护：来源头验证、Fetch Metadata 检查和首次登录保护。

### 配置

```ts
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  advanced: {
    disableCSRFCheck: false, // 默认：false（保持启用）
  },
});
```

仅在测试或使用替代 CSRF 机制时禁用。

## 受信任的来源

### 配置受信任的来源

```ts
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  baseURL: "https://api.example.com",
  trustedOrigins: [
    "https://app.example.com",
    "https://admin.example.com",
  ],
});
```

`baseURL` 来源自动受信任。也可以通过环境变量配置：`BETTER_AUTH_TRUSTED_ORIGINS=https://app.example.com,https://admin.example.com`

### 通配符模式

```ts
trustedOrigins: [
  "*.example.com", // 匹配任何子域名
  "https://*.example.com", // 协议特定的通配符
  "exp://192.168.*.*:*/*", // 自定义方案（例如，Expo）
]
```

### 动态受信任的来源

根据请求计算受信任的来源：

```ts
trustedOrigins: async (request) => {
  // 验证数据库、头部等
  const tenant = getTenantFromRequest(request);
  return [`https://${tenant}.myapp.com`];
}
```

验证 `callbackURL`、`redirectTo`、`errorCallbackURL`、`newUserCallbackURL` 和 `origin` 是否受信任。无效的 URL 将收到 403。

## 会话安全

### 会话过期

```ts
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 天（默认）
    updateAge: 60 * 60 * 24, // 每 24 小时刷新会话（默认）
  },
});
```

### 会话缓存策略

在 cookie 中缓存会话数据以减少数据库查询：

```ts
session: {
  cookieCache: {
    enabled: true,
    maxAge: 60 * 5, // 5 分钟
    strategy: "compact", // 选项：`"compact"`、`"jwt"`、`"jwe"`
  },
}
```

策略：`"compact"`（Base64url + HMAC，最小）、`"jwt"`（HS256，标准）、`"jwe"`（加密，会话包含敏感数据时使用）。

## Cookie 安全

默认值：`secure: true`（HTTPS/生产）、`sameSite: "lax"`、`httpOnly: true`、`path: "/"`、前缀 `__Secure-`。

### 自定义 Cookie 配置

```ts
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  advanced: {
    useSecureCookies: true, // 强制使用安全 cookie
    cookiePrefix: "myapp", // 自定义前缀（默认：`"better-auth"`）
    defaultCookieAttributes: {
      sameSite: "strict", // 更严格的 CSRF 保护
      path: "/auth", // 限制 cookie 范围
    },
  },
});
```

### 跨子域名 Cookie

```ts
advanced: {
  crossSubDomainCookies: {
    enabled: true,
    domain: ".example.com", // 注意前面的点
    additionalCookies: ["session_token", "session_data"],
  },
}
```

仅在需要身份验证共享并信任所有子域名时启用。

## OAuth / 社交提供者安全

所有 OAuth 流程自动使用 PKCE。状态令牌是 32 个字符的随机字符串，10 分钟后过期。

### 状态参数存储

```ts
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  account: {
    storeStateStrategy: "cookie", // 选项：`"cookie"`（默认）、`"database"`
  },
});
```

### 加密 OAuth 令牌

```ts
account: {
  encryptOAuthTokens: true, // 使用 AES-256-GCM
}
```

如果为用户代表 API 存储OAuth令牌，请启用。仅当移动应用无法维护 cookie 时使用 `skipStateCookieCheck: true`。

## 基于 IP 的安全

### IP 地址配置

```ts
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  advanced: {
    ipAddress: {
      ipAddressHeaders: ["x-forwarded-for", "x-real-ip"], // 要检查的头部
      disableIpTracking: false, // 保持启用以用于速率限制
    },
  },
});
```

设置 `ipv6Subnet`（128、64、48、32；默认 64）以分组 IPv6 地址。仅当位于受信任的反向代理后面时才启用 `trustedProxyHeaders: true`。

## 数据库钩子用于安全审计

```ts
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  databaseHooks: {
    session: {
      create: {
        after: async ({ data, ctx }) => {
          await auditLog("session.created", {
            userId: data.userId,
            ip: ctx?.request?.headers.get("x-forwarded-for"),
            userAgent: ctx?.request?.headers.get("user-agent"),
          });
        },
      },
      delete: {
        before: async ({ data }) => {
          await auditLog("session.revoked", { sessionId: data.id });
        },
      },
    },
    user: {
      update: {
        after: async ({ data, oldData }) => {
          if (oldData?.email !== data.email) {
            await auditLog("user.email_changed", {
              userId: data.id,
              oldEmail: oldData?.email,
              newEmail: data.email,
            });
          }
        },
      },
    },
    account: {
      create: {
        after: async ({ data }) => {
          await auditLog("account.linked", {
            userId: data.userId,
            provider: data.providerId,
          });
        },
      },
    },
  },
});
```

从 `before` 钩子返回 `false` 以阻止操作。

## 后台任务

```ts
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  advanced: {
    backgroundTasks: {
      handler: (promise) => {
        // 平台特定的处理器
        // Vercel：waitUntil(promise)
        // Cloudflare：ctx.waitUntil(promise)
        waitUntil(promise);
      },
    },
  },
});
```

确保发送邮件等操作不会影响响应时间。

## 账户枚举预防

内置：一致响应消息、无效请求上的虚拟操作、后台邮件发送。返回通用错误消息（"Invalid credentials"）而不是特定消息（"User not found"）。

## 完整安全配置示例

```ts
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET,
  baseURL: "https://api.example.com",
  trustedOrigins: [
    "https://app.example.com",
    "https://*.preview.example.com",
  ],
  
  // 速率限制
  rateLimit: {
    enabled: true,
    storage: "secondary-storage",
    customRules: {
      "/api/auth/sign-in/email": { window: 60, max: 5 },
      "/api/auth/sign-up/email": { window: 60, max: 3 },
    },
  },
  
  // 会话安全
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 天
    updateAge: 60 * 60 * 24, // 24 小时
    freshAge: 60 * 60, // 敏感操作 1 小时
    cookieCache: {
      enabled: true,
      maxAge: 300,
      strategy: "jwe", // 加密会话数据
    },
  },
  
  // OAuth 安全
  account: {
    encryptOAuthTokens: true,
    storeStateStrategy: "cookie",
  },
  
  
  // 高级设置
  advanced: {
    useSecureCookies: true,
    cookiePrefix: "myapp",
    defaultCookieAttributes: {
      sameSite: "lax",
    },
    ipAddress: {
      ipAddressHeaders: ["x-forwarded-for"],
      ipv6Subnet: 64,
    },
    backgroundTasks: {
      handler: (promise) => waitUntil(promise),
    },
  },
  
  // 安全审计
  databaseHooks: {
    session: {
      create: {
        after: async ({ data, ctx }) => {
          console.log(`新会话为用户 ${data.userId}`);
        },
      },
    },
    user: {
      update: {
        after: async ({ data, oldData }) => {
          if (oldData?.email !== data.email) {
            console.log(`用户 ${data.id} 的邮箱已更改`);
          }
        },
      },
    },
  },
});
```

## 安全检查清单

部署到生产环境前：

- [ ] **密钥**：使用强、唯一的密钥（32+ 字符，高熵）
- [ ] **HTTPS**：确保 `baseURL` 使用 HTTPS
- [ ] **受信任的来源**：配置所有有效来源（前端、移动应用）
- [ ] **速率限制**：保持启用并设置适当的限制
- [ ] **CSRF 保护**：保持启用（`disableCSRFCheck: false`）
- [ ] **安全 Cookie**：启用自动使用 HTTPS
- [ ] **OAuth 令牌**：考虑 `encryptOAuthTokens: true` 如果存储令牌
- [ ] **后台任务**：为无服务器平台配置
- [ ] **审计日志**：通过 `databaseHooks` 或 `hooks` 实现
- [ ] **IP 跟踪**：配置头部如果位于代理后面
