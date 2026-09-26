# 专业PDF生成器

该技能使用pandoc和typst将Markdown文件转换为专业排版PDF白皮书。

## 资产

该技能包含（位于插件根目录）：
- **Typst模板**：`templates/whitepaper.typ`
- **Source Sans 3字体**：`fonts/` — 支持所有字重的可变字体（来自Google Fonts的开源字体）
- **Source Code Pro字体**：`fonts/`（常规、粗体、斜体、粗斜体）——用于代码块和行内代码

**插件根目录**：插件根目录是动态确定的（见下文步骤2.5）

### 字体层级

| 元素 | 字重 | 样式 |
|------|------|------|
| 标题（H1） | 黑色（900） | 大号、紧密跟踪 |
| 章节标题（H2） | 粗体（700） | 蓝色强调线 |
| 副标题（H3、H4） | 粗体（700） | 中等大小 |
| 正文 | 常规（400） | 两端对齐、舒适的行距 |
| 代码 | Source Code Pro | 等宽字体 |

## 关键：完全自动执行

**此技能完全无人值守运行。请不要：**
- 在生成PDF之前询问"是否继续"
- 在清理之前询问"是否删除这些文件"
- 在任何步骤中询问"可以吗"
- 在步骤之间等待用户确认
- 暂停以显示中间结果
- 请求文件操作权限

**必须行为：**
- 顺序执行所有步骤，不得中断
- 调用时立即生成PDF
- 创建PDF后立即删除所有源文件
- 仅在所有操作完成后与用户通信
- 报告最终结果："PDF创建：[路径]"

**如果在PDF生成或清理过程中，您发现自己即将向用户提问，请停止并直接执行操作。**

## 使用方法

当用户要求创建PDF时，请按照以下步骤操作：

### 1. 确定输入和输出

- 解析`$ARGUMENTS`以获取输入的Markdown文件和可选的输出PDF路径
- 如果未给出输出路径，则使用与输入文件相同的名称，但扩展名为`.pdf`
- 如果未给出输入，请询问用户要转换哪个Markdown文件
- 检查文件的YAML前文（见下文"前文参考"）。如果缺少`title`，请在继续前询问用户标题。如果缺少`date`，则默认为当前日期。

### 2. 安装依赖项（如果缺失）

为每个缺失的工具运行——脚本会自动检测平台：

```bash
OS=$(uname -s)
# pandoc
command -v pandoc >/dev/null 2>&1 || {
  [ "$OS" = "Darwin" ] && brew install pandoc || sudo apt-get update && sudo apt-get install -y pandoc
}
# typst
command -v typst >/dev/null 2>&1 || {
  [ "$OS" = "Darwin" ] && brew install typst || {
    curl -fsSL https://github.com/typst/typst/releases/latest/download/typst-x86_64-unknown-linux-musl.tar.xz \
      | tar xJ --strip-components=1 -C /usr/local/bin/ typst-x86_64-unknown-linux-musl/typst
    chmod +x /usr/local/bin/typst
  }
}
```

### 2.5 定位插件根目录

**关键：在复制资产之前确定插件根目录。**

插件根目录包含`templates/`和`fonts/`目录。使用此单个命令：

```bash
PLUGIN_ROOT=$([ -d ".claude/plugins/project-management" ] && echo ".claude/plugins/project-management" || echo "$CLAUDE_PLUGIN_ROOT")
echo "使用插件根目录：$PLUGIN_ROOT"
ls "$PLUGIN_ROOT/templates/whitepaper.typ" || echo "错误：模板未找到！"
```

**预期位置：** `.claude/plugins/project-management`

### 3. 将模板复制到输出目录

将typst模板复制到输出PDF的同一目录：

```bash
PLUGIN_ROOT=$([ -d ".claude/plugins/project-management" ] && echo ".claude/plugins/project-management" || echo "$CLAUDE_PLUGIN_ROOT")
cp "$PLUGIN_ROOT/templates/whitepaper.typ" <output-directory>/whitepaper.typ
```

将`<output-directory>`替换为PDF生成的目录（例如，`project-guides/`）。

### 4. 运行Pandoc

使用以下确切标志执行转换。从输出目录运行，以便找到模板：

```bash
cd <output-directory> && \
PLUGIN_ROOT=$(if [ -d "../.claude/plugins/project-management" ]; then echo "../.claude/plugins/project-management"; elif [ -d ".claude/plugins/project-management" ]; then echo ".claude/plugins/project-management"; else echo "$CLAUDE_PLUGIN_ROOT"; fi) && \
TYPST_FONT_PATHS="$PLUGIN_ROOT/fonts" pandoc <input.md> \
  -o <output.pdf> \
  --pdf-engine=typst \
  -V template="whitepaper.typ" \
  -V mainfont="Source Sans 3" \
  -V fontsize=10pt \
  -V papersize=a4
```

**`project-guides/ADMIN-GUIDE.md`的示例：**
```bash
cd content && \
PLUGIN_ROOT=$([ -d "../.claude/plugins/project-management" ] && echo "../.claude/plugins/project-management" || echo "$CLAUDE_PLUGIN_ROOT") && \
TYPST_FONT_PATHS="$PLUGIN_ROOT/fonts" pandoc ADMIN-GUIDE.md -o ADMIN-GUIDE.pdf --pdf-engine=typst -V template="whitepaper.typ" -V mainfont="Source Sans 3" -V fontsize=10pt -V papersize=a4
```

