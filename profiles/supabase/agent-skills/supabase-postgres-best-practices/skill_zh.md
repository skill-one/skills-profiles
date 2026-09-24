# Supabase Postgres 最佳实践

Supabase 维护的 Postgres 全面性能优化指南，涵盖 8 个类别的规则，按影响程度排序，用于指导自动化查询优化和模式（schema）设计。

## 适用场景

参考以下指南时：
- 编写 SQL 查询或设计模式（schema）
- 实施索引或查询优化
- 审查数据库性能问题
- 配置连接池或扩展（scaling）
- 针对 Postgres 特定特性进行优化
- 使用行级安全（RLS）

## 规则类别（按优先级）

|---|---|---|---|
|---|---|---|---|

## 使用方法

阅读单个规则文件以获取详细解释和 SQL 示例：

```
references/query-missing-indexes.md
references/query-partial-indexes.md
references/_sections.md
```

每个规则文件包含：
- 简要说明其重要性
- 带解释的 SQL 错误示例
- 带解释的 SQL 正确示例
- 可选的 EXPLAIN 输出或指标
- 额外背景和参考资料
- Supabase 特定说明（如适用）

## 参考资料

- https://www.postgresql.org/docs/current/
- https://supabase.com/docs
- https://wiki.postgresql.org/wiki/Performance_Optimization
- https://supabase.com/docs/guides/database/overview
- https://supabase.com/docs/guides/auth/row-level-security
