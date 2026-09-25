# 动画设计师技能

我使用 Framer Motion 和 CSS 帮您为 Web 应用创建流畅、专业的动画。

## 我能做什么

**UI 动画：**

- 页面过渡
- 组件进入/退出动画
- 悬停效果、按钮交互
- 加载动画

**滚动动画：**

- 视差效果
- 滚动触发动画
- 进度指示器

**微交互：**

- 按钮按压反馈
- 表单字段焦点状态
- 成功/错误动画
- 拖放反馈

## Framer Motion 基础

### 安装

```bash
npm install framer-motion
```

### 基本动画

```typescript
import { motion } from 'framer-motion'

export function FadeIn({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {children}
    </motion.div>
  )
}
```

---

## 常见动画模式

### 模式 1：挂载时淡入

```typescript
import { motion } from 'framer-motion'

export function Card({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="p-6 bg-white rounded-lg shadow"
    >
      {children}
    </motion.div>
  )
}
```

---

### 模式 2：交错列表动画

```typescript
import { motion } from 'framer-motion'

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
}

export function List({ items }: { items: string[] }) {
  return (
    <motion.ul
      variants={container}
      initial="hidden"
      animate="show"
    >
      {items.map((text, i) => (
        <motion.li key={i} variants={item}>
          {text}
        </motion.li>
      ))}
    </motion.ul>
  )
}
```

---

### 模式 3：按钮悬停动画

```typescript
import { motion } from 'framer-motion'

export function AnimatedButton({ children, onClick }: {
  children: React.ReactNode
  onClick: () => void
}) {
  return (
    <motion.button
      onClick={onClick}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      transition={{ type: 'spring', stiffness: 400, damping: 17 }}
      className="px-6 py-3 bg-blue-600 text-white rounded-lg"
    >
      {children}
    </motion.button>
  )
}
```

---

### 模式 4：模态框/对话框动画

```typescript
import { motion, AnimatePresence } from 'framer-motion'

export function Modal({ isOpen, onClose, children }: {
  isOpen: boolean
  onClose: () => void
  children: React.ReactNode
}) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* 背景遮罩 */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 z-40"
          />

          {/* 模态框 */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="fixed inset-0 flex items-center justify-center z-50 p-4"
          >
            <div className="bg-white rounded-lg p-6 max-w-md w-full">
              {children}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
```

---

### 模式 5：页面过渡

```typescript
'use client'
import { motion } from 'framer-motion'
import { usePathname } from 'next/navigation'

export function PageTransition({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  return (
    <motion.div
      key={pathname}
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ duration: 0.3 }}
    >
      {children}
    </motion.div>
  )
}

// 在布局中使用
export default function Layout({ children }) {
  return (
    <PageTransition>
      {children}
    </PageTransition>
  )
}
```

---

## 滚动动画

### 滚动触发动画

```typescript
import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'

export function ScrollReveal({ children }: { children: React.ReactNode }) {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start end', 'end start']
  })

  const opacity = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0, 1, 1, 0])
  const y = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [100, 0, 0, -100])

  return (
    <motion.div
      ref={ref}
      style={{ opacity, y }}
    >
      {children}
    </motion.div>
  )
}
```

### 视差效果

```typescript
import { motion, useScroll, useTransform } from 'framer-motion'

export function ParallaxSection() {
  const { scrollY } = useScroll()
  const y = useTransform(scrollY, [0, 500], [0, 150])

  return (
    <div className="relative h-screen overflow-hidden">
      <motion.div
        style={{ y }}
        className="absolute inset-0"
      >
        <img src="/background.jpg" alt="" className="w-full h-full object-cover" />
      </motion.div>

      <div className="relative z-10 flex items-center justify-center h-full">
        <h1 className="text-6xl font-bold text-white">
          视差效果
        </h1>
      </div>
    </div>
  )
}
```

### 滚动进度指示器

```typescript
import { motion, useScroll } from 'framer-motion'

export function ScrollProgress() {
  const { scrollYProgress } = useScroll()

  return (
    <motion.div
      style={{ scaleX: scrollYProgress }}
      className="fixed top-0 left-0 right-0 h-1 bg-blue-600 origin-left z-50"
    />
  )
}
```

---

## 加载动画

### 旋转加载器

```typescript
import { motion } from 'framer-motion'

export function Spinner() {
  return (
    <motion.div
      animate={{ rotate: 360 }}
      transition={{
        duration: 1,
        repeat: Infinity,
        ease: 'linear'
      }}
      className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full"
    />
  )
}
```

### 骨架加载器

```typescript
import { motion } from 'framer-motion'

export function SkeletonLoader() {
  return (
    <motion.div
      animate={{ opacity: [0.5, 1, 0.5] }}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: 'easeInOut'
      }}
      className="bg-gray-200 rounded h-4 w-full"
    />
  )
}
```

### 脉冲点

```typescript
import { motion } from 'framer-motion'

const dotVariants = {
  start: { scale: 0.8, opacity: 0.5 },
  end: { scale: 1.2, opacity: 1 }
}

export function PulsingDots() {
  return (
    <div className="flex gap-2">
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          variants={dotVariants}
          animate="end"
          initial="start"
          transition={{
            duration: 0.6,
            repeat: Infinity,
            repeatType: 'reverse',
            delay: i * 0.2
          }}
          className="w-3 h-3 bg-blue-600 rounded-full"
        />
      ))}
    </div>
  )
}
```

