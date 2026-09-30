---
name: prisma-next-contract
description: 编辑 Prisma Next 数据合约——添加模型、字段、关系、索引、枚举、值对象（复合类型）、类型别名、命名空间（Postgres 模式）、跨合约外键（跨空间 FK）、多态类型（`@@discriminator` / `@@base`）、使用扩展命名空间（`pgvector.Vector(...)`、`cipherstash.EncryptedString(...)`）、使用 `@prisma-next/<target>/config` 面具中的 `defineConfig` 配置 `prisma-next.config.ts`，并运行 `prisma-next contract emit`。用于模式、模型、字段、属性、软删除、paranoid、作用域、验证、回调、prisma schema、PSL、contract.prisma、contract.ts、contract.json、contract.d.ts、`@prisma-next/postgres/config`、`@prisma-next/postgres/contract-builder`、`@prisma-next/postgres/control`、`@prisma-next/mongo/config`、`@prisma-next/mongo/contract-builder`、`extensions:`、pgvector、cipherstash、postgis、paradedb、supabase、`@prisma-next/extension-supabase`、`@@control`、控制策略、受管理、容忍、外部、观察。
---

# Prisma Next — 合约编写

> **编辑你的数据合约。Prisma 会处理其余部分。**

数据合约是你数据层的单一事实来源。你编辑合约源——`contract.prisma`（PSL，规范表面）或`contract.ts`（TypeScript 构建器）——框架会从它派生类型、迁移和运行时配置。三步用户模型：

1. **你编辑你的数据合约。**
2. **系统为你计划迁移。** (`prisma-next-migrations`)
3. **如果你需要数据迁移，你编辑`migration.ts`并执行它。** (`prisma-next-migrations`)

第一步背后，代理会运行`prisma-next contract emit`（每次编辑合约后），或者安装 Vite 插件让打包器在保存时运行它（见`prisma-next-build`）。Emit 会通过基于`contract:`文件扩展名的 façade 选择的提供者读取合约源，然后写入两个位于源文件同位置的产物：

- `contract.json`——规范、内容哈希的合约 IR。被规划器、运行时和`db verify`读取。
- `contract.d.ts`——运行时+lanes 在你从它导入`Contract`时传播的精确 TypeScript 类型。

这两个文件都是**发射产物**。编辑源；不要编辑 JSON 或`.d.ts`。

## 使用场景

- 用户想添加、更改或删除模型/字段/关系。
- 用户想添加索引、唯一约束、枚举或值对象（复合类型）。
- 用户想添加命名空间块（Postgres 模式）或跨合约外键。
- 用户想为模型设置`@@control`或配置`defaultControlPolicy`。
- 用户想使用来自扩展的自定义类型（`pgvector.Vector(length: 1536)`，`cipherstash.EncryptedString({...})`）。
- 用户想通过`prisma-next.config.ts`中的`extensions: [...]`安装或配置扩展，包括`@prisma-next/extension-supabase`。
- 用户在编写源之间迁移（PSL ↔ TypeScript 构建器）。
- 用户收到`PN-CLI-4002`、`PN-CLI-4003`或`PN-CLI-4011`来自`contract emit`。
- 用户提到：*模式、字段、模型、属性、prisma 模式、PSL、contract.prisma、contract.ts、contract.json、contract.d.ts、contract emit、façade 导入、`@prisma-next/postgres/config`、`@prisma-next/postgres/contract-builder`、扩展、pgvector、cipherstash、postgis、paradedb、supabase、命名空间、跨空间 FK、`@@control`、枚举、值对象、验证、回调、软删除、paranoid、作用域*（最后一组会路由到*Prisma Next 尚未实现的功能*下方）。

## 不使用场景

- 用户想将合约更改应用到数据库 → `prisma-next-migrations`。
- 用户想对合约编写查询 → `prisma-next-queries`。
- 用户想连接`db.ts`（运行时入口点、中间件、环境配置）→ `prisma-next-runtime`。
- 用户想使用 Vite / 打包器集成 → `prisma-next-build`。
- 用户想首次设置 Prisma Next → `prisma-next-quickstart`。
- 用户想深入了解单个结构化错误包 → `prisma-next-debug`。
- 用户想提交缺失功能请求 → `prisma-next-feedback`。

