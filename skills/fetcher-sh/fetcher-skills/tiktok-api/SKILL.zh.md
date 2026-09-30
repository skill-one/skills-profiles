---
name: tiktok-api
description: fetcher.sh 上的 TikTok API 替代方案——通过 x402 使用 USDC 按调用付费，或使用 Bearer 密钥预付费积分，无需登录且无需应用审核。当用户需要按关键词搜索 TikTok 帖子并按点赞最多或最新排序（在日期范围内），通过分享链接或 ID 查找帖子，抓取 TikTok 个人资料（通过 @用户名），获取用户的帖子、粉丝或关注对象，获取标签的帖子，使用特定音轨/音乐抓取帖子，获取地点的帖子，或阅读帖子的评论和评论回复时使用。此外，还涵盖 TikTok 趋势追踪、标签监控、网红发现、竞争对手内容分析以及 TikTok 数据管道，无需官方 TikTok API 访问或抓取浏览器。
---

# TikTok API

按需获取 TikTok 数据：带排序和日期筛选的关键词帖子搜索、通过用户名（handle）查找个人资料、关注者和被关注者、话题标签和音乐/音效信息流、基于位置的帖子以及评论线程——每次调用只需一个普通的 HTTP GET 请求，按使用量付费。无需登录、无会话 Cookie、无需浏览器自动化、也无需通过 TikTok 开发者应用审核。

基础 URL：`https://tiktok.fetcher.sh`

## 快速参考

| | |
| --- | --- |
| 基础 URL | `https://tiktok.fetcher.sh` |
| 认证 | `Authorization: Bearer bby_live_...` 或 x402 (USDC) |
| 价格 | $0.004/次（固定价格） |
| 端点 | 13 个，均为 `GET` |
| MCP | `https://tiktok.fetcher.sh/mcp` |
| 机器可读 | `/openapi.json` · `/llms.txt` · `/skill.md` |

## 我需要使用哪个端点？

| 我想要…… | 调用 |
| --- | --- |
| 按关键词搜索帖子（可选按点赞最多/最新排序） | `GET /api/post/search` |
| 通过分享 URL 查找帖子 | `GET /api/post?url=...` |
| 通过 @用户名查找个人资料 | `GET /api/user/handle/{username}` |
| 获取用户的帖子、关注者或被关注者 | `GET /api/user/{id}/posts` / `/followers` / `/followings` |
| 获取帖子的评论 | `GET /api/post/{id}/comments` |
| 查找话题标签下的帖子 | `GET /api/hashtag/{id}/posts` |
| 查找使用特定音效的帖子 | `GET /api/music/{id}/posts` |

每一行的完整参数详情：[`references/endpoints.md`](references/endpoints.md)。

## 认证

两种付费方式，数据相同——完整机制见 [`fetcher` 技能](../fetcher/SKILL.md)：

```bash
# 1. 预付费额度（推荐 — 在 https://fetcher.sh/topup 获取密钥，
#    或通过 POST /api/credits/topup，参见 fetcher 技能）
export FETCHER_API_KEY="bby_live_xxxxxxxxxxxx"
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/post/search?keyword=hello"

# 2. x402 按次付费 — 省略请求头；未携带支付的 GET 请求将返回 402，
#    并附带机器可读的支付要求（USDC on Base, Polygon, Arbitrum, Monad, or Solana）。@x402/fetch 会自动签署并重试。
```

每个响应均为 `{ "status": number, "message": string, "data": ... }`；HTTP 状态码与 `status` 保持一致。

## 端点（13 个 — 均为 GET，$0.004/次）

