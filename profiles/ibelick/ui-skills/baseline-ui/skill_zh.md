# 基线 UI

强制执行一个有争议的 UI 基线，以防止 AI 生成的界面混乱。

## 如何使用

- `/baseline-ui`
  将这些约束应用于此对话中的任何 UI 工作。

- `/baseline-ui <文件>`
  根据以下所有约束审查文件并输出：
  - 违规（引用确切的行/片段）
  - 为什么要这样做（一句话）
  - 具体的修复方案（代码级别的建议）

## 技术栈

- 必须使用 Tailwind CSS 默认值，除非已有自定义值或明确要求
- 必须在需要 JavaScript 动画时使用 `motion/react`（以前称为 `framer-motion`）
- 应该在 Tailwind CSS 中使用 `tw-animate-css` 进行入场动画和微动画
- 必须使用 `cn` 工具（`clsx` + `tailwind-merge`）进行类逻辑

## 组件

- 必须使用可访问的组件原语处理任何具有键盘或焦点行为的元素（`Base UI`，`React Aria`，`Radix`）
- 必须首先使用项目现有的组件原语
- 绝不能在同一交互表面上混合原语系统
- 应该优先使用 [`Base UI`](https://base-ui.com/react/components) 作为新的原语，如果与技术栈兼容
- 必须为仅包含图标的按钮添加 `aria-label`
- 绝不能手动重建键盘或焦点行为，除非明确要求

## 交互

- 必须使用 `AlertDialog` 处理破坏性或不可逆的操作
- 应该使用结构骨架表示加载状态
- 绝不能使用 `h-screen`，应该使用 `h-dvh`
- 必须尊重 `safe-area-inset` 用于固定元素
- 必须在操作发生的位置显示错误
- 绝不能在 `input` 或 `textarea` 元素中阻止粘贴

## 动画

- 绝不能添加动画，除非明确要求
- 必须仅对合成器属性（`transform`，`opacity`）进行动画
- 绝不能对布局属性（`width`，`height`，`top`，`left`，`margin`，`padding`）进行动画
- 应该避免对绘制属性（`background`，`color`）进行动画，除非是小范围的局部 UI（文本、图标）
- 应该在入场时使用 `ease-out`
- 绝不能超过 `200ms` 的交互反馈时间
- 必须在元素离开屏幕时暂停循环动画
- 应该尊重 `prefers-reduced-motion`
- 绝不能引入自定义缓动曲线，除非明确要求
- 应该避免对大图像或全屏表面进行动画

## 字体

- 必须为标题使用 `text-balance`，为正文/段落使用 `text-pretty`
- 必须为数据使用 `tabular-nums`
- 应该在密集 UI 中使用 `truncate` 或 `line-clamp`
- 绝不能修改 `letter-spacing`（`tracking-*`），除非明确要求

## 布局

- 必须使用固定的 `z-index` 尺度（不要使用任意的 `z-*`）
- 应该使用 `size-*` 表示方形元素，而不是 `w-*` + `h-*`

## 性能

- 绝不能对大 `blur()` 或 `backdrop-filter` 表面进行动画
- 绝不能在活动动画之外应用 `will-change`
- 绝不能使用 `useEffect` 处理任何可以表示为渲染逻辑的内容

## 设计

- 绝不能使用渐变，除非明确要求
- 绝不能使用紫色或多色渐变
- 绝不能将辉光效果作为主要可供性
- 应该使用 Tailwind CSS 默认的阴影尺度，除非明确要求
- 必须为空状态提供一个明确的下一步操作
- 应该将强调色使用限制为每个视图一个
- 应该在使用现有主题或 Tailwind CSS 颜色标记之前引入新的颜色
