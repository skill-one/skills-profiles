# Azure Data Explorer (Kusto) 查询与分析

执行 KQL 查询并管理 Azure Data Explorer 资源，以快速、可扩展地分析日志、遥测和时间序列数据。

## 技能激活触发器

**当用户要求时立即使用此技能：**
- "查询我的 Kusto 数据库中的 [数据模式]"
- "显示我来自 Azure Data Explorer 的过去一小时事件"
- "分析我的 ADX 集群中的日志"
- "在 [数据库] 上运行 KQL 查询"
- "我的 Kusto 数据库中有哪些表？"
- "显示 [表] 的架构"
- "列出我的 Azure Data Explorer 集群"
- "按 [维度] 聚合遥测数据"
- "从我的日志创建时间序列图表"

**关键指标：**
- 提及 "Kusto"、"Azure Data Explorer"、"ADX" 或 "KQL"
- 日志分析或遥测分析请求
- 时间序列数据探索
- 物联网数据分析查询
- SIEM 或安全分析任务
- 对大型数据集进行数据聚合的请求
- 性能监控或 APM 查询

## 概述

此技能可查询和管理 Azure Data Explorer (Kusto)，这是一种针对日志和遥测数据优化的快速、高度可扩展的数据探索服务。Azure Data Explorer 使用 Kusto 查询语言 (KQL) 在数十亿条记录上提供亚秒级的查询性能。

主要功能：
- **查询执行**：对海量数据集运行 KQL 查询
- **架构探索**：发现表、列和数据类型
- **资源管理**：列出集群和数据库
- **分析**：聚合、时间序列、异常检测、机器学习

## 核心工作流

1. **发现资源**：列出订阅中的可用集群和数据库
2. **探索架构**：检索表结构以了解数据模型
3. **查询数据**：执行 KQL 查询以进行分析、过滤、聚合
4. **分析结果**：处理查询输出以获取洞察和报告

## 查询模式

### 模式 1：基本数据检索
从表中检索最近记录并进行简单过滤。

**示例 KQL**：
```kql
Events
| where Timestamp > ago(1h)
| take 100
```

**用于**：快速数据检查、最近事件检索

### 模式 2：聚合分析
按维度汇总数据以获取洞察和报告。

**示例 KQL**：
```kql
Events
| summarize count() by EventType, bin(Timestamp, 1h)
| order by count_ desc
```

**用于**：事件计数、分布分析、Top-N 查询

### 模式 3：时间序列分析
分析时间窗口内的数据以识别趋势和模式。

**示例 KQL**：
```kql
Telemetry
| where Timestamp > ago(24h)
| summarize avg(ResponseTime), percentiles(ResponseTime, 50, 95, 99) by bin(Timestamp, 5m)
| render timechart
```

**用于**：性能监控、趋势分析、异常检测

### 模式 4：连接和关联
组合多个表进行跨数据集分析。

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

**用于**：根本原因分析、关联事件跟踪

### 模式 5：架构发现
在查询前探索表结构。

**工具**：`kusto_table_schema_get`

**用于**：理解数据模型、查询规划

## 关键数据字段

执行查询时，常见字段模式：
- **Timestamp**：事件时间（日期时间）- 使用 `ago()`、`between()`、`bin()` 进行时间过滤
- **EventType/Category**：用于分组的分类字段
- **CorrelationId/SessionId**：用于跟踪相关事件
- **Severity/Level**：按重要性过滤
- **Dimensions**：用于分组和过滤的自定义属性

## 结果格式

查询结果包括：
- **列**：字段名称和数据类型
- **行**：匹配查询的数据记录
- **统计信息**：行数、执行时间、资源利用率
- **可视化**：图表渲染提示（timechart、barchart 等）

## KQL 最佳实践

**🟢 性能优化：**
- 早期过滤：在连接和聚合之前使用 `where`
- 限制结果大小：使用 `take` 或 `limit` 减少数据传输
- 时间过滤器：始终按时间范围过滤时间序列数据
- 索引列：首先在索引列上过滤

