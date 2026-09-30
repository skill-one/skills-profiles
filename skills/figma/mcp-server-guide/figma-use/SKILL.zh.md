---
name: figma-use
description: '**必须的先决条件** — 你必须在每次调用 `use_figma` 工具之前调用这个技能。绝对不能在未加载此技能的情况下直接调用 `use_figma`。跳过它会导致常见且难以调试的失败。当用户想要在 Figma 文件上下文中执行写操作或需要 JavaScript 执行的独特读操作时触发——例如创建/编辑/删除节点、设置变量或标记、构建组件和变体、修改自动布局或填充、将变量绑定到属性，或以编程方式检查文件结构。'
---

# use_figma — Figma 插件 API 技能

通过插件 API 在 Figma 文件中执行 JavaScript。调用 `use_figma` 时**始终传递 `skillNames: "figma-use"`**（日志参数，不影响执行）。

**如果任务涉及从代码在 Figma 中构建或更新整个页面、屏幕或多部分布局**，请同时加载 [figma-generate-design](../figma-generate-design/SKILL.md)。它提供了通过 `search_design_system` 发现设计系统组件、导入它们以及逐步组装屏幕的工作流程。这两种技能协同工作：这个技能用于 API 规则，那个技能用于屏幕构建工作流程。

**如果任务涉及在 Figma 中创建或构建组件（即使是单个组件），也请同时加载 [figma-generate-library](../figma-generate-library/SKILL.md)。** 它拥有组件创建工作流程——首先是变量基础、然后是变体集，最后是设计令牌绑定——而 `figma-use` 单独无法涵盖这些。在构建组件之前构建令牌/变量基础，然后将组件的 `fills`/`cornerRadius`/间距绑定到这些变量，而不是在存在令牌的地方内联字面量。

**重要提示：** 每次您处理设计系统时，请从 [working-with-design-systems/wwds.md](references/working-with-design-systems/wwds.md) 开始，以了解 Figma 中与设计系统相关的基本概念、流程和指南。然后根据需要加载更具体的组件、变量、文本样式和效果样式的参考。

## $fig — 基于计划的构建 API（所有节点创建必须使用此 API）

`$fig` 是一个全局变量，负责所有节点的创建。它在脚本结束时自动刷新（不需要 `$fig.done()`），处理字体预加载、批量变异，并正确排序属性分配。**用于所有节点创建和变异操作。** 永远不要使用 `figma.createFrame()`、`figma.createText()` 或任何 `figma.create*` 方法。在这个环境中它们不存在。

### 复制这些模式

**使用单个调用构建具有子项的自动布局框架：**
```js
$fig.autoLayout(
  // 固定宽度；省略高度以垂直包裹
  { name: '待办事项列表', layoutMode: 'VERTICAL', width: 480 },
  ['项目 1', '项目 2', '项目 3'].map((item) =>
    $fig.autoLayout(
      // 将 `layoutSizingHorizontal` 设置为 FILL，因为自动布局默认情况下是 x x x 包裹
      { name: '待办事项', layoutSizingHorizontal: 'FILL' },
      [$fig.text({ characters: item, fontName: { family: 'Inter', style: 'Bold' } })],
    ),
  ),
).screenshot() // 截屏新的节点树以进行验证。优先使用 `.screenshot()` 而不是在 `use_figma` 之后调用 `get_screenshot`。
```

**N 个平行项用于重复的小 UI 元素，如色板、列表项等：**
```js
const ITEMS = [
  { name: 'A', bg: hex('#ffffff'), accent: hex('#0969da') },
  { name: 'B', bg: hex('#fff8f1'), accent: hex('#bf5af2') },
  // ...在这里添加更多
]
ITEMS.forEach((v, i) => $fig.autoLayout({ name: v.name, x: i * 410, width: 390, fills: [{ type:'SOLID', color: v.bg }] }, [
  $fig.text({ characters: v.name, fills: [{ type:'SOLID', color: v.accent }] }),
]))
```

**更新现有节点——通过查询或通过 ID：**
```js
$fig.query('FRAME[name=Header] TEXT[name=Title]').set({ characters: '新标题', fontSize: 24 })
$fig.get('1:42').set({ opacity: 0.8, cornerRadius: 12 })
```

