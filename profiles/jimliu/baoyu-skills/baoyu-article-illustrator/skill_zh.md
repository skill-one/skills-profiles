# 文章插画师

分析文章，识别插画位置，根据类型 × 风格 × 色彩一致性生成图像。

## 用户输入工具

当此技能提示用户时，请遵循以下工具选择规则（优先级顺序）：

1. **优先使用**当前代理运行时暴露的**内置用户输入工具** — 例如，`AskUserQuestion`、`request_user_input`、`clarify`、`ask_user` 或任何等效工具。
2. **降级处理**：如果没有此类工具，则发出编号的纯文本消息，并要求用户回复选择的编号/答案以回答每个问题。
3. **批量处理**：如果该工具支持每调用一次询问多个问题，则将所有适用问题合并为单个调用；如果仅支持单个问题，则按优先级顺序逐个询问。

下方的具体 `AskUserQuestion` 引用仅为示例 — 在其他运行时环境中，请替换本地等效工具。

## 图像生成工具

当此技能需要渲染图像时，按以下顺序解析后端：

1. **当前请求覆盖** — 如果用户在当前消息中指定了特定的后端，则使用它。
2. **保存的偏好设置** — 如果 `EXTEND.md` 将 `preferred_image_backend` 设置为当前可用的后端，则使用它。
3. **自动选择**（当偏好设置为 `auto`、未设置或固定后端不可用时）：
   - **Codex (`imagegen`)** — 首先，检查您的可用技能/工具清单。如果列出了名为 `imagegen` 的技能，则表示您正在 Codex 环境中运行，并且**必须**使用它：通过 `Skill` 工具以 `skill: "imagegen"` 调用它，并将保存的提示文件内容（以及输出路径和宽高比，根据 Codex `imagegen` 自身的参数）传递给它。Codex `imagegen` 是该运行时中的官方光栅后端，优先于任何非原生技能（例如，`baoyu-image-gen`），除非用户明确固定了不同的 `preferred_image_backend`。
   - **通过 `codex exec` 的 Codex (`codex-imagegen`)** — 如果当前运行时不暴露原生 `imagegen` 技能，但 `codex` CLI 位于 `PATH` 上且 `codex login` 处于活动状态，则通过 `baoyu-image-gen --provider codex-cli` 路径路由（首选），或者 — 如果 `baoyu-image-gen` 不可用 — 调用捆绑的包装器直接。详细信息、参数和运行时发现程序位于 [references/codex-imagegen.md](references/codex-imagegen.md) — 仅在选中此分支时加载该文件。
   - **Cursor (`GenerateImage`)** — 如果运行时暴露了原生 `GenerateImage` 工具，则表示您正在 Cursor 环境中运行，并且其优先级与非原生技能相同（与 Codex `imagegen` 相同）。有两个严格的限制：(a) 它没有宽高比参数 — 必须在作为 `description` 传递的提示文本中明确指定目标宽高比/尺寸；(b) 它不接受输出目录 — 它将文件保存到工具管理的位置，因此生成后需要将文件复制/移动到技能预期的输出路径（例如，`outputs/.../NN-xxx.png`）。参考图像放在 `reference_image_paths`。
   - **其他运行时原生工具** — 如果运行时暴露了不同的原生图像工具（例如，Hermes `image_generate`），则按相同方式使用它。
   - 否则，如果恰好安装了一个非原生后端（例如，`baoyu-image-gen`），则使用它。
   - 否则（存在多个非原生后端且没有运行时原生工具），一次询问用户 — 与其他任何初始问题批量处理。
4. **如果都不可用**，则告知用户并询问如何操作。

**⛔ 永远不要用 SVG、HTML、canvas 或其他代码渲染来替代光栅图像生成。** Codex `imagegen` 自己的描述说它应该用于“当输出应该是位图资源而不是仓库原生代码或矢量时”。如果您无法通过步骤 3 解决光栅后端，则应降级到步骤 4 并询问用户 — 不要静默地发出 SVG、写入内联 `<svg>` 标记或生成 HTML/CSS 艺术品作为替代。即使文章/部分看起来“类似图表”也是如此：调用此规则的消费技能已经决定需要光栅图像。

**⛔ 永远不要通过在生成的光栅图像上绘画来修复渲染的文本。** 不要使用 ImageMagick、Pillow、Canvas、SVG、HTML/CSS、OCR 脚本或任何其他程序化叠加来覆盖、重写、擦除或替换已生成插图中任何已存在的文本。如果文本错误或不清晰，请从更正后的提示中重新生成、使用较少或无图像文本重新绘制，或询问用户要保留哪个不完美的候选者。

