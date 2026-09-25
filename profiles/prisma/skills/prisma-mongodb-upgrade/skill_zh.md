# Prisma MongoDB 升级路径

MongoDB 项目是 Prisma 群组中唯一没有升级到 Prisma 7 的项目：**v6 是 MongoDB 的经典 ORM 主要版本终点，v7 永远不会发布 MongoDB 连接器**。后续路径是 [Prisma Next](https://github.com/prisma/prisma-next)，其中 MongoDB 支持处于早期访问阶段，计划在 PostgreSQL GA 后发布正式版。这项技能明确了实际决策——迁移到 Prisma Next（推荐路径），或停留在 v6（存在硬性障碍）——并涵盖迁移机制。

**绝对不要做以下操作：**

- 绝对不要建议 MongoDB 项目“升级到 Prisma 7”。连接器不存在。`prisma-upgrade-v7` 指南不适用于 MongoDB 项目。
- 绝对不要通过将应用重写到 SQL 数据库来解决版本问题。更换数据库引擎是一个独立的、更重大的决策，不应隐式地做出。

## 版本现状

| 版本 | MongoDB 状态 |
|------|--------------|
| Prisma ORM v6 | 完全支持 (`mongodb` 提供者)；最新 6.x 是当前稳定路径；维护分支 |
| Prisma ORM v7 | **无 MongoDB 连接器——永远不是选项** |
| Prisma Next | MongoDB 支持处于 **早期访问** 状态，积极开发中，计划在 PostgreSQL GA 后发布——MongoDB 项目的后续路径 |

## 决策要点

**迁移到 Prisma Next 是推荐路径。** Prisma Next 中的 MongoDB 支持处于早期访问阶段：功能完善且快速迭代，计划在 PostgreSQL GA 后发布正式版——Prisma 团队希望 MongoDB 用户尽早迁移并提供反馈。迁移机制在参考资料中有详细说明。

**在存在硬性障碍的情况下继续使用最新 v6 也是一个合理选择**——直白地说：Next 的 MongoDB 界面尚未封装事务（底层驱动可直接使用；预计很快会改变），且 1.0 版本前的次级版本可能包含已发布的升级方案中的破坏性变更。

### 决策表

| 信号 | 方向 |
|------|------|
| 以下无障碍 | 迁移到 Next；运行 `verify-cutover-checklist` 并向 Prisma 团队提供反馈 |
| 绿色字段 / 原型 / 内部工具 | 迁移到 Next |
| 代码库使用多文档事务 (`$transaction`)——使用 grep 检查，不要询问 | 首先规划原始驱动器会话等效方案（见 `client-api-mapping`），或停留在 v6 直至界面封装器发布 |
| 团队无法承受次级版本间的 1.0 版本前破坏性升级 | 直至 GA 停留在 v6 |
| 风险规避但感兴趣 | 在副本上运行分阶段 Next 循环（见 `verify-cutover-checklist`），然后迁移 |

注意：事务差距预计很快会关闭——当界面事务合并到 Prisma Next 时，本节将更新。

### 如果停留在 v6：卫生措施（有意停留，非忽视）

- 将 Prisma 包固定到最新 6.x 线，并继续获取 6.x 补丁版本。
- 跟踪 6.x 线的 Prisma 发布说明和安全公告。
- 保持经典 v6 MongoDB 设置：`url = env("DATABASE_URL")` 在模式中，`db push` 工作流，无 SQL 驱动器适配器（见 `prisma-database-setup` 获取 v6 MongoDB 结构）。
- 在 Prisma Next 的 MongoDB GA 时，或尝试早期访问的障碍解决时重新评估。

## 参考资料

| 参考资料 | 涵盖内容 |
|----------|----------|
| `references/decision-stay-or-migrate.md` | 完整决策框架、障碍检查和停留卫生细节 |
| `references/schema-contract-mapping.md` | v6 模式 (`mongodb` 提供者，`@db.ObjectId`，复合类型) → Next 合同概念 |
| `references/client-api-mapping.md` | v6 客户端调用 → Next 等效方案，包括原始逃逸通道和事务——名称映射，功能对等性不保证 |
| `references/migrations-mapping.md` | v6 仅 `db push` 故事 → Next 的计划/迁移/验证/签名流程 |
| `references/verify-cutover-checklist.md` | 无数据迁移验证：相同数据库、索引对等性、切换前分阶段循环 |

## 验证信息

本技能中关于 Prisma Next 的行为性声明已针对 [prisma/prisma-next](https://github.com/prisma/prisma-next) 提交 `a2791c5dd59d579b4b3052942ae7f8fe5e2ee852`（1.0 版本前，约 v0.14/0.15 线）进行验证。Prisma Next 在早期访问阶段快速迭代：**在采取任何 Next 方面的声明前，请针对实际安装的版本进行验证**（检查项目的 `@prisma-next/*` 版本以及与它一起安装的 prisma-next 技能）。Next 的 MongoDB 目标需要 MongoDB 8.0+，并期望 `mongodb@^7` 作为用户提供的依赖项。

## 交接规则

本技能是 **发现桥梁**，而非 Prisma Next 自身文档的替代品。项目切换到 Prisma Next 后，运行 Prisma Next 的 `init`/技能安装，并遵循其自身技能（快速启动、合同、查询、迁移、运行时）进行日常工作——不要继续使用本技能的摘要。
