## 快速入门

1. 启用邮箱/密码：`emailAndPassword: { enabled: true }`
2. 配置 `emailVerification.sendVerificationEmail`
3. 添加 `sendResetPassword` 用于密码重置流程
4. 运行 `npx auth@latest migrate`
5. 验证：尝试注册并确认验证邮件是否触发

---

## 邮箱验证设置

配置 `emailVerification.sendVerificationEmail` 以验证用户邮箱地址。

```ts
import { betterAuth } from "better-auth";
import { sendEmail } from "./email"; // 你的邮箱发送函数

export const auth = betterAuth({
  emailVerification: {
    sendVerificationEmail: async ({ user, url, token }, request) => {
      await sendEmail({
        to: user.email,
        subject: "验证你的邮箱地址",
        text: `点击链接验证你的邮箱：${url}`,
      });
    },
  },
});
```

**注意**：`url` 参数包含完整的验证链接。如果需要构建自定义验证 URL，`token` 是可用的。

### 要求邮箱验证

为了更严格的安全性，启用 `emailAndPassword.requireEmailVerification` 以阻止用户在验证邮箱前登录。启用后，未验证的用户在每次登录尝试时都会收到新的验证邮件。

```ts
export const auth = betterAuth({
  emailAndPassword: {
    requireEmailVerification: true,
  },
});
```

**注意**：这需要配置 `sendVerificationEmail`，并且仅适用于邮箱/密码登录。

## 客户端验证

实现客户端验证以提供即时用户反馈并减少服务器负载。

## 回调 URL

在注册和登录请求中始终使用绝对 URL（包括协议和域名）。这可以防止 Better Auth 需要推断协议和域名，当你的后端和前端在不同的域时可能会引发问题。

```ts
const { data, error } = await authClient.signUp.email({
  callbackURL: "https://example.com/callback", // 绝对 URL，包含协议和域名
});
```

## 密码重置流程

在邮箱和密码配置中提供 `sendResetPassword` 以启用密码重置。

```ts
import { betterAuth } from "better-auth";
import { sendEmail } from "./email"; // 你的邮箱发送函数

export const auth = betterAuth({
  emailAndPassword: {
    enabled: true,
    // 自定义邮箱发送函数，用于发送重置密码邮件
    sendResetPassword: async ({ user, url, token }, request) => {
      void sendEmail({
        to: user.email,
        subject: "重置你的密码",
        text: `点击链接重置你的密码：${url}`,
      });
    },
    // 可选的事件钩子
    onPasswordReset: async ({ user }, request) => {
      // 你的逻辑
      console.log(`用户 ${user.email} 的密码已被重置。`);
    },
  },
});
```

### 安全考虑

内置保护：后台邮件发送（防时序攻击）、无效请求上的虚拟操作、无论用户是否存在，始终返回相同响应消息。

在无服务器平台上，配置后台任务处理器：

```ts
export const auth = betterAuth({
  advanced: {
    backgroundTasks: {
      handler: (promise) => {
        // 使用平台特定的方法，如 waitUntil
        waitUntil(promise);
      },
    },
  },
});
```

#### 令牌安全

令牌默认在 1 小时后过期。使用 `resetPasswordTokenExpiresIn`（以秒为单位）进行配置：

```ts
export const auth = betterAuth({
  emailAndPassword: {
    enabled: true,
    resetPasswordTokenExpiresIn: 60 * 30, // 30 分钟
  },
});
```

令牌是一次性的——在成功重置后立即删除。

#### 会话失效

启用 `revokeSessionsOnPasswordReset` 以在密码重置时使所有现有会话失效：

```ts
export const auth = betterAuth({
  emailAndPassword: {
    enabled: true,
    revokeSessionsOnPasswordReset: true,
  },
});
```

#### 密码要求

密码长度限制（可配置）：

```ts
export const auth = betterAuth({
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 12,
    maxPasswordLength: 256,
  },
});
```

### 发送密码重置

调用 `requestPasswordReset` 发送重置链接。触发你配置中的 `sendResetPassword` 函数。

```ts
const data = await auth.api.requestPasswordReset({
  body: {
    email: "john.doe@example.com", // 必填
    redirectTo: "https://example.com/reset-password",
  },
});
```

或使用 authClient：

```ts
const { data, error } = await authClient.requestPasswordReset({
  email: "john.doe@example.com", // 必填
  redirectTo: "https://example.com/reset-password",
});
```

**注意**：虽然 `email` 是必填的，但我们还建议配置 `redirectTo` 以提供更平滑的用户体验。

## 密码哈希

默认：`scrypt`（Node.js 原生，无外部依赖）。

### 自定义哈希算法

要使用 Argon2id 或其他算法，提供自定义的 `hash` 和 `verify` 函数：

```ts
import { betterAuth } from "better-auth";
import { hash, verify, type Options } from "@node-rs/argon2";

const argon2Options: Options = {
  memoryCost: 65536, // 64 MiB
  timeCost: 3, // 3 迭代
  parallelism: 4, // 4 并行通道
  outputLen: 32, // 32 字节输出
  algorithm: 2, // Argon2id 变体
};

export const auth = betterAuth({
  emailAndPassword: {
    enabled: true,
    password: {
      hash: (password) => hash(password, argon2Options),
      verify: ({ password, hash: storedHash }) =>
        verify(storedHash, password, argon2Options),
    },
  },
});
```

**注意**：如果你在现有系统上切换哈希算法，使用旧算法哈希的密码的用户将无法登录。如有需要，请规划迁移策略。
