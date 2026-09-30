---
name: platform-widget-generate
description: 使用此技能来创建一个完整的 HXL WidgetBundle（UEM 主体 + schema.json + -meta.xml）。触发条件为：当用户请求任何主题、领域、功能或实体名词的组件、马赛克、片段、卡片或富 UI 界面时；提示仅命名实体或数据形状，而未调用 Lightning 类型、CLT 或 Apex 支持的类型。不触发条件为：提示明确说明“Lightning 类型”、“CLT”、“自定义 Lightning 类型”、“Apex 支持的类型”，或引用“@apexClassType/...”（请使用 platform-lightning-type-widget-coordinate）；为自定义 Lightning 类型创建自定义-LWC 渲染器（请使用 platform-custom-lightning-type-generate）；或仅编辑 LWC 组件。
---

# 生成 Widget Bundle

编写一个完整的 WidgetBundle：一个 UEM 树（`tile/widget`）、一个描述 Widget 输入契约的 JSON Schema，以及 `.uiwidget-meta.xml` 文件来注册该 Bundle。

## 使用此技能的场景

当用户要求一个 Widget、马赛克、片段或卡片式富 UI 表面时使用。不要使用此技能来生成自定义-LWC 渲染器或 Custom Lightning Type Bundle 中的 `renderer.json` 文件——这些属于 `platform-custom-lightning-type-generate`。

## 输入

- **`widgetName`** (必需) —— `camelCase` 标识符；将成为 `uiWidgets/` 下面的目录名。
- 一个 **形状** —— Widget 渲染的数据。没有形状，Widget 无法生成。形状有两种来源，按优先级顺序：
  1. **`lightningTypeSchema`** —— `{ path, apexClassFqn }` 用于现有的 Apex 支持的 Lightning Type。FQN 有两种形式：外类（`<namespace>__<ClassName>`）其中外类是有效负载，或内类（`<namespace>__<ClassName>$<InnerClass>`）其中命名的内类是有效负载。由 `platform-lightning-type-widget-coordinate` 协调器传递。当存在时，根据 `references/schema-from-lightning-type.md` 推导。
  2. 从用户提示中提取——当未传递 `lightningTypeSchema` 时，直接从用户写入的内容中推断形状：粘贴的 JSON 负载、枚举的字段列表（"id as string, total as number"）或描述性文字。输出是相同顺序的 `{ name, type, required }` 列表。

如果两种来源都没有产生形状，则停止并询问用户再继续。

## 输出

`<pkgDir>/uiWidgets/<widgetName>/` 中的三个文件：

| 文件 | 内容 |
|---|---|
| `<widgetName>.json` | Widget 封装——`{ "type": "lightning__agentforceWidget", "contentBody": { "widgetBody": { UEM 树以 tile/widget 为根 } } }` |
| `schema.json` | JSON Schema——根有 `type: "object"` + `properties.attributes` 包装，其中包含 `lightning:type: "lightning__objectType"` 和字段 `properties` |
| `<widgetName>.uiwidget-meta.xml` | `<UiWidgetBundle>` 元素，包含 `<masterLabel>`、`<description>` 和 `<widgetType>JSON</widgetType>` |

有关 `<pkgDir>` 解析过程和确切的 `<widgetName>.uiwidget-meta.xml` 形状的详细信息，请参阅 `references/widget-bundle-layout.md`。

---

## 组成

Widget 身体是一个 UEM 树，嵌套在 `contentBody.widgetBody` 下。根节点是 `tile/widget`。每个节点——根节点和非根节点——具有相同的形状：没有 `type` 键；只有 `definition`、可选的 `attributes`、可选的 `meta` 和可选的 `children`。块形状：

```ts
interface Block {
  definition: string  // {namespace}/{blockName} — 根是 "tile/widget"
  attributes?: Record<string, any>
  meta?: { // see references/widget-meta-directives.md
    forEach?: string
    forItem?: string
    if?: string
  }
  children?: Block[]
}
```

`tile/widget.children` 的第一个子节点应该是单个 `tile/column`。所有 Widget 内容通常放在第一个子节点中，以在各个表面上实现可预测的垂直结构。

