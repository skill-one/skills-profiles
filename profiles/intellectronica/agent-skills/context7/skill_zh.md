# Context7

## 概述

该技能通过使用 curl 查询 Context7 API 来检索软件库和组件的当前文档。使用它来代替依赖可能过时的训练数据。

## 工作流程

### 第一步：搜索库

要查找 Context7 库 ID，请查询搜索端点：

```bash
curl -s "https://context7.com/api/v2/libs/search?libraryName=LIBRARY_NAME&query=TOPIC" | jq '.results[0]'
```

**参数：**
- `libraryName` (必需)：要搜索的库名称（例如，"react"、"nextjs"、"fastapi"、"axios"）
- `query` (必需)：用于相关性排序的主题描述

**响应字段：**
- `id`：上下文端点的库标识符（例如，`/websites/react_dev_reference`）
- `title`：人类可读的库名称
- `description`：库的简要描述
- `totalSnippets`：可用的文档片段数量

### 第二步：获取文档

要检索文档，请使用第一步中的库 ID：

```bash
curl -s "https://context7.com/api/v2/context?libraryId=LIBRARY_ID&query=TOPIC&type=txt"
```

**参数：**
- `libraryId` (必需)：搜索结果中的库 ID
- `query` (必需)：要检索文档的特定主题
- `type` (可选)：响应格式 - `json`（默认）或 `txt`（纯文本，更易读）

## 示例

### React hooks 文档

```bash
# 查找 React 库 ID
curl -s "https://context7.com/api/v2/libs/search?libraryName=react&query=hooks" | jq '.results[0].id'
# 返回："/websites/react_dev_reference"

# 获取 useState 文档
curl -s "https://context7.com/api/v2/context?libraryId=/websites/react_dev_reference&query=useState&type=txt"
```

### Next.js 路由文档

```bash
# 查找 Next.js 库 ID
curl -s "https://context7.com/api/v2/libs/search?libraryName=nextjs&query=routing" | jq '.results[0].id'

# 获取 app router 文档
curl -s "https://context7.com/api/v2/context?libraryId=/vercel/next.js&query=app+router&type=txt"
```

### FastAPI 依赖注入

```bash
# 查找 FastAPI 库 ID
curl -s "https://context7.com/api/v2/libs/search?libraryName=fastapi&query=dependencies" | jq '.results[0].id'

# 获取依赖注入文档
curl -s "https://context7.com/api/v2/context?libraryId=/fastapi/fastapi&query=dependency+injection&type=txt"
```

## 小贴士

- 使用 `type=txt` 获取更易读的输出
- 使用 `jq` 过滤和格式化 JSON 响应
- 使用 `query` 参数时保持具体，以提高相关性排序
- 如果第一个搜索结果不正确，请检查数组中的其他结果
- 对包含空格的查询参数进行 URL 编码（使用 `+` 或 `%20`）
- 基本使用不需要 API 密钥（有限速率限制）
