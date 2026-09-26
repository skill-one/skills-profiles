# 策略：GEO（生成式引擎优化）

为AI搜索可见性提供GEO/AEO策略指南。GEO针对ChatGPT、Claude、Perplexity和AI搜索摘要（Google AI概览、Bing Copilot、Yandex AI）进行内容优化，以在AI生成的答案中被引用，而不是在传统SERP中排名。参见**serp-features**了解AI搜索作为SERP功能；**featured-snippet**了解与AI概览重叠的摘要优化。

**调用时**：在**首次使用**时，如果有帮助，先用1-2句话说明此技能涵盖的内容及其重要性，然后提供主要输出。在**后续使用**或用户要求跳过时，直接提供主要输出。

## 范围

- **GEO** = 生成式引擎优化
- **AEO** = 答案引擎优化
- **LLMO** = 大型语言模型优化
- **AIO** = 人工智能优化

所有这些都指向同一个目标：在AI助手回答中提高可见性。

## GEO与SEO

| 维度 | SEO | GEO |
|-------|-----|-----|
| **目标** | 搜索结果中的排名 | AI答案中的引用 |
| **用户路径** | 点击→访问→转化 | 原地获取答案；可能不会访问 |
| **内容** | 全页优化 | 清晰、可引用的段落 |
| **指标** | 点击量、流量 | 引用量、品牌提及 |
| **平台** | Google、Bing、Yandex（自然搜索） | AI概览、Copilot、Yandex AI、ChatGPT、Perplexity |

**两者都很重要**：创建既排名又可被引用的内容。AI搜索摘要（AI概览、Copilot、Yandex AI）是**SERP功能**——参见**serp-features**。当SERP功能导致**零点击**（用户无需点击即可获得答案）时，引用成为主要价值；优化目标应为被引用，而不仅仅是排名。

## AI搜索平台（SERP功能+独立平台）

| 平台 | 类型 | 来源选择 | 优化重点 |
|------|------|------------------|---------------------|
| **Google AI概览** | SERP功能 | 顶部10-12个自然搜索结果；Gemini；偏好较旧的域名（49%超过15年） | 传统SEO；结构化数据；可引用的段落 |
| **Bing Copilot搜索** | SERP功能 | Bing索引；GPT-4；与Google的域名重叠率为9.81%；偏好较新的域名（18.85%）；LinkedIn信号用于B2B可见性 | Bing优化；LinkedIn存在感；结构化内容 |
| **Yandex Search with AI / Neuro** | SERP功能 | 实时Yandex搜索；YandexGPT；以俄罗斯为中心 | Yandex索引；俄罗斯内容；引用来源 |
| **Perplexity** | 独立平台 | 200B+ URL索引；独立爬取；偏好时效性、语义一致性 | 内容新鲜度；语义标记；中端网站机会 |
| **ChatGPT（网络搜索）** | 独立平台 | GPTbot；高权威性、频繁更新、适合LLM；偏好较旧的域名（45.8%） | 反向链接；结构化数据；权威信号 |
| **Claude（网络搜索）** | 独立平台 | 未公开披露 | 专注于通用爬取性和清晰的结构化内容 |

