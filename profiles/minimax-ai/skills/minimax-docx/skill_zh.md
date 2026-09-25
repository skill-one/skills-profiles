# minimax-docx

通过 CLI 工具或基于 OpenXML SDK (.NET) 构建的直接 C# 脚本创建、编辑和格式化 DOCX 文档。

## 安装

**首次使用：** `bash scripts/setup.sh`（在 Windows 上为 `powershell scripts/setup.ps1`，使用 `--minimal` 跳过可选依赖项）。

**会话中的首次操作：** `scripts/env_check.sh` — 如果显示 `NOT READY` 则不要继续。（在相同会话中的后续操作中可跳过。）

## 快速入门：直接 C# 路径

当任务需要结构化文档操作（自定义样式、复杂表格、多节布局、页眉/页脚、目录、图像）时，直接编写 C# 而不是与 CLI 限制搏斗。使用此脚手架：

```csharp
// 文件：scripts/dotnet/task.csx（或 Console 项目中的新 .cs 文件）
// dotnet run --project scripts/dotnet/MiniMaxAIDocx.Cli -- run-script task.csx
#r "nuget: DocumentFormat.OpenXml, 3.2.0"

using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;

using var doc = WordprocessingDocument.Create("output.docx", WordprocessingDocumentType.Document);
var mainPart = doc.AddMainDocumentPart();
mainPart.Document = new Document(new Body());

// --- 你的逻辑代码 ---
// 首先阅读相关的 Samples/*.cs 文件以获取经过测试的模式。
// 参见下文参考资料部分中的 Samples 表格。
```

**在编写任何 C# 代码之前，请先阅读相关的 `Samples/*.cs` 文件** — 它们包含可编译、经过 SDK 版本验证的模式。参考资料部分中的 Samples 表格将主题映射到文件。

## CLI 简写

所有以下 CLI 命令使用 `$CLI` 作为简写：
```bash
dotnet run --project scripts/dotnet/MiniMaxAIDocx.Cli --
```

## 管道路由

通过检查用户是否有输入的 .docx 文件进行路由：

```
用户任务
├─ 无输入文件 → 管道 A：创建
│   信号： "写入", "创建", "草稿", "生成", "新建", "制作报告/提案/备忘录"
│   → 阅读参考资料/scenario_a_create.md
│
└─ 有输入 .docx
    ├─ 替换/填充/修改内容 → 管道 B：填充-编辑
    │   信号： "填写", "替换", "更新", "更改文本", "添加节", "编辑"
    │   → 阅读参考资料/scenario_b_edit_content.md
    │
    └─ 重新格式化/应用样式/模板 → 管道 C：格式化-应用
        信号： "重新格式化", "应用模板", "重新样式", "匹配此格式", "套模板", "排版"
        ├─ 模板是纯样式（无内容）→ C-1：覆盖（将样式应用于源文件）
        └─ 模板具有结构（封面/目录/示例节）→ C-2：基础-替换
            （使用模板作为基础，将示例内容替换为用户内容）
        → 阅读参考资料/scenario_c_apply_template.md
```

如果请求跨越多个管道，请按顺序运行它们（例如，创建然后格式化-应用。

## 预处理

如有需要，将 `.doc` 转换为 `.docx`：`scripts/doc_to_docx.sh input.doc output_dir/`

编辑前预览（避免读取原始 XML）：`scripts/docx_preview.sh document.docx`

为编辑场景分析结构：`$CLI analyze --input document.docx`

## 场景 A：创建

首先阅读 `references/scenario_a_create.md`、`references/typography_guide.md` 和 `references/design_principles.md`。从 `Samples/AestheticRecipeSamples.cs` 中选择与文档类型匹配的审美配方 — 不要凭空发明格式值。对于 CJK，还请阅读 `references/cjk_typography.md`。

**选择你的路径：**
- **简单**（纯文本、最小格式化）：使用 CLI — `$CLI create --type report --output out.docx --config content.json`
- **结构化**（自定义样式、多节、目录、图像、复杂表格）：直接编写 C#。首先阅读相关的 `Samples/*.cs` 文件。

CLI 选项：`--type`（report|letter|memo|academic）、`--title`、`--author`、`--page-size`（letter|a4|legal|a3）、`--margins`（standard|narrow|wide）、`--header`、`--footer`、`--page-numbers`、`--toc`、`--content-json`。

然后运行**验证管道**（下方）。

## 场景 B：编辑 / 填充

首先阅读 `references/scenario_b_edit_content.md`。预览 → 分析 → 编辑 → 验证。

**选择你的路径：**
- **简单**（文本替换、占位符填充）：使用 CLI 子命令。
- **结构化**（添加/重组节、修改样式、操作表格、插入图像）：直接编写 C#。阅读 `references/openxml_element_order.md` 和相关的 `Samples/*.cs`。

