# ENCODE数据库技能

该技能允许您通过SCREEN GraphQL API查询ENCODE注册中心中的cCRE（候选顺式调控元件）。它通过分析生化特征（DNase、H3K4me3、H3K27ac、CTCF）帮助识别功能性非编码DNA元件（如启动子、增强子和绝缘子）。

## 前置条件

1.  **`uv`**：阅读`uv`技能并遵循其设置说明，确保`uv`已安装并在PATH中。
2.  **用户通知**：如果工作区根目录中不存在`.licenses/encode_ccres_database_LICENSE.txt`，则（1）显著通知用户检查[https://www.encodeproject.org/help/rest-api/](https://www.encodeproject.org/help/rest-api/)处的条款，然后（2）创建记录通知文本和时间戳的文件。

## 核心规则

-   **使用包装器**：始终使用提供的辅助脚本来查询数据库，而不是直接访问数据库。脚本会自动优雅地执行所需的速率限制。
-   **解析输出**：不要使用`cat`将整个JSON输出文件读入上下文，因为它可能非常大。您必须使用`jq`来高效地解析并提取相关字段。
-   **通知**：如果使用此技能，请确保在输出中提及。

### 快速入门

```bash
# 通过坐标搜索cCRE
uv run scripts/screen_api.py search --chromosome chr11 \
  --start 5205263 --end 5207263 \
  --output /tmp/search.json

# 获取特定cCRE的详细信息
uv run scripts/screen_api.py details EH38E2941922 \
  --output /tmp/details.json
```

所有子命令将JSON写入磁盘。始终将输出保存在临时位置，如`/tmp/`。

### 识别高置信度（"类型A"）生物样本

ENCODE中的生物样本通常按其数据完整性进行分类。"**类型A**"（或高置信度）生物样本是指具有所有四个核心表观遗传标记（**DNase、H3K4me3、H3K27ac和CTCF**）的实验数据的生物样本。

`biosamples`和`details`命令会自动在其输出中为每个生物样本添加`is_type_a`布尔标志。

**示例：查找高置信度的细胞类型**

```bash
uv run scripts/screen_api.py biosamples --output /tmp/biosamples.json
# 使用jq过滤类型A生物样本
jq '.data.ccREBiosampleQuery.biosamples[] | select(.is_type_a == true) | .displayname' /tmp/biosamples.json
```

### 解析输出（关键）

**不要使用`cat`将整个JSON输出文件读入上下文，因为它** **可能非常大。** 相反，您必须使用`jq`来高效地解析并提取脚本保存的JSON文件中的相关字段。如果系统上没有`jq`，请编写自己的Python过滤代码（例如，`python3 -c "import json..."`）来提取必要的数据。

要获取每个子命令返回的JSON结构的完整参考（以便知道使用`jq`查询哪些字段），请阅读`references/json_output_structure.md`。

### 可用命令

-   `search`：通过坐标、访问权限或表观遗传信号搜索cCRE。

    ```bash
    uv run scripts/screen_api.py search \
        --chromosome chr11 --start 5205263 --end 5207263 \
        --output /tmp/search.json
    ```

-   `nearby-genes`：为给定cCRE访问权限查找附近的基因。

    ```bash
    uv run scripts/screen_api.py nearby-genes \
        EH38E1516972 --output /tmp/nearby.json
    ```

-   `details`：获取特定cCRE的详细信息和生物样本特定的最大Z分数。

    ```bash
    uv run scripts/screen_api.py details EH38E2941922 \
        --output /tmp/details.json
    ```

-   `biosamples`：获取汇编的生物样本元数据。

    ```bash
    uv run scripts/screen_api.py biosamples \
        --output /tmp/biosamples.json
    ```

-   `orthologs`：获取另一个汇编中的同源cCRE。

    ```bash
    uv run scripts/screen_api.py orthologs EH38E2941922 \
        --output /tmp/orthologs.json
    ```

-   `linked-genes`：通过HiC或eQTL等方法查找相关基因。

    ```bash
    uv run scripts/screen_api.py linked-genes \
        EH38E1516972 --output /tmp/linked.json
    ```

-   `gene-expression`：获取指定基因在所有生物样本中的基因表达（TPM）。内部将基因符号解析为Ensembl基因ID，然后查询每个生物样本的RNA-seq定量。

    ```bash
    uv run scripts/screen_api.py gene-expression GAPDH \
        --output /tmp/gene_expr.json
    ```

-   `entex`：获取cCRE或基因组区域的ENTEx数据。

    ```bash
    uv run scripts/screen_api.py entex \
        --accession EH38E1310345 \
        --output /tmp/entex.json
    ```

    ```bash
    uv run scripts/screen_api.py entex \
        --region chr1:1000068:1000409 \
        --output /tmp/entex.json
    ```

-   `gwas`：查询全基因组关联研究、SNPs或富集数据。

    ```bash
    uv run scripts/screen_api.py gwas studies \
        --output /tmp/gwas.json
    ```

    ```bash
    uv run scripts/screen_api.py gwas snps --study \
        Ahola-Olli_AV-27989323-Eotaxin_levels \
        --output /tmp/gwas_snps.json
    ```

您可以提供`--assembly mm10`或`--assembly grch38`标志来显式请求特定汇编。默认情况下，脚本针对`grch38`，但如果未找到结果或查询失败，则会自动回退到`mm10`。

## ENCODE门户REST API（直接访问）

要访问SCREEN中未表示为cCRE的原始实验、ChIP-seq峰或其他数据集，请使用`scripts/encode_portal_api.py`脚本。它允许对ENCODE门户REST API进行自定义查询。

### 用法

```bash
uv run scripts/encode_portal_api.py search "type=Experiment&target.label=ZNF549" --output /tmp/znf549_experiments.json
```

### 数据分析技巧

当分析从ENCODE下载的`.bed`或`.bigBed`文件时，强烈建议使用标准生物信息学工具来查找重叠（例如，基因启动子和峰之间）：

-   **`bedtools`**：用于对基因组区间进行快速数学操作。
-   **`bigBedToBed`**：用于将二进制BigBed文件转换为可读的BED格式。
-   **`pybedtools`**：`bedtools`的Python包装器。

如果这些工具未预安装，请编写自定义逻辑。

## 自定义查询（SCREEN GraphQL）

如果您需要执行脚本不支持的复杂GraphQL查询，请阅读`references/graphql_schema.md`，以获取SCREEN GraphQL API中可用查询、参数和返回字段的参考。
