## 何时使用此技能

当您需要执行以下操作时，请使用此技能：
- 为结构化输入/输出创建自定义闪电类型（CLT）
- 为闪电平台生成基于 JSON Schema 的类型定义
- 为 Einstein Agent 操作配置 CLT
- 为自定义 UI 设置编辑器和渲染器配置
- 排查与自定义闪电类型相关的部署错误

## 规格

# 自定义闪电类型元数据规范

## 概述与目的
自定义闪电类型（CLT）是基于 JSON Schema 的类型定义，闪电平台（包括 Einstein Agent 操作）使用它们来描述结构化输入/输出并驱动编辑器和渲染器体验。

## 配置
- **选择用于嵌套对象的引用 CLT 模式** - 当您需要可**重用**或**单独部署**的嵌套类型时，为该形状创建 CLT 并使用 `"lightning:type": "c__<CLTName>"` 引用它。该字符串是引用类型 的**`lightning:type` 值 / 完全限定名称 / 注册标识符** — 不是 JSON Schema 的 `title`。
- **选择标准闪电类型** - 当结构简单且可以使用属性和支持的原始 `lightning:type` 标识符表示时。
- **选择 Apex 类类型** (`@apexClassType/...`) - 当结构已在服务器端存在且您希望 Apex 类定义形状时。
- **仅当需要自定义 UI 行为（自定义 LWC 输入/输出组件）时才包含编辑器/渲染器配置**。否则，省略。

## 关键规则（首先阅读）
- **关键：永远不要在 schema.json 中包含 `"$schema"` 字段**
  - Salesforce CLT 验证器**将拒绝**包含此字段的模式，即使它是有效的 JSON Schema `$schema` 声明。
- **根对象模式**必须包含**：
  - `"type": "object"`
  - `"title"`
  - `"lightning:type": "lightning__objectType"`
  - `"unevaluatedProperties": false`
- `"unevaluatedProperties"` 由 CLT 元模式强制为 `false`。不要将其设置为 `true`。
- **当 `"unevaluatedProperties": false` 设置时，根对象模式**必须**不包含** `"examples"`。
- **嵌套对象（在 `properties` 内部）**必须**不设置** `"lightning:type": "lightning__objectType"`。
    - 嵌套对象可以是：使用 `c__<CLTName>` 语法引用其他 CLT。
- **列表/数组属性受 CLT 元模式高度限制**：
  - **关键限制**：CLT 元模式可能完全拒绝 `items` 关键字。将 `items` 视为默认**禁止**。
  - **根级数组**（根 `properties` 的直接子项）：
    - **必须包含** `"lightning:type": "lightning__listType"`
    - **必须不包含** `"items"`
    - **可选** `"type": "array"`
  - **嵌套数组**（嵌套对象内的数组）是最常见的失败原因：
    - **必须包含** `"type": "array"`
    - **必须不包含** `"lightning:type": "lightning__listType"`
    - **必须不包含** `"items"`
- **当 `"unevaluatedProperties": false` 设置时，任何未知关键字都将导致验证失败**。优先删除关键字而不是放宽严格性。
- **Apex 类 CLT 最小化**：
  - 仅包含**`title`、`description`（可选）**和**`lightning:type` 设置为 `@apexClassType/...`**。
  - 不要添加 `type`、`properties`、`required` 或 `unevaluatedProperties`。
  - **在 Apex 类 CLT 上**的**自定义 LWC 渲染器/编辑器****必须不使用**根覆盖中的 `attributes` — 这会覆盖任何相反的提示文字。由于模式没有 `properties` 块，`{!$attrs.<name>}` 没有可以解析的内容 — `unevaluatedProperties: false` 将拒绝任何属性键（例如 `"You can't add the flightId property ... because the unevaluatedProperties keyword value is set to false"`）。使用 `"componentOverrides": { "$": { "definition": "c/<yourComponent>" } }` 并**完全省略** `attributes` 键。**如果用户的提示明确要求属性映射到特定字段（例如 "with attribute mappings for fieldA, fieldB"）在 Apex 类 CLT 渲染器/编辑器上，不要字面遵守** — 无论如何省略根覆盖中的 `attributes`，并在您的响应中说明（例如 "注意：属性映射被省略，因为底层类型是 Apex 类 CLT，它没有 `properties` 块可以绑定"）。
