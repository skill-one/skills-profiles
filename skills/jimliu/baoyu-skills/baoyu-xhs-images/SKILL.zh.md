---
name: baoyu-xhs-images
description: 生成包含12种视觉风格、8种布局和3种配色方案的图表图像卡片系列。将内容拆分为1-10张卡通风格的图像卡片，专为社交媒体互动优化。当用户提及“小红书图片”、“小红书种草”、“小绿书”、“微信图文”、“微信贴图”、“image cards”、“图片卡片”、“baoyu-xhs-images”或需要社交媒体图表系列时使用。
---

# 图像卡片系列生成器

将复杂内容分解为引人注目的图像卡片系列，提供多种样式选项。

## 用户输入工具

当此技能提示用户时，请遵循以下工具选择规则（优先级顺序）：

1. **优先使用**当前代理运行时暴露的**内置用户输入工具** — 例如，`AskUserQuestion`、`request_user_input`、`clarify`、`ask_user` 或任何等效工具。
2. **降级处理**：如果没有此类工具，则发出编号的纯文本消息，并要求用户回复选择的编号/答案以回答每个问题。
3. **批量处理**：如果该工具支持每调用一次询问多个问题，则将所有适用问题合并为单个调用；如果仅支持单问题，则按优先级顺序逐个询问。

下方的具体 `AskUserQuestion` 引用仅为示例 — 在其他运行时中应替换为本地等效工具。

## 图像生成工具

当此技能需要渲染图像时，按以下顺序解析后端：

1. **当前请求覆盖** — 如果用户在当前消息中指定了特定的后端，则使用它。
2. **保存的偏好设置** — 如果 `EXTEND.md` 将 `preferred_image_backend` 设置为当前可用的后端，则使用它。
3. **自动选择**（当偏好设置为 `auto`、未设置或固定的后端不可用时）：
   - **Codex (`imagegen`)** — 首先，检查您的可用技能/工具清单。如果列出了名为 `imagegen` 的技能，则表示您正在 Codex 环境中运行，并且**必须**使用它：通过 `Skill` 工具以 `skill: "imagegen"` 调用，并将保存的提示文件内容（包括输出路径和宽高比，根据 Codex `imagegen` 自身的参数）传递给它。Codex `imagegen` 是该运行时中的官方光栅后端，优先于任何非原生技能（例如，`baoyu-image-gen`），除非用户明确固定了不同的 `preferred_image_backend`。
   - **通过 `codex exec` 的 Codex (`codex-imagegen`)** — 如果当前运行时未暴露原生 `imagegen` 技能，但 `codex` CLI 位于 `PATH` 上且 `codex login` 处于活动状态，则通过 `baoyu-image-gen --provider codex-cli` 路由（首选），或者 — 如果 `baoyu-image-gen` 不可用 — 调用捆绑的包装器直接。详细信息、参数和运行时发现流程位于 [references/codex-imagegen.md](references/codex-imagegen.md) — 仅当选择此分支时加载该文件。
   - **Cursor (`GenerateImage`)** — 如果运行时暴露了原生 `GenerateImage` 工具，则表示您正在 Cursor 环境中运行，其优先级与非原生技能相同（与 Codex `imagegen` 相同）。有两个硬性限制：(a) 它没有宽高比参数 — 必须在作为 `description` 传递的提示文本中明确指定目标宽高比/尺寸；(b) 它不接受输出目录 — 它将保存到工具管理的位置，因此生成后需要将文件复制/移动到技能预期的输出路径（例如，`outputs/.../NN-xxx.png`）。参考图像放在 `reference_image_paths`。
   - **其他运行时原生工具** — 如果运行时暴露了不同的原生图像工具（例如，Hermes `image_generate`），则按相同方式使用它。
   - 否则，如果恰好安装了一个非原生后端（例如，`baoyu-image-gen`），则使用它。
   - 否则（存在多个非原生后端且没有运行时原生工具），一次询问用户 — 并与其他初始问题批量处理。
