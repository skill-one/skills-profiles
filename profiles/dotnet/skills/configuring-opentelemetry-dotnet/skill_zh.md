# 在 .NET 中配置 OpenTelemetry

## 何时使用

- 为 ASP.NET Core 应用程序添加分布式追踪
- 设置 OpenTelemetry 导出器（OTLP 是主要协议；Jaeger 原生支持 OTLP；Prometheus OTLP 消费需要显式选择）
- 为业务操作创建自定义指标或追踪跨度
- 解决跨服务分布式追踪上下文传播问题

## 何时不使用

- 用户只需要应用程序级日志（使用 ILogger、Serilog）
- 用户直接使用 Application Insights SDK（不同的 API）
- 用户需要带有商业供应商专有 SDK 的 APM

## 输入

| 输入 | 是否必需 | 描述 |
|------|----------|-------|
| ASP.NET Core 项目 | 是 | 要instrument的应用程序 |
| 可观察性后端 | 否 | 导出目标：OTLP 收集器、Aspire 仪表板、Jaeger（原生支持 OTLP） |

## 工作流

### 第 1 步：安装正确的包

**有许多 OpenTelemetry NuGet 包。仅安装以下这些：**

```bash
# 核心SDK + ASP.NET Core instrument + 日志集成
dotnet add package OpenTelemetry.Extensions.Hosting
dotnet add package OpenTelemetry.Instrumentation.AspNetCore
dotnet add package OpenTelemetry.Instrumentation.Http

# 导出器
dotnet add package OpenTelemetry.Exporter.OpenTelemetryProtocol  # 用于追踪、指标和日志的OTLP导出器

# 可选 — 仅限开发/本地调试（生产部署中不要包含）
# dotnet add package OpenTelemetry.Exporter.Console
```

**不要单独安装 `OpenTelemetry`** — 你需要 `OpenTelemetry.Extensions.Hosting` 以便进行正确的 DI 集成。

#### 可选：额外的自动instrument包

仅安装与你的应用程序使用的库匹配的包：

```bash
dotnet add package OpenTelemetry.Instrumentation.SqlClient           # SQL Server查询
dotnet add package OpenTelemetry.Instrumentation.EntityFrameworkCore  # EF Core
dotnet add package OpenTelemetry.Instrumentation.GrpcNetClient       # gRPC调用
dotnet add package OpenTelemetry.Instrumentation.Runtime             # GC、线程池指标
```

### 第 2 步：在 Program.cs 中配置所有信号

```csharp
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;
using OpenTelemetry.Metrics;
using OpenTelemetry.Logs;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddOpenTelemetry()
    .ConfigureResource(resource => resource
        .AddService(serviceName: builder.Environment.ApplicationName))
    .WithTracing(tracing => tracing
        .AddAspNetCoreInstrumentation(options =>
        {
            // 从追踪中过滤出健康检查端点
            options.Filter = httpContext =>
                !httpContext.Request.Path.StartsWithSegments("/healthz");
        })
        .AddHttpClientInstrumentation(options =>
        {
            options.RecordException = true;
        })
        // 可选：如果直接使用 SqlClient，添加 SQL instrument
        // .AddSqlClientInstrumentation(options =>
        // {
        //     options.SetDbStatementForText = true;
        //     options.RecordException = true;
        // })
        // 自定义活动源（必须与代码中的 ActivitySource 名称匹配）
        .AddSource("MyApp.Orders")
        .AddSource("MyApp.Payments")
        .AddSource("MyApp.Messaging"))
    .WithMetrics(metrics => metrics
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        // 可选：.AddRuntimeInstrumentation() 用于 GC 和线程池指标
        //   （需要 OpenTelemetry.Instrumentation.Runtime 包）
        // 自定义计量器（必须与代码中的 Meter 名称匹配）
        .AddMeter("MyApp.Metrics"))
    .WithLogging(logging =>
    {
        logging.IncludeScopes = true;
        // logging.IncludeFormattedMessage = true;  // 如果需要在日志导出中包含格式化的消息字符串，则启用
    })
    // 单个 OTLP 导出器用于所有信号 — 读取 OTEL_EXPORTER_OTLP_ENDPOINT 环境变量
    // （默认为 http://localhost:4317）。可通过环境变量或 appsettings.json 配置覆盖。
    .UseOtlpExporter();
```

