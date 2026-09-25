## 何时使用此技能

当你需要执行以下操作时，请使用此技能：
- 创建 Lightning 页面（RecordPage、AppPage、HomePage）
- 生成 FlexiPage 元数据 XML
- 向现有的 FlexiPages 添加组件
- 排查 FlexiPages 部署错误
- 理解 FlexiPages 结构和组件配置
- 处理页面布局或 Lightning 页面自定义
- 编辑或更新任何 *.flexipage-meta.xml 文件

## 规格

## 概述

**关键：** 创建新的 FlexiPages 时，你必须始终使用 CLI 模板命令。切勿从头开始创建 FlexiPage XML —— CLI 提供有效的结构、正确的区域和正确的组件配置，以防止部署错误。

使用 CLI 引导生成 Lightning 页面（RecordPage、AppPage、HomePage），用于组件发现和配置。

---

## 快速入门工作流

### 第 1 步：使用 CLI 引导

**对于新页面：此步骤是强制性的，不可省略。** 创建新的 FlexiPage 时，始终使用 CLI 模板命令。CLI 生成有效的 XML 结构、正确的区域和正确的元数据，以防止常见的部署错误。只有当你正在编辑现有的 FlexiPage 文件时，才能跳过此步骤。

**`<packageDirectory>`** = `sfdx-project.json` 中的 `path` 值 → `packageDirectories[0]`（例如，`force-app`）。在运行命令之前，从项目文件中读取它。

```bash
sf template generate flexipage \
  --name <PageName> \
  --template <RecordPage|AppPage|HomePage> \
  --sobject <SObject> \
  --primary-field <Field1> \
  --secondary-fields <Field2,Field3> \
  --detail-fields <Field4,Field5,Field6,Field7> \
  --output-dir <packageDirectory>/main/default/flexipages
```

**关键：** 如果 `sf template generate flexipage` 命令失败，**停止**。

1.  安装模板插件：
   ```bash
   sf plugins install templates
   ```
2.  重试 `sf template generate flexipage` 命令
3.  验证 FlexiPage XML 文件是否已创建

在模板命令成功之前，不要继续到第 2 步。整个工作流都需要生成的 XML。

#### **特定于模板的要求**

**RecordPage：**
- 需要 `--sobject`（例如，Account、Custom_Object__c）
- 需要 字段参数：
  - `--primary-field`：最重要的标识字段（例如，Name）
  - `--secondary-fields`：记录摘要（建议 4-6 个，最多 12 个）
  - `--detail-fields`：完整的记录详细信息，包括必需字段（例如，Name）

**AppPage：**
- 没有其他要求

**HomePage：**
- 没有其他要求

#### **字段选择规则**
- **验证字段是否存在**：使用 MCP 工具或 describe 命令在指定它们之前发现对象的可用字段
- **优先使用复合字段**：使用 `Name`（而不是 `FirstName`/`LastName`）、`BillingAddress`（而不是 `BillingStreet`/`BillingCity`/`BillingState`）、`MailingAddress` 等，如果可用
- **在 detail-fields 中包含必需字段**：始终在 `--detail-fields` 参数中包含对象必需字段（例如 `Name`），即使它们也用于 `--primary-field` 或 `--secondary-fields`

#### **你会得到**
- 具有正确结构的有效 FlexiPage XML
- 预配置的区域和基本组件
- 正确的字段引用和 facet 结构
- 可以直接部署或进一步增强

### 第 2 步：部署基础页面

运行 **干运行** 部署以验证页面和依赖项（使用 `sfdx-project.json` 中的默认包目录）：
```bash
sf project deploy start --dry-run -d "<packageDirectory>/main/default" --test-level NoTestRun --wait 10 --json
```

**关键：** 在继续之前修复任何部署错误。页面必须成功验证。

### 第 3 步：动态添加组件（如果需要）

基础页面成功部署后，如果用户需要额外的组件，请按照以下 **动态添加组件** 工作流进行操作。所有组件的添加都必须通过发现和推理管道——不要仅凭记忆编写组件 XML。

