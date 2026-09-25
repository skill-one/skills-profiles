# 深入研究技能

## 触发条件

在用户想要执行以下操作时激活此技能：
- "研究一个主题"、"文献综述"、"查找关于...的论文"、"关于...的综述论文"
- "深入探究[主题]"、"在[主题]领域的技术现状"
- 使用`/research <主题>`斜杠命令

## 概述

此技能通过6个阶段进行系统的学术文献综述，生成结构化笔记、精选论文数据库和综合最终报告。输出按阶段组织，以便清晰。

**安装位置**：`~/.claude/skills/deep-research/` — 脚本、参考文献和此技能定义。
**输出位置**：相对于当前工作目录的`.//Users/lingzhi/Code/deep-research-output/{slug}/`。

## 关键：严格按顺序执行阶段

**你必须严格按照1 → 2 → 3 → 4 → 5 → 6的顺序执行所有6个阶段：绝不能跳过任何阶段。**

这是此技能最重要的规则。违规行为包括：
- ❌ 从阶段2跳到阶段5/6（跳过深入探究和代码）
- ❌ 在完成阶段3深入阅读之前编写综合或报告
- ❌ 仅基于搜索结果的摘要/标题生成最终报告
- ❌ 合并或合并阶段（例如，执行"阶段3-5一起"）

### 阶段门禁协议

在开始阶段N+1之前，你必须验证阶段N的**必需输出文件**是否存在于磁盘。如果不存在，则表示你没有完成该阶段。

| 阶段 | 门禁：必需输出文件 |
|------|-------------------|
| 1 → 2 | `phase1_frontier/frontier.md`存在且包含≥10篇论文 |
| 2 → 3 | `phase2_survey/survey.md`存在且`paper_db.jsonl`包含35-80篇论文 |
| 3 → 4 | `phase3_deep_dive/selection.md`和`phase3_deep_dive/deep_dive.md`都存在且`deep_dive.md`包含≥8篇论文的详细笔记 |
| 4 → 5 | `phase4_code/code_repos.md`存在且包含≥3个仓库 |
| 5 → 6 | `phase5_synthesis/synthesis.md`和`phase5_synthesis/gaps.md`都存在 |

**完成每个阶段后，打印阶段完成检查点：**
```
✅ 阶段N完成。输出：[列出写入的文件]。继续执行阶段N+1。
```

### 每个阶段的重要性

- **阶段3（深入探究）** 是你实际阅读论文的地方——没有它，你的综合分析将是肤浅的，仅基于摘要
- **阶段4（代码与工具）** 将研究与实践实现相结合——没有它，你将错过开源生态系统
- **阶段5（综合分析）** 需要阶段3的深入知识——你不能综合你没有阅读的论文
- **阶段6（报告）** 汇集了所有先前阶段的内容——它应引用阶段3笔记中的具体发现

## 论文质量政策

**同行评审的会议论文优先于arXiv预印本。** 许多arXiv论文尚未经过同行评审，可能包含未经验证的声明。

### 源优先级（从高到低）
1. **顶级AI会议**：NeurIPS、ICLR、ICML、ACL、EMNLP、NAACL、AAAI、IJCAI、CVPR、KDD、CoRL
2. **同行评审期刊**：JMLR、TACL、Nature、Science等
3. **研讨会论文**：NeurIPS/ICML研讨会（标准较低但仍经过评审）
4. **高引用的arXiv预印本**：可能质量高但未经验证
5. **最新的arXiv预印本**：谨慎使用，明确注明"预印本"状态

### 使用arXiv论文的时机
- 作为**补充证据**与同行评审作品一起使用
- 用于**非常新**的结果（< 3个月旧）尚未在会议上发表
- 当同行评审版本不存在时——引用时注明`(preprint)`
- 用于**综述/评论**论文（即使没有同行评审也很有用）

## 搜索工具（按优先级）

### 1. paper_finder（主要——仅限会议论文）
**位置**：`/Users/lingzhi/Code/documents/tool/paper_finder/paper_finder.py`

在ai-paper-finder.info（HuggingFace Space）搜索已发表的会议论文。支持按会议+年份筛选。输出JSONL格式的BibTeX。

