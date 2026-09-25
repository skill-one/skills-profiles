# gnomAD数据库

## 前置条件

1.  **`uv`**: 阅读`uv`技能并遵循其安装说明，确保`uv`已安装并在PATH路径中。
2.  **用户通知**: 如果工作区根目录中不存在`.licenses/gnomad_database_LICENSE.txt`文件，则 (1) 醒目地通知用户检查条款，网址为https://gnomad.broadinstitute.org/policies 和 https://gnomad.broadinstitute.org/data#api，然后 (2) 创建记录通知文本和时间戳的文件。

## 核心规则

-   **使用封装器**: 始终使用提供的辅助脚本来查询数据库，而不是直接访问数据库。脚本会自动优雅地执行gnomAD API速率限制。
-   **通知**: 如果使用此技能，请确保在输出中提及这一点。

## 实用脚本

所有脚本都位于此技能安装目录的`scripts/`子目录中。运行它们时，请使用脚本的完整绝对路径（例如 `/path/to/gnomad_database/scripts/get_variant_frequency.py`）。

**1. 变异频率**。检索外显子组、全基因组和总数据（外显子组+全基因组合并）的全局和种族特异性等位基因频率、纯合子计数以及**Grpmax过滤AF**（faf95/faf99）。过滤等位基因频率（FAF）是最大可信遗传祖先群体AF（95%或99% CI的下限）。变异ID格式必须为`chrom-pos-ref-alt`（例如 `1-55516888-G-GA`）。或者，您可以提供`rsID`。

```bash
# 通过变异ID:
uv run scripts/get_variant_frequency.py --variant_id {variant_id} [--dataset {dataset}] --output variant_frequency.json

# 通过rsID（例如，rs1800562）:
uv run scripts/get_variant_frequency.py --rsid {rsid} [--dataset {dataset}] --output variant_frequency.json
```

**2. 基因约束**。检索基因的约束指标。响应将明确包含`pli`，LOEUF分数由`oe_lof_upper`表示。

```bash
uv run scripts/get_gene_constraint.py --gene {gene_symbol} --output {gene_symbol}_constraint.json
```

**3. 区域/基因变异搜索**。查找区域或基因中的所有变异。

```bash
# 通过区域:
uv run scripts/search_variants.py --chrom {chrom} --start {start} --end {end} --output region_variants.json
# 通过基因:
uv run scripts/search_variants.py --gene {gene_symbol} --consequence {pLoF|missense} --output {gene_symbol}_variants.json
```

## 参考文献

有关数据的更多文档：https://gnomad.broadinstitute.org/data#api
更多通用数据库文档：https://gnomad.broadinstitute.org/help
