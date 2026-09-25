**角色设定：** 你是一位 Go 架构师，正在设置依赖注入。你将容器保留在组合根处，依赖接口而非具体类型，并将提供者错误视为一级错误。

# 在 Go 中使用 samber/do 进行依赖注入

基于 Go 1.18+ 泛型的 Go 类型安全依赖注入工具包。

**官方资源：**

- [pkg.go.dev/github.com/samber/do/v2](https://pkg.go.dev/github.com/samber/do/v2)
- [do.samber.dev](https://do.samber.dev)
- [github.com/samber/do/v2](https://github.com/samber/do)

这项技能并不详尽——请参考库文档和代码示例以获取更多信息：

- 对于 Go 包文档、符号、版本、导入者和已知漏洞，→ 查看 `samber/cc-skills-golang@golang-pkg-go-dev` 技能 (`godig`)，优先于 Context7 以获取 Go 包事实信息。
- 要导航此库在你代码中的使用（定义、调用位置、诊断），→ 查看 `samber/cc-skills-golang@golang-gopls` 技能 (`gopls`)。
- Context7 仍然是未在 pkg.go.dev 上索引的文档的备用方案。

安装 v2 —— v1 已被取代，并且缺少下面文档中提到的基于泛型的容器、作用域和生命周期钩子，因此 v1 时代的指导会误导此技能中的每个 API：

```bash
go get -u github.com/samber/do/v2
```

## 核心概念

### 注入器（容器）

```go
import "github.com/samber/do/v2"

injector := do.New()
```

### 服务类型

- **延迟**（默认）：在第一次请求时创建
- **立即**：在容器启动时立即创建
- **瞬态**：每次请求创建新实例
- **值**：预创建的值，无需实例化

### 提供者函数

服务必须通过提供者函数注册：

```go
type Provider[T any] func(i Injector) (T, error)
```

## 基本用法

### 1. 定义和注册服务

遵循“接受接口，返回结构体”原则：

```go
// 注册服务（默认延迟）
do.Provide(injector, func(i do.Injector) (Database, error) {
    return &PostgreSQLDatabase{connString: "postgres://..."}, nil
})

// 注册预创建的值
do.ProvideValue(injector, &Config{Port: 8080})

// 注册瞬态服务（每次请求创建新实例）
do.ProvideTransient(injector, func(i do.Injector) (*Logger, error) {
    return &Logger{}, nil
})

// 注册立即服务（在启动时立即创建）
do.ProvideValue(injector, &Config{Port: 8080})
```

### 2. 调用服务

容器只能在组合根处访问：

```go
// 带错误处理的调用——保留用于 DI 图外的调用位置
// （例如，必须优雅降级而不是崩溃的 HTTP 处理程序）
db, err := do.Invoke[Database](injector)

// MustInvoke 在出错时会触发 panic——在提供者中优先使用，由 do.Invoke 在父调用中恢复
db := do.MustInvoke[Database](injector)
```

在提供者函数中，始终使用 `do.MustInvoke`（或 `MustInvokeAs`/`MustInvokeNamed`/`MustInvokeStruct`）而不是返回错误的变体：

- 提供者已经返回 `(T, error)`，因此使用 `do.Invoke` 传播依赖失败会为每个调用增加额外的 `if err != nil { return nil, err }`。
- `do.MustInvoke` 会触发 panic，但 samber/do 会正确捕获并在外层 `Invoke` 调用中恢复该 panic，将其转换回常规错误——这个恢复发生在库内部，而不是调用者代码中，因此 `MustInvoke` 可以在提供者内部安全使用。
- 失败仍然会在组合根处作为错误出现，只是每个提供者中都没有手动样板代码。

### 3. 服务依赖

```go
func NewUserService(i do.Injector) (UserService, error) {
    db := do.MustInvoke[Database](i)
    cache := do.MustInvoke[Cache](i)
    return &userService{db: db, cache: cache}, nil
}

do.Provide(injector, NewUserService)
```

### 4. 隐式别名（推荐）

注册具体类型并作为接口调用，无需显式别名：

```go
// 注册具体类型
do.Provide(injector, func(i do.Injector) (*PostgreSQLDatabase, error) {
    return &PostgreSQLDatabase{}, nil
})

// 直接作为接口调用（隐式别名）
db := do.MustInvokeAs[Database](injector)
```

### 5. 命名服务

注册同类型的多重服务：

```go
do.ProvideNamed(injector, "primary-db", func(i do.Injector) (*Database, error) {
    return &Database{URL: "postgres://primary..."}, nil
})

mainDB := do.MustInvokeNamed[*Database](injector, "primary-db")
```

## 包组织

使用 `do.Package()` 按模块组织服务注册：

```go
// infrastructure/package.go
var Package = do.Package(
    do.Lazy(func(i do.Injector) (*postgres.DB, error) {
        cfg := do.MustInvoke[*Config](i)
        return postgres.Connect(cfg.DatabaseURL)
    }),
    do.Lazy(func(i do.Injector) (*redis.Client, error) {
        cfg := do.MustInvoke[*Config](i)
        return redis.NewClient(cfg.RedisURL), nil
    }),
)

// main.go
injector := do.New(infrastructure.Package, service.Package)
```

## 完整应用设置

```go
func main() {
    injector := do.New(
        infrastructure.Package,
        repository.Package,
        service.Package,
        transport.Package,
    )

    server := do.MustInvoke[*http.Server](injector)
    go server.ListenAndServe()

    _ = injector.ShutdownOnSignalsWithContext(context.Background(), os.Interrupt)
}
```

## 最佳实践

1. 依赖接口而非具体类型——让你可以在测试中替换实现，而无需触碰生产代码
2. 每个服务应只有一个职责——具有多重职责的服务更难测试且更难替换
3. 保持依赖树浅——超过 3-4 级的链会使初始化顺序变得脆弱，且错误更难追踪
4. 在提供者函数中处理错误——一个静默失败提供者会创建一个损坏的服务，该服务会在后续意想不到的地方崩溃
5. 使用作用域按生命周期组织服务——请求作用域的服务防止泄漏，全局服务防止重复初始化
6. 在提供者函数中使用 `do.MustInvoke*` 而不是 `do.Invoke*`——samber/do 会正确捕获并在外层 `Invoke` 调用中恢复该 panic，将其转换回常规错误，因此可以在提供者内部安全使用，并且你可以在不增加样板代码的情况下获得相同的错误传播

有关作用域、生命周期管理、结构体注入和调试，请参阅 [高级用法](./references/advanced.md)。

有关测试模式（克隆、覆盖、模拟），请参阅 [测试](./references/testing.md)。

## 快速参考

### 注册

| 函数                        | 目的                          |
| --------------------------- | ----------------------------- |
| `do.Provide[T]()`           | 注册延迟服务（默认）          |
| `do.ProvideNamed[T]()`      | 注册命名延迟服务              |
| `do.ProvideValue[T]()`      | 注册预创建的值                |
| `do.ProvideNamedValue[T]()` | 注册命名值                    |
| `do.ProvideTransient[T]()`  | 每次请求注册新实例            |
| `do.ProvideNamedTransient[T]()` | 注册命名瞬态服务            |
| `do.Package()`              | 分组服务注册                  |

### 调用

| 函数                   | 目的                                   |
| ---------------------- | -------------------------------------- |
| `do.Invoke[T]()`       | 获取服务（带错误）                    |
| `do.InvokeNamed[T]()`  | 获取命名服务                          |
| `do.InvokeAs[T]()`     | 获取匹配接口的第一个服务              |
| `do.InvokeStruct[T]()` | 使用标签将注入到结构体字段中          |
| `do.MustInvoke[T]()`    | 获取服务（出错时触发 panic）          |
| `do.MustInvokeNamed[T]()` | 获取命名服务（出错时触发 panic）        |
| `do.MustInvokeAs[T]()`  | 通过接口获取服务（出错时触发 panic） |
| `do.MustInvokeStruct[T]()` | 将注入到结构体（出错时触发 panic）       |

## 交叉引用

- → 查看 `samber/cc-skills-golang@golang-dependency-injection` 技能以获取 DI 概念、比较以及何时采用 DI 库
- → 查看 `samber/cc-skills-golang@golang-structs-interfaces` 技能以获取接口设计模式
- → 查看 `samber/cc-skills-golang@golang-testing` 技能以获取一般测试模式
