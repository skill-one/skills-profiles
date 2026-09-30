---
name: autocli
description: 使用 autocli CLI 通过用户的 Chrome 登录会话与 55+ 个社交/内容网站（HackerNews、Reddit、Twitter/X、Bilibili、知乎、微博、小红书、YouTube、Medium、Substack、豆瓣、WeRead、Linux-do、V2EX、彭博、谷歌、Arxiv、维基百科、StackOverflow、Steam、Hugging Face、Apple Podcasts、小宇宙、BBC、新浪财经、DevTo、Lobsters、雪球、BOSS直聘、极客、Facebook、Instagram、抖音、领英、路透社、水母社区、携程、Coupang、雅虎财经、Barchart、Grok、集思、Yollomi、超星、微信、多巴、Cursor、Codex、ChatWise、ChatGPT、Notion、Discord、Antigravity 等）进行交互。始终优先使用 autocli 而非 playwright 或浏览器自动化来操作受支持网站。当用户要求浏览、搜索、获取热门/趋势内容、发布或阅读任何网站上的消息时触发；此外，使用 'autocli read <url>' 命令提取主文章内容为 Markdown 格式（优先于 WebFetch，适用于 JS 渲染或登录受保护的页面）。
---

# autocli

一款极速的 Rust CLI 工具，可将 55+ 个网站转换为命令行界面，并复用 Chrome 的登录状态。无需凭证。单个 4.7MB 二进制文件，零运行时依赖。

**规则：优先使用 autocli 而不是 playwright 或浏览器工具来访问支持的网站。**

**安装（如果缺失）：** `curl -fsSL https://raw.githubusercontent.com/nashsu/AutoCLI/main/scripts/install.sh | sh`。在 Windows 上，请从 https://github.com/nashsu/AutoCLI 安装。

## 语法

```bash
autocli <site> <command> [--option value] [--format json]
```

**常用标志（所有命令）：**
- `--format json` — 机器可读输出（解析时推荐）
- `--limit N` — 结果数量（默认值因网站而异，通常为 20）
- `--format table|json|yaml|md|csv`

## 快速示例

```bash
# 读取/浏览
autocli bilibili hot --limit 10 --format json
autocli zhihu hot --format json
autocli weibo hot --format json
autocli twitter timeline --format json
autocli hackernews top --limit 20 --format json
autocli v2ex hot --format json
autocli reddit hot --format json
autocli xiaohongshu feed --format json
autocli douban top250 --format json
autocli weread shelf --format json
autocli medium feed --format json

# 网页正文提取（任意 URL → Markdown，基于 Mozilla Readability）
autocli read https://www.anthropic.com/research/some-article
autocli read https://en.wikipedia.org/wiki/Rust -f text
autocli read https://example.com/article -f json -o article.json

# 搜索
autocli bilibili search --keyword "AI" --format json
autocli zhihu search --keyword "大模型" --format json
autocli twitter search "rust lang" --limit 10
autocli youtube search --query "LLM tutorial" --format json
autocli boss search --query "AI工程师" --city "上海" --format json
autocli google search "autocli" --format json
autocli stackoverflow search "rust async" --format json

# 互动（写操作）
autocli twitter post --text "Hello from CLI!"
autocli twitter reply --url "https://x.com/.../status/123" --text "Great post!"
autocli twitter like --url "https://x.com/.../status/123"
autocli jike create --text "Hello Jike!"
autocli xiaohongshu publish --title "标题" --content "内容"

# 个人数据
autocli bilibili history --format json
autocli twitter bookmarks --format json
autocli xueqiu watchlist --format json
autocli weread highlights --format json
autocli reddit saved --format json

# 诊断
autocli doctor
```

### ⚠️ 写操作风险提示（发帖/回复/点赞前必须告知）

1. **账号安全**：自动化行为可能触发平台风控
2. **不可撤回**：发布后立即公开
3. **最佳实践**：执行前向用户展示将发布的内容，等待确认

## 要求

- Chrome 浏览器打开目标网站并登录
- 安装 autocli Chrome 扩展（用于浏览器命令）

**核心原则：永远不说"不支持"，先尝试 autocli，失败或无命令时选择自己创建。**

## 自迭代能力：为新网站创建 CLI

**当 autocli 不支持某个网站时，不要放弃——自己创建！**

