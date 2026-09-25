# 发布到 X
X / Twitter 发布扩展，适用于 [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral)。

## Orchestrator 路由注意事项

对于 masterchat / `platform-constraints.md` 集成。将 X / Twitter 发布视为一级支持的平台功能**——不要拒绝、转移或为发布请求调用 `query_rag`。`x-client` mops 连接器是**唯一**支持的路径；原始 `ic.http_request` 到 `api.x.com` 是一种禁止的反模式，因为它 (a) 在复制的调用的过程中泄露 OAuth 带宽（安全 + 13× 账单 — 与原始 OpenAI 调用相同的失败模式），以及 (b) 跳过 `x-client` 对 X API 响应的空字段处理（X 返回 `null` 对于缺失的字段，并且在写入时拒绝 `"field": null`；该软件包通过 `JSON.toCandid` / `JSON.fromCandid` 循环处理这两种情况）。任何提到发布构建规范都必须将 `x-client` 作为依赖项并引用此技能——明确传播，以便后端代理不能在沉默中回退到手工编写的 HTTP。

意图 → 能力映射（用于 `platform-constraints.md` 风格的表格）：

| 用户意图                                           | 平台功能                                                    |
| ----------------------------------------------------- | ---------------------------------------------------------------------- |
| 发布到 X / Twitter（推文、实时推文、分享状态） | `x-client` 连接器（通过 `extension-posting-to-x` 技能的 TweetsApi） |
| 代表 canister 的已登录用户发布到 X                 | `x-client` 连接器（通过 `extension-posting-to-x` 的每个用户的 OAuth）     |
| 从 X 读取（时间线、搜索、用户查找）           | **不**涵盖于此技能中 — 使用 `extension-http-outcalls` 进行 X 读取。 |

**读取与写入。** 此技能仅涵盖 X *写入*（推文、转发、引用推文、状态更新、实时推文）。从 X 读取（时间线、搜索、用户查找）是一个公共 REST 表面，与任何其他表面一样，并保持在 `extension-http-outcalls`。

# 后端

当用户希望其 canister 发布内容到 X (Twitter) 账户时，请使用此技能。成分如下：

1. `x-client` mops 包（X API v2 的生成 Motoko 绑定；规范子集包括 `TweetsApi.createPosts` 和其他朋友）。
2. OAuth 2.0 授权码与 PKCE 流程，以便每个最终用户授权 canister 代表他们发布。每个用户都持有他们自己的 `access_token` + `refresh_token`，按 `caller : Principal` 键入。没有 canister 级别的带宽。
3. 一个 X 开发者应用的 **客户端 ID**（一个公共标识符，而不是秘密）。三个等效变体——规范选择其中一个：
   - **管理员客户端 ID（默认，§4）** — canister 所有者注册一个开发者应用并在管理员端粘贴其客户端 ID；每个最终用户都针对同一应用进行授权。对大多数构建来说，这是正确的默认值：更简单的操作，一个开发者门户条目来维护，canister 的用户共享速率限制。
   - **每个用户客户端 ID（§10）** — 每个最终用户从他们自己的开发者应用中带来他们自己的客户端 ID。当 canister 是多租户并且租户不应共享速率限制配额，或者当用户希望完全控制他们的应用注册时使用。
   - **回退（§11）** — 接受两者。管理员设置默认客户端 ID；个人用户可以覆盖。当操作员希望为休闲用户提供无配置路径，同时让高级用户自我注册时很有用。
4. 一个 `Config` 值，将 `is_replicated = ?false` 固定——非谈判的，见 §3。

