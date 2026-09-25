# Notion API 技能

该技能通过 Notion REST API 实现与 Notion 工作区的交互。使用 `curl` 和 `jq` 进行直接的 REST 调用，或根据任务需求编写临时脚本。

## 认证

### API 密钥处理

1. **环境变量**：检查环境变量中是否存在 `NOTION_API_TOKEN`
2. **用户提供的密钥**：如果用户在上下文中提供了 API 密钥，则使用该密钥
3. **无密钥可用**：如果两者都不可用，则使用 AskUserQuestion（或等效方法）向用户请求 API 密钥

**重要提示**：除了在 `Authorization` 头部之外，永远不要在任何地方显示、记录或发送 `NOTION_API_TOKEN`。确认其存在，如果缺失则询问，在请求中使用它——但永远不要回显或暴露它。

### 请求头部

所有请求都需要以下头部：

```bash
-H "Authorization: Bearer $NOTION_API_TOKEN" \
-H "Notion-Version: 2025-09-03" \
-H "Content-Type: application/json"
```

### 验证认证

通过获取机器人用户来测试 API 密钥：

```bash
curl -s "https://api.notion.com/v1/users/me" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" | jq
```

## 基础 URL 和约定

- **基础 URL**：`https://api.notion.com`
- **API 版本**：`2025-09-03`（必需的头部）
- **数据格式**：所有请求/响应体使用 JSON
- **ID**：UUIDv4 格式（请求中可选连字符）
- **时间戳**：ISO 8601 格式（`2020-08-12T02:12:33.231Z`）
- **属性名称**：`snake_case`
- **空值**：使用 `null` 而不是空字符串

## 速率限制

- **平均**：每个集成每秒 3 个请求
- **突发**：允许短暂超过此限制
- **速率限制响应**：HTTP 429 带有 `Retry-After` 头部
- **策略**：在收到 429 响应时实施指数退避

## 请求大小限制

| 类型 | 限制 |
|------|-------|
| 最大块元素数（每个负载） | 1000 |
| 最大负载大小 | 500KB |
| 富文本内容 | 2000 个字符 |
| URL | 2000 个字符 |
| 方程式 | 1000 个字符 |
| 电子邮件地址 | 200 个字符 |
| 电话号码 | 200 个字符 |
| 多选选项 | 100 项 |
| 关系 | 100 个相关页面 |
| 用户提及 | 100 个用户 |
| 块数组（每个请求） | 100 个元素 |

## 破坏性操作的确认

**重要提示**：在执行任何修改或删除数据的操作之前，必须询问用户确认。这包括：
- 更新页面或块
- 删除/归档页面或块
- 修改数据库模式
- 批量创建页面
- 任何批量操作

对于逻辑相关的操作组，一个确认即可。

## 核心API端点

### 搜索

跨所有可访问的页面和数据库进行搜索：

```bash
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "搜索词",
    "filter": {"property": "object", "value": "page"},
    "sort": {"direction": "descending", "timestamp": "last_edited_time"},
    "page_size": 100
  }' | jq
```

过滤器值：`"page"` 或 `"data_source"`（或两者都省略）

### 页面

#### 获取页面

```bash
curl -s "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" | jq
```

**注意**：这返回页面属性，而不是内容。要获取内容，请使用“获取块子元素”并使用页面 ID。

#### 创建页面

```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "父页面ID"},
    "properties": {
      "title": {
        "title": [{"text": {"content": "页面标题"}}]
      }
    },
    "children": [
      {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
          "rich_text": [{"type": "text", "text": {"content": "段落内容"}}]
        }
      }
    ]
  }' | jq
```

父选项：
- `{"page_id": "..."}` - 在页面下创建
- `{"database_id": "..."}` - 在数据库中创建（旧版）
- `{"data_source_id": "..."}` - 在数据源中创建（API v2025-09-03+）

#### 更新页面

```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "title": {"title": [{"text": {"content": "更新标题"}}]}
    },
    "icon": {"type": "emoji", "emoji": "📝"},
    "archived": false
  }' | jq
```

其他更新选项：`cover`、`is_locked`、`in_trash`

#### 归档（删除）页面

```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"archived": true}' | jq
```

#### 获取页面属性项

对于超过 25 个引用的属性：

```bash
curl -s "https://api.notion.com/v1/pages/{page_id}/properties/{property_id}" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" | jq
```

### 块（页面内容）

#### 获取块子元素

```bash
curl -s "https://api.notion.com/v1/blocks/{block_id}/children?page_size=100" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" | jq
```

使用页面 ID 作为 `block_id` 获取页面内容。检查每个块的 `has_children` 以获取嵌套内容。

#### 追加块子元素

```bash
curl -s -X PATCH "https://api.notion.com/v1/blocks/{block_id}/children" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
          "rich_text": [{"type": "text", "text": {"content": "新章节"}}]
        }
      },
      {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
          "rich_text": [{"type": "text", "text": {"content": "内容这里"}}]
        }
      }
    ]
  }' | jq
```

最多每请求 100 个块，最多 2 层嵌套。

请求体中的位置选项：
- 默认：追加到末尾
- `"position": {"type": "start"}` - 插入到开头
- `"position": {"type": "after_block", "after_block": {"id": "block-id"}}` - 插入到特定块之后

#### 获取块

```bash
curl -s "https://api.notion.com/v1/blocks/{block_id}" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" | jq
```

#### 更新块

```bash
curl -s -X PATCH "https://api.notion.com/v1/blocks/{block_id}" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "paragraph": {
      "rich_text": [{"type": "text", "text": {"content": "更新内容"}}]
    }
  }' | jq
```

更新将替换指定字段的所有值。

#### 删除块

```bash
curl -s -X DELETE "https://api.notion.com/v1/blocks/{block_id}" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" | jq
```

