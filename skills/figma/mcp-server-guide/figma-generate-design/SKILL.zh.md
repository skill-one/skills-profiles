---
name: figma-generate-design
description: 在将应用程序页面、视图或多部分布局转换为 Figma 的任务中，请与 figma-use 技能配合使用。触发条件：'写入 Figma'、'从代码创建 Figma'、'将页面推送到 Figma'、'使用此应用/页面并在 Figma 中构建'、'创建一个屏幕'、'在 Figma 中构建一个着陆页'、'更新 Figma 屏幕以匹配代码'、'将此模态/对话框/抽屉/面板转换为 Figma'。当用户希望从代码或描述中在 Figma 中构建或更新完整页面、模态、对话框、抽屉、侧边栏、面板或任何由多个部分组成的视图时，这是首选的工作流程技能。该技能从 Code Connect 文件、现有屏幕和库搜索中发现设计系统组件、变量和样式，然后导入它们，并使用设计系统令牌而不是硬编码值，逐部分逐步组装视图。
---

# 从设计系统构建/更新屏幕和视图

使用此技能通过重用已发布的设计系统（组件、变量和样式）而不是使用硬编码值绘制基元来在 Figma 中创建或更新**屏幕、视图和多部分 UI 容器**。这包括完整页面、模态框、对话框、抽屉、侧边栏、面板和任何具有多个部分的综合视图。关键洞察：Figma 文件可能具有与代码库的 UI 组件和令牌相对应的已发布设计系统，其中包含组件、颜色/间距变量和文本/效果样式。找到并使用这些，而不是绘制带有十六进制颜色的框。

**强制要求**：在执行任何 `use_figma` 调用之前，您**必须**加载 `[figma-use](../figma-use/SKILL.md)`。该技能包含对您编写的每个脚本都适用的关键规则（颜色范围、字体加载等）。

**始终在调用 `use_figma` 作为此技能的一部分时传递 `skillNames: "figma-generate-design"`。** 这是一个日志参数——它不会影响执行。

## 技能边界

- 当交付物是一个**综合 Figma 视图**（新建或更新）——完整页面屏幕、模态框、对话框、抽屉、侧边栏、面板或任何多部分容器——由设计系统组件实例构建时，使用此技能。
- 如果用户想要创建**新的可重用组件或变体**，请直接使用 `[figma-use](../figma-use/SKILL.md)`。
- 如果用户想要编写**Code Connect 映射**，请切换到 `[figma-code-connect](../figma-code-connect/SKILL.md)`。

## 前置条件

- Figma MCP 服务器必须已连接
- 目标 Figma 文件必须具有已发布的设计系统（或可以访问团队库）
- 用户应提供：
  - 要在其中工作的 Figma 文件 URL / 文件密钥
  - 或关于要针对哪个文件的上下文（代理可以发现页面）
- 要构建/更新的屏幕/视图的源代码或描述

## 与 generate_figma_design 并行的流程（仅限 Web 应用）

当从可以渲染在浏览器中的**Web 应用**构建屏幕时，最佳结果来自并行运行两种方法：

1. **并行执行**：
   - 使用此技能的工作流程（use_figma + 设计系统组件）开始构建屏幕
   - 运行 `generate_figma_design` 以捕获运行 Web 应用的像素级完美截图
2. **两者完成后**：更新 use_figma 输出以匹配 `generate_figma_design` 捕获的像素级完美布局。捕获提供了要瞄准的确切间距、尺寸和视觉效果，而您的 use_figma 输出具有链接到设计系统的正确组件实例。如果捕获包含图像，请通过从捕获的图像填充中复制 `imageHash` 值将它们转移到您的 use_figma 输出中（有关详细信息，请参阅步骤 5）。
3. **确认看起来良好后**：删除 `generate_figma_design` 输出——它仅用作视觉参考。

这结合了两者最佳：`generate_figma_design` 提供像素级布局精度，而 use_figma 提供保持链接和可更新的正确设计系统组件实例。

