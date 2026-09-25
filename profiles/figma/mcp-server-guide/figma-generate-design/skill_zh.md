# 从设计系统构建/更新屏幕和视图

使用此技能通过重用已发布的设计系统（组件、变量和样式）来创建或更新 Figma 中的屏幕、视图和多功能 UI 容器，而不是使用硬编码值绘制基元。这包括完整页面、模态框、对话框、抽屉、侧边栏、面板以及任何具有多个部分的组合视图。关键洞察：Figma 文件可能包含与代码库的 UI 组件和令牌相对应的已发布设计系统，包括组件、颜色/间距变量和文本/效果样式。找到并使用这些，而不是绘制带有十六进制颜色的框。

**强制要求**：在执行任何 `use_figma` 调用之前，您也必须加载 [figma-use](../figma-use/SKILL.md)。该技能包含适用于您编写的每个脚本的关键规则（颜色范围、字体加载等）。

**在调用 `use_figma` 作为此技能的一部分时，始终在逗号分隔的 `skillNames` 参数中包含 `figma-generate-design`。如果此技能通过 MCP 资源加载，则必须将名称前缀为 `resource:`（例如 `resource:figma-generate-design`）。** 这是一个日志参数——它不会影响执行。

## 技能边界

- 当交付物是**组合的 Figma 视图**（新创建或更新）——完整页面屏幕、模态框、对话框、抽屉、侧边栏、面板或任何多功能容器——并从设计系统组件实例构建时，使用此技能。
- 如果用户想要创建**新的可重用组件或变体**，请直接使用 [figma-use](../figma-use/SKILL.md)。
- 如果用户想要编写**Code Connect 映射**，请切换到 [figma-code-connect](../figma-code-connect/SKILL.md)。

## 前置条件

- Figma MCP 服务器必须已连接
- 目标 Figma 文件必须包含已发布的设计系统（或可以访问团队库）
- 用户必须提供一个目标 Figma 文件（URL 或 `fileKey`）。如果他们还没有，请先调用 `/figma-create-new-file`（或调用 `create_new_file`）并重用返回的 `file_key`。`use_figma` 和 `generate_figma_design` 都需要一个现有的 `fileKey`。
- 要构建/更新的屏幕/视图的源代码或描述

## 与 generate_figma_design 并行的流程（仅限 Web 应用）

当从可以渲染到浏览器中的**Web 应用**构建屏幕时，同时运行这两种方法可以获得最佳结果：

1. **并行执行**：
   - 使用此技能的工作流程（`use_figma` + 设计系统组件）针对目标 Figma 文件（`fileKey`）开始构建屏幕。
   - 针对**相同的 `fileKey`** 运行 `generate_figma_design` 以将运行中的 Web 应用的像素级完美截图捕获到该文件中。`generate_figma_design` 始终需要 `fileKey`——如果用户还没有 Figma 文件，请先调用 `/figma-create-new-file`（或调用 `create_new_file` MCP 工具）来获取一个，并重用该 `file_key` 用于此技能和捕获。
2. **两者完成后**：更新 `use_figma` 输出以匹配 `generate_figma_design` 捕获的像素级布局。捕获提供了要瞄准的确切间距、尺寸和视觉效果，而您的 `use_figma` 输出具有链接到设计系统的正确组件实例。如果捕获包含图像，请通过复制捕获的图像填充中的 `imageHash` 值将它们转移到您的 `use_figma` 输出中（有关详细信息，请参阅步骤 5）。
3. **确认看起来良好后**：删除 `generate_figma_design` 输出——它仅用作视觉参考。

这结合了两者中的最佳部分：`generate_figma_design` 提供像素级布局精度，而 `use_figma` 提供保持链接和可更新的正确设计系统组件实例。

**当源代码包含图像时，此并行工作流程是强制要求的**。`use_figma` 插件 API 无法获取外部图像 URL——它只能通过复制文件中已有的节点的 `imageHash` 值来设置图像填充。`generate_figma_design` 将所有可见图像矢量化到 Figma 中，为您提供所需的哈希值。如果您在图像存在时跳过捕获，图像框架将保持空白。

对于非 Web 应用（iOS、Android 等）或更新现有屏幕，请使用标准工作流程。

## 必需的工作流程

