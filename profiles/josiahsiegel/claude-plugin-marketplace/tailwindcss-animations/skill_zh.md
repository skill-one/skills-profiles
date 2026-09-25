# Tailwind CSS 动画与过渡

## 内置动画

### 旋转

加载指示器的持续旋转：

```html
<svg class="animate-spin h-5 w-5 text-blue-500" viewBox="0 0 24 24">
  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
</svg>
```

### 脉冲

通知的雷达式脉冲效果：

```html
<span class="relative flex h-3 w-3">
  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-sky-400 opacity-75"></span>
  <span class="relative inline-flex rounded-full h-3 w-3 bg-sky-500"></span>
</span>
```

### 淡入淡出

骨架加载器的微妙淡入淡出效果：

```html
<div class="animate-pulse flex space-x-4">
  <div class="rounded-full bg-slate-200 h-10 w-10"></div>
  <div class="flex-1 space-y-2 py-1">
    <div class="h-2 bg-slate-200 rounded"></div>
    <div class="h-2 bg-slate-200 rounded w-5/6"></div>
  </div>
</div>
```

### 弹跳

吸引注意力的垂直弹跳效果：

```html
<svg class="animate-bounce w-6 h-6 text-blue-500" fill="none" viewBox="0 0 24 24">
  <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
</svg>
```

## 过渡效果

### 过渡属性

| 类名 | CSS属性 |
|-------|--------------|
| `transition-none` | 无 |
| `transition-all` | 所有属性 |
| `transition` | 常见属性 |
| `transition-colors` | 仅颜色 |
| `transition-opacity` | 仅透明度 |
| `transition-shadow` | 仅阴影 |
| `transition-transform` | 仅变换 |

### 过渡时长

| 类名 | 时长 |
|-------|----------|
| `duration-75` | 75ms |
| `duration-100` | 100ms |
| `duration-150` | 150ms |
| `duration-200` | 200ms |
| `duration-300` | 300ms |
| `duration-500` | 500ms |
| `duration-700` | 700ms |
| `duration-1000` | 1000ms |

### 过渡缓动函数

| 类名 | 缓动效果 |
|-------|--------|
| `ease-linear` | 线性 |
| `ease-in` | 加速 |
| `ease-out` | 减速 |
| `ease-in-out` | 先加速后减速 |

### 过渡延迟

| 类名 | 延迟 |
|-------|-------|
| `delay-75` | 75ms |
| `delay-100` | 100ms |
| `delay-150` | 150ms |
| `delay-200` | 200ms |
| `delay-300` | 300ms |
| `delay-500` | 500ms |

### 基本过渡示例

```html
<!-- 颜色过渡 -->
<button class="bg-blue-500 hover:bg-blue-700 transition-colors duration-200">
  悬停我
</button>

<!-- 悬停时缩放 -->
<div class="transform hover:scale-105 transition-transform duration-200">
  卡片
</div>

<!-- 透明度过渡 -->
<div class="opacity-100 hover:opacity-75 transition-opacity duration-150">
  淡入
</div>

<!-- 多个属性 -->
<button class="
  bg-blue-500 hover:bg-blue-700
  transform hover:scale-105
  shadow-md hover:shadow-lg
  transition-all duration-200
">
  完整过渡
</button>
```

## 变换工具

### 缩放

```html
<div class="transform scale-100 hover:scale-110 transition-transform">
  放大
</div>

<div class="transform scale-100 hover:scale-90 transition-transform">
  缩小
</div>

<!-- 指定轴 -->
<div class="transform hover:scale-x-110">水平</div>
<div class="transform hover:scale-y-110">垂直</div>
```

### 旋转

```html
<div class="transform hover:rotate-12 transition-transform">
  向右旋转
</div>

<div class="transform hover:-rotate-12 transition-transform">
  向左旋转
</div>

<div class="transform hover:rotate-180 transition-transform duration-500">
  翻转
</div>
```

### 平移

```html
<div class="transform hover:translate-x-2 transition-transform">
  向右移动
</div>

<div class="transform hover:-translate-y-2 transition-transform">
  向上移动
</div>
```

### 倾斜

```html
<div class="transform hover:skew-x-3 transition-transform">
  水平倾斜
</div>

<div class="transform hover:skew-y-3 transition-transform">
  垂直倾斜
</div>
```

### 变换原点

```html
<div class="origin-center transform hover:rotate-45">中心（默认）</div>
<div class="origin-top-left transform hover:rotate-45">左上角</div>
<div class="origin-bottom-right transform hover:rotate-45">右下角</div>
```

