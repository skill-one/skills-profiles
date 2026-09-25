# 知识漫画创作器

创建具有灵活艺术风格×色调组合的原创知识漫画。

## 用户输入工具

当此技能提示用户时，请遵循以下工具选择规则（优先级顺序）：

1. **优先使用**当前代理运行时暴露的**内置用户输入工具** — 例如，`AskUserQuestion`、`request_user_input`、`clarify`、`ask_user`，或任何等效工具。
2. **备用方案**：如果不存在此类工具，则发出编号的纯文本消息，并要求用户回复所选编号/答案以回答每个问题。
3. **批量处理**：如果该工具支持每调用一次处理多个问题，则将所有适用问题合并为单个调用；如果仅支持单个问题，则按优先级顺序逐一询问。

下方的具体 `AskUserQuestion` 引用仅为示例 — 在其他运行时环境中，请替换本地等效工具。

## 图像生成工具

当此技能需要渲染图像时，按以下顺序解析后端：

1. **当前请求覆盖** — 如果用户在当前消息中指定了特定的后端，则使用它。
2. **保存的偏好设置** — 如果 `EXTEND.md` 将 `preferred_image_backend` 设置为当前可用的后端，则使用它。
3. **自动选择**（当偏好设置为 `auto`、未设置或固定后端不可用时）：
   - **Codex (`imagegen`)** — 首先，检查您的可用技能/工具清单。如果列出了名为 `imagegen` 的技能，则表示您正在 Codex 环境中运行，并且**必须**使用它：通过 `Skill` 工具以 `skill: "imagegen"` 调用它，并将保存的提示文件内容（以及输出路径和宽高比，根据 Codex `imagegen` 自身的参数）传递给它。Codex `imagegen` 是该运行时中的官方光栅后端，优先于任何非原生技能（例如，`baoyu-image-gen`），除非用户明确固定了不同的 `preferred_image_backend`。
   - **通过 `codex exec` 的 Codex (`codex-imagegen`)** — 如果当前运行时不暴露原生 `imagegen` 技能，但 `codex` CLI 位于 `PATH` 上且 `codex login` 处于活动状态，则通过 `baoyu-image-gen --provider codex-cli`（首选）路由（如果 `baoyu-image-gen` 不可用，则调用捆绑的包装器）。详细信息、参数和运行时发现程序位于 [references/codex-imagegen.md](references/codex-imagegen.md) — 仅在选中此分支时加载该文件。
   - **Cursor (`GenerateImage`)** — 如果运行时暴露了原生 `GenerateImage` 工具，则表示您正在 Cursor 环境中运行，并且其优先级与非原生技能与 Codex `imagegen` 相同。两个严格的限制条件：(a) 它没有宽高比参数 — 必须在传递给 `description` 的提示文本中明确说明目标宽高比/尺寸；(b) 它不接受输出目录 — 它将保存到工具管理的位置，因此生成后需要将文件复制/移动到技能的预期输出路径（例如，`outputs/.../NN-xxx.png`）。参考图像放在 `reference_image_paths`。
   - **其他运行时原生工具** — 如果运行时暴露了不同的原生图像工具（例如，Hermes `image_generate`），则按相同方式使用它。
   - 否则，如果恰好安装了一个非原生后端（例如，`baoyu-image-gen`），则使用它。
   - 否则（存在多个非原生后端且没有运行时原生工具），一次询问用户 — 与其他任何初始问题批量处理。
4. **如果都不可用**，则告知用户并询问如何继续。

**⛔ 永远不要用 SVG、HTML、canvas 或其他基于代码的渲染来替代光栅图像生成。** Codex `imagegen` 自己的描述说它应该用于“当输出应该是位图资源而不是存储库原生代码或矢量时”。如果您无法通过步骤 3 解析光栅后端，则应降级到步骤 4 并询问用户 — 不要静默地发出 SVG、写入内联 `<svg>` 标记或生成 HTML/CSS 艺术作品作为替代。即使文章/部分看起来像“图表”，这也适用：调用此规则的消费者技能已经决定需要光栅图像。

