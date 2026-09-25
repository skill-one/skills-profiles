# Apple App Store API

App Store 应用和捆绑包搜索、详情、评论、相似应用和开发者目录，跨越任何国家的商店——每次调用一个简单的 HTTP GET，按需付费。无需 Apple 开发者计划会员资格，无需 App Store Connect 访问权限，无需抓取商店 HTML。

基础 URL：`https://appstore.fetcher.sh`

## 认证

两种付费方式，相同的数据——完整的机制在 [`fetcher` 技能](../fetcher/SKILL.md) 中：

```bash
# 1. 预付费积分（推荐——在 https://fetcher.sh/topup 获取密钥
#    或通过 POST /api/credits/topup，参见 fetcher 技能）
export FETCHER_API_KEY="bby_live_xxxxxxxxxxxx"
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://appstore.fetcher.sh/api/apps?term=meditation"

# 2. x402 按调用付费——省略头部；无支付的 GET 会返回 402，并附带机器可读的支付要求（Base、Polygon、Arbitrum、Monad 或 Solana 上的 USDC）。@x402/fetch 自动签名和重试。
```

每个响应都是 `{ "status": number, "message": string, "data": ... }`；HTTP 状态与 `status` 相同。

## 端点（9 个——全部为 GET，每次调用 0.003 美元）

| 端点 | 返回内容 |
| --- | --- |
| `/api/apps` | 匹配关键词的应用；页面和国家商店过滤 |
| `/api/apps/{appId}` | 应用的完整详情 |
| `/api/apps/{appId}/reviews` | 应用的评论 |
| `/api/apps/{appId}/similar` | 与给定应用相似的应用 |
| `/api/bundles` | 匹配关键词的应用捆绑包 |
| `/api/bundles/{bundleId}` | 捆绑包的完整详情 |
| `/api/bundles/{bundleId}/reviews` | 捆绑包的评论 |
| `/api/bundles/{bundleId}/similar` | 与给定捆绑包相似的应用捆绑包 |
| `/api/developers/{developerId}` | 开发者的完整应用目录 |

在 `/api/apps` 和 `/api/bundles` 上必须包含 `term`。 everywhere 可选：`country`（商店，例如 `us`、`jp`、`de`）、`lang`、`page`。评论支持 `sort` (`recent`、`helpful`)。

## 场景

**美国商店搜索：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "term=habit tracker" -G \
  --data-urlencode "country=us" \
  "https://appstore.fetcher.sh/api/apps"
```

**日本商店搜索：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "term=camera" -G \
  --data-urlencode "country=jp" \
  "https://appstore.fetcher.sh/api/apps"
```

**应用的完整详情，然后按有用性排序的评论：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "country=us" -G \
  "https://appstore.fetcher.sh/api/apps/324684580"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "country=us" -G \
  --data-urlencode "sort=helpful" \
  "https://appstore.fetcher.sh/api/apps/324684580/reviews"
```

**与给定应用相似的应用：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "country=us" -G \
  "https://appstore.fetcher.sh/api/apps/324684580/similar"
```

**搜索和获取应用捆绑包：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "term=photo editing suite" -G \
  "https://appstore.fetcher.sh/api/bundles"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "country=us" -G \
  "https://appstore.fetcher.sh/api/bundles/1234567890"
```

**开发者的完整应用目录：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://appstore.fetcher.sh/api/developers/284882218"
```

## MCP

```json
{
  "mcpServers": {
    "app-store": {
      "url": "https://appstore.fetcher.sh/mcp",
      "headers": { "Authorization": "Bearer bby_live_..." }
    }
  }
}
```

免费：`search_endpoints`、`describe_endpoint`、`check_balance`。付费：`fetch_data`（上述任何端点）、`topup_credits`，以及命名的快捷方式 `appstore_apps`。省略 `headers` 块即可用 x402 按调用付费——参见 [`fetcher` 技能](../fetcher/SKILL.md) 的完整流程。

## 错误

- `400` — 缺少/无效参数（消息中会列出名称）
- `401` — 未知或旋转的密钥
- `402` — 需要支付（x402 挑战）或 `topup_required`（积分耗尽）
- `404` — 不是计价路径
- 无速率限制；上游失败不退款（结算先于交付）

## 参考

- 完整代理设置：<https://appstore.fetcher.sh/skill.md>
- OpenAPI 3.1 合同：<https://appstore.fetcher.sh/openapi.json>
- 精简目录：<https://appstore.fetcher.sh/llms.txt>
- 支付、积分和 MCP 深入了解：[`fetcher` 技能](../fetcher/SKILL.md)
- 网站：<https://appstore.fetcher.sh>
