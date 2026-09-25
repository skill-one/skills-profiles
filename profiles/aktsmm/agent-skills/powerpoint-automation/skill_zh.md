# PowerPoint 自动化

使用 Orchestrator-Workers 模式进行 AI 驱动的 PPTX 生成。

## 使用场景

- 想将网络文章或博客转换为幻灯片时
- 想翻译和重构现有 PPTX 文件时
- 想使用 COM Automation 直接编辑打开的 PPTX 文件时
- 想基于模板生成 PPTX 文件时
- 想将 content.json 作为单一事实来源（SSOT），并将提取、翻译、生成、评审分离时

## 快速入门

**从网络文章**

```text
从 https://zenn.dev/example/article 创建一个包含 15 张幻灯片的演示文稿
```

**从现有 PPTX**

```text
将此演示文稿翻译成日语：input/presentation.pptx
```

**使用 COM 编辑打开的 PPTX**

```text
使用 COM Automation 编辑当前打开的 PowerPoint 演示文稿，并验证 RefURL、备注、溢出内容和超链接。
```

## 工作流程

```text
triage → plan → prepare_template → extract → translate → build → review → done
```

| 阶段   | 主要执行者                | 目的                          |
| ------ | ------------------------- | ----------------------------- |
| extract | `extract_images.py`       | 源文件 -> content.json        |
| build  | `create_from_template.py` | content.json -> PPTX          |
| review | PPTX Reviewer             | 溢出 / 一致性 / 质量         |

## 核心资源

### 脚本

脚本选择、参数和验证入口在 [references/SCRIPTS.md](references/SCRIPTS.md) 中定义。

### content.json

`content.json` 是此技能的单一事实来源（SSOT）。在提取、翻译、生成、评审期间，始终以此为基准。

```json
{
  "slides": [
    { "type": "title", "title": "Title", "subtitle": "Sub" },
    { "type": "content", "title": "Topic", "items": ["Point 1"] }
  ]
}
```

详细架构请参考 [references/schemas/content.schema.json](references/schemas/content.schema.json)。

### 模板

标准模板是 `assets/template.pptx`。布局和用途的详细说明在模板侧管理，主技能中仅保留最小必要内容。

```bash
python scripts/create_from_template.py assets/template.pptx content.json output.pptx --config assets/template_layouts.json
```

### 代理

角色定义和交接在 [references/AGENTS.md](references/AGENTS.md) 和 [references/agents/](references/agents/) 中定义。

## 操作规则