**⛔ 永远不要通过在生成的光栅图像上绘画来修复渲染的文本。** 不要使用 ImageMagick、Pillow、Canvas、SVG、HTML/CSS、OCR 脚本或任何其他程序化叠加来覆盖、重写、擦除、描边或替换已生成漫画页面中的对话、音效、面板标签或任何其他文本。如果文本错误或不清晰，请从更正后的提示中重新生成，重新绘制带有较少或无图像文本的页面，或询问用户要保留哪个不完美的候选者。

将 `preferred_image_backend: ask` 设置为强制每次运行都提示步骤 3 的偏好设置，而不管是否有可用后端。用户通过下方“## 更改偏好设置”部分更改固定后端。

**提示文件要求（硬性要求）**：在调用任何后端之前，将每个图像的完整最终提示写入 `prompts/` 下的独立文件（命名：`NN-{type}-[slug].md`）。后端接收提示文件（或其内容）；该文件是可重复性记录，并允许您在不重新生成提示的情况下切换后端。

上方的具体工具名称（`imagegen`、`GenerateImage`、`image_generate`、`baoyu-image-gen`）仅为示例 — 按相同规则替换本地等效工具。

## 批量生成策略

在当前生成组的每个提示文件都已保存并验证后，默认按批量生成图像。

优先级顺序：

1. 如果有，则使用所选后端的原生批处理/多任务接口。每个任务必须保持自己的提示文件、输出路径、宽高比、会话 ID 和直接参考图像。
2. 如果没有原生批处理接口，但运行时可以发出并行工具调用，则一次最多分派 `generation_batch_size` 张图像。默认：`4`。当前消息中的明确用户请求（例如 `--batch-size 4` 或“并行4张一起生成”）会覆盖 EXTEND.md。
3. 如果既没有原生批处理也没有并行工具调用可用，则按顺序生成。

规则：

- 首先尊重工作流依赖关系：在使用它作为参考的页面之前生成 `characters/characters.png`。
- 在所有选定的页面提示文件都存在于磁盘上之前，永远不要开始第一个页面批处理。
- 一次重试失败的项目，不要重新生成成功的项目。
- 不要仅用于并行化图像渲染而使用子代理。仅当用于单独的提示迭代或创意探索时才使用子代理。

## 参考图像

用户可以提供参考图像来指导艺术风格、调色板、场景构图或主题。这与自动生成的角色表（步骤 7.1）**分开** — 两者可以共存：用户参考指导外观，角色表锚定重复的角色身份。

**输入**：通过 `--ref <files...>` 或当用户在对话中提供文件路径/粘贴图像来接受。
- 文件路径 → 与漫画输出一起复制到 `refs/NN-ref-{slug}.{ext}`
- 没有路径粘贴的图像 → 根据上方的用户输入工具规则询问用户路径，或作为文本备用方案提取风格特征
- 无参考 → 跳过此部分

**使用模式**（每个参考）：

| 使用 | 效果 |
|-------|-------|
| `direct` | 将文件作为参考图像在每一页（或选定页面）传递给后端 |
| `style` | 提取风格特征（线条处理、纹理、情绪）并追加到每一页的提示正文 |
| `palette` | 提取十六进制颜色并追加到每一页的提示正文 |

在每一页的提示文件 frontmatter 中记录参考图像存在时：

```yaml
references:
  - ref_id: 01
    filename: 01-ref-scene.png
    usage: direct
```

**生成时**：
- 验证每个参考文件是否存在于磁盘上
- 如果 `usage: direct` **且**所选后端接受多个参考图像 → 通过后端的 ref 参数传递角色表（步骤 7.2）和用户参考；根据步骤 7.1 的指导先压缩图像以避免有效载荷失败
- 如果后端只接受一个 ref → 对于具有重复角色的页面优先使用角色表；将用户参考特征嵌入提示正文
- 对于 `style`/`palette` 使用 → 将提取的特征嵌入到每一页的提示文本中（无论后端能力如何）

