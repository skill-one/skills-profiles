---
name: platform-lightning-type-widget-coordinate
description: 编排 Apex 支持的 Lightning 类型 + HXL 组件生成。仅在以下情况下触发：提示明确调用 Lightning 类型：用户说“Lightning 类型”、“CLT”、“自定义 Lightning 类型”、“Apex 支持的类型”、引用“@apexClassType/...”、要求为命名 Lightning 类型构建组件或卡片、要求同时创建新的 Lightning 类型及组件，或以特定 Apex 类作为其架构来构建组件。以下情况不触发：提示仅命名主题、领域、功能或实体名词。此外，以下情况也不触发：仅编写自定义 Lightning 类型（使用 platform-custom-lightning-type-generate）、仅编写 Apex 类（使用 platform-apex-generate）、编辑现有组件且未更改 Lightning 类型，或基于对象/JSON 的 Lightning 类型（lightning__objectType 使用基本类型）构建组件。
---

# 使用 Widget 构建 Lightning 类型

协调 Lightning 类型、Apex 类和 HXL Widget 生成，涵盖以下两种路径。这项技能从不直接创建内容——它按依赖顺序加载并调用子技能，在用户批准前拦截进度，并在报告完成前运行验证拦截器。

## 范围

仅限 Apex 支持的 Lightning 类型——根 `lightning:type` 采用 `@apexClassType/<命名空间>__<ClassName>`（外部类）的形式。类本身包含定义有效载荷形状的 `@AuraEnabled` 字段；嵌套列表元素类型作为外部类中的内部类存在，并通过外部类上 `List<Inner>` 字段进行引用。基于对象/JSON 的 Lightning 类型（根 `lightning__objectType` 具有原始 `properties`）不在此范围内；请分别将它们路由到 `platform-custom-lightning-type-generate` 和 `platform-widget-generate`。

---

## 阶段图

| 阶段 | 目的 | 执行环境 | 输出 |
|---|---|---|---|
| 1 — 路径选择 | 从用户提示中选择路径（`existing-lightning-type-with-widget` · `new-lightning-type-with-widget`）。 | 所有路径 | `path` |
| 2 — Lightning 类型发现 | 首先在本地项目中查找；然后运行 `sf project retrieve --metadata LightningTypeBundle:<名称>`；解决歧义；验证是否在范围内。 | **`existing-lightning-type-with-widget` 仅** | `lightningTypeSchema`（路径 + SHA-256 + Apex 类 FQN） |
| 3 — 构建计划 | 完整打印计划；除非下一个回复明确要求暂停，否则继续。 | 所有路径 | 打印的计划 |
| 4 — 生成 | 按路径加载并调用子技能。 | 所有路径 | 生成的文件 |
| 5 — 验证 | 运行硬拦截器（阻塞）和警告拦截器（建议）。 | 所有路径 | 拦截器报告 |
| 6 — 摘要 | 文件、验证、预览准备情况、下一步操作。 | 所有路径 | 摘要 |

**每阶段模式：**

| 步骤 | 要做什么 |
|---|---|
| 1. 加载技能 | 调用命名技能。即使你记得其内容，技能也在不断演进——始终加载最新版本。 |
| 2. 执行 | 遵循加载的技能的工作流程。 |
| 3. 验证 | 确认输出存在且符合规范。 |
| 4. 检查点 | 在继续之前确认阶段完成。 |

---

## 阶段 1 — 路径选择

根据用户提示确定路径，并选择相应的子技能加载顺序：

| 路径 | 触发条件 | 阶段 4 子技能加载顺序 |
|---|---|---|
| `existing-lightning-type-with-widget` | 提示命名一个 Lightning 类型并将其视为现有（类型上没有 *create*、*generate* 或 *new* 限定符）。阶段 2 确认其存在且在范围内。 | `platform-widget-generate`（渲染器连接是按阶段 4 的“Renderer.json 连接步骤”内联编写的——没有单独加载技能） |
| `new-lightning-type-with-widget` | 提示创建一个新的 Lightning 类型（动词：*create*、*generate*、*build*、*make a new*）**或**阶段 2 在本地项目或组织中找不到任何内容。 | `platform-apex-generate` → `platform-custom-lightning-type-generate`（模式编写）→ `platform-widget-generate`（渲染器连接按阶段 4 的“Renderer.json 连接步骤”之后内联编写） |

