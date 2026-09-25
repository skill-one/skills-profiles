# OpenAPI 转换为 TypeScript

将 OpenAPI 3.0 规范转换为 TypeScript 接口和类型守卫。

**输入：** OpenAPI 文件（JSON 或 YAML）
**输出：** 包含接口和类型守卫的 TypeScript 文件

## 使用场景

- "从 openapi 生成类型"
- "将 openapi 转换为 typescript"
- "创建 API 接口"
- "从规范生成类型"

## 工作流程

1. 请求 OpenAPI 文件路径（如果未提供）
2. 读取并验证文件（必须是 OpenAPI 3.0.x）
3. 从 `components/schemas` 提取模式
4. 从 `paths` 提取端点（请求/响应类型）
5. 生成 TypeScript（接口 + 类型守卫）
6. 询问保存位置（默认：当前目录中的 `types/api.ts`）
7. 写入文件

## OpenAPI 验证

处理前检查：

```
- 字段 "openapi" 必须存在且以 "3.0" 开头
- 字段 "paths" 必须存在
- 字段 "components.schemas" 必须存在（如果有类型）
```

如果无效，报告错误并停止。

## 类型映射

### 基本类型

| OpenAPI     | TypeScript   |
|-------------|--------------|
| `string`    | `string`     |
| `number`    | `number`     |
| `integer`   | `number`     |
| `boolean`   | `boolean`    |
| `null`      | `null`       |

### 格式修饰符

| 格式        | TypeScript              |
|-------------|-------------------------|
| `uuid`      | `string`（注释 UUID）  |
| `date`      | `string`（注释日期）  |
| `date-time` | `string`（注释 ISO）  |
| `email`     | `string`（注释邮箱）  |
| `uri`       | `string`（注释 URI）  |

### 复杂类型

**对象：**
```typescript
// OpenAPI: type: object, properties: {id, name}, required: [id]
interface Example {
  id: string;      // required: no ?
  name?: string;   // optional: with ?
}
```

**数组：**
```typescript
// OpenAPI: type: array, items: {type: string}
type Names = string[];
```

**枚举：**
```typescript
// OpenAPI: type: string, enum: [active, draft]
type Status = "active" | "draft";
```

**oneOf（联合类型）：**
```typescript
// OpenAPI: oneOf: [{$ref: Cat}, {$ref: Dog}]
type Pet = Cat | Dog;
```

**allOf（交集/扩展）：**
```typescript
// OpenAPI: allOf: [{$ref: Base}, {type: object, properties: ...}]
interface Extended extends Base {
  extraField: string;
}
```

## 代码生成

### 文件头部

```typescript
/**
 * 自动生成自：{source_file}
 * 生成于：{timestamp}
 *
 * 手动编辑请勿修改 - 从 OpenAPI 模式重新生成
 */
```

### 接口（来自 `components/schemas`）

对于 `components/schemas` 中的每个模式：

```typescript
export interface Product {
  /** 产品唯一标识符 */
  id: string;

  /** 产品标题 */
  title: string;

  /** 产品价格 */
  price: number;

  /** 创建时间戳 */
  created_at?: string;
}
```

- 使用 OpenAPI 描述作为 JSDoc
- `required[]` 中的字段没有 `?`
- `required[]` 外的字段有 `?`

### 请求/响应类型（来自 `paths`）

对于 `paths` 中的每个端点：

```typescript
// GET /products - 查询参数
export interface GetProductsRequest {
  page?: number;
  limit?: number;
}

// GET /products - 响应 200
export type GetProductsResponse = ProductList;

// POST /products - 请求体
export interface CreateProductRequest {
  title: string;
  price: number;
}

// POST /products - 响应 201
export type CreateProductResponse = Product;
```

命名约定：
- `{Method}{Path}Request` 用于参数/请求体
- `{Method}{Path}Response` 用于响应

### 类型守卫

为每个主接口生成类型守卫：

```typescript
export function isProduct(value: unknown): value is Product {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    typeof (value as any).id === 'string' &&
    'title' in value &&
    typeof (value as any).title === 'string' &&
    'price' in value &&
    typeof (value as any).price === 'number'
  );
}
```

类型守卫规则：
- 检查 `typeof value === 'object' && value !== null`
- 对于每个必需字段：检查 `'field' in value`
- 对于基本字段：检查 `typeof`
- 对于数组：检查 `Array.isArray()`
- 对于枚举：检查 `.includes()`

### 错误类型（始终包含）

```typescript
export interface ApiError {
  status: number;
  error: string;
  detail?: string;
}

export function isApiError(value: unknown): value is ApiError {
  return (
    typeof value === 'object' &&
    value !== null &&
    'status' in value &&
    typeof (value as any).status === 'number' &&
    'error' in value &&
    typeof (value as any).error === 'string'
  );
}
```

## $ref 解析

当遇到 `{"$ref": "#/components/schemas/Product"}` 时：
1. 提取模式名称（`Product`）
2. 直接使用类型（不要内联解析）

```typescript
// OpenAPI: items: {$ref: "#/components/schemas/Product"}
// TypeScript:
items: Product[]  // 引用，非内联
```

## 完整示例

**输入（OpenAPI）：**
```json
{
  "openapi": "3.0.0",
  "components": {
    "schemas": {
      "User": {
        "type": "object",
        "properties": {
          "id": {"type": "string", "format": "uuid"},
          "email": {"type": "string", "format": "email"},
          "role": {"type": "string", "enum": ["admin", "user"]}
        },
        "required": ["id", "email", "role"]
      }
    }
  },
  "paths": {
    "/users/{id}": {
      "get": {
        "parameters": [{"name": "id", "in": "path", "required": true}],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {"$ref": "#/components/schemas/User"}
              }
            }
          }
        }
      }
    }
  }
}
```

**输出（TypeScript）：**
```typescript
/**
 * 自动生成自：api.openapi.json
 * 生成于：2025-01-15T10:30:00Z
 *
 * 手动编辑请勿修改 - 从 OpenAPI 模式重新生成
 */

// ============================================================================
// 类型
// ============================================================================

export type UserRole = "admin" | "user";

export interface User {
  /** UUID */
  id: string;

  /** 邮箱 */
  email: string;

  role: UserRole;
}

// ============================================================================
// 请求/响应类型
// ============================================================================

export interface GetUserByIdRequest {
  id: string;
}

export type GetUserByIdResponse = User;

// ============================================================================
// 类型守卫
// ============================================================================

export function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    typeof (value as any).id === 'string' &&
    'email' in value &&
    typeof (value as any).email === 'string' &&
    'role' in value &&
    ['admin', 'user'].includes((value as any).role)
  );
}

// ============================================================================
// 错误类型
// ============================================================================

export interface ApiError {
  status: number;
  error: string;
  detail?: string;
}

export function isApiError(value: unknown): value is ApiError {
  return (
    typeof value === 'object' &&
    value !== null &&
    'status' in value &&
    typeof (value as any).status === 'number' &&
    'error' in value &&
    typeof (value as any).error === 'string'
  );
}
```

## 常见错误

| 错误 | 操作 |
|------|------|
| OpenAPI 版本 != 3.0.x | 报告仅支持 3.0 |
| $ref 未找到 | 列出缺失的 ref |
| 未知类型 | 使用 `unknown` 并警告 |
| 循环引用 | 使用类型别名与延迟引用 |
