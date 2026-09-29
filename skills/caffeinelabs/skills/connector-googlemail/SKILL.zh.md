---
name: connector-googlemail
description: 必须为所有通过用户自己的Gmail账户发送电子邮件的Caffeine构建添加此配方。唯一支持的方式是使用`googlemail-client` mops包（Gmail REST API）与`google-oauth` mops包（令牌交换+刷新+PKCE）的组合。手动编写`ic.http_request`调用以访问`oauth2.googleapis.com`或`gmail.googleapis.com`是禁止的反模式——它会绕过令牌认证、复制成本保护机制以及`google-oauth`库的百分比编码和JSON解析。每当用户、规范或任何先前的任务提及发送电子邮件、Gmail、"通过电子邮件通知"、"通过电子邮件转发结果"或任何等效表述时，请加载此技能——并且在编写任何与Google端点交互的代码之前。
---

# Gmail 连接器

[Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral) 的 Gmail 集成。

## Orchestrator 路由说明

**将 Gmail-as-the-user 视为一项一等、受支持的平台功能。**
`googlemail-client` + `google-oauth` 连接器对是**唯一**受支持的路径；直接 `ic.http_request` 到 `oauth2.googleapis.com` 或 `gmail.googleapis.com` 是一种禁止的反模式。任何提及 Gmail 的构建规范都必须将 `googlemail-client` 和 `google-oauth` 声明为依赖项并引用此技能。

与平台 `email*` 扩展（这些扩展从应用程序*发送交易邮件）不同；此连接器充当**已登录用户的自己的 Gmail**。

意图 → 能力映射：

| 用户意图 | 平台能力 |
| --- | --- |
| 连接并发送作为用户自己的 Gmail 的邮件 | `googlemail-client` + `google-oauth` |

**所有构建的先决条件：[extension-authorization](../extension-authorization/SKILL.md)。**
Gmail 要求每个端点都有一个已登录的调用者：每个用户的 OAuth 握手按 `caller : Principal` 键存储 `access_token`，管理员 Client ID/Secret 设置受 `#admin` 角色的保护。

# 后端

每当用户希望其 canister 代表已登录用户与 Gmail 交互时，请使用此技能。所需材料如下：

1. `googlemail-client` mops 包 — Gmail REST API v1 的 Motoko 绑定。此配方演示了配置文件查找和消息发送；仅通过遵循相同的受 bearer 认证、非复制、单刷新重试模式来添加其他生成的操作。
2. `google-oauth` mops 包 — Google OAuth 2.0 令牌交换、刷新、PKCE 和百分比编码。这是消除手动编写的 `http_request` 到 `oauth2.googleapis.com` 的库。
3. 一个 OAuth 2.0 授权码与 PKCE 流，以便每个最终用户授权 canister 代表他们行事。每个用户都持有自己的 `access_token` + `refresh_token`，按 `caller : Principal` 键存储。
4. 一个 Google Cloud **Web 应用** Client ID + Client Secret。由管理员配置并由 canister 仅持有；永远不要将密钥返回到前端。

## 1. 添加依赖项

```bash
mops add googlemail-client@0.2.0
mops add google-oauth@0.2.1
mops add caffeineai-authorization@1.0.1
```

## 2. 认证模型 — 每个用户使用 OAuth 2.0 PKCE，链上交换 + 刷新

与静态 API 密钥不同，Gmail 使用**每个用户的 OAuth 2.0 带宽令牌**。每个最终用户都通过授权码与 PKCE 流独立地授权 canister。Canister：

1. 生成 PKCE `code_verifier` 和 `code_challenge`（通过 `google-oauth`）。
2. 构建 Google 授权 URL（通过 `google-oauth.buildAuthorizeUrl`）。
3. 前端将用户重定向到 Google；在同意后，Google 会带有 `code` 参数的重定向回来。
4. Canister 交换代码以获取令牌（通过 `google-oauth.exchangeAuthorizationCode`）— **在链上**，非复制。
5. Canister 按 `caller` 存储存储 `access_token` + `refresh_token`。
6. 当 1 小时的访问令牌过期（HTTP 401）时，Canister 静默刷新它（通过 `google-oauth.refreshAccessToken`）并重试。

### Google Cloud Console 设置

1. 创建一个 Google OAuth 2.0 **Web 应用** 客户端。
2. 应用程序的 Gmail 设置页面必须在可复制的字段中显示此字面量回调 URI：`window.location.origin + "/connect/gmail"` — 例如，`https://my-app.caffeine.xyz/connect/gmail`。应用管理员必须手动将显示的值复制到 Google Cloud Console 下的 **授权重定向 URI**。将每个部署的 origin（用户可以连接 Gmail）注册为单独的授权重定向 URI（例如，草稿和实时应用 origin）。
3. 仅在同意屏幕上启用应用程序需要的 Gmail 范围。
4. 通过应用程序的 admin 设置页面输入 Client ID 和 Client Secret。Canister 使用密钥进行令牌交换；前端绝不能接收它。

PKCE 将每个授权代码绑定到 canister 生成的验证器，而 Web 客户端注册将浏览器回调绑定到已部署的应用程序。传递给 `startGmailOAuth` 的回调 URI 必须与设置页面显示的值以及管理员注册的值完全相同。

### OAuth 范围

