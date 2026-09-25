# ClinVar 数据库

## 前置条件

1.  **`uv`**: 阅读 `uv` 技能并按照其设置说明进行操作，确保 `uv` 已安装并在 PATH 路径中。
2.  **用户通知**: 如果工作区根目录中不存在 `.licenses/clinvar_database_LICENSE.txt` 文件，则 (1) 需要显著通知用户检查 https://www.ncbi.nlm.nih.gov/clinvar/ 上的条款，然后 (2) 创建一个记录通知文本和时间戳的文件。
3.  **`.env` 文件**: 确保您的家目录中存在 `.env` 文件。如果不存在，请创建一个。
4.  **`NCBI_API_KEY`** (可选): 将 NCBI 速率限制从每秒 3 次请求提高到 10 次。该技能在没有密钥的情况下也能工作，但如果用户计划进行大量查询或遇到 429 错误，建议使用密钥。您可以在 https://www.ncbi.nlm.nih.gov/account/settings/ 免费注册密钥。如果此技能与用户的请求相关，您 **必须** 在 `credentials` 技能中使用安全凭证协议来检查并请求此密钥，以帮助用户将其添加到他们的 `.env` 文件中。

## 概述

ClinVar 是人类基因组变异临床分类的主要共识记录。它基于全球实验室的断言，提供致病性标签（致病、可能致病、良性、VUS）的“临床真实情况”。

## 何时使用

**当您需要时使用：**

-   查找特定变异的当前临床意义和星级评分（审查状态）。
-   获取临床医生笔记、断言标准或先前临床实验室分类的推理依据。
-   检索特定变异的首选疾病名称和相关 HPO 术语。
-   查找变异控制列表（例如，“查找 HBB 基因内 50bp 范围内所有致病变异”）。
-   检查给定变异的冲突解释，并识别提交每个分类的组织。

**当您不需要时不要使用：**

-   查找全球人群中的特定等位基因频率（使用 **gnomAD**）。
-   描述蛋白质的正常生物学作用和典型遗传模式（使用 **OMIM**）。
-   预测新型突变（如移码或外显子跳跃）的机制效应（使用 **AlphaGenome**）。
-   查找对致病变异患者推荐的监测计划（使用 **GeneReviews**）。
-   生成或查看受影响蛋白质的 3D 结构模型（使用 **PDB / AlphaFold**）。

## 快速入门

ClinVar 查询通过一个强大的 Python 包装脚本执行，以处理严格的速率限制和 XML/JSON 解析。

示例：搜索 BRCA1 变异

```bash
uv run scripts/clinvar_api.py search --query "BRCA1[gene]" --output results.json
```

## 核心规则

-   **Retmax 限制**: 搜索命令默认为 `--retmax 200`。对于任何“列出所有”或基因范围请求，您 **必须** 显式设置 `--retmax` 更高（例如，1000），以确保数据的完整性。
-   **使用包装脚本**: 对于标准查询，请优先使用包装脚本。它处理速率限制、重试和复杂的 XML 解析。如果脚本解析的输出不包含您需要的特定字段，您可以修改脚本或直接查询 NCBI E-utilities API —— 但请注意，原始 XML 架构很复杂，并且在不同记录类型之间有所不同。
-   如果达到速率限制，脚本将抛出一个清晰的错误。您 **必须** 在 `credentials` 技能中使用安全凭证协议来检查并请求 `NCBI_API_KEY`，以帮助用户将其添加到他们的 `.env` 文件中。
-   **通知**: 如果使用此技能，请确保在输出中提及这一点。

## 实用脚本

### 1. `count` — 计数匹配的变异

**目的**: 检查有多少变异与查询匹配，而无需获取 ID。用于决定是否需要执行完整的 `search`。

*参数:*

-   `--query`: (必需) NCBI Entrez 搜索查询字符串。
-   `--output`: (必需) 输出 JSON 文件路径。

*示例:* `uv run scripts/clinvar_api.py count \ --query "TP53[gene] AND
\"uncertain significance\"[clinsig]" \ --output count.json` *输出:*
`{"total_count": <int>}`

