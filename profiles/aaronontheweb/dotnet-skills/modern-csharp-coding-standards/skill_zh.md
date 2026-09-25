# 现代 C# 编码规范

## 何时使用这项技能

在以下情况下使用这项技能：
- 编写新的 C# 代码或重构现有代码
- 设计库或服务的公共 API
- 优化性能关键代码路径
- 实现强类型的领域模型
- 构建以 async/await 为主的应用程序
- 处理二进制数据、缓冲区或高吞吐量场景

## 参考文件

- [value-objects-and-patterns.md](value-objects-and-patterns.md)：完整的值对象示例和模式匹配代码
- [performance-and-api-design.md](performance-and-api-design.md)：Span<T>/Memory<T> 示例和 API 设计原则
- [composition-and-error-handling.md](composition-and-error-handling.md)：组合优于继承、Result 类型、测试模式
- [anti-patterns-and-reflection.md](anti-patterns-and-reflection.md)：避免反射和常见反模式

## 核心原则

1. **默认不可变** - 使用 `record` 类型和使用 `init`-only 属性
2. **类型安全** - 利用可空引用类型和值对象
3. **现代模式匹配** - 大量使用 `switch` 表达式和模式
4. **全程异步** - 优先使用具有适当取消支持的异步 API
5. **零分配模式** - 使用 `Span<T>` 和 `Memory<T>` 进行性能关键代码
6. **API 设计** - 接受抽象，返回适当具体的类型
7. **组合优于继承** - 避免抽象基类，优先使用组合
8. **值对象作为结构体** - 使用 `readonly record struct` 作为值对象

---

## 语言模式

### Records 用于不可变数据 (C# 9+)

使用 `record` 类型编写 DTOs、消息、事件和领域实体。

```csharp
// 简单不可变 DTO
public record CustomerDto(string Id, string Name, string Email);

// 在构造函数中包含验证
public record EmailAddress
{
    public string Value { get; init; }

    public EmailAddress(string value)
    {
        if (string.IsNullOrWhiteSpace(value) || !value.Contains('@'))
            throw new ArgumentException("Invalid email address", nameof(value));

        Value = value;
    }
}

// 使用集合的 Records - 使用 IReadOnlyList
public record ShoppingCart(
    string CartId,
    string CustomerId,
    IReadOnlyList<CartItem> Items
)
{
    public decimal Total => Items.Sum(item => item.Price * item.Quantity);
}
```

**何时使用 `record class` 与 `record struct`：**
- `record class`（默认）：引用类型，用于实体、聚合、具有多个属性的 DTOs
- `record struct`：值类型，用于值对象（见下一节）

### 值对象作为 readonly record struct

值对象**必须始终是 `readonly record struct`**，以实现性能和值语义。使用显式转换，不要使用隐式运算符。

```csharp
public readonly record struct OrderId(string Value)
{
    public OrderId(string value) : this(
        !string.IsNullOrWhiteSpace(value)
            ? value
            : throw new ArgumentException("OrderId cannot be empty", nameof(value)))
    { }
    public override string ToString() => Value;
}

public readonly record struct Money(decimal Amount, string Currency);
public readonly record struct CustomerId(Guid Value)
{
    public static CustomerId New() => new(Guid.NewGuid());
}
```

有关完整示例，包括多值对象、工厂模式和 no-implicit-conversion 规则，请参阅 [value-objects-and-patterns.md](value-objects-and-patterns.md)。

### 模式匹配 (C# 8-12)

使用 `switch` 表达式、属性模式、关系模式和列表模式编写更简洁的代码。

```csharp
public decimal CalculateDiscount(Order order) => order switch
{
    { Total: > 1000m } => order.Total * 0.15m,
    { Total: > 500m } => order.Total * 0.10m,
    { Total: > 100m } => order.Total * 0.05m,
    _ => 0m
};
```

有关完整的模式匹配示例，请参阅 [value-objects-and-patterns.md](value-objects-and-patterns.md)。

---

### 可空引用类型 (C# 8+)

在项目中启用可空引用类型，并显式处理空值。

```csharp
// 在 .csproj 中
<PropertyGroup>
    <Nullable>enable</Nullable>
</PropertyGroup>

// 显式空值
public string? FindUserName(string userId)
{
    var user = _repository.Find(userId);
    return user?.Name;
}

// 使用模式匹配进行空值检查
public decimal GetDiscount(Customer? customer) => customer switch
{
    null => 0m,
    { IsVip: true } => 0.20m,
    { OrderCount: > 10 } => 0.10m,
    _ => 0.05m
};

// 使用 ArgumentNullException.ThrowIfNull (C# 11+) 进行守卫语句
public void ProcessOrder(Order? order)
{
    ArgumentNullException.ThrowIfNull(order);
    // order 在此作用域中现在是不可空的
    Console.WriteLine(order.Id);
}
```

---

## 组合优于继承

**避免抽象基类**。使用接口+组合。使用静态辅助方法共享逻辑。使用带有工厂方法的记录实现变体。

有关完整示例，请参阅 [composition-and-error-handling.md](composition-and-error-handling.md)。

---

## 性能模式

### Async/Await 最佳实践

