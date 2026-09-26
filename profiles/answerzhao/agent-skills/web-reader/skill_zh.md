# Web Reader 技能

本技能指导使用 z-ai-web-dev-sdk 包实现网页阅读和内容提取功能，使应用程序能够以编程方式获取和处理网页内容。

## 技能路径

**技能位置**: `{project_path}/skills/web-reader`

此技能位于您项目的上述路径。

**参考脚本**: 示例测试脚本位于 `{Skill Location}/scripts/` 目录中，供快速测试和参考。参见 `{Skill Location}/scripts/web-reader.ts` 获取一个工作示例。

## 概述

Web Reader 允许您构建可以从网页中提取内容、获取文章元数据并处理 HTML 内容的应用程序。API 自动处理内容提取，从任何网页 URL 提供干净、结构化的数据。

**重要提示**: z-ai-web-dev-sdk 必须仅在后端代码中使用。切勿在客户端代码中使用它。

## 前置条件

z-ai-web-dev-sdk 包已安装。按以下示例导入它。

## CLI 使用（适用于简单任务）

对于简单的网页内容提取，您可以使用 z-ai CLI 而不是编写代码。这对于快速内容抓取、测试 URL 或简单自动化任务很理想。

### 基本页面阅读

```bash
# 从网页提取内容
z-ai function --name "page_reader" --args '{"url": "https://example.com"}'

# 使用简短选项
z-ai function -n page_reader -a '{"url": "https://www.example.com/article"}'
```

### 保存页面内容

```bash
# 将提取的内容保存到 JSON 文件
z-ai function \
  -n page_reader \
  -a '{"url": "https://news.example.com/article"}' \
  -o page_content.json

# 提取并保存博客文章
z-ai function \
  -n page_reader \
  -a '{"url": "https://blog.example.com/post/123"}' \
  -o blog_post.json
```

### 常见用例

```bash
# 提取新闻文章
z-ai function \
  -n page_reader \
  -a '{"url": "https://news.site.com/breaking-news"}' \
  -o news.json

# 阅读文档页面
z-ai function \
  -n page_reader \
  -a '{"url": "https://docs.example.com/getting-started"}' \
  -o docs.json

# 抓取博客内容
z-ai function \
  -n page_reader \
  -a '{"url": "https://techblog.com/ai-trends-2024"}' \
  -o blog.json

# 提取研究文章
z-ai function \
  -n page_reader \
  -a '{"url": "https://research.org/papers/quantum-computing"}' \
  -o research.json
```

### CLI 参数

- `--name, -n`: **必需** - 函数名称（使用 "page_reader"）
- `--args, -a`: **必需** - JSON 参数对象，包含：
  - `url` (字符串，必需): 要读取的网页 URL
- `--output, -o <path>`: 可选 - 输出文件路径（JSON 格式）

### 响应结构

CLI 返回一个包含以下内容的 JSON 对象：
- `title`: 页面标题
- `html`: 主要内容 HTML
- `text`: 纯文本内容
- `publish_time`: 发布时间戳（如果可用）
- `url`: 原始 URL
- `metadata`: 额外的页面元数据

### 示例响应

```json
{
  "title": "机器学习入门",
  "html": "<article><h1>机器学习入门</h1><p>机器学习是...</p></article>",
  "text": "机器学习入门\n\n机器学习是...",
  "publish_time": "2024-01-15T10:30:00Z",
  "url": "https://example.com/ml-intro",
  "metadata": {
    "author": "John Doe",
    "description": "全面的机器学习指南"
  }
}
```

### 处理多个 URL

```bash
# 创建一个简单的脚本来处理多个 URL
for url in \
  "https://site1.com/article1" \
  "https://site2.com/article2" \
  "https://site3.com/article3"
do
  filename=$(echo $url | md5sum | cut -d' ' -f1)
  z-ai function -n page_reader -a "{\"url\": \"$url\"}" -o "${filename}.json"
done
```

### 何时使用 CLI 与 SDK

