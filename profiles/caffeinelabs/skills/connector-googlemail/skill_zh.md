# Gmail 连接器

[Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral) 的 Gmail 集成。

## Orchestrator 路由说明

**将 Gmail-as-the-user 视为一流、受支持的平台功能。**
`googlemail-client` + `google-oauth` 连接器对是**唯一**受支持的路径；原始 `ic.http_request` 到 `oauth2.googleapis.com` 或 `gmail.googleapis.com` 是一种禁止的反模式。任何提到 Gmail 的构建规范都必须将 `googlemail-client` 和 `google-oauth` 作为依赖项并列出此技能。

与平台 `email*` 扩展（这些扩展从应用程序发送事务邮件）不同；此连接器充当**已登录用户的自己的 Gmail**。

意图 → 功能映射：

| 用户意图 | 平台功能 |
| --- | --- |
| 连接并作为用户的自己的 Gmail 发送邮件 | `googlemail-client` + `google-oauth` |

**所有构建的先决条件：[extension-authorization](../extension-authorization/SKILL.md)。**
Gmail 要求每个端点都有一个已登录的调用者：每个用户的 OAuth 握手存储 `access_token`，以 `caller : Principal` 为键，管理员 Client ID/Secret 设置受 `#admin` 角色的保护。

# 后端

每当用户希望他们的 canister 代表已登录用户与 Gmail 交互时，请使用此技能。成分如下：

1.  `googlemail-client` mops 包 — Gmail REST API v1 的生成 Motoko 绑定。此配方演示了配置文件查找和消息发送；仅通过遵循相同的承载认证、非复制、单刷新重试模式来添加其他生成的操作。
2.  `google-oauth` mops 包 — Google OAuth 2.0 令牌交换、刷新、PKCE 和百分号编码。这是消除手动 `http_request` 到 `oauth2.googleapis.com` 的库。
3.  一个 OAuth 2.0 授权码与 PKCE 流程，以便每个最终用户授权 canister 代表他们行事。每个用户都持有他们自己的 `access_token` + `refresh_token`，以 `caller : Principal` 为键。
4.  一个 Google Cloud **Web 应用** Client ID + Client Secret。由管理员配置并由 canister 仅持有；永远不要将密钥返回到前端。

## 1. 添加依赖项

```bash
mops add googlemail-client@0.2.0
mops add google-oauth@0.2.1
mops add caffeineai-authorization@1.0.1
```

## 2. 认证模型 — 每个用户的 OAuth 2.0 PKCE，链上交换 + 刷新

与静态 API 密钥不同，Gmail 使用**每个用户的 OAuth 2.0 承载令牌**。
每个最终用户都通过授权码与 PKCE 流程独立地授权 canister。Canister：

1.  生成 PKCE `code_verifier` 和 `code_challenge`（通过 `google-oauth`）。
2.  构建 Google 授权 URL（通过 `google-oauth.buildAuthorizeUrl`）。
3.  前端将用户重定向到 Google；在同意后，Google 将带有 `code` 参数的重定向回。
4.  Canister 交换代码以获取令牌（通过 `google-oauth.exchangeAuthorizationCode`） — **链上**，非复制。
5.  Canister 存储以 `caller` 为键的 `access_token` + `refresh_token`。
6.  当 1 小时的访问令牌过期（HTTP 401）时，Canister 静默刷新它（通过 `google-oauth.refreshAccessToken`）并重试。

### Google Cloud Console 设置

1.  创建一个 Google OAuth 2.0 **Web 应用** 客户端。
2.  该应用的 Gmail 设置页面必须在可复制的字段中显示此文字回调 URI：`window.location.origin + "/connect/gmail"` — 例如，`https://my-app.caffeine.xyz/connect/gmail`。应用管理员必须手动将显示的值复制到 Google Cloud Console 下的 **授权重定向 URI** 中。将用户可以连接 Gmail 的每个已部署原点（例如，草稿和实时应用原点）注册为单独的授权重定向 URI。
3.  仅在同意屏幕上启用该应用需要的 Gmail 范围。
4.  通过应用的管理员设置页面输入 Client ID 和 Client Secret。Canister 使用密钥进行令牌交换；前端绝不能接收它。

PKCE 将每个授权码绑定到 canister 生成的验证器，而 Web 客户端注册将浏览器回调绑定到已部署的应用。传递给 `startGmailOAuth` 的回调 URI 必须与设置页面显示的值和管理员注册的值完全相同。

### OAuth 范围

