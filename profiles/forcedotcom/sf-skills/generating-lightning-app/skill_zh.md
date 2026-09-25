# 生成闪电应用

## 概述

通过定义闪电自定义应用并按正确的依赖顺序协调其依赖的元数据类型，从自然语言描述构建一个完整、可部署的 Salesforce Lightning Experience 应用程序。在可用时调用专业元数据技能；在没有技能时直接生成元数据。

## 何时使用此技能

**使用场景：**

- 用户请求“闪电应用”或“端到端解决方案”
- 用户说“构建一个应用”、“创建一个应用程序”、“构建一个[类型]应用”（如项目管理、跟踪等）
- 工作成果是一个自定义应用（CustomApplication）以及支持性元数据，而不是孤立的单个对象、页面或标签

**应触发此技能的示例：**

- “构建一个具有任务、资源和供应对象的项目管理闪电应用”
- “创建一个用于跟踪车辆的 LEX 应用，包含闪电页面和权限集”
- “我需要一个具有多个对象和关系的太空站管理系统”
- “构建一个具有自定义闪电记录页面的员工入职闪电应用”

**不使用场景：**

- 创建单个元数据组件（应使用特定元数据技能）
- 排错或调试现有元数据
- 构建Salesforce Classic应用程序（非闪电体验）
- 用户仅请求一个对象、一个页面或一个权限集（没有其他内容）
- 用户只需要创建或配置应用容器（分组现有标签）；应使用 `generating-custom-application`

## 元数据类型注册表

此表格显示了闪电体验应用常用的哪些元数据类型、技能可用性以及 API 上下文要求。

| 元数据类型 | 技能名称 | API 上下文 | 使用规则 |
|------------|----------|------------|----------|
| **自定义对象** | `generating-custom-object` | `salesforce-api-context` | 必须加载技能 **且** 调用 API 上下文 |
| **自定义字段** | `generating-custom-field` | `salesforce-api-context` | 必须加载技能 **且** 调用 API 上下文 |
| **自定义标签** | `generating-custom-tab` | `salesforce-api-context` | 必须加载技能 **且** 调用 API 上下文 |
| **FlexiPage** | `generating-flexipage` | `salesforce-api-context` | 必须加载技能 **且** 调用 API 上下文 |
| **自定义应用** | `generating-custom-application` | `salesforce-api-context` | 必须加载技能 **且** 调用 API 上下文 |
| **列表视图** | `generating-list-view` | `salesforce-api-context` | 必须加载技能 **且** 调用 API 上下文（如果请求） |
| **验证规则** | `generating-validation-rule` | `salesforce-api-context` | 必须加载技能 **且** 调用 API 上下文（如果请求） |
| **流程** | `generating-flow` | `metadata-experts` 管道 | 必须加载技能 **且** 运行管道。**豁免 `salesforce-api-context`**。 |
| **权限集** | `generating-permission-set` | `salesforce-api-context` | 必须加载技能 **且** 调用 API 上下文 |

### 使用规则

**技能规则**：当一个技能存在用于某个元数据类型时，你必须**加载该技能**。在加载技能之前**不能直接生成元数据**。

**API 上下文规则**：对于每个元数据类型（流程除外），你必须**调用 `salesforce-api-context` 工具**后再生成。在调用 API 上下文之前**不能生成元数据**。技能提供结构和规则；API 上下文确认当前 API 版本下的有效性。两者都至关重要。

**回退规则**：当没有技能存在用于你需要的元数据类型时，使用你对 Salesforce 元数据 API 和最佳实践的了解直接生成元数据。仍然需要 API 上下文。

**原因**：技能包含经过验证的模式和约束。API 上下文提供版本特定的准确性。两者结合可以防止部署失败。

---

## 依赖图 & 构建顺序

### 第一阶段：数据模型（基础）

```
自定义对象（无依赖）
    ↓
自定义字段（依赖：对象存在）
    ↓
关系（依赖：父对象和子对象 + 字段存在）
```

**此阶段的元数据类型：**

1. `generating-custom-object` - 一次，包含所有对象
2. `generating-custom-field` - 一次，包含所有字段（包括主从、查找、汇总字段）

### 第二阶段：业务逻辑（可选 - 仅在请求时）

```
验证规则（依赖：字段存在）
    ↓
流程（依赖：对象、字段存在）
```

**此阶段（仅如果用户请求）的元数据类型：**

1. `generating-validation-rule` - 一次，如果提及验证需求
2. `generating-flow` - 一次，如果提及自动化/工作流需求

### 第三阶段：用户界面

