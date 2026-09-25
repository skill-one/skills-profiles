# 问卷生成

生成完整的学术论文问卷，包含结构化大纲、基于RAG的写作和引用验证。

## 输入

- `$0` — 问卷主题或研究领域

## 脚本

### 文献检索
```bash
python ~/.claude/skills/deep-research/scripts/search_semantic_scholar.py \
  --query "相关检索查询" --max-results 50
```

## 参考文献

- 问卷提示（大纲、写作、引用、连贯性）：`~/.claude/skills/survey-generation/references/survey-prompts.md`

## 工作流程（来自AutoSurvey）

### 第1步：收集论文
1. 在Semantic Scholar / arXiv上搜索主题相关的论文
2. 收集50-200篇相关论文，包含标题和摘要
3. 根据相关性和引用次数进行筛选

### 第2步：生成大纲（多LLM并行）
1. 独立并行生成N个粗略大纲
2. 合并大纲为一个全面的综合大纲
3. 将每个部分扩展为子部分
4. 编辑最终大纲以删除冗余内容

### 第3步：撰写子部分（基于RAG）
针对每个子部分：
1. 检索与子部分主题相关的论文
2. 生成带内联引用的内容 `[论文标题]`
3. 执行每个子部分的最小字数要求
4. 仅引用提供的论文列表中的论文

### 第4步：验证引用
针对每个子部分：
1. 检查引用的论文标题是否正确
2. 验证引用是否支持所提出的论点
3. 删除或纠正不支持的引用
4. 使用NLI（自然语言推理）进行论点-来源忠实度验证

### 第5步：增强局部连贯性
针对每个子部分：
1. 阅读前一个和后一个子部分
2. 优化过渡和流程
3. 保留核心内容和引用
4. 确保流畅的阅读体验

### 第6步：转换为BibTeX
1. 将`[论文标题]`替换为`\cite{key}`
2. 为所有引用的论文生成BibTeX条目
3. 验证所有引用键在.bib文件中存在

## 输出结构

```
survey/
├── main.tex          # 完整的问卷论文
├── references.bib    # 所有引用
├── outline.json      # 问卷大纲
└── sections/         # 单独的章节文件
```

## 规则

- 仅引用收集的论文列表中的论文——绝不凭空捏造引用
- 每个子部分必须满足最小字数要求
- 各章节之间不得存在重复的子部分
- 最终输出前必须执行引用验证
- 局部连贯性增强必须保留所有引用
- 问卷应全面且逻辑组织合理

## 相关技能
- 上游：[deep-research](../deep-research/), [literature-search](../literature-search/), [literature-review](../literature-review/)
- 参见：[related-work-writing](../related-work-writing/)