**使用 CLI 的情况**:
- 快速内容提取
- 测试 URL 可访问性
- 简单的网页抓取任务
- 一次性内容检索

**使用 SDK 的情况**:
- 批量 URL 处理与自定义逻辑
- 与网页应用程序集成
- 复杂的内容处理管道
- 具有错误处理的生产品应用程序

## 工作原理

Web Reader 使用 `page_reader` 函数执行以下操作：
1. 获取网页内容
2. 提取主要文章内容和元数据
3. 解析和清理 HTML
4. 返回包括标题、内容和发布时间在内的结构化数据

## 基本网页阅读实现

### 简单页面阅读

```javascript
import ZAI from 'z-ai-web-dev-sdk';

async function readWebPage(url) {
  try {
    const zai = await ZAI.create();

    const result = await zai.functions.invoke('page_reader', {
      url: url
    });

    console.log('标题:', result.data.title);
    console.log('URL:', result.data.url);
    console.log('发布:', result.data.publishedTime);
    console.log('HTML 内容:', result.data.html);
    console.log('使用的 token 数量:', result.data.usage.tokens);

    return result.data;
  } catch (error) {
    console.error('页面阅读失败:', error.message);
    throw error;
  }
}

// 使用
const pageData = await readWebPage('https://example.com/article');
console.log('页面标题:', pageData.title);
```

### 仅提取文章文本

```javascript
import ZAI from 'z-ai-web-dev-sdk';

async function extractArticleText(url) {
  const zai = await ZAI.create();

  const result = await zai.functions.invoke('page_reader', {
    url: url
  });

  // 将 HTML 转换为纯文本（基本方法）
  const plainText = result.data.html
    .replace(/<[^>]*>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  return {
    title: result.data.title,
    text: plainText,
    url: result.data.url,
    publishedTime: result.data.publishedTime
  };
}

// 使用
const article = await extractArticleText('https://news.example.com/story');
console.log(article.title);
console.log(article.text.substring(0, 200) + '...');
```

### 读取多个页面

```javascript
import ZAI from 'z-ai-web-dev-sdk';

async function readMultiplePages(urls) {
  const zai = await ZAI.create();
  const results = [];

  for (const url of urls) {
    try {
      const result = await zai.functions.invoke('page_reader', {
        url: url
      });

      results.push({
        url: url,
        success: true,
        data: result.data
      });
    } catch (error) {
      results.push({
        url: url,
        success: false,
        error: error.message
      });
    }
  }

  return results;
}

// 使用
const urls = [
  'https://example.com/article1',
  'https://example.com/article2',
  'https://example.com/article3'
];

const pages = await readMultiplePages(urls);
pages.forEach(page => {
  if (page.success) {
    console.log(`✓ ${page.data.title}`);
  } else {
    console.log(`✗ ${page.url}: ${page.error}`);
  }
});
```

## 高级用例

### 网页内容分析器

```javascript
import ZAI from 'z-ai-web-dev-sdk';

class WebContentAnalyzer {
  constructor() {
    this.cache = new Map();
  }

  async initialize() {
    this.zai = await ZAI.create();
  }

  async readPage(url, useCache = true) {
    // 检查缓存
    if (useCache && this.cache.has(url)) {
      console.log('返回缓存结果:', url);
      return this.cache.get(url);
    }

    // 获取最新内容
    const result = await this.zai.functions.invoke('page_reader', {
      url: url
    });

    // 缓存结果
    if (useCache) {
      this.cache.set(url, result.data);
    }

    return result.data;
  }

  async getPageMetadata(url) {
    const data = await this.readPage(url);

    return {
      title: data.title,
      url: data.url,
      publishedTime: data.publishedTime,
      contentLength: data.html.length,
      wordCount: this.estimateWordCount(data.html)
    };
  }

  estimateWordCount(html) {
    const text = html.replace(/<[^>]*>/g, ' ');
    const words = text.split(/\s+/).filter(word => word.length > 0);
    return words.length;
  }

  async comparePages(url1, url2) {
    const [page1, page2] = await Promise.all([
      this.readPage(url1),
      this.readPage(url2)
    ]);

    return {
      page1: {
        title: page1.title,
        wordCount: this.estimateWordCount(page1.html),
        published: page1.publishedTime
      },
      page2: {
        title: page2.title,
        wordCount: this.estimateWordCount(page2.html),
        published: page2.publishedTime
      }
    };
  }

  clearCache() {
    this.cache.clear();
  }
}

// 使用
const analyzer = new WebContentAnalyzer();
await analyzer.initialize();

const metadata = await analyzer.getPageMetadata('https://example.com/article');
console.log('文章元数据:', metadata);

const comparison = await analyzer.comparePages(
  'https://example.com/article1',
  'https://example.com/article2'
);
console.log('比较结果:', comparison);
```

