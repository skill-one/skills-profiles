# typst-author 技能

## 概述

此技能帮助智能体生成、编辑和推理 Typst 文档。它提供快速入门示例、详细的工作流程以及指向完整 Typst 文档（指南、教程、参考）的链接。

## 最小文档示例

```typst
#set document(title: "我的文档", author: "作者姓名")
#set page(numbering: "1")
#set text(lang: "zh")

// 启用段落对齐和字符级对齐
#set par(
  justify: true,
  justification-limits: (
    tracking: (min: -0.012em, max: 0.012em),
    spacing: (min: 75%, max: 120%),
  )
)

#title[我的文档]

= 标题 1

这是一个 Typst 中的段落。

== 标题 2

#lorem(50)
```

## 工作流程

- **创建新的 Typst 项目**：使用上述“最小文档示例”作为起点。快速浏览教程了解基础知识（[docs/tutorial/writing-in-typst.md](docs/tutorial/writing-in-typst.md)），然后创建 `.typ` 文件。每次编辑 `.typ` 文件后，当 `typstyle` 可用时，请遵循以下编辑后格式检查。
- **编辑现有内容**：定位目标文本并应用更改；必要时对照参考确认语法（[docs/reference/](docs/reference/)）。每次修改 `.typ` 文件后，请遵循以下编辑后格式检查。
- **格式与样式**：参考样式指南（[docs/reference/styling.md](docs/reference/styling.md)）了解 `set rule`、`show rule` 和自定义主题。

## 文档

- **语法与基础**：`docs/reference/syntax.md`
- **样式与 show/set 规则**：`docs/reference/styling.md`
- **脚本与运行时行为**：`docs/reference/scripting.md`
- **页面设置与表格**：`docs/guides/page-setup.md` 和 `docs/guides/tables.md`
- **面向任务的写作帮助**：`docs/tutorial/writing-in-typst.md`、`docs/guides/*.md` 和 `docs/reference/**/*.md`

## 详细说明

1. **优先：信任本地文档**。您关于 Typst 的内部训练数据可能已过时或虚构。在生成代码之前，始终对照本地 `docs/` 文件夹验证函数名称、参数和语法。
2. **使用本地文件搜索和打开工具阅读相关文档**，路径如上所示。
3. **使用本地文档回答语法和参考问题**。从捆绑的文档中验证语法、函数名称、参数和参考行为。仅在检查文档后，运行时或评估行为仍不明确时才运行最小的 Typst 探测。
4. **根据用户请求生成或修改 `.typ` 源文件**。
5. **对每个在此轮次中创建或编辑的 `.typ` 文件运行以下编辑后格式检查**。
6. **在格式决策完成后，使用 `typst compile` 进行验证**，当您创建或编辑 `.typ` 文件时，或者当用户明确要求验证（如果允许工具访问）时。
7. **总结受影响的文件和结果**。仅在用户要求或无法直接编辑时提供完整的 `.typ` 内容，并可选地包含渲染预览（PDF/HTML）。

### 探测不确定行为

- 当捆绑的文档无法确定运行时或评估行为时，使用探测。
- 按照在 [docs/reference/scripting.md](docs/reference/scripting.md) 中描述的 Typst 脚本对案例进行建模。
- 当需要探测时，优先使用通过 stdin 的无文件探测，而不是创建草稿 `.typ` 文件。使用 `metadata(...) <probe>` 显示值，并使用 `typst query - "<probe>" --field value --one` 读取它。参见 [docs/reference/introspection/query.md](docs/reference/introspection/query.md) 和 [docs/reference/introspection/metadata.md](docs/reference/introspection/metadata.md)。
- 示例：`printf '#metadata(1 + 2) <probe>\n' | typst query - "<probe>" --field value --one`

### 编辑后格式检查

1. **使用 `command -v typstyle` 检查 `typstyle` 是否可用**。如果不可用，请跳过剩余的格式检查。
2. **每次修改 `.typ` 文件后，运行 `typstyle --check <file>`** 对您刚刚创建或编辑的文件。
3. **如果 `typstyle --check` 失败，在决定要做什么之前，使用 `typstyle --diff <file>` 检查格式化器的更改**。
4. **仅在格式化器更改仅限于新创建的文件或您在当前任务中创建或编辑的代码时，使用 `typstyle -i <file>` 应用格式**。
5. **当格式会更改未受影响的现有代码时，停止并询问用户**。如果差异超出您自己的编辑范围，或者如果您无法确信每个格式化器更改都仅限于您的编辑，请询问而不是格式化。