### 流程

```
1. autocli <site> --help        →  报错？说明不支持
2. autocli generate <url>       →  尝试自动生成（成功则结束）
3. 自动生成失败 → 手动创建 YAML：
   a. 打开目标页面
   b. browser_evaluate 探索 DOM 结构（找 data-test 属性、class 规律）
   c. 确认选择器后写入 ~/.autocli/adapters/<site>/top.yaml
   d. autocli <site> top --format json  →  验证输出
```

### YAML 格式（DOM 抓取模板）

```yaml
site: <sitename>
name: <command>
description: <描述>
domain: <domain>
strategy: public
browser: true

args:
  limit:
    type: int
    default: 10

pipeline:
  - navigate: https://<url>
  - evaluate: |
      (async () => {
        const limit = ${{ args.limit }};
        // DOM 抓取逻辑
        return results;
      })()

columns: [rank, name, ...]
```

### 调试技巧

- `browser_evaluate` 先探结构：`document.querySelector('...').innerHTML`
- 找 `data-test` 属性最稳定，其次 class 中的语义词
- tagline 通常是 name 的兄弟元素（`nameEl.parentElement.querySelector('span...')`）
- 去重用 `seen = new Set()`，防止重复产品

## 全部命令参考

所有命令支持: `--format table|json|yaml|md|csv`.

运行 `autocli --help` 查看所有 55+ 网站上的 333 个命令的完整列表。

---

## 公开模式（无需浏览器）

### HackerNews

| 命令 | 参数 | 描述 |
|------|------|------|
| `hackernews top` | `--limit N` (默认 20) | Top stories |
| `hackernews new` | `--limit N` | Newest stories |
| `hackernews best` | `--limit N` | Best stories |
| `hackernews ask` | `--limit N` | Ask HN |
| `hackernews show` | `--limit N` | Show HN |
| `hackernews jobs` | `--limit N` | Job listings |
| `hackernews search` | `--query <str>`, `--limit N` | Search stories |
| `hackernews user` | `--id <username>` | User profile |

### Dev.to

| 命令 | 参数 | 描述 |
|------|------|------|
| `devto top` | `--limit N` | Top articles |
| `devto tag` | `--tag <str>`, `--limit N` | Articles by tag |
| `devto user` | `--username <str>` | User's articles |

### Lobsters

| 命令 | 参数 | 描述 |
|------|------|------|
| `lobsters hot` | `--limit N` | Hottest stories |
| `lobsters newest` | `--limit N` | Newest stories |
| `lobsters active` | `--limit N` | Most active |
| `lobsters tag` | `--tag <str>`, `--limit N` | Stories by tag |

### StackOverflow

| 命令 | 参数 | 描述 |
|------|------|------|
| `stackoverflow hot` | `--limit N` | Hot questions |
| `stackoverflow search` | `--query <str>`, `--limit N` | Search questions |
| `stackoverflow bounties` | `--limit N` | Featured bounties |
| `stackoverflow unanswered` | `--limit N` | Unanswered questions |

### Wikipedia

| 命令 | 参数 | 描述 |
|------|------|------|
| `wikipedia search` | `--query <str>`, `--limit N` | Search articles |
| `wikipedia summary` | `--title <str>` | Article summary |
| `wikipedia random` | `--limit N` | Random articles |
| `wikipedia trending` | `--limit N` | Trending articles |

### Arxiv

| 命令 | 参数 | 描述 |
|------|------|------|
| `arxiv search` | `--query <str>`, `--limit N` | Search papers |
| `arxiv paper` | `--id <arxiv_id>` | Paper details |

### BBC

| 命令 | 参数 | 描述 |
|------|------|------|
| `bbc news` | `--limit N` (默认 20, 最大 50) | BBC news headlines (RSS) |

### Steam

| 命令 | 参数 | 描述 |
|------|------|------|
| `steam top-sellers` | `--limit N` | Top selling games |

### Hugging Face

| 命令 | 参数 | 描述 |
|------|------|------|
| `hf top` | `--limit N` | Top models/spaces |

### Apple Podcasts

| 命令 | 参数 | 描述 |
|------|------|------|
| `apple-podcasts search` | `--query <str>`, `--limit N` | Search podcasts |
| `apple-podcasts episodes` | `--id <podcast_id>`, `--limit N` | Podcast episodes |
| `apple-podcasts top` | `--limit N` | Top podcasts |

