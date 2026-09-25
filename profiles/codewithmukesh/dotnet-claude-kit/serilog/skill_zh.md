# Serilog

## 核心原则

1. **两阶段初始化** — 创建一个引导日志记录器用于启动，在依赖注入准备就绪后替换为完整日志记录器。这捕获了否则会丢失的启动错误。
2. **`AddSerilog()` 覆盖 `UseSerilog()`** — 使用 `builder.Services.AddSerilog()`（现代 API）而不是 `builder.Host.UseSerilog()`。它通过 `ReadFrom.Services(services)` 与依赖注入服务集成。
3. **消息模板而非插值** — `{PropertyName}` 语法创建可查询的结构化数据。字符串插值 (`$"..."`) 会破坏结构，即使日志级别被禁用也会分配内存。
4. **通过 appsettings.json 配置** — 将日志级别、接收器和覆盖项保存在配置中，以便它们可以根据环境更改而无需重新部署。

## 模式

### 两阶段引导设置

```csharp
using Serilog;

// 阶段 1：引导日志记录器 — 在依赖注入之前捕获启动错误
Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Override("Microsoft", LogEventLevel.Information)
    .Enrich.FromLogContext()
    .WriteTo.Console()
    .CreateBootstrapLogger();

try
{
    Log.Information("启动应用程序");

    var builder = WebApplication.CreateBuilder(args);

    // 阶段 2：带依赖注入和配置的完整日志记录器
    builder.Services.AddSerilog((services, lc) => lc
        .ReadFrom.Configuration(builder.Configuration)
        .ReadFrom.Services(services)
        .Enrich.FromLogContext()
        .Enrich.WithMachineName()
        .Enrich.WithEnvironmentName()
        .Enrich.WithProperty("Application", "MyApp.Api"));

    var app = builder.Build();

    app.UseSerilogRequestLogging(options =>
    {
        options.EnrichDiagnosticContext = (diagnosticContext, httpContext) =>
        {
            diagnosticContext.Set("RequestHost", httpContext.Request.Host.Value);
            diagnosticContext.Set("UserAgent",
                httpContext.Request.Headers.UserAgent.ToString());
        };
    });

    app.Run();
}
catch (Exception ex)
{
    Log.Fatal(ex, "应用程序意外终止");
}
finally
{
    await Log.CloseAndFlushAsync();
}
```

### appsettings.json 配置

```json
{
  "Serilog": {
    "MinimumLevel": {
      "Default": "Information",
      "Override": {
        "Microsoft": "Warning",
        "Microsoft.AspNetCore": "Warning",
        "Microsoft.EntityFrameworkCore": "Warning",
        "Microsoft.Hosting.Lifetime": "Information",
        "System": "Warning"
      }
    },
    "WriteTo": [
      {
        "Name": "Console",
        "Args": {
          "outputTemplate": "[{Timestamp:HH:mm:ss} {Level:u3}] {Message:lj} {Properties:j}{NewLine}{Exception}"
        }
      },
      {
        "Name": "File",
        "Args": {
          "path": "logs/app-.log",
          "rollingInterval": "Day",
          "retainedFileCountLimit": 30,
          "fileSizeLimitBytes": 104857600
        }
      },
      {
        "Name": "Seq",
        "Args": { "serverUrl": "http://localhost:5341" }
      }
    ],
    "Enrich": ["FromLogContext", "WithMachineName", "WithEnvironmentName"],
    "Destructure": [
      { "Name": "ToMaximumDepth", "Args": { "maximumDestructuringDepth": 4 } },
      { "Name": "ToMaximumStringLength", "Args": { "maximumStringLength": 1024 } },
      { "Name": "ToMaximumCollectionCount", "Args": { "maximumCollectionCount": 10 } }
    ]
  }
}
```

覆盖部分使用命名空间前缀与 `SourceContext` 匹配。更具体的前缀优先级更高。

### 请求日志中间件

用单个摘要事件替换 ASP.NET Core 的多个每个请求的日志事件。

```csharp
app.UseSerilogRequestLogging(options =>
{
    options.MessageTemplate =
        "HTTP {RequestMethod} {RequestPath} responded {StatusCode} in {Elapsed:0.0000} ms";

    options.GetLevel = (httpContext, elapsed, ex) => ex is not null
        ? LogEventLevel.Error
        : httpContext.Response.StatusCode >= 500
            ? LogEventLevel.Error
            : LogEventLevel.Information;

    options.EnrichDiagnosticContext = (diagnosticContext, httpContext) =>
    {
        diagnosticContext.Set("UserId",
            httpContext.User.FindFirstValue(ClaimTypes.NameIdentifier) ?? "anonymous");
    };
});
```

### 结构化日志和分解

```csharp
// 命名属性 — 创建可查询的结构化数据
logger.LogInformation("Order {OrderId} placed by {CustomerId} for {Total:C}",
    orderId, customerId, total);

// @ 运算符保留对象结构为属性
logger.LogInformation("Processing {@SensorInput}", sensorInput);
// 输出: Processing {"Latitude": 25, "Longitude": 134}

// $ 运算符强制调用 ToString()
logger.LogInformation("Received {$Data}", new[] { 1, 2, 3 });
// 输出: Received "System.Int32[]"
```