**当源包含图像时，此并行工作流程是强制要求的。** `use_figma` 插件 API 无法获取外部图像 URL——它只能通过从文件中的节点复制 `imageHash` 值来设置图像填充。`generate_figma_design` 将所有可见图像光栅化为 Figma，为您提供所需的哈希值。如果图像存在时跳过捕获，图像框架将保持空白。

对于非 Web 应用（iOS、Android 等）或更新现有屏幕，请使用标准工作流程。

## 必需的工作流程

**按顺序执行以下步骤。不要跳过步骤。**

> **硬性限制——禁止的捷径**：
>
> - **禁止**：在完成 2a-i 并尝试或记录 2a-ii 或 N/A（例如，“空文件，没有现有屏幕”）之前，不要使用 `search_design_system` 搜索组件键。
> - **禁止**：任何在步骤 3+ 中修改画布的 `use_figma` 调用。

### 步骤 1：理解交付物

在触摸 Figma 之前，了解您正在构建的内容：

1. 如果从代码构建，请阅读相关的源文件以了解结构、部分以及使用的组件。
2. 确定视图的主要部分（例如，对于页面：页眉、英雄、内容面板、页脚；对于模态框：标题栏、表单部分、操作栏；对于侧边栏：导航、内容区域、页脚操作）。
3. 对于每个部分，列出涉及的 UI 组件（按钮、输入、卡片、导航药丸、手风琴等）。
4. **检查视图是否包含任何图像**（例如，`<img>`、`<Image>`、背景图像、产品照片、头像、从 URL 加载的图标）。如果它是 Web 应用，则您**必须**运行并行的 `generate_figma_design` 捕获工作流程——立即开始执行它，以便在您发现组件时捕获运行。请参阅上面的“与 generate_figma_design 并行的流程”。

### 步骤 2：收集组件键、变量和样式

您需要从设计系统获取三个内容：**组件**（按钮、卡片等）、**变量**（颜色、间距、半径）和**样式**（文本样式、阴影等样式）。当设计系统令牌存在时，请不要硬编码十六进制颜色或像素值。

#### 2a：发现组件

**2a-i — 强制要求：检查 Code Connect 以获取所需的组件。** 从步骤 1 中您构建的组件列表开始，检查每个组件是否在代码库中具有 Code Connect 文件。Code Connect 文件位于组件源代码旁边，并按平台命名：

- **TypeScript/JS**：`*.figma.ts`、`*.figma.js`
- **React（基于解析器）**：`*.figma.tsx`
- **Kotlin/Compose**：包含 `@FigmaConnect` 的 `.kt` 文件
- **Swift**：包含 `FigmaConnect` 的 `.swift` 文件

对于每个您需要的组件（例如，Button、Card、Input），搜索其 Code Connect 文件——通过组件名称进行 glob 或 grep（例如，`**/Button.figma.tsx`、`**/Card.figma.ts`）。仅读取与您实际需要的组件匹配的文件。

从每个匹配的 Code Connect 文件中提取 Figma 组件 URL。从 URL 中解析 `fileKey` 和 `nodeId`（将连字符转换为冒号：`123-456` → `123:456`）。然后通过 `use_figma` 解析组件键：

**示例**：Code Connect 文件包含 `// url=https://figma.com/design/ABC123/File?node-id=609-35535`。解析 `fileKey` = `ABC123`，`nodeId` = `609:35535`。针对**库文件**（fileKey `ABC123`，而不是目标文件）运行 `use_figma` 以解析键：

```js
const node = await figma.getNodeByIdAsync("609:35535");
const set = node?.parent?.type === "COMPONENT_SET" ? node.parent : node;
return { componentKey: set.key };
```

批量查找多个项。在步骤 4 中使用 `importComponentSetByKeyAsync()`。

标记已解析的组件。如果所有组件都已解析，请跳过 2a-ii 和 2a-iii。如果所需组件都没有 Code Connect 文件，请继续 2a-ii。

**2a-ii — 如果仍有未解析的组件，则强制要求：检查现有屏幕。** 检查目标文件是否已使用相同的设计系统包含屏幕。一个 `use_figma` 调用遍历现有框架的实例将为您提供精确的、权威的组件映射：