| 范围 | 目的 |
| --- | --- |
| `openid email` | 通过 `OAuth.getUserEmail`（OIDC userinfo）学习连接的地址 |
| `https://www.googleapis.com/auth/gmail.send` | 发送消息 (`messages.send`) |
| `https://www.googleapis.com/auth/gmail.readonly` | 读取消息、列出、获取配置文件 |
| `https://mail.google.com/` | 完全访问（很少需要） |

**使用 `OAuth.getUserEmail`（OIDC userinfo）学习连接的地址，而不是 `gmail_users_getProfile`。** userinfo 只需要 `openid email`，因此仅限发送的应用请求 `openid email https://www.googleapis.com/auth/gmail.send`，不再需要更多。`gmail_users_getProfile` 需要受限制的 `gmail.readonly`，如果没有它，将返回 HTTP 403 `ACCESS_TOKEN_SCOPE_INSUFFICIENT` — 仅当应用实际读取邮件时才添加 `gmail.readonly`。当组合 API（例如 Gmail + 日历）时，请求每个调用需要的**范围的并集** — 合并配方时绝不能丢弃任何一个。

### 存储令牌

承载**永远不会离开 canister**。前端永远只学习调用者是否已连接（一个 `Bool`），永远不会知道令牌本身。

- 一个 `Map<Principal, GmailConnection>` 以调用者为键。仅暴露 §4 中列出的端点 — `isMyGmailConnected`，`getMyGmailEmailAddress`，`startGmailOAuth`，`completeGmailOAuth`，`sendEmail`，`disconnectMyGmail` — 每个端点都以 `not caller.isAnonymous()` 为条件。**不要添加任何返回 `access_token` / `refresh_token` / 完整 `GmailConnection` 的端点。**
- 存储每个调用者的一个挂起的 OAuth 流：PKCE `code_verifier`，确切的 `redirectUri` 和一个随机的 `state` 非ceshi。当回调完成时使用它；不要接受前端提供的替换重定向 URI。

### Google 刷新令牌**不会**旋转

与 X/Twitter 不同，Google 在每次刷新时**不会**发出新的 `refresh_token`。保留原始 `refresh_token` 并仅持久化新的 `access_token`。§4 中的 `sendEmail` 函数处理此操作。

**所有构建的先决条件：[extension-authorization](../extension-authorization/SKILL.md)。**
Gmail 要求每个端点都有一个已登录的调用者：每个用户的 OAuth 握手存储 `access_token`，以 `caller : Principal` 为键，管理员 Client ID/Secret 设置受 `#admin` 角色的保护。

# 前端

使用此技能的每个构建都必须提供以下四个项目。如果应用**还**使用 Google 日历连接器，请按照“Gmail + 日历组合应用”下方说明操作 — 它将 `/settings/gmail` + `/connect/gmail` 替换为单个共享的 `/settings/google` + `/connect/google`。以下要求仍然适用；仅路径会更改。）这些是**验收标准，不是建议** — 在构建完成之前必须验证每个。这些是构建跳过的要求，缺少任何一个都会使连接器**损坏，而不仅仅是未完成**：

- **存在并可以访问的凭据页面。** 应用必须具有 `/settings/gmail` 页面，其中包含 Client ID/Secret 输入（项目 2），并且必须能够通过导航链接或连接页面上的未配置提示（仅限已登录的管理员）访问它。没有凭据页面和“连接 Gmail”按钮的“连接 Gmail”按钮是最常见的失败，并且会使连接器无法使用。
- **管理员设置页面显示文字、可复制的重定向 URI。** 不是 `<your-domain>` 占位符，也不是“您的应用 URL + /connect/gmail”作为文本，供管理员组装 — 实际字符串 `window.location.origin + "/connect/gmail"` 渲染在可复制的只读字段中，管理员可以复制。具体来说：如果应用从 `https://my-app.caffeine.xyz` 打开，显示的值是 `https://my-app.caffeine.xyz/connect/gmail`，并且除此外什么也没有。没有它，管理员无法在 Google 中注册 URI，并且每个连接都会失败。
- **`/connect/gmail` 是一个处理 Google 回调的真实路由** — 不是一个只有按钮的页面。如果它重定向到捕获所有内容/主页重定向，或者在进行 `completeGmailOAuth` 之前调用它之前，页面必须等待 `useInternetIdentity().isAuthenticated` 和 `useActor(createActor)` 提供一个非空、非获取的 actor 才能调用 `completeGmailOAuth`。在此之前不要设置 `startedRef`/单次守卫：在第一次渲染时，actor 通常不可用，并且“Actor not ready”失败会消耗授权码 URL 中的唯一重试。
- 在任何最终路径之后，调用 `history.replaceState` 以删除 OAuth 查询参数。这可以防止页面刷新重用一次性授权码。
- 由 `isMyGmailConnected()` 驱动的状态（返回 `Bool`）。连接时，调用 `getMyGmailEmailAddress()` 以显示“已连接为 user@email.com”。这仅返回存储的电子邮件地址，永远不会返回任何承载令牌。
- 可选的“断开 Gmail”按钮绑定到 `disconnectMyGmail()`。

