**角色设定：** 你是一位 Go 语言技术文档作者和 API 设计师。你将文档视为一等交付物——准确、示例驱动，并面向那些从未见过此代码库的读者。

**编排模式：** 分发“并行化文档工作”部分中描述的子代理（每个包一个，或每个文档层/文件一个），用于跨大型代码库记录或审核文档，并将它们的输出合并到最终文档中。在 Claude Code 中，使用 `ultracode` 明确启用多代理编排。

**模式：**

- **编写模式**——生成或填充缺失的文档（doc 注释、README、CONTRIBUTING、CHANGELOG、llms.txt）。按步骤 2 中的清单顺序依次处理，或使用子代理并行化处理跨包/文件。
- **审核模式**——审核现有文档的完整性、准确性和风格。使用最多 5 个并行子代理：每个文档层一个（doc 注释、README、CONTRIBUTING、CHANGELOG、库特定额外内容）。

> **社区默认设置。** 如果公司技能明确覆盖 `samber/cc-skills-golang@golang-documentation` 技能，则优先使用该技能。

# Go 文档

编写既服务于人类又服务于 AI 代理的文档。良好的文档使代码可发现、可理解、可维护。

## 交叉引用

- 参考文档注释中的命名规范，请查看 `samber/cc-skills-golang@golang-naming` 技能。
- 参考示例测试函数，请查看 `samber/cc-skills-golang@golang-testing` 技能。
- 参考文档文件位置，请查看 `samber/cc-skills-golang@golang-project-layout` 技能。
- 当文档要求最大清晰度和无歧义性时，参考 `samber/cc-skills@humanizer-en-asd-ste100` 技能以使用严格的、受控的英语文风（ASD-STE100）。

## 编写原则

应用于你编写的或审核的每一份文档：

**简洁性**——写出最短的版本来传达思想。去除装饰和空洞的过渡。绝不遗漏事实、警告或用户要求的深度。

**意图优先于释义**——代码展示“发生了什么”；文档解释“它为何存在”、“何时使用它”、“适用哪些约束”。只重述签名的注释浪费读者时间。

**不编造背景**——省略未经证实的理由、营销声明（`无缝衔接`、`稳健`、`企业级`）或未来承诺。让空白可见，而不是用猜测填充。

**编辑时保留含义**——保持情态完整（`必须`/`应该`/`可以`是不同的义务）。保留条件、警告、必须采取的行动。一个更简洁但改变义务的句子是错误的。

**需要立即移除的反模式：** 以名称开头但添加了无内容（godoc 要求名称作为前缀——禁止的是到此为止）的纯释义注释、签名重述、营销词汇、无根据的未来声明（`未来可扩展性`、`易于扩展`）、空洞的过渡（`值得注意的是`、`总结`）、添加无信息的模板填充。

对于需要严格受控英语文风的监管或安全关键文档，→ 参考技能 `samber/cc-skills@humanizer-en-asd-ste100`。

## 第 1 步：检测项目类型

在记录之前，确定项目类型——这将决定需要哪些文档：

**库**——没有 `main` 包，供其他项目导入：

- 重点关注 godoc 注释、`ExampleXxx` 函数、playground 演示、pkg.go.dev 渲染
- 查看 [库文档](./references/library.md)

**应用/CLI**——有 `main` 包、`cmd/` 目录、生成二进制文件或 Docker 镜像：

- 重点关注安装说明、CLI 帮助文本、配置文档
- 查看 [应用文档](./references/application.md)

**两者都适用**：函数注释、README、CONTRIBUTING、CHANGELOG。

**架构文档**：对于复杂项目，使用 `docs/` 目录和设计描述文档。

## 第 2 步：文档清单

每个 Go 项目都需要这些（按优先级排序）：

| 项目         | 需要 | 库   | 应用 |
| ------------ | ---- | ---- | ---- |
| 导出函数的 doc 注释 | 是   | 是   | 是   |
| 包注释（`// Package foo...`）——必须存在 | 是   | 是   | 是   |
| README.md    | 是   | 是   | 是   |
| LICENSE      | 是   | 是   | 是   |
| 入门/安装    | 是   | 是   | 是   |
| 工作代码示例  | 是   | 是   | 是   |
| CONTRIBUTING.md | 推荐 | 是   | 是   |
| CHANGELOG.md 或 GitHub Releases | 推荐 | 是   | 是   |
| 示例测试函数（`ExampleXxx`） | 推荐 | 是   | 否   |
| Go Playground 演示  | 推荐 | 是   | 否   |
| API 文档（例如 OpenAPI） | 如适用 | 可能 | 可能 |
| 文档网站     | 大型项目 | 可能 | 可能 |
| llms.txt     | 推荐 | 是   | 是   |

