# 临床试验数据库

## 前置条件

1.  **`uv`**: 阅读 `uv` 技能并遵循其设置说明，确保 `uv` 已安装并在 PATH 路径中。
2.  **用户通知**: 如果工作区根目录中不存在 `.licenses/clinical_trials_database_LICENSE.txt`，则 (1) 显著通知用户检查 https://clinicaltrials.gov/ 上的条款，然后 (2) 创建记录通知文本和时间戳的文件。

## 概述

通过 REST API v2 访问全球临床试验数据，该 CLI 脚本位于 `scripts/clinical_trials_api.py`，它用专门用于常见筛选器（如分期、年龄组、状态、干预措施、赞助商等）的标志封装了 API，因此您很少需要构建原始查询。

## 核心规则

-   **使用封装器**: 始终使用提供的辅助脚本查询数据库，而不是直接访问数据库。脚本会自动优雅地执行所需的速率限制。
-   **始终使用 `--fields`** — 试验 JSON 记录可能非常大；限制为您需要的数据点。
-   **首先使用 `--count-total`** — 在获取所有记录之前检查结果量。
-   **分页大型结果集** — 使用 `--limit` 与 `--page-token` 进行迭代。
-   **信任搜索筛选器**: 除非明确要求验证详细资格，否则不要手动重新筛选结果。
-   **通知**: 如果使用此技能，请确保在输出中提及。

## 上下文效率警告

试验 JSON 记录可能非常大。**始终**使用 `--fields` 参数将响应限制为仅包含您需要的数据点。写入文件后，仅读取您需要的字段，而不是整个文件。

> [!TIP] 使用 `references/studies_schema.md` 来确定 `--fields` 的确切字段路径。

## 响应布局摘要

API 响应包含研究列表（通常在 `studies[]` 数组中）。每个研究分为 `protocolSection` 和可选的 `resultsSection`。

> [!Tip] 使用下面的**简写别名**与 `--fields` 参数请求特定数据并保持响应大小。

### 顶层字段

-   `totalCount` — 符合查询的总研究数（整数）
-   `studies[]` — 研究对象数组
-   `nextPageToken` — 用于分页的光标字符串

### 常见研究字段（以及简写别名）

-   **识别**
    -   `protocolSection.identificationModule.nctId` (`NCTId`) — 唯一试验 ID
    -   `protocolSection.identificationModule.briefTitle` (`BriefTitle`) — 简短标题
-   **状态**
    -   `protocolSection.statusModule.overallStatus` (`OverallStatus`) — 招募状态
-   **描述**
    -   `protocolSection.descriptionModule.briefSummary` (`BriefSummary`) — 简短描述
-   **治疗组 & 干预措施**
    -   `protocolSection.armsInterventionsModule.interventions` (`ArmsInterventionsModule`)
-   **资格**
    -   `protocolSection.eligibilityModule.eligibilityCriteria` (`EligibilityCriteria`) — 排除/纳入
    -   `protocolSection.eligibilityModule.stdAges` (`StdAge`) — CHILD、ADULT、等

参考 `references/studies_schema.md` 获取完整路径（位置、结果）和常见的 `--fields` 配方。

## 命令

### 搜索研究

用于：通过疾病、药物、分期、状态、年龄组或这些筛选器的任何组合查找试验。

```bash
uv run scripts/clinical_trials_api.py search \
  --condition "<disease>" \
  --intervention "<drug_or_treatment>" \
  --status "<status>" \
  --phase "<phase>" \
  --age-group "<age_group>" \
  --study-type "<study_type>" \
  --sponsor "<sponsor_name>" \
  --has-results \
  --sort "<field>:<asc|desc>" \
  --fields "<fields>" \
  --limit <N> \
  --count-total \
  --page-token "<token>" \
  --output /tmp/search_results.json
```

所有标志都是可选的，并通过 AND 逻辑组合。

**标志参考:**

