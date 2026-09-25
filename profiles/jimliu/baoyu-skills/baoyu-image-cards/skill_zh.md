# 图像卡片系列生成器

将复杂内容分解为引人注目的图像卡片系列，提供多种风格选项。

## 用户输入工具

当此技能提示用户时，请遵循以下工具选择规则（优先顺序）：

1. **优先使用**当前代理运行时暴露的**内置用户输入工具** — 例如，`AskUserQuestion`、`request_user_input`、`clarify`、`ask_user`或任何等效工具。
2. **降级**：如果没有此类工具，则发出编号的纯文本消息，并要求用户回复选择的编号/答案以回答每个问题。
3. **批量处理**：如果工具支持每调用一次询问多个问题，则将所有适用问题合并为单个调用；如果仅支持单个问题，则按优先顺序逐一询问。

以下具体的`AskUserQuestion`参考是示例 — 在其他运行时中替换本地等效项。

## 图像生成工具

当此技能需要渲染图像时，按以下顺序解析后端：

1. **当前请求覆盖** — 如果用户在当前消息中指定了特定的后端，则使用它。
2. **保存的偏好设置** — 如果`EXTEND.md`将`preferred_image_backend`设置为当前可用的后端，则使用它。
3. **自动选择**（当偏好设置为`auto`、未设置或固定的后端不可用时）：
   - **Codex (`imagegen`)** — 首先，检查您的可用技能/工具清单。如果列出了名为`imagegen`的技能，则表示您正在Codex中运行，并且**必须**使用它：通过`Skill`工具以`skill: "imagegen"`调用，并将保存的提示文件的内容（以及输出路径和宽高比，根据Codex `imagegen`自己的参数）传递给它。Codex `imagegen`是该运行时的官方光栅后端，优先于任何非原生技能（例如，`baoyu-imagine`），除非用户明确固定了不同的`preferred_image_backend`。
   - **其他运行时原生工具** — 如果运行时暴露了不同的原生图像工具（例如，Hermes `image_generate`），则以相同的方式使用它。
   - 否则，如果恰好安装了一个非原生后端（例如，`baoyu-imagine`），则使用它。
   - 否则（存在多个非原生后端且没有运行时原生工具），一次询问用户 — 与其他任何初始问题批量处理。
4. **如果都没有可用**，告诉用户并询问如何继续。

**⛔ 永远不要用SVG、HTML、画布或其他基于代码的渲染来替代光栅图像生成。** Codex `imagegen`自己的描述说它应该用于“当输出应该是位图资源而不是本地代码或矢量时”。如果您无法通过步骤3解析光栅后端，请通过步骤4询问用户 — 不要默默地发出SVG、写入内联`<svg>`标记或生成HTML/CSS艺术作为替代。即使文章/部分看起来像是“图表式的”，调用此规则的消费者技能已经决定需要光栅图像。

**⛔ 永远不要通过在生成的光栅图像上绘画来修复渲染的文本。** 不要使用ImageMagick、Pillow、Canvas、SVG、HTML/CSS、OCR脚本或任何其他程序化叠加来覆盖、重写、擦除、描边或替换已生成图像卡片中的标题、正文、标签或任何其他文本。如果文本错误或不清晰，请从更正后的提示中重新生成，切换到卡片上文本较少的布局，或询问用户要保留哪个不完美的候选者。

设置`preferred_image_backend: ask`会强制在每次运行中提示步骤3，无论是否有可用后端。用户通过下方“## 更改偏好设置”部分更改固定的后端。

**提示文件要求（硬性要求）**：在调用任何后端之前，将每个图像的完整最终提示写入`prompts/`下的独立文件（命名：`NN-{type}-[slug].md`）。该文件是可重复性记录，并允许您在不重新生成提示的情况下切换后端。

以上具体的工具名称（`imagegen`、`image_generate`、`baoyu-imagine`）是示例 — 替换本地等效项。

## 批量生成策略

在保存并验证当前生成组的每个提示文件后，默认按批量生成图像。

优先顺序：

1. 如果存在，则使用所选后端的本地批量/多任务接口。每个任务必须保持自己的提示文件、输出路径、宽高比、会话ID和直接参考图像。
2. 如果不存在本地批量接口，但运行时可以发出并行工具调用，则一次派遣最多`generation_batch_size`张图像。默认：`4`。当前消息中的显式用户请求，例如`--batch-size 4`或"并行4张一起生成"，会覆盖EXTEND.md。
3. 如果既没有本地批量也没有并行工具调用可用，则按顺序生成。

