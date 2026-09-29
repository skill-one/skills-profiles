---
name: baoyu-slide-deck
description: 从内容生成专业的幻灯片演示文稿图像。创建带样式说明的大纲，然后生成单个幻灯片图像。当用户要求“创建幻灯片”、“制作演示文稿”、“生成演示文稿”、“幻灯片演示文稿”或“PPT”时使用。
---

# 幻灯片套件生成器

将内容转换为专业的幻灯片套件图像。该套件的设计用于**阅读和分享**（自我解释的幻灯片、逻辑滚动流程、社交媒体友好）而不是现场演示——这一假设驱动了以下每个布局和密度决策。

## 用户输入工具

当此技能提示用户时，请遵循此工具选择规则（优先级顺序）：

1. **优先使用**当前代理运行时暴露的**内置用户输入工具**——例如，`AskUserQuestion`、`request_user_input`、`clarify`、`ask_user`或任何等效工具。
2. **后备**：如果没有此类工具，则发出编号的纯文本消息，并要求用户回复所选择编号/答案以回答每个问题。
3. **批量处理**：如果该工具支持每调用一次询问多个问题，则将所有适用问题组合为单个调用；如果仅支持单个问题，则按优先级顺序一次询问它们。

以下具体的`AskUserQuestion`引用是示例——在其他运行时中，请替换本地等效工具。

## 图像生成工具

当此技能需要渲染图像时，按以下顺序解析后端：

1. **当前请求覆盖**——如果用户在当前消息中指定了特定的后端，则使用它。
2. **保存的偏好设置**——如果`EXTEND.md`将`preferred_image_backend`设置为当前可用的后端，则使用它。
3. **自动选择**（当偏好设置为`auto`、未设置或固定的后端不可用时）：
   - **Codex (`imagegen`)** — 首先，检查您的可用技能/工具清单。如果列出了名为`imagegen`的技能，则表示您正在Codex中运行，并且**必须**使用它：通过`Skill`工具使用`skill: "imagegen"`调用，传递保存的提示文件的内容（以及输出路径和Codex `imagegen`自己的参数指定的宽高比）。Codex `imagegen`是该运行时中的官方光栅后端，并且优先于任何非原生技能（例如，`baoyu-image-gen`），除非用户显式固定了不同的`preferred_image_backend`。
   - **通过`codex exec`的Codex (`codex-imagegen`)** — 如果当前运行时不暴露原生`imagegen`技能，但`codex` CLI位于`PATH`上并且有活动的`codex login`，则通过`baoyu-image-gen --provider codex-cli`（首选）路由，或者——如果`baoyu-image-gen`不可用——直接调用捆绑的包装器。详细信息、参数和运行时发现程序位于[references/codex-imagegen.md](references/codex-imagegen.md)——仅在选中此分支时加载该文件。
   - **Cursor (`GenerateImage`)** — 如果运行时暴露了原生`GenerateImage`工具，则表示您正在Cursor中运行，并且它以与Codex `imagegen`相同的方式优先于任何非原生技能。有两个严格的限制：(a) 它没有宽高比参数——在作为`description`传递的提示文本中明确说明目标宽高比/尺寸；(b) 它不接受输出目录——它保存到工具管理的位置，因此生成后需要将文件复制/移动到技能的预期输出路径（例如，`outputs/.../NN-xxx.png`）。参考图像放在`reference_image_paths`中。
   - **其他运行时原生工具** — 如果运行时暴露了不同的原生图像工具（例如，Hermes `image_generate`），则按相同方式使用它。
   - 否则，如果恰好安装了一个非原生后端（例如，`baoyu-image-gen`），则使用它。
   - 否则（存在多个非原生后端且没有运行时原生工具），一次询问用户——与其他初始问题批量处理。
4. **如果都不可用**，则告知用户并询问如何操作。

**⛔ 永远不要用SVG、HTML、画布或其他基于代码的渲染来替代光栅图像生成。** Codex `imagegen`自己的描述说它应该用于“当输出应该是位图资源而不是存储库原生代码或矢量时”。如果您无法通过步骤3解析光栅后端，则通过步骤4询问用户——不要无声地发出SVG、写入内联`<svg>`标记或生成HTML/CSS艺术作品作为替代。即使文章/部分看起来像是“图表”，这也适用：调用此规则的消费技能已经决定需要一个光栅图像。

