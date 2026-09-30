---
name: golang-gopls
description: 通过 `gopls` 实现的 Go 语义代码智能——官方 Go 语言服务器，支持跳转到定义、查找引用、调用/实现层级、工作区符号搜索、包 API 发现、诊断、安全重命名、重构（提取/内联/填充/重写代码操作）、格式化以及生成测试。可通过 `gopls` 自带的 MCP 服务器（`go_*` 工具）、Claude Code 的原生 `LSP` 工具或 `gopls` CLI 连接到代理。适用于导航或重构 Go 代码——跳转到定义、在重命名前查找调用位置、理解文件或包的依赖关系、编辑后运行诊断，或进行提取/内联/重命名。不适用于已发布的生态系统——不在你的 `go.mod` 中的包、版本、许可证、导入者——→参见 `samber/cc-skills-golang@golang-pkg-go-dev` 技能（`godig`）。不适用于全树漏洞审计→参见 `samber/cc-skills-golang@golang-security` 技能（`govulncheck`）。
---

**角色设定：** 你是一名 Go 工程师，每当问题涉及已解析的构建（resolved build）时，你都会优先使用语义化的代码智能工具，而不是 grep——grep 只能查找文本，`gopls` 能查找语义（类型、调用图、变量遮蔽、实现关系）。

**依赖项：** `gopls` —— 通过 `go install golang.org/x/tools/gopls@latest` 安装（v0.20+）。原生 `LSP` 工具还需要设置 `ENABLE_LSP_TOOL=1`，并安装来自 `gopls-lsp@claude-plugins-official` 市场的插件（参见 [references/mcp.md](references/mcp.md)）。

`gopls` 是官方的 Go 语言服务器。它只回答关于**你本地特定已解析构建**的问题——即你的工作区加上在 `go.sum` 中精确锁定的所有依赖项，包括 `replace` 指令。对于不属于该构建的包（你尚未添加的内容的版本、文档、许可证或 CVE），请参见 `samber/cc-skills-golang@golang-pkg-go-dev` 技能（`godig`）。

## 访问 gopls 的三种方式

它们并不完全等同——请根据你的已知信息和期望返回的内容来选择：

- **gopls 自带的 MCP 服务器（大多数任务的首选）**——专为智能体设计：工具使用名称、文件路径和模糊查询，而非原始光标位置。每台机器只需注册一次：`claude mcp add gopls -- gopls mcp`。它以无头模式通过 stdio 运行，不连接编辑器，只能看到已保存到磁盘的文件——这是仅由智能体工作流的正确默认设置。有关所有工具的详细信息，参见 [references/mcp.md](references/mcp.md)。
- **原生 `LSP` 工具**——Claude Code 内置的类编辑器集成。默认关闭：请设置 `ENABLE_LSP_TOOL=1`，安装 `gopls`，并安装官方 `gopls-lsp@claude-plugins-official` 市场插件，将其配置为 Go 语言服务器。操作（`goToDefinition`、`findReferences`、`hover`、`documentSymbol`、`workspaceSymbol`、`goToImplementation`、调用层级）以 `line`/`character` 为键，因此在你已经有位置信息时最为有用——通常是在执行 grep 或读取文件之后。独特价值：每次编辑后，编译器诊断信息会自动推送到上下文中，无需显式调用。
- **`gopls` CLI**——相同的引擎，以 `gopls <command> <file:line:col>` 方式调用。Go 团队将其文档标记为实验性和仅用于调试——“并不高效、完整、灵活，也不受官方支持”。当未配置 MCP 或原生工具时，或需要进行一次性脚本化检查时使用它。位置采用 `file:line:col`（从 1 开始，UTF-8 字节）或 `file:#offset`（从 0 开始）。参见 [references/cli.md](references/cli.md)。

**优先顺序：MCP → 原生 `LSP` → CLI。** MCP 工具符合智能体的思考方式（按名称/路径，而非光标位置）；原生工具免费提供自动诊断信息；CLI 是文档中记载的最后手段后备方案。配置尽可能多的可用方式，让任务选择工具——对于你已经有 `line:col` 的查询，通过 `LSP` 处理成本低；对于“X 在哪里”的查询，通过 `go_search` 处理成本低；对于快速的无人值守检查，通过 CLI 处理成本低。

## 能力 → CLI → MCP → 原生 LSP

所有能力与其 CLI 命令、MCP 工具及原生 `LSP` 操作的完整映射：[references/matrix.md](references/matrix.md)。

## 用例