4. **如果都不可用**，则告知用户并询问如何继续。

**⛔ 永远不要用 SVG、HTML、canvas 或其他基于代码的渲染来替代光栅图像生成。** Codex `imagegen` 自己的描述说它应该用于“当输出应该是位图资源而不是仓库原生代码或矢量时”。如果您无法通过步骤 3 解析光栅后端，则转入步骤 4 并询问用户 — 不要默默发出 SVG、写入内联 `<svg>` 标记或生成 HTML/CSS 艺术作品作为替代。即使文章/部分看起来像“图表样式”，调用此规则的消费技能已经决定需要光栅图像。

**⛔ 永远不要通过在生成的光栅图像上绘画来修复渲染的文本。** 不要使用 ImageMagick、Pillow、Canvas、SVG、HTML/CSS、OCR 脚本或任何其他程序化叠加来覆盖、重写、擦除、描边或替换已生成图像卡片中的标题、正文、标签或任何其他文本。如果文本错误或不清晰，请从更正后的提示中重新生成，切换到卡片上文字较少的布局，或询问用户要保留哪个不完美的候选者。

设置 `preferred_image_backend: ask` 会强制在每次运行时都执行步骤 3 的提示，无论是否有可用后端。用户通过下方“## 更改偏好设置”部分更改固定的后端。

**提示文件要求（硬性要求）**：在调用任何后端之前，将每个图像的完整最终提示写入 `prompts/` 下的独立文件（命名：`NN-{type}-[slug].md`）。该文件是可重复性记录，并允许您在不重新生成提示的情况下切换后端。

上方的具体工具名称（`imagegen`、`GenerateImage`、`image_generate`、`baoyu-image-gen`）仅为示例 — 应按相同规则替换本地等效工具。

## 批量生成策略

在保存并验证当前生成组的所有提示文件后，默认按批量生成图像。

优先级顺序：

1. 如果选择的后端存在原生批处理/多任务接口，则使用它。每个任务必须保持自己的提示文件、输出路径、宽高比、会话 ID 和直接参考图像。
2. 如果没有原生批处理接口，但运行时可以发出并行工具调用，则一次派遣最多 `generation_batch_size` 张图像。默认：`4`。当前消息中的显式用户请求（例如 `--batch-size 4` 或“并行 4 张一起生成”）会覆盖 EXTEND.md。
3. 如果既没有原生批处理也没有并行工具调用可用，则按顺序生成。

规则：

- 尊重图像-1 锚链：首先生成图像 1，然后使用图像 1 作为参考批量生成图像 2+。
- 只有当为该批量选择的每个提示文件都存在于磁盘上时，才开始批量。
- 重新生成失败项一次，不要重新生成成功项。
- 不要使用子代理仅仅是为了并行化图像渲染。仅当用于单独的提示迭代或创意探索时才使用子代理。

## 确认策略

默认行为：**生成前确认**。

- 将显式技能调用、文件路径、匹配的信号/预设和 `EXTEND.md` 默认视为**建议输入**。它们都不授权跳过确认。
- **不要**在用户完成步骤 2 之前开始步骤 3。
- 仅当当前请求明确说明这样做时才跳过确认，例如：`--yes`、`"直接生成"`、`"不用确认"`、`"跳过确认"`、`"按默认出图"` 或等效措辞。
- 如果明确跳过确认，则在生成之前，在下一个面向用户更新中说明所假设的策略/样式/布局/调色板/数量/后端。

## 语言

在整个问题、进度、错误和完成摘要中用用户的语言回答。保持技术标记（样式名称、文件路径、代码）为英文。

## 选项

