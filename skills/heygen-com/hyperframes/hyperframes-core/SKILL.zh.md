---
name: hyperframes-core
description: HyperFrames组合合约——构建一个可渲染的项目。用于组合结构、`data-*`时间属性、`class="clip"`、轨道、子组合、变量、框架拥有的媒体播放、确定性渲染规则和验证。在编写组合HTML之前请阅读。
---

**插件安装：** 在设置或新鲜命令之前，当此技能位于 HyperFrames 插件内时，请遵循 [插件执行规则](../hyperframes/references/plugin-installation.md)。独立安装保留以下更新说明。

# HyperFrames 核心

**代理陷阱（首先阅读）：**

- 使用 flex/`inset` 居中，而不是在节点上使用 CSS `transform: translate(-50%,-50%)` 然后在节点上使用 GSAP `x`/`y`。检查：`gsap_css_transform_conflict`。使用 `fromTo` 或 `xPercent`/`yPercent`。
- 不要添加场景退出的 `tl.set(..., {visibility:"hidden"})`。运行时已经隐藏了定时剪辑。内部节点的透明度渐变（或 `.clip` 上的 `opacity`）就足够了。字幕硬杀是不同的规则。
- `window.__timelines["id"]` 必须与根 `data-composition-id` 匹配。
- 在 `render` 之后，阅读摘要的第二行：`beginframe` 与 `screenshot`，GPU 模式，舞台时间。`screenshot` + `software gpu` 在 Linux 上是慢路径。

HyperFrames 从 HTML 渲染视频。一个合成是一个 HTML 文件，其 DOM 使用 `data-*` 属性声明时间，其动画运行时是可寻址的，其媒体播放由框架拥有。

这项技能是 **技术合同** — 如何构建一个 HyperFrames 项目。下面的正文是构建指南；每个主题的详细信息位于 `references/`（索引下一个），按需阅读。流程文档（简要，故事板，审查，生产，分发，帧工作器）位于 `/hyperframes` → `references/`。其他关注点位于兄弟域技能 — `hyperframes-animation`，`hyperframes-creative`，`media-use`，`hyperframes-cli`，`hyperframes-registry`。`/hyperframes` 中的能力映射说明了每个涵盖的内容。

## 参考

| 文件                                    | 阅读它以…                                                                                                                                                         |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `references/minimal-composition.md`     | 从最小的可渲染合成骨架开始                                                                                                                                       |
| `references/composition-patterns.md`    | 选择整体式与模块式；构建模块化的 `index.html`；选择子合成原型                                                                                                          |
| `references/data-attributes.md`         | 查找任何 `data-*`（根 / 剪辑 / 子合成主机 / 旧别名）；使用 `class="clip"`                                                                                             |
| `references/tracks-and-clips.md`        | 了解 `data-track-index` 控制什么（以及不控制什么），z-index，相对于另一个剪辑的时间；使用 `npx hyperframes timeline` 列出每个轨道和剪辑 |
| `references/creator-editing-recipes.md` | 复制真实的剪切/修剪/重新排序/重新时间/冻结/摄像机/蒙版/交叉渐变/音频编辑配方及其限制                                                                                   |
| `references/sub-compositions.md`        | 连接一个子合成（主机属性，`<template>`，每个实例变量）并在其中动画                                                                                                      |
| `references/variables-and-media.md`     | 声明变量；放置 `<video>`/`<audio>`，设置音量，修剪                                                                                                                    |
| `references/determinism-rules.md`       | 构建一个可寻址的时间线；确定性禁止；布局 / 文本适应                                                                                                                    |
| `references/full-screen-motion.md`      | 使用共享背景编写全帧运动                                                                                                                                          |
| `references/tailwind.md`                | 在 Tailwind v4 项目中工作 (`init --tailwind`；运行时合同与 Studio 的 v3 不同)                                                                                              |

对于动画运行时具体细节（GSAP API，Lottie，Three.js 等）请转到 `hyperframes-animation` → `adapters/<runtime>.md`。

## 构建一个合成

### 两种根形式（不可互换）