**按顺序执行以下步骤。不要跳过步骤。**

> **硬性限制——禁止的捷径**：
>
> - **禁止**：在完成 2a-i 并尝试或记录 N/A（例如“空文件，没有现有屏幕”）之前，使用 `search_design_system` 查找组件键。
> - **禁止**：任何在步骤 3+ 中修改画布的 `use_figma` 调用，直到清单下所有 2a 行都填写完毕。

### 步骤 1：理解交付物

在触摸 Figma 之前，了解您正在构建的内容：

1. 如果从代码构建，请阅读相关源文件以了解结构、部分以及使用的组件。
2. 确定视图的主要部分（例如，对于页面：页眉、英雄、内容面板、页脚；对于模态框：标题栏、表单部分、操作栏；对于侧边栏：导航、内容区域、页脚操作）。
3. 对于每个部分，列出涉及的 UI 组件（按钮、输入、卡片、导航药丸、手风琴等）。
4. **从源代码中识别产品的字体族。不要默认为 Inter。** 在编写任何脚本之前，找到产品使用的**具体字体**。有关查找位置（CSS 变量、组件文件）和如何解决混乱的 Figma 字体名称的信息，请参阅 [references/discover-product-font.md](references/discover-product-font.md)。
5. **检查视图是否包含任何图像**（例如，`<img>`、`<Image>`、背景图像、产品照片、头像、从 URL 加载的图标）。如果它是 Web 应用，并且包含图像，则您**必须**运行并行的 `generate_figma_design` 捕获工作流程——立即开始，以便捕获在您发现组件时运行。有关详细信息，请参阅上文的“与 generate_figma_design 并行的流程”。

### 步骤 2：收集组件键、变量和样式

您需要从设计系统中获取三个东西：**组件**（按钮、卡片等）、**变量**（颜色、间距、半径）和**样式**（文本样式、效果样式，如阴影）。当设计系统令牌存在时，不要硬编码十六进制颜色或像素值。

#### 2a：发现组件


**2a-i — 强制要求：检查 Code Connect 以获取所需的组件。** 从步骤 1 中构建的组件列表开始，检查每个组件是否在代码库中具有 Code Connect 文件。Code Connect 文件位于组件源代码旁边，并根据平台命名：

- **TypeScript/JS**：`*.figma.ts`、`*.figma.js`
- **React（基于解析器）**：`*.figma.tsx`
- **Kotlin/Compose**：包含 `@FigmaConnect` 的 `.kt` 文件
- **Swift**：包含 `FigmaConnect` 的 `.swift` 文件

对于每个您需要的组件（例如，Button、Card、Input），搜索其 Code Connect 文件——通过组件名称进行 glob 或 grep（例如，`**/Button.figma.tsx`、`**/Card.figma.ts`）。仅读取与您实际需要的组件匹配的文件。

从每个匹配的 Code Connect 文件中提取 Figma 组件 URL。解析 URL 中的 `fileKey` 和 `nodeId`（将连字符转换为冒号：`123-456` → `123:456`）。然后通过 `use_figma` 解析组件键：

**示例**：Code Connect 文件包含 `// url=https://figma.com/design/ABC123/File?node-id=609-35535`。解析 `fileKey` = `ABC123`，`nodeId` = `609:35535`。针对**库文件**（`fileKey` `ABC123`，而不是目标文件）运行 `use_figma` 以解析键：

```js
const node = await figma.getNodeByIdAsync("609:35535");
const set = node?.parent?.type === "COMPONENT_SET" ? node.parent : node;
return { componentKey: set.key };
```

批量查找多个，在单个调用中使用 `importComponentSetByKeyAsync()`（步骤 4）。

标记已解析的组件。如果所有组件都已解析，请跳过 2a-ii 和 2a-iii。如果所需组件都没有 Code Connect 文件，请继续进行 2a-ii。

**2a-ii — 如果仍有未解决的组件，则强制要求：检查现有屏幕。** 检查目标文件是否已经包含使用相同设计系统的屏幕。一个 `use_figma` 调用遍历现有框架的实例，为您提供精确且权威的组件映射：

