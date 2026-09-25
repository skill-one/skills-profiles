# notion API 技能

本技能通过 notion REST API 实现与 notion 工作空间的交互。使用 `curl` 和 `jq` 进行直接的 REST 调用，或根据任务需要编写临时脚本。

## 身份验证

### API 密钥处理

1. **环境变量**：检查环境中是否包含 `NOTION_API_TOKEN`
2. **用户提供的密钥**：如果用户在上下文中提供了 API 密钥，则使用它
3. **无可用密钥**：如果两者均不可用，则使用 AskUserQuestion（或等效方法）向用户请求 API 密钥

**重要**：切勿在任何地方显示、记录或发送 `NOTION_API_TOKEN`，除了在 `Authorization` 请求头中。确认其存在、询问是否缺失、在请求中使用它——但切勿回显或暴露它。

### 请求头

所有请求均需要以下请求头：

```bash
-H "Authorization: Bearer $NOTION_API_TOKEN" \
-H "Notion-Version: 2025-09-03" \
-H "Content-Type: application/json"
```

### 验证身份认证

通过获取机器人用户来测试 API 密钥：

```bash
curl -s "https://api.notion.com/v1/users/me" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" | jq
```

## 基础 URL 与约定

- **基础 URL**：`https://api.notion.com`
- **API 版本**：`2025-09-03`（必需请求头）
- **数据格式**：所有请求/响应体均使用 JSON
- **ID**：UUIDv4 格式（请求中横杠可选）
- **时间戳**：ISO 8601 格式（`2020-08-12T02:12:33.231Z`）
- **属性名称**：`snake_case`
- **空值**：使用 `null` 而非空字符串

## 速率限制

- **平均**：每个集成每秒 3 次请求
- **突发请求**：允许在此限制之上的短暂突发请求
- **速率受限响应**：HTTP 429 状态码及 `Retry-After` 请求头
- **策略**：收到 429 响应时实施指数退避

## 请求大小限制

| 类型 | 限制 |
|------|------|
| 每次负载中最大区块元素数量 | 1000 |
| 最大负载大小 | 500KB |
| 富文本内容 | 2000 个字符 |
| 网址 | 2000 个字符 |
| 公式 | 1000 个字符 |
| 邮箱地址 | 200 个字符 |
| 电话号码 | 200 个字符 |
| 多选选项 | 100 项 |
| 关系 | 100 个相关页面 |
| 提及的人员 | 100 位用户 |
| 每次请求中的区块数组 | 100 个元素 |

## 破坏性操作的确认

**重要**：在执行任何修改或删除数据的操作之前，请向用户确认。这包括：
- 更新页面或区块
- 删除/归档页面或区块
- 修改数据库模式
- 创建页面（如果多个或批量创建）
- 任何批量操作

对于一组相关的逻辑操作，一次确认即可。

## 核心 API 端点

### 搜索

在所有可访问的页面和数据库中搜索：

```bash
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "search term",
    "filter": {"property": "object", "value": "page"},
    "sort": {"direction": "descending", "timestamp": "last_edited_time"},
    "page_size": 100
  }' | jq
```

过滤值：`"page"` 或 `"data_source"`（或两者均省略）

### 页面

#### 检索页面

```bash
curl -s "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" | jq
```

**注意**：此请求返回页面属性，而非内容。如需获取内容，请使用带有页面 ID 的“检索区块子元素”接口。

#### 创建页面

父级选项：
- `{"page_id": "..."}` - 在页面下创建
- `{"database_id": "..."}` - 在数据库中创建（旧版）
- `{"data_source_id": "..."}` - 在数据源中创建（API v2025-09-03 及之后版本）

#### 更新页面

其他更新选项：`cover`、`is_locked`、`in_trash`

#### 归档（删除）页面

```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"archived": true}' | jq
```

#### 检索页面属性项

对于带有超过 25 个引用的属性：

```bash
curl -s "https://api.notion.com/v1/pages/{page_id}/properties/{property_id}" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" | jq
```

### 区块（页面内容）

#### 检索区块子元素

使用页面 ID 作为 `block_id` 以获取页面内容。检查每个区块的 `has_children` 属性以查找嵌套内容。

```bash
curl -s "https://api.notion.com/v1/blocks/{block_id}/children?page_size=100" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" | jq
```

#### 追加区块子元素

每次请求最多 100 个区块，嵌套层级最多 2 级。

请求体中的位置选项：
- 默认：追加到末尾
- `"position": {"type": "start"}` - 插入到开头
- `"position": {"type": "after_block", "after_block": {"id": "block-id"}}` - 插入到特定区块之后

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
          "rich_text": [{"type": "text", "text": {"content": "New Section"}}]
        }
      },
      {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
          "rich_text": [{"type": "text", "text": {"content": "Content here"}}]
        }
      }
    ]
  }' | jq