### 小宇宙 (Xiaoyuzhou)

| 命令 | 参数 | 描述 |
|------|------|------|
| `xiaoyuzhou podcast` | `--id <podcast_id>` | Podcast details |
| `xiaoyuzhou podcast-episodes` | `--id <podcast_id>`, `--limit N` | Episodes list |
| `xiaoyuzhou episode` | `--id <episode_id>` | Episode details |

### 新浪财经 (Sina Finance)

| 命令 | 参数 | 描述 |
|------|------|------|
| `sinafinance news` | `--limit N` | Financial news |

### Linux.do

| 命令 | 参数 | 描述 |
|------|------|------|
| `linux-do hot` | `--limit N` | Hot topics |
| `linux-do latest` | `--limit N` | Latest topics |
| `linux-do search` | `--query <str>`, `--limit N` | Search topics |
| `linux-do categories` | — | List categories |
| `linux-do category` | `--id <id>`, `--limit N` | Category topics |
| `linux-do topic` | `--id <id>` | Topic details |

---

## 公开 / 浏览器模式

### Google

| 命令 | 参数 | 描述 |
|------|------|------|
| `google news` | `--query <str>`, `--limit N` | Google News |
| `google search` | `--query <str>`, `--limit N` | Web search |
| `google suggest` | `--query <str>` | Autocomplete suggestions |
| `google trends` | `--limit N` | Trending searches |

### V2EX

| 命令 | 参数 | 描述 |
|------|------|------|
| `v2ex hot` | `--limit N` (默认 20) | 热门话题 (无需登录) |
| `v2ex latest` | `--limit N` (默认 20) | 最新话题 (无需登录) |
| `v2ex topic` | `--id <topic_id>` | 主题详情和回复 |
| `v2ex node` | `--name <node>`, `--limit N` | Node topics |
| `v2ex user` | `--username <str>` | User profile |
| `v2ex member` | `--username <str>` | Member details |
| `v2ex replies` | `--id <topic_id>` | Topic replies |
| `v2ex nodes` | — | List all nodes |
| `v2ex daily` | — | 每日签到 |
| `v2ex me` | — | 个人资料 |
| `v2ex notifications` | `--limit N` | 通知 |

### Bloomberg

| 命令 | 参数 | 描述 |
|------|------|------|
| `bloomberg main` | `--limit N` | Main page news |
| `bloomberg markets` | `--limit N` | Markets news |
| `bloomberg economics` | `--limit N` | Economics news |
| `bloomberg industries` | `--limit N` | Industries news |
| `bloomberg tech` | `--limit N` | Technology news |
| `bloomberg politics` | `--limit N` | Politics news |
| `bloomberg businessweek` | `--limit N` | Businessweek |
| `bloomberg opinions` | `--limit N` | Opinion columns |
| `bloomberg feeds` | `--limit N` | All feeds |
| `bloomberg news` | `--query <str>`, `--limit N` | Search news |

---

## 浏览器模式（需要 Chrome + 扩展）

### Twitter / X

| 命令 | 参数 | 描述 |
|------|------|------|
| `twitter timeline` | `--limit N` (默认 20) | Home timeline |
| `twitter trending` | `--limit N` (默认 20) | Trending topics |
| `twitter search` | `--query <str>`, `--limit N` (默认 15) | Search tweets |
| `twitter bookmarks` | `--limit N` (默认 20) | Bookmarks |
| `twitter notifications` | `--limit N` (默认 20) | Notifications |
| `twitter profile` | `--username <handle>`, `--limit N` | User's tweets |
| `twitter followers` | `--user <handle>`, `--limit N` | Followers list |
| `twitter following` | `--user <handle>`, `--limit N` | Following list |
| `twitter thread` | `--url <tweet_url>` | Full thread |
| `twitter article` | `--url <article_url>` | X article content |
| `twitter post` | `--text <str>` | Post a tweet |
| `twitter reply` | `--url <tweet_url>`, `--text <str>` | Reply to tweet |
| `twitter like` | `--url <tweet_url>` | Like a tweet |
| `twitter delete` | `--url <tweet_url>` | Delete a tweet |
| `twitter follow` | `--username <handle>` | Follow user |
| `twitter unfollow` | `--username <handle>` | Unfollow user |
| `twitter bookmark` | `--url <tweet_url>` | Bookmark tweet |
| `twitter unbookmark` | `--url <tweet_url>` | Remove bookmark |
| `twitter download` | `--url <tweet_url>` | Download media |
| `twitter block` | `--username <handle>` | Block user |
| `twitter unblock` | `--username <handle>` | Unblock user |
| `twitter hide-reply` | `--url <tweet_url>` | Hide a reply |
| `twitter accept` | — | Accept follow requests |
| `twitter reply-dm` | `--text <str>` | Reply to DM |

