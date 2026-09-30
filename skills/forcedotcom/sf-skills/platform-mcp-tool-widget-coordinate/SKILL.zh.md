---
name: platform-mcp-tool-widget-coordinate
description: 配置基于对象的 Lightning 类型 + HXL 组件生成，以渲染由 Apex 调用动作支持的定制 MCP 服务器工具的输出。仅在以下情况下触发：提示明确涉及渲染 MCP 工具结果时：用户说“MCP 服务器”、“MCP 工具”、“定制 MCP 服务器”，引用工具的“输出模式”/“工具输出”/“输出值”包，命名支持 MCP 工具的“调用动作”，或要求为 Apex 调用动作支持的 MCP 工具输出构建组件或富 UI 渲染。以下情况不触发：定制 Apex 支持的代理动作输出（使用 platform-lightning-type-widget-coordinate）、仅编写 Custom Lightning Type（使用 platform-custom-lightning-type-generate）、仅编写 Apex 类（使用 platform-apex-generate），或构建不涉及 Lightning 类型或 MCP 工具的独立组件（使用 platform-widget-generate）。
---

# 使用小部件渲染自定义 MCP 工具输出

协调**两个基于对象的 Custom Lightning Types (CLTs)** 和一个 **HXL 小部件**，以渲染自定义 MCP 服务器工具的输出，该工具的实现是 Apex `@InvocableMethod`。这项技能从不直接创建内容——它按依赖顺序加载并调用子技能，在用户批准后控制进度，并在报告完成前运行验证关卡。

**所有权边界**——这项技能仅拥有：

1. **MCP 工具用例**——解析工具的输出形状并按正确顺序协调子技能；以及
2. **信封 CLT 的默认 `renderer.json`**——它是该技能内联创建的唯一工件，用于将信封连接到小部件。

**CLTs** 由 `platform-custom-lightning-type-generate` 创建，**所有小部件元数据**（模式 + 正文 + `.uiwidget-meta.xml`）由 `platform-widget-generate` 创建和验证。这项技能从不编写小部件元数据，也从不修改 Apex 类——它为每个子技能提供输入并将结果连接在一起。

## 范围

仅限于由 Apex Invocable Action 支持的自定义 MCP 服务器工具。MCP 工具返回平台的 **invocable-action 结果信封**——一个包含 `actionName`、`isSuccess` 和一个携带工具实际有效负载的 `outputValues` 节点的对象。要使用小部件渲染此信封，请将其建模为 **两个基于对象的 CLTs** (`lightning__objectType`)，它们具有同等地位——之所以有两个是因为一个必须通过名称引用另一个（CLT 不能引用自身），因此它们需要不同的部署名称。通过实际建模的内容命名和描述每个，而不是通过发明的角色标签对，如“Payload CLT”/“Envelope CLT”或“Inner CLT”/“Outer CLT”：

- 模仿工具结果信封的 CLT，命名为 `<toolApiName>`。其 `outputValues` 属性通过 `c__<responseCLT>`（CLT 引用前缀——见下文命名空间说明）类型化为另一个 CLT。
- 与 Invocable Action 的 **响应** 完全相同的 CLT（`@InvocableVariable` 字段在 `@InvocableMethod` 响应类上），命名为 `<toolApiName>Response`——“Response”不是一个发明的角色词；它是 Apex 源代码本身用于该类的词。

小部件基于 **响应字段**（扁平的），而信封 CLT 中的 **默认 `renderer.json`** 通过 `{!$attrs.outputValues.<field>}` 将信封嵌套连接到扁平的小部件。

> **命名空间前缀来源 (`c__` / `@apexClassType/<ns>__…`):** Actions REST 描述返回裸的、未加前缀的类名（`Outer$Inner`）和没有命名空间——前缀是 *组织的 CLT 命名空间*，由这项技能添加。在无命名空间的组织（这种情况很常见，本文档中始终使用字面量）中是 `c__`，在打包组织中是包命名空间 `<ns>__`（从类的 `NamespacePrefix` 读取；如果没有命名空间，则默认为 `c`）。下面的每个 `c__` 都是这个前缀。

**超出范围，请转至其他地方：**

