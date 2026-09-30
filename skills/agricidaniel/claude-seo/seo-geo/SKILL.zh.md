---
name: seo-geo
description: 审计并改进AI概述和答案引擎的内容，包括可引用性、实体清晰度、爬虫访问、品牌信号和段落结构。
---

# AI 搜索 / GEO 优化 (2026年5月)

## 主要来源：Google 的 AI 优化指南

Google 官方在 Search Central 文档中发布的立场：

> "从 Google 搜索的角度来看，针对生成式 AI 搜索进行优化就是针对搜索体验进行优化，因此**仍然是 SEO**。"

阅读 `references/google-ai-optimization-guide.md` 获取完整综合分析、辟谣清单（`llms.txt`、分段、AI 重述、提及农场，均被 Google 认为无效），以及内容质量的 Who/How/Why 测试。

审核应将 GEO 发现结果表述为**将 SEO 基础应用于 AI 搜索界面**，而不是作为独立的优化学科。当社区建议与 Google 的主要来源相矛盾时，应优先参考 Google，并在报告中注明矛盾之处。

## 关键数据

下方的第三方数据在 2026年9月23日未重新核实。引用时请务必注明其来源和日期，或直接省略。

| 指标 | 数值 | 来源 |
|------|-------|-------|
| AI 概览覆盖范围 | 每月超过 25 亿活跃用户，源自 2026年 Google I/O 大会主旨演讲报道；未在 Google 自有来源上确认；200 多个国家 | 第三方 I/O 报道 |
| AI 概览查询覆盖范围 | 查询的约 50%（第三方测量；各国差异） | 行业数据 |
| AI 模式月活跃用户 | 10 亿以上，源自 2026年 Google I/O 大会主旨演讲报道；未在 Google 自有来源上确认 | 第三方 I/O 报道 |
| AI 模式模型 | Google 经常升级（Gemini 3.5 Flash 于 2026年5月19日成为默认设置，此后已推出更新的 Flash 模型）；切勿将建议与特定模型绑定 | Google (blog.google) |
| AI 引用会话增长 | 527%（2025年1月至5月） | 第三方（归因于 SparkToro；未重新核实） |
| ChatGPT 周活跃用户 | 9 亿 | OpenAI |
| Perplexity 月查询量 | 5 亿以上 | Perplexity |

## 关键洞察：品牌提及 > 反向链接

**品牌提及与 AI 可见性相关性是反向链接的 3 倍。**
(Ahrefs 2025年12月对 7.5 万个品牌的调查)

| 信号 | 与 AI 引用的相关性 |
|------|------------------|
| YouTube 提及 | ~0.737（最强） |
| Reddit 提及 | 高 |
| 维基百科存在 | 高 |
| LinkedIn 存在 | 中等 |
| 域名评级（反向链接） | ~0.266（弱） |

**只有 11% 的域名**同时被 ChatGPT 和 Google AI 概览在相同查询中引用，因此平台特定优化至关重要。

---

## GEO 分析标准（更新）

### 1. 引用分数（25%）

**自包含的答案块**易于 AI 系统引用。第三方研究表明大约 130-170 字；这是一个可读性启发式方法，不是 Google 的要求（Google 的 AI 优化指南表示您无需为 AI 分段内容）。并且 **~44% 的 AI 引用来自页面的前 30%**（SE Ranking 研究），优先加载最易于引用、自包含的答案，而不是将其隐藏在页面下方。

**强信号：**
- 清晰、可引用的句子，包含具体事实/数据
- 自包含的答案块（无需上下文即可提取）
- 在章节前 40-60 字内直接回答
- 声明附有具体来源
- 定义遵循 "X 是..." 或 "X 指的是..." 模式
- 独特的数据点，其他地方找不到

**弱信号：**
- 模糊、笼统的陈述
- 无证据的观点
- 隐藏的结论
- 无具体数据点

### 2. 结构可读性（20%）

**92% 的 AI 概览引用来自前 10 名排名页面**，但 47% 来自排名低于第 5 的页面，显示出不同的选择逻辑。

