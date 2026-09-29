---
name: target-prioritization
description: 从排序的基因列表（例如scRNA-seq差异表达输出）中优先筛选药物靶点，通过并行API查询UniProt、OpenTargets（整合DepMap CRISPR必需性+gnomAD约束）、PubMed、人类蛋白质图谱（HPA）和ChEMBL工具化合物，然后根据综合评分重新排序。该评分结合了蛋白质定位、成药性、疾病遗传性、组织特异性（安全性）、焦点细胞类型表达、CRISPR必需性、LoF安全性约束和研究成熟度。用户在筛选、分诊、优先排序或对药物发现候选基因列表进行“尽职调查”时均可使用，尤其是在DE/DEG分析后，当用户提出“我应该关注哪些基因”、“筛选成药性靶点”、“制作靶点档案”、“按可操作性排序”、“标注基因成药性”或“构建靶点报告”等需求时。即使用户仅说“筛选这些候选基因”或从DE流程中提供CSV文件，也会触发该功能。
---

# 目标优先级排序

一个用于排名基因列表的多源药物靶点尽职调查流程。

## 触发此技能的条件

用户有一个候选基因列表（通常来自差异表达/差异基因/单细胞RNA测序分析），并希望获得跨多个证据维度的每个基因档案以及复合重新排序。DE统计排名只是一个起点；最终优先级由蛋白质生物学、遗传学、成药性和研究成熟度决定。

常见输入格式：

- 带有`gene`列的CSV文件（DE输出，如`expression_table_pass_either_1s.csv`）
- 纯文本基因列表（每行一个符号）
- 用户消息中内联的符号列表

## 输出

`<output_dir>/`中的四个文件：

1. **`targets_report.md`** — 每个基因一个部分，按复合分数排序，带有简短的LLM编写的理由和推荐下一步操作
2. **`targets_report.html`** — 自包含的交互式报告（可排序+可搜索的摘要表，按层级可过滤的每个基因卡片，分数分量条，UniProt链接）。从`.md`和`.csv`构建，作为最终步骤，在Claude填充理由栏和执行摘要后。
3. **`targets_summary.csv`** — 用于Excel/pandas排序/过滤的平面表
4. **`raw_data/<source>.json`** — 原始API响应（审计追踪，可跨未来重新评分复用）

## 流程

```
输入基因列表
   │
   ▼
scripts/orchestrate.py
   │
   ├─► fetch_uniprot.py        → 蛋白质定位、表面、MHC、编码
   ├─► fetch_opentargets.py    → 可行性、已批准药物、相关疾病（通过OT整合的遗传证据涵盖GWAS目录）、DepMap CRISPR必要性、gnomAD LOEUF / pLI约束
   ├─► fetch_pubmed.py         → 论文计数（总数+聚焦疾病+细胞环境）
   ├─► fetch_hpa.py            → HPA组织/单细胞特异性+nCPM、表达簇、癌症预后
   └─► fetch_chembl.py         → 每个基因的强效工具化合物（pIC50、IC50 nM、机制）— 仅档案，无分数
   │
   ▼
scripts/aggregate.py
   │
   ▼
output_dir/
  ├─ raw_data/*.json
  ├─ targets_summary.csv       ← 复合分数排名
  └─ targets_report.md         ← Claude填充理由部分
   │
   ▼
scripts/build_html_report.py   ← 在Claude填充理由后运行
   │
   ▼
output_dir/targets_report.html ← 自包含的交互式报告
```

## 如何调用

```bash
python3 ~/myagents/myskills/target-prioritization/scripts/orchestrate.py \
    --input <gene_list.csv_or_txt> \
    --output <output_dir> \
    [--gene-col gene] \
    [--top 50]
```

- `--input` 接受CSV（带`--gene-col`，默认`gene`）、`.txt`/.`.tsv`，或任何第一列包含基因符号的文件。如果第一行是`gene`/`symbol`（不区分大小写），则跳过标题。
- `--top` 限制档案为前N个输入基因（默认50）— 输入顺序在切割前保留，然后复合分数重新排序。

`orchestrate.py` 并行运行五个获取器（Python线程，因为所有调用都是I/O绑定的）。每个都写入一个自包含的JSON到`<output_dir>/raw_data/<source>.json`。然后`aggregate.py`合并它们，使用`weights.yaml`计算复合分数，写入`targets_summary.csv`，并发出一个带有每个基因部分的`targets_report.md`骨架 — **理由和风险字段为空，供Claude填充**。

## 复合分数

权重位于`weights.yaml`中，并可通过`--weights`在每次运行中覆盖。默认目标是“寻找成药性、遗传学支持的靶点，具有清洁的治疗窗口并在目标细胞中表达”：

```
composite_score = w1 * druggability_score          (已批准药物、可行性、临床试验)
                + w2 * disease_genetics_score      (OpenTargets疾病关联+聚焦疾病奖励)
                + w3 * tractability_bonus          (表面或分泌vs细胞内)
                + w4 * tissue_specificity          (HPA组织标签 — 狭义表达=更清洁的窗口)
                + w5 * cell_context_score          (HPA单细胞nCPM排名在FOCUS_CELL_TYPES)
                + w6 * essentiality_score          (DepMap CRISPR % 必要性，全必需品封顶)
                + w7 * safety_constraint_score     (gnomAD LOEUF — 高=容忍LoF → 更安全抑制)
                + w8 * expression_score            (如果存在，来自输入DE)
                + w9 * novelty_bonus               (倾向于中等研究)
                - w10 * over_studied_penalty       (PubMed总数>封顶 → 追求递减)
```