### 2. `search` — 搜索变异

**目的**: 使用 NCBI Entrez 搜索语法根据基因组位置、基因符号或临床属性来识别变异。搜索命令 **自动分页** 通过所有匹配结果，以确保完整、确定性的检索。

```bash
# 获取所有匹配的变异（默认行为）
uv run scripts/clinvar_api.py search \
  --query "BRCA1[gene]" --output results.json

# 通过染色体和位置范围搜索
uv run scripts/clinvar_api.py search \
  --query "11[chr] AND 5225000:5226000[chrpos]" --output results.json

# 使用 Entrez 语法组合术语
uv run scripts/clinvar_api.py search \
  --query "HBB[gene] AND pathogenic[clinsig]" --output results.json

# 结果限制为 50
uv run scripts/clinvar_api.py search \
  --query "TP53[gene]" --retmax 50 --output results.json
```

*参数:*

-   `--query`: (必需) NCBI Entrez 搜索查询字符串。
-   `--retmax`: 返回的最大总变异 ID 数量。**默认为 0，这意味着“获取所有匹配结果”。** 设置为正整数以限制结果集。
-   `--page_size`: 每次 API 请求获取的 ID 数量（默认：500，最大：10000，根据 NCBI 限制）。
-   `--output`: (必需) 输出 JSON 文件路径。

*输出:* 一个包含以下内容的 JSON 对象:

-   `total_count` — ClinVar 中匹配的变异总数。
-   `fetched_count` — 实际检索到的 ID 数量。
-   `variant_ids` — ClinVar 变异 ID 字符串列表。

### 3. `summary` — 获取解释摘要

**目的**: 获取一线临床意义标签、星级评分（审查状态）和基本表型数据，用于快速变异筛选。

```bash
# 获取一个或多个 Variation ID 的摘要
uv run scripts/clinvar_api.py summary \
  --variant_ids 12345 67890 --output summary.json
```

*参数:*

-   `--variant_ids`: (必需) 一个或多个 ClinVar 变异 ID。
-   `--output`: (必需) 输出 JSON 文件路径。

*输出:* 一个包含摘要对象的 JSON 列表，每个对象包含:

-   `variant_id`, `title`, `clinical_significance`, `review_status`, \
    `last_evaluated`, `phenotypes`
-   `genes` — 基因列表 `{gene_id, symbol, strand}`
-   `variation_type` — 例如，单核苷酸变异、缺失、插入
-   `molecular_consequences` — 字符串列表（例如，["错义变异", \
    "无义变异"）]

### 4. `evidence` — 获取临床证据

**目的**: 获取单个变异的完整临床记录，包括自由文本临床医生推理依据、断言方法和特定提交者笔记。

```bash
# 获取单个 Variation ID 的完整证据
uv run scripts/clinvar_api.py evidence \
  --variant_id 12345 --output evidence.json
```

*参数:*

-   `--variant_id`: (必需) 一个 ClinVar 变异 ID。
-   `--output`: (必需) 输出 JSON 文件路径。

*输出:* 一个包含以下内容的 JSON 对象:

-   `variant_id`
-   `allele_info` — `{chromosome, position_start, position_stop,
    reference_allele, alternate_allele, cytogenetic_band, dbsnp_rsid}` (GRCh38 优先)
-   `conditions` — 疾病列表 `{name, medgen_cui, omim_id, orphanet_id, hpo_terms}`
-   `functional_consequences` — `{value, sequence_ontology_id}`
-   `structural_variant_details` — `{outer_start, inner_start, inner_stop,
    outer_stop, copy_number}` (仅 CNVs 才存在，否则为 null)
-   `citation_references` — 全球“引用”部分中引用的 PubMed ID 列表
-   `submissions` — 每个提交者的记录列表，每个记录包含:
    -   `submitter_name`, `classification`, `curator_notes`,
        `assertion_criteria`
    -   `date_last_evaluated` — 提交者最后一次审查分类的时间

## 典型工作流程

### 先计数后搜索工作流程（推荐）

