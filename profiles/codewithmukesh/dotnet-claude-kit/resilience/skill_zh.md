# 弹性

## 核心原则

1. **使用 Polly v8 弹性管道，而非 v7 策略** — Polly v8 将 `Policy` 替换为 `ResiliencePipeline`。切勿使用 `PolicyBuilder`、`Policy.Handle<>()` 或 `ISyncPolicy`。新 API 可组合、类型安全，并原生集成 `IHttpClientFactory`。
2. **通过 `AddResilienceHandler` 配置，而非手动包装** — 对于 HTTP 调用，使用 `Microsoft.Extensions.Http.Resilience`，它通过依赖注入直接将管道添加到 `HttpClient`。无需手动 `ExecuteAsync` 包装。
3. **组合策略，而非嵌套策略** — 单个 `ResiliencePipeline` 可以链式组合重试 + 电路断路器 + 超时。策略按外到内执行（先添加的为最外层）。无需嵌套 try/catch 或手动编排。
4. **始终设置超时** — 每个外部调用都需要超时。使用 Polly 的 `AddTimeout()` 作为最内层策略，使其应用于每次尝试，并可选地设置外层超时以限制总耗时。
5. **监控所有操作** — Polly v8 发射 `Metering` 事件，并支持 `TelemetryOptions` 用于 OpenTelemetry。使用它们监控重试率、电路断路器状态和超时频率。

## 模式

### HTTP 客户端弹性（推荐默认）

```csharp
// Program.cs — 标准弹性处理器覆盖 90% 的用例
builder.Services.AddHttpClient<IPaymentGateway, PaymentGatewayClient>(client =>
{
    client.BaseAddress = new Uri("https://api.payments.example.com");
})
.AddStandardResilienceHandler(); // 开箱即用的重试 + 电路断路器 + 超时

// 就这些。标准处理器配置：
// - 重试：3 次尝试，指数退避，抖动
// - 电路断路器：30 秒采样内 10% 的失败率，30 秒断开
// - 每次尝试超时：10 秒
// - 总请求超时：30 秒
```

**原因**：`AddStandardResilienceHandler()` 从 `Microsoft.Extensions.Http.Resilience` 应用生产就绪的默认值。仅在需要不同阈值时才覆盖。

### 自定义 HTTP 弹性配置

```csharp
builder.Services.AddHttpClient<ICatalogService, CatalogServiceClient>(client =>
{
    client.BaseAddress = new Uri("https://api.catalog.example.com");
})
.AddResilienceHandler("catalog", builder =>
{
    // 总超时 — 最外层，限制总耗时
    builder.AddTimeout(TimeSpan.FromSeconds(15));

    // 重试 — 指数退避带抖动
    builder.AddRetry(new HttpRetryStrategyOptions
    {
        MaxRetryAttempts = 3,
        BackoffType = DelayBackoffType.Exponential,
        UseJitter = true,
        Delay = TimeSpan.FromMilliseconds(500),
        ShouldHandle = static args => ValueTask.FromResult(
            args.Outcome.Result?.StatusCode is HttpStatusCode.RequestTimeout
                or HttpStatusCode.TooManyRequests
                or HttpStatusCode.ServiceUnavailable
                || args.Outcome.Exception is HttpRequestException)
    });

    // 电路断路器 — 防止级联故障
    builder.AddCircuitBreaker(new HttpCircuitBreakerStrategyOptions
    {
        FailureRatio = 0.5,
        SamplingDuration = TimeSpan.FromSeconds(10),
        MinimumThroughput = 10,
        BreakDuration = TimeSpan.FromSeconds(30)
    });

    // 每次尝试超时 — 最内层
    builder.AddTimeout(TimeSpan.FromSeconds(5));
});
```

**原因**：命名弹性处理器允许按服务进行微调。顺序很重要：总超时 > 重试 > 电路断路器 > 每次尝试超时。

### 非 HTTP 弹性管道

```csharp
// 用于数据库调用、消息队列或任何非 HTTP 操作
builder.Services.AddResiliencePipeline("database", builder =>
{
    builder
        .AddRetry(new RetryStrategyOptions
        {
            MaxRetryAttempts = 3,
            BackoffType = DelayBackoffType.Exponential,
            Delay = TimeSpan.FromMilliseconds(200),
            ShouldHandle = new PredicateBuilder()
                .Handle<TimeoutException>()
                .Handle<InvalidOperationException>(ex =>
                    ex.Message.Contains("deadlock", StringComparison.OrdinalIgnoreCase))
        })
        .AddTimeout(TimeSpan.FromSeconds(10));
});

// 注入和使用
public sealed class OrderRepository(
    AppDbContext db,
    [FromKeyedServices("database")] ResiliencePipeline pipeline)
{
    public async Task<Order?> GetByIdAsync(Guid id, CancellationToken ct)
    {
        return await pipeline.ExecuteAsync(
            async token => await db.Orders.FindAsync([id], token),
            ct);
    }
}
```

