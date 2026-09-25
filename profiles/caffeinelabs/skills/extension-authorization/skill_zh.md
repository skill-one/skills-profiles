# 授权
为 [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral) 提供授权扩展。

## 概述

此技能通过 mixin 模式添加了一个基于角色的访问控制的认证和授权系统。`MixinAuthorization` mixin 自动提供标准的授权端点。

# 后端

基于角色的访问控制的认证系统。

存在一个预制库 `mo:caffeineai-authorization/access-control.mo`。它提供基于角色的访问控制的核心认证。

## 模块 API

```mo:caffeineai-authorization/access-control.mo
module {
  public type UserRole = {
    #admin;
    #user;
    #guest;
  };

  public type AccessControlState = { /* 内部状态 */ };

  public func initState() : AccessControlState;
  public func getUserRole(state : AccessControlState, caller : Principal) : UserRole;
  public func assignRole(state : AccessControlState, caller : Principal, user : Principal, role : UserRole);
  public func isAdmin(state : AccessControlState, caller : Principal) : Bool;
  public func hasPermission(state : AccessControlState, caller : Principal, requiredRole : UserRole) : Bool;
};
```

初始化由 `MixinAuthorization` 内部处理——不要直接调用 `initialize`。第一个登录的用户自动成为管理员；不需要令牌或密钥。

**重要提示**：`include MixinAuthorization(accessControlState)` 行**必须**放置在 `main.mo` 中，而不是在自定义 mixin 文件中。

## 选择退出/自定义认证

如果用户要求用自定义认证系统替换此授权系统（例如用户名/密码认证、无 Internet Identity 或无 `MixinAuthorization`），请从项目中移除 `caffeineai-authorization` mops 包。这是移除 `include-authorization` lint 要求的唯一支持方式，因为该 lint 规则由该包提供。不要添加抑制注释或在省略 `include MixinAuthorization(accessControlState)` 的情况下保留该包。

移除包时，还需删除所有 `mo:caffeineai-authorization/*` 导入、`accessControlState` 初始化、`include MixinAuthorization(accessControlState)` 以及属于此组件的任何 `AccessControl` 守卫调用。用用户请求的自定义认证和授权检查来替换它们。

## 在 main.mo 中设置

```motoko filepath=src/backend/main.mo
import Map "mo:core/Map";
import Principal "mo:core/Principal";
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import Types "types";
import ProfileMixin "mixins/Profile";

actor {
  let accessControlState : AccessControl.AccessControlState;
  include MixinAuthorization(accessControlState, null);

  let userProfiles : Map.Map<Principal, Types.UserProfile>;

  include ProfileMixin(accessControlState, userProfiles);
};
```

迁移链头：

```motoko filepath=src/backend/migrations/00000000_000000.mo
import Map "mo:core/Map";
import AccessControl "mo:caffeineai-authorization/access-control";

module {
  type UserProfile = {
    name : Text;
  };

  type NewActor = {
    accessControlState : AccessControl.AccessControlState;
    userProfiles : Map.Map<Principal, UserProfile>;
  };

  public func migration(_old : {}) : NewActor {
    {
      accessControlState = AccessControl.initState();
      userProfiles = Map.empty<Principal, UserProfile>();
    };
  };
};
```

## types.mo 中的类型定义

```motoko filepath=src/backend/types.mo
module {
  public type UserProfile = {
    name : Text;
  };
};
```

## 自定义 Mixin 示例 (mixins/Profile.mo)

前端需要 `getCallerUserProfile`、`saveCallerUserProfile` 和 `getUserProfile`。将 `accessControlState` 传递给您的 mixin，以便它可以检查权限。

