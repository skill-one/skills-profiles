# Ensembl 数据库：ID 映射和基因组特征

## 前置条件

1.  **`uv`**：阅读 `uv` 技能并遵循其设置说明，确保 `uv` 已安装并在 PATH 中。
2.  **用户通知**：如果工作区根目录中不存在 `.licenses/ensembl_database_LICENSE.txt`，则 (1) 显著通知用户检查条款，访问 https://useast.ensembl.org/index.html 和 https://github.com/Ensembl/ensembl-rest/wiki，然后 (2) 创建记录通知文本和时间戳的文件。

## 概述

Ensembl 数据库是一个基因组注释资源。此技能允许您通过 Ensembl REST API 与数据库交互，解析模糊符号、交叉引用 ID（RefSeq、HGNC、UniProt、ENSG）、获取原始序列，并检索详细的转录本结构。

**关键概念：**

-   **ENSG（基因）**：人类基因的稳定标识符。其他物种将具有不同的三字母物种代码。
-   **ENST（转录本）**：转录本（剪接异构体）的稳定标识符。
-   **ENSP（蛋白质）**：翻译蛋白质的稳定标识符。
-   **MANE Select**：由 Ensembl 和 NCBI 共同商定的共识初级转录本。
-   **Canonical**：Ensembl 的代表性转录本（如果 MANE 不可用或非人类时使用）。

## 核心规则

-   **使用封装器**：始终使用提供的辅助脚本查询数据库，而不是直接访问数据库。脚本会自动优雅地执行所需的速率限制。
-   **默认物种**：如果提示中缺少物种或物种不明确，默认为 `"human"`。您必须明确向用户标记此默认值，以确保他们知晓。
-   **初级转录本**：列出基因的转录本时，除非用户明确要求所有替代异构体，否则仅返回 MANE Select 转录本（人类）或 Canonical 转录本（其他物种）。当存在多个转录本且您默认使用初级转录本时，必须向用户标记。
-   **组装处理**：默认组装为 GRCh38。对于 GRCh37 请求，必须使用 `--assembly GRCh37` 标志。当使用非默认组装时，必须明确向用户标记。
-   **输出位置**：脚本默认将完整的 JSON/FASTA 输出到 `/tmp` 中的临时文件，或使用 `--output` 标志写入用户指定的文件。它还会将简洁的摘要打印到 stdout。
-   **通知**：如果使用此技能，请确保在输出中提及。

### 可用命令

**1. 解析基因 ID** — 将符号、别名或 RefSeq ID 解析为 ENSG ID。如果找不到主符号，会自动回退解析同义词。

```bash
uv run scripts/ensembl_api.py resolve-gene TP53 --species human --output tp53.json
uv run scripts/ensembl_api.py resolve-gene PCL2 --output pcl2.json # 回退到同义词解析
```

**2. ID 映射到外部数据库** — 将 Ensembl ID 交叉引用到 UniProt、HGNC、RefSeq 等。

```bash
uv run scripts/ensembl_api.py map-id ENSG00000141510 --external-db UniProt --output uniprot_map.json
uv run scripts/ensembl_api.py map-id ENST00000269305 --external-db RefSeq_mRNA --output refseq_map.json
```

**3. 获取基因组序列** — 获取坐标窗口的原始 DNA。支持通过 `--assembly GRCh37` 使用 GRCh37。

```bash
uv run scripts/ensembl_api.py get-sequence 17:7661779-7687550 --species human --output seq.txt
uv run scripts/ensembl_api.py get-sequence chr9:21971100-21971200 --assembly GRCh37 --output seq_grch37.txt
```

**4. 基因摘要** — 高级元数据：符号、生物类型、描述、染色体位置。

```bash
uv run scripts/ensembl_api.py gene-summary ENSG00000141510 --output gene_summary.json
```

**5. 列出转录本** — 基因的所有转录本，可选 `--only-mane` 或 `--only-canonical` 过滤器。输出包括转录本支持级别 (TSL)。

```bash
uv run scripts/ensembl_api.py transcripts ENSG00000141510 --only-mane --output transcripts_mane.json
uv run scripts/ensembl_api.py transcripts ENSG00000141510 --only-canonical --output transcripts_canonical.json
uv run scripts/ensembl_api.py transcripts ENSG00000141510 --output transcripts_all.json
```

**5b. Canonical TSS** — 获取基因的 Canonical 转录本的单个转录起始位点 (TSS) 坐标。

