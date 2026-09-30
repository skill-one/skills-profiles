---
name: web-crawler
description: '网络爬虫结合社交数据：YouTube、TikTok、Instagram、LinkedIn、Reddit、Threads，以及强大的网页回退提取功能。


  适用于提取公开帖子、文本记录或JS密集型页面（例如下载YouTube文本记录、抓取TikTok评论、反爬虫/Cloudflare屏蔽的页面列表）。自动回退触发条件：网络抓取失败、403错误、反爬虫、Cloudflare、JS密集型页面。'
---

## 推荐的入口：调用 exports.py（不要手动编写请求）
现成的辅助工具位于 `skills/web-crawler/exports.py` 中。优先使用它们而不是编写自己的 `proxied_get`/`proxied_post` 调用——它们已经注入了代理凭证，因此**无需寻找 API 密钥**（不要读取 `$SCRAPECREATORS_API_KEY` / `$FIRECRAWL_API_KEY`，不要检查 `.env`，不要询问用户）。

```python
import sys; sys.path.insert(0, "/data/workspace/skills/web-crawler")
from exports import scrape_markdown, youtube_transcript, sc_get
scrape_markdown("https://example.com/article")          # Firecrawl 备用
youtube_transcript("https://youtube.com/watch?v=ID")     # ScrapeCreators
youtube_video("https://youtube.com/watch?v=ID")          # 元数据：标题/描述/上传者 (+ 文本)
sc_get("/v1/tiktok/profile", handle="charlidamelio")     # 任何 SC 端点

from exports import archive_fallback                      # 付费墙 / Firecrawl-403
archive_fallback("https://www.nytimes.com/.../article.html")  # 归档快照
```

### 文本轨道——任何媒体链接的单一入口

```python
from core.skill_tools import web_crawler
r = web_crawler.get_transcript(url, caller_id="chat:<thread>")
# {found, kind, source, text, url, title, tried, note}
```

**设计规则：字幕 / 字幕 / 发布的文本是元数据；媒体文件是有效载荷。** 首先尝试所有元数据提供者；只有在用户明确同意时才接触媒体。相同的规则适用于 claude-video、spoken.md 和 yt-dlp 的 `--skip-download` 工作流程。这里没有特定于网站的：

| 提供者（成本顺序） | 是什么 | 身份 / 有效性检查 |
|---|---|---|
| `media_info(url)` | yt-dlp `extract_info(download=False)` — 1800+ 网站，返回标题、时长、上传日期、频道、字幕轨道 URL。零媒体字节。 | 获取的轨道必须是 2xx 并带有真实正文 |
| RSS `<podcast:transcript>` | Podcasting 2.0 标准，任何播客 | 播放项通过时长 ±5 % + 日期 ±3 天匹配；文本 URL 必须是 2xx，> 500 字符，不是错误页面 |
| 节目自己的 YouTube 上传 | 频道 = 节目在 RSS 中声明的 YouTube URL（否则搜索命中，其频道名**等于**节目名减去停用词） | 候选者 = 时长 ±5 % AND 日期 ±3 天；**身份 = 标题相似度 ≥ 0.6 或 节目笔记重叠**（≥ 6 个共享的独特标记，Jaccard ≥ 0.15）。失败的候选者返回在 `candidate` 中带有 `found=False`——永远不会作为节目交付 |
| `scrape_markdown(url)` | 任何其他页面（发布者、Snipd、博客）——浏览器渲染，可抵抗 WAF 403 | > 1000 字符 |

`found=False` ⇒ 报告 `kind`、`title`、`tried`、`note`（以及 `candidate` 如果有的话）并在任何下载前**询问用户**。YouTube 通过 URL 识别：即使 yt-dlp 元数据失败，字幕 API 也会运行，并且媒体 URL 的页面抓取永远不会报告为文本。`yt-dlp --skip-download` / `-J` / `--list-subs` 是元数据调用并通过 bash 门禁；`yt-dlp <url>`、`curl … .mp3`、ffmpeg、whisper 等需要确认。

仅标题，无链接 → `web_search("<show> <title> transcript")` 然后 `get_transcript(<页面 URL>)`。

事件 2026-09-17：两个 403 在文本主机上导致代理进入 49 MB mp3 + ffmpeg + 4 whisper 调用 + 不完整的摘要。相同的链接通过 `get_transcript`：RSS 没有文本 → RSS 声明 `youtube.com/@a16z` → 频道列表 → 1.2 % 时长内一个上传，同一天 → 字幕，55k 字符，~30 秒，零音频。

## 快速触发规则（首先阅读此部分）
当任何这些条件为真时立即使用此技能：

- `web_fetch` 返回 HTTP **401/403/429/5xx**
- 响应是反机器人挑战页面（例如 Cloudflare "Attention Required", "Just a moment", 或挑战/验证码页面）
- 页面是 JS 重型，第一个抓取错过了必要的字段（例如发布时间、作者、列表代码、更新时间、价格明细）
- 搜索结果不包含请求的字段，值必须从目标页面本身提取

