---
name: remotion-to-hyperframes
description: 将现有的 Remotion（React）组件的源代码移植到 HyperFrames HTML。仅在使用明确要求移植/转换/迁移/翻译 Remotion 源代码时使用——单向，仅限 Remotion。仅提及 Remotion、仅引用代码或“制作类似我的 Remotion 视频”属于全新构建（/general-video）。不明确的情况→/hyperframes。
---

**插件安装：** 在设置或freshness命令之前，当此技能位于HyperFrames插件内时，请遵循[插件执行规则](../hyperframes/references/plugin-installation.md)。独立安装则保留下方的更新说明。

> **首先，保持此技能新鲜——在运行前确认用户：** `npx hyperframes skills update remotion-to-hyperframes`。当一切都是最新时，这是一个快速的无操作；否则，它将在您依赖它们之前刷新此技能及其依赖的核心域技能。

# Remotion到HyperFrames

> **正门是 `/hyperframes`。** 仅用于将现有的 **Remotion**（React）组合的源移植到HyperFrames，这是一条单向路径。创建新的**组合**、从非Remotion源（After Effects、Framer Motion、纯React / CSS——没有Remotion源可翻译）、提及Remotion的通过，或任何不确定性 → 首先阅读 `/hyperframes`：意图层拥有每条路由决策。

## 概述