## 关键概念

- **`@prisma-next/<target>` façade 是用户编写代码唯一导入的表面。** 对于 Postgres 应用：`@prisma-next/postgres/config`、`@prisma-next/postgres/contract-builder`、`@prisma-next/postgres/control`、`@prisma-next/postgres/runtime`。Mongo 有相同的布局（`@prisma-next/mongo/config`、`@prisma-next/mongo/contract-builder`、`@prisma-next/mongo/runtime`）。每个扩展都会发布自己的 façade——`@prisma-next/extension-pgvector/control`、`@prisma-next/extension-postgis/control`、`@prisma-next/extension-paradedb/control`。**永远不要从用户代码中访问`@prisma-next/cli/*`、`@prisma-next/family-*`、`@prisma-next/target-*`、`@prisma-next/adapter-*`、`@prisma-next/driver-*`或`@prisma-next/sql-contract-*`。** façade 会烘焙家庭/目标/适配器/驱动器连接。见*常见陷阱* #4。
- **合约源。** 框架读取并降低到规范合约 IR 的文件。两种类型，都是第一类：
  - **`contract.prisma` (PSL)**——模式风格的 DSL。典型应用和传统 Prisma 用户的规范。通过`contract: './<path>/contract.prisma'`连接——`defineConfig` façade 检测`.prisma`扩展并路由到 PSL 提供者。
  - **`contract.ts` (TypeScript 构建器)**——使用`defineContract({...}, ({ field, model, rel, type }) => ({...}))`从`@prisma-next/postgres/contract-builder`（或`@prisma-next/mongo/contract-builder`）进行程序化编写。通过`contract: './<path>/contract.ts'`连接——façade 检测`.ts`扩展并路由到 TS 提供者。当你需要程序化组合（租户变体、生成字段）或 PSL 无法表达的构造（例如注册参数化扩展类型——见 pgvector 的合约）时使用。
- **`prisma-next.config.ts`。** 连接合约源、数据库连接、迁移目录和任何安装的扩展。使用来自`@prisma-next/postgres/config`（或`@prisma-next/mongo/config`）的`defineConfig({...})`。façade 接受的四个字段：`contract`（路径字符串——`.prisma`或`.ts`）、`db`（`{ connection?: string }`）、`extensions`（控制描述符数组）、`migrations`（`{ dir?: string }`）。`contract.json`的输出路径自动从`contract`派生（例如`./src/prisma/contract.prisma` → `./src/prisma/contract.json`）。
- **发射管道。** `prisma-next contract emit --config <path>?`读取`prisma-next.config.ts`，调用 façade 选择的提供者，验证生成的合约，然后原子性地写入`contract.json` + `contract.d.ts`与源文件同位置。
- **扩展命名空间。** 扩展会贡献命名空间构造函数（`pgvector.Vector(length: 1536)`、`cipherstash.EncryptedString({equality: true})`）和辅助预设。通过向**两个**位置添加描述符来安装它们——两个字段都命名为`extensions`，但两个表面消费两种不同类型的描述符和形状：
  - **在配置（façade 和核心）：** `extensions: [pgvector]`——从`@prisma-next/extension-<name>/control`导入的控制描述符数组。
  - **在 TS 构建器的`defineContract`（仅当编写`contract.ts`时）：** `extensions: { pgvector }`——从`@prisma-next/extension-<name>/pack`导入的包描述符记录。
