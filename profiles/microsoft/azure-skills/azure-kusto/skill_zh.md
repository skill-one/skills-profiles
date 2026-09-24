# Azure Data Explorer (Kusto) 查询与分析

执行 KQL 查询并管理 Azure Data Explorer 资源，支持对日志、遥测和时序数据执行快速、可扩展的大数据分析。

## 技能激活触发条件

**当用户要求时，请立即使用此技能：**
- "为我的 Kusto 数据库查询 [数据模式]"
- "显示来自 Azure Data Explorer 过去一小时的 event"
- "分析我在 ADX 集群中的日志"
- "在 [数据库] 上运行 KQL 查询"
- "我的 Kusto 数据库中有哪些表？"
- "显示 [表] 的模式"
- "列出我的 Azure Data Explorer 集群"
- "按 [维度] 聚合遥测数据"
- "根据我的日志创建时序图表"

**关键指标：**
- 提及 "Kusto"、"Azure Data Explorer"、"ADX" 或 "KQL"
- 日志分析或遥测分析请求
- 时序数据探索
- IoT 数据分析查询
- SIEM 或安全分析任务
- 对大规模数据集进行数据聚合的请求
- 性能监控或 APM 查询

## 概述

本技能用于查询和管理 Azure Data Explorer（Kusto），这是一种针对日志和遥测数据优化的、快速且高度可扩展的数据探索服务。Azure Data Explorer 使用 Kusto 查询语言（KQL）在数十亿条记录上提供亚秒级查询性能。

关键能力：
- **查询执行**：针对大规模数据集运行 KQL 查询
- **模式探索**：发现表、列和数据类型
- **资源管理**：列出集群和数据库
- **分析**：聚合、时序、异常检测、机器学习

## 核心工作流

1. **发现资源**：在订阅中列出可用的集群和数据库
2. **探索模式**：获取表结构以理解数据模型
3. **查询数据**：执行 KQL 查询以进行分析、筛选和聚合
4. **分析结果**：处理查询输出，获取洞察和报告

## 查询模式

### 模式 1：基础数据检索
从表中获取最近记录，并使用简单筛选。

**示例 KQL**：
```kql
Events
| where Timestamp > ago(1h)
| take 100
```

**用途**：快速数据检查、最近事件获取

### 模式 2：聚合分析
按维度汇总数据，获取洞察和报告。

**示例 KQL**：
```kql
Events
| summarize count() by EventType, bin(Timestamp, 1h)
| order by count_ desc
```

**用途**：事件计数、分布分析、Top-N 查询

### 模式 3：时序分析
在时间段窗口内分析数据，以了解趋势和模式。

**示例 KQL**：
```kql
Telemetry
| where Timestamp > ago(24h)
| summarize avg(ResponseTime), percentiles(ResponseTime, 50, 95, 99) by bin(Timestamp, 5m)
| render timechart
```

**用途**：性能监控、趋势分析、异常检测

### 模式 4：连接与关联
结合多个表进行跨数据集分析。

**示例 KQL**：
```kql
Events
| where EventType == "Error"
| join kind=inner (
    Logs
    | where Severity == "Critical"
) on CorrelationId
| project Timestamp, EventType, LogMessage, Severity
```

**用途**：根因分析、关联事件追踪

### 模式 5：模式发现
查询前探索表结构。

**工具**：`kusto_table_schema_get`

**用途**：理解数据模型、查询规划

## 关键数据字段

执行查询时，常见的字段模式：
- **时间戳**：事件时间（日期时间）- 使用 `ago()`、`between()`、`bin()` 进行时间筛选
- **事件类型/类别**：用于分组的分类字段
- **关联ID/会话ID**：用于追踪相关事件
- **严重度/级别**：用于按重要性筛选
- **维度**：用于分组和筛选的自定义属性

## 结果格式

查询结果包括：
- **列**：字段名称和数据类型
- **行**：符合查询条件的数据记录
- **统计信息**：行数、执行时间、资源利用率
- **可视化**：图表渲染提示（timechart、barchart 等）

## KQL 最佳实践

**🟢 性能优化：**
- 提前筛选：在连接和聚合之前使用 `where`
- 限制结果大小：使用 `take` 或 `limit` 以减少数据传输
- 时间筛选：始终针对时序数据进行时间范围筛选
- 索引列：优先在索引列上进行筛选

