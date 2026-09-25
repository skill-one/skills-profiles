# 研究规划

根据研究主题或想法创建全面的研究计划和论文架构。

## 输入

- `$0` — 研究主题、想法描述或待复制的论文

## 参考文献

- Paper2Code、AI-Researcher、AgentLaboratory 的规划提示：`~/.claude/skills/research-planning/references/planning-prompts.md`
- 输出模式和模板：`~/.claude/skills/research-planning/references/output-schemas.md`

## 工作流程

### 第 1 步：理解研究背景
- 阅读提供的任何论文、代码或参考文献
- 确定核心研究问题及其重要性
- 评估可用资源（数据集、计算资源、现有代码）

### 第 2 步：生成研究计划
使用 4 阶段规划方法（改编自 Paper2Code）：

1. **总体计划** — 战略概述：方法论、关键实验、评估指标
2. **架构设计** — 文件结构、系统设计、Mermaid 类/序列图
3. **逻辑设计** — 任务分解及依赖关系、所需包、共享知识
4. **配置** — 提取或指定超参数、训练细节、config.yaml

### 第 3 步：构建论文结构
设计论文结构并按章节规划：
- 摘要、引言、背景、相关工作、方法、实验、结果、讨论/结论
- 每个章节：需涵盖的关键点、所需图表、目标字数

### 第 4 步：创建任务依赖图
- 按依赖关系排序任务（数据 → 模型 → 训练 → 评估 → 写作）
- 识别可并行任务
- 标记风险和潜在失败模式

## 输出格式

```json
{
  "research_question": "...",
  "methodology": "...",
  "paper_structure": {
    "sections": ["Abstract", "Introduction", ...],
    "section_plans": { "Introduction": "..." }
  },
  "task_list": [
    {"task": "...", "depends_on": [], "priority": 1}
  ],
  "baselines": ["..."],
  "datasets": ["..."],
  "evaluation_metrics": ["..."],
  "risks": ["..."]
}
```

## 规则

- 每个计划组件必须详细且可执行
- 在可用时包含具体的实现参考
- 确保所有组件协同一致
- 始终包含测试/评估计划
- 明确标记歧义，而非假设

## 相关技能
- 上游：[想法生成](../idea-generation/)、[文献综述](../literature-review/)
- 下游：[实验设计](../experiment-design/)、[论文组装](../paper-assembly/)
- 参见：[原子分解](../atomic-decomposition/)
