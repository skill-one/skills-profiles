# Prisma Next — 合约编写

> **编辑你的数据合约。Prisma 处理其余部分。**

数据合约是你数据层的单一事实来源。你编辑合约源 — `contract.prisma`（PSL，规范表面）或 `contract.ts`（TypeScript 构建器） — 框架会根据它派生类型、迁移和运行时配置。三步用户模型：

1. **你编辑你的数据合约。**
2. **系统为你计划迁移。** (`prisma-next-migrations`)
3. **如果你需要数据迁移，你编辑 `migration.ts` 并执行它。** (`prisma-next-migrations`)

步骤 1 后代理运行 `prisma-next contract emit`（每次编辑合约后），或者安装 Vite 插件以便捆绑器在保存时运行它（见 `prisma-next-build`）。Emit 读取合约源，通过 facade 基于文件扩展名选择提供者，然后写入两个位于源同位置的工件：

- `contract.json` — 规范的、内容哈希的合约中间表示 (IR)。被规划器、运行时和 `db verify` 读取。
- `contract.d.ts` — 运行时 + 域传播的精确 TypeScript 类型，当你从它导入 `Contract` 时。

这两个文件都是**发射工件**。编辑源；永远不要编辑 JSON 或 `.d.ts`。

## 使用场景

- 用户想要添加、更改或删除模型 / 字段 / 关系。
- 用户想要添加索引、唯一约束、枚举或值对象（复合类型）。
- 用户想要添加命名空间块（Postgres 模式）或跨合约外键。
- 用户想要在模型上设置 `@@control` 或配置 `defaultControlPolicy`。
- 用户想要使用来自扩展的自定义类型（`pgvector.Vector(length: 1536)`，`cipherstash.EncryptedString({...})`）。
- 用户想要通过 `prisma-next.config.ts` 中的 `extensions: [...]` 安装或配置扩展，包括 `@prisma-next/extension-supabase`。
- 用户正在迁移作者源（PSL ↔ TypeScript 构建器）。
- 用户收到了 `PN-CLI-4002`、`PN-CLI-4003` 或 `PN-CLI-4011` 来自 `contract emit`。
- 用户提到了：*模式、字段、模型、属性、prisma 模式、PSL、contract.prisma、contract.ts、contract.json、contract.d.ts、contract emit、facade 导入、`@prisma-next/postgres/config`、`@prisma-next/postgres/contract-builder`、扩展、pgvector、cipherstash、postgis、paradedb、supabase、命名空间、跨空间 FK、`@@control`、枚举、值对象、验证、回调、软删除、paranoid、作用域*。（最后一个集群路由到 *Prisma Next 尚未实现的功能* 下面。）

## 不使用场景

- 用户想要将合约更改应用到数据库 → `prisma-next-migrations`。
- 用户想要针对合约编写查询 → `prisma-next-queries`。
- 用户想要连接 `db.ts`（运行时入口点、中间件、环境配置）→ `prisma-next-runtime`。
- 用户想要 Vite / 打包器集成 → `prisma-next-build`。
- 用户想要首次设置 Prisma Next → `prisma-next-quickstart`。
- 用户想要深入了解单个结构化错误包 → `prisma-next-debug`。
- 用户想要提交缺失功能请求 → `prisma-next-feedback`。

## 关键概念

