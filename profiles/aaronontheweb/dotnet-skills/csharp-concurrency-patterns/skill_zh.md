# .NET 并发：选择合适的工具

## 何时使用这项技能

在以下情况下使用这项技能：
- 决定如何在 .NET 中处理并发操作
- 评估是否应使用 Channels、Akka.NET 或其他抽象
- 考虑使用锁、信号量或其他同步原语
- 需要处理具有背压、批处理或防抖的数据流
- 跨多个并发实体管理状态

## 参考文件

- [advanced-concurrency.md](advanced-concurrency.md)：Akka.NET Streams、Reactive Extensions、Akka.NET Actors（每个实体一个 Actor、状态机、集群分片）和 async local 函数模式

## 哲学思想

**从简单开始，仅在需要时升级。**

大多数并发问题都可以通过 `async/await` 解决。只有当你有特定需求且 `async/await` 无法简洁地解决时，才应使用更复杂的工具。

**尽量避免共享可变状态。** 处理并发最好的方式是将其设计出去。不可变数据、消息传递和隔离状态（如 Actors）可以消除整个类别的错误。

**锁应该是例外，而不是规则。** 当你无法避免共享可变状态时：
1. **首选方案**：重新设计以避免它（不可变性、消息传递、Actor 隔离）
2. **次选方案**：使用 `System.Collections.Concurrent`（ConcurrentDictionary 等）
3. **第三选方案**：使用 `Channel<T>` 通过消息传递序列化访问
4. **最后手段**：使用 `lock` 处理简单、短暂的临界区

---

## 决策树

```
你在尝试做什么？
│
├─► 等待 I/O（HTTP、数据库、文件）？
│   └─► 使用 async/await
│
├─► 并行处理集合（CPU 密集型）？
│   └─► 使用 Parallel.ForEachAsync
│
├─► 生产者/消费者模式（工作队列）？
│   └─► 使用 System.Threading.Channels
│
├─► UI 事件处理（防抖、节流、组合）？
│   └─► 使用 Reactive Extensions (Rx)
│
├─► 服务器端流处理（背压、批处理）？
│   └─► 使用 Akka.NET Streams
│
├─► 复杂状态转换的状态机？
│   └─► 使用 Akka.NET Actors（Become 模式）
│
├─► 管理许多独立实体的状态？
│   └─► 使用 Akka.NET Actors（每个实体一个 Actor）
│
├─► 协调多个异步操作？
│   └─► 使用 Task.WhenAll / Task.WhenAny
│
└─► 以上都不适用？
    └─► 问自己：“我真的需要共享可变状态吗？”
        ├─► 是 → 考虑重新设计以避免它
        └─► 真正无法避免 → 使用 Channels 或 Actors 来序列化访问
```

---

## 第 1 级：async/await（默认选择）

**用于**：I/O 密集型操作、非阻塞等待、大多数日常并发。

```csharp
// 简单的异步 I/O
public async Task<Order> GetOrderAsync(string orderId, CancellationToken ct)
{
    var order = await _database.GetAsync(orderId, ct);
    var customer = await _customerService.GetAsync(order.CustomerId, ct);
    return order with { Customer = customer };
}

// 并行异步操作（当独立时）
public async Task<Dashboard> LoadDashboardAsync(string userId, CancellationToken ct)
{
    var ordersTask = _orderService.GetRecentOrdersAsync(userId, ct);
    var notificationsTask = _notificationService.GetUnreadAsync(userId, ct);
    var statsTask = _statsService.GetUserStatsAsync(userId, ct);

    await Task.WhenAll(ordersTask, notificationsTask, statsTask);

    return new Dashboard(
        Orders: await ordersTask,
        Notifications: await notificationsTask,
        Stats: await statsTask);
}
```

**关键原则**：始终接受 `CancellationToken`。在库代码中使用 `ConfigureAwait(false)`。不要在异步代码上阻塞。

---

## 第 2 级：Parallel.ForEachAsync（CPU 密集型并行）

**用于**：当工作为 CPU 密集型或需要受控并发时，并行处理集合。

```csharp
public async Task ProcessOrdersAsync(
    IEnumerable<Order> orders,
    CancellationToken ct)
{
    await Parallel.ForEachAsync(
        orders,
        new ParallelOptions
        {
            MaxDegreeOfParallelism = Environment.ProcessorCount,
            CancellationToken = ct
        },
        async (order, token) =>
        {
            await ProcessOrderAsync(order, token);
        });
}
```