上方的具体工具名称（`imagegen`、`GenerateImage`、`image_generate`、`baoyu-image-gen`）仅为示例 — 按相同规则替换本地等效工具。

## 选项

### 视觉尺寸

| 选项 | 值 | 描述 |
|-------|-------|-------|
| `--art` | ligne-claire（默认）、manga、realistic、ink-brush、chalk、minimalist | 艺术风格/渲染技术 |
| `--tone` | neutral（默认）、warm、dramatic、romantic、energetic、vintage、action | 情绪/氛围 |
| `--layout` | standard（默认）、cinematic、dense、splash、mixed、webtoon、four-panel | 面板布局 |
| `--aspect` | 3:4（默认，肖像）、4:3（横向）、16:9（宽屏） | 页面宽高比 |
| `--lang` | auto（默认）、zh、en、ja、等 | 输出语言 |
| `--ref <files...>` | 文件路径 | 应用于每一页的参考图像，用于风格/调色板/场景指导。见上方“## 参考图像”。 |
| `--batch-size <n>` | 1-8 | 此运行中临时页面生成批处理大小。默认：EXTEND.md 中的 `generation_batch_size`，否则 4。 |

### 部分工作流选项

| 选项 | 描述 |
|-------|-------|
| `--storyboard-only` | 仅生成故事板，跳过提示和图像 |
| `--prompts-only` | 生成故事板+提示，跳过图像 |
| `--images-only` | 从现有提示目录生成图像 |
| `--regenerate N` | 仅重新生成特定页面（例如，`3` 或 `2,5,8`） |

详细信息：[references/partial-workflows.md](references/partial-workflows.md)

### 艺术、色调与预设目录

- **艺术风格**（6）：`ligne-claire`、`manga`、`realistic`、`ink-brush`、`chalk`、`minimalist`。完整定义位于 `references/art-styles/<style>.md`。
- **色调**（7）：`neutral`、`warm`、`dramatic`、`romantic`、`energetic`、`vintage`、`action`。完整定义位于 `references/tones/<tone>.md`。
- **预设**（5）具有超出普通艺术+色调的特殊规则：

  | 预设 | 等效 | 钩子 |
  |-------|-------|------|
  | `ohmsha` | manga + neutral | 视觉隐喻、无对话头、装置揭示 |
  | `wuxia` | ink-brush + action | 气效果、战斗视觉效果、氛围 |
  | `shoujo` | manga + romantic | 装饰元素、眼睛细节、浪漫节奏 |
  | `concept-story` | manga + warm | 视觉符号系统、成长弧、对话+动作平衡 |
  | `four-panel` | minimalist + neutral + four-panel layout | 起承转合结构、黑白+点阵色、火柴人角色 |

  完整规则位于 `references/presets/<preset>.md` — 选择预设时加载该文件。

  兼容性矩阵和**内容信号→预设**表位于 [references/auto-selection.md](references/auto-selection.md)。在步骤 2 中推荐组合之前，请阅读它。

- **EXTEND.md** 中的**内容信号**和**预设**表支持：水印、首选艺术/色调/布局、自定义风格定义、角色预设、语言偏好、首选图像后端、生成批处理大小。模式：[references/config/preferences-schema.md](references/config/preferences-schema.md)。

## 脚本目录

**重要**：所有脚本都位于此技能的 `scripts/` 子目录中。

**代理执行说明**：
1. 确定此 `SKILL.md` 文件的目录路径作为 `{baseDir}`
2. 脚本路径 = `{baseDir}/scripts/<script-name>.ts`
3. 将此文档中的所有 `{baseDir}` 替换为实际路径
4. 解析 `${BUN_X}` 运行时：如果安装了 `bun` → `bun`；如果 `npx` 可用 → `npx -y bun`；否则建议安装 bun

