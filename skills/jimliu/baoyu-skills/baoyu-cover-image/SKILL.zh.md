---
name: baoyu-cover-image
description: 生成具有5个维度（类型、调色板、渲染方式、文字、氛围）的文章封面图片，结合11种调色板和7种渲染风格。支持电影感（2.35:1）、宽屏（16:9）和方形（1:1）的宽高比。当用户要求“生成封面图片”、“创建文章封面”或“制作封面”时使用。
---

# 封面图像生成器

为文章生成具有五维定制的优雅封面图像。

## 用户输入工具

当此技能提示用户时，请遵循以下工具选择规则（优先级顺序）：

1. **优先使用**当前代理运行时暴露的**内置用户输入工具** — 例如，`AskUserQuestion`、`request_user_input`、`clarify`、`ask_user` 或任何等效工具。
2. **降级处理**：如果没有此类工具，则发出编号的纯文本消息，并要求用户回复选择的编号/答案以回答每个问题。
3. **批量处理**：如果工具支持每调用一次询问多个问题，则将所有适用问题合并为单个调用；如果仅支持单个问题，则按优先级顺序逐个询问。

下方的具体 `AskUserQuestion` 引用仅为示例 — 在其他运行时中替换本地等效工具。

## 图像生成工具

当此技能需要渲染图像时，按以下顺序解析后端：

1. **当前请求覆盖** — 如果用户在当前消息中指定了特定的后端，则使用它。
2. **保存的偏好设置** — 如果 `EXTEND.md` 将 `preferred_image_backend` 设置为当前可用的后端，则使用它。
3. **自动选择**（当偏好设置为 `auto`、未设置或固定的后端不可用时）：
   - **Codex (`imagegen`)** — 首先，检查您的可用技能/工具清单。如果列出了名为 `imagegen` 的技能，则表示您正在 Codex 环境中运行，并且**必须**使用它：通过 `Skill` 工具以 `skill: "imagegen"` 调用，并将保存的提示文件内容（以及输出路径和宽高比，根据 Codex `imagegen` 自身的参数）传递给它。Codex `imagegen` 是该运行时中的官方光栅后端，优先于任何非原生技能（例如，`baoyu-image-gen`），除非用户显式固定了不同的 `preferred_image_backend`。
   - **通过 `codex exec` 的 Codex (`codex-imagegen`)** — 如果当前运行时不暴露原生 `imagegen` 技能，但 `codex` CLI 位于 `PATH` 上且 `codex login` 处于活动状态，则通过 `baoyu-image-gen --provider codex-cli` 路由（首选），或者 — 如果 `baoyu-image-gen` 不可用 — 调用捆绑的包装器直接。详细信息、参数和运行时发现程序位于 [references/codex-imagegen.md](references/codex-imagegen.md) — 仅当选择此分支时加载该文件。
   - **Cursor (`GenerateImage`)** — 如果运行时暴露了原生 `GenerateImage` 工具，则表示您正在 Cursor 环境中运行，并且它以与 Codex `imagegen` 相同的方式优先于任何非原生技能。有两个严格的限制：(a) 它没有宽高比参数 — 在作为 `description` 传递的提示文本中明确说明目标宽高比/尺寸；(b) 它不接受输出目录 — 它保存到工具管理的位置，因此生成后需要将文件复制/移动到技能预期的输出路径（例如，`outputs/.../NN-xxx.png`）。参考图像放在 `reference_image_paths`。
   - **其他运行时原生工具** — 如果运行时暴露了不同的原生图像工具（例如，Hermes `image_generate`），则按相同方式使用它。
   - 否则，如果恰好安装了一个非原生后端（例如，`baoyu-image-gen`），则使用它。
   - 否则（存在多个非原生后端且没有运行时原生工具），一次询问用户 — 与任何其他初始问题批量处理。
4. **如果都不可用**，则告知用户并询问如何继续。

**⛔ 永远不要用 SVG、HTML、canvas 或其他基于代码的渲染来替代光栅图像生成。** Codex `imagegen` 自己的描述说它应该用于“当输出应该是位图资源而不是仓库原生代码或矢量时”。如果您无法通过步骤 3 解决光栅后端，则应降级到步骤 4 并询问用户 — 不要静默地发出 SVG、写入内联 `<svg>` 标记或生成 HTML/CSS 艺术作品作为替代。即使文章/部分看起来像“图表”，这也适用：调用此规则的消费技能已经决定需要光栅图像。

**⛔ 永远不要通过在生成的光栅图像上绘画来修复渲染的文本。** 不要使用 ImageMagick、Pillow、Canvas、SVG、HTML/CSS、OCR 脚本或任何其他程序化叠加来覆盖、重写、擦除、描边或替换已生成封面图像中的标题/副标题文本。如果文本错误或不清晰，请从更正后的提示中重新生成，切换到低文本或无标题变体，或询问用户要保留哪个不完美的候选者。

