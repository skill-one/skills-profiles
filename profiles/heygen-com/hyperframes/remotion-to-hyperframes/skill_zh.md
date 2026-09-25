> **首先，保持这项技能的更新状态——在运行前与用户确认：** `npx hyperframes skills update remotion-to-hyperframes`。当所有内容都为最新时，这是一个快速的无操作；否则，它将在您依赖它们之前刷新这项技能及其依赖的核心领域技能。

# Remotion 到 HyperFrames

> **正门是 `/hyperframes`。** 仅用于将现有的 **Remotion**（React）组合的源移植到 HyperFrames，这是一条单向路径。创建新的 **组合**、从非 Remotion 源（After Effects、Framer Motion、纯 React / CSS——没有 Remotion 源可以翻译）、提及 Remotion 的情况或任何不确定性 → 首先阅读 `/hyperframes`：意图层拥有所有路由决策。

## 概述

将 Remotion（基于 React）视频组合翻译成 HyperFrames（HTML + GSAP）组合。大多数 Remotion 习语都有直接的 HyperFrames 对应物——对于典型的 ~80% 的组合，翻译是机械的。这项技能编码了映射，并通过拒绝翻译不适合 HF 的顺序驱动模型的模式来防止 20% 的损失，并建议从 [PR #214](https://github.com/heygen-com/hyperframes/pull/214) 中的运行时互操作模式。

这项技能附带一个 **分层的测试语料库**（T1–T4，共 4 个测试用例），根据测量的 SSIM 阈值对翻译进行评分。不要在不运行评估的情况下进行翻译——一个看起来正确的翻译，但渲染比验证的基线低 0.05 SSIM，会被静默地判定为错误。

## 使用时机

**仅在用户明确要求从 Remotion 迁移时使用这项技能。** 示例触发短语：

- "将我的 Remotion 项目移植到 HyperFrames"
- "将这个 Remotion 代码转换为 HyperFrames"
- "从 Remotion 迁移"
- "翻译这个 Remotion 组合"
- "将其重写为 HyperFrames HTML"

**不要在这种情况下使用这项技能：**

- (a) 用户正在创建新的 HyperFrames 组合，即使他们有或正在 A/B 测试类似的 Remotion 视频。
- (b) 用户在提及 Remotion 时没有要求迁移。
- (c) 用户共享 Remotion 代码作为参考材料而不是要求翻译。
- (d) 用户要求 "与我的 Remotion 视频相同" 而没有明确要求迁移源——将其视为新的 HyperFrames 构建。

**不支持（拒绝——这不是这项技能的功能）：**

- **反向方向。** 将 HyperFrames 组合导出到 Remotion（或任何其他框架）不是一个工作流程——翻译是 Remotion → HyperFrames 仅此而已。明确说明这一点。
- **非 Remotion 源。** After Effects 项目（`.aep`）、Framer Motion / 纯 React / CSS 动画或任何其他工具的源不是 Remotion 组合——没有 Remotion 源可以翻译。通过 `/general-video` 原生重新创建它，或者如果 HyperFrames 无法表示它，则拒绝。

不确定时，默认使用 `/general-video`（通用的 HyperFrames 编写流程）编写原生 HyperFrames 组合。

## 工作流程

### 第 1 步：检查源

在 Remotion 源目录上运行 [`scripts/lint_source.py`](scripts/lint_source.py)。检查器检测无法干净翻译的模式：

- **阻止器**（拒绝 + 推荐互操作）：`useState`、`useReducer`、`useEffect`/`useLayoutEffect` 具有非空依赖、异步 `calculateMetadata`、第三方 React UI 库（MUI、Chakra、Mantine、antd、shadcn、Radix、NextUI）。
- **警告**（删除结构后翻译）：`@remotion/lambda` 配置、`delayRender`、`useCallback`、`useMemo`、自定义钩子。
- **信息**（带注释翻译）：`staticFile`、`interpolateColors`。

如果任何阻止器触发，**停止**。阅读 [`references/escape-hatch.md`](references/escape-hatch.md) 并显示推荐消息。警告不会停止翻译——在步骤 3 中删除有问题的结构，并在 `TRANSLATION_NOTES.md` 中记录差距。`@remotion/lambda` 配置是标准的警告案例：技能删除导入 + `renderMediaOnLambda(...)` 调用，但翻译组合的其余部分。

### 第 2 步：规划翻译

阅读 [`references/api-map.md`](references/api-map.md)——每个 Remotion API 及其 HF 对应物或主题参考的索引。根据源使用的内容确定您需要哪些主题参考：

| 源包含                                                                 | 加载参考                                |
| ------------------------------------------------------------------------- | --------------------------------------------- |
| `Composition`、`defaultProps`、`schema`、`calculateMetadata`              | [`parameters.md`](references/parameters.md)   |
| `Sequence`、`Series`、`Loop`、`AbsoluteFill`、`Freeze`                    | [`sequencing.md`](references/sequencing.md)   |
| `useCurrentFrame`、`interpolate`、`spring`、`Easing`、`interpolateColors` | [`timing.md`](references/timing.md)           |
| `Audio`、`Video`、`Img`、`IFrame`、`staticFile`、`delayRender`            | [`media.md`](references/media.md)             |
| `TransitionSeries`、`@remotion/transitions`                               | [`transitions.md`](references/transitions.md) |
| `@remotion/lottie`                                                        | [`lottie.md`](references/lottie.md)           |
| `@remotion/google-fonts/<Family>`、`Font.loadFont`、`@font-face`          | [`fonts.md`](references/fonts.md)             |

不要加载所有内容——仅加载特定源需要的部分。

**在实时目录中搜索表格未映射的任何视觉效果。** 当源用没有 HF API 对应物的外观绘制时——扫描线/CRT 叠加、故障或色差通道、着色器擦除、胶片颗粒处理——在用 GSAP 手写它之前运行 `npx hyperframes catalog --query "<用普通英语描述的效果>" --json`。搜索不需要**安装任何内容**：没有项目、没有先前的 `add`、没有账户。它从任何目录中排名整个托管注册表（~400 个模块和组件），并且 `transitions.md` 已经通过 `npx hyperframes add sdf-iris` 采取了这种路线来处理 `clockWipe()` / `iris()`。真实组件比手写近似更接近源，因此它通常提高 SSIM 而不是降低它——但第 4 步中的渲染差异仍然是仲裁者。当搜索返回没有适合的内容时，手动编写效果，并在 `TRANSLATION_NOTES.md` 中记录替代方案，无论哪种方式。

### 第 3 步：生成 HF 组合

使用以下内容生成 `index.html`：

- 根 `<div id="stage">` 携带组合的 `data-composition-id`、`data-start="0"`、`data-duration`（以秒为单位）、`data-fps`、`data-width`、`data-height`，以及每个标量属性的一个 `data-*`。
- 每个场景一个主机 `<div>`，具有 `data-composition-src="compositions/<scene>.html"` 和 `data-start` / `data-duration` / `data-track-index`。根不包含嵌套布局。
- 每个场景一个 `compositions/<scene>.html`（一个 `<template>` 子组合）：它的内联 `<style>` 用于布局（CSS 设置每个动画属性的 `from` 状态），它的标记，以及场景本地时间中的一个暂停 `gsap.timeline({paused: true})`。每个 Remotion `useCurrentFrame()` 派生都成为该时间线上的补间，位于场景内的偏移量。
- 每个场景文件中的 `window.__timelines["<scene-id>"] = tl;`，以及根的（可能为空）时间线上的 `window.__timelines["<composition-id>"]`。

自定义 React 子组件内联为重复的 HTML，使用属性接口作为模板（有关每个实例的 `data-*` 模式，请参阅 [`parameters.md`](references/parameters.md)）。

### 第 4 步：验证

运行评估框架——[`references/eval.md`](references/eval.md) 为完整指南。快速路径：

```bash
# 渲染 Remotion 基线（在 fixture 中 npm install 后）
cd remotion-src && npx remotion render <CompositionId> out/baseline.mp4

# 渲染 HF 翻译
cd ../hf-src && npx hyperframes render --skill=remotion-to-hyperframes --output ../hf.mp4

# SSIM 差异
../../scripts/render_diff.sh ./remotion-src/out/baseline.mp4 ./hf.mp4 ./diff
```

阈值：源复杂度级别的 `p05` 以下约 0.02（见 `eval.md` 的验证阈值表）。如果差异失败，运行 [`scripts/frame_strip.sh`](scripts/frame_strip.sh) 查看哪些帧出现了差异，然后重新阅读相关的定时/序列/媒体参考。

**关键**：两个渲染必须使用匹配的像素格式。在 Remotion 源的 `remotion.config.ts` 中设置 `Config.setVideoImageFormat("png")` + `Config.setColorSpace("bt709")`——否则差异测量的是编码差异（约 0.05 SSIM 击中），而不是翻译保真度。

### 第 5 步：记录差距

任何无法干净翻译的内容（音量渐变丢失、自定义演示近似、字体替换）都会在 HF 输出旁边编写 `TRANSLATION_NOTES.md`。参见 [`references/limitations.md`](references/limitations.md) 了解格式。

## 这项技能明确不做什么

- **翻译 React 状态机。** 通过 `useState` + `useEffect` 驱动的动画组合在 HyperFrames 的顺序驱动模型中不是确定性帧捕获目标。建议运行时互操作模式。
- **在 HyperFrames 旁边运行 Remotion 的渲染管道。** 这是来自 [PR #214](https://github.com/heygen-com/hyperframes/pull/214) 的运行时互操作模式——一个单独的解决方案，用于失败的组合。

(`@remotion/lambda` 不是阻止器——Lambda 配置是部署，不是动画。技能将其作为警告丢弃，并翻译其余部分。参见 [`references/escape-hatch.md`](references/escape-hatch.md)。)

## 如何自行评分翻译

运行测试语料库协调器：

```bash
./assets/test-corpus/run.sh
```

它运行 T1、T2、T3（渲染 + 差异）和 T4（检查验证），打印每个级别的通过/失败表，并输出聚合 JSON 报告。使用此方法验证技能在干净的签出上端到端工作——并且作为编辑任何参考后的回归检查。

验证基线（截至 2026-04-27）：

| 级别 | 组合形状                           | 平均 SSIM | 阈值 |
| ---- | ------------------------------------------- | --------- | --------- |
| T1   | 单元素淡入                      | 0.974     | 0.95      |
| T2   | 多场景 + spring + 音频 + 图像        | 0.985     | 0.95      |
| T3   | 数据驱动，自定义子组件，计数器 | 0.953     | 0.90      |
| T4   | 逃逸通道（8 检查验证）                 | 8/8 通过  | n/a       |