备用规则：
- 如果普通抓取被阻止或不完整，在此技能中切换到 Firecrawl 备用，然后再请求用户截图/手动文本。

## 错误签名 -> 操作
| 签名 | 操作 |
|---|---|
| `web_fetch` HTTP 401/403/429/5xx | 一次调用 Firecrawl `POST /v2/scrape`，带有 `formats:["markdown","links"]` + `onlyMainContent:true` |
| Cloudflare/挑战页面文本在正文 | 上述相同的 Firecrawl 调用 |
| Markdown 仍然缺少关键字段 | 一次重试，带有 `formats:["rawHtml"]` |
| **Firecrawl 返回 403 / 空白对于社交媒体 URL** | 检查下面的意图路由表，为该域查找**ScrapeCreators 平台特定端点**（例如 `sc_get('/v1/instagram/post', url=...)`，`sc_get('/v2/tiktok/video', url=...)`）。如果存在，使用它——这些有专门的提取功能，可以绕过反机器人。如果没有专用端点，则降级到 `archive_fallback` 或询问用户。 |
| **Firecrawl 本身返回 403 / 空白**（硬付费墙：NYT、WSJ、Economist、FT、Bloomberg） | 调用 `archive_fallback(url)` — 从网络存档快照恢复全文 |
| **需要来自中国应用的结构化数据**（抖音/小红书/微博/B站/京东/淘宝/1688/闲鱼/得物等。） | 调用 `apify_run()` — Apify Store 有针对这些平台的专门构建的 actor，Firecrawl/ScrapeCreators 没有覆盖 |

### 付费墙 / Firecrawl-阻止备用链（使用 `archive_fallback`）
当 Firecrawl 也无法获取页面时（它返回 403，或者 markdown 返回为空），该网站后面是硬付费墙或侵略性 WAF。不要继续重试 Firecrawl。从**网络存档快照**中恢复文章：

```python
from exports import archive_fallback
res = archive_fallback("https://www.nytimes.com/.../article.html")
res["markdown"]      # 全文，或 "" 如果任何地方都没有快照
res["source"]        # "archive.today" | "wayback" | None
res["snapshot_url"]  # 被抓取的快照
```

它是如何工作的（以及为什么这个顺序）：
- **archive.today 首先使用** (`archive.ph` / `archive.is` 镜像)。用户触发，真实浏览器捕获；历史上保留了付费墙后的全文。对 NYT/WSJ/Economist 的最佳选择。我们通过 Firecrawl 抓取它的 `/newest/` 快照（archive.today 有自己的 Cloudflare，所以通过 Firecrawl 抓取它，从不直接 `web_fetch` 它）。
- **Wayback Machine 第二** (`archive.org`)。自动爬虫，*尊重* robots.txt 和付费墙，所以它通常没有硬付费墙的全文——但它对于普通 403/Cloudflare 页面（未付费墙）是一个很好的备用。

限制：存档只返回**有人已经保存**的文本。如果 `res["markdown"] == ""`，没有快照——停止，告诉用户，并尝试出处的官方 API/RSS 或其他来源。不要编造文章。

### 中国应用的结构化数据（使用 `apify_run`）

当你需要**来自中国应用的结构化数据**——抖音视频搜索、小红书笔记、微博帖子、B站视频、京东/淘宝产品价格、1688 批发列表、闲鱼二手、得物运动鞋等。——Firecrawl 和 ScrapeCreators 没有覆盖这些平台。使用 **Apify Store** 备用。Apify 是一个无服务器爬虫市场，有数百个社区维护的 actor，它们运行真实浏览器 + 代理池针对中国平台。

**认证：** 无需用户提供密钥。sc-proxy 自动注入平台令牌。`Authorization: Bearer` 头部可以是任何假值——代理用真实令牌替换它。不要从 env 读取 `$APIFY_TOKEN`，不要检查 `.env`，不要询问用户 Apify 密钥。

**何时使用 Apify（与 Firecrawl/ScrapeCreators 相比）：**
- ✅ 中国应用：抖音、小红书、微博、B站、京东、淘宝、1688、闲鱼、得物、携程、知乎、豆瓣、雪球、快手、爱奇艺、优酷
- ✅ 东南亚电子商务：Shopee、Lazada、Temu
- ❌ 西方社交媒体（TikTok/Instagram/YouTube/X/Reddit）→ 首先使用 ScrapeCreators（更便宜）
- ❌ 通用网页抓取 → 首先使用 Firecrawl（更便宜）
- ❌ 硬付费墙文章 → 使用 `archive_fallback`（Apify 帮不上忙）

