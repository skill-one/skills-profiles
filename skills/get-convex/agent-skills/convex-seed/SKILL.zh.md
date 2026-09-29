---
name: convex-seed
description: 将数据种子或导入到 Convex 数据库中。
---

<!-- GENERATED from convex-agents content/capabilities/seed.json — do not edit by手。 -->

# Seed / 导入数据

通过内部变异 seed 函数（可重新运行）或 `npx convex import` 填充表格，匹配模式。

## 工作流

1. 对于 fixtures：编写一个内部变异来插入示例行；使用 `npx convex run` 运行它。
2. 对于批量导入：将数据塑形到模式，并使用 `npx convex import`。
3. 使 seeding 具有幂等性（先清除后插入或使用 upsert）以便安全地重新运行。
4. 验证行数。

## 规则

- 通过内部变异或 convex import 进行 seeding，匹配验证器。
- 使 seeding 具有幂等性。
- 永远不要将秘密/个人身份信息 seeding 到共享部署中。
