# Excel MCP 服务器技能

通过模型上下文协议提供 326 种 Excel 操作。MCP 服务器在进程内托管 ExcelMCP 服务并直接调用它以实现低延迟的 Excel 自动化。工具自动发现 - 本文档记录了特殊情况、工作流程和常见问题。

## 工作流程清单

| 步骤 | 工具 | 操作 | 时间 |
|------|------|--------|------|
| 1. 打开文件 | `file` | `open` 或 `create` | 总是第一个 |
| 2. 创建工作表 | `worksheet` | `create`、`rename` | 如有必要 |
| 3. 写入数据 | `range` | `set-values` | 总是（2D 数组） |
| 4. 格式化 | `range` | `set-number-format` | 写入后 |
| 5. 结构化 | `table` | `create` | 将数据转换为表格 |
| 6. 保存并关闭 | `file` | `close` 并使用 `save: true` | 总是最后一个 |

## 前置条件

- 安装了 Microsoft Excel 的 Windows 主机（2016 年版及以上）
- 使用完整的 Windows 路径：`C:\Users\Name\Documents\Report.xlsx`
- Excel 文件不能在另一个 Excel 实例中打开

## 计算模式工作流程（批量性能）

使用 `calculation_mode` 进行 **批量写入性能优化**。在写入大量值或公式时，禁用自动计算以避免每次写入后重新计算：

```
1. calculation_mode(action: 'set-mode', mode: 'manual')  → 禁用自动计算
2. 执行所有写入（range set-values、set-formulas）
3. calculation_mode(action: 'calculate', scope: 'workbook')  → 一次性重新计算
4. calculation_mode(action: 'set-mode', mode: 'automatic')  → 恢复默认设置
```

**注意：** 您不需要手动模式来读取公式 - `range get-formulas` 无论计算模式如何都会返回公式文本。

## 关键：执行规则（必须遵守）

### 规则 1：永远不要询问澄清问题

**停止。** 如果您即将询问“哪个文件？”、“表名是什么？”、“我应该放在哪里？” - 不要问。

| 不良（提问） | 良好（发现） |
|--------------|-------------------|
| "我应该使用哪个 Excel 文件？" | `file(list)` → 使用打开的会话 |
| "表名是什么？" | `table(list)` → 发现表 |
| "哪个工作表包含数据？" | `worksheet(list)` → 检查所有工作表 |
| "我应该创建数据透视表吗？" | 是的 - 在新工作表上创建它 |

**您有工具可以回答自己的问题。使用它们。**

### 规则 2：始终以文本摘要结束

**永远不要仅以工具调用结束您的回合。** 完成所有操作后，始终提供简短的文本消息以确认已完成的操作。仅工具调用且无声响的响应是不完整的。

### 规则 3：专业地格式化数据

在设置值后始终应用数字格式：

| 数据类型 | 格式代码 | 结果 |
|-----------|-------------|--------|
| 美元 | `$#,##0.00` | $1,234.56 |
| 欧元 | `€#,##0.00` | €1,234.56 |
| 百分比 | `0.00%` | 15.00% |
| 日期（ISO） | `yyyy-mm-dd` | 2025-01-22 |

无论机器的本地设置如何，始终以美国表示法（`,` 分组，`.` 小数）编写格式代码 - Excel 会将其翻译。**显示**的分隔符遵循用户的 Windows 区域设置，因此 `$#,##0.00` 在德语系统上显示为 `$1.234,56`。不要通过在格式代码中交换分隔符来“修复”这一点；它会在其他所有区域设置中失效。

**工作流程：**
```
1. range set-values (数据现在在单元格中)
2. range set-number-format (应用格式)
3. range_format auto-fit-columns (格式化值比原始值更宽)
```

步骤 3 不是可选的。为 `45678` 调整的列在值渲染为 `2025-01-22` 或 `$1,234.56` 后会太窄，Excel 会显示 `#####` 而不是数字。

### 规则 4：使用 Excel 表（而不是普通范围）

始终将表格数据转换为 Excel 表：

```
1. range set-values (写入数据包括标题)
2. table(action: 'create', table_name: 'SalesData', range_address: 'A1:D100')
```

**原因：** 结构化引用、自动扩展、需要 Data Model/DAX。

### 规则 5：会话生命周期