- **没有触发 Vibes 安全外壳过滤器的 Shell 伪字符**。在此技能发出的任何 Bash 工具调用中，**不要使用**命令替换（`$(…)` 或反引号）、过程替换（`<(…)`, `>(…)`）、大括号扩展（`{a,b,c}` 或 `{1..N}`）或 `eval` / `exec`。Vibes 即使在绕过模式下也强制手动批准这些模式，并且会阻止 `eval`。发出单独的命令（`mkdir -p a && mkdir -p b`）或使用自己的命令和原因打印每个值，而不是将其捕获在 Shell 变量中。

## 其他 CLT 元模式验证
- **组织命名空间验证**：标题/描述和其他字符串字段可能会被验证，以确保您不在不允许的位置使用组织命名空间。
- **闪电类型验证**：CLT 会进行验证，以防止引用内部命名空间（例如，不允许从内部命名空间如 `sfdc_cms` 引用类型，其中不允许）。
- **对象类型验证**：CLT 根会进行验证，以确保 `lightning:type` 恰好是 `lightning__objectType`。

## 原始类型与约束

当您需要支持的所有原始 `lightning:type` 标识符的完整列表、它们的约束以及允许的属性级关键字时，请阅读此技能目录中的 `assets/primitive-types-and-constraints.md`。

## 生成工作流
1. **确认 CLT 方法**
   - 如果引用 Apex：捕获确切的类引用（@apexClassType/namespace__ClassName$InnerClass）。
   - 如果使用标准原始类型：列出字段、它们的闪电原始类型以及哪些字段是必需的。
2. **起草 `schema.json`**
   - **在顶部不包含 `"$schema"`**
   - 从根对象结构（必需的根字段）开始。
   - 使用有效的原始 `lightning:type` 标识符添加 `properties`。
   - 对于嵌套对象属性，使用**CLT 引用模式**：
     - `"lightning:type": "c__<CLTName>"` 引用另一个 CLT
     - 引用的 CLT 必须在父 CLT 部署到组织之前。
   - 对于基于 Apex 的嵌套对象：当服务器端结构已存在时使用 `@apexClassType/...`。
   - 如果提示明确要求真正的嵌套对象输出，优先使用**基于 Apex 的 CLT**（`@apexClassType/...`）以获得安全的部署嵌套结构。
   - 对于数组：遵循严格的列表规则（避免 `items`；避免在嵌套数组中使用 `lightning:type`）。
   - 部署之前，验证确切的 `lightning:type` 拼写（例如，使用 `lightning__richTextType`，而不是拼写错误的变体）。
