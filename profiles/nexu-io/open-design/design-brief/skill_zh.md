# 设计简报技能

将结构化的设计简报解析为具体的 DESIGN.md 文件，并可选生成视觉预览。代理，请严格按照以下工作流程执行。

## 背景

本技能中的 8 个维度源自 OpenDesign 的原始 71 系统目录；71 是研究样本，并非当前捆绑系统数量。`design-systems/` 中的每个 `DESIGN.md` 至少解析为：调色板、强调色、排版、展示字体、布局模型和组件样式。我们将这些提炼为 8 个正交维度，涵盖设计师在放置任何像素之前做出的决策。添加了氛围和密度，因为它们是自然语言简报中最常见的模糊来源（“使其简洁”对不同的人意味着不同的事情）。

有意排除的简报级别维度：动画时间、响应式策略和可访问性对比度。这些由各个技能在模板级别强制执行（例如，`saas-landing` 处理自己的响应式逻辑），但生成的 DESIGN.md 包含下游消费的合理断点默认值。

## 1. 接收输入

用户以以下两种格式之一提供设计简报：

### 选项 A：I-Lang 结构化简报

```
[PLAN:@DESIGN|type=saas_landing]
  |palette=navy_and_white|accent=coral
  |typography=inter|display=space_grotesk
  |layout=single_column|max_width=1200px
  |mood=professional_minimal
  |density=spacious|section_gap=96px
  |hero=headline+subhead+cta
  |sections=features,pricing,testimonials,footer
  |exclude=animations,parallax,gradients
  |responsive=mobile_first
```

### 选项 B：自然语言

> "我需要一个开发者工具的着陆页。简洁、极简、暗黑模式。Inter 字体。没有花哨的动画。"

如果用户提供选项 B，则使用下表中的映射表将其转换为结构化格式，然后继续。明确标识每个维度中明确声明的维度，并标记未指定的维度。

### 自然语言 → I-Lang 映射

对于自然语言输入中的每个句子，识别维度关键词并映射到最接近的结构化值：

| 自然语言短语 | 维度 | I-Lang 值 |
|------------------------|-----------|-------------|
| "暗黑模式", "暗黑主题" | 调色板 | `monochrome_dark` |
| "亮色", "白色背景" | 调色板 | `light_clean` |
| "大地色", "暖色调" | 调色板 | `earth_tones` |
| "色彩点缀", "鲜艳" | 强调色 | `electric_blue` (默认) 或 `coral` |
| "微妙强调" | 强调色 | `muted_sage` (默认) 或 `slate` |
| "简洁", "极简", "简单" | 氛围 | `professional_minimal` |
| "俏皮", "有趣", "友好" | 氛围 | `playful` |
| "大胆", " brutalist", "原始" | 氛围 | `brutalist` |
| "编辑", "杂志式" | 氛围 | `editorial` |
| "宽敞", "大量空白" | 密度 | `spacious` |
| "紧凑", "密集", "信息丰富" | 密度 | `compact` |
| "Inter", "系统字体" | 排版 | `inter` (默认) 或 `system_ui` |
| "衬线", "传统" | 排版 | `georgia` (默认) 或 `playfair` |
| "等宽", "代码样式" | 排版 | `jetbrains_mono` |
| "无动画", "静态" | 排除 | `animations` |
| "无渐变" | 排除 | `gradients` |
| "无库存照片" | 排除 | `stock_photos` |
| "单页" | 布局 | `single_column` |
| "两列", "侧边栏" | 布局 | `two_column` |
| "移动优先" | 响应式 | `mobile_first` |

当一个短语映射到多个维度（例如，“简洁暗黑着陆页”→ 氛围=professional_minimal + 调色板=monochrome_dark + 布局=single_column）时，独立解析每个维度。当为单个映射列出多个值时，第一个是默认值；代理只有在周围上下文强烈支持时才可以选择替代值。

## 2. 验证维度

每个设计简报必须解析这 8 个维度。如果输入中缺少任何维度，则使用第 2.2 节中的规则选择合理的默认值。

下面列出的值形成一个封闭词汇。只有此表中列出的值在 2.1 节中有具体的标记映射。如果用户提供了一个表中未列出的值，代理必须要求澄清，而不是猜测。

