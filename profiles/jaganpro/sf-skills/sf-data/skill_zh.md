# Salesforce 数据操作专家 (sf-data)

当用户需要 **Salesforce 数据工作** 时使用此技能：记录的创建、更新、删除、批量导入/导出、测试数据生成、清理脚本或用于验证 Apex、Flow 或集成行为的数据库工厂模式。

## 此技能负责任务的情况

当工作涉及以下内容时，使用 `sf-data`：
- `sf data` CLI 命令
- 记录的创建、更新、删除、upsert、导出或树形导入/导出
- 真实的测试数据生成
- 批量数据操作和清理
- 用于数据播种/回滚的 Apex 匿名脚本

当用户处于以下情况时，将任务委托给其他技能：
- 仅编写 SOQL → [sf-soql](../sf-soql/SKILL.md)
- 运行或修复 Apex 测试 → [sf-testing](../sf-testing/SKILL.md)
- 首先部署元数据 → [sf-deploy](../sf-deploy/SKILL.md)
- 发现模式/字段定义 → [sf-metadata](../sf-metadata/SKILL.md)

---

## 重要模式决策

确认用户想要哪种模式：

| 模式 | 使用场景 |
|---|---|
| 脚本生成 | 他们希望在尚未连接到组织的情况下生成可重用的 `.apex`、CSV 或 JSON 资产 |
| 远程执行 | 他们现在希望在真实组织中创建/修改记录 |

如果用户可能仅想要脚本，则不要假设远程执行。

---

## 首先收集的必要上下文

询问或推断：
- 目标对象
- 如果需要远程执行，则组织别名
- 操作类型：查询、创建、更新、删除、upsert、导入、导出、清理
- 预期数据量
- 这是否是测试数据、迁移数据或一次性故障排除数据
- 任何必须首先存在的父子关系

---

## 核心操作规则

- `sf-data` 作用于 **远程组织数据**，除非用户明确要求本地脚本生成。
- 在创建数据之前，对象和字段必须已经存在。
- 对于自动化测试，当批量行为很重要时，优先选择 **251+ 记录**。
- 在创建大型或嘈杂的数据集之前，始终考虑清理。
- 不要在生成的测试数据中使用真实 PII。
- 对于简单的 CRUD，优先选择 **CLI 首选**；当操作真正需要服务器端编排时，使用匿名 Apex。

如果元数据缺失，停止并将任务委托给：
- [sf-metadata](../sf-metadata/SKILL.md) 或 [sf-deploy](../sf-deploy/SKILL.md)

---

## 推荐的工作流程

### 1. 验证先决条件
确认对象/字段可用性、组织授权和所需的父记录。

### 2. 在模式不确定时运行描述优先的预飞验证
在创建或更新记录之前，使用对象描述数据来验证：
- 必填字段
- 可创建字段与不可创建字段
- 挑单值
- 关系字段和父记录要求

示例模式：
```bash
sf sobject describe --sobject ObjectName --target-org <alias> --json
```

有用的过滤器：
```bash
# 必填且可创建的字段
jq '.result.fields[] | select(.nillable==false and .createable==true) | {name, type}'

# 某个字段的合法挑单值
jq '.result.fields[] | select(.name=="StageName") | .picklistValues[].value'

# 创建时不可设置的字段
jq '.result.fields[] | select(.createable==false) | .name'
```

### 3. 选择最小的正确机制
| 需求 | 默认方法 |
|---|---|
| 小型一次性 CRUD | `sf data` 单记录命令 |
| 大型导入/导出 | 通过 `sf data ... bulk` 的批量 API 2.0 |
| 父子播种设置 | 树形导入/导出 |
| 可重用的测试数据集 | 工厂/匿名 Apex 脚本 |
| 可逆的实验 | 清理脚本或基于保存点的方案 |

### 4. 执行或生成资产
在它们适用时使用内置模板：
- `assets/factories/`
- `assets/bulk/`
- `assets/cleanup/`
- `assets/soql/`
- `assets/csv/`
- `assets/json/`

### 5. 验证结果
创建或更新后检查计数、关系和记录 ID。

### 6. 应用有界的重试策略
如果创建失败：
1. 尝试一次主要的 CLI 形式
2. 使用修正参数重试一次
3. 重新运行描述/验证假设
4. 转向不同的机制或提供手动解决方案

