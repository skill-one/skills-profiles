# Firebase SQL Connect

Firebase SQL Connect 是一个使用 Cloud SQL for PostgreSQL 的关系型数据库服务，具有 GraphQL 架构、自动生成的查询/变更以及类型安全的 SDK。

> [!NOTE] **产品重命名**：Firebase Data Connect 已更名为 **Firebase SQL Connect**。本技能仓库中所有指向 "Data Connect" 或 "Firebase Data Connect" 的说明、参考和示例均适用于 "SQL Connect" 和 "Firebase SQL Connect"。

## 项目结构

```text
dataconnect/
├── dataconnect.yaml      # 服务配置
├── seed_data.gql         # 仅限本地 — 原型/测试数据
├── schema/
│   └── schema.gql        # 数据模型 (带 @table 的类型)
└── connector/
    ├── connector.yaml    # 连接器配置 + SDK 生成
    ├── queries.gql       # 查询
    └── mutations.gql     # 变更
```

## 验证的关键工具

依赖这两个机制来确保项目正确性：

1. **审查 GraphQL 架构**：用户定义的和生成的扩展 (位于 `.dataconnect/schema/main/` 中)。
1. **验证操作**：对架构运行 `npx -y firebase-tools@latest dataconnect:compile`。

## 操作策略：GraphQL 与原生 SQL

始终默认使用 **原生 GraphQL**。**原生 SQL 缺乏类型安全**，绕过了架构强制的结构。仅在用户明确请求或任务需要高级数据库功能时使用 **原生 SQL**。

| 策略                     | 使用场景                                                                                                            | 实现                                                                                                        |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- |
| **原生 GraphQL** (默认) | 几乎所有用例。标准 CRUD、基本过滤/排序、简单关系连接。需要完全的类型安全。      | 自动生成的字段 (`movie_insert`, `movies`)。强类型和架构强制执行。                               |
| **原生 SQL** (高级)    | PostgreSQL 扩展 (例如，PostGIS)、窗口函数 (`RANK()`)、复杂聚合或高度优化的子查询。 | 通过 `_select`, `_execute` 等使用原始 SQL 字符串字面量。需要严格的 positional parameters (`$1`)。无类型安全。 |

## 开发工作流

遵循以下严格工作流程来构建您的应用程序。您 **必须** 阅读每个步骤的链接参考文件以了解语法和可用功能。

### 1. 定义数据模型 (`schema/schema.gql`)

定义您的 GraphQL 类型、表和关系 (映射到 Postgres 架构)。

> **阅读 [参考/schema.md](reference/schema.md)** 以了解：
>
> - `@table`, `@col`, `@default`
> - 关系 (`@ref`, 一对多，多对多)
> - 数据类型 (UUID, Vector, JSON 等)

### 2. 定义授权操作 (`connector/queries.gql`, `connector/mutations.gql`)

编写客户端将使用的查询和变更，包括授权逻辑。SQL Connect 默认安全。

> **阅读 [参考/operations.md](reference/operations.md)** 以了解：
>
> - **查询**：过滤 (`where`)、排序 (`orderBy`)、分页 (`limit`/`offset`)。
> - **变更**：创建 (`_insert`)、更新 (`_update`)、删除 (`_delete`)。
> - **Upserts**：使用 `_upsert` "插入或更新" 记录 (用户配置文件的关键)。
> - **事务**：使用 `@transaction` 进行多步骤原子操作。使用 `_expr: "response.<prevStep>"` 在步骤间传递数据。
>
> **阅读 [参考/security.md](reference/security.md)** 以了解授权：
>
> - `@auth(level: ...)` 用于 PUBLIC、USER 或 NO_ACCESS。
> - `@check` 和 `@redact` 用于行级安全性和验证。
>
> **阅读 [参考/realtime.md](reference/realtime.md)** 以了解实时订阅：
>
> - `@refresh` 指令用于基于时间的轮询和事件驱动更新。
> - CEL 条件精确地作用域刷新触发器。
>
> **阅读 [参考/native_sql.md](reference/native_sql.md)** 以了解原生 SQL 操作：
>
> - 使用 `_select`, `_selectFirst`, `_execute` 嵌入原始 SQL
> - 严格的 positional parameters (`$1`, `$2`)、引号和 CTE 规则
> - 高级 PostgreSQL 功能 (PostGIS, 窗口函数)