### 带日志上下文的范围属性

```csharp
using (LogContext.PushProperty("CorrelationId", correlationId))
using (LogContext.PushProperty("TenantId", tenantId))
{
    logger.LogInformation("Processing order {OrderId}", orderId);
    // CorrelationId 和 TenantId 附着在此作用域中的所有日志事件
}
```

需要在日志记录器配置中包含 `.Enrich.FromLogContext()`。

### OpenTelemetry 接收器（OTLP 导出）

直接将 Serilog 事件导出到任何 OTLP 后端，而无需 OpenTelemetry SDK：

```csharp
.WriteTo.OpenTelemetry(options =>
{
    options.Endpoint = "http://localhost:4317";
    options.Protocol = OtlpProtocol.Grpc;
    options.ResourceAttributes = new Dictionary<string, object>
    {
        ["service.name"] = "MyApp.Api",
        ["deployment.environment"] = "production"
    };
})
```

### Serilog.Expressions 用于过滤

需要 `Serilog.Expressions` 包。

```csharp
// 排除健康检查噪音
.Filter.ByExcluding("RequestPath like '/health%'")

// 将错误路由到单独的文件
.WriteTo.Conditional("@l = 'Error'",
    wt => wt.File("logs/errors-.log", rollingInterval: RollingInterval.Day))
```

### `[LoggerMessage]` 源生成器用于热点路径

集成在 `Microsoft.Extensions.Logging.Abstractions` 中 — 编译时生成，当日志级别被禁用时零内存分配。

```csharp
public static partial class OrderLogs
{
    [LoggerMessage(Level = LogLevel.Information,
        Message = "Order {OrderId} created for {CustomerId}")]
    public static partial void OrderCreated(this ILogger logger, Guid orderId, Guid customerId);
}

// 使用
logger.OrderCreated(order.Id, order.CustomerId);
```

## 反模式

### 不要使用字符串插值

```csharp
// BAD — 破坏结构化日志，即使日志级别被禁用也会分配内存
logger.LogInformation($"Order {orderId} created for {customerId}");

// GOOD — 命名参数的消息模板
logger.LogInformation("Order {OrderId} created for {CustomerId}", orderId, customerId);
```

### 不要跳过 CloseAndFlush

```csharp
// BAD — 异步接收器（Seq、OTLP、Elasticsearch）丢失缓冲的事件
app.Run();

// GOOD — 用 try/finally 包裹
try { app.Run(); }
catch (Exception ex) { Log.Fatal(ex, "未处理的异常"); }
finally { await Log.CloseAndFlushAsync(); }
```

### 不要记录敏感数据

```csharp
// BAD — 日志中记录密码和令牌
logger.LogInformation("Login: {Email} with password {Password}", email, password);

// GOOD — 从不记录密钥、密码、令牌或个人身份信息
logger.LogInformation("Login: {Email}", email);
```

### 不要无限制分解

```csharp
// BAD — 大型对象图导致内存问题和巨大的日志条目
logger.LogInformation("Request: {@Request}", httpContext.Request);

// GOOD — 配置分解限制
.Destructure.ToMaximumDepth(4)
.Destructure.ToMaximumStringLength(1024)
.Destructure.ToMaximumCollectionCount(10)

// BETTER — 分解到特定属性
.Destructure.ByTransforming<HttpRequest>(r => new { r.Method, r.Path })
```

### 不要使用已弃用的 Elasticsearch 接收器

```csharp
// BAD — Serilog.Sinks.Elasticsearch 包已弃用
// <PackageReference Include="Serilog.Sinks.Elasticsearch" />
.WriteTo.Elasticsearch("http://localhost:9200")

// GOOD — 相同方法名，但来自官方的 Elastic.Serilog.Sinks 包，该包将 ECS 格式的文档写入数据流
// <PackageReference Include="Elastic.Serilog.Sinks" />
.WriteTo.Elasticsearch([new Uri("https://elastic.example.com:9200")], opts =>
    opts.DataStream = new DataStreamName("logs", "myapp"))
```

## 决策指南

| 场景 | 建议 |
|------|------|
| 应用程序日志记录 | Serilog 与 `AddSerilog()` 和 appsettings.json |
| 开发环境日志存储 | Seq（免费单用户）或 Aspire 控制台 |
| 生产环境日志存储 | Seq、Elasticsearch（Elastic 接收器）或 OTLP 后端 |
| 请求日志记录 | `UseSerilogRequestLogging()`（替换每个请求的噪音） |
| 范围属性 | 在中间件中使用 `LogContext.PushProperty()` |
| 日志过滤 | `Serilog.Expressions` 进行基于表达式的过滤 |
| 高性能路径 | `[LoggerMessage]` 源生成器 |
| 审计跟踪 | `AuditTo`（同步，异常传播） |
| 环境日志级别 | 在 appsettings 中为每个命名空间使用 `MinimumLevel.Override` |
| OpenTelemetry 集成 | `Serilog.Sinks.OpenTelemetry`（无 SDK 依赖） |
