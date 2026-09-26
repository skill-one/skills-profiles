# 后端开发指南

使用此技能进行 `web/`、`worker/` 和 `packages/shared/` 范围内的后端和 API 工作。

## 适用场景

- 创建或修改 tRPC 路由器和过程
- 创建或修改公共 API 端点
- 创建或修改队列处理器、生产者或基于队列的工作流
- 构建或重构后端服务和存储库
- 处理后端认证、中间件、验证或可观察性
- 更新 Prisma 或 ClickHouse 访问模式
- 向共享后端代码添加字段、选项、标志或枚举成员
- 添加或修复后端测试

## 如何阅读此技能

- 当任务跨越多个后端领域或需要端到端参考图时，使用此 `SKILL.md`。
- 当范围较窄时，仅阅读与工作匹配的特定参考文件。
- 如果任务引入了用户提供的 URL、出站 HTTP 请求、新集成或涉及密钥、RBAC 或重定向处理，则在设计或实现更改之前，还需加载共享的 [`security-review`](../security-review/SKILL.md) 技能。

## 添加新概念前的准备

在将字段添加到共享模式或有效载荷、在共享签名上添加选项或标志、添加枚举成员、添加环境切换或创建仅适用于一个调用者的分支之前——或者在得出无需更改的结论之前——请阅读 [`references/new-concepts.md`](references/new-concepts.md)。

## 快速入门清单

### UI：新的 tRPC 功能

- 在 `features/[feature]/server/*Router.ts` 中定义路由器。
- 使用适当的受保护或公共过程。
- 使用 JWT 感知的中间件进行认证。
- 检查项目/资源访问和授权。
- 使用 Zod v4 验证输入。
- 将业务逻辑放在服务文件中。
- 在相关位置使用 `traceException` 进行错误处理。
- 在 `__tests__/` 中添加单元或集成测试。
- 通过 `env.mjs` 访问配置。

### 现有端点：添加字段或过滤器

在编码之前，将更改分类为新的端点、现有端点的添加字段/过滤器或语义替换/破坏性更改。

对于添加字段/过滤器：

- 重用规范谓词。对于已经支持字段组选择的端点，重用其现有的字段组/投影路径。
- 保留端点现有的响应契约：对于字段组端点，使用正常的可选部分行模式和转换路径；对于普通端点，保留严格的响应模式和转换路径。
- 除非兼容性要求，否则不要创建 API 版本特定的字段集、转换或“必须选择”的运行时断言。
- 扩展示例和契约；不要替换现有的过滤器示例。
- 按唯一边界编写一个测试，而不是按触摸的文件编写一个测试。

### SDKs：新的公共 API 端点

- 在 `pages/api/public/` 中创建路由。
- 用 `withMiddlewares` 和 `createAuthedProjectAPIRoute` 包装它。
- 在 `features/public-api/types/` 中定义类型。
- 使用基本认证进行认证。
- 使用 Zod 模式验证查询、正文和响应。
- 在路径和模式中包含 API 版本控制。
- 更新 Fern API 定义以匹配 TypeScript 类型。
- 在 `__tests__/async/` 中添加端到端测试。

### Worker：新的队列处理器

- 在 `worker/src/queues/` 中创建处理器。
- 在 `packages/shared/src/server/queues` 中定义队列类型。
- 将业务逻辑放在 `features/` 或 `worker/src/features/` 中。
- 区分失败的工作和应该记录错误但成功的工作。
- 在 `app.ts` 中的 `WorkerManager` 中注册队列。
- 添加工作 vitest 覆盖率。

## 核心原则

- tRPC 过程、公共 API 路由和队列处理器将业务逻辑委托给服务。
- 通过 `env.mjs` 访问配置；不要在环境设置外直接读取 `process.env`。
- 使用 Zod v4 验证所有外部输入。
- 直接使用 Prisma 进行简单的 CRUD，使用存储库进行复杂的查询访问。
- 使用共享代码已有的词汇表表达新需求；将概念添加到共享抽象是最后的手段，而不是首选。
- 使用 OpenTelemetry 和 DataDog 进行后端可观察性。
- 始终通过 `projectId` 过滤项目范围的数据库查询。
- 保持 Fern API 定义与公共 TypeScript API 合约同步。
- 保持后端测试独立且并行安全。

## 活用示例

- 具有项目认证和 Zod 输入的 tRPC 路由器：`web/src/features/events/server/eventsRouter.ts`。
- 具有中间件和类型化请求/响应模式的公共 API 路由：`web/src/pages/api/public/datasets/index.ts`。
- 具有类型化工作、日志记录和重试行为的 Worker 队列处理器：`worker/src/queues/evalQueue.ts`。
- Prisma 和 ClickHouse 的租户过滤器：`references/database-patterns.md`。

## 命名约定

- tRPC 路由器：`camelCaseRouter.ts`，例如 `datasetRouter.ts`。
- 服务：在功能服务器目录中的 `service.ts`。
- 队列处理器：`camelCaseQueue.ts`，例如 `evalQueue.ts`。
- 公共 API 路由：使用连字符命名的文件，例如 `dataset-items.ts`。

## 需要避免的反模式

- 路由器或过程中包含业务逻辑。
- 直接使用 `process.env` 而不是 `env.mjs` / `env.ts`。
- 缺少错误处理。
- 缺少输入验证。
- 租户范围查询缺少 `projectId` 过滤器。
- 使用 `console.log` 而不是 `logger` / `traceException`。

## 参考图

| 主题                               | 当你需要阅读时                                                           | 文件                                                                               |
| ----------------------------------- | ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| 架构和包边界                       | 你需要 web/worker/shared 分割、请求流或队列生命周期                       | [references/architecture-overview.md](references/architecture-overview.md)         |
| 路由和控制器                       | 你正在编写 tRPC 过程、公共 API 路由或队列入口点                           | [references/routing-and-controllers.md](references/routing-and-controllers.md)     |
| 中间件和认证                       | 你正在更改请求认证、权限或中间件组合                                     | [references/middleware-guide.md](references/middleware-guide.md)                   |
| 服务和存储库                       | 你正在放置业务逻辑、存储库代码或 DI 模式                                 | [references/services-and-repositories.md](references/services-and-repositories.md) |
| 数据库访问                         | 你正在触摸 Prisma、ClickHouse、租户过滤器或查询模式                       | [references/database-patterns.md](references/database-patterns.md)                 |
| 共享代码中的新概念               | 你正在向共享抽象添加字段、选项、标志或枚举成员                           | [references/new-concepts.md](references/new-concepts.md)                            |
| 配置                               | 你正在添加环境变量、启动配置或运行时切换                                 | [references/configuration.md](references/configuration.md)                         |
| 测试                               | 你正在添加或更新后端测试                                                 | [references/testing-guide.md](references/testing-guide.md)                         |
