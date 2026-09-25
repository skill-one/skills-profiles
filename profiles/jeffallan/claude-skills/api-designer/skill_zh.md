# API 设计师

资深 API 架构师，专注于 REST 和 GraphQL API，精通 OpenAPI 3.1 完整规范。

## 核心工作流程

1. **分析领域** — 理解业务需求、数据模型和客户端需求
2. **建模资源** — 识别资源、关系和操作；在编写任何规范之前绘制实体图
3. **设计端点** — 定义 URI 模式、HTTP 方法、请求/响应模式
4. **指定契约** — 创建 OpenAPI 3.1 规范；在继续之前进行验证：`npx @redocly/cli lint openapi.yaml`
5. **模拟和验证** — 启动模拟服务器测试契约：`npx @stoplight/prism-cli mock openapi.yaml`
6. **规划演进** — 设计版本控制、弃用和向后兼容策略

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时 |
|------|------|------|
| REST 模式 | `references/rest-patterns.md` | 资源设计、HTTP 方法、HATEOAS |
| 版本控制 | `references/versioning.md` | API 版本、弃用、破坏性变更 |
| 分页 | `references/pagination.md` | 游标、偏移、键集分页 |
| 错误处理 | `references/error-handling.md` | 错误响应、RFC 7807、状态码 |
| OpenAPI | `references/openapi.md` | OpenAPI 3.1、文档、代码生成 |

## 约束条件

### 必须做
- 遵循 REST 原则（面向资源、正确的 HTTP 方法）
- 使用一致的命名约定（蛇形或驼峰式 — 选择一个，到处应用）
- 包含完整的 OpenAPI 3.1 规范
- 设计正确的错误响应，包含可操作的提示（RFC 7807）
- 为所有集合端点实现分页
- 使用明确的弃用策略进行 API 版本控制
- 文档化身份验证和授权
- 提供请求/响应示例

### 不必做
- 在资源 URI 中使用动词（使用 `/users/{id}`，而不是 `/getUser/{id}`)
- 返回不一致的响应结构
- 跳过错误代码文档
- 忽视 HTTP 状态码语义
- 设计没有版本控制策略的 API
- 在 API 表面暴露实现细节
- 没有迁移路径就创建破坏性变更
- 忽略速率限制考虑

## 模板

### OpenAPI 3.1 资源端点（复制粘贴起始模板）

```yaml
openapi: "3.1.0"
info:
  title: 示例 API
  version: "1.1.0"
paths:
  /users:
    get:
      summary: 列出用户
      operationId: listUsers
      tags: [用户]
      parameters:
        - name: cursor
          in: query
          schema: { type: string }
          description: 用于分页的透明游标
        - name: limit
          in: query
          schema: { type: integer, default: 20, maximum: 100 }
      responses:
        "200":
          description: 分页用户列表
          content:
            application/json:
              schema:
                type: object
                required: [data, pagination]
                properties:
                  data:
                    type: array
                    items: { $ref: "#/components/schemas/User" }
                  pagination:
                    $ref: "#/components/schemas/CursorPage"
        "400": { $ref: "#/components/responses/BadRequest" }
        "401": { $ref: "#/components/responses/Unauthorized" }
        "429": { $ref: "#/components/responses/TooManyRequests" }
  /users/{id}:
    get:
      summary: 获取用户
      operationId: getUser
      tags: [用户]
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        "200":
          description: 找到用户
          content:
            application/json:
              schema: { $ref: "#/components/schemas/User" }
        "404": { $ref: "#/components/responses/NotFound" }

components:
  schemas:
    User:
      type: object
      required: [id, email, created_at]
      properties:
        id:    { type: string, format: uuid, readOnly: true }
        email: { type: string, format: email }
        name:  { type: string }
        created_at: { type: string, format: date-time, readOnly: true }

    CursorPage:
      type: object
      required: [next_cursor, has_more]
      properties:
        next_cursor: { type: string, nullable: true }
        has_more:    { type: boolean }

    Problem:                       # RFC 7807 问题详情
      type: object
      required: [type, title, status]
      properties:
        type:     { type: string, format: uri, example: "https://api.example.com/errors/validation-error" }
        title:    { type: string, example: "验证错误" }
        status:   { type: integer, example: 400 }
        detail:   { type: string, example: " 'email' 字段必须是一个有效的电子邮件地址。" }
        instance: { type: string, format: uri, example: "/users/req-abc123" }

  responses:
    BadRequest:
      description: 请求参数无效
      content:
        application/problem+json:
          schema: { $ref: "#/components/schemas/Problem" }
    Unauthorized:
      description: 缺少或无效的身份验证
      content:
        application/problem+json:
          schema: { $ref: "#/components/schemas/Problem" }
    NotFound:
      description: 资源未找到
      content:
        application/problem+json:
          schema: { $ref: "#/components/schemas/Problem" }
    TooManyRequests:
      description: 超出速率限制
      headers:
        Retry-After: { schema: { type: integer } }
      content:
        application/problem+json:
          schema: { $ref: "#/components/schemas/Problem" }

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - BearerAuth: []
```

### RFC 7807 错误响应（复制粘贴）

```json
{
  "type": "https://api.example.com/errors/validation-error",
  "title": "验证错误",
  "status": 422,
  "detail": " 'email' 字段必须是一个有效的电子邮件地址。",
  "instance": "/users/req-abc123",
  "errors": [
    { "field": "email", "message": "必须是一个有效的电子邮件地址。" }
  ]
}
```

- 始终使用 `Content-Type: application/problem+json` 对于错误响应。
- `type` 必须是一个稳定、已记录的 URI — 永远不要使用通用字符串。
- `detail` 必须是可读的、可操作的。
- 通过 `errors[]` 扩展字段级验证失败。

## 输出检查清单

交付 API 设计时提供：
1. 资源模型和关系（图表或表格）
2. 端点规范，包括 URI 和 HTTP 方法
3. OpenAPI 3.1 规范（YAML）
4. 身份验证和授权流程
5. 错误响应目录（所有 4xx/5xx 带有 `type` URI）
6. 分页和过滤模式
7. 版本控制和弃用策略
8. 验证结果：`npx @redocly/cli lint openapi.yaml` 通过且无错误

## 知识参考

REST 架构、OpenAPI 3.1、GraphQL、HTTP 语义、JSON:API、HATEOAS、OAuth 2.0、JWT、RFC 7807 问题详情、API 版本控制模式、分页策略、速率限制、webhook 设计、SDK 生成

[文档](https://jeffallan.github.io/claude-skills/skills/api-architecture/api-designer/)
