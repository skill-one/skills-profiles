# 日志与可观察性

## 核心原则

1. **使用 Serilog 进行结构化日志记录** — 每条日志条目都是一个具有命名属性的规范化事件，而不是格式化的字符串。这支持搜索、过滤和告警。所有配置（两阶段引导、`AddSerilog()`、接收器、增强器）都位于 **serilog** 技能中 — 该技能的 `AddSerilog()`-over-`UseSerilog()` 指导是权威的。
2. **使用 OpenTelemetry 进行分布式追踪** — 追踪连接跨服务的请求；指标跟踪系统随时间变化的健康状况。完整配置位于 **opentelemetry** 技能中。
3. **用于操作就绪的健康检查** — 每个服务都暴露 `/health` 端点给负载均衡器和编排器。存活性和就绪性是分开的问题和分开的端点。
4. **用于请求追踪的相关 ID** — 每个请求都有一个唯一 ID，该 ID 流经所有日志条目和下游服务调用，因此一个用户投诉映射到一个过滤后的日志流。

## 模式

### 各部分如何协同工作

| 关注点 | 所有者 | 技能 |
|---------|-------|-------|
| 结构化应用日志 | Serilog (`AddSerilog()`) | `serilog` |
| 请求摘要日志记录 | `UseSerilogRequestLogging()` | `serilog` |
| 追踪 + 指标 + OTLP 导出 | OpenTelemetry SDK | `opentelemetry` |
| 健康端点、相关 ID、日志级别策略 | 本技能 | `logging` |

首先配置日志记录（你需要日志来调试其他部分），然后是健康检查，然后是追踪。

### 相关 ID

```csharp
// 中间件用于设置相关 ID
public class CorrelationIdMiddleware(RequestDelegate next)
{
    private const string CorrelationIdHeader = "X-Correlation-Id";

    public async Task InvokeAsync(HttpContext context)
    {
        var correlationId = context.Request.Headers[CorrelationIdHeader].FirstOrDefault()
            ?? Guid.NewGuid().ToString();

        context.Items["CorrelationId"] = correlationId;
        context.Response.Headers[CorrelationIdHeader] = correlationId;

        using (LogContext.PushProperty("CorrelationId", correlationId))
        {
            await next(context);
        }
    }
}

// Program.cs — 早期注册，以便每个下游日志都携带该 ID
app.UseMiddleware<CorrelationIdMiddleware>();
```

为什么使用中间件：在管道边缘一次性推送属性，将其附加到请求范围内的每个日志事件 — 无需在每个调用点进行管道处理。通过 `DelegatingHandler` 在出站 `HttpClient` 调用中传播相同的头部（见 **httpclient-factory** 技能）。

### 健康检查

```csharp
// Program.cs
builder.Services.AddHealthChecks()
    .AddNpgSql(builder.Configuration.GetConnectionString("Default")!,
        name: "database", tags: ["ready"])
    .AddRedis(builder.Configuration.GetConnectionString("Redis")!,
        name: "redis", tags: ["ready"])
    .AddRabbitMQ(builder.Configuration.GetConnectionString("RabbitMq")!,
        name: "rabbitmq", tags: ["ready"]);

// 映射端点
app.MapHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate = _ => false // 无依赖检查 — 仅“我是否在运行？”
});

app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready")
});
```

为什么有两个端点：存活性失败意味着“重启我”；就绪性失败意味着“停止发送流量”。将它们混淆会导致慢数据库重启应用程序形成死循环。

### 日志级别策略

| 级别 | 用于 | 环境默认值 |
|-------|---------|---------------------|
| Debug | 诊断细节、有效载荷转储（生产环境中绝不含 PII） | 仅开发环境 |
| Information | 业务事件：订单已放置、作业已完成 | 开发 + 测试 |
| Warning | 可恢复的异常：触发了重试、使用了回退 | 所有环境 — 生产环境默认值 |
| Error | 需要关注的失败操作 | 所有环境 |
| Fatal/Critical | 应用程序无法继续 | 所有环境 |

为什么生产环境默认为 Warning：大规模的 Information 级请求噪音会消耗真实的日志存储成本，淹没信号。通过命名空间覆盖保留 Information 用于真实的业务事件（见 **serilog** 技能的 `MinimumLevel.Override` 模式）。

## 反模式

### 不要记录敏感数据

```csharp
// BAD — 记录凭证
logger.LogInformation("User logged in: {Email} with password {Password}", email, password);

// GOOD — 记录标识符，Information 级别从不记录秘密或 PII
logger.LogInformation("User {UserId} logged in", userId);
```

### 不要跳过健康检查标签

```csharp
// BAD — 所有检查都用于存活性和就绪性
app.MapHealthChecks("/health");

// GOOD — 将存活性（我是否在运行？）与就绪性（我能服务流量吗？）分开？
app.MapHealthChecks("/health/live", new() { Predicate = _ => false });
app.MapHealthChecks("/health/ready", new() { Predicate = c => c.Tags.Contains("ready") });
```

### 不要重新实现所有者技能提供的内容

```csharp
// BAD — 在内存中手动编写 Serilog 引导
builder.Host.UseSerilog(...);  // 遗留 API — serilog 技能禁止这样做

// GOOD — 加载 serilog 技能并使用其两阶段 AddSerilog() 引导
builder.Services.AddSerilog((services, lc) => lc.ReadFrom.Configuration(builder.Configuration)...);
```

## 决策指南

| 场景 | 建议 |
|----------|---------------|
| 应用程序日志记录设置 | 加载 `serilog` — `AddSerilog()` 两阶段引导 |
| 分布式追踪 / 指标 | 加载 `opentelemetry` — OTLP 导出器 |
| 自定义业务指标 | `IMeterFactory` + 计数器/直方图 (`opentelemetry` 技能) |
| 请求追踪 | 相关 ID 中间件（本技能） |
| 容器健康 | `/health/live` 和 `/health/ready` 端点（本技能） |
| 日志存储 | Seq（开发）、Elastic/Grafana/OTLP 后端（生产） |
| 日志级别 | 开发环境中的 Debug、测试环境中的 Information、生产环境默认的 Warning |
