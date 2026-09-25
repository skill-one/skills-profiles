# Prisma Next — 路由器

> **编辑你的数据合约。Prisma 会处理其余部分。**

此技能用于消除模糊的 Prisma Next 提示。当用户尚未确定特定的工作流程（例如 *"帮我使用 Prisma Next"*、*"解释 Prisma Next 的工作原理"*、*"我是 PN 新手，从哪里开始?"*）时，此技能会被触发，并将用户路由到正确的特定技能。

## 使用场景

- 用户尚未陈述具体任务。
- 用户输入关于 Prisma Next 的元问题（*"Prisma Next 是什么?"*、*"PN 与 Drizzle/Prisma 7 相比如何?"*）。
- 用户请求参观、概述或起点。

## 不适用场景

- 用户指定了工作流程 — 直接使用匹配的技能：
  - 设置新项目或采用现有数据库 → `prisma-next-quickstart`。
  - 编辑模式、添加模型、更改字段 → `prisma-next-contract`。
  - 编写迁移、修复规划器错误 → `prisma-next-migrations`。
  - 审查即将合并的内容、处理并发迁移 → `prisma-next-migration-review`。
  - 编写查询 → `prisma-next-queries`。
  - Supabase — RLS 策略、角色绑定（`asUser` / `asAnon` / `asServiceRole`）、`auth.users` 外键、`@prisma-next/extension-supabase` → `prisma-next-supabase`。
  - 连接 `db.ts`、中间件、环境配置 → `prisma-next-runtime`。
  - 构建系统 / 开发服务器插件（Vite、Next.js、…）→ `prisma-next-build`。
  - 特定错误代码或症状 → `prisma-next-debug`。
  - 向 Prisma Next 报告错误或提交功能请求 → `prisma-next-feedback`。

## 路由规则

如果用户的提示明确匹配某个工作流程技能，直接路由到该技能，无需询问。

否则，提出**一个**消除歧义的提问。从以下选项中选择：

- *"你是 Prisma Next 新手，询问可以用它做什么，或从哪里开始?"*（以及任何 *"我可以用 Prisma Next 做什么?"* / *"我刚运行 createprisma"* 变体）→ `prisma-next-quickstart`（首次接触导向路径）。
- *"你想设置一个新的 Prisma Next 项目，还是将其连接到现有数据库?"* → `prisma-next-quickstart`。
- *"你想编辑你的数据合约（添加模型 / 字段 / 关系），还是与数据库一起工作（迁移、查询）?"* → `prisma-next-contract` vs 其他选项。
- *"这是关于编写迁移，还是关于审查部署时将要运行的内容?"* → `prisma-next-migrations` vs `prisma-next-migration-review`。
- *"这是关于将 Prisma Next 连接到你的构建工具（Vite / Next.js / …），还是关于在运行时连接 `db.ts` 和中间件?"* → `prisma-next-build` vs `prisma-next-runtime`。
- *"你看到什么错误或症状?"* → `prisma-next-debug`。
- *"你想将此报告为 Prisma Next 团队的错误，还是这是一个功能请求?"* → `prisma-next-feedback`。

如果你仍然无法确定哪个技能适用，询问用户他们想做什么。不要猜测。

## 标准模型（一段话）

Prisma Next 是一个以合约优先的数据层。你编写一个**数据合约**（一个 `contract.prisma` 文件，或一个 TypeScript 构建器）。框架生成机器可读的工件（`contract.json`、`contract.d.ts`），并在 SQL 目标上提供三个运行时接口：一个类型化的 SQL 查询构建器（`db.sql.from(...)`）、一个类型化的 ORM 客户端（`db.orm.User.select(...)`）和一个原始 SQL 逃逸通道（`db.sql.raw(...)`）。在 MongoDB 目标上，只有 ORM 路径存在，其键是集合存储名称（`db.orm.users`）而不是 PSL 模型名称 — `prisma-next-queries` § *MongoDB ORM 地址* 涵盖了规则。迁移是从合约差异中规划的；你审查它们，可选择编辑 `migration.ts` 进行数据转换，然后应用。

用户执行的三个步骤：

1. **编辑你的数据合约。** (`prisma-next-contract`)
2. **系统为你规划迁移。** (`prisma-next-migrations`)
3. **如果你需要数据迁移，你编辑 `migration.ts` 并执行它。** (`prisma-next-migrations`)

其他所有内容 — 查询、运行时连接、构建集成、调试、反馈 — 都建立在这三个步骤之上。

## 检查清单

- [ ] 如果提示匹配特定工作流程技能，直接路由，无需询问。
- [ ] 如果提示模糊，提出一个消除歧义的提问。
- [ ] 不要尝试从此技能回答用户的问题 — 首先加载正确的特定技能。
- [ ] 如果用户描述了一个缺失的功能或他们希望修复的行为，路由到 `prisma-next-feedback`。