- **`@prisma-next/<target>` facade 是用户编写代码唯一导入的表面。** 对于 Postgres 应用：`@prisma-next/postgres/config`、`@prisma-next/postgres/contract-builder`、`@prisma-next/postgres/control`、`@prisma-next/postgres/runtime`。Mongo 具有相同的布局（`@prisma-next/mongo/config`、`@prisma-next/mongo/contract-builder`、`@prisma-next/mongo/runtime`）。每个扩展发布它自己的 facade — `@prisma-next/extension-pgvector/control`、`@prisma-next/extension-postgis/control`、`@prisma-next/extension-paradedb/control`。**永远不要从用户代码中访问 `@prisma-next/cli/*`、`@prisma-next/family-*`、`@prisma-next/target-*`、`@prisma-next/adapter-*`、`@prisma-next/driver-*` 或 `@prisma-next/sql-contract-*`。** facade 在其中烘焙了 family / target / adapter / driver 连接。见 *常见陷阱* #4。
- **合约源。** 框架读取并将其降低到规范合约中间表示 (IR) 的文件。两种风味，都是第一类：
  - **`contract.prisma` (PSL)** — 模式风味 DSL。典型应用和棕色字段 Prisma 用户的规范。通过 `contract: './<path>/contract.prisma'` 连接 — `defineConfig` facade 检测 `.prisma` 扩展名并通过 PSL 提供者路由。
  - **`contract.ts` (TypeScript 构建器)** — 基于程序的编写，使用 `defineContract({...}, ({ field, model, rel, type }) => ({...}))` 从 `@prisma-next/postgres/contract-builder`（或 `@prisma-next/mongo/contract-builder`）。通过 `contract: './<path>/contract.ts'` 连接 — facade 检测 `.ts` 扩展名并通过 TS 提供者路由。当你需要程序化组合（按租户变体、生成字段）或 PSL 尚未表达的构造（例如注册参数化扩展类型 — 见 pgvector 的合约）时使用。
- **`prisma-next.config.ts`。** 连接合约源、数据库连接、迁移目录和任何安装的扩展。使用 `defineConfig({...})` 从 `@prisma-next/postgres/config`（或 `@prisma-next/mongo/config`）。facade 接受的四个字段：`contract`（路径字符串 — `.prisma` 或 `.ts`）、`db`（`{ connection?: string }`）、`extensions`（控制描述符数组）、`migrations`（`{ dir?: string }`）。`contract.json` 的输出路径从 `contract` 自动派生（例如 `./src/prisma/contract.prisma` → `./src/prisma/contract.json`）。
- **发射管道。** `prisma-next contract emit --config <path>?` 读取 `prisma-next.config.ts`，调用 facade 选择的提供者，验证生成的合约，然后原子性地写入 `contract.json` + `contract.d.ts` 与源同位置。
- **扩展命名空间。** 扩展贡献命名空间构造函数（`pgvector.Vector(length: 1536)`，`cipherstash.EncryptedString({equality: true})`）和辅助预设。通过向两个位置添加描述符来安装它们 — 两个字段都命名为 `extensions`，但两个表面消费两种不同的描述符类型和形状：
  - **在配置（facade 和核心）：** `extensions: [pgvector]` — *控制* 描述符数组，从 `@prisma-next/extension-<name>/control` 导入。
  - **在 TS 构建器的 `defineContract`（仅当编写 `contract.ts` 时）：** `extensions: { pgvector }` — *包* 描述符记录，从 `@prisma-next/extension-<name>/pack` 导入。
- **合约空间。** 每个发射合约的包拥有自己的 *合约空间* — 包根目录的 `prisma-next.config.ts`、合约源、同位置发射的工件和 `migrations/` 目录。**有两个有意在磁盘上的布局**，由合约空间是消费应用程序还是合约空间包（扩展、内部聚合根包等）选择：
  - **应用程序布局**（构建应用程序时使用）。`prisma-next.config.ts` 在仓库根目录；`src/prisma/contract.{prisma,ts}`；`src/prisma/contract.{json,d.ts}` 与源同位置；`src/prisma/db.ts` 与源同位置；迁移在 `migrations/app/<timestamp>_<slug>/` 下。`app/` 段是消费应用程序的空间 ID；扩展空间 ID 落在扩展包管理的兄弟 `migrations/<extension-space-id>/` 目录中。这是 `examples/prisma-next-demo` 使用的。`prisma-next init` 目前构建了不同的东西（`prisma/...` 在仓库根目录）—— 这是一个缺陷（TML-2532）；规范布局是每个命令实际期望看到的。
  - **合约空间包布局**（发布合约空间包时使用——扩展、内部单体仓库包）。`prisma-next.config.ts` 在包根目录；`src/contract.{prisma,ts}` 直接（没有 `prisma/` 子目录）；`src/contract.{json,d.ts}` 与源同位置；`migrations/<timestamp>_<slug>/` 直接在 `migrations/` 下（没有 `<space-id>` 段——包本身是一个单一空间）。在 `.cursor/rules/contract-space-package-layout.mdc` 和 ADR 212 中记录。
  
  两种布局都允许 `defineConfig` 的 `contract:` 路径指向源；框架从那里派生所有其他内容（发射输出、迁移根）。选择与你要构建的匹配的布局并坚持使用——不要混合。

