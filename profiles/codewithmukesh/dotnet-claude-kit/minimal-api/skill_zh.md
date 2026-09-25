# 最小API (.NET 10)

## 核心原则

1. **最小API是默认选择** — 仅在迁移遗留代码时使用控制器。最小API更轻量、更快，并且能与任何架构风格良好组合。
2. **使用`MapGroup`分组端点** — 不要在`Program.cs`中分散`MapGet`/`MapPost`调用。将相关端点组合在一起。
3. **使用`TypedResults`生成OpenAPI** — `TypedResults.Ok(value)`提供编译时类型安全性和正确的OpenAPI文档。`Results.Ok(value)`则不提供。
4. **元数据优于注释** — 使用`.WithName()`、`.WithTags()`、`.WithSummary()`来记录端点。元数据会输入OpenAPI规范。

## 模式

### 端点分组自动发现（必需模式）

每个端点分组都位于自己的文件中，并实现`IEndpointGroup`。`Program.cs`中的单个`app.MapEndpoints()`调用会自动发现并注册所有分组。**添加新的端点分组时，`Program.cs`永远不会改变。**

```csharp
// 扩展/IEndpointGroup.cs
public interface IEndpointGroup
{
    void Map(IEndpointRouteBuilder app);
}
```

```csharp
// 扩展/EndpointExtensions.cs
public static class EndpointExtensions
{
    public static WebApplication MapEndpoints(this WebApplication app)
    {
        var groups = typeof(Program).Assembly
            .GetTypes()
            .Where(t => t.IsAssignableTo(typeof(IEndpointGroup)) && !t.IsInterface && !t.IsAbstract)
            .Select(Activator.CreateInstance)
            .Cast<IEndpointGroup>();

        foreach (var group in groups)
            group.Map(app);

        return app;
    }
}
```

```csharp
// Program.cs — 添加端点时此文件永远不会改变
var app = builder.Build();
app.MapEndpoints();
app.Run();
```

```csharp
// 功能/订单/OrderEndpoints.cs — 每个端点分组一个文件
public sealed class OrderEndpoints : IEndpointGroup
{
    public void Map(IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/orders").WithTags("订单");

        group.MapPost("/", CreateOrder)
            .WithName("CreateOrder")
            .WithSummary("创建新订单")
            .Produces<OrderResponse>(StatusCodes.Status201Created)
            .ProducesValidationProblem()
            .RequireAuthorization();

        group.MapGet("/{id:guid}", GetOrder)
            .WithName("GetOrder")
            .Produces<OrderResponse>()
            .ProducesProblem(StatusCodes.Status404NotFound);

        group.MapGet("/", ListOrders)
            .WithName("ListOrders")
            .Produces<PagedList<OrderResponse>>();
    }

    private static async Task<Results<Created<OrderResponse>, ValidationProblem>> CreateOrder(
        CreateOrderRequest request,
        ISender sender,
        CancellationToken ct)
    {
        var result = await sender.Send(new CreateOrder.Command(request.CustomerId, request.Items), ct);
        return result.IsSuccess
            ? TypedResults.Created($"/api/orders/{result.Value.Id}", result.Value)
            : TypedResults.ValidationProblem(result.Errors);
    }

    private static async Task<Results<Ok<OrderResponse>, NotFound>> GetOrder(
        Guid id,
        ISender sender,
        CancellationToken ct)
    {
        var result = await sender.Send(new GetOrder.Query(id), ct);
        return result.IsSuccess
            ? TypedResults.Ok(result.Value)
            : TypedResults.NotFound();
    }

    private static async Task<Ok<PagedList<OrderResponse>>> ListOrders(
        [AsParameters] ListOrdersQuery query,
        ISender sender,
        CancellationToken ct)
    {
        var result = await sender.Send(query, ct);
        return TypedResults.Ok(result);
    }
}
```

### 使用`TypedResults`实现类型安全的响应

`TypedResults`提供编译时保证并自动生成OpenAPI模式。

```csharp
// 良好实践 — 使用联合返回类型
private static async Task<Results<Ok<Product>, NotFound, ValidationProblem>> GetProduct(
    Guid id,
    AppDbContext db,
    CancellationToken ct)
{
    var product = await db.Products.FindAsync([id], ct);
    return product is not null
        ? TypedResults.Ok(product)
        : TypedResults.NotFound();
}
```

### 参数绑定

.NET 10最小API自动从路由、查询、头部、正文和依赖注入中绑定参数。

```csharp
// 路由参数
app.MapGet("/orders/{id:guid}", (Guid id) => ...);

// 查询参数（可空 = 可选）
app.MapGet("/orders", (int page, int? pageSize, string? status) => ...);

// 复杂查询参数使用[AsParameters]
public record ListOrdersQuery(int Page = 1, int PageSize = 20, string? Status = null);
app.MapGet("/orders", ([AsParameters] ListOrdersQuery query) => ...);

// 头部绑定
app.MapGet("/orders", ([FromHeader(Name = "X-Correlation-Id")] string? correlationId) => ...);

// DI服务自动解析（无需属性）
app.MapPost("/orders", (CreateOrderRequest request, ISender sender) => ...);
```

### 端点过滤器

过滤器是最小API中动作过滤器的等效物。用于跨领域关注点，如验证、日志记录和幂等性检查。

