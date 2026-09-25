# Valyu 最佳实践

本指南提供了使用 Valyu API 进行搜索、内容提取、AI 驱动的答案和深度研究任务的说明。

## 快速参考：选择正确的 API

使用此决策树选择合适的 Valyu API：

```
你需要什么？

├─ 跨多个来源查找信息
│  └─ 使用 Search API
│
├─ 从特定 URL 提取内容
│  └─ 使用 Contents API
│
├─ 获取带有引用的 AI 合成答案
│  └─ 使用 Answer API
│
├─ 生成全面的深度研究报告
│  └─ 使用 DeepResearch API
│
└─ 发现可用的数据来源
   └─ 使用 Datasources API
```

---

## ⚠️ 强制要求：使用官方 Valyu SDK 库

**关键：** 在编写使用 Valyu API 的代码时，你必须使用官方的 SDK 库。**绝对不要**对 Valyu API 端点进行原始 HTTP/fetch 调用。

### JavaScript/TypeScript: `valyu-js`

```bash
npm install valyu-js
# 或
pnpm add valyu-js
```

```typescript
import { Valyu } from 'valyu-js';

const valyu = new Valyu(process.env.VALYU_API_KEY);

// 现在可以使用 valyu.search()、valyu.contents()、valyu.answer()、valyu.deepResearch
```

### Python: `valyu`

```bash
pip install valyu
# 或
uv add valyu
```

```python
from valyu import Valyu

valyu = Valyu(api_key=os.environ.get("VALYU_API_KEY"))

# 现在可以使用 valyu.search()、valyu.contents()、valyu.answer()、valyu.deep_research
```

### 为什么使用 SDK 而不是原始 API 调用？

1. **类型安全** - 所有参数和响应的完整 TypeScript/Python 类型提示
2. **自动重试** - 建立的暂时性故障重试逻辑
3. **流支持** - 流式响应的适当异步迭代器支持
4. **错误处理** - 结构化错误类型和有用消息
5. **未来兼容性** - SDK 更新自动处理 API 变更

### ❌ 绝对不要这样做

```typescript
// 不要进行原始 fetch 调用
const response = await fetch('https://api.valyu.ai/v1/search', {
  method: 'POST',
  headers: {
    'x-api-key': apiKey,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ query: '...' })
});
```

### ✅ 始终这样做

```typescript
// 使用 SDK
import { Valyu } from 'valyu-js';

const valyu = new Valyu(process.env.VALYU_API_KEY);
const response = await valyu.search({ query: '...' });
```

---

## 1. 搜索 API

**目的：** 在网络、学术、医疗、交通、金融、新闻和专有来源中查找信息。

### 何时使用

- 查找任何主题的最新信息
- 学术研究（arXiv、PubMed、bioRxiv、medRxiv）
- 金融数据（SEC 文件、盈利报告、股票数据）
- 新闻监测和时事
- 医疗保健数据（临床试验、药品标签）
- 预测市场（Polymarket、Kalshi）
- 交通（英国国家铁路、全球航运）

### 基本用法

```typescript
const response = await valyu.search({
  query: "transformer architecture attention mechanism 2024",
  searchType: "all",
  maxNumResults: 10
});
```

### 搜索类型

| 类型 | 用于 |
|------|------|
| `all` | 所有 - 网络、学术、金融、专有 |
| `web` | 仅限一般互联网内容 |
| `proprietary` | 许可的学术论文和研究 |
| `news` | 新闻文章和时事 |

### 关键参数

| 参数 (TS/JS) | 参数 (Python) | 目的 | 示例 |
|-------------------|-------------------|---------|---------|
| `query` | `query` | 搜索查询（少于 400 个字符） | `"CRISPR gene editing 2024"` |
| `searchType` | `search_type` | 来源范围 | `"all"`, `"web"`, `"proprietary"`, `"news"` |
| `maxNumResults` | `max_num_results` | 结果数量（1-20） | `10` |
| `includedSources` | `included_sources` | 限制为特定来源 | `["valyu/valyu-arxiv", "valyu/valyu-pubmed"]` |
| `startDate` / `endDate` | `start_date` / `end_date` | 日期过滤 | `"2024-01-01"` |
| `relevanceThreshold` | `relevance_threshold` | 最小相关性（0-1） | `0.7` |

### 特定领域搜索模式