```js
const frame = figma.currentPage.findOne(n => n.name === "Existing Screen");
const uniqueSets = new Map();
frame.findAllWithCriteria({ types: ["INSTANCE"] }).forEach(inst => {
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

将结果与未解决的组件进行匹配。标记任何新解析的组件。如果所有组件都已解析，请跳过 2a-iii。

**2a-iii — 最后手段：`search_design_system`。** 只有在完成 2a-i 和 2a-ii 后仍有组件未解决时，才使用 `search_design_system`。

在搜索之前，调用 `get_libraries` 以发现文件可用的库。这返回两个列表：已添加到文件的库和可添加的库（社区 UI 套件和组织库）。每个条目都包含一个 `libraryKey`，您可以通过 `includeLibraryKeys` 参数将搜索范围限定为特定库，而不是搜索所有内容。

```
// 步骤 1：发现可用的库
get_libraries({ fileKey })
// 返回：{
//   libraries_added_to_file: [...],
//   libraries_available_to_add: [...],
//   libraries_available_to_add_next_offset: number | null
// }

// 步骤 2：使用其 libraryKey 在特定库中搜索
search_design_system({ queries: [{ entity: "component", query: "button" }], fileKey, includeLibraryKeys: ["lk-abc123..."] })
```

组织库在 `libraries_available_to_add` 中是分页的（每页 20 个）。当 `libraries_available_to_add_next_offset` 为非空时，还有更多组织库——调用 `get_libraries` 并将 `offset` 设置为此值以获取下一页。社区 UI 套件仅出现在第一页。如果用户在当前页面上没有看到您命名的特定库，请继续翻页，然后再放弃。

这在文件包含许多库并且您想要有针对性的结果时特别有用（例如，仅在“iOS 26”或“Material 3”中搜索，而不是从每个库中获取匹配项）。

**广泛搜索，但每个查询一个意图**——`search_design_system` 不应用 OR 逻辑，因此永远不要将替代项或同义词组合到一个字符串中（“Button IconButton icon”匹配不到任何有用的内容）。将每个术语作为组件条目传递在单个 `queries` 调用中：`{ "entity": "component", "query": "..." }` 对象，永远不要只传递裸字符串：`{ "entity": "component", "query": "gray" }`，`{ "entity": "component", "query": "red" }` 等。
- **语义颜色**：`{ "entity": "variable", "query": "background" }`，`{ "entity": "variable", "query": "surface" }` 等。
- **间距/尺寸**：`{ "entity": "variable", "query": "space" }`，`{ "entity": "variable", "query": "radius" }` 等。

如果初始搜索返回空，请尝试更短的片段或不同的命名约定——库差异很大（“grey”与“gray”，“spacing”与“space”，“color/bg”与“background”）。

检查现有屏幕的绑定变量以获取最权威的结果：

```js
const frame = figma.currentPage.findOne(n => n.name === "Existing Screen");

// boundVariables 可以存在于任何场景节点上——枚举每个场景类型
// 只是用来喂 findAllWithCriteria，大致相当于 findAll(() => true)
// 并且在脚本输出中噪声更大。
const uniqueIds = new Set(
  frame.findAll(() => true).flatMap(n =>
    Object.values(n.boundVariables ?? {})
      .flatMap(b => Array.isArray(b) ? b : [b])
      .map(b => b?.id)
      .filter(Boolean)
  )
);
const variables = await Promise.all(
  [...uniqueIds].map(id => figma.variables.getVariableByIdAsync(id))
);
return variables
  .filter(Boolean)
  .map(v => ({ name: v.name, id: v.id, key: v.key, type: v.resolvedType, remote: v.remote }));
```

对于库变量（remote = true），使用 `figma.variables.importVariableByKeyAsync(key)` 导入它们。对于本地变量，直接使用 `figma.variables.getVariableByIdAsync(id)` 导入。

有关绑定模式，请参阅 [variable-patterns.md](../figma-use/references/variable-patterns.md)。

#### 2b：发现样式（文本样式、效果样式）

使用 `search_design_system` 并使用 `entity: "style"` 查询条目和术语（如“heading”、“body”、“shadow”、“elevation”）搜索样式。或者检查现有屏幕使用的内容：

```js
const frame = figma.currentPage.findOne(n => n.name === "Existing Screen");
const styles = { text: new Map(), effect: new Map() };