| # | 维度 | 键 | 示例值 |
|---|-----------|-----|---------------|
| 1 | 调色板 | `palette` | navy_and_white, earth_tones, monochrome_dark, light_clean |
| 2 | 强调色 | `accent` | coral, electric_blue, emerald, muted_sage |
| 3 | 正文排版 | `typography` | inter, system_ui, dm_sans, georgia |
| 4 | 展示排版 | `display` | space_grotesk, clash_display, same_as_body, playfair |
| 5 | 布局模型 | `layout` | single_column, two_column, asymmetric |
| 6 | 氛围 | `mood` | professional_minimal, playful, brutalist, editorial |
| 7 | 密度 | `density` | compact, balanced, spacious |
| 8 | 限制 | `exclude` | animations, gradients, stock_photos, carousel |

### 2.1 符号 → 具体标记解析

每个符号值映射到具体的 设计标记。代理在编写 DESIGN.md 之前必须解析这些：

| 符号值 | 具体标记 |
|---------------|----------------|
| `palette=navy_and_white` | 背景: #0F172A, 表面: #1E293B, 文本: #F8FAFC, 次要: #94A3B8 |
| `palette=monochrome_dark` | 背景: #09090B, 表面: #18181B, 文本: #FAFAFA, 次要: #A1A1AA |
| `palette=light_clean` | 背景: #FFFFFF, 表面: #F8FAFC, 文本: #0F172A, 次要: #64748B |
| `palette=earth_tones` | 背景: #FFFBEB, 表面: #FEF3C7, 文本: #451A03, 次要: #92400E |
| `accent=coral` | 强调: #F97316, 悬停: #EA580C |
| `accent=electric_blue` | 强调: #3B82F6, 悬停: #2563EB |
| `accent=emerald` | 强调: #10B981, 悬停: #059669 |
| `accent=muted_sage` | 强调: #84A98C, 悬停: #6B8F73 |
| `accent=slate` | 强调: #64748B, 悬停: #475569 |
| `typography=inter` | 正文: Inter, 400, 1rem/1.6 |
| `typography=system_ui` | 正文: system-ui, 400, 1rem/1.6 |
| `typography=dm_sans` | 正文: DM Sans, 400, 1rem/1.6 |
| `typography=georgia` | 正文: Georgia, 400, 1.125rem/1.7 |
| `display=space_grotesk` | 展示: Space Grotesk, 700, clamp(2rem, 5vw, 3.5rem) |
| `display=clash_display` | 展示: Clash Display, 700, clamp(2rem, 5vw, 3.5rem) |
| `display=playfair` | 展示: Playfair Display, 700, clamp(2rem, 5vw, 3.5rem) |
| `display=same_as_body` | 展示继承正文字体族，权重 600 |
| `density=compact` | 区块间距: 48px，内容填充: 16px/24px |
| `density=balanced` | 区块间距: 72px，内容填充: 24px/40px |
| `density=spacious` | 区块间距: 96px，内容填充: 24px/48px |

符号值不在本表中有效。如果用户提供了一个未识别的值（例如，`palette=ocean_blue`），代理必须要求澄清：“我不认识 `palette=ocean_blue`。您是指 `navy_and_white`、`monochrome_dark`、`light_clean` 还是 `earth_tones`？”

### 2.2 默认解析规则

当维度未指定时，根据氛围兼容性选择默认值：

| 未指定的维度 | 默认规则 |
|----------------------|-------------|
| `palette` | 如果氛围=editorial → `light_clean`。如果氛围=brutalist → `monochrome_dark`。否则 → `light_clean`。 |
| `accent` | 如果调色板是暗色 → `coral`。如果调色板是亮色 → `electric_blue`。 |
| `typography` | 始终 → `inter`（跨平台最高可读性）。 |
| `display` | 如果氛围=editorial → `playfair`。如果氛围=brutalist → `space_grotesk`。否则 → `same_as_body`。 |
| `layout` | 始终 → `single_column`（最安全的响应式默认值）。 |
| `mood` | 始终 → `professional_minimal`（最不具意见的）。 |
| `density` | 始终 → `balanced`。 |
| `exclude` | 始终 → 无（除非指定，否则无限制）。 |

如果氛围也未指定，所有默认值将回退到安全的默认集：`palette=light_clean`、`accent=electric_blue`、`typography=inter`、`display=same_as_body`、`layout=single_column`、`mood=professional_minimal`、`density=balanced`、`exclude=none`。

## 3. 生成 DESIGN.md

本技能从头开始根据解析的简报维度生成新的 DESIGN.md。如果工作目录中已存在 DESIGN.md，代理应询问用户是否要覆盖或跳过。

