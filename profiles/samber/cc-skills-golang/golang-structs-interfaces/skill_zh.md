**角色设定：** 你是一位 Go 类型系统设计师。你倾向于使用小型、可组合的接口和具体的返回类型——你为了可测试性和清晰性而设计，而不是为了抽象而抽象。

> **社区默认值。** 如果一个公司技能明确地覆盖了 `samber/cc-skills-golang@golang-structs-interfaces` 技能，则该技能优先。

# Go 结构体与接口

## 接口设计原则

### 保持接口小

> "接口越大，抽象就越弱。" —— Go 谚语

接口应该包含 1-3 个方法。小接口更容易实现、模拟和组合。如果你需要一个更大的契约，请将其从小接口组合而成：

→ 参考在 `samber/cc-skills-golang@golang-naming` 技能中了解接口命名规范（方法名加 "-er" 后缀，规范名称）

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

// 由小接口组合而成
type ReadWriter interface {
    Reader
    Writer
}
```

从较小的接口组合成较大的接口：

```go
type ReadWriteCloser interface {
    io.Reader
    io.Writer
    io.Closer
}
```

### 在使用处定义接口

接口属于使用者。

接口必须在被使用处定义，而不是实现处。这使使用者控制契约，并避免为了一个接口而导入一个包。

```go
// package notification — 只定义它需要的部分
type Sender interface {
    Send(to, body string) error
}

type Service struct {
    sender Sender
}
```

`email` 包导出了一个具体的 `Client` 结构体——它不需要知道 `Sender`。

### 接受接口，返回结构体

函数应该接受接口参数以获得灵活性，并返回具体类型以获得清晰性。调用者可以完全访问返回类型的所有字段和方法；上游消费者仍然可以根据需要将结果分配给接口变量。

```go
// 良好——接受接口，返回具体类型
func NewService(store UserStore) *Service { ... }

// 不良——接口返回隐藏了具体类型的所有其他方法
func NewService(store UserStore) ServiceInterface { ... }
```

### 不要过早创建接口

> "不要设计接口，而是发现它们。"

在第二个实现存在之前编写的接口是对哪些方法会变化的一种猜测——这种猜测通常是错误的，因此抽象必须被重新塑造。同时，它增加了一层间接性，这会隐藏具体类型，使读者和工具难以理解。从具体类型开始；当第二个消费者、第二个实现或测试模拟需要它时，再提取接口。

```go
// 不良——只有一个实现的过早接口
type UserRepository interface {
    FindByID(ctx context.Context, id string) (*User, error)
}
type userRepository struct { db *sql.DB }

// 良好——先具体，需要时再提取接口
type UserRepository struct { db *sql.DB }
```

## 使零值有用

设计结构体以便它们可以在没有显式初始化的情况下工作。一个设计良好的零值可以减少构造函数的样板代码，并防止与 nil 相关的错误：

```go
// 良好——零值可以直接使用
var buf bytes.Buffer
buf.WriteString("hello")

var mu sync.Mutex
mu.Lock()

// 不良——零值是损坏的，需要构造函数
type Registry struct {
    items map[string]Item // nil map，写入时会引发恐慌
}

// 良好——惰性初始化保护零值
func (r *Registry) Register(name string, item Item) {
    if r.items == nil {
        r.items = make(map[string]Item)
    }
    r.items[name] = item
}
```

## 避免使用 `any` / `interface{}` 当具体类型足够时

自 Go 1.18 起，必须优先使用泛型而不是 `any` 进行类型安全的操作。仅在真正的边界处使用 `any`，在这些边界处类型确实是未知的（例如 JSON 解码、反射）：

```go
// 不良——丢失了类型安全性
func Contains(slice []any, target any) bool { ... }

// 良好——泛型，类型安全
func Contains[T comparable](slice []T, target T) bool { ... }
```

## 标准库中的关键接口

| 接口     | 包名         | 方法                                |
| ------- | ----------- | ----------------------------------- |
| `Reader` | `io`        | `Read(p []byte) (n int, err error)` |
| `Writer` | `io`        | `Write(p []byte) (n int, err error)` |
| `Closer` | `io`        | `Close() error`                    |
| `Stringer` | `fmt`       | `String() string`                  |
| `error`  | 内建        | `Error() string`                   |
| `Handler` | `net/http`  | `ServeHTTP(ResponseWriter, *Request)` |
| `Marshaler` | `encoding/json` | `MarshalJSON() ([]byte, error)`       |
| `Unmarshaler` | `encoding/json` | `UnmarshalJSON([]byte) error`         |

必须遵守规范方法签名——如果你的类型有一个 `String()` 方法，它必须匹配 `fmt.Stringer`。不要发明 `ToString()` 或 `ReadData()`。

## 编译时接口检查

使用空白标识符赋值来在编译时验证类型是否实现了接口。将其放置在类型定义附近：

```go
var _ io.ReadWriter = (*MyBuffer)(nil)
```

这不会在运行时产生任何成本。如果 `MyBuffer` 永远不再满足 `io.ReadWriter`，构建将立即失败。

## 类型断言与类型切换

类型断言必须使用逗号-OK 形式 (`s, ok := val.(string)`)——单值形式在类型不匹配时会引发恐慌而不是分支。使用类型切换来根据动态类型进行分发，并使用断言到一个小的可选接口 (`if f, ok := w.(Flusher); ok`) 来利用更丰富的实现，而不会扩大声明的参数类型。

→ 参考在 [类型断言与类型切换](references/type-assertions.md) 中了解类型切换的顺序、nil 情况和可选行为模式。

## 结构体与接口嵌入

### 结构体嵌入

嵌入将内部类型的成员方法和字段提升到外部类型——这是组合而不是继承：

```go
type Logger struct {
    *slog.Logger
}

