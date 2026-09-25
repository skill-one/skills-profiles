# 消息传递

## 核心原则

1. **推荐使用 Wolverine 作为默认方案** — MIT 授权，将中介者（mediator）+ 消息传递（messaging）集成在一个库中，内置发送箱（outbox）、saga 支持，并基于约定的处理器。MassTransit 是一个替代方案，但从 v9 版本起需要商业授权。
2. **使用发送箱模式以保证可靠性** — 始终使用事务性发送箱，以确保只有在数据库事务成功时才发布消息。
3. **简单流程使用编排（choreography），复杂流程使用 saga** — 如果工作流包含 2-3 步，使用事件编排。如果包含补偿操作或复杂状态，使用 saga。
4. **消息即契约** — 将消息类型放在共享的契约项目中。将它们保持为简单的记录，并使用原始类型。

## 模式

### Wolverine 配置

```csharp
// Program.cs
builder.Host.UseWolverine(opts =>
{
    // 从当前程序集自动发现处理器
    opts.Discovery.IncludeAssembly(typeof(Program).Assembly);

    // RabbitMQ 传输
    opts.UseRabbitMq(rabbit =>
    {
        rabbit.HostName = "localhost";
        // 或从配置中获取：
        // rabbit.HostName = builder.Configuration["RabbitMq:Host"]!;
    })
    .AutoProvision()   // 自动创建队列/交换
    .AutoPurgeOnStartup(); // 开发环境专用 — 启动时清空队列

    // 使用 EF Core 启用事务性发送箱
    opts.Services.AddDbContextWithWolverineIntegration<AppDbContext>(x =>
        x.UseNpgsql(builder.Configuration.GetConnectionString("Default")));

    opts.Policies.AutoApplyTransactions(); // 将处理器包装在数据库事务中
});
```

**原因**：`UseWolverine()` 在一个地方注册了处理器发现、传输和发送箱。`AutoProvision()` 消除了开发期间手动配置代理的步骤。

### 发布事件

Wolverine 支持两种发布风格：级联消息（返回值）和显式发布。

```csharp
// 消息契约（在共享的 Contracts 项目中）
public record OrderCreated(Guid OrderId, string CustomerId, decimal Total, DateTimeOffset CreatedAt);

// 风格 1：级联消息 — 从处理器返回事件
// Wolverine 在处理器完成后自动发布返回的消息。
public static class CreateOrder
{
    public record Command(string CustomerId, List<OrderItem> Items);
    public record Response(Guid OrderId, decimal Total);

    public static async Task<(Response, OrderCreated)> HandleAsync(
        Command command, AppDbContext db, TimeProvider clock, CancellationToken ct)
    {
        var order = Order.Create(command.CustomerId, command.Items, clock.GetUtcNow());
        db.Orders.Add(order);
        await db.SaveChangesAsync(ct);

        var response = new Response(order.Id, order.Total);
        var @event = new OrderCreated(order.Id, order.CustomerId, order.Total, order.CreatedAt);

        return (response, @event); // 两者都会被自动发布
    }
}
```

```csharp
// 风格 2：通过 IMessageBus 显式发布
public static class CreateOrder
{
    public record Command(string CustomerId, List<OrderItem> Items);
    public record Response(Guid OrderId, decimal Total);

    public static async Task<Response> HandleAsync(
        Command command, AppDbContext db, IMessageBus bus, TimeProvider clock, CancellationToken ct)
    {
        var order = Order.Create(command.CustomerId, command.Items, clock.GetUtcNow());
        db.Orders.Add(order);
        await db.SaveChangesAsync(ct);

        await bus.PublishAsync(new OrderCreated(
            order.Id, order.CustomerId, order.Total, order.CreatedAt));

        return new Response(order.Id, order.Total);
    }
}
```

**原因**：级联消息（元组返回）更简单且可测试 — 处理器是一个纯函数。当发布是条件性的或需要多个事件时，使用显式的 `IMessageBus`。

### 消费事件

Wolverine 使用基于约定的处理器 — 无需接口，无需基类。只需一个 `Handle` 方法，第一个参数是消息类型。

```csharp
// 通知模块 — 处理来自订单模块的 OrderCreated
public static class OrderCreatedHandler
{
    public static async Task HandleAsync(
        OrderCreated message, NotificationsDbContext db, ILogger logger, CancellationToken ct)
    {
        logger.LogInformation("处理 OrderCreated: {OrderId}", message.OrderId);

        var notification = new OrderNotification(message.OrderId, message.CustomerId);
        db.Notifications.Add(notification);
        await db.SaveChangesAsync(ct);
    }
}
```

**原因**：基于约定的处理器几乎没有仪式。Wolverine 通过签名发现它们：任何名为 `Handle`/`HandleAsync`/`Consume`/`ConsumeAsync` 的公共方法，第一个参数是消息类型。

### 事务性发送箱

确保只有在数据库事务成功时才发布消息。

