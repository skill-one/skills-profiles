# Reddit API

按需获取 Reddit 数据：跨子版块帖子搜索、版块和用户搜索、版块信息与信息流、单个帖子及其完整评论树、全站最佳/热门/新帖/置顶信息流，以及用户资料/帖子/评论 — 每次调用仅一个 HTTP GET 请求，按量付费。无需 OAuth 应用注册，无需客户端 ID/密钥对，无需 Reddit API 速率限制等级。

基础 URL：`https://reddit.fetcher.sh`

## 认证

两种付费方式，获取相同数据 — `fetcher` 技能的完整机制在 [`fetcher`
技能](../fetcher/SKILL.md) 中：

```bash
# 1. 预付费积分（推荐 — 在 https://fetcher.sh/topup 获取密钥
#    或通过 POST /api/credits/topup，参见 fetcher 技能）
export FETCHER_API_KEY="bby_live_xxxxxxxxxxxx"
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://reddit.fetcher.sh/api/search/post?keyword=hello"

# 2. x402 按次付费 — 省略头部；无付费的 GET 请求返回 402，包含机器可读的付费要求（Base、Polygon、Arbitrum、Monad 或 Solana 上的 USDC）。@x402/fetch 自动签名和重试。
```

每个响应格式为 `{ "status": number, "message": string, "data": ... }`；HTTP 状态码与 `status` 一致。

## 端点 (15 — 全部为 GET，每次调用 $0.002)

| 端点 | 返回内容 |
| --- | --- |
| `/api/search/post` | 匹配关键词的跨子版块帖子 |
| `/api/search/subreddit` | 匹配关键词的版块 |
| `/api/search/user` | 匹配关键词的用户 |
| `/api/subreddit/{name}` | 版块信息 |
| `/api/subreddit/{name}/posts` | 版块的帖子信息流 |
| `/api/post/{id}` | 单个帖子 |
| `/api/post/{id}/comments` | 帖子的评论树 |
| `/api/post/{id}/comments/{commentId}/replies` | 评论的回复 |
| `/api/posts/hot` | 全站热门信息流 |
| `/api/posts/new` | 全站新帖信息流 |
| `/api/posts/top` | 全站置顶信息流 |
| `/api/posts/best` | 全站最佳信息流 |
| `/api/user/{username}` | 用户资料 |
| `/api/user/{username}/posts` | 用户的帖子 |
| `/api/user/{username}/comments` | 用户的评论 |

`{id}` / `{name}` / `{username}` 是路径参数。可选 `sort` / `cursor` 重新排序和分页；`keyword`（搜索）在出现的地方是必需的。

## 场景

**跨所有版块关于某个主题的置顶帖子：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "keyword=ai agents" -G \
  --data-urlencode "sort=top" \
  "https://reddit.fetcher.sh/api/search/post"
```

**讨论最多（评论数最多）：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "keyword=stablecoin payments" -G \
  --data-urlencode "sort=comments" \
  "https://reddit.fetcher.sh/api/search/post"
```

**最新优先：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "keyword=x402" -G \
  --data-urlencode "sort=new" \
  "https://reddit.fetcher.sh/api/search/post"
```

`/api/search/post` 的其他 `sort` 值：`relevance`，`hot`。

**通过关键词搜索版块或用户：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "keyword=machine learning" -G \
  "https://reddit.fetcher.sh/api/search/subreddit"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "keyword=spez" -G \
  "https://reddit.fetcher.sh/api/search/user"
```

**版块信息，然后是其热门/新帖/置顶信息流：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://reddit.fetcher.sh/api/subreddit/MachineLearning"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "sort=top" -G \
  "https://reddit.fetcher.sh/api/subreddit/MachineLearning/posts"
```

**单个帖子、其评论树以及一个评论的回复：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://reddit.fetcher.sh/api/post/1abcde2"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "sort=top" -G \
  "https://reddit.fetcher.sh/api/post/1abcde2/comments"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://reddit.fetcher.sh/api/post/1abcde2/comments/fghij3k/replies"
```

**全站信息流：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://reddit.fetcher.sh/api/posts/hot"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://reddit.fetcher.sh/api/posts/best"
```

**用户的资料、帖子、评论：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://reddit.fetcher.sh/api/user/spez"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "sort=new" -G \
  "https://reddit.fetcher.sh/api/user/spez/posts"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "sort=top" -G \
  "https://reddit.fetcher.sh/api/user/spez/comments"
```

## MCP

```json
{
  "mcpServers": {
    "reddit": {
      "url": "https://reddit.fetcher.sh/mcp",
      "headers": { "Authorization": "Bearer bby_live_..." }
    }
  }
}
```

免费：`search_endpoints`，`describe_endpoint`，`check_balance`。付费：`fetch_data`（上述任何端点），`topup_credits`，以及命名的快捷方式 `reddit_search_post`。省略 `headers` 块即可用 x402 按次付费 — 参见 [`fetcher` 技能](../fetcher/SKILL.md) 了解完整流程。

## 错误

- `400` — 缺少/无效参数（消息中会指明）
- `401` — 未知或已轮换的密钥
- `402` — 需要付费（x402 挑战）或 `topup_required`（积分耗尽）
- `404` — 非计价路径
- 无速率限制；上游失败不退款（结算先于交付）

## 参考

- 完整代理设置：<https://reddit.fetcher.sh/skill.md>
- OpenAPI 3.1 合同：<https://reddit.fetcher.sh/openapi.json>
- 简明目录：<https://reddit.fetcher.sh/llms.txt>
- 付费、积分和 MCP 深入了解：[`fetcher` 技能](../fetcher/SKILL.md)
- 网站：<https://reddit.fetcher.sh>
