# 幻灯片生成

将完成的论文转换为演示文稿幻灯片或海报。

## 输入

- `$0` — 论文 LaTeX 文件（main.tex）或论文目录

## 参考文献

- 幻灯片模板和布局模式：`~/.claude/skills/slide-generation/references/slide-templates.md`

## 脚本

### 提取用于幻灯片的论文元素
```bash
python ~/.claude/skills/slide-generation/scripts/extract_paper_elements.py --tex main.tex --output slides_skeleton.tex
python ~/.claude/skills/slide-generation/scripts/extract_paper_elements.py --tex main.tex --format json --output elements.json
python ~/.claude/skills/slide-generation/scripts/extract_paper_elements.py --tex main.tex --output slides.tex --theme metropolis
```

解析 .tex 文件，提取标题/作者/章节/公式/图表/表格，生成 Beamer 骨架。

## 工作流程

### 第 1 步：提取关键内容
从论文中提取：
1. **标题、作者、所属机构**
2. **核心贡献**（从摘要中提取 1-3 个要点）
3. **关键图表**（所有 \includegraphics 路径）
4. **关键表格**（简化版本）
5. **关键公式**（来自方法部分的编号公式）
6. **主要结果**（结果部分的最佳数据）

### 第 2 步：设计幻灯片结构
标准口头演示流程（约 15-20 张幻灯片）：

| 幻灯片编号 | 内容 | 来源章节 |
|---------|---------|---------------|
| 1 | 标题幻灯片 | 标题/作者 |
| 2 | 动机 / 问题 | 引言 |
| 3 | 现有解决方案为何失败 | 相关工作 |
| 4-5 | 我们的方案（高层级） | 方法 |
| 6-8 | 技术细节 + 公式 | 方法 |
| 9 | 实验设置 | 实验 |
| 10-13 | 结果（图表 + 表格） | 结果 |
| 14 | 消融研究 | 结果 |
| 15 | 限制与未来工作 | 讨论 |
| 16 | 结论 | 结论 |
| 17 | 感谢 + 问答 | — |

### 第 3 步：生成 Beamer LaTeX
```latex
\documentclass[aspectratio=169]{beamer}
\usetheme{metropolis}
\title{论文标题}
\author{作者}
\date{会议年份}

\begin{document}
\maketitle

\begin{frame}{动机}
\begin{itemize}
    \item 问题陈述
    \item 为何重要
\end{itemize}
\end{frame}

% ... 更多框架
\end{document}
```

### 第 4 步：简化用于演示
- 表格：减少到必要的行/列
- 公式：仅显示关键见解，不显示完整推导
- 图表：使用最大版本，添加注释
- 文本：仅使用要点，不使用段落

### 第 5 步：生成海报布局（可选）
对于海报会议，使用多列布局：
- 列 1：引言 + 动机
- 列 2：方法 + 关键公式
- 列 3：结果 + 图表
- 列 4：结论 + 参考文献

## 规则

- 每张幻灯片最多 1 个关键信息
- 图表应大且易读
- 每张幻灯片最多 6 个要点
- 公式应为简化版本
- 包含幻灯片编号
- 使用与论文图表一致的颜色方案
- 演示应自包含（无需阅读论文即可理解）

## 相关技能
- 上游：[paper-compilation](../paper-compilation/)、[figure-generation](../figure-generation/)
- 参见：[self-review](../self-review/)、[paper-assembly](../paper-assembly/)
