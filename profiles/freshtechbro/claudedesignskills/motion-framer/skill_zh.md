# 动画与 Framer Motion

## 概述

Motion（前身为 Framer Motion）是一个用于 React 和 JavaScript 的生产级动画库，它能够以最少的代码实现声明式、高性能的动画。它提供 `motion` 组件，这些组件为 HTML 元素添加了动画功能，支持手势识别（悬停、点击、拖拽、聚焦），并包含布局动画、退出动画和弹簧物理等高级功能。

**何时使用此技能：**
- 构建交互式 UI 组件（按钮、卡片、菜单）
- 创建微交互和悬停效果
- 实现页面过渡和路由动画
- 添加基于滚动的动画和视差效果
- 动画化布局变化（调整大小、重新排序、共享元素过渡）
- 拖拽界面
- 复杂的动画序列和基于状态的动画
- 用更强大、可控的动画替换 CSS 过渡

**技术：**
- **Motion** (v11+) - 来自 Framer Motion 创作者的现代化、更小的库
- **Framer Motion** - 功能全面的先辈（仍然广泛使用）
- 兼容 React 18+，也支持 Vue
- 支持 TypeScript
- 与 Next.js、Vite、Remix 以及所有现代 React 框架兼容

## 核心概念

### 1. Motion 组件

通过在元素前缀 `motion.` 将任何 HTML/SVG 元素转换为可动画组件：

```jsx
import { motion } from "framer-motion"

// 普通HTML变为motion组件
<motion.div />
<motion.button />
<motion.svg />
<motion.path />
```

每个 motion 组件都接受动画属性（如 `animate`、`initial`、`transition`）和手势属性（如 `whileHover`、`whileTap` 等）。

### 2. Animate 属性

`animate` 属性定义目标动画状态。当值变化时，Motion 会自动进行动画：

```jsx
// 简单动画 - x位置变化
<motion.div animate={{ x: 100 }} />

// 多个属性
<motion.div animate={{ x: 100, opacity: 1, scale: 1.2 }} />

// 状态变化时动画
const [isOpen, setIsOpen] = useState(false)
<motion.div animate={{ width: isOpen ? 300 : 100 }} />
```

### 3. Initial State

使用 `initial` 属性在动画前设置初始状态：

```jsx
<motion.div
  initial={{ opacity: 0, y: 50 }}
  animate={{ opacity: 1, y: 0 }}
/>
```

设置 `initial={false}` 以禁用挂载时的初始动画。

### 4. Transitions

使用 `transition` 属性控制动画在状态之间如何移动：

```jsx
// 基于持续时间
<motion.div
  animate={{ x: 100 }}
  transition={{ duration: 0.5, ease: "easeInOut" }}
/>

// 弹簧物理
<motion.div
  animate={{ scale: 1.2 }}
  transition={{ type: "spring", stiffness: 300, damping: 20 }}
/>

// 不同属性使用不同过渡
<motion.div
  animate={{ x: 100, opacity: 1 }}
  transition={{
    x: { type: "spring", stiffness: 300 },
    opacity: { duration: 0.2 }
  }}
/>
```

**过渡类型：**
- `"tween"`（默认）- 基于持续时间的缓动过渡
- `"spring"` - 基于物理的弹簧动画
- `"inertia"` - 减速动画（用于拖拽）

### 5. Variants

使用命名变体组织动画状态，以获得更清晰的代码并将状态传播到子元素：

```jsx
const variants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
  exit: { opacity: 0, scale: 0.9 }
}

<motion.div
  variants={variants}
  initial="hidden"
  animate="visible"
  exit="exit"
/>
```

**变体传播** - 子元素自动继承父元素变体状态：

```jsx
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1  // 延迟子元素动画
    }
  }
}

const itemVariants = {
  hidden: { x: -20, opacity: 0 },
  visible: { x: 0, opacity: 1 }
}

<motion.ul variants={containerVariants} initial="hidden" animate="visible">
  <motion.li variants={itemVariants} />
  <motion.li variants={itemVariants} />
  <motion.li variants={itemVariants} />
</motion.ul>
```

## 常见模式

### 1. 悬停动画

使用 `whileHover` 属性在悬停时进行动画：

