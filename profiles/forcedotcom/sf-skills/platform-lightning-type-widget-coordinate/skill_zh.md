# 使用 Widget 构建 Lightning 类型

协调 Lightning 类型、Apex 类和 HXL Widget 生成，涵盖以下两种路径。这项技能从不直接创建内容——它按依赖顺序加载并调用子技能，在用户批准前拦截进度，并在报告完成前运行验证门。

## 范围

仅限 Apex 支持的 Lightning 类型——根 `lightning:type` 采用 `@apexClassType/<命名空间>__<ClassName>`（外部类）的形式。类本身包含定义有效载荷形状的 `@AuraEnabled` 字段；嵌套列表元素类型作为外部类中的内部类存在，并通过外部类上的 `List<Inner>` 字段进行引用。基于对象/JSON 的 Lightning 类型（根 `lightning__objectType` 具有原始 `properties`）不在此范围内；请将它们路由到 `platform-custom-lightning-type-generate` 和 `platform-widget-generate`。

---

## 阶段图

| 阶段 | 目的 | 执行环境 | 输出 |
|---|---|---|---|
| 1 — 路径选择 | 从用户提示中选择路径 (`existing-lightning-type-with-widget` · `new-lightning-type-with-widget`)。 | 所有路径 | `path` |
| 2 — Lightning 类型发现 | 首先在本地项目中查找；然后运行 `sf project retrieve --metadata LightningTypeBundle:<名称>`；歧义解决；在范围内验证。 | **仅 `existing-lightning-type-with-widget`** | `lightningTypeSchema` (路径 + SHA-256 + Apex 类 FQN) |
| 3 — 构建计划 | 完整打印计划；除非下一轮回复明确表示反对，否则继续。 | 所有路径 | 打印的计划 |
| 4 — 生成 | 按路径加载并调用子技能。 | 所有路径 | 生成的文件 |
| 5 — 验证 | 运行硬门（拦截）和警告门（建议）。 | 所有路径 | 门报告 |
| 6 — 摘要 | 文件、验证、预览准备情况、下一步操作。 | 所有路径 | 摘要 |

**按阶段模式：**

| 步骤 | 要做什么 |
|---|---|
| 1. 加载技能 | 调用命名技能。即使你记得其内容，技能也在不断演进——始终加载最新版本。 |
| 2. 执行 | 遵循加载的技能的工作流程。 |
| 3. 验证 | 确认输出存在且符合规范。 |
| 4. 检查点 | 在继续之前确认阶段完成。 |

---

## 阶段 1 — 路径选择

根据用户提示确定路径，并选择相应的子技能加载顺序：

| 路径 | 触发器 | 阶段 4 子技能加载顺序 |
|---|---|---|
| `existing-lightning-type-with-widget` | 提示命名一个 Lightning 类型并将其视为现有（类型上没有 *创建*、*生成* 或 *新建* 限定符）。阶段 2 确认其存在且在范围内。 | `platform-widget-generate` (渲染器连接是按阶段 4 "Renderer.json 连接步骤"内联编写——不加载单独的技能) |
| `new-lightning-type-with-widget` | 提示要求一个新 Lightning 类型（动词：*创建*、*生成*、*构建*、*创建一个新*）**或** 阶段 2 在本地项目或组织中找不到任何内容。 | `platform-apex-generate` → `platform-custom-lightning-type-generate` (模式作者) → `platform-widget-generate` (渲染器连接在阶段 4 "Renderer.json 连接步骤"之后内联编写) |

如果提示未命名任何 Lightning 类型（只是针对提示提供的字段或示例数据的 Widget），则不应触发此协调器——直接将用户路由到 `platform-widget-generate`。

如果提示在两个路径之间不明确，最多问一个澄清问题，然后选择。`new-lightning-type-with-widget` 路径的 `platform-apex-generate` 步骤将自动启动——不要提示用户确认 Apex。

---

## 阶段 2 — Lightning 类型发现（仅 `existing-lightning-type-with-widget`）

对于 `new-lightning-type-with-widget` 跳过（Lightning 类型尚不存在）。

**对于 `existing-lightning-type-with-widget`，首先阅读 `references/lightning-type-discovery.md`（必需——不要跳过；不要仅从摘要中运行阶段 2），然后按步骤执行其查找→验证→确保类程序步骤。** 以下要点是提醒，不是 `references/lightning-type-discovery.md` 的替代：

