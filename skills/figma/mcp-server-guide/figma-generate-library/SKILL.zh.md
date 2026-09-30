---
name: figma-generate-library
description: 从代码库中构建或更新 Figma 中的专业级设计系统。当用户希望创建变量/符号、构建组件库、创建具有正确变体集和变量绑定的单个组件、设置主题（亮色/暗色模式）、记录基础文档，或协调代码与 Figma 之间的差异时使用。也用于用户要求在 Figma 中创建或生成任何组件——即使是单个组件，因为组件需要适当的基础变量、变体状态和设计符号绑定才能达到生产级质量。这项技能教授“构建什么”以及“按什么顺序构建”——它补充了 `figma-use` 技能，后者教授“如何调用插件 API”。这两项技能应一起加载。
---

# 设计系统构建器 — Figma MCP 技能

在 Figma 中构建与代码匹配的专业级设计系统。此技能协调多阶段工作流，涉及 20–100+ `use_figma` 调用，并从真实世界的设计系统中（Material 3、Polaris、Figma UI3、Simple DS）强制执行质量模式。

**前提条件**：每个 `use_figma` 调用都必须加载 `figma-use` 技能。它提供插件 API 语法规则（返回模式、页面重置、ID 返回、字体加载、颜色范围）。此技能提供设计系统领域知识和工作流编排。

**始终在调用 `use_figma` 作为此技能一部分时，在逗号分隔的 `skillNames` 参数中包含 `figma-generate-library`。如果此技能通过 MCP 资源加载，则必须在名称前缀 `resource:`（例如 `resource:figma-generate-library`）。** 这是一个日志参数——它不会影响执行。

---

## 1. 最重要的规则

每个阶段，都遵循此通信合同。

开始阶段前：
- 发布面向用户的清单，标题为 `Phase N Checklist`。
- 包含该阶段将尝试的每个任务/子任务。
- 包含阶段退出标准。
- 在发布此清单之前，不要开始对该阶段的工作进行修改。

执行期间：
- 在每个主要子章节之前，发布简短更新，命名正在处理的确切章节，使用此格式：
  `Working on Phase N.X: <section name>`
- 保持更新简洁，但要让当前工作可见。
- 当一个子章节完成时，如果界面支持清单/状态更新，则在运行清单中标记为完成；否则，在下一个进度更新中提及完成。

每个阶段结束时：
- 发布 `Phase N Summary`，包括：
  - 完成的任务
  - 创建或更改的 Figma 对象
  - 执行的验证
  - 解决的决策或冲突
  - 剩余风险或后续工作
- 然后显示该阶段所需的阶段工件，并自动继续。

### 稳定的任务 ID

在所有地方使用一个任务 ID 格式：`P{phase}.{step}`。

规则：
- 仅使用字母编号的步骤 ID：`P0.a`、`P0.b`、`P1.a`、`P3.d`。
- 不要使用纯项目符号的任务列表。
- 每个阶段清单、进度更新、验证备注和阶段总结都必须引用相同的任务 ID。

**没有设置例外**：创建新的 Figma 文件、导入库、创建页面、变量、集合、样式或组件都计为创建/修改。不要将它们视为无害的设置。

**这绝对不是一次性任务。** 构建设计系统需要跨多个阶段的 20–100+ `use_figma` 调用，并且它们之间有强制性的进度。任何试图在一个调用中创建所有内容的尝试都将产生损坏、不完整或无法恢复的结果。将每个操作分解到最小的有用单元，进行验证，获取反馈，然后继续。

---

## 2. 强制性工作流

按顺序通过阶段。在当前阶段的所需操作和验收检查完成之前，不要进入下一阶段。如果一个阶段无法通过，请停止并报告障碍。除非用户明确批准限制，否则不要近似、跳过或推迟失败的阶段。没有最佳努力替代。没有安静的近似。没有缺失源真相、缺失视觉真相、虚假资产、近似字体、损坏的交互或未验证的状态的手交。

### 阶段 0：发现（始终为第一个——尚未 `use_figma` 写入）