- **单一事实来源（SSOT）**：从批准的手稿中提取 content.json，并保留稳定的主题/问题到幻灯片映射。对未更改的内容重用批准；更改的声明或明确的范围限制需要确认。为演示格式压缩相关问答，而不是删除限定条件。
- **一个阶段，一个目的**：不要混合提取、翻译、生成、评审
- **快速失败**：发现问题时不强行进入下一阶段
- **人工介入**：在 PLAN 阶段进行用户确认
- **技术内容是验证内容**：Azure / Microsoft 的内容需在 MCP 确认后作为一级信息加入
- **PowerPoint 首先锁定**：对打开的 PPTX 使用 python-pptx 时不进行覆盖写入。读取也会触发 `PermissionError`，因此先使用 `Copy-Item` 复制到 `%TEMP%` 再读取。由于 `markitdown` 的输出在 PowerShell 管道中会乱码，使用 `-o` 将输出写入文件
- **COM 用于打开的演示文稿**：直接编辑打开的 PPTX 或现有 deck 请参考 [references/instructions/com-automation.instructions.md](references/instructions/com-automation.instructions.md)
- **保留打开或完全关闭**：COM 操作的最后必须决定是“用户可见所以保留打开”还是“完全关闭”。不要保留空的 PowerPoint 窗口。仅内部处理则 `Presentation.Close()` 后确认 `Presentations.Count` 为 0，然后 `Application.Quit()`，如果仍有 `POWERPNT` 进程残留，则仅停止 **MainWindowTitle 为空或无文件名的进程**（带文件名的仍可能是用户操作中）
- **了解演示文稿的打开方式**：通过 `Invoke-Item` / 探索器打开的 OneDrive 或 SharePoint 上的 PPTX 会使 `Presentation.FullName` 为 `https://`，且 **`SaveCopyAs` 不会写入 %TEMP% 而直接失败**。在 PDF 导出前确认 `FullName`，如果是 URL 则先关闭再使用本地绝对路径 `Presentations.Open()` 重新打开，然后 `SaveAs($tmp, 32)` 进行保存
- **备注是可分发内容**：将演讲者指南放在备注中，但排除可能不会从整个交付物中接收到的材料，包括隐藏幻灯片、备注和嵌入源。使用单独的受限文件；NDA 标签和隐藏标志不授予共享权限
- **受众上下文优先**：在答案和下一步操作之前，先介绍每个主题的目的或触发器、当前情况和未解决的问题。将此上下文保留在主幻灯片上，而不仅限于备注；将备注保留为允许的演讲者指南和实施细节
- **模板即模板**：如果有用户指定模板，特别是封面页，使用模板的现有占位符/布局，不要在上层覆盖其他图形
- **可重用模板即幻灯片母版**：如果被要求“创建模板”，则封面页、正文、Ending 的可重用设计应直接放置在幻灯片上，而不是 `SlideMaster.CustomLayouts`，编辑文字保留为 placeholder / text shape
- **PPTX 资产元数据门禁**：在将模板或分发用 PPTX 包含为技能资产 / 公共工件前，使用 `scripts/clean_template.py` 清理 `docProps/custom.xml`（MIP 标签、tenant、SharePoint 字段、同事邮箱）和 `docProps/core.xml`（`cp:lastModifiedBy` / `cp:revision`）。PowerPoint 会从 OneDrive / SharePoint 每次打开时重新应用 MIP，因此每次提交前必须运行。详细说明请参考 [references/instructions/template.instructions.md](references/instructions/template.instructions.md#template-metadata-hygiene)。不要仅通过幻灯片正文搜索进行安全判定
- **JP 模板字体默认**：日语可重用模板中，master/layout 的默认和文字体统一为 `BIZ UDPゴシック`，不要在生成幻灯片侧的后续处理中重复调整字体
- **渲染问答在交接前**：即使使用 COM 直接 touch-up 打开的 deck，也要从目标 deck 中导出实际渲染图像，分别对每张幻灯片确认重叠、字体不一致、表格可读性
- **像评论家一样评审，而不是生成者**：在展示给用户前，自己通过渲染图像查找“空白、文字太小、图标粗糙、模板遵循不足、旧词残留”等问题并修正。详细说明请参考 [references/instructions/deck-iteration-review.instructions.md](references/instructions/deck-iteration-review.instructions.md)
- **媒体恢复门禁**：用户评审后的幻灯片插入/删除/恢复必须重新检查预期幻灯片数量和嵌入视频/媒体位置
- **模板基幻灯片门禁**：复制模板生成时，先明确保留的 sample slide，通过结构编辑删除不需要的 contact / next-event 等。完成前验证从 content manifest 导出的预期张数、剩余 placeholder、幻灯片顺序
- **架构图使用形状**：使用形状而非 ASCII 艺术绘制
- **附录 URL 使用 Title - URL**：参考 URL 的显示格式需统一
- **分别评审内容和视觉效果**：生成后不仅进行视觉评审，还需评审与官方信息的准确性、URL 超链接数量、备注数量、placeholder/内部措辞

## 参考地图

### 常用

- [references/SCRIPTS.md](references/SCRIPTS.md)
- [references/USE_CASES.md](references/USE_CASES.md)
- [references/content-guidelines.md](references/content-guidelines.md)
- [references/IMPLEMENTATION_PATTERNS.md](references/IMPLEMENTATION_PATTERNS.md)
- [references/instructions/com-automation.instructions.md](references/instructions/com-automation.instructions.md)
- [references/instructions/template.instructions.md](references/instructions/template.instructions.md)
- [references/instructions/customer-facing-deck.instructions.md](references/instructions/customer-facing-deck.instructions.md)
- [references/instructions/deck-iteration-review.instructions.md](references/instructions/deck-iteration-review.instructions.md)

使用 [Implementation Patterns](references/IMPLEMENTATION_PATTERNS.md) 进行形状图、模板 XML、SlideMaster 编辑、视觉评审、超链接、RefURL、锁定、居中、损坏恢复和媒体嵌入。

## 完成 标准

- source 和 goal 固定
- content.json 作为基准各阶段分离
- template / layout 前提确认
- technical content 已完成一级信息确认
- operational text 未出现在幻灯片上
- template 使用时确认单调重复的相同布局和多余 placeholder
- 期待幻灯片数（含模板的保留/删除目标）与实际幻灯片集一致
- visual QA 通过渲染图像进行，修正后重新确认对应幻灯片
- 表格以正文 16pt 为原则，header 居中/中段对齐确认可视性
- build 后评审 overflow / consistency / hyperlink
