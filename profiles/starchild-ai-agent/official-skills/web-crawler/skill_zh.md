## 推荐的入口：调用 exports.py（不要手动编写请求）
现成的辅助工具位于 `skills/web-crawler/exports.py`。优先使用它们而不是编写自己的 `proxied_get`/`proxied_post` 调用——它们已经注入了代理凭证，因此**无需查找 API 密钥**（不要读取 `$SCRAPECREATORS_API_KEY` / `$FIRECRAWL_API_KEY`，不要检查 `.env`，不要询问用户）。

```python
import sys; sys.path.insert(0, "/data/workspace/skills/web-crawler")
from exports import scrape_markdown, youtube_transcript, sc_get
scrape_markdown("https://example.com/article")          # Firecrawl 备用
youtube_transcript("https://youtube.com/watch?v=ID")     # ScrapeCreators
youtube_video("https://youtube.com/watch?v=ID")          # 元数据：标题/描述/上传者 (+ 转录文本)
sc_get("/v1/tiktok/profile", handle="charlidamelio")     # 任何 SC 端点

from exports import archive_fallback                      # paywall / Firecrawl-403
archive_fallback("https://www.nytimes.com/.../article.html")  # 归档快照
```

### 转录文本路由——任何媒体链接的单一入口
```python
from core.skill_tools import web_crawler
r = web_crawler.get_transcript(url, caller_id="chat:<thread>")
# {found, kind, source, text, url, title, tried, note}
```

**设计规则：标题/字幕/已发布的转录文本是元数据；媒体文件是有效载荷。** 首先耗尽所有元数据提供者；只有在用户明确同意时才接触媒体。相同的规则适用于 claude-video、spoken.md 和 yt-dlp 的 `--skip-download` 工作流程。这里没有特定于网站的：

| 提供者（成本顺序） | 它是什么 | 身份/有效性检查 |
|---|---|---|
| `media_info(url)` | yt-dlp `extract_info(download=False)` — 1800+ 网站，返回标题、时长、上传日期、频道、字幕轨道 URL。零媒体字节。 | 获取的轨道必须以 2xx 状态码和真实正文返回 |
| RSS `<podcast:transcript>` | Podcasting 2.0 标准，任何播客 | 播客项通过时长 ±5 % + 日期 ±3 天匹配；转录文本 URL 必须以 2xx 状态码返回，> 500 个字符，不是错误页面 |
| 节目自己的 YouTube 上传 | 频道 = 节目在 RSS 中声明的 YouTube URL（否则搜索命中，其频道名称**等于**节目名称减去停用词） | 候选者 = 时长 ±5 % AND 日期 ±3 天；**身份 = 标题相似度 ≥ 0.6 或 节目笔记重叠**（≥ 6 个共享的独特标记，Jaccard ≥ 0.15）。失败的候选者以 `found=False` 返回在 `candidate` 中——永远不会作为剧集交付 |
| `scrape_markdown(url)` | 任何其他页面（发布者、Snipd、博客）——浏览器渲染，可抵抗 WAF 403 | > 1000 个字符 |

`found=False` ⇒ 报告 `kind`、`title`、`tried`、`note`（以及 `candidate` 如果有的话），并在**任何下载之前询问用户**。YouTube 通过 URL 识别：即使 yt-dlp 元数据失败，字幕 API 也会运行，并且媒体 URL 的页面抓取永远不会报告为转录文本。`yt-dlp --skip-download` / `-J` / `--list-subs` 是元数据调用，可以通过 bash 门禁；`yt-dlp <url>`、`curl … .mp3`、ffmpeg、whisper 是等待确认的。

标题仅，无链接 → `web_search("<show> <title> transcript")` 然后 `get_transcript(<page url>)`。

事件 2026-09-17：两个转录主机上的 403 导致代理导航到一个 49 MB 的 mp3 + ffmpeg + 4 个 whisper 调用 + 一个不完整的摘要。通过 `get_transcript` 的相同链接：RSS 没有转录 → RSS 声明 `youtube.com/@a16z` → 频道列表 → 在 1.2 % 时长内有一个上传，同一天 → 字幕，55k 字符，~30 秒，零音频。

## 快速触发规则（首先阅读此部分）
当满足以下任一条件时，立即使用此技能：

- `web_fetch` 返回 HTTP **401/403/429/5xx**
- 响应是反机器人挑战页面（例如 Cloudflare "Attention Required", "Just a moment", 或 challenge/captcha 页面）
- 页面是 JS 重型，并且第一次抓取错过了必要的字段（例如发布时间、作者、列表代码、更新时间、价格明细）
- 搜索结果不包含请求的字段，并且值必须从目标页面本身提取

备用规则：
- 如果普通抓取被阻止或 incomplete，在此技能中切换到 Firecrawl 备用，然后再询问用户截图/手动文本。