### RSS 阅读器

```javascript
import ZAI from 'z-ai-web-dev-sdk';

class FeedReader {
  constructor() {
    this.articles = [];
  }

  async initialize() {
    this.zai = await ZAI.create();
  }

  async fetchArticlesFromUrls(urls) {
    const articles = [];

    for (const url of urls) {
      try {
        const result = await this.zai.functions.invoke('page_reader', {
          url: url
        });

        articles.push({
          title: result.data.title,
          url: result.data.url,
          publishedTime: result.data.publishedTime,
          content: result.data.html,
          fetchedAt: new Date().toISOString()
        });

        console.log(`获取: ${result.data.title}`);
      } catch (error) {
        console.error(`获取 ${url} 失败:`, error.message);
      }
    }

    this.articles = articles;
    return articles;
  }

  getRecentArticles(limit = 10) {
    return this.articles
      .sort((a, b) => {
        const dateA = new Date(a.publishedTime || a.fetchedAt);
        const dateB = new Date(b.publishedTime || b.fetchedAt);
        return dateB - dateA;
      })
      .slice(0, limit);
  }

  searchArticles(keyword) {
    return this.articles.filter(article => {
      const searchText = `${article.title} ${article.content}`.toLowerCase();
      return searchText.includes(keyword.toLowerCase());
    });
  }
}

// 使用
const reader = new FeedReader();
await reader.initialize();

const feedUrls = [
  'https://example.com/article1',
  'https://example.com/article2',
  'https://example.com/article3'
];

await reader.fetchArticlesFromUrls(feedUrls);
const recent = reader.getRecentArticles(5);
console.log('最新文章:', recent.map(a => a.title));
```

### 内容聚合器

```javascript
import ZAI from 'z-ai-web-dev-sdk';

async function aggregateContent(urls, options = {}) {
  const zai = await ZAI.create();
  const aggregated = {
    sources: [],
    totalWords: 0,
    aggregatedAt: new Date().toISOString()
  };

  for (const url of urls) {
    try {
      const result = await zai.functions.invoke('page_reader', {
        url: url
      });

      const text = result.data.html.replace(/<[^>]*>/g, ' ');
      const wordCount = text.split(/\s+/).filter(w => w.length > 0).length;

      aggregated.sources.push({
        title: result.data.title,
        url: result.data.url,
        publishedTime: result.data.publishedTime,
        wordCount: wordCount,
        excerpt: text.substring(0, 200).trim() + '...'
      });

      aggregated.totalWords += wordCount;

      if (options.delay) {
        await new Promise(resolve => setTimeout(resolve, options.delay));
      }
    } catch (error) {
      console.error(`获取 ${url} 失败:`, error.message);
    }
  }

  return aggregated;
}

// 使用
const sources = [
  'https://example.com/news1',
  'https://example.com/news2',
  'https://example.com/news3'
];

const aggregated = await aggregateContent(sources, { delay: 1000 });
console.log(`聚合了 ${aggregated.sources.length} 个来源`);
console.log(`总字数: ${aggregated.totalWords}`);
```

### 网页抓取管道