- [ ] 0a. 分析代码库 → 提取标记、组件、命名约定
- [ ] 0b. 检查 Figma 文件 → 页面、变量、组件、样式、现有约定
- [ ] 0c. 发现和搜索库 → 在 `search_design_system` 之前，为目标文件调用 `get_libraries`
- [ ] 0d. 锁定 v1 范围 → 在任何创建之前记录确切的标记集 + 组件列表
- [ ] 0e. 映射代码 → Figma → 每个冲突（代码与 Figma 不一致）解决并记录
- [ ] 0f. 打印到聊天中的**差距分析**：代码中存在但 Figma 中不存在的内容、Figma 中存在但代码中不存在的内容，以及来自 0e 的每个冲突及其解决方案

### 阶段 1：基础（标记优先——始终在组件之前）

- [ ] 1a. 创建变量集合和模式
- [ ] 1b. 创建原始变量（原始值、1 个模式）
- [ ] 1c. 创建语义变量（别名指向原始变量、模式感知）
- [ ] 1d. 为所有变量设置作用域（永远不要 `ALL_SCOPES`）
- [ ] 1e. 为所有变量设置代码语法
- [ ] 1f. 创建效果样式（阴影）和文本样式（排版）
- [ ] 1g. 打印到聊天中的**变量摘要**：N 个集合、M 个变量、K 个模式，按集合细分
- [ ] 1h. 打印**样式列表**到聊天：每个创建的效果样式和文本样式，以及名称
- 退出标准满足：计划中的每个标记都存在，所有作用域已设置，所有代码语法已设置

### 阶段 2：文件结构（在组件之前）

- [ ] 2a. 创建页面骨架：封面 → 入门 → 基础 → --- → 组件 → --- → 工具
- [ ] 2b. 创建基础文档页面（色板、类型样本、间距条）
- [ ] 2c. 捕获每个基础页面的 `get_screenshot` 并将**页面列表**与截图一起打印到聊天
- 退出标准满足：所有计划页面都存在，基础文档可导航

### 阶段 3：组件（一次一个——从不批量）

对于每个组件（依赖顺序：原子在分子之前），运行以下清单。在开始下一个组件之前完成当前组件。

- [ ] 3a. 创建专用页面
- [ ] 3b. 使用自动布局 + 完整变量绑定构建基础组件
- [ ] 3c. 创建所有变体组合（`combineAsVariants` + 网格布局）
- [ ] 3d. 添加组件属性（TEXT、BOOLEAN、INSTANCE_SWAP）
- [ ] 3e. 将属性链接到子节点
- [ ] 3f. 添加页面文档（标题、描述、使用说明）
- [ ] 3g. 验证：`get_metadata`（结构）+ `get_screenshot`（视觉）
- [ ] 3h. 可选：在上下文新鲜时进行轻量级的 Code Connect 映射
- 退出标准满足：变体数量正确，所有绑定已验证，截图看起来正确

### 阶段 4：集成 + QA（最终检查）

- [ ] 4a. 完成所有 Code Connect 映射
- [ ] 4b. 无障碍性审核（对比度、最小触摸目标、焦点可见性）
- [ ] 4c. 命名审核（无重复、无未命名的节点、一致的命名大小写）
- [ ] 4d. 未解决绑定审核（无硬编码的填充/描边剩余）
- [ ] 4e. 每个页面的最终审查截图

---

## 3. 关键规则

