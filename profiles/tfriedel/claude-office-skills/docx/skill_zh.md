# DOCX 创建、编辑和分析

## 概述

用户可能会要求你创建、编辑或分析 .docx 文件的内容。.docx 文件本质上是一个包含 XML 文件和其他资源的 ZIP 压缩包，你可以读取或编辑这些内容。针对不同的任务，你有不同的工具和工作流程可供选择。

## 工作流程决策树

### 读取/分析内容
使用下方的“文本提取”或“原始 XML 访问”部分

### 创建新文档
使用“创建新 Word 文档”工作流程

### 编辑现有文档
- **自己的文档 + 简单修改**
  使用“基本 OOXML 编辑”工作流程

- **他人的文档**
  使用 **“修订工作流程”**（推荐默认设置）

- **法律、学术、商业或政府文档**
  使用 **“修订工作流程”**（必须使用）

## 读取和分析内容

### 文本提取
如果你只需要读取文档的文本内容，你应该使用 pandoc 将文档转换为 Markdown 格式。Pandoc 提供了出色的支持来保留文档结构，并且可以显示跟踪的更改：

```bash
# 将文档转换为带跟踪更改的 Markdown
pandoc --track-changes=all path-to-file.docx -o output.md
# 选项：--track-changes=accept/reject/all
```

### 原始 XML 访问
你需要原始 XML 访问来处理：评论、复杂格式、文档结构、嵌入媒体和元数据。对于这些功能中的任何一项，你都需要解包文档并读取其原始 XML 内容。

#### 解包文件
`python ooxml/scripts/unpack.py <office_file> <output_directory>`

#### 关键文件结构
* `word/document.xml` - 主要文档内容
* `word/comments.xml` - 文档.xml 中引用的评论
* `word/media/` - 嵌入的图像和媒体文件
* 跟踪更改使用 `<w:ins>`（插入）和 `<w:del>`（删除）标签

## 创建新 Word 文档

当从零开始创建新 Word 文档时，使用 **docx-js**，它允许你使用 JavaScript/TypeScript 创建 Word 文档。

### 工作流程
1. **必须 - 读取整个文件**：完整阅读 [`docx-js.md`](docx-js.md)（约 500 行）从头到尾。**永远不要在读取此文件时设置任何范围限制。** 在继续文档创建之前，请先阅读完整文件内容以了解详细语法、关键格式规则和最佳实践。
2. 使用 Document、Paragraph、TextRun 组件创建 JavaScript/TypeScript 文件（你可以假设所有依赖项都已安装，如果没有，请参考下面的依赖项部分）
3. 使用 Packer.toBuffer() 导出为 .docx

## 编辑现有 Word 文档

当编辑现有 Word 文档时，使用 **文档库**（一个用于 OOXML 操作的 Python 库）。该库自动处理基础设施设置并提供文档操作方法。对于复杂场景，你可以通过库直接访问底层 DOM。

### 工作流程
1. **必须 - 读取整个文件**：完整阅读 [`ooxml.md`](ooxml.md)（约 600 行）从头到尾。**永远不要在读取此文件时设置任何范围限制。** 请阅读完整文件内容以了解文档库 API 和直接编辑文档文件的 XML 模式。
2. 解包文档：`python ooxml/scripts/unpack.py <office_file> <output_directory>`
3. 使用文档库创建并运行 Python 脚本（见 ooxml.md 中的“文档库”部分）
4. 打包最终文档：`python ooxml/scripts/pack.py <input_directory> <office_file>`

文档库提供用于常见操作的高级方法，以及用于复杂场景的直接 DOM 访问。

## 用于文档审阅的修订工作流程

此工作流程允许你使用 Markdown 规划全面的跟踪更改，然后再在 OOXML 中实现它们。**关键**：为了实现完整的跟踪更改，你必须系统地实现所有更改。

**批量策略**：将相关的更改分组为 3-10 个更改的批次。这使调试变得容易，同时保持效率。在移动到下一个批次之前测试每个批次。

**原则：最小化、精确的编辑**
在实现跟踪更改时，只标记实际发生更改的文本。重复不变的文本使编辑更难审查，并且看起来不专业。将替换分解为：[不变的文本] + [删除] + [插入] + [不变的文本]。通过从原始中提取 `<w:r>` 元素并重新使用它来保留原始运行的建议的 RSID。

示例 - 在句子中更改“30 天”为“60 天”：
```python
# BAD - 替换整个句子
'<w:del><w:r><w:delText>The term is 30 days.</w:delText></w:r></w:del><w:ins><w:r><w:t>The term is 60 days.</w:t></w:r></w:ins>'

# GOOD - 仅标记更改内容，保留原始 <w:r> 以用于不变的文本
'<w:r w:rsidR="00AB12CD"><w:t>The term is </w:t></w:r><w:del><w:r><w:delText>30</w:delText></w:r></w:del><w:ins><w:r><w:t>60</w:t></w:r></w:ins><w:r w:rsidR="00AB12CD"><w:t> days.</w:t></w:r>'
```

### 跟踪更改工作流程

