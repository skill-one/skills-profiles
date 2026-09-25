# 搜索技能

搜索网络并获取针对大语言模型优化的相关结果。

## 认证

脚本通过 Tavily MCP 服务器使用 OAuth。**无需手动设置** - 首次运行时，它将：
1. 检查 `~/.mcp-auth/` 中的现有令牌
2. 如果未找到，将自动打开浏览器进行 OAuth 认证

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
./scripts/search.sh '<json>'
```

**示例：**
```bash
# 基本搜索
./scripts/search.sh '{"query": "python async patterns"}'

# 带选项
./scripts/search.sh '{"query": "React hooks tutorial", "max_results": 10}'

# 带过滤器的进阶搜索
./scripts/search.sh '{"query": "AI news", "time_range": "week", "max_results": 10}'

# 域过滤搜索
./scripts/search.sh '{"query": "machine learning", "include_domains": ["arxiv.org", "github.com"], "search_depth": "advanced"}'
```

### 基本搜索

```bash
curl --request POST \
  --url https://api.tavily.com/search \
  --header "Authorization: Bearer $TAVILY_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
    "query": "latest developments in quantum computing",
    "max_results": 5
  }'
```

### 进阶搜索

```bash
curl --request POST \
  --url https://api.tavily.com/search \
  --header "Authorization: Bearer $TAVILY_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
    "query": "machine learning best practices",
    "max_results": 10,
    "search_depth": "advanced",
    "include_domains": ["arxiv.org", "github.com"]
  }'
```

## API 参考

### 端点

```
POST https://api.tavily.com/search
```

### 标头

| 标头 | 值 |
|-------|-------|
| `Authorization` | `Bearer <TAVILY_API_KEY>` |
| `Content-Type` | `application/json` |

### 请求体

| 字段 | 类型 | 默认值 | 描述 |
|-------|------|---------|-------------|
| `query` | string | 必填 | 搜索查询（保持在 400 字符以内） |
| `max_results` | integer | 10 | 最大结果数（0-20） |
| `search_depth` | string | `"basic"` | `ultra-fast`, `fast`, `basic`, `advanced` |
| `topic` | string | `"general"` | 搜索主题（仅限 general） |
| `time_range` | string | null | `day`, `week`, `month`, `year` |
| `start_date` | string | null | 返回此日期之后的结果 (`YYYY-MM-DD`) |
| `end_date` | string | null | 返回此日期之前的结果 (`YYYY-MM-DD`) |
| `include_domains` | array | [] | 包含的域名（最多 300 个） |
| `exclude_domains` | array | [] | 排除的域名（最多 150 个） |
| `country` | string | null | 提升特定国家结果（仅限 general 主题） |
| `include_raw_content` | boolean | false | 包含完整页面内容 |
| `include_images` | boolean | false | 包含图片结果 |
| `include_image_descriptions` | boolean | false | 包含图片描述 |
| `include_favicon` | boolean | false | 为每个结果包含 favicon URL |

### 响应格式

```json
{
  "query": "latest developments in quantum computing",
  "results": [
    {
      "title": "Page Title",
      "url": "https://example.com/page",
      "content": "Extracted text snippet...",
      "score": 0.85
    }
  ],
  "response_time": 1.2
}
```

## 搜索深度

| 深度 | 延迟 | 相关性 | 内容类型 |
|-------|---------|-----------|--------------|
| `ultra-fast` | 最低 | 较低 | NLP 摘要 |
| `fast` | 低 | 良好 | 片段 |
| `basic` | 中等 | 高 | NLP 摘要 |
| `advanced` | 较高 | 最高 | 片段 |

**何时使用每种深度：**
- `ultra-fast`：实时聊天、自动补全
- `fast`：需要片段但延迟重要
- `basic`：通用、平衡
- `advanced`：精确性重要（默认推荐）

## 示例

### 域过滤搜索

```bash
curl --request POST \
  --url https://api.tavily.com/search \
  --header "Authorization: Bearer $TAVILY_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
    "query": "Python async best practices",
    "include_domains": ["docs.python.org", "realpython.com", "github.com"],
    "search_depth": "advanced"
  }'
```

### 带完整内容的搜索

```bash
curl --request POST \
  --url https://api.tavily.com/search \
  --header "Authorization: Bearer $TAVILY_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
    "query": "React hooks tutorial",
    "max_results": 3,
    "include_raw_content": true
  }'
```

## 小贴士

- **保持查询在 400 字符以内** - 想搜索查询，不是提示
- **将复杂查询拆分为子查询** - 比单个大查询效果更好
- **使用 `include_domains`** 聚焦可信来源
- **使用 `time_range`** 获取最新信息
- **按 `score`（0-1）过滤** 获取最高相关性结果
