---
name: math-reasoning
description: 用于研究论文的正式数学推理——推导方程、撰写证明、形式化问题设定、选择统计检验，以及生成LaTeX数学符号。当用户需要数学推导、定理证明、符号表或统计分析形式化时使用。
---

# 数学推理

执行严谨的数学推理，并生成符合发表标准的 LaTeX 输出。

## 输入

- `$0` — 任务类型：`derive`（推导）、`prove`（证明）、`formalize`（形式化）、`stats`（统计）、`notation`（符号）、`verify`（验证）
- `$1` — 上下文：方程式、定理陈述、问题描述或数据描述

## 任务

### `derive` — 步骤化方程式推导
展示每个中间步骤。用所应用的规则进行说明。用 `\boxed{}` 框出最终结果。用 `\label{eq:name}` 对重要方程编号。

### `prove` — 形式化定理证明
使用适当的技术：直接证明、反证法、归纳法、构造法或分情况讨论。参考 `references/proof-templates.md` 中的 LaTeX 模板。

### `formalize` — 问题描述形式化
将非正式描述转换为形式化数学框架，包括：变量定义、定义域/值域说明、假设、目标函数。

### `stats` — 统计检验选择
使用 `references/notation-guide.md` 中的决策树选择适当的检验。报告 p 值、效应量、置信区间。

### `notation` — 生成符号表
创建一个 `\begin{table}`，包含论文中使用的所有符号。使用 `references/notation-guide.md` 中的标准 ML 符号。

### `verify` — 检查数学正确性
验证：维度一致性、边界情况、梯度计算、各章节符号一致性。

## 参考文献

- 标准 ML 符号 + 统计检验：`~/.claude/skills/math-reasoning/references/notation-guide.md`
- 证明模板和定理环境：`~/.claude/skills/math-reasoning/references/proof-templates.md`

## 规则

- 在首次使用前定义所有符号："令 $\mathcal{X}$ 表示..."
- 在全文中使用一致的符号
- 对后续会引用的方程编号
- 用 `\tag{reason}` 标注关键推导步骤
- 明确陈述假设
- 引用证明中使用的引理和已有结果

## 相关技能
- 上游：[研究规划](../research-planning/)
- 下游：[算法设计](../algorithm-design/)、[论文写作章节](../paper-writing-section/)
- 参见：[符号方程式](../symbolic-equation/)、[数据分析](../data-analysis/)
