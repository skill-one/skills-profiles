# 生成 Widget Bundle

编写一个完整的 WidgetBundle：一个 UEM 树（`tile/widget`）、一个描述 Widget 输入合同的 JSON Schema，以及 `.uiwidget-meta.xml` 文件来注册该 Bundle。

## 使用此技能的场景

当用户要求一个 Widget、马赛克、片段或卡片式富 UI 界面时使用。不要使用此技能来生成自定义-LWC 渲染器或 Custom Lightning Type bundle 中的 `renderer.json` 文件——这些属于 `platform-custom-lightning-type-generate`。

## 输入

- **`widgetName`** (必需) — `camelCase` 标识符；将成为 `uiWidgets/` 下面的目录名。
- 一个 **形状** — Widget 渲染的数据。没有形状，Widget 将无法生成。形状通过以下两种方式之一提供，优先级依次：
  1. **`lightningTypeSchema`** — `{ path, apexClassFqn }` 用于现有的 Apex 支持的 Lightning Type。FQN 采用两种形式之一：外类（`<namespace>__<ClassName>`），其中外类是有效负载，或内类（`<namespace>__<ClassName>$<InnerClass>`），其中命名的内类是有效负载。由 `platform-lightning-type-widget-coordinate` 协调器传递。当存在时，根据 `references/schema-from-lightning-type.md` 进行派生。
  2. 从用户的提示中提取——当未传递 `lightningTypeSchema` 时，直接从用户写入的内容中推断形状：粘贴的 JSON 负载、枚举的字段列表（"id as string, total as number"）或描述性文本。输出是相同顺序的 `{ name, type, required }` 列表，无论哪种方式。

如果两种来源都没有产生形状，则停止并询问用户再继续。

## 输出

`<pkgDir>/uiWidgets/<widgetName>/` 中的三个文件：

| 文件 | 内容 |
|---|---|
| `<widgetName>.json` | Widget 封装——`{ "type": "lightning__agentforceWidget", "contentBody": { "widgetBody": { UEM 树以 tile/widget 为根 } } }` |
| `schema.json` | JSON Schema — 根具有 `type: "object"` + `properties.attributes` 包装，其中包含 `lightning:type: "lightning__objectType"` 和字段 `properties` |
| `<widgetName>.uiwidget-meta.xml` | `<UiWidgetBundle>` 元素，包含 `<masterLabel>`、`<description>` 和 `<widgetType>JSON</widgetType>` |

有关 `<pkgDir>` 解析过程和 `<widgetName>.uiwidget-meta.xml` 的确切形状，请参阅 `references/widget-bundle-layout.md`。

---

## 组成

Widget 身体是一个嵌套在 `contentBody.widgetBody` 下的 UEM 树。根节点是 `tile/widget`。每个节点——根节点和非根节点——具有相同的形状：没有 `type` 键；只有 `definition`、可选的 `attributes`、可选的 `meta` 和可选的 `children`。块形状：

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

`tile/widget.children` 的第一个子节点应该是单个 `tile/column`。所有 Widget 内容通常都放在第一个子节点中，以在各个表面上保持可预测的垂直结构。

---

## 可用的元数据操作

### discoverUiComponents

**目的：** 发现用于组合的块板。

**必需参数：** `actionName: "discoverUiComponents"`，`metadataType: "FRAGMENT"`，`parameters.pageType: "FRAGMENT"`。可选：`searchQuery` 以按名称/描述过滤。

**返回：** `{ definition, description, label, attributes? }` 列表。

### getUiComponentSchemas

**目的：** 获取选定块的 JSON Schema（属性类型、必需与可选、验证）。

**必需参数：** `actionName: "getUiComponentSchemas"`，`metadataType: "FRAGMENT"`，`parameters.pageType: "FRAGMENT"`，`parameters.componentDefinitions: ["namespace/definition", ...]`。可选：`includeKnowledge`（默认 `true`）。

**返回：** `componentSchemas[]` — 成功条目包含 JSON Schema，失败条目包含错误消息。支持部分失败。