- **合约空间。** 每个发射合约的包都拥有自己的*合约空间*——包根目录的`prisma-next.config.ts`、合约源、同位置发射的产物和`migrations/`目录。**有两个有意磁盘布局**，由合约空间是消费应用还是合约空间包（扩展、内部聚合根包等）决定：
  - **应用布局**（构建*应用*时使用）。`prisma-next.config.ts`在仓库根目录；`src/prisma/contract.{prisma,ts}`；`src/prisma/contract.{json,d.ts}`同位置；`src/prisma/db.ts`同位置；迁移在`migrations/app/<timestamp>_<slug>/`下。`app/`段是消费应用的space-id；扩展space-ids位于扩展包管理的兄弟`migrations/<extension-space-id>/`目录。这是`examples/prisma-next-demo`使用的。`prisma-next init`目前生成不同的结构（仓库根目录下的`prisma/...`）——这是一个缺陷（TML-2532）；规范布局是每个命令实际期望看到的。
  - **合约空间包布局**（发布合约空间包时使用——扩展、内部单体仓库包）。`prisma-next.config.ts`在包根目录；`src/contract.{prisma,ts}`直接（没有`prisma/`子目录）；`src/contract.{json,d.ts}`同位置；`migrations/<timestamp>_<slug>/`直接在`migrations/`下（没有`<space-id>`段——包本身就是一个单一空间）。在`.cursor/rules/contract-space-package-layout.mdc`和 ADR 212 中记录。

  两种布局都允许`defineConfig`的`contract:`路径指向源；框架会从那里派生所有其他内容（发射输出、迁移根）。选择与你正在构建的匹配的布局并坚持使用——不要混合。

## 诊断代码

`prisma-next contract emit`会以稳定的代码表面结构化错误；按`code`分支而不是消息文本。

| 代码 | 含义 | 下一步 |
|---|---|---|
| `PN-CLI-4002` *合约配置缺失* | `contract`未在`prisma-next.config.ts`中设置。 | 向`defineConfig({...})`从`@prisma-next/postgres/config`添加`contract: './src/prisma/contract.prisma'`（应用布局）或`'./src/contract.prisma'`（合约空间包布局）——同样适用于`.ts`源。 |
| `PN-CLI-4003` *合约验证失败* | 源加载但合约 IR 结构验证失败。 | 读取`meta.diagnostics` / `meta.issues`以获取冒犯性模型/字段，修复源，重新发射。 |
| `PN-CLI-4011` *缺失配置中的扩展包* | 合约使用命名空间构造函数（例如`pgvector.Vector(...)`），但配置中的`extensions`未列出匹配的描述符。`meta.missingExtensions`命名它们。 | 安装包，导入其控制描述符（`import pgvector from '@prisma-next/extension-pgvector/control'`），将其添加到`prisma-next.config.ts`中的`extensions: [...]`。 |

## 工作流——读取合约源

概念：每个合约更改都从定位源文件开始。配置是权威的——读取`prisma-next.config.ts`，找到`contract:`字段（façade 下的路径字符串），然后打开它指向的文件。相同的字段告诉你安装的`extensions: [...]`。

```bash
cat prisma-next.config.ts
```

如果`contract:`以`.prisma`结尾，源是 PSL；如果以`.ts`结尾，源是 TS 构建器。如果`prisma-next.config.ts`缺失，路由到`prisma-next-quickstart`。

## 工作流——编辑模型/字段/关系（PSL）

概念：PSL 模型降低为表（Mongo 上为集合）；字段降低为列；`@relation(...)`声明外键端。只在拥有端添加关系——框架会自动派生反向引用。

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

然后运行`pnpm prisma-next contract emit`（或依赖 Vite 插件——见`prisma-next-build`）。使用`onDelete` / `onUpdate`显式指定级联行为；默认是`Restrict`。

`@@index`也接受`expression:`（替代字段列表）、`where:`（部分索引谓词）、`unique:`、`type:`/`options:`（目标注册访问方法）和`name:` xor `map:`：

```prisma
@@index(expression: "lower(email)", name: "users_email_lower")
@@index([authorId], where: "(archived_at IS NULL)", name: "posts_author_active")
```