**如何选择 actor：** 可靠 actor 目录位于 `output/apify_china_reliable.json`（按 30 天成功计数排序）。为目标平台选择顶 actor。一些常见的：

| 平台 | Actor ID | 输入键 |
|---|---|---|
| 抖音搜索 | `zen-studio~douyin-search-scraper` | `{"keywords": [...], "maxResultsPerQuery": N}` |
| 小红书搜索 | `zen-studio~rednote-search-scraper` | `{"keywords": [...], "maxResults": N}` |
| 小红书笔记详情 | `sian.agency~xiaohongshu-rednote-scraper` | `{"operation": "noteDetail", "noteId": "...", "xsecToken": "..."}` |
| 微博热搜 | `gentle_cloud~weibo-hot-search-scraper` | `{"mode": "hot_band", "includeScores": true}` |
| 微博帖子 | `zhorex~weibo-scraper` | (见 actor 输入模式) |
| B站视频 | `zhorex~bilibili-scraper` | (见 actor 输入模式) |
| 京东搜索 | `zen-studio~jd-com-search-scraper` | `{"keyword": "...", "maxProducts": N}` |
| 京东产品 | `sian.agency~jd-com-product-scraper` | `{"operation": "productSearch", "keyword": "...", "maxPages": 1}` |
| 淘宝产品 | `sian.agency~taobao-tmall-product-scraper` | `{"operation": "keywordSearch", "keyword": "...", "maxPages": 1}` |
| 1688 批发 | `zen-studio~1688-wholesale-scraper` | (见 actor 输入模式) |
| 闲鱼搜索 | `zen-studio~goofish-xianyu-search-scraper` | (见 actor 输入模式) |
| TikTok | `clockworks~tiktok-scraper` | `{"hashtags": [...]}` 或 `{"profiles": [...]}` |

**两步小红书工作流程（搜索 → 笔记详情）：**
搜索抓取器 (`zen-studio~rednote-search-scraper`) 只返回截断的 `desc` (~60 字符)。为了获取完整的帖子正文，以 `noteDetail` 模式运行第二个调用，传递搜索结果行中的 `id` 和 `xsec_token`。这是获取完整笔记文本的唯一可靠方法，用于价格/住宿/行程详情。

**使用方法：**

```python
import sys
sys.path.insert(0, "/data/workspace/skills/web-crawler")
from exports import apify_run

# 同步运行（小批量，≤100 结果）：阻塞直到完成，返回结果列表
results = apify_run("zen-studio~douyin-search-scraper",
                     {"keywords": ["MacBook"], "maxResultsPerQuery": 5})
for r in results:
    print(r.get("text", "")[:80])

# 为了发现不熟悉 actor 的正确输入字段，首先通过 Firecrawl 获取其输入模式页面：
from exports import scrape_markdown
schema_md = scrape_markdown("https://apify.com/<user>/<actor>/input-schema")
```

**计费 & 成本控制——在每次 Apify 调用前阅读：**

Apify 使用 **按事件付费** 计费：`(actor-start + result_count × per_result + add-ons) × 2` 信用。主要因素是 **result_count × per-result price**，并且**每个 actor 的价格都不同** ($0.003–$0.007/结果)。未知的 actor 默认为最高级别 ($0.007)。完整定价表和估算示例：`reference/apify-pricing.md`。

**你必须在使用前估算成本：**
1. 查找 actor 的每结果价格（`reference/apify-pricing.md` 中的表格；未列出 = $0.007）。
2. 从输入参数估算结果数量（`maxResults`、`maxProducts` 等）。如果没有限制，假设 100+。
3. 计算：`result_count × per_result × 2` = 估算信用。
4. **如果估算 > 5 信用，在进行下一步之前告诉用户成本。**

**硬支出上限——代理强制的默认值 + 每次调用覆盖：**

代理**自动注入** `maxTotalChargeUsd=$2.5`（≈ 5 信用）在**每个没有指定一个的 actor 运行**。Apify 在预算耗尽时终止运行并返回到目前为止收集的结果——不会超支，不会失控成本。

`apify_run()` 也传递 `max_charge_usd`（相同的默认 $2.5），它优先于代理默认值。这意味着：

- **默认（无额外参数）：** 每次调用限制在 ≈ 5 信用。适用于常规搜索、个人资料查找、小批量抓取。
- **需要更多数据？** 明确提高上限：`max_charge_usd=10`（≈ 20 信用）。在用户明确想要大型数据集并且你已经告诉他们估算成本时使用。
- **首次测试：** 降低它：`max_charge_usd=0.5`（≈ 1 信用），限制结果为 5–10，在扩大之前验证输出质量。
- **完全禁用上限：** `max_charge_usd=None`。**除非**用户在警告潜在成本后明确要求无上限运行，否则**永远不要这样做**。

**小批量测试首先：**
当第一次使用 actor 时，设置 `max_charge_usd=0.5`（≈ 1 信用）并限制结果为 5–10。在扩大之前验证输出质量。

