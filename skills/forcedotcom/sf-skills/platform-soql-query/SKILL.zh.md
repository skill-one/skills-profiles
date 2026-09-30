---
name: platform-soql-query
description: 当用户需要编写或优化 SOQL/SOSL 时使用：自然语言到查询的生成、关系查询、聚合、查询计划/选择性分析，以及性能或安全性的改进。触发条件：当用户编写、优化或调试 SOQL/SOSL，接触 .soql 文件，或询问关于关系查询、聚合或查询性能时。不触发用于批量数据操作（使用 platform-data-manage）、Apex DML 逻辑（使用 platform-apex-generate）或报告/仪表板查询。
---

# platform-soql-query: Salesforce SOQL 查询专家

当用户需要 **SOQL/SOSL 编写或优化** 时使用此技能：自然语言到查询的生成、关系查询、聚合、查询计划分析，以及 Salesforce 查询的性能/安全性改进。

## 此技能负责任务的情况

当工作涉及以下内容时，使用 `platform-soql-query`：
- `.soql` 文件
- 从自然语言生成查询
- 关系查询和聚合查询
- 查询优化和选择性问题分析
- SOQL/SOSL 语法和受管理员限制的设计

当用户执行以下操作时，将任务委托给其他技能：
- 执行批量数据操作 → [platform-data-manage](../platform-data-manage/SKILL.md)
- 在更广泛的 Apex 实现中嵌入查询逻辑 → [platform-apex-generate](../platform-apex-generate/SKILL.md)
- 通过日志而不是查询形状进行调试 → [platform-apex-logs-debug](../platform-apex-logs-debug/SKILL.md)

---

## 收集初始所需上下文

请求或推断：
- 目标对象
- 需要的字段
- 过滤标准
- 排序/限制要求
- 查询是用于显示、自动化、报告式分析还是 Apex 使用
- 是否已经关注性能/选择性

---

## 推荐工作流程

### 1. 生成最简单的正确查询
优先考虑：
- 仅需要字段
- 清晰的 WHERE 标准
- 适当情况下合理的 LIMIT
- 关系深度仅到必要程度

在起草时，使用 `mcp__plugin_salesforce-development_salesforce-lsp__complete_soql` 带部分查询来获取针对连接组织的对象、字段和关系名称的架构感知完成——这避免了猜测然后失败验证的 API 名称。出错信封或不可用（`{error: <code>}` / 工具未注册），跳过完成并依赖 `references/soql-syntax-reference.md` 中的语法参考。

当查询已经存在于 Apex 类中（优化或调试嵌入的 SOQL 而不是编写新的）时，使用 `.cls` 文件调用 `mcp__plugin_salesforce-development_salesforce-lsp__extract_soql_from_apex` 来提取 SOQL 字符串，然后再进行分析，以便优化类运行的精确查询。

### 2. 选择正确的查询形状
| 需求 | 默认模式 |
|---|---|
| 从子对象获取父数据 | 子到父遍历 |
| 从父对象获取子行 | 子查询 |
| 计数/汇总 | 聚合查询 |
| 带有/没有相关行的记录 | 半连接/反连接 |
| 跨对象文本搜索 | SOSL |

### 3. 使用 LSP 工具验证（必需）

**必需：** 在对组织运行 SOQL 查询或推荐用于生产使用之前：

1. **调用 `mcp__plugin_salesforce-development_salesforce-lsp__validate_soql`** 带查询字符串来检查语法并在执行前捕获解析错误。
   - 成功 (`{ok: true}`)，继续。**干净的解析不等于干净的查询。** `validate_soql` 仅是解析器——它接受目标组织中不存在的对象、字段和关系。成功解析意味着语法格式正确，**不意味着标识符解析成功。**
   - **对不确定结果采取封闭失败。** 如果调用超时、重试或结果不确定，**不要将其视为成功验证**——回退到步骤 2 并记录 `validate_soql=unavailable: timeout`。
   - 出错信封 (`{error: <code>}`)，记录 `validate_soql=unavailable: <code>` 并回退到步骤 2。
   - 不可用（工具未注册），记录 `validate_soql=unavailable: lsp_not_present` 并回退到步骤 2。

2. **验证标识符与组织架构（必需，即使解析成功）。** 在推荐之前，确认查询中的每个对象、字段和关系实际上都存在于目标组织中——一个格式正确的解析在不存在字段上必须不被报告为有效。
   - **权威检查——描述或有限探测。不要执行用户的完整查询来验证架构**（它可能是无界的并检索大量结果集）。相反：
     - **首选：** `sf sobject describe --sobject <Object> --target-org <org>` 对查询中的每个对象，并确认每个引用的字段/关系都出现在描述输出中。这使用无行检索解析标识符。
     - **替代：** 有限组织后端探测——通过 `sf data query --query "<bounded-query>" --json --target-org <org>` 重写具有 `LIMIT 0`（或对象的键 `LIMIT 1`）的相同查询。`LIMIT 0` 在服务器端验证每个标识符而不返回行；一个坏对象或字段作为 `INVALID_TYPE` / `INVALID_FIELD` 错误出现。
   - `mcp__plugin_salesforce-development_salesforce-lsp__complete_soql` 可用于起草时解析名称，但完成返回光标位置的候选者——不是每个标识符的验证结果——并且可以返回 `{ok: true, hint: "no_org_connected"}` 带占位符架构。**完成输出不充分验证架构：** 如果 `complete_soql` 返回 `no_org_connected` 或未解析每个标识符，回退到上述描述或有限探测检查。
   - **永远**不要因为验证检查未运行或仅解析就报告查询为有效——始终首先确认标识符与组织架构。