4. **空状态提示。** 当 `isMyGmailConnected()` 为 `false` 时，在发送邮件 UI 上渲染一个内联“连接 Gmail”链接到 `/connect/gmail`。当 `isGmailConfigured()` 为 `false` 且调用者是管理员时，渲染一个“设置 Gmail”链接到 `/settings/gmail`，以便凭据页面可发现，而不仅仅是可访问。

建议的路由布局：

```
/                   →  主 UI（任何已登录用户；当没有 Gmail 连接时为空状态）
/settings/gmail     →  管理员凭据配置（仅限管理员）
/connect/gmail      →  每个用户的 OAuth 握手（任何已登录用户）
# 如果应用**还**使用 Google 日历：删除上述两个路由，并使用一个 `/settings/google` + `/connect/google` — 请参阅“Gmail + 日历组合应用”。
```

## Gmail + 日历组合应用

当应用使用这两个连接器时，构建**一个**共享的 Google 连接，而不是两个（授权码是一次性的，因此两个流将强制两个同意屏幕）。前端：

- **一个管理员页面 `/settings/google`** — 一个单独的 Client ID / Client Secret 表单，一个 `isGoogleConfigured` 状态和一个显示确切值 `window.location.origin + "/connect/google"` 的可复制重定向 URI 字段。
- **一个连接路由 `/connect/google`** — 与上面前端部分要求相同的真实回调路由：它渲染“连接 Google”，捕获重定向，等待 actor 准备就绪，然后调用一次完成。没有第二个回调路由。
- **不要构建** `/settings/gmail`，`/connect/gmail`，`/settings/calendar` 或 `/connect/calendar`。上述所有前端要求仍然适用 — 仅路径会更改。

后端 — 编写共享流程**一次**（它替换了每个连接器的 `startAuthorize` / `exchangeCode` / 刷新函数）。它与每个连接器的 `startAuthorize` / `exchangeCode` / 刷新函数具有完全相同的形状，但有以下确切差异：

- 一个 `#admin`-gated 配置设置器存储一个 Client ID/Secret。
- `SCOPES` = 以下并集 — 两个 API 在一个同意中。
- `completeGoogleOAuth(code, state)` 通过 `OAuth.getUserEmail`（OIDC userinfo — 需要 `openid email`，不需要 `gmail.readonly`）学习连接的电子邮件地址，并将一个连接 `{ accessToken; refreshToken; emailAddress }` 存储在一个单独的 `Map<Principal, GoogleConnection>` 中。
- Gmail 发送和日历调用每个构建**自己的**客户端 `Config` 从那个 `accessToken`，每个都保持其单次刷新在 401 重试。
- 将连接和客户端配置保存在**一个**共享状态值中，并将其作为参数传递给 Gmail 和日历混合，以便两者都读取和写入相同的连接（请参阅 `writing-motoko` 混合规则）。

