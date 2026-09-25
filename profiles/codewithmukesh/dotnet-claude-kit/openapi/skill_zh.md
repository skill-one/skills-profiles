# OpenAPI

## 核心原则

1. **内置而非 Swashbuckle** — .NET 10 将 `Microsoft.AspNetCore.OpenApi` 作为官方的、由框架维护的 OpenAPI 解决方案一同发布。Swashbuckle 已从 .NET 9 模板中移除，不再推荐使用。
2. **TypedResults 驱动模式** — `TypedResults.Ok<T>()` 会自动生成正确的 OpenAPI 响应模式。`Results.Ok()` 则不会。始终使用 `TypedResults`。
3. **转换器优于解决方案** — 文档、操作和模式转换器可以干净地组合。使用它们来处理安全方案、全局响应和模式自定义。
4. **每个端点都有元数据** — 在每个端点上使用 `.WithName()`, `.WithSummary()`, `.WithTags()`。这些元数据会直接输入 OpenAPI 规范和客户端生成器。

## 模式

### 基本设置

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddOpenApi();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();  // 服务于 /openapi/v1.json
}
```

### 端点元数据

```csharp
group.MapPost("/", CreateOrder)
    .WithName("CreateOrder")
    .WithSummary("创建新订单")
    .WithDescription("为指定客户创建新订单。")
    .Produces<OrderResponse>(StatusCodes.Status201Created)
    .ProducesValidationProblem()
    .ProducesProblem(StatusCodes.Status500InternalServerError);
```

使用 `TypedResults`，响应元数据会自动推断：

```csharp
static async Task<Results<Created<OrderResponse>, ValidationProblem>> CreateOrder(
    CreateOrderRequest request, ISender sender, CancellationToken ct)
{
    var result = await sender.Send(new CreateOrder.Command(request), ct);
    return result.IsSuccess
        ? TypedResults.Created($"/api/orders/{result.Value.Id}", result.Value)
        : TypedResults.ValidationProblem(result.Errors);
}
```

### Bearer Token 安全方案

```csharp
builder.Services.AddOpenApi(options =>
{
    options.AddDocumentTransformer<BearerSecuritySchemeTransformer>();
});

internal sealed class BearerSecuritySchemeTransformer(
    IAuthenticationSchemeProvider authSchemeProvider) : IOpenApiDocumentTransformer
{
    public async Task TransformAsync(OpenApiDocument document,
        OpenApiDocumentTransformerContext context, CancellationToken ct)
    {
        var schemes = await authSchemeProvider.GetAllSchemesAsync();
        if (!schemes.Any(s => s.Name == "Bearer"))
            return;

        document.Components ??= new OpenApiComponents();
        document.Components.SecuritySchemes = new Dictionary<string, IOpenApiSecurityScheme>
        {
            ["Bearer"] = new OpenApiSecurityScheme
            {
                Type = SecuritySchemeType.Http,
                Scheme = "bearer",
                BearerFormat = "JWT",
                In = ParameterLocation.Header
            }
        };

        foreach (var operation in document.Paths.Values.SelectMany(p => p.Operations))
        {
            operation.Value.Security ??= [];
            operation.Value.Security.Add(new OpenApiSecurityRequirement
            {
                [new OpenApiSecuritySchemeReference("Bearer", document)] = []
            });
        }
    }
}
```

### 文档信息转换器

```csharp
builder.Services.AddOpenApi(options =>
{
    options.AddDocumentTransformer((document, context, ct) =>
    {
        document.Info = new()
        {
            Title = "结算 API",
            Version = "v1",
            Description = "处理订单和支付的 API。"
        };
        return Task.CompletedTask;
    });
});
```

### 多个 OpenAPI 文档

```csharp
builder.Services.AddOpenApi("v1");
builder.Services.AddOpenApi("internal", options =>
{
    options.AddDocumentTransformer<BearerSecuritySchemeTransformer>();
});

// 端点通过 WithGroupName 选择其文档
app.MapGet("/public", () => "Hello").WithGroupName("v1");
app.MapGet("/admin", () => "Secret").WithGroupName("internal");
```

没有 `.WithGroupName()` 的端点会出现在所有文档中。

### XML 文档注释 (.NET 10)

在项目文件中启用 — 源生成器会自动提取 `<summary>`、`<param>`、`<response>` 标签：

```xml
<PropertyGroup>
    <GenerateDocumentationFile>true</GenerateDocumentationFile>
