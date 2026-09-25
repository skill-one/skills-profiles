# Emil Kowalski 动画最佳实践

基于 Emil Kowalski 的教学、开源库（Sonner、Vaul）及其 [animations.dev](https://animations.dev) 课程，这是一份关于网页界面动画的全面指南。包含 8 个类别中的 58 条规则，按影响优先级排序。

## 何时应用

在以下情况下参考这些指南：
- 为 React 组件添加动画
- 选择缓动曲线或时间值
- 实现基于手势的交互（滑动、拖拽）
- 构建toast通知或抽屉组件
- 优化动画性能
- 确保动画的可访问性
- 使用 Tailwind CSS v4 工具类表达上述任何内容（参见 `tw-` 类别）

## 按优先级排序的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | 缓动曲线选择 | 关键 | `ease-` |
| 2 | 时间与持续时间 | 关键 | `timing-` |
| 3 | 属性选择 | 高 | `props-` |
| 4 | 变换技术 | 高 | `transform-` |
| 5 | 交互模式 | 中高 | `interact-` |
| 6 | 战略性动画 | 中 | `strategy-` |
| 7 | 可访问性与润色 | 中 | `polish-` |
| 8 | Tailwind v4 工具类 | 中 | `tw-` |

## 快速参考

### 1. 缓动曲线选择（关键）

- [`ease-out-default`](references/ease-out-default.md) - 将 ease-out 作为默认缓动曲线
- [`ease-custom-curves`](references/ease-custom-curves.md) - 使用自定义 cubic-bezier 覆盖内置CSS
- [`ease-in-out-onscreen`](references/ease-in-out-onscreen.md) - 在屏幕上移动时使用 ease-in-out
- [`ease-spring-natural`](references/ease-spring-natural.md) - 使用弹簧动画实现自然运动
- [`ease-spring-config`](references/ease-spring-config.md) - 使用持续时间和回弹配置弹簧
- [`ease-ios-drawer`](references/ease-ios-drawer.md) - 为抽屉组件使用iOS风格的缓动曲线
- [`ease-context-matters`](references/ease-context-matters.md) - 使缓动曲线与动画上下文匹配

### 2. 时间与持续时间（关键）

- [`timing-300ms-max`](references/timing-300ms-max.md) - 将UI动画保持在300ms以内
- [`timing-faster-better`](references/timing-faster-better.md) - 更快的动画提升感知性能
- [`timing-asymmetric`](references/timing-asymmetric.md) - 使用非对称时间处理按下和释放
- [`timing-tooltip-delay`](references/timing-tooltip-delay.md) - 延迟初始提示框，即时显示后续提示框
- [`timing-drawer-500ms`](references/timing-drawer-500ms.md) - 使用500ms持续时间为抽屉动画

### 3. 属性选择（高）

- [`props-transform-opacity`](references/props-transform-opacity.md) - 仅动画化 transform 和 opacity
- [`props-hardware-accelerated`](references/props-hardware-accelerated.md) - 当主线程繁忙时使用硬件加速动画
- [`props-will-change`](references/props-will-change.md) - 使用 will-change 防止1px偏移
- [`props-avoid-css-variables`](references/props-avoid-css-variables.md) - 避免使用CSS变量进行拖拽动画
- [`props-clip-path-performant`](references/props-clip-path-performant.md) - 使用 clip-path 实现无布局的显示效果

### 4. 变换技术（高）

- [`transform-scale-097`](references/transform-scale-097.md) - 按下时将按钮缩放到0.97
- [`transform-never-scale-zero`](references/transform-never-scale-zero.md) - 从 scale(0) 开始动画
- [`transform-percentage-translate`](references/transform-percentage-translate.md) - 使用百分比值进行 translateY
- [`transform-origin-aware`](references/transform-origin-aware.md) - 使动画与原点相关
- [`transform-scale-children`](references/transform-scale-children.md) - 缩放变换影响子元素
- [`transform-3d-preserve`](references/transform-3d-preserve.md) - 使用 preserve-3d 实现三维变换效果
- [`transform-starting-style`](references/transform-starting-style.md) - 使用 @starting-style 动画化进入状态

### 5. 交互模式（中高）

- [`interact-interruptible`](references/interact-interruptible.md) - 使动画可中断
- [`interact-momentum-dismiss`](references/interact-momentum-dismiss.md) - 使用基于动量的关闭
- [`interact-damping`](references/interact-damping.md) - 在边界处阻尼拖拽
- [`interact-scroll-drag-conflict`](references/interact-scroll-drag-conflict.md) - 解决滚动和拖拽冲突
- [`interact-snap-points`](references/interact-snap-points.md) - 实现基于速度的快进点
- [`interact-friction-upward`](references/interact-friction-upward.md) - 允许带摩擦的向上拖拽
- [`interact-pointer-capture`](references/interact-pointer-capture.md) - 使用指针捕获进行拖拽操作
- [`interact-multitouch`](references/interact-multitouch.md) - 拖拽时忽略额外的触摸点
- [`interact-touch-hover`](references/interact-touch-hover.md) - 在指针媒体查询后触发悬停动画

### 6. 战略性动画（中）

- [`strategy-keyboard-no-animate`](references/strategy-keyboard-no-animate.md) - 永不动画化键盘触发的操作
- [`strategy-frequency-matters`](references/strategy-frequency-matters.md) - 在动画前考虑交互频率
- [`strategy-purpose-required`](references/strategy-purpose-required.md) - 每个动画必须有目的
- [`strategy-feedback-immediate`](references/strategy-feedback-immediate.md) - 对所有操作提供即时反馈
- [`strategy-marketing-exception`](references/strategy-marketing-exception.md) - 营销网站是例外
- [`strategy-cohesion`](references/strategy-cohesion.md) - 使运动与组件的个性匹配
- [`strategy-review-fresh-eyes`](references/strategy-review-fresh-eyes.md) - 慢动作和第二天重新审查动画

### 7. 可访问性与润色（中）

- [`polish-reduced-motion`](references/polish-reduced-motion.md) - 尊重 prefers-reduced-motion
- [`polish-opacity-fallback`](references/polish-opacity-fallback.md) - 使用透明度作为减少运动的回退
- [`polish-framer-hook`](references/polish-framer-hook.md) - 在 Framer Motion 中使用 useReducedMotion 钩子
- [`polish-dont-remove-all`](references/polish-dont-remove-all.md) - 为减少运动保留轻柔动画
- [`polish-blur-bridge`](references/polish-blur-bridge.md) - 使用模糊桥接动画状态
- [`polish-clip-path-tabs`](references/polish-clip-path-tabs.md) - 使用 clip-path 实现标签过渡
- [`polish-toast-stacking`](references/polish-toast-stacking.md) - 使用缩放和偏移实现toast堆叠
- [`polish-scroll-reveal`](references/polish-scroll-reveal.md) - 在适当的阈值触发滚动动画
- [`polish-hover-gap-fill`](references/polish-hover-gap-fill.md) - 填充可交互元素之间的间隙
- [`polish-stagger-children`](references/polish-stagger-children.md) - 为编排 stagger 子元素动画

### 8. Tailwind v4 工具类（中）

使用正确的 Tailwind CSS v4 工具类表达上述原则。仅适用于 Tailwind v4 项目；上述原始CSS和 Framer Motion 规则仍然是权威来源。

- [`tw-ease-duration-defaults`](references/tw-ease-duration-defaults.md) - 明确设置 ease-out 和小于300ms的持续时间
- [`tw-custom-easing-theme`](references/tw-custom-easing-theme.md) - 将自定义缓动曲线注册为 @theme 令牌
- [`tw-press-scale`](references/tw-press-scale.md) - 使用 active:scale-[0.97] 实现按钮按下反馈
- [`tw-asymmetric-timing`](references/tw-asymmetric-timing.md) - 使用 active:duration 分隔按下和释放时间
- [`tw-starting-enter`](references/tw-starting-enter.md) - 使用 starting: 变体动画化进入状态
- [`tw-reduced-motion`](references/tw-reduced-motion.md) - 在 motion-safe / motion-reduce 后触发移动
- [`tw-origin-aware`](references/tw-origin-aware.md) - 使用 origin-* 工具类设置 transform-origin
- [`tw-will-change`](references/tw-will-change.md) - 将 will-change-transform 作用在活跃手势上

## 关键值参考

| 值 | 用法 |
|------|------|
| `cubic-bezier(0.23, 1, 0.32, 1)` | UI交互的强 ease-out |
| `cubic-bezier(0.77, 0, 0.175, 1)` | 屏幕上移动的强 ease-in-out |
| `cubic-bezier(0.32, 0.72, 0, 1)` | iOS风格的抽屉/面板动画 |
| `scale(0.97)` | 按钮按下反馈 |
| `scale(0.95)` | 最小进入缩放（永不 scale(0)） |
| `200ms ease-out` | 标准UI过渡 |
| `300ms` | UI动画的最大持续时间 |
| `500ms` | 抽屉动画持续时间 |
| `0.11 px/ms` | 动量关闭的速度阈值 |
| `100px` | 滚动揭示的视口阈值 |
| `14px` | Toast堆叠偏移 |

## 元素持续时间

根据元素可见频率和移动量选择持续时间。保持UI动画在300ms以内。

| 元素 | 持续时间 |
|------|------|
| 按钮按下反馈 | 100–160ms |
| 提示框、小型弹出框 | 125–200ms |
| 下拉框、选择框 | 150–250ms |
| 模态框、抽屉 | 200–500ms |
| 营销/解释性 | 可以更长 |

## 参考文件

| 文件 | 描述 |
|------|------|
| [references/_sections.md](references/_sections.md) | 类别定义和排序 |
| [assets/templates/_template.md](assets/templates/_template.md) | 新规则的模板 |
| [metadata.json](metadata.json) | 版本和参考信息 |