**学术研究：**
```typescript
await valyu.search({
  query: "CRISPR therapeutic applications clinical trials",
  searchType: "proprietary",
  includedSources: ["valyu/valyu-arxiv", "valyu/valyu-pubmed", "valyu/valyu-biorxiv"],
  startDate: "2024-01-01"
});
```

**金融分析：**
```typescript
await valyu.search({
  query: "Apple revenue Q4 2024 earnings",
  searchType: "all",
  includedSources: ["valyu/valyu-sec-filings", "valyu/valyu-earnings-US"]
});
```

**新闻监测：**
```typescript
await valyu.search({
  query: "AI regulation EU",
  searchType: "news",
  startDate: "2024-06-01",
  countryCode: "EU"
});
```

### 搜索配方

有关详细模式，请参阅：
- [基本搜索模式](references/search-recipes/basic-search-all.md)
- [学术搜索](references/search-recipes/academic-search.md)
- [金融搜索](references/search-recipes/finance-search.md)
- [新闻搜索](references/search-recipes/news-search.md)
- [医疗保健搜索](references/search-recipes/healthcare-and-bio-search.md)

---

## 2. 内容 API

**目的：** 从网页中提取干净、结构化的内容，以优化 LLM 处理。

### 何时使用

- 将网页转换为干净的 Markdown
- 提取文章文本以进行摘要
- 解析文档以用于 RAG 系统
- 从产品页面提取结构化数据
- 处理学术论文

### 基本用法

```typescript
const response = await valyu.contents({
  urls: ["https://example.com/article"]
});
```

### 带摘要

```typescript
const response = await valyu.contents({
  urls: ["https://arxiv.org/abs/2401.12345"],
  summary: "Extract key findings in 3 bullet points"
});
```

### 结构化提取（JSON Schema）

```typescript
const response = await valyu.contents({
  urls: ["https://example.com/product"],
  summary: {
    type: "object",
    properties: {
      product_name: { type: "string" },
      price: { type: "number" },
      features: { type: "array", items: { type: "string" } }
    },
    required: ["product_name", "price"]
  }
});
```

### 关键参数

| 参数 (TS/JS) | 参数 (Python) | 目的 | 示例 |
|-------------------|-------------------|---------|---------|
| `urls` | `urls` | 要处理的 URL（1-10） | `["https://example.com"]` |
| `responseLength` | `response_length` | 内容长度 | `"short"`, `"medium"`, `"large"`, `"max"` |
| `extractEffort` | `extract_effort` | 提取质量 | `"normal"`, `"high"`, `"auto"` |
| `summary` | `summary` | AI 摘要 | `true`, `"instructions"`, 或 JSON schema |
| `screenshot` | `screenshot` | 捕获屏幕截图 | `true` |

### 内容配方

有关详细模式，请参阅：
- [基本内容提取](references/content-recipes/basic-content-extraction-from-web.md)
- [带摘要提取](references/content-recipes/basic-content-extraction-from-web-with-summary.md)
- [结构化提取](references/content-recipes/structured-content-extraction-from-web.md)
- [研究论文提取](references/content-recipes/extract-content-from-research-paper.md)

---

## 3. 答案 API

**目的：** 获取基于实时搜索结果的 AI 驱动的答案，并附带引用。

### 何时使用

- 需要当前信息综合的问题
- 多来源事实验证
- 技术文档问题
- 需要引用来源的研究
- 从搜索结果中提取结构化数据

### 基本用法

```typescript
const response = await valyu.answer({
  query: "What are the latest developments in quantum computing?"
});
```

### 带快速模式（较低延迟）

```typescript
const response = await valyu.answer({
  query: "Current Bitcoin price and 24h change",
  fastMode: true
});
```

### 带自定义指令

```typescript
const response = await valyu.answer({
  query: "Compare React and Vue for enterprise applications",
  systemInstructions: "Provide a balanced comparison with pros and cons. Format as a comparison table."
});
```

### 带流式传输

```typescript
const stream = await valyu.answer({
  query: "Explain transformer architecture",
  streaming: true
});

for await (const chunk of stream) {
  // 处理：search_results、content、metadata、done、error
  console.log(chunk);
}
```

### 结构化输出

```typescript
const response = await valyu.answer({
  query: "Apple Q4 2024 financial highlights",
  structuredOutput: {
    type: "object",
    properties: {
      revenue: { type: "string" },
      growthRate: { type: "string" },
      keyHighlights: { type: "array", items: { type: "string" } }
    }
  }
});
```

