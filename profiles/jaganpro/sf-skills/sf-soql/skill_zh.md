# sf-soql：Salesforce SOQL查询专家

当用户需要**SOQL/SOSL编写或优化**时使用此技能：自然语言到查询的生成、关系查询、聚合、查询计划分析，以及Salesforce查询的性能/安全性改进。

## 此技能负责任务的情况

当工作涉及以下内容时，使用`sf-soql`：
- `.soql`文件
- 从自然语言生成查询
- 关系查询和聚合查询
- 查询优化和选择性分析
- SOQL/SOSL语法和受治理器限制的设计

当用户执行以下操作时，将任务委托给其他技能：
- 执行批量数据操作 → [sf-data](../sf-data/SKILL.md)
- 在更广泛的Apex实现中嵌入查询逻辑 → [sf-apex](../sf-apex/SKILL.md)
- 通过日志而不是查询形状进行调试 → [sf-debug](../sf-debug/SKILL.md)

---

## 首先收集所需的上下文

请求或推断：
- 目标对象
- 需要的字段
- 过滤条件
- 排序/限制要求
- 查询是用于显示、自动化、报表式分析还是Apex使用
- 是否已经关注性能/选择性

---

## 推荐的工作流程

### 1. 生成最简单的正确查询
优先考虑：
- 仅需要字段
- 清晰的WHERE条件
- 适当时的合理LIMIT
- 仅必要的关系深度

### 2. 选择正确的查询形状
| 需求 | 默认模式 |
|---|---|
| 从子对象获取父数据 | 子到父的遍历 |
| 从父对象获取子行 | 子查询 |
| 计数/汇总 | 聚合查询 |
| 具有或不具有相关行的记录 | 半连接/反连接 |
| 跨对象文本搜索 | SOSL |

### 3. 优化选择性和安全性
检查：
- 索引/选择性过滤器
- 无需的字段
- 避免不必要的通配符或扫描密集型模式
- 安全性执行预期

### 4. 如有必要，验证执行路径
如果用户需要运行时验证，将执行委托给：
- [sf-data](../sf-data/SKILL.md)

---

## 高信号规则

- 不要使用`SELECT *`风格的思维；仅查询所需字段
- 在Apex上下文中不要在循环内查询
- 优先在SOQL中进行过滤，而不是在Apex中进行后过滤
- 使用聚合进行计数和分组摘要，而不是加载不必要记录
- 仔细评估通配符使用；前导通配符通常会破坏索引
- 在查询进入Apex时考虑安全模式/字段访问要求

---

## 输出格式

完成时按以下顺序报告：
1. **查询目的**
2. **最终SOQL/SOSL**
3. **选择此形状的原因**
4. **优化或安全性说明**
5. **执行建议（如果需要）**

建议形状：

```text
Query goal: <摘要>
Query: <soql或sosl>
Design: <关系/聚合/过滤选择>
Notes: <选择性、限制、安全性、治理器意识>
Next step: <在sf-data中运行或在Apex中嵌入>
```

---

## 跨技能集成

| 需求 | 委托给 | 原因 |
|---|---|---|
| 在组织中运行查询 | [sf-data](../sf-data/SKILL.md) | 执行和导出 |
| 将查询嵌入服务/选择器 | [sf-apex](../sf-apex/SKILL.md) | 实现上下文 |
| 从日志分析慢查询症状 | [sf-debug](../sf-debug/SKILL.md) | 运行时证据 |
| 连接基于查询的UI | [sf-lwc](../sf-lwc/SKILL.md) | 前端集成 |

---

## 参考地图

### 从这里开始
- [references/soql-syntax-reference.md](references/soql-syntax-reference.md)
- [references/query-optimization.md](references/query-optimization.md)
- [references/cli-commands.md](references/cli-commands.md)

### 专门指导
- [references/soql-reference.md](references/soql-reference.md)
- [references/anti-patterns.md](references/anti-patterns.md)
- [references/selector-patterns.md](references/selector-patterns.md)
- [references/field-coverage-rules.md](references/field-coverage-rules.md)
- [assets/](assets/)

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 90+ | 生产优化的查询 |
| 80–89 | 良好查询，有微小改进空间 |
| 70–79 | 功能性但仍有性能问题 |
| < 70 | 在生产使用前需要修订 |