- 自定义 Apex 支持的代理动作输出（Apex 支持的 CLT `@apexClassType/...`，单个 CLT，特定于表面的渲染器）→ `platform-lightning-type-widget-coordinate`。
- 没有 MCP 工具 / Lightning Type 的独立小部件 → `platform-widget-generate`。
- 仅创建 CLT 或仅创建 Apex 类 → `platform-custom-lightning-type-generate` / `platform-apex-generate`。

> **Beta 基数：** invocable-action 结果是一个批量数组 (`content[]`)。对于 Beta 版本，这项技能建模和渲染一个 **单个响应**——`content[]` 的第一个元素。CLT 信封建模一个结果对象，而不是 `content[]` 包装器。

---

## 与 `platform-lightning-type-widget-coordinate` 的区别

| 维度 | agent-action flow (`...lightning-type-widget-coordinate`) | 此 MCP 工具 flow |
|---|---|---|
| CLT 类型 | Apex 支持 (`@apexClassType/...`) | 基于对象 (`lightning__objectType`) |
| CLT 数量 | 一个 | **两个**（信封 + 响应） |
| 字段来源 | `@AuraEnabled` | **`@InvocableVariable`** 在顶层响应类上（引用的内部类：公共/`@AuraEnabled`——见硬规则 6） |
| 渲染器位置 | `lightningTypes/<T>/lightningDesktopGenAi/renderer.json`（特定于表面） | `lightningTypes/<toolCLT>/renderer.json`（默认，与 `schema.json` 平行） |
| 渲染器绑定 | 扁平 `{!$attrs.<field>}` | **嵌套 `{!$attrs.outputValues.<field>}`** |

---

## 阶段图

| 阶段 | 目的 | 输出 |
|---|---|---|
| 1 — 输入选择 | 确定有效负载来源：一个 **invocable action API 名称**（首选），一个 Apex Invocable 类，或一个粘贴的工具输出 JSON 示例。 | `source` (`action` \| `apex` \| `sample`), 工具 API 名称 |
| 2 — 有效负载发现 | 通过 Actions REST API 描述 invocable action 并读取其类型化的 `outputs`（或从源解析响应类，或从样本读取 `outputValues`）。 | `payloadFields` (名称 + `lightning:type`) |
| 3 — 构建计划 | 打印完整计划；除非下一个回复明确表示反对，否则继续。 | 打印的计划 |
| 4 — 生成 | 加载并调用子技能：响应 CLT → 信封 CLT → 小部件 → 信封 CLT 中的内联默认渲染器。 | 生成的文件 |
| 5 — 验证 | 运行硬关卡（阻止）和警告关卡（建议）。 | 关卡报告 |
| 6 — 摘要 | 文件、验证、部署顺序、预览准备情况。 | 摘要 |

**每个阶段的模式：** 刷新技能 → 执行其工作流 → 验证输出 → 在下一个阶段之前设置检查点。即使你记得子技能的内容，技能也在不断演变——始终刷新加载。

---

## 阶段 1 — 输入选择

确定有效负载形状来自哪里。按从上到下的顺序优先选择来源：

| 来源 | 触发 | 阶段 2 动作 |
|---|---|---|
| `action` | 提示提供了一个 **invocable action API 名称**——直接提供，或通过解析为该名称的 Apex 类——并且一个经过身份验证的组织可用。**首选。** | 通过 Actions REST API 描述该 action 并读取其类型化的 `outputs`。 |
| `sample` | 没有可访问的组织（或描述 404 错误），但一个粘贴的工具输出 JSON 示例可用。 | 从样本解析 `outputValues` 对象。 |
| `apex` | 仅提供 Apex **类**（没有可访问的组织，没有可访问的 action 名称，没有样本）——仅作为后备，可能与实际部署的内容不一致。 | 解析响应类并枚举 `@InvocableVariable` 字段。 |

捕获 **工具 API 名称**（用于命名所有工件——见下文命名约定）。

**来源优先级：** 活动或权威模式来源优先于解析本地类，其次是粘贴的示例。顺序：
1. **`action`** 如果提供 action API 名称和一个经过身份验证的组织。Actions REST API 描述与平台本身暴露的模式相同，因此不需要请求/助手过滤，并给出真实的字段类型。
2. **`sample`** 如果粘贴了运行时 JSON 示例（运行时响应——明确且当前）。
3. **`apex`** 如果本地存在 Apex 类，并且以上都不适用（仅作为后备——可能与实际部署的内容不一致）。

