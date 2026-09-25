# Salesforce 数据访问

## 数据 SDK 要求

> **所有 Salesforce 数据访问必须使用 Data SDK** (`@salesforce/sdk-data`)。SDK 处理身份验证、CSRF 和基础 URL 解析。

```typescript
import { createDataSDK, gql } from "@salesforce/sdk-data";
import type { ResponseTypeQuery } from "../graphql-operations-types";

const sdk = await createDataSDK();

// GraphQL 用于记录查询/变更（首选）
const response = await sdk.graphql?.<ResponseTypeQuery>(query, variables);

// REST 用于 Connect REST、Apex REST、UI API（当 GraphQL 不足时）
const res = await sdk.fetch?.("/services/apexrest/my-resource");
```

**始终使用可选链** (`sdk.graphql?.()`, `sdk.fetch?.()`) — 这些方法在某些表面上可能未定义。

## 前置条件 — 开始前验证

| # | 要求 | 验证方法 | 缺失时 |
|---|-------------|---------------|------------|
| 1 | 安装 `@salesforce/sdk-data` | 检查 UI 包含目录中的 `package.json` | 无法继续 — 告知用户安装它 |
| 2 | 项目根目录存在 `schema.graphql` | 检查文件是否存在 | 从 UI 包含目录运行 `npm run graphql:schema` |
| 3 | 自定义对象/字段已部署 | 运行 `graphql-search.sh <Entity>` — 无输出表示未部署 | 要求用户部署元数据并分配权限集 |

**如果前置条件未满足**，您可以构建组件、路由、布局和 UI 逻辑，但使用空数组 / `null` 作为数据，并用 `// TODO: schema 验证后添加查询` 标记查询位置，并将其包含在计划中返回，解决要求并编写 GraphQL。在 schema 工作流程完成之前，不要编写 GraphQL 查询字符串。

## 支持的 API

**仅允许以下 API。** 列表之外的任何端点都不得使用。

| API | 方法 | 端点 / 用例 |
|-----|--------|----------------------|
| GraphQL | `sdk.graphql` | 所有记录查询和变更通过 `uiapi { }` 命名空间 |
| UI API REST | `sdk.fetch` | `/services/data/v{ver}/ui-api/records/{id}` — 当 GraphQL 不足时记录元数据 |
| Apex REST | `sdk.fetch` | `/services/apexrest/{resource}` — 自定义服务器端逻辑、聚合、多步事务 |
| Connect REST | `sdk.fetch` | `/services/data/v{ver}/connect/file/upload/config` — 文件上传配置 |
| Einstein LLM | `sdk.fetch` | `/services/data/v{ver}/einstein/llm/prompt/generations` — AI 文本生成 |

**不支持:**

- **企业 REST 查询端点** (`/services/data/v*/query` 使用 SOQL) — 在代理级别被阻止。使用 GraphQL 进行记录读取；如果需要服务器端 SOQL 聚合，请使用 Apex REST。
- **Aura 启用的 Apex** (`@AuraEnabled`) — 一种没有从 React UI 包含中调用的 LWC/Aura 模式。
- **Chatter API** (`/chatter/users/me`) — 在 GraphQL 查询中使用 `uiapi { currentUser { ... } }` 代替。
- **任何其他未在上述支持表中列出的 Salesforce REST 端点**。

## 决策：GraphQL 与 REST

| 需求 | 方法 | 示例 |
|------|--------|---------|
| 查询/变更记录 | `sdk.graphql` | Account, Contact, 自定义对象 |
| 当前用户信息 | `sdk.graphql` | `uiapi { currentUser { Id Name { value } } }` |
| UI API 记录元数据 | `sdk.fetch` | `/ui-api/records/{id}` |
| Connect REST | `sdk.fetch` | `/connect/file/upload/config` |
| Apex REST | `sdk.fetch` | `/services/apexrest/auth/login` |
| Einstein LLM | `sdk.fetch` | `/einstein/llm/prompt/generations` |

**首选 GraphQL 用于记录操作。** 仅当 GraphQL 无法覆盖用例时才使用 REST。

---

## GraphQL 不可协商规则

这些规则的存在是因为 Salesforce GraphQL 具有特定于平台的特性，与标准 GraphQL 不同。违反规则会导致静默运行时错误。

1. **HTTP 200 不表示成功** — Salesforce 即使操作失败也会返回 HTTP 200。**始终解析响应正文中的 `errors` 数组。**