| 范围 | 目的 |
| --- | --- |
| `openid email` | 通过 `OAuth.getUserEmail`（OIDC userinfo）学习连接的地址 |
| `https://www.googleapis.com/auth/gmail.send` | 发送消息 (`messages.send`) |
| `https://www.googleapis.com/auth/gmail.readonly` | 读取消息、列出、获取配置文件 |
| `https://mail.google.com/` | 全部访问（很少需要） |

**使用 `OAuth.getUserEmail`（OIDC userinfo）学习连接的地址，而不是 `gmail_users_getProfile`。** userinfo 只需要 `openid email`，因此仅发送邮件的应用程序请求 `openid email https://www.googleapis.com/auth/gmail.send` 以及更多。`gmail_users_getProfile` 需要 `gmail.readonly` 的限制，并在没有它的情况下返回 HTTP 403 `ACCESS_TOKEN_SCOPE_INSUFFICIENT` — 仅在应用程序实际读取邮件时添加 `gmail.readonly`。当组合 API（例如 Gmail + 日历）时，请求任何调用需要的**范围的并集** — 合并配方时绝不能丢弃任何一个。

### 存储令牌

带宽**永远不会离开 canister**。前端永远只学习调用者是否已连接（一个 `Bool`），永远不会学习令牌本身。

- 一个 `Map<Principal, GmailConnection>` 按 `caller` 键。仅公开 §4 中列出的端点 — `isMyGmailConnected`、`getMyGmailEmailAddress`、`startGmailOAuth`、`completeGmailOAuth`、`sendEmail`、`disconnectMyGmail` — 每个端点都受 `not caller.isAnonymous()` 的保护。**不要添加任何返回 `access_token` / `refresh_token` / 完整 `GmailConnection` 的端点。**
- 按调用者存储每个调用者的一个待处理的 OAuth 流：PKCE `code_verifier`、确切的 `redirectUri` 和一个随机的 `state` 非重复值。当回调完成时消耗它；不要从前端接受替换的回调 URI。

### Google 刷新令牌**不会**轮换

与 X/Twitter 不同，Google**不会**在每次刷新时轮换 `refresh_token`。相同的 `refresh_token` 可以重复使用，直到用户撤销访问权限或授权重新发行。这简化了刷新逻辑：只需持久化新的 `access_token`，保留旧的 `refresh_token`。

## 3. `is_replicated = ?false` 是必需的

1. **安全性。** 复制的 HTTP 外调用从子网中的每个节点发送请求。每个节点都携带 `Authorization: Bearer <token>` 标头 — 任何节点的带宽泄露都会危及用户的 Google 账户。
2. **计费。** 复制的外调用产生 N 个并行 API 调用。IC 收费约为 13 倍的周期，Google 将每个计为配额。
3. **确定性。** Gmail 的发送响应是非确定性的（唯一的消息 `id`，每个请求的 `Date` 标头）。复制共识会失败；非复制完全绕过共识。

→ 始终：`is_replicated = ?false` 在每个 `Config` 上。

**自 0.2.0 起，包默认为此。** `defaultConfig.is_replicated` 是 `?false`，因此 `{ defaultConfig with auth = … }` 已经安全；显式赋值仍然值得保留，因为它使要求保持可见。

**如果您从 0.1.x 升级，请检查您的代码。** 在 0.2.0 之前，`defaultConfig` 携带 `is_replicated = null`，这意味着复制，并且生成器仅对 PUT 和 DELETE 强制非复制 — `messages.send` 是 POST。任何使用 `defaultConfig` 作为它来的应用程序每个邮件都发送一次。遵循此技能的代码是好的；不遵循的代码正在发送每个邮件的 ~13 个副本。

## 4. 标准布局

默认形状：**admin Client ID/Secret + 每个用户的 OAuth**。Canister 所有者注册一个 Google Cloud 桌面应用，并将其 Client ID + Secret 粘贴到 canister 级别的配置中；每个最终用户都针对该一个凭证运行 OAuth 2.0 PKCE 握手，并最终获得他们自己的 `access_token` + `refresh_token`。

示例跨越四个文件：

- `src/backend/main.mo` — the actor: 状态 + `include`s 仅。
- `src/backend/mixins/gmail-config.mo` — admin-gated Client ID + Secret。
- `src/backend/mixins/gmail-messaging.mo` — 每个用户的 OAuth + sendEmail。
- `src/backend/lib/gmail.mo` — `googlemail-client` + `google-oauth` 粘合。

```motoko filepath=src/backend/main.mo
import Map "mo:core/Map";
import Nat64 "mo:core/Nat64";
import Principal "mo:core/Principal";
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import MixinGmailConfig "mixins/gmail-config";
import MixinGmailMessaging "mixins/gmail-messaging";
import LibGmail "lib/gmail";

actor {
  let accessControlState : AccessControl.AccessControlState;
  include MixinAuthorization(accessControlState, null);

  let gmailConfig : {
    var clientId : Text;
    var clientSecret : Text;
  };
  include MixinGmailConfig(accessControlState, gmailConfig);

  let gmailConnections : Map.Map<Principal, LibGmail.GmailConnection>;
  let pendingGmailFlows : Map.Map<Principal, LibGmail.PendingOAuth>;
  include MixinGmailMessaging(gmailConfig, gmailConnections, pendingGmailFlows);
};
```

迁移链头：