-   `--condition` — 要搜索的疾病或状况（例如 `"cystic fibrosis"`）。
-   `--intervention` — 药物、设备或治疗名称（例如 `"pembrolizumab"`）。
-   `--status` — 招募状态筛选器。值：RECRUITING、COMPLETED、NOT_YET_RECRUITING、ACTIVE_NOT_RECRUITING、ENROLLING_BY_INVITATION、TERMINATED、SUSPENDED、WITHDRAWN。
-   `--phase` — 试验分期筛选器。值：PHASE1、PHASE2、PHASE3、PHASE4、EARLY_PHASE1、NA。
-   `--age-group` — 患者年龄组筛选器。值：CHILD（0–17）、ADULT（18–64）、OLDER_ADULT（65+）。
-   `--study-type` — 研究类型。值：INTERVENTIONAL、OBSERVATIONAL、EXPANDED_ACCESS。
-   `--sponsor` — 主要赞助商或机构名称（例如 `"National Cancer Institute"`）。
-   `--has-results` — 布尔标志（不需要值）。存在时，筛选出在 ClinicalTrials.gov 上有结果的试验。
-   `--sort` — 排序顺序为 `FieldName:asc` 或 `FieldName:desc`。常见字段：`LastUpdatePostDate`、`EnrollmentCount`、`StudyFirstPostDate`、`StartDate`。
-   `--fields` — 要包含在响应中的 JSON 字段名称的逗号分隔列表。使用此方法保持响应大小（例如 `"NCTId,BriefTitle,OverallStatus,Phase"`）。参见 `references/studies_schema.md` 获取可用字段路径。
-   `--limit` — 每次请求返回的最大研究数量（1–1000，默认 10）。
-   `--count-total` — 布尔标志（不需要值）。存在时，响应包含 `totalCount` 字段，显示跨所有页面的匹配研究总数。
-   `--page-token` — 用于获取下一页结果的透明光标字符串。从先前搜索响应中的 `nextPageToken` 字段获取此值。不要自行构建此字符串；始终逐字复制 API 响应。参见下方的分页部分。
-   `--advanced` — 原始 Essie 筛选表达式，用于结构化查询，超出专门标志的范围（例如 `"AREA[LocationCountry]United States"`）。与其他标志通过 AND 组合。参见 `references/clinical_trials_api.md` 获取语法。
-   `--output` — **（必需）** JSON 响应写入的文件路径。

**示例 — 招募中的儿童囊性纤维化 3 期试验：**

```bash
uv run scripts/clinical_trials_api.py search \
  --condition "cystic fibrosis" \
  --status RECRUITING \
  --phase PHASE3 \
  --age-group CHILD \
  --fields "NCTId,BriefTitle,OverallStatus,Phase" \
  --limit 10 \
  --output /tmp/cf_trials.json
```

**示例 — 招募的阿替利珠单抗食管癌试验：**

```bash
uv run scripts/clinical_trials_api.py search \
  --condition "esophageal cancer" \
  --intervention "Atezolizumab" \
  --status RECRUITING \
  --fields "NCTId,BriefTitle,Phase" \
  --limit 10 \
  --output /tmp/atezolizumab_trials.json
```

### 根据 NCT ID 获取研究

用于：在您已经拥有 NCT 标识符时，获取特定试验的完整详细信息。

```bash
uv run scripts/clinical_trials_api.py get-study \
  <nct_id> [--fields "<fields>"] \
  --output /tmp/study.json
```

如果省略 `--fields`，则返回一组有用的默认字段：
`NCTId,BriefTitle,OverallStatus,Phase,BriefSummary,`
`ConditionsModule,ArmsInterventionsModule,EligibilityModule`

**默认响应的结构:**

```json
{
  "protocolSection": {
    "identificationModule": {
      "nctId": "NCT00000000",
      "briefTitle": "Study Title"
    },
    "statusModule": {
      "overallStatus": "RECRUITING"
    },
    "descriptionModule": {
      "briefSummary": "This study is about..."
    },
    "conditionsModule": {
      "conditions": [ "Condition Name" ]
    },
    "armsInterventionsModule": {
      "interventions": [ { "type": "DRUG", "name": "Drug Name" } ]
    },
    "eligibilityModule": {
      "eligibilityCriteria": "Inclusion:\n- ...",
      "stdAges": [ "ADULT" ]
    }
  }
}
```

### 获取资格/纳入标准

用于：提取纳入/排除规则、年龄范围和性别要求，用于患者匹配任务。

```bash
uv run scripts/clinical_trials_api.py \
  get-eligibility <nct_id> \
  --output /tmp/eligibility.json
```

快捷方式，返回标题和完整的资格模块（纳入/排除标准、年龄范围、性别）。

**示例 — NCT04886804 的纳入标准:**

