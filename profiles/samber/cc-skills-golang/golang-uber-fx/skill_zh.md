**角色：** 你是一位 Go 架构师，正在使用 fx 构建一个长期运行的服务。你在组合根处进行图连接，将生命周期推入钩子而不是 `init()`，并将模块视为可重用的单元。

# 使用 uber-go/fx 进行 Go 应用程序连接

一个结合了基于反射的 DI 容器（基于 `uber-go/dig` 构建）、生命周期、模块系统、信号感知运行循环和结构化事件日志的应用程序框架。适用于需要启动顺序、优雅关闭和模块化组合的长期运行服务。

**官方资源：**

- [pkg.go.dev/go.uber.org/fx](https://pkg.go.dev/go.uber.org/fx)
- [uber-go.github.io/fx](https://uber-go.github.io/fx/)
- [github.com/uber-go/fx](https://github.com/uber-go/fx)

这项技能并不详尽——请参考库文档和代码示例以获取更多信息：

- 对于 Go 包文档、符号、版本、导入者和已知漏洞，→ 查看 `samber/cc-skills-golang@golang-pkg-go-dev` 技能（`godig`），优先于 Context7 以获取 Go 包事实。
- 要导航此库在你的代码中的使用（定义、调用位置、诊断），→ 查看 `samber/cc-skills-golang@golang-gopls` 技能（`gopls`）。
- Context7 仍然是一个备用方案，用于未在 pkg.go.dev 上索引的文档。

```bash
go get go.uber.org/fx
```

## fx vs. dig

fx 基于 dig 构建，并共享相同的基于反射的容器引擎。DI 原语（`Provide`、`Invoke`、`In`/`Out` 结构体、命名值、值组）是相同的——`fx.In`/`fx.Out` 是 `dig.In`/`dig.Out` 的重新导出。

fx 在其上添加的内容：

| 关注点 | dig | fx |
| --- | --- | --- |
| DI 容器 | ✅ `dig.New()` | ✅ (嵌入) |
| 生命周期钩子 | ❌ | ✅ `fx.Lifecycle` OnStart/OnStop |
| 模块系统 | ❌ | ✅ `fx.Module` 带有作用域装饰器 |
| 信号感知运行循环 | ❌ | ✅ `app.Run()` 在 SIGINT/SIGTERM 上阻塞 |
| 结构化事件日志 | ❌ | ✅ `fx.WithLogger` / `fxevent` |
| 启动/关闭超时 | ❌ | ✅ `fx.StartTimeout` / `fx.StopTimeout` |

**选择 fx** 用于长期运行的服务（HTTP 服务器、工作进程、守护进程）——生命周期和信号处理是必需的，模块使大型服务图变得可管理。

**选择原始 dig** 当你需要连接而无需框架时：CLI 工具、向调用者暴露容器的库、测试沙盒或将 DI 嵌入管理其自身生命周期的现有应用程序。查看 `samber/cc-skills-golang@golang-uber-dig` 技能。

## 应用程序

```go
import "go.uber.org/fx"

app := fx.New(
    fx.Provide(NewLogger, NewDatabase, NewServer),
    fx.Invoke(RegisterRoutes),
)
app.Run() // 在 SIGINT/SIGTERM 阻塞，然后运行 OnStop 钩子
```

启动阶段：`fx.New` 验证类型（构造函数不会运行）；`app.Start(ctx)` 按拓扑顺序运行每个 `fx.Invoke` 并触发 OnStart 钩子；main 在 `app.Done()` 上阻塞；`app.Stop(ctx)` 按反向顺序触发 OnStop 钩子。默认超时为 **15 秒**——使用 `fx.StartTimeout` / `fx.StopTimeout` 覆盖。

## Provide 和 Invoke

```go
fx.New(
    fx.Provide(NewLogger, NewDatabase, NewServer),  // 懒加载
    fx.Invoke(RegisterRoutes, StartMetricsExporter), // 总是在 Start 时运行
)
```

`fx.Provide` 注册构造函数；`fx.Invoke` 是触发器——如果没有一个 Invoke（直接或传递）引用一个类型，其构造函数将不会运行。

## 生命周期钩子

注入 `fx.Lifecycle` 并追加钩子。构造函数应快速返回；长时间运行的工作属于 `OnStart`。

```go
func NewHTTPServer(lc fx.Lifecycle, log *zap.Logger, cfg *Config) *http.Server {
    srv := &http.Server{Addr: cfg.Addr}

    lc.Append(fx.Hook{
        OnStart: func(ctx context.Context) error {
            ln, err := net.Listen("tcp", srv.Addr)
            if err != nil { return err }
            go srv.Serve(ln)         // 在 goroutine 中阻塞工作
            return nil
        },
        OnStop: func(ctx context.Context) error {
            return srv.Shutdown(ctx)
        },
    })
    return srv
}
```

两个回调都会接收到一个由 `StartTimeout`/`StopTimeout` 限制的上下文——请尊重取消。**OnStart 必须快速返回**——为阻塞工作在钩子内部启动一个 goroutine；否则启动挂起，依赖的钩子不会触发。

`fx.StartHook` / `fx.StopHook` / `fx.StartStopHook` 适配更简单的签名（没有上下文、没有错误，或两者都没有）：

```go
lc.Append(fx.StartStopHook(srv.Start, srv.Stop))   // 匹配对
```

## 参数和结果对象

fx 重新导出了 dig 的 `dig.In` / `dig.Out` 作为 `fx.In` / `fx.Out`。当构造函数有 4 个或更多依赖项时，或者当你需要 `name`/`group`/`optional` 标签时，使用它们。

```go
type ServerParams struct {
    fx.In

    Logger *zap.Logger
    DB     *sql.DB
    Cache  *redis.Client     `optional:"true"`
    Routes []http.Handler    `group:"routes"`
}

func NewServer(p ServerParams) *Server { /* ... */ }
```

## fx.Annotate

`fx.Annotate` 包装一个构造函数以添加标签或接口绑定，而无需 `fx.Out` 结构体。优先用于具有名称/组/As 绑定的便利性：

```go
fx.Provide(
    fx.Annotate(NewPrimaryDB, fx.ResultTags(`name:"primary"`)),
    fx.Annotate(NewPostgresDB, fx.As(new(Database))),    // 暴露接口
    fx.Annotate(NewUserHandler,
        fx.As(new(http.Handler)),
        fx.ResultTags(`group:"routes"`),
    ),
)
```

## 值组

多个构造函数，一个消费者切片——典型用于路由、健康检查、指标收集器：

```go
type RouteResult struct {
    fx.Out
    Handler http.Handler `group:"routes"`
}

type ServerParams struct {
    fx.In
    Routes []http.Handler `group:"routes"`
}
```

追加 `,flatten` (`group:"routes,flatten"`) 以展开切片而不是嵌套它。顺序**不保证**——如果顺序很重要，请从一个构造函数提供有序切片。

## fx.Module

`fx.Module` 将提供者、调用者和装饰器按名称分组。模块**将装饰器作用域限制为自己及其子代**——在 `fx.Module("db", ...)` 中重命名的日志记录器仅在模块内的代码中显示为重命名。

```go
var DatabaseModule = fx.Module("database",
    fx.Provide(NewConnection, NewUserRepository),
    fx.Decorate(func(log *zap.Logger) *zap.Logger {
        return log.Named("db")
    }),
)

func main() {
    fx.New(
        fx.Provide(NewConfig, NewLogger),
        DatabaseModule,
        HTTPModule,
    ).Run()
}
```

将每个模块视为一个小型库，可以将其移入另一个应用程序——其公共表面是它提供的类型。

对于 `fx.Supply`/`fx.Replace`/`fx.Decorate`、可选依赖项、自定义日志记录、手动生命周期和快速参考，请参阅 [advanced.md](./references/advanced.md)。

## 最佳实践

1. 保持 `main()` 薄——提供者、模块和单个 `Run()`。将实际工作推入模块，以便每个模块都可以独立测试。
2. 使用生命周期钩子而不是 `init()` 或从构造函数启动的 goroutine——Start/Stop 顺序取决于图拓扑，但 `init()` goroutine 不依赖，这会导致竞争和泄漏。
3. OnStart 必须快速返回——长时间工作在钩子内部的 goroutine 中进行。阻塞的 OnStart 挂起其余的启动。
4. 在钩子中尊重 `ctx.Done()`——忽略取消的钩子会报告为超时失败，但其 goroutine 会继续，导致资源泄漏。
5. 按模块而不是按层分组——一个模块拥有一个关注点（HTTP、DB、指标）的提供者、生命周期和装饰器。
6. 使用 `fx.Annotate` 而不是将构造函数包装在 `fx.Out` 结构体中——保持构造函数在 fx 外部可重用。
7. 使用 `fx.Supply` 替换 `fx.Provide` 以用于预构建的值（配置、命令行标志）。更短，表示意图。
8. 通过在 CI 中启动 `fx.New(...).Err()` 来验证图——在部署前捕获缺失的提供者和循环。

## 常见错误

| 错误 | 修复 |
| --- | --- |
| 在 OnStart 中直接进行长时间运行的工作 | 在 OnStart 内部启动一个 goroutine；钩子本身必须快速返回，以便依赖的钩子可以运行。 |
| `fx.Provide` 了一些应该使用 `fx.Supply` 的东西 | 预构建的值（配置、密钥）属于 `fx.Supply`——更清晰，并避免无操作的构造函数。 |
| 模块装饰器泄漏到兄弟模块 | 在 `fx.Module(...)` 内部装饰——装饰器仅流向子代。顶级 `fx.Decorate` 是全局的。 |
| 假设组顺序 | 组是无序的。如果顺序很重要，请从一个构造函数提供有序切片。 |
| 具有副作用的构造函数 | 副作用属于 OnStart——构造函数应该是廉价的和纯的，因为它们可能会并发和懒加载地运行。 |
| 遗忘 `fx.Invoke` | 没有 Invoke（直接或传递），构造函数不会运行。至少为每个应用程序添加一个 Invoke。 |

## 测试

使用 `go.uber.org/fx/fxtest` 将 fx 与 `*testing.T` 集成（失败调用 `t.Fatal`，`RequireStop` 注册为 `t.Cleanup`）。`fx.Populate(&target)` 从图中拉出值；`fx.Replace` 用假依赖项替换真实依赖项。完整模式在 [testing.md](./references/testing.md) 中。

## 进一步阅读

- [advanced.md](./references/advanced.md) — Supply/Replace/Decorate、可选依赖项、自定义事件日志、手动生命周期、完整快速参考
- [recipes.md](./references/recipes.md) — 完整的 HTTP 服务（带数据库/指标）、带优雅排干的背景工作、相同接口的多个实现、CLI 嵌入的手动生命周期
- [testing.md](./references/testing.md) — fxtest 模式、`fx.Replace`、`fx.Populate`、隔离的生命周期测试、CI 图验证

## 交叉引用

- → 查看 `samber/cc-skills-golang@golang-uber-dig` 技能以获取底层容器、`dig.In`/`dig.Out` 和无生命周期的 DI
- → 查看 `samber/cc-skills-golang@golang-dependency-injection` 技能以获取 DI 概念和库比较
- → 查看 `samber/cc-skills-golang@golang-samber-do` 技能以获取无反射的泛型替代方案
- → 查看 `samber/cc-skills-golang@golang-google-wire` 技能以获取编译时 DI（无运行时容器）
- → 查看 `samber/cc-skills-golang@golang-structs-interfaces` 技能以获取接口设计模式
- → 查看 `samber/cc-skills-golang@golang-context` 技能以获取 OnStart/OnStop 钩子中的上下文传播
- → 查看 `samber/cc-skills-golang@golang-testing` 技能以获取一般测试模式

如果你在 uber-go/fx 中遇到 bug 或意外行为，请通过 <https://github.com/uber-go/fx/issues> 打开问题。