## 诊断代码

`prisma-next contract emit` 表面结构化错误，具有稳定代码；按 `code` 而不是消息文本分支。

| 代码 | 含义 | 下一步 |
|---|---|---|
| `PN-CLI-4002` *合约配置缺失* | `contract` 未在 `prisma-next.config.ts` 中设置。 | 向 `defineConfig({...})` 从 `@prisma-next/postgres/config` 添加 `contract: './src/prisma/contract.prisma'`（应用布局）或 `'./src/contract.prisma'`（合约空间包布局）——同样适用于 `.ts` 源——。 |
| `PN-CLI-4003` *合约验证失败* | 源已加载，但合约中间表示 (IR) 失败结构验证。 | 阅读 `meta.diagnostics` / `meta.issues` 以获取冒犯的模型/字段，修复源，重新发射。 |
| `PN-CLI-4011` *缺失扩展包在配置中* | 合约使用命名空间构造函数（例如 `pgvector.Vector(...)`），但配置中的 `extensions` 未列出匹配的描述符。 `meta.missingExtensions` 列出了它们。 | 安装包，导入其控制描述符（`import pgvector from '@prisma-next/extension-pgvector/control'`），将其添加到 `prisma-next.config.ts` 中的 `extensions: [...]`。 |

## 工作流程 — 读取合约源

概念：每个合约更改都从定位源文件开始。配置是权威的——读取 `prisma-next.config.ts`，找到 `contract:` 字段（facade 下的路径字符串），并打开它指向的文件。相同的字段告诉您安装的 `extensions: [...]`。

```bash
cat prisma-next.config.ts
```

如果 `contract:` 以 `.prisma` 结尾，源是 PSL；如果以 `.ts` 结尾，源是 TS 构建器。如果 `prisma-next.config.ts` 缺失，路由到 `prisma-next-quickstart`。

## 工作流程 — 编辑模型 / 字段 / 关系（PSL）

概念：PSL 模型降低为表（Mongo 上为集合）；字段降低为列；`@relation(...)` 声明外键的一侧。只在拥有侧添加关系——框架自动派生反向引用。

```prisma
model User {
  id    Int    @id @default(autoincrement())
  email String @unique
}

model Post {
  id       Int    @id @default(autoincrement())
  title    String
  authorId Int
  author   User   @relation(fields: [authorId], references: [id], onDelete: Cascade)

  @@unique([title, authorId])
  @@index([authorId])
}
```

然后运行 `pnpm prisma-next contract emit`（或依赖 Vite 插件——见 `prisma-next-build`）。使用 `onDelete` / `onUpdate` 明确指定级联行为；默认是 `Restrict`。

`@@index` 也接受 `expression:`（而不是字段列表）、`where:`（部分索引谓词）、`unique:`, `type:`/`options:`（目标注册的访问方法），以及 `name:` xor `map:`:

```prisma
@@index(expression: "lower(email)", name: "users_email_lower")
@@index([authorId], where: "(archived_at IS NULL)", name: "posts_author_active")
```

`name:` 声明一个受管理的索引（物理名称 `<name>_<8-hex hash>`，重命名计划为 `ALTER INDEX … RENAME`）；`map:` 直接采用确切的物理名称（用于 infer-captured objects — 将其与 SQL 身体结合会发出警告，因为漂移检测以字节方式比较授权文本与 Postgres 的重印）。`expression:` 需要 `name:` 或 `map:`。TS 构建器通过 `constraints.index([cols.x], {...})` / `constraints.index({ expression, ... })` 镜像此功能——见 `packages/2-sql/2-authoring/contract-ts/README.md`。

PSL 别名表面用于重复类型位于顶级 `types {}` 块中：

