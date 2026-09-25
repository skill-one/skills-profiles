# 设计系统构建器 — Figma MCP 技能

在 Figma 中构建与代码匹配的专业级设计系统。此技能协调跨越 20–100+ `use_figma` 调用的多阶段工作流，从现实世界的设计系统（Material 3、Polaris、Figma UI3、Simple DS）中强制执行质量模式。

**前提条件**：每个 `use_figma` 调用都必须加载 `figma-use` 技能。它提供插件 API 语法规则（返回模式、页面重置、ID 返回、字体加载、颜色范围）。此技能提供设计系统领域知识和工作流协调。

**始终在调用 `use_figma` 作为此技能的一部分时传递 `skillNames: "figma-generate-library"`。** 这是一个日志参数——它不会影响执行。

---

## 1. 最重要的规则

**这绝对不是一次性任务。** 构建设计系统需要跨越多个阶段，进行 20–100+ `use_figma` 调用，并且在这些阶段之间有强制性的用户检查点。任何试图在一个调用中创建所有内容的尝试都将产生损坏、不完整或无法恢复的结果。将每个操作分解到最小的有用单元，进行验证，获取反馈，然后继续。

---

## 2. 强制性工作流

每个设计系统构建都遵循此阶段顺序。跳过或重新排序阶段会导致结构性的失败，而撤销这些失败的成本很高。

```
阶段 0：发现（始终为第一个阶段——尚未进行任何 `use_figma` 写入）
  0a. 分析代码库 → 提取令牌、组件、命名约定
  0b. 检查 Figma 文件 → 页面、变量、组件、样式、现有约定
  0c. 搜索订阅的库 → 使用 search_design_system 搜索可重用资源
  0d. 锁定 v1 范围 → 在任何创建之前就同意确切的令牌集 + 组件列表
  0e. 映射代码 → Figma → 解决冲突（代码和 Figma 不一致 = 询问用户）
  ✋ 用户检查点：展示完整计划，等待明确批准

阶段 1：基础（令牌优先——始终在组件之前）
  1a. 创建变量集合和模式
  1b. 创建原始变量（原始值、1 个模式）
  1c. 创建语义变量（别名指向原始变量、模式感知）
  1d. 为所有变量设置作用域
  1e. 为所有变量设置代码语法
  1f. 创建效果样式（阴影）和文本样式（排版）
  → 退出标准：已商定的计划中的每个令牌都存在，所有作用域已设置，所有代码语法已设置
  ✋ 用户检查点：显示变量摘要，等待批准

阶段 2：文件结构（在组件之前）
  2a. 创建页面骨架：封面 → 入门指南 → 基础 → --- → 组件 → --- → 工具
  2b. 创建基础文档页面（色板、类型样本、间距条）
  → 退出标准：所有计划的页面都存在，基础文档可导航
  ✋ 用户检查点：显示页面列表 + 截图，等待批准

阶段 3：组件（一次一个——绝不批量）
  对于每个组件（按依赖顺序：原子在分子之前）：
    3a. 创建专用页面
    3b. 使用自动布局 + 完整变量绑定构建基础组件
    3c. 创建所有变体组合（combineAsVariants + 网格布局）
    3d. 添加组件属性（TEXT、BOOLEAN、INSTANCE_SWAP）
    3e. 将属性链接到子节点
    3f. 添加页面文档（标题、描述、使用说明）
    3g. 验证：get_metadata（结构）+ get_screenshot（视觉）
    3h. 可选：在上下文仍然新鲜时进行轻量级的 Code Connect 映射
    → 退出标准：变体数量正确，所有绑定已验证，截图看起来正确
    ✋ 用户检查点：每个组件：显示截图，等待批准后再创建下一个组件

阶段 4：集成 + QA（最终检查）
  4a. 完成所有 Code Connect 映射
  4b. 无障碍性审计（对比度、最小触摸目标、焦点可见性）
  4c. 命名审计（无重复、无未命名的节点、一致的格式）
  4d. 未解决绑定审计（无硬编码的填充/描边剩余）
  4e. 每个页面的最终审查截图
  ✋ 用户检查点：完成最终批准
```

---

## 3. 关键规则

**插件 API 基础**（来自 use_figma 技能——在此处也强制执行）：
- 使用 `return` 发送数据（自动序列化）。不要用 IIFE 包裹或调用 closePlugin。
- 在每个返回值中返回所有创建/修改的节点 ID
- 页面上下文每次调用都会重置——始终在开始时 `await figma.setCurrentPageAsync(page)`
- `figma.notify()` 会抛出异常——永远不要使用它
- 颜色是 0–1 范围，不是 0–255
- 字体必须在任何文本写入之前加载：`await figma.loadFontAsync({family, style})`

