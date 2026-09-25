# 表格生成

将实验结果转换为适合发表的 LaTeX 表格。

## 输入

- `$0` — 表格类型：`comparison`（比较）、`ablation`（消融）、`descriptive`（描述性）、`custom`（自定义）
- `$1` — 数据源：JSON 文件、CSV 文件或内联数据

## 脚本

### 从 JSON/CSV 生成 LaTeX 表格
```bash
python ~/.claude/skills/table-generation/scripts/results_to_table.py \
  --input results.json --type comparison \
  --bold-best max --caption "性能比较" \
  --label tab:main_results
```

支持：`comparison`（比较）、`ablation`（消融）、`descriptive`（描述性）、`multi-dataset`（多数据集）表格类型。
附加标志：`--type multi-dataset` 用于方法 x 数据集 x 指标布局，`--significance` 用于 p 值星标，`--underline-second` 用于第二优结果。

## 参考文献

- LaTeX 表格模板和示例：`~/.claude/skills/table-generation/references/table-templates.md`

## 表格类型

### `comparison` — 主要结果表格
- 行 = 方法（基线 + 我们的），列 = 指标/数据集
- 每列中的最佳结果加粗
- 可用时包含均值 +/- 标准差
- 使用 `\multirow` 用于方法类别（监督、自监督等）

### `ablation` — 消融研究表格
- 行 = 变体（完整模型、移除组件 A、移除组件 B、...），列 = 指标
- 加粗完整模型结果
- 使用复选标记表示组件存在

### `descriptive` — 数据集/统计表格
- 数据集特征、超参数或汇总统计数据
- 清晰的格式，包含正确的单位

### `custom` — 自定义表格
- 用户指定布局和内容

## 必要的 LaTeX 包
```latex
\usepackage{booktabs}    % \toprule, \midrule, \bottomrule
\usepackage{multirow}    % \multirow
\usepackage{multicol}    % 多列布局
\usepackage{threeparttable}  % 表格注释
```

## 输出格式

始终生成包含以下内容的表格：
1. `booktabs` 规则 (`\toprule`, `\midrule`, `\bottomrule`)
2. `\caption{}` 和 `\label{tab:...}`
3. 使用 `\textbf{}` 加粗最佳结果
4. 需要时通过 `threeparttable` 添加表格注释
5. 正确的对齐 (`l` 用于文本，`c` 或 `r` 用于数字)

## 规则

- 仅包含实际实验日志中的数字 — 永不凭空捏造结果
- 所有数字必须与数据源完全匹配
- 使用 `$\pm$` 表示标准差
- 适当使用 `\underline{}` 为第二优结果加下划线
- 保持表格紧凑 — 避免不必要的列
- 使用 `table*` 用于跨越两列的宽表格
- 为缩写列标题添加术语表/注释

## 相关技能
- 上游：[数据分析](../data-analysis/)、[实验代码](../experiment-code/)
- 下游：[论文写作部分](../paper-writing-section/)、[论文编译](../paper-compilation/)
- 参见：[图表生成](../figure-generation/)
