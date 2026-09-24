# HyperFrames Creative

品牌、节奏、风格、旁白与构图方向。需在 `hyperframes-core` 的技术协议就绪后方可使用。

对于动态模式、场景蓝图、转场以及 CSS 标记效果，使用 `hyperframes-animation` —— 本技能刻意不含动画相关功能。

> **在处理任何非简单构图时，请首先阅读以下两份文档 —— 它们会覆盖网络相关直觉：**
>
> - `references/house-style.md` — "interpret the prompt, generate real content," the lazy-default list, and the background/foreground layer recipe. This is what turns a literal restyle into a _concept_.
> - `references/video-composition.md` — video-medium scale, depth, and foreground detail. It explains how to avoid empty web-page layouts without imposing a universal element count.

**跳过这两份文档是导致输出过于通用、呈现网页风格的头号原因。它们不是下方路由表中的可选行项——对于任何超出单行编辑的工作，在选择颜色或编写 HTML 之前，请先打开这两份文档。**

## Workflow

1. 如果项目已有设计规范，**请先阅读**，并将其 frontmatter tokens 视为品牌事实（颜色、字体、间距、语气、约束条件）。应读取哪个文件（优先级为 `frame.md` → `design.md` → `DESIGN.md`）以及如何解析（frontmatter = 规范性，正文 = 上下文）已在 [`references/design-spec.md`](references/design-spec.md) 中定义一次——请根据该文档进行解析并加载。
2. 如果不存在设计规范，且用户要求视觉方向，请选择路线：
   - 现成帧预设（可选）→ `frame-presets/`（将 `FRAME.md` 作为 `frame.md` 采用；详见 `references/design-spec.md`）
   - 命名风格或情绪 → `references/visual-styles.md`
   - 快速默认值 → `references/house-style.md`
   - 交互式选择 → `references/design-picker.md`
3. 对于多场景工作，在编写 HTML 之前规划节拍和节奏 → `references/beat-direction.md`。对于场景转场，请跳转至 `hyperframes-animation/transitions/`。
4. 对于动作量大的工作，阅读 `references/motion-principles.md`（高层级护栏），然后到 `hyperframes-animation` 查阅原子规则。

## Routing

| 主题                                                                                                   | 阅读                                           |
| ------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| 将现成帧预设作为 `frame.md` 采用（可选）                                                | `frame-presets/` · `references/design-spec.md` |
| 默认调色板、动作、字体、待质疑的懒默认设置                                                       | `references/house-style.md`                    |
| 命名风格预设、情绪到风格的路由                                                              | `references/visual-styles.md`                  |
| 特定调色板的颜色令牌                                                                           | `palettes/*.md`                                |
| 构图模式 — PiP、文本在主体后方、标题卡、幻灯片展示                                                   | `references/composition-patterns.md`           |
| 数据 / 信息图展示                                                                                | `references/data-in-motion.md`                 |
| 开放式提示的结构化扩展                                                                            | `references/prompt-expansion.md`               |
| 视频媒介的密度、规模、颜色、帧构图                                                               | `references/video-composition.md`              |
| 每个节拍的方向、节奏规划、转场时间                                                               | `references/beat-direction.md`                 |
| 后编写规范校验（颜色、字体、边角、间距、深度）                                                     | `references/design-adherence.md`               |
| 高层级动作护栏及 GSAP 质量规则                                                                        | `references/motion-principles.md`              |
| 字体选择、搭配、渲染视频字体护栏                                                                    | `references/typography.md`                     |
| 故事原则——钩子语言、价值先于证据、剧本即提案、可溯源视觉                                           | `references/story-spine.md`                    |
| 脚本节奏、语气、开场、数字发音                                                                    | `references/narration.md`                      |
| 映射到动作的预计算音频频段                                                                            | `references/audio-reactive.md`                 |

## Scripts

- `scripts/contrast-report.mjs` — 检查渲染帧的对比警告。
- `scripts/extract-audio-data.py` — 为音频响应式构图预先提取音频频段。
- `scripts/package-loader.mjs` — 支持打包创意工具脚本。

`contrast-report.mjs` 首先从当前项目解析辅助包，然后可以引导打包的 HyperFrames 包版本。仅在技能在打包的 CLI/技能安装外部运行且需要明确固定该引导版本时，设置 `HYPERFRAMES_SKILL_PKG_VERSION=<version>`。

从仓库根目录运行，并使用显式路径，例如：

```bash
python skills/hyperframes-creative/scripts/extract-audio-data.py <audio-file>
```

动画分析（`animation-map.mjs`）位于 `hyperframes-animation/scripts/` 中。

## Boundaries

- 不覆盖 `hyperframes-core` 技术规则。
- 对于极简技术构图，不要求设计系统。
- 除非请求要求，或你首先提出扩展，否则不额外添加场景、旁白、音乐、字幕或转场。
- 保持配方引用任务特定；对于简单编辑，不要阅读每一个参考文档。