```motoko filepath=src/backend/mixins/Profile.mo
import Map "mo:core/Map";
import Principal "mo:core/Principal";
import Runtime "mo:core/Runtime";
import AccessControl "mo:caffeineai-authorization/access-control";
import Types "../types";

mixin (
  accessControlState : AccessControl.AccessControlState,
  userProfiles : Map.Map<Principal, Types.UserProfile>,
) {
  public query ({ caller }) func getCallerUserProfile() : async ?Types.UserProfile {
    if (not AccessControl.hasPermission(accessControlState, caller, #user)) {
      Runtime.trap("Unauthorized");
    };
    userProfiles.get(caller);
  };

  public shared ({ caller }) func saveCallerUserProfile(profile : Types.UserProfile) : async () {
    if (not AccessControl.hasPermission(accessControlState, caller, #user)) {
      Runtime.trap("Unauthorized");
    };
    userProfiles.add(caller, profile);
  };

  public query ({ caller }) func getUserProfile(user : Principal) : async ?Types.UserProfile {
    if (caller != user and not AccessControl.isAdmin(accessControlState, caller)) {
      Runtime.trap("Unauthorized: Can only view your own profile");
    };
    userProfiles.get(user);
  };
};
```

## 守卫模式

对每个公共函数应用适当的守卫：

```
// 仅管理员：
if (not AccessControl.hasPermission(accessControlState, caller, #admin)) {
  Runtime.trap("Unauthorized: Only admins can perform this action");
};

// 仅用户：
if (not AccessControl.hasPermission(accessControlState, caller, #user)) {
  Runtime.trap("Unauthorized: Only users can perform this action");
};

// 任何用户（包括访客）：无需检查
```

## 设计指南

- 匿名主 Prinicipal 被视为访客。
- `assignRole` 内部包含一个仅管理员守卫。
- 使用 `shared({ caller })` 对于修改数据的认证端点。
- 使用 `query({ caller })` 对于获取数据的认证端点。
- 在需要时处理所有权验证。
- 使用 `Runtime.trap` 处理授权失败。

## 电子邮件属性

`MixinAuthorization` 可以在登录时捕获用户的已验证 Internet Identity 属性（姓名和电子邮件）。将回调作为第二个参数传递，而不是 `null`；它在每次登录后运行一次，在属性包验证后运行。

**不要**直接使用 `mo:identity-attributes` mixin——始终通过 `MixinAuthorization` 使用。回调接收调用者主 Prinicipal 和已验证的属性：

```
{
  name : ?Text;   // 验证的显示名称，当存在时
  email : ?Text;  // 始终是已验证的地址——源自 II 的 `verified_email`，从不读取未验证的 `email` 键
  sso : ?Text;    // 当身份来自 SSO 时 SSO 域，否则为 null
}
```

字段名为 `email`，但它只包含 II 的 `verified_email` 值——从不读取未验证的 `email` 键。在回调中使用 `attrs.email`（没有 `attrs.verified_email` 字段）。

哪些属性到达取决于前端使用的登录变体（有关完整 API 和 UI 模式的详细信息，请参阅 `extension-core-infrastructure` 技能中的 `extension-authorization`-兼容 `login()` 选项）：

- `login()`（普通 Internet Identity）：当用户在 II 中有验证电子邮件时 `email` 存在；`sso` 为 null。
- `login({ provider: 'google' })`：来自用户 Google 账户的验证 `name` 和 `email`；`sso` 为 null。
- `login({ provider: 'microsoft' })`：来自用户 Microsoft 账户的验证 `name` 和 `email`；`sso` 为 null。
- `login({ ssoDomain: 'acme.com' })`：来自公司身份提供者的验证 `name` 和 `email`；`sso` 包含域（例如 `"acme.com"`）。使用 `attrs.sso` 来限制公司成员功能或按域自动分配角色。

将它们存储在您自己的状态中，并暴露一个 getter 来读取它们：