**强信号：**
- 清晰的 H1->H2->H3 标题层次结构
- 基于问题的标题（匹配查询模式）
- 短段落（2-4 句话）
- 表格用于比较数据
- 有序/无序列表用于分步或多项内容
- FAQ 部分具有清晰的问答格式

**弱信号：**
- 没有结构的文本墙
- 不一致的标题层次结构
- 无列表或表格
- 信息隐藏在段落中

### 3. 多模态内容（15%）

多模态内容可以支持 AI 答案的选择（仅第三方声称；无主要来源提供具体数据）。

**检查：**
- 文本 + 相关图片
- 视频内容（嵌入或链接）
- 信息图表和图表
- 交互式元素（计算器、工具）
- 支持媒体的结构化数据

### 4. 权威性与品牌信号（20%）

**强信号：**
- 带有资质的作者署名
- 发布日期和最后更新日期
- **时效性**，内容在 3 个月内更有可能被 AI 答案引用；6 个月以上过时的页面会失去引用资格（SE Ranking，1.3 万次引用研究）。定期的刷新计划是 GEO 的高杠杆操作之一。
- 对原始来源的引用（研究、官方文档、数据）
- 组织资质和隶属关系
- 带有归属的专家引言
- 实体在维基百科、Wikidata 中的存在
- Reddit、YouTube、LinkedIn 上的提及

**弱信号：**
- 匿名作者
- 无日期
- 无来源引用
- 无跨平台品牌存在

### 5. 技术可访问性（20%）

**许多 AI 爬虫抓取原始 HTML 而不执行 JavaScript**（例如公共测试中的 GPTBot 和 PerplexityBot），而 Googlebot 渲染 JavaScript 并为 AI 概览和 AI 模式提供内容。服务器端渲染对所有爬虫都可见。

**检查：**
- 服务器端渲染（SSR）与客户端内容
- AI 爬虫在 robots.txt 中的访问权限
- llms.txt 存在（报告完整性的目的；它在此次评分中**不携带权重**，见 `references/llmstxt-evidence.md`）
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
| Claude-User | Anthropic | 代表用户浏览的 Claude（用户触发） | **是**（Anthropic：所有三个爬虫都遵守 robots.txt） |
| PerplexityBot | Perplexity | Perplexity AI 搜索（**不用于** 基础模型训练抓取） | 是 |
| Perplexity-User | Perplexity | 为用户问题抓取（用户触发） | 通常忽略 |
| CCBot | Common Crawl | 训练数据（通常被阻止） | 是 |
| Bytespider | ByteDance | TikTok/Douyin AI | 是 |
| cohere-ai | Cohere | Cohere 模型 | 是 |
| Google-Extended | Google | **仅 Gemini/Vertex 训练和基础**（**不是** Google 搜索） | 是 |
| Google-CloudVertexBot | Google | 所有者请求的 Vertex AI 代理抓取 | 是 |
| Google-Agent | Google | 用户触发的代理抓取（为用户进行代理浏览） | **否**（用户触发） |
| Google-GeminiNotebook | Google | 抓取用户添加的源 URL（已取代 `Google-NotebookLM`，支持至 2026年8月） | **否**（用户触发） |
| Google Messages | Google | 用户触发的抓取 | **否**（用户触发） |
| Applebot-Extended | Apple | **仅 Apple Intelligence / 生成式 AI 训练数据选择退出**（**不是** Siri、Spotlight 或 Safari 搜索；它本身不抓取，而是标记 Applebot 已抓取的内容） | 是 |