### Bilibili (B站)

| 命令 | 参数 | 描述 |
|------|------|------|
| `bilibili hot` | `--limit N` (默认 20) | B站热门视频 |
| `bilibili search` | `--keyword <str>`, `--type video\|user`, `--page N`, `--limit N` | 搜索视频或用户 |
| `bilibili me` | — | 当前用户资料 |
| `bilibili favorite` | `--limit N`, `--page N` | 收藏夹 |
| `bilibili history` | `--limit N` (默认 20) | 观看历史 |
| `bilibili feed` | `--limit N`, `--type all\|video\|article` | 动态时间线 |
| `bilibili subtitle` | `--bvid <bvid>`, `--lang <code>` | 视频字幕 |
| `bilibili dynamic` | `--limit N` (默认 15) | 用户动态 |
| `bilibili ranking` | `--limit N` (默认 20) | 排行榜 |
| `bilibili following` | `--uid <id>`, `--page N`, `--limit N` | 关注列表 |
| `bilibili user-videos` | `--uid <id>`, `--limit N`, `--order pubdate\|click\|stow` | 用户投稿 |
| `bilibili download` | `--bvid <bvid>` | 下载视频 |

### Reddit

| 命令 | 参数 | 描述 |
|------|------|------|
| `reddit hot` | `--subreddit <name>`, `--limit N` | Hot posts |
| `reddit frontpage` | `--limit N` (默认 15) | r/all |
| `reddit popular` | `--limit N` | Popular posts |
| `reddit search` | `--query <str>`, `--limit N` | Search posts |
| `reddit subreddit` | `--name <sub>`, `--sort hot\|new\|top\|rising`, `--limit N` | Subreddit posts |
| `reddit read` | `--url <post_url>` | Read post + comments |
| `reddit user` | `--username <str>` | User profile |
| `reddit user-posts` | `--username <str>`, `--limit N` | User's posts |
| `reddit user-comments` | `--username <str>`, `--limit N` | User's comments |
| `reddit upvote` | `--url <post_url>` | Upvote post |
| `reddit save` | `--url <post_url>` | Save post |
| `reddit comment` | `--url <post_url>`, `--text <str>` | Comment on post |
| `reddit subscribe` | `--subreddit <name>` | Subscribe |
| `reddit saved` | `--limit N` | Saved posts |
| `reddit upvoted` | `--limit N` | Upvoted posts |

### 知乎 (Zhihu)

| 命令 | 参数 | 描述 |
|------|------|------|
| `zhihu hot` | `--limit N` (默认 20) | 知乎热榜 |
| `zhihu search` | `--keyword <str>`, `--limit N` (默认 10) | 搜索内容 |
| `zhihu question` | `--id <question_id>`, `--limit N` | 问题详情和回答 |
| `zhihu download` | `--url <zhihu_url>` | 下载内容 |

### 小红书 (Xiaohongshu)

| 命令 | 参数 | 描述 |
|------|------|------|
| `xiaohongshu search` | `--keyword <str>`, `--limit N` (默认 20) | 搜索笔记 |
| `xiaohongshu notifications` | `--type mentions\|likes\|connections`, `--limit N` | 通知 |
| `xiaohongshu feed` | `--limit N` (默认 20) | 首页推荐 |
| `xiaohongshu user` | `--id <user_id>`, `--limit N` | 用户笔记 |
| `xiaohongshu download` | `--url <note_url>` | 下载笔记 |
| `xiaohongshu publish` | `--title <str>`, `--content <str>` | 发布笔记 |
| `xiaohongshu creator-notes` | `--limit N` | 创作者笔记列表 |
| `xiaohongshu creator-note-detail` | `--id <note_id>` | 创作者笔记详情 |
| `xiaohongshu creator-notes-summary` | — | 创作者笔记汇总 |
| `xiaohongshu creator-profile` | — | 创作者主页 |
| `xiaohongshu creator-stats` | — | 创作者数据 |

