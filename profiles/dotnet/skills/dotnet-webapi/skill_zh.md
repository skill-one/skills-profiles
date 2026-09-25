# ASP.NET Core Web API

使用正确的 HTTP 语义、OpenAPI 文档和错误处理来生成结构良好的 ASP.NET Core Web API 端点。

## 使用场景

在处理 ASP.NET Core HTTP API 时使用此技能，包括：

- 添加或修改使用控制器或最小 API 实现的 Web API 端点；
- 配置 OpenAPI/Swagger 元数据和端点文档；
- 定义请求/响应 DTO 并保持一致的 HTTP 状态码行为；
- 添加 `.http` 文件或类似的基于请求的 API 测试工件；
- 配置集中式 API 错误处理中间件或异常映射。

## 不适用场景

不要使用此技能用于：

- 通用 C# 编码风格或非 API 重构；
- EF Core 数据建模或查询优化工作；使用 `optimizing-ef-core-queries`；
- 前端、Razor 或 Blazor UI 变更；
- gRPC 服务；
- SignalR 节点或实时消息流。

## 输入/前提条件

在应用此技能之前，收集与现有 API 风格和配置相匹配的项目上下文：

- ASP.NET Core 入口点，通常是 `Program.cs`；
- 任何现有控制器，特别是继承 `ControllerBase` 或使用 `[ApiController]` 的类；
- 任何现有最小 API 注册，例如 `app.MapGet`、`app.MapPost`、`app.MapPut` 或 `app.MapDelete`；
- 项目已使用的相关 DTO、模型、验证和错误处理类型；
- 可用的构建、运行和测试命令，以便验证更改。

如果用户要求添加新端点，请先检查当前项目结构，以便实现遵循既定约定，而不是混合风格。

## 工作流程

### 第 1 步：确定 API 风格

在编写任何代码之前，扫描项目以查找现有的端点模式。

1. 搜索继承 `ControllerBase` 或装饰 `[ApiController]` 的类。
2. 在 `Program.cs` 或端点文件中搜索 `app.MapGet`、`app.MapPost` 等。
3. 如果项目已使用 **控制器**，则继续使用控制器。
4. 如果项目已使用 **最小 API**，则继续使用最小 API。
5. 如果两者都不存在（新项目），则 **默认使用最小 API**，除非用户明确要求控制器。

不要在同一项目中混合风格。

### 第 2 步：定义请求和响应类型

为 API 输入和输出创建专用类型。永远不要直接在请求或响应正文中暴露 EF Core 实体。

**使用 `sealed record` 作为所有 DTO**。记录强制不可变性、提供基于值的相等性，并生成简洁的代码。将它们密封以防止意外继承并启用 JIT 虚拟化（CA1852）。

**命名约定**：

| 角色 | 约定 | 示例 |
|------|-----------|---------|
| 输入（创建） | `Create{Entity}Request` | `CreateProductRequest` |
| 输入（更新） | `Update{Entity}Request` | `UpdateProductRequest` |
| 输出（单个） | `{Entity}Response` | `ProductResponse` |
| 输出（列表） | `{Entity}ListResponse` | `ProductListResponse` |

**所有 DTO 的 XML 文档注释**：为 API 中公开的每个请求和响应类型添加 `<summary>` XML 文档注释。这些注释会自动包含在生成的 OpenAPI 规范中，从而在不添加额外元数据调用的情况下生成更丰富的文档。

参考：https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/openapi-comments

**日期和时间值 — 使用 `DateTimeOffset`**：当 DTO 包含日期或时间属性时，始终使用 `DateTimeOffset` 而不是 `DateTime`。
`DateTimeOffset` 保留 UTC 偏移量，避免模糊的时区转换，并在 JSON 中序列化为带有偏移量信息的 ISO 8601 — 这是 API 消费者期望的格式。

参考：https://learn.microsoft.com/en-us/dotnet/api/system.datetimeoffset

**JSON 序列化选项 — 默认保留现有行为**：对于现有 API，**不要**引入更严格的序列化/反序列化设置，除非项目已使用它们或用户明确要求它们。设置（如区分大小写的属性匹配和严格的数字处理）可能会破坏现有客户端。对于**新项目**，或在明确要求严格 JSON 处理时，配置以下选项以最大程度地减少处理恶意请求的可能性：