- **导航**——在触碰非自己编写的代码之前，跳转到定义、实现或追踪调用图。详情：[references/features.md](references/features.md#navigation)。
- **代码发现**——了解工作区的结构（`go_workspace`），模糊搜索无法精确定位的符号（`go_search`），或在使用第三方依赖项前先查看其公共接口（`go_package_api`）。
- **文档**——悬停查看类型/文档/大小信息，调用函数时获取签名帮助，或浏览渲染后的包文档（`source.doc`，包括 pkg.go.dev 看不到的内部包）。
- **诊断与安全**——每次编辑后的编译器和分析器错误（`go_diagnostics` / 使用 `LSP` 时自动触发），以及轻量级的 `go_vulncheck` 可达性检查：在工作区检测到后立即运行一次作为基线，并在任何 `go.mod` 更改后再次运行。
- **格式化**——标准的 `gofmt` 等效格式化和导入组织，既可通过脚本运行，也可通过代码操作驱动。
- **重构**——安全重命名（阻止会破坏接口满足性的更改）、提取/内联，以及完整的 `refactor.rewrite.*` 系列（填充结构体/switch、反转 if、拆分/合并行、删除未使用的参数、添加结构体标签、实现接口）。包含陷阱的完整目录：[references/features.md](references/features.md#transformation)。

## 高效工作流

以下 Read/Edit 工作流编码了避免冗余查询和部分应用编辑的顺序——将每一步都视为必需项，而非可选项，即使是为了节省一轮交互也是如此。

- **会话开始**——调用一次 `go_workspace` 以检测这是否确实是 Go 工作区；如果是，立即接着运行一次基线 `go_vulncheck`，以揭示工作区已携带的漏洞。这是无条件执行的，与编辑工作流中在依赖项更改后进行的检查是分开的。

**读取工作流**（在触碰任何东西之前先理解）：

1. `go_workspace`——布局（模块/工作区/GOPATH）；如果尚未运行，则与上述会话开始检查使用相同的调用。
2. `go_search`——按名称模糊定位类型/函数/变量。
3. `go_file_context`——在首次读取任何 Go 文件后立即执行，查看它从包的其余部分引入了什么；如果该文件的依赖项发生变化，请重新运行。
4. `go_package_api`——查看第三方依赖项或同级包的公共接口，无需阅读每个文件。

**编辑工作流**（迭代直到诊断信息清晰）：

1. 先读取（上述工作流）。
2. 在修改任何定义之前运行 `go_symbol_references`——评估影响范围，然后阅读每个需要相应编辑的引用文件。
3. 在继续之前完成所有计划好的编辑，包括引用位置的编辑。
4. 对每个更改的文件运行 `go_diagnostics`——每次修改后都是强制性的，而非可选的清理步骤。
5. 修复报告的错误：在应用之前审阅任何建议的快速修复差异，然后重新运行诊断以确认修复已落地。忽略与任务无关的提示/信息级诊断。诊断信息可能是对周围源码的转述，而非逐字引用。
6. 仅当 `go.mod` 依赖项发生变化时，对整个工作区运行 `go_vulncheck`——在诊断信息清晰之后，而非之前。
7. 运行 `go test <changed-package-paths>`——除非明确要求，否则不要运行 `./...`，因为全仓库运行会减慢迭代循环。

**依赖结果前值得了解的陷阱：**

- `references` 结果仅反映**被查询文件的构建配置**——在 `foo_windows.go` 上的查询不会显示 `bar_linux.go` 中的匹配项；如果缺少跨平台结果，请在相关的 `GOOS`/构建标签下重新运行。
- `call_hierarchy` 仅显示**静态**调用——通过函数值或接口方法的调用对其不可见；当调用位置重要时，请用 `references` 进行佐证。
- 提取/内联重构不如重命名严谨：有时注释会被丢弃，标记为 `DO NOT EDIT` 的生成文件完全不会收到代码操作。
- `refactor.rewrite.fillStruct` 仅搜索光标上方的当前文件，并且需要已导入该结构体的包——如果类型是刚输入进去的，请先运行 `source.organizeImports`。

## gopls 与 godig、Context7 及 govulncheck 的比较

`gopls` 仅推理本地构建中现成且可解析的代码：

- 对于与该构建无关的任何内容（版本历史、许可证、生态系统范围内的导入者、尚未添加的包的 CVE）→ 参见 `samber/cc-skills-golang@golang-pkg-go-dev` 技能（`godig`）——它直接查询 pkg.go.dev，无需本地检出。
- 对于全面的、全树漏洞审计（CI 门禁、定期扫描），而非 gopls 的轻量级按需 `go_vulncheck` → 参见 `samber/cc-skills-golang@golang-security` 技能（`govulncheck`）。
- Context7 仍然是非 Go 文档或未在 pkg.go.dev 上索引的 Go 模块的后备方案。

完整的任务到工具矩阵位于 `samber/cc-skills-golang@golang-how-to` 技能的“`godig` vs gopls vs Context7 vs govulncheck”部分中。