```csharp
// 全程异步 - 始终接受 CancellationToken
public async Task<Order> GetOrderAsync(string orderId, CancellationToken cancellationToken)
{
    var order = await _repository.GetAsync(orderId, cancellationToken);
    return order;
}

// 使用 ValueTask 处理频繁调用且通常同步的方法
public ValueTask<Order?> GetCachedOrderAsync(string orderId, CancellationToken cancellationToken)
{
    if (_cache.TryGetValue(orderId, out var order))
        return ValueTask.FromResult<Order?>(order);
    return GetFromDatabaseAsync(orderId, cancellationToken);
}

// 使用 IAsyncEnumerable 进行流式处理
public async IAsyncEnumerable<Order> StreamOrdersAsync(
    string customerId,
    [EnumeratorCancellation] CancellationToken cancellationToken = default)
{
    await foreach (var order in _repository.StreamAllAsync(cancellationToken))
    {
        if (order.CustomerId == customerId)
            yield return order;
    }
}
```

**关键规则：**
- 始终使用 `CancellationToken` 并设置 `= default`
- 在库代码中使用 `ConfigureAwait(false)`
- 不要阻塞异步代码（不要使用 `.Result` 或 `.Wait()`）
- 使用 linked CancellationTokenSource 进行超时

### Span<T> 和 Memory<T>

使用 `Span<T>` 进行同步零分配操作，使用 `Memory<T>` 进行异步操作，使用 `ArrayPool<T>` 处理大型临时缓冲区。

有关完整的 Span/Memory 示例和 API 设计部分，请参阅 [performance-and-api-design.md](performance-and-api-design.md)。

---

## 错误处理：Result 类型

对于预期错误，使用 `Result<T, TError>` 而不是异常。仅对意外/系统错误使用异常。

有关完整的 Result 类型实现和使用示例，请参阅 [composition-and-error-handling.md](composition-and-error-handling.md)。

---

## 避免基于反射的元编程

**禁止**：AutoMapper、Mapster、ExpressMapper。使用显式映射扩展方法。当您确实需要私有成员访问时，使用 `UnsafeAccessorAttribute` (.NET 8+)。

有关完整指导，请参阅 [anti-patterns-and-reflection.md](anti-patterns-and-reflection.md)。

---

## 代码组织

```csharp
// 文件：Domain/Orders/Order.cs

namespace MyApp.Domain.Orders;

// 1. 主要领域类型
public record Order(
    OrderId Id,
    CustomerId CustomerId,
    Money Total,
    OrderStatus Status,
    IReadOnlyList<OrderItem> Items
)
{
    public bool IsCompleted => Status is OrderStatus.Completed;

    public Result<Order, OrderError> AddItem(OrderItem item)
    {
        if (Status is not OrderStatus.Draft)
            return Result<Order, OrderError>.Failure(
                new OrderError("ORDER_NOT_DRAFT", "Can only add items to draft orders"));

        var newItems = Items.Append(item).ToList();
        var newTotal = new Money(
            Items.Sum(i => i.Total.Amount) + item.Total.Amount,
            Total.Currency);

        return Result<Order, OrderError>.Success(
            this with { Items = newItems, Total = newTotal });
    }
}

// 2. 用于状态的枚举
public enum OrderStatus { Draft, Submitted, Processing, Completed, Cancelled }

// 3. 相关类型
public record OrderItem(ProductId ProductId, Quantity Quantity, Money UnitPrice)
{
    public Money Total => new(UnitPrice.Amount * Quantity.Value, UnitPrice.Currency);
}

// 4. 值对象
public readonly record struct OrderId(Guid Value)
{
    public static OrderId New() => new(Guid.NewGuid());
}

// 5. 错误
public readonly record struct OrderError(string Code, string Message);
```

---

## 最佳实践总结

### 应做

- 使用 `record` 编写 DTOs、消息和领域实体
- 使用 `readonly record struct` 编写值对象
- 使用 `switch` 表达式进行模式匹配
- 启用并尊重可空引用类型
- 使用 async/await 进行所有 I/O 操作
- 在所有异步方法中接受 `CancellationToken`
- 使用 `Span<T>` 和 `Memory<T>` 进行高性能场景
- 接受抽象 (`IEnumerable<T>`、`IReadOnlyList<T>`)
- 使用 `Result<T, TError>` 处理预期错误
- 使用 `ArrayPool<T>` 池化缓冲区进行大型分配
- 优先使用组合而非继承

### 不应做

- 当记录适用时，不要使用可变类
- 不要使用类作为值对象（使用 `readonly record struct`）
- 不要创建深度继承层次
- 不要忽略可空引用类型警告
- 不要阻塞异步代码（`.Result`、`.Wait()`）
- 当 `Span<byte>` 足够时，不要使用 `byte[]`
- 不要遗漏 `CancellationToken` 参数
- 不要从 API 返回可变集合
- 不要对预期业务错误抛出异常
- 不要重复分配大型数组（使用 `ArrayPool`）

有关详细的反模式示例，请参阅 [anti-patterns-and-reflection.md](anti-patterns-and-reflection.md)。

---

## 其他资源

- **C# 语言规范**：https://learn.microsoft.com/en-us/dotnet/csharp/
- **模式匹配**：https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/functional/pattern-matching
- **Span<T> 和 Memory<T>**：https://learn.microsoft.com/en-us/dotnet/standard/memory-and-spans/
- **异步最佳实践**：https://learn.microsoft.com/en-us/archive/msdn-magazine/2013/march/async-await-best-practices-in-asynchronous-programming
- **.NET 性能技巧**：https://learn.microsoft.com/en-us/dotnet/framework/performance/
