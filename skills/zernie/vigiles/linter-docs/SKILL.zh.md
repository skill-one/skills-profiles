---
name: linter-docs
description: 深度lint工具参考，用于编写或调试vigiles enforce()规则——插件表、AST选择器、类型感知规则、自动修复，以及针对ESLint、Ruff、Pylint、RuboCop、Stylelint和Clippy的边缘案例。当您需要特定lint工具的确切规则名称或配置时使用，而不是用于运行lint工具。（JVM/Go lint工具——detekt、ktlint、Checkstyle、golangci-lint——以及Cedar目前还没有深度解析文件；它们的参考文档位于docs/linter-support.md中。）
---

linter vigiles 的参考材料交叉引用。当你需要精确的规则名称、AST 选择器或配置详细信息来编写 `enforce()` 规则（或诊断为什么某个规则被报告为缺失或禁用）时，请打开你正在使用的 linter 的文件。

| linter | 参考                                                                                   |
| ------ | ------------------------------------------------------------------------------------ |
| ESLint | [`eslint.md`](eslint.md) — 插件表格、AST 选择器、类型感知规则、自动修复             |
| Ruff   | [`ruff.md`](ruff.md) — 800多条重新实现的规则、选择、自动修复、pyproject 配置         |
| Pylint | [`pylint.md`](pylint.md) — 插件表格、astroid AST、类型推断、自定义检查器            |
| RuboCop| [`rubocop.md`](rubocop.md) — gem 表格、节点模式 DSL、自动纠正、自定义 cops          |
| Stylelint| [`stylelint.md`](stylelint.md) — 插件表格、PostCSS AST、自定义规则、SCSS            |
| Clippy | [`clippy.md`](clippy.md) — Rust 代码风格检查组及配置                                |

**JVM/Go 代码风格检查器（detekt、ktlint、Checkstyle、golangci-lint）和 Cedar** 通过 `enforce()` 进行交叉引用，但目前还没有在此处提供深入的文件——它们的特性、配置界面和已知限制（例如 ktlint 仅用于格式化，Checkstyle 启用状态仅限于白名单）在 [`docs/linter-support.md`](../../docs/linter-support.md) 中进行了说明。

当匹配指导规则到实际的代码风格检查器规则时，`strengthen` 和 `edit-spec` 技能会读取这些内容。这是一个用户触发的技能（参考而非操作），因此它不会自行触发——直接打开相关文件即可。
