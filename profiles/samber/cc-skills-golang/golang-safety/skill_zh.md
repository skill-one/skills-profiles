**角色设定：** 你是一位防御性的 Go 工程师。你将所有未经测试的关于 nil、容量和数值范围的假设视为潜在的崩溃隐患。

# Go 安全：正确性与防御性编码

防止程序员错误——包括 bug、恐慌和正常（非对抗性）代码中的静默数据损坏。安全机制处理攻击者；安全机制处理我们自己。

## 最佳实践总结

1. **在类型集已知时优先使用泛型而非 `any`** —— 编译器在运行时捕获不匹配，而不是恐慌
2. **始终使用安全的类型断言** —— 对于普通接口使用逗号-ok (`v, ok := x.(T)`)；对于 Go 1.25+ 中的反射优先使用 `reflect.TypeAssert[T](value)` 而非 `value.Interface().(T)`。
3. **接口中的 typed nil 指针不等于 `== nil`** —— 类型描述符使其不为 nil
4. **向 nil 映射写入会引发恐慌** —— 始终在使用前初始化
5. **`append` 可能会重用底层数组** —— 如果容量允许，两个切片共享内存，会彼此静默地破坏对方
6. **从导出函数返回防御性副本** —— 否则调用者会修改你的内部结构
7. **`defer` 在函数退出时运行，而非循环迭代时** —— 将循环体提取到函数中
8. **整数转换会静默截断** —— `int64` 到 `int32` 会环绕而不报错
9. **浮点运算不精确** —— 使用 epsilon 比较或 `math/big`
10. **设计有用的零值** —— nil 映射字段在第一次写入时会引发恐慌；使用延迟初始化
11. **使用 `sync.Once` 进行延迟初始化** —— 即使在并发情况下也保证精确一次执行

## nil 安全

与 nil 相关的恐慌是 Go 中最常见的崩溃原因。

### nil 接口陷阱

接口存储（类型、值）。只有当两者都为 nil 时，接口才为 nil。返回 typed nil 指针会设置类型描述符，使其不为 nil：

```go
// ✗ 危险——接口{类型：*MyHandler，值：nil} 不等于 nil
func getHandler() http.Handler {
    var h *MyHandler // nil 指针
    if !enabled {
        return h // 接口{类型：*MyHandler，值：nil} 不等于 nil
    }
    return h
}

// ✓ 良好——显式返回 nil
func getHandler() http.Handler {
    if !enabled {
        return nil // 接口{类型：nil，值：nil} 等于 nil
    }
    return &MyHandler{}
}
```

### nil 映射、切片和通道的行为

| 类型    | 索引 nil  | 向 nil 写入 | nil 的 Len/Cap | 遍历 nil |
| ------- | -------------- | -------------- | -------------- | -------------- |
| 映射     | 零值     | **恐慌**      | 0              | 0 次迭代   |
| 切片   | **恐慌**      | **恐慌**      | 0              | 0 次迭代   |
| 通道   | 永久阻塞 | 永久阻塞 | 0              | 永久阻塞 |

```go
// ✗ 坏——nil 映射写入时引发恐慌
var m map[string]int
m["key"] = 1

// ✓ 良好——在方法中初始化或延迟初始化
m := make(map[string]int)

func (r *Registry) Add(name string, val int) {
    if r.items == nil { r.items = make(map[string]int) }
    r.items[name] = val
}
```

参见 **[Nil 安全深入探讨](./references/nil-safety.md)** 以了解 nil 接收者、泛型中的 nil 和 nil 接口的性能。

## 切片与映射安全

### 切片别名——append 陷阱

`append` 如果容量允许会重用底层数组。两个切片会共享内存：

```go
// ✗ 危险——a 和 b 共享底层数组
a := make([]int, 3, 5)
b := append(a, 4)
b[0] = 99 // 也修改 a[0]

// ✓ 良好——完整切片表达式强制重新分配
b := append(a[:len(a):len(a)], 4)
```

### 映射并发访问

映射绝对不能并发访问——→ 参见 `samber/cc-skills-golang@golang-concurrency` 了解同步原语。

参见 **[切片和映射深入探讨](./references/slice-map-safety.md)** 以了解遍历陷阱、子切片内存保留以及 `slices.Clone`/`maps.Clone`。

## 数值安全

### 隐式类型转换会静默截断

```go
// ✗ 坏——如果 val > math.MaxInt32 (3B 变为 -1.29B)，会静默环绕
var val int64 = 3_000_000_000
i32 := int32(val) // -1294967296 (静默环绕)

// ✓ 良好——转换前检查
if val > math.MaxInt32 || val < math.MinInt32 {
    return fmt.Errorf("值 %d 超出 int32 范围", val)
}
i32 := int32(val)
```

### 浮点比较

```go
// ✗ 坏——浮点运算不精确
var a, b, c float64 = 0.1, 0.2, 0.3
a+b == c // false

// ✓ 良好——使用 epsilon 比较
const epsilon = 1e-9
math.Abs((a+b)-c) < epsilon // true
```

### 除以零

整数除以零会引发恐慌。浮点除以零会产生 `+Inf`、`-Inf` 或 `NaN`。

```go
func avg(total, count int) (int, error) {
    if count == 0 {
        return 0, errors.New("除以零")
    }
    return total / count, nil
}
```

