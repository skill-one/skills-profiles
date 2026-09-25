# dbSNP数据库集成

## 前置条件

1.  **`uv`**: 阅读`uv`技能并按照其设置说明进行操作，确保`uv`已安装并在PATH路径中。
2.  **用户通知**: 如果工作区根目录中不存在`.licenses/dbsnp_database_LICENSE.txt`文件，则 (1) 醒目地通知用户检查https://www.ncbi.nlm.nih.gov/snp/处的条款，然后 (2) 创建一个记录通知文本和时间戳的文件。
3.  **`.env`文件**: 确保您的家目录中存在`.env`文件。如果不存在，请创建它。
4.  **`NCBI_API_KEY`** (可选): 将NCBI速率限制从每秒3次请求提高到每秒10次请求。该技能可以在没有密钥的情况下工作，但如果用户计划进行大量查询或遇到429错误，建议使用密钥。您可以在https://www.ncbi.nlm.nih.gov/account/settings/免费注册密钥。如果此技能与用户的请求相关，您**必须**在`credentials`技能中使用安全凭证协议来检查和请求此密钥。

## 核心规则

-   **使用包装器**: 始终使用提供的包装器脚本`scripts/dbsnp_cli.py`查询数据库，而不是构建自定义HTTP或curl请求。该脚本自动处理速率限制、重试和JSON解析。
-   **命令选择**: 不要使用`search-region`来查找特定变异的rsID；改用`resolve-variant`。
-   **输出大小**: 除非特别需要，否则避免在`get-variant`上使用`--full`，因为原始有效负载可能会超过1 MB。
-   **Shell安全**: 始终用单引号包裹HGVS字符串，以防止Shell扩展错误。
-   **通知**: 如果使用此技能，请确保在输出中提及。

## 使用场景

**当您需要使用此技能时：**

-   将基因组变异映射到其规范rsID（从VCF坐标或HGVS表示法）。
-   获取rsID的摘要数据：变异类型、基因关联、临床意义和人群等位基因频率。
-   将rsID转换回特定组装上的基因组坐标。
-   查找染色体区域内所有已知的变异。

**当您不需要使用此技能时：**

-   获取临床致病性分类及提交者理由（使用**clinvar-database**）。
-   获取按祖先分层的人群级等位基因频率（使用**gnomad-database**）。
-   预测新突变的 功能效应（使用**alphagenome-single-variant-analysis**）。
-   查看受变异影响的3D蛋白质结构（使用**alphafold-database-fetch-and-analyze / pdb-database**）。

## 命令选择指南

**第一次就选择正确的命令。** 将用户的输入与下面的正确子命令匹配——几乎总是只需要一个命令调用。

-   用户给您...: 运行此命令
-   rsID（例如`rs7412`，`rs268`）: `get-variant`
-   基因组坐标: 染色体 位置 参考碱基 替代碱基（例如`8 19962213 C T`）: `resolve-variant`
-   HGVS字符串（例如`NC_000008.11:g.19962213del`）: `resolve-hgvs`
-   rsID并且他们想要坐标回来: `resolve-rsid`
-   染色体区域（染色体 起始位置 结束位置）: `search-region`

> [!CAUTION] **不要使用`search-region`来查找特定变异的rsID。** 如果用户提供染色体、位置、参考碱基和替代碱基（四个值），请使用`resolve-variant`——它是一个直接的、单API调用查找。`search-region`仅用于调查指定位置范围内的所有变异，并返回数百/数千个结果。

## 快速入门

```bash
# 查询变异rs7412: 类型、基因、临床意义、MAF
uv run scripts/dbsnp_cli.py get-variant rs7412 --output /tmp/rs7412.json

# 查找位于chr8:19962213 C>T的rsID
uv run scripts/dbsnp_cli.py resolve-variant 8 19962213 C T \
  --output /tmp/resolve.json
```

所有子命令将JSON写入磁盘。始终将输出保存在`/tmp/`目录中。`--output`标志是必需的。

## 命令

### 1. `get-variant` — 获取变异记录

检索一个rsID的RefSNP记录。默认情况下，输出被缩减为最有用的字段。`rs268`和`268`都接受。

```bash
uv run scripts/dbsnp_cli.py get-variant rs268 --output /tmp/rs268.json
uv run scripts/dbsnp_cli.py get-variant 268 --assembly GCF_000001405.40 \
  --output /tmp/rs268.json
```

*参数:*

