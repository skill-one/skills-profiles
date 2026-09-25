# 使用小部件渲染自定义 MCP 工具输出

协调**两个基于对象的 Custom Lightning Types (CLTs)** 和一个 **HXL 小部件**，以渲染自定义 MCP 服务器工具的输出，该工具的实现是一个 Apex `@InvocableMethod`。这项技能从不直接创建内容——它按依赖顺序加载和调用子技能，在用户批准的情况下控制进度，并在报告完成之前运行验证关卡。

**所有权边界**——这项技能仅拥有：

1.  **MCP 工具用例**——解析工具的输出形状并按正确顺序协调子技能；以及
2.  **信封 CLT 的默认 `renderer.json`**——它是该技能内联创建的唯一工件，用于将信封连接到小部件。

CLTs 由 `platform-custom-lightning-type-generate` 创建，**所有小部件元数据**（模式 + 正文 + `.uiwidget-meta.xml`）由 `platform-widget-generate` 创建和验证。这项技能从不编写小部件元数据，也从不修改 Apex 类——它为每个子技能提供输入并将结果连接在一起。

## 范围

仅支持由 Apex Invocable Action 支持的自定义 MCP 服务器工具。MCP 工具返回平台的 **invocable-action 结果信封**——一个包含 `actionName`、`isSuccess` 和一个携带工具实际有效负载的 `outputValues` 节点的对象。要使用小部件渲染此信封，请将其建模为两个具有同等地位的 **基于对象的 CLTs** (`lightning__objectType`)——之所以有两个是因为一个必须通过名称引用另一个（CLT 不能引用自身），因此它们需要不同的部署名称。通过实际建模的内容命名每个，而不是通过发明的角色标签对，如“有效负载 CLT”/“信封 CLT”或“内部 CLT”/“外部 CLT”：

- 仿真工具结果信封的 CLT，命名为 `<toolApiName>`。其 `outputValues` 属性通过 `c__<responseCLT>`（CLT 引用前缀——见下文命名空间说明）类型化为另一个 CLT。
- 精确形状为 Invocable Action 响应的 CLT（`@InvocableVariable` 字段在 `@InvocableMethod` 响应类上），命名为 `<toolApiName>Response`——“Response”不是一个发明的角色词；它是 Apex 源代码本身用于该类的词。

小部件基于**响应字段**（扁平），信封 CLT 中的**默认 `renderer.json`** 通过 `{!$attrs.outputValues.<field>}` 将信封嵌套连接到扁平小部件。

> **命名空间前缀来源 (`c__` / `@apexClassType/<ns>__…`):** Actions REST 描述返回裸的、未加前缀的类名（`Outer$Inner`）并且没有命名空间——前缀是*组织的 CLT 命名空间*，由这项技能添加。在无命名空间的组织中（这是常见情况，在本文档中始终使用字面量）是 `c__`，在打包组织中是包命名空间 `<ns>__`（从类的 `NamespacePrefix` 读取；如果没有组织的命名空间，则默认为 `c`）。下面的每个 `c__` 都是此前缀。

**超出范围，另寻途径：**

- 自定义 Apex 支持的代理动作输出（Apex 支持的 CLT `@apexClassType/...`，单个 CLT，特定于表面的渲染器）→ `platform-lightning-type-widget-coordinate`。
- 没有 MCP 工具 / Lightning Type 的独立小部件 → `platform-widget-generate`。
- 仅创建 CLT 或仅创建 Apex 类 → `platform-custom-lightning-type-generate` / `platform-apex-generate`。

> **Beta 基数：** invocable-action 结果是一个批量数组（`content[]`）。对于 Beta 版本，这项技能建模和渲染**单个响应**——`content[]` 的第一个元素。CLT 信封建模一个结果对象，而不是 `content[]` 包装器。

---

## 范围

