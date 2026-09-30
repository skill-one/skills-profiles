---
name: experience-ui-bundle-salesforce-data-access
description: 必须在使用 uiBundles/*/src/ 项目的任何 Salesforce 数据时激活——包括构建页面、列表、表格、卡片网格、仪表板或表单，这些页面、列表、表格、卡片网格、仪表板或表单会显示、筛选、计数或编辑任何对象（例如 Property__c、Account、Case）的记录，即使提示名称仅提及 UI 或对象，也从未提及查询、GraphQL 或 SDK。此类组件背后的记录来自 Salesforce，因此请与 experience-ui-bundle-frontend-generate 一起使用：该技能为组件提供样式，而本技能则为其连接数据。此外，在 @salesforce/platform-sdk 导入、sdk.graphql.query / mutate / sdk.fetch 调用、*.graphql 文件或需要强制刷新的过期数据时也会触发。新的读写工作使用当前的 @salesforce/platform-sdk API；仅迁移现有的旧 @salesforce/sdk-data 可调用代码。不适用于纯样式/布局、无记录、应用外壳、文件上传或认证/搜索脚手架的情况。禁止在 OAuth、对象/字段模式更改、批量/工具/元数据 API 或声明式自动化时触发。
---

# Salesforce 数据访问（UI 套件）

UI 套件中的所有 Salesforce 数据访问都通过 **`@salesforce/platform-sdk`** 数据 SDK 进行。该 SDK 处理认证、CSRF 和基础 URL 解析，并且在 WebApp 表面默认缓存每个 GraphQL 查询。

此文件是 **工作流程 + 安全防护骨干**。深度存在于关联文档中：

- **[references/graphiti-cli.md](references/graphiti-cli.md)** — **`graphiti` 命令行工具** (`sf-gql-*` 命令) 将一个小型 JSON 规范编译为符合模式、应用安全防护的查询 + 变量 + 类型。这是编写以下步骤中 GraphQL 的首选方式；当不可用时，会回退到 schema-grep 脚本。
- **[references/sdk-api.md](references/sdk-api.md)** — `query`/`mutate` 调用接口 + 生成的类型放置；行为差异（接口、错误状态、`QueryResult`）基于 **tier-2b**。
- **[references/caching.md](references/caching.md)** — 默认开启的缓存 + 两种刷新模式；行为基于 **tier-2b** `docs/data/`（安装时提供），此处提供完整版本标记的回退。
- **[references/graphql-hand-authoring.md](references/graphql-hand-authoring.md)** — 模式查找、读/写模板、每个平台安全防护 (`@optional`、分页、限制、半连接、包装器、错误表等）。
- **[references/rest-and-integration.md](references/rest-and-integration.md)** — `sdk.fetch`、支持的 API 允许列表和响应式/生命周期集成模式。
- **[references/migration.md](references/migration.md)** — 旧的 `@salesforce/sdk-data` 可调用代码 → 新命名空间。**唯一** 出现已废弃 API 作为可用代码的地方。

## 一段话的心智模型

`const sdk = await createDataSDK()`。然后 `sdk.graphql` 是一个 **命名空间**，而不是函数：**`sdk.graphql!.query({...})`** 用于读操作，**`sdk.graphql!.mutate({...})`** 用于写操作。在 WebApp 上，**每个 `query()` 默认都会被缓存**（300 秒）。HTTP 200 并不意味着成功 — 始终检查 `result.errors`。在查询之前，验证每个实体和字段是否符合模式：一个未验证的字段会导致整个查询在运行时失败，并且 `schema.graphql` 太大无法目视查看 — 请查找它。

```typescript
import { createDataSDK, gql } from "@salesforce/platform-sdk"; // gql 标记查询字符串，以便 codegen + eslint 验证

const sdk = await createDataSDK();
const result = await sdk.graphql!.query({ query: GET_ACCOUNTS, variables });
if (result.errors?.length) throw new Error(result.errors.map((e) => e.message).join("; "));
const rows = result.data?.uiapi?.query?.Account?.edges?.map((e) => e.node) ?? []; // 解包 edges/node；通过 .value 读取字段值
```

类型调用参数（`query<GetAccountsQuery, GetAccountsQueryVariables>`）、`CacheControl` 类型以及 `NodeOfConnection<T>`（从 Connection 中提取节点类型以进行干净的类型化）都位于 [references/sdk-api.md](references/sdk-api.md)。

> **此变更（破坏性 — PR #502）。** 旧的 `sdk.graphql(...)` 形式和旧的包名已**废弃** — 上述代码是唯一正确的形式。如果你在现有代码中遇到旧的 API（或过时的 `dist/` 构件），不要复制它；按照 [Working on existing code](#working-on-existing-code-migration) 进行转换。
>
> **`sdk.graphql!` 仅限 WebApp。** 上述的非空断言仅在套件完全在 WebApp 上运行时才正确。在其他表面上它可能会崩溃 — 在编写前做出决定。参见 **[表面 — `!` vs 安全防护](#surfaces--sdkgraphql-vs-guard)**。

---

## 基于安装的类型锚定 SDK 合约（tier-2a）

`@salesforce/platform-sdk` 强制发布到共享版本线并快速迭代。此技能的文本是一个时间点的快照；**实际拥有的安装声明对版本具有权威性**。在编写任何 `query`/`mutate` 之前，阅读安装的类型并让它们生效：

- `node_modules/@salesforce/platform-sdk/dist/core/data.d.ts` — `query`/`mutate` 签名、`QueryResult`（具有 `subscribe`/`refresh`）与 `MutationResult`（按设计没有，具有 `errors`）、`CacheControl` 联合、默认 TTL。
- `node_modules/@salesforce/platform-sdk/dist/data/index.d.ts` — `createDataSDK`、`gql`、`NodeOfConnection`。

**优先级 — 安装的 `.d.ts` 优先于此技能的文本。** 如果这里的签名、类型或默认值与安装声明不一致，请遵循声明并注意差异；不要“修正”类型以匹配文本。

**锚定阶梯**（一个模型，两个轴）：

| Tier | 锚定 | 回答 | 通过 |
|---|---|---|---|
| tier-1 | GraphQL **模式** | *存在哪些数据* | graphiti / `graphql-search.sh`（前提 #2） |
| tier-2a | SDK **合约** | *如何调用它* | 上述安装的 `.d.ts` |
| tier-2b | SDK **行为** | *如何表现* | 安装的 `docs/data/` 文件夹（下方） |
| 骨干 | 此 SKILL.md | 工作流程 + 安全防护，协调所有三个；当层级无法锚定时作为回退 |

**当 `.d.ts` 缺失时的回退** — 包已安装但未提供声明（陈旧或移除类型的构建构件）。然后使用此技能的文本作为最佳尝试。此回退**不**涵盖缺失的包：如果 `@salesforce/platform-sdk` 未安装，停止并安装它（前提 #1） — 不要针对你没有的依赖项的文本编写调用。

---

## 基于 installed docs 锚定 SDK 行为（tier-2b）

同一包附带一个编写的**行为**指南：`node_modules/@salesforce/platform-sdk/docs/data/`（编号文件，按顺序阅读）。Tier-2a 的 `.d.ts` 修复调用 *合约*；此文件夹是未明确说明合约的行为的权威来源 — 缓存模型、表面 `!`-vs-安全防护决策、错误处理立场、迁移思维。**在选择缓存策略、表面断言或错误立场之前阅读它并让它在优先级上获胜** — 同 tier-2a（安装的源优先于此文本；当存在时它是完整、版本当前的副本）。

**当文件夹缺失时**（旧 SDK 或类型仅构建）：此技能保留一个针对每个行为的薄型回退 — 下方和每个部分中 — 仅够保持你前进；根据它行动。与 tier-2a 类似，缺失的 *包* 不同：如果 `@salesforce/platform-sdk` 未安装，停止并安装它（前提 #1）。

---

## 表面 — `sdk.graphql!` vs 安全防护

`sdk.graphql` / `sdk.fetch` 真正可选（类型为 `graphql?: …`），并且你是否有权用 `!` 断言它们是一个 *运行时崩溃* 决策 — 在编写任何 `query`/`mutate` 之前做出。**回退规则：WebApp 唯一套件 → `sdk.graphql!` 是安全的；任何可能在 WebApp 外运行的套件（Mosaic / OpenAI / MCPApps）→ 首先安全防护 (`if (!sdk.graphql) return …`)，然后调用。** 如果你无法证明 WebApp 唯一，安全防护 — 一个裸的 `!`，稍后会在其他地方提供，会抛出 `Cannot read properties of undefined`，TypeScript 不会捕获它（`sdk.fetch!` 也一样）。

表面矩阵、便携式安全防护片段和完整推理基于 **tier-2b** `docs/data/`（上方回退）；安全防护片段也位于 [references/sdk-api.md](references/sdk-api.md#sdkgraphql-vs-guard)。

---

## 步骤 0 — 路由任务

| 任务是… | 前往 |
|---|---|
| 读取记录 | **[Read workflow](#read-workflow)** 下方 |
| 创建/更新/删除记录 | **[Write workflow](#write-workflow)** 下方 |
| 对象/字段元数据、选择列表值、关联列表元数据、聚合 | **[Beyond record CRUD](#beyond-record-crud)** 下方 |
| 数据已过时 / "添加刷新按钮" / "缓存更长时间" | **[Freshness & caching](#freshness--caching)** 下方 |
| GraphQL 无法表达的内容（Apex REST、文件上传、Einstein） | [references/rest-and-integration.md](references/rest-and-integration.md) |
| 迁移旧的 `sdk.graphql?.(query, vars)` 代码 | **[Working on existing code](#working-on-existing-code-migration)** 下方 |

GraphQL 涵盖的内容远不止记录读和写 — 优先用于 **`uiapi` 命名空间暴露的任何内容**（参见 [Beyond record CRUD](#beyond-record-crud)）。仅在数据确实存在于 `uiapi` 外部时才使用 REST（Apex REST、文件上传、Einstein） — 参见 [references/rest-and-integration.md](references/rest-and-integration.md)。

---

## 前提条件 — 在编写任何查询之前验证

`<skill-dir>` 下方是此技能安装的位置（此 `SKILL.md` 加载的目录）。模式查找脚本随附在其中。脚本不会通过向上遍历来搜索 `schema.graphql` — 祖先模式可能属于不同的组织，并且会针对错误的模式验证字段。明确解析模式：从 SFDX 项目根目录运行（`schema.graphql` 存放的地方），或传递 `--schema <path>` / 设置 `GRAPHQL_SCHEMA=<path>`。脚本会回显它解析的模式 (`[graphql-search] using schema: …` 在 stderr 上) — 快速查看以确认你针对正确的文件进行了锚定。

| # | 要求 | 验证 | 缺失时 |
|---|---|---|---|
| 1 | `@salesforce/platform-sdk` 安装 **且其合约 + 行为文档已阅读** | `package.json` 在 UI 套件目录中列出了它；然后阅读 `dist/core/data.d.ts` + `dist/data/index.d.ts` ([tier-2a](#ground-the-sdk-contract-on-the-installed-types-tier-2a)) **和** `docs/data/` 文件夹 ([tier-2b](#ground-the-sdk-behavior-on-the-installed-docs-tier-2b))，并让它们优先于此技能的文本 | 未安装 → 告知用户安装它；无法继续。安装但 `.d.ts` / `docs/` 缺失（陈旧或类型仅构件）→ 使用文本回退 |
| 2 | 锚定工具解析 | **首选：** 从 UI 套件目录运行 `npx graphiti sf-gql-discover '{"org":"<alias>","mode":"list_objects"}'` 返回对象。**回退：** 从 SFDX 项目根目录运行 `bash <skill-dir>/scripts/graphql-search.sh <Entity>` 打印查找，而不是 "schema.graphql not found" | 没有graphiti依赖项 / 组织无法启动 → 使用脚本。脚本找不到 `schema.graphql` → 传递 `--schema <path>`，或从 UI 套件目录运行 `npm run graphql:schema` ([references/graphiti-cli.md](references/graphiti-cli.md) 涵盖 CLI 设置) |
| 3 | 目标对象/字段已部署 | 对象出现在 `sf-gql-discover`（或 `graphql-search.sh <Entity>` 返回输出） | 实体缺失通常意味着它未部署（或缓存/模式已过时）。刷新：`npx graphiti sf-gql-connect '{"org":"<alias>","forceRefresh":true}'`（CLI）或 `npm run graphql:schema`（脚本）。如果仍然缺失，部署元数据（**platform-metadata-deploy** 技能处理此操作）并分配权限集，然后重新检查 |

如果前提条件未满足，你仍然可以搭建组件、路由和布局 — 但使用空数组 / `null` 作为数据，用 `// TODO: 添加查询后进行模式验证` 标记查询位置，并添加一个返回计划项。**不要** 在模式工作流程完成之前编写 GraphQL 字符串。

---

## 读取工作流程

1. **首先查找模式 — 不要猜测名称。** **首选（graphiti）：** 当确切的 API 名称有任何不确定性时，**先列出再描述** — `npx graphiti sf-gql-discover '{"org":"<alias>","mode":"list_objects","search":"<intent>"}'` 找到真实名称，然后 `npx graphiti sf-gql-discover '{"org":"<alias>","mode":"describe_object","object":"<Entity>"}'` 获取确切的字段/类型名称、选择列表值、可过滤/可排序。空列表或缺失对象是关于组织的**事实**（名称错误或未部署），**不是工具故障** — 重新列出或 `forceRefresh`；**不要** 回退到脚本（见安全防护 2）。**回退** 仅适用于无法运行的 CLI（没有 graphiti 依赖项 / 组织无法启动）：从 SFDX 项目根目录运行 `bash <skill-dir>/scripts/graphql-search.sh <Entity>`。完整规则：[references/graphql-hand-authoring.md](references/graphql-hand-authoring.md)。
2. **编写查询。** **首选 — 用 graphiti 编译它：**
   `npx graphiti sf-gql-list '{"org":"<alias>","object":"<Entity>","fields":[…],"first":N}'` 返回一个 `{ query, variables, types, warnings }` 封装，其中包含 `@optional`、`value`/`displayValue`、`edges/node` 和 `first:`/`pageInfo` **已应用**。确认 `warnings: []`（非空数组表示对象不在预热的模式中 — 查询已降级；不要发布它），然后原封不动地将 `query` 粘贴到内联 `gql`（简单）或外部 `.graphql` 文件（每个文件一个操作，使用捆绑包的 `?raw` 后缀导入 — `import Q from "./q.graphql?raw"` 将文件作为纯字符串导入）。**回退 — 手动编写：** 对每个**可选的 FLS 门控字段**应用 `@optional` — 标量叶字段（`Name @optional { value }`）和父/子关系*以及*它们内部的字段 — 但**不**应用于 `Id`、连接管道（`edges`、`node`、连接字段本身）或 `pageInfo`；graphiti 输出保留这些裸字段，是规范位置。始终设置 `first:`，如果可能则包含 `pageInfo`。无论如何，完整机制和预热与降级行为：[references/graphiti-cli.md](references/graphiti-cli.md)。
3. **生成类型** — `npm run graphql:codegen`（从 UI 套件目录）→
   `src/api/graphql-operations-types.ts`。
4. **调用 `query()`** 使用生成的类型：

   ```typescript
   import type { GetAccountsQuery, GetAccountsQueryVariables } from "../graphql-operations-types";

   const result = await sdk.graphql!.query<GetAccountsQuery, GetAccountsQueryVariables>({
     query: GET_ACCOUNTS,
     variables: { first: 20 },
     // cacheControl,            // 可选 — 参见 Freshness & caching
   });
   ```
5. **处理结果。** `result.data` + `result.errors` 是初始快照；`result.subscribe` / `result.refresh` 是响应式处理。始终在读取 `data` 之前检查 `errors`：

   ```typescript
   if (result.errors?.length) throw new Error(result.errors.map((e) => e.message).join("; "));
   const rows = result.data?.uiapi?.query?.Account?.edges?.map((e) => e.node) ?? [];
   ```

用 `?.`/`??` 保护消费代码（因为 `@optional` 可能会省略字段）。错误处理立场（严格 / 宽容 / 区分）基于 **tier-2b** `docs/data/`（回退：安全防护 #1 — 始终检查 `result.errors`）；`NodeOfConnection` 类型化位于 [references/sdk-api.md](references/sdk-api.md)。

---

## 写入工作流程

1-3 如上（模式查找 → 编写**mutation** → 代码生成）。使用 graphiti 编译 mutation，使用 `sf-gql-create` / `sf-gql-update` / `sf-gql-delete` — 它们发出 `uiapi { <Object>Create(input: $input) { Record {…} } }` 形状；`types` 字段告诉您输入形状。详情：[references/graphiti-cli.md](references/graphiti-cli.md)。
4. **调用 `mutate()`** 注意选项键是 **`mutation`**，而不是 `query`，并且 mutation **永远不会被缓存**。运行时 `variables` 形状因操作而异 — 值是**原始的**（永远不会用 `{value}` 包装；包装器是读形状的东西，会破坏写入）并嵌套在**实体键**下：

   ```typescript
   // 创建 — input.<Entity> 包含新字段值
   variables: { input: { Account: { Name: "Acme", Industry: "Technology" } } }
   // 更新 — 兄弟 Id 与实体键一起
   variables: { input: { Id: "001…", Account: { Industry: "Finance" } } }
   // 删除 — 仅 Id，无实体键（通用 RecordDeleteInput）
   variables: { input: { Id: "001…" } }

   const { data, errors } = await sdk.graphql!.mutate<CreateAccountMutation, CreateAccountMutationVariables>({
     mutation: CREATE_ACCOUNT,
     variables: { input: { Account: { Name: "Acme" } } },
   });
   if (errors?.length) throw new Error(errors.map((e) => e.message).join("; "));
   ```

这是脊柱拥有的**`variables`结构**；CLI `types`-字段的解释在[references/graphiti-cli.md](references/graphiti-cli.md)中，GraphQL文档字段约束（`createable`/`updateable`，`ApiName`引用，`@{alias}`链式调用）在[references/graphql-hand-authoring.md](references/graphql-hand-authoring.md)中。
5. **刷新受影响的读取操作**。`mutate()`没有`refresh`。在写入后更新实时列表，请保留您早期`query()`调用（例如`accountsResult`）的`QueryResult`，然后调用`await accountsResult.refresh()`（强制重新获取，推送给订阅者）——请注意，这是读取的句柄，而不是`mutate()`返回的任何内容。参见**[新鲜度与缓存](#freshness--caching)**。

Mutation语法非常严格：在`uiapi(input: { allOrNone: ... })`下封装，仅`createable`/`updateable`字段，创建/更新输出始终是`Record`，但**删除没有`Record`字段——仅选择`Id`**。完整的模板+链式调用+约束：[references/graphql-hand-authoring.md](references/graphql-hand-authoring.md)。

---

## 超越记录CRUD

`uiapi`命名空间不仅用于记录读取/写入。在转向REST之前，请检查GraphQL是否已经涵盖了它——相同的`sdk.graphql!.query()`调用，不同的子选择。顶层的`uiapi`字段：

| 需求 | 使用 | 返回 |
|---|---|---|
| 查询记录 | `uiapi { query { <Entity>(...) } }` | 记录（[读取工作流](#read-workflow)） |
| 计数/求和/分组汇总，无需拉取行 | `uiapi { aggregate { <Entity>(groupBy: …) } }` | 汇总桶 |
| 对象/字段元数据——标签、数据类型、`createable`/`updateable`、记录类型 | `uiapi { objectInfos(apiNames: […]) }` | `ObjectInfo[]` |
| 挑单值（每个记录类型） | `uiapi { objectInfos(objectInfoInputs: […]) { fields … on PicklistField { … } } }` | 挑单值 |
| 关联列表元数据——父记录关联列表的显示列、排序 | `uiapi { relatedListByName(parentApiName, relatedListName) }` | `RelatedListInfo` |

记录读取规则相同：首先验证每个类型/字段，FLS适用时使用`@optional`，检查`result.errors`。聚合可以与`npx graphiti sf-gql-aggregate`（传递`groupBy` + `aggregations`）编译；对象元数据/挑单/关联列表是手动编写的——模板：[references/graphql-hand-authoring.md](references/graphql-hand-authoring.md)。

> 两个相关功能（**当前用户**记录和**布局**交付）需要在当前组织架构中确认后，此技能才能文档化查询形状——作为后续跟踪，尚未在此涵盖。

---

## 新鲜度与缓存

基于**tier-2b** `docs/data/`构建缓存模型——缓存键机制、缓存内容、`baseUrl`共享细节、未缓存表面语义以及响应式句柄的细微差别都在那里存在（[references/caching.md](references/caching.md)将其重述为版本标记的回退）。**承重回退**（文件夹缺失时足够执行）：

- **WebApp默认开启缓存**——每个`query()`缓存**300秒**；没有选择标志、没有工厂、没有`/cache`子路径。**不要自行构建缓存**（React Query、SWR、`localStorage`、手写的`Map`）。`mutate()`从不缓存。
- **按主机+API版本共享**——来自另一个针对相同主机**和**`apiVersion`的`createDataSDK()`的相同查询+变量的缓存命中=一个网络调用；每个实例的获取管道保持隔离。
- **两个不同的新鲜度工具——不要混淆它们：**
  1. **每次调用的`cacheControl`**（选项包上的单次策略）：“no-cache”（绕过，写回）/**“only-if-cached”**/**`{ type: "max-age", maxAge: <秒> }`**；默认300秒。将其作为可选参数传递给读取函数，并在同一数据层文件中暴露每个策略为**薄的命名导出**（`refreshAccounts` → `"no-cache"`，`offlineAccounts` → `"only-if-cached"`，…）。一个`“only-if-cached”`**未命中**会在`result.errors`上显示`extensions.code === "CACHE_MISS"`——渲染空状态，**不要**回退到网络（那会破坏离线优先）。
  2. **响应式`subscribe` / `refresh`**（`QueryResult`上的实时句柄）：`subscribe(cb)`仅在**后续**快照上触发（始终在拆解时`unsubscribe`）；`refresh()`重新获取，绕过缓存，推送给订阅者——在`mutate()`后使用它（`mutate()`没有`refresh`）。多订阅者分叉/独立性基于**tier-2b** `docs/data/`。

