# 领域驱动设计 (DDD)

## 核心原则

1. **聚合定义一致性边界** — 聚合是一组实体和值对象，它们被视为一个单元进行数据变更。聚合内的所有不变式都在单个事务中强制执行。跨聚合的一致性是最终一致性。
2. **值对象优于原始类型** — 用值对象替换原始类型痴迷。`Money`、`EmailAddress`、`OrderNumber` 不是字符串 — 它们包含验证、相等性和行为。使用 C# 记录类型创建不可变的值对象。
3. **领域事件解耦副作用** — 当领域内发生有意义的事情（`OrderPlaced`、`PaymentReceived`）时，引发一个领域事件。副作用（发送电子邮件、更新读模型、通知另一个聚合）订阅这些事件。聚合专注于自己的规则。
4. **聚合根是唯一入口点** — 外部代码只能通过其根实体访问聚合。子实体从不独立加载或修改。根实体为整个聚合强制执行所有不变式。
5. **仓库持久化聚合，而非实体** — 每个聚合根一个仓库。仓库将整个聚合作为一个单元加载和保存。没有子实体的仓库。基础设施实现使用 `DbContext` 内部 — 这是 DDD 战术模式用于聚合边界，而不是通用的 CRUD 封装。

## 模式

### 聚合根

聚合根拥有对其子实体的所有访问权限并强制执行不变式：

```csharp
// Domain/Orders/Order.cs
public sealed class Order : AggregateRoot
{
    private readonly List<OrderLine> _lines = [];

    private Order() { } // EF Core

    public OrderNumber Number { get; private set; } = null!;
    public CustomerId CustomerId { get; private set; }
    public Money Total { get; private set; } = Money.Zero("USD");
    public OrderStatus Status { get; private set; }
    public DateTimeOffset PlacedAt { get; private set; }
    public IReadOnlyList<OrderLine> Lines => _lines.AsReadOnly();

    public static Order Place(CustomerId customerId, OrderNumber number, DateTimeOffset now)
    {
        var order = new Order
        {
            Id = Guid.CreateVersion7(),
            CustomerId = customerId,
            Number = number,
            Status = OrderStatus.Placed,
            PlacedAt = now
        };

        order.RaiseDomainEvent(new OrderPlaced(order.Id, customerId, now));
        return order;
    }

    public Result AddLine(ProductId productId, int quantity, Money unitPrice)
    {
        if (Status is not OrderStatus.Placed)
            return Result.Failure("Cannot modify a confirmed or cancelled order");

        if (quantity <= 0)
            return Result.Failure("Quantity must be positive");

        var existing = _lines.FirstOrDefault(l => l.ProductId == productId);
        if (existing is not null)
        {
            existing.IncreaseQuantity(quantity);
        }
        else
        {
            _lines.Add(new OrderLine(productId, quantity, unitPrice));
        }

        RecalculateTotal();
        return Result.Success();
    }

    public Result Confirm()
    {
        if (Status is not OrderStatus.Placed)
            return Result.Failure("Only placed orders can be confirmed");

        if (_lines.Count == 0)
            return Result.Failure("Cannot confirm an order with no lines");

        Status = OrderStatus.Confirmed;
        RaiseDomainEvent(new OrderConfirmed(Id));
        return Result.Success();
    }

    private void RecalculateTotal()
    {
        Total = _lines.Aggregate(Money.Zero(Total.Currency), (sum, line) => sum + line.Subtotal);
    }
}
```

### 值对象作为记录类型

使用 C# 记录类型创建具有结构化相等性的不可变值对象：

```csharp
// Domain/Common/Money.cs
public sealed record Money
{
    public decimal Amount { get; }
    public string Currency { get; }

    public Money(decimal amount, string currency)
    {
        ArgumentOutOfRangeException.ThrowIfNegative(amount);
        ArgumentException.ThrowIfNullOrWhiteSpace(currency);

        Amount = amount;
        Currency = currency.ToUpperInvariant();
    }

    public static Money Zero(string currency) => new(0, currency);

    public static Money operator +(Money left, Money right)
    {
        if (left.Currency != right.Currency)
            throw new InvalidOperationException($"Cannot add {left.Currency} and {right.Currency}");
        return new Money(left.Amount + right.Amount, left.Currency);
    }
}

// 其他值对象（`EmailAddress`、`OrderNumber` 等）遵循相同模式：
// sealed record、构造函数验证、无公共设置器
```

### 强类型 ID 与 EF Core 转换器

防止混淆来自不同实体的 GUID：

```csharp
// Domain/Common/StronglyTypedId.cs
public readonly record struct CustomerId(Guid Value)
{
    public static CustomerId New() => new(Guid.CreateVersion7());
    public override string ToString() => Value.ToString();
}

public readonly record struct ProductId(Guid Value)
{
    public static ProductId New() => new(Guid.CreateVersion7());
}

public readonly record struct OrderNumber(string Value)
{
    public override string ToString() => Value;
}

// Infrastructure/Persistence/Configurations/OrderConfiguration.cs
public class OrderConfiguration : IEntityTypeConfiguration<Order>
{
    public void Configure(EntityTypeBuilder<Order> builder)
    {
        builder.HasKey(o => o.Id);

        builder.Property(o => o.CustomerId)
            .HasConversion(id => id.Value, value => new CustomerId(value));

        builder.Property(o => o.Number)
            .HasConversion(n => n.Value, value => new OrderNumber(value))
            .HasMaxLength(50);

        builder.ComplexProperty(o => o.Total, money =>
        {
            money.Property(m => m.Amount).HasColumnName("Total").HasPrecision(18, 2);
            money.Property(m => m.Currency).HasColumnName("Currency").HasMaxLength(3);
        });

        builder.HasMany(o => o.Lines).WithOne().HasForeignKey("OrderId");
        builder.Navigation(o => o.Lines).AutoInclude();
    }
}
```