仅支持由 Apex Invocable Action 支持的自定义 MCP 服务器工具。MCP 工具返回平台的 **invocable-action 结果信封**——一个包含 `actionName`、`isSuccess` 和一个携带工具实际有效负载的 `outputValues` 节点的对象。要使用小部件渲染此信封，请将其建模为两个具有同等地位的 **基于对象的 CLTs** (`lightning__objectType`)——之所以有两个是因为一个必须通过名称引用另一个（CLT 不能引用自身），因此它们需要不同的部署名称。之所以有两个 CLT 是因为一个必须通过名称引用另一个（CLT 不能引用自身），所以它们需要不同的部署名称。命名和描述每个时，要按实际建模的内容命名——不要用发明的角色标签对，如“Payload CLT”/“Envelope CLT”或“Inner CLT”/“Outer CLT”：

- 仿真工具结果信封的 CLT，命名为 `<toolApiName>`。其 `outputValues` 属性通过 `c__<responseCLT>`（CLT 引用前缀——见下文命名空间说明）类型化为另一个 CLT。
- 精确形状为 Invocable Action 响应的 CLT（`@InvocableVariable` 字段在 `@InvocableMethod` 响应类上），命名为 `<toolApiName>Response`——“Response”不是一个发明的角色词；它是 Apex 源代码本身用于该类的词。

小部件基于**响应字段**（扁平），信封 CLT 中的**默认 `renderer.json`** 通过 `{!$attrs.outputValues.<field>}` 将信封嵌套连接到扁平小部件。

> **命名空间前缀来源 (`c__` / `@apexClassType/<ns>__…`):** Actions REST 描述返回裸的、未加前缀的类名（`Outer$Inner`）并且没有命名空间——前缀是*组织的 CLT 命名空间*，由这项技能添加。在无命名空间的组织中（这是常见情况，在本文档中始终使用字面量）是 `c__`，在打包组织中是包命名空间 `<ns>__`（从类的 `NamespacePrefix` 读取；如果没有组织的命名空间，则默认为 `c`）。下面的每个 `c__` 都是此前缀。

**超出范围，另寻途径：**

- 自定义 Apex 支持的代理动作输出（Apex 支持的 CLT `@apexClassType/...`，单个 CLT，特定于表面的渲染器）→ `platform-lightning-type-widget-coordinate`。
- 独立小部件，没有 MCP 工具 / Lightning Type → `platform-widget-generate`。
- 仅创建 CLT 或仅创建 Apex 类 → `platform-custom-lightning-type-generate` / `platform-apex-generate`。

> **Beta 基数：** invocable-action 结果是一个批量数组（`content[]`）。对于 Beta 版本，这项技能建模和渲染**单个响应**——`content[]` 的第一个元素。CLT 信封建模一个结果对象，而不是 `content[]` 包装器。

---

## 与 `platform-lightning-type-widget-coordinate` 的区别

| 维度 | agent-action 流 (`...lightning-type-widget-coordinate`) | 这项 MCP 工具流 |
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
| 1 — 输入选择 | 确定有效负载来源：一个 **invocable action API 名称**（首选）、一个 Apex Invocable 类，或一个粘贴的工具输出 JSON 示例。 | `source` (`action` \| `apex` \| `sample`), 工具 API 名称 |
| 2 — 有效负载发现 | 通过 Actions REST API 描述 invocable action 并读取其类型化的 `outputs`（或从源解析响应类，或从样本读取 `outputValues`）。 | `payloadFields` (名称 + `lightning:type`) |
| 3 — 构建计划 | 完整打印计划；除非下一个回复明确反对，否则继续。 | 打印的计划 |
| 4 — 生成 | 加载和调用子技能：响应 CLT → 信封 CLT → 小部件 → 信封 CLT 中的内联默认渲染器。 | 生成的文件 |
| 5 — 验证 | 运行硬关卡（阻止）和警告关卡（建议）。 | 关卡报告 |
| 6 — 摘要 | 文件、验证、部署顺序、预览准备情况。 | 摘要 |