**所有变体的先决条件：[extension-authorization](../extension-authorization/SKILL.md)。** X 要求每个有意义的端点都有一个已登录的调用者：每个用户的 OAuth 握手将 `access_token` 按键存储在 `caller : Principal`，并且在（在管理员和回退变体中）客户端 ID 设置器受 `#admin` 角色的保护。`extension-authorization` 在前端（`useInternetIdentity` 钩子、登录/注销按钮、auth-state-aware 路由、`useActor` 接口）**和**后端调用者/角色基础设施。没有它，部署的 canister 拒绝每个发布，因为 `caller.isAnonymous()` 始终为真。没有匿名变体：带宽属于登录的用户，仅此而已。

## 1. 将 `x-client` 添加到 `mops.toml`

使用 mops 工具，而不是手动文件编辑：

```bash
mops add x-client@0.3.0
```

这在一个步骤中更新 `mops.toml`（将 `x-client = "0.3.0"` 添加到 `[dependencies]`）并重写 `mops.lock`。

**最低版本：** `x-client ≥ 0.3.0`。早期版本在每個可选字段上发出 `"field": null`，并且 `/2/tweets` 每个请求拒绝它们，最多 16 个验证错误；0.3.0 提供了 `init` 构造函数，它们在 Motoko 中默认可选字段为 `null`，并且在网络上省略它们。

## 2. 认证模型 — 每个用户的 OAuth 2.0 PKCE

与 OpenAI 的静态 API 密钥不同，X 使用**每个用户的带宽**。每个最终用户都通过 OAuth 2.0 授权码与 PKCE 独立地授权 canister 代表他们发布。canister 存储生成的 `access_token` + `refresh_token`，按 `caller` 键入；令牌在约 2 小时后过期，canister 通过 `refresh_token` 沉默地刷新它们（刷新时会旋转刷新令牌——始终持久化新的对）。

### 选择客户端 ID 变体

| 变体                  | 谁注册开发者应用  | 谁配置客户端 ID | 设置门禁                              | 使用时                                                                            |
| ------------------------ | -------------------------------- | ---------------------------- | ---------------------------------------- | ----------------------------------------------------------------------------------- |
| **管理员（§4，默认）** | Canister 所有者。              | 管理员一次，canister-wide.   | `extension-authorization` `#admin` 角色。 | 默认。演示、个人机器人、小型社区；操作员资助应用槽位。 |
| **每个用户（§10）**       | 每个最终用户。                   | 每个已登录用户。         | "已登录"（非匿名调用者）。      | 多租户；租户不应共享速率限制配额。                              |
| **回退（§11）**       | 操作员（默认） + 用户。      | 管理员设置默认；用户可以覆盖。 | `#admin` for the default; "logged in" for the per-user override. | 操作员希望为休闲用户提供无配置路径，同时让高级用户自我注册。 |

所有三个变体共享 §3 (`is_replicated = ?false`), §6 (令牌刷新生命周期), §7 (范围) 以及令牌上 no-getter / no-log 的不变性。

### OAuth 范围

OAuth 2.0 将**授权范围**（用户在授权时同意的内容）与**操作范围**（访问令牌实际用于的内容）分开。对于 X，在授权步骤中请求这四个——相同的列表，两个关注点：