可用的 CLI 编辑子命令：
- `replace-text --find "X" --replace "Y"`
- `fill-placeholders --data '{"key":"value"}'`
- `fill-table --data table.json`
- `insert-section`, `remove-section`, `update-header-footer`

```bash
$CLI edit replace-text --input in.docx --output out.docx --find "OLD" --replace "NEW"
$CLI edit fill-placeholders --input in.docx --output out.docx --data '{"name":"John"}'
```

然后运行**验证管道**。还运行 diff 以验证最小更改：
```bash
$CLI diff --before in.docx --after out.docx
```

## 场景 C：应用模板

首先阅读 `references/scenario_c_apply_template.md`。预览并分析源文件和模板。

```bash
$CLI apply-template --input source.docx --template template.docx --output out.docx
```

对于复杂的模板操作（多模板合并、每节页眉/页脚、样式合并），直接编写 C# — 见下方关键规则，了解所需的模式。

运行**验证管道**，然后运行**硬门禁检查**：
```bash
$CLI validate --input out.docx --gate-check assets/xsd/business-rules.xsd
```
门禁检查是**硬性要求**。在通过之前不要交付。如果失败：诊断、修复、重新运行。

还运行 diff 以验证内容保留：`$CLI diff --before source.docx --after out.docx`

## 验证管道

每次写入操作后运行。对于场景 C，完整的管道是**强制要求**；对于 A/B，它是**推荐**的（仅当操作非常简单时才跳过）。

```bash
$CLI merge-runs --input doc.docx                                    # 1. 合并运行
$CLI validate --input doc.docx --xsd assets/xsd/wml-subset.xsd     # 2. XSD 结构
$CLI validate --input doc.docx --business                           # 3. 业务规则
```

如果 XSD 失败，自动修复并重试：
```bash
$CLI fix-order --input doc.docx
$CLI validate --input doc.docx --xsd assets/xsd/wml-subset.xsd
```

如果 XSD 仍然失败，回退到业务规则 + 预览：
```bash
$CLI validate --input doc.docx --business
scripts/docx_preview.sh doc.docx
# 验证：字体污染=0，表格数量正确，绘图数量正确，sectPr 数量正确
```

最终预览：`scripts/docx_preview.sh doc.docx`

## 关键规则

这些规则防止文件损坏 — OpenXML 对元素顺序非常严格。

**元素顺序**（属性始终优先）：

| 父元素 | 顺序 |
|--------|-------|
| `w:p`  | `pPr` → runs |
| `w:r`  | `rPr` → `t`/`br`/`tab` |
| `w:tbl`| `tblPr` → `tblGrid` → `tr` |
| `w:tr` | `trPr` → `tc` |
| `w:tc` | `tcPr` → `p` (至少 1 个 `<w:p/>`) |
| `w:body` | 块内容 → `sectPr` (最后一个子元素) |

**直接格式污染**：当从源文档复制内容时，内联 `rPr`（字体、颜色）和 `pPr`（边框、阴影、间距）会覆盖模板样式。始终清除直接格式 — 仅保留 `pStyle` 引用和 `t` 文本。清理表格（包括单元格内的 `pPr/rPr`）。

**跟踪更改**：`<w:del>` 使用 `<w:delText>`，从不使用 `<w:t>`。`<w:ins>` 使用 `<w:t>`，从不使用 `<w:delText>`。

**字体大小**：`w:sz` = 点数 × 2（12pt → `sz="24"`）。边距/间距以 DXA 为单位（1 英寸 = 1440，1cm ≈ 567）。

**标题样式必须具有 OutlineLevel**：定义标题样式（Heading1、ThesisH1 等）时，始终在 `StyleParagraphProperties` 中包含 `new OutlineLevel { Val = N }`（H1→0，H2→1，H3→2）。如果没有，Word 将它们视为普通样式文本 — 目录和导航窗格将无法工作。

**多模板合并**：当提供多个模板文件（字体、标题、分页符）时，首先阅读 `references/scenario_c_apply_template.md` 中的“多模板合并”部分。关键规则：
- 将所有模板的样式合并到一个 styles.xml 中。结构（节/分页符）来自分页符模板。
- 每个内容段落必须出现一次 — 在插入节分页符时不要重复。
- 永远不要插入空/空白段落作为填充或节分隔符。输出段落数量必须等于输入。使用节分页符属性（`w:sectPr` 在 `w:pPr` 内）和样式间距（`w:spacing` 前/后）进行视觉分隔。
- 在每个章节标题之前插入 oddPage 节分页符，而不仅仅是第一个。即使章节具有双列内容，它也必须以 oddPage 开头；在标题后使用第二个连续分页符进行列切换。
- 双列章节需要三个节分页符：(1) 在前一个段落的 pPr 中的 oddPage，(2) 在章节标题的 pPr 中的连续+cols=2，(3) 在最后一个正文段落的 pPr 中的连续+cols=1 以恢复。
- 从分页符模板为每个节复制 `titlePg` 设置。摘要和目录节通常需要 `titlePg=true`。