**🔵 查询模式：**
- 使用 `summarize` 进行聚合，而不是单独使用 `count()`
- 使用 `bin()` 进行时间序列中的时间分桶
- 使用 `project` 选择仅需要的列
- 使用 `extend` 添加计算字段

**🟡 常见函数：**
- `ago(timespan)`：相对时间（ago(1h)、ago(7d)）
- `between(start .. end)`：范围过滤
- `startswith()`、`contains()`、`matches regex`：字符串过滤
- `parse`、`extract`：从字符串中提取值
- `percentiles()`、`avg()`、`sum()`、`max()`、`min()`：聚合

## 最佳实践

- 始终包含时间范围过滤器以优化查询性能
- 使用 `take` 或 `limit` 进行探索性查询以避免大型结果集
- 利用 `summarize` 进行聚合，而不是客户端处理
- 将常用查询作为数据库中的函数存储
- 使用物化视图进行重复聚合
- 监控查询性能和资源消耗
- 应用数据保留策略以管理存储成本
- 使用流式摄取进行实时分析（延迟 < 1 秒）
- 与 Azure Monitor 集成以获取操作洞察

## MCP 工具使用

| 工具 | 目的 |
|------|---------|
| `kusto_cluster_list` | 列出订阅中的所有 Azure Data Explorer 集群 |
| `kusto_database_list` | 列出特定 Kusto 集群中的所有数据库 |
| `kusto_query` | 对 Kusto 数据库执行 KQL 查询 |
| `kusto_table_schema_get` | 检索特定表的架构信息 |

**必需参数**：
- `subscription`：Azure 订阅 ID 或显示名称
- `cluster`：Kusto 集群名称（例如，"mycluster"）
- `database`：数据库名称
- `query`：KQL 查询字符串（用于查询操作）
- `table`：表名称（用于架构操作）

**可选参数**：
- `resource-group`：资源组名称（用于列出操作）
- `tenant`：Azure AD 租户 ID

## 备用策略：Azure CLI 命令

如果 Azure MCP Kusto 工具失败、超时或不可用，请使用 Azure CLI 命令作为备用。

### CLI 命令参考

| 操作 | Azure CLI 命令 |
|-----------|-------------------|
| 列出集群 | `az kusto cluster list --resource-group <rg-name>` |
| 列出数据库 | `az kusto database list --cluster-name <cluster> --resource-group <rg-name>` |
| 显示集群 | `az kusto cluster show --name <cluster> --resource-group <rg-name>` |
| 显示数据库 | `az kusto database show --cluster-name <cluster> --database-name <db> --resource-group <rg-name>` |

### 通过 Azure CLI 执行 KQL 查询

对于查询，使用 Kusto REST API 或直接集群 URL：
```bash
az rest --method post \
  --url "https://<cluster>.<region>.kusto.windows.net/v1/rest/query" \
  --body "{ \"db\": \"<database>\", \"csl\": \"<kql-query>\" }"
```

### 何时备用

在以下情况下切换到 Azure CLI：
- MCP 工具返回超时错误（查询 > 60 秒）
- MCP 工具返回“服务不可用”或连接错误
- MCP 工具身份验证失败
- 数据库已知有数据时返回空响应

## 常见问题

- **访问被拒绝**：验证数据库权限（至少需要查看者角色进行查询）
- **查询超时**：使用时间过滤器优化查询，减少结果集，或增加超时时间
- **语法错误**：验证 KQL 语法 - 常见问题：缺少管道符、运算符不正确
- **空结果**：检查时间范围过滤器（可能过于严格），验证表名称
- **集群未找到**：检查集群名称格式（排除 ".kusto.windows.net" 后缀）
- **高 CPU 使用率**：查询过于广泛 - 添加过滤器，减少时间范围，减少聚合
- **摄取延迟**：流式数据可能有 1-30 秒的延迟，具体取决于摄取方法

## 用例

- **日志分析**：应用程序日志、系统日志、审计日志
- **物联网分析**：传感器数据、设备遥测、实时监控
- **安全分析**：SIEM 数据、威胁检测、安全事件关联
- **APM**：应用程序性能指标、用户行为、错误跟踪
- **商业智能**：点击流分析、用户分析、运营 KPI
