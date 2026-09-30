---
name: golang-data-structures
description: Go数据结构——切片（内部实现、容量增长、预分配、切片包）、映射（内部实现、哈希桶、映射包）、数组、容器/列表/堆/环形、字符串构建器与字节缓冲区、泛型集合、指针（unsafe.Pointer、weak.Pointer）以及拷贝语义。用于选择或优化Go数据结构、实现泛型容器、使用容器包、unsafe或weak指针，或疑问切片/映射内部实现。不适用于在性能分析识别瓶颈后应用优化模式（→参见`samber/cc-skills-golang@golang-performance`技能）。
---

**角色设定：** 你是一位精通 Go 语言数据结构内部实现的工程师。你根据内存布局、分配成本和访问模式来选择最合适的数据结构，而不是选择最熟悉的那种。

# Go 数据结构

内置数据结构和标准库数据结构：内部实现、正确使用方法以及选择指导。

- 关于安全陷阱（nil 映射、追加别名、防御性拷贝）请参考 `samber/cc-skills-golang@golang-safety` 技能。
- 关于通道和同步原语请参考 `samber/cc-skills-golang@golang-concurrency` 技能。
- 关于字符串/字节/字符的选择请参考 `samber/cc-skills-golang@golang-design-patterns` 技能。

## 最佳实践总结

1. **预分配切片和映射** 使用 `make(T, 0, n)` / `make(map[K]V, n)` 当大小已知或可估计时——避免重复增长拷贝和重新哈希
2. **数组** 应该优先于切片，仅适用于固定、编译时已知大小的场景（哈希摘要、IPv4 地址、矩阵维度）
3. **绝对不要依赖切片容量增长时机** —— Go 版本之间的增长算法可能改变，并且未来可能再次改变；你的代码不应依赖于何时分配新的底层数组
4. **使用 `container/heap`** 用于优先队列，**`container/list`** 仅在需要频繁中间插入时使用，**`container/ring`** 用于固定大小的循环缓冲区
5. **`strings.Builder`** 必须用于构建字符串；**`bytes.Buffer`** 必须用于双向 I/O（实现 `io.Reader` 和 `io.Writer` 接口）
6. 泛型数据结构应该使用**最严格的约束**——`comparable` 用于键，自定义接口用于排序
7. **`unsafe.Pointer`** 必须仅遵循 Go 规范中的 6 种有效转换模式——绝对不要跨语句存储在 `uintptr` 变量中
8. **`weak.Pointer[T]`** (Go 1.24+) 应该用于缓存和规范化映射，以允许 GC 回收条目

## 切片内部实现

切片是一个 3 字节头：指针、长度、容量。多个切片可以共享一个底层数组（→ 参考见 `samber/cc-skills-golang@golang-safety` 了解别名陷阱和头结构图）。

### 容量增长

- 小于 256 个元素：容量翻倍
- 大于等于 256 个元素：增长约 25% (`newcap += (newcap + 3*256) / 4`)
- 每次增长都会拷贝整个底层数组——O(n)

### 预分配

```go
// 精确大小已知
users := make([]User, 0, len(ids))

// 近似大小已知
results := make([]Result, 0, estimatedCount)

// 在批量追加前预增长（Go 1.21+）
s = slices.Grow(s, additionalNeeded)
```

### `slices` 包（Go 1.21+）

关键函数：`Sort`/`SortFunc`、`BinarySearch`、`Contains`、`Compact`、`Grow`。关于 `Clone`、`Equal`、`DeleteFunc` → 参考见 `samber/cc-skills-golang@golang-safety` 技能。

**[切片内部实现深入](./references/slice-internals.md)** — 完整 `slices` 包参考，增长机制，`len` vs `cap`，头拷贝，底层数组别名。

## 映射内部实现

映射是具有 8 个条目的桶和溢出链的哈希表。它们是引用类型——赋值映射时拷贝的是指针，而不是数据。

### 预分配

```go
m := make(map[string]*User, len(users)) // 避免在填充过程中重新哈希
```

### `maps` 包快速参考（Go 1.21+）

| 函数          | 目的                      |
| ------------- | ------------------------- |
| `Collect` (1.23+) | 从迭代器构建映射      |
| `Insert` (1.23+)  | 从迭代器插入条目      |
| `All` (1.23+)     | 迭代所有条目    |
| `Keys`, `Values`  | 迭代键/值   |

关于 `Clone`、`Equal`、排序迭代 → 参考见 `samber/cc-skills-golang@golang-safety` 技能。

**[映射内部实现深入](./references/map-internals.md)** — Go 映射如何存储和哈希数据，桶溢出链，为什么映射永远不会缩小（以及如何处理），比较映射性能与替代方案。

## 数组

固定大小、值类型。赋值时完全拷贝。用于编译时已知大小的场景：

```go
type Digest [32]byte           // 固定大小，值类型
var grid [3][3]int             // 多维
cache := map[[2]int]Result{}   // 数组是可比较的——可用作映射键
```

其他场景优先选择切片——数组不能增长，且按值传递（对于大尺寸代价高昂）。

## `container` 标准库

| 包       | 数据结构   | 适用场景     |
| -------- | ---------- | ------------ |
| `container/list` | 双向链表   | LRU 缓存，频繁中间插入/删除 |
| `container/heap` | 最小堆（优先队列） | Top-K，调度，Dijkstra |
| `container/ring` | 循环缓冲区 | 滚动窗口，循环调度 |
| `bufio`  | 缓冲读写/扫描器 | 高效的读写小数据 I/O |

