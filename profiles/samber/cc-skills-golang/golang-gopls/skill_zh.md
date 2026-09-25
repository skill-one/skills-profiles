**角色：** 你是一位 Go 工程师，当遇到关于已解析构建的问题时，你会优先使用语义代码智能工具（如 `gopls`）而不是 `grep`。`grep` 仅用于查找文本，而 `gopls` 能够理解代码含义（类型、调用图、遮蔽关系、实现关系）。

**依赖项：** `gopls` — `go install golang.org/x/tools/gopls@latest` (v0.20+)。原生 `LSP` 工具还需要设置 `ENABLE_LSP_TOOL=1` 并安装 `gopls-lsp@claude-plugins-official` 市场插件（参见 [references/mcp.md](references/mcp.md)）。

`gopls` 是 Go 语言的官方语言服务器。它仅回答关于**你特定本地已解析构建**的问题——即你的工作区以及 `go.sum` 中精确指定的所有依赖项，包括 `replace` 指令。对于不属于该构建的包（如版本历史、文档、许可证、你尚未添加的 CVE），→ 参见 `samber/cc-skills-golang@golang-pkg-go-dev` 技能 (`godig`)。

## 连接 `gopls` 的三种方法

不可互换——根据你已有的知识和需要返回的内容进行选择：

- **`gopls` 自带的 MCP 服务器（大多数任务的首选）** — 为代理专门设计：工具接收名称、文件路径和模糊查询，而不是原始光标位置。每台机器注册一次：`claude mcp add gopls -- gopls mcp`。以无头模式运行，通过 stdio，不连接编辑器，仅看到磁盘上保存的文件——这是纯代理工作流程的正确默认设置。有关每个工具的详细信息，参见 [references/mcp.md](references/mcp.md)。
- **原生 `LSP` 工具** — Claude Code 的内置编辑器式集成。默认关闭：设置 `ENABLE_LSP_TOOL=1`，安装 `gopls`，并安装官方的 `gopls-lsp@claude-plugins-official` 市场插件，将其配置为 Go 语言服务器。操作 (`goToDefinition`、`findReferences`、`hover`、`documentSymbol`、`workspaceSymbol`、`goToImplementation`、调用层次结构) 以 `line`/`character` 为键，因此在你已经有一个位置时最有用——通常是在 `grep` 或读取之后。独特价值：编译器诊断在每次编辑后自动推入上下文，无需显式调用。
- **`gopls` 命令行界面** — 相同的引擎，以 `gopls <command> <file:line:col>` 的方式调用。Go 团队将其记录为实验性和仅用于调试的——"效率不高、不完整、不灵活或不官方支持。" 在 MCP 或原生工具未配置时，或用于一次性脚本检查时使用。位置是 `file:line:col`（1 索引，UTF-8 字节）或 `file:#offset`（0 索引）。参见 [references/cli.md](references/cli.md)。

**优先顺序：MCP → 原生 `LSP` → CLI。** MCP 工具匹配代理的思维方式（通过名称/路径，而不是光标位置）；原生工具添加了自动诊断；CLI 是最后的选择性回退。配置尽可能多的工具，让任务选择工具——对于已有 `line:col` 的查询，通过 `LSP` 很高效；"X 在哪里"的查询通过 `go_search` 很高效；快速无人值守检查通过 CLI 很高效。

## 能力 → CLI → MCP → 原生 LSP

每个能力到其 CLI 命令、MCP 工具和原生 `LSP` 操作的完整映射：[references/matrix.md](references/matrix.md)。

## 用例

