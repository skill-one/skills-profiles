# 提取技能

从特定URL中提取干净的内容。当你知道要从哪些页面获取内容时，这是理想的选择。

## 认证

脚本通过Tavily MCP服务器使用OAuth。**无需手动设置** - 首次运行时，它将：
1. 检查`~/.mcp-auth/`中是否存在现有令牌
2. 如果未找到，将自动打开浏览器进行OAuth认证

> **注意**：你必须拥有一个现有的Tavily账户。OAuth流程仅支持登录 - 通过此流程无法创建账户。如果你没有账户，请先在 [tavily.com](https://tavily.com) 注册。

### 替代方案：API密钥

如果你更喜欢使用API密钥，请在 https://tavily.com 获取一个，并添加到 `~/.claude/settings.json`：
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
./scripts/extract.sh '<json>'
```

**示例**：
```bash
# 单个URL
./scripts/extract.sh '{"urls": ["https://example.com/article"]}'

# 多个URL
./scripts/extract.sh '{"urls": ["https://example.com/page1", "https://example.com/page2"]}'

# 带查询焦点和片段
./scripts/extract.sh '{"urls": ["https://example.com/docs"], "query": "authentication API", "chunks_per_source": 3}'

# 针对JS页面的高级提取
./scripts/extract.sh '{"urls": ["https://app.example.com"], "extract_depth": "advanced", "timeout": 60}'
```

### 基本提取

```bash
curl --request POST \
  --url https://api.tavily.com/extract \
  --header "Authorization: Bearer $TAVILY_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
    "urls": ["https://example.com/article"]
  }'
```

### 带查询焦点的多个URL

```bash
curl --request POST \
  --url https://api.tavily.com/extract \
  --header "Authorization: Bearer $TAVILY_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
    "urls": [
      "https://example.com/ml-healthcare",
      "https://example.com/ai-diagnostics"
    ],
    "query": "AI diagnostic tools accuracy",
    "chunks_per_source": 3
  }'
```

## API参考

### 端点

```
POST https://api.tavily.com/extract
```

### 标头

| 标头 | 值 |
|--------|-------|
| `Authorization` | `Bearer <TAVILY_API_KEY>` |
| `Content-Type` | `application/json` |

### 请求体

| 字段 | 类型 | 默认值 | 描述 |
|-------|------|---------|-------------|
| `urls` | 数组 | 必填 | 要提取的URL（最多20个） |
| `query` | 字符串 | null | 根据相关性重新排序片段 |
| `chunks_per_source` | 整数 | 3 | 每个URL的片段数（1-5，需要查询） |
| `extract_depth` | 字符串 | `"basic"` | `basic` 或 `advanced`（针对JS页面） |
| `format` | 字符串 | `"markdown"` | `markdown` 或 `text` |
| `include_images` | 布尔值 | false | 包含图片URL |
| `timeout` | 浮点数 | 变化 | 最大等待时间（1-60秒） |

### 响应格式

```json
{
  "results": [
    {
      "url": "https://example.com/article",
      "raw_content": "# Article Title\n\nContent..."
    }
  ],
  "failed_results": [],
  "response_time": 2.3
}
```

## 提取深度

| 深度 | 何时使用 |
|-------|-------------|
| `basic` | 简单文本提取，更快 |
| `advanced` | 动态/JS渲染页面、表格、结构化数据 |

## 示例

### 单个URL提取

```bash
curl --request POST \
  --url https://api.tavily.com/extract \
  --header "Authorization: Bearer $TAVILY_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
    "urls": ["https://docs.python.org/3/tutorial/classes.html"],
    "extract_depth": "basic"
  }'
```

### 带查询的定向提取

```bash
curl --request POST \
  --url https://api.tavily.com/extract \
  --header "Authorization: Bearer $TAVILY_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
    "urls": [
      "https://example.com/react-hooks",
      "https://example.com/react-state"
    ],
    "query": "useState and useEffect patterns",
    "chunks_per_source": 2
  }'
```

### JS密集型页面

```bash
curl --request POST \
  --url https://api.tavily.com/extract \
  --header "Authorization: Bearer $TAVILY_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
    "urls": ["https://app.example.com/dashboard"],
    "extract_depth": "advanced",
    "timeout": 60
  }'
```

### 批量提取

```bash
curl --request POST \
  --url https://api.tavily.com/extract \
  --header "Authorization: Bearer $TAVILY_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
    "urls": [
      "https://example.com/page1",
      "https://example.com/page2",
      "https://example.com/page3",
      "https://example.com/page4",
      "https://example.com/page5"
    ],
    "extract_depth": "basic"
  }'
```

## 小贴士

- **每请求最多20个URL** - 批量处理较大列表
- **使用`query` + `chunks_per_source`** 获取仅相关的內容
- **先尝试`basic`**，如果内容缺失则切换到`advanced`
- **为慢速页面设置更长的`timeout`**（最长60秒）
- **检查`failed_results`** 获取无法提取的URL