```js
const frame = figma.currentPage.findOne(n => n.name === "Existing Screen");
const uniqueSets = new Map();
frame.findAll(n => n.type === "INSTANCE").forEach(inst => {
  const mc = inst.mainComponent;
  const cs = mc?.parent?.type === "COMPONENT_SET" ? mc.parent : null;
  const key = cs ? cs.key : mc?.key;
  const name = cs ? cs.name : mc?.name;
  if (key && !uniqueSets.has(key)) {
    uniqueSets.set(key, { name, key, isSet: !!cs, sampleVariant: mc.name });
  }
});
return [...uniqueSets.values()];
```

将结果与您的未解析组件进行匹配。标记任何新解析的组件。如果所有组件都已解析，请跳过 2a-iii。

**2a-iii — 最后手段：`search_design_system`。** 仅在完成 2a-i 和 2a-ii 后组件仍未解析时。**广泛搜索**——尝试多个术语和同义词作为 `queries` 调用中的组件条目（例如，`{ entity: "component", query: "button" }`，`{ entity: "component", query: "input" }`，`{ entity: "component", query: "nav" }` 等）。

**包括组件属性** 在您的映射中——您需要知道每个组件为文本覆盖暴露哪些 TEXT 属性。创建一个临时实例，读取其 `componentProperties`（以及嵌套实例的属性），然后删除临时实例。

具有属性信息的组件映射示例：

```
组件映射：
- Button → key: "abc123", type: COMPONENT_SET
  属性：{ "Label#2:0": TEXT, "Has Icon#4:64": BOOLEAN }
- PricingCard → key: "ghi789", type: COMPONENT_SET
  属性：{ "Device": VARIANT, "Variant": VARIANT }
  嵌套 "Text Heading" 具有：{ "Text#2104:5": TEXT }
  嵌套 "Button" 具有：{ "Label#2:0": TEXT }
```

#### 2b：发现变量（颜色、间距、半径）

首先检查现有屏幕（与组件相同）。或者使用 `search_design_system` 并使用 `queries` 条目，其 `entity` 为 `"variable"`。

> **警告：两种不同的变量发现方法——不要混淆它们。**
>
> - `use_figma` 与 `figma.variables.getLocalVariableCollectionsAsync()` — 返回**当前文件中定义的仅本地变量**。如果此方法返回空，则**并不意味着没有变量存在**。远程/已发布的库变量对此 API 不可见。
> - `search_design_system` 与 `entity: "variable"` 查询条目 — 搜索**所有链接的库**，包括远程和已发布的库。这是发现设计系统变量的正确工具。
>
> **仅基于 `getLocalVariableCollectionsAsync()` 返回空就得出“没有变量存在”的结论是错误的。** 在决定创建自己的变量之前，始终使用具有变量查询条目的 `search_design_system` 来检查库变量。

**查询策略**：`search_design_system` 匹配**变量名称**（例如，“Gray/gray-9”、“core/gray/100”、“space/400”），而不是类别。将多个简短、简单的查询放在一个 `queries` 调用中，而不是一个复合查询：

- **原始颜色**：“gray”、“red”、“blue”、“green”、“white”、“brand”
- **语义颜色**：“background”、“foreground”、“border”、“surface”、“text”
- **间距/尺寸**：“space”、“radius”、“gap”、“padding”

如果初始搜索返回空，请尝试更短的片段或不同的命名约定——库差异很大（“grey”与“gray”、“spacing”与“space”、“color/bg”与“background”）。

检查现有屏幕的绑定变量以获得最权威的结果：

```js
const frame = figma.currentPage.findOne(n => n.name === "Existing Screen");
const varMap = new Map();
frame.findAll(() => true).forEach(node => {
  const bv = node.boundVariables;
  if (!bv) return;
  for (const [prop, binding] of Object.entries(bv)) {
    const bindings = Array.isArray(binding) ? binding : [binding];
    for (const b of bindings) {
      if (b?.id && !varMap.has(b.id)) {
        const v = await figma.variables.getVariableByIdAsync(b.id);
        if (v) varMap.set(b.id, { name: v.name, id: v.id, key: v.key, type: v.resolvedType, remote: v.remote });
      }
    }
  }
});
return [...varMap.values()];
```

