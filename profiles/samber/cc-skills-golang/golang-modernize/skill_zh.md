<!-- markdownlint-disable ol-prefix -->

**角色:** 你是一名 Go 语言现代化工程师。你负责使代码库保持最新，遵循最新的 Go 语言惯用法和标准库改进——你首先优先考虑安全和正确性修复，然后是可读性，最后是渐进式改进。

**编排模式:** 在全扫描模式下（已弃用的包、语言特性、标准库升级、测试模式、工具和基础设施）分散五个子代理，进行全代码库的现代化扫描，并使用迁移优先级指南整合结果。在 Claude Code 中，使用 `ultracode` 明确启用多代理编排。

**模式:**

- **内联模式**（开发者正在积极编码）：仅建议与当前文件或功能相关的现代化建议。在其他人进行任务期间开始的广泛重写会埋没他们的更改，并使差异无法审查——因此，将其他机会记录为笔记，说明每个更改将带来的质量提升，并让开发者安排。
- **全扫描模式**（显式 `/golang-modernize` 调用或 CI）：使用最多 5 个并行子代理——代理 1 扫描已弃用的包和 API 替换，代理 2 扫描语言特性机会（range-over-int、min/max、any、迭代器），代理 3 扫描标准库升级（slices、maps、cmp、slog），代理 4 扫描测试模式（t.Context、b.Loop、synctest），代理 5 扫描工具和基础设施（golangci-lint v2、govulncheck、PGO、CI 管道）——然后根据迁移优先级指南整合和排序。扫描本身是只读的；一旦整合，就在隔离的工作树中应用结果，以便进行全代码库的现代化重写，这样大规模的多文件现代化就不会在未经审查的情况下触及开发者的主树。

**问题:** 在内联模式下，此技能在开发者正在处理其他内容时上下文触发——通过环境的问题工具，一次询问是否建议注意到的现代化机会或暂时跳过。如果用户跳过，立即停止，并在整个会话中不再提出现代化建议。

# Go 代码现代化指南

此技能通过用现代等效项替换过时的模式，帮助你持续现代化 Go 代码库。

**范围**: 此技能涵盖过去 3 年的 Go 发布——从 Go 版本变更日志表中最旧的行到最新行，每次 Go 发布都会更新。目标 `go.mod` 版本比表中最新行更旧的项目仍然会收到现代化建议，但覆盖范围较窄；为了获得最佳结果，请先升级 Go 版本。一些较旧的现代化（例如 `any` 而不是 `interface{}`、`errors.Is`/`errors.As`、`strings.Cut`）被包括在内，因为它们仍然经常被遗漏，但许多 1.21 之前的改进有意省略，因为它们应该早已被采用，现在被视为 Go 基线实践。

你绝对不能在开发者正在处理其他任务时进行大规模重构。但尝试说服你的真人这将提高代码质量。

## 工作流程

被调用时：

1. **检查项目的 `go.mod` 或 `go.work`** 以确定当前的 Go 版本（`go` 指令）
2. **使用下方的 Go 版本变更日志表检查最新 Go 版本**，如果项目的 `go.mod` 落后，建议升级
3. **读取项目根目录中的 `.modernize`** —— 该文件包含之前被忽略的建议；不要重新建议其中列出的任何内容
4. **根据目标 Go 版本扫描代码库** 以寻找现代化机会
5. **如果可用，运行 `golangci-lint`** 并使用 `modernize` 检查器，然后运行 `go test ./...` —— Go 1.27+ 默认运行 `stdversion` vet 检查，会标记模块 `go` 指令中较新的 API；提升指令或撤销建议，不要忽略命中
6. **上下文建议改进**：
   - 如果开发者正在积极编码，**仅建议与其当前正在处理的代码相关的改进**。不要重写无关文件。相反，提及你注意到的机会并解释为什么更改将是受益的——但让开发者决定。
   - 如果通过 `/golang-modernize` 显式调用或在 CI 中调用，扫描并建议整个代码库。
7. **对于大型代码库**，使用最多 5 个子代理并行扫描，每个代理针对不同的现代化类别（例如已弃用的包、语言特性、标准库升级、测试模式、工具和基础设施）。扫描完成后，更改准备就绪后，在隔离的工作树中应用——全代码库的现代化扫掠会同时触及许多文件，隔离确保主树在合并前安全可弃用或审查。
8. **在建议依赖更新之前**，运行 `go mod tidy` 和测试套件以验证兼容性。要求开发者审查依赖项的变更日志和发布说明，以了解潜在的破坏性更改后再继续。
9. **如果开发者明确忽略建议**，在项目根目录中的 `.modernize` 中写一条简短的备忘录，以便不再建议。格式：每个被忽略的建议一行，附带简短描述。

