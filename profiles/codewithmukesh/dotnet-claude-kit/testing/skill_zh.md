# 测试 (.NET 10)

## 核心原则

1. **集成测试是最高价值的测试** — 单个 `WebApplicationFactory` 测试可一次性覆盖路由、绑定、验证、业务逻辑和持久化。在编写单元测试之前，从这里开始。
2. **测试中使用真实数据库** — 使用 Testcontainers 启动真实的 PostgreSQL/SQL Server 实例。内存提供程序会隐藏真实错误（事务、约束、SQL 生成）。
3. **AAA 模式是强制性的** — 每个测试都有三个明确分隔的部分：Arrange、Act、Assert。不允许混合。
4. **测试行为而非实现** — 测试应能经受重构。测试系统做了什么，而不是它如何做。

## 模式

### xUnit v3 基础

```csharp
public class OrderServiceTests
{
    [Fact]
    public async Task CreateOrder_WithValidItems_ReturnsSuccessResult()
    {
        // Arrange
        var db = CreateInMemoryDb();
        var clock = new FakeTimeProvider(new DateTimeOffset(2025, 1, 15, 0, 0, 0, TimeSpan.Zero));
        var service = new OrderService(db, clock);
        var request = new CreateOrderRequest("customer-1", [new("product-1", 2)]);

        // Act
        var result = await service.CreateAsync(request);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.NotEqual(Guid.Empty, result.Value.Id);
        Assert.Equal(clock.GetUtcNow(), result.Value.CreatedAt);
    }

    [Theory]
    [InlineData("")]
    [InlineData(null)]
    public async Task CreateOrder_WithInvalidCustomerId_ReturnsFailure(string? customerId)
    {
        // Arrange
        var service = CreateService();

        // Act
        var result = await service.CreateAsync(new CreateOrderRequest(customerId!, []));

        // Assert
        Assert.False(result.IsSuccess);
    }
}
```

### 使用 WebApplicationFactory 的集成测试

最高价值的测试模式。测试完整的 HTTP 管道。

```csharp
// Fixtures/ApiFixture.cs
public class ApiFixture : WebApplicationFactory<Program>, IAsyncLifetime
{
    private readonly PostgreSqlContainer _postgres = new PostgreSqlBuilder()
        .WithImage("postgres:18")
        .Build();

    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.ConfigureServices(services =>
        {
            // 使用 Testcontainers 替换真实数据库
            services.RemoveAll<DbContextOptions<AppDbContext>>();
            services.AddDbContext<AppDbContext>(options =>
                options.UseNpgsql(_postgres.GetConnectionString()));
        });
    }

    // xUnit v3: IAsyncLifetime.InitializeAsync 返回 ValueTask (v2 使用 Task)
    public async ValueTask InitializeAsync()
    {
        await _postgres.StartAsync();

        // 应用迁移
        using var scope = Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        await db.Database.MigrateAsync();
    }

    // xUnit v3: IAsyncLifetime 继承 IAsyncDisposable — 重写 WebApplicationFactory 已提供的
    // ValueTask DisposeAsync
    public override async ValueTask DisposeAsync()
    {
        await _postgres.DisposeAsync();
        await base.DisposeAsync();
    }
}
```

```csharp
// Tests/Orders/CreateOrderTests.cs
public class CreateOrderTests(ApiFixture fixture) : IClassFixture<ApiFixture>
{
    private readonly HttpClient _client = fixture.CreateClient();

    [Fact]
    public async Task CreateOrder_ReturnsCreated_WithValidRequest()
    {
        // Arrange
        var request = new CreateOrderRequest("customer-1", [new("product-1", 2)]);

        // Act
        var response = await _client.PostAsJsonAsync("/api/orders", request);

        // Assert
        Assert.Equal(HttpStatusCode.Created, response.StatusCode);

        var order = await response.Content.ReadFromJsonAsync<OrderResponse>();
        Assert.NotNull(order);
        Assert.NotEqual(Guid.Empty, order.Id);
        Assert.Contains("/api/orders/", response.Headers.Location?.ToString());
    }

    [Fact]
    public async Task CreateOrder_ReturnsValidationProblem_WithEmptyItems()
    {
        // Arrange
        var request = new CreateOrderRequest("customer-1", []);

        // Act
        var response = await _client.PostAsJsonAsync("/api/orders", request);

        // Assert
        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
    }
}
```

### 使用 Testcontainers 进行真实数据库测试

```csharp
// 用于 SQL Server
private readonly MsSqlContainer _mssql = new MsSqlBuilder()
    .WithImage("mcr.microsoft.com/mssql/server:2022-latest")
    .Build();

// 用于 PostgreSQL
private readonly PostgreSqlContainer _postgres = new PostgreSqlBuilder()
    .WithImage("postgres:18")
    .Build();

// 用于 Redis
private readonly RedisContainer _redis = new RedisBuilder()
    .WithImage("redis:7")
    .Build();
```

### Verify 快照测试

用于复杂响应对象，手动断言会脆弱的情况。

```csharp
[Fact]
public async Task GetOrder_MatchesSnapshot()
{
    // Arrange
    await SeedOrder(fixture);

    // Act
    var response = await _client.GetAsync("/api/orders/known-id");
    var content = await response.Content.ReadAsStringAsync();

    // Assert — 与存储的 .verified.txt 文件比较
    await Verify(content);
}
```

