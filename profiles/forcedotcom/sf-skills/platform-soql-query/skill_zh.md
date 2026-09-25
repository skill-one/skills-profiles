# platform-soql-query: Salesforce SOQL 查询专家

当用户需要 **SOQL/SOSL 编写或优化** 时使用此技能：自然语言到查询的生成、关系查询、聚合、查询计划分析，以及 Salesforce 查询的性能/安全性改进。

## 此技能负责任务的情况

当工作涉及以下内容时，使用 `platform-soql-query`：
- `.soql` 文件
- 从自然语言生成查询
- 关系查询和聚合查询
- 查询优化和选择性问题分析
- SOQL/SOSL 语法和受限制设计

当用户执行以下操作时，将任务委托给其他技能：
- 执行批量数据操作 → [platform-data-manage](../platform-data-manage/SKILL.md)
- 在更广泛的 Apex 实现中嵌入查询逻辑 → [platform-apex-generate](../platform-apex-generate/SKILL.md)
- 通过日志而不是查询形状进行调试 → [platform-apex-logs-debug](../platform-apex-logs-debug/SKILL.md)

---

## 收集初始所需上下文

询问或推断：
- 目标对象
- 需要的字段
- 过滤条件
- 排序/限制要求
- 查询是用于显示、自动化、报表式分析还是 Apex 使用
- 是否已经关注性能/选择性

---

## 推荐工作流程

### 1. 生成最简单的正确查询
优先考虑：
- 仅需要字段
- 清晰的 WHERE 条件
- 适当情况下合理的 LIMIT
- 仅必要的关系深度

### 2. 选择正确的查询形状
| 需求 | 默认模式 |
|---|---|
| 从子对象获取父数据 | 子到父遍历 |
| 从父对象获取子行 | 子查询 |
| 计数/汇总 | 聚合查询 |
| 具有或不具有相关行的记录 | 半连接/反连接 |
| 跨对象文本搜索 | SOSL |

### 3. 优化选择性和安全性
检查：
- 索引/选择性过滤器
- 无需字段
- 无需的通配符或扫描密集型模式
- 安全性执行预期

### 4. 如有必要验证执行路径
如果用户需要运行时验证，将执行委托给：
- [platform-data-manage](../platform-data-manage/SKILL.md)

---

## 高信号规则

- 不要使用 `SELECT *` 式的思考；仅查询所需字段
- 在 Apex 上下文中不要在循环内查询
- 优先在 SOQL 中过滤，而不是在 Apex 中后过滤
- 使用聚合进行计数和分组摘要，而不是加载不必要的记录
- 仔细评估通配符使用；前导通配符通常会破坏索引
- 在查询进入 Apex 时考虑安全模式/字段访问要求

---

## 输出格式

完成时按以下顺序报告：
1. **查询目的**
2. **最终 SOQL/SOSL**
3. **选择此形状的原因**
4. **优化或安全性说明**
5. **执行建议（如需要）**

建议形状 — 使用 `references/soql-syntax-reference.md` 获取确切语法：

```text
Query goal: <摘要>
Query: <soql 或 sosl>
Design: <关系/聚合/过滤选择>
Notes: <选择性、限制、安全性、限制意识>
Next step: <在 platform-data-manage 中运行或在 Apex 中嵌入>
```

---

## 跨技能集成

| 需求 | 委托给 | 原因 |
|---|---|---|
| 对组织运行查询 | [platform-data-manage](../platform-data-manage/SKILL.md) | 执行和导出 |
| 将查询嵌入服务/选择器 | [platform-apex-generate](../platform-apex-generate/SKILL.md) | 实现上下文 |
| 从日志分析慢查询症状 | [platform-apex-logs-debug](../platform-apex-logs-debug/SKILL.md) | 运行时证据 |
| 连接基于查询的 UI | [experience-lwc-generate](../experience-lwc-generate/SKILL.md) | 前端集成 |

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 90+ | 生产优化的查询 |
| 80–89 | 良好查询，有微小改进空间 |
| 70–79 | 功能性但仍有性能问题 |
| < 70 | 在生产使用前需要修订 |

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `references/soql-syntax-reference.md` | 语法、运算符、日期字面量、关系查询模式 |
| `references/query-optimization.md` | 选择性规则、索引策略、限制、安全模式 |
| `references/soql-reference.md` | 快速参考 — 运算符、日期函数、聚合函数、WITH 子句 |
| `references/anti-patterns.md` | 常见 SOQL 错误及其修复 — 在最终确定任何查询前阅读 |
| `references/selector-patterns.md` | Apex 选择器层模式 — 在将查询嵌入 Apex 类时阅读 |
| `references/field-coverage-rules.md` | 字段覆盖验证 — 在生成用于 Apex 代码的 SOQL 时阅读 |
| `references/cli-commands.md` | sf CLI 查询执行、批量导出、查询计划命令 |
| `assets/basic-queries.soql` | 常见对象启动查询示例 |
| `assets/relationship-queries.soql` | 父到子和子到父关系查询模式 |
| `assets/aggregate-queries.soql` | COUNT、SUM、GROUP BY、ROLLUP 查询模式 |
| `assets/optimization-patterns.soql` | 选择性过滤和索引感知查询模式 |
| `assets/bulkified-query-pattern.cls` | 触发器上下文中基于 Apex Map 的批量查询模式 |
| `assets/selector-class.cls` | 完整选择器类实现模板 |
| `scripts/post-tool-validate.py` | 后写钩子 — 在 `.soql` 文件编辑后运行静态 SOQL 验证和实时查询计划分析 |