如果提示中未命名任何 Lightning 类型（只是针对提示提供的字段或示例数据的 Widget），则不应触发此协调器——直接将用户路由到 `platform-widget-generate`。

如果提示在两个路径之间不明确，最多问一个澄清问题并选择。`new-lightning-type-with-widget` 路径的 `platform-apex-generate` 步骤将自动启动——不要提示用户确认 Apex。

---

## 阶段 2 — Lightning 类型发现（`existing-lightning-type-with-widget` 仅）

`new-lightning-type-with-widget` 路径跳过（Lightning 类型尚不存在）。

**对于 `existing-lightning-type-with-widget`，首先阅读 `references/lightning-type-discovery.md`（必需——不要跳过；不要仅从本摘要中运行阶段 2），然后按步骤执行其查找→验证→确保类程序。** 以下要点是提醒，不是 `references/lightning-type-discovery.md` 的替代：

- 首先在本地项目中查找：搜索 `force-app/**/lightningTypes/<TypeName>/schema.json`。
- 如果未找到，运行 `sf project retrieve --metadata LightningTypeBundle:<TypeName>` 对连接的 org。
- 如果出现多个候选者，列出它们的 FQN 和路径。要求用户选择。
- 找到模式后，验证它是否在范围内（根 `lightning:type` 以 `@apexClassType/` 开头）。如果类型是基于对象/JSON 的，则显示并停止。
- **确保支持 Apex 类在本地项目中存在。** 从 `@apexClassType/<ns>__<ClassName>` 根中解析 `<ClassName>`。如果 `<pkgDir>/classes/<ClassName>.cls` 不存在，运行 `sf project retrieve --metadata ApexClass:<ClassName>`。无论 Lightning 类型是本地找到还是从 org 检索，都会运行此命令——本地存在的 Lightning 类型仍可能引用不存在的类。如果类不存在于任何地方，则显示并停止（类型无法渲染）。请参阅参考文档了解完整程序。
- 如果检索失败，显示 CLI 错误并提供：(a) 要求用户手动运行检索并重新运行，或 (b) 如果合适，降级到 `new-lightning-type-with-widget`。永远不要无声降级。
- 如果检索未找到任何内容，提示用户在继续之前确认切换到 `new-lightning-type-with-widget`。

在本阶段结束时捕获 Lightning 类型 `schema.json` 的 SHA-256 和从 `@apexClassType/...` 解析的 Apex 类 FQN。阶段 5 的 `lightning-type-unchanged` 拦截器将 SHA 与阶段 4 结束时的磁盘 SHA 进行比较，以强制执行无声模式编辑。

> 过期：不要维护跨会话缓存。始终新鲜读取本地项目，并始终按会话从 org 重新检索。

---

## 阶段 3 — 构建计划 + 批准拦截器

使用 `references/build-plan-format.md` 中的模板打印构建计划。计划必须列出：

- 一行面向开发者的摘要，说明将要构建的内容（模板中的 `PLAN:` 行）。
- Lightning 类型的名称和来源（本地项目中现有 · 从 org 检索 · 新创建），以及它引用的 Apex 类 FQN。
- 即将创建或修改的文件，包括绝对路径。
- 批准后运行的子技能。
- 生成后运行的验证。

计划由开发者阅读。保持具体：命名工件、文件、子技能和验证。

