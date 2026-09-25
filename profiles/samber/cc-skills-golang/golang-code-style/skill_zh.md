**编排模式：** 在跨大型代码库审查代码风格时，使用“并行化代码风格审查”部分中描述的子代理，每个子代理负责一个独立的风格问题，并合并它们的发现。在 Claude Code 中，使用 `ultracode` 显式地选择多代理编排。

> **社区默认值。** 一个明确覆盖 `samber/cc-skills-golang@golang-code-style` 技能的公司技能优先。

# Go 代码风格

需要人工判断的风格规则——格式化由静态分析器处理，此技能处理清晰度。命名规则参见 `samber/cc-skills-golang@golang-naming` 技能；设计模式参见 `samber/cc-skills-golang@golang-design-patterns` 技能；结构体/接口设计参见 `samber/cc-skills-golang@golang-structs-interfaces` 技能。

> “清晰胜于机智。” —— Go 谚语

忽略规则时，在代码中添加注释。

## 行长度与换行

没有严格的行长度限制，但超过 ~120 个字符的行必须换行。在**语义边界**处换行，而不是随意的列数。具有 4 个以上参数的函数调用必须每行一个参数——即使提示要求单行代码：

```go
// 良好——每个参数单独一行，右括号单独一行
mux.HandleFunc("/api/users", func(w http.ResponseWriter, r *http.Request) {
    handleUsers(
        w,
        r,
        serviceName,
        cfg,
        logger,
        authMiddleware,
    )
})
```

当函数签名过长时，真正的修复通常是**更少的参数**（使用选项结构体），而不是更好的换行。对于多行签名，将每个参数放在单独的一行。

## 变量声明

对于非零值应使用 `:=`，对于零值初始化应使用 `var`。这种形式表示意图：`var` 表示“这个从零开始”。

```go
var count int              // 零值，稍后设置
name := "default"          // 非零值，`:=` 是合适的
var buf bytes.Buffer       // 零值已准备好使用
```

### 切片与映射初始化

切片和映射必须显式初始化，不能为 nil。nil 映射在写入时会引发恐慌；nil 切片在 JSON 中序列化为 `null`（而空切片为 `[]`），这会令 API 消费者感到意外。

```go
users := []User{}                       // 始终初始化
m := map[string]int{}                   // 始终初始化
users := make([]User, 0, len(ids))      // 当容量已知时预分配
m := make(map[string]int, len(items))   // 当大小已知时预分配
```

不要推测性地预分配——`make([]T, 0, 1000)` 在常见情况是 10 个元素时会浪费内存。

### 复合字面量

复合字面量必须使用字段名——基于位置的字段会在类型添加或重新排序字段时失效：

```go
srv := &http.Server{
    Addr:         ":8080",
    ReadTimeout:  5 * time.Second,
    WriteTimeout: 10 * time.Second,
}
```

## 控制流

### 减少嵌套

错误和边缘情况必须首先处理（早期返回）。保持快乐路径的缩进最小：

```go
func process(data []byte) (*Result, error) {
    if len(data) == 0 {
        return nil, errors.New("empty data")
    }

    parsed, err := parse(data)
    if err != nil {
        return nil, fmt.Errorf("parsing: %w", err)
    }

    return transform(parsed), nil
}
```

### 消除不必要的 `else`

当 `if` 体的末尾是 `return`/`break`/`continue` 时，必须删除 `else`。对于简单的赋值，使用默认值然后覆盖——分配一个默认值，然后用独立的条件或 `switch` 覆盖：

```go
// 良好——使用 switch 的默认值然后覆盖（对于互斥覆盖最干净）
level := slog.LevelInfo
switch {
case debug:
    level = slog.LevelDebug
case verbose:
    level = slog.LevelWarn
}

// 不良——else-if 链隐藏了默认值的存在
if debug {
    level = slog.LevelDebug
} else if verbose {
    level = slog.LevelWarn
} else {
    level = slog.LevelInfo
}
```

### 复杂条件与初始化作用域

当 `if` 条件有 3 个以上操作数时，必须提取为命名布尔值——一堵 `||` 墙难以阅读且隐藏了业务逻辑。对于短路的收益，将昂贵的检查内联。 [详情](./references/details.md)

```go
// 良好——命名布尔值使意图清晰
isAdmin := user.Role == RoleAdmin
isOwner := resource.OwnerID == user.ID
isPublicVerified := resource.IsPublic && user.IsVerified
if isAdmin || isOwner || isPublicVerified || permissions.Contains(PermOverride) {
    allow()
}
```