首次运行时，Verify 会创建一个 `.verified.txt` 文件。后续运行时，它会比较输出。如果输出发生变化，测试会失败并显示差异。

### 测试数据构建器

```csharp
public class OrderBuilder
{
    private string _customerId = "default-customer";
    private List<OrderItem> _items = [new("product-1", 1, 9.99m)];
    private OrderStatus _status = OrderStatus.Pending;

    public OrderBuilder WithCustomer(string customerId)
    {
        _customerId = customerId;
        return this;
    }

    public OrderBuilder WithItems(params OrderItem[] items)
    {
        _items = [..items];
        return this;
    }

    public OrderBuilder WithStatus(OrderStatus status)
    {
        _status = status;
        return this;
    }

    public Order Build() => Order.Create(_customerId, _items, _status);
}

// 测试中使用
var order = new OrderBuilder()
    .WithCustomer("vip-customer")
    .WithStatus(OrderStatus.Confirmed)
    .Build();
```

### 测试依赖时间的代码

使用 `TimeProvider`（.NET 8+ 内置）和 `FakeTimeProvider`（来自 `Microsoft.Extensions.TimeProvider.Testing`）。

```csharp
[Fact]
public async Task ExpireOrders_MarksOldPendingOrdersAsExpired()
{
    // Arrange
    var clock = new FakeTimeProvider(new DateTimeOffset(2025, 6, 1, 0, 0, 0, TimeSpan.Zero));
    var db = CreateDb();
    var order = Order.Create("customer-1", items, clock.GetUtcNow());
    db.Orders.Add(order);
    await db.SaveChangesAsync();

    // 跳过过期阈值的时间
    clock.Advance(TimeSpan.FromDays(31));

    var handler = new ExpireOrders.Handler(db, clock);

    // Act
    await handler.Handle(new ExpireOrders.Command(), CancellationToken.None);

    // Assert
    var updated = await db.Orders.FindAsync(order.Id);
    Assert.Equal(OrderStatus.Expired, updated!.Status);
}
```

### 测试命名约定

使用模式：`方法名_状态下_预期行为`

```csharp
[Fact] public async Task CreateOrder_WithValidItems_ReturnsSuccessResult() { }
[Fact] public async Task CreateOrder_WithEmptyItems_ReturnsValidationError() { }
[Fact] public async Task GetOrder_WithNonExistentId_ReturnsNotFound() { }
[Fact] public async Task CancelOrder_WhenAlreadyShipped_ReturnsConflict() { }
```

## 反模式

### 不要在集成测试中使用内存数据库

```csharp
// BAD — 隐藏真实的 SQL 行为、事务、约束
services.AddDbContext<AppDbContext>(options =>
    options.UseInMemoryDatabase("TestDb"));

// GOOD — 使用 Testcontainers 和真实数据库
services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(testContainer.GetConnectionString()));
```

### 不要测试实现细节

```csharp
// BAD — 测试特定仓库方法是否被调用
mock.Verify(x => x.AddAsync(It.IsAny<Order>()), Times.Once);
mock.Verify(x => x.SaveChangesAsync(), Times.Once);

// GOOD — 测试可观察的结果
var order = await db.Orders.FindAsync(orderId);
Assert.NotNull(order);
Assert.Equal(OrderStatus.Created, order.Status);
```

### 不要在测试之间共享可变状态

```csharp
// BAD — 静态共享状态
private static readonly AppDbContext SharedDb = CreateDb();

// GOOD — 每个测试的新鲜状态（或使用 IAsyncLifetime 共享固定装置）
private AppDbContext CreateDb() => new(new DbContextOptionsBuilder<AppDbContext>()...);
```

### 不要编写无断言的测试

```csharp
// BAD — 没有断言，只检查没有抛出异常
[Fact]
public async Task CreateOrder_Works()
{
    await service.CreateAsync(request);
    // "它没有抛出异常，所以它工作！" — NO
}

// GOOD — 断言预期结果
[Fact]
public async Task CreateOrder_PersistsOrderToDatabase()
{
    var result = await service.CreateAsync(request);

    var persisted = await db.Orders.FindAsync(result.Value.Id);
    Assert.NotNull(persisted);
    Assert.Equal(request.CustomerId, persisted.CustomerId);
}
```

## 决策指南

| 场景 | 建议 |
|------|------|
| 测试 API 端点 | `WebApplicationFactory` 集成测试 |
| 独立测试业务逻辑 | 使用假/桩的单元测试 |
| 依赖数据库的测试 | Testcontainers（真实数据库） |
| 复杂响应验证 | Verify 快照测试 |
| 依赖时间的逻辑 | `FakeTimeProvider` |
| 外部 API 依赖 | `WireMock.Net` 或 `HttpMessageHandler` 桩 |
| 参数化测试用例 | `[Theory]` 与 `[InlineData]` 或 `[MemberData]` |
| 测试数据设置 | 构建器模式 |
| 共享昂贵的固定装置 | `IClassFixture<T>` 与 `IAsyncLifetime` |
