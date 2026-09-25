# 用户界面维基

面向网页界面的全面 UI/UX 最佳实践指南。包含 12 个类别的 152 条规则，按影响程度优先级排序，用于指导自动化代码审查和生成。

## 应用场景

在以下情况参考这些指南：
- 实施或审查动画（CSS 过渡、Motion/Framer Motion）
- 在弹簧、缓动曲线或无动画之间进行选择
- 使用 AnimatePresence 和退出动画
- 使用伪元素或 View Transitions API 编写 CSS
- 为 UI 添加音频反馈或程序化声音
- 构建变形图标组件
- 使用动态内容动画容器宽/高
- 设计符合认知心理学的 UI（Fitts 定律、Hick 定律、Miller 定律）
- 实施预测预取以提升感知性能
- 设置排版、OpenType 功能或数字格式

## 按优先级分类的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | 动画原则 | 关键 | `timing-`, `physics-`, `staging-` |
| 2 | 时间函数 | 高 | `spring-`, `easing-`, `duration-`, `none-` |
| 3 | 退出动画 | 高 | `exit-`, `presence-`, `mode-`, `nested-` |
| 4 | CSS 伪元素 | 中 | `pseudo-`, `transition-`, `native-` |
| 5 | 音频反馈 | 中 | `a11y-`, `appropriate-`, `impl-`, `weight-` |
| 6 | 声音合成 | 中 | `context-`, `envelope-`, `design-`, `param-` |
| 7 | 变形图标 | 低 | `morphing-` |
| 8 | 容器动画 | 中 | `container-` |
| 9 | UX 定律 | 高 | `ux-` |
| 10 | 预测预取 | 中 | `prefetch-` |
| 11 | 排版 | 中 | `type-` |
| 12 | 视觉设计 | 高 | `visual-` |

## 快速参考

### 1. 动画原则 (关键)

- `timing-under-300ms` - 用户动画必须在 300ms 内完成
- `timing-consistent` - 相似元素使用相同的时序值
- `timing-no-entrance-context-menu` - 上下文菜单：无进入动画，仅退出动画
- `easing-natural-decay` - 使用指数衰减，而非线性
- `easing-no-linear-motion` - 线性缓动仅用于进度指示器
- `physics-active-state` - 交互元素需要 :active 缩放变换
- `physics-subtle-deformation` - 在 0.95-1.05 范围内进行挤压/拉伸
- `physics-spring-for-overshoot` - 使用弹簧进行过冲并重置，而非缓动
- `physics-no-excessive-stagger` - 每个项目延迟小于 50ms
- `staging-one-focal-point` - 一次一个突出动画
- `staging-dim-background` - 暗化模态/对话框背景
- `staging-z-index-hierarchy` - 动画元素尊重 z-index 层级

### 2. 时间函数 (高)

- `spring-for-gestures` - 手势驱动运动（拖拽、快速滑动）必须使用弹簧
- `spring-for-interruptible` - 可中断运动必须使用弹簧
- `spring-preserves-velocity` - 弹簧在释放时保留输入能量
- `spring-params-balanced` - 避免弹簧参数过度振荡
- `easing-for-state-change` - 系统状态变化使用缓动曲线
- `easing-entrance-ease-out` - 进入动画使用 ease-out
- `easing-exit-ease-in` - 退出动画使用 ease-in
- `easing-transition-ease-in-out` - 视图过渡使用 ease-in-out
- `easing-linear-only-progress` - 线性仅用于进度/时间表示
- `duration-press-hover` - 按钮悬停：120-180ms
- `duration-small-state` - 小状态变化：180-260ms
- `duration-max-300ms` - 用户发起的最大 300ms
- `duration-shorten-before-curve` - 使用更短的持续时间而非曲线修复缓慢感
- `none-high-frequency` - 高频交互无动画
- `none-keyboard-navigation` - 键盘导航即时，无动画
- `none-context-menu-entrance` - 上下文菜单：无进入动画，仅退出动画

### 3. 退出动画 (高)

- `exit-requires-wrapper` - 条件运动元素需要 AnimatePresence 包装器
- `exit-prop-required` - AnimatePresence 中的元素需要退出属性
- `exit-key-required` - 动态列表需要唯一键，而非索引
- `exit-matches-initial` - 退出动画与初始动画对称
- `presence-hook-in-child` - useIsPresent 在子组件中，而非父组件
- `presence-safe-to-remove` - 异步清理后调用 safeToRemove
- `presence-disable-interactions` - 退出元素禁用交互
- `mode-wait-doubles-duration` - "wait" 模式持续时间翻倍；时序减半
- `mode-sync-layout-conflict` - "sync" 模式导致布局冲突
- `mode-pop-layout-for-lists` - 列表重排序使用 popLayout
- `nested-propagate-required` - 嵌套 AnimatePresence 需要 propagate 属性
- `nested-consistent-timing` - 协调父-子退出时序

