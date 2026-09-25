# 生成或搭建 ASP.NET Core 代码

生成 ASP.NET Core 搭建代码——控制器、视图、Razor 页面、Blazor 组件、Minimal API 端点。生成的代码与项目现有的 CSS 框架、布局约定和编码模式相匹配。不使用基于 CLI 的搭建/代码生成工具；仍然需要使用标准的 `dotnet` CLI 命令进行构建、还原和迁移。

## 何时使用

- 在 ASP.NET Core 项目中为模型添加 CRUD 页面、视图或组件
- 使用 Entity Framework Core 搭建 API 控制器或 Minimal API 端点
- 生成由 DbContext 支持的 Razor 页面、MVC 视图或 Blazor 组件

## 何时不使用

- 项目不是 ASP.NET Core 项目
- 您需要搭建非 Web 资产（类库、控制台应用程序等）

## 输入

| 输入 | 必填 | 描述 |
|-------|----------|-------------|
| 搭建请求 | 是 | 自然语言描述要搭建的内容（见下方格式） |
| 项目文件路径 | 是 | 目标 `.csproj` 文件的完整路径 |
| 解决方案根路径 | 推荐 | 多项目解决方案的解决方案根路径 |

### 搭建请求格式

搭建请求应是一个自然语言的描述，说明要搭建的内容。请求必须包含目标项目路径，并提供足够的细节，以便代理生成正确的代码。示例：

**使用 EF 的 Razor 页面：**
```
为 `<ModelName>` 模型（来自 `<Namespace>`) 在项目 `<path-to-csproj>` 中搭建 Razor 页面进行 CRUD 操作。
使用 `<database-provider>` 创建一个新的 DbContext `<DbContextName>`。
还搭建任何 `<ModelName>` 通过必需的外键依赖的实体的 CRUD，以便可以首先创建父实体。
```

**Blazor CRUD 组件：**
```
为 `<ModelName>` 模型（来自 `<Namespace>`) 在项目 `<path-to-csproj>` 中搭建 Blazor CRUD 组件。
使用 `<database-provider>` 创建一个新的 DbContext `<DbContextName>`。
```

**Minimal API 端点：**
```
为 `<ModelName>` 模型（来自 `<Namespace>`) 在项目 `<path-to-csproj>` 中搭建 Minimal API 端点。
将端点类命名为 `<EndpointsClassName>`。
使用 `<database-provider>` 创建一个新的 DbContext `<DbContextName>`。
启用 OpenAPI 支持。
```

**带有视图的 MVC 控制器：**
```
为 `<ModelName>` 模型（来自 `<Namespace>`) 在项目 `<path-to-csproj>` 中搭建带有 Entity Framework 的 MVC 控制器和视图。
将控制器命名为 `<ControllerName>`。
使用现有的 DbContext `<DbContextName>`。
生成视图。
```

**空项（无 EF）：**
```
在项目 `<path-to-csproj>` 中搭建一个名为 `<PageName>` 的空 Razor 页面。
```

## 工作流程

### 第 1 步：理解搭建请求

解析搭建请求以识别：
- **搭建器类型**：Razor 页面、Blazor 组件、MVC 控制器、Minimal API、空页/视图/组件
- **模型类** 及其命名空间
- **DbContext**：新的或现有的，数据库提供程序（SQLite、SQL Server 等）
- **命名项**：控制器名称、端点类名称、页面名称、视图名称、区域名称
- **选项**：OpenAPI、异步操作、部分视图、自定义布局
- **FK 范围**：是否还要搭建引用必需外键的父实体的 CRUD

### 执行检查清单

按顺序完成适用的检查清单。不要在创建仅请求的子资源后停止，当必需的外键使父资源成为必要时。

**所有 EF 搭建器**

1. 在编辑之前，检查项目文件、`Program.cs`、目标模型、验证属性、导航属性和外键。
2. 重用请求的现有 `DbContext`；否则创建请求的上下文。仅添加所需的提供程序包，并使用请求的提供程序和连接字符串通过 `AddDbContext` 注册它。当需要迁移且它缺失时，需要添加 Microsoft.EntityFrameworkCore.Design（PrivateAssets="all”）。
3. 为请求的实体和每个必需的父实体生成完整的 CRUD：列表、详细信息、创建、编辑和删除。
4. 使用 EF 迁移生命周期：创建迁移并应用它。永远不要调用 `EnsureCreated` 或在 `Program.cs` 中填充数据库。
5. 还原、构建并测试生成的项目。在报告完成之前修复错误。

