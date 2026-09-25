# YouTube API

按需获取 YouTube 数据：支持视频/频道/播放列表搜索，并可通过真实过滤器（上传日期、时长、排序顺序）进行筛选，频道和视频查询、视频、短片、直播、播放列表内容、评论、话题标签流、热门趋势等——每次调用仅一个 HTTP GET 请求，按量付费。无需开发者控制台项目、无需 OAuth 同意屏幕、无每日配额限制。

基础 URL：`https://youtube.fetcher.sh`

## 认证

有两种付费方式，获取相同数据——完整机制详见 [`fetcher` 技能](../fetcher/SKILL.md)：

```bash
# 1. 预付费积分（推荐——在 https://fetcher.sh/topup 获取密钥
#    或通过 POST /api/credits/topup，参见 fetcher 技能）
export FETCHER_API_KEY="bby_live_xxxxxxxxxxxx"
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://youtube.fetcher.sh/api/search/video?query=hello"

# 2. x402 按次付费——省略头部；无付费的 GET 请求将返回 402，并包含机器可读的支付要求（Base、Polygon、Arbitrum、Monad 或 Solana 上的 USDC）。@x402/fetch 自动签名和重试。
```

每个响应格式为 `{ "status": number, "message": string, "data": ... }`；HTTP 状态码与 `status` 一致。

## 端点（15 个 — 全部为 GET 请求，每次调用 0.005 美元）

| 端点 | 返回内容 |
| --- | --- |
| `/api/search/video` | 符合查询条件的视频；上传日期、时长、排序过滤器 |
| `/api/search/channel` | 符合查询条件的频道 |
| `/api/search/playlist` | 符合查询条件的播放列表 |
| `/api/channel/{id}` | 通过 ID 获取频道详情 |
| `/api/channel/handle/{handle}` | 通过 @handle 获取频道详情 |
| `/api/channel/path` | 通过自定义 URL 路径获取频道详情 |
| `/api/channel/{id}/videos` | 频道的视频 |
| `/api/channel/{id}/shorts` | 频道的短片 |
| `/api/channel/{id}/live-streams` | 频道的直播 |
| `/api/video/{id}` | 视频（或短片）详情 |
| `/api/video/{id}/comments` | 视频的评论 |
| `/api/shorts/{id}` | 短片详情 |
| `/api/playlist/{id}/videos` | 播放列表的视频 |
| `/api/hashtag/{tag}` | 话题标签下的视频 |
| `/api/trending` | 热门视频，可选按地区 |

`{id}` / `{handle}` / `{tag}` 是路径参数。可选 `cursor` / `lang` / `geo` 精细筛选结果；`query`（搜索）和 `channelPath`（路径查询）在出现时为必填项。

## 场景

**本周上传：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=ai agents" -G \
  --data-urlencode "uploadDate=week" \
  "https://youtube.fetcher.sh/api/search/video"
```

**观看次数最多，仅长视频：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=x402 protocol" -G \
  --data-urlencode "sortBy=view_count" \
  --data-urlencode "duration=long" \
  "https://youtube.fetcher.sh/api/search/video"
```

**最新优先：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=stablecoin payments" -G \
  --data-urlencode "sortBy=upload_date" \
  "https://youtube.fetcher.sh/api/search/video"
```

其他 `uploadDate` 值：`hour`、`today`、`month`、`year`。其他 `duration` 值：`short`、`medium`。其他 `sortBy` 值：`relevance`、`rating`。

**搜索频道或播放列表：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=lofi hip hop" -G \
  "https://youtube.fetcher.sh/api/search/channel"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=lofi hip hop" -G \
  "https://youtube.fetcher.sh/api/search/playlist"
```

**通过 ID、handle 或自定义路径获取频道，然后获取其视频、短片和直播：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://youtube.fetcher.sh/api/channel/handle/mkbhd"

curl -H "Authorization: Bearer $FETCHER_API_KEY" -G \
  --data-urlencode "channelPath=@mkbhd" \
  "https://youtube.fetcher.sh/api/channel/path"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://youtube.fetcher.sh/api/channel/UCBJycsmduvYEL83R_U4JriQ/videos"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://youtube.fetcher.sh/api/channel/UCBJycsmduvYEL83R_U4JriQ/shorts"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://youtube.fetcher.sh/api/channel/UCBJycsmduvYEL83R_U4JriQ/live-streams"
```

**视频详情和评论，或短片详情：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://youtube.fetcher.sh/api/video/dQw4w9WgXcQ"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "sort=top" -G \
  "https://youtube.fetcher.sh/api/video/dQw4w9WgXcQ/comments"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://youtube.fetcher.sh/api/shorts/abc123XYZ90"
```

**播放列表的视频、话题标签下的视频和热门趋势（按地区）：**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://youtube.fetcher.sh/api/playlist/PLFgquLnL59alCl_2TQvOiD5Vgm1hCaGSI/videos"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://youtube.fetcher.sh/api/hashtag/shorts"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "geo=US" -G \
  "https://youtube.fetcher.sh/api/trending"
```

## MCP

```json
{
  "mcpServers": {
    "youtube": {
      "url": "https://youtube.fetcher.sh/mcp",
      "headers": { "Authorization": "Bearer bby_live_..." }
    }
  }
}
```

免费：`search_endpoints`、`describe_endpoint`、`check_balance`。付费：`fetch_data`（上述任何端点）、`topup_credits`，以及命名快捷 `youtube_search_video`。省略 `headers` 块即可使用 x402 按次付费——详见 [`fetcher` 技能](../fetcher/SKILL.md) 的完整流程。

## 错误

- `400` — 缺少/无效参数（消息中会指明）
- `401` — 未知或已轮换的密钥
- `402` — 需要付费（x402 挑战）或 `topup_required`（积分耗尽）
- `404` — 非计费路径
- 无速率限制；上游失败不退款（结算先于交付）

## 参考

- 完整代理设置：<https://youtube.fetcher.sh/skill.md>
- OpenAPI 3.1 合同：<https://youtube.fetcher.sh/openapi.json>
- 精简目录：<https://youtube.fetcher.sh/llms.txt>
- 付费、积分和 MCP 深入：[`fetcher` 技能](../fetcher/SKILL.md)
- 网站：<https://youtube.fetcher.sh>
