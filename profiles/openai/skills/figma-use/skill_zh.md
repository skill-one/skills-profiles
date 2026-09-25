# use_figma — Figma 插件 API 技能

使用 `use_figma` MCP 通过插件 API 在 Figma 文件中执行 JavaScript。所有详细的参考文档都位于 `references/` 目录中。

**调用 `use_figma` 时始终传递 `skillNames: "figma-use"`。** 这是一个用于跟踪技能使用的日志参数——它不会影响执行。

**如果任务涉及从代码在 Figma 中构建或更新整个页面、屏幕或多部分布局，** 也加载 [figma-generate-design](../figma-generate-design/SKILL.md)。它提供了通过 `search_design_system` 发现设计系统组件、导入它们以及逐步组装屏幕的工作流程。这两种技能协同工作：这个用于 API 规则，那个用于屏幕构建工作流程。

在开始之前，加载 [plugin-api-standalone.index.md](references/plugin-api-standalone.index.md) 以了解可能实现的功能。当你被要求编写插件 API 代码时，使用这个上下文来搜索 [plugin-api-standalone.d.ts](references/plugin-api-standalone.d.ts) 中的相关类型、方法和属性。这是 API 表面的权威来源。它是一个大的 typings 文件，所以不要一次性加载它，按需搜索相关部分。

**重要提示：** 每次你使用设计系统时，从 [working-with-design-systems/wwds.md](references/working-with-design-systems/wwds.md) 开始了解与 Figma 中设计系统相关的基本概念、流程和指南。然后根据需要加载更具体的参考文档，用于组件、变量、文本样式和效果样式。

## 1. 关键规则