- **导航** — 在修改你未编写的代码之前，跳转到定义、实现或跟踪调用图。详情：[references/features.md](references/features.md#navigation)。
- **代码发现** — 在使用之前，了解工作区的结构 (`go_workspace`)，模糊搜索无法精确定位的符号 (`go_search`)，或读取依赖项的公共表面 (`go_package_api`)。
- **文档** — 悬停以获取类型/文档/大小信息，调用函数时的签名帮助，或浏览渲染的包文档 (`source.doc`，包括内部包 pkg.go.dev 从未看到的)。
- **诊断与安全** — 每次编辑后的编译器和分析器错误 (`go_diagnostics` / 通过 `LSP` 自动)，以及轻量级的 `go_vulncheck` 可达性检查：在检测到工作区后立即运行一次作为基线，并在任何 `go.mod` 更改后再次运行。
- **格式化** — 标准的 `gofmt` 等价格式化和导入组织，均可脚本化和通过代码操作驱动。
- **重构** — 安全重命名（阻止会破坏接口满足的更改）、提取/内联，以及完整的 `refactor.rewrite.*` 系列（填充结构/switch、反转 if、拆分/合并行、移除未使用的参数、添加结构标签、实现接口）。完整目录和注意事项：[references/features.md](references/features.md#transformation)。

## 高效工作流程

这些读/改工作流程编码了避免冗余查询和半应用编辑的顺序——将每一步视为必需，即使为了节省一次往返。

- **会话启动** — 调用一次 `go_workspace` 以检测是否为 Go 工作区；如果是，立即跟随基线 `go_vulncheck` 以暴露工作区已携带的漏洞。这是无条件的，与编辑工作流程稍后依赖更改后的检查分开。

**读工作流程**（在触摸任何东西之前理解）：

1. `go_workspace` — 结构（模块/工作区/GOPATH）；如果会话启动尚未运行，则与上述检查使用相同的调用。
2. `go_search` — 通过名称模糊定位类型/函数/变量。
3. `go_file_context` — 在首次读取任何 Go 文件后立即查看它从其包的其余部分拉取了什么；如果该文件的依赖项发生变化，则重新运行。
4. `go_package_api` — 第三方依赖项或兄弟包的公共表面，无需读取每个文件。

**改工作流程**（迭代直到诊断干净）：

1. 先读（上述工作流程）。
2. 修改任何定义之前调用 `go_symbol_references` — 判断影响范围，然后读取需要匹配编辑的每个引用文件。
3. 进行所有计划编辑，包括引用站点编辑，然后继续。
4. 对每个已更改文件进行 `go_diagnostics` — 每次修改后强制执行，而不是可选的清理传递。
5. 修复报告的错误：在应用之前审查任何建议的快速修复差异，然后重新运行诊断以确认修复已应用。忽略与任务无关的提示/信息诊断。诊断消息可以概括周围的源代码，而不是逐字引用。
6. 只有当 `go.mod` 依赖项发生变化时，对整个工作区运行 `go_vulncheck` — 在诊断干净后，而不是之前。
7. 运行 `go test <已更改的包路径>` — 除非明确要求，否则不要使用 `./...`，因为完整仓库运行会减慢迭代循环。

**在依赖结果之前需要知道的注意事项：**

- `references` 结果仅反映查询文件的**构建配置**——对 `foo_windows.go` 的查询不会显示 `bar_linux.go` 中的匹配项；如果缺少跨平台结果，请在相关的 `GOOS`/构建标签下重新运行。
- `call_hierarchy` 仅显示**静态**调用——通过函数值或接口方法的调用对它不可见；当调用位置重要时，通过 `references` 核实。
- 提取/内联重构不如重命名严格：有时会丢失注释，并且标记为 `DO NOT EDIT` 的生成文件不会收到任何代码操作。
- `refactor.rewrite.fillStruct` 仅搜索光标上方的当前文件，并且需要已导入结构的包——如果类型刚刚输入，请先运行 `source.organizeImports`。

## `gopls` vs `godig` vs Context7 vs `govulncheck`

`gopls` 仅对本地构建中存在且可解析的代码进行推理：

- 对于与该构建无关的内容（版本历史、许可证、生态系统范围内的导入器、尚未添加的包的 CVE）→ 参见 `samber/cc-skills-golang@golang-pkg-go-dev` 技能 (`godig`) — 它直接查询 pkg.go.dev，无需本地检出。
- 对于全面的、整棵树的漏洞审计（CI 网关、定期扫描）而不是 `gopls` 轻量级的按需 `go_vulncheck` → 参见 `samber/cc-skills-golang@golang-security` 技能 (`govulncheck`)。
- Context7 仍然是用于非 Go 文档或未在 pkg.go.dev 上索引的 Go 模块的回退。

完整的任务到工具矩阵位于 `samber/cc-skills-golang@golang-how-to` 技能的 "`godig` vs `gopls` vs Context7 vs `govulncheck`" 部分。
