---
name: prisma-next-quickstart
description: 将 Prisma Next 集成到新项目中、现有数据库中，或作为引导工具将你带入脚手架后的第一步。适用于“我可以用 Prisma Next 做什么”、“接下来我该如何使用 Prisma”、“我从哪里开始”、“我应该先做什么”、“刚刚运行了 createprisma”、“createprisma”、“npx createprisma”、“npx create-prisma”、“第一步”、“第一个查询”、“我有一个脚手架式的 Prisma Next 项目现在该怎么办”；适用于 `pnpm dlx prisma-next init` 绿地设置；以及适用于 `prisma-next contract infer` + `db sign` 针对现有数据库的操作。此外还涵盖了连接-写入-读取的首阶段导向、日常命令（`contract emit`、`db init`、`db update`、`migration plan`、`migrate`、`db schema`、`db verify`），以及路由到 `prisma-next-contract` / `prisma-next-queries` / `prisma-next-runtime` 以进行下一步操作。标志：`--target`、`--authoring`、`--schema-path`、`--probe-db`、`--output`。
---

# Prisma Next — 快速入门（采用）

> **编辑你的数据合约。Prisma 会处理其余部分。**

这项技能将用户从零（或接近零）引导至对 Prisma Next 执行第一个工作查询。三条路径——它们都汇聚到相同的第一阶段：**连接 → 写入 → 读取**。模式编辑是在第一阶段之后，而不是之前。

- **首次接触导向**——用户首次到达 Prisma Next 项目（由 `npx createprisma` 等脚手架工具放置，他们克隆了队友的存储库，或者他们自己运行了 `prisma-next init` 并想进行第一次操作），并询问 *"我可以用 Prisma Next 做什么？*"，*"我从哪里开始？*"，或 *"接下来该做什么？*"。目标是将他们锚定在合约上，连接到数据库，完成一次数据往返，并让后续命令自然浮现。
- **绿地**——新项目，新数据库。用户自己运行 `prisma-next init`。`init` 会用示例模型预填充一个起始合约，因此路径会立即与首次接触导向阶段汇合，一旦数据库初始化完成。
- **棕色地-DB**——现有数据库，还没有合约。使用 `contract infer` 从数据库中推断合约，使用 `db sign` 签署标记，然后针对其中一个现有表编写查询。

这项技能**不**涵盖从其他 ORM（Drizzle、Prisma 6/7、Sequelize、TypeORM、Kysely、Knex、原始驱动器）迁移。这些是单独可安装的技能。

## 何时使用

- 用户询问 *"我可以用 Prisma Next 做什么？*"，*"我接下来可以用 Prisma 做什么？*"，*"我从哪里开始？*"，*"我首先该做什么？*"——并且磁盘上已经存在一个 PN 项目。**首次接触导向**路径。
- 用户刚刚运行了 `createprisma`（或等效脚手架工具）并询问接下来该做什么。**首次接触导向**路径。
- 用户正在开始一个新项目并想使用 Prisma Next。**绿地**路径。
- 用户有一个现有数据库（没有 PN 合约）并想引入 PN。**棕色地-DB**路径。
- 用户输入了 *"prisma-next init"*，*"开始使用 PN"*，*"设置 PN"*，*"我该如何创建项目脚手架"*。**绿地**路径。
- 用户说 *"我有一个现有的 Postgres/Mongo，我该如何开始使用 PN？*"。**棕色地-DB**路径。

## 何时不用

- 用户已经有一个 PN 项目并想添加一个模型 → `prisma-next-contract`。
- 用户想从特定的 ORM 迁移 → 安装 `@prisma-next/migrate-from-<orm>-skill`（单独）。
- 用户想在已经有一个合约的项目中连接 `db.ts` → `prisma-next-runtime`。
- 用户想将 Prisma Next 与构建工具（Vite 插件、Next.js、…）集成 → `prisma-next-build`。

## 关键概念

