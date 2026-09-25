# 原子分解

将研究想法分解为原子概念，通过数学公式 <-> 代码实现映射。

## 输入

- `$0` — 研究想法、论文或方法描述

## 参考文献

- 分解提示和工作流：`~/.claude/skills/atomic-decomposition/references/decomposition-prompts.md`

## 工作流（来自 AI-Researcher 调查代理）

### 第 1 步：分解为原子定义
分析研究想法并分解为原子、自包含的概念：
- 每个原子应是一个单一概念
- 必须有明确的数学基础
- 必须可以在代码中实现
- 必须可追溯到特定论文

### 第 2 步：针对每个原子定义

#### A. 论文调查（数学公式）
- 搜索论文以获取数学公式
- 提取确切的 LaTeX 公式
- 记录假设和约束
- 记录参考论文

#### B. 代码调查（实现）
- 搜索代码库以获取实现
- 提取相应的代码
- 记录实现细节和变体
- 记录参考仓库

#### C. 创建知识条目
```json
{
  "definition": "核化 Gumbel-Softmax 算子",
  "math_formula": "Z = \\text{softmax}((\\log \\pi + g) / \\tau), g \\sim \\text{Gumbel}(0,1)",
  "code_implementation": "def gumbel_softmax(logits, tau=1.0): ...",
  "reference_papers": ["论文标题 1"],
  "reference_codebases": ["github_user/repo_name"],
  "assumptions": ["可微离散采样的松弛"],
  "connections": ["用于提出方法中的组件 X"]
}
```

### 第 3 步：编译知识库
- 将所有原子定义合并到一个结构化的知识库中
- 验证一致性：每个数学公式都有一个代码实现
- 验证完整性：每个代码模块可追溯到一个形式化定义
- 识别任何差距（没有代码的公式，或没有理论的代码）

## 规则

- 每个原子定义必须足够具体，可追溯到具体的公式和代码
- 不要跳过或合并定义——单独分析每个
- 如果不确定原子性，倾向于进一步分解
- 在分析前记录分解理由
- 论文中的每个数学概念都必须有验证过的代码
- 每个代码模块都必须追溯到一个形式化的数学定义

## 相关技能
- 上游：[研究规划](../research-planning/), [想法生成](../idea-generation/)
- 下游：[实验代码](../experiment-code/), [算法设计](../algorithm-design/)
- 参见：[数学推理](../math-reasoning/)