设置 `preferred_image_backend: ask` 强制在每次运行中无条件地执行步骤 3 的提示，无论是否有可用后端。用户通过下方 `## Changing Preferences` 部分更改固定的后端。

**提示文件要求（硬性要求）**：在调用任何后端之前，将每个图像的完整、最终提示写入 `prompts/` 下的独立文件（命名：`NN-{type}-[slug].md`）。后端接收提示文件（或其内容）；该文件是可重复性记录，并允许您在不重新生成提示的情况下切换后端。

上方的具体工具名称（`imagegen`、`GenerateImage`、`image_generate`、`baoyu-image-gen`）仅为示例 — 按相同规则替换本地等效工具。

## 确认策略

默认行为：**生成前确认**。

- 将显式技能调用、文件路径、匹配的关键字/预设、`EXTEND.md` 默认值以及任何文档化的自动选择视为**仅推荐输入**。它们均无权授权跳过确认。
- **不要**在用户确认尺寸/宽高比/语言/后端选择之前开始步骤 3 或步骤 4。
- 仅在当前请求明确说明这样做时才跳过确认，例如：`--quick`、"直接生成"、"不用确认"、"跳过确认"、"按默认出图" 或等效措辞。`quick_mode: true` 在 `EXTEND.md` 中计为永久显式排除 — 仅在您希望每次运行都跳过步骤 2 时设置它。
- 如果明确跳过确认，则在生成之前，在下一个面向用户更新中声明所假设的尺寸/宽高比/语言/后端。

## 选项

| 选项 | 描述 |
|------|------|
| `--type <name>` | hero（主角）、conceptual（概念性）、typography（字体排印）、metaphor（隐喻）、scene（场景）、minimal（极简） |
| `--palette <name>` | warm（暖色调）、elegant（优雅）、cool（冷色调）、dark（暗色调）、earth（大地色）、vivid（鲜艳）、pastel（柔和色调）、mono（单色）、retro（复古）、duotone（双色调）、macaron（马卡龙色） |
| `--rendering <name>` | flat-vector（平面矢量）、hand-drawn（手绘）、painterly（绘画风格）、digital（数字）、pixel（像素）、chalk（粉笔）、screen-print（丝网印刷） |
| `--style <name>` | 预设简称（参见 [Style Presets](references/style-presets.md)） |
| `--text <level>` | none（无文本）、title-only（仅标题）、title-subtitle（标题副标题）、text-rich（丰富文本） |
| `--mood <level>` | subtle（微妙）、balanced（平衡）、bold（大胆） |
| `--font <name>` | clean（干净）、handwritten（手写）、serif（衬线）、display（展示） |
| `--aspect <ratio>` | 16:9（默认）、2.35:1、4:3、3:2、1:1、3:4 |
| `--lang <code>` | 标题语言（en、zh、ja 等） |
| `--no-title` | `--text none` 的别名 |
| `--quick` | 跳过确认，使用自动选择 |
| `--ref <files...>` | 用于风格/构图指导的参考图像 |

## 五维定制

| 维度 | 值 | 默认值 |
|------|------|--------|
| **类型** | hero、conceptual、typography、metaphor、scene、minimal | auto |
| **调色板** | warm、elegant、cool、dark、earth、vivid、pastel、mono、retro、duotone、macaron | auto |
| **渲染** | flat-vector、hand-drawn、painterly、digital、pixel、chalk、screen-print | auto |
| **文本** | none、title-only、title-subtitle、text-rich | title-only |
| **情绪** | subtle、balanced、bold | balanced |
| **字体** | clean、handwritten、serif、display | clean |

自动选择规则：[references/auto-selection.md](references/auto-selection.md)

## 画廊

**类型**：hero、conceptual、typography、metaphor、scene、minimal
→ 详细信息：[references/types.md](references/types.md)

**调色板**：warm、elegant、cool、dark、earth、vivid、pastel、mono、retro、duotone、macaron
→ 详细信息：[references/palettes/](references/palettes/)

**渲染**：flat-vector、hand-drawn、painterly、digital、pixel、chalk、screen-print
→ 详细信息：[references/renderings/](references/renderings/)

**文本级别**：none（纯视觉） | title-only（默认） | title-subtitle | text-rich（带标签）
→ 详细信息：[references/dimensions/text.md](references/dimensions/text.md)

**情绪级别**：subtle（低对比度） | balanced（默认） | bold（高对比度）
→ 详细信息：[references/dimensions/mood.md](references/dimensions/mood.md)

**字体**：clean（无衬线字体） | handwritten | serif | display（粗体装饰）
→ 详细信息：[references/dimensions/font.md](references/dimensions/font.md)

## 文件结构

