# Supabase Postgres 最佳实践

由 Supabase 维护的 Postgres 性能优化综合指南。包含 8 个类别的规则，按影响程度排序，以指导自动查询优化和模式设计。

## 应用时机

在以下情况下参考这些指南：
- 编写 SQL 查询或设计模式
- 实现索引或查询优化
- 审查数据库性能问题
- 配置连接池或扩展
- 针对特定 Postgres 功能进行优化
- 使用行级安全 (RLS)

## 按优先级排序的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | 查询性能 | 关键 | `query-` |
| 2 | 连接管理 | 关键 | `conn-` |
| 3 | 安全与 RLS | 关键 | `security-` |
| 4 | 模式设计 | 高 | `schema-` |
| 5 | 并发与锁 | 中高 | `lock-` |
| 6 | 数据访问模式 | 中 | `data-` |
| 7 | 监控与诊断 | 低中 | `monitor-` |
| 8 | 高级功能 | 低 | `advanced-` |

## 使用方法

阅读单个规则文件获取详细说明和 SQL 示例：

```
references/query-missing-indexes.md
references/query-partial-indexes.md
references/_sections.md
```

每个规则文件包含：
- 规则重要性的简要说明
- 带说明的错误 SQL 示例
- 带说明的正确 SQL 示例
- 可选的 EXPLAIN 输出或指标
- 额外上下文和参考
- Supabase 特定说明（适用时）

## 参考

- https://www.postgresql.org/docs/current/
- https://supabase.com/docs
- https://wiki.postgresql.org/wiki/Performance_Optimization
- https://supabase.com/docs/guides/database/overview
- https://supabase.com/docs/guides/auth/row-level-security