**设计系统规则**：
1. **变量在组件之前** — 组件绑定到变量。没有令牌 = 没有组件。
2. **创建前检查** — 运行只读 `use_figma` 发现现有约定。匹配它们。
3. **每个组件一个页面** *(默认)* — 例外：紧密相关的系列（例如，Input + 辅助功能）可以共享一个页面，并有清晰的区域分隔。
4. **将视觉属性绑定到变量** *(默认)* — 填充、描边、填充、半径、间隙。例外：有意固定的几何形状（图标像素网格大小、静态分隔符）。
5. **每个变量都有作用域** — 永远不要设置为 `ALL_SCOPES`。背景：`FRAME_FILL, SHAPE_FILL`。文本：`TEXT_FILL`。边框：`STROKE_COLOR`。间距：`GAP`。半径：`CORNER_RADIUS`。原始值：`[]`（隐藏）。
6. **每个变量都有代码语法** — WEB 语法必须使用 `var()` 包装器：`var(--color-bg-primary)`，而不是 `--color-bg-primary`。使用代码库中的实际 CSS 变量名称。ANDROID/iOS 不使用包装器。
7. **将语义别名到原始值** — `{ type: 'VARIABLE_ALIAS', id: primitiveVar.id }`。在语义层中永远不要复制原始值。
8. **在 combineAsVariants 之后定位变体** — 它们堆叠在 (0,0)。手动网格布局 + 调整大小。
9. **图标使用 INSTANCE_SWAP** — 永远不要为每个图标创建一个变体。限制变体矩阵：如果 Size × Style × State > 30 组合，则拆分为子组件。
10. **确定性命名** — 使用一致且唯一的节点名称，以便进行幂等的清理和可恢复性。通过返回值和状态账本跟踪创建的节点 ID。
11. **无破坏性清理** — 清理脚本通过命名约定或返回的 ID 识别节点，而不是猜测。
12. **在继续之前验证** — 永远不要在未验证的工作上构建。`get_metadata` 在每次创建后，`get_screenshot` 在每个组件后。
13. **永远不要并行化 `use_figma` 调用** — Figma 状态突变必须是严格顺序的。即使您的工具支持并行调用，也永远不要同时运行两个 use_figma 调用。
14. **永远不要臆测 Node IDs** — 始终从先前调用的返回状态账本中读取 ID。永远不要从内存中重建或臆测 ID。
15. **使用辅助脚本** — 将 `scripts/` 中的脚本嵌入到您的 use_figma 调用中。不要从头开始编写 200 行的 inline 脚本。
16. **明确的阶段批准** — 在每个检查点，明确指定下一个阶段。如果关于阶段 1 询问了“看起来不错”，则不要在没有完成阶段 0-2 的情况下开始阶段 3。

---

## 4. 状态管理（长工作流的必需项）

> **`getPluginData()` / `setPluginData()` 在 `use_figma` 中不受支持。** 使用 `getSharedPluginData()` / `setSharedPluginData()`（这些是受支持的），或使用基于名称的查找和状态账本（返回的 ID）。

| 实体类型 | 幂等性键 | 如何检查存在性 |
|-------------|----------------|----------------------|
| 场景节点（页面、框架、组件） | `setSharedPluginData('dsb', 'key', value)` 或唯一名称 | `node.getSharedPluginData('dsb', 'key')` 或 `page.findOne(n => n.name === 'Button')` |
| 变量 | 集合内的名称 | `(await figma.variables.getLocalVariablesAsync()).find(v => v.name === name && v.variableCollectionId === collId)` |
| 样式 | 名称 | `getLocalTextStyles().find(s => s.name === name)` |

立即在创建后标记每个**场景节点**：
```javascript
node.setSharedPluginData('dsb', 'run_id', RUN_ID);        // 识别此构建运行
node.setSharedPluginData('dsb', 'phase', 'phase3');        // 哪个阶段创建的它
node.setSharedPluginData('dsb', 'key', 'component/button');// 唯一的逻辑键
```

**状态持久化**：不要仅依赖对话上下文来记录状态账本。将其写入磁盘：
```
/tmp/dsb-state-{RUN_ID}.json
```
在每次轮次的开始时重新读取此文件。在长工作流中，对话上下文将被截断——文件是事实来源。