每个 `default_output_dir` 偏好设置对应的输出目录：
- `same-dir`：`{article-dir}/`
- `imgs-subdir`：`{article-dir}/imgs/`
- `independent`（默认）：`cover-image/{topic-slug}/`

```
<output-dir>/
├── source-{slug}.{ext}    # 源文件
├── refs/                  # 参考图像（如果提供）
│   ├── ref-01-{slug}.{ext}
│   └── ref-01-{slug}.md   # 描述文件
├── prompts/cover.md       # 生成提示
└── cover.png              # 输出图像
```

**Slug**：2-4 个单词，kebab-case。冲突：追加 `-YYYYMMDD-HHMMSS`

## 工作流程

### 进度清单

```
封面图像进度：
- [ ] 步骤 0：检查偏好设置 (EXTEND.md) ⛔ 阻塞
- [ ] 步骤 1：分析内容 + 保存参考图像 + 确定输出目录
- [ ] 步骤 2：确认选项（6 个维度） ⚠️ 除非 --quick
- [ ] 步骤 3：创建提示
- [ ] 步骤 4：生成图像
- [ ] 步骤 5：完成报告
```

### 流程

```
输入 → [步骤 0：偏好设置] ─┬─ 找到 → 继续
                           └─ 未找到 → 首次设置 ⛔ 阻塞 → 保存 EXTEND.md → 继续
        ↓
分析 + 保存参考图像 → [输出目录] → [确认：6 个维度] → 提示 → 生成 → 完成
                                              ↓
                                     （如果 --quick 或所有指定）
```

### 步骤 0：加载偏好设置 ⛔ 阻塞

按优先级顺序检查 EXTEND.md — 第一个找到的胜出：

| 优先级 | 路径 | 范围 |
|------|------|------|
| 1 | `.baoyu-skills/baoyu-cover-image/EXTEND.md` | 项目 |
| 2 | `${XDG_CONFIG_HOME:-$HOME/.config}/baoyu-skills/baoyu-cover-image/EXTEND.md` | XDG |
| 3 | `$HOME/.baoyu-skills/baoyu-cover-image/EXTEND.md` | 用户主目录 |

| 结果 | 操作 |
|------|------|
| 找到 | 加载，显示摘要 → 继续 |
| 未找到 | ⛔ 运行首次设置 ([references/config/first-time-setup.md](references/config/first-time-setup.md)) → 保存 → 继续 |

**关键**：如果未找到，请在执行任何其他步骤或问题之前完成设置。

### 步骤 1：分析内容

1. **保存参考图像**（如果提供）→ [references/workflow/reference-images.md](references/workflow/reference-images.md)
2. **保存源内容**（如果粘贴，保存到 `source.md`）
3. **分析内容**：主题、语气、关键词、视觉隐喻
4. **深入分析参考图像** ⚠️：提取具体、具体的元素（参见 reference-images.md）
5. **检测语言**：比较源内容、用户输入、EXTEND.md 偏好设置
6. **确定输出目录**：按文件结构规则

**⚠️ 参考图像中的人物**：

如果参考图像包含**人物**，这些人应该在封面上出现：

- **模型支持 `--ref`**（默认）：将图像复制到 `refs/`，在生成时通过 `--ref` 传递。不需要描述文件 — 模型直接看到人脸。
- **模型不支持 `--ref`**（Jimeng、Seedream 3.0）：创建 `refs/ref-NN-{slug}.md`，包含每个角色的描述（头发、眼镜、肤色、服装）。嵌入为 MUST/REQUIRED 指令到提示文本中。

有关完整决策表，请参见 [reference-images.md](references/workflow/reference-images.md)。

### 步骤 2：确认选项 ⚠️

