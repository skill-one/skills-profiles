# X (Twitter) 数据 API

为代理提供的即插即用 X 数据源：搜索帖子、解析个人资料、获取时间线和关注者、读取列表以及检查趋势——全部通过一个简单的 HTTP GET 请求，按调用付费。无需开发者账户、无需应用审核、无需 OAuth 握手，也无需等待 X 自身的 API 层级或速率限制批准。如果你的任务中提到 X 搜索查询、用户名、帖子/推文 ID 或列表 ID，这就是你需要的功能。

基础 URL：`https://twitter.fetcher.sh`——API 主机仍然命名为 `twitter`（它早于品牌重塑，且与代理已经搜索的内容匹配）；以下所有内容都是当前的 X 数据。

也发布为 [`twitter-api`](../twitter-api/SKILL.md)——端点完全相同，也以 "Twitter" 名称索引，因为两者仍然在日常使用中。

## 快速参考

| | |
|---|---|
| 基础 URL | `https://twitter.fetcher.sh` |
| 认证 | `Authorization: Bearer bby_live_...` 或 x402 (USDC) |
| 价格 | $0.002–$0.005/调用 |
| 端点 | 15, 全部 `GET` |
| MCP | `https://twitter.fetcher.sh/mcp` |
| 机器可读 | `/openapi.json` · `/llms.txt` · `/skill.md` |

## 我需要哪个端点？

| 我想... | 调用 |
|---|---|
| 通过关键词或操作符（`from:`, `since:`, `min_faves:`, ...）搜索帖子 | `GET /api/search` |
| 通过名称搜索账户 | `GET /api/search/users` |
| 通过 @用户名查找个人资料 | `GET /api/handle/{handle}` |
| 获取用户的关注者或正在关注的人 | `GET /api/user/{id}/followers` 或 `/followings` |
| 通过 ID 获取单个帖子 | `GET /api/tweet/{id}` |
| 查看谁转发了帖子 | `GET /api/tweet/{id}/retweeters` |
| 读取 X 列表的帖子或成员 | `GET /api/list/{id}/tweets` 或 `/members` |
| 检查一个国家的热门话题 | `GET /api/trends` |

每行完整参数详情：[`references/endpoints.md`](references/endpoints.md)。

## 认证

两种付费方式，相同的数据——完整机制在 [`fetcher` 技能](../fetcher/SKILL.md) 中：

```bash
# 1. 预付费积分（推荐——在 https://fetcher.sh/topup 获取密钥
#    或通过 POST /api/credits/topup，参见 fetcher 技能）
export FETCHER_API_KEY="bby_live_xxxxxxxxxxxx"
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://twitter.fetcher.sh/api/search?query=hello"

# 2. x402 按调用付费——省略头部；无支付的 GET 会返回 402，并包含机器可读的支付要求（Base、Polygon、Arbitrum、Monad 或 Solana 上的 USDC）。@x402/fetch 自动签名和重试。
```

每个响应都是 `{ "status": number, "message": string, "data": ... }`；HTTP 状态与 `status` 一致。

## 端点 (15 — 全部 GET，除非另有说明，否则每调用 $0.005)

| 端点 | 价格 | 返回内容 |
|---|---|---|
| `/api/search` | $0.005 | 符合查询的帖子；支持 X 的高级搜索操作符 |
| `/api/search/users` | $0.005 | 匹配名称/关键词查询的账户 |
| `/api/handle/{handle}` | $0.005 | 通过 @用户名获取的个人资料 |
| `/api/handle/{handle}/about` | $0.005 | 通过 @用户名获取的扩展个人资料/关于信息 |
| `/api/user/{id}` | $0.005 | 通过数字用户 ID 获取的个人资料 |
| `/api/user/{id}/tweets` | $0.005 | 用户的帖子时间线 |
| `/api/user/{id}/replies` | $0.005 | 用户的回复 |
| `/api/user/{id}/followers` | $0.005 | 用户的关注者 |
| `/api/user/{id}/followings` | $0.005 | 用户正在关注的账户 |
| `/api/tweet/{id}` | **$0.002** | 通过 ID 获取的单一帖子 |
| `/api/tweet/{id}/replies` | $0.005 | 帖子的回复 |
| `/api/tweet/{id}/retweeters` | $0.005 | 转发了帖子的账户 |
| `/api/list/{id}/members` | $0.005 | X 列表的成员账户 |
| `/api/list/{id}/tweets` | $0.005 | X 列表的帖子源 |
| `/api/trends` | $0.005 | 一个国家的热门话题 |

