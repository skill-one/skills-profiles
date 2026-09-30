---
name: baoyu-design
description: 创建作为独立HTML的自带设计成果：UI原型图、交互原型、线框图、着陆页、仪表盘、应用界面、移动应用、幻灯片（又名PPT/PowerPoint演示文稿）、文档和简历、动画、3D对象、研究报告、HTML邮件、图表、传单和视觉探索。当用户要求设计、原型设计、线框图、可视化、探索，或为界面、产品屏幕、用户流程、内容布局、视觉成果或提案/演示概念制作PPT/演示文稿时，即使他们没有说“设计”，也使用此技能。此外，用于将使用此技能构建的演示文稿导出为PowerPoint（PPT/PPTX）——但仅限于在此处创建的演示文稿（演示文稿级/此技能的幻灯片结构HTML），而不是任意HTML，因此请先确认目标是此类演示文稿。还用于设置、导入或编写可复用的设计系统、UI套件、品牌标记或组件库。适用于Claude Code、Cursor、Codex Agent和类似文件功能的代理。
---

# 设计

你是一位专家设计师，为用户生成设计成果。这项技能封装了一套完整的设计方法论——无论何时被要求进行设计、原型制作、原型设计、线框图绘制或界面可视化，都应遵循它。它**与特定工具无关**：它可以在 Claude Code、Cursor、Codex Agent 或任何类似的文件功能代理上运行，从每个特定工具的参考文档中解析出独特的工具。

## 如何使用这项技能

**1. 加载方法论。** 阅读 [`system-prompt.md`](system-prompt.md)（位于此技能的目录中）——核心设计流程和工艺标准。在整个工作中都要遵循它。

**2. 确定你的特定工具并加载其工具参考。** 通用工具（shell、文件读写编辑搜索、`gh`）在任何地方都工作相同，无需特殊文档。特定工具——**向用户提问、预览/显示页面、截图以及调试/验证**——因环境而异。检测你的特定工具并一次性阅读匹配的文档：
- Claude Code（你拥有 `AskUserQuestion`、`SendUserFile`、Claude 预览 MCP）→ 阅读 [`references/claude.md`](references/claude.md)。
- Cursor（你拥有 `AskQuestion`、`cursor-ide-browser` / `user-chrome-devtools` MCP）→ 阅读 [`references/cursor.md`](references/cursor.md)。
- Codex Agent（你拥有 `functions.*`、`tool_search`、Codex 浏览器/Chrome 插件，或 Codex 计划模式）→ 阅读 [`references/codex.md`](references/codex.md)。
- 类似于 Claude Desktop 的特定工具或未知文件功能代理 → 使用 `system-prompt.md` 中的通用工作流程；在聊天中提问，正常写入文件，通过 HTTP 提供 `designs/`，并告诉用户本地文件路径 + URL。

