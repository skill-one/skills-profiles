# Instagram API

按需获取 Instagram 数据：通过 @handle 查询用户资料、帖子、Reels、故事、被标记的帖子、粉丝和关注对象、话题标签和位置信息流、音频/音乐信息流以及帖子评论 — 每次调用仅一个简单的 HTTP GET 请求，按次付费。无需登录、无需会话 Cookie、无需无头浏览器、无需 Graph API 商业验证。

基础 URL：`https://instagram.fetcher.sh`

## 快速参考

| | |
| --- | --- |
| 基础 URL | `https://instagram.fetcher.sh` |
| 认证 | `Authorization: Bearer bby_live_...` 或 x402 (USDC) |
| 价格 | $0.004/次调用 (固定费用) |
| 端点 | 16 个 — 全部为 `GET` 请求 |
| MCP | `https://instagram.fetcher.sh/mcp` |
| 机器可读格式 | `/openapi.json` · `/llms.txt` · `/skill.md` |

## 我需要哪个端点？

| 我想要... | 调用 |
| --- | --- |
| 通过 @handle 查询用户资料 | `GET /api/user/handle/{handle}` |
| 通过名称搜索账号 | `GET /api/user/search` |
| 获取用户的帖子、Reels 或故事 | `GET /api/user/{id}/posts` / `/reels` / `/stories` |
| 获取用户的粉丝或关注对象 | `GET /api/user/{id}/followers` / `/followings` |
| 通过分享链接短码查询帖子 | `GET /api/post/code/{code}` |
| 获取帖子的评论 | `GET /api/post/{id}/comments` |
| 查找某个话题下的帖子 | `GET /api/hashtag/{name}/posts` |
| 查找某个位置被标记的帖子 | `GET /api/location/{id}/posts` |

每个端点的完整参数详情：[`references/endpoints.md`](references/endpoints.md)。

## 认证

两种付费方式，获取相同数据 — 完整机制在 [`fetcher` 技能](../fetcher/SKILL.md) 中：

```bash
# 1. 预付费积分（推荐 — 在 https://fetcher.sh/topup 获取密钥
#    或通过 POST /api/credits/topup，参见 fetcher 技能）
export FETCHER_API_KEY="bby_live_xxxxxxxxxxxx"
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/user/handle/nasa"

# 2. x402 按次付费 — 省略头部；无付费的 GET 请求将返回 402 并附带机器可读的支付要求（Base、Polygon、Arbitrum、Monad 或 Solana 上的 USDC）。@x402/fetch 自动签名和重试。
```

每个响应格式为 `{ "status": number, "message": string, "data": ... }`；HTTP 状态码与 `status` 一致。

## 端点 (16 个 — 全部为 GET 请求，每次调用 $0.004)

| 端点 | 返回内容 |
| --- | --- |
| `/api/user/handle/{handle}` | 通过 @handle 获取完整用户资料 — 粉丝数量、简介、数字 ID |
| `/api/user/search` | 匹配关键词查询的用户资料 |
| `/api/userid/{handle}` | @handle 对应的数字用户 ID |
| `/api/user/{id}` | 通过数字 ID 获取用户资料 |
| `/api/user/{id}/posts` | 用户的帖子 |
| `/api/user/{id}/posts/tagged` | 用户被标记的帖子 |
| `/api/user/{id}/reels` | 用户的 Reels |
| `/api/user/{id}/stories` | 用户的活跃故事 |
| `/api/user/{id}/followers` | 用户的粉丝 |
| `/api/user/{id}/followings` | 用户关注的账号 |
| `/api/post/code/{code}` | 通过短码（来自帖子 URL）获取单个帖子 |
| `/api/post/{id}/comments` | 帖子的评论 |
| `/api/hashtag/{name}/posts` | 某个话题下的帖子 |
| `/api/hashtag/{name}/reels` | 某个话题下的 Reels |
| `/api/location/{id}/posts` | 某个位置被标记的帖子 |
| `/api/audio/{id}/posts` | 使用特定音频/音乐轨道的帖子 |

`{id}` / `{handle}` / `{name}` / `{code}` 是路径参数。可选 `cursor` / `page` 分页；`query`（用户搜索）在出现时必须提供。

## 场景

**通过 @handle 解析用户资料 — 大多数调用者首先需要的端点：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/user/handle/nasa"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/user/handle/natgeo"
```

**通过关键词搜索用户资料，或仅解析 @handle 的数字 ID：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=fitness influencer" -G \
  "https://instagram.fetcher.sh/api/user/search"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/userid/nasa"
```

**用户的帖子、Reels、故事和被标记的帖子（通过上述 @handle 查询获取的数字 ID）：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/user/528817151/posts"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/user/528817151/reels"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/user/528817151/stories"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/user/528817151/posts/tagged"
```

**粉丝和关注对象：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/user/528817151/followers"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/user/528817151/followings"
```

**通过短码（URL 中 `/p/` 后面的部分）获取单个帖子及其评论：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/post/code/C0JD3tntcmy"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/post/3245142029192513970/comments"
```

**某个话题下的帖子、Reels，来自某个位置的帖子，以及使用特定音频轨道的帖子：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/hashtag/travel/posts"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/hashtag/travel/reels"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/location/213131048/posts"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/audio/271328201351336/posts"
```

## MCP

```json
{
  "mcpServers": {
    "instagram": {
      "url": "https://instagram.fetcher.sh/mcp",
      "headers": { "Authorization": "Bearer bby_live_..." }
    }
  }
}
```

免费：`search_endpoints`、`describe_endpoint`、`check_balance`。付费：`fetch_data`（上述任何端点）、`topup_credits`，以及命名的快捷方式 `instagram_user_handle`。省略 `headers` 块即可使用 x402 按次付费 — 参见 [`fetcher` 技能](../fetcher/SKILL.md) 获取完整流程。

## 错误

- `400` — 缺少/无效参数（消息中会列出名称）
- `401` — 未知或已轮换的密钥
- `402` — 需要付费（x402 挑战）或 `topup_required`（积分耗尽）
- `404` — 非计费路径
- 无速率限制；上游失败不退款（结算先于交付）

## 参考

- 深入了解：[`references/endpoints.md`](references/endpoints.md)（所有参数）· [`references/scenarios.md`](references/scenarios.md)（每个端点一个 `curl`）· [`references/faq.md`](references/faq.md) ·
  [`references/comparison.md`](references/comparison.md)（与官方 Instagram Graph API 和浏览器爬虫的比较）
- 任务指南：[用户资料查询](../../task-guides/instagram-profile-lookup.md) ·
  [话题标签和位置监控](../../task-guides/instagram-hashtag-and-location-monitoring.md)
- 命令：[`/instagram-profile`](../../commands/instagram-profile.md)
- 完整代理设置：<https://instagram.fetcher.sh/skill.md>
- OpenAPI 3.1 合约：<https://instagram.fetcher.sh/openapi.json>
- 精简目录：<https://instagram.fetcher.sh/llms.txt>
- 付费、积分和 MCP 深入了解：[`fetcher` 技能](../fetcher/SKILL.md)
- 网站：<https://instagram.fetcher.sh>