```csharp
// 仅适用于新项目，当现有项目已使用它们，或用户明确要求更严格的 JSON 行为时应用这些设置。
builder.Services.ConfigureHttpJsonOptions(options =>
{
    // 禁止从 JSON 字符串读取数字
    options.SerializerOptions.NumberHandling = JsonNumberHandling.Strict;
    // 在反序列化期间区分大小写地匹配属性
    options.SerializerOptions.PropertyNameCaseInsensitive = false;
    // 在反序列化期间拒绝重复的 JSON 属性名
    options.SerializerOptions.AllowDuplicateProperties = false;
    // 从序列化输出中省略 null 属性
    options.SerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
});
```

**枚举属性 — 默认按字符串序列化**：除非用户明确要求整数序列化，否则所有枚举属性都应按字符串序列化。按字符串序列化的枚举更易于阅读，在值重新排序时更不脆弱，并生成更好的 OpenAPI 文档。有关 `JsonStringEnumConverter` 配置，请参阅第 4 步。

**响应 DTO** — 使用位置密封记录以实现简洁、不可变的输出：

```csharp
/// <summary>表示 API 返回的产品。</summary>
public sealed record ProductResponse(
    int Id,
    string Name,
    decimal Price,
    Category Category,
    bool IsAvailable,
    DateTimeOffset CreatedAt);
```

**请求 DTO** — 使用带有 `init` 属性的密封记录，以便数据注解自然工作：

```csharp
/// <summary>创建新产品的有效负载。</summary>
public sealed record CreateProductRequest
{
    [Required, MaxLength(200)]
    public required string Name { get; init; }

    [Range(0.01, 999999.99)]
    public required decimal Price { get; init; }

    public required Category Category { get; init; }
}
```

对于 `Update{Entity}Request` 记录，遵循相同的模式，添加更新所需的任何附加属性（例如 `IsAvailable`）。

**最小 API 验证 — 显式注册**：数据注解验证（`[Required]`、`[MaxLength]`、`[Range]` 等）在 MVC 控制器中自动执行，但最小 API 需要显式选择。对于 **.NET 10+** 使用最小 API 的项目，在 `Program.cs` 中添加验证服务：

```csharp
builder.Services.AddValidation();
```

这将连接一个端点过滤器，在处理程序执行之前验证带有数据注解的参数，并在失败时返回 `400 Bad Request` 以及包含验证问题详情的响应。

参考：https://learn.microsoft.com/aspnet/core/fundamentals/minimal-apis?view=aspnetcore-10.0

**不要**使用可变类（`{ get; set; }`）作为 DTO。可变 DTO 允许在构造后意外修改，并丢失记录提供的自我描述不可变性。

### 第 3 步：实现端点

无论使用控制器还是最小 API，始终一致地遵循这些 HTTP 约定。

**组织最小 API 端点**：对于使用最小 API 的项目，按资源组织端点，使用静态类和静态 `Map<Resource>` 方法。此模式将端点定义按资源类型分组，使代码更易于维护和导航，因为 API 随着时间的推移而增长。

**模式结构**：

1. 为每个资源创建一个静态类（例如，`ProductEndpoints`、`CategoryEndpoints`）。
2. 定义一个静态 `Map<Resource>(this WebApplication app)` 扩展方法。
3. 在方法内部，为该资源的端点调用 `MapGet`、`MapPost`、`MapPut`、`MapDelete` 等。
4. 在 `Program.cs` 中按顺序调用每个资源的 `Map` 方法。

**最小 API 返回类型 — 优先使用 `TypedResults`**：

始终优先使用 `TypedResults` 而不是 `Results` 工厂。`TypedResults` 将响应类型信息嵌入方法签名中，自动为 OpenAPI 生成器提供更丰富的元数据。

当处理程序返回**多个结果类型**（例如，`Ok` 或 `NotFound`）时，用显式的 `Results<T1, T2>` 返回类型注释 lambda。这允许您使用 `TypedResults`，同时仍然为编译器提供一个通用类型：

```csharp
async Task<Results<Ok<ProductResponse>, NotFound>> (int id, ...) => ...
```

**不要**在裸三元中没有显式返回类型注释的情况下使用 `TypedResults.Ok(x)` 和 `TypedResults.NotFound()`。`Ok<T>` 和 `NotFound` 是不同类型，编译器无法推断它们之间的共同基础，这会导致 `CS1593: Delegate 'RequestDelegate' does not take N arguments`，因为编译器回退到匹配 `RequestDelegate(HttpContext)`。