**错误处理：**
- `400 run-failed` → 输入错误（字段名错误）。获取 actor 的输入模式页面并修复。
- `401` → 代理配置错误（不应发生）。向用户报告。
- 空结果 `[]` → actor 运行但什么都没找到。尝试不同的关键词或另一个 actor。
- 超时 → 增加 `timeout` 参数（默认 180s）。有些 actor 很慢。

**成本纪律：** Apify actor 比 Firecrawl/ScrapeCreators 更贵。只有在更便宜的选项无法获取数据时（中国应用、结构化电子商务字段）才使用 Apify。对于单个网页，始终首先尝试 Firecrawl。

## 每个服务的作用
### ScrapeCreators — 社交媒体数据提取（27+ 平台）

用于任何涉及社交媒体个人资料、帖子、视频、评论、文本、搜索、广告、热门内容或参与指标的请求。涵盖抖音、Instagram、YouTube、LinkedIn、Facebook、Twitter/X、Reddit、Threads、Bluesky、Pinterest、Snapchat、Twitch、Kick、Truth Social、抖音商店、Google 搜索和链接在生物服务（Linktree、Komi、Pillar、Linkbio、Linkme、Amazon Shop）。

**基础 URL：** `https://api.scrapecreators.com`
**认证：** 无需用户提供密钥。sc-proxy 自动注入平台凭证——只需发送请求。`x-api-key` 头部可以是任何值或完全省略。如果 `$SCRAPECREATORS_API_KEY` 看起来未设置，不要放弃或询问用户密钥；该 env 变量故意不要求。
**方法：** 所有端点都使用带有查询参数的 GET 请求。响应是 JSON。

### Firecrawl — 备用网页抓取器

仅当普通抓取失败时，用于单个网页的备用爬虫。使用 `POST /v2/scrape`，带有单个 `url` 和专注的格式，如 `markdown`、`html`、`rawHtml`、`links`、`summary` 或受约束的 `json`/`question`/`highlights` 提取。

**认证：** 无需用户提供密钥。sc-proxy 在通过 `core.http_client.proxied_post` 调用时自动注入 Firecrawl 凭证——只需发送请求。不要从 env 读取 `$FIRECRAWL_API_KEY`，不要检查 `.env`，如果它看起来未设置，不要询问用户 Firecrawl 密钥；该 env 变量故意不要求。与 ScrapeCreators 相同的代理注入模型适用于此处。

不要使用 Firecrawl crawl/map/search/agent/browser 端点。除非代理策略稍后扩展，否则不要请求屏幕截图、音频、品牌、图像或浏览器操作。

---

## ScrapeCreators — 意图路由
将用户意图映射到正确的端点。端点路径使用模式 `/v1/platform/action`。

**重要：** 从下表中选择端点后，在做出实际 API 调用之前，获取其 OpenAPI 规范，`https://docs.scrapecreators.com/{path}/openapi.json`，以获取完整参数细节、类型和示例响应。例如：`https://docs.scrapecreators.com/v1/tiktok/profile/openapi.json`

### 个人资料 / 用户信息
| 平台 | 端点 | 主要参数 | 示例 |
|------|------|----------|------|
| TikTok | `/v1/tiktok/profile` | handle | `stoolpresidente` |
| Instagram | `/v1/instagram/profile` | handle | `jane` |
| YouTube | `/v1/youtube/channel` | handle, channelId, 或 url | `ThePatMcAfeeShow` |
| LinkedIn (个人) | `/v1/linkedin/profile` | url | `https://www.linkedin.com/in/parrsam/` |
| LinkedIn (公司) | `/v1/linkedin/company` | url | `https://linkedin.com/company/shopify` |
| Facebook | `/v1/facebook/profile` | url | `https://www.facebook.com/mantraindianfolsom` |
| Twitter/X | `/v1/twitter/profile` | handle | `elonmusk` |
| Reddit | `/v1/reddit/subreddit/details` | subreddit 或 url | `AskReddit` |
| Threads | `/v1/threads/profile` | handle | `zuck` |
| Bluesky | `/v1/bluesky/profile` | handle | `jay.bsky.team` |
| Pinterest | `/v1/pinterest/user/boards` | handle | `pinterest` |
| Truth Social | `/v1/truthsocial/profile` | handle | `realDonaldTrump` |
| Twitch | `/v1/twitch/profile` | handle | `ninja` |
| Snapchat | `/v1/snapchat/profile` | handle | `djkhaled` |

