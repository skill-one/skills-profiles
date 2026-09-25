# 铅笔设计技能

在铅笔中设计生产级 UI，并从它们生成干净、可维护的代码。此技能强制执行设计系统重用、变量使用、布局正确性、视觉验证和设计到代码工作流的最佳实践。

## 何时使用此技能

- 在 `.pen` 文件中设计屏幕、页面或组件
- 从铅笔设计生成代码（React、Next.js、Vue、Svelte、HTML/CSS）
- 在铅笔中构建或扩展设计系统
- 在铅笔和代码之间同步设计令牌（Tailwind v4 `@theme`、shadcn/ui 令牌）
- 将现有代码导入铅笔设计
- 使用任何铅笔 MCP 工具（`pencil_batch_design`、`pencil_batch_get` 等）

## 严格规则

这些规则针对最常见的代理错误。违反它们会产生不一致、难以维护且生成糟糕代码的设计。

### 规则 1：始终重用设计系统组件

**永远不要从头开始创建一个组件，当设计文件中已经存在一个时。**

在插入任何元素之前，你必须：
1. 调用 `pencil_batch_get` 并使用 `patterns: [{ reusable: true }]` 列出所有可重用的组件
2. 在结果中搜索与你需要匹配的组件（按钮、卡片、输入、导航等）
3. 如果存在匹配项，使用 `I(parent, { type: "ref", ref: "<componentId>" })` 作为 `ref` 实例插入它
4. 通过更新其子代来定制实例，使用 `U(instanceId + "/childId", { ... })`
5. 只有在没有合适的可重用组件时，才从头开始创建新组件

有关详细工作流的参考，请参阅 [references/design-system-components.md](references/design-system-components.md)。

### 规则 2：始终使用变量而不是硬编码值

**当存在变量时，永远不要硬编码颜色、边框半径、间距或排版值。**

在应用任何样式值之前，你必须：
1. 调用 `pencil_get_variables` 读取所有定义的设计令牌
2. 将你的预期值映射到现有变量（例如，使用 `primary` 而不是 `#3b82f6`，使用 `radius-md` 而不是 `6`）
3. 使用变量引用而不是原始值应用值
4. 在生成代码时，使用 Tailwind v4 语义实用类（例如，`bg-primary`、`text-foreground`、`rounded-md`）。永远不要使用任意值语法（`bg-[#3b82f6]`、`text-[var(--primary)]`、`rounded-[6px]`）

有关详细工作流的参考，请参阅 [references/variables-and-tokens.md](references/variables-and-tokens.md)。

### 规则 3：防止文本和内容溢出

**永远不要允许文本或子元素溢出其父元素或画板。**

对于每个文本元素和容器：
1. 设置适当的文本换行和截断
2. 限制宽度为父边界，尤其是在移动屏幕上（通常为 375px 宽）
3. 在自动布局框架内的文本元素上使用 `"fill_container"` 设置宽度
4. 插入内容后，调用 `pencil_snapshot_layout` 并使用 `problemsOnly: true` 检测剪切/溢出
5. 在继续之前修复任何报告的问题

有关详细工作流的参考，请参阅 [references/layout-and-text-overflow.md](references/layout-and-text-overflow.md)。

### 规则 4：每个部分都要进行视觉验证

**在构建部分或屏幕后，永远不要跳过视觉验证。**

完成每个逻辑部分（页眉、英雄部分、侧边栏、表单、卡片网格等）后：
1. 对部分或整个屏幕节点调用 `pencil_get_screenshot`
2. 分析截图以检查：对齐问题、间距不一致、文本溢出、视觉故障、缺失内容
3. 调用 `pencil_snapshot_layout` 并使用 `problemsOnly: true` 捕获剪切和重叠
4. 修复发现的问题，然后再进入下一个部分
5. 当整个设计完成时，进行一次最终的全屏截图

有关详细工作流的参考，请参阅 [references/visual-verification.md](references/visual-verification.md)。