| 选项 | 描述 |
|------|------|
| `--style <name>` | 视觉样式（见下文“样式”） |
| `--layout <name>` | 信息布局（见下文“布局”） |
| `--palette <name>` | 颜色覆盖：macaron / warm / neon |
| `--preset <name>` | 样式 + 布局 + 可选调色板缩写（见下文“预设”；每个预设的提示片段在 `references/style-presets.md` 中） |
| `--ref <files...>` | 应用于图像 1 作为系列锚点的参考图像 |
| `--batch-size <n>` | 此运行的临时生成批量大小。默认：EXTEND.md 中的 `generation_batch_size`，否则为 4。钳位到 1-8。 |
| `--yes` | 非交互式：跳过所有确认，使用 EXTEND.md 或内置默认值，自动确认建议计划（路径 A） |

## 尺寸

三个独立的旋钮可以自由组合：

| 尺寸 | 控制 | 选项 |
|------|------|------|
| **样式** | 视觉美学（线条、装饰、渲染） | 12 种样式（见下文“样式”） |
| **布局** | 信息结构（密度、排列） | 8 种布局（见下文“布局”） |
| **调色板**（可选） | 颜色覆盖，替换样式的默认颜色 | macaron / warm / neon（见下文“调色板”） |

示例：`--style notion --layout dense` 制作知识卡片；添加 `--palette macaron` 可柔化颜色，而不会改变 notion 的渲染规则。`--preset` 是样式 + 布局的缩写。

**调色板行为**：无 `--palette` → 样式的内置颜色；`--palette <name>` → 仅覆盖颜色，渲染规则不变。某些样式声明了 `default_palette`（例如，sketch-notes 默认为 macaron）。

## 样式（12）

| 样式 | 描述 |
|------|------|
| `cute`（默认） | 可爱、甜美、少女风格 |
| `fresh` | 干净、清新、自然 |
| `warm` | 舒适、友好、易亲近 |
| `bold` | 高冲击力、引人注目 |
| `minimal` | 超级干净、精致 |
| `retro` | 复古、怀旧、时尚 |
| `pop` | 鲜艳、充满活力、引人注目 |
| `notion` | 极简手绘线条艺术、知识型 |
| `chalkboard` | 彩色粉笔在黑板上，教育性 |
| `study-notes` | 真实手写照片风格，蓝色笔 + 红色注释 + 黄色荧光笔 |
| `screen-print` | 粗犷的海报艺术，半色调纹理，有限颜色，象征性叙事 |
| `sketch-notes` | 手绘教育信息图表，macaron 柔粉在温暖米色上，摇摆线条 |

每样式规范：`references/presets/<style>.md`。

## 布局（8）

| 布局 | 描述 |
|------|------|
| `sparse`（默认） | 1-2 点，最大冲击力 |
| `balanced` | 3-4 点，标准 |
| `dense` | 5-8 点，知识卡片风格 |
| `list` | 列表/排名（4-7 项） |
| `comparison` | 并列对比 |
| `flow` | 流程/时间线（3-6 步） |
| `mindmap` | 中心辐射（4-8 分支） |
| `quadrant` | 四象限/圆形区域 |

布局规范：`references/elements/canvas.md`。

## 调色板（可选覆盖）

替换样式的颜色，同时保持渲染规则（线条处理、纹理）不变。

| 调色板 | 背景 | 区域颜色 | 强调色 | 感觉 |
|------|------|----------|--------|------|
| `macaron` | 温暖米色 #F5F0E8 | 蓝色 #A8D8EA，薰衣草 #D5C6E0，薄荷 #B5E5CF，桃子 #F8D5C4 | 橙珊瑚 #E8655A | 温柔、教育性 |
| `warm` | 柔和桃子 #FFECD2 | 橙色 #ED8936，陶土 #C05621，金色 #F6AD55，玫瑰 #D4A09A | 棕褐色 #A0522D | 地表色调、舒适 |
| `neon` | 深紫色 #1A1025 | 青色 #00F5FF，品红 #FF00FF，绿色 #39FF14，粉色 #FF6EC7 | 黄色 #FFFF00 | 高能量、未来感 |

调色板规范：`references/palettes/<palette>.md`。

## 预设（样式 + 布局快捷方式）

按场景分组的快速启动组合。使用 `--preset <name>` 或在步骤 2 中推荐。