维护一个状态账本跟踪：
```json
{
  "runId": "ds-build-2024-001",
  "phase": "phase3",
  "step": "component-button",
  "entities": {
    "collections": { "primitives": "id:...", "color": "id:..." },
    "variables": { "color/bg/primary": "id:...", "spacing/sm": "id:..." },
    "pages": { "Cover": "id:...", "Button": "id:..." },
    "components": { "Button": "id:..." }
  },
  "pendingValidations": ["Button:screenshot"],
  "completedSteps": ["phase0", "phase1", "phase2", "component-avatar"]
}
```

**幂等性检查**：在每次创建之前查询名称 + 状态账本 ID。如果存在，则跳过或更新——永远不要重复。

**恢复协议**：在会话开始时或在上下文截断后，运行只读 `use_figma` 扫描所有页面、组件、变量和样式以按名称重建 `{key → id}` 映射。然后如果可用，从磁盘重新读取状态文件。

**继续提示**（在新的聊天中恢复时提供给用户）：
> "我正在继续设计系统的构建。运行 ID: {RUN_ID}。加载 figma-generate-library 技能并从上次完成的步骤继续。"

---

## 5. search_design_system — 重用决策矩阵

在阶段 0 中首先搜索，然后在每个组件创建前立即再次搜索。

```
search_design_system({ query, fileKey, includeComponents: true, includeVariables: true, includeStyles: true })
```

**如果**所有这些都为真，则重用：
- 组件属性 API 符合您的需求（相同的变体轴，兼容的类型）
- 令牌绑定模型兼容（使用相同的或可别名的变量）
- 命名约定与目标文件匹配
- 组件可编辑（不在您不拥有的远程库中锁定）

**如果**任何这些不满足：
- API 不兼容（不同的属性名称，错误的变体模型）
- 令牌模型不兼容（硬编码值，不同的变量架构）
- 所有权问题（无法修改库）

**如果**视觉匹配但 API 不兼容：
- 将库组件作为嵌套实例导入到新的包装组件中
- 在包装器上暴露干净的 API

**三向优先级**：本地现有 → 订阅库导入 → 创建新。

---

## 6. 用户检查点

强制性的。设计决策需要人工判断。

| 之后 | 必要的工件 | 询问 |
|-------|-------------------|-----|
| 发现 + 范围锁定 | 令牌列表、组件列表、差距分析 | "这是我的计划。在创建任何内容之前批准吗？" |
| 基础 | 变量摘要（N 个集合、M 个变量、K 个模式）、样式列表 | "所有令牌已创建。在文件结构之前进行审查吗？" |
| 文件结构 | 页面列表 + 截图 | "页面设置完毕。在组件之前进行审查吗？" |
| 每个组件 | get_screenshot of component page | "这是 [Component] 与 N 个变体。正确吗？" |
| 每个冲突（代码 ≠ Figma） | 显示两个版本 | "代码说 X，Figma 有 Y。哪个优先？" |
| 最终 QA | 每个页面的截图 + 审计报告 | "完成。签字？" |

**如果用户拒绝**：在继续之前修复。永远不要在拒绝的工作上构建。

---

## 7. 命名约定

匹配现有文件约定。如果从头开始：

**变量**（斜杠分隔）：
```
color/bg/primary     color/text/secondary    color/border/default
spacing/xs  spacing/sm  spacing/md  spacing/lg  spacing/xl  spacing/2xl
radius/none  radius/sm  radius/md  radius/lg  radius/full
typography/body/font-size    typography/heading/line-height
```

**原始值**：`blue/50` → `blue/900`, `gray/50` → `gray/900`

**组件名称**：`Button`, `Input`, `Card`, `Avatar`, `Badge`, `Checkbox`, `Toggle`

**变体名称**：`Property=Value, Property=Value` — 例如，`Size=Medium, Style=Primary, State=Default`

**页面分隔符**：`---`（最常见）或 `——— 组件 ———`

> 完整命名参考：[naming-conventions.md](references/naming-conventions.md)

---

## 8. 令牌架构

| 复杂性 | 模式 |
|-----------|---------|
| < 50 令牌 | 单个集合，2 个模式（亮色/暗色） |
| 50–200 令牌 | **标准**：原始值（1 个模式）+ 颜色语义（亮色/暗色）+ 间距（1 个模式）+ 排版（1 个模式） |
| 200+ 令牌 | **高级**：多个语义集合，4–8 个模式（亮色/暗色 × 对比度 × 品牌）。参见 M3 模式在 [token-creation.md](references/token-creation.md) |

标准模式（推荐起点）：
```
集合: "Primitives"    模式: ["Value"]
  blue/500 = #3B82F6, gray/900 = #111827, ...

集合: "Color"         模式: ["Light", "Dark"]
  color/bg/primary → 亮色: 别名 Primitives/white, 暗色: 别名 Primitives/gray-900
  color/text/primary → 亮色: 别名 Primitives/gray-900, 暗色: 别名 Primitives/white

集合: "Spacing"       模式: ["Value"]
  spacing/xs = 4, spacing/sm = 8, spacing/md = 16, ...
```