for (const node of frame.findAll(() => true)) {
  // textStyleId 是在 TEXT 和 TEXT_PATH 上；effectStyleId 是在大多数场景
  // 形状/容器类型上。使用 `in` 保护的语句来处理两者，而无需 exhaustive 类型列表。
  if ('textStyleId' in node && node.textStyleId) {
    const s = figma.getStyleById(node.textStyleId);
    if (s) styles.text.set(s.id, { name: s.name, id: s.id, key: s.key });
  }
  if ('effectStyleId' in node && node.effectStyleId) {
    const s = figma.getStyleById(node.effectStyleId);
    if (s) styles.effect.set(s.id, { name: s.name, id: s.id, key: s.key });
  }
}

return {
  textStyles: [...styles.text.values()],
  effectStyles: [...styles.effect.values()]
};
```

使用 `figma.importStyleByKeyAsync(key)` 导入库样式，然后使用 `node.textStyleId = style.id` 或 `node.effectStyleId = style.id` 应用它们。

有关详细信息，请参阅 [text-style-patterns.md](../figma-use/references/text-style-patterns.md) 和 [effect-style-patterns.md](../figma-use/references/effect-style-patterns.md)。

### 步骤 3：首先创建包装框架

**不要**将部分作为顶级页面子元素构建并重新父级它们——在 `use_figma` 调用中使用 `appendChild()` 移动节点会静默失败并产生孤立的框架。相反，首先创建包装框架，然后直接在其内部构建每个部分。

在它自己的 `use_figma` 调用中创建包装框架。将其定位到现有内容之外并返回其 ID：

```js
// 找到空白空间
let maxX = 0;
for (const child of figma.currentPage.children) {
  maxX = Math.max(maxX, child.x + child.width);
}

const wrapper = figma.createAutoLayout("VERTICAL");

// --- 根据容器类型调整包装框架的大小 ---
// 完整页面：       wrapper.resize(1440, 100); wrapper.name = "Homepage";
// 模态框/对话框：    wrapper.resize(640, 100);  wrapper.name = "Settings Modal";
// 抽屉/侧边栏：  wrapper.resize(360, 100);  wrapper.name = "Navigation Drawer";
// 面板：           wrapper.resize(400, 100);  wrapper.name = "Details Panel";
// 调整宽度以匹配源代码的实际尺寸。

wrapper.name = "VIEW_NAME";
wrapper.primaryAxisAlignItems = "CENTER";
wrapper.counterAxisAlignItems = "CENTER";
wrapper.resize(WIDTH, 100);
wrapper.layoutSizingHorizontal = "FIXED";
wrapper.x = maxX + 200;
wrapper.y = 0;

return { success: true, wrapperId: wrapper.id };
```

### 步骤 4：在包装框架内构建部分

**这是最重要的步骤。** 以安全的构建阶段进行构建：相关的部分可能共享一个 `use_figma` 调用，当生成的脚本可以安全重试时。仅在需要跨越页面上下文、部分执行将难以恢复或实际失败需要针对性重试时拆分阶段——不要仅仅为了创建验证检查而拆分。在脚本的开始处，通过 ID 获取包装框架并直接将其内容附加到它。

```js
const createdNodeIds = [];

// 并行解析包装框架并导入每个设计系统依赖项。
// 此处使用顺序等待将每个部分构建中的 N 个独立 IPC 轮次序列化到每个节点的顶部——这大大加快了速度。
const [wrapper, buttonSet, bgColorVar, spacingVar, shadowStyle] = await Promise.all([
  figma.getNodeByIdAsync("WRAPPER_ID_FROM_STEP_3"),
  figma.importComponentSetByKeyAsync("BUTTON_SET_KEY"),
  figma.variables.importVariableByKeyAsync("BG_COLOR_VAR_KEY"),
  figma.variables.importVariableByKeyAsync("SPACING_VAR_KEY"),
  figma.importStyleByKeyAsync("SHADOW_STYLE_KEY"),
]);
const primaryButton = buttonSet.children.find(c =>
  c.type === "COMPONENT" && c.name.includes("variant=primary")
) || buttonSet.defaultVariant;

