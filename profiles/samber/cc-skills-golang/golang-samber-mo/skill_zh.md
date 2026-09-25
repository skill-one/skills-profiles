**角色设定：** 你是一位 Go 工程师，致力于将函数式编程的安全性引入 Go 语言。你使用单子（monads）来使不可能的状态无法表示——空值检查变成了类型约束，错误处理变成了可组合的管道。

**思考模式：** 在设计多步 Option/Result/Either 管道时，尽可能彻底地推理——错误的选择类型会创建不必要的包装/解包，这会违背单子的目的。在 Claude Code 中，使用 `ultrathink` 明确触发扩展思考。

# samber/mo — Go 中的单子与函数式抽象

Go 1.18+ 库，提供零依赖的类型安全单子类型。灵感来自 Scala、Rust 和 fp-ts。

**官方资源：**

- [pkg.go.dev/github.com/samber/mo](https://pkg.go.dev/github.com/samber/mo)
- [github.com/samber/mo](https://github.com/samber/mo)

这项技能并不详尽——请参考库文档和代码示例获取更多信息：

- 对于 Go 包文档、符号、版本、导入者和已知漏洞，→ 查看 `samber/cc-skills-golang@golang-pkg-go-dev` 技能（`godig`），优先于 Context7 获取 Go 包事实。
- 为了在您的代码中导航此库的使用（定义、调用位置、诊断），→ 查看 `samber/cc-skills-golang@golang-gopls` 技能（`gopls`）。
- Context7 仍然是未在 pkg.go.dev 索引的文档的备用方案。

```bash
go get github.com/samber/mo
```

有关函数式编程概念以及单子在 Go 中的价值的介绍，请参阅 [单子指南](./references/monads-guide.md)。

## 核心类型概览

| 类型 | 目的 | 可以将其视为... |
| --- | --- | --- |
| `Option[T]` | 可能有值的值 | Rust 的 `Option`，Java 的 `Optional` |
| `Result[T]` | 可能失败的运算 | Rust 的 `Result<T, E>`，替换 `(T, error)` |
| `Either[L, R]` | 两种可能类型之一的值 | Scala 的 `Either`，TypeScript 的区分联合 |
| `EitherX[L, R]` | X 种可能类型之一的值 | Scala 的 `Either`，TypeScript 的区分联合 |
| `Future[T]` | 异步尚未可用的值 | JavaScript 的 `Promise` |
| `IO[T]` | 懒惰的同步副作用 | Haskell 的 `IO` |
| `Task[T]` | 懒惰的异步计算 | fp-ts 的 `Task` |
| `State[S, A]` | 带状态的计算 | Haskell 的 `State` 单子 |

## Option[T] — 无需 nil 的可空值

表示一个值要么是存在的（`Some`），要么是不存在的（`None`）。在类型级别消除了空指针风险。

```go
import "github.com/samber/mo"

name := mo.Some("Alice")          // Option[string] 带有值
empty := mo.None[string]()        // Option[string] 没有值
fromPtr := mo.PointerToOption(ptr) // 空指针 -> None

// 安全提取
name.OrElse("Anonymous")  // "Alice"
empty.OrElse("Anonymous")  // "Anonymous"

// 如果存在则转换，不存在则跳过
upper := name.Map(func(s string) (string, bool) {
    return strings.ToUpper(s), true
})
```

**关键方法：** `Some`，`None`，`Get`，`MustGet`，`OrElse`，`OrEmpty`，`Map`，`FlatMap`，`Match`，`ForEach`，`ToPointer`，`IsPresent`，`IsAbsent`。

Option 实现 `json.Marshaler/Unmarshaler`，`sql.Scanner`，`driver.Valuer`——直接用于 JSON 结构和数据库模型。

有关完整的 API 参考，请参阅 [Option 参考](./references/option.md)。

## Result[T] — 将错误处理作为值

表示成功（`Ok`）或失败（`Err`）。等效于 `Either[error, T]`，但针对 Go 的错误模式进行了专门化。

```go
// 包装 Go 的 (value, error) 模式
result := mo.TupleToResult(os.ReadFile("config.yaml"))

// 同类型转换——错误会自动短路
upper := mo.Ok("hello").Map(func(s string) (string, error) {
    return strings.ToUpper(s), nil
})
// Ok("HELLO")

// 带回退提取
val := upper.OrElse("default")
```

**Go 限制：** 直接方法（`.Map`，`.FlatMap`）不能改变类型参数——`Result[T].Map` 返回 `Result[T]`，而不是 `Result[U]`。Go 方法不能引入新的类型参数。对于类型转换的转换（例如 `Result[[]byte]` 到 `Result[Config]`），请使用子包函数或 `mo.Do`：

```go
import "github.com/samber/mo/result"

// 类型转换管道：[]byte -> Config -> ValidConfig
parsed := result.Pipe2(
    mo.TupleToResult(os.ReadFile("config.yaml")),
    result.Map(func(data []byte) Config { return parseConfig(data) }),
    result.FlatMap(func(cfg Config) mo.Result[ValidConfig] { return validate(cfg) }),
)
```

**关键方法：** `Ok`，`Err`，`Errf`，`TupleToResult`，`Try`，`Get`，`MustGet`，`OrElse`，`Map`，`FlatMap`，`MapErr`，`Match`，`ForEach`，`ToEither`，`IsOk`，`IsError`。

有关完整的 API 参考，请参阅 [Result 参考](./references/result.md)。

## Either[L, R] — 两种类型的区分联合

表示一个值是两种可能类型中的一种。与 Result 不同，两边都不表示成功或失败——两者都是有效的替代方案。

```go
// 返回缓存数据或新鲜数据的 API
func fetchUser(id string) mo.Either[CachedUser, FreshUser] {
    if cached, ok := cache.Get(id); ok {
        return mo.Left[CachedUser, FreshUser](cached)
    }
    return mo.Right[CachedUser, FreshUser](db.Fetch(id))
}

// 模式匹配
result := fetchUser("user-123")
result.Match(
    func(cached CachedUser) mo.Either[CachedUser, FreshUser] { /* 使用缓存 */ },
    func(fresh FreshUser) mo.Either[CachedUser, FreshUser] { /* 使用新鲜 */ },
)
```

**何时使用 Either 而不是 Result：** 当一条路径是错误时使用 `Result[T]`。当两条路径都是有效替代方案时使用 `Either[L, R]`（缓存与新鲜、左与右、策略 A 与 B）。

`Either3[T1, T2, T3]`，`Either4` 和 `Either5` 扩展此功能以支持 3-5 种类型变体。

有关完整的 API 参考，请参阅 [Either 参考](./references/either.md)。

## Do 语法——带单子安全的命令式风格

`mo.Do` 将命令式代码包装在 `Result` 中，捕获 `MustGet()` 调用的恐慌：

```go
result := mo.Do(func() int {
    // MustGet 在 None/Err 上会引发恐慌——Do 会捕获它作为 Result 错误
    a := mo.Some(21).MustGet()
    b := mo.Ok(2).MustGet()
    return a * b  // 42
})
// result 是 Ok(42)

result := mo.Do(func() int {
    val := mo.None[int]().MustGet()  // 引发恐慌
    return val
})
// result 是 Err("no such element")
```

Do 语法将命令式 Go 风格与单子安全性连接起来——编写直线代码，自动捕获错误传播。

## 管道子包与直接链式调用的区别

samber/mo 提供了两种组合操作的方式：

**直接方法**（`.Map`，`.FlatMap`）——当输出类型等于输入类型时工作：

```go
opt := mo.Some(42)
doubled := opt.Map(func(v int) (int, bool) {
    return v * 2, true
})  // Option[int]
```

**子包函数**（`option.Map`，`result.Map`）——当输出类型与输入类型不同时需要：

```go
import "github.com/samber/mo/option"

// int -> string 类型转换：使用子包 Map
strOpt := option.Map(func(v int) string {
    return fmt.Sprintf("value: %d", v)
})(mo.Some(42))  // Option[string]
```

**管道函数**（`option.Pipe3`，`result.Pipe3`）——可读地链式多个类型转换：

```go
import "github.com/samber/mo/option"

result := option.Pipe3(
    mo.Some(42),
    option.Map(func(v int) string { return strconv.Itoa(v) }),
    option.Map(func(s string) []byte { return []byte(s) }),
    option.FlatMap(func(b []byte) mo.Option[string] {
        if len(b) > 0 { return mo.Some(string(b)) }
        return mo.None[string]()
    }),
)
```

**经验法则：** 对于同类型转换，使用直接方法。当步骤之间的类型发生变化时，使用子包函数 + 管道。

有关详细的管道 API 参考，请参阅 [管道参考](./references/pipelines.md)。

## 常见模式

### JSON API 响应使用 Option

```go
type UserResponse struct {
    Name     string            `json:"name"`
    Nickname mo.Option[string] `json:"nickname"`  // 优雅地忽略 null
    Bio      mo.Option[string] `json:"bio"`
}
```

### 数据库可空列

```go
type User struct {
    ID       int
    Email    string
    Phone    mo.Option[string]  // 实现 sql.Scanner + driver.Valuer
}

err := row.Scan(&u.ID, &u.Email, &u.Phone)
```

### 包装现有 Go API

```go
// 将 map 查找转换为 Option
func MapGet[K comparable, V any](m map[K]V, key K) mo.Option[V] {
    return mo.TupleToOption(m[key])  // m[key] 返回 (V, bool)
}
```

### 使用 Fold 进行统一提取

`mo.Fold` 通过 `Foldable` 接口在 Option、Result 和 Either 之间统一工作：

```go
str := mo.Fold[error, int, string](
    mo.Ok(42),  // 可用于 Option、Result 或 Either
    func(v int) string { return fmt.Sprintf("got %d", v) },
    func(err error) string { return "failed" },
)
// "got 42"
```

## 最佳实践

1. **优先使用 `OrElse` 而不是 `MustGet`**——`MustGet` 在不存在/错误值时会引发恐慌；仅在 `mo.Do` 块中捕获恐慌，或当您确定值存在时使用它
2. **在 API 边界使用 `TupleToResult`**——在边界将 Go 的 `(T, error)` 转换为 `Result[T]`，然后在您的域逻辑中使用 `Map`/`FlatMap` 链式操作
3. **使用 `Result[T]` 处理错误，使用 `Either[L, R]` 处理替代方案**——Result 专门用于成功/失败；Either 用于两种有效类型
4. **Option 用于可空字段，而不是零值**——`Option[string]` 区分“不存在”与“空字符串”；当空字符串是有效值时，使用普通的 `string`
5. **链式调用，不要嵌套**——`result.Map(...).FlatMap(...).OrElse(default)` 从左到右读取；当单子链式调用更清晰时，避免嵌套 if/else 模式
6. **使用子包管道进行多步类型转换**——当 3+ 步每步都改变类型时，`option.Pipe3(...)` 比嵌套函数调用更易读

有关高级类型（Future、IO、Task、State），请参阅 [高级类型参考](./references/advanced-types.md)。

如果您在 samber/mo 中遇到错误或意外行为，请在 <https://github.com/samber/mo/issues> 打开问题。

## 交叉引用

- → 查看 `samber/cc-skills-golang@golang-samber-lo` 技能，用于函数式集合转换（对切片的 Map、Filter、Reduce），可与 mo 类型组合
- → 查看 `samber/cc-skills-golang@golang-error-handling` 技能，用于 Go 习惯性错误处理模式
- → 查看 `samber/cc-skills-golang@golang-safety` 技能，用于 nil 安全和防御性 Go 编码
- → 查看 `samber/cc-skills-golang@golang-database` 技能，用于数据库访问模式
- → 查看 `samber/cc-skills-golang@golang-design-patterns` 技能，用于函数式选项和其他 Go 模式
