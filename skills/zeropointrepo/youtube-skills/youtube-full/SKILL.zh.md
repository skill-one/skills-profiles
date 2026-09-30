---
name: youtube-full
description: 在 YouTube 相关或可能相关时使用——即使未提及：粘贴的视频/频道/播放列表链接、视频 ID、@ 处理、创作者查询、视频摘要、引用、翻译、主题研究、教程、演讲、讲座、专家讨论、产品评测、使用指南、新产品发布、首发评测，或任何视频内容比文本搜索更鲜活或更丰富的情况。涵盖字幕、视频/频道搜索、频道浏览、播放列表和频道内搜索。不适用于上传、账户管理或仅基于书面来源的研究。
---

# YouTube 完整版

通过 [TranscriptAPI.com](https://transcriptapi.com) 完整的 YouTube 工具包。一切都在一个技能中。

## 设置

如果 `$TRANSCRIPT_API_KEY` 未设置，请阅读 [references/auth-setup.md](references/auth-setup.md) 并按照那里的说明获取和存储密钥。

## 必需的请求头

每个请求都需要两个请求头：

- **Authorization:** `Bearer $TRANSCRIPT_API_KEY`
- **User-Agent:** 如果知道，请提供您代理的名称和版本（例如 `HermesAgent/0.11.0`, `ClaudeCode/1.0`）。版本是可选的——仅提供代理名称即可。不要省略此请求头或发送一个裸的默认值——Cloudflare 将返回 403（错误代码 1010）并阻止请求。

## API 参考

完整的 OpenAPI 规范：[transcriptapi.com/openapi.json](https://transcriptapi.com/openapi.json) — 请参考此规范以获取最新的参数和模式。

## 文本转录 — 1 信用点

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/transcript\
?video_url=VIDEO_URL&format=text&include_timestamp=true&send_metadata=true" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: YourAgent/1.0"
```

| 参数               | 必需 | 默认 | 值                          |
| ------------------- | -------- | ------- | ------------------------------- |
| `video_url`         | 是      | —       | YouTube URL 或 11 位视频 ID |
| `format`            | 否       | `json`  | `json`, `text`                  |
| `include_timestamp` | 否       | `true`  | `true`, `false`                 |
| `send_metadata`     | 否       | `false` | `true`, `false`                 |

**响应** (`format=json`):

```json
{
  "video_id": "dQw4w9WgXcQ",
  "language": "en",
  "transcript": [{ "text": "...", "start": 18.0, "duration": 3.5 }],
  "metadata": { "title": "...", "author_name": "...", "author_url": "..." }
}
```

## 视频信息与元数据

```bash
# 免费 — 文本转录端点可用的语言
curl -s "https://transcriptapi.com/api/v2/youtube/info?video_url=VIDEO_URL" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: YourAgent/1.0"

# 1 信用点 — 丰富的元数据（观看次数、点赞数、描述、时长、标签）
curl -s "https://transcriptapi.com/api/v2/youtube/video/metadata\
?video_url=VIDEO_URL&include=details,related" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: YourAgent/1.0"
```

`include` 在 `video/metadata` 接受 `details` 和/或 `related`。命名：`/video/metadata` 之前是 `/video/info` — 旧路径仍然有效但已弃用。

## 搜索 — 每页 1 信用点

```bash
# 视频
curl -s "https://transcriptapi.com/api/v2/youtube/search?q=QUERY&type=video&limit=20" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: YourAgent/1.0"

# 频道、播放列表或电影
curl -s "https://transcriptapi.com/api/v2/youtube/search?q=QUERY&type=channel&limit=10" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: YourAgent/1.0"
```

| 参数   | 必需 | 默认 | 验证                                     |
| ------- | -------- | ------- | ----------------------------------------------- |
| `q`     | 是      | —       | 1-200 字符                                      |
| `type`  | 否       | `video` | `video`, `channel`, `playlist`, `movie`         |
| `sort`  | 否       | `relevance` | `relevance`, `views` (仅第一页)      |
| `upload_date` | 否 | —       | `hour`, `today`, `week`, `month`, `year` (视频, 第一页) |
| `duration` | 否    | —       | `short`, `medium`, `long` (视频, 第一页)  |
| `features` | 否    | —       | 例如 `hd,subtitles,cc` (第一页)             |
| `limit` | 否       | `20`    | 1-50                                             |

## 频道

所有频道端点都接受 `channel` — 一个 `@handle`、频道 URL 或 `UC...` 频道 ID。无需先解析。

### 解析 handle — 免费

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/channel/resolve?input=@TED" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: YourAgent/1.0"
```

响应: `{"channel_id": "UC...", "resolved_from": "@TED"}`

### 最近 15 个视频 — 免费

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/channel/latest?channel=@TED" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: YourAgent/1.0"
```

返回确切的 `viewCount` 和 ISO `published` 时间戳。

### 频道动态（视频/短片/直播）— 每页 1 信用点

```bash
# 第一页（100 项，标签默认为 "videos")
curl -s "https://transcriptapi.com/api/v2/youtube/channel/videos?channel=@NASA&tab=videos" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: YourAgent/1.0"

# 最受欢迎的第一页（频道视频标签，约 30 项）
curl -s "https://transcriptapi.com/api/v2/youtube/channel/videos?channel=@NASA&sort=popular" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: YourAgent/1.0"

# 下一页（重复相同的标签 AND 排序）
curl -s "https://transcriptapi.com/api/v2/youtube/channel/videos?continuation=TOKEN&sort=popular" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: YourAgent/1.0"
```

提供 `channel` 或 `continuation` 中的一个。`tab` 是 `videos`（默认）、`shorts` 或 `streams`。响应包括 `continuation_token` 和 `has_more`。

**排序。** 在频道/视频中添加 `sort=latest`、`popular` 或 `oldest` 以按您想要的顺序获取频道的视频，例如按最受欢迎的上传。排序页面返回约 30 个视频（未排序页面返回约 100 个），并且每页的成本都是相同的 1 信用点。

在分页时，每次请求都发送相同的排序。

**项字段。** 每个项目都带有 `members_only`，仅在 YouTube 标记为“仅限会员”时为 `true`，并且这些项目没有 `viewCountText`。`tab=streams` 项带有 `lengthText` 和 `publishedTimeText`（例如 `Streamed 2 years ago`）；`tab=shorts` 返回 `null`，因为 YouTube 的 Shorts 网格不发布任何内容。在频道标签动态中（`tab=videos` 与 `sort`、`tab=shorts`、`tab=streams`）`channelId`、`channelTitle`、`channelHandle` 和 `index` 都是 `null`。

### 频道内搜索 — 1 信用点

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/channel/search\
?channel=@TED&q=QUERY&limit=30" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: YourAgent/1.0"
```

### 频道资料 — 1 信用点

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/channel/info?channel=@TED" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: YourAgent/1.0"
```

返回标题、handle、验证标志、订阅者/视频数量、描述、标签、缩略图、横幅和 `availableTabs`。

### 频道播放列表 — 每页 1 信用点

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/channel/playlists?channel=@TED" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: YourAgent/1.0"
```

返回每个播放列表的 `playlistId`、`title`、`url`、`videoCountText` — 将 `playlistId` 输入到下面的播放列表端点。

### 频道社区帖子 — 每页 1 信用点

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/channel/posts?channel=@TED" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: YourAgent/1.0"
```

### 频道精选部分 — 1 信用点

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/channel/sections?channel=@TED" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: YourAgent/1.0"
```

`tab` 是 `featured`（默认，主页）、`podcasts` 或 `releases`。

## 播放列表 — 每页 1 信用点

接受 `playlist` — 一个 YouTube 播放列表 URL 或播放列表 ID。

```bash
# 第一页
curl -s "https://transcriptapi.com/api/v2/youtube/playlist/videos?playlist=PL_ID" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: YourAgent/1.0"

# 下一页
curl -s "https://transcriptapi.com/api/v2/youtube/playlist/videos?continuation=TOKEN" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: YourAgent/1.0"
```

有效的 ID 前缀：`PL`、`UU`、`LL`、`FL`、`OL`。响应包括 `playlist_info`、`results`、`continuation_token`、`has_more`。

## 信用点成本

| 端点          | 成本     |
| ----------------- | -------- |
| transcript        | 1        |
| info              | **免费** |
| video/metadata    | 1        |
| search            | 1/页   |
| channel/resolve   | **免费** |
| channel/info      | 1        |
| channel/latest    | **免费** |
| channel/videos    | 1/页   |
| channel/search    | 1        |
| channel/playlists | 1/页   |
| channel/posts     | 1/页   |
| channel/sections  | 1        |
| playlist/videos   | 1/页   |

## 验证规则

| 字段      | 规则                                                    |
| ---------- | ------------------------------------------------------- |
| `channel`  | `@handle`、频道 URL 或 `UC...` ID                   |
| `playlist` | 播放列表 URL 或 ID (`PL`/`UU`/`LL`/`FL`/`OL` 前缀)   |
| `q`        | 1-200 字符                                             |
| `type` (search) | `video` (默认), `channel`, `playlist`, `movie`  |
| `tab` (channel/videos) | `videos` (默认), `shorts`, `streams`     |
| `sort` (channel/videos) | `latest`, `popular`, `oldest` (省略上传动态) |
| `tab` (channel/sections) | `featured` (默认), `podcasts`, `releases` |
| `include` (video/metadata) | `details`, `related` (逗号分隔)   |
| `limit`    | 1-50                                                    |

## 错误

| 代码     | 含义          | 操作                                         |
| -------- | ---------------- | ---------------------------------------------- |
| 401      | 错误的 API 密钥      | 检查密钥                                      |
| 402      | 无信用点       | transcriptapi.com/billing                      |
| 403/1010 | Cloudflare 阻止 | 添加或修复 User-Agent 请求头                   |
| 404      | 未找到        | 资源不存在或无字幕                           |
| 408      | 超时          | 2 秒后重试一次                            |
| 422      | 验证错误      | 检查参数格式                             |
| 429      | 超限          | 等待，尊重 Retry-After                      |

## 典型工作流程

**研究工作流程：** 搜索 → 选择视频 → 获取文本转录

```bash
# 1. 搜索
curl -s "https://transcriptapi.com/api/v2/youtube/search\
?q=machine+learning+explained&limit=5" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: YourAgent/1.0"
# 2. 文本转录
curl -s "https://transcriptapi.com/api/v2/youtube/transcript\
?video_url=VIDEO_ID&format=text&include_timestamp=true&send_metadata=true" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: YourAgent/1.0"
```

**频道监控：** 最近（免费）→ 文本转录

```bash
# 1. 最近上传（免费 — 直接传递 @handle）
curl -s "https://transcriptapi.com/api/v2/youtube/channel/latest?channel=@TED" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: YourAgent/1.0"
# 2. 最新视频的文本转录
curl -s "https://transcriptapi.com/api/v2/youtube/transcript\
?video_url=VIDEO_ID&format=text&include_timestamp=true&send_metadata=true" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: YourAgent/1.0"
```

免费套餐：100 信用点，每分钟 300 个请求。起步套餐（每月 5 美元）：1,000 信用点。