```javascript
import ZAI from 'z-ai-web-dev-sdk';

class ScrapingPipeline {
  constructor() {
    this.processors = [];
  }

  async initialize() {
    this.zai = await ZAI.create();
  }

  addProcessor(name, processorFn) {
    this.processors.push({ name, fn: processorFn });
  }

  async scrape(url) {
    // 获取页面
    const result = await this.zai.functions.invoke('page_reader', {
      url: url
    });

    let data = {
      raw: result.data,
      processed: {}
    };

    // 通过处理器
    for (const processor of this.processors) {
      try {
        data.processed[processor.name] = await processor.fn(data.raw);
        console.log(`✓ 使用 ${processor.name} 处理`);
      } catch (error) {
        console.error(`✗ 失败 ${processor.name}:`, error.message);
        data.processed[processor.name] = null;
      }
    }

    return data;
  }
}

// 处理器函数
function extractLinks(pageData) {
  const linkRegex = /href=["'](https?:\/\/[^"']+)["']/g;
  const links = [];
  let match;

  while ((match = linkRegex.exec(pageData.html)) !== null) {
    links.push(match[1]);
  }

  return [...new Set(links)]; // 移除重复项
}

function extractImages(pageData) {
  const imgRegex = /src=["'](https?:\/\/[^"']+\.(jpg|jpeg|png|gif|webp))["']/gi;
  const images = [];
  let match;

  while ((match = imgRegex.exec(pageData.html)) !== null) {
    images.push(match[1]);
  }

  return [...new Set(images)];
}

function extractPlainText(pageData) {
  return pageData.html
    .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
    .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
    .replace(/<[^>]*>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

// 使用
const pipeline = new ScrapingPipeline();
await pipeline.initialize();

pipeline.addProcessor('links', extractLinks);
pipeline.addProcessor('images', extractImages);
pipeline.addProcessor('plainText', extractPlainText);

const result = await pipeline.scrape('https://example.com/article');
console.log('找到的链接:', result.processed.links.length);
console.log('找到的图片:', result.processed.images.length);
console.log('文本长度:', result.processed.plainText.length);
```

## 响应格式

### 成功响应

```typescript
{
  code: 200,
  status: 200,
  data: {
    title: "文章标题",
    url: "https://example.com/article",
    html: "<div>文章内容...</div>",
    publishedTime: "2025-01-15T10:30:00Z",
    usage: {
      tokens: 1500
    }
  },
  meta: {
    usage: {
      tokens: 1500
    }
  }
}
```

### 响应字段

| 字段 | 类型 | 描述 |
|-------|------|-------------|
| `code` | number | 响应状态码 |
| `status` | number | HTTP 状态码 |
| `data.title` | string | 页面标题 |
| `data.url` | string | 页面 URL |
| `data.html` | string | 提取的 HTML 内容 |
| `data.publishedTime` | string | 发布日期（可选） |
| `data.usage.tokens` | number | 处理使用的 token 数量 |
| `meta.usage.tokens` | number | 使用的总 token 数量 |

## 最佳实践

### 1. 错误处理

```javascript
async function safeReadPage(url) {
  try {
    const zai = await ZAI.create();

    // 验证 URL
    if (!url || !url.startsWith('http')) {
      throw new Error('URL 格式无效');
    }

    const result = await zai.functions.invoke('page_reader', {
      url: url
    });

    // 检查响应状态
    if (result.code !== 200) {
      throw new Error(`获取页面失败: ${result.code}`);
    }

    // 验证基本数据
    if (!result.data.html || !result.data.title) {
      throw new Error('接收到的页面数据不完整');
    }

    return {
      success: true,
      data: result.data
    };
  } catch (error) {
    console.error('页面阅读错误:', error);
    return {
      success: false,
      error: error.message
    };
  }
}
```

### 2. 速率限制

