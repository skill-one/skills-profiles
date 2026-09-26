> [所有技能](../../SKILL_TREE.md) > [SDK 设置](../sentry-sdk-setup/SKILL.md) > .NET SDK

# Sentry .NET SDK

一个有主见的向导，它会扫描您的 .NET 项目并指导您完成 Sentry 的完整设置：错误监控、分布式追踪、性能分析、结构化日志记录以及跨所有主要 .NET 框架的定时任务监控。

## 何时调用此技能

- 用户询问“将 Sentry 添加到 .NET”、“在 C# 中设置 Sentry”或“为 ASP.NET Core 安装 Sentry”
- 用户希望为 .NET 应用程序添加错误监控、追踪、性能分析、日志记录或定时任务
- 用户提到 `SentrySdk.Init`、`UseSentry`、`Sentry.AspNetCore` 或 `Sentry.Maui`
- 用户希望捕获 WPF、WinForms、MAUI 或 Azure Functions 中的未处理异常
- 用户询问关于 `SentryOptions`、`BeforeSend`、`TracesSampleRate` 或符号上传的问题

> **注意：** 以下 SDK 版本和 API 反映的是 ≥6.1.0 的 `Sentry` NuGet 包（OTLP 导出需要 ≥6.5.0）。
> 在实施之前，请始终参考 [docs.sentry.io/platforms/dotnet/](https://docs.sentry.io/platforms/dotnet/) 进行验证。

---

## 第一阶段：检测

在提出任何建议之前，运行这些命令以了解项目：

```bash
# 检测框架类型 — 查找所有 .csproj 文件
find . -name "*.csproj" | head -20

# 检测框架目标
grep -r "TargetFramework\|Project Sdk" --include="*.csproj" .

# 检查现有的 Sentry 包
grep -r "Sentry" --include="*.csproj" . | grep "PackageReference"

# 检查启动文件
ls Program.cs src/Program.cs App.xaml.cs MauiProgram.cs 2>/dev/null

# 检查 appsettings
ls appsettings.json src/appsettings.json 2>/dev/null

# 检查日志库
grep -r "Serilog\|NLog\|log4net" --include="*.csproj" .

# 检查配套前端
ls ../frontend ../client ../web 2>/dev/null
cat ../package.json 2>/dev/null | grep -E '"next"|"react"|"vue"' | head -3
```

**需要确定的内容：**

| 问题 | 影响 |
|----------|--------|
| 框架类型？ | 确定正确的包和初始化模式 |
| .NET 版本？ | 推荐使用 .NET 8+；支持 .NET Framework 4.6.2+ |
| Sentry 已安装？ | 跳过安装，直接进行功能配置 |
| 日志库 (Serilog, NLog)？ | 推荐匹配 Sentry 消费端/目标 |
| 异步/托管应用 (ASP.NET Core)？ | 在 `WebHost` 上调用 `UseSentry()`；不需要 `IsGlobalModeEnabled` |
| 桌面应用 (WPF, WinForms, WinUI)？ | 必须设置 `IsGlobalModeEnabled = true` |
| 无服务器 (Azure Functions, Lambda)？ | 必须设置 `FlushOnCompletedRequest = true` |
| 找到前端目录？ | 触发第四阶段的跨链接 |

**框架 → 包映射：**

| 检测到 | 安装包 |
|----------|--------|
| `Sdk="Microsoft.NET.Sdk.Web"` (ASP.NET Core) | `Sentry.AspNetCore` |
| `App.xaml.cs` 包含 `Application` 基类 | `Sentry` (WPF) |
| `Program.cs` 中包含 `[STAThread]` | `Sentry` (WinForms) |
| `MauiProgram.cs` | `Sentry.Maui` |
| `WebAssemblyHostBuilder` | `Sentry.AspNetCore.Blazor.WebAssembly` |
| `FunctionsStartup` | `Sentry.Extensions.Logging` + `Sentry.OpenTelemetry` |
| `HttpApplication` / `Global.asax` | `Sentry.AspNet` |
| 通用主机 / 工作服务 | `Sentry.Extensions.Logging` |

---

## 第二阶段：建议

根据您发现的内容，提出具体的建议。以提案开头，不要提出开放式问题。

**推荐（核心覆盖）：**
- ✅ **错误监控** — 总是；捕获未处理的异常、结构化捕获、作用域增强
- ✅ **追踪** — 总是为 ASP.NET Core 和托管应用；自动检测 HTTP 请求和 EF Core 查询
- ✅ **日志记录** — 推荐用于所有应用；将 ILogger / Serilog / NLog 条目路由到 Sentry 作为面包屑和事件

**可选（增强可观察性）：**
- ⚡ **性能分析** — CPU 性能分析；推荐用于运行在 .NET 6+ 的性能关键服务
- ⚡ **指标** — 与追踪关联的计数器、仪表板、分布；推荐用于需要自定义业务指标的应用
- ⚡ **定时任务** — 检测丢失/失败的定时任务；当检测到 Hangfire、Quartz.NET 或定时端点时推荐

**建议逻辑：**

| 功能 | 当...推荐 |
|----------|----------|
| 错误监控 | **始终** — 不可协商的基线 |
| 追踪 | **始终为 ASP.NET Core** — 请求追踪、EF Core 跨度、HttpClient 跨度具有高价值 |
| 日志记录 | 应用使用 `ILogger<T>`、Serilog、NLog 或 log4net |
| 性能分析 | .NET 6+ 上的性能关键服务 |
| 指标 | 应用需要自定义业务指标（请求计数、队列深度、响应时间） |
| 定时任务 | 应用使用 Hangfire、Quartz.NET 或定时 Azure Functions |

建议：*"我建议设置错误监控 + 追踪 + 日志记录。您希望我是否也添加性能分析或定时任务？*"

---

## 第三阶段：指导

### 选项 1：向导（推荐）

> **您需要自行运行** — 向导会打开浏览器进行登录，并需要交互式输入，代理无法处理。将以下内容复制粘贴到您的终端：
>
> ```
> npx @sentry/wizard@latest -i dotnet
> ```
>
> 它处理登录、组织/项目选择、DSN 配置以及 MSBuild 符号上传设置，以便在生产环境中显示可读的堆栈跟踪。
>
> **一旦完成，请返回并跳转到 [验证](#verification)。**

如果用户跳过向导，请继续执行下面的选项 2（手动设置）。

---

### 选项 2：手动设置

#### 安装正确的包

```bash
# ASP.NET Core
dotnet add package Sentry.AspNetCore -v 6.1.0

# WPF 或 WinForms 或控制台
dotnet add package Sentry -v 6.1.0

# .NET MAUI
dotnet add package Sentry.Maui -v 6.1.0

# Blazor WebAssembly
dotnet add package Sentry.AspNetCore.Blazor.WebAssembly -v 6.1.0

# Azure Functions (隔离工作进程)
dotnet add package Sentry.Extensions.Logging -v 6.1.0
dotnet add package Sentry.OpenTelemetry -v 6.1.0

# 经典 ASP.NET (System.Web / .NET Framework)
dotnet add package Sentry.AspNet -v 6.1.0
```

---

#### ASP.NET Core — `Program.cs`

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.WebHost.UseSentry(options =>
{
    options.Dsn = Environment.GetEnvironmentVariable("SENTRY_DSN")
                  ?? "___YOUR_DSN___";
    options.Debug = true;                         // 生产环境禁用
    options.SendDefaultPii = true;                // 捕获用户 IP、姓名、电子邮件
    options.MaxRequestBodySize = RequestSize.Always;
    options.MinimumBreadcrumbLevel = LogLevel.Debug;
    options.MinimumEventLevel = LogLevel.Warning;
    options.TracesSampleRate = 1.0;               // 生产环境调至 0.1–0.2
    options.SetBeforeSend((@event, hint) =>
    {
        @event.ServerName = null;                 // 从事件中清除主机名
        return @event;
    });
});

var app = builder.Build();
app.Run();
```

**`appsettings.json`（替代配置）：**

```json
{
  "Sentry": {
    "Dsn": "___YOUR_DSN___",
    "SendDefaultPii": true,
    "MaxRequestBodySize": "Always",
    "MinimumBreadcrumbLevel": "Debug",
    "MinimumEventLevel": "Warning",
    "AttachStacktrace": true,
    "Debug": true,
    "TracesSampleRate": 1.0,
    "Environment": "production",
    "Release": "my-app@1.0.0"
  }
}
```

**环境变量（使用双下划线作为分隔符）：**

```bash
export Sentry__Dsn="https://examplePublicKey@o0.ingest.sentry.io/0"
export Sentry__TracesSampleRate="0.1"
export Sentry__Environment="staging"
```

---

#### WPF — `App.xaml.cs`

> ⚠️ **关键：** 在构造函数中初始化，而不是在 `OnStartup()` 中。构造函数会先触发，可以捕获更多失败模式。

```csharp
using System.Windows;
using Sentry;

public partial class App : Application
{
    public App()
    {
        SentrySdk.Init(options =>
        {
            options.Dsn = "___YOUR_DSN___";
            options.Debug = true;
            options.SendDefaultPii = true;
            options.TracesSampleRate = 1.0;
            options.IsGlobalModeEnabled = true;   // 桌面应用必需
        });

        // 在 WPF 的崩溃对话框出现之前捕获 UI 线程异常
        DispatcherUnhandledException += App_DispatcherUnhandledException;
    }

    private void App_DispatcherUnhandledException(
        object sender,
        System.Windows.Threading.DispatcherUnhandledExceptionEventArgs e)
    {
        SentrySdk.CaptureException(e.Exception);
        // 设置 e.Handled = true 以防止崩溃对话框并保持应用运行
    }
}
```

---

#### WinForms — `Program.cs`

```csharp
using System;
using System.Windows.Forms;
using Sentry;

static class Program
{
    [STAThread]
    static void Main()
    {
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);

        // 必需：允许 Sentry 捕获未处理的 WinForms 异常
        Application.SetUnhandledExceptionMode(UnhandledExceptionMode.ThrowException);

        using (SentrySdk.Init(new SentryOptions
        {
            Dsn = "___YOUR_DSN___",
            Debug = true,
            TracesSampleRate = 1.0,
            IsGlobalModeEnabled = true,           // 桌面应用必需
        }))
        {
            Application.Run(new MainForm());
        } // 释放时清空所有待处理事件
    }
}
```

---

#### .NET MAUI — `MauiProgram.cs`

```csharp
public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder
            .UseMauiApp<App>()
            .UseSentry(options =>
            {
                options.Dsn = "___YOUR_DSN___";
                options.Debug = true;
                options.SendDefaultPii = true;
                options.TracesSampleRate = 1.0;
                // MAUI 特定：选择是否包含面包屑中的文本（默认关闭 — PII 风险）
                options.IncludeTextInBreadcrumbs = false;
                options.IncludeTitleInBreadcrumbs = false;
                options.IncludeBackgroundingStateInBreadcrumbs = false;
            });

        return builder.Build();
    }
}
```

---

#### Blazor WebAssembly — `Program.cs`

```csharp
var builder = WebAssemblyHostBuilder.CreateDefault(args);

