# 影像数据公共库

## 概述

从国家癌症研究院影像数据公共库（IDC）查询并下载公共癌症影像数据。数据访问无需身份验证。

**预期网络访问：** IDC 元数据可通过三种方式访问——随 `idc-index` Python 包一起发布的本地 DuckDB 索引（无需网络），或通过 MCP 或 REST 访问托管的 IDC 服务（`api.imaging.datacommons.cancer.gov`，无需身份验证）。文件下载使用公共 GCS（`storage.googleapis.com`）和 AWS S3（`s3.amazonaws.com`）——无需身份验证。DICOMweb 访问使用公共 IDC 代理（`proxy.imaging.datacommons.cancer.gov`，无需认证）或 Google Cloud Healthcare API（`healthcare.googleapis.com`，需要 GCP 认证）。可选的 BigQuery 查询（`bigquery.googleapis.com`）同样需要 GCP 认证。本技能不访问任何凭证或环境变量。

**当前 IDC 数据版本：v24**（务必核实——参见*最佳实践*）

**首先选择访问路径。** 不存在单一默认选项：最经济且正确的路径取决于会话和任务。

1. **会话中是否已有 IDC MCP 服务器？** 将发现和元数据路由到该服务器——参见*IDC MCP 服务器*。
2. **否则，是否已安装 `idc-index`？** 运行 `python scripts/check_version.py`。如果通过，则对一切使用 `idc-index`。
3. **未安装，且任务仅限只读元数据**——计数、属性值、集合查找、10 000 行以内的 SQL、许可证、引用、查看器 URL？**使用 `curl` 调用 REST API；不要安装任何东西。** 安装需要约 77 MB 的打包索引数据以及 pandas、pyarrow 和 duckdb，而元数据问题并不需要这些。参见*数据访问选项*。
4. **未安装，且任务需要超出元数据的内容**——下载文件、pandas 或绘图、pydicom/SimpleITK、病理瓦片切分、超过 10 000 行的结果，或用户会重复运行的版本锁定脚本？安装 `idc-index`：`check_version.py` 会返回非零退出码并打印当前解释器对应的精确安装命令。优先使用虚拟环境，然后重启 Python。