---

## 可用的元数据操作

### discoverUiComponents

**目的：** 发现可用于组成的组件面板。

**必需参数：** `actionName: "discoverUiComponents"`，`metadataType: "FRAGMENT"`，`parameters.pageType: "FRAGMENT"`。可选：`searchQuery` 以按名称/描述过滤。

**返回：** `{ definition, description, label, attributes? }` 列表。

### getUiComponentSchemas

**目的：** 获取选定块的 JSON Schema（属性类型、必需与可选、验证）。

**必需参数：** `actionName: "getUiComponentSchemas"`，`metadataType: "FRAGMENT"`，`parameters.pageType: "FRAGMENT"`，`parameters.componentDefinitions: ["namespace/definition", ...]`。可选：`includeKnowledge`（默认 `true`）。

**返回：** `componentSchemas[]`——成功条目包含 JSON Schema，失败条目包含错误消息。支持部分失败。

> 永远不要将 `tile/widget` 传递给 `getUiComponentSchemas`——它是一个固定的包装器，不是可查询的组件。

---

## 属性绑定

- 使用 `{!$attrs.<attrName>}` 将块属性绑定到运行时数据。`<attrName>` 必须与 `schema.json` 中的属性名称匹配。
- 在 `forEach` 内，引用循环变量——例如 `"text": "{!$item.name}"`。请参阅 `references/widget-meta-directives.md`。

---

## 操作

`tile/button` 支持一个 `actions` 属性，在事件上派发操作节点。支持两种操作定义：

| 操作 | 时间 | 必需属性 | 效果 |
|---|---|---|---|
| `action/openLink` | 同步 | `url` (string)。可选 `target` (`_blank`\|`_self`，默认 `_blank`) | 打开 URL |
| `action/sendMessage` | 异步 | `content` (string) | 向代理发布新用户消息并赚取一个新回合 |

```json
{
  "definition": "tile/button",
  "attributes": {
    "label": "Button Label",
    "variant": "primary",
    "actions": { "click": [ { "definition": "action/sendMessage", "attributes": { "content": "content" } } ] }
  }
}
```

```json
{
   "definition": "tile/button",
   "attributes": {
      "label": "Button Label",
      "variant": "primary",
      "actions": { "click": [ { "definition": "action/openLink", "attributes": { "url": "https://www.example.com", "target": "_blank" } } ] }
   }
}
```

**没有 `actions` 属性的 `tile/button` 渲染为禁用状态**——按钮用于触发操作，因此始终将 `click` 操作附加到打算交互的按钮上。

---

## 布局最佳实践

这些约定涵盖 Widget 的 *结构*——块如何分组和堆叠。

| 基本元素 | 目的 | 使用场景 |
|---|---|---|
| `tile/column` | 垂直堆叠子节点 | 根包装器，以及任何应堆叠的块组 |
| `tile/row` | 水平堆叠子节点 | 两个或多个属于同一行的块 |
| `tile/spacer` | 块之间的空白 | 当需要在内容组之间添加额外空间时 |

- **嵌套：** 优先使用扁平布局。仅在视觉方向实际改变该子组时才将 `tile/column` 嵌套在 `tile/row`（反之亦然）内。
- **权威调色板：** 上述表格列出了 *典型* 布局基本元素。始终通过检查 `discoverUiComponents` 输出来确认块的存在——不要假设此表格中的块名称，除非在发现响应中看到它。

---

## 样式最佳实践

Widgets 表达 *意图*，而不是像素。每个表面提供默认的外观和感觉；品牌/主题覆盖自动应用。