**后备 — `Results` 工厂**：如果处理程序具有许多条件分支（7+ 结果类型），您可以使用 `Results` 工厂（`Results.Ok()`、`Results.NotFound()`），它返回 `IResult`，牺牲编译时 OpenAPI 推断以简化签名。

**状态码**：

| 操作 | 成功 | 常见错误 |
|-----------|---------|---------------|
| GET（单个） | `200 OK` | `404 Not Found` |
| GET（列表） | `200 OK` | — |
| POST（创建） | `201 Created` 带有 `Location` 头 | `400 Bad Request`，`409 Conflict` |
| PUT（完整更新） | `200 OK` | `400 Bad Request`，`404 Not Found` |
| PATCH（部分/操作） | `200 OK` | `400 Bad Request`，`404 Not Found` |
| DELETE | `204 No Content` | `404 Not Found`，`409 Conflict` |

**POST 201 响应**：始终返回指向新创建资源的 `Location` 头。

- 控制器：使用 `CreatedAtAction(nameof(GetById), new { id = ... }, response)`
- 最小 API：使用 `TypedResults.Created($"/api/products/{id}", response)`

**CancellationToken**：在每个端点签名中接受 `CancellationToken`，并将其传递到所有异步调用（服务方法、EF Core 查询、`HttpClient` 调用）。这允许服务器在客户端断开连接时停止工作。

```csharp
// 控制器示例
[HttpGet("{id}")]
public async Task<ActionResult<ProductResponse>> GetById(
    int id, CancellationToken cancellationToken)
{
    var product = await _productService.GetByIdAsync(id, cancellationToken);
    return product is null ? NotFound() : Ok(product);
}

// 最小 API 示例 — 带有显式返回类型的 TypedResults（推荐）
app.MapGet("/api/products/{id}", async Task<Results<Ok<ProductResponse>, NotFound>> (
    int id, IProductService service, CancellationToken cancellationToken) =>
{
    var product = await service.GetByIdAsync(id, cancellationToken);
    return product is null ? TypedResults.NotFound() : TypedResults.Ok(product);
});
```

### 第 4 步：连接 OpenAPI

每个 ASP.NET Core Web API 都应有 OpenAPI 文档。在添加之前检查项目是否已配置 OpenAPI。

**对于 .NET 9+ 项目**，使用内置的 ASP.NET Core OpenAPI 支持（`builder.Services.AddOpenApi()` + `app.MapOpenApi()` 在开发中）。这就足够了 — 无需额外的包。

**不要**向 .NET 9+ 项目添加任何 `Swashbuckle.*` NuGet 包（`Swashbuckle.AspNetCore`、`Swashbuckle.AspNetCore.SwaggerUI`、`Swashbuckle.AspNetCore.SwaggerGen` 等）。Swashbuckle 与 .NET 9+ 和 .NET 10 OpenAPI 类型存在已知的兼容性问题。对于目标为 .NET 8 或更早版本的项目，Swashbuckle 是可以接受的。如果项目已安装 Swashbuckle，除非用户要求删除，否则保留它。

参考：https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/overview

**端点的 OpenAPI 元数据**：添加描述性元数据，以便生成的文档不仅是一系列路由，而且是实用的。对于最小 API，链接元数据方法：

```csharp
app.MapGet("/api/products/{id}", handler)
    .WithName("GetProductById")
    .WithSummary("通过 ID 获取产品")
    .WithDescription("返回完整的产品详细信息，包括类别。")
    .Produces<ProductResponse>(StatusCodes.Status200OK)
    .Produces(StatusCodes.Status404NotFound);
```

**枚举序列化（默认为字符串）**：配置 JSON 序列化，以便枚举在 API 响应和 OpenAPI 模式中作为可读字符串出现。除非用户明确要求整数枚举序列化，否则始终添加此配置。为最小 API 和控制器配置它，因为它们使用不同的选项类型：

```csharp
// 最小 API
builder.Services.ConfigureHttpJsonOptions(options =>
    options.SerializerOptions.Converters.Add(new JsonStringEnumConverter()));

// 控制器 / MVC
builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        options.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter());
    });
```

### 第 5 步：设置错误处理

使用全局异常处理程序，以便每个端点不需要 try-catch 块。为所有错误响应返回 RFC 7807 Problem Details。