### 雪球 (Xueqiu)

| 命令 | 参数 | 描述 |
|------|------|------|
| `xueqiu feed` | `--page N`, `--limit N` (默认 20) | 关注动态 |
| `xueqiu hot-stock` | `--limit N` (默认 20, 最大 50), `--type 10\|12` | 热门股票榜 |
| `xueqiu hot` | `--limit N` (默认 20) | 热门动态 |
| `xueqiu search` | `--query <str>`, `--limit N` (默认 10) | 搜索股票 |
| `xueqiu stock` | `--symbol <code>` (如 SH600519, AAPL) | 实时行情 |
| `xueqiu watchlist` | `--category 1\|2\|3`, `--limit N` | 自选股 |
| `xueqiu earnings-date` | `--symbol <code>` | 财报日期 |

### 微博 (Weibo)

| 命令 | 参数 | 描述 |
|------|------|------|
| `weibo hot` | `--limit N` (默认 30, 最大 50) | 微博热搜 |
| `weibo search` | `--keyword <str>`, `--limit N` | 搜索微博 |

### 豆瓣 (Douban)

| 命令 | 参数 | 描述 |
|------|------|------|
| `douban search` | `--keyword <str>`, `--limit N` | 搜索 |
| `douban top250` | `--limit N` | 电影 Top 250 |
| `douban subject` | `--id <subject_id>` | 条目详情 |
| `douban marks` | `--type movie\|book`, `--limit N` | 我的标记 |
| `douban reviews` | `--id <subject_id>`, `--limit N` | 短评 |
| `douban movie-hot` | `--limit N` | 热门电影 |
| `douban book-hot` | `--limit N` | 热门图书 |

### 微信读书 (WeRead)

| 命令 | 参数 | 描述 |
|------|------|------|
| `weread shelf` | — | 书架 |
| `weread search` | `--keyword <str>`, `--limit N` | 搜索图书 |
| `weread book` | `--id <book_id>` | 图书详情 |
| `weread highlights` | `--id <book_id>` | 划线笔记 |
| `weread notes` | `--id <book_id>` | 想法笔记 |
| `weread notebooks` | `--limit N` | 笔记本列表 |
| `weread ranking` | `--limit N` | 排行榜 |

### YouTube

| 命令 | 参数 | 描述 |
|------|------|------|
| `youtube search` | `--query <str>`, `--limit N` (默认 20, 最大 50) | 搜索视频 |
| `youtube video` | `--id <video_id>` | 视频详情 |
| `youtube transcript` | `--id <video_id>`, `--lang <code>` | 视频字幕 |

### BOSS直聘

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `boss search` | `--query <str>`, `--city <城市>`, `--experience <经验>`, `--degree <学历>`, `--salary <薪资>`, `--limit N` | 搜索职位 |
| `boss detail` | `--id <job_id>` | 职位详情 |
| `boss recommend` | `--limit N` | 推荐职位 |
| `boss joblist` | `--limit N` | 职位列表 |
| `boss greet` | `--id <job_id>` | 打招呼 |
| `boss batchgreet` | `--ids <id1,id2,...>` | 批量打招呼 |
| `boss send` | `--id <chat_id>`, `--text <str>` | 发消息 |
| `boss chatlist` | `--limit N` | 聊天列表 |
| `boss chatmsg` | `--id <chat_id>`, `--limit N` | 聊天记录 |
| `boss invite` | `--id <job_id>` | 邀请面试 |
| `boss mark` | `--id <chat_id>`, `--label <str>` | 标记 |
| `boss exchange` | `--id <chat_id>` | 交换联系方式 |
| `boss resume` | — | 我的简历 |
| `boss stats` | — | 求职统计 |