### 领域事件派发

在聚合中引发事件，在 `SaveChangesAsync` 中派发：

```csharp
// Domain/Common/AggregateRoot.cs
public abstract class AggregateRoot : Entity
{
    private readonly List<IDomainEvent> _domainEvents = [];

    public IReadOnlyList<IDomainEvent> DomainEvents => _domainEvents.AsReadOnly();

    protected void RaiseDomainEvent(IDomainEvent domainEvent) => _domainEvents.Add(domainEvent);

    public void ClearDomainEvents() => _domainEvents.Clear();
}

// `INotification` 来自 MIT 许可的 Mediator 包（不是 MediatR —
// 请参阅包规则）。如果未使用中介，请使用一个普通的标记接口。
public interface IDomainEvent : INotification
{
    DateTimeOffset OccurredAt { get; }
}

// Domain/Orders/Events/OrderPlaced.cs
public sealed record OrderPlaced(Guid OrderId, CustomerId CustomerId, DateTimeOffset PlacedAt) : IDomainEvent
{
    public DateTimeOffset OccurredAt => PlacedAt;
}

// Infrastructure/Persistence/AppDbContext.cs — 通过主构造器注入发布者
public class AppDbContext(DbContextOptions<AppDbContext> options, IPublisher publisher)
    : DbContext(options)
{
    public override async Task<int> SaveChangesAsync(CancellationToken ct = default)
    {
        var aggregates = ChangeTracker.Entries<AggregateRoot>()
            .Where(e => e.Entity.DomainEvents.Count > 0)
            .Select(e => e.Entity)
            .ToList();

        var events = aggregates.SelectMany(a => a.DomainEvents).ToList();

        var result = await base.SaveChangesAsync(ct);

        foreach (var @event in events)
            await publisher.Publish(@event, ct);

        foreach (var aggregate in aggregates)
            aggregate.ClearDomainEvents();

        return result;
    }
}
```

### 领域服务

用于不属于单个聚合的逻辑：

```csharp
// Domain/Orders/Services/PricingService.cs
// 跨聚合协调逻辑 — 接收领域接口，返回值对象
public sealed class PricingService(IDiscountPolicy discountPolicy)
{
    public Money CalculatePrice(ProductId productId, int quantity, Money unitPrice, CustomerId customerId)
    {
        var subtotal = new Money(unitPrice.Amount * quantity, unitPrice.Currency);
        var discount = discountPolicy.GetDiscount(customerId, productId, quantity);
        return new Money(subtotal.Amount * (1 - discount), subtotal.Currency);
    }
}
```

## 反模式

### 过大的聚合

```csharp
// BAD — 客户聚合拥有客户接触到的所有内容
public class Customer : AggregateRoot
{
    public List<Order> Orders { get; } = [];        // 应该是独立的聚合
    public List<Payment> Payments { get; } = [];     // 应该是独立的聚合
    public List<Address> Addresses { get; } = [];    // 可能可以作为子聚合
    public ShoppingCart Cart { get; set; }            // 应该是独立的聚合
}

// GOOD — 小型、专注的聚合通过 ID 链接
public class Customer : AggregateRoot
{
    public CustomerName Name { get; private set; }
    public EmailAddress Email { get; private set; }
    // `Orders`、`Payments`、`Cart` 是引用 `CustomerId` 的独立聚合
}
```

### 同聚合内的领域事件

```csharp
// BAD — 使用事件处理同一聚合内的逻辑
order.RaiseDomainEvent(new OrderLineAdded(line));
// 然后一个处理器重新计算总数... 但你处于同一个聚合！

// GOOD — 直接在聚合内调用方法
_lines.Add(line);
RecalculateTotal();  // 私有方法，无需事件
```

### 具有身份的值对象

```csharp
// BAD — 值对象具有一个 ID（它就是一个实体了！）
public record Address
{
    public Guid Id { get; init; }  // 值对象没有身份
    public string Street { get; init; }
}

// GOOD — 值对象由其属性定义，而不是一个 ID
public record Address(string Street, string City, string PostalCode, string Country);
```

### 贫血聚合

```csharp
// BAD — 聚合只是一个数据包，服务做所有工作
public class Order : AggregateRoot
{
    public OrderStatus Status { get; set; }  // 公共设置器！
    public List<OrderLine> Lines { get; set; } = [];
}

// 服务直接操作订单状态
order.Status = OrderStatus.Confirmed;  // 没有不变式检查！
order.Lines.Add(newLine);              // 没有验证！

// GOOD — 聚合封装规则（见聚合根模式）
order.Confirm();  // 验证状态，引发事件
order.AddLine(productId, quantity, unitPrice);  // 验证，重新计算
```

## 决策指南

| 场景 | 建议 |
|------|------|
| 何时使用 DDD | 复杂领域，业务规则超出 CRUD |
| 何时使用值对象 | 任何具有验证规则或基于属性而非身份的相等性概念 |
| 聚合大小 | 保持小 — 通常 1 个根实体 + 0-3 个子实体。每次加载整个聚合 |
| 领域事件与集成事件 | 领域事件：在边界内，同一事务。集成事件：跨上下文，通过消息总线 |
| 强类型 ID | 聚合根 ID 跨边界时始终使用。子实体 ID 可选 |
| 何时不使用 DDD | 简单 CRUD、设置、审计日志、读模型 — 使用普通实体 |
| 仓库与 DbContext | 复杂聚合每个聚合根一个仓库；`IAppDbContext` 用于简单查询 |
| 领域服务 | 仅当逻辑需要多个聚合或聚合不应知道的外部数据时使用 |
