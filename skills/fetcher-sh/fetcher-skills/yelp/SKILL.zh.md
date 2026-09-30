---
name: yelp
description: fetcher.sh 上的 Yelp API 替代方案 — 按调用付费，使用 USDC 通过 x402 支付，或使用 Bearer 密钥预付费积分，无需 Yelp Fusion API 应用审批。当用户需要按查询和位置搜索本地商家（按评分或评论数量排序）、通过 ID 或 Yelp URL handle/slug 获取商家的详细信息，或获取商家的评论时使用。此外，还涵盖本地商家发现、餐厅/服务研究、评论情感输入以及本地商家竞争监控，无需 Yelp Fusion API 的应用审批流程和每日调用限制。
---

# Yelp API

本地商家搜索、商家详情和评论以干净的 JSON 格式呈现 — 每次调用一个简单的 HTTP GET 请求，按需付费。无需 Yelp Fusion API 应用审批，无每日调用限制，无需 API 密钥申请表。

基础 URL：`https://yelp.fetcher.sh`

## 认证

两种付费方式，相同的数据 — 完整机制在 [`fetcher` 技能](../fetcher/SKILL.md) 中：

```bash
# 1. 预付费积分（推荐 — 在 https://fetcher.sh/topup 获取密钥
#    或通过 POST /api/credits/topup，参见 fetcher 技能）
export FETCHER_API_KEY="bby_live_xxxxxxxxxxxx"
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://yelp.fetcher.sh/api/search?query=ramen&location=San+Francisco"

# 2. x402 按调用付费 — 省略头部；无支付的 GET 请求将返回 402，并包含机器可读的支付要求（Base、Polygon、Arbitrum、Monad 或 Solana 上的 USDC）。@x402/fetch 自动签名和重试。
```

每个响应都是 `{ "status": number, "message": string, "data": ... }`；HTTP 状态码与 `status` 一致。

## 端点（4 — 全部为 GET，每次调用 0.003 美元）

| 端点 | 返回内容 |
| --- | --- |
| `/api/search` | 符合查询和位置的商家 |
| `/api/place/{id}` | 通过 ID 获取商家的完整详情 |
| `/api/place/handle/{handle}` | 通过其 Yelp URL handle/slug 获取商家的完整详情 |
| `/api/place/{id}/reviews` | 商家的评论 |

搜索时必须包含：`query`、`location`。可选：`sortBy` (`recommended`、`rating`、`reviewCount`)、`page`。评论支持 `page`。

## 场景

**按评分最高排序：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=ramen" -G \
  --data-urlencode "location=San Francisco" \
  --data-urlencode "sortBy=rating" \
  "https://yelp.fetcher.sh/api/search"
```

**按评论数量最多排序：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=tacos" -G \
  --data-urlencode "location=Austin, TX" \
  --data-urlencode "sortBy=reviewCount" \
  "https://yelp.fetcher.sh/api/search"
```

**通过 ID 或其 Yelp URL handle/slug 获取商家的详情：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://yelp.fetcher.sh/api/place/gary-danko-san-francisco"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://yelp.fetcher.sh/api/place/handle/gary-danko-san-francisco"
```

**商家的评论，分页显示：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "page=2" -G \
  "https://yelp.fetcher.sh/api/place/gary-danko-san-francisco/reviews"
```

## MCP

```json
{
  "mcpServers": {
    "yelp": {
      "url": "https://yelp.fetcher.sh/mcp",
      "headers": { "Authorization": "Bearer bby_live_..." }
    }
  }
}
```

免费：`search_endpoints`、`describe_endpoint`、`check_balance`。付费：`fetch_data`（上述任何端点）、`topup_credits`，以及命名的快捷方式 `yelp_search`。省略 `headers` 块即可使用 x402 按调用付费 — 参见 [`fetcher` 技能](../fetcher/SKILL.md) 了解完整流程。

## 错误

- `400` — 缺少/无效参数（消息中会指明）
- `401` — 未知或轮换的密钥
- `402` — 需要支付（x402 挑战）或 `topup_required`（积分耗尽）
- `404` — 非计价路径
- 无速率限制；上游失败不退款（结算先于交付）

## 参考

- 完整代理设置：<https://yelp.fetcher.sh/skill.md>
- OpenAPI 3.1 合同：<https://yelp.fetcher.sh/openapi.json>
- 简明目录：<https://yelp.fetcher.sh/llms.txt>
- 支付、积分和 MCP 深入了解：[`fetcher` 技能](../fetcher/SKILL.md)
- 网站：<https://yelp.fetcher.sh>