**🔵 查询模式：**
- 使用 `summarize` 进行聚合，而非单独使用 `count()`
- 在时序数据中使用 `bin()` 进行时间分桶
- 使用 `project` 仅选择所需的列
- 使用 `extend` 添加计算字段

**🟡 常用函数：**
- `ago(timespan)`：相对时间（ago(1h)、ago(7d)）
- `between(start .. end)`：范围筛选
- `startswith()`、`contains()`、`matches regex`：字符串筛选
- `parse`、`extract`：从字符串中提取值
- `percentiles()`、`avg()`、`sum()`、`max()`、`min()`：聚合

## 最佳实践

- 始终包含时间范围筛选以优化查询性能
- 在探索性查询中使用 `take` 或 `limit`，避免产生大规模结果集
- 使用 `summarize` 进行聚合，而非在客户端处理
- 将常用查询存储为数据库中的函数
- 为重复聚合使用物化视图
- 监控查询性能与资源消耗
- 应用数据保留策略以管理存储成本
- 使用流式摄入进行实时分析（延迟 < 1 秒）
- 与 Azure Monitor 集成以获取运维洞察

## 使用的 MCP 工具

**工具** | **用途**
|---------|---------|
| `kusto_cluster_list` | 列出订阅中所有 Azure Data Explorer 集群
| `kusto_database_list` | 列出特定 Kusto 集群中的所有数据库
| `kusto_query` | 针对 Kusto 数据库执行 KQL 查询
| `kusto_table_schema_get` | 获取特定表的模式信息

**必需参数：**
- `subscription`：Azure 订阅 ID 或显示名称
- `cluster`：Kusto 集群名称（例如 "mycluster"）
- `database`：数据库名称
- `query`：KQL 查询字符串（用于查询操作）
- `table`：表名称（用于模式操作）

**可选参数：**
- `resource-group`：资源组名称（用于列举操作）
- `tenant`：Azure AD 租户 ID

## 备选方案：Azure CLI 命令

如果 Azure MCP Kusto 工具失败、超时或不可用，请使用 Azure CLI 命令作为备选方案。

### CLI 命令参考

**操作** | **Azure CLI 命令**
-----------|-------------------
| 列出集群 | `az kusto cluster list --resource-group <rg-name>`
| 列出数据库 | `az kusto database list --cluster-name <cluster} --resource-group <rg-name}`
| 显示集群 | `az kusto cluster show --name <cluster} --resource-group <rg-name}`
| 显示数据库 | `az kusto database show --cluster-name <cluster} --database-name <db} --resource-group <rg-name}`

### 通过 Azure CLI 执行 KQL 查询
通过 Kusto REST API 或直接集群 URL 执行查询：
```bash
az rest --method post \
  --url "https://<cluster>.<region>.kusto.windows.net/v1/rest/query" \
  --body "{ \"db\": \"<database>\", \"csl\": \"<kql-query>\" }"
```

### 何时使用备选方案

切换到 Azure CLI 时，当：
- MCP 工具返回超时错误（查询时间 > 60 秒）
- MCP 工具返回“服务不可用”或连接错误
- MCP 工具出现认证失败
- 当数据库已知有数据但返回空响应

## 常见问题

- **权限被拒绝**：验证数据库权限（查询最低需要 Viewer 角色）
- **查询超时**：通过时间筛选优化查询、减少结果集或增加超时时间
- **语法错误**：验证 KQL 语法 - 常见问题：缺少管道符、运算符错误
- **结果为空**：检查时间范围筛选（可能过于严格），验证表名称
- **未找到集群**：检查集群名称格式（排除 ".kusto.windows.net" 后缀）
- **CPU 使用率过高**：查询范围过广 - 添加筛选条件、缩小时间范围、限制聚合
- **数据摄入延迟**：流式数据的延迟取决于摄入方式，可能为 1-30 秒

## 使用场景

- **日志分析**：应用日志、系统日志、审计日志
- **IoT 分析**：传感器数据、设备遥测、实时监控
- **安全分析**：SIEM 数据、威胁检测、安全事件关联
- **APM**：应用性能指标、用户行为、错误追踪
- **商业智能**：点击流分析、用户分析、运营 KPI