- **合约**：数据模型。作为 `contract.prisma`（PSL，规范表面）或 `contract.ts`（TypeScript 构建器）编写。框架读取它并生成两个产物：`contract.json`（运行时 IR）和 `contract.d.ts`（类型）。
- **目标**：后端存储。目前：`postgres` 或 `mongodb`。在 `init` 时选择；烘焙到 `@prisma-next/<target>` 界面中，脚手架从该界面导入。
- **编写模式**：你如何编写合约。`psl`（Prisma 模式语言，默认）或 `typescript`（程序化构建器，可选与 Vite 插件配对以在 `vite dev` 期间自动发出——见 `prisma-next-build`）。
- **界面包**。脚手架为每个目标安装一个界面包——`@prisma-next/postgres`（或 `@prisma-next/mongo`）。用户代码从界面子路径导入（`@prisma-next/postgres/config`，`@prisma-next/postgres/runtime`，`@prisma-next/postgres/contract-builder`）。界面包烘焙了家族/目标/适配器/驱动器连接；不要越过它。见 `prisma-next-contract` 获取完整列表。
- **`db.ts`**：运行时入口点。位于合约源旁边的 `src/prisma/db.ts`。导入合约产物并导出一个 `db` 值，应用程序其余部分使用该值。
- **标记**：数据库中记录合约哈希的 `pn_meta_marker` 行。让 PN 检测合约与实时数据库之间的差异。由 `db init`（绿地/首次接触导向）或 `db sign`（棕色地）创建。

### 规范磁盘布局

每个使用 Prisma Next 的应用程序都使用相同的结构：

```text
<app-root>/
├── prisma-next.config.ts             ← 存储库根目录的项目配置
├── src/
│   └── prisma/
│       ├── contract.prisma           ← (或 contract.ts) — 你编写的模式源
│       ├── contract.json             ← 由 `contract emit` 发出 — 不要编辑
│       ├── contract.d.ts             ← 由 `contract emit` 发出 — 不要编辑
│       └── db.ts                     ← 运行时入口；`src/` 的其余部分从此导入
└── migrations/
    ├── snapshots/                    ← 内容寻址的合约存储，跨空间共享
    │   └── <hex>/
    │       ├── contract.json
    │       └── contract.d.ts
    └── app/                          ← 在第一次 `migration plan` / `db init` 时创建
        ├── refs/head.json
        └── <timestamp>_<slug>/
            ├── migration.json
            ├── ops.json
            └── migration.ts
```

需要掌握的三件事：

- **`src/prisma/` 是合约的家**——源 + 发出的产物 + `db.ts` 都位于同一位置。`src/` 的其余部分从 `./prisma/db`（或 `../prisma/db`，取决于文件深度）导入。
- **`migrations/app/`**——`app/` 段是消费应用程序的空间 ID。你依赖的扩展会在 `migrations/` 下获得兄弟目录（每个扩展合约空间一个），但你不会写入这些——只有 `app/` 子树是你的迁移。
- **`prisma-next.config.ts` 位于存储库根目录**，而不是在 `src/` 下。每个命令相对于配置的目录解析路径。

**构建扩展包或聚合根单体包的贡献者使用不同的布局**——`src/contract.{prisma,ts}`（没有 `prisma/` 子目录）+ `migrations/<timestamp>_<slug>/`（没有 `app/` 段）。这种区别是故意的；见 `prisma-next-contract` 确定哪个路径适用于你。

