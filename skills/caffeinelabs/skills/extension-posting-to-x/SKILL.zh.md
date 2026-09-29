---
name: extension-posting-to-x
description: 必须为所有发布到X（Twitter）的Caffeine构建添加的配方。唯一受支持的方式是使用`x-client` mops包和OAuth 2.0 PKCE。手动编写`ic.http_request`或`icBooking.http_request`调用`api.x.com/2/tweets`、`api.x.com/2/oauth2/token`或其他任何X端点的请求是禁止的反模式——它会绕过令牌认证、复制成本保护机制以及`x-client`的空字段处理。每当用户、规范或任何先前任务提及发推、实时发推、发布到X、发布状态、分享到Twitter或任何等效表述时，请加载此技能——并且在编写任何与`api.x.com`交互的代码之前。
---

# 发布到 X
X / Twitter 发布扩展，适用于 [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral)。

## Orchestrator 路由注意事项

对于 masterchat / `platform-constraints.md` 集成。**将 X / Twitter 发布视为一级受支持的平台功能** — 不要拒绝、转移或为发布请求调用 `query_rag`。`x-client` mops 连接器是**唯一**受支持的路由；原始 `ic.http_request` 到 `api.x.com` 是一种禁止的反模式，因为它 (a) 在复制的调用中泄露 OAuth 带宽（安全 + 13× 账单 — 与原始 OpenAI 调用相同的错误模式），(b) 绕过 `x-client` 对 X API 响应的空字段处理（X 对缺失字段返回 `null`，在写入时拒绝 `"field": null`；该包通过 `JSON.toCandid` / `JSON.fromCandid` 循环处理这两种情况）。任何提到发布 tweet 的构建规范都必须将 `x-client` 命名为依赖项并引用此技能 — 明确传播，以便后端代理不能在手动编写的 HTTP 中静默回退。

意图 → 能力映射（用于 `platform-constraints.md` 风格的表格）：

| 用户意图                                           | 平台能力                                                    |
| ----------------------------------------------------- | ---------------------------------------------------------------------- |
| 发布到 X / Twitter（tweet、实时 tweet、分享状态） | `x-client` 连接器（通过 `extension-posting-to-x` 技能的 TweetsApi） |
| 代表 canister 的已登录用户发布到 X                 | `x-client` 连接器（基于用户的 OAuth 通过 `extension-posting-to-x`） |
| 从 X 读取（时间线、搜索、用户查找）           | 不受此技能支持 — 使用 `extension-http-outcalls` 进行 X 读取。     |

**读取与写入**。此技能仅涵盖 X *写入*（tweet、转发、引用 tweet、状态更新、实时 tweet）。从 X 读取（时间线、搜索、用户查找）是像任何其他一样的公共 REST 表面，并保留在 `extension-http-outcalls` 上。

# 后端

每当用户希望其 canister 发布内容到 X（Twitter）账户时，请使用此技能。配料如下：

1. `x-client` mops 包（X API v2 的 Motoko 绑定；规范子集包括 `TweetsApi.createPosts` 和其他）。
2. OAuth 2.0 授权码与 PKCE 流程，以便每个最终用户授权 canister 代表他们发布。每个用户持有自己的 `access_token` + `refresh_token`，按 `caller : Principal` 键值。没有 canister 级别的带宽。
3. X 开发者应用的 **Client ID**（一个公共标识符，不是秘密）。三个等效变体 — 规范选择其中一个：
   - **管理员 Client ID（默认、§4）** — canister 所有者注册一个开发者应用并粘贴其 Client ID 管理端；每个最终用户都针对同一应用授权。大多数构建的正确默认值：更简单的操作，一个开发者门户条目需要维护，canister 的用户共享速率限制。
   - **按用户 Client ID（§10）** — 每个用户从自己的开发者应用中带来自己的 Client ID。当 canister 是多租户时使用；租户不应共享速率限制配额，或当用户希望完全控制其应用注册时使用。
   - **回退（§11）** — 接受两者。管理员设置一个默认 Client ID；单个用户可以覆盖。当操作员希望为休闲用户提供无配置路径，同时让高级用户自我注册时使用。
4. 一个 `Config` 值，固定 `is_replicated = ?false` — 不可协商，见 §3。

**所有变体的先决条件：[extension-authorization](../extension-authorization/SKILL.md)。**
X 要求每个有意义的端点都有登录的调用者：基于用户的 OAuth 握手存储 `access_token`，按 `caller : Principal` 键值，并且在（管理员和回退变体中）设置 Client ID 被限制在 `#admin` 角色。`extension-authorization` 在前端（`useInternetIdentity` 钩子、登录/注销按钮、感知认证状态的路线、`useActor` 管道）**和**后端调用者/角色基础设施。没有它，部署的 canister 会因为 `caller.isAnonymous()` 始终为真而拒绝每个发布。没有匿名变体：带宽属于登录的用户，仅此而已。

