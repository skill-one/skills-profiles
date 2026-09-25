# NCBI 序列获取

## 前置条件

1.  **`uv`**: 阅读 `uv` 技能并遵循其设置说明，确保已安装 `uv` 并在 PATH 路径中。
2.  **用户通知**: 如果工作区根目录中不存在 `.licenses/ncbi_sequence_fetch_LICENSE.txt` 文件，则 (1) 显著通知用户检查 https://www.ncbi.nlm.nih.gov/ 和 https://www.ncbi.nlm.nih.gov/home/about/policies/ 上的条款，然后 (2) 创建记录通知文本和时间戳的文件。
3.  **`.env` 文件**: 确保您的家目录中存在 `.env` 文件。如果不存在，请创建一个。
4.  **`NCBI_API_KEY`** (可选): 将 NCBI 速率限制从 3 提升至每秒 10 个请求。该技能无需此密钥即可工作，但如果用户计划进行大量查询或遇到 429 错误，建议使用密钥。您可以在 https://www.ncbi.nlm.nih.gov/account/settings/ 免费注册密钥。如果此技能与用户的请求相关，您 **必须** 在 `credentials` 技能中使用安全凭证协议来检查和请求此密钥。

## 核心规则

-   **使用包装器**: 始终使用提供的辅助脚本查询数据库，而不是直接访问数据库。脚本会自动优雅地执行所需的速率限制。
-   **API 密钥支持**: 如果用户在其环境中提供了 `NCBI_API_KEY`，查询速度限制将自动显著提高。
-   **通知**: 如果使用此技能，请确保在输出中提及。

## 概述

封装了 NCBI 的 Entrez E-utilities (efetch, esearch, elink, esummary)，用于检索蛋白质和核酸序列。提供 10 个子命令，涵盖完整的序列检索工作流程：

-   `fetch-protein` — 直接蛋白质登录号查询 (GenPept, RefSeq)
-   `fetch-nucleotide` — 直接核酸登录号查询
-   `cds-translate` — 获取 CDS 并翻译为蛋白质 (3 种方法)
-   `search` — 对任何 NCBI 数据库进行自由文本搜索
-   `elink` — 跟随跨数据库链接 (PubMed→蛋白质等)
-   `gene-protein` — 通过基因名 + 生物体搜索蛋白质
-   `locus-protein` — 通过位点标签 + 生物体搜索蛋白质
-   `pubmed-proteins` — 查找与 PubMed 文章链接的蛋白质
-   `patent-search` — 从专利中提取蛋白质序列
-   `organism-length` — 通过生物体 + 精确氨基酸长度进行最后手段搜索

## 实用脚本

**`scripts/ncbi_fetch.py`** — 带有子命令的单个脚本。

所有子命令都写入结构化的 JSON 输出。使用 `--output FILE` 保存到文件，或省略它以打印到标准输出。始终会打印人类可读的摘要到标准输出。

### 1. 通过登录号获取蛋白质

通过登录号从 NCBI 获取蛋白质 FASTA (XP_, NP_, GenPept 等)

```bash
uv run scripts/ncbi_fetch.py fetch-protein XP_022033624 -o /tmp/result.json
uv run scripts/ncbi_fetch.py fetch-protein NP_001234567 ABC12345.1
```

### 2. 通过登录号获取核酸

通过登录号从 NCBI 获取核酸 FASTA。

```bash
uv run scripts/ncbi_fetch.py fetch-nucleotide MK034466 -o /tmp/result.json
```

### 3. CDS 翻译

获取 CDS/核酸登录号并翻译为蛋白质序列。按顺序尝试三种方法：1. NCBI 预翻译的 CDS 蛋白 (`fasta_cds_aa`) 2. GenBank XML CDS 注释翻译 3. 原始核酸 → 6 帧ORF 寻找

```bash
uv run scripts/ncbi_fetch.py cds-translate MK034466 -o /tmp/result.json
uv run scripts/ncbi_fetch.py cds-translate HQ662330 --target-length 1043
```

如果登录号是 **基因组记录** (不是 mRNA/CDS)，工具将报告 `is_genomic: true`，以便您可以改用基于同源性的方法。

### 4. 搜索任何数据库

使用 Entrez 查询语法进行自由文本搜索。支持所有 NCBI 数据库。

```bash
# 搜索蛋白质数据库
uv run scripts/ncbi_fetch.py search "WRR4B[Gene Name] AND Arabidopsis[Organism]" \
  --database protein --retmax 5 --fetch-sequences

# 搜索核酸数据库
uv run scripts/ncbi_fetch.py search "Rz2[Gene Name] AND Beta vulgaris[Organism]" \
  --database nuccore --retmax 10

# 带专利过滤器的搜索
uv run scripts/ncbi_fetch.py search "disease resistance AND Solanum[Organism] AND patent[Properties]" \
  --database protein --fetch-sequences

# 通过序列长度搜索
uv run scripts/ncbi_fetch.py search '"Oryza sativa"[Organism] AND 1043[SLEN]' \
  --database protein --fetch-sequences --retmax 50
```

### 5. 跨数据库链接 (elink)