- **语义化样式。** 使用 `variant`、`size` 和其他枚举类型属性（`primary`、`destructive`、`success`、`warning`）。不要固定字面量颜色或像素值。
- **每个可见组最多一个主要操作。** 至多一个 `tile/button` 具有 `variant: primary`。使用 `secondary` 或 `destructive` 为附加操作（请参阅 `tile/button` schema 获取完整的 variant 枚举）。
- **每个 `tile/button` 需要一个 `click` 操作。** 请参阅 *操作*——无操作的按钮渲染为禁用状态。
- **每个 Widget 一个 `h1`。** 使用 `h2`/`h3` 为子节标题，`body` 为文本，`caption` 为辅助文本。
- **在具有状态的基本块上使用语义状态变体** (`tile/badge`，`tile/callout`)。
- **接受 `gap`、`size` 的 schema 默认值** 除非有特定原因要覆盖。
- **不要固定 `width`** 除非内容约束需要它。
- **使用 Lucide 图标集。** 传递 Lucide 名称（`"check"`，`"alert-circle"`）；不支持其他图标库。

---

## 工作流程

1. **解析 Widget 规格**——一个有序的 `{ name, type, required }` 列表。来源取决于提供的输入（见 *输入*）：
   - 如果 `lightningTypeSchema` 由协调器传递 → 根据 `references/schema-from-lightning-type.md` 推导。
   - 否则 → 直接从用户提示中推断列表（粘贴的 JSON 负载、枚举的字段列表或描述性文字）。

2. **发现块（必需——不要跳过）。** 通过 `execute_metadata_action` 调用 `discoverUiComponents` 元数据操作。使用 Widget 规格中的属性类型来初始化 `searchQuery`（文本 → `"text"`，数字 → `"number"`）。**如果 `discoverUiComponents` 返回 `success: false`、错误或空列表，停止并直接显示错误——不要从记忆、先前的运行或训练数据中推断块名称。** 仅当失败是特定于搜索查询时，才重新运行发现，使用不同的 `searchQuery`。

3. **选择块。** 为每个 Widget 规格属性选择一个块，并从 *布局最佳实践* 中选择结构化基本元素。

4. **获取块 schema（必需——不要跳过）。** 通过 `execute_metadata_action` 为选定的块调用 `getUiComponentSchemas` 元数据操作。审查属性元数据。**如果 `componentSchemas` 返回全失败或空，停止并直接显示错误——不要从项目中的现有 Widget 中推断。**

5. **构建 UEM 树（示例读取必需——不要跳过）。** 首先，识别与 Widget 规格匹配的模式，并从此技能自己的 `examples/` 目录中读取每个匹配的示例文件（`<skill-root>/examples/`）：

   | 规格中的模式 | 读取的示例 |
   |---|---|
   | 单个对象（无迭代） | `<skill-root>/examples/single-object.json` |
   | 任何列表迭代（根级数组、嵌套列表或嵌入在单个对象 Widget 中的列表） | `<skill-root>/examples/list-with-foreach.json` |
   | 条件渲染（`if` 绑定到布尔值） | `<skill-root>/examples/conditional.json` |

   规格可能匹配多个模式（例如，列表中的某些项条件渲染读取 `list-with-foreach.json` 和 `conditional.json`）。**读取所有匹配的示例，并且仅这些——不要因为模式熟悉而跳过读取。**

   然后：
   - 将每个 Widget 规格属性映射到块属性；保留规格顺序。
   - **决定根迭代：** 单个对象 → 属性直接在根 `tile/column` 下。集合 → 用 `forEach`/`forItem` 包装重复的块。请参阅 `references/widget-meta-directives.md`。
   - 使用 `{!$attrs.X}`（或 `{!$item.X}` 在 `forEach` 内）绑定值。
   - 对于条件块，在 `meta` 上添加 `"if"`——仅当 schema 有匹配的 `lightning__booleanType` 属性时。

6. **编写 `schema.json`。** 从 Widget 规格构建 JSON Schema。字段位于 `attributes` 包装器下一级：

   ```json
   {
     "title": "<Widget 显示名称>",
     "description": "<一句话描述 Widget 显示的内容>",
     "type": "object",
     "properties": {
       "attributes": {
         "lightning:type": "lightning__objectType",
         "properties": {
           "<propertyName>": {
             "title": "<label>",
             "description": "<简短描述>",
             "lightning:type": "<lightning__textType | lightning__numberType | ...>"
           }
         }
       }
     }
   }
   ```

   **必需的根键：** `title`，`type: "object"`，`properties.attributes`（包含 `lightning:type: "lightning__objectType"` 和嵌套的 `properties` 映射）。有关完整基本类型指导，请参阅 `references/schema-from-lightning-type.md`。

