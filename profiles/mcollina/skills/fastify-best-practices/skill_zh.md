## 何时使用

当你需要以下功能时，请使用此技能：
- 使用 Fastify 开发后端应用程序
- 实现 Fastify 插件和路由处理器
- 获取 Fastify 架构和模式的指导
- 使用 TypeScript 与 Fastify（移除类型）
- 使用 Fastify 的 inject 方法实现测试
- 配置验证、序列化和错误处理

## 快速入门

一个最小化的可运行 Fastify 服务器，立即开始：

```ts
import Fastify from 'fastify'

const app = Fastify({ logger: true })

app.get('/health', async (request, reply) => {
  return { status: 'ok' }
})

const start = async () => {
  await app.listen({ port: 3000, host: '0.0.0.0' })
}
start()
```

## 常见场景的推荐阅读顺序

- **新使用 Fastify？** 从 `plugins.md` → `routes.md` → `schemas.md` 开始
- **添加认证：** `plugins.md` → `hooks.md` → `authentication.md`
- **提升性能：** `schemas.md` → `serialization.md` → `performance.md`
- **设置测试：** `routes.md` → `testing.md`
- **进入生产环境：** `logging.md` → `configuration.md` → `deployment.md`

## 如何使用

阅读单个规则文件以获取详细的解释和代码示例：

- [rules/plugins.md](rules/plugins.md) - 插件开发和封装
- [rules/routes.md](rules/routes.md) - 路由组织和处理器
- [rules/schemas.md](rules/schemas.md) - JSON Schema 验证
- [rules/error-handling.md](rules/error-handling.md) - 错误处理模式
- [rules/hooks.md](rules/hooks.md) - 钩子和请求生命周期
- [rules/authentication.md](rules/authentication.md) - 认证和授权
- [rules/testing.md](rules/testing.md) - 使用 inject() 进行测试
- [rules/performance.md](rules/performance.md) - 性能优化
- [rules/logging.md](rules/logging.md) - 使用 Pino 进行日志记录
- [rules/typescript.md](rules/typescript.md) - TypeScript 集成
- [rules/decorators.md](rules/decorators.md) - 装饰器和扩展
- [rules/content-type.md](rules/content-type.md) - 内容类型解析
- [rules/serialization.md](rules/serialization.md) - 响应序列化
- [rules/cors-security.md](rules/cors-security.md) - CORS 和安全头部
- [rules/websockets.md](rules/websockets.md) - WebSocket 支持
- [rules/database.md](rules/database.md) - 数据库集成模式
- [rules/configuration.md](rules/configuration.md) - 应用程序配置
- [rules/deployment.md](rules/deployment.md) - 生产部署
- [rules/http-proxy.md](rules/http-proxy.md) - HTTP 代理和 reply.from()

## 核心原则

- **封装**：Fastify 的插件系统提供自动封装
- **先定义模式**：为验证和序列化定义模式
- **性能**：Fastify 针对速度进行了优化；正确使用其功能
- **Async/await**：所有处理器和钩子都支持异步函数
- **最小依赖**：优先使用 Fastify 的内置功能和官方插件
