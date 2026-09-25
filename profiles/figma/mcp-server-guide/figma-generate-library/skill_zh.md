# 设计系统构建器 — Figma MCP 技能

在 Figma 中构建与代码匹配的专业级设计系统。此技能协调多阶段工作流，跨越连贯且可安全重试的构建阶段，从现实世界的设计系统（Material 3、Polaris、Figma UI3、Simple DS）中强制执行质量模式。

**前提条件**：对于每个 `use_figma` 调用，都必须加载 `figma-use` 技能。它提供插件 API 语法规则（返回模式、页面重置、ID 返回、字体加载、颜色范围）。此技能提供设计系统领域知识和工作流协调。

**始终在调用 `use_figma` 作为此技能一部分时，在逗号分隔的 `skillNames` 参数中包含 `figma-generate-library`。如果此技能通过 MCP 资源加载，则必须在名称前缀 `resource:`（例如 `resource:figma-generate-library`）。这是一个日志参数——它不会影响执行。

---

## 1. 最重要的规则

对于每个阶段，遵循此通信合同。

开始阶段之前：
- 发布一个面向用户的清单，标题为 `Phase N Checklist`。
- 包含该阶段将尝试的每个任务/子任务。
- 包含阶段退出标准。
- 在发布此清单之前，不要开始对该阶段的工作进行变异。

执行期间：
- 在每个主要子部分之前，发布一个简短的更新，命名正在处理的确切部分，使用此格式：
  `Working on Phase N.X: <section name>`
- 保持更新简洁，但使当前工作可见。
- 当一个子部分完成时，如果界面支持清单/状态更新，则在运行清单中将其标记为已完成；否则，在下一个进度更新中提及完成。

每个阶段结束时：
- 发布 `Phase N Summary`，包括：
  - 完成的任务
  - 创建或更改的 Figma 对象
  - 执行的验证
  - 解决的决策或冲突
  - 剩余风险或后续操作
- 然后显示该阶段所需的阶段工件，并自动继续。

### 稳定的任务 ID

在整个系统中使用一个任务 ID 格式：`P{phase}.{step}`。

规则：
- 仅使用字母编号的步骤 ID：`P0.a`、`P0.b`、`P1.a`、`P3.d`。
- 不要使用纯项目符号表示任务列表。
- 每个阶段清单、进度更新、验证笔记和阶段摘要都必须引用相同的任务 ID

**无设置例外**：创建新的 Figma 文件、导入库、创建页面、变量、集合、样式或组件都计为创建/变异。不要将它们视为无害的设置。

**这绝对不是一次性任务。** 构建设计系统跨越多个阶段，它们之间有强制性的进度。任何试图一次调用中创建所有内容都将产生损坏、不完整或无法恢复的结果。将工作组织成连贯且可安全重试的构建阶段：当结果脚本保持安全可重试时批量相关操作，仅在页面上下文边界、难以恢复的变异或实际失败后的目标重试后拆分——绝不要仅为了创建验证检查点而拆分正在工作的操作。保持变异严格按顺序，从证据中验证，获取反馈，然后继续。

---

## 2. 强制性工作流

按顺序通过阶段。在当前阶段的必要操作和验收检查完成之前，不要进入下一个阶段。如果一个阶段无法通过，请停止并报告障碍。除非用户明确批准限制，否则不要近似、跳过或推迟失败的阶段。没有最佳努力替代。没有安静的近似。没有缺少源真相、缺少视觉真相、虚假资产、近似字体、损坏的交互或未验证的状态的手交。

### 阶段 0：发现（始终为第一个——尚未 `use_figma` 写入）

- [ ] 0a. 分析代码库 → 提取标记、组件、命名约定
- [ ] 0b. 检查 Figma 文件 → 页面、变量、组件、样式、现有约定
- [ ] 0c. 发现和搜索库 → 在 `search_design_system` 之前为目标文件调用 `get_libraries`
- [ ] 0d. 锁定 v1 范围 → 在任何创建之前记录确切的标记集 + 组件列表
- [ ] 0e. 代码 → Figma → 每个冲突（代码与 Figma 不一致）解决并记录
- [ ] 0f. 打印到聊天中的**差距分析**：代码中存在但 Figma 中不存在的内容、Figma 中存在但代码中不存在的内容，以及 0e 中的每个冲突及其解决方案

