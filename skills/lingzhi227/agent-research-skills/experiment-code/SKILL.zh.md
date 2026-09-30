---
name: experiment-code
description: 使用迭代改进方法编写机器学习实验代码。生成训练/评估流程，调试错误，并通过代码反思优化结果。适用于为研究论文实现实验。
---

# 实验代码

为研究论文生成并迭代改进机器学习实验代码。

## 输入

- `$0` — 任务：`generate`（生成）、`improve`（改进）、`debug`（调试）、`plot`（绘图）
- `$1` — 研究计划、想法描述或错误信息

## 参考文献

- 实验提示和模板：`~/.claude/skills/experiment-code/references/experiment-prompts.md`
- 代码模板（错误处理、修复、爬山算法）：`~/.claude/skills/experiment-code/references/code-patterns.md`

## 动作：`generate`

按照以下结构生成初始实验代码：

1. **先规划实验** — 列出所有需要的运行（超参数扫描、消融实验、基线）
2. **编写自包含代码** — 所有代码在项目目录中，不引用参考代码库的外部导入
3. **包含正确的日志记录** — 将结果保存到 JSON 文件，打印中间指标
4. **生成图表** — 至少生成 Figure_1.png 和 Figure_2.png

### 必须的结构
```
project/
├── experiment.py      # 主实验脚本
├── plot.py            # 可视化脚本
├── notes.txt          # 实验描述和结果
├── run_1/             # 第 1 次运行的结果
│   └── final_info.json
├── run_2/
└── ...
```

### 限制条件
- 不得使用占位符代码（`pass`、`...`、`raise NotImplementedError`）
- 必须使用实际数据集（除非明确要求使用玩具数据）
- 优先使用 PyTorch 或 scikit-learn（不使用 TensorFlow/Keras）
- 每次运行使用：`python experiment.py --out_dir=run_i`

## 动作：`improve`

改进现有的实验代码：
1. 阅读当前代码和结果
2. 反思哪些地方有效，哪些地方无效
3. 应用有针对性的修改（优先选择小范围修改而不是完全重写）
4. 重新运行并比较分数
5. 保留表现最好的代码变体

## 动作：`debug`

修复实验代码错误：
1. 阅读错误信息（如果非常长，则截断到最后 1500 个字符）
2. 确定根本原因
3. 应用最小化修复
4. 最多尝试 4 次重试，如果仍然无效则改变方法

## 动作：`plot`

从实验结果生成符合发表标准的图表：
1. 读取所有 `run_*/final_info.json` 文件
2. 生成带有正确标签的比较图表
3. 使用图表生成技能进行样式设计

## 规则

- 写代码前必须先规划实验
- 每次运行后，在 notes.txt 中记录结果
- 包含解释结果含义的打印语句
- 方法必须不能达到 0% 准确率 — 验证准确率计算
- 使用种子进行可重复性
- 每次实验前包含打印语句，解释结果预期展示的内容

## 相关技能
- 上游：[实验设计](../experiment-design/)、[算法设计](../algorithm-design/)
- 下游：[数据分析](../data-analysis/)、[可追溯性](../backward-traceability/)
- 参见：[代码调试](../code-debugging/)、[论文到代码](../paper-to-code/)