**不使用的情况**：纯 I/O 操作、顺序重要、需要背压。

---

## 第 3 级：System.Threading.Channels（生产者/消费者）

**用于**：工作队列、生产者/消费者模式、解耦生产者和消费者。

```csharp
public class OrderProcessor
{
    private readonly Channel<Order> _channel;

    public OrderProcessor()
    {
        _channel = Channel.CreateBounded<Order>(new BoundedChannelOptions(100)
        {
            FullMode = BoundedChannelFullMode.Wait
        });
    }

    // 生产者
    public async Task EnqueueOrderAsync(Order order, CancellationToken ct)
    {
        await _channel.Writer.WriteAsync(order, ct);
    }

    // 消费者（作为后台任务运行）
    public async Task ProcessOrdersAsync(CancellationToken ct)
    {
        await foreach (var order in _channel.Reader.ReadAllAsync(ct))
        {
            await ProcessOrderAsync(order, ct);
        }
    }

    public void Complete() => _channel.Writer.Complete();
}
```

**Channels 的优点**：解耦速度、带背压的缓冲、分发给工作线程、后台队列。

**Channels 的缺点**：不适合复杂流操作（批处理、窗口）、状态化每个实体处理、复杂的监督。

---

## 第 4 级及以上：Akka.NET Streams、Reactive Extensions、Actors

对于需要流处理、UI 事件组合或状态化实体管理的先进场景，请参阅 [advanced-concurrency.md](advanced-concurrency.md)。

**Akka.NET Streams** 在服务器端批处理、节流和背压方面表现出色。**Reactive Extensions** 非常适合 UI 事件组合。**Akka.NET Actors** 处理每个实体一个 Actor 模式、`Become()` 的状态机以及通过集群分片进行分布式系统管理。

---

## 反模式：应避免的做法

### 用于业务逻辑的锁

```csharp
// 错误：使用锁保护共享状态
private readonly object _lock = new();
private Dictionary<string, Order> _orders = new();

public void UpdateOrder(string id, Action<Order> update)
{
    lock (_lock) { if (_orders.TryGetValue(id, out var order)) update(order); }
}

// 正确：使用 Actor 或 Channel 来序列化访问
```

### 手动线程管理

```csharp
// 错误：手动创建线程
var thread = new Thread(() => ProcessOrders());
thread.Start();

// 正确：使用 Task.Run 或更好的抽象
_ = Task.Run(() => ProcessOrdersAsync(cancellationToken));
```

### 异步代码中的阻塞

```csharp
// 错误：在异步上阻塞 - 死锁风险！
var result = GetDataAsync().Result;

// 正确：全程异步
var result = await GetDataAsync();
```

### 没有保护的共享可变状态

```csharp
// 错误：多个任务修改共享状态
var results = new List<Result>();
await Parallel.ForEachAsync(items, async (item, ct) =>
{
    var result = await ProcessAsync(item, ct);
    results.Add(result); // 竞态条件！
});

// 正确：使用 ConcurrentBag
var results = new ConcurrentBag<Result>();
```

---

## 快速参考：何时使用哪个工具？

| 需求 | 工具 | 示例 |
|------|------|---------|
| 等待 I/O | `async/await` | HTTP 调用、数据库查询 |
| 并行 CPU 工作 | `Parallel.ForEachAsync` | 图像处理、计算 |
| 工作队列 | `Channel<T>` | 后台任务处理 |
| UI 事件防抖/节流 | Reactive Extensions | 输入时搜索、自动保存 |
| 服务器端批处理/节流 | Akka.NET Streams | 事件聚合、速率限制 |
| 状态机 | Akka.NET Actors | 支付流程、订单生命周期 |
| 实体状态管理 | Akka.NET Actors | 订单管理、用户会话 |
| 执行多个异步操作 | `Task.WhenAll` | 加载仪表板数据 |
| 竞态多个异步操作 | `Task.WhenAny` | 超时与回退 |
| 定期工作 | `PeriodicTimer` | 健康检查、轮询 |

---

## 升级路径

```
async/await（从这里开始）
    │
    ├─► 需要并行性？ → Parallel.ForEachAsync
    │
    ├─► 需要生产者/消费者？ → Channel<T>
    │
    ├─► 需要UI事件组合？ → Reactive Extensions
    │
    ├─► 需要服务器端流处理？ → Akka.NET Streams
    │
    └─► 需要状态机或实体管理？ → Akka.NET Actors
```

**仅在明确需要时升级。** 不要因为“以防万一”而使用 Actors 或 Streams。