```
列表视图（依赖：对象、字段存在）
    ↓
自定义标签（依赖：对象存在）
    ↓
FlexiPages（依赖：对象、标签存在）
```

**此阶段的元数据类型：**

1. `generating-list-view` - 一次，用于过滤记录视图（如果请求）
2. `generating-custom-tab` - 一次，包含所有对象标签
3. `generating-flexipage` - 一次，包含所有记录/主页/应用页面

### 第四阶段：应用组装

```
自定义应用（依赖：标签存在）
```

**此阶段的元数据类型：**

1. `generating-custom-application` - 一次，创建闪电应用容器

### 第五阶段：安全 & 访问

```
权限集（依赖：对象、字段、标签、应用存在）
```

**此阶段的元数据类型：**

1. `generating-permission-set` - 一次，包含所有权限集和访问权限：
   - 对象（读取、创建、编辑、删除）
   - 字段（读取、编辑）
   - 标签（可见）
   - 自定义应用（可见）

---

## 执行工作流

### 第一步：需求分析 & 规划

**操作：**

1. 解析用户的自然语言请求
2. 提取业务实体（成为自定义对象）
3. 提取属性/属性（成为自定义字段）
4. 识别关系（主从、查找）
5. 检测验证需求（成为验证规则）
6. 检测自动化需求（成为流程）
7. 识别用户角色（通知权限集）

**输出：构建计划**

生成一个结构化计划，列出：

```
闪电应用构建计划：[应用名称]

数据模型：
- 自定义对象：[列出对象名称]
- 自定义字段：[按对象分组列出]
- 关系：[列出主从和查找关系]

业务逻辑（如果适用）：
- 验证规则：[列出对象和规则名称]
- 流程：[列出流程名称和类型]

用户界面：
- 列表视图（如果请求）：[列出对象和视图名称]
- 自定义标签：[列出对象]
- FlexiPages：[列出页面名称和类型]
- 自定义应用：[应用名称]

安全：
- 权限集：[列出目的]

每类型执行（技能 + API 上下文）：
- CustomObject：加载 generating-custom-object + 调用 salesforce-api-context
- CustomField：加载 generating-custom-field + 调用 salesforce-api-context
- ValidationRule：加载 generating-validation-rule + 调用 salesforce-api-context（如果请求）
- Flow：加载 generating-flow + 运行 metadata-experts 管道（如果请求）
- ListView：加载 generating-list-view + 调用 salesforce-api-context（如果请求）
- CustomTab：加载 generating-custom-tab + 调用 salesforce-api-context
- FlexiPage：加载 generating-flexipage + 调用 salesforce-api-context
- CustomApplication：加载 generating-custom-application + 调用 salesforce-api-context
- PermissionSet：加载 generating-permission-set + 调用 salesforce-api-context

状态行（在文件写入前发出）：
- `type=<Type> skill=complete mcp=complete|unavailable mcp_tools=<tool-list|none>`
- 流程异常：`type=Flow skill=complete pipeline=complete`

依赖顺序：
1. 第一阶段：数据模型（对象 -> 字段）
2. 第二阶段：业务逻辑（验证规则 -> 流程）
3. 第三阶段：用户界面（列表视图 -> 标签 -> 页面）
4. 第四阶段：应用组装（应用）
5. 第五阶段：安全（权限集）
```

### 第二步：按类型执行

针对每个元数据类型，一次执行这四个步骤。完成当前类型的所有四个步骤后再移动到下一个类型。**不要跳过任何步骤**。

| 步骤 | 做什么 | 为什么 |
|------|-------|-------|
| **① 加载技能** | 搜索并读取每个类型的 SKILL.md | 提供你 XML 结构、所需元素、命名规则和验证约束 |
| **② 调用 API 上下文** | 使用一个或多个 `get_metadata_type_sections`、`get_metadata_type_context`、`get_metadata_type_fields`、`get_metadata_type_fields_properties`、`search_metadata_types` 调用 `salesforce-api-context` 工具 | 提供当前有效的值 — 允许的枚举值、必填与可选字段、此 API 版本的子类型。技能提供结构；API 上下文提供版本特定的准确性。 |
| **③ 记录状态** | 发出：`type=<Type> skill=complete mcp=complete\|unavailable mcp_tools=<tool-list\|none>` | 确认在写入任何文件之前尝试了这两个步骤，并记录使用的 API 上下文工具 |
| **④ 生成文件** | 生成此类型的所有文件，然后检查点 | 只有在完成 ①②③ 后。验证，然后移动到下一个类型。 |

**不要将 ① 和 ② 合并为一个操作，或在完成 ① 后跳过 ②。** 它们是独立的步骤，目的不同。在加载技能后，你可能觉得可以生成 — 先停下来做 ②。

