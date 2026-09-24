# HyperFrames 动画

所有动态知识整合为一个技能：**规则**（原子配方）、**蓝图**（多阶段场景模板）、**转场**（场景之间过渡）、**技法**（更广泛的动态设计模式）、**适配器**（按运行时 API）。

组合契约（数据属性、子组合、确定性）见 `hyperframes-core`。

## 默认：组合原子规则

从 `rules-index.md` 中选择 2-4 条规则，用单个暂停的 GSAP 时间线将其组合起来，即可完成。这种方式比从蓝图开始更快，产生的代码也更少。

## 何时加载蓝图

- 场景匹配已有的预设多阶段模板（品牌展示、社会认同证明等），复用其阶段流程可节省实际的创作时间
- 需要为复杂的 4-5 阶段编排提供可运行的基准代码

蓝图位于 `blueprints-index.md`。每条条目指向 `blueprints/<id>.md`（配方）。不要提前阅读；在已决定需要场景级编排后再加载。

## 路由

| 想要…… | 阅读 |
| --- | --- |
| 通过触发器/标签选择原子动态模式 | `rules-index.md` |
| 阅读某条规则的完整 HTML/CSS/GSAP 配方 | `rules/<name>.md` |
| 选择多阶段场景模板 | `blueprints-index.md` |
| 阅读某个蓝图的完整配方 | `blueprints/<id>.md` |
| 创作场景过渡（CSS 驱动，在两个片段之间） | `transitions/overview.md`，`transitions/catalog.md` |
| 查找更广泛的动态设计技法 | `techniques.md` |
| 运动模糊——元素上的快门拖影，以及何时不使用它 | `references/motion-blur.md` |
| 分析现有组合的动画映射 | `scripts/animation-map.mjs` |
| GSAP API——时间线/补间/位置参数 | `adapters/gsap.md` |
| GSAP——即插即用效果配方 | `rules/gsap-effects.md` |
| GSAP——变换/性能 | `adapters/gsap-transforms-and-perf.md` |
| GSAP——缓动/交错 | `adapters/gsap-easing-and-stagger.md` |
| GSAP——时间线/标签 | `adapters/gsap-timeline-and-labels.md` |
| Lottie / dotLottie（After Effects 导出，`window.__hfLottie`） | `adapters/lottie.md` |
| Three.js / WebGL（3D 场景，`AnimationMixer`，`hf-seek`） | `adapters/three.md` |
| Anime.js（`window.__hfAnime`） | `adapters/animejs.md` |
| CSS 关键帧（`animation-delay` / `play-state` / `fill-mode`） | `adapters/css-animations.md` |
| Web Animations API（`element.animate()`，`currentTime` 检索） | `adapters/waapi.md` |
| TypeGPU / WebGPU（`navigator.gpu`，WGSL，计算管线） | `adapters/typegpu.md` |
| HTML 作为纹理 + WebGL/GLSL 后处理（通过 `drawElementImage` 捕获实时 DOM） | `adapters/html-in-canvas-patterns.md` |
| 命名文本动画效果（通过外部 `animate-text` 技能通过 24 个 ID） | `adapters/animate-text.md` |

## 选择运行时

- **GSAP** 是 95% 运动工作的默认选择——覆盖时间线编排、变换、缓动、交错。本技能中的所有原子规则均基于 GSAP。
- **Lottie** 用于资产自身已预烘焙时间线（通常是 After Effects 导出的）。
- **Three.js** 用于 3D 场景、摄像机运动、着色器驱动的视觉效果。
- **Anime.js** 用于在 GSAP 过度时轻量级的补间动画。
- **CSS** 用于简单的重复图案、装饰、闪烁——无需 JavaScript 动画开销。
- **WAAPI** 用于无需 GSAP 依赖的原生浏览器关键帧。
- **TypeGPU / WebGPU** 用于 GPU 渲染的画布（粒子、液态玻璃、自定义着色器）。

多个运行时可以在同一组合中共存。每个运行时在其对应的特定全局变量上注册其实例，以便 HyperFrames 在一次遍历中检索所有内容。

## 关键约束

**前提：`hyperframes-core` → 不可协商规则**（单个暂停时间线，`data-duration` 决定长度，不使用 `Math.random` / `Date.now` / `performance.now`，不使用 `repeat: -1`，不在后场景片段上进行页面加载时的 `gsap.set`，不使用 `display` 或原始 `visibility` 补间，不在 `async` / `setTimeout` / `Promise` 中构建时间线）。核心允许 `autoAlpha` 和显式时间线边界处的零时长可见性设置。仅在使用这些例外于片段内或非片段元素/片段内包装器时有效；框架负责 `.clip` 生命周期。此处不重复完整契约。

在核心契约之上添加的动画创作补充：

- **预计算的布局常量**——切勿在时间补间时从 `getBoundingClientRect()` 推导位置。渲染器并行采样导致的时间补间时 DOM 测量不同步；在组合设置时一次性计算坐标并复用。
- **空间运动仅使用 GSAP 变换别名**（`x`、`y`、`scale`、`rotation`）。核心的允许列表还允许非空间属性补间使用 `opacity` / `color` / `backgroundColor` / `borderRadius`——但永不使用 `width` / `height` / `top` / `left` 进行布局变化。

## 脚本

```bash
node skills/hyperframes-animation/scripts/animation-map.mjs <composition-dir> \
  --out <composition-dir>/.hyperframes/anim-map
```

读取 `window.__timelines` 上注册的所有 GSAP 时间线，枚举补间，采样边界框，计算标志，输出 `animation-map.json`。在作者化后用于审计编排（死区、交错一致性、生命周期警告）。

`animation-map.mjs` 首先从当前项目解析辅助包，然后可以引导打包的 HyperFrames 包版本。仅在技能在打包的 CLI/技能安装之外运行时，且需要显式固定该引导版本时，才设置 `HYPERFRAMES_SKILL_PKG_VERSION=<版本>`。

## 参见

- `hyperframes-core` — 组合结构、数据属性、子组合、确定性渲染契约
- `hyperframes-creative` — 调色板、字体排印、旁白、节拍规划（非动画创意方向）
- `hyperframes-cli` — `npx hyperframes lint / check / snapshot / preview / render`
