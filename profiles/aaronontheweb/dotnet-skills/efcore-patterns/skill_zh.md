# Entity Framework Core 模式

## 何时使用此技能

使用此技能的情况：
- 在新项目中设置 EF Core
- 优化查询性能
- 管理数据库迁移
- 将 EF Core 与 .NET Aspire 集成
- 调试变更跟踪问题
- 高效加载多个导航集合（查询拆分）

## 核心原则

1. **默认不跟踪** - 大多数查询是只读的；选择性地启用跟踪
2. **切勿手动编辑迁移** - 始终使用 CLI 命令
3. **专用的迁移服务** - 将迁移执行与应用程序启动分离
4. **执行策略用于重试** - 处理瞬态数据库故障
5. **显式更新** - 当不跟踪时，显式标记实体以进行更新

---

## 模式 1：默认不跟踪

配置你的 DbContext 以默认禁用变更跟踪。这可以提高只读工作负载的性能。

```csharp
public class ApplicationDbContext : DbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options)
    {
        // 默认禁用变更跟踪以在只读查询上提高性能
        // 对于需要跟踪更改的查询，显式使用 .AsTracking()
        ChangeTracker.QueryTrackingBehavior = QueryTrackingBehavior.NoTracking;
    }

    public DbSet<Order> Orders => Set<Order>();
    public DbSet<Customer> Customers => Set<Customer>();
}
```

### 不跟踪处于活动状态时

**只读查询正常工作：**
```csharp
// ✅ 快速读取 - 无跟踪开销
var orders = await dbContext.Orders
    .Where(o => o.Status == OrderStatus.Pending)
    .ToListAsync();
```

**写入需要显式处理：**
```csharp
// ❌ 错误 - 实体未跟踪，SaveChanges 无任何操作
var order = await dbContext.Orders.FirstOrDefaultAsync(o => o.Id == orderId);
order.Status = OrderStatus.Shipped;
await dbContext.SaveChangesAsync(); // 无任何操作！

// ✅ 正确 - 显式标记实体以进行更新
var order = await dbContext.Orders.FirstOrDefaultAsync(o => o.Id == orderId);
order.Status = OrderStatus.Shipped;
dbContext.Orders.Update(order); // 标记整个实体为已修改
await dbContext.SaveChangesAsync();

// ✅ 也正确 - 使用 AsTracking() 进行查询
var order = await dbContext.Orders
    .AsTracking()
    .FirstOrDefaultAsync(o => o.Id == orderId);
order.Status = OrderStatus.Shipped;
await dbContext.SaveChangesAsync(); // 可以正常工作！
```

### 何时使用跟踪

| 情景 | 是否使用跟踪 | 原因 |
|----------|---------------|-----|
| 在 UI 中显示数据 | 否 | 只读，无更新 |
| API GET 端点 | 否 | 返回数据，无变更 |
| 更新单个实体 | 是或显式 Update() | 需要保存更改 |
| 复杂更新涉及导航 | 是 | 跟踪处理关系 |
| 批量操作 | 否 + ExecuteUpdate | 更高效 |

### 显式 Add/Update 模式

```csharp
public class OrderService
{
    private readonly ApplicationDbContext _db;

    // 创建 - 始终使用 Add（无论是否跟踪）
    public async Task<Order> CreateOrderAsync(Order order)
    {
        _db.Orders.Add(order);
        await _db.SaveChangesAsync();
        return order;
    }

    // 更新 - 显式标记为已修改
    public async Task UpdateOrderStatusAsync(Guid orderId, OrderStatus newStatus)
    {
        var order = await _db.Orders.FirstOrDefaultAsync(o => o.Id == orderId)
            ?? throw new NotFoundException($"Order {orderId} not found");

        order.Status = newStatus;
        order.UpdatedAt = DateTimeOffset.UtcNow;

        // 由于 DbContext 默认使用不跟踪，显式标记为已修改
        _db.Orders.Update(order);
        await _db.SaveChangesAsync();
    }

    // 删除 - 附加并删除
    public async Task DeleteOrderAsync(Guid orderId)
    {
        var order = new Order { Id = orderId };
        _db.Orders.Remove(order);
        await _db.SaveChangesAsync();
    }
}
```

---

## 模式 2：切勿手动编辑迁移

**关键：** 始终使用 EF Core CLI 命令管理迁移。切勿：
- 手动编辑迁移文件（除了在 `Up()`/`Down()` 中的自定义 SQL）
- 直接删除迁移文件
- 重命名迁移文件
- 在项目之间复制迁移

