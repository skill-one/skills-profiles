# AI 搜索 / GEO 优化 (2026年5月)

## 主要来源：Google 的 AI 优化指南

Google 官方在 Search Central 文档中发布的立场：

> "从 Google 搜索的角度来看，针对生成式 AI 搜索进行优化就是针对搜索体验进行优化，因此仍然是 SEO（搜索引擎优化）。

阅读 `references/google-ai-optimization-guide.md` 获取完整分析、辟谣列表（`llms.txt`、内容分块、AI 重述、提及农场等均被 Google 认为无效），以及内容质量测试的 Who/How/Why。

审计应将 GEO 发现结果作为 **应用于 AI 搜索表面的 SEO 基础**，而不是作为独立的优化学科。当社区建议与 Google 的主要来源相矛盾时，应优先考虑 Google，并在报告中注明矛盾之处。

## 关键数据

下方的第三方数据未在 2026年9月23日 进行重新核实。引用时请务必注明来源和日期，或直接省略。

| 指标 | 数值 | 来源 |
|------|-------|-------|
| AI 概览覆盖范围 | 每月超过 25 亿活跃用户，数据来自 2026年 Google I/O 大会主旨演讲报道；未在 Google 自有来源上确认；200 多个国家 | 第三方 I/O 报道 |
| AI 概览查询覆盖范围 | 查询的约 50%（第三方测量；各国差异） | 行业数据 |
| AI 模式月活跃用户 | 1 亿以上，数据来自 2026年 Google I/O 大会主旨演讲报道；未在 Google 自有来源上确认 | 第三方 I/O 报道 |
| AI 模式模型 | Google 经常升级（Gemini 3.5 Flash 于 2026年5月19日 成为默认版本，此后还推出了更新的 Flash 模型）；切勿将建议与特定模型绑定 | Google (blog.google) |
| AI 引用会话增长 | 527%（2025年1月至5月） | 第三方（归因于 SparkToro；未重新核实） |
| ChatGPT 周活跃用户 | 9 亿 | OpenAI |
| Perplexity 月查询量 | 5 亿以上 | Perplexity |

## 关键洞察：品牌提及 > 链接

**品牌提及与 AI 可见性的相关性是链接的 3 倍。**
(Ahrefs 2025年12月对 7.5 万个品牌的调查)

| 信号 | 与 AI 引用的相关性 |
|------|------------------|
| YouTube 提及 | ~0.737（最强） |
| Reddit 提及 | 高 |
| 维基百科存在 | 高 |
| LinkedIn 存在 | 中等 |
| 域名评级（链接） | ~0.266（弱） |

**只有 11% 的域名** 同时被 ChatGPT 和 Google AI 概览在相同查询中引用，因此平台特定的优化至关重要。

---

## GEO 分析标准（更新）

### 1. 引用分数 (25%)

**自包含的答案块** 对 AI 系统来说易于引用。第三方研究表明大约 130-170 字；这是一个可读性启发式方法，而不是 Google 的要求（Google 的 AI 优化指南表示您不需要为 AI 分块内容）。并且 **约 44% 的 AI 引用来自页面的前 30%**（SE Ranking 研究），优先加载最易于引用、自包含的答案，而不是将其隐藏在折叠内容之下。

**强信号：**
- 清晰、可引用的句子，包含具体事实/数据
- 自包含的答案块（可以脱离上下文提取）
- 在段落前 40-60 字内直接回答
- 声明有具体来源
- 遵循 "X 是..." 或 "X 指的是..." 模式的定义
- 其他地方找不到的独特数据点

**弱信号：**
- 模糊、笼统的陈述
- 没有证据的观点
- 隐藏的结论
- 没有具体数据点

### 2. 结构化可读性 (20%)

**92% 的 AI 概览引用来自前 10 名排名页面**，但 47% 来自排名低于第 5 的页面，显示了不同的选择逻辑。

**强信号：**
- 清晰的 H1->H2->H3 标题层次结构
- 基于问题的标题（匹配查询模式）
- 短段落（2-4 句话）
- 用于比较数据的表格
- 用于分步或多项内容的有序/无序列表
- 结构化的 FAQ 部分（清晰的问答格式）

**弱信号：**
- 没有结构的文本墙
- 不一致的标题层次结构
- 没有列表或表格
- 信息隐藏在段落中

### 3. 多模态内容 (15%)

多模态内容可以支持 AI 答案的选择（仅第三方声称；没有主要来源提供具体数据）。

