# Google Maps API

位置搜索、位置详情和评论以干净的 JSON 格式返回 — 每次调用一个简单的 HTTP GET 请求，按需付费。无需 Google Cloud 项目，无 API 密钥限制规则，无每请求 Places API 计费。

基础 URL：`https://google-maps.fetcher.sh`

## 认证

两种付费方式，相同的数据 — 完整机制在 [`fetcher`
技能](../fetcher/SKILL.md) 中：

```bash
# 1. 预付费积分（推荐 — 在 https://fetcher.sh/topup 获取密钥
#    或通过 POST /api/credits/topup，参见 fetcher 技能）
export FETCHER_API_KEY="bby_live_xxxxxxxxxxxx"
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://google-maps.fetcher.sh/api/place/search?query=coffee"

# 2. x402 按调用付费 — 省略头部；无支付的 GET 请求返回 402，并包含机器可读的支付要求（Base、Polygon、Arbitrum、Monad 或 Solana 上的 USDC）。@x402/fetch 自动签名和重试。
```

每个响应都是 `{ "status": number, "message": string, "data": ... }`；HTTP 状态码与 `status` 一致。

## 端点（4 — 全部为 GET，每次调用 $0.005）

| 端点 | 返回内容 |
| --- | --- |
| `/api/place/search` | 匹配文本查询的位置，可选锚定到坐标 |
| `/api/place/{fid}` | 通过特征 ID 获取位置的完整详情 |
| `/api/place/{fid}/reviews` | 位置的评论 |
| `/api/review/{id}` | 通过 ID 获取单个评论 |

搜索时必须包含 `query`。可选：`languageCode`、`countryCode`、`latitude`、`longitude`、`offset`、`zoom`（搜索半径/精度）。评论支持 `sort` (`relevant`, `newest`, `highest`, `lowest`) 和 `cursor`。

## 场景

**纯文本搜索：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=ramen in brooklyn" -G \
  "https://google-maps.fetcher.sh/api/place/search"
```

**将搜索锚定到坐标（用于 "near me" 风格查询）：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=coffee" -G \
  --data-urlencode "latitude=40.7128" \
  --data-urlencode "longitude=-74.0060" \
  "https://google-maps.fetcher.sh/api/place/search"
```

**位置的详情，然后按最新排序的评论：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://google-maps.fetcher.sh/api/place/0x89c259af336b3341%3A0x8c584d6dfe89aa89"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "sort=newest" -G \
  "https://google-maps.fetcher.sh/api/place/0x89c259af336b3341%3A0x8c584d6dfe89aa89/reviews"
```

**通过 ID 获取单个评论：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://google-maps.fetcher.sh/api/review/ChdDSUhNMG9nS0VJQ0FnSURDeGRXQnl3RRAB"
```

**本地化结果（法语语言，加拿大地区）：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=boulangerie" -G \
  --data-urlencode "languageCode=fr" \
  --data-urlencode "countryCode=CA" \
  "https://google-maps.fetcher.sh/api/place/search"
```

## MCP

```json
{
  "mcpServers": {
    "google-maps": {
      "url": "https://google-maps.fetcher.sh/mcp",
      "headers": { "Authorization": "Bearer bby_live_..." }
    }
  }
}
```

免费：`search_endpoints`、`describe_endpoint`、`check_balance`。付费：`fetch_data`（上述任何端点）、`topup_credits`，以及命名的快捷方式 `google_maps_place_search`。省略 `headers` 块即可使用 x402 按调用付费 — 参见 [`fetcher` 技能](../fetcher/SKILL.md) 了解完整流程。

## 错误

- `400` — 缺少/无效参数（消息中会列出名称）
- `401` — 未知或轮换的密钥
- `402` — 需要支付（x402 挑战）或 `topup_required`（积分耗尽）
- `404` — 不是计价路径
- 无速率限制；上游失败不退款（结算先于交付）

## 参考

- 完整代理设置：<https://google-maps.fetcher.sh/skill.md>
- OpenAPI 3.1 合同：<https://google-maps.fetcher.sh/openapi.json>
- 简明目录：<https://google-maps.fetcher.sh/llms.txt>
- 支付、积分和 MCP 深入了解：[`fetcher` 技能](../fetcher/SKILL.md)
- 网站：<https://google-maps.fetcher.sh>