**⛔ 永远不要通过在生成的光栅图像上绘画来修复渲染的文本。** 不要使用ImageMagick、Pillow、Canvas、SVG、HTML/CSS、OCR脚本或任何其他程序化覆盖来覆盖、重写、擦除、描边或替换已生成幻灯片图像中的幻灯片标题、项目符号或任何其他文本。如果文本不正确或不清晰，请从更正后的提示中重新生成，简化图像上的文本，或询问用户要保留哪个不完美的候选者。

设置`preferred_image_backend: ask`会强制在每次运行时都执行步骤3的提示，无论是否有可用后端。用户通过以下部分的“## 更改偏好设置”来更改固定的后端。

**提示文件要求（硬性要求）**：在调用任何后端之前，将每个图像的完整、最终提示写入`prompts/`下的独立文件（命名：`NN-slide-[slug].md`）。该文件是可重复性记录，并允许您在不重新生成提示的情况下切换后端。

上述具体工具名称（`imagegen`、`GenerateImage`、`image_generate`、`baoyu-image-gen`）是示例——请按相同规则替换本地等效工具。

## 批量生成策略

在保存并验证当前生成组的每个提示文件后，默认按批量生成幻灯片图像。

优先级顺序：

1. 如果所选后端存在原生批处理/多任务接口，则使用它。每个任务必须保持自己的提示文件、输出路径、宽高比、会话ID和直接参考图像。
2. 如果没有原生批处理接口，但运行时可以发出并行工具调用，则一次派遣最多`generation_batch_size`张幻灯片图像。默认：`4`。当前消息中的显式用户请求（例如`--batch-size 4`或“并行4张一起生成”）会覆盖EXTEND.md中的设置。
3. 如果既没有原生批处理也没有并行工具调用可用，则按顺序生成。

规则：

- 在所有选定的幻灯片提示文件都存在于磁盘上之前，永远不要开始第一个批量。
- 重新生成失败的项目一次，不要重新生成成功的项目。
- 不要使用子代理仅仅是为了并行化图像渲染。仅使用子代理进行单独的提示迭代或创意探索。
- 仅在所有选定的幻灯片图像生成后，才合并PPTX/PDF。

## 确认策略

默认行为：**生成前确认**。

- 将显式技能调用、文件路径、匹配的信号/预设和`EXTEND.md`默认值视为**仅建议输入**。它们都不授权跳过确认。
- **不要**在用户完成步骤2之前开始步骤3或更晚。
- 仅在当前请求明确说明这样做时才跳过确认，例如：“直接生成”、“不用确认”、“跳过确认”、“按默认出幻灯片”或等效措辞。
- 如果明确跳过确认，则在生成之前，在下一个面向用户更新中说明假设的样式/受众/幻灯片数量/语言/后端。

## 语言

在整个问题、进度报告、错误消息和完成摘要中用用户的语言回答。保持技术标记（样式名称、文件路径、代码）为英文。

## 脚本目录

`{baseDir}` = 此`SKILL.md`的目录。解析`${BUN_X}`：优先使用`bun`；否则`npx -y bun`；否则建议`brew install oven-sh/bun/bun`。

| 脚本 | 目的 |
|------|------|
| `scripts/merge-to-pptx.ts` | 将幻灯片合并到PowerPoint |
| `scripts/merge-to-pdf.ts` | 将幻灯片合并到PDF |

## 选项

| 选项 | 描述 |
|------|------|
| `--style <name>` | 预设（见下文预设）、`custom`或自定义样式名称 |
| `--audience <type>` | 初学者 / 中级 / 专家 / 高管 / 普通人 |
| `--lang <code>` | 输出语言（en、zh、ja、...） |
| `--slides <N>` | 目标幻灯片数量（推荐8-25张，最多30张） |
| `--ref <files...>` | 每张幻灯片应用的参考图像（样式 / 调色板 / 布局 / 主题） |
| `--batch-size <n>` | 此运行中临时幻灯片图像生成批量大小。默认：`EXTEND.md`中的`generation_batch_size`，否则为4。限制在1-8之间。 |
| `--outline-only` | 在大纲后停止 |
| `--prompts-only` | 在提示后停止（跳过图像生成） |
| `--images-only` | 跳过到步骤7；需要现有的`prompts/` |
| `--regenerate <N>` | 重新生成特定幻灯片：`3`或`2,5,8` |