```javascript
class RateLimitedReader {
  constructor(requestsPerMinute = 10) {
    this.requestsPerMinute = requestsPerMinute;
    this.requestTimes = [];
  }

  async initialize() {
    this.zai = await ZAI.create();
  }

  async readPage(url) {
    await this.waitForRateLimit();

    const result = await this.zai.functions.invoke('page_reader', {
      url: url
    });

    this.requestTimes.push(Date.now());
    return result.data;
  }

  async waitForRateLimit() {
    const now = Date.now();
    const oneMinuteAgo = now - 60000;

    // 移除旧的时间戳
    this.requestTimes = this.requestTimes.filter(time => time > oneMinuteAgo);

    // 检查是否需要等待
    if (this.requestTimes.length >= this.requestsPerMinute) {
      const oldestRequest = this.requestTimes[0];
      const waitTime = 60000 - (now - oldestRequest);

      if (waitTime > 0) {
        console.log(`达到速率限制。等待 ${waitTime}ms...`);
        await new Promise(resolve => setTimeout(resolve, waitTime));
      }
    }
  }
}

// 使用
const reader = new RateLimitedReader(10); // 每分钟 10 个请求
await reader.initialize();

const urls = ['https://example.com/1', 'https://example.com/2', 'https://example.com/3', 'https://example.com/4', 'https://example.com/5'
];

const results = await readPagesInParallel(urls, 2); // 2 个并发请求
results.forEach(result => {
  if (result.success) {
    console.log(`✓ ${result.data.title}`);
  } else {
    console.log(`✗ ${result.url}: ${result.error}`);
  }
});
```

### 3. 缓存策略

```javascript
import ZAI from 'z-ai-web-dev-sdk';

class CachedWebReader {
  constructor(cacheDuration = 3600000) { // 默认 1 小时
    this.cache = new Map();
    this.cacheDuration = cacheDuration;
  }

  async initialize() {
    this.zai = await ZAI.create();
  }

  async readPage(url, forceRefresh = false) {
    const cacheKey = url;
    const cached = this.cache.get(cacheKey);

    // 返回缓存的如果有效且不强制刷新
    if (cached && !forceRefresh) {
      const age = Date.now() - cached.timestamp;
      if (age < this.cacheDuration) {
        console.log('返回缓存的內容:', url);
        return cached.data;
      }
    }

    // 获取最新内容
    const result = await this.zai.functions.invoke('page_reader', {
      url: url
    });

    // 更新缓存
    this.cache.set(cacheKey, {
      data: result.data,
      timestamp: Date.now()
    });

    return result.data;
  }

  clearCache() {
    this.cache.clear();
  }

  getCacheStats() {
    return {
      size: this.cache.size,
      entries: Array.from(this.cache.keys())
    };
  }
}

// 使用
const reader = new CachedWebReader(3600000); // 1 小时缓存
await reader.initialize();

const data1 = await reader.readPage('https://example.com'); // 刷新获取
const data2 = await reader.readPage('https://example.com'); // 从缓存
const data3 = await reader.readPage('https://example.com', true); // 强制刷新
```

### 4. 并行处理

```javascript
import ZAI from 'z-ai-web-dev-sdk';

async function readPagesInParallel(urls, concurrency = 3) {
  const zai = await ZAI.create();
  const results = [];
  
  // 批量处理
  for (let i = 0; i < urls.length; i += concurrency) {
    const batch = urls.slice(i, i + concurrency);
    
    const batchResults = await Promise.allSettled(
      batch.map(url =>
        zai.functions.invoke('page_reader', { url })
          .then(result => ({
            url: url,
            success: true,
            data: result.data
          }))
          .catch(error => ({
            url: url,
            success: false,
            error: error.message
          }))
    );

    results.push(...batchResults.map(r => r.value));
    console.log(`完成批次 ${Math.floor(i / concurrency) + 1}`);
  }

  return results;
}

// 使用
const urls = [
  'https://example.com/1',
  'https://example.com/2',
  'https://example.com/3',
  'https://example.com/4',
  'https://example.com/5'
];

const results = await readPagesInParallel(urls, 2); // 2 个并发请求
results.forEach(result => {
  if (result.success) {
    console.log(`✓ ${result.data.title}`);
  } else {
    console.log(`✗ ${result.url}: ${result.error}`);
  }
});
```