**MVC、Razor 页面和 Blazor**

1. 在生成标记之前，检查现有的布局、CSS 和代表性 UI。
2. 生成完整的子资源和必需父资源的 UI 流程，包括到每个资源的导航路径，以便用户可以在创建子资源之前创建父资源。
3. 匹配现有的 UI 框架和约定；保留 Blazor 的现有渲染模式配置。

**Minimal APIs**

1. 为每个资源使用路由组，并为子资源和必需父资源映射 `GET`（列表和按 ID）、`POST`、`PUT` 和 `DELETE` 端点。
2. 为每个端点添加 OpenAPI 元数据：唯一名称、标签、描述、成功/错误响应元数据，并在启用 OpenAPI 时使用 `WithOpenApi`。
3. 为每个 CRUD 请求创建一个可执行的 `.http` 文件。首先创建父记录，捕获或明确重用其返回的 ID，以在子请求中使用，并按依赖顺序运行请求。

### 第 2 步：发现 UI 风格（仅限非 API 搭建器）

为 API 控制器和 Minimal API 端点跳过此步骤。

1. 检查项目的布局文件（`_Layout.cshtml`、`MainLayout.razor` 或等效文件）
2. 检查主 CSS 文件（`site.css`、`app.css`、Tailwind 配置等）
3. 检查项目中的 1-2 个现有页面、视图或组件

所有生成的文件必须与现有的 UI 框架、CSS 类和约定相匹配。如果使用 Bootstrap，则生成 Bootstrap 标记。如果使用 Tailwind，则生成 Tailwind 标记。

### 第 3 步：应用 Blazor 特定规则（仅限 Blazor 搭建器）

为非 Blazor 搭建器跳过此步骤。

- `[SupplyParameterFromForm]` 属性必须使用 `= new()`（而不是 `null!`）——防止 `EditForm` 在初始 GET 时崩溃
- `Program.cs` 必须在 `AddRazorComponents()` 上链式调用 `.AddInteractiveServerComponents()`，并在 `MapRazorComponents<App>()` 上链式调用 `.AddInteractiveServerRenderMode()`。仅在生成的组件实际使用 @rendermode InteractiveServer（或项目已经使用）时才添加交互式服务器服务/渲染模式
- 不要替换现有的链式渲染模式调用（例如，`.AddInteractiveWebAssemblyRenderMode()`）

### 第 4 步：生成代码

手动生成所有代码文件。遵循以下约束：

- **不要**使用任何搭建 CLI 工具
- **不要**添加超出搭建功能所需包（例如，不要添加 `RuntimeCompilation` 或其他便利包）
- 匹配项目中现有文件的编码风格（命名约定、缩进、命名空间模式）

#### 为 API 端点添加 OpenAPI 元数据（仅限 API 搭建器）

在生成带有 OpenAPI 支持的 Minimal API 或 MVC API 端点时，为每个端点添加丰富的元数据，以便 OpenAPI 文档具有描述性和实用性：

- `.WithName("GetTodoItems")` — 为每个端点提供唯一的操作 ID
- `.WithTags("TodoItems")` — 按资源分组端点
- `.WithDescription("Returns all todo items")` — 人类可读的摘要
- `.Produces<List<TodoItem>>(StatusCodes.Status200OK)` — 文档成功响应类型
- `.Produces(StatusCodes.Status404NotFound)` — 文档错误响应
- `.ProducesValidationProblem()` — 用于验证输入的端点
- `.WithOpenApi()` — 将端点纳入 OpenAPI 生成（如果尚未全局启用）

Minimal API GET 端点示例：
```csharp
group.MapGet("/", async (TodoDbContext db) =>
        await db.TodoItems.ToListAsync())
    .WithName("GetAllTodoItems")
    .WithTags("TodoItems")
    .WithDescription("Returns all todo items")
    .Produces<List<TodoItem>>(StatusCodes.Status200OK);
```

### 第 5 步：设置 Entity Framework（如果适用）