```jsx
// 简单悬停效果
<motion.button
  whileHover={{ scale: 1.1 }}
  transition={{ duration: 0.2 }}
>
  悬停我
</motion.button>

// 多个属性
<motion.div
  whileHover={{
    scale: 1.05,
    backgroundColor: "#f0f0f0",
    boxShadow: "0px 10px 30px rgba(0, 0, 0, 0.2)"
  }}
>
  悬停卡片
</motion.div>

// 自定义过渡
<motion.button
  whileHover={{
    scale: 1.2,
    transition: { duration: 0.1 }  // 手势开始时的过渡
  }}
  transition={{ duration: 0.5 }}  // 手势结束时的过渡
>
  按钮
</motion.button>
```

**嵌套元素的悬停：**

```jsx
<motion.div whileHover="hover" variants={cardVariants}>
  <motion.h3 variants={titleVariants}>标题</motion.h3>
  <motion.img variants={imageVariants} />
</motion.div>
```

### 2. 点击/按动画

使用 `whileTap` 属性在点击/按时进行动画：

```jsx
// 点击时缩小
<motion.button
  whileTap={{ scale: 0.9 }}
>
  点击我
</motion.button>

// 组合悬停+点击
<motion.button
  whileHover={{ scale: 1.1 }}
  whileTap={{ scale: 0.95, rotate: 3 }}
>
  交互式按钮
</motion.button>

// 使用变体
const buttonVariants = {
  rest: { scale: 1 },
  hover: { scale: 1.1 },
  pressed: { scale: 0.95 }
}

<motion.button
  variants={buttonVariants}
  initial="rest"
  whileHover="hover"
  whileTap="pressed"
>
  按钮
</motion.button>
```

### 3. 拖拽交互

使用 `drag` 属性使元素可拖拽：

```jsx
// 基本拖拽（两个轴）
<motion.div drag />

// 限制在轴上
<motion.div drag="x" />  // 仅水平
<motion.div drag="y" />  // 仅垂直

// 拖拽限制
<motion.div
  drag
  dragConstraints={{ left: -100, right: 100, top: -100, bottom: 100 }}
/>

// 带父元素限制的拖拽
<motion.div ref={constraintsRef}>
  <motion.div drag dragConstraints={constraintsRef} />
</motion.div>

// 拖拽时的视觉反馈
<motion.div
  drag
  whileDrag={{
    scale: 1.1,
    boxShadow: "0px 10px 20px rgba(0,0,0,0.2)",
    cursor: "grabbing"
  }}
  dragElastic={0.1}  // 拖拽超出限制时的弹性
  dragTransition={{ bounceStiffness: 600, bounceDamping: 20 }}
/>
```

**拖拽事件：**

```jsx
<motion.div
  drag
  onDragStart={(event, info) => console.log(info.point)}
  onDrag={(event, info) => console.log(info.offset)}
  onDragEnd={(event, info) => console.log(info.velocity)}
/>
```

### 4. 退出动画 (AnimatePresence)

使用 `AnimatePresence` 在组件从 DOM 中移除时进行动画：

```jsx
import { AnimatePresence } from "framer-motion"

// 基本退出动画
<AnimatePresence>
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

**关键要求：**
- 组件必须是 `<AnimatePresence>` 的直接子元素
- 必须有一个唯一的 `key` 属性
- 使用 `exit` 属性定义退出动画

**带退出动画的列表项：**

```jsx
<AnimatePresence>
  {items.map(item => (
    <motion.li
      key={item.id}
      initial={{ opacity: 0, x: -50 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 50 }}
      layout  // 平滑布局移动
    >
      {item.name}
    </motion.li>
  ))}
</AnimatePresence>
```

**延迟退出动画：**

```jsx
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      when: "beforeChildren",
      staggerChildren: 0.1
    }
  },
  exit: {
    opacity: 0,
    transition: {
      when: "afterChildren",
      staggerChildren: 0.05,
      staggerDirection: -1  // 逆序
    }
  }
}

<AnimatePresence>
  {show && (
    <motion.div variants={containerVariants} initial="hidden" animate="visible" exit="exit">
      <motion.div variants={itemVariants} />
      <motion.div variants={itemVariants} />
      <motion.div variants={itemVariants} />
    </motion.div>
  )}
</AnimatePresence>
```

### 5. 布局动画

使用 `layout` 属性自动动画化布局变化（位置、大小）：

```jsx
// 动画化所有布局变化
<motion.div layout />

// 动画化仅位置变化
<motion.div layout="position" />

// 动画化仅大小变化
<motion.div layout="size" />
```

**网格布局动画：**

```jsx
const [columns, setColumns] = useState(3)