> [!NOTE] 与标准的 `transcripts` 命令不同，`canonical-tss` 接受符号（例如 `TP53`）和 Ensembl ID，并自动解析它们。它还会计算链方向（`+` 链的 TSS 为 `Start`，`-` 链的 TSS 为 `End`），直接输出单个整数坐标。

```bash
uv run scripts/ensembl_api.py canonical-tss TP53 --output tp53_tss.json
uv run scripts/ensembl_api.py canonical-tss ENSG00000141510 --output tss.json
```

**6. 转录本结构** — 转录本的 Exon 坐标、CDS 边界和计算的 5'/3' UTR 区域。

```bash
uv run scripts/ensembl_api.py transcript-structure ENST00000269305 --output structure.json
```

**7. 蛋白质信息** — 转录本的 ENSP ID 和序列长度。

```bash
uv run scripts/ensembl_api.py protein-info ENST00000269305 --output protein_info.json
```

**8. 蛋白质序列** — 转录本（ENST）或蛋白质（ENSP）ID 的氨基酸 FASTA。

```bash
uv run scripts/ensembl_api.py protein-sequence ENST00000269305 --output protein.fasta
uv run scripts/ensembl_api.py protein-sequence ENSP00000269305 --output protein_ensp.fasta
```

**9. 变异后果 (VEP)** — 预测基因组变异的分子后果。包括开源插件：AlphaMissense、Conservation、DosageSensitivity、IntAct、MaveDB、OpenTargets、LoF（Loftee）、NMD、UTRAnnotator、mutfunc、LOEUF。

```bash
uv run scripts/ensembl_api.py vep 9:21971147:T:C --species human --output vep.json
uv run scripts/ensembl_api.py vep rs699 --species human --output vep_rs699.json
```

示例 VEP stdout 输出：

```
[*] 变异：9:21971147:T>C
[*] 最严重的后果：missense_variant
[*] 找到 15 个转录本后果。

[*] VEP 预测：

  - ENST00000304494 (CDKN2A)：Consequence = missense_variant
  - ENST00000304494 (CDKN2A)：Amino Acids = N/S
  - ENST00000304494 (CDKN2A)：SIFT = deleterious (0.01)
  - ENST00000304494 (CDKN2A)：AlphaMissense Class = likely_benign
  - ENST00000304494 (CDKN2A)：AlphaMissense Pathogenicity = 0.2129
  - ENST00000304494 (CDKN2A)：Conservation = 2.05
  - ENST00000304494 (CDKN2A)：Dosage Sensitivity (Haplo) = 0.889228328567991
  - ENST00000304494 (CDKN2A)：Dosage Sensitivity (Triplo) = 0.135514349094646
  - ENST00000304494 (CDKN2A)：Loss of Function (LOEUF) = 0.791
```

**展示 VEP 结果**：运行 VEP 命令后，必须向用户展示从 stdout 获取的完整 VEP 预测列表。此列表包含标准 VEP 预测（Consequence、Amino Acids、SIFT、PolyPhen）和开源插件结果（AlphaMissense、Conservation、Dosage Sensitivity、LOEUF、Loftee LoF、NMD、UTRAnnotator、Mutfunc）。不要仅总结——显示完整的列表，以便用户可以看到所有预测。如果列表非常长（许多转录本），请完整显示 MANE Select / canonical 转录本行，并注明完整数据在 JSON 输出中。

## 解析输出

如果用户需要详细的嵌套结构数据（例如转录本第 2 个 Exon 的精确整数坐标），而 stdout 中没有总结：

1.  定位 JSON 文件（通过 `--output` 指定或脚本打印的临时文件路径）。
2.  使用终端工具（如 `jq`）或编写一个快速、临时的 python 段落来提取请求的特定数据点。如果 JSON 文件非常大，请**不要**尝试将其整个内容读入您的上下文中。

## 自定义查询

如果您需要执行脚本不支持的 API 调用（例如，获取蛋白质结构域注释、组装之间的坐标映射、同源性搜索、连锁不平衡或表型查找），请阅读 `references/ensembl_rest_api_reference.md`，以获取可用端点、参数和响应字段的完整参考。

**关键**：编写自定义脚本或使用提供的脚本替代方案时，您**必须**尊重 Ensembl REST API 速率限制（每秒最多 15 个请求），并优雅地处理 `429 Too Many Requests` 错误（例如，使用指数退避）。
