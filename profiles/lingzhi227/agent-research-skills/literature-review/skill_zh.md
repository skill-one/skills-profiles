# 文献综述

通过多视角对话和系统化检索进行深入的文献综述。

## 输入

- `$0` — 研究主题或问题
- `$1` — 可选：特定的关注点或角度

## 参考文献

- 多视角对话提示（STORM）：`~/.claude/skills/literature-review/references/dialogue-prompts.md`
- 文献综述工作流（AgentLaboratory）：`~/.claude/skills/literature-review/references/review-workflow.md`

## 脚本（来自文献检索技能）

```bash
# 搜索Semantic Scholar
python ~/.claude/skills/deep-research/scripts/search_semantic_scholar.py --query "topic" --max-results 20

# 搜索OpenAlex
python ~/.claude/skills/literature-search/scripts/search_openalex.py --query "topic" --max-results 20

# 搜索arXiv
python ~/.claude/skills/deep-research/scripts/search_arxiv.py --query "topic" --max-results 10
```

## 工作流

### 第一步：生成专家角色（来自STORM）
根据主题，创建3-5个不同的专家角色：
- 每个角色代表不同的视角、角色或研究角度
- 示例："专注于效率的机器学习系统研究者"、"关注保证的理论统计学家"
- 使用参考文献中的角色生成提示

### 第二步：多视角对话
针对每个角色，模拟多轮问答对话：
1. **角色提出问题**，从其独特角度出发
2. **根据问题生成搜索查询**
3. **使用搜索脚本检索文献**
4. **基于检索到的论文合成答案**，并添加内联引用
5. **记录对话回合**，包含搜索结果
6. 每个角色重复3-5轮对话
7. 当角色说"非常感谢您的帮助！"时结束

### 第三步：知识合成
- 将所有角色的对话合并为一个统一的知识库
- 消除角色之间的冗余
- 按主题/子主题组织
- 根据收集的信息生成大纲

### 第四步：生成文献综述
- 按照生成的大纲撰写结构化综述
- 每个论点必须得到引用支持
- 包含关键论文的总结表格（方法、贡献、局限性）

## 输出

结构化的文献综述，包含：
1. **大纲** — 分层主题结构
2. **各部分摘要** — 每部分基于检索到的论文
3. **论文数据库** — 所有已综述论文的结构化条目
4. **知识空白** — 需要进一步研究的领域

## 规则

- 综述中的每句话都必须得到收集的信息支持
- 如果信息未找到，明确指出空白
- 广泛引用 — 涵盖多种方法，而不仅是最流行的方法
- 包含近期的论文（最后2-3年），与基础性工作并存
- 使用内联引用："Smith等人[1]提出..."

## 相关技能
- 上游：[literature-search](../literature-search/)，[deep-research](../deep-research/)
- 下游：[related-work-writing](../related-work-writing/)，[research-planning](../research-planning/)
- 参见：[survey-generation](../survey-generation/)
