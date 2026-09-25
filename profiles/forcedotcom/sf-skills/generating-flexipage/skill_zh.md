## 何时使用此技能

当你需要执行以下操作时，请使用此技能：
- 创建 Lightning 页面（RecordPage、AppPage、HomePage）
- 生成 FlexiPage 元数据 XML
- 向现有的 FlexiPages 添加组件
- 排查 FlexiPages 部署错误
- 理解 FlexiPages 结构和组件配置
- 使用页面布局或 Lightning 页面自定义
- 编辑或更新任何 *.flexipage-meta.xml 文件

## 规格

# FlexiPage 生成指南

## 概述

**关键：创建新的 FlexiPages 时，你必须始终使用 CLI 模板命令。** 绝对不要从零开始创建 FlexiPage XML - CLI 提供有效的结构、正确的区域和正确的组件配置，可防止部署错误。

使用 CLI 引导生成 Lightning 页面（RecordPage、AppPage、HomePage），以便进行组件发现和配置。

---

## 快速入门工作流

### 第 1 步：使用 CLI 引导

**对于新页面：此步骤是强制性的，不可省略。** 创建新的 FlexiPage 时，始终使用 CLI 模板命令。CLI 生成有效的 XML 结构、正确的区域和正确的元数据，可防止常见的部署错误。只有当你正在编辑现有的 FlexiPage 文件时，才可以跳过此步骤。

```bash
sf template generate flexipage \
  --name <页面名称> \
  --template <RecordPage|AppPage|HomePage> \
  --sobject <对象> \
  --primary-field <字段1> \
  --secondary-fields <字段2,字段3> \
  --detail-fields <字段4,字段5,字段6,字段7> \
  --output-dir force-app/main/default/flexipages
```

**关键：** 如果 `sf template generate flexipage` 命令失败，**停止操作**。

1.  安装模板插件：
   ```bash
   sf plugins install templates
   ```
2.  重试 `sf template generate flexipage` 命令
3.  验证是否创建了 FlexiPage XML 文件

在模板命令成功之前，不要继续到第 2 步。整个工作流都需要生成的 XML。

#### **特定模板的要求**

**RecordPage:**
- 需要 `--sobject`（例如，Account、Custom_Object__c）
- 需要 字段参数：
  - `--primary-field`：最重要的标识字段（例如，Name）
  - `--secondary-fields`：记录摘要（建议 4-6 个，最多 12 个）
  - `--detail-fields`：完整的记录详细信息，包括必填字段（例如，Name）

**AppPage:**
- 无额外要求

**HomePage:**
- 无额外要求

#### **字段选择规则**
- **验证字段存在**：在使用 MCP 工具或 describe 命令发现对象的可用字段之前，不要在命令中指定它们
- **优先使用复合字段**：当可用时，使用 `Name`（而不是 `FirstName`/`LastName`）、`BillingAddress`（而不是 `BillingStreet`/`BillingCity`/`BillingState`）、`MailingAddress` 等
- **在 detail-fields 中包含必填字段**：始终在 `--detail-fields` 参数中包含对象必填字段（例如 `Name`），即使它们也用于 `--primary-field` 或 `--secondary-fields`

#### **你会得到**
- 具有正确结构的有效 FlexiPage XML
- 预配置的区域和基本组件
- 正确的字段引用和 facet 结构
- 可以直接部署或进一步增强

### 第 2 步：部署基础页面

运行整个项目的**干运行**部署，以验证页面和依赖项：
```bash
sf project deploy start --dry-run -d "force-app/main/default" --test-level NoTestRun --wait 10 --json
```

**关键：** 在继续之前修复任何部署错误。页面必须成功验证。

### 第 3 步：**停止 - 无进一步修改**

**强制要求：** 在第 2 步后停止。不要添加组件或编辑 FlexiPage XML。

即使用户请求：
- 额外的组件
- 页面自定义
- 组件配置

你可以做：
- 建议有用的组件
- 解释可能的增强功能
- 记录需要手动添加的内容

你不能做：
- 修改 XML 文件
- 添加任何组件
- 进行任何增强

---

## 关键 XML 规则

### 1. 属性值编码（最常见错误）

**任何包含 HTML/XML 字符的属性值必须按以下顺序手动编码**（顺序错误会导致双重编码损坏）：

```
1. & → &amp;   (首先！在编码其他内容之前编码此内容)
2. < → &lt;
3. > → &gt;
4. " → &quot;
5. ' → &apos;
```

