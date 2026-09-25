# 科学图形生成

为研究论文生成出版质量的图形。

## 输入

- `$0` — 所需图形的描述
- `$1` — (可选) 数据文件路径（CSV、JSON、NPY、PKL）或结果目录路径

## 脚本

### 生成图形模板
```bash
python ~/.claude/skills/figure-generation/scripts/figure_template.py --type bar --output figure_script.py --name comparison
python ~/.claude/skills/figure-generation/scripts/figure_template.py --list-types
```

可用类型：`bar`、`training-curve`、`heatmap`、`ablation`、`line`、`scatter`、`radar`、`violin`、`tsne`、`attention`

## 三阶段流程（源自MatPlotAgent）

### 阶段 1：查询扩展
使用`references/figure-prompts.md`中的提示，将用户的图形描述扩展为逐步的编码规范。确定：图形类型、数据映射（x/y/颜色/hue）、样式要求、论文规范。

### 阶段 2：带执行循环的代码生成（最多 4 次重试）
1. 使用`scripts/figure_template.py`模板生成自包含的 Python 脚本作为起点
2. 将脚本写入临时文件并执行：`python figure_script.py`
3. 若出错：捕获堆栈跟踪，反馈并重新生成（参见 references 中的 ERROR_PROMPT）
4. 若未生成`.png`文件：添加显式保存指令，重试
5. 若成功：报告生成的图形路径

### 阶段 3：视觉优化
读取生成的 PNG 文件，使用`references/figure-prompts.md`中的 VLM 反馈提示进行视觉检查：
- 图形类型是否与请求匹配？
- 标签、标题和图例是否正确？
- 颜色方案是否合适且一致？
- 坐标轴刻度是否合理？在出版尺寸下文本是否可读？

若需改进：生成纠正指令并重新执行。

## 参考文献

- 所有 MatPlotAgent 提示：`~/.claude/skills/figure-generation/references/figure-prompts.md`
- 图形模板：`~/.claude/skills/figure-generation/scripts/figure_template.py`

## 输出

PNG（预览，300 DPI）和 PDF（矢量，用于论文）格式。以及 LaTeX 包含代码：

```latex
\begin{figure}[t]
    \centering
    \includegraphics[width=\linewidth]{figures/figure_name.pdf}
    \caption{描述。最佳以彩色查看。}
    \label{fig:figure_name}
\end{figure}
```

## 质量要求
- DPI ≥ 300，或矢量 PDF
- 无障碍颜色方案（不含红绿组合）
- 所有文本在印刷尺寸下 ≥ 8pt
- 所有论文图形风格一致
- 无 matplotlib 默认标题 — 使用 LaTeX 图注

## 相关技能
- 上游：[数据分析](../data-analysis/)、[实验代码](../experiment-code/)
- 下游：[论文写作部分](../paper-writing-section/)、[论文编译](../paper-compilation/)、[幻灯片生成](../slide-generation/)
- 参见：[表格生成](../table-generation/)
