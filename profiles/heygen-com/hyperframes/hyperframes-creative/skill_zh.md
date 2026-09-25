# HyperFrames 创意

品牌、节奏、风格、叙述和构图方向。在 `hyperframes-core` 的技术合同完成后使用。

对于运动模式、场景蓝图、过渡和 CSS 标记效果，使用 `hyperframes-animation` — 这项技能有意不涉及动画。

> **对于任何非平凡的构图，首先阅读以下两项 — 它们会覆盖网页本能：**
>
> - `references/house-style.md` — "解释提示，生成真实内容"，懒人默认列表，以及背景/前景层配方。这是将字面重制转化为 _概念_ 的关键。
> - `references/video-composition.md` — 视频媒介的尺度、深度和前景细节。它解释了如何避免空白的网页布局，而无需强加通用的元素数量。
>
> 跳过这两项是导致通用、网页样式输出的最大原因。它们不是路由表中的可选行 — 对于任何超出单行编辑的内容，在选择颜色或编写 HTML 之前，请同时打开两者。

## 工作流程

1. 如果项目有设计规范，**首先阅读它**，并将其 frontmatter 令牌视为品牌真理（颜色、字体、间距、语气、限制）。要读取哪个文件（优先级 `frame.md` → `design.md` → `DESIGN.md`）以及如何解析它（frontmatter = 规范，散文 = 上下文）在 [`references/design-spec.md`](references/design-spec.md) 中定义一次 — 根据该文档解析并加载。
2. 如果不存在设计规范，并且用户要求视觉方向，选择一条路线：
   - 即用型框架预设（可选）→ `frame-presets/`（采用一个 `FRAME.md` 作为 `frame.md`；参见 `references/design-spec.md`）
   - 命名风格或情绪 → `references/visual-styles.md`
   - 快速默认值 → `references/house-style.md`
   - 交互式选择 → `references/design-picker.md`
3. 对于多场景工作，在编写 HTML 之前规划节拍和节奏 → `references/beat-direction.md`。对于场景过渡，跳转到 `hyperframes-animation/transitions/`。
4. 对于运动密集型工作，阅读 `references/motion-principles.md`（高级指导方针），然后转到 `hyperframes-animation` 获取原子规则。

## 路由

| 主题                                                                                                   | 阅读                                           |
| ------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| 采用即用型框架预设作为 `frame.md`（可选）                                                | `frame-presets/` · `references/design-spec.md` |
| 默认调色板、运动、排版、懒人默认值到问题                                         | `references/house-style.md`                    |
| 命名风格预设、情绪到风格路由                                                              | `references/visual-styles.md`                  |
| 调色板特定的颜色令牌                                                                           | `palettes/*.md`                                |
| 构图模式 — PiP、主体后文本、标题卡、幻灯片展示                                 | `references/composition-patterns.md`           |
| 统计 / 信息图表展示                                                                        | `references/data-in-motion.md`                 |
| 开放式提示的结构化扩展                                                                     | `references/prompt-expansion.md`               |
| 视频媒介密度、尺度、颜色、框架构图                                                   | `references/video-composition.md`              |
| 每个节拍的方向、节奏规划、过渡时间                                                          | `references/beat-direction.md`                 |
| 发表后规范验证（颜色、类型、角落、间距、深度）                                | `references/design-adherence.md`               |
| 高级运动指导方针和 GSAP 质量规则                                                     | `references/motion-principles.md`              |
| 字体选择、搭配、渲染视频类型指导方针                                                | `references/typography.md`                     |
| 故事准则 — 钩子语言、价值先于证据、故事板作为提案、来源可追溯的视觉效果                    | `references/story-spine.md`                    |
| 脚本节奏、语气、开场、数字发音                                                     | `references/narration.md`                      |
| 预计算音频频段映射到运动                                                                | `references/audio-reactive.md`                 |

## 脚本

- `scripts/contrast-report.mjs` — 检查渲染框架的对比度警告。
- `scripts/extract-audio-data.py` — 预提取音频频段用于音频反应式构图。
- `scripts/package-loader.mjs` — 支持捆绑创意工具的脚本。

`contrast-report.mjs` 首先从当前项目解析辅助包，然后可以引导捆绑的 HyperFrames 包版本。仅在运行技能时需要明确固定引导版本，并且不在捆绑的 CLI/技能安装外运行时设置 `HYPERFRAMES_SKILL_PKG_VERSION=<version>`。

从仓库根目录运行，使用显式路径，例如：

```bash
python skills/hyperframes-creative/scripts/extract-audio-data.py <audio-file>
```

动画分析 (`animation-map.mjs`) 位于 `hyperframes-animation/scripts/`。

## 边界

- 不要覆盖 `hyperframes-core` 的技术规则。
- 不要为最小技术构图要求设计系统。
- 除非请求要求或您首先提出扩展，否则不要添加额外的场景、叙述、音乐、字幕或过渡。
- 保持配方参考任务特定；不要为简单编辑读取每个参考。
