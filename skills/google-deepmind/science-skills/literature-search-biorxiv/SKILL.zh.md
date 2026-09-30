---
name: literature-search-biorxiv
description: 浏览、筛选和下载bioRxiv和medRxiv上的生命科学、生物学和医学预印本。支持通过DOI获取论文元数据，并支持按日期范围、类别和关键词进行筛选。关键词筛选是本地的，因此日期范围必须狭窄（1-4周），并结合类别以防止超时。
---

# bioRxiv 和 medRxiv 文献检索

## 前置条件

1.  **`uv`**：阅读 `uv` 技能文档，并按照其安装说明进行操作，以确保
    `uv` 已安装并包含在 PATH 中。
2.  **用户通知**：如果工作区根目录中尚不存在 .licenses/literature_search_biorxiv_LICENSE.txt，则 (1) 显著
    提醒用户查看 https://api.biorxiv.org/ 和
    https://www.biorxiv.org/content/about-biorxiv 上的条款，并始终检查该技能检索到的论文的许可证是否存在任何限制，然后 (2)
    创建该文件以记录通知文本和时间戳。

## 搜索策略指南（首先阅读）

**此技能浏览基于日期的预印本存档。它不是关键词搜索
引擎。** 根据你已知的信息选择方法：

-   **DOI**（例如来自引用）：使用 `search_by_doi.py`。快速且
    可靠。
-   **大致日期 + 类别**：使用 `search_by_dates.py`，指定 1–4 周的
    范围并使用 `--category`。
-   **仅有主题或关键词，无日期**：**不要使用此技能进行
    发现。** 首先使用支持关键词的文献检索技能以找到相关的
    DOI，然后返回此处获取元数据。

> **关键反模式 — 切勿这样做：** 不要尝试使用 `--keywords` 搜索宽泛的
> 日期范围（数月或数年）以期望找到特定的
> 论文。bioRxiv API 不支持服务器端关键词搜索。该脚本
> 必须下载整个日期范围的所有元数据，并在 Python 中进行本地过滤。宽泛的范围会导致数千次 API 调用、超时，并且你的
> 请求可能因滥用 API 而被阻止。这是此技能失败的首要原因。

## 核心规则

-   **使用封装器**：始终执行提供的辅助脚本来查询
    数据库，而不是直接访问数据库。这些脚本
    会自动优雅地强制执行所需的速率限制。
-   **本地过滤（关键警告）**：与 arXiv 不同，bioRxiv API **不
    支持服务器端关键词或作者搜索**。关键词和作者
    过滤在脚本下载指定日期范围内的所有
    元数据后在*本地*执行。当你使用
    `--keywords` 或 `--author` 进行搜索时，**必须**使用狭窄的日期范围
    （例如 1-4 周）并且使用 `--category` 过滤器。
-   **默认排除摘要**：为了节省结果 JSON 中的上下文空间，默认情况下会从输出中移除摘要。如果你正在
    通过 `--keywords` 搜索，并希望阅读所得论文的摘要以了解其背景，你**必须**传递
    `--include_abstracts` 标志。
-   **输出重定向**：搜索命令将 JSON 数组输出到标准输出。始终将输出重定向到文件（例如 `> results.json`）并单独解析该文件。
-   **列出来源** 如果使用了此技能，确保在输出中提到这一点，并列出在产生输出过程中使用的
    所有论文的 URL。

## 实用脚本

所有工具都强制实施跨进程速率限制，并在失败时进行带退避的重试。
为了确保你尊重服务条款，不要编写自定义的 `curl` 查询。

**分页：** bioRxiv API 以每页最多 100 篇论文的形式返回结果。
`search_by_dates.py` 脚本自动获取所有页面并向 stderr 报告
分页进度（例如，`[Page 2] Fetched 200/543 papers...`）。输出到 stdout 的 JSON
包含跨所有页面的**完整**过滤结果集——
无需手动分页。

### 1. 按日期搜索 (`search_by_dates.py`)

在明确的日期范围内搜索预印本，可选按类别、
关键词或作者进行过滤。

```bash
# 在 2 周内进行宽泛的类别搜索
uv run scripts/search_by_dates.py --server biorxiv \
  --start_date 2024-01-01 --end_date 2024-01-14 \
  --category neuroscience > results.json

# 使用 OR 逻辑进行深度关键词过滤并包含摘要
uv run scripts/search_by_dates.py --server medrxiv \
  --start_date 2023-11-01 --end_date 2023-11-30 \
  --category infectious_diseases \
  --keywords "covid" "sars-cov-2" --match_logic OR \
  --include_abstracts > covid_papers.json

# 在狭窄的时间窗口内按特定作者查找论文
uv run scripts/search_by_dates.py \
  --start_date 2024-05-01 --end_date 2024-05-14 \
  --author "Smith" > smith_papers.json
```

*必填参数：*

-   `--start_date`：YYYY-MM-DD
-   `--end_date`：YYYY-MM-DD

*可选参数：*

-   `--server`：`biorxiv`（默认）或 `medrxiv`
-   `--category`：有效的主题类别（见下文）。**强烈建议**使用 —
    显著减少脚本需要下载和过滤的数据量。
-   `--keywords`：要在标题/摘要中搜索的字符串列表。
-   `--match_logic`：用于关键词的 `AND`（默认）或 `OR`。
-   `--author`：作者姓名（大小写不敏感的字符串匹配）。
-   `--include_abstracts`：标志，用于在 JSON 输出中包含完整摘要。

### 2. 按 DOI 获取元数据 (`search_by_doi.py`)

如果你已经知道某篇论文的
DOI，可以检索该单篇论文的详细 JSON 元数据。**这是最可靠的入口点。**

```bash
uv run scripts/search_by_doi.py --server biorxiv \
  --doi "10.1101/2023.08.15.551388" \
  --include_abstracts > paper_info.json
```

### 下载全文 PDF

> **此技能不支持 PDF 下载。** 要下载 bioRxiv 或 medRxiv 预印本的全文 PDF，请使用 **`literature-search-europepmc`**
> 技能。首先，使用论文的 DOI 通过 EuropePMC 查找其 PMCID，然后使用
> EuropePMC 的 PDF 检索功能下载文档。

## 有效的主题类别

你可以将这些传递给 `search_by_dates.py` 中的 `--category` 标志。该脚本将严格验证它们。

### bioRxiv 类别：

`animal_behavior_and_cognition`, `biochemistry`, `bioengineering`,
`bioinformatics`, `biophysics`, `cancer_biology`, `cell_biology`,
`clinical_trials`, `developmental_biology`, `ecology`, `epidemiology`,
`evolutionary_biology`, `genetics`, `genomics`, `immunology`, `microbiology`,
`molecular_biology`, `neuroscience`, `paleontology`, `pathology`,
`pharmacology_and_toxicology`, `physiology`, `plant_biology`,
`scientific_communication_and_education`, `synthetic_biology`,
`systems_biology`, `zoology`

### medRxiv 类别：

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
