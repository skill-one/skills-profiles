# 添加 TypeSpec API 操作

为 Microsoft 365 Copilot 添加 RESTful 操作到现有的 TypeSpec API 插件。

## 添加 GET 操作

### 简单 GET - 列出所有项目
```typescript
/**
 * 列出所有项目。
 */
@route("/items")
@get op listItems(): Item[];
```

### 带查询参数的 GET - 过滤结果
```typescript
/**
 * 根据条件过滤项目列表。
 * @param userId 可选的用户 ID 以过滤项目
 */
@route("/items")
@get op listItems(@query userId?: integer): Item[];
```

### 带路径参数的 GET - 获取单个项目
```typescript
/**
 * 通过 ID 获取特定项目。
 * @param id 要检索的项目 ID
 */
@route("/items/{id}")
@get op getItem(@path id: integer): Item;
```

### 带自适应卡片的 GET
```typescript
/**
 * 使用自适应卡片可视化列出项目。
 */
@route("/items")
@card(#{
  dataPath: "$",
  title: "$.title",
  file: "item-card.json"
})
@get op listItems(): Item[];
```

**创建自适应卡片** (`appPackage/item-card.json`):
```json
{
  "type": "AdaptiveCard",
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "version": "1.5",
  "body": [
    {
      "type": "Container",
      "$data": "${$root}",
      "items": [
        {
          "type": "TextBlock",
          "text": "**${if(title, title, 'N/A')}**",
          "wrap": true
        },
        {
          "type": "TextBlock",
          "text": "${if(description, description, 'N/A')}",
          "wrap": true
        }
      ]
    }
  ],
  "actions": [
    {
      "type": "Action.OpenUrl",
      "title": "查看详情",
      "url": "https://example.com/items/${id}"
    }
  ]
}
```

## 添加 POST 操作

### 简单 POST - 创建项目
```typescript
/**
 * 创建新项目。
 * @param item 要创建的项目
 */
@route("/items")
@post op createItem(@body item: CreateItemRequest): Item;

model CreateItemRequest {
  title: string;
  description?: string;
  userId: integer;
}
```

### 带确认的 POST
```typescript
/**
 * 带确认创建新项目。
 */
@route("/items")
@post
@capabilities(#{
  confirmation: #{
    type: "AdaptiveCard",
    title: "创建项目",
    body: """
    您确定要创建此项目吗？
      * **标题**: {{ function.parameters.item.title }}
      * **用户 ID**: {{ function.parameters.item.userId }}
    """
  }
})
op createItem(@body item: CreateItemRequest): Item;
```

## 添加 PATCH 操作

### 简单 PATCH - 更新项目
```typescript
/**
 * 更新现有项目。
 * @param id 要更新的项目 ID
 * @param item 更新的项目数据
 */
@route("/items/{id}")
@patch op updateItem(
  @path id: integer,
  @body item: UpdateItemRequest
): Item;

model UpdateItemRequest {
  title?: string;
  description?: string;
  status?: "active" | "completed" | "archived";
}
```

### 带确认的 PATCH
```typescript
/**
 * 带确认更新项目。
 */
@route("/items/{id}")
@patch
@capabilities(#{
  confirmation: #{
    type: "AdaptiveCard",
    title: "更新项目",
    body: """
    正在更新项目 #{{ function.parameters.id }}:
      * **标题**: {{ function.parameters.item.title }}
      * **状态**: {{ function.parameters.item.status }}
    """
  }
})
op updateItem(
  @path id: integer,
  @body item: UpdateItemRequest
): Item;
```

## 添加 DELETE 操作

### 简单 DELETE
```typescript
/**
 * 删除项目。
 * @param id 要删除的项目 ID
 */
@route("/items/{id}")
@delete op deleteItem(@path id: integer): void;
```

### 带确认的 DELETE
```typescript
/**
 * 带确认删除项目。
 */
@route("/items/{id}")
@delete
@capabilities(#{
  confirmation: #{
    type: "AdaptiveCard",
    title: "删除项目",
    body: """
    ⚠️ 您确定要删除项目 #{{ function.parameters.id }}？
    此操作无法撤销。
    """
  }
})
op deleteItem(@path id: integer): void;
```

## 完整的 CRUD 示例