### 创建迁移

```bash
# 创建新的迁移
dotnet ef migrations add AddCustomerTable \
    --project src/MyApp.Infrastructure \
    --startup-project src/MyApp.Api

# 使用特定的 DbContext（如果你有多个）
dotnet ef migrations add AddCustomerTable \
    --context ApplicationDbContext \
    --project src/MyApp.Infrastructure \
    --startup-project src/MyApp.Api
```

### 删除迁移

```bash
# 删除最后一个迁移（如果尚未应用）
dotnet ef migrations remove \
    --project src/MyApp.Infrastructure \
    --startup-project src/MyApp.Api

# 永远不要这样做：
# rm Migrations/20240101_AddCustomerTable.cs  # ❌ 错误！
```

### 应用迁移

```bash
# 应用所有待处理的迁移
dotnet ef database update \
    --project src/MyApp.Infrastructure \
    --startup-project src/MyApp.Api

# 应用到特定迁移
dotnet ef database update AddCustomerTable \
    --project src/MyApp.Infrastructure \
    --startup-project src/MyApp.Api

# 回滚到之前的迁移
dotnet ef database update PreviousMigrationName \
    --project src/MyApp.Infrastructure \
    --startup-project src/MyApp.Api
```

### 生成 SQL 脚本

```bash
# 生成所有迁移的 SQL 脚本
dotnet ef migrations script \
    --project src/MyApp.Infrastructure \
    --startup-project src/MyApp.Api \
    --output migrations.sql

# 生成幂等脚本（安全多次运行）
dotnet ef migrations script \
    --idempotent \
    --project src/MyApp.Infrastructure \
    --startup-project src/MyApp.Api
```

---

## 模式 3：使用 Aspire 的专用迁移服务

使用专用的迁移服务将迁移执行与你的主应用程序分离。这确保了：
- 迁移在应用程序启动之前完成
- 清晰的关注点分离
- 在测试环境中受控的播种

### 项目结构

```
src/
├── MyApp.AppHost/           # Aspire 编排
├── MyApp.Api/               # 主应用程序
├── MyApp.Infrastructure/    # DbContext 和迁移
└── MyApp.MigrationService/  # 专用的迁移执行者
```

### MigrationService Program.cs

```csharp
using MyApp.Infrastructure.Data;
using MyApp.MigrationService;
using Microsoft.EntityFrameworkCore;

var builder = Host.CreateApplicationBuilder(args);

// 添加 Aspire 服务默认值
builder.AddServiceDefaults();

// 添加 PostgreSQL DbContext
var connectionString = builder.Configuration.GetConnectionString("appdb")
    ?? throw new InvalidOperationException("Connection string 'appdb' not found.");

builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseNpgsql(connectionString, npgsqlOptions =>
        npgsqlOptions.MigrationsAssembly("MyApp.Infrastructure")));

// 添加迁移工作程序
builder.Services.AddHostedService<MigrationWorker>();

var host = builder.Build();
host.Run();
```

### MigrationWorker.cs

```csharp
public class MigrationWorker : BackgroundService
{
    private readonly IServiceProvider _serviceProvider;
    private readonly IHostApplicationLifetime _hostApplicationLifetime;
    private readonly ILogger<MigrationWorker> _logger;

    public MigrationWorker(
        IServiceProvider serviceProvider,
        IHostApplicationLifetime hostApplicationLifetime,
        ILogger<MigrationWorker> logger)
    {
        _serviceProvider = serviceProvider;
        _hostApplicationLifetime = hostApplicationLifetime;
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("Migration service starting...");

        try
        {
            using var scope = _serviceProvider.CreateScope();
            var dbContext = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();

            await RunMigrationsAsync(dbContext, stoppingToken);

            _logger.LogInformation("Migration service completed successfully.");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Migration service failed: {Error}", ex.Message);
            throw;
        }
        finally
        {
            // 迁移完成后停止应用程序
            _hostApplicationLifetime.StopApplication();
        }
    }

    private async Task RunMigrationsAsync(ApplicationDbContext dbContext, CancellationToken ct)
    {
        // 使用执行策略处理瞬态故障
        var strategy = dbContext.Database.CreateExecutionStrategy();

        await strategy.ExecuteAsync(async () =>
        {
            var pendingMigrations = await dbContext.Database.GetPendingMigrationsAsync(ct);

            if (pendingMigrations.Any())
            {
                _logger.LogInformation("Applying {Count} pending migrations...",
                    pendingMigrations.Count());

                await dbContext.Database.MigrateAsync(ct);

                _logger.LogInformation("Migrations applied successfully.");
            }
            else
            {
                _logger.LogInformation("No pending migrations. Database is up to date.");
            }
        });
    }
}
```

