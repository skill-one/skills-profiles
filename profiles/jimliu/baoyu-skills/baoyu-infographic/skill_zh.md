# 信息图生成器

两个维度：**布局**（信息结构）× **风格**（视觉美学）。可自由组合任何布局与任何风格。

## 用户输入工具

当此技能提示用户时，遵循以下工具选择规则（优先级顺序）：

1. **优先使用**当前代理运行时暴露的**内置用户输入工具** — 例如，`AskUserQuestion`、`request_user_input`、`clarify`、`ask_user` 或任何等效工具。
2. **降级处理**：如果没有此类工具，则发出编号的纯文本消息，并要求用户回复选择的编号/答案以回答每个问题。
3. **批量处理**：如果工具支持每调用一次询问多个问题，则将所有适用问题合并为单个调用；如果仅支持单问题，则按优先级顺序逐一询问。

下方的具体 `AskUserQuestion` 引用仅为示例 — 在其他运行时中应替换为本地等效工具。

## 图像生成工具

当此技能需要渲染图像时，按以下顺序解析后端：

1. **当前请求覆盖** — 如果用户在当前消息中指定了特定后端，则使用该后端。
2. **保存的偏好设置** — 如果 `EXTEND.md` 将 `preferred_image_backend` 设置为当前可用的后端，则使用它。
3. **自动选择**（当偏好设置为 `auto`、未设置或固定后端不可用时）：
   - **Codex (`imagegen`)** — 首先，检查您的可用技能 / 工具清单。如果列出了名为 `imagegen` 的技能，则表示您正在 Codex 环境中运行，并且**必须**使用它：通过 `Skill` 工具以 `skill: "imagegen"` 调用，传递保存的提示文件内容（以及输出路径和 Codex `imagegen` 自身的参数）。Codex `imagegen` 是该运行时中的官方光栅后端，优先于任何非原生技能（例如，`baoyu-image-gen`），除非用户明确固定了不同的 `preferred_image_backend`。
   - **通过 `codex exec` 的 Codex (`codex-imagegen`)** — 如果当前运行时不暴露原生 `imagegen` 技能，但 `codex` CLI 在 `PATH` 上且 `codex login` 处于活动状态，则通过 `baoyu-image-gen --provider codex-cli` 路径路由（首选），或者 — 如果 `baoyu-image-gen` 不可用 — 调用捆绑的包装器直接。详细信息、参数和运行时发现程序位于 [references/codex-imagegen.md](references/codex-imagegen.md) — 仅在选中此分支时加载该文件。
   - **Cursor (`GenerateImage`)** — 如果运行时暴露了原生 `GenerateImage` 工具，则表示您正在 Cursor 环境中运行，其优先级与非原生技能与 Codex `imagegen` 相同。有两个硬性限制： (a) 它没有宽高比参数 — 在传递给 `description` 的提示文本中明确说明目标宽高比 / 尺寸；(b) 它不接受输出目录 — 它将保存到工具管理的位置，因此生成后需要将文件复制/移动到技能的预期输出路径（例如，`outputs/.../NN-xxx.png`）。参考图像放在 `reference_image_paths`。
   - **其他运行时原生工具** — 如果运行时暴露了不同的原生图像工具（例如，Hermes `image_generate`），则按相同方式使用。
   - 否则，如果恰好安装了一个非原生后端（例如，`baoyu-image-gen`），则使用它。
   - 否则（存在多个非原生后端且没有运行时原生工具），一次询问用户 — 与其他任何初始问题批量处理。
4. **如果都不可用**，则告知用户并询问如何继续。

**⛔ 永远不要用 SVG、HTML、canvas 或其他基于代码的渲染来替代光栅图像生成。** Codex `imagegen` 自己的描述说它应该用于“当输出应该是位图资源而不是仓库原生代码或矢量时”。如果您无法通过步骤 3 解析光栅后端，则应降级到步骤 4 并询问用户 — 不要无声地发出 SVG、写入内联 `<svg>` 标记或生成 HTML/CSS 艺术品作为替代。即使文章/部分看起来像“图表”，这也适用：调用此规则的消费技能已经决定需要光栅图像。