```prisma
types {
  Email = String
}

model User {
  id    Int    @id @default(autoincrement())
  email Email  @unique
}
```

注意：标量列表（例如 `String[]`）和隐式 Prisma-ORM 多对多（双方都没有连接模型，但存在列表导航）被 SQL 解释器拒绝——使用连接模型。复合/嵌入类型（`type Address { ... }` 在模型上带有 `address Address`）受支持：解释器将它们降低为合约域中的 `valueObjects`，并将它们存储为 `jsonb` 列。见 *工作流程 — 值对象* 下面。

## 工作流程 — 值对象（复合类型）

概念：`type Foo { ... }` 块声明值对象形状。解释器将它们降低为合约域中的 `valueObjects`，并将它们存储为 `jsonb` 列。支持嵌套值对象引用。

```prisma
type Address {
  street  String
  city    String
  zip     String?
  country String
}

model User {
  id      String   @id @default(uuid())
  email   String
  address Address?
}
```

发射的 `contract.json` 包含 `domain.namespaces.<ns>.valueObjects.Address` 及其字段描述符，`address` 列最终作为 `codecId: "pg/jsonb@1"` / `nativeType: "jsonb"` 存储在 `storage` 中。

规范工作示例：`examples/prisma-next-demo/src/prisma/contract.prisma`。

## 工作流程 — 枚举

概念：PSL `enum` 块声明一个域枚举：一个命名值集通过声明的编解码器（`@@type("pg/text@1"` → 一个 `text` 列）存储，并通过规划器生成的 CHECK 约束强制执行。每个成员映射到其数据库值 `Name = "value"`。在任何模型上使用枚举名称作为字段类型，该模型位于同一合约中。

```prisma
enum user_type {
  @@type("pg/text@1")
  admin = "admin"
  user  = "user"
}

model User {
  id   String    @id @default(uuid())
  kind user_type
}
```

规范工作示例：`examples/prisma-next-demo/src/prisma/contract.prisma`。

## 工作流程 — 命名空间（Postgres 模式）

概念：将模型包装在 `namespace <name> { ... }` 块中，将它们放置在非默认 Postgres 模式下。任何块外的模型都进入隐式默认命名空间。

```prisma
namespace public {
  model Profile {
    id       String @id @default(uuid())
    username String
    userId   String @unique
    @@map("profile")
  }
}
```

规范工作示例：`examples/supabase/src/contract.prisma`。

## 工作流程 — 跨合约外键

概念：关系字段可以引用另一个合约空间中的模型，使用 `<space>:<namespace>.<Model>` 形式。合约还支持在顶级 `types {}` 块中命名类型别名，由相同的裸类型位置构造函数支持，这些构造函数也用于字段。移除了 `@db.X(args)` 通道：重写 `@db.X` 为 `X`，重写 `@db.X(args)` 为 `X(args)`；剩余使用会以可操作的诊断命名替换。

```prisma
types {
  AuthUserId = Uuid
}

namespace public {
  model Profile {
    id       String     @id @default(uuid())
    username String
    userId   AuthUserId @unique
    user     supabase:auth.AuthUser @relation(fields: [userId], references: [id], onDelete: Cascade)
    @@map("profile")
  }
}
```

`supabase:auth.AuthUser` 的意思是：`AuthUser` 模型在 `auth` 命名空间中的 `supabase` 合约空间中。目标空间由注册的扩展包提供（这里 `@prisma-next/extension-supabase/pack`）。

规范工作示例：`examples/supabase/src/contract.prisma`。

## 工作流程 — `@@control`（控制策略）

概念：在模型上设置 `@@control(<policy>)` 会设置 Prisma 是否管理该表的 DDL 在迁移中。参数是位置小写文字——`managed`、`tolerated`、`external` 或 `observed` 之一。

```prisma
model AuditLog {
  id        Int    @id
  message   String

  @@control(observed)
}
```

可以在合约级别设置默认值，通过 `prismaContract(path, { defaultControlPolicy })` 上的 `defaultControlPolicy` 设置。见 `prisma-next-migrations`，了解控制策略如何影响 DDL 规划。