标准的`ValidationFilter<TRequest>`实现（FluentValidation，从DI解析验证器并在未注册时优雅跳过）位于**错误处理**技能中 — 使用这个实现，不要每个项目重新实现。

```csharp
// 将标准过滤器（见错误处理技能）应用于可变端点
group.MapPost("/", CreateOrder)
    .AddEndpointFilter<ValidationFilter<CreateOrderRequest>>();

// 将过滤器应用于分组（影响分组中的所有端点）
group.AddEndpointFilter<LoggingFilter>();
```

### OpenAPI / Swagger配置

.NET 10具有内置的OpenAPI支持。使用它替代Swashbuckle。

```csharp
// Program.cs — 仅服务注册，无端点连接
builder.Services.AddOpenApi();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}
app.MapEndpoints(); // 自动发现所有IEndpointGroup实现

// 端点元数据丰富OpenAPI规范
group.MapPost("/", CreateOrder)
    .WithName("CreateOrder")
    .WithSummary("创建新订单")
    .WithDescription("为指定客户创建新订单，包含给定行项目。")
    .Produces<OrderResponse>(StatusCodes.Status201Created)
    .ProducesValidationProblem()
    .ProducesProblem(StatusCodes.Status500InternalServerError);
```

### 速率限制

```csharp
builder.Services.AddRateLimiter(options =>
{
    options.AddFixedWindowLimiter("api", opt =>
    {
        opt.PermitLimit = 100;
        opt.Window = TimeSpan.FromMinutes(1);
    });
});

// 在IEndpointGroup.Map方法中应用
var group = app.MapGroup("/api/orders")
    .WithTags("订单")
    .RequireRateLimiting("api");
```

### 输出缓存

```csharp
builder.Services.AddOutputCache(options =>
{
    options.AddBasePolicy(builder => builder.Expire(TimeSpan.FromMinutes(5)));
    options.AddPolicy("ByIdCache", builder => builder
        .Expire(TimeSpan.FromMinutes(10))
        .SetVaryByRouteValue("id"));
});

group.MapGet("/{id:guid}", GetOrder)
    .CacheOutput("ByIdCache");
```

## 反模式

### 不要在Program.cs中放置端点

```csharp
// 不好 — 端点分散在Program.cs中
app.MapGet("/orders", async (AppDbContext db) => await db.Orders.ToListAsync());
app.MapGet("/orders/{id}", async (Guid id, AppDbContext db) => await db.Orders.FindAsync(id));
app.MapPost("/orders", async (Order order, AppDbContext db) => { /* ... */ });
app.MapGet("/products", async (AppDbContext db) => await db.Products.ToListAsync());

// 同样不好 — Program.cs中手动调用MapGroup（随功能增长）
app.MapGroup("/api/orders").WithTags("订单").MapOrderEndpoints();
app.MapGroup("/api/products").WithTags("产品").MapProductEndpoints();
app.MapGroup("/api/customers").WithTags("客户").MapCustomerEndpoints();
// 每次添加功能时Program.cs都会增长...

// 良好实践 — 自动发现，Program.cs不变
app.MapEndpoints(); // 发现所有IEndpointGroup实现
```

### 不要使用未分类结果

```csharp
// 不好 — Results.Ok不贡献OpenAPI模式
private static async Task<IResult> GetOrder(Guid id, AppDbContext db)
{
    var order = await db.Orders.FindAsync(id);
    return order is not null ? Results.Ok(order) : Results.NotFound();
}

// 良好实践 — 使用显式联合类型
private static async Task<Results<Ok<Order>, NotFound>> GetOrder(Guid id, AppDbContext db)
{
    var order = await db.Orders.FindAsync(id);
    return order is not null ? TypedResults.Ok(order) : TypedResults.NotFound();
}
```

### 不要直接返回领域实体

```csharp
// 不好 — 泄露内部结构，无法独立演进
app.MapGet("/orders/{id}", async (Guid id, AppDbContext db) =>
    await db.Orders.Include(o => o.Items).FirstOrDefaultAsync(o => o.Id == id));

// 良好实践 — 映射到响应DTO
app.MapGet("/orders/{id}", async (Guid id, AppDbContext db) =>
{
    var order = await db.Orders
        .Where(o => o.Id == id)
        .Select(o => new OrderResponse(o.Id, o.Total, o.CreatedAt))
        .FirstOrDefaultAsync();
    return order is not null ? TypedResults.Ok(order) : TypedResults.NotFound();
});
```

## 决策指南

| 场景 | 建议 |
|------|------|
| 新HTTP API | 每个功能一个`IEndpointGroup` + `app.MapEndpoints()`自动发现 |
| 现有MVC项目 | 保持控制器，逐步迁移 |
| OpenAPI文档 | 使用`TypedResults` + `.WithName()` + `.WithSummary()` |
| 请求验证 | 使用FluentValidation的端点过滤器 |
| 身份验证/授权 | 在分组或端点上使用`.RequireAuthorization("PolicyName")` |
| 速率限制 | `AddRateLimiter` + `.RequireRateLimiting()` |
| 响应缓存 | `AddOutputCache` + `.CacheOutput()` |
| 复杂模型绑定 | 使用记录类型的`[AsParameters]` |