builder.UseSentry(options =>
{
    options.Dsn = "___YOUR_DSN___";
    options.Debug = true;
    options.SendDefaultPii = true;
    options.TracesSampleRate = 0.1;
});

// 钩子日志管道而不重新初始化 SDK
builder.Logging.AddSentry(o => o.InitializeSdk = false);

await builder.Build().RunAsync();
```

---

#### Azure Functions (隔离工作进程) — `Program.cs`

> **推荐：** 安装 `Sentry.OpenTelemetry.Exporter` (≥6.5.0) 用于 OTLP 导出。或者，使用 `Sentry.OpenTelemetry` 进行桥接模式。

```csharp
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using OpenTelemetry.Trace;

// 包：Sentry.OpenTelemetry.Exporter
var host = new HostBuilder()
    .ConfigureFunctionsWorkerDefaults()
    .ConfigureLogging(logging =>
    {
        logging.AddSentry(options =>
        {
            options.Dsn = "___YOUR_DSN___";
            options.Debug = true;
            options.TracesSampleRate = 1.0;
            options.UseOtlp(); // 通过 OTLP 发送 OTel 跨度（需要 6.5.0+）
        });
    })
    .ConfigureServices(services =>
    {
        services.AddOpenTelemetry().WithTracing(builder =>
        {
            builder
                .AddHttpClientInstrumentation()
                .AddSentryOtlpExporter("___YOUR_DSN___"); // 将跨度路由到 Sentry OTLP 端点
        });
    })
    .Build();