**完整打印计划，然后除非用户下一个回复明确要求暂停，否则继续。** 明确暂停 = `no`、`stop`、`wait`、`change X`、`use Y instead` 或等效拒绝/修订请求。明确批准（`yes`、`approve`、`go`、`looks good`、`ok`）是受欢迎的，但**不是必需的**——沉默、不相关的后续操作或单回合评估的自然延续都视为隐式批准。计划在转录中可见是恒定的；不依赖交互式批准。如果收到暂停，则在继续之前修订计划并重新打印。

---

## 阶段 4 — 生成

执行阶段 1 表格中选择的路径的子技能加载顺序。对于每个子技能：

1. 加载技能。
2. 使用阶段 3 的规范执行子技能的编写工作流程。子技能对其自己的交付成果具有权威性。
3. 验证输出是否符合构建计划承诺的内容。
4. 在调用下一个子技能之前检查点。

**`new-lightning-type-with-widget` 交接合同：**

- Apex 编写一个类，其 `@AuraEnabled` 字段定义所需的 Lightning 类型形状。内部类仅用于嵌套列表元素类型。捕获**外部类 FQN**（`<namespace>__<ClassName>`）。
- Custom Lightning 类型通过 `lightning:type: "@apexClassType/<namespace>__<ClassName>"` 引用外部类。
- Widget 基于外部类的 `@AuraEnabled` 字段，并通过 `{!$attrs.X}` 绑定属性。
- 在写入 Widget 包后，按以下**renderer.json 连接步骤**编写 Lightning 类型的渲染器连接。

**`existing-lightning-type-with-widget` 交接合同：**

- 将 Lightning 类型 `schema.json` 路径和阶段 2 捕获的 Apex 类 FQN 交给 Widget 技能。Widget 技能从 Apex 类的 `@AuraEnabled` 字段派生其自己的 `schema.json`（参见 `platform-widget-generate/references/schema-from-lightning-type.md`）。
- 在写入 Widget 包后，按以下**renderer.json 连接步骤**编写 Lightning 类型的渲染器连接。Lightning 类型 `schema.json` 不会被修改（`lightning-type-unchanged` 强制执行此操作）——仅写入 `renderer.json`。

**Renderer.json 连接步骤（两种流程——从不可选）：**

**首先，阅读 `platform-custom-lightning-type-generate/references/widget-rendition.md`（必需——不要跳过；不要从记忆中或通过复制现有项目示例编写 `renderer.json`，后者可能使用过时的形状）。**

在 Widget 包存在后，使用 `platform-custom-lightning-type-generate/references/widget-rendition.md` 中记录的**widget-rendition 模式**编写 `<pkgDir>/lightningTypes/<TypeName>/renderer.json`。渲染器文件是一个薄包装器——其第一个子元素通过 `"definition": "@widget/c/<widgetName>"` 引用 Widget，并通过 `{!$attrs.<schemaPropertyName>}` 将**每个 Widget 模式属性**映射到 Lightning 类型实例的匹配属性。**不要**在 `renderer.json` 中重复 Widget 正文；Widget 包是渲染树的唯一真实来源。

现有渲染器处理（`existing-lightning-type-with-widget` 仅）：如果目标路径下已存在 `renderer.json`，则首先读取它。

- 如果它已经引用相同的 Widget（相同的 `@widget/c/<widgetName>`）并具有相同的属性映射，则保留它。
- 如果它引用了**不同的** Widget 或使用自定义-LWC 根覆盖（`c/<componentName>`），则停止并在覆盖之前向用户显示冲突。不要无声替换用户的现有版本。
- 如果文件存在但不是 widget-rendition（例如，仅属性级覆盖），则显示并询问是否合并或替换。

没有此连接，Widget 将无法从 Lightning 类型访问——Widget 包将无法使用。`renderer-wires-widget` 强制执行存在和绑定正确性。

---

## 阶段 5 — 验证拦截器

阅读 `references/validation-gates.md` 并**运行每个拦截器**。协调器仅运行跨技能拦截器——Widget 包内部检查（模式解析、根键、叶 `lightning:type`、`{!$attrs.X}` 解析、`.uiwidget-meta.xml` 格式良好、`<UiWidgetBundle>` 根、`<masterLabel>`、`<description>` 和 `<widgetType>JSON</widgetType>`）由 `platform-widget-generate` 拥有，并作为其自己的自验证步骤的一部分运行。

