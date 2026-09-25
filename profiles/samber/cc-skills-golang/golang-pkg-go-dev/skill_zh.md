# golang-pkg-go-dev

**依赖项：** `godig` — `go install github.com/samber/godig/cmd/godig@latest`（或者使用注册的godig MCP服务器/托管实例）。

`godig` 查询 [pkg.go.dev](https://pkg.go.dev) API。用它来回答有关Go包和模块的问题：文档、符号、版本、导入者和漏洞。它既可以用作CLI，也可以用作MCP服务器，并且所有操作都是**只读**的，不需要身份验证。

## 何时使用此技能

在以下问题触发时使用：

- "github.com/samber/lo 有哪些可用版本？"
- "golang.org/x/text 是否有已知漏洞？"
- "显示包X的文档/符号。"
- "哪些包导入X？"
- "搜索Go包Y。"

## 在 `godig`、gopls、Context7 和 govulncheck 之间进行选择

简而言之：`godig` 回答有关**已发布生态系统**的问题（即使包尚未在您的 `go.mod` 中也能工作）；`gopls` 推理**您的本地解析构建**（`go.sum`，包括 `replace` 的分支）；Context7 是非Go或未索引文档的回退；`govulncheck` 是整棵树的漏洞审计（→ `samber/cc-skills-golang@golang-security`）。有关将 `gopls`（MCP服务器、原生 `LSP` 工具和CLI）与Claude Code连接的说明，请参阅 `samber/cc-skills-golang@golang-gopls` 技能；有关 `samber/cc-skills-golang@golang-how-to` 技能的“`godig` vs gopls vs Context7 vs govulncheck”部分，请参阅完整的任务到工具矩阵。

## 设置

### 安装

```bash
go install github.com/samber/godig/cmd/godig@latest
```

### 注册MCP服务器（可选）

`godig mcp` 默认运行在 **stdio** 上，或者使用 `--transport http` 运行在 **流式HTTP** 上。该命令与托管的独立性无关——任何支持MCP的主机都可以指向它。Claude Code 通过其自己的CLI注册它：

stdio（客户端按需启动godig）：

```bash
claude mcp add pkg-go-dev -- godig mcp
```

流式HTTP（共享服务器在 `/mcp`，默认 `:8080`）：

```bash
godig mcp --transport http --addr :8080
claude mcp add --transport http pkg-go-dev http://localhost:8080/mcp
```

托管实例（无需安装）—— 一个公共服务器运行在 `https://godig.samber.dev/mcp`：

```bash
claude mcp add --transport http pkg-go-dev https://godig.samber.dev/mcp
```

其他支持MCP的托管工具（Cursor、Windsurf 和其他）各自有自己的MCP服务器注册——它们各自设置文件中的一个条目指向相同的 `godig mcp` 命令或托管URL，而不是共享配置格式。

CLI 和 MCP 服务器在匹配的名称下暴露**相同的**操作。当 `godig` 安装时，请优先使用CLI；当 `godig` 未安装时，托管实例是一个回退。

## 命令

**全局标志（所有命令）：** `-o/--output table|json|raw|md`（默认 `table`——传递 `-o md` 用于聊天），`--base-url`（pkg.go.dev API），`--vuln-base-url`（Go漏洞数据库，由 `vulns` 和 `overview` 调用），`--timeout`，`--log-level debug|info|warn|error|off`。所有标志也可以通过 `GODIG_*` 环境变量设置。

| 命令 | 参数 | 特定标志 | 目的 |
| --- | --- | --- | --- |
| `overview` | `<path>` | `--version` | 紧凑摘要（元数据、版本、许可证、漏洞）——从这里开始 |
| `search` | `<query>` | `--symbol --limit --filter` | 查找包（可选导出符号） |
| `package info` | `<path>` | `--module --version` | 包元数据 |
| `package imports` | `<path>` | `--module --version` | 此包导入的包（纯列表） |
| `package doc` | `<path>` | `--module --version --goos --goarch --format md\|text\|html\|markdown` | 完整的包文档（大） |
| `package examples` | `<path>` | `--module --version --goos --goarch --symbol` | 可运行的示例（大；使用 `--symbol` 范围） |
| `package licenses` | `<path>` | `--module --version` | 许可证文件，完整文本（大） |
| `symbol doc` | `<path> <symbol>` | `--module --version --goos --goarch` | 一个符号的签名+文档（高效的token） |
| `symbol examples` | `<path> <symbol>` | `--module --version --goos --goarch` | 一个符号的可运行示例 |
| `symbols` | `<path>` | `--module --version --goos --goarch --limit --filter` | 列出导出的符号 |
| `module info` | `<path>` | `--version` | 模块元数据 |
| `module licenses` | `<path>` | `--version` | 模块许可证文件（大） |
| `module readme` | `<path>` | `--version` | 模块README，完整Markdown（大） |
| `dependencies` | `<path>` | `--version` | go.mod 依赖：requires / replaces / excludes / go指令 |
| `packages` | `<path>` | `--version --limit --filter` | 模块中包含的包 |
| `versions` | `<path>` | `--limit --filter` | 所有版本，最新版本优先 |
| `major-versions` | `<path>` | `--limit --filter --exclude-pseudo` | 主要版本（v1、v2 …）作为单独的模块存在 |
| `imported-by` | `<path>` | `--module --version --limit --filter` | 导入此包的包 |
| `vulns` | `<path>` | `--version --limit` | 已知漏洞（来自Go漏洞数据库） |
| `mcp` | — | `--transport stdio\|http --addr --cache-ttl --cache-size` | 作为MCP服务器运行 |
| `version` | — | — | 打印godig版本/提交/构建日期 |

当 `godig` 作为MCP服务器运行时，上述每个数据命令都作为同名操作暴露。

**退出代码：** `0` 成功，`1` 运行时错误（网络、包未找到），`2` 使用错误——缺少/无效参数或标志（例如非正的 `--limit`），或者使用没有子命令的命令组调用的命令（`godig package`）。检查 `2` 以区分格式错误和查找失败。

每个命令的完整 `-o md` 输出：[sample-output.md](references/sample-output.md)。

### 小贴士

- **从 `overview` 开始**——一次调用返回紧凑摘要（元数据、最新+最近版本、许可证类型、漏洞）。只有在需要完整文本时，才使用 `doc`/`examples`/`module readme`/`licenses`（大）。
- **始终传递 `-o md`** 以便结果以Markdown格式（表格，或原始文档/README）在聊天中显示。其他格式存在（`table` 默认，`json`，`raw`），但在此处优先使用 `md`。
- `<path>` 是完整导入路径，例如 `github.com/samber/lo`——将其作为位置参数传递。
- `--version` 固定特定模块版本（`v1.5.0`，`latest`，`master`，`main`）；`--module` 消除包所属模块的歧义。
- `--filter` 使用Go布尔表达式在服务器端缩小列表结果——请参阅 [Filter语法](#filter-syntax)。
- `--goos`/`--goarch` 设置文档/符号构建上下文（例如 `linux`/`amd64`）。
- 当您只需要一个符号时，优先使用 `symbol doc`/`symbol examples` 而不是包范围的 `package doc`/`package examples`——token数量大大减少。
- **并行化独立的查找**——每个命令都是一个自包含的、只读的HTTP查询，因此调用之间不会相互依赖。当任务需要为**多个**符号、包或模块获取文档、示例、版本或漏洞时，一次发出所有调用（在单个回合中多次调用 `godig`），而不是一个接一个地调用——时间从延迟总和变为最慢的单个调用。对于大型扩展（文档许多符号、比较许多候选库、跨依赖集审计CVE），分派最多5个并行子代理，每个子代理运行自己的 `godig` 调用并返回紧凑摘要，因此原始大输出永远不会出现在主上下文中。
- 列出命令自动分页（返回所有结果）；使用 `--limit` 来限制。

### Filter语法

`--filter`（在 `search`、`versions`、`major-versions`、`packages`、`imported-by`、`symbols`）接受一个**在服务器端评估的Go布尔表达式，每个结果项评估一次**。它不是正则表达式——将整个表达式用单引号括起来以供shell使用。

- **标识符是每个项的字段，这些字段因命令而异**——一个列表中有效的字段在另一个列表中被拒绝（例如 `search` 暴露 `packagePath`，而不是 `path`）。未知字段会失败并显示 `undefined identifier: <name>`（HTTP 400），其中包含冒犯字段。字段使用项的小写JSON键；例外是类似枚举的值，如 `kind`，它们是大写的（`Function`，而不是 `func`）。
- **运算符**：`==` `!=` `<` `<=` `>` `>=`，布尔 `&&` `||` `!`，括号用于分组。
- **字符串函数**：`contains(s, sub)`，`hasPrefix(s, pre)`，`hasSuffix(s, suf)`。
- **字面量**：双引号字符串（`"Function"`），`true`/`false`，数字。

每个命令的过滤字段（除非另有说明，否则为字符串）：

| 命令 | 字段 |
| --- | --- |
| `search` | `modulePath`, `packagePath`, `synopsis`, `version` |
| `versions` | `version`, `modulePath`, `deprecated` (bool), `retracted` (bool), `hasGoMod` (bool), `commitTime` |
| `packages` | `path`, `name`, `synopsis`, `isRedistributable` (bool) |
| `imported-by` | `path`（导入的包路径） |
| `symbols` | `name`, `kind` (`Function`/`Method`/`Type`/`Variable`/`Constant`), `synopsis`, `parent` |
| `major-versions` | `modulePath`, `major`, `version`, `isLatest` (bool) |

```bash
godig symbols github.com/samber/lo --filter 'kind=="Function"' -o md
godig symbols github.com/samber/lo --filter 'kind=="Function" && hasPrefix(name,"Map")' -o md
godig versions github.com/samber/lo --filter 'hasPrefix(version,"v1.5")' -o md
godig versions github.com/samber/lo --filter 'deprecated==false && retracted==false' -o md
godig search "result option" --filter 'hasPrefix(packagePath,"github.com/samber/")' -o md
```

### 示例

始终请求Markdown输出（`-o md`）：

```bash
# 概述——从这里开始（紧凑，一次调用）
godig overview github.com/samber/ro -o md

# 搜索
godig search "result option monad" --limit 5 -o md

# 包方面
godig package info github.com/samber/ro -o md
godig package imports github.com/samber/ro -o md
godig package doc github.com/samber/ro --format md -o md
godig package examples github.com/samber/ro --symbol Map -o md
godig package licenses github.com/samber/ro -o md

# 单个符号（高效的token vs 包范围的文档/示例）
godig symbol doc github.com/samber/lo Map -o md
godig symbol examples github.com/samber/oops OopsError.Error -o md

# 模块方面
godig module info github.com/samber/ro -o md
godig module readme github.com/samber/ro -o raw
godig dependencies github.com/samber/ro -o md

# 列表（自动分页；使用 `--limit` 限制）
godig versions github.com/samber/ro -o md
godig major-versions github.com/samber/lo -o md
godig packages github.com/samber/ro -o md
godig imported-by github.com/samber/ro --limit 20 -o md
godig symbols github.com/samber/ro --filter 'kind=="Function"' -o md

# 固定版本/设置构建上下文
godig versions github.com/samber/ro --filter 'hasPrefix(version,"v0.3")' -o md
godig package doc github.com/samber/lo --version v1.50.0 -o md
godig symbols github.com/samber/ro --goos linux --goarch amd64 -o md

# 漏洞
godig vulns github.com/samber/ro -o md
```

---

此技能并不详尽。`godig --help` 和每个子命令的 `--help` 列出当前标志和输出格式；数据与 [pkg.go.dev](https://pkg.go.dev) 暴露的内容相同。

如果您在 `godig` 中遇到错误或意外行为，请在 <https://github.com/samber/godig/issues> 打开问题。
