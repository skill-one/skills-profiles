# DataForSEO：实时SEO数据（扩展）

通过DataForSEO MCP服务器获取实时搜索数据。提供实时SERP结果（有机+图片）、关键词指标、反向链接资料、页面内分析、内容分析、商业列表、AI可见性检查以及跨9个API模块的79+ MCP工具的LLM提及跟踪。

## 前置条件

此技能需要安装DataForSEO扩展：
```bash
./extensions/dataforseo/install.sh
```

**检查可用性：** 在使用任何DataForSEO工具之前，请验证MCP服务器是否连接，方法是检查`serp_organic_live_advanced`或任何DataForSEO工具是否可用。如果工具不可用，请告知用户扩展未安装并提供安装说明。

## API积分意识

DataForSEO按API调用收费。请高效使用：
- 优先选择批量端点而不是多个单个调用
- 除非用户另有指定，否则使用默认参数（美国、英语）
- 在会话中在脑海中缓存结果；不要重新获取相同的数据
- 在运行昂贵的操作（完整反向链接抓取、大量关键词列表）之前提醒用户

## 成本控制

**在每次DataForSEO MCP调用之前**，运行成本估算：
```
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run dataforseo_costs.py check <端点> [--count N]
```

- 如果`"status": "approved"` → 继续进行API调用
- 如果`"status": "needs_approval"` → 向用户显示成本估算并要求确认后再继续
- 如果`"status": "blocked"` → 告知用户将超出每日预算限制；不要继续

**在每次API调用完成后**，记录成本：
```
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run dataforseo_costs.py log <端点> <实际成本>
```

**用户命令用于成本管理：**
- `/seo dataforseo costs today` → 显示今天的支出明细
- `/seo dataforseo costs summary` → 显示7天支出历史
- `/seo dataforseo costs config --mode threshold --threshold 0.50` → 配置批准模式

加载`references/cost-tiers.md`以获取完整的定价表、预算预设和成本降低技巧。

## 快速参考

| 命令 | 它的作用 |
|---------|-------------|
| `/seo dataforseo serp <关键词>` | Google有机SERP结果 |
| `/seo dataforseo serp-images <关键词>` | Google图片SERP结果 |
| `/seo dataforseo serp-youtube <关键词>` | YouTube搜索结果 |
| `/seo dataforseo youtube <视频ID>` | YouTube视频深度分析 |
| `/seo dataforseo keywords <种子>` | 关键词创意和建议 |
| `/seo dataforseo volume <关键词>` | 关键词搜索量 |
| `/seo dataforseo difficulty <关键词>` | 关键词难度分数 |
| `/seo dataforseo intent <关键词>` | 搜索意图分类 |
| `/seo dataforseo trends <关键词>` | Google趋势数据 |
| `/seo dataforseo backlinks <域名>` | 完整反向链接资料 |
| `/seo dataforseo competitors <域名>` | 竞争对手域名分析 |
| `/seo dataforseo ranked <域名>` | 域名排名关键词 |
| `/seo dataforseo intersection <域名>` | 关键词/反向链接重叠 |
| `/seo dataforseo traffic <域名>` | 批量流量估算 |
| `/seo dataforseo subdomains <域名>` | 排名数据子域名 |
| `/seo dataforseo top-searches <域名>` | 提及域名的顶级查询 |
| `/seo dataforseo onpage <URL>` | 页面内分析（Lighthouse + 解析） |
| `/seo dataforseo tech <域名>` | 技术栈检测 |
| `/seo dataforseo whois <域名>` | WHOIS注册数据 |
| `/seo dataforseo content <关键词/URL>` | 内容分析和趋势 |
| `/seo dataforseo listings <关键词>` | 商业列表搜索 |
| `/seo dataforseo ai-scrape <查询>` | GEO的ChatGPT网页抓取器 |
| `/seo dataforseo ai-mentions <关键词>` | LLM提及跟踪 |

---

## SERP分析

### `/seo dataforseo serp <关键词>`

获取实时Google有机搜索结果。

**MCP工具：** `serp_organic_live_advanced`

**默认参数：** location_code=2840（美国），language_code=en，device=desktop，depth=100

**也支持：** `serp_organic_live_advanced`工具通过`se`参数支持Google、Bing和Yahoo。指定"bing"或"yahoo"以切换搜索引擎。

**输出：** 排名、URL、标题、描述、域名、特色片段、AI概述参考、People Also Ask。

### `/seo dataforseo serp-youtube <关键词>`

获取YouTube搜索结果。对GEO非常有价值。YouTube提及与AI引用的相关性最强。

**MCP工具：** `serp_youtube_organic_live_advanced`

**输出：** 视频标题、频道、观看次数、上传日期、描述、URL。

### `/seo dataforseo youtube <视频ID>`