- 首先在本地项目中搜索：`force-app/**/lightningTypes/<TypeName>/schema.json`。
- 如果未找到，运行 `sf project retrieve --metadata LightningTypeBundle:<TypeName>` 对连接的 org。
- 如果出现多个候选者，列出它们的 FQN 和路径。要求用户选择。
- 定位模式后，验证它是否在范围内（根 `lightning:type` 以 `@apexClassType/` 开头）。如果类型是基于对象/JSON 的，则显示并停止。
- **确保支持 Apex 类在本地项目中。** 从 `@apexClassType/<ns>__<ClassName>` 根中解析 `<ClassName>`。如果 `<pkgDir>/classes/<ClassName>.cls` 不存在，运行 `sf project retrieve --metadata ApexClass:<ClassName>`。无论 Lightning 类型是本地找到还是从 org 检索，都会运行此命令——本地存在的 Lightning 类型仍可以引用不存在的类。如果类不存在于任何地方，则显示并停止（类型无法渲染）。参考文件了解完整程序。
- 如果检索失败，显示 CLI 错误并提供建议：(a) 要求用户手动运行检索并重新运行，或 (b) 如果合适，降级到 `new-lightning-type-with-widget`。永远不要无声降级。
- 如果检索未找到任何内容，提示用户在继续之前确认切换到 `new-lightning-type-with-widget`。

在阶段结束时捕获 Lightning 类型 `schema.json` 的 SHA-256 和 Apex 类 FQN（从 `@apexClassType/...` 解析）。阶段 5 的 `lightning-type-unchanged` 门将 SHA 与阶段 4 结束时的磁盘 SHA 进行比较，以强制执行无声模式编辑。

> 过期：不要维护跨会话缓存。始终新鲜读取本地项目，并始终按会话从 org 重新检索。

---

## 阶段 3 — 构建计划 + 批准门

使用 `references/build-plan-format.md` 中的模板打印构建计划。计划必须列出：

- 开发者面向的一行摘要，说明将构建的内容（模板中的 `PLAN:` 行）。
- Lightning 类型名称和来源（本地项目中存在 · 从 org 检索 · 新创建），以及它引用的 Apex 类 FQN。
- 即将创建或修改的文件，带绝对路径。
- 批准后运行的子技能。
- 生成后运行的验证。

计划由开发者阅读。保持具体：命名工件、文件、子技能和验证。

**完整打印计划，然后除非用户下一轮回复明确反对，否则继续。** 明确反对 = `no`、`stop`、`wait`、`change X`、`use Y instead` 或等效拒绝/修订请求。明确批准 (`yes`、`approve`、`go`、`looks good`、`ok`) 是受欢迎的，但**不是必需的**——沉默、不相关的后续消息或单轮评估的自然延续都视为隐式批准。计划在转录中可见是不变量；不依赖交互式批准。如果收到反对，则在继续之前修订计划并重新打印。

---

## 阶段 4 — 生成

执行阶段 1 表中选择的路径的子技能加载顺序。对于每个子技能：

1. 加载技能。
2. 执行子技能的作者工作流程，针对阶段 3 的规范。子技能对其自己的交付成果具有权威性。
3. 验证输出是否符合构建计划承诺的内容。
4. 在调用下一个子技能之前检查点。

**`new-lightning-type-with-widget` 交接合同：**

- Apex 编写一个类，其 `@AuraEnabled` 字段定义所需的 Lightning 类型形状。内部类仅用于嵌套列表元素类型。捕获**外部类 FQN** (`<namespace>__<ClassName>`).
- Custom Lightning 类型通过 `lightning:type: "@apexClassType/<namespace>__<ClassName>"` 引用外部类。
- Widget 基于 外部类的 `@AuraEnabled` 字段，并通过 `{!$attrs.X}` 绑定属性。
- Widget 包写入后，根据下面的 **renderer.json 连接步骤**编写 Lightning 类型的渲染器连接。

**`existing-lightning-type-with-widget` 交接合同：**