2. **模式是单一事实来源** — 在查询中使用实体名称、字段名称和类型之前，必须通过模式搜索脚本进行确认。不要猜测 — Salesforce 字段名称区分大小写，关系可能是多态的，自定义对象使用后缀 (`__c`, `__e`)。v60+ 中添加到 UI API 的对象可能使用 `_Record` 后缀（例如，`FeedItem_Record` 而不是 `FeedItem`）。

3. **所有记录字段上的 `@optional`**（读取查询）— Salesforce 字段级安全 (FLS) 会导致查询因用户缺乏对任何字段的访问权限而完全失败。`@optional` 指令（v65+）告诉服务器省略无法访问的字段而不是失败。将其应用于每个标量字段、父关系和子关系。消费代码必须使用可选链 (`?.`) 和空值合并 (`??`)。

4. **正确的变更语法** — 变更在 `uiapi(input: { allOrNone: true/false })` 下包装，而不是裸 `uiapi { ... }`。始终显式设置 `allOrNone`。输出字段不能包含子关系或导航引用字段。

5. **显式分页** — 在每个查询中始终包含 `first:`。如果省略，服务器将静默默认为 10 条记录。对于可能需要分页的任何查询，包含 `pageInfo { hasNextPage endCursor }`。仅向前分页 (`first`/`after`) — `last`/`before` 不支持。

6. **SOQL 衍生的执行限制** — 每个请求最多 10 个子查询，最多 5 级子到父遍历，最多 1 级父到子（没有孙辈），每个子查询最多 2,000 条记录。如果查询会超出这些限制，请将其拆分为多个请求。

7. **仅请求的字段** — 仅生成用户明确请求的字段。**不要**添加额外字段。

8. **复合字段** — 在过滤或排序时，使用组成字段（例如，`BillingCity`, `BillingCountry`），而不是复合包装器（`BillingAddress`）。复合包装器仅用于选择。

---

## GraphQL 工作流

| 步骤 | 操作 | 关键输出 |
|------|--------|------------|
| 1 | 获取模式 | `schema.graphql` 存在 |
| 2 | 查找实体 | 字段名称、类型、关系确认 |
| 3 | 生成查询 | `.graphql` 文件或内联 `gql` 标签 |
| 4 | 生成类型 | `graphql-operations-types.ts` |
| 5 | 验证 | Lint + 代码生成通过 |

### 步骤 1：获取模式

`schema.graphql` 文件（265K+ 行）是事实来源。**永远不要直接打开或解析它** — 没有cat、less、head、tail、编辑器或程序化解析器。