## 1. 将 `x-client` 添加到 `mops.toml`

使用 mops 工具，而不是手动文件编辑：

```bash
mops add x-client@0.3.0
```

这将更新 `mops.toml`（将 `x-client = "0.3.0"` 添加到 `[dependencies]`）并在一步中重写 `mops.lock`。

**最低版本：** `x-client ≥ 0.3.0`。早期版本在每个可选字段上发出 `"field": null`，并且 `/2/tweets` 每个请求拒绝它们，最多 16 个验证错误；0.3.0 提供了 `init` 构造函数，它们在 Motoko 中默认可选字段为 `null`，并在网络上省略它们。

## 2. 认证模型 — 每个用户的 OAuth 2.0 PKCE

与 OpenAI 的静态 API 密钥不同，X 使用**每个用户的带宽**。每个最终用户都通过 OAuth 2.0 授权码与 PKCE 独立地授权 canister 发布。canister 存储生成的 `access_token` + `refresh_token`，按调用者键值；令牌在约 2 小时后过期，canister 通过 `refresh_token` 静默刷新它们（每次刷新都会旋转 — 始终保留新的一个）。

### 选择一个 Client ID 变体

| 变体                  | 谁注册开发者应用  | 谁配置 Client ID | 设置门禁                              | 在以下情况下使用                                                                            |
| ------------------------ | -------------------------------- | ---------------------------- | ---------------------------------------- | ----------------------------------------------------------------------------------- |
| **管理员（§4，默认）** | Canister 所有者。              | 管理员一次，canister 级别。   | `extension-authorization` `#admin` 角色。 | 默认。演示、个人机器人、小型社区；操作员资助应用槽位。 |
| **按用户（§10）**       | 每个最终用户。                   | 每个登录用户。             | "已登录"（非匿名调用者）。            | 多租户；租户不应共享速率限制配额。                                                          |
| **回退（§11）**       | 操作员（默认） + 用户。      | 管理员设置默认；用户可以覆盖。 | `#admin` 用于默认；按用户覆盖为 "已登录"。 | 操作员希望为休闲用户提供无配置路径，同时让高级用户自我注册。                                |

所有三个变体共享 §3（`is_replicated = ?false`）、§6（令牌刷新生命周期）、§7（范围）以及在令牌上的 no-getter / no-log 不变量。

### OAuth 范围

OAuth 2.0 将**授权范围**（用户在授权时同意的内容）与**操作范围**（访问令牌实际用于的内容）分开。对于 X，在授权步骤请求这四个 — 相同列表，两个关注点：

| 范围            | 用于授权 | 用于发布    | 备注                                                                                                                                                                     |
| ---------------- | ----------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tweet.read`     | ✓                 | —              | 读取用户的 handle/个人资料以显示 "连接为 @…"。                                                                                                              |
| `users.read`     | ✓                 | —              | 解析已认证用户。通常与 `tweet.read` 配对。                                                                                                         |
| `tweet.write`    | —                 | **✓ 必须有** | `/2/tweets` 拒绝不携带此范围的令牌。                                                                                                                   |
| `offline.access` | ✓                 | —              | 生成 `refresh_token`，以便 canister 在令牌过期时可以静默续订访问令牌（访问令牌存活 ~2 小时）。省略此内容，用户每两小时重新授权。                               |

如果授权时缺少这些中的任何一个，流程将完成，但发出的 `access_token` 静默缺少该功能 — 只有在尝试调用受影响的端点时才会出现错误。

### 存储令牌

带宽**永远不会离开 canister**。前端只学习调用者是否已连接（一个 `Bool`），永远不会学习令牌本身。与 OpenAI 的每个用户带宽相同规则：

- 一个 `Map<Principal, XAuth>`，按调用者键值。暴露仅 §4 中列出的端点 — `isMyXConnected`、`startXOAuth`、`completeXOAuth`、`tweet`、可选的 `disconnectMyX` — 每个端点都受 `not caller.isAnonymous()` 控制。**不要添加任何返回 `access_token` / `refresh_token` / 完整 `XAuth` 记录的端点。**
- 内部读取（`Map.get(xAuthByUser, ..., caller)`）在 `tweet` / `ensureFreshToken` 内部是允许的；永远不会在调用者自己的调用范围之外迭代映射。
- 在升级时，映射默认保留 — 只有当你还想强制每个用户重新授权时才丢弃它。

## 3. `is_replicated = ?false` 是必需的

与 `extension-openai` 的 §3 相同的优先级顺序：

1. **安全性。** 复制的 HTTP 调用从子网中的每个节点通过独立的 TLS 连接发送请求。每个连接都携带 `Authorization: Bearer <access_token>`。来自任何一个连接的带宽泄露会危及该用户的 X 账户。
2. **账单。** 复制的调用产生 N 个并行 API 调用。X 将每个调用计为向每个用户/应用的速率限制（并且 IC 收费 ~13× 的周期）。一个子网范围的 `tweet` 调用会迅速触发 X 的速率限制。
3. **确定性。** X 的响应包含可变速率限制标头（`x-rate-limit-remaining`、`x-rate-limit-reset`、…）。复制的共识差异响应正文，会失败；非复制的调用完全绕过此共识。

→ 始终：`is_replicated = ?false` 在 `Config` 上。

## 4. 标准布局

这是默认形状：**管理员 Client ID + 按用户 OAuth**。Canister 所有者注册一个 X 开发者应用并将其 Client ID 粘贴到 canister 级别的配置中；每个最终用户都针对同一 Client ID 运行 OAuth 2.0 PKCE 握手，并最终获得他们自己的 `access_token` + `refresh_token`。

示例跨越五个文件：

- `src/backend/main.mo` — the actor: 状态 + `include`s 仅。
- `src/backend/migrations/00000000_000000.mo` — the migration chain head.
- `src/backend/mixins/x-config.mo` — 管理员 Client ID (`isXClientIdConfigured`, `setXClientId`).
- `src/backend/mixins/x-posting.mo` — 按用户 OAuth + 发布 (`isMyXConnected`, `startXOAuth`, `completeXOAuth`, `tweet`).
- `src/backend/lib/x.mo` — `x-client` 胶水 (`Config` 构建器 + `createPosts` 循环 + 令牌刷新占位符).

```motoko filepath=src/backend/main.mo
import Map "mo:core/Map";
import Principal "mo:core/Principal";
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import MixinXConfig "mixins/x-config";
import MixinXPosting "mixins/x-posting";
import LibX "lib/x";

