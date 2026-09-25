# 垂直切片架构 (VSA)

## 核心原则

1. **按功能组织，而非按层级** — 每个功能是一个自包含的垂直切片，包含其端点、处理器、请求/响应类型和验证。不再需要在 Controllers/、Services/、Repositories/ 文件夹之间跳转。
2. **最小化跨功能耦合** — 功能不应直接引用其他功能。共同关注点放在 `Common/` 或 `Shared/` 目录中。
3. **每个功能一个文件即可** — 简单的 CRUD 端点不需要 5 个分散在各个层级的文件。从所有内容放在一个文件开始，仅在复杂性要求时提取。
4. **处理器是工作单元** — 每个处理器只做一件事。没有包含 20 个方法的神级服务。

## 模式

### 功能文件夹结构

```
src/
  MyApp.Api/
    Features/
      Orders/
        CreateOrder.cs          # 请求、处理器、响应、端点 — 全部在一个文件中
        GetOrder.cs
        ListOrders.cs
        CancelOrder.cs
        Shared/
          OrderMapper.cs        # 仅在 Orders 功能内部共享
      Products/
        CreateProduct.cs
        GetProduct.cs
    Common/
      Behaviors/
        ValidationBehavior.cs   # 跨切面中介管道行为
      Persistence/
        AppDbContext.cs
      Extensions/
        ServiceCollectionExtensions.cs
    Program.cs
```

### 模式 A：中介处理器（推荐默认）

源生成中介 — MIT 许可证，无反射，原生 AOT 兼容。使用 `IRequest<T>` / `IRequestHandler<TRequest, TResponse>` 与管道行为。与 MediatR 几乎相同的 API 但更快且免费。包：`Mediator.Abstractions` + `Mediator.SourceGenerator`。

```csharp
// Features/Orders/CreateOrder.cs

public static class CreateOrder
{
    public record Command(string CustomerId, List<OrderItemDto> Items) : IRequest<Result<OrderResponse>>;

    public record OrderItemDto(string ProductId, int Quantity);

    public record OrderResponse(Guid Id, decimal Total, DateTime CreatedAt);

    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(x => x.CustomerId).NotEmpty();
            RuleFor(x => x.Items).NotEmpty();
            RuleForEach(x => x.Items).ChildRules(item =>
            {
                item.RuleFor(x => x.ProductId).NotEmpty();
                item.RuleFor(x => x.Quantity).GreaterThan(0);
            });
        }
    }

    internal sealed class Handler(AppDbContext db, TimeProvider clock) : IRequestHandler<Command, Result<OrderResponse>>
    {
        public async ValueTask<Result<OrderResponse>> Handle(Command request, CancellationToken ct)
        {
            var order = Order.Create(request.CustomerId, request.Items, clock.GetUtcNow());
            db.Orders.Add(order);
            await db.SaveChangesAsync(ct);

            return Result.Success(new OrderResponse(order.Id, order.Total, order.CreatedAt));
        }
    }
}

// 在 Program.cs 或模块 DI 中注册
builder.Services.AddMediator();

// Features/Orders/OrderEndpoints.cs — 自动发现 via IEndpointGroup
public sealed class OrderEndpoints : IEndpointGroup
{
    public void Map(IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/orders").WithTags("Orders");

        group.MapPost("/", async (CreateOrder.Command command, ISender sender, CancellationToken ct) =>
        {
            var result = await sender.Send(command, ct);
            return result.IsSuccess
                ? TypedResults.Created($"/api/orders/{result.Value.Id}", result.Value)
                : result.ToProblemDetails();
        })
        .WithName("CreateOrder").Produces<CreateOrder.OrderResponse>(201)
        .ProducesValidationProblem()
        .AddEndpointFilter<ValidationFilter<CreateOrder.Command>>();
    }
}
```

### 模式 B：Wolverine 处理器

基于约定 — 无需实现接口。Wolverine 通过方法签名发现处理器。

```csharp
// Features/Orders/CreateOrder.cs

public static class CreateOrder
{
    public record Command(string CustomerId, List<OrderItemDto> Items);

    public record OrderItemDto(string ProductId, int Quantity);

    public record OrderResponse(Guid Id, decimal Total, DateTime CreatedAt);

    // Wolverine 通过约定发现此方法 (静态 Handle 方法)
    public static async Task<Result<OrderResponse>> Handle(
        Command command,
        AppDbContext db,
        TimeProvider clock,
        CancellationToken ct)
    {
        var order = Order.Create(command.CustomerId, command.Items, clock.GetUtcNow());
        db.Orders.Add(order);
        await db.SaveChangesAsync(ct);
        return Result.Success(new OrderResponse(order.Id, order.Total, order.CreatedAt));
    }
}
```

### 模式 C：原始处理器类（无库依赖）

无外部依赖的直接处理器类。适合小型项目或希望完全控制的团队。