## 工作流程 — `@prisma-next/extension-supabase`

概念：Supabase 扩展提供 `supabase` 合约空间（`auth` / `storage` 模式作为 `external` 表，以及平台角色）。它不暴露 `/control` 子路径，因此无法通过用户面 `defineConfig({ extensions: [...] })` facade 注册——它通过低级配置中的 `extensions` 连接。见 `examples/supabase` 以获取完整的工作模式。

`prisma-next.config.ts`（与示例镜像）:

```typescript
import supabasePack from '@prisma-next/extension-supabase/pack';
import { defineConfig } from '@prisma-next/cli/config-types';
// ... 其他低级导入

export default defineConfig({
  // ...
  extensions: [supabasePack],
});
```

`db.ts` **不**使用标准的 `postgres()` 工厂——Supabase 应用使用来自 `@prisma-next/extension-supabase/runtime` 的 `supabase()` 工厂构建客户端（角色优先：`asUser(jwt)` / `asAnon()` / `asServiceRole()`，JWT 验证，RLS）。该运行时——以及 RLS 策略编写（`policy_select` / `@@rls`）——由 **`prisma-next-supabase`** 覆盖；为配置连接后的任何内容加载它。

导出子路径：`@prisma-next/extension-supabase/pack`, `@prisma-next/extension-supabase/runtime`, `@prisma-next/extension-supabase/contract`. 规范工作示例：`examples/supabase`。

## 工作流程 — 棕色字段内省

概念：从现有数据库中提取合约源并继续。`prisma-next contract infer --db <url>` 读取实时模式并写入一个 `contract.prisma` 文件。它停止在那里——跟随它进行 `contract emit`，以及（当模式与固定哈希匹配时）作为单独步骤进行 `db sign`。

```bash
pnpm prisma-next contract infer --db $DATABASE_URL --output ./src/prisma/contract.prisma
pnpm prisma-next contract emit
```

## 常见陷阱

1. **编辑后忘记重新发射。** `contract.json` 和 `contract.d.ts` 过期；下游类型检查和 `migration plan` 看到旧的形状。重新发射，或者安装 Vite 插件（`prisma-next-build`）。
2. **编辑发射的工件。** `contract.json` 和 `contract.d.ts` 是发射的；那里的编辑在下次发射时会循环返回。编辑源。
3. **TS 构建器错误的工厂/导入路径。** `defineContract`, `field`, `model`, `rel` 来自 `@prisma-next/postgres/contract-builder`（或 `@prisma-next/mongo/contract-builder`）。在回调重载之外，可用的字段构造函数是 `field.column(...)`, `field.generated(...)`, `field.namedType(...)`.
4. **从用户代码中访问内部包。** 用户编写文件（`prisma-next.config.ts`, `contract.ts`, `db.ts`, 控制客户端）仅导入 `@prisma-next/<target>/<subpath>` 和 `@prisma-next/extension-<name>/<subpath>`。来自 `@prisma-next/cli/*`, `@prisma-next/family-*`, `@prisma-next/target-*`, `@prisma-next/adapter-*`, `@prisma-next/driver-*`, 或 `@prisma-next/sql-contract-*` 的导入是框架内部的——facade 为您组合它们。如果您的 facade 子路径在您的目标中缺失，请参阅 *Prisma Next 尚未实现的功能* 并路由到 `prisma-next-feedback`。规范工作示例是 `examples/multi-extension-monorepo/app/prisma-next.config.ts` 和 `examples/prisma-next-postgis-demo/prisma-next.config.ts`。
5. **混淆配置 `extensions` 与 TS 构建器的 `extensions`。** 相同的包，两个表面，一个字段名但两种形状：`defineConfig({ extensions: [pgvector] })`（*控制* 描述符数组，从 `@prisma-next/extension-<name>/control` 导入）与 `defineContract({ extensions: { pgvector } })`（*包* 描述符记录，从 `@prisma-next/extension-<name>/pack` 导入）。
6. **重命名字段并期望规划器检测。** Prisma Next 没有合约内重命名提示；规划器看到破坏性删除+添加。在 `migration plan` 后手动编辑 `migration.ts`（见 `prisma-next-migrations`），或者使用保留然后删除的两迁移模式。

