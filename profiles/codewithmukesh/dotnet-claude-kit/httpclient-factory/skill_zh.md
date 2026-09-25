# HttpClient 工厂

## 核心原则

1. **每个请求都不要 `new HttpClient()`** — 原始 `HttpClient` 创建会导致在高负载下套接字耗尽，并且忽略 DNS 变更。使用 `IHttpClientFactory` 来管理处理器生命周期。
2. **键值客户端优于类型化客户端** — 在 .NET 10 中，键值依赖注入（`.AddAsKeyed()`）是推荐的模式。在单例中捕获的类型化客户端会无声地破坏处理器轮换。
3. **弹性不是可选的** — 每个外部 HTTP 调用都需要重试、断路器和超时。`AddStandardResilienceHandler()` 提供一行代码中的合理默认值。
4. **使用 DelegatingHandlers 处理横切关注点** — 认证令牌、关联 ID 和日志记录应属于处理器管道，而不是分散在服务方法中。

## 模式

### 带弹性的命名客户端

```csharp
builder.Services.AddHttpClient("github", client =>
{
    client.BaseAddress = new Uri("https://api.github.com/");
    client.DefaultRequestHeaders.UserAgent.ParseAdd("MyApp/1.0");
    client.DefaultRequestHeaders.Accept.Add(
        new MediaTypeWithQualityHeaderValue("application/json"));
})
.AddStandardResilienceHandler();

// 通过工厂使用
public sealed class GitHubService(IHttpClientFactory factory)
{
    public async Task<Repo?> GetRepoAsync(string owner, string name, CancellationToken ct)
    {
        var client = factory.CreateClient("github");
        return await client.GetFromJsonAsync<Repo>($"repos/{owner}/{name}", ct);
    }
}
```

### 键值客户端（.NET 10 推荐模式）

结合了命名客户端的配置灵活性和直接注入。无需字符串查找。

```csharp
builder.Services.AddHttpClient("payments", client =>
{
    client.BaseAddress = new Uri("https://api.payments.example.com/");
})
.AddStandardResilienceHandler()
.AddAsKeyed();  // 注册为键值作用域服务

// 直接注入 — 无需 IHttpClientFactory
app.MapPost("/charge", async (
    [FromKeyedServices("payments")] HttpClient httpClient,
    ChargeRequest request,
    CancellationToken ct) =>
{
    var response = await httpClient.PostAsJsonAsync("charges", request, ct);
    return response.IsSuccessStatusCode
        ? TypedResults.Ok()
        : TypedResults.Problem("Payment failed");
});
```

全局选择：`builder.Services.ConfigureHttpClientDefaults(b => b.AddAsKeyed());`

### 标准弹性处理器

`AddStandardResilienceHandler()` 链接了 5 种策略：

| 策略 | 默认值 |
|------|--------|
| 速率限制器 | 1000 个并发请求 |
| 总超时 | 30 秒 |
| 重试 | 3 次重试，带抖动的指数退避 |
| 断路器 | 失败率达到 10% 时触发 |
| 尝试超时 | 每次尝试 10 秒 |

```csharp
builder.Services.AddHttpClient("api")
    .AddStandardResilienceHandler(options =>
    {
        options.Retry.MaxRetryAttempts = 5;
        options.Retry.Delay = TimeSpan.FromSeconds(1);
        options.TotalRequestTimeout.Timeout = TimeSpan.FromSeconds(60);
        options.AttemptTimeout.Timeout = TimeSpan.FromSeconds(15);

        // 对于非幂等方法禁用重试
        options.Retry.DisableForUnsafeHttpMethods();
    });
```

### 用于认证令牌注入的 DelegatingHandler

```csharp
public sealed class AuthenticationHandler(ITokenService tokenService)
    : DelegatingHandler
{
    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken)
    {
        var token = await tokenService.GetAccessTokenAsync(cancellationToken);
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        return await base.SendAsync(request, cancellationToken);
    }
}

// 注册
builder.Services.AddTransient<AuthenticationHandler>();
builder.Services.AddHttpClient("api")
    .AddHttpMessageHandler<AuthenticationHandler>()
    .AddStandardResilienceHandler();
```

### 用于关联 ID 传播的 DelegatingHandler

```csharp
public sealed class CorrelationIdHandler(IHttpContextAccessor httpContextAccessor)
    : DelegatingHandler
{
    protected override Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken)
    {
        if (httpContextAccessor.HttpContext?.Request.Headers
                .TryGetValue("X-Correlation-Id", out var correlationId) is true)
        {
            request.Headers.Add("X-Correlation-Id", correlationId.ToString());
        }
        return base.SendAsync(request, cancellationToken);
    }
}
```