`name:`声明一个受管理的索引（物理名称`<name>_<8-hex hash>`，重命名计划为`ALTER INDEX … RENAME`）；`map:`直接采用精确物理名称（用于 infer-captured 对象——结合 SQL 身体会警告，因为漂移检测会字节比较编写的文本与 Postgres 的重印）。`expression:`需要`name:`或`map:`。TS 构建器通过`constraints.index([cols.x], {...})` / `constraints.index({ expression, ... })`镜像此功能——见`packages/2-sql/2-authoring/contract-ts/README.md`。

PSL 重复类型表面位于顶级`types {}`块：

```prisma
types {
  Email = String
}

model User {
  id    Int    @id @default(autoincrement())
  email Email  @unique
}
```

注意：标量列表（例如`String[]`）和隐式 Prisma-ORM 多对多（双方无连接模型的无连接导航）被 SQL 解释器拒绝——使用连接模型。复合/嵌入类型（`type Address { ... }`在模型上带有`address Address`）受支持：解释器将它们降低为域中的`valueObjects`并作为`jsonb`列存储。见*工作流——值对象*下方。

## 工作流——编辑模型/字段/关系（TS 构建器）

概念：相同模型，不同的编写表面。façade 重新导出`defineContract`、`field`、`model`、`rel`，以及`family`/`target`包作为`@prisma-next/postgres/family`和`@prisma-next/postgres/target`的默认导出。使用回调重载（`defineContract({...}, ({ field, model, rel, type }) => ({...}))`）以获取高级助手（`field.text()`、`field.id.uuidv7String()`、`field.temporal.createdAt()`、`type.sql.String(35)`）。

```typescript
import sqlFamily from '@prisma-next/postgres/family';
import { defineContract } from '@prisma-next/postgres/contract-builder';
import postgresPack from '@prisma-next/postgres/target';

export const contract = defineContract(
  {
    family: sqlFamily,
    target: postgresPack,
  },
  ({ field, model }) => ({
    models: {
      User: model('User', {
        fields: {
          id: field.id.uuidv7String(),
          email: field.text().unique(),
          createdAt: field.temporal.createdAt(),
        },
      }).sql({ table: 'app_user' }),
    },
  }),
);
```

然后`pnpm prisma-next contract emit`。`field.<scalar>()`助手仅在回调重载内可用；回调外只有`field.column(...)`、`field.generated(...)`、`field.namedType(...)`存在。

对于 Mongo，将每个`@prisma-next/postgres/*`导入替换为`@prisma-next/mongo/*`。Mongo 构建器还暴露了`index`和`valueObject`。

## 工作流——添加扩展类型标量（pgvector）

概念：扩展会贡献一个命名空间（`pgvector.*`）和两种描述符风格——配置 façade 的*控制*描述符和 TS 构建器的*包*描述符。在`defineConfig.extensions`（数组形式）中注册控制描述符。如果你使用 TS 构建器编写，还应在`defineContract.extensions`（记录形式）中注册包描述符。然后在合约中引用命名空间构造函数。

`prisma-next.config.ts`:

```typescript
import pgvector from '@prisma-next/extension-pgvector/control';
import { defineConfig } from '@prisma-next/postgres/config';

export default defineConfig({
  contract: './src/prisma/contract.prisma',
  extensions: [pgvector],
});
```

`src/prisma/contract.prisma`:

```prisma
model Document {
  id        Int                          @id @default(autoincrement())
  content   String
  embedding pgvector.Vector(length: 1536)
}
```

发射。命名类型降低将`vector(1536)`放在列上，类型映射在`contract.d.ts`中携带正确的 TS 类型。

如果你未在配置中注册包而引用`pgvector.*`，发射会失败，并带有`PN-CLI-4011`和`meta.missingExtensions: ['pgvector']`。包的`fix`文本说*"向`prisma-next.config.ts`中的`extensions`添加缺失的扩展描述符"*——该字段名与 façade 匹配。

对于涵盖单扩展和多扩展设置的规范工作示例，请阅读`examples/multi-extension-monorepo/app/prisma-next.config.ts`和`examples/prisma-next-postgis-demo/prisma-next.config.ts`。

## 工作流——多态（`@@discriminator` / `@@base`）

