# Framer Motion 动画师

使用 Framer Motion 声明式 API 创建令人愉悦的动画和交互。

## 核心工作流程

1. **识别动画需求**：入场、退出、悬停、手势
2. **选择动画类型**：简单、变体、手势、布局
3. **定义运动值**：不透明度、缩放、位置、旋转
4. **添加过渡效果**：持续时间、缓动、弹簧物理效果
5. **编排序列**：错开、延迟、父子关系
6. **优化性能**：GPU 加速属性

## 安装

```bash
npm install framer-motion
```

## 基础动画

### 简单动画

```tsx
import { motion } from 'framer-motion';

// 入场动画
export function FadeIn({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {children}
    </motion.div>
  );
}

// 悬停动画
export function ScaleOnHover({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      transition={{ type: 'spring', stiffness: 400, damping: 17 }}
    >
      {children}
    </motion.div>
  );
}
```

### 使用 AnimatePresence 的退出动画

```tsx
import { motion, AnimatePresence } from 'framer-motion';

export function Modal({ isOpen, onClose, children }: ModalProps) {
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

          {/* 弹窗 */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="fixed inset-0 z-50 flex items-center justify-center"
          >
            <div className="bg-white rounded-xl p-6 max-w-md w-full">
              {children}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
```

## 变体模式

### 错开子元素

```tsx
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { type: 'spring', stiffness: 300, damping: 24 },
  },
};

export function StaggeredList({ items }: { items: string[] }) {
  return (
    <motion.ul
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {items.map((item, index) => (
        <motion.li key={index} variants={itemVariants}>
          {item}
        </motion.li>
      ))}
    </motion.ul>
  );
}
```

### 交互式变体

```tsx
const buttonVariants = {
  initial: { scale: 1 },
  hover: { scale: 1.05 },
  tap: { scale: 0.95 },
  disabled: { opacity: 0.5, scale: 1 },
};

export function AnimatedButton({
  children,
  disabled,
  onClick,
}: ButtonProps) {
  return (
    <motion.button
      variants={buttonVariants}
      initial="initial"
      whileHover={disabled ? 'disabled' : 'hover'}
      whileTap={disabled ? 'disabled' : 'tap'}
      animate={disabled ? 'disabled' : 'initial'}
      onClick={onClick}
      disabled={disabled}
      className="px-4 py-2 bg-blue-500 text-white rounded-lg"
    >
      {children}
    </motion.button>
  );
}
```

## 页面过渡

### Next.js 应用路由

```tsx
// app/template.tsx
'use client';

import { motion } from 'framer-motion';

export default function Template({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 20 }}
      transition={{ duration: 0.3 }}
    >
      {children}
    </motion.div>
  );
}
```

### 共享布局动画

```tsx
import { motion, LayoutGroup } from 'framer-motion';

export function Tabs({ tabs, activeTab, onTabChange }: TabsProps) {
  return (
    <LayoutGroup>
      <div className="flex gap-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className="relative px-4 py-2"
          >
            {activeTab === tab.id && (
              <motion.div
                layoutId="activeTab"
                className="absolute inset-0 bg-blue-500 rounded-lg"
                transition={{ type: 'spring', stiffness: 500, damping: 30 }}
              />
            )}
            <span className="relative z-10">{tab.label}</span>
          </button>
        ))}
      </div>
    </LayoutGroup>
  );
}
```

## 手势动画

### 拖拽

```tsx
export function DraggableCard() {
  return (
    <motion.div
      drag
      dragConstraints={{ left: -100, right: 100, top: -100, bottom: 100 }}
      dragElastic={0.2}
      dragTransition={{ bounceStiffness: 600, bounceDamping: 20 }}
      whileDrag={{ scale: 1.1, cursor: 'grabbing' }}
      className="w-32 h-32 bg-blue-500 rounded-lg cursor-grab"
    />
  );
}
```

### 滑动删除

```tsx
export function SwipeToDelete({ onDelete, children }: SwipeProps) {
  return (
    <motion.div
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      onDragEnd={(_, info) => {
        if (info.offset.x < -100) {
          onDelete();
        }
      }}
      className="relative"
    >
      {children}
      <motion.div
        className="absolute right-0 inset-y-0 bg-red-500 flex items-center px-4"
        style={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        删除
      </motion.div>
    </motion.div>
  );
}
```

## 滚动动画

### 滚动触发

```tsx
import { motion, useInView } from 'framer-motion';
import { useRef } from 'react';

export function FadeInWhenVisible({ children }: { children: React.ReactNode }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 50 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
    >
      {children}
    </motion.div>
  );
}
```

### 滚动进度

```tsx
import { motion, useScroll, useTransform } from 'framer-motion';

export function ParallaxHero() {
  const { scrollY } = useScroll();
  const y = useTransform(scrollY, [0, 500], [0, 150]);
  const opacity = useTransform(scrollY, [0, 300], [1, 0]);

  return (
    <motion.div
      style={{ y, opacity }}
      className="h-screen flex items-center justify-center"
    >
      <h1 className="text-6xl font-bold">视差英雄</h1>
    </motion.div>
  );
}

export function ScrollProgress() {
  const { scrollYProgress } = useScroll();

  return (
    <motion.div
      style={{ scaleX: scrollYProgress }}
      className="fixed top-0 left-0 right-0 h-1 bg-blue-500 origin-left z-50"
    />
  );
}
```

