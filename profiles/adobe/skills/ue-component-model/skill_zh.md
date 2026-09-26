# Universal Editor 组件模型配置

这项技能帮助你创建或编辑三个控制 AEM Edge Delivery Services (EDS) 组件在 Universal Editor (UE) 中显示和行为方式的 JSON 配置文件：

1. **component-definition.json** — 在 UE 组件面板中注册组件
2. **component-models.json** — 为每个组件定义属性面板字段
3. **component-filters.json** — 控制组件可以放置的位置

## 何时使用

- 创建需要 UE 作者支持的新组件
- 添加/修改现有组件的属性面板字段
- 注册组件以便它出现在作者的组件面板中
- 设置具有子项的容器组件
- 添加组件变体/样式选项

## 工作流程

### 第 1 步：理解组件

在生成任何配置之前，阅读和分析：

1. **组件的 JS 文件** (`blocks/<name>/<name>.js`) — 理解 `decorate(block)` 函数期望的内容：
   - 它从组件 div 中读取什么？(图片、链接、文本、类)
   - 它期望扁平结构还是项目行？
   - 它是否使用 `block.querySelector('a')` (链接/URL)、`block.querySelector('picture')` (图片) 等？
   - 它是否检查 CSS 类/变体？

2. **组件的 CSS 文件** (`blocks/<name>/<name>.css`) — 查找特定于变体的样式。

3. **现有配置** — 检查是否已存在条目：
   - 在 `component-definition.json` 中搜索组件 ID
   - 在 `component-models.json` 中搜索模型 ID
   - 在 `component-filters.json` 中搜索 `section` 组件列表中的组件
   - 检查是否存在 `blocks/<name>/_<name>.json` 分布式配置文件

### 第 2 步：确定组件类型

根据 JS 分析：

- **简单组件**：一个组件具有自己的字段。大多数组件都是这种类型。
  - 示例：Hero、Embed — 单一模型，无子项

- **容器组件**：具有可重复的子项（卡片、幻灯片、选项卡）。
  - 指示：JS 遍历 `block.children` 或从行创建项
  - 需要：容器定义 + 项定义 + 过滤器

- **键值组件**：配置式组件（两列键值对）。
  - 指示：每个属性都是独立的，不是内容网格
  - 需要：在模板中包含 `"key-value": true`

### 第 3 步：设计模型字段

将组件的内容期望映射到组件模型字段。阅读 [references/field-types.md](references/field-types.md) 获取完整的字段类型参考。

**常见字段映射：**

| 组件期望... | 使用组件类型 | 备注 |
|-------------|--------------|------|
| 一个图片 | `reference` (name: `image`) | 与名为 `imageAlt` 的 `text` 字段配对 |
| 一个 URL/链接 | `aem-content` (name: `link` 或 `url`) | 用于页面链接和外部 URL |
| 富文本内容 | `richtext` | 用于带标题、列表、链接的格式化文本 |
| 单行纯文本 | `text` | 用于标题、标签、短字符串 |
| 多行纯文本 | `textarea` | 用于描述、注释、无格式的长文本 |
| 标题级别选择 | `select` 带有 h1-h6 选项 | 将其命名为 `titleType` 以自动与标题折叠 |
| 样式变体 | `multiselect` (name: `classes`) | 值成为组件 div 上的 CSS 类 |
| 多个开关 | `checkbox-group` | 用于多个独立的布尔选项 |
| 布尔开关 | `boolean` | 用于显示/隐藏选项 |
| 数值 | `number` | 用于计数、限制 |
| 内容片段 | `aem-content-fragment` | 用于 CF 驱动的组件 |
| 体验片段 | `aem-experience-fragment` | 用于可重用的内容和布局片段 |
| 内容标签 | `aem-tag` | 用于通过 AEM 标签选择器进行分类 |

**字段命名规则（语义折叠）：**
- `image` + `imageAlt` → 折叠为 `<picture><img alt="...">`
- `link` + `linkText` + `linkTitle` + `linkType` → 折叠为 `<a href="..." title="...">text</a>` 并带可选类
- `title` + `titleType` → 折叠为 `<h2>title</h2>` (级别来自 titleType)
- 以 `group_` 前缀（下划线分隔符）的字段被分组到一个单元格中

### 第 4 步：生成配置

为三个文件生成条目。方法取决于项目是否使用集中式或分布式配置。

**检查分布式配置模式**：如果组件目录包含 `_<blockname>.json` 文件（例如，`blocks/hero/_hero.json`），则创建分布式配置文件，而不是编辑中央文件。

#### 对于集中式配置（编辑三个根 JSON 文件）：

