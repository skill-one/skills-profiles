# 交互设计

通过运动、反馈和周到的状态转换，创造引人入胜、直观的交互，提升可用性并让用户感到愉悦。

## 何时使用此技能

- 添加微交互以增强用户反馈
- 实现平滑的页面和组件转换
- 设计加载状态和骨架屏
- 创建基于手势的交互
- 构建通知和吐司系统
- 实现拖放界面
- 添加滚动触发的动画
- 设计悬停和焦点状态

## 核心原则

### 1. 有目的的运动

运动应传达信息，而非仅用于装饰：

- **反馈**：确认用户操作已发生
- **方向**：显示元素来自何处或去向何方
- **焦点**：将注意力引导至重要变化
- **连续性**：在转换期间保持上下文

### 2. 时间规范

| 持续时间  | 用途                          |
| --------- | ----------------------------- |
| 100-150ms | 微反馈（悬停、点击）          |
| 200-300ms | 小型转换（切换、下拉菜单）    |
| 300-500ms | 中型转换（模态框、页面切换） |
| 500ms+    | 复杂的编排动画              |

### 3. 缓动函数

```css
/* 常用缓动函数 */
--ease-out: cubic-bezier(0.16, 1, 0.3, 1); /* 减速 - 进入时 */
--ease-in: cubic-bezier(0.55, 0, 1, 0.45); /* 加速 - 离开时 */
--ease-in-out: cubic-bezier(0.65, 0, 0.35, 1); /* 双向 - 移动时 */
--spring: cubic-bezier(0.34, 1.56, 0.64, 1); /* 超调 - 活泼效果 */
```

## 快速入门：按钮微交互

```tsx
import { motion } from "framer-motion";

export function InteractiveButton({ children, onClick }) {
  return (
    <motion.button
      onClick={onClick}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: "spring", stiffness: 400, damping: 17 }}
      className="px-4 py-2 bg-blue-600 text-white rounded-lg"
    >
      {children}
    </motion.button>
  );
}
```

## 交互模式

### 1. 加载状态

**骨架屏**：加载时保持布局

```tsx
function CardSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="h-48 bg-gray-200 rounded-lg" />
      <div className="mt-4 h-4 bg-gray-200 rounded w-3/4" />
      <div className="mt-2 h-4 bg-gray-200 rounded w-1/2" />
    </div>
  );
}
```

**进度指示器**：显示确定性的进度

```tsx
function ProgressBar({ progress }: { progress: number }) {
  return (
    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
      <motion.div
        className="h-full bg-blue-600"
        initial={{ width: 0 }}
        animate={{ width: `${progress}%` }}
        transition={{ ease: "easeOut" }}
      />
    </div>
  );
}
```

### 2. 状态转换

**带平滑转换的切换**：

```tsx
function Toggle({ checked, onChange }) {
  return (
    <button
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={`
        relative w-12 h-6 rounded-full transition-colors duration-200
        ${checked ? "bg-blue-600" : "bg-gray-300"}
      `}
    >
      <motion.span
        className="absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow"
        animate={{ x: checked ? 24 : 0 }}
        transition={{ type: "spring", stiffness: 500, damping: 30 }}
      />
    </button>
  );
}
```

### 3. 页面转换

**Framer Motion 布局动画**：

```tsx
import { AnimatePresence, motion } from "framer-motion";

function PageTransition({ children, key }) {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={key}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3 }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
```

### 4. 反馈模式

**点击时的涟漪效果**：

```tsx
function RippleButton({ children, onClick }) {
  const [ripples, setRipples] = useState([]);

  const handleClick = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const ripple = {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
      id: Date.now(),
    };
    setRipples((prev) => [...prev, ripple]);
    setTimeout(() => {
      setRipples((prev) => prev.filter((r) => r.id !== ripple.id));
    }, 600);
    onClick?.(e);
  };

  return (
    <button onClick={handleClick} className="relative overflow-hidden">
      {children}
      {ripples.map((ripple) => (
        <span
          key={ripple.id}
          className="absolute bg-white/30 rounded-full animate-ripple"
          style={{ left: ripple.x, top: ripple.y }}
        />
      ))}
    </button>
  );
}
```

### 5. 手势交互

**滑动关闭**：

```tsx
function SwipeCard({ children, onDismiss }) {
  return (
    <motion.div
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      onDragEnd={(_, info) => {
        if (Math.abs(info.offset.x) > 100) {
          onDismiss();
        }
      }}
      className="cursor-grab active:cursor-grabbing"
    >
      {children}
    </motion.div>
  );
}
```

## CSS 动画模式

### 关键帧动画

```css
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.3s ease-out;
}
.animate-pulse {
  animation: pulse 2s ease-in-out infinite;
}
.animate-spin {
  animation: spin 1s linear infinite;
}
```

### CSS 过渡

```css
.card {
  transition:
    transform 0.2s ease-out,
    box-shadow 0.2s ease-out;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}
```

## 可访问性考虑

```css
/* 尊重用户运动偏好 */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

```tsx
function AnimatedComponent() {
  const prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)",
  ).matches;

  return (
    <motion.div
      animate={{ opacity: 1 }}
      transition={{ duration: prefersReducedMotion ? 0 : 0.3 }}
    />
  );
}
```

## 最佳实践

1. **优先考虑性能**：使用 `transform` 和 `opacity` 实现流畅的 60fps
2. **减少运动支持**：始终尊重 `prefers-reduced-motion`
3. **一致的时间**：在应用中使用统一的时间尺度
4. **自然物理**：优先使用弹簧动画而非线性动画
5. **可中断**：允许用户取消长时间动画
6. **渐进增强**：无 JS 动画也能工作
7. **设备测试**：性能差异显著

## 常见问题

- **卡顿动画**：避免动画 `width`、`height`、`top`、`left`
- **过度动画**：过多运动会导致疲劳
- **阻塞交互**：动画期间绝不能阻止用户输入
- **内存泄漏**：卸载时清理动画监听器
- **闪烁内容**：谨慎使用 `will-change` 进行优化
