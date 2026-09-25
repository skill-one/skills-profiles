# 自我评估

使用结构化评估表格，通过多个评审者角色来评估一篇学术论文。

## 输入

- `$ARGUMENTS` — PDF 文件路径或 `.tex` 文件路径

## 脚本

### 从 PDF 中提取文本
```bash
python ~/.claude/skills/self-review/scripts/extract_pdf_text.py paper.pdf --output paper_text.txt
python ~/.claude/skills/self-review/scripts/extract_pdf_text.py paper.pdf --format markdown
```

尝试 pymupdf4llm（最佳）→ pymupdf → pypdf。安装：`pip install pymupdf4llm pymupdf pypdf`

### 将 PDF 解析为结构化章节
```bash
python ~/.claude/skills/self-review/scripts/parse_pdf_sections.py \
  --pdf paper.pdf --output sections.json
```

提取标题（通过字体大小）、章节标题和章节文本。需要：`pip install pymupdf`
关键标志：`--format text`, `--verbose`

## 工作流程

### 第 1 步：加载论文
- 如果是 PDF：使用 `extract_pdf_text.py` 提取文本
- 如果是 `.tex`：直接读取 LaTeX 源代码

### 第 2 步：三人角色评估
使用不同的角色（来自 `references/review-form.md`）运行三次独立评估：

1. **严厉但公正的评审者**：期望良好的实验，能得出见解
2. **严厉且批判的评审者**：寻找领域中的有影响力的想法
3. **开放心态的评审者**：寻找之前未提出的新想法

对于每个角色，按照 `references/review-form.md` 中的 NeurIPS 评审 JSON 格式生成评审。

### 第 3 步：反思改进（每个评审者最多 3 轮）
每次评审后，应用反思提示：重新评估准确性和合理性，如有必要则改进。当出现“我完成了”时停止。

### 第 4 步：汇总
- 合并所有三次评审
- 平均数值分数（四舍五入到最接近的整数）
- 综合得出元评审结论
- 使用 AgentLaboratory 权重：整体（1.0）、贡献（0.4）、展示（0.2）、其他（每个 0.1）

### 第 5 步：可操作的报告

输出格式：
```
## 评审摘要
- **整体评分**：X/10（加权：Y/10）
- **决定**：接受 / 拒绝
- **信心**：Z/5

## 优势（评审者共识）
1. ...
2. ...

## 劣势（评审者共识）
1. ...
2. ...

## 作者问题
1. ...

## 具体改进建议
1. [章节 X，页码 Y]: ...
2. [章节 Z，页码 W]: ...

## 评分明细
| 维度 | R1 | R2 | R3 | 平均 |
|------|----|----|-----|-----|
| 整体 | ... | ... | ... | ... |
| 贡献 | ... | ... | ... | ... |
| ... | ... | ... | ... | ... |
```

## 参考文献

- NeurIPS 评审表格、评分权重、角色、反思提示：`~/.claude/skills/self-review/references/review-form.md`
- PDF 文本提取：`~/.claude/skills/self-review/scripts/extract_pdf_text.py`

## 缺失章节检查
你必须验证所有必需章节是否存在：摘要、引言、方法/方法、实验/结果、讨论/结论。如有缺失，则降低分数。

## 相关技能
- 上游：[paper-compilation](../paper-compilation/)
- 下游：[paper-revision](../paper-revision/)、[rebuttal-writing](../rebuttal-writing/)
- 参见：[slide-generation](../slide-generation/)