**多节页眉/页脚**：具有 10+ 节的模板（例如中文论文）每节具有不同的页眉/页脚（罗马数字与阿拉伯数字页码、每个区域不同的页眉文本）。规则：
- 使用 C-2 基础-替换：将模板作为输出基础复制，然后替换正文内容。这会自动保留所有节、页眉、页脚和 titlePg 设置。
- 永远不要从头开始重新创建页眉/页脚 — 字节对字节复制模板页眉/页脚 XML。
- 永远不要添加模板页眉 XML 中不存在的格式（边框、对齐、字体大小）。
- 非封面节必须具有页眉/页脚 XML 文件（至少空页眉 + 页码页脚）。
- 参见 `references/scenario_c_apply_template.md` 中的“多节页眉/页脚传输”部分。

## 参考资料

按需加载 — 不要一次性加载所有文件。选择与任务最相关的文件。

**下方的 C# 示例和设计参考资料是项目的知识库（“百科全书”）**。在编写 OpenXML 代码时，始终先阅读相关的示例文件 — 它们包含可编译、经过 SDK 版本验证的模式，可防止常见错误。在做出审美决策时，阅读设计原则和配方文件 — 它们编码了来自权威来源（IEEE、ACM、APA、Nature 等）的经过测试的和谐参数集，而不是猜测。

### 场景指南（每个管道首先阅读）

| 文件 | 使用场景 |
|------|------|
| `references/scenario_a_create.md` | 管道 A：从空白创建 |
| `references/scenario_b_edit_content.md` | 管道 B：编辑现有内容 |
| `references/scenario_c_apply_template.md` | 管道 C：应用模板格式 |

### C# 代码示例（可编译、 heavily commented — 编写代码时阅读）

| 文件 | 主题 |
|------|------|
| `Samples/DocumentCreationSamples.cs` | 文档生命周期：创建、打开、保存、流、doc 默认值、设置、属性、页面设置、多节 |
| `Samples/StyleSystemSamples.cs` | 样式：Normal/Heading 链、字符/表格/列表样式、DocDefaults、latentStyles、CJK 公文、APA 7th、导入、解析继承 |
| `Samples/CharacterFormattingSamples.cs` | RunProperties：字体、大小、粗体/斜体、所有下划线、颜色、高亮、删除线、上/下标、大写、间距、阴影、边框、强调标记 |
| `Samples/ParagraphFormattingSamples.cs` | ParagraphProperties：对齐、缩进、行/段落间距、保持/孤儿、大纲级别、边框、制表符、编号、双向、框架 |
| `Samples/TableSamples.cs` | 表格：边框、网格、单元格属性、边距、行高、重复表头、合并（H+V）、嵌套、浮动、三线表、条纹 |
| `Samples/HeaderFooterSamples.cs` | 页眉/页脚：页码、 "第 X 页，共 Y 页"，第一页/偶数页/奇数页、标志图像、表格布局、公文 "-X-"、每节 |
| `Samples/ImageSamples.cs` | 图像：内联、浮动、文本环绕、边框、替代文本、页眉/表格内、替换、SVG 回退、尺寸计算 |
| `Samples/ListAndNumberingSamples.cs` | 编号：项目符号、多级十进制、自定义符号、大纲→标题、法律、中文 一/（一）/1./(1)、重启/继续 |
| `Samples/FieldAndTocSamples.cs` | 字段：目录、SimpleField vs 复杂字段、DATE/PAGE/REF/SEQ/MERGEFIELD/IF/STYLEREF、目录样式 |
| `Samples/FootnoteAndCommentSamples.cs` | 脚注、尾注、评论（4 文件系统）、书签、超链接（内部 + 外部） |
| `Samples/TrackChangesSamples.cs` | 修订：插入（w:t）、删除（w:delText!）、格式更改、全部接受/拒绝、移动跟踪 |
| `Samples/AestheticRecipeSamples.cs` | 13 个来自权威来源的审美配方：ModernCorporate、AcademicThesis、ExecutiveBrief、ChineseGovernment (GB/T 9704)、MinimalModern、IEEE Conference、ACM sigconf、APA 7th、MLA 9th、Chicago/Turabian、Springer LNCS、Nature、HBR — 每个配方都包含来自官方样式指南的确切值 |

注意：`Samples/` 路径相对于 `scripts/dotnet/MiniMaxAIDocx.Core/`。