**知识 & 学习**：

| 预设 | 样式 | 布局 | 最适合 |
|------|------|------|--------|
| `knowledge-card` | notion | dense | 干货知识卡、概念科普 |
| `checklist` | notion | list | 清单、排行榜 |
| `concept-map` | notion | mindmap | 概念图、知识脉络 |
| `swot` | notion | quadrant | SWOT 分析、四象限 |
| `tutorial` | chalkboard | flow | 教程步骤、操作流程 |
| `classroom` | chalkboard | balanced | 课堂笔记、知识讲解 |
| `study-guide` | study-notes | dense | 学习笔记、考试重点 |
| `hand-drawn-edu` | sketch-notes | flow | 手绘教程、流程图解 |
| `sketch-card` | sketch-notes | dense | 手绘知识卡 |
| `sketch-summary` | sketch-notes | balanced | 手绘总结、图文笔记 |

**生活方式 & 分享**：

| 预设 | 样式 | 布局 | 最适合 |
|------|------|------|--------|
| `cute-share` | cute | balanced | 少女风分享、日常种草 |
| `girly` | cute | sparse | 甜美封面、氛围感 |
| `cozy-story` | warm | balanced | 生活故事、情感分享 |
| `product-review` | fresh | comparison | 产品对比、测评 |
| `nature-flow` | fresh | flow | 健康流程、自然主题 |

**影响 & 意见**：

| 预设 | 样式 | 布局 | 最适合 |
|------|------|------|--------|
| `warning` | bold | list | 避坑指南、重要提醒 |
| `versus` | bold | comparison | 正反对比 |
| `clean-quote` | minimal | sparse | 金句、极简封面 |
| `pro-summary` | minimal | balanced | 专业总结、商务内容 |

**趋势 & 娱乐**：

| 预设 | 样式 | 布局 | 最适合 |
|------|------|------|--------|
| `retro-ranking` | retro | list | 复古排行、经典盘点 |
| `throwback` | retro | balanced | 怀旧分享 |
| `pop-facts` | pop | list | 趣味冷知识 |
| `hype` | pop | sparse | 炸裂封面、惊叹分享 |

**海报 & 编辑**：

| 预设 | 样式 | 布局 | 最适合 |
|------|------|------|--------|
| `poster` | screen-print | sparse | 海报风封面、影评书评 |
| `editorial` | screen-print | balanced | 观点文章、文化评论 |
| `cinematic` | screen-print | comparison | 电影对比、戏剧张力 |

完整提示片段定义：`references/style-presets.md`。

## 自动选择

匹配内容信号到最佳组合。第一个关键词出现所在的行获胜；如果没有匹配，则回退到 `cute-share`。

| 源中的信号 | 样式 | 布局 | 推荐预设 |
|----------|------|------|----------|
| beauty, fashion, cute, girl, pink | `cute` | sparse/balanced | `cute-share`, `girly` |
| health, nature, fresh, organic | `fresh` | balanced/flow | `product-review`, `nature-flow` |
| life, story, emotion, warm | `warm` | balanced | `cozy-story` |
| warning, important, must, critical | `bold` | list/comparison | `warning`, `versus` |
| professional, business, elegant | `minimal` | sparse/balanced | `clean-quote`, `pro-summary` |
| classic, vintage, traditional | `retro` | balanced | `throwback`, `retro-ranking` |
| fun, exciting, wow, amazing | `pop` | sparse/list | `hype`, `pop-facts` |
| knowledge, concept, productivity, SaaS | `notion` | dense/list | `knowledge-card`, `checklist` |
| education, tutorial, learning, classroom | `chalkboard` | balanced/dense | `tutorial`, `classroom` |
| notes, handwritten, study guide, realistic | `study-notes` | dense/list/mindmap | `study-guide` |
| movie, poster, opinion, editorial, cinematic | `screen-print` | sparse/comparison | `poster`, `editorial`, `cinematic` |
| hand-drawn, infographic, workflow, 手绘，图解 | `sketch-notes` | flow/balanced/dense | `hand-drawn-edu`, `sketch-card`, `sketch-summary` |

