---
name: quarto-authoring
description: 当用户明确使用 Quarto、.qmd 文件、_quarto.yml、Quarto 项目或 Quarto 特性（如引用、交叉引用、引用、Mermaid 图表、扩展、网站、书籍、演示文稿和报告）时使用。也用于从 R Markdown、bookdown、blogdown、xaringan、distill 或 Jupyter 笔记本明确迁移到或与 Quarto 进行比较。除非明确提及 Quarto 或迁移到 Quarto，否则不要用于一般 R Markdown 或相关格式的问题。
---

# Quarto 编写

> 此技能基于 Quarto CLI v1.9.36 (2026-03-24)。

## 何时使用什么

任务：编写新的 Quarto 文档
使用：遵循下方的“QMD 基础”，然后查看具体的参考文件

任务：添加交叉引用
使用：[references/cross-references.md](references/cross-references.md)

任务：配置代码单元格
使用：[references/code-cells.md](references/code-cells.md)

任务：添加带标题的图表
使用：[references/figures.md](references/figures.md)

任务：创建表格
使用：[references/tables.md](references/tables.md)

任务：添加引文和参考文献
使用：[references/citations.md](references/citations.md)

任务：添加注释块
使用：[references/callouts.md](references/callouts.md)

任务：添加图表（Mermaid, Graphviz）
使用：[references/diagrams.md](references/diagrams.md)

任务：控制页面布局
使用：[references/layout.md](references/layout.md)

任务：使用简码
使用：[references/shortcodes.md](references/shortcodes.md)

任务：添加条件内容
使用：[references/conditional-content.md](references/conditional-content.md)

任务：使用 divs 和 spans
使用：[references/divs-and-spans.md](references/divs-and-spans.md)

任务：配置 YAML 前置内容
使用：[references/yaml-front-matter.md](references/yaml-front-matter.md)

任务：查找和使用扩展
使用：[references/extensions.md](references/extensions.md)

任务：应用 markdown 语法检查规则
使用：[references/markdown-linting.md](references/markdown-linting.md)

任务：选择或配置计算引擎（knitr, jupyter, julia）
使用：[references/engines.md](references/engines.md)

### 迁移（仅当转换现有项目时）

编写新的 Quarto 文档时，请勿阅读这些参考。
用户明确要求转换或迁移现有项目时，仅阅读与源格式匹配的参考。

- R Markdown (.Rmd) 到 Quarto：[references/conversion-rmarkdown.md](references/conversion-rmarkdown.md)
- bookdown 项目：[references/conversion-bookdown.md](references/conversion-bookdown.md)
- xaringan 幻灯片：[references/conversion-xaringan.md](references/conversion-xaringan.md)
- distill 文章：[references/conversion-distill.md](references/conversion-distill.md)
- blogdown 网站：[references/conversion-blogdown.md](references/conversion-blogdown.md)
- Jupyter 笔记本 (.ipynb) 到/从 Quarto：[references/conversion-jupyter.md](references/conversion-jupyter.md)

## QMD 基础

### 基本文档结构

```markdown
---
title: "Document Title"
author: "Author Name"
date: today
format: html
---

Content goes here.
```

Quarto 文档由两部分组成：

1. **YAML 前置内容**：位于顶部的元数据和配置，用 `---` 包围。
2. **Markdown 内容**：使用标准 Markdown 语法的主正文。

### Divs 和 Spans

Divs 使用三冒号分隔符：

```markdown
::: {.class-name}
Content inside the div.
:::
```

Spans 使用括号语法：

```markdown
This is [important text]{.highlight}.
```

详情：[references/divs-and-spans.md](references/divs-and-spans.md)

### 代码单元格选项语法

代码单元格以三个反引号开头，并在花括号中包含语言标识符。
代码单元格是可执行的代码块，用于生成输出。