**脚本参考**：
| 脚本 | 目的 |
|-------|-------|
| `scripts/merge-to-pdf.ts` | 合并漫画页面到 PDF |

## 文件结构

输出目录：`comic/{topic-slug}/`
- Slug：从主题中提取的 2-4 个单词的 kebab-case（例如，`alan-turing-bio`）
- 冲突：附加时间戳（例如，`turing-story-20260118-143052`）

**内容**：
| 文件 | 描述 |
|-------|-------|
| `source-{slug}.{ext}` | 源文件 |
| `analysis.md` | 内容分析 |
| `storyboard.md` | 带面板分解的故事板 |
| `characters/characters.md` | 角色定义 |
| `characters/characters.png` | 角色参考表 |
| `prompts/NN-{cover\|page}-[slug].md` | 生成提示 |
| `NN-{cover\|page}-[slug].png` | 生成的图像 |
| `{topic-slug}.pdf` | 最终合并的 PDF |

## 语言处理

**检测优先级**：
1. `--lang` 标志（明确）
2. EXTEND.md `language` 设置
3. 用户的对话语言
4. 源内容语言

**规则**：使用用户的输入语言或保存的语言偏好设置进行所有交互：
- 故事板大纲和场景描述
- 图像生成提示
- 用户选择选项和确认
- 进度更新、问题、错误、摘要

技术术语保持为英文。

## 工作流

### 进度检查清单

```
漫画进度：
- [ ] 步骤 1：设置与分析
  - [ ] 1.1 偏好设置 (EXTEND.md) ⛔ 阻塞
    - [ ] 已找到 → 加载偏好设置 → 继续
    - [ ] 未找到 → 运行首次设置 → 必须在执行其他步骤之前完成
  - [ ] 1.2 分析，1.3 检查现有
- [ ] 步骤 2：确认 - 风格和选项 ⚠️ 必须执行
- [ ] 步骤 3：生成故事板+角色
- [ ] 步骤 4：审查大纲（有条件）
- [ ] 步骤 5：生成提示
- [ ] 步骤 6：审查提示（有条件）
- [ ] 步骤 7：生成图像
  - [ ] 7.1 生成角色表（如果需要）→ characters/characters.png
  - [ ] 7.2 生成页面（如有角色表则使用 `--ref`）
- [ ] 步骤 8：合并到 PDF
- [ ] 步骤 9：完成报告
```

### 流程

```
输入 → [偏好设置] ─┬─ 已找到 → 继续
                       │
                       └─ 未找到 → 首次设置 ⛔ 阻塞
                                      │
                                      └─ 完成设置 → 保存 EXTEND.md → 继续
                                                                              │
        ┌─────────────────────────────────────────────────────────────────────┘
        ↓
分析 → [检查现有?] → [确认：风格+审查] → 故事板 → [审查?] → 提示 → [审查?] → 图像 → PDF → 完成
```

### 步骤摘要

| 步骤 | 操作 | 关键输出 |
|-------|-------|----------|
| 1.1 | 加载 EXTEND.md 偏好设置 ⛔ 阻塞如果未找到 | 配置已加载 |
| 1.2 | 分析内容 | `analysis.md` |
| 1.3 | 检查现有目录 | 处理冲突 |
| 2 | 确认风格、焦点、受众、审查 | 用户偏好 |
| 3 | 生成故事板+角色 | `storyboard.md`，`characters/` |
| 4 | 审查大纲（如果请求） | 用户批准 |
| 5 | 生成提示 | `prompts/*.md` |
| 6 | 审查提示（如果请求） | 用户批准 |
| 7.1 | 生成角色表（如果需要） | `characters/characters.png` |
| 7.2 | 生成页面（如有角色参考则使用） | `*.png` 文件 |
| 8 | 合并到 PDF | `{slug}.pdf` |
| 9 | 完成报告 | 摘要 |