> **注意**——`prisma-next init` 目前会创建错误的布局。它会在存储库根目录写入 `prisma/contract.{prisma,ts}` 和 `prisma/db.ts`，而不是在 `src/prisma/` 下。作为 [TML-2532](https://linear.app/prisma-company/issue/TML-2532) 追踪。直到修复落地，要么将 `--schema-path src/prisma/contract.prisma` 传递给 `init`，要么在 `init` 后将脚手架的 `prisma/` 目录移动到 `src/prisma/` 并更新 `prisma-next.config.ts` 中的 `contract` 路径以匹配。上面的规范布局是演示示例使用的，也是框架期望的。

## 你的第一个阶段——连接、写入、读取

这项技能中的三条路径都会汇聚到这里。一旦项目脚手架完成且数据库可访问，第一个操作**总是**相同的：连接、写入一行、读取它，针对合约已经声明的任何模型。在这个第一个操作中不要修改合约源——稍后扩展它，一旦往返操作正常工作。

在 `src/` 下直接创建一个新文件（例如 `src/first-arc.ts`），以便相对导入解析到一级深度：

```typescript
// src/first-arc.ts
import 'dotenv/config';
import { db } from './prisma/db';

// 针对起始模型写入一行。将字段名调整为合约源实际声明的模型——先读取它。
await db.orm.User.create({ email: 'alice@example.com' });

// 读取它。
const users = await db.orm.User.select('id', 'email').all();
console.log(users);
```

如果它打印 `[{ id: 1, email: 'alice@example.com' }]`，则项目端到端连接完成，用户已经从 *"我有一个项目"* 过渡到 *"我在构建。"*。

`db.orm.<Model>` 是默认的 ORM 路径——模型形状的，完全针对合约进行类型化，在第一次使用时惰性连接到数据库（它通过运行时的 `dotenv/config` 加载的环境从 `.env` 中选择 `DATABASE_URL`）。更深层的 `prisma-next-queries` 技能涵盖了用户准备好时的其余表面（过滤器、连接、事务、SQL 构建器、原始 SQL、TypedSQL）。

> **Mongo 目标**：上面的代码是 SQL 目标形状。在 `@prisma-next/mongo` 上，`db.orm` 是按集合的存储名称键入的（`@@map(...)`，如果没有 `@@map`，则按小写的模型名称），所以相同的弧读取 `await db.orm.users.create(...)` / `await db.orm.users.select('id', 'email').all()`——不是 `db.orm.User`。完整规则和重写配方在 `prisma-next-queries` § *MongoDB ORM 地址* 中。

**弧操作的先决条件**。三条路径在到达弧时都会保留这些：

- `prisma-next.config.ts` 位于存储库根目录并声明目标 + 合约源（通常 `src/prisma/contract.prisma` 或 `src/prisma/contract.ts`；一个早于 [TML-2532](https://linear.app/prisma-company/issue/TML-2532) 的项目可能将其位于 `prisma/contract.{prisma,ts}` 而不是——检查配置的 `contract` 字段）——存在哪些起始模型。
- 合约源位于 `src/prisma/contract.{prisma,ts}`（来自 `init` 的起始模型，或从 `contract infer` 推断的合约，或 whatever the bootstrap tool generated）。
- `src/prisma/db.ts` 存在并使用发出的合约实例化运行时。
- `DATABASE_URL` 在 `.env` 中设置（或运行时的配置告诉它在哪里查找）。
- 数据库已初始化（`db init`）或标记签署（`db sign`），因此标记行存在且模式与合约匹配。

下面的三个工作流分别描述了它们的路径如何让用户到达该状态。之后，上面的弧是相同的。

## 工作流——首次接触导向

触发：*"我可以用 Prisma Next 做什么？*"，*"我接下来可以用 Prisma 做什么？*"，*"我从哪里开始？*"，*"我刚运行了 createprisma"*，*"接下来该做什么？*"，或任何接近变体——搭配磁盘上已经存在的 PN 项目（由 `createprisma`、`prisma-next init`、队友或 whatever 创建）。

用户的宏观意图是 *"我想运行一个针对我的数据库的应用程序，针对这个名为 Prisma Next 的东西。"* 这个工作流的任务是让他们锚定在合约上，让一次往返操作正常工作，并让后续命令在他们的下一步操作需要时自然浮现。**它是导向，不是导游，不是功能清单，不是课程大纲。**

### 概念——首先传达什么

Prisma Next 是合约优先。框架执行的每项操作——查询类型、迁移、运行时类型、差异检测——都源自单一事实来源：**合约**。合约描述了用户应用程序的数据模型。框架读取它；框架推导出其余部分。先从这里开始。

对 *"我可以用 Prisma Next 做什么？*" 的第一个响应命名合约路径，用一句话框定其作用，然后引导用户让应用程序运行。不要以功能清单开头。不要以命令列表开头。以：*"你的合约位于 `<路径>`，它描述了你的应用程序——你的查询类型、迁移和运行时类型都源自它。让我们帮你连接到数据库，这样你的应用程序就可以实际运行它。"* 开头。

第一个**阶段**——一旦导向——是 **连接 → 写入 → 读取**。不是先编辑合约，不是先计划迁移。用户的胜利是 *"我的应用程序正在运行在我的数据库上。"*。

### 第 1 步——读取项目，命名合约

在说任何特定于用户的特定内容之前，读取：

- 存储库根目录的 `prisma-next.config.ts`——连接了什么目标（`postgres` / `mongodb`），它声明的 `contract:` 路径是什么，安装了哪些扩展。
- 配置声明的合约源（规范上 `src/prisma/contract.prisma` 或 `src/prisma/contract.ts`；早于 [TML-2532](https://linear.app/prisma-company/issue/TML-2532) 的项目可能将其位于 `prisma/contract.{prisma,ts}` 而不是——检查配置的 `contract` 字段）——存在哪些起始模型。
- `src/prisma/db.ts`（位于合约旁边）——运行时入口点。
- `.env` / `.env.example`——`DATABASE_URL` 设置了吗，还是只有示例？
- 可选地 `pnpm prisma-next db verify`——实时数据库是否与合约匹配？

然后**向用户说出合约路径，并附加其作用**。类似：*"你的合约位于 `src/prisma/contract.prisma`，它目前声明了一个 `User` 模型。合约描述了你的应用程序——框架给你提供的每个查询类型、迁移和运行时类型都源自这个文件。让我们让你的应用程序连接到数据库。"* 具体措辞由代理决定；重要的是用户在第一个响应中知道 *"合约在哪里"* 以及 *"它是事实来源"*。

### 第 2 步——让用户的应用程序连接并完成往返

动机是 *"这样你的应用程序才能实际运行在你的数据库上"*，而不是 *"这样先决条件清单才能通过"*。机制取决于第 1 步中已经准备好的内容：

- **一切都已连接**。直接编写并读取一行（见上文 *你的第一个阶段——连接、写入、读取*）。将代码段调整为合约声明的模型。
- **`DATABASE_URL` 未设置**。让用户在 `.env` 中设置它（不要在 `prisma-next.config.ts` 中——见陷阱 5）。然后 `pnpm prisma-next db init` 将当前合约应用于该数据库并写入标记行。现在应用程序可以连接。
- **数据库可连接但尚未意识到合约**（缺少标记行；`db verify` 报告差异）。运行 `pnpm prisma-next db init`。(`db update` 是快速开发周期时的替代方案——它更宽松，不会写入迁移历史，并且是用户在快速迭代模式时想要使用的。如果用户询问如何让模式更改流向数据库，则提及它；不要预先解释它。)
- **合约为空**（启动工具留下了空白源）。添加**一个**模型，具有**两个**字段（例如 `User { id, email }`），`pnpm prisma-next contract emit`，然后 `pnpm prisma-next db init`。最小化——让往返操作正常工作，*然后*扩展。

用户在这里遇到 `db init`（以及可选的 `db update`，`contract emit`），因为这是他们当前操作*需要的*命令。他们通过使用这些命令来学习这些命令。

### 第 3 步——完成一行往返

运行上文 *你的第一个阶段——连接、写入、读取* 中的代码段，针对合约声明的模型。当它打印行时，用户已经从 *"我有一个项目"* 过渡到 *"我的应用程序正在运行在我的数据库上。"*。这就是胜利。

### 第 4 步——转交给下一步操作

现在询问用户他们想构建什么。路由到拥有该操作的技能：

- 更多查询（过滤器、连接、事务、原始 SQL、TypedSQL）→ `prisma-next-queries`。
- 添加模型，更改字段，添加关系 → `prisma-next-contract`。他们会在该工作流中触摸 `contract emit` 和 `db update`（或 `migration plan` + `migrate`）。
- 中间件、环境配置、多个目标 → `prisma-next-runtime`。
- Vite / Next.js / dev-server 集成 → `prisma-next-build`。
- 他们想在这个阶段获得更全面的工具包概述——*日常使用的命令* 下面是一个一目了然的摘要。

### 此路径上的反模式

- **以功能巡游或能力清单开头**。用户询问他们可以*做什么*。让他们开始做。
- **在未使用任何命令之前列出命令**。命令属于特定的操作；在操作需要时才显示它们。
- **在运行第一个查询之前深入迁移概念**。迁移存在；它们的值稍后会到来。
- **一次添加多个模型**。添加一个，让一个查询变绿，然后迭代。
- **引导用户通过 `prisma-next.config.ts` 键**。脚手架的默认值是正确的；在用户需要更改某事时再回顾。
- **跳过合约框架**。即使是一行——*"你的合约位于 `<路径>`，它是事实来源"*——也能让用户锚定；没有它，其余的工作流会像脱节仪式一样落地。

## 工作流——绿地

概念：`prisma-next init` 是一个 CLI 命令，它脚手架配置、模式、运行时、依赖项和合约发出步骤。它作用于当前工作目录——没有位置项目名参数。创建目录，`cd` 进去，然后运行 init。

```bash
mkdir my-app && cd my-app
pnpm init                                          # 如果还没有 package.json
pnpm dlx prisma-next init                          # 交互式
# 或者非交互式（CI / 代理运行）：
pnpm dlx prisma-next init --yes --target postgres --authoring psl
```

> **遥测数据是可选的。** CLI 默认收集匿名使用数据。每个命令——包括 `init`——在首次使用时会在 **stderr** 上打印一次性通知，然后发送；没有交互式同意提示。随时可以通过运行 `prisma-next telemetry disable`、设置 `DO_NOT_TRACK=1` 或 `PRISMA_NEXT_DISABLE_TELEMETRY=1`，或在用户配置（`prisma-next` 配置目录，**不是** `prisma-next.config.ts`）中设置 `"enableTelemetry": false` 来选择退出。运行 `prisma-next telemetry status` 查看当前生效的设置。这对于代理驱动运行——CLI 记录代理调用了它——是相关的。收集的内容、每个用户的配置路径以及如何完全重置在 `docs/Telemetry.md` 中有说明。

`init` 接受的标志（运行 `prisma-next init --help` 获取权威来源）：

- `--target <db>` — `postgres` 或 `mongodb`。
- `--authoring <style>` — `psl` 或 `typescript`。
- `--schema-path <path>` — 默认为 `prisma/contract.prisma`（或 `prisma/contract.ts`）。**将 `--schema-path src/prisma/contract.prisma`（或 `.../contract.ts`）** 直接生成到标准的 `src/prisma/` 位置——`init` 的默认值今天不正确，参见 [TML-2532](https://linear.app/prisma-company/issue/TML-2532)。
- `--force` — 覆盖现有的脚手架而不提示（在已脚手架的目录中重新运行 `init` 触发重新初始化流程——`--force` 跳过确认）。
- `--write-env` — 同时写入 `.env`（默认只写入 `.env.example`；`.env` 仍然由你控制）。
- `--probe-db` — 连接到 `DATABASE_URL` 一次并检查服务器版本是否满足目标的最小版本。
- `--strict-probe` — 如果探测失败则失败初始化（没有 `--probe-db` 则无操作）。
- `--no-install` — 跳过依赖安装 + 初始合约发出。
- `--no-skill` — 跳过 Prisma Next 技能安装（隔离的 / 受限的环境）。技能集群始终在项目级别安装——永远不会全局安装——因此其版本始终锁定到项目的 Prisma Next 版本。

`init` 在正常运行时写入：

- 项目根目录下的 `prisma-next.config.ts`。
- 合约源文件在 `--schema-path`——如果你传递了标准覆盖，则为 `src/prisma/contract.prisma`，如果你接受了（目前错误的）默认值，则为 `prisma/contract.prisma`。
- 与合约源文件相同的目录下的 `db.ts`。
- 人类快速参考 `prisma-next.md`。
- `.env.example`（如果 `--write-env` 则写入 `.env`）。
- 更新 `package.json`（依赖项 + 脚本）和 `tsconfig.json`（必需的编译器选项）。
- 安装依赖项并运行 `prisma-next contract emit` 一次。
- 向本地代理运行时注册 Prisma Next 技能。

**如果你选择了 `init` 的默认值，最终得到了一个顶层 `prisma/` 目录**（TML-2532），清理操作是一次移动 + 一次配置编辑：

```bash
mkdir -p src && mv prisma src/prisma
# 然后更新 `prisma-next.config.ts`，使 `contract` 读取
# 'src/prisma/contract.prisma'（或 .ts）而不是 'prisma/contract.prisma'。
pnpm prisma-next contract emit   # 重新发出 contract.json + contract.d.ts 在 src/prisma/ 下
```

在运行 `db init` 之前执行此操作——一旦写入标记行，重构会更困难。

初始化成功后，路径将汇聚到上面提到的“你的第一个弧——连接、写入、读取”。`init` 已经用 `User` 和 `Post` 模型（它们之间有关联）生成了一个起始合约并运行了一次 `contract emit`；剩下的唯一前提条件是设置 `DATABASE_URL` 并初始化数据库。两个命令：

1. 在 `.env` 中设置 `DATABASE_URL`（从 `.env.example` 复制）。
2. 初始化数据库：`pnpm prisma-next db init`。创建表、索引、约束并写入标记行——使用 `init` 生成的起始合约。

然后运行上面“你的第一个弧”中的代码片段，使用 `User` 模型。当用户准备好扩展合约——添加更多模型、更改字段、添加关联时——链到 `prisma-next-contract`。对于更多查询，链到 `prisma-next-queries`。

**为什么这是查询优先而不是合约编辑优先。** `init` 有意包含 `User` 和 `Post`：用户不应该设计一个模式来证明他们的设置可以工作。扩展合约是在第一个弧落地后的下一步，而不是到达那里的一部分。如果用户要求你直接跳到“添加一个 Comment 模型”——当然可以这么做——但如果有任何疑问项目配置是否正确，先让 `User` 或 `Post` 的一个查询变绿。

## 工作流——老数据库（现有数据库，没有合约）

概念：针对一个没有 PN 合约的现有数据库，`contract infer` 遍历实时模式（表、列、索引、约束）并写入一个描述它的 PSL 合约。结果是起点，不是最终合约——审查并清理它，然后 `db sign` 记录当前合约哈希作为标记（而不是让 `db init` 尝试从头开始重建模式）。

```bash
mkdir my-app && cd my-app
pnpm init
pnpm dlx prisma-next init --yes --target postgres --authoring psl
# 脚手架生成；你会覆盖下面要生成的起始模式
```

然后，在 `.env` 中设置 `DATABASE_URL`：

```bash
pnpm prisma-next contract infer --db "$DATABASE_URL" --output src/prisma/contract.prisma
```

（注意：标志是 `--output`，不是 `--out`。运行 `prisma-next contract infer --help` 获取完整表面。）

代理应该在这里暂停并读取推断的 PSL。需要重新作者遍历的症状：

- PN 无法分类的表（例如，你可以表示为关系的遗留链接表）。
- PN 类型猜测错误的列（例如，`String` 而你想使用扩展类型如 `pgvector.Vector(length: 1536)`）。
- PN 无法看到的缺失 `@unique` / `@index` 提示。
- 你更喜欢别名字段名。

然后重新发出并签名：

```bash
pnpm prisma-next contract emit
pnpm prisma-next db sign
pnpm prisma-next db verify   # 确认数据库与合约匹配；如果不匹配则报告漂移
```

然后运行上面“你的第一个弧——连接、写入、读取”中的代码片段，使用你现有的表代替起始模型。路径相同；只有到达那里的路径不同。

## 你日常会使用的命令

一个参考表——不是用户需要背诵的脚本。命令在上述工作流中根据用户下一步需要它们而出现；此表在此处是为了用户在第一次往返后请求更广泛的视图（通常如此），以及作为任何新接触 Prisma Next 的人可以扫描的快速概览。对于标志级细节，运行 `<command> --help`；帮助输出是权威来源。

| 你想做什么 | 命令 | 更深入的技能 |
|---|---|---|
| 首次将当前合约应用到数据库 | `prisma-next db init` | 此技能 |
| 编辑合约源后重新发出 `contract.json` + `contract.d.ts` | `prisma-next contract emit` | `prisma-next-contract` |
| 快速开发模式下的模式同步（不保留迁移历史） | `prisma-next db update` | `prisma-next-migrations` |
| 从合约差异规划迁移 | `prisma-next migration plan --name <slug>` | `prisma-next-migrations` |
| 应用待处理的迁移 | `prisma-next migrate` | `prisma-next-migrations` |
| 检查实时数据库 | `prisma-next db schema` | `prisma-next-debug` |
| 确认数据库与合约匹配（漂移检查） | `prisma-next db verify` | `prisma-next-debug` |
| 将现有数据库纳入 PN 合约 | `prisma-next contract infer --db "$DATABASE_URL"` | 此技能（老数据库） |
| 解码结构化错误信封 | （读取 `code` / `why` / `fix` 字段） | `prisma-next-debug` |
| 报告错误或请求功能 | （通过反馈技能提交） | `prisma-next-feedback` |

## 决策——PSL vs TypeScript 作者模式

- **PSL** (`contract.prisma`) — 默认。简洁、声明式、任何使用过 Prisma 的人都熟悉。推荐大多数项目使用。
- **TypeScript** (`contract.ts`) — 命令式构建器。当合约确实需要计算（多租户按租户变体）、在文件间重用合约片段，或需要 PSL 尚未表达的扩展结构（例如 pgvector 的参数化存储类型注册）时使用。与 `prisma-next-build` 的 Vite 插件配对，实现保存时自动发出。

在同一个目录中重新运行 `prisma-next init` 来切换作者模式。初始化流程检测到现有脚手架并提示重新初始化（在非交互式运行中使用 `--force` 跳过提示）。现有合约内容不会自动自动翻译——你需要手动在目标语言中重新作者。

## 常见陷阱

1. **使用 `prisma-next init <project-name>` 并带位置参数运行。** `init` 在当前工作目录上操作；没有位置项目名参数。`mkdir foo && cd foo && pnpm dlx prisma-next init`。
2. **`init` 没有连接到你的数据库。** 它只生成文件和安装依赖项（并运行初始 `contract emit`）。你通过 `db init` / `db update` / `migrate` 连接。如果 `init` 成功但查询失败，问题在于 `DATABASE_URL`，而不是 `init`。
3. **将推断的 PSL 视为最终合约。** `contract infer` 生成起点。不要对未阅读的合约进行 `db sign`。
4. **编辑合约后忘记发出。** 合约工件（`contract.json`、`contract.d.ts`）在运行 `contract emit` 之前是过时的。如果类型检查器说模型“不存在”，你错过了发出。
5. **在 `prisma-next.config.ts` 中设置 `DATABASE_URL` 而不是 `.env`。** 配置自动通过 `dotenv/config` 读取 `.env`。硬编码 URL 泄露凭证并绕过每个环境的覆盖。参见 `prisma-next-runtime`。
6. **手动编辑 `contract.json` 或 `contract.d.ts`。** 它们是发出工件；下一个 `contract emit` 会覆盖你的更改。编辑源代码而不是它们。
7. **使用 `--out` 对于 `contract infer`。** 标志是 `--output`。

## Prisma Next 尚未实现的功能

- **从其他 ORM 迁移。** Prisma Next 不会从 Drizzle / Prisma 6/7 / Sequelize / TypeORM / Kysely / Knex / 原生驱动器迁移你的模式。解决方法：如果存在匹配的 `@prisma-next/migrate-from-<orm>-skill`，安装它，或者将源视为老数据库并从它 `contract infer`。如果你需要一个内置的引导迁移流程，通过 `prisma-next-feedback` 技能提交功能请求。
- **`prisma db push` 风格的生产同步。** `db update` 是快速开发路径；对于生产，使用迁移（`migration plan` + `migrate`）。PN 故意不提供“无需迁移直接推送到生产”的表面——参见 `prisma-next-migrations`。
- **Studio / GUI 数据库浏览器。** 使用 `prisma-next db schema` 获取实时数据库的 CLI 树形摘要。如果你需要一个交互式 UI，通过 `prisma-next-feedback` 技能提交功能请求。

## 参考文件

此技能有意只包含正文；`prisma-next init --help`、`contract infer --help` 和 `db sign --help` 是标志级细节的权威表面。如有疑问，运行 `--help` 并阅读实际命令的描述，而不是猜测此技能。

## 检查清单

- [ ] 确认了哪种路径适用（首次接触导向 / 绿地 / 老数据库）在提出命令之前。
- [ ] **首次接触导向：** 将合约路径回退给用户并阐述其作用（查询类型、迁移和运行时类型流出的来源）在提出任何命令之前。
- [ ] **所有路径：** 在编写应用程序代码之前，将项目带到 *你的第一个弧* 前提条件（配置、合约源、`db.ts`、`DATABASE_URL`、标记行）。
- [ ] **所有路径：** 运行了第一个弧——对起始（或推断的）模型一个 `create` + 一个 `select`——并使往返工作变绿。
- [ ] **所有路径：** 在第一个弧中未编辑合约源。模式扩展是 *下一步*，不是第一步。
- [ ] **所有路径：** 未以功能巡游、功能清单或 CLI 命令的背诵开头。命令在用户当前需要它们时出现。
- [ ] 确认了用户的靶标（`postgres` / `mongodb`）和作者模式（`psl` / `typescript`）。
- [ ] **首次接触导向：** 在提出任何内容之前，阅读了 `prisma-next.config.ts`、合约源、`db.ts` 和 `.env`——没有假设脚手架工具或队友留下了什么。
- [ ] **绿地路径：** 从项目目录运行 `prisma-next init`——没有位置项目名参数。
- [ ] **所有路径：** 项目最终进入了标准的 `src/prisma/contract.{prisma,ts}` + `src/prisma/db.ts` + `migrations/app/` 布局——包括如果 `init` 生成一个顶层 `prisma/`，则将脚手架目录移出（TML-2532）。
- [ ] **老数据库路径：** 运行 `contract infer --db "$DATABASE_URL" --output src/prisma/contract.prisma`，审查结果，然后 `contract emit` + `db sign`。
- [ ] 在 `.env` 中设置 `DATABASE_URL` 并确认值是可访问的。
- [ ] 初始化数据库（绿地 / 首次接触导向的 `db init` / 老数据库的 `db sign`）。
- [ ] 未手动编辑 `contract.json` 或 `contract.d.ts`。
- [ ] 未在 `prisma-next.config.ts` 中设置 `DATABASE_URL`。
- [ ] 确认用户理解他们工作流程中的 *下一步* 技能是什么（通常 `prisma-next-queries` 用于更多查询，然后在准备好扩展模式时 `prisma-next-contract`）。
