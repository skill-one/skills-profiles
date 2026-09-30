---
name: twitter-reader
description: 获取 Twitter/X 帖子和文章的内容——包括文本、作者、互动指标以及嵌入的媒体——将图片下载到本地，并生成带有图片引用的完整 Markdown。当需要获取包含图片的推文文本或 X 文章，或为 Markdown/PKM 记录拉取帖子元数据时，请使用此功能。对于包含图片的 X 文章，优先于仅使用 Jina。
---

# Twitter Reader

获取 Twitter/X 帖子和文章内容，支持完整媒体。

## 读取单个帖子的文本：fxtwitter first (2026-08-30)

对于纯文本帖子，建议使用 fxtwitter 镜像 API — 无需登录、无需密钥，
直接工作，并在 `tweet.text` 中返回**完整的 note_tweet 正文**（
`full_text` 键不存在；一个 2,324 字符的长篇公告完整返回）：

```bash
curl -sS --max-time 20 "https://api.fxtwitter.com/<user>/status/<id>" \
  | python3 -c "import json,sys; t=json.load(sys.stdin)['tweet']; print(t['created_at']); print(t['text'])"
```

`replies` 是一个计数，不是回复线程。对于带图片的 X 文章，使用下方的
`fetch_article.py` — fxtwitter 不包含文章正文。

## 带图片的 X 文章：fetch_article.py

```bash
uv run --with pyyaml python scripts/fetch_article.py <article_url> [output_dir]
```

示例：
```bash
uv run --with pyyaml python scripts/fetch_article.py \
  https://x.com/HiTw93/status/2040047268221608281 \
  ./Clippings
```

这将：
- 通过 `twitter-cli` 获取结构化数据（点赞、转发、收藏）
- 通过 `jina.ai` API 获取带图片的内容
- 将所有图片下载到 `attachments/YYYY-MM-DD-AUTHOR-TITLE/`
- 生成带嵌入图片引用的完整 Markdown
- 包含带有元数据的 YAML 前置文本

元数据和纯文本文章来自 `twitter-cli`；图片 URL 随 Jina 返回的 markdown 一起返回。
当 Jina 拒绝时（见下文部分），脚本在 stderr 上警告，保留 twitter-cli 文本，
并报告 `Images: 0`。Markdown 仍然正确；它只是没有图片。
文章明显包含图片时出现 `Images: 0` 是 Jina 拒绝的标志。

### 示例输出

```
Fetching: https://x.com/HiTw93/status/2040047268221608281
--------------------------------------------------
Getting metadata...
Title: 你不知道的大模型训练：原理、路径与新实践
Author: Tw93
Likes: 1648

Getting content and images...
Images: 15

Downloading 15 images...
  ✓ 01-image.jpg
  ✓ 02-image.jpg
  ...

✓ Saved: ./Clippings/2026-04-03-文章标题.md
✓ Images: ./Clippings/attachments/2026-04-03-HiTw93-.../ (15 downloaded)
```

## Jina 的阅读器是间歇性的，它的拒绝看起来像成功

匿名 `r.jina.ai` 访问 x.com 在第三方调用者滥用域名时会被阻塞数小时。
每次匿名调用者都会被阻塞，然后自动过期。两种状态在 2026-09-12 几分钟内都出现了。

拒绝看起来不像失败。`curl` 退出状态为 0，正文是一个 JSON 封装：

```json
{"data":null,"code":403,"name":"AbuseAlleviationError","status":40305,
 "message":"Anonymous access to domain x.com blocked until <date> ..."}
```

过期或未付费的密钥返回相同的形状，带有 `"code":402,
"name":"InsufficientBalanceError"`。`curl --fail` 都捕获不到：这个端点
以 200 HTTP 响应并带有正文中的封装。唯一有效的信号是 Jina 的阅读器在文章正文前
面放置的 `Markdown Content:` 标记：没有标记，就没有文章。`fetch_article.py`
在接受响应之前会测试该标记，这可以防止拒绝封装出现在生成的 Markdown 中。

`scripts/fetch_tweets.sh` 和 `scripts/fetch_tweet.py` 都需要
`JINA_API_KEY` 并且没有第二个备选方案，所以当该密钥过期时它们都会停止工作。
两者都检查相同的标记，并在拒绝时大声失败 — Python 版本在抛出异常时不写入输出文件，
Shell 版本在 stderr 上报告 URL 并以非零状态退出 — 而不是返回一个伪装成帖子的封装。
本仓库不附带任何密钥。