**⛔ 永远不要通过在生成的光栅图像上绘画来修复渲染的文本。** 不要使用 ImageMagick、Pillow、Canvas、SVG、HTML/CSS、OCR 脚本或任何其他程序化叠加来覆盖、重写、擦除、描边或替换已生成信息图中的标签、标题、注释、数据值或任何其他文本。如果文本错误或不清晰，请从更正后的提示中重新生成，切换到具有较少图像文本的布局，或询问用户要保留哪个不完美的候选者。

设置 `preferred_image_backend: ask` 会强制在每次运行时都提示步骤 3 的提示，无论是否可用后端。用户通过下方 **更改偏好设置** 部分更改固定后端。

**提示文件要求（硬性要求）**：在调用任何后端之前，将每个图像的完整最终提示写入 `prompts/` 下的独立文件（命名：`NN-{type}-[slug].md`）。后端接收提示文件（或其内容）；该文件是可重复性记录，并允许您在不重新生成提示的情况下切换后端。

上方的具体工具名称（`imagegen`、`GenerateImage`、`image_generate`、`baoyu-image-gen`）仅为示例 — 应按相同规则替换本地等效工具。

## 参考图像

用户可以提供参考图像来指导风格、调色板、构图或主题。

**输入**：通过 `--ref <files...>` 接收，或当用户提供文件路径 / 在对话中粘贴图像时接收。
- 文件路径 → 与输出一起复制到 `refs/NN-ref-{slug}.{ext}`
- 无路径粘贴的图像 → 按照上方的 **用户输入工具** 规则询问用户路径，或作为文本后备提取风格特征
- 无参考 → 跳过此部分

**使用模式**（按参考）：

| 使用 | 效果 |
|------|------|
| `direct` | 将文件作为参考图像传递给后端 |
| `style` | 提取风格特征（线条处理、纹理、情绪）并追加到提示正文 |
| `palette` | 从图像中提取十六进制颜色并追加到提示正文 |

**在 `prompts/infographic.md` 前置符中记录**，当存在参考时：

```yaml
references:
  - ref_id: 01
    filename: 01-ref-brand.png
    usage: direct
```

**生成时**：
- 验证每个引用文件是否存在于磁盘上
- 如果 `usage: direct` **且**选择的后端接受参考图像（例如，`baoyu-image-gen` 通过 `--ref`）→ 通过后端的 ref 参数传递文件
- 否则 → 将提取的 `style`/`palette` 特征嵌入提示文本中

## 确认策略

默认行为：**生成前确认**。

- 将显式技能调用、文件路径、匹配的快捷键关键字、`EXTEND.md` 默认值和文档中记录的默认组合视为**仅推荐输入**。它们都不授权跳过确认。
- **不要**在用户确认组合/宽高比/语言/后端选择之前开始步骤 5 或步骤 6。
- 仅在当前请求明确说明这样做时才跳过确认，例如：`--no-confirm`、"直接生成"、"不用确认"、"跳过确认"、"按默认出图" 或等效措辞。
- 如果明确跳过确认，则在生成之前在下一个面向用户的更新中声明所假设的组合/宽高比/语言/后端。

## 选项

| 选项 | 值 |
|------|------|
| `--layout` | 21 个选项（见布局库），默认：bento-grid |
| `--style` | 22 个选项（见风格库），默认：craft-handmade |
| `--aspect` | 命名：横向（16:9）、纵向（9:16）、方形（1:1）。自定义：任何 W:H 比率（例如，3:4、4:3、2.35:1） |
| `--lang` | en、zh、ja 等 |
| `--no-confirm` | 仅当用户明确请求直接生成而不确认时才跳过步骤 4 |
| `--ref <files...>` | 参考图像（文件路径）用于风格 / 调色板 / 构图 / 主题指导 |

## 布局库 (21)

