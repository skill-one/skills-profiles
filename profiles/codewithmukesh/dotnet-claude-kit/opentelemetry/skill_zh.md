# OpenTelemetry

## 核心原则

1. **三大支柱，单一配置** — 通过单个 `AddOpenTelemetry()` 调用配置追踪、指标和日志。使用 `UseOtlpExporter()` 进行跨切面导出到任何 OTLP 兼容的后端。
2. **使用 `IMeterFactory` 配置指标** — 永远不要用 `new` 创建 `Meter` 实例。工厂通过依赖注入管理生命周期并防止内存泄漏。
3. **空安全活动** — `StartActivity()` 在未附加监听器时返回 `null`。设置标签或事件时始终使用 `?.`。
4. **环境变量优于代码** — 使用 `OTEL_EXPORTER_OTLP_ENDPOINT` 和 `OTEL_SERVICE_NAME`，以便部署控制遥测路由而无需修改代码。
5. **低基数指标标签** — 将每个仪器的指标标签组合保持在 ~1000 个以下。使用追踪属性或日志处理用户 ID 或请求 ID 等高基数数据。

## 模式

### 全部三个信号完整配置

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddOpenTelemetry()
    .ConfigureResource(resource => resource
        .AddService(
            serviceName: builder.Environment.ApplicationName,
            serviceVersion: "1.0.0"))
    .WithTracing(tracing => tracing
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddEntityFrameworkCoreInstrumentation()
        .AddSource("MyApp.Orders"))
    .WithMetrics(metrics => metrics
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddRuntimeInstrumentation()
        .AddMeter("MyApp.Orders"))
    .WithLogging()             // 这里没有针对每个信号的导出器——
    .UseOtlpExporter();        // UseOtlpExporter 覆盖所有三个信号

// UseOtlpExporter 替代针对每个信号的 AddOtlpExporter 调用。永远不要混用
// 这两种方式——混合使用会抛出 NotSupportedException（参见反模式）。
```

OTLP 端点默认为 `http://localhost:4317`（gRPC）。通过以下方式覆盖：
```
OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4317
OTEL_SERVICE_NAME=MyApp.Api
```

### 使用 IMeterFactory 的自定义指标

将指标类注册为单例。`IMeterFactory` 通过依赖注入处理 `Meter` 的销毁。

```csharp
public sealed class OrderMetrics
{
    private readonly Counter<int> _ordersCreated;
    private readonly Histogram<double> _orderDuration;
    private readonly UpDownCounter<int> _activeOrders;
    private readonly Gauge<double> _queueDepth;

    public OrderMetrics(IMeterFactory meterFactory)
    {
        var meter = meterFactory.Create("MyApp.Orders");

        _ordersCreated = meter.CreateCounter<int>(
            "myapp.orders.created", "{orders}", "创建的订单数量");

        _orderDuration = meter.CreateHistogram<double>(
            "myapp.orders.duration", "s", "订单处理时长",
            advice: new InstrumentAdvice<double>
            {
                HistogramBucketBoundaries = [0.01, 0.05, 0.1, 0.5, 1, 5, 10]
            });

        _activeOrders = meter.CreateUpDownCounter<int>(
            "myapp.orders.active", "{orders}", "当前活跃的订单");

        _queueDepth = meter.CreateGauge<double>(
            "myapp.orders.queue_depth", "{items}", "当前队列深度");
    }

    public void OrderCreated() => _ordersCreated.Add(1);
    public void RecordDuration(double seconds) => _orderDuration.Record(seconds);
    public void OrderStarted() => _activeOrders.Add(1);
    public void OrderCompleted() => _activeOrders.Add(-1);
    public void SetQueueDepth(double depth) => _queueDepth.Record(depth);
}

// 注册
builder.Services.AddSingleton<OrderMetrics>();
```

### 多维度指标标签

三个或更少的标签是无分配的。更多则使用 `TagList`。

```csharp
// 无分配（3个或更少标签）
_ordersCreated.Add(1,
    new KeyValuePair<string, object?>("order.type", "standard"),
    new KeyValuePair<string, object?>("payment.method", "credit_card"));

// 4+ 标签 — 使用 TagList 避免分配
var tags = new TagList
{
    { "order.type", "standard" },
    { "payment.method", "credit_card" },
    { "region", "us-east" },
    { "priority", "high" }
};
_ordersCreated.Add(1, tags);
```

### 自定义分布式追踪的 ActivitySource