如果没有可用，停止并要求用户提供 action 名称、类、样本或模式。

---

## 阶段 2 — 有效负载发现

首先阅读 `references/mcp-tool-output-discovery.md`（必需——不要仅从本摘要中运行阶段 2），然后执行为所选来源指定的程序。参考是权威的，用于每个来源的完整程序、字段类型映射表和嵌套/列表处理；下面的指针仅是到它的映射：

- **`action`（首选）：** 通过 `sf api request rest '/services/data/v<APIVER>/actions/custom/apex/<ActionApiName>' -o <org>` 描述；仅使用 `outputs` 数组（**忽略 `inputs`**——请求包装器）；不区分大小写地将每个 `type` 映射到 CLT `lightning:type`。具有 `"type": null` 和一个 `"apexClass": "<Outer>$<Inner>"` 键的条目是 Apex 类类型的字段（不是描述差距）：`maxOccurs: 1` → 单个嵌套对象，`maxOccurs > 1` → 顶层列表。如果描述 404 错误，则回退到 `sample` 然后到 `apex`。
- **`apex`（后备）：** 定位类，识别响应类（`@InvocableMethod` 返回 `List<...>` 元素类型），枚举其 `@InvocableVariable` 字段（**排除**请求类和 `private` 助手），将 Apex 类型映射到 CLT 类型。
- **`sample`（后备）：** 解析 `outputValues` 对象；从其 JSON 值推断每个字段的 `lightning:type`。

**嵌套对象和列表字段（每个来源，扁平原始字段的附加）：** 将字段类型化为另一个 Apex 类——单个对象（`maxOccurs: 1`）、顶层列表（`maxOccurs > 1`）或包装对象内部的列表（描述返回一个 `maxOccurs: 1` `apexClass` 输出并隐藏内部列表）——在范围内，并且**永远不会**建模为裸的 `{"type":"object"}` 或内联的 `lightning__objectType`。在响应 CLT 中将其类型化为 `@apexClassType/c__<Outer>$<Inner>`（**永远不会**在 CLT 级别使用 `lightning__listType`/`items`），枚举引用/内部类的公共/`@AuraEnabled` 成员（见硬规则 6），并且当子技能本身是类时递归。每个形状的 CLT 类型化和渲染绑定深度在 `references/mcp-tool-output-discovery.md` 和 `references/two-clt-modeling.md`（“顶层列表与列表在包装器内”）中——还有硬规则 4、6、14——以及 `examples/nested-object-*-source-prompt.md` 演示。

捕获 `payloadFields`——定义响应 CLT 和小部件模式的 `{ name, title, lightning:type }` 有序列表。在构建计划中记录它是由哪个来源产生的。

> 陈旧性：**不要维护跨会话缓存**。每次会话重新读取本地项目并从组织中重新检索。

---

## 阶段 3 — 构建计划 + 批准关卡

使用 `references/build-plan-format.md` 中的模板打印构建计划。计划必须列出：

- 一行面向开发者的摘要（`PLAN:` 行）。
- 工具 API 名称和响应类 FQN（或“来自粘贴的样本”）。
- 两个 CLT 名称（信封 + 有效负载）和 小部件名称，以及绝对路径。
- **信封 CLT 携带 `actionName`（文本）、`isSuccess`（布尔值）和 `outputValues`**（类型化为 `c__<responseCLT>`，渲染器通过它桥接的承重字段）——`actionName`/`isSuccess` 是信封专用的，永远不会出现在小部件上（硬规则 5）——以及响应 CLT + 小部件将携带的响应字段。
- 生成后将运行的验证。

**打印完整计划，然后除非用户下一个回复明确反对，否则继续。** 明确反对 = `no`、`stop`、`wait`、`change X`、`use Y instead` 或等效拒绝/修订请求。明确批准是受欢迎的，但**不是必需的**——沉默、不相关的后续内容或单回合评估的自然延续都视为隐式批准。不变量是计划在转录中可见。如果收到反对，则在继续之前修订并重新打印。

---

## 阶段 4 — 生成

