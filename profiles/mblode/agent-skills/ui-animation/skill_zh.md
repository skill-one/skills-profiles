# UI 动画

- **职责范围：** 设计、实现、评审、调试 UI 动画（弹簧、手势、拖拽、缓动、CSS 过渡、关键帧、Motion），筛选出真正能从动画中受益的界面元素，通过录制回放测量动画（提取帧、追踪、拟合曲线）以生成代码和交接规范，命名描述的动画效果（反向查找词汇），以及控制稀疏界面音效。
- **非职责范围：** 选择整体视觉方向、调色板或字体（使用 `ui-design` Direction 模式），评审整个页面的 UI 质量（使用 `ui-design` Audit 模式），或命名文本效果规范（在安装了外部 `animate-text` 技能的地方使用）。

## 路由边界

`product-design` 负责动作语义、范围、可逆性以及有争议的状态选择。`ui-design` 构建和样式化这些状态。`ui-animation` 负责时序、手势和测量动画。缺少加载或错误状态的常规流程将保留在 UI 构建；替换控制的手势需要在产品决策和可访问替代方案之前确定其物理特性。

## 参考文件

| 文件 | 读取时机 |
| --- | --- |
| [references/discovery-workflow.md](references/discovery-workflow.md) | 在现有界面中寻找值得动画化的机会 |
| [references/decision-framework.md](references/decision-framework.md) | 默认：决定是否/为何要动画化，选择缓动特性；也是 Discovery 扫描的接缝列表 |
| [references/spring-animations.md](references/spring-animations.md) | 弹簧物理、Motion `useSpring`、配置弹簧参数、Apple 阻尼/响应值、非对称开合特性、中断机制 |
| [references/component-patterns.md](references/component-patterns.md) | 带动画的按钮、弹出框、工具提示、抽屉、模态框、吐司 |
| [references/clip-path-techniques.md](references/clip-path-techniques.md) | 用于揭示、标签、长按删除、比较滑块的 `clip-path` |
| [references/gesture-drag.md](references/gesture-drag.md) | 拖拽、滑动关闭、动量、指针捕获、速度交接、动量投影、旋转/旋钮拖拽、定位点、轮播 `touch-action` |
| [references/scroll-animations.md](references/scroll-animations.md) | 滚动触发的揭示、滚动驱动的动画 (`animation-timeline`, `useScroll`)、视差、粘性滚动故事、以及滚动动画不应存在的情况 |
| [references/performance-deep-dive.md](references/performance-deep-dive.md) | 卡顿、CSS 与 JS、WAAPI、CSS 变量陷阱、Framer Motion 注意事项 |
| [references/debugging-symptoms.md](references/debugging-symptoms.md) | 动画感觉不对劲且原因未命名：针对迟缓、机械、廉价、跳跃和误触动的动画的索引表格 |
| [references/svg-animation.md](references/svg-animation.md) | 动画矢量图形：线绘制 (`stroke-dashoffset`)、SVG 变换原点陷阱、路径变形、抖动、环境生命 |
| [references/review-format.md](references/review-format.md) | 评审动画代码：十个标准（每个都有现场触发器）、Before/After/Why 表格、Block/Approve 判决 |
| [references/contextual-animations.md](references/contextual-animations.md) | 上下文图标交换、单词级交错进入、边缘弱化、固定偏移退出 |
| [references/transition-recipes.md](references/transition-recipes.md) | 安装 CSS 过渡：容器变形、卡片调整大小、徽章、下拉菜单、模态框、面板、页面滑动、图标交换、数字弹出、里程表滚动、文本交换、成功、头像悬停、错误抖动 |
| [references/measurement-guide.md](references/measurement-guide.md) | 反向工程：测量什么、眼睛与脚本、读取 `metrics.json`、选择 ROI |
| [references/curve-fitting.md](references/curve-fitting.md) | 反向工程：读取 `fit_curves.py` 输出、弹簧与贝塞尔、判断拟合误差、非对称开合 |
| [references/code-output.md](references/code-output.md) | 反向工程：为 CSS、Motion/Framer Motion、SwiftUI、React Native、UIKit 生成代码 |
| [references/choreography.md](references/choreography.md) | 反向工程：多元素/多阶段动画：交错、模糊前移动、边缘逐点沉降 |
| [references/live-tuning.md](references/live-tuning.md) | 在没有参考模型的情况下实时调整曲线：DevTools 贝塞尔编辑器、动画面板中重时序、当控制面板库值得依赖时 |
| [references/vocabulary.md](references/vocabulary.md) | 命名用户模糊描述的动画效果（“当...时叫什么”） |
| [references/interface-sfx.md](references/interface-sfx.md) | 点击声音、界面音频、UI SFX、触觉加声音，或“为什么网页害怕声音” |