设置 `preferred_image_backend: ask` 会强制在每次运行时都提示用户，无论是否有可用后端。用户通过下方“## 修改偏好设置”部分更改固定后端。

**提示文件要求（硬性要求）**：在调用任何后端之前，将每个图像的完整最终提示写入 `prompts/` 下的独立文件（命名：`NN-{type}-[slug].md`）。后端接收提示文件（或其内容）；该文件是可重复性记录，并允许您在不重新生成提示的情况下切换后端。

上方的具体工具名称（`imagegen`、`GenerateImage`、`image_generate`、`baoyu-image-gen`）仅为示例 — 请按相同规则替换本地等效工具。

## 批量生成策略

在运行中每个提示文件都保存并验证后，默认按批量生成图像。

优先级顺序：

1. 如果选择的后端存在原生批处理/多任务接口，则使用它。每个任务必须保持自己的提示文件、输出路径、宽高比和直接参考图像。
2. 如果没有原生批处理接口，但运行时可以发出并行工具调用，则一次派遣最多 `generation_batch_size` 张图像。默认：`4`。当前消息中的显式用户请求（例如 `--batch-size 4` 或“并行4张一起生成”）会覆盖 EXTEND.md。
3. 如果既没有原生批处理也没有并行工具调用可用，则按顺序生成。

规则：

- 只有在所有该批次对应的提示文件都存在于磁盘上时，才启动第一个批次。
- 重新生成失败的项目一次，不要重新生成成功的项目。
- 不要使用子代理仅仅是为了并行化图像渲染。仅使用子代理进行单独的提示迭代或创意探索。

## 确认策略

默认行为：**生成前确认**。

- 将显式技能调用、文件路径、匹配的信号/预设和 `EXTEND.md` 默认值视为**建议输入仅**。它们都不授权跳过确认。
- **不要**在用户完成步骤 3 之前开始步骤 4 或后续步骤。
- 仅在当前请求明确说明这样做时才跳过确认，例如：“直接生成”、“不用确认”、“跳过确认”、“按默认出图”或等效措辞。
- 如果明确跳过确认，则在生成之前，在下一个面向用户更新中声明所假设的类型/密度/风格/色彩/语言/后端。

## 参考图像

用户可以通过 `--ref <files...>` 或通过提供文件路径/在对话中粘贴图像来提供参考图像。参考图像指导特定插画的风格、色彩、构图或主题。

完整检测、存储和处理规则在 [references/workflow.md](references/workflow.md)（步骤 1.0 保存到 `references/NN-ref-{slug}.{ext}`；步骤 5.3 按每幅插图使用 `direct | style | palette` 处理）。当选择的后端支持批量输入时，每个提示文件的 `references:` 前置符中的 `direct` 使用条目应传播到其批量有效负载，以便后端可以将其传递（例如，`baoyu-image-gen` 接受每个任务的 `ref`）。

## 三维度

| 维度 | 控制 | 示例 |
|-------|------|------|
| **类型** | 信息结构 | 信息图表、场景、流程图、比较、框架、时间线 |
| **风格** | 渲染方法 | notion、温暖、简约、蓝图、水彩、优雅 |
| **色彩** | 色彩方案（可选） | 马卡龙、温暖、霓虹 — 覆盖风格的默认颜色 |

自由组合：`--type infographic --style vector-illustration --palette macaron`

或者使用预设：`--preset edu-visual` → 类型 + 风格 + 色彩在一个标志中。参见 [Style Presets](references/style-presets.md)。

## 类型

| 类型 | 适用场景 |
|------|----------|
| `infographic` | 数据、指标、技术 |
| `scene` | 叙事、情感 |
| `flowchart` | 流程、工作流 |
| `comparison` | 并列、选项 |
| `framework` | 模型、架构 |
| `timeline` | 历史、演变 |

## 风格

参见 [references/styles.md](references/styles.md) 获取核心风格、完整画廊和类型 × 风格兼容性。

## 工作流

```
- [ ] 步骤 1：预检查（EXTEND.md、参考、配置）
- [ ] 步骤 2：分析内容
- [ ] 步骤 3：确认设置（AskUserQuestion）
- [ ] 步骤 4：生成大纲
- [ ] 步骤 5：生成图像
- [ ] 步骤 6：最终化
```