将块移至回收站（可以恢复）。

### 数据库

#### 获取数据库

```bash
curl -s "https://api.notion.com/v1/databases/{database_id}" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" | jq
```

返回数据库结构，包括数据源和属性。

#### 查询数据库

```bash
curl -s -X POST "https://api.notion.com/v1/databases/{database_id}/query" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {
      "property": "Status",
      "select": {"equals": "Done"}
    },
    "sorts": [
      {"property": "Created", "direction": "descending"}
    ],
    "page_size": 100
  }' | jq
```

有关全面的过滤器和排序文档，请参阅 `references/filters-and-sorts.md`。

#### 创建数据库

```bash
curl -s -X POST "https://api.notion.com/v1/databases" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "父页面ID"},
    "title": [{"type": "text", "text": {"content": "我的数据库"}}],
    "is_inline": true,
    "initial_data_source": {
      "properties": {
        "Name": {"title": {}},
        "Status": {
          "select": {
            "options": [
              {"name": "待办", "color": "red"},
              {"name": "进行中", "color": "yellow"},
              {"name": "已完成", "color": "green"}
            ]
          }
        },
        "Due Date": {"date": {}}
      }
    }
  }' | jq
```

#### 更新数据库

```bash
curl -s -X PATCH "https://api.notion.com/v1/databases/{database_id}" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "title": [{"text": {"content": "更新标题"}}],
    "description": [{"text": {"content": "数据库描述"}}]
  }' | jq
```

### 数据源（API v2025-09-03+）

数据源是数据库中的单个表格。自 API 版本 2025-09-03 起，数据库可以包含多个数据源。

#### 创建数据源

```bash
curl -s -X POST "https://api.notion.com/v1/data_sources" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"type": "database_id", "database_id": "database-id"},
    "title": [{"type": "text", "text": {"content": "新数据源"}}],
    "properties": {
      "Name": {"title": {}},
      "Description": {"rich_text": {}}
    }
  }' | jq
```

### 用户

#### 列出所有用户

```bash
curl -s "https://api.notion.com/v1/users?page_size=100" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" | jq
```

#### 获取用户

```bash
curl -s "https://api.notion.com/v1/users/{user_id}" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" | jq
```

#### 获取机器人用户（自身）

```bash
curl -s "https://api.notion.com/v1/users/me" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" | jq
```

### 评论

#### 获取评论

```bash
curl -s "https://api.notion.com/v1/comments?block_id={block_id}&page_size=100" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" | jq
```

使用页面 ID 作为 `block_id` 获取页面级别的评论。

#### 创建评论

在页面：

```bash
curl -s -X POST "https://api.notion.com/v1/comments" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "page-id"},
    "rich_text": [{"type": "text", "text": {"content": "评论内容"}}]
  }' | jq
```

回复讨论：

```bash
curl -s -X POST "https://api.notion.com/v1/comments" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "discussion_id": "discussion-id",
    "rich_text": [{"type": "text", "text": {"content": "回复内容"}}]
  }' | jq
```

**注意**：API 无法启动新的内联讨论线程或编辑/删除现有评论。

## 分页

分页端点返回：
- `has_more`：布尔值指示是否存在更多结果
- `next_cursor`：下一页的游标
- `results`：项目数组

要迭代所有结果：

1. 执行初始请求（省略 `start_cursor`）
2. 检查响应中的 `has_more`
3. 如果为 `true`，提取 `next_cursor` 并将其作为 `start_cursor` 在下一个请求中使用
4. 重复，直到 `has_more` 为 `false`

带游标的请求示例：

```json
{
  "page_size": 100,
  "start_cursor": "v1%7C..."
}
```

## 错误处理

| HTTP 状态 | 代码 | 描述 |
|-------------|------|-------------|
| 400 | `invalid_json` | 请求体不是有效的 JSON |
| 400 | `invalid_request_url` | URL 格式错误 |
| 400 | `invalid_request` | 请求不受支持 |
| 400 | `validation_error` | 请求体不符合预期模式 |
| 400 | `missing_version` | 缺少 Notion-Version 头部 |
| 401 | `unauthorized` | 无效的 bearer 令牌 |
| 403 | `restricted_resource` | 令牌没有权限 |
| 404 | `object_not_found` | 资源不存在或未与集成共享 |
| 409 | `conflict_error` | 事务期间数据冲突 |
| 429 | `rate_limited` | 超出速率限制（检查 Retry-After 头部） |
| 500 | `internal_server_error` | 服务器意外错误 |
| 503 | `service_unavailable` | Notion 不可用或 60 秒超时超过 |
| 503 | `database_connection_unavailable` | 数据库无响应 |
| 504 | `gateway_timeout` | 请求超时 |

## 最佳实践

1. **存储 ID**：创建页面/数据库时，存储返回的 ID 以便将来更新
2. **使用属性 ID**：通过 ID 而不是名称引用属性，以确保稳定性
3. **批量操作**：将多个小操作合并为较少的请求
4. **尊重速率限制**：对 429 响应实施指数退避
5. **检查 `has_more`**：始终处理列表端点的分页
6. **更新前验证**：在更新之前检索当前状态
7. **使用环境变量**：永远不要硬编码 API 密钥
8. **优雅处理错误**：检查响应状态代码和错误消息
9. **模式大小**：将数据库模式保持在 50KB 以下以获得最佳性能
10. **属性限制**：超过 25 个页面引用的属性需要单独检索

## 参考

有关特定主题的详细文档，请参阅：
- `references/block-types.md` - 所有支持的块类型及其结构
- `references/property-types.md` - 数据库属性类型和值格式
- `references/filters-and-sorts.md` - 数据库查询过滤器和排序语法
- `references/rich-text.md` - 富文本对象结构和注释