**原因**：`AddResiliencePipeline` 在依赖注入中注册一个命名管道。使用 `[FromKeyedServices]` 进行干净、可测试的代码。

### 类型化弹性管道

```csharp
// 当操作返回特定类型时，使用 ResiliencePipeline<T>
builder.Services.AddResiliencePipeline<string, HttpResponseMessage>("external-api", builder =>
{
    builder
        .AddFallback(new FallbackStrategyOptions<HttpResponseMessage>
        {
            FallbackAction = static args =>
            {
                var response = new HttpResponseMessage(HttpStatusCode.OK)
                {
                    Content = new StringContent("{\"status\":\"degraded\",\"data\":[]}")
                };
                return Outcome.FromResultAsValueTask(response);
            },
            ShouldHandle = static args => ValueTask.FromResult(
                args.Outcome.Exception is not null
                || args.Outcome.Result?.IsSuccessStatusCode == false)
        })
        .AddRetry(new RetryStrategyOptions<HttpResponseMessage>
        {
            MaxRetryAttempts = 2,
            Delay = TimeSpan.FromMilliseconds(500)
        })
        .AddTimeout(TimeSpan.FromSeconds(5));
});
```

**原因**：类型化管道允许在所有重试耗尽时添加回退策略以返回默认值——对优雅降级至关重要。

### 分散风险（并行请求）

```csharp
builder.Services.AddHttpClient<ISearchService, SearchServiceClient>()
    .AddResilienceHandler("search-hedging", builder =>
    {
        builder.AddHedging(new HttpHedgingStrategyOptions
        {
            MaxHedgedAttempts = 2,
            Delay = TimeSpan.FromMilliseconds(500) // 500 毫秒后发送并行请求
        });
        builder.AddTimeout(TimeSpan.FromSeconds(3));
    });
```

**原因**：如果第一个请求在延迟内未响应，则发送并行请求。用于对延迟敏感的读取，可以容忍重复工作。

### 拉取式监控集成

```csharp
builder.Services.AddResiliencePipeline("monitored", (builder, context) =>
{
    // Polly v8 自动通过 System.Diagnostics.Metrics 发射指标。
    // ConfigureTelemetry 为策略事件配置结构化日志记录。
    builder
        .ConfigureTelemetry(new TelemetryOptions
        {
            LoggerFactory = context.ServiceProvider.GetRequiredService<ILoggerFactory>()
        })
        .AddRetry(new RetryStrategyOptions { MaxRetryAttempts = 3 })
        .AddCircuitBreaker(new CircuitBreakerStrategyOptions())
        .AddTimeout(TimeSpan.FromSeconds(10));
});

// 在 Program.cs — 将 OpenTelemetry 链接到捕获 Polly 指标
builder.Services.AddOpenTelemetry()
    .WithMetrics(metrics => metrics.AddMeter("Polly"));
```

### 速率限制 (.NET 内置)

.NET 提供通过 `AddRateLimiter()` 的内置速率限制中间件——无需外部包。算法：`AddFixedWindowLimiter`、`AddSlidingWindowLimiter`、`AddTokenBucketLimiter`、`AddConcurrencyLimiter`。

```csharp
builder.Services.AddRateLimiter(options =>
{
    options.AddFixedWindowLimiter("fixed", opt =>
    {
        opt.PermitLimit = 100;
        opt.Window = TimeSpan.FromSeconds(60);
        opt.QueueLimit = 0;
    });

    // 总是返回 ProblemDetails 并包含 Retry-After 在 429
    options.OnRejected = async (context, ct) =>
    {
        context.HttpContext.Response.StatusCode = StatusCodes.Status429TooManyRequests;
        if (context.Lease.TryGetMetadata(MetadataName.RetryAfter, out var retryAfter))
            context.HttpContext.Response.Headers.RetryAfter =
                ((int)retryAfter.TotalSeconds).ToString();
        await context.HttpContext.Response.WriteAsJsonAsync(
            new ProblemDetails { Title = "Too many requests", Status = 429 }, ct);
    };
});

app.UseRateLimiter();
app.MapGet("/api/orders", ListOrders).RequireRateLimiting("fixed");
```