> 永远不要将 `tile/widget` 传递给 `getUiComponentSchemas`——它是一个固定的包装器，不是可查询的组件。

---

## 属性绑定

- 使用 `{!$attrs.<attrName>}` 将块属性绑定到运行时数据。`<attrName>` 必须与 `schema.json` 中的属性名称匹配。
- 在 `forEach` 内部，引用循环变量——例如 `"text": "{!$item.name}"`。请参阅 `references/widget-meta-directives.md`。
- 绑定可以是一个 **公式表达式** 而不是裸字段引用。请参阅 `references/widget-formulas.md` 以获取完整支持函数列表、语法和注意事项。

---

## 操作

`tile/button` 支持一个 `actions` 属性，在事件上派发一个操作节点。支持两种操作定义：

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

**没有 `actions` 属性的 `tile/button` 渲染为禁用状态**——按钮存在是为了触发操作，因此始终将 `click` 操作附加到打算交互的按钮上。

---

## 布局最佳实践

这些约定涵盖了 Widget 的 *结构*——块如何分组和堆叠。

| 基本元素 | 目的 | 何时使用 |
|---|---|---|
| `tile/column` | 垂直堆叠子节点 | 根包装器，以及任何应堆叠的块组 |
| `tile/row` | 水平堆叠子节点 | 两个或多个应位于同一行上的块 |
| `tile/spacer` | 块之间的空白 | 当需要在内容组之间添加额外空间时 |

- **嵌套：** 优先使用扁平布局。仅在视觉方向实际改变该子组时才将 `tile/column` 嵌套在 `tile/row` 内（反之亦然）。
- **权威调色板：** 表格列出了 *典型* 布局基本元素。始终通过检查 `discoverUiComponents` 输出来确认块的存在——不要假设此表格中的块名，除非在发现响应中看到它。

---

## 样式最佳实践

Widgets 表达 *意图*，而不是像素。每个表面提供默认的外观和感觉；品牌/主题覆盖自动应用。

- **语义化样式。** 使用 `variant`、`size` 和其他枚举类型属性（`primary`、`destructive`、`success`、`warning`）。不要固定字面量颜色或像素值。
- **每个可见组最多一个主要操作。** 最多一个 `tile/button` 具有 `variant: primary`。使用 `secondary` 或 `destructive` 为附加操作（请参阅 `tile/button` schema 以获取完整的 variant 枚举）。
- **每个 `tile/button` 需要一个 `click` 操作。** 请参阅 *操作*——无操作的按钮渲染为禁用状态。
- **每个 Widget 一个 `h1`。** 使用 `h2`/`h3` 为子节标题，`body` 为文本，`caption` 为辅助文本。
- **在具有状态的基本元素上使用语义状态变体** (`tile/badge`、`tile/callout`)。
- **接受 `gap`、`size` 的 schema 默认值**，除非有特定原因要覆盖。
- **不要固定 `width`**，除非内容约束需要它。
- **使用 Lucide 图标集。** 传递 Lucide 名称（`"check"`、`"alert-circle"`）；不支持其他图标库。

---

## 工作流程

1. **解析 Widget 规格**——一个 `{ name, type, required }` 的有序列表。来源取决于提供的输入（见 *输入*）：
   - 如果 `lightningTypeSchema` 由协调器传递 → 根据 `references/schema-from-lightning-type.md` 派生。
   - 否则 → 直接从用户提示中推断列表（粘贴的 JSON 负载、枚举的字段列表或描述性文本）。

2. **发现块（必需——不要跳过）。** 通过 `execute_metadata_action` 调用 `discoverUiComponents` 元数据操作。使用 Widget 规格中的属性类型来为 `searchQuery` 喂入（文本 → `"text"`，数字 → `"number"`）。**如果 `discoverUiComponents` 返回 `success: false`、错误或空列表，停止并逐字显示错误——不要从记忆、先前的运行或训练数据中臆造块名。** 只有当失败是特定于搜索查询时，才重新运行发现，使用不同的 `searchQuery`。