## 错误签名 -> 操作
| 签名 | 操作 |
|---|---|
| `web_fetch` HTTP 401/403/429/5xx | 一次调用 Firecrawl `POST /v2/scrape`，带有 `formats:["markdown","links"]` + `onlyMainContent:true` |
| Cloudflare/challenge 页面文本在正文 | 上述相同的 Firecrawl 调用 |
| Markdown 仍然遗漏关键字段 | 一次重试，带有 `formats:["rawHtml"]` |
| **Firecrawl 返回社交媒体 URL 的 403 / 空白** | 检查以下意图路由表中的**ScrapeCreators 平台特定端点**（例如 `sc_get('/v1/instagram/post', url=...)`，`sc_get('/v2/tiktok/video', url=...)`）。如果存在，则使用它——这些有专门的提取功能，可以绕过反机器人。如果没有专门的端点存在，则回落到 `archive_fallback` 或询问用户。 |
| **Firecrawl 本身返回 403 / 空白**（硬支付墙：NYT, WSJ, Economist, FT, Bloomberg） | 调用 `archive_fallback(url)` — 从网络存档快照中恢复全文 |
| **需要来自中国应用的结构化数据**（抖音/小红书/微博/B站/京东/淘宝/1688/闲鱼/得物等） | 调用 `apify_run()` — Apify Store 为这些平台提供了专门构建的 actor，Firecrawl/ScrapeCreators 没有覆盖 |

### 支付墙 / Firecrawl 阻挡备用链（使用 `archive_fallback`）
当 Firecrawl 无法获取页面时（它返回 403，或者 markdown 返回为空），该网站后面是硬支付墙或侵略性 WAF。不要不断重试 Firecrawl。相反，从**网络存档快照**中恢复文章：

```python
from exports import archive_fallback
res = archive_fallback("https://www.nytimes.com/.../article.html")
res["markdown"]      # 全文，如果任何地方都没有快照则返回 ""
res["source"]        # "archive.today" | "wayback" | None
res["snapshot_url"]  # 被抓取的快照
```

