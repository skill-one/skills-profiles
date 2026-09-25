# bioRxiv和medRxiv文献检索

## 前置条件

1.  **`uv`**: 阅读`uv`技能并按照其设置说明进行操作，确保`uv`已安装并在PATH路径中。
2.  **用户通知**: 如果工作区根目录中不存在`.licenses/literature_search_biorxiv_LICENSE.txt`文件，则 (1) 需要显著通知用户检查https://api.biorxiv.org/和https://www.biorxiv.org/content/about-biorxiv上的条款，并始终检查该技能检索的论文的许可证以了解任何限制，然后 (2) 创建记录通知文本和时间戳的文件。

## 搜索策略指南（首先阅读）

**此技能浏览基于日期的预印本存档。它不是一个关键词搜索引擎。** 根据您已有的信息选择您的搜索方法：

-   **DOI**（例如，来自引文）：使用`search_by_doi.py`。快速且可靠。
-   **近似日期 + 类别**: 使用`search_by_dates.py`并设置1-4周的日期范围以及`--category`。
-   **仅主题或关键词，无日期**: **不要使用此技能进行发现。** 首先使用一个关键词文献技能找到相关的DOI，然后返回这里获取元数据。

> **关键反模式 — 请勿这样做**：不要尝试使用`--keywords`搜索宽泛的日期范围（月份或年份）以期望找到特定论文。bioRxiv API不支持服务器端关键词搜索。脚本必须下载整个日期范围的全部元数据，并在Python中本地过滤。宽泛的范围会导致数千个API调用、超时，并且您的请求可能会因API滥用而被阻止。这是此技能失败的首要原因。

## 核心规则

-   **使用包装器**: 始终使用提供的辅助脚本来查询数据库，而不是直接访问数据库。脚本会自动优雅地执行所需的速率限制。
-   **本地过滤（关键警告）**: 与arXiv不同，bioRxiv API **不支持服务器端关键词或作者搜索**。关键词和作者过滤是在下载指定日期范围的全部元数据后由脚本在本地执行的。您**必须**在使用`--keywords`或`--author`时使用狭窄的日期范围（例如，1-4周）并结合`--category`过滤器。
-   **默认情况下排除摘要**: 为了在生成的JSON中节省上下文空间，摘要默认情况下会被从输出中剥离。如果您正在使用`--keywords`搜索，并且想要阅读结果的论文摘要以了解其上下文，您**必须**传递`--include_abstracts`标志。
-   **输出重定向**: 搜索命令将JSON数组输出到标准输出。始终将输出重定向到文件（例如，`> results.json`），并单独解析该文件。
-   **列出来源** 如果使用此技能，请确保在输出中提及这一点，并列出所有用于生成输出的论文的URL。

## 实用脚本

所有工具都执行跨进程速率限制，并在失败时进行退避重试。为确保您遵守服务条款，请勿编写自定义`curl`查询。

**分页**: bioRxiv API以最多100篇论文的页面返回结果。`search_by_dates.py`脚本会自动获取所有页面并向stderr报告分页进度（例如，`[第2页] 已获取200/543篇论文...`）。stdout的JSON输出包含跨所有页面的**完整**过滤结果集 — 无需手动分页。

### 1. 按日期搜索 (`search_by_dates.py`)

在显式日期范围内搜索预印本，可选择按类别、关键词或作者进行过滤。

```bash
# 在2周内进行宽泛类别搜索
uv run scripts/search_by_dates.py --server biorxiv \
  --start_date 2024-01-01 --end_date 2024-01-14 \
  --category neuroscience > results.json

# 使用OR逻辑进行深度关键词过滤并包含摘要
uv run scripts/search_by_dates.py --server medrxiv \
  --start_date 2023-11-01 --end_date 2023-11-30 \
  --category infectious_diseases \
  --keywords "covid" "sars-cov-2" --match_logic OR \
  --include_abstracts > covid_papers.json

# 在狭窄窗口中查找特定作者的论文
uv run scripts/search_by_dates.py \
  --start_date 2024-05-01 --end_date 2024-05-14 \
  --author "Smith" > smith_papers.json
```

*必需参数:*

-   `--start_date`: YYYY-MM-DD
-   `--end_date`: YYYY-MM-DD

*可选参数:*

-   `--server`: `biorxiv`（默认）或`medrxiv`
-   `--category`: 一个有效的主题类别（见下文）。**强烈推荐** — 大幅减少脚本必须下载和过滤的数据。
-   `--keywords`: 在标题/摘要中搜索的字符串列表。
-   `--match_logic`: `AND`（默认）或`OR`用于关键词。
-   `--author`: 作者姓名（不区分大小写的字符串匹配）。
-   `--include_abstracts`: 标志，用于在JSON输出中包含完整摘要。

### 2. 按DOI获取元数据 (`search_by_doi.py`)

如果您知道DOI，则检索单个论文的详细JSON元数据。**这是最可靠的入口点。**

```bash
uv run scripts/search_by_doi.py --server biorxiv \
  --doi "10.1101/2023.08.15.551388" \
  --include_abstracts > paper_info.json
```

### 下载全文PDF

> **此技能不支持PDF下载。** 要下载bioRxiv或medRxiv预印本的全文PDF，请使用**`literature-search-europepmc`**技能。首先，使用论文的DOI通过EuropePMC查找其PMCID，然后使用EuropePMC的PDF检索下载文档。

## 有效的主题类别

您可以将这些传递给`search_by_dates.py`中的`--category`标志。脚本会严格验证它们。

### bioRxiv类别:

`animal_behavior_and_cognition`, `biochemistry`, `bioengineering`,
`bioinformatics`, `biophysics`, `cancer_biology`, `cell_biology`,
`clinical_trials`, `developmental_biology`, `ecology`, `epidemiology`,
`evolutionary_biology`, `genetics`, `genomics`, `immunology`, `microbiology`,
`molecular_biology`, `neuroscience`, `paleontology`, `pathology`,
`pharmacology_and_toxicology`, `physiology`, `plant_biology`,
`scientific_communication_and_education`, `synthetic_biology`,
`systems_biology`, `zoology`

### medRxiv类别:

`addiction_medicine`, `allergy_and_immunology`, `anesthesia`,
`cardiovascular_medicine`, `dentistry_and_oral_medicine`, `dermatology`,
`emergency_medicine`, `endocrinology`, `epidemiology`, `forensic_medicine`,
`gastroenterology`, `genetic_and_genomic_medicine`, `health_informatics`,
`health_economics_and_outcomes_research`, `health_policy`,
`health_systems_and_quality_improvement`, `hematology`, `hiv_aids`,
`infectious_diseases`, `intensive_care_and_critical_care_medicine`,
`medical_education`, `medical_ethics`, `nephrology`, `neurology`, `nursing`,
`nutrition`, `obstetrics_and_gynecology`,
`occupational_and_environmental_health`, `oncology`, `ophthalmology`,
`orthopedics`, `otolaryngology`, `pain_medicine`, `palliative_care`,
`pathology`, `pediatrics`, `pharmacology_and_therapeutics`,
`primary_care_research`, `psychiatry_and_clinical_psychology`,
`public_and_global_health`, `radiology_and_imaging`,
`rehabilitation_medicine_and_physical_therapy`, `respiratory_medicine`,
`rheumatology`, `sexual_and_reproductive_health`, `sports_medicine`, `surgery`,
`toxicology`, `transplantation`, `urology`