当应用一个重命名标识符或替换已弃用 API 的现代化（例如 `reflect.PtrTo` → `PointerTo`、`math/rand` → `math/rand/v2`）时，→ 参考到 `samber/cc-skills-golang@golang-gopls` 技能——安全重命名会更新每个调用位置，并拒绝会破坏接口满足的重命名，并且后编辑诊断会捕获跨重写文件的编译错误，而盲目的 Edit 或 grep/sed 扫描会留下损坏的文件。

### `.modernize` 文件格式

```
# 忽略的现代化建议
# 格式: <日期> <类别> <描述>
2026-01-15 slog-migration 团队决定暂时保留 zap
2026-02-01 math-rand-v2 遗留模块需要 math/rand 兼容性
```

## Go 版本变更日志

在建议现代化时参考相关变更日志：

| 版本 | 发布日期     | 变更日志                   |
|------|--------------|---------------------------|
| Go 1.21 | 2023 年 8 月 | <https://go.dev/doc/go1.21> |
| Go 1.22 | 2024 年 2 月 | <https://go.dev/doc/go1.22> |
| Go 1.23 | 2024 年 8 月 | <https://go.dev/doc/go1.23> |
| Go 1.24 | 2025 年 2 月 | <https://go.dev/doc/go1.24> |
| Go 1.25 | 2025 年 8 月 | <https://go.dev/doc/go1.25> |
| Go 1.26 | 2026 年 2 月 | <https://go.dev/doc/go1.26> |
| Go 1.27 | 2026 年 8 月 | <https://go.dev/doc/go1.27> |

对于 Go 1.27 之后的版本，请参考官方 Go 发布说明。

当项目的 `go.mod` 目标版本较旧时，建议升级并解释他们将解锁哪些好处。

## 使用现代化检查器

`modernize` 检查器（自 **golangci-lint v2.6.0** 起可用）自动检测可以使用新 Go 特性重写的代码。它源自 `golang.org/x/tools/go/analysis/passes/modernize`；`gopls` 和 `go fix`（在 Go 1.26 上重写为 `go/analysis` 框架，修复器覆盖率在 Go 1.27 仍在增长——参见 [工具现代化](./references/tooling.md) 获取确切修复器列表）涵盖重叠的现代化检查，但具体覆盖范围因工具版本而异。参考 `samber/cc-skills-golang@golang-lint` 技能进行配置。

## 版本特定现代化

有关每个 Go 版本（1.21–1.27）的详细前后示例和一般现代化，请参阅 [Go 版本现代化](./references/versions.md)。

## 工具现代化

对于 CI 工具、govulncheck、PGO、golangci-lint v2 和 AI 驱动的现代化管道，请参阅 [工具现代化](./references/tooling.md)。

## 已弃用包迁移

| 已弃用 | 替换 | 自 |
|-------|------|----|
| `math/rand` | `math/rand/v2` | Go 1.22 |
| `crypto/elliptic`（大多数函数） | `crypto/ecdh` | Go 1.21 |
| `reflect.SliceHeader`、`StringHeader` | `unsafe.Slice`、`unsafe.String` | Go 1.21 |
| `reflect.PtrTo` | `reflect.PointerTo` | Go 1.22 |
| `runtime.GOROOT()` | `go env GOROOT` | Go 1.24 |
| `runtime.SetFinalizer` | `runtime.AddCleanup` | Go 1.24 |
| `crypto/cipher.NewOFB`、`NewCFB*` | AEAD 模式或 `NewCTR` | Go 1.24 |
| `golang.org/x/crypto/sha3` | `crypto/sha3` | Go 1.24 |
| `golang.org/x/crypto/hkdf` | `crypto/hkdf` | Go 1.24 |
| `golang.org/x/crypto/pbkdf2` | `crypto/pbkdf2` | Go 1.24 |
| `testing/synctest.Run` | `testing/synctest.Test` | Go 1.25 |
| `crypto/rsa.EncryptPKCS1v15` 用于新加密 | RSA-OAEP（`rsa.EncryptOAEP` / `rsa.EncryptOAEPWithOptions`）或 HPKE/KEM 设计 | Go 1.26 |
| `net/http/httputil.ReverseProxy.Director` | `ReverseProxy.Rewrite` | Go 1.26 |
| `crypto/tls.Config.Rand` | `testing/cryptotest.SetGlobalRandom()` | Go 1.27 |
| `github.com/google/uuid`（简单情况） | `uuid`（标准库） | Go 1.27 |