对于整数溢出作为安全漏洞，参见 `samber/cc-skills-golang@golang-security` 技能部分。

## 资源安全

### 循环中的 defer —— 资源累积

`defer` 在函数退出时运行，而非循环迭代时。资源会累积直到函数返回：

```go
// ✗ 坏——所有文件会保持打开状态直到函数返回
for _, path := range paths {
    f, _ := os.Open(path)
    defer f.Close() // 延迟执行直到函数退出
    process(f)
}

// ✓ 良好——将体提取到函数中，使 defer 在每次迭代时运行
for _, path := range paths {
    if err := processOne(path); err != nil { return err }
}
func processOne(path string) error {
    f, err := os.Open(path)
    if err != nil { return err }
    defer f.Close()
    return process(f)
}
```

### Goroutine 泄漏

→ 参见 `samber/cc-skills-golang@golang-concurrency` 了解 Goroutine 生命周期和泄漏预防。

## 不可变性与防御性复制

导出函数返回的切片/映射应返回防御性副本。

### 保护结构体内部

```go
// ✗ 坏——导出切片字段，任何人都可以修改
type Config struct {
    Hosts []string
}

// ✓ 良好——非导出字段，通过访问器返回副本
type Config struct {
    hosts []string
}

func (c *Config) Hosts() []string {
    return slices.Clone(c.hosts)
}
```

## 初始化安全

### 零值设计

设计类型使 `var x MyType` 安全——防止“忘记初始化”的 bug：

```go
var mu sync.Mutex   // ✓ 零值可用
var buf bytes.Buffer // ✓ 零值可用

// ✗ 坏——nil 映射写入时引发恐慌
type Cache struct { data map[string]any }
```

### 使用 `sync.Once` 进行延迟初始化

```go
type DB struct {
    once sync.Once
    conn *sql.DB
}

func (db *DB) connection() *sql.DB {
    db.once.Do(func() {
        db.conn, _ = sql.Open("postgres", connStr)
    })
    return db.conn
}
```

### `init()` 函数陷阱

→ 参见 `samber/cc-skills-golang@golang-design-patterns` 了解为什么应避免使用 `init()`，而应使用显式构造函数。

## 使用 Linters 强制执行

许多安全陷阱会自动被 linter 捕获：`errcheck`、`forcetypeassert`、`nilerr`、`govet`、`staticcheck`。参见 `samber/cc-skills-golang@golang-lint` 技能了解配置和使用。

### Go 1.25+ 反射类型断言

对于反射代码，优先使用 `reflect.TypeAssert[T]` 而非 `value.Interface().(T)`。

```go
v := reflect.ValueOf(x)
if s, ok := reflect.TypeAssert[string](v); ok {
    use(s)
}
```

## 常见错误

| 错误 | 修复 |
| --- | --- |
| 素数类型断言 `v := x.(T)` | 类型不匹配时引发恐慌，导致程序崩溃。使用 `v, ok := x.(T)` 优雅处理 |
| 接口函数返回 typed nil | 接口存储（类型，nil），不等于 nil。对于 nil 情况返回未类型化的 `nil` |
| 向 nil 映射写入 | nil 映射没有后备存储——写入会引发恐慌。使用 `make(map[K]V)` 或延迟初始化 |
| 假设 `append` 总是复制 | 如果容量允许，两个切片共享底层数组。使用 `s[:len(s):len(s)]` 强制复制 |
| 循环中的 `defer` | `defer` 在函数退出时运行，而非循环迭代时——资源会累积。将体提取到单独的函数 |
| 未进行边界检查的 `int64` 到 `int32` 转换 | 值会静默环绕（3B → -1.29B）。先检查 `math.MaxInt32`/`math.MinInt32` |
| 使用 `==` 比较浮点数 | IEEE 754 表示不精确 (`0.1+0.2 != 0.3`)。使用 `math.Abs(a-b) < epsilon` |
| 未检查零的整数除法 | 整数除以零会引发恐慌。除法前用 `if divisor == 0` 防护 |
| 返回内部切片/映射引用 | 调用者可以通过共享的后备数组修改你的结构体内部。返回防御性副本 |
| 多个 `init()` 与顺序假设 | `init()` 在文件间的执行顺序未指定。→ 参见 `samber/cc-skills-golang@golang-design-patterns`——使用显式构造函数 |
| 在 nil 通道上永久阻塞 | nil 通道在发送和接收时都会永久阻塞。始终在使用前初始化 |

## 交叉引用

- → 参见 `samber/cc-skills-golang@golang-concurrency` 技能了解并发访问模式和同步原语
- → 参见 `samber/cc-skills-golang@golang-data-structures` 技能了解切片/映射内部、容量增长和容器/包
- → 参见 `samber/cc-skills-golang@golang-error-handling` 技能了解 nil 错误接口陷阱
- → 参见 `samber/cc-skills-golang@golang-security` 技能了解与安全相关的安全问题（内存安全、整数溢出）
- → 参见 `samber/cc-skills-golang@golang-troubleshooting` 技能了解调试恐慌和竞态条件
- → 参见 `samber/cc-skills-golang@golang-continuous-integration` 技能了解使用这些指南在 CI 中进行自动 AI 驱动的代码审查
