<!-- GENERATED from convex-agents content/capabilities/seed.json — do not edit by hand. -->

# Seed / 导入数据

通过内部 mutation seed 函数（可重新运行）或 `npx convex import` 填充表格，匹配模式。

## 工作流

1. 对于 fixtures：编写一个插入示例行的内部 mutation；使用 `npx convex run` 运行它。
2. 对于批量导入：将数据塑形到模式，并使用 `npx convex import`。
3. 使 seeding 具有幂等性（先清除后插入或使用 upsert）以便安全地重新运行。
4. 验证行数。

## 规则

- 通过内部 mutation 或 convex import 进行 seeding，匹配验证器。
- 使 seeding 具有幂等性。
- 永不向共享部署中 seeding 密码/个人身份信息。