## 动画钩子

### useAnimate (命令式)

```tsx
import { useAnimate } from 'framer-motion';

export function SubmitButton() {
  const [scope, animate] = useAnimate();

  const handleClick = async () => {
    // 动画序列
    await animate(scope.current, { scale: 0.95 }, { duration: 0.1 });
    await animate(scope.current, { scale: 1 }, { type: 'spring' });

    // 成功动画
    await animate(
      scope.current,
      { backgroundColor: '#22c55e' },
      { duration: 0.2 }
    );
  };

  return (
    <motion.button ref={scope} onClick={handleClick} className="px-4 py-2">
      提交
    </motion.button>
  );
}
```

### useMotionValue & useTransform

```tsx
import { motion, useMotionValue, useTransform } from 'framer-motion';

export function RotatingCard() {
  const x = useMotionValue(0);
  const rotateY = useTransform(x, [-200, 200], [-45, 45]);
  const opacity = useTransform(x, [-200, 0, 200], [0.5, 1, 0.5]);

  return (
    <motion.div
      drag="x"
      dragConstraints={{ left: -200, right: 200 }}
      style={{ x, rotateY, opacity }}
      className="w-64 h-96 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl"
    />
  );
}
```

## 可重用动画组件

### AnimatedContainer

```tsx
// components/AnimatedContainer.tsx
import { motion, Variants } from 'framer-motion';

const animations: Record<string, Variants> = {
  fadeIn: {
    hidden: { opacity: 0 },
    visible: { opacity: 1 },
  },
  fadeInUp: {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  },
  fadeInDown: {
    hidden: { opacity: 0, y: -20 },
    visible: { opacity: 1, y: 0 },
  },
  scaleIn: {
    hidden: { opacity: 0, scale: 0.8 },
    visible: { opacity: 1, scale: 1 },
  },
  slideInLeft: {
    hidden: { opacity: 0, x: -50 },
    visible: { opacity: 1, x: 0 },
  },
  slideInRight: {
    hidden: { opacity: 0, x: 50 },
    visible: { opacity: 1, x: 0 },
  },
};

interface AnimatedContainerProps {
  children: React.ReactNode;
  animation?: keyof typeof animations;
  delay?: number;
  duration?: number;
  className?: string;
}

export function AnimatedContainer({
  children,
  animation = 'fadeInUp',
  delay = 0,
  duration = 0.5,
  className,
}: AnimatedContainerProps) {
  return (
    <motion.div
      variants={animations[animation]}
      initial="hidden"
      animate="visible"
      transition={{ duration, delay, ease: 'easeOut' }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
```

### AnimatedList

```tsx
// components/AnimatedList.tsx
import { motion } from 'framer-motion';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, x: -20 },
  visible: { opacity: 1, x: 0 },
};

interface AnimatedListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  keyExtractor: (item: T, index: number) => string;
  className?: string;
}

export function AnimatedList<T>({
  items,
  renderItem,
  keyExtractor,
  className,
}: AnimatedListProps<T>) {
  return (
    <motion.ul
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className={className}
    >
      {items.map((item, index) => (
        <motion.li key={keyExtractor(item, index)} variants={itemVariants}>
          {renderItem(item, index)}
        </motion.li>
      ))}
    </motion.ul>
  );
}
```

## 过渡预设

```tsx
// lib/transitions.ts
export const transitions = {
  spring: {
    type: 'spring',
    stiffness: 300,
    damping: 24,
  },
  springBouncy: {
    type: 'spring',
    stiffness: 500,
    damping: 15,
  },
  springStiff: {
    type: 'spring',
    stiffness: 700,
    damping: 30,
  },
  smooth: {
    type: 'tween',
    duration: 0.3,
    ease: 'easeInOut',
  },
  snappy: {
    type: 'tween',
    duration: 0.15,
    ease: [0.25, 0.1, 0.25, 1],
  },
} as const;

// 使用示例
<motion.div transition={transitions.spring} />
```

## 减少运动支持

```tsx
import { useReducedMotion } from 'framer-motion';

export function AccessibleAnimation({ children }: { children: React.ReactNode }) {
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.div
      initial={{ opacity: 0, y: shouldReduceMotion ? 0 : 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: shouldReduceMotion ? 0 : 0.5 }}
    >
      {children}
    </motion.div>
  );
}
```

## 最佳实践

1. **使用 GPU 加速属性**：`opacity`、`transform`（不是 `width`、`height`）
2. **添加 `layout` 实现平滑缩放**：自动布局动画
3. **使用 `AnimatePresence`**：用于退出动画
4. **优先使用弹簧**：比补间更自然
5. **尊重减少运动**：使用 `useReducedMotion` 钩子
6. **避免布局抖动动画**：不要动画化 `top`、`left`、`width`
7. **使用 `layoutId`**：用于共享元素过渡
8. **错开子元素**：用于列表动画

## 输出清单

每个动画实现应包含：

- [ ] 合适的动画类型（简单、变体、手势）
- [ ] 平滑过渡和适当的缓动
- [ ] 使用 AnimatePresence 的退出动画
- [ ] 减少运动支持
- [ ] 仅使用 GPU 加速属性
- [ ] 弹簧物理效果，自然感觉
- [ ] 列表动画的错开子元素
- [ ] 在低端设备上测试性能
