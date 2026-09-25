# Auth0 React 集成

使用 @auth0/auth0-react 为 React 单页应用程序添加身份验证。

---

## 前置条件

- React 16.11+ 应用程序（Vite 或 Create React App）- 支持 React 16、17、18 和 19
- 已配置 Auth0 账户和应用程序
- 如果您尚未设置 Auth0，请先使用 `auth0-quickstart` 技能

## 不应使用的情况

- **Next.js 应用程序** - 使用 `auth0-nextjs` 技能（适用于 App Router 和 Pages Router）
- **React Native 移动应用程序** - 使用 `auth0-react-native` 技能（适用于 iOS/Android）
- **服务器端渲染的 React** - 使用特定框架的 SDK（Next.js、Remix 等）
- **嵌入式登录** - 此 SDK 使用 Auth0 通用登录（基于重定向）
- **后端 API 身份验证** - 使用 express-openid-connect 或 JWT 验证

---

## 快速入门工作流

### 1. 安装 SDK

```bash
npm install @auth0/auth0-react
```

### 2. 配置环境

**使用 Auth0 CLI 自动设置**，请参阅 [设置指南](references/setup.md) 获取完整脚本。

**手动设置**：

创建 `.env` 文件：

**Vite:**
```bash
VITE_AUTH0_DOMAIN=your-tenant.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id
```

**Create React App:**
```bash
REACT_APP_AUTH0_DOMAIN=your-tenant.auth0.com
REACT_APP_AUTH0_CLIENT_ID=your-client-id
```

### 3. 使用 Auth0Provider 包裹应用程序

更新 `src/main.tsx`（Vite）或 `src/index.tsx`（CRA）：

```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { Auth0Provider } from '@auth0/auth0-react';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Auth0Provider
      domain={import.meta.env.VITE_AUTH0_DOMAIN} // 或 process.env.REACT_APP_AUTH0_DOMAIN
      clientId={import.meta.env.VITE_AUTH0_CLIENT_ID}
      authorizationParams={{
        redirect_uri: window.location.origin
      }}
    >
      <App />
    </Auth0Provider>
  </React.StrictMode>
);
```

### 4. 添加身份验证 UI

```tsx
import { useAuth0 } from '@auth0/auth0-react';

export function LoginButton() {
  const { loginWithRedirect, logout, isAuthenticated, user, isLoading } = useAuth0();

  if (isLoading) return <div>Loading...</div>;

  if (isAuthenticated) {
    return (
      <div>
        <span>欢迎，{user?.name}</span>
        <button onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}>
          退出登录
        </button>
      </div>
    );
  }

  return <button onClick={() => loginWithRedirect()}>登录</button>;
}
```

### 5. 测试身份验证

启动开发服务器并测试登录流程：

```bash
npm run dev  # Vite
# 或
npm start    # CRA
```

---

## 详细文档

- **[设置指南](references/setup.md)** - 自动设置脚本（Bash/PowerShell）、CLI 命令、手动配置
- **[集成指南](references/integration.md)** - 受保护的路由、API 调用、错误处理、高级模式
- **[API 参考](references/api.md)** - 完整 SDK API、配置选项、钩子参考、测试策略

---

## 常见错误

| 错误 | 修复 |
|------|------|
| 忘记在 Auth0 控制台添加重定向 URI | 在 Auth0 控制台的“允许的回调 URL”中添加您的应用程序 URL（例如，`http://localhost:3000`、`https://app.example.com`） |
| 使用错误的 env 变量前缀 | Vite 使用 `VITE_` 前缀，Create React App 使用 `REACT_APP_` |
| 未处理加载状态 | 在渲染依赖身份验证的 UI 前始终检查 `isLoading` |
| 在 localStorage 中存储令牌 | 不要手动存储令牌 - SDK 会自动处理安全存储 |
| 缺少 Auth0Provider 包裹 | 整个应用程序必须被 `<Auth0Provider>` 包裹 |
| Provider 未在根级别 | Auth0Provider 必须包裹所有使用身份验证钩子的组件 |
| 环境变量的导入路径错误 | Vite 使用 `import.meta.env.VITE_*`，Create React App 使用 `process.env.REACT_APP_*` |
| 使用 `acr_values` 重定向进行应用内 MFA | 使用 `useAuth0().mfa` API 进行应用内注册/挑战/验证流程 |
| 未捕获 `MfaRequiredError` | 将 `getAccessTokenSilently` 包裹在 try/catch 中并检查 `instanceof MfaRequiredError` |
| 直接向 MFA 端点发起 HTTP 调用 | 使用 `useAuth0()` 的 `mfa` 属性 - 它会自动处理令牌管理 |
| 忘记步骤升级 MFA 的刷新令牌 | 在使用 `interactiveErrorHandler="popup"` 时，在 Auth0Provider 上设置 `useRefreshTokens={true}` |

---

## 相关技能

- `auth0-quickstart` - 基本 Auth0 设置
- `auth0-migration` - 从其他身份验证提供者迁移
- `auth0-mfa` - 添加多因素身份验证
- `auth0-cli` - 从终端管理 Auth0 资源

---

## 快速参考

**核心钩子：**

- `useAuth0()` - 主要身份验证钩子
- `isAuthenticated` - 检查用户是否已登录
- `user` - 用户配置文件信息
- `loginWithRedirect()` - 启动登录
- `logout()` - 注销用户
- `getAccessTokenSilently()` - 获取用于 API 调用的访问令牌
- `mfa` - MFA API 客户端，用于注册、挑战和验证
  - `mfa.getAuthenticators(mfaToken)` - 列出已注册的身份验证器
  - `mfa.getEnrollmentFactors(mfaToken)` - 获取可用的注册因素
  - `mfa.enroll(params)` - 注册新的身份验证器（OTP、SMS、电子邮件、语音、推送）
  - `mfa.challenge(params)` - 启动 MFA 挑战
  - `mfa.verify(params)` - 验证 MFA 挑战并完成身份验证

**MFA 错误类型（从 `@auth0/auth0-react` 导入）：**

- `MfaRequiredError` - 当需要 MFA 时由 `getAccessTokenSilently` 抛出（具有 `mfa_token` 和 `mfa_requirements`）
- `MfaEnrollmentError`, `MfaChallengeError`, `MfaVerifyError` - 分别由 `mfa.*` 方法抛出

**常见用例：**

- 登录/退出登录按钮 → 见上述第 4 步
- 受保护的路由 → [集成指南](references/integration.md#protected-routes)
- 带令牌的 API 调用 → [集成指南](references/integration.md#calling-apis)
- 错误处理 → [集成指南](references/integration.md#error-handling)
- MFA 处理 → [集成指南](references/integration.md#mfa-handling)

---

## 参考

- [Auth0 React SDK 文档](https://auth0.com/docs/libraries/auth0-react)
- [Auth0 React 快速入门](https://auth0.com/docs/quickstart/spa/react)
- [SDK GitHub 仓库](https://github.com/auth0/auth0-react)