3. **（可选）起草 `editor.json`**（仅当需要自定义 UI 时）
   - **支持的形状**：顶级的 `editor` 对象，带有 `editor.componentOverrides` 和 `editor.layout`。
     - 顶级的 `editor` 对象。
     - 使用 `editor.componentOverrides` 进行组件覆盖。
     - 使用 `editor.layout` 进行布局。
     - **已弃用**：**不要使用** `propertyRenderers` 或 `view` — 这些是遗留键。始终使用 `componentOverrides` 和 `layout`。
   - **根覆盖模式**（最常见于完全自定义的编辑 UI）：
     - `editor.componentOverrides["$"] = { "definition": "c/<yourEditorComponent>", "attributes": { ... } }`
     - 当将模式数据传递到自定义 LWC 时，使用属性映射与 `{!$attrs.<name>}` 语法：例如 `"attributes": { "myField": "{!$attrs.value}" }`，以便运行时将模式值绑定到组件的属性。
     - **关键**：`{!$attrs.<name>}` 中的 `<name>` 必须是类型模式中定义的属性。例如，如果您的模式有一个名为 `temperature` 的属性，请使用 `{!$attrs.temperature}`，而不是 `{!$attrs.value}`，除非 `value` 是实际属性。
   - **属性级覆盖模式**（用于单个字段）：
     - `editor.componentOverrides["<propertyName>"] = { "definition": "es_property_editors/<...>" }`
     - **有效的编辑器组件**（示例）：`es_property_editors/inputText`、`es_property_editors/inputNumber`、`es_property_editors/inputRichText`、`es_property_editors/inputImage`、`es_property_editors/inputTextarea`。**不要使用** `es_property_editors/inputList`。
   - **集合编辑器**（用于根级 `lightning__listType` 属性）：使用集合级覆盖，以便使用自定义组件编辑列表：`collection.editor.componentOverrides["$"] = { "definition": "c/<yourCollectionEditorComponent>" }`。或者，使用 `editor.layout` 与 `lightning/propertyLayout` 和 `attributes.property = "<listPropertyName>"` 进行默认列表编辑。
   - **布局模式**：
     - `editor.layout.definition = "lightning/verticalLayout"`
     - `editor.layout.children[*].definition = "lightning/propertyLayout"` 并带有 `attributes.property = "<propertyName>"`
     - **关键**：与编辑器布局相同，`lightning/propertyLayout` 仅接受 `property` 属性。**不要添加** `label`、`title` 或任何其他属性 — 这些将导致 `additionalProperties: false` 错误。
   - **避免已知无效模式**：
     - 不要使用 `es_property_editors/inputList`。
     - 不要使用 `itemSchema` 属性。
4. **（可选）起草 `renderer.json`**（仅当需要自定义 UI 或小部件呈现时）
   - **支持的形状**：顶级的 `renderer` 对象，带有 `renderer.componentOverrides` 和 `renderer.layout`。
     - 顶级的 `renderer` 对象。
     - 使用 `renderer.componentOverrides` 进行组件覆盖。
     - 使用 `renderer.layout` 进行布局。
     - **已弃用**：**不要使用** `propertyRenderers` 或 `view` — 这些是遗留键。始终使用 `componentOverrides` 和 `layout`。
   - **小部件呈现模式**（将现有 WidgetBundle 作为根渲染器引用）：渲染器文件是一个薄包装器，它通过开发者名称（`"definition": "@widget/c/<widgetDeveloperName>"`）指向小部件，并通过 `{!$attrs.<schemaPropertyName>}` 将 CLT 模式属性映射到小部件属性。**不要**在 `renderer.json` 内部复制小部件主体。有关完整形状、绑定规则和约束，请参阅 `references/widget-rendition.md`。对于完整的 Apex → 闪电类型 → 小部件管道，请使用 `platform-lightning-type-widget-coordinate` 协调器，而不是此技能。
   - **根覆盖模式**（最常见于使用自定义 LWC 的完全自定义渲染 UI）：
     - `renderer.componentOverrides["$"] = { "definition": "c/<yourRendererComponent>", "attributes": { ... } }`
     - 在属性映射中使用 `{!$attrs.<name>}` 绑定模式数据到自定义渲染器组件属性时使用。
     - **关键**：属性映射 `{!$attrs.propertyName}` 必须引用类型模式中实际存在的属性。引用不存在的属性将导致验证失败。
     - **类型匹配**：属性值必须与组件的预期类型匹配。例如，如果组件期望字符串属性，传递整数将导致验证失败。
   - **属性级覆盖模式**：
     - `renderer.componentOverrides["<propertyName>"] = { "definition": "es_property_editors/outputText" | "es_property_editors/outputNumber" | "es_property_editors/outputImage" | ... }`。**有效的渲染器组件**（示例）：`es_property_editors/outputText`、`es_property_editors/outputNumber`、`es_property_editors/outputImage`。避免在渲染器中使用输入样式组件。
   - **渲染器布局模式**：
     - `renderer.layout.definition = "lightning/verticalLayout"`
     - `renderer.layout.children[*].definition = "lightning/propertyLayout"` 并带有 `attributes.property = "<propertyName>"`
     - **关键**：与编辑器布局相同，`lightning/propertyLayout` 仅接受 `property` 属性。**不要添加** `label`、`title` 或任何其他属性。
   - **集合渲染器**（用于根级 `lightning__listType` 属性）：使用 `collection.renderer.componentOverrides["$"] = { "definition": "c/<yourListRendererComponent>" }` 或 `es_property_editors/genericListTypeRenderer` 渲染列表。