概念（SQL 目标）：一个基础模型声明 discriminator 字段；每个变体模型声明其基础 + discriminator 值。变体通过**是否设置`@@map(...)`**选择 STI 还是 MTI：没有`@@map`意味着变体继承基础表（单表继承）；`@@map("variant_table")`意味着变体获得自己的表，通过主键 1:1 连接（多表继承）。

```prisma
model Task {
  id    Int    @id @default(autoincrement())
  title String
  type  String

  @@discriminator(type)
  @@map("tasks")
}

// STI variant — shares the `tasks` table.
model Bug {
  severity String

  @@base(Task, "bug")
}

// MTI variant — joins to `tasks` via PK; carries its own `features` table.
model Feature {
  priority Int

  @@base(Task, "feature")
  @@map("features")
}
```

若对多态语法有疑问，请参考解释器测试：`packages/2-sql/2-authoring/contract-psl/test/interpreter.polymorphism.test.ts`。

Mongo 没有模式层，因此其在 Mongo 上的多态是通过在 TS 构建器中的模型上显式的 `discriminator` 字段来建模的（参见 `@prisma-next/mongo/contract-builder`）；`@@base` / `@@discriminator` PSL 属性仅适用于 SQL。

查询变体是运行时问题——参见 `prisma-next-queries`。

## 工作流——值对象（复合类型）

概念：`type Foo { ... }` 块声明值对象形状。解释器将其转换为合同域中的 `valueObjects` 并存储为 `jsonb` 列。支持嵌套值对象引用。

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

生成的 `contract.json` 包含 `domain.namespaces.<ns>.valueObjects.Address` 及其字段描述符，`address` 列作为 `codecId: "pg/jsonb@1"` / `nativeType: "jsonb"` 存储在 `storage` 中。

规范示例：`examples/prisma-next-demo/src/prisma/contract.prisma`。

## 工作流——枚举

概念：PSL `enum` 块声明一个域枚举：一个通过声明的编解码器（`@@type("pg/text@1")` → `text` 列）存储的命名值集，并通过规划器生成的 CHECK 约束强制执行。每个成员映射到其数据库值（`Name = "value"`）。在同一个合同中的任何模型上使用枚举名作为字段类型。

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

规范示例：`examples/prisma-next-demo/src/prisma/contract.prisma`。

## 工作流——命名空间（Postgres 模式）

概念：使用 `namespace <name> { ... }` 块将模型放置在非默认的 Postgres 模式下。任何块外的模型都进入隐式的默认命名空间。

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

规范示例：`examples/supabase/src/contract.prisma`。

## 工作流——跨合同外键

概念：关系字段可以使用 `<space>:<namespace>.<Model>` 形式引用另一个合同空间中的模型。合同还支持在 `types {}` 块中命名顶级类型别名，其由与字段相同的裸类型位置构造器支持。`@db.X(args)` 通道被移除：将 `@db.X` 重写为 `X`，将 `@db.X(args)` 重写为 `X(args)`；其余使用将因可操作的诊断命名替换而失败。

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

`supabase:auth.AuthUser` 的含义：在 `supabase` 合同空间的 `auth` 命名空间中模型 `AuthUser`。目标空间由注册的扩展包提供（此处为 `@prisma-next/extension-supabase/pack`）。

规范示例：`examples/supabase/src/contract.prisma`。

## 工作流——`@@control`（控制策略）

概念：在模型上使用 `@@control(<policy>)` 设置 Prisma 是否在迁移中管理该表的 DDL。参数是位置小写字面量——`managed`、`tolerated`、`external` 或 `observed` 之一。

```prisma
model AuditLog {
  id        Int    @id
  message   String

  @@control(observed)
}
```

可以在合同级别通过在 `prismaContract(path, { defaultControlPolicy })` 上设置 `defaultControlPolicy` 来设置默认控制策略。有关控制策略如何影响 DDL 规划，请参阅 `prisma-next-migrations`。

## 工作流——`@prisma-next/extension-supabase`