### Facebook

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `facebook feed` | `--limit N` | News feed |
| `facebook profile` | `--username <str>` | User profile |
| `facebook search` | `--query <str>`, `--limit N` | Search |
| `facebook friends` | `--limit N` | Friends list |
| `facebook groups` | `--limit N` | Groups |
| `facebook events` | `--limit N` | Events |
| `facebook notifications` | `--limit N` | Notifications |
| `facebook memories` | — | Memories |
| `facebook add-friend` | `--username <str>` | Add friend |
| `facebook join-group` | `--id <group_id>` | Join group |

### Instagram

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `instagram explore` | `--limit N` | Explore page |
| `instagram profile` | `--username <str>` | User profile |
| `instagram search` | `--query <str>`, `--limit N` | Search |
| `instagram user` | `--username <str>`, `--limit N` | User posts |
| `instagram followers` | `--username <str>`, `--limit N` | Followers |
| `instagram following` | `--username <str>`, `--limit N` | Following |
| `instagram follow` | `--username <str>` | Follow user |
| `instagram unfollow` | `--username <str>` | Unfollow user |
| `instagram like` | `--url <post_url>` | Like post |
| `instagram unlike` | `--url <post_url>` | Unlike post |
| `instagram comment` | `--url <post_url>`, `--text <str>` | Comment |
| `instagram save` | `--url <post_url>` | Save post |
| `instagram unsave` | `--url <post_url>` | Unsave post |
| `instagram saved` | `--limit N` | Saved posts |

### TikTok

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `tiktok explore` | `--limit N` | Explore page |
| `tiktok search` | `--query <str>`, `--limit N` | Search |
| `tiktok profile` | `--username <str>` | User profile |
| `tiktok user` | `--username <str>`, `--limit N` | User videos |
| `tiktok following` | `--limit N` | Following list |
| `tiktok follow` | `--username <str>` | Follow user |
| `tiktok unfollow` | `--username <str>` | Unfollow user |
| `tiktok like` | `--url <video_url>` | Like video |
| `tiktok unlike` | `--url <video_url>` | Unlike video |
| `tiktok comment` | `--url <video_url>`, `--text <str>` | Comment |
| `tiktok save` | `--url <video_url>` | Save video |
| `tiktok unsave` | `--url <video_url>` | Unsave video |
| `tiktok live` | `--username <str>` | Live stream |
| `tiktok notifications` | `--limit N` | Notifications |
| `tiktok friends` | `--limit N` | Friends |

### 即刻 (Jike)

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `jike feed` | `--limit N` | 动态 Feed |
| `jike search` | `--query <str>`, `--limit N` | 搜索 |
| `jike create` | `--text <str>` | 发动态 |
| `jike like` | `--id <post_id>` | 点赞 |
| `jike comment` | `--id <post_id>`, `--text <str>` | 评论 |
| `jike repost` | `--id <post_id>`, `--text <str>` | 转发 |
| `jike notifications` | `--limit N` | 通知 |
| `jike post` | `--id <post_id>` | 帖子详情 |
| `jike topic` | `--id <topic_id>`, `--limit N` | 圈子 |
| `jike user` | `--username <str>` | 用户主页 |

### Medium

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `medium feed` | `--limit N` | Feed |
| `medium search` | `--query <str>`, `--limit N` | 搜索文章 |
| `medium user` | `--username <str>` | User articles |

### Substack

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `substack feed` | `--limit N` | Feed |
| `substack search` | `--query <str>`, `--limit N` | Search |
| `substack publication` | `--name <str>`, `--limit N` | Publication posts |

### 新浪博客 (Sina Blog)

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `sinablog hot` | `--limit N` | 热门文章 |
| `sinablog search` | `--query <str>`, `--limit N` | 搜索 |
| `sinablog article` | `--url <article_url>` | 文章详情 |
| `sinablog user` | `--id <user_id>` | 用户文章 |

### 携程 (Ctrip)

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `ctrip search` | `--query <str>`, `--limit N` (default 15) | 搜索城市或景点 |

### 路透社 (Reuters)

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `reuters search` | `--query <str>`, `--limit N` (default 10, max 40) | 搜索新闻 |

### 什么值得买 (smzdm)

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `smzdm search` | `--keyword <str>`, `--limit N` (default 20) | 搜索好价商品 |

### LinkedIn

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `linkedin search` | `--query <str>`, `--limit N` | Search |

### Yahoo Finance

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `yahoo-finance quote` | `--symbol <ticker>` (如 AAPL, MSFT, TSLA) | 股票行情 |