对于大型或未知的结果集，首先使用 `count` 来决定是否继续，然后使用 `search`（自动分页并返回 `total_count` /
`fetched_count`），然后使用 `summary` 进行筛选。

```bash
# 第 1 步：评估大小（可选 — search 也返回 total_count）
uv run scripts/clinvar_api.py count \
  --query "HBB[gene] AND pathogenic[clinsig]" --output count.json

# 第 2 步：获取所有变异 ID（自动分页）
uv run scripts/clinvar_api.py search \
  --query "HBB[gene] AND pathogenic[clinsig]" --output ids.json

# 第 3 步：获取摘要（从 search 输出中提取 variant_ids）
uv run scripts/clinvar_api.py summary \
  --variant_ids 12345 67890 --output summary.json
```

### 深入分析：search → evidence

当您需要特定变异的完整临床信息——包括提交者推理依据、PubMed 引用、本体链接的疾病和等位基因坐标时，请使用 `evidence`。

```bash
uv run scripts/clinvar_api.py evidence \
  --variant_id 12345 --output evidence.json
```

### 工作流程：稳健变异发现（三角测量）

ClinVar 元数据不一致。为了满足“列出所有”请求，不要依赖单个过滤器。执行以下操作并合并结果：

1.  **按精确标签搜索**（例如，`"3 prime UTR
    variant"[molecular_consequence]`）。
2.  **按 HGVS 命名法模式搜索**（例如，`c.*`）。
3.  **按基因组坐标范围搜索**（使用 `[chrpos]`）。

这种“三角测量”确保没有标签的结构变异不会被忽略。

### 通过 HGVS 验证编码与非编码状态

`molecular_consequences` 单独可能很模糊（例如，`splice donor variant`
出现在编码和非编码环境中）。始终通过 `title` 字段检查 HGVS 模式：

-   `c.-…` — 5' UTR（非编码）
-   `c.*…` — 3' UTR（非编码）
-   `c.123+N` / `c.123-N` — 内含子（非编码）
-   `p.Trp146Arg` 等 — 蛋白质效应（编码）

具有 UTR/内含子 HGVS 且没有 `p.` 注释的变异是非编码的，即使有剪接标签。相反，任何 `p.` 注释都表示编码效应。

### ClinVar 元数据参考

-   **3' UTR**
    -   搜索字符串: `"3 prime UTR variant"[mol_consequence]`
    -   HGVS: `c.*`
-   **5' UTR**
    -   搜索字符串: `"5 prime UTR variant"[mol_consequence]`
    -   HGVS: `c.-`
-   要查找“高置信度”变异或专家审查的共识，请使用 `review_status` 过滤器。这是区分单实验室断言和面板审查真实情况的最有效方法。

### 何时使用哪些字段

-   **快速致病性标签** — 使用 `summary` → `clinical_significance`
-   **基因符号和链** — 使用 `summary` → `genes`
-   **变异类型 (SNV, del, 等)** — 使用 `summary` → `variation_type`
-   **蛋白质级效应** — 使用 `summary` → `molecular_consequences`
-   **基因组坐标 (GRCh38)** — 使用 `evidence` → `allele_info`
-   **链接的疾病（本体）** — 使用 `evidence` → `conditions`
-   **SO 功能后果** — 使用 `evidence` → `functional_consequences`
-   **CNV 断点/拷贝数** — 使用 `evidence` →
    `structural_variant_details`
-   **PubMed 参考文献** — 使用 `evidence` → `citation_references`
-   **实验室最后审查日期** — 使用两者 → `last_evaluated`
-   **临床医生推理依据** — 使用 `evidence` → `submissions[].curator_notes`

### 获取基因组坐标（默认 HG38/GRCh38）

要获取 `<chrom>:<pos>:<ref>><alt>` 格式的精确基因组坐标（例如，`chr5:70951945:G>A`），您必须使用 `evidence` 命令，因为这些细节不在 `summary` 输出中可用。