- **独立式**（顶层 `index.html`）：根 `<div data-composition-id="…">` 直接位于 `<body>` 中，**没有 `<template>` 包装**。包装一个独立根会隐藏所有内容，并且 `lint` 会拒绝它 (`standalone_composition_wrapped_in_template`，错误)。
- **子合成**（通过 `data-composition-src` 加载）：将根包装在 `<template>` 中。这是要编写的形状：加载器也接受一个纯文本完整文档并回退到其 `<body>`，但模板形式是示例和工具所假设的。

> ⚠ 运输规则：对于**模板化**的子合成，组装器会丢弃文件自己的 `<head>` `<style>`/`<script>` (`packages/core/src/compiler/compositionAssembly.ts`，`hasTemplate` 门），所以请将 `<style>`/`<script>` **放在**模板内。`<link>` 无论哪种方式都会被提升。
> ⚠ 主机-id约定：给主机槽，内部的模板，以及 `window.__timelines["<id>"]` 键相同的 id。支持不同的本地 id（组装器回退到文件中的第一个根），但差异是沉默的，所以除非你有不匹配的理由，否则请匹配它们。

文件形状，主机连接，以及预渲染检查清单 → `references/sub-compositions.md`。

### 根必须定尺寸（沉默的布局错误）

独立根作者 `width`/`height: 100%`。画布大小是 `data-width`/`data-height`。运行时将那些像素戳在合成根上。不要在 `#root` 上硬编码 `1920px`/`1080px`。骨架 → `references/minimal-composition.md`。

### 一个暂停的时间线

每个合成注册 **正好一个** `gsap.timeline({ paused: true })` 在 `window.__timelines["<id>"]`（键 = 根 `data-composition-id`）。在异步回调（`document.fonts.ready`）内构建它是支持的；重要的是，你**只有在构建完成后才注册**。渲染长度是根的 `data-duration`，**不是**时间线的长度：运行时间线超过它的时间线会被截断，而一个结束过早的时间线会保持其最后一帧。省略根 `data-duration`，长度会被推断（时间线，媒体窗口或适配器）。你不需要 `window.__timelines = window.__timelines || {}`：运行时在您的内联脚本运行之前创建该注册表，并且 `lint` 现在不再要求它。不要手动将子时间线嵌套到主机中；运行时会自动嵌套注册的子时间线。完整合同（包括非 GSAP 运行时）→ `references/determinism-rules.md` + `hyperframes-animation/adapters/`。

### 第一次检查的陷阱（保证第一次构建失败）

`lint` 捕获的规则，但事后才捕获。第一次编写它们：

- 永远不要将 CSS 初始 `transform` 与在**同一**属性上的 GSAP 补间配对 — CSS 值和补间的起始值会冲突，并且 `lint` 会用 `gsap_css_transform_conflict` 拒绝它。在补间内设置初始状态，使用 `gsap.fromTo(el, { x: -40 }, { x: 0 })` 而不是 CSS `transform: translateX(-40px)`。
- 永远不要在 `<video>`/`<audio>` 上放置 `crossorigin`。`lint` 会无条件拒绝它 (`media_crossorigin_breaks_preview`，错误)，包括对于 canvas/WebGL/WebAudio 读回。没有抑制。
- 永远不要给 `<video data-start>` 一个也携带 `data-start` 的祖先。`lint` 会用 `video_nested_in_timed_element`（错误）拒绝它。时间包装器**或**视频，而不是两者都时间。
- 每个 `<audio>` 需要一个 `id`。`lint` 会用 `media_missing_id` 拒绝它，并且没有 id 的 `<audio>` 永远不会被混音器拾取，因此渲染是**沉默的**。
- 永远不要用 `.clip` 与 `autoAlpha` 或 `visibility` 补间 — `lint` 会用 `gsap_animates_clip_element` 拒绝它。动画一个子元素。
- 一个命名的 CSS `font-family` 需要一个指向已发布的本地文件的文件内 `@font-face`，否则 `lint` 会触发 `font_family_without_font_face`。
- 子合成 `#root` 使用 `width`/`height: 100%`（或 `inset: 0`），而不是硬编码 `1920px`/`1080px`。画布大小是 `data-width`/`data-height`。

一个 `lint` **错误**也会关闭布局和对比度检查：`check` 然后报告 `0 sample(s)` 和 `0/0 text checks`，这看起来像是一个干净的文件，但实际上什么都没运行。在信任这些数字之前清除 `lint` 错误。

### 不可协商的规则（自动门可能遗漏的沉默错误）

在这里提出；完整理由在链接的参考中。不要违反：

- 没有渲染时时钟 / 未播种的 `Math.random` / 网络 / 输入状态；没有 `repeat: -1`（使用有限计数）。→ `determinism-rules.md`
- 永远不要在 `.clip` 元素上补间 `display`，`visibility` 或 `autoAlpha`。框架拥有剪辑可见性，并且 `lint` 会拒绝它 (`gsap_animates_clip_element`)。动画一个子元素。→ `determinism-rules.md`
- 正文文本中不要有 `<br>`；转换的元素必须是块级 + 尺寸；脉冲的绝对装饰需要峰值清除。→ `determinism-rules.md`
- `<video>`/`<audio>` 是通过扁平文档查询找到的，因此框架在任何嵌套深度（包括在子合成 `<template>` 或包装器内）都会寻址和解码它们。一个硬限制：如果 `<video data-start>` 位于另一个**纯**元素内，该元素也具有 `data-start`，则 `lint` 会报错（错误的源帧，然后剪辑在插槽中消失），所以请将时间放在包装器或视频上，永远不要两者都放。子合成主机是例外：子合成内的媒体渲染正确。另一个注意事项是时间线，而不是位置：子合成时间线不能动画主机根元素。→ `variables-and-media.md`
- 保持每个 `id` 在**组装**的页面上唯一（将子合成 id 前缀为合成 id，`#<id>-hero`），以便您的 `#id` CSS 和 `getElementById` 调用解析。帧注入不再依赖于它：编译器在每个 `video[src]`/`audio[src]`/`img[src]` 上戳上一个文档唯一的 `data-hf-render-id`。使用 `<source>` 子元素的媒体而不是 `src` 属性的媒体**不**会被戳，所以唯一的 id 仍然很重要。→ `composition-patterns.md`
- 合成根上的全屏填充在正常渲染上是好的。只有在分层合成路径（HDR 内容，或使用着色器过渡的合成）上才会被丢弃，此时引擎强制每个合成根透明，以便下面的层显示出来。如果你的合成使用着色器过渡或 HDR 媒体，请将填充放在一个全出血**子元素**上（`position:absolute; inset:0`）。→ `composition-patterns.md`

## 编辑现有合成

- 首先阅读文件。保留无关的时间，轨道，ID，变量，媒体路径。
- 要知道项目时间线上的内容（轨道，剪辑，开始，结束，播放什么），运行 `npx hyperframes timeline [--json]` 而不是阅读 `index.html` 和每个子合成文件。
- 匹配现有合成 ID 和时间线键。
- 添加剪辑：有意设置其 `data-start`/`data-duration` 以相对于周围的剪辑。`data-track-index` 是 Studio 显示轨道，不是时间约束，所以它不需要是空闲的。
- 一个结束在根 `data-duration` 之后的剪辑会被截断：在相同的编辑中扩展根 `data-duration` 到剪辑的结束（`lint` 警告 `clip_ends_past_root_duration`）。
- 任何合成元素的 `data-hidden` 都会在预览和渲染中隐藏它，覆盖其时间窗口；它是非破坏性/可逆的，并由 Studio 的时间线眼睛图标切换。
- 添加子合成：在连接主机之前验证其内部 `data-composition-id`。

## 验证

使用 `hyperframes-cli` 获取命令详细信息

- [ ] `npx hyperframes check` 通过（跨 `lint`，运行时，布局，运动和对比度 0 个发现）
- [ ] 具有子合成的项目：`npx hyperframes snapshot --at <midpoints>` 并目测每个帧
- [ ] `npx hyperframes preview --background` 用于审查（用户可以编辑 Studio 时间线中的任何内容，并且服务器在调用命令后仍然存在）
- [ ] `npx hyperframes render` 仅在用户批准后