3. **对于生产查询**，还调用 `mcp__plugin_salesforce-development_salesforce-lsp__check_soql_selectivity` 在推荐查询用于高容量或计划使用前分析选择性启发式。
   - 出错信封或不可用，记录 `check_soql_selectivity=unavailable: <code>` 并注意未验证选择性。

4. **在部署架构更改后**，如果字段或对象引用在部署后立即失败验证，调用 `mcp__plugin_salesforce-development_salesforce-lsp__refresh_org_schema` 使缓存的组织描述失效，然后重新验证，然后再假设代码错误。

参考 `platform-lsp-integrate` 技能获取完整的 LSP 调用/回退合同和错误代码参考。

### 4. 针对选择性和安全性进行优化
检查：
- 索引/选择性过滤器
- 无需的字段
- 避免可用的通配符或扫描密集模式
- 安全执行预期

### 5. 如有必要，验证执行路径
如果用户需要运行时验证，将执行委托给：
- [platform-data-manage](../platform-data-manage/SKILL.md)

---

## 高信号规则

- 从不使用 `SELECT *` 风格的思考；仅查询所需字段
- 在 Apex 上下文中不在循环中查询
- 优先在 SOQL 中过滤，而不是在 Apex 中后过滤
- 使用聚合进行计数和分组摘要，而不是加载不必要记录
- 仔细评估通配符使用；前导通配符通常破坏索引
- 在查询移动到 Apex 时考虑安全模式/字段访问要求

---

## 输出格式

完成时按以下顺序报告：
1. **查询目的**
2. **最终 SOQL/SOSL**
3. **选择此形状的原因**
4. **优化或安全性说明**
5. **如需执行的建议**

建议形状——使用 `references/soql-syntax-reference.md` 获取精确语法：

```text
Query goal: <摘要>
Query: <soql or sosl>
Design: <关系/聚合/过滤选择>
Notes: <选择性、限制、安全性、管理员限制意识>
Next step: <在 platform-data-manage 中运行或在 Apex 中嵌入>
```

---

## 跨技能集成

| 需求 | 委托给 | 原因 |
|---|---|---|
| 对组织运行查询 | [platform-data-manage](../platform-data-manage/SKILL.md) | 执行和导出 |
| 在服务/选择器中嵌入查询 | [platform-apex-generate](../platform-apex-generate/SKILL.md) | 实现上下文 |
| 从日志分析慢查询症状 | [platform-apex-logs-debug](../platform-apex-logs-debug/SKILL.md) | 运行时证据 |
| 查询支持的 UI 线路 | [experience-lwc-generate](../experience-lwc-generate/SKILL.md) | 前端集成 |

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 90+ | 生产优化查询 |
| 80–89 | 良好查询，有微小改进空间 |
| 70–79 | 功能性但仍有性能问题 |
| < 70 | 在生产使用前需要修订 |

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `references/soql-syntax-reference.md` | 语法、运算符、日期字面量、关系查询模式 |
| `references/query-optimization.md` | 选择性规则、索引策略、管理员限制、安全模式 |
| `references/soql-reference.md` | 快速参考——运算符、日期函数、聚合函数、WITH 子句 |
| `references/anti-patterns.md` | 常见 SOQL 错误及其修复——在最终确定任何查询前阅读 |
| `references/selector-patterns.md` | Apex 选择器层模式——在将查询嵌入 Apex 类时阅读 |
| `references/field-coverage-rules.md` | 字段覆盖验证——在生成用于 Apex 代码内的 SOQL 时阅读 |
| `references/cli-commands.md` | sf CLI 查询执行、批量导出、查询计划命令 |
| `assets/basic-queries.soql` | 常见对象启动查询示例 |
| `assets/relationship-queries.soql` | 父到子以及子到父关系查询模式 |
| `assets/aggregate-queries.soql` | COUNT、SUM、GROUP BY、ROLLUP 查询模式 |
| `assets/optimization-patterns.soql` | 选择性过滤器和索引感知查询模式 |
| `assets/bulkified-query-pattern.cls` | 触发器上下文中的 Apex Map 基础批量查询模式 |
| `assets/selector-class.cls` | 完整选择器类实现模板 |
| `scripts/post-tool-validate.py` | 后写挂钩——在 `.soql` 文件编辑后运行静态 SOQL 验证和实时查询计划分析 |