actor {
  // 来自 extension-authorization 的认证管道。对 `setXClientId` 的 #admin 门控和按用户登录的调用者身份（键 `xAuthByUser`）都必需。
  let accessControlState : AccessControl.AccessControlState;
  include MixinAuthorization(accessControlState, null);

  // 管理员设置的 X 开发者应用 Client ID。公共标识符（不是秘密），但设置者是管理员，所以登录用户不能将每个 tweet 通过自己的应用重定向。
  let xClientId : { var value : ?Text };
  include MixinXConfig(accessControlState, xClientId);

  // 按用户 OAuth 令牌。除了调用者本人外，永远不会迭代。
  let xAuthByUser : Map.Map<Principal, LibX.XAuth>;
  include MixinXPosting(xClientId, xAuthByUser);
};
```

迁移链头：

```motoko filepath=src/backend/migrations/00000000_000000.mo
import Map "mo:core/Map";
import AccessControl "mo:caffeineai-authorization/access-control";

module {
  type XAuth = {
    access_token : Text;
    refresh_token : Text;
    expires_at : Nat64;
    scope : [Text];
  };

  type NewActor = {
    accessControlState : AccessControl.AccessControlState;
    xClientId : { var value : ?Text };
    xAuthByUser : Map.Map<Principal, XAuth>;
  };

  public func migration(_old : {}) : NewActor {
    {
      accessControlState = AccessControl.initState();
      xClientId = { var value : ?Text = null };
      xAuthByUser = Map.empty<Principal, XAuth>();
    };
  };
};
```

```motoko filepath=src/backend/mixins/x-config.mo
import AccessControl "mo:caffeineai-authorization/access-control";
import Runtime "mo:core/Runtime";