<motion.div className="grid">
  {items.map(item => (
    <motion.div
      key={item.id}
      layout
      transition={{ layout: { duration: 0.3, ease: "easeInOut" } }}
    />
  ))}
</motion.div>
```

**共享布局动画（layoutId）：**

使用 `layoutId` 将两个不同元素连接起来以实现平滑过渡：

```jsx
// 标签指示器示例
<nav>
  {tabs.map(tab => (
    <button key={tab.id} onClick={() => setActive(tab.id)}>
      {tab.label}
      {activeTab === tab.id && (
        <motion.div
          layoutId="underline"
          style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: 2 }}
        />
      )}
    </button>
  ))}
</nav>

// 从缩略图打开模态
<motion.img
  src={thumbnail}
  layoutId="product-image"
  onClick={() => setExpanded(true)}
/>

<AnimatePresence>
  {expanded && (
    <motion.div layoutId="product-image">
      <img src={fullsize} />
    </motion.div>
  )}
</AnimatePresence>
```

### 6. 基于滚动的动画

当元素进入视口时进行动画，使用 `whileInView`：

```jsx
<motion.div
  initial={{ opacity: 0, y: 50 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, amount: 0.8 }}  // once: 只触发一次, amount: 80%可见
  transition={{ duration: 0.5 }}
>
  滚动到视口时动画
</motion.div>
```

**视口选项：**
- `once: true` - 动画只触发一次
- `amount: 0.5` - 元素可见的百分比（0-1）或 "some" | "all"
- `margin: "-100px"` - 偏移视口边界

**延迟滚动动画：**

```jsx
<motion.ul
  initial="hidden"
  whileInView="visible"
  viewport={{ once: true, amount: 0.3 }}
  variants={{
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    },
    hidden: { opacity: 0 }
  }}
>
  <motion.li variants={itemVariants} />
  <motion.li variants={itemVariants} />
  <motion.li variants={itemVariants} />
</motion.ul>
```

### 7. 弹簧动画

使用弹簧物理实现自然、有弹性的动画：

```jsx
// 基本弹簧
<motion.div
  animate={{ scale: 1.2 }}
  transition={{ type: "spring" }}
/>

// 自定义弹簧物理
<motion.div
  animate={{ x: 100 }}
  transition={{
    type: "spring",
    stiffness: 300,  // 更高=更快、更突然（默认: 100）
    damping: 20,     // 更高=弹性更小（默认: 10）
    mass: 1,         // 更高=惯性更大（默认: 1）
  }}
/>

// 视觉持续时间（更容易控制弹簧）
<motion.div
  animate={{ rotate: 90 }}
  transition={{
    type: "spring",
    visualDuration: 0.5,  // 感知持续时间
    bounce: 0.25          // 弹性（0-1，默认: 0.25）
  }}
/>
```

**弹簧预设：**
- **温和**: `stiffness: 100, damping: 20`
- **摇晃**: `stiffness: 200, damping: 10`
- **僵硬**: `stiffness: 400, damping: 30`
- **缓慢**: `stiffness: 50, damping: 20`

## 手势识别

Motion 提供声明式手势处理器：

### 手势属性

```jsx
<motion.div
  whileHover={{ scale: 1.1 }}        // 指针悬停在元素上
  whileTap={{ scale: 0.9 }}          // 主要指针按下元素
  whileFocus={{ outline: "2px" }}    // 元素获得焦点
  whileDrag={{ scale: 1.1 }}         // 元素正在被拖拽
  whileInView={{ opacity: 1 }}       // 元素在视口内
/>
```

### 手势事件

```jsx
<motion.div
  onHoverStart={(event, info) => {}}
  onHoverEnd={(event, info) => {}}
  onTap={(event, info) => {}}
  onTapStart={(event, info) => {}}
  onTapCancel={(event, info) => {}}
  onDragStart={(event, info) => {}}
  onDrag={(event, info) => {}}
  onDragEnd={(event, info) => {}}
  onViewportEnter={(entry) => {}}
  onViewportLeave={(entry) => {}}
/>
```

**事件信息对象包含：**
- `point: { x, y }` - 页面坐标
- `offset: { x, y }` - 从拖拽开始的偏移
- `velocity: { x, y }` - 拖拽速度

## 钩子

### useAnimate

使用 `useAnimate` 钩子手动控制动画：

```jsx
import { useAnimate } from "framer-motion"