---

## CSS 动画

### 关键帧动画

```css
/* 淡入动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn 0.5s ease-out;
}

/* 从右侧滑入 */
@keyframes slideInRight {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}

.slide-in-right {
  animation: slideInRight 0.3s ease-out;
}

/* 弹跳 */
@keyframes bounce {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.bounce {
  animation: bounce 0.5s ease-in-out infinite;
}
```

### Tailwind 动画

```typescript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        },
        'slide-in': {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(0)' }
        }
      },
      animation: {
        'fade-in': 'fade-in 0.5s ease-out',
        'slide-in': 'slide-in 0.3s ease-out'
      }
    }
  }
}
```

**使用：**

```typescript
<div className="animate-fade-in">淡入</div>
<div className="animate-slide-in">滑入</div>
```

---

## 微交互

### 成功对勾动画

```typescript
import { motion } from 'framer-motion'

export function SuccessCheckmark() {
  return (
    <motion.svg
      width="48"
      height="48"
      viewBox="0 0 48 48"
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
    >
      <motion.circle
        cx="24"
        cy="24"
        r="22"
        fill="none"
        stroke="#10B981"
        strokeWidth="4"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.5 }}
      />
      <motion.path
        d="M12 24 L20 32 L36 16"
        fill="none"
        stroke="#10B981"
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.3, delay: 0.3 }}
      />
    </motion.svg>
  )
}
```

### 通知徽章

```typescript
import { motion } from 'framer-motion'

export function NotificationBadge({ count }: { count: number }) {
  return (
    <div className="relative">
      <button className="p-2">
        <BellIcon />
      </button>

      {count > 0 && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 500, damping: 15 }}
          className="absolute -top-1 -right-1 bg-red-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center"
        >
          {count}
        </motion.div>
      )}
    </div>
  )
}
```

---

## 动画最佳实践

### 1. 性能

```typescript
// ✅ 好：动画 transform 和 opacity（GPU 加速）
<motion.div
  animate={{ x: 100, opacity: 0.5 }}
/>

// ❌ 不好：动画 width、height（触发布局）
<motion.div
  animate={{ width: '100%', height: '200px' }}
/>
```

### 2. 持续时间

```typescript
// 太快：< 100ms（感觉突兀）
// 太慢：> 500ms（感觉迟缓）

// ✅ 甜点范围：200-400ms 大多数 UI 动画
<motion.div
  animate={{ opacity: 1 }}
  transition={{ duration: 0.3 }}
/>
```

### 3. 缓动

```typescript
// 自然运动：easeOut（开始快，结束慢）
<motion.div
  animate={{ y: 0 }}
  transition={{ ease: 'easeOut' }}
/>

// 弹性：spring
<motion.button
  whileTap={{ scale: 0.95 }}
  transition={{ type: 'spring', stiffness: 400 }}
/>
```

### 4. 减少运动（无障碍）

```typescript
import { useReducedMotion } from 'framer-motion'

export function AccessibleAnimation({ children }: { children: React.ReactNode }) {
  const shouldReduceMotion = useReducedMotion()

  return (
    <motion.div
      initial={{ opacity: 0, y: shouldReduceMotion ? 0 : 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: shouldReduceMotion ? 0 : 0.4
      }}
    >
      {children}
    </motion.div>
  )
}
```

---

## 复杂动画

### 拖放

```typescript
import { motion } from 'framer-motion'
import { useState } from 'react'

export function Draggable() {
  const [position, setPosition] = useState({ x: 0, y: 0 })

  return (
    <motion.div
      drag
      dragConstraints={{ left: 0, right: 300, top: 0, bottom: 300 }}
      dragElastic={0.1}
      onDragEnd={(e, info) => {
        setPosition({ x: info.point.x, y: info.point.y })
      }}
      className="w-24 h-24 bg-blue-600 rounded-lg cursor-grab active:cursor-grabbing"
    />
  )
}
```

### 动画数字计数器

```typescript
import { motion, useSpring, useTransform } from 'framer-motion'
import { useEffect } from 'react'

export function AnimatedNumber({ value }: { value: number }) {
  const spring = useSpring(0, { stiffness: 100, damping: 30 })
  const display = useTransform(spring, (current) =>
    Math.round(current).toLocaleString()
  )

  useEffect(() => {
    spring.set(value)
  }, [spring, value])

  return <motion.span>{display}</motion.span>
}

// 使用
<AnimatedNumber value={1250} />
```

---

## 何时使用我

**非常适合：**

- 创建精致的 UI 动画
- 构建交互式组件
- 添加滚动效果
- 设计加载状态
- 改善用户反馈

**我会帮助您：**

- 选择正确的动画类型
- 实现平滑过渡
- 优化动画性能
- 确保无障碍
- 创建令人愉悦的微交互

## 我会创建

```
✨ 页面过渡
🎯 微交互
📜 滚动动画
⏳ 加载状态
🎨 悬停效果
🎪 复杂动画
```

让我们让您的界面充满活力！