如果 `salesforce-api-context` 在真实尝试后不可用，记录 `mcp=unavailable` 并仅使用技能知识生成。完全跳过 ② 是一个错误。

---

**1. 自定义对象**
- ① 加载技能：读取 `generating-custom-object` SKILL.md
- ② API 上下文：调用 `salesforce-api-context` for CustomObject
- ③ 状态：`type=CustomObject skill=complete mcp=complete|unavailable mcp_tools=<tool-list|none>`
- ④ 生成 + 检查点：生成所有自定义对象文件，然后继续到 #2

**2. 自定义字段**
- ① 加载技能：读取 `generating-custom-field` SKILL.md
- ② API 上下文：调用 `salesforce-api-context` for CustomField
- ③ 状态：`type=CustomField skill=complete mcp=complete|unavailable mcp_tools=<tool-list|none>`
- ④ 生成 + 检查点：生成所有自定义字段文件，然后继续到 #3

**3. 验证规则**（仅如果请求）
- ① 加载技能：读取 `generating-validation-rule` SKILL.md
- ② API 上下文：调用 `salesforce-api-context` for ValidationRule
- ③ 状态：`type=ValidationRule skill=complete mcp=complete|unavailable mcp_tools=<tool-list|none>`
- ④ 生成 + 检查点：生成所有验证规则文件，然后继续到 #4

**4. 流程**（仅如果请求）
- ① 加载技能：读取 `generating-flow` SKILL.md
- ② 管道：运行 `metadata-experts/execute_metadata_action` 3 步骤管道（豁免 `salesforce-api-context`）
- ③ 状态：`type=Flow skill=complete pipeline=complete`
- ④ 生成 + 检查点：通过管道生成所有流程文件，然后继续到 #5

**5. 列表视图**（仅如果请求）
- ① 加载技能：读取 `generating-list-view` SKILL.md
- ② API 上下文：调用 `salesforce-api-context` for ListView
- ③ 状态：`type=ListView skill=complete mcp=complete|unavailable mcp_tools=<tool-list|none>`
- ④ 生成 + 检查点：生成所有列表视图文件，然后继续到 #6

**6. 自定义标签**
- ① 加载技能：读取 `generating-custom-tab` SKILL.md
- ② API 上下文：调用 `salesforce-api-context` for CustomTab
- ③ 状态：`type=CustomTab skill=complete mcp=complete|unavailable mcp_tools=<tool-list|none>`
- ④ 生成 + 检查点：生成所有自定义标签文件，然后继续到 #7

**7. FlexiPages**
- ① 加载技能：读取 `generating-flexipage` SKILL.md
- ② API 上下文：调用 `salesforce-api-context` for FlexiPage
- ③ 状态：`type=FlexiPage skill=complete mcp=complete|unavailable mcp_tools=<tool-list|none>`
- ④ 生成 + 检查点：生成所有 FlexiPage 文件，然后继续到 #8

**8. 自定义应用**
- ① 加载技能：读取 `generating-custom-application` SKILL.md
- ② API 上下文：调用 `salesforce-api-context` for CustomApplication
- ③ 状态：`type=CustomApplication skill=complete mcp=complete|unavailable mcp_tools=<tool-list|none>`
- ④ 生成 + 检查点：生成自定义应用文件，然后继续到 #9

**9. 权限集**
- ① 加载技能：读取 `generating-permission-set` SKILL.md
- ② API 上下文：调用 `salesforce-api-context` for PermissionSet
- ③ 状态：`type=PermissionSet skill=complete mcp=complete|unavailable mcp_tools=<tool-list|none>`
- ④ 生成 + 检查点：生成所有权限集文件 — 所有类型完成

### 第三步：最终工件组装

所有阶段完成后，将输出整合为可部署结构。

---

## 输出

完成的构建产生：

1. **Salesforce DX 项目目录**，包含所有生成的元数据
   - 按标准 SFDX 结构组织：`force-app/main/default/`
2. **元数据文件** - 每个组件一个文件，按类型组织：

   ```
   force-app/main/default/
   ├── objects/              # 自定义对象 (.object-meta.xml)
   ├── fields/               # 自定义字段 (.field-meta.xml)
   ├── tabs/                 # 自定义标签 (.tab-meta.xml)
   ├── flexipages/           # 闪电页面 (.flexipage-meta.xml)
   ├── applications/         # 自定义应用 (.app-meta.xml)
   ├── permissionsets/       # 权限集 (.permissionset-meta.xml)
   ├── flows/                # 流程 (.flow-meta.xml) - 如果适用
   └── objects/.../validationRules/  # 验证规则 (.validationRule-meta.xml) - 如果适用
   ```

