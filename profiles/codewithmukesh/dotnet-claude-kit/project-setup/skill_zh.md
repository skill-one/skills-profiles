# 项目设置 — 技术栈顾问

这项技能拥有一个核心功能：推荐技术栈的默认配置及其原因。使用它的工作流存在于其他地方：

- **初始化项目 / 生成 CLAUDE.md** → `dotnet-init`（交互式流程，架构问卷，CLAUDE.md 生成）
- **评估现有代码库** → `health-check`（标准的 8 维度评分评估）
- **EF Core 模式，NuGet 或 .NET 版本迁移** → `migrate`
- **选择架构** → `architecture-advisor`（推荐前必须询问）

## 核心原则

1. **推荐默认值，解释原因，让用户选择** — 每个维度都有默认配置，但默认值只是起点而非强制要求。用一句话说明权衡利弊，使选择更明智。
2. **优先使用内置 .NET 而非第三方** — `HybridCache` 优于 Redis 客户端包装，内置速率限制优于包，内置 OpenAPI 优于 Swashbuckle。更少的依赖意味着更少的许可意外和升级中断。
3. **许可感知选择** — MediatR (v13+)，MassTransit (v9+) 和 FluentAssertions (v8+) 已转为商业许可。工具默认使用 MIT 许可的替代方案：Mediator，Wolverine，纯 xUnit 断言。
4. **后期添加消息传递，而非永不添加** — 大多数项目第一天不需要消息总线。默认为“无（后期添加）”，当异步工作流实际出现时使用 Wolverine。

## 模式

### 技术栈维度和默认值

| 维度 | 选项 | 默认值 | 原因 |
|-------|------|--------|------|
| 数据库 | PostgreSQL，SQL Server，SQLite | PostgreSQL | 开源，非 SQL Server 的最佳 EF Core 提供商，一流的 Testcontainers 支持 |
| 认证 | JWT Bearer，OIDC (Keycloak/Auth0)，无 | JWT Bearer | API 最简单的安全默认值；当存在外部身份提供者时切换到 OIDC |
| 缓存 | HybridCache，Redis，无 | HybridCache | 内置，拥塞保护，L1+L2 — 仅将其作为 L2 后端添加 Redis |
| 消息传递 | Wolverine (RabbitMQ)，MassTransit，无 | 无（后期添加） | 过早添加消息会增加运维负担；需要时使用 MIT 许可的 Wolverine |
| 可观察性 | Serilog + OpenTelemetry，基础日志记录 | Serilog + OTEL | 从第一天开始就有结构化日志和跟踪；后期改造不划算 |
| 弹性 | Polly v8 管道，基础重试 | Polly v8 | `AddStandardResilienceHandler()` 一行代码即可实现生产级默认值 |
| API 文档 | 内置 OpenAPI + Scalar | OpenAPI + Scalar | 框架维护的规范生成；Scalar 替代 Swagger UI |
| 测试 | xUnit v3 + Testcontainers | xUnit v3 + Testcontainers | 测试中使用真实数据库；内存提供者隐藏真实错误 |

选定维度后，`dotnet-init` 将它们烘焙到生成的 CLAUDE.md 中，每个选择都映射到在相应工作区域（`ef-core`，`authentication`，`caching`，`messaging`，`serilog`，`opentelemetry`，`resilience`，`openapi`，`scalar`，`testing`）工作时加载的技能。

## 反模式

### 未询问就强制指定技术栈

```
# BAD — 假设工具默认值适用于所有场景
"你应该使用 PostgreSQL 和 Wolverine。"
# 团队全公司使用 SQL Server 且没有任何异步工作流。

# GOOD — 默认值 + 权衡 + 询问
"工具默认值是 PostgreSQL（最佳的 OSS EF 提供商）。任何组织约束 — 现有 SQL Server 许可证，DBA 支持 — 应该覆盖它吗？"
```

### 重复运行不属于本技能的工作流

```
# BAD — 从本技能临时编排健康评分或初始化流程
"让我在 5 个类别中对你的代码库进行评分..."
# 该评分与标准评分冲突。

# GOOD — 路由到所有者
Init/CLAUDE.md → dotnet-init | 评估 → health-check | 升级 → migrate
```

## 决策指南

| 场景 | 路由到 |
|------|--------|
| "为 Claude Code 设置这个项目" | `dotnet-init` |
| "我应该使用哪个数据库/认证/缓存？" | 本技能 — 上表 |
| "这个代码库的健康状况如何？" | `health-check` |
| "升级到 .NET 10" / "更新包" | `migrate` |
| "哪种架构适合？" | `architecture-advisor` |
| 技术栈选定，准备构建 | 为第一个功能使用 `scaffold` |
