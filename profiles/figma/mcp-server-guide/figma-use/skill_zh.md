# use_figma — Figma 插件 API 技能

使用 `use_figma` 工具通过插件 API 在 Figma 文件中执行 JavaScript。所有详细参考文档都位于 `references/` 中。

**在调用 `use_figma` 时，始终在逗号分隔的 `skillNames` 参数中包含 `figma-use`。如果此技能是通过 MCP 资源加载的，则必须将名称前缀为 `resource:`（例如 `resource:figma-use`）。** 这是一个用于跟踪技能使用的日志参数——它不会影响执行。

**如果 Figma MCP 工具显示为延迟工具，请在单个 `ToolSearch` 调用中批量加载所有它们的模式**，使用 `select:` 语法——例如 `ToolSearch query="select:use_figma,get_screenshot,get_metadata,create_new_file"`。一次往返比六次更有效。

**如果任务涉及从代码在 Figma 中构建或更新完整页面、屏幕或多部分布局**，请加载 [figma-generate-design](../figma-generate-design/SKILL.md)。它提供了通过 `search_design_system` 发现设计系统组件、导入它们以及逐步组装屏幕的工作流程。这两个技能协同工作：这个用于 API 规则，那个用于屏幕构建工作流程。

**如果任务涉及在 Figma 中创建或构建组件**（即使是单个组件），也请加载 [figma-generate-library](../figma-generate-library/SKILL.md)。它提供了组件创建工作流程——变量基础、变体集、设计令牌绑定——这些是 `figma-use` 单独无法涵盖的。

在开始之前，加载 [plugin-api-standalone.index.md](references/plugin-api-standalone.index.md) 以了解可能实现的内容。当要求您编写插件 API 代码时，使用此上下文来搜索 [plugin-api-standalone.d.ts](references/plugin-api-standalone.d.ts) 中的相关类型、方法和属性。这是 API 表面的权威来源。它是一个大型typings文件，因此不要一次性加载所有内容，按需搜索相关部分。

**重要提示**：每当您处理设计系统时，请从 [working-with-design-systems/wwds.md](references/working-with-design-systems/wwds.md) 开始了解关键概念、流程和 Figma 中使用设计系统的指南。然后按需加载更具体的参考文档，用于组件、变量、文本样式和效果样式。