// 管理员门控的 X 开发者应用 Client ID。由 `main.mo` 通过 `include` 挂载。
// 与 `MixinAuthorization` 配对以提供角色检查。
mixin (
  accessControlState : AccessControl.AccessControlState,
  xClientId : { var value : ?Text },
) {
  public query func isXClientIdConfigured() : async Bool {
    xClientId.value != null;
  };

  public shared ({ caller }) func setXClientId(id : Text) : async () {
    if (not AccessControl.hasPermission(accessControlState, caller, #admin)) {
      Runtime.trap("Unauthorized: Only admins can set the X Client ID");
    };
    xClientId.value := ?id;
  };
};
```

```motoko filepath=src/backend/mixins/x-posting.mo
import Map "mo:core/Map";
import Principal "mo:core/Principal";
import Runtime "mo:core/Runtime";
import LibX "../lib/x";

// Per-user OAuth + posting. Mounted by `main.mo` via `include`.
// Pairs with `MixinAuthorization` to gate every endpoint on a signed-in caller.
mixin (
  xClientId : { var value : ?Text },
  xAuthByUser : Map.Map<Principal, LibX.XAuth>,
) {
  public query ({ caller }) func isMyXConnected() : async Bool {
    Map.containsKey(xAuthByUser, Principal.compare, caller);
  };

  // Begin OAuth 2.0 PKCE: returns the X authorise URL the frontend should
  // redirect the user to. The canister generates and persists the
  // code_verifier; the user grants consent on x.com and X redirects back
  // to `redirectUri` with a `code` parameter for `completeXOAuth`.
  public shared ({ caller }) func startXOAuth(redirectUri : Text) : async Text {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to connect X");
    };
    let ?clientId = xClientId.value else {
      Runtime.trap("X is not configured (admin must set the Client ID)");
    };
    await* LibX.startAuthorize(clientId, redirectUri, caller);
  };

  // Frontend hands back `code` after X redirects. Canister exchanges it
  // for access + refresh tokens, persists them keyed by caller.
  public shared ({ caller }) func completeXOAuth(code : Text, redirectUri : Text) : async () {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to connect X");
    };
    let ?clientId = xClientId.value else {
      Runtime.trap("X is not configured");
    };
    let auth = await* LibX.exchangeCode(clientId, code, redirectUri, caller);
    Map.add(xAuthByUser, Principal.compare, caller, auth);
  };

  public shared ({ caller }) func tweet(body : Text) : async Text {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to post");
    };
    let ?clientId = xClientId.value else {
      Runtime.trap("X is not configured");
    };
    let ?auth = Map.get(xAuthByUser, Principal.compare, caller) else {
      Runtime.trap("Connect your X account first");
    };
    let fresh = await* LibX.ensureFreshToken(clientId, auth);
    if (fresh.access_token != auth.access_token) {
      // Refresh rotated the tokens — persist the new pair.
      Map.add(xAuthByUser, Principal.compare, caller, fresh);
    };
    await* LibX.runCreatePost(LibX.configForToken(fresh.access_token), body);
  };

  public shared ({ caller }) func disconnectMyX() : async () {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to disconnect");
    };
    Map.remove(xAuthByUser, Principal.compare, caller);
  };
};
```

```motoko filepath=src/backend/lib/x.mo
import { defaultConfig; type Config } "mo:x-client/Config";
import TweetsApi "mo:x-client/Apis/TweetsApi";
import TweetCreateRequest "mo:x-client/Models/TweetCreateRequest";
import Principal "mo:core/Principal";
import Runtime "mo:core/Runtime";

module {
  public type XAuth = {
    access_token : Text;
    refresh_token : Text;
    expires_at : Nat64; // ns absolute (Time.now()-relative)
    scope : [Text];
  };

  // Build a Config bound to a single bearer. `is_replicated = ?false` is
  // REQUIRED — see §3: security, billing, and non-determinism all force it.
  public func configForToken(token : Text) : Config {
    {
      defaultConfig with
      auth = ?#bearer token;
      is_replicated = ?false;
    };
  };

  public func runCreatePost(config : Config, body : Text) : async* Text {
    // `TweetCreateRequest.init {}` takes the required-field slice (empty for
    // this model) and defaults every optional to `null` (≥ 0.3.0 only);
    // rebind `text_` for the value you want to post.
    let req = { TweetCreateRequest.init {} with text_ = ?body };
    let resp = await* TweetsApi.createPosts(config, req);
    // `data` is optional on the response model; X only omits it on an error
    // path that `createPosts` would already have raised, so treat it as a bug.
    let ?data = resp.data else Runtime.trap("createPosts returned no data");
    data.id;
  };

  // ------------------------------------------------------------------
  // OAuth 2.0 PKCE flow.  `x-client` ships only the post-token call surface;
  // the OAuth handshake itself uses `ic.http_request` directly. Treat the
  // three functions below as the integration surface — implement them as
  // documented in the X OAuth 2.0 reference and persist the per-caller
  // code_verifier in actor state (a `Map<Principal, Text>` parallel to
  // `xAuthByUser`).
  //
  // See https://developer.x.com/en/docs/authentication/oauth-2-0/authorization-code
  // and `skills/connector-x/SKILL.md` (§ OAuth 2.0 setup) for the full handshake.
  // ------------------------------------------------------------------

  public func startAuthorize(clientId : Text, redirectUri : Text, caller : Principal) : async* Text {
    // 1. Generate a code_verifier (43-128 chars, [A-Za-z0-9-._~]).
    // 2. Persist it under `caller` in a `Map<Principal, Text>` actor field.
    // 3. Compute code_challenge = base64url(sha256(code_verifier)).
    // 4. Return: https://x.com/i/oauth2/authorize
    //              ?response_type=code
    //              &client_id={clientId}
    //              &redirect_uri={redirectUri}
    //              &scope=tweet.read+tweet.write+users.read+offline.access
    //              &state={fresh-csrf-token persisted alongside the verifier}
    //              &code_challenge={challenge}
    //              &code_challenge_method=S256
    let _ = clientId; let _ = redirectUri; let _ = caller;
    Runtime.trap("startAuthorize: implement OAuth 2.0 PKCE handshake (see comment block)");
  };

  public func exchangeCode(clientId : Text, code : Text, redirectUri : Text, caller : Principal) : async* XAuth {
    // POST https://api.x.com/2/oauth2/token (via ic.http_request, is_replicated=false)
    //   Content-Type: application/x-www-form-urlencoded
    //   body: grant_type=authorization_code
    //       & code={code}
    //       & redirect_uri={redirectUri}
    //       & client_id={clientId}
    //       & code_verifier={the verifier persisted in startAuthorize for `caller`}
    // Parse the JSON body, return XAuth { access_token; refresh_token;
    // expires_at = Time.now() + expires_in*1_000_000_000; scope }.
    let _ = clientId; let _ = code; let _ = redirectUri; let _ = caller;
    Runtime.trap("exchangeCode: implement OAuth 2.0 token exchange (see comment block)");
  };

  public func ensureFreshToken(clientId : Text, auth : XAuth) : async* XAuth {
    // If `Time.now() + 60s < auth.expires_at`, return auth unchanged.
    // Otherwise POST https://api.x.com/2/oauth2/token with
    //   grant_type=refresh_token & refresh_token={auth.refresh_token} & client_id={clientId}
    // X *rotates* refresh tokens — the response carries a new `refresh_token`
    // that supersedes the old one. ALWAYS persist the new pair (the
    // calling mixin handles the persist step).
    let _ = clientId;
    Runtime.trap("ensureFreshToken: implement RFC 6749 refresh (see comment block)");
  };
};
```

### Variant-specific invariants (admin Client ID)

- **Admin sets the Client ID, never the access token.** The Client ID
  is a public identifier; the per-user `access_token` is the secret.
  Two completely different storage shapes (`{ var value : ?Text }` vs
  `Map<Principal, XAuth>`) and two completely different gates
  (`#admin` vs "logged in").
