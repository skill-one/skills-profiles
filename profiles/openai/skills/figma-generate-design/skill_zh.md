# 从设计系统构建/更新屏幕

使用此技能通过**重用已发布的设计系统**（组件、变量和样式）来在 Figma 中创建或更新全页屏幕，而不是使用硬编码值绘制基本元素。关键洞察：Figma 文件可能包含与代码库 UI 组件和令牌相对应的组件、颜色/间距变量和文本/效果样式等已发布的设计系统。找到并使用这些，而不是绘制带有十六进制颜色的框。

**强制要求**：在执行任何 `use_figma` 调用之前，您**必须**加载 `[figma-use](../figma-use/SKILL.md)`。该技能包含关键规则（颜色范围、字体加载等），这些规则适用于您编写的每个脚本。

**在调用 `use_figma` 作为此技能的一部分时，始终传递 `skillNames: "figma-generate-design"`。** 这是一个日志参数——它不会影响执行。

## 技能边界

- 当交付物是一个由设计系统组件实例组成的设计系统屏幕（新屏幕或更新屏幕）时，使用此技能。
- 如果用户想要从 Figma 设计生成代码，请切换到 [figma-implement-design](../figma-implement-design/SKILL.md)。
- 如果用户想要创建新的可重用组件或变体，请直接使用 [figma-use](../figma-use/SKILL.md)。
- 如果用户想要编写 **Code Connect 映射**，请切换到 [figma-code-connect-components](../figma-code-connect-components/SKILL.md)。

## 前置条件

- Figma MCP 服务器必须已连接
- 目标 Figma 文件必须包含已发布的设计系统（或可以访问团队库）
- 用户应提供：
  - 要在其中工作的 Figma 文件 URL / 文件密钥
  - 或关于要针对的文件的信息（代理可以发现页面）
- 要构建/更新的屏幕的源代码或描述

## 与 generate_figma_design（仅限 Web 应用）的并行工作流程

当从可以渲染在浏览器中的**Web 应用**构建屏幕时，同时运行这两种方法可以获得最佳结果：

1. **并行执行**：
   - 使用此技能的工作流程开始构建屏幕（use_figma + 设计系统组件）
   - 运行 `generate_figma_design` 以捕获正在运行的 Web 应用的像素级完美截图
2. **两者完成后**：更新 use_figma 输出以匹配 `generate_figma_design` 捕获的像素级布局。捕获提供了要瞄准的确切间距、尺寸和视觉效果，而您的 use_figma 输出具有链接到设计系统的正确组件实例。
3. **确认看起来良好后**：删除 `generate_figma_design` 输出——它仅用作视觉参考。

这结合了两者最好的方面：`generate_figma_design` 提供像素级布局精度，而 use_figma 提供保持链接和可更新的正确设计系统组件实例。

**此工作流程仅适用于** `generate_figma_design` 可以捕获运行页面的 Web 应用。对于非 Web 应用（iOS、Android 等）或更新现有屏幕，请使用标准工作流程。

## 必需工作流程

**按顺序遵循这些步骤。不要跳过步骤。**

### 第 1 步：理解屏幕

在触摸 Figma 之前，了解您正在构建的内容：

1. 如果从代码构建，请阅读相关的源文件以了解页面结构、部分以及使用的组件。
2. 确定屏幕的主要部分（例如，页眉、英雄、内容面板、定价网格、常见问题解答手风琴、页脚）。
3. 对于每个部分，列出涉及的 UI 组件（按钮、输入、卡片、导航药丸、手风琴等）。

### 第 2 步：发现设计系统——组件、变量和样式

您需要三个来自设计系统的东西：**组件**（按钮、卡片等）、**变量**（颜色、间距、半径）和**样式**（文本样式、阴影等效果样式）。当设计系统令牌存在时，不要硬编码十六进制颜色或像素值。

#### 2a：发现组件

**首选：首先检查现有屏幕。** 如果目标文件已经包含使用相同设计系统的屏幕，请跳过 `search_design_system` 并直接检查现有实例。一个 `use_figma` 调用，遍历现有框架的实例，为您提供精确的、权威的组件映射：

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