如果搭建请求不涉及 Entity Framework，则跳过此步骤。

- **不要**在 `Program.cs` 中填充数据库——始终使用迁移
- 对于 `dotnet ef`：优先使用从本地工具清单中的 `dotnet tool restore`。如果不存在清单，则仅在必要时全局安装
- 检查模型中的导航属性和外键。确保为引用的实体存在 CRUD 端点/页面
- 对于 API 搭建器：`.http` 文件必须先创建父实体，然后创建子实体。使用与创建顺序一致的 FK 值

### 第 6 步：生成 `.http` 文件（仅限 API 搭建器）

为非 API 搭建器跳过此步骤。

1. 在项目目录中创建一个名为 `{ModelName}.http` 的 `.http` 文件。如果存在同名文件，则追加数字后缀（`Product2.http`、`Product3.http`）直到唯一
2. 包括为每个搭建的 CRUD 端点（包括父/依赖实体端点）提供的示例请求
3. 每个请求必须指向与实际映射端点匹配的正确 URL 路径
4. 请求标签必须准确描述操作（例如，“创建一个类别”必须 POST 到类别端点）
5. 按依赖顺序排列请求：先创建父实体，然后创建子实体
6. 当可能时，使用 HTTP 客户端的变量/模板功能捕获父创建响应的 ID，并将其作为子实体 POST 负载中的外键值
7. 如果您的客户端无法捕获响应值，请添加注释，指示在运行父创建请求后必须更新的 FK ID；不要留下不切实际的占位符或假设的 FK 值，这些值与实际父记录不对应，在执行请求时

### 第 7 步：验证

1. 从项目目录运行 `dotnet restore && dotnet build`
2. 如果使用 Entity Framework 且这是首次验证：
   - 运行 `dotnet ef migrations add InitialCreate`
   - 运行 `dotnet ef database update`
   - 如果多次运行此命令，需要将 "InitialCreate" 更改为其他内容，因为 EF Core 要求迁移名称唯一
3. 如果 API 搭建器：
   - 检查 `Properties/launchSettings.json`——如果存在名为 `https` 的配置文件，则使用 `dotnet run --launch-profile https`
   - 按依赖顺序逐个执行每个 `.http` 请求
   - 为每个请求报告方法、URL 和状态代码
   - 如果任何请求返回非 2xx，则停止并修复
4. 修复所有错误，直到干净构建成功

## 验证

- [ ] 所有生成的文件与项目的现有 CSS 框架和约定相匹配
- [ ] `dotnet build` 成功且错误为零
- [ ] EF 迁移干净应用（如果适用）
- [ ] 所有 `.http` 请求返回 2xx 状态代码（如果 API 搭建器）
- [ ] 没有添加禁用包（`RuntimeCompilation` 等）
- [ ] 没有调用 CLI 搭建工具
- [ ] Blazor `[SupplyParameterFromForm]` 属性使用 `= new()`（如果 Blazor 搭建器）

## 常见陷阱

| 陷阱 | 解决方案 |
|---------|----------|
| 生成的 UI 与项目的 CSS 框架不匹配 | 始终在生成代码前检查布局和 CSS 文件（步骤 2） |
| Blazor `EditForm` 在初始 GET 时崩溃 | 使用 `= new()` 而不是 `null!` 为 `[SupplyParameterFromForm]` 属性 |
| EF 迁移因缺少父实体 CRUD 而失败 | 当请求提到外键时，搭建 FK 依赖实体的 CRUD |
| `.http` 文件具有错误的 FK 值 | 按依赖顺序排列请求；使用与创建顺序一致的 FK 值 |
| 未找到 `dotnet ef` | 首先尝试 `dotnet tool restore`；仅在必要时全局安装 |
| 添加了不必要的包 | 仅添加显式为搭建功能所需的包 |
| 生成的代码使用不同的命名约定 | 在生成代码前检查现有项目文件以匹配命名模式 |

## 参考

- [Entity Framework Core DbContext 生命周期、配置和初始化](https://learn.microsoft.com/en-us/ef/core/dbcontext-configuration/)
- [ASP.NET Core 中的 OpenAPI 概述](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/overview?view=aspnetcore-10.0) — .NET 10 具体版本；其他版本存在类似页面