### 发布 / 内容动态
| 平台 | 端点 | 主要参数 | 示例 |
|------|------|----------|------|
| TikTok 视频 | `/v3/tiktok/profile/videos` | handle | `stoolpresidente` |
| Instagram 发布 | `/v2/instagram/user/posts` | handle | `jane` |
| Instagram Reels | `/v1/instagram/user/reels` | handle 或 user_id | `jane` 或 `2700692569` |
| Instagram 高亮 | `/v1/instagram/user/highlights` | handle 或 user_id | `jane` 或 `2700692569` |
| YouTube 视频 | `/v1/youtube/channel/videos` | handle 或 channelId | `ThePatMcAfeeShow` |
| YouTube Shorts | `/v1/youtube/channel/shorts` | handle 或 channelId | `starterstory` |
| YouTube 播放列表 | `/v1/youtube/playlist` | playlist_id | `PLP32wGpgzmIlInfgKVFfCwVsxgGqZNIiS` |
| LinkedIn 发布 | `/v1/linkedin/company/posts` | url | `https://linkedin.com/company/shopify` |
| Facebook 发布 | `/v1/facebook/profile/posts` | url 或 pageId | `https://www.facebook.com/pacemorby` |
| Facebook Reels | `/v1/facebook/profile/reels` | url | `https://www.facebook.com/Spurs` |
| Facebook 照片 | `/v1/facebook/profile/photos` | url | `https://www.facebook.com/Spurs` |
| Facebook 小组发布 | `/v1/facebook/group/posts` | url 或 group_id | `742354120555345` |
| Twitter/X 推文 | `/v1/twitter/user/tweets` | handle | `elonmusk` |
| Reddit 发布 | `/v1/reddit/subreddit` | subreddit | `AskReddit` |
| Threads 发布 | `/v1/threads/user/posts` | handle | `zuck` |
| Bluesky 发布 | `/v1/bluesky/user/posts` | handle 或 user_id | `jay.bsky.team` |
| Truth Social 发布 | `/v1/truthsocial/user/posts` | handle 或 user_id | `realDonaldTrump` |
| Pinterest 板块 | `/v1/pinterest/board` | url | `https://www.pinterest.com/...` |

### 单个发布 / 视频详情
| 平台 | 端点 | 主要参数 | 示例 |
|------|------|----------|------|
| TikTok | `/v2/tiktok/video` | url | `https://www.tiktok.com/@randomspamvideos25/video/7251387037834595630` |
| Instagram | `/v1/instagram/post` | url | `https://www.instagram.com/reel/DOq6eV6iIgD` |
| Instagram 高亮 | `/v1/instagram/user/highlight/detail` | id | `18067016518767507` |
| YouTube | `/v1/youtube/video` | url | `https://www.youtube.com/watch?v=Y2Ah_DFr8cw` |
| YouTube 社区发布 | `/v1/youtube/community-post` | url | `https://www.youtube.com/post/Ugkxvj2KoApYAXoqLWnKVr6zZe5JjeHrQeP8` |
| LinkedIn | `/v1/linkedin/post` | url | `https://www.linkedin.com/pulse/being-father-has-made-me-better-leader...` |
| Facebook | `/v1/facebook/post` | url | `https://www.facebook.com/reel/1535656380759655` |
| Twitter/X | `/v1/twitter/tweet` | url | `https://twitter.com/elonmusk/status/...` |
| Twitter/X 社区 | `/v1/twitter/community` | url | `https://twitter.com/i/communities/...` |
| Twitter/X 社区推文 | `/v1/twitter/community/tweets` | url | `https://twitter.com/i/communities/...` |
| Reddit | `/v1/reddit/post/comments` | url | `https://www.reddit.com/r/AskReddit/comments/...` |
| Threads | `/v1/threads/post` | url | `https://www.threads.net/@zuck/post/...` |
| Bluesky | `/v1/bluesky/post` | url | `https://bsky.app/profile/.../post/...` |
| Truth Social | `/v1/truthsocial/post` | url | `https://truthsocial.com/@realDonaldTrump/posts/...` |
| Pinterest | `/v1/pinterest/pin` | url | `https://www.pinterest.com/pin/...` |
| Twitch 剪辑 | `/v1/twitch/clip` | url | `https://clips.twitch.tv/...` |
| Kick 剪辑 | `/v1/kick/clip` | url | `https://kick.com/...` |

### 评论
| 平台 | 端点 | 主要参数 | 示例 |
|------|------|----------|------|
| TikTok | `/v1/tiktok/video/comments` | url | `https://www.tiktok.com/@stoolpresidente/video/7499229683859426602` |
| Instagram | `/v2/instagram/post/comments` | url | `https://www.instagram.com/reel/DOq6eV6iIgD` |
| YouTube | `/v1/youtube/video/comments` | url | `https://www.youtube.com/watch?v=dQw4w9WgXcQ` |
| Facebook | `/v1/facebook/post/comments` | url 或 feedback_id | `https://www.facebook.com/reel/753347914167361` |
| Reddit | `/v1/reddit/post/comments` | url | `https://www.reddit.com/r/AskReddit/comments/...` |

### 文字稿