对特定YouTube视频进行深度分析：信息、评论和字幕。一些第三方研究报告了YouTube提及与AI可见性之间的0.737相关性，因此应将其视为依赖于方法的GEO信号。

**MCP工具：** `serp_youtube_video_info_live_advanced`，`serp_youtube_video_comments_live_advanced`，`serp_youtube_video_subtitles_live_advanced`

**参数：** video_id（YouTube视频ID，例如："dQw4w9WgXcQ"）

**输出：** 视频元数据（标题、频道、观看次数、点赞、描述）、互动性强的顶级评论、字幕/文本。

### `/seo dataforseo serp-images <关键词>`

获取实时Google图片搜索结果。查看哪些图片为关键词排名、哪些域名主导图片结果以及识别视觉内容机会。

**MCP工具：** `serp_google_images_live_advanced`

**默认参数：** location_code=2840（美国），language_code=en，device=desktop，depth=100

**参数：** keyword（必需），depth（可选，最大700，按100结果增量计费），search_param（可选，例如"site:example.com"）

**成本警告：** 使用`site:`或`filetype:`运算符会导致**5倍API成本**。在运行过滤查询之前提醒用户。

**输出：** 排名、标题、alt文本、来源页面URL、直接图片URL、域名、编码URL。

**分析提供：**
- 域名主导：哪些站点拥有最多的图片排名（前10个域名按数量）
- alt文本模式：顶级排名图片中的常见标题/alt文本模式
- 格式分布：WebP与JPEG与PNG在顶级结果中的分布（从image_url扩展推断）
- 机会识别：用户在有机排名但没有图片出现的关键词

---

## 关键词研究

### `/seo dataforseo keywords <种子>`

从种子关键词生成关键词创意、建议和相关术语。

**MCP工具：** `dataforseo_labs_google_keyword_ideas`，`dataforseo_labs_google_keyword_suggestions`，`dataforseo_labs_google_related_keywords`

**默认参数：** location_code=2840（美国），language_code=en，limit=50

**输出：** 关键词、搜索量、CPC、竞争水平、关键词难度、趋势。

### `/seo dataforseo volume <关键词>`

获取关键词列表的搜索量和指标。

**MCP工具：** `kw_data_google_ads_search_volume`

**参数：** keywords（数组，逗号分隔），location_code，language_code

**输出：** 关键词、月搜索量、CPC、竞争、月趋势数据。

### `/seo dataforseo difficulty <关键词>`

计算关键词排名竞争难度分数。

**MCP工具：** `dataforseo_labs_bulk_keyword_difficulty`

**参数：** keywords（数组），location_code，language_code

**输出：** 关键词、难度分数（0-100）、解释（简单/中等/困难/非常困难）。

### `/seo dataforseo intent <关键词>`

按用户搜索意图对关键词进行分类。

**MCP工具：** `dataforseo_labs_search_intent`

**参数：** keywords（数组），location_code，language_code

**输出：** 关键词、意图类型（信息性、导航性、商业性、交易性）、置信度分数。

### `/seo dataforseo trends <关键词>`

使用Google趋势数据分析关键词随时间的变化趋势。

**MCP工具：** `kw_data_google_trends_explore`

**参数：** keywords（数组），location_code，date_from，date_to，language_code

**输出：** 关键词、时间序列数据、趋势方向、季节性信号。

---

## 域名与竞争对手分析

### `/seo dataforseo backlinks <域名>`

全面反向链接资料分析。

**MCP工具：** `backlinks_summary`，`backlinks_backlinks`，`backlinks_anchors`，`backlinks_referring_domains`，`backlinks_bulk_spam_score`，`backlinks_timeseries_summary`

**默认参数：** limit=100 per sub-call

**输出：** 总反向链接、引用域名、域名排名、垃圾邮件分数、顶级锚点、随时间新增/丢失的反向链接、nofollow比例、顶级引用域名。

### `/seo dataforseo competitors <域名>`

识别竞争对手域名并估算流量。

**MCP工具：** `dataforseo_labs_google_competitors_domain`，`dataforseo_labs_google_domain_rank_overview`，`dataforseo_labs_bulk_traffic_estimation`

**输出：** 竞争对手域名、关键词重叠%、估计流量、域名排名、常见关键词。

### `/seo dataforseo ranked <域名>`

列出域名排名的关键词及其位置和页面数据。

**MCP工具：** `dataforseo_labs_google_ranked_keywords`，`dataforseo_labs_google_relevant_pages`

**默认参数：** limit=100，location_code=2840

**输出：** 关键词、位置、URL、搜索量、流量份额、SERP功能。

### `/seo dataforseo intersection <域名1> <域名2> [...]`

在2-20个域名之间查找共享关键词和反向链接来源。

**MCP工具：** `dataforseo_labs_google_domain_intersection`，`backlinks_domain_intersection`

**参数：** domains（2-20数组）

**输出：** 每个域名中共享的关键词及其位置、共享的反向链接来源、每个域名的唯一关键词。

