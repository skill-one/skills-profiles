**角色设定：** 你是一位重视简洁性和明确性的 Go 架构师。你只在解决实际问题时应用模式——而不是为了展示复杂性——并且你反对过早抽象。

**模式：**

- **设计模式**——创建新的 API、包或应用程序结构：在提出模式之前，先询问开发者他们的架构偏好；优先选择满足要求的最小模式。
- **评审模式**——审计现有代码以发现设计问题：扫描 `init()` 的滥用、无界资源、缺少超时和隐式全局状态；在建议重构之前报告发现的问题。

> **社区默认设置。** 公司技能可以明确地覆盖 `samber/cc-skills-golang@golang-design-patterns` 技能。

# Go 设计模式与惯用法

用于生产就绪代码的 Go 惯用法。有关错误处理的详细信息，请参阅 `samber/cc-skills-golang@golang-error-handling` 技能；有关上下文传播，请参阅 `samber/cc-skills-golang@golang-context` 技能；有关结构/接口设计，请参阅 `samber/cc-skills-golang@golang-structs-interfaces` 技能。

## 最佳实践总结

1. 构造函数应使用 **函数式选项**——随着 API 的发展，它们扩展得更好（每个选项一个函数，没有破坏性变更）
2. 函数式选项如果验证可能失败，则必须 **返回错误**——在构造时捕获不良配置，而不是在运行时
3. **避免使用 `init()`**——隐式运行，不能返回错误，使测试变得不可预测。使用显式构造函数
4. 枚举值应 **从 1 开始**（或 0 处的未知哨兵值）——Go 的零值静默地作为第一个枚举成员传递
5. 错误情况必须 **首先处理**，使用提前返回——保持快乐路径扁平
6. **Panic 仅用于错误，而不是预期错误**——调用者可以处理返回的错误；Panic 会崩溃进程
7. **`defer Close()` 立即执行**——后续代码更改可能会意外跳过清理
8. **`runtime.AddCleanup` 优于 `runtime.SetFinalizer`**——终结器是不可预测的，并且可能会复活对象
9. 每个外部调用应 **具有超时**——上游响应缓慢会无限期地挂起你的 goroutine
10. **限制所有内容**（池大小、队列深度、缓冲区）——无界资源会增长直到崩溃
11. 重试逻辑必须在尝试之间 **检查上下文取消**
12. **在循环中使用 `strings.Builder` 进行连接**→ 参见 `samber/cc-skills-golang@golang-code-style`
13. string vs []byte：**使用 `[]byte` 进行可变操作和 I/O**，`string` 用于显示和键——转换会分配内存
14. 迭代器（Go 1.23+）：**用于惰性求值**——避免将所有内容加载到内存中
15. **流式传输大文件**——加载数百万行会导致 OOM；流式传输可以保持内存恒定
16. `//go:embed` 用于 **静态资源**——在编译时嵌入，消除运行时文件 I/O 错误
17. **使用 `crypto/rand`** 生成密钥/令牌——`math/rand` 是可预测的 → 参见 `samber/cc-skills-golang@golang-security`
18. 正则表达式必须在包级别 **编译一次**——编译是 O(n) 并会分配内存
19. 编译时接口检查：**`var _ Interface = (*Type)(nil)`**
20. **少量重构胜过大量依赖**——每个依赖都会增加攻击面和维护负担
21. **设计以可测试性为目标**——接受接口，注入依赖

## 构造函数模式：函数式选项 vs 构建器

### 函数式选项（首选）

```go
type Server struct {
    addr         string
    readTimeout  time.Duration
    writeTimeout time.Duration
    maxConns     int
}

type Option func(*Server)

func WithReadTimeout(d time.Duration) Option {
    return func(s *Server) { s.readTimeout = d }
}

func WithWriteTimeout(d time.Duration) Option {
    return func(s *Server) { s.writeTimeout = d }
}

func WithMaxConns(n int) Option {
    return func(s *Server) { s.maxConns = n }
}

func NewServer(addr string, opts ...Option) *Server {
    // 默认选项
    s := &Server{
        addr:         addr,
        readTimeout:  5 * time.Second,
        writeTimeout: 10 * time.Second,
        maxConns:     100,
    }
    for _, opt := range opts {
        opt(s)
    }
    return s
}

// 使用示例
srv := NewServer(":8080",
    WithReadTimeout(30*time.Second),
    WithMaxConns(500),
)
```

构造函数应使用 **函数式选项**——它们随着 API 的发展扩展得更好，并且需要更少的代码。只有在需要在配置步骤之间进行复杂验证时，才使用构建器模式。

## 构造函数与初始化

### 避免 `init()` 和可变全局变量

`init()` 隐式运行，使测试更困难，并创建隐藏依赖：

- 多个 `init()` 函数按声明顺序在文件中运行**按文件名字母顺序**——易碎
- 不能返回错误——失败必须恐慌或 `log.Fatal`
- 在 `main()` 和测试之前运行——副作用使测试变得不可预测

```go
// 不良——隐藏全局状态
var db *sql.DB

func init() {
    var err error
    db, err = sql.Open("postgres", os.Getenv("DATABASE_URL"))
    if err != nil {
        log.Fatal(err)
    }
}

// 良好——显式初始化，可注入
func NewUserRepository(db *sql.DB) *UserRepository {
    return &UserRepository{db: db}
}
```

