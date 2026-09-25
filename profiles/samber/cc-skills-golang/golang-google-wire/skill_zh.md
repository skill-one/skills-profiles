**角色设定：** 你是一位使用 wire 进行编译时依赖注入的 Go 架构师。你让编译器捕获缺失的依赖项，将 `wire_gen.go` 视为已提交的源代码，并在每次图结构变更后重新运行 `wire ./...`。

**依赖项：**

- wire: `go install github.com/google/wire/cmd/wire@latest`

# 使用 google/wire 在 Go 中进行编译时依赖注入

代码生成式依赖注入工具。Wire 在编译时解析依赖关系图并生成普通的 Go 构造函数调用——无需运行时容器，无需反射。错误会在你运行 `wire ./...` 时出现，而不是在第一次请求时。

注意：`google/wire` 于 2025 年 8 月归档（功能完善；仍接受错误修复）。

**官方资源：** [pkg.go.dev](https://pkg.go.dev/github.com/google/wire) · [github.com/google/wire](https://github.com/google/wire) · [用户指南](https://github.com/google/wire/blob/main/docs/guide.md) · [最佳实践](https://github.com/google/wire/blob/main/docs/best-practices.md)

这项技能并不详尽——请参考库文档和代码示例获取更多信息：

- 对于 Go 包文档、符号、版本、导入者和已知漏洞，→ 查看 `samber/cc-skills-golang@golang-pkg-go-dev` 技能（`godig`），优先于 Context7 获取 Go 包事实。
- 要导航此库在你自己的代码中的使用（定义、调用位置、诊断信息），→ 查看 `samber/cc-skills-golang@golang-gopls` 技能（`gopls`）。
- Context7 仍然是未在 pkg.go.dev 索引的文档的回退方案。

```bash
go get -tool github.com/google/wire/cmd/wire@latest
go get github.com/google/wire
```

## wire 与运行时 DI 的对比

| 关注点       | wire                      | dig / fx / samber/do   |
| ------------ | ------------------------- | ---------------------- |
| 解析         | 编译时（代码生成）        | 运行时（反射）         |
| 错误检测     | `wire ./...` 失败        | 第一次 `Invoke`/启动时 |
| 运行时容器   | 无——纯 Go 调用          | 存在                  |
| 生命周期钩子 | 内置不提供              | fx: OnStart/OnStop     |
| 生成的文件   | `wire_gen.go`（已提交） | 无                    |

对于生命周期、懒加载和完整矩阵，请参阅 `samber/cc-skills-golang@golang-dependency-injection`。

## 提供者

提供者是任何 Go 函数——输入是依赖项，输出是提供类型。三种返回形式：

```go
func NewConfig() *Config                          { return &Config{Addr: ":8080"} }
func NewDB(cfg *Config) (*sql.DB, error)          { return sql.Open("postgres", cfg.DSN) }
func NewRedis(cfg *Config) (*redis.Client, func(), error) { // 清理链按逆序执行
    c := redis.NewClient(&redis.Options{Addr: cfg.RedisAddr})
    return c, func() { c.Close() }, nil
}
```

## 提供者集

`wire.NewSet` 用于分组提供者以复用。集可以引用其他集。

```go
// infra/wire.go
var InfraSet = wire.NewSet(
    NewConfig,
    NewDB,
    NewRedis,
)

// service/wire.go
var ServiceSet = wire.NewSet(
    NewUserRepo,
    NewUserService,
    wire.Bind(new(UserStore), new(*UserRepo)), // 接口绑定
)
```

保持集小：库集暴露一个稳定的表面（添加输入或移除输出会破坏下游注入器）。每个包一个集是一个有用的默认值。

## 注入器和 `//go:build wireinject`

注入器文件声明初始化函数。Wire 将其主体生成到 `wire_gen.go` 并替换占位符。

```go
//go:build wireinject

package main

import "github.com/google/wire"

// Wire 生成此函数的主体。
func InitApp() (*App, func(), error) {
    wire.Build(InfraSet, ServiceSet, NewApp)
    return nil, nil, nil // 被 codegen 替换
}
```

`//go:build wireinject` 标签防止占位符被编译到二进制文件中——只有 `wire_gen.go`（没有此标签）会通过 `go build`。没有此标签，两个文件定义了相同的函数，导致编译错误。

当使用占位符返回不方便时，可以使用替代语法：

```go
func InitApp() (*App, func(), error) {
    panic(wire.Build(InfraSet, ServiceSet, NewApp))
}
```

## 接口绑定

Wire 禁止隐式接口满足——你必须显式声明绑定，以便在多个类型实现相同接口时，图结构保持明确。

```go
var Set = wire.NewSet(
    NewPostgresUserRepo,
    wire.Bind(new(UserStore), new(*PostgresUserRepo)), // 告知 wire: *PostgresUserRepo 满足 UserStore
)
```

显式绑定可以防止在别处添加实现相同接口的新类型时图结构被破坏。

## 结构提供者和值

`wire.Struct` 从图中填充结构字段，无需手动构造函数。标记字段 `wire:"-"` 以排除它们。

```go
wire.Struct(new(Server), "Logger", "DB") // 注入命名字段
wire.Struct(new(Server), "*")            // 注入所有非排除字段
wire.Value(Foo{X: 42})                   // 常量表达式（无函数调用/通道）
wire.InterfaceValue(new(io.Reader), os.Stdin) // 接口类型的字面量
wire.FieldsOf(new(Config), "DSN", "Addr")    // 将结构字段作为图节点提升
```

有关 `wire:"-"` 排除标签和 `wire.FieldsOf` 的详细信息，请参阅 [advanced.md](references/advanced.md)。

## 消除重复类型的歧义

Wire 禁止为相同类型提供两个提供者。将底层类型包装在不同的命名类型中，以便每个类型恰好有一个提供者：

```go
type PrimaryDSN string
type ReplicaDSN string
```

## 完整应用程序示例

```go
// wire.go — 注入器，通过构建标签排除二进制文件
//go:build wireinject

package main

func InitApp() (*App, func(), error) {
    wire.Build(config.ConfigSet, infra.InfraSet, service.ServiceSet, NewApp)
    return nil, nil, nil
}

// main.go
func main() {
    app, cleanup, err := InitApp()
    if err != nil { log.Fatal(err) }
    defer cleanup()
    app.Run()
}
```

Wire 生成 `wire_gen.go`（纯 Go，已提交，不要编辑）。有关包含每个包集、清理密集型图和生成输出的完整示例，请参阅 [recipes.md](references/recipes.md)。

## 代码生成工作流

```bash
wire ./...           # 重新生成模块中所有注入器
wire check ./...     # 验证图结构而不重新生成（快速 CI 检查）
```

每次构造函数签名变更后运行 `wire ./...`。将 `//go:generate go run github.com/google/wire/cmd/wire` 添加到注入器文件中，以便 `go generate ./...` 也有效。提交 `wire_gen.go`——它必须与 CI 构建保持同步。

## 最佳实践

1. 不要手动编辑 `wire_gen.go`——它会在每次 `wire ./...` 运行时被覆盖。将其视为一个已提交的构建工件；真实来源是提供者和注入器文件。
2. 始终在注入器文件中添加 `//go:build wireinject`——遗漏它会导致重复符号的编译错误，因为占位符和生成的文件定义了相同的函数。
3. 使用命名类型来区分相同底层类型的值——wire 强制每个类型只有一个提供者；命名类型如 `type DSN string` 允许 `PrimaryDSN` 和 `ReplicaDSN` 共存。
4. 保持库提供者集最小并向后兼容——添加新的必需输入会破坏下游注入器；移除输出也会破坏。仅在相同版本中引入新创建的类型。
5. 从清理提供者返回 `(T, func(), error)` 并让 wire 链接它们——wire 生成正确的逆序清理并处理部分失败（如果构建中途失败，只有已构建的清理会运行）。
6. 保持注入器文件专注——每个文件一个函数，一次一个包导入。包含几十个 `wire.Build` 参数的胖注入器难以推理；委托给每个包的集。

## 常见错误

| 错误       | 修复 |
| ---------- | ---- |
| 手动编辑 `wire_gen.go` | 不要编辑它。更改提供者或注入器并重新运行 `wire ./...`。 |
| 缺少 `//go:build wireinject` | 将标签作为每个注入文件的第一行添加。 |
| 两个提供者返回 `*sql.DB` | 用命名结构类型包装：`type PrimaryDB struct { *sql.DB }`——Wire 无法区分指针类型别名。 |
| 未使用 `wire.Bind` 注入接口 | 在提供者集中添加 `wire.Bind(new(MyInterface), new(*MyImpl))`。 |
| 忘记更改后重新运行 `wire ./...` | 在 `go build` 之前运行 wire；将其添加到 `go generate` 或 Makefile 目标。 |
| 未加保护调用 `cleanup()` | Wire 在构建错误时返回 nil 清理；用 `if cleanup != nil { defer cleanup() }` 加保护。 |

## 测试

Wire 生成纯 Go 构造函数，因此单元测试使用手动注入——无需克隆或重置容器。有关测试模式（测试注入器用假提供者替换真实提供者、CI `wire_gen.go` 过期检查），请参阅 [testing.md](references/testing.md)。

## 进一步阅读

- [advanced.md](references/advanced.md) — 清理链、多个注入器、集嵌套、错误目录、代码生成标志、快速参考
- [recipes.md](references/recipes.md) — HTTP 服务器、多注入器构建、清理密集型图、CLI 嵌入
- [testing.md](references/testing.md) — 测试注入器、假绑定、CI 过期检查

## 交叉引用

- → 查看 `samber/cc-skills-golang@golang-dependency-injection` 技能以了解 DI 概念和库比较
- → 查看 `samber/cc-skills-golang@golang-uber-dig` 技能以了解无生命周期的运行时反射式 DI
- → 查看 `samber/cc-skills-golang@golang-uber-fx` 技能以了解带生命周期钩子、模块和信号感知的 `Run()` 的运行时 DI
- → 查看 `samber/cc-skills-golang@golang-samber-do` 技能以了解基于泛型的无反射 DI
- → 查看 `samber/cc-skills-golang@golang-structs-interfaces` 技能以了解接口设计模式
- → 查看 `samber/cc-skills-golang@golang-testing` 技能以了解通用测试模式

如果你在 google/wire 中遇到错误或意外行为，请通过 <https://github.com/google/wire/issues> 打开问题。