### 规则 5：重用现有资源（标志、图标、图片）

**当文档中已经存在一个时，永远不要生成新的标志或复制资源。**

在生成任何图像或标志之前：
1. 调用 `pencil_batch_get` 并按名称模式搜索现有图像/标志节点（例如，`patterns: [{ name: "logo|brand|icon" }]`）
2. 如果在文档的其他位置（另一个画板/屏幕）存在匹配的资产，使用 `C()`（复制）操作复制它
3. 只有对于文档中确实不存在的全新图像，才使用 `G()`（生成）操作
4. 对于标志特别说明：始终从现有实例复制，永远不要重新生成

有关详细工作流的参考，请参阅 [references/asset-reuse.md](references/asset-reuse.md)。

### 规则 6：始终加载 `frontend-design` 技能

**在铅笔中设计或从铅笔生成代码之前，永远不要加载 `frontend-design` 技能。**

`frontend-design` 技能提供了防止通用、千篇一律 UI 的美学方向和设计质量标准。你必须：
1. 在任何铅笔设计或代码生成任务的开始时加载 `frontend-design` 技能
2. 遵循其设计思维过程：理解目的、承诺大胆的美学方向、考虑差异化
3. 应用其关于排版、颜色、运动、空间构图和视觉细节的指南——无论是在铅笔中设计还是在铅笔设计中生成代码时
4. 永远不要产生通用的 AI 美学（过时的字体、陈词滥调的配色方案、可预测的布局）

这适用于两个方向：
- **铅笔设计任务**：使用该技能的美学指南来指导布局、排版、颜色和构图选择在 .pen 文件中
- **从铅笔生成代码**：使用该技能的指南确保生成的代码包括独特的排版、有意为之的颜色主题、运动/动画和精致的视觉细节——而不仅仅是设计树机械的翻译

## 设计工作流

### 开始新设计

```
0. 加载 `frontend-design` 技能   -> 获取美学方向和设计质量标准
1. pencil_get_editor_state        -> 理解文件状态，获取 schema
2. pencil_batch_get (reusable)    -> 发现设计系统组件
3. pencil_get_variables           -> 读取设计令牌
4. pencil_get_guidelines          -> 获取相关设计规则
5. pencil_get_style_guide_tags    -> (可选) 获取样式灵感
6. pencil_get_style_guide         -> (可选) 应用样式方向
7. pencil_find_empty_space_on_canvas -> 为新屏幕查找空间
8. pencil_batch_design            -> 构建设计（按部分）
9. pencil_get_screenshot          -> 视觉验证每个部分
10. pencil_snapshot_layout        -> 检查布局问题
```

### 按部分构建

对于屏幕的每个部分（页眉、内容区域、页脚、侧边栏、等）：

1. **计划** - 确定要重用的设计系统组件
2. **构建** - 作为 `ref` 实例插入组件，使用变量应用样式
3. **验证** - 截图部分 + 检查布局问题
4. **修复** - 解决任何溢出、对齐或间距问题
5. **继续** - 只有在验证通过后才能进入下一个部分

### 设计到代码工作流

有关完整工作流的参考，请参阅 [references/design-to-code-workflow.md](references/design-to-code-workflow.md)。
有关完整的铅笔到 Tailwind 映射表的参考，请参阅 [references/tailwind-shadcn-mapping.md](references/tailwind-shadcn-mapping.md)。
有关多画板响应式代码生成的参考，请参阅 [references/responsive-breakpoints.md](references/responsive-breakpoints.md)。

总结：
1. 加载 `frontend-design` 技能以获取美学方向
2. 调用 `pencil_get_guidelines` 并使用主题 `"code"` 和 `"tailwind"`
3. 调用 `pencil_get_variables` 将设计令牌映射到 Tailwind `@theme` 声明
4. 使用 `pencil_batch_get` 读取设计树
5. 将可重用的铅笔组件映射到 shadcn/ui 组件（按钮、卡片、输入、等）
6. 使用语义 Tailwind 类生成代码（`bg-primary`、`rounded-md`），永远不要使用任意值
7. 应用 `frontend-design` 指南：独特的排版、有意为之的颜色、运动、空间构图
8. 使用 CVA 进行自定义组件变体，`cn()` 进行类合并，Lucide 用于图标

