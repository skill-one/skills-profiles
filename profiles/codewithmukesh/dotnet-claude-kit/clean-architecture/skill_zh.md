# 清洁架构

## 核心原则

1. **依赖倒置是基础** — 所有依赖都指向内部。领域层没有项目引用。应用层只引用领域层。基础设施层引用应用层和领域层。API层引用所有层但依赖抽象。编译器通过项目引用强制执行此规则。
2. **领域拥有规则** — 业务逻辑存在于领域层作为实体方法、领域服务或规范。领域层不知道数据库、HTTP或任何框架 — 只有纯C#和.NET原语。
3. **用例是工作单元** — 每个用例（命令或查询）是应用层中的一个类。它协调领域对象，通过抽象持久化，并返回结果。没有包含20个方法的"服务"类。
4. **基础设施是插件** — EF Core、外部API、邮件发送器、文件存储 — 所有这些都存在于基础设施中，并实现应用层或领域层定义的接口。在不触及业务逻辑的情况下交换实现。
5. **API层很薄** — 端点将HTTP映射到用例，并将用例映射到HTTP响应。端点中没有业务逻辑。

## 模式

### 项目布局

```
src/
  MyApp.Domain/
    Entities/
      Order.cs                    # 带行为的实体
      OrderItem.cs
    Enums/
      OrderStatus.cs
    Exceptions/
      DomainException.cs          # 基础领域异常
    Interfaces/
      IOrderRepository.cs         # 仅当查询需要超出DbSet时才需要
    Common/
      Entity.cs                   # 带Id的基础实体
      Result.cs                   # 结果模式类型

  MyApp.Application/
    Common/
      Behaviors/
        ValidationBehavior.cs     # 中介管道行为
      Interfaces/
        IAppDbContext.cs           # DbContext抽象（优先于仓库）
    Orders/
      Commands/
        CreateOrder/
          CreateOrderCommand.cs
          CreateOrderHandler.cs
          CreateOrderValidator.cs
      Queries/
        GetOrder/
          GetOrderQuery.cs
          GetOrderHandler.cs
          OrderDto.cs

  MyApp.Infrastructure/
    Persistence/
      AppDbContext.cs              # 实现 IAppDbContext
      Configurations/
        OrderConfiguration.cs
      Migrations/
    Services/
      EmailSender.cs               # 实现 IEmailSender 来自应用层
    DependencyInjection.cs         # AddInfrastructure 扩展

  MyApp.Api/
    Endpoints/
      OrderEndpoints.cs            # 薄的，映射 HTTP ↔ 用例
    Program.cs
```

### DbContext抽象（优先于仓库）

在应用层定义一个最小接口；在基础设施层实现：

```csharp
// Application/Common/Interfaces/IAppDbContext.cs
public interface IAppDbContext
{
    DbSet<Order> Orders { get; }
    DbSet<Product> Products { get; }
    Task<int> SaveChangesAsync(CancellationToken ct = default);
}

// Infrastructure/Persistence/AppDbContext.cs
public class AppDbContext(DbContextOptions<AppDbContext> options)
    : DbContext(options), IAppDbContext
{
    public DbSet<Order> Orders => Set<Order>();
    public DbSet<Product> Products => Set<Product>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
    }
}
```

为什么使用IAppDbContext而不是IRepository？EF Core的DbSet本身就是仓库。在大多数情况下，在顶部添加另一个抽象会增加间接性而没有价值。

### 用例处理器（命令）