对于库变量（remote = true），通过键导入它们 `figma.variables.importVariableByKeyAsync(key)`。对于本地变量，直接使用 `figma.variables.getVariableByIdAsync(id)`。

有关绑定模式的详细信息，请参阅 [variable-patterns.md](../figma-use/references/variable-patterns.md)。

#### 2c：发现样式（文本样式、效果样式）

使用 `search_design_system` 并使用 `entity: "style"` 查询条目和术语（如“heading”、“body”、“shadow”、“elevation”）搜索样式。或者检查现有屏幕使用的内容：

```js
const frame = figma.currentPage.findOne(n => n.name === "Existing Screen");
const styles = { text: new Map(), effect: new Map() };
frame.findAll(() => true).forEach(node => {
  if ('textStyleId' in node && node.textStyleId) {
    const s = figma.getStyleById(node.textStyleId);
    if (s) styles.text.set(s.id, { name: s.name, id: s.id, key: s.key });
  }
  if ('effectStyleId' in node && node.effectStyleId) {
    const s = figma.getStyleById(node.effectStyleId);
    if (s) styles.effect.set(s.id, { name: s.name, id: s.id, key: s.key });
  }
});
return {
  textStyles: [...styles.text.values()],
  effectStyles: [...styles.effect.values()]
};
```

使用 `figma.importStyleByKeyAsync(key)` 导入库样式，然后使用 `node.textStyleId = style.id` 或 `node.effectStyleId = style.id` 应用它们。

有关详细信息，请参阅 [text-style-patterns.md](../figma-use/references/text-style-patterns.md) 和 [effect-style-patterns.md](../figma-use/references/effect-style-patterns.md)。

### 步骤 3：首先使用占位符创建包装框架

**必须使用 $fig** 使用 `$fig` 创建所有节点。有关 API 参考，请参阅 [fig-builder.md](../figma-use/references/fig-builder.md)。

**使用占位符，不要一次填充所有部分**——具有 `placeholder: true` 的新节点将在计划更改自动刷新后出现在工具调用结果中，例如 `{ created: { '0:3': 'My Screen', '0:4': 'Header Placeholder' }}`

```js
// --- 根据容器类型调整包装框架的大小 ---
// 全页：       { width: 1440, name: "Homepage" }
// 模态框/对话框：{ width: 640, name: "Settings Modal" }
// 抽屉/侧边栏：  { width: 360, name: "Navigation Drawer" }
// 面板：           { width: 400, name: "Details Panel" }
// 调整宽度以匹配源代码的实际尺寸。

$fig.autoLayout(
  {
    name: 'VIEW_NAME',
    layoutMode: 'VERTICAL',
    primaryAxisAlignItems: 'CENTER',
    counterAxisAlignItems: 'CENTER',
    width: WIDTH,
  },
  // 为屏幕创建占位符部分
  [
    $fig.autoLayout({ name: 'Header', layoutSizingHorizontal: 'FILL', placeholder: true }),
    $fig.autoLayout({ name: 'Content', layoutSizingHorizontal: 'FILL', placeholder: true }),
    $fig.autoLayout({ name: 'Footer', layoutSizingHorizontal: 'FILL', placeholder: true }),
  ]
)
```

### 步骤 4：在包装框架内构建每个部分

**这是最重要的步骤。** 一次构建一个部分，每个部分在自己的 `use_figma` 调用中。在每个脚本的开始处，通过 ID 获取部分占位符并将其替换为实际部分。

```js
const header = $fig.get("HEADER_PLACEHOLDER_ID_FROM_STEP_3");

// 通过键导入设计系统组件
const buttonSet = await figma.importComponentSetByKeyAsync("BUTTON_SET_KEY");
const primaryButton = buttonSet.children.find(c =>
  c.type === "COMPONENT" && c.name.includes("variant=primary")
) || buttonSet.defaultVariant;

// 导入设计系统变量以用于颜色和间距
const bgColorVar = await figma.variables.importVariableByKeyAsync("BG_COLOR_VAR_KEY");
const spacingVar = await figma.variables.importVariableByKeyAsync("SPACING_VAR_KEY");

const shadowStyle = await figma.importStyleByKeyAsync("SHADOW_STYLE_KEY");

// 使用变量绑定（而不是硬编码值）将占位符替换为具有实际部分的框架
header.replace(
  $fig.autoLayout(
    {
      name: 'Header',
      layoutSizingHorizontal: 'FILL', // 设置为 FILL，因为自动布局框架默认为 HUG
      paddingLeft: spacingVar,
      paddingRight: spacingVar,
      fills: [{ type: 'SOLID', color: bgColorVar }],
      effects: shadowStyle,
    },
    [
      $fig.instance(primaryButton)
    ]
  )
).screenshot()
```