<!-- motoko-check:skip -->
```motoko
import Map "mo:core/Map";
import Principal "mo:core/Principal";
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";

actor {
  let accessControlState : AccessControl.AccessControlState;

  let emails : Map.Map<Principal, Text>;

  include MixinAuthorization(
    accessControlState,
    ?(func(caller : Principal, attrs : { name : ?Text; email : ?Text; sso : ?Text }) {
      switch (attrs.email) {
        case (?email) { emails.add(caller, email) };
        case null {};
      };
    }),
  );

  public query ({ caller }) func getCallerEmail() : async ?Text {
    emails.get(caller);
  };
};
```

`trusted_attribute_signers` 和 `frontend_origins` canister 环境变量用于属性验证，由 Caffeine 平台自动配置——您无需设置它们。

### 前端获取电子邮件

登录后，像其他认证演员方法一样查询获取器：

```typescript
const { data: callerEmail } = useQuery<string | null>({
  queryKey: ['callerEmail'],
  queryFn: () => actor.getCallerEmail(),
  enabled: !!actor && isAuthenticated,
});
```

# 前端

基于角色的访问控制的认证系统。

## 登录选项

登录通过 `@caffeineai/core-infrastructure` 的 `useInternetIdentity` 钩子进行（有关完整 API 和 UI 模式的详细信息，请参阅 `extension-core-infrastructure` 技能）。默认为普通 `login()`，除非请求了 Google、Microsoft 或公司/工作区 SSO 登录。

规则：

- 当请求 Google、Microsoft 或 SSO 登录时，登录屏幕必须显示请求的直接选项（Google 按钮、Microsoft 按钮和/或 SSO 域输入）**并且**保留一个普通的 `login()` “使用 Internet Identity 登录”按钮作为后备——没有 Google 或 Microsoft 账户或注册公司域的用户仍然必须能够登录。
- 永远不要从已经拥有用户的现有应用中移除 Internet Identity 选项。主 Prinicipal 来自用户的 Internet Identity：一个 II 身份由 Google 或 Microsoft 支持的用户通过任一按钮获得**相同的**主 Prinicipal，但使用基于 passkey 的 II 身份注册的用户如果使用与该身份未链接的 Google 或 Microsoft 账户进行认证，则获得**不同的**主 Prinicipal——他们的数据将显示为丢失。保留两个按钮可以让每个现有用户以他们一直以来的方式登录。

## 用户资料设置

使用 Internet Identity 时，用户只有在登录后才能获得主 Prinicipal id。匿名主 Prinicipal 被视为访客。主 Prinicipal id 不可读——在用户使用新的主 Prinicipal 首次登录时请求他们的姓名。

后端资料 API：

- `getCallerUserProfile(): Promise<UserProfile | null>` -- 如果没有资料则返回 `null`
- `saveCallerUserProfile(profile: UserProfile): Promise<void>` -- 保存姓名和资料数据
- `getUserProfile(user: Principal): Promise<UserProfile | null>` -- 获取其他用户的资料

规则：

- 登录时，如果用户已经拥有资料，不要再次请求姓名
- 显示用户的资料姓名，而不是主 Prinicipal id
- 确保用户必须在登录后才能看到任何应用数据
- 登出时，清除所有缓存的 应用数据，包括缓存的用户资料

### 防止资料设置模态闪烁

```typescript
export function useGetCallerUserProfile() {
  const { actor, isFetching: actorFetching } = useActor();

  const query = useQuery<UserProfile | null>({
    queryKey: ['currentUserProfile'],
    queryFn: async () => {
      if (!actor) throw new Error('Actor not available');
      return actor.getCallerUserProfile();
    },
    enabled: !!actor && !actorFetching,
    retry: false,
  });

  return {
    ...query,
    isLoading: actorFetching || query.isLoading,
    isFetched: !!actor && query.isFetched,
  };
}
```

然后在您的组件中：
```typescript
const showProfileSetup = isAuthenticated && !profileLoading && isFetched && userProfile === null;
```

## 认证状态生命周期

`useInternetIdentity` 钩子暴露了两种状态——使用正确的一种：