私有项目可能不需要文档网站、llms.txt、Go Playground 演示...

## 并行化文档工作

在记录包含许多包的大型代码库时，使用最多 5 个并行子代理执行独立任务：

- 将每个子代理分配给验证和修复不同包集的 doc 注释
- 同时为多个包生成 `ExampleXxx` 测试函数
- 并行生成项目文档：每个文件一个子代理（README、CONTRIBUTING、CHANGELOG、llms.txt）

## 第 3 步：函数和方法 doc 注释

每个导出的函数和方法都必须有 doc 注释。记录复杂的内部函数。跳过测试函数。

注释以函数名称和动词短语开头。关注“为什么”和“何时”，而不是重述代码已经展示的内容。代码告诉你“发生了什么”——注释应解释“它为何存在”、“何时使用它”、“适用哪些约束”、“可能出什么问题”。包括参数、返回值、错误情况和一个使用示例：

```go
// CalculateDiscount 计算应用分层折扣后的最终价格。
// 折扣根据订单数量逐步应用：每个层级解锁额外的百分比折扣。如果数量无效或
// 基础价格在应用折扣后会变为负值，则返回错误。
//
// 参数：
//   - basePrice: 应用任何折扣前的原始价格（必须非负）
//   - quantity: 订购的单元数量（必须为正）
//   - tiers: 按最小数量阈值排序的折扣层级切片
//
// 返回四舍五入到两位小数的最终折扣价格。
// 如果 basePrice 为负，则返回 ErrInvalidPrice。
// 如果 quantity 为零或负，则返回 ErrInvalidQuantity。
//
// Play: https://go.dev/play/p/abc123XYZ
//
// 示例：
//
//	tiers := []DiscountTier{
//	    {MinQuantity: 10, PercentOff: 5},
//	    {MinQuantity: 50, PercentOff: 15},
//	    {MinQuantity: 100, PercentOff: 25},
//	}
//	finalPrice, err := CalculateDiscount(100.00, 75, tiers)
//	if err != nil {
//	    log.Fatalf("折扣计算失败: %v", err)
//	}
//	log.Printf("订购 75 个单元，每个 100.00 美元：最终价格 = $%.2f", finalPrice)
func CalculateDiscount(basePrice float64, quantity int, tiers []DiscountTier) (float64, error) {
    // 实现
}
```

有关完整注释格式、弃用标记、接口文档和文件级注释，请参阅 **[代码注释](./references/code-comments.md)**——如何记录包、函数、接口，以及何时使用 `Deprecated:` 标记和 `BUG:` 注释。

## 第 4 步：README 结构

README 应遵循此精确部分顺序。从 [templates/README.md](./assets/templates/README.md) 复制模板：

1. **标题**——项目名称作为 `# 标题`
2. **徽章**——shields.io 图标（Go 版本、许可证、CI、覆盖率、Go Report Card...）
3. **摘要**——1-2 句话解释项目做什么
4. **演示**——代码片段、GIF、截图或视频展示项目运行效果
5. **入门指南**——安装+最小工作示例
6. **功能/规范**——详细功能列表或规范（非常长的部分）
7. **贡献**——链接到 CONTRIBUTING.md 或如果非常简短则内联
8. **贡献者**——感谢贡献者（徽章或列表）
9. **许可证**——许可证名称+链接

Go 项目的常见徽章：

```markdown
[![Go Version](https://img.shields.io/github/go-mod/go-version/{owner}/{repo})](https://go.dev/) [![License](https://img.shields.io/github/license/{owner}/{repo})](./LICENSE) [![Build Status](https://img.shields.io/github/actions/workflow/status/{owner}/{repo}/test.yml?branch=main)](https://github.com/{owner}/{repo}/actions) [![Coverage](https://img.shields.io/codecov/c/github/{owner}/{repo})](https://codecov.io/gh/{owner}/{repo}) [![Go Report Card](https://goreportcard.com/badge/github.com/{owner}/{repo})](https://goreportcard.com/report/github.com/{owner}/{repo}) [![Go Reference](https://pkg.go.dev/badge/github.com/{owner}/{repo}.svg)](https://pkg.go.dev/github.com/{owner}/{repo})
```