## 样式系统

17个预设涵盖技术 / 教育 / 生活方式 / 编辑用途。每个预设都是四个维度（纹理 / 氛围 / 字体 / 密度）的组合。如果用户在第一轮中选择“自定义维度”，则第二轮确认会针对每个维度问一个问题——选项和逐字复制位于`references/confirmation.md`中。

### 预设（17）

| 预设 | 维度 | 最适合 |
|------|------|------|
| `blueprint`（默认） | 网格 + 冷 + 技术 + 平衡 | 建筑、系统设计 |
| `chalkboard` | 有机 + 温暖 + 手写 + 平衡 | 教育、教程 |
| `corporate` | 干净 + 专业 + 几何 + 平衡 | 投资者套件、提案 |
| `minimal` | 干净 + 中性 + 几何 + 极简 | 高管简报 |
| `sketch-notes` | 有机 + 温暖 + 手写 + 平衡 | 教育、教程 |
| `hand-drawn-edu` | 有机 + 马卡龙 + 手写 + 平衡 | 教育图表、流程说明 |
| `watercolor` | 有机 + 温暖 + 人文 + 极简 | 生活方式、健康 |
| `dark-atmospheric` | 干净 + 暗色 + 编辑 + 平衡 | 娱乐、游戏 |
| `notion` | 干净 + 中性 + 几何 + 密集 | 产品演示、SaaS |
| `bold-editorial` | 干净 + 活泼 + 编辑 + 平衡 | 产品发布、主旨演讲 |
| `editorial-infographic` | 干净 + 冷 + 编辑 + 密集 | 技术说明、研究 |
| `fantasy-animation` | 有机 + 活泼 + 手写 + 极简 | 教育故事讲述 |
| `intuition-machine` | 干净 + 冷 + 技术 + 密集 | 技术文档、学术 |
| `pixel-art` | 像素 + 活泼 + 技术 + 平衡 | 游戏、开发者演讲 |
| `scientific` | 干净 + 冷 + 技术 + 密集 | 生物学、化学、医学 |
| `vector-illustration` | 干净 + 活泼 + 人文 + 平衡 | 创意、儿童内容 |
| `vintage` | 纸张 + 温暖 + 编辑 + 平衡 | 历史、遗产 |

每个预设的规格：`references/styles/<preset>.md`。预设到维度的映射：`references/dimensions/presets.md`。

### 维度（当选择“自定义维度”时）

| 维度 | 选项 | 目的 |
|------|------|------|
| **纹理** | 干净、网格、有机、像素、纸张 | 背景处理 |
| **氛围** | 专业、温暖、冷、活泼、暗、中性、马卡龙 | 色温 |
| **字体** | 几何、人文、手写、编辑、技术 | 标题/正文样式 |
| **密度** | 极简、平衡、密集 | 每张幻灯片的 信息量 |

每个维度的完整规格：`references/dimensions/*.md`。

### 自动选择

将内容信号匹配到预设。选择源中第一个包含信号关键词的行；如果没有匹配项，则回退到`blueprint`。

| 源中的信号 | 预设 |
|------|------|
| tutorial、learn、education、guide、beginner | `sketch-notes` |
| hand-drawn、infographic、diagram、process、onboarding | `hand-drawn-edu` |
| classroom、teaching、school、chalkboard | `chalkboard` |
| architecture、system、data、analysis、技术 | `blueprint` |
| creative、children、kids、cute | `vector-illustration` |
| briefing、academic、research、bilingual | `intuition-machine` |
| executive、极简、干净、简单 | `minimal` |
| saas、product、dashboard、metrics | `notion` |
| investor、quarterly、business、corporate | `corporate` |
| launch、marketing、keynote、magazine | `bold-editorial` |
| entertainment、music、gaming、atmospheric | `dark-atmospheric` |
| explainer、journalism、science communication | `editorial-infographic` |
| story、fantasy、animation、magical | `fantasy-animation` |
| gaming、retro、pixel、developer | `pixel-art` |
| biology、chemistry、medical、scientific | `scientific` |
| history、heritage、vintage、expedition | `vintage` |
| lifestyle、wellness、travel、artistic | `watercolor` |