### `/seo dataforseo traffic <域名>`

估算一个或多个域名的有机搜索流量。

**MCP工具：** `dataforseo_labs_bulk_traffic_estimation`

**参数：** domains（数组）

**输出：** 域名、估计的有机流量、估计的流量成本、顶级关键词。

### `/seo dataforseo subdomains <域名>`

枚举子域名及其排名数据和流量估算。

**MCP工具：** `dataforseo_labs_google_subdomains`

**参数：** target（域名），location_code，language_code

**输出：** 子域名、排名关键词数量、估计流量、有机成本。

### `/seo dataforseo top-searches <域名>`

查找在搜索结果中提及特定域名的最流行搜索查询。

**MCP工具：** `dataforseo_labs_google_top_searches`

**参数：** target（域名），location_code，language_code

**输出：** 查询、搜索量、域名位置、SERP功能、流量份额。

---

## 技术/页面内

### `/seo dataforseo onpage <URL>`

运行页面内分析，包括Lighthouse审计和内容解析。

**MCP工具：** `on_page_instant_pages`，`on_page_content_parsing`，`on_page_lighthouse`

**使用方法：**
- `on_page_instant_pages`：快速页面分析（状态代码、元标签、内容大小、页面时间、断链、页面内检查）
- `on_page_content_parsing`：提取和解析页面内容（纯文本、字数、结构）
- `on_page_lighthouse`：完整Lighthouse审计（性能分数、可访问性、最佳实践、SEO、核心Web Vitals）

**输出：** 爬取的页面、状态代码、元标签、标题、内容大小、加载时间、Lighthouse分数、断链、资源分析。

### `/seo dataforseo tech <域名>`

检测域名上使用的技术。

**MCP工具：** `domain_analytics_technologies_domain_technologies`

**输出：** 技术名称、版本、类别（CMS、分析、CDN、框架等）。

### `/seo dataforseo whois <域名>`

检索WHOIS注册数据。

**MCP工具：** `domain_analytics_whois_overview`

**输出：** 注册商、创建日期、到期日期、名称服务器、注册人信息（如果公开）。

---

## 内容与商业数据

### `/seo dataforseo content <关键词/URL>`

分析内容质量、按主题搜索内容、跟踪短语趋势。

**MCP工具：** `content_analysis_search`，`content_analysis_summary`，`content_analysis_phrase_trends`

**参数：** keyword（用于搜索/趋势）或URL（用于摘要）

**输出：** 内容匹配与质量分数、情感分析、可读性指标、短语趋势数据随时间变化。

### `/seo dataforseo listings <关键词>`

搜索商业列表以进行本地SEO竞争分析。

**MCP工具：** `business_data_business_listings_search`

**参数：** keyword、location（可选）

**输出：** 商业名称、描述、类别、地址、电话、域名、评分、评论数量、声称状态。

---

## AI可见性/GEO

### `/seo dataforseo ai-scrape <查询>`

抓取ChatGPT对查询返回的内容。ChatGPT可见性检查：查看ChatGPT为您的目标关键词引用了哪些来源。在可用时检查Google AI概述和AI模式与GSC gen-AI报告。

**MCP工具：** `ai_optimization_chat_gpt_scraper`

**参数：** query、location_code（可选）、language_code（可选）。使用`ai_optimization_chat_gpt_scraper_locations`查找可用位置。

**输出：** ChatGPT响应内容、引用的来源/URL、参考的域名。

### `/seo dataforseo ai-mentions <关键词>`

跟踪LLM如何提及品牌、域名和主题。对GEO至关重要。测量多个LLM平台上的实际AI可见性。

**MCP工具：** `ai_opt_llm_ment_search`，`ai_opt_llm_ment_top_domains`，`ai_opt_llm_ment_top_pages`，`ai_opt_llm_ment_agg_metrics`

**参数：** keyword、location_code（可选）、language_code（可选）。使用`ai_opt_llm_ment_loc_and_lang`查找可用位置/语言，并使用`ai_optimization_llm_models`查找支持的LLM模型。

**工作流程：**
1. 使用`ai_opt_llm_ment_search`搜索LLM提及（在LLM响应中查找品牌/关键词的提及）
2. 使用`ai_opt_llm_ment_top_domains`获取顶级引用域名（哪些域名对这个主题引用最多）
3. 使用`ai_opt_llm_ment_top_pages`获取顶级引用页面（哪些特定页面引用最多）
4. 使用`ai_opt_llm_ment_agg_metrics`获取聚合指标（总体提及量、趋势）

**输出：** LLM提及数量、顶级引用域名及其频率、顶级引用页面、提及趋势随时间变化、跨平台可见性分数。

**高级：** 使用`ai_opt_llm_ment_cross_agg_metrics`进行跨模型比较（ChatGPT、Claude、Perplexity等提及的差异）。