## MCP 工具快速参考

| 工具 | 何时使用 |
|------|-------------|
| `pencil_get_editor_state` | 首次调用 - 理解文件状态和获取 .pen schema |
| `pencil_batch_get` | 读取节点，搜索组件（`reusable: true`），检查结构 |
| `pencil_batch_design` | 插入、复制、更新、替换、移动、删除元素；生成图像 |
| `pencil_get_variables` | 读取设计令牌（颜色、半径、间距、字体） |
| `pencil_set_variables` | 创建或更新设计令牌 |
| `pencil_get_screenshot` | 任何节点的视觉验证 |
| `pencil_snapshot_layout` | 检测剪切、溢出、重叠元素 |
| `pencil_get_guidelines` | 获取设计规则：`code`、`table`、`tailwind`、`landing-page`、`design-system` |
| `pencil_find_empty_space_on_canvas` | 为新屏幕/框架查找空间 |
| `pencil_get_style_guide_tags` | 浏览可用的样式方向 |
| `pencil_get_style_guide` | 获取特定样式灵感 |
| `pencil_search_all_unique_properties` | 跨文档审核属性值 |
| `pencil_replace_all_matching_properties` | 批量更新属性（例如，交换颜色） |
| `pencil_open_document` | 打开 .pen 文件或创建新文档 |

## 要避免的常见错误

| 错误 | 正确方法 |
|---------|-----------------|
| 从头开始创建按钮 | 搜索现有按钮组件，作为 `ref` 插入 |
| 使用 `fill: "#3b82f6"` | 使用变量：引用 `primary` 或相应变量 |
| 使用 `cornerRadius: 8` | 使用变量：引用 `radius-md` 或相应变量 |
| 在代码中生成 `bg-[#3b82f6]` | 使用语义 Tailwind 类：`bg-primary` |
| 在代码中生成 `text-[var(--primary)]` | 使用语义 Tailwind 类：`text-primary` |
| 在代码中生成 `rounded-[6px]` | 使用语义 Tailwind 类：`rounded-md` |
| 在 className 中使用 `var(--primary)` | 使用语义 Tailwind 类：`bg-primary` 或 `text-primary` |
| 不检查溢出 | 在每个部分后调用 `pencil_snapshot_layout(problemsOnly: true)` |
| 跳过截图 | 在每个部分后调用 `pencil_get_screenshot` |
| 生成新标志 | 使用 `C()` 从另一个画板复制现有标志 |
| 整个屏幕构建后检查 | 按部分构建和验证 |
| 忽略 `pencil_get_guidelines` | 在开始之前始终调用相关主题 |
| 使用 `tailwind.config.ts` | 使用 CSS `@theme` 块（Tailwind v4） |
| 在代码中使用 Material Icons | 映射到 Lucide 图标（`<Search />`、`<ArrowRight />` 等） |
| 跳过 `frontend-design` 技能 | 在铅笔设计或生成代码之前始终加载它 |
| 通用 AI 美学（Inter 字体、紫色渐变） | 遵循 `frontend-design` 指南以获得独特、有意为之的设计 |

## 资源

- [Pencil 文档](https://docs.pencil.dev)
- [Pencil Prompt 画廊](https://www.pencil.dev/prompts)
- [设计为代码](https://docs.pencil.dev/core-concepts/design-as-code)
- [变量](https://docs.pencil.dev/core-concepts/variables)
- [组件](https://docs.pencil.dev/core-concepts/components)
- [设计到代码](https://docs.pencil.dev/design-and-code/design-to-code)
- [样式和 UI 套件](https://docs.pencil.dev/design-and-code/styles-and-ui-kits)
