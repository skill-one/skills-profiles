---
name: imaging-data-commons
description: 从NCI成像数据公共平台查询并下载公共癌症影像数据。针对任何关于IDC集合、癌症影像数据集、DICOM数据访问、放射科（CT、MR、PET）或病理AI训练集、元数据查询、可视化或许可证检查的问题，均可调用——即使用户未明确提及“IDC”。无需身份验证。
---

# 医学影像数据公共平台

## 概述

从国家癌症研究所医学影像数据公共平台（IDC）查询和下载数据。数据访问无需身份验证。

**预期网络访问：** IDC元数据可通过三种方式访问——随`idc-index` Python包提供的本地DuckDB索引（无需网络），或通过MCP或REST托管的IDC服务（`api.imaging.datacommons.cancer.gov`，无需身份验证）。文件下载使用公共GCS（`storage.googleapis.com`）和AWS S3（`s3.amazonaws.com`）——无需身份验证。DICOMweb访问使用公共IDC代理（`proxy.imaging.datacommons.cancer.gov`，无需认证）或Google Cloud Healthcare API（`healthcare.googleapis.com`，需要GCP身份验证）。可选的BigQuery查询（`bigquery.googleapis.com`）也需要GCP身份验证。此技能不会访问任何凭证或环境变量。

**当前IDC数据版本：v24**（始终验证——参见*最佳实践*）

**首先选择访问路径。** 没有单一的默认选项：最经济且正确的路径取决于会话和任务。

1. **会话中已有IDC MCP服务器？** 路由发现和元数据——参见*IDC MCP服务器*。
2. **否则，已安装`idc-index`？** 运行`python scripts/check_version.py`。如果通过，则对所有操作使用`idc-index`。
3. **未安装，且任务仅读取元数据**——计数、属性值、集合查找、10,000行以下的SQL、许可证、引用、查看器URL？**使用`curl`的REST API；不要安装任何东西。** 安装成本约为77 MB的打包索引数据，以及pandas、pyarrow和duckdb，而元数据问题不需要这些。参见*数据访问选项*。
4. **未安装，且任务需要更多元数据**——下载文件、pandas或绘图、pydicom/SimpleITK、病理瓦片、10,000行以上的结果，或用户重新运行的用户固定版本脚本？安装`idc-index`：`check_version.py`退出非零并打印运行解释器的确切安装命令。优先使用虚拟环境，然后重启Python。