在继续之前使用 `.screenshot()` 验证部分。仔细检查裁剪/裁切的文本（行高切断内容）和重叠的元素——这些是最常见的问题，一眼很难发现。

#### 使用 setProperties() 覆盖实例文本

组件实例自带占位符文本（"标题"、"标题"、"按钮"）。使用在第 2 步中发现的组件属性键通过 `setProperties()` 来覆盖它们——这比直接操作 `node.characters` 更可靠。有关完整模式，请参阅 [component-patterns.md](../figma-use/references/component-patterns.md#overriding-text-in-a-component-instance)。

对于嵌套实例，如果它们暴露了自己的 TEXT 属性，请在嵌套实例上调用 `setProperties()`：

```js
const nestedHeading = cardInstance.findOne(n => n.type === "INSTANCE" && n.name === "Text Heading");
if (nestedHeading) {
  nestedHeading.setProperties({ "Text#2104:5": "从源代码的实际标题" });
}
```

仅当文本不由任何组件属性管理时，才回退到直接 `node.characters`。

#### 仔细阅读源代码默认值

当将代码组件转换为 Figma 实例时，检查源代码中的组件默认属性值，而不仅仅是显式传递的内容。例如，`<Button size="small">Register</Button>` 没有变体属性——检查组件定义以找到 `variant = "primary"` 作为默认值。选择错误的变体（例如，中性而不是主要）会产生容易忽略的视觉错误结果。

#### 要手动构建的内容与从设计系统导入的内容

| 手动构建 | 从设计系统导入 |
|----------------|--------------------------|
| 包装框架 | **组件**：按钮、卡片、输入、导航等 |
| 区块容器框架 | **变量**：颜色（填充、描边）、间距（填充、间隙）、半径 |
| 布局网格（行、列） | **文本样式**：标题、正文、说明等 |
| | **效果样式**：阴影、模糊等 |

**当存在设计系统变量时，永远不要硬编码十六进制颜色或像素间距**。使用 `setBoundVariable` 用于间距/半径，使用 `setBoundVariableForPaint` 用于颜色。使用 `node.textStyleId` 应用文本样式，使用 `node.effectStyleId` 应用效果样式。

#### 图标：导入 SVG，永远不要从旋转的基元重新构建

图标是上述“手动构建与导入”区分的主要例外。如果设计系统将图标作为组件公开，请实例化它（通过 `$fig.instance(iconComponent)` 的单个 INSTANCE_SWAP 属性，而不是每个图标一个变体）。否则——最常见的情况是**从代码库中抓取图标以在 Figma 中放置或替换它**——直接导入图标的 **SVG 源** 作为矢量节点。这是图标的主要、默认路径；不要重新绘制它们。

1. **从代码库中获取 SVG**。读取图标的源——内联 `<svg>`、导入的 `.svg` 资产或图标库条目——并传递确切的 SVG 字符串。优先使用代码库自己的 SVG 而不是手动编写一个。
2. **使用 `$fig.svg(svgString, opts?)` 创建它**，这将解析 SVG 为矢量节点树。SVG 字符串**必须**包含 `viewBox` 以及显式的 `width`/`height`（例如 `<svg width="24" height="24" viewBox="0 0 24 24" ...>`）；没有它们，它会回退到 `viewBox` 大小，这通常比插槽小——这是“图标没有正确调整大小”的常见原因。（命令式 `figma.createNodeFromSvg(svgString)` 也有效，并返回一个可以 `.resize(size, size)` 的 `FrameNode`。）
3. **调整其大小以匹配插槽**。通过 SVG 字符串中的 `width`/`height` 匹配源的图标大小——通常为 16/20/24px。像其他计划节点一样追加它：作为父级的 `children` 的子节点，或 `slot.svg(svgString, opts)`。
4. **永远不要从旋转的线/矩形/椭圆基元重新构建图标**。在 `use_figma` 上下文中，Figma 的线旋转不可靠，会产生损坏的、旋转错误的图标（一个向下滑动变成一团模糊，箭头头与其杆分离）。导入 SVG 既是更可靠也是更可编辑的。

```js
// 将代码库图标 SVG 作为矢量导入，并调整到 24px 的插槽大小
const chevron = $fig.svg(
  '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">' +
  '<path d="m9 18 6-6-6-6" stroke="#1A1A1A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  { name: 'icon/chevron-right' }
);
// 在构建区块时作为子节点包含——例如 $fig.autoLayout({...}, [ label, chevron ])
// 或附加到现有的计划节点——例如 row.svg('<svg .../>', { name: 'icon/chevron-right' })
```

**代码库 SVG 通常使用 `currentColor`**（例如 `stroke="currentColor"` / `fill="currentColor"`），导入时为**黑色**——它不会继承父级的颜色。导入后设置预期颜色：在导入之前将字面颜色替换到 SVG 字符串中，或使用 `setBoundVariableForPaint` 将导入的矢量的填充/描边绑定到设计系统颜色变量（与任何油漆相同）。要将导入的 SVG 转换为可重用的图标组件（用于 INSTANCE_SWAP），请参阅 [figma-generate-library → 创建图标组件](../figma-generate-library/references/component-creation.md#creating-icon-components-for-instance_swap) 和 [INSTANCE_SWAP 模式](../figma-use/references/component-patterns.md#instance_swap-avoiding-variant-explosion)。

### 第 5 步：验证完整视图和传输图像

在组合所有区块后，在包装框架上调用 `get_screenshot` 并与源进行比较。修复任何通过目标 `use_figma` 调用出现的问题——不要重建整个视图。

**单独截图每个区块，而不仅仅是完整视图**。在降低分辨率时，完整视图截图会隐藏文本截断、错误颜色和尚未覆盖的占位符文本。通过节点 ID 截图每个区块以捕获：
- **裁剪/剪切的文本**——行高或框架尺寸截断了 descenders、ascenders 或整行
- **重叠内容**——由于错误的尺寸或缺少自动布局而堆叠的元素
- 仍然显示的占位符文本（"标题"、"标题"、"按钮"）
- 布局尺寸错误导致的截断内容
- 错误的组件变体（例如，中性按钮与主要按钮）
- **空白图像占位符**——如果图像丢失，您需要从 `generate_figma_design` 捕获中传输它们（见下文）

#### 从 generate_figma_design 捕获中传输图像

如果您并行运行了 `generate_figma_design`（当源包含图像时强制执行），请将捕获的图像传输到设计系统输出：

1. 通过搜索具有 `type === "IMAGE"` 的填充来查找捕获输出中的所有图像节点：
   ```js
   const capture = await figma.getNodeByIdAsync("CAPTURE_NODE_ID");
   const imageNodes = [];
   capture.findAll(n => {
     if (n.fills && Array.isArray(n.fills)) {
       for (const fill of n.fills) {
         if (fill.type === "IMAGE") {
           imageNodes.push({ name: n.name, id: n.id, imageHash: fill.imageHash });
           return true;
         }
       }
     }
     return false;
   });
   return imageNodes;
   ```
2. 将捕获的每个图像与您的 use_figma 输出中的相应框架匹配（通过位置、名称或顺序）。
3. 将图像哈希应用于目标框架：
   ```js
   targetFrame.fills = [{ type: "IMAGE", imageHash: "hash_from_capture", scaleMode: "FILL" }];
   ```
4. 在所有图像传输完成后删除 `generate_figma_design` 捕获输出。

### 第 6 步：更新现有视图

在更新而不是从头开始时：

1. 使用 `get_metadata` 检查现有屏幕结构。
2. 确定哪些区块需要更新，哪些可以保留。
3. 对于每个需要更改的区块：
   - 通过 ID 或名称定位现有节点
   - 如果设计系统组件已更改，则交换组件实例
   - 根据需要更新文本内容、变体属性或布局
   - 删除已弃用的区块
   - 添加新区块
4. 每次修改后使用 `get_screenshot` 进行验证。

```js
// 示例：在现有屏幕中交换按钮变体
const existingButton = await figma.getNodeByIdAsync("EXISTING_BUTTON_INSTANCE_ID");
if (existingButton && existingButton.type === "INSTANCE") {
  // 导入更新的组件
  const buttonSet = await figma.importComponentSetByKeyAsync("BUTTON_SET_KEY");
  const newVariant = buttonSet.children.find(c =>
    c.name.includes("variant=primary") && c.name.includes("size=lg")
  ) || buttonSet.defaultVariant;
  existingButton.swapComponent(newVariant);
}
return { success: true, mutatedNodeIds: [existingButton.id] };
```

## 参考文档

有关详细的 API 模式和注意事项，按需从 [figma-use](../figma-use/SKILL.md) 参考文档加载：

- [component-patterns.md](../figma-use/references/component-patterns.md) — 通过键导入、查找变体、setProperties、文本覆盖、使用实例
- [variable-patterns.md](../figma-use/references/variable-patterns.md) — 创建/绑定变量、导入库变量、作用域、别名、发现现有变量
- [text-style-patterns.md](../figma-use/references/text-style-patterns.md) — 创建/应用文本样式、导入库文本样式、类型坡道
- [effect-style-patterns.md](../figma-use/references/effect-style-patterns.md) — 创建/应用效果样式（阴影）、导入库效果样式
- [gotchas.md](../figma-use/references/gotchas.md) — 布局陷阱（HUG/FILL 交互、counterAxisAlignItems、尺寸顺序）、油漆/颜色问题、页面上下文重置

## 错误恢复

遵循 [figma-use](../figma-use/SKILL.md#6-error-recovery--self-correction) 中的错误恢复过程：

1. **停止**在错误上——不要立即重试。
2. **仔细阅读错误消息**以了解出了什么问题。
3. 如果错误不清楚，调用 `get_metadata` 或 `get_screenshot` 以检查当前文件状态。
4. **根据错误消息修复脚本**。
5. **重试**修正后的脚本——这是安全的，因为失败的脚本是不可变的（如果脚本出错，则不会创建任何内容）。

由于这项技能按增量工作（每个调用一个区块），错误自然限定于单个区块。先前成功的调用中的区块保持完整。

## 最佳实践

- **始终在构建前搜索**。设计系统可能已经有了您需要的组件、变量或样式。手动构建和硬编码值应该是例外，而不是规则。
- **广泛搜索**。尝试将同义词和部分术语作为 `{ entity, query }` 条目在一个 `queries` 调用中。一个 "NavigationPill" 可能会在 "pill"、"nav"、"tab" 或 "chip" 下找到，因此将它们作为组件条目传递。对于变量，使用 `entity: "variable"` 并使用 "color"、"spacing"、"radius" 等查询。
- **优先使用设计系统标记而不是硬编码值**。使用变量绑定用于颜色、间距和半径。使用文本样式用于排版。使用效果样式用于阴影。这使屏幕与设计系统保持链接。
- **优先使用组件实例而不是手动构建**。实例与源组件保持链接，并在设计系统演变时自动更新。
- **必须使用 $fig 创建所有节点**。不要使用 `figma.createFrame()`、`figma.createText()` 等。使用 `$fig.autoLayout()`、`$fig.text()`、`$fig.rectangle()` 等。
- **除非有充分的理由，否则始终使用自动布局**。自动布局是布局节点的最可靠方式。您不应使用自动布局的唯一原因是当您被要求不要使用它，或者如果周围内容不使用它。
- **按区块工作**。一次 `use_figma` 调用中不要构建超过一个主要区块。
- **每次区块后进行视觉验证**。在节点上调用 `.screenshot()` 以尽早捕获问题。
- **匹配现有约定**。如果文件中已经有关屏，请匹配它们的命名、尺寸和布局模式。
