# Salesforce 数据操作专家（platform-data-manage）

当用户需要进行 **Salesforce 数据工作** 时使用此技能：记录的增删改查、批量导入/导出、测试数据生成、清理脚本或用于验证 Apex、Flow 或集成行为的数据库工厂模式。

## 此技能负责任务的情况

当工作涉及以下内容时，使用 `platform-data-manage`：
- `sf data` CLI 命令
- 记录创建、更新、删除、upsert、导出或树形导入/导出
- 真实的测试数据生成
- 批量数据操作和清理
- 用于数据播种/回滚的 Apex 匿名脚本

当用户处于以下情况时，将任务委托给其他技能：
- 仅编写 SOQL → [platform-soql-query](../platform-soql-query/SKILL.md)
- 运行或修复 Apex 测试 → [platform-apex-test-run](../platform-apex-test-run/SKILL.md)
- 首先部署元数据 → [platform-metadata-deploy](../platform-metadata-deploy/SKILL.md)
- 创建或修改自定义对象/字段 → [platform-custom-object-generate](../platform-custom-object-generate/SKILL.md) 或 [platform-custom-field-generate](../platform-custom-field-generate/SKILL.md)

---

## 重要模式决策

确认用户希望使用哪种模式：

| 模式 | 使用场景 |
|---|---|
| 脚本生成 | 用户希望在尚未连接到组织的情况下生成可重用的 `.apex`、CSV 或 JSON 资产 |
| 远程执行 | 用户希望立即在真实组织中创建/修改记录 |

如果用户可能仅希望获取脚本，则**不要**假设远程执行。

---

## 首先收集的必要上下文

请求或推断：
- 目标对象
- 如果需要远程执行，请提供组织别名
- 操作类型：查询、创建、更新、删除、upsert、导入、导出、清理
- 预期数据量
- 这是否是测试数据、迁移数据或一次性故障排除数据
- 任何必须首先存在的父子关系

---

## 核心操作规则

- `platform-data-manage` 作用于**远程组织数据**，除非用户明确要求本地脚本生成。
- 在创建数据之前，对象和字段必须已存在。
- 对于自动化测试，当批量行为很重要时，优先选择**251+ 记录**。
- 在创建大型或嘈杂的数据集之前，计划清理操作——未跟踪的记录会跨运行累积并污染组织状态。
- 在测试记录中使用合成数据，而不是标识符——真实 PII 会产生合规风险，并且在批量导入后无法安全删除。
- 对于简单的 CRUD，优先选择**CLI 首选**；当操作确实需要服务器端编排时，使用匿名 Apex。

如果元数据缺失，停止并转交给：
- [platform-custom-object-generate](../platform-custom-object-generate/SKILL.md) 或 [platform-custom-field-generate](../platform-custom-field-generate/SKILL.md) 以创建缺失的架构，然后使用 [platform-metadata-deploy](../platform-metadata-deploy/SKILL.md) 部署它，然后重试数据操作

---

## 推荐工作流程

### 1. 验证先决条件
确认对象/字段的可用性、组织授权和所需的父记录。

### 2. 在架构不确定时运行 describe-first 预飞验证
在创建或更新记录之前，使用对象描述数据验证：
- 必填字段
- 可创建字段与不可创建字段
- 挑单值
- 关系字段和父记录要求

参考 [references/sf-cli-data-commands.md](references/sf-cli-data-commands.md) 了解 `sf sobject describe` 命令和用于检查字段、挑单值和可创建约束的 jq 过滤模式。

### 3. 选择最小的正确机制
| 需求 | 默认方法 |
|---|---|
| 小型一次性 CRUD | `sf data` 单记录命令 |
| 大型导入/导出 | 通过 `sf data ... bulk` 的批量 API 2.0 |
| 父子播种集 | 树形导入/导出 |
| 可重用测试数据集 | 工厂/匿名 Apex 脚本 |
| 可逆实验 | 清理脚本或基于保存点的方案 |

### 4. 执行或生成资产
在符合要求时使用内置模板：
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
4. 转换到不同的机制或提供手动解决方案

**不要**无限期地重复相同的失败命令。

### 7. 提供清理指导
每当创建数据时，提供确切的清理命令或回滚资产。

---

## 高信号规则