规则：

- 尊重图像-1锚链：首先生成图像1，然后使用图像1作为参考批量生成图像2+。
- 只有在为该批量选择了所有提示文件都存在于磁盘上后，才永远不会开始一个批量。
- 重新生成失败项一次，不要重新生成成功项。
- 不要使用子代理仅仅是为了并行图像渲染。仅用于单独的提示迭代或创意探索。

## 确认策略

默认行为：**生成前确认**。

- 将显式技能调用、文件路径、匹配的信号/预设和`EXTEND.md`默认值视为**仅建议输入**。它们都不授权跳过确认。
- **不要**在用户完成步骤2之前开始步骤3。
- 仅当当前请求明确说明这样做时才跳过确认，例如：`--yes`、"直接生成"、"不用确认"、"跳过确认"、"按默认出图"或等效措辞。
- 如果明确跳过确认，则在生成之前，在下一个面向用户更新中声明所假设的策略/风格/布局/调色板/数量/后端。

## 语言

在问题、进度、错误和完成摘要中用用户的语言回答。保持技术标记（风格名称、文件路径、代码）为英文。

## 选项

| 选项 | 描述 |
|------|-------------|
| `--style <name>` | 视觉风格（见下文风格部分） |
| `--layout <name>` | 信息布局（见下文布局部分） |
| `--palette <name>` | 颜色覆盖：macaron / warm / neon |
| `--preset <name>` | 风格 + 布局 + 可选调色板缩写（见下文预设部分；每个预设的提示片段在`references/style-presets.md`中） |
| `--ref <files...>` | 作为系列锚点应用于图像1的参考图像 |
| `--batch-size <n>` | 此运行的临时生成批量大小。默认：`generation_batch_size`来自EXTEND.md，否则为4。限制在1-8之间。 |
| `--yes` | 非交互式：跳过所有确认，使用EXTEND.md或内置默认值，自动确认建议的计划（路径A） |

## 尺寸

三个独立的旋钮可以自由组合：

| 尺寸 | 控制 | 选项 |
|-----------|----------|---------|
| **风格** | 视觉美学（线条、装饰、渲染） | 12种风格（见下文风格部分） |
| **布局** | 信息结构（密度、排列） | 8种布局（见下文布局部分） |
| **调色板**（可选） | 颜色覆盖，替换风格的默认颜色 | macaron / warm / neon（见下文调色板部分） |

示例：`--style notion --layout dense`制作知识卡片；添加`--palette macaron`以柔化颜色，而不会改变notion的渲染规则。`--preset`是风格 + 布局的缩写。

**调色板行为**：没有`--palette` → 风格的内置颜色；`--palette <name>` → 仅覆盖颜色，渲染规则不变。某些风格声明了`default_palette`（例如，sketch-notes默认为macaron）。

## 风格（12）

| 风格 | 描述 |
|-------|-------------|
| `cute`（默认） | 可爱、甜美、少女美学 |
| `fresh` | 干净、清新、自然 |
| `warm` | 舒适、友好、易接近 |
| `bold` | 高冲击力、引人注目 |
| `minimal` | 超级干净、精致 |
| `retro` | 复古、怀旧、时尚 |
| `pop` | 鲜艳、充满活力、引人注目 |
| `notion` | 极简手绘线条艺术、知识性 |
| `chalkboard` | 彩色粉笔在黑板上，教育性 |
| `study-notes` | 真实的照片风格手写，蓝色笔 + 红色注释 + 黄色荧光笔 |
| `screen-print` | 粗犷的海报艺术，半色调纹理，有限的颜色，象征性叙事 |
| `sketch-notes` | 手绘教育信息图表，macaron粉彩在温暖奶油上，摇摆线条 |

每种风格的规范：`references/presets/<style>.md`。

## 布局（8）

| 布局 | 描述 |
|-------|-------------|
| `sparse`（默认） | 1-2点，最大冲击力 |
| `balanced` | 3-4点，标准 |
| `dense` | 5-8点，知识卡片风格 |
| `list` | 枚举/排名（4-7项） |
| `comparison` | 并列对比 |
| `flow` | 流程/时间线（3-6步） |
| `mindmap` | 中心辐射（4-8分支） |
| `quadrant` | 四象限/圆形区域 |