⚠️ **首先获取元数据。** 文字稿端点返回**仅语音文本 — 无说话人、无标题、无上传者**。在总结视频时，首先调用视频元数据端点（`youtube_video` / `/v1/tiktok/video` / …）获取标题、描述和上传者，然后调用文字稿。**仅凭文字稿内容无法归因说话人或公众人物** — 如果元数据不可用，请说“说话人未识别”，并在总结时不要提及任何人。

| 平台 | 端点 | 示例 | 备注 |
|------|------|------|------|
| TikTok | `/v1/tiktok/video/transcript` | `url=https://www.tiktok.com/...&lang=en` | 也可通过 `/v2/tiktok/video` 使用 get_transcript=true 获取 |
| Instagram | `/v2/instagram/media/transcript` | `url=https://www.instagram.com/reel/...` | 人工智能驱动，10-30秒，最长2分钟 |
| YouTube | `/v1/youtube/video/transcript` | `url=https://www.youtube.com/watch?v=bjVIDXPP7Uk` | 也包含在 `/v1/youtube/video` 响应中 |
| Facebook | `/v1/facebook/post/transcript` | `url=https://www.facebook.com/reel/...` | 仅限2分钟以内 |
| Twitter/X | `/v1/twitter/tweet/transcript` | `url=https://twitter.com/...` | 人工智能驱动，速度较慢 |

### 搜索
| 平台 | 端点 | 主要参数 | 示例 |
|------|------|----------|------|
| TikTok 用户 | `/v1/tiktok/search/users` | query | `funny` |
| TikTok 视频（关键词） | `/v1/tiktok/search/keyword` | query | `funny` |
| TikTok 视频（话题标签） | `/v1/tiktok/search/hashtag` | hashtag | `fyp` |
| TikTok Top（照片+视频） | `/v1/tiktok/search/top` | query | `funny` |
| Instagram Reels | `/v2/instagram/reels/search` | query | `dogs` |
| YouTube | `/v1/youtube/search` | query | `funny` |
| YouTube 话题标签 | `/v1/youtube/search/hashtag` | hashtag | `funny` |
| Reddit（全部） | `/v1/reddit/search` | query | `best programming languages` |
| Reddit（在子版块中） | `/v1/reddit/subreddit/search` | subreddit + query | `AskReddit` + `funny` |
| Threads 发布 | `/v1/threads/search` | query | `AI` |
| Threads 用户 | `/v1/threads/search/users` | query | `zuck` |
| Pinterest | `/v1/pinterest/search` | query | `home decor` |
| Google | `/v1/google/search` | query | `best restaurants in NYC` |

### 广告库
| 平台 | 端点 | 主要参数 | 示例 |
|------|------|----------|------|
| Facebook 广告搜索 | `/v1/facebook/adLibrary/search/ads` | query | `running` |
| Facebook 公司广告 | `/v1/facebook/adLibrary/company/ads` | pageId 或 companyName | `Lululemon` |
| Facebook 广告详情 | `/v1/facebook/adLibrary/ad` | id 或 url | `702369045530963` |
| Facebook 查找公司 | `/v1/facebook/adLibrary/search/companies` | query | `Nike` |
| Google 公司广告 | `/v1/google/company/ads` | domain 或 advertiser_id | `nike.com` |
| Google 广告详情 | `/v1/google/ad` | url | `https://adstransparency.google.com/...` |
| Google 查找广告商 | `/v1/google/adLibrary/advertisers/search` | query | `Nike` |
| LinkedIn 广告搜索 | `/v1/linkedin/ads/search` | company 或 keyword | `Shopify` |
| LinkedIn 广告详情 | `/v1/linkedin/ad` | url | `https://www.linkedin.com/ad/...` |
| Reddit 广告搜索 | `/v1/reddit/ads/search` | query | `gaming` |
| Reddit 广告详情 | `/v1/reddit/ad` | id | `t3_abc123` |

### 热门 / 畅销
| 内容 | 端点 | 参数 | 示例 |
|------|------|------|------|
| 热门动态 | `/v1/tiktok/get-trending-feed` | region（必填） | `US` |
| 畅销视频 | `/v1/tiktok/videos/popular` | | |
| 畅销创作者 | `/v1/tiktok/creators/popular` | | |
| 畅销话题标签 | `/v1/tiktok/hashtags/popular` | | |
| 畅销歌曲 | `/v1/tiktok/songs/popular` | | |
| 歌曲详情 | `/v1/tiktok/song` | clipId | `7439295283975702544` |
| 使用该歌曲的视频 | `/v1/tiktok/song/videos` | clipId | `7439295283975702544` |
| 热门短片（YT） | `/v1/youtube/shorts/trending` | | |