**检查：**
- 文本 + 相关图片
- 视频内容（嵌入或链接）
- 信息图表和图表
- 交互式元素（计算器、工具）
- 支持媒体的结构化数据

### 4. 权威性与品牌信号 (20%)

**强信号：**
- 带有资质的作者署名
- 发布日期和最后更新日期
- **时效性**，内容在 3 个月内更有可能被 AI 答案引用；6 个月以上的页面失去引用资格（SE Ranking，1.3 亿引用研究）。定期更新计划是 GEO 中最高杠杆的操作之一。
- 对原始来源的引用（研究、官方文档、数据）
- 组织资质和隶属关系
- 带有归属的专家引言
- 实体在维基百科、Wikidata 中的存在
- Reddit、YouTube、LinkedIn 上的提及

**弱信号：**
- 匿名作者
- 没有日期
- 没有引用来源
- 跨平台没有品牌存在

### 5. 技术可访问性 (20%)

**许多 AI 爬虫抓取原始 HTML 而不运行 JavaScript**（例如公共测试中的 GPTBot 和 PerplexityBot），而 Googlebot 渲染 JavaScript 并为 AI 概览和 AI 模式提供内容。服务器端渲染可保持内容对所有爬虫可见。

**检查：**
- 服务器端渲染 (SSR) 与客户端内容
- AI 爬虫在 robots.txt 中的访问权限
- llms.txt 存在（报告完整性；它在本次评分中**没有权重**，见 `references/llmstxt-evidence.md`）
- RSL 1.0 许可条款

---

## AI 爬虫检测

检查 `robots.txt` 中的这些 AI 爬虫：

| 爬虫 | 所有者 | 目的 | 是否遵守 robots.txt? |
|------|-------|-------|---|
| GPTBot | OpenAI | **仅模型训练**（**不是** ChatGPT 搜索） | 是 |
| OAI-SearchBot | OpenAI | **ChatGPT 搜索可引用性**（决定可引用性的爬虫） | 是 |
| ChatGPT-User | OpenAI | ChatGPT 浏览（用户触发） | "可能不适用" 根据 OpenAI（用户触发） |
| ClaudeBot | Anthropic | **仅模型训练**（**不是** Claude 的搜索功能） | 是 |
| Claude-SearchBot | Anthropic | **Claude/Claude.ai 搜索结果可引用性**（决定可引用性的爬虫） | 是 |
| Claude-User | Anthropic | 代表用户浏览 Claude（用户触发） | **是**（Anthropic：所有三个爬虫都遵守 robots.txt） |
| PerplexityBot | Perplexity | Perplexity AI 搜索（**不用于** 基础模型训练） | 是 |
| Perplexity-User | Perplexity | 为用户问题抓取（用户触发） | 通常忽略 |
| CCBot | Common Crawl | 训练数据（通常被阻止） | 是 |
| Bytespider | ByteDance | TikTok/Douyin AI | 是 |
| cohere-ai | Cohere | Cohere 模型 | 是 |
| Google-Extended | Google | **仅 Gemini/Vertex 训练和基础**（**不是** Google 搜索） | 是 |
| Google-CloudVertexBot | Google | 网站所有者请求的 Vertex AI 代理抓取 | 是 |
| Google-Agent | Google | 用户触发的代理抓取（为用户进行代理浏览） | **否**（用户触发） |
| Google-GeminiNotebook | Google | 抓取用户添加的单独源 URL（已取代 `Google-NotebookLM`，支持至 2026 年 8 月） | **否**（用户触发） |
| Google Messages | Google | 用户触发的抓取 | **否**（用户触发） |
| Applebot-Extended | Apple | **仅 Apple Intelligence / 生成式 AI 训练数据选择退出**（**不是** Siri、Spotlight 或 Safari 搜索；它本身不抓取内容，而是标记 Applebot 已经抓取的内容） | 是 |