**每个阶段的模式：** 刷新技能 → 执行其工作流 → 验证输出 → 在下一个阶段之前设置检查点。即使你记得子技能的内容，技能也会演变——始终刷新加载。

---

## 阶段 1 — 输入选择

确定有效负载形状的来源。按从上到下的顺序优先选择来源：

| 来源 | 触发器 | 阶段 2 动作 |
|---|---|---|
| `action` | 提示提供 **invocable action API 名称**——直接提供，或通过解析为该名称的 Apex 类提供——并且一个经过身份验证的组织可用。**首选。** | 通过 Actions REST API 描述该 action 并读取其类型化的 `outputs`。 |
| `sample` | 没有可访问的组织（或描述 404），但一个粘贴的工具输出 JSON 示例可用。 | 从样本解析 `outputValues` 对象。 |
| `apex` | 仅提供 Apex **类**（没有可访问的组织，没有可访问的 API 名称，没有样本）——仅作为后备，可能与实际部署的版本不一致。 | 解析响应类并枚举 `@InvocableVariable` 字段。 |

捕获 **工具 API 名称**（用于命名所有工件——见下文命名约定）。

**来源优先级：** 活动或权威的模式来源优先于解析本地类，其次是粘贴的示例。按顺序：

1.  **`action`** 如果提供 action API 名称和一个经过身份验证的组织。Actions REST API 描述与平台本身公开的模式相同，因此不需要请求/助手过滤，并给出实际的字段类型。
2.  **`sample`** 如果粘贴了运行时 JSON 示例（运行时响应——明确且当前）。
3.  **`apex`** 如果本地存在 Apex 类并且上述都不适用（仅作为后备——可能与实际部署的版本不一致）。

如果没有可用，停止并要求用户提供 action 名称、类、样本或模式。

---

## 阶段 2 — 有效负载发现

首先阅读 `references/mcp-tool-output-discovery.md`（必需——不要单独从本摘要运行阶段 2），然后执行为所选来源指定的程序。参考是权威的，用于每个来源的完整程序、字段类型映射表和嵌套/列表处理；下方的指针仅是映射：

- **`action`（首选）：** 通过 `sf api request rest '/services/data/v<APIVER>/actions/custom/apex/<ActionApiName>' -o <org>` 描述；仅使用 `outputs` 数组（**忽略 `inputs`**——请求包装）；不区分大小写地将每个 `type` 映射到 CLT `lightning:type`。具有 `"type": null` 和一个 `"apexClass": "<Outer>$<Inner>"` 键的条目是 Apex 类类型的字段（不是描述差距）：`maxOccurs: 1` → 单个嵌套对象，`maxOccurs > 1` → 顶层列表。如果描述 404，则回退到 `sample` 然后到 `apex`。
- **`apex`（后备）：** 定位类，识别响应类（`@InvocableMethod` 返回 `List<...>` 元素类型），枚举其 `@InvocableVariable` 字段（**排除**请求类和 `private` 辅助类），将 Apex 类型映射到 CLT 类型。
- **`sample`（后备）：** 解析 `outputValues` 对象；从其 JSON 值推断每个字段的 `lightning:type`。

**嵌套对象和列表字段（每个来源，附加到扁平原语的情况）：** 将字段类型化为另一个 Apex 类——单个对象（`maxOccurs: 1`）、顶层列表（`maxOccurs > 1`）或包装对象内部的列表（描述返回一个 `maxOccurs: 1` `apexClass` 输出并隐藏内部列表）——是**在范围内的**并且**永远不会**建模为裸的 `{"type":"object"}` 或内联的 `lightning__objectType`。在响应 CLT 中将其类型化为 `@apexClassType/c__<Outer>$<Inner>`，枚举引用的/内部类通过其**公共 / `@AuraEnabled`** 成员（硬规则 6），当子技能本身是类时递归。每个形状的 CLT 类型化和渲染绑定深度位于 `references/mcp-tool-output-discovery.md` 和 `references/two-clt-modeling.md`（“顶层列表与列表在包装器内部”）——也见硬规则 4、6、14——以及 `examples/nested-object-*-source-prompt.md` 漫游。