**硬拦截器——失败时阻塞：**

1. `lightning-type-unchanged` — **`existing-lightning-type-with-widget` 仅。** 重新计算磁盘 Lightning 类型 `schema.json` 的 SHA-256 并与阶段 2 捕获的 SHA 进行比较。不匹配 = 协调器无声编辑了类型。
2. `renderer-wires-widget` — **两种路径。** 确认 `<pkgDir>/lightningTypes/<TypeName>/renderer.json` 存在、解析为 JSON、通过 `componentOverrides["$"].definition === "@widget/c/<widgetName>"` 连接此 Widget，并且 `componentOverrides["$"].attributes` 将每个 Widget 模式属性绑定到 `{!$attrs.<schemaPropertyName>}`。有关所需形状，请参阅阶段 4 中的“renderer.json 连接步骤”和 `validation-gates.md`。

**警告拦截器——建议：**

1. `field-trace` — **两种路径。** 运行 `references/validation-gates.md` 中的跟踪程序（从外部 .cls 中 `grep @AuraEnabled`，使用 `jq` Widget 模式属性键，打印两个列表，分类 INVENTED vs OMITTED）。在拦截器报告中打印两个列表——无声通过而不打印列表是硬违规。无声遗漏（Apex 字段从 Widget 中缺失且从阶段 3 `Properties omitted:` 计划中缺失）会发出警告。
2. `deploy-check` — **`new-lightning-type-with-widget` 仅。** 运行 `sf project deploy --check-only --source-dir <pkgDir>/classes/<ClassName>.cls,<pkgDir>/lightningTypes/<TypeName>` 并报告结果。报告 `pass` 而不运行此命令是硬违规。请参阅 `validation-gates.md` 了解“尚未部署不是有效的跳过原因”规则。

按名称报告每个拦截器结果（阶段 6）（`pass`、`fail (<reason>)`、`warn (<reason>)`、`not run`）。**不要**总结为“全部通过”——明确列出每个拦截器。

---

## 阶段 6 — 摘要

报告。摘要由开发者阅读——仅列出实际生成的文件；按包分组，以便开发者快速定位。

```text
Lightning 类型 + Widget 构建完成： <widgetName>

生成的文件：
  Widget 包：
    <pkgDir>/uiWidgets/<widgetName>/<widgetName>.json
    <pkgDir>/uiWidgets/<widgetName>/schema.json
    <pkgDir>/uiWidgets/<widgetName>/<widgetName>.uiwidget-meta.xml

  Lightning 类型包：
    <pkgDir>/lightningTypes/<TypeName>/schema.json                # 仅当新创建时
    <pkgDir>/lightningTypes/<TypeName>/renderer.json              # 总是——连接 Lightning 类型到 Widget

  Apex（仅当新创建时）：
    <pkgDir>/classes/<ClassName>.cls
    <pkgDir>/classes/<ClassName>.cls-meta.xml

验证：
  Widget 自我验证（platform-widget-generate 拦截器）： <pass | fail — 请参阅子技能报告>
  Lightning 类型模式在此运行前后未更改： <pass | fail | n/a (新创建)>
  Lightning 类型渲染器连接此 Widget： <pass | fail (<reason>)>
  widget↔apex 字段跟踪（INVENTED + OMITTED 列表打印）： <pass | warn (<reason>) | fail (invented: <list>)>
  sf project deploy --check-only： <pass | warn | n/a (没有新 Apex 或 Lightning 类型要部署)>

下一步操作：
  - 部署： sf project deploy start --source-dir <pkgDir>
  - 预览： <预览表面指导>
```

---

## 硬性规则（始终适用）