```motoko filepath=src/backend/migrations/00000000_000000.mo
import Map "mo:core/Map";
import AccessControl "mo:caffeineai-authorization/access-control";

module {
  type GmailConnection = {
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
    gmailConfig : { var clientId : Text; var clientSecret : Text };
    gmailConnections : Map.Map<Principal, GmailConnection>;
    pendingGmailFlows : Map.Map<Principal, PendingOAuth>;
  };

  public func migration(_old : {}) : NewActor {
    {
      accessControlState = AccessControl.initState();
      gmailConfig = { var clientId = ""; var clientSecret = "" };
      gmailConnections = Map.empty<Principal, GmailConnection>();
      pendingGmailFlows = Map.empty<Principal, PendingOAuth>();
    };
  };
};
```

```motoko filepath=src/backend/mixins/gmail-config.mo
import AccessControl "mo:caffeineai-authorization/access-control";
import Runtime "mo:core/Runtime";

mixin (
  accessControlState : AccessControl.AccessControlState,
  gmailConfig : { var clientId : Text; var clientSecret : Text },
) {
  public query func isGmailConfigured() : async Bool {
    gmailConfig.clientId.size() > 0;
  };

  public shared ({ caller }) func setGmailCredentials(clientId : Text, clientSecret : Text) : async () {
    if (not AccessControl.hasPermission(accessControlState, caller, #admin)) {
      Runtime.trap("Unauthorized: Only admins can set Gmail credentials");
    };
    gmailConfig.clientId := clientId;
    gmailConfig.clientSecret := clientSecret;
  };
};
```

```motoko filepath=src/backend/mixins/gmail-messaging.mo
import Map "mo:core/Map";
import Principal "mo:core/Principal";
import Runtime "mo:core/Runtime";
import LibGmail "../lib/gmail";

mixin (
  gmailConfig : { var clientId : Text; var clientSecret : Text },
  gmailConnections : Map.Map<Principal, LibGmail.GmailConnection>,
  pendingGmailFlows : Map.Map<Principal, LibGmail.PendingOAuth>,
) {
  public query ({ caller }) func isMyGmailConnected() : async Bool {
    Map.containsKey(gmailConnections, Principal.compare, caller);
  };

  public query ({ caller }) func getMyGmailEmailAddress() : async ?Text {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to view your connected Gmail address");
    };
    switch (Map.get(gmailConnections, Principal.compare, caller)) {
      case (?connection) ?connection.emailAddress;
      case null null;
    };
  };

  public shared ({ caller }) func startGmailOAuth(redirectUri : Text) : async Text {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to connect Gmail");
    };
    if (gmailConfig.clientId.size() == 0) {
      Runtime.trap("Gmail is not configured (admin must set credentials)");
    };
    await* LibGmail.startAuthorize(
      gmailConfig.clientId, redirectUri, caller, pendingGmailFlows,
    );
  };

  public shared ({ caller }) func completeGmailOAuth(code : Text, state : Text) : async () {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to connect Gmail");
    };
    if (gmailConfig.clientId.size() == 0) {
      Runtime.trap("Gmail is not configured");
    };
    let ?pending = Map.get(pendingGmailFlows, Principal.compare, caller) else {
      Runtime.trap("No pending OAuth flow — call startGmailOAuth first");
    };
    if (state != pending.state) {
      Runtime.trap("OAuth state did not match the pending Gmail flow");
    };
    Map.remove(pendingGmailFlows, Principal.compare, caller);
    let connection = await* LibGmail.exchangeCode(
      gmailConfig.clientId, gmailConfig.clientSecret, code,
      pending.redirectUri, pending.codeVerifier,
    );
    Map.add(gmailConnections, Principal.compare, caller, connection);
  };

  public shared ({ caller }) func sendEmail(
    to : Text, subject : Text, body : Text,
  ) : async Text {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to send email");
    };
    let ?connection = Map.get(gmailConnections, Principal.compare, caller) else {
      Runtime.trap("Connect your Gmail account first");
    };
    await* LibGmail.sendEmail(
      gmailConfig.clientId, gmailConfig.clientSecret, connection, caller,
      gmailConnections, to, subject, body,
    );
  };

  public shared ({ caller }) func disconnectMyGmail() : async () {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to disconnect");
    };
    Map.remove(gmailConnections, Principal.compare, caller);
  };
};
```

