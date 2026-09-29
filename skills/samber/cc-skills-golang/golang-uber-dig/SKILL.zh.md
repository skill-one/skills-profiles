---
name: golang-uber-dig
description: 使用uber-go/dig在Go语言中实现依赖注入——基于反射的容器，Provide/Invoke，dig.In/dig.Out参数和结果对象，命名值，值组，可选依赖项，作用域和Decorate。在采用uber-go/dig时，代码库导入`go.uber.org/dig`，或在启动时连接应用程序图时使用。对于更高级的生命周期和模块，请参阅`samber/cc-skills-golang@golang-uber-fx`技能。
---

**角色设定：** 你是一位 Go 架构师，正在使用 dig 工具构建应用程序依赖图。你将容器置于组合根处，依赖接口而非具体类型，并将构造器错误视为一级错误。

# 使用 uber-go/dig 进行 Go 中的依赖注入

基于反射的依赖注入工具包，旨在为应用程序框架（它是 `uber-go/fx` 的引擎）提供支持，并在启动时解析对象图。

**官方资源：**

- [pkg.go.dev/go.uber.org/dig](https://pkg.go.dev/go.uber.org/dig)
- [github.com/uber-go/dig](https://github.com/uber-go/dig)

这项技能并不详尽——请参考库文档和代码示例以获取更多信息：

- 对于 Go 包文档、符号、版本、导入者和已知漏洞，→ 查看 `samber/cc-skills-golang@golang-pkg-go-dev` 技能 (`godig`)，优先于 Context7 以获取 Go 包事实信息。
- 要导航此库在你自己的代码中的使用（定义、调用位置、诊断），→ 查看 `samber/cc-skills-golang@golang-gopls` 技能 (`gopls`)。
- Context7 仍然是未在 pkg.go.dev 上索引的文档的备用方案。

```bash
go get go.uber.org/dig
```

## dig 与 fx 的比较

fx 基于 dig 构建，并共享相同的容器引擎——依赖注入基础 (`Provide`、`Invoke`、`In`/`Out` 结构体、命名值、值组) 是相同的。`fx.In`/`fx.Out` 是 `dig.In`/`dig.Out` 的重新导出。

fx 在 dig 之上添加的内容：

| 关注点 | dig | fx |
| --- | --- | --- |
| 依赖注入容器 | ✅ `dig.New()` | ✅ (嵌入) |
| 生命周期钩子 | ❌ | ✅ `fx.Lifecycle` OnStart/OnStop |
| 模块系统 | ❌ | ✅ `fx.Module` 带有作用域装饰器 |
| 信号感知运行循环 | ❌ | ✅ `app.Run()` 在 SIGINT/SIGTERM 上阻塞 |
| 结构化事件日志 | ❌ | ✅ `fx.WithLogger` / `fxevent` |
| 启动/关闭超时 | ❌ | ✅ `fx.StartTimeout` / `fx.StopTimeout` |

**选择 dig** 当你只需要接线图时：CLI 工具、向调用者暴露容器的库、测试框架，或将依赖注入嵌入到管理自身生命周期的现有应用程序中。

**选择 fx** 用于长时间运行的服务（HTTP 服务器、工作进程、守护进程）——在那里，生命周期和信号处理是不可协商的。参见 `samber/cc-skills-golang@golang-uber-fx` 技能。

## 容器

```go
import "go.uber.org/dig"

c := dig.New()
```

有用的选项：`dig.DeferAcyclicVerification()`（更快启动）、`dig.RecoverFromPanics()`（将恐慌转换为 `dig.PanicError`）、`dig.DryRun(true)`（验证而不调用）。

## Provide 和 Invoke

```go
// 注册一个构造器——惰性，仅在输出需要时运行
err := c.Provide(func(cfg *Config) (*sql.DB, error) {
    return sql.Open("postgres", cfg.DSN)
})

// 从容器中拉取服务，作为函数参数请求
err = c.Invoke(func(db *sql.DB) error {
    return db.Ping()
})
```

构造器是**惰性**和**缓存**的：每种输出类型只构建一次并共享（每个容器一个单例）。`Provide` 在注册时如果构造器格式不正确会报错；`Invoke` 返回构造器的错误，并包装依赖路径。

dig 构造器是任何输入为依赖项、输出为提供类型的函数。`error`（最后一个返回值）表示构造失败。遵循“接受接口，返回结构体”。

## 使用 `dig.In` 的参数对象

一旦构造器有 4 个或更多依赖项，嵌入 `dig.In` 将它们作为结构体字段并标记字段：

```go
type HandlerParams struct {
    dig.In

    Logger *zap.Logger
    DB     *sql.DB
    Cache  *redis.Client `optional:"true"`           // 如果未提供则为零值
    DBRO   *sql.DB       `name:"readonly"`           // 命名依赖项
    Routes []http.Handler `group:"routes"`           // 值组
}

func NewHandler(p HandlerParams) *Handler { /* ... */ }
```

标签：`name:"..."`，`optional:"true"`，`group:"..."`。

## 使用 `dig.Out` 的结果对象

从一个构造器返回多个值，并附加 `name`/`group` 标签到结果：

```go
type ConnResult struct {
    dig.Out

    ReadWrite *sql.DB `name:"primary"`
    ReadOnly  *sql.DB `name:"readonly"`
}

func NewConnections(cfg *Config) (ConnResult, error) { /* ... */ }
```

## 命名值

相同类型的两个提供者冲突。使用 `dig.Name` 消除歧义：

```go
c.Provide(NewPrimaryDB,  dig.Name("primary"))
c.Provide(NewReadOnlyDB, dig.Name("readonly"))
```

通过在 `dig.In` 字段中添加 `name:"primary"` / `name:"readonly"` 来消费。

## 值组

多个提供者，一个消费者切片——典型用于 HTTP 处理器、健康检查、迁移：

```go
type RouteResult struct {
    dig.Out
    Handler http.Handler `group:"routes"`
}

func NewUserHandler(db *sql.DB) RouteResult { /* ... */ }
func NewPostHandler(db *sql.DB) RouteResult { /* ... */ }

type ServerParams struct {
    dig.In
    Routes []http.Handler `group:"routes"`
}
```

**展平**——追加 `,flatten`（例如 `group:"routes,flatten"）以展开切片而不是嵌套它。组顺序**不保证**；如果顺序重要，从一个构造器提供显式有序切片。

## 使用 `dig.As` 提供（作为接口）

注册一个具体构造器，并在一个或多个接口下暴露它，而无需单独的适配器：

```go
c.Provide(NewPostgresDB, dig.As(new(Database), new(io.Closer)))
// 消费者请求 Database 或 io.Closer；*PostgresDB 保持隐藏。
```

## 完整应用程序示例

```go
func main() {
    c := dig.New()

    must(c.Provide(NewConfig))
    must(c.Provide(NewLogger))
    must(c.Provide(NewDatabase))
    must(c.Provide(NewServer))

    err := c.Invoke(func(srv *http.Server) error {
        return srv.ListenAndServe()
    })
    if err != nil {
        log.Fatal(err)
    }
}

func must(err error) { if err != nil { panic(err) } }
```

dig 没有内置的生命周期。如果你需要 OnStart/OnStop 钩子、信号处理和优雅关闭，使用 fx —— 参见 `samber/cc-skills-golang@golang-uber-fx` 技能。

对于 Decorate、Scopes、可选依赖项、错误帮助和 Visualize，参见 [advanced.md](./references/advanced.md)。

## 最佳实践

1. 将容器置于组合根处——永远不要将 `*dig.Container` 作为参数传递；将其视为 `main()` 的管道细节。服务定位器模式会破坏依赖注入的测试性收益。
2. 依赖接口而非具体类型——让你可以在测试中替换实现而不触及生产代码，并让你可以使用 `dig.As` 从宽结构体暴露窄接口。
3. 一旦构造器有 4 个或更多依赖项，优先使用参数对象 (`dig.In` 结构体) —— 调用位置保持可读性，添加新依赖项是一次性更改而不是签名破坏。
4. 按模块分组注册（每个调用 `c.Provide` 其类型的模块一个文件）——审查和重构成为每个模块的 concern，并且你可以稍后提取模块为 fx.Module 而无需重写接线。
5. 在测试中尽早验证图——在 CI 中对组合根调用 `c.Invoke` 以在启动时而不是第一次请求时暴露缺失提供者。`DryRun(true)` 跳过构造器执行。
6. 从构造器返回错误而不是恐慌——dig 将它们包装为依赖路径，这使得失败点显而易见。

## 常见错误

| 错误 | 修复 |
| --- | --- |
| 将容器传递给服务 | 容器属于 `main()`。注入服务需要的类型化依赖项；否则测试需要构建一个真实容器。 |
| 没有使用 `Name` 的相同类型的两个提供者 | dig 在 `Provide` 时报错。要么命名它们，要么合并为一个返回 `dig.Out` 结果结构体的提供者。 |
| 忽略 `Provide` 错误 | 用 `must` 辅助函数包装每个 `Provide`。一个无声的注册错误会在远后才变成类型缺失错误。 |
| 使用组时顺序重要 | 组是无序的。如果顺序重要（中间件链、迁移序列），用一个构造器提供显式有序切片。 |
| 构造器在导入时产生副作用 | 保持 `init()` 为空——仅在图构建后构造器内部开始工作。 |

## 测试

dig 容器是廉价的——为每个测试构建一个新鲜容器，用 `Decorate` 覆盖提供者，并调用 `Invoke` 来驱动系统。对于完整模式（每个测试的接线、共享帮助程序、CI 中的图验证、断言接线时的错误、从构造器恐慌中恢复），参见 [testing.md](./references/testing.md)。

## 进一步阅读

- [advanced.md](./references/advanced.md) — Decorate、Scopes、可选依赖项、错误帮助、Visualize、完整快速参考
- [recipes.md](./references/recipes.md) — 端到端示例：带路由组的 HTTP 服务器、两个数据库、请求作用域、装饰器、干运行验证
- [testing.md](./references/testing.md) — 测试模式和图验证

## 跨参考

- → 查看 `samber/cc-skills-golang@golang-uber-fx` 技能以获取应用程序生命周期、模块和 dig 之上的信号感知 Run()
- → 查看 `samber/cc-skills-golang@golang-dependency-injection` 技能以获取 DI 概念和库比较
- → 查看 `samber/cc-skills-golang@golang-samber-do` 技能以获取无反射的泛型替代方案
- → 查看 `samber/cc-skills-golang@golang-google-wire` 技能以获取编译时依赖注入（无运行时容器）
- → 查看 `samber/cc-skills-golang@golang-structs-interfaces` 技能以获取接口设计模式
- → 查看 `samber/cc-skills-golang@golang-testing` 技能以获取一般测试模式

如果你在 uber-go/dig 中遇到 bug 或意外行为，请 <https://github.com/uber-go/dig/issues> 打开问题。