**在现有节点内添加节点**
```js
$fig.get('1:42').append($fig.autoLayout({ name: '新框架' }))
```

**创建具有几个不同变体的组件**
```js
const SIZES = ['Small', 'Medium', 'Large']
$fig.variants({ name: '按钮' }, SIZES.map((size) => $fig.component({ name: `Size=${size}`, layoutMode: 'HORIZONTAL', /** 其他属性 */ })))
```
> ⚠️ `$fig.variants` **不**定位变体——它们在 (0,0) 处堆叠，集合渲染为一个折叠的、重叠的元素。您必须在之后对变体进行网格化并调整集合大小。参见 [`fig-builder.md`](references/fig-builder.md#required-follow-up--grid-the-variants-fig-build--raw-layout) 以获取所需的后续配方。

> **构建组件——即使是单个组件？绑定令牌化值是完成工作的一部分，而不是一种选择。** 只要任何具有相应设计令牌的值（该令牌已存在于文件中，或您从源创建的）仍然是硬编码的字面量，组件就**不完整**。当 `fills` 颜色 / `cornerRadius` / 填充 / `itemSpacing` 存在令牌时，请绑定它：构建一个 `$fig.varCollection`（原始层级 + 意义层级别别名为它），并将变量**句柄直接传递到属性**中。**要避免的反模式：** 不要将解析后的令牌值复制到本地 JS 常量（例如 `const VARIANTS = [{ bg: '#2c2c2c' }]`）并使用 `hex(...)` 绘制——即使源定义了令牌，这也默默地绕过了变量。这适用于单个组件，也适用于完整的设计系统。**只绑定实际具有令牌的值**——没有令牌的真实值（一次性几何形状、图标像素大小、静态 1px 分隔符）正确保持为字面量；不要编造令牌来绑定。**如果您在一个 `use_figma` 调用中创建变量，在稍后的调用中构建组件，请首先重新加载句柄** (`$fig.getVar(id)` 或 `figma.variables.getVariableByIdAsync` 使用您返回的 ID)——先前调用的句柄不在作用域内。有效配方：[fig-builder.md → 使用绑定变量的组件构建](references/fig-builder.md#building-a-component-with-bound-variables-the-default-for-components)。

**创建组件的实例**
```js
// 第一个参数可以是节点 ID ('1:2') 或来自 `search_design_system` 结果的库资源键（`componentKey` 字段）。
$fig.instance('1:2', { name: '取消按钮', props: { label: '取消'}})
```

**使用样式/变量**
```js
$fig.autoLayout({ name: '卡片', itemSpacing: spacingVar, fills: fillStyle })

// 通过 `search_design_system` 的资产键查找（`key` 字段）
$fig.autoLayout({ fills: $fig.getStyle(BG_STYLE_KEY) })
$fig.rectangle({ fills: [{ type: 'SOLID', color: $fig.getVar(BRAND_VAR_KEY) }] })
```

**使用设计系统资源（通过键）**

`search_design_system` 返回组件和组件集的 `componentKey`，以及样式和变量的 `key`。直接将这些键传递到统一的 `$fig` 查找——计划会自动排队库导入，因此您不需要单独的 `await figma.importComponentByKeyAsync(...)` / `importStyleByKeyAsync(...)` / `importVariableByKeyAsync(...)` 步骤。
```js
// 一个调用位置，多个输入形状——节点 ID、真实的变量/样式 ID，
// 以及 40 个字符的资产键（例如 '49c8754d4b898e176148650df612a47998a8c4a1'）
const btn        = $fig.get(BUTTON_KEY)                    // 组件 / 组件集
const instance   = $fig.instance(BUTTON_SET_KEY, {         // 从集合中创建一个实例
  props: { Size: 'md', Variant: 'primary' },
})
const heading    = $fig.getStyle(HEADING_TEXT_STYLE_KEY)   // 绘制 / 文本 / 效果 / 网格样式
const brand      = $fig.getVar(BRAND_COLOR_VAR_KEY)        // 变量

$fig.text({ characters: 'Hello', textStyle: heading })
$fig.rectangle({ fills: [{ type: 'SOLID', color: brand }] })
```

**从其键发现集合的变体属性**——`search_design_system` 返回集合的 `componentKey`，而不是其变体属性。这是**两个 `use_figma` 调用**：调用 1 `返回` 集合的属性定义及其变体，以便它们的属性在工具结果中返回给您；然后，知道有效属性后，调用 2 实例化您想要的变体。
```js
const setHandle = $fig.get(BUTTON_SET_KEY)
await $fig.done()
const set = setHandle.node
if (!set || set.type !== 'COMPONENT_SET') {
  throw new Error(`键 ${BUTTON_SET_KEY} 不是一个 COMPONENT_SET`)
}
return {
  componentPropertyDefinitions: set.componentPropertyDefinitions,
  variants: set.children
    .filter((c) => c.type === 'COMPONENT')
    .map((c) => ({ name: c.name, variantProperties: c.variantProperties })),
}
```
```js
// 调用 2 — 使用调用 1 输出中挑选的属性实例化
$fig.instance(BUTTON_SET_KEY, { props: { Size: 'Large', Kind: 'Secondary' } })
```

**批量组件替换——`$fig.query().set()`：**
```js
const chevron = $fig.get('CHEVRON_KEY')
$fig.query('INSTANCE[name=arrow_drop_down]').set({ mainComponent: chevron })
```

**`.query()` 和 `.values()` 用于搜索和投影子值**
```js
const menuArrows = $fig
  .query('PAGE[name=Menu] INSTANCE[mainComponent.name*=arrow], PAGE[name=Menu] INSTANCE[mainComponent.name*=chevron]')
  .values(['id', 'name', 'mainComponent.name', 'mainComponent.id']);

// 使用引号表示多词选择器值
const expandComponents = $fig
  .query('COMPONENT[name*=expand], COMPONENT[name*=chevron_down], COMPONENT[name*=chevron_up], COMPONENT[name*="多词名称"]')
  .values(['id', 'name']);
```

**在另一个页面上执行操作：**
```js
// 切换到特定页面（加载其内容）
const targetPage = figma.root.children.find((p) => p.name === "我的页面");
await figma.setCurrentPageAsync(targetPage);
$fig.query('INSTANCE[name=arrow_drop_down]').set({ ... })
```

**通过辅助函数实现渐变——无需手动变换矩阵：**
```js
$fig.gradient(node, 'LINEAR', [
  { position: 0, color: { r: 0, g: 0, b: 0 } },
  { position: 1, color: { r: 1, g: 1, b: 1 } },
])
```

**脚本顶部的十六进制辅助函数：**
```js
const hex = h => { const n = parseInt(h.replace('#',''), 16); return { r:((n>>16)&255)/255, g:((n>>8)&255)/255, b:(n&255)/255 } }
// 然后：color: hex('#2563eb')
```

**计划节点上的链接——替代子项数组：**
```js
const card = $fig.autoLayout({ name: '卡片', layoutMode: 'VERTICAL' })
card.text({ characters: '标题', fontSize: 20 })
card.text({ characters: '描述', fontSize: 14 })
```

### `$fig` 创建 + 变异 API（完整表面）

- **创建：** `$fig.autoLayout / .frame / .text / .rectangle / .ellipse / .polygon / .star / .line / .vector / .section / .component / .page` — 所有 `(opts?, children?)`。计划节点是可链接的。
- **从 SVG 创建——首选的 ICON 路径：** `$fig.svg(svgStr, opts?)` 从 SVG 字符串构建矢量节点树。**优先使用真实的矢量图标：** 通过 `$fig.svg(...)` 导入图标的 SVG 源（内联 `<svg>`、`.svg` 资产，或源图标库字形——例如 lucide/heroicons）而不是用键入的 Unicode 字符/表情符号（★ ⚙ 🔍 ☰ ▾）或一个普通的矩形来近似图标。当真实的 SVG 真正无法获取时，一个简单的字形或形状是一个很好的后备方案——首先尝试 SVG。（不要从旋转的线/矩形原始图形中重建图标。）完整配方（viewBox+宽度/高度大小、`currentColor`、INSTANCE_SWAP 用于设计系统图标）：[figma-generate-design → 图标](../figma-generate-design/SKILL.md#icons-import-the-svg-never-reconstruct-from-rotated-primitives)。
- **创建组件的实例：** `$fig.instance(compRef, opts?)` — `compRef` 是一个组件计划节点、节点 ID 字符串，或库资产键（`componentKey` 来自 `search_design_system`）；导入在计划中自动排队。
- **分组/布尔值：** `$fig.group / .union / .subtract / .intersect / .exclude / .variants` — 所有 `(opts?, children?)`。
- **读取：** `$fig.get(id)` 包装一个现有的 `SceneNode` — `id` 可以是一个真实的节点 ID 或库资产键（`componentKey` 来自 `search_design_system`）；导入在计划中自动排队。`$fig.query(selector, scope?)` 返回 `{ length, values(paths), first(), last(), each(fn), filter(fn), set(props), moveTo(parent, idx?), remove() }`。选择器是 CSS 类似的（例如 `'FRAME[name*=Card] TEXT'`）。`$fig.getStyle(nameOrIdOrKey)` 和 `$fig.getVar(nameOrIdOrKey)` 接受来自 `search_design_system` 的匹配 `key` 值。
- **变异：** `$fig.set(target, props)`, `.delete(...nodes)`, `.move(target, parent, idx?)`, `.clone(target, props?)`, `.append(parent, child)`, `.addAt(parent, idx, child)`, `.replace(old, new)`, `.reorder(parent, children)`, `.gradient(node, type, stops, transform?)`, `.image(node, hash, scaleMode?)`。
- **计划节点方法（可链接）：** `.set()`, `.remove()`, `.clone()`, `.moveTo(parent, idx?)`, `.append(child)`, `.query(selector)`, `.screenshot({scale?, contentsOnly?})`，以及 `.node` 获取器用于已实现的 `SceneNode`（刷新前为 null）。

### 何时使用原始 Figma 插件 API

仅在这种情况下——即使在这种情况下，也在同一脚本中混合原始 API 与 `$fig`：

- **脚本中途需要异步结果：** `await figma.setCurrentPageAsync(...)`, `await figma.loadFontAsync(...)` — 必须在后续的计划步骤使用结果之前完成。 （导入库组件不是这种情况：直接将 `componentKey` 传递到 `$fig.get(...)` / `$fig.instance(...)` 并在 `props` 中传递变体属性值。`$fig` 在计划中排队库导入并为您解析变体。）
- **脚本中途读取真实节点状态：** 自动布局后的测量 `width` / `height`、计算颜色、获取StyledTextSegments — 在脚本中途实例化，然后在计划节点的 `.node` 上读取。参见 [references/fig-builder.md](references/fig-builder.md) 以获取脚本中途检查模式。
- **`$fig` 真正不暴露的事情：** `node.setRangeFontName(...)` 等。通过 `planNode.node` 访问（参见 [references/fig-builder.md](references/fig-builder.md)）。

## 关键规则

1. **仅使用 `$fig` 进行创建 / 批量编辑节点** (`$fig.autoLayout(...)`, `$fig.text(...)`, `$fig.query(...).set(...)`)。原始插件 API 是后备——仅在 `$fig` 无法表达操作时使用它（中间节点状态读取、非 SceneNode 类型如变量）。库组件不是离开 `$fig` 的理由：`$fig.get(componentKey)` / `$fig.instance(componentSetKey, { props })` 自动排队库导入并解析变体。参见 [references/fig-builder.md](references/fig-builder.md) 和 [references/critical-rules-deep.md](references/critical-rules-deep.md) 以获取错误的/正确的示例。

2. **不要直接使用 `findOne`、`findAll`、`findAllWithCriteria`、`findChildren`、`findChild` 进行节点搜索** 它们比 `query()` 更冗长、更容易出错且效率更低。此外，不要使用递归来搜索。

3. **如果仅使用 `$fig`，避免 `return` / `$fig.done()`** — 运行时自动刷新并返回一个 `FigDoneResult`，其中包含创建/更新的节点 ID。如果您需要在脚本中途使用原始插件 API 或其他数据，请使用 `return`。

4. **通过部分逐步构建更大的设计。** 参考设计系统技能 [figma-generate-design](../figma-generate-design/SKILL.md) 以获取占位符 + 替换工作流程。在内部创建带有占位符的屏幕，例如 `$fig.autoLayout({ name: 'Header', layoutSizingHorizontal: 'FILL', placeholder: true })`，然后通过后续的 `use_figma` 调用替换它们并截图：`$fig.get("从上一步获取的占位符 ID").replace( ... ).screenshot()`。每工具调用最多可进行 5 个 `.screenshot()` 调用。如果您需要更多截图，您的工作量过多，需要将任务分解为多个 `use_figma` 调用。

5. **顶层的纯 JS `await`。** 代码自动包装为异步。不要用 `(async () => {})()` 包裹。

6. **颜色是 0–1 RGB；所有字段都是必需的。** `{r, g, b}` — 没有 `hex:`，没有 `a:` 在颜色中。不透明度在颜色外部：`{type:'SOLID', color:{r,g,b}, opacity: 0.5}`。十六进制辅助函数：`const hex = h => { const n = parseInt(h.replace('#',''), 16); return { r:((n>>16)&255)/255, g:((n>>8)&255)/255, b:(n&255)/255 } }`。参见 [references/critical-rules-deep.md](references/critical-rules-deep.md) 以获取错误的/正确的。

7. **没有 `curl` / `wget` / `Read` 来自 `Bash` 的 Figma URL。** 仅通过 `use_figma` 和 `mcp__figma__*` 工具访问 Figma 文件。在 `get_screenshot` 之后，图像嵌入在工具结果中——不要重新获取或重新读取它。

8. **空 / 不支持的响应是终止的。** 接受并继续——不要尝试替代绕过路径。

9. **在修改属性前验证节点类型**。只有 `FRAME / COMPONENT / COMPONENT_SET / INSTANCE / GROUP / SECTION / PAGE` 才有 `.children`。`GROUP` 没有 `fills` / `strokes` / `cornerRadius`。`TEXT` 没有 `cornerRadius` / `padding*` / `layoutMode`。`layoutPositioning='ABSOLUTE'` 需要 `layoutMode !== 'NONE'` 的父节点。检查 `'<prop>' in node` 或 grep [references/plugin-api-standalone.d.ts](references/plugin-api-standalone.d.ts)。完整列表见 [references/critical-rules-deep.md](references/critical-rules-deep.md)。

10. **不要重复查询相同信息**。对同一目标进行两次 `get_metadata` / `get_comments` 会得到相同的结果。在脑中缓存。

11. **获取足够信息后果断行动**。不要继续收集——来自第三个截图或第四次元数据调用的边际信息几乎为零。

12. **来自 `use_figma` 的 `"An unexpected error occurred"` 是服务器端问题，不是你的脚本错误**。不要重试未更改的——改变方法（更小的批次、不同的选择器、删除一个节点属性）。

13. **永远不要调用 `mcp__figma__get_design_context`。禁止**。这个工具需要选择（在此环境中不存在选择），所以每次调用都会失败。错误不可恢复——调用它只会浪费一个工具槽并强制重试。对于文件的结构化读取，使用 `mcp__figma__get_metadata`（用于顶层框架发现）和 `use_figma` 配合 `$fig.query()`。**任何情况下都不要调用 `get_design_context`。**

14. **当任务引用源代码时，代码库 `Read` 调用不超过3次**。超过之后，仅使用 grep。第四次代码库 `Read` 被禁止——用你现有的 `use_figma` 脚本。

15. **同一错误重试3次 → 改变方法**。通常：切换到 `$fig`（它会自动处理排序）。修补原始API不起作用。

16. **除非有充分的理由，否则必须使用自动布局**。使用 `$fig.autoLayout(...)` 创建自动布局框架，而不是绝对定位节点。新的自动布局框架在两个轴上都会紧贴内容。如果你想让自动布局子元素填充自动布局容器的反轴，请显式分配 `layoutSizingHorizontal` 或 `layoutSizingVertical` 为 `'FILL'`。

17. **渐变填充需要所有字段**：`type`、`gradientStops`、`gradientTransform`（一个 `[[a,b,tx],[c,d,ty]]` 矩阵）。缺少任何字段都会引发验证错误。见 [references/critical-rules-deep.md](references/critical-rules-deep.md)。

18. **发现可用字体，尤其是用于样式变化**。使用 `await figma.listAvailableFontsAsync()` 发现 `$fig.text({ fontName: ... })` 的可用字体。

19. **创建变量时显式设置 `scopes`**。默认的 `ALL_SCOPES` 会污染每个属性选择器。使用特定作用域——`['FRAME_FILL', 'SHAPE_FILL']` 用于背景，`['TEXT_FILL']` 用于文本，`['GAP']` 用于间距，`['CORNER_RADIUS']` 用于半径；不应出现在选择器中的原始类型会得到 `[]`。在 `$fig` 中，将 `scopes` 传递给 `colorVar` / `numVar`；在原始API中，设置 `variable.scopes`。见 [references/variable-patterns.md](references/variable-patterns.md)。

### 批量修改现有节点（交换/更新/替换）在3次 `use_figma` 调用中完成

对于“交换 N 个图标”、“更新 M 个颜色”、“替换 K 个实例”等任务：
1. **发现 + 修改** 在一个脚本中（通过 `figma.currentPage.query()` 查找，导入任何组件，通过 `$fig.query(...).each(...)` 修改，返回计数）。
2. **验证**（可选）——只读的 `.query()` 计数。
3. **最终报告** 在助手文本中，无工具调用。停止。

不要第四次调用。不要追逐最后20%的边缘情况。如果第一次调用出错，修复并重做——那仍然是你的一个修改调用。完整模板见 [references/critical-rules-deep.md](references/critical-rules-deep.md)。

## 节点属性陷阱

不要猜测节点属性或假设类似CSS的属性。访问不存在的属性会抛出 `TypeError: node.foo: no such property 'foo' on TYPE node`。每次抛出都会消耗一次重试。[plugin-api-standalone.index.md](references/plugin-api-standalone.index.md) 包含API中所有符号的列表。使用该文件并 grep 完整的API类型定义 [plugin-api-standalone.d.ts](references/plugin-api-standalone.d.ts) 以获取完整定义。

- **只有 `FRAME` / `COMPONENT` / `COMPONENT_SET` / `INSTANCE` / `GROUP` / `SECTION` / `PAGE` 有 `.children`。** `RECTANGLE`、`TEXT`、`ELLIPSE`、`POLYGON`、`STAR`、`VECTOR`、`LINE`、`SLICE`、`STICKY`、`SHAPE_WITH_TEXT`、`STAMP`、`CONNECTOR`、`TABLE`、`WIDGET`、`EMBED`、`MEDIA` 没有。在访问节点的子节点前检查 `'children' in node`。
- **`GROUP` 没有 `fills` / `strokes` / `cornerRadius`。** 在内部的子形状上应用填充/半径。
- **Figma自动布局 != CSS flexbox。** 没有所谓的边距。
- **`TEXT` 没有容器属性**。文本有字体/大小/装饰/填充。不要使用类似容器的属性，如填充、布局模式、项间距等。
- **`INSTANCE` 的后代在结构操作中是只读的**——你不能 `appendChild` / `insertChild` 到实例子节点。先编辑源 `COMPONENT` 或先分离。
- **永远不要在节点上使用 `primaryAxisSizingMode` 或 `counterAxisSizingMode`。** 使用 `layoutSizingHorizontal` 或 `layoutSizingVertical` 配合 'FIXED' | 'HUG' | 'FILL'。只有在父节点有自动布局时才使用 'FILL'。
- **没有 `instance.swapMainComponent(...)`。** 使用 `instance.setProperties({...})` 配合组件属性变体值，或 `$fig.query(...).set({props: {...}})`。有 `instance.swapComponent(component)`（不同的方法名）。

## 参考

- [references/fig-builder.md](references/fig-builder.md) — 完整的 `$fig` API 和工作模式
- [references/critical-rules-deep.md](references/critical-rules-deep.md) — 错误/正确示例，完整节点类型陷阱列表，批量修改模板，语法错误检查清单
- [references/gotchas.md](references/gotchas.md) — 原始插件API边缘情况
- [references/plugin-api-standalone.d.ts](references/plugin-api-standalone.d.ts) — 类型定义（grep，不要通读）
- [references/plugin-api-standalone.index.md](references/plugin-api-standalone.index.md) — API导航
- [references/common-patterns.md](references/common-patterns.md)、[component-patterns.md](references/component-patterns.md)、[variable-patterns.md](references/variable-patterns.md)、[text-style-patterns.md](references/text-style-patterns.md)、[effect-style-patterns.md](references/effect-style-patterns.md) — 模式手册
- [references/working-with-design-systems/](references/working-with-design-systems/) — 设计系统工作流
- [references/validation-and-recovery.md](references/validation-and-recovery.md) — 错误恢复模式