### 阶段 1：基础（标记优先——始终在组件之前）

- [ ] 1a. 创建变量集合和模式
- [ ] 1b. 创建原始变量（原始值，1 个模式）
- [ ] 1c. 创建语义变量（别名到原始值，模式感知）
- [ ] 1d. 为所有变量设置范围（从不使用 `ALL_SCOPES`）
- [ ] 1e. 为所有变量设置代码语法
- [ ] 1f. 创建效果样式（阴影）和文本样式（排版）
- [ ] 1g. 打印到聊天中的**变量摘要**：N 个集合、M 个变量、K 个模式，按集合细分
- [ ] 1h. 打印**样式列表**到聊天：每个效果样式和文本样式，包括名称
- [ ] 退出标准满足：已商定的计划中的每个标记都存在，所有范围已设置，所有代码语法已设置

### 阶段 2：文件结构（在组件之前）

- [ ] 2a. 创建页面骨架：封面 → 获取 started → 基础 → --- → 组件 → --- → 工具
- [ ] 2b. 创建基础文档页面（色板、类型样本、间距条）
- [ ] 2c. 在组成基础页面后，对阶段进行**一次视觉审查**，并打印**页面列表**到聊天。如果审查发现有意义的视觉缺陷，应用有针对性的修复并取**一个修复后截图**；最新通过的截图是最终的（不需要未更改的最终截图）
- [ ] 退出标准满足：所有计划页面都存在，基础文档可导航

### 阶段 3：组件（重试安全的阶段，依赖顺序保留）

按依赖顺序（原子在前，分子在后）通过组件。一个构建阶段可以包含多个相关组件，但不同页面上的工作必须跨连贯且可安全重试的 `use_figma` 调用进行拆分。每个变异调用必须针对一个页面，并且最多调用一次 `figma.setCurrentPageAsync`。在开始依赖于它的工作之前，运行每个组件所需的清单项目，并满足其退出标准。

- [ ] 3a. 创建专用页面
- [ ] 3b. 使用自动布局 + 完全变量绑定构建基础组件
- [ ] 3c. 创建所有变体组合（`combineAsVariants` + 网格布局）
- [ ] 3d. 添加组件属性（TEXT、BOOLEAN、INSTANCE_SWAP）
- [ ] 3e. 将属性链接到子节点
- [ ] 3f. 添加页面文档（标题、描述、使用说明）
- [ ] 3g. 从写入返回的结构化证据（ID 加上相关计数、名称、边界）进行验证；仅在证据缺失或变异使其失效时运行单独的结构化审核。对每个连贯的组合阶段进行**一次视觉审查**，并且仅在需要目标视觉修复时才进行**一个修复后截图**
- [ ] 3h. 可选：在上下文新鲜时进行轻量级的 Code Connect 映射
- [ ] 退出标准满足：变体计数正确、所有绑定已验证、最新通过的截图看起来正确

### 阶段 4：集成 + QA（最终遍历）

- [ ] 4a. 完成所有 Code Connect 映射
- [ ] 4b. 无障碍审核（对比度、最小触摸目标、焦点可见性）
- [ ] 4c. 命名审核（无重复、无未命名的节点、一致的 casing）
- [ ] 4d. 未解决绑定审核（无硬编码的填充/描边剩余）
- [ ] 4e. 每个在集成期间更改的组合阶段的最终视觉审查；最新通过的截图是最终的（不需要未更改的最终截图）

---

## 3. 关键规则

