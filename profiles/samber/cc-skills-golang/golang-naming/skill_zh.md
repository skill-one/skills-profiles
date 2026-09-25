> **社区默认值。** 如果一个公司技能明确地覆盖了 `samber/cc-skills-golang@golang-naming` 技能，则该技能优先。

# Go 命名规范

Go 倾向于使用简短、可读的名称。大小写控制可见性——大写表示导出，小写表示未导出。所有标识符必须使用 `MixedCaps`，绝不能使用下划线。

> "清晰胜于机智。" — Go 格言
>
> "设计架构，命名组件，记录细节。" — Go 格言

要忽略一条规则，只需在代码中添加注释。

## 快速参考

| 元素 | 规范 | 示例 |
| --- | --- | --- |
| 包 | 小写，单个单词，_test 后缀可用于测试文件 | `json`，`http`，`tabwriter`，`http_test` |
| 文件 | 小写，下划线可用 | `user_handler.go` |
| 导出名称 | UpperCamelCase | `ReadAll`，`HTTPClient` |
| 未导出 | lowerCamelCase | `parseToken`，`userCount` |
| 接口 | 方法名 + `-er` | `Reader`，`Closer`，`Stringer` |
| 结构体 | MixedCaps 名词 | `Request`，`FileHeader` |
| 常量 | MixedCaps（不是 ALL_CAPS） | `MaxRetries`，`defaultTimeout` |
| 接收者 | 1-2 个字母缩写 | `func (s *Server)`，`func (b *Buffer)` |
| 错误变量 | `Err` 前缀 | `ErrNotFound`，`ErrTimeout` |
| 错误类型 | `Error` 后缀 | `PathError`，`SyntaxError` |
| 构造函数 | 单一类型使用 `New`，多类型使用 `NewTypeName` | `ring.New`，`http.NewRequest` |
| 布尔字段 | 在字段和方法上使用 `is`，`has`，`can` 前缀 | `isReady`，`IsConnected()` |
| 测试函数 | `Test` + 函数名 | `TestParseToken` |
| 缩写词 | 全大写或全小写 | `URL`，`HTTPServer`，`xmlParser` |
| 变体：上下文 | `WithContext` 后缀 | `FetchWithContext`，`QueryContext` |
| 变体：原地操作 | `In` 后缀 | `SortIn()`，`ReverseIn()` |
| 变体：错误 | `Must` 前缀 | `MustParse()`，`MustLoadConfig()` |
| 选项函数 | `With` + 字段名 | `WithPort()`，`WithLogger()` |
| 枚举（iota） | 类型名前缀，零值等于未知 | `StatusUnknown` 在 0，`StatusReady` |
| 命名返回值 | 描述性，仅用于文档 | `(n int, err error)` |
| 错误字符串 | 全小写（包括缩写），无标点 | `"image: unknown format"`，`"invalid id"` |
| 导入别名 | 简短，仅在冲突时使用 | `mrand "math/rand"`，`pb "app/proto"` |
| 格式函数 | `f` 后缀 | `Errorf`，`Wrapf`，`Logf` |
| 测试表字段 | `got`/`expected` 前缀 | `input string`，`expected int` |

## MixedCaps

所有 Go 标识符必须使用 `MixedCaps`（或 `mixedCaps`）。绝不能在标识符中使用下划线——唯一的例外是测试函数的子案例（`TestFoo_InvalidInput`）、生成代码和 OS/cgo 互操作。这是有意义的，而不是装饰性的——Go 的导出机制依赖于大小写，工具假设整个代码库使用 MixedCaps。

```go
// ✓ 良好
MaxPacketSize
userCount
parseHTTPResponse

// ✗ 错误 — 这些规范与 Go 的导出机制和工具期望冲突
MAX_PACKET_SIZE   // C/Python 风格
max_packet_size   // snake_case
kMaxBufferSize    // 匈牙利标记
```

## 避免重复

Go 调用站点始终包含包名，因此将包名重复在标识符中浪费了读者的时间——`http.HTTPClient` 强制解析两次 "HTTP"。名称绝不能重复已经在包名、类型名或上下文中存在的信息。