---

## 关键 XML 规则

**阅读 `references/xml_rules.md`** 以了解所有 XML 编码规则、字段引用格式、区域/facet 类型、fieldInstance 结构、唯一标识符要求以及常见部署错误解决方案。

**关键规则（快速提醒）：**
- 在 `<value>` 标签中编码 HTML：首先编码 `&`，然后是 `<`、`>`、`"`、`'`
- 字段引用：`Record.{FieldApiName}`（绝不能是 `Object.Field`）
- 每个 `<identifier>` 和区域 `<name>` 在整个文件中必须唯一
- 同一 facet 中的多个组件 → 在一个区域中使用多个 `<itemInstances>` 组合

---

### 标识符、区域和容器

**阅读 `references/identifiers_and_regions.md`** 以了解标识符生成算法、facet 命名模式（命名与 UUID）、区域选择规则和容器组件 facet 结构。

---

## 组件特定提示

### dynamicHighlights (RecordPage 头部)
**位置：** 仅 `header` 区域。有关完整结构，请参阅 `references/record_flexipage_dynamicHighlights.md`。
CLI 自动从 `--primary-field` 和 `--secondary-fields` 生成 Facets。

### fieldSection
**用于：** 以列形式显示字段。三级嵌套：区域 → 列 Facets → 字段 Facets。
有关完整结构和 XML 示例，请参阅 `references/flexipage_fieldSection.md`。
**关键：** `columns` 属性值是 Facet 名称，而不是数字。

### richText
有关编码规则和 XML 结构，请参阅 `references/flexipage_richText.md`。
标识符：`flexipage_richText` 或 `flexipage_richText_{N}`

---
## 必需的元数据结构

```xml
<FlexiPage xmlns="http://soap.sforce.com/2006/04/metadata">
   <flexiPageRegions>
      <!-- 区域和组件在此处 -->
   </flexiPageRegions>
   <masterLabel>页面标签</masterLabel>
   <template>
      <name>flexipage:recordHomeTemplateDesktop</name>
   </template>
   <type>RecordPage</type>
   <sobjectType>Object__c</sobjectType> <!-- RecordPage 仅 -->
</FlexiPage>
```

**页面类型：**
- `RecordPage` - 需要 `<sobjectType>`
- `AppPage` - 无 sobjectType
- `HomePage` - 无 sobjectType

---

## 验证清单

### 结构（新页面）
- [ ] 使用 CLI 引导——从不从头开始创建 FlexiPage XML

### 标识符 & 区域
- [ ] 所有 `<identifier>` 值在整个文件中唯一
- [ ] 所有区域/facet `<name>` 值在整个文件中唯一
- [ ] 同一 facet 中的多个组件组合在一个区域中，使用多个 `<itemInstances>`

### 字段实例
- [ ] 所有字段引用使用 `Record.{Field}` 格式
- [ ] 每个字段实例都有 `fieldInstanceProperties`，其中包含 `uiBehavior`
- [ ] 每个字段实例在其自己的 `<itemInstances>` 包装器中

### 类型 & 编码
- [ ] 模板区域使用 `<type>Region</type>`；组件 facet 使用 `<type>Facet</type>`
- [ ] 属性值包含 HTML/XML 时，进行实体编码
- [ ] 没有 `<mode>` 标签（仅在组件模式需要时使用）
- [ ] 页面名称中没有 `__c` 后缀
- [ ] 每个Facet正好由一个组件属性引用

---

## 快速参考：CLI 命令

**阅读 `references/cli_commands.md`** 以了解完整的 CLI 示例（RecordPage、AppPage、HomePage）和可用选项。

---

## 动态添加组件

> **强制工作流：** 所有 FlexiPage 的组件添加都必须遵循此工作流。不要从记忆中编写组件 XML 或跳过发现。这适用于标准 OOTB 组件、自定义 LWC 组件和任何其他组件类型。

### 概述

当用户请求组件（例如，“添加联系人的相关列表和报告”）时，请遵循此管道：