### 第 3 步：理解日志—追踪关联

Step 2 中的 `.WithLogging()` 调用集成了 ILogger 与 OpenTelemetry：

- 每条日志条目自动包含 TraceId 和 SpanId 以便与追踪关联
- 从 `.ConfigureResource()` 获取的服务资源会自动传播到日志
- `UseOtlpExporter()` 与追踪和指标一起应用于日志
- 无需额外的包或单独的 `SetResourceBuilder` 调用

### 第 4 步：为业务操作创建自定义跨度（Activities）

```csharp
using System.Diagnostics;
using Microsoft.Extensions.Logging;

public class OrderService
{
    // 创建与 Step 2 中注册匹配的 ActivitySource
    private static readonly ActivitySource ActivitySource = new("MyApp.Orders");
    private readonly ILogger<OrderService> _logger;

    public OrderService(ILogger<OrderService> logger) => _logger = logger;

    public async Task<Order> ProcessOrderAsync(CreateOrderRequest request)
    {
        // 启动新的跨度
        using var activity = ActivitySource.StartActivity("ProcessOrder");

        // 向跨度添加属性（标签）
        activity?.SetTag("order.customer_id", request.CustomerId);
        activity?.SetTag("order.item_count", request.Items.Count);

        try
        {
            // 用于验证的子跨度
            using (var validationActivity = ActivitySource.StartActivity("ValidateOrder"))
            {
                await ValidateOrderAsync(request);
                validationActivity?.SetTag("validation.result", "passed");
            }

            // 用于支付的子跨度
            using (var paymentActivity = ActivitySource.StartActivity("ProcessPayment",
                ActivityKind.Client))  // Client = 外发调用
            {
                paymentActivity?.SetTag("payment.method", request.PaymentMethod);
                await ProcessPaymentAsync(request);
            }

            var order = new Order { Id = Guid.NewGuid(), CustomerId = request.CustomerId, Status = "Completed" };

            activity?.SetTag("order.status", "completed");
            activity?.SetStatus(ActivityStatusCode.Ok);

            return order;
        }
        catch (Exception ex)
        {
            activity?.SetStatus(ActivityStatusCode.Error, ex.Message);
            // 通过 ILogger 记录 — OpenTelemetry 会捕获与追踪关联的日志。
            // 优先使用日志而不是 activity.RecordException()，因为 OTel 正在弃用
            // 用于异常记录的跨度事件，改用基于日志的异常。
            _logger.LogError(ex, "Order processing failed for customer {CustomerId}", request.CustomerId);
            throw;
        }
    }
}
```

**关键：`ActivitySource` 名称必须与配置中的 `AddSource("...")` 匹配。** 未匹配的源会被静默忽略——这是 #1 调试问题。

### 第 5 步：创建自定义指标

使用 `IMeterFactory`（通过 DI 注入）创建计量器——这可确保正确的生命周期管理和可测试性。

