# 效果

在此技能中，使用当前的 Effect v4 API 和生产默认设置。已建立的项目的约定仍然优先，除非任务明确地更改它们。

## 源规则

在猜测之前检查这些：

- 最近的 `AGENTS.md` 和任何项目本地的 Effect 实践文档
- 项目固定的 `effect` 包源和版本
- 当安装的包无法回答问题时，检查当前的上游 Effect 源

## 分支选择器

仅读取与任务匹配的分支引用。

- 数据模型、模式、品牌、变体、可选键或解码器：读取 `references/SCHEMA.md`。
- 服务、模块表面、层、运行时连接、错误、`Effect.fn` 或测试服务：读取 `references/SERVICES_LAYERS.md`。
- 运行时配置、环境变量、`ConfigProvider` 或 `layerConfig`：读取 `references/CONFIG.md`。
- 重试、重复、轮询、退避、抖动、速率限制感知策略或传递循环：读取 `references/SCHEDULING.md`。
- 缓存、按键 TTL 缓存、去重并发查找或请求批处理：读取 `references/CACHING.md`。
- 流、事件源、异步可迭代对象、队列/发布订阅、分页、背压或流消费者：读取 `references/STREAMS.md`。
- 出站 HTTP 调用、Effect HttpClient、状态处理或 HTTP 速率限制：读取 `references/HTTP_CLIENTS.md`。
- Effect 测试、时间、睡眠、并发同步或伪造：读取 `references/TESTING.md`。

如果一个任务跨越多个分支，编辑之前读取所有匹配的文件。

## 核心默认值

- 使用 `Effect.gen(function* () { ... })` 组合工作流。
- 使用 `Effect.fn("Domain.operation")` 定义公共服务方法和非平凡的内部服务方法。
- 仅在内部辅助程序中故意不需要堆栈帧/跨度元数据时，使用 `Effect.fnUntraced`。
- 当代码库未针对当前服务标签样式标准化时，优先使用 `Context.Service` 应用服务。
- 使用 `Layer.effect(Service, Effect.gen(...))` 构建真实服务实现，并返回 `Service.of({ ... })`。
- 使用 `Schema.Struct(...)` 加上同名的 `interface` 对记录进行建模。
- 使用 `Schema.TaggedError` 对 typed Effect 错误进行建模。
- 通过 `Config` 读取运行时配置，而不是在应用程序逻辑中直接访问 `process.env`。
- 使用 `Schedule` 用于重试、重复、轮询、节拍和退避策略。
- 使用 `Stream` 用于在长时间内发出许多值并需要拉取、背压、中断或转换的有效源。
- 当 Effect 应用程序中的 Effect HTTP 客户端模块的 typed 错误、层和客户端转换有用时，优先使用 Effect HTTP 客户端模块进行出站 HTTP。
- 优先使用 Effect 感知的测试、显式层和确定性同步，而不是睡眠。
- 在不受信任的边界处优先使用解码器和 `schema.makeEffect(...)`；保留在受信任的构造中抛出 `schema.make(...)`，并且永远不要使用强制转换来跳过验证。

## 快速选择指南

- 普通对象记录：`Schema.Struct(...)` 加上同名的 `interface`。
- 标量 ID/值对象：约束品牌模式。
- 内部工作流决策或状态：`Data.TaggedEnum<...>` 加上 `Data.taggedEnum<...>()` 构造函数和穷尽 `$match`。
- 可重用的跨边界标记变体：`Schema.TaggedStruct(...)` 加上同名的 `interface`。
- 跨边界标记联合：`Schema.TaggedUnion(...)` 并带有 `.cases`、`.guards` 和 `.match`。
- 外部/自定义判别器，例如 `type`：当需要联合帮助程序时，使用 `Schema.Struct({ type: Schema.tag("variant"), ... })` 加上 `Schema.toTaggedUnion("type")`。
- 预期的 typed 失败：`Schema.TaggedError`。
- 未知边界有效负载：`Schema.decodeUnknownEffect(...)`。
- 服务边界：`Context.Service<Service, Interface>()(...)` 加上 `Layer.effect(...)` 加上 `Service.of(...)`。
- 公共或非平凡的内部服务方法：`Effect.fn("Domain.operation")`。
- 运行时配置：在层中读取的 `Config` 配方；在测试中使用 `ConfigProvider` 覆盖。
- 事件源：使用 `Stream.runForEach(...)` 消费并使用 `Effect.forkScoped` 在拥有层中分叉。
- 队列后端事件源：生产边界使用 `Queue`，消费者使用 `Stream.fromQueue(...)`。
- 广播事件源：`PubSub` / `Stream.fromPubSub(...)` 或 `SubscriptionRef` 用于最新值状态。
- 轮询工作程序：`runPass().pipe(Effect.repeat(Schedule.spaced(...)))`，在重复之前处理 typed pass 失败。
- 重试瞬态操作：`Effect.retry(...)` / `Effect.retryOrElse(...)` 带有有界的 `Schedule`。
- 带有 TTL 和并发查找去重的按键查找缓存：当它们的生命周期和淘汰模型适合时，优先使用 `Cache.make(...)` / 退出感知的 `Cache.makeWith(...)`。
- 缓存单个 Effect 结果：`Effect.cached(...)` / `Effect.cachedWithTTL(...)`。
- 将 N 个键批处理到一个后端调用（仅当存在真实的批处理端点时）：`Effect.request(...)` + `RequestResolver`。
- Effect 应用程序中的 HTTP 请求：优先使用 Effect `HttpClient` 加上请求/响应模式解码。
- HTTP 瞬态重试：`HttpClient.retryTransient(...)`。
- 时间敏感的测试：`TestClock`，而不是真实的睡眠。
- 并发/后台测试同步：`Deferred`、`Queue`、`Latch`、`Ref` 或显式测试钩子。

## 边界规则

- 保持 HTTP 处理程序瘦：解码输入、读取上下文、调用服务、将 typed 错误映射到传输响应。
- 将业务规则保留在服务或领域函数中，而不是传输处理程序中。
- 在适配器边界将 HTTP 客户端、SDK、CLI 和外部集成包装在命名效果中。
- 当值不是简单可信时，使用 Schema 或特定于 SQL 的帮助程序解码持久化行。
- 将提供者/网络调用保留在权威数据库事务之外。
- 仅当当前边界具有真实响应时才捕获或重试。
- 仅当操作已证明幂等性时才重试。
- 让耗尽的失败保持可见，除非边界具有真实的回退。

## 不要

- 不要使用 `as any`、非空断言或未检查的强制转换来抑制 Effect 类型问题。
- 不要将 `Schema.Class` 或 `Schema.TaggedClass` 作为默认的应用程序数据建模模式引入。
- 当 `Schema.TaggedError` 适用时，不要手滚 `_tag` 错误类。
- 当 typed 错误恢复就足够时，不要使用 cause 级别恢复。
- 不要使用 `Layer.mergeAll(...)` 或 `provideMerge(...)` 作为盲目使其编译的工具。
- 不要在 `Context.Reference` 默认后面隐藏必需的应用程序权限、凭证、持久化、传输或外部服务。
- 当有确定性同步原语可用时，不要在测试中添加任意的 `Effect.sleep(...)`。
- 当 `effect/Cache` 适用时，不要手滚 Map/TTL/修剪缓存或飞行中去重。