await host.RunAsync();
```

---

#### AWS Lambda — `LambdaEntryPoint.cs`

```csharp
public class LambdaEntryPoint : APIGatewayProxyFunction
{
    protected override void Init(IWebHostBuilder builder)
    {
        builder
            .UseSentry(options =>
            {
                options.Dsn = "___YOUR_DSN___";
                options.TracesSampleRate = 1.0;
                options.FlushOnCompletedRequest = true; // 对于 Lambda 必须设置
            })
            .UseStartup<Startup>();
    }
}
```

---

#### 经典 ASP.NET — `Global.asax.cs`

```csharp
public class MvcApplication : HttpApplication
{
    private IDisposable _sentry;

    protected void Application_Start()
    {
        _sentry = SentrySdk.Init(options =>
        {
            options.Dsn = "___YOUR_DSN___";
            options.TracesSampleRate = 1.0;
            options.AddEntityFramework(); // EF6 查询面包屑
            options.AddAspNet();          // 经典 ASP.NET 集成
        });
    }

    protected void Application_Error() => Server.CaptureLastError();

    protected void Application_BeginRequest() => Context.StartSentryTransaction();
    protected void Application_EndRequest() => Context.FinishSentryTransaction();

    protected void Application_End() => _sentry?.Dispose();
}
```

---

### 符号上传（可读的堆栈跟踪）

没有调试符号，堆栈跟踪只显示方法名，不显示文件名或行号。SDK 通过 Release 构建的 MSBuild 属性上传 PDB 文件（可选上传源文件）：

```xml
<PropertyGroup Condition="'$(Configuration)' == 'Release'">
  <SentryOrg>___ORG_SLUG___</SentryOrg>
  <SentryProject>___PROJECT_SLUG___</SentryProject>
  <SentryUploadSymbols>true</SentryUploadSymbols>
  <SentryUploadSources>true</SentryUploadSources>
  <SentryCreateRelease>true</SentryCreateRelease>
  <SentrySetCommits>true</SentrySetCommits>