```csharp
// Application/Orders/Commands/CreateOrder/CreateOrderCommand.cs
public record CreateOrderCommand(
    string CustomerId,
    List<OrderItemDto> Items) : IRequest<Result<Guid>>;

public record OrderItemDto(string ProductId, int Quantity, decimal UnitPrice);

// Application/Orders/Commands/CreateOrder/CreateOrderHandler.cs — 使用中介（源生成，MIT）
internal sealed class CreateOrderHandler(
    IAppDbContext db,
    TimeProvider clock) : IRequestHandler<CreateOrderCommand, Result<Guid>>
{
    public async ValueTask<Result<Guid>> Handle(CreateOrderCommand request, CancellationToken ct)
    {
        var order = Order.Create(
            request.CustomerId,
            request.Items.Select(i => new OrderItem(i.ProductId, i.Quantity, i.UnitPrice)),
            clock.GetUtcNow());

        db.Orders.Add(order);
        await db.SaveChangesAsync(ct);

        return Result.Success(order.Id);
    }
}

// Application/Orders/Commands/CreateOrder/CreateOrderValidator.cs
public class CreateOrderValidator : AbstractValidator<CreateOrderCommand>
{
    public CreateOrderValidator()
    {
        RuleFor(x => x.CustomerId).NotEmpty();
        RuleFor(x => x.Items).NotEmpty();
        RuleForEach(x => x.Items).ChildRules(item =>
        {
            item.RuleFor(x => x.ProductId).NotEmpty();
            item.RuleFor(x => x.Quantity).GreaterThan(0);
            item.RuleFor(x => x.UnitPrice).GreaterThan(0);
        });
    }
}
```

### 用例处理器（查询）

```csharp
// Application/Orders/Queries/GetOrder/GetOrderQuery.cs
public record GetOrderQuery(Guid OrderId) : IRequest<Result<OrderDto>>;

public record OrderDto(Guid Id, string CustomerId, decimal Total, string Status, DateTimeOffset CreatedAt);

// Application/Orders/Queries/GetOrder/GetOrderHandler.cs
internal sealed class GetOrderHandler(IAppDbContext db) : IRequestHandler<GetOrderQuery, Result<OrderDto>>
{
    public async ValueTask<Result<OrderDto>> Handle(GetOrderQuery request, CancellationToken ct)
    {
        var order = await db.Orders
            .Where(o => o.Id == request.OrderId)
            .Select(o => new OrderDto(o.Id, o.CustomerId, o.Total, o.Status.ToString(), o.CreatedAt))
            .FirstOrDefaultAsync(ct);

        return order is not null
            ? Result.Success(order)
            : Result.Failure<OrderDto>("Order not found");
    }
}
```

### 域实体带行为

```csharp
// Domain/Entities/Order.cs
public class Order : Entity
{
    private readonly List<OrderItem> _items = [];

    private Order() { } // EF Core

    public string CustomerId { get; private set; } = null!;
    public OrderStatus Status { get; private set; }
    public decimal Total { get; private set; }
    public DateTimeOffset CreatedAt { get; private set; }
    public IReadOnlyList<OrderItem> Items => _items.AsReadOnly();

    public static Order Create(string customerId, IEnumerable<OrderItem> items, DateTimeOffset now)
    {
        var order = new Order
        {
            Id = Guid.CreateVersion7(),
            CustomerId = customerId,
            Status = OrderStatus.Pending,
            CreatedAt = now
        };

        foreach (var item in items)
            order.AddItem(item);

        return order;
    }

    public void AddItem(OrderItem item)
    {
        _items.Add(item);
        Total = _items.Sum(i => i.Quantity * i.UnitPrice);
    }

    public Result Cancel()
    {
        if (Status is not OrderStatus.Pending)
            return Result.Failure("只有待处理订单可以被取消");

        Status = OrderStatus.Cancelled;
        return Result.Success();
    }
}
```

### 薄端点连接（IEndpointGroup自动发现）

每个端点组实现`IEndpointGroup`并通过`app.MapEndpoints()`自动发现。添加新端点时`Program.cs`永远不会改变。参见**最小API**技能以了解完整的`IEndpointGroup`接口和`EndpointExtensions`设置。

```csharp
// Api/Endpoints/OrderEndpoints.cs
public sealed class OrderEndpoints : IEndpointGroup
{
    public void Map(IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/orders").WithTags("Orders");

        group.MapPost("/", CreateOrder)
            .WithName("CreateOrder");

        group.MapGet("/{id:guid}", GetOrder)
            .WithName("GetOrder");

        group.MapGet("/", ListOrders)
            .WithName("ListOrders");
    }

    private static async Task<IResult> CreateOrder(
        CreateOrderCommand command, ISender sender, CancellationToken ct)
    {
        var result = await sender.Send(command, ct);
        return result.IsSuccess
            ? TypedResults.Created($"/api/orders/{result.Value}", result.Value)
            : result.ToProblemDetails();
    }

    private static async Task<IResult> GetOrder(
        Guid id, ISender sender, CancellationToken ct)
    {
        var result = await sender.Send(new GetOrderQuery(id), ct);
        return result.IsSuccess
            ? TypedResults.Ok(result.Value)
            : TypedResults.NotFound();
    }

    private static async Task<IResult> ListOrders(
        [AsParameters] ListOrdersQuery query, ISender sender, CancellationToken ct)
    {
        var result = await sender.Send(query, ct);
        return TypedResults.Ok(result);
    }
}
```