## 样式 × 布局矩阵

兼容性评分（✓✓ 高度推荐，✓ 工作良好，✗ 避免使用）。当用户选择非默认组合并且您想标记一个不良匹配时使用。

|              | sparse | balanced | dense | list | comparison | flow | mindmap | quadrant |
|--------------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| cute         | ✓✓ | ✓✓ | ✓  | ✓✓ | ✓  | ✓  | ✓  | ✓  |
| fresh        | ✓✓ | ✓✓ | ✓  | ✓  | ✓  | ✓✓ | ✓  | ✓  |
| warm         | ✓✓ | ✓✓ | ✓  | ✓  | ✓✓ | ✓  | ✓  | ✓  |
| bold         | ✓✓ | ✓  | ✓  | ✓✓ | ✓✓ | ✓  | ✓  | ✓✓ |
| minimal      | ✓✓ | ✓✓ | ✓✓ | ✓  | ✓  | ✓  | ✓  | ✓  |
| retro        | ✓✓ | ✓✓ | ✓  | ✓✓ | ✓  | ✓  | ✓  | ✓  |
| pop          | ✓✓ | ✓✓ | ✓  | ✓✓ | ✓✓ | ✓  | ✓  | ✓  |
| notion       | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ |
| chalkboard   | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓  | ✓✓ | ✓✓ | ✓  |
| study-notes  | ✗  | ✓  | ✓✓ | ✓✓ | ✓  | ✓  | ✓✓ | ✓  |
| screen-print | ✓✓ | ✓✓ | ✗  | ✓  | ✓✓ | ✓  | ✗  | ✓✓ |
| sketch-notes | ✓  | ✓✓ | ✓✓ | ✓✓ | ✓  | ✓✓ | ✓✓ | ✓  |

## 提纲策略

三种差异化方法 — 每种方法产生结构上不同的提纲。工作流程推荐一种；路径 C 生成所有三种，并让用户选择。

| 策略 | 概念 | 最适合 | 结构 |
|------|------|--------|------|
| **A — 以故事驱动** | 以个人经历为线索，情感共鸣优先 | 评论、个人分享、转型 | 钩子 → 问题 → 发现 → 经历 → 结论 |
| **B — 信息密集型** | 价值优先，高效信息传递 | 教程、对比、清单 | 核心结论 → 信息卡片 → 优缺点 → 推荐 |
| **C — 视觉优先** | 视觉冲击力为核心，最少文字 | 高审美产品、生活方式、情绪内容 | 主图 → 细节照片 → 生活方式场景 → CTA |

## 参考图像

用户提供的参考图像**独立于**内部的“图像-1 作为锚点”链（步骤 3） — 它们叠加在其上。

**输入**：通过 `--ref <文件...>` 或在对话中粘贴路径。
- 文件路径 → 复制到 `refs/NN-ref-{slug}.{ext}`
- 无路径粘贴 → 请求路径，或作为文本后备提取样式特征

**使用模式**（每个引用）：

| 使用 | 效果 |
|------|------|
| `direct` | 将文件传递给后端（通常仅在图像1上，以便锚点通过链传播） |
| `style` | 提取样式特征并附加到每个卡片提示的正文中 |
| `palette` | 提取十六进制颜色并附加到每个卡片提示的正文中 |

在每个受影响的卡片的提示前码中记录引用：

```yaml
references:
  - ref_id: 01
    filename: 01-ref-brand.png
    usage: direct
```

生成时：验证文件是否存在。图像1与 `usage: direct` + 接受引用的后端 → 通过后端的引用参数传递（成为链锚点）。图像2+ 保持使用图像1作为 `--ref` 根据步骤3 — 不要在顶部重新堆叠用户引用（避免冲突信号）。对于 `style`/`palette`，将提取的特征嵌入每个提示中。