### 关键参数

| 参数 (TS/JS) | 参数 (Python) | 目的 | 示例 |
|-------------------|-------------------|---------|---------|
| `query` | `query` | 要回答的问题 | `"What is quantum computing?"` |
| `fastMode` | `fast_mode` | 降低延迟 | `true` |
| `systemInstructions` | `system_instructions` | AI 指令 | `"Be concise"` |
| `structuredOutput` | `structured_output` | JSON schema | `{type: "object", ...}` |
| `streaming` | `streaming` | 启用 SSE 流式传输 | `true` |
| `dataMaxPrice` | `data_max_price` | 美元限制 | `1.0` |

### 答案配方

有关详细模式，请参阅：
- [基本答案](references/answer-recipes/basic-answer.md)
- [快速模式](references/answer-recipes/answer-with-fast-mode.md)
- [流式传输](references/answer-recipes/answer-with-streaming.md)
- [自定义指令](references/answer-recipes/answer-with-custom-instructions.md)

---

## 4. DeepResearch API

**目的：** 生成包含详细分析和引用的全面研究报告。

### 何时使用

- 市场分析
- 文献综述
- 竞争情报
- 技术深度分析
- 需要跨来源综合的主题

### 研究模式

| 模式 | 持续时间 | 适用于 |
|------|----------|----------|
| `fast` | ~5 分钟 | 快速查找、简单问题 |
| `standard` | ~10-20 分钟 | 平衡研究（最常见） |
| `heavy` | ~90 分钟 | 全面分析、复杂主题 |

### 创建研究任务

```typescript
const task = await valyu.deepResearch.create({
  query: "AI chip market competitive landscape 2024",
  model: "standard"
});
// 返回：{ deepresearch_id: "abc123", status: "queued" }
```

### 检查完成状态

```typescript
const status = await valyu.deepResearch.getStatus(task.deepresearch_id);
// status: "queued" | "running" | "completed" | "failed" | "cancelled"

if (status.status === "completed") {
  console.log(status.output);  // Markdown 报告
  console.log(status.sources); // 引用来源
  console.log(status.pdf_url); // PDF 下载链接
}
```

### 关键参数

| 参数 (TS/JS) | 参数 (Python) | 目的 | 示例 |
|-------------------|-------------------|---------|---------|
| `query` | `query` | 研究问题 | `"AI market trends 2024"` |
| `model` | `model` | 研究深度 | `"fast"`, `"standard"`, `"heavy"` |
| `outputFormat` | `output_format` | 报告格式 | `"markdown"`, `"pdf"` |
| `includedSources` | `included_sources` | 来源过滤 | `["valyu/valyu-arxiv", "techcrunch.com"]` |
| `startDate` / `endDate` | `start_date` / `end_date` | 日期范围 | `"2024-01-01"` |

### DeepResearch 配方

有关详细模式，请参阅：
- [快速研究](references/deepresearch-recipes/create-a-fast-research-task-and-await-completion.md)
- [标准研究](references/deepresearch-recipes/create-a-standard-research-task-and-await-completion.md)
- [深度研究](references/deepresearch-recipes/create-a-heavy-research-task-and-await-completion.md)

---

## 5. 查询编写最佳实践

### 核心原则

1. **具体** - 使用领域术语
2. **简洁** - 保持查询少于 400 个字符
3. **专注** - 每个查询一个主题
4. **添加约束** - 包括时间范围、来源类型

### 查询结构

| 元素 | 描述 | 示例 |
|---------|-------------|---------|
| **意图** | 你需要什么 | "最新进展" vs "概述" |
| **领域** | 主题术语 | "transformer architecture" |
| **约束** | 过滤器 | "2024", "peer-reviewed" |
| **来源类型** | 去哪里查找 | 学术论文、SEC 文件 |

### 好的 vs 坏的查询

```
BAD:  "I want to know about AI"
GOOD: "transformer attention mechanism survey 2024"

BAD:  "Apple financial information"
GOOD: "Apple revenue growth Q4 2024 earnings SEC filing"

BAD:  "gene editing research"
GOOD: "CRISPR off-target effects therapeutic applications 2024"
```

### 分割复杂请求

```
# 不要这样做
"Tesla stock performance, new products, and Elon Musk statements"

# 这样做
查询 1: "Tesla stock performance Q4 2024"
查询 2: "Tesla Cybertruck production updates 2024"
查询 3: "Tesla FSD autonomous driving progress"
```