</PropertyGroup>
```

上传需要 CI 中设置 `SENTRY_AUTH_TOKEN`（一个秘密）。有关创建令牌和 CI 集成，请参阅 [`sentry-source-maps`](../sentry-source-maps/SKILL.md)。`SentryCreateRelease` / `SentrySetCommits` 属性还会创建一个包含可疑提交的发布 — 请参阅 [`sentry-releases`](../sentry-releases/SKILL.md)。

---

### 对每个同意的功能

加载相应的参考文件并按照其步骤操作：

| 功能 | 参考文件 | 当...加载 |
|----------|----------|----------|
| 错误监控 | `references/error-monitoring.md` | 始终 — `CaptureException`、作用域、增强、过滤 |
| 追踪 | `references/tracing.md` | 服务器应用、分布式追踪、EF Core 跨度、自定义仪器 |
| 性能分析 | `references/profiling.md` | .NET 6+ 上的性能关键应用 |
| 日志记录 | `references/logging.md` | `ILogger<T>`、Serilog、NLog、log4net 集成 |
| 指标 | `references/metrics.md` | 自定义计数器、仪表板、分布；`EmitCounter`、`EmitGauge`、`EmitDistribution` |
| 定时任务 | `references/crons.md` | Hangfire、Quartz.NET 或定时函数监控 |

对于每个功能：阅读参考文件，完全按照其步骤操作，并在继续之前进行验证。

---

## 配置参考

### 核心的 `SentryOptions`

| 选项 | 类型 | 默认值 | 环境变量 | 备注 |
|----------|------|--------|---------|-------|
| `Dsn` | `string` | — | `SENTRY_DSN` | 必需。如果未设置，SDK 将禁用。 |
| `Debug` | `bool` | `false` | — | SDK 诊断输出。生产环境禁用。 |
| `DiagnosticLevel` | `SentryLevel` | `Debug` | — | `Debug`、`Info`、`Warning`、`Error`、`Fatal` |
| `Release` | `string` | 自动 | `SENTRY_RELEASE` | 自动从程序集版本 + git SHA 检测 |
| `Environment` | `string` | `"production"` | `SENTRY_ENVIRONMENT` | `"debug"` 当调试器连接时 |
| `Dist` | `string` | — | — | 构建变体。最多 64 个字符。 |
| `SampleRate` | `float` | `1.0` | — | 错误事件采样率 0.0–1.0 |
| `TracesSampleRate` | `double` | `0.0` | — | 事务采样。必须为 `> 0` 才能启用。 |
| `TracesSampler` | `Func<SamplingContext, double>` | — | — | 每个事务的动态采样器；覆盖 `TracesSampleRate` |
| `ProfilesSampleRate` | `double` | `0.0` | — | 要分析的追踪事务的比例。需要 `Sentry.Profiling` |
| `SendDefaultPii` | `bool` | `false` | — | 包含用户 IP、姓名、电子邮件 |
| `AttachStacktrace` | `bool` | `true` | — | 将堆栈跟踪附加到所有消息 |
| `MaxBreadcrumbs` | `int` | `100` | — | 每个事件存储的最大面包屑数 |
| `IsGlobalModeEnabled` | `bool` | `false`* | — | *MAUI、Blazor WASM 自动 `true`。**桌面应用必须为 `true`。 |
| `AutoSessionTracking` | `bool` | `false`* | — | *MAUI 自动 `true`。启用以用于 Release Health。 |
| `CaptureFailedRequests` | `bool` | `true` | — | 自动捕获 HTTP 客户端错误 |
| `CacheDirectoryPath` | `string` | — | — | 离线事件缓存目录 |
| `ShutdownTimeout` | `TimeSpan` | — | — | 关闭时最大等待事件刷新时间 |
| `HttpProxy` | `string` | — | — | Sentry 请求的代理 URL |
| `EnableBackpressureHandling` | `bool` | `true` | — | 在交付失败时自动降低采样率 |
| `TraceIgnoreStatusCodes` | `IList<HttpStatusCodeRange>` | `[]` | — | 忽略 HTTP 响应状态与任何范围匹配的事务；例如，`[404]` 或 `[(500, 599)]` |
| `StrictTraceContinuation` | `bool` | `false` | — | 当 `true` 时，如果只有一方（SDK 或传入的 `sentry-org_id` 袋包）具有 org ID，则开始新的追踪。完全不匹配（两者都存在但不同）始终开始新的追踪，无论此设置如何。（需要 ≥6.6.0） |
| `OrgId` | `string` | 自动 | — | 用于追踪验证的组织 ID；从 DSN 子域自动解析（例如，`o123.ingest.sentry.io` → `"123"`）。推荐在自托管 Sentry、本地 Relay 或自定义域名中显式设置（需要 ≥6.6.0） |

### ASP.NET Core 扩展选项 (`SentryAspNetCoreOptions`)

| 选项 | 类型 | 默认值 | 备注 |
|----------|------|--------|-------|
| `MaxRequestBodySize` | `RequestSize` | `None` | `None`, `Small` (~4 KB), `Medium` (~10 KB), `Always` |
| `MinimumBreadcrumbLevel` | `LogLevel` | `Information` | 最小面包屑日志级别 |
| `MinimumEventLevel` | `LogLevel` | `Error` | 最小发送为 Sentry 事件的日志级别 |
| `CaptureBlockingCalls` | `bool` | `false` | 检测 `.Wait()` / `.Result` 线程池资源耗尽 |
| `FlushOnCompletedRequest` | `bool` | `false` | **对于 Lambda / 无服务器** |
| `IncludeActivityData` | `bool` | `false` | 捕获 `System.Diagnostics.Activity` 值 |

### MAUI 扩展选项 (`SentryMauiOptions`)

| 选项 | 类型 | 默认值 | 备注 |
|----------|------|--------|-------|
| `IncludeTextInBreadcrumbs` | `bool` | `false` | 来自 `Button`、`Label`、`Entry` 元素的文本。⚠️ PII 风险。 |
| `IncludeTitleInBreadcrumbs` | `bool` | `false` | 来自 `Window`、`Page` 元素的标题。⚠️ PII 风险。 |
| `IncludeBackgroundingStateInBreadcrumbs` | `bool` | `false` | `Window.Backgrounding` 事件状态。⚠️ PII 风险。 |

### 环境变量

| 变量 | 目的 |
|----------|------|
| `SENTRY_DSN` | 项目 DSN |
| `SENTRY_RELEASE` | 应用版本（例如 `my-app@1.2.3`） |
| `SENTRY_ENVIRONMENT` | 部署环境名称 |
| `SENTRY_AUTH_TOKEN` | MSBuild / `sentry-cli` 符号上传授权令牌 |

**ASP.NET Core：** 使用双下划线 `__` 作为层级分隔符：

```bash
export Sentry__Dsn="https://..."
export Sentry__TracesSampleRate="0.1"
```

### MSBuild 符号上传属性

| 属性 | 类型 | 默认值 | 描述 |
|----------|------|--------|-------|
| `SentryOrg` | `string` | — | Sentry 组织缩写 |
| `SentryProject` | `string` | — | Sentry 项目缩写 |
| `SentryUploadSymbols` | `bool` | `false` | 上传 PDB 文件以在堆栈跟踪中显示行号 |
| `SentryUploadSources` | `bool` | `false` | 上传源文件以显示源上下文 |
| `SentryCreateRelease` | `bool` | `false` | 在构建过程中自动创建 Sentry 发布 |
| `SentrySetCommits` | `bool` | `false` | 将 git 提交与发布关联 |
| `SentryUrl` | `string` | — | 自托管 Sentry URL |

---

## 验证

在向导或手动设置后，添加一个测试抛出并验证后删除：

```csharp
// ASP.NET Core: 添加一个临时端点
app.MapGet("/sentry-test", () =>
{
    throw new Exception("Sentry 测试错误 — 删除我");
});

