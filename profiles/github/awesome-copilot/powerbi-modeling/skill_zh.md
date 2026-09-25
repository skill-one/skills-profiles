# Power BI 语义建模

指导用户遵循微软最佳实践，构建优化且文档完善的 Power BI 语义模型。

## 使用此技能的场景

当用户询问以下内容时，使用此技能：
- 创建或优化 Power BI 语义模型
- 设计星型模式（维度/事实表）
- 编写 DAX 度量值或计算列
- 配置表关系（基数、跨筛选）
- 实施行级安全（RLS）
- 表格、列、度量值的命名规范
- 为模型添加描述和文档
- 性能调优和优化
- 计算组和字段参数
- 模型验证和最佳实践检查

**触发短语：** "创建度量值"、"添加关系"、"星型模式"、"优化模型"、"DAX 公式"、"RLS"、"命名规范"、"模型文档"、"基数"、"跨筛选"

## 前置条件

### 必需工具
- **Power BI 建模 MCP 服务器**：用于连接和修改语义模型
  - 启用：连接操作、表操作、度量值操作、关系操作等
  - 必须配置并运行，才能与模型交互

### 可选依赖
- **Microsoft Learn MCP 服务器**：推荐用于研究最新最佳实践
  - 启用：microsoft_docs_search、microsoft_docs_fetch
  - 用于复杂场景、新功能和官方文档

## 工作流程

### 1. 首先连接和分析

在提供任何建模指导之前，始终检查当前模型状态：

```
1. 列出连接：connection_operations(operation: "ListConnections")
2. 如果没有连接，检查本地实例：connection_operations(operation: "ListLocalInstances")
3. 连接到模型（桌面版或 Fabric）
4. 获取模型概览：model_operations(operation: "Get")
5. 列出表格：table_operations(operation: "List")
6. 列出关系：relationship_operations(operation: "List")
7. 列出度量值：measure_operations(operation: "List")
```

### 2. 评估模型健康状况

连接后，根据最佳实践评估模型：

- **星型模式**：表格是否正确分类为维度或事实？
- **关系**：基数正确吗？是否存在最小双向筛选？
- **命名**：是否为人类可读、一致的命名规范？
- **文档**：表格、列、度量值是否有描述？
- **度量值**：是否为关键计算提供显式度量值？
- **隐藏字段**：技术列是否从报告视图中隐藏？

### 3. 提供针对性指导

根据分析结果，使用参考文档指导改进：
- 星型模式设计：参见 [STAR-SCHEMA.md](references/STAR-SCHEMA.md)
- 关系配置：参见 [RELATIONSHIPS.md](references/RELATIONSHIPS.md)
- DAX 度量值和命名：参见 [MEASURES-DAX.md](references/MEASURES-DAX.md)
- 性能优化：参见 [PERFORMANCE.md](references/PERFORMANCE.md)
- 行级安全：参见 [RLS.md](references/RLS.md)

## 快速参考：模型质量检查清单

| 领域 | 最佳实践 |
|------|----------|
| 表格 | 清晰的维度与事实分类 |
| 命名 | 人类可读：`Customer Name` 而不是 `CUST_NM` |
| 描述 | 所有表格、列、度量值均有文档 |
| 度量值 | 为业务指标提供显式 DAX 度量值 |
| 关系 | 从维度到事实的一对多关系 |
| 跨筛选 | 单向，除非特别需要 |
| 隐藏字段 | 隐藏技术键、ID 以免在报告中显示 |
| 日期表 | 使用专用标记的日期表 |

## MCP 工具参考

使用以下 Power BI 建模 MCP 操作：

| 操作类别 | 关键操作 |
|-------------------|----------------|
| `connection_operations` | Connect, ListConnections, ListLocalInstances, ConnectFabric |
| `model_operations` | Get, GetStats, ExportTMDL |
| `table_operations` | List, Get, Create, Update, GetSchema |
| `column_operations` | List, Get, Create, Update (描述、隐藏、格式) |
| `measure_operations` | List, Get, Create, Update, Move |
| `relationship_operations` | List, Get, Create, Update, Activate, Deactivate |
| `dax_query_operations` | Execute, Validate |
| `calculation_group_operations` | List, Create, Update |
| `security_role_operations` | List, Create, Update, GetEffectivePermissions |

## 常见任务

### 添加带描述的度量值
```
measure_operations(
  operation: "Create",
  definitions: [{
    name: "Total Sales",
    tableName: "Sales",
    expression: "SUM(Sales[Amount])",
    formatString: "$#,##0",
    description: "所有销售金额的总和"
  }]
)
```

### 更新列描述
```
column_operations(
  operation: "Update",
  definitions: [{
    tableName: "Customer",
    name: "CustomerKey",
    description: "客户维度的唯一标识符",
    isHidden: true
  }]
)
```

### 创建关系
```
relationship_operations(
  operation: "Create",
  definitions: [{
    fromTable: "Sales",
    fromColumn: "CustomerKey",
    toTable: "Customer",
    toColumn: "CustomerKey",
    crossFilteringBehavior: "OneDirection"
  }]
)
```

## 使用 Microsoft Learn MCP 的场景

使用 `microsoft_docs_search` 研究当前最佳实践：
- 最新 DAX 函数文档
- 新的 Power BI 功能和特性
- 复杂建模场景（SCD Type 2、多对多）
- 性能优化技术
- 安全实现模式