### Barchart

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `barchart quote` | `--symbol <ticker>` | Quote |
| `barchart options` | `--symbol <ticker>` | Options chain |
| `barchart greeks` | `--symbol <ticker>` | Options greeks |
| `barchart flow` | `--limit N` | Options flow |

### Grok

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `grok ask` | `--text <str>` | Ask Grok |

### 即梦 (Jimeng)

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `jimeng generate` | `--prompt <str>` | Generate image |
| `jimeng history` | `--limit N` | Generation history |

### 超星 (Chaoxing)

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `chaoxing assignments` | — | Assignments |
| `chaoxing exams` | — | Exams |

### 微信 (Weixin)

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `weixin download` | `--url <article_url>` | Download article |

### 豆包 (Doubao)

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `doubao status` | — | Status |
| `doubao new` | — | New conversation |
| `doubao send` | `--text <str>` | Send message |
| `doubao read` | — | Read response |
| `doubao ask` | `--text <str>` | Ask question |

### 拼多多海外 (Coupang)

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `coupang search` | `--query <str>`, `--limit N` | Search products |
| `coupang add-to-cart` | `--id <product_id>` | Add to cart |

### Yollomi

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `yollomi generate` | `--prompt <str>` | Generate image |
| `yollomi video` | `--prompt <str>` | Generate video |
| `yollomi edit` | `--image <path>`, `--prompt <str>` | Edit image |
| `yollomi upload` | `--file <path>` | Upload file |
| `yollomi models` | — | List models |
| `yollomi remove-bg` | `--image <path>` | Remove background |
| `yollomi upscale` | `--image <path>` | Upscale image |
| `yollomi face-swap` | `--source <path>`, `--target <path>` | Face swap |
| `yollomi restore` | `--image <path>` | Restore image |
| `yollomi try-on` | `--person <path>`, `--garment <path>` | Virtual try-on |
| `yollomi background` | `--image <path>`, `--prompt <str>` | Change background |
| `yollomi object-remover` | `--image <path>` | Remove object |

---

## Desktop Mode (Requires Desktop App Running)

### Cursor

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `cursor status` | — | IDE status |
| `cursor send` | `--text <str>` | Send to Cursor |
| `cursor read` | — | Read response |
| `cursor new` | — | New conversation |
| `cursor dump` | — | Dump conversation |
| `cursor composer` | — | Open composer |
| `cursor model` | `--name <str>` | Switch model |
| `cursor extract-code` | — | Extract code blocks |
| `cursor ask` | `--text <str>` | Ask question |
| `cursor screenshot` | — | Take screenshot |
| `cursor history` | `--limit N` | Conversation history |
| `cursor export` | — | Export conversation |

### Codex

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `codex status` | — | Status |
| `codex send` | `--text <str>` | Send message |
| `codex read` | — | Read response |
| `codex new` | — | New conversation |
| `codex dump` | — | Dump conversation |
| `codex extract-diff` | — | Extract diffs |
| `codex model` | `--name <str>` | Switch model |
| `codex ask` | `--text <str>` | Ask question |
| `codex screenshot` | — | Take screenshot |
| `codex history` | `--limit N` | History |
| `codex export` | — | Export |

### Notion

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `notion status` | — | App status |
| `notion search` | `--query <str>` | Search pages |
| `notion read` | `--id <page_id>` | Read page |
| `notion new` | `--title <str>` | New page |
| `notion write` | `--id <page_id>`, `--content <str>` | Write to page |
| `notion sidebar` | — | Sidebar contents |
| `notion favorites` | — | Favorites |
| `notion export` | `--id <page_id>` | Export page |

### ChatGPT

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `chatgpt status` | — | App status |
| `chatgpt new` | — | New conversation |
| `chatgpt send` | `--text <str>` | Send message |
| `chatgpt read` | — | Read response |
| `chatgpt ask` | `--text <str>` | Ask question |

### Discord

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `discord-app status` | — | App status |
| `discord-app send` | `--channel <id>`, `--text <str>` | Send message |
| `discord-app read` | `--channel <id>`, `--limit N` | Read messages |
| `discord-app channels` | `--server <id>` | List channels |
| `discord-app servers` | — | List servers |
| `discord-app search` | `--query <str>` | Search |
| `discord-app members` | `--server <id>` | List members |

