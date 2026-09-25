# Next.js 动画

## 概述

本指南提供了在 Next.js 和 React 应用中实现流畅、高性能和可访问动画的全面指导。它涵盖了 CSS 动画、Framer Motion、缓动原理和可访问性考虑因素。

## 快速参考

### 缓动速查表

| 动画类型 | 缓动 | 持续时间 |
|----------|------|----------|
| 元素进入 | `ease-out` | 200-300ms |
| 元素在屏幕上移动 | `ease-in-out` | 200-300ms |
| 元素退出 | `ease-in` | 150-200ms |
| 悬停效果 | `ease` | 150ms |
| 仅透明度 | `linear` | 变化 |

### CSS 自定义属性（推荐）

```css
:root {
  --ease-out-quint: cubic-bezier(.23, 1, .32, 1);
  --ease-in-out-cubic: cubic-bezier(.645, .045, .355, 1);
  --ease-out-cubic: cubic-bezier(.33, 1, .68, 1);
}
```

## 常见动画模式

### 1. 悬停提升效果

```css
.card {
  transition: transform 200ms var(--ease-out-quint),
              box-shadow 200ms var(--ease-out-quint);
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}
```

### 2. 按钮按压

```css
.button {
  transition: transform 100ms ease-out;
}
.button:active {
  transform: scale(0.97);
}
```

### 3. 挂载时淡入（Framer Motion）

```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3, ease: [.23, 1, .32, 1] }}
>
  内容
</motion.div>
```

### 4. 带退出动画的模态框

```tsx
<AnimatePresence>
  {isOpen && (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.2, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  )}
</AnimatePresence>
```

### 5. 选项卡指示器（共享布局）

```tsx
{tabs.map(tab => (
  <button key={tab} onClick={() => setActive(tab)} className="relative px-4 py-2">
    {tab}
    {active === tab && (
      <motion.div
        layoutId="tab-indicator"
        className="absolute inset-0 bg-blue-500 rounded -z-10"
        transition={{ type: "spring", stiffness: 400, damping: 30 }}
      />
    )}
  </button>
))}
```

### 6. 交错列表动画

```tsx
const container = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
}

const item = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
}

<motion.ul variants={container} initial="hidden" animate="visible">
  {items.map(i => <motion.li key={i} variants={item}>{i}</motion.li>)}
</motion.ul>
```

## 黄金法则

1. **退出比进入更快**：退出动画应为进入持续时间的约 75%
2. **仅动画变换和透明度**：这些是 GPU 加速的
3. **200-300ms 是最佳范围**：大多数动画应在此范围内
4. **始终尊重 prefers-reduced-motion**：参见参考资料中的可访问性部分
5. **使用弹簧进行可中断动画**：用户中断时体验更好

## 示例

课程中的完整工作示例位于 `examples/` 目录：

| 示例 | 描述 | 关键技术 |
|------|------|----------|
| `card-hover.tsx` | 悬停时的上滑描述 | CSS 过渡、变换、透明度 |
| `toast-stacking.tsx` | 动画提示通知 | CSS 自定义属性、data-* 触发 |
| `text-reveal.tsx` | 交错字母动画 | @keyframes、animation-delay、calc() |
| `shared-layout.tsx` | 元素位置/大小变形 | Framer Motion layoutId |
| `animate-height.tsx` | 平滑高度变化 | useMeasure、animate height |
| `multi-step-flow.tsx` | 方向性步骤向导 | AnimatePresence、自定义变体 |
| `feedback-popover.tsx` | 按钮到弹出框扩展 | 嵌套 layoutId、表单状态 |
| `app-store-card.tsx` | iOS 风格卡片扩展 | 多个 layoutId 元素 |

要使用示例，请阅读：`Read examples/<name>.tsx`

## 参考资料

有关详细文档，请阅读参考文件：

- `references/easing-and-timing.md` - 缓动函数、时间指南、弹簧配置
- `references/css-animations.md` - 变换、过渡、关键帧、clip-path
- `references/framer-motion.md` - Motion 组件、AnimatePresence、变体、布局动画、钩子
- `references/performance-accessibility.md` - 60fps 优化、prefers-reduced-motion、可访问性

## 何时使用什么

| 场景 | 推荐方法 |
|------|----------|
| 简单悬停效果 | CSS 过渡 |
| 进入/退出动画 | Framer Motion + AnimatePresence |
| 布局变化 | Framer Motion `layout` 属性 |
| 共享元素过渡 | Framer Motion `layoutId` |
| 滚动关联动画 | Framer Motion `useScroll` |
| 复杂编排动画 | Framer Motion 变体 |
| 拖拽交互 | Framer Motion 拖拽手势 |
| 性能关键 | CSS-仅变换 |

## 依赖项

对于 Framer Motion 示例，请安装：
```bash
pnpm add framer-motion react-use-measure usehooks-ts
```