## 反模式

### BAD: 使用 Polly v7 API

```csharp
// BAD — v7 策略语法，不要使用
var retryPolicy = Policy
    .Handle<HttpRequestException>()
    .WaitAndRetryAsync(3, attempt => TimeSpan.FromSeconds(Math.Pow(2, attempt)));

var response = await retryPolicy.ExecuteAsync(() => httpClient.GetAsync("/api/data"));
```

### GOOD: Polly v8 弹性管道

```csharp
// GOOD — 通过 DI 使用 v8 管道
builder.Services.AddHttpClient<IDataService, DataServiceClient>()
    .AddStandardResilienceHandler();
```

---

### BAD: 手动包装每个调用

```csharp
// BAD — 每个调用点手动弹性
public async Task<Order> GetOrderAsync(Guid id)
{
    try
    {
        return await _pipeline.ExecuteAsync(async ct =>
            await _httpClient.GetFromJsonAsync<Order>($"/orders/{id}", ct));
    }
    catch (TimeoutRejectedException)
    {
        return Order.Empty;
    }
    catch (BrokenCircuitException)
    {
        return Order.Empty;
    }
}
```

### GOOD: 通过 HttpClient DI 处理所有弹性

```csharp
// GOOD — 弹性在 HttpClient 层配置
public async Task<Order?> GetOrderAsync(Guid id, CancellationToken ct)
{
    var response = await _httpClient.GetAsync($"/orders/{id}", ct);
    if (!response.IsSuccessStatusCode) return null;
    return await response.Content.ReadFromJsonAsync<Order>(ct);
}
```

---

### BAD: 在非幂等操作上重试

```csharp
// BAD — 重试 POST 可能导致资源重复创建
builder.AddRetry(new RetryStrategyOptions
{
    MaxRetryAttempts = 5 // 这将在瞬态故障时创建 5 个订单！
});
```

### GOOD: 仅重试幂等操作或使用幂等键

```csharp
// GOOD — 为非幂等操作添加幂等键头
builder.AddRetry(new HttpRetryStrategyOptions
{
    MaxRetryAttempts = 3,
    ShouldHandle = static args => ValueTask.FromResult(
        args.Outcome.Result?.StatusCode is HttpStatusCode.RequestTimeout
            or HttpStatusCode.ServiceUnavailable)
});

// 与请求中的幂等键配对
httpClient.DefaultRequestHeaders.Add("Idempotency-Key", Guid.NewGuid().ToString());
```

---

### BAD: 无监控的电路断路器

```csharp
// BAD — 无状态变更可见性的电路断路器
builder.AddCircuitBreaker(new CircuitBreakerStrategyOptions());
// 你如何知道何时触发？你不知道。
```

### GOOD: 带有监控的电路断路器

```csharp
// GOOD — Polly v8 指标通过 OpenTelemetry 捕获
builder.Services.AddOpenTelemetry()
    .WithMetrics(metrics => metrics.AddMeter("Polly"));

// 仪表板警报：polly.circuit_breaker.state = Open
```

## 决策指南

| 场景 | 策略 | 配置 |
|------|------|------|
| 外部 API 的 HTTP 调用 | `AddStandardResilienceHandler()` | 使用默认值，仅覆盖特定阈值 |
| 带自定义阈值的 HTTP | `AddResilienceHandler("name", ...)` | 命名处理器按服务微调 |
| 数据库 / EF Core 调用 | `AddResiliencePipeline("db", ...)` | 重试死锁/超时，无电路断路器 |
| 消息队列发布 | `AddResiliencePipeline("mq", ...)` | 指数退避重试，超时 |
| 对延迟敏感的读取 | `AddHedging(...)` | 延迟阈值后发送并行请求 |
| 优雅降级 | `AddFallback(...)` | 总失败时返回缓存/默认值 |
| 每次尝试时间限制 | `AddTimeout(...)` 最内层 | 2-10 秒取决于操作 |
| 总操作时间限制 | `AddTimeout(...)` 最外层 | 所有重试 + 缓冲的总和 |
| 非幂等写入 | 带幂等键重试 | 或不重试——快速失败 |
| 读取密集型微服务 | 标准处理器 + 分散风险 | 低延迟带冗余 |
| API 速率限制 | `AddRateLimiter()` + `RequireRateLimiting()` | 每个端点固定、滑动或令牌桶 |