### 4. CSS 伪元素 (中)

- `pseudo-content-required` - ::before/::after 需要内容属性
- `pseudo-over-dom-node` - 伪元素覆盖额外 DOM 节点用于装饰
- `pseudo-position-relative-parent` - 父元素需要 position: relative
- `pseudo-z-index-layering` - z-index 用于正确伪元素层级
- `pseudo-hit-target-expansion` - 负值内边距用于更大的点击目标
- `pseudo-marker-styling` - 使用 ::marker 自定义列表符号样式
- `pseudo-first-line-styling` - 使用 ::first-line 用于排版处理
- `transition-name-required` - 视图过渡需要 view-transition-name
- `transition-name-unique` - 过渡期间每个过渡名称唯一
- `transition-name-cleanup` - 完成后清理过渡名称
- `transition-over-js-library` - 优先使用 View Transitions API 而非 JS 库
- `transition-style-pseudo-elements` - 样式 ::view-transition-group 用于自定义动画
- `native-backdrop-styling` - 使用 ::backdrop 用于对话框背景
- `native-placeholder-styling` - 使用 ::placeholder 用于输入框样式
- `native-selection-styling` - 使用 ::selection 用于文本选择样式

### 5. 音频反馈 (中)

- `a11y-visual-equivalent` - 每个声音必须有视觉等价物
- `a11y-toggle-setting` - 提供开关禁用声音
- `a11y-reduced-motion-check` - 尊重 prefers-reduced-motion 设置
- `a11y-volume-control` - 允许独立音量调节
- `appropriate-no-high-frequency` - 无打字或键盘导航声音
- `appropriate-confirmations-only` - 仅在支付、上传、提交时使用声音
- `appropriate-errors-warnings` - 用于无法忽视的错误提示
- `appropriate-no-decorative` - 无悬停或装饰性声音
- `appropriate-no-punishing` - 声音用于提示而非惩罚
- `impl-preload-audio` - 预加载音频文件避免延迟
- `impl-default-subtle` - 默认音量柔和（0.3），非刺耳
- `impl-reset-current-time` - 重置 currentTime 后再次播放
- `weight-match-action` - 声音权重匹配动作重要性
- `weight-duration-matches-action` - 声音时长匹配动作时长

### 6. 声音合成 (中)

- `context-reuse-single` - 重用单个 AudioContext，而非每个声音创建
- `context-resume-suspended` - 恢复暂停的 AudioContext 前播放
- `context-cleanup-nodes` - 播放后断开音频节点
- `envelope-exponential-decay` - 指数衰减用于自然效果
- `envelope-no-zero-target` - 指数衰减目标为 0.001，非 0
- `envelope-set-initial-value` - 衰减前设置初始值
- `design-noise-for-percussion` - 滤波噪声用于点击/轻击
- `design-oscillator-for-tonal` - 带音高扫频的振荡器用于音调声音
- `design-filter-for-character` - 带通滤波器塑造打击音效果
- `param-click-duration` - 点击声音：5-15ms 持续时间
- `param-filter-frequency-range` - 点击滤波器：3000-6000Hz
- `param-reasonable-gain` - 增益低于 1.0 防止削波
- `param-q-value-range` - 滤波器 Q 值：2-5，聚焦自然

### 7. 变形图标 (低)

- `morphing-three-lines` - 每个图标使用 3 条 SVG 线
- `morphing-use-collapsed` - 未使用线条使用折叠常量
- `morphing-consistent-viewbox` - 所有图标共享相同 viewBox (14x14)
- `morphing-group-variants` - 旋转变体共享组和基础线条
- `morphing-spring-rotation` - 使用弹簧物理效果旋转图标组
- `morphing-reduced-motion` - 尊重 prefers-reduced-motion
- `morphing-jump-non-grouped` - 非分组图标间旋转跳转即时
- `morphing-strokelinecap-round` - 圆形线帽
- `morphing-aria-hidden` - 图标 SVG aria-hidden

### 8. 容器动画 (中)

- `container-two-div-pattern` - 外层动画 div，内层测量 div；绝不使用同一元素
- `container-guard-initial-zero` - 初始渲染时边界 === 0，回退为 "auto"
- `container-use-resize-observer` - 使用 ResizeObserver 进行测量，而非 getBoundingClientRect
- `container-overflow-hidden` - 动画容器过渡期间设置 overflow: hidden
- `container-no-excessive-use` - 节制使用：按钮、手风琴、交互元素
- `container-callback-ref` - 使用回调引用（非 useRef）进行测量钩子
- `container-transition-delay` - 添加小延迟产生自然追赶感

### 9. UX 定律 (高)