### AppHost 配置

```csharp
var builder = DistributedApplication.CreateBuilder(args);

var postgres = builder.AddPostgres("postgres");
var db = postgres.AddDatabase("appdb");

// 迁移首先运行，然后退出
var migrations = builder.AddProject<Projects.MyApp_MigrationService>("migrations")
    .WaitFor(db)
    .WithReference(db);

// API 等待迁移完成
var api = builder.AddProject<Projects.MyApp_Api>("api")
    .WaitForCompletion(migrations)  // 关键：等待迁移完成
    .WithReference(db);
```

---

## 模式 4：执行策略用于瞬态故障

始终使用 `CreateExecutionStrategy()` 处理可能瞬态失败的操作：

```csharp
public async Task UpdateWithRetryAsync(Guid id, Action<Order> update)
{
    var strategy = _dbContext.Database.CreateExecutionStrategy();

    await strategy.ExecuteAsync(async () =>
    {
        var order = await _dbContext.Orders
            .AsTracking()
            .FirstOrDefaultAsync(o => o.Id == id);

        if (order is null) return;

        update(order);
        await _dbContext.SaveChangesAsync();
    });
}
```

**重要：** 不能使用 `CreateExecutionStrategy()` 与用户发起的事务。如果你需要带重试的事务：

```csharp
var strategy = _dbContext.Database.CreateExecutionStrategy();

await strategy.ExecuteAsync(async () =>
{
    // 事务必须在策略回调内部
    await using var transaction = await _dbContext.Database.BeginTransactionAsync();

    try
    {
        // ... 你的操作 ...
        await _dbContext.SaveChangesAsync();
        await transaction.CommitAsync();
    }
    catch
    {
        await transaction.RollbackAsync();
        throw;
    }
});
```

---

## 批量操作与 ExecuteUpdate/ExecuteDelete

对于批量操作，使用 EF Core 7+ `ExecuteUpdateAsync` 和 `ExecuteDeleteAsync` 而不是加载实体：

```csharp
// ❌ 慢 - 将所有实体加载到内存中
var expiredOrders = await _db.Orders
    .Where(o => o.ExpiresAt < DateTimeOffset.UtcNow)
    .ToListAsync();

foreach (var order in expiredOrders)
{
    order.Status = OrderStatus.Expired;
}
await _db.SaveChangesAsync();

// ✅ 快 - 单个 SQL UPDATE 语句
await _db.Orders
    .Where(o => o.ExpiresAt < DateTimeOffset.UtcNow)
    .ExecuteUpdateAsync(setters => setters
        .SetProperty(o => o.Status, OrderStatus.Expired)
        .SetProperty(o => o.UpdatedAt, DateTimeOffset.UtcNow));

// ✅ 快 - 单个 SQL DELETE 语句
await _db.Orders
    .Where(o => o.Status == OrderStatus.Cancelled && o.CreatedAt < cutoffDate)
    .ExecuteDeleteAsync();
```

---

## 常见陷阱

### 1. 忘记在不跟踪时更新

```csharp
// ❌ 静默失败 - 实体未跟踪
var customer = await _db.Customers.FindAsync(id);
customer.Name = "New Name";
await _db.SaveChangesAsync(); // 无任何操作！

// ✅ 显式更新
var customer = await _db.Customers.FindAsync(id);
customer.Name = "New Name";
_db.Customers.Update(customer);
await _db.SaveChangesAsync();
```

### 2. N+1 查询问题

```csharp
// ❌ N+1 查询 - 每个订单一个查询
var customers = await _db.Customers.ToListAsync();
foreach (var customer in customers)
{
    var orders = customer.Orders; // 懒加载触发查询
}

// ✅ 激烈加载 - 单个查询
var customers = await _db.Customers
    .Include(c => c.Orders)
    .ToListAsync();
```

### 3. 跟踪与多个 DbContext 实例冲突

```csharp
// ❌ 跟踪冲突 - 不同上下文跟踪实体
var order1 = await _db1.Orders.AsTracking().FindAsync(id);
var order2 = await _db2.Orders.AsTracking().FindAsync(id);
order2.Status = OrderStatus.Shipped;
await _db2.SaveChangesAsync(); // 可能抛出异常或行为异常

// ✅ 使用单个上下文或先分离
_db1.Entry(order1).State = EntityState.Detached;
```