## 自定义动画（v4）

### 在@theme中定义

```css
@theme {
  /* 自定义关键帧 */
  --animate-fade-in: fade-in 0.5s ease-out;
  --animate-slide-up: slide-up 0.3s ease-out;
  --animate-shake: shake 0.5s ease-in-out;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}
```

### 使用

```html
<div class="animate-fade-in">淡入</div>
<div class="animate-slide-up">上滑</div>
<div class="animate-shake">错误时抖动</div>
```

### 自定义缓动函数

```css
@theme {
  --ease-in-expo: cubic-bezier(0.95, 0.05, 0.795, 0.035);
  --ease-out-expo: cubic-bezier(0.19, 1, 0.22, 1);
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
```

```html
<div class="transition-transform ease-bounce duration-300 hover:scale-110">
  弹性缩放
</div>
```

## 可访问性：减少动画

### motion-safe / motion-reduce

```html
<!-- 仅在用户不偏好动画时才动画 -->
<div class="motion-safe:animate-bounce motion-reduce:animate-none">
  尊重偏好
</div>

<!-- 替代方案：减少动画 -->
<button class="
  motion-safe:transition-all motion-safe:duration-200
  motion-reduce:transition-none
  hover:bg-blue-600
">
  可访问按钮
</button>
```

### 减少动画模式

```css
/* 全局应用 */
@media (prefers-reduced-motion: reduce) {
  *,
  ::before,
  ::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## 常见动画模式

### 悬停时卡片提升

```html
<div class="
  transform transition-all duration-200
  hover:-translate-y-1 hover:shadow-lg
  bg-white rounded-lg p-6 shadow
">
  卡片内容
</div>
```

### 按钮按压效果

```html
<button class="
  transform transition-transform duration-100
  active:scale-95
  bg-blue-500 text-white px-4 py-2 rounded
">
  点击我
</button>
```

### 加载点

```html
<div class="flex space-x-1">
  <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
  <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
  <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
</div>
```

### 滚动时淡入（需JS）

```html
<div class="opacity-0 translate-y-4 transition-all duration-500" data-animate>
  淡入内容
</div>
```

```javascript
// 使用Intersection Observer触发动画
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.remove('opacity-0', 'translate-y-4')
    }
  })
})

document.querySelectorAll('[data-animate]').forEach(el => observer.observe(el))
```

### 骨架加载器

```html
<div class="animate-pulse">
  <div class="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
  <div class="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
  <div class="h-4 bg-gray-200 rounded w-5/6"></div>
</div>
```

### 汉堡图标到X的动画

```html
<button class="group" aria-label="切换菜单">
  <span class="block w-6 h-0.5 bg-black transition-all duration-200 group-open:rotate-45 group-open:translate-y-1.5"></span>
  <span class="block w-6 h-0.5 bg-black mt-1 transition-opacity duration-200 group-open:opacity-0"></span>
  <span class="block w-6 h-0.5 bg-black mt-1 transition-all duration-200 group-open:-rotate-45 group-open:-translate-y-1.5"></span>
</button>
```

## 进入/离开时过渡（需JS）

对于复杂的进入/离开过渡，可以使用Headless UI等库：

```jsx
import { Transition } from '@headlessui/react'

function Modal({ isOpen, children }) {
  return (
    <Transition
      show={isOpen}
      enter="transition-opacity duration-300"
      enterFrom="opacity-0"
      enterTo="opacity-100"
      leave="transition-opacity duration-200"
      leaveFrom="opacity-100"
      leaveTo="opacity-0"
    >
      {children}
    </Transition>
  )
}
```

## 性能技巧

### 1. 优先使用GPU加速属性

```html
<!-- GOOD - GPU加速 -->
<div class="transform hover:translate-x-2 transition-transform">

<!-- AVOID - 可能导致重绘 -->
<div class="hover:left-2 transition-all">
```

### 2. 使用特定过渡

```html
<!-- GOOD - 仅过渡变化属性 -->
<div class="transition-colors duration-200 hover:bg-blue-500">

<!-- AVOID - 过渡所有属性 -->
<div class="transition-all duration-200 hover:bg-blue-500">
```

### 3. 保持动画简短

```html
<!-- GOOD - 快速反馈 -->
<button class="transition-colors duration-150">

<!-- AVOID - 过慢的UI反馈 -->
<button class="transition-colors duration-1000">
```

### 4. 适度使用will-change

```html
<!-- 仅用于复杂、频繁动画的元素 -->
<div class="will-change-transform animate-spin">
  加载动画
</div>
```