---

## 9. 每个阶段的反模式

**阶段 0 反模式：**
- ❌ 在使用户锁定范围之前开始创建任何内容
- ❌ 忽略现有文件约定并强加新的约定
- ❌ 在计划组件创建之前跳过 `search_design_system`

**阶段 1 反模式：**
- ❌ 对任何变量使用 `ALL_SCOPES`
- ❌ 在语义层中复制原始值而不是别名
- ❌ 不设置代码语法（破坏 Dev Mode 和往返）
- ❌ 在同意令牌分类之前创建组件令牌

**阶段 2 反模式：**
- ❌ 跳过封面页面或基础文档
- ❌ 在一个页面上放置多个不相关的组件

**阶段 3 反模式：**
- ❌ 在基础存在之前创建组件
- ❌ 在组件中硬编码任何填充/描边/间距/半径值
- ❌ 为每个图标创建一个变体（使用 INSTANCE_SWAP 代替）
- ❌ 在 combineAsVariants 之后不定位变体（它们都堆叠在 0,0）
- ❌ 创建变体矩阵 > 30 而不拆分（变体爆炸）
- ❌ 导入远程组件然后立即将其分离

**通用反模式：**
- ❌ 在理解错误之前重试失败的脚本
- ❌ 使用名称前缀匹配进行清理（删除用户拥有的节点）
- ❌ 在前一步的未验证工作上构建
- ❌ 跳过用户检查点以“节省时间”
- ❌ 并行化 use_figma 调用（始终顺序）
- ❌ 从内存中臆测/猜测节点 ID（始终从状态账本中读取）
- ❌ 编写巨大的 inline 脚本而不是使用提供的辅助脚本
- ❌ 因为用户说“构建按钮”而没有完成阶段 0-2 就开始阶段 3

---

## 10. 参考文档

按需加载——每个参考都是其阶段的权威来源：

使用您的文件读取工具在需要时读取这些文档。不要从文件名中假设其内容。

| 文档 | 阶段 | 必需/可选 | 加载时 |
|-----|-------|---------------------|-----------|
| [discovery-phase.md](references/discovery-phase.md) | 0 | **必需** | 开始任何构建 — 代码库分析 + Figma 检查 |
| [token-creation.md](references/token-creation.md) | 1 | **必需** | 创建变量、集合、模式、样式 |
| [documentation-creation.md](references/documentation-creation.md) | 2 | 必需 | 创建封面页面、基础文档、色板 |
| [component-creation.md](references/component-creation.md) | 3 | **必需** | 创建任何组件或变体 |
| [code-connect-setup.md](references/code-connect-setup.md) | 3–4 | 必需 | 设置 Code Connect 或变量代码语法 |
| [naming-conventions.md](references/naming-conventions.md) | 任何 | 可选 | 命名任何内容 — 变量、页面、变体、样式 |
| [error-recovery.md](references/error-recovery.md) | 任何 | **出错时必需** | 脚本失败、多步骤工作流恢复、清理被遗弃的工作流状态 |

---

## 11. 脚本

可重用的插件 API 辅助函数。嵌入到 `use_figma` 调用：

| 脚本 | 目的 |
|--------|---------|
| [inspectFileStructure.js](scripts/inspectFileStructure.js) | 发现所有页面、组件、变量、样式；返回完整清单 |
| [createVariableCollection.js](scripts/createVariableCollection.js) | 创建一个命名集合并设置模式；返回 `{collectionId, modeIds}` |
| [createSemanticTokens.js](scripts/createSemanticTokens.js) | 从令牌映射创建别名语义变量 |
| [createComponentWithVariants.js](scripts/createComponentWithVariants.js) | 从变体矩阵构建组件集；处理网格布局 |
| [bindVariablesToComponent.js](scripts/bindVariablesToComponent.js) | 将设计令牌绑定到所有组件视觉属性 |
| [createDocumentationPage.js](scripts/createDocumentationPage.js) | 创建一个带有标题 + 描述 + 区域结构的页面 |
| [validateCreation.js](scripts/validateCreation.js) | 验证创建的节点符合预期的数量、名称、结构 |
| [cleanupOrphans.js](scripts/cleanupOrphans.js) | 通过名称约定或状态账本 ID 删除孤儿节点 |
| [rehydrateState.js](scripts/rehydrateState.js) | 扫描文件中的所有页面、组件、变量按名称；返回完整的 `{key → nodeId}` 映射以用于状态重建 |
