# 使用AlphaGenome进行变异分析

## 前置条件

1.  **`uv`**: 阅读`uv`技能并遵循其设置说明，确保`uv`已安装并在PATH路径中。
2.  **用户通知**: 如果工作区根目录中不存在`.licenses/alphagenome_single_variant_analysis_LICENSE.txt`，则 (1) 向用户显著通知检查条款 [https://deepmind.google.com/science/alphagenome/](https://deepmind.google.com/science/alphagenome/) ，然后 (2) 创建记录通知文本和时间戳的文件。
3.  **`.env`文件**: 确保您的家目录中存在`.env`文件。如果不存在，请创建一个。
4.  **`ALPHAGENOME_API_KEY`**: 此技能需要API密钥才能运行。

    您可以在 [https://deepmind.google.com/science/alphagenome/](https://deepmind.google.com/science/alphagenome/) 注册密钥。
    如果此技能与用户请求相关，您**必须**在`credentials`技能中使用安全凭证协议检查并请求此密钥。
5.  **`ALPHAGENOME_GTF_PATH` (可选)**: 通过指向本地GTF feather文件的路径，而不是从GCS下载，来加速基因/转录本查找：

    ```bash
    echo "ALPHAGENOME_GTF_PATH=/path/to/local/gencode.v46.annotation.gtf.gz.feather" >> ~/.env
    ```

## 核心规则

-   **绝对不要直接运行`python3`或`python3 -c`。** 系统Python不一定包含pandas、numpy和其他关键依赖项。**始终**使用`uv run`来运行所有Python代码——包括脚本、临时分析文件和单行代码。不要尝试`pip install`或创建新的venv——`uv`会自动管理隔离环境。
-   **仅限离线使用**: 绝对不要使用外部API（例如MyGene.info、Ensembl REST）进行基因/转录本查找。使用`lookup_gene_info.py`和本地GTF。如果失败，请修复环境/路径，不要切换到外部API。
-   **需要API密钥**: 在运行任何脚本之前，必须设置`ALPHAGENOME_API_KEY`。
-   **通知**: 如果使用此技能，请确保在输出中提及。
-   **报告格式**: 始终使用`docs/report-templates.md`中的模板来生成分析报告，并确保包含发现扫描的顶部命中表。

## 环境设置与故障排除

### Python环境

所有脚本必须使用`uv run`执行，它通过`uv`管理具有正确依赖项的隔离虚拟环境。

```bash
uv run <script_name> [args...]
```

对于临时脚本（例如保存在临时文件中的内联分析代码），请传递完整路径而不是短名称：

```bash
uv run --project $SKILL_DIR /tmp/my_analysis.py --arg1 val1
```

> [!NOTE] 第一次调用会解析并安装依赖项（约10秒）。后续运行将使用缓存的环境并立即启动。缓存位于`~/.cache/uv/`。

### 常见问题

-   **列名**: `tidy_scores`和元数据通常使用`gene_name`（而不是`gene_symbol`）和`output_type`（而不是`modality`）。在过滤之前，始终检查`df.columns`。
-   **大基因**: 基因>500kb（例如`USH2A`）会破坏`whole_gene`视图。使用`--view detail`或手动区域窗口。
-   **Sashimi链错误**: `plot_components.Sashimi`不直接接受`strand`参数。过滤输入轨道。
-   **KeyError: 'ontology_curie'**: 并非所有轨道都有`ontology_curie`。在过滤之前，请检查`track.metadata.columns`。
-   **Python路径**: 如果出现`exec: "python": 可执行文件未找到`，请确保您使用的是`uv run`而不是裸`python`/`python3`。
-   **NotImplementedError (pandas)**: "iLocation based boolean indexing on an integer type is not available"。这发生在使用`.iloc`在较新版本的pandas中针对整数索引的DataFrame时进行布尔掩码时。**修复方法**: 使用`np.flatnonzero(mask)`将布尔掩码转换为整数索引。
-   **GTF Feather大小写敏感**: AlphaGenome GTF Feather文件使用**大写**的列名（`Feature`、`Start`、`End`、`Strand`），这与标准GTF文件不同。如果出现KeyErrors，请始终检查`df.columns`。
-   **`score_variant`本体过滤**: `score_variant`不接受`ontology_terms`作为参数。您必须手动过滤返回的AnnData对象，通过检查`adata.var`列。相比之下，`predict_variant`可以直接接受`ontology_terms`。
-   **Sashimi缩放逻辑**: 为了确保"跳过"的弧可见，请将缩放扩展以包含**侧翼外显子**，而不是仅依赖连接重叠。
-   **连接分数**: 来自`prediction`的原始`Junction`对象可能是简单的Intervals。使用`junction_data.get_junctions_to_plot(predictions=..., name=...)`检索具有`.k`（丰度/分数）属性的对象。
-   **`uv`未找到**: 如果出现`exec: uv: not found`，请按照[前置条件](#prerequisites)中的安装说明进行操作。
-   **注册身份验证错误 (401)**: 如果`uv`因私有注册失败而显示401未授权，请在运行脚本之前设置`UV_INDEX_URL=https://pypi.org/simple`。

## 参考文献

-   [alphagenome-api.md](docs/alphagenome-api.md) — API参考和代码模式
-   [interpretation-guide.md](docs/interpretation-guide.md) — 解释指南、分数大小规则、ISM和清单。
-   [report-templates.md](docs/report-templates.md) — 完整报告模板
-   [`scripts/visualize_variant_effects.py`](scripts/visualize_variant_effects.py) — 单变异可视化模板（Ref/Alt比较、剪接）。
    -   **剪接缩放策略**: 使用**混合方法**以获得最佳可见性：
        1.  **基本区间**: 变异 +/- 1下游和上游外显子（结构背景）。
        2.  **连接扩展**: 扩展以包含任何**重要剪接连接**的完整跨度（例如跨越多个外显子的外显子跳过事件）。
        3.  **锚定强制**: 确保锚定这些长连接的外显子完全可见。*经验*: 简单固定窗口（例如2kb）或最近外显子逻辑通常无法处理跳过事件。始终使用*观察到的连接数据*来驱动缩放级别。
-   [`examples/splicing/`](docs/examples/splicing/) — 剪接分析示例
-   [`examples/model_limitation_RNU4ATAC/`](docs/examples/model_limitation_RNU4ATAC/) — ncRNA结构限制案例研究
-   [`examples/polyadenylation_HBA2/`](docs/examples/polyadenylation_HBA2/) — 3' UTR / 聚腺苷酸化案例研究
-   [`examples/regulatory/`](docs/examples/regulatory/) — 调控变异示例
-   [`examples/negative_result_GATA4/`](docs/examples/negative_result_GATA4/) — 负面结果（数学伪影）
-   [`examples/negative_result_TGFB3/`](docs/examples/negative_result_TGFB3/) — 负面结果（代理）
-   [`scripts/lookup_gene_info.py`](scripts/lookup_gene_info.py) — 基因和转录本查找
-   [`scripts/resolve_ontology_terms.py`](scripts/resolve_ontology_terms.py) — 本体术语解析（UBERON/CL ID）

--------------------------------------------------------------------------------

## 代码模式

### 广泛发现扫描

使用`score_variant`仅针对**差异评分器**来发现意外的组织效应。

```python
from alphagenome.models import dna_client
from alphagenome.models import variant_scorers
from alphagenome.data import genome
import os
import pandas as pd
import dotenv

# 从~/.env加载环境变量
dotenv.load_dotenv(os.path.expanduser('~/.env'))

# 设置API密钥和客户端
dna_model = dna_client.create(api_key=os.environ.get('ALPHAGENOME_API_KEY'),
                              address='dns:///gdmscience.googleapis.com:443')

# 定义变异（示例）
variant_str = "chr2:1234:A>C"
chrom, pos_str, ref_alt = variant_str.split(':')
ref, alt = ref_alt.split('>')
pos = int(pos_str)

# 使用支持的序列长度（例如，2**20以获得最佳性能）
SEQ_LENGTH = 2**20
interval = genome.Interval(chrom, pos - SEQ_LENGTH // 2, pos + SEQ_LENGTH // 2)
variant = genome.Variant(chrom, pos, ref, alt)

scorers = [
    variant_scorers.RECOMMENDED_VARIANT_SCORERS[m]
    for m in variant_scorers.RECOMMENDED_VARIANT_SCORERS
    if "ACTIVE" not in m and "CAGE" not in m and "PROCAP" not in m
]

print(f"Scoring variant {variant_str}...")
scores_list = dna_model.score_variant(interval=interval, variant=variant, variant_scorers=scorers)

# 处理并显示结果
all_dfs = []
for score_adata in scores_list:
    df = variant_scorers.tidy_scores([score_adata], match_gene_strand=True)
    if df is not None:
        all_dfs.append(df)

if all_dfs:
    df = pd.concat(all_dfs)
    significant = df[df['quantile_score'].abs() > 0.995]
    ranked = significant.sort_values('raw_score', key=abs, ascending=False)
    print("Top Significant Hits:")
    print(ranked[['biosample_name', 'gene_name', 'output_type', 'quantile_score', 'raw_score']])
```

### 扩展搜索以查找与疾病相关的组织

```python
# 根据疾病背景定义关键词
disease_keywords = ["liver", "hepatocyte"]

# 过滤任何匹配项
mask = df['biosample_name'].str.contains('|'.join(disease_keywords), case=False, na=False)

relevant_hits = df[mask].sort_values('raw_score', key=abs, ascending=False)
print(f"\n--- Extended Analysis (Keywords: {disease_keywords}) ---")
print(relevant_hits.head(20)[['biosample_name', 'output_type', 'raw_score', 'quantile_score']])
```

## 工作流清单

```
变异分析进度：
- [ ] 第0步：查看黄金示例（强制）
- [ ] 第1步：创建输出文件夹和设置
- [ ] 第2步：解析用户查询与研究
- [ ] 第3步：解析组织与模式
- [ ] 第4步：可视化并保存图形
- [ ] 第5步：分析预测（查看图形，无代码）。强制：解释结果前阅读[interpretation-guide.md](docs/interpretation-guide.md)。
- [ ] 第6步：撰写报告，保存为`report.md`（强制）
- [ ] 第7步：自我批评（查看`report.md`以验证链接和声明）
- [ ] 第8步：将`report.md`制作成工件
```

--------------------------------------------------------------------------------

## 多变异工作流

如果指定了多个变异，请生成子代理来运行每个变异分析，然后将每个`report.md`合成到单个报告中。

### 脚本参考

| 脚本                      | 目的                                        |
| --------------------------- | ---------------------------------------------- |
| `lookup_gene_info`          | 使用GTF数据进行的综合基因和转录本查找         |
| `resolve_ontology_terms`    | 生物术语→ UBERON/CL/EFO ID                  |
| `visualize_variant_effects` | REF/ALT可视化（表达、调控、剪接）            |
| `analyze_ism`               | In-Silico Mutagenesis SeqLogo生成            |
| `interpret_splicing`        | 定量剪接分析（delta分数、连接）              |
| `visualize_genome_tracks`   | 区域基因组轨道可视化                        |