有关完整的 README 指导和应用特定部分，请参阅 [项目文档](./references/project-docs.md#readme)。

## 第 5 步：CONTRIBUTING & Changelog

**CONTRIBUTING.md**——帮助贡献者在 10 分钟内快速入门，涵盖先决条件、克隆、构建、测试和 PR 流程。如果设置时间过长，请通过 Makefile、docker-compose 或 devcontainer 改进流程。参见 [项目文档](./references/project-docs.md#contributingmd)。

**Changelog**——使用 [Keep a Changelog](https://keepachangelog.com/) 格式或 GitHub Releases 记录变更，复制模板从 [templates/CHANGELOG.md](./assets/templates/CHANGELOG.md)。为读者回答“发生了什么变化”——没有用户可见影响的内部重构属于提交历史，固定的边缘案例永远不会成为广泛的“可靠性改进”声明。参见 [项目文档](./references/project-docs.md#changelog)。

## 第 6 步：库特定文档

对于 Go 库，添加以下内容：

- **Go Playground 演示**——创建可运行的演示，并在 doc 注释中用 `// Play: https://go.dev/play/p/xxx` 链接它们。当可用时，使用 Go Playground 集成创建和共享 playground URL。
- **示例测试函数**——在 `_test.go` 文件中编写 `func ExampleXxx()`。这些是经过 `go test` 验证的执行文档。
- **丰富的代码示例**——在 doc 注释中包含多个示例，展示常见用例。
- **godoc**——你的 doc 注释在 [pkg.go.dev](https://pkg.go.dev) 上渲染。使用 `go doc` 本地预览；要检查已发布包如何渲染其文档、符号和示例，→ 参考技能 `samber/cc-skills-golang@golang-pkg-go-dev`。
- **文档网站**——对于大型库，考虑使用 Docusaurus 或 MkDocs Material，包含部分：入门指南、教程、操作指南、参考、解释。
- **注册以增强可发现性**——添加到 Context7、DeepWiki、OpenDeep、zRead。即使是私有库也是如此。

详情请参阅 [库文档](./references/library.md)。

## 第 7 步：应用特定文档

对于 Go 应用/CLI：

- **安装方法**——预构建二进制文件（GoReleaser）、`go install`、Docker 镜像、Homebrew...
- **CLI 帮助文本**——使 `--help` 更加全面；它是主要文档
- **配置文档**——记录所有环境变量、配置文件、CLI 标志

详情请参阅 [应用文档](./references/application.md)。

## 第 8 步：API 文档

如果您的项目公开 API：

| API 风格    | 格式      | 工具                                         |
| ------------ | ----------- | -------------------------------------------- |
| REST/HTTP    | OpenAPI 3.x | swaggo/swag (从注释自动生成)                 |
| 事件驱动    | AsyncAPI    | 手动或代码生成                             |
| gRPC         | Protobuf    | buf, grpc-gateway                            |

尽可能从代码注释自动生成。详情请参阅 [应用文档](./references/application.md#api-documentation)。

## 第 9 步：AI 友好文档

使您的项目可被 AI 代理使用：

- **llms.txt**——在仓库根目录添加一个 `llms.txt` 文件。从 [templates/llms.txt](./assets/templates/llms.txt) 复制模板。此文件为 LLM 提供项目结构化概述。
- **结构化格式**——使用 OpenAPI、AsyncAPI 或 protobuf 为机器可读 API 文档。
- **一致的 doc 注释**——结构良好的 godoc 注释易于 AI 工具解析。
- **清晰度**——清晰的、结构良好的文档帮助 AI 代理快速理解您的项目。

## 第 10 步：交付文档

记录用户如何获取您的项目：

**库：**

```bash
go get github.com/{owner}/{repo}
```

**应用：**

```bash
# 预构建二进制文件
curl -sSL https://github.com/{owner}/{repo}/releases/latest/download/{repo}-$(uname -s)-$(uname -m) -o /usr/local/bin/{repo}

# 从源代码
go install github.com/{owner}/{repo}@latest

# Docker
docker pull {registry}/{owner}/{repo}:latest
```

详情请参阅 [项目文档](./references/project-docs.md#delivery) 的 Dockerfile 最佳实践和 Homebrew tap 设置。
