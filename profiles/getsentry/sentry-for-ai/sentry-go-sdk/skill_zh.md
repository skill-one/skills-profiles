> [所有技能](../../SKILL_TREE.md) > [SDK 设置](../sentry-sdk-setup/SKILL.md) > Go SDK

# Sentry Go SDK

一个有主见的向导，扫描您的 Go 项目并指导您完成完整的 Sentry 设置。

## 在何时调用此技能

- 用户询问在 Go 应用中“添加 Sentry”或“设置 Sentry”
- 用户希望在 Go 中实现错误监控、跟踪、日志记录、指标或定时任务
- 用户提到 `sentry-go`、`github.com/getsentry/sentry-go` 或 Go Sentry SDK
- 用户希望监控 Go 中的恐慌、HTTP 处理程序或计划任务

> **注意：** 以下 SDK 版本和 API 反映了编写本文时 Sentry 文档的状态（sentry-go v0.43.0+）。
> 自 v0.33.0 起，SDK 需要 **Go 1.25 或更高版本**（支持最新的两个 Go 主版本）。
> 在实施之前，请始终参考 [docs.sentry.io/platforms/go/](https://docs.sentry.io/platforms/go/) 进行验证。

---

## 第一阶段：检测

在提出任何建议之前，运行这些命令以了解项目：

```bash
# 检查现有的 Sentry 依赖项
grep -i sentry go.mod 2>/dev/null

# 检测 Web 框架
grep -E "gin-gonic/gin|labstack/echo|gofiber/fiber|valyala/fasthttp|kataras/iris|urfave/negroni" go.mod 2>/dev/null

# 检测 gRPC
grep "google.golang.org/grpc" go.mod 2>/dev/null

# 检测日志库
grep -E "sirupsen/logrus|go.uber.org/zap|rs/zerolog|log/slog" go.mod go.sum 2>/dev/null

# 检测定时任务/调度器模式
grep -E "robfig/cron|go-co-op/gocron|jasonlvhit/gocron" go.mod 2>/dev/null

# 检测 OpenTelemetry 使用情况
grep "go.opentelemetry.io" go.mod 2>/dev/null

# 检查配套前端
ls frontend/ web/ client/ ui/ 2>/dev/null
```

**注意事项：**
- `sentry-go` 是否已经在 `go.mod` 中？如果是，请跳到第二阶段（配置功能）。
- 使用了哪个框架？（这决定了要安装哪个子包和中间件。）
- 使用了哪个日志库？（启用自动日志捕获。）
- 是否存在定时任务/调度器模式？（触发定时任务建议。）
- 是否有配套前端目录？（触发第四阶段跨链接。）

---

## 第二阶段：建议

根据您的发现，提出具体的建议。不要提出开放式问题——直接提出建议：

**推荐（核心覆盖）：**
- ✅ **错误监控** — 总是；捕获恐慌和未处理的错误
- ✅ **跟踪** — 如果检测到 HTTP 处理程序、gRPC 或数据库调用
- ✅ **日志记录** — 如果检测到 logrus、zap、zerolog 或 slog

**可选（增强可观察性）：**
- ⚡ **指标** — 自定义计数器和指标用于业务 KPI / SLO
- ⚡ **定时任务** — 检测计划任务中的静默失败
- ⚠️ **分析** — 在 sentry-go v0.31.0 中已移除；请参阅 `references/profiling.md` 获取替代方案

**建议逻辑：**

| 功能 | 当...推荐 |
|------|----------|
| 错误监控 | **始终** — 不可协商的基线 |
| 跟踪 | 检测到 `net/http`、gin、echo、fiber、gRPC 或数据库调用 |
| 日志记录 | 检测到 logrus、zap、zerolog 或 `log/slog` 导入 |
| 指标 | 需要业务事件、SLO 跟踪或计数器 |
| 定时任务 | 检测到 `robfig/cron`、`gocron` 或计划任务模式 |
| 分析 | ⚠️ **v0.31.0 中已移除** — 不要推荐；请参阅 `references/profiling.md` |

建议：*"我建议设置错误监控 + 跟踪 [+ 日志记录（如果适用）]。是否还需要我添加指标或定时任务？*"

---

## 第三阶段：指导

### 安装

```bash
# 核心 SDK（始终需要）
go get github.com/getsentry/sentry-go

# 框架子包——仅安装与检测到的框架匹配的部分：
go get github.com/getsentry/sentry-go/http      # net/http
go get github.com/getsentry/sentry-go/gin       # Gin
go get github.com/getsentry/sentry-go/echo      # Echo
go get github.com/getsentry/sentry-go/fiber     # Fiber
go get github.com/getsentry/sentry-go/fasthttp  # FastHTTP

# 日志库子包——仅安装与检测到的日志库匹配的部分：
go get github.com/getsentry/sentry-go/logrus    # Logrus
go get github.com/getsentry/sentry-go/slog      # slog (标准库，Go 1.21+) 
go get github.com/getsentry/sentry-go/zap       # Zap
go get github.com/getsentry/sentry-go/zerolog   # Zerolog

# gRPC 中间件（仅当检测到 `google.golang.org/grpc` 时）：
go get github.com/getsentry/sentry-go/grpc

# OpenTelemetry 桥接（仅当已使用 OpenTelemetry 时）：
go get github.com/getsentry/sentry-go/otel
```

### 快速入门——推荐初始化

在 `main()` 中添加任何其他代码之前添加。此配置使用合理的默认值启用最多功能：

```go
import (
    "log"
    "os"
    "time"
    "github.com/getsentry/sentry-go"
)

err := sentry.Init(sentry.ClientOptions{
    Dsn:              os.Getenv("SENTRY_DSN"),
    Environment:      os.Getenv("SENTRY_ENVIRONMENT"), // "production", "staging", 等
    Release:          release,                          // 在构建时通过 -ldflags 注入
    SendDefaultPII:   true,
    AttachStacktrace: true,

    // 跟踪（为生产环境调整采样率）
    EnableTracing:    true,
    TracesSampleRate: 1.0, // 在高流量生产环境中降低到 0.1–0.2

    // 日志记录
    EnableLogs: true,
})
if err != nil {
    log.Fatalf("sentry.Init: %s", err)
}
defer sentry.Flush(2 * time.Second)
```

**在构建时注入 `Release`（推荐）：**
```go
var release string // 由 -ldflags 设置

// go build -ldflags="-X main.release=my-app@$(git describe --tags)"
```

### 框架中间件

在 `sentry.Init` 之后，为您的框架注册 Sentry 中间件：

| 框架 | 导入路径 | 中间件调用 | `Repanic` | `WaitForDelivery` |
|------|---------|-----------|----------|------------------|
| `net/http` | `.../sentry-go/http` | `sentryhttp.New(opts).Handle(h)` | `true` | `false` |
| Gin | `.../sentry-go/gin` | `router.Use(sentrygin.New(opts))` | `true` | `false` |
| Echo | `.../sentry-go/echo` | `e.Use(sentryecho.New(opts))` | `true` | `false` |
| Fiber | `.../sentry-go/fiber` | `app.Use(sentryfiber.New(opts))` | `false` | `true` |
| FastHTTP | `.../sentry-go/fasthttp` | `sentryfasthttp.New(opts).Handle(h)` | `false` | `true` |
| Iris | `.../sentry-go/iris` | `app.Use(sentryiris.New(opts))` | `true` | `false` |
| Negroni | `.../sentry-go/negroni` | `n.Use(sentrynegroni.New(opts))` | `true` | `false` |

> **注意：** Fiber 和 FastHTTP 基于 `valyala/fasthttp`，没有内置的恢复功能。使用 `Repanic: false, WaitForDelivery: true`。

**在处理程序中访问 Hub：**
```go
// net/http, Negroni:
hub := sentry.GetHubFromContext(r.Context())

// Gin:
hub := sentrygin.GetHubFromContext(c)

// Echo:
hub := sentryecho.GetHubFromContext(c)

// Fiber:
hub := sentryfiber.GetHubFromContext(c)
```

### gRPC 集成

对于 gRPC 服务器和客户端，使用 `sentrygrpc` 中间件：

```go
import sentrygrpc "github.com/getsentry/sentry-go/grpc"

// 服务器：在创建 gRPC 服务器时注册中间件
server := grpc.NewServer(
    grpc.UnaryInterceptor(sentrygrpc.UnaryServerInterceptor()),
    grpc.StreamInterceptor(sentrygrpc.StreamServerInterceptor()),
)

// 客户端：在连接时注册中间件
conn, err := grpc.NewClient(
    address,
    grpc.WithUnaryInterceptor(sentrygrpc.UnaryClientInterceptor()),
    grpc.WithStreamInterceptor(sentrygrpc.StreamClientInterceptor()),
)

// 在 gRPC 处理程序中访问 Hub：
hub := sentry.GetHubFromContext(ctx)
```

### 对于每个同意的功能

逐个功能进行操作。加载每个功能的参考文件，按照其步骤操作，并在进入下一个功能之前进行验证：

| 功能 | 参考文件 | 加载时... |
|------|---------|----------|
| 错误监控 | `${SKILL_ROOT}/references/error-monitoring.md` | 始终（基线） |
| 跟踪 | `${SKILL_ROOT}/references/tracing.md` | HTTP 处理程序/分布式跟踪 |
| 分析 | `${SKILL_ROOT}/references/profiling.md` | 性能敏感的生产应用 |
| 日志记录 | `${SKILL_ROOT}/references/logging.md` | 检测到 logrus / zap / zerolog / slog |
| 指标 | `${SKILL_ROOT}/references/metrics.md` | 业务 KPI / SLO 跟踪 |
| 定时任务 | `${SKILL_ROOT}/references/crons.md` | 检测到调度器/定时任务模式 |

对于每个功能：`读取 ${SKILL_ROOT}/references/<功能>.md`，精确跟随步骤，验证其是否正常工作。

---

## 配置参考

### `ClientOptions` 的关键字段

| 选项 | 类型 | 默认值 | 目的 |
|------|------|--------|------|
| `Dsn` | `string` | `""` | 如果为空，则禁用 SDK；环境变量：`SENTRY_DSN` |
| `Environment` | `string` | `""` | 例如，`"production"`；环境变量：`SENTRY_ENVIRONMENT` |
| `Release` | `string` | `""` | 例如，`"my-app@1.0.0"`；环境变量：`SENTRY_RELEASE` |
| `SendDefaultPII` | `bool` | `false` | 包括 IP、请求头 |
| `AttachStacktrace` | `bool` | `false` | 在 `CaptureMessage` 调用中附加堆栈跟踪 |
| `SampleRate` | `float64` | `1.0` | 错误事件采样率（0.0 视为 1.0） |
| `EnableTracing` | `bool` | `false` | 启用性能跟踪 |
| `TracesSampleRate` | `float64` | `0.0` | 事务采样率 |
| `TracesSampler` | `TracesSampler` | `nil` | 自定义每个事务采样（覆盖采样率） |
| `EnableLogs` | `bool` | `false` | 启用 Sentry 日志功能 |
| `MaxBreadcrumbs` | `int` | `100` | 每个事件的最大面包屑数 |
| `MaxErrorDepth` | `int` | `100` | 解包错误链的最大深度 |
| `Debug` | `bool` | `false` | SDK 详细调试输出 |
| `BeforeSend` | `func` | `nil` | 钩子，用于修改/丢弃错误事件 |
| `BeforeSendTransaction` | `func` | `nil` | 钩子，用于修改/丢弃事务事件 |
| `IgnoreErrors` | `[]string` | `nil` | 用于丢弃错误的正则表达式模式 |
| `IgnoreTransactions` | `[]string` | `nil` | 用于丢弃事务的正则表达式模式 |

### 环境变量

| 变量 | 映射到 | 目的 |
|------|--------|------|
| `SENTRY_DSN` | `Dsn` | 数据源名称 |
| `SENTRY_RELEASE` | `Release` | 应用版本（例如，`my-app@1.0.0`） |
| `SENTRY_ENVIRONMENT` | `Environment` | 部署环境 |
| `HTTP_PROXY` / `HTTPS_PROXY` | `HTTPProxy` / `HTTPSProxy` | 出站代理 |

在 `ClientOptions` 中设置的选项 **覆盖** 环境变量。

---

## 验证

测试 Sentry 是否接收事件：

```go
// 在处理程序或测试中——触发真实的错误事件：
sentry.CaptureMessage("Sentry Go SDK 测试")

// 或者触发捕获的恐慌（在恢复中间件存在的情况下）：
panic("sentry 测试恐慌")
```

几秒钟后在 Sentry 仪表板中检查。如果什么也没有出现：
1. 在 `ClientOptions` 中设置 `Debug: true` — 将 SDK 内部信息打印到 stdout
2. 验证 DSN 是否正确且项目存在
3. 确保 `sentry.Flush(2 * time.Second)` 被调用（事件默认异步）

---

## 第四阶段：跨链接

完成 Go 设置后，检查是否有缺少 Sentry 覆盖的配套前端：

```bash
ls frontend/ web/ client/ ui/ 2>/dev/null
cat frontend/package.json web/package.json 2>/dev/null | grep -E '"react"|"svelte"|"vue"|"next"'
```

如果存在未配置 Sentry 的前端目录，建议匹配的技能：

| 检测到的前端 | 建议技能 |
|-------------|---------|
| React / Next.js | `sentry-react-sdk` |
| Svelte / SvelteKit | `sentry-svelte-sdk` |
| Vue | 使用 `@sentry/vue` — 请参阅 [docs.sentry.io/platforms/javascript/guides/vue/](https://docs.sentry.io/platforms/javascript/guides/vue/) |
| 其他 JS/TS | `sentry-react-sdk`（覆盖通用浏览器 JS 模式） |

---

## 故障排除

| 问题 | 解决方案 |
|------|---------|
| 事件未出现 | 设置 `Debug: true`，检查 DSN，验证 `sentry.Flush()` 是否被调用 |
| `sentry.Init` 返回错误 | 格式错误的 DSN — 检查格式：`https://<key>@o<org>.ingest.sentry.io/<project>` |
| 恐慌未捕获 | 确保在处理程序之前注册框架中间件 |
| `defer sentry.Flush` 未运行 | `os.Exit()` 跳过 `defer` — 在 `os.Exit()` 之前显式调用 `sentry.Flush()` |
| 缺少堆栈跟踪 | 为 `CaptureMessage` 设置 `AttachStacktrace: true`；`CaptureException` 自动工作 |
| Goroutine 事件缺少上下文 | 在创建 goroutine 之前克隆 hub：`hub := sentry.CurrentHub().Clone()` |
| 事务过多 | 降低 `TracesSampleRate` 或使用 `TracesSampler` 丢弃健康检查/指标端点 |
| Fiber/FastHTTP 未恢复 | 对于基于 fasthttp 的框架使用 `Repanic: false, WaitForDelivery: true` |
| `SampleRate: 0.0` 发送所有事件 | `0.0` 视为 `1.0`；要丢弃所有事件，请改为设置 `Dsn: ""` |