### 定义服务和模型
```typescript
@service
@server("https://api.example.com")
@actions(#{
  nameForHuman: "项目 API",
  descriptionForHuman: "管理项目",
  descriptionForModel: "读取、创建、更新和删除项目"
})
namespace ItemsAPI {
  
  // 模型
  model Item {
    @visibility(Lifecycle.Read)
    id: integer;
    
    userId: integer;
    title: string;
    description?: string;
    status: "active" | "completed" | "archived";
    
    @format("date-time")
    createdAt: utcDateTime;
    
    @format("date-time")
    updatedAt?: utcDateTime;
  }

  model CreateItemRequest {
    userId: integer;
    title: string;
    description?: string;
  }

  model UpdateItemRequest {
    title?: string;
    description?: string;
    status?: "active" | "completed" | "archived";
  }

  // 操作
  @route("/items")
  @card(#{ dataPath: "$", title: "$.title", file: "item-card.json" })
  @get op listItems(@query userId?: integer): Item[];

  @route("/items/{id}")
  @card(#{ dataPath: "$", title: "$.title", file: "item-card.json" })
  @get op getItem(@path id: integer): Item;

  @route("/items")
  @post
  @capabilities(#{
    confirmation: #{
      type: "AdaptiveCard",
      title: "创建项目",
      body: "创建: **{{ function.parameters.item.title }}**"
    }
  })
  op createItem(@body item: CreateItemRequest): Item;

  @route("/items/{id}")
  @patch
  @capabilities(#{
    confirmation: #{
      type: "AdaptiveCard",
      title: "更新项目",
      body: "更新项目 #{{ function.parameters.id }}"
    }
  })
  op updateItem(@path id: integer, @body item: UpdateItemRequest): Item;

  @route("/items/{id}")
  @delete
  @capabilities(#{
    confirmation: #{
      type: "AdaptiveCard",
      title: "删除项目",
      body: "⚠️ 删除项目 #{{ function.parameters.id }}?"
    }
  })
  op deleteItem(@path id: integer): void;
}
```

## 高级功能

### 多个查询参数
```typescript
@route("/items")
@get op listItems(
  @query userId?: integer,
  @query status?: "active" | "completed" | "archived",
  @query limit?: integer,
  @query offset?: integer
): ItemList;

model ItemList {
  items: Item[];
  total: integer;
  hasMore: boolean;
}
```

### 头部参数
```typescript
@route("/items")
@get op listItems(
  @header("X-API-Version") apiVersion?: string,
  @query userId?: integer
): Item[];
```

### 自定义响应模型
```typescript
@route("/items/{id}")
@delete op deleteItem(@path id: integer): DeleteResponse;

model DeleteResponse {
  success: boolean;
  message: string;
  deletedId: integer;
}
```

### 错误响应
```typescript
model ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: string[];
  };
}

@route("/items/{id}")
@get op getItem(@path id: integer): Item | ErrorResponse;
```

## 测试提示

添加操作后，使用以下提示进行测试：

**GET 操作:**
- "列出所有项目并在表格中显示"
- "显示用户 ID 为 1 的项目"
- "获取项目 42 的详细信息"

**POST 操作:**
- "为用户 1 创建一个标题为 '我的任务' 的新项目"
- "添加项目: 标题 '新功能', 描述 '添加登录'"

**PATCH 操作:**
- "更新项目 10 的标题为 '更新标题'"
- "将项目 5 的状态更改为已完成"

**DELETE 操作:**
- "删除项目 99"
- "删除 ID 为 15 的项目"

## 最佳实践

### 参数命名
- 使用描述性参数名：`userId` 而不是 `uid`
- 在操作之间保持一致性
- 使用可选参数 (`?`) 用于过滤器

### 文档
- 为所有操作添加 JSDoc 注释
- 描述每个参数的作用
- 文档化预期响应

### 模型
- 使用 `@visibility(Lifecycle.Read)` 用于只读字段如 `id`
- 使用 `@format("date-time")` 用于日期字段
- 使用联合类型表示枚举：`"active" | "completed"`
- 通过 `?` 明确可选字段

### 确认
- 始终为破坏性操作（DELETE、PATCH）添加确认
- 在确认正文中显示关键详细信息
- 使用警告表情符号 (⚠️) 表示不可逆操作

### 自适应卡片
- 保持卡片简单和专注
- 使用条件渲染 `${if(..., ..., 'N/A')}`
- 包括操作按钮用于常见下一步操作
- 使用实际 API 响应测试数据绑定

### 路由
- 使用 RESTful 规范：
  - `GET /items` - 列出
  - `GET /items/{id}` - 获取一个
  - `POST /items` - 创建
  - `PATCH /items/{id}` - 更新
  - `DELETE /items/{id}` - 删除
- 将相关操作分组在同一命名空间中
- 使用嵌套路由表示分层资源

## 常见问题

### 问题：参数未在 Copilot 中显示
**解决方案**：检查参数是否正确装饰了 `@query`、`@path` 或 `@body`

### 问题：自适应卡片未渲染
**解决方案**：验证 `@card` 装饰器中的文件路径并检查 JSON 语法

### 问题：确认未出现
**解决方案**：确保 `@capabilities` 装饰器正确格式化确认对象

### 问题：模型属性未在响应中显示
**解决方案**：检查属性是否需要 `@visibility(Lifecycle.Read)` 或如果它应该是可写的则移除它
