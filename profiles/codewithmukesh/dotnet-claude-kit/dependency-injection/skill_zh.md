# 依赖注入

## 核心原则

1. **构造函数注入是默认方式** — 通过构造函数注入依赖（主要构造函数使这种方式更清晰）。不要使用服务定位器，不要使用属性注入。
2. **仔细匹配生命周期** — 单例绝不能依赖范围型或瞬态服务。这是最常见的DI Bug。
3. **注册接口，解析接口** — 注册 `services.AddScoped<IOrderService, OrderService>()`，而不是具体类型。
4. **键值服务用于策略模式** — .NET 8+ 的键值服务取代了手动工厂模式，用于在多个实现之间进行选择。

## 模式

### 键值服务 (.NET 8+)

使用键值服务来注册和解析同一接口的多个实现。

```csharp
// 注册
builder.Services.AddKeyedScoped<INotificationService, EmailNotificationService>("email");
builder.Services.AddKeyedScoped<INotificationService, SmsNotificationService>("sms");
builder.Services.AddKeyedScoped<INotificationService, PushNotificationService>("push");

// 通过属性解析
public class OrderHandler([FromKeyedServices("email")] INotificationService notifier)
{
    public async Task Handle(CreateOrder.Command command, CancellationToken ct)
    {
        // ... 创建订单
        await notifier.SendAsync(notification, ct);
    }
}

// 通过 IServiceProvider 解析
public class NotificationRouter(IServiceProvider provider)
{
    public INotificationService GetService(string channel)
    {
        return provider.GetRequiredKeyedService<INotificationService>(channel);
    }
}
```

### 装饰器模式

```csharp
// 基础服务
public interface IOrderService
{
    Task<Result<Order>> CreateAsync(CreateOrderRequest request, CancellationToken ct);
}

public class OrderService(AppDbContext db, TimeProvider clock) : IOrderService
{
    public async Task<Result<Order>> CreateAsync(CreateOrderRequest request, CancellationToken ct)
    {
        var order = Order.Create(request, clock.GetUtcNow());
        db.Orders.Add(order);
        await db.SaveChangesAsync(ct);
        return Result.Success(order);
    }
}

// 装饰器 — 添加日志记录
public class LoggingOrderService(IOrderService inner, ILogger<LoggingOrderService> logger) : IOrderService
{
    public async Task<Result<Order>> CreateAsync(CreateOrderRequest request, CancellationToken ct)
    {
        logger.LogInformation("为顾客 {CustomerId} 创建订单", request.CustomerId);
        var result = await inner.CreateAsync(request, ct);
        if (result.IsSuccess)
            logger.LogInformation("创建订单 {OrderId}", result.Value.Id);
        return result;
    }
}

// 使用 Scrutor 注册
builder.Services.AddScoped<IOrderService, OrderService>();
builder.Services.Decorate<IOrderService, LoggingOrderService>();
```

### 基于约定的注册 (Scrutor)

```csharp
// 自动注册符合约定的所有服务
builder.Services.Scan(scan => scan
    .FromAssemblyOf<Program>()
    .AddClasses(classes => classes.AssignableTo<ITransientService>())
    .AsImplementedInterfaces()
    .WithTransientLifetime()
    .AddClasses(classes => classes.AssignableTo<IScopedService>())
    .AsImplementedInterfaces()
    .WithScopedLifetime());
```

### 工厂模式

当你需要运行时逻辑来选择实现时。

```csharp
builder.Services.AddScoped<IPaymentProcessor>(sp =>
{
    var config = sp.GetRequiredService<IOptions<PaymentOptions>>().Value;
    return config.Provider switch
    {
        "stripe" => ActivatorUtilities.CreateInstance<StripeProcessor>(sp),
        "paypal" => ActivatorUtilities.CreateInstance<PayPalProcessor>(sp),
        _ => throw new InvalidOperationException($"未知的支付提供者: {config.Provider}")
    };
});
```

### 选项注册

```csharp
// 绑定配置节到一个强类型的选项类
builder.Services.AddOptions<JwtOptions>()
    .BindConfiguration("Jwt")
    .ValidateDataAnnotations()
    .ValidateOnStart();

// 作为 IOptions<T> 注入
public class TokenService(IOptions<JwtOptions> options)
{
    private readonly JwtOptions _jwt = options.Value;
}
```

## 反模式

### 不要在单例中捕获范围型服务

```csharp
// BAD — DbContext 是范围型的，被单例捕获 = 内存泄漏 + 过期数据
builder.Services.AddSingleton<OrderCache>(); // 依赖 AppDbContext

// GOOD — 在单例中使用 IServiceScopeFactory
public class OrderCache(IServiceScopeFactory scopeFactory)
{
    public async Task<Order?> GetAsync(Guid id)
    {
        await using var scope = scopeFactory.CreateAsyncScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        return await db.Orders.FindAsync(id);
    }
}
```

### 不要将所有服务注册为单例

```csharp
// BAD — 将持有可变状态的服务注册为单例
builder.Services.AddSingleton<OrderService>(); // 依赖 DbContext

// GOOD — 根据服务的需求匹配生命周期
builder.Services.AddScoped<OrderService>();
```

## 决策指南

| 场景 | 建议 |
|------|------|
| 无状态服务 | 范围型（默认）或瞬态 |
| 配置 / 缓存 | 单例 |
| DbContext | 范围型（由 `AddDbContext` 注册） |
| 多个实现 | 键值服务（策略模式） |
| 跨切关注点行为 | 装饰器模式 |
| 基于约定的注册 | Scrutor |
| 运行时实现选择 | 工厂委托 |
| 审计现有注册 | `get_di_registrations` MCP 工具 — 生命周期、重复、被捕获依赖风险一次调用即可查看 |
| 强类型配置 | `AddOptions<T>().BindConfiguration()` |