// 构建具有变量绑定（而不是硬编码值）的部分框架
const section = figma.createAutoLayout();
section.name = "Header";
section.setBoundVariable("paddingLeft", spacingVar);
section.setBoundVariable("paddingRight", spacingVar);
const bgPaint = figma.variables.setBoundVariableForPaint(
  { type: 'SOLID', color: { r: 0, g: 0, b: 0 } }, 'color', bgColorVar
);
section.fills = [bgPaint];

// 应用上面导入的效果样式
section.effectStyleId = shadowStyle.id;

// 在部分内创建组件实例
const btnInstance = primaryButton.createInstance();
section.appendChild(btnInstance);
createdNodeIds.push(btnInstance.id);

// 将部分附加到包装框架
wrapper.appendChild(section);
section.layoutSizingHorizontal = "FILL"; // AFTER appending

createdNodeIds.push(section.id);
return { success: true, createdNodeIds };
```

从每个调用返回创建的节点 ID 以及相关的计数、名称和边界，这是您的默认结构验证。运行单独的结构读取，仅当缺少证据或相关突变使其失效时才运行。保存视觉检查用于步骤 5。

#### 使用 setProperties() 覆盖实例文本

组件实例带有占位符文本（“Title”、“Heading”、“Button”）。使用您在步骤 2 中发现的组件属性键使用 `setProperties()` 覆盖它们——这比直接 `node.characters` 操作更可靠。有关完整模式，请参阅 [component-patterns.md](../figma-use/references/component-patterns.md#overriding-text-in-a-component-instance)。

对于嵌套实例，如果它们暴露自己的 TEXT 属性，请在嵌套实例上调用 `setProperties()`：

```js
// 使用类型索引标准进行类型过滤，然后通过名称缩小范围。
const nestedHeading = cardInstance
  .findAllWithCriteria({ types: ["INSTANCE"] })
  .find(n => n.name === "Text Heading");