### 来源过滤

使用 `includedSources` 进行领域权威性：
​
金融研究集合。一些要包含的来源：
- `valyu/valyu-sec-filings` - SEC 监管文件
- `valyu/valyu-stocks` - 股票市场数据
- `valyu/valyu-earnings-US` - 盈利报告
- `reuters.com` - 金融新闻
- `bloomberg.com` - 市场分析
​
医疗研究集合。一些要包含的来源：
- `valyu/valyu-pubmed` - 医学文献
- `valyu/valyu-clinical-trials` - 临床试验数据
- `valyu/valyu-drug-labels` - FDA 药品信息
- `nejm.org` - New England Journal of Medicine
- `thelancet.com` - The Lancet
​
技术文档集合。一些要包含的来源：
- `docs.aws.amazon.com` - AWS 文档
- `cloud.google.com/docs` - Google Cloud 文档
- `learn.microsoft.com` - Microsoft 文档
- `kubernetes.io/docs` - Kubernetes 文档
- `developer.mozilla.org` - MDN Web Docs

```javascript
// 学术
includedSources: ["valyu/valyu-arxiv", "valyu/valyu-pubmed", "nature"]

// 金融
includedSources: ["valyu/valyu-sec-filings", "bloomberg.com", "reuters.com"]

// 科技新闻
includedSources: ["techcrunch.com", "theverge.com", "arstechnica.com"]
```

有关完整提示指南，请参阅 [references/prompting.md](references/prompting.md)。

---

## 6. 常见工作流

### 研究工作流

```typescript
// 1. 快速搜索以找到来源
const searchResults = await valyu.search({
  query: "CRISPR therapeutic applications",
  searchType: "proprietary",
  maxNumResults: 20
});

// 2. 从前三个结果中提取关键内容
const contents = await valyu.contents({
  urls: searchResults.results.slice(0, 3).map(r => r.url),
  summary: "Extract key findings"
});

// 3. 深度分析以生成全面报告
const research = await valyu.deepResearch.create({
  query: "CRISPR therapeutic applications comprehensive review",
  model: "heavy"
});
```

### 金融分析工作流

```typescript
// 1. 获取 SEC 文件
const filings = await valyu.search({
  query: "Apple 10-k 2024",
  includedSources: ["valyu/valyu-sec-filings"]
});

// 2. 快速综合
const summary = await valyu.answer({
  query: "Apple Q4 2024 financial highlights",
  fastMode: true
});

// 3. 结构化提取
const metrics = await valyu.answer({
  query: "Apple financial metrics 2024",
  structuredOutput: {
    type: "object",
    properties: {
      revenue: { type: "string" },
      netIncome: { type: "string" },
      growthRate: { type: "string" }
    }
  }
});
```

---

## 7. 可用数据来源

Valyu 提供对 25+ 专用数据集的访问：

| 类别 | 示例 |
|----------|----------|
| **学术** | arXiv (2.5M+ 论文), PubMed (37M+), bioRxiv, medRxiv |
| **金融** | SEC 文件, 盈利记录, 股票数据, 加密货币 |
| **医疗保健** | 临床试验, DailyMed, PubChem, 药品标签, ChEMBL, DrugBank, Open Target, WHO ICD |
| **经济** | FRED, BLS, 世界银行, 美国财政部, Destatis |
| **预测** | Polymarket, Kalshi |
| **专利** | 美国专利数据库 |
| **交通** | 英国铁路, 航运跟踪 |

有关完整数据源参考，请参阅 [references/datasources.md](references/datasources.md)。

---

## 8. API 参考

有关完整的 API 文档，包括所有参数、响应结构和错误代码，请参阅 [references/api-guide.md](references/api-guide.md)。

---

## 9. 集成指南

特定平台的集成文档：

- [Anthropic Claude](references/integrations/anthropic.md)
- [OpenAI](references/integrations/openai.md)
- [Vercel AI SDK](references/integrations/vercel-ai-sdk.md)
- [LangChain](references/integrations/langchain.md)
- [LlamaIndex](references/integrations/llamaindex.md)
- [MCP Server](references/integrations/mcp-server.md)

---

## 其他资源

- [所有配方索引](references/recipes.md)
- [设计理念](references/design-philosophy.md)
- [提示指南](references/prompting.md)
- [完整 API 参考](references/api-guide.md)