## 快速语法参考

### 关键区别

- **数组**：`(item1, item2)`（括号）。参见 [docs/reference/foundations/array.md](docs/reference/foundations/array.md)。
- **字典**：`(key: value, key2: value2)`（带冒号的括号）。参见 [docs/reference/foundations/dictionary.md](docs/reference/foundations/dictionary.md)。
- **内容块**：`[markup content]`（方括号）。参见 [docs/reference/foundations/content.md](docs/reference/foundations/content.md)。
- **没有元组**：Typst 只有数组。

### 哈希用法（标记与代码）

- 使用 `#` 在标记或内容块内开始代码表达式；它区分代码和文本。这对于标记中的内容生成函数调用和字段访问是必需的：`#figure[...]`、`#image("file.png")`、`text(...)[#numbering(...)]`。
- 不要在代码上下文中使用 `#`（参数列表、代码块、show-rule 正文）。示例：`#figure(image("file.png"))`（`image` 前面没有 `#`）。
- 参考：[docs/reference/scripting.md](docs/reference/scripting.md)、[docs/tutorial/writing-in-typst.md](docs/tutorial/writing-in-typst.md)

```typst
// 错误（内容块内缺少 #）
text(...)[(numbering(...))]

// 正确
text(...)[(#numbering(...))]
```

### 样式规则：set 与 show

- `set`：设置规则用于配置元素函数的可选参数（样式默认范围限于当前块或文件）。
- `show`：显示规则用于定位选定的元素并应用设置规则或转换/替换元素输出。
- 使用 `set` 进行常规样式；使用 `show` 进行选择性或结构性更改（例如，`heading.where(level: 1)`、标签、文本、正则表达式）。

```typst
// 设置规则：配置元素类型的可选参数
#set heading(numbering: "I.")
#set text(font: "New Computer Modern")

// 显示-设置规则：仅对选定元素应用设置规则
#show heading: set text(navy)

// 显示转换规则：替换/重塑元素输出
#show heading: it => block[#emph(it.body)]
```

## 常见错误避免

- 称之为“元组”（Typst 只有数组）。
- 使用 `[]` 表示数组（应使用 `()`）。
- 使用 `arr[0]` 访问数组元素（应使用 `arr.at(0)`）。
- 在标记/内容块中省略 `#`（例如，`text(...)[numbering(...)]` 应为 `text(...)[#numbering(...)]`）。
- 在代码上下文中使用 `#`（例如，在参数列表中 `figure(#image("x.png"))`）。
- 混淆内容块 `[]` 与代码块 `{}`。
- 忘记在访问导入的变量/函数时包含命名空间（例如，使用 `color.hsl` 而不是仅 `hsl`）。
- 使用 LaTeX 语法（**不要**使用 `\begin{...}`、`\section` 或其他 LaTeX 命令）。
- 虚构环境（例如，`tabular` 不存在；使用 `table`）。

## 高级功能

- **自定义主题**：参见 [docs/reference/styling.md](docs/reference/styling.md) 了解主题创建。
- **脚本**：使用 Typst 的脚本功能（[docs/reference/scripting.md](docs/reference/scripting.md)）进行自动生成。
- **数学和可视化**：参考 [docs/reference/math/](docs/reference/math/) 和 [docs/reference/visualize/](docs/reference/visualize/) 了解公式和图表。

### 对于大型项目

在处理大型项目时，请考虑将项目组织到多个文件中。

- 使用 `#include "file.typ"` 分割到多个文件
- 相关文档：[docs/reference/foundations/module.md](docs/reference/foundations/module.md)

## 故障排除

### 缺失字体警告

如果您看到“未知字体族”警告，请移除字体规范以使用系统默认字体。注意：字体警告不会阻止编译；文档将使用备用字体。

### 模板/包未找到

如果导入失败并显示“包未找到”：

- 验证 Typst Universe 上的确切包名称和版本。
- 检查 `@preview/package:version` 语法中的拼写错误。

### 编译错误

常见修复：

- **"expected content, found ..."**：您在期望标记的地方使用了代码 - 用 `#{ }` 包裹或使用正确的语法。
- **"expected expression, found ..."**：在标记/内容块中缺少 `#`（或 `#(...)`）。
- **"unknown variable"**：检查拼写，确保导入正确。
- **数组/字典错误**：检查语法 - 使用 `()` 表示两者，字典需要 `key: value`，单元素数组是 `(elem,)`。
