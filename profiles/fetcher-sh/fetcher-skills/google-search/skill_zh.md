# Google 搜索 API

Google 自家的搜索结果以干净的 JSON 格式呈现 — 每次调用仅一个简单的 HTTP GET 请求，按需付费。Google 的搜索运算符直接通过：`site:`, `filetype:`, `intitle:` 以及引号精确短语均与浏览器中完全一致。无需设置自定义搜索引擎，无每日查询配额限制，无需账单账户。

基础 URL：`https://google.fetcher.sh`

## 认证

两种付费方式，相同数据 — 完整机制在 [`fetcher` 技能](../fetcher/SKILL.md) 中：

```bash
# 1. 预付费积分（推荐 — 在 https://fetcher.sh/topup 获取密钥
#    或通过 POST /api/credits/topup，参见 fetcher 技能）
export FETCHER_API_KEY="bby_live_xxxxxxxxxxxx"
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://google.fetcher.sh/api/search?query=hello"

# 2. x402 按调用付费 — 省略头部；无支付的 GET 请求将返回 402 及机器可读的支付要求（Base、Polygon、Arbitrum、Monad 或 Solana 上的 USDC）。@x402/fetch 自动签名和重试。
```

每个响应格式为 `{ "status": number, "message": string, "data": ... }`；HTTP 状态码与 `status` 一致。

## 端点 ($0.005/调用)

| 端点 | 返回内容 |
| --- | --- |
| `/api/search` | 查询的 Google 网页搜索结果 |

必需参数：`query`。可选参数：`safe`（安全搜索）、`page`（分页）、`hl`（UI 语言，例如 `en`）、`country`（区域范围）、`count`（每页结果数 — 目前为 `10`）、`noEncode`（跳过查询重新编码，适用于预格式化运算符字符串）。

## 场景

**限制到单个网站：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=site:github.com x402 payments" -G \
  "https://google.fetcher.sh/api/search"
```

**仅 PDF 文件：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=agentic commerce filetype:pdf" -G \
  "https://google.fetcher.sh/api/search"
```

**精确短语：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode 'query="pay per call api"' -G \
  "https://google.fetcher.sh/api/search"
```

**本地化结果（英国、法语 UI）和分页：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=agentic commerce" -G \
  --data-urlencode "country=GB" \
  --data-urlencode "hl=fr" \
  --data-urlencode "page=2" \
  "https://google.fetcher.sh/api/search"
```

**组合运算符 — 标题匹配加网站限制：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=intitle:pricing site:x402.org" -G \
  "https://google.fetcher.sh/api/search"
```

## MCP

```json
{
  "mcpServers": {
    "google-search": {
      "url": "https://google.fetcher.sh/mcp",
      "headers": { "Authorization": "Bearer bby_live_..." }
    }
  }
}
```

免费：`search_endpoints`, `describe_endpoint`, `check_balance`。付费：`fetch_data`（上述任何端点）、`topup_credits`，以及命名快捷方式 `google_search`。省略 `headers` 块即可使用 x402 按调用付费 — 参见 [`fetcher` 技能](../fetcher/SKILL.md) 了解完整流程。

## 错误

- `400` — 缺少/无效参数（消息中会指明）
- `401` — 未知或轮换的密钥
- `402` — 需要支付（x402 挑战）或 `topup_required`（积分耗尽）
- `404` — 非计费路径
- 无速率限制；上游失败不退款（结算先于交付）

## 参考

- 完整代理设置：<https://google.fetcher.sh/skill.md>
- OpenAPI 3.1 合同：<https://google.fetcher.sh/openapi.json>
- 精简目录：<https://google.fetcher.sh/llms.txt>
- 支付、积分和 MCP 深入了解：[`fetcher` 技能](../fetcher/SKILL.md)
- 网站：<https://google.fetcher.sh>