### 批量安全
- 对于大批量使用批量操作
- 在适当的情况下使用 251+ 记录测试自动化敏感行为
- 避免批量场景中的一条记录一次的模式

### 数据完整性
- 包含必填字段
- 在创建前验证挑单值
- 验证父 ID 和关系完整性
- 考虑验证规则和重复约束
- 从输入负载中排除不可创建字段

### 清理纪律
优先选择以下之一：
- 通过 ID 删除
- 通过模式删除
- 通过创建日期窗口删除
- 脚本测试运行的回滚/保存点模式

---

## 常见失败模式

| 错误 | 可能原因 | 默认修复方向 |
|---|---|---|
| `INVALID_FIELD` | 错误的字段 API 名称或 FLS 问题 | 验证架构和访问权限 |
| `REQUIRED_FIELD_MISSING` | 遗漏必填字段 | 从描述数据中包含必填值 |
| `INVALID_CROSS_REFERENCE_KEY` | 坏的父 ID | 首先创建/验证父记录 |
| `FIELD_CUSTOM_VALIDATION_EXCEPTION` | 验证规则阻止了记录 | 使用有效的测试数据或调整设置 |
| 无效的挑单值 | 猜测值而不是描述支持的值 | 首先检查挑单值 |
| 不可写入字段错误 | 字段不可创建/更新 | 从负载中移除它 |
| 批量限制/超时 | 工具不适用于数据量 | 切换到批量/分阶段导入 |

---

## 输出格式

完成时按以下顺序报告：
1. **执行的操作**
2. **对象和计数**
3. **目标组织或本地文件路径**
4. **记录 ID / 输出文件**
5. **验证结果**
6. **清理说明**

建议格式：

```text
数据操作：<创建 / 更新 / 删除 / 导出 / 播种>
对象：<对象 + 计数>
目标：<组织别名或本地路径>
资产：<记录 ID / CSV / Apex / JSON 文件>
验证：<通过 / 部分通过 / 失败>
清理：<确切的删除或回滚指导>
```

---

## 跨技能集成

| 需求 | 委托给 | 原因 |
|---|---|---|
| 创建缺失的自定义对象 | [platform-custom-object-generate](../platform-custom-object-generate/SKILL.md) | 架构必须在数据操作之前存在 |
| 创建缺失的自定义字段 | [platform-custom-field-generate](../platform-custom-field-generate/SKILL.md) | 字段级别的架构必须在数据创建之前存在 |
| 运行批量敏感的 Apex 验证 | [platform-apex-test-run](../platform-apex-test-run/SKILL.md) | 测试执行和覆盖率 |
| 首先部署缺失的架构 | [platform-metadata-deploy](../platform-metadata-deploy/SKILL.md) | 元数据就绪 |
| 实现消费数据的 Apex 逻辑 | [platform-apex-generate](../platform-apex-generate/SKILL.md) | Apex 类/触发器编写 |
| 实现消费数据的 Flow 逻辑 | [automation-flow-generate](../automation-flow-generate/SKILL.md) | Flow 编写和自动化 |

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

### 验证脚本
- [scripts/soql_validator.py](scripts/soql_validator.py) — 在执行前验证 SOQL 查询
- [scripts/validate_data_operation.py](scripts/validate_data_operation.py) — 数据操作的预飞检查（必填字段、挑单值、可创建字段）

### 资产模板
- `assets/factories/` — Apex 测试数据工厂脚本（账户、联系人、机会、潜在客户、用户等）
- `assets/bulk/` — 批量 API 2.0 Apex 模板（插入 200、500、10000 条记录；通过外部 ID upsert）
- `assets/cleanup/` — 清理和回滚脚本（按名称、日期、模式删除；事务回滚）
- `assets/soql/` — SOQL 查询模板（聚合、子查询、父到子、子到父、多态）
- `assets/csv/` — 账户、联系人、机会、自定义对象的 CSV 导入模板
- `assets/json/` — JSON 树形导入模板（账户-联系人、账户-机会、完整层次结构）

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 117+ | 强大的生产安全数据工作流 |
| 104–116 | 良好操作，但可能存在微小改进空间 |
| 91–103 | 可接受，但建议审查 |
| 78–90 | 存在部分/风险模式 |
| < 78 | 需要修正才能继续 |