仅在文件没有现有屏幕可供参考时才回退到 `search_design_system`。在使用它时，**广泛搜索**——尝试多个术语和同义词（例如，“按钮”、“输入”、“导航”、“卡片”、“手风琴”、“页眉”、“页脚”、“标签”、“头像”、“切换”、“图标”等）。使用 `includeComponents: true` 以专注于组件。

**在您的映射中包含组件属性**——您需要知道每个组件暴露哪些 TEXT 属性以用于文本覆盖。创建一个临时实例，读取其 `componentProperties`（以及嵌套实例的属性），然后删除临时实例。

示例组件映射，包含属性信息：

```
组件映射：
- 按钮 → key: "abc123", type: 组件集
  属性: { "Label#2:0": 文本, "Has Icon#4:64": 布尔值 }
- PricingCard → key: "ghi789", type: 组件集
  属性: { "Device": 变体, "Variant": 变体 }
  嵌套 "Text Heading" 有: { "Text#2104:5": 文本 }
  嵌套 "Button" 有: { "Label#2:0": 文本 }
```

#### 2b：发现变量（颜色、间距、半径）

**首先检查现有屏幕**（与组件相同）。或者使用 `search_design_system` 并设置 `includeVariables: true`。

> **警告：两种不同的变量发现方法——不要混淆它们。**
>
> - `use_figma` 与 `figma.variables.getLocalVariableCollectionsAsync()` — 返回**当前文件中仅定义的本地变量**。如果此方法返回空，则**并不意味着没有变量存在**。远程/发布的库变量对此 API 不可见。
> - `search_design_system` 与 `includeVariables: true` — 搜索**所有链接的库**，包括远程和发布的库。这是发现设计系统变量的正确工具。
>
> **仅基于 `getLocalVariableCollectionsAsync()` 返回空就得出“没有变量存在”的结论是错误的。** 在决定创建自己的变量之前，始终运行 `search_design_system` 并设置 `includeVariables: true` 以检查库变量。

**查询策略**：`search_design_system` 匹配**变量名称**（例如，“Gray/gray-9”、“core/gray/100”、“space/400”），而不是类别。并行运行多个简短、简单的查询，而不是一个复合查询：

- **基本颜色**：“gray”、“red”、“blue”、“green”、“white”、“brand”
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

对于库变量（remote = true），使用 `figma.variables.importVariableByKeyAsync(key)` 导入它们。对于本地变量，直接使用 `figma.variables.getVariableByIdAsync(id)`。

有关绑定模式，请参阅 [variable-patterns.md](../figma-use/references/variable-patterns.md)。

#### 2c：发现样式（文本样式、效果样式）

使用 `search_design_system` 并设置 `includeStyles: true` 来搜索样式，并使用术语如“heading”、“body”、“shadow”、“elevation”。或者检查现有屏幕使用的内容：

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

使用 `figma.importStyleByKeyAsync(key)` 导入库样式，然后应用 `node.textStyleId = style.id` 或 `node.effectStyleId = style.id`。

有关详细信息，请参阅 [text-style-patterns.md](../figma-use/references/text-style-patterns.md) 和 [effect-style-patterns.md](../figma-use/references/effect-style-patterns.md)。

### 第 3 步：首先创建页面包装框架

**不要**将部分作为顶级页面子项构建并稍后重新父项——在 `use_figma` 调用之间移动节点（使用 `appendChild()`）会静默失败并产生孤立的框架。相反，首先创建包装器，然后直接在其内部构建每个部分。

在它自己的 `use_figma` 调用中创建页面包装器。将其定位到现有内容之外并返回其 ID：

```js
// 查找空白空间
let maxX = 0;
for (const child of figma.currentPage.children) {
  maxX = Math.max(maxX, child.x + child.width);
}

const wrapper = figma.createFrame();
wrapper.name = "Homepage";
wrapper.layoutMode = "VERTICAL";
wrapper.primaryAxisAlignItems = "CENTER";
wrapper.counterAxisAlignItems = "CENTER";
wrapper.resize(1440, 100);
wrapper.layoutSizingHorizontal = "FIXED";
wrapper.layoutSizingVertical = "HUG";
wrapper.x = maxX + 200;
wrapper.y = 0;

return { success: true, wrapperId: wrapper.id };
```