ChEMBL贡献档案列（`chembl_target_id`、`chembl_best_pchembl`、`chembl_best_ic50_nm`、`chembl_top_compounds`），但无分数分量 — 它的工作是为“建议下一步”槽提供具体的工具化合物。

每个分量都归一化到[0, 1]。复合分数因此大致在[-w7, sum(w1..w6)]，并在报告前进行最小-最大缩放。
**请阅读`weights.yaml`了解当前默认值。**

## 编写理由

在`aggregate.py`生成带有空白理由槽的`targets_report.md`后，Claude读取每个基因档案行，并为每个基因编写2-3句理由。使用`prompts/rationale_template.md`中的模板 — 它指定了结构（最有力的证据一行，主要风险一行，建议的下一步实验步骤一行）。

对于复合分数排名前5-10的基因，还在报告顶部写一个简短的执行摘要。保持事实性和基于档案数据；不要超出JSON包含的内容进行幻觉。

## 构建HTML报告（最终步骤）

一旦`targets_report.md`的理由槽和执行摘要填写完毕，运行`build_html_report.py`生成自包含的交互式HTML报告：

```bash
python3 ~/myagents/myskills/target-prioritization/scripts/build_html_report.py \
    --report-dir <output_dir> \
    [--title "Target Prioritization Report"] \
    [--subtitle "<cohort / contrast description>"]
```

这是**始终是最后一步**。它读取`targets_summary.csv`和`targets_report.md`，并写入`--report-dir`中的`targets_report.html`。输出是一个没有外部依赖的单文件：顶部有可排序的摘要表，实时搜索+层级过滤按钮，每个基因一张卡片带芯片（表面/分泌/MHC/聚焦疾病/已批准药物），完整档案网格，以及每个分数分量的水平条。直接在浏览器中打开它；原样分享。

如果理由槽在运行时仍然为空，每个基因卡片在这些位置将显示“尚未编写”——这对于预览布局很有用，但应告知用户在分享前填写理由。

## 数据源说明

所有免费，无需API密钥。获取器中处理速率限制：

- **UniProt REST** — 100 req/sec，通过`accession`查询分批
- **OpenTargets GraphQL** — 慷慨，单个端点；通过集成的`associatedDiseases`提供疾病遗传信号
- **PubMed E-utilities** — 无密钥时3 req/sec；获取器尊重此限制
- **Human Protein Atlas** — `search_download.php`用于符号→ENSG，然后每个ENSG `/<ENSG>.json`；无记录速率限制，获取器每基因睡眠0.15s
- **DepMap CRISPR必要性** — 通过OpenTargets调用内的`target.depMapEssentiality`获取（无单独端点）
- **gnomAD约束** — 通过OpenTargets调用内的`target.geneticConstraint`获取（避免直接API访问的gnomAD WAF）
- **ChEMBL REST** — `target/search.json`然后`activity.json`；~5 req/sec友好，获取器每基因睡眠0.2s

有关更深入的API细节和字段映射，请参阅`references/api_endpoints.md`。

## 聚焦疾病和细胞环境的重新靶向

该技能带有自身免疫/ T细胞默认值，但有意疾病无关。三个编辑切换焦点：

- `scripts/fetch_opentargets.py`和`scripts/aggregate.py` — 修改`FOCUS_DISEASE_TERMS`为应标记药物或疾病关联为“在范围内”的小写字符串（例如`("cancer", "carcinoma", "lymphoma")`用于肿瘤学；
  `("alzheimer", "parkinson", "huntington", "als")`用于神经退行性疾病；
  `("diabetes", "obesity", "fatty liver", "nash")`用于代谢性疾病）。
- `scripts/aggregate.py` — 修改`FOCUS_CELL_TYPES`为应驱动`cell_context_score`的HPA单细胞类型名称。必须与HPA的精确字符串（区分大小写）匹配；见上方元组注释块中的每个域示例。
- `scripts/fetch_pubmed.py` — 调整`CONTEXTS`中的`focus_disease`和`cell_context`查询（这些驱动档案中的PubMed计数）。

无需其他代码更改；CSV列名已使用中性的`focus_disease_*` / `cell_context`前缀。

## 不应使用此技能的情况

- 单基因查询（过度 — 只需让Claude进行网络搜索）
- 非人类基因（大多数API仅限人类；获取器将静默返回空）
- 纯文献综述无靶点目标 — 使用`scholar-deep-research`或`literature-review`替代

## 迭代提示

该流程设计为可廉价重新运行：

- 原始JSON缓存意味着使用不同的`weights.yaml`重新评分是一个一秒钟的`aggregate.py`重跑
- 要添加新的证据源，添加`scripts/fetch_<source>.py`写入`raw_data/<source>.json`，与`{gene: {fields}}`形状相同，然后在`aggregate.py::compute_composite_score`中添加相应术语。