```text
1. 解析意图 → 识别所有请求的组件
2. 发现所有 → 批量组件通过三层发现
3. 推断属性 → 对每个发现的组件运行三步推断
4. 生成 XML → 一起生成所有组件的有效 XML
5. 验证 → 检查标识符、区域、属性完整性
```

**关键规则：** 首先批量发现所有组件（一次扫描，一次 MCP 调用），然后为每个组件推断属性。不要逐个组件调用发现步骤或交错发现和推断。

### 第 1 步：解析用户意图

从用户的话语中提取每个组件请求。示例：
- "创建带有报告和相关联系人的 Account 页面" → 2 个组件：报告、相关列表
- "添加活动、聊天和 Cases 的 DRL" → 3 个组件：活动、聊天、动态相关列表

### 第 2 步：三层组件发现

在进入下一层之前，对所有组件完成每一层：

| 层级 | 来源 | 何时 | 调用 |
|------|------|------|-------|
| **1** | 本地工作区扫描 | 总是第一个——对所有组件运行 | 0（仅本地） |
| **2** | `discoverUiComponents` MCP 操作 | 单个调用，用于所有在层级 1 后仍未解决的组件 | 1 |
| **3** | 生成新的 LWC 包 | 仅当组件在层级 2 后仍未解决且用户确认时 | 0 |

层级 1 完成后，收集所有未解决的组件，并在单个 MCP 调用中传递给层级 2。只有层级 2 后仍未解决的组件才会进入层级 3。

有关详细信息，请参阅下方的 **本地工作区扫描器** 和 **MCP 操作集成** 部分。

### 第 3 步：属性推断（每个组件）

对于每个发现的组件，使用三步策略推断属性：

1. **获取架构或读取源** — 对于层级 2（组织）组件，调用 `getUiComponentSchemas`；对于层级 1（本地），从源中提取 `@api` 属性
2. **应用组件指令** — 如果存在 `references/<name>.md`，则读取并遵循其推断规则
3. **解决剩余** — 智能默认值 → LLM 推断 → 用户提示（最后手段）

有关详细信息，请参阅下方的 **混合属性推断策略** 部分。

### 第 4 步：生成 XML

你不能做的事情：
- 修改 XML 文件中的顶层结构
- 从记忆中添加任何未通过三层组件发现解决的组件
- 进行任何增强

**在编写任何 XML 之前，请阅读 `references/xml_rules.md`。** 遵循那里定义的所有元素命名和结构规则。

为所有已解决的组件生成 `<itemInstances>` XML：
- 使用 `<componentInstanceProperties>` 为每个属性（不是 `<properties>`）
- 在整个集中分配唯一标识符（请参阅 `references/identifiers_and_regions.md`）
- 插入到适当的区域（header、main、sidebar 或 facets）
- 遵循每个组件的 XML 结构，从其指令文件或架构中获取

### 第 5 步：验证

检查完整的 FlexiPage，以验证以下内容：
- 标识符唯一性（整个文件中没有重复）
- 区域有效性（组件位于正确的区域）
- 属性完整性（所有必需属性都已填充）
- XML 编码（HTML 值必须进行实体编码）
- 元素名称正确性（请参阅 `references/xml_rules.md` §6）

使用默认包目录（来自 `sfdx-project.json`）进行干运行部署：
```bash
sf project deploy start --dry-run -d "<packageDirectory>/main/default" --test-level NoTestRun --wait 10 --json
```

---

## MCP 操作集成

**阅读 `references/mcp_action_examples.md`** 以了解完整的输入/输出示例和参数表。

通过 `execute_metadata_action` 进行两个 MCP 操作：

| 操作 | 目的 | 何时 |
|------|------|------|
| `DISCOVER_UI_COMPONENTS` | 查找页面类型的组件 | 层级 2 发现——单个调用，用于所有未解决的组件 |
| `GET_UI_COMPONENT_SCHEMAS` | 获取属性架构 | 属性推断步骤 1（仅层级 2 组织组件） |