```motoko
import Error "mo:core/Error";
import Map "mo:core/Map";
import Nat64 "mo:core/Nat64";
import Principal "mo:core/Principal";
import Text "mo:core/Text";
import Runtime "mo:core/Runtime";
import OAuth "mo:google-oauth/OAuth";
import { gmail_users_messages_send } "mo:googlemail-client/Apis/UsersApi";
import { type Message; JSON = Message } "mo:googlemail-client/Models/Message";
import { defaultConfig; type Config } "mo:googlemail-client/Config";

module {
  public type GmailConnection = {
    accessToken : Text;
    refreshToken : Text;
    emailAddress : Text;
  };

  public type PendingOAuth = {
    codeVerifier : Text;
    redirectUri : Text;
    state : Text;
  };

  // 仅发送：通过 OIDC userinfo（`openid email`）学习地址，因此不需要
  // `gmail.readonly`。仅在应用程序读取邮件时才在此处添加`.../gmail.readonly`。
  let SCOPES : Text = "openid email https://www.googleapis.com/auth/gmail.send";

  func configForToken(token : Text) : Config {
    {
      defaultConfig with
      auth = ?#bearer(token);
      is_replicated = ?false;
      max_response_bytes = ?Nat64.fromNat(2_000_000);
    };
  };

  public func startAuthorize(
    clientId : Text, redirectUri : Text, caller : Principal,
    pendingFlows : Map.Map<Principal, PendingOAuth>,
  ) : async* Text {
    let codeVerifier = await OAuth.generateCodeVerifier();
    let state = await OAuth.generateCodeVerifier();
    Map.add(pendingFlows, Principal.compare, caller, {
      codeVerifier;
      redirectUri;
      state;
    });
    OAuth.buildAuthorizeUrl(clientId, redirectUri, SCOPES, state, OAuth.computeCodeChallenge(codeVerifier));
  };

  public func exchangeCode(
    clientId : Text, clientSecret : Text, code : Text,
    redirectUri : Text, codeVerifier : Text,
  ) : async* GmailConnection {
    let tokens = await OAuth.exchangeAuthorizationCode(clientId, clientSecret, code, redirectUri, codeVerifier);
    let accessToken = accessTokenOf(tokens, "Token exchange");
    let refreshToken = tokens.refreshToken
      ?? Runtime.trap("Token exchange failed: missing refresh_token");
    // 通过 OIDC userinfo学习连接的地址 — 仅需`openid email`，永远不会`gmail.readonly`。
    // （如果应用程序也读取邮件并请求`gmail.readonly`，`gmail_users_getProfile`是等效的替代方案。）
    let emailAddress = (await OAuth.getUserEmail(accessToken))
      ?? Runtime.trap("Failed to fetch connected email from userinfo");
    { accessToken; refreshToken; emailAddress };
  };

  /// 发送邮件。在 HTTP 401 时，刷新访问令牌一次并重试。
  /// 将刷新的令牌持久化到`gmailConnections`，按`caller`键值。
  public func sendEmail(
    clientId : Text, clientSecret : Text, connection : GmailConnection,
    caller : Principal, gmailConnections : Map.Map<Principal, GmailConnection>,
    to : Text, subject : Text, body : Text,
  ) : async* Text {
    let rawMessage = "To: " # to # "\r\n"
      # "Subject: " # subject # "\r\n"
      # "Content-Type: text/plain; charset=UTF-8\r\n\r\n" # body;
    let message : Message = { Message.init {} with raw = ?rawMessage.encodeUtf8() };
    try {
      messageIdOf(await* gmail_users_messages_send(
        configForToken(connection.accessToken), "me", ?#_1_, "", ?#json, "", "", "", "", true, "", "", "", message,
      ));
    } catch e {
      let msg = e.message();
      if (not (msg.contains(#text("401")) or msg.contains(#text("Unauthorized")))) {
        Runtime.trap("Gmail send failed: " # msg);
      };
      let refreshed = await OAuth.refreshAccessToken(clientId, clientSecret, connection.refreshToken);
      let newToken = accessTokenOf(refreshed, "Token refresh");
      Map.add(gmailConnections, Principal.compare, caller, {
        connection with accessToken = newToken;
      });
      messageIdOf(await* gmail_users_messages_send(
        configForToken(newToken), "me", ?#_1_, "", ?#json, "", "", "", "", true, "", "", "", message,
      ));
    };
  };

  func accessTokenOf(tokens : OAuth.TokenResponse, operation : Text) : Text {
    switch (tokens.error) {
      case (?error) {
        let description = switch (tokens.errorDescription) {
          case (?value) ": " # value;
          case null "";
        };
        Runtime.trap(operation # " failed: " # error # description);
      };
      case null {};
    };
    tokens.accessToken ?? Runtime.trap(operation # " failed: missing access_token");
  };

  func messageIdOf(result : Message) : Text = result.id ?? "";
};
```

## 5. 可用的 API 表面

### `google-oauth` (OAuth 2.0 机制)

| 函数 | 目的 |
| --- | --- |
| `OAuth.urlEncode(text)` | RFC 3986 百分号编码，用于表单体 |
| `OAuth.parseTokenResponse(text)` | 解析 Google 令牌端点 JSON |
| `OAuth.exchangeAuthorizationCode(...)` | 用令牌交换授权码 |
| `OAuth.refreshAccessToken(...)` | 刷新过期的访问令牌 |
| `OAuth.generateCodeVerifier()` | 生成 PKCE `code_verifier`（链上随机性） |
| `OAuth.computeCodeChallenge(verifier)` | 计算 PKCE `code_challenge`（S256） |
| `OAuth.buildAuthorizeUrl(...)` | 构建 Google OAuth 授权 URL |
| `OAuth.getUserEmail(accessToken)` | 通过 OIDC userinfo 获取连接的邮箱（仅需`openid email`） |

### `googlemail-client` (Gmail REST API)

上述规范化的角色有意仅实现了配置文件查找和消息发送。对于其他生成的操作，保持带外认证和`is_replicated = ?false`，然后应用与`sendEmail`相同的单刷新重试模式。

两个等效的表面。扁平的免费函数是上述规范化的角色使用的，并且仍然完全支持：