跟随 NCBI 的跨数据库链接 (例如，PubMed 文章 → 链接的蛋白质)。

```bash
uv run scripts/ncbi_fetch.py elink 24896089 --dbfrom pubmed --db protein \
  --fetch-sequences -o /tmp/linked.json
```

### 6. 基因 + 生物体搜索

通过基因名和生物体搜索蛋白质序列。在 NCBI 蛋白质中使用 `[Gene Name]` 和 `[Organism]` 限定符进行搜索。

```bash
uv run scripts/ncbi_fetch.py gene-protein WRR4B --organism "Arabidopsis thaliana"
uv run scripts/ncbi_fetch.py gene-protein Pikh-2 --organism "Oryza sativa" \
  --target-length 1043 -o /tmp/result.json
```

### 7. 位点标签搜索

在 NCBI 蛋白质和 Nuccore 数据库中通过位点标签进行搜索。当直接蛋白质命中不可用时，从 GenBank XML 中提取 CDS 翻译。

```bash
uv run scripts/ncbi_fetch.py locus-protein At1g56540 --organism "Arabidopsis thaliana"
uv run scripts/ncbi_fetch.py locus-protein Niben101Scf02422g02015.1 \
  --organism "Nicotiana benthamiana" -o /tmp/result.json
```

### 8. PubMed-链接的蛋白质

查找与 PubMed 文章链接的蛋白质序列。通过 PMID 在 NCBI 蛋白质中搜索，跟随 elink PubMed→蛋白质，并从链接的 Nuccore 记录中提取 CDS 翻译。

```bash
uv run scripts/ncbi_fetch.py pubmed-proteins 30692254 --identifier WRR4B
uv run scripts/ncbi_fetch.py pubmed-proteins 24896089 --identifier "K2" \
  -o /tmp/result.json
```

### 9. 专利序列搜索

两种模式：

**通过专利号** — 获取特定专利中的所有蛋白质序列：`bash uv run scripts/ncbi_fetch.py patent-search --patent-number US10123456 -o /tmp/patent.json`

**通过关键词** — 使用 `patent[Properties]` 过滤器搜索 NCBI 蛋白质：`bash uv run scripts/ncbi_fetch.py patent-search --keywords WRR4B Albugo --organism "Arabidopsis thaliana" -o /tmp/patent.json`

> [!IMPORTANT] **专利惯例**: 在分子生物学专利中，SEQ ID NO: 1 通常是 DNA 序列，SEQ ID NO: 2 是主要蛋白质。更高的 SEQ ID NO 是变体或相关序列。选择主要蛋白质时，优先考虑序列 2。

### 10. 生物体 + 长度搜索

当仅知道生物体和预期蛋白质长度时，作为最后手段进行搜索。使用 NCBI 的 `[SLEN]` 过滤器进行精确长度匹配。

```bash
uv run scripts/ncbi_fetch.py organism-length \
  --organism "Arabidopsis thaliana" --length 1048 --retmax 50 \
  -o /tmp/result.json
```

> [!NOTE] 这通常会返回多个候选者。使用 JSON 输出标题来识别正确的蛋白质。

## 工作流程

### 标准序列检索级联

当尝试查找蛋白质序列时，请按此优先级顺序操作：

1.  **直接登录号** — 使用 GenPept/RefSeq 登录号的 `fetch-protein`
2.  **CDS 翻译** — 使用核酸/CDS 登录号的 `cds-translate`
3.  **PubMed-链接** — 使用 PMID + 基因名的 `pubmed-proteins`
4.  **位点查找** — 使用位点标签 + 生物体的 `locus-protein`
5.  **基因 + 生物体** — 使用基因名 + 生物体的 `gene-protein`
6.  **专利搜索** — 使用专利号或关键词的 `patent-search`
7.  **生物体 + 长度** — 作为最后手段使用 `organism-length`

### 解释结果

-   所有子命令都返回带有 `results` 数组的 JSON
-   每个结果都有 `sequence` (AA 字符串)、`length` 和 `header`/元数据
-   当返回多个结果时，通过以下方式选择：
    -   与预期长度最接近的匹配 (`target_length`)
    -   标题相关性 (匹配基因名、"疾病抗性" 关键词)
    -   源优先级 (RefSeq > GenPept > 专利)

## 参考

-   **NCBI E-utilities 文档**: https://www.ncbi.nlm.nih.gov/books/NBK25499/
-   **Entrez 搜索语法**: https://www.ncbi.nlm.nih.gov/books/NBK49540/
-   **数据库列表**: protein, nuccore, gene, pubmed, pmc, biosample, 等
-   **常见登录号格式**:
    -   `XP_` / `NP_` — NCBI RefSeq 蛋白质
    -   `AAA` 到 `AZZ` + 数字 — GenPept (翻译的 GenBank)
    -   `MK`, `MN`, `HQ`, 等 + 数字 — GenBank 核酸
    -   `ENSG`, `ENST`, `ENSP` — Ensembl (使用 `ensembl-database` 技能代替)
    -   `Q`, `P`, `O` + 数字 — UniProt (使用 `uniprot-database` 技能代替)
