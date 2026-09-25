# /scaffold — 基于架构感知的功能脚手架

## 什么是

根据项目的架构生成完整的功能，包含所有必需的文件。绝不生成半成品功能——每个脚手架都包含端点、处理器、验证、数据传输对象（DTO）、EF 配置以及至少一个作为单一单元的集成测试，使用现代 C# 14（主要构造函数、集合表达式、记录、密封处理器、TypedResults）编写。

支持的架构（文件放置映射和代码形状模板位于 `references/architecture-patterns.md` 中）：

- **垂直切片架构 (VSA)** — 位于 `Features/` 中的单文件功能
- **整洁架构 (CA)** — 文件分布在领域、应用、基础设施、Api 各层
- **领域驱动设计 (DDD) + 整洁架构** — 聚合根、值对象、领域事件，以及 CA 各层
- **模块化单体** — 具有自己 DbContext 和集成事件的独立模块

## 何时使用

- "为 [功能名称] 脚手架"、"为...创建端点"、"添加功能"
- "为...生成 CRUD"、"添加实体"、"新模块"、"为模块脚手架"
- 在 `/plan` 生成批准的计划后开始新功能
- 自定义生成模板或定义完整切片包含的内容
- 任何用户需要完整、可工作的功能骨架时

## 如何使用

### 第 1 步：检测架构

使用 `architecture-advisor` 技能确定项目的架构：
- 检查文件夹结构、项目引用和现有模式
- 如果架构不明确，则询问用户而不是猜测
- 加载匹配的架构技能（垂直切片、整洁架构、DDD）

### 第 2 步：明确范围

在生成前与用户确认（跳过计划已回答的内容）：
1. 功能/实体名称和所需操作——完整 CRUD 还是子集？
2. 新实体的关键字段和不变性
3. 模块放置（仅限模块化单体）——现有模块还是新模块？

### 第 3 步：学习约定

使用 `convention-learner` 技能和 MCP 工具进行检查：
- 命名模式（`*Handler`、`*Service`、`*Endpoint`、`*Command`、`*Query`）
- 文件夹结构、文件组织、访问修饰符、密封约定
- 现有验证方法（FluentValidation、数据注解、手动）
- 测试项目结构和命名（`*Tests`、`*IntegrationTests`）

匹配现有约定。不要在已建立的代码库中强加新约定。

### 第 4 步：生成所有层

根据 `references/architecture-patterns.md` 中的模板生成架构所需的每个文件：

- **VSA** — 阅读 VSA 部分：单文件功能 + 端点组 + EF 配置 + 测试
- **整洁架构** — 阅读 CA 部分：应用层中的中介命令/处理器，Api 层中的端点
- **DDD** — 阅读 DDD 部分：具有不变性和领域事件的聚合，薄处理器
- **模块化单体** — 模块 DbContext、DI 注册、集成事件

参考也涵盖了每个架构重用的共享形状（端点组、验证器、实体 + `IEntityTypeConfiguration<T>` 对、测试固定件）以及应避免的反模式。

### 第 5 步：完整性检查清单（强制要求）

每个脚手架的功能必须包含所有九项。不要跳过任何一项：

- [ ] **端点** — `IEndpointGroup` 文件，包含路由组；从未在 Program.cs 中配置
- [ ] **处理器** — `sealed`、主要构造函数，每个操作一个
- [ ] **验证器** — 有意义的 FluentValidation 规则（范围、必需、最大长度），通过 `.AddEndpointFilter<ValidationFilter<T>>()` 在修改端点上配置
- [ ] **DTO** — 为消费者定制的记录，绝不与实体一对一映射
- [ ] **EF 配置** — `IEntityTypeConfiguration<T>`；实体上没有数据注解
- [ ] **集成测试** — `WebApplicationFactory` + Testcontainers，通过 `services.RemoveAll<DbContextOptions<T>>()` 替换 DI
- [ ] **OpenAPI 元数据** — `.WithName()`、`.WithSummary()`、`.Produces<T>()`、`.ProducesValidationProblem()`、`.ProducesProblem(404)`
- [ ] **CancellationToken** — 在每个异步方法上，并在每个异步调用中传递
- [ ] **结果模式** — 处理器返回 `Result<T>`；端点将成功映射到 TypedResults，失败映射到 `ToProblemDetails()`

同时验证支持的基础设施——如果缺失则脚手架生成：列出端点、获取有界分页（`page`/`pageSize`，最大 50）、Program.cs 包含 `app.UseExceptionHandler()`、appsettings.json 包含连接字符串。

### 第 6 步：验证

在报告完成前证明脚手架可用：

```bash
dotnet build --no-restore
dotnet test --no-build --filter "FullyQualifiedName~{FeatureName}"
```

如果构建或测试失败，修复后重新运行再呈现结果。

## 示例

```
用户: /scaffold 一个具有 CRUD 操作的产品目录功能

Claude: 检测到架构：垂直切片架构

创建的文件：
  src/Features/Products/CreateProduct.cs     -- 命令 + 处理器 + 验证器
  src/Features/Products/GetProduct.cs        -- 通过 ID 查询 + 处理器
  src/Features/Products/ListProducts.cs      -- 分页列表 + 处理器
  src/Features/Products/UpdateProduct.cs     -- 命令 + 处理器 + 验证器
  src/Features/Products/DeleteProduct.cs     -- 命令 + 处理器
  src/Features/Products/ProductEndpoints.cs  -- IEndpointGroup, OpenAPI 元数据
  src/Features/Products/ProductConfig.cs     -- EF Core 配置
  tests/Features/Products/CreateProductTests.cs
  tests/Features/Products/GetProductTests.cs
  tests/Features/Products/ListProductsTests.cs

检查清单：9/9 | 构建：PASS | 测试：PASS

所有文件遵循现有约定（密封处理器、主要构造函数、TypedResults 返回类型）。
```

## 相关

- `dotnet-init` — 在脚手架功能前初始化项目和 CLAUDE.md
- `vertical-slice` — VSA 脚手架遵循的 VSA 模式
- `clean-architecture` — CA 脚手架背后的分层规则
- `ddd` — DDD 脚手架背后的聚合和领域事件模式
- `project-structure` — 每个架构中文件所属位置