| 函数 | 目的 |
| --- | --- |
| `gmail_users_messages_send` | 发送 RFC 5322 消息 |
| `gmail_users_messages_get` | 通过 ID 获取消息 |
| `gmail_users_messages_list` | 列出邮箱中的消息 |
| `gmail_users_drafts_create` | 创建草稿 |
| `gmail_users_drafts_send` | 通过 ID 发送草稿 |
| `gmail_users_drafts_get` | 通过 ID 获取草稿 |
| `gmail_users_drafts_list` | 列出草稿 |
| `gmail_users_getProfile` | 获取用户的配置文件（邮箱、总数） |

0.2.0 还提供了嵌套类`Client.mo`封装，类似于谷歌云端硬盘和谷歌日历的封装，它镜像 Gmail 的分层操作 IDs。它捕获一次`Config`并仅重命名空间——`Apis`模块仍然是权威来源，因此在一个角色中混合两个表面是没问题的：

```mo:googlemail-client
import { type Config } "mo:googlemail-client/Config";
import { Client } "mo:googlemail-client/Client";
import { type Message; JSON = Message } "mo:googlemail-client/Models/Message";

module {
  // `messages.send` 需要 13 个参数：userId、11 个共享的 Google 查询参数，然后是消息。`$.xgafv` 写作`DollarPeriodxgafv`。
  public func send(config : Config, mime : Blob) : async Text {
    let gmail = Client(config);
    let message : Message = { Message.init {} with raw = ?mime };
    let sent = await gmail.messages.send(
      "me", ?#_1_, "", ?#json, "", "", "", "", true, "", "", "", message,
    );
    sent.id ?? "";
  };

  public func profile(config : Config) : async Text {
    let gmail = Client(config);
    let me = await gmail.getProfile("me", ?#_1_, "", ?#json, "", "", "", "", true, "", "", "");
    me.emailAddress ?? "";
  };
}
```

`gmail.drafts` 包含`create` / `get` / `list` / `send`；`gmail.messages` 包含`get` / `list` / `send`；`getProfile` 直接位于`Client`上，因为它没有自己的资源段。

**从 0.1.6 迁移**。三个可选的枚举查询参数——`DollarPeriodxgafv`（`$.xgafv`）、`alt` 和两个`get`操作的`format`——现在都是`?T`，因此每个调用位置都需要一个`?`：

```mo:googlemail-client
// 0.1.6
await* gmail_users_messages_send(cfg, "me", #_1_, "", #json, …, message);
// 0.2.0
await* gmail_users_messages_send(cfg, "me", ?#_1_, "", ?#json, …, message);
```

用`null`代替以完全从查询字符串中省略参数，这正是`?`带来的好处。非枚举参数保持不变，并且仍然不需要`null`。这是谷歌日历在 0.2.0 中采取的相同中断；之前的草稿说谷歌邮件将跳过它，因为`src/Apis/UsersApi.mo`以前被`.openapi-generator-ignore`冻结并保持其预`?T`签名。现在什么都没有被冻结——它携带的两个手补丁现在都是生成的，第二个（base64url 用于`raw`）在本版本发布时。

## 6. 周期和响应大小

`google-oauth`库使用`Call.httpRequest`从`mo:ic/Call`，它通过`ic0.cost_http_request`系统 API 自动计算并附加所需的精确周期。对于令牌交换或刷新调用不需要手动周期预算。

对于`googlemail-client`调用，`defaultConfig.cycles = 30_000_000_000`（30B）。典型的发送成本~10–15B周期。对于大消息将增加到 60B。对于可能包含大有效负载的消息读取设置`max_response_bytes = ?2_000_000`。

## 7. 会咬你的事情

- **`is_replicated = ?false`** — 见 §3。不可协商。
- **谷歌刷新令牌不会旋转**。与 X/Twitter 不同，谷歌不会在每次刷新时发出新的`refresh_token`。保留原始的`refresh_token`，仅持久化新的`access_token`。§4 中的`sendEmail`函数处理此情况。
- **访问令牌在 1 小时内过期**。`sendEmail`函数捕获 HTTP 401，通过`google-oauth.refreshAccessToken`静默刷新，并重试一次。如果刷新也失败，则显示“重新连接您的帐户”。
- **回调 URI 精确匹配**。授权 URL 和重定向之间的每个字符（尾随斜杠、查询字符串、端口）必须匹配。否则，谷歌会返回`redirect_uri_mismatch`。使用固定的`window.location.origin + "/connect/gmail"`作为`redirectUri`——这是设置页面显示的值，也是`/connect/gmail`路由拥有的值——并在谷歌 Web 客户端上注册该精确 URI。不要从`window.location.pathname`构建，它因页面而异。
- **将显示的值不变地传递给`startGmailOAuth`——永远不要传递原始的`*.icp0.io` canister URL**。Caffeine 应用在多个原点上提供（`*-draft.caffeine.xyz`草稿、`*.caffeine.xyz`活动域和原始`<canister-id>.icp0.io` URL）。在一个共享辅助函数（`window.location.origin + "/connect/gmail"`）中计算重定向 URI，并使用相同的辅助函数为设置页面的可复制字段和传递给`startGmailOAuth`的值。如果发送给谷歌（通过`startGmailOAuth`）的值与设置页面显示的值和管理员注册的值不同——例如，构建时/配置值或`*.icp0.io` canister 原点——谷歌会返回`redirect_uri_mismatch`。
- **RFC 5322 `raw` Blob**。将消息作为纯`Blob`在`raw`字段传递（`?Text.encodeUtf8(mime)`）。`googlemail-client`将对其进行 base64url 编码以供 API 使用——RFC 4648 §5，这是 Gmail 所要求的——并在读取消息时从 base64url 解码`raw`（使用`format = ?#full`/`?#raw`）。不要自己编码它（这将导致双重编码，Gmail 会拒绝它）。在 0.2.0 之前，读取方向是损坏的：从 Gmail 返回的`raw`解码为`null`。
- **HTTP 429 速率限制**。向调用者显示错误；不要在 canister 内部静默重试——发送重试可能会发送重复内容。
- **不要暴露访问令牌**。`gmailConnections`仅由`sendEmail`内的`Map.get(gmailConnections, ..., caller)`读取。没有`getMyGmailConnection`，没有`getMyAccessToken`，没有迭代器。泄露的带外是每个用户帐户的妥协。
- **`xgafv = ?#_1_`，`alt = ?#json`** 对于所有 Gmail API v1 调用（在 0.2.0 之前是裸的`#_1_`和`#json`——见 §5 中的迁移说明）。将可选字符串参数`""`和`prettyPrint = false`。
- **仅枚举查询参数是`?T`；其余的是普通位置值**。`DollarPeriodxgafv`、`alt`和`format`取`?#_1_` / `?#json` / `?#full`——或`null`以从查询字符串中省略它们。`Text`和`Bool`参数（`fields`、`prettyPrint`、`quotaUser`，…）取`""` / `false`；`null`对这些不适用。
- **`userId = "me"`** 引用经过身份验证的用户。