3. **选择块。** 为每个 Widget 规格属性选择一个块，并从 *布局最佳实践* 中选择结构基本元素。

4. **获取块 schema（必需——不要跳过）。** 通过 `execute_metadata_action` 为选定的块调用 `getUiComponentSchemas`。审查属性元数据。**如果 `componentSchemas` 返回全失败或空，停止并逐字显示错误——不要从项目中的现有 Widget 臆造。**

5. **构建 UEM 树（示例读取必需——不要跳过）。** 首先，识别与 Widget 规格匹配的模式，并从此技能自己的 `examples/` 目录中读取每个匹配的示例文件（`<skill-root>/examples/`）：

   | 规格中的模式 | 读取的示例 |
   |---|---|
   | 单个对象（无迭代） | `<skill-root>/examples/single-object.json` |
   | 任何列表迭代（根级数组、嵌套列表或嵌入在单个对象 Widget 中的列表） | `<skill-root>/examples/list-with-foreach.json` |
   | 条件渲染（`if` 绑定到布尔值或公式） | `<skill-root>/examples/conditional.json` |
   | 计算值、文本/数字转换或由公式驱动的 `if`（不是裸布尔字段） | `<skill-root>/examples/formulas.json` |

   规格可能匹配多个模式（例如，列表中的某些项条件渲染读取 `list-with-foreach.json` 和 `conditional.json`）。**读取所有匹配的示例，并且仅这些——不要因为模式熟悉而跳过读取。**

   **在编写任何公式之前**，完整阅读 `references/widget-formulas.md`——它是支持运算符和函数的权威列表；不要臆造未在此处文档化的函数名或运算符。

   然后：
   - 将每个 Widget 规格属性映射到块属性；保留规格顺序。
   - **决定根迭代：** 单个对象 → 属性直接在根 `tile/column` 下。集合 → 用 `forEach`/`forItem` 包装重复块。请参阅 `references/widget-meta-directives.md`。
   - 使用 `{!$attrs.X}`（或 `{!$item.X}` 在 `forEach` 内部）绑定值。
   - 对于条件块，添加 `"if"` 在 `meta`——要么是一个裸 `lightning__booleanType` 属性，要么是一个求值为布尔的表达式。请参阅 `references/widget-formulas.md`。
   - **当 Widget 规格要求计算值**（总计、派生标签、格式化字符串）而不是原始字段时，根据 `references/widget-formulas.md` 在 `{!...}` 内表达它——不要发明一个新 schema 属性来持有可以从现有属性计算出的值。

6. **编写 `schema.json`。** 从 Widget 规格构建 JSON Schema。字段位于一个级别的 `attributes` 包装下：

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
             "title": "<标签>",
             "description": "<简短描述>",
             "lightning:type": "<lightning__textType | lightning__numberType | ...>"
           }
         }
       }
     }
   }
   ```

   **必需的根键：** `title`，`type: "object"`，`properties.attributes`（具有 `lightning:type: "lightning__objectType"` 和嵌套的 `properties` 映射）。请参阅 `references/schema-from-lightning-type.md` 以获取完整的原始类型指导。

7. **编写 `<widgetName>.uiwidget-meta.xml`。** 请参阅 `references/widget-bundle-layout.md` 以获取确切形状。

8. **解析 `<pkgDir>` 并写入 Bundle。** 按照 `references/widget-bundle-layout.md` (`## Resolving <pkgDir>`) 中的程序进行操作。Widget Bundle 是一个 **三文件集**——必须同时写入所有三个文件；少于三个文件的 Bundle 是不完整的，将无法部署。

   ```text
   <pkgDir>/uiWidgets/<widgetName>/<widgetName>.json               # widget 封装 — UEM 树（主要工件）
   <pkgDir>/uiWidgets/<widgetName>/schema.json                     # 属性合同，用于封装
   <pkgDir>/uiWidgets/<widgetName>/<widgetName>.uiwidget-meta.xml  # UiWidgetBundle 注册
   ```

   每个文件具有不同的作用：
   - `<widgetName>.json` — 具有 `tile/widget` UEM 树的 widget 封装。这是主要工件；`schema.json` 是其伴随合同，不是替代品。
   - `schema.json` — 属性的 JSON Schema，这些属性在封装中通过 `{!$attrs.X}` 绑定。
   - `<widgetName>.uiwidget-meta.xml` — 注册 Bundle 以进行源跟踪和部署的 `UiWidgetBundle` 元素。

   在继续自我验证之前，写入所有三个文件。

