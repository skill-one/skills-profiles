# React 动画库 Motion

包名：`motion`（曾用名 `framer-motion`）。从 `"motion/react"` 中导入。

## 安装

```bash
pnpm add motion
```

## 导入

```tsx
// 标准React（Vite、CRA、Pages Router）
import { motion, AnimatePresence } from "motion/react"

// Next.js App Router — 使用 "motion/react-client" 进行RSC树形摇动
"use client"
import * as motion from "motion/react-client"

// 最小化包（2.3 KB）— 仅包含命令式API
import { useAnimate } from "motion/react-mini"

// 减小包（4.6 KB）— LazyMotion + m组件
import { LazyMotion, domAnimation, m } from "motion/react"
```

## Motion组件

每个HTML/SVG元素都有对应的`motion`版本：

```tsx
<motion.div />
<motion.button />
<motion.svg />
<motion.circle />
```

自定义组件：用`motion.create()`包裹：

```tsx
const MotionBox = motion.create(Box)
// 需要forwardRef — ref必须指向DOM节点
```

## 核心动画属性

```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}     // 挂载状态（或false跳过）
  animate={{ opacity: 1, y: 0 }}      // 目标状态
  exit={{ opacity: 0, y: -20 }}       // 卸载状态（需要AnimatePresence）
  transition={{ type: "spring", bounce: 0.25 }}
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  whileFocus={{ borderColor: "#00f" }}
  whileDrag={{ scale: 1.1 }}
  whileInView={{ opacity: 1 }}
  viewport={{ once: true, margin: "-100px" }}
/>
```

## 可动画值

Motion可以动画化**任何CSS值**：`opacity`、`filter`、`background-image`、`mask-image`。

**独立的变换**（CSS单独无法实现）：
- 平移：`x`、`y`、`z`
- 缩放：`scale`、`scaleX`、`scaleY`
- 旋转：`rotate`、`rotateX`、`rotateY`、`rotateZ`
- 倾斜：`skewX`、`skewY`
- 原点：`originX`、`originY`、`originZ`

**值类型**：数字、带单位的字符串（`"100px"`）、颜色（hex/rgba/hsla）、`"auto"`用于宽高。

**硬件加速**：直接设置`transform`进行GPU合成：

```tsx
<motion.li
  initial={{ transform: "translateX(-100px)" }}
  animate={{ transform: "translateX(0px)" }}
  transition={{ type: "spring" }}
/>
```

## 关键帧

将数组传递给Motion以按顺序动画化：

```tsx
<motion.div animate={{ x: [0, 100, 0] }} />

// null = "使用当前值"
<motion.div animate={{ x: [null, 100, 0] }} />
```

## 变体

用于编排动画的命名动画状态：

```tsx
const list = {
  visible: {
    transition: { staggerChildren: 0.1 }
  },
  hidden: {}
}

const item = {
  visible: { opacity: 1, y: 0 },
  hidden: { opacity: 0, y: 20 }
}

<motion.ul initial="hidden" animate="visible" variants={list}>
  <motion.li variants={item} />
  <motion.li variants={item} />
</motion.ul>
```

变体会向下传递。子元素会继承父元素的`animate`/`initial`/`exit`。

## AnimatePresence — 退出动画

```tsx
import { AnimatePresence } from "motion/react"

<AnimatePresence>
  {isVisible && (
    <motion.div
      key="modal"           // 必须的：唯一key
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    />
  )}
</AnimatePresence>
```

**关键规则**：
1. AnimatePresence必须保持挂载 — 永远不要在条件语句中包裹它
2. 直接子元素必须有唯一的`key`属性
3. `exit`属性仅适用于AnimatePresence内的motion组件

```tsx
// 错误 — AnimatePresence随条件卸载
{show && <AnimatePresence><motion.div /></AnimatePresence>}

// 正确 — 条件在AnimatePresence内
<AnimatePresence>{show && <motion.div key="k" />}</AnimatePresence>
```

**模式**：`"sync"`（默认）、`"wait"`（顺序进入/退出）、`"popLayout"`（将退出元素弹出流）

**幻灯片模式** — 更改`key`触发退出+进入：

```tsx
<AnimatePresence mode="wait">
  <motion.img
    key={image.src}
    initial={{ x: 300, opacity: 0 }}
    animate={{ x: 0, opacity: 1 }}
    exit={{ x: -300, opacity: 0 }}
  />
</AnimatePresence>
```

**动态退出数据** — 通过`custom`属性+`usePresenceData`传递：

```tsx
<AnimatePresence custom={direction}>
  <Slide key={id} />
</AnimatePresence>

// 在Slide内部：
const direction = usePresenceData()
```

## 过渡效果

完整的过渡API详情，请参阅[references/transitions-api.md](references/transitions-api.md)。

**快速参考**：

```tsx
// 弹簧（物理属性：x、y、scale的默认值）
transition={{ type: "spring", bounce: 0.25 }}
transition={{ type: "spring", stiffness: 300, damping: 20 }}
transition={{ type: "spring", visualDuration: 0.5, bounce: 0.25 }}

// 插值（不透明度、颜色的默认值）
transition={{ duration: 0.3, ease: "easeInOut" }}

// 单值过渡
transition={{
  default: { type: "spring" },
  opacity: { duration: 0.2, ease: "linear" }
}}

// 编排
transition={{ delay: 0.5, repeat: Infinity, repeatType: "reverse" }}

// 全局默认
<MotionConfig transition={{ duration: 0.3 }}>
```