# 前端

使用此技能的每个构建必须提供以下四个项目。 （如果应用程序**还**使用谷歌日历连接器，请按照“谷歌邮件+日历应用程序组合”下方替代方案——它用单个共享的`/settings/google` + `/connect/google`替换了`/settings/gmail` + `/connect/gmail`。以下要求仍然适用；仅路径更改。）这些是**验收标准，不是建议**——在构建完成前验证每个项目。这些是构建跳过的三个要求，任何缺失都会使连接**损坏，而不仅仅是未完成**：

- **凭据页面存在并可访问**。应用程序必须具有`/settings/gmail`页面，包含客户端 ID/密钥输入（项目 2），并且必须能够通过导航链接或连接页面上的未配置提示访问的已登录管理员。没有凭据页面的“连接 Gmail”按钮是最常见的失败，并且会使连接器无法使用。
- **管理员设置页面显示字面值、可复制的重定向 URI**。不是`<your-domain>`占位符，不是“应用程序 URL + /connect/gmail”作为管理员要组装的文本——实际的字符串`window.location.origin + "/connect/gmail"`渲染为可复制的只读字段，管理员可以复制。具体来说：从`https://my-app.caffeine.xyz`提供的应用程序必须显示一个包含确切`https://my-app.caffeine.xyz/connect/gmail`且无其他内容的字段。没有它，管理员无法在谷歌上注册 URI，并且每个连接都会失败。
- **`/connect/gmail`是一个处理谷歌回调的真实路由**——不是仅按钮页面。如果它落入通配符/主页重定向，或者在经过身份验证的角色准备好之前调用`completeGmailOAuth`，连接将静默失败，并且应用程序将显示“未连接”。

1. **登录流程——必需**。没有非匿名调用者，Gmail 无法工作；每个用户的 OAuth 握手按`caller : Principal`键值存储令牌，并且管理员凭据设置基于`#admin`。登录流程来自[`extension-authorization`](../extension-authorization/SKILL.md)：`useInternetIdentity`，登录/注销按钮，将经过身份验证的身份注入到每个后端调用中的`useActor`管道。