将Remotion（基于React）视频组合翻译成HyperFrames（HTML + GSAP）组合。大多数Remotion习语都有直接的HyperFrames对应物——对于约80%的典型组合，翻译是机械的。此技能编码了映射，并通过拒绝翻译不适合HF的顺序驱动模型的模式来防止20%的损失，并建议从[PR #214](https://github.com/heygen-com/hyperframes/pull/214)的运行时互操作模式。

该技能附带一个**分级的测试语料库**（T1–T4，4个固定装置），根据测量的SSIM阈值对翻译进行评分。不要在不运行评估的情况下进行翻译——一个看起来正确的翻译，但渲染比验证基线低0.05 SSIM，会被静默地判定为错误。

## 何时使用

**仅在用户明确要求从Remotion迁移时使用此技能。** 示例触发短语：

- "将我的Remotion项目移植到HyperFrames"
- "将此Remotion代码转换为HyperFrames"
- "从Remotion迁移"
- "翻译此Remotion组合"
- "将其重写为HyperFrames HTML"

**不要在此技能时使用：**

- (a) 用户正在创建新的**HyperFrames组合**，即使他们有或正在A/B测试类似的Remotion视频。
- (b) 用户在提及Remotion时没有要求迁移。
- (c) 用户共享Remotion代码作为参考材料，而不是要求翻译。
- (d) 用户要求"与我的Remotion一个相同的视频"而没有明确要求迁移源——将其视为新鲜的HyperFrames构建。

**不支持（拒绝——这不是此技能的作用）：**

- **反向方向。** 将HyperFrames组合导出到Remotion（或任何其他框架）不是一个工作流程——翻译是Remotion → HyperFrames仅。明确说明。
- **非Remotion源。** 一个After Effects项目（`.aep`）、一个Framer Motion / 纯React / CSS动画或任何其他工具的源不是Remotion组合——没有Remotion源可翻译。通过 `/general-video`原生重新创建它，或者在HyperFrames无法表示它的情况下拒绝。

如有疑问，默认使用 `/general-video`（通用的HyperFrames创作流程）创作原生的HyperFrames组合。

## 工作流程

### 第1步：检查源

在Remotion源目录上运行 [`scripts/lint_source.py`](scripts/lint_source.py)。检查器检测无法干净翻译的模式：

- **阻止器**（拒绝 + 推荐互操作）：`useState`、`useReducer`、`useEffect`/`useLayoutEffect`带有非空依赖、异步 `calculateMetadata`、第三方React UI库（MUI、Chakra、Mantine、antd、shadcn、Radix、NextUI）。
- **警告**（删除结构后翻译）：`@remotion/lambda` 配置、`delayRender`、`useCallback`、`useMemo`、自定义钩子。
- **信息**（带注释翻译）：`staticFile`、`interpolateColors`。

如果任何阻止器触发，**停止**。阅读 [`references/escape-hatch.md`](references/escape-hatch.md) 并显示推荐消息。警告不会停止翻译——在步骤3中删除有问题的结构，并在 `TRANSLATION_NOTES.md` 中记录差距。`@remotion/lambda` 配置是标准的警告案例：技能删除导入 + `renderMediaOnLambda(...)` 调用，但翻译组合的其余部分。

### 第2步：规划翻译

阅读 [`references/api-map.md`](references/api-map.md)——每个Remotion API及其HF等效物或主题参考的索引。根据源使用的内容确定您将需要哪些主题参考：

| 源包含                                                           | 加载参考                                |
| ------------------------------------------------------------------------- | --------------------------------------------- |
| `Composition`、`defaultProps`、`schema`、`calculateMetadata`              | [`parameters.md`](references/parameters.md)   |
| `Sequence`、`Series`、`Loop`、`AbsoluteFill`、`Freeze`                    | [`sequencing.md`](references/sequencing.md)   |
| `useCurrentFrame`、`interpolate`、`spring`、`Easing`、`interpolateColors` | [`timing.md`](references/timing.md)           |
| `Audio`、`Video`、`Img`、`IFrame`、`staticFile`、`delayRender`            | [`media.md`](references/media.md)             |
| `TransitionSeries`、`@remotion/transitions`                               | [`transitions.md`](references/transitions.md) |
| `@remotion/lottie`                                                        | [`lottie.md`](references/lottie.md)           |
| `@remotion/google-fonts/<Family>`、`Font.loadFont`、`@font-face`          | [`fonts.md`](references/fonts.md)             |

不要加载所有内容——仅加载特定源需要的部分。

**在实时目录中搜索表格未映射的任何视觉效果。** 当源用没有HF API等效物的外观绘制时——扫描线/CRT叠加、故障或色差通道、着色器擦除、胶片颗粒处理——在用GSAP手写它之前运行 `npx hyperframes catalog --query "<用普通英语描述的效果>" --json`。搜索不需要**安装任何内容**：没有项目、没有先前的 `add`、没有账户。它从任何目录对托管注册表（~400个模块和组件）进行排名，并且 `transitions.md` 已经通过 `npx hyperframes add sdf-iris` 采取了这种路线来处理 `clockWipe()` / `iris()`。真实组件比手绘近似更接近源，因此它通常提高SSIM，而不是降低它——但步骤4中的渲染差异仍然是仲裁者。当搜索返回没有适合的内容时，手动编写效果，并在 `TRANSLATION_NOTES.md` 中记录替代方案，无论如何。

### 第3步：生成HF组合

使用以下内容发出 `index.html`：

- 根 `<div id="stage">` 携带组合的 `data-composition-id`、`data-start="0"`、`data-duration`（以秒为单位）、`data-fps`、`data-width`、`data-height`，以及每个标量属性的 `data-*`。
- 每个场景一个主机 `<div>`，带有 `data-composition-src="compositions/<scene>.html"` 和 `data-start` / `data-duration` / `data-track-index`。根不包含嵌套布局。
- 每个场景一个 `compositions/<scene>.html`（一个 `<template>` 子组合）：它的内联 `<style>` 用于布局（CSS设置每个动画属性的 `from` 状态），它的标记，以及场景本地时间中的一个暂停的 `gsap.timeline({paused: true})`。每个Remotion `useCurrentFrame()` 派生都成为该时间线上的补间，偏移量在场景内。
- 每个场景文件中的 `window.__timelines["<scene-id>"] = tl;`，以及 `window.__timelines["<composition-id>"]` 为根的（可能为空的）时间线。

自定义React子组件内联为重复的HTML，使用属性接口作为模板（有关每个实例的 `data-*` 模式，请参阅 [`parameters.md`](references/parameters.md)）。

### 第4步：验证

运行评估框架—— [`references/eval.md`](references/eval.md) 为完整指南。快速路径：

```bash
# 渲染Remotion基线（在固定装置中的npm install后）
cd remotion-src && npx remotion render <CompositionId> out/baseline.mp4

# 渲染HF翻译
cd ../hf-src && npx hyperframes render --skill=remotion-to-hyperframes --output ../hf.mp4

# SSIM差异
../../scripts/render_diff.sh ./remotion-src/out/baseline.mp4 ./hf.mp4 ./diff
```

阈值：低于源复杂性级别的 `p05` 约0.02（见 `eval.md` 的验证阈值表）。如果差异失败，运行 [`scripts/frame_strip.sh`](scripts/frame_strip.sh) 查看哪些帧出现了差异，然后重新阅读相关的定时/序列/媒体参考。

**关键**：两个渲染必须使用匹配的像素格式。在Remotion源的 `remotion.config.ts` 中设置 `Config.setVideoImageFormat("png")` + `Config.setColorSpace("bt709")`——否则差异测量的是编码差异（约0.05 SSIM打击），而不是翻译保真度。

### 第5步：记录差距

任何无法干净翻译的内容（音量渐变被丢弃、自定义演示近似、字体被替代）都会在HF输出旁边编写 `TRANSLATION_NOTES.md`。参见 [`references/limitations.md`](references/limitations.md) 了解格式。

## 此技能明确不做什么

- **翻译React状态机。** 通过 `useState` + `useEffect` 驱动的动画组合在HyperFrames的顺序驱动模型中不是确定性帧捕获目标。建议运行时互操作模式。
- **在HyperFrames旁边运行Remotion的渲染管道。** 那是来自 [PR #214](https://github.com/heygen-com/hyperframes/pull/214) 的运行时互操作模式——一个单独的解决方案，用于此技能的检查失败的组合。

(`@remotion/lambda` 不是阻止器——Lambda配置是部署，不是动画。技能将其作为警告丢弃，并翻译其余部分。参见 [`references/escape-hatch.md`](references/escape-hatch.md)。)

## 如何评估自己的翻译

运行测试语料库协调器：

```bash
./assets/test-corpus/run.sh
```

它运行T1、T2、T3（渲染 + 差异）和T4（检查验证），打印每个级别的通过/失败表，并发出汇总的JSON报告。使用此方法验证技能在干净的签出上端到端工作——并且作为编辑任何参考后的回归检查。

验证基线（截至2026-04-27）：

| 级别 | 组合形状                           | 平均SSIM | 阈值 |
| ---- | ------------------------------------------- | --------- | --------- |
| T1   | 单元素淡入                      | 0.974     | 0.95      |
| T2   | 多场景 + spring + audio + image        | 0.985     | 0.95      |
| T3   | 数据驱动，自定义子组件，计数器 | 0.953     | 0.90      |
| T4   | 逃逸通道（8检查案例）                 | 8/8通过  | n/a       |