## 1. 关键规则
1.  **使用 `return` 发送数据。** 返回值会自动序列化为 JSON（对象、数组、字符串、数字）。**不要调用 `figma.closePlugin()` 或将代码包装在异步 IIFE 中**——这会为您处理。
2.  **使用普通的 JavaScript，并使用顶级 `await` 和 `return`。** 代码会自动包装在异步上下文中。**不要将其包装在 `(async () => { ... })()` 中**。
3.  `figma.notify()` **会抛出 "未实现"**——**永远不要使用它**
3a. **返回节点 ID 并将工作流程状态保持在 Figma 文件之外。** 仅在 `COMPONENT` 或 `COMPONENT_SET` 上设置人类可读的组件目的和使用情况在 `node.description` 中——**永远不要在框架或实例上设置**。
3b. **在访问类型特定属性之前进行缩小。** 检查 `node.type`，使用能力守卫，例如 `"characters" in node`，或使用 `findAllWithCriteria` 进行预过滤。`characters` 需要一个文本功能的节点；可选链不会保护不受支持的属性访问。
4.  `console.log()` **不会返回**——使用 `return` 进行输出
5.  **为安全的重试和从证据中验证构建调用。** 不要仅仅为了创建验证检查而分割一个正在工作的操作。当结果脚本保持安全可重试时，请批量相关工作；一次调用可能构建一个完整的部分或页面。当跨越页面上下文、部分执行将难以恢复或实际失败需要有针对性的重试时，请分割。从每个写入中返回受影响的 ID 和相关的计数、名称或边界——这算作结构验证。仅在需要证据或验证后发生突变时运行单独的结构检查。通常在组合后和视觉修复后各拍一次快照。最新的通过快照是最终检查；当没有相关变化时，不要重复它。一旦通过要求，请停止。
6.  颜色是 **0–1 范围**（不是 0–255）：`{r: 1, g: 0, b: 0}` = 红色。`color` 对象的绘制使用 `{r, g, b}` **仅**——没有 `a` 字段；不透明度在绘制级别 (`{ type: 'SOLID', color: {...}, opacity: 0.5 }`)。
7.  填充/描边是 **只读数组**——克隆、修改、重新分配
8.  **每个文本编辑都遵循标准的配方：加载字体 → `await` → 变化 → 返回受影响的节点 ID。** 跳过加载会抛出 `Cannot write to node with unloaded font "<family> <style>"`。该规则涵盖的不仅仅是 `characters`——它适用于任何对未加载字体的节点进行的操作（`appendChild`、`insertChild`、`setBoundVariable`、`setExplicitVariableModeForCollection`、`setValueForMode`、`findAll` 回调触及文本）。当修改现有文本时，通过 `getStyledTextSegments(['fontName'])` 加载节点的*当前*字体，而不是硬编码的默认值。在大多数环境中，Inter 会预先加载，因此其他字体更常出现此错误——每个字体的配方都是相同的。如果样式字符串未经验证，请首先使用 `await figma.listAvailableFontsAsync()`——**永远不要猜测**（`"SemiBold"` 与 `"Semi Bold"` 是一个常见的陷阱）。对于 `FONT_FAMILY` 范围的变量，在 `setBoundVariable("fontFamily", …)`、`setValueForMode` 或 `setExplicitVariableModeForCollection` 之前，加载每个相关模式的所有值。`lineHeight`/`letterSpacing` 作为 `{unit, value}`，而不是裸数字。参见 [标准的文本编辑配方](references/gotchas.md#canonical-text-edit-recipe-font-load--await--mutate--return-ids)。
9.  **页面逐个加载**——使用 `await figma.setCurrentPageAsync(page)` 切换页面并加载它们的内容。同步设置器 `figma.currentPage = page` **不起作用**并抛出 `"Setting figma.currentPage is not supported"`。每次 `use_figma` 调用的开始时，页面上下文重置为**第一个页面**，因此每次调用都要重新切换；最多**每调用一次**切换一次，并并行展开多页工作——参见 [页面规则](#2-page-rules-critical) 和 [gotchas.md](references/gotchas.md#set-current-page-once-per-use_figma-call--split-multi-page-work-into-parallel-calls)。
10. `setBoundVariableForPaint` 返回一个**新的**绘制——必须捕获并重新分配
11. `createVariable` 接受集合**对象或 ID 字符串**（对象优先）
12. **`layoutSizingHorizontal/Vertical` 由结构上下文限制值**——`FIXED` 始终有效，`HUG` 和 `FILL` 无效。`'HUG'` 仅在自动布局框架本身上或在其**文本**子元素上有效。`'FILL'` 仅在对自动布局框架的子元素有效，该子元素不是绝对定位的、不在不可变框架内、也不是画布网格子元素的。实际后果：首先追加到自动布局父元素，然后设置 `HUG`/`FILL`——新创建的或未父化的节点还不能满足该规则。该属性本身存在于每个 `SceneNode`；错误是值拒绝，而不是“没有此属性”。参见 [陷阱](references/gotchas.md#layoutsizinghorizontallayoutsizingvertical-value-rules-fixed-hug-fill)。
12a. **使用自动布局来处理包含相关子元素的容器。** 当子元素具有结构关系——堆叠、并排、对齐、间隔、hugged——将它们包裹在 `figma.createAutoLayout()` 中，而不是使用绝对 `x`/`y` 的 `figma.createFrame()`。绝对坐标控制容器在画布上的位置；自动布局控制其子元素在其内部的关联方式。跳过容器会导致无法防止文本重排、内容变化或重叠。
12b. **`layoutSizing*` 和 `*AxisSizingMode` 是不同的枚举——不要交叉它们。** `layoutSizingHorizontal`/`layoutSizingVertical`（在**子元素**上设置）接受 `'FIXED'|'HUG'|'FILL'`；`primaryAxisSizingMode`/`counterAxisSizingMode`（在**框架**本身上设置）接受 `'FIXED'|'AUTO'`。因此 `layoutSizingVertical = 'AUTO'` 无效（使用 `'HUG'`），而 `counterAxisSizingMode = 'FILL'` 会抛出 `Expected 'FIXED' | 'AUTO', received 'FILL'`（使用 `'FIXED'`/`'AUTO'`）。来自同一设置器的两个错误——`Error: in set_layoutSizingHorizontal: node must be an auto-layout frame or a child of an auto-layout frame` 和 `Error: in set_layoutSizingHorizontal: FILL can only be set on children of auto-layout frames`——意味着节点尚未处于自动布局上下文中；**建议**：使父元素自动布局（`figma.createAutoLayout()`）并在设置之前将节点追加到父元素（参见规则 12）。
12c. **`resize()` 将尺寸模式重置为 `FIXED`，因此在使用 `layoutSizing*` 之前调用它。** 包装的**文本**块需要 `textAutoResize = 'HEIGHT'` 加上明确的 `FIXED` 宽度（`resize()`），而不是单独的 `FILL`——默认的 `WIDTH_AND_HEIGHT` 模式会忽略 `FILL` 并将节点压缩为接近零宽度的线程。之后验证 `node.width > 0`。
13. **将新的顶级节点远离 (0,0)。** 直接追加到页面上的节点默认为 (0,0)。扫描 `figma.currentPage.children` 以找到清晰的位置（例如，在右侧最右侧的节点右侧）。这仅适用于页面级节点——嵌套在其他框架或自动布局容器内的节点由其父节点定位。参见 [陷阱](references/gotchas.md)。
14. **在 `use_figma` 错误时，遵守 `safeToRetryWithoutCanvasRead`。** 如果 `true`，则修正已识别的错误并重试，而无需添加诊断画布读取；如果 `false`，则读取画布，确定发生了什么变化，然后进行更改。如果相同的 API 或属性错误发生两次，请检查其定义一次并修复根本原因，然后再重试；不要继续围绕相同的无效突变分解操作。错误修复已经是关键规则的诊断——`"not implemented"` (`figma.notify`, 规则 3)、`layoutSizing*` HUG/FILL 拒绝（规则 12, 12b）、`"Setting figma.currentPage is not supported"`（规则 9）、在变体上的 `componentPropertyDefinitions`（规则 18），以及错误节点类型上的 `characters`/`description`（规则 3a, 3b）。下面的表格涵盖了合同未命名的失败：

| 错误消息 | 可能的原因 | 如何修复 |
|---|---|---|
| 属性值超出范围 | 颜色通道 > 1（使用 0–255 而不是 0–1） | 除以 255 |
| `"Cannot read properties of null"` | 节点不存在（错误的 ID，错误的页面） | 检查页面上下文，验证 ID |
| 脚本挂起/无响应 | 无限循环或未解决的 Promise | 检查 `while(true)` 或缺少 `await`；确保代码终止 |
| `"The node with id X does not exist"` | 父实例被隐式分离，改变了 ID | 通过从稳定的（非实例）父框架遍历重新发现节点 |

### 当脚本成功但结果看起来错误时

调用 `get_metadata` 以检查结构正确性（层次结构、计数、位置）和 `get_screenshot` 以检查视觉正确性——仔细检查裁剪/剪切的文本（行高切断内容）和重叠元素，这些是常见且容易忽略的。确定差异是结构性的还是视觉性的，然后编写一个**有针对性的**修复脚本，仅修改损坏的部分——不要重新创建所有内容。

> 对于完整的验证工作流程，请参阅 [验证和错误恢复](references/validation-and-recovery.md)。

## 8. 起飞前检查清单
在提交任何 `use_figma` 调用之前，请对照 [第 1 节](#1-critical-rules) 中的操作合同重新阅读脚本。以前在此处枚举的每个门现在都存在于那里——任何违反这些规则的脚本都不准备提交：

- [ ] **输出** — 使用 `return`（不是 `figma.closePlugin()`），未包装在异步 IIFE 中，没有 `console.log()` 作为输出；`return`s 结构化数据，包含所有创建/修改的节点 ID（规则 1, 2, 4, 15）
- [ ] **颜色 & 填充** — 0–1 范围；`color` 对象使用 `{r, g, b}` **仅**——没有 `a`；填充/描边重新分配为新的数组（规则 6, 7）
- [ ] **类型缩小** — 在访问 `characters`、`description` 和 `componentPropertyDefinitions` 之前进行守卫/缩小（规则 3a, 3b, 18）
- [ ] **页面** — 切换使用 `await figma.setCurrentPageAsync(page)`，最多每调用一次（规则 9）
- [ ] **布局 & 尺寸** — 相关子元素在 `figma.createAutoLayout()` 中；顶级节点远离 (0,0)；`HUG`/`FILL` 设置在追加之后；`resize()` 在尺寸模式之前；包装的 TEXT 使用 `textAutoResize='HEIGHT'` + `FIXED` 宽度（规则 12, 12a, 12b, 12c, 13）
- [ ] **文本** — 标准的字体配方，样式名称通过 `listAvailableFontsAsync()` 验证；`lineHeight`/`letterSpacing` 作为 `{unit, value}`，而不是裸数字。对于 `FONT_FAMILY` 范围的变量，在 `setBoundVariable("fontFamily", …)`、`setValueForMode` 或 `setExplicitVariableModeForCollection` 之前，加载每个相关模式的所有值（规则 8）
- [ ] **异步 & 状态** — 每个 Promise `await`ed；多步 ID 作为字符串字面量传递（规则 15, 17）

## 9. 在创建之前发现约定

**始终在创建任何内容之前检查 Figma 文件。** 不同的文件使用不同的命名约定、变量结构和组件模式。您的代码应该与现有的内容匹配，而不是强加新的约定。

当对任何约定（命名、作用域、结构）有任何疑问时，请首先检查 Figma 文件，然后是用户的代码库。只有在两者都不存在时，才回退到常见模式。

### 快速检查脚本

**列出所有页面和顶级节点:**
```js
const pages = figma.root.children.map(p => `${p.name} id=${p.id} children=${p.children.length}`);
return pages.join('\n');
```

**列出所有页面中的组件:**

`search_design_system` 是发布组件的选项。对于画布组件，请使用两步扇出——**不要在单个脚本中循环页面。**

步骤 1: 一个只读的 `use_figma` 以获取页面 ID:
```js
return figma.root.children.map(p => ({ id: p.id, name: p.name }));
```

步骤 2: 在**下一个助手回合中，并行发出一个 `use_figma` 每个页面**（一个包含 N 个工具使用块的单一消息）。每个脚本运行:
```js
const page = await figma.getNodeByIdAsync(PAGE_ID);
await figma.setCurrentPageAsync(page);
// findAllWithCriteria 使用索引类型查找——比 findAll(n => n.type === '…') 侧效应在谓词中的反模式快数百倍.
const matches = page.findAllWithCriteria({ types: ['COMPONENT', 'COMPONENT_SET'] });
return matches.map(n => ({ page: page.name, name: n.name, type: n.type, id: n.id }));
```

**列出现有的变量集合及其约定:**
```js
const collections = await figma.variables.getLocalVariableCollectionsAsync();
const results = collections.map(c => ({
  name: c.name, id: c.id,
  varCount: c.variableIds.length,
  modes: c.modes.map(m => m.name)
}));
return results;
```

## 10. 参考文档

根据您的任务涉及的内容按需加载这些文档：

| 文档 | 加载时间 | 涵盖内容 |
|-----|-------------|----------------|
| [gotchas.md](references/gotchas.md) | 在任何 `use_figma` 之前 | 每个已知的陷阱，包括 WRONG/CORRECT 代码示例——从 [标准的文本编辑配方](references/gotchas.md#canonical-text-edit-recipe-font-load--await--mutate--return-ids) 开始 |
| [common-patterns.md](references/common-patterns.md) | 需要工作代码示例 | 脚本脚手架：形状、文本、自动布局、变量、组件、多步骤工作流 |
| [plugin-api-patterns.md](references/plugin-api-patterns.md) | 创建/编辑节点 | 填充、描边、自动布局、效果、分组、克隆、样式 |
| [api-reference.md](references/api-reference.md) | 需要精确的 API 表面 | 节点创建、变量 API、核心属性、什么有效，什么无效 |
| [validation-and-recovery.md](references/validation-and-recovery.md) | 多步骤写入或错误恢复 | `get_metadata` 与 `get_screenshot` 工作流程、强制错误恢复步骤 |
| [component-patterns.md](references/component-patterns.md) | 创建组件/变体 | combineAsVariants、组件属性、INSTANCE_SWAP、变体布局、发现现有组件、元数据遍历 |
| [variable-patterns.md](references/variable-patterns.md) | 创建/绑定变量 | 集合、模式、作用域、别名、绑定模式、发现现有变量 |
| [text-style-patterns.md](references/text-style-patterns.md) | 创建/应用文本样式 | 类型坡道、通过 `listAvailableFontsAsync` 发现字体、列出样式、将样式应用于节点 |
| [effect-style-patterns.md](references/effect-style-patterns.md) | 创建/应用效果样式 | 阴影、列出样式、将样式应用于节点 |
| [plugin-api-standalone.index.md](references/plugin-api-standalone.index.md) | 需要了解完整的 API 表面 | 所有类型、方法和属性在插件 API 中的索引 |
| [plugin-api-standalone.d.ts](references/plugin-api-standalone.d.ts) | 需要精确的类型签名 | 完整的 typings 文件——搜索特定符号，不要一次性加载所有内容 |

## 11. 代码片段示例

您将在本文档的文档中看到代码片段。这些代码片段包含有用的插件 API 代码，可以重新使用。直接使用它们，或者作为您进行中的起点代码。如果关键概念最好作为通用代码片段记录，请指出并写入磁盘，以便将来可以重用。