概念：Supabase 扩展提供了 `supabase` 合同空间（`auth` / `storage` 模式作为 `external` 表，以及平台角色），以及它自己的基于角色的运行时工厂。它不暴露 `/control` 子路径，因此不能通过用户界面的 `defineConfig({ extensions: [...] })` 伪装进行注册——它通过低级配置中的 `extensions` 进行连接。有关完整的工作模式，请参阅 `examples/supabase`。

`prisma-next.config.ts`（与示例一致）：

```typescript
import supabasePack from '@prisma-next/extension-supabase/pack';
import { defineConfig } from '@prisma-next/cli/config-types';
// ... 其他低级导入

export default defineConfig({
  // ...
  extensions: [supabasePack],
});
```

`db.ts` 不使用标准的 `postgres()` 工厂——Supabase 应用程序使用来自 `@prisma-next/extension-supabase/runtime` 的 `supabase()` 工厂构建客户端（基于角色：`asUser(jwt)` / `asAnon()` / `asServiceRole()`，JWT 验证，RLS）。该运行时——以及 RLS 策略编写（`policy_select` / `@@rls`）——由 **`prisma-next-supabase`** 覆盖；在配置连接之后加载它。

导出子路径：`@prisma-next/extension-supabase/pack`、`@prisma-next/extension-supabase/runtime`、`@prisma-next/extension-supabase/contract`。规范示例：`examples/supabase`。

## 工作流——老系统逆向工程

概念：从现有数据库中拉取合同源并继续。`prisma-next contract infer --db <url>` 读取实时模式并写入 `contract.prisma` 文件。它将停止于此——随后使用 `contract emit`，并在模式匹配已固定哈希时使用 `db sign` 作为单独步骤。

```bash
pnpm prisma-next contract infer --db $DATABASE_URL --output ./src/prisma/contract.prisma
pnpm prisma-next contract emit
```

## 常见陷阱

1. **编辑后忘记重新生成。** `contract.json` 和 `contract.d.ts` 过期；下游类型检查和 `migration plan` 看到旧形状。重新生成，或安装 Vite 插件（`prisma-next-build`）。
2. **编辑已生成的工件。** `contract.json` 和 `contract.d.ts` 被生成；那里的编辑在下次生成时会循环消失。编辑源代码。
3. **TS 构建器工厂/导入路径错误。** `defineContract`、`field`、`model`、`rel` 来自 `@prisma-next/postgres/contract-builder`（或 `@prisma-next/mongo/contract-builder`）。在回调重载之外，可用的字段构造器是 `field.column(...)`、`field.generated(...)`、`field.namedType(...)`。
4. **从用户代码中访问内部包。** 用户编写的文件（`prisma-next.config.ts`、`contract.ts`、`db.ts`、控制客户端）仅从 `@prisma-next/<target>/<subpath>` 和 `@prisma-next/extension-<name>/<subpath>` 导入。来自 `@prisma-next/cli/*`、`@prisma-next/family-*`、`@prisma-next/target-*`、`@prisma-next/adapter-*`、`@prisma-next/driver-*` 或 `@prisma-next/sql-contract-*` 的导入是框架内部的——伪装为你组合它们。如果您的目标缺少您需要的伪装子路径，请参阅 *Prisma Next 尚未实现的功能* 并路由到 `prisma-next-feedback`。规范示例是 `examples/multi-extension-monorepo/app/prisma-next.config.ts` 和 `examples/prisma-next-postgis-demo/prisma-next.config.ts`。
5. **混淆配置 `extensions` 与 TS 构建器的 `extensions`。** 相同的包，两个表面，一个字段名但两个形状：`defineConfig({ extensions: [pgvector] })`（来自 `@prisma-next/extension-<name>/control` 的 *控制* 描述符数组）与 `defineContract({ extensions: { pgvector } })`（来自 `@prisma-next/extension-<name>/pack` 的 *包* 描述符记录）。
6. **重命名字段并期望规划器检测到。** Prisma Next 没有合同内重命名提示；规划器看到破坏性的删除+添加。在 `migration plan` 后手动编辑 `migration.ts`（参见 `prisma-next-migrations`），或使用保留然后删除的两迁移模式。