- 将 Lightning 类型 `schema.json` 路径和阶段 2 捕获的 Apex 类 FQN 交给 Widget 技能。Widget 技能从 Apex 类的 `@AuraEnabled` 字段派生其自己的 `schema.json`（见 `platform-widget-generate/references/schema-from-lightning-type.md`）。
- Widget 包写入后，根据下面的 **renderer.json 连接步骤**编写 Lightning 类型的渲染器连接。Lightning 类型 `schema.json` 不会被修改（`lightning-type-unchanged` 强制执行此操作）——仅写入 `renderer.json`。

**Renderer.json 连接步骤（两个流程——从不可选）：**

**首先，阅读 `platform-custom-lightning-type-generate/references/widget-rendition.md`（必需——不要跳过；不要从记忆中或通过复制现有项目示例编写 `renderer.json`，后者可能使用过时的形状）。**

Widget 包存在后，使用 `platform-custom-lightning-type-generate/references/widget-rendition.md` 中记录的 **widget-rendition 模式**编写 `<pkgDir>/lightningTypes/<TypeName>/renderer.json`。渲染器文件是一个薄包装——其第一个子元素通过 `"definition": "@widget/c/<widgetName>"` 引用 Widget，并将**每个 Widget 模式属性**映射到 Lightning 类型实例的匹配属性 via `{!$attrs.<schemaPropertyName>}`。**不要**在 `renderer.json` 中重复 Widget 身体；Widget 包是渲染树的单源真理。

现有渲染器处理（仅 `existing-lightning-type-with-widget`）：如果目标路径存在 `renderer.json`，则首先读取它。

- 如果它已经引用相同的 Widget（相同的 `@widget/c/<widgetName>`）并具有相同的属性映射，则保留它。
- 如果它引用**不同**的 Widget 或使用自定义 LWC 根覆盖 (`c/<componentName>`), 在覆盖之前停止并显示冲突给用户。不要无声替换用户的现有版本。
- 如果文件存在但不是 Widget-rendition（例如仅属性级覆盖），则显示并询问是否合并或替换。

没有此连接，Widget 将无法从 Lightning 类型访问——Widget 包将无法使用。`renderer-wires-widget` 强制执行存在和绑定正确性。

---

## 阶段 5 — 验证门

阅读 `references/validation-gates.md` 并**运行每个门**。协调器仅运行跨技能门——Widget 包内部检查（模式解析、根键、叶 `lightning:type`、`{!$attrs.X}` 解析、`.uiwidget-meta.xml` 格式正确性、`<UiWidgetBundle>` 根、`<masterLabel>`、`<description>` 和 `<widgetType>JSON</widgetType>`）由 `platform-widget-generate` 拥有，并作为其自己的自验证步骤的一部分运行。

**硬——失败时拦截：**

1. `lightning-type-unchanged` — **仅 `existing-lightning-type-with-widget`**。重新计算磁盘 Lightning 类型 `schema.json` 的 SHA-256 并与阶段 2 捕获的 SHA 进行比较。不匹配 = 协调器无声编辑了类型。
2. `renderer-wires-widget` — **两个路径**。确认 `<pkgDir>/lightningTypes/<TypeName>/renderer.json` 存在、解析为 JSON、通过 `componentOverrides["$"].definition === "@widget/c/<widgetName>"` 连接此 Widget，并且 `componentOverrides["$"].attributes` 将每个 Widget 模式属性绑定到 `{!$attrs.<schemaPropertyName>}`。见“renderer.json 连接步骤”在阶段 4 和 `validation-gates.md` 中所需的形状。

**警告——建议：**

1. `field-trace` — **两个路径**。运行 `references/validation-gates.md` 中的跟踪程序（从外部 .cls 中 grep `@AuraEnabled`，使用 `jq` Widget 模式属性键，打印两个列表，分类 INVENTED vs OMITTED）。在门报告中打印两个列表——没有打印列表而断言 `pass` 是硬违规。无声遗漏（Apex 字段从 Widget 中缺失且从阶段 3 `Properties omitted:` 计划中缺失）会警告。
2. `deploy-check` — **仅 `new-lightning-type-with-widget`**。运行 `sf project deploy --check-only --source-dir <pkgDir>/classes/<ClassName>.cls,<pkgDir>/lightningTypes/<TypeName>` 并报告结果。不运行此命令而报告 `pass` 是硬违规。见 `validation-gates.md` 中“尚未部署不是有效的跳过原因”规则。