```csharp
using System.Diagnostics;
using System.Diagnostics.Metrics;

public class OrderMetrics
{
    private readonly Counter<long> _ordersProcessed;
    private readonly Histogram<double> _orderProcessingDuration;
    private readonly UpDownCounter<int> _activeOrders;

    public OrderMetrics(IMeterFactory meterFactory)
    {
        // 计量器名称必须与配置中的 AddMeter("...") 匹配
        var meter = meterFactory.Create("MyApp.Metrics");

        // 计数器 — 用于只增量的指标
        _ordersProcessed = meter.CreateCounter<long>(
            "orders.processed", "orders", "成功处理的订单总数");

        // 直方图 — 用于测量分布（延迟、大小）
        _orderProcessingDuration = meter.CreateHistogram<double>(
            "orders.processing_duration", "ms", "处理一个订单的时间");

        // UpDownCounter — 用于增减量的指标
        _activeOrders = meter.CreateUpDownCounter<int>(
            "orders.active", "orders", "当前正在处理的订单");
    }

    public void RecordOrderProcessed(string region, double durationMs)
    {
        // 标签启用维度过滤（按区域、状态等）
        var tags = new TagList
        {
            { "region", region },
            { "order.type", "standard" }
        };

        _ordersProcessed.Add(1, tags);
        _orderProcessingDuration.Record(durationMs, tags);
    }
}
```

在 DI 中注册 `OrderMetrics`：

```csharp
builder.Services.AddSingleton<OrderMetrics>();
```

### 第 6 步：配置分布式场景的上下文传播

使用 `AddHttpClientInstrumentation()` 时，HTTP 调用的追踪上下文传播是自动的。对于非 HTTP 场景：

```csharp
using System;
using System.Collections.Generic;
using System.Diagnostics;
using OpenTelemetry.Context.Propagation;

// ActivitySource 应该是静态的 — 通过 Step 2 中的 .AddSource("MyApp.Messaging") 注册
private static readonly ActivitySource MessageSource = new("MyApp.Messaging");

// 手动上下文传播（例如，跨消息队列）
// 在发送端：
var propagator = Propagators.DefaultTextMapPropagator;
var activityContext = Activity.Current?.Context ?? default;
var context = new PropagationContext(activityContext, Baggage.Current);
var carrier = new Dictionary<string, string>();

propagator.Inject(context, carrier, (dict, key, value) => dict[key] = value);
// 将 carrier 字典作为消息标头发送

// 在接收端：
var parentContext = propagator.Extract(default, carrier,
    (dict, key) => dict.TryGetValue(key, out var value) ? new[] { value } : Array.Empty<string>());

Baggage.Current = parentContext.Baggage;
using var activity = MessageSource.StartActivity("ProcessMessage",
    ActivityKind.Consumer,
    parentContext.ActivityContext);  // 链接到父追踪！
```

## 验证

- [ ] 追踪出现在可观察性后端（Jaeger、Aspire 仪表板等）
- [ ] HTTP 请求自动创建带有正确动词、URL、状态码的跨度
- [ ] 自定义 `ActivitySource` 名称与 `AddSource()` 注册匹配
- [ ] 自定义 `Meter` 名称与 `AddMeter()` 注册匹配
- [ ] 日志包含 TraceId 和 SpanId 以便关联
- [ ] 健康检查端点从追踪中过滤
- [ ] 错误跨度显示异常详细信息

## 常见陷阱

| 陷阱 | 解决方案 |
|------|----------|
| `ActivitySource.StartActivity` 返回 null | 源名称与任何 `AddSource()` 不匹配——名称必须完全匹配 |
| 追踪未出现在导出器中 | 检查 OTLP 端点：gRPC 使用端口 4317，HTTP 使用 4318 |
| 缺少 HTTP 客户端跨度 | 确保 `AddHttpClientInstrumentation()` 已注册；它适用于 `IHttpClientFactory`/DI 和 `new HttpClient()`（使用 `IHttpClientFactory` 进行生命周期管理） |
| 高基数标签 | 不要将用户 ID、请求 ID 或 UUID 用作指标标签——会导致存储爆炸 |
| OTLP gRPC 与 HTTP 不匹配 | 默认是 gRPC（端口 4317）；如果收集器只接受 HTTP，设置 `OtlpExportProtocol.HttpProtobuf` |
| `Meter` / `ActivitySource` 生命周期 | `ActivitySource` 应该是静态的；通过 DI 中的 `IMeterFactory` 创建 `Meter`（而不是 `new Meter()`）以进行正确的生命周期管理和可测试性 |