### 4. 不一致使用异步

```csharp
// ❌ 阻塞调用 - 异步上下文中
var orders = _db.Orders.ToList(); // 阻塞线程

// ✅ 全程异步
var orders = await _db.Orders.ToListAsync();
```

### 5. 在循环中查询

```csharp
// ❌ 每次迭代查询
foreach (var orderId in orderIds)
{
    var order = await _db.Orders.FindAsync(orderId);
    // 处理订单
}

// ✅ 单个查询
var orders = await _db.Orders
    .Where(o => orderIds.Contains(o.Id))
    .ToListAsync();
```

---

## DbContext 在 DI 中的生命周期

### ASP.NET Core（默认作用域）

```csharp
// 作用域 = 每个HTTP请求一个实例
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseNpgsql(connectionString));
```

### 后台服务（创建作用域）

```csharp
public class MyBackgroundService : BackgroundService
{
    private readonly IServiceProvider _serviceProvider;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        // ✅ 为每个工作单元创建作用域
        using var scope = _serviceProvider.CreateScope();
        var dbContext = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();

        // ... 使用 dbContext ...
    }
}
```

### Actor / 长生命对象（工厂模式）

```csharp
public class OrderActor : ReceiveActor
{
    private readonly IDbContextFactory<ApplicationDbContext> _dbFactory;

    public OrderActor(IDbContextFactory<ApplicationDbContext> dbFactory)
    {
        _dbFactory = dbFactory;

        ReceiveAsync<GetOrder>(async msg =>
        {
            // 为每个操作创建新的上下文
            await using var db = await _dbFactory.CreateDbContextAsync();
            var order = await db.Orders.FindAsync(msg.OrderId);
            Sender.Tell(order);
        });
    }
}

// 注册
builder.Services.AddDbContextFactory<ApplicationDbContext>(options =>
    options.UseNpgsql(connectionString));
```

---

## 模式 6：查询拆分以防止笛卡尔积

当你通过 `Include()` 加载多个导航集合时，EF Core 生成单个查询，这可能导致笛卡尔积。如果你有 10 个订单，每个订单有 10 个项目，你会得到 100 行而不是 10 + 10。

### 全局配置（大多数情况下推荐）

在你的 DbContext 配置中全局启用查询拆分：

```csharp
services.AddDbContext<ApplicationDbContext>(options =>
    options.UseNpgsql(connectionString, npgsqlOptions =>
        {
            npgsqlOptions.UseQuerySplittingBehavior(QuerySplittingBehavior.SplitQuery);
        }));
```

### 每个查询覆盖

当你知道它更高效时使用单个查询：

```csharp
// 当你知道结构理解良好时使用单个查询
var orders = await dbContext.Orders
    .Include(o => o.Items)
    .Include(o => o.Payments)
    .AsSingleQuery()  // 覆盖全局拆分行为
    .ToListAsync();
```

### 权衡

| 行为 | 优点 | 缺点 |
|-----------|-------|-------|
| SplitQuery | 无笛卡尔积，适用于大集合 | 多次往返，潜在一致性问题 |
| SingleQuery | 单次往返，事务一致性 | 笛卡尔积涉及多个集合 |

**建议：** 默认全局使用 `SplitQuery`，对于特定查询使用 `AsSingleQuery()` 知道单个查询更好。

### 何时优先使用 SingleQuery

- 小型、理解良好的导航图（2-3 级）
- 查询总是需要所有相关数据
- 性能关键路径，往返成本低于笛卡尔积

### 何时优先使用 SplitQuery

- 大型或不可预测的导航图
- 多对多关系
- 查询加载可能不需要的所有集合

---

## 使用 EF Core 进行测试

### In-Memory Provider（仅单元测试）

```csharp
// 仅用于简单的单元测试 - 不匹配真实数据库行为
var options = new DbContextOptionsBuilder<ApplicationDbContext>()
    .UseInMemoryDatabase(databaseName: Guid.NewGuid().ToString())
    .Options;

using var context = new ApplicationDbContext(options);
```

### 使用 TestContainers 的真实数据库（集成测试）

参见 `testcontainers-integration-tests` 技能进行正确的数据库测试。

```csharp
// 使用容器中的真实 PostgreSQL
var container = new PostgreSqlBuilder()
    .WithImage("postgres:16-alpine")
    .Build();

await container.StartAsync();

var options = new DbContextOptionsBuilder<ApplicationDbContext>()
    .UseNpgsql(container.GetConnectionString())
    .Options;
```