```csharp
// 1. 使用 Wolverine 集成注册 DbContext
builder.Host.UseWolverine(opts =>
{
    opts.Services.AddDbContextWithWolverineIntegration<AppDbContext>(x =>
        x.UseNpgsql(builder.Configuration.GetConnectionString("Default")));

    opts.Policies.AutoApplyTransactions();
});

// 2. DbContext — 添加 Wolverine 发送箱表
public class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
{
    public DbSet<Order> Orders => Set<Order>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // Wolverine 的输入/输出消息表 — 事务性消息传递所必需
        modelBuilder.AddIncomingWolverineMessageTable();
        modelBuilder.AddOutgoingWolverineMessageTable();
    }
}
```

**原因**：`AddDbContextWithWolverineIntegration` + `AutoApplyTransactions` 将每个处理器包装在一个包含发送箱写入的事务中。只有在事务提交后才会发送消息 — 没有双写问题。

### Saga（状态化编排）

Wolverine saga 使用 `Saga<T>` 基类，包含 `Start` 和 `Handle` 方法。级联消息驱动 saga 向前推进。

```csharp
public record OrderSagaState(Guid Id)
{
    public string? CustomerId { get; set; }
    public bool PaymentReceived { get; set; }
}

public class OrderSaga : Saga<OrderSagaState>
{
    public Guid Id { get; set; }

    // 当收到 OrderCreated 事件时启动 saga
    public static (OrderSagaState, ProcessPayment) Start(OrderCreated message)
    {
        var state = new OrderSagaState(message.OrderId)
        {
            CustomerId = message.CustomerId
        };

        var command = new ProcessPayment(message.OrderId, message.Total);
        return (state, command); // 状态被持久化，命令被发送
    }

    // 处理支付结果
    public CompleteOrder Handle(PaymentCompleted message)
    {
        PaymentReceived = true;
        MarkCompleted(); // 结束 saga
        return new CompleteOrder(Id);
    }

    // 失败时的补偿操作
    public CancelOrder Handle(PaymentFailed message)
    {
        MarkCompleted();
        return new CancelOrder(Id);
    }
}
```

**原因**：Wolverine saga 使用简单的 C# 方法而不是状态机 DSL。每个处理器返回级联消息来驱动工作流。`MarkCompleted()` 清理 saga 状态。

### 替代方案：MassTransit

MassTransit 是一个成熟的替代方案，从 v9 版本起需要商业授权。关键 API 界面：

```csharp
// 配置
builder.Services.AddMassTransit(x =>
{
    x.SetKebabCaseEndpointNameFormatter();
    x.AddConsumers(typeof(Program).Assembly);
    x.UsingRabbitMq((context, cfg) =>
    {
        cfg.Host(builder.Configuration.GetConnectionString("RabbitMq"));
        cfg.ConfigureEndpoints(context);
    });
});

// 发布
await publishEndpoint.Publish(new OrderCreated(...), ct);

// 消费 — 需要 IConsumer<T> 接口
public class OrderCreatedConsumer(AppDbContext db) : IConsumer<OrderCreated>
{
    public async Task Consume(ConsumeContext<OrderCreated> context)
    {
        var message = context.Message;
        // 处理事件...
    }
}

// 发送箱
x.AddEntityFrameworkOutbox<AppDbContext>(o =>
{
    o.UsePostgres();
    o.UseBusOutbox();
});

// Saga — 使用 MassTransitStateMachine<TState>
public class OrderSaga : MassTransitStateMachine<OrderSagaState> { /* ... */ }
```

> **授权说明**：MassTransit v9+ 在生产环境中需要商业授权。对于新项目，推荐使用 Wolverine (MIT)。

## 反模式

### 不要在没有发送箱的情况下发布事件

```csharp
// 错误 — 如果 SaveChanges 成功但 Publish 失败，数据不一致
await db.SaveChangesAsync(ct);
await bus.PublishAsync(new OrderCreated(...));

// 正确 — 使用事务性发送箱（消息在同一事务中）
// 配置 AddDbContextWithWolverineIntegration() + AutoApplyTransactions()
// Wolverine 会自动处理
```

### 不要在消息契约中放置复杂逻辑

```csharp
// 错误 — 消息中包含行为
public record OrderCreated(Guid OrderId)
{
    public decimal CalculateShipping() => /* 逻辑 */; // 不要这样做
}

// 正确 — 消息是纯数据
public record OrderCreated(Guid OrderId, string CustomerId, decimal Total, DateTimeOffset CreatedAt);
```

### 不要对重要事件使用“发后即忘”

```csharp
// 错误 — 没有保证投递
_ = Task.Run(() => bus.PublishAsync(new OrderCreated(...)));

// 正确 — 等待发布（使用发送箱，这是事务性的）
await bus.PublishAsync(new OrderCreated(...));
```

## 决策指南

| 场景 | 推荐 |
|------|------|
| 模块间通信（新项目） | Wolverine + 事件（MIT，免费） |
| 模块间通信（现有 MassTransit） | MassTransit（v9 需要商业授权） |
| 可靠的事件发布 | 事务性发送箱（Wolverine 和 MassTransit 都支持） |
| 简单 2-3 步工作流 | 事件编排 |
| 复杂工作流带补偿操作 | Wolverine saga 或 MassTransit saga |
| 本地开发代理 | RabbitMQ（通过 Docker 或 Aspire） |
| 生产云代理 | Azure Service Bus 或 RabbitMQ |
| 想要单个库集成中介者 + 消息传递 | Wolverine（替代了中介者和 MassTransit） |