捕获 `payloadFields`——定义响应 CLT 和小部件模式的 `{ name, title, lightning:type }` 有序列表。在构建计划中记录它是由哪个来源产生的。

> 陈旧性：不要维护跨会话缓存。每次会话都刷新本地项目并从组织中重新检索。

---

## 阶段 3 — 构建计划 + 批准关卡

使用 `references/build-plan-format.md` 中的模板打印构建计划。计划必须列出：

- 一行面向开发者的摘要（`PLAN:` 行）。
- 工具 API 名称和响应类 FQN（或“来自粘贴的样本”）。
- 两个 CLT 名称（信封 + 有效负载）和 小部件名称，以及绝对路径。
- **信封 CLT 恰好携带 `actionName`（文本）、`isSuccess`（布尔值）和 `outputValues`**（类型化为 `c__<responseCLT>`，渲染器通过它连接到扁平小部件）——`actionName`/`isSuccess` 仅限于信封，永远不会出现在小部件上（硬规则 5）——以及响应 CLT + 小部件将携带的响应字段。
- 生成后将要运行的验证。

**完整打印计划，然后除非用户下一个回复明确反对，否则继续。** 明确反对 = `no`，`stop`，`wait`，`change X`，`use Y instead`，或等效的拒绝/修订请求。明确批准是受欢迎的，但**不是必需的**——沉默、不相关的后续内容或单回合评估的所有内容都视为隐式批准。不变量是计划在转录中可见。如果收到反对，则在继续之前修订并重新打印。

---

## 阶段 4 — 生成

按此顺序加载和调用子技能。对于每个子技能：加载技能，针对阶段 3 规范执行其工作流，验证输出，在下一个子技能之前设置检查点。

1.  **响应 CLT** — 加载 `platform-custom-lightning-type-generate`。创建一个基于对象的 CLT `<responseCLT>`（约定：`<toolApiName>Response`），其 `properties` 是阶段 2 的 `payloadFields`。根是 `lightning__objectType`，具有根级别的 `"lightning:tags": ["mcp"]`。
    - **响应 CLT 的顶层属性与描述的 `outputs[]` 名称一对一对应**（或，对于 `apex`/`sample`，响应类的 `@InvocableVariable` 字段——描述会显示相同的字段集）。描述具有 **N 个同级输出** → **N 个扁平属性**；描述具有 **一个输出** → **一个以该输出命名的属性**。只有一个属性的 CLT 仅当描述本身返回单个输出时才是正确的。 
    - **永远不要将多个同级输出合并为一个发明的包装属性。** 将一个单独的属性命名为包含多个输出的属性发明了一个**在没有任何描述输出中**的键，并且无法在 `action` 来源下解析——响应类名称永远不会出现在 `outputs[]` 中。每个响应 CLT 属性名称必须追溯到描述输出名称（见 `field-trace` / `clt-reference-integrity`）。
    - 顶层列表输出直接类型化为其元素类（`@apexClassType/c__<Outer>$<ElementClass>`），而不是包装——见上文的“嵌套对象的列表”。

2.  **信封 CLT** — 加载 `platform-custom-lightning-type-generate`。创建一个基于对象的 CLT `<toolCLT>`（约定：`<toolApiName>`，信封），也具有根级别的 `"lightning:tags": ["mcp"]`，并：
    - `actionName` → `lightning__textType`
    - `isSuccess` → `lightning__booleanType`
    - `outputValues` → **`c__<responseCLT>`**（引用 CLT 模式；响应 CLT 必须先部署，然后才能部署信封 CLT）

