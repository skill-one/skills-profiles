# 数据分析

生成经过多轮审核的严格统计分析代码。

## 输入

- `$0` — 数据源（CSV、JSON、pickle 或实验日志）
- `$1` — 研究目标或待检验的假设

## 参考文献

- 4轮代码审核提示：`~/.claude/skills/data-analysis/references/review-prompts.md`

## 脚本

### 统计摘要和比较
```bash
python ~/.claude/skills/data-analysis/scripts/stat_summary.py --input results.csv --compare method --metric accuracy --output summary.json
python ~/.claude/skills/data-analysis/scripts/stat_summary.py --input results.csv --describe
```

检测数据类型、推荐测试、运行比较、输出效应大小和显著性星号。需要 numpy、scipy。

### 格式化p值
```bash
python ~/.claude/skills/data-analysis/scripts/format_pvalue.py --values "0.001 0.05 0.23" --format stars
python ~/.claude/skills/data-analysis/scripts/format_pvalue.py --csv results.csv --column pvalue --format latex
```

使用星号、LaTeX符号或纯文本格式化p值。仅使用标准库。

## 工作流程

### 第1步：生成分析代码
使用以下部分结构化代码：
1. `# 导入` — pandas、numpy、scipy、statsmodels、sklearn
2. `# 加载数据` — 从原始数据文件加载
3. `# 数据集准备` — 缺失值、单位、排除标准
4. `# 描述性统计` — 如有必要，生成摘要表
5. `# 预处理` — 虚拟变量、归一化
6. `# 分析` — 根据假设进行统计测试
7. `# 保存附加结果` — 保存pickle格式的额外结果

### 第2步：4轮代码审核
1. **第1轮 — 代码缺陷**：数学/统计错误、计算错误、琐碎测试
2. **第2轮 — 数据处理**：缺失值、单位、预处理、测试选择
3. **第3轮 — 按表**：合理值、不确定性度量、缺失数据
4. **第4轮 — 横向表**：完整性、一致性、缺失变量

### 第3步：生成结果
- 每个名义值必须有不确定性（CI、STD 或 p值）
- 统计测试必须适用于数据类型
- 结果必须与实际数据一致 — 不要凭空捏造

## 允许的包

`pandas`, `numpy`, `scipy`, `statsmodels`, `sklearn`, `pickle`

## 统计测试选择

| 数据类型 | 测试 |
|-----------|------|
| 两组，正态 | 独立t检验 |
| 两组，非正态 | 曼-惠特尼U检验 |
| 配对样本 | 配对t检验 / 威尔科克森 |
| 多组 | 方差分析 / 克鲁斯卡尔-沃利斯检验 |
| 分类数据 | 卡方检验 / 精确检验 |
| 相关性 | 皮尔逊 / 斯皮尔曼 |
| 回归 | OLS / 逻辑回归 / 混合效应 |

## 规则

- 必须报告统计测试的p值
- 考虑相关的混杂变量
- 使用内置包功能（例如，`formula = "y ~ a * b"` 用于交互作用）
- 不要手动实现可用的统计函数
- 使用基于字符串的列名访问数据框，而不是整数索引

## 相关技能
- 上游：[实验代码](../experiment-code/), [实验设计](../experiment-design/)
- 下游：[表格生成](../table-generation/), [图形生成](../figure-generation/), [逆向可追溯性](../backward-traceability/)
- 参见：[数学推理](../math-reasoning/)