## 布局动画

完整的布局动画详情，请参阅[references/layout-animations.md](references/layout-animations.md)。

```tsx
// 自动动画化任何布局变化
<motion.div layout />

// 共享元素过渡
<motion.div layoutId="underline" />

// 自定义布局过渡
<motion.div layout transition={{ layout: { duration: 0.3 } }} />
```

## 手势与拖拽

完整的gestures/drag API，请参阅[references/gestures-and-drag.md](references/gestures-and-drag.md)。

```tsx
<motion.div
  whileHover={{ scale: 1.1 }}
  whileTap={{ scale: 0.9 }}
  drag                           // 启用两个轴
  drag="x"                       // 限制为x轴
  dragConstraints={{ left: -100, right: 100 }}
  dragElastic={0.2}
/>
```

## 滚动动画

完整的滚动API，请参阅[references/scroll-animations.md](references/scroll-animations.md)。

```tsx
// 视口触发
<motion.div
  initial={{ opacity: 0, y: 50 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true }}
/>

// 滚动关联进度条
const { scrollYProgress } = useScroll()
<motion.div style={{ scaleX: scrollYProgress }} />

// 元素滚动进度
const ref = useRef(null)
const { scrollYProgress } = useScroll({
  target: ref,
  offset: ["start end", "end start"]
})
```

## Hooks与Motion值

完整的hooks API，请参阅[references/hooks-and-motion-values.md](references/hooks-and-motion-values.md)。

```tsx
// 手动Motion值（无重新渲染）
const x = useMotionValue(0)
const opacity = useTransform(x, [-200, 0, 200], [0, 1, 0])
<motion.div drag="x" style={{ x, opacity }} />

// 弹簧跟随
const springX = useSpring(x, { stiffness: 100, damping: 30 })

// 命令式动画控制
const [scope, animate] = useAnimate()
animate("li", { opacity: 1 }, { stagger: 0.1 })

// 事件监听（无重新渲染）
useMotionValueEvent(scrollY, "change", (v) => console.log(v))
```

## 包优化

| 方法 | 大小 | 你获得的内容 |
|------|------|-------------|
| `motion/react` | ~34 KB | 完整API |
| `LazyMotion` + `m` | ~4.6 KB | 声明式动画，无手势 |
| `motion/react-mini` | ~2.3 KB | `useAnimate`仅 |

```tsx
// LazyMotion模式
import { LazyMotion, domAnimation, m } from "motion/react"

<LazyMotion features={domAnimation}>
  <m.div animate={{ opacity: 1 }} />
</LazyMotion>
```

## 可访问性

```tsx
<MotionConfig reducedMotion="user">
  <App />
</MotionConfig>
```

选项：`"user"`（尊重系统设置）、`"always"`（强制即时）、`"never"`（忽略）。

Hook：`useReducedMotion()`返回`true`当用户偏好减少动画时。

## Tailwind集成

让每个库处理其优势。**移除Tailwind的`transition-*`类** — 它们会冲突。

```tsx
// 错误 — Tailwind过渡与Motion冲突
<motion.div className="transition-all duration-300" animate={{ x: 100 }} />

// 正确 — Tailwind用于样式，Motion用于动画
<motion.div className="rounded-lg bg-blue-600 p-4" whileHover={{ scale: 1.05 }} />
```

## Next.js App Router

Motion组件需要客户端渲染。使用`"motion/react-client"`进行最佳树形摇动：

```tsx
// components/motion-client.tsx
"use client"
import * as motion from "motion/react-client"
export { motion }

// app/page.tsx（服务器组件）
import { motion } from "@/components/motion-client"
<motion.div animate={{ opacity: 1 }} />
```

## 常见陷阱

1. **退出动画未触发** — AnimatePresence必须保持挂载；子元素需要唯一的`key`
2. **Tailwind过渡冲突** — 从motion元素移除`transition-*`类
3. **`height: "auto"` + `display: "none"`** — 使用`visibility: "hidden"`代替
4. **可滚动容器中的布局动画** — 给滚动父元素添加`layoutScroll`属性
5. **固定元素中的布局动画** — 给固定父元素添加`layoutRoot`属性
6. **百分比变换+布局** — 转换为像素；百分比值会破坏FLIP计算
7. **`popLayout`模式** — 自定义组件必须使用`forwardRef`将ref转发到DOM节点
8. **AnimatePresence `propagate`** — 在嵌套的AnimatePresence上设置为`true`以触发子元素退出

## 参考

- **动画API详情**：[references/animation-api.md](references/animation-api.md)
- **过渡类型与弹簧配置**：[references/transitions-api.md](references/transitions-api.md)
- **手势与拖拽**：[references/gestures-and-drag.md](references/gestures-and-drag.md)
- **布局动画**：[references/layout-animations.md](references/layout-animations.md)
- **滚动动画**：[references/scroll-animations.md](references/scroll-animations.md)
- **Hooks与Motion值**：[references/hooks-and-motion-values.md](references/hooks-and-motion-values.md)
