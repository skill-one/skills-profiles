# Google News API

Google News 标题和搜索以干净的 JSON 格式呈现 — 每次调用仅一个简单的 HTTP GET 请求，按需付费。无需 RSS 源抓取，无需手动解码重定向 URL，无需未公开的内部端点。

基础 URL：`https://google-news.fetcher.sh`

## 认证

有两种付费方式，获取相同的数据 — 完整机制在 [`fetcher` 技能](../fetcher/SKILL.md) 中：

```bash
# 1. 预付费积分（推荐 — 在 https://fetcher.sh/topup 获取密钥
#    或通过 POST /api/credits/topup，参见 fetcher 技能）
export FETCHER_API_KEY="bby_live_xxxxxxxxxxxx"
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://google-news.fetcher.sh/api/search?keyword=hello&languageCode=en-US"

# 2. x402 按调用付费 — 省略头部；无支付的 GET 请求返回 402，并包含机器可读的支付要求（Base、Polygon、Arbitrum、Monad 或 Solana 上的 USDC）。@x402/fetch 自动签名和重试。
```

每个响应都是 `{ "status": number, "message": string, "data": ... }`；HTTP 状态码与 `status` 一致。

## 端点 (12 — 全部为 GET，每次调用 $0.005)

| 端点 | 返回内容 |
| --- | --- |
| `/api/search` | 匹配关键词的一个语言版面的标题 |
| `/api/latest` | 最新标题 |
| `/api/world` | 世界版面的标题 |
| `/api/business` | 商业版面的标题 |
| `/api/technology` | 科技版面的标题 |
| `/api/entertainment` | 娱乐版面的标题 |
| `/api/sport` | 体育版面的标题 |
| `/api/science` | 科学版面的标题 |
| `/api/health` | 健康版面的标题 |
| `/api/topic/{topicId}` | 指定主题 ID 的标题 |
| `/api/language-regions` | 每个支持的 `languageCode` 值 |
| `/api/decode-article-url` | 解析 Google News 重定向 URL 到真实文章 URL |

`languageCode`（例如 `en-US`、`en-GB`、`fr-FR`）在除 `/api/language-regions` 以外的所有端点中都是**必需的**，该端点不接受任何参数，专门用于列出有效值。`keyword` 在 `/api/search` 中额外必需；`url` 在 `/api/decode-article-url` 中必需。

## 场景

**关键词搜索，美国英语版：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "keyword=stablecoin regulation" -G \
  --data-urlencode "languageCode=en-US" \
  "https://google-news.fetcher.sh/api/search"
```

**相同搜索，英国英语版：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "keyword=ai policy" -G \
  --data-urlencode "languageCode=en-GB" \
  "https://google-news.fetcher.sh/api/search"
```

**版面标题（科技、商业）：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "languageCode=en-US" -G \
  "https://google-news.fetcher.sh/api/technology"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "languageCode=en-US" -G \
  "https://google-news.fetcher.sh/api/business"
```

**特定主题 ID 的标题：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "languageCode=en-US" -G \
  "https://google-news.fetcher.sh/api/topic/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGxqTVdZU0FtVnVHZ0pWVXlnQVAB"
```

**在选择一个之前列出所有支持的语言/区域代码：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://google-news.fetcher.sh/api/language-regions"
```

**将 Google News 重定向 URL 解码为真实文章链接：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" -G \
  --data-urlencode "url=https://news.google.com/rss/articles/CBMi..." \
  "https://google-news.fetcher.sh/api/decode-article-url"
```

## MCP

```json
{
  "mcpServers": {
    "google-news": {
      "url": "https://google-news.fetcher.sh/mcp",
      "headers": { "Authorization": "Bearer bby_live_..." }
    }
  }
}
```

免费：`search_endpoints`、`describe_endpoint`、`check_balance`。付费：`fetch_data`（上述任何端点）、`topup_credits`，以及命名的快捷方式 `google_news_search`。省略 `headers` 块即可使用 x402 按调用付费 — 详见 [`fetcher` 技能](../fetcher/SKILL.md) 的完整流程。

## 错误

- `400` — 缺少/无效参数（消息中会指明） — 最常见的是缺少 `languageCode`
- `401` — 未知或轮换的密钥
- `402` — 需要支付（x402 挑战）或 `topup_required`（积分耗尽）
- `404` — 不是计价路径
- 无速率限制；上游失败不退款（结算先于交付）

## 参考

- 完整代理设置：<https://google-news.fetcher.sh/skill.md>
- OpenAPI 3.1 合同：<https://google-news.fetcher.sh/openapi.json>
- 精简目录：<https://google-news.fetcher.sh/llms.txt>
- 支付、积分和 MCP 深入了解：[`fetcher` 技能](../fetcher/SKILL.md)
- 网站：<https://google-news.fetcher.sh>