### 第 4 步：在包装器内构建每个部分

**这是最重要的步骤。** 一次构建一个部分，每个部分在自己的 `use_figma` 调用中。在每个脚本的开始处，通过 ID 获取包装器并直接将其内容附加到它。

```js
const createdNodeIds = [];
const wrapper = await figma.getNodeByIdAsync("WRAPPER_ID_FROM_STEP_3");

// 通过 key 导入设计系统组件
const buttonSet = await figma.importComponentSetByKeyAsync("BUTTON_SET_KEY");
const primaryButton = buttonSet.children.find(c =>
  c.type === "COMPONENT" && c.name.includes("variant=primary")
) || buttonSet.defaultVariant;

// 导入设计系统变量以用于颜色和间距
const bgColorVar = await figma.variables.importVariableByKeyAsync("BG_COLOR_VAR_KEY");
const spacingVar = await figma.variables.importVariableByKeyAsync("SPACING_VAR_KEY");

// 使用变量绑定构建部分框架（而不是硬编码值）
const section = figma.createFrame();
section.name = "Header";
section.layoutMode = "HORIZONTAL";
section.setBoundVariable("paddingLeft", spacingVar);
section.setBoundVariable("paddingRight", spacingVar);
const bgPaint = figma.variables.setBoundVariableForPaint(
  { type: 'SOLID', color: { r: 0, g: 0, b: 0 } }, 'color', bgColorVar
);
section.fills = [bgPaint];

// 导入并应用文本/效果样式
const shadowStyle = await figma.importStyleByKeyAsync("SHADOW_STYLE_KEY");
section.effectStyleId = shadowStyle.id;

// 在部分内创建组件实例
const btnInstance = primaryButton.createInstance();
section.appendChild(btnInstance);
createdNodeIds.push(btnInstance.id);

// 将部分附加到包装器
wrapper.appendChild(section);
section.layoutSizingHorizontal = "FILL"; // 在附加之后

createdNodeIds.push(section.id);
return { success: true, createdNodeIds };
```

构建每个部分后，在继续之前使用 `get_screenshot` 进行验证。仔细检查裁剪/裁切的文本（行高或框架尺寸切断 descenders、ascenders 或整行）和重叠的元素——这些是最常见的错误，在一眼看上去时很容易错过。

#### 使用 setProperties() 覆盖实例文本

