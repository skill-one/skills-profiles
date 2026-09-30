---
name: hyperframes-animation
description: HyperFrames的所有动画知识——包括原子运动规则、多阶段场景蓝图、场景过渡、更广泛的运动设计技巧，以及七种运行时适配器（GSAP默认适配器，以及Lottie、Three.js、Anime.js、CSS关键帧、Web动画API、TypeGPU）。适用于任何运动或动画任务：选择2-4条规则进行组合，或加载一个蓝图，或查找特定运行时的API（例如GSAP缓动函数/Lottie播放器/Three.js混合器）。还涵盖了审核现有组合的编排（动画映射）和24种命名文本动画效果。HyperFrames原生特性：单个暂停时间轴、安全搜索、确定性。
---

**插件安装：** 在设置或新鲜命令之前，当此技能位于 HyperFrames 插件内时，请遵循 [插件执行规则](../hyperframes/references/plugin-installation.md)。独立安装则保留下方的更新说明。

# HyperFrames 动画

一个技能中的所有运动知识：**规则**（原子配方）、**蓝图**（多阶段场景模板）、**过渡**（场景间）、**技术**（更广泛的运动设计模式）和**适配器**（每运行时 API）。

关于组合契约（数据属性、子组合、确定性）请参阅 `hyperframes-core`。

## 默认：组合原子规则

从 `rules-index.md` 中选择 2-4 条规则，用单个暂停的 GSAP 时间轴将它们粘合在一起，搞定。这比从蓝图开始更快，产生的代码也更少。

## 当需要加载蓝图时

- 场景匹配现有的预设计多阶段模板（品牌展示、社会证明等），并且重用其阶段管道可以节省真实的编写时间
- 你需要一个可运行的基准代码用于复杂的 4-5 阶段编排

蓝图位于 `blueprints-index.md` 中。每个条目指向 `blueprints/<id>.md`（配方）。不要推测性地读取它；在你已经决定需要场景级编排时再加载它。

## 路由

| 想要…                                                                                                  | 阅读                                     |
| -------------------------------------------------------------------- | -------------------------------------- |
| 通过触发器 / 标签选择一个原子运动模式                                                              | `rules-index.md`                         |
| 读取一条规则的完整 HTML / CSS / GSAP 配方                                                          | `rules/<name>.md`                        |
| 选择一个多阶段场景模板                                                                                | `blueprints-index.md`                    |
| 读取一个蓝图的完整配方                                                                                | `blueprints/<id>.md`                     |
| 编写场景过渡（CSS 驱动，在两个片段之间）                                                              | `transitions/overview.md`, `transitions/catalog.md` |
| 查找一个更广泛的运动设计技术                                                                          | `techniques.md`                          |
| 运动模糊 —— 元素的快门拖曳，以及何时不使用它                                                          | `references/motion-blur.md`              |
| 分析现有组合的动画地图                                                                                | `scripts/animation-map.mjs`              |
| GSAP API —— 时间轴 / 补间 / 位置参数                                                                | `adapters/gsap.md`                       |
| GSAP —— 即插即用效果配方                                                                              | `rules/gsap-effects.md`                  |
| GSAP —— 变换 / 性能                                                                                   | `adapters/gsap-transforms-and-perf.md`   |
| GSAP —— 缓动 / 错开                                                                                   | `adapters/gsap-easing-and-stagger.md`    |
| GSAP —— 时间轴 / 标签                                                                                 | `adapters/gsap-timeline-and-labels.md`   |
| Lottie / dotLottie（After Effects 导出，`window.__hfLottie`）                                           | `adapters/lottie.md`                     |
| 角色动画（行走循环、吉祥物、关节式木偶、手势）                                                          | `adapters/lottie.md` → Characters        |
| Three.js / WebGL（3D 场景，`AnimationMixer`，`hf-seek`）                                                | `adapters/three.md`                      |
| Anime.js（`window.__hfAnime`）                                                                        | `adapters/animejs.md`                    |
| CSS 关键帧（`animation-delay` / `play-state` / `fill-mode`）                                           | `adapters/css-animations.md`             |
| Web Animations API（`element.animate()`，`currentTime` 搜索）                                           | `adapters/waapi.md`                      |
| TypeGPU / WebGPU（`navigator.gpu`，WGSL，计算管道）                                                      | `adapters/typegpu.md`                    |
| HTML-as-texture + WebGL/GLSL 后处理特效（通过 `drawElementImage` 捕获实时 DOM）                          | `adapters/html-in-canvas-patterns.md`     |
| 命名文本动画效果（通过外部 `animate-text` 技能的 24 个 ID）                                             | `adapters/animate-text.md`               |

