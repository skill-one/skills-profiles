# 使用 `x-client` 发布到 X

用于 [X API v2](https://developer.x.com/en/docs/x-api) 的 Motoko 绑定，从 X 的 OpenAPI 规范生成。写入路径是 **`TweetsApi.createPosts`** (`POST /2/tweets`)；请求模型是 **`TweetCreateRequest`**。

# 后端

一个极简的 canister，代表持有 OAuth 2.0 授权码的用户发布推文（token 获取/刷新在 canister 端——见下文）。默认是非复制的，因此你只需提供 token；每个可选字段都必须存在，`null` 表示“未提供”：

```motoko filepath=src/backend/main.mo
import { createPosts } "mo:x-client/Apis/TweetsApi";
import { type TweetCreateRequest } "mo:x-client/Models/TweetCreateRequest";
import { defaultConfig } "mo:x-client/Config";

persistent actor {
  // 代表持有 OAuth 2.0 授权码的用户发布推文。
  public func postTweet(accessToken : Text, body : Text) : async () {
    let cfg = { defaultConfig with auth = ?#bearer accessToken };
    let req : TweetCreateRequest = {
      text_ = ?body;
      for_super_followers_only = null; poll = null; reply = null;
      reply_settings = null; media = null; geo = null; quote_tweet_id = null;
      nullcast = null; direct_message_deep_link = null; community_id = null;
      card_uri = null; edit_options = null; made_with_ai = null;
      paid_partnership = null; share_with_followers = null;
    };
    ignore await* createPosts(cfg, req);
  };
}
```

文本字段是 `text_ : ?Text`（下划线是为了避免 Motoko 关键字冲突；它序列化为 JSON 键 `"text"`）。

## OAuth 2.0 设置 — PKCE，无客户端密钥

每个写入端点（`/2/tweets` 最突出）需要一个 **每个用户的 OAuth 2.0 授权码**。`x-client` 是为 **PKCE** 流设计的，因此**没有客户端密钥**——只有一个**客户端 ID**。

1. 访问 [X 开发者门户](https://developer.x.com/en/portal/dashboard)，创建一个项目（免费层 = 每月 1500 条推文），并创建一个 **应用**。
2. 应用 → **设置 → 用户认证设置 → 编辑**，打开 **OAuth 2.0**。**应用类型**：`Web 应用、自动化应用或机器人`（PKCE）。**不要**选择 `原生应用` 或“机密客户端”——这些会强制使用客户端密钥流，而该客户端不会发出这种流。
3. **回调 URI**：接收 `?code=…` 的 canister 的 HTTPS 端点，精确匹配（例如 `https://<canister-id>.ic0.app/oauth/x/callback`）。
4. **授权时请求的范围**：

   | 范围 | 原因 |
   |---|---|
   | `tweet.write` | **必须**用于 `createPosts` / 发布 |
   | `tweet.read` | 在 UI 中显示“连接为 @…” |
   | `users.read` | 解析认证用户 |
   | `offline.access` | 发出**刷新 token**（访问 token 有效期约 2 小时） |

5. 保存；复制 **OAuth 2.0 客户端 ID**（一个约 30 个字符的公开字符串）。它**不是密钥**——可以提交、记录或硬编码。

**部署模型**——选择一个或支持两者：一个**全局 canister** 的客户端 ID 由管理员一次性设置（默认），或**每个用户**的客户端 ID，用于多租户应用，不应共享速率限制配额。

范围在授权时请求，但如果没有勾选，则会在发出的 token 中静默缺失——`createPosts` 上的“OAuth 范围不足”几乎总是意味着缺少 `tweet.write`。

## 调用默认非复制

每个 `x-client` 调用都是 IC 上的 `http_request`。包中包含 `is_replicated = ?false` 在 `defaultConfig`：X 是有副作用的（发布会改变状态），其速率限制头/响应时间戳因请求而异，因此一个*复制的*出调用——每个子网节点发出请求，IC 要求一个比特相同的响应，~13× 周期——会发布重复内容并导致共识失败。你不需要自己设置；默认值是正确的。仅当您需要共识时才使用 `is_replicated = ?true`。

## 可选字段：保持为 `null`

`x-client` 会从出站 JSON 中移除 `null` 值的可选字段（通过 `serde-core` 的 `skip_null_fields` 选项），因此 `/2/tweets` 只会看到您设置的字段。构造一个 `TweetCreateRequest`，其中 `text_ = ?"…"`，其他字段为 `null`（如上面的代码片段所示），则请求体会验证。Motoko 要求所有记录字段在值位置存在——`null` 是如何表示“未提供”。

## 非空可选子对象规则

如果您将 `poll`、`reply`、`geo`、`media` 或 `edit_options` 设置为 `?Some`，X 会强制执行该子对象自己的必填字段——您不能发送空对象，因此要么保持该字段为 `null`，要么完全填充它：

- `poll` — `options`（≥ 2）和 `duration_minutes`。
- `reply` — `in_reply_to_tweet_id`。
- `media` — `media_ids`（必须预先上传）。
- `geo` — `place_id`。

## Token 刷新

访问 token 过期（约 2 小时）。在每次调用之前，canister 应在接近 `expires_at` 的安全缓冲区中刷新，向 `https://api.x.com/2/oauth2/token` 发送 `grant_type=refresh_token`，并使用存储的 `refresh_token` 和客户端 ID。**X 在每次刷新时都会旋转刷新 token**——存储*新的* `access_token` *和* `refresh_token`；重复使用旧的刷新 token 会返回 400 并强制重新授权。`x-client` 对刷新一无所知——这是 canister 端的；请参阅 `posting-to-x` 扩展以获取规范代码结构。

## 速率限制

免费层：每月 1500 条推文，每月 500 次读取/应用。在生产环境中对 HTTP 429 进行退避；永远不要静默重试发布（重试可能会重复推文）。X 的速率限制头会返回在响应体中，但包不会解释它们。