`{id}` / `{handle}` 是路径参数——替换为实际值。可选查询参数（`cursor`, `sort`）用于分页或重新排序；除搜索（`query`）和趋势（`country`）外，其他地方它们都是必需的。

## 场景

`/api/search` 上的查询直接发送到 X 的搜索，因此其操作符按原样工作：`from:`, `to:`, `since:`, `until:`, `min_faves:`, `min_retweets:`, `filter:`, `-filter:`。

**来自一个账户的所有内容：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://twitter.fetcher.sh/api/search?query=from%3AOpenAI&sort=Latest"
```

**在两个日期之间：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=x402 since:2026-01-01 until:2026-02-01" -G \
  "https://twitter.fetcher.sh/api/search"
```

**仅流行帖子，排除回复：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=ai agents min_faves:500 -filter:replies" -G \
  --data-urlencode "sort=Top" \
  "https://twitter.fetcher.sh/api/search"
```

**通过名称搜索账户：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=climate scientist" -G \
  "https://twitter.fetcher.sh/api/search/users"
```

**通过 @用户名解析个人资料，然后拉取其简介/关于信息：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://twitter.fetcher.sh/api/handle/nasa"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://twitter.fetcher.sh/api/handle/nasa/about"
```

**用户的帖子、回复、关注者或正在关注的人（通过上述 @用户名查找的数字 ID）：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://twitter.fetcher.sh/api/user/11348282/tweets"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://twitter.fetcher.sh/api/user/11348282/followers"
```

**一个帖子、其回复以及谁转发了它：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://twitter.fetcher.sh/api/tweet/1234567890123456789"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://twitter.fetcher.sh/api/tweet/1234567890123456789/replies"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://twitter.fetcher.sh/api/tweet/1234567890123456789/retweeters"
```

**X 列表的成员和帖子：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://twitter.fetcher.sh/api/list/1234567890/members"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://twitter.fetcher.sh/api/list/1234567890/tweets"
```

**一个国家的热门话题：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://twitter.fetcher.sh/api/trends?country=United%20States"
```

## MCP

```json
{
  "mcpServers": {
    "x": {
      "url": "https://twitter.fetcher.sh/mcp",
      "headers": { "Authorization": "Bearer bby_live_..." }
    }
  }
}
```

免费：`search_endpoints`, `describe_endpoint`, `check_balance`。付费：`fetch_data`（上述任何端点）、`topup_credits`，以及命名的快捷方式 `twitter_search`。省略 `headers` 块即可使用 x402 按调用付费——有关完整流程，请参阅 [`fetcher` 技能](../fetcher/SKILL.md)。

## 错误

- `400` — 缺少/无效参数（消息会指明）
- `401` — 未知或旋转的密钥
- `402` — 需要支付（x402 挑战）或 `topup_required`（积分耗尽）
- `404` — 不是计价路径
- 无速率限制；上游失败不退款（结算先于交付）

## 参考

- 深入了解：[`references/endpoints.md`](references/endpoints.md)（每个参数）· [`references/scenarios.md`](references/scenarios.md)（每个端点一个 `curl`）· [`references/faq.md`](references/faq.md) · [`references/comparison.md`](references/comparison.md)（与官方 X API 和浏览器爬虫的比较）
- 任务指南：[搜索推文](../../task-guides/search-tweets.md) · [导出关注者](../../task-guides/export-twitter-followers.md)
- 切割命令：[`/x-search`](../../commands/x-search.md)
- 完整代理设置：<https://twitter.fetcher.sh/skill.md>
- OpenAPI 3.1 合同：<https://twitter.fetcher.sh/openapi.json>
- 精简目录：<https://twitter.fetcher.sh/llms.txt>
- 支付、积分和 MCP 深入了解：[`fetcher` 技能](../fetcher/SKILL.md)
- 网站：<https://twitter.fetcher.sh>