9. **自我验证。** 在报告之前，确认以下每个检查，并逐个报告结果（`pass` 或 `fail (<reason>)`）。**不要**总结为一条“全部通过”的行——列出每个检查，以便审查者可以识别静默跳过。
    - **`schema-parses`** — `<pkgDir>/uiWidgets/<widgetName>/schema.json` 解析为 JSON。
    - **`schema-root-keys`** — 根具有 `title` (string)，`type: "object"`，和 `properties.attributes` (object) — 其中 `properties.attributes` 包含 `lightning:type: "lightning__objectType"` 和嵌套的 `properties` 映射。没有 `unevaluatedProperties: false`。
    - **`schema-leaf-types`** — 每个 `properties.attributes.properties` 下的叶子都包含 `lightning:type`。单数嵌套内类字段将 `lightning:type` 设置为内 Apex 类引用（`@apexClassType/<namespace>__<OuterClass>$<InnerClass>`）；嵌套形状不重新声明。`List<InnerClass>` 字段将 `lightning:type: "lightning__listType"` 设置为内 Apex 类引用（`@apexClassType/<namespace>__<OuterClass>$<InnerClass>`），而不是重新声明的字段映射——请参阅 `references/schema-from-lightning-type.md`。**当列表没有 Apex 支持的类型**（从提示推断的 schema）时，`items.lightning:type: "lightning__objectType"` 必须包含一个嵌套的 `properties` 映射，用于每个通过 `{!$item.X}` 绑定的项字段。
    - **`bindings-resolve`** — `<widgetName>.json` 中的每个 `{!$attrs.X}`（或 `{!$attrs.<outerField>.<innerField>}` 对于嵌套对象）解析到 `schema.json` `properties.attributes.properties` 下的属性，并且每个 `{!$item.X}` 解析到上游定义的 `forItem` 循环变量。这适用于 `$attrs`/`$item` 参考在公式表达式内部。
    - **`formulas-supported`** — `{!...}` 表达式内部使用的每个函数名都出现在 `references/widget-formulas.md` 中 *支持的函数* 列表中。
    - **`body-envelope`** — `<widgetName>.json` 根具有 `type: "lightning__agentforceWidget"` 和一个 `contentBody` 对象，其 `widgetBody` 包含以 `tile/widget` 为根的 UEM 树。树中的任何节点——根节点或非根节点——都不应包含 `type` 键。
    - **`metaxml-wellformed`** — `<widgetName>.uiwidget-meta.xml` 解析为良好形成的 XML。
    - **`metaxml-elements`** — `<widgetName>.uiwidget-meta.xml` 具有 `<UiWidgetBundle>` 根，并包含 `<masterLabel>`（非空）、`<description>`（非空）和 `<widgetType>JSON</widgetType>`。
    - **`files-present`** — 所有三个文件都存在于解析的 `<pkgDir>/uiWidgets/<widgetName>/` 路径。
    - **`button-actions-present`** — `<widgetName>.json` 中的每个 `tile/button` 都有一个 `actions.click` 操作节点，其 `definition` 是 `action/openLink` 或 `action/sendMessage`。

---

## 规则 / 约束

