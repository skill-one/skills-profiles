# Framer Motion 动画原则

使用 Framer Motion 的声明式 React API 实现 12 条迪士尼动画原则。

## 1. 压缩与拉伸

```jsx
<motion.div
  animate={{ scaleX: [1, 1.2, 1], scaleY: [1, 0.8, 1] }}
  transition={{ duration: 0.3, times: [0, 0.5, 1] }}
/>
```

## 2. 预期

```jsx
<motion.div
  variants={{
    idle: { y: 0, scaleY: 1 },
    anticipate: { y: 10, scaleY: 0.9 },
    jump: { y: -200 }
  }}
  initial="idle"
  animate={["anticipate", "jump"]}
  transition={{ duration: 0.5, times: [0, 0.2, 1] }}
/>
```

## 3. 舞台化

```jsx
<motion.div animate={{ filter: "blur(3px)", opacity: 0.6 }} /> {/* 背景 */}
<motion.div animate={{ scale: 1.1, zIndex: 10 }} /> {/* 英雄 */}
```

## 4. 直接前进 / 姿态到姿态

```jsx
<motion.div
  animate={{
    x: [0, 100, 200, 300],
    y: [0, -50, 0, -30]
  }}
  transition={{ duration: 1, ease: "easeInOut" }}
/>
```

## 5. 追随与重叠动作

```jsx
<motion.div animate={{ x: 200 }} transition={{ duration: 0.5 }}>
  <motion.span
    animate={{ x: 200 }}
    transition={{ duration: 0.5, delay: 0.05 }} // 头发
  />
  <motion.span
    animate={{ x: 200 }}
    transition={{ duration: 0.6, delay: 0.1 }} // 披风
  />
</motion.div>
```

## 6. 缓入缓出

```jsx
<motion.div
  animate={{ x: 300 }}
  transition={{
    duration: 0.6,
    ease: [0.42, 0, 0.58, 1] // easeInOut cubic-bezier
  }}
/>
// 或使用: "easeIn", "easeOut", "easeInOut"
```

## 7. 弧线

```jsx
<motion.div
  animate={{
    x: [0, 100, 200],
    y: [0, -100, 0]
  }}
  transition={{ duration: 1, ease: "easeInOut" }}
/>
```

## 8. 次要动作

```jsx
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
>
  <motion.span
    animate={{ rotate: [0, 10, -10, 0] }}
    transition={{ duration: 0.3 }}
  >
    图标
  </motion.span>
</motion.button>
```

## 9. 时间

```jsx
const timings = {
  fast: { duration: 0.15 },
  normal: { duration: 0.3 },
  slow: { duration: 0.6 },
  spring: { type: "spring", stiffness: 300, damping: 20 }
};
```

## 10. 夸张

```jsx
<motion.div
  animate={{ scale: 1.5, rotate: 720 }}
  transition={{
    type: "spring",
    stiffness: 200,
    damping: 10 // 低阻尼 = 超调
  }}
/>
```

## 11. 实体绘制

```jsx
<motion.div
  style={{ perspective: 1000 }}
  animate={{ rotateX: 45, rotateY: 30 }}
  transition={{ duration: 0.5 }}
/>
```

## 12. 吸引力

```jsx
<motion.div
  whileHover={{
    scale: 1.02,
    boxShadow: "0 20px 40px rgba(0,0,0,0.2)"
  }}
  transition={{ duration: 0.3 }}
/>
```

## 错开子元素

```jsx
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

<motion.ul variants={container} initial="hidden" animate="show">
  {items.map(item => <motion.li variants={itemVariant} />)}
</motion.ul>
```

## Framer Motion 关键特性

- `animate` - 目标状态
- `variants` - 命名动画状态
- `whileHover` / `whileTap` - 手势动画
- `transition` - 时间与缓动
- `AnimatePresence` - 退出动画
- `useAnimation` - 程序化控制
- `layout` - 自动动画布局变更
