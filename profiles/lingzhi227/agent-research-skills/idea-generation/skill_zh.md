# 创意生成

通过文献支持的原创性评估，生成和改进新颖的科研想法。

## 输入

- `$0` — 研究领域、任务描述或现有代码库背景
- `$1` — 可选：附加背景信息（例如，“用于NeurIPS”，约束条件）

## 脚本

### 与Semantic Scholar进行原创性检查
```bash
python ~/.claude/skills/idea-generation/scripts/novelty_check.py \
  --idea "通过梯度引导的重要性自适应注意力头剪枝" \
  --max-rounds 5
```

执行迭代文献搜索，以评估想法是否新颖。

## 参考文献

- 创意提示（生成、反思、原创性）：`~/.claude/skills/idea-generation/references/ideation-prompts.md`

## 工作流程

### 第1步：生成想法
给定研究领域和可选的代码/论文背景：
1. 生成3-5个多样化的研究想法
2. 对每个想法，提供：名称、标题、实验计划以及评分
3. 使用参考文献中的创意提示模板

### 第2步：迭代改进（每个想法最多5轮）
对每个想法：
1. 批判性地评估质量、原创性和可行性
2. 在保持其核心精神的同时改进想法
3. 当收敛（“我完成了”）或达到最大轮数时停止

### 第3步：原创性评估
对每个有潜力的想法：
1. 运行 `novelty_check.py` 或手动搜索Semantic Scholar / arXiv
2. 使用参考文献中的原创性检查提示
3. 多轮搜索：生成查询、审查结果、决定
4. 二元决策：原创 / 非原创并说明理由

### 第4步：排序和选择
- 在三个维度（1-10）上对每个想法进行评分：趣味性、可行性、原创性
- 对评分要谨慎和现实
- 选择最优秀的想法进行开发

## 输出格式

```json
{
  "Name": "adaptive_attention_pruning",
  "Title": "Adaptive Attention Head Pruning via Gradient-Guided Importance Scoring",
  "Experiment": "详细的实施计划...",
  "Interestingness": 8,
  "Feasibility": 7,
  "Novelty": 9,
  "novel": true,
  "most_similar_papers": ["paper1", "paper2"]
}
```

## 规则

- 想法必须在使用现有资源的情况下可行（不要求新的数据集或大量计算）
- 不要让想法过度拟合特定的数据集或模型——力求更广泛的显著性
- 对原创性要严苛——确保对会议论文有足够的贡献
- 每个想法应源于一个简单、优雅的问题或假设
- 在决定采纳想法之前，始终检查其原创性

## 相关技能
- 上游：[文献搜索](../literature-search/)、[深入研究](../deep-research/)
- 下游：[研究计划](../research-planning/)、[实验设计](../experiment-design/)
- 参见：[原创性评估](../novelty-assessment/)