## 选择运行时

- **GSAP** 是 95% 运动工作的默认选择——涵盖时间轴编排、变换、缓动、错开。此技能中的所有原子规则都是基于 GSAP 的。
- **Lottie** 当一个资源有自己的预烘焙时间轴时（通常是 After Effects 导出），包括行走、手势或反应的角色。
- **Three.js** 用于 3D 场景、相机运动、着色器驱动视觉效果。
- **Anime.js** 当 GSAP 过于庞大时，用于轻量级补间。
- **CSS** 用于简单的重复主题、装饰、闪烁——没有 JavaScript 动画成本。
- **WAAPI** 用于没有 GSAP 依赖的本地浏览器关键帧。
- **TypeGPU / WebGPU** 用于 GPU 渲染画布（粒子、液体玻璃、自定义着色器）。

多个运行时可以共存于一个组合中。每个都会在其特定的全局上注册实例，以便 HyperFrames 可以一次性搜索所有实例。

## 关键约束

**前提条件：`hyperframes-core` → 不可协商规则**（单个暂停时间轴，`data-duration` 控制长度，没有 `Math.random` / `Date.now` / `performance.now`，没有 `repeat: -1`，没有页面加载 `gsap.set` 在后续场景片段上，没有 `display` 或原始 `visibility` 补间，以及在 `async` / `setTimeout` / `Promise` 内部不构建时间轴）。核心允许 GSAP `autoAlpha` 和在显式时间轴边界处的零持续时间可见性设置。仅在这些例外情况下使用它们，非片段元素或片段内的包装器；框架拥有 `.clip` 生命周期。不要在此处重述完整契约。

在核心契约之上的动画制作补充：

- **预计算布局常量**——在补间时间不要从 `getBoundingClientRect()` 推导位置。补间时间的 DOM 测量会脱同步，因为渲染器并行采样；在组合设置时计算坐标一次，并重复使用。
- **空间运动仅使用 GSAP 变换别名**（`x`，`y`，`scale`，`rotation`）。核心的允许列表还允许 `opacity` / `color` / `backgroundColor` / `borderRadius` 用于非空间属性补间——但永远不要用于布局更改的 `width` / `height` / `top` / `left`。

## 脚本

```bash
node skills/hyperframes-animation/scripts/animation-map.mjs <composition-dir> \
  --out <composition-dir>/.hyperframes/anim-map
```

读取 `window.__timelines` 上注册的每个 GSAP 时间轴，枚举补间，采样边界框，计算标志，输出 `animation-map.json`。在编写后使用它来审计编排（死区、错开一致性、生命周期警告）。

`animation-map.mjs` 首先从当前项目解析辅助包，然后可以引导捆绑的 HyperFrames 包版本。仅在运行技能时需要明确固定引导版本，并且不在捆绑的 CLI/技能安装外运行时设置 `HYPERFRAMES_SKILL_PKG_VERSION=<version>`。

## 参见

- `hyperframes-core` — 组合结构、数据属性、子组合、确定性渲染契约
- `hyperframes-creative` — 调色板、排版、叙述、节拍规划（非动画创意方向）
- `hyperframes-cli` — `npx hyperframes lint / check / snapshot / preview / render`