容器类型使用 `any`（无类型安全）——考虑使用泛型包装器。**[容器模式，bufio，以及示例](./references/containers.md)** — 何时使用每种容器类型，泛型包装器以增加类型安全，以及 `bufio` 高效 I/O 模式。

## `strings.Builder` vs `bytes.Buffer`

用于纯字符串连接（`String()` 时避免拷贝），需要 `io.Reader` 或字节操作时使用 `bytes.Buffer`。两者都支持 `Grow(n)`。**[详细信息和比较](./references/containers.md)**

## 泛型集合（Go 1.18+）

使用最严格的约束。`comparable` 用于映射键，`cmp.Ordered` 用于排序，自定义接口用于特定领域排序。

```go
type Set[T comparable] map[T]struct{}

func (s Set[T]) Add(v T)          { s[v] = struct{}{} }
func (s Set[T]) Contains(v T) bool { _, ok := s[v]; return ok }
```

**[编写泛型数据结构](./references/generics.md)** — 使用 Go 1.18+ 泛型编写类型安全的容器，理解约束满足，以及构建特定领域泛型类型。

## 指针类型

| 类型        | 用途               | 零值     |
| ----------- | ------------------ | -------- |
| `*T`        | 普通间接引用，修改，可选值 | `nil`    |
| `unsafe.Pointer` | FFI，低级内存布局（仅 6 种规范模式） | `nil`    |
| `weak.Pointer[T]` (1.24+) | 缓存，规范化，弱引用 | N/A      |

**[指针类型深入](./references/pointers.md)** — 普通指针，`unsafe.Pointer`（6 种有效的规范模式），以及 `weak.Pointer[T]` 用于 GC 安全的缓存，不会阻止清理。

## 拷贝语义快速参考

| 类型        | 拷贝行为   | 独立性     |
| ----------- | ---------- | ---------- |
| `int`, `float`, `bool`, `string` | 值（深度拷贝） | 完全独立   |
| `array`, `struct` | 值（深度拷贝） | 完全独立   |
| `slice`     | 头拷贝，共享底层数组 | 使用 `slices.Clone` |
| `map`       | 引用拷贝   | 使用 `maps.Clone` |
| `channel`   | 引用拷贝   | 相同通道   |
| `*T` (指针) | 地址拷贝   | 相同底层值 |
| `interface` | 值拷贝（类型+值对） | 取决于所持类型 |

## 第三方库

用于标准库之外的复杂数据结构（树、集合、队列、栈）：

- **`emirpasic/gods`** — 全面集合库（树、集合、列表、栈、映射、队列）
- **`deckarep/golang-set`** — 线程安全和非线程安全的集合实现
- **`gammazero/deque`** — 快速双端队列

使用第三方库时，参考其官方文档和代码示例以获取当前 API 签名。

- 关于 Go 包文档、符号、版本、导入者和已知漏洞，→ 参考见 `samber/cc-skills-golang@golang-pkg-go-dev` 技能 (`godig`) —— 优先于 Context7 获取 Go 包事实。
- 用于在代码中导航本库的使用（定义、调用位置、诊断），→ 参考见 `samber/cc-skills-golang@golang-gopls` 技能 (`gopls`)。
- Context7 仍然是未在 pkg.go.dev 索引的文档的备用方案。

## 交叉引用

- → 参考见 `samber/cc-skills-golang@golang-performance` 技能了解结构字段对齐、内存布局优化和缓存局部性
- → 参考见 `samber/cc-skills-golang@golang-safety` 技能了解 nil 映射/切片陷阱、追加别名、防御性拷贝、`slices.Clone`/`Equal`
- → 参考见 `samber/cc-skills-golang@golang-concurrency` 技能了解通道、`sync.Map`、`sync.Pool` 和所有同步原语
- → 参考见 `samber/cc-skills-golang@golang-design-patterns` 技能了解 `string` vs `[]byte` vs `[]rune`，迭代器，流式处理
- → 参考见 `samber/cc-skills-golang@golang-structs-interfaces` 技能了解结构组合，嵌入，以及泛型 vs `any`
- → 参考见 `samber/cc-skills-golang@golang-code-style` 技能了解切片/映射初始化风格

## 常见错误

| 错误       | 修复方法     |
| ---------- | ------------ |
| 在循环中不预分配切片 | 每次增长都会拷贝整个底层数组——每次增长 O(n)。使用 `make([]T, 0, n)` 或 `slices.Grow` |
| 使用 `container/list` 而切片足够 | 链表缓存局部性差（每个节点是单独的堆分配）。先进行基准测试 |
| `bytes.Buffer` 用于纯字符串构建 | Buffer 的 `String()` 会拷贝底层字节。`strings.Builder` 避免这种拷贝 |
| `unsafe.Pointer` 跨语句存储为 `uintptr` | GC 可能在语句间移动对象——`uintptr` 成为悬空引用 |
| 映射中大型结构体值（拷贝开销） | 映射访问会拷贝整个值。使用 `map[K]*V` 用于大型值类型以避免拷贝 |

## 参考文献

- [Go 数据结构 (Russ Cox)](https://research.swtch.com/godata)
- [Go 内存模型](https://go.dev/ref/mem)
- [Effective Go](https://go.dev/doc/effective_go)
