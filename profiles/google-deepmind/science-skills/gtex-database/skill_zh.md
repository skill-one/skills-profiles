# GTEx 数据库集成

该技能从 GTEx Portal API V2 中检索转录组数据（RNA 表达基线）和表达数量性状基因座（eQTLs）。它提供对基因的中位数 TPM（每百万条转录本）值以及变异体在 54 个人类组织位点上的显著 eQTLs 的访问。

## 前置条件

1.  **`uv`**：阅读 `uv` 技能并遵循其设置说明，确保 `uv` 已安装并在 PATH 中。
2.  **用户通知**：如果工作区根目录中不存在 `.licenses/gtex_database_LICENSE.txt`，则 (1) 醒目地通知用户检查 https://gtexportal.org/home/license 和 https://gtexportal.org/home/documentationPage#gtexApi 上的条款，然后 (2) 创建记录通知文本和时间戳的文件。

## 何时使用

**当您需要时使用此技能：**

-   将基因符号映射到其版本化的 GENCODE ID。
-   检索基因在各个组织中基线中位数表达水平（以 TPM 表示）。
-   找到特定基因表达量最高的组织。
-   获取变异体或染色体窗口内显著的单组织 eQTLs。
-   获取与特定基因相关的所有显著 eQTLs。
-   使用 eQTL 数据将变异体置于 GWAS 位点中进行背景化。

**当您不需要时不要使用：**

-   查询蛋白质水平表达或翻译后修饰（PTMs）。GTEx 仅测量 mRNA 数量。
-   查询患病组织中的基因表达（例如，肿瘤样本、肝硬化）。GTEx 是正常、非患病组织的基线图谱。
-   查询胚胎或胎儿基因表达。GTEx 捐赠者仅限于成人。

## 核心规则

**关键**：您必须尊重 GTEx Portal API 使用条款。

-   **使用包装器**：始终使用提供的辅助脚本来查询数据库，而不是直接访问数据库。脚本会自动优雅地执行所需的速率限制。
-   将请求限制在适用的每页最多 250 个项目。
-   **通知**：如果使用此技能，请确保在输出中提及这一点。

## 命令选择指南

**第一次就选择正确的命令。** 将用户的输入与下面的正确子命令进行匹配。

-   将基因符号映射到 GENCODE ID：`resolve-gencode-id`
-   获取基因的中位数表达（TPM）：`get-median-expression`
-   查找基因表达量最高的组织：`get-top-expressed-tissues`
-   获取特定基因的所有 eQTLs：`get-gene-eqtls`
-   查找染色体区域内的 eQTLs：`get-eqtls-in-region`

## 快速入门

```bash
# 将 TNF 基因符号映射到其 GENCODE ID
uv run scripts/gtex_cli.py resolve-gencode-id TNF --output /tmp/tnf_id.json

# 通过 GENCODE ID 获取基因的中位数表达
uv run scripts/gtex_cli.py get-median-expression ENSG00000232810.2 --output /tmp/tnf_expr.json
```

所有子命令将 JSON 写入磁盘。始终将输出保存在 `/tmp/` 目录中。如果未指定 `--output`，则默认输出文件为 `/tmp/gtex_output.json`。

## 命令

### 1. `resolve-gencode-id` — 基因符号 → GENCODE ID

将标准基因符号（例如 "JUN"、"TNF"）映射到其版本化的 GENCODE ID。此 ID 是所有其他表达和 eQTL 调用的必要项。

```bash
uv run scripts/gtex_cli.py resolve-gencode-id TNF --output /tmp/tnf_id.json
```

*参数：*

-   `gene_symbol` (位置参数)：标准基因符号（例如 "TNF"）。
-   `--output`：输出文件路径（默认：`/tmp/gtex_output.json`）。

### 2. `get-median-expression` — 获取中位数表达（TPM）

检索基因在所有 54 个 GTEx 组织位点或指定组织位点上的中位数 TPM。

```bash
uv run scripts/gtex_cli.py get-median-expression ENSG00000232810.2 \
  --tissues "Whole Blood,Spleen" --output /tmp/expr.json
```

*参数：*

-   `gencode_id` (位置参数)：版本化的 GENCODE ID。
-   `--tissues`：组织 ID 的逗号分隔列表（可选，默认为所有 54 个组织）。
-   `--output`：输出文件路径（默认：`/tmp/gtex_output.json`）。

### 3. `get-top-expressed-tissues` — 获取表达量最高的组织

返回目标基因中位数表达量最高的 `n` 个组织。

```bash
uv run scripts/gtex_cli.py get-top-expressed-tissues ENSG00000232810.2 \
  --n 5 --output /tmp/top_tissues.json
```

*参数：*

-   `gencode_id` (位置参数)：版本化的 GENCODE ID。
-   `--n`：返回的最高组织数量（默认：5）。
-   `--output`：输出文件路径。

### 4. `get-gene-eqtls` — 获取基因的所有 eQTLs

返回与基因在指定组织中相关的所有显著 eQTLs。

```bash
uv run scripts/gtex_cli.py get-gene-eqtls ENSG00000232810.2 \
  --tissues "Whole Blood" --output /tmp/eqtls.json
```

*参数：*

-   `gencode_id` (位置参数)：版本化的 GENCODE ID。
-   `--tissues`：组织 ID 的逗号分隔列表（可选，默认为所有）。
-   `--output`：输出文件路径。

### 5. `get-eqtls-in-region` — 获取染色体区域内的 eQTLs

返回染色体窗口内（最多 8Mb）的所有显著单组织 eQTLs。

```bash
uv run scripts/gtex_cli.py get-eqtls-in-region chr17 7000000 7100000 "Esophagus - Muscularis" \
  --output /tmp/region_eqtls.json
```

*参数：*

-   `chromosome` (位置参数)：染色体名称（例如 `chr17`）。
-   `start` (位置参数)：起始位置。
-   `end` (位置参数)：结束位置（从起始位置最多 8Mb）。
-   `tissue_id` (位置参数)：目标组织 ID。
-   `--output`：输出文件路径。

## 典型工作流程

### 识别基因表达量最高的组织

```bash
# 第一步：将符号映射到 GENCODE ID
uv run scripts/gtex_cli.py resolve-gencode-id GATA4 --output /tmp/gata4_id.json

# 第二步：使用解析的 ID 查询最高组织
uv run scripts/gtex_cli.py get-top-expressed-tissues <gencode_id> --n 5 \
  --output /tmp/gata4_top.json
```
