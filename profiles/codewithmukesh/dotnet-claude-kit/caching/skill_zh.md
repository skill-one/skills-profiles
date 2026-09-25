# 缓存

## 核心原则

1. **HybridCache 是默认选项** — .NET 9+ 引入了 `HybridCache` 作为统一的缓存抽象。它结合了内存（L1）和分布式（L2）缓存，并具有雪崩保护。参见 ADR-004。
2. **缓存读取操作，而非写入操作** — 缓存 GET 操作。在数据变更时使缓存失效。永远不要缓存 POST/PUT/DELETE 响应。
3. **对整个响应进行输出缓存** — 当完整的 HTTP 响应可以被缓存时（公共 API、静态数据），使用输出缓存中间件。
4. **设置明确的 TTL** — 每个缓存项都需要过期时间。不要使用无界缓存。

## 模式

### HybridCache（推荐默认）

```csharp
// Program.cs
builder.Services.AddHybridCache(options =>
{
    options.DefaultEntryOptions = new HybridCacheEntryOptions
    {
        Expiration = TimeSpan.FromMinutes(5),
        LocalCacheExpiration = TimeSpan.FromMinutes(2)
    };
});

// 可选：添加 Redis 作为 L2 分布式缓存
builder.Services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = builder.Configuration.GetConnectionString("Redis");
});
```

```csharp
// 在处理器中使用
public class GetProduct
{
    public record Query(Guid Id);
    public record Response(Guid Id, string Name, decimal Price);

    internal class Handler(AppDbContext db, HybridCache cache)
    {
        public async Task<Response?> Handle(Query query, CancellationToken ct)
        {
            return await cache.GetOrCreateAsync(
                $"products:{query.Id}",
                async token => await db.Products
                    .Where(p => p.Id == query.Id)
                    .Select(p => new Response(p.Id, p.Name, p.Price))
                    .FirstOrDefaultAsync(token),
                new HybridCacheEntryOptions
                {
                    Expiration = TimeSpan.FromMinutes(10)
                },
                cancellationToken: ct);
        }
    }
}
```

### 缓存失效

```csharp
// 在数据变更时使缓存失效
public class UpdateProduct
{
    internal class Handler(AppDbContext db, HybridCache cache)
    {
        public async Task<Result> Handle(Command command, CancellationToken ct)
        {
            var product = await db.Products.FindAsync([command.Id], ct);
            if (product is null) return Result.Failure("Product not found");

            product.Update(command.Name, command.Price);
            await db.SaveChangesAsync(ct);

            // 使缓存项失效
            await cache.RemoveAsync($"products:{command.Id}", ct);

            return Result.Success();
        }
    }
}
```

### 输出缓存（完整响应缓存）

```csharp
// Program.cs
builder.Services.AddOutputCache(options =>
{
    options.AddBasePolicy(b => b.NoCache()); // 默认不缓存

    options.AddPolicy("ProductList", b => b
        .Expire(TimeSpan.FromMinutes(5))
        .Tag("products"));

    options.AddPolicy("ProductById", b => b
        .Expire(TimeSpan.FromMinutes(10))
        .SetVaryByRouteValue("id")
        .Tag("products"));
});

app.UseOutputCache();

// 应用于端点
group.MapGet("/", ListProducts).CacheOutput("ProductList");
group.MapGet("/{id:guid}", GetProduct).CacheOutput("ProductById");

// 在数据变更时通过标签使缓存失效
group.MapPut("/{id:guid}", async (Guid id, UpdateProductRequest request,
    IOutputCacheStore store, CancellationToken ct) =>
{
    // ... 更新逻辑 ...
    await store.EvictByTagAsync("products", ct);
    return TypedResults.NoContent();
});
```

### 旁路缓存模式（遗留）

> **所有新代码都应优先使用 HybridCache**。手动 `IDistributedCache` 旁路缓存缺乏雪崩保护，需要手动序列化，且没有 L1/L2 分层。仅在集成已直接使用 `IDistributedCache` 的现有代码时使用。

## 反模式

### 不要无过期时间地缓存

```csharp
// BAD — 缓存永存，保证数据过时
await cache.SetStringAsync(key, value);

// GOOD — 始终设置 TTL
await cache.SetStringAsync(key, value, new DistributedCacheEntryOptions
{
    AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(10)
});
```

### 不要缓存可变用户特定数据

```csharp
// BAD — 使用全局键缓存用户的购物车
await cache.GetOrCreateAsync("shopping-cart", ...);

// GOOD — 在键中包含用户 ID
await cache.GetOrCreateAsync($"shopping-cart:{userId}", ...);
```

### 不要自行实现雪崩保护

```csharp
// BAD — 使用手动锁防止缓存雪崩
private static readonly SemaphoreSlim Lock = new(1, 1);
await Lock.WaitAsync();
try { /* 检查缓存，如果缺失则填充 */ }
finally { Lock.Release(); }

// GOOD — HybridCache 具有内置的雪崩保护
await hybridCache.GetOrCreateAsync(key, factory);
```

## 决策指南

| 场景 | 建议 |
|------|------|
| 一般数据缓存 | HybridCache (`GetOrCreateAsync`) |
| 完整 HTTP 响应 | 使用 `.CacheOutput()` 的输出缓存 |
| 常读少写 | 使用具有较长 TTL 的 HybridCache |
| 用户特定数据 | 使用用户范围键的 HybridCache |
| 写入时的缓存失效 | `cache.RemoveAsync()` 或输出缓存标签 |
| 分布式部署 | HybridCache + Redis L2 后端 |
| 单服务器部署 | 仅使用内存的 HybridCache |
