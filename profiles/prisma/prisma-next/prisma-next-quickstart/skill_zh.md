# Prisma Next — 快速入门（采用）

> **编辑你的数据合约。Prisma 处理其余部分。**

这项技能将用户从零（或接近零）引导至对 Prisma Next 执行第一个工作查询。三条路径——它们都汇聚到相同的第一阶段：**连接 → 写入 → 读取**。模式编辑是在第一阶段之后，而不是之前。

- **首次接触导向**——用户首次到达 Prisma Next 项目（由 `npx createprisma` 等脚手架工具放置，他们克隆了队友的存储库，或者他们自己运行了 `prisma-next init` 并想进行第一次操作），并询问 *"我可以用 Prisma Next 做什么？*"，*"我从哪里开始？*"，或 *"接下来做什么？*"。目标是将他们锚定在合约上，连接到数据库，完成一次往返操作，并让后续命令自然浮现。
- **绿地**——新项目，新数据库。用户自己运行 `prisma-next init`。`init` 会用示例模型预填充一个起始合约，因此路径会立即加入首次接触导向阶段，一旦数据库初始化完成。
- **棕地-DB**——现有数据库，还没有合约。使用 `contract infer` 从数据库中推断合约，使用 `db sign` 签署标记，然后在其中一个现有表上编写查询。

这项技能**不**涵盖从另一个 ORM（Drizzle、Prisma 6/7、Sequelize、TypeORM、Kysely、Knex、原始驱动程序）迁移。这些是单独安装的技能。

## 何时使用

- 用户询问 *"我可以用 Prisma Next 做什么？*"，*"我接下来可以用 Prisma 做什么？*"，*"我从哪里开始？*"，*"我应该首先做什么？*"——并且磁盘上已经存在一个 PN 项目。**首次接触导向**路径。
- 用户刚刚运行了 `createprisma`（或等效脚手架工具）并询问接下来做什么。**首次接触导向**路径。
- 用户正在开始一个新项目并想使用 Prisma Next。**绿地**路径。
- 用户有一个现有数据库（没有 PN 合约）并想引入 PN。**棕地-DB**路径。
- 用户输入了 *"prisma-next init"*，*"开始使用 PN"*，*"设置 PN"*，*"我该如何构建项目脚手架"*。**绿地**路径。
- 用户说 *"我有一个现有的 Postgres/Mongo，我该如何开始使用 PN？*"。**棕地-DB**路径。

## 何时不用

- 用户已经有一个 PN 项目并想添加一个模型 → `prisma-next-contract`。
- 用户想从特定的 ORM 迁移 → 安装 `@prisma-next/migrate-from-<orm>-skill`（单独）。
- 用户想在已经有一个合约的项目中连接 `db.ts` → `prisma-next-runtime`。
- 用户想将 Prisma Next 与构建工具（Vite 插件、Next.js 等）集成 → `prisma-next-build`。

## 关键概念

- **合约**：数据模型。作为 `contract.prisma`（PSL，规范表面）或 `contract.ts`（TypeScript 构建器）编写。框架读取它，并发出两个工件：`contract.json`（运行时 IR）和 `contract.d.ts`（类型）。
- **目标**：后端存储。目前：`postgres` 或 `mongodb`。在 `init` 时选择；烘焙到 `@prisma-next/<target>` 面板中，该面板由脚手架导入。
- **编写模式**：你如何编写合约。`psl`（Prisma 模式语言，默认）或 `typescript`（程序化构建器，可选与 Vite 插件配对以在 `vite dev` 期间自动发出——见 `prisma-next-build`）。
- **面包装饰包**。脚手架为每个目标安装一个面包装饰包——`@prisma-next/postgres`（或 `@prisma-next/mongo`）。用户代码从面包装饰子路径导入（`@prisma-next/postgres/config`，`@prisma-next/postgres/runtime`，`@prisma-next/postgres/contract-builder`）。面包装饰包烘焙了家庭/目标/适配器/驱动程序的连接；永远不要越过它。见 `prisma-next-contract` 以获取完整列表。
- **`db.ts`**：运行时入口点。位于合约源旁边，`src/prisma/db.ts`。导入合约工件并导出一个 `db` 值供应用程序其余部分使用。
- **标记**：数据库中的一个 `pn_meta_marker` 行，记录合约哈希。让 PN 检测合约与实时数据库之间的差异。由 `db init`（绿地/首次接触导向）或 `db sign`（棕地）创建。

