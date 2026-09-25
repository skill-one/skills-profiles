**角色设定：** 你是一位 Go 工程师，更倾向于使用声明式集合转换而非手动循环。你习惯使用 `lo` 来消除样板代码，但也知道何时 stdlib 足够，何时需要升级到 `lop`、`lom` 或 `loi`。

# samber/lo — Go 语言的函数式工具库

受 Lodash 启发，以泛型优先的实用工具库，为切片、映射、字符串、数学、通道、元组、并发提供 500 多种类型安全的辅助函数。零外部依赖。默认不可变。

**官方资源：**

- [github.com/samber/lo](https://github.com/samber/lo)
- [lo.samber.dev](https://lo.samber.dev)
- [pkg.go.dev/github.com/samber/lo](https://pkg.go.dev/github.com/samber/lo)

这项技能并不详尽——请参考库文档和代码示例获取更多信息：

- 对于 Go 包文档、符号、版本、导入者和已知漏洞，→ 查看 `samber/cc-skills-golang@golang-pkg-go-dev` 技能（`godig`），优先于 Context7 获取 Go 包信息。
- 要在您的代码中导航此库的使用（定义、调用位置、诊断），→ 查看 `samber/cc-skills-golang@golang-gopls` 技能（`gopls`）。
- Context7 仍然是未在 pkg.go.dev 索引的文档的备用方案。

## 为什么选择 samber/lo

Go 的 stdlib `slices` 和 `maps` 包包含约 10 个基本辅助函数（排序、包含、键）。其他所有功能——映射、过滤、归约、分组、分块、展平、压缩——都需要手动 for 循环。`lo` 弥补了这一空白：

- **类型安全的泛型** — 无 `interface{}` 转换，无反射，编译时检查，无接口装箱开销
- **默认不可变** — 返回新的集合，适合并发读取，更易于推理
- **可组合** — 函数接受并返回切片/映射，因此可以无包装类型地链式调用
- **零依赖** — 仅 Go stdlib，无传递依赖风险
- **渐进式复杂度** — 先从 `lo` 开始，仅在性能分析要求时升级到 `lop`/`lom`/`loi`
- **错误变体** — 大多数函数都有 `Err` 后缀（`MapErr`、`FilterErr`、`ReduceErr`），在第一个错误时停止

## 安装

```bash
go get github.com/samber/lo
```

| 包 | 导入 | 别名 | Go 版本 |
| --- | --- | --- | --- |
| 核心（不可变） | `github.com/samber/lo` | `lo` | 1.18+ |
| 并行 | `github.com/samber/lo/parallel` | `lop` | 1.18+ |
| 可变 | `github.com/samber/lo/mutable` | `lom` | 1.18+ |
| 迭代器 | `github.com/samber/lo/it` | `loi` | 1.23+ |
| SIMD（实验性） | `github.com/samber/lo/exp/simd` | — | 1.25+（仅 amd64） |

## 选择合适的包

从 `lo` 开始。仅在性能分析显示瓶颈或明确需要惰性求值时才迁移到其他包。

| 包 | 使用场景 | 代价 |
| --- | --- | --- |
| `lo` | 所有转换的默认选择 | 分配新的集合（安全、可预测） |
| `lop` | 大数据集（1000+ 项）上的 CPU 密集型工作 | Goroutine 开销；不适用于 I/O 或小切片 |
| `lom` | `pprof -alloc_objects` 确认的热路径 | 修改输入——调用者必须理解副作用 |
| `loi` | Go 1.23+ 的大型数据集上的链式转换 | 惰性求值节省内存，但增加了迭代器复杂性 |
| `simd` | 基于基准测试的数值批量操作（实验性） | 不稳定 API，可能在版本之间中断 |

**关键规则：**

- `lop` 用于 CPU 并行，而非 I/O 并发——对于 I/O 分发，使用 `errgroup` 而不是
- `lom` 破坏不可变性——仅在测量分配压力时使用，绝不能假设
- `loi` 通过惰性求值消除链式转换（如 `Map → Filter → Take`）中的中间分配
- 对于无限事件流上的响应式/流式管道，→ 查看 `samber/cc-skills-golang@golang-samber-ro` 技能 + `samber/ro` 包

有关详细包比较和决策流程图，请参阅 [包指南](./references/package-guide.md)。

## 核心模式

### 转换切片

```go
// ✓ lo — 声明式，类型安全
names := lo.Map(users, func(u User, _ int) string {
    return u.Name
})

// ✗ 手动 — 存在样板代码，易出错
names := make([]string, 0, len(users))
for _, u := range users {
    names = append(names, u.Name)
}
```

### 过滤 + 归约

```go
total := lo.Reduce(
    lo.Filter(orders, func(o Order, _ int) bool {
        return o.Status == "paid"
    }),
    func(sum float64, o Order, _ int) float64 {
        return sum + o.Amount
    },
    0,
)
```

### 分组

```go
byStatus := lo.GroupBy(tasks, func(t Task, _ int) string {
    return t.Status
})
// map[string][]Task{"open": [...], "closed": [...]}
```

### 错误变体——第一个错误即停止

```go
results, err := lo.MapErr(urls, func(url string, _ int) (Response, error) {
    return http.Get(url)
})
```

## 常见错误

| 错误 | 为什么失败 | 修复 |
| --- | --- | --- |
| 使用 `lo.Contains` 而存在 `slices.Contains` | 对于 stdlib 覆盖的操作，无需额外依赖 | 优先使用 `slices.Contains`/`slices.Sort`（Go 1.21+）和 `slices.Collect(maps.Keys(m))`（Go 1.23+） |
| 在 10 项上使用 `lop.Map` | Goroutine 创建开销超过转换成本 | 使用 `lo.Map`——`lop` 的优势始于 CPU 密集型工作约 1000+ 项 |
| 假设 `lo.Filter` 修改输入 | `lo` 默认不可变——它返回一个新的切片 | 如果需要原地突变，使用 `lom.Filter` |
| 在生产代码路径中使用 `lo.Must` | `Must` 在出错时恐慌——适用于测试和 init，请求处理程序中危险 | 使用非 `Must` 变体并处理错误 |
| 在大型数据上链式许多急切转换 | 每一步分配一个中间切片 | 使用 `loi`（惰性迭代器）避免中间分配 |

## 最佳实践

1. **优先使用 stdlib** — `slices.Contains` 和 `slices.Sort`（Go 1.21+）无依赖；`maps.Keys` 是 Go 1.23+ 并返回迭代器，因此当您需要切片时使用 `slices.Collect(maps.Keys(m))`。使用 `lo` 进行 stdlib 未提供的转换（映射、过滤、归约、分组、分块、展平）
2. **组合 `lo` 函数** — 链式 `lo.Filter` → `lo.Map` → `lo.GroupBy` 而非编写嵌套循环。每个函数都是一个构建块
3. **优化前进行性能分析** — 仅在 `go tool pprof` 确认分配或 CPU 为瓶颈时，从 `lo` 切换到 `lom`/`lop`
4. **使用错误变体** — 优先使用 `lo.MapErr` 而非 `lo.Map` + 手动错误收集。错误变体提前停止并清晰传播
5. **仅在测试和 init 中使用 `lo.Must`** — 生产中显式处理错误

## 快速参考

| 函数 | 它的作用 |
| --- | --- |
| `lo.Map` | 转换每个元素 |
| `lo.Filter` / `lo.Reject` | 保留/移除匹配谓词的元素 |
| `lo.Reduce` | 归约元素为单个值 |
| `lo.ForEach` | 副作用迭代 |
| `lo.GroupBy` | 按键分组元素 |
| `lo.Chunk` | 分割为固定大小的批次 |
| `lo.Flatten` | 展平嵌套切片一层 |
| `lo.Uniq` / `lo.UniqBy` | 移除重复项 |
| `lo.Find` / `lo.FindOrElse` | 第一个匹配或默认值 |
| `lo.Contains` / `lo.Every` / `lo.Some` | 成员资格测试 |
| `lo.Keys` / `lo.Values` | 提取映射键或值 |
| `lo.PickBy` / `lo.OmitBy` | 过滤映射条目 |
| `lo.Zip2` / `lo.Unzip2` | 配对/解配对两个切片 |
| `lo.Range` / `lo.RangeFrom` | 生成数字序列 |
| `lo.Ternary` / `lo.If` | 内联条件 |
| `lo.ToPtr` / `lo.FromPtr` | 指针辅助 |
| `lo.Must` / `lo.Try` | 恐慌出错/恢复为布尔值 |
| `lo.Async` / `lo.Attempt` | 异步执行/带退避重试 |
| `lo.Debounce` / `lo.Throttle` | 速率限制 |
| `lo.ChannelDispatcher` | 分发到多个通道 |

有关完整函数目录（300+ 函数），请参阅 [API 参考](./references/api-reference.md)。

有关组合模式、stdlib 互操作性和迭代器管道，请参阅 [高级模式](./references/advanced-patterns.md)。

如果您在 samber/lo 中遇到错误或意外行为，请在新问题中打开 [github.com/samber/lo/issues](https://github.com/samber/lo/issues)。

## 交叉引用

- → 查看 `samber/cc-skills-golang@golang-samber-ro` 技能，用于无限事件流上的响应式/流式管道（`samber/ro` 包）
- → 查看 `samber/cc-skills-golang@golang-samber-mo` 技能，用于与 `lo` 转换组合的 monadic 类型（Option、Result、Either）
- → 查看 `samber/cc-skills-golang@golang-data-structures` 技能，用于选择合适的底层数据结构
- → 查看 `samber/cc-skills-golang@golang-performance` 技能，用于在切换到 `lom`/`lop` 之前进行性能分析