**关键约定：**
- 组件定义格式：`namespace/blockName`（正斜杠）在 MCP 调用中，`namespace:blockName`（冒号）在 XML 中
- 需要 `pageContext` 与 `entityName`，用于 RECORD_PAGE
- `getUiComponentSchemas` 支持部分失败——检查每个组件的 `success` 布尔值

---

## 本地工作区扫描器

在执行任何 MCP 调用（层级 1 发现）之前，扫描本地 SFDX 项目中的自定义 LWC 组件。

### 算法

为每个组件查询运行扫描器（本地扫描——不进行网络调用）：

```bash
scripts/scan-lwc-components.sh "<query>" [packageDirectory]
```

脚本扫描 `<packageDirectory>/**/lwc/*/`，对 camelCase 组件名称进行分词，并根据用户意图关键字对其进行评分，然后返回一个包含置信度级别的 JSON 数组匹配项：

- **高置信度（≥70%）：** 自动选择，用户确认
- **中等置信度（40-69%）：** 向用户显示排名列表以供选择
- **低置信度（<40%）：** 跳过，进入层级 2

在将任何组件转移到层级 2 之前，对所有组件运行层级 1。收集所有层级 1 未解决的组件，然后将它们作为单个 MCP 调用传递给层级 2。

有关详细信息，请参阅下方的 **消歧义** 部分。

### 消歧义

对于中等置信度匹配（40-69%）或多个高置信度匹配：
1.  读取每个候选的 `.js-meta.xml` 中的 `<description>` 和 `<targetConfigs>`
2.  向用户显示排名列表，包括组件名称 + 描述
3.  用户选择或说“都不是”（→ 进入层级 2）

### 跳过条件

在以下情况下跳过本地扫描：
- 用户明确提到组织级组件（“使用标准报告组件”）
- 用户意图明确映射到已知标准组件（DRL、richText 等）
- 工作区中不存在 `<packageDirectory>` 目录

---

## 混合属性推断策略

对于每个发现的组件，按以下顺序使用此三步策略填充其属性：

### 第 1 步：获取最新架构（有条件）

仅当组件不在本地机器上（即层级 2 组织发现组件）时，调用 `getUiComponentSchemas`。对于本地组件（层级 1），直接从源代码中提取 `@api` 属性。

**调用条件：**
- 层级 2（组织发现）：始终——架构是属性信息的唯一来源
- 层级 1（本地）：跳过——从组件的 `.js` 源文件中读取 `@api` 属性
- 层级 3（生成）：跳过——你刚刚创建了源，所以属性已经已知

### 第 2 步：应用组件指令（如果存在）

运行 `scripts/resolve-component-instructions.sh <namespace:component>`——如果存在，则返回指令文件路径，否则为空字符串。

示例：
- `record_flexipage:dynamicHighlights` → `references/record_flexipage_dynamicHighlights.md`
- `flexipage:fieldSection` → `references/flexipage_fieldSection.md`
- `c:expenseTracker` → （空——没有文件）

如果返回文件：读取并遵循其推断规则、XML 模式和默认值。
如果为空：直接跳到第 3 步。

指令文件增强架构——它们提供如何从用户意图中导出值的*方法*。架构中未涵盖的任何属性将在第 3 步中解决。

### 第 3 步：解决剩余属性

对于尚未解决的任何属性，按以下优先级顺序应用：

**3a. 智能默认启发式算法：**

| 属性模式 | 默认值 |
|-----------------|---------------|
| `recordId` | `{!recordId}` |
| `objectApiName` / `sObjectName` | 页面的 `<sobjectType>` 值 |
| `show*` / `visible*` / `display*` | `true` |
| `hide*` / `hidden*` / `disabled*` | `false` |
| 布尔值不带前缀 | `false` |
| 架构指定 `"default"` | 使用架构默认值 |

**3b. LLM 推断：**
使用组件架构 + 用户意图 + 页面上下文推断合理的值。示例：用户说“显示顶级机会的报告”→ 推断 `reportName` 应该引用一个机会报告。

**3c. 用户提示（最后手段）：**
仅提示用户输入关键必需属性，这些属性无法推断。如果用户说“跳过”，则完全省略该组件。

