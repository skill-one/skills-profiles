# Framer Motion / 动画规范

您是 Framer Motion（现更名为 Motion）和 React 以及 TypeScript 的专家。在创建动画时，请遵循以下规范。

## 核心原则

### 从正确的包中导入
- 对于 React 项目，请使用 `import { motion } from "motion/react"`（而不是 "framer-motion" - 这是过时的）
- 该库已从 Framer Motion 更名为 Motion
- 始终使用最新的 Motion API

### 以性能优先的方式
- 动画变换属性（`x`、`y`、`scale`、`rotate`）和 `opacity` 以获得最佳性能
- 这些属性可以进行硬件加速，并且不会触发布局重新计算
- 避免动画会导致布局偏移的属性，如 `width`、`height`、`top`、`left`、`margin`、`padding`

## 硬件加速

### 正确使用 will-change
```tsx
// 动画变换时
<motion.div
  style={{ willChange: "transform" }}
  animate={{ x: 100, y: 50, scale: 1.2 }}
/>

// 动画其他 GPU 加速属性时
<motion.div
  style={{ willChange: "opacity, transform" }}
  animate={{ opacity: 0.5, x: 100 }}
/>
```

### 应添加到 willChange 的属性
- `transform` - 用于 x、y、scale、rotate、skew
- `opacity` - 用于透明度动画
- `filter` - 用于模糊、亮度等
- `clipPath` - 用于 clip-path 动画
- `backgroundColor` - 用于背景色过渡

## 动画最佳实践

### 使用 Variants 处理复杂动画
```tsx
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: { y: 0, opacity: 1 }
};
```

### 使用 layoutId 处理共享元素过渡
```tsx
<motion.div layoutId="shared-element" />
```

### 优先使用弹簧动画
```tsx
// 弹簧动画比基于时间的动画更自然
<motion.div
  animate={{ x: 100 }}
  transition={{ type: "spring", stiffness: 300, damping: 30 }}
/>
```

## React 集成

### 性能优化缓存
```tsx
// 缓存动画 variants
const variants = useMemo(() => ({
  hidden: { opacity: 0 },
  visible: { opacity: 1 }
}), []);

// 缓存回调
const handleAnimationComplete = useCallback(() => {
  // 处理逻辑
}, []);
```

### 避免使用内联样式对象
```tsx
// 不良 - 每次渲染都会创建新对象
<motion.div style={{ willChange: "transform" }} />

// 良好 - 定义在外部或缓存
const style = { willChange: "transform" };
<motion.div style={style} />
```

## 可访问性

### 尊重减少动画的偏好
```tsx
import { useReducedMotion } from "motion/react";

function Component() {
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.div
      animate={{ x: shouldReduceMotion ? 0 : 100 }}
      transition={{ duration: shouldReduceMotion ? 0 : 0.3 }}
    />
  );
}
```

## 手势动画

### 正确使用手势属性
```tsx
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  transition={{ type: "spring", stiffness: 400, damping: 17 }}
/>
```

## 滚动动画

### 使用 useScroll 处理滚动关联动画
```tsx
import { useScroll, useTransform, motion } from "motion/react";

function ParallaxComponent() {
  const { scrollYProgress } = useScroll();
  const y = useTransform(scrollYProgress, [0, 1], [0, -100]);

  return <motion.div style={{ y }} />;
}
```

## 退出动画

### 使用 AnimatePresence 处理退出动画
```tsx
import { AnimatePresence, motion } from "motion/react";

<AnimatePresence mode="wait">
  {isVisible && (
    <motion.div
      key="modal"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    />
  )}
</AnimatePresence>
```

## 常见模式

### 错落有致的列表动画
```tsx
<motion.ul
  initial="hidden"
  animate="visible"
  variants={{
    visible: { transition: { staggerChildren: 0.07 } }
  }}
>
  {items.map((item) => (
    <motion.li
      key={item.id}
      variants={{
        hidden: { opacity: 0, y: 20 },
        visible: { opacity: 1, y: 0 }
      }}
    />
  ))}
</motion.ul>
```

### 页面过渡
```tsx
const pageTransition = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 },
  transition: { duration: 0.3 }
};
```

## 性能调试

- 使用 React DevTools 检查重新渲染
- 使用 Chrome DevTools 性能标签识别动画卡顿
- 目标帧率至少为 60fps，高刷新率屏幕为 120fps
- 在实际设备上测试，尤其是中端 Android 手机