**对于 .NET 8+ 项目**，优先使用内置的异常处理中间件：

```csharp
builder.Services.AddProblemDetails();

app.UseExceptionHandler();
app.UseStatusCodePages();
```

如果项目需要自定义异常到状态码映射（例如，`NotFoundException` 应返回 404），请实现 `IExceptionHandler`：

```csharp
internal sealed class ApiExceptionHandler(ILogger<ApiExceptionHandler> logger)
    : IExceptionHandler
{
    public async ValueTask<bool> TryHandleAsync(
        HttpContext httpContext,
        Exception exception,
        CancellationToken cancellationToken)
    {
        var (statusCode, title) = exception switch
        {
            KeyNotFoundException => (StatusCodes.Status404NotFound, "Not Found"),
            ArgumentException => (StatusCodes.Status400BadRequest, "Bad Request"),
            InvalidOperationException => (StatusCodes.Status409Conflict, "Conflict"),
            _ => (0, (string?)null)
        };

        if (statusCode == 0)
            return false; // 让默认处理程序处理它

        // 重要：返回 true 会抑制此异常的异常诊断中间件
        // 确保在返回之前记录/遥测它。
        logger.LogWarning(exception, "处理 API 异常：{Title}", title);

        httpContext.Response.StatusCode = statusCode;
        await httpContext.Response.WriteAsJsonAsync(new ProblemDetails
        {
            Status = statusCode,
            Title = title,
            // 不要在此处使用 exception.Message — 它可能会泄露敏感的内部详细信息。
            // 使用安全、面向用户的消息。
            Detail = title,
            Instance = httpContext.Request.Path
        }, cancellationToken);

        return true;
    }
}
```

注册它：

```csharp
builder.Services.AddExceptionHandler<ApiExceptionHandler>();
builder.Services.AddProblemDetails();

app.UseExceptionHandler();
```

**文件位置**：始终将异常处理程序类放在 `Middleware/` 文件夹中，以保持一致的项目组织。不要将它们放在项目根目录下。

### 第 6 步：使用服务层

不要将数据存储直接注入控制器或端点处理程序。创建一个服务接口和一个密封的实现类，该类拥有数据访问逻辑和实体与请求/响应类型之间的映射。

始终为每个服务定义一个接口 — 这使使用模拟进行单元测试成为可能，并遵循依赖倒置原则：

```csharp
// Services/IProductService.cs
public interface IProductService
{
    Task<IReadOnlyList<ProductResponse>> GetAllAsync(CancellationToken ct);
    Task<ProductResponse?> GetByIdAsync(int id, CancellationToken ct);
    Task<ProductResponse> CreateAsync(CreateProductRequest request, CancellationToken ct);
}

// Services/ProductService.cs
public sealed class ProductService(...) : IProductService
{
    // 数据访问逻辑，实体到 DTO 的映射
}
```

使用接口而不是具体类型进行注册：

```csharp
// 在 Program.cs 中
builder.Services.AddScoped<IProductService, ProductService>();
```

对于 EF Core 数据访问模式（迁移、Fluent API 配置、`AsNoTracking`、种子数据），请参阅 `optimizing-ef-core-queries` 技能。

### 第 7 步：创建 .http 测试文件

在实现端点后，在项目根目录创建一个 `.http` 文件，演示如何调用每个新端点。这作为活文档和快速手动测试工具。

```http
@baseUrl = http://localhost:5000

### 获取所有产品
GET {{baseUrl}}/api/products

### 通过 ID 获取产品
GET {{baseUrl}}/api/products/1

### 创建产品
POST {{baseUrl}}/api/products
Content-Type: application/json

{
  "name": "Wireless Mouse",
  "price": 29.99,
  "category": "Electronics"
}

### 删除产品
DELETE {{baseUrl}}/api/products/1
```

至少包含每个端点的一个请求，并使用现实的正文。显示错误路径（例如，不存在的 ID）。将端口与 `launchSettings.json` 匹配。

### 第 8 步：构建和验证

1. 运行 `dotnet build` — 确认零错误和零警告。
2. 启动应用程序并验证 OpenAPI 文档加载（默认：`/openapi/v1.json`）。
3. 运行 `.http` 文件中的请求，并确认正确的状态码。

## 验证