### 层级特定行为

| 层级 | 额外步骤 | 架构调用 | 指令 |
|------|-----------|-------------|--------------|
| 层级 1（本地） | 从源中提取 `@api` 属性 | 否（使用源） | 如果存在 |
| 层级 2（组织） | — | 是 | 如果存在 |
| 层级 3（生成） | 从刚刚生成的源中提取 `@api` | 否（刚刚创建） | 无 |

---

## 新 LWC 生成（层级 3）

当本地（层级 1）和组织（层级 2）都找不到或用户拒绝了所有候选时，提供生成新的 LWC。

### 触发条件

- 层级 1 和层级 2 都错过或用户拒绝了所有候选
- 用户尚未明确说“跳过”或“不要创建”

### 确认

始终在创建之前确认。解释：组件名称。如果用户拒绝：跳过，继续处理其他组件。

### 生成后

创建 LWC 包后：
1. 立即将其视为层级 1 本地组件
2. 从生成的源中提取 `@api` 属性
3. 为 `recordId` 和 `objectApiName` 应用智能默认值
4. 使用 `c:{componentName}` 作为 `componentName` 生成 FlexiPage XML

### 命名约定

- 从用户意图派生：`customer health score` → `customerHealthScore`
- camelCase，无连字符，无下划线在 JS 类名中
- 文件夹名称与类名匹配（首字母小写）：`customerHealthScore/`

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `references/xml_rules.md` | 在编写或编辑任何 FlexiPage XML 之前——编码、字段引用、标识符、部署错误 |
| `references/identifiers_and_regions.md` | 添加组件时——标识符算法、facet 命名、区域选择、容器模式 |
| `references/cli_commands.md` | 引导新页面时——RecordPage、AppPage、HomePage 的完整 CLI 示例 |
| `references/mcp_action_examples.md` | 调用 MCP 操作时——discoverUiComponents 和 getUiComponentSchemas 的完整输入/输出 JSON |
| `references/flexipage_fieldSection.md` | 添加带有列的 Field Section 时 |
| `references/record_flexipage_dynamicHighlights.md` | 添加 Dynamic Highlights 面板时 |
| `references/flexipage_richText.md` | 添加 Rich Text 组件时 |
| `scripts/scan-lwc-components.sh` | 层级 1 本地工作区扫描——对 LWC 组件名称进行分词并评分，以匹配用户查询 |
| `scripts/resolve-component-instructions.sh` | 属性推断步骤 2——将组件定义解析为指令文件路径 |

**要添加新的组件模式：** 按照现有文件的结构创建 `references/<namespace>_<componentName>.md`。技能在工作流步骤 2 的属性推断期间自动检查该文件。

---

## 动态组件的验证规则

在为动态添加的组件生成 XML 后，在部署之前验证所有以下内容：

### 标识符唯一性
- 从整个 FlexiPage 文件中提取所有 `<identifier>` 值
- 确认没有重复
- 如果冲突：自动添加后缀（`_2`、`_3` 等）

### 区域有效性
- 组件放置在其类型的正确区域中：
  - `record_flexipage:dynamicHighlights` → 仅 `header`
  - `flexipage:fieldSection` → `main` 或 tab facets
  - `flexipage:richText` → 任何区域

### 属性完整性
- 所有架构中标记为必需的属性都有值
- 所有值匹配预期的类型（String、Boolean、valueList、Integer）
- `<value>` 标签中不包含原始 HTML（必须进行实体编码）

### 结构完整性
- 每个由组件属性引用的 Facet 都存在作为 `<flexiPageRegions>` 块
- 没有孤儿 Facet（每个 Facet 都正好由一个组件引用）
- 同一区域中的多个组件使用一个 `<flexiPageRegions>` 块和多个 `<itemInstances>`

### 跨组件一致性
- 对于多组件添加：所有新组件的标识符在整个文件中唯一
- 组件之间的 Facet UUID 不冲突
- 需要单例放置（dynamicHighlights、recordDetailPanelMobile）的组件不会重复
