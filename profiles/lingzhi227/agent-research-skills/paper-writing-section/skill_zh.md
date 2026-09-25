# 论文章节生成器

为学术论文撰写出版质量的章节。

## 输入

- `$0` — 章节名称：`abstract`（摘要）、`introduction`（引言）、`background`（背景）、`related-work`（相关工作）、`methods`（方法）、`experimental-setup`（实验设置）、`results`（结果）、`discussion`（讨论）、`conclusion`（结论）
- `$1` — （可选）上下文文件路径（研究计划、结果、先前的章节）

## 工作流程

### 第一步：收集上下文
读取论文现有的 `.tex` 文件、实验日志、结果文件以及提供的任何上下文。理解：标题、贡献、方法、关键结果、图表、表格。

### 第二步：撰写章节
加载来自 `references/section-tips.md` 的章节特定提示。在每个段落之前，作为 LaTeX 注释（`% Plan: ...`）包含一个简短的计划。

### 第三步：两遍润色
应用来自 `references/refinement-prompts.md` 的两遍润色：
- **第一遍**：修正错误（未封闭的数学公式、损坏的引用、幻觉的数字、重复的标签）
- **第二遍**：删除冗余、压缩、确保过渡平滑

## 参考文献

- 章节撰写提示：`~/.claude/skills/paper-writing-section/references/section-tips.md`
- 润色提示和错误检查清单：`~/.claude/skills/paper-writing-section/references/refinement-prompts.md`

## 输出

LaTeX 片段（不包含 `\documentclass`，不包含前置部分）。所有数学公式用 `$...$` 或 `\begin{equation}` 包围，所有图表引用用 `\ref{}`，所有引用文献使用 `\cite{}`，不包含占位符文本。

## 质量检查清单
- 所有数学公式正确包围
- 所有 `\ref{}` 和 `\cite{}` 有效
- 无 TODO/TBD/FIXME 标记
- 数字与实验日志完全一致
- 写作风格客观——无夸张词汇
- 章节长度适合会议/期刊

## 相关技能
- 上游：[数据分析](../data-analysis/)、[图表生成](../figure-generation/)、[表格生成](../table-generation/)、[相关工作撰写](../related-work-writing/)
- 下游：[LaTeX 格式化](../latex-formatting/)、[引用管理](../citation-management/)
- 参见：[论文组装](../paper-assembly/)