验证前置条件 1–3（见 [前置条件](#preconditions--verify-before-starting)），然后继续步骤 2。

### 步骤 2：查找实体模式

将用户意图映射到 PascalCase 名称（"accounts" → `Account`），然后从 `sfdx-project` 文件夹（项目根目录）**运行搜索脚本**：

```bash
bash scripts/graphql-search.sh Account
# 多个实体：
bash scripts/graphql-search.sh Account Contact Opportunity
```

脚本为每个实体输出七个部分：
1. **类型定义** — 所有可查询字段和关系
2. **过滤选项** — 可用于 `where:` 条件的字段
3. **排序选项** — 可用于 `orderBy:` 的字段
4. **创建变更包装器** — `<Entity>CreateInput`
5. **创建变更字段** — `<Entity>CreateRepresentation`（创建变更接受的字段）
6. **更新变更包装器** — `<Entity>UpdateInput`
7. **更新变更字段** — `<Entity>UpdateRepresentation`（更新变更接受的字段）

**最多 2 次脚本运行。** 如果实体仍然无法找到，请询问用户 — 对象可能未部署。

#### 实体识别

如果候选实体不匹配：
- 尝试 `__c` 后缀（自定义对象）、`__e` 后缀（平台事件）
- 尝试 `_Record` 后缀 — v60+ 中添加的对象可能使用 `<EntityName>_Record`
- 如果仍然无法解决，**请询问用户** — 不要猜测

#### 迭代内省（最多 3 个周期）

1. **内省** — 运行脚本以解决每个未解决的实体
2. **字段** — 从类型定义中提取请求的字段名称和类型
3. **引用** — 识别引用字段。如果多态（多个类型），请使用内联片段。将新发现的实体类型添加到工作列表。
4. **子关系** — 识别连接类型。将子实体类型添加到工作列表。
5. **如果未解决的实体仍然存在（最多 3 个周期），请重复**

**硬停止：** 如果某个实体未返回数据，请停止 — 它可能未部署。如果 3 个周期后仍有未知实体，请询问用户。不要生成包含未确认实体或字段的查询。

### 步骤 3：生成查询

每个字段名称**必须**在步骤 2 的脚本输出中验证。

#### 读取查询模板

```graphql
query QueryName($after: String) {
  uiapi {
    query {
      EntityName(
        first: 10
        after: $after
        where: { ... }
        orderBy: { ... }
      ) {
        edges {
          node {
            Id
            FieldName @optional { value }
            # 父关系（非多态）
            Owner @optional { Name { value } }
            # 父关系（多态 — 使用片段）
            What @optional {
              ...WhatAccount
              ...WhatOpportunity
            }
            # 子关系 — 最多 1 级，没有孙辈
            Contacts @optional(first: 10) {
              edges { node { Name @optional { value } } }
            }
          }
        }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
}

fragment WhatAccount on Account {
  Id
  Name @optional { value }
}
fragment WhatOpportunity on Opportunity {
  Id
  Name @optional { value }
}
```

**消费代码必须防御缺失字段：**

```typescript
const name = node.Name?.value ?? "";
const relatedName = node.Owner?.Name?.value ?? "N/A";
```

#### 过滤

```graphql
# 隐式 AND
Account(where: { Industry: { eq: "Technology" }, AnnualRevenue: { gt: 1000000 } })

# 显式 OR
Account(where: { OR: [{ Industry: { eq: "Technology" } }, { Industry: { eq: "Finance" } }] })

# NOT
Account(where: { NOT: { Industry: { eq: "Technology" } } })

# 日期字面量
Opportunity(where: { CloseDate: { eq: { value: "2024-12-31" } } })

# 相对日期
Opportunity(where: { CloseDate: { gte: { literal: TODAY } } })

# 关系过滤（嵌套对象，非点表示法）
Contact(where: { Account: { Name: { like: "Acme%" } } })

# 多态关系过滤
Account(where: { Owner: { User: { Username: { like: "admin%" } } } })
```

字符串相等 (`eq`) 不区分大小写。15 字符和 18 字符的记录 ID 都被接受。

#### 排序

```graphql
Account(
  first: 10,
  orderBy: { Name: { order: ASC }, CreatedDate: { order: DESC } }
) { ... }
```

不支持用于排序：多选 picklist、富文本、长文本区域、加密字段。添加 `Id` 作为确定性排序的破折号。

#### 上限分页（v59+）

对于每页 >200 条记录或总计 >4,000 条记录，请使用 `upperBound`。设置 `first` 时必须为 200–2000。

```graphql
Account(first: 2000, after: $cursor, upperBound: 10000) {
  edges { node { Id Name @optional { value } } }
  pageInfo { hasNextPage endCursor }
}
```

#### 半连接和反连接

使用父实体的 `Id` 过滤父实体，基于子实体上的条件使用 `inq`（半连接）或 `ninq`（反连接）在父实体的 `Id` 上。如果唯一条件是子存在性，请使用 `Id: { ne: null }`。

```graphql
query SemiJoinExample {
  uiapi {
    query {
      Account(where: {
        Id: {
          inq: {
            Contact: { LastName: { like: "Smith%" } }
            ApiName: "AccountId"
          }
        }
      }, first: 10) {
        edges { node { Id Name @optional { value } } }
      }
    }
  }
}
```

将 `inq` 替换为 `ninq` 用于反连接。限制：子查询中无 `OR`，子查询中无嵌套连接。

#### 当前用户

使用 `uiapi.currentUser`（无参数）而不是标准查询模式：

```graphql
query CurrentUser {
  uiapi { currentUser { Id Name { value } } }
}
```

#### 字段值包装器

模式字段使用类型包装器 — 通过 `.value` 访问：

| 包装器类型 | 底层 | 包装器类型 | 底层 |
|---|---|---|---|
| `StringValue` | `String` | `BooleanValue` | `Boolean` |
| `IntValue` | `Int` | `DoubleValue` | `Double` |
| `CurrencyValue` | `Currency` | `PercentValue` | `Percent` |
| `DateTimeValue` | `DateTime` | `DateValue` | `Date` |
| `PicklistValue` | `Picklist` | `LongValue` | `Long` |
| `IDValue` | `ID` | `TextAreaValue` | `TextArea` |
| `EmailValue` | `Email` | `PhoneNumberValue` | `PhoneNumber` |
| `UrlValue` | `Url` | | |

所有包装器还暴露 `displayValue: String`（通过 `toLabel()`/`format()` 服务器渲染）— 用于 UI 显示而不是客户端格式化。

#### 变更模板

变更在 API v66+ 中正式发布。三种操作：**创建**、**更新**、**删除**。

```graphql
# 创建
mutation CreateAccount($input: AccountCreateInput!) {
  uiapi(input: { allOrNone: true }) {
    AccountCreate(input: $input) {
      Record { Id Name { value } }
    }
  }
}

# 更新 — 必须包含 Id
mutation UpdateAccount {
  uiapi(input: { allOrNone: true }) {
    AccountUpdate(input: { Id: "001xx000003GYkZAAW", Account: { Name: "New Name" } }) {
      Record { Id Name { value } }
    }
  }
}
```

**输入约束：**
- **创建**：必需字段（除非 `defaultedOnCreate`）、仅 `createable` 字段、无子关系。引用字段通过 `ApiName` 设置（例如，`AccountId`）。
- **更新**：必须包含 `Id`、仅 `updateable` 字段、无子关系。
- **删除**：`Id` 仅。
- **`IdOrRef` 类型**：更新和删除输入中的 `Id` 字段使用 `IdOrRef` 类型，它接受字面记录 ID（例如，`"001xx..."`）或变更链接引用（`"@{Alias}"`）。创建输入中的引用字段（例如，`AccountId`）也接受 `@{Alias}` 用于链接。
- **原始值**：无逗号、货币符号或区域格式化（例如，`80000` 而不是 `"$80,000"`）。

**输出约束：**
- 创建/更新：排除子关系，排除导航引用字段（仅允许 `ApiName` 成员）。输出字段始终命名为 `Record`。
- 删除：`Id` 仅。

**`allOrNone` 语义：**
- `true`（默认） — 所有操作成功或所有回滚。
- `false` — 独立操作成功，但依赖操作（使用 `@{alias}`）仍然一起回滚。

#### 变更链接

使用 `@{alias}` 引用从早期变更中的 `Id` 链接相关变更。对于父-子创建（不支持的嵌套子创建）必需。

```graphql
mutation CreateAccountAndContact {
  uiapi(input: { allOrNone: true }) {
    AccountCreate(input: { Account: { Name: "Acme" } }) {
      Record { Id }
    }
    ContactCreate(input: { Contact: { LastName: "Smith", AccountId: "@{AccountCreate}" } }) {
      Record { Id }
    }
  }
}
```

规则：`A` 必须在查询中先于 `B`。`@{A}` 始终是变更 `A` 的 `Id`。仅 `Create` 或 `Delete` 可以从（不能是 `Update`）链接。

#### 删除变更

删除使用通用 `RecordDeleteInput`（不是实体特定）。输出是 `Id` 仅 — 无 `Record` 字段。

```graphql
mutation DeleteAccount($id: ID!) {
  uiapi(input: { allOrNone: true }) {
    AccountDelete(input: { Id: $id }) {
      Id
    }
  }
}
```

#### 对象元数据和 Picklist 值

使用 `uiapi { objectInfos(...) }` 获取字段元数据或 picklist 值。传递**要么** `apiNames` 或 `objectInfoInputs` — 永远不要两者都传递。

```typescript
// 对象元数据
const GET_OBJECT_INFO = gql`
  query GetObjectInfo($apiNames: [String!]!) {
    uiapi {
      objectInfos(apiNames: $apiNames) {
        ApiName
        label
        labelPlural
        fields { ApiName label dataType updateable createable }
      }
    }
  }
`;

// Picklist 值（使用 objectInfoInputs + 内联片段）
const GET_PICKLIST_VALUES = gql`
  query GetPicklistValues($objectInfoInputs: [ObjectInfoInput!]!) {
    uiapi {
      objectInfos(objectInfoInputs: $objectInfoInputs) {
        ApiName
        fields {
          ApiName
          ... on PicklistField {
            picklistValuesByRecordTypeIDs {
              recordTypeID
              picklistValues { label value }
            }
          }
        }
      }
    }
  }
`;
```

### 步骤 4：生成类型（codegen）

编写查询（无论在 `.graphql` 文件中还是在 `gql` 中内联），生成 TypeScript 类型：

```bash
# 从 UI 包含目录运行
npm run graphql:codegen
```

输出：`src/api/graphql-operations-types.ts`

生成的类型命名约定：
- `<OperationName>Query` / `<OperationName>Mutation` — 响应类型
- `<OperationName>QueryVariables` / `<OperationName>MutationVariables` — 变量类型

**始终导入并使用生成的类型** 当调用 `sdk.graphql`：

```typescript
import type { GetAccountsQuery, GetAccountsQueryVariables } from "../graphql-operations-types";

const response = await sdk.graphql?.<GetAccountsQuery, GetAccountsQueryVariables>(GET_ACCOUNTS, variables);
```

使用 `NodeOfConnection<T>` 从 Connection 中提取节点类型以获得更干净的类型：

```typescript
import { type NodeOfConnection } from "@salesforce/sdk-data";

type AccountNode = NodeOfConnection<GetAccountsQuery["uiapi"]["query"]["Account"]>;
```

### 步骤 5：验证和测试

1. **Lint**: `npx eslint <file>` 从 UI 包含目录运行
2. **codegen**: `npm run graphql:codegen` 从 UI 包含目录运行

#### 常见错误模式

| 错误包含 | 解决方案 |
|----------------|------------|
| `Cannot query field` / `ValidationError` | 字段名称错误 — 运行 `graphql-search.sh <Entity>` 并使用类型定义部分中的确切名称 |
| `Unknown type` | 类型名称错误 — 运行 `graphql-search.sh <Entity>` 确认正确的 PascalCase 实体名称 |
| `Unknown argument` | 参数名称错误 — 运行 `graphql-search.sh <Entity>` 并检查过滤或排序部分 |
| `invalid syntax` / `InvalidSyntax` | 根据错误消息修复语法 |
| `validation error` | 字段名称错误 — 运行 `graphql-search.sh <Entity>` 进行验证 |
| `VariableTypeMismatch` | 从模式中正确参数类型 |
| `invalid cross reference id` | 实体已删除 — 询问有效 Id |

**部分** 如果变更返回数据和错误（部分成功）：报告无法访问的字段，解释它们不能在变更输出中，提供删除它们的选项。**等待用户同意** 再更改。

---

## UI 包含集成（React）

两种集成模式：

### 模式 1 — 外部 `.graphql` 文件（复杂查询）

**每个操作一个 `.graphql` 文件。** 每个文件包含恰好一个 `query` 或 `mutation`（以及其片段）。不要将多个操作组合在单个文件中。

```typescript
import { createDataSDK, type NodeOfConnection } from "@salesforce/sdk-data";
import MY_QUERY from "./query/myQuery.graphql?raw"; // ?raw 后缀必需
import type { GetMyDataQuery, GetMyDataQueryVariables } from "../graphql-operations-types";

const sdk = await createDataSDK();
const response = await sdk.graphql?.<GetMyDataQuery, GetMyDataQueryVariables>(MY_QUERY, variables);
```

创建/更改 `.graphql` 文件后，运行 `npm run graphql:codegen` 以生成类型到 `src/api/graphql-operations-types.ts`。

### 模式  | 内联 `gql` 标签（简单查询）

**必须使用 `gql`** — 普通模板字符串绕过 ESLint 模式验证。

```typescript
import { createDataSDK, gql } from "@salesforce/sdk-data";
import type { GetAccountsQuery } from "../graphql-operations-types";

const GET_ACCOUNTS = gql`
  query GetAccounts {
    uiapi {
      query {
        Account(first: 10) {
          edges { node { Id Name @optional { value } } }
        }
      }
    }
  }
`;

const sdk = await createDataSDK();
const response = await sdk.graphql?.<GetAccountsQuery>(GET_ACCOUNTS);
```

### 错误处理

```typescript
// 严格（默认） — 任何错误 = 失败
if (response?.errors?.length) {
  throw new Error(response.errors.map(e => e.message).join("; "));
}

// 宽容 — 记录错误，使用可用数据
if (response?.errors?.length) {
  console.warn("GraphQL 部分错误:", response.errors);
}

// 区分性 — 仅当未返回数据时失败
if (!response?.data && response?.errors?.length) {
  throw new Error(response.errors.map(e => e.message).join("; "));
}

const accounts = response?.data?.uiapi?.query?.Account?.edges?.map(e => e.node) ?? [];
```

---

## REST API 模式

使用 `sdk.fetch` 当 GraphQL 不足时。参见 [支持的 API](#supported-apis) 表格以获取完整的允许列表。

```typescript
declare const __SF_API_VERSION__: string;
const API_VERSION = typeof __SF_API_VERSION__ !== "undefined" ? __SF_API_VERSION__ : "65.0";

// Connect — 文件上传配置
const res = await sdk.fetch?.(`/services/data/v${API_VERSION}/connect/file/upload/config`);

// Apex REST（路径中无版本）
const res = await sdk.fetch?.("/services/apexrest/auth/login", {
  method: "POST",
  body: JSON.stringify({ email, password }),
  headers: { "Content-Type": "application/json" },
});

// UI API — 记录与元数据（简单读取时首选 GraphQL）
const res = await sdk.fetch?.(`/services/data/v${API_VERSION}/ui-api/records/${recordId}`);

// Einstein LLM
const res = await sdk.fetch?.(`/services/data/v${API_VERSION}/einstein/llm/prompt/generations`, {
  method: "POST",
  body: JSON.stringify({ promptTextorId: prompt }),
});
```

**当前用户**: 不要使用 Chatter (`/chatter/users/me`)。使用 GraphQL 代替：

```typescript
const GET_CURRENT_USER = gql`
  query CurrentUser {
    uiapi { currentUser { Id Name { value } } }
  }
`;
const response = await sdk.graphql?.(GET_CURRENT_USER);
```

---

## 目录结构

```
<project-root>/                              ← SFDX 项目根目录
├── schema.graphql                           ← grep 目标（位于此处）
├── sfdx-project.json
├── scripts/graphql-search.sh                ← 模式搜索脚本
└── force-app/main/default/uiBundles/<app-name>/  ← UI 包含目录
    ├── package.json                         ← npm 脚本
    └── src/
```

| 命令 | 从运行 | 原因 |
|---------|----------|-----|
| `npm run graphql:schema` | UI 包含目录 | UI 包含的 package.json 中的脚本 |
| `npm run graphql:codegen` | UI 包含目录 | 生成 GraphQL 类型 |
| `npx eslint <file>` | UI 包含目录 | 读取 eslint.config.js |
| `bash scripts/graphql-search.sh <Entity>` | 项目根目录 | 模式查找 |

---

## 快速参考

### 模式查找（从项目根目录）

运行搜索脚本以一次性获取所有相关模式信息：

```bash
bash scripts/graphql-search.sh <EntityName>
```

| 脚本输出部分 | 用于 |
|-----------------------|----------|
| 类型定义 | 字段名称、父/子关系 |
| 过滤选项 | `where:` 条件 |
| 排序选项 | `orderBy:` |
| CreateRepresentation | 创建变更字段列表 |
| UpdateRepresentation | 更新变更字段列表 |

### 错误类别

| 错误包含 | 解决方案 |
|----------------|------------|
| `Cannot query field` | 字段名称错误 — 运行 `graphql-search.sh <Entity>` 并使用类型定义部分中的确切名称 |
| `Unknown type` | 类型名称错误 — 运行 `graphql-search.sh <Entity>` 确认正确的 PascalCase 实体名称 |
| `Unknown argument` | 参数名称错误 — 运行 `graphql-search.sh <Entity>` 并检查过滤或排序部分 |
| `invalid syntax` | 根据错误消息修复语法 |
| `validation error` | 字段名称错误 — 运行 `graphql-search.sh <Entity>` 进行验证 |
| `VariableTypeMismatch` | 从模式中正确参数类型 |
| `invalid cross reference id` | 实体已删除 — 询问有效 Id |

### 检查清单

- [ ] 所有字段名称通过搜索脚本验证（步骤 2）
- [ ] 读取查询上的 `@optional` 应用到所有记录字段
- [ ] 变更使用 `uiapi(input: { allOrNone: ... })` 包装器
- [ ] 每个查询指定 `first:`
- [ ] 消费代码中的可选链
- [ ] 响应处理中检查 `errors` 数组
- [ ] Lint 通过：`npx eslint <file>`
