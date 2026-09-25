# 新闻聚合技能

从 44+ 个来源（包括国际新闻 + AI 筛选聚合器 + 用户定义的 OPML 订阅源）实时获取热点新闻，生成中文深度分析报告。

---

## 🔄 通用工作流程（3 步）

**每**一个新闻请求都遵循相同的工作流程，无论来源或组合如何：

### 第 1 步：获取数据
```bash
# 单个来源
python3 scripts/fetch_news.py --source <来源键> --no-save

# 多个来源（逗号分隔）
python3 scripts/fetch_news.py --source hackernews,github,wallstreetcn --no-save

# 所有来源（广泛扫描）
python3 scripts/fetch_news.py --source all --limit 15 --deep --no-save

# 带关键词筛选（自动扩展："AI" → "AI,LLM,GPT,Claude,Agent,RAG"）
python3 scripts/fetch_news.py --source hackernews --keyword "AI,LLM,GPT" --deep --no-save
```

### 第 2 步：生成报告
读取输出 JSON 并使用下方的**统一报告模板**格式化**每个**条目。将所有内容翻译成**简体中文**。

### 第 3 步：保存并展示
将报告保存到 `reports/YYYY-MM-DD/<来源>_report.md`，然后将完整内容展示给用户。

---

## 📰 统一报告模板

**所有来源使用此单一模板。** 根据数据可用性显示/隐藏可选字段。

```markdown
#### N. [标题 (中文翻译)](https://原始链接.com)
- **来源**: 源名 | **时间**: 时间 | **热度**: 🔥 热度值
- **链接**: [讨论](hn_url) | [GitHub](gh_url)     ← 仅在数据存在时显示
- **摘要**: 一句中文摘要。
- **深度分析**: 💡 **洞察**: 深度分析（背景、影响、技术价值）。
```

### 来源特定适配

仅与通用模板的差异：

| 来源 | 适配 |
|---|---|
| **Hacker News** | **必须**包含 `[讨论](hn_url)` 链接 |
| **GitHub** | 使用 `🌟 Stars` 表示热度，添加 `Lang` 字段，在深度分析中添加 `#Tags` |
| **Hugging Face** | 使用 `🔥 +N` 点赞表示热度，如果存在则包含 `[GitHub](url)`，**深度解读**（不只是翻译摘要） |
| **Weibo** | 保留精确的热度文本（例如 "108万"） |
| **AIHOT** | `summary` 已是中文编辑稿，**直接引用**不要再翻译；热度字段为空也不要造数据；保留 `推荐理由` 风格的一句话点评 |
| **TLDR AI** | 单条标题往往是多主题混合（`主题 A 💻, 主题 B ⚡, 主题 C ⛪`），**拆成 bullet 列出每个主题**；`summary` 是 HTML 段落，需要拆出每个主题对应的一两句概述 |
| **Import AI** | 周刊长文，标题形如 `Import AI 458: 主题1; 主题2; 主题3`。**建议默认配 `--deep`**，否则 RSS summary 只是开头几句；深度分析直接提炼 Jack Clark 的核心观点而非平铺事实 |
| **国际新闻** | **必须**对每个条目使用统一报告模板；仅使用最近 24h RSS 条目，不用更早新闻 Smart Fill；英文标题与摘要翻译成简体中文，保留原始媒体名与链接；同一事件多家媒体重复时可合并观点但不能合并链接 |
| **Reuters** | `reuters` 使用 Google News RSS 的 `site:reuters.com` 备用；报告中保留 `Reuters (Google News fallback)` 来源，不要写成官方公开 RSS |

---

## 🛠️ 工具

### fetch_news.py

| 参数 | 描述 | 默认值 |
|---|---|---|
| `--source` | 来源键（逗号分隔）。见下表。 | `all` |
| `--limit` | 每个来源最大条目数 | `15` |
| `--keyword` | 逗号分隔的关键词筛选 | 无 |
| `--deep` | 下载文章文本以进行更丰富的分析 | 关闭 |
| `--save` | 强制保存到报告目录 | 单个来源自动保存 |
| `--outdir` | 自定义输出目录 | `reports/YYYY-MM-DD/` |

### 可用来源（44+ 加用户 OPML）