注意：**不要**传递`--toc`——模板会生成自己的目录页，并具有正确的样式。

### 5. 清理（强制执行 - 不得跳过）

**关键：您必须在PDF生成后立即执行清理。仅保留PDF。**

```bash
# 使用单个命令删除所有中间文件
rm -f <output-directory>/whitepaper.typ <input.md> <input-without-extension>.plain.html <input-without-extension>.html
```

**`project-guides/AUTHOR-GUIDE.md`的示例清理：**
```bash
rm -f project-guides/whitepaper.typ project-guides/AUTHOR-GUIDE.md project-guides/AUTHOR-GUIDE.plain.html project-guides/AUTHOR-GUIDE.html
```

**清理后，仅应存在`project-guides/AUTHOR-GUIDE.pdf`。不应有`.md`、`.html`或`.plain.html`文件。**

### 6. 报告结果

```
"PDF创建：[output.pdf]"
```

## 前文参考

模板从Markdown文件中读取pandoc YAML前文，以填充标题页和页脚。前文块必须是文件中绝对的第一件事，由`---`行分隔。

### 必填字段

| 字段 | 目的 | 示例 |
|------|------|------|
| `title` | 封面页标题、PDF元数据 | `"AEM Code Sync for Edge Delivery Services"` |

### 推荐字段

| 字段 | 目的 | 示例 |
|------|------|------|
| `subtitle` | 封面第二行、强调线下方 | `"Technical Architecture and Security Documentation"` |
| `date` | 封面页和页脚 | `"January 29, 2026"` |

### 可选字段

| 字段 | 目的 | 示例 |
|------|------|------|
| `author` | 封面页上的作者列表 | 见下方结构化示例 |

### 最小示例

```yaml
---
title: "AEM Code Sync for Edge Delivery Services"
subtitle: "Technical Architecture and Security Documentation"
date: "January 29, 2026"
---
```

### 带作者的完整示例

```yaml
---
title: "AEM Code Sync for Edge Delivery Services"
subtitle: "Technical Architecture and Security Documentation"
date: "January 29, 2026"
author:
  - name: "Jane Smith"
    affiliation: "Edge Delivery Services"
  - name: "John Doe"
    affiliation: "Security Engineering"
---
```

### 模板渲染的内容

- **标题**：封面上的大号黑色权重文本
- **副标题**：强调分隔线下方的浅色文本
- **日期**：显示在封面上，并在页脚中显示
- **作者**：在封面上列出，可选的隶属关系

### 常见错误

- 将前文放在标题或空行之后（它必须是文件中的第一件事）
- 使用未加引号的包含冒号的字符串，例如`title: AEM: A Guide`——用引号括起来
- 在前文中添加pandoc变量，如`fontsize`或`papersize`——将它们作为`-V`标志传递给pandoc（该技能会自动处理）

## 模板设计

模板提供专业文档格式：
- **专业排版**使用Source Sans 3（来自Google Fonts的开源字体）
- **蓝色强调色**（#0066cc）用于章节分隔线和链接
- **干净的页眉**包含标题/副标题（无分隔线）
- **页脚**包含日期和页码（在标题页上隐藏）
- **Source Code Pro**用于代码块和行内代码
- **自动目录页**
- **标题页**带强调分隔线

### 模板功能

| 功能 | 描述 |
|------|------|
| 标题页 | 干净的设计，包含标题、副标题、日期、作者 |
| 目录 | 在第2页自动生成 |
| H1标题 | 黑色权重，标题前换页 |
| H2标题 | 带蓝色强调线的粗体 |
| 代码块 | 灰色背景，圆角 |
| 引用块 | 蓝色左边界，浅蓝色背景 |
| 表格 | 浅色边框，粗体标题行 |
| 链接 | 蓝色（#0066cc） |

## 定制文档

用户可以使用`-V key=value`覆盖pandoc变量：

| 变量 | 默认值 | 描述 |
|------|--------|------|
| `papersize` | `a4` | 页面大小（`a4`、`us-letter`等） |
| `fontsize` | `10pt` | 基础字体大小 |
| `template` | `whitepaper.typ` | Typst模板文件 |
| `mainfont` | `Source Sans 3` | 正文字体 |

## 要求

- `pandoc`和`typst`必须已安装（该技能在缺失时自动安装它们）
  - **macOS**：通过Homebrew（`brew`）
  - **Linux**：`pandoc`通过`apt-get`，`typst`通过GitHub发布二进制文件
- Source Sans 3字体包含在插件的`fonts/`目录中

## 故障排除

如果typst找不到字体，请确保`TYPST_FONT_PATHS`环境变量设置正确：

```bash
export TYPST_FONT_PATHS=${CLAUDE_PLUGIN_ROOT}/fonts
```

| 问题 | 解决方案 |
|------|--------|
| 字体未找到 | 检查TYPST_FONT_PATHS指向插件的fonts/目录 |
| 模板未找到 | 确保whitepaper.typ已复制到输出目录 |
| 表格不换页 | 模板会自动处理 |
| 缺少标题页 | 检查前文是否有`title`字段 |
