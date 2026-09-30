---
name: modern-csharp
description: 现代 C# 语言特性，适用于 .NET 10 和 C# 14。涵盖主要构造函数、集合表达式、字段关键字、扩展成员、记录、模式匹配、跨度（spans）和原始字符串字面量。在编写任何新的 C# 代码、审查现有代码以实现现代化、使用“现代 C#”、“C# 14”、“主要构造函数”、“集合表达式”、“记录”、“模式匹配”、“跨度”、“字段关键字”或“扩展成员”时，请加载此技能。始终作为所有代理的基准加载。
---

# 现代 C# (C# 14 / .NET 10)

## 核心原则

1. **使用最新的稳定特性** — C# 14 是目标。优先选择语言级构造，而非库的解决方案。
2. **可读性优于技巧** — 模式匹配和表达式成员体在适当使用时能提升可读性；过度嵌套的模式则相反。
3. **尽可能使用值类型** — 优先选择 `record struct`、`Span<T>` 和栈分配，以减少 GC 压力。
4. **默认不可变** — 使用 `record`、`readonly`、`init` 和 `required` 使非法状态不可表示。

## 模式

### 知名特性快速参考

| 特性 | 用法 | 示例 |
|------|------|------|
| 主要构造器 | 依赖注入，消除字段赋值 | `public class OrderService(IOrderRepo repo, TimeProvider clock) { }` |
| 集合表达式 | `[]` 用于所有集合类型 + 展开操作符 | `List<string> names = ["Alice", "Bob"];` / `int[] all = [..a, ..b, 99];` |
| 记录类型 | DTO、值对象、不可变数据 | `public record CreateOrderRequest(string CustomerId, List<OrderItem> Items);` |
| `readonly record struct` | 小型栈分配值类型 | `public readonly record struct Money(decimal Amount, string Currency);` |
| 模式匹配 | `switch` 表达式、列表/属性模式 | `order switch { { Total: > 1000 } => "Premium", _ => "Standard" };` |
| 列表模式 | 解构数组/列表 | `items switch { [] => "Empty", [var x] => $"One: {x}", [var f, .., var l] => $"{f}..{l}" };` |
| `Span<T>` | 零分配切片 | `ReadOnlySpan<char> trimmed = input.Trim(); int.TryParse(trimmed[4..], out id);` |
| 原始字符串字面量 | 多行 SQL、JSON、XML | `var sql = """ SELECT ... """;` / 插值：`$$""" {"id": "{{id}}"} """;` |
| `required` 成员 | 强制初始化 | `public required string ConnectionString { get; init; }` |
| `is` 模式 + 提取 | 空值/类型/属性检查 | `if (result is { IsSuccess: true, Value: var order }) { ... }` |

### `field` 关键字 (C# 14)

在属性访问器中直接访问自动生成的后备字段，无需手动声明。

```csharp
// GOOD — field 关键字用于自动属性的验证
public class Product
{
    public string Name
    {
        get => field;
        set => field = value?.Trim() ?? throw new ArgumentNullException(nameof(value));
    }

    public decimal Price
    {
        get => field;
        set => field = value >= 0 ? value : throw new ArgumentOutOfRangeException(nameof(value));
    }
}
```

#### 使用 `field` 实现延迟初始化

```csharp
public class ProductCatalog
{
    // 第一次访问时懒加载 — 无需手动 Lazy<T> 或后备字段
    public IReadOnlyList<Product> Products
    {
        get => field ??= LoadProducts();
    }

    private static List<Product> LoadProducts() => /* 昂贵加载 */;
}
```

#### 使用 `field` 实现变更通知

```csharp
// 无需手动后备字段的 INotifyPropertyChanged
public class OrderViewModel : INotifyPropertyChanged
{
    public event PropertyChangedEventHandler? PropertyChanged;

    public string CustomerName
    {
        get => field;
        set
        {
            if (field == value) return;
            field = value;
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(nameof(CustomerName)));
        }
    } = "";

    public decimal Total
    {
        get => field;
        set
        {
            if (field == value) return;
            field = value;
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(nameof(Total)));
        }
    }
}
```

### 扩展成员 (C# 14)

C# 14 在静态类中添加了 `extension` 块。与经典扩展方法不同，它们支持扩展**属性**和**静态**扩展成员 — 接收者在整个块中只声明一次。

```csharp
// GOOD — 扩展块 (C# 14 语法)
public static class OrderExtensions
{
    extension(Order order)
    {
        public decimal TotalWithTax => order.Total * 1.2m;

        public bool IsHighValue => order.Total > 1000m;

        public string ToSummary() =>
            $"Order #{order.Id}: {order.Total:C} ({order.Items.Count} items)";
    }

    // 静态扩展成员使用类型 (无需接收者实例)
    extension(Order)
    {
        public static Order Empty => Order.Create("none", [], DateTimeOffset.MinValue);
    }
}

// 调用者视其如 Order 类型上声明
if (order.IsHighValue) { /* ... */ }
```

经典 `this`-参数扩展方法仍然有效且共存 — 当需要同一接收者上多个属性或成员时，使用扩展块。

## 反模式

### 当现代替代方案存在时，不要使用过时的模式

```csharp
// BAD — 使用 field 关键字时仍手动声明后备字段
private string _name;
public string Name
{
    get => _name;
    set => _name = value ?? throw new ArgumentNullException();
}

// BAD — 旧式集合初始化
var list = new List<int>() { 1, 2, 3 };

// BAD — 使用 Tuple 而非记录处理领域类型
(string Name, decimal Price) product = ("Widget", 9.99m);
// GOOD — 使用记录
public record Product(string Name, decimal Price);
```

### 不要过度使用模式匹配

```csharp
// BAD — 过度嵌套的难以阅读的模式
if (order is { Customer: { Address: { Country: { Code: "US" } } } })

// GOOD — 提取到清晰的方法或使用顺序检查
if (order.Customer.Address.Country.Code == "US")
```

### 当类型不明显时，不要使用 `var`

```csharp
// BAD — 这是什么类型？
var result = Process(order);

// GOOD — 类型不明显时显式声明
Result<Order> result = Process(order);
// 也 GOOD — 类型明显时 var 完美
var orders = new List<Order>();
```

## 决策指南

| 场景 | 建议 |
|------|------|
| DTO / API 合约 | `record` (引用类型) |
| 小型值对象 (2-3 字段) | `readonly record struct` |
| 依赖注入的服务 | 主要构造器 |
| 集合创建 | 集合表达式 `[]` |
| 带验证的属性 | `field` 关键字 |
| 多行字符串 (SQL、JSON) | 原始字符串字面量 `"""` |
| 切片字符串/数组 | `Span<T>` |
| 类型检查 + 提取 | 带有 `is` / `switch` 的模式匹配 |
| 强制初始化 | `required` 修饰符 |
| 为外部类型添加方法 | 扩展成员 |
