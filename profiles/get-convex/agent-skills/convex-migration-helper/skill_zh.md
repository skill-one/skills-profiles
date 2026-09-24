# Convex 迁移助手

在进行破坏性变更时，安全地迁移 Convex schema 和数据。

## 何时使用

- 为现有表添加新的必需字段
- 更改字段类型或结构
- 拆分或合并表
- 重命名或删除字段
- 从嵌套数据迁移到关联数据

## 不使用时

- 生产环境或开发环境无现有数据的全新 schema
- 添加无需回填的可选字段
- 添加需要迁移但无现有数据的新表
- 添加或删除索引且无正确性问题的
- 涉及 Convex schema 设计但无需迁移的问题

## 关键概念

### Schema 校验驱动工作流程

Convex 不允许您部署与静止数据不匹配的 schema。
这是塑造每一次迁移的根本约束：

- 如果现有文档没有该字段，则无法添加必需字段
- 如果现有文档仍有旧类型，则无法更改字段类型
- 如果现有文档仍然包含该字段，则无法从 schema 中移除该字段

这意味着迁移遵循可预测的模式：**拓宽 schema，迁移数据，收窄 schema**。

### 在线迁移

Convex 迁移在线运行，即应用继续处理请求，同时数据以批次形式异步更新。在迁移窗口期间，您的代码必须同时处理旧版和新版数据格式。

### 优先使用新字段而非更改类型

在改变数据结构时，创建新字段而非修改现有字段。这使转换更安全，且更易于回滚。

### 不要删除数据

除非您完全确定，否则优先弃用字段而非删除它们。将该字段标记为 `v.optional`，并添加代码注释说明该字段已弃用及其存在的原因。

## 安全变更（无需迁移）

### 添加可选字段

```typescript
// Before
users: defineTable({
  name: v.string(),
});

// After - safe, new field is optional
users: defineTable({
  name: v.string(),
  bio: v.optional(v.string()),
});
```

### 添加新表

```typescript
posts: defineTable({
  userId: v.id("users"),
  title: v.string(),
}).index("by_user", ["userId"]);
```

### 添加索引

```typescript
users: defineTable({
  name: v.string(),
  email: v.string(),
}).index("by_email", ["email"]);
```

## 破坏性变更：部署流程

每一次破坏性迁移都遵循相同的多部署模式：

**部署 1 - 拓宽 schema：**

1. 更新 schema 以允许旧版和新版格式（例如，添加可选的新字段）
2. 更新代码以在读取时同时处理两种格式
3. 更新代码以对新文档写入新版格式
4. 部署

**部署之间 - 迁移数据：**

5. 运行迁移以回填现有文档
6. 验证所有文档均已迁移

**部署 2 - 收窄 schema：**

7. 更新 schema 仅要求新版格式
8. 移除处理旧版格式的代码
9. 部署

## 使用迁移组件

对于任何非简单的迁移，请使用
[`@convex-dev/migrations`](https://www.convex.dev/components/migrations)
组件。它负责批处理、基于游标的分页、状态跟踪、失败后恢复、试运行以及进度监控。

请参阅 `references/migrations-component.md`，了解安装、设置、使用 `npx convex run migrations:myMigration` 直接定义并运行迁移、试运行、状态监控以及配置选项。

## 常见迁移模式

请参阅 `references/migration-patterns.md`，了解包含代码示例的完整模式，涵盖：

- 添加必需字段
- 删除字段
- 更改字段类型
- 将嵌套数据拆分为独立的表
- 清理孤立文档
- 零停机策略（双写、双读）
- 小型表的快捷方式（不使用组件直接使用单一 internalMutation）
- 验证迁移已完成

## 常见陷阱

1. **在迁移数据前将字段设为必需**：Convex 会拒绝部署，因为现有文档缺少该字段。始终先拓宽 schema。
2. **在大型表上使用 `.collect()`**：会触达事务限制或导致超时。请使用迁移组件进行正确的批量分页。`.collect()` 仅对您已知为小型表的场景是安全的。
3. **迁移前未写入新版格式**：迁移窗口期间创建的文档会被遗漏，导致迁移“完成”后仍有未迁移的数据。
4. **跳过试运行**：使用 `dryRun: true` 在提交变更到生产数据前验证迁移逻辑。可在问题触及真实文档前发现错误。
5. **过早删除字段**：优先使用 `v.optional` 并添加注释进行弃用。只有在您确信数据不再需要且没有代码引用它时，才进行删除。
6. **使用 cron 进行迁移批次**：迁移组件通过内部递归调度处理批处理。cron 需要手动清理并额外进行一次部署来移除。

## 迁移清单

- [ ] 识别破坏性变更并规划多部署流程
- [ ] 更新 schema 以允许旧版和新版格式
- [ ] 更新代码以在读取时同时处理两种格式
- [ ] 更新代码以对新文档写入新版格式
- [ ] 部署拓宽后的 schema 和更新后的代码
- [ ] 使用 `@convex-dev/migrations` 组件定义迁移
- [ ] 使用 `npx convex run migrations:myMigration '{"dryRun": true}'` 进行测试
- [ ] 使用 `npx convex run migrations:myMigration` 直接运行迁移，并监控状态
- [ ] 验证所有文档均已迁移
- [ ] 更新 schema 仅要求新版格式
- [ ] 清理处理旧版格式的代码
- [ ] 部署最终 schema 和代码
- [ ] 确认稳定后移除迁移代码