```csharp
// Features/Orders/CreateOrder.cs

public static class CreateOrder
{
    public record Command(string CustomerId, List<OrderItemDto> Items);

    public record OrderItemDto(string ProductId, int Quantity);

    public record OrderResponse(Guid Id, decimal Total, DateTime CreatedAt);

    internal class Handler(AppDbContext db, TimeProvider clock)
    {
        public async Task<Result<OrderResponse>> ExecuteAsync(Command command, CancellationToken ct)
        {
            var order = Order.Create(command.CustomerId, command.Items, clock.GetUtcNow());
            db.Orders.Add(order);
            await db.SaveChangesAsync(ct);

            return Result.Success(new OrderResponse(order.Id, order.Total, order.CreatedAt));
        }
    }
}

// 端点连接 — Result 映射到 HTTP 响应
group.MapPost("/", async (CreateOrder.Command command, CreateOrder.Handler handler, CancellationToken ct) =>
{
    var result = await handler.ExecuteAsync(command, ct);
    return result.IsSuccess
        ? TypedResults.Created($"/api/orders/{result.Value.Id}", result.Value)
        : result.ToProblemDetails();
});
```

### 添加模块边界（可选）

对于规模超出单个项目的应用程序，引入模块边界。每个模块是一个独立的类库，拥有自己的功能和 DbContext。

```
src/
  MyApp.Api/                      # 主机 — 连接模块
    Program.cs
    Modules/
      ModuleExtensions.cs         # app.MapOrderModule(), app.MapCatalogModule()
  MyApp.Orders/                   # 模块 — 自己的功能，自己的 DbContext
    Features/
      CreateOrder.cs
    Persistence/
      OrdersDbContext.cs
    OrdersModule.cs               # IServiceCollection + IEndpointRouteBuilder 扩展
  MyApp.Catalog/                  # 模块
    Features/
      CreateProduct.cs
    Persistence/
      CatalogDbContext.cs
    CatalogModule.cs
```

模块通过以下方式通信：
- **集成事件**（推荐）— 异步、通过 Wolverine 或 MassTransit 解耦
- **共享契约** — `MyApp.Contracts` 项目中的 DTO 接口（谨慎使用）

### 共同关注点

跨切面关注点位于功能文件夹之外：

```csharp
// Common/Behaviors/ValidationBehavior.cs (Mediator 管道)
public sealed class ValidationBehavior<TRequest, TResponse>(IEnumerable<IValidator<TRequest>> validators)
    : IPipelineBehavior<TRequest, TResponse>
    where TRequest : IMessage
{
    public async ValueTask<TResponse> Handle(
        TRequest request,
        MessageHandlerDelegate<TRequest, TResponse> next,
        CancellationToken ct)
    {
        var context = new ValidationContext<TRequest>(request);
        var failures = validators
            .Select(v => v.Validate(context))
            .SelectMany(r => r.Errors)
            .Where(f => f is not null)
            .ToList();

        if (failures.Count > 0)
            throw new ValidationException(failures);

        return await next(request, ct);
    }
}
```

## 反模式

### 不要在切片内创建分层抽象

```csharp
// BAD — 一个包含自己的服务层和仓库的功能文件夹
Features/
  Orders/
    CreateOrder.cs
    IOrderService.cs         # 不必要的抽象
    OrderService.cs          # 不必要的抽象
    IOrderRepository.cs      # 不必要的抽象
    OrderRepository.cs       # 不必要的抽象

// GOOD — 处理器直接与 DbContext 通信
Features/
  Orders/
    CreateOrder.cs           # 处理器直接使用 AppDbContext
```

### 不要直接引用功能

```csharp
// BAD — CreateOrder 直接调用 GetProduct 处理器
var product = await _getProductHandler.Handle(new GetProduct.Query(productId));

// GOOD — 直接查询数据库或使用共享读取模型
var product = await db.Products.FindAsync(productId, ct);
```

### 不要将所有内容放在一个神级功能文件中

```csharp
// BAD — 500 行文件包含 CRUD + 业务逻辑 + 映射
public static class Orders
{
    // Create, Read, Update, Delete, Cancel, Refund, Export...
}

// GOOD — 每个操作一个文件
Features/Orders/CreateOrder.cs
Features/Orders/GetOrder.cs
Features/Orders/CancelOrder.cs
```

## 决策指南

| 场景 | 推荐 |
|------|------|
| 新项目（默认） | 模式 A — 中介（源生成，MIT，快速） |
| 需要中介 + 消息传递在一个库中 | 模式 B — Wolverine（也处理事件/队列） |
| 想完全控制，无依赖 | 模式 C — 原始处理器类 |
| 现有 MediatR 代码库且已获许可 | 如果有许可则保留 MediatR；否则迁移到 Mediator（几乎相同的 API） |
| 单体增长复杂 | 添加模块边界，在每个模块内保持 VSA |
| 简单 CRUD 功能 | 单个文件：请求 + 处理器 + 端点 |
| 复杂功能（Saga，事件） | 功能文件夹内多个文件，仍然同地 |
| 在功能之间共享逻辑 | 提取到 `Common/` — 不要提取到另一个功能 |
