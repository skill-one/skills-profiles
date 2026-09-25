# 论文组装

通过状态管理和检查点机制，端到端地编排整个论文流程。

## 输入

- `$0` — 论文项目目录或论文计划

## 参考文献

- 编排模式和状态管理：`~/.claude/skills/paper-assembly/references/orchestration-patterns.md`

## 脚本

### 检查流程完整性
```bash
python ~/.claude/skills/paper-assembly/scripts/assembly_checker.py --dir paper/ --output checkpoint.json
python ~/.claude/skills/paper-assembly/scripts/assembly_checker.py --dir paper/ --verbose
```

扫描论文目录，检查9个流程阶段，报告缺失的工件，建议下一步操作。

## 工作流

### 第1步：评估当前状态
1. 扫描论文目录以查找现有工件
2. 确定哪些阶段已完成，哪些待处理
3. 构建剩余工作的依赖图

### 第2步：执行流程阶段
按依赖顺序运行阶段：

| 阶段 | 技能 | 输入 | 输出 |
|------|------|------|------|
| 1. 文献调研 | literature-search, literature-review | 主题 | 知识库, BibTeX |
| 2. 规划 | research-planning | 知识库 | 论文结构, 任务列表 |
| 3. 代码 | experiment-code | 计划 | 训练/评估流程 |
| 4. 实验 | experiment-design | 代码 | 结果 JSON/CSV |
| 5. 图表 | figure-generation | 结果 | PNG 图表 |
| 6. 表格 | table-generation | 结果 | LaTeX 表格 |
| 7. 写作 | paper-writing-section | 以上所有 | main.tex 章节 |
| 8. 引用 | citation-management | 草稿 | references.bib |
| 9. 格式化 | latex-formatting | 草稿 | 格式化 LaTeX |
| 10. 编译 | paper-compilation | 以上所有 | PDF |
| 11. 审查 | self-review | PDF | 审查分数 |

### 第3步：状态传播
每个阶段完成后：
1. 将输出工件保存到论文目录
2. 将结果传播到下游阶段
3. 更新进度检查点文件

### 第4步：质量门禁
在进行下一个阶段之前：
- 验证所有必需的输出是否存在
- 检查一致性（例如，所有 .bib 中的引用键）
- 验证图表/表格与实验结果一致

### 第5步：最终组装
1. 将所有章节合并到 main.tex
2. 验证所有 \includegraphics 文件是否存在
3. 验证所有 \cite 键存在于 .bib
4. 编译为 PDF
5. 运行自我审查进行质量检查

## 编排模式

### 顺序流程（AI-科学家）
```
generate_ideas → experiments → writeup → review
```

### 多代理状态广播（AgentLaboratory）
```python
# 将结果传播到所有下游代理
set_agent_attr("dataset_code", code)
set_agent_attr("results", results_json)
```

### 协作者模式（AgentLaboratory）
人类可以在任何阶段边界处进行审查/修正。

## 检查点格式

```json
{
  "project": "paper-name",
  "phases_completed": ["literature", "planning", "code"],
  "current_phase": "experiments",
  "artifacts": {
    "literature": "knowledge_base.json",
    "plan": "research_plan.json",
    "code": "experiments/",
    "results": null
  },
  "last_updated": "2024-01-15T10:30:00Z"
}
```

## 规则

- 不要跳过任何阶段——每个阶段都依赖于前一个输出
- 每个阶段完成后保存检查点
- 建议在阶段边界进行人工审查
- 论文中的所有数字必须追溯到实际的实验日志
- 如果上游发生变化，重新运行下游阶段

## 相关技能
- 上游：所有其他技能（这是编排者）
- 下游：[paper-compilation](../paper-compilation/), [self-review](../self-review/)
- 参见：[research-planning](../research-planning/)