**您必须始终以 `<chrom>:<pos>:<ref>><alt>` 格式列出或展示变异，即使用户没有明确请求。如果摘要中缺少坐标，请使用 `evidence` 命令或 dbSNP 回退来检索它们。**

1.  **获取证据**: 使用 `uv run scripts/clinvar_api.py evidence --variant_id
    <ID> --output evidence.json`。
2.  **提取 VCF 属性**: `evidence` 命令解析 XML。提取:
    *   染色体: `Chr`
    *   位置: `positionVCF` (或 `start`)
    *   Ref: `referenceAlleleVCF` (或 `referenceAllele`)
    *   Alt: `alternateAlleleVCF` (或 `alternateAllele`) 从具有 `Assembly="GRCh38"`
        的 `SequenceLocation` 元素。

**不精确坐标的回退（基因范围）**: ClinVar 经常为非编码变异返回整个基因范围。如果提取的坐标对应于基因范围而不是特定位置，请使用 `dbsnp-database` 技能通过 `dbsnp_rsid` 或 HGVS 标题来解析精确的 GRCh38 坐标：1. 在 `evidence` 输出中检查 `dbsnp_rsid`。 2. 运行 `uv run scripts/dbsnp_cli.py resolve-rsid {rsid}` 获取精确的 GRCh38 坐标。 3. 使用 dbSNP 的 SPDI 或 HGVS 数据格式化为 `<chrom>:<pos>:<ref>><alt>`。

### 结构变异注意

`structural_variant_details` 字段**仅对拷贝数变异 (CNVs) 才会填充**。对于标准 SNVs 和小插入/缺失，此字段将为 `null`。请使用 `allele_info` 字段 (`position_start`, `position_stop`,
`reference_allele`, `alternate_allele`)。

### CNV / 大型缺失注意

大型拷贝数变异 (CNVs) 经常具有空的 `molecular_consequences`。如果变异标题提到“del”并且坐标与您的目标区域重叠，则无论是否有标签，它都是相关的。

### 获取和使用 API 密钥

您可以在 https://www.ncbi.nlm.nih.gov/account/settings/ 免费注册密钥。您 **必须** 在 `credentials` 技能中使用安全凭证协议来检查并请求此密钥，如果此技能与用户的请求相关。

## 最佳实践

-   始终使用 `uv run` 来执行 `python`。
-   如果 `jq` 不可用，立即切换到使用 Python 一行代码处理 JSON（例如，`uv run python3 -c "import json; ..."`）。
-   在 `search` 之前使用 `count` 了解结果集大小。
-   `search` 命令默认获取所有结果，并在输出中包含 `total_count` 和 `fetched_count` — 始终验证这些是否匹配以确认完整检索。
-   Entrez 结果是**未排序**的。要按日期排序，请获取所有结果并在本地按 `last_evaluated` 排序。

## 常见错误

-   **尝试自行解析 E-utilities XML** — 始终使用提供的 `clinvar_api.py` 客户端，它能够稳健地处理不可预测的 XML 架构。
-   **遇到 HTTP 429 Too Many Requests** — 客户端抛出异常告诉您暂停。您 **必须** 在 `credentials` 技能中使用安全凭证协议来检查并请求 `NCBI_API_KEY`，以帮助用户将其添加到他们的 `.env` 文件中，然后重试。
-   **向 API 发送原始 DNA 序列** — API 期望 HGVS 命名法、RS ID 或正确的 Entrez 坐标语法 (`11[chr] AND
    1234[chrpos]`)，而不是原始 ATCG 字符串。
-   **对于同义或非编码变异** — HGVS 命名法（例如，CAPN3 AND "c.551C>T"）比坐标搜索（[chrpos]）更可靠，因为许多 ClinVar 记录对于这些类型的变异缺乏精确的基因组映射。
-   **分子后果中的大小写敏感性** — ClinVar 返回混合大小写字符串。在过滤时始终使用**不区分大小写**的匹配（`.lower()`)。
-   **将 `search` 输出解析为纯列表** — `search` 返回一个包含 `total_count`、`fetched_count` 和 `variant_ids` 的 JSON 对象——而不是一个纯列表。
