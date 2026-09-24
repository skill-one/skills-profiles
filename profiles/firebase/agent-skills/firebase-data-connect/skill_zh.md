# Firebase SQL Connect

Firebase SQL Connect 是一个基于 Cloud SQL 的 PostgreSQL 关系型数据库服务，支持 GraphQL 模式、自动生成的查询/变更以及类型安全的 SDK。

> [!NOTE] **产品更名**：Firebase Data Connect 更名为 **Firebase SQL Connect**。本技能仓库中所有提及 "Data Connect" 或 "Firebase Data Connect" 的说明、引用和示例，同样适用于 "SQL Connect" 和 "Firebase SQL Connect"。

## 项目结构

```text
dataconnect/
├── dataconnect.yaml      # Service configuration
├── seed_data.gql         # LOCAL ONLY — prototype/test data
├── schema/
│   └── schema.gql        # Data model (types with @table)
└── connector/
    ├── connector.yaml    # Connector config + SDK generation
    ├── queries.gql       # Queries
    └── mutations.gql     # Mutations
```

## 关键验证工具

依赖以下两种机制来确保项目正确性：

1. **审查 GraphQL 模式**：包括用户定义的扩展和生成的扩展（位于 `.dataconnect/schema/main/` 中）。
1. **验证操作**：针对模式运行
   `npx -y firebase-tools@latest dataconnect:compile`。

## 操作策略：GraphQL 与原生 SQL

始终默认使用 **Native GraphQL**。**Native SQL 缺乏类型安全性**，会绕过模式强制的结构约束。仅在用户明确要求或使用任务需要高级数据库功能时使用 **Native SQL**。

| 策略                     | 何时使用                                                                                                            | 实现方式                                                                                                        |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Native GraphQL** (默认) | 几乎所有使用场景。标准 CRUD、基本筛选/排序、简单的关联连接。需要完整的类型安全性。      | 自动生成的字段（`movie_insert`、`movies`）。强类型与模式强制。                               |
| **Native SQL** (高级)    | PostgreSQL 扩展（如 PostGIS）、窗口函数（`RANK()`）、复杂的聚合或高度优化的子查询。 | 通过 `_select`、`_execute` 等嵌入原始 SQL 字符串字面量。要求严格的按位置参数（`$1`）。无类型安全性。 |

## 开发工作流程

遵循此严格的工作流程来构建您的应用程序。您**必须**阅读每个步骤中链接的参考文件，以理解语法和可用功能。

### 1. 定义数据模型（`schema/schema.gql`）

定义您的 GraphQL 类型、表及关系（映射到 Postgres 模式）。

> **阅读 [reference/schema.md](reference/schema.md)** 以了解：
>
> - `@table`、`@col`、`@default`
> - 关系（`@ref`、一对多、多对多）
> - 数据类型（UUID、Vector、JSON 等）

### 2. 定义授权操作（`connector/queries.gql`、`connector/mutations.gql`）

编写客户端将使用的查询和变更，包括授权逻辑。SQL Connect 默认即安全。

> **阅读 [reference/operations.md](reference/operations.md)** 以了解：
>
> - **查询**：筛选（`where`）、排序（`orderBy`）、分页（`limit`/`offset`）。
> - **变更**：创建（`_insert`）、更新（`_update`）、删除（`_delete`）。
> - **插入或更新**：使用 `_upsert` 进行记录“插入或更新”（对用户资料至关重要）。
> - **事务**：使用 `@transaction` 进行多步原子操作。使用 `_expr: "response.<prevStep>"` 在步骤之间传递数据。
>
> **阅读 [reference/security.md](reference/security.md)** 以了解授权：
>
> - `@auth(level: ...)` 用于 PUBLIC、USER 或 NO_ACCESS。
> - `@check` 和 `@redact` 用于行级安全与验证。
>
> **阅读 [reference/realtime.md](reference/realtime.md)** 以了解实时订阅：
>
> - `@refresh` 指令用于基于时间轮询和事件驱动更新。
> - CEL 条件用于精确限定刷新触发条件。
>
> **阅读 [reference/native_sql.md](reference/native_sql.md)** 以了解原生 SQL 操作：
>
> - 使用 `_select`、`_selectFirst`、`_execute` 嵌入原始 SQL
> - 严格的位置参数（`$1`、`$2`）、引号引用与 CTE 的规则
> - 高级 PostgreSQL 功能（PostGIS、窗口函数）