**错误示例：**
```xml
<value><b>重要</b> 文本</value>
```

**正确示例：**
```xml
<value>&lt;b&gt;重要&lt;/b&gt; 文本</value>
```

**检查你的 XML：** 搜索 `<value>` 标签 - 它们不应包含原始 `<` 或 `>` 字符。

### 2. 字段引用

**始终：** `Record.{字段 API 名称}`  
**绝不：** `{对象名称}.{字段 API 名称}`

```xml
<!-- 正确 -->
<fieldItem>Record.Name</fieldItem>

        <!-- 错误 -->
<fieldItem>Account.Name</fieldItem>
```

### 3. 区域与 Facet 类型

**模板区域**（header、main、sidebar）：
```xml
<name>header</name>
<type>Region</type>
```

**组件 Facet**（内部插槽，如 fieldSection 列）：
```xml
<name>Facet-12345</name>
<type>Facet</type>
```

**规则：** 如果是模板区域名称 → `Region`。如果是组件插槽 → `Facet`。

### 4. fieldInstance 结构

每个 fieldInstance 需要：
```xml
<itemInstances>
   <fieldInstance>
      <fieldInstanceProperties>
         <name>uiBehavior</name>
         <value>none</value> <!-- none|readonly|required -->
      </fieldInstanceProperties>
      <fieldItem>Record.FieldName__c</fieldItem>
      <identifier>RecordFieldName_cField</identifier>
   </fieldInstance>
</itemInstances>
```

**规则：**
- 每个 fieldInstance 需要自己的 `<itemInstances>` 包装
- 必须有 `fieldInstanceProperties` 并包含 `uiBehavior`
- 使用 `Record.{字段}` 格式

### 5. 唯一标识符和区域名称（关键 - 防止重复错误）

**整个 FlexiPage 文件中，每个标识符和区域/facet 名称都必须唯一。**

**关键规则：**
- ❌ **绝对不要创建具有相同 `<name>` 的两个 `<flexiPageRegions>` 块**
- ✅ **如果多个组件属于同一 facet，将它们组合在一个具有多个 `<itemInstances>` 的区域中**
- ❌ **绝对不要重用相同的 `<identifier>` 值**
- ✅ **始终先读取整个文件，然后提取所有现有的标识符和名称**

**错误示例 - 这会导致重复名称错误：**
```xml
<!-- 第一个 detail 标签中的字段区域 -->
<flexiPageRegions>
   <itemInstances>
      <componentInstance>
         <identifier>flexipage_property_details_fieldSection</identifier>
         ...
      </componentInstance>
   </itemInstances>
   <name>detailTabContent</name>  <!-- ❌ 重复名称 -->
   <type>Facet</type>
</flexiPageRegions>

<!-- 第二个 detail 标签中的字段区域 -->
<flexiPageRegions>
   <itemInstances>
      <componentInstance>
         <identifier>flexipage_pricing_fieldSection</identifier>
         ...
      </componentInstance>
   </itemInstances>
   <name>detailTabContent</name>  <!-- ❌ 重复名称 - 部署失败 -->
   <type>Facet</type>
</flexiPageRegions>
```

**正确示例 - 将 itemInstances 组合在一个区域中：**
```xml
<!-- 同一个 detail 标签 facet 中的两个字段区域 -->
<flexiPageRegions>
   <itemInstances>
      <componentInstance>
         <identifier>flexipage_property_details_fieldSection</identifier>
         ...
      </componentInstance>
   </itemInstances>
   <itemInstances>
      <componentInstance>
         <identifier>flexipage_pricing_fieldSection</identifier>
         ...
      </componentInstance>
   </itemInstances>
   <name>detailTabContent</name>  <!-- ✅ 一个区域，多个组件 -->
   <type>Facet</type>
</flexiPageRegions>
```

**何时组合 vs 分离：**
- **组合**：逻辑上属于同一标签/区域的组件（例如，detail 标签中的多个字段区域）
- **分离**：属于不同标签/区域的组件（例如，`detailTabContent` vs `relatedTabContent`）

---

## 常见部署错误

### "我们无法检索或加载字段上的信息"

**原因：** 无效的字段 API 名称 - 字段不存在于对象上或拼写错误
**修复：** 使用 MCP 工具或 describe 命令发现有效字段，然后更新字段引用（见字段选择规则）