使用以下九部分大纲生成 DESIGN.md。此大纲是技能的可移植独立输出，继承自 OpenDesign 的原始上游基线；它不是当前仓库包架构。当前的捆绑包还包含 `manifest.json`、`tokens.css` 和可选的丰富资源，而遗留和用户安装的仅 `DESIGN.md` 内容保持可读。所有颜色十六进制值、字体堆栈和间距值必须来自 2.1 节中解析的标记——不要在解析表中之外发明值。

```markdown
# [项目名称] 设计系统

## 视觉主题与氛围
- 氛围: [从氛围解析]
- 感觉: [从氛围派生 — 例如，professional_minimal → "简洁、自信、克制"]
- 参考: [如果氛围=editorial → "杂志布局、Monocle、Cereal"；如果氛围=brutalist → "暴露结构、原始排版"]

## 调色板与角色
- 背景: [从调色板解析]
- 表面: [从调色板解析]
- 文本主要: [从调色板解析]
- 文本次要: [从调色板解析]
- 强调: [从强调解析]
- 强调悬停: [从强调解析]

## 排版规则
- 展示: [从展示解析], 700, clamp(2rem, 5vw, 3.5rem)
- 正文: [从排版解析], 400, 1rem/1.6
- 等宽: JetBrains Mono, 400, 0.875rem

## 组件样式
- 按钮: [如果氛围=playful → "圆角全", 否则 → "圆角中"], 强调背景, 对比文本
- 卡片: 表面背景, 微妙边框, 12px 半径
- 输入: [如果氛围=brutalist → "粗边框", 否则 → "透明背景, 底部边框"]

## 布局原则
- 最大宽度: 1200px
- 网格: [从布局解析]
- 区块间距: [从密度解析]
- 内容填充: [从密度解析]

## 深度与提升
- 阴影: [如果氛围=brutalist → "硬 4px 偏移", 如果氛围=professional_minimal → "无", 否则 → "微妙 sm"]
- 边框: 1px 实线 [从调色板派生, 文本颜色 8% 不透明度]

## 该做与不该做
- 该使用声明的颜色标记。
- 该保持一致区块间距。
- 该确保所有文本符合 WCAG AA 对比度。
- 不该在调色板之外发明颜色。
- 不该添加装饰性阴影，除非深度与提升允许。
- 不该使用超过 2 种展示/正文字体（等宽是代码和数据的实用字体 — 它不计入此限制）。

## 响应式行为
- 断点: 640px (sm), 768px (md), 1024px (lg), 1280px (xl)
- 移动端: 单列，垂直堆叠所有区块
- 平板: 允许 2 列功能网格
- 桌面端: 带最大宽度约束的全布局
- 图片: 流体，最大宽度 100%，保持宽高比

## 代理提示指南
- 不要在调色板之外发明颜色。
- 不要添加 box-shadows，除非上述规定。
- 强调色在每个视口最多出现 3 次。
- 所有交互元素需要 :focus-visible 边框。
- [如果 exclude 包含项 → 列出每个项作为 "不要使用 {项}。"。]

```

## 4. 生成 brief-preview.html

创建一个 HTML 文件，以视觉方式渲染解析的设计标记。预览必须按顺序包含以下 4 个部分：

1. **调色板色块** — 水平排列的矩形，每个显示颜色部分的一个颜色。标记每个颜色角色（背景、表面、文本、强调）和十六进制代码。
2. **排版样本** — 三个文本块显示展示、正文和等宽字体在其声明的尺寸。使用样本句子（"The quick brown fox..."）填充每个。
3. **间距尺** — 视觉尺或堆叠条，显示区块间距和内容填充值，标记其 px 值。
4. **组件预览** — 使用解析的标记渲染 2–3 个实时组件（主要按钮、带标题/正文的卡片、文本输入）。这些应该是功能性的 HTML/CSS，而不是截图。

使用解析的设计系统标记（背景颜色、字体、间距）样式化预览本身。预览应像设计系统文档页面。

## 5. 报告未指定的维度

在输出末尾，列出用户未指定的维度以及应用的默认值，包括选择每个默认值的规则：

```
从默认值解析的维度：
- display: 设置为 "same_as_body" (规则: 氛围=professional_minimal → same_as_body)
- density: 设置为 "balanced" (规则: 静态回退，未给出间距偏好)
- exclude: 设置为 "none" (规则: 除非指定，否则无限制)
```

这种透明度可防止无声假设传播到最终设计。