组件实例带有占位符文本（“Title”、“Heading”、“Button”）。使用您在步骤 2 中发现的组件属性键使用 `setProperties()` 覆盖它们——这比直接 `node.characters` 操作更可靠。有关完整模式，请参阅 [component-patterns.md](../figma-use/references/component-patterns.md#overriding-text-in-a-component-instance)。

对于暴露自己 TEXT 属性的嵌套实例，请调用嵌套实例上的 `setProperties()`：

```js
const nestedHeading = cardInstance.findOne(n => n.type === "INSTANCE" && n.name === "Text Heading");
if (nestedHeading) {
  nestedHeading.setProperties({ "Text#2104:5": "实际来自源代码的标题" });
}
```

仅在不是由任何组件属性管理的文本情况下才回退到直接 `node.characters`。

#### 仔细阅读源代码默认值

当将代码组件转换为 Figma 实例时，请检查源代码中的组件默认属性值，而不仅仅是显式传递的内容。例如，`<Button size="small">Register</Button>` 没有变体属性——检查组件定义以找到 `variant = "primary"` 作为默认值。选择错误的变体（例如，中性而不是主要）会产生视觉上不正确的结果，很容易错过。

#### 要手动构建与从设计系统导入的内容

| 手动构建 | 从设计系统导入 |
|----------------|--------------------------|
| 页面包装框架 | **组件**：按钮、卡片、输入、导航等 |
| 部分容器框架 | **变量**：颜色（填充、描边）、间距（填充、间隙）、半径 |
| 布局网格（行、列） | **文本样式**：标题、正文、说明等 |
| | **效果样式**：阴影、模糊等 |

**当设计系统变量存在时，永远不要硬编码十六进制颜色或像素间距。** 使用 `setBoundVariable` 用于间距/半径，并使用 `setBoundVariableForPaint` 用于颜色。使用 `node.textStyleId` 应用文本样式，并使用 `node.effectStyleId` 应用效果样式。

### 第 5 步：验证完整屏幕

在组合所有部分后，对全页框架调用 `get_screenshot` 并与源进行比较。使用有针对性的 `use_figma` 调用修复任何问题——不要重新构建整个屏幕。

**逐个部分截图，而不仅仅是全页。** 在降低分辨率的全页截图会隐藏文本截断、错误颜色和尚未覆盖的占位符文本。通过节点 ID 对每个部分进行截图以捕获：
- **裁剪/裁切的文本**——行高或框架尺寸切断 descenders、ascenders 或整行
- **重叠的内容**——由于不正确的尺寸或缺少自动布局而堆叠的元素
- 仍然显示的占位符文本（“Title”、“Heading”、“Button”）
- 布局尺寸错误导致的截断内容
- 错误的组件变体（例如，中性按钮与主要按钮）

### 第 6 步：更新现有屏幕

在更新而不是从头开始时：

1. 使用 `get_metadata` 检查现有屏幕结构。
2. 确定哪些部分需要更新，哪些可以保留。
3. 对于需要更改的每个部分：
   - 通过 ID 或名称定位现有节点
   - 如果设计系统组件已更改，则交换组件实例
   - 根据需要更新文本内容、变体属性或布局
   - 删除已弃用的部分
   - 添加新部分
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

有关详细的 API 模式和注意事项，按需从 [figma-use](../figma-use/SKILL.md) 参考加载：

- [component-patterns.md](../figma-use/references/component-patterns.md) — 通过 key 导入、查找变体、setProperties、文本覆盖、使用实例
- [variable-patterns.md](../figma-use/references/variable-patterns.md) — 创建/绑定变量、导入库变量、范围、别名、发现现有变量
- [text-style-patterns.md](../figma-use/references/text-style-patterns.md) — 创建/应用文本样式、导入库文本样式、类型坡道
- [effect-style-patterns.md](../figma-use/references/effect-style-patterns.md) — 创建/应用效果样式（阴影）、导入库效果样式
- [gotchas.md](../figma-use/references/gotchas.md) — 布局陷阱（HUG/FILL 交互、counterAxisAlignItems、尺寸顺序）、颜色/填充问题、页面上下文重置

## 错误恢复

遵循从 [figma-use](../figma-use/SKILL.md#6-error-recovery--self-correction) 的错误恢复过程：

1. **停止**在错误上——不要立即重试。
2. **仔细阅读**错误消息以了解出了什么问题。
3. 如果错误不清楚，调用 `get_metadata` 或 `get_screenshot` 以检查当前文件状态。
4. **根据**错误消息修复脚本。
5. **重试**更正后的脚本——这是安全的，因为失败的脚本是不可变的（如果脚本出错，则不会创建任何内容）。

由于此技能按增量工作（每个部分调用一次），错误自然限制在单个部分内。来自成功调用的先前部分保持完整。

## 最佳实践

- **始终先搜索再构建。** 设计系统可能具有您需要的组件、变量或样式。手动构建和硬编码值应该是例外，而不是规则。
- **广泛搜索。** 尝试同义词和部分术语。一个 "NavigationPill" 可能是在 "pill"、"nav"、"tab" 或 "chip" 下找到的。对于变量，搜索 "color"、"spacing"、"radius" 等。
- **优先使用设计系统令牌而不是硬编码值。** 使用变量绑定用于颜色、间距和半径。使用文本样式用于排版。使用效果样式用于阴影。这使屏幕链接到设计系统。
- **优先使用组件实例而不是手动构建。** 实例保持链接到源组件，并在设计系统演变时自动更新。
- **按部分工作。** 每个调用中不要构建超过一个主要部分。
- **从每个调用中返回节点 ID。** 您将需要它们来组合部分和进行错误恢复。
- **在每次构建后进行视觉验证。** 使用 `get_screenshot` 捕获早期问题。
- **匹配现有约定。** 如果文件已经包含屏幕，请匹配它们的命名、尺寸和布局模式。