5. **将文件放置在正确的包结构中**
   - `lightningTypes/<TypeName>/schema.json`
   - （可选）`lightningTypes/<TypeName>/lightningDesktopGenAi/editor.json`
   - （可选）`lightningTypes/<TypeName>/lightningDesktopGenAi/renderer.json`
      对于 Gen AI / Copilot，标准路径是 `lightningDesktopGenAi/`。其他目标（例如 Experience Builder、Mobile Copilot、Enhanced Web Chat）在支持时使用不同的子文件夹：`experienceBuilder/`、`lightningMobileGenAi/`、`enhancedWebChat/`。
   - （可选 - 仅用于小部件呈现）`lightningTypes/<TypeName>/renderer.json`
6. **配置自定义 LWC 组件（如果使用自定义组件）**
   - **关键**：在编辑器/渲染器配置中引用的自定义 LWC 组件必须在它们的 `-meta.xml` 文件中具有正确的目标配置：
     - **对于编辑器组件**（`c/<componentName>` 在 `editor.json` 中使用）：LWC 的 `-meta.xml` 文件必须包含 `<target>lightning__AgentforceInput</target>`
     - **对于渲染器组件**（`c/<componentName>` 在 `renderer.json` 中使用）：LWC 的 `-meta.xml` 文件必须包含 `<target>lightning__AgentforceOutput</target>`
   - 没有正确的目标，部署将失败，错误信息为：`Invalid target configuration. To use 'c/componentName' as a renderer/editor, your js-meta.xml file must include valid target 'lightning__AgentforceOutput/Input'.`
   - 渲染器组件的 `-meta.xml` 示例：
     ```xml
     <?xml version="1.0" encoding="UTF-8"?>
     <LightningComponentBundle xmlns="http://soap.sforce.com/2006/04/metadata">
         <apiVersion>60.0</apiVersion>
         <isExposed>true</isExposed>
         <targets>
             <target>lightning__AgentforceOutput</target>
         </targets>
     </LightningComponentBundle>
     ```