```
1. file(action: 'open', path: '...')  → 将响应.session_id 捕获为 sessionId
2. workbook(action: 'get-info', session_id: sessionId)
3. file(action: 'close', session_id: sessionId, save: true)  → 保存并关闭
```

在每个基于会话的后续调用中传递相同的值作为 `session_id`。
`sessionId` 上面是一个局部变量，不是 MCP 参数名。当从 `file(list)` 重用会话时，将匹配条目的 `sessionId` 值复制到 `session_id`。永远不要猜测或替换会话。

**未关闭的会话会导致 Excel 进程运行，锁定文件。**

### 规则 6：数据模型前提条件

DAX 操作需要在数据模型中创建表：

```
步骤 1：创建表 → 表存在
步骤 2：table(action: 'add-to-data-model') → 表在数据模型中
步骤 3：datamodel(action: 'create-measure') → 现在可以工作了
```

### 规则 7：Power Query 开发生命周期

**最佳实践：测试优先工作流程**

```
1. powerquery(action: 'evaluate', m_code: '...') → 无需持久化即可测试
2. powerquery(action: 'create', ...) → 存储验证后的查询
3. powerquery(action: 'refresh', ...) → 加载数据
```

**首先评估的原因：**
- 在创建永久查询之前捕获语法错误和缺失的源
- 比来自 COM 异常的错误消息更好
- 查看实际数据预览（列 + 样本行）
- 无需清理 - 像是 M 代码的 REPL
- 仅适用于简单的字面量表

**常见错误：** 无评估即创建/更新 → 污染工作簿中的损坏查询

### 规则 8：针对性更新而非删除重建

- **优先选择**：`set-values` 在特定范围内（例如，`A5:C5` 用于第 5 行）
- **避免**：删除并重新创建整个结构

**原因：** 保留格式、公式和引用。

### 规则 9：遵循 suggestedNextActions

错误响应包括可操作的提示：
```json
{
  "success": false,
  "errorMessage": "未在数据模型中找到表 'Sales'",
  "suggestedNextActions": ["table(action: 'add-to-data-model', table_name: 'Sales')"]
}
```

## 工具选择快速参考

| 任务 | 工具 | 关键操作 |
|------|------|------------|
| 创建/打开/保存工作簿 | `file` | open、create、close |
| 写入/读取单元格数据 | `range` | set-values、get-values |
| 单元格格式化 | `range` | set-number-format |
| 从数据创建表 | `table` | create |
| 添加表到 Power Pivot | `table` | add-to-data-model |
| 创建 DAX 公式 | `datamodel` | create-measure |
| 创建数据透视表 | `pivottable` | create、create-from-datamodel |
| 使用切片器筛选 | `slicer` | set-slicer-selection |
| 创建图表 | `chart` | create-from-range |
| 运行假设分析 | `analysis` | goal-seek、create-scenario、create-data-table |
| 控制计算模式 | `calculation_mode` | get-mode、set-mode、calculate |
| 可视化验证 | `screenshot` | capture、capture-sheet |

## 参考文档

有关详细指导，请参阅 `references/`：

- [假设分析和求解器限制](./references/analysis.md)
- [核心执行规则和 LLM 指南](./references/behavioral-rules.md)
- [常见错误避免](./references/anti-patterns.md)
- [批量写入性能优化](./references/calculation.md)
- [数据模型约束和模式](./references/workflows.md)
- [图表和格式化](./references/chart.md)
- [条件格式化操作](./references/conditionalformat.md)
- [仪表板和报告最佳实践](./references/dashboard.md)
- [数据模型/DAX 特定内容](./references/datamodel.md)
- [DMV 查询参考用于数据模型分析](./references/dmv-reference.md)
- [Excel 代理模式和高级自动化](./references/excel_agent_mode.md)
- [常见问题和已知限制](./references/gotchas.md)
- [Power Query M 代码语法参考](./references/m-code-syntax.md)
- [数据透视表操作](./references/pivottable.md)
- [Power Query 特定内容](./references/powerquery.md)
- [范围操作和数字格式](./references/range.md)
- [截图和可视化验证](./references/screenshot.md)
- [切片器操作](./references/slicer.md)
- [表操作](./references/table.md)
- [窗口和可见性操作](./references/window.md)
- [工作表操作](./references/worksheet.md)