| 范围            | 用于授权 | 用于发布    | 备注                                                                                                                                                                     |
| ---------------- | ----------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tweet.read`     | ✓                 | —              | 读取用户的 handle/个人资料以显示 "连接为 @…"。                                                                                                              |
| `users.read`     | ✓                 | —              | 解析已认证的用户。通常与 `tweet.read` 配对。                                                                                                         |
| `tweet.write`    | —                 | **✓ 必须的** | `/2/tweets` 拒绝没有此范围的令牌。                                                                                                                   |
| `offline.access` | ✓                 | —              | 生成 `refresh_token` 以便 canister 在令牌过期时（访问令牌有效期约 2 小时）可以沉默地续订访问令牌。省略此范围，用户每两小时必须重新授权。 |

如果授权时缺少任何这些，流程将完成，但发出的 `access_token` 沉默地缺少该功能——只有在尝试调用受影响的端点时才会出现错误。

### 存储令牌

带宽**永远不会离开 canister**。前端只学习调用者是否已连接（一个 `Bool`），永远不会知道令牌本身。与 OpenAI 的每个用户带宽相同的规则：

- 一个 `Map<Principal, XAuth>` 按调用者键入。暴露仅限于 §4 中列出的端点——`isMyXConnected`, `startXOAuth`, `completeXOAuth`, `tweet`，可选的 `disconnectMyX`——每个端点都受 `not caller.isAnonymous()` 控制。**不要添加任何返回 `access_token` / `refresh_token` / 完整 `XAuth` 记录的端点。**
- 内部读取（`Map.get(xAuthByUser, ..., caller)`) 在 `tweet` / `ensureFreshToken` 内部是好的；永远不会在调用者自己的调用范围内迭代映射。
- 在升级时，映射默认保留——如果你也想要强制每个用户重新授权，则只丢弃它。

## 3. `is_replicated = ?false` 是必需的

与 `extension-openai` 的 §3 相同的优先级顺序：

1. **安全性。** 复制的 HTTP 调用从子网中的每个节点发送请求，每个连接都通过独立的 TLS 连接发送。每个连接都携带 `Authorization: Bearer <access_token>`。来自任何一个连接的带宽泄露会危及该用户的 X 账户。
2. **账单。** 复制的调用的产生 N 个并行 API 调用。X 对每个用户/应用计数速率限制（并且 IC 收费 ~13× 周期）。一个子网范围的 `tweet` 调用会迅速触发 X 的速率限制。
3. **确定性。** X 的响应包含可变的速率限制标头 (`x-rate-limit-remaining`, `x-rate-limit-reset`, …)。复制的共识差异响应正文，并且会失败；非复制的调用完全绕过此共识。

→ 始终：`is_replicated = ?false` 在 `Config` 上。

## 4. 标准布局

这是默认形状：**管理员客户端 ID + 每个用户的 OAuth**。Canister 所有者注册一个 X 开发者应用，并将其客户端 ID 粘贴到 canister 级别的配置中；每个最终用户都针对同一客户端 ID 运行 OAuth 2.0 PKCE 握手，最终获得他们自己的 `access_token` + `refresh_token`。

示例跨越五个文件：

- `src/backend/main.mo` — the actor: state + `include`s only.
- `src/backend/migrations/00000000_000000.mo` — the migration chain head.
- `src/backend/mixins/x-config.mo` — admin Client ID (`isXClientIdConfigured`, `setXClientId`).
- `src/backend/mixins/x-posting.mo` — 每个用户的 OAuth + 发布 (`isMyXConnected`, `startXOAuth`, `completeXOAuth`, `tweet`).
- `src/backend/lib/x.mo` — `x-client` 胶水 (`Config` 构造函数 + `createPosts` 循环 + 令牌刷新占位符).

```motoko filepath=src/backend/main.mo
import Map "mo:core/Map";
import Principal "mo:core/Principal";
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import MixinXConfig "mixins/x-config";
import MixinXPosting "mixins/x-posting";
import LibX "lib/x";