来源：[OpenAI 爬虫](https://platform.openai.com/docs/bots)、[Google 爬虫概述](https://developers.google.com/search/docs/crawling-indexing/overview-google-crawlers)、[Anthropic 爬虫支持文章](https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler)、[Apple Applebot-Extended 支持文章](https://support.apple.com/en-us/119829)。
Anthropic 当前的爬虫支持文章仅记录 ClaudeBot、Claude-User 和 Claude-SearchBot；它没有列出 `anthropic-ai`，因此之前未经核实的 `anthropic-ai` 行已被移除，而不是作为猜测保留。

**建议：** 允许 OAI-SearchBot、Claude-SearchBot 和 PerplexityBot 以实现 AI 搜索可见性。GPTBot、ClaudeBot、CCBot 和 Applebot-Extended 仅用于训练信号——根据许可偏好允许或阻止它们，而不是基于搜索可见性。

### 检查您要提出的声明对应的正确爬虫

两对通常会被混淆。**每个声明下只能由其自己的爬虫的 robots.txt 状态支持**——分别检查并单独报告。

| 您要提出的声明 | 要检查的爬虫 | 不支持此声明的爬虫 |
|---|---|---|
| "内容可在 ChatGPT 搜索中引用" | `OAI-SearchBot` | `GPTBot` |
| "内容可用于 OpenAI 模型训练" | `GPTBot` | `OAI-SearchBot` |
| "内容可用于 Gemini/Vertex 训练和基础" | `Google-Extended` | `Googlebot` |
| "内容有资格被 Google 搜索 / AI 概览" | `Googlebot` | `Google-Extended` |
| "内容可在 Claude 的搜索功能中引用" | `Claude-SearchBot` | `ClaudeBot` |
| "内容可用于 Anthropic 模型训练" | `ClaudeBot` | `Claude-SearchBot` |
| "内容可用于 Apple Intelligence 训练" | `Applebot-Extended` | `Applebot` |
| "内容可通过 Siri、Spotlight 或 Safari 搜索发现" | `Applebot` | `Applebot-Extended` |

- **`Google-Extended` 仅管理 Gemini 和 Vertex AI 训练和基础使用。它不影响普通 Google 搜索的包含，也不影响 AI 概览和 AI 模式的包含，这两者都来自 `Googlebot` 索引。** 永远不要将 `Google-Extended` 评为“Google 搜索准备就绪”信号，也永远不要引用被阻止的 `Google-Extended` 作为证据表明网站未包含在 Google 搜索中。
- **`OAI-SearchBot` 是决定 ChatGPT 搜索可引用性的爬虫。`GPTBot` 是 OpenAI 的独立训练爬虫。** 检查 `GPTBot` 访问权限并不能告诉您 ChatGPT 搜索是否可以引用该页面。一个阻止 `GPTBot` 但允许 `OAI-SearchBot` 的网站可以在 ChatGPT 搜索中完全被引用。
- **`Claude-SearchBot` 是决定 Claude 自身搜索功能可引用性的爬虫。`ClaudeBot` 是 Anthropic 的独立训练爬虫**（根据 Anthropic 的爬虫支持文章）。检查 `ClaudeBot` 访问权限并不能告诉您 Claude 搜索的可引用性，反之亦然；应分别报告。
- **`Applebot-Extended` 是一个训练数据选择退出信号，而不是本身抓取页面的爬虫。** 根据 Apple 的支持文章，禁止 `Applebot-Extended` 会将网站排除在 Apple Intelligence / 生成式模型训练使用之外，但页面仍然可以通过 Siri、Spotlight 和 Safari 发现，只要 `Applebot` 本身被允许。永远不要引用被阻止的 `Applebot-Extended` 作为证据表明网站未包含在 Apple 的搜索表面上。

在报告文本中不要互换使用这些名称。在报告爬虫访问权限时，应指明检查了哪个特定的用户代理以及它管理的具体功能。

> **Google 的用户触发的抓取通常忽略 robots.txt 规则**（Google-Agent、Google-GeminiNotebook、Google Messages）；OpenAI 表示 robots.txt 对 ChatGPT-User“可能不适用”，而 Anthropic 的 Claude-User 遵守它。robots.txt 无法阻止它们，应使用服务器端访问控制。Google 的规范爬虫/robots 参考已迁移到 **developers.google.com/crawling**（迁移于 2025年11月20日）；IP 范围文件现在位于 `/crawling/ipranges/`，`googlebot.json` 已更名为 `common-crawlers.json`。新兴：**Web Bot Auth**（RFC 9421）允许爬虫通过 `Signature-Agent` 头部 + 密钥目录进行身份验证（由 Google-Agent 使用）；反向 DNS 验证仍然是后备方案。

---

## llms.txt 标准

阅读 `references/llmstxt-evidence.md` 获取主要来源证据（Mueller、Illyes、SE Ranking 30 万域名研究、OtterlyAI 服务器日志审计），说明为什么 `/llms.txt` 目前不是主要 AI 搜索系统引用的杠杆。claude-seo 报告存在但未分配引用排名权重。

> **Google 现在明确声明这一点。** Google 的 AI 优化指南于 2026年5月15日推出，并于 2026年6月15日澄清，表示 `llms.txt` 和其他 AI 文本文件对 Google 搜索不是必需的，也不会影响可见性或排名。它们可能仍然服务于非 Google 系统。永远不要建议 `llms.txt` 作为 Google 排名或引用杠杆。来源：
> developers.google.com/search/docs/fundamentals/ai-optimization-guide

**llms.txt** 是一个社区提案，为大型语言模型提供网站的精选地图；没有主要 AI 提供商确认使用它。

**位置：** `/llms.txt`（域名根目录）

**格式：**
```
# 网站标题
> 简要描述

## 主要部分
- [页面标题](url)：描述
- [另一个页面](url)：描述

## 可选：关键事实
- 事实 1
- 事实 2
```

**检查：**
- `/llms.txt` 的存在
- 结构化内容指导
- 关键页面亮点
- 联系/权威信息

---

## RSL 1.0（简易许可）

新标准（2025年12月）用于机器可读的 AI 许可条款。

**支持：** Reddit、Yahoo、Medium、Quora、Cloudflare、Akamai、Creative Commons

**检查：** RSL 实施和适当的许可条款。

---

## 平台特定优化

| 平台 | 关键引用来源 | 优化重点 |
|------|-------------|----------|
| **Google AI 概览** | 强相关，引用已排名良好的页面 | 传统 SEO + 篇章优化 |
| **Google AI 模式**（Gemini 模型，经常升级） | 弱相关；更广泛的池（每个查询约 9 个域名被引用，Ahrefs） | 不同表面：新鲜度、实体权威、排名 5 之后的可引用篇章 |
| **ChatGPT** | 维基百科（47.9%）、Reddit（11.3%） | 实体存在、权威来源 |
| **Perplexity** | Reddit（46.7%）、维基百科 | 社区验证、讨论 |
| **Bing Copilot** | Bing 索引、权威网站 | Bing SEO、IndexNow |

> **两个 Google 引用引擎，而不是一个。** AI 模式和 AI 概览约 86% 的情况下得出相同结论，但引用相同 URL 的概率仅为 **13.7%**（Ahrefs 研究，54 万查询对）。将它们视为不同的表面：在传统搜索结果中排名良好可让 AI 概览引用，但 AI 模式从更广泛的池中抽取，其中新鲜度和实体权威胜过原始排名。两者都应评分。
>
> **AI 模式也是一个预订表面（2026年8月27日）。** 航班价格跟踪带电子邮件提醒（覆盖 180 多个国家和地区）、通过集成合作伙伴的酒店预订、以及以点数或里程显示的票价现在都在 AI 模式内部发生。旅游和酒店客户应检查合作伙伴资格；这里没有记录的排名变化。
>
> **用户体验现已统一，表面仍然不同。** 在 2026年 Google I/O 大会（2026年5月19日）上，Google 将 AI 概览和 AI 模式合并为“无缝的 AI 搜索体验”（问题 → AI 概览 → 在 AI 模式中进行后续）以及新的智能搜索框。体验是一个流程，但两个引用引擎在技术上仍然不同（不同的模型/链接集），继续评分两者。

### AI 搜索中的引用表面和控制（2026）

Google 在 AI 概览 **和** AI 模式（2026年5月）中添加了许多 AI 引用/来源表面：

- **首选来源**，一个符合条件的域名或子域名可以被用户选择，使其内容更有可能出现在该用户的 Top Stories 中，并符合在 AI 模式或 AI 概览中获得首选徽章的资格。这是一个**按用户偏好**，而不是一个记录在案的通用排名信号。出版商可以提供 Google 的交互式按钮或深度链接，但不应承诺全站排名提升。自 2026年9月18 日起，文档还要求网站包含在 Search generative AI 功能（Search Console 的“Search generative AI”控制）中，才能在 AI 模式和 AI 概览中显示为首选来源。来源：
> developers.google.com/search/docs/appearance/preferred-sources
- **“高度引用”徽章**，通过原创主要报道获得，其他文章会引用。
- **社区观点**，提升 Reddit/论坛/一手内容。
- 内联链接、桌面悬停**链接预览**和突出的链接轮播。

**控制 AI 功能外观：** 没有 AI 特定的选择退出文件，但自 2026年8月31 日起，每个网站都有一个 Search Console 控制，“Search generative AI”（默认包含、排除或继承），该控制控制 AI 概览和 AI 模式的资格；它不是一个排名信号或训练控制。除此之外，外观受标准预览/索引指令、`nosnippet`、`data-nosnippet`、`max-snippet`、`noindex`（与上述第三方 AI 爬虫 robots 控制不同）管理。来源：developers.google.com/search/docs/appearance/ai-features

**搜索代理（实时，而不仅仅是 WebMCP）：** Google 的“信息代理”在后台运行以监控主题，加上针对特定类别的代理浏览/调用（正在推出至美国用户，2026 年夏季），因此代理友好页面优化（真实的交互元素、可访问性树、布局稳定性）现在不仅对行动重要，而且对引用也重要。使用 `/seo agentic`（`seo-agentic` 子技能）进行审计，它还读取 Lighthouse 的 Agentic Browsing 分数。

---

## Google 更新关联

针对 AI 概览或 AI 模式可见性变化，首先检查日期产品更新和核心更新条目：
`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run seo_updates.py --kind product --kind core --json`。
将陈旧的账本（`freshness.stale`）视为不完整。

## 输出

生成 `GEO-ANALYSIS.md`，包含：

1. **GEO 准备分数：XX/100**
2. **平台细分**（Google AIO、ChatGPT、Perplexity）：仅对使用工具（例如 DataForSEO 或 SE Ranking）测量的平台给出分数；否则报告定性准备情况，并说明未测量
3. **AI 爬虫访问状态**——分别报告每个爬虫及其管理的能力。训练访问（`GPTBot`、`Google-Extended`、`CCBot`、`ClaudeBot`、`Applebot-Extended`）和搜索可引用性（`OAI-SearchBot`、`Googlebot`、`PerplexityBot`、`Claude-SearchBot`、`Applebot`）是不同的发现，永远不能合并为一条线。
4. **llms.txt 状态**（存在、缺失、建议）
5. **品牌提及分析**（维基百科、Reddit、YouTube、LinkedIn 上的存在）
6. **篇章级可引用性**（识别的自包含答案块；~130-170 字是一个启发式方法，而不是 Google 规则）
7. **服务器端渲染检查**（JavaScript 依赖分析）
8. **前 5 个最高影响变化**
9. **模式建议**（用于 AI 发现）
10. **内容重新格式化建议**（要重写的特定段落）

---

## 快速见效

1. 在前 60 字内添加“什么是 [主题]？”定义
2. 创建自包含的答案块（大约 130-170 字是一个常见启发式方法）
3. 添加基于问题的 H2/H3 标题
4. 包含带来源的具体统计数据
5. 添加发布/更新日期
6. 实施作者模式（为作者）
7. 在 robots.txt 中允许关键的 AI 爬虫

## 中等努力

1. 创建 `/llms.txt` 文件（可选：被 Google 搜索忽略；可能有助于其他 AI 爬虫）
2. 添加作者简介（带资质）+ 维基百科/LinkedIn 链接
3. 确保关键内容的服务器端渲染
4. 在 Reddit、YouTube 上建立实体存在
5. 添加带数据的比较表格
6. 实施FAQ部分（结构化，不是商业网站的 schema）

## 高影响

1. 创建原创研究/调查（独特的可引用性）
2. 为品牌/关键人物建立维基百科存在
3. 建立带内容提及的 YouTube 频道
4. 实施全面实体链接（跨平台 sameAs）
5. 开发独特的工具或计算器

## DataForSEO 集成（可选）

如果 DataForSEO MCP 工具可用，使用 `ai_optimization_chat_gpt_scraper` 检查目标查询的 ChatGPT 网络搜索返回结果（真实的 GEO 可见性检查），并使用 `ai_opt_llm_ment_search` 与 `ai_opt_llm_ment_top_domains` 跨 AI 平台进行 LLM 提及跟踪。

## 错误处理

| 情景 | 操作 |
|------|------|
| URL 不可达（DNS 故障、连接被拒绝） | 清晰地报告错误。不要猜测网站内容。建议用户验证 URL 并重试。 |
| AI 爬虫被 robots.txt 阻止 | 准确报告被阻止的爬虫和被允许的爬虫。提供启用 AI 搜索可见性的具体 robots.txt 指令。 |
| 未找到 llms.txt | 注明缺失（可选文件；Google 搜索忽略它）并提供一个可用于非 Google AI 爬虫的现成 llms.txt 模板。 |
| 未检测到结构化数据 | 报告差距并提供具体的模式建议（文章、组织、人物）以改善 AI 发现。 |

## FLOW 框架集成

对于提示引导的 AI 内容优化，使用 `/seo flow optimize <url>`，FLOW 的 21 个优化阶段提示在 GEO 的可引用性和结构分析的基础上，通过证据引导的 AI 提示进行补充。
