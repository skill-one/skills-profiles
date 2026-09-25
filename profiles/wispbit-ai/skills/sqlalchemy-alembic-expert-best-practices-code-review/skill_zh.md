# SQLAlchemy & Alembic 专家最佳实践

简洁、务实、有主见。仅包含编写生产级 SQLAlchemy 和 Alembic 代码时需要关注的内容。

## 应用场景

在以下情况下参考这些指南：
- 编写用于模式变更的 Alembic 迁移脚本
- 创建或修改 SQLAlchemy 模型
- 通过 Alembic 添加索引、约束或外键
- 审查数据库迁移代码以确保安全性
- 重构现有数据库模式
- 优化查询模式或数据库性能

## 按优先级分类的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | 索引管理 | 关键-高 | `only-concurrent-indexes`, `verify-query-patterns-are-indexed` |
| 2 | 约束安全 | 高 | `unique-constraint`, `split-foreign-key`, `change-column-type` |
| 3 | 优化 | 中 | `split-check-constraint`, `limit-non-unique-index` |
| 4 | 索引效率 | 低 | `ensure-index-not-covered` |

## 快速参考

- `only-concurrent-indexes` - 在自动提交块中使用索引操作时始终使用 `postgresql_concurrently=True`
- `verify-query-patterns-are-indexed` - 确保 SQLAlchemy 查询已定义适当的索引
- `unique-constraint` - 将唯一约束创建拆分为并发索引+约束步骤
- `split-foreign-key` - 首先使用 `NOT VALID` 添加外键，然后单独验证
- `change-column-type` - 使用多步方法进行列类型变更以避免表锁定
- `split-check-constraint` - 首先使用 `NOT VALID` 添加检查约束，然后单独验证
- `limit-non-unique-index` - 为效率起见，将非唯一索引限制为最多三列
- `ensure-index-not-covered` - 防止被复合索引已覆盖的冗余索引

## 使用方法

阅读单个规则文件以获取详细说明和代码示例：

```
rules/only-concurrent-indexes.md
rules/verify-query-patterns-are-indexed.md
rules/unique-constraint.md
rules/split-foreign-key.md
rules/change-column-type.md
rules/split-check-constraint.md
rules/limit-non-unique-index.md
rules/ensure-index-not-covered.md
```

每个规则文件包含：
- 解释为什么它很重要
- 影响级别和描述
- 带有说明的 SQLAlchemy/Alembic 不正确示例
- 最佳实践的正确实现
- 用于安全迁移的附加上下文