7. **编写 `<widgetName>.uiwidget-meta.xml`。** 请参阅 `references/widget-bundle-layout.md` 以获取确切的形状。

8. **解析 `<pkgDir>` 并写入 Bundle。** 按照 `references/widget-bundle-layout.md` 中的 `## Resolving <pkgDir>` 程序进行操作。Widget Bundle 是一个 **三文件集**——必须同时写入这三个文件；少于三个文件的 Bundle 是不完整的，将不会部署。

   ```text
   <pkgDir>/uiWidgets/<widgetName>/<widgetName>.json               # widget 封装——UEM 树（主要工件）
   <pkgDir>/uiWidgets/<widgetName>/schema.json                     # 封装的属性契约
   <pkgDir>/uiWidgets/<widgetName>/<widgetName>.uiwidget-meta.xml  # UiWidgetBundle 注册
   ```

   每个文件都有不同的作用：
   - `<widgetName>.json` — 具有 `tile/widget` UEM 树的 Widget 封装。这是主要工件；`schema.json` 是其伴随契约，不是替代品。
   - `schema.json` — 属性的 JSON Schema，这些属性在封装中通过 `{!$attrs.X}` 绑定。
   - `<widgetName>.uiwidget-meta.xml` — 注册 Bundle 以进行源跟踪和部署的 `UiWidgetBundle` 元素。

   在继续自验证之前，写入所有三个文件。

9. **自验证。** 在报告之前，确认以下每个检查，并单独报告每个结果（`pass` 或 `fail (<reason>)`）。**不要**总结为“全部通过”行——列出每个检查，以便审查者可以识别静默跳过。
    - **`schema-parses`** — `<pkgDir>/uiWidgets/<widgetName>/schema.json` 解析为 JSON。
    - **`schema-root-keys`** — 根有 `title`（字符串），`type: "object"`，和 `properties.attributes`（对象）——其中 `properties.attributes` 包含 `lightning:type: "lightning__objectType"` 和嵌套的 `properties` 映射。没有 `unevaluatedProperties: false`。
    - **`schema-leaf-types`** — 每个 `properties.attributes.properties` 下的叶节点都包含 `lightning:type`。单数嵌套内类字段将 `lightning:type` 设置为内类 Apex 类引用（`@apexClassType/<namespace>__<OuterClass>$<InnerClass>`）；嵌套形状不会重新声明。`List<InnerClass>` 字段将 `lightning:type` 设置为 `lightning__listType`，其中 `items.lightning:type` 设置为内类 Apex 类引用（`@apexClassType/<namespace>__<OuterClass>$<InnerClass>`），而不是重新声明的字段映射——请参阅 `references/schema-from-lightning-type.md`。**当列表没有 Apex 支持的类型**（从提示推断的 schema）时，`items.lightning:type: "lightning__objectType"` 必须包含每个项字段的嵌套 `properties` 映射，这些字段通过 `{!$item.X}` 在身体中绑定。
    - **`bindings-resolve`** — 每个 `{!$attrs.X}`（或 `{!$attrs.<outerField>.<innerField>}` 对于嵌套对象）在 `<widgetName>.json` 中解析到 `schema.json` `properties.attributes.properties` 下的属性，并且每个 `{!$item.X}` 解析到上游定义的 `forItem` 循环变量。
    - **`body-envelope`** — `<widgetName>.json` 根有 `type: "lightning__agentforceWidget"` 和一个 `contentBody` 对象，其 `widgetBody` 包含以 `tile/widget` 为根的 UEM 树。树中的任何节点——根节点或非根节点——都不包含 `type` 键。
    - **`metaxml-wellformed`** — `<widgetName>.uiwidget-meta.xml` 解析为格式良好的 XML。
    - **`metaxml-elements`** — `<widgetName>.uiwidget-meta.xml` 有根 `<UiWidgetBundle>` 并包含 `<masterLabel>`（非空）、`<description>`（非空）和 `<widgetType>JSON</widgetType>`。
    - **`files-present`** — 所有三个文件存在于解析的 `<pkgDir>/uiWidgets/<widgetName>/` 路径。
    - **`button-actions-present`** — `<widgetName>.json` 中的每个 `tile/button` 都有一个 `actions.click` 操作节点，其 `definition` 是 `action/openLink` 或 `action/sendMessage`。