**硬性门槛**：根据 [确认策略](#confirmation-policy)，此步骤是强制性的 — 步骤 3–4 不能在此处确认用户（或使用 `--quick` / `quick_mode: true` / 当前请求中的等效措辞明确排除）之前开始。

**必须使用 `AskUserQuestion` 工具**来作为交互式选择呈现选项 — **不能**使用纯文本表格。一次最多呈现 4 个问题在单个 `AskUserQuestion` 调用中（类型、调色板、渲染、字体+设置）。每个问题首先显示推荐选项及其原因，然后是替代选项。

完整确认流程和问题格式：[references/workflow/confirm-options.md](references/workflow/confirm-options.md)

| 条件 | 跳过 | 仍然询问 |
|------|------|----------|
| `--quick` 或 `quick_mode: true` | 6 个维度 | 宽高比（除非 `--aspect`） |
| 所有 6 个 + `--aspect` 指定 | 所有 | 无 |

### 步骤 3：创建提示

保存到 `prompts/cover.md`。模板：[references/workflow/prompt-template.md](references/workflow/prompt-template.md)

**关键 - 前置文件中的参考**：
- 保存到 `refs/` 的文件 → 添加到前置文件 `references` 列表
- 口头提取的风格（无文件）→ 忽略 `references`，在正文中描述
- 在写入之前 → 验证：`test -f refs/ref-NN-{slug}.{ext}`

**正文中的参考元素** 必须详细，以 "MUST"/"REQUIRED" 开头，并说明集成方法。

### 步骤 4：生成图像

1. **备份现有的** `cover.png`（如果重新生成）
2. **通过 `## 图像生成工具` 规则选择后端**：使用可用的任何后端；如果有多个，一次询问用户。每次会话在生成之前只做一次。
3. **将完整的最终提示** 写入 `prompts/01-cover-[slug].md`（硬性要求）在调用后端之前。
4. **处理参考** 从提示前置文件：
   - `direct` 使用 → 通过 `--ref` 传递（使用支持 ref 的后端）
   - `style`/`palette` → 提取特征，附加到提示
5. **生成**：调用选定的后端，使用提示文件、输出路径、宽高比。
   - **`codex-imagegen`**：参见 [references/codex-imagegen.md](references/codex-imagegen.md) 的调用契约（首选 `baoyu-image-gen --provider codex-cli` 路径、运行时包装器发现、参数说明、stdout 模式、批量语义）。
   - **Codex `imagegen`（原生）** 或其他运行时原生工具 / `baoyu-image-gen` 技能：按上述 `## 图像生成工具` 中的规则。
6. 失败时：自动重试一次

### 步骤 5：完成报告

```
封面已生成！

主题：[主题]
类型：[类型] | 调色板：[调色板] | 渲染：[渲染]
文本：[文本] | 情绪：[情绪] | 字体：[字体] | 宽高比：[比例]
标题：[标题或 "纯视觉"]
语言：[语言] | 水印：[启用/禁用]
参考：[N 张图像或 "提取风格" 或 "无"]
位置：[目录路径]

文件：
✓ source-{slug}.{ext}
✓ prompts/cover.md
✓ cover.png
```

## 图像修改

| 操作 | 步骤 |
|------|------|
| **重新生成** | 备份 → 首先更新提示文件 → 重新生成 |
| **更改维度** | 备份 → 确认新值 → 更新提示 → 重新生成 |

文本更正策略：

- 如果标题/副标题拼写错误、混乱、难以阅读或视觉上较弱，不要用代码修补光栅图像。
- 对于文本更正重新生成，请编写新的提示文件和新的输出路径，以保留有缺陷的候选者进行比较。
- 后处理仅限于裁剪、调整大小、压缩或格式转换，这些操作不会改变文本或主要构图。

## 构图原则

- **空白**：40-60% 的呼吸空间
- **视觉锚点**：主要元素居中或左偏移
- **人物**：简化轮廓；**不**出现逼真的人类
- **标题**：使用用户/源的确切标题；**永不**凭空创造

- **直接编辑** — 打开 EXTEND.md 并修改字段。完整架构：[references/config/preferences-schema.md](references/config/preferences-schema.md)。
- **交互式重新配置** — 删除 EXTEND.md（或询问“重新配置 baoyu-cover-image 偏好” / “重新配置”）。下次运行将重新触发首次设置。
- **常用单行编辑**：
  - `preferred_image_backend: auto` — 默认；运行时原生工具优先，回退到唯一安装的后端，仅在存在多个非原生工具时询问。
  - `preferred_image_backend: codex-imagegen` — 固定 Codex 的内置功能。
  - `preferred_image_backend: baoyu-image-gen` — 固定 baoyu-image-gen 技能。
  - `preferred_image_backend: ask` — 每次运行都确认后端。
  - `watermark.enabled: true`, `preferred_type`, `preferred_palette`, `preferred_rendering`, `default_aspect`, `quick_mode: true`, `language` — 调整自动选择默认值和确认流程。

## 参考

**尺寸**：[text.md](references/dimensions/text.md) | [mood.md](references/dimensions/mood.md) | [font.md](references/dimensions/font.md)
**调色板**：[references/palettes/](references/palettes/)
**渲染**：[references/renderings/](references/renderings/)
**类型**：[references/types.md](references/types.md)
**自动选择**：[references/auto-selection.md](references/auto-selection.md)
**风格预设**：[references/style-presets.md](references/style-presets.md)
**兼容性**：[references/compatibility.md](references/compatibility.md)
**视觉元素**：[references/visual-elements.md](references/visual-elements.md)
**工作流程**：[confirm-options.md](references/workflow/confirm-options.md) | [prompt-template.md](references/workflow/prompt-template.md) | [reference-images.md](references/workflow/reference-images.md)
**配置**：[preferences-schema.md](references/config/preferences-schema.md) | [first-time-setup.md](references/config/first-time-setup.md) | [watermark-guide.md](references/config/watermark-guide.md)