对于简单的纯文本获取：

```bash
# 单个 tweet
curl "https://r.jina.ai/https://x.com/USER/status/TWEET_ID" \
  -H "Authorization: Bearer ${JINA_API_KEY}"

# 批量获取
scripts/fetch_tweets.sh url1 url2 url3
```

## 功能

### 完整文章模式 (fetch_article.py)
- ✅ 结构化元数据（作者、日期、参与指标）
- ✅ 自动图片下载（所有嵌入媒体）
- ✅ 带本地图片引用的完整 Markdown
- ✅ 用于 PKM 系统的 YAML 前置文本
- ✅ 处理 X 文章（长篇内容）

### 简单模式 (Jina API)
- 纯文本内容
- 间歇性可用性（见上部分）；两个脚本都需要
  `JINA_API_KEY` 并且没有备用方案
- 可用于 Jina 回应时的快速文本提取

## 前置条件

### 对于完整文章模式
- `uv`（Python 包管理器）
- 无需额外设置（twitter-cli 自动安装）

### 对于简单模式 (Jina)
```bash
export JINA_API_KEY="your_api_key_here"
# 从 https://jina.ai/ 获取
```

## 输出结构

```
output_dir/
├── YYYY-MM-DD-article-title.md       # 主 Markdown 文件
└── attachments/
    └── YYYY-MM-DD-author-title/
        ├── 01-image.jpg
        ├── 02-image.jpg
        └── ...
```

## 返回的内容

### 完整文章模式
- **YAML 前置文本**：来源、作者、日期、点赞、转发、收藏
- **Markdown 内容**：带本地图片引用的完整文章文本
- **附件**：所有下载的图片在专用文件夹中

### 简单模式
- **标题**：帖子作者和内容预览
- **URL 来源**：原始 tweet 链接
- **发布时间**：GMT 时间戳
- **Markdown 内容**：带远程媒体 URL 的文本

## 支持的 URL 格式

- `https://x.com/USER/status/ID`（帖子）
- `https://x.com/USER/article/ID`（长篇文章）
- `https://twitter.com/USER/status/ID`（旧版）

## 脚本

### fetch_article.py
带图片下载的完整功能文章获取器：
```bash
uv run --with pyyaml python scripts/fetch_article.py <url> [output_dir]
```

### fetch_tweet.py
使用 Jina API 的简单纯文本获取器：
```bash
python scripts/fetch_tweet.py <tweet_url> [output_file]
```

### fetch_tweets.sh
批量获取多个 tweet（Jina API）：
```bash
scripts/fetch_tweets.sh <url1> <url2> ...
```

## twitter-cli 的 500 项上限属于工具，而不是 X

这项技能通过 `twitter-cli` 读取元数据，所以工具自身的限制适用。
无论配置如何编写，`twitter bookmarks` 和其他时间线命令都会停在 500 项。
这个上限是客户端中的一个模块常量：
`_ABSOLUTE_MAX_COUNT = 500` 在 `twitter_cli/client.py` 中，在客户端构建时
作为 `min(maxCount, 500)` 应用。这两行都来自版本 0.8.5。X 自己的收藏时间线远比
这个要深。

两个容易出错的后果：

- 停在正好 500 的运行是自己计数器停止，从未达到读取下一个游标的点。
"平台不再提供页面" 和 "我的循环完成" 是不同的主张，只有第一个是证据。
一个整数是一个需要仔细查看的原因，而不是边界。
- `maxCount` 必须放在配置的 `rateLimit:` 部分下。把它放在 `fetch:` 下，
客户端会忽略它而不提供任何消息，回退到 200。

更深层次意味着直接调用 GraphQL 端点：带有客户端自己的功能标志的
`Bookmarks` 操作，由 `twitter_cli.parser.parse_timeline_response` 解析，
分页直到平台停止返回游标或返回相同的游标两次。在平台的信号下停止，而不是在计数上。

## 从 Jina API 迁移

旧工作流程：
```bash
curl "https://r.jina.ai/https://x.com/..."
# 手动图片提取和下载
```

新工作流程：
```bash
uv run --with pyyaml python scripts/fetch_article.py <url>
# 自动图片下载，完整 Markdown
```