1.  **使用 `return` 发送数据。** 返回值会自动序列化为 JSON（对象、数组、字符串、数字）。**不要**调用 `figma.closePlugin()` 或将代码包装在异步 IIFE 中——这些都会为你处理。
2.  **使用普通的 JavaScript 并使用顶级 `await` 和 `return`。** 代码会自动包装在异步上下文中。**不要**将其包装在 `(async () => { ... })()` 中。
3.  `figma.notify()` **会抛出 "not implemented"** —— **永远不要**使用它
3a. `getPluginData()` / `setPluginData()` 在 `use_figma` 中**不受支持** —— **不要**使用它们。使用 `getSharedPluginData()` / `setSharedPluginData()` 代替（这些是受支持的），或者通过返回它们并将它们传递给后续调用来跟踪节点 ID。
4.  `console.log()` **不会返回** —— 使用 `return` 进行输出
5.  **逐步进行工作。** 将大型操作分解为多个 `use_figma` 调用。每一步后进行验证。这是避免错误的最重要实践。
6.  颜色是 **0–1 范围**（不是 0–255）：`{r: 1, g: 0, b: 0}` = 红色
7.  填充/描边是 **只读数组** —— 克隆、修改、重新分配
8.  字体**必须**在任何文本操作之前加载：`await figma.loadFontAsync({family, style})`
9.  **页面逐步加载** —— 使用 `await figma.setCurrentPageAsync(page)` 切换页面并加载其内容（见下文的页面规则）
10. `setBoundVariableForPaint` 返回一个**新的**填充——必须捕获并重新分配
11. `createVariable` 接受集合**对象或 ID 字符串**（对象优先）
12. **`layoutSizingHorizontal/Vertical = 'FILL'` 必须在 `parent.appendChild(child)` 之后设置** —— 在追加之前设置会抛出错误。对于非自动布局节点上的 `'HUG'` 也适用。
13. **将新的顶级节点定位到 (0,0) 之外。** 直接追加到页面上的节点默认为 (0,0)。扫描 `figma.currentPage.children` 找到一个清晰的位置（例如，在最右侧节点的右侧）。这仅适用于页面级节点——嵌套在其他框架或自动布局容器内的节点由其父节点定位。见 [Gotchas](references/gotchas.md)。
14. **在 `use_figma` 出错时，停止。** **不要**立即重试。失败的脚本**是原子性的**——如果脚本出错，它将不会执行，并且文件不会发生任何更改。仔细阅读错误消息，修复脚本，然后重试。见 [Error Recovery](#6-error-recovery--self-correction)。
15. **必须 `return` 所有创建/修改的节点 ID。** 每当脚本在画布上创建新节点或修改现有节点时，收集所有受影响的节点 ID 并以结构化对象返回它们（例如 `return { createdNodeIds: [...], mutatedNodeIds: [...] }`）。这对于后续调用参考、验证或清理这些节点至关重要。
16. **创建变量时始终显式设置 `variable.scopes`。** 默认的 `ALL_SCOPES` 会污染每个属性选择器——这几乎不是你想要的结果。使用特定的作用域，如 `["FRAME_FILL", "SHAPE_FILL"]` 用于背景，`["TEXT_FILL"]` 用于文本颜色，`["GAP"]` 用于间距等。见 [variable-patterns.md](references/variable-patterns.md) 获取完整列表。
17. **等待每个 Promise。** **不要**留下未等待的 Promise——未等待的异步调用（例如没有 `await` 的 `figma.loadFontAsync(...)`，或没有 `await` 的 `figma.setCurrentPageAsync(page)`）会触发并忘记，导致静默失败或竞争条件。脚本可能在异步操作完成之前返回，导致数据丢失或部分应用更改。

> 每条规则详细的错误/正确示例，见 [Gotchas & Common Mistakes](references/gotchas.md)。

## 2. 页面规则（关键）

**`use_figma` 调用之间页面上下文会重置**——每次 `figma.currentPage` 都会从第一个页面开始。

### 切换页面

使用 `await figma.setCurrentPageAsync(page)` 切换页面并加载其内容。同步设置器 `figma.currentPage = page` 在 `use_figma` 运行时**会抛出错误**。

```js
// 切换到特定页面（加载其内容）
const targetPage = figma.root.children.find((p) => p.name === "My Page");
await figma.setCurrentPageAsync(targetPage);
// targetPage.children 现在已填充

// 遍历所有页面
for (const page of figma.root.children) {
  await figma.setCurrentPageAsync(page);
  // page.children 现在已加载——在此处读取或修改它们
}
```

### 跨脚本运行

`figma.currentPage` 在每次 `use_figma` 调用的开始时重置为**第一个页面**。如果你的工作流程跨越多个调用并针对非默认页面，在每个调用开始时调用 `await figma.setCurrentPageAsync(page)`。

你可以多次调用 `use_figma` 以逐步构建文件状态，或在编写另一个脚本之前检索信息。例如，编写一个脚本获取现有节点的元数据，`return` 该数据，然后在后续脚本中使用它来修改这些节点。

## 3. `return` 是你的输出通道

代理**只看到**你 `return` 的值。其他所有内容都是不可见的。

- **返回 ID（关键）**：每个创建或修改画布节点的脚本**必须**返回所有受影响的节点 ID——例如 `return { createdNodeIds: [...], mutatedNodeIds: [...] }`。这是一个硬性要求，不是可选的。
- **进度报告**：`return { createdNodeIds: [...], count: 5, errors: [] }`
- **错误信息**：抛出的错误会自动捕获并返回——只需让它们传播或显式 `throw`。
- `console.log()` 输出**永远不会**返回给代理
- 始终返回可操作的输出数据（ID、计数、状态）以便后续调用可以参考创建的对象

## 4. 编辑器模式

`use_figma` 在**设计模式**（`editorType` 为 `"figma"`，默认模式）下工作。FigJam (`"figjam"`) 有不同的可用节点类型集——大多数设计节点在那里被阻塞。

设计模式下可用：矩形、框架、组件、文本、椭圆、星形、线条、矢量、多边形、布尔运算、切片、页面、部分、文本路径。

**被阻塞**在设计模式下：粘性、连接器、带文本的形状、代码块、幻灯片、幻灯片行、网页。

## 5. 逐步工作流程（如何避免错误）

最常见的错误原因是试图在单个 `use_figma` 调用中做太多事情。**逐步进行并每一步后进行验证。**

### 模式

1. **先检查。** 在创建任何内容之前，运行一个只读的 `use_figma` 来发现文件中已经存在的内容——页面、组件、变量、命名约定。匹配现有内容。
2. **每个调用做一件事。** 在一个调用中创建变量，在下一个调用中创建组件，在另一个调用中组合布局。不要试图在一个脚本中构建整个屏幕。
3. **每个调用返回 ID。** 始终 `return` 创建的节点 ID、变量 ID、集合 ID 作为对象（例如 `return { createdNodeIds: [...] }`）。你需要在后续调用中使用这些作为输入。
4. **每一步后验证。** 使用 `get_metadata` 验证结构（计数、名称、层次结构、位置）。使用 `get_screenshot` 在主要里程碑后捕获视觉问题。
5. **在继续之前修复。** 如果验证发现问题，在继续下一步之前修复它。不要在破损的基础上构建。

### 复杂任务的推荐步骤顺序

```
步骤 1：检查文件——发现现有页面、组件、变量、约定
步骤 2：创建标记/变量（如果需要）
       → 使用 get_metadata 验证
步骤 3：创建单个组件
       → 使用 get_metadata + get_screenshot 验证
步骤 4：从组件实例组合布局
       → 使用 get_screenshot 验证
步骤 5：最终验证
```

### 每一步需要验证的内容

| 在...之后 | 使用 `get_metadata` 验证 | 使用 `get_screenshot` 验证 |
|---|---|---|
| 创建变量 | 集合计数、变量计数、模式名称 | — |
| 创建组件 | 子节点计数、变体名称、属性定义 | 变体可见、未折叠、网格可读 |
| 绑定变量 | 节点属性反映绑定 | 颜色/标记正确解析 |
| 组合布局 | 实例节点有 mainComponent、层次结构正确 | 无裁剪/裁切的文本、无重叠元素、正确间距 |

## 6. 错误恢复与自我纠正

**`use_figma` 是原子性的**——失败的脚本不会执行。如果脚本出错，文件不会发生任何更改。文件保持调用前的状态。这意味着没有部分节点，没有来自失败脚本的孤儿元素，并且在修复后重试是安全的。

### 当 `use_figma` 返回错误时

1. **停止。** 不要立即修复代码并重试。
2. **仔细阅读错误消息。** 了解确切的问题——错误的 API 使用、缺失的字体、无效的属性值等。
3. **如果错误不明确**，调用 `get_metadata` 或 `get_screenshot` 以了解当前文件状态。
4. **根据错误消息修复脚本。**
5. **重试**修正后的脚本。

### 常见的自我纠正模式

| 错误消息 | 可能的原因 | 如何修复 |
|---|---|---|
| `"not implemented"` | 使用了 `figma.notify()` | 删除它——使用 `return` 进行输出 |
| `"node must be an auto-layout frame..."` | 在追加到自动布局父节点之前设置了 `FILL`/`HUG` | 将 `appendChild` 移动到 `layoutSizingX = 'FILL'` 之前 |
| `"Setting figma.currentPage is not supported"` | 使用了同步页面设置器 | 使用 `await figma.setCurrentPageAsync(page)` |
| 属性值超出范围 | 颜色通道 > 1（使用了 0–255 而不是 0–1） | 除以 255 |
| `"Cannot read properties of null"` | 节点不存在（错误的 ID、错误的页面） | 检查页面上下文，验证 ID |
| 脚本挂起/无响应 | 无限循环或未解决的 Promise | 检查 `while(true)` 或缺失 `await`；确保代码终止 |
| `"The node with id X does not exist"` | 父实例通过 `detachInstance()` 隐式分离，改变了 ID | 通过稳定（非实例）父框架遍历重新发现节点 |

### 当脚本成功但结果看起来错误时

1. 调用 `get_metadata` 检查结构正确性（层次结构、计数、位置）。
2. 调用 `get_screenshot` 检查视觉正确性。仔细查找裁剪/裁切的文本（行高切断内容）和重叠元素——这些是常见且容易忽略的问题。
3. 确定差异——是结构性的（错误的层次结构、缺失的节点）还是视觉的（错误的颜色、破损的布局、裁剪的内容）？
4. 编写一个有针对性的修复脚本，只修改损坏的部分——不要重新创建所有内容。

> 完整的验证工作流程，见 [Validation & Error Recovery](references/validation-and-recovery.md)。

## 7. 飞行前检查清单

在提交任何 `use_figma` 调用之前，验证：

- [ ] 代码使用 `return` 发送数据（不是 `figma.closePlugin()`）
- [ ] 代码**没有**包装在异步 IIFE 中（自动包装为你）
- [ ] `return` 值包含结构化数据，包含可操作信息（ID、计数）
- [ ] **没有**任何地方使用 `figma.notify()`
- [ ] **没有**作为输出使用 `console.log()`（使用 `return` 代替）
- [ ] 所有颜色使用 0–1 范围（不是 0–255）
- [ ] 填充/描边作为新数组重新分配（不在原地修改）
- [ ] 页面切换使用 `await figma.setCurrentPageAsync(page)`（同步设置器会抛出错误）
- [ ] `layoutSizingVertical/Horizontal = 'FILL'` 在 `parent.appendChild(child)` 之后设置
- [ ] 在任何文本属性更改之前调用 `loadFontAsync()`
- [ ] `lineHeight`/`letterSpacing` 使用 `{unit, value}` 格式（不是裸数字）
- [ ] 在设置尺寸模式之前调用 `resize()`（resize 会将它们重置为 FIXED）
- [ ] 对于多步骤工作流：前一个调用的 ID 作为字符串字面量传递（不是变量）
- [ ] 新顶级节点定位到 (0,0) 之外，以避免与现有内容重叠
- [ ] **所有**创建/修改的节点 ID 都被收集并包含在 `return` 值中
- [ ] 每个异步调用（`loadFontAsync`、`setCurrentPageAsync`、`importComponentByKeyAsync` 等）都被 `await`——没有触发并忘记的 Promise

## 8. 在创建前发现约定

**始终在创建任何内容之前检查 Figma 文件。** 不同的文件使用不同的命名约定、变量结构和组件模式。你的代码应该匹配现有内容，而不是强加新的约定。

当对任何约定（命名、作用域、结构）有任何疑问时，先检查 Figma 文件，然后是用户的代码库。只有在两者都不存在时，才回退到常见模式。

### 快速检查脚本

**列出所有页面和顶级节点：**
```js
const pages = figma.root.children.map(p => `${p.name} id=${p.id} children=${p.children.length}`);
return pages.join('\n');
```

**列出所有页面中的现有组件：**
```js
const results = [];
for (const page of figma.root.children) {
  await figma.setCurrentPageAsync(page);
  page.findAll(n => {
    if (n.type === 'COMPONENT' || n.type === 'COMPONENT_SET')
      results.push(`[${page.name}] ${n.name} (${n.type}) id=${n.id}`);
    return false;
  });
}
return results.join('\n');
```

**列出现有变量集合及其约定：**
```js
const collections = await figma.variables.getLocalVariableCollectionsAsync();
const results = collections.map(c => ({
  name: c.name, id: c.id,
  varCount: c.variableIds.length,
  modes: c.modes.map(m => m.name)
}));
return results;
```

## 9. 参考文档

根据你的任务需求按需加载这些文档：

| 文档 | 加载时机 | 涵盖内容 |
|-----|-------------|----------------|
| [gotchas.md](references/gotchas.md) | 任何 `use_figma` 之前 | 每个已知陷阱，包含错误/正确代码示例 |
| [common-patterns.md](references/common-patterns.md) | 需要工作代码示例 | 脚本框架：形状、文本、自动布局、变量、组件、多步骤工作流 |
| [plugin-api-patterns.md](references/plugin-api-patterns.md) | 创建/编辑节点 | 填充、描边、自动布局、效果、分组、克隆、样式 |
| [api-reference.md](references/api-reference.md) | 需要精确 API 表面 | 节点创建、变量 API、核心属性、什么可行和不可行 |
| [validation-and-recovery.md](references/validation-and-recovery.md) | 多步骤写入或错误恢复 | `get_metadata` vs `get_screenshot` 工作流程，强制错误恢复步骤 |
| [component-patterns.md](references/component-patterns.md) | 创建组件/变体 | combineAsVariants、组件属性、INSTANCE_SWAP、变体布局、发现现有组件、元数据遍历 |
| [variable-patterns.md](references/variable-patterns.md) | 创建/绑定变量 | 集合、模式、作用域、别名、绑定模式、发现现有变量 |
| [text-style-patterns.md](references/text-style-patterns.md) | 创建/应用文本样式 | 类型坡道、字体探测、列出样式、将样式应用于节点 |
| [effect-style-patterns.md](references/effect-style-patterns.md) | 创建/应用效果样式 | 阴影、列出样式、将样式应用于节点 |
| [plugin-api-standalone.index.md](references/plugin-api-standalone.index.md) | 需要理解完整的 API 表面 | 插件 API 中所有类型、方法和属性的索引 |
| [plugin-api-standalone.d.ts](references/plugin-api-standalone.d.ts) | 需要精确类型签名 | 完整的 typings 文件——按需搜索特定符号，不要一次性加载所有内容 |

## 10. 代码片段示例

你将在本文档的整个文档中看到代码片段。这些代码片段包含有用的插件 API 代码，可以重新使用。直接使用它们，或作为你进行过程中的起点。如果关键概念最好作为通用代码片段记录，请明确指出并写入磁盘，以便将来重用。