| 布局 | 最佳用途 |
|------|----------|
| `linear-progression` | 时间线、流程、教程 |
| `binary-comparison` | A 与 B、前后、优缺点 |
| `comparison-matrix` | 多因素比较 |
| `hierarchical-layers` | 金字塔、优先级级别 |
| `tree-branching` | 类别、分类法 |
| `hub-spoke` | 中心概念及相关项目 |
| `structural-breakdown` | 分解视图、横截面 |
| `bento-grid` | 多个主题、概览（默认） |
| `iceberg` | 表面与隐藏方面 |
| `bridge` | 问题-解决方案 |
| `funnel` | 转化、过滤 |
| `isometric-map` | 空间关系 |
| `dashboard` | 指标、KPI |
| `periodic-table` | 分类集合 |
| `comic-strip` | 故事、序列 |
| `story-mountain` | 情节结构、张力弧 |
| `jigsaw` | 相互连接的部分 |
| `venn-diagram` | 重叠概念 |
| `winding-roadmap` | 旅程、里程碑 |
| `circular-flow` | 循环、重复过程 |
| `dense-modules` | 高密度模块、数据丰富的指南 |

完整定义位于 `references/layouts/<layout>.md`。

## 风格库 (22)

| 风格 | 描述 |
|------|------|
| `craft-handmade` | 手绘、纸艺（默认） |
| `claymation` | 3D 沥青人物、定格动画 |
| `kawaii` | 日本可爱、粉彩 |
| `storybook-watercolor` | 柔和绘画、异想天开 |
| `chalkboard` | 黑板上的粉笔 |
| `cyberpunk-neon` | 霓虹光、未来主义 |
| `bold-graphic` | 漫画风格、半色调 |
| `aged-academia` | 复古科学、棕褐色 |
| `corporate-memphis` | 平面矢量、鲜艳 |
| `technical-schematic` | 蓝图、工程 |
| `origami` | 折纸、几何 |
| `pixel-art` | 复古 8 位 |
| `ui-wireframe` | 灰度界面模型 |
| `subway-map` | 交通图 |
| `ikea-manual` | 最小线艺术 |
| `knolling` | 有组织的平面堆放 |
| `lego-brick` | 玩具砖结构 |
| `pop-laboratory` | 蓝图网格、坐标标记、实验室精度 |
| `morandi-journal` | 手绘涂鸦、暖莫兰迪色调 |
| `retro-pop-grid` | 1970 年复古流行艺术、瑞士网格、粗轮廓 |
| `hand-drawn-edu` | 马卡龙粉彩、手绘抖动、火柴人 |
| `retro-popup-pop` | 复古弹出拼贴、复古 UI、粗轮廓、平面流行颜色 |

完整定义位于 `references/styles/<style>.md`。

## 推荐组合

| 内容类型 | 布局 + 风格 |
|----------|--------------|
| 时间线/历史 | `linear-progression` + `craft-handmade` |
| 步骤式 | `linear-progression` + `ikea-manual` |
| A 与 B | `binary-comparison` + `corporate-memphis` |
| 层级 | `hierarchical-layers` + `craft-handmade` |
| 重叠 | `venn-diagram` + `craft-handmade` |
| 转化 | `funnel` + `corporate-memphis` |
| 循环 | `circular-flow` + `craft-handmade` |
| 技术 | `structural-breakdown` + `technical-schematic` |
| 指标 | `dashboard` + `corporate-memphis` |
| 教育 | `bento-grid` + `chalkboard` |
| 旅程 | `winding-roadmap` + `storybook-watercolor` |
| 类别 | `periodic-table` + `bold-graphic` |
| 产品指南 | `dense-modules` + `morandi-journal` |
| 技术指南 | `dense-modules` + `pop-laboratory` |
| 时尚指南 | `dense-modules` + `retro-pop-grid` |
| 复古流行指南 | `dense-modules` + `retro-popup-pop` |
| 教育图表 | `hub-spoke` + `hand-drawn-edu` |
| 流程教程 | `linear-progression` + `hand-drawn-edu` |

