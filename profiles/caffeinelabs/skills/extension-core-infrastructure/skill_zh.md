# 核心基础设施
核心基础设施扩展包，适用于 [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral)。

## 概述

该组件为所有项目提供基础基础设施：后端连接配置、Internet Identity 身份验证钩子以及 actor 管理工具。

## 依赖项

```
"@caffeineai/core-infrastructure": "^1.4.0"
"@caffeineai/object-storage": "^1.1.0"
"@icp-sdk/auth": "^7.1.0"
"@icp-sdk/core": "^5.3.0"
```

`@caffeineai/object-storage` 是核心基础设施的横向依赖项。每个项目都必须将其作为直接的 npm 依赖项安装（构建模板包含这两个包）。

## 集成

核心基础设施会自动包含在所有项目中。无需手动集成步骤。

# 前端

核心基础设施前端包（`@caffeineai/core-infrastructure`）会自动包含在所有项目中。

## 应用入口点

使用 `InternetIdentityProvider` 和 `QueryClientProvider` 包裹应用：

```typescript
import { InternetIdentityProvider } from "@caffeineai/core-infrastructure";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ReactDOM from "react-dom/client";
import App from "./App";

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById("root")!).render(
  <QueryClientProvider client={queryClient}>
    <InternetIdentityProvider>
      <App />
    </InternetIdentityProvider>
  </QueryClientProvider>,
);
```

## `useInternetIdentity()` — 身份验证钩子

提供 Internet Identity 的身份状态、登录和登出。

### 返回值

