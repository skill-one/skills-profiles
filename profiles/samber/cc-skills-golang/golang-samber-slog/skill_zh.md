**角色设定：** 你是一位 Go 语言日志架构师。你设计日志处理流程，确保每条记录都能通过正确的处理器——采样器在早期过滤掉噪声，格式化器在记录离开流程前移除个人身份信息（PII），路由器将错误发送到 Sentry，而信息日志则发送到 Loki。

# samber/slog-\*\*\*\* — Go 语言结构化日志处理流程

20+ 可组合的 `slog.Handler` Go 包，适用于 Go 1.21 及更高版本。包含三个核心处理流程库，以及适用于 HTTP 的中间件和后端接收器，它们都实现了标准的 `slog.Handler` 接口。

**官方资源：**

- [github.com/samber/slog-multi](https://github.com/samber/slog-multi) — 处理器组合
- [github.com/samber/slog-sampling](https://github.com/samber/slog-sampling) — 吞吐量控制
- [github.com/samber/slog-formatter](https://github.com/samber/slog-formatter) — 属性转换

这项技能并非详尽无遗——请参考库文档和代码示例获取更多信息：

- 对于 Go 包文档、符号、版本、导入者和已知漏洞，→ 查看 `samber/cc-skills-golang@golang-pkg-go-dev` 技能（`godig`），优先于 Context7 获取 Go 包信息。
- 要在您的代码中导航此库的使用（定义、调用位置、诊断信息），→ 查看 `samber/cc-skills-golang@golang-gopls` 技能（`gopls`）。
- Context7 仍然作为未在 pkg.go.dev 索引的文档的备用方案。

## 处理流程模型

每个 samber/slog 处理流程都遵循标准顺序。记录从左到右流动——首先放置采样器以在早期过滤并避免在永远不会到达接收器的记录上浪费 CPU。

```
记录 → [采样器] → [管道：跟踪/PII] → [路由器] → [接收器]
```

顺序很重要：采样器在格式化之前可以节省 CPU。格式化器在路由之前可以确保所有接收器接收干净的属性。颠倒这个顺序会浪费被过滤掉的记录的工作。

## 核心库

| 库名 | 目的 | 关键构造函数 |
| --- | --- | --- |
| `slog-multi` | 处理器组合 | `Fanout`, `Router`, `FirstMatch`, `Failover`, `Pool`, `Pipe` |
| `slog-sampling` | 吞吐量控制 | `UniformSamplingOption`, `ThresholdSamplingOption`, `AbsoluteSamplingOption`, `CustomSamplingOption` |
| `slog-formatter` | 属性转换 | `PIIFormatter`, `ErrorFormatter`, `FormatByType[T]`, `FormatByKey`, `FlattenFormatterMiddleware` |

## slog-multi — 处理器组合

六种组合模式，每种模式针对不同的路由需求：

| 模式 | 行为 | 延迟影响 |
| --- | --- | --- |
| `Fanout(handlers...)` | 顺序广播到所有处理器 | 所有处理器延迟的总和 |
| `Router().Add(h, predicate).Handler()` | 路由到所有匹配的处理器 | 匹配处理器的延迟总和 |
| `Router().Add(...).FirstMatch().Handler()` | 仅路由到第一个匹配项 | 单个处理器的延迟 |
| `Failover()(handlers...)` | 顺序尝试直到一个成功 | 主要处理器的延迟（正常路径） |
| `Pool()(handlers...)` | 负载均衡：将每条记录发送到一个处理器 | 单个处理器的延迟 |
| `Pipe(middlewares...).Handler(sink)` | 接收器之前的中间件链 | 中间件开销 + 接收器 |

```go
// 将错误路由到 Sentry，所有日志输出到 stdout
logger := slog.New(
    slogmulti.Router().
        Add(sentryHandler, slogmulti.LevelIs(slog.LevelError)).
        Add(slog.NewJSONHandler(os.Stdout, nil)).
        Handler(),
)
```

内置谓词：`LevelIs`, `LevelIsNot`, `MessageIs`, `MessageIsNot`, `MessageContains`, `MessageNotContains`, `AttrValueIs`, `AttrKindIs`。

有关每种模式的完整代码示例，请参阅 [处理流程模式](references/pipeline-patterns.md)。

## slog-sampling — 吞吐量控制

| 策略 | 行为 | 适用于 |
| --- | --- | --- |
| Uniform | 放弃固定百分比的记录 | 开发/测试环境噪声过滤 |
| Threshold | 每个间隔记录前 N 条，然后以 R 的速率采样 | 生产环境——保留初始可见性 |
| Absolute | 每个间隔全局限制为 N 条记录 | 硬成本控制 |
| Custom | 用户函数返回每条记录的采样率 | 按级别或按时间规则 |

采样必须在处理流程中最外层——将其放置在格式化器之后会浪费被过滤掉的记录的 CPU。

```go
// Threshold：每 5 秒记录前 10 条，然后采样 10% — 错误始终通过 Router 传递
logger := slog.New(
    slogmulti.
        Pipe(slogsampling.ThresholdSamplingOption{
            Tick: 5 * time.Second, Threshold: 10, Rate: 0.1,
        }.NewMiddleware()).
        Handler(innerHandler),
)
```

匹配器将相似的记录分组以进行去重：`MatchByLevel()`, `MatchByMessage()`, `MatchByLevelAndMessage()`（默认），`MatchBySource()`, `MatchByAttribute(groups, key)`。

有关策略比较和配置详情，请参阅 [采样策略](references/sampling-strategies.md)。

## slog-formatter — 属性转换

作为 `Pipe` 中间件应用，以便所有下游处理器接收干净的属性。

```go
logger := slog.New(
    slogmulti.Pipe(slogformatter.NewFormatterMiddleware(
        slogformatter.PIIFormatter("user"),          // 掩盖 PII 字段
        slogformatter.ErrorFormatter("error"),       // 结构化错误信息
        slogformatter.IPAddressFormatter("client"),  // 掩盖 IP 地址
    )).Handler(slog.NewJSONHandler(os.Stdout, nil)),
)
```

关键格式化器：`PIIFormatter`, `ErrorFormatter`, `TimeFormatter`, `UnixTimestampFormatter`, `IPAddressFormatter`, `HTTPRequestFormatter`, `HTTPResponseFormatter`。通用格式化器：`FormatByType[T]`, `FormatByKey`, `FormatByKind`, `FormatByGroup`, `FormatByGroupKey`。使用 `FlattenFormatterMiddleware` 折叠嵌套属性。

## HTTP 中间件

跨框架的一致模式：`router.Use(slogXXX.New(logger))`。

可用：`slog-gin`, `slog-echo`, `slog-fiber`, `slog-chi`, `slog-http`（net/http）。

所有中间件共享一个 `Config` 结构，包含：`DefaultLevel`, `ClientErrorLevel`, `ServerErrorLevel`, `WithRequestBody`, `WithResponseBody`, `WithUserAgent`, `WithRequestID`, `WithTraceID`, `WithSpanID`, `Filters`。

```go
// Gin 带有过滤器 — 跳过健康检查
router.Use(sloggin.NewWithConfig(logger, sloggin.Config{
    DefaultLevel:     slog.LevelInfo,
    ClientErrorLevel: slog.LevelWarn,
    ServerErrorLevel: slog.LevelError,
    WithRequestBody:  true,
    Filters: []sloggin.Filter{
        sloggin.IgnorePath("/health", "/metrics"),
    },
}))
```

有关框架特定设置，请参阅 [HTTP 中间件](references/http-middlewares.md)。

## 后端接收器

所有接收器都遵循 `Option{}.NewXxxHandler()` 构造函数模式。

| 类别 | 包名 |
| --- | --- |
| 云服务 | `slog-datadog`, `slog-sentry`, `slog-loki`, `slog-graylog` |
| 消息传递 | `slog-kafka`, `slog-fluentd`, `slog-logstash`, `slog-nats` |
| 通知 | `slog-slack`, `slog-telegram`, `slog-webhook` |
| 存储 | `slog-parquet` |
| 桥接 | `slog-zap`, `slog-zerolog`, `slog-logrus` |

**批量处理器需要优雅关闭** — `slog-datadog`, `slog-loki`, `slog-kafka`, 和 `slog-parquet` 内部缓冲记录。在关闭时刷新（例如，`handler.Stop(ctx)` 对于 Datadog，`lokiClient.Stop()` 对于 Loki，`writer.Close()` 对于 Kafka）或缓冲日志会丢失。

有关配置示例和关闭模式，请参阅 [后端处理器](references/backend-handlers.md)。

## 常见错误

| 错误 | 原因 | 修复 |
| --- | --- | --- |
| 采样器在格式化器之后 | 浪费 CPU 格式化被过滤掉的记录 | 将采样器作为最外层处理器 |
| 广播到许多同步处理器 | 阻塞调用者 — 延迟是所有处理器延迟的总和 | 使用 `Pool()` 进行并发分发 |
| 批量处理器缺少关闭时刷新 | 关闭时缓冲日志丢失 | `defer handler.Stop(ctx)`（Datadog），`defer lokiClient.Stop()`（Loki），`defer writer.Close()`（Kafka） |
| 路由器没有默认/捕获处理器 | 未匹配的记录被静默过滤掉 | 添加一个没有谓词的处理器作为捕获器 |
| `AttrFromContext` 而没有 HTTP 中间件 | 上下文中没有请求属性可以提取 | 首先安装 `slog-gin`/`echo`/`fiber`/`chi` 中间件 |
| 使用 `Pipe` 而没有中间件 | 无操作包装器增加每个记录的开销 | 如果不需要中间件，请移除 `Pipe()` |

## 性能警告

- **Fanout 延迟** = 所有处理器延迟的总和（顺序）。如果有 5 个处理器每个 10ms，每次日志调用将花费 50ms。使用 `Pool()` 将减少到 max(latencies)
- **Pipe 中间件** 增加每个记录的函数调用开销 — 保持链短（2-4 个中间件）
- **slog-formatter** 顺序处理属性 — 许多格式化器会累积。对于热路径属性格式化，优先在您的类型上实现 `slog.LogValuer` 而不是
- **Benchmark** 在生产部署前使用 `go test -bench` 测试您的处理流程

**诊断：** 测量您的处理流程的每条记录分配和延迟，并识别链中分配最多的处理器。

## 最佳实践

1. **先采样，后格式化，最后路由** — 这种标准顺序最小化浪费并确保所有接收器接收干净的数据
2. **使用 Pipe 处理横切关注点** — 跟踪 ID 注入和 PII 清理应属于中间件，而不是每个处理器的逻辑
3. **使用 `slogmulti.NewHandleInlineHandler` 测试处理流程** — 在没有真实接收器的情况下断言每条记录是否到达每个阶段
4. **使用 `AttrFromContext`** 将 HTTP 中间件中的请求范围属性传播到所有处理器
5. **优先使用 Router 而不是 Fanout** 当处理器需要不同的记录子集时 — Router 评估谓词并跳过不匹配的处理器

## 交叉引用

- → 查看 `samber/cc-skills-golang@golang-observability` 技能以了解 slog 基础知识（级别、上下文、处理器设置、迁移）
- → 查看 `samber/cc-skills-golang@golang-error-handling` 技能以了解日志或返回规则
- → 查看 `samber/cc-skills-golang@golang-security` 技能以了解日志中的 PII 处理
- → 查看 `samber/cc-skills-golang@golang-samber-oops` 技能以了解 `samber/oops` 的结构化错误上下文

如果您在任何 samber/slog-\* 包中发现错误或意外行为，请在相关存储库（例如，[slog-multi/issues](https://github.com/samber/slog-multi/issues)，[slog-sampling/issues](https://github.com/samber/slog-sampling/issues)）中打开问题。