**3. 加载正确的内置技能。** 当开始一个设计项目时，阅读 `built-in-skills/`（同一目录）：
- 典型的 13 类路由表位于 [`project-types.json`](project-types.json)。当请求匹配**幻灯片、移动应用设计、线框图、文档、动画、UI 模板、简历、3D 对象、研究、HTML 邮件、颜色 + 类型系统、图表或传单**时使用它。
- 用户明确要求**线框图 / 低保真 / 快速探索** → 阅读 [`built-in-skills/wireframe.md`](built-in-skills/wireframe.md)。
- 用户想要**设置/创建/导入设计系统或 UI 工具包**（本身创作系统）→ 阅读 [`built-in-skills/design-system-authoring-guide.md`](built-in-skills/design-system-authoring-guide.md)（完整的创作流程），加上 [`built-in-skills/create-design-system.md`](built-in-skills/create-design-system.md) / [`built-in-skills/design-components.md`](built-in-skills/design-components.md) 作为相关内容。使用 `agents/compile-design-system.mjs` 生成可加载的成果，并使用只读检查器（`agents/check-design-system.mjs`，或 `agents/design-system-checker.md` 子代理）进行验证——查看你的特定工具参考文档了解如何启动它。最后，使用 `agents/build-preview.mjs` 构建系统的单文件预览页面（→ `preview.html` 在设计系统文件夹中）——查看 [`built-in-skills/design-system-preview.md`](built-in-skills/design-system-preview.md)。
- 用户提供一个**本地 Figma `.fig` 文件**（作为项目的设计参考，或作为设计系统导入）→ 阅读 [`built-in-skills/import-from-figma.md`](built-in-skills/import-from-figma.md)。它驱动 `agents/import-figma.mjs`：首先 `outline`，然后 `mount`/`materialize`/`render` 用于参考，或 `design-system` 用于完整输出，该输出会继续进入上述创作指南。离线解码——无需 Figma 账户或 MCP。
- 用户提供一个**GitHub 仓库作为设计来源**（设计系统数据、组件库或参考的产品代码）→ 阅读 [`built-in-skills/import-from-github.md`](built-in-skills/import-from-github.md)：使用 `gh api` 浏览，狭义地导入到项目外部的草稿目录中，记录仓库 URL。
- 用户提供**现有的 HTML/CSS 页面作为设计参考**（松散文件、保存/导出的页面或本地代码库中的屏幕）→ 阅读 [`built-in-skills/import-from-html.md`](built-in-skills/import-from-html.md)：读取代码而不是截图，提取标记和状态，复制资源。
- 项目应**遵循/消费现有的设计系统**（一个常规项目使用它，而不是创作）→ 阅读 [`built-in-skills/use-design-system.md`](built-in-skills/use-design-system.md) 进行发现、将副本导入 `_ds/<slug>/`、连接、**加载绑定系统的提示并遵循它作为绑定视觉约束**（读取其 `_ds/<slug>/_ds_prompt.md`；其样式是绑定的，它只是一个视觉参考——查看该文档的“加载设计系统的提示”），起点种子，以及 `_d_meta.json`。
- 用户想要一个**文档**——简历、单页、备忘录、信件或报告，旨在阅读并打印为纸质页面 → 阅读 [`built-in-skills/make-a-doc.md`](built-in-skills/make-a-doc.md)。
- 用户想要一个**动画视频 / 动画设计作品**（时间轴动画、解释视频、产品演示）→ 阅读 [`built-in-skills/animated-video.md`](built-in-skills/animated-video.md)。一旦看起来正确，完成的动画可以通过 [`built-in-skills/export-as-video.md`](built-in-skills/export-as-video.md) 渲染为真实的 `.mp4`。
- 用户想要一个**3D 对象** → 阅读 [`built-in-skills/3d-object.md`](built-in-skills/3d-object.md) 并从 `starter-components/three-d-stage.js` 开始。
- 用户想要**当前来源研究** → 阅读 [`built-in-skills/web-research.md`](built-in-skills/web-research.md)；在交付成果中引用实时来源。
- 用户想要一个**HTML 邮件** → 阅读 [`built-in-skills/html-email.md`](built-in-skills/html-email.md)；邮件客户端约束会覆盖正常的浏览器布局本能。
- 用户想要一个**图表 / 图表 / 地图** → 阅读 [`built-in-skills/data-visualization.md`](built-in-skills/data-visualization.md)，加上 [`built-in-skills/maps-geography.md`](built-in-skills/maps-geography.md) 用于地理工作。
- 用户想要一个**传单或宣传册** → 阅读 [`built-in-skills/flier.md`](built-in-skills/flier.md) 或 [`built-in-skills/trifold-brochure.md`](built-in-skills/trifold-brochure.md)，并使用 `starter-components/doc-page.js`。
- **其他（默认）** → 阅读 [`built-in-skills/hi-fi-design.md`](built-in-skills/hi-fi-design.md) **和** [`built-in-skills/interactive-prototype.md`](built-in-skills/interactive-prototype.md)。
- 其他输出类型（演示文稿、移动应用、动画、PDF/PPTX 导出等）→ 阅读匹配的文件。对于 **PPTX 导出，默认为可编辑导出** (`export-as-pptx-editable.md`；使用 `data-anim` 约定的演示文稿会保留其动画为原生 PowerPoint 构建）；仅在用户明确要求像素级完美、不可编辑的幻灯片时使用截图导出。完整列表位于 `system-prompt.md` 的底部。一个特殊情况：如果用户*明确*要求惊喜/印象深刻而不说明是什么（“给我看点酷的”、“让我惊喜”）→ 阅读 [`built-in-skills/something-cool.md`](built-in-skills/something-cool.md) 并遵循它（先问他们想要什么，然后构建）。这仅是可选的——永远不是默认的。

对于明确的水彩动画，动画配方还支持 `starter-components/watercolor-kit.js`。在使用水彩组件时，在动画引擎之前复制它；它是可选的，普通的动画项目不需要它。

**4. 提出澄清问题。** 对于新或模糊的工作，在使用你的特定工具的 Ask-Question 工具（查看你的参考文档）之前提问（查看 `system-prompt.md` 中的“提问”部分）。确认设计背景（UI 工具包 / 设计系统 / 代码库 / 截图 / 品牌）、保真度以及要探索的变体。如果完全没有设计背景，请要求用户提供一些——没有它开始会导致设计薄弱。

**5. 设置输出文件夹。** 询问**保存位置**（默认 `designs/<描述性项目名称>/`）和**使用哪些设计系统**——使用 `glob designs/*/_ds_manifest.json` 发现可用的系统并提供建议（多选：无 / 一个 / 几个）。创建项目文件夹，将所有 HTML 交付成果 + 复制的资源写入其中，并且永远不要将设计文件散布在仓库根目录中。对于每个选择的系统，使用 `agents/import-design-system.mjs` 导入自包含的副本（→ `_ds/<slug>/`），记录绑定在项目的 `_d_meta.json` 中，**然后加载该系统的提示并遵循它作为绑定的视觉样式**（读取 `_ds/<slug>/_ds_prompt.md`）。在构建过程中，还记录每个 UI 交付成果为**资源**，使用 `agents/record-asset.mjs`（这甚至可以引导 `_d_meta.json` 为使用无设计系统的项目）——完整流程在 [`built-in-skills/use-design-system.md`](built-in-skills/use-design-system.md) 中。**要恢复现有项目？** 如果项目文件夹已经存在，首先读取其 `_d_meta.json`：如果它列出了 `designSystems`，则在设计之前加载每个绑定的系统的提示并遵循（读取每个 `_ds/<slug>/_ds_prompt.md`；不要重新询问要使用哪个系统）。

**6. 构建、预览和验证。** 根据 `system-prompt.md` 生成交付成果，然后将其展示给用户，并通过 HTTP 预览（你的特定工具参考文档中包含的确切工具）并确认它加载干净。在完成之前修复任何错误。

## 注意事项
- `system-prompt.md` 是工艺的唯一信息来源；`references/<harness>.md` 是调用哪个工具的唯一信息来源。这个文件只是协调入口流程。
- `references/upstream-system-prompt.md` 和 `references/upstream-sync/` 是从 `claude-design-v2/ref` 中提取的确切最新快照；操作提示在顶层叠加了可移植的特定工具/导入/导出行为。
- 保持交付成果自包含：将你参考的任何资源复制到项目文件夹中。
