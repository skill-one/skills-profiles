# 文献检索

搜索多个学术数据库以查找相关论文。

## 输入

- `$ARGUMENTS` — 搜索查询（自然语言）

## 脚本

### Semantic Scholar（主要 — 最佳用于机器学习/人工智能，提供BibTeX）
```bash
python ~/.claude/skills/deep-research/scripts/search_semantic_scholar.py \
  --query "QUERY" --max-results 20 --year-range 2022-2026 \
  --api-key "$(grep S2_API_Key /Users/lingzhi/Code/keys.md 2>/dev/null | cut -d: -f2 | tr -d ' ')" \
  -o results_s2.jsonl
```

关键标志：`--peer-reviewed-only`, `--top-conferences`, `--min-citations N`, `--venue NeurIPS ICML`

### arXiv（最新预印本）
```bash
python ~/.claude/skills/deep-research/scripts/search_arxiv.py \
  --query "QUERY" --max-results 10 -o results_arxiv.jsonl
```

### OpenAlex（覆盖范围最广，免费，无需API密钥）
```bash
python ~/.claude/skills/literature-search/scripts/search_openalex.py \
  --query "QUERY" --max-results 20 --year-range 2022-2026 \
  --min-citations 5 -o results_openalex.jsonl
```

### 合并与去重
```bash
python ~/.claude/skills/deep-research/scripts/paper_db.py merge \
  --inputs results_s2.jsonl results_arxiv.jsonl results_openalex.jsonl \
  --output merged.jsonl
```

### CrossRef（基于DOI的查找，类型覆盖范围最广）
```bash
python ~/.claude/skills/literature-search/scripts/search_crossref.py \
  --query "QUERY" --rows 10 --output results_crossref.jsonl
```

关键标志：`--bibtex`（输出.bib格式），`--rows N`

### 下载arXiv源（获取.tex文件）
```bash
python ~/.claude/skills/literature-search/scripts/download_arxiv_source.py \
  --title "Paper Title" --output-dir arxiv_papers/
```

关键标志：`--arxiv-id 1706.03762`, `--metadata`, `--max-results N`

### 从结果生成BibTeX
```bash
python ~/.claude/skills/deep-research/scripts/bibtex_manager.py \
  --jsonl merged.jsonl --output references.bib
```

## 工作流程

1. 将用户的查询扩展为2-4个互补的搜索查询
2. 使用扩展的查询运行Semantic Scholar搜索（主要）
3. 运行arXiv以获取非常近期的预印本（< 3个月）
4. 可选地运行OpenAlex以获取更广泛的覆盖范围
5. 合并和去重结果
6. 按以下权重排序：引用次数（0.3）+ 近期性（0.3）+ 会议质量（0.2）+ 相关性（0.2）
7. 以结构化结果表格的形式呈现

## 会议质量等级

**等级1：** NeurIPS, ICML, ICLR, ACL, EMNLP, NAACL, CVPR, ICCV, ECCV, KDD, AAAI, IJCAI, SIGIR, WWW
**等级2：** AISTATS, UAI, COLT, COLING, EACL, WACV, JMLR, TACL
**等级3：** 工作坊，arXiv预印本 — 标记为`(预印本)`

## 输出格式

以表格形式呈现结果 + 带有BibTeX键的详细条目。始终注明预印本状态。

## 相关技能
- 下游：[引用管理](../citation-management/), [文献综述](../literature-review/), [相关工作撰写](../related-work-writing/)
- 参见：[深度研究](../deep-research/), [新颖性评估](../novelty-assessment/)