Quarto 使用语言的注释符号 + `|` 表示单元格选项。选项使用**短横线，而不是点**（例如，`fig-cap` 而不是 `fig.cap`）。

- R, Python, Julia：`#|`
- Mermaid：`%%|`
- Graphviz/DOT：`//|`

````markdown
```{language}
#| label: fig-example
#| echo: false
#| fig-cap: "A scatter plot example."

# code that produces a figure
```
````

在 YAML 前置内容中设置文档级默认值：

```yaml
execute:
  echo: false
  warning: false
```

**缓存——关键引擎差异**：仅建议 `#| cache: true` 用于 R 代码单元格（knitr 引擎）。
不要为其他语言单元格建议它——它不起作用，将被静默忽略。
唯一正确的方法是在使用非 `knitr` 引擎时，在顶层 YAML 前置内容中设置 `execute: cache: true`。
Python/Jupyter 需要 `jupyter-cache` (`pip install jupyter-cache`)：

```yaml
execute:
  cache: true
```

详情：[references/code-cells.md](references/code-cells.md)

### 交叉引用

标签必须以类型前缀开头。使用 `@` 引用：

- 图表：`fig-` 前缀，例如，`#| label: fig-plot` → `@fig-plot`
- 表格：`tbl-` 前缀，例如，`#| label: tbl-data` → `@tbl-data`
- 部分：`sec-` 前缀，例如，`{#sec-intro}` → `@sec-intro`
- 方程式：`eq-` 前缀，例如，`{#eq-model}` → `@eq-model`

````markdown
```{language}
#| label: fig-plot
#| fig-cap: "A caption for the plot."

# code that produces a figure
```

See @fig-plot for the results.
````

详情：[references/cross-references.md](references/cross-references.md)

### 注释块

五种类型：`note`, `warning`, `important`, `tip`, `caution`。

```markdown
::: {.callout-note}
This is a note callout.
:::

::: {.callout-warning}

## Custom Title

This is a warning with a custom title.

:::
```

详情：[references/callouts.md](references/callouts.md)

### 图表

```markdown
![Caption text](image.png){#fig-name fig-alt="Alt text"}
```

子图表：

```markdown
::: {#fig-group layout-ncol=2}
![Sub caption 1](image1.png){#fig-sub1}

![Sub caption 2](image2.png){#fig-sub2}

Main caption for the group.
:::
```

详情：[references/figures.md](references/figures.md)

### 表格

```markdown
::: {#tbl-example}

| Column 1 | Column 2 |
| -------- | -------- |
| Data 1   | Data 2   |

Table caption.
:::
```

详情：[references/tables.md](references/tables.md)

### 引文

```markdown
According to @smith2020, the results show...
Multiple citations [@smith2020; @jones2021].
```

在 YAML 中配置：

```yaml
bibliography: references.bib
csl: apa.csl
```

详情：[references/citations.md](references/citations.md)

## 常见工作流

### 创建 HTML 文档

```yaml
title: "My Report"
author: "Your Name"
date: today
format:
  html:
    toc: true
    code-fold: true
    theme: cosmo
```

### 创建 PDF 文档

```yaml
title: "My Report"
format:
  pdf:
    documentclass: article
    papersize: a4
```

### 创建 RevealJS 演示文稿

```markdown
---
title: "My Presentation"
format: revealjs
---

## First Slide

Content here.

## Second Slide

More content.
```

### 设置 Quarto 项目

在项目根目录下创建 `_quarto.yml`：

```yaml
project:
  type: website

website:
  title: "My Site"
  navbar:
    left:
      - href: index.qmd
        text: Home
      - href: about.qmd
        text: About

format:
  html:
    theme: cosmo
```

## 资源

- [Quarto 文档](https://quarto.org/docs/)
- [Quarto 指南](https://quarto.org/docs/guide/)
- [Quarto 扩展](https://quarto.org/docs/extensions/)
- [社区扩展列表](https://m.canouil.dev/quarto-extensions/)
