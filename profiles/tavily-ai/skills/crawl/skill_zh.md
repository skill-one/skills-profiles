# 爬取技能

爬取网站以从多个页面中提取内容。适用于文档、知识库和全站内容提取。

## 认证

脚本使用通过 Tavily MCP 服务器进行 OAuth 认证。**无需手动设置** - 首次运行时，它将：
1. 检查 `~/.mcp-auth/` 中是否存在现有令牌
2. 如果未找到，将自动打开您的浏览器进行 OAuth 认证

> **注意**：您必须拥有一个现有的 Tavily 账户。OAuth 流仅支持登录 - 通过此流程无法创建账户。如果您没有账户，请先在 [tavily.com](https://tavily.com) 注册。

### 替代方案：API 密钥

如果您更喜欢使用 API 密钥，请在 https://tavily.com 获取密钥并添加到 `~/.claude/settings.json`：
```json
{
  "env": {
    "TAVILY_API_KEY": "tvly-your-api-key-here"
  }
}
```

## 快速入门

### 使用脚本

```bash
./scripts/crawl.sh '<json>' [output_dir]
```

**示例**：
```bash
# 基本爬取
./scripts/crawl.sh '{"url": "https://docs.example.com"}'

# 深度爬取并设置限制
./scripts/crawl.sh '{"url": "https://docs.example.com", "max_depth": 2, "limit": 50}'

# 保存到文件
./scripts/crawl.sh '{"url": "https://docs.example.com", "max_depth": 2}' ./docs

# 聚焦爬取并设置路径过滤器
./scripts/crawl.sh '{"url": "https://example.com", "max_depth": 2, "select_paths": ["/docs/.*", "/api/.*"], "exclude_paths": ["/blog/.*"]}'

# 带语义指令（用于代理使用）
./scripts/crawl.sh '{"url": "https://docs.example.com", "instructions": "Find API documentation", "chunks_per_source": 3}'
```

当提供 `output_dir` 时，每个爬取的页面将保存为单独的 Markdown 文件。

### 基本爬取

```bash
curl --request POST \
  --url https://api.tavily.com/crawl \
  --header "Authorization: Bearer $TAVILY_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
    "url": "https://docs.example.com",
    "max_depth": 1,
    "limit": 20
  }'
```

### 带指令的聚焦爬取

```bash
curl --request POST \
  --url https://api.tavily.com/crawl \
  --header "Authorization: Bearer $TAVILY_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
    "url": "https://docs.example.com",
    "max_depth": 2,
    "instructions": "Find API documentation and code examples",
    "chunks_per_source": 3,
    "select_paths": ["/docs/.*", "/api/.*"]
  }'
```

## API 参考

### 端点

```
POST https://api.tavily.com/crawl
```

### 标头

| 标头 | 值 |
|-------|-------|
| `Authorization` | `Bearer <TAVILY_API_KEY>` |
| `Content-Type` | `application/json` |

### 请求体

| 字段 | 类型 | 默认值 | 描述 |
|-------|------|---------|-------------|
| `url` | 字符串 | 必填 | 开始爬取的根 URL |
| `max_depth` | 整数 | 1 | 爬取的深度级别（1-5） |
| `max_breadth` | 整数 | 20 | 每页的链接数 |
| `limit` | 整数 | 50 | 总页面上限 |
| `instructions` | 字符串 | null | 用于聚焦的自然语言指导 |
| `chunks_per_source` | 整数 | 3 | 每页的片段数（1-5，需要指令） |
| `extract_depth` | 字符串 | `"basic"` | `basic` 或 `advanced` |
| `format` | 字符串 | `"markdown"` | `markdown` 或 `text` |
| `select_paths` | 数组 | null | 要包含的正则表达式模式 |
| `exclude_paths` | 数组 | null | 要排除的正则表达式模式 |
| `allow_external` | 布尔值 | true | 包含外部域名链接 |
| `timeout` | 浮点数 | 150 | 最大等待时间（10-150 秒） |

### 响应格式

```json
{
  "base_url": "https://docs.example.com",
  "results": [
    {
      "url": "https://docs.example.com/page",
      "raw_content": "# Page Title\n\nContent..."
    }
  ],
  "response_time": 12.5
}
```

## 深度与性能

| 深度 | 典型页面数 | 时间 |
|-------|---------------|------|
| 1 | 10-50 | 秒 |
| 2 | 50-500 | 分钟 |
| 3 | 500-5000 | 多分钟 |

**从 `max_depth=1` 开始**，仅在需要时增加。

## 用于上下文提取与数据收集的爬取

**用于代理使用（将结果输入上下文）**：始终使用 `instructions` + `chunks_per_source`。这返回仅相关的片段而不是完整页面，防止上下文窗口爆炸。

**用于数据收集（保存到文件）**：省略 `chunks_per_source` 以获取完整页面内容。

## 示例

### 用于上下文：代理研究（推荐）

在将爬取结果输入 LLM 上下文时使用：

```bash
curl --request POST \
  --url https://api.tavily.com/crawl \
  --header "Authorization: Bearer $TAVILY_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
    "url": "https://docs.example.com",
    "max_depth": 2,
    "instructions": "Find API documentation and authentication guides",
    "chunks_per_source": 3
  }'
```

返回每个页面的最相关片段（每个最多 500 字符）- 适合上下文且不会使其过载。

### 用于上下文：目标技术文档

```bash
curl --request POST \
  --url https://api.tavily.com/crawl \
  --header "Authorization: Bearer $TAVILY_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
    "url": "https://example.com",
    "max_depth": 2,
    "instructions": "Find all documentation about authentication and security",
    "chunks_per_source": 3,
    "select_paths": ["/docs/.*", "/api/.*"]
  }'
```

### 用于数据收集：完整页面存档

在将内容保存到文件以供后续处理时使用：

```bash
curl --request POST \
  --url https://api.tavily.com/crawl \
  --header "Authorization: Bearer $TAVILY_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
    "url": "https://example.com/blog",
    "max_depth": 2,
    "max_breadth": 50,
    "select_paths": ["/blog/.*"],
    "exclude_paths": ["/blog/tag/.*", "/blog/category/.*"]
  }'
```

返回完整页面内容 - 使用脚本并指定 `output_dir` 以保存为 Markdown 文件。

## Map API（URL 发现）

当您只需要 URL 而不是内容时，使用 `map` 而不是 `crawl`：

```bash
curl --request POST \
  --url https://api.tavily.com/map \
  --header "Authorization: Bearer $TAVILY_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
    "url": "https://docs.example.com",
    "max_depth": 2,
    "instructions": "Find all API docs and guides"
  }'
```

仅返回 URL（比爬取更快）：

```json
{
  "base_url": "https://docs.example.com",
  "results": [
    "https://docs.example.com/api/auth",
    "https://docs.example.com/guides/quickstart"
  ]
}
```

## 小贴士

- **对于代理工作流始终使用 `chunks_per_source`** - 防止在将结果输入 LLM 时上下文爆炸
- **仅用于数据收集时省略 `chunks_per_source`** - 保存完整页面到文件
- **从保守开始** (`max_depth=1`, `limit=20`) 并逐步扩展
- **使用路径模式** 聚焦相关部分
- **首先使用 Map** 了解网站结构，然后再进行完整爬取
- **始终设置 `limit`** 以防止失控爬取