| 情景 | `loginStatus` | `isAuthenticated` |
|---|---|---|
| 页面加载，没有存储的会话 | `"idle"` | `false` |
| 页面加载，恢复存储的会话 | `"initializing"` | `false` → `true` |
| 存储的会话在重新加载后恢复 | `"idle"` | `true` |
| 交互式登录正在进行中（弹出窗口打开） | `"logging-in"` | `false` |
| 交互式登录刚刚完成 | `"success"` | `true` |
| 登录弹出窗口失败/取消 | `"loginError"` | `false` |

**重要提示**：`isLoginSuccess` (`loginStatus === "success"`) 仅在通过弹出窗口进行交互式登录后为 `true`。当页面重新加载时恢复存储的身份时，它**不是** `true`。永远不要使用 `isLoginSuccess` 来区分认证和未认证的 UI——始终使用 `isAuthenticated`。

登录按钮的关键状态：

- `isInitializing` — `AuthClient` 正在从 IndexedDB 加载；禁用按钮以防止在客户端准备好之前点击。
- `isLoggingIn` — II 弹出窗口已打开；禁用按钮以防止重复弹出窗口。

## 登录组件

```typescript
import { useInternetIdentity } from '@caffeineai/core-infrastructure';
import { useQueryClient } from '@tanstack/react-query';

export default function LoginButton() {
  const { login, clear, isAuthenticated, isInitializing, isLoggingIn } = useInternetIdentity();
  const queryClient = useQueryClient();

  const handleAuth = () => {
    if (isAuthenticated) {
      clear();
      queryClient.clear();
    } else {
      login();
    }
  };

  return (
    <button
      onClick={handleAuth}
      disabled={isInitializing || isLoggingIn}
      className={`px-6 py-2 rounded-full transition-colors font-medium ${
        isAuthenticated
          ? 'bg-gray-200 hover:bg-gray-300 text-gray-800'
          : 'bg-blue-600 hover:bg-blue-700 text-white'
      } disabled:opacity-50`}
    >
      {isInitializing ? 'Loading...' : isAuthenticated ? 'Logout' : 'Login'}
    </button>
  );
}
```

`login()` 和 `clear()` 函数是“发射即忘”（它们不返回跟踪完整流程的 Promise）。钩子的 `isLoggingIn` / `isInitializing` 状态跟踪异步生命周期——**不要**将它们包装在本地 `useState` / `isPending` 逻辑中。

当应用请求 Google 或 Microsoft 登录或公司/工作区 SSO 时，使用相同的钩子并传递选项：`login({ provider: 'google' })`、`login({ provider: 'microsoft' })` 或 `login({ ssoDomain: 'acme.com' })`。所有变体都产生相同的身份和会话行为；有关完整登录 UI 模式，请参阅 `extension-core-infrastructure` 技能。

在 `isAuthenticated` 上限制认证 UI（涵盖新鲜登录和页面重新加载时恢复的会话）：
```typescript
{isAuthenticated ? (
  <AuthenticatedApp />
) : (
  <LoginScreen />
)}
```

## 当前用户与数据作者的比较

```typescript
import { useInternetIdentity } from '@caffeineai/core-infrastructure';
import type { Principal } from '@icp-sdk/core/principal';

const { identity } = useInternetIdentity();

const isAuthor = (authorPrincipal: Principal): boolean => {
  if (!identity) return false;
  return authorPrincipal.toString() === identity.getPrincipal().toString();
};
```

## 访问控制 UI

对于仅管理员或个人应用，当未授权用户尝试访问应用时，显示 `AccessDeniedScreen` 组件。

## 错误处理

在 UI 中优雅地处理来自后端 `Debug.trap` 调用的授权错误，向用户显示适当的错误消息。

注意：第一个管理员的初始化在 `@caffeineai/core-infrastructure` 中自动完成。第一个登录的认证用户成为管理员；不需要令牌或密钥。