-   `rsid` (位置参数，必需): RefSNP标识符。
-   `--assembly`: RefSeq组装访问号（默认: `GCF_000001405.40` = GRCh38）。
-   `--full`: 返回完整的原始JSON有效负载——见警告。
-   `--output`: 输出文件路径（默认: `/tmp/dbsnp_output.json`）。

*缩减输出字段:*

-   `refsnp_id`: 数字rsID
-   `variant_type`: 例如`snv`，`ins`，`del`，`delins`
-   `genes`: 基因符号（位点名称）的排序列表
-   `clinical_significances`: 临床意义标签列表
-   `minor_allele_frequencies`: 研究名称、等位基因计数、总计数
-   `placements`: 请求的组装的基因组定位

> [!WARNING] **关于`--full`**: 原始RefSNP有效负载通常为50–500 KB，对于具有许多提交的临床显著变异可能超过1 MB。仅在您需要从缩减输出中缺少的数据时使用`--full`——例如:
>
> -   每个转录本和蛋白质异构体的完整HGVS命名法。
> -   带有单个提交者详细信息和时间戳的完整提交历史记录。
> -   研究内按亚群划分的人群级等位基因频率分解（例如每个人群的gnomAD计数）。
> -   跨多个组装的完整基因组定位集（同时为GRCh37和GRCh38）。
> -   显示哪些旧的rsID被合并到此rsID中的合并历史记录。

### 2. `resolve-variant` — 基因组坐标→rsID

给定基因组坐标（染色体、位置、参考碱基、替代碱基）确定rsID。**当用户提供空间分隔坐标时使用此命令**，例如`8 19962213 C T`。

```bash
uv run scripts/dbsnp_cli.py resolve-variant 8 19962213 C T \
  --output /tmp/resolve.json
```

*参数:*

-   `chrom` (位置参数): 染色体编号（例如`8`）或RefSeq序列访问号（例如`NC_000008.11`）。**X和Y染色体必须作为其数值等价物传递：`23`为X，`24`为Y。**
-   `pos` (位置参数): 1-based基因组位置。
-   `ref` (位置参数): 参考碱基（例如`C`）。
-   `alts` (位置参数): 替代碱基，逗号分隔（例如`T`）。
-   `--assembly`: RefSeq组装访问号（默认: `GCF_000001405.40`）。
-   `--output`: 输出文件路径（默认: `/tmp/dbsnp_output.json`）。

*输出:* `{"rsids": ["12345", "67890"]}`

### 3. `resolve-rsid` — rsID→基因组坐标

获取特定组装上已知rsID的基因组定位（序列ID和等位基因详细信息）。

```bash
uv run scripts/dbsnp_cli.py resolve-rsid rs7412 --output /tmp/coords.json
```

*参数:*

-   `rsid` (位置参数): RefSNP标识符。
-   `--assembly`: RefSeq组装访问号（默认: `GCF_000001405.40`）。
-   `--output`: 输出文件路径（默认: `/tmp/dbsnp_output.json`）。

*输出:* `{"rsid": "7412", "assembly": "...", "placements": [...]}`

### 4. `resolve-hgvs` — HGVS→rsID

查找与HGVS表达式对应的rsID。

```bash
uv run scripts/dbsnp_cli.py resolve-hgvs 'NC_000008.11:g.19962213del' \
  --output /tmp/hgvs.json
```

*参数:*

-   `hgvs` (位置参数): HGVS字符串。
-   `--assembly`: RefSeq组装访问号（默认: `GCF_000001405.40`）。
-   `--output`: 输出文件路径（默认: `/tmp/dbsnp_output.json`）。

*输出:* `{"rsids": ["12345"]}`

> [!TIP] HGVS字符串通常包含Shell解释的字符（冒号、大于号）。始终用单引号包裹它们，以防止Shell扩展。

### 5. `search-region` — 区域变异搜索

查找染色体区域内所有rsID。

```bash
uv run scripts/dbsnp_cli.py search-region 7 117100000 117300000 \
  --output /tmp/region.json
```

*参数:*

-   `chrom` (位置参数): 染色体（例如`7`）。**使用`23`为染色体X，`24`为染色体Y。**
-   `start` (位置参数): 起始位置。
-   `end` (位置参数): 结束位置。
-   `--retmax`: 返回的最大rsID数量（默认: 500，上限: 5 000）。
-   `--output`: 输出文件路径（默认: `/tmp/dbsnp_output.json`）。

*输出:*

```json
{
  "rsids": ["12345", "67890", "..."],
  "returned": 500,
  "total_available": 1423,
  "truncated": true,
  "note": "Only 500 of 1423 variants returned.  Increase --retmax ..."
}
```

