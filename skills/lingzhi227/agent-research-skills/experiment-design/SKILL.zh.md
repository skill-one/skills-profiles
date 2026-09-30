---
name: experiment-design
description: 设计具有渐进式阶段的实验计划——初始实施、基线调优、创意研究和消融研究。规划基线、数据集、超参数扫描和评估指标。在为研究论文规划实验时使用。
---

# 实验设计

为研究论文设计结构化、逐步推进的实验计划。

## 输入

- `$0` — 研究想法、计划或方法描述

## 参考文献

- 4阶段逐步推进实验提示：`~/.claude/skills/experiment-design/references/stage-prompts.md`

## 脚本

### 生成实验设计
```bash
python ~/.claude/skills/experiment-design/scripts/design_experiments.py --plan research_plan.json --output experiment_design.json
python ~/.claude/skills/experiment-design/scripts/design_experiments.py --method "对比学习" --task 分类 --format markdown
```

生成基线、消融矩阵、超参数网格、指标选择。仅使用标准库。

## 4阶段逐步推进框架 (来自 AI-Scientist-v2)

### 阶段1：初始实现
- 专注于获得一个基本的可工作实现
- 使用简单的数据集
- 目标是基本的功能正确性
- 完成：至少有一个可工作的（无bug）实现

### 阶段2：基线调优
- 调整超参数（学习率、轮数、批大小）
- 不要改变模型架构
- 在至少两个数据集上测试
- 完成：稳定的训练曲线，比阶段1有所改进

### 阶段3：创造性研究
- 探索新颖的改进和见解
- 充分发挥创造力，跳出思维定式
- 在至少三个数据集上测试
- 完成：展示了新颖的改进

### 阶段4：消融研究
- 系统化的组件分析
- 每个消融测试不同的方面
- 使用与阶段3相同的数据库
- 完成：所有计划的消融都已完成

## 输出格式

```json
{
  "stages": [
    {
      "name": "initial_implementation",
      "goals": ["基本可工作的基线", "简单数据集"],
      "max_iterations": 5,
      "completion_criteria": "具有非零准确性的可工作实现"
    }
  ],
  "baselines": ["方法A", "方法B"],
  "datasets": ["Dataset1", "Dataset2", "Dataset3"],
  "metrics": ["准确率", "F1", "推理时间"],
  "ablation_components": ["组件A", "组件B"],
  "hyperparameter_grid": {
    "lr": [1e-4, 1e-3, 1e-2],
    "batch_size": [32, 64, 128]
  },
  "num_seeds": 3
}
```

## 规则

- 始终从简单（阶段1）开始，再进行复杂的实验
- 每个阶段都建立在上一阶段最佳结果的基础上
- 多种子评估以获得统计显著性
- 在 notes.txt 中记录每个实验运行
- 生成训练曲线和比较的图表

## 相关技能
- 上游：[研究规划](../research-planning/)，[想法生成](../idea-generation/)
- 下游：[实验代码](../experiment-code/)，[数据分析](../data-analysis/)
- 参见：[论文组装](../paper-assembly/)
