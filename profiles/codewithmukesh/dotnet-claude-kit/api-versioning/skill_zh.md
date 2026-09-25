# API 版本控制

## 核心原则

1. **从一开始就进行版本控制** — 后续添加版本控制会非常痛苦。即使只有 v1 版本，也要在 URL 中使用版本号。
2. **URL 段版本控制是默认方式** — `/api/v1/orders` 是最易于发现且对缓存友好的策略。
3. **不要破坏现有版本** — 对破坏性变更添加新版本。为旧版本设置弃用时间表。
4. **对 API 进行版本控制，而不是单个端点** — 同一版本组内的所有端点共享相同的版本号。

## 模式

### 使用 Asp.Versioning 进行设置

```csharp
// Program.cs
builder.Services.AddApiVersioning(options =>
{
    options.DefaultApiVersion = new ApiVersion(1, 0);
    options.AssumeDefaultVersionWhenUnspecified = true;
    options.ReportApiVersions = true;
    options.ApiVersionReader = new UrlSegmentApiVersionReader();
})
.AddApiExplorer(options =>
{
    options.GroupNameFormat = "'v'VVV";
    options.SubstituteApiVersionInUrl = true;
});
```

### URL 段版本控制（推荐）

```csharp
var v1 = app.NewApiVersionSet()
    .HasApiVersion(new ApiVersion(1, 0))
    .Build();

var v2 = app.NewApiVersionSet()
    .HasApiVersion(new ApiVersion(2, 0))
    .Build();

app.MapGroup("/api/v{version:apiVersion}/orders")
    .WithApiVersionSet(v1)
    .WithTags("订单")
    .MapOrderEndpointsV1();

app.MapGroup("/api/v{version:apiVersion}/orders")
    .WithApiVersionSet(v2)
    .WithTags("订单")
    .MapOrderEndpointsV2();
```

### 头部版本控制（替代方案）

```csharp
options.ApiVersionReader = new HeaderApiVersionReader("X-Api-Version");

// 客户端发送：X-Api-Version: 2.0
```

### 弃用版本

```csharp
var v1 = app.NewApiVersionSet()
    .HasDeprecatedApiVersion(new ApiVersion(1, 0))
    .HasApiVersion(new ApiVersion(2, 0))
    .Build();

// 响应头将包含：api-deprecated-versions: 1.0
```

### 版本特定端点组

```csharp
public static class OrderEndpointsV1
{
    public static RouteGroupBuilder MapOrderEndpointsV1(this RouteGroupBuilder group)
    {
        group.MapGet("/{id:guid}", GetOrderV1);
        group.MapPost("/", CreateOrderV1);
        return group;
    }

    private static async Task<Results<Ok<OrderResponseV1>, NotFound>> GetOrderV1(
        Guid id, ISender sender, CancellationToken ct)
    {
        // v1 响应结构
        var result = await sender.Send(new GetOrder.Query(id), ct);
        return result.IsSuccess
            ? TypedResults.Ok(result.Value.ToV1())
            : TypedResults.NotFound();
    }
}

public static class OrderEndpointsV2
{
    public static RouteGroupBuilder MapOrderEndpointsV2(this RouteGroupBuilder group)
    {
        group.MapGet("/{id:guid}", GetOrderV2);
        group.MapPost("/", CreateOrderV2);
        return group;
    }

    private static async Task<Results<Ok<OrderResponseV2>, NotFound>> GetOrderV2(
        Guid id, ISender sender, CancellationToken ct)
    {
        // v2 响应结构 — 包含新字段
        var result = await sender.Send(new GetOrder.Query(id), ct);
        return result.IsSuccess
            ? TypedResults.Ok(result.Value.ToV2())
            : TypedResults.NotFound();
    }
}
```

## 反模式

### 不要单独版本化端点

```csharp
// BAD — 组内版本不一致
app.MapGet("/api/v1/orders", ListOrdersV1);
app.MapGet("/api/v2/orders/{id}", GetOrderV2); // 仅此端点使用 v2？

// GOOD — 整组版本化
app.MapGroup("/api/v1/orders").MapOrderEndpointsV1();
app.MapGroup("/api/v2/orders").MapOrderEndpointsV2();
```

### 不要将查询字符串版本作为默认方式

```csharp
// BAD for REST APIs — 版本隐藏在查询字符串中，不利于缓存
GET /api/orders?api-version=2.0

// GOOD — URL 中包含版本，易于发现且可缓存
GET /api/v2/orders
```

## 决策指南

| 场景 | 建议 |
|------|------|
| 新的公共 API | 从一开始就使用 URL 段版本控制 |
| 服务间内部 API | 头部版本控制（更干净的 URL） |
| 破坏性响应结构变更 | 新版本 |
| 添加新的可选字段 | 同一版本（向后兼容） |
| 弃用版本 | 标记为弃用，设置失效日期，记录迁移路径 |
