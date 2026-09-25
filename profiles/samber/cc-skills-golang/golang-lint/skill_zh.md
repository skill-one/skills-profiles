**角色：** 你是一个 Go 代码质量工程师。你将代码检查视为开发工作流程的一流部分——而不是事后清理步骤。

**编排模式：** 在采用旧代码库的代码检查时，使用“并行化旧代码库清理”部分中描述的五个子代理（自动修复、安全代码检查器、错误处理、样式/格式化、代码质量），以便独立代码检查器类别可以同时修复。在 Claude 代码中，使用 `ultracode` 明确选择多代理编排。

**模式：**

- **设置模式** — 配置 `.golangci.yml`、选择代码检查器、启用 CI：按顺序遵循配置和工作流部分。
- **编码模式** — 编写新的 Go 代码：在主代理继续实现功能时，在修改的文件上启动一个后台代理运行 `golangci-lint run --fix`；完成后显示结果。
- **解释/修复模式** — 阅读代码检查输出、抑制警告、修复现有代码问题：从“解释输出”和“抑制代码检查警告”开始；使用并行子代理进行大规模旧代码清理。

**依赖项：**

- golangci-lint: `go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest`

# Go 代码检查

## 概述

`golangci-lint` 是标准的 Go 代码检查工具。它将 100 多个代码检查器聚合到一个二进制文件中，并行运行它们，并提供统一的配置格式。在开发过程中频繁运行，并在 CI 中始终运行。

每个 Go 项目都必须有 `.golangci.yml` — 它是**事实依据**，用于确定启用了哪些代码检查器以及如何配置它们。查看 [推荐的配置](./assets/.golangci.yml) 以获得具有 48 个代码检查器的生产就绪设置。

## 快速参考

```bash
# 运行所有配置的代码检查器
golangci-lint run ./...

# 尽可能自动修复问题
golangci-lint run --fix ./...

# 格式化代码 (golangci-lint v2+)
golangci-lint fmt ./...

# 仅运行单个代码检查器
golangci-lint run --enable-only govet ./...

# 列出所有可用的代码检查器
golangci-lint linters

# 带有时间信息的详细输出
golangci-lint run --verbose ./...
```

## 配置

[推荐的 .golangci.yml](./assets/.golangci.yml) 提供了具有 33 个代码检查器的生产就绪设置。有关配置详细信息、代码检查器类别和每个代码检查器的描述，请参阅 **[代码检查器参考](./references/linter-reference.md)** — 哪些代码检查器检查什么（正确性、样式、复杂性、性能、安全性），所有 33 个以上代码检查器的描述，以及何时使用每个代码检查器。

## 抑制代码检查警告

谨慎使用 `//nolint` 指令——首先修复根本原因。

```go
// 良好：特定的代码检查器 + 理由
//nolint:errcheck // 一次性日志记录，错误不可操作
_ = logger.Sync()

// 不良：无理由的全面抑制
//nolint
_ = logger.Sync()
```

规则：

1. **`//nolint` 指令必须指定代码检查器名称**：`//nolint:errcheck` 而不是 `//nolint`
2. **`//nolint` 指令必须包含理由注释**：`//nolint:errcheck // 理由`
3. **`nolintlint` 代码检查器强制执行上述两条规则** — 它标记裸 `//nolint` 和缺少理由
4. **绝对不要在没有非常强烈理由的情况下抑制安全代码检查器** (gosec, bodyclose, sqlclosecheck)

有关全面模式和示例，请参阅 **[nolint 指令](./references/nolint-directives.md)** — 何时抑制、如何编写理由、单行与单函数抑制的模式，以及反模式。

## 开发工作流

1. **代码检查器应在每次重大更改后运行**：`golangci-lint run ./...`
2. **尽可能自动修复**：`golangci-lint run --fix ./...`
3. **提交前格式化**：`golangci-lint fmt ./...`
4. **旧代码的逐步采用**：在 `.golangci.yml` 中设置 `issues.new-from-rev` 仅检查新/更改的代码，然后逐步清理旧代码

Makefile 目标（推荐）：

```makefile
lint:
	golangci-lint run ./...

lint-fix:
	golangci-lint run --fix ./...

fmt:
	golangci-lint fmt ./...
```

有关 CI 管道设置（使用 `golangci-lint-action` 的 GitHub Actions），请参阅 `samber/cc-skills-golang@golang-continuous-integration` 技能。

## 解释输出

每个问题都遵循以下格式：

```
path/to/file.go:42:10: 描述问题的消息 (代码检查器名称)
```

括号中的代码检查器名称告诉你哪个代码检查器标记了它。使用此功能：

- 在 [参考](./references/linter-reference.md) 中查找代码检查器以了解它检查什么
- 如果是误报，使用 `//nolint:linter-name // 理由` 抑制
- 使用 `golangci-lint run --verbose` 获取附加上下文和时间信息

## 常见问题

| 问题 | 解决方案 |
| --- | --- |
| "deadline exceeded" | 在 `.golangci.yml` 中设置或增加 `run.timeout`；golangci-lint v2 默认无超时 (`0`) |
| 旧代码存在过多问题 | 设置 `issues.new-from-rev: HEAD~1` 仅检查新代码 |
| 找不到代码检查器 | 检查 `golangci-lint linters` — 代码检查器可能需要更新版本 |
| 代码检查器之间存在冲突 | 使用注释解释原因禁用不太有用的代码检查器 |
| 升级后 v1 配置错误 | 运行 `golangci-lint migrate` 转换配置格式 |
| 大型代码库运行缓慢 | 减少 `run.concurrency` 或使用 `linters.exclusions.paths` / `formatters.exclusions.paths` 排除路径 |

## 并行化旧代码库清理

在采用旧代码库的代码检查时，使用最多 5 个并行子代理同时修复独立的代码检查器类别：

- 子代理 1：运行 `golangci-lint run --fix ./...` 修复可自动修复的问题
- 子代理 2：修复安全代码检查器发现的问题（bodyclose、sqlclosecheck、gosec）
- 子代理 3：修复错误处理问题（errcheck、nilerr、wrapcheck）
- 子代理 4：修复样式和格式化（gofumpt、goimports、revive）
- 子代理 5：修复代码质量（gocritic、unused、ineffassign）

## 跨参考

- → 查看 `samber/cc-skills-golang@golang-continuous-integration` 技能以获取使用 golangci-lint-action 的 CI 管道
- → 查看 `samber/cc-skills-golang@golang-code-style` 技能以获取代码检查器强制执行的样式规则
- → 查看 `samber/cc-skills-golang@golang-security` 技能以获取代码检查之外的 SAST 工具（gosec、govulncheck）
- → 查看 `samber/cc-skills-golang@golang-continuous-integration` 技能以获取使用这些指南在 CI 中自动 AI 驱动的代码审查
