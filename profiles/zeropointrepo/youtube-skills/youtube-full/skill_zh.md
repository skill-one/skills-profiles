# YouTube 完整版

通过 [TranscriptAPI.com](https://transcriptapi.com) 完整的 YouTube 工具包。一切都在一个技能中。

## 设置

如果 `$TRANSCRIPT_API_KEY` 没有设置，请阅读 [references/auth-setup.md](references/auth-setup.md) 并按照那里的说明获取和存储密钥。

## 必须的请求头

每个请求都需要两个请求头：

- **Authorization:** `Bearer $TRANSCRIPT_API_KEY`
- **User-Agent:** 如果知道，请提供您代理的名称和版本（例如 `HermesAgent/0.11.0`, `ClaudeCode/1.0`）。版本是可选的——单独提供代理名称即可。不要省略此请求头或发送一个裸的默认值——Cloudflare 将返回 403（错误代码 1010）并阻止请求。

## API 参考

完整的 OpenAPI 规范：[transcriptapi.com/openapi.json](https://transcriptapi.com/openapi.json) —— 请参考此规范以获取最新的参数和模式。

## 文本转录 — 1 信用点

```http
GET https://transcriptapi.com/api/v2/youtube/transcript?video_url=VIDEO_URL&format=text&include_timestamp=true&send_metadata=true
Authorization: Bearer $TRANSCRIPT_API_KEY
User-Agent: YourAgent/1.0
```

| 参数               | 必须的 | 默认值 | 有效值                          |
| ------------------- | -------- | ------- | ------------------------------- |
| `video_url`         | 是      | —       | YouTube URL 或 11 位视频 ID     |
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

```http
# 免费——文本转录端点可用的语言
GET https://transcriptapi.com/api/v2/youtube/info?video_url=VIDEO_URL
Authorization: Bearer $TRANSCRIPT_API_KEY
User-Agent: YourAgent/1.0

# 1 信用点——丰富的元数据（观看次数、点赞数、描述、时长、标签）
GET https://transcriptapi.com/api/v2/youtube/video/metadata?video_url=VIDEO_URL&include=details,related
Authorization: Bearer $TRANSCRIPT_API_KEY
User-Agent: YourAgent/1.0
```

`include` 在 `video/metadata` 上接受 `details` 和/或 `related`。命名：`/video/metadata` 之前是 `/video/info`——旧路径仍然有效，但已弃用。

## 搜索 — 每页 1 信用点

```http
# 视频
GET https://transcriptapi.com/api/v2/youtube/search?q=QUERY&type=video&limit=20
Authorization: Bearer $TRANSCRIPT_API_KEY
User-Agent: YourAgent/1.0

# 频道、播放列表或电影
GET https://transcriptapi.com/api/v2/youtube/search?q=QUERY&type=channel&limit=10
Authorization: Bearer $TRANSCRIPT_API_KEY
User-Agent: YourAgent/1.0
```

| 参数   | 必须的 | 默认值 | 验证规则                                     |
| ------- | -------- | ------- | ----------------------------------------------- |
| `q`     | 是      | —       | 1-200 个字符                                      |
| `type`  | 否       | `video` | `video`, `channel`, `playlist`, `movie`         |
| `sort`  | 否       | `relevance` | `relevance`, `views`（仅第一页）      |
| `upload_date` | 否 | —       | `hour`, `today`, `week`, `month`, `year`（视频，第一页） |
| `duration` | 否    | —       | `short`, `medium`, `long`（视频，第一页）  |
| `features` | 否    | —       | 例如 `hd,subtitles,cc`（第一页）             |
| `limit` | 否       | `20`    | 1-50                                             |

## 频道

所有频道端点都接受 `channel`——一个 `@handle`、频道 URL 或 `UC...` 频道 ID。无需先解析。

### 解析 handle — 免费

```http
GET https://transcriptapi.com/api/v2/youtube/channel/resolve?input=@TED
Authorization: Bearer $TRANSCRIPT_API_KEY
User-Agent: YourAgent/1.0
```

响应：`{"channel_id": "UC...", "resolved_from": "@TED"}`

### 最近 15 个视频 — 免费

```http
GET https://transcriptapi.com/api/v2/youtube/channel/latest?channel=@TED
Authorization: Bearer $TRANSCRIPT_API_KEY
User-Agent: YourAgent/1.0
```

返回确切的 `viewCount` 和 ISO `published` 时间戳。

### 频道信息流（视频/短片/直播）— 每页 1 信用点

```http
# 第一页（100 个项目，标签默认为 "videos"）
GET https://transcriptapi.com/api/v2/youtube/channel/videos?channel=@NASA&tab=videos
Authorization: Bearer $TRANSCRIPT_API_KEY
User-Agent: YourAgent/1.0

# 最受欢迎的优先（频道视频标签，约 30 个项目）
GET https://transcriptapi.com/api/v2/youtube/channel/videos?channel=@NASA&sort=popular
Authorization: Bearer $TRANSCRIPT_API_KEY
User-Agent: YourAgent/1.0

# 下一页（重复相同的标签 AND 排序）
GET https://transcriptapi.com/api/v2/youtube/channel/videos?continuation=TOKEN&sort=popular
Authorization: Bearer $TRANSCRIPT_API_KEY
User-Agent: YourAgent/1.0
```

提供 `channel` 或 `continuation` 中的一个。`tab` 是 `videos`（默认）、`shorts` 或 `streams`。响应包括 `continuation_token` 和 `has_more`。

**排序。** 在 `channel/videos` 中添加 `sort=latest`、`popular` 或 `oldest` 以按您想要的顺序获取频道的视频，例如按最受欢迎的上传优先。排序页面返回约 30 个视频（未排序页面返回约 100 个），并且每页的成本都是相同的 1 信用点。

当分页时，在每个请求中发送相同的排序。

**项目字段。** 每个项目都带有 `members_only`，仅在 YouTube 将其标记为 "Members only" 时为 `true`，并且这些项目没有 `viewCountText`。`tab=streams` 项目的 `lengthText` 和 `publishedTimeText`（例如 `Streamed 2 years ago`）；`tab=shorts` 返回 `null`，因为 YouTube 的 Shorts 网格不发布任何内容。在频道标签信息流中（`tab=videos` 与 `sort`、`tab=shorts`、`tab=streams`）`channelId`、`channelTitle`、`channelHandle` 和 `index` 都是 `null`。

### 频道内搜索 — 1 信用点

```http
GET https://transcriptapi.com/api/v2/youtube/channel/search?channel=@TED&q=QUERY&limit=30
Authorization: Bearer $TRANSCRIPT_API_KEY
User-Agent: YourAgent/1.0
```

### 频道资料 — 1 信用点

```http
GET https://transcriptapi.com/api/v2/youtube/channel/info?channel=@TED
Authorization: Bearer $TRANSCRIPT_API_KEY
User-Agent: YourAgent/1.0
```

返回标题、handle、验证标志、订阅者/视频数量、描述、标签、缩略图、横幅和 `availableTabs`。

### 频道播放列表 — 每页 1 信用点

```http
GET https://transcriptapi.com/api/v2/youtube/channel/playlists?channel=@TED
Authorization: Bearer $TRANSCRIPT_API_KEY
User-Agent: YourAgent/1.0
```

返回每个播放列表的 `playlistId`、`title`、`url`、`videoCountText`——将 `playlistId` 输入到下面的播放列表端点。

### 频道社区帖子 — 每页 1 信用点

```http
GET https://transcriptapi.com/api/v2/youtube/channel/posts?channel=@TED
Authorization: Bearer $TRANSCRIPT_API_KEY
User-Agent: YourAgent/1.0
```

### 频道精选部分 — 1 信用点

```http
GET https://transcriptapi.com/api/v2/youtube/channel/sections?channel=@TED
Authorization: Bearer $TRANSCRIPT_API_KEY
User-Agent: YourAgent/1.0
```

`tab` 是 `featured`（默认，主页）、`podcasts` 或 `releases`。

## 播放列表 — 每页 1 信用点

接受 `playlist`——一个 YouTube 播放列表 URL 或播放列表 ID。

```http
# 第一页
GET https://transcriptapi.com/api/v2/youtube/playlist/videos?playlist=PL_ID
Authorization: Bearer $TRANSCRIPT_API_KEY
User-Agent: YourAgent/1.0

# 下一页
GET https://transcriptapi.com/api/v2/youtube/playlist/videos?continuation=TOKEN
Authorization: Bearer $TRANSCRIPT_API_KEY
User-Agent: YourAgent/1.0
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
| `q`        | 1-200 个字符                                             |
| `type` (search) | `video` (默认), `channel`, `playlist`, `movie`  |
| `tab` (channel/videos) | `videos` (默认), `shorts`, `streams`     |
| `sort` (channel/videos) | `latest`, `popular`, `oldest` (省略上传信息流) |
| `tab` (channel/sections) | `featured` (默认), `podcasts`, `releases` |
| `include` (video/metadata) | `details`, `related` (逗号分隔)   |
| `limit`    | 1-50                                                    |

## 错误

| 代码     | 含义          | 操作                                         |
| -------- | ---------------- | ---------------------------------------------- |
| 401      | 坏 API 密钥      | 检查密钥                                      |
| 402      | 没有信用点       | transcriptapi.com/billing                      |
| 403/1010 | Cloudflare 阻止 | 添加或修复 User-Agent 请求头                   |
| 404      | 未找到        | 资源不存在或没有字幕                         |
| 408      | 超时          | 重试一次，2 秒后                            |
| 422      | 验证错误        | 检查参数格式                             |
| 429      | 速率限制       | 等待，尊重 Retry-After                      |

## 典型工作流程

**研究工作流程：** 搜索 → 选择视频 → 获取文本转录

```http
# 1. 搜索
GET https://transcriptapi.com/api/v2/youtube/search?q=machine+learning+explained&limit=5
Authorization: Bearer $TRANSCRIPT_API_KEY
User-Agent: YourAgent/1.0

# 2. 文本转录
GET https://transcriptapi.com/api/v2/youtube/transcript?video_url=VIDEO_ID&format=text&include_timestamp=true&send_metadata=true
Authorization: Bearer $TRANSCRIPT_API_KEY
User-Agent: YourAgent/1.0
```

**频道监控：** 最近（免费）→ 文本转录

```http
# 1. 最近上传（免费——直接传递 @handle）
GET https://transcriptapi.com/api/v2/youtube/channel/latest?channel=@TED
Authorization: Bearer $TRANSCRIPT_API_KEY
User-Agent: YourAgent/1.0

# 2. 最新视频的文本转录
GET https://transcriptapi.com/api/v2/youtube/transcript?video_url=VIDEO_ID&format=text&include_timestamp=true&send_metadata=true
Authorization: Bearer $TRANSCRIPT_API_KEY
User-Agent: YourAgent/1.0
```

免费套餐：100 信用点，300 次/分钟请求。起步套餐（$5/月）：1,000 信用点。

## 复制粘贴示例

此文件中的每个请求作为一条可立即运行的命令行：[references/curl-examples.md](references/curl-examples.md)