### ChatWise

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `chatwise status` | — | Status |
| `chatwise new` | — | New conversation |
| `chatwise send` | `--text <str>` | Send message |
| `chatwise read` | — | Read response |
| `chatwise ask` | `--text <str>` | Ask question |
| `chatwise model` | `--name <str>` | Switch model |
| `chatwise history` | `--limit N` | History |
| `chatwise export` | — | Export |
| `chatwise screenshot` | — | Screenshot |

### 豆包 App (Doubao App)

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `doubao-app status` | — | Status |
| `doubao-app new` | — | New conversation |
| `doubao-app send` | `--text <str>` | Send message |
| `doubao-app read` | — | Read response |
| `doubao-app ask` | `--text <str>` | Ask question |
| `doubao-app screenshot` | — | Screenshot |
| `doubao-app dump` | — | Dump conversation |

### Antigravity

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `antigravity status` | — | Status |
| `antigravity send` | `--text <str>` | Send message |
| `antigravity read` | — | Read response |
| `antigravity new` | — | New conversation |
| `antigravity dump` | — | Dump conversation |
| `antigravity extract-code` | — | Extract code |
| `antigravity model` | `--name <str>` | Switch model |
| `antigravity watch` | — | Watch mode |

---

## External CLI Integration (Passthrough)

| 命令 | 描述 |
|-------|-------|
| `autocli gh <args>` | GitHub CLI passthrough |
| `autocli docker <args>` | Docker CLI passthrough |
| `autocli kubectl <args>` | Kubernetes CLI passthrough |
| `autocli obsidian <args>` | Obsidian passthrough |
| `autocli readwise <args>` | Readwise passthrough |
| `autocli gws <args>` | Google Workspace passthrough |

---

## Generic Web Reader

使用 Mozilla Readability 从任何网页中提取主要文章内容（默认返回干净的 Markdown 格式）。

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `autocli read <url>` | `-f markdown\|text\|html\|json` (默认: markdown), `-o <file>` | 从任何网页中提取主要文章内容 |

**何时优先选择 `autocli read` 而非 WebFetch / curl:**
- 用户要求“阅读”、“总结”、“从”或“获取”特定 URL 的文章
- 页面是新闻文章、博客文章、文档、维基百科页面、论文等
- 需要干净的 Markdown（自动去除导航/广告/侧边栏/脚本）
- 页面是 JavaScript 渲染的（SPA）— WebFetch 看到一个空壳，`autocli read` 看到完全渲染的 DOM，因为它在一个真实浏览器中运行
- 页面需要登录 — `autocli read` 自动重用用户的 Chrome 会话

**何时不使用 `autocli read`:**
- 当已经存在专门的 autocli 站点适配器（例如 `autocli hackernews top`, `autocli zhihu question`）。站点特定命令提供结构化数据，应始终首先尝试。
- 当用户只需要从已知 API 端点获取原始 JSON。
- 当页面是一个纯应用/仪表板，没有文章内容 — Readability 严格在这种情况下会失败（没有回退，非零退出）。

**示例:**

```bash
# 默认：带有标题、署名、网站名称、发布时间的头部 Markdown
autocli read https://www.anthropic.com/research/some-article

# 仅纯文本（理想情况下用于将摘要输入 LLM）
autocli read https://en.wikipedia.org/wiki/Large_language_model -f text

# 完全结构化输出（标题、署名、摘要、内容 HTML、长度、语言、...）
autocli read https://example.com/article -f json

# 保存到文件而不是标准输出
autocli read https://example.com/article -o ./article.md
```

---

## AI Discovery Commands

| 命令 | 参数 | 描述 |
|-------|------|-------|
| `autocli explore` | `<url>` | 探索网站 API |
| `autocli cascade` | `<url>` | 自动检测认证策略 |
| `autocli generate` | `<url>`, `--goal <str>` | 自动生成适配器 |

---

## Utility Commands

| 命令 | 描述 |
|-------|-------|
| `autocli doctor` | 运行诊断 |
| `autocli completion bash\|zsh\|fish` | 生成 shell 适配器 |
| `autocli list` | 列出所有可用命令 |
| `autocli read <url>` | 作为 Markdown 提取主要文章内容（见通用网页阅读器部分） |
