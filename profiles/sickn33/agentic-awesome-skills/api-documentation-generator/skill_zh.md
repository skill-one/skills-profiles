# API 文档生成器

## 概述

从您的代码库中自动生成清晰、全面的 API 文档。这项技能帮助您创建专业的文档，包括端点描述、请求/响应示例、认证细节、错误处理和使用指南。

适用于 REST API、GraphQL API 和 WebSocket API。

## 何时使用此技能

- 需要记录新 API 时使用
- 更新现有 API 文档时使用
- API 缺乏清晰文档时使用
- 新开发者接入您的 API 时使用
- 准备为外部用户准备 API 文档时使用
- 创建 OpenAPI/Swagger 规范时使用

## 工作原理

### 第一步：分析 API 结构

首先，我将检查您的 API 代码库以了解：
- 可用的端点和路由
- HTTP 方法（GET、POST、PUT、DELETE 等）
- 请求参数和正文结构
- 响应格式和状态码
- 认证和授权要求
- 错误处理模式

### 第二步：生成端点文档

对于每个端点，我将创建包括以下内容的文档：

**端点详情：**
- HTTP 方法和 URL 路径
- 简要说明其功能
- 认证要求
- 速率限制信息（如适用）

**请求规范：**
- 路径参数
- 查询参数
- 请求头
- 请求正文模式（包括类型和验证规则）

**响应规范：**
- 成功响应（状态码 + 正文结构）
- 错误响应（所有可能的错误代码）
- 响应头

**代码示例：**
- cURL 命令
- JavaScript/TypeScript（fetch/axios）
- Python（requests）
- 根据需要提供其他语言

### 第三步：添加使用指南

我将包括：
- 入门指南
- 认证设置
- 常见用例
- 最佳实践
- 速率限制细节
- 分页模式
- 过滤和排序选项

### 第四步：记录错误处理

清晰的错误记录，包括：
- 所有可能的错误代码
- 错误消息格式
- 排错指南
- 常见错误场景和解决方案

### 第五步：创建交互式示例

在可能的情况下，我将提供：
- Postman 集合
- OpenAPI/Swagger 规范
- 交互式代码示例
- 示例响应

## 示例

### 示例 1：REST API 端点文档

```markdown
## 创建用户

创建新用户账户。

**端点：** `POST /api/v1/users`

**认证：** 需要（Bearer 令牌）

**请求正文：**
\`\`\`json
{
  "email": "user@example.com",      // 必填：有效的电子邮件地址
  "password": "SecurePass123!",     // 必填：最小 8 个字符，1 个大写字母，1 个数字
  "name": "John Doe",               // 必填：2-50 个字符
  "role": "user"                    // 可选："user" 或 "admin"（默认："user"）
}
\`\`\`

**成功响应（201 Created）：**
\`\`\`json
{
  "id": "usr_1234567890",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "createdAt": "2026-01-20T10:30:00Z",
  "emailVerified": false
}
\`\`\`

**错误响应：**

- `400 Bad Request` - 无效输入数据
  \`\`\`json
  {
    "error": "VALIDATION_ERROR",
    "message": "无效的电子邮件格式",
    "field": "email"
  }
  \`\`\`

- `409 Conflict` - 邮箱已存在
  \`\`\`json
  {
    "error": "EMAIL_EXISTS",
    "message": "已存在此邮箱的账户"
  }
  \`\`\`

- `401 Unauthorized` - 缺少或无效的认证令牌

**示例请求（cURL）：**
\`\`\`bash
curl -X POST https://api.example.com/api/v1/users \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "name": "John Doe"
  }'
\`\`\`

**示例请求（JavaScript）：**
\`\`\`javascript
const response = await fetch('https://api.example.com/api/v1/users', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'SecurePass123!',
    name: 'John Doe'
  })
});

const user = await response.json();
console.log(user);
\`\`\`

**示例请求（Python）：**
\`\`\`python
import requests

response = requests.post(
    'https://api.example.com/api/v1/users',
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    },
    json={
        'email': 'user@example.com',
        'password': 'SecurePass123!',
        'name': 'John Doe'
    }
)

user = response.json()
print(user)
\`\`\`
```

### 示例 2：GraphQL API 文档

```markdown
## 用户查询

通过 ID 获取用户信息。

**查询：**
\`\`\`graphql
query GetUser($id: ID!) {
  user(id: $id) {
    id
    email
    name
    role
    createdAt
    posts {
      id
      title
      publishedAt
    }
  }
}
\`\`\`

**变量：**
\`\`\`json
{
  "id": "usr_1234567890"
}
\`\`\`

**响应：**
\`\`\`json
{
  "data": {
    "user": {
      "id": "usr_1234567890",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "user",
      "createdAt": "2026-01-20T10:30:00Z",
      "posts": [
        {
          "id": "post_123",
          "title": "我的第一篇帖子",
          "publishedAt": "2026-01-21T14:00:00Z"
        }
      ]
    }
  }
}
\`\`\`

**错误：**
\`\`\`json
{
  "errors": [
    {
      "message": "用户未找到",
      "extensions": {
        "code": "USER_NOT_FOUND",
        "userId": "usr_1234567890"
      }
    }
  ]
}
\`\`\`
```