```bash
python /Users/lingzhi/Code/documents/tool/paper_finder/paper_finder.py --mode scrape --config <config.yaml>
python /Users/lingzhi/Code/documents/tool/paper_finder/paper_finder.py --mode download --jsonl <results.jsonl>
python /Users/lingzhi/Code/documents/tool/paper_finder/paper_finder.py --list-venues
```

配置示例：
```yaml
searches:
  - query: "long horizon reasoning agent"
    num_results: 100
    venues:
      neurips: [2024, 2025]
      iclr: [2024, 2025, 2026]
      icml: [2024, 2025]
output:
  root: /Users/lingzhi/Code/deep-research-output/{slug}/phase1_frontier/search_results
  overwrite: true
```

### 2. search_semantic_scholar.py（补充——引文数据+更广泛的覆盖范围）
**位置**：`/Users/lingzhi/.claude/skills/deep-research/scripts/search_semantic_scholar.py`
支持`--peer-reviewed-only`和`--top-conferences`过滤器。API密钥：`/Users/lingzhi/Code/keys.md`（字段`S2_API_Key`）

### 3. search_arxiv.py（补充——最新预印本）
**位置**：`/Users/lingzhi/.claude/skills/deep-research/scripts/search_arxiv.py`
用于搜索尚未在会议上发表的近期论文。引文标注为`(preprint)`。

### 其他脚本
| 脚本 | 位置 | 关键标志 |
|------|------|----------|
| `download_papers.py` | `~/.claude/skills/deep-research/scripts/` | `--jsonl`, `--output-dir`, `--max-downloads`, `--sort-by-citations` |
| `extract_pdf.py` | `~/.claude/skills/deep-research/scripts/` | `--pdf`, `--pdf-dir`, `--output-dir`, `--sections-only` |
| `paper_db.py` | `~/.claude/skills/deep-research/scripts/` | 子命令：`merge`, `search`, `filter`, `tag`, `stats`, `add`, `export` |
| `bibtex_manager.py` | `~/.claude/skills/deep-research/scripts/` | `--jsonl`, `--output`, `--keys-only` |
| `compile_report.py` | `~/.claude/skills/deep-research/scripts/` | `--topic-dir` |

### WebFetch模式（无需Bash）
1. **论文发现**：`WebSearch` + `WebFetch`查询Semantic Scholar/arXiv API
2. **论文阅读**：`WebFetch`在ar5iv HTML上或`Read`工具在下载的PDF上
3. **写作**：`Write`工具用于JSONL、笔记、报告文件

## 6阶段工作流程

### 阶段1：前沿
搜索最新的会议录和预印本，了解当前趋势。
1. 编写`phase1_frontier/paper_finder_config.yaml`，目标为最近1-2年
2. 运行paper_finder抓取
3. WebSearch最新接受的论文列表
4. 确定趋势方向、关键突破
→ 输出：`phase1_frontier/frontier.md`, `phase1_frontier/search_results/`

### 阶段2：综述
构建更广泛时间范围内的综合图景。筛选后目标**35-80篇论文**。
1. 编写`phase2_survey/paper_finder_config.yaml`，覆盖2023-2025年
2. 运行paper_finder + Semantic Scholar + arXiv
3. 合并所有结果：`python /Users/lingzhi/.claude/skills/deep-research/scripts/paper_db.py merge`
4. 筛选至35-80篇最相关的：`python /Users/lingzhi/.claude/skills/deep-research/scripts/paper_db.py filter --min-score 0.80 --max-papers 70`
5. 按主题聚类，撰写综述笔记
→ 输出：`phase2_survey/survey.md`, `phase2_survey/search_results/`, `paper_db.jsonl`

### 阶段3：深入探究 ⚠️ 绝不能跳过

**此阶段是强制性的。** 你必须实际阅读8-15篇完整论文，而不仅仅是它们的摘要。

1. 从paper_db.jsonl中选择8-15篇论文并说明理由→编写`phase3_deep_dive/selection.md`
2. 下载PDF：`python download_papers.py --jsonl paper_db.jsonl --output-dir phase3_deep_dive/papers/ --sort-by-citations --max-downloads 15`
3. 对于每篇选定的论文，阅读全文（PDF通过`Read`或HTML通过`WebFetch`在ar5iv上）
4. 按论文编写详细的结构化笔记（见note-format.md模板）：问题、贡献、方法、实验、局限性、联系
5. 编写所有笔记→`phase3_deep_dive/deep_dive.md`