### 幻灯片数量启发式算法

| 源长度 | 推荐幻灯片数量 |
|------|------|
| < 1000字 | 5-10张 |
| 1000-3000字 | 10-18张 |
| 3000-5000字 | 15-25张 |
| > 5000字 | 20-30张（考虑拆分） |

## 参考图像

用户可以提供参考图像来指导样式、调色板、布局或主题。

**输入**：通过`--ref <files...>`或当用户在对话中提供文件路径/粘贴图像来接受。
- 文件路径 → 复制到`{slide-deck-dir}/refs/NN-ref-{slug}.{ext}`
- 没有路径粘贴的图像 → 询问路径，或口头提取样式特征作为文本后备

**使用模式**（每个参考图像）：

| 使用模式 | 效果 |
|------|------|
| `direct` | 将文件作为参考图像传递给后端，用于每张幻灯片 |
| `style` | 提取样式特征（线条处理、纹理、氛围）并追加到每张幻灯片的提示正文 |
| `palette` | 提取十六进制颜色并追加到每张幻灯片的提示正文 |

在每个幻灯片的提示文件的前置中记录参考图像：

```yaml
references:
  - ref_id: 01
    filename: 01-ref-brand.png
    usage: direct
```

在生成时，验证文件是否存在。如果`usage: direct`且后端接受参考图像（例如，`baoyu-image-gen --ref`），则在每个幻灯片中传递文件。否则，将提取的`style`/`palette`特征嵌入提示文本中。

## 文件布局

```
slide-deck/{topic-slug}/
├── source-{slug}.{ext}
├── outline.md
├── prompts/NN-slide-{slug}.md
├── NN-slide-{slug}.png
├── {topic-slug}.pptx
└── {topic-slug}.pdf
```

**Slug**：2-4个词，短横线命名法，从主题中提取。“机器学习入门”→`intro-machine-learning`。

**备份规则**（适用于所有步骤）：如果即将写入的文件已存在，则在写入新文件之前将其重命名为`<name>-backup-YYYYMMDD-HHMMSS.<ext>`。这可以保护用户编辑并启用回滚。

## 工作流程

复制此清单并随着完成情况勾选项目：

```
- [ ] 步骤1：设置和分析
- [ ] 步骤2：确认 ⚠️ 必须执行（第一轮；第二轮仅如果“自定义维度”）
- [ ] 步骤3：生成大纲
- [ ] 步骤4：审查大纲（有条件）
- [ ] 步骤5：生成提示
- [ ] 步骤6：审查提示（有条件）
- [ ] 步骤7：生成图像
- [ ] 步骤8：合并到PPTX/PDF
- [ ] 步骤9：输出摘要
```

### 步骤1：设置和分析

**1.1 加载EXTEND.md** — 按顺序检查这些路径；第一个命中者胜出：

| 路径 | 范围 |
|------|------|
| `.baoyu-skills/baoyu-slide-deck/EXTEND.md` | 项目 |
| `${XDG_CONFIG_HOME:-$HOME/.config}/baoyu-skills/baoyu-slide-deck/EXTEND.md` | XDG |
| `$HOME/.baoyu-skills/baoyu-slide-deck/EXTEND.md` | 用户主目录 |

如果找到，则读取、解析并打印摘要（样式 / 受众 / 语言 / 审查 / 生成批量大小）。如果没有找到，则使用默认值——首次设置不会阻止此技能。模式：`references/config/preferences-schema.md`。

**1.2 分析内容** — 遵循`references/analysis-framework.md`：对内容进行分类，检测语言，注意样式选择的信号，根据长度（见上文的“幻灯片数量启发式算法”）估计幻灯片数量，生成主题slug。将源保存为`source.md`（如果存在，则遵守备份规则）。