## 核心规则

- 为反馈、定位、连续性或刻意愉悦而动画。如果只是“看起来很酷”且用户经常看到，则不要。
- 保持键盘焦点和重复导航即时。状态转换可以动画化，如果焦点和任务完成不等待它。
- 优先使用 CSS 过渡来中断 UI：关键帧在中断时从零重新开始，过渡重新目标。仅用于预定序列的关键帧。
- 实现优先级：CSS 过渡 > WAAPI > CSS 关键帧 > JS (`requestAnimationFrame`)；在负载下 CSS 保持平滑，而 JS 丢帧。
- 非对称时序：偶尔交互可以稍慢进入、快速退出。高频短暂 UI（悬停高亮、弹出框、面板切换）则相反：立即进入（0ms）、快速淡出退出（100-150ms），使操作感觉即时。
- 可点击控件在 `:active` 时 0ms 压下并设置 `touch-action: manipulation`。
- 使用 `@starting-style` 进行 DOM 进入；在不支持的地方回退到 `data-mounted` 属性。
- 小的 `filter: blur(2px)` 隐藏交换内容之间的粗糙过渡。

## 动画设计原则

- **连续性胜过传送。** 两个状态下都可见的元素原地过渡；从元素所在位置扩展，而不是在新实例中淡入。永远不要复制持久元素或在不同共享组件的视图之间硬切；硬切会丢失空间上下文。
- **方向性动画匹配位置。** 标签和轮播过渡沿匹配空间布局的方向动画（左到右前进，右到左后退）。
- **从触发器中浮现。** 叠加层、托盘和面板从打开它们的元素向外动画；通用的居中屏幕进入会破坏空间定位。更好的是，如果形状允许：让触发器成为表面（参见容器变形配方）。
- **在原位确认，而不是在角落。** 动作的结果属于引发它的控件：按钮变为“已复制”、保持并恢复。远角吐司使用户的视线离开他们刚刚触摸的东西去发现是否成功。保留角落吐司用于没有屏幕原点的结果（后台任务完成、传入消息）。
- **一起动画化配对状态。** 如果打开动画化，关闭也动画化。如果悬停有动画，焦点和按下状态获得等效反馈。不要只打磨重复交互的一半。
- **愉悦感与频率成反比。** 稀有交互获得更多个性；高频动作必须不可见。
- **动画增强感知速度。** 平滑过渡比硬切感觉更快，即使加载时间相同。

## 动画化内容

- 运动：仅 `transform` 和 `opacity`；它们跳过布局和绘制。
- 状态反馈：`color`、`background-color` 和 `opacity` 是可接受的。
- 永不动画化布局属性（`width`、`height`、`top`、`left`）；它们会触发每帧的布局重新计算。（例外：故意的容器插值，参见卡片调整大小和容器变形配方。）
- 永不使用 `transition: all`；它会动画化未预期的属性并默默采用未来的属性。明确列出它们。
- 避免核心交互的 `filter` 动画；如果不可避免，保持模糊 ≤ 20px（模糊很昂贵，尤其是在 Safari 中）。
- SVG：在 `<g>` 包装器上应用变换，`transform-box: fill-box; transform-origin: center`；否则它们会围绕画布原点旋转/缩放。线绘制、路径变形和 Motion SVG 原点覆盖在 [references/svg-animation.md](references/svg-animation.md) 中。
- `transform: scale()` 也缩放子元素（图标、文本、边框按比例缩放），与 `width`/`height` 不同：这是按反馈的特征，但在内部元素必须保持固定大小时要考虑它。
- 在主题切换期间禁用过渡（`[data-theme-switching] * { transition: none !important }`），或每个主题属性都同时动画化。切换后强制重排（`void document.body.offsetHeight`）并在下一帧移除覆盖，或使用 `next-themes` `disableTransitionOnChange`。

## 缓动默认值

| 元素                   | 持续时间     | 缓动                           |
| --------------------- | ------------ | -------------------------------- |
| 按钮按下反馈         | 100-160ms    | `cubic-bezier(0.22, 1, 0.36, 1)` |
| 工具提示、小弹出框      | 125-200ms    | `ease-out` 或进入曲线        |
| 下拉菜单、选择器        | 150-250ms    | `cubic-bezier(0.22, 1, 0.36, 1)` |
| 模态框、抽屉           | 200-350ms    | `cubic-bezier(0.22, 1, 0.36, 1)` |
| 屏幕上的移动/滑动      | 200-300ms    | `cubic-bezier(0.25, 1, 0.5, 1)`  |
| 页面过渡              | 250-400ms    | 进入或移动曲线              |
| 悬停（颜色/不透明度）    | 200ms        | `ease`                           |
| 悬停（变换/缩放）       | 100-150ms    | 进入曲线                      |
| 插图/营销            | 最高 1000ms | 弹簧或自定义                 |

