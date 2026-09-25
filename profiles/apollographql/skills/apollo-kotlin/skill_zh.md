# Apollo Kotlin 指南

Apollo Kotlin 是一个强类型的 GraphQL 客户端，它可以从您的 GraphQL 操作和模式生成 Kotlin 模型，可用于 Android、JVM 和 Kotlin Multiplatform 项目。

## 流程

在添加或使用 Apollo Kotlin 时，请遵循以下流程：

- [ ] 确认目标平台（Android、JVM、KMP）、GraphQL 端点以及模式来源。
- [ ] 配置 Gradle 和代码生成，包括自定义标量
- [ ] 创建一个带有认证、日志记录和缓存的 `ApolloClient`。
- [ ] 实现 GraphQL 操作。
- [ ] 通过测试和错误处理验证行为。

## 参考

- [设置](references/setup.md) - Gradle 插件、模式下载、代码生成配置（包括标量）、客户端配置（认证、日志记录、拦截器）
- [操作](references/operations.md) - 查询、变异、订阅以及如何执行它们
- [缓存](references/caching.md) - 设置和使用规范化缓存
- [迁移指南](references/migrating-from-4.md) - 从 Apollo Kotlin 4 迁移

## 脚本

- [list-apollo-kotlin-versions.sh](scripts/list-apollo-kotlin-versions.sh) - 列出 Apollo Kotlin 的版本
- [list-apollo-kotlin-normalized-cache-versions.sh](scripts/list-apollo-kotlin-normalized-cache-versions.sh) - 列出 Apollo Kotlin 规范化缓存库的版本

## 关键规则

- 优先使用 Apollo Kotlin v5+ 版本。不要使用 v3 或更早版本。
- 将模式和操作保存在源代码管理中，以确保构建的可重复性。