if (nestedHeading) {
  nestedHeading.setProperties({ "Text#2104:5": "Actual heading from source code" });
}
```

仅在不是由任何组件属性管理的文本上才回退到直接 `node.characters`。

#### 小心读取源代码默认值

当将代码组件翻译为 Figma 实例时，请检查源代码中的组件默认属性，而不仅仅是显式传递的内容。例如，`<Button size="small">Register</Button>` 没有变体属性——检查组件定义以找到 `variant = "primary"` 作为默认值。选择错误的变体（例如，Neutral 而不是 Primary 按钮）会产生视觉上不正确的结果，很容易被忽略。

#### 手动构建与从设计系统导入的区别

| 手动构建 | 从设计系统导入 |
|----------|----------------|
| 包装框架 | **组件**：按钮、卡片、输入、导航等 |
| 部分容器框架 | **变量**：颜色（填充、描边）、间距（填充、间隙）、半径 |
| 布局网格（行、列） | **文本样式**：标题、正文、副标题等 |
|          | **效果样式**：阴影、模糊等 |

**永远不要硬编码十六进制颜色或像素间距**，当存在设计系统变量时。使用 `setBoundVariable` for 间距/半径，使用 `setBoundVariableForPaint` for 颜色。使用 `node.textStyleId` 应用文本样式，使用 `node.effectStyleId` 应用效果样式。

**默认情况下优先考虑组件化。** 构建重复或可重用元素为组件一次，然后放置实例。不要发送一个扁平的、一次性框架树，需要第二个“使其组件化”步骤。

- **设计系统实例已经是组件化的**（步骤 2）。优先使用它们。
- **对于设计系统不涵盖的任何重复或映射到可重用源组件的内容，请使用 `figma.createComponent()` 创建本地组件一次，然后放置实例，而不是手动构建 N 个几乎相同的框架。一个源组件映射到一个 Figma 主组件。**

有关构建一次、放置实例模式的详细信息，请参阅 [references/componentization.md](references/componentization.md) 和代码。

#### 图标：导入 SVG，永远不要从旋转的基元重新构建

图标是上述手动构建与导入区分的主要例外。如果设计系统将图标作为组件公开，则实例化它（单个 INSTANCE_SWAP 属性，而不是每个图标一个变体）。否则——最常见的情况是**从代码库中抓取图标以将其放置或替换到 Figma 中**——直接导入图标的 **SVG 源** 作为矢量节点。这是图标的**主要、默认路径**；不要重新绘制它们。

1. **从代码库中获取 SVG。** 读取图标的源——内联 `<svg>`、导入的 `.svg` 资产或图标库条目——并传递确切的 SVG 字符串。优先使用代码库自己的 SVG 考虑到手动编写一个。

2. **使用 `figma.createNodeFromSvg(svgString)` 导入**，这将返回一个 `FrameNode`，其中包含可编辑的矢量路径。SVG 字符串**必须**包括 `viewBox` 以及显式的 `width`/`height`（例如 `<svg width="24" height="24" viewBox="0 0 24 24" ...>`）。没有 `width`/`height`，它将回退到 `viewBox` 大小，这通常比插槽小——这是“图标没有正确调整大小”的常见原因。

3. **调整大小以匹配插槽。** `createNodeFromSvg` 框架在调整大小时缩放其内容，所以 `icon.resize(size, size)` 将整个图标（包括描边权重）调整到目标框。或者等价地指定 `width`/`height` 等于目标。匹配源代码的图标大小——通常为 16/20/24px。

4. **永远不要从旋转的线/矩形/椭圆基元重新构建图标。** 在 `use_figma` 上下文中，Figma 的线旋转不可靠，并且会产生损坏的、旋转错误的图标（一个箭头头会塌缩成一个blob，箭头头会与杆分离）。导入 SVG 既是更可靠的方法，也是可编辑的。

```js
// 将图标从代码库 SVG 放置/替换到 24px 插槽中
const icon = figma.createNodeFromSvg(
  '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">' +
  '<path d="m9 18 6-6-6" stroke="#1A1A1A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
);
icon.name = "icon/chevron-right";
icon.resize(24, 24);          // 将整个图标缩放到插槽
slotFrame.appendChild(icon);
```

**代码库 SVG 通常使用 `currentColor**`（例如 `stroke="currentColor"` / `fill="currentColor"`），`createNodeFromSvg` 导入为**黑色**——它不会继承父级的颜色。导入后设置预期颜色：在导入的 SVG 字符串中替换字面量颜色，或使用 `setBoundVariableForPaint` 将导入的矢量填充/描边绑定到设计系统颜色变量（与任何油漆相同）。将导入的 SVG 转换为可重用图标组件（用于 INSTANCE_SWAP），请参阅 [figma-generate-library → Creating Icon Components](../figma-generate-library/references/component-creation.md) 和 [INSTANCE_SWAP 模式](../figma-use/references/component-patterns.md#instance_swap-avoiding-variant-explosion)。

## 错误恢复

遵循 [figma-use 错误恢复](../figma-use/SKILL.md#7-error-recovery--self-correction):

- 如果 `safeToRetryWithoutCanvasRead` 为 `true`，则修复错误并重试。
- 如果为 `false`，则读取画布，确定发生了什么变化，然后进行更改。

由于此技能在安全的构建阶段工作，错误自然地限定于当前阶段。来自先前成功调用的内容保持完整。

## 最佳实践

- **始终在构建之前搜索。** 设计系统可能具有您需要的组件、变量或样式。手动构建和硬编码值应该是例外，而不是规则。
- **广泛搜索，每个查询一个意图。** 尝试同义词和部分术语作为单独的 `{ entity, query }` 条目在一个 `queries` 调用中，永远不要将替代项或同义词组合到一个字符串中——一个“NavigationPill”可能以“pill”、“nav”、“tab”或“chip”的形式找到，所以传递四个组件条目。对于变量，使用 `entity: "variable"` 并使用查询，如 "color"、"spacing"、"radius" 等。
- **优先使用设计系统令牌而不是硬编码值。** 使用变量绑定 for 颜色、间距和半径。使用文本样式 for 字体。使用效果样式 for 阴影。这使屏幕链接到设计系统。
- **优先使用组件实例而不是手动构建。** 实例保持链接到源组件并随着设计系统的演变自动更新。
- **默认情况下进行组件化。** 构建重复或可重用元素为组件一次，然后放置实例。不要发送一个扁平的、一次性框架树，需要第二个“使其组件化”步骤。
- **在安全的构建阶段工作。** 将相关的部分批量到单个 `use_figma` 调用中，当脚本保持安全重试时，这样可以安全地重试；仅在页面上下文边界、难以恢复的突变或实际失败需要针对性重试时拆分。