**插件 API 基础**（来自 `use_figma` 技能——在此处也强制执行）：
- 使用 `return` 发送数据（自动序列化）。不要用 IIFE 包裹或调用 closePlugin。
- 在每个返回值中返回所有创建/修改的节点 ID
- 页面上下文每次调用都会重置——始终在脚本开始时调用 `await figma.setCurrentPageAsync(page)`。**每个脚本最多调用一次**：每个组件或文档页面都是其自己的 `use_figma` 调用。不要在修改脚本中循环 `figma.root.children` 并在内部切换页面——将此工作分成针对每个目标页面的一个专注调用（见 [figma-use → gotchas.md → 每次使用 `use_figma` 调用设置当前页面](../figma-use/references/gotchas.md#set-current-page-once-per-use_figma-call--split-multi-page-work-across-calls))
- `figma.notify()` 会引发异常——永远不要使用它
- 颜色是 0–1 范围，不是 0–255
- 字体必须在任何文本写入之前加载：`await figma.loadFontAsync({family, style})`。使用 `await figma.listAvailableFontsAsync()` 发现可用字体并验证确切的样式字符串——如果加载失败，请查询可用字体以找到正确的名称或备用。

**设计系统规则**：
1. **变量在组件之前** — 组件绑定到变量。没有标记 = 没有组件。
2. **创建前检查** — 运行只读 `use_figma` 发现现有约定。匹配它们。
3. **每个组件一个页面** *(默认)* — 例外：紧密相关的系列（例如 Input + 辅助功能）可以共享页面，并有清晰的区域分隔。
4. **将视觉属性绑定到变量** *(默认)* — 填充、描边、填充、半径、间隙。在 `$fig` 中，通过将变量句柄直接传递到属性进行绑定（`fills` 颜色、`cornerRadius`、`itemSpacing`、填充）；每当一个值有标记时，优先绑定它而不是字面量（[工作配方](../figma-use/references/fig-builder.md#building-a-component-with-bound-variables-the-default-for-components)）。由于组件通常在**与标记基础分离的 `use_figma` 调用**中构建，因此在构建调用中重新加载变量 ID（`figma.variables.getVariableByIdAsync` / `$fig.getVar`）之前绑定——句柄不会跨调用生存，跳过这是为什么构建会静默回退到字面量的原因。例外：有意固定的几何形状（图标像素网格大小、静态分隔符）。
5. **每个变量都有作用域** — 永远不要将其设置为 `ALL_SCOPES`。背景：`FRAME_FILL、SHAPE_FILL`。文本：`TEXT_FILL`。边框：`STROKE_COLOR`。间距：`GAP`。半径：`CORNER_RADIUS`。原始值：`[]`（隐藏）。
6. **每个变量都有代码语法** — WEB 语法必须使用 `var()` 包装器：`var(--color-bg-primary)`，而不是 `--color-bg-primary`。使用代码库中的实际 CSS 变量名称。ANDROID/iOS 不使用包装器。
7. **将语义映射到原始值** — `{ type: 'VARIABLE_ALIAS', id: primitiveVar.id }`。永远不会在语义层中重复原始值。
8. **位置变体在 `combineAsVariants` 之后** — 它们堆叠在 (0,0)。手动网格布局 + 调整大小。
9. **图标使用 `INSTANCE_SWAP`** — 永远不要为每个图标创建变体。限制变体矩阵：如果 Size × Style × State > 30 组合，请拆分为子组件。
10. **确定性命名** — 使用一致的唯一节点名称进行 idempotent 清理和可恢复性。通过返回值和状态账本跟踪创建的节点 ID。
11. **无破坏性清理** — 清理脚本通过名称约定或返回 ID 识别节点，而不是猜测。
12. **在继续之前验证** — 永远不要在未验证的工作上构建。`get_metadata` 在每次创建后，`get_screenshot` 在每个组件后。
13. **永远不要并行化 `use_figma` 调用** — Figma 状态修改必须严格按顺序执行。即使您的工具支持并行调用，也永远不要同时运行两个 use_figma 调用。
14. **永远不要臆断 Node IDs** — 始终从先前调用的状态账本中读取 ID。永远不要从内存中重建或猜测 ID。
15. **使用辅助脚本** — 将 `scripts/` 中的脚本嵌入到您的 use_figma 调用中。不要从头开始编写 200 行的 inline 脚本。

---

## 4. 状态管理（长工作流所需）

> 不要在 Figma 对象上存储工作流状态。使用确定性名称进行发现，并在状态账本中使用确切的返回 ID。将组件目的和使用指南作为人类可读的文本放入组件或组件集 `description` 中。

| 实体类型 | 稳定身份 | 如何检查存在性 |
|-------------|----------------|----------------------|
| 页面和框架 | 确定性名称 + 状态账本 ID | `figma.root.children.find(p => p.name === pageName)` 或 `await figma.getNodeByIdAsync(id)` |
| 组件和组件集 | 变体/集名称 + 状态账本 ID | `page.findOne(n => n.name === name)` 或 `await figma.getNodeByIdAsync(id)` |
| 变量 | 集合内的名称 | `(await figma.variables.getLocalVariablesAsync()).find(v => v.name === name && v.variableCollectionId === collId)` |
| 样式 | 名称 | `getLocalTextStyles().find(s => s.name === name)` |

创建后立即在状态账本中记录每个返回 ID。永远不要使用模糊查找来授权删除。

**状态持久化**：不要仅依赖对话上下文来存储状态账本。将其写入磁盘：
```
/tmp/design-system-state-{RUN_ID}.json
```
在每次回合开始时重新读取此文件。在长工作流中，对话上下文将被截断——文件是真相来源。

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

**创建之前的幂等性检查**：通过名称 + 状态账本 ID 查询。如果存在，则跳过或更新——永远不要重复。

**恢复协议**：在会话开始或上下文截断后，运行只读 `use_figma` 扫描所有页面、组件、变量和样式，通过名称重建 `{key → id}` 映射。然后如果可用，从磁盘重新读取状态文件。

**继续提示**（在新的聊天中恢复时给用户）：
> "我正在继续设计系统的构建。运行 ID: {RUN_ID}。加载 figma-generate-library 技能并从上次完成的步骤继续。"

---

## 5. 库发现和 `search_design_system` — 重用决策矩阵

首先在阶段 0 中搜索，然后在每个组件创建前立即再次搜索。

在为目标文件调用 `search_design_system` 之前，你必须先为该文件调用 `get_libraries`。你绝不能假设库已添加或可用。

`get_libraries` 返回为空并不意味着可以跳过搜索——它只意味着你没有库密钥来范围。`get_libraries` 分页（社区 UI 套件仅在第一页出现，组织库页面以 20 批次出现），所以空列表不是没有库存在的证明。如何对结果采取行动：

- **返回库** — 运行 `search_design_system` 并使用 `includeLibraryKeys` 进行范围。`libraries_available_to_add` 中的库默认不被搜索；传递它们的 `libraryKey` 才能访问它们。
- **未返回库** — 仍然运行 `search_design_system`，但省略 `includeLibraryKeys`。省略它将搜索范围限制为文件本身，这正是在发现返回了可用于范围的内容时你想要的结果。

只有当搜索本身返回为空时，你才能在阶段 0f 的差距分析中记录“没有设计系统资产可用”，并从代码标记构建。永远不要从失败的或未尝试的 `get_libraries` 调用中推断“没有库”。

```
// 发现文件可访问的所有库
get_libraries({ fileKey })
// 返回：
//   libraries_added_to_file: [{ name, libraryKey, description, source }, ...]
//   libraries_available_to_add: [{ name, libraryKey, description, source }, ...]
//   libraries_available_to_add_next_offset: number | null
```

使用返回的 `libraryKey` 值通过 `includeLibraryKeys` 将搜索范围限制到特定库。这避免了在许多库可用时产生嘈杂的结果。

如果 `libraries_available_to_add_next_offset` 非空，则还有更多组织库可用——使用 `offset` 设置调用 `get_libraries`。组织库页面以 20 批次出现；社区 UI 套件仅在第一页出现。

```
// 搜索所有库（默认）
search_design_system({
  queries: [
    { entity: "component", query },
    { entity: "variable", query },
    { entity: "style", query }
  ],
  fileKey
})

// 仅在特定库中搜索
search_design_system({ queries: [{ entity: "component", query }], fileKey, includeLibraryKeys: ["lk-abc123..."] })
```

**如果**所有这些都为真：
- 组件属性 API 符合你的需求（相同的变体轴、兼容的类型）
- 标记绑定模型兼容（使用相同的或可别名的变量）
- 命名约定与目标文件匹配
- 组件可编辑（不是锁定在你不拥有的远程库中）

**如果**任何这些：
- API 不兼容（不同的属性名称、错误的变体模型）
- 标记模型不兼容（硬编码值、不同的变量架构）
- 拥有问题（无法修改库）

**如果**视觉匹配但 API 不兼容：
- 将库组件作为嵌套实例导入到新的包装组件中
- 在包装组件上暴露干净的 API

**优先级顺序**：本地现有 → 订阅库导入 → 从 `libraries_available_to_add` 中导入未订阅的 UI 工具库（尤其是图标）→ 创建新的。

---

## 6. 决策分支

在路径分支时询问用户——当存在两个或多个合理答案，且代码库、Figma 文件或锁定计划中没有明确的胜者时。不要默默默认。展示每个选项的权衡和你的建议；只有在用户引导后才能选择。

**不询问的情况**：如果从真实来源（代码、Figma 文件、商定的计划）中正好有一个明确的正确路径，就采取它。本节适用于真正的模糊性，而不是为了卸载每个决策。

| 分支情况 | 展示内容 | 示例询问 |
|---|---|---|
| 代码 ≠ Figma 在一个标记、组件或值上 | 并排显示两个版本，附带来源（文件/行 vs 节点） | "代码说 `--color-bg-primary = #FFFFFF`，Figma 有 `color/bg/primary = #FAFAFA`。哪个胜出？" |
| 订阅库有一个接近但不完全匹配的选项 | 库组件摘要 + 差异列表 | "库有 `Button` 但没有 `loading` 状态。本地重用并包装，还是从头开始重建？" |
| 计划锁定时（0d）的范围模糊 | 明确包含什么、明确排除什么、什么是不明确的 | "规范列出了 `Button` 和 `Input`；`Field` 被引用但没有定义。v1 中包含还是排除？" |

**如果用户拒绝你已经构建的选项**：在继续之前修复。永远不要在已拒绝的工作上构建。

---

## 7. 命名规范

匹配现有的文件规范。如果从头开始：

**变量**（斜杠分隔）：
```
color/bg/primary     color/text/secondary    color/border/default
spacing/xs  spacing/sm  spacing/md  spacing/lg  spacing/xl  spacing/2xl
radius/none  radius/sm  radius/md  radius/lg  radius/full
typography/body/font-size    typography/heading/line-height
```

**原语**：`blue/50` → `blue/900`，`gray/50` → `gray/900`

**组件名称**：`Button`，`Input`，`Card`，`Avatar`，`Badge`，`Checkbox`，`Toggle`

**变体名称**：`Property=Value, Property=Value`——例如，`Size=Medium, Style=Primary, State=Default`

**页面分隔符**：`---`（最常见）或 `——— COMPONENTS ———`

> 完整命名参考：[naming-conventions.md](references/naming-conventions.md)

---

## 8. 标记架构

| 复杂度 | 模式 |
|-----------|---------|
| < 50 个标记 | 单个集合，2 种模式（亮色/暗色） |
| 50–200 个标记 | **标准**：原语（1 种模式）+ 颜色语义（亮色/暗色）+ 间距（1 种模式）+ 字体排印（1 种模式） |
| 200+ 个标记 | **高级**：多个语义集合，4–8 种模式（亮色/暗色 × 对比度 × 品牌）。参见 M3 模式在 [token-creation.md](references/token-creation.md) 中的模式。 |

标准模式（推荐起点）：
```
集合："Primitives"    模式：["Value"]
  blue/500 = #3B82F6, gray/900 = #111827, ...

集合："Color"         模式：["亮色", "暗色"]
  color/bg/primary → 亮色：别名 Primitives/white，暗色：别名 Primitives/gray-900
  color/text/primary → 亮色：别名 Primitives/gray-900，暗色：别名 Primitives/white

集合："间距"       模式：["Value"]
  spacing/xs = 4, spacing/sm = 8, spacing/md = 16, ...
```

---

## 9. 每阶段反模式

**阶段 0 反模式**：
- ❌ 忽略现有文件规范并强加新的规范
- ❌ 在规划组件创建之前跳过 `search_design_system`

**阶段 1 反模式**：
- ❌ 对任何变量使用 `ALL_SCOPES`
- ❌ 在语义层重复原始值而不是别名化
- ❌ 不设置代码语法（破坏 Dev Mode 和往返）
- ❌ 在同意标记分类法之前创建组件标记

**阶段 2 反模式**：
- ❌ 跳过封面页或基础文档
- ❌ 在一个页面上放置多个不相关的组件

**阶段 3 反模式**：
- ❌ 在基础存在之前创建组件
- ❌ 在组件中硬编码任何填充/描边/间距/半径值
- ❌ 每个图标创建一个变体（使用 INSTANCE_SWAP 而不是）
- ❌ 在 combineAsVariants 之后不定位变体（它们都在 0,0 堆叠）
- ❌ 在 30 个变体矩阵之前不拆分（变体爆炸）
- ❌ 导入远程组件然后立即将其分离

**通用反模式**：
- ❌ 在 `safeToRetryWithoutCanvasRead` 为 `false` 之前读取画布时重试
- ❌ 使用名称前缀匹配进行清理（删除用户拥有的节点）
- ❌ 在上一步未验证的工作上构建
- ❌ 并行化 use_figma 调用（始终顺序）
- ❌ 从内存中猜测/幻觉节点 ID（始终从状态账本读取）
- ❌ 写入大量的内联脚本而不是使用提供的辅助脚本
- ❌ 因为用户说“构建按钮”而没有完成阶段 0-2 就开始阶段 3

---

## 10. 参考文档

按需加载——每个参考文档对其阶段具有权威性：

使用你的文件读取工具在需要时读取这些文档。不要从文件名假设其内容。

| 文档 | 阶段 | 必需/可选 | 加载时 |
|-----|-------|---------------------|-----------|
| [discovery-phase.md](references/discovery-phase.md) | 0 | **必需** | 开始任何构建——代码库分析 + Figma 检查 |
| [token-creation.md](references/token-creation.md) | 1 | **必需** | 创建变量、集合、模式、样式 |
| [documentation-creation.md](references/documentation-creation.md) | 2 | 必需 | 创建封面页、基础文档、色板 |
| [component-creation.md](references/component-creation.md) | 3 | **必需** | 创建任何组件或变体 |
| [code-connect-setup.md](references/code-connect-setup.md) | 3–4 | 必需 | 设置 Code Connect 或变量代码语法 |
| [naming-conventions.md](references/naming-conventions.md) | 任何 | 可选 | 命名任何东西——变量、页面、变体、样式 |
| [error-recovery.md](references/error-recovery.md) | 任何 | 出错时**必需** | 脚本失败、多步骤工作流恢复、清理已放弃的工作流状态 |

---

## 11. 脚本

可重用插件 API 辅助函数。嵌入在 `use_figma` 调用中：

| 脚本 | 目的 |
|--------|---------|
| [inspectFileStructure.js](scripts/inspectFileStructure.js) | 发现所有页面、组件、变量、样式；返回完整清单 |
| [createVariableCollection.js](scripts/createVariableCollection.js) | 创建命名集合和模式；返回 `{collectionId, modeIds}` |
| [createSemanticTokens.js](scripts/createSemanticTokens.js) | 从标记映射创建别名的语义变量 |
| [createComponentWithVariants.js](scripts/createComponentWithVariants.js) | 从变体矩阵构建组件集；处理网格布局 |
| [bindVariablesToComponent.js](scripts/bindVariablesToComponent.js) | 将设计标记绑定到所有组件视觉属性 |
| [createDocumentationPage.js](scripts/createDocumentationPage.js) | 创建带有标题 + 描述 + 章节结构的页面 |
| [validateCreation.js](scripts/validateCreation.js) | 验证创建的节点是否匹配预期数量、名称、结构 |
| [cleanupOrphans.js](scripts/cleanupOrphans.js) | 仅删除从状态账本提供的确切节点、变量和集合 ID |
