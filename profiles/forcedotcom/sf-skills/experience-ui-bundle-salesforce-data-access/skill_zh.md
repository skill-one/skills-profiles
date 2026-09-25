# Salesforce 数据访问 (UI bundles)

所有 UI bundle 中的 Salesforce 数据访问都通过 **`@salesforce/platform-sdk`**
数据 SDK 进行。该 SDK 处理认证、CSRF 和基础 URL 解析，并且在 WebApp 表面 — 默认缓存每个 GraphQL 查询。

此文件是 **工作流 + 安全约束骨干**。深度存在于链接文档中：

- **[references/graphiti-cli.md](references/graphiti-cli.md)** — **`graphiti` CLI** (`sf-gql-*`
  命令) 将一个小 JSON 规范编译成一个符合模式、应用了安全约束的查询 + 变量 + 类型。编写以下步骤中的 GraphQL 的首选方式；当不可用时，回退到 schema-grep 脚本。
- **[references/sdk-api.md](references/sdk-api.md)** — `query`/`mutate` 调用表面 + 生成的类型放置；行为差异 (表面、错误立场、`QueryResult`) 基于 **tier-2b**。
- **[references/caching.md](references/caching.md)** — 默认开启的缓存 + 两种刷新模式；行为基于 **tier-2b** `docs/data/`（安装时），此处为完整版本标记的回退。
- **[references/graphql-hand-authoring.md](references/graphql-hand-authoring.md)** — 模式查找、读取 / 变更模板、每个平台安全约束 (`@optional`、分页、限制、半连接、包装器、错误表…).
- **[references/rest-and-integration.md](references/rest-and-integration.md)** — `sdk.fetch`、支持的 API 允许列表，以及响应式/生命周期集成模式。
- **[references/migration.md](references/migration.md)** — 旧的 `@salesforce/sdk-data` 可调用代码 → 新命名空间。**唯一** 的死 API 出现在此处作为可用代码。

## 单段心智模型

`const sdk = await createDataSDK()`. 然后 `sdk.graphql` 是一个 **命名空间**，而不是函数：**`sdk.graphql!.query({...})`** 用于读取，**`sdk.graphql!.mutate({...})`** 用于写入。在 WebApp 上，**每个 `query()` 默认缓存**（300s）。HTTP 200 从不意味着成功 — 始终检查 `result.errors`。在查询之前验证每个实体和字段是否符合模式：一个未验证的字段会在运行时导致整个查询失败，并且 `schema.graphql` 太大无法目测 — 查找它。

```typescript
import { createDataSDK, gql } from "@salesforce/platform-sdk"; // gql 标记查询字符串，以便代码生成 + eslint 验证

const sdk = await createDataSDK();
const result = await sdk.graphql!.query({ query: GET_ACCOUNTS, variables });
if (result.errors?.length) throw new Error(result.errors.map((e) => e.message).join("; "));
const rows = result.data?.uiapi?.query?.Account?.edges?.map((e) => e.node) ?? []; // 解包 edges/node；通过 .value 读取字段值
```

类型调用参数 (`query<GetAccountsQuery, GetAccountsQueryVariables>`), `CacheControl`
类型，以及 `NodeOfConnection<T>`（从连接中提取节点类型以进行干净类型化）都存在于 [references/sdk-api.md](references/sdk-api.md)。

