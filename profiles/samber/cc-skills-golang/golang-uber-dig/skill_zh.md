**角色设定：** 你是一位Go架构师，正在使用dig为应用程序构建依赖关系图。你将容器保持在组合根处，依赖于接口而不是具体类型，并将构造函数错误视为一级错误。

# 使用uber-go/dig在Go中进行依赖注入

基于反射的依赖注入工具包，设计用于为应用程序框架（它是`uber-go/fx`背后的引擎）提供动力，并在启动期间解析对象图。

**官方资源：**

- [pkg.go.dev/go.uber.org/dig](https://pkg.go.dev/go.uber.org/dig)
- [github.com/uber-go/dig](https://github.com/uber-go/dig)

这项技能并不详尽——请参考库文档和代码示例以获取更多信息：

- 对于Go包文档、符号、版本、导入者和已知漏洞，→ 查看`samber/cc-skills-golang@golang-pkg-go-dev`技能（`godig`），优先于Context7以获取Go包事实。
- 要导航此库在你的代码中的使用（定义、调用位置、诊断），→ 查看`samber/cc-skills-golang@golang-gopls`技能（`gopls`）。
- Context7仍然是一个备用选项，用于pkg.go.dev上未索引的文档。

```bash
go get go.uber.org/dig
```

## dig与fx的比较

fx基于dig构建，并共享相同的容器引擎——依赖注入原语（`Provide`、`Invoke`、`In`/`Out`结构体、命名值、值组）是相同的。`fx.In`/`fx.Out`是`dig.In`/`dig.Out`的重新导出。

fx在dig之上添加的内容：

| 关注点 | dig | fx |
| --- | --- | --- |
| 依赖注入容器 | ✅ `dig.New()` | ✅ (嵌入) |
| 生命周期钩子 | ❌ | ✅ `fx.Lifecycle` OnStart/OnStop |
| 模块系统 | ❌ | ✅ `fx.Module` 带有作用域装饰器 |
| 信号感知运行循环 | ❌ | ✅ `app.Run()` 在SIGINT/SIGTERM上阻塞 |
| 结构化事件日志记录 | ❌ | ✅ `fx.WithLogger` / `fxevent` |
| 启动/关闭超时 | ❌ | ✅ `fx.StartTimeout` / `fx.StopTimeout` |

**选择dig** 当你只需要接线图时：CLI工具、向调用者暴露容器的库、测试框架，或将依赖注入到管理自己生命周期的现有应用程序中。

**选择fx** 用于长时间运行的服务（HTTP服务器、工作进程、守护进程）——在那里，生命周期和信号处理是不可协商的。查看`samber/cc-skills-golang@golang-uber-fx`技能。

## 容器

```go
import "go.uber.org/dig"

c := dig.New()
```

有用的选项：`dig.DeferAcyclicVerification()`（更快启动）、`dig.RecoverFromPanics()`（将恐慌转换为`dig.PanicError`）、`dig.DryRun(true)`（验证而不调用）。

## Provide和Invoke

```go
// 注册一个构造函数——惰性，仅在输出需要时运行
err := c.Provide(func(cfg *Config) (*sql.DB, error) {
    return sql.Open("postgres", cfg.DSN)
})

// 从容器中拉出服务，将其作为函数参数请求
err = c.Invoke(func(db *sql.DB) error {
    return db.Ping()
})
```

构造函数是**惰性**和**缓存的**：每种输出类型只构建一次并共享（每个容器一个单例）。`Provide`在注册时如果构造函数格式不正确会报错；`Invoke`会返回构造函数的错误，并包装依赖路径。

dig构造函数是任何输入为依赖项、输出为提供类型的函数。`error`（最后一个返回值）表示构造失败。遵循“接受接口，返回结构体”。

## 使用`dig.In`的参数对象

一旦构造函数有4个以上的依赖项，嵌入`dig.In`将它们作为结构体字段并标记字段：

```go
type HandlerParams struct {
    dig.In

    Logger *zap.Logger
    DB     *sql.DB
    Cache  *redis.Client `optional:"true"`           // 如果未提供，则为零值
    DBRO   *sql.DB       `name:"readonly"`           // 命名依赖项
    Routes []http.Handler `group:"routes"`           // 值组
}

func NewHandler(p HandlerParams) *Handler { /* ... */ }
```

标签：`name:"..."`，`optional:"true"`，`group:"..."`。

## 使用`dig.Out`的结果对象

从一个构造函数返回多个值，并附加`name`/`group`标签到结果：

```go
type ConnResult struct {
    dig.Out

    ReadWrite *sql.DB `name:"primary"`
    ReadOnly  *sql.DB `name:"readonly"`
}

func NewConnections(cfg *Config) (ConnResult, error) { /* ... */ }
```

## 命名值

相同类型的两个提供者冲突。使用`dig.Name`消除歧义：

```go
c.Provide(NewPrimaryDB,  dig.Name("primary"))
c.Provide(NewReadOnlyDB, dig.Name("readonly"))
```

通过在`dig.In`字段中添加`name:"primary"` / `name:"readonly"`来消费。

## 值组

多个提供者，一个消费者切片——典型用于HTTP处理程序、健康检查、迁移：

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

**展平**——追加`,flatten`（例如`group:"routes,flatten"）以解包切片而不是嵌套它。组顺序**不保证**；如果顺序重要，从一个构造函数提供显式有序切片。

## 使用`dig.As`作为接口提供

注册一个具体构造函数，并在一个或多个接口下暴露它，而无需单独的适配器：

```go
c.Provide(NewPostgresDB, dig.As(new(Database), new(io.Closer)))
// 消费者请求Database或io.Closer；*PostgresDB保持隐藏。
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

dig没有**内置的生命周期**。如果你需要OnStart/OnStop钩子、信号处理和优雅关闭，请使用fx——查看`samber/cc-skills-golang@golang-uber-fx`技能。

对于Decorate、Scopes、可选依赖项、错误帮助程序和Visualize，请参阅[advanced.md](./references/advanced.md)。

## 最佳实践

1. 将容器保持在组合根处——永远不要将`*dig.Container`作为参数传递；将其视为`main()`的管道细节。服务定位器模式会破坏依赖注入的测试性收益。
2. 依赖于接口而不是具体类型——让你可以在测试中替换实现而不触及生产代码，并让你可以使用`dig.As`从宽结构体暴露窄接口。
3. 一旦构造函数有4个以上的依赖项，优先使用参数对象（`dig.In`结构体）——调用位置保持可读，添加新依赖项是一次性更改而不是签名破坏。
4. 按模块分组注册（每个调用`c.Provide`其类型的模块文件）——审查和重构成为每个模块的 concern，并且你可以稍后提取模块为fx.Module而无需重写接线。
5. 在测试中尽早验证图——在CI中调用`c.Invoke`针对组合根以在启动时暴露缺失提供者，而不是在第一次请求时。`DryRun(true)`跳过构造函数执行。
6. 从构造函数返回错误而不是恐慌——dig将它们包装在依赖路径中，这使得失败点显而易见。

## 常见错误

| 错误 | 修复 |
| --- | --- |
| 将容器传递给服务 | 容器属于`main()`。注入服务需要的类型依赖项；否则测试需要构建一个真实的容器。 |
| 没有使用`Name`的相同类型的两个提供者 | dig在`Provide`时出错。要么命名它们，要么合并到一个返回`dig.Out`结果结构体的单个提供者中。 |
| 忽略`Provide`错误 | 用`must`帮助程序包装每个`Provide`。一个无声的注册错误会在远后才变成类型错误。 |
| 使用组时顺序重要 | 组是无序的。如果顺序重要（中间件链、迁移序列），用一个构造函数提供显式有序切片。 |
| 构造函数在导入时具有副作用 | 保持`init()`为空——仅在构造函数内部，在图构建后开始工作。 |

## 测试

dig容器很便宜——为每个测试构建一个新鲜容器，用`Decorate`覆盖提供者，并调用`Invoke`来驱动系统。对于完整模式（每个测试的接线、共享帮助程序、CI中的图验证、断言接线时的错误、从构造函数恐慌中恢复），请参阅[testing.md](./references/testing.md)。

## 进一步阅读

- [advanced.md](./references/advanced.md) — Decorate、Scopes、可选依赖项、错误帮助程序、Visualize、完整快速参考
- [recipes.md](./references/recipes.md) — 端到端示例：带路由组的HTTP服务器、两个数据库、请求作用域、装饰器、干运行验证
- [testing.md](./references/testing.md) — 测试模式和图验证

## 跨参考

- → 查看`samber/cc-skills-golang@golang-uber-fx`技能以获取应用程序生命周期、模块和基于dig的信号感知Run()
- → 查看`samber/cc-skills-golang@golang-dependency-injection`技能以获取DI概念和库比较
- → 查看`samber/cc-skills-golang@golang-samber-do`技能以获取基于泛型的无反射替代方案
- → 查看`samber/cc-skills-golang@golang-google-wire`技能以获取编译时依赖注入（无运行时容器）
- → 查看`samber/cc-skills-golang@golang-structs-interfaces`技能以获取接口设计模式
- → 查看`samber/cc-skills-golang@golang-testing`技能以获取一般测试模式

如果你在uber-go/dig中遇到错误或意外行为，请在<https://github.com/uber-go/dig/issues>中打开问题。