### 步骤 1：预检查

**1.5 加载偏好设置（EXTEND.md） ⛔ 阻塞**

按优先级顺序检查 EXTEND.md — 第一个找到的将获胜：

| 优先级 | 路径 | 范围 |
|--------|------|------|
| 1 | `.baoyu-skills/baoyu-article-illustrator/EXTEND.md` | 项目 |
| 2 | `${XDG_CONFIG_HOME:-$HOME/.config}/baoyu-skills/baoyu-article-illustrator/EXTEND.md` | XDG |
| 3 | `$HOME/.baoyu-skills/baoyu-article-illustrator/EXTEND.md` | 用户主目录 |

| 结果 | 操作 |
|------|------|
| 找到 | 读取、解析、显示摘要 |
| 未找到 | ⛔ 运行 [first-time-setup](references/config/first-time-setup.md) |

完整程序：[references/workflow.md](references/workflow.md#step-1-pre-check)

### 步骤 2：分析

| 分析 | 输出 |
|------|------|
| 内容类型 | 技术/教程/方法论/叙事 |
| 目的 | 信息/可视化/想象 |
| 核心论点 | 2-5 个主要论点 |
| 位置 | 插画增加价值的位置 |

**关键**：隐喻 → 可视化底层概念，而不是字面图像。

完整程序：[references/workflow.md](references/workflow.md#step-2-setup--analyze)

### 步骤 3：确认设置 ⚠️

**硬性门槛**：根据 [确认策略](#confirmation-policy)，此步骤是强制性的 — 步骤 4+ 不能在此处确认用户（或当前请求中明确使用“直接生成”/等效措辞选择跳过）之前开始。

**一个 AskUserQuestion，最多 4 个问题。Q1-Q2 必须执行。Q3 在选择预设时不需要执行。**

| Q | 选项 |
|---|------|
| **Q1：预设或类型** | [推荐预设]、[其他预设]，或手动：信息图表、场景、流程图、比较、框架、时间线、混合 |
| **Q2：密度** | 简约（1-2）、均衡（3-5）、按节（推荐）、丰富（6+） |
| **Q3：风格** | [推荐]、简约平面、科幻、手绘、编辑、场景、海报、其他 — **如果选择预设则跳过** |
| Q4：色彩 | 默认（风格颜色）、马卡龙、温暖、霓虹 — **如果预设包含色彩或 `preferred_palette` 已设置则跳过** |
| Q5：语言 | 当文章语言 ≠ EXTEND.md 设置时 |

完整程序：[references/workflow.md](references/workflow.md#step-3-confirm-settings-)

### 步骤 4：生成大纲

保存 `outline.md`，包含前置符（类型、密度、风格、色彩、图像数量）和条目：

```yaml
## 插画 1
**位置**： [章节/段落]
**目的**： [为什么]
**视觉内容**： [什么]
**文件名**： 01-infographic-concept-name.png
```

完整模板：[references/workflow.md](references/workflow.md#step-4-generate-outline)

### 步骤 5：生成图像

⛔ **阻塞**：提示文件必须在任何图像生成之前保存。这是一个硬性要求，无论选择哪个后端 — 提示文件是可重复性记录。

1. 对于每个插画，根据 [references/prompt-construction.md](references/prompt-construction.md) 创建一个提示文件。
2. 保存到 `prompts/NN-{type}-{slug}.md`，带有 YAML 前置符。
3. 提示**必须**使用类型特定模板，具有结构化部分（ZONES / LABELS / COLORS / STYLE / ASPECT）
4. LABELS**必须**包含文章特定数据：实际数字、术语、指标、引言
5. **不要**在保存提示文件之前，不通过 `--prompt` 传递临时提示
6. 通过顶部的 `## 图像生成工具` 规则选择后端：使用任何可用的；如果多个，一次询问用户。在会话中生成之前只做一次。
   - **`codex-imagegen` 调用**：当规则解析为 `codex-imagegen` 时，请参阅 [references/codex-imagegen.md](references/codex-imagegen.md) 获取调用契约（首选 `baoyu-image-gen --provider codex-cli` 路径、运行时包装器发现、参数说明、stdout 模式、批量语义）。
7. **执行策略**：根据 `## 批量生成策略` 按批量生成：首先使用后端原生批量，其次使用运行时并行工具调用，仅作为后备使用顺序生成。默认批量大小为 4，除非 EXTEND.md 或当前请求覆盖它。
8. 根据提示前置符处理参考 (`direct`/`style`/`palette`)
9. 如果 EXTEND.md 启用，则应用水印
10. 从保存的提示文件生成；失败时重试一次

完整程序：[references/workflow.md](references/workflow.md#step-5-generate-images)

### 步骤 6：最终化

在段落之后插入 `![description]({relative-path}/NN-{type}-{slug}.png)`。路径根据输出目录设置，相对于文章文件计算。

```
文章插画完成！
文章：[路径] | 类型：[类型] | 密度：[级别] | 风格：[风格] | 色彩：[色彩或默认]
图像：X/N 生成
```

## 输出目录

输出目录由 EXTEND.md 中的 `default_output_dir` 决定（在首次设置期间设置）：

| `default_output_dir` | 输出路径 | Markdown 插入路径 |
|----------------------|----------|----------------------|
| `imgs-subdir`（默认） | `{article-dir}/imgs/` | `imgs/NN-{type}-{slug}.png` |
| `same-dir` | `{article-dir}/` | `NN-{type}-{slug}.png` |
| `illustrations-subdir` | `{article-dir}/illustrations/` | `illustrations/NN-{type}-{slug}.png` |
| `independent` | `illustrations/{topic-slug}/` | `illustrations/{topic-slug}/NN-{type}-{slug}.png`（相对于当前工作目录） |

所有辅助文件（大纲、提示）都保存在输出目录内：

```
{output-dir}/
├── outline.md
├── prompts/
│   └── NN-{type}-{slug}.md
└── NN-{type}-{slug}.png
```

当输入是**粘贴内容**（没有文件路径）时，始终使用 `illustrations/{topic-slug}/`，并将 `source-{slug}.{ext}` 保存在旁边。

**Slug**：2-4 个单词，kebab-case。**冲突**：追加 `-YYYYMMDD-HHMMSS`。

## 修改

| 操作 | 步骤 |
|------|------|
| 编辑 | 更新提示 → 重新生成 → 更新参考 |
| 添加 | 位置 → 提示 → 生成 → 更新大纲 → 插入 |
| 删除 | 删除文件 → 移除参考 → 更新大纲 |

文本更正策略：

- 如果任何渲染的文本（标签、标题等）拼写错误、混乱、难以阅读或视觉上较弱，不要用代码覆盖光栅图像。
- 对于文本更正重新生成的，请编写新的提示文件和新的输出路径，以便保留有缺陷的候选者以供比较。
- 后处理仅限于裁剪、调整大小、压缩或格式转换，这些操作不会改变文本或主要构图。

## 参考

| 文件 | 内容 |
|------|------|
| [references/workflow.md](references/workflow.md) | 详细程序 |
| [references/usage.md](references/usage.md) | 命令语法 |
| [references/styles.md](references/styles.md) | 风格画廊 + 色彩画廊 |
| [references/style-presets.md](references/style-presets.md) | 预设快捷方式（类型 + 风格 + 色彩） |
| [references/prompt-construction.md](references/prompt-construction.md) | 提示模板 |
| [references/config/first-time-setup.md](references/config/first-time-setup.md) | 首次设置 |

## 修改偏好设置

EXTEND.md 位于步骤 1.5 列出的第一个匹配路径。更改它的三种方法：

- **直接编辑** — 打开 EXTEND.md 并更改字段。完整模式：`references/config/preferences-schema.md`。
- **交互式重新配置** — 删除 EXTEND.md（或询问“重新配置 baoyu-article-illustrator 偏好设置”/“重新配置”）。下一次运行会重新触发首次设置。
- **常见的单行编辑**：
  - `preferred_image_backend: auto` — 默认；运行时原生工具获胜，降级到唯一安装的后端，仅在存在多个非原生时询问。
  - `preferred_image_backend: codex-imagegen` — 固定到 Codex 的内置。
  - `preferred_image_backend: baoyu-image-gen` — 固定到 baoyu-image-gen 技能。
  - `preferred_image_backend: ask` — 每次运行都确认后端。
  - `generation_batch_size: 4` — 默认并发渲染的图像数量，当运行时支持并行生成调用时。
  - `preferred_type: infographic`，`preferred_style: notion`，`preferred_palette: macaron`，`language: zh`。
  - `default_output_dir: imgs-subdir` — 生成图像的相对路径。