3.  **小部件** — 加载 `platform-widget-generate`。创建一个**扁平**小部件，其 `schema.json` 属性是 `payloadFields`（名称 + 原始类型）——一个独立的小部件合同，不是从任何 Lightning Type 派生或与之耦合。它仅渲染**`outputValues` 数据字段**：永远不会 `actionName`/`isSuccess`（仅限于信封）。小部件正文通过 `{!$attrs.<field>}` 绑定每个字段——小部件是信封无关的，永远不会引用 `outputValues`。

4.  **默认渲染器**（内联创建于信封 CLT——永远不会可选）。首先阅读 `platform-custom-lightning-type-generate/references/widget-rendition.md`（必需——不要凭记忆或复制现有样本，这可能使用已弃用的形状）。然后创建 `<pkgDir>/lightningTypes/<toolCLT>/renderer.json`——**默认渲染器，位于包根目录，与 `schema.json` 平行**（**不**在 `lightningDesktopGenAi/` 下）。其 `renderer.componentOverrides["$"]` 将 `definition` 设置为 `@widget/c/<widgetName>` 并将**每个小部件模式属性**通过 `{!$attrs.outputValues.<payloadField>}` 映射到匹配的有效负载字段，嵌套在信封的 `outputValues` 节点下——将信封 CLT 与扁平小部件连接起来的嵌套绑定。**不要**在 `renderer.json` 中复制小部件正文。工作 JSON 位于 `references/two-clt-modeling.md`。

**现有渲染器处理：** 如果在目标路径存在 `renderer.json`，则首先读取它。如果它引用了相同的小部件并具有相同的绑定，则保留它。如果它引用了不同的小部件或自定义 LWC 根级覆盖（`c/<component>`），则停止并在覆盖之前显示冲突。

---

## 阶段 5 — 验证关卡

阅读 `references/validation-gates.md`（必需——它包含每个关卡的 RUN 程序和精确的通过/失败谓词）并**运行每个关卡**。小部件包内部的检查（模式解析、根键、子类型、`{!$attrs.X}` 解析、`.uiwidget-meta.xml` 格式正确性）由 `platform-widget-generate` 拥有，并在其自己的自我验证中运行。

**硬性——失败阻止：**

1.  `clt-reference-integrity` — 信封 `outputValues` 类型化为 `c__<responseCLT>`，响应 CLT 存在且两者都能解析，没有 `$schema`/`items`，每个非原语响应属性都是 `@apexClassType/...` 引用（永远不会是裸对象或 CLT 级别的 `lightning__listType`）。
2.  `renderer-wires-widget` — 包根目录的 `renderer.json` 连接 `@widget/c/<widgetName>` 并在描述指定的深度（顶层原语或列表输出为两个段，包装对象内部的嵌套/列表为三个段）。双向：缺少或额外的绑定都失败。
3.  `nested-list-coverage` — 在阶段 2 中发现的每个嵌套对象和列表字段都由小部件在正确的深度渲染。**“超出范围” / “beta 单个响应”不是有效的放弃理由**。

**警告——建议：**

1.  `field-trace` — 在 `references/validation-gates.md` 中运行跟踪：枚举响应字段，`jq` 小部件模式键，分类 INVENTED vs OMITTED。发明的字段会失败；省略的响应数据字段会警告。

按名称在阶段 6 中报告每个关卡结果（`pass`，`fail (<reason>)`，`warn (<reason>)`，`not run`）。**不要**总结为“所有通过”。这项技能只生成元数据——它不会部署；部署是调用者的责任。

---

## 阶段 6 — 摘要