```csharp
public sealed class OrderService(ILogger<OrderService> logger)
{
    private static readonly ActivitySource Source = new("MyApp.Orders");

    public async Task<Order> ProcessOrderAsync(CreateOrderRequest request, CancellationToken ct)
    {
        using var activity = Source.StartActivity("ProcessOrder", ActivityKind.Internal);
        activity?.SetTag("order.customer_id", request.CustomerId);

        try
        {
            await ValidateOrder(request, ct);
            activity?.AddEvent(new ActivityEvent("OrderValidated"));

            var order = await SaveOrder(request, ct);
            activity?.SetTag("order.id", order.Id.ToString());
            activity?.SetStatus(ActivityStatusCode.Ok);
            return order;
        }
        catch (Exception ex)
        {
            activity?.SetStatus(ActivityStatusCode.Error, ex.Message);
            activity?.RecordException(ex);
            throw;
        }
    }
}
```

在追踪构建器中注册源：`.AddSource("MyApp.Orders")`。

### 本地开发用 Aspire 控制台

无 Aspire 协调的情况下运行独立 Aspire 控制台：

```bash
docker run --rm -it -p 18888:18888 -p 4317:18889 \
    mcr.microsoft.com/dotnet/aspire-dashboard:latest
```

然后指向你的应用：
```
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

控制台 UI 在 `http://localhost:18888`。

### 使用 OTel 的源生成日志

为最高性能，使用 `[LoggerMessage]` — 消除装箱和分配。

```csharp
public partial class OrderService(ILogger<OrderService> logger)
{
    [LoggerMessage(Level = LogLevel.Information,
        Message = "处理订单 {OrderId} 为客户 {CustomerId}")]
    partial void LogOrderProcessing(Guid orderId, Guid customerId);
}
```

OpenTelemetry 日志在当前 `Activity` 时自动包含 `TraceId` 和 `SpanId`。

## 反模式

### 不要每个请求创建 Meter

```csharp
// BAD — 每个请求创建 Meter 导致内存泄漏
public void HandleRequest()
{
    var meter = new Meter("MyApp");
    meter.CreateCounter<int>("requests").Add(1);
}

// GOOD — 通过 IMeterFactory 单例
public class MyMetrics(IMeterFactory meterFactory)
{
    private readonly Counter<int> _requests =
        meterFactory.Create("MyApp").CreateCounter<int>("myapp.requests");
    public void RequestHandled() => _requests.Add(1);
}
```

### 不要在 Activity 上跳过空检查

```csharp
// BAD — 无监听器时抛出 NullReferenceException
using var activity = source.StartActivity("Work");
activity.SetTag("key", "value");

// GOOD — 空安全
activity?.SetTag("key", "value");
```

### 不要使用高基数指标标签

```csharp
// BAD — 无限基数导致收集器内存爆炸
_counter.Add(1, new("request.id", Guid.NewGuid().ToString()));
_counter.Add(1, new("user.id", userId));

// GOOD — 仅使用低基数维度
_counter.Add(1, new("http.method", "GET"), new("http.status_code", 200));
```

### 不要混用 UseOtlpExporter 与 AddOtlpExporter

```csharp
// BAD — 运行时抛出 NotSupportedException
builder.Services.AddOpenTelemetry()
    .UseOtlpExporter()
    .WithTracing(t => t.AddOtlpExporter());

// GOOD — 使用一种方法
builder.Services.AddOpenTelemetry().UseOtlpExporter();
```

### 不要忘记注册自定义源

```csharp
// BAD — 活动（无监听器注册）被静默丢弃
var source = new ActivitySource("MyApp.Custom");
using var activity = source.StartActivity("Work"); // null!

// GOOD — 在追踪构建器中注册
otel.WithTracing(t => t.AddSource("MyApp.Custom"));
otel.WithMetrics(m => m.AddMeter("MyApp.Custom"));
```

## 决策指南

| 场景 | 建议 |
|------|------|
| 完整可观测性配置 | `AddOpenTelemetry()` 全部三个信号 + `UseOtlpExporter()` |
| 自定义业务指标 | `IMeterFactory` + 单例指标类 |
| 自定义追踪片段 | `ActivitySource` + `StartActivity()` |
| 本地开发后端 | 独立 Aspire 控制台容器 |
| 生产后端 | OTel 收集器作为中间层到 Grafana/Datadog 等 |
| 生产中的采样 | `OTEL_TRACES_SAMPLER=parentbased_traceidratio` 10% 比率 |
| 高性能日志 | `[LoggerMessage]` 源生成器 |
| 指标标签基数 | 每个仪器最多 ~1000 组组合 |
| 环境配置 | `OTEL_*` 环境变量（也通过 `appsettings.json` 工作） |