按此顺序加载并调用子技能。对于每个子技能：加载技能，针对阶段 3 规范执行其工作流，验证输出，并在下一个之前设置检查点。

1. **响应 CLT** — 加载 `platform-custom-lightning-type-generate`。创建一个基于对象的 CLT `<responseCLT>`（约定：`<toolApiName>Response`），其 `properties` 是阶段 2 的 `payloadFields`。根是 `lightning__objectType`，根级别的 `"lightning:tags": ["mcp"]`。
   - **响应 CLT 的顶层属性与描述的 `outputs[]` 名称一对一对应**（或对于 `apex`/`sample`，与响应类的 `@InvocableVariable` 字段对应——与描述显示的相同）。具有 **N 个兄弟输出**的描述 → **N 个扁平属性**；具有 **一个输出**的描述 → **一个以该输出命名的属性**。只有一个属性的 CLT 仅当描述本身返回单个输出时才是正确的。
   - **永远不要将多个兄弟输出合并为一个发明的包装属性。** 将一个属性命名为包含多个输出发明了一个在**没有任何描述输出**中的键，并且无法在 `action` 来源下解析——响应类名称永远不会出现在 `outputs[]` 中。每个响应 CLT 属性名称必须追溯到描述输出名称（见 `field-trace` / `clt-reference-integrity`）。
   - 顶层列表输出直接类型化为其元素类（`@apexClassType/c__<Outer>$<ElementClass>`），而不是包装——见上面的“嵌套对象的列表”。

2. **信封 CLT** — 加载 `platform-custom-lightning-type-generate`。创建一个基于对象的 CLT `<toolCLT>`（约定：`<toolApiName>`，信封），也具有根级别的 `"lightning:tags": ["mcp"]`，并：
   - `actionName` → `lightning__textType`
   - `isSuccess` → `lightning__booleanType`
   - `outputValues` → **`c__<responseCLT>`**（引用 CLT 模式；响应 CLT 必须在信封 CLT 部署之前）

3. **小部件** — 加载 `platform-widget-generate`。创建一个**扁平**的小部件，其 `schema.json` 属性是 `payloadFields`（名称 + 原始类型）——一个独立的小部件合同，不是从任何 Lightning Type 派生或耦合的。它渲染**仅 `outputValues` 数据字段**：永远不会 `actionName`/`isSuccess`（信封专用的）。小部件正文通过 `{!$attrs.<field>}` 绑定每个字段——小部件是信封无关的，并且永远不会引用 `outputValues` 本身。

4. **默认渲染器（在信封 CLT 中内联创建——永远不会是可选的）。** 首先阅读 `platform-custom-lightning-type-generate/references/widget-rendition.md`（必需——不要凭记忆或复制现有示例，这可能使用已弃用的形状）。然后创建 `<pkgDir>/lightningTypes/<toolCLT>/renderer.json`——**默认渲染器，在包根目录下，与 `schema.json` 平行**（**不**在 `lightningDesktopGenAi/` 下）。其 `renderer.componentOverrides["$"]` 将 `definition` 设置为 `@widget/c/<widgetName>`，并将**每个小部件模式属性**通过 `{!$attrs.outputValues.<payloadField>}` 映射到嵌套在信封的 `outputValues` 节点下的匹配有效负载字段——将信封 CLT 连接到扁平小部件的嵌套绑定。**不要**在 `renderer.json` 中重复小部件正文。工作 JSON 在 `references/two-clt-modeling.md` 中。

**现有渲染器处理：** 如果在目标路径存在 `renderer.json`，则首先读取它。如果它引用相同的小部件并具有相同的绑定，则保留它。如果它引用不同的小部件或自定义-LWC 根级覆盖（`c/<component>`），则停止并在覆盖之前显示冲突。

---

## 阶段 5 — 验证关卡

阅读 `references/validation-gates.md`（必需——它包含每个关卡的 RUN 程序和精确的通过/失败谓词）并**运行每个关卡**。小部件包内部的检查（模式解析、根键、子类型、`{!$attrs.X}` 解析、`.uiwidget-meta.xml` 格式正确性）由 `platform-widget-generate` 拥有，并在其自己的自验证中运行。

**硬性——失败时阻止：**