| 约束 | 理由 |
|---|---|
| 块定义遵循 `{namespace}/{blockName}`，必须匹配 `discoverUiComponents` 输出 | 运行时通过确切的定义字符串解析块 |
| 永远不要将 `tile/widget` 传递给 `getUiComponentSchemas` | 它是一个固定的包装器，不是可查询的组件 |
| 调用 `execute_metadata_action` 时始终提供 `parameters`（带必需键） | 缺少参数会导致硬失败，而不是部分结果 |
| Widget 中的每个 `{!$attrs.X}` 解析到 `schema.json` 中的属性 | 没有臆造的字段 |
| 每个 `tile/button` 都带有使用 `action/openLink` 或 `action/sendMessage` 的 `actions.click` 条目 | 这是仅支持的两种 tile 操作定义；无操作的按钮渲染为禁用状态 |
| 在任何 Bash 工具调用中都没有 `$(…)`, 反引号, `<(…)` 或brace 扩展 `{a,b,c}` 或 `eval`/`exec` | Vibes' safe-shell 过滤器强制手动批准这些模式，即使在 Bypass 模式下也是如此。分别发出命令 (`mkdir -p a && mkdir -p b`) 或使用自己的命令和原因打印每个值——不要捕获到 shell 变量中 |

---

## 注意事项

| 问题 | 解决方案                                                                                                                                                                                                                                                     |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `getUiComponentSchemas` 返回部分失败条目 | 选择 `discoverUiComponents` 中的不同块；不要在没有 schema 的情况下静默继续                                                                                                                                                                  |
| 身体引用 `{!$attrs.foo}`，但 `foo` 不在 `schema.json` `properties.attributes.properties` 下 | 将 `foo` 添加到 `schema.json` `properties.attributes.properties` **或** 移除身体引用                                                                                                                                                                     |
| 输出写入在 `<pkgDir>/uiWidgets/<widgetName>/` 外部 | `<pkgDir>` = `<packageDirectories[].path>/main/default`（见 `references/widget-bundle-layout.md`）。丢失 `main/default/` 段是导致 Widget 落在 `force-app/uiWidgets/...` 而不是 `force-app/main/default/uiWidgets/...` 的常见原因 |
| 直接绑定到原始字符串或数字的 `if` 依赖于真值，不可靠 | 绑定到 `lightning__booleanType` 属性，或使用一个求值为布尔的表达式进行比较                                                                                                                                                             |
| 点击时 `tile/button` 渲染但无任何操作 | 未设置 `actions.click` 条目——按设计，无操作的按钮渲染为禁用状态。添加一个（见 *操作* 以上）                                                                                                                                             |
| 使用 `action/sendMessage` 进行纯导航，或使用 `action/openLink` 而代理应响应 | `action/openLink` 是同步的，不会消耗回合；`action/sendMessage` 是异步的，会赚取一个新回合。选择与预期 UX 匹配的一个                                                                                                                               |

---

## 参考文件索引

| 文件 | 何时阅读                                                                                                                                                                        |
|---|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `references/widget-meta-directives.md` | 用于 `forEach` / `forItem`（迭代）和 `if`（条件渲染），包括嵌套循环                                                                                      |
| `references/schema-from-lightning-type.md` | 当提供 `lightningTypeSchema` 时；如何从 Apex 支持的 Lightning Type 派生 Widget `schema.json`                                                                   |
| `references/widget-bundle-layout.md` | 文件夹布局、`-meta.xml` 形状、`<pkgDir>` 解析规则                                                                                                                       |
| `references/widget-formulas.md` | 支持的公式函数和运算符                                                                                                                                           |
| `examples/single-object.json` | 单个对象模式（通过 `{!$attrs.X}` 根绑定，无迭代）                                                                                                                |
| `examples/list-with-foreach.json` | 任何列表迭代情况——根级集合、嵌套列表和嵌入在单个对象 Widget 中的列表（例如，在 outer Apex 负载中迭代 `List<InnerClass>`） |
| `examples/conditional.json` | 条件模式 (`if` 在 `meta`，包括 `if` + `forEach` 一起）                                                                                                           |
| `examples/formulas.json` | 公式使用——文本/算术/日期转换，`IF`/`AND`/`NOT` 驱动 `tile/text` 和 `meta.if`                                                                          |
