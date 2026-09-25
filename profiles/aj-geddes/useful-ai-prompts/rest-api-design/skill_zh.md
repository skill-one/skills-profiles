# REST API 设计

## 目录

- [概述](#概述)
- [使用场景](#使用场景)
- [快速入门](#快速入门)
- [参考指南](#参考指南)
- [最佳实践](#最佳实践)

## 概述

设计直观、一致，并遵循面向资源架构的行业最佳实践的 REST API。

## 使用场景

- 设计新的 RESTful API
- 创建端点结构
- 定义请求/响应格式
- 实现API版本控制
- 文档化API规范
- 重构现有API

## 快速入门

最小可工作示例：

```
✅ 良好的资源名称（名词，复数）
GET    /api/users
GET    /api/users/123
GET    /api/users/123/orders
POST   /api/products
DELETE /api/products/456

❌ 不良的资源名称（动词，不一致）
GET    /api/getUsers
POST   /api/createProduct
GET    /api/user/123  (不一致的单数/复数)
```

## 参考指南

`references/` 目录中的详细实现：

| 指南 | 内容 |
|---|---|
| [资源命名](references/resource-naming.md) | 资源命名，HTTP 方法 & 操作 |
| [请求示例](references/request-examples.md) | 请求示例 |
| [查询参数](references/query-parameters.md) | 查询参数 |
| [响应格式](references/response-formats.md) | 响应格式 |
| [HTTP 状态码](references/http-status-codes.md) | HTTP 状态码，API 版本控制，认证 & 安全，速率限制标头 |
| [OpenAPI 文档](references/openapi-documentation.md) | OpenAPI 文档 |
| [完整示例：Express.js](references/complete-example-expressjs.md) | const express = require("express"); |

## 最佳实践

### ✅ 应该做

- 资源使用名词，而不是动词
- 集合使用复数名称
- 保持命名约定一致
- 返回适当的 HTTP 状态码
- 集合包含分页
- 提供过滤和排序选项
- 版本控制 API
- 使用 OpenAPI 进行彻底文档化
- 使用 HTTPS
- 实现速率限制
- 提供清晰的错误消息
- 日期使用 ISO 8601 格式

### ❌ 不应该做

- 端点名称中使用动词
- 错误返回 200
- 不必要地暴露内部 ID
- 资源过度嵌套（最多 2 级）
- 使用不一致的命名
- 忘记认证
- 返回敏感数据
- 未使用版本控制就破坏向后兼容性