```

#### 检索区块

```bash
curl -s "https://api.notion.com/v1/blocks/{block_id}" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" | jq
```

#### 更新区块

更新操作会替换指定字段的完整值。

```bash
curl -s -X PATCH "https://api.notion.com/v1/blocks/{block_id}" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "paragraph": {
      "rich_text": [{"type": "text", "text": {"content": "Updated content"}}]
    }
  }' | jq
```

#### 删除区块

```bash
curl -s -X DELETE "https://api.notion.com/v1/blocks/{block_id}" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" | jq
```

将区块移至回收站（可恢复）。

### 数据库

#### 检索数据库

```bash
curl -s "https://api.notion.com/v1/databases/{database_id}" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" | jq
```

返回包括数据源和属性的数据库结构。

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

有关完整的筛选和排序文档，请参阅 `references/filters-and-sorts.md`。

#### 创建数据库

```bash
curl -s -X POST "https://api.notion.com/v1/databases" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "parent-page-id"},
    "title": [{"type": "text", "text": {"content": "My Database"}}],
    "is_inline": true,
    "initial_data_source": {
      "properties": {
        "Name": {"title": {}},
        "Status": {
          "select": {
            "options": [
              {"name": "To Do", "color": "red"},
              {"name": "In Progress", "color": "yellow"},
              {"name": "Done", "color": "green"}
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
    "title": [{"text": {"content": "Updated Title"}}],
    "description": [{"text": {"content": "Database description"}}]
  }' | jq
```

### 数据源（API v2025-09-03 及之后版本）

数据源是数据库中的独立表格。自 API 版本 2025-09-03 起，数据库可包含多个数据源。

#### 创建数据源

```bash
curl -s -X POST "https://api.notion.com/v1/data_sources" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"type": "database_id", "database_id": "database-id"},
    "title": [{"type": "text", "text": {"content": "New Data Source"}}],
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

#### 检索用户

```bash
curl -s "https://api.notion.com/v1/users/{user_id}" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" | jq
```

#### 检索机器人用户（自身）

```bash
curl -s "https://api.notion.com/v1/users/me" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" | jq
```

### 评论

#### 检索评论

```bash
curl -s "https://api.notion.com/v1/comments?block_id={block_id}&page_size=100" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" | jq
```

页面级别的评论使用页面 ID 作为 `block_id`。

#### 创建评论

在页面中：

```bash
curl -s -X POST "https://api.notion.com/v1/comments" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "page-id"},
    "rich_text": [{"type": "text", "text": {"content": "Comment content"}}]
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
    "rich_text": [{"type": "text", "text": {"content": "Reply content"}}]
  }' | jq
```

**注意**：API 无法启动新的内联讨论线程，也无法编辑或删除现有评论。

## 分页

分页端点返回：
- `has_more`：布尔值，表示存在更多结果
- `next_cursor`：下一页的游标
- `results`：项目数组

要遍历所有结果：

1. 发起初始请求（省略 `start_cursor`）
2. 检查响应中的 `has_more`
3. 如果为 `true`，提取 `next_cursor` 并将其作为 `start_cursor` 包含在下一请求中
4. 重复直至 `has_more` 为 `false`

游标请求示例：

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
| 400 | `invalid_request_url` | 网址格式错误 |
| 400 | `invalid_request` | 请求不受支持 |
| 400 | `validation_error` | 请求体不符合预期模式 |
| 400 | `missing_version` | 缺少 Notion-Version 请求头 |
| 401 | `unauthorized` | 无效的 Bearer 令牌 |
| 403 | `restricted_resource` | 令牌缺少权限 |
| 404 | `object_not_found` | 资源不存在或未与集成共享 |
| 409 | `conflict_error` | 事务期间数据冲突 |
| 429 | `rate_limited` | 超出速率限制（检查 `Retry-After` 请求头） |
| 500 | `internal_server_error` | 意外的服务器错误 |
| 503 | `service_unavailable` | notion 不可用或超过 60 秒超时 |
| 503 | `database_connection_unavailable` | 数据库无响应 |
| 504 | `gateway_timeout` | 请求超时 |

## 最佳实践

1. **存储 ID**：创建页面/数据库时，存储返回的 ID 以供后续更新使用
2. **使用属性 ID**：通过 ID 而非名称引用属性，以保证稳定性
3. **批量操作**：将多个小操作聚合为更少的请求
4. **遵守速率限制**：对 429 响应实施指数退避
5. **检查 `has_more`**：对于列表端点，始终处理分页
6. **更新前验证**：在进行更新之前获取当前状态
7. **使用环境变量**：切勿硬编码 API 密钥
8. **优雅处理错误**：检查响应状态码和错误信息
9. **模式大小**：将数据库模式控制在 50KB 以下以获得最佳性能
10. **属性限制**：带有超过 25 个页面引用的属性需要单独检索

## 参考资料

关于特定主题的详细文档，请参阅：
- `references/block-types.md` - 所有支持的区块类型及其结构
- `references/property-types.md` - 数据库属性类型及值格式
- `references/filters-and-sorts.md` - 数据库查询筛选与排序语法
- `references/rich-text.md` - 富文本对象结构及注释