仅在检查时需要时将变量作用域限制在 `if` 块内：

```go
if err := validate(input); err != nil {
    return err
}
```

### 使用 `switch` 而不是 If-Else 链

当多次比较同一个变量时，优先使用 `switch`：

```go
switch status {
case StatusActive:
    activate()
case StatusInactive:
    deactivate()
default:
    panic(fmt.Sprintf("unexpected status: %d", status))
}
```

## 函数设计

- 函数应**简短且专注**——一个函数，一个任务。
- 函数参数应**≤4 个**。超过这个数量，使用选项结构体（参见 `samber/cc-skills-golang@golang-design-patterns` 技能）。
- **参数顺序**：首先 `context.Context`，然后输入，最后输出目标。
- 裸露返回有助于非常短的函数（1-3 行）其中返回值很明显，但在需要滚动查找返回内容时变得令人困惑——在较长的函数中显式命名返回值。

```go
func FetchUser(ctx context.Context, id string) (*User, error)
func SendEmail(ctx context.Context, msg EmailMessage) error  // 分组到结构体
```

### 优先使用 `range` 进行迭代

应使用 `range` 而不是基于索引的循环。使用 `range n`（Go 1.22+）进行简单的计数。

```go
for _, user := range users {
    process(user)
}
```

## 值与指针参数

传递小类型（`string`、`int`、`bool`、`time.Time`）按值传递。当需要修改、传递大型结构体（~128+ 字节）或 `nil` 有意义时使用指针。 [详情](./references/details.md)

## 文件内代码组织

- **分组相关声明**：类型、构造函数、方法放在一起
- **顺序**：包文档、导入、常量、类型、构造函数、方法、辅助函数
- **每个文件一个主要类型**：当它有显著方法时
- **空导入**（`_ "pkg"`）注册副作用（初始化函数）。将它们限制在 `main` 和测试包中，使副作用在应用程序根处可见，而不是隐藏在库代码中
- **点导入**污染命名空间，并使无法判断名称的来源——在库代码中永远不要使用
- **激进地不导出**——你可以随时导出；不导出是一个破坏性变更。→ 参见 `samber/cc-skills-golang@golang-gopls` 技能安全地不导出——它的重命名会原子地更新每个调用位置，并在将方法小写会破坏接口满足时拒绝更改，破坏性变更 grep/sed 默默地发布。

## 字符串处理

使用 `strconv` 进行简单的转换（更快），`fmt.Sprintf` 进行复杂的格式化。在错误消息中使用 `%q` 使字符串边界可见。在循环中使用 `strings.Builder`，使用 `+` 进行简单的连接。

## 类型转换

优先使用显式、狭窄的转换。当有具体类型时使用泛型而不是 `any`：

```go
func Contains[T comparable](slice []T, target T) bool  // 不是 []any
```

## 哲学

- **“少量复制胜于少量依赖”**
- **使用 `slices` 和 `maps` 标准包**；对于过滤/分组/分块，使用 `github.com/samber/lo`
- **“反射永远不会清晰”**——除非必要，否则避免使用 `reflect`
- **不要过早抽象**——当模式稳定时提取
- **最小化公共表面**——每个导出名称都是一个承诺

## 并行化代码风格审查

在跨大型代码库审查代码风格时，使用最多 5 个并行子代理，每个代理针对一个独立的风格问题（例如控制流、函数设计、变量声明、字符串处理、代码组织）。

## 使用静态分析器强制执行

许多规则会自动强制执行：`gofmt`、`gofumpt`、`goimports`、`gocritic`、`revive`、`wsl_v5`。 → 参见 `samber/cc-skills-golang@golang-lint` 技能。

## 跨引用

- → 参见 `samber/cc-skills-golang@golang-naming` 技能了解标识符命名约定
- → 参见 `samber/cc-skills-golang@golang-structs-interfaces` 技能了解指针与值接收器、接口设计
- → 参见 `samber/cc-skills-golang@golang-design-patterns` 技能了解函数选项、构建器、构造函数
- → 参见 `samber/cc-skills-golang@golang-lint` 技能了解自动格式化强制执行
- → 参见 `samber/cc-skills-golang@golang-continuous-integration` 技能了解使用这些指南在 CI 中使用 AI 驱动的代码审查
- → 参见 `samber/cc-skills-golang@golang-refactoring` 技能安全地跨多个调用位置机械地应用守卫子句转换、函数提取和选项结构体迁移，一旦在规模上审查发现违规