function Component() {
  const [scope, animate] = useAnimate()

  useEffect(() => {
    // 动画化多个元素
    animate([
      [scope.current, { opacity: 1 }],
      ["li", { x: 0, opacity: 1 }, { delay: stagger(0.1) }],
      [".button", { scale: 1.2 }]
    ])
  }, [])

  return (
    <div ref={scope}>
      <ul>
        <li>项目1</li>
        <li>项目2</li>
      </ul>
      <button className="button">点击</button>
    </div>
  )
}
```

**动画控制：**

```jsx
const controls = animate(element, { x: 100 })
controls.play()
controls.pause()
controls.stop()
controls.speed = 0.5
controls.time = 0  // 跳转到开始
```

### useSpring

创建弹簧动画值：

```jsx
import { useSpring } from "framer-motion"

function Component() {
  const x = useSpring(0, { stiffness: 300, damping: 20 })

  return (
    <motion.div style={{ x }}>
      <button onClick={() => x.set(100)}>移动</button>
    </motion.div>
  )
}
```

### useInView

检测元素何时在视口内：

```jsx
import { useInView } from "framer-motion"

function Component() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, amount: 0.5 })

  return (
    <div ref={ref}>
      {isInView ? "在视口内!" : "不在视口内"}
    </div>
  )
}
```

## 集成模式

### 与 GSAP

结合 Motion 用于 React 状态动画和 GSAP 用于复杂时间线：

```jsx
import { motion } from "framer-motion"
import gsap from "gsap"

function Component() {
  const boxRef = useRef()

  const handleClick = () => {
    // 使用GSAP进行复杂时间线
    const tl = gsap.timeline()
    tl.to(boxRef.current, { rotation: 360, duration: 1 })
      .to(boxRef.current, { scale: 1.5, duration: 0.5 })
  }

  return (
    // 使用Motion进行悬停/点击/布局动画
    <motion.div
      ref={boxRef}
      whileHover={{ scale: 1.1 }}
      onClick={handleClick}
    />
  )
}
```

### 与 React Three Fiber

使用 Motion 值动画化 3D 对象：

```jsx
import { motion } from "framer-motion"
import { useFrame } from "@react-three/fiber"

function Box() {
  const x = useMotionValue(0)

  useFrame(() => {
    // 同步Motion值与Three.js位置
    meshRef.current.position.x = x.get()
  })

  return (
    <>
      <mesh ref={meshRef}>
        <boxGeometry />
        <meshStandardMaterial />
      </mesh>
      <motion.div
        style={{ x }}
        drag="x"
        dragConstraints={{ left: -5, right: 5 }}
      />
    </>
  )
}
```

### 与表单库

动画化表单验证状态：

```jsx
import { motion, AnimatePresence } from "framer-motion"

function FormField({ error }) {
  return (
    <div>
      <motion.input
        animate={{
          borderColor: error ? "#ff0000" : "#cccccc",
          x: error ? [0, -10, 10, -10, 10, 0]  // 摇晃动画
        }}
        transition={{ duration: 0.4 }}
      />
      <AnimatePresence>
        {error && (
          <motion.p
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            style={{ color: "#ff0000" }}
          >
            {error}
          </motion.p>
        )}
      </AnimatePresence>
    </div>
  )
}
```

## 性能优化

### 1. 使用变换属性

变换属性（x, y, scale, rotate）是硬件加速的：

```jsx
// ✅ 良好 - 硬件加速
<motion.div animate={{ x: 100, scale: 1.2 }} />

// ❌ 避免 - 触发布局/绘制
<motion.div animate={{ left: 100, width: 200 }} />
```

### 2. 单独的变换属性

Motion 支持单独的变换属性以获得更清晰的代码：

```jsx
// 单独属性 (Motion特性)
<motion.div style={{ x: 100, rotate: 45, scale: 1.2 }} />

// 传统 (也受支持)
<motion.div style={{ transform: "translateX(100px) rotate(45deg) scale(1.2)" }} />
```

### 3. 为可访问性减少动画

尊重用户对减少动画的偏好：

```jsx
import { useReducedMotion } from "framer-motion"

function Component() {
  const shouldReduceMotion = useReducedMotion()

  return (
    <motion.div
      animate={{ x: 100 }}
      transition={shouldReduceMotion ? { duration: 0 } : { duration: 0.5 }}
    />
  )
}
```

### 4. 布局动画性能

布局动画可能很昂贵。使用以下方法优化：

```jsx
// 指定要动画化的内容
<motion.div layout="position" />  // 仅位置，不包括大小

