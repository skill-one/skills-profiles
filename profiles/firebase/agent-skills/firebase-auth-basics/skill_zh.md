## 前提条件

- **Firebase 项目**：通过
  `npx -y firebase-tools@latest projects:create`（详见 `firebase-basics`）。
- **Firebase CLI**：已安装并登录（详见 `firebase-basics`）。

## 核心概念

Firebase 认证为用户提供后端服务、易于使用的 SDK 以及现成的 UI 库，以实现向您的应用认证用户。

### 用户

用户是您应用中可以登录的实体。每个用户由一个唯一的 ID（`uid`）标识，该 ID 在所有提供商中均保证唯一。用户属性包括：

- `uid`：唯一标识符。
- `email`：用户邮箱地址（如有）。
- `displayName`：用户显示名称（如有）。
- `photoURL`：用户照片的 URL（如有）。
- `emailVerified`：布尔值，表示邮箱是否已验证。

### 身份提供商

Firebase 认证支持多种登录方式：

- **Email/Password**：基础的邮箱和密码认证。
- **Federated Identity Providers**：Google、Facebook、Twitter、GitHub、Microsoft、Apple 等。
- **Phone Number**：基于短信的认证。
- **Anonymous**：临时访客账户，后续可关联到永久账户。
- **Custom Auth**：与您现有的认证系统集成。

Google Sign In 是推荐使用的良好且安全的默认提供商。

### 令牌

用户登录时，会收到一个 ID Token（JWT）。该令牌在向 Firebase 服务（实时数据库、云存储、Firestore）或您自己的后端发送请求时，用于识别用户。

- **ID Token**：短期（1小时），用于验证身份。
- **Refresh Token**：长期有效，用于获取新的 ID Token。

## 工作流

### 1. 配置

#### 选项 1：通过 CLI 启用认证

仅支持通过 CLI 启用 Google Sign In、匿名认证和邮箱/密码认证。对于其他提供商，请使用 Firebase 控制台。

在 `firebase.json` 中添加一个 `auth` 代码块，以配置 Firebase 认证：

```
{
  "auth": {
  "authorizedDomains": ["localhost"],
    "providers": {
      "anonymous": true,
      "emailPassword": true,
      "googleSignIn": {
        "oAuthBrandDisplayName": "Your Brand Name",
        "supportEmail": "support@example.com"
      }
    }
  }
}
```


[!NOTE] 如果 Google Sign-In 弹窗打开后立即以错误 `[firebase_auth/unauthorized-domain]` 关闭，这意味着该域名未获得授权。对于本地开发，请确保 `localhost` 包含在 Firebase 控制台的 **Authorized Domains**（授权域名列表）中，或在 `firebase.json` 的 `authorizedDomains` 字段中配置。**CRITICAL**：切勿在授权域名列表中包含协议或端口号（例如，使用 `localhost`，而不是 `http://localhost:9090`）。

**CRITICAL**：配置 `firebase.json` 后，必须将认证配置部署到 Firebase 后端，否则更改不会生效。这对于 Google Sign In、邮箱/密码等认证提供商自动为您的应用平台生成必要的 OAuth 客户端至关重要。请运行：

```bash
npx -y firebase-tools@latest deploy --only auth
```

#### 选项 2：在控制台中启用认证

在 Firebase 控制台中启用其他提供商。

1. 前往
   https://console.firebase.google.com/project/_/authentication/providers
1. 选择您的项目。
1. 启用所需的登录提供商（例如，邮箱/密码、Google）。

### 2. 客户端设置与使用

**Web**：详见 [references/client_sdk_web.md](references/client_sdk_web.md)。

**Flutter**：详见 [references/flutter_setup.md](references/flutter_setup.md)。
**Android (Kotlin)**：详见
[references/client_sdk_android.md](references/client_sdk_android.md)。

### 3. 安全规则

使用 Firestore/存储规则中的 `request.auth` 来保护您的数据。
详见 [references/security_rules.md](references/security_rules.md)。