### 规范磁盘布局

每个消耗 Prisma Next 的应用程序都使用相同的形状：

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

记住三件事：

- **`src/prisma/` 是合约的家**——源 + 发出的工件 + `db.ts` 都位于同一位置。`src/` 的其余部分从 `./prisma/db`（或 `../prisma/db`，取决于文件深度）导入。
- **`migrations/app/`** — `app/` 段是消费应用程序的空间 ID。你依赖的扩展会在 `migrations/` 下获得兄弟目录（每个扩展合约空间一个），但你不会写入这些目录——只有 `app/` 子树是你的迁移。
- **`prisma-next.config.ts`** 位于存储库根目录，而不是 `src/` 下。每个命令都相对于配置的目录解析路径。

**构建扩展包或聚合根单体包的贡献者使用不同的布局**——`src/contract.{prisma,ts}`（没有 `prisma/` 子目录）+ `migrations/<timestamp>_<slug>/`（没有 `app/` 段）。这种区别是故意的；见 `prisma-next-contract` 以了解哪个路径适用于你。

> **注意**——`prisma-next init` 目前构建了错误的布局。它将 `prisma/contract.{prisma,ts}` 和 `prisma/db.ts` 写在存储库根目录，而不是在 `src/prisma/` 下。作为 [TML-2532](https://linear.app/prisma-company/issue/TML-2532) 追踪。在修复落地之前，要么将 `--schema-path src/prisma/contract.prisma` 传递给 `init`，要么在 `init` 后将脚手架的 `prisma/` 目录移动到 `src/prisma/` 下，并更新 `prisma-next.config.ts` 中的 `contract` 路径以匹配。上面的规范布局是演示示例使用的，也是框架期望的。

## 你的第一个阶段——连接，写入，读取

这三种路径都汇聚于此。一旦项目脚手架完成且数据库可访问，第一个操作始终相同：连接，写入一行，读取它，针对合约已经声明的任何模型。在此第一个操作中不要触摸合约源——稍后扩展它，在往返操作工作后再进行。

在 `src/` 下一个新文件中编写片段（例如 `src/first-arc.ts`），以便相对导入解析到一级深度：

```typescript
// src/first-arc.ts
import 'dotenv/config';
import { db } from './prisma/db';

// 对起始模型写入一行。根据你的合约源实际声明的字段名进行调整。
await db.orm.User.create({ email: 'alice@example.com' });

// 读取它。
const users = await db.orm.User.select('id', 'email').all();
console.log(users);
```

如果它打印 `[{ id: 1, email: 'alice@example.com' }]`，则项目端到端连接，用户已经从 *"我有一个项目"* 过渡到 *"我在构建。*"

`db.orm.<Model>` 是默认 ORM 轨道——模型形状，完全针对合约进行类型检查，在第一次使用时懒惰地连接到数据库（它通过运行时的 `dotenv/config` 加载的环境从 `.env` 中获取 `DATABASE_URL`）。更深层的 `prisma-next-queries` 技能涵盖了用户准备好时其余的表面（过滤器，连接，事务，SQL 构建器，原始 SQL，TypedSQL）。

> **Mongo 目标**：上面的片段是 SQL 目标形状。在 `@prisma-next/mongo` 上，`db.orm` 是按集合的存储名称键入的（`@@map(...)`，或者如果没有 `@@map`，则按小写的模型名称），所以相同的弧读取 `await db.orm.users.create(...)` / `await db.orm.users.select('id', 'email').all()`——不是 `db.orm.User`。完整规则和重写配方在 `prisma-next-queries` § *MongoDB ORM 地址* 中。

**弧的先决条件**。这三种路径在您到达弧时都保留这些内容：

- `prisma-next.config.ts` 存在于存储库根目录，并声明了目标（`postgres` / `mongodb`）+ 合约源（规范地 `src/prisma/contract.prisma` 或 `src/prisma/contract.ts`；在 [TML-2532](https://linear.app/prisma-company/issue/TML-2532) 之前的存储库可能将合约位于 `prisma/contract.{prisma,ts}` 而不是 `src/prisma/contract.prisma`——检查配置的 `contract` 字段）——是否存在起始模型。
- 合约源存在于 `src/prisma/contract.{prisma,ts}`（来自 `init` 的起始模型，或从 `contract infer` 推断的合约，或 whatever the bootstrap tool generated）。
- `src/prisma/db.ts` 存在并使用发出的合约实例化运行时。
- `DATABASE_URL` 在 `.env` 中设置（或运行时的配置告诉它在哪里查找）。
- 数据库已初始化（`db init`）或标记签署（`db sign`），因此标记行存在，模式与合约匹配。

下面三种工作流中的每一种都描述了它们的路径如何让用户到达该状态。之后，上面的弧是相同的。

## 工作流——首次接触导向

触发：*"我可以用 Prisma Next 做什么？*"，*"我接下来可以用 Prisma 做什么？*"，*"我从哪里开始？*"，*"我刚运行了 createprisma"*，*"接下来做什么？*"，或任何接近变体——与磁盘上已经存在 PN 项目的配合（由 `createprisma` 脚手架，`prisma-next init`，队友，无论如何）。

用户的意图是 *"我想运行一个针对我的数据库的应用程序，针对这个名为 Prisma Next 的东西。*“ 这项工作流的任务是让他们锚定在合约上，连接到数据库，完成一次往返操作，并让后续命令自然浮现，因为他们的下一步操作需要它们。**它是导向，不是导游，不是功能清单，不是课程表。**

### 概念——首先传达什么

Prisma Next 是合约优先。框架执行的每项操作——查询类型，迁移，运行时类型，漂移检测——都源自单一事实来源：**合约**。合约描述了用户应用程序的数据模型。框架读取它；框架推导出其余部分。首先强调这一点。

对 *"我可以用 Prisma Next 做什么？*" 的第一个响应命名合约路径，用一句话框定其作用，然后引导用户运行他们的应用程序。不要以功能清单开头。不要以命令列表开头。以：*"你的合约位于 `<路径>`，它是事实来源"*——然后引导用户连接到数据库，以便他们的应用程序实际上可以运行。如果用户询问你跳转到 *"添加一个 Comment 模型"*——当然，做这个——但如果有任何疑问项目是否正确连接，首先针对 `User` 或 `Post` 运行一个查询变为绿色。

**为什么这是查询优先，而不是模式编辑优先。** `init` 故意提供了 `User` 和 `Post`：用户不应该设计模式来证明他们的设置工作正常。扩展合约是第一个弧落地后的下一步，不是到达那里的一部分。如果用户要求你跳转到 *"添加一个 Comment 模型"*——当然，做这个——但如果任何疑问项目是否正确连接，首先针对 `User` 或 `Post` 运行一个查询变为绿色。

## 工作流——绿地

概念：`prisma-next init` 是一个 CLI 命令，它脚手架配置，模式，运行时，依赖项和合约发出步骤。它作用于当前工作目录——没有位置项目名参数。创建目录，`cd` 进入，然后运行初始化。

```bash
mkdir my-app && cd my-app
pnpm init                                          # 如果还没有 package.json
pnpm dlx prisma-next init                          # 交互式
# 或非交互式（CI / 代理运行）:
pnpm dlx prisma-next init --yes --target postgres --authoring psl
```

> **遥测数据是可选的。** CLI 通过默认值收集匿名使用数据。每个命令——包括 `init`——在首次使用时在 **stderr** 上打印一次性通知，然后发送；没有交互式同意提示。随时通过运行 `prisma-next telemetry disable`，使用 `DO_NOT_TRACK=1` 或 `PRISMA_NEXT_DISABLE_TELEMETRY=1`，或在用户配置（`prisma-next` 配置目录，**不是** `prisma-next.config.ts`）中设置 `"enableTelemetry": false` 来退出。运行 `prisma-next telemetry status` 查看当前生效的内容。这对于代理驱动运行是相关的——CLI 记录了代理调用了它。收集的内容，用户配置路径以及如何完全重置在 `docs/Telemetry.md` 中记录。

`init` 接受的标志（运行 `prisma-next init --help` 获取权威来源）：

- `--target <db>` — `postgres` 或 `mongodb`。
- `--authoring <style>` — `psl` 或 `typescript`。
- `--schema-path <path>` — 默认为 `prisma/contract.prisma`（或 `prisma/contract.ts`）。**传递 `--schema-path src/prisma/contract.prisma`（或 `.../contract.ts`）** 以直接在规范 `src/prisma/` 位置脚手架——`init` 的默认值是错误的，见 [TML-2532](https://linear.app/prisma-company/issue/TML-2532)。
- `--force` — 覆盖现有脚手架而不提示（在已脚手架目录中重新运行 `init` 触发重新初始化流程——`--force` 跳过确认）。
- `--write-env` — 同时写入 `.env`（默认只写入 `.env.example`；`.env` 仍然在你的控制之下）。
- `--probe-db` — 连接到 `DATABASE_URL` 一次并检查服务器版本与目标的最低版本是否匹配。
- `--strict-probe` — 如果探测失败则失败 `init`（没有 `--probe-db` 则无操作）。
- `--no-install` — 跳过依赖项安装 + 初始合约发出。
- `--no-skill` — 跳过 Prisma Next 技能安装（空气隔离/受限环境）。技能集群始终在项目级别安装——永远不会全局安装——因此其版本锁定到项目的 Prisma Next 版本。

`init` 运行干净时写入：

- `prisma-next.config.ts` 在项目根目录。
- 合约源位于 `--schema-path` — 如果传递了规范覆盖，则为 `src/prisma/contract.prisma`，如果接受（目前错误的）默认值，则为 `prisma/contract.prisma`。
- 合约源所在目录中的 `db.ts`。
- `prisma-next.md` — 人类快速参考。
- `.env.example`（如果 `--write-env`）。
- 更新 `package.json`（依赖项 + 脚本）和 `tsconfig.json`（所需的编译器选项）。
- 安装依赖项并运行 `prisma-next contract emit` 一次。
- 在本地代理运行时中注册 Prisma Next 技能。

**如果你接受了 `init` 的默认值并最终得到一个顶层 `prisma/` 目录**（TML-2532），清理是一个操作 + 一个配置编辑：

```bash
mkdir -p src && mv prisma src/prisma
# 然后更新 prisma-next.config.ts 以便 `contract` 读取
# 'src/prisma/contract.prisma'（或 .ts）而不是 'prisma/contract.prisma'.
pnpm prisma-next contract emit   # 重新发出 contract.json + contract.d.ts under src/prisma/
```

在运行 `db init` 之前这样做——一旦写入标记行，重构就变得更困难。

初始化成功后，路径会汇聚到上面提到的 *Your first arc*。`init` 已经用 `User` 和 `Post` 模型（它们之间有一个关系）预填充了一个起始合约并运行了 `contract emit` 一次；唯一剩余的先决条件是设置 `DATABASE_URL` 和初始化数据库。两个命令：

1. 在 `.env` 中设置 `DATABASE_URL`（从 `.env.example` 复制）。
2. 初始化数据库：`pnpm prisma-next db init`。创建表，索引，约束，并写入标记行——使用 `init` 生成的起始合约。

然后运行上面 *Your first arc* 中的片段，使用你现有的表代替起始模型。弧是相同的；只有到达那里的路径不同。

**为什么这是查询优先，而不是模式编辑优先。** `init` 故意提供了 `User` 和 `Post`：用户不应该设计模式来证明他们的设置工作正常。扩展合约是第一个弧落地后的下一步，不是到达那里的一部分。如果用户要求你跳转到 *"添加一个 Comment 模型"*——当然，做这个——但如果任何疑问项目是否正确连接，首先针对 `User` 或 `Post` 运行一个查询变为绿色。

## 工作流——棕地-DB（现有数据库，没有合约）

概念：针对一个现有数据库，没有 PN 合约，`contract infer` 会遍历实时模式（表，列，索引，约束）并写入一个描述它的 PSL 合约。结果是一个 *起点*，不是最终合约——审查并清理它，然后使用 `db sign` 记录当前合约哈希作为标记（而不是让 `db init` 尝试从头开始重建模式）。

```bash
mkdir my-app && cd my-app
pnpm init
pnpm dlx prisma-next init --yes --target postgres --authoring psl
# 脚手架落地；你将覆盖下面的起始模式
```

然后，在 `.env` 中设置 `DATABASE_URL`：

```bash
pnpm prisma-next contract infer --db "$DATABASE_URL" --output src/prisma/contract.prisma
```

（注意：标志的标志是 `--output`，不是 `--out`。运行 `prisma-next contract infer --help` 获取完整表面。）

代理应该在这里暂停并阅读推断的 PSL。需要重新编写的情况的症状：

- PN 无法分类的表（例如，您可以表达为关系的遗留链接表）。
- PN 的类型猜测不正确的列（例如，`String` 而您想要扩展类型，如 `pgvector.Vector(length: 1536)`）。
- PN 无法看到的缺失 `@unique` / `@index` 提示。
- 您更喜欢别名字段名。

然后重新发出并签署：

```bash
pnpm prisma-next contract emit
pnpm prisma-next db sign
pnpm prisma-next db verify   # 确认数据库与合约匹配；如果不匹配，则报告差异
```

然后运行上面 *Your first arc* 中的片段，使用你现有的表代替起始模型。弧是相同的；只有到达那里的路径不同。

## 日常使用的命令

一个参考表——不是要背诵的脚本。命令在上述工作流中浮现，因为用户的下一步操作需要它们；这个表格在这里是为了在用户询问更广泛的视图时（通常在第一次往返之后），以及任何新导向 Prisma Next 的人可以扫描。对于标志级别的详细信息，运行 `<command> --help`；帮助输出是权威来源。

| 你想做什么 | 命令 | 更深的技能 |
|---|---|---|
| 应用当前合约到数据库第一次 | `prisma-next db init` | 这项技能 |
| 编辑合约源后重新发出 `contract.json` + `contract.d.ts` | `prisma-next contract emit` | `prisma-next-contract` |
| 快速开发仅模式同步（不保留迁移历史） | `prisma-next db update` | `prisma-next-migrations` |
| 计划从合约差异的迁移 | `prisma-next migration plan --name <slug>` | `prisma-next-migrations` |
| 应用挂起的迁移 | `prisma-next migrate` | `prisma-next-migrations` |
| 检查实时数据库 | `prisma-next db schema` | `prisma-next-debug` |
| 确认数据库与合约匹配（漂移检查） | `prisma-next db verify` | `prisma-next-debug` |
| 将现有数据库引入 PN 合约 | `prisma-next contract infer --db "$DATABASE_URL"` | 这项技能（棕地） |
| 解码结构化错误包 | (读取 `code` / `why` / `fix` 字段) | `prisma-next-debug` |
| 报告错误或请求功能 | (通过反馈技能提交) | `prisma-next-feedback` |

## 决策——PSL 与 TypeScript 编写模式

- **PSL** (`contract.prisma`) — 默认。简洁，声明性，任何使用过 Prisma 的人都会熟悉。建议大多数项目使用。
- **TypeScript** (`contract.ts`) — 程序化构建器。在合约确实计算时使用（多租户每个租户变体），当你重用合约片段跨文件时，或者当扩展需要 PSL 尚未表达的构造（例如 pgvector 的参数化存储类型注册）。与来自 `prisma-next-build` 的 Vite 插件配对以在保存时自动发出。

稍后通过在同一目录中重新运行 `prisma-next init` 切换编写模式。初始化流程检测到现有脚手架并提示重新初始化（在非交互式运行中使用 `--force` 跳过提示）。现有合约内容不会自动翻译——你将在目标语言中手动重新编写。

## 常见陷阱

1. **运行 `prisma-next init <project-name>` 带有位置参数。** `init` 作用于当前工作目录；没有位置项目名参数。`mkdir foo && cd foo && pnpm dlx prisma-next init`。
2. **`init` 无法连接到你的数据库。** 它只脚手架文件和安装依赖项（并运行初始 `contract emit`）。你通过 `db init` / `db update` / `migrate` 连接。如果 `init` 成功而查询失败，问题在于 `DATABASE_URL`，而不是 `init`。
3. **将推断的 PSL 视为最终合约。** `contract infer` 产生一个起点。不要 `db sign` 对一个你还没有阅读的合约。
4. **忘记编辑合约后发出。** 合约工件 (`contract.json`, `contract.d.ts`) 在你运行 `contract emit` 之前是过时的。如果类型检查器说模型 *"不存在"*，你错过了发出。
5. **在 `prisma-next.config.ts` 中设置 `DATABASE_URL` 考虑到 `.env`。配置通过 `dotenv/config` 自动读取 `.env`。硬编码 URL 泄露凭据并绕过每个环境的覆盖。见 `prisma-next-runtime`。
6. **手动编辑 `contract.json` 或 `contract.d.ts`。** 它们是发出的工件；下一个 `contract emit` 会覆盖你的更改。编辑源代码而不是。
7. **使用 `--out` for `contract infer`。** 标志是 `--output`。