| 分类 | 键 | 名称 |
|---|---|---|
| **全球新闻** | `hackernews` | Hacker News |
| | `36kr` | 36氪 |
| | `wallstreetcn` | 华尔街见闻 |
| | `tencent` | 腾讯新闻 |
| | `weibo` | 微博热搜 |
| | `v2ex` | V2EX |
| | `producthunt` | Product Hunt |
| | `github` | GitHub Trending |
| **技术社区** (v2) | `lobsters` | Lobsters |
| | `devto` | Dev.to |
| **AI/技术** | `huggingface` | HF Daily Papers |
| | `arxiv` | arXiv (cs.AI/cs.CL/cs.LG, v2) |
| | `ai_newsletters` | 所有 AI 订阅源（聚合） |
| | `bensbites` | Ben's Bites |
| | `interconnects` | Interconnects (Nathan Lambert) |
| | `oneusefulthing` | One Useful Thing (Ethan Mollick) |
| | `chinai` | ChinAI (Jeffrey Ding) |
| | `memia` | Memia |
| | `aitoroi` | AI to ROI |
| | `kdnuggets` | KDnuggets |
| **中文** (v2) | `sspai` | 少数派 |
| | `infoq_cn` | InfoQ 中文站（RSS 只给标题，**推荐配 `--deep`** 拿正文） |
| **AI 筛选** (v3) | `aihot` | AIHOT 中文 AI 精选（跨源 + 中文编辑稿）|
| | `tldr_ai` | TLDR AI 英文日刊 |
| | `import_ai` | Import AI by Jack Clark 周刊（**推荐 `--deep`**）|
| **国际新闻** | `international` | 最近 24h 国际新闻聚合（BBC / Guardian / Al Jazeera / France 24 / Reuters fallback）|
| | `bbc_top` | BBC Top News (24h) |
| | `bbc_world` | BBC World (24h) |
| | `bbc_chinese` | BBC 中文 (24h) |
| | `guardian_world` | The Guardian World (24h) |
| | `aljazeera` | Al Jazeera (24h) |
| | `france24` | France 24 (24h) |
| | `reuters` | Reuters via Google News RSS fallback (24h) |
| **播客** | `podcasts` | 所有播客（聚合） |
| | `lexfridman` | Lex Fridman |
| | `80000hours` | 80,000 Hours |
| | `latentspace` | Latent Space |
| **文章** | `essays` | 所有文章（聚合） |
| | `paulgraham` | Paul Graham |
| | `waitbutwhy` | Wait But Why |
| | `jamesclear` | James Clear |
| | `farnamstreet` | Farnam Street |
| | `scottyoung` | Scott Young |
| | `dankoe` | Dan Koe |
| **自定义** (v2) | `user` | 你的 OPML 订阅源（见下文） |

### 自定义订阅源 (User OPML)

把你常看的 RSS/Atom 源写进 OPML，`--source user` 即可统一抓取。

**1. 放置 OPML 文件**（按优先级查找）：
- `~/.config/news-aggregator/user_sources.opml`（推荐，跨技能复用）
- `<skill_root>/user_sources.opml`（本仓库内）

**2. 文件格式**：标准 OPML 2.0，可直接从 Feedly / Inoreader / NetNewsWire 导出。参考 `user_sources.opml.example`：

```xml
<outline type="rss" text="Simon Willison" title="Simon Willison"
         xmlUrl="https://simonwillison.net/atom/everything/" />
```

只 `xmlUrl` 必填，其它可选。

**3. 运行**：`python3 scripts/fetch_news.py --source user --limit 15`


### daily_briefing.py (晨间例行)

预配置的多来源配置文件：

```bash
python3 scripts/daily_briefing.py --profile <配置文件>
```

| 配置文件 | 来源 | 指令文件 |
|---|---|---|
| `general` | HN, 36Kr, GitHub, Weibo, PH, WallStreetCN | `instructions/briefing_general.md` |
| `finance` | WallStreetCN, 36Kr, Tencent | `instructions/briefing_finance.md` |
| `tech` | GitHub, HN, Product Hunt | `instructions/briefing_tech.md` |
| `social` | Weibo, V2EX, Tencent | `instructions/briefing_social.md` |
| `ai_daily` | HF Papers, AI Newsletters | `instructions/briefing_ai_daily.md` |
| `reading_list` | Essays, Podcasts | (使用通用模板) |

**工作流程**：执行脚本 → 读取对应的指令文件 → 生成遵循指令文件和通用模板的报告。

---

## ⚠️ 规则（严格）

1. **语言**：所有输出为**简体中文 (简体中文)**。保留知名英文专有名词（ChatGPT, Python 等）。
2. **时间**：**必填字段**。不得跳过。如果 JSON 中缺失，标记为 "未知时间"。保留 "实时" / "今天" / "热点" 原样。
3. **反幻觉**：仅使用 JSON 中的数据。不得编造新闻条目。使用简单的主谓宾句子。不要编造因果关系。
4. **智能关键词扩展**：当用户说 "AI" → 自动扩展为 `"AI,LLM,GPT,Claude,Agent,RAG,DeepSeek"`。类似扩展适用于其他领域。
5. **智能填充**：如果在时间窗口内结果少于 5 条，用高价值条目补充。标记补充条目为 ⚠️。**例外**：国际新闻来源是 24h 窗口；不要用更早的条目补充。
6. **保存**：在展示前，始终将报告保存到 `reports/YYYY-MM-DD/`。

---

## 📋 交互式菜单

当用户说 **"如意如意"** 或询问 "菜单/帮助" 时：

1. 读取 `templates.md`
2. 显示菜单
3. 使用上述通用工作流程执行用户的选择

---

## 要求

- Python 3.8+，`pip install -r requirements.txt`
- Playwright（用于 HF Papers & Ben's Bites）：`playwright install chromium`
