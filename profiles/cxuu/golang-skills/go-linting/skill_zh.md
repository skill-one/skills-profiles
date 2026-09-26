# Go 代码风格检查

## 核心原则

比任何"神圣"的代码风格检查工具更重要的：**在整个代码库中保持一致的代码风格检查**。

一致的代码风格检查有助于捕获常见问题，并建立高标准的代码质量，而无需进行不必要的限制。

## 资源路由

- `scripts/setup-lint.sh` - 在生成 `.golangci.yml`、验证首次代码风格检查或生成 JSON 元数据时运行。
- `assets/golangci.yml` - 作为已建立项目的 v2 golangci-lint 基线使用。

## 设置步骤

1. 使用 `scripts/setup-lint.sh` 创建 `.golangci.yml` 或复制 `assets/golangci.yml`
2. 运行 `golangci-lint run ./...`
3. 如果出现错误，按类别逐个修复（首先修复格式问题，然后是 `vet` 问题，最后是风格问题）
4. 重新运行直到无错误

生成 `.golangci.yml` 后，运行 `golangci-lint config verify --config .golangci.yml`
以验证配置模式，然后再依赖代码风格检查结果。

---

## 推荐的最低限度代码风格检查工具

这些代码风格检查工具能够捕获最常见的常见问题，同时保持高标准：

| 代码风格检查工具 | 目的 |
|------------------|------|
| [errcheck](https://github.com/kisielk/errcheck) | 确保错误被处理 |
| [goimports](https://pkg.go.dev/golang.org/x/tools/cmd/goimports) | 格式化代码和管理导入 |
| [revive](https://github.com/mgechev/revive) | 常见风格错误（现代的 `golint` 替代品） |
| [govet](https://pkg.go.dev/cmd/vet) | 分析代码中的常见错误 |
| [staticcheck](https://staticcheck.dev) | 各种静态分析检查 |

> **注意**：`revive` 是现代的、更快的 `golint` 的替代品，后者现已弃用。

---

## 代码风格检查工具：golangci-lint

使用 [golangci-lint](https://github.com/golangci/golangci-lint) 作为您的代码风格检查工具。参考 uber-go/guide 的 [示例 .golangci.yml](https://github.com/uber-go/guide/blob/master/.golangci.yml)。

---

## 示例配置

使用 `assets/golangci.yml` 作为维护的示例。它针对 golangci-lint v2（在 2026-06-19 使用 2.10.1 版本验证），将 `goimports` 保留在 `formatters` 下，并启用核心代码风格检查工具及常见的生产环境增强功能。

### 运行

```bash
# 安装此技能的配置所验证的版本
go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.10.1

# 运行所有代码风格检查工具
golangci-lint run

# 在特定路径上运行
golangci-lint run ./pkg/...
```

---

## 推荐的附加代码风格检查工具

除了最低限度的一组工具外，对于生产项目可以考虑以下工具：

| 代码风格检查工具 | 目的 | 启用时 |
|------------------|------|--------|
| [gosec](https://github.com/securego/gosec) | 安全漏洞检测 | 始终用于处理用户输入的服务 |
| [ineffassign](https://github.com/gordonklaus/ineffassign) | 检测无效的赋值 | 始终——捕获死代码 |
| [misspell](https://github.com/client9/misspell) | 修正注释/字符串中的常见拼写错误 | 始终 |
| [gocyclo](https://github.com/fzipp/gocyclo) | 圈复杂度阈值 | 当函数复杂度超过 ~15 时 |
| [exhaustive](https://github.com/nishanths/exhaustive) | 确保开关覆盖所有枚举值 | 当使用 `iota` 枚举时 |
| [bodyclose](https://github.com/timakin/bodyclose) | 检测未关闭的 HTTP 响应体 | 始终用于 HTTP 客户端代码 |

---

## nolint 指令

在抑制代码风格检查结果时，始终解释原因：

```go
//nolint:errcheck // 一次性日志记录；错误不可操作
_ = logger.Sync()
```

规则：
- 使用 `//nolint:lintername` —— 决不使用裸 `//nolint`
- 将注释放在与发现问题相同的行上
- 在 `//` 后面包含解释

---

## CI/CD 集成

在 CI 中测试后运行 `golangci-lint run ./...`。固定 CI 使用的 golangci-lint 版本，以防止本地和发布行为漂移。

### 提交前钩子

```bash
#!/bin/sh
# .git/hooks/pre-commit
golangci-lint run --new-from-rev=HEAD~1
```

使用 `--new-from-rev` 仅对已更改的代码进行代码风格检查，以保持反馈循环快速。

---

## 快速参考

| 任务 | 命令/操作 |
|------|----------|
| 安装 golangci-lint | `go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.10.1` |
| 运行代码风格检查工具 | `golangci-lint run` |
| 在路径上运行 | `golangci-lint run ./pkg/...` |
| 配置文件 | 项目根目录中的 `.golangci.yml` |
| CI 集成 | 在管道中运行 `golangci-lint run` |
| nolint 指令 | `//nolint:name // reason` —— 决不使用裸 `//nolint` |
| CI 集成 | 使用 `golangci/golangci-lint-action` for GitHub Actions |
| 提交前 | `golangci-lint run --new-from-rev=HEAD~1` |

### 代码风格检查工具选择指南

| 当您需要... | 使用 |
|------------|------|
| 错误处理覆盖率 | errcheck |
| 导入格式化 | goimports |
| 风格一致性 | revive |
| 错误检测 | govet, staticcheck |
| 以上所有 | 配置 golangci-lint |

---

## 相关技能

- **风格基础**：在解决代码风格检查工具强制执行的格式问题、嵌套和命名问题时，参考 [go-style-core](../go-style-core/SKILL.md)
- **代码审查**：在将代码风格检查工具输出与手动审查清单结合时，参考 [go-code-review](../go-code-review/SKILL.md)
- **错误处理**：在 errcheck 标记未处理的错误时，参考 [go-error-handling](../go-error-handling/SKILL.md) 以决定如何处理它们
- **测试**：在 CI 管道中与测试一起运行代码风格检查工具时，参考 [go-testing](../go-testing/SKILL.md)