### 步骤 7：图像生成

**每次会话选择一个后端**，使用顶部的“## 图像生成工具”规则。如果后端是存储库技能（例如，`baoyu-image-gen`），请阅读其 `SKILL.md` 并使用其文档接口，而不是其脚本。

**`codex-imagegen` 调用**：当规则解析为 `codex-imagegen` 时，请参阅 [references/codex-imagegen.md](references/codex-imagegen.md) 了解调用契约（首选 `baoyu-image-gen --provider codex-cli` 路径、运行时包装器发现、参数说明、stdout 模式、批量语义 — 每次调用 n=1，因此页面批量必须分派一个包装器调用每页）。

**7.1 角色表** — 当漫画是多页且具有重复角色时，生成它（到 `characters/characters.png`，宽高比 `4:3`）。对于简单预设（例如，four-panel minimalist）或单页漫画则跳过。根据步骤 7.1 的指导压缩为 JPEG 以避免有效载荷失败。在用作 `--ref` 之前，必须存在 `characters/characters.md` 中的提示文件。

**7.2 页面** — 每个页面的提示必须在调用后端之前已经位于 `prompts/NN-{cover|page}-[slug].md` 中；该文件是可重复性记录。策略取决于角色表：

| 角色表 | 后端 `--ref` | 策略 |
|-----------------|-----------------|----------|
| 存在 | 支持 | 在每一页上作为 `--ref` 传递表 |
| 存在 | 不支持 | 将角色描述追加到每个提示文件 |
| 跳过 | — | 所有描述嵌入在提示中 |

**执行策略**：当需要时，首先生成角色表。然后从保存的提示文件构建选定的页面任务列表，并按“## 批量生成策略”分派页面：首先使用后端原生批处理，其次使用运行时并行工具调用，仅作为备用按顺序执行。`--regenerate N` 和 `--images-only` 对选定的现有提示应用相同的批量规则。

**备用规则**：现有的 `prompts/…md` 和 `…png` 文件 → 在重新生成之前添加 `-backup-YYYYMMDD-HHMMSS` 后缀。宽高比来自故事板（默认 `3:4`；预设可能覆盖）。

**`--ref` 失败恢复**：压缩表 → 重试 → 仍然失败 → 放弃 `--ref` 并将角色描述嵌入提示文本。

完整步骤工作流（分析、故事板、审查门禁、再生变体）：[references/workflow.md](references/workflow.md).

### EXTEND.md 路径 ⛔ 阻塞

如果找不到 EXTEND.md，首次设置是**阻塞**的 — 在进行任何内容分析或风格/色调问题之前完成它。

| 优先级 | 路径 | 范围 |
|----------|------|-------|
| 1 | `.baoyu-skills/baoyu-comic/EXTEND.md` | 项目 |
| 2 | `$HOME/.baoyu-skills/baoyu-comic/EXTEND.md` | 用户主目录 |

| 结果 | 操作 |
|--------|--------|
| 找到 | 读取、解析、显示摘要 → 继续 |
| 未找到 | ⛔ 运行首次设置 ([references/config/first-time-setup.md](references/config/first-time-setup.md)) → 保存 EXTEND.md → 继续 |

**EXTEND.md 支持**：水印、首选艺术/色调/布局、自定义风格定义、角色预设、语言偏好、首选图像后端、生成批处理大小。模式：[references/config/preferences-schema.md](references/config/preferences-schema.md).

## 参考

**核心模板**：
- [analysis-framework.md](references/analysis-framework.md) - 深度内容分析
- [character-template.md](references/character-template.md) - 角色定义格式
- [storyboard-template.md](references/storyboard-template.md) - 故事板结构
- [ohmsha-guide.md](references/ohmsha-guide.md) - Ohmsha 漫画特定内容