1. `clt-reference-integrity` — 信封 `outputValues` 类型化为 `c__<responseCLT>`，响应 CLT 存在且两者都能解析，没有 `$schema`/`items`，每个非原始响应属性都是 `@apexClassType/...` 引用（**永远不会**是裸对象或 CLT 级别的 `lightning__listType`）。
2. `renderer-wires-widget` — 包根目录的 `renderer.json` 连接 `@widget/c/<widgetName>` 并在描述指定的深度（顶层原始或列表输出为两个段，包装对象内部的嵌套/列表为三个段）下绑定每个小部件属性。双向：缺少或多余的绑定都失败。
3. `nested-list-coverage` — 阶段 2 中发现的每个嵌套对象和列表字段都由小部件在正确深度渲染。**“超出范围” / “beta 单个响应”不是有效的放弃理由**。

**警告——建议：**

1. `field-trace` — 在 `references/validation-gates.md` 中运行跟踪：枚举响应字段，`jq` 小部件模式键，分类 INVENTED vs OMITTED。发明的字段会失败；遗漏的响应数据字段会警告。

按名称报告第 6 阶段的每个门结果（`pass`、`fail (<reason>)`、`warn (<reason>)`、`not run`）。**不要**总结为“全部通过”。这项技能仅生成元数据——它不进行部署；部署是调用者的责任。

---

## 第 6 阶段——摘要

```text
MCP 工具小部件构建完成： <widgetName>

生成的文件：
  响应 CLT：
    <pkgDir>/lightningTypes/<responseCLT>/schema.json
  信封 CLT：
    <pkgDir>/lightningTypes/<toolCLT>/schema.json
    <pkgDir>/lightningTypes/<toolCLT>/renderer.json          # 默认渲染器——连接小部件
  小部件包：
    <pkgDir>/uiWidgets/<widgetName>/<widgetName>.json
    <pkgDir>/uiWidgets/<widgetName>/schema.json
    <pkgDir>/uiWidgets/<widgetName>/<widgetName>.uiwidget-meta.xml

验证：
  小部件自验证（platform-widget-generate 门）： <pass | fail — 请参阅子技能报告>
  clt 引用完整性（envelope.outputValues → c__<responseCLT>；嵌套 → @apexClassType）： <pass | fail (<reason>)>
  渲染器连接小部件（嵌套 {!$attrs.outputValues.X} 绑定）： <pass | fail (<reason>)>
  嵌套列表覆盖率（每个发现的嵌套/列表字段都渲染）： <pass | fail (<reason>)>
  字段跟踪（INVENTED + OMITTED 列表打印）： <pass | warn (<reason>) | fail (invented: <list>)>
```

---

## 硬性规则（始终适用）

