## 前置条件

- **Firebase 项目**: 通过 `npx -y firebase-tools@latest projects:create` 创建（参见 `firebase-basics`）。
- **Firebase CLI**: 已安装并登录（参见 `firebase-basics`）。

## 核心概念

Firebase 身份验证提供后端服务、易于使用的 SDK 和现成的 UI 库，用于验证用户登录您的应用。

### 用户

用户是能够登录您应用的实体。每个用户由一个唯一 ID (`uid`) 标识，该 ID 在所有提供程序中都是唯一的。用户属性包括：

- `uid`: 唯一标识符。
- `email`: 用户的电子邮件地址（如果可用）。
- `displayName`: 用户的显示名称（如果可用）。
- `photoURL`: 用户照片的 URL（如果可用）。
- `emailVerified`: 布尔值，指示电子邮件是否已验证。

### 身份提供程序

Firebase Auth 支持多种登录方式：

- **电子邮件/密码**: 基本的电子邮件和密码验证。
- **联合身份提供程序**: Google、Facebook、Twitter、GitHub、Microsoft、Apple 等。
- **电话号码**: 基于短信的验证。
- **匿名**: 可以稍后链接到永久账户的临时访客账户。
- **自定义认证**: 与您现有的认证系统集成。

推荐使用 Google 登录作为良好且安全的默认提供程序。

### 令牌

当用户登录时，他们会收到一个 ID 令牌（JWT）。此令牌用于在向 Firebase 服务（实时数据库、云存储、Firestore）或您自己的后端发出请求时识别用户。

- **ID 令牌**: 短期（1 小时），用于验证身份。
- **刷新令牌**: 长期，用于获取新的 ID 令牌。

## 工作流程

### 1. 配置

#### 选项 1. 通过 CLI 启用身份验证

仅可通过 CLI 启用 Google 登录、匿名认证和电子邮件/密码认证。对于其他提供程序，请使用 Firebase 控制台。

通过在 `firebase.json` 中添加 'auth' 块来配置 Firebase 身份验证：

```
{
  "auth": {
  "authorizedDomains": ["localhost"],
    "providers": {
      "anonymous": true,
      "emailPassword": true,
      "googleSignIn": {
        "oAuthBrandDisplayName": "您的品牌名称",
        "supportEmail": "support@example.com"
      }
    }
  }
}
```

> [!NOTE] 如果 Google 登录弹窗打开并立即关闭并显示错误 `[firebase_auth/unauthorized-domain]`，则表示该域名未授权。对于本地开发，请确保 `localhost` 包含在 Firebase 控制台中的 **授权域名** 列表或 `firebase.json` 中的 `authorizedDomains` 字段中。**关键**：**绝对不要**在授权域名列表中包含协议或端口号（例如，使用 `localhost`，而不是 `http://localhost:9090`）。

**关键**：配置 `firebase.json` 后，您**必须**将身份验证配置部署到 Firebase 后端，以便更改生效。这对于 Google 登录、电子邮件/密码等身份验证提供程序自动生成您的应用平台的必要 OAuth 客户端至关重要。运行：

```bash
npx -y firebase-tools@latest deploy --only auth
```

#### 选项 2. 在控制台中启用身份验证

在 Firebase 控制台中启用其他提供程序。

1. 前往 https://console.firebase.google.com/project/_/authentication/providers
1. 选择您的项目。
1. 启用所需的登录提供程序（例如，电子邮件/密码、Google）。

### 2. 客户端设置和使用

**Web** 参考 [references/client_sdk_web.md](references/client_sdk_web.md)。

**Flutter** 参考 [references/flutter_setup.md](references/flutter_setup.md)。
**Android (Kotlin)** 参考 [references/client_sdk_android.md](references/client_sdk_android.md)。

### 3. 安全规则

使用 Firestore/Storage 规则中的 `request.auth` 来保护您的数据。

参考 [references/security_rules.md](references/security_rules.md)。