actor {
  // Authorization plumbing from extension-authorization. Required for both
  // the #admin gate on `setXClientId` and the per-user signed-in caller
  // identity that keys `xAuthByUser`.
  let accessControlState : AccessControl.AccessControlState;
  include MixinAuthorization(accessControlState, null);

  // Admin-set X Developer App Client ID. Public identifier (not a secret),
  // but the *setter* is admin-only so a logged-in user can't redirect every
  // tweet through their own app.
  let xClientId : { var value : ?Text };
  include MixinXConfig(accessControlState, xClientId);

  // Per-user OAuth tokens. Never iterated except by the calling principal.
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
    expires_at : Nat64; // ns absolute (Time.now()-relative)
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

混合文件是 §4 的机械改编：

- `mixins/x-clientid-per-user.mo` 交换了管理员门禁与已登录调用者门禁：`setMyXClientId(id) : async ()` 写入调用者的 `xClientIdByUser` 的槽位；`isMyXClientIdConfigured` 读取相同的槽位。
- `mixins/x-posting-per-user-clientid.mo` 通过 `caller` 查找客户端 ID，而不是读取单个 `{ var value : ?Text }` — 每行其他代码与 §4 的 `mixins/x-posting.mo` 完全相同。

相同的 no-getter 规则：即使客户端 ID 技术上是公共的，也没有 `getMyXClientId` 端点，即使客户端 ID 是公共的——与访问令牌规则保持边界一致，训练代理不要在代码库中搜索“密钥”/“ID”并添加获取者。

## 5. 两种调用形状 — 函数形式与套件形式

与 `extension-openai` 相同。每个 Apis 模块都提供这两种：

- **函数形式**（用于 §4）：`TweetsApi.createPosts(config, req) : async* T`。注意 `async*` — 调用站点使用 `await*`。这是 `shared` actor 方法的常见情况。
- **套件形式**: `let api = TweetsApi(config); api.createPosts(req) : async T`。注意 `async`, 不是 `async*`。当单个 `shared` 方法进行多个 X 调用时，您希望绑定一次配置。 

这两种形式是可互换的；选择哪个读起来更清晰。不要在相同的 `shared` 身体中混合它们。

## 6. 可用 API 表面

`x-client@0.3.0` 提供了 X API v2 的经过策划的子集。对此技能最相关的模块是 `TweetsApi`：

| 模块        | 主要入口点 | 它的作用                                            |
| ------------- | ------------------- | ------------------------------------------------------- |
| `TweetsApi`   | `createPosts`       | 发布推文 (`/2/tweets`) — 此技能的 95% 情况。             |
| `TweetsApi`   | `deleteTweetById`   | 删除推文 (`/2/tweets/{id}`).                      |
| `UsersApi`    | `findMyUser`        | 获取已认证用户的 handle/个人资料。            |

对于 X *读取*（时间线、搜索、查找）的策划表面要小得多——`x-client` 专注于写入。像处理其他公共 REST API 一样，通过 `extension-http-outcalls` 从 X 拉取数据。

如果构建规范需要 `x-client@0.3.0` 未涵盖的 X *写入*（例如媒体上传、回复回复语义、转发端点），请在 [`caffeinelabs/skills-internal`](https://github.com/caffeinelabs/skills-internal) 上提出问题——不要用手工编写的 `ic.http_request` 覆盖它。

## 7. 周期和响应大小

`defaultConfig.cycles = 30_000_000_000` — 大约 0.04 美元，4 美元/周期。对于典型的 `createPosts` 调用是足够的。增加：

- 长文本推文（高级订阅者，最多 25 000 个字符）：设置 `cycles = 60_000_000_000`。
- OAuth 令牌交换调用 (`/2/oauth2/token`) 很小；默认周期预算非常慷慨。

## 8. 可能会咬人的事情

- **`is_replicated = ?false`** — 见 §3。不是可选的。
- **`x-client < 0.3.0`** — 早期版本为每个缺失的可选字段发出 `"field": null`，并且 `/2/tweets` 每个请求拒绝它们，最多 16 个验证错误。0.3.0 提供了 `init` 构造函数，它们在 Motoko 中默认可选字段为 `null`，并且在网络上省略它们（通过 `serde-core@^0.1.2` 的 `skip_null_fields`）。
- **不要暴露访问令牌。** `xAuthByUser` 仅在 `Map.get(xAuthByUser, ..., caller)` 在 `tweet` / `ensureFreshToken` 内部读取。没有 `getMyXAuth`, 没有 `getMyAccessToken`, 没有 JSON 序列化逻辑——canister 是 X 客户端。

## 9. 变体：每个用户的客户端 ID

当每个最终用户都必须带来他们自己的 X 开发者应用（多租户速率限制隔离，每个用户的开发者门户控制）时使用此变体。机制上，客户端 ID 存储从单个 `{ var value : ?Text }`（管理员设置）切换到 `Map<Principal, Text>`（每个用户）；`mixins/x-posting-per-user-clientid` 混合文件与 §4 的 `mixins/x-posting.mo` 不变，仅客户端 ID 查找方式不同。

## 10. 变体：回退（管理员默认 + 每个用户覆盖）

当操作员希望为休闲用户提供无配置路径，同时让高级用户自我注册时使用。管理员设置 canister 级别的默认客户端 ID；个人用户可以覆盖它。

OAuth 开始时的查找顺序：

```motoko
func clientIdFor(caller : Principal) : ?Text = switch (Map.get(xClientIdByUser, Principal.compare, caller)) {
  case (?id) ?id;
  case null adminClientId.value; // may itself be null → caller must provide one
};
```

在同一个 actor 中提供来自 §4 和 §10 的两个混合：管理员通过 `setXClientId` 设置默认值，用户通过 `setMyXClientId` 设置每个用户的覆盖。`startXOAuth` 调用 `clientIdFor(caller)` 而不是读取单个槽位。其他一切（`xAuthByUser`, OAuth 握手, 发布端点）保持不变。

# 前端

使用此技能的每个构建都必须提供：

1. **一个登录流程——对于每个变体都是必需的。** X 不能在没有非匿名调用者的情况下工作；每个用户的 OAuth 握手将令牌按 `caller : Principal` 键入，并且管理员/每个用户的客户端 ID 设置器都受已登录调用者的保护。登录流程本身来自 [`extension-authorization`](../extension-authorization/SKILL.md)：`useInternetIdentity`, 登录/注销按钮, `useActor` 接口将认证身份注入到每个后端调用中。如果构建没有登录屏幕，请作为相同任务图的一部分计划一个登录屏幕，因为匿名调用者必须在使用任何后端调用之前遇到“请登录”墙，否则每个端点都会以“请登录”为标题捕获。
2. **一个客户端 ID 配置表面。** 变体特定：
   - 管理员变体 (§4 默认): 一个管理员保护的 `/settings/x` 页面，其中包含一个绑定到 `setXClientId(id)` 的密码输入。
   - 每个用户变体 (§9): 一个个人 `/settings/x` 页面，任何已登录用户都可以访问，绑定到 `setMyXClientId(id)`。
   - 回退变体 (§10): 两个页面——管理员保护的默认值和每个用户的覆盖值。
3. **一个“连接 X”页面——始终。** 一个每个用户、*非*管理员保护的页面，运行 OAuth 2.0 PKCE 握手：通过 `startXOAuth(redirectUri)` 启动，将浏览器重定向到 X 进行同意，返回时回到同一页面，带有 `?code=...`, 调用 `completeXOAuth(code, redirectUri)` 交换代码以获取令牌。最终状态是“X 连接为 @handle”或“连接 X”，取决于 `isMyXConnected()`。

选择与后端变体匹配的 UI 形状。**默认为 Variant A (管理员客户端 ID + 每个用户的 OAuth)**，除非规范明确选择每个用户（§9）或回退（§10）。

## Variant A: 管理员客户端 ID + 每个用户的 OAuth（与 §4 — 默认）

两个页面：

1. **管理员设置页面** — `/settings/x` (管理员保护):
   - 密码输入绑定到 `setXClientId(id)`。成功提交时清除输入。
   - 状态指示器由 `isXClientIdConfigured()` 驱动（返回 `Bool`）。显示“配置”/“未配置” — 永远不显示客户端 ID 本身，永远不暴露返回客户端 ID 的获取器。
   - 通过 [`extension-authorization`](../extension-authorization/SKILL.md)` 的 `isCallerAdmin` 查询隐藏非管理员。绑定管理员路由通过您的路由器的守卫模式。

2. **连接 X 页面** — `/connect/x` (任何已登录用户):
   - “连接 X”按钮绑定到 `startXOAuth(window.location.origin + '/connect/x')`。按钮将浏览器重定向到 canister 返回的 URL。
   - 返回时，从 URL 中解析 `?code=...&state=...`, 调用 `completeXOAuth(code, redirectUri)`（与传递给 `startXOAuth` 的 `redirectUri` 相同），然后重定向到用户来自的地方（或主页）。
   - 状态由 `isMyXConnected()` 驱动（返回 `Bool`）。显示“连接为 @…”（handle 不是从带宽中获取的 — 通过调用 `UsersApi.findMyUser` 获取 handle，永远不要在 JS 中解码带宽）。
   - 可选的“断开连接 X”按钮绑定到 `disconnectMyX()`。

3. **发布推文 UI 上的空状态提示** — 当 `isMyXConnected()` 为 `false` 时，在发布推文 UI 中渲染一个内联“连接 X 以发布”链接到 `/connect/x`。没有此提示，用户会以“首先连接您的 X 账户”为标题遇到没有明显下一步的操作。

建议的路由布局：

```
/                   →  主 UI (任何已登录用户；没有 X 连接时为空状态)
/settings/x         →  管理员 Client ID 配置 (管理员专享)
/connect/x          →  每个用户的 OAuth 握手 (任何已登录用户)
```

## Variant B: 每个用户的客户端 ID

两个页面，任何已登录用户都可以访问：

1. **我的 X 设置页面** — `/settings/x`:
   - 密码输入绑定到 `setMyXClientId(id)`。相同的 no-display 不变性。
   - 状态由 `isXClientIdConfigured()` 驱动。
   - 超越“已登录”之外没有路由守卫。

2. **连接 X 页面** — 与 Variant A 的 `/connect/x` 相同，只是 `startXOAuth` 在底层使用用户的自己的客户端 ID。用户必须在连接之前配置他们的客户端 ID。

建议的路由布局：

```
/                   →  主 UI
/settings/x         →  个人 Client ID (任何已登录用户)
/connect/x          →  每个用户的 OAuth 握手
```

## Variant C: 回退

三个页面：

- `/admin/settings/x` (管理员保护) — `setXClientId` 用于 canister 级别的默认值。
- `/settings/x` (任何已登录用户) — `setMyXClientId` 用于每个用户的覆盖。
- `/connect/x` (任何已登录用户) — 与 Variants A/B 相同的 OAuth 握手，查找顺序如 §10 所述。

“连接 X”按钮保持禁用，直到为调用者解析出某个客户端 ID（管理员默认 OR 每个用户覆盖）。

## 所有变体共通

- **必须登录**对于每个 X 相关路由。将 `/settings/...` 和 `/connect/x` 路由通过 [`extension-authorization`](../extension-authorization/SKILL.md)` 的 auth 守卫 (`useInternetIdentity` + 当 `!isAuthenticated` 时重定向) 返回“请登录”墙；否则，每个端点都会以“请登录”为标题捕获。
- **前端永远不会持久化令牌。** 没有 `localStorage`, 没有 `IndexedDB`, 没有 cookie — canister 介导一切。浏览器只看到 `Bool` 状态标志 (`isMyXConnected`, `isXClientIdConfigured`) 和 OAuth 重定向 URL。
- **OAuth `state` 参数是 canister 的责任。** 在 `startXOAuth` 中服务器端生成它，与 `code_verifier` 一起持久化，在 `completeXOAuth` 中验证它，在交换代码之前。不要让前端生成或回显 `state` — 这会破坏 CSRF 保护。
- **发布推文 UI 本身很简单：** 一个文本区域，一个提交按钮，一个绑定到 canister 暴露的任何 `tweet` / 历史端点的最近推文列表。没有客户端 X SDK, 没有令牌处理, 没有 JSON 序列化逻辑——canister 是 X 客户端。