---

## 规则 / 约束

| 约束 | 理由 |
|---|---|
| 块定义遵循 `{namespace}/{blockName}` 并必须与 `discoverUiComponents` 输出匹配 | 运行时通过精确定义字符串解析块 |
| 永远不要将 `tile/widget` 传递给 `getUiComponentSchemas` | 它是一个固定的包装器，不是一个可查询的组件 |
| 调用 `execute_metadata_action` 时始终提供 `parameters`（包含必需的键） | 缺少参数会导致硬失败，而不是部分结果 |
| 正文中的每个 `{!$attrs.X}` 都解析为小部件 `schema.json` 中的属性 | 没有虚构的字段 |
| 每个 `tile/button` 都带有使用 `action/openLink` 或 `action/sendMessage` 的 `actions.click` 条目 | 这两个是仅支持的块操作定义；无操作的按钮会渲染为禁用状态 |
| 任何 Bash 工具调用中都不包含 `$(…)`, 反引号, `<(…)`, 大括号展开 `{a,b,c}` 或 `eval`/`exec` | Vibes 的 safe-shell 过滤器强制在绕过模式下对这些模式进行手动批准。发出单独的命令 (`mkdir -p a && mkdir -p b`) 或使用各自的命令和原因打印每个值——不要捕获到 shell 变量 |

---

## 注意事项

| 问题 | 解决方案 |
|---|---|
| `getUiComponentSchemas` 返回一个部分失败条目 | 从 `discoverUiComponents` 选择不同的块；不要在缺少模式的情况下静默继续 |
| 正文引用 `{!$attrs.foo}`，但 `foo` 不在 `schema.json` 的 `properties.attributes.properties` 下 | 将 `foo` 添加到 `schema.json` 的 `properties.attributes.properties` 或删除正文引用 |
| 输出写入到 `<pkgDir>/uiWidgets/<widgetName>/` 之外 | `<pkgDir>` = `<packageDirectories[].path>/main/default`（参见 `references/widget-bundle-layout.md`）。丢失 `main/default/` 段是导致小部件落在 `force-app/uiWidgets/...` 而不是 `force-app/main/default/uiWidgets/...` 的常见原因 |
| `if` 绑定到非布尔值 | 仅在模式具有 `lightning__booleanType` 属性时使用 `if` |
| `tile/button` 渲染但点击时什么也不做 | 未设置 `actions.click` 条目——无操作的按钮按设计渲染为禁用状态。添加一个（参见上文 *操作*） |
| 使用 `action/sendMessage` 进行纯导航，或在使用代理应响应时使用 `action/openLink` | `action/openLink` 是同步的，不会消耗回合；`action/sendMessage` 是异步的，会获得一个新回合。选择与预期 UX 匹配的一个 |

---

## 参考文件索引

| 文件 | 何时阅读 |
|---|---|
| `references/widget-meta-directives.md` | 用于 `forEach` / `forItem`（迭代）和 `if`（条件渲染），包括嵌套循环 |
| `references/schema-from-lightning-type.md` | 当提供 `lightningTypeSchema` 时；如何从 Apex 支持的 Lightning Type 推导小部件 `schema.json` |
| `references/widget-bundle-layout.md` | 文件夹布局，`-meta.xml` 形状，`<pkgDir>` 解析规则 |
| `examples/single-object.json` | 单对象模式（通过 `{!$attrs.X}` 根绑定，无迭代） |
| `examples/list-with-foreach.json` | 任何列表迭代情况——根级集合、嵌套列表和嵌入在单个对象小部件中的列表（例如，在外部 Apex 负载中迭代 `List<InnerClass>`） |
| `examples/conditional.json` | 条件模式（`meta` 上的 `if`，包括 `if` + `forEach` 一起） |