### 3. 在您的应用程序中使用类型安全的 SDK

为您的客户端平台生成类型安全代码。

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

生成 SDKs：

```bash
npx -y firebase-tools@latest dataconnect:sdk:generate
```

有关如何使用生成的 SDK 的平台特定说明，请阅读：

- **Web (TypeScript)**：[参考/sdk_web.md](reference/sdk_web.md)
- **Android (Kotlin)**：[参考/sdk_android.md](reference/sdk_android.md)
- **iOS (Swift)**：[参考/sdk_ios.md](reference/sdk_ios.md)
- **Admin (Node.js)**：
  [参考/sdk_admin_node.md](reference/sdk_admin_node.md)
- **Flutter (Dart)**：[参考/sdk_flutter.md](reference/sdk_flutter.md)

______________________________________________________________________

## 功能能力映射

如果您需要实现特定功能，请参考映射的参考文件：

| 功能                         | 参考文件                                               | 关键概念                                       |
| :-------------------------- | :----------------------------------------------------- | :--------------------------------------------- |
| **数据建模**               | [参考/schema.md](reference/schema.md)                   | `@table`, `@unique`, `@index`, 关系           |
| **向量搜索**               | [参考/search.md](reference/search.md)                   | `Vector`, `@col(dataType: "vector")`, 嵌入   |
| **全文搜索**               | [参考/search.md](reference/search.md)                   | `@searchable`, `movies_search`                 |
| **Upsert 数据**              | [参考/operations.md](reference/operations.md)           | `_upsert` 变更                                |
| **复杂过滤**             | [参考/operations.md](reference/operations.md)           | `_or`, `_and`, `_not`, `eq`, `contains`        |
| **事务**                | [参考/operations.md](reference/operations.md)           | `@transaction`, `response` 绑定                 |
| **环境配置**          | [参考/config.md](reference/config.md)                   | `dataconnect.yaml`, `connector.yaml`               |
| **实时订阅**              | [参考/realtime.md](reference/realtime.md)               | `@refresh`, `subscribe()`, 自动刷新            |
| **云函数集成**            | [参考/cloud_functions.md](reference/cloud_functions.md) | `onMutationExecuted`, 触发事件            |
| **数据播种 & 迁移**   | [参考/data_seeding.md](reference/data_seeding.md)       | `seed_data.gql`, `_insertMany`, Admin SDK 批量     |
| **启动模板**           | [templates.md](templates.md)                                 | CRUD, 用户拥有的资源, 多对多, SDK 初始化 |

______________________________________________________________________

## 部署 & CLI

> **阅读 [参考/config.md](reference/config.md)** 以深入了解配置。

根据您当前的任务遵循这些模式：

### 如何在 Firebase 项目中初始化 SQL Connect

1. 理解应用想法。如果不清楚，请提出澄清问题。
1. 运行 `npx -y firebase-tools@latest init dataconnect`。
1. 验证应用模板和生成的 SDK 是否已设置。

### 如何使用 SQL Connect 本地构建应用程序

1. 启动模拟器：
   `npx -y firebase-tools@latest emulators:start --only dataconnect`。
1. 编写架构和操作。
1. 将本地测试数据播种到 `seed_data.gql`。阅读
   [参考/data_seeding.md](reference/data_seeding.md#本地原型数据播种)。
1. 运行 `npx -y firebase-tools@latest dataconnect:compile` 或
   `npx -y firebase-tools@latest dataconnect:sdk:generate` 以验证它们。
1. 在您的应用程序中使用这些操作并构建它。

### 如何将 SQL Connect 部署到 Cloud SQL

1. 运行 `npx -y firebase-tools@latest deploy --only dataconnect`。

## 示例

有关架构和操作的完整、可工作的代码示例，请参阅 **[examples.md](examples.md)**。

有关现成的启动模板 (CRUD、用户拥有的资源、多对多、YAML 配置、SDK 初始化)，请参阅 **[templates.md](templates.md)**。