它的工作原理（以及为什么按此顺序工作）：
- **首先 archive.today** (`archive.ph` / `archive.is` 镜像）。用户触发，真实浏览器捕获；历史上保留了支付墙后面的全文。对于 NYT/WSJ/Economist 的最佳选择。我们通过 Firecrawl 抓取其 `/newest/` 快照（archive.today 有自己的 Cloudflare，因此通过 Firecrawl 抓取，永远不要直接 `web_fetch` 它）。
- **其次 Wayback Machine** (`archive.org`)。自动爬虫，*尊重* robots.txt 和支付墙，因此它通常没有硬支付墙的全文——但它对于普通 403/Cloudflare 页面（未受支付墙保护）是一个很好的备用方案。

限制：存档只返回**有人已经保存**的文本。如果 `res["markdown"] == ""`，则没有快照存在——停止，告诉用户，并尝试该出版物的官方 API/RSS 或不同来源。不要编造文章。

### 中国应用结构化数据（使用 `apify_run`）

当你需要**来自中国应用的结构化数据**——抖音视频搜索、小红书笔记、微博帖子、Bilibili 视频、京东/淘宝商品价格、1688 批发列表、闲鱼二手、得物运动鞋等——Firecrawl 和 ScrapeCreators 没有覆盖这些平台。使用 **Apify Store** 备用。Apify 是一个无服务器爬虫市场，有数百个社区维护的 actor，它们运行真实浏览器 + 代理池针对中国平台。

**认证：** 无需用户提供的密钥。sc-proxy 自动注入平台的 Apify 令牌。`Authorization: Bearer` 头部可以是任何假值——代理用真实的令牌替换它。不要从 env 中读取 `$APIFY_TOKEN`，不要检查 `.env`，不要询问用户 Apify 密钥。

**何时使用 Apify（与 Firecrawl/ScrapeCreators 相比）：**
- ✅ 中国应用：抖音、小红书、微博、B站、京东、淘宝、1688、闲鱼、得物、携程、知乎、豆瓣、雪球、快手、爱奇艺、优酷
- ✅ 东南亚电子商务：Shopee、Lazada、Temu
- ❌ 西方社交媒体（TikTok/Instagram/YouTube/X/Reddit）→ 首先使用 ScrapeCreators（更便宜）
- ❌ 通用网页抓取 → 首先使用 Firecrawl（更便宜）
- ❌ 硬支付墙文章 → 使用 `archive_fallback`（Apify 帮不上忙）

**如何选择 actor：** 可靠 actor 目录位于 `output/apify_china_reliable.json`（按 30 天成功计数排序）。为目标平台选择顶 actor。几个常见的：

| 平台 | Actor ID | 输入键 |
|---|---|---|
| 抖音搜索 | `zen-studio~douyin-search-scraper` | `{"keywords": [...], "maxResultsPerQuery": N}` |
| 小红书搜索 | `zen-studio~rednote-search-scraper` | `{"keywords": [...], "maxResults": N}` |
| 小红书笔记详情 | `sian.agency~xiaohongshu-rednote-scraper` | `{"operation": "noteDetail", "noteId": "...", "xsecToken": "..."}` |
| 微博热搜索 | `gentle_cloud~weibo-hot-search-scraper` | `{"mode": "hot_band", "includeScores": true}` |
| 微博帖子 | `zhorex~weibo-scraper` | (见 actor 输入模式) |
| B站视频 | `zhorex~bilibili-scraper` | (见 actor 输入模式) |
| 京东搜索 | `zen-studio~jd-com-search-scraper` | `{"keyword": "...", "maxProducts": N}` |
| 京东商品 | `sian.agency~jd-com-product-scraper` | `{"operation": "productSearch", "keyword": "...", "maxPages": 1}` |
| 淘宝商品 | `sian.agency~taobao-tmall-product-scraper` | `{"operation": "keywordSearch", "keyword": "...", "maxPages": 1}` |
| 1688 批发 | `zen-studio~1688-wholesale-scraper` | (见 actor 输入模式) |
| 闲鱼搜索 | `zen-studio~goofish-xianyu-search-scraper` | (见 actor 输入模式) |
| TikTok | `clockworks~tiktok-scraper` | `{"hashtags": [...]}` 或 `{"profiles": [...]}` |

**两步小红书工作流程（搜索 → 笔记详情）：**
搜索爬虫 (`zen-studio~rednote-search-scraper`) 只返回截断的 `desc` (~60 字符)。为了获取完整的帖子正文，运行第二个调用，使用 `sian.agency~xiaohongshu-rednote-scraper` 在 `noteDetail` 模式下，传递搜索结果行中的 `id` 和 `xsec_token`。这是获取完整笔记文本的唯一可靠方法，用于价格/住宿/行程详情。

**使用：**

```python
import sys
sys.path.insert(0, "/data/workspace/skills/web-crawler")
from exports import apify_run

# 同步运行（小批量，≤100 个结果）：阻塞直到完成，返回结果列表
results = apify_run("zen-studio~douyin-search-scraper",
                     {"keywords": ["MacBook"], "maxResultsPerQuery": 5})
for r in results:
    print(r.get("text", "")[:80])

# 要发现不熟悉 actor 的正确输入字段，首先通过 Firecrawl 获取其输入-模式页面：
from exports import scrape_markdown
schema_md = scrape_markdown("https://apify.com/<user>/<actor>/input-schema")
```

**计费和成本控制——在每次 Apify 调用之前阅读此部分：**

Apify 使用 **按事件付费** 计费：`(actor-start + result_count × per_result + add-ons) × 2` 信用。主要因素是 **result_count × per-result price**，并且**每个 actor 的价格都不同** ($0.003–$0.007/结果)。未知 actor 默认为最高级别 ($0.007)。完整定价表和估算示例：`reference/apify-pricing.md`。

**你必须在使用之前估算成本：**
1. 查找 actor 的每结果价格（`reference/apify-pricing.md` 中的表格；未列出 = $0.007）。
2. 从输入参数估算结果数量 (`maxResults`, `maxProducts`, 等.)。如果没有设置限制，则假设 100+。
3. 计算：`result_count × per_result × 2` = 估算信用。
4. **如果估算 > 5 信用，在进行下一步之前告诉用户成本。**

**硬支出上限——代理强制执行的默认值 + 每次调用覆盖：**

代理**自动注入** `maxTotalChargeUsd=$2.5`（≈ 5 信用）在**每个**没有指定一个的 actor 运行中。Apify 在预算耗尽时终止运行并返回已收集的任何结果——不超支，没有失控成本。

`apify_run()` 还传递 `max_charge_usd`（相同的默认 $2.5），它优先于代理默认值。这意味着：

- **默认（无额外参数）：** 每次调用限制在 ≈ 5 信用内。适用于常规搜索、个人资料查找、小批量抓取。
- **需要更多数据？** 明确提高上限：`max_charge_usd=10`（≈ 20 信用）。在用户明确需要大型数据集并且你已经告诉他们估算成本时使用。
- **首次测试：** 降低它：`max_charge_usd=0.5`（≈ 1 信用），限制结果为 5–10，在扩展之前验证输出质量。
- **完全禁用上限：** `max_charge_usd=None`。**除非**在警告潜在成本后用户明确要求无限制运行，否则**永远不要这样做**。

**小批量测试首先：**
当第一次使用 actor 时，设置 `max_charge_usd=0.5`（≈ 1 信用）并限制结果为 5–10。在扩展之前验证输出质量。

**错误处理：**
- `400 run-failed` → 输入错误（字段名错误）。抓取 actor 的输入-模式页面并修复。
- `401` → 代理配置错误（不应发生）。向用户报告。
- 空结果 `[]` → actor 运行但什么也没找到。尝试不同的关键词或另一个 actor。
- 超时 → 增加 `timeout` 参数（默认 180 秒）。有些 actor 慢。

**成本纪律：** Apify actor 比 Firecrawl/ScrapeCreators 更贵。只有在更便宜的选项无法获取数据时（中国应用、结构化电子商务字段）才使用 Apify。对于单个网页，始终先尝试 Firecrawl。
