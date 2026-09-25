# 引用管理

管理 LaTeX 论文中引用的完整生命周期。

## 输入

- `$0` — 操作：`harvest`、`validate`、`add`、`format`
- `$1` — `.tex` 或 `.bib` 文件的路径

## 脚本

### 验证引用（检查所有引用键是否解析）
```bash
python ~/.claude/skills/citation-management/scripts/validate_citations.py \
  --tex paper/main.tex --bib paper/references.bib --check-figures --figures-dir paper/figures/
```

报告：缺失引用、未使用的 bib 条目、重复键、重复章节、重复标签、未定义引用、缺失图表。

### 从论文数据库生成 BibTeX
```bash
python ~/.claude/skills/deep-research/scripts/bibtex_manager.py \
  --jsonl paper_db.jsonl --output references.bib
```

### 搜索特定论文以添加
```bash
python ~/.claude/skills/deep-research/scripts/search_semantic_scholar.py \
  --query "attention is all you need" --max-results 5 \
  --api-key "$(grep S2_API_Key /Users/lingzhi/Code/keys.md 2>/dev/null | cut -d: -f2 | tr -d ' ')"
```

### 自动收集缺失引用
```bash
python ~/.claude/skills/citation-management/scripts/harvest_citations.py \
  --tex paper/main.tex --bib paper/references.bib --output candidates.bib --max-rounds 10
```

扫描 .tex 文件以查找未引用的声明，搜索 Semantic Scholar，输出候选 BibTeX 条目。
关键标志：`--dry-run`（仅预览）、`--verbose`、`--api-key`

### 自动修复缺失引用占位符
```bash
python ~/.claude/skills/citation-management/scripts/validate_citations.py \
  --tex paper/main.tex --bib paper/references.bib --fix
```

生成 `references_fixed.bib`，为所有缺失的引用键创建占位符条目。

## 操作：`harvest` — 迭代引用收集

基于 AI-Scientist 的 20 轮引用收集循环。每一轮：

1. 读取当前的 `.tex` 草稿
2. 识别最重要的缺失引用
3. 通过脚本搜索 Semantic Scholar
4. 从结果中选择最相关的论文
5. 提取 BibTeX 并生成干净的键 (`lastNameYearWord`)
6. 追加到 `.bib`（如果键已存在则跳过）
7. 在适当的位置插入 `\cite{key}`
8. 当没有更多空缺或达到 20 轮时停止

**关键规则：**
- 不要添加已存在的引用
- 仅通过 API 查找引用——绝不编造
- 广泛引用——不仅限于热门论文
- 不要从先前文献中逐字复制

## 操作：`validate` — 编译前检查

运行 `validate_citations.py` 以在编译前捕获所有问题。修复报告的任何问题。

## 操作：`add` — 添加特定论文

搜索 Semantic Scholar 以查找论文，提取 BibTeX，清理键，追加到 `.bib`。

BibTeX 键格式：`firstAuthorLastNameYearFirstContentWord`（例如，`vaswani2017attention`）

## 操作：`format` — 标准化 .bib

- 按键字母顺序排序条目
- 确保一致的缩进（2 个空格）
- 删除空字段
- 在标题中使用 `{Braces}` 保护专有名词
- 确保每个条目类型的必填字段

## 相关技能
- 上游：[literature-search](../literature-search/)、[deep-research](../deep-research/)
- 下游：[paper-compilation](../paper-compilation/)、[latex-formatting](../latex-formatting/)
- 参见：[related-work-writing](../related-work-writing/)