// 或者显式捕获任何地方
SentrySdk.CaptureException(new Exception("Sentry 测试错误 — 删除我"));
```

然后检查您的 [Sentry 问题面板](https://sentry.io/issues/) — 错误应在约 30 秒内出现。

**验证清单：**

| 检查 | 方法 |
|----------|-----|
| 捕获异常 | 抛出测试异常，在 Sentry Issues 中验证 |
| 堆栈跟踪可读 | 检查文件名和行号是否出现 |
| 追踪激活 | 检查性能选项卡中的事务 |
| 日志记录连接 | 通过 `ILogger` 记录错误，检查它作为 Sentry 面包屑出现 |
| 符号上传工作 | 堆栈跟踪显示 `Controllers/HomeController.cs:42` 而不是 `<unknown>` |

---

## 第四阶段：跨链接

完成 .NET 设置后，检查是否有配套的前端项目：

```bash
# 检查相邻目录中的前端
ls ../frontend ../client ../web ../app 2>/dev/null

# 检查 JavaScript 框架指示符
cat ../package.json 2>/dev/null | grep -E '"next"|"react"|"vue"|"nuxt"' | head -3
```

如果找到前端，建议匹配的 SDK 技能：

| 前端检测到 | 建议技能 |
|----------|----------|
| Next.js (`"next"` 在 `package.json` 中) | `sentry-nextjs-sdk` |
| React SPA (`"react"` 没有 `"next"`) | `@sentry/react` — 查看 [docs.sentry.io/platforms/javascript/guides/react/](https://docs.sentry.io/platforms/javascript/guides/react/) |
| Vue.js | `@sentry/vue` — 查看 [docs.sentry.io/platforms/javascript/guides/vue/](https://docs.sentry.io/platforms/javascript/guides/vue/) |
| Nuxt | `@sentry/nuxt` — 查看 [docs.sentry.io/platforms/javascript/guides/nuxt/](https://docs.sentry.io/platforms/javascript/guides/nuxt/) |

连接前端和后端使用相同的 Sentry 项目可以启用**分布式追踪** — 一个跨浏览器、.NET 服务器和任何下游 API 的单个追踪视图。

---

## 故障排除

| 问题 | 原因 | 解决方案 |
|----------|-------|----------|
| 事件未出现 | DSN 配置错误 | 设置 `Debug = true` 并检查控制台输出中的 SDK 诊断消息 |
| 堆栈跟踪显示无文件/行 | 未上传 PDB 文件 | 在 `.csproj` 中添加 `SentryUploadSymbols=true`；在 CI 中设置 `SENTRY_AUTH_TOKEN` |
| WPF/WinForms 异常丢失 | 未设置 `IsGlobalModeEnabled` | 在 `SentrySdk.Init()` 中设置 `options.IsGlobalModeEnabled = true` |
| Lambda/无服务器事件丢失 | 容器在刷新前冻结 | 设置 `options.FlushOnCompletedRequest = true` |
| WPF UI 线程异常丢失 | 未连接 `DispatcherUnhandledException` | 在构造函数中注册 `App.DispatcherUnhandledException`（而不是 `OnStartup`） |
| Azure Functions 中出现重复的 HTTP 跨度 | Sentry 和 OTel 都检测到 HTTP | 设置 `options.DisableSentryHttpMessageHandler = true` |
| `TracesSampleRate` 没有效果 | 率为 `0.0`（默认） | 设置 `TracesSampleRate > 0` 以启用追踪 |
| `appsettings.json` 值被忽略 | 配置键格式错误 | 使用扁平键 `"Sentry:Dsn"` 或环境变量 `Sentry__Dsn`（双下划线） |
| `BeforeSend` 丢弃所有事件 | 无条件返回 `null` | 验证您的过滤逻辑；仅在您想要丢弃事件时返回 `null` |
| MAUI 原生崩溃未捕获 | 安装了错误的包 | 确认安装了 `Sentry.Maui`（而不仅仅是 `Sentry`） |
