**角色：** 你是一个 Go 依赖管理负责人。你将每一个新的依赖都视为一个长期维护的承诺——在寻求外部包之前，你会先询问标准库是否已经解决了这个问题。

**依赖项：**

- govulncheck: `go install golang.org/x/vuln/cmd/govulncheck@latest`

# Go 依赖管理

## AI 代理规则：添加依赖前必须询问

**在运行 `go get` 添加任何新依赖之前，AI 代理必须向用户请求确认。** AI 代理可以在标准库已经提供等效功能时，建议那些未维护、质量低或不必要的包。使用 `go get -u` 升级现有依赖是安全的。

在提出依赖项之前，进行评估：

- 标准库是否已经涵盖了该用例？
- 许可证是否兼容？
- 是否有众所周知的替代方案？
- 它的作用以及为什么需要它？

`samber/cc-skills-golang@golang-popular-libraries` 技能包含一个经过筛选的、生产就绪的库列表。优先推荐该列表中的包。当没有经过筛选的选项时，优先选择 Go 团队 (`golang.org/x/...`) 或知名组织提供的知名包，而不是那些鲜为人知的替代方案。

## 关键规则

- `go.sum` 必须提交——它记录了每个依赖项版本的加密校验和，让 `go mod verify` 检测供应链篡改。没有它，一个被篡改的代理可能会无声地替换恶意代码
- 在每次发布前运行 `govulncheck ./...` 或 `go tool govulncheck ./...`——在它们到达生产环境之前捕获依赖树中的已知 CVE
- 在添加依赖项之前，维护状态、许可证兼容性和标准库替代方案是重要的考虑因素——每个依赖项都会增加攻击面、维护负担和二进制文件大小
- 在每次更改依赖项的提交前运行 `go mod tidy`——删除未使用的模块并添加缺失的模块，保持 go.mod 的真实性

## go.mod & go.sum

### 基本命令

| 命令           | 目的                                      |
| -------------- | ---------------------------------------- |
| `go mod tidy`  | 添加缺失的依赖项，删除未使用的依赖项         |
| `go mod download` | 下载模块到本地缓存                      |
| `go mod verify` | 验证缓存的模块与 go.sum 校验和是否匹配     |
| `go mod vendor` | 将依赖项复制到 `vendor/` 目录           |
| `go mod edit`  | 以编程方式编辑 go.mod（脚本、CI）   |
| `go mod graph` | 打印模块依赖关系图                      |
| `go mod why`  | 解释为什么需要某个模块或包              |

### Vendoring

当你需要封闭构建（无需网络访问）、校验和之外的再现性保证，或者在你部署到没有模块代理访问的环境时，使用 `go mod vendor`。CI 管道和 Docker 构建有时会受益于 vendoring。在每次依赖项更改后运行 `go mod vendor` 并提交 `vendor/` 目录。

## 安装和升级依赖项

### 添加依赖项

```bash
go get github.com/google/uuid          # 最新版本
go get github.com/google/uuid@v1.6.0   # 特定版本
go get github.com/google/uuid@latest   # 明确指定最新版本
go get github.com/google/uuid@<commit> # 特定提交（伪版本）
```

在固定版本之前，检查模块的可用版本、导入者和已知漏洞，在 pkg.go.dev 上查看 `samber/cc-skills-golang@golang-pkg-go-dev` 技能。

### 升级

```bash
go get -u ./...            # 将所有直接和间接依赖项升级到最新的次要版本/补丁版本
go get -u=patch ./...      # 仅升级到最新的补丁版本（更安全）
go get github.com/pkg@v1.5 # 升级特定包
```

**优先使用 `go get -u=patch`** 进行常规更新。补丁和次要版本更新通常比主要升级的风险更低，但仍需要审查。对于依赖项更新，运行：

```bash
go get -u=patch ./...
go mod tidy
go test ./...
go vet ./...
govulncheck ./...   # 或: go tool govulncheck ./...
```

受影响的库的发布说明和变更日志可能包含有关破坏性变更的重要信息。

### 删除依赖项

```bash
go get github.com/google/uuid@none  # 标记为删除
go mod tidy                          # 清理 go.mod 和 go.sum
```

### 安装 CLI 工具

对于 Go 1.24+ 模块，使用 `tool` 指令在 `go.mod` 中固定可执行工具。除非模块必须支持 Go <1.24，否则不要创建新的 `tools.go` 空导入文件。