**component-definition.json** — 添加到 `"Blocks"` 组的 `components` 数组中：

```json
{
  "title": "<Block Display Name>",
  "id": "<block-id>",
  "plugins": {
    "xwalk": {
      "page": {
        "resourceType": "core/franklin/components/block/v1/block",
        "template": {
          "name": "<Block Name>",
          "model": "<model-id>"
        }
      }
    }
  }
}
```

对于容器组件，添加容器和项定义。容器使用 `"filter"` 而不是 `"model"`，项使用 `"core/franklin/components/block/v1/block/item"` 作为 resourceType。

对于键值组件，在模板中添加 `"key-value": true`。

模板可以包含任何模型字段的默认值（例如，`"titleType": "h3"`, `"classes": ["light"]`）。

**component-models.json** — 添加一个新的模型条目：

```json
{
  "id": "<model-id>",
  "fields": [
    {
      "component": "<field-type>",
      "name": "<property-name>",
      "label": "<Display Label>",
      "valueType": "string"
    }
  ]
}
```

**component-filters.json** — 将组件 ID 添加到 `section` 过滤器的 `components` 数组中。对于容器组件，还添加一个新的过滤条目来定义允许的子项。

#### 对于分布式配置（创建 `blocks/<name>/_<name>.json`）：

创建一个包含所有三个配置的单个文件：

```json
{
  "definitions": [ ... ],
  "models": [ ... ],
  "filters": [ ... ]
}
```

仍然在中央 `component-filters.json` 中将组件添加到 `section` 过滤器。

### 第 5 步：验证

生成配置后，验证：

1. **ID 一致性**：定义中的 `id` 与 `component-filters.json` 中使用的 `id` 匹配。`template.model` 值与 `component-models.json` 中的 `id` 匹配。
2. **过滤注册**：组件的 ID 出现在 `section` 过滤器的 `components` 数组中（否则作者无法将其添加到页面）。
3. **字段名与组件 JS 匹配**：模型字段中的 `name` 属性应生成组件的 `decorate()` 函数可以消费的 HTML。
4. **语义折叠**：配对字段使用正确的后缀（例如，`image`/`imageAlt`，而不是 `image`/`altText` 除非有意为之）。
5. **有效的 JSON**：编辑后三个文件仍然是有效的 JSON。
6. **无重复 ID**：模型或过滤 ID 不会与现有条目冲突。

## 参考文件

需要详细信息时，阅读这些参考文件：

- **[references/architecture.md](references/architecture.md)** — 三个文件如何连接、完整的 AEM→Markdown→HTML 管道、资源类型、字段命名约定、语义折叠规则和 RTE 过滤器配置
- **[references/field-types.md](references/field-types.md)** — 所有 17 个字段组件类型的完整参考 (`text`, `textarea`, `richtext`, `reference`, `aem-content`, `aem-content-fragment`, `aem-experience-fragment`, `aem-tag`, `select`, `multiselect`, `checkbox-group`, `radio-group`, `boolean`, `number`, `date-time`, `container`, `tab`), valueType 约束、必需属性、字段属性、验证类型、条件字段和选项格式
- **[references/examples.md](references/examples.md)** — 显示 Hero（简单）、Embed（简单带 URL）、卡片（容器）、Teaser（变体）、产品详情（键值）、文章（内容片段）、部分配置、元数据（textarea）、功能开关（checkbox-group）和 RTE 过滤器配置的真实示例

## 常见陷阱

- **忘记添加到 section 过滤器**：除非在 `section` 过滤器的组件列表中，否则组件不会出现在作者的添加菜单中。
- **错误的 resourceType**：几乎所有自定义组件都使用 `core/franklin/components/block/v1/block`。不要发明自定义资源类型。
- **模型/过滤 ID 不匹配**：`template.model` 必须与模型 `id` 完全匹配，`template.filter` 必须与过滤 `id` 完全匹配。
- **选择错误的文本字段类型**：使用 `text` 用于单行字符串，`textarea` 用于多行纯文本，`richtext` 用于格式化内容。对于 URL 和页面链接，使用 `aem-content` 以便作者使用内容选择器。
- **错误的 valueType**：大多数组件强制执行特定的 `valueType`（例如，`boolean` 必须使用 `"boolean"`，`number` 必须使用 `"number"`，`checkbox-group` 必须使用 `"string[]"`）。始终包含 `valueType` 并检查字段类型的参考以获取强制执行的值。
- **容器没有过滤**：容器组件需要在模板中有一个 `filter`（而不是 `model`），并且在 `component-filters.json` 中有一个相应的过滤条目。
