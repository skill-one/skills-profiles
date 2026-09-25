## 概述

Lightning 报告定义了 Salesforce 数据的查询、分组、过滤和显示方式。每个报告都是一个 `.report-meta.xml` 文件，放置在项目源目录的 `reports/<文件夹名>/` 下（检查 `sfdx-project.json` → `packageDirectories[].path` 获取源根目录）。

## 关键规则（首先阅读）

**导致部署失败的顶级问题 — 在生成任何报告之前检查这些：**
1. **列中的分组字段** — `<groupingsDown>` 或 `<groupingsAcross>` 中的字段绝不能也出现在 `<columns>` 中
2. **错误的列名** — 列名是报告类型特定的。始终使用 MCP 工具进行验证（参见 `references/column-names.md`）
3. **错误的范围** — LeadList 使用 `org`，而不是 `organization`
4. **过滤列点表示法** — 过滤 `<column>` 值使用扁平名称（`INDUSTRY`、`TYPE`），而不是点表示法（`ACCOUNT.INDUSTRY` 是无效的）
5. **多值选择列表过滤器** — 使用一个 `<criteriaItems>` 并用逗号分隔 `<value>`（例如，`Technology,Financial Services`）。不要拆分为多个 `criteriaItems` 并使用布尔过滤器

### 规则 1：格式决定必需的元素

| 格式 | `<groupingsDown>` | `<groupingsAcross>` | `<block>` |
|------|-------------------|---------------------|-----------|
| `Tabular` | 不允许 | 不允许 | 无 |
| `Summary` | 至少 1（最多 3） | 不允许 | 无 |
| `Matrix` | 至少 1（最多 3） | 至少 1（最多 3） | 无 |
| `Joined` | 不能在顶层 | 不能在顶层 | 至少 2（最多 5） |

### 规则 2：使用平台列名

报告元数据使用**平台报告列名**，而不是原始 API 字段名。**始终调用 `get_metadata_type_sections` 或 `get_metadata_type_context` 确认有效的列名。** 参见 `references/column-names.md` 获取每种报告类型的常见映射。

### 规则 3：需要有效的报告类型

`<reportType>` 必须是标准 API 名称（例如，`Opportunity`、`AccountList`、`CaseList`、`LeadList`、`AccountContactRole`）或已部署的自定义报告类型开发者名称。

### 规则 4–5：图表和聚合需要 Summary/Matrix

图表和 `<aggregateTypes>`（求和、平均值等）仅在 Summary 和 Matrix 报告中工作。

### 规则 6–8：限制

- 每个报告最多 **3 个跨过滤器**，每个跨过滤器最多有 **5 个条件项**
- `<filterLogic>` 必须按顺序引用所有过滤器（例如，`1 AND (2 OR 3)`）
- 连接报告：2–5 个块，每个块格式必须是 Summary 或 Matrix（不能是 Tabular）

### 规则 9：文件夹结构

报告必须存放在具有相应文件夹元数据文件的文件夹中：
```xml
<sourceDir>/reports/<FolderName>/<ReportName>.report-meta.xml
<sourceDir>/reports/<FolderName>-meta.xml
```
从 `sfdx-project.json` 确定 `<sourceDir>`（通常为 `force-app/main/default`，但这是可配置的）。

### 规则 10–11：日期列和范围

- 日期列使用平台名称（`CLOSE_DATE`，而不是 `CloseDate`）
- LeadList 范围是 `org`；Opportunity/AccountList/CaseList 使用 `organization`

### 规则 12–13：描述和分组

- `<description>` 最大 **255 个字符**
- 分组字段不能出现在 `<columns>` 中 — 自动部署失败

### 规则 14：文件夹元数据需要 `<sharedTo>`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ReportFolder xmlns="http://soap.sforce.com/2006/04/metadata">
    <folderShares>
        <accessLevel>Manage</accessLevel>
        <sharedTo>AllInternalUsers</sharedTo>
        <sharedToType>Group</sharedToType>
    </folderShares>
    <name>My Report Folder</name>