```go
// 良好 — 调用站点清晰
http.Client       // 不是 http.HTTPClient
json.Decoder      // 不是 json.JSONDecoder
user.New()        // 不是 user.NewUser()
config.Parse()    // 不是 config.ParseConfig()

// 在包 sqldb 中：
type Connection struct{}  // 不是 DBConnection — "db" 已经在包名中

// Anti-stutter 适用于所有导出类型，而不仅仅是主结构：
// 在包 dbpool 中：
type Pool struct{}        // 不是 DBPool
type Status struct{}      // 不是 PoolStatus — 调用者写 dbpool.Status
type Option func(*Pool)   // 不是 PoolOption
```

## 常见的命名错误

这些规范是正确的，但并不明显——它们是最常见的命名错误来源：

**构造函数命名：** 当一个包导出一个单一的主要类型时，构造函数是 `New()`，而不是 `NewTypeName()`。这避免了重复——调用者写 `apiclient.New()` 而不是 `apiclient.NewClient()`。仅在包有多个可构造类型时使用 `NewTypeName()`（例如 `http.NewRequest`，`http.NewServeMux`）。

**布尔结构体字段：** 未导出的布尔字段必须使用 `is`/`has`/`can` 前缀——`isConnected`，`hasPermission`，而不是 `connected` 或 `permission`。导出获取器保留前缀：`IsConnected() bool`。这读起来自然，并区分了布尔值和其他类型。

**错误字符串全小写——包括缩写。** 写 `"invalid message id"` 而不是 `"invalid message ID"`，因为错误字符串通常与其他上下文连接（`fmt.Errorf("parsing token: %w", err)`）中混合大小写看起来不合适。哨兵错误应包括包名作为前缀：`errors.New("apiclient: not found")`。

**枚举零值：** 始终在 iota 位置 0 放置显式的 `Unknown`/`Invalid` 哨兵。`var s Status` 静默变为 0——如果这映射到一个真实的状态（如 `StatusReady`），代码可能表现得好像故意选择了状态，而实际上没有。

**子测试名称：** `t.Run()` 中的表格驱动测试案例名称应为全小写的描述性短语：`"valid id"`，`"empty input"`——不是 `"valid ID"` 或 `"Valid Input"`。

## 详细分类

有关完整规则、示例和理由，请参阅：

- **[包、文件和导入别名](./references/packages-files.md)** — 包命名（单个单词，小写，无复数），文件命名规范，导入别名模式（仅在冲突时使用以避免认知负担），以及目录结构。

- **[变量、布尔值、接收者和缩写词](./references/identifiers.md)** — 基于作用域的命名（长度匹配作用域：`i` 用于 3 行循环，更长的名称用于包级），单字母接收器约定（`s` 用于 Server），缩写词大小写（URL 不是 Url，HTTPServer 不是 HttpServer），以及布尔命名模式（isReady，hasPrefix）。

- **[函数、方法和选项](./references/functions-methods.md)** — 获取器/设置器模式（Go 省略 `Get`，所以 `user.Name()` 在调用站点读起来自然），构造函数约定（`New` 或 `NewTypeName`），命名返回值（仅用于文档），格式函数后缀（`Errorf`，`Wrapf`），以及功能选项（`WithPort`，`WithLogger`）。

- **[类型、常量和错误](./references/types-errors.md)** — 接口命名（`Reader`，`Closer` 后缀带 `-er`），结构体命名（名词，MixedCaps），常量（MixedCaps，不是 ALL_CAPS），枚举（类型名前缀，如 `StatusReady`），哨兵错误（`ErrNotFound` 变量），错误类型（`PathError` 后缀），以及错误消息规范（全小写，无标点）。

- **[测试命名](./references/testing.md)** — 测试函数命名（`TestFunctionName`），表格驱动测试字段约定（`input`，`expected`），测试辅助命名，以及子案例命名模式。

## 常见错误