### "无效的字段引用"

**原因：** 使用了 `ObjectName.Field` 而不是 `Record.Field`
**修复：** 更改为 `Record.{FieldApiName}`

### "Element fieldInstance 重复"

**原因：** 一个 itemInstances 中有多个 fieldInstances
**修复：** 每个 fieldInstance 需要自己的 `<itemInstances>` 包装

### "缺少 fieldInstanceProperties"

**原因：** 未指定 uiBehavior
**修复：** 添加 `fieldInstanceProperties` 并包含 `uiBehavior`

### "未使用的 Facet"

**原因：** 定义了 facet 但未在任何组件中引用
**修复：** 删除 Facet 或在组件属性中引用它

### "XML 解析错误"

**原因：** 属性值中未编码的 HTML/XML
**修复：** 在所有 `<value>` 标签中手动编码 `<`、`>`、`&`、`"`、`'`

### "无法创建具有命名空间的组件"

**原因：** 页面名称无效（不要在页面名称中使用 `__c` 后缀）
**修复：** 使用 "Volunteer_Record_Page" 而不是 "Volunteer__c_Record_Page"

### "区域指定了父级不支持的模式"

**原因：** 向区域添加了 `<mode>` 标签
**修复：** 删除 `<mode>` 标签 - 标准区域不需要它们

---

### 生成唯一标识符

**关键：** 在生成任何新的标识符或 facet 名称之前，请遵循上述“关键 XML 规则”第 5 部分的规则。

**标识符生成算法**：
```
1. 从 XML 中提取所有现有的 <identifier> 和 <name> 值
2. 生成基本名称：{组件类型}_{上下文}
   示例："relatedList_contacts"、"richText_header"、"tabs_main"
3. 找到第一个可用数字：
   - 尝试 "{base}_1"
   - 如果存在，尝试 "{base}_2"、"{base}_3"，等等
   - 使用第一个可用的
```

**示例**：
- 第一个联系人相关列表：`relatedList_contacts_1`
- 第二个联系人相关列表：`relatedList_contacts_2`
- 头部中的富文本：`richText_header_1`
- 字段区域：`fieldSection_details_1`

**Facet 命名 - 两种模式**：

1. **命名 facet**（用于主要内容区域）：
   - `detailTabContent`（detail 标签内容）
   - `maintabs`（主标签容器）
   - `sidebartabs`（侧边栏标签容器）
   - 当 facet 代表有意义的内容区域时使用

2. **UUID facet**（用于内部结构）：
   - 格式：`Facet-{8hex}-{4hex}-{4hex}-{4hex}-{12hex}`
   - 示例：`Facet-66d5a4b3-bf14-4665-ba75-1ceaa71b2cde`
   - 用于字段区域列、嵌套容器、匿名插槽

**向现有文件添加组件时：**
- 检查目标 facet 名称是否已存在
- 如果存在：将新的 `<itemInstances>` 添加到该现有区域（见上述第 5 部分的详细信息）
- 如果不存在：创建具有唯一名称的新区域

---

### 区域选择

**从文件中解析区域** - 不要硬编码名称。模板不同：
- `flexipage:recordHomeTemplateDesktop` → `header`、`main`、`sidebar`
- `runtime_service_fieldservice:...` → `header`、`main`、`footer`
- 其他可能具有不同的区域名称

**默认放置**：目标区域的末尾（在最后一个 `<itemInstances>` 之后）

**插入模式**：
```xml
<flexiPageRegions>
   <name>main</name>  <!-- 或任何存在的区域名称 -->
   <type>Region</type>
   <itemInstances><!-- 现有组件 1 --></itemInstances>
   <itemInstances><!-- 现有组件 2 --></itemInstances>
   <itemInstances>
      <!-- 在此处插入新组件 -->
   </itemInstances>
</flexiPageRegions>
```

---

### 具有 Facet 的容器组件

像标签、手风琴、字段区域这样的组件需要 facets。

