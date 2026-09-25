# Prisma MongoDB 升级路径

MongoDB 项目是 Prisma 中唯一没有进入 Prisma 7 路径的项目群体：**v6 是 MongoDB 终结的经典 ORM 主流版本，且 v7 永远不会发布 MongoDB 连接器**。后继路径是 [Prisma Next](https://github.com/prisma/prisma-next)，其中 MongoDB 支持处于早期访问阶段（Early Access），并计划在 Postgres 之后正式发布（GA）。本技能明确了真正需要做出的决策——迁移至 Prisma Next（推荐路径），或在存在硬性阻碍时停留在 v6，并包含了迁移的机械机制。

**切勿执行以下任一操作：**

- 切勿建议 MongoDB 项目“升级到 Prisma 7”。该连接器在此处并不存在。`prisma-upgrade-v7` 指南不适用于 MongoDB 项目。
- 切勿通过将该应用重写至 SQL 数据库来解决版本问题。更改数据库引擎是另一项、规模大得多的决定，不能由你隐含做出。

## 版本格局

### 表格

版本 | MongoDB 状态
|---------|----------------
Prisma ORM v6 | 完全支持（`mongodb` 提供程序）；最新的 6.x 是当前稳定路径；维护线
Prisma ORM v7 | **无 MongoDB 连接器——从未成为选项**
Prisma Next | MongoDB 支持处于**早期访问**阶段，持续开发中，计划在 Postgres 之后正式发布（GA）—— MongoDB 项目的后继路径

## 前置决策

**迁移至 Prisma Next 是推荐路径。** Prisma Next 中的 MongoDB 支持处于早期访问阶段：功能可用且发展迅速，并计划在 Postgres 之后正式发布——且 Prisma 团队希望 MongoDB 用户尽早迁移并分享反馈。迁移的机械细节见相关参考资料。

**在存在硬性阻碍时，停留在最新的 v6 仍是一个合法选择**——直言不讳地说明：Next 的 MongoDB 门面尚未封装事务（底层驱动程序可直接使用；预计很快会改变），且 1.0 之前的次要版本可能携带在已发布的升级指南中。

### 决策表格

信号 | 方向
|--------|--------
以下暂无阻碍 | 迁移至 Next；运行 `verify-cutover-checklist` 并与 Prisma 团队分享反馈
绿地项目 / 原型 / 内部工具 | 迁移至 Next
代码库使用多文档事务（`$transaction`）——用 grep 检查，不要询问 | 首先规划原始驱动会话等价方案（见 `client-api-mapping`），或在门面封装落地前停留在 v6
团队无法在次要版本间吸收 1.0 之前的破坏性升级 | 停留在 v6 直至正式发布
风险规避但感兴趣 | 在副本上进行分阶段 Next 往返测试（见 `verify-cutover-checklist`），然后进行迁移

注意：事务缺口预计很快会闭合——本节将在 Prisma Next 中融合门面事务时进行更新。

### 若停留在 v6：维护卫生（有意的停留，而非疏忽）

- 将 Prisma 包锁定在最新的 6.x 线，并持续接收 6.x 补丁版本。
- 跟踪 6.x 线的 Prisma 发布说明和安全通告。
- 保持经典的 v6 MongoDB 配置：在模式中设置 `url = env("DATABASE_URL")`，采用 `db push` 工作流程，不使用 SQL 驱动适配器（关于 v6 MongoDB 配置的具体说明见 `prisma-database-setup`）。
- 在 Prisma Next 的 MongoDB 正式发布，或尝试早期访问所面临阻碍被解决时，重新评估。

## 参考文件

参考文件 | 涵盖内容
-----------|----------------
`references/decision-stay-or-migrate.md` | 完整的决策框架、阻碍检查，以及停留卫生细节
`references/schema-contract-mapping.md` | v6 模式（`mongodb` 提供程序、`@db.ObjectId`、复合类型）→ Next 契约概念
`references/client-api-mapping.md` | v6 客户端调用 → Next 等价方案，包括原始逃生机制与事务——名称对应，但一致性不保证
`references/migrations-mapping.md` | v6 仅 `db push` 方案 → Next 的规划/迁移/验证/签名流程
`references/verify-cutover-checklist.md` | 无数据迁移验证：同一数据库、索引一致性、切换前进行分阶段往返测试

## 经核验对照

关于本技能中 Prisma Next 的行为声明，已对照 [prisma/prisma-next](https://github.com/prisma/prisma-next) 的提交 `a2791c5dd59d579b4b3052942ae7f8fe5e2ee852`（1.0 之前，约 v0.14/0.15 版本线）进行验证。Prisma Next 在早期访问阶段进展迅速：**在基于任何 Prisma Next 方面的声明采取行动之前，必须对照实际安装的版本进行验证**（检查项目的 `@prisma-next/*` 版本以及随其安装的 prisma-next 技能）。Prisma Next 的 MongoDB 目标要求 MongoDB 8.0 及以上版本，并期望 `mongodb@^7` 作为用户提供的 peer 依赖。

## 交接规则

本技能是**探索桥梁**，而非替代 Prisma Next 自身文档的工具。项目切换至 Prisma Next 后，请运行 Prisma Next 的 `init`/技能安装，并遵循其自身的技能（快速入门、契约、查询、迁移、运行时）进行日常开发工作——不要继续仅依据本技能的摘要开展工作。