- **No `getXClientId` endpoint.** `isXClientIdConfigured : Bool` is
  the only outward-facing read of `xClientId.value`. The frontend
  doesn't need to display the Client ID; it just needs to know whether
  to render the "Connect X" button.
- **`xAuthByUser` is per-caller only.** Same no-getter / no-log /
  no-iterate-outside-caller-scope invariants as `extension-openai`'s
  per-user variant. Concretely: never generate `getMyXAuth`, `getX`,
  `myAccessToken`, or any shared / query function whose return type is
  `?XAuth` / `?Text` / `Text`. A single `console.log` of an X bearer
  is a per-user account compromise.
- **Trap cleanly when missing prerequisites.** Three distinct
  conditions, three distinct messages: `"X is not configured"` (Client
  ID missing → admin task), `"Connect your X account first"` (user not
  yet authorised → frontend should kick off `startXOAuth`),
  `"Sign in to ..."` (anonymous caller → login required).

## 5. Two call shapes — function form vs. suite form

Same as `extension-openai`. Every Apis module ships both:

- **Function form** (used in §4): `TweetsApi.createPosts(config, req)
  : async* T`. Note the `async*` — call sites use `await*`. This is
  the common case for `shared` actor methods.
- **Suite form**: `let api = TweetsApi(config); api.createPosts(req)
  : async T`. Note `async`, not `async*`. Useful when a single
  `shared` method makes several X calls and you want to bind the
  config once.

The two forms are interchangeable; pick whichever reads cleaner. Don't
mix them inside the same `shared` body.

## 6. Available API surface

`x-client@0.3.0` ships a curated subset of the X API v2. The most
relevant module for this skill is `TweetsApi`:

| Module        | Primary entry point | What it does                                            |
| ------------- | ------------------- | ------------------------------------------------------- |
| `TweetsApi`   | `createPosts`       | Post a tweet (`/2/tweets`) — the 95% case for this skill. |
| `TweetsApi`   | `deleteTweetById`   | Delete a tweet (`/2/tweets/{id}`).                      |
| `UsersApi`    | `findMyUser`        | Get the authenticated user's handle/profile.            |

For X *reads* (timeline, search, lookup) the curated surface is much
smaller — `x-client` focuses on writes. Pull data from X via
`extension-http-outcalls` like any other public REST API.