> **此更改（破坏性 — PR #502）。** 以前的可调用 `sdk.graphql(...)` 形式和以前的包名已**过时** — 上述代码是唯一正确的形式。如果您在现有代码中遇到旧 API（或过时的 `dist/` 构件），请不要复制它；按照
> [Working on existing code](#working-on-existing-code-migration) 进行转换。
>
> **`sdk.graphql!` 仅限 WebApp。** 上述的非空断言仅在 bundle 仅在 WebApp 上运行时才正确。在其他表面上它可能会崩溃 — 在编写之前决定。见 **[Surfaces](#surfaces--sdkgraphql-vs-guard)** 下面。

---

## 在安装的类型上锚定 SDK 合约 (tier-2a)

`@salesforce/platform-sdk` 强制发布到一个共享的版本线上，并且移动很快。此 SKILL 的文本是某个时间点的快照；**安装的声明对于您实际拥有的版本具有权威性**。在编写任何 `query`/`mutate` 之前，阅读安装的类型并让它们获胜：

- `node_modules/@salesforce/platform-sdk/dist/core/data.d.ts` — `query`/`mutate`
  签名，`QueryResult`（有 `subscribe`/`refresh`）与 `MutationResult`（按设计没有，`CacheControl` 联合，默认 TTL）。
- `node_modules/@salesforce/platform-sdk/dist/data/index.d.ts` — `createDataSDK`,
  `gql`, `NodeOfConnection`.

**优先级 — 安装的 `.d.ts` 胜过此 SKILL 的文本。** 如果这里的签名、类型或默认值与安装的声明不一致，请遵循声明并注意差异；不要“纠正”类型以匹配文本。

**锚定阶梯**（一个模型，两个轴）：

| Tier | 锚定 | 回答 | 通过 |
|---|---|---|---|
| tier-1 | GraphQL **模式** | *存在哪些数据* | graphiti / `graphql-search.sh`（前提 #2） |
| tier-2a | SDK **合约** | *如何调用它* | 上面安装的 `.d.ts` |
| tier-2b | SDK **行为** | *它如何表现* | 安装的 `docs/data/` 文件夹（下面） |
| 骨干 | 此 SKILL.md | 工作流 + 安全约束，编排所有三个；当 tier 无法锚定时回退 | |

**当 `.d.ts` 缺失时的回退** — 包已安装但未提供声明（过时或类型剥离的构建构件）。然后使用此 SKILL 的文本作为最佳尝试。此回退**不**涵盖缺失的包：如果 `@salesforce/platform-sdk` 未安装，请停止并安装它（前提 #1） — 不要从文本对您没有的依赖项编写调用。([references/graphiti-cli.md](references/graphiti-cli.md) 涵盖 CLI 设置) |

---

## 在安装的文档上锚定 SDK 行为 (tier-2b)

相同的包在其类型旁边提供了一个编写的**行为**指南：`node_modules/@salesforce/platform-sdk/docs/data/`（编号文件，按顺序阅读）。Tier-2a 的 `.d.ts` 修复调用合约；此文件夹是未在合约中说明的*行为*的权威来源 — 缓存模型、表面 `!`-vs-安全决策、错误处理立场、迁移心态。**在选择缓存策略、表面断言或错误立场之前阅读它，并让它获胜** — 同 tier-2a（安装的源胜过文本；当存在时，它是完整版本标记的副本）。

**当文件夹缺失时回退**（旧 SDK，或类型仅构建）：此 SKILL 保留一个针对每个行为的薄回退 — 以下和每个部分中 — 仅够保持您继续前进；采取行动。与 tier-2a 一样，缺失的*包*是不同的：如果 `@salesforce/platform-sdk` 未安装，请停止并安装它（前提 #1）。 |

---

## 表面 — `sdk.graphql!` vs 安全约束

`sdk.graphql` / `sdk.fetch` 是真正可选的（类型为 `graphql?: …`），并且您是否可以带 `!` 断言它们是一个*运行时崩溃*决策 — 在编写任何 `query`/`mutate` 之前做出。**回退规则：WebApp 仅 bundle → `sdk.graphql!` 是安全的；任何可能在 WebApp 之外运行的 bundle（Mosaic / OpenAI / MCPApps）→ 首先使用安全约束 (`if (!sdk.graphql) return …`)，然后调用。** 如果您无法证明仅限 WebApp，则使用安全约束 — 一个裸的 `!`，稍后将在其他地方提供，会引发 `Cannot read properties of undefined`，TypeScript 不会捕获它（`sdk.fetch!` 也一样）。 |

表面矩阵、可移植安全约束片段，以及完整推理基于 **tier-2b**
`docs/data/`（回退在上面）；安全约束片段也存在于
[references/sdk-api.md](references/sdk-api.md#sdkgraphql-vs-guard)。 |

---

## 步骤 0 — 路由任务

| 任务是… | 前往 |
|---|---|
| 读取记录 | **[Read workflow](#read-workflow)** 下面 |
| 创建 / 更新 / 删除记录 | **[Write workflow](#write-workflow)** 下面 |
| 对象/字段元数据、选择列表值、关联列表元数据、聚合 | **[Beyond record CRUD](#beyond-record-crud)** 下面 |
| 数据已过时 / “添加刷新按钮” / “缓存更长时间” | **[Freshness & caching](#freshness--caching)** 下面 |
| GraphQL 无法表达的东西（Apex REST、文件上传、Einstein） | [references/rest-and-integration.md](references/rest-and-integration.md) |
| 迁移旧的 `sdk.graphql?.(query, vars)` 代码 | **[Working on existing code](#working-on-existing-code-migration)** 下面 |

GraphQL 涵盖的范围远不止记录读取和写入 — 优先为**任何 `uiapi`
命名空间暴露的内容**编写（见 [Beyond record CRUD](#beyond-record-crud)）。仅在数据确实存在于 `uiapi` 之外时才使用 REST（Apex REST、文件上传、Einstein） — 见
[references/rest-and-integration.md](references/rest-and-integration.md)。 |

---

## 前提条件 — 在编写任何查询之前进行验证

`<skill-dir>` 下面是此技能安装的位置（此 `SKILL.md` 加载的目录）。模式查找脚本包含在其中。脚本不会通过向上遍历树来搜索 `schema.graphql` — 一个祖先模式可能属于不同的组织，并且会针对错误的模式验证字段。明确解析模式：从 SFDX 项目根目录运行（`schema.graphql` 存放的地方），或者传递 `--schema <path>` / 设置 `GRAPHQL_SCHEMA=<path>`。脚本会回显它解析的模式 (`[graphql-search] using schema: …` 在 stderr 上) — 快速查看以确认您针对正确的文件进行了锚定。 |

| # | 要求 | 验证 | 如果缺失 |
|---|---|---|---|
| 1 | `@salesforce/platform-sdk` 安装**并且其合约 + 行为文档已阅读** | `UI bundle dir` 中的 `package.json` 列出它；然后阅读 `dist/core/data.d.ts` + `dist/data/index.d.ts` ([tier-2a](#ground-the-sdk-contract-on-the-installed-types-tier-2a)) **和** `docs/data/` 文件夹 ([tier-2b](#ground-the-sdk-behavior-on-the-installed-docs-tier-2b))，并让它们胜过此 SKILL 的文本 | 未安装 → 告知用户安装它；无法继续。已安装但 `.d.ts` / `docs/` 缺失（过时或类型剥离的构建构件）→ 使用文本回退 |
| 2 | 一个锚定工具解析 | **首选：** 从 UI bundle 目录运行 `npx graphiti sf-gql-discover '{"org":"<alias>","mode":"list_objects"}'` 返回对象。**回退：** 从项目根目录运行 `bash <skill-dir>/scripts/graphql-search.sh <Entity>` 打印查找，而不是 "schema.graphql not found" | 没有图iti 依赖项 / 组织无法启动 → 使用脚本。脚本无法找到 `schema.graphql` → 传递 `--schema <path>`，或者从 UI bundle 目录运行 `npm run graphql:schema`。([references/graphiti-cli.md](references/graphiti-cli.md) 涵盖 CLI 设置) |
| 3 | 目标对象/字段已部署 | 对象出现在 `sf-gql-discover`（或 `graphql-search.sh <Entity>` 返回输出） | 实体缺失通常意味着它没有被部署（或者缓存/模式已过时）。刷新：`npx graphiti sf-gql-connect '{"org":"<alias>","forceRefresh":true}'`（CLI）或 `npm run graphql:schema`（脚本）。如果仍然缺失，请部署元数据（**platform-metadata-deploy** 技能处理此操作），然后分配权限集，然后重新检查 |

如果前提条件未满足，您仍然可以构建组件、路由和布局 — 但使用空数组 / `null` 作为数据，用 `// TODO: after schema verification add query` 标记查询位置，并添加一个计划项以返回。**不要**在模式工作流完成之前编写 GraphQL 字符串。