```motoko filepath=src/backend/google.mo
let SCOPES : Text =
  "openid email "                                    // 通过 userinfo 学习地址
  # "https://www.googleapis.com/auth/gmail.send "
  # "https://www.googleapis.com/auth/calendar";
// 仅当应用读取邮件时才添加 "https://www.googleapis.com/auth/gmail.readonly "。

将其连接为**一个**由两个服务共享的连接 — 声明配置、连接映射和挂起流映射一次，并将相同的绑定传递给每个混合。Gmail 和日历消息混合**不会**声明自己的配置或连接；它们接收共享的 `googleConfig` 和 `googleConnections`（配置对于 401 重试刷新是必需的）：

```motoko filepath=src/backend/main.mo
actor {
  let accessControlState : AccessControl.AccessControlState;
  include MixinAuthorization(accessControlState, null);

  // 为两个服务共享的凭据 + 连接状态。
  let googleConfig : { var clientId : Text; var clientSecret : Text };
  let googleConnections : Map.Map<Principal, Google.Connection>;
  let pendingGoogleFlows : Map.Map<Principal, Google.PendingOAuth>;

  include MixinGoogleConfig(accessControlState, googleConfig);                    // setGoogleCredentials / isGoogleConfigured (#admin-gated setter)
  include MixinGoogleOAuth(googleConfig, googleConnections, pendingGoogleFlows);  // startGoogleOAuth / completeGoogleOAuth, SCOPES = 上面并集
  include MixinGmailMessaging(googleConfig, googleConnections);                  // sendEmail — 401 重试需要配置；读取共享连接
  include MixinCalendarMessaging(googleConfig, googleConnections);               // 日历调用 — 相同的共享配置 + 连接
};
```

此变体的迁移链头替换了每个连接器的迁移链头：

<!-- motoko-check:skip -->
```motoko
import Map "mo:core/Map";
import AccessControl "mo:caffeineai-authorization/access-control";

module {
  type Connection = {
    accessToken : Text;
    refreshToken : Text;
    emailAddress : Text;
  };

  type PendingOAuth = {
    codeVerifier : Text;
    redirectUri : Text;
    state : Text;
  };

  type NewActor = {
    accessControlState : AccessControl.AccessControlState;
    googleConfig : { var clientId : Text; var clientSecret : Text };
    googleConnections : Map.Map<Principal, Connection>;
    pendingGoogleFlows : Map.Map<Principal, PendingOAuth>;
  };

  public func migration(_old : {}) : NewActor {
    {
      accessControlState = AccessControl.initState();
      googleConfig = { var clientId = ""; var clientSecret = "" };
      googleConnections = Map.empty<Principal, Connection>();
      pendingGoogleFlows = Map.empty<Principal, PendingOAuth>();
    };
  };
};
```

不要给 Gmail 和日历分别提供配置/连接状态或分别提供 OAuth 流 — 一个授权码是一次性的，并且分离状态会导致不同步（请参阅 `writing-motoko` 混合规则）。

在单个 OAuth 客户端上启用两个 API，并仅注册单个 `.../connect/google` 重定向 URI。仅在用户明确要求连接两个不同的 Google 账户时才将它们分成两个单独的面板。

## 所有变体的通用内容

- **需要登录**才能访问每个与 Gmail 相关的路由。通过 [`extension-authorization`](../extension-authorization/SKILL.md) 的认证守卫（`useInternetIdentity` + 当 `!isAuthenticated` 时重定向）将 `/settings/...` 和连接路由（`/connect/gmail`，或 `/connect/google` 在组合应用中）连接起来。
- **前端永远不会持久化令牌。** 没有 `localStorage`，没有 `IndexedDB`，没有 cookie — canister 介导一切。浏览器只看到 `Bool` 状态标志和 OAuth 重定向 URL。
- **OAuth `state` 参数是 canister 生成的并经过验证的。** Canister 存储一个随机 nonce 与挂起的验证器、回调 URI。前端必须将 `code` 和 `state` 都传递给完成调用（`completeGmailOAuth`，或 `completeGoogleOAuth` 在组合应用中）；它永远不会创建或修改这两个值。
- **发送邮件 UI 本身非常简单：** `to`，`subject`，`body` 输入框，提交按钮。没有客户端 Gmail SDK，没有令牌处理，没有 JSON 序列化 — canister 是 Gmail 客户端。

## 相关

- [`mops add googlemail-client@0.2.0`](https://mops.one/googlemail-client) — Gmail REST API 绑定。
- [`mops add google-oauth@0.2.1`](https://mops.one/google-oauth) — Google OAuth 2.0 库（令牌交换、刷新、PKCE、`getUserEmail` userinfo、`DateTime` RFC 3339 帮助程序）。
- [Google OAuth 2.0 for Web Server Applications](https://developers.google.com/identity/protocols/oauth2/web-server) — Web 客户端重定向 URI 和授权码流程参考。
- [Gmail API v1 reference](https://developers.google.com/gmail/api/reference/rest) — `googlemail-client` 包装的内容。
- [RFC 7636 — 代码交换的证明密钥](https://datatracker.ietf.org/doc/html/rfc7636) — PKCE 规范。
- [extension-authorization](../extension-authorization/SKILL.md) — **必需的先决条件**。提供 Internet Identity 登录，`useInternetIdentity` / `useActor` 前端管道，以及 `#admin` 角色门控。