**阶段3门禁**：`deep_dive.md`必须包含≥8篇论文的详细笔记，每篇论文都必须填写方法和实验部分。仅摘要的总结不计数。

→ 输出：`phase3_deep_dive/selection.md`, `phase3_deep_dive/deep_dive.md`, `phase3_deep_dive/papers/`

### 阶段4：代码与工具 ⚠️ 绝不能跳过

**此阶段是强制性的。** 你必须调查开源生态系统。

1. 从阶段3阅读的论文中提取GitHub URL
2. WebSearch实现："site:github.com {方法名}"，"site:paperswithcode.com {主题}"
3. 对于每个找到的仓库：记录URL、星标、语言、最后更新、文档质量
4. 搜索相关基准和数据集
5. 编写→`phase4_code/code_repos.md`（必须包含≥3个仓库）

**阶段4门禁**：`code_repos.md`必须存在且至少包含3个带元数据的仓库。

→ 输出：`phase4_code/code_repos.md`

### 阶段5：综合分析（需要阶段3+4完成）
跨论文分析。**优先考虑同行评审的发现**。
此阶段必须基于阶段3的详细笔记和阶段4的代码图景。
分类法、比较表、差距分析。

**开始前**：验证`phase3_deep_dive/deep_dive.md`和`phase4_code/code_repos.md`是否存在。如果不存在，请先完成这些阶段。

→ 输出：`phase5_synthesis/synthesis.md`, `phase5_synthesis/gaps.md`

### 阶段6：编译（需要阶段1-5完成）
从所有先前阶段输出汇编最终报告。用`(preprint)`后缀标注预印本引文。

**开始前**：验证所有阶段输出是否存在：
- `phase1_frontier/frontier.md`
- `phase2_survey/survey.md`
- `phase3_deep_dive/deep_dive.md`
- `phase4_code/code_repos.md`
- `phase5_synthesis/synthesis.md` + `gaps.md`

如果任何缺失，请先完成缺失的阶段。

→ 输出：`phase6_report/report.md`, `phase6_report/references.bib`

## 输出目录

```
output/{topic-slug}/
├── paper_db.jsonl                    # 主数据库（累积）
├── phase1_frontier/
│   ├── paper_finder_config.yaml
│   ├── search_results/
│   └── frontier.md
├── phase2_survey/
│   ├── paper_finder_config.yaml
│   ├── search_results/
│   └── survey.md
├── phase3_deep_dive/
│   ├── papers/
│   ├── selection.md
│   └── deep_dive.md
├── phase4_code/
│   └── code_repos.md
├── phase5_synthesis/
│   ├── synthesis.md
│   └── gaps.md
└── phase6_report/
    ├── report.md
    └── references.bib
```

## 关键约定

- **论文ID**：有arxiv_id时使用，否则使用Semantic Scholar `paperId`
- **引文**：`[@key]`格式，key = firstAuthorYearWord（例如，`[@vaswani2017attention]`）
- **JSONL schema**：标题、作者、摘要、年份、会议、会议标准化、**同行评审**、引用计数、paperId、arxiv_id、pdf_url、标签、来源
- **预印本标注**：引用非同行评审工作时始终注明`(preprint)`
- **增量保存**：每个阶段立即写入磁盘
- **论文数量**：最终paper_db.jsonl目标35-80篇（使用`paper_db.py filter`）

## 参考文献

- `/Users/lingzhi/.claude/skills/deep-research/references/workflow-phases.md` — 详细6阶段方法
- `/Users/lingzhi/.claude/skills/deep-research/references/note-format.md` — 笔记模板、BibTeX格式、报告结构
- `/Users/lingzhi/.claude/skills/deep-research/references/api-reference.md` — arXiv、Semantic Scholar、ar5iv API指南

## 相关技能
- 下游：[literature-search](../literature-search/), [literature-review](../literature-review/), [citation-management](../citation-management/)
- 参见：[novelty-assessment](../novelty-assessment/), [survey-generation](../survey-generation/)