| 字段 | 类型 | 描述 |
|---|---|---|
| `identity` | `Identity \| undefined` | 用户的身份（登录或会话恢复后可用） |
| `login` | `(options?: LoginOptions) => void` | 打开 II 弹窗。即发即弃——不要 `await`。参见 [登录变体](#登录变体-plain-ii-google-microsoft-workspace-sso)。 |
| `clear` | `() => void` | 登出并清除存储的身份。即发即弃。 |
| `isAuthenticated` | `boolean` | 用户拥有有效身份时为 `true`。**用于 UI 控制显示。** |
| `isInitializing` | `boolean` | `AuthClient` 从 IndexedDB 加载时为 `true` |
| `isLoggingIn` | `boolean` | II 弹窗打开时为 `true` |
| `isLoginSuccess` | `boolean` | 仅在交互式登录后（页面重新加载恢复后不会）为 `true` |
| `isLoginError` | `boolean` | 登录或初始化失败时为 `true` |
| `loginError` | `Error \| undefined` | `isLoginError` 为 `true` 时的错误对象 |

### 身份验证状态生命周期

| 场景 | `loginStatus` | `isAuthenticated` |
|---|---|---|
| 页面加载，无存储会话 | `"idle"` | `false` |
| 恢复存储会话 | `"initializing"` | `false` → `true` |
| 页面重新加载后恢复存储会话 | `"idle"` | `true` |
| 交互式登录进行中 | `"logging-in"` | `false` |
| 交互式登录刚刚完成 | `"success"` | `true` |
| 登录弹窗失败/取消 | `"loginError"` | `false` |

**重要提示：** `isLoginSuccess` 仅在通过弹窗进行交互式登录后为 `true`——页面重新加载恢复存储身份时不会。始终使用 `isAuthenticated` 进行条件渲染。

### 使用方法

基于 `isAuthenticated` 控制身份验证 UI：

```typescript
const { isAuthenticated } = useInternetIdentity();

{isAuthenticated ? <AuthenticatedApp /> : <LoginScreen />}
```

初始化或登录时禁用登录按钮：

```typescript
const { login, isInitializing, isLoggingIn } = useInternetIdentity();

<button onClick={() => login()} disabled={isInitializing || isLoggingIn}>
  登录
</button>
```

`login()` 和 `clear()` 是即发即弃——钩子的状态字段（`isLoggingIn`, `isInitializing`）跟踪异步生命周期。不要将它们包裹在本地 `useState` / `isPending` 逻辑中。

### 登录变体：plain II、Google、Microsoft、工作区 SSO

`login()` 接受可选的 `LoginOptions` 对象选择用户如何登录。所有变体都通过 Internet Identity 并产生相同的身份、会话行为和登出——它们仅改变用户首先看到的屏幕：

```typescript
login();                            // plain Internet Identity 登录
login({ provider: "google" });      // 一键 Google 登录（II 直接打开 Google OAuth）
login({ provider: "microsoft" });   // 一键 Microsoft 登录（II 直接打开 Microsoft OAuth）
login({ ssoDomain: "acme.com" });   // 通过域的身份提供程序进行公司/工作区 SSO
```

- **Google**：无需 Google API 密钥或 OAuth 客户端设置——Internet Identity 处理 OAuth 流程。
- **Microsoft**：无需 Azure/Entra 应用注册——Internet Identity 拥有 OAuth 客户端。接受个人 Microsoft 账户和工作/学校账户。
- **工作区 SSO**：用户输入其公司域名（例如 `acme.com`）；Internet Identity 从 `https://<domain>/.well-known/ii-openid-configuration` 发现公司的 OpenID Connect 提供程序并登录（适用于 Okta、Entra ID 和其他公司配置的 OIDC 提供程序）。当应用需要特定公司的租户时使用此选项；使用 `provider: "microsoft"` 进行一键 Microsoft 按钮时无需公司特定设置。
- Apple 登录不提供：Internet Identity 对 Apple 返回无电子邮件或名称声明，因此属性回调将为空。
- 所有变体的会话都以相同方式存储：`isAuthenticated`、页面重新加载时恢复会话以及 `clear()` 的行为与使用的变体无关。
- 当后端使用 `caffeineai-authorization` 时，Google、Microsoft 和 SSO 登录会自动将验证的姓名/电子邮件属性（以及 SSO 域）传递给属性回调——参见 `extension-authorization` 技能。

**仅在按钮的 `onClick` 处理程序中调用 `login()`。** Internet Identity 弹窗只能在真实点击事件派发时打开；否则会失败，错误信息为 `Signer window should not be opened outside of click handler`。特别是：

- 从表单的 `onSubmit` 中永远不要调用 `login()`——`submit` 事件在点击事件完成后触发，因此检查会失败。对于 SSO 域字段，使用纯 `<div>`（不是 `<form>`）和 `type="button"` 提交按钮，其 `onClick` 验证域名并直接调用 `login({ ssoDomain })`。
- 从键盘处理程序（例如域名输入中的 Enter）或 `await` 后永远不要调用 `login()`——两者都在点击派发之外运行。

如果应用在调用 `login` 前验证 SSO 域，请镜像 Internet Identity 自己的规则：接受至少有两个标签的普通 DNS 名称（例如 `acme.com`）**或** 环回主机——`localhost` 或 `127.0.0.1`，可带可选的 `:port`（例如 `localhost:3000`）。II 接受环回域名用于本地测试，因此输入不能拒绝它们。

标准登录 UI 模式——显眼的 Google 和 Microsoft 按钮、plain II 登录以及提示输入域名的“公司 SSO”选项：

```typescript
function SignInOptions() {
  const { login, isInitializing, isLoggingIn } = useInternetIdentity();
  const [ssoDomain, setSsoDomain] = useState("");
  const disabled = isInitializing || isLoggingIn;

  return (
    <div>
      <button onClick={() => login({ provider: "google" })} disabled={disabled}>
        使用 Google 继续
      </button>
      <button onClick={() => login({ provider: "microsoft" })} disabled={disabled}>
        使用 Microsoft 继续
      </button>
      <button onClick={() => login()} disabled={disabled}>
        使用 Internet Identity 登录
      </button>
      {/* 公司 SSO：故意不是 `<form>`——login 必须在按钮的点击事件内运行，而 form onSubmit 在点击结束后触发 */}
      <input
        value={ssoDomain}
        onChange={(e) => setSsoDomain(e.target.value)}
        placeholder="yourcompany.com"
      />
      <button
        onClick={() => login({ ssoDomain: ssoDomain.trim() })}
        disabled={disabled || !ssoDomain.trim()}
      >
        使用您的公司登录
      </button>
    </div>
  );
}
```

仅提供应用实际需要的变体：默认为 plain `login()`，除非请求了 Google、Microsoft 或公司 SSO 登录。当其中之一**被**请求时，登录页面必须显示请求的直接登录选项（Google 按钮、Microsoft 按钮，和/或 SSO 域名输入），并保留一个 plain "使用 Internet Identity 登录"按钮作为后备——没有 Google 或 Microsoft 账户或注册公司域名的用户仍然必须能够登录。

## `useActor()` — 后端 Actor 钩子

创建和管理一个类型的后端 Actor 实例。当用户的身份变化（登录/登出）时，会自动重新创建 Actor。

```typescript
import { useActor } from "@caffeineai/core-infrastructure";
import { createActor } from "declarations/backend";

function MyComponent() {
  const { actor, isFetching } = useActor(createActor);

  // actor 在加载时为 null，然后是类型的后端 Actor
  if (!actor || isFetching) return <Loading />;

  // 直接调用后端方法
  const data = await actor.myBackendMethod();
}
```

### 返回值

| 字段 | 类型 | 描述 |
|---|---|---|
| `actor` | `T \| null` | 类型的后端 Actor，加载时为 `null` |
| `isFetching` | `boolean` | Actor 创建时为 `true` |

当身份变化（登录、登出或会话恢复）时，会自动使用新身份重新创建 Actor，并且所有依赖的查询都会失效并重新获取。

### 用于视觉测试的模拟后端 (`VITE_USE_MOCK=true`)

`useActor` 可以提供应用拥有的模拟，而不是连接到 canister。将模拟放在 `src/frontend/src/mocks/backend.ts`，导出 `mockBackend`，并从**应用源**传递通配符：

```typescript
import { useActor } from "@caffeineai/core-infrastructure";
import { createActor } from "declarations/backend";

const mockModules = import.meta.glob("../mocks/backend.{ts,tsx,js,jsx}");

export function useAppActor() {
  return useActor(createActor, { mockModules });
}
```

通配符必须在应用中编写，因为 Vite 相对于包含调用该函数的文件解析 `import.meta.glob`；包无法看到应用的 `mocks/` 目录。通配符而不是导入可以保持模拟文件不存在时构建为绿色。仅在 `VITE_USE_MOCK=true` 时使用模拟；否则 `useActor` 行为与之前完全相同，并且加载真实后端配置。

在 React 外部，`createActorWithConfig(createActor, { mockModules })` 接受相同的选项，`loadMockBackendFromModules(mockModules)` 会自行解析模拟。