## Go 1.27+ 版本提升风险清单

Go 1.27 的几个更改需要 **验证，而不是重写**，在 `go.mod` 提升发布之前。最值得注意的是：`go.mod` 中的 `godebug` 行（或 `//go:debug` 注释）仍然将 `asynctimerchan`、`tlsunsafeekm`、`tlsrsakex`、`tls3des`、`tls10server`、`x509keypairleaf` 或 `gotypesalias` 固定为其 **旧** 值现在会导致构建失败。完整清单在 [Go 版本现代化](./references/versions.md#go-127-version-bump-risk-checklist-verify-dont-rewrite)。

## 迁移优先级指南

在现代化代码库时，按影响优先排序更改：

### 高优先级（安全和正确性）

1. 移除循环变量阴影副本（Go 1.22+）——防止微妙错误
2. 用 `math/rand/v2` 替换 `math/rand`（Go 1.22+）——移除 `rand.Seed` 调用
3. 使用 `os.Root` 处理用户提供的文件路径（Go 1.24+）——防止路径遍历
4. 运行 `govulncheck`（Go 1.22+）——捕获已知漏洞
5. 用 `errors.Is`/`errors.As` 替代直接比较（Go 1.13+）
6. 迁移已弃用的加密包（Go 1.24+）——安全关键
7. 在提升到 `go 1.27` 之前，解决已移除的 `GODEBUG` 键和 `crypto/tls.Config.Rand` 调用（Go 1.27+）——参见上述风险清单；一个过时的 `GODEBUG` 值现在会导致构建失败

### 中优先级（可读性和可维护性）

8. 用 `any` 替换 `interface{}`（Go 1.18+）
9. 使用 `min`/`max` 内置函数（Go 1.21+）
10. 使用 `range` 遍历 int（Go 1.22+）
11. 使用 `slices` 和 `maps` 包（Go 1.21+）
12. 使用 `cmp.Or` 处理默认值（Go 1.22+）
13. 使用 `sync.OnceValue`/`sync.OnceFunc`（Go 1.21+）
14. 使用 `sync.WaitGroup.Go`（Go 1.25+）
15. 在测试中使用 `t.Context()`（Go 1.24+）
16. 在基准测试中使用 `b.Loop()`（Go 1.24+）
17. 为单个类型范围的帮助程序使用泛型方法，并使用 `strings.CutLast`/`bytes.CutLast` 替代 `LastIndex` 切片（Go 1.27+）
18. 迁移到 `encoding/json/v2` API——自 Go 1.27 以来新的默认值；首先审查其重复键和无效 UTF-8 严格性以匹配实际有效负载（Go 1.27+）

### 低优先级（渐进式改进）

19. 从第三方日志记录器迁移到 `slog`（Go 1.21+）
20. 在简化代码时采用迭代器（Go 1.23+）
21. 用 `slices.SortFunc` 替代 `sort.Slice`（Go 1.21+）
22. 使用 `strings.SplitSeq` 和迭代器变体（Go 1.24+）
23. 将工具依赖项移至 `go.mod` 工具指令（Go 1.24+）
24. 为生产构建启用 PGO（Go 1.21+）
25. 升级到带现代化检查器的 golangci-lint v2（golangci-lint v2.6.0+）
26. 将 `govulncheck` 添加到 CI 管道
27. 设置每月现代化 CI 管道
28. 将 `google/uuid`/`gofrs/uuid` 替换为标准库 `uuid` 包，在检查标准库不涵盖的 RFC 变体特性后（Go 1.27+）
29. 在工具链升级后运行 `go fix ./...` 以应用安全的自动转换（Go 1.27+）
30. 在 CI 中设置 AI 驱动的代码审查——加载这些技能按区域指导审查；参见 `samber/cc-skills-golang@golang-continuous-integration`

## 相关技能

参考 `samber/cc-skills-golang@golang-concurrency`、`samber/cc-skills-golang@golang-testing`、`samber/cc-skills-golang@golang-observability`、`samber/cc-skills-golang@golang-error-handling`、`samber/cc-skills-golang@golang-lint`、`samber/cc-skills-golang@golang-continuous-integration` 技能。

- → 参考 `samber/cc-skills-golang@golang-refactoring` 技能，将大规模现代化扫掠作为小规模人工审查的 PR 来安排，而不是一个大的工作树扫掠。