## Prisma Next 尚未实现的功能

- **合约内重命名提示。** 没有 `@@rename(old: ..., new: ...)` 或类似。使用 *常见陷阱* #6 中的工作绕过。要请求第一类重命名，请通过 `prisma-next-feedback` 提交。
- **模型验证。** 没有 `@validates(...)` 表面。在应用代码中验证（arktype）。要请求合约中的声明性验证，请通过 `prisma-next-feedback` 提交。
- **生命周期回调**（`beforeSave`, `afterCreate` 等）。不受支持。使用中间件（`prisma-next-runtime`）或应用代码。要请求生命周期回调，请通过 `prisma-next-feedback` 提交。
- **软删除 / `paranoid: true`。** 没有内置软删除列。添加一个可空的 `deletedAt DateTime?` 并在查询中显式过滤（或在中间件中过滤）。要请求内置软删除，请通过 `prisma-next-feedback` 提交。
- **作用域 / 默认过滤器。** 没有 ActiveRecord 风格的作用域。自己组合查询辅助函数。要请求作用域，请通过 `prisma-next-feedback` 提交。
- **隐式 Prisma-ORM 多对多。** 双方都没有显式连接模型，列表导航被拒绝。显式编写连接模型。要请求隐式 M2M，请通过 `prisma-next-feedback` 提交。

## 参考

- 运行 `pnpm prisma-next contract --help` 获取实时命令表面。
- PSL 特性表面和解释器接受的内容：`packages/2-sql/2-authoring/contract-psl/README.md`。
- TS 构建器表面和回调帮助词汇：`packages/2-sql/2-authoring/contract-ts/README.md`。
- 布局（`contract.prisma`, `contract.json`, `contract.d.ts` 和 `migrations/` 放在哪里）:
  - **应用布局** (`src/prisma/...` + `migrations/app/...`) — `examples/prisma-next-demo` 演示的规范形状；消费应用程序使用的规范布局。
  - **合约空间包布局** (`src/contract.{prisma,ts}` 直接，`migrations/<timestamp>_<slug>/` 直接在 `migrations/` 下，没有 `<space-id>` 段——包本身是一个单一空间）。在 `.cursor/rules/contract-space-package-layout.mdc` 和 ADR 212 中记录。

## 检查清单

- [ ] 读取 `prisma-next.config.ts` 并确定合约源（以 `.prisma` 或 `.ts` 结尾的路径字符串）和安装的 `extensions: [...]`。
- [ ] 所有用户编写的导入解析为 `@prisma-next/<target>/<subpath>`（例如 `@prisma-next/postgres/config`）。用户文件中没有来自 `@prisma-next/cli/*`、`@prisma-next/family-*`、`@prisma-next/target-*`、`@prisma-next/adapter-*`、`@prisma-next/driver-*` 或 `@prisma-next/sql-contract-*` 的导入。
- [ ] 编辑了合约源 (`contract.prisma` 或 `contract.ts`), 而不是发射的工件。
- [ ] 对于新的扩展命名空间：添加了包，导入了其控制描述符（`@prisma-next/extension-<name>/control`），将其添加到 `defineConfig({...})` 中的 `extensions: [...]`（如果使用 TS 构建器，则将匹配的包描述符添加到 `defineContract({extensions: {...}})`）。
- [ ] 对于重命名：在 `migration plan` 后手动编辑 `migration.ts`（或者使用保留然后删除的两迁移模式）——Prisma Next 目前没有重命名提示。
- [ ] 编辑后运行 `pnpm prisma-next contract emit`（或者依赖 Vite 插件重新发射在保存时）。
- [ ] 确认 `contract.json` 和 `contract.d.ts` 更新为与源相邻。
- [ ] **没有**手动编辑 `contract.json` / `contract.d.ts`。
- [ ] **没有**编造缺失的功能（验证、回调、软删除、作用域）——将用户引导至 *Prisma Next 尚未实现的功能* + `prisma-next-feedback`.