布局规范：`references/elements/canvas.md`。

## 调色板（可选覆盖）

替换风格的颜色，同时保持渲染规则（线条处理、纹理）不变。

| 调色板 | 背景 | 区域颜色 | 强调 | 感觉 |
|---------|------------|-------------|--------|------|
| `macaron` | 温暖奶油 #F5F0E8 | 蓝色 #A8D8EA, 淡紫色 #D5C6E0, 薄荷绿 #B5E5CF, 桃色 #F8D5C4 | 橙珊瑚 #E8655A | 柔和、教育 |
| `warm` | 柔和桃色 #FFECD2 | 橙色 #ED8936, 陶土色 #C05621, 金色 #F6AD55, 粉色 #D4A09A | 棕褐色 #A0522D | 地球色系，舒适 |
| `neon` | 深紫色 #1A1025 | 青色 #00F5FF, 紫红色 #FF00FF, 绿色 #39FF14, 粉色 #FF6EC7 | 黄色 #FFFF00 | 高能量，未来感 |

调色板规范：`references/palettes/<palette>.md`。

## 预设（风格 + 布局快捷方式）

按场景分组快速启动组合。使用`--preset <name>`或在步骤2中推荐。

**知识 & 学习**：

| 预设 | 风格 | 布局 | 最佳用途 |
|--------|-------|--------|----------|
| `knowledge-card` | notion | dense | 知识卡片、概念科普 |
| `checklist` | notion | list | 清单、排行榜 |
| `concept-map` | notion | mindmap | 概念图、知识脉络 |
| `swot` | notion | quadrant | SWOT分析、四象限 |
| `tutorial` | chalkboard | flow | 教程步骤、操作流程 |
| `classroom` | chalkboard | balanced | 课堂笔记、知识讲解 |
| `study-guide` | study-notes | dense | 学习笔记、考试重点 |
| `hand-drawn-edu` | sketch-notes | flow | 手绘教程、流程图解 |
| `sketch-card` | sketch-notes | dense | 手绘知识卡片 |
| `sketch-summary` | sketch-notes | balanced | 手绘总结、图文笔记 |

**生活方式 & 分享**：

| 预设 | 风格 | 布局 | 最佳用途 |
|--------|-------|--------|----------|
| `cute-share` | cute | balanced | 少女风分享、日常种草 |
| `girly` | cute | sparse | 甜美封面、氛围感 |
| `cozy-story` | warm | balanced | 生活故事、情感分享 |
| `product-review` | fresh | comparison | 产品对比、测评 |
| `nature-flow` | fresh | flow | 健康流程、自然主题 |

**影响 & 意见**：

| 预设 | 风格 | 布局 | 最佳用途 |
|--------|-------|--------|----------|
| `warning` | bold | list | 避坑指南、重要提醒 |
| `versus` | bold | comparison | 正反对比 |
| `clean-quote` | minimal | sparse | 金句、极简封面 |
| `pro-summary` | minimal | balanced | 专业总结、商务内容 |

**趋势 & 娱乐**：

| 预设 | 风格 | 布局 | 最佳用途 |
|--------|-------|--------|----------|
| `retro-ranking` | retro | list | 复古排行、经典盘点 |
| `throwback` | retro | balanced | 怀旧分享 |
| `pop-facts` | pop | list | 趣味冷知识 |
| `hype` | pop | sparse | 炸裂封面、惊叹分享 |

**海报 & 编辑**：

| 预设 | 风格 | 布局 | 最佳用途 |
|--------|-------|--------|----------|
| `poster` | screen-print | sparse | 海报风封面、影评书评 |
| `editorial` | screen-print | balanced | 观点文章、文化评论 |
| `cinematic` | screen-print | comparison | 电影对比、戏剧张力 |

完整的提示片段定义：`references/style-presets.md`。

## 自动选择

匹配内容信号到最佳组合。第一行其关键字出现者胜出；如果没有匹配，则回退到`cute-share`。

| 源中的信号 | 风格 | 布局 | 推荐预设 |
|-------------------|-------|--------|--------------------|
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
| hand-drawn, infographic, workflow, 手绘, 图解 | `sketch-notes` | flow/balanced/dense | `hand-drawn-edu`, `sketch-card`, `sketch-summary` |