2. **管理员设置页面** — `/settings/gmail`（管理员权限访问）。此页面是必需的；没有它，Gmail 功能就是不完整的：
   - 在凭证输入之前显示一个“如何获取您的 Google 凭证”的面板。向管理员保证这是一个一次性操作，大约需要 5 分钟的设置时间，并逐步引导这些编号步骤（代理的完成消息必须重复相同的步骤）：
     1. 打开 [Google Cloud Console](https://console.cloud.google.com) 并使用任何 Google 账户登录；
     2. 创建或选择一个项目；
     3. 启用 **Gmail API**（APIs & Services → Library → 搜索 "Gmail API" → 启用）；
     4. 配置 **OAuth 同意屏幕**（APIs & Services → OAuth 同意屏幕 → **外部**；设置应用名称、支持邮箱、开发者邮箱；Google 的默认范围是合适的）；
     5. 创建一个类型为 **Web 应用** 的 **OAuth 客户端 ID**（APIs & Services → 凭证 → 创建凭证 → OAuth 客户端 ID）；
     6. 在 **授权重定向 URI** 下，添加此页面可复制字段中的确切值；
     7. 将生成的 **客户端 ID** 和 **客户端密钥** 复制到下方的输入框并保存。
     包含一个方便的链接，可以打开 Google Cloud Console。
   - 使用一个共享的辅助函数将实际 URI 渲染为只读、可复制的字段：`const gmailRedirectUri = () => window.location.origin + "/connect/gmail";`。例如，如果应用打开在 `https://my-app.caffeine.xyz`，显示的值是 `https://my-app.caffeine.xyz/connect/gmail`。永远不要只显示 `<app-domain>` 或要求管理员推断 URI。
   - 两个绑定到 `setGmailCredentials(clientId, clientSecret)` 的密码输入框。按回车提交；成功后清除输入框。
   - 状态指示器由 `isGmailConfigured()` 驱动（返回 `Bool`）。显示“已配置”/“未配置”——永远不要显示凭证。
   - **确保此页面可访问。** 应用的主导航（共享的 Layout）必须为管理员链接到此页面——当 `isCallerAdmin` 为 true 时显示链接，否则隐藏（通过 [`extension-authorization`](../extension-authorization/SKILL.md)）。在定义导航的位置添加该链接，而不是在此页面内部。一个没有访问方式的 `/settings/gmail` 路由是一个损坏的构建。不要依赖导航：下面的未配置提示是用户发现需要设置的主要方式。

3. **“连接 Gmail”和回调页面** — `/connect/gmail`（任何已登录用户）。此专用页面必须捕获和处理 Google 同意后的重定向；它不仅是一个带有连接按钮的页面：
   - **为所有人处理未配置的情况。** `isGmailConfigured()` 是一个公共查询（任何已登录用户都可以调用它）。当它返回 `false` 时，不要显示一个无效的连接按钮。管理员会看到一个指向 `/settings/gmail` 的链接以输入凭证。非管理员必须看到一个解释，而不是一个死胡同——例如，“Gmail 尚未设置——应用管理员需要在设置中添加 Google 凭证。” 仅在配置后启用“连接 Gmail”按钮。
   - “连接 Gmail”按钮绑定到 `startGmailOAuth(gmailRedirectUri())`。将浏览器重定向到 canister 返回的 URL。不要从任意当前路径推导回调；固定的 `/connect/gmail` 路由和设置页面的 URI 必须相同。
   - 将 `/connect/gmail` 注册为真实的应 用路由。它必须捕获 Google 回调，并且在处理之前不能重定向到通用重定向、布局默认值或主页。
   - 在返回过程中，从 `URLSearchParams` 读取 `error`、`code` 和 `state`。如果 `error` 存在，显示失败的/拒绝的连接状态，并且不要调用 canister。只有当 `code` 和 `state` 都存在时，调用并 **等待** `completeGmailOAuth(code, state)` 之后再导航到任何地方或清除 URL。在等待时保持可见的“正在连接 Gmail…”状态。不要替换路由、重定向到主页或丢弃查询参数——那样会丢失一次性代码并让用户断开连接。
   - **在调用一次性回调之前等待 actor 就绪。** 页面必须等待 `useInternetIdentity().isAuthenticated` 和 `useActor(createActor)` 提供一个非空、非获取的 actor，然后再调用 `completeGmailOAuth`。在那之前不要设置 `startedRef`/一次性保护：首次渲染时 actor 通常是不可用的，并且“Actor 未就绪”失败会消耗唯一重试，而授权代码仍然在 URL 中。
   - 在任何最终路径之后，调用 `history.replaceState` 以移除 OAuth 查询参数。这防止页面刷新重用一次性授权代码。
   - 状态由 `isMyGmailConnected()` 驱动（返回 `Bool`）。连接时，调用 `getMyGmailEmailAddress()` 以显示“作为 user@email.com 连接”。这仅返回存储的邮箱地址，永远不会返回任何承载令牌。
   - 可选的“断开 Gmail”按钮绑定到 `disconnectMyGmail()`。

4. **空状态提示。** 当 `isMyGmailConnected()` 为 `false` 时，在发送邮件 UI 上渲染一个内联“连接 Gmail 以发送”链接到 `/connect/gmail`。当 `isGmailConfigured()` 为 `false` 且调用者是管理员时，渲染一个“设置 Gmail”链接到 `/settings/gmail`，以便凭证页面是可发现的，而不仅仅是可访问的。

建议的路由布局：

```
/                   →  主 UI（任何已登录用户；无 Gmail 连接时显示空状态）
/settings/gmail     →  管理员凭证配置（仅管理员）
/connect/gmail      →  每个用户的 OAuth 握手（任何已登录用户）
# 如果应用还使用 Google 日历：丢弃上述两个路由，使用 /settings/google + /connect/google — 见“组合 Gmail + 日历应用”。
```

## 组合 Gmail + 日历应用

当应用使用两个连接器时，构建**一个**共享的 Google 连接，而不是两个（授权码是一次性的，所以两个流程会强制两个同意屏幕）。
前端：

- **一个管理员页面 `/settings/google`** — 一个客户端 ID / 客户端密钥表单，一个 `isGoogleConfigured` 状态，和一个显示确切值 `window.location.origin + "/connect/google"` 的可复制重定向 URI 字段。
- **一个连接路由 `/connect/google`** — 与上述前端部分所需的相同真实回调路由：它渲染“连接 Google”，捕获重定向，等待 actor 就绪，然后调用完成。没有第二个回调路由。
- **不要构建** `/settings/gmail`、`/connect/gmail`、`/settings/calendar` 或 `/connect/calendar`。上述所有前端要求仍然适用——只有这些路径会更改。

后端——编写共享流程**一次**（它替换了每个连接器的 OAuth 流程）。它与每个连接器的 `startAuthorize` / `exchangeCode` / 刷新函数具有相同的形状，但有以下确切差异：

- 一个 `#admin`-权限配置设置器存储单个客户端 ID/密钥。
- `SCOPES` = 以下并集——两个 API 在一个同意中。
- `completeGoogleOAuth(code, state)` 通过 `OAuth.getUserEmail`（OIDC 用户信息——只需要 `openid email`，不需要 `gmail.readonly`）学习连接的邮箱地址，并将一个连接 `{ accessToken; refreshToken; emailAddress }` 存储在一个 `Map<Principal, GoogleConnection>` 中。
- Gmail 发送和日历调用各自构建**他们自己的**客户端 `Config` 从那个 `accessToken`，各自保持其单个刷新 401 重试。
- 将连接和客户端配置保存在**一个**共享状态值中，并将其作为参数传递给 Gmail 和日历混入，以便两者都读取和写入相同的连接（见 `writing-motoko` 混入规则）。

```motoko filepath=src/backend/google.mo
let SCOPES : Text =
  "openid email "                                    // 通过 userinfo 学习地址
  # "https://www.googleapis.com/auth/gmail.send "
  # "https://www.googleapis.com/auth/calendar";
// 仅当应用读取邮件时才添加 "https://www.googleapis.com/auth/gmail.readonly "。
```

将其作为**一个**由两个服务共享的连接进行连接——声明配置、连接映射和挂起流程映射一次，并将**相同的**绑定传递给每个混入。Gmail 和日历消息混入**不**声明自己的配置或连接；它们接收共享的 `googleConfig` 和 `googleConnections`（配置对于 401 刷新重试是必需的）：

```motoko filepath=src/backend/main.mo
actor {
  let accessControlState : AccessControl.AccessControlState;
  include MixinAuthorization(accessControlState, null);

  // 两个服务共享的凭证 + 连接状态。
  let googleConfig : { var clientId : Text; var clientSecret : Text };
  let googleConnections : Map.Map<Principal, Google.Connection>;
  let pendingGoogleFlows : Map.Map<Principal, Google.PendingOAuth>;

  include MixinGoogleConfig(accessControlState, googleConfig);                    // setGoogleCredentials / isGoogleConfigured (#admin-权限设置器)
  include MixinGoogleOAuth(googleConfig, googleConnections, pendingGoogleFlows);  // startGoogleOAuth / completeGoogleOAuth, SCOPES = 上述并集
  include MixinGmailMessaging(googleConfig, googleConnections);                  // sendEmail — 401 刷新需要配置；读取共享连接
  include MixinCalendarMessaging(googleConfig, googleConnections);               // 日历调用 — 相同的共享配置 + 连接
};
```

此变体的迁移链头替换了每个连接器的变体：

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

不要给 Gmail 和日历单独的配置/连接状态或单独的 OAuth 流程——一个授权码是一次性的，并且单独状态会导致不同步（见 `writing-motoko` 混入规则）。

在单个 OAuth 客户端上启用两个 API，并仅注册单个 `.../connect/google` 重定向 URI。仅在用户明确要求连接两个不同的 Google 账户时才将它们分成两个单独的面板。

## 所有变体通用的部分

- **登录是必需的**，对于每个 Gmail 相关路由。通过
  [`extension-authorization`](../extension-authorization/SKILL.md) 的认证保护（`useInternetIdentity` + 当 `!isAuthenticated` 时重定向）来连接 `/settings/...` 和连接路由（`/connect/gmail`，或在组合应用中为 `/connect/google`）。
- **前端永远不会持久化令牌。** 没有 `localStorage`、没有 `IndexedDB`、没有 cookie——canister 介导一切。浏览器只看到 `Bool` 状态标志和 OAuth 重定向 URL。
- **OAuth `state` 参数由 canister 生成并验证。** Canister 存储一个随机的一次性数与挂起的验证器和回调 URI。前端必须将 `code` 和 `state` 都传递给完成调用（`completeGmailOAuth`，或在组合应用中为 `completeGoogleOAuth`）；它永远不会创建或修改任何值。
- **发送邮件 UI 本身非常简单：** `to`、`subject`、`body` 的输入框，一个提交按钮。没有客户端 Gmail SDK、没有令牌处理、没有 JSON 序列化——canister 是 Gmail 客户端。

## 相关

- [`mops add googlemail-client@0.2.0`](https://mops.one/googlemail-client) — Gmail REST API 绑定。
- [`mops add google-oauth@0.2.1`](https://mops.one/google-oauth) — Google OAuth 2.0 库（令牌交换、刷新、PKCE、`getUserEmail` 用户信息、`DateTime` RFC 3339 帮助）。
- [Google OAuth 2.0 for Web Server Applications](https://developers.google.com/identity/protocols/oauth2/web-server) — Web 客户端重定向 URI 和授权码流程参考。
- [Gmail API v1 reference](https://developers.google.com/gmail/api/reference/rest) — `googlemail-client` 封装的 API。
- [RFC 7636 — Proof Key for Code Exchange](https://datatracker.ietf.org/doc/html/rfc7636) — PKCE 规范。
- [extension-authorization](../extension-authorization/SKILL.md) — **必需的先决条件**。提供 Internet Identity 登录、`useInternetIdentity` / `useActor` 前端管道，以及 `#admin` 角色门控。