`idc-index`（[GitHub](https://github.com/imagingdatacommons/idc-index)）仍然是能力最强的路径，也是唯一能传输图像字节的方案；规则只是在任务尚未需要时不要提前付费使用它。`check_version.py` 本身永远不会安装任何东西——当存在更新的 `idc-index` 或技能版本时，它也会标记出来。

**`idc-index` 路径的设置：**

```python
from idc_index import IDCClient
client = IDCClient()

# 验证 IDC 数据版本（应为 "v24"）
print(f"IDC 数据版本：{client.get_idc_version()}")
```

**核心工作流：** 使用 `client.sql_query()` 查询元数据 → 使用
`client.download_from_selection()` 下载 → 使用 `client.get_viewer_URL()` 可视化。以下 Python 示例假设已创建此 `client`；*数据访问选项*中有 REST 等价操作。要了解当前数据规模，请运行 `references/sql_patterns.md` 中的汇总查询或 `GET /v3/stats`。

## IDC MCP 服务器

IDC 在 `https://api.imaging.datacommons.cancer.gov/mcp`
运营托管的 MCP 服务器（可流式 HTTP，无需认证）。在可用时，它是对以下 `idc-index` 工作流的补充——而非替代。

**识别方式：** 通过 MCP 资源 `idc://guide`，或通过三个及以上的工具名称
`build_cohort`、`get_cohort_urls`、`list_analysis_results` 和 `get_idc_version`。通用名称如 `run_sql` 本身不构成证据。如果识别不明确，使用
`idc-index`。

**如果此会话中有该服务器**，将其视为发现和元数据的权威来源——
IDC 版本、计数、属性值、队列构建、元数据 SQL——并遵循服务器自身的说明，而非从本文件重新推导。其数据版本以服务器报告为准：调用 `get_idc_version` 而非依赖本文件中固定的版本号。

服务器未涵盖的功能请回到这里：下载文件、本地 pandas/笔记本
分析、DICOMweb、BigQuery、数字病理瓦片切分，以及可复现脚本。通过
将服务器返回的 SeriesInstanceUID 传递给 `client.download_from_selection(...)` 进行交接，并在该时点运行
`scripts/check_version.py`。

**如果不可用**，相同的服务无需任何配置即可作为 REST
API 在 `https://api.imaging.datacommons.cancer.gov/v3` 访问——按照 *概述* 中的路由门控，
使用它进行只读元数据操作，而非安装 `idc-index`。最多建议连接一次 MCP
服务器，且仅用于重复的交互式发现操作；切勿自行更改用户配置。

工具清单、交接模式及各主机说明参见 `references/mcp_guide.md`。

## 何时使用此技能

- 查找公开发布的放射科（CT、MR、PET）或病理学（切片显微镜）影像
- 按癌症类型、模态、解剖部位或其他元数据选择影像子集
- 从 IDC 下载 DICOM 数据
- 在科研或商业应用使用前检查数据许可证
- 在浏览器中可视化医学影像，无需本地 DICOM 查看器软件

## 快速导航

以下内容内联在此：MCP/REST 路由规则、IDC 数据模型、索引表及其连接方式、核心 API 模式（查询、下载、可视化、许可证、引用）、最佳实践，以及故障排除。

**参考指南（按需加载）：**

| 指南 | 加载时机 |
|-------|--------------|
| `index_tables_guide.md` | 复杂 JOIN、模式发现、DataFrame 访问 |
| `use_cases.md` | 端到端工作流：训练数据集、批量下载、使用 pydicom/SimpleITK 读取 DICOM、流水线集成 |
| `sql_patterns.md` | 快速 SQL 模式：筛选发现、注释、大小估算 |
| `clinical_data_guide.md` | 临床/表格数据、影像+临床连接、值映射 |
| `licensing_and_citation.md` | 商用问题、混合许可证队列、引用格式 |
| `cloud_storage_guide.md` | 直接 S3/GCS 访问、版本控制、UUID 映射 |
| `dicomweb_guide.md` | DICOMweb 端点、PACS 集成 |
| `digital_pathology_guide.md` | 切片显微镜（SM）、注释（ANN）、病理工作流 |
| `bigquery_guide.md` | 完整 DICOM 元数据、私有元素（需要 GCP） |
| `cli_guide.md` | 命令行工具（`idc download`、清单文件） |
| `parquet_access_guide.md` | 通过 GCS 直接查询 Parquet（无需安装 idc-index） |
| `mcp_guide.md` | 托管 IDC MCP 服务器：工具清单、识别、向 `idc-index` 交接 |
| `rest_api_guide.md` | 托管 IDC REST API：端点、筛选语法、HTTP SQL、清单 |

## IDC 数据模型

IDC 在标准 DICOM 层级（患者 → 检查 → 序列 → 实例）之上增加了两个分组层级：

- **collection_id**：按疾病、模态或研究重点对患者进行分组（例如 `tcga_luad`、`nlst`）。一个患者恰好属于一个集合。
- **analysis_result_id**：跨一个或多个原始集合标识派生对象（分割、注释、影像组学特征）。使用它查找 AI 生成或专家注释，而 `collection_id` 则用于查找原始影像数据（其本身可能包含已提交的注释）。

**查询的关键标识符：**
| 标识符 | 范围 | 用途 |
|------------|-------|---------|
| `collection_id` | 数据集分组 | 按项目/研究筛选 |
| `PatientID` | 患者 | 按患者分组影像 |
| `StudyInstanceUID` | DICOM 检查 | 关联序列的分组、可视化 |
| `SeriesInstanceUID` | DICOM 序列 | 关联序列的分组、可视化 |

## 索引表

`idc-index` 包提供多个元数据索引表，可通过 SQL 或 pandas DataFrame 访问。REST API 通过 `GET /tables` 和 `POST /sql` 公开相同的表。

**重要：** `client.indices_overview` 是当前表描述、可用列及其类型的权威来源——编写 SQL 或探索数据结构时请查询它。它也能回答"哪个表包含列 X"；参见 `references/index_tables_guide.md` 了解该搜索模式及完整的模式发现方法。

### 可用表

查询任何索引表之前，始终先调用 `client.fetch_index("table_name")`——对所有表（包括启动时自动加载的表）它都是安全且幂等的。

| 类别 | 表 | 粒度 |
|--------|--------|-------------|
| 核心 | `index`（所有当前数据的主要元数据）、`collections_index`、`analysis_results_index` | 序列 / 集合 / 分析结果 |
| 模态采集参数 | `ct_index`、`mr_index`、`pt_index`、`contrast_index` | 1 行 = 该模态的 1 个序列 |
| 派生对象 | `seg_index`、`rtstruct_index`、`ann_index`、`ann_group_index` | 1 行 = 1 个序列（或注释组） |
| 显微镜 | `sm_index`、`sm_instance_index` | 1 行 = 1 个 SM 序列 / 实例 |
| 几何、临床、历史 | `volume_geometry_index`、`clinical_index`、`version_metadata_index`、`prior_versions_index` | 参见指南 |

`references/index_tables_guide.md` 包含完整的表清单及各表的列和内容——需要了解专用表实际包含什么时再加载它。

**`prior_versions_index` 仅用于可复现性。** 它包含从 IDC 中永久*移除*的序列，与 `index` 零重叠。仅用于复现针对旧版 IDC 的工作。切勿用它回答版本历史或"有什么新增"问题——那些应使用主 `index` 表中的 `series_init_idc_version` / `series_revised_idc_version`，它们与本表的 `min_idc_version` / `max_idc_version` 并不等价。

### 表连接

**`SeriesInstanceUID` 是所有序列级专用表的通用连接键**：`sm_index`、`sm_instance_index`、`seg_index`、`ann_index`、`ann_group_index`、`contrast_index`、`volume_geometry_index`、`rtstruct_index`、`ct_index`、`mr_index`、`pt_index`。连接这些表到 `index` 时始终使用 `SeriesInstanceUID`。下方列出的例外使用不同的列名。

| 连接列 | 表 | 使用场景 |
|-------------|--------|----------|
| `collection_id` | index、prior_versions_index、collections_index、clinical_index | 将序列连接到集合元数据或临床数据 |
| `analysis_result_id` | index、analysis_results_index | 将序列连接到分析结果元数据（注释、分割） |
| `source_DOI` | index、analysis_results_index | 按出版物 DOI 连接 |
| `segmented_SeriesInstanceUID` | seg_index → index | 将分割连接到其源影像序列（`seg_index.segmented_SeriesInstanceUID = index.SeriesInstanceUID`） |
| `referenced_SeriesInstanceUID` | ann_index → index、rtstruct_index → index | 将注释或 RTSTRUCT 连接到其源影像序列 |

**注意：** `subjects`、`updated` 和 `description` 出现在多个表中但含义不同（计数 vs 标识符，不同的更新上下文）。将 `prior_versions_index` 按 `SeriesInstanceUID` 连接到 `index` 始终返回零行——参见上方警告。

有关详细的连接示例、模式发现模式、关键列参考和 DataFrame 访问，参见 `references/index_tables_guide.md`。

### 临床数据访问

临床（非影像）属性——分期、人口学、治疗——存储在各集合的表中。`client.fetch_index("clinical_index")` 加载列到集合的映射字典；`client.get_clinical_table(name)` 返回单个表作为 DataFrame。

发现工作流、编码值映射以及临床数据与影像的连接参见 `references/clinical_data_guide.md`。

## 数据访问选项

| 方法 | 认证 | 适用场景 | 参考 |
|--------|------|----------|-----------|
| `idc-index` | 无 | 下载、pandas 分析、无限制查询——能力最强的路径 | 本文档 |
| IDC MCP 服务器 | 无 | 当会话中已有时用于发现、队列构建、元数据 | `mcp_guide.md` |
| IDC REST API | 无 | 无需安装的元数据操作，可从任何语言或 shell 调用——`idc-index` 不存在时的默认选择 | `rest_api_guide.md` |
| 直接 Parquet（GCS） | 无 | 版本锁定查询，或超出 REST 行数上限的结果 | `parquet_access_guide.md` |
| 云存储（S3/GCS） | 无 | 直接文件访问、批量传输、自定义流水线 | `cloud_storage_guide.md` |
| DICOMweb（IDC 代理） | 无 | 工具和 PACS 集成；有每日配额，适合测试和中等使用量 | `dicomweb_guide.md` |
| DICOMweb（Google Healthcare） | 是（GCP） | 同等 DICOMweb API 的生产级流量，无代理配额限制 | `dicomweb_guide.md` |
| SlicerIDCBrowser | 无 | 在 3D Slicer 中进行 3D 可视化和分析 | https://github.com/ImagingDataCommons/SlicerIDCBrowser |
| BigQuery | 是（GCP） | 完整 DICOM 元数据、私有元素、SR 测量值——最后手段 | `bigquery_guide.md` |

**IDC 门户（https://portal.imaging.datacommons.cancer.gov/）仅供交互式使用**——
基于浏览器的探索、手动队列选择和下载。与上述所有选项不同，
它没有编程接口，因此应引导用户到那里自行浏览或点击数据；切勿将其用作脚本或工作流中的步骤。

**REST API——无需安装的元数据路径**

`https://api.imaging.datacommons.cancer.gov/v3`，无需认证：发现、队列计数和
清单、只读 SQL、临床表、查看器 URL、许可证、引用。它是与 MCP 服务器相同的服务，通过普通 HTTP 提供，因此无需任何配置。它不会传输图像字节——下载、获取 DataFrame 或获取超过 10 000 行的结果时需切换到 `idc-index`。

```bash
B=https://api.imaging.datacommons.cancer.gov/v3
curl -s $B/version   # idc_version, idc_index_data_version, api_version
curl -s $B/stats     # collections, patients, studies, series, instances, size_TB
curl -s "$B/attributes/Modality/values?limit=5"   # 真实筛选值及计数
curl -s $B/sql -H 'content-type: application/json' \
  -d '{"sql":"SELECT collection_id, COUNT(*) n FROM index GROUP BY 1 ORDER BY n DESC LIMIT 3"}'
curl -s $B/cohort/counts -H 'content-type: application/json' \
  -d '{"filters":{"terms":{"collection_id":["rider_pilot"]}}}'
```

**筛选对象始终放在 `filters` 下**——无论 `cohort/counts`、`cohort/manifest`、
`cohort/manifest.txt`、`licenses` 还是 `citations`。裸筛选对象或未识别的键会返回 422 并指明修复方法；未筛选的序列枚举请求返回 400，而非返回整个档案。每个筛选响应都会回显 `filters_applied` 和 `warnings`——请阅读它们，因为它们会指明服务器丢弃了哪些谓词。计数为零且 `warnings` 为空意味着筛选未匹配到任何内容，而非某个值大小写错误；大小写错误会产生相应的警告。

`POST /sql` 接受一个只读的 `SELECT`/`WITH`，范围覆盖 `idc-index` 公开的表及
`clinical.<table>`；`max_rows` 默认为 5 000，上限 10 000，`truncated` 标记是否被截断。
`GET /attributes` 列出 19 个可筛选属性——临床值、分割解剖和采集参数不在其中，需要 SQL。无速率限制或配额。**仅使用 v3：** V1 和 V2 已被取代并计划关闭，因此请将用户带来的 `/v1/`- 或
`Modality_btw`- 风格示例进行迁移，而非在其基础上扩展。

两端都基于 `idc-index-data`，因此在混合使用前请比较 API 的 `idc_index_data_version` 与本地
`idc_index_data.__version__`：**主版本是 IDC 数据发布版本**（`24.x.y` 对应 `v24`），因此次/补丁版本不同意味着序列相同。如果 API 领先一个完整发布版本，`idc-index` **无法下载额外的序列**——它会静默跳过自身索引未列出的序列——因此要么升级（运行 `scripts/check_version.py` 获取正确命令）
要么使用 `s5cmd --no-sign-request` 直接从存储桶传输。

端点参考、筛选基础、限制及基于清单的下载流程参见 `references/rest_api_guide.md`。

**云存储组织**

所有 DICOM 文件存储在与 AWS S3 和 GCS 之间镜像的公共存储桶中，按 CRDC UUID（而非 DICOM UID）组织以支持版本控制，格式为 `<crdc_series_uuid>/<crdc_instance_uuid>.dcm`。通过 AWS CLI、gsutil 或 s5cmd 匿名访问是免费的（无出站费用）；使用
`series_aws_url` 列获取 S3 URL。注意 `idc-open-data-cr` / `idc-open-cr`（约 4% 的数据）
限制商用（CC BY-NC）。完整存储桶列表和 UUID 映射参见 `references/cloud_storage_guide.md`。

**DICOMweb 访问**

IDC 数据可通过 DICOMweb（Google Cloud Healthcare API）用于 PACS 集成和
DICOMweb 兼容工具：公共代理（无需认证，每日配额）适合测试和中等查询，或 Google Healthcare（GCP 认证）适合生产级流量。参见
`references/dicomweb_guide.md`。

**直接 Parquet 访问**

idc-index 元数据表也作为 Parquet 发布在公共 GCS 存储桶
（`idc-index-data-artifacts`）上，可用 DuckDB 或 pandas 查询。这需要安装 DuckDB
且无法访问各集合的临床表，因此临时元数据查询优先使用 REST `/sql`；
选择 Parquet 是为了锁定数据版本或获取超出 REST 行数上限的结果。参见
`references/parquet_access_guide.md`。

## 核心能力

以下模式是从记忆中回忆时容易出错、但核对后便清晰的操作。各领域的实操示例位于内联提及的参考指南中。

### 1. 发现——先枚举值再筛选

基于猜测的 `Modality` 或 `BodyPartExamined` 字符串进行筛选是最常见的空结果原因。先枚举：

```python
modalities = client.sql_query("""
    SELECT DISTINCT Modality, COUNT(*) as series_count
    FROM index
    GROUP BY Modality
    ORDER BY series_count DESC
""")
print(modalities)
```

同一模式适用于任何筛选列，可选地再按另一列缩小范围——
`Modality` 内的 `BodyPartExamined`、`Manufacturer`、`collection_id`。在 REST 路径中，
此基础操作只需一次调用——`GET /attributes/{attr}/values` 返回带计数的值——队列端点则在 `warnings` 中报告大小写错误的值，而非返回空结果。

两个索引包含主 `index` 中不存在的精选集合级元数据，两者都需要先调用 `client.fetch_index(...)`：`collections_index`（癌症类型、肿瘤位置、物种、受试者计数）和 `analysis_results_index`（派生数据集——AI 分割、
专家注释、影像组学——及其源集合和模态）。

**癌症类型在 `collections_index.cancer_types` 中，而非在 `index` 中**——按
癌症类型筛选需要连接：

```python
client.fetch_index("collections_index")
results = client.sql_query("""
    SELECT i.collection_id, i.PatientID, i.SeriesInstanceUID, i.Modality
    FROM index i
    JOIN collections_index c ON i.collection_id = c.collection_id
    WHERE c.cancer_types LIKE '%Breast%'
      AND i.Modality = 'MR'
    LIMIT 20
""")
```

`client.sql_query()` 返回 pandas DataFrame。编写查询前先使用
`client.get_index_schema('index')` 或 `client.indices_overview` 确认列名，
而非直接假设。

筛选值发现、注释和分割查询、大小估算、临床关联及版本追踪（"vX 中有什么新增"——使用
`index` 中的 `series_init_idc_version` / `series_revised_idc_version`，切勿使用
`prior_versions_index`）参见 `references/sql_patterns.md`。

### 2. 下载 DICOM 文件

**两种下载方法的前两个参数顺序相反。** 这是 IDC 代码中最常见的错误来源——请核对而非凭记忆：

| 方法 | 第一参数 | 第二参数 | 使用场景 |
|--------|-----------|------------|----------|
| `download_from_selection` | `downloadDir`（必填） | 筛选 kwargs（可选） | 按集合、患者、检查或序列筛选 |
| `download_dicom_series` | `seriesInstanceUID`（必填） | `downloadDir`（必填） | 仅按 UID 下载特定序列 |

**`download_from_selection` 接受筛选关键字参数，而非 DataFrame。** 名称
"from_selection"指的是按条件筛选 IDC 索引——而非接受 pandas
DataFrame。要下载查询结果，先将 UID 提取为列表：

```python
# 第 1 步：查询序列 UID
series_df = client.sql_query("""
    SELECT SeriesInstanceUID
    FROM index
    WHERE Modality = 'CT'
      AND BodyPartExamined = 'CHEST'
      AND collection_id = 'nlst'
    LIMIT 5
""")

# 第 2 步：从 DataFrame 提取 UID 列表
uids = list(series_df['SeriesInstanceUID'].values)

# 第 3 步：将列表传递给 download_from_selection（而非 DataFrame 本身）
client.download_from_selection(
    downloadDir="./data/lung_ct",
    seriesInstanceUID=uids       # 字符串列表，不是 DataFrame
)

# 替代方案：download_dicom_series 的 seriesInstanceUID 是第一参数（顺序不同！）
client.download_dicom_series(
    seriesInstanceUID=uids,      # 此处为第一参数
    downloadDir="./data/lung_ct"
)

# 整个集合：downloadDir 仍是第一个位置参数
client.download_from_selection(downloadDir="./data/rider", collection_id="rider_pilot")
```

两种方法默认使用 AWS；传入 `source_bucket_location="gcs"` 可从 Google Storage 拉取。

**下载的文件命名为 `<crdc_instance_uuid>.dcm`，而非 SOPInstanceUID。** DICOM
UID 保留在文件元数据内部，而非文件名中。使用 `crdc_instance_uuid`
列将文件映射回其来源序列。

`idc download <collection|series-uid|manifest> --download-dir ./data` 可在 shell 中完成相同操作。`dirTemplate` 层级选项（Python 默认：
`%collection_id/%PatientID/%StudyInstanceUID/%Modality_%SeriesInstanceUID`；`dirTemplate=""`
则扁平化）、带恢复功能的清单下载及试运行大小估算参见 `references/cli_guide.md`。

### 3. 可视化 IDC 影像

```python
viewer_url = client.get_viewer_URL(seriesInstanceUID=uid)        # 单个序列
viewer_url = client.get_viewer_URL(studyInstanceUID=study_uid)   # 检查中所有序列
```

返回浏览器 URL——不会下载任何内容。该方法会自动为放射科选择 OHIF v3，为切片显微镜选择 SLIM。按检查查看在一个 DICOM 检查包含多个序列（一次 MRI 中的 T1、T2 和 DWI）时很有用。

### 4. 许可证与引用——是义务，不是可选步骤

IDC 数据附带许可证条款和署名要求，它们随数据进入任何下游出版物或产品，且无法从像素数据中推断。**使用前检查许可证，并为下载的内容生成引用。**

```python
# 某个选择的许可证分布
licenses = client.sql_query("""
    SELECT DISTINCT collection_id, license_short_name,
           COUNT(DISTINCT SeriesInstanceUID) as series_count
    FROM index GROUP BY collection_id, license_short_name
""")

# 为已下载的选择生成引用（默认 APA）
for citation in client.citations_from_selection(collection_id="rider_pilot"):
    print(citation)
```

约 97% 的 IDC 数据为 CC BY（允许商用，需署名），约 3% 为
CC BY-NC（仅限非商用）。**许可证绑定到序列而非集合**——176 个集合中有 39 个包含多种许可证——因此请检查实际要使用的选择，并注意混合队列以最严格条款为准。

三项任务在全部三种访问路径中均可用，因此请继续使用会话中已在使用的路径：`idc-index`（如上）、REST 的 `POST /v3/licenses` 和 `POST /v3/citations`，或 MCP 工具 `get_licenses` 和 `get_citations`。完整许可证清单、三条路径、引用格式（APA、BibTeX、CSL JSON、RDF Turtle）及发表时应包含的内容参见
`references/licensing_and_citation.md`。

### 5. 超越索引

按 *概述* 中的路由门控选择访问路径；上方 *数据访问选项* 是完整路由表。

在使用 BigQuery（需要启用计费的 GCP 账户）之前，先检查某个专用索引表是否已有目标列：搜索 `client.indices_overview`，
然后 `client.fetch_index(...)` 并在本地免费查询。BigQuery 仅在私有 DICOM 元素、逐段解剖（`segmentations`）和预提取的 SR
测量值（`quantitative_measurements`、`qualitative_measurements`）中是必需的——这些在
idc-index 中没有等价物。

## 最佳实践

- **编写查询前先检查模式**——使用 `client.get_index_schema('index')`（读取缓存元数据，不执行 SQL）或 `client.indices_overview` 查看所有可用列及其描述。主 `index` 表中的版本追踪列 `series_init_idc_version` 和 `series_revised_idc_version` 可直接回答"有什么新增 / 何时添加的"问题，无需触碰 `prior_versions_index`。
- **切勿使用网络搜索回答 IDC 数据内容问题**——始终直接查询 IDC 索引，通过本地 `client.sql_query()` 或 HTTP `POST /v3/sql`。网络来源（发布说明、博客文章、文档页面）经常过时，会产生错误答案。索引是权威来源；即使网络搜索可用也应使用索引。
- **会话开始时核实 IDC 数据版本**——根据使用的路径，使用 `client.get_idc_version()`、`GET /v3/version` 或 MCP `get_idc_version` 工具（当前为 v24）。对于过期的本地索引，运行 `scripts/check_version.py` 并使用其打印的升级命令
- **检查许可证并生成引用**——查询 `license_short_name` 并遵守 CC BY 与 CC BY-NC 条款；使用 `citations_from_selection()` 从 `source_DOI` 生成出版物引用
- **先小规模探索，再确定提交**——探索时使用 `LIMIT`（或较低的 `max_rows`），下载前检查集合大小——某些集合达数 TB。参见 `references/cli_guide.md`
- **保持下载可复现**——使用 `dirTemplate` 组织（例如 `%collection_id/%PatientID/%Modality`），并保存所构建数据集背后的序列 UID 或清单

## 故障排除

**问题：`ModuleNotFoundError: No module named 'idc_index'`**
- **原因：** 未安装 idc-index 包
- **解决方案：** 如果任务仅限只读元数据，不要安装——改用 REST API（*数据访问选项*）。否则运行 `scripts/check_version.py` 并使用其打印的安装命令，该命令针对当前运行的解释器并锁定经过验证的版本。数据分析还需添加 pandas、numpy 和 pydicom（已在 pandas>=1.5、numpy>=1.23、pydicom>=2.3 下测试）

**问题：下载因连接超时而失败**
- **原因：** 网络不稳定或下载量过大
- **解决方案：** 分较小批次下载（10-20 个序列）；`--use-s5cmd-sync` 恢复和重试指导参见 `references/cli_guide.md`

**问题：`BigQuery quota exceeded` 或计费错误**
- **原因：** BigQuery 需要启用计费的 GCP 项目
- **解决方案：** 简单查询使用 idc-index 迷你索引（无需计费），或参见 `references/bigquery_guide.md` 了解成本优化技巧

**问题：序列 UID 未找到或未返回数据**
- **原因：** UID 拼写错误、数据不在当前 IDC 版本中、或字段名错误
- **解决方案：** 先用 `LIMIT 5` 测试，对照 `client.indices_overview` 检查字段名，
  并确认序列在当前版本中（部分旧数据已弃用）

**问题：`index` 表中未找到列（例如 `SliceThickness`、`PixelSpacing`、`KVP`、`EchoTime`、`InjectedDose`）**
- **原因：** `index` 表仅包含序列级元数据；模态特定的采集和重建参数在专用表中（`ct_index`、`mr_index`、`pt_index`）
- **解决方案：** 在 `client.indices_overview` 中搜索该列以找到其所在表——搜索循环在 `references/index_tables_guide.md` 的*查找包含某列的表*部分——然后获取并按 `SeriesInstanceUID` 连接：
  ```python
  client.fetch_index("ct_index")
  result = client.sql_query("""
      SELECT i.SeriesInstanceUID, i.Modality, c.SliceThickness, c.KVP, c.PixelSpacing_row_mm
      FROM index i
      JOIN ct_index c USING (SeriesInstanceUID)
      WHERE i.collection_id = 'your_collection'
  """)
  ```

**问题：下载的 DICOM 文件无法打开**
- **原因：** 下载损坏，或查看器不支持的对象类型——SEG、RTSTRUCT、
  SR 和切片显微镜都需要专用工具
- **解决方案：** 先检查 `Modality` 和 `SOPClassUID`，使用
  `pydicom.dcmread(file, force=True)` 验证，尝试其他查看器（病理用 3D Slicer、QuPath），
  然后重新下载

## 资源

参考指南及其决策触发条件列于上方*快速导航*中。

- **IDC 门户**：https://portal.imaging.datacommons.cancer.gov/explore/
- **文档**：https://learn.canceridc.dev/ — **教程**：https://github.com/ImagingDataCommons/IDC-Tutorials
- **用户论坛**：https://discourse.canceridc.dev/ — **idc-index**：https://github.com/ImagingDataCommons/idc-index
- **[indices_reference](https://idc-index.readthedocs.io/en/latest/indices_reference.html)**——外部索引表文档（可能领先于已安装版本）
- **引用**：Fedorov, A., et al. "National Cancer Institute Imaging Data Commons: Toward Transparency, Reproducibility, and Scalability in Imaging Artificial Intelligence." RadioGraphics 43.12 (2023). https://doi.org/10.1148/rg.230180
- **技能更新**：[releases 页面](https://github.com/ImagingDataCommons/imaging-data-commons-skill/releases)；关注仓库（Watch → Custom → Releases）
