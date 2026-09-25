# sf-permissions

当用户需要**权限分析和访问审计**时使用此技能：权限集/权限集组层次结构视图，“谁可以访问 X？”的调查，用户权限分析或权限集元数据审查。

## 当此技能拥有任务时

当工作涉及以下内容时，使用 `sf-permissions`：
- 权限集/权限集组分析
- 用户访问调查
- 查找哪些权限授予对象/字段/Apex/流程/标签/自定义权限访问
- 审计或导出权限配置
- 审查权限元数据影响

当用户需要以下操作时，将其委派给其他技能：
- 创建新的元数据定义 → [sf-metadata](../sf-metadata/SKILL.md)
- 部署权限集 → [sf-deploy](../sf-deploy/SKILL.md)
- 分析 Apex 管理的共享逻辑 → [sf-apex](../sf-apex/SKILL.md)

---

## 首先收集所需的上下文

询问或推断：
- 目标组织的别名
- 问题是否关于对象、字段、Apex 类、流程、标签、自定义权限或特定用户
- 目标是否为层次结构可视化、访问检测、导出或元数据生成
- 输出是否应为终端导向或文档友好

---

## 推荐的工作流程

### 1. 分类请求
| 请求形状 | 默认能力 |
|---|---|
| “谁可以访问 X？” | 权限检测器 |
| “这个用户有什么权限？” | 用户分析器 |
| “显示给我层次结构” | 层次结构查看器 |
| “导出这个权限集” | 导出器 |
| “从分析中生成元数据” | 生成器或转交 |

### 2. 连接到正确的组织
在运行权限分析之前，验证 `sf` 身份验证。

### 3. 使用最窄的有用查询
除非用户明确要求全面审计，否则优先选择聚焦分析而非全组织扫描。

选择标识符时，优先使用稳定的元数据名称：
- `PermissionSet.Name`
- `PermissionSetGroup.DeveloperName`
- `CustomPermission.DeveloperName`
- 对象和字段 API 名称，如 `Account` 或 `Account.AnnualRevenue`
- `Assignee.Username` / 邮箱，用于以用户为中心的检查

仅在以下情况下使用 Salesforce 记录 ID：
- 底层对象模型需要 `ParentId` 或 `SetupEntityId`，或
- 您正在钻取同一调查中先前只读查询返回的记录

### 4. 清晰地呈现结果
使用：
- ASCII 树或表格输出用于终端工作
- 仅当文档收益明显时使用 Mermaid
- 简洁总结哪些权限源授予访问权限

### 5. 转交创建或部署工作
使用：
- [sf-metadata](../sf-metadata/SKILL.md) 用于更丰富的元数据生成
- [sf-deploy](../sf-deploy/SKILL.md) 用于部署

---

## 高信号规则

- 区分直接权限集授权和通过权限集组授权
- 优先使用 `Name` / `DeveloperName` / API 名称，而不是组织特定的记录 ID，用于初步调查查询
- 明确说明访问是对象级、字段级、类级、流程级或基于自定义权限的
- 在需要时使用 Tooling API 以便设置实体和高级可见性问题
- 对于代理访问问题，验证权限元数据中代理名称的精确匹配
- 当后续子查询需要 `ParentId` 或 `SetupEntityId` 时，从先前结果中解析 ID，而不是从复制的 ID 开始

---

## 输出格式

完成时，按以下顺序报告：
1. **分析了什么**
2. **组织/主题范围**
3. **哪些权限授予访问权限**
4. **访问是直接的还是继承的**
5. **建议的后续步骤**

建议形状：

```text
权限分析： <层次结构 / 检测 / 用户 / 导出>
范围： <组织，用户，权限目标>
发现： <权限集 / 组 / 访问级别>
来源： <直接分配或通过组>
下一步： <导出，生成元数据，或部署更改>
```

---

## 跨技能集成

| 需要 | 委托给 | 原因 |
|---|---|---|
| 生成或修改权限元数据 | [sf-metadata](../sf-metadata/SKILL.md) | 元数据编写 |
| 部署权限更改 | [sf-deploy](../sf-deploy/SKILL.md) | 推广 |
| 识别需要授权的 Apex 类 | [sf-apex](../sf-apex/SKILL.md) | 实施上下文 |
| 批量用户分配分析 | [sf-data](../sf-data/SKILL.md) | 大型数据操作 |

---

## 参考地图

### 从这里开始
- [references/permission-model.md](references/permission-model.md)
- [references/soql-reference.md](references/soql-reference.md)
- [references/workflow-examples.md](references/workflow-examples.md)

### 专业化分析
- [references/agent-access-guide.md](references/agent-access-guide.md)
- [references/usage-examples.md](references/usage-examples.md)

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 90+ | 强大的权限分析，具有清晰的访问来源 |
| 75–89 | 有用的审计，存在轻微差距 |
| 60–74 | 仅部分可见性 |
| < 60 | 证据不足；扩展分析 |