### 示例 3：认证文档

```markdown
## 认证

所有 API 请求都需要使用 Bearer 令牌进行认证。

### 获取令牌

**端点：** `POST /api/v1/auth/login`

**请求：**
\`\`\`json
{
  "email": "user@example.com",
  "password": "your-password"
}
\`\`\`

**响应：**
\`\`\`json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 3600,
  "refreshToken": "refresh_token_here"
}
\`\`\`

### 使用令牌

在 Authorization 头中包含令牌：

\`\`\`
Authorization: Bearer YOUR_TOKEN
\`\`\`

### 令牌过期

令牌在 1 小时后过期。使用刷新令牌获取新的访问令牌：

**端点：** `POST /api/v1/auth/refresh`

**请求：**
\`\`\`json
{
  "refreshToken": "refresh_token_here"
}
\`\`\`
```

## 最佳实践

### ✅ 做到这一点

- **保持一致性** - 所有端点使用相同的格式
- **包含示例** - 提供多种语言的可用代码示例
- **记录错误** - 列出所有可能的错误代码及其含义
- **显示真实数据** - 使用真实的示例数据，而不是 "foo" 和 "bar"
- **解释参数** - 描述每个参数的作用及其约束
- **版本 API** - 在 URL 中包含版本号（/api/v1/）
- **添加时间戳** - 显示文档最后更新时间
- **链接相关端点** - 帮助用户发现相关功能
- **包含速率限制** - 记录任何速率限制策略
- **提供 Postman 集合** - 使测试您的 API 更容易

### ❌ 不要这样做

- **不要遗漏错误情况** - 用户需要知道可能出错的情况
- **不要使用模糊的描述** - "获取数据" 没有帮助
- **不要忘记认证** - 始终记录认证要求
- **不要忽略边缘情况** - 记录分页、过滤、排序
- **不要留下损坏的示例** - 测试所有代码示例
- **不要使用过时的信息** - 保持文档与代码同步
- **不要过于复杂** - 保持简单和可扫描
- **不要忘记响应头** - 记录重要的头信息

## 文档结构

### 推荐部分

1. **简介**
   - API 的功能
   - 基础 URL
   - API 版本
   - 支持联系方式

2. **认证**
   - 如何认证
   - 令牌管理
   - 安全最佳实践

3. **快速入门**
   - 入门简单示例
   - 常见用例演示

4. **端点**
   - 按资源组织
   - 每个端点的详细信息

5. **数据模型**
   - 模式定义
   - 字段描述
   - 验证规则

6. **错误处理**
   - 错误代码参考
   - 响应格式
   - 排错指南

7. **速率限制**
   - 限制和配额
   - 检查头信息
   - 处理速率限制错误

8. **变更日志**
   - API 版本历史
   - 不兼容变更
   - 废弃通知

9. **SDK 和工具**
   - 官方客户端库
   - Postman 集合
   - OpenAPI 规范

## 常见陷阱

### 问题：文档与代码不同步
**症状：** 示例无法工作，参数错误，端点返回不同数据
**解决方案：**
- 从代码注释/注解生成文档
- 使用 Swagger/OpenAPI 等工具
- 添加 API 测试以验证文档
- 每次 API 变更时审查文档

### 问题：缺少错误文档
**症状：** 用户不知道如何处理错误，支持工单增加
**解决方案：**
- 记录所有可能的错误代码
- 提供清晰的错误消息
- 包含排错步骤
- 显示示例错误响应

### 问题：示例无法工作
**症状：** 用户无法入门，挫败感增加
**解决方案：**
- 测试每个代码示例
- 使用真实、可工作的端点
- 提供完整的示例（而不是片段）
- 提供沙箱环境

### 问题：参数要求不明确
**症状：** 用户发送无效请求，验证错误
**解决方案：**
- 清晰标记必填和可选参数
- 记录数据类型和格式
- 显示验证规则
- 提供示例值

## 工具和格式

### OpenAPI/Swagger
生成交互式文档：
```yaml
openapi: 3.0.0
info:
  title: 我的 API
  version: 1.0.0
paths:
  /users:
    post:
      summary: 创建新用户
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
```

### Postman 集合
导出集合以便轻松测试：
```json
{
  "info": {
    "name": "我的 API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "创建用户",
      "request": {
        "method": "POST",
        "url": "{{baseUrl}}/api/v1/users"
      }
    }
  ]
}
```

## 相关技能

- `@doc-coauthoring` - 用于协作文档编写
- `@copywriting` - 用于清晰、用户友好的描述
- `@test-driven-development` - 确保 API 行为与文档一致
- `@systematic-debugging` - 用于排错 API 问题

## 额外资源

- [OpenAPI 规范](https://swagger.io/specification/)
- [REST API 最佳实践](https://restfulapi.net/)
- [GraphQL 文档](https://graphql.org/learn/)
- [API 设计模式](https://www.apiguide.com/)
- [Postman 文档](https://learning.postman.com/docs/)

---

**小贴士：** 将您的 API 文档尽可能靠近您的代码。使用从代码注释生成文档的工具，以确保它们保持同步！