**不要** 无限重复相同的失败命令。

### 7. 提供清理指导
每当创建数据时，提供确切的清理命令或回滚资产。

---

## 高信号规则

### 批量安全
- 对于大批量，使用批量操作
- 在适当的情况下，使用 251+ 记录测试自动化敏感行为
- 避免批量场景中的一条记录一次的模式

### 数据完整性
- 包括必填字段
- 在创建之前验证挑单值
- 验证父 ID 和关系完整性
- 考虑验证规则和重复约束
- 从输入有效载荷中排除不可创建字段

### 清理纪律
优先选择以下之一：
- 通过 ID 删除
- 通过模式删除
- 通过创建日期窗口删除
- 脚本测试运行的回滚/保存点模式

---

## 常见失败模式

| 错误 | 可能的原因 | 默认修复方向 |
|---|---|---|
| `INVALID_FIELD` | 错误的字段 API 名称或 FLS 问题 | 验证模式和访问权限 |
| `REQUIRED_FIELD_MISSING` | 遗漏了必填字段 | 从描述数据中包含必填值 |
| `INVALID_CROSS_REFERENCE_KEY` | 坏的父 ID | 首先创建/验证父记录 |
| `FIELD_CUSTOM_VALIDATION_EXCEPTION` | 验证规则阻止了记录 | 使用有效的测试数据或调整设置 |
| 无效的挑单值 | 猜测值而不是基于描述的值 | 首先检查挑单值 |
| 不可写入字段错误 | 字段不可创建/更新 | 从有效载荷中移除它 |
| 批量限制/超时 | 工具不适合数据量 | 切换到批量/分阶段导入 |

---

## 输出格式

完成时，按以下顺序报告：
1. **执行的操作**
2. **对象和计数**
3. **目标组织或本地文件路径**
4. **记录 ID / 输出文件**
5. **验证结果**
6. **清理说明**

建议的格式：

```text
数据操作： <创建 / 更新 / 删除 / 导出 / 种子>
对象： <对象 + 计数>
目标： <组织别名或本地路径>
资产： <记录 ID / CSV / Apex / JSON 文件>
验证： <通过 / 部分通过 / 失败>
清理： <确切的删除或回滚指导>
```

---

## 跨技能集成

| 需求 | 委托给 | 原因 |
|---|---|---|
| 发现对象/字段结构 | [sf-metadata](../sf-metadata/SKILL.md) | 准确的模式基础 |
| 运行批量敏感的 Apex 验证 | [sf-testing](../sf-testing/SKILL.md) | 测试执行和覆盖 |
| 首先部署缺失的模式 | [sf-deploy](../sf-deploy/SKILL.md) | 元数据准备就绪 |
| 实现消费数据的生产行为 | [sf-apex](../sf-apex/SKILL.md) 或 [sf-flow](../sf-flow/SKILL.md) | 行为实现 |

---

## 参考地图

### 从这里开始
- [references/sf-cli-data-commands.md](references/sf-cli-data-commands.md)
- [references/test-data-best-practices.md](references/test-data-best-practices.md)
- [references/orchestration.md](references/orchestration.md)
- [references/test-data-patterns.md](references/test-data-patterns.md)
- [references/test-data-factory-usage.md](references/test-data-factory-usage.md)

### 查询 / 批量 / 清理
- [references/soql-relationship-guide.md](references/soql-relationship-guide.md)
- [references/relationship-query-examples.md](references/relationship-query-examples.md)
- [references/bulk-operations-guide.md](references/bulk-operations-guide.md)
- [references/cleanup-rollback-guide.md](references/cleanup-rollback-guide.md)
- [references/cleanup-rollback-example.md](references/cleanup-rollback-example.md)

### 示例 / 限制
- [references/crud-workflow-example.md](references/crud-workflow-example.md)
- [references/bulk-testing-example.md](references/bulk-testing-example.md)
- [references/anonymous-apex-guide.md](references/anonymous-apex-guide.md)
- [references/governor-limits-reference.md](references/governor-limits-reference.md)
- [assets/](assets/)

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 117+ | 强大的生产安全数据工作流程 |
| 104–116 | 良好操作，但可能存在小的改进空间 |
| 91–103 | 可接受但建议审查 |
| 78–90 | 存在部分/风险模式 |
| < 78 | 需要修正才能继续 |