type Server struct {
    Logger
    addr string
}

// s.Info(...) 可以工作——通过 Logger 提升自 slog.Logger
s := Server{Logger: Logger{slog.Default()}, addr: ":8080"}
s.Info("starting", "addr", s.addr)
```

提升方法的接收者是内部类型，而不是外部类型。外部类型可以通过定义一个同名的自己的方法来覆盖。

### 何时嵌入与命名字段

| 使用 | 条件 |
| --- | --- |
| **嵌入** | 你希望提升内部类型的完整 API——外部类型是增强版本的 |
| **命名字段** | 你只需要内部类型内部使用——外部类型是依赖项 |

```go
// 嵌入——Server 暴露所有 http.Handler 方法
type Server struct {
    http.Handler
}

// 命名字段——Server 使用 store 但不暴露其方法
type Server struct {
    store *DataStore
}
```

## 通过接口进行依赖注入

在构造函数中接受接口作为依赖项。这使组件解耦，并使测试变得简单：

```go
type UserStore interface {
    FindByID(ctx context.Context, id string) (*User, error)
}

type UserService struct {
    store UserStore
}

func NewUserService(store UserStore) *UserService {
    return &UserService{store: store}
}
```

在测试中，传递一个满足 `UserStore` 的模拟或存根——不需要真实的数据库。

## 结构体字段标签

序列化结构体中的导出字段必须有字段标签——没有标签，编码器会回退到 Go 字段名，因此重命名字段会无声地改变线格式：

```go
type Order struct {
    ID        string    `json:"id"         db:"id"`
    Total     float64   `json:"total"      db:"total"`
    CreatedAt time.Time `json:"created_at" db:"created_at"`
    Internal  string    `json:"-"          db:"-"`
}
```

→ 参考在 [结构体字段：标签和拷贝安全性](references/struct-fields.md) 中了解完整的标签指令表、`omitempty` 与 `omitzero` 的陷阱以及 `go vet` 诊断。

## 指针接收器与值接收器

| 使用指针 `(s *Server)` | 使用值 `(s Server)` |
| --- | --- |
| 方法修改接收器 | 接收器是小型且不可变的 |
| 接收器包含 `sync.Mutex` 或类似内容 | 接收器是基本类型（int、string） |
| 接收器是一个大型结构体 | 方法是一个只读访问器 |
| 一致性：如果任何方法使用指针，所有方法都应如此 | 映射和函数值（已经是引用类型） |

接收器类型必须跨类型的所有方法保持一致——如果有一个方法使用指针接收器，所有方法都应如此。

## 使用 `noCopy` 防止结构体拷贝

包含互斥锁、通道或内部指针的结构体在拷贝时会破坏：拷贝会复制锁状态，因此两个 goroutine 会守护两个不同的互斥锁，不变性会无声地消失。嵌入一个 `noCopy` 标记，以便 `go vet` 报告所有值拷贝，并通过指针传递此类结构体。

**诊断：** 1- `go vet ./...` — `copylocks` 报告锁持有结构体的值拷贝

→ 参考在 [结构体字段：标签和拷贝安全性](references/struct-fields.md) 中了解 `noCopy` 实现以及 `vet` 如何检测它。

## 参考链接

- → 参考在 `samber/cc-skills-golang@golang-naming` 技能中了解接口命名规范（Reader、Closer、Stringer）
- → 参考在 `samber/cc-skills-golang@golang-design-patterns` 技能中了解函数选项、构造函数和构建者模式
- → 参考在 `samber/cc-skills-golang@golang-dependency-injection` 技能中了解使用接口的 DI 模式
- → 参考在 `samber/cc-skills-golang@golang-code-style` 技能中了解值与指针函数参数（与接收器不同）
- → 参考在 `samber/cc-skills-golang@golang-gopls` 技能中了解安全的重命名和 `implementInterface` 代码操作——重命名参与接口满足的方法或接收器会更新每个调用位置，并拒绝会导致无声破坏接口的重命名，grep/sed 无法检测到

## 常见错误

| 错误 | 修复 |
| --- | --- |
| 大型接口（5+ 方法） | 分割成专注的 1-3 方法接口，如果需要则组合 |
| 在实现者包中定义接口 | 在使用处定义 |
| 从构造函数返回接口 | 返回具体类型 |
| 没有逗号-OK 的裸类型断言 | 总是使用 `v, ok := x.(T)` |
| 嵌入时你只需要几个方法 | 使用命名字段并显式委托 |
| 序列化结构体缺少字段标签 | 在序列化类型中标记所有导出字段 |
| 在一个类型中混合指针和值接收器 | 选择一个并保持一致性 |
| 忘记编译时接口检查 | 添加 `var _ Interface = (*Type)(nil)` |
| 使用 `ToString()` 而不是 `String()` | 遵守规范方法名称 |
| 过早创建只有一个实现的接口 | 先具体，需要时再提取接口 |
| 零值结构体中的 nil 映射/切片 | 在方法中使用惰性初始化 |
| 使用 `any` 进行类型安全的操作 | 使用泛型 (`[T comparable]`) 而不是 |