**模式**：
```xml
<!-- 1. 区域中的组件 -->
<flexiPageRegions>
   <itemInstances>
      <componentInstance>
         <componentName>flexipage:tabset2</componentName>
         <identifier>tabs_main_1</identifier>
         <componentInstanceProperties>
            <name>tabs</name>
            <value>tab1_content</value>
            <value>tab2_content</value>
         </componentInstanceProperties>
      </componentInstance>
   </itemInstances>
   <name>main</name>
   <type>Region</type>
</flexiPageRegions>

        <!-- 2. Facets（区域同级，不是嵌套） -->
<flexiPageRegions>
<itemInstances><!-- Tab 1 内容 --></itemInstances>
<name>tab1_content</name>
<type>Facet</type>
</flexiPageRegions>

<flexiPageRegions>
<itemInstances><!-- Tab 2 内容 --></itemInstances>
<name>tab2_content</name>
<type>Facet</type>
</flexiPageRegions>
```

**关键**：Facet 区域是模板区域的同级兄弟，而不是嵌套在它们内部。
---
## 组件特定提示
### dynamicHighlights (RecordPage 头部)
**位置：** 必须在 `header` 区域。
**显式字段**（通过 CLI）：使用最重要的字段显示记录摘要。单个主字段用于标识记录，如名称。次要字段（最多 12 个，建议 6 个）用作记录摘要。
```bash
--primary-field Name
--secondary-fields Phone,Industry,AnnualRevenue
```
CLI 自动生成带有字段引用的 Facets。
### fieldSection
**用途：** 显示字段为列。
**结构：** 三级嵌套：
1. 模板区域（Region 类型）
2. 列 Facet（Facet 类型）
3. 字段 Facet（Facet 类型）
   **在组件属性中引用：**
```xml
<componentInstanceProperties>
   <name>columns</name>
   <value>Facet-{uuid}</value>
</componentInstanceProperties>
```

### rich Text 组件

组件名称：flexipage:richText

用途：显示支持文本格式、标题、列表、表格、图像、链接、表单和多媒体元素的 HTML 格式富文本内容。保留样式和布局。在默认文本中转义所有特殊字符。

位置：可用于任何页面类型（Home、Record、App、社区页面）的任何区域。

CLI 直接生成组件，无需嵌套结构。

用户："向 force-app/.../Account_Record_Page.flexipage-meta.xml 添加一个 rich text 组件"

结构：单级组件（无 facets）：
1. 组件实例（flexipage:richText）具有直接属性

XML 结构示例：
```xml
<itemInstances>
   <componentInstance>
      <componentInstanceProperties>
         <name>decorate</name>
         <value>true</value>
      </componentInstanceProperties>
      <componentName>flexipage:richText</componentName>
      <identifier>flexipage_richText</identifier>
   </componentInstance>
</itemInstances>
```

标识符模式：flexipage_richText 或 flexipage_richText_{序列}
---
## 必要的元数据结构

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

部署前：
- [ ] **[仅新页面]** 使用 CLI 引导 - 绝对不要从零开始创建 FlexiPage XML
- [ ] **所有标识符都是唯一的** - 文件中没有任何重复的 `<identifier>` 值
- [ ] **所有区域/facet 名称都是唯一的** - `<flexiPageRegions>` 中没有重复的 `<name>` 值
- [ ] **同一 facet 中的多个组件已组合** - 一个区域具有多个 `<itemInstances>`，而不是具有相同名称的多个区域
- [ ] 所有字段引用使用 `Record.{字段}` 格式
- [ ] 每个fieldInstance都有 `fieldInstanceProperties` 并包含 `uiBehavior`
- [ ] 每个fieldInstance都在自己的 `<itemInstances>` 包装中
- [ ] 模板区域使用 `<type>Region</type>`
- [ ] 组件 facet 使用 `<type>Facet</type>`
- [ ] 属性值包含 HTML/XML 已手动编码
- [ ] 区域中没有 `<mode>` 标签
- [ ] 页面名称中没有 `__c` 后缀
- [ ] 每个Facet都由恰好一个组件属性引用

---

## CLI 命令快速参考

```bash
# RecordPage 带字段
sf template generate flexipage \
  --name Account_Custom_Page \
  --template RecordPage \
  --sobject Account \
  --primary-field Name \
  --secondary-fields Phone,Industry,AnnualRevenue \
  --detail-fields Street,City,State,Name,Phone,Email

# AppPage
sf template generate flexipage \
  --name Sales_Dashboard \
  --template AppPage \
  --label "Sales Dashboard"

# HomePage
sf template generate flexipage \
  --name Custom_Home \
  --template HomePage \
  --description "销售团队的定制首页"
```

**所有模板都支持：**
- `--output-dir`（默认：当前目录）
- `--api-version`（默认：最新）
- `--label`（默认：页面名称）
- `--description`
