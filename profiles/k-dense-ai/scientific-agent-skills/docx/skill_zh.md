# DOCX 创建、编辑和分析

`.docx` 是一个包含 XML 文件的 ZIP 压缩包。根据任务选择你的方法：

| 任务 | 方法 |
|---|---|
| **创建** 新文档 | 编写 `docx` (npm) 脚本 — 下方有注意事项 |
| **编辑** 现有文档 | `unzip` → 编辑 `word/document.xml` → `zip` (docx-js 无法打开现有文件) |
| **读取** 内容 | `pandoc -t markdown file.docx` |

> 下方脚本路径相对于此技能的目录。

## 使用 docx-js 创建 — 注意事项

`docx` 已预装 — 不要先运行 `npm install`；直接编写脚本并 `require('docx')`。只有在 `require('docx')` 失败时才需要 `npm install docx`。模型了解 API；这些是陷阱：

- **页面大小默认为 A4。** 对于美国信纸设置 `page: { size: { width: 12240, height: 15840 } }` (DXA；1440 = 1 英寸)。
- **横向：** 传递纵向尺寸并 `orientation: PageOrientation.LANDSCAPE` — docx-js 内部会交换宽高。
- **表格需要双重宽度：** 在表格上设置 `columnWidths`，在每个单元格上设置 `width`，两者均在 `WidthType.DXA` (PERCENTAGE 在 Google Docs 中会中断)。列宽之和必须等于表格宽度。
- **表格着色：** 使用 `ShadingType.CLEAR`，永远不要使用 `SOLID` (会渲染为黑色)。
- **列表：** 不要直接插入 `•`；使用带有 `LevelFormat.BULLET` 的 `numbering` 配置。
- **`ImageRun` 需要 `type:`** (`"png"`, `"jpg"`, …)。
- **`PageBreak` 必须在 `Paragraph` 内部。**
- **永远不要使用 `\n`** — 使用单独的 `Paragraph` 元素。
- **目录 (TOC)：** 标题必须使用内置的 `HeadingLevel.*`；自定义标题样式需要设置 `outlineLevel` 或它们不会显示。
- **不要使用表格作为水平线** — 使用段落底部边框代替。
- **点引导 / 同行右对齐：** 在 `TextRun` 内部使用 `PositionalTab` (`alignment: PositionalTabAlignment.RIGHT`, `leader: PositionalTabLeader.DOT`)，而不是直接使用 `.` 或空格填充。

## 验证输出

创建 `.docx` 后，渲染并查看：

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.docx
pdftoppm -jpeg -r 100 output.pdf page
ls page-*.jpg   # 然后读取图像
```

`pdftoppm` 会用页码宽度补零 (`page-01.jpg`…`page-12.jpg`)。

## 编辑现有文档

遗留 `.doc` 文件必须先转换：`python scripts/office/soffice.py --headless --convert-to docx file.doc`。

```bash
unzip -q doc.docx -d unpacked/
find unpacked -type l -delete   # 删除符号链接条目 — 来自外部方的 docx 不可信
python scripts/merge_runs.py unpacked/   # 合并碎片化运行，使文本可查找
# 原地编辑 unpacked/word/document.xml — 不要重新格式化或美化输出
(cd unpacked && rm -f ../out.docx && zip -Xr ../out.docx .)
python scripts/office/validate.py out.docx --original doc.docx   # XSD 检查；--auto-repair 修复常见问题
# 跟踪修订？添加 `--author "<你修订时的名字>"` 以检查每个修订是否被跟踪
```

Word 将文本拆分到多个 `<w:r>` 运行中（修订 ID、拼写检查标记），因此文档中可见的短语可能不作为连续字符串存在于 XML 中。`merge_runs.py` 合并 `word/document.xml` 中相邻的相同格式运行，不改变内容或渲染；它也接受直接传入 `.docx` (`python scripts/merge_runs.py doc.docx -o merged.docx`)。

**跟踪修订：** 修订时使用 `--author "<你修订时的名字>"`（需要 `--original`） — 它会报告任何没有 `<w:ins>`/`<w:del>` 包围的文本更改，这很容易意外操作且在可见视图中不可见。用 `<w:ins>`/`<w:del>` 包裹运行，并添加 `w:id`、`w:author`、`w:date` 属性。在 `<w:del>` 内，文本元素是 `<w:delText>`，不是 `<w:t>`。删除段落标记 (`<w:pPr><w:rPr><w:del w:id=".." w:author=".." w:date=".."/></w:rPr></w:pPr>`) 意味着“将此段落合并到下一个” — 因此删除段落是加上这个，再加上每个运行周围的 `<w:del>`。`<w:del/>` 必须在 `rPr` 的其他子元素之前；它们的顺序由模式强制。

要生成所有跟踪修订都被接受的干净副本：`python scripts/accept_changes.py in.docx out.docx`。

接受删除的段落标记应将段落与下方段落合并，因此所有运行都被删除的段落会消失。Word 会这样做；`accept_changes.py` 和 `pandoc --track-changes=accept` 不总是这样。它们以相同的方式失败 — 它们删除了文本但留下了空段落，当它是自动编号时，会显示为孤立的空项目符号：

- `pandoc --track-changes=accept` 从不合并段落。
- `accept_changes.py` (LibreOffice) 正确合并，但当删除的段落后面跟着一个空占位符段落时会出错。

任何视图中的空项目符号都是该视图的产物，而不是文档的缺陷。在 XML 中检查段落删除。

## 修订

修订需要六个交叉链接文件。使用辅助工具 — 目录模式当你也会编辑 `document.xml` 时（节省解压/压缩周期），`.docx` 直接模式否则：

```bash
# 对已解压的目录（当放置标记时首选）
python scripts/comment.py unpacked/ "费用上限太低"
python scripts/comment.py unpacked/ "同意" --parent 0

# 对 .docx 直接操作
python scripts/comment.py contract.docx "此上限太低" -o annotated.docx
```

脚本会写入 `comments.xml`、`commentsExtended.xml`、`commentsIds.xml`、`commentsExtensible.xml`、关系和内容类型覆盖。修订 ID 会自动分配。然后它会打印 `<w:commentRangeStart>`/`<w:commentRangeEnd>`/`<w:commentReference>` 片段添加到 `word/document.xml`，以便修订锚定到特定文本 — 在你放置这些标记之前，修订存在但不可见。

## 依赖项

`docx` (npm，预装 — 只有 `require('docx')` 失败时才安装) · `pandoc` · LibreOffice (`soffice`) · `pdftoppm` (Poppler)

---

*此技能由 [Anthropic](https://github.com/anthropics/skills/tree/main/skills/docx) 创建和维护；在此处未修改，仅更改了 frontmatter 元数据；有关条款，请参阅 LICENSE.txt。*