```text
MCP 工具小部件构建完成: <widgetName>

生成的文件:
  响应 CLT:
    <pkgDir>/lightningTypes/<responseCLT>/schema.json
  信封 CLT:
    <pkgDir>/lightningTypes/<toolCLT>/schema.json
    <pkgDir>/lightningTypes/<toolCLT>/renderer.json          # 默认渲染器——连接小部件
  小部件包:
    <pkgDir>/uiWidgets/<widgetName>/<widgetName>.json
    <pkgDir>/uiWidgets/<widgetName>/schema.json
    <pkgDir>/uiWidgets/<widgetName>/<widgetName>.uiwidget-meta.xml

验证:
  小部件自我验证 (platform-widget-generate 关卡): <pass | fail — 见子技能报告>
  clt-reference-integrity (envelope.outputValues → c__<responseCLT>; 嵌套 → @apexClassType): <pass | fail (<reason>)>
  renderer-wires-widget (嵌套 {!$attrs.outputValues.X} 绑定): <pass | fail (<reason>)>
  nested-list-coverage (每个发现的嵌套/列表字段都渲染): <pass | fail (<reason>)>
  field-trace (INVENTED + OMITTED 列表打印): <pass | warn (<reason>) | fail (invented: <list>)>
```

---

## 硬性规则（始终适用）

1.  **先计划，再进行。** 在写入任何文件之前完整打印阶段 3 的构建计划。明确拒绝或更改请求→停止并修订；否则继续。不变量是计划在转录中可见，而不是交互式人类批准——这在手动聊天、代理到代理流程和单回合评估中都适用。
2.  **两个基于对象的 CLTs，永远不会一个。** 信封和有效负载是分开的 CLTs。信封的 `outputValues` 通过 `c__<responseCLT>` 类型化，永远不会内联为嵌套的 `lightning__objectType`。两个 CLTs 都携带根级别的 `"lightning:tags": ["mcp"]`（见 `platform-custom-lightning-type-generate/assets/primitive-types-and-constraints.md`）。
3.  **渲染器位于信封 CLT 中，在包根目录。** `lightningTypes/<toolCLT>/renderer.json`——默认渲染器，与 `schema.json` 平行。永远不会 `lightningDesktopGenAi/renderer.json`（那是代理动作流程的特定于表面的路径），永远不会在响应 CLT 中。
4.  **渲染器绑定是嵌套的。** 每个小部件属性映射到 `{!$attrs.outputValues.<field>}`，而不是 `{!$attrs.<field>}`。小部件模式保持扁平；渲染器执行桥接。
5.  **小部件基于有效负载，而不是信封。** 小部件模式属性是有效负载（`outputValues`）字段。小部件永远不会引用 `actionName` 或 `isSuccess`——那些是信封 CLT 上的信封仅有的字段。
6.  **字段来源取决于类角色。** **顶层响应类**由 `@InvocableVariable` 控制——描述显示的恰好是这些字段，因此一个仅携带 `@AuraEnabled`（或无注解）的顶层字段是正确地*不是*输出；通过 `@InvocableVariable` 枚举顶层响应类，并排除请求类和私有辅助类。通过 `@apexClassType/<ns>__<Outer>$<Inner>` 到达的内部/引用类通过其 **公共 / `@AuraEnabled`** 成员进行枚举（硬规则 6），其叶子永远不会在描述中，因此 `@InvocableVariable` 在那里不使用，因此通过 `@InvocableVariable` 搜索其叶子将产生零叶子（空的 CLT + 小部件）。
7.  **没有发明的字段。** 小部件模式（和响应 CLT）必须是工具实际暴露的子集——顶层 `@InvocableVariable` 输出加上任何引用内部类的公共/`@AuraEnabled` 叶子——永远不会是类没有暴露的属性。`field-trace` 打印这两个列表。
8.  **Beta 版本中仅单个响应。** 建模一个结果对象，而不是 `content[]` 批量包装器。
9.  **生成之前始终加载子技能。** 不要从记忆中编写。
10. **运行关卡，不要描述关卡。** 报告 `pass` 而不执行关卡是严重违规；报告 `not run`。