// 优化过渡
<motion.div
  layout
  transition={{
    layout: { duration: 0.3, ease: "easeOut" }
  }}
/>
```

### 5. 有节制地使用 layoutId

`layoutId` 创建共享布局动画，但会全局跟踪元素。仅在需要时使用。

## 常见陷阱

### 1. 忘记使用 AnimatePresence 进行退出动画

**问题：** 退出动画不工作

```jsx
// ❌ 错误 - 没有AnimatePresence
{show && <motion.div exit={{ opacity: 0 }} />}
```

```jsx
// ✅ 正确 - 包裹在AnimatePresence中
<AnimatePresence>
  {show && <motion.div exit={{ opacity: 0 }} />}
</AnimatePresence>
```

### 2. 列表中缺少 key 属性

**问题：** AnimatePresence 无法跟踪元素

```jsx
// ❌ 错误 - 没有关键字
<AnimatePresence>
  {items.map(item => <motion.div exit={{ opacity: 0 }} />)}
</AnimatePresence>
```

```jsx
// ✅ 正确 - 唯一关键字
<AnimatePresence>
  {items.map(item => (
    <motion.div key={item.id} exit={{ opacity: 0 }} />
  ))}
</AnimatePresence>
```

### 3. 动画非变换属性

**问题：** 动画卡顿，性能差

```jsx
// ❌ 避免 - 不支持硬件加速
<motion.div animate={{ top: 100, left: 50, width: 200 }} />
```

```jsx
// ✅ 更好 - 使用变换
<motion.div animate={{ x: 50, y: 100, scaleX: 2 }} />
```

### 4. 过度使用布局动画

**问题：** 许多布局动画元素导致性能问题

```jsx
// ❌ 太多布局动画
{items.map(item => <motion.div layout>{item}</motion.div>)}
```

```jsx
// ✅ 仅在需要的地方使用布局，优化其他动画
{items.map(item => (
  <motion.div
    key={item.id}
    animate={{ opacity: 1 }}  // 更便宜的动画
    exit={{ opacity: 0 }}
  />
))}
```

### 5. 不使用变体进行复杂动画

**问题：** 重复的动画代码，无法对子元素进行编排

```jsx
// ❌ 重复
<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} />
<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} />
```

```jsx
// ✅ 使用变体
const variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 }
}

<motion.div variants={variants} initial="hidden" animate="visible" />
<motion.div variants={variants} initial="hidden" animate="visible" />
```

### 6. 过渡时间不正确

**问题：** 过渡不应用于特定手势

```jsx
// ❌ 错误 - 通用过渡不会应用于悬停
<motion.div
  whileHover={{ scale: 1.2 }}
  transition={{ duration: 1 }}  // 这会应用于animate属性，而不是whileHover
/>
```

```jsx
// ✅ 正确 - 在whileHover中过渡或分离的手势过渡
<motion.div
  whileHover={{
    scale: 1.2,
    transition: { duration: 0.2 }  // 应用于悬停开始
  }}
  transition={{ duration: 0.5 }}  // 应用于悬停结束
/>
```

## 资源

### 官方文档
- [Motion Docs](https://motion.dev/) - 官方 Motion 文档
- [Framer Motion Docs](https://www.framer.com/motion/) - Framer Motion（遗留）
- [Motion GitHub](https://github.com/framer/motion) - 源代码和示例

### 打包资源

此技能包括：

**references/**
- `api_reference.md` - 完整 Motion API 参考
- `variants_patterns.md` - 变体模式和编排
- `gesture_guide.md` - 全面手势处理指南

**scripts**
- `animation_generator.py` - 生成 Motion 组件模板
- `variant_builder.py` - 交互式变体配置工具

**assets**
- `starter_motion/` - 完整 Motion + Vite 启动模板
- `examples/` - 真实世界的 Motion 组件模式

### 社区资源
- [Motion Dev Discord](https://discord.gg/motion) - 官方社区
- [Framer Motion Examples](https://www.framer.com/motion/examples/) - 交互式示例
- [Motion Recipes](https://motion.dev/docs/recipes) - 常见模式
- [CodeSandbox Templates](https://codesandbox.io/s/framer-motion-examples) - 实时演示
