## 设置

1. 将 `twoFactor()` 插件添加到服务器配置中，并指定 `issuer`
2. 将 `twoFactorClient()` 插件添加到客户端配置中
3. 运行 `npx auth@latest migrate`（内置适配器）或为 Drizzle/Prisma 生成并推送
4. 验证：检查用户表中是否存在 `twoFactorSecret` 列

```ts
import { betterAuth } from "better-auth";
import { twoFactor } from "better-auth/plugins";

export const auth = betterAuth({
  appName: "我的应用",
  plugins: [
    twoFactor({
      issuer: "我的应用",
    }),
  ],
});
```

### 客户端设置

```ts
import { createAuthClient } from "better-auth/client";
import { twoFactorClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  plugins: [
    twoFactorClient({
      onTwoFactorRedirect() {
        window.location.href = "/2fa";
      },
    }),
  ],
});
```

## 为用户启用 2FA

需要密码验证。返回 TOTP URI（用于生成二维码）和备用码。

```ts
const enable2FA = async (password: string) => {
  const { data, error } = await authClient.twoFactor.enable({
    password,
  });

  if (data) {
    // data.totpURI — 从这里生成二维码
    // data.backupCodes — 显示给用户
  }
};
```

`twoFactorEnabled` 不会在第一次 TOTP 验证成功后才设置为 `true`。可以通过 `skipVerificationOnEnable: true` 覆盖（不推荐）。

## TOTP（身份验证器应用）

### 显示二维码

```tsx
import QRCode from "react-qr-code";

const TotpSetup = ({ totpURI }: { totpURI: string }) => {
  return <QRCode value={totpURI} />;
};
```

### 验证 TOTP 码

接受当前时间前后一个时间段内的码：

```ts
const verifyTotp = async (code: string) => {
  const { data, error } = await authClient.twoFactor.verifyTotp({
    code,
    trustDevice: true,
  });
};
```

### TOTP 配置选项

```ts
twoFactor({
  totpOptions: {
    digits: 6, // 6 或 8 位（默认：6）
    period: 30, // 码的有效期（秒）（默认：30）
  },
});
```

## OTP（电子邮件/短信）

### 配置 OTP 发送

```ts
import { betterAuth } from "better-auth";
import { twoFactor } from "better-auth/plugins";
import { sendEmail } from "./email";

export const auth = betterAuth({
  plugins: [
    twoFactor({
      otpOptions: {
        sendOTP: async ({ user, otp }, ctx) => {
          await sendEmail({
            to: user.email,
            subject: "您的验证码",
            text: `您的码是：${otp}`,
          });
        },
        period: 5, // 码的有效期（分钟）（默认：3）
        digits: 6, // 码的位数（默认：6）
        allowedAttempts: 5, // 最大验证尝试次数（默认：5）
      },
    }),
  ],
});
```

### 发送和验证 OTP

发送：`authClient.twoFactor.sendOtp()`。验证：`authClient.twoFactor.verifyOtp({ code, trustDevice: true })`。

### OTP 存储安全

配置 OTP 码在数据库中的存储方式：

```ts
twoFactor({
  otpOptions: {
    storeOTP: "encrypted", // 选项： "plain", "encrypted", "hashed"
  },
});
```

自定义加密：

```ts
twoFactor({
  otpOptions: {
    storeOTP: {
      encrypt: async (token) => myEncrypt(token),
      decrypt: async (token) => myDecrypt(token),
    },
  },
});
```

## 备用码

在启用 2FA 时自动生成。每个码仅可使用一次。

### 显示备用码

```tsx
const BackupCodes = ({ codes }: { codes: string[] }) => {
  return (
    <div>
      <p>将这些码保存在安全的地方：</p>
      <ul>
        {codes.map((code, i) => (
          <li key={i}>{code}</li>
        ))}
      </ul>
    </div>
  );
};
```

### 重新生成备用码

使所有之前的码失效：

```ts
const regenerateBackupCodes = async (password: string) => {
  const { data, error } = await authClient.twoFactor.generateBackupCodes({
    password,
  });
  // data.backupCodes 包含新的码
};
```

### 使用备用码进行恢复

```ts
const verifyBackupCode = async (code: string) => {
  const { data, error } = await authClient.twoFactor.verifyBackupCode({
    code,
    trustDevice: true,
  });
};
```

### 备用码配置

```ts
twoFactor({
  backupCodeOptions: {
    amount: 10, // 生成的码数量（默认：10）
    length: 10, // 每个码的长度（默认：10）
    storeBackupCodes: "encrypted", // 选项： "plain", "encrypted"
  },
});
```

## 在登录过程中处理 2FA

当需要 2FA 时，响应将包含 `twoFactorRedirect: true`：

### 登录流程

1. 调用 `signIn.email({ email, password })`
2. 在 `onSuccess` 中检查 `context.data.twoFactorRedirect`
3. 如果为 `true`，重定向到 `/2fa` 验证页面
4. 通过 TOTP、OTP 或备用码进行验证
5. 在验证成功后创建会话 cookie

```ts
const signIn = async (email: string, password: string) => {
  const { data, error } = await authClient.signIn.email(
    { email, password },
    {
      onSuccess(context) {
        if (context.data.twoFactorRedirect) {
          window.location.href = "/2fa";
        }
      },
    }
  );
};
```

服务器端：在使用 `auth.api.signInEmail` 时检查 `response` 中是否包含 `"twoFactorRedirect"`。

## 受信任的设备

验证时传递 `trustDevice: true`。默认信任持续时间：30 天 (`trustDeviceMaxAge`)。每次登录时刷新。

## 安全注意事项

### 会话管理

流程：凭证 → 会话移除 → 临时 2FA cookie（默认 10 分钟）→ 验证 → 会话创建。

```ts
twoFactor({
  twoFactorCookieMaxAge: 600, // 10 分钟（秒）（默认）
});
```

### 速率限制

内置：所有 2FA 端点每 10 秒 3 个请求。OTP 有额外的尝试限制：

```ts
twoFactor({
  otpOptions: {
    allowedAttempts: 5, // 每个OTP码的最大尝试次数（默认：5）
  },
});
```

### 静态加密

TOTP 密钥：使用 auth 密钥加密。备用码：默认加密。OTP：可配置（`"plain"`, `"encrypted"`, `"hashed"`）。使用常量时间比较进行验证。

2FA 仅能对凭证（电子邮件/密码）账户启用。

## 禁用 2FA

需要密码确认。撤销受信任的设备记录：

```ts
const disable2FA = async (password: string) => {
  const { data, error } = await authClient.twoFactor.disable({
    password,
  });
};
```

## 完整配置示例

```ts
import { betterAuth } from "better-auth";
import { twoFactor } from "better-auth/plugins";
import { sendEmail } from "./email";

export const auth = betterAuth({
  appName: "我的应用",
  plugins: [
    twoFactor({
      // TOTP 设置
      issuer: "我的应用",
      totpOptions: {
        digits: 6,
        period: 30,
      },
      // OTP 设置
      otpOptions: {
        sendOTP: async ({ user, otp }) => {
          await sendEmail({
            to: user.email,
            subject: "您的验证码",
            text: `您的码是：${otp}`,
          });
        },
        period: 5,
        allowedAttempts: 5,
        storeOTP: "encrypted",
      },
      // 备用码设置
      backupCodeOptions: {
        amount: 10,
        length: 10,
        storeBackupCodes: "encrypted",
      },
      // 会话设置
      twoFactorCookieMaxAge: 600, // 10 分钟
      trustDeviceMaxAge: 30 * 24 * 60 * 60, // 30 天
    }),
  ],
});
```