当`total_available`超过返回计数时，输出包括`truncated`标志和`note`。增加`--retmax`以检索更多（最多5 000）。

## 典型工作流程

### 从坐标识别已知变异

```bash
# 第一步：将VCF坐标映射到rsID
uv run scripts/dbsnp_cli.py resolve-variant 19 44908684 T C \
  --output /tmp/step1.json

# 第二步：获取解析的rsID的完整详细信息
uv run scripts/dbsnp_cli.py get-variant <step1中的rsid> \
  --output /tmp/step2.json
```

### 调查基因区域内的变异

```bash
# 第一步：查找跨越CFTR基因区域的变异
uv run scripts/dbsnp_cli.py search-region 7 117100000 117300000 \
  --retmax 1000 --output /tmp/region.json

# 第二步：检索感兴趣的个别rsID的详细信息
uv run scripts/dbsnp_cli.py get-variant <rsid> --output /tmp/detail.json
```

### 将HGVS表示法转换为基因组坐标

```bash
# 第一步：获取HGVS表达式的rsID
uv run scripts/dbsnp_cli.py resolve-hgvs 'NC_000019.10:g.44908684T>C' \
  --output /tmp/hgvs.json

# 第二步：将该rsID解析为VCF样式坐标
uv run scripts/dbsnp_cli.py resolve-rsid <rsid> --output /tmp/coords.json
```

## 组装默认值和自动回退

Variation Services端点（由`get-variant`，`resolve-variant`，`resolve-rsid`，`resolve-hgvs`使用）期望一个**RefSeq组装访问号**。GRCh38的RefSeq访问号是`GCF_000001405.40`，GRCh37的是`GCF_000001405.25`。

`search-region`子命令始终搜索GRCh38位置。

> [!IMPORTANT] **自动组装回退**: `resolve-variant`和`resolve-hgvs`命令首先尝试GRCh38。如果没有找到rsID，它们会重试GRCh37，然后再报告失败。当发生回退时，输出JSON包括一个解释哪个组装成功的`"note"`字段。**您不需要手动重试不同的组装**——脚本透明地处理此操作。

您只需要覆盖`--assembly`，当您特别想要将查找限制为一个组装时（例如，因为用户的坐标已知为GRCh37）。

## NCBI API密钥和速率限制

没有API密钥，脚本限制为**每秒3次请求**。使用密钥后，这增加到**每秒10次请求**。

您可以在https://www.ncbi.nlm.nih.gov/account/settings/免费注册密钥。如果此技能与用户的请求相关，您**必须**在`credentials`技能中使用安全凭证协议来检查和请求此密钥。

## 故障排除HTTP 500错误

### 参考碱基不匹配

如果您收到一个带有消息的HTTP 500错误，该消息详细说明声明的参考碱基不等于请求组装中的参考序列：

**含义:** 坐标位置可能有效，但您提供的参考碱基（`ref`）与该位置在请求的组装中的碱基不匹配。

**操作:** 1. **不要**机械地重试完全相同的查询。 2. **检查组装**: 坐标是组装特定的。 3. **切换组装**: 如果您正在查询GRCh37，请尝试GRCh38（使用`--assembly GCF_000001405.40`），或者如果您正在查询GRCh38，请尝试GRCh37（使用`--assembly GCF_000001405.25`）。

## 常见错误

-   **错误:** 忘记引用HGVS字符串 **修复:** 用单引号包裹: `'NC_000008.11:g.19962213del'`
-   **错误:** 将染色体名称传递给`resolve-variant`而不是序列访问号 **修复:** 使用数值染色体ID（例如`8`）或RefSeq访问号，如`NC_000008.11`
-   **错误:** 在不需要的情况下在`get-variant`上使用`--full` **修复:** 缩减输出涵盖大多数用例；`--full`返回50–500 KB+的JSON
-   **错误:** 期望`search-region`默认返回所有结果 **修复:** 默认`--retmax`为500；检查输出中的`total_available`以查看是否截断
-   **错误:** 使用GRCh37坐标与`search-region` **修复:** `search-region`始终使用GRCh38位置；如果从GRCh37开始，请先转换坐标
-   **错误:** 当第一个调用失败时手动重试`resolve-variant`或`resolve-hgvs`使用不同的`--assembly` **修复:** 脚本自动尝试GRCh38然后GRCh37；一个调用就足够了
-   **错误:** 将`X`或`Y`作为染色体值传递 **修复:** 使用数值等价物：`23`为染色体X，`24`为染色体Y。CLI默认按数值处理染色体。