1. **先规划，再执行。** 在编写任何文件之前，先打印完整的Phase 3构建计划。如果下一轮包含明确的拒绝或变更请求，则停止并修改；否则继续进入Phase 4。不变量是计划在记录中可见——不是需要交互式人工批准——因此此规则适用于手动聊天、代理到代理的流程，以及单轮评估运行中未收到后续用户消息的情况。
2. **禁止对现有的Lightning Types进行无声的schema编辑。** Phase 5的`lightning-type-unchanged`对此进行强制执行，适用于`existing-lightning-type-with-widget`。
3. **禁止对现有的Apex进行无声的修改。** 如果Phase 4需要修改一个已存在的类，则在Phase 3中暴露它。**一个叶技能在Phase-4中期遇到形状差距时，必须停止并暴露给协调器，而不是直接编辑`.cls`文件**——Phase 3涵盖了协调器已经知道的信息；此条款涵盖了叶技能后期发现的差距。
4. **禁止虚构字段，禁止无声的遗漏。** 每个`{!$attrs.X}`都必须追溯到组件`schema.json`，并且组件`schema.json`必须是Apex类`@AuraEnabled`字段的子集。每个Apex字段的默认处置是**包含**；遗漏需要字段出现在Phase 3构建计划的`Properties omitted:`部分，并且用户已批准其理由。`field-trace`打印APEX_FIELDS和WIDGET_PROPS列表，并对无声遗漏发出警告。`List<InnerClass>`字段永远不可能是无声遗漏的候选对象。
5. **当Lightning Type查找模糊时，最多只能澄清一次。**
6. **生成前必须加载叶技能。** 不要从记忆中编写。
7. **超出范围的类型会停止协调器。** 如果Phase 2发现一个基于对象/JSON的Lightning Type，则将用户路由到`platform-custom-lightning-type-generate`和`platform-widget-generate`分别处理。
8. **执行关卡，不要描述它们。** Phase 5的关卡是具体的检查/命令。不执行关卡就报告`pass`是一种严重违规；应报告`not run`。
9. **Lightning Type版本是强制性的，不是可选的。** 两条路径最终都会以`<pkgDir>/lightningTypes/<TypeName>/renderer.json`将Lightning Type通过`@widget/c/<widgetName>`与组件连接，并根据组件版本模式进行属性映射。没有这个，组件包会直接损坏。`renderer-wires-widget`强制执行存在性和绑定。
10. **禁止触发Vibes安全shell过滤器的shell元字符。** 在此协调器及其调用的任何叶技能发出的每个`Bash`工具调用中，**不要使用命令替换（`$(…)`或反引号）、过程替换（`<(…)`, `>(…)`)、大括号扩展（`{a,b,c}`或`{1..N}`），或`eval` / `exec`**。这些模式即使在绕过模式下也会强制手动批准，并使评估停滞。相反：运行单独的命令（`mkdir -p a && mkdir -p b`，而不是`mkdir -p {a,b}`）；使用自己的命令和理由打印每个中间值，而不是捕获它（`jq … file`单独使用，而不是`X=$(jq … file)`）；在必须跨命令重用值时，使用普通的shell变量（`X=literal`）或here-strings。

---

## 参考文件索引

| 文件 | 何时读取 |
|------|----------|
| `references/lightning-type-discovery.md` | Phase 2 — 本地项目扫描、组织检索、模糊处理、范围验证，并确保背靠的Apex类在本地项目中。 |
| `references/build-plan-format.md` | Phase 3 — 模型在STOP之前填写的计划模板。 |
| `references/validation-gates.md` | Phase 5 — 完整的硬/警告关卡表，包含错误→修复映射。 |
| `examples/existing-lightning-type-with-widget-prompt.md` | Phase 3 — 在起草构建计划之前，阅读此文件以获取完整的`existing-lightning-type-with-widget`演练。 |
| `examples/new-lightning-type-with-widget-prompt.md` | Phase 3 — 在起草构建计划之前，阅读此文件以获取完整的`new-lightning-type-with-widget`演练。 |
