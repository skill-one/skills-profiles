# TikTok Scraper API

按需获取TikTok数据：通过关键词发布搜索（支持排序/日期筛选）、用户名查询、粉丝与关注列表、话题和音乐/声音信息流、基于地理位置的发布以及评论线程——每次调用仅一个简单的HTTP GET请求，按量付费。无需登录、无需会话cookie、无需浏览器自动化、无需TikTok开发者应用审核。

基础URL：`https://tiktok.fetcher.sh`

## 快速参考

| | |
| --- | --- |
| 基础URL | `https://tiktok.fetcher.sh` |
| 认证 | `Authorization: Bearer bby_live_...` 或 x402 (USDC) |
| 价格 | $0.004/次调用（固定费用） |
| 端点 | 13个，全部为 `GET` 请求 |
| MCP | `https://tiktok.fetcher.sh/mcp` |
| 机器可读格式 | `/openapi.json` · `/llms.txt` · `/skill.md` |

## 我需要哪个端点？

| 我想要... | 调用 |
| --- | --- |
| 通过关键词搜索发布（可选：最受欢迎/最新） | `GET /api/post/search` |
| 通过分享链接查询发布 | `GET /api/post?url=...` |
| 通过@用户名查询用户资料 | `GET /api/user/handle/{username}` |
| 获取用户的发布、粉丝或关注列表 | `GET /api/user/{id}/posts` / `/followers` / `/followings` |
| 获取发布的评论 | `GET /api/post/{id}/comments` |
| 查找特定话题下的发布 | `GET /api/hashtag/{id}/posts` |
| 查找使用特定声音的发布 | `GET /api/music/{id}/posts` |

每个端点的完整参数详情：[`references/endpoints.md`](references/endpoints.md)。

## 认证

两种付费方式，获取相同数据——完整机制在 [`fetcher` 技能](../fetcher/SKILL.md) 中：

```bash
# 1. 预付费积分（推荐——在 https://fetcher.sh/topup 获取密钥
#    或通过 POST /api/credits/topup，参考 `fetcher` 技能）
export FETCHER_API_KEY="bby_live_xxxxxxxxxxxx"
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/post/search?keyword=hello"

# 2. x402 按次付费——省略头部；无付费的GET请求将返回402，并附带机器可读的支付要求（Base、Polygon、Arbitrum、Monad 或 Solana上的USDC）。@x402/fetch 自动签名和重试。
```

每个响应格式为 `{ "status": number, "message": string, "data": ... }`；HTTP状态码与 `status` 一致。

## 端点（13个 — 全部为 `GET`，$0.004/次调用）

| 端点 | 返回内容 |
| --- | --- |
| `/api/post/search` | 符合关键词的发布；支持排序和日期范围筛选 |
| `/api/post` | 通过分享链接解析的单个发布 |
| `/api/post/{id}` | 通过ID获取的单个发布 |
| `/api/post/{id}/comments` | 发布的评论 |
| `/api/post/{id}/comments/{commentId}/replies` | 评论的回复 |
| `/api/user/handle/{username}` | 通过@用户名获取的用户资料 |
| `/api/user/{id}/posts` | 用户的发布 |
| `/api/user/{id}/followers` | 用户的粉丝 |
| `/api/user/{id}/followings` | 用户关注的账号 |
| `/api/hashtag/handle/{name}` | 通过名称获取的话题元数据 |
| `/api/hashtag/{id}/posts` | 特定话题下的发布 |
| `/api/music/{id}/posts` | 使用特定声音/音乐轨道的发布 |
| `/api/location/{locationId}/posts` | 标记在特定地理位置的发布 |

`{id}` / `{username}` / `{name}` 是路径参数。可选的查询参数（`cursor`、`region`）用于分页或地理范围筛选；`keyword`（搜索）和 `url`（发布查询）在出现时为必填项。

## 场景示例

**本月最受欢迎的发布：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "keyword=ai agent" -G \
  --data-urlencode "sortType=MOST_LIKED" \
  --data-urlencode "dateRange=THIS_MONTH" \
  "https://tiktok.fetcher.sh/api/post/search"
```

**昨日发布的，按最新排序：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "keyword=crypto payments" -G \
  --data-urlencode "sortType=DATE_POSTED" \
  --data-urlencode "dateRange=YESTERDAY" \
  "https://tiktok.fetcher.sh/api/post/search"
```

其他 `sortType` 值：`RELEVANCE`。其他 `dateRange` 值：`ALL_TIME`、`THIS_WEEK`、`LAST_THREE_MONTHS`、`LAST_SIX_MONTHS`。

**通过分享链接查询发布，或直接通过ID查询：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" -G \
  --data-urlencode "url=https://www.tiktok.com/@username/video/1234567890123456789" \
  "https://tiktok.fetcher.sh/api/post"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/post/1234567890123456789"
```

**发布的评论和评论回复：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/post/1234567890123456789/comments"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/post/1234567890123456789/comments/9876543210/replies"
```

**通过@用户名获取用户资料，然后获取其发布、粉丝和关注列表：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/user/handle/khaby.lame"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/user/6935741396776976390/posts"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/user/6935741396776976390/followers"
```

**话题的元数据，然后获取该话题下的发布：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/hashtag/handle/fyp"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/hashtag/1234567890/posts"
```

**使用特定声音的发布，以及来自特定地理位置的发布：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/music/1234567890123456789/posts"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/location/1234567890123456789/posts"
```

## MCP

```json
{
  "mcpServers": {
    "tiktok": {
      "url": "https://tiktok.fetcher.sh/mcp",
      "headers": { "Authorization": "Bearer bby_live_..." }
    }
  }
}
```

免费：`search_endpoints`、`describe_endpoint`、`check_balance`。付费：`fetch_data`（上述任何端点）、`topup_credits`，以及命名的快捷方式 `tiktok_post_search`。省略 `headers` 块即可使用x402按次付费——完整流程请参考 [`fetcher` 技能](../fetcher/SKILL.md)。

## 错误

- `400` — 缺少/无效参数（消息中会列出名称）
- `401` — 未知或已轮换的密钥
- `402` — 需要付费（x402挑战）或 `topup_required`（积分耗尽）
- `404` — 非计费路径
- 无速率限制；上游失败不退款（结算先于交付）

## 参考

- 深入了解：[`references/endpoints.md`](references/endpoints.md)（所有参数）· [`references/scenarios.md`](references/scenarios.md)（每个端点一个 `curl` 示例）· [`references/faq.md`](references/faq.md) · [`references/comparison.md`](references/comparison.md)（与官方TikTok API和浏览器爬虫的比较）
- 任务指南：[病毒式发布搜索](../../task-guides/tiktok-viral-post-search.md) · [用户资料和粉丝](../../task-guides/tiktok-profile-and-followers.md)
- 命令行：[`/tiktok-search`](../../commands/tiktok-search.md)
- 完整代理设置：<https://tiktok.fetcher.sh/skill.md>
- OpenAPI 3.1 合约：<https://tiktok.fetcher.sh/openapi.json>
- 精简目录：<https://tiktok.fetcher.sh/llms.txt>
- 付费、积分和MCP深入指南：[`fetcher` 技能](../fetcher/SKILL.md)
- 网站：<https://tiktok.fetcher.sh>