## Prisma Next 尚未实现的功能

- **合同内重命名提示。** 没有 `@@rename(old: ..., new: ...)` 或类似的。使用 *常见陷阱* #6 中的工作方法。要请求第一类重命名，通过 `prisma-next-feedback` 提交。
- **模型验证。** 没有 `@validates(...)` 声明性表面。在应用程序代码中验证（arktype）。要请求合同中的声明性验证，通过 `prisma-next-feedback` 提交。
- **生命周期回调**（`beforeSave`、`afterCreate` 等）。不受支持。使用中间件（`prisma-next-runtime`）或应用程序代码。要请求生命周期回调，通过 `prisma-next-feedback` 提交。
- **软删除 / `paranoid: true`。** 没有内置软删除列。添加一个可空的 `deletedAt DateTime?` 并在查询中显式过滤（或在中间件中）。要请求内置软删除，通过 `prisma-next-feedback` 提交。
- **作用域 / 默认过滤器。** 没有 ActiveRecord 风格的作用域。自己组合查询帮助程序。要请求作用域，通过 `prisma-next-feedback` 提交。
- **隐式 Prisma-ORM 多对多。** 在双方都没有显式连接模型的情况下拒绝列表导航。显式编写连接模型。要请求隐式 M2M，通过 `prisma-next-feedback` 提交。

## 参考

- 运行 `pnpm prisma-next contract --help` 获取实时命令表面。
- PSL 功能表面和解释器接受的：`packages/2-sql/2-authoring/contract-psl/README.md`。
- TS 构建器表面和回调帮助程序词汇：`packages/2-sql/2-authoring/contract-ts/README.md`。
- 布局（`contract.prisma`、`contract.json`、`contract.d.ts` 和 `migrations/` 的位置）：
  - **应用程序布局**（`src/prisma/...` + `migrations/app/...`）——`examples/prisma-next-demo` 演示的；应用程序使用的规范形状。
  - **合同空间包布局**（`src/contract.{prisma,ts}` 直接，`migrations/<timestamp>_<slug>/` 没有空间 ID 段）——用于扩展和聚合根包，在 `.cursor/rules/contract-space-package-layout.mdc` 和 ADR 212 中记录。

## 检查清单

- [ ] 阅读 `prisma-next.config.ts` 并确定合同源（以 `.prisma` 或 `.ts` 结尾的路径字符串）和安装的 `extensions: [...]`。
- [ ] 所有用户编写的导入都解析到 `@prisma-next/<target>/<subpath>`（例如 `@prisma-next/postgres/config`）或 `@prisma-next/extension-<name>/<subpath>`。用户文件中没有来自 `@prisma-next/cli/*`、`@prisma-next/family-*`、`@prisma-next/target-*`、`@prisma-next/adapter-*`、`@prisma-next/driver-*` 或 `@prisma-next/sql-contract-*` 的导入。
- [ ] 编辑了合同源（`contract.prisma` 或 `contract.ts`），而不是已生成的工件。
- [ ] 对于新的扩展命名空间：添加了包，导入了其控制描述符（`@prisma-next/extension-<name>/control`），在 `defineConfig({...})` 中将其添加到 `extensions: [...]`（如果使用 TS 构建器，则将匹配的包描述符添加到 `defineContract({extensions: {...}})`）。
- [ ] 对于重命名：在 `migration plan` 后手动编辑 `migration.ts`（或使用保留然后删除的两迁移模式）——Prisma Next 目前没有重命名提示。
- [ ] 编辑后运行 `pnpm prisma-next contract emit`（或让 Vite 插件在保存时重新生成）。
- [ ] 确认 `contract.json` 和 `contract.d.ts` 更新后紧邻源代码。
- [ ] 没有手动编辑 `contract.json` / `contract.d.ts`。
- [ ] 没有编造缺失的功能（验证、回调、软删除、作用域、合同内重命名提示）——将用户引导至 *Prisma Next 尚未实现的功能* + `prisma-next-feedback`。