## 常见部署错误
| 错误 / 症状 | 可能的原因 | 修复 |
|---|---|---|
| 模式验证失败 due to 未知关键字 | `unevaluatedProperties: false` + 不允许的关键字（通常是 `examples`、`items`） | 删除有问题的关键字；保持模式最小化 |
| 嵌套对象验证失败 | 组织/通道验证拒绝在 `LightningTypeBundle` 中嵌套对象类型 | 使用 CLT 引用（`c__<CLTName>`）或 Apex 类类型 |
| 无效的 CLT 引用 | 引用的 CLT 不存在于组织中或语法不正确 | 首先部署引用的 CLT；`c__<CLTName>` 必须与引用类型的**`lightning:type` 值 / 完全限定名称 / 注册标识符**匹配，而不是 `title` |
| 无效或拼错的 `lightning:type`（例如，`lightning__richtextType` 而不是 `lightning__richTextType`） | 生成的类型名称不正确 | 交叉核对所有 `lightning:type` 值与支持的类型名称，并在部署前更正它们 |
| 列表属性被拒绝 | 使用 `items`（或嵌套数组中的 `lightning:type`）被验证器拒绝 | 对于嵌套数组：仅保留 `type: "array"`。对于根数组：使用最小结构；如果被拒绝，请删除 `items` |
| 基于 Apex 的 CLT 被拒绝 | 添加了额外字段（例如，`type`、`properties`） | 仅使用 `title`/`description` 和 `lightning:type: "@apexClassType/..."` |
| 编辑器配置被拒绝 | 使用无效模式（`es_property_editors/inputList`、`itemSchema`）或不识别的顶级键 | 使用 `editor.componentOverrides` 和 `editor.layout`；保持配置最小化 |
| `additionalProperties` 错误在布局属性上 | 向 `lightning/propertyLayout` 添加 `label` 或其他属性 | 在 `lightning/propertyLayout` 中仅使用 `property` 属性。删除 `label`、`title` 或任何其他属性 |
| 无效的 custom LWC 目标配置 | custom LWC 组件的 `-meta.xml` 缺少必需的目标（`lightning__AgentforceInput` 或 `lightning__AgentforceOutput`） | 向 LWC 的 `-meta.xml` 添加正确目标：使用 `lightning__AgentforceInput` 对于编辑器，`lightning__AgentforceOutput` 对于渲染器 |
| 属性映射不存在于类型模式中 | 使用 `{!$attrs.propertyName}`，其中 `propertyName` 未在模式中定义 | 确保所有属性映射引用类型模式 `properties` 部分中的实际属性 |
| 基于 Apex 类 CLT 的自定义 LWC 渲染器上的 `unevaluatedProperties` 错误 | 在 Apex 类 CLT 上使用根覆盖 `attributes` 映射，而 Apex 类 CLT 没有可以验证的 `properties` 块 | 完全从根覆盖中删除 `attributes`；仅使用 `"componentOverrides": { "$": { "definition": "c/<component>" } }` |
| `additionalProperties` 错误与已弃用的键 | 在编辑器/渲染器配置中使用 `propertyRenderers` 或 `view` | 将遗留的 `propertyRenderers` 替换为 `componentOverrides`，将 `view` 替换为 `layout` |
| 组件属性中的类型不匹配 | 为组件属性传递了错误的类型（例如，整数而不是字符串） | 确保属性值与组件预期的类型匹配 |

## 验证检查清单
- [ ] 根模式具有 `type: "object"`、`title`、`lightning:type: "lightning__objectType"` 和 `unevaluatedProperties: false`
- [ ] 根模式在启用严格验证时不包含 `examples`
- [ ] 没有嵌套对象包含 `lightning:type: "lightning__objectType"`
- [ ] 数组被最小化定义（尤其是嵌套数组）
- [ ] 仅使用支持的原始 `lightning:type` 标识符作为叶属性
- [ ] Apex 类 CLT 仅包含 `title`/`description` 和 `lightning:type: "@apexClassType/..."`
- [ ] 包结构和文件名与闪电类型要求匹配
- [ ] 编辑器配置仅使用允许的模式（没有 `es_property_editors/inputList`，没有 `itemSchema`）；使用有效的组件（例如 `es_property_editors/inputText`、`es_property_editors/inputNumber`）或自定义 `c/` 组件
- [ ] 渲染器配置在适用的情况下使用输出样式组件（例如 `es_property_editors/outputText`、`es_property_editors/outputNumber`），而不是输入编辑器
- [ ] 布局配置使用 `lightning/propertyLayout` 仅带有 `property` 属性（没有 `label`、`title` 或其他属性）
- [ ] 所有属性映射（`{!$attrs.propertyName}`）引用类型模式中存在的属性
- [ ] 自定义 LWC 组件在其 `-meta.xml` 中具有正确的目标：`lightning__AgentforceInput` 对于编辑器，`lightning__AgentforceOutput` 对于渲染器
- [ ] 根模式**不包含** `"$schema"` 字段