### 关注者 / 关注 / 直播（仅限TikTok）
| 类型 | 端点 | 示例 |
|------|------|------|
| 关注 | `/v1/tiktok/user/following` | `handle=stoolpresidente` |
| 关注者 | `/v1/tiktok/user/followers` | `handle=stoolpresidente` |
| 受众人口统计 | `/v1/tiktok/user/audience`（26个积分！） | `handle=shakira` |
| 直播流 | `/v1/tiktok/user/live` | `handle=thejustalex` |

### TikTok Shop
| 类型 | 端点 | 主要参数 | 示例 |
|------|------|----------|------|
| 搜索商品 | `/v1/tiktok/shop/search` | query | `shoes` |
| 店铺商品 | `/v1/tiktok/shop/products` | url | `https://www.tiktok.com/shop/store/goli-nutrition/7495794203056835079` |
| 商品详情 | `/v1/tiktok/product` | url | `https://www.tiktok.com/shop/pdp/goli-ashwagandha-gummies.../1729587769570529799` |
| 商品评价 | `/v1/tiktok/shop/product/reviews` | url 或 product_id | `1731578642912612516` |
| 用户展示 | `/v1/tiktok/user/showcase` | handle | `mrtiktokreviews` |

### Link-in-Bio / 其他
| 服务 | 端点 | 参数 | 示例 |
|------|------|------|------|
| Linktree | `/v1/linktree` | url | `https://linktr.ee/...` |
| Komi | `/v1/komi` | url | `https://komi.io/...` |
| Pillar | `/v1/pillar` | url | `https://pillar.io/...` |
| Linkbio | `/v1/linkbio` | url | `https://linkbio.co/...` |
| Linkme | `/v1/linkme` | url | `https://linkme.bio/...` |
| Amazon Shop | `/v1/amazon/shop` | url | `https://www.amazon.com/shop/...` |
| Instagram 基础资料 | `/v1/instagram/basic/profile` | userId | `314216` |
| Instagram 嵌入HTML | `/v1/instagram/user/embed` | handle | `jane` |
| 年龄/性别检测 | `/v1/detect/age-gender` | url（社交资料） | `https://www.tiktok.com/@charlidamelio` |
| 信用余额 | `/v1/credit/balance` | （无） | |

### ScrapeCreators 分页

分页端点在响应中返回一个游标/令牌。将其作为查询参数返回以获取下一页。

| 游标字段 | 使用 |
|----------|------|
| `cursor` | TikTok 评论搜索/歌曲视频、Instagram 评论、Reddit 子版块搜索、Pinterest、Bluesky、Facebook Reels/照片/发布/评论、TikTok Shop 商品/用户展示 |
| `max_cursor` | TikTok 个人资料视频 |
| `min_time` | TikTok 关注/关注者 |
| `continuationToken` | YouTube（所有分页端点） |
| `after` | Reddit 发布、Reddit 搜索 |
| `next_max_id` | Instagram 发布、Truth Social 发布 |
| `max_id` | Instagram Reels |
| `page` | TikTok 畅销/店铺、Instagram Reels 搜索、LinkedIn 公司发布、TikTok Shop 评价 |
| `paginationToken` | LinkedIn 广告 |

### ScrapeCreators 已知限制

- **用户名**：无需 `@` 符号。使用 `charlidamelio` 而不是 `@charlidamelio`。适用于 TikTok、Instagram、Twitter、Threads、Bluesky、Snapchat、Twitch、Pinterest、Truth Social
- **YouTube 用户名**：无需 `@` 符号。使用 `ThePatMcAfeeShow` 而不是 `@ThePatMcAfeeShow`。也可以传递 channelId 或完整 URL
- **话题标签**：无需 `#` 符号。使用 `fyp` 而不是 `#fyp`。适用于 TikTok 和 YouTube 话题标签搜索端点
- **Twitter**：返回约100条最热门推文，不是按时间顺序/最新
- **Threads**：仅公开可见最后20-30条发布
- **Facebook 发布**：每页仅3条发布（API限制）
- **Facebook 小组发布**：每页仅3条发布（相同限制）
- **LinkedIn 公司发布**：最多7页
- **Instagram 播放次数**：仅Instagram的观看次数（排除跨平台发布的FB观看次数）
- **Truth Social**：仅知名用户（特朗普、范斯等）公开可用
- **文字稿**：所有文字稿端点要求视频时长不超过2分钟
- **Reddit 子版块名称**：区分大小写！使用 "AskReddit" 而不是 "askreddit"

---

## 访问模式
### ScrapeCreators（社交媒体）

使用 Python 并使用 `core.http_client.proxied_get`，以便 sc-proxy 正确注入凭证并正确计费。包括一个类型的 `SC-CALLER-ID` 头（`chat:`, `job:`, `preview:`, 等）以跟踪成本。**不要从环境变量中读取 `$SCRAPECREATORS_API_KEY`，也不要要求用户提供密钥 — 代理会处理它。**