```bash
uv run scripts/clinical_trials_api.py \
  get-eligibility NCT04886804 \
  --output /tmp/eligibility_NCT04886804.json
```

### 匹配研究计数

用于：探索试验格局——在获取完整记录之前，检查针对状况、分期或状态的试验数量。

```bash
uv run scripts/clinical_trials_api.py count \
  --condition "<disease>" \
  [--status "<status>"] [--phase "<phase>"] ... \
  --output /tmp/count.json
```

仅返回符合搜索标准的临床试验总数，不获取研究记录。接受与 `search` 相同的筛选器标志。

### 按位置/地理搜索

用于：将试验缩小到特定国家、州或城市。

使用 `--advanced` 与 `AREA[LocationCountry]` 或 `AREA[LocationCity]` 限制结果按地理位置：

```bash
uv run scripts/clinical_trials_api.py search \
  --condition "cystic fibrosis" \
  --status RECRUITING \
  --advanced "AREA[LocationCity]New York" \
  --fields "NCTId,BriefTitle" \
  --limit 20 \
  --output /tmp/nyc_cf_trials.json
```

### 按赞助商/组织搜索

用于：识别赞助商或机构的试验组合。

使用 `--sponsor` 查找由特定机构或公司运行的试验：

```bash
uv run scripts/clinical_trials_api.py search \
  --sponsor "National Cancer Institute" \
  --fields "NCTId,BriefTitle,LeadSponsorName" \
  --limit 20 \
  --output /tmp/nci_trials.json
```

### 组合多标准搜索

用于：复杂查询，通过多个筛选器（状况和药物和分期和地理位置和赞助商等）分层。

所有标志通过 AND 组合，因此您可以在单个查询中分层条件、干预措施、状态、分期、地理位置和赞助商：

```bash
uv run scripts/clinical_trials_api.py search \
  --condition "pancreatic cancer" \
  --intervention "immunotherapy" \
  --status RECRUITING \
  --phase PHASE3 \
  --advanced "AREA[LocationCountry]United States" \
  --fields "NCTId,BriefTitle,Phase,LeadSponsorName" \
  --limit 20 \
  --output /tmp/panc_trials.json
```

### 原始 API 查询（逃生舱）

用于：不涵盖专门标志的不常见端点或参数组合。

```bash
uv run scripts/clinical_trials_api.py raw-query \
  --endpoint <path> \
  --params '<json_dict>' \
  --output /tmp/raw_result.json
```

## 分页

当结果超过 `--limit` 时，响应将包含 `nextPageToken`。使用 `--page-token` 传递它以获取下一页：

```bash
uv run scripts/clinical_trials_api.py search \
  --condition "breast cancer" \
  --status RECRUITING \
  --limit 50 --count-total \
  --output /tmp/breast_cancer_p1.json

uv run scripts/clinical_trials_api.py search \
  --condition "breast cancer" \
  --status RECRUITING \
  --limit 50 --page-token "CAo=" \
  --output /tmp/breast_cancer_p2.json
```

## 高级查询

对于超出专门标志的复杂筛选，使用 `--advanced` 与 Essie 表达式。

**什么是 Essie 表达式？** Essie 是 ClinicalTrials.gov 的搜索引擎。Essie 表达式是针对特定字段（例如国家、分期）的结构化查询，而不是进行一般关键词搜索。

-   **`AREA[Field]Value`**: 针对特定字段。
    -   `AREA[LocationCountry]United States`
    -   `AREA[Phase]PHASE3`
-   **布尔运算符**: 使用 `AND`、`OR`、`NOT` 组合。
-   **`RANGE[min, max]`**: 用于数字/日期字段（例如 `RANGE[500, MAX]`）。

参见 `references/clinical_trials_api.md` 获取语法和可用字段。

它与其他标志通过 AND 组合：

```bash
uv run scripts/clinical_trials_api.py search \
  --condition "diabetes" \
  --advanced "AREA[LocationCountry]United States \
    AND AREA[EnrollmentCount]RANGE[500, MAX]" \
  --fields "NCTId,BriefTitle,EnrollmentCount" \
  --output /tmp/diabetes_us_large.json
```

## 参考

-   **API 参数、枚举值和 Essie 语法:**
    `references/clinical_trials_api.md`
-   **JSON 字段路径和 `--fields` 配方:** `references/studies_schema.md`