1. **获取 Markdown 表示形式**：使用 pandoc 保留跟踪更改将文档转换为 Markdown：
   ```bash
   pandoc --track-changes=all path-to-file.docx -o current.md
   ```

2. **识别和分组更改**：审查文档并识别所有需要的更改，将它们组织成逻辑批次：

   **位置方法**（用于在 XML 中查找更改）：
   - 章节/标题编号（例如，“第 3.2 章”，“第 IV 条”）
   - 如果编号，则使用段落标识符
   - 具有唯一周围文本的 Grep 模式
   - 文档结构（例如，“第一段”，“签名块”）
   - **不要使用 Markdown 行号** - 它们不映射到 XML 结构

   **批量组织**（每个批次分组 3-10 个相关更改）：
   - 按章节： "批次 1：第 2 章修订案"，"批次 2：第 5 章更新"
   - 按类型： "批次 1：日期更正"，"批次 2：当事人名称更改"
   - 按复杂性： 从简单的文本替换开始，然后处理复杂的结构更改
   - 顺序： "批次 1：第 1-3 页"，"批次 2：第 4-6 页"

3. **阅读文档和解包**：
   - **必须 - 读取整个文件**：完整阅读 [`ooxml.md`](ooxml.md)（约 600 行）从头到尾。**永远不要在读取此文件时设置任何范围限制。** 特别注意“文档库”和“跟踪更改模式”部分。
   - **解包文档**：`python ooxml/scripts/unpack.py <file.docx> <dir>`
   - **注意建议的 RSID**：解包脚本将建议一个用于跟踪更改的 RSID。复制此 RSID 以在步骤 4b 中使用。

4. **分批实现更改**：将更改逻辑分组（按章节、按类型或按邻近性），并在单个脚本中一起实现它们。这种方法：
   - 使调试更容易（较小的批次更容易隔离错误）
   - 允许逐步进展
   - 保持效率（3-10 个更改的批次效果很好）

   **建议的批量分组**：
   - 按文档章节（例如，“第 3 章更改”，“定义”，“终止条款”）
   - 按更改类型（例如，“日期更改”，“当事人名称更新”，“法律术语替换”）
   - 按邻近性（例如，“第 1-3 页的更改”，“文档前半部分的更改”）

   对于每个相关的更改批次：

   **a. 将文本映射到 XML**：在 `word/document.xml` 中 Grep 文本以验证文本如何分布在 `<w:r>` 元素中。

   **b. 创建并运行脚本**：使用 `get_node` 找到节点，实现更改，然后 `doc.save()`。见 ooxml.md 中的 **“文档库”** 部分以获取模式。

   **注意**：在编写脚本之前始终 Grep `word/document.xml` 以获取当前行号并验证文本内容。每次脚本运行后行号都会改变。

5. **打包文档**：所有批次完成后，将解包的目录转换回 .docx：
   ```bash
   python ooxml/scripts/pack.py unpacked reviewed-document.docx
   ```

6. **最终验证**：对完整文档进行全面检查：
   - 将最终文档转换为 Markdown：
     ```bash
     pandoc --track-changes=all reviewed-document.docx -o verification.md
     ```
   - 验证所有更改是否正确应用：
     ```bash
     grep "original phrase" verification.md  # 不应该找到它
     grep "replacement phrase" verification.md  # 应该找到它
     ```
   - 检查是否引入了任何意外的更改


## 将文档转换为图像

为了进行视觉分析 Word 文档，使用两步过程将它们转换为图像：

1. **将 DOCX 转换为 PDF**：
   ```bash
   soffice --headless --convert-to pdf document.docx
   ```

2. **将 PDF 页面转换为 JPEG 图像**：
   ```bash
   pdftoppm -jpeg -r 150 document.pdf page
   ```
   这会创建像 `page-1.jpg`、`page-2.jpg` 等文件。

选项：
- `-r 150`：将分辨率设置为 150 DPI（调整以平衡质量/大小）
- `-jpeg`：输出 JPEG 格式（如果需要，可以使用 `-png` 输出 PNG）
- `-f N`：第一个转换的页面（例如，`-f 2` 从第 2 页开始）
- `-l N`：最后一个转换的页面（例如，`-l 5` 停在第 5 页）
- `page`：输出文件的前缀

示例 - 转换特定范围：
```bash
pdftoppm -jpeg -r 150 -f 2 -l 5 document.pdf page  # 只转换第 2-5 页
```

## 代码风格指南
**重要**：在为 DOCX 操作生成代码时：
- 编写简洁的代码
- 避免冗长的变量名和冗余操作
- 避免不必要的 print 语句

## 依赖项

必需的依赖项（如果不可用，请安装）：

- **pandoc**：`sudo apt-get install pandoc`（用于文本提取）
- **docx**：`npm install -g docx`（用于创建新文档）
- **LibreOffice**：`sudo apt-get install libreoffice`（用于 PDF 转换）
- **Poppler**：`sudo apt-get install poppler-utils`（用于 pdftoppm 将 PDF 转换为图像）
- **defusedxml**：`pip install defusedxml`（用于安全 XML 解析）