</PropertyGroup>
```

```csharp
/// <summary>通过 ID 获取项目看板。</summary>
/// <param name="id">项目看板 ID。</param>
/// <response code="200">返回项目看板。</response>
/// <response code="404">看板未找到。</response>
static async Task<Results<Ok<Board>, NotFound>> GetBoard(int id, AppDbContext db)
{
    var board = await db.Boards.FindAsync(id);
    return board is not null ? TypedResults.Ok(board) : TypedResults.NotFound();
}
```

Lambda 表达式上的 XML 注释不会被编译器捕获。使用命名方法。

### 模式转换器

```csharp
options.AddSchemaTransformer((schema, context, ct) =>
{
    if (context.JsonTypeInfo.Type == typeof(decimal))
    {
        schema.Format = "decimal";
    }
    return Task.CompletedTask;
});
```

### 端点操作转换器 (.NET 10)

```csharp
app.MapGet("/old", () => "已弃用")
    .AddOpenApiOperationTransformer((operation, context, ct) =>
    {
        operation.Deprecated = true;
        return Task.CompletedTask;
    });
```

### 构建时文档生成

```xml
<PackageReference Include="Microsoft.Extensions.ApiDescription.Server" Version="*" />
<PropertyGroup>
    <OpenApiDocumentsDirectory>.</OpenApiDocumentsDirectory>
</PropertyGroup>
```

规范文件会在构建时生成在输出目录中。

### YAML 端点 (.NET 10)

```csharp
app.MapOpenApi("/openapi/{documentName}.yaml");
```

## 反模式

### 新项目不要使用 Swashbuckle

```csharp
// BAD — 已从 .NET 9+ 模板中移除，维护问题
builder.Services.AddSwaggerGen();
app.UseSwagger();
app.UseSwaggerUI();

// GOOD — 内置 OpenAPI
builder.Services.AddOpenApi();
app.MapOpenApi();
```

### .NET 10 不要使用 WithOpenApi()

```csharp
// BAD — 已弃用，产生 ASPDEPR002 警告
app.MapGet("/", () => "hello").WithOpenApi(op => { op.Deprecated = true; return op; });

// GOOD — 使用端点操作转换器
app.MapGet("/", () => "hello")
    .AddOpenApiOperationTransformer((op, ctx, ct) =>
    {
        op.Deprecated = true;
        return Task.CompletedTask;
    });
```

### 不要使用未类型化的结果

```csharp
// BAD — Results.Ok 不会对 OpenAPI 模式做出贡献
static async Task<IResult> GetOrder(Guid id, AppDbContext db)
{
    var order = await db.Orders.FindAsync(id);
    return order is not null ? Results.Ok(order) : Results.NotFound();
}

// GOOD — 使用带联合返回类型的 TypedResults
static async Task<Results<Ok<Order>, NotFound>> GetOrder(Guid id, AppDbContext db)
{
    var order = await db.Orders.FindAsync(id);
    return order is not null ? TypedResults.Ok(order) : TypedResults.NotFound();
}
```

### 端点不要跳过 WithName

```csharp
// BAD — 客户端生成器在没有 operationId 的情况下会生成较差的方法名
group.MapGet("/{id:guid}", GetOrder);

// GOOD — operationId 会输入生成的客户端方法名
group.MapGet("/{id:guid}", GetOrder).WithName("GetOrder");
```

### .NET 10 不要使用 OpenApiAny

```csharp
// BAD — Microsoft.OpenApi v2.x 中已移除 OpenApiAny 类型
schema.Example = new OpenApiString("2025-01-01");

// GOOD — 使用 System.Text.Json.Nodes 中的 JsonValue
schema.Example = JsonValue.Create("2025-01-01");
```

## 决策指南

| 场景 | 建议 |
|------|------|
| 新 API 项目 | `AddOpenApi()` + `MapOpenApi()` (内置) |
| API 文档 UI | Scalar (`MapScalarApiReference()`) |
| 文档中的安全方案 | 使用 `IOpenApiDocumentTransformer` 的文档转换器 |
| 响应文档 | 使用带联合返回类型的 `TypedResults` |
| XML 文档集成 | `<GenerateDocumentationFile>true</GenerateDocumentationFile>` |
| 多个 API 版本 | 多次调用 `AddOpenApi("v1")` + `WithGroupName()` |
| 客户端代码生成 | Kiota (微软推荐) 或 NSwag |
| 构建时规范 | `Microsoft.Extensions.ApiDescription.Server` 包 |
| OpenAPI 版本 | 3.1 (.NET 10 默认)，如果消费者需要 3.0 则强制指定 |
| 端点自定义 | 在端点上使用 `.AddOpenApiOperationTransformer()` |
