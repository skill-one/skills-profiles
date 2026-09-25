# Node.js Express 服务器

## 目录

- [概述](#概述)
- [使用场景](#使用场景)
- [快速入门](#快速入门)
- [参考指南](#参考指南)
- [最佳实践](#最佳实践)

## 概述

遵循行业最佳实践，使用 Express.js 创建具有正确路由、中间件链、认证机制和数据库集成的健壮应用程序。

## 使用场景

- 使用 Node.js 构建 REST API
- 实现服务器端请求处理
- 创建用于横切关注点的中间件链
- 管理认证和授权
- 从 Node.js 连接数据库
- 实现错误处理和日志记录

## 快速入门

最小可工作示例：

```javascript
const express = require("express");
const app = express();
const PORT = process.env.PORT || 3000;

// 中间件
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 路由
app.get("/health", (req, res) => {
  res.json({ status: "OK", timestamp: new Date().toISOString() });
});

// 错误处理
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(err.status || 500).json({
    error: err.message,
    requestId: req.id,
  });
});

app.listen(PORT, () => {
  console.log(`服务器运行在端口 ${PORT}`);
});
```

## 参考指南

`references/` 目录中的详细实现：

| 指南 | 内容 |
|---|---|
| [基本 Express 设置](references/basic-express-setup.md) | 基本 Express 设置 |
| [中间件链实现](references/middleware-chain-implementation.md) | 中间件链实现 |
| [数据库集成（使用 Sequelize 的 PostgreSQL）](references/database-integration-postgresql-with-sequelize.md) | 数据库集成（使用 Sequelize 的 PostgreSQL） |
| [使用 JWT 的认证](references/authentication-with-jwt.md) | 使用 JWT 的认证 |
| [具有 CRUD 操作的 RESTful 路由](references/restful-routes-with-crud-operations.md) | 具有 CRUD 操作的 RESTful 路由 |
| [错误处理中间件](references/error-handling-middleware.md) | 错误处理中间件 |
| [环境配置](references/environment-configuration.md) | 环境配置 |

## 最佳实践

### ✅ 应该做

- 使用中间件处理横切关注点
- 实现适当的错误处理
- 在处理之前验证输入数据
- 使用 async/await 进行异步操作
- 在受保护的路由上实现认证
- 使用环境变量进行配置
- 添加日志记录和监控
- 生产环境中使用 HTTPS
- 实现速率限制
- 保持路由处理程序专注且小巧

### ❌ 不应该做

- 沉默地处理错误
- 在代码中存储敏感数据
- 在路由中使用同步操作
- 忘记验证用户输入
- 在路由处理程序中实现认证
- 使用回调地狱（使用 Promise/async-await）
- 生产环境中暴露堆栈跟踪
- 仅依赖客户端验证