**插件 API 基础**（来自 use_figma 技能——在此处也强制执行）：
- 使用 `return` 发送数据（自动序列化）。不要用 IIFE 或调用 closePlugin 包裹。
- 在每个返回值中返回所有创建/变异的节点 ID
- 页面上下文每次调用都会重置——始终在开始时 `await figma.setCurrentPageAsync(page)`。**每个脚本最多调用一次**：每个组件或文档页面都是其自己的 `use_figma` 调用。永远不要在变异脚本中循环 `figma.root.children` 并在页面之间切换（将此工作拆分为每个目标页面一个专注的调用（见 [figma-use → gotchas.md → 每个use_figma调用最多设置一次当前页面](../figma-use/references/gotchas.md#set-current-page-once-per-use_figma-call--split-multi-page-work-across-calls))
- `figma.notify()` 会引发异常——永远不要使用它
- 颜色是 0–1 范围，不是 0–255
- 字体必须在任何文本写入之前加载：`await figma.loadFontAsync({family, style})`。使用 `await figma.listAvailableFontsAsync()` 发现可用字体并验证确切的样式字符串——如果加载失败，请查询可用字体以找到正确的名称或备用。

**设计系统规则**：
1. **变量在组件之前** — 组件绑定到变量。没有标记 = 没有组件。
2. **创建前检查** — 运行只读 `use_figma` 发现现有约定。匹配它们。
3. **每个组件一个页面** *(默认)* — 例外：紧密相关的家族（例如，Input + 辅助工具）可以共享一个页面，并有清晰的区域分隔。
4. **将视觉属性绑定到变量** *(默认)* — 填充、描边、填充、半径、间隙。例外：有意固定的几何形状（图标像素网格大小、静态分隔符）。
5. **每个变量都有范围** — 绝对不要作为 `ALL_SCOPES` 留下。背景：`FRAME_FILL, SHAPE_FILL`。文本：`TEXT_FILL`。边框：`STROKE_COLOR`。间距：`GAP`。半径：`CORNER_RADIUS`。原始值：`[]`（隐藏）。
6. **每个变量都有代码语法** — WEB 语法必须使用 `var()` 包装器：`var(--color-bg-primary)`，而不是 `--color-bg-primary`。使用代码库中的实际 CSS 变量名称。ANDROID/iOS 不使用包装器。
7. **将语义映射到原始值** — `{ type: 'VARIABLE_ALIAS', id: primitiveVar.id }`。从不重复原始值在语义层。
8. **位置变体在 combineAsVariants 之后** — 它们堆叠在 (0,0)。手动网格布局 + 调整大小。
9. **图标使用 INSTANCE_SWAP** — 永远不要为每个图标创建变体。限制变体矩阵：如果 Size × Style × State > 30 组合，则拆分为子组件。
10. **确定性命名** — 使用一致且唯一的节点名称进行 idempotent 清理和可恢复性。通过返回值和状态账本跟踪创建的节点 ID。
11. **无破坏性清理** — 清理脚本通过名称约定或返回的 ID 识别节点，而不是猜测。
12. **在继续之前从证据中验证** — 永远不要在未验证的工作上构建。依赖写入返回的结构化证据（ID 加上相关计数、名称、边界）；仅在需要建立阶段退出标准或相关变异使先前证据失效时运行一次批量的结构化审核。每个连贯的组合阶段进行一次视觉审查（在目标视觉修复后只进行一次修复后截图）。
13. **永远不要并行化 `use_figma` 调用** — Figma 状态变异必须严格按顺序。即使您的工具支持并行调用，也永远不要同时运行两个 use_figma 调用。
14. **永远不要臆断节点 ID** — 始终从先前调用的状态账本中读取 ID。永远不要从内存中重建或臆断 ID。
15. **使用辅助脚本** — 将 `scripts/` 中的脚本嵌入到您的 use_figma 调用中。不要从头开始编写 200 行的 inline 脚本。

---

## 4. 状态管理（长工作流的必需项）

> 不要在 Figma 对象上存储工作流状态。使用确定性名称进行发现，并在状态账本中使用确切的返回 ID。将组件的目的和使用指南作为人类可读的内容放入组件或组件集 `description`。

| 实体类型 | 稳定性 ID | 如何检查存在性 |
|-------------|----------------|----------------------|
| 页面和框架 | 确定性名称 + 状态账本 ID | `figma.root.children.find(p => p.name === pageName)` 或 `await figma.getNodeByIdAsync(id)` |
| 组件和组件集 | 变体/集名称 + 状态账本 ID | `page.findOne(n => n.name === name)` 或 `await figma.getNodeByIdAsync(id)` |
| 变量 | 集合内的名称 | `(await figma.variables.getLocalVariablesAsync()).find(v => v.name === name && v.variableCollectionId === collId)` |
| 样式 | 名称 | `getLocalTextStyles().find(s => s.name === name)` |

立即在创建后记录每个返回 ID 到状态账本。永远不要使用模糊查找来授权删除。

**状态持久化**：不要仅依赖对话上下文来记录状态账本。将其写入磁盘：
```
/tmp/design-system-state-{RUN_ID}.json
```
在每次轮次开始时重新读取此文件。在长工作流中，对话上下文将被截断——文件是真相来源。

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

**在每次创建之前进行幂等性检查**：通过名称 + 状态账本 ID 查询。如果存在，则跳过或更新——永远不要重复。

**恢复协议**：在会话开始或上下文截断后，运行只读 `use_figma` 扫描所有页面、组件、变量和样式，通过名称重建 `{key → id}` 映射。然后如果可用，从磁盘重新读取状态文件。

**继续提示**（在新的聊天中恢复时提供给用户）：
> "我正在继续构建设计系统。运行 ID: {RUN_ID}。加载 figma-generate-library 技能并从上次完成的步骤继续。"

---

## 5. 库发现和 search_design_system — 重用决策矩阵

首先在阶段 0 中搜索，然后在每个组件创建之前再次搜索。

在为目标文件调用 `search_design_system` 之前，你必须先为该文件调用 `get_libraries`。你绝不能假设库已添加或可用。

`get_libraries` 结果为空**并不**免除跳过搜索——它只是意味着你没有库密钥来范围。`get_libraries` 分页（社区 UI 套件仅在第一页出现，组织库页面以 20 批次出现），所以空列表不是没有库存在的证明。如何对结果采取行动：

- **返回库** — 运行 `search_design_system` 并使用 `includeLibraryKeys` 进行范围。`libraries_available_to_add` 中的库默认不被搜索；传递它们的 `libraryKey` 才能到达它们。
- **未返回库** — 仍然运行 `search_design_system`，但省略 `includeLibraryKeys`。省略它将搜索范围限制为文件本身，这正是在你从发现返回了 nothing to scope by 时想要的。

只有当搜索本身返回为空时，你才能在阶段 0f 差距分析中记录“没有设计系统资产可用”，并从代码标记构建。永远不要从失败的或未尝试的 `get_libraries` 调用中推断“没有库”。

```
// 发现文件可访问的所有库
get_libraries({ fileKey })
// 返回：
//   libraries_added_to_file: [{ name, libraryKey, description, source }, ...]
//   libraries_available_to_add: [{ name, libraryKey, description, source }, ...]
//   libraries_available_to_add_next_offset: number | null
```

使用返回的 `libraryKey` 值通过 `includeLibraryKeys` 将搜索范围限制到特定库。这避免了当许多库可用时出现嘈杂的结果。

如果 `libraries_available_to_add_next_offset` 非空，则还有更多组织库可用——再次调用 `get_libraries`，将 `offset` 设置为该值。组织库页面以 20 批次出现；社区 UI 套件仅在第一页出现。

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

// 仅在特定库内搜索
search_design_system({ queries: [{ entity: "component", query }], fileKey, includeLibraryKeys: ["lk-abc123..."] })
```

**如果**所有这些都为真：
- 组件属性 API 与您的需求匹配（相同的变体轴，兼容的类型）
- 标记绑定模型兼容（使用相同的或可别名的变量）
- 命名约定与目标文件匹配
- 组件可编辑（不是锁定在您不拥有的远程库中）

**如果**任何这些：
- API 不兼容（不同的属性名称，错误的变体模型）
- 标记模型不兼容（硬编码值，不同的变量架构）
- 拥有问题（无法修改库）

**如果**视觉匹配但 API 不兼容：
- 将库组件作为嵌套实例导入到新的包装组件中
- 在包装器上暴露干净的 API

**优先级顺序**：本地现有 → 订阅库导入 → 未订阅的 UI Kit 库从 `libraries_available_to_add`（尤其是图标）→ 创建新的。

---

## 6. 决策分支

当路径分支时询问用户——当存在两个或多个合理的答案，并且没有从代码库、Figma 文件或锁定计划中出现的明确赢家时。不要无声地默认。每个选项都应与其权衡和您的建议一起呈现；只有在用户引导后才能选择。

**不询问的情况**：如果从源真相（代码、Figma 文件、商定的计划）中确实只有一个路径是正确的，请采取它。本节适用于真正的歧义，而不是为了卸载每个决策。

| 分支情况 | 要呈现的内容 | 示例询问 |
|---|---|---|
| 代码 ≠ Figma on a token, component, or value | 两者版本并排显示，包括来源（文件/行 vs 节点） | "代码说 `--color-bg-primary = #FFFFFF`，Figma 有 `color/bg/primary = #FAFAFA`。哪个获胜?" |
| 订阅库有一个接近但不完全匹配 | 库组件摘要 + 差距列表 | "库有 `Button` 但没有 `loading` 状态。本地重用 + 包装，或从头开始重建?" |
| 计划锁定时的范围歧义 | 明确包含的内容、明确排除的内容、模糊的内容 | "规范列出了 `Button` 和 `Input`；`Field` 被引用但未定义。v1 中包含或排除?" |

**如果用户拒绝您已经构建在上的选项**：在继续之前修复。永远不要在拒绝的工作上构建。

---

## 7. 命名约定

匹配现有文件约定。如果从头开始：

**变量**（斜杠分隔）:
```
color/bg/primary     color/text/secondary    color/border/default
spacing/xs  spacing/sm  spacing/md  spacing/lg  spacing/xl  spacing/2xl
radius/none  radius/sm  radius/md  radius/lg  radius/full
typography/body/font-size    typography/heading/line-height
```

**原始值**: `blue/50` → `blue/900`, `gray/50` → `gray/900`

**组件名称**: `Button`, `Input`, `Card`, `Avatar`, `Badge`, `Checkbox`, `Toggle`

**变体名称**: `Property=Value, Property=Value` — 例如，`Size=Medium, Style=Primary, State=Default`

**页面分隔符**: `---`（最常见）或 `——— 组件 ———`

> 完整命名参考: [naming-conventions.md](references/naming-conventions.md)

---

## 8. 标记架构

| 复杂性 | 模式 |
|-----------|---------|
| < 50 标记 | 单个集合，2 个模式（Light/Dark） |
| 50–200 标记 | **标准**: 原始值（1 个模式） + 颜色语义（Light/Dark） + 间距（1 个模式） + 排版（1 个模式） |
| 200+ 标记 | **高级**: 多个语义集合，4–8 个模式（Light/Dark × 对比度 × 品牌）。见 M3 模式在 [token-creation.md](references/token-creation.md) |

标准模式（推荐起点）:
```
集合: "Primitives"    模式: ["Value"]
  blue/500 = #3B82F6, gray/900 = #111827, ...

集合: "Color"         模式: ["Light", "Dark"]
  color/bg/primary → Light: 别名 Primitives/white, Dark: 别名 Primitives/gray-900
  color/text/primary → Light: 别名 Primitives/gray-900, Dark: 别名 Primitives/white

集合: "Spacing"       模式: ["Value"]
  spacing/xs = 4, spacing/sm = 8, spacing/md = 16, ...
```

---

## 9. 每个阶段的反模式

**阶段 0 反模式**:
- ❌ 忽略现有文件约定并强加新的约定
- ❌ 在计划组件创建之前跳过 `search_design_system`

**阶段 1 反模式**:
- ❌ 对任何变量使用 `ALL_SCOPES`
- ❌ 在语义层重复原始值而不是别名
- ❌ 不设置代码语法（破坏 Dev Mode 和往返）
- ❌ 在商定标记分类之前创建组件标记

**阶段 2 反模式**:
- ❌ 跳过封面页面或基础文档
- ❌ 在一个页面上放置多个不相关的组件

**阶段 3 反模式**:
- ❌ 在基础存在之前创建组件
- ❌ 在组件中硬编码任何填充/描边/间距/半径值
- ❌ 为每个图标创建变体（使用 INSTANCE_SWAP 代替）
- ❌ combineAsVariants 之后不定位变体（它们都堆叠在 0,0）
- ❌ 变体矩阵 > 30 不拆分（变体爆炸）
- ❌ 导入远程组件然后立即分离它们

**一般反模式**:
- ❌ 在 `safeToRetryWithoutCanvasRead` 为 `false` 之前读取画布时重试
- ❌ 使用名称前缀匹配进行清理（删除用户拥有的节点）
- ❌ 在前一步未验证的工作上构建
- ❌ 并行化 use_figma 调用（始终按顺序）
- ❌ 从内存中臆断/幻觉节点 ID（始终从状态账本中读取）
- ❌ 写入巨大的 inline 脚本而不是使用提供的辅助脚本
- ❌ 因为用户说“构建按钮”而开始阶段 3，而没有完成阶段 0-2

---

## 10. 参考文档

按需加载——每个参考都是其阶段的权威：

使用您的文件阅读工具在需要时读取这些文档。不要从文件名假设其内容。

| 文档 | 阶段 | 必须的/可选 | 加载时 |
|-----|-------|---------------------|-----------|
| [discovery-phase.md](references/discovery-phase.md) | 0 | **必须** | 开始任何构建——代码库分析 + Figma 检查 |
| [token-creation.md](references/token-creation.md) | 1 | **必须** | 创建变量、集合、模式、样式 |
| [documentation-creation.md](references/documentation-creation.md) | 2 | 必须的 | 创建封面页面、基础文档、色板 |
| [component-creation.md](references/component-creation.md) | 3 | **必须** | 创建任何组件或变体 |
| [code-connect-setup.md](references/code-connect-setup.md) | 3–4 | 必须的 | 设置 Code Connect 或变量代码语法 |
| [naming-conventions.md](references/naming-conventions.md) | 任何 | 可选的 | 命名任何内容——变量、页面、变体、样式 |
| [error-recovery.md](references/error-recovery.md) | 任何 | **错误时必须** | 脚本失败、多步骤工作流恢复、清理被遗弃的工作流状态 |

---

## 11. 脚本

可重用插件 API 辅助函数。嵌入到 `use_figma` 调用中：

| 脚本 | 目的 |
|--------|---------|
| [inspectFileStructure.js](scripts/inspectFileStructure.js) | 发现所有页面、组件、变量、样式；返回完整清单 |
| [createVariableCollection.js](scripts/createVariableCollection.js) | 创建一个命名集合和模式；返回 `{collectionId, modeIds}` |
| [createSemanticTokens.js](scripts/createSemanticTokens.js) | 从标记映射创建别名语义变量 |
| [createComponentWithVariants.js](scripts/createComponentWithVariants.js) | 从变体矩阵构建组件集；处理网格布局 |
| [bindVariablesToComponent.js](scripts/bindVariablesToComponent.js) | 将设计标记绑定到所有组件视觉属性 |
| [createDocumentationPage.js](scripts/createDocumentationPage.js) | 创建一个带有标题 + 描述 + 章节结构的页面 |
| [validateCreation.js](scripts/validateCreation.js) | 验证创建的节点符合预期的计数、名称、结构 |
| [cleanupOrphans.js](scripts/cleanupOrphans.js) | 仅删除状态账本中提供的确切节点、变量和集合 ID |
