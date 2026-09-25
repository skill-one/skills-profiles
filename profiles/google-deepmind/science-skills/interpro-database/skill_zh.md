# InterPro 数据库访问

## 前置条件

1.  **`uv`**: 阅读 `uv` 技能并遵循其设置说明，确保 `uv` 已安装并在 PATH 中。
2.  **用户通知**: 如果工作区根目录中不存在 `.licenses/interpro_database_LICENSE.txt`，则 (1) 显著通知用户检查条款 [https://www.ebi.ac.uk/interpro/](https://www.ebi.ac.uk/interpro/) 和 [https://www.ebi.ac.uk/about/terms-of-use/](https://www.ebi.ac.uk/about/terms-of-use/)，然后 (2) 创建记录通知文本和时间戳的文件。

## 概述

InterPro 将来自多个、多样化的数据库的签名组合成一个可搜索的资源，减少冗余并帮助用户解释其序列分析结果。通过整合这些成员数据库（例如 Pfam、CDD、SMART），InterPro 利用它们的各自优势，产生一个强大的诊断工具和集成资源。

使用 `interpro-database`：

-   识别特定蛋白质中存在的域、家族和位点。
-   识别所有属于蛋白质家族或包含特定域的蛋白质，即使蛋白质的名称和活性高度可变。
-   检查特定蛋白质家族或域存在的物种。
-   使用蛋白质家族信息和 Gene Ontology (GO) 术语对基因组进行注释。

此技能提供了一个强大的实用程序 `interpro_client.py`，用于无缝地与 InterPro API 交互。它原生处理速率限制（HTTP 429）、后台查询睡眠跟踪（HTTP 408）、终端错误（HTTP 404/410）和惰性分页。

## 核心规则

-   **使用包装器**: 始终使用 `scripts/interpro_client.py` 辅助脚本查询数据库，而不是直接访问数据库。脚本会自动执行公平使用并实现重试逻辑。
-   **用于探索性查询**: 始终使用具有严格 `--limit` 的 CLI。这允许您快速了解数据模式，而不会污染您的上下文窗口或获取数百万个结果。
-   **输出到文件**: 使用具有 `--output` 的 CLI 输出到文件，而不是尝试将所有内容打印到控制台。使用 jq 或代码处理输出。
-   **用于更复杂的管道**: 原生将模块导入您的 Python 脚本中，直接消费生成器，防止在大型工作流中需要反序列化 CLI 字符串。
-   **通知**: 如果使用此技能，请确保在输出中提及。

示例：

```bash
uv run ./scripts/interpro_client.py fetch protein --source_db reviewed --limit 2 --query_params tax_id=9606 --output exploratory_results.jsonl
```

```python
import sys
sys.path.append('scripts')
from interpro_client import fetch_interpro_data
import itertools

# fetch_interpro_data 惰性按页面生成结果
results = fetch_interpro_data(
    endpoint="entry",
    source_db="pfam",
    query_params={"page_size": 10}
)
for match in itertools.islice(results, 10):
    print(match["metadata"]["accession"])
```

### 4 种构造端点的方法：

参数严格映射到四种常见的 API 路径构造。**不要自行格式化 `/` 分隔的字符串：**

1.  **`/{endpoint}`** (例如 `/entry`) `uv run ./scripts/interpro_client.py fetch entry --limit 10 --output entries.jsonl`
2.  **`/{endpoint}/{sourceDB}`** (例如 `/entry/pfam`) `uv run ./scripts/interpro_client.py fetch entry --source_db pfam --limit 10 --output pfam_entries.jsonl`
3.  **`/{endpoint}/{sourceDB}/{accession}`** (例如 `/entry/pfam/PF00001`) `uv run ./scripts/interpro_client.py fetch entry --source_db pfam --accession PF00001 --limit 10 --output pf00001_entry.jsonl`
4.  **`/{endpoint}/{sourceDB}/{linked_endpoint}/{sourceDB}/{accession}`** (例如 `/entry/interpro/protein/uniprot/P04637`) `uv run ./scripts/interpro_client.py fetch entry \ --source_db interpro \ --linked_endpoint protein \ --linked_source_db uniprot \ --linked_accession P04637 \ --limit 10 --output p04637_entries.jsonl`

## 有效的源数据库 (`--source_db`)

每个端点只接受特定的 `source_db` 值。使用无效值将返回 404 错误。

*   **`/entry`** (16 个值): `interpro`, `pfam`, `cathgene3d`, `ssf`, `panther`, `cdd`, `profile`, `smart`, `ncbifam`, `prosite`, `prints`, `hamap`, `pirsf`, `sfld`, `antifam`.
*   **`/protein`** (3 个值): `uniprot` (所有), `reviewed` (SwissProt), `unreviewed` (TrEMBL).
*   **`/structure`** (1 个值): `pdb`.
*   **`/taxonomy`** (1 个值): `uniprot`.
*   **`/proteome`** (1 个值): `uniprot`.
*   **`/set`** (2 个值): `pfam`, `cdd`.

## 快速参考 / 核心端点及参数

**有关所有查询参数的完整、详尽列表，请参阅 [完整 API 参考](references/api_reference.md)。**

API 完全开放并支持 6 个核心端点。您可以使用上面描述的链接参数将它们组合。以下是每个端点可用的特定查询参数的嵌套列表：

*   **`/entry`** (域、家族、活性位点、重复或同源超家族条目)

    *   `integrated`: 按集成状态过滤（例如，`pfam`）。
    *   `type`: 按类型过滤（例如，`family`, `domain`, `homologous_superfamily`）。
    *   `go_term` / `go_category`: 按Gene Ontology过滤。
    *   `ida_search` / `ida_ignore` / `exact` / `ordered`: 按域架构过滤（见 IDA 搜索部分）。
    *   `extra_fields`: 请求附加数据（例如，`counters` 用于匹配坐标）。
    *   `group_by` / `sort_by`: 聚合或排序结果 *(有效值取决于上下文，请参阅 [完整 API 参考](references/api_reference.md))*。
    *   *示例*: `uv run ./scripts/interpro_client.py count entry --source_db pfam --query_params type=domain --output count.jsonl`

*   **`/protein`** (匹配条目或域的蛋白质记录)

    *   `tax_id`: 按分类学 ID 过滤（不搜索谱系）。
    *   `match_presence`: 按具有 InterPro 匹配的蛋白质过滤 (`true`/`false`)。
    *   `is_fragment`: 过滤完整与片段序列。
    *   `group_by`: 聚合结果（例如，`taxonomy`）。
    *   `extra_fields`: 请求序列或匹配详细信息。
    *   `isoforms` / `residues` / `structureinfo`: 包含特定子特征。
    *   `conservation` / `extra_features`: 添加残基保守性标志或 Mobidb/coil 特征 *(仅对 `/protein/{source_db}/{accession}` 有效)*。
    *   *示例*: `uv run ./scripts/interpro_client.py fetch protein --source_db uniprot --limit 20 --query_params tax_id=9606 --output human_proteins.jsonl`

*   **`/structure`** (链接到 InterPro 条目的 PDB 结构)

    *   `experiment_type`: 按实验方法过滤（例如，`X-RAY DIFFRACTION`）。
    *   `resolution`: 按分辨率限制过滤。
    *   `extra_fields`: 包含附加的结构元数据。
    *   `group_by`: 聚合结果。
    *   *示例*: `./scripts/interpro_client.py fetch structure --source_db pdb --accession 1ATP --limit 10 --output 1atp_structures.jsonl`

*   **`/taxonomy`** (分类学分布节点)

    *   `key_species`: 过滤以限制到关键物种。
    *   `with_names`: 包含科学名称。
    *   `filter_by_entry` / `filter_by_entry_db`: 与特定条目过滤交集。
    *   `extra_fields`: 附加分类学元数据。
    *   *示例*: `./scripts/interpro_client.py fetch taxonomy --source_db uniprot --accession 9606 --limit 10 --output human_taxonomy.jsonl`

*   **`/proteome`** (链接到 InterPro 的完整蛋白质组)

    *   `extra_fields`: 一般查询扩展。
    *   *示例*: `uv run ./scripts/interpro_client.py fetch proteome --source_db uniprot --accession UP000005640 --limit 10 --output proteome.jsonl`

*   **`/set`** (相关的条目集合，例如 Pfam 族群)

    *   `extra_fields`: 附加元数据 *(仅对 `/set/{sourceDB}` 有效)*。
    *   *示例*: `uv run ./scripts/interpro_client.py fetch set --source_db pfam --accession CL0001 --limit 10 --output pfam_clan.jsonl`

## InterPro 域架构 (IDA) 搜索

InterPro 提供了强大的工具，用于根据蛋白质的域架构（域的确切组合和顺序）进行搜索。由于 API 不允许一次查询多个域（例如，“给我具有 PF00069 和 PF00017 的蛋白质”），查找具有特定域组合的蛋白质需要两步过程。

### 第一步：查找匹配的架构 (`ida_search`)

在根 `/entry` 端点使用 `ida_search` 参数查找包含您指定域的所有域架构 (IDAs)。

-   **约束**:
    -   仅在根 `/entry` 端点上有效。
    -   不能与非 IDA 参数组合。
-   **修饰符** (仅与 `ida_search` 有效):
    -   `ida_ignore`: 在搜索中忽略给定的域（查询参数）。
    -   `ordered`: 确保域按指定的顺序出现（标志）。
    -   `exact`: 确保架构完全匹配（无附加域）（标志）。**需要 `ordered` 标志存在。**

**示例**: 查找同时包含激酶域（PF00069）和 SH2 域（PF00017）且顺序正确的架构：

```bash
uv run scripts/interpro_client.py fetch entry
  --query_params ida_search=PF00069,PF00017
  --flags ordered exact
  --output architectures.jsonl
```

*注意：这返回架构及其唯一的 `ida_id`，而不是所有单个蛋白质。*

### 第二步：为这些架构获取蛋白质 (`ida`)

一旦您从第一步获得 `ida_id`（例如，`619edbb...`），您可以通过过滤 `/protein` 端点获取所有共享该精确布局的实际蛋白质。

**约束**:

-   在 `/protein` 和 `/entry/{sourceDB}/{accession}` 端点上有效。

**示例**: 获取与第一步架构 ID 之一匹配的蛋白质：

```bash
uv run scripts/interpro_client.py fetch protein
  --source_db uniprot
  --query_params ida=619edbb2b445bfa3ad51bd894e3c115b025a5f25
  --output matching_proteins.jsonl
```

*(在构建管道或全面查询时，您将循环遍历第一步的所有 `ida_id`，并为每个 ID 运行第二步)。*

## InterPro 条目类型

每个 InterPro 条目都被分配一个类型，指示当蛋白质匹配条目时可以推断的内容：

-   **域**: 存在于各种生物学环境中的不同功能、结构或序列单元。示例：*PH 域* 或 *经典 C2H2 锌指*。
-   **家族**: 分享共同进化起源的蛋白质组，反映功能、序列相似性或初级/二级/三级结构。示例：*Pfam 家族*。
-   **同源超家族**: 分享进化起源的蛋白质，通常具有结构相似性但序列相似性很低。通常包含来自 SUPERFAMILY 和 CATH-Gene3D 数据库的签名。
-   **重复**: 通常长度小于 50 个氨基酸的短序列，在蛋白质内部重复。示例：*富含亮氨酸的重复* 或 *WD40 重复*。
-   **位点**: 包括 `活性位点`（包含催化活性保守残基的序列）和 `结合位点`（形成蛋白质相互作用位点的保守残基序列）。

## InterPro-N 预测

InterPro-N 是标准 InterPro 数据库的基于深度学习的扩展。它利用受计算机视觉启发的 AI 架构将蛋白质序列注释视为“全景分割”任务，标记残基并区分域。

### 何时使用 InterPro-N

标准 InterPro 签名是“黄金标准”，不应因 InterPro-N 预测而放弃。主要使用 InterPro-N 来填补空白或完善结果。

**除了标准 InterPro 之外：**

-   **分析“暗物质”（未表征蛋白质）**: 当蛋白质在标准 InterPro 中没有命中时使用。InterPro-N 在识别远程同源物方面表现出色。
-   **解决复杂重复**: 用于具有多个串联重复（例如 TPR 或 WD40）的蛋白质，其中标准 HMM 可能会合并或遗漏它们。
-   **预测不连续域**: 当域序列被完全不同的插入序列中断时使用。

**在以下特定情况下代替标准 InterPro：**

-   **精确边界界定**: 当您需要比模糊标准命中提供的更准确的域起始和结束坐标时。
-   **大规模宏基因组筛选**: 用于初始高回收率的片段化或高度分化序列的筛选。

### Fallback 策略：检查 InterPro-N

当您被要求为蛋白质查找注释，而标准 InterPro 查询未返回结果或未返回注释时，您**必须**将 InterPro-N 作为 Fallback 检查。

**示例场景**：如果用户要求“列出蛋白质 X 的 SSF 注释”，而标准查询未命中，您应该重试使用 `interpro_n` 标志的查询。

这种 Fallback 至关重要，因为 InterPro-N 可以识别标准方法遗漏的“暗物质”蛋白质中的远程同源物和域。

如果找到，**始终**向用户报告这些注释来自 InterPro-N 的深度学习预测。

### 如何使用

通过向源数据库为 `uniprot` 的 `protein` 端点传递 `interpro_n` 标志来访问 InterPro-N 预测。

**通过 CLI:**

```bash
uv run ./scripts/interpro_client.py fetch protein
    --source_db uniprot
    --accession A0A096LNN2
    --flags interpro_n
    --output A0A096LNN2_interpro_n.jsonl
```

**通过 Python 管道:**

```python
results = fetch_interpro_data(
    endpoint="protein",
    source_db="uniprot",
    accession="A0A096LNN2",
    flags=["interpro_n"])
```

## 严格查找规则

1.  **始终使用 UniProt Accession，绝不要使用基因名称**: 在 InterPro 中查找蛋白质时，您**必须**使用它们的 UniProt Accession（例如 `P04637`）。InterPro 不原生支持或可靠映射基因名称（例如 `TP53`）。如果用户提供基因名称，您必须使用 Ensembl 或 UniProt 等数据库首先将其解析为 accession。

2.  **绝不要迭代计数**: 当要求聚合计数（例如，“有多少个域？”）时，您**必须**使用 `get_interpro_count()` 辅助函数从初始 API JSON 响应中读取 `count` 字段。绝不要迭代 `fetch_interpro_data` 生成器来统计元素。迭代具有 50,000+ 条目的端点只是为了计数会无声地挂起代理并滥用 API。每次都是如此。没有例外。

    ✅ **正确**:

    **通过 CLI:**

    ```bash
    uv run ./scripts/interpro_client.py count entry
        --source_db interpro
        --query_params type=domain
        --output count.json
    ```

    **通过 Python 管道:**

    ```python
    from interpro_client import get_interpro_count
    cnt = get_interpro_count(
        endpoint="entry",
        source_db="interpro",
        query_params={"type": "domain"},
    )
    ```

    ❌ **错误**（迭代 fetch）:

    ```bash
    # 绝对不要这样做：
    uv run ./scripts/interpro_client.py fetch entry
        --source_db interpro
        --query_params type=domain
        --output output.jsonl
        && wc -l output.jsonl
    ```

## 快速示例

**有关各种端点调用的详细示例和返回的 JSON 输出模式，请参阅 [示例响应参考](references/example_responses.tsv)。** 此 TSV 包含命令行调用、Python 等价物和相应的 JSON 有效负载结构。

### 1. 确定所有蛋白质域

```bash
# 获取 UniProt 蛋白质 P04637 中的 InterPro 条目
# URL 等价：/entry/interpro/protein/uniprot/P04637
uv run ./scripts/interpro_client.py fetch entry
    --source_db interpro
    --linked_endpoint protein
    --linked_source_db uniprot
    --linked_accession P04637
    --output p04637_domains.jsonl
```

### 2. 获取条目的所有 PDB 结构

```bash
# URL 等价：/structure/pdb/entry/interpro/IPR011615
# 仅获取前 5 个结构
uv run ./scripts/interpro_client.py fetch structure
    --source_db pdb
    --linked_endpoint entry
    --linked_source_db interpro
    --linked_accession IPR011615
    --output ipr011615_structures.jsonl
```