### 5. 内容处理

```javascript
import ZAI from 'z-ai-web-dev-sdk';

class ContentProcessor {
  static extractMainContent(html) {
    // 移除脚本、样式和注释
    let content = html
      .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
      .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
      .replace(/<!--[\s\S]*?-->/g, '');

    return content;
  }

  static htmlToPlainText(html) {
    return html
      .replace(/<br\s*\/?>/gi, '\n')
      .replace(/<\/p>/gi, '\n\n')
      .replace(/<[^>]*>/g, '')
      .replace(/&nbsp;/g, ' ')
      .replace(/&amp;/g, '&')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&quot;/g, '"')
      .replace(/\s+/g, ' ')
      .trim();
  }

  static extractMetadata(html) {
    const metadata = {};

    // 提取 meta 描述
    const descMatch = html.match(/<meta\s+name=["']description["']\s+content=["']([^"']+)["']/i);
    if (descMatch) metadata.description = descMatch[1];

    // 提取关键词
    const keywordsMatch = html.match(/<meta\s+name=["']keywords["']\s+content=["']([^"']+)["']/i);
    if (keywordsMatch) metadata.keywords = keywordsMatch[1].split(',').map(k => k.trim());

    // 提取作者
    const authorMatch = html.match(/<meta\s+name=["']author["']\s+content=["']([^"']+)["']/i);
    if (authorMatch) metadata.author = authorMatch[1];

    return metadata;
  }
}

// 使用
async function processWebPage(url) {
  const zai = await ZAI.create();
  const result = await zai.functions.invoke('page_reader', { url });

  return {
    title: result.data.title,
    url: result.data.url,
    mainContent: ContentProcessor.extractMainContent(result.data.html),
    plainText: ContentProcessor.htmlToPlainText(result.data.html),
    metadata: ContentProcessor.extractMetadata(result.data.html),
    publishedTime: result.data.publishedTime
  };
}

const processed = await processWebPage('https://example.com/article');
console.log('处理后的內容:', processed.title);
```

## 常见用例

1. **新闻聚合**: 从多个来源收集和聚合新闻文章
2. **内容监控**: 跟踪特定网页上的更改
3. **研究工具**: 从学术或参考网站提取信息
4. **价格跟踪**: 监控产品页面上的价格变化
5. **SEO 分析**: 提取页面元数据和内容用于 SEO
6. **存档创建**: 创建网页内容的本地副本
7. **内容管理**: 按主题收集和组织网页内容
8. **竞争情报**: 监控竞争对手网站上的更新

## 集成示例

### Express.js API 端点

```javascript
import express from 'express';
import ZAI from 'z-ai-web-dev-sdk';

const app = express();
app.use(express.json());

let zaiInstance;

async function initZAI() {
  zaiInstance = await ZAI.create();
}

app.post('/api/read-page', async (req, res) => {
  try {
    const { url } = req.body;

    if (!url) {
      return res.status(400).json({ 
        error: 'URL 是必需的' 
      });
    }

    const result = await zaiInstance.functions.invoke('page_reader', {
      url: url
    });

    res.json({
      success: true,
      data: {
        title: result.data.title,
        url: result.data.url,
        content: result.data.html,
        publishedTime: result.data.publishedTime,
        tokensUsed: result.data.usage.tokens
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.post('/api/read-multiple', async (req, res) => {
  try {
    const { urls } = req.body;

    if (!urls || !Array.isArray(urls)) {
      return res.status(400).json({ 
        error: 'URL 数组是必需的' 
      });
    }

    const results = await Promise.allSettled(
      urls.map(url =>
        zaiInstance.functions.invoke('page_reader', { url })
          .then(result => ({
            url: url,
            success: true,
            data: result.data
          }))
          .catch(error => ({
            url: url,
            success: false,
            error: error.message
          }))
    );

    res.json({
      success: true,
      results: results.map(r => r.value)
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

initZAI().then(() => {
  app.listen(3000, () => {
    console.log('Web reader API 运行在端口 3000');
  });
});
```

