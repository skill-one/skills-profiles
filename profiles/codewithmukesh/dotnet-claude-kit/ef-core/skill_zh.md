# EF Core (.NET 10)

## 核心原则

1. **EF Core 是默认的 ORM** — 除非有特定原因（如极端性能需求、没有外键约束的遗留数据库），否则应使用它。参见 ADR-003。
2. **DbContext 是一个工作单元** — 不要用另一个工作单元抽象来包装它。EF Core 内部已经实现了工作单元和仓库模式。
3. **查询应该是投影** — 使用 `.Select()` 将其投影到 DTO 中，而不是加载完整实体。这可以避免过度获取和 N+1 问题。
4. **迁移是代码** — 将其像任何其他源代码一样对待。审查它们，测试它们，生产环境中永远不要自动应用。

## 模式

### DbContext 配置

使用 `IEntityTypeConfiguration<T>` 将实体配置保持分离并可发现。

```csharp
// Persistence/AppDbContext.cs
public class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
{
    public DbSet<Order> Orders => Set<Order>();
    public DbSet<Product> Products => Set<Product>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
    }
}

// Persistence/Configurations/OrderConfiguration.cs
public class OrderConfiguration : IEntityTypeConfiguration<Order>
{
    public void Configure(EntityTypeBuilder<Order> builder)
    {
        builder.HasKey(o => o.Id);

        builder.Property(o => o.Total)
            .HasPrecision(18, 2);

        builder.HasMany(o => o.Items)
            .WithOne()
            .HasForeignKey(i => i.OrderId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasIndex(o => o.CustomerId);
        builder.HasIndex(o => o.CreatedAt);
    }
}
```

### 注册

```csharp
// Program.cs
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("Default")));
```

### 查询投影（避免过度获取）

```csharp
// 良好实践 — 投影到 DTO，只加载需要的列
public async Task<OrderResponse?> GetOrderAsync(Guid id, CancellationToken ct)
{
    return await db.Orders
        .Where(o => o.Id == id)
        .Select(o => new OrderResponse(
            o.Id,
            o.Total,
            o.CreatedAt,
            o.Items.Select(i => new OrderItemResponse(i.ProductName, i.Quantity, i.Price)).ToList()))
        .FirstOrDefaultAsync(ct);
}
```

### 分页

```csharp
public async Task<PagedList<OrderSummary>> ListOrdersAsync(int page, int pageSize, CancellationToken ct)
{
    var query = db.Orders
        .OrderByDescending(o => o.CreatedAt)
        .Select(o => new OrderSummary(o.Id, o.CustomerName, o.Total, o.Status));

    var totalCount = await query.CountAsync(ct);
    var items = await query
        .Skip((page - 1) * pageSize)
        .Take(pageSize)
        .ToListAsync(ct);

    return new PagedList<OrderSummary>(items, totalCount, page, pageSize);
}
```

### ExecuteUpdateAsync / ExecuteDeleteAsync

绕过变更跟踪的批量操作，以获得更好的性能。

```csharp
// 不加载实体进行更新
await db.Orders
    .Where(o => o.Status == OrderStatus.Pending && o.CreatedAt < cutoff)
    .ExecuteUpdateAsync(s => s
        .SetProperty(o => o.Status, OrderStatus.Expired)
        .SetProperty(o => o.UpdatedAt, clock.GetUtcNow()),
        ct);

// 不加载实体进行删除
await db.Orders
    .Where(o => o.Status == OrderStatus.Cancelled && o.CreatedAt < archiveCutoff)
    .ExecuteDeleteAsync(ct);
```

### Interceptors

使用拦截器处理审计追踪和软删除等横切关注点。

```csharp
public class AuditInterceptor(TimeProvider clock) : SaveChangesInterceptor
{
    public override ValueTask<InterceptionResult<int>> SavingChangesAsync(
        DbContextEventData eventData,
        InterceptionResult<int> result,
        CancellationToken ct = default)
    {
        var context = eventData.Context;
        if (context is null) return ValueTask.FromResult(result);

        var now = clock.GetUtcNow();

        foreach (var entry in context.ChangeTracker.Entries<IAuditable>())
        {
            switch (entry.State)
            {
                case EntityState.Added:
                    entry.Entity.CreatedAt = now;
                    entry.Entity.UpdatedAt = now;
                    break;
                case EntityState.Modified:
                    entry.Entity.UpdatedAt = now;
                    break;
            }
        }

        return ValueTask.FromResult(result);
    }
}

// 注册
builder.Services.AddDbContext<AppDbContext>((sp, options) =>
    options
        .UseNpgsql(connectionString)
        .AddInterceptors(sp.GetRequiredService<AuditInterceptor>()));
```

