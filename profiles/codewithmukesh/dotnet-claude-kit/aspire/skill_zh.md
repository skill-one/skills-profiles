# .NET Aspire

## 核心原则

1. **AppHost 负责协调，它自身从不被部署** — Aspire 的核心工作是本地开发体验：一起启动服务、数据库和消息代理。现代 Aspire 还会生成部署资源（`aspire publish` 用于 docker-compose/Kubernetes 部署清单，`aspire deploy` 用于 Azure Container Apps），但 AppHost 进程本身始终是开发/构建时工具，而非生产时运行时。
2. **服务默认配置是你的基准** — `ServiceDefaults` 项目统一配置所有服务的 OpenTelemetry、健康检查和容错能力。
3. **使用 Aspire 集成** — Aspire 提供对 PostgreSQL、Redis、RabbitMQ、SQL Server 等的内置集成。它们会自动处理连接字符串、健康检查和追踪。
4. **仪表板是你的可观测性工具** — 使用 Aspire 仪表板进行本地开发时的追踪、日志记录和指标监控，而不是在本地设置 Seq/Grafana。

## 模式

### AppHost 配置

```csharp
// AppHost/Program.cs
var builder = DistributedApplication.CreateBuilder(args);

// 基础设施资源
var postgres = builder.AddPostgres("postgres")
    .WithPgAdmin()
    .AddDatabase("myappdb");

var redis = builder.AddRedis("redis")
    .WithRedisInsight();

var rabbitmq = builder.AddRabbitMQ("messaging")
    .WithManagementPlugin();

// 应用项目
var api = builder.AddProject<Projects.MyApp_Api>("api")
    .WithReference(postgres)
    .WithReference(redis)
    .WithReference(rabbitmq)
    .WithExternalHttpEndpoints();

var worker = builder.AddProject<Projects.MyApp_Worker>("worker")
    .WithReference(postgres)
    .WithReference(rabbitmq);

builder.Build().Run();
```

### 服务默认配置

```csharp
// ServiceDefaults/Extensions.cs — 标准 Aspire 服务默认配置
// 配置 OpenTelemetry（指标+追踪）、健康检查、服务发现和容错能力
public static class Extensions
{
    public static IHostApplicationBuilder AddServiceDefaults(this IHostApplicationBuilder builder)
    {
        builder.ConfigureOpenTelemetry();
        builder.AddDefaultHealthChecks();
        builder.Services.AddServiceDiscovery();

        builder.Services.ConfigureHttpClientDefaults(http =>
        {
            http.AddStandardResilienceHandler();
            http.AddServiceDiscovery();
        });

        return builder;
    }

    // ConfigureOpenTelemetry: 添加日志记录、指标（ASP.NET、HttpClient、运行时）、
    //   追踪（ASP.NET、HttpClient、EF Core）以及如果配置了 OTLP 导出器
    // AddDefaultHealthChecks: 添加标记为 ["live"] 的 "self" 活性检查
}
```

### 在项目中使用服务默认配置

```csharp
// MyApp.Api/Program.cs
var builder = WebApplication.CreateBuilder(args);
builder.AddServiceDefaults();

// 添加 Aspire 集成
builder.AddNpgsqlDbContext<AppDbContext>("myappdb");
builder.AddRedisDistributedCache("redis");

var app = builder.Build();
app.MapDefaultEndpoints(); // 健康检查端点
app.Run();
```

### 服务间通信

```csharp
// AppHost — 配置服务引用
var orderApi = builder.AddProject<Projects.OrderApi>("order-api");
var paymentApi = builder.AddProject<Projects.PaymentApi>("payment-api")
    .WithReference(orderApi); // paymentApi 可以发现 orderApi

// 在 PaymentApi — 使用服务发现
builder.Services.AddHttpClient<OrderClient>(client =>
{
    client.BaseAddress = new Uri("https+http://order-api");
});
```

### 使用 Aspire 的解决方案结构

```
MyApp.slnx
├── MyApp.AppHost/               # Aspire 协调器
│   └── Program.cs
├── MyApp.ServiceDefaults/       # 共享服务配置
│   └── Extensions.cs
├── src/
│   ├── MyApp.Api/               # Web API 项目
│   └── MyApp.Worker/            # 后台工作进程
└── tests/
    └── MyApp.Api.Tests/
```

## 反模式

### 不要部署 AppHost 进程

```csharp
// BAD — 在生产环境中以协调器身份运行 AppHost 可执行文件
// AppHost 是开发/构建时工具，而非生产时运行时

// GOOD — 部署生成的资源，而不是 AppHost：
//   aspire publish  → 从应用模型生成 docker-compose / Kubernetes 部署清单
//   aspire deploy   → 直接部署（例如 Azure Container Apps）
```

### 不要使用 Aspire 硬编码连接字符串

```csharp
// BAD — 硬编码连接字符串违背了 Aspire 的设计初衷
builder.Services.AddDbContext<AppDbContext>(o =>
    o.UseNpgsql("Host=localhost;Database=myapp;..."));

// GOOD — 使用 Aspire 集成（连接字符串自动注入）
builder.AddNpgsqlDbContext<AppDbContext>("myappdb");
```

### 不要跳过服务默认配置

```csharp
// BAD — 手动配置每个服务
builder.Services.AddOpenTelemetry()...
builder.Services.AddHealthChecks()...

// GOOD — 使用共享服务默认配置
builder.AddServiceDefaults();
```

## 决策指南

| 场景 | 建议 |
|------|------|
| 多服务本地开发 | Aspire AppHost |
| 单项目本地开发 | `dotnet run` 足够，Aspire 可选 |
| 共享服务配置 | ServiceDefaults 项目 |
| 本地开发数据库 | Aspire `AddPostgres()` / `AddSqlServer()` |
| 服务发现 | Aspire 内置服务发现 |
| 生产部署 | `aspire publish`（compose/K8s 部署清单）或 `aspire deploy`（ACA）；绝不部署 AppHost 本身 |
| 本地开发可观测性 | Aspire 仪表板（自动配置） |