来源：[OpenAI 爬虫](https://platform.openai.com/docs/bots)、[Google 爬虫概述](https://developers.google.com/search/docs/crawling-indexing/overview-google-crawlers)、[Anthropic 爬虫支持文章](https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler)、[Apple Applebot-Extended 支持文章](https://support.apple.com/en-us/119829)。
Anthropic 当前的爬虫支持文章仅记录 ClaudeBot、Claude-User 和 Claude-SearchBot；它未列出 `anthropic-ai`，因此已删除先前未经核实的 `anthropic-ai` 行，而不是猜测。

**建议：** 允许 OAI-SearchBot、Claude-SearchBot 和 PerplexityBot 以实现 AI 搜索可见性。GPTBot、ClaudeBot、CCBot 和 Applebot-Extended 仅用于训练信号——根据许可偏好允许或阻止，而不是基于搜索可见性。

### 检查您正在提出的声明的正确爬虫

两对通常被混淆。**下表中每个声明只能由其自己的爬虫的 robots.txt 状态支持**——分别检查并分别报告。

| 您想要提出的声明 | 检查的爬虫 | 不支持此声明的爬虫 |
|---|---|---|
| "内容可在 ChatGPT 搜索中引用" | `OAI-SearchBot` | `GPTBot` |
| "内容可用于 OpenAI 模型训练" | `GPTBot` | `OAI-SearchBot` |
| "内容可用于 Gemini/Vertex 训练和基础" | `Google-Extended` | `Googlebot` |
| "内容有资格被 Google 搜索 / AI 概览" | `Googlebot` | `Google-Extended` |
| "内容可在 Claude 的搜索功能中引用" | `Claude-SearchBot` | `ClaudeBot` |
| "内容可用于 Anthropic 模型训练" | `ClaudeBot` | `Claude-SearchBot` |
| "内容可用于 Apple Intelligence 训练" | `Applebot-Extended` | `Applebot` |
| "内容可通过 Siri、Spotlight 或 Safari 搜索发现" | `Applebot` | `Applebot-Extended` |

- **`Google-Extended` 仅管理 Gemini 和 Vertex AI 训练和基础使用。它不影响普通 Google 搜索的包含，也不影响 AI 概览和 AI 模式的包含，这两者均来自 `Googlebot` 索引。** 永远不要将 `Google-Extended` 评分视为“Google 搜索准备就绪”信号，也永远不要引用被阻止的 `Google-Extended` 作为证据表明网站未包含在 Google 搜索中。
- **`OAI-SearchBot` 是决定 ChatGPT 搜索可引用性的爬虫。`GPTBot` 是 OpenAI 的独立训练爬虫。** 检查 `GPTBot` 访问权限并不能告诉您 ChatGPT 搜索是否可以引用该页面。一个阻止 `GPTBot` 但允许 `OAI-SearchBot` 的网站可以在 ChatGPT 搜索中完全被引用。
- **`Claude-SearchBot` 是决定 Claude 自身搜索功能可引用性的爬虫。`ClaudeBot` 是 Anthropic 的独立训练爬虫**（根据 Anthropic 的爬虫支持文章）。检查 `ClaudeBot` 访问权限并不能告诉您 Claude 搜索的可引用性，反之亦然；分别报告。
- **`Applebot-Extended` 是一个训练数据选择退出信号，而不是自己抓取页面的爬虫。** 根据 Apple 的支持文章，阻止 `Applebot-Extended` 会将网站从 Apple Intelligence / 生成式模型训练使用中排除，但只要允许 `Applebot` 本身，页面仍然可通过 Siri、Spotlight 和 Safari 发现。永远不要引用被阻止的 `Applebot-Extended` 作为证据表明网站未包含在 Apple 的搜索界面中。

报告中不要互换使用这些名称。在报告爬虫访问权限时，应指明检查了哪个特定的用户代理以及它管理的具体功能。

> **Google 的用户触发抓取通常忽略 robots.txt 规则**（Google-Agent、Google-GeminiNotebook、Google Messages）；OpenAI 表示 robots.txt 对 ChatGPT-User“可能不适用”，而 Anthropic 的 Claude-User 遵守它。robots.txt 无法阻止它们，应使用服务器端访问控制。Google 的规范爬虫/robots 参考已迁移到 **developers.google.com/crawling**（迁移于 2025年11月20日）；IP 范围文件现在位于 `/crawling/ipranges/`，`googlebot.json` 已更名为 `common-crawlers.json`。新兴：**Web Bot Auth**（RFC 9421）允许爬虫通过 `Signature-Agent` 头部 + 密钥目录进行身份验证（Google-Agent 使用）；反向 DNS 验证仍然是后备方案。

---

## llms.txt 标准

阅读 `references/llmstxt-evidence.md` 获取主要来源证据（Mueller、Illyes、SE Ranking 30 万域名研究、OtterlyAI 服务器日志审核），说明为什么 `/llms.txt` 目前不是主要 AI 搜索系统引用的杠杆。claude-seo 报告其存在，但未分配引用排名权重。

> **Google 现在明确声明这一点。** Google 的 AI 优化指南于 2026年5月15日引入并于 2026年6月15日澄清，指出 `llms.txt` 和其他 AI 文本文件对 Google 搜索不是必需的，也不会影响可见性或排名。它们可能仍然为非 Google 系统服务。永远不要建议 `llms.txt` 作为 Google 排名或引用杠杆。来源：
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
| **Google AI 概览** | 强相关排名，引用已排名良好的页面 | 传统 SEO + 段落优化 |
| **Google AI 模式**（Gemini 模型，经常升级） | 弱相关排名；更广泛的池（每个查询约 9 个域名引用，Ahrefs） | 不同界面：新鲜度、实体权威、排名 5 之后的可引用段落 |
| **ChatGPT** | 维基百科（47.9%）、Reddit（11.3%） | 实体存在、权威来源 |
| **Perplexity** | Reddit（46.7%）、维基百科 | 社区验证、讨论 |
| **Bing Copilot** | Bing 索引、权威网站 | Bing SEO、IndexNow |

> **两个 Google 引用引擎，而不是一个。** AI 模式和 AI 概览约 86% 的情况下得出相同结论，但引用相同 URL 的概率仅为 **13.7%**（Ahrefs 研究，54 万个查询对）。将它们视为独立的界面：在传统搜索中排名良好可让 AI 概览引用，但 AI 模式从更广泛的池中抽取，其中新鲜度和实体权威胜过原始排名。两者都要评分。
>
> **AI 模式也是一个预订界面（2026年8月27日）。** 航班价格跟踪带电子邮件提醒（180 多个国家和地区）、通过集成合作伙伴预订酒店、以及以点数或英里显示票价现在都在 AI 模式中进行。旅游和酒店客户应检查合作伙伴资格；这里没有记录的排名变化。
>
> **UX 现在统一，界面仍然独立。** 在 2026年 Google I/O 大会（2026年5月19日）上，Google 将 AI 概览和 AI 模式合并为“无缝的 AI 搜索体验”（问题 → AI 概览 → 在 AI 模式中进行后续）以及新的智能搜索框。*体验*是一个流程，但两个引用引擎在技术上仍然是独立的（不同的模型/链接集），继续评分两者。

### AI 搜索中的引用界面和控制（2026）

Google 在 AI 概览**和** AI 模式（2026年5月）中添加了许多 AI 引用/来源界面：

- **首选来源**，用户可以选择一个符合条件的域名或子域名，使其内容更有可能出现在该用户的“热门故事”中，并符合AI模式或AI概述中的首选徽章资格。这是一种**用户偏好**，而不是一个记录在案的通用排名信号。发布者可以提供Google的交互式按钮或深度链接，但不应承诺全站排名提升。自2026年9月18日起，文档还要求网站包含在搜索生成式AI功能中（搜索控制台“搜索生成式AI”控制），以在AI模式和AI概述中显示为首选来源。来源：developers.google.com/search/docs/appearance/preferred-sources
- **“高被引”徽章**，通过原创的一手报道获得，其他文章会引用这些内容。
- **社区观点**，提升Reddit/论坛/一手内容的影响力。
- 内联链接、桌面悬停**链接预览**和显眼的链接轮播。

**控制AI功能外观**：没有专门的AI退出文件，但自2026年8月31日起，每个网站都有一个搜索控制台控制项，“搜索生成式AI”（默认包含、排除或继承），该控制项控制AI概述和AI模式的资格；它不是排名信号也不是训练控制。除此之外，外观受标准预览/索引指令管理，`nosnippet`、`data-nosnippet`、`max-snippet`、`noindex`（与上述第三方AI爬虫robots控制不同）。来源：developers.google.com/search/docs/appearance/ai-features

**搜索代理（实时，不仅仅是WebMCP）**：Google的“信息代理”在后台运行以监控主题，并对特定类别进行代理式预订/呼叫（将于2026年夏季向美国用户推广），因此代理友好页面优化（真实的交互元素、可访问性树、布局稳定性）现在不仅对引用有影响，还对操作有影响。使用`/seo agentic`（`seo-agentic`子技能）进行审核，该技能还会读取Lighthouse的代理式浏览分数。

---

## Google更新关联

对于AI概述或AI模式可见性变化，首先检查日期产品和核心更新条目：
`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run seo_updates.py --kind product --kind core --json`。
将过时的账本（`freshness.stale`）视为不完整。

## 输出

生成`GEO-ANALYSIS.md`文件：

1. **GEO准备评分：XX/100**
2. **平台分解**（Google AIO、ChatGPT、Perplexity）：仅对使用工具测量的平台（例如DataForSEO或SE Ranking）给出评分；否则报告定性准备情况，并说明未测量
3. **AI爬虫访问状态** -- 分别报告每个爬虫及其管辖的能力。训练访问（`GPTBot`、`Google-Extended`、`CCBot`、`ClaudeBot`、`Applebot-Extended`）和搜索可引用性（`OAI-SearchBot`、`Googlebot`、`PerplexityBot`、`Claude-SearchBot`、`Applebot`）是不同的发现，绝不能合并到一行。
4. **llms.txt状态**（存在、缺失、建议）
5. **品牌提及分析**（维基百科、Reddit、YouTube、领英上的存在）
6. **段落级可引用性**（识别出的自包含答案块；~130-170字是一个启发式方法，不是Google规则）
7. **服务器端渲染检查**（JavaScript依赖分析）
8. **前5个最高影响变化**
9. **模式建议**（用于AI发现）
10. **内容重新格式化建议**（特定段落需要重写）

---

## 快速见效

1. 在前60个字内添加“什么是[主题]？”定义
2. 创建自包含答案块（约130-170字是一个常见启发式方法）
3. 添加基于问题的H2/H3标题
4. 包含具体数据并注明来源
5. 添加发布/更新日期
6. 对作者实施Person模式
7. 在robots.txt中允许关键AI爬虫

## 中等努力

1. 创建`/llms.txt`文件（可选：Google搜索忽略；可能有助于其他AI爬虫）
2. 添加作者简介并注明资质 + 维基百科/领英链接
3. 确保关键内容的服务器端渲染
4. 在Reddit、YouTube上建立实体存在
5. 添加数据对比表格
6. 实施FAQ部分（结构化，非商业网站的模式）

## 高影响

1. 创建原创研究/调查（独特可引用性）
2. 为品牌/关键人物建立维基百科存在
3. 建立YouTube频道并提及内容
4. 实施全面的实体链接（跨平台sameAs）
5. 开发独特工具或计算器

## DataForSEO集成（可选）

如果DataForSEO MCP工具可用，使用`ai_optimization_chat_gpt_scraper`检查ChatGPT对目标查询的网页搜索返回结果（真实的GEO可见性检查），并使用`ai_opt_llm_ment_search`与`ai_opt_llm_ment_top_domains`进行跨AI平台的LLM提及跟踪。

## 错误处理

| 情景 | 操作 |
|------|------|
| URL无法访问（DNS故障、连接拒绝） | 清晰地报告错误。不要猜测网站内容。建议用户验证URL并重试。 |
| AI爬虫被robots.txt阻止 | 精确报告被阻止的爬虫和允许的爬虫。提供具体的robots.txt指令以启用AI搜索可见性。 |
| 未找到llms.txt | 注明缺失（可选文件；Google搜索忽略），并提供一个用于非Google AI爬虫的现成llms.txt模板。 |
| 未检测到结构化数据 | 报告差距并提供具体的模式建议（文章、组织、人物）以改善AI发现性。 |

## FLOW框架集成

对于提示引导的AI内容优化，使用`/seo flow optimize <url>`，FLOW的21个优化阶段提示通过证据引导的AI提示补充GEO的可引用性和结构分析。