## 文件布局

```
image-cards/{topic-slug}/
├── source-{slug}.{ext}
├── analysis.md
├── outline-strategy-{a,b,c}.md    # 仅路径C
├── outline.md
├── prompts/NN-{type}-{slug}.md
├── NN-{type}-{slug}.png
└── refs/                          # 仅如果使用 --ref
```

**Slug**：2-4个词，小写破折号分隔。 "AI 工具推荐" → `ai-tools-recommend`。发生冲突时，追加 `-YYYYMMDD-HHMMSS`。

**备份规则**（全程适用）：在覆盖任何文件（源文件、大纲、提示、图像）之前 — 将现有文件重命名为 `<name>-backup-YYYYMMDD-HHMMSS.<ext>`。这保护了用户编辑。

## 工作流程

```
- [ ] 步骤0：加载 EXTEND.md ⛔ 阻塞（仅交互式）
- [ ] 步骤1：分析内容 → analysis.md
- [ ] 步骤2：智能确认 ⚠️ 必须执行（路径A / B / C）
- [ ] 步骤3：生成图像
- [ ] 步骤4：完成报告
```

### 步骤0：加载 EXTEND.md ⛔ 阻塞

按顺序检查这些路径；第一个命中者胜出：

| 路径 | 范围 |
|------|------|
| `.baoyu-skills/baoyu-xhs-images/EXTEND.md` | 项目 |
| `${XDG_CONFIG_HOME:-$HOME/.config}/baoyu-skills/baoyu-xhs-images/EXTEND.md` | XDG |
| `$HOME/.baoyu-skills/baoyu-xhs-images/EXTEND.md` | 用户主目录 |

- **找到** → 读取、解析、打印摘要（样式 / 布局 / 水印 / 语言），继续。
- **未找到 + 交互式** → 运行首次设置（参见 `references/config/first-time-setup.md`）并在任何其他操作之前保存。在存在偏好之前，不要分析内容或询问样式问题 — 这使首次运行行为可预测。
- **未找到 + `--yes`** → 跳过设置，使用内置默认值（无水印，样式/布局自动选择，语言来自内容）。不要提示，不要创建 EXTEND.md。

**EXTEND.md 键**：水印、首选样式/布局、自定义样式定义、语言偏好、首选图像后端、生成批次大小。模式：`references/config/preferences-schema.md`。

### 步骤1：分析内容 → `analysis.md`

1. 保存源（如果 `source.md` 存在，则适用备份规则）。
2. 在 `references/workflows/analysis-framework.md` 中运行深度分析：内容类型、钩子潜力、受众、参与信号、视觉机会地图、滑动流程。
3. 检测源语言，选择推荐图像数量（2-10）。
4. 使用上述 **自动选择** 表格自动推荐策略 + 样式 + 布局 + 配色。
5. 将所有内容写入 `analysis.md`。

### 步骤2：智能确认 ⚠️ 必须执行