- [ ] 所有端点返回正确的 HTTP 状态码（根据第 3 步中的表格）
- [ ] POST 端点返回 `201 Created` 并带有 `Location` 头
- [ ] DELETE 端点返回 `204 No Content`
- [ ] 每个端点签名都包含 `CancellationToken`
- [ ] `CancellationToken` 被传递到所有下游异步调用
- [ ] 生成了 OpenAPI 文档并包含所有新端点
- [ ] 端点有 OpenAPI 的摘要/描述元数据
- [ ] 枚举值在 JSON 响应和 OpenAPI 模式中作为字符串出现（除非用户明确要求整数序列化）
- [ ] 错误响应使用 RFC 7807 Problem Details 格式
- [ ] 域实体没有直接在 API 请求/响应正文中暴露
- [ ] 所有 API 暴露的 DTO 都有 `<summary>` XML 文档注释
- [ ] 日期和时间属性使用 `DateTimeOffset`，而不是 `DateTime`
- [ ] 存在一个 `.http` 文件，其中包含每个新端点的请求
- [ ] `dotnet build` 通过，零错误和零警告
- [ ] 所有 DTO 都是 `sealed record` 类型（不是可变类）
- [ ] 最小 API 处理程序使用带有显式 `Results<T1, T2>` 返回类型的 `TypedResults`
- [ ] 每个服务都有一个对应的接口在 DI 中注册
- [ ] 异常处理程序位于 `Middleware/` 文件夹中

## 常见陷阱

| 陷阱 | 解决方案 |
|---------|----------|
| 将域实体作为 API 响应暴露 | 创建单独的 `sealed record` 请求/响应类型。实体会泄露导航属性和内部字段。 |
| 遗忘 `CancellationToken` | 在每个端点中添加，并通过整个异步调用链传递。 |
| 从 POST 创建返回 `200 OK` | 返回 `201 Created` 并带有 `Location` 头。 |
| 缺少 OpenAPI 元数据 | 在每个端点上链接 `.WithName()`、`.WithSummary()`、`.WithDescription()`、`.Produces<T>()`。 |
| 直接将数据存储注入端点 | 使用服务层和接口进行分离和可测试性。 |
| 混合控制器和最小 API 风格 | 在每个项目中选择一个，并保持一致性。 |
| 在三元中没有显式返回类型的 `TypedResults` | `Ok<T>` 和 `NotFound` 没有共同基础 — 注释为 `Task<Results<Ok<T>, NotFound>>` 或回退到 `Results` 工厂。 |
| 使用可变类作为 DTO | 使用 `sealed record` 带有位置语法（响应）或 `init` 属性（请求）。 |
| 未使用接口注册服务 | 定义 `IService` 并注册为 `AddScoped<IService, Service>()`。 |
| 向新 .NET 9+ 项目添加任何 `Swashbuckle.*` 包 | 使用内置的 `AddOpenApi()` + `MapOpenApi()`。不要添加 `Swashbuckle.AspNetCore`、`Swashbuckle.AspNetCore.SwaggerUI` 或任何其他 Swashbuckle 包。 |
| 缺少 DTO 的 XML 文档注释 | 为每个请求和响应类型添加 `<summary>` XML 文档注释。这些会自动流入生成的 OpenAPI 规范中。 |
| 使用 `DateTime` 作为日期/时间属性 | 使用 `DateTimeOffset` 而不是 — 它保留 UTC 偏移量，避免时区模糊，并在 JSON 中正确序列化。 |
| 将枚举按整数序列化 | 配置 `JsonStringEnumConverter` 以便枚举默认按字符串序列化。只有在用户明确要求时才使用整数序列化。 |

## 更多信息

- [ASP.NET Core Web API 概述](https://learn.microsoft.com/en-us/aspnet/core/web-api/) — 构建 Web API 的基本概念
- [ASP.NET Core 中的 OpenAPI](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/overview) — .NET 9+ 中内置的 OpenAPI 支持
- [从 XML 文档生成 OpenAPI](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/openapi-comments) — XML 文档注释如何流入 OpenAPI 规范
- [最小 API 概述](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/overview) — 路由、参数绑定和响应类型
- [在 ASP.NET Core API 中处理错误](https://learn.microsoft.com/en-us/aspnet/core/web-api/handle-errors) — Problem Details 和异常处理
- [DateTimeOffset](https://learn.microsoft.com/en-us/dotnet/api/system.datetimeoffset) — API 中日期/时间值的推荐类型