### Compiled Queries

用于频繁执行且形状相同的查询。

```csharp
public class OrderQueries
{
    public static readonly Func<AppDbContext, Guid, CancellationToken, Task<Order?>> GetById =
        EF.CompileAsyncQuery((AppDbContext db, Guid id, CancellationToken ct) =>
            db.Orders
                .Include(o => o.Items)
                .FirstOrDefault(o => o.Id == id));
}

// 使用
var order = await OrderQueries.GetById(db, orderId, ct);
```

### Value Converters

```csharp
// 将枚举存储为字符串
builder.Property(o => o.Status)
    .HasConversion<string>()
    .HasMaxLength(50);

// 强类型 ID
public readonly record struct OrderId(Guid Value);

builder.Property(o => o.Id)
    .HasConversion(id => id.Value, value => new OrderId(value));
```

### 迁移工作流

```bash
# 创建迁移
dotnet ef migrations add AddOrderIndex --project src/MyApp.Infrastructure --startup-project src/MyApp.Api

# 审查生成的迁移 — 应用前必须始终审查
# 检查数据丢失、索引策略、约束名称

# 应用到开发数据库
dotnet ef database update --project src/MyApp.Infrastructure --startup-project src/MyApp.Api

# 生成生产 SQL 脚本
dotnet ef migrations script --idempotent --output migrations.sql
```

### Global Query Filters

```csharp
// 软删除过滤器
builder.HasQueryFilter(o => !o.IsDeleted);

// 多租户过滤器
builder.HasQueryFilter(o => o.TenantId == _tenantProvider.TenantId);

// 需要时绕过
var allOrders = await db.Orders.IgnoreQueryFilters().ToListAsync(ct);
```

## 反模式

### 不要将 DbContext 封装在仓库中

```csharp
// 不良实践 — 无谓的抽象限制了 EF Core 的能力
public interface IOrderRepository
{
    Task<Order?> GetByIdAsync(Guid id);
    Task AddAsync(Order order);
    Task SaveChangesAsync();
}

// 良好实践 — 在处理器中直接使用 DbContext
public class Handler(AppDbContext db)
{
    public async Task<Order?> Handle(GetOrder.Query query, CancellationToken ct)
    {
        return await db.Orders.FindAsync([query.Id], ct);
    }
}
```

### 不要使用懒加载

```csharp
// 不良实践 — 懒加载导致 N+1 查询并隐藏数据访问
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseLazyLoadingProxies()); // 不要这样

// 良好实践 — 使用 Include 或投影显式加载
var orders = await db.Orders
    .Include(o => o.Items)
    .Where(o => o.CustomerId == customerId)
    .ToListAsync(ct);
```

### 不要使用 .ToListAsync() 然后在内存中过滤

```csharp
// 不良实践 — 加载所有订单，在 C# 中过滤
var orders = await db.Orders.ToListAsync(ct);
var pending = orders.Where(o => o.Status == OrderStatus.Pending);

// 良好实践 — 在数据库中过滤
var pending = await db.Orders
    .Where(o => o.Status == OrderStatus.Pending)
    .ToListAsync(ct);
```

### 不要忘记等待异步方法

```csharp
// 不良实践 — 缺少 await，在保存完成前返回
public void Handle(CreateOrder.Command command)
{
    db.Orders.Add(order);
    db.SaveChangesAsync(); // 瞬发并忘 BUG
}

// 良好实践
public async Task Handle(CreateOrder.Command command, CancellationToken ct)
{
    db.Orders.Add(order);
    await db.SaveChangesAsync(ct);
}
```

## 决策指南

| 场景 | 建议 |
|------|------|
| 标准 CRUD | DbContext 与投影 |
| 批量更新（100+ 行） | `ExecuteUpdateAsync` / `ExecuteDeleteAsync` |
| 热路径读取查询 | 编译查询 |
| 复杂报表查询 | 原生 SQL 与 `FromSqlInterpolated` 或 Dapper |
| 审计追踪 | `SaveChangesInterceptor` |
| 多租户 | 全局查询过滤器 |
| 软删除 | 全局查询过滤器 + 拦截器 |
| 强类型 ID | 值转换器 |
| 生产迁移 | 等幂 SQL 脚本，永远不要自动迁移 |