默认组合：`bento-grid` + `craft-handmade`（仅作为降级推荐 — 根据[确认策略](#confirmation-policy)，默认值永远不会绕过步骤 4）。

## 关键字快捷方式

当用户的输入包含这些关键字时，使用映射的布局作为步骤 3 的主要推荐，并将列出的风格提升到步骤 3 列表的顶部。跳过基于内容的布局推断以匹配关键字。将任何 `Prompt Notes` 追加到步骤 5 的提示中。

| 用户关键字 | 布局 | 推荐风格 | 默认宽高比 | 提示备注 |
|----------|------|----------|------------|----------|
| 高密度信息大图 / high-density-info | `dense-modules` | `morandi-journal`, `pop-laboratory`, `retro-pop-grid`, `retro-popup-pop` | 纵向 | — |
| 信息图 / infographic | `bento-grid` | `craft-handmade` | 横向 | 极简：干净的画布、充足的空白、无复杂的背景纹理。仅使用简单的卡通元素和图标。 |

## 输出结构

```
infographic/{topic-slug}/
├── source-{slug}.{ext}
├── analysis.md
├── structured-content.md
├── prompts/infographic.md
└── infographic.png
```

Slug：2-4 个单词的 kebab-case 来自主题。冲突：追加 `-YYYYMMDD-HHMMSS`。

## 核心原则

- 忠实保留源数据 — 不进行总结或重述（但在包含输出之前**移除任何凭证、API 密钥、令牌或机密信息**）
- 在构建内容之前定义学习目标
- 为视觉传达构建结构（标题、标签、视觉元素）

## 工作流程

### 步骤 1：设置与分析

**1.1 加载偏好设置 (EXTEND.md)**

按优先级顺序检查 EXTEND.md — 第一个找到的将获胜：

| 优先级 | 路径 | 范围 |
|------|------|------|
| 1 | `.baoyu-skills/baoyu-infographic/EXTEND.md` | 项目 |
| 2 | `${XDG_CONFIG_HOME:-$HOME/.config}/baoyu-skills/baoyu-infographic/EXTEND.md` | XDG |
| 3 | `$HOME/.baoyu-skills/baoyu-infographic/EXTEND.md` | 用户主目录 |

| 结果 | 操作 |
|------|------|
| 找到 | 读取、解析、显示一行摘要 |
| 未找到 | 使用 `AskUserQuestion`（见 `references/config/first-time-setup.md`）询问用户 |

EXTEND.md 支持：首选布局/风格、默认宽高比、语言偏好、首选图像后端、自定义风格定义。

Schema: `references/config/preferences-schema.md`

**1.2 分析内容 → `analysis.md`**

1. 保存源内容（文件路径或粘贴 → `source.md`）
   - **备份规则**：如果 `source.md` 存在，则重命名为 `source-backup-YYYYMMDD-HHMMSS.md`
2. 分析：主题、数据类型、复杂性、语气、受众
3. 检测源语言和用户语言
4. 从用户输入中提取设计指令
5. 保存分析
   - **备份规则**：如果 `analysis.md` 存在，则重命名为 `analysis-backup-YYYYMMDD-HHMMSS.md`

见 `references/analysis-framework.md` 了解详细格式。

### 步骤 2：生成结构化内容 → `structured-content.md`

将内容转换为信息图结构：
1. 标题和学习目标
2. 带有：关键概念、内容（原文）、视觉元素、文本标签的章节
3. 数据点（所有统计数据/引言精确复制）
4. 来自用户输入的设计指令

**规则**：仅使用 Markdown。不添加新信息。忠实保留数据。从输出中移除任何凭证或机密信息。

见 `references/structured-content-template.md` 了解详细格式。

### 步骤 3：推荐组合

**3.1 首先检查关键字快捷方式**：如果用户输入匹配 **关键字快捷方式** 表中的关键字，则使用关联的布局作为主要推荐，并将关联的风格作为步骤 3 列表中的首选推荐。跳过基于内容的布局推断。

**3.2 否则**，根据以下内容推荐 3-5 个布局×风格的组合：
- 数据结构 → 匹配的布局
- 内容语气 → 匹配的风格
- 受众期望
- 用户设计指令

### 步骤 4：确认选项

**硬性门槛**：根据 [确认策略](#confirmation-policy) 此步骤是强制性的 — 步骤 5–6 不能在此处确认之前开始（或当前请求中明确选择使用 `--no-confirm` / 等效措辞退出）。

按照此文件顶部的 [用户输入工具](#user-input-tools) 规则，询问用户确认以下问题（如果运行时支持多个问题，则将它们批量为一个调用；否则按优先级顺序逐一询问）。

| 优先级 | 问题 | 当... | 选项 |
|------|------|------|------|
| 1 | **组合** | 总是 | 3+ 布局×风格组合及其理由 |
| 2 | **宽高比** | 总是 | 命名预设（横向/纵向/方形）或自定义 W:H 比率（例如，3:4、4:3、2.35:1） |
| 3 | **语言** | 仅当源 ≠ 用户语言时 | 文本内容的语言 |
| 4 | **图像后端** | 仅当 `## 图像生成工具` 规则的步骤 3 需要询问时（无运行时原生工具且存在多个非原生后端，或 `preferred_image_backend: ask`） | 可用后端 |

### 步骤 5：生成提示 → `prompts/infographic.md`

**备份规则**：如果 `prompts/infographic.md` 存在，则重命名为 `prompts/infographic-backup-YYYYMMDD-HHMMSS.md`

组合：
1. 来自 `references/layouts/<layout>.md` 的布局定义
2. 来自 `references/styles/<style>.md` 的风格定义
3. 来自 `references/base-prompt.md` 的基础模板
4. 来自步骤 2 的结构化内容
5. 所有确认语言的文本

**宽高比解析**用于 `{{ASPECT_RATIO}}`：
- 命名预设 → 比率字符串：横向→`16:9`，纵向→`9:16`，方形→`1:1`
- 自定义 W:H 比率 → 使用原样（例如，`3:4`、`4:3`、`2.35:1`）

### 步骤 6：生成图像

1. 按照此文件顶部的 `## 图像生成工具` 规则解析后端。
2. 确保完整的最终提示在调用后端之前持久化到 `prompts/infographic.md`（已在步骤 5 中写入） — 该文件是可重复性记录。
3. **检查现有文件**：在生成之前，检查 `infographic.png` 是否存在
   - 如果存在：重命名为 `infographic-backup-YYYYMMDD-HHMMSS.png`
4. 使用提示文件和输出路径调用所选后端。
   - **`codex-imagegen` 调用**：当规则解析为 `codex-imagegen` 时，见 [references/codex-imagegen.md](references/codex-imagegen.md) 了解调用契约（首选 `baoyu-image-gen --provider codex-cli` 路径、运行时包装器发现、参数说明、stdout 模式、批量语义）。
5. 失败时，自动重试一次

文本校正策略：

- 如果标签、标题、注释、数据值或任何其他渲染的文本拼写错误、混乱、难以阅读或视觉上较弱，**不要**用代码修补位图。
- 对于文本校正重新生成，请编写新的提示文件和新的输出路径，以便保留有缺陷的候选者以供比较。
- 后处理仅限于裁剪、调整大小、压缩或格式转换，这些操作不会改变文本或主要构图。

### 步骤 7：输出摘要

报告：主题、布局、风格、宽高比、语言、图像后端、输出路径、创建的文件。

## 参考文献

- `references/analysis-framework.md` - 分析方法
- `references/structured-content-template.md` - 内容格式
- `references/base-prompt.md` - 提示模板
- `references/layouts/<layout>.md` - 21 个布局定义
- `references/styles/<style>.md` - 21 个风格定义

## 更改偏好设置

EXTEND.md 位于步骤 1.1 中第一个匹配的路径。更改它的三种方式：

- **直接编辑** — 打开 EXTEND.md 并更改字段。完整 schema: `references/config/preferences-schema.md`。
- **交互式重新配置** — 删除 EXTEND.md（或询问“重新配置 baoyu-infographic 偏好设置” / “重新配置”） — 下一次运行会重新触发首次设置。
- **常见的单行编辑**：
  - `preferred_image_backend: auto` — 默认；运行时原生工具获胜，降级到唯一安装的后端，仅在存在多个非原生后端时询问。
  - `preferred_image_backend: codex-imagegen` — 固定到 Codex 的内置。
  - `preferred_image_backend: baoyu-image-gen` — 固定到 baoyu-image-gen 技能。
  - `preferred_image_backend: ask` — 每次运行都提示后端。
  - `preferred_layout: dense-modules`, `preferred_style: morandi-journal`, `preferred_aspect: portrait`, `language: zh` — 调整步骤 3 的推荐和步骤 4 的默认值（根据 [确认策略](#confirmation-policy)，这些永远不会绕过步骤 4）。