**硬门槛**：此步骤根据 [确认政策](#confirmation-policy) 是强制性的 — Step 3 不能在此处用户确认之前开始（或明确使用 `--yes` / 当前请求中等效措辞选择退出）。

目标：展示自动推荐的计划并允许用户确认或调整。在 `--yes` 下完全跳过此步骤 — 使用分析和任何CLI覆盖按路径A继续。

**显示摘要** 在询问之前：

```
📋 内容分析
  主题：[topic] | 类型：[content_type]
  要点：[key points]
  受众：[audience]

🎨 推荐方案（自动匹配）
  策略：[A/B/C] [name]（[reason]）
  样式：[style] · 布局：[layout] · 配色：[palette or 默认] · 预设：[preset]
  图像：[N]张（封面+[N-2]内容+结尾）
  元素：[background] / [decorations] / [emphasis]
```

然后问一个问题 — 三个路径。逐字选项复制：`references/confirmation.md`。

**路径A — 快速确认**（信任自动推荐）：使用推荐策略 + 样式生成一个大纲 → 保存到 `outline.md` → Step 3。

**路径B — 自定义**：询问五个问题（策略/样式、布局、配色、数量、可选注释）并预填推荐 — 空白保持推荐。使用用户的选择生成一个大纲 → `outline.md` → Step 3。参见 `references/confirmation.md`。

**路径C — 详细模式**：两个子确认。

- *步骤2a — 内容理解*：询问卖点（多选）、受众、样式偏好（真实 / 专业 / 美学 / 自动），可选上下文。更新 `analysis.md`。
- *步骤2b — 三个大纲变体*：生成 `outline-strategy-a.md`、`outline-strategy-b.md`、`outline-strategy-c.md`。每个必须具有不同的结构和不同的推荐样式 — 在前码中包含 `style_reason`。页数启发式：A ~4-6，B ~3-5，C ~3-4。模板：`references/workflows/outline-template.md`；前码示例在 `references/confirmation.md`。
- *步骤2c — 选择*：询问三个问题（大纲 A/B/C/组合、样式、视觉元素）。将选择/合并的大纲保存到 `outline.md` → Step 3。

### 步骤3：生成图像

使用确认的大纲 + 样式 + 布局 + 配色：

**视觉一致性 — 图像1锚点链**：角色 / 萌宠 / 颜色渲染在调用之间漂移，除非你锚定它们。首先生成图像1（封面）而不带 `--ref`，然后将图像1作为 `--ref` 传递给每个后续图像。这是此技能最重要的连贯性技巧 — 即使后端也支持会话ID，也不要跳过它。

生成流程：

1. 将每个图像的完整提示写入 `prompts/NN-{type}-{slug}.md` 在用户的偏好语言中（适用备份规则），然后验证所有选定的提示文件是否存在。
2. 首先生成 **图像1** 不带 `--ref`；PNG文件适用备份规则。这建立了锚点。
3. 使用图像1作为 `--ref <path-to-image-01.png>` 构建任务列表 **图像2+**。
4. 按照批处理生成策略分批发送图像2+：后端原生批处理优先，运行时并行工具调用其次，仅作为后备顺序。
5. 每个完成图像后报告进度。失败时，仅从相同的保存提示文件重试失败项一次。

**水印**（如果 EXTEND.md 中启用）：附加到生成提示：

```
包含一个微妙的水印 "[content]" 定位在 [位置]。
水印应清晰可读但不会分散注意力。
```

参见 `references/config/watermark-guide.md`。

**后端选择**：根据顶部的图像生成工具规则 — 使用任何可用的，如果有多个则询问一次，在任何生成之前。在 `--yes` 下，使用 EXTEND.md 偏好并回退到第一个可用的后端。提示文件必须在调用任何后端之前存在。

**`codex-imagegen` 调用**：当规则解析为 `codex-imagegen` 时，参见 [references/codex-imagegen.md](references/codex-imagegen.md) 调用契约（首选 `baoyu-image-gen --provider codex-cli` 路径，运行时包装器发现，参数说明，stdout 模式，批处理语义 — 每次调用n=1，因此卡片批次必须为每张卡片发送一个包装器调用；包装器不接受 `--sessionId`，因此链一致性必须来自上述步骤3的 `--ref`）。

**会话ID**（如果后端支持 `--sessionId`）：对每个图像使用 `cards-{topic-slug}-{timestamp}`；结合引用链，这提供了最大的连贯性。

### 步骤4：完成报告

```
图像卡片系列完成！

主题：[topic]
模式：[快速 / 自定义 / 详细]
策略：[A/B/C/组合]
样式：[name]
配色：[name or "默认"]
布局：[name or "变化"]
位置：[目录]
图像：N总计

✓ analysis.md
✓ outline.md
✓ outline-strategy-a/b/c.md (详细模式仅)
- 01-cover-[slug].png ✓ 封面（稀疏）
- 02-content-[slug].png ✓ 内容（平衡）
- ...
- NN-ending-[slug].png ✓ 结尾（稀疏）
```

## 内容分解原则

| 位置 | 目的 | 典型布局 |
|------|------|----------|
| 封面（图像1） | 钩子 + 视觉冲击 | `稀疏` |
| 内容（中间） | 每个图像的核心价值 | `平衡` / `密集` / `列表` / `比较` / `流程` |
| 结尾（最后） | CTA / 总结 | `稀疏` 或 `平衡` |

对于样式 × 布局兼容性矩阵，参见上述 **样式 × 布局矩阵**。

## 图像修改

| 操作 | 如何 |
|------|------|
| 编辑 | 首先更新 `prompts/NN-{type}-{slug}.md`，然后使用相同的会话ID重新生成 |
| 添加 | 指定位置，创建提示，生成，重新编号后续文件 `NN+1`，更新大纲 |
| 删除 | 删除文件，重新编号后续 `NN-1`，更新大纲 |

始终在重新生成之前更新提示文件 — 它是真相来源，并使更改可重复。

文本更正政策：

- 如果卡片的标题、正文副本、标签或任何其他渲染文本拼写错误、混乱、难以阅读或视觉上薄弱，不要用代码修补位图。
- 对于文本更正重新生成，创建一个新的提示文件和新的输出路径，以便保留有缺陷的候选文件进行比较。
- 后处理仅限于裁剪、调整大小、压缩或格式转换，这些不会改变文本或主要构图。

## 引用

| 文件 | 内容 |
|------|------|
| `references/confirmation.md` | 每个确认路径的逐字 AskUserQuestion 复制 |
| `references/style-presets.md` | 完整预设快捷方式定义 |
| `references/presets/<style>.md` | 每个样式的元素定义 |
| `references/palettes/<name>.md` | 每个配色的颜色定义 |
| `references/elements/canvas.md` | 纵横比、安全区域、网格布局 |
| `references/elements/image-effects.md` | 切片、描边、滤镜 |
| `references/elements/typography.md` | 装饰文本、标签、文本方向 |
| `references/elements/decorations.md` | 强调标记、背景、涂鸦、框架 |
| `references/workflows/analysis-framework.md` | 内容分析框架 |
| `references/workflows/outline-template.md` | 布局指南的大纲模板 |
| `references/workflows/prompt-assembly.md` | 提示组装指南 |
| `references/config/preferences-schema.md` | EXTEND.md 模式 |
| `references/config/first-time-setup.md` | 首次设置流程 |
| `references/config/watermark-guide.md` | 水印配置 |

## 注意事项

- 生成失败时自动重试一次，然后报告错误。
- 对于敏感的公众人物，使用风格化的卡通替代品。
- 智能确认（步骤2）是必须的；详细模式添加了第二次确认（2a + 2c）。

## 更改偏好

EXTEND.md 位于步骤0中列出的第一个匹配路径。更改它的三种方式：

- **直接编辑** — 打开 EXTEND.md 并更改字段。完整模式：`references/config/preferences-schema.md`。
- **交互式重新配置** — 删除 EXTEND.md（或询问“重新配置 baoyu-xhs-images 偏好” / “重新配置”）。下一次运行重新触发首次设置。
- **常见的单行编辑**：
  - `preferred_image_backend: auto` — 默认；运行时原生工具获胜，回退到唯一安装的后端，仅在存在多个非原生时询问。
  - `preferred_image_backend: codex-imagegen` — 固定到Codex的内置。
  - `preferred_image_backend: baoyu-image-gen` — 固定到 baoyu-image-gen 技能。
  - `preferred_image_backend: ask` — 每次运行确认后端。
  - `generation_batch_size: 4` — 默认并发渲染的图像数量，当后端/运行时支持批处理或并行生成时。
  - `preferred_style: notion`, `preferred_layout: dense`, `preferred_palette: macaron`, `language: zh`.
  - `watermark.enabled: true` + `watermark.content: "@handle"` — 添加水印。