## 风格 × 布局矩阵

兼容性分数（✓✓高度推荐，✓工作良好，✗避免）。在用户选择非默认组合并且您想要标记不良匹配时使用。

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

三种不同的方法 — 每种方法都会产生结构上不同的提纲。工作流程推荐一种；路径C生成所有三种并让用户选择。

| 策略 | 概念 | 最佳用途 | 结构 |
|----------|---------|----------|-----------|
| **A — 以故事为驱动** | 个人经历作为主线，情感共鸣优先 | 评论、个人分享、转型 | 钩子 → 问题 → 发现 → 经历 → 结论 |
| **B — 信息密集型** | 价值优先，高效的信息传递 | 教程、对比、清单 | 核心结论 → 信息卡片 → 优缺点 → 推荐 |
| **C — 视觉优先** | 视觉冲击力为核心，文本最少 | 高美学产品、生活方式、情绪内容 | 主图像 → 细节照片 → 生活方式场景 → CTA |

## 参考图像

用户提供的参考图像**与**内部"图像-1作为锚点"链（步骤3）**分离** — 它们叠加在其上。

**输入**：通过`--ref <files...>`或对话中粘贴的路径。
- 文件路径 → 复制到`refs/NN-ref-{slug}.{ext}`
- 无路径粘贴 → 询问路径，或提取风格特征作为文本后备

**使用模式**（每个参考）：

| 使用 | 效果 |
|-------|--------|
| `direct` | 将文件传递给后端（通常仅在图像1上，因此锚点会通过链传播） |
| `style` | 提取风格特征并附加到每个卡片的提示正文 |
| `palette` | 提取十六进制颜色并附加到每个卡片的提示正文 |

在每个受影响的卡片的提示文件的前置符中记录参考：

```yaml
references:
  - ref_id: 01
    filename: 01-ref-brand.png
    usage: direct
```

生成时：验证文件是否存在。图像1使用`usage: direct` + 接受参考的后端 → 通过后端的参考参数传递（成为链锚点）。图像2+继续使用图像1作为`--ref`（根据步骤3），不要重新堆叠用户参考（避免冲突信号）。对于`style`/`palette`，将提取的特征嵌入到每个提示中。

## 文件布局

```
image-cards/{topic-slug}/
├── source-{slug}.{ext}
├── analysis.md
├── outline-strategy-{a,b,c}.md    # Path C only
├── outline.md
├── prompts/NN-{type}-{slug}.md
├── NN-{type}-{slug}.png
└── refs/                          # only if --ref used
```

**Slug**：2-4个词，kebab-case。 "AI 工具推荐" → `ai-tools-recommend`。如果冲突，追加`-YYYYMMDD-HHMMSS`。

**备份规则**（适用于整个流程）：在覆盖任何文件之前 — 源文件、提纲、提示、图像 — 将现有文件重命名为`<name>-backup-YYYYMMDD-HHMMSS.<ext>`。这可以保护用户编辑。

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
|------|-------|
| `.baoyu-skills/baoyu-image-cards/EXTEND.md` | 项目 |
| `${XDG_CONFIG_HOME:-$HOME/.config}/baoyu-skills/baoyu-image-cards/EXTEND.md` | XDG |
| `$HOME/.baoyu-skills/baoyu-image-cards/EXTEND.md` | 用户主目录 |

- **找到** → 读取、解析，打印摘要（风格 / 布局 / 水印 / 语言），继续。
- **未找到 + 交互式** → 运行首次设置（见`references/config/first-time-setup.md`），在任何其他操作之前保存。不要在分析内容或询问风格问题之前保持第一运行行为可预测。
- **未找到 + `--yes`** → 跳过设置，使用内置默认值（无水印、风格/布局自动选择、语言来自内容）。不要提示，不要创建 EXTEND.md。

**EXTEND.md键**：watermark、preferred style/layout、自定义风格定义、语言偏好、preferred image backend、generation batch size。模式：`references/config/preferences-schema.md`。

### 步骤1：分析内容 → `analysis.md`