1. **先计划，再执行。** 在编写任何文件之前，打印完整的第 3 阶段构建计划。明确的拒绝或变更请求→停止并修订；否则继续。不变量是计划在转录中可见，而不是交互式人工批准——这在手动聊天、代理到代理的流程和单次评估中都适用。
2. **两个基于对象的 CLT，永不一个。** 信封和有效负载是分开的 CLT。信封的 `outputValues` 通过 `c__<responseCLT>` 进行类型化，永不内联为嵌套的 `lightning__objectType`。两个 CLT 都包含根级别的 `"lightning:tags": ["mcp"]`（参见 `platform-custom-lightning-type-generate/assets/primitive-types-and-constraints.md`）。
3. **渲染器位于信封 CLT 的包根目录。** `lightningTypes/<toolCLT>/renderer.json` — 默认渲染器，与 `schema.json` 平行。永不 `lightningDesktopGenAi/renderer.json`（那是代理动作流程的表面特定路径），永不位于响应 CLT。
4. **渲染器绑定是嵌套的。** 每个小部件属性映射到 `{!$attrs.outputValues.<field>}`，而不是 `{!$attrs.<field>}`。小部件模式保持扁平；渲染器负责桥接。
5. **小部件基于有效负载，而非信封。** 小部件模式属性是有效负载（`outputValues`）字段。小部件从不引用 `actionName` 或 `isSuccess` — 那些是信封 CLT 上的信封专用字段。
6. **字段源取决于类角色。** **顶层响应类** 由 `@InvocableVariable` 控制 — 描述表面仅显示那些字段，因此仅携带 `@AuraEnabled`（或无注解）的顶层字段正确地*不是*输出；通过 `@InvocableVariable` 列出顶层响应类并排除请求类和私有辅助类。通过 `@apexClassType/<ns>__<Outer>$<Inner>` 访问的**内部/引用类**通过其**公共 / `@AuraEnabled`** 成员进行枚举——其叶子节点永远不会在描述中，`@InvocableVariable` 在此处不使用，因此搜索 `@InvocableVariable` 产生零叶子（空 CLT + 小部件）。
7. **无虚构字段。** 小部件模式（以及响应 CLT）必须是工具实际暴露的字段的子集——顶层 `@InvocableVariable` 输出加上任何引用内部类的公共/`@AuraEnabled` 叶子——永不暴露任何类未公开的属性。`field-trace` 打印两个列表。
8. **beta 版本单个响应。** 模型一个结果对象，而不是 `content[]` 批量包装。
9. **始终在生成前加载叶子技能。** 不要从记忆中编写。
10. **运行门，不要描述它们。** 未执行门就报告 `pass` 是硬性违规；报告 `not run` 代替。
11. **无触发 Vibes 安全 shell 过滤器的 shell 伪字符。** 在此编排器发出的以及它调用的任何叶子技能发出的每个 `Bash` 工具调用中，**不要**使用命令替换（`$(…)` 或反引号）、过程替换（`<(…)`, `>(…)`）、大括号扩展（`{a,b,c}` 或 `{1..N}`）或 `eval` / `exec`。这些强制手动批准，即使在绕过模式下也会停滞评估。运行单独命令（`mkdir -p a && mkdir -p b`），用各自的命令和原因打印每个中间值，并在必须重用值时使用普通 shell 变量（`X=literal`）或 here-strings。
12. **从 Actions REST API 描述解析 `action` 模式，永不从原始 HTTP 到 MCP 端点或从凭证提取。** 使用 `sf api request rest` 对组织的 Actions REST API（它使用现有的 `sf` 组织认证）。永不读取 `a4d_mcp_settings.json` 或任何 MCP 设置文件，永不提取组织访问令牌，永不直接 `curl` MCP 服务器端点——那需要会话没有的凭证，并且目标 URL 实际上不会以这种方式暴露。
13. **永不调用 MCP 工具来发现其输出形状。** 描述有效负载绝不能执行底层动作。通过支持动作的 Actions REST API 描述解析模式——永不通过调用工具并使用样本/猜测输入来观察响应。如果无法解析动作名称，请要求用户粘贴 `sample` 而不是调用任何东西。
14. **将响应字段类型化为另一个 Apex 类时，永远不会是裸的 `{"type":"object"}`。** 在响应 CLT 中将其类型化为 `@apexClassType/<ns>__<OuterClass>$<InnerClass>`，在渲染器中将其扁平化为其叶子字段，并绑定两层的渲染器（`{!$attrs.outputValues.<objectField>.<leaf>}`）。这是对扁平原始情况的补充（硬性规则 5），而不是它的替代品——参见 `references/two-clt-modeling.md`。

---

## 参考文件索引

| 文件 | 何时读取 |
|------|--------------|
| `references/mcp-tool-output-discovery.md` | 第 2 阶段 — 三个来源、字段枚举和类型映射。 |
| `references/two-clt-modeling.md` | 第 4 阶段 — 信封 + 响应 CLT、嵌套渲染器绑定、命名约定和嵌套对象处理。 |
| `references/build-plan-format.md` | 第 3 阶段 — 计划模板。 |
| `references/validation-gates.md` | 第 5 阶段 — 完整的硬性/警告门表，包括 RUN 程序。 |
| `examples/action-name-source-prompt.md` | 第 3 阶段 — 从可调用的动作 API 名称（首选）。 |
| `examples/apex-invocable-source-prompt.md` | 第 3 阶段 — 从 Apex 可调用类（后备）。 |
| `examples/pasted-tool-output-prompt.md` | 第 3 阶段 — 从粘贴的工具输出样本（后备）。 |
| `examples/nested-object-single-source-prompt.md` | 第 3 阶段 — 单个 Apex 类引用的有效负载字段。 |
| `examples/nested-object-list-source-prompt.md` | 第 3 阶段 — 顶层列表和列表在包装器内。 |
