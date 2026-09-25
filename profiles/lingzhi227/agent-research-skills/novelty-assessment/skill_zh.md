# 新颖性评估

通过系统文献检索，严格评估研究想法是否新颖。

## 输入

- `$0` — 研究想法描述、标题或 JSON 文件

## 脚本

### 自动新颖性检查
```bash
python ~/.claude/skills/idea-generation/scripts/novelty_check.py \
  --idea "您的研究想法描述" \
  --max-rounds 10 --output novelty_report.json
```

### 文献检索
```bash
python ~/.claude/skills/deep-research/scripts/search_semantic_scholar.py \
  --query "相关检索查询" --max-results 10
```

## 参考文献

- 评估提示和标准：`~/.claude/skills/novelty-assessment/references/assessment-prompts.md`

## 工作流程

### 第 1 步：理解想法
- 确定核心贡献
- 列出关键技术组件
- 确定研究领域和子领域

### 第 2 步：多轮文献检索（最多 10 轮）
每轮操作：
1. 生成目标检索查询
2. 检索 Semantic Scholar / arXiv / OpenAlex
3. 审阅前 10 条结果及摘要
4. 评估与想法的重叠程度
5. 决定：需要更多检索，还是准备做出判断

### 第 3 步：做出决策
- **新颖**：经过充分检索后，没有论文显著重叠
- **不新颖**：发现一篇显著重叠的论文

### 第 4 步：定位想法
如果新颖，需识别：
- 最相似的现有论文（用于相关工作）
- 想法与每篇论文的不同之处
- 该想法填补的具体空白

## 严苛批评者角色

```
扮演一个严苛的新颖性批评者。确保新贡献足以发表在会议或研讨会论文中。现有工作的琐碎扩展**不**算新颖。该想法必须提供有意义的不同方法、公式或见解。
```

## 输出格式

```json
{
  "decision": "novel" | "not_novel",
  "confidence": "high" | "medium" | "low",
  "justification": "经过检索 X 轮后...",
  "most_similar_papers": [
    {"title": "...", "year": 2024, "overlap": "..."}
  ],
  "differentiation": "我们的想法之所以不同，因为..."
}
```

## 规则

- 至少 3 轮检索后才能声明新颖
- 尽力回忆目标查询的精确论文名称
- 如果是现有工作的琐碎扩展，想法**不**算新颖
- 考虑方法新颖性和应用新颖性
- 检查并发/近期 arXiv 提交

## 相关技能
- 上游：[文献检索](../literature-search/)，[深度研究](../deep-research/)
- 下游：[想法生成](../idea-generation/)，[研究规划](../research-planning/)
- 参见：[相关工作撰写](../related-work-writing/)
