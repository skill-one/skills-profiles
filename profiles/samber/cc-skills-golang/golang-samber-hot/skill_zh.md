**角色设定：** 你是一位将缓存视为系统设计决策的 Go 工程师。你根据测量的访问模式选择驱逐算法，根据工作集数据设置缓存大小，并始终为过期、加载器故障和监控进行规划。

# 在 Go 中使用 samber/hot 进行内存缓存

适用于 Go 1.22+ 的通用、类型安全的内存缓存库，具有 9 种驱逐算法、TTL、带 singleflight 去重的加载器链、分片、陈旧验证（stale-while-revalidate）和 Prometheus 指标。

**官方资源：**

- [pkg.go.dev/github.com/samber/hot](https://pkg.go.dev/github.com/samber/hot)
- [github.com/samber/hot](https://github.com/samber/hot)

这项技能并不详尽——请参考库文档和代码示例获取更多信息：

- 对于 Go 包文档、符号、版本、导入者和已知漏洞，→ 查看 `samber/cc-skills-golang@golang-pkg-go-dev` 技能（`godig`），优先于 Context7 用于 Go 包事实。
- 要导航此库在你的代码中的使用（定义、调用位置、诊断），→ 查看 `samber/cc-skills-golang@golang-gopls` 技能（`gopls`）。
- Context7 仍然是未在 pkg.go.dev 索引的文档的备用方案。

```bash
go get -u github.com/samber/hot
```

## 算法选择

根据你的访问模式进行选择——错误的算法会浪费内存或降低命中率。

| 算法 | 常量 | 适用于 | 避免 |
| --- | --- | --- | --- |
| **W-TinyLFU** | `hot.WTinyLFU` | 通用，混合工作负载（默认） | 你需要为调试的简单性 |
| **LRU** | `hot.LRU` | 以近期为主导（会话、最近查询） | 频率重要（扫描污染会驱逐热项） |
| **LFU** | `hot.LFU` | 以频率为主导（热门产品、DNS） | 访问模式变化（陈旧的热项永远不会驱逐） |
| **TinyLFU** | `hot.TinyLFU` | 读取密集且频率偏向 | 写入密集（准入过滤器开销） |
| **S3FIFO** | `hot.S3FIFO` | 高吞吐量，抗扫描 | 小型缓存（<1000 项） |
| **ARC** | `hot.ARC` | 自适应调整，未知模式 | 内存受限（2 倍跟踪开销） |
| **TwoQueue** | `hot.TwoQueue` | 混合带热/冷分离 | 调整复杂性不可接受 |
| **SIEVE** | `hot.SIEVE` | 简单抗扫描 LRU 替代方案 | 高度倾斜的访问模式 |
| **FIFO** | `hot.FIFO` | 简单，可预测的驱逐顺序 | 命中率重要（无频率/近期意识） |

**决策捷径：** 从 `hot.WTinyLFU` 开始。仅在分析显示你的 SLO 的错失率过高时才切换。

有关详细算法比较、基准测试和决策树，请参阅 [算法指南](./references/algorithm-guide.md)。

## 核心用法

### 带有 TTL 的基本缓存

```go
import "github.com/samber/hot"

cache := hot.NewHotCache[string, *User](hot.WTinyLFU, 10_000).
    WithTTL(5 * time.Minute).
    WithJanitor().
    Build()
defer cache.StopJanitor()

cache.Set("user:123", user)
cache.SetWithTTL("session:abc", session, 30*time.Minute)

value, found, err := cache.Get("user:123")
```

### 加载器模式（读通）

加载器会自动获取缺失的键，并使用 singleflight 去重——对相同缺失键的并发 `Get()` 调用共享一个加载器调用：

```go
cache := hot.NewHotCache[int, *User](hot.WTinyLFU, 10_000).
    WithTTL(5 * time.Minute).
    WithLoaders(func(ids []int) (map[int]*User, error) {
        return db.GetUsersByIDs(ctx, ids) // 批量查询
    }).
    WithJanitor().
    Build()
defer cache.StopJanitor()

user, found, err := cache.Get(123) // 错失时触发加载器
```

## 容量调整

在设置缓存容量之前，估计内存预算中可以容纳多少项：

1. **估计单项大小**——估计结构体的大小，加上堆分配字段（切片、映射、字符串）的大小。包括键的大小。每项约 100 字节的粗略开销涵盖内部记账（指针、过期时间戳、算法元数据）。
2. **询问开发者**此缓存在生产中分配了多少内存（例如，256 MB、1 GB）。这取决于服务的总内存以及什么与其他进程共享。
3. **计算容量**——`capacity = memoryBudget / estimatedItemSize`。向下取整以留出余量。

```
示例：*User 结构体 ~500 字节 + 字符串键 ~50 字节 + 开销 ~100 字节 = ~650 字节/项
         256 MB 预算 → 256_000_000 / 650 ≈ 393,000 项
```

如果项大小未知，请要求开发者使用分配 N 项并检查 `runtime.ReadMemStats` 的单元测试来测量它。未测量就猜测容量会导致 OOM 或浪费内存。

## 常见错误

1. **忘记 `WithJanitor()`**——没有它，过期条目会保留在内存中，直到算法驱逐它们。始终在构建器中链式调用 `.WithJanitor()` 并 `defer cache.StopJanitor()`。
2. **未配置缺失缓存的情况下调用 `SetMissing()`**——运行时会触发恐慌。首先在构建器中启用 `WithMissingCache(algorithm, capacity)` 或 `WithMissingSharedCache()`。
3. **`WithoutLocking()` + `WithJanitor()`**——互斥，会触发恐慌。`WithoutLocking()` 仅适用于无后台清理的单 goroutine 访问。
4. **过大的缓存**——持有所有内容的缓存是一个具有开销的映射。调整为你的工作集（通常是总数据的 10-20%）。监控命中率以验证。
5. **忽略加载器错误**——`Get()` 在加载器失败时返回 `(零, false, err)`。始终检查 `err`，而不仅仅是 `found`。

## 最佳实践

1. 始终设置 TTL——无限制的缓存会无限期地提供陈旧数据，因为没有刷新信号
2. 使用 `WithJitter(lambda, upperBound)` 来分散过期时间——没有抖动，同时创建的项会同时过期，导致加载器上的雷声效应
3. 使用 `WithPrometheusMetrics(cacheName)` 进行监控——命中率低于 80% 通常意味着缓存太小或算法不适合工作负载
4. 使用 `WithCopyOnRead(fn)` / `WithCopyOnWrite(fn)` 处理可变值——没有副本，调用者会修改缓存的对象并破坏共享状态

有关高级模式（重新验证、分片、缺失缓存、监控设置），请参阅 [生产模式](./references/production-patterns.md)。

有关完整的 API 表面，请参阅 [API 参考](./references/api-reference.md)。

如果你在 samber/hot 中遇到 bug 或意外行为，请 <https://github.com/samber/hot/issues> 打开问题。

## 交叉引用

- → 查看 `samber/cc-skills-golang@golang-performance` 技能以了解通用缓存策略和何时使用内存缓存 vs Redis vs CDN
- → 查看 `samber/cc-skills-golang@golang-observability` 技能以了解 Prometheus 指标集成和监控
- → 查看 `samber/cc-skills-golang@golang-database` 技能以了解与缓存加载器配对的数据库查询模式
- → 查看 `samber/cc-skills@promql-cli` 技能以通过 CLI 查询 Prometheus 缓存指标