### 基础设施DI注册

```csharp
// Infrastructure/DependencyInjection.cs
public static class DependencyInjection
{
    public static IServiceCollection AddInfrastructure(
        this IServiceCollection services,
        IConfiguration config)
    {
        services.AddDbContext<AppDbContext>(options =>
            options.UseNpgsql(config.GetConnectionString("DefaultConnection")));

        services.AddScoped<IAppDbContext>(sp => sp.GetRequiredService<AppDbContext>());

        return services;
    }
}
```

## 反模式

### 贫血领域模型

```csharp
// BAD — 实体只是一个数据包，所有逻辑都在处理器中
public class Order
{
    public Guid Id { get; set; }
    public string CustomerId { get; set; } = null!;
    public decimal Total { get; set; }
    public List<OrderItem> Items { get; set; } = [];
}

// 处理器直接设置所有内容
order.Total = order.Items.Sum(i => i.Quantity * i.UnitPrice);
order.Status = OrderStatus.Pending;

// GOOD — 实体封装自己的规则（见领域实体模式）
var order = Order.Create(customerId, items, clock.GetUtcNow());
```

### 领域层中的DbContext

```csharp
// BAD — 领域引用EF Core
// Domain/Services/OrderService.cs
public class OrderService(AppDbContext db) { } // 领域依赖于基础设施！

// GOOD — 领域定义接口，基础设施实现
// Domain/Interfaces/IOrderRepository.cs（仅当你需要超出DbSet的查询抽象时）
// Application/Common/Interfaces/IAppDbContext.cs（优先）
```

### 胖端点

```csharp
// BAD — 端点中包含业务逻辑
app.MapPost("/orders", async (CreateOrderRequest req, AppDbContext db) =>
{
    var order = new Order { CustomerId = req.CustomerId };
    foreach (var item in req.Items)
    {
        order.Items.Add(new OrderItem { ProductId = item.ProductId, Quantity = item.Quantity });
    }
    order.Total = order.Items.Sum(i => i.Quantity * i.UnitPrice);
    db.Orders.Add(order);
    await db.SaveChangesAsync();
    return TypedResults.Created($"/orders/{order.Id}", order);
});

// GOOD — 端点委托给用例
app.MapPost("/orders", async (CreateOrderCommand command, ISender sender, CancellationToken ct) =>
{
    var result = await sender.Send(command, ct);
    return result.IsSuccess
        ? TypedResults.Created($"/orders/{result.Value}", result.Value)
        : result.ToProblemDetails();
});
```

### 每个实体使用仓库

```csharp
// BAD — 每个实体仓库重复DbSet功能
public interface IOrderRepository { Task<Order?> GetByIdAsync(Guid id); }
public interface IProductRepository { Task<Product?> GetByIdAsync(Guid id); }
public interface ICustomerRepository { Task<Customer?> GetByIdAsync(Guid id); }

// GOOD — 直接使用IAppDbContext与DbSet<T>直接
// 仅当你有复杂的可重用查询逻辑时才创建仓库
// 你希望在隔离中测试或跨多个用例重用时
```

## 决策指南

| 场景 | 建议 |
|------|------|
| 何时使用CA而非VSA | 中等+领域复杂度，长期系统，团队熟悉分层 |
| 何时添加领域层 | 业务规则涉及跨实体组的不变量 |
| IAppDbContext与仓库 | 优先使用IAppDbContext；仅当需要复杂可重用查询时才添加仓库 |
| CA中的中介与原始处理器 | 中介用于管道行为（验证、日志）；原始处理器用于简单性 |
| 何时添加领域事件 | 当副作用（通知、审计）应与主流程解耦时 |
| 从VSA进化到CA | 当处理器开始需要不属于Common/的共享领域逻辑时 |