1. 保存源（如果`source.md`存在，则应用备份规则）。
2. 运行`references/workflows/analysis-framework.md`中的深度分析：内容类型、钩子潜力、受众、参与信号、视觉机会地图、滑动流程。
3. 检测源语言，选择推荐图像数量（2-10）。
4. 使用上表中的**自动选择**表格自动推荐策略 + 风格 + 布局 + 调色板。
5. 将所有内容写入`analysis.md`。

### 步骤2：智能确认 ⚠️ 必须执行

**硬性门槛**：根据[确认策略](#confirmation-policy)，此步骤是强制性的 — Step 3不能在用户在此处确认（或当前请求明确选择跳过）之前开始。

目标：展示自动推荐的计划并允许用户确认或调整。完全跳过此步骤 — 使用Path A使用分析和任何CLI覆盖项 — 进行。

**显示摘要** 在询问之前：

```
📋 内容分析
  主题：[topic] | 类型：[content_type]
  要点：[key points]
  受众：[audience]

🎨 推荐方案（自动匹配）
  策略：[A/B/C] [name]（[reason]）
  风格：[style] · 布局：[layout] · 配色：[palette or 默认] · 预设：[preset]
  图像：[N]张（封面+[N-2]内容+结尾）
  元素：[background] / [decorations] / [emphasis]
```

然后问一个问题 — 三种路径。逐字复制选项：`references/confirmation.md`。

**路径 A — 快速确认**（信任自动推荐）：生成一个使用推荐策略 + 风格的提纲 → 保存到`outline.md` → Step 3。

**路径 B — 自定义**：询问五个问题（策略/风格，布局，调色板，数量，可选注释）并预填推荐值 — 空白保留推荐值。生成一个提纲使用用户的选项 → `outline.md` → Step 3。见`references/confirmation.md`。

**路径 C — 详细模式**：两个子确认。

- *步骤2a — 内容理解*：询问卖点（多选），受众，风格偏好（真实 / 专业 / 美学 / 自动），可选上下文。更新`analysis.md`。
- *步骤2b — 三种提纲变体*：生成`outline-strategy-a.md`、`outline-strategy-b.md`、`outline-strategy-c.md`。每个都必须具有不同的结构和不同的推荐风格 — 在前端符中包含`style_reason`。页面计数启发式：A ~4-6, B ~3-5, C ~3-4。模板：`references/workflows/outline-template.md`；前端符示例在`references/confirmation.md`中。

- *步骤2c — 选择*：询问三种问题（提纲A/B/C/组合，风格，视觉元素）。将选择的/合并的提纲保存到`outline.md` → Step 3。

### 步骤3：生成图像

在确认的提纲 + 风格 + 布局 + 调色板：

**视觉一致性 — 图像-1锚链**：角色 / 萌宠 / 颜色渲染漂移，除非您锚定它们。生成图像1（封面）首先不使用`--ref`，然后使用图像1作为参考批量生成图像2+。这是此技能最重要的连贯性技巧 — 不要跳过它，即使后端也支持会话ID。

生成流程：

1. 将每个图像的完整提示写入`prompts/NN-{type}-{slug}.md`（用户的首选语言），然后验证所有选定的提示文件是否存在。
2. 首先生成**图像1**，不使用`--ref`；备份规则适用于PNG文件。这建立了锚点。
3. 构建任务列表以生成**图像2+**，使用图像1作为`--ref <path-to-image-01.png>`。
4. 按照批量生成策略`## Batch Generation Policy`：如果后端/运行时支持本地批量，则首先使用它；如果运行时可以发出并行工具调用，则一次派遣最多`generation_batch_size`张图像。默认：`4`。当前消息中的显式用户请求，例如`--batch-size 4`或"并行4张一起生成"，会覆盖EXTEND.md。
5. 在完成每个图像后报告进度。失败时，从相同的保存的提示文件中重新生成失败项一次，不要重新生成成功项。
6. 不要使用子代理仅仅是为了并行图像渲染。仅用于单独的提示迭代或创意探索。

**水印**（如果EXTEND.md中启用）：附加到生成提示：

```
包含一个微妙的水印"[content]"定位在[position]。
水印应该是可读的，但不要分散注意力。
```

见`references/config/watermark-guide.md`。

**后端选择**：按照顶部图像生成工具规则 — 使用可用的任何内容，如果存在多个，则询问用户选择一次，在生成之前。

**会话ID**（如果后端支持`--sessionId`）：对于每个图像使用`cards-{topic-slug}-{timestamp}`；结合参考链，这提供了最大的连贯性。

### 步骤4：完成报告

```
图像卡片系列完成！

主题：[topic]
模式：[Quick / Custom / Detailed]
策略：[A/B/C/Combined]
风格：[name]
调色板：[name or "default"]
布局：[name or "varies"]
位置：[directory]
图像：N总

✓ analysis.md
✓ outline.md
✓ outline-strategy-a/b/c.md (detailed mode only)

- 01-cover-[slug].png ✓ 封面（sparse）
- 02-content-[slug].png ✓ 内容（balanced）
- ...
- NN-ending-[slug].png ✓ 结尾（sparse）
```

## 内容分解原则

| 位置 | 目的 | 典型布局 |
|----------|----------|----------------|
| Cover (image 1) | 钩子 + 视觉冲击力 | `sparse` |
| Content (middle) | 每个图像的核心价值 | `balanced` / `dense` / `list` / `comparison` / `flow` |
| Ending (last) | CTA / 总结 | `sparse` or `balanced` |

对于风格 × 布局兼容性矩阵，请参阅上文的**风格 × 布局矩阵**。

## 图像修改

| 操作 | 如何 |
|-------|-----|
| 编辑 | 更新`prompts/NN-{type}-{slug}.md` **首先**，然后使用相同的会话ID重新生成 |
| 添加 | 指定位置，创建提示，生成，重新编号后续文件 `NN+1`，更新提纲 |
| 删除 | 删除文件，重新编号后续 `NN-1`，更新提纲 |

始终在重新生成之前更新提示文件 — 它是事实来源，并使更改可重复。

文本校正策略：

- 如果卡片的标题、正文、标签或任何其他渲染文本拼写错误、混乱、难以阅读或视觉上较弱，则不要通过在光栅图像上绘画来修复渲染的文本。
- 对于文本校正重新生成，请写入一个新的提示文件和新的输出路径，以便保留有缺陷的候选者以供比较。
- 后处理仅限于裁剪、调整大小、压缩或格式转换，不能改变文本或主要构图。

## 参考

| 文件 | 内容 |
|------|---------|
| `references/confirmation.md` | 逐字`AskUserQuestion`副本，用于每个确认路径 |
| `references/style-presets.md` | 完整预设快捷方式定义 |
| `references/presets/<style>.md` | 每种风格的元素定义 |
| `references/palettes/<name>.md` | 每个调色板的颜色定义 |
| `references/elements/canvas.md` | 宽高比、安全区域、网格布局 |
| `references/elements/image-effects.md` | 切片、描边、过滤器 |
| `references/elements/typography.md` | 装饰文本、标签、文本方向 |
| `references/elements/decorations.md` | 强调标记、背景、涂鸦、边框 |
| `references/workflows/analysis-framework.md` | 内容分析框架 |
| `references/workflows/outline-template.md` | 提纲模板，包含布局指南 |
| `references/workflows/prompt-assembly.md` | 提示组装指南 |
| `references/config/preferences-schema.md` | EXTEND.md模式 |
| `references/config/first-time-setup.md` | 首次设置流程 |
| `references/config/watermark-guide.md` | 水印配置 |

## 备注

- 生成失败时自动重试一次，然后报告错误。
- 对于敏感的公众人物，使用风格化的卡通替代品。
- 智能确认（步骤2）是必需的；详细模式增加了第二个确认（2a + 2c）。

## 更改偏好设置

EXTEND.md位于步骤0中列出的第一个匹配路径。更改它的三种方法：

- **直接编辑** — 打开EXTEND.md并更改字段。完整模式：`references/config/preferences-schema.md`。
- **交互式重新配置** — 删除EXTEND.md（或询问"重新配置 baoyu-image-cards 偏好设置" / "重新配置"）。下一个运行会重新触发首次设置。
- **常见的单行编辑**:
  - `preferred_image_backend: auto` — 默认；运行时原生工具获胜，回退到仅安装了一个非原生后端，例如，`baoyu-imagine`，询问一次。
  - `preferred_image_backend: codex-imagegen` — 固定到Codex的内置。
  - `preferred_image_backend: baoyu-imagine` — 固定到baoyu-imagine技能。
  - `preferred_image_backend: ask` — 每次运行都强制提示步骤3，无论是否有可用后端。提示文件必须存在，然后才能调用任何后端。