---

## 在现有代码上工作（迁移）

**只有当现有代码实际使用旧API时才进入此路径**——即它导入`@salesforce/sdk-data`或调用`sdk.graphql(query, vars)`形式。对于任何新的读取/写入，完全忽略迁移，使用[读取工作流](#read-workflow) / [写入工作流](#write-workflow)——那些已经显示了**唯一**正确的API。

当你确实有旧代码需要转换时，请参阅**[references/migration.md](references/migration.md)**中的前后差异（导入、查询/突变调用、可选链→非空断言、代码生成类型放置）和检查清单。目标API与上述读取/写入工作流完全相同——迁移只是用那个替换旧形式。

---

## 平台约束——永远不要倒退

这些是Salesforce GraphQL平台行为，独立于SDK。违反会导致静默运行时失败。（详细信息+模板：[references/graphql-hand-authoring.md](references/graphql-hand-authoring.md)。）

1. **HTTP 200 ≠ 成功**——始终解析`result.errors`；即使失败，Promise也会解决。
2. **架构是唯一的事实来源——验证，永不凭空创造。** 在使用前，通过graphiti `sf-gql-discover`（首选）或`bash <skill-dir>/scripts/graphql-search.sh <Entity>`验证每个实体/字段/类型。区分大小写；`__c`/`__e`；`_Record`实体后缀（v60+）。当graphiti准备就绪时，一个“未找到”/空/`Cannot query field`的答案（包括来自`graphql-codegen`/`@graphql-eslint`的答案，即使消息指向`schema.graphql`）是关于组织的**事实**——名称错误或元数据未部署/无法访问，而不是工具故障：修复操作，或部署元数据（**平台元数据部署**技能）+分配权限+刷新（`sf-gql-connect --forceRefresh` / `npm run graphql:schema`）。不要回退到脚本，围绕它手写，或**猜测名称**——猜测的实体或字段在运行时会导致整个查询失败；如果查找未收敛，**请询问用户，而不是继续螺旋式下降**。**`schema.graphql`和代码生成输出（`src/api/graphql-operations-types.ts`）是只读生成的镜像——不要打开或编辑它们**（尊重任何`# DO NOT EDIT`标记）。手动添加缺失的类型可以满足代码生成/检查，但不会授予组织访问权限；它只是隐藏了故障，直到运行时。只有在CLI完全无法运行时（没有依赖项 / `SCHEMA_PRIME_FAILED`）才回退到脚本。
3. **每个FLS门控字段在每个嵌套级别上使用`@optional`**——标量叶字段加上每个父级/子级关系*以及它里面的字段（否则FLS会失败整个查询，v65+）。**不要**装饰`Id`、连接管道（`edges`、`node`、连接字段）或`pageInfo`——这些不是FLS门控的，graphiti输出将它们保留为裸的。使用`?.`/`??`。放置规则：[references/graphql-hand-authoring.md](references/graphql-hand-authoring.md)。
4. **突变**在`uiapi(input: { allOrNone: ... })`下封装；显式设置`allOrNone`；输出不包括子级/导航引用字段；输出字段确实是`Record`（与规则2中的`_Record`实体后缀无关）——删除→仅`Id`。GA v66+。
5. **显式分页**——始终设置`first:`，因为服务器会静默限制为10，否则您会丢失行而没有错误；向前（`first`/`after`，没有`last`/`before`）；`upperBound`（v59+）提高对大型集合的请求上限（设置时，`first`必须为200–2000）。
6. **SOQL治理限制适用**——`uiapi`查询编译为SOQL，因此继承相同的治理限制：≤10子查询，≤5子级→父级级别，≤1父级→子级级别，≤2,000记录/子查询。如果超出限制，请拆分为多个请求。
7. **字段值包装器**——通过`.value`读取原始值；`displayValue`是服务器格式化的字符串，用于UI。当字段既显示*又*操作时（货币、日期、挑单），选择**两者**`value`和`displayValue`，这样您就不会在客户端重新格式化。仅显示字段可以仅使用`displayValue`。
8. **复合字段**——按构成部分（`BillingCity`）过滤/排序，而不是包装器（`BillingAddress`）。
9. **仅支持API**——GraphQL（`uiapi`）、UI API REST、Apex REST、Connect REST、Einstein LLM通过`sdk.fetch`。**不**：企业SOQL `/query`、Aura启用的Apex、Chatter（使用`uiapi.currentUser`）。参见[references/rest-and-integration.md](references/rest-and-integration.md)。

> 一个SDK约定存在于工作流中，而不是此列表（它不是平台行为）：始终运行`npm run graphql:codegen`并在编写操作后使用生成的类型（[读取工作流](#read-workflow)步骤3）。也位于[预飞行检查清单](#pre-flight-checklist)。

>
> **graphiti会为你应用大部分这些规则。** 当你使用`sf-gql-*`针对已准备好的架构编译查询时，规则3（`@optional`）、4（突变`Record` *输出* 封装和实体键输入——**不是** `allOrNone`，你仍然需要自己添加）、5（`first:`/`pageInfo`）、7（`value`/`displayValue`包装器）都会自动满足——这就是为什么你**直接粘贴`query`**而不是重新派生的原因。规则1（检查`result.errors`）、6（治理限制）、8（复合字段）、9（支持的API）仍然由你负责。并且自动化仅在对象准备就绪时才会触发：一个非空的`warnings`数组意味着它没有准备好，发出的查询是**降级的**（裸字段，没有约束）——参见[references/graphiti-cli.md](references/graphiti-cli.md#primed-vs-degraded--why-the-guardrails-sometimes-vanish)。

---

## 命令与布局

```text
<skill-dir>/                            ← 无论此技能安装在哪里
└── scripts/graphql-search.sh           ← 架构查找（随技能一起提供）

<project-root>/                         ← SFDX项目根；从这里运行脚本
├── schema.graphql                      ← 生成的镜像；grep目标（永远不要打开或编辑；脚本读取./schema.graphql）
└── force-app/main/default/uiBundles/<app>/   ← UI包目录
    ├── package.json                    ← npm脚本
    └── src/api/                        ← 查询、生成的类型、SDK调用
```

| 命令 | 从哪里运行 | 目的 |
|---|---|---|
| `npx graphiti sf-gql-discover '{…}'` | UI包目录 | 针对实时组织发现对象/字段（首选基础） |
| `npx graphiti sf-gql-<list\|detail\|aggregate\|create\|update\|delete\|raw> '{…}'` | UI包目录 | 编译应用了约束的查询/突变（[references/graphiti-cli.md](references/graphiti-cli.md)） |
| `npx graphiti sf-gql-connect '{"org":"<alias>","forceRefresh":true}'` | UI包目录 | 部署后刷新graphiti的架构缓存 |
| `bash <skill-dir>/scripts/graphql-search.sh <Entity>` | 项目根（或传递`--schema <路径>`；无树向上遍历） | 架构查找回退（本地`schema.graphql`上grep） |
| `npm run graphql:schema` | UI包目录 | 获取/刷新`schema.graphql`（用于回退脚本） |
| `npm run graphql:codegen` | UI包目录 | 生成操作类型 |
| `npx eslint <file>` | UI包目录 | 检查（捕获`gql`架构违规） |

## 预飞行检查清单

- [ ] 表面确定：`sdk.graphql!`仅当WebApp专用；否则用`if (!sdk.graphql) …`保护（[表面](#surfaces--sdkgraphql-vs-guard)）
- [ ] SDK合同基于安装的`dist/*.d.ts`（类型胜过文本）([tier-2a](#ground-the-sdk-contract-on-the-installed-types-tier-2a))
- [ ] SDK行为基于安装的`docs/data/`（文档胜过文本；如果缺失则回退）([tier-2b](#ground-the-sdk-behavior-on-the-installed-docs-tier-2b))
- [ ] 每个字段/实体验证——`sf-gql-discover`（首选）或`graphql-search.sh`（回退，针对正确的架构）
- [ ] 如果用graphiti编译：`warnings: []`确认（非空=降级查询，不要发布）；`query`直接粘贴
- [ ] FLS门控字段+关系上的`@optional`（不是`Id`/`edges`/`node`/`pageInfo`）；`?.`/`??`在消费代码中
- [ ] 在读取`result.data`之前检查`result.errors`
- [ ] 考虑缓存：默认300秒OK，或`cacheControl` / `refresh`有意选择
- [ ] 运行`npm run graphql:codegen`；使用生成的类型；`npx eslint`通过