| 端点 | 返回内容 |
| --- | --- |
| `/api/post/search` | 匹配关键词的帖子；排序和日期范围筛选 |
| `/api/post` | 从分享 URL 解析出的单个帖子 |
| `/api/post/{id}` | 按 ID 获取单个帖子 |
| `/api/post/{id}/comments` | 帖子的评论 |
| `/api/post/{id}/comments/{commentId}/replies` | 对某条评论的回复 |
| `/api/user/handle/{username}` | 通过 @用户名获取个人资料 |
| `/api/user/{id}/posts` | 用户的帖子 |
| `/api/user/{id}/followers` | 用户的关注者 |
| `/api/user/{id}/followings` | 用户关注的人 |
| `/api/hashtag/handle/{name}` | 按名称获取话题标签元数据 |
| `/api/hashtag/{id}/posts` | 话题标签下的帖子 |
| `/api/music/{id}/posts` | 使用特定音效/音乐轨道的帖子 |
| `/api/location/{locationId}/posts` | 标记在特定位置的帖子 |

`{id}` / `{username}` / `{name}` 是路径参数。可选查询参数（`cursor`、`region`）用于分页或按地理范围限定结果；`keyword`（搜索）和 `url`（帖子查找）在出现时是必填项。

## 场景

**本月点赞最多的帖子：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "keyword=ai agent" -G \
  --data-urlencode "sortType=MOST_LIKED" \
  --data-urlencode "dateRange=THIS_MONTH" \
  "https://tiktok.fetcher.sh/api/post/search"
```

**昨天发布的，按最新优先排序：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "keyword=crypto payments" -G \
  --data-urlencode "sortType=DATE_POSTED" \
  --data-urlencode "dateRange=YESTERDAY" \
  "https://tiktok.fetcher.sh/api/post/search"
```

其他 `sortType` 值：`RELEVANCE`。其他 `dateRange` 值：`ALL_TIME`、`THIS_WEEK`、`LAST_THREE_MONTHS`、`LAST_SIX_MONTHS`。

**通过分享 URL 或直接按 ID 查找帖子：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" -G \
  --data-urlencode "url=https://www.tiktok.com/@username/video/1234567890123456789" \
  "https://tiktok.fetcher.sh/api/post"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/post/1234567890123456789"
```

**帖子的评论及评论回复：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/post/1234567890123456789/comments"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/post/1234567890123456789/comments/9876543210/replies"
```

**通过 @handle 获取个人资料，然后获取其帖子、关注者和被关注者：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/user/handle/khaby.lame"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/user/6935741396776976390/posts"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/user/6935741396776976390/followers"
```

**话题标签的元数据，然后获取其帖子：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/hashtag/handle/fyp"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/hashtag/1234567890/posts"
```

**使用特定音效的帖子，以及来自特定位置的帖子：**

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

免费：`search_endpoints`、`describe_endpoint`、`check_balance`。付费：
`fetch_data`（上述任意端点）、`topup_credits`，以及命名快捷方式
`tiktok_post_search`。移除 `headers` 块即可改为通过 x402 按次付费——完整流程见
[`fetcher` 技能](../fetcher/SKILL.md)。

## 错误

- `400` — 缺少/无效参数（消息中会指明具体参数）
- `401` — 未知或已轮换的密钥
- `402` — 需要支付（x402 质询）或 `topup_required`（额度已耗尽）
- `404` — 不是按定价计费的端点
- 无速率限制；上游故障不退费（结算先于交付）

## 参考

- 深入详解：[`references/endpoints.md`](references/endpoints.md)（所有参数） ·
  [`references/scenarios.md`](references/scenarios.md)（每个端点一个 `curl`
  示例） · [`references/faq.md`](references/faq.md) ·
  [`references/comparison.md`](references/comparison.md)（与官方
  TikTok API 及浏览器爬虫的对比）
- 任务指南：[热门帖子搜索](../../task-guides/tiktok-viral-post-search.md) ·
  [个人资料与关注者](../../task-guides/tiktok-profile-and-followers.md)
- 斜杠命令：[`/tiktok-search`](../../commands/tiktok-search.md)
- 完整代理设置：<https://tiktok.fetcher.sh/skill.md>
- OpenAPI 3.1 契约：<https://tiktok.fetcher.sh/openapi.json>
- 精简目录：<https://tiktok.fetcher.sh/llms.txt>
- 支付、额度及 MCP 深入详解：[`fetcher` 技能](../fetcher/SKILL.md)
- 站点：<https://tiktok.fetcher.sh>