### 定时内容获取器

```javascript
import ZAI from 'z-ai-web-dev-sdk';
import cron from 'node-cron';

class ScheduledFetcher {
  constructor() {
    this.urls = [];
    this.results = [];
  }

  async initialize() {
    this.zai = await ZAI.create();
  }

  addUrl(url, schedule) {
    this.urls.push({ url, schedule });
  }

  async fetchContent(url) {
    try {
      const result = await this.zai.functions.invoke('page_reader', {
        url: url
      });

      return {
        url: url,
        success: true,
        title: result.data.title,
        content: result.data.html,
        fetchedAt: new Date().toISOString()
      };

      console.log(`获取: ${result.data.title}`);
    } catch (error) {
      console.error(`获取 ${url} 失败:`, error.message);
    }
  }

  startScheduledFetch(url, schedule) {
    cron.schedule(schedule, async () => {
      console.log(`获取 ${url}...`);
      const result = await this.fetchContent(url);
      this.results.push(result.data);
      
      // 保持仅当有效时才返回缓存结果
      if (this.results.length > 100) {
        this.results = this.results.slice(-100);
      }
      
      console.log(`获取: ${result.success ? result.title : result.error}`);
    });
  }

  start() {
    for (const { url, schedule } of this.urls) {
      this.startScheduledFetch(url, schedule);
    }
  }

  getResults() {
    return this.results;
  }
}

// 使用
const fetcher = new ScheduledFetcher();
await fetcher.initialize();

// 每小时获取一次
fetcher.addUrl('https://example.com/news', '0 * * * *');

// 每天午夜获取一次
fetcher.addUrl('https://example.com/daily', '0 0 * * *');

fetcher.start();
console.log('定时获取已启动');
```

## 故障排除

**问题**: "SDK 必须在后端使用"
- **解决方案**: 确保 z-ai-web-dev-sdk 仅导入并用于服务器端代码

**问题**: 获取页面失败（404、403 等）
- **解决方案**: 验证 URL 是可访问的，并且没有被身份验证或付费墙保护

**问题**: 内容不完整或缺失
- **解决方案**: 某些页面可能具有动态内容，需要 JavaScript。阅读器提取的是静态 HTML 内容。

**问题**: token 使用量过高
- **解决方案**: token 使用量取决于页面大小。考虑缓存频繁访问的页面以减少 API 调用

**问题**: 响应时间缓慢
- **解决方案**: 实现缓存，使用并行处理多个 URL，并考虑速率限制

**问题**: 空的 HTML 内容
- **解决方案**: 检查页面是否需要身份验证或具有反抓取措施。验证 URL 是否正确。

## 性能提示

1. **实现缓存**: 缓存频繁访问的页面以减少 API 调用
2. **使用并行处理**: 并发获取多个页面（带速率限制）
3. **高效处理内容**: 从 HTML 中提取所需信息
4. **设置超时**: 设置合理的页面获取超时
5. **监控 token 使用情况**: 跟踪使用情况以优化成本
6. **批量操作**: 尽可能地批量获取多个 URL

## 安全注意事项

- 在处理之前验证所有 URL
- 处理提取的 HTML 内容以供显示
- 实施速率限制以防止滥用
- 永远不要在客户端代码中暴露 SDK 凭据
- 尊重 robots.txt 和网站服务条款
- 根据隐私法规处理用户数据
- 实施适当的错误处理以处理失败的请求

## 注意

- 始终使用 z-ai-web-dev-sdk 仅在后端代码中使用
- SDK 已经安装 - 按示例导入
- 实现适当的错误处理以构建健壮的应用程序
- 使用缓存以改善性能并降低成本
- 尊重网站服务条款和速率限制
- 小心处理 HTML 内容以提取有意义的数据
- 监控 token 使用情况以优化成本