保持常规 UI 在 300ms 以下；根据距离缩放持续时间（全屏滑动可以超过 300ms，6px 工具提示移动保持在 150ms 以下）。

**命名曲线**

- **进入：** `cubic-bezier(0.22, 1, 0.36, 1)` 用于进入和基于变换的悬停
- **移动：** `cubic-bezier(0.25, 1, 0.5, 1)` 用于滑动、抽屉、面板
- **iOS 风格抽屉：** `cubic-bezier(0.32, 0.72, 0, 1)`（极陡峭的起始；这就是为什么 500ms 不显得慢）
- **指数退出：** `cubic-bezier(0.19, 1, 0.22, 1)` 用于戏剧性揭示、卡片悬停、文本揭示
- **按下：** `cubic-bezier(0.25, 0.46, 0.45, 0.94)` 用于按钮按下反馈
- **屏幕上移动：** `cubic-bezier(0.645, 0.045, 0.355, 1)` 用于往返屏幕内的移动

避免为 UI 使用 `ease-in`：它开始慢，所以元素滞后于用户操作，感觉迟缓。优先使用 [easing.dev](https://easing.dev/) 的自定义曲线，而不是内置的 `ease`/`ease-out`，它们的温和加速读起来柔和，而不是果断。

## 过渡决策规则

首先匹配 UI 元素，然后从 [references/transition-recipes.md](references/transition-recipes.md) 中选择配方：

| UI 模式 | 配方 |
|---|---|
| 触发器 + 漂浮点/计数 | 通知徽章 |
| 触发器扩展到它打开的表面 | 容器变形 |
| 触发器 + 锚定表面 | 菜单下拉 |
| 屏幕上方的居中表面 | 模态对话框 |
| 面板滑入现有容器 | 面板揭示 |
| 列表 ↔ 详情或向导步骤 | 页面并排滑动 |
| 元素尺寸变化 | 卡片调整大小 |
| 原地更新文本 | 文本状态交换 |
| 同一槽位中的两个图标 | 图标交换 |
| 数字自行出现 | 数字弹出 |
| 用户驾驶的数字 | 里程表数字滚动 |
| 确认/成功时刻 | 成功庆祝 |
| 水平堆栈中的悬停项 | 头像组悬停 |
| 表单验证错误 | 错误状态抖动 |

除非设计需要 JS 协调，否则优先使用低开销过渡（纯 CSS）。

## 空间和时序

- 弹出框 `transform-origin` 在触发器（模态框保持 `center`），对话框/菜单进入从 `scale(0.9-0.96)` 而不是 `scale(0)`（低端小弹出框，高端全屏对话框：大面积表面在绝对像素中已经移动很远），以及 30-50ms 交错（总时长小于 300ms，最重要的元素领先）。完整规则和代码在 [references/component-patterns.md](references/component-patterns.md) 和 [references/contextual-animations.md](references/contextual-animations.md) 中。
- **配对元素规则：** 一起动画化的元素（模态框 + 叠加层、工具提示 + 箭头、FAB + 标签）必须共享缓动和持续时间。不匹配的时序是“感觉不对劲”的常见原因。

## 可访问性

- 通过 `@media (hover: hover) and (pointer: fine)` 或触摸设备在轻击时重放悬停来控制悬停（动画和绘制）。在添加门之前检查生成的 CSS；Tailwind v4 已经将 `hover:` 包裹在 `@media (hover: hover)` 中。
- 在直接操作期间，将元素锁定到指针，无缓动；释放后添加缓动。
- 可选界面 SFX：稀疏、手势解锁、仅加性确认。参见 [references/interface-sfx.md](references/interface-sfx.md)。

## 性能

- 使用 `IntersectionObserver` 在屏幕外暂停循环动画；即使不可见，它们也会消耗 GPU。
- 仅在重动画期间切换 `will-change`，且仅针对 `transform`/`opacity`；之后移除它。每次提升都会消耗合成器内存；在许多元素上永久提升比不提升更糟。
- 不要通过 CSS 变量在容器上动画拖拽；每次更新都会为所有子元素重新计算样式。直接在移动元素上设置 `transform`。
- Motion `x`/`y` 值是轴移动和拖拽的默认值（它们绕过 React 重绘）。当一个所有者必须组合多个变换函数、与非 Motion 代码互操作或存活在繁忙的主线程时，使用完整的 `transform` 字符串：短横线运行在 `requestAnimationFrame` 上，当动画与导航、数据加载或水合重合时掉帧；CSS/WAAPI 在那里保持平滑。
- 仅有时会卡顿的动画（打开时、导航期间、数据到达时）通常是共享同一帧的长任务，而不是昂贵的动画。不要在同一帧启动动画和昂贵工作：启动动画，让一帧落地，然后做工作，或将其推迟到 `transitionend`。

## 反模式

未涵盖的高信号失败：

- 无用户触发而挂载动画：意外的动画会使用户迷失方向；用户没有做任何导致它的事情。
- 拖拽边界上的硬停止感觉不完整；应用摩擦/阻尼，使其在边界后减弱（参见手势拖拽参考）。
- 动画容器和交错其子元素：每个容器选择一个进入。如果面板滑入，其内容应在到达时已经可见。
- 第一个打开后的工具提示动画：组内后续工具提示立即打开，或工具栏感觉卡顿。
- 滚动揭示产品 UI、首屏内容或页面每个部分：滚动揭示属于营销界面的几个选定时刻，运行一次，且永不滚动回滚（参见 [references/scroll-animations.md](references/scroll-animations.md)）。
- 滚动动画的缓动或持续时间：滚动位置是时钟，所以任何曲线或持续时间都会使其滞后于滚动条。`linear` 和无持续时间是那里正确的，且仅在那里。
- 为新工作安装 `framer-motion`：该包现在为 `motion`，React 导入来自 `motion/react`。旧包仍然解析，所以混合代码库可以编译，同时发送两份库副本。

## 工作流程

复制和跟踪：

```text
动画进度：
- [ ] 步骤 1：决定交互是否应该动画化
- [ ] 步骤 2：选择目的、缓动和持续时间
- [ ] 步骤 3：选择实现风格
- [ ] 步骤 4：加载相关组件或技术参考
- [ ] 步骤 5：验证时序、中断和设备行为
```

1. 回答 [references/decision-framework.md](references/decision-framework.md) 中的四个问题：是否动画化？目的？缓动？速度？
2. 从上表中选择持续时间。如果值有争议或组件难以访问，请在 DevTools bezier 编辑器中实时调整，而不是猜测，然后将结果烘焙到源代码 ([references/live-tuning.md](references/live-tuning.md))。
3. 选择实现：CSS 过渡 > WAAPI > 弹簧 > 关键帧 > JS。
4. 加载您的组件或技术的参考。
5. 审查时，应用 [references/review-format.md](references/review-format.md) 中的严格立场：对照十个标准测量，输出 Before/After/Why 表格，然后是一个分级的裁决，以 Block/Approve 决策结束。

## 验证

为每个检查生成证据（DevTools 观察，而不是“看起来很好”）：

- Grep 差分查找布局属性过渡（`width`、`height`、`top`、`left`）和 `transition: all`。
- 快速切换组件；确认过渡重新目标而不是从零重新开始。
- 在 DevTools 动画面板中减速到 10% 以捕获时序和 `transform-origin` 问题（在满速时不可见）。
- 确认 `will-change` 在动画周围切换，而不是永久设置，并且循环动画在屏幕外暂停。
- 在真实设备上测试触摸交互；模拟器低估手势和悬停轻击问题。
- 尊重 `prefers-reduced-motion`：用立即状态变化或受约束的淡出替换空间旅行。使用 `animation-play-state: paused` 暂停循环装饰（不要用 `display: none` 将它们拉出）。保持显式的用户触发反馈。在该模式下执行相同任务。

## 发现工作流程

对于“这个应该在哪里动画化”，加载 `references/discovery-workflow.md` 和 `references/decision-framework.md`。报告由目的和使用频率支持的机会。仅在实现范围之内时才实现建议。

## 反向工程工作流程

使用此分支来测量屏幕录制中的现有动画，然后生成代码和交接规范以重现它。脚本在 `scripts/` 下是规范、确定性的路径；运行它们而不是重建它们的逻辑。

将 `scripts/` 下的每个命令相对于安装的技能目录解析，而不是应用程序工作目录。

**依赖项：** `ffmpeg` 用于帧提取（`brew install ffmpeg`）；Python 并安装 `pip install opencv-python numpy scipy` 用于追踪和曲线拟合。优雅降级：仅使用 `ffmpeg` 可以提取帧并直观地推理；追踪和拟合需要 Python 包。

反向工程进度：
- [ ] 步骤 1：提取帧 + 接触表（如果开与关不同）
- [ ] 步骤 2：视觉检查：识别元素、效果、阶段
- [ ] 步骤 3：决定精度（仅眼睛 vs 脚本）
- [ ] 步骤 4：追踪运动并拟合曲线（如果升级）
- [ ] 步骤 5：标注编排（延迟、非对称）
- [ ] 步骤 6：为目标生成代码
- [ ] 步骤 7：与录制验证

1. **提取。** 运行 `python3 scripts/extract_frames.py <video> <outdir>`。修剪仅包含过渡的部分，使用 `--start`/`--duration`；如果交互有开和关，修剪两个窗口并运行管道一次每个方向（它们几乎不可能是镜像）。匹配 `--fps` 到源（用 `ffprobe` 探测），永远不要在源速率以上采样。首先打开 `contact_sheet.png`。
2. **视觉检查。** 命名移动的元素、每个效果（经常是各向异性的变换、不透明度、模糊、圆角半径、阴影、颜色），以及阶段，注意哪个属性领先和滞后。使用 `references/measurement-guide.md` 中的清单。
3. **决定精度。** 简单淡入或线性滑动：从接触表中读取时序，跳到步骤 5。弹性、弹簧或多属性运动：升级到步骤 4（用眼睛追踪弹簧不可靠）。
4. **追踪和拟合。** 运行 `python3 scripts/track_motion.py <outdir>` 以获取 `metrics.json`（传递 `--bbox X,Y,W,H` 以隔离一个元素），然后 `python3 scripts/fit_curves.py <outdir>/metrics.json` 以获取弹簧参数、cubic-bezier 和每属性拟合误差。传递与提取时相同的 `--fps`。阅读 `references/curve-fitting.md` 以选择模型；高误差在两者都意味着多阶段运动（分割并拟合每个段）。
5. **标注。** 加载 `references/choreography.md`。构建时序偏移表（每个属性何时开始和沉降）；领先/滞后差距和过度拉伸比任何单一曲线更能传达感觉。
6. **生成。** 将拟合参数代入 `references/code-output.md` 中的模板为目标。保持移动在 `transform`/`opacity`。当开和关不同时生成两个过渡，以及整合的交接规范，以便无需视频即可实现。
7. **验证。** 重新推导：播放生成的动画，屏幕录制它，将其重新通过 `extract_frames.py`，并比较接触表并排。减速到 0.1x 以确认阶段顺序和过度拉伸存活。确认代码仅动画化 `transform`、`opacity` 和 `filter`。

**反向工程陷阱：**

- `fit_curves.py` 默认为 `--fps 30`：提取时 60 但拟合时使用默认值，拟合的刚度降低到四分之一，而拟合持续时间翻倍。始终传递提取的 fps 到拟合。
- 采样高于源速率会重复帧：24 fps GIF 在 60 fps 提取会因 `metrics.json` 中的平台运行而增加拟合误差。探测并匹配源速率。
- 屏幕录制会丢帧，iOS/QuickTime 捕获是可变帧率的；连续相同的行是重复帧，而不是暂停。如果平台主导，请以更稳定的速率重新录制。
- 将开和关作为单独片段报告，并报告两个曲线；永远不要拟合一个并反向使用它（参见 `references/choreography.md`）。将拟合 `error` 高于 0.08 视为可疑。

仅限维护：更改发现路由或门时，运行 `evaluations/` 中的场景作为回归基准。它们永远不会在用户任务期间加载。

## 来源

界面 SFX 门控取自 Craft (gustavo-fior) 和 Raphael Salaja 的网络声音写作。新奇 90/10 分割、单次介绍门控、以及循环 `animation-play-state` 取自 Rauno Freiberg。拒绝打包 emilkowalski/skills 和 gustavo-fior/craft：与该技能触发冲突。剪影和比例缩放已经在其中。

## 相关技能

- `product-design`：哪些状态存在，动作影响什么，以及它是否可逆。当手势替换控件时，首先路由到这里，因为滑动删除和长按确认改变了用户在改变其移动方式之前可以做什么。
- `ui-design` Direction 模式：视觉方向、调色板、字体；在调整运动之前确定视觉系统。
- `ui-design` Audit 模式：页面/功能级 UI 质量审计。动画工艺和修复属于这里。
- 可选外部 `animate-text` 技能（如果安装）：经过策划的命名文本效果（打字机、行揭示、交错构建）具有精确的 JSON 规格。

仅限维护：`evals/evals.json` 包含对此技能更改的回归场景；它不会在用户任务期间加载。