### 3. 在您的应用中使用类型安全的 SDK

为您的客户端平台生成类型安全的代码。

在 `connector.yaml` 中配置 SDK 生成：

```yaml
connectorId: my-connector
generate:
  javascriptSdk:
    outputDir: "../web-app/src/lib/dataconnect"
    package: "@movie-app/dataconnect"
  kotlinSdk:
    outputDir: "../android-app/app/src/main/kotlin/com/example/dataconnect"
    package: "com.example.dataconnect"
  swiftSdk:
    outputDir: "../ios-app/DataConnect"
```

生成 SDK：

```bash
npx -y firebase-tools@latest dataconnect:sdk:generate
```

关于如何使用这些生成的 SDK 的平台特定说明，请阅读：

- **Web (TypeScript)**: [reference/sdk_web.md](reference/sdk_web.md)
- **Android (Kotlin)**: [reference/sdk_android.md](reference/sdk_android.md)
- **iOS (Swift)**: [reference/sdk_ios.md](reference/sdk_ios.md)
- **Admin (Node.js)**:
  [reference/sdk_admin_node.md](reference/sdk_admin_node.md)
- **Flutter (Dart)**: [reference/sdk_flutter.md](reference/sdk_flutter.md)

______________________________________________________________________

## 功能能力映射

如果需要实现特定功能，请查阅对应的映射参考文件：

| 功能                         | 参考文件                                               | 关键概念                                       |
| :------------------------------ | :----------------------------------------------------------- | :------------------------------------------------- |
| **数据建模**               | [reference/schema.md](reference/schema.md)                   | `@table`、`@unique`、`@index`、关系           |
| **向量搜索**               | [reference/search.md](reference/search.md)                   | `Vector`、`@col(dataType: "vector")`、嵌入   |
| **全文搜索**            | [reference/search.md](reference/search.md)                   | `@searchable`、`movies_search`                     |
| **数据插入或更新**              | [reference/operations.md](reference/operations.md)           | `_upsert` 变更                                |
| **复杂筛选**             | [reference/operations.md](reference/operations.md)           | `_or`、`_and`、`_not`、`eq`、`contains`            |
| **事务**                | [reference/operations.md](reference/operations.md)           | `@transaction`、`response` 绑定                 |
| **环境配置**          | [reference/config.md](reference/config.md)                   | `dataconnect.yaml`、`connector.yaml`               |
| **实时订阅**      | [reference/realtime.md](reference/realtime.md)               | `@refresh`、`subscribe()`、自动刷新            |
| **云函数集成** | [reference/cloud_functions.md](reference/cloud_functions.md) | `onMutationExecuted`、触发事件            |
| **数据播种与迁移**   | [reference/data_seeding.md](reference/data_seeding.md)       | `seed_data.gql`、`_insertMany`、Admin SDK 批量     |
| **入门模板**           | [templates.md](templates.md)                                 | CRUD、用户拥有的资源、多对多、SDK 初始化 |

______________________________________________________________________

## 部署与 CLI

> **阅读 [reference/config.md](reference/config.md)** 以深入了解配置。

根据您当前的任务，遵循以下模式：

### 如何在 Firebase 项目中初始化 SQL Connect

1. 理解应用方案。如有疑问，请提出澄清问题。
1. 运行 `npx -y firebase-tools@latest init dataconnect`。
1. 验证应用模板和生成的 SDK 是否已正确配置。

### 如何使用 SQL Connect 在本地构建应用

1. 启动模拟器：
   `npx -y firebase-tools@latest emulators:start --only dataconnect`。
1. 编写模式与操作。
1. 将本地测试数据填充到 `seed_data.gql` 中。阅读
   [reference/data_seeding.md](reference/data_seeding.md#local-prototyping-data-seeding)。
1. 运行 `npx -y firebase-tools@latest dataconnect:compile` 或
   `npx -y firebase-tools@latest dataconnect:sdk:generate` 以进行验证。
1. 在您的应用中使用操作并构建应用。

### 如何部署 SQL Connect 至 Cloud SQL

1. 运行 `npx -y firebase-tools@latest deploy --only dataconnect`。

## 示例

有关模式与操作的完整、可运行代码示例，请参阅
**[examples.md](examples.md)**。

有关可直接使用的入门模板（CRUD、用户拥有的资源、多对多、YAML 配置、SDK 初始化），请参阅
**[templates.md](templates.md)**。