3. **部署清单** (`package.xml`)
   - 列出所有组件及其正确的 API 版本
   - 按元数据类型在依赖顺序中组织
   - 准备好 Salesforce CLI 部署或元数据 API 部署
4. **构建摘要报告** - 一个 markdown 文件，列出：
   - 每个创建的组件
   - 组件类型和 API 名称
   - 文件路径位置
   - 依赖关系
   - 任何警告或建议

**示例摘要结构：**

```
闪电应用构建完成：项目管理应用

METADATA 生成：
1 自定义对象
   - Project__c -> force-app/main/default/objects/Project__c/Project__c.object-meta.xml
   - Task__c -> force-app/main/default/objects/Task__c/Task__c.object-meta.xml
   - Resource__c -> force-app/main/default/objects/Resource__c/Resource__c.object-meta.xml

2 自定义字段
   - Project__c.Name -> force-app/main/default/objects/Project__c/fields/Name.field-meta.xml
   - Project__c.Status__c -> force-app/main/default/objects/Project__c/fields/Status__c.field-meta.xml
   [... 等等 ...]

3 自定义标签
   - Project__c -> force-app/main/default/tabs/Project__c.tab-meta.xml
   [... 等等 ...]

4 闪电记录页面
   - Project_Record_Page -> force-app/main/default/flexipages/Project_Record_Page.flexipage-meta.xml
   [... 等等 ...]

5 自定义应用
   - Project_Management -> force-app/main/default/applications/Project_Management.app-meta.xml

6 权限集
   - Project_Manager -> force-app/main/default/permissionsets/Project_Manager.permissionset-meta.xml
   - Project_User -> force-app/main/default/permissionsets/Project_User.permissionset-meta.xml

WARNINGS: 无

```

---

## 验证

在向用户展示完成的构建之前，验证跨组件完整性：

- [ ] **对象-标签覆盖**：每个自定义对象至少有一个自定义标签
- [ ] **关系完整性**：在关系中引用的每个自定义对象（父对象或子对象）都在构建中存在
- [ ] **页面中的字段引用**：在 FlexiPage 中引用的每个字段都在相应对象上存在
- [ ] **应用中的标签引用**：在自定义应用中引用的每个标签都已成功创建
- [ ] **权限集完整性**：权限集授予对所有生成的对象、字段、标签和应用的访问权限
- [ ] **无孤立组件**：没有没有对象的标签，没有没有对应标签的页面，没有没有标签的应用
- [ ] **部署清单完整性**：`package.xml` 包含所有生成的组件，并按正确的依赖顺序排列

**验证失败处理（类别 2）：**

- 如果验证失败，在构建摘要报告的 `VALIDATION WARNINGS` 部分包含失败的检查
- 这些是生成后的问题 — 不要阻止交付构建，但要清楚地传达需要手动审查或更正的内容
- 为每个失败的验证检查提供具体的修复步骤

**注意**：单个组件验证（保留字、名称长度、字段类型等）由专门的元数据技能处理，在此不需要重新验证。

---

## 错误处理

### 类别 1：停止并询问用户

如果用户请求过于模糊无法提取任何对象或字段，或检测到冲突要求（例如，“使其私有” + “每个人都应该看到它”），或检测到无效的 Salesforce 命名（如保留字 `Order`、`Group`），则停止执行并询问用户澄清。

### 类别 2：生成后警告（记录警告，继续）

如果跨组件验证检查失败（例如，FlexiPage 引用的字段不存在于对象上），或可选组件生成失败（例如，列表视图生成有轻微问题），或验证规则或流程有轻微输出问题，则记录警告并继续。

**警告模式：**

```
Warning: [组件类型] 生成遇到问题
    组件: [名称]
    问题: [描述]
    影响: [什么将无法工作]
    建议: [如何手动修复]
    继续处理剩余组件...
```

---

## 最佳实践

### 1. 始终遵循依赖顺序

不要将技能按顺序调用。字段需要对象，页面需要标签，应用需要标签。

### 2. 使用技能时可用

不要重新发明轮子。专门的技能具有字段特定的验证，可以防止部署错误。

### 3. 生成深思熟虑的默认值

当用户没有指定详细信息时：

- 使用文本名称字段用于人类实体
- 使用自动编号用于交易
- 启用搜索和报告用于用户界面对象
- 基于关系设置 sharingModel

### 4. 在构建前验证

检查：

- API 名称中的保留字
- 关系限制（每个对象最多 2 个主从）
- 名称长度限制
- 重复名称