`idc-index`（[GitHub](https://github.com/imagingdatacommons/idc-index)）仍然是功能最强大的路径，并且是唯一移动图像字节的路径；规则只是在使用任务之前不要为此付费。`check_version.py`本身永远不会安装任何东西——当存在时，它还会标记更新的`idc-index`或技能版本。

**`idc-index`路径的设置：**

```python
from idc_index import IDCClient
client = IDCClient()

# 验证IDC数据版本（应为"v24"）
print(f"IDC数据版本: {client.get_idc_version()}")
```

**核心工作流：** 使用`client.sql_query()`查询元数据 → 使用`client.download_from_selection()`下载 → 使用`client.get_viewer_URL()`可视化。下面的Python示例假设此`client`；*数据访问选项*提供了REST等效项。对于当前数据规模，运行`references/sql_patterns.md`中的摘要查询或`GET /v3/stats`。

## IDC MCP服务器

IDC在`https://api.imaging.datacommons.cancer.gov/mcp`运行一个托管的MCP服务器（流式HTTP，无需身份验证）。在其可用时，它补充——而不是取代——以下`idc-index`工作流。

**通过以下方式识别它**：MCP资源`idc://guide`，或通过三个或更多的工具名称`build_cohort`、`get_cohort_urls`、`list_analysis_results`和`get_idc_version`。通用名称（如`run_sql`）本身不能作为证据。如果识别不明确，请使用`idc-index`。

**如果此会话有服务器**，将其视为发现和元数据的权威——IDC版本、计数、属性值、队列构建、元数据SQL——并遵循服务器自己的说明，而不是从此文件重新推导它们。其数据版本是服务器报告的任何内容：调用`get_idc_version`而不是依赖此文件中固定的版本。

返回此处了解服务器未做的事情：下载文件、本地pandas/笔记本分析、DICOMweb、BigQuery、数字病理瓦片和可重复的脚本。通过将服务器中的SeriesInstanceUID传递给`client.download_from_selection(...)`进行交接，并在该点运行`scripts/check_version.py`。

**如果它不可用**，可以使用无需配置的REST API`https://api.imaging.datacommons.cancer.gov/v3`访问相同的相同服务——使用它进行只读元数据，而不是安装`idc-index`，根据*概述*中的路由网关。建议最多连接一次MCP服务器，仅用于重复的交互式发现，并且永远不要自己更改用户的配置。

参见`references/mcp_guide.md`了解工具清单、交接模式以及每个主机的说明。

## 何时使用此技能

- 查找公开的放射学（CT、MR、PET）或病理学（切片显微镜）图像
- 根据癌症类型、模态、解剖部位或其他元数据选择图像子集
- 从IDC下载DICOM数据
- 在研究或商业应用程序中使用前检查数据许可证
- 在浏览器中可视化医学图像，而无需本地DICOM查看器软件

## 快速导航

内联以下内容：MCP/REST路由规则、IDC数据模型、索引表及其如何连接、核心API模式（查询、下载、可视化、许可证、引用）、最佳实践和故障排除。

**参考指南（按需加载）：**

| 指南 | 加载时机 |
|------|----------|
| `index_tables_guide.md` | 复杂的JOIN、模式发现、DataFrame访问 |
| `use_cases.md` | 端到端工作流：训练数据集、批量下载、使用pydicom/SimpleITK的DICOM读取、管道集成 |
| `sql_patterns.md` | 快速SQL模式，用于过滤发现、注释、大小估计 |
| `clinical_data_guide.md` | 临床/表格数据、影像+临床连接、值映射 |
| `licensing_and_citation.md` | 商业使用问题、混合许可证队列、引用格式 |
| `cloud_storage_guide.md` | 直接S3/GCS访问、版本控制、UUID映射 |
| `dicomweb_guide.md` | DICOMweb端点、PACS集成 |
| `digital_pathology_guide.md` | 滑片显微镜（SM）、注释（ANN）、病理工作流 |
| `bigquery_guide.md` | 完整DICOM元数据、私有元素（需要GCP） |
| `cli_guide.md` | 命令行工具（`idc download`、清单文件） |
| `parquet_access_guide.md` | 通过GCS直接Parquet查询（无需安装idc-index） |
| `mcp_guide.md` | 托管的IDC MCP服务器：工具清单、识别、交接到`idc-index` |
| `rest_api_guide.md` | 托管的IDC REST API：端点、过滤语法、HTTP上的SQL、清单 |

## IDC数据模型

IDC在标准DICOM层次结构（患者→研究→系列→实例）之上添加了两个分组级别：

- **collection_id**：按疾病、模态或研究重点对患者进行分组（例如，`tcga_luad`、`nlst`）。患者恰好属于一个集合。
- **analysis_result_id**：标识跨一个或多个原始集合派生的对象（分割、注释、影像组学特征）。使用它来查找AI生成的或专家注释，而`collection_id`查找原始影像数据（这可能本身包括已存档的注释）。

**查询的关键标识符：**
| 标识符 | 范围 | 用于 |
|--------|------|------|
| `collection_id` | 数据集分组 | 按项目/研究过滤 |
| `PatientID` | 患者 | 按患者分组图像 |
| `StudyInstanceUID` | DICOM研究 | 分组的系列、可视化 |
| `SeriesInstanceUID` | DICOM系列 | 分组的系列、可视化 |

## 索引表

`idc-index`包提供多个元数据索引表，可通过SQL或作为pandas DataFrame访问。REST API通过`GET /tables`和`POST /sql`公开相同的表。

**重要提示：** `client.indices_overview`是当前表描述、可用列及其类型的权威来源——在编写SQL或探索数据结构时查询它。它还回答“哪个表包含列X”；参见`references/index_tables_guide.md`以获取该搜索模式和完整模式发现。

### 可用表

在查询任何索引表之前，始终调用`client.fetch_index("table_name")`——对所有表都是安全的，包括在启动时自动加载的表。

| 系列 | 表 | 粒度 |
|------|------|------|
| 核心 | `index`（所有当前数据的初级元数据）、`collections_index`、`analysis_results_index` | 系列/集合/分析结果 |
| 模态采集参数 | `ct_index`、`mr_index`、`pt_index`、`contrast_index` | 1行=1个该模态的系列 |
| 派生对象 | `seg_index`、`rtstruct_index`、`ann_index`、`ann_group_index` | 1行=1个系列（或注释组） |
| 显微镜 | `sm_index`、`sm_instance_index` | 1行=1个SM系列/实例 |
| 几何、临床、历史 | `volume_geometry_index`、`clinical_index`、`version_metadata_index`、`prior_versions_index` | 参见指南 |

`references/index_tables_guide.md`提供了每个表的完整清单，包括其列和内容——当您需要知道特殊表实际包含什么时，加载它。

**`prior_versions_index`仅用于可重复性。** 它包含永久从IDC中移除的系列，与`index`完全重叠。仅用于对先前的IDC版本进行可重复性工作。**不要**使用它进行版本历史或“有什么新内容”的问题——这些使用`series_init_idc_version` / `series_revised_idc_version`在主`index`表中，它们不等于此表的`min_idc_version` / `max_idc_version`。

### 连接表

**`SeriesInstanceUID`是所有系列级特殊表的通用连接键**：`sm_index`、`sm_instance_index`、`seg_index`、`ann_index`、`ann_group_index`、`contrast_index`、`volume_geometry_index`、`rtstruct_index`、`ct_index`、`mr_index`、`pt_index`。始终在`SeriesInstanceUID`上连接这些表到`index`。以下是例外情况，它们使用不同的列名。

| 连接列 | 表 | 用例 |
|--------|------|------|
| `collection_id` | index、prior_versions_index、collections_index、clinical_index | 将系列链接到集合元数据或临床数据 |
| `analysis_result_id` | index、analysis_results_index | 将系列链接到分析结果元数据（注释、分割） |
| `source_DOI` | index、analysis_results_index | 通过出版DOI链接 |
| `segmented_SeriesInstanceUID` | seg_index → index | 将分割链接到其源图像系列（`seg_index.segmented_SeriesInstanceUID = index.SeriesInstanceUID`） |
| `referenced_SeriesInstanceUID` | ann_index → index、rtstruct_index → index | 将注释或RTSTRUCT链接到其源图像系列 |

**注意：** `subjects`、`updated`和`description`出现在多个表中，但含义不同（计数与标识符、不同的更新上下文）。连接`prior_versions_index`到`index`在`SeriesInstanceUID`上始终返回零行——参见上面的警告。

有关详细连接示例、模式发现模式、关键列参考和DataFrame访问，请参阅`references/index_tables_guide.md`。

### 临床数据访问

临床（非影像）属性——分期、人口统计学、治疗——存在于每个集合的表中。`client.fetch_index("clinical_index")`加载将列映射到集合的字典；`client.get_clinical_table(name)`返回一个DataFrame作为表。

参见`references/clinical_data_guide.md`以获取发现工作流、编码值映射以及将临床数据与影像连接。

## 数据访问选项

| 方法 | 身份验证 | 最适合 | 参考 |
|------|----------|----------|------|
| `idc-index` | 无 | 下载、pandas分析、无限制查询——最强大的路径 | 本文档 |
| IDC MCP服务器 | 无 | 发现、队列构建、会话已有服务器时的元数据 | `mcp_guide.md` |
| IDC REST API | 无 | 无需安装的元数据，任何语言或shell均可——当`idc-index`不存在时的默认选项 | `rest_api_guide.md` |
| 直接Parquet（GCS） | 无 | 固定版本的查询，或结果超过REST行限制 | `parquet_access_guide.md` |
| 云存储（S3/GCS） | 无 | 直接文件访问、批量传输、自定义管道 | `cloud_storage_guide.md` |
| DICOMweb通过IDC代理 | 无 | 工具和PACS集成；每日配额，因此测试和适度使用 | `dicomweb_guide.md` |
| DICOMweb通过Google Healthcare | 是（GCP） | 相同的DICOMweb API在生产容量下，无需代理配额 | `dicomweb_guide.md` |
| SlicerIDCBrowser | 无 | 在3D Slicer中进行3D可视化和分析 | https://github.com/ImagingDataCommons/SlicerIDCBrowser |
| BigQuery | 是（GCP） | 完整DICOM元数据、私有元素、SR测量——最后的选择 | `bigquery_guide.md` |

**IDC门户（https://portal.imaging.datacommons.cancer.gov/）仅支持交互**——基于浏览器的探索、手动队列选择和下载。与上面所有选项不同，它没有程序化接口，因此将用户引导浏览或自行点击数据；永远不要将其用作脚本或工作流中的一步。

**REST API——无需安装的元数据路径**

`https://api.imaging.datacommons.cancer.gov/v3`，无需身份验证：发现、队列计数和清单、只读SQL、临床表、查看器URL、许可证、引用。它是MCP服务器通过纯HTTP提供的相同服务，因此无需配置。它永远不会移动图像字节——切换到`idc-index`以下载、获取DataFrame或用于超过10,000行的结果。

```bash
B=https://api.imaging.datacommons.cancer.gov/v3
curl -s $B/version   # idc_version, idc_index_data_version, api_version
curl -s $B/stats     # collections, patients, studies, series, instances, size_TB
curl -s "$B/attributes/Modality/values?limit=5"   # 真实过滤值，带计数
curl -s $B/sql -H 'content-type: application/json' \
  -d '{"sql":"SELECT collection_id, COUNT(*) n FROM index GROUP BY 1 ORDER BY n DESC LIMIT 3"}'
curl -s $B/cohort/counts -H 'content-type: application/json' \
  -d '{"filters":{"terms":{"collection_id":["rider_pilot"]}}}'
```

**过滤对象始终位于`filters`下**——在`cohort/counts`、`cohort/manifest`、`cohort/manifest.txt`、`licenses`和`citations`中一样。裸过滤或未识别的键会导致422命名修复；未过滤的系列枚举请求是400，而不是整个存档。每个过滤响应都会回显`filters_applied`和`warnings`——请阅读它们，因为它们命名服务器丢弃的任何谓词。零计数与空的`warnings`因此意味着过滤器匹配了 nothing，而不是值拼写错误；拼写错误会产生一个警告，说明这一点。

`POST /sql`接受一个只读的`SELECT`/`WITH`，跨越`idc-index`公开的表加上`clinical.<table>`；`max_rows`默认为5,000，上限为10,000，`truncated`标志剪切。`GET /attributes`列出了19个可过滤的属性——临床值、分割解剖学和采集参数都不在其中，需要SQL。没有速率限制或配额。**仅使用v3**：V1和V2已被取代，并计划停用，因此请将用户带来的任何`/v1/`-或`Modality_btw`-风格示例迁移，而不是扩展它。

双方都基于`idc-index-data`，因此在混合它们之前比较API的`idc_index_data_version`与本地`idc_index_data.__version__`——**主版本是IDC数据发布**（`24.x.y`服务`v24`），因此次要/补丁版本不同意味着系列是相同的。如果API比整个发布提前，`idc-index`**无法下载额外的系列**——它默默地跳过其自己的索引未列出的内容——因此要么升级它（运行`scripts/check_version.py`以获取正确的命令），要么直接从桶中传输，使用`s5cmd --no-sign-request`。

参见`references/rest_api_guide.md`以获取端点参考、过滤基础、限制和基于清单的下载流程。

**云存储组织**

所有 DICOM 文件都存储在 AWS S3 和 GCS 之间的镜像公共存储桶中，按 CRDC UUID（非 DICOM UID）组织以支持版本控制，格式为 `<crdc_series_uuid>/<crdc_instance_uuid>.dcm`。通过 AWS CLI、gsutil 或 s5cmd 以匿名访问方式免费访问（无出网费用）；使用 `series_aws_url` 列获取 S3 URL。请注意，`idc-open-data-cr` / `idc-open-cr`（约 4% 的数据）受商业使用限制（CC BY-NC）。有关完整存储桶列表和 UUID 映射，请参阅 `references/cloud_storage_guide.md`。

**DICOMweb 访问**

IDC 数据可通过 DICOMweb（Google Cloud Healthcare API）用于 PACS 集成和 DICOMweb 兼容工具：一个公共代理（无需认证，每日配额）用于测试和适度查询，或 Google Healthcare（GCP 认证）用于生产量级。有关详细信息，请参阅 `references/dicomweb_guide.md`。

**直接 Parquet 访问**

idc-index 元数据表也作为 Parquet 发布在公共 GCS 存储桶上（`idc-index-data-artifacts`），可使用 DuckDB 或 pandas 进行查询。这需要安装 DuckDB，且无法访问每个集合的临床表，因此建议使用 REST `/sql` 进行临时元数据查询；选择 Parquet 以固定数据版本或用于超出 REST 行限制的结果。有关详细信息，请参阅 `references/parquet_access_guide.md`。

## 核心功能

以下模式是在从记忆中调取时容易出错而不是进行检查的模式。每个领域的示例代码位于内联命名的参考指南中。

### 1. 发现 — 在过滤之前枚举值

基于猜测的 `Modality` 或 `BodyPartExamined` 字符串进行过滤是导致空结果集的最常见原因。应先枚举：

```python
modalities = client.sql_query("""
    SELECT DISTINCT Modality, COUNT(*) as series_count
    FROM index
    GROUP BY Modality
    ORDER BY series_count DESC
""")
print(modalities)
```

相同的模式适用于任何过滤列，并可选择按其他列进一步缩小范围——`BodyPartExamined` 在 `Modality`、`Manufacturer`、`collection_id` 内。在 REST 路径上，这种基础是一个单独的调用——`GET /attributes/{attr}/values` 返回带计数的值——并且队列端点在 `warnings` 中报告大小写错误的值，而不是作为空结果。

两个索引包含 curated 集合级元数据，而主 `index` 不包含，两者都需要先使用 `client.fetch_index(...)`：`collections_index`（癌症类型、肿瘤位置、物种、受试者计数）和 `analysis_results_index`（衍生数据集——AI 段落、专家注释、影像组学——及其来源集合和模态）。

**癌症类型位于 `collections_index.cancer_types`，而不是在 `index` 中**——按癌症类型过滤需要连接：

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

`client.sql_query()` 返回一个 pandas DataFrame。在编写查询之前，使用 `client.get_index_schema('index')` 或 `client.indices_overview` 确认列名，而不是假设它们。

有关过滤值发现、注释和分段查询、大小估计、临床链接和版本跟踪（“vX 中新增了什么”——在 `index` 中使用 `series_init_idc_version` / `series_revised_idc_version`，而不是 `prior_versions_index`）的详细信息，请参阅 `references/sql_patterns.md`。

### 2. 下载 DICOM 文件

**两种下载方法的前两个参数顺序相反。** 这是 IDC 代码中最常见的错误来源——检查它而不是回忆它：

| 方法 | 第一个参数 | 第二个参数 | 使用场景 |
|------|-----------|------------|----------|
| `download_from_selection` | `downloadDir`（必需） | 过滤关键字参数（可选） | 按集合、患者、研究或系列过滤 |
| `download_dicom_series` | `seriesInstanceUID`（必需） | `downloadDir`（必需） | 仅通过 UID 下载特定系列 |

**`download_from_selection` 使用过滤关键字参数，而不是 DataFrame。** “from_selection” 的名称是指通过标准过滤 IDC 索引，而不是接受 pandas DataFrame。要下载查询结果，请先提取 UID 到列表中：

```python
# 第一步：查询系列 UID
series_df = client.sql_query("""
    SELECT SeriesInstanceUID
    FROM index
    WHERE Modality = 'CT'
      AND BodyPartExamined = 'CHEST'
      AND collection_id = 'nlst'
    LIMIT 5
""")

# 第二步：从 DataFrame 中提取 UID 为列表
uids = list(series_df['SeriesInstanceUID'].values)

# 第三步：将列表传递给 download_from_selection（不是 DataFrame 本身）
client.download_from_selection(
    downloadDir="./data/lung_ct",
    seriesInstanceUID=uids       # 字符串列表，而不是 DataFrame
)

# 替代方案：download_dicom_series 将 seriesInstanceUID 作为第一个参数（顺序不同！）
client.download_dicom_series(
    seriesInstanceUID=uids,      # 这里是第一个参数
    downloadDir="./data/lung_ct"
)

# 整个集合：downloadDir 仍然是第一个位置参数
client.download_from_selection(downloadDir="./data/rider", collection_id="rider_pilot")
```

两种方法默认为 AWS；传递 `source_bucket_location="gcs"` 可从 Google Storage 拉取。

**下载的文件命名为 `<crdc_instance_uuid>.dcm`，而不是 SOPInstanceUID。** DICOM UID 保留在文件元数据中，而不是文件名中。使用 `crdc_instance_uuid` 列将文件映射回其来源系列。

`idc download <collection|series-uid|manifest> --download-dir ./data` 从 Shell 执行相同的操作。有关 `dirTemplate` 层次结构选项（Python 默认：`%collection_id/%PatientID/%StudyInstanceUID/%Modality_%SeriesInstanceUID`；`dirTemplate=""` 扁平化）、使用清单下载和恢复以及预运行大小估计，请参阅 `references/cli_guide.md`。

### 3. 可视化 IDC 图像

```python
viewer_url = client.get_viewer_URL(seriesInstanceUID=uid)        # 一个系列
viewer_url = client.get_viewer_URL(studyInstanceUID=study_uid)   # 一个研究中的所有系列
```

返回一个浏览器 URL——不会下载任何内容。该方法会自动选择 OHIF v3 用于放射学或 SLIM 用于显微镜切片。当单个 DICOM 研究包含多个系列（T1、T2 和一个 MRI 会话的 DWI）时，按研究查看很有用。

### 4. 许可证和引用 — 义务，非可选步骤

IDC 数据包含许可证条款和归属要求，这些条款会随其进入任何下游出版物或产品，并且无法从像素数据中推断。**使用前检查许可证，并为下载的内容生成引用。**

```python
# 某个选择的许可证分解
licenses = client.sql_query("""
    SELECT DISTINCT collection_id, license_short_name,
           COUNT(DISTINCT SeriesInstanceUID) as series_count
    FROM index GROUP BY collection_id, license_short_name
""")

# 相同选择的引用（默认为 APA）
for citation in client.citations_from_selection(collection_id="rider_pilot"):
    print(citation)
```

约 97% 的 IDC 数据为 CC BY（允许署名后的商业使用）和约 3% 为 CC BY-NC（仅限非商业使用）。**许可证附加到系列，而不是集合**——176 个集合中有 39 个包含多个许可证——因此请检查您实际打算使用的选择，并注意最严格的条款适用于混合队列。

这两项任务都可通过三种访问路径完成，因此请保持在会话已使用的路径上：上述 `idc-index`、REST 上的 `POST /v3/licenses` 和 `POST /v3/citations`，或 `get_licenses` 和 `get_citations` MCP 工具。有关完整许可证清单、所有三种路径、引用格式（APA、BibTeX、CSL JSON、RDF Turtle）以及发布时应包含的内容，请参阅 `references/licensing_and_citation.md`。

### 5. 超越索引

在“概述”中选择带路由网关的访问路径；上面的“数据访问选项”是完整路由表。

在转向 BigQuery（需要启用计费的 GCP 账户）之前，请检查是否已有专用索引表包含您想要的列：搜索 `client.indices_overview`，然后使用 `client.fetch_index(...)` 本地查询（免费）。BigQuery 仅用于私有 DICOM 元素、按段解剖（`segmentations`）和预提取 SR 测量（`quantitative_measurements`、`qualitative_measurements`）——这些没有 `idc-index` 对应项。

## 最佳实践

- **在编写查询前检查模式** — 使用 `client.get_index_schema('index')`（读取缓存元数据，不执行 SQL）或 `client.indices_overview` 查看所有可用列及其描述。主 `index` 表中的版本跟踪列 `series_init_idc_version` 和 `series_revised_idc_version` 直接回答“新增了什么/何时添加”的问题，无需触及 `prior_versions_index`。
- **切勿使用网络搜索 IDC 数据内容问题** — 始终直接查询 IDC 索引，通过本地 `client.sql_query()` 或 HTTP 上的 `POST /v3/sql`。网络来源（发布说明、博客文章、文档页面）经常过时，并将产生错误答案。索引是权威来源；即使网络搜索可用时也使用它。
- **在会话开始时验证 IDC 数据版本** - `client.get_idc_version()`、`GET /v3/version` 或 MCP 的 `get_idc_version` 工具，取决于当前路径（目前为 v24）。对于过时的本地索引，运行 `scripts/check_version.py` 并使用其打印的升级命令。
- **检查许可证并生成引用** - 查询 `license_short_name` 并尊重 CC BY vs CC BY-NC 条款；使用 `citations_from_selection()` 从 `source_DOI` 生成引用用于出版物。
- **从小处探索，然后提交** - 使用 `LIMIT`（或低 `max_rows`）进行探索，并在下载前检查集合大小——某些集合有 TB 级大小。有关详细信息，请参阅 `references/cli_guide.md`。
- **保持下载可重复** - 使用 `dirTemplate`（例如 `%collection_id/%PatientID/%Modality`）组织，并保存您构建的任何数据集背后的系列 UID 或清单

## 故障排除

**问题：`ModuleNotFoundError: No module named 'idc_index'`**
- **原因**：idc-index 包未安装
- **解决方案**：如果任务仅是只读元数据，则不要安装它——改用 REST API（上面的“数据访问选项”）。否则运行 `scripts/check_version.py` 并使用其打印的安装命令，该命令针对正在运行的解释器并固定了经过审核的版本。对于数据分析，还需添加 pandas、numpy 和 pydicom（测试版本为 pandas>=1.5, numpy>=1.23, pydicom>=2.3）

**问题：下载失败，连接超时**
- **原因**：网络不稳定或下载文件过大
- **解决方案**：分批下载（10-20 个系列）；有关 `--use-s5cmd-sync` 恢复和重试指导，请参阅 `references/cli_guide.md`

**问题：`BigQuery quota exceeded` 或计费错误**
- **原因**：BigQuery 需要启用计费的 GCP 项目
- **解决方案**：使用 idc-index mini-index 进行简单查询（无需计费），或参阅 `references/bigquery_guide.md` 获取成本优化建议

**问题：系列 UID 未找到或未返回数据**
- **原因**：UID 拼写错误、当前 IDC 版本中无数据或字段名错误
- **解决方案**：首先使用 `LIMIT 5` 测试，检查字段名与 `client.indices_overview` 匹配，并确认系列在当前版本中（某些旧数据已弃用）

**问题：`index` 表中列未找到（例如，`SliceThickness`、`PixelSpacing`、`KVP`、`EchoTime`、`InjectedDose`）**
- **原因**：`index` 表仅包含系列级元数据；模态特定的采集和重建参数存储在专用表（`ct_index`、`mr_index`、`pt_index`）
- **解决方案**：在 `client.indices_overview` 中搜索列以找到其表——循环位于 `references/index_tables_guide.md` 中 *找到包含列的表* 下——然后使用 `SeriesInstanceUID` 进行获取和连接：
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
- **原因**：下载损坏，或对象类型查看器无法处理——SEG、RTSTRUCT、SR 和显微镜切片都需要专用工具
- **解决方案**：首先检查 `Modality` 和 `SOPClassUID`，使用 `pydicom.dcmread(file, force=True)` 验证，尝试另一个查看器（3D Slicer、QuPath 用于病理学），然后重新下载

## 资源

参考指南及其决策触发器在上述“快速导航”中列出。

- **IDC Portal**：https://portal.imaging.datacommons.cancer.gov/explore/
- **文档**：https://learn.canceridc.dev/ — **教程**：https://github.com/ImagingDataCommons/IDC-Tutorials
- **用户论坛**：https://discourse.canceridc.dev/ — **idc-index**：https://github.com/ImagingDataCommons/idc-index
- **[indices_reference](https://idc-index.readthedocs.io/en/latest/indices_reference.html)** — 外部索引表文档（可能领先于安装版本）
- **引用**：Fedorov, A., 等。“国家癌症研究所影像数据公共库：迈向影像人工智能的透明度、可重复性和可扩展性。” RadioGraphics 43.12 (2023)。https://doi.org/10.1148/rg.230180
- **技能更新**：[发布页面](https://github.com/ImagingDataCommons/imaging-data-commons-skill/releases)；关注存储库（Watch → Custom → Releases）