### SocketsHttpHandler 配置

```csharp
builder.Services.AddHttpClient("advanced")
    .UseSocketsHttpHandler((handler, _) =>
    {
        handler.PooledConnectionLifetime = TimeSpan.FromMinutes(2);
        handler.PooledConnectionIdleTimeout = TimeSpan.FromMinutes(1);
        handler.MaxConnectionsPerServer = 100;
        handler.AutomaticDecompression =
            DecompressionMethods.GZip | DecompressionMethods.Brotli;
    });
```

### 使用 Mock Handler 进行测试

```csharp
public sealed class MockHttpHandler(
    HttpStatusCode statusCode,
    string content) : HttpMessageHandler
{
    protected override Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken)
    {
        return Task.FromResult(new HttpResponseMessage(statusCode)
        {
            Content = new StringContent(content, Encoding.UTF8, "application/json")
        });
    }
}

// 在测试中
var handler = new MockHttpHandler(HttpStatusCode.OK, """{"id":1}""");
var client = new HttpClient(handler) { BaseAddress = new Uri("https://api.test/") };
var service = new MyService(client);
```

## 反模式

### 不要每个请求创建 HttpClient

```csharp
// BAD — 高负载下套接字耗尽，忽略 DNS 变更
public async Task<string> GetDataAsync()
{
    using var client = new HttpClient();
    return await client.GetStringAsync("https://api.example.com/data");
}

// GOOD — 工厂管理
public async Task<string> GetDataAsync(CancellationToken ct)
{
    var client = factory.CreateClient("api");
    return await client.GetStringAsync("https://api.example.com/data", ct);
}
```

### 不要在单例中捕获类型化客户端

```csharp
// BAD — 临时 HttpClient 被单例捕获，破坏处理器轮换
services.AddSingleton<MySingletonService>();
services.AddHttpClient<MySingletonService>();

// GOOD — 在单例中使用键值客户端或 IHttpClientFactory
services.AddSingleton<MySingletonService>();
services.AddHttpClient("myservice").AddAsKeyed(ServiceLifetime.Singleton);
```

### 不要在共享客户端上修改 DefaultRequestHeaders

```csharp
// BAD — 不是线程安全的
httpClient.DefaultRequestHeaders.Authorization =
    new AuthenticationHeaderValue("Bearer", token);

// GOOD — 使用 DelegatingHandler 或每个请求的 HttpRequestMessage
using var request = new HttpRequestMessage(HttpMethod.Get, "/api/data");
request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
await httpClient.SendAsync(request, ct);
```

### 不要忘记 CancellationToken

```csharp
// BAD — 没有取消支持
var result = await httpClient.GetFromJsonAsync<Order>("/orders/1");

// GOOD — 总是传递 CancellationToken
var result = await httpClient.GetFromJsonAsync<Order>("/orders/1", cancellationToken);
```

### 不要堆叠多个弹性处理器

```csharp
// BAD — 冲突的弹性策略
builder.AddStandardResilienceHandler();
builder.AddStandardHedgingHandler();

// GOOD — 一个标准处理器，或自定义管道
builder.AddStandardResilienceHandler();
```

## 决策指南

| 场景 | 推荐方案 |
|------|---------|
| 新的 .NET 10 项目 | 使用 `AddAsKeyed()` 的键值客户端 |
| 单例服务需要 HttpClient | 通过 `IHttpClientFactory` 的命名客户端或键值单例 |
| 外部 API 调用 | 每个客户端上使用 `AddStandardResilienceHandler()` |
| 认证令牌注入 | 使用 `AddHttpMessageHandler` 注册的 `DelegatingHandler` |
| 保险（并行请求） | 对于延迟敏感的调用使用 `AddStandardHedgingHandler()` |
| 非幂等方法 | 在重试选项上使用 `DisableForUnsafeHttpMethods()` |
| 自定义重试逻辑 | 使用 `AddResilienceHandler("name", builder => ...)` |
| 连接池控制 | 使用 `UseSocketsHttpHandler` 和 `PooledConnectionLifetime` |
| API 客户端生成 | 使用 `AddRefitClient<T>()` |
| 集成测试 | 自定义 `HttpMessageHandler` 或 `MockHttpMessageHandler` |
