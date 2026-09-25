# SwiftLint

SwiftLint 通过对源文件进行可配置规则集的检查来强制执行 Swift 风格和规范。本指南涵盖设置、配置、规则选择、抑制、CI 集成和发布策略。

SwiftLint 是一个 **风格强制执行工具**，而不是一个风格指南。关于底层的 Swift 命名和设计规范，请参阅 `swift-api-design-guidelines`。关于架构模式，请参阅 `swift-architecture`。

## 目录

- [推荐设置](#推荐设置)
- [配置](#配置)
- [规则选择策略](#规则选择策略)
- [抑制](#抑制)
- [基线](#基线)
- [自动修正](#自动修正)
- [CI 集成](#ci集成)
- [集成决策树](#集成决策树)
- [多个配置](#多个配置)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

---

## 推荐设置

**默认：通过 `SimplyDanny/SwiftLintPlugins` 的构建工具插件。**

将插件包添加到 `Package.swift` 或通过 Xcode 的包依赖项：

```swift
// Package.swift
dependencies: [
  .package(url: "https://github.com/SimplyDanny/SwiftLintPlugins", from: "<已审查版本>")
]
```

对于 SwiftPM 目标，应用插件：

```swift
.target(
    name: "MyApp",
    plugins: [.plugin(name: "SwiftLintBuildToolPlugin", package: "SwiftLintPlugins")]
)
```

对于没有 `Package.swift` 的 Xcode 项目，在项目设置中添加包依赖项，然后在目标的构建阶段或包的插件信任对话框中启用插件。

构建工具插件会在每次构建时自动运行 SwiftLint。不需要运行脚本。

> **首次构建**：Xcode 提示信任插件。为 SwiftLintPlugins 包选择“信任并启用所有”。

有关替代方案（运行脚本、命令插件、Homebrew CLI），请参阅 [参考资料/plugins-run-scripts-and-integrations.md](references/plugins-run-scripts-and-integrations.md)。

## 配置

在项目根目录下创建 `.swiftlint.yml`。SwiftLint 会从调用或插件工作目录加载主配置，然后在自动发现配置时，可以为每个文件合并最近的嵌套 `.swiftlint.yml`。传递 `--config` 会覆盖自动发现并禁用嵌套配置查找。

```yaml
# .swiftlint.yml — 保守的启动配置
disabled_rules:
  - trailing_whitespace
  - todo

opt_in_rules:
  - empty_count
  - closure_spacing
  - force_unwrapping
  - sorted_imports
  - vertical_whitespace_opening_braces
  - private_swiftui_state
  - unhandled_throwing_task
  - accessibility_label_for_image

included:
  - Sources
  - Tests

excluded:
  - .build
  - DerivedData
  - "**/.build"
  - "**/Generated"

line_length:
  warning: 140
  error: 200

type_body_length:
  warning: 300
  error: 500

file_length:
  warning: 500
  error: 1000
```

关键配置选项：

| 键 | 目的 |
|-----|---------|
| `disabled_rules` | 关闭默认启用的规则 |
| `opt_in_rules` | 启用默认未启用的规则 |
| `only_rules` | 仅使用列出的规则（与 `disabled_rules`/`opt_in_rules` 互斥） |
| `analyzer_rules` | 需要编译器日志的规则（通过 `swiftlint analyze` 运行） |
| `baseline` | 已有基线文件的路径，用于抑制已知违规 |
| `write_baseline` | SwiftLint 应该写入新基线文件的路径 |
| `included` | 要检查的路径（默认：当前目录） |
| `excluded` | 要跳过的路径 |
| `strict` | 将所有警告提升为错误 |
| `lenient` | 将所有错误降级为警告 |
| `allow_zero_lintable_files` | 当没有找到 Swift 文件时抑制错误 |
| `reporter` | 输出格式：`xcode`（默认）、`json`、`checkstyle`、`sarif`、`csv`、`emoji` 等 |

有关完整配置细节，包括严重性调整、环境变量插值和嵌套/远程配置，请参阅 [参考资料/adoption-and-configuration.md](references/adoption-and-configuration.md)。

## 规则选择策略

SwiftLint 提供三种规则类别：

1. **默认规则** — 自动启用，涵盖广泛接受的规范
2. **opt-in 规则** — 默认禁用，通过 `opt_in_rules` 选择性启用
3. **分析器规则** — 需要编译器日志，通过 `analyzer_rules` 启用

在 <https://realm.github.io/SwiftLint/rule-directory.html> 浏览完整的分类列表。

**新项目的推荐方法：**

1. 从默认值开始。运行 `swiftlint rules` 查看哪些规则已启用。
2. 禁用与团队已建立的规范冲突的规则。
3. 逐个添加 opt-in 规则。在每次提交前审查违规。
4. 除非有特定原因，否则不要使用 `only_rules`。

**现有代码库的推荐方法：**

1. 从默认规则集开始。
2. 创建基线（见 [基线](#基线)）以抑制所有现有违规。
3. 运行与 CI 使用的相同严格、基线感知命令并修复每个新违规。
4. 重新运行，直到变为绿色，然后再启用另一个规则或开始下一个清理批次。
5. 逐步减少基线违规，不要接受基线增长。

不要转录或记忆规则目录。当需要时，在官方规则目录中查找规则标识符和配置选项。

## 抑制

当规则产生误报或违规是故意且经过审查时，抑制特定行的 SwiftLint。

```swift
// swiftlint:disable:next force_cast
let view = object as! UIView

let legacy = try! JSONDecoder().decode(T.self, from: data) // swiftlint:disable:this force_try

// swiftlint:disable:previous large_tuple
```

为区域禁用：

```swift
// swiftlint:disable cyclomatic_complexity
func complexRouter(...) { ... }
// swiftlint:enable cyclomatic_complexity
```

禁用所有规则（谨慎使用）：

```swift
// swiftlint:disable all
// ... 生成的或遗留代码 ...
// swiftlint:enable all
```

**策略：**
- 优先选择有针对性的单个规则抑制，而不是 `all`。
- 始终在区域结束后重新启用。
- 对于生成代码，优先使用 `.swiftlint.yml` 中的 `excluded` 路径，而不是内联抑制。
- 对于具有不同容忍度的测试目标，使用子配置（见 [多个配置](#多个配置)）。

有关完整抑制语法，请参阅 [参考资料/rules-suppressions-and-baselines.md](references/rules-suppressions-and-baselines.md)。

## 基线

基线允许您在不首先修复每个遗留违规的情况下，在现有代码库中采用 SwiftLint。

**创建基线：**

```sh
swiftlint --write-baseline .swiftlint.baseline
```

这将记录所有当前违规。未来的运行将与此基线进行比较，并仅报告新违规。

**使用基线：**

```sh
swiftlint --baseline .swiftlint.baseline
```

在 CI 中，传递 `--baseline`，以便只有新违规会导致构建失败。通过修复遗留违规并重新生成，逐步减少基线。

有关基线工作流程和发布策略，请参阅 [参考资料/rules-suppressions-and-baselines.md](references/rules-suppressions-and-baselines.md)。

## 自动修正

SwiftLint 可以自动修复某些违规：

```sh
swiftlint --fix
# 或遗留别名：
swiftlint --autocorrect
```

**警告：**

- **永远不要将 `--fix` 作为预编译构建阶段运行。** 自动修复会修改源文件。如果每次构建都自动运行，这会创建不可预测的编辑-构建循环，并可能掩盖真实问题。
- 手动运行 `--fix` 或在专用 CI 步骤中运行，然后审查差异。
- 并非所有规则都支持自动修正。检查 `swiftlint rules` — “可修正”列显示哪些规则可以自动修复。
- 运行 `--fix` 前始终提交或暂存。

## CI 集成

CI 是主要的强制执行表面。CI 检查可确保没有人合并会增加违规计数的代码。

**推荐的 CI 模式：**

```yaml
# GitHub Actions 示例
- name: Lint
  run: |
    brew install swiftlint
    swiftlint --strict --reporter sarif > swiftlint.sarif
```

关键 CI 选项：

| 标志 | 效果 |
|------|--------|
| `--strict` | 在警告（而不仅仅是错误）时退出非零 |
| `--reporter sarif` | GitHub 高级安全兼容的输出 |
| `--reporter json` | 机器可读的输出 |
| `--reporter checkstyle` | Jenkins/SonarQube 兼容 |
| `--baseline .swiftlint.baseline` | 仅在新违规时失败 |

对于上传到 GitHub 代码扫描的 SARIF，在 lint 步骤后添加 `github/codeql-action/upload-sarif`。

在配置、基线或规则更改后，在本地或验证作业中运行确切的 CI lint 命令。在非零退出时，检查并修复新违规，然后重新运行相同的命令直到通过；不要仅仅为了隐藏失败而重新生成基线。

有关完整的 CI 配方和报告器细节，请参阅 [参考资料/plugins-run-scripts-and-integrations.md](references/plugins-run-scripts-and-integrations.md)。

## 集成决策树

根据项目结构选择如何运行 SwiftLint：

| 场景 | 推荐集成 |
|----------|------------------------|
| SwiftPM 包或具有 `Package.swift` 的 Xcode 项目 | 通过 `SwiftLintPlugins` 的构建工具插件 |
| 需要 CLI 标志 (`--fix`，`--baseline`) 的 SwiftPM 项目 | 命令插件：`swift package plugin swiftlint` |
| 没有 SwiftPM 的 Xcode 项目，团队使用 Homebrew | 运行脚本构建阶段 |
| CI/CD 管道 | Homebrew 或 Docker 安装，直接运行 `swiftlint` |
| 预提交钩子 | Homebrew 安装 + `.pre-commit-config.yaml` 或 git 钩子脚本 |

构建工具插件对于本地开发是首选的，因为它不需要 PATH 配置，通过包解析固定 SwiftLint 版本，并在构建时自动运行。

有关每个集成的详细设置说明，请参阅 [参考资料/plugins-run-scripts-and-integrations.md](references/plugins-run-scripts-and-integrations.md)。

## 多个配置

SwiftLint 支持分层配置文件。子目录中的 `.swiftlint.yml` 会继承并覆盖父配置。

常见模式：

- **宽松的测试配置**：在 `Tests/` 中放置一个 `.swiftlint.yml`，禁用 `force_unwrapping` 并提高 `file_length`
- **严格的模块配置**：在共享模块目录中放置一个更严格的 `.swiftlint.yml`
- **远程配置**：使用 `parent_config` 与 HTTPS URL 拉取共享团队配置（支持缓存）

```yaml
# Tests/.swiftlint.yml — 子配置
disabled_rules:
  - force_unwrapping
  - force_try

file_length:
  warning: 800
```

您还可以在 CLI 中传递多个配置：

```sh
swiftlint --config .swiftlint.yml --config .swiftlint-extra.yml
```

较后的配置会覆盖先前的配置中的重叠键。

有关嵌套配置解析、远程配置和 CLI 多配置细节，请参阅 [参考资料/adoption-and-configuration.md](references/adoption-and-configuration.md)。

## 常见错误

1. **在构建阶段运行 `--fix`。** 在每次构建时自动修复会创建不可预测的源修改。手动运行 `--fix`。

2. **在不知道影响的情况下使用 `only_rules`。** 这会禁用所有规则，除了列出的规则。大多数团队应使用 `disabled_rules` + `opt_in_rules`。

3. **使用 `// swiftlint:disable all` 抑制并忘记重新启用。** 这会静默禁用文件其余部分的 linting。

4. **没有固定 SwiftLint 版本。** 不同版本具有不同的默认规则。使用构建工具插件（通过 SPM 固定）或在您的 `Brewfile` / CI 配置中固定。

5. **过于广泛地排除。** 完全排除 `Tests/` 意味着测试代码没有 linting。使用具有宽松规则的子配置代替。

6. **忽略工具链不匹配。** SwiftLint 必须使用（或兼容）与您的项目编译相同的 Swift 工具链构建。不匹配会导致解析错误。有关多工具链指导，请参阅 [参考资料/plugins-run-scripts-and-integrations.md](references/plugins-run-scripts-and-integrations.md)。

7. **在大型代码库中一次性采用太多 opt-in 规则。** 这会创建过多的违规。逐个添加规则并使用基线。

8. **没有配置 `included` 路径。** 如果没有 `included`，SwiftLint 会递归扫描工作目录，这可能会选中托管的或生成的代码。

## 审查清单

- [ ] `.swiftlint.yml` 存在于项目根目录，具有明确的 `included`/`excluded` 路径
- [ ] SwiftLint 版本已固定（通过 SPM 插件解析、Brewfile 或 CI 配置）
- [ ] 为每个应进行 linting 的目标启用了构建工具插件
- [ ] CI 运行 `swiftlint --strict`（或使用 `--baseline` 进行渐进式采用）
- [ ] 基线不会无意中增长，并且在下一个规则或清理批次之前 CI 是绿色的
- [ ] 构建 阶段中没有 `--fix` / `--autocorrect`
- [ ] 内联抑制针对特定规则，而不是 `all`
- [ ] 内联抑制包括解释原因的注释
- [ ] 测试目标具有适当的配置（通过子配置进行宽松规则，而不是完全排除）
- [ ] 自动修正更改在一个单独的提交中审查
- [ ] 新 opt-in 规则逐个添加，并获得团队共识

## 参考资料

- [参考资料/adoption-and-configuration.md](references/adoption-and-configuration.md) — 安装路径、`.swiftlint.yml` 深入探讨、严重性调整、环境变量、嵌套/远程配置、发布策略
- [参考资料/plugins-run-scripts-and-integrations.md](references/plugins-run-scripts-and-integrations.md) — 构建工具插件、命令插件、运行脚本、CI 配方、多工具链指导、VS Code、Fastlane、Docker、pre-commit
- [参考资料/rules-suppressions-and-baselines.md](references/rules-suppressions-and-baselines.md) — 默认与 opt-in 与分析器规则、抑制语法、基线工作流程、误报处理
- [参考资料/rule-reference.md](references/rule-reference.md) — 本地查找的捆绑完整规则索引；通过 `swiftlint rules` 或官方规则目录验证当前细节
- [参考资料/custom-rules-and-analyze.md](references/custom-rules-and-analyze.md) — 正则表达式自定义规则、Swift 自定义规则（简要）、`swiftlint analyze`、编译器日志工作流程
- [SwiftLint 文档](https://realm.github.io/SwiftLint/) — 官方文档
- [SwiftLint 规则目录](https://realm.github.io/SwiftLint/rule-directory.html) — 完整分类规则列表
- [SimplyDanny/SwiftLintPlugins](https://github.com/SimplyDanny/SwiftLintPlugins) — 推荐的插件包