```python
from core.http_client import proxied_get

headers = {"SC-CALLER-ID": "chat:youtube-transcript"}

transcript = proxied_get(
    "https://api.scrapecreators.com/v1/youtube/video/transcript",
    params={"url": "https://www.youtube.com/watch?v=VIDEO_ID", "language": "en"},
    headers=headers,
    timeout=20,
).json()
```

Bash/curl 也行（代理是透明的），但 Python 更受推荐，因为可以跟踪成本：

```bash
curl -s "https://api.scrapecreators.com/v1/tiktok/profile?handle=charlidamelio" \
  -H "x-api-key: any"
```

每个端点都有其自己的 OpenAPI 规范，位于 `https://docs.scrapecreators.com/{path}/openapi.json`。**在发出实际 API 调用之前，始终首先获取每个端点的规范**以获取完整的参数详细信息。完整规范位于 `https://docs.scrapecreators.com/openapi.json`（大文件 — 建议使用每个端点的规范）。

常见可选参数：
- **`trim`**（布尔值）：减少响应有效负载大小。当您只需要关键指标时使用。
- **`region`**（字符串）：2字母国家代码，用于代理位置。**不按地区过滤 — 仅通过该国家的代理路由。**

### Firecrawl（通过透明代理的网页回退）

无需 Firecrawl API 密钥 — sc-proxy 会注入它。不要在 `.env` 中查找或要求用户提供。只需调用：

```python
from core.http_client import proxied_post

headers = {"SC-CALLER-ID": "chat:web-crawl-fallback"}

page = proxied_post(
    "https://api.firecrawl.dev/v2/scrape",
    json={
        "url": "https://example.com/article",
        "formats": ["markdown", "links"],
        "onlyMainContent": True,
        "timeout": 60000,
    },
    headers=headers,
).json()
```

## 决策规则
将每个请求路由到正确的后端。用户永远不需要指定要使用哪个 API。

### 社交媒体请求（个人资料、发布、评论、搜索、广告、热门、文字稿）
使用 **ScrapeCreators**。将用户的意图与上表中匹配的端点匹配。在调用之前，从用户名和话题标签中删除 `@` 和 `#`。首先获取每个端点的 OpenAPI 规范，以获取完整的参数详细信息。

### YouTube URL 或 YouTube 内容请求
使用 **ScrapeCreators** 进行 YouTube（频道信息、视频、短片、播放列表、评论、文字稿、搜索、热门短片）。将用户的意图与上表中匹配的 YouTube 端点匹配。

对于 YouTube URL，使用 `/v1/youtube/video` 获取视频详情和文字稿。如果用户的目标是内容分析、总结、引用提取或主题挖掘，则文字稿包含在视频响应中。

对于 YouTube 主题查询，使用 `/v1/youtube/search` 查找相关视频，然后仅对需要的视频调用 `/v1/youtube/video`。避免默认获取大量视频。

### 被屏蔽或 JS 重量级网页
使用一次 **Firecrawl**，并设置 `formats:["markdown","links"]` 和 `onlyMainContent:true`。将返回的 Markdown 视为提取的底层数据，而非最终真相：从页面结构中解析标题、价格/价值字段、规格、正文描述、图片 URL、外部链接以及明显的联系方式/位置线索。

通用网页提取要点：
- 许多列表/详情页面使用 JavaScript、图片画廊、隐藏区域或重复的 UI 标签渲染重要内容。`web_fetch` 可能返回模板内容，而 Firecrawl 仍能恢复实际主要内容。
- 不要硬编码特定网站的标签。将页面文本转换为通用结构化摘要：它是什么、在哪里、关键数字、证据片段、媒体/链接以及注意事项。
- 保留有助于验证页面的图片和链接的源 URL，但除非用户要求，否则不要下载或批量处理所有媒体资源。
- 如果 Markdown 遗漏重要布局或结构化字段，使用 `rawHtml` 重新尝试一次；仅在用户要求窄范围提取且模式/提示具体时，才使用 `json`、`question` 或 `highlights`。

## 成本控制
**ScrapeCreators** — 大多数端点每请求消耗 1 个信用点。例外：`/v1/tiktok/user/audience` 消耗 26 个信用点；`/v1/tiktok/video/transcript` 设置 `use_ai_as_fallback=true` 则额外消耗 +10 个信用点；`/v1/google/company/ads` 设置 `get_ad_details=true` 消耗 25 个信用点。在调用昂贵端点前提醒用户。

**Firecrawl** — 按页面计费，并可能因昂贵修饰项产生额外费用。

保持调用紧凑：一个页面、一个视频或一小份短清单。切勿使用此技能批量爬取整个网站或大量抓取整个数据源。

如果代理返回 403，请求超出允许的使用范围。应改变方法而非重试。

如果代理返回 429，应降低频率；不要在限制范围内并行化。

如果上游返回失败，报告确切失败原因，除非参数变更有明确理由，否则避免重复付费重试。