- `ux-fitts-target-size` - 交互目标尺寸便于点击（最小 32px）
- `ux-fitts-hit-area` - 使用不可见填充或伪元素扩展点击区域
- `ux-hicks-minimize-choices` - 最小化选择以减少决策时间
- `ux-millers-chunking` - 将数据分块（5-9）便于扫描
- `ux-doherty-under-400ms` - 400ms 内响应感觉即时
- `ux-doherty-perceived-speed` - 使用骨架屏、乐观 UI、进度指示器制造速度感
- `ux-postels-accept-messy-input` - 接受混乱输入，输出清洁数据
- `ux-progressive-disclosure` - 先显示重要内容，再揭示复杂信息
- `ux-jakobs-familiar-patterns` - 使用用户熟悉的 UI 模式
- `ux-aesthetic-usability` - 视觉优化提升感知可用性
- `ux-proximity-grouping` - 空间上紧密间距组合相关元素
- `ux-similarity-consistency` - 相似元素外观一致
- `ux-common-region-boundaries` - 使用边界组合相关内容
- `ux-von-restorff-emphasis` - 使重要元素视觉突出
- `ux-serial-position` - 将关键项放在序列首尾
- `ux-peak-end-finish-strong` - 结束体验时显示清晰成功状态
- `ux-teslers-complexity` - 将复杂度移至系统，而非用户
- `ux-goal-gradient-progress` - 显示完成进度
- `ux-zeigarnik-show-incomplete` - 显示未完成状态驱动完成
- `ux-pragnanz-simplify` - 将复杂视觉简化为清晰形式
- `ux-pareto-prioritize-features` - 优先 20% 关键功能
- `ux-cognitive-load-reduce` - 减少额外认知负荷
- `ux-uniform-connectedness` - 使用线条或框架连接相关元素

### 10. 预测预取 (中)

- `prefetch-trajectory-over-hover` - 预测悬停轨迹；节省 100-200ms
- `prefetch-not-everything` - 按意图预取，非视口；避免带宽浪费
- `prefetch-hit-slop` - 使用 hitSlop 触发更早预测
- `prefetch-touch-fallback` - 触摸设备优雅回退（无光标）
- `prefetch-keyboard-tab` - 聚焦接近时键盘导航预取
- `prefetch-use-selectively` - 仅在感知延迟明显时使用

### 11. 排版 (中)

- `type-tabular-nums-for-data` - 数据列、仪表盘、价格使用表格数字
- `type-oldstyle-nums-for-prose` - 旧式数字融入正文
- `type-slashed-zero` - 代码相关 UI 使用斜杠零
- `type-opentype-contextual-alternates` - 保持 calt 开启用于上下文字形调整
- `type-disambiguation-stylistic-set` - 启用 ss02 区分 I/l/1 和 0/O
- `type-optical-sizing-auto` - 字体光学尺寸自动适应字形
- `type-antialiased-on-retina` - 高分辨率屏幕字体抗锯齿
- `type-text-wrap-balance-headings` - 标题使用 text-wrap: balance 产生均匀行
- `type-underline-offset` - 下划线偏移低于 descender
- `type-no-font-synthesis` - 禁用字体合成防止伪粗体/斜体
- `type-font-display-swap` - 使用 font-display: swap 避免加载时文字不可见
- `type-variable-weight-continuous` - 变量字体使用连续字重（100-900）
- `type-text-wrap-pretty` - body text 使用 text-wrap: pretty 减少孤行
- `type-justify-with-hyphens` - text-align: justify 配合 hyphens: auto
- `type-letter-spacing-uppercase` - 大写和小写字母加字间距
- `type-proper-fractions` - 使用对角线分数表示正确排版分数

### 12. 视觉设计 (高)

- `visual-concentric-radius` - 内层半径 = 外层半径减去填充
- `visual-layered-shadows` - 多层阴影产生真实深度
- `visual-shadow-direction` - 所有阴影共享相同偏移方向（单一光源）
- `visual-no-pure-black-shadow` - 阴影使用中性色，非纯黑
- `visual-shadow-matches-elevation` - 阴影大小表示一致比例的抬升
- `visual-animate-shadow-pseudo` - 通过伪元素不透明度动画阴影提升性能
- `visual-consistent-spacing-scale` - 使用一致间距比例，非任意值
- `visual-border-alpha-colors` - 半透明边框适应任何背景
- `visual-button-shadow-anatomy` - 六层阴影结构打造精致按钮

## 如何使用

阅读单个规则文件获取详细解释和代码示例：

```
rules/timing-under-300ms.md
rules/spring-for-gestures.md
rules/ux-doherty-under-400ms.md
rules/type-tabular-nums-for-data.md
```

每个规则文件包含：
- 规则重要性简述
- 错误代码示例及解释
- 正确代码示例及解释

## 完整编译文档

完整指南（所有规则展开）：`AGENTS.md`