**1.3 检查现有输出** ⚠️ 必须在步骤2之前执行。如果`slide-deck/{topic-slug}/`存在，则询问如何操作——四个选项（重新生成大纲 / 重新生成图像 / 备份并重新生成 / 退出），逐字复制在`references/confirmation.md`中。

将分析结果保存到`analysis.md`：主题、受众、信号、推荐的样式和幻灯片数量、语言检测。

### 步骤2：确认 ⚠️ 必须执行

**硬性门槛**：此步骤是根据[确认策略](#confirmation-policy)强制执行的——步骤3+不能在用户在此处确认（或使用当前请求中的“直接生成”/等效措辞明确选择退出）之前开始。

**第一轮（始终）** — 将五个问题批量在一个 `AskUserQuestion` 调用中：风格、受众、幻灯片数量、评审大纲？、评审提示？。逐字选项在 `references/confirmation.md` 中。

问题前显示摘要：
- 内容类型 + 主题
- 检测到的语言
- 基于信号推荐的风格
- 基于长度推荐的幻灯片数量

**第二轮（仅在第一轮中“自定义维度”）** — 批量四个问题：纹理、情绪、字体、密度。逐字选项在 `references/confirmation.md` 中。这四个答案将替换预设。

**确认后**：更新 `analysis.md` 并存储来自 Q4/Q5 的 `skip_outline_review` / `skip_prompt_review` 标志。

### 第 3 步：生成大纲

解析风格：预设 → `references/styles/{preset}.md`；自定义维度 → 合并 `references/dimensions/` 中的文件。从解析的风格构建 `STYLE_INSTRUCTIONS`，应用确认的受众 + 语言 + 幻灯片数量，遵循 `references/outline-template.md`，并保存为 `outline.md`。

如果 `--outline-only`，则在此停止。如果 `skip_outline_review`，则跳过第 4 步。

### 第 4 步：评审大纲（条件性）

显示幻灯片逐页表格（`# | 标题 | 类型 | 布局`）以及总数和解析的风格。询问：继续 / 先编辑大纲 / 重新生成 — 逐字选项在 `references/confirmation.md` 中。

如果“先编辑大纲”，请告诉用户编辑 `outline.md` 并准备好时再次询问。如果“重新生成大纲”，则返回第 3 步。

### 第 5 步：生成提示

对于大纲中的每一页幻灯片：
1. 读取 `references/base-prompt.md`
2. 从大纲中提取 `STYLE_INSTRUCTIONS`（不要重新读取风格文件）
3. 添加幻灯片的内容
4. 如果指定了 `Layout:`，则包含来自 `references/layouts.md` 的指导
5. 保存到 `prompts/NN-slide-{slug}.md`（备份规则适用）

如果 `--prompts-only`，则在此停止。如果 `skip_prompt_review`，则跳过第 6 步。

### 第 6 步：评审提示（条件性）

显示提示索引（`# | 文件名 | 幻灯片标题`）并询问：继续 / 先编辑提示 / 重新生成 — 逐字选项在 `references/confirmation.md` 中。分支与第 4 步相同。

### 第 7 步：生成图像

1. 通过顶部的图像生成工具规则解析图像后端 — 如果安装了多个，则询问一次。
   - **`codex-imagegen` 调用**：当规则解析为 `codex-imagegen` 时，请参阅 [references/codex-imagegen.md](references/codex-imagegen.md) 以获取调用合同（首选 `baoyu-image-gen --provider codex-cli` 路径、运行时包装器发现、参数说明、stdout 模式、批量语义 — 每次调用 n=1，因此幻灯片批量必须为每页幻灯片分派一个包装器调用）。
2. 确认每个 `prompts/NN-slide-{slug}.md` 存在（硬性要求；提示文件是可重复性的记录，无论后端如何）。
3. 会话 ID：`slides-{topic-slug}-{timestamp}` — 仅在它支持会话时才传递给后端。
4. 为选定的幻灯片构建任务列表，每个幻灯片的提示文件、输出 PNG 路径、宽高比、会话 ID 和验证的直接引用。
5. 按照的 `## 批量生成策略` 分批分派幻灯片图像：首先使用后端原生批量，其次使用运行时并行工具调用，仅作为后备使用顺序。在分派前对 PNG 文件应用备份规则。报告进度为 `Generated X/N`。在报告错误之前仅重试失败的项目一次。

`--regenerate N` 仅跳转到命名的幻灯片。`--images-only` 从现有的提示开始。

### 第 8 步：合并

```bash
${BUN_X} {baseDir}/scripts/merge-to-pptx.ts <slide-deck-dir>
${BUN_X} {baseDir}/scripts/merge-to-pdf.ts <slide-deck-dir>
```

### 第 9 步：摘要

```
幻灯片集完成！
主题：[主题]
风格：[预设或“自定义：纹理+情绪+字体+密度”]
位置：[目录]
幻灯片：N

- 01-slide-cover.png
- ...
- NN-slide-back-cover.png

大纲：outline.md
PPTX：{topic-slug}.pptx
PDF：{topic-slug}.pdf
```

## 幻灯片修改

| 操作 | 如何 |
|------|-----|
| 编辑 | 首先更新 `prompts/NN-slide-{slug}.md`，然后 `--regenerate N` |
| 添加 | 在位置创建新的提示，生成图像，重新编号后续 `NN`（slugs 不变），更新 `outline.md`，重新合并 |
| 删除 | 删除 PNG + 提示，重新编号后续，更新 `outline.md`，重新合并 |

始终在重新生成图像之前更新提示文件 — 这将保持提示目录作为真实来源，并使更改可重复。重新编号时仅更改 `NN`；slugs 保持稳定，因此引用仍然有效。

文本更正策略：

- 如果幻灯片的标题、项目符号或任何其他渲染文本拼写错误、混乱、难以阅读或视觉上较弱，请不要用代码修补位图。
- 对于文本更正重新生成，请编写新的提示文件和新的输出路径，以便保留有缺陷的候选文件以供比较。
- 后处理仅限于裁剪、调整大小、压缩或格式转换，这些操作不会更改文本或主要构图。

有关完整详细信息，请参阅 `references/modification-guide.md`。

## 参考

| 文件 | 内容 |
|------|---------|
| `references/confirmation.md` | 每次确认的逐字 AskUserQuestion 选项副本 |
| `references/analysis-framework.md` | 内容分析框架 |
| `references/outline-template.md` | 大纲结构 |
| `references/base-prompt.md` | 图像生成的基本提示正文 |
| `references/layouts.md` | 布局选项 |
| `references/design-guidelines.md` | 受众、字体、颜色选择 |
| `references/content-rules.md` | 内容指南 |
| `references/modification-guide.md` | 编辑/添加/删除工作流 |
| `references/styles/<preset>.md` | 每个预设的规范 |
| `references/dimensions/*.md` | 每个维度的规范 |
| `references/config/preferences-schema.md` | EXTEND.md 模式 |

## 备注

- 图像生成大约需要每页幻灯片 10-30 秒；在它们之间报告进度。
- 对于敏感的公众人物，请优先选择风格化的替代方案，以避免肖像问题。
- 当后端支持时，通过会话 ID 维护视觉一致性。

## 更改偏好设置

EXTEND.md 位于第 1.1 步中列出的第一个匹配路径。更改它的两种方法：

- **直接编辑** — 打开 EXTEND.md 并更改字段。完整模式：`references/config/preferences-schema.md`。
- **常见的单行编辑**：
  - `preferred_image_backend: auto` — 默认；运行时原生工具获胜，回退到唯一安装的后端，仅在存在多个非原生时询问。
  - `preferred_image_backend: codex-imagegen` — 固定到 Codex 的内置。
  - `preferred_image_backend: baoyu-image-gen` — 固定到 baoyu-image-gen 技能。
  - `preferred_image_backend: ask` — 每次运行确认后端。
  - `generation_batch_size: 4` — 默认情况下，当后端/运行时支持批量或并行生成时，同时渲染的幻灯片图像数量。
  - `preferred_style: blueprint`, `preferred_audience: experts`, `language: zh`。