```bash
# 将工具添加到当前模块。
go get -tool github.com/golangci/golangci-lint/v2/cmd/golangci-lint@latest
go get -tool golang.org/x/vuln/cmd/govulncheck@latest
go get -tool golang.org/x/perf/cmd/benchstat@latest

# 可重现地运行固定的工具。
go tool golangci-lint run ./...
go tool govulncheck ./...
go tool benchstat old.txt new.txt

# 当需要时，将所有模块固定的工具安装到 GOBIN/PATH。
go install tool

# 故意更新固定的工具，然后审查 go.mod/go.sum。
go get -u tool
go mod tidy
```

针对 Go 1.27 或更高版本的模块的 `go.mod` 结构。这是一个示例目标，不是上限；保持项目的实际 `go` 指令，不要为了添加工具而更改它。

```go
module example.com/project

go 1.27

tool (
    github.com/golangci/golangci-lint/v2/cmd/golangci-lint
    golang.org/x/vuln/cmd/govulncheck
    golang.org/x/perf/cmd/benchstat
)
```

对于 `go 1.27` 或更高版本，`go mod tidy` 自动合并重复的 `require` 块，并强制执行两块布局（直接依赖项，然后是间接依赖项），保留现有注释——合并引入第二个 `require` 块后无需手动清理。

仅适用于 Go <1.24 的遗留 `tools.go` 空导入解决方案：

```go
//go:build tools

package tools

import (
    _ "github.com/golangci/golangci-lint/v2/cmd/golangci-lint"
    _ "golang.org/x/vuln/cmd/govulncheck"
)
```

规则：Go 1.24+ = `tool` 指令。Go <1.24 = `tools.go` 回退。

### 模块目标说明

在使用更新的工具链时，`go mod init` 可能会创建一个具有较旧默认 `go` 指令的模块。如果项目有意针对更新工具链的 API，故意更新指令：

```bash
go mod edit -go=1.27
go mod tidy
```

对于未来的 Go 版本，使用项目打算的目标版本。在项目明确同意升级它之前，不要使用比模块的 `go` 指令更新的 API。

## 深入探讨

- **[版本控制 & MVS](./references/versioning.md)** — 语义版本控制规则（主版本号.次版本号.修订号），何时递增每个数字，预发布版本，最小版本选择（MVS）算法（为什么你不能只是选择“最新”），以及主版本号后缀约定（v0、v1、v2 后缀用于破坏性变更）。

- **[审计依赖项](./references/auditing.md)** — 使用 `govulncheck` 进行漏洞扫描，跟踪过时的依赖项，分析哪些依赖项使二进制文件变大（`goweight`），以及区分测试专用与二进制依赖项以保持 `go.mod` 清洁。

- **[依赖项冲突 & 解决方案](./references/conflicts.md)** — 诊断版本冲突（当你请求不兼容的版本时 `go get` 会做什么），解决方案策略（`replace` 指令用于本地开发，`exclude` 用于损坏的版本，`retract` 用于应跳过的已发布版本），以及解决你依赖树中冲突的工作流程。

- **[Go 工作区](./references/workspaces.md)** — 用于多模块开发（例如，库 + 示例应用程序）的 `go.work` 文件，何时使用工作区与单一代码库，以及工作区最佳实践。

- **[自动依赖项更新](./references/automated-updates.md)** — 设置 Dependabot 或 Renovate 以自动依赖项更新 PR，自动合并策略（何时自动合并与需要审查），以及处理安全更新。

- **[可视化依赖关系图](./references/visualization.md)** — 使用 `go mod graph` 检查完整的依赖关系树，使用 `modgraphviz` 可视化它，以及使用交互式工具查找哪些依赖项链导致臃肿。

## 跨参考

- → 参考 `samber/cc-skills-golang@golang-continuous-integration` 技能以设置 Dependabot/Renovate CI
- → 参考 `samber/cc-skills-golang@golang-security` 技能以使用 govulncheck 进行漏洞扫描
- → 参考 `samber/cc-skills-golang@golang-popular-libraries` 技能以获取经过筛选的库推荐

## 快速参考

```bash
# 创建新模块
go mod init github.com/user/project

# 添加依赖项
go get github.com/google/uuid@v1.6.0

# 升级所有依赖项（仅补丁，更安全）
go get -u=patch ./...

# 删除未使用的依赖项
go mod tidy

# 检查漏洞
govulncheck ./...   # 或: go tool govulncheck ./...

# 检查过时的依赖项
go list -u -m -json all | go-mod-outdated -update -direct

# 通过依赖项分析二进制文件大小
goweight

# 了解依赖项存在的原因
go mod why -m github.com/some/module

# 可视化依赖关系图
go mod graph | modgraphviz | dot -Tpng -o deps.png

# 验证校验和
go mod verify
```