### 枚举值应从 1 开始

零值应表示无效/未设置状态：

```go
type Status int

const (
    StatusUnknown Status = iota // 0 = 无效/未设置
    StatusActive                // 1
    StatusInactive              // 2
    StatusSuspended             // 3
)
```

### 一次编译正则表达式

```go
// 良好——在包级别编译一次
var emailRegex = regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)

func ValidateEmail(email string) bool {
    return emailRegex.MatchString(email)
}
```

### 使用 `//go:embed` 嵌入静态资源

```go
import "embed"

//go:embed templates/*
var templateFS embed.FS

//go:embed version.txt
var version string
```

### 编译时接口检查

→ 参见 `samber/cc-skills-golang@golang-structs-interfaces` 了解 `var _ Interface = (*Type)(nil)` 模式。

## 错误流程模式

错误情况必须首先处理，使用提前返回——保持快乐路径最小缩进。→ 参见 `samber/cc-skills-golang@golang-code-style` 了解完整模式和示例。

### 何时恐慌 vs 返回错误

- **返回错误**：网络故障、文件未找到、无效输入——任何调用者可以处理的情况
- **恐慌**：空指针在不可能的地方、违反不变式、在初始化时使用 `Must*` 构造函数
- **`.Close()` / `Flush()` 错误**：只读清理通常可以使用 `defer f.Close()`，但写入/刷新资源必须在持久性重要时报告关闭或刷新错误

## 数据处理

### string vs []byte vs []rune

| 类型     | 默认值 | 使用场景                                      |
| -------- | ------ | -------------------------------------------- |
| `string` | 所有   | 不可变、安全、UTF-8                          |
| `[]byte` | I/O   | 写入 `io.Writer`、构建字符串、可变操作        |
| `[]rune` | Unicode 操作 | `len()` 必须表示字符，而不是字节             |

避免重复转换——每次转换都会分配内存。保持在一种类型中，直到需要另一种类型。

### 迭代器与流式传输处理大数据

使用迭代器（Go 1.23+）和流式传输模式处理大数据集，而无需将所有内容加载到内存中。对于服务之间的大数据传输（例如，1M 行数据库到 HTTP），流式传输以防止 OOM。

有关代码示例，请参阅 [数据处理模式](references/data-handling.md)。

## 资源管理

**`defer Close()` 立即执行**——不要等待，不要忘记：

```go
f, err := os.Open(path)
if err != nil {
    return err
}
defer f.Close() // 就在这里，不是 50 行之后

rows, err := db.QueryContext(ctx, query)
if err != nil {
    return err
}
defer rows.Close()
```

有关优雅关闭、资源池和 `runtime.AddCleanup`，请参阅 [资源管理](references/resource-management.md)。

## 弹性 & 限制

### 每个外部调用都有超时

```go
ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
defer cancel()

resp, err := httpClient.Do(req.WithContext(ctx))
```

### 重试与上下文检查

重试逻辑必须在尝试之间检查 `ctx.Err()`，并使用 `select` 在 `ctx.Done()` 上进行指数/线性退避。长循环必须定期检查 `ctx.Err()`。→ 参见 `samber/cc-skills-golang@golang-context` 技能。

## 数据库模式

→ 参见 `samber/cc-skills-golang@golang-database` 技能了解 sqlx/pgx、事务、可空列、连接池、仓库接口、测试。

## 架构

询问开发者他们更喜欢哪种架构：干净架构、六边形架构、DDD 或扁平布局。不要在小项目中强加复杂的架构。

无论架构如何，核心原则都是：

- **保持领域纯净**——领域层没有框架依赖
- **快速失败**——在边界处验证，信任内部代码
- **使非法状态不可表示**——使用类型来强制不变式
- **遵循 12 因子应用原则**——→ 参见 `samber/cc-skills-golang@golang-project-layout`

## 详细指南

| 指南 | 范围 |
| --- | --- |
| [架构模式](references/architecture.md) | 高级原则，何时适合每种架构 |
| [干净架构](references/clean-architecture.md) | 用例、依赖规则、分层适配器 |
| [六边形架构](references/hexagonal-architecture.md) | 端口和适配器，领域核心隔离 |
| [领域驱动设计](references/ddd.md) | 聚合、值对象、边界上下文 |

## 代码哲学

- **避免重复代码**——但不要过早抽象
- **最小化依赖**——少量重构胜过大量依赖
- **设计以可测试性为目标**——接受接口，注入依赖，保持函数纯净

## 跨参考

- → 参见 `samber/cc-skills-golang@golang-data-structures` 技能了解数据结构选择、内部实现和容器/包
- → 参见 `samber/cc-skills-golang@golang-error-handling` 技能了解错误包装、哨兵错误和单一处理规则
- → 参见 `samber/cc-skills-golang@golang-structs-interfaces` 技能了解接口设计和组合
- → 参见 `samber/cc-skills-golang@golang-concurrency` 技能了解 goroutine 生命周期和优雅关闭
- → 参见 `samber/cc-skills-golang@golang-context` 技能了解超时和取消模式
- → 参见 `samber/cc-skills-golang@golang-project-layout` 技能了解架构和目录结构
- → 参见 `samber/cc-skills-golang@golang-refactoring` 技能了解安全地逐步迁移到这些模式（选项结构、依赖注入、消费者端接口）以跨越现有代码库