按名称在阶段 6 报告每个门结果 (`pass`、`fail (<reason>)`、`warn (<reason>)`、`not run`)。**不要**总结为“全部通过”——明确列出每个门。

---

## 阶段 6 — 摘要

报告。摘要由开发者阅读——仅列出实际写入的文件；按包分组，以便开发者快速定位。

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
  Widget 自验证（platform-widget-generate 门）： <pass | fail — 见子技能报告>
  Lightning 类型模式在此运行前后未更改： <pass | fail | n/a (新创建)>
  Lightning 类型渲染器连接此 Widget： <pass | fail (<reason>)>
  widget↔apex 字段跟踪（INVENTED + OMITTED 列表打印）： <pass | warn (<reason>) | fail (invented: <list>)>
  sf project deploy --check-only： <pass | warn | n/a (没有新 Apex 或 Lightning 类型要部署)>

下一步操作：
  - 部署： sf project deploy start --source-dir <pkgDir>
  - 预览： <预览表面指导>
```

---

## 硬规则（始终适用）

1. **先计划，再执行。** 在写入任何文件之前完整打印阶段 3 的构建计划。如果下一轮包含明确拒绝或变更请求，停止并修订；否则继续到阶段 4。不变量是计划在转录中可见——不是交互式人工批准——因此此规则适用于手动聊天、代理到代理流程和单轮评估运行（没有后续用户消息到达）。
2. **不要对现有 Lightning 类型进行无声模式编辑。** 阶段 5 `lightning-type-unchanged` 强制执行此操作，用于 `existing-lightning-type-with-widget`。
3. **不要对现有 Apex 进行无声更改。** 如果阶段 4 需要修改预先存在的类，则在阶段 3 中显示它。**在阶段 4 中遇到形状差距的子技能必须停止并显示给协调器，而不是直接编辑 `.cls`**——阶段 3 涵盖协调器已知的差距；此条款涵盖子技能后来发现的差距。
4. **不要有虚构字段，不要有无声遗漏。** 每个 `{!$attrs.X}` 必须追溯到 Widget `schema.json`，并且 Widget `schema.json` 必须是 Apex 类的 `@AuraEnabled` 字段的子集。每个 Apex 字段的默认处置是**包含**；遗漏需要字段出现在阶段 3 构建计划的 `Properties omitted:` 部分中，并且用户已批准理由。`field-trace` 打印 APEX_FIELDS 和 WIDGET_PROPS 列表，并在无声遗漏上警告。`List<InnerClass>` 字段**永远不会**是无声遗漏的候选者。
5. **Lightning 类型查找最多澄清一次。**
6. **生成前始终加载子技能。** 不要从记忆中编写。
7. **超出范围的类型停止协调器。** 如果阶段 2 发现基于对象/JSON 的 Lightning 类型，请将用户路由到 `platform-custom-lightning-type-generate` 和 `platform-widget-generate` 分别。
8. **运行门，不要描述它们。** 阶段 5 门是具体的检查/命令。不执行门而报告 `pass` 是硬违规；报告 `not run`。
9. **Lightning 类型版本是强制性的，从不可选。** 两个路径都以 `<pkgDir>/lightningTypes/<TypeName>/renderer.json` 连接 Lightning 类型到 Widget via `@widget/c/<widgetName>` 并按 Widget-rendition 模式映射属性。没有这个，Widget 包将无法使用。`renderer-wires-widget` 强制执行存在和绑定。
10. **不要触发 Vibes safe-shell 过滤器的 shell 修饰符。** 在此协调器和它调用的任何子技能发出的每个 `Bash` 工具调用中，**不要**使用命令替换 (`$(…)` 或反引号)、过程替换 (`<(…)`, `>(…)`)、大括号扩展 (`{a,b,c}` 或 `{1..N}`) 或 `eval` / `exec`。这些模式强制手动批准，即使在 Bypass 模式下也会停滞评估。相反：运行单独的命令 (`mkdir -p a && mkdir -p b`，而不是 `mkdir -p {a,b}`)；使用自己的命令打印每个中间值并讨论结果，而不是捕获它 (`jq … file` 单独使用，而不是 `X=$(jq … file)`)；在必须跨命令重用值时使用普通 shell 变量 (`X=literal`) 或 here-strings。
