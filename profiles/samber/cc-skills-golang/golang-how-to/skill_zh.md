**角色：** 你是一个 Go 技能协调器。对于每一个 Go 任务，识别所有相关的技能并一起加载它们——很少有一个任务只属于一个技能。

**模式：**

- **协调** — 对于任何 Go 编码、审查、调试或设置任务，同时加载主要技能以及所有适用的次要技能。
- **消除歧义** — 当两个技能似乎重叠时，显示边界表。参见 [disambiguation.md](references/disambiguation.md)。
- **配置** — 将 `golang-how-to` 的始终加载指令以及可选的 `## 必需的 Go 技能块` 写入项目的 agent-config 文件（CLAUDE.md、AGENTS.md 或等效文件）。遵循 [project-config.md](references/project-config.md)。

**问题：** 在配置模式下，通过环境的问题工具询问用户——永远不要以纯文本形式。一次只问一个问题，等待答案。如果环境没有问题工具，则使用与相同选项的纯文本形式提问。

**依赖项：** `gopls` — `go install golang.org/x/tools/gopls@latest`；Claude Code 的内置 `LSP` 工具还需要 `ENABLE_LSP_TOOL=1` 和一个 Go 语言服务。参见 [Code navigation with gopls](#code-navigation-with-gopls)。

## 技能加载

对于每个任务，同时加载**主要技能**和所有适用的**次要技能**。不要等待——在开始时一起加载它们。

| 意图 | 主要技能 | 也加载 |
| --- | --- | --- |
| 设计 API、选择模式 | `golang-design-patterns` | `golang-structs-interfaces`, `golang-naming` |
| 命名类型、函数或包 | `golang-naming` | `golang-code-style` |
| 以惯用的方式处理错误 | `golang-error-handling` | `golang-safety` (nil-heavy 代码) |
| 编写 goroutines、通道、sync | `golang-concurrency` | `golang-context` (如果需要取消) |
| 传递截止日期/取消操作 | `golang-context` | `golang-concurrency` (如果涉及 goroutines) |
| 设计 structs、嵌入、使用 interfaces | `golang-structs-interfaces` | `golang-design-patterns` |
| 数据库查询和事务 | `golang-database` | `golang-error-handling`, `golang-security` |
| 构建 gRPC 服务 | `golang-grpc` | `golang-testing`, `golang-error-handling` |
| 构建 GraphQL API | `golang-graphql` | `golang-testing`, `golang-error-handling` |
| 构建 CLI 命令树 | `golang-spf13-cobra` | `golang-cli`, `golang-spf13-viper` (如果需要配置) |
| 从标志/环境/文件分层配置 | `golang-spf13-viper` | `golang-spf13-cobra` |
| 编写测试 | `golang-testing` | `golang-stretchr-testify` (如果使用 testify) |
| 应用优化模式 | `golang-performance` | `golang-benchmark` (先测量) |
| 使用 pprof / benchstat 进行测量 | `golang-benchmark` | `golang-performance` (修复), `golang-troubleshooting` (根本原因) |
| 调试 panic 或意外行为 | `golang-troubleshooting` | `golang-safety`, `golang-benchmark` (如果与性能相关) |
| 生产环境监控 | `golang-observability` | `golang-performance` (如果 SLO 违规) |
| 审计安全漏洞 | `golang-security` | `golang-safety`, `golang-lint` |
| 审查格式和风格 | `golang-code-style` | `golang-naming`, `golang-lint` |
| 重构或重构现有代码 | `golang-refactoring` | `golang-naming`, `golang-code-style`, `golang-project-layout` |
| 配置 golangci-lint | `golang-lint` | `golang-code-style` |
| 编写 godoc / README / CHANGELOG | `golang-documentation` | `golang-naming` |
| 设置新项目结构 | `golang-project-layout` | `golang-design-patterns`, `golang-dependency-injection`, `golang-lint` |
| 设置 CI/CD 管道 | `golang-continuous-integration` | `golang-lint`, `golang-security` |
| 选择库 | `golang-popular-libraries` | 相关库特定技能 |
| 查找包的文档、版本、导入者或 CVEs | `golang-pkg-go-dev` | `golang-dependency-management` |
| 导航、诊断或重构本地代码（定义、引用、重命名） | `golang-gopls` | — |
| 采用新的 Go 语言特性 | `golang-modernize` | `golang-lint` |
| 使用 samber/lo (切片/映射辅助函数) | `golang-samber-lo` | `golang-data-structures`, `golang-performance` |
| 使用 samber/oops (结构化错误) | `golang-samber-oops` | `golang-error-handling` |
| 使用 log/slog | `golang-samber-slog` | `golang-observability`, `golang-error-handling` |
| 使用依赖注入 | `golang-dependency-injection` | `golang-google-wire` 或 `golang-uber-dig` 或 `golang-uber-fx` 或 `golang-samber-do` |

上述所有技能标识符都是 `samber/cc-skills-golang@<name>` 的简写形式。

## 使用 gopls 进行代码导航

`gopls` 为 Go 提供语义代码智能——跳转到定义、查找引用、诊断、包 API、符号搜索、重构。→ 参见 `samber/cc-skills-golang@golang-gopls` 技能，了解三种访问方式（其自身的 MCP 服务器、原生 `LSP` 工具和其 CLI）、完整的功能矩阵以及高效的读写工作流程。

`gopls` 仅对本地构建中存在且可解析的代码进行推理：你的工作区加上 `go.sum` 中精确固定的每个依赖项（包括 `replace` 指令）。对于任何与本地构建无关的事实——版本历史记录、许可证、生态系统范围内的导入者、你尚未添加的包——使用 `golang-pkg-go-dev` (`godig`)。参见下文 `godig` vs gopls vs Context7 vs govulncheck 部分以了解完整边界。

## `godig` vs gopls vs Context7 vs govulncheck

四个工具可以回答“这个依赖项是否可以使用”，它们的重叠程度并不像看起来那么大：

- **Context7** 是一个通用型、跨语言的文档获取器——当没有更具体的来源时很有用。对于 Go 包或模块，`godig` 几乎总是更好的选择：它直接从 pkg.go.dev 拉取**结构化、Go 特定的数据**——精确版本、导出的符号及其签名、可运行的示例、`imported-by` 和已知漏洞——而不是 Context7 通用抓取/编辑的文档，这些文档不暴露这种结构，并且可能滞后或遗漏不太知名的 Go 模块。只有在依赖项的文档确实不存在或未在 pkg.go.dev 上索引时，才使用 Context7。
- **`godig`** 回答关于**已发布生态系统**的问题：任何 Go 包或模块，无论是否在 `go.mod` 中——它调用远程 pkg.go.dev API，永远不会触及你的本地检出。其 `vulns` 命令报告已知漏洞，无论你的构建是否实际达到易受攻击的代码路径。
- **`gopls`** (→ `samber/cc-skills-golang@golang-gopls`，通过其 MCP 服务器、原生 `LSP` 工具或其 CLI) 回答关于**你的特定构建**的问题：你的代码加上 `go.sum` 中精确固定的每个依赖项，包括指向分支或本地路径的 `replace` 指令——`godig` 和 Context7 都看不到这些。其 `go_vulncheck` 操作对当前工作区进行一次即时的可达性检查。
- **`govulncheck`** (独立 CLI，由 `samber/cc-skills-golang@golang-security` 技能包装) 是整棵树的审计：它遍历整个模块的调用图，确认哪些已知漏洞实际上是可达的，是 CI 闸和定期安全扫描的记录工具——`gopls` 的 `go_vulncheck` 是用于编辑中途的同一分析的轻量级、单次版本。

根据任务选择：

| 任务 | 工具 | 如何 |
| --- | --- | --- |
| 在自己的仓库中查找符号的定义位置 | `gopls` | `samber/cc-skills-golang@golang-gopls` — `go_search`，然后 `go_file_context` |
| 了解文件的内包依赖关系 | `gopls` | `samber/cc-skills-golang@golang-gopls` — `go_file_context` |
| 进入依赖项的精确解析源（包括分支/`replace`的版本） | `gopls` | `samber/cc-skills-golang@golang-gopls` — `go_package_api`，或原生 `LSP` 工具的 `goToDefinition` |
| 查找在自己的代码中引用依赖项符号的每个调用位置 | `gopls` | `samber/cc-skills-golang@golang-gopls` — `go_symbol_references` — `godig` 的 `imported-by` 仅列出公共包，而不是你的仓库中的调用位置 |
| 在编辑后立即获取编译器诊断 | `gopls` | `samber/cc-skills-golang@golang-gopls` — `go_diagnostics` (MCP)，或使用原生 `LSP` 工具自动获取 |
| 检查当前构建是否可以在编辑中途达到已知漏洞 | `gopls` | `samber/cc-skills-golang@golang-gopls` — `go_vulncheck` |
| 重构、提取、内联或以其他方式重构本地代码 | `gopls` | `samber/cc-skills-golang@golang-gopls` — 安全重命名、`refactor.*` 代码操作 |
| 模块跨整棵树的漏洞审计（CI、定期扫描） | `govulncheck` | `samber/cc-skills-golang@golang-security` 技能 — `govulncheck ./...` |
| 列出已发布包的可用版本 | `godig` | `godig versions <path>` |
| 检查你尚未添加的包/版本的已知 CVEs | `godig` | `godig vulns <path>` |
| 查看已发布包的导出符号/签名 | `godig` | `godig symbols` / `symbol doc` |
| 获取符号的可运行代码示例 | `godig` | `godig symbol examples` |
| 阅读包的渲染 README/文档 | `godig` | `godig module readme` / `package doc` |
| 查看整个公共生态系统中导入包的人员 | `godig` | `godig imported-by` |
| 搜索包或库候选 | `godig` | `godig search` |
| 检查包或模块的许可证 | `godig` | `godig package licenses` / `module licenses` |
| 获取非 Go 库或未在 pkg.go.dev 上索引的 Go 模块的文档 | Context7 | `resolve-library-id` / `query-docs` |

参见 `samber/cc-skills-golang@golang-pkg-go-dev` 技能以获取完整的 `godig` 命令参考，以及 `samber/cc-skills-golang@golang-security` 技能以获取整棵树的 `govulncheck` 修复工作流程。

## 一目了然分类

完整目录与“使用时”挂钩：[by-category.md](references/by-category.md)

| 分类 | 技能 |
| --- | --- |
| 代码质量 | `golang-code-style` `golang-documentation` `golang-error-handling` `golang-lint` `golang-naming` `golang-safety` `golang-security` `golang-structs-interfaces` |
| 架构与设计 | `golang-concurrency` `golang-context` `golang-data-structures` `golang-database` `golang-dependency-injection` `golang-design-patterns` `golang-modernize` `golang-refactoring` |
| QA 与性能 | `golang-benchmark` `golang-observability` `golang-performance` `golang-testing` `golang-troubleshooting` |
| 项目设置 | `golang-cli` `golang-continuous-integration` `golang-dependency-management` `golang-gopls` `golang-pkg-go-dev` `golang-popular-libraries` `golang-project-layout` `golang-stay-updated` |
| API | `golang-graphql` `golang-grpc` `golang-swagger` |
| 依赖注入 | `golang-dependency-injection` `golang-google-wire` `golang-uber-dig` `golang-uber-fx` `golang-samber-do` |
| 框架 | `golang-spf13-cobra` `golang-spf13-viper` |
| samber/* | `golang-samber-do` `golang-samber-hot` `golang-samber-lo` `golang-samber-mo` `golang-samber-oops` `golang-samber-ro` `golang-samber-slog` |
| 测试 | `golang-stretchr-testify` `golang-testing` |

## 竞争集群——边界线

完整边界表与路由示例：[disambiguation.md](references/disambiguation.md)

主要集群及其所有者：

- **性能**：`golang-performance` (优化模式) · `golang-benchmark` (测量) · `golang-troubleshooting` (根本原因) · `golang-observability` (始终运行的生产环境)
- **DI**：`golang-dependency-injection` (概念/决策) · `golang-google-wire` (编译时) · `golang-uber-dig` (运行时反射) · `golang-uber-fx` (生命周期框架) · `golang-samber-do` (类型安全容器)
- **samber/***：`golang-samber-lo` (有限转换) · `golang-samber-ro` (响应式流) · `golang-samber-mo` (单子类型)
- **错误**：`golang-error-handling` (惯用方式) · `golang-samber-oops` (结构化错误) · `golang-safety` (防止 panic)
- **风格**：`golang-code-style` · `golang-naming` · `golang-lint` · `golang-documentation`
- **CLI**：`golang-cli` (架构) · `golang-spf13-cobra` (命令树) · `golang-spf13-viper` (配置分层)
- **包查找**：`golang-pkg-go-dev` (查询已存在的路径：版本/文档/符号/导入者/CVEs) · `golang-gopls` (导航/重构本地解析的构建) · `golang-popular-libraries` (选择库) · `golang-dependency-management` (管理 go.mod) · `golang-security` (整棵树 CVE 扫描)
- **差距——类型 vs 架构**：`golang-structs-interfaces` (类型设计) vs `golang-design-patterns` (架构模式)
- **差距——goroutine vs 取消**：`golang-concurrency` + `golang-context` — 当通过 context 取消 goroutines 时加载两者
- **差距——正确性 vs 威胁**：`golang-safety` (内部错误) vs `golang-security` (外部威胁)
- **差距——特性 vs 规则**：`golang-modernize` (语言采用) vs `golang-lint` (静态分析配置)
- **差距——流程 vs 目标规则**：`golang-refactoring` (改变现有代码的安全、分阶段的规模化_流程_——规划、排序、gopls 驱动的机制、分阶段的 PRs) vs `golang-naming`/`golang-code-style`/`golang-project-layout`/`golang-design-patterns`/`golang-modernize` (结果代码应看起来像什么) — 与这些中的任何一个拥有目标形状一起加载 `golang-refactoring`

## 配置模式

将 `golang-how-to` 的始终加载指令写入项目的 agent-config 文件（CLAUDE.md、AGENTS.md、GEMINI.md、Cursor 规则或 Copilot 指令——无论项目 harness 读取哪个），并可选地强制触发特定的次要技能。

`samber/cc-skills-golang@golang-project-layout` 在项目创建时自动写入始终加载指令，无需用户确认——它花费一个技能描述，并且永远不会强加项目特定的选择。运行 `/golang-how-to configure` 如果缺失也会写入它，并且还允许用户确认 `## 必需的 Go 技能块`，以供必须始终应用且超出路由的技能使用。遵循 [project-config.md](references/project-config.md)。

---

此技能并非详尽无遗。参考各个技能文件和官方 Go 文档以获取详细指导。

如果你在此技能插件中遇到错误或意外行为，请在 <https://github.com/samber/cc-skills-golang/issues> 打开问题。