| 错误 | 修正 |
| --- | --- |
| `ALL_CAPS` 常量 | Go 保留大小写用于可见性，而不是强调——使用 `MixedCaps` (`MaxRetries`) |
| `GetName()` 获取器 | Go 省略 `Get`，因为 `user.Name()` 在调用站点读起来自然。但 `Is`/`Has`/`Can` 前缀保留用于布尔谓词：`IsHealthy() bool` 而不是 `Healthy() bool`。这读起来像一个问题，并区分了布尔值和其他类型。 |
| `Url`，`Http`，`Json` 缩写词 | 混合大小写缩写词产生歧义（`HttpsUrl` — 是 `Https+Url` 吗？）。使用全大写或全小写 |
| `this` 或 `self` 接收者 | Go 方法调用频繁——使用 1-2 字母缩写（`s` 用于 `Server`）以减少视觉噪音 |
| `util`，`helper` 包 | 这些名称对内容没有描述——使用描述抽象的特定名称 |
| `http.HTTPClient` 重复 | 包名始终在调用站点存在——`http.Client` 避免重复读取 "HTTP" 两次 |
| `user.NewUser()` 构造函数 | 单一主要类型使用 `New()` — `user.New()` 避免重复类型名称 |
| `connected bool` 字段 | 纯形容词是模糊的——使用 `isConnected`，使字段读起来像真/假问题 |
| `"invalid message ID"` 错误 | 错误字符串必须全小写，包括缩写 — `"invalid message id"` |
| `StatusReady` 在 iota 0 | 零值应为哨兵 — `StatusUnknown` 在 0 捕获未初始化的值 |
| `"not found"` 错误字符串 | 哨兵错误应包括包名 — `"mypackage: not found"` 识别来源 |
| `userSlice` 类型名 | 类型编码实现细节——`users` 描述其持有内容，而不是如何实现 |
| 不一致的接收者名称 | 在同一类型的多个方法中切换名称会使读者困惑——使用一致的名称 |
| `snake_case` 标识符 | 下划线与 Go 的 MixedCaps 规范和工具期望冲突 — 使用 `mixedCaps` |
| 长名称用于短作用域 | 名称长度应匹配作用域 — `i` 适用于 3 行循环，`userIndex` 是噪音 |
| 命名常量按值 | 值会变化，角色不会——`DefaultPort` 在端口变化后仍然有效，`Port8080` 不行 |
| `FetchCtx()` 上下文变体 | `WithContext` 是 Go 标准后缀 — `FetchWithContext()` 立即可识别 |
| `sort()` 原地操作但无 `In` | 读者假设函数返回新值。`SortIn()` 信号突变 |
| `parse()` 出错时恐慌 | `MustParse()` 警告调用者失败时恐慌——意外属于名称 |
| 混合 `With*`，`Set*`，`Use*` | 代码库一致性 — `With*` 是 Go 的功能选项规范 |
| 复数包名 | Go 规范是单数 (`net/url` 而不是 `net/urls`) — 保持导入路径一致 |
| `Wrapf` 而无 `f` 后缀 | `f` 后缀表示格式字符串语义 — `Wrapf`，`Errorf` 告诉调用者传递格式参数 |
| 不必要的导入别名 | 别名增加认知负担。仅在冲突时别名 — `mrand "math/rand"` |
| 不一致的抽象名称 | 使用 `user`/`account`/`person` 表示同一概念迫使读者跟踪同义词 — 选择一个名称 |

应用这些修正意味着重命名现有标识符——→ 查看 `samber/cc-skills-golang@golang-gopls` 技能以安全地执行：它的重命名更新工作区中的每个调用站点，并拒绝会破坏接口满足的重命名，而 `grep/sed` 或手动 `Edit` 基于的重命名会无声地遗漏。

## 使用 Linter 强制执行

许多命名规范问题都由 linter 自动捕获：`revive`，`predeclared`，`misspell`，`errname`。查看 `samber/cc-skills-golang@golang-lint` 技能以配置和使用。

## 跨参考

- → 查看 `samber/cc-skills-golang@golang-code-style` 技能以了解更广泛的格式和风格决策
- → 查看 `samber/cc-skills-golang@golang-structs-interfaces` 技能以了解接口命名的深度和接收器设计
- → 查看 `samber/cc-skills-golang@golang-lint` 技能以了解自动强制执行（revive，predeclared，misspell，errname）
- → 查看 `samber/cc-skills-golang@golang-gopls` 技能以在应用命名修正时安全地重命名
- → 查看 `samber/cc-skills-golang@golang-refactoring` 技能以了解如何在决定重命名标识符后如何安全地大规模应用重命名（gopls Rename/Inline，blast-radius 映射，分阶段 PR 工作流)
