# Yelp API

本地商家搜索、商家详情和评论以干净的JSON格式呈现——每次调用一个简单的HTTP GET请求，按需付费。无需Yelp Fusion API应用审批，无每日调用限制，无需API密钥申请表。

基础URL：`https://yelp.fetcher.sh`

## 认证

两种付费方式，相同的数据——完整的机制在[`fetcher`技能](../fetcher/SKILL.md)中：

```bash
# 1. 预付费积分（推荐——在https://fetcher.sh/topup获取密钥
#    或通过POST /api/credits/topup，参见fetcher技能）
export FETCHER_API_KEY="bby_live_xxxxxxxxxxxx"
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://yelp.fetcher.sh/api/search?query=ramen&location=San+Francisco"

# 2. x402按调用付费——省略头部；无支付的GET请求返回402，并包含机器可读的支付要求（Base、Polygon、Arbitrum、Monad或Solana上的USDC）。@x402/fetch自动签名和重试。
```

每个响应都是`{ "status": number, "message": string, "data": ... }`；HTTP状态与`status`一致。

## 端点（4个——全部为GET，每次调用0.003美元）

| 端点 | 返回内容 |
| --- | --- |
| `/api/search` | 符合查询和位置的商家 |
| `/api/place/{id}` | 商家的完整详情（按ID） |
| `/api/place/handle/{handle}` | 商家的完整详情（按Yelp URL handle/slug） |
| `/api/place/{id}/reviews` | 商家的评论 |

搜索时必须包含：`query`、`location`。可选：`sortBy`（`recommended`、`rating`、`reviewCount`）、`page`。评论支持`page`。

## 场景

**按评分从高到低：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=ramen" -G \
  --data-urlencode "location=San Francisco" \
  --data-urlencode "sortBy=rating" \
  "https://yelp.fetcher.sh/api/search"
```

**按评论数量从多到少：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=tacos" -G \
  --data-urlencode "location=Austin, TX" \
  --data-urlencode "sortBy=reviewCount" \
  "https://yelp.fetcher.sh/api/search"
```

**通过ID或Yelp URL handle/slug获取商家的详情：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://yelp.fetcher.sh/api/place/gary-danko-san-francisco"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://yelp.fetcher.sh/api/place/handle/gary-danko-san-francisco"
```

**商家的评论（分页）：**

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

免费：`search_endpoints`、`describe_endpoint`、`check_balance`。付费：`fetch_data`（上述任何端点）、`topup_credits`，以及命名的快捷方式`yelp_search`。省略`headers`块即可使用x402按调用付费——参见[`fetcher`技能](../fetcher/SKILL.md)获取完整流程。

## 错误

- `400` — 缺少/无效参数（消息中会列出名称）
- `401` — 未知或轮换的密钥
- `402` — 需要支付（x402挑战）或`topup_required`（积分耗尽）
- `404` — 非计价路径
- 无速率限制；上游失败不退款（结算先于交付）

## 参考

- 完整代理设置：<https://yelp.fetcher.sh/skill.md>
- OpenAPI 3.1合约：<https://yelp.fetcher.sh/openapi.json>
- 简明目录：<https://yelp.fetcher.sh/llms.txt>
- 支付、积分和MCP深入探讨：[`fetcher`技能](../fetcher/SKILL.md)
- 网站：<https://yelp.fetcher.sh>
