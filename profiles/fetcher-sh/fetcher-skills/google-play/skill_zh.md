# Google Play API

Google Play 商店应用搜索、详情、评论、权限、数据安全以及开发者目录 — 每次调用仅一个简单的 HTTP GET 请求，按需付费。无需 Play Console 访问权限，无需开发者账号，无需抓取商店 HTML 内容。

基础 URL：`https://googleplay.fetcher.sh`

## 认证

两种付费方式，相同的数据 — 完整机制在 [`fetcher` 技能](../fetcher/SKILL.md) 中：

```bash
# 1. 预付费积分（推荐 — 在 https://fetcher.sh/topup 获取密钥
#    或通过 POST /api/credits/topup，参见 fetcher 技能）
export FETCHER_API_KEY="bby_live_xxxxxxxxxxxx"
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://googleplay.fetcher.sh/api/apps?search=meditation"

# 2. x402 按调用付费 — 省略头部；无支付的 GET 请求返回 402，并附带机器可读的支付要求（Base、Polygon、Arbitrum、Monad 或 Solana 上的 USDC）。@x402/fetch 自动签名和重试。
```

每个响应都是 `{ "status": number, "message": string, "data": ... }`；HTTP 状态码与 `status` 一致。

## 端点（7 — 全部为 GET，每次调用 0.003 美元）

| 端点 | 返回内容 |
| --- | --- |
| `/api/apps` | 匹配关键词的应用；价格和国家过滤器 |
| `/api/apps/{appId}` | 应用完整详情 |
| `/api/apps/{appId}/reviews` | 应用评论 |
| `/api/apps/{appId}/similar` | 与给定应用相似的应用 |
| `/api/apps/{appId}/permissions` | 应用请求的权限 |
| `/api/apps/{appId}/datasafety` | 应用数据安全声明 |
| `/api/developers/{developerId}` | 开发者的完整应用目录 |

搜索时必须包含 `search`；可选：`price` (`all`, `free`, `paid`)、`country`、`lang`。评论需要 `country`；可选 `sort` (`NEWEST`, `RATING`, `HELPFULNESS`)。

## 场景

**仅免费应用：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "search=meditation" -G \
  --data-urlencode "price=free" \
  "https://googleplay.fetcher.sh/api/apps"
```

**付费应用，德国商店：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "search=photo editor" -G \
  --data-urlencode "price=paid" \
  --data-urlencode "country=de" \
  "https://googleplay.fetcher.sh/api/apps"
```

**应用的完整详情，然后按评分排序的评论：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://googleplay.fetcher.sh/api/apps/com.spotify.music"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "country=us" -G \
  --data-urlencode "sort=RATING" \
  "https://googleplay.fetcher.sh/api/apps/com.spotify.music/reviews"
```

**权限和数据安全声明：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://googleplay.fetcher.sh/api/apps/com.spotify.music/permissions"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://googleplay.fetcher.sh/api/apps/com.spotify.music/datasafety"
```

**与给定应用相似的应用，以及开发者的完整目录：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://googleplay.fetcher.sh/api/apps/com.spotify.music/similar"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "country=us" -G \
  "https://googleplay.fetcher.sh/api/developers/Spotify+AB"
```

## MCP

```json
{
  "mcpServers": {
    "google-play": {
      "url": "https://googleplay.fetcher.sh/mcp",
      "headers": { "Authorization": "Bearer bby_live_..." }
    }
  }
}
```

免费：`search_endpoints`、`describe_endpoint`、`check_balance`。付费：`fetch_data`（上述任何端点）、`topup_credits`，以及命名的快捷方式 `googleplay_apps`。省略 `headers` 块即可使用 x402 按调用付费 — 参见 [`fetcher` 技能](../fetcher/SKILL.md) 获取完整流程。

## 错误

- `400` — 缺少/无效参数（消息中会指明）
- `401` — 未知或已轮换的密钥
- `402` — 需要支付（x402 挑战）或 `topup_required`（积分耗尽）
- `404` — 非计费路径
- 无速率限制；上游失败不退款（结算先于交付）

## 参考

- 完整代理设置：<https://googleplay.fetcher.sh/skill.md>
- OpenAPI 3.1 合约：<https://googleplay.fetcher.sh/openapi.json>
- 简化目录：<https://googleplay.fetcher.sh/llms.txt>
- 支付、积分和 MCP 深入了解：[`fetcher` 技能](../fetcher/SKILL.md)
- 网站：<https://googleplay.fetcher.sh>