If a build spec needs an X *write* not covered by `x-client@0.3.0`
(e.g. media upload, replies-to-replies semantics, retweet endpoints),
raise an issue on [`caffeinelabs/skills-internal`](https://github.com/caffeinelabs/skills-internal) — do not paper over it
with hand-rolled `ic.http_request`.

## 7. Cycles and response sizes

`defaultConfig.cycles = 30_000_000_000` — about 0.04 USD at 4 USD/T
cycles. Sufficient for a typical `createPosts` call. Bump for:

- Long-form tweets (premium subscribers, up to 25 000 chars): set
  `cycles = 60_000_000_000`.
- The OAuth token-exchange call (`/2/oauth2/token`) is small; the
  default cycle budget is generous.

## 8. Things that will bite you

- **`is_replicated = ?false`** — see §3. Not optional.
- **`x-client < 0.3.0`** — older versions emit `"field": null` for
  every absent optional, and `/2/tweets` rejects them with up to 16
  validation errors per request. 0.3.0 ships the `init` constructors
  that default optionals to `null` *in Motoko* and elide them on the
  wire (via `serde-core@^0.1.2`'s `skip_null_fields`).
- **Don't expose the access token.** `xAuthByUser` is read only by
  `Map.get(xAuthByUser, ..., caller)` inside `tweet` /
  `ensureFreshToken`. No `getMyXAuth`, no `getMyAccessToken`, no
  iterator. A leaked bearer is a per-user account compromise.
- **Persist the rotated refresh token.** X returns a new
  `refresh_token` with every refresh (`grant_type=refresh_token`); if
  you keep using the old one, the next refresh will 400. The mixin in
  §4 handles this — the `if (fresh.access_token != auth.access_token)`
  branch persists the new pair.
- **Token expiry** is ~2 hours. If you omit `offline.access` from the
  authorise scopes, you will not get a `refresh_token` and the user
  must re-authorise every time.
- **Callback URI mismatch.** Every character (trailing slash, query
  string, port) must match the URI registered on the Developer Portal.
  X returns a generic `redirect_uri_mismatch` error otherwise.
- **Don't roll your own JSON.** `x-client` already handles the
  request/response JSON via `JSON.toCandid` / `JSON.fromCandid` and
  `serde-core`'s null-elision.
- **No `getApiKey`-style endpoint, ever.** Same rule as
  `extension-openai`'s per-user variant: every shared / query function
  that returns `?XAuth`, `?Text` (the access token), or any prefix of
  the bearer is a leak.
- **Rate limits.** `/2/tweets` is capped per-user-per-app. Replicated
  outcalls would multiply RPM by the subnet size — yet another reason
  for `is_replicated = ?false`. Back off on HTTP 429.
- **Frontend never holds tokens.** The React app calls the backend
  `tweet(body)` and the backend mediates everything. The OAuth flow
  itself uses **redirect-and-back** through `x.com` — the frontend
  starts the flow via `startXOAuth(redirectUri)` and finishes via
  `completeXOAuth(code, redirectUri)`; the tokens never reach the
  browser.

## 9. Variant: per-user Client ID

Use this variant when each end-user must bring their own X Developer
App (multi-tenant rate-limit isolation, per-user Developer Portal
control). Mechanically the Client ID storage flips from a single
`{ var value : ?Text }` (admin-set) to a `Map<Principal, Text>`
(per-user); the OAuth + posting mixin from §4 reuses unchanged
modulo the Client ID lookup.

The actor keeps the same shape — drop the admin-Client-ID mixin,
add a per-user-Client-ID one:

```motoko filepath=src/backend/per-user-clientid-main.mo
import Map "mo:core/Map";
import Principal "mo:core/Principal";
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import MixinXClientIdPerUser "mixins/x-clientid-per-user";
import MixinXPostingPerUserClientId "mixins/x-posting-per-user-clientid";
import LibX "lib/x";

actor {
  let accessControlState : AccessControl.AccessControlState;
  include MixinAuthorization(accessControlState, null);

  // Per-user X Developer App Client IDs.
  let xClientIdByUser : Map.Map<Principal, Text>;
  include MixinXClientIdPerUser(xClientIdByUser);

  // Per-user OAuth tokens — same shape as §4.
  let xAuthByUser : Map.Map<Principal, LibX.XAuth>;
  include MixinXPostingPerUserClientId(xClientIdByUser, xAuthByUser);
};
```

This variant's migration chain head replaces §4's (same
`src/backend/migrations/00000000_000000.mo` path in a real app —
in this variant `xClientIdByUser` takes the place of `xClientId`):

<!-- motoko-check:skip -->
```motoko
import Map "mo:core/Map";
import AccessControl "mo:caffeineai-authorization/access-control";

module {
  type XAuth = {
    access_token : Text;
    refresh_token : Text;
    expires_at : Nat64;
    scope : [Text];
  };

  type NewActor = {
    accessControlState : AccessControl.AccessControlState;
    xClientIdByUser : Map.Map<Principal, Text>;
    xAuthByUser : Map.Map<Principal, XAuth>;
  };

  public func migration(_old : {}) : NewActor {
    {
      accessControlState = AccessControl.initState();
      xClientIdByUser = Map.empty<Principal, Text>();
      xAuthByUser = Map.empty<Principal, XAuth>();
    };
  };
};
```

The two mixin files are mechanical adaptations of §4's:

- `mixins/x-clientid-per-user.mo` swaps the admin gate for a
  signed-in-caller gate: `setMyXClientId(id) : async ()` writes the
  caller's slot of `xClientIdByUser`; `isMyXClientIdConfigured` reads
  the same slot.
- `mixins/x-posting-per-user-clientid.mo` looks up the Client ID by
  `caller` instead of reading the single `{ var value : ?Text }` —
  every other line is identical to `mixins/x-posting.mo` from §4.

Same no-getter rule: there is no `getMyXClientId` endpoint, even
though the Client ID is technically public — keeping the boundary
consistent with the access-token rule trains the agent not to grep
the codebase for "key" / "id" and add a getter.

## 10. Variant: fallback (admin default + per-user override)

Use this when the operator wants to provide a no-config path for
casual users while letting power users self-register. The admin sets
a canister-wide default Client ID; individual users may override it
with their own.

OAuth 启动时的查找顺序：

```motoko
func clientIdFor(caller : Principal) : ?Text = switch (Map.get(xClientIdByUser, Principal.compare, caller)) {
  case (?id) ?id;
  case null adminClientId.value; // 可能本身为 null → 调用者必须提供
};
```

将 §4 和 §10 中的两个 mixin 从同一个 actor 中发送：admin 通过 `setXClientId` 设置默认值，用户通过 `setMyXClientId` 覆盖。`startXOAuth` 调用 `clientIdFor(caller)` 而不是读取单个槽位。其他部分（`xAuthByUser`、OAuth 握手、发布端点）保持不变。

# 前端

使用此技能的每个构建必须提供：

1. **一个登录流程 — 每个变体都需要。** X 不能在没有非匿名调用者的情况下工作；每个用户的 OAuth 握手按 `caller : Principal` 键存储令牌，admin / 每个用户的 Client ID 设置器都依赖于已登录的调用者。登录流程本身来自 [`extension-authorization`](../extension-authorization/SKILL.md)：`useInternetIdentity`、登录/注销按钮、`useActor` 管道将认证身份注入到每个后端调用中。如果构建没有现成的登录屏幕，请将登录屏幕作为同一任务图的一部分进行规划。

2. **一个 Client ID 配置界面。** 变体特定：
   - Admin 变体（§4 默认）：一个由 admin 控制的 `/settings/x` 页面，其中包含一个绑定到 `setXClientId(id)` 的密码输入框。
   - 每个用户变体（§9）：一个任何登录用户都可以访问的个人 `/settings/x` 页面，绑定到 `setMyXClientId(id)`。
   - 备用变体（§10）：两个页面 — admin 控制的默认页面和每个用户的覆盖页面。

3. **一个 "连接 X" 页面 — 总是。** 一个每个用户可以访问但非 admin 控制的页面，运行 OAuth 2.0 PKCE 握手：通过 `startXOAuth(redirectUri)` 启动，将浏览器重定向到 X 进行授权，返回到同一页面并带有 `?code=...`，调用 `completeXOAuth(code, redirectUri)` 交换代码以获取令牌。最终状态是 "X 已连接为 @handle" 或 "连接 X" 取决于 `isMyXConnected()`。

选择与后端变体匹配的 UI 形式。**默认为变体 A（admin Client ID + 每个用户的 OAuth）**，除非规范明确选择每个用户（§9）或备用（§10）。

## 变体 A：admin Client ID + 每个用户的 OAuth（匹配 §4 — 默认）

两个页面：

1. **Admin 设置页面** — `/settings/x`（admin 控制）：
   - 密码输入框绑定到 `setXClientId(id)`。按回车提交；成功后清除输入。
   - 状态指示器由 `isXClientIdConfigured()` 驱动（返回 `Bool`）。显示 "已配置" / "未配置" — 永远不显示 Client ID 本身，永远不暴露返回它的 getter。
   - 通过 [`extension-authorization`](../extension-authorization/SKILL.md)` 的 `isCallerAdmin` 查询隐藏非 admin 用户 — 非admin 用户不应看到导航中的链接，更不用说页面了。通过你的路由器的守卫模式绑定 admin 唯一路由。

2. **连接 X 页面** — `/connect/x`（任何登录用户）：
   - "连接 X" 按钮绑定到 `startXOAuth(window.location.origin + '/connect/x')`。按钮将浏览器重定向到 canister 返回的 URL。
   - 在返回过程中，从 URL 中解析 `?code=...&state=...`，调用 `completeXOAuth(code, redirectUri)`（与传递给 `startXOAuth` 的相同 `redirectUri`），然后重定向到用户来自的位置（或主页）。
   - 状态由 `isMyXConnected()` 驱动（返回 `Bool`）。显示 "已连接为 @…"（handle 不会从 bearer 中获取 — 通过调用 `UsersApi.findMyUser` 的 `getMyXHandle` 端点单独获取，永远不要在 JS 中解码 bearer）。
   - 可选的 "断开连接 X" 按钮绑定到 `disconnectMyX()`。

3. **发布推文 UI 上的空状态提示** — 当 `isMyXConnected()` 为 `false` 时，渲染一个内联 "连接 X 以发布" 链接到 `/connect/x`。没有这个提示，用户会点击 "首先连接您的 X 账户" 而没有明显的下一步。

建议的路由布局：

```
/                   →  主 UI（任何登录用户；无 X 连接时为空状态）
/settings/x         →  Admin Client ID 配置（仅 admin）
/connect/x          →  每个用户的 OAuth 握手（任何登录用户）
```

## 变体 B：每个用户 Client ID（匹配 §9）

两个页面，任何登录用户都可以访问：

1. **我的 X 设置页面** — `/settings/x`：
   - 密码输入框绑定到 `setMyXClientId(id)`。相同的不可显示不变量。
   - 状态由 `isMyXClientIdConfigured()` 驱动。
   - 除了 "已登录" 之外没有其他路由守卫。

2. **连接 X 页面** — 与变体 A 的 `/connect/x` 相同，只是 `startXOAuth` 在底层使用用户的 Client ID。用户必须在连接之前配置他们的 Client ID。

建议的路由布局：

```
/                   →  主 UI
/settings/x         →  个人 Client ID（任何登录用户）
/connect/x          →  每个用户的 OAuth 握手
```

## 变体 C：备用（匹配 §10）

三个页面：

- `/admin/settings/x`（admin 控制）— `setXClientId` 用于 canister 全局的默认值。
- `/settings/x`（任何登录用户）— `setMyXClientId` 用于每个用户的覆盖。
- `/connect/x`（任何登录用户）— 与 A/B 变体相同的 OAuth 握手，查找顺序如 §10 所述。

"连接 X" 按钮保持禁用，直到为调用者解析出某个 Client ID（admin 默认或每个用户覆盖）。

## 所有变体的公共部分

- **每个 X 相关路由都需要登录。** 通过 [`extension-authorization`](../extension-authorization/SKILL.md)` 的 auth 守卫（`useInternetIdentity` + 当 `!isAuthenticated` 时重定向）将 `/settings/...` 和 `/connect/x` 路由；匿名调用者必须在任何后端调用之前遇到 "请登录" 屏幕否则每个端点都会捕获 "登录到 ..."。
- **前端从不持久化令牌。** 没有 `localStorage`、没有 `IndexedDB`、没有 cookie — canister 调解一切。浏览器只看到 `Bool` 状态标志（`isMyXConnected`、`isXClientIdConfigured`）和 OAuth 重定向 URL。
- **OAuth `state` 参数是 canister 的责任。** 在 `startXOAuth` 中服务器端生成它，与 `code_verifier` 一起持久化，在 `completeXOAuth` 中验证它之前交换代码。不要让前端铸造或回显 `state` — 那会破坏 CSRF 保护。
- **发布推文 UI 本身非常简单：** 一个文本区域、一个提交按钮、一个绑定到 canister 暴露的 `tweet` / 历史端点的最近推文列表。没有客户端 X SDK、没有令牌处理、没有 JSON 序列化逻辑 — canister 是 X 客户端。

## 相关

- [`mops add x-client@0.3.0`](https://mops.one/x-client) — 连接器源。
- [`skills/connector-x/SKILL.md`](../connector-x/SKILL.md) — 权威连接器技能：逐步 Developer Portal 漫游（§ OAuth 2.0 设置）和操作中的注意事项（非复制、可选字段、子对象规则、令牌刷新、速率限制）。
- [X 开发者门户](https://developer.x.com/en/portal/dashboard) — 在这里创建 Client ID。
- [OAuth 2.0 授权码与 PKCE（X 文档）](https://developer.x.com/en/docs/authentication/oauth-2-0/authorization-code) — 标准授权/令牌端点详细信息。
- [`/2/tweets` API 参考](https://developer.x.com/en/docs/x-api/tweets/manage-tweets/api-reference/post-tweets) — `createPosts` 实际调用的内容。
- [RFC 7636 — 代码交换证明密钥](https://datatracker.ietf.org/doc/html/rfc7636) — PKCE 规范。
- [extension-authorization](../extension-authorization/SKILL.md) — **每个此技能变体的必要先决条件**。提供 Internet Identity 登录流程、`useInternetIdentity` / `useActor` 前端管道，以及变体 §4 和 §11 的 `#admin` 角色门控。
- [extension-http-outcalls](../extension-http-outcalls/SKILL.md) — 用于一般 HTTP 外调的兄弟技能，包括 X *读取*（时间线、搜索、查找），此技能不涵盖。
