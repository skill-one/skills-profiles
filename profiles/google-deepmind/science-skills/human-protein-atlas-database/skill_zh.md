# 人类蛋白质图谱（HPA）数据库集成

该技能提供来自人类蛋白质图谱（HPA）的半定量蛋白质表达和空间定位数据。虽然 RNA 测序（例如 GTEx）可以告诉我们基因是否正在转录，但 HPA 可以确认蛋白质产物是否实际存在，它在细胞内的位置（例如细胞核与细胞质），以及其在全身血液循环中的浓度。该数据基于对正常人类组织和癌症类型的免疫组化（IHC）检测。

## 前置条件

1.  **`uv`**: 阅读 `uv` 技能并遵循其设置说明，确保 `uv` 已安装并在 PATH 中。
2.  **用户通知**: 如果工作区根目录中不存在 `.licenses/human_protein_atlas_database_LICENSE.txt` 文件，则 (1) 醒目地通知用户检查 https://www.proteinatlas.org/about/licence 上的条款，然后 (2) 创建记录通知文本和时间戳的文件。

## 使用场景

**当您需要时使用此技能：**

-   将基因符号映射到 HPA 查询的 Ensembl ID。
-   基于 IHC 染色（高、中、低或未检测到）检索正常人类组织和癌症类型的半定量蛋白质丰度。
-   查找蛋白质已定位于特定细胞器或亚细胞结构的详细信息（例如核质、线粒体）。
-   检查 RNA 测序共识与蛋白质表达水平之间的一致性/一致性。
-   根据特定的蛋白质表达标准搜索基因（例如，“杏仁核升高”或“分泌蛋白”）。

**当您不需要时不要使用：**

-   查询 eQTLs、pQTLs 或任何变异水平关联。HPA 提供野生型表达数据，对 QTL 一无所知。
-   查询非人类物种的基因表达。HPA 严格针对人类蛋白质。
-   检索纯量 RNA 表达而不关心蛋白质产物（考虑使用 GTEx 技能）。

## 命令选择指南

**第一次就选择正确的命令。** 将用户的输入与下面的正确子命令进行匹配。

-   将基因符号映射到 Ensembl ID: `resolve-ensembl-id`
-   获取组织蛋白质表达水平: `get-tissue-expression`
-   获取蛋白质的亚细胞定位: `get-subcellular-location`
-   获取基因的完整 HPA 元数据条目: `get-atlas-entry`
-   根据 HPA 搜索匹配特定标准的基因: `search-hpa`

## 快速入门

```bash
# 将 ERBB2 基因符号映射到其 Ensembl ID
uv run scripts/hpa_cli.py resolve-ensembl-id ERBB2 --output /tmp/erbb2_id.json

# 通过 Ensembl ID 获取亚细胞定位
uv run scripts/hpa_cli.py get-subcellular-location ENSG00000141736 --output /tmp/erbb2_location.json
```

所有子命令将 JSON 写入磁盘。始终将输出保存在 `/tmp/` 目录中。如果未指定 `--output`，则默认输出文件为 `/tmp/hpa_output.json`。

## 命令

### 1. `resolve-ensembl-id` — 基因符号 → Ensembl ID

将常见基因符号（例如 "TP53"、"ERBB2"）映射到其 Ensembl 基因 ID。HPA 端点严格基于 Ensembl。

```bash
uv run scripts/hpa_cli.py resolve-ensembl-id TP53 --output /tmp/tp53_id.json
```

*参数:*

-   `gene_symbol` (位置参数): 标准基因符号（例如 "TP53"）。
-   `--output`: 输出文件路径（默认: `/tmp/hpa_output.json`）。

### 2. `get-tissue-expression` — 获取组织蛋白质水平

返回一系列组织和它们对应的蛋白质表达水平（高、中、低或未检测到）的列表，基于 IHC 染色。

```bash
uv run scripts/hpa_cli.py get-tissue-expression ENSG00000130234 \
  --tissues "十二指肠,甲状腺" --output /tmp/tissue_expr.json
```

*参数:*

-   `ensembl_id` (位置参数): Ensembl 基因 ID。
-   `--tissues`: 要过滤的逗号分隔组织列表（可选，默认为所有可用组织）。
-   `--output`: 输出文件路径（默认: `/tmp/hpa_output.json`）。

### 3. `get-subcellular-location` — 获取亚细胞定位

检索蛋白质已定位于特定细胞器或细胞结构的详细信息。

```bash
uv run scripts/hpa_cli.py get-subcellular-location ENSG00000141736 \
  --output /tmp/subcellular.json
```

*参数:*

-   `ensembl_id` (位置参数): Ensembl 基因 ID。
-   `--output`: 输出文件路径。

### 4. `get-atlas-entry` — 获取完整 HPA 条目

获取基因的完整元数据，包括 IHC 分数、RNA 测序共识和亚细胞定位。

```bash
uv run scripts/hpa_cli.py get-atlas-entry ENSG00000254647 \
  --output /tmp/ins_entry.json
```

*参数:*

-   `ensembl_id` (位置参数): Ensembl 基因 ID。
-   `--format`: 返回条目的格式，例如 json（默认: `json`）。
-   `--output`: 输出文件路径。

### 5. `search-hpa` — 按属性搜索

允许根据特定标准（例如 "amygdala 中升高"）过滤基因。

```bash
uv run scripts/hpa_cli.py search-hpa \
  --query "brain_category_rna:amygdala" \
  --output /tmp/search_results.json
```

*参数:*

-   `--query`: 搜索查询字符串。参考 references/search-api.md 获取详细信息。
-   `--output`: 输出文件路径。

## 核心规则

-   **使用包装器**: 始终使用提供的辅助脚本来查询数据库，而不是直接访问数据库。脚本会自动执行公平使用并实现重试逻辑。
-   **通知**: 如果使用此技能，请确保在输出中提及这一点。

## API 版本控制

HPA 网站 `www.proteinatlas.org` 始终提供 **最新** 数据版本。旧版归档版本可以通过 `vNN.proteinatlas.org` 访问（例如 `v24.proteinatlas.org`），而当前版本的子域名会重定向到 `www.proteinatlas.org`。此技能的脚本默认查询最新版本。

## 常见错误

-   如果未返回结果，请确认查询是否足够详细，并从 references/search-api.md 中的 API 参考开始。
-   如果找不到结果，请在网络上搜索示例 HPA 查询，并使用这些查询来构建更好的查询。
-   输出通常很大。使用 jq 或编写自己的 Python 数据解析库来处理搜索结果。切勿输出到 stdout，或 cat 输出文件。