</ReportFolder>
```

### 规则 15：仅使用有效的日期间隔

使用 `INTERVAL_CURRENT` 表示“本季度”，`INTERVAL_CURY` 表示“今年”，`INTERVAL_LAST30` 表示“过去 30 天”。不要使用 `INTERVAL_CURQ` — 它是无效的。参见 `references/date-intervals.md` 获取完整列表。

## 顶层元素

| 元素 | 必需 | 备注 |
|------|------|------|
| `<name>` | 是 | 报告名称（最多 40 个字符） |
| `<reportType>` | 是 | 报告类型 API 名称 |
| `<format>` | 是 | `Tabular`、`Summary`、`Matrix` 或 `Joined` |
| `<scope>` | 推荐 | `organization`（或 `org` 用于 LeadList） |
| `<columns>` | 是 | 字段列 — 每个列有 `<field>` 和可选的 `<aggregateTypes>` |
| `<filter>` | 否 | 包含 `<criteriaItems>`，其中包含 `<column>`、`<operator>`、`<value>` |
| `<groupingsDown>` | 条件性 | 行分组：`<field>`、`<dateGranularity>`、`<sortOrder>` |
| `<groupingsAcross>` | 条件性 | 列分组（仅 Matrix） |
| `<timeFrameFilter>` | 推荐 | `<dateColumn>`、`<interval>`，可选的 `<startDate>`/`<endDate>` |
| `<chart>` | 否 | 参见 `references/chart-types.md` |
| `<buckets>` | 否 | 桶字段定义 |
| `<crossFilters>` | 否 | 跨对象过滤器（`with`/`without`） |
| `<showDetails>` | 推荐 | `true`/`false` |
| `<showGrandTotal>` | 推荐 | `true`/`false` |
| `<showSubTotals>` | 推荐 | `true`/`false` |
| `<description>` | 推荐 | 业务目的（最多 255 个字符） |
| `<block>` | 条件性 | 连接格式块 |

## 过滤语法

```xml
<filter>
    <criteriaItems>
        <column>STAGE_NAME</column>
        <operator>equals</operator>
        <value>Closed Won</value>
    </criteriaItems>
</filter>
```

**多值选择列表：** 使用一个 `criteriaItem` 并用逗号分隔值：
```xml
<criteriaItems>
    <column>INDUSTRY</column>
    <operator>equals</operator>
    <value>Technology,Financial Services</value>
</criteriaItems>
```

常用运算符：`equals`、`notEqual`、`lessThan`、`greaterThan`、`contains`、`startsWith`、`includes`、`excludes`、`isBlank`、`notBlank`。完整列表在 `references/filter-operations.md`。

## 生成工作流

1. **收集需求** — 对象、字段、分组、过滤器、图表需求
2. **确定格式** — 无分组 → Tabular；行分组 → Summary；行 + 列 → Matrix；多个对象 → Joined
3. **识别列名** — 调用 `get_metadata_type_sections` MCP 工具获取报告类型的有效平台列名
4. **编写元数据** — 从 `examples/` 中最接近的示例开始并调整
5. **创建文件夹** — 生成文件夹目录 + `<FolderName>-meta.xml` 并包含 `<folderShares>`
6. **验证** — 运行 `references/verification-checklist.md` 中的验证清单

## 参考文件索引

| 文件 | 何时阅读 |
|------|----------|
| `references/column-names.md` | 第 3 步 — 每种报告类型的列名映射 |
| `references/date-intervals.md` | 设置 `timeFrameFilter` 间隔时 |
| `references/chart-types.md` | 添加图表时 — 所有 17 种类型 + `legendPosition` 规则 |
| `references/filter-operations.md` | 构建过滤器时 — 完整运算符参考 |
| `references/verification-checklist.md` | 第 6 步 — 部署前验证 |
| `references/errors-and-troubleshooting.md` | 字段缺失或部署失败时 |
| `examples/TabularOpportunitiesReport.report-meta.xml` | Tabular 报告模板 |
| `examples/OpportunitiesByStageReport.report-meta.xml` | 带图表的 Summary 报告 |
| `examples/OpportunitiesByStageAndQuarter.report-meta.xml` | Matrix 报告模板 |
| `examples/AccountsCreatedThisYear.report-meta.xml` | 带时间范围的过滤报告 |
