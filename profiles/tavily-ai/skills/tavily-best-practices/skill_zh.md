# Tavily

Tavily 是一个专为大型语言模型设计的搜索 API，使 AI 应用能够访问实时网络数据。

## 安装

**Python:**
```bash
pip install tavily-python
```

**JavaScript:**
```bash
npm install @tavily/core
```

参见 **[references/sdk.md](references/sdk.md)** 获取完整的 SDK 参考。

## 客户端初始化

```python
from tavily import TavilyClient

# 使用 TAVILY_API_KEY 环境变量（推荐）
client = TavilyClient()

# 带项目跟踪（用于使用量组织）
client = TavilyClient(project_id="your-project-id")

# 异步客户端用于并行查询
from tavily import AsyncTavilyClient
async_client = AsyncTavilyClient()
```

## 选择合适的方法

**用于自定义代理/工作流：**

| 需求 | 方法 |
|------|--------|
| 网络搜索结果 | `search()` |
| 特定 URL 的内容 | `extract()` |
| 整个网站的内容 | `crawl()` |
| 网站的 URL 发现 | `map()` |

**用于即用型研究：**

| 需求 | 方法 |
|------|--------|
| 带人工智能合成的端到端研究 | `research()` |

## 快速参考

### search() - 网络搜索

```python
response = client.search(
    query="量子计算突破",  # 保持少于 400 个字符
    max_results=10,
    search_depth="advanced"
)
print(response)
```
关键参数：`query`、`max_results`、`search_depth`（超快/快/基本/高级）、`include_domains`、`exclude_domains`、`time_range`

参见 **[references/search.md](references/search.md)** 获取完整的搜索参考。

### extract() - URL 内容提取

```python
# 简单单步提取
response = client.extract(
    urls=["https://docs.example.com"],
    extract_depth="advanced"
)
print(response)
```
关键参数：`urls`（最多 20 个）、`extract_depth`、`query`、`chunks_per_source`（1-5）

参见 **[references/extract.md](references/extract.md)** 获取完整的提取参考。

### crawl() - 全站提取

```python
response = client.crawl(
    url="https://docs.example.com",
    instructions="查找 API 文档页面",  # 语义焦点
    extract_depth="advanced"
)
print(response)
```
关键参数：`url`、`max_depth`、`max_breadth`、`limit`、`instructions`、`chunks_per_source`、`select_paths`、`exclude_paths`

参见 **[references/crawl.md](references/crawl.md)** 获取完整的爬取参考。

### map() - URL 发现

```python
response = client.map(
    url="https://docs.example.com"
)
print(response)
```

### research() - 人工智能驱动的研究

```python
import time

# 用于全面多主题研究
result = client.research(
    input="分析 X 在中小企业市场中的竞争格局",
    model="pro"  # 或 "mini" 用于专注查询，"auto" 在不确定时
)
request_id = result["request_id"]

# 循环查询直至完成
response = client.get_research(request_id)
while response["status"] not 在 ["completed", "failed"]:
    time.sleep(10)
    response = client.get_research(request_id)

print(response["content"])  # 研究报告
```
关键参数：`input`、`model`（"mini"/"pro"/"auto"）、`stream`、`output_schema`、`citation_format`

参见 **[references/research.md](references/research.md)** 获取完整的研究参考。

## 详细指南

获取完整参数、响应字段、模式及示例：

- **[references/sdk.md](references/sdk.md)** - Python & JavaScript SDK 参考、异步模式、混合 RAG
- **[references/search.md](references/search.md)** - 查询优化、搜索深度选择、域名过滤、异步模式、后过滤
- **[references/extract.md](references/extract.md)** - 单步 vs 两步提取、查询/块用于定位、高级模式
- **[references/crawl.md](references/crawl.md)** - 爬取 vs 映射、用于语义焦点的指令、用例、映射后提取模式
- **[references/research.md](references/research.md)** - 提示最佳实践、模型选择、流式传输、结构化输出模式
- **[references/integrations.md](references/integrations.md)** - LangChain、LlamaIndex、CrewAI、Vercel AI SDK 及框架集成
