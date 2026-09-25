# Typst

此技能适用于 Typst 0.15 及更高版本。对于 Typst 0.14.2，请使用 `typst-0.14.2` 仓库标签以获取先前技能快照。

## 编译

```bash
typst compile document.typ              # 一次性编译 → PDF
typst compile document.typ output.pdf   # 显式输出路径
typst compile document.typ -f png       # 导出为 PNG 图片
typst compile src/main.typ --root .     # 设置项目根目录以用于 /path 导入
typst watch document.typ                # 发生变化时重新编译
typst eval --in document.typ 'query(heading).len()'  # Typst 0.15+ 反射
```

对于此快速参考之外的命令选项，请参阅 [cli.md](cli.md)。

代理验证 — 根据您需要检查的内容选择（详细信息请参阅 [debug.md](debug.md)）：

| 方法      | 命令                                                                 | 最适用于                                  |
| ----------- | ----------------------------------------------------------------------- | ----------------------------------------- |
| HTML 导出 | `typst compile doc.typ /dev/stdout -f html --features html 2>/dev/null` | 文本内容、结构、标题、表格             |
| PNG 导出  | `typst compile doc.typ page-{p}.png -f png`                             | 视觉布局、对齐、间距、字体             |
| pdftotext   | `typst compile doc.typ && pdftotext doc.pdf -`                          | 作为特定页面内容的备用方案              |

## 最小文档

```typst
#set page(paper: "a4", margin: 2cm)
#set text(size: 11pt)

= 标题

内容放在这里。
```

## 编写文档

**开始一个新文档？** 从下方 [Examples](#examples) 处复制最接近的食谱 — 比空白开始更快，并且每一行都命名了下一个要阅读的文档。

| 当您需要...                                | 阅读                           |
| -------------------------------------------------- | ------------------------------ |
| 学习语法、导入、函数、控制流     | [basics.md](basics.md)         |
| 学习数据类型、运算符、字符串/数组方法  | [types.md](types.md)           |
| 样式页面、标题、图表、布局             | [styling.md](styling.md)       |
| 表格、网格、单元格跨度、边框、数据表格    | [tables.md](tables.md)         |
| 学术论文、参考文献、定理、方程式 | [academic.md](academic.md)     |
| 从 Markdown 或 LaTeX 转换                     | [conversion.md](conversion.md) |
| 升级旧的 Typst 代码，0.15 版本中断变化    | [migration.md](migration.md)   |
| 使用 Typst CLI 命令和构建选项           | [cli.md](cli.md)               |
| 从文档中提取数据、多遍构建     | [query.md](query.md)           |

## 开发包和模板

| 当您需要...                            | 阅读                       |
| ---------------------------------------------- | -------------------------- |
| 状态、计数器、文档内 `query()`、XML    | [advanced.md](advanced.md) |
| CLI 反射、元数据导出、多遍             | [query.md](query.md)       |
| 创建可重用的模板函数            | [template.md](template.md) |
| 创建或发布包                    | [package.md](package.md)   |
| 验证输出 (HTML/PNG/pdftotext, repr)       | [debug.md](debug.md)       |
| 分析性能 (--timings, hotspots)      | [perf.md](perf.md)         |

[basics.md](basics.md) 和 [types.md](types.md) 也是开发者的基础。

## 查找包

搜索 Typst Universe 包的嵌入式索引（每周更新）：

```bash
python3 scripts/search-packages.py "what you need"
python3 scripts/search-packages.py "chart" --category visualization
python3 scripts/search-packages.py --category cv --top 5
python3 scripts/search-packages.py --list-categories
```

## 常见错误

| 错误                                            | 原因                        | 修复                                                  |
| ------------------------------------------------ | ---------------------------- | ---------------------------------------------------- |
| "未知变量"                               | 未定义标识符         | 检查拼写，确保 `#let` 在使用前定义             |
| "期望 X，找到 Y"                            | 类型不匹配                | 检查文档中函数签名                                     |
| "文件未找到"                                 | 导入路径错误              | 路径相对于当前文件解析                                   |
| "未知字体"                                   | 字体未安装           | 使用系统字体或 Web 安全替代字体                      |
| "最大函数调用深度超出"           | 深度递归               | 使用迭代代替                                |
| "只能在上下文已知时使用"         | 缺少 `context` 包装器    | 包裹在 `context { ... }` 中                            |
| "意外的参数"                            | `=` 而不是 `:` 用于参数  | 命名参数使用 `:` 语法: `func(name: value)`       |
| "外部变量只读"           | 修改捕获的变量   | 使用循环累积或 `state()` — 请参阅 advanced.md |
| "期望内容，找到字符串" (或反之) | 内容/字符串类型不匹配 | 使用 `[#str-var]` 嵌入字符串到内容中          |
| set/show 规则无效                      | 规则放在内容之后    | 将 set/show 规则放在它们目标的内容之前          |

## 示例

复制最接近的启动模板，调整，编译。对于简历、信件或幻灯片，搜索包：`python3 scripts/search-packages.py --category cv`（或 `letter`，`presentation`）。

| 示例                                             | 当您需要...              | 下一步阅读                                        |
| --------------------------------------------------- | ---------------------------------------- | ------------------------------------------------ |
| [basic-document.typ](examples/basic-document.typ)   | 短笔记或备忘录                     | [basics.md](basics.md), [styling.md](styling.md) |
| [styled-document.typ](examples/styled-document.typ) | 带页面样式的多节报告             | [styling.md](styling.md), [tables.md](tables.md) |
| [template-report.typ](examples/template-report.typ) | 可重用的系列模板            | [template.md](template.md)                       |
| [tables-showcase.typ](examples/tables-showcase.typ) | 数据密集型文档 (表格、CSV/JSON)      | [tables.md](tables.md), [types.md](types.md)     |
| [academic-paper.typ](examples/academic-paper.typ)   | 带引用、定理、数学的论文   | [academic.md](academic.md)                       |
| [query-export.typ](examples/query-export.typ)       | 元数据导出或多遍构建     | [query.md](query.md)                             |
| [package-example/](examples/package-example/)       | 可发布的包                    | [package.md](package.md)                         |

## 依赖项

- **typst CLI 0.15+ 推荐**: 从 https://typst.app 或通过包管理器安装
  - macOS: `brew install typst`
  - Linux: `cargo install typst-cli`
  - Windows: `winget install typst`
- **pdftotext** (可选): 用于文本级输出验证
- **Python 3.10+** (可选): 用于包搜索和验证脚本
- **jq** (可选): 用于解析 `typst eval` 在 shell 脚本中的 JSON 输出

## API 参考 搜索

搜索 Typst API 函数、方法和构造函数的嵌入式索引：

```bash
python3 scripts/search-api.py "image width fit"
python3 scripts/search-api.py "color lighten" --kind method
python3 scripts/search-api.py --name str.position -v
python3 scripts/search-api.py "rightarrow" --kind symbol   # LaTeX 名称有效
python3 scripts/search-api.py --list-categories
```

## 生态系统工具

生态系统工具: **tinymist** (LSP/编辑器), **typstyle** (格式化器), **typst-package-check** (包验证器), **tytanic** (视觉测试运行器)。有关包工具的详细信息，请参阅 [package.md](package.md)。