**风格定义**：
- `references/art-styles/` - 艺术风格（ligne-claire、manga、realistic、ink-brush、chalk、minimalist）
- `references/tones/` - 色调（neutral、warm、dramatic、romantic、energetic、vintage、action）
- `references/presets/` - 具有特殊规则的预设（ohmsha、wuxia、shoujo、concept-story、four-panel）
- `references/layouts/` - 布局（standard、cinematic、dense、splash、mixed、webtoon、four-panel）

**工作流**：
- [workflow.md](references/workflow.md) - 完整工作流细节
- [auto-selection.md](references/auto-selection.md) - 内容信号分析
- [partial-workflows.md](references/partial-workflows.md) - 部分工作流选项

**配置**：
- [config/preferences-schema.md](references/config/preferences-schema.md) - EXTEND.md 模式
- [config/first-time-setup.md](references/config/first-time-setup.md) - 首次设置
- [config/watermark-guide.md](references/config/watermark-guide.md) - 水印配置

## 页面修改

| 操作 | 步骤 |
|-------|-------|
| **编辑** | **首先更新提示文件** → `--regenerate N` → 重新生成 PDF |
| **添加** | 在位置创建提示 → 使用角色参考生成 → 重新编号后续 → 更新故事板 → 重新生成 PDF |
| **删除** | 删除文件 → 重新编号后续 → 更新故事板 → 重新生成 PDF |

**重要**：在更新页面时，**始终首先更新提示文件** (`prompts/NN-{cover|page}-[slug].md`) 之前再重新生成。这确保了更改被记录且可重复。

文本更正政策：

- 如果对话、音效、面板标签或任何其他渲染文本拼写错误、混乱、难以阅读或视觉效果差，**不要**用代码修补位图。
- 对于文本更正再生，请编写新的提示文件和新的输出路径，以便保留有缺陷的候选者以供比较。
- 后处理仅限于裁剪、调整大小、压缩或格式转换，不能改变文本或主要构图。

## 注意事项

- 图像生成：每页 10-30 秒
- 自动重试一次生成失败
- 使用风格化替代方案处理敏感公众人物
- 通过会话 ID 保持风格一致性
- **步骤 2 确认需要** - 不要跳过
- **步骤 4/6 有条件** - 仅当用户在步骤 2 中请求时
- **步骤 7.1 角色表** - 推荐用于多页漫画，简单预设（例如 four-panel minimalist）或单页漫画可选
- **步骤 7.2 角色参考** - 如果表存在则使用 `--ref`；失败时压缩/转换；回退到仅提示
- 水印/语言配置一次在 EXTEND.md 中设置

## 更改偏好设置

EXTEND.md 位于 `.baoyu-skills/baoyu-comic/EXTEND.md`（项目）或 `~/.baoyu-skills/baoyu-comic/EXTEND.md`（用户）。更改它的三种方式：

- **直接编辑** — 打开 EXTEND.md 并更改字段。完整模式：`references/config/preferences-schema.md`。
- **交互式重新配置** — 删除 EXTEND.md（或询问“重新配置 baoyu-comic 偏好设置” / “重新配置”）。下一次运行会重新触发首次设置。
- **常见的单行编辑**：
  - `preferred_image_backend: auto` — 默认；运行时原生工具获胜，回退到唯一安装的后端，仅在存在多个非原生时询问。
  - `preferred_image_backend: codex-imagegen` — 固定到 Codex 的内置。
  - `preferred_image_backend: baoyu-image-gen` — 固定到 baoyu-image-gen 技能。
  - `preferred_image_backend: ask` — 每次运行都确认后端。
  - `generation_batch_size: 4` — 默认同时渲染的页面图像数量，当后端/运行时支持批量或并行生成时。默认：EXTEND.md 中的 `generation_batch_size`，否则 4。
  - `watermark.enabled: true`, `preferred_art`, `preferred_tone`, `preferred_layout`, `language` — 调整自动选择默认值和装饰性选择。
