# sf-metadata：Salesforce 元数据生成和组织查询

当用户需要 **元数据定义或组织元数据发现** 时，请使用此技能：自定义对象、字段、验证规则、记录类型、页面布局、权限集，或使用 `sf` CLI 进行架构检查。

## 此技能负责任务的情况

当工作涉及以下内容时，请使用 `sf-metadata`：
- 对象、字段、验证规则、记录类型、布局、配置文件或权限集的元数据
- `.object-meta.xml`、`.field-meta.xml`、`.profile-meta.xml` 及相关元数据文件
- 在编码或流程工作之前描述架构
- 根据需求生成元数据 XML

当用户处于以下情况时，请将任务委托给其他技能：
- 分析权限访问而不是定义元数据 → [sf-permissions](../sf-permissions/SKILL.md)
- 部署元数据 → [sf-deploy](../sf-deploy/SKILL.md)
- 编辑流程 XML → [sf-flow](../sf-flow/SKILL.md)

---

## 收集初始所需上下文

询问或推断：
- 用户是否需要 **生成** 还是 **查询**
- 涉及的元数据类型
- 目标对象 / 字段 / 包目录
- 如果需要查询，请提供目标组织别名
- 新自定义对象或字段是否也应包括 **权限集 / FLS 生成**

除非用户明确选择退出，否则假设新自定义对象或字段需要权限集后续处理。

---

## 推荐工作流程

### 1. 选择模式
| 模式 | 使用场景 |
|---|---|
| 生成 | 用户需要新的或更新的元数据 XML |
| 查询 | 用户需要对象 / 字段 / 元数据发现 |

### 2. 从模板或 CLI 描述数据开始
对于生成，使用以下资源：
- `assets/objects/`
- `assets/fields/`
- `assets/permission-sets/`
- `assets/profiles/`
- `assets/record-types/`
- `assets/validation-rules/`
- `assets/layouts/`

对于查询，优先使用 `sf` 元数据和 `sobject describe` 命令。

在阅读旧示例时值得注意的近期 SDR/CLI 支持：`CnfgItemSourceDefinition`、`ExtlClntAppOauthSecuritySettings` 和 `UIBundle` 现在以其当前名称作为源支持。参见 [references/metadata-types-reference.md](references/metadata-types-reference.md)。

### 3. 验证元数据质量
检查：
- 命名规范
- 结构正确性
- 字段类型匹配
- 安全性 / FLS 影响
- 下游部署依赖

### 4. 默认规划权限影响
当创建新的自定义字段或对象时：
- 默认生成或更新权限集，除非用户选择退出
- 为 **符合条件的自定义字段** 包含 `fieldPermissions`
- 注意 Salesforce 将某些元数据类别视为系统管理或始终可用的，因此排除这些类别
- 记住，仅对象 CRUD **不会** 使自定义字段可见

### 5. 交接部署
当用户需要元数据部署时，使用 [sf-deploy](../sf-deploy/SKILL.md)。

---

## 高信号规则

- 字段级安全通常是部署后的隐藏障碍
- **对象权限 ≠ 字段权限**
- 优先使用权限集而不是以配置文件为中心的访问模式
- 默认为新的自定义对象和字段生成权限集后续处理
- 为符合条件的自定义字段包含 `fieldPermissions` 而不是将 FLS 作为事后考虑的手动操作
- 避免在公式或元数据逻辑中硬编码 ID
- 当操作上需要时，验证规则应有有意绕过策略
- 在尝试依赖它的流程或数据任务之前创建元数据

---

## 输出格式

完成时，按以下顺序报告：
1. **创建或查询的元数据**
2. **创建或更新的文件**
3. **关键架构/安全决策**
4. **权限 / 布局后续处理**
5. **部署下一步**

建议格式：

```text
元数据任务： <生成 / 查询>
项目： <对象、字段、规则、布局、权限集>
文件： <路径>
备注： <命名、字段类型、安全、依赖>
下一步： <部署、分配权限集或在 Setup 中验证>
```

---

## 跨技能集成

| 需求 | 委托给 | 原因 |
|---|---|---|
| 部署元数据 | [sf-deploy](../sf-deploy/SKILL.md) | 部署和验证 |
| 在新架构上构建流程 | [sf-flow](../sf-flow/SKILL.md) | 声明式自动化 |
| 在新架构上构建 Apex | [sf-apex](../sf-apex/SKILL.md) | 针对元数据编写代码 |
| 创建后分析权限访问 | [sf-permissions](../sf-permissions/SKILL.md) | 访问审计 |
| 部署后填充数据 | [sf-data](../sf-data/SKILL.md) | 测试数据创建 |

---

## 参考地图

### 从这里开始
- [references/field-and-cli-reference.md](references/field-and-cli-reference.md)
- [references/metadata-types-reference.md](references/metadata-types-reference.md)
- [references/naming-conventions.md](references/naming-conventions.md)
- [references/orchestration.md](references/orchestration.md)

### 安全 / 评分 / 示例
- [references/fls-best-practices.md](references/fls-best-practices.md)
- [references/permset-auto-generation.md](references/permset-auto-generation.md)
- [references/best-practices-scoring.md](references/best-practices-scoring.md)
- [references/field-types-guide.md](references/field-types-guide.md)
- [references/field-types-example.md](references/field-types-example.md)
- [references/custom-object-example.md](references/custom-object-example.md)
- [references/permission-set-example.md](references/permission-set-example.md)
- [references/profile-permission-guide.md](references/profile-permission-guide.md)
- [references/sf-cli-commands.md](references/sf-cli-commands.md)
- [assets/](assets/)

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 108+ | 强生产就绪的元数据 |
| 96–107 | 良好元数据，有少量审查项 |
| 84–95 | 可接受但需仔细验证 |
| < 84 | 阻止部署直到修正 |