**引用行为**：AI概览引用的CTR比同等自然搜索结果高20-35%。Copilot：最短的回答，最少的链接（约3.13/回答）。Perplexity：突出的URL引用，高可追踪性。[Geneo](https://geneo.app/blog/chatgpt-vs-perplexity-vs-google-ai-overview-geo-comparison/)，[GEO AIO](https://geoaiomarketing.com/how-bing-copilot-selects-sources-compared-to-perplexity/)

**平台流量背景**：在独立AI工具中，ChatGPT占据60%以上的独立Gen AI流量，Gemini占据20%以上，而Claude、Perplexity和Grok各占2-4%左右。这些工具直接触达用户。SERP功能（AI概览、Copilot）通过现有搜索流程触达用户，而不是作为独立目的地。按比例分配优化工作。

## GEO工作原理（RAG与搜索供应）

GEO通过**RAG（检索增强生成）**运作——AI工具首先检索内容，然后生成答案。检索供应类型因平台而异，并决定哪些内容被引用。

### 检索供应类型

| 类型 | 描述 | 平台 |
|------|------------|-----------|
| **自建索引** | 平台维护自己的爬取和搜索索引 | Perplexity（200B+ URL索引，PerplexityBot）；ChatGPT（OAI-SearchBot索引） |
| **绑定搜索引擎** | 平台使用固定的第一方搜索API | Copilot（Bing）；Google AI概览/AI模式（Google搜索+查询扩展） |
| **第三方API** | 平台签约第三方搜索API | Claude for Government（Brave Search API）；使用Tavily、Exa、You.com等较小AI工具 |
| **混合** | 自建+外部API的组合 | ChatGPT（OAI-SearchBot+可能的搜索合作伙伴）；Claude Web Search（供应商未公开披露） |

### 平台检索及影响

| 平台 | 主要供应 | 战略影响 |
|----------|---------------|----------------------|
| **Google AI概览/AI模式** | Google搜索（查询扩展） | 强大的传统SEO+结构化数据是最可靠的路径 |
| **Bing Copilot** | Bing索引 | 需要Bing索引；LinkedIn信号用于B2B可见性 |
| **ChatGPT（网络搜索）** | OAI-SearchBot+合作伙伴 | 高权威性、频繁更新的内容受青睐；反向链接很重要 |
| **Perplexity** | 专有爬取 | 内容新鲜度；语义一致性；中端网站有机会 |
| **Claude（网络搜索）** | 未公开披露 | 专注于通用爬取性和清晰的结构化内容 |

**第三方搜索API**（Tavily、Exa、You.com、Brave Search API）为较小AI工具和自定义代理提供支持。可通过标准网络搜索爬取和索引的内容通过其供应索引到达这些API。**核心模型训练**（长、昂贵、不广泛可操作）：专注于RAG优化。

## AI爬虫与发现

AI爬虫分为三类，对内容策略有不同影响：

| 类型 | 目的 | 示例 | 影响 |
|------|---------|---------|-------------|
| **训练爬虫** | 收集模型训练数据 | GPTBot、ClaudeBot、Google-Extended、Meta爬虫 | 通过robots.txt阻止可防止训练数据使用；**不**影响同一供应商的实时搜索/检索 |
| **索引/RAG爬虫** | 构建用于检索的搜索索引 | OAI-SearchBot、PerplexityBot、Claude-SearchBot、Bytespider（Cohere）、AppleBot | **必须允许**用于基于RAG的AI引用；对GEO至关重要 |
| **实时爬虫** | 查询时按需获取内容 | ChatGPT-User（通过网络搜索选择加入） | 内容必须无需登录即可访问；付费墙可能阻止引用 |

**内容发现**：“推送”提交主要支持Bing IndexNow。Google的索引API仅限于JobPosting和BroadcastEvent页面（不包括一般内容）。OpenAI、Anthropic、Perplexity、xAI、Meta和DeepSeek**不**提供公共提交门户——它们的爬虫通过标准爬取和站点地图发现内容。

AI爬虫通常**不**执行JavaScript——关键内容必须在初始HTML中。参见**rendering-strategies**了解SSR、SSG、CSR；**site-crawlability**了解AI爬虫优化；**robots-txt**了解允许/阻止决策。[Vercel/MERJ研究](https://vercel.com/blog/the-rise-of-the-ai-crawler)（2024）

## 内容最佳实践

| 实践 | 目的 |
|----------|---------|
| **直接回答格式** | 以清晰段落回答特定问题 |
| **实体信号** | 清晰的品牌、产品、作者身份；参见**entity-seo** |
| **可引用段落** | 每个段落独立可理解 |
| **分发** | 网站、**YouTube**（Google在搜索中优先考虑YouTube；AI概览中约78%的社交媒体引用来自YouTube+Reddit）、论坛、Reddit——深思熟虑的评论可能超过博客文章 |

### 文章级GEO

对于博客文章和文章，为AI引用构建内容。研究发现，具有TL;DR、结构化格式和清晰答案的内容被AI引擎引用得更多。

| 元素 | 指导方针 |
|---------|-----------|
| **TL;DR或关键要点** | 选择其一：**TL;DR** = 50-100字的粗体摘要段落；**关键要点** = 5-7个要点；位于引言之后 |
| **QAE模式** | 问题（H2）→ 回答（2句话）→ 证据（数据、示例、列表） |
| **先回答** | 每个H2后40-60字直接回答 |
| **回答段落** | 每个部分100-200字；直接回答+上下文+证据+细微差别 |
| **结构化格式** | 列表、表格、编号步骤增加引用率 |

参见**article-content**了解内容创作；**article-page-generator**了解页面结构。

## 寄生SEO与高权威平台

**寄生SEO** = 在高权威平台上发布内容，利用其域名强度进行排名和AI引用。参见**parasite-seo**了解完整策略。

**GitHub**：二级技术权威；非常高的AI引用。参见**github**了解仓库、README、Pages、gists、awesome lists。

**YouTube**：Google在搜索中优先考虑YouTube；YouTube在AI概览中的引用激增25.21%。长视频教学和视觉演示视频占主导地位。参见**youtube-seo**了解频道和视频优化；**video-optimization**了解嵌入视频的网站SEO。

**Grokipedia**：xAI的AI百科全书；ChatGPT、Perplexity、Copilot引用它。参见**grokipedia-recommendations**了解添加推荐或链接。提供真正有用的内容；避免操纵性放置（Google站点声誉滥用政策）。

## 工具

- GEO跟踪和优化工具，用于测量AI引用和可见性

## 关键洞察

ChatGPT流量转化率显著高于Google搜索——研究显示，不同行业提升率为2倍至9倍。AI工具用户意图更明确，但结果因垂直领域而异。

## 输出格式

- **内容结构**，用于AI引用
- **实体**优化；参见**entity-seo**
- **分发**策略
- **测量**方法

## 相关技能

- **site-crawlability**：AI爬虫优化；URL/重定向管理
- **rendering-strategies**：SSR、SSG、CSR；为AI爬虫准备的初始HTML内容
- **robots-txt**：AI爬虫允许/阻止（GPTBot、ClaudeBot、PerplexityBot）
- **parasite-seo**：寄生SEO策略；高权威平台用于GEO
- **github**：GitHub用于GEO；仓库、README；二级技术权威
- **youtube-seo**：YouTube优化；GEO分发；Google优先考虑YouTube
- **serp-features**：**强相关**——AI概览、Bing Copilot、Yandex AI；平台比较
- **featured-snippet**：片段优化；与AI概览重叠
- **entity-seo**：实体信号；组织、人物模式；GEO引用
- **article-content**：文章正文创作；TL;DR、关键要点、QAE模式
- **article-page-generator**：文章页面结构；模式；布局
- **faq-page-generator**：GEO的FAQ结构；可引用的问答块；初始HTML内容
- **howto-section-generator**：HowTo步骤部分；可引用的有序程序；HowTo JSON-LD
