# React Spring Physics

基于物理的 React 应用动画，结合了 React Spring 的声明式弹簧动画和 Popmotion 的低级物理工具。

## 概述

React Spring 提供了自然且可中断的弹簧物理动画。与基于持续时间的动画不同，弹簧根据物理属性（质量、张力、摩擦力）计算运动，从而产生有机、逼真的运动效果。Popmotion 则通过可组合的动画函数补充了关键帧、衰减和惯性动画。

**何时使用此技能：**
- 自然、基于物理的 UI 动画
- 手势驱动界面（拖拽、滑动、滚动）
- 可中断的动画，在动画过程中响应用户输入
- 平滑过渡，在状态变化时保持速度
- 动量滚动和惯性效果

**核心库：**
- `@react-spring/web` - React 钩子用于弹簧动画
- `@react-spring/three` - Three.js 集成
- `popmotion` - 低级动画工具（可选，用于高级用例）

## 核心概念

### 弹簧物理

弹簧使用物理模拟将值从当前状态动画到目标状态：

```jsx
import { useSpring, animated } from '@react-spring/web'

function SpringExample() {
  const springs = useSpring({
    from: { opacity: 0, y: -40 },
    to: { opacity: 1, y: 0 },
    config: {
      mass: 1,        // 物体重量
      tension: 170,   // 弹簧强度
      friction: 26    // 对抗力
    }
  })

  return <animated.div style={springs}>Hello</animated.div>
}
```

### useSpring 钩子模式

两种初始化模式，适用于不同场景：

```jsx
// 对象配置（更简单，在属性变化时自动更新）
const springs = useSpring({
  from: { x: 0 },
  to: { x: 100 }
})

// 函数配置（更多控制，返回用于命令式更新的 API）
const [springs, api] = useSpring(() => ({
  from: { x: 0 }
}), [])

// 通过 API 触发动画
const handleClick = () => {
  api.start({
    from: { x: 0 },
    to: { x: 100 }
  })
}
```

### 弹簧配置预设

React Spring 提供了内置的配置预设：

```jsx
import { config } from '@react-spring/web'

// 可用预设
config.default  // { tension: 170, friction: 26 }
config.gentle   // { tension: 120, friction: 14 }
config.wobbly   // { tension: 180, friction: 12 }
config.stiff    // { tension: 210, friction: 20 }
config.slow     // { tension: 280, friction: 60 }
config.molasses // { tension: 280, friction: 120 }

// 使用
const springs = useSpring({
  from: { x: 0 },
  to: { x: 100 },
  config: config.wobbly
})
```

## 常见模式

### 1. 点击触发的弹簧动画

```jsx
import { useSpring, animated } from '@react-spring/web'

function ClickAnimated() {
  const [springs, api] = useSpring(() => ({
    from: { scale: 1 }
  }), [])

  const handleClick = () => {
    api.start({
      from: { scale: 1 },
      to: { scale: 1.2 },
      config: { tension: 300, friction: 10 }
    })
  }

  return (
    <animated.button
      onClick={handleClick}
      style={{
        transform: springs.scale.to(s => `scale(${s})`)
      }}
    >
      Click Me
    </animated.button>
  )
}
```

### 2. 多元素轨迹动画

```jsx
import { useTrail, animated } from '@react-spring/web'

function Trail({ items }) {
  const trails = useTrail(items.length, {
    from: { opacity: 0, x: -20 },
    to: { opacity: 1, x: 0 },
    config: config.gentle
  })

  return (
    <div>
      {trails.map((style, i) => (
        <animated.div key={i} style={style}>
          {items[i]}
        </animated.div>
      ))}
    </div>
  )
}
```

### 3. 列表过渡（进入/退出）

```jsx
import { useTransition, animated } from '@react-spring/web'

function List({ items }) {
  const transitions = useTransition(items, {
    from: { opacity: 0, height: 0 },
    enter: { opacity: 1, height: 80 },
    leave: { opacity: 0, height: 0 },
    config: config.stiff,
    keys: item => item.id
  })

  return transitions((style, item) => (
    <animated.div style={style}>
      {item.text}
    </animated.div>
  ))
}
```

### 4. 基于滚动的弹簧动画

```jsx
import { useScroll, animated } from '@react-spring/web'

function ScrollReveal() {
  const { scrollYProgress } = useScroll()

  return (
    <animated.div
      style={{
        opacity: scrollYProgress.to([0, 0.5], [0, 1]),
        scale: scrollYProgress.to([0, 0.5], [0.8, 1])
      }}
    >
      Scroll to reveal
    </animated.div>
  )
}
```

### 5. 视口交点动画

```jsx
import { useInView, animated } from '@react-spring/web'

function FadeInOnView() {
  const [ref, springs] = useInView(
    () => ({
      from: { opacity: 0, y: 100 },
      to: { opacity: 1, y: 0 }
    }),
    { rootMargin: '-40% 0%' }
  )

  return <animated.div ref={ref} style={springs}>Content</animated.div>
}
```

### 6. 链式异步动画

```jsx
import { useSpring, animated } from '@react-spring/web'

function ChainedAnimation() {
  const springs = useSpring({
    from: { x: 0, background: '#ff6d6d' },
    to: [
      { x: 80, background: '#fff59a' },
      { x: 0, background: '#88DFAB' },
      { x: 80, background: '#569AFF' }
    ],
    config: { tension: 200, friction: 20 },
    loop: true
  })

  return <animated.div style={springs} />
}
```

### 7. 保持速度的弹簧

```jsx
import { useSpring, animated } from '@react-spring/web'

function VelocityPreservation() {
  const [springs, api] = useSpring(() => ({
    x: 0,
    config: { tension: 300, friction: 30 }
  }), [])

  const handleDragEnd = () => {
    api.start({
      x: 0,
      velocity: springs.x.getVelocity(), // 保持动量
      config: { tension: 200, friction: 20 }
    })
  }

  return <animated.div style={springs} onMouseUp={handleDragEnd} />
}
```

## 集成模式

### 与 React Three Fiber (3D)

```jsx
import { useSpring, animated } from '@react-spring/three'
import { Canvas } from '@react-three/fiber'

const AnimatedBox = animated(MeshDistortMaterial)

function ThreeScene() {
  const [clicked, setClicked] = useState(false)

  const springs = useSpring({
    scale: clicked ? 1.5 : 1,
    color: clicked ? '#569AFF' : '#ff6d6d',
    config: { tension: 200, friction: 20 }
  })

  return (
    <Canvas>
      <mesh onClick={() => setClicked(!clicked)} scale={springs.scale}>
        <sphereGeometry args={[1, 64, 32]} />
        <AnimatedBox color={springs.color} />
      </mesh>
    </Canvas>
  )
}
```

### 与 Popmotion (低级物理)

```jsx
import { spring, inertia } from 'popmotion'
import { useState } from 'react'

function PopmotionIntegration() {
  const [x, setX] = useState(0)

  const handleDragEnd = (velocity) => {
    inertia({
      from: x,
      velocity: velocity,
      power: 0.3,
      timeConstant: 400,
      modifyTarget: v => Math.round(v / 100) * 100 // 对齐到网格
    }).start(setX)
  }

  return <div style={{ transform: `translateX(${x}px)` }} />
}
```

### 与表单和验证

```jsx
import { useSpring, animated } from '@react-spring/web'

function ValidatedInput() {
  const [error, setError] = useState(false)

  const shakeAnimation = useSpring({
    x: error ? [0, -10, 10, -10, 10, 0] : 0,
    config: { tension: 300, friction: 10 },
    onRest: () => setError(false)
  })

  return <animated.input style={shakeAnimation} />
}
```

## 性能优化

### 按需渲染

```jsx
// 仅在动画活跃时重新渲染
const [springs, api] = useSpring(() => ({
  from: { x: 0 },
  config: { precision: 0.01 } // 更高的值 = 更少的更新
}), [])
```

### 批量多个弹簧

```jsx
// 使用 useSprings 批量处理多个相似动画
const springs = useSprings(
  items.length,
  items.map(item => ({
    from: { opacity: 0 },
    to: { opacity: 1 }
  }))
)
```

### 跳过动画（测试/无障碍）

```jsx
import { Globals } from '@react-spring/web'

// 跳过所有动画（prefers-reduced-motion）
useEffect(() => {
  Globals.assign({ skipAnimation: true })
  return () => Globals.assign({ skipAnimation: false })
}, [])
```

## 常见陷阱

### 1. 忘记依赖数组

```jsx
// ❌ 错误：没有依赖，每次渲染创建新的弹簧
const springs = useSpring(() => ({ x: 0 }))

// ✅ 正确：空数组防止重新创建
const [springs, api] = useSpring(() => ({ x: 0 }), [])
```

### 2. 修改弹簧值

```jsx
// ❌ 错误：直接修改
springs.x.set(100)

// ✅ 正确：使用 API 动画
api.start({ x: 100 })
```

### 3. 忽略配置精度

```jsx
// ❌ 默认精度太细（0.0001），导致不必要的渲染
const springs = useSpring({ x: 0 })

// ✅ 根据用例设置合适的精度
const springs = useSpring({
  x: 0,
  config: { precision: 0.01 } // 当接近目标值时停止更新
})
```

### 4. 不处理速度

```jsx
// ❌ 中断动画时突然停止
api.start({ x: 0 })

// ✅ 保持动量
api.start({
  x: 0,
  velocity: springs.x.getVelocity()
})
```

### 5. 混合配置模式

```jsx
// ❌ 错误：同时使用对象和函数配置
const springs = useSpring({
  from: { x: 0 }
})
api.start({ x: 100 }) // api 是 undefined

// ✅ 正确：使用函数配置进行命令式控制
const [springs, api] = useSpring(() => ({
  from: { x: 0 }
}), [])
```

### 6. 动画非数值值

```jsx
// ❌ 错误：弹簧不能直接插值复杂的字符串
const springs = useSpring({ transform: 'translateX(100px) rotate(45deg)' })

// ✅ 正确：动画单个值
const springs = useSpring({ x: 100, rotation: 45 })
// 然后组合：transform: `translateX(${x}px) rotate(${rotation}deg)`
```

## 资源

### 脚本
- `spring_generator.py` - 生成 React Spring 模板代码
- `physics_calculator.py` - 计算最佳的弹簧物理参数

### 参考
- `react_spring_api.md` - 完整的 React Spring 钩子和 API 参考
- `popmotion_api.md` - Popmotion 函数和响应式流
- `physics_guide.md` - 弹簧物理深入解析及调优指南

### 资产
- `starter_spring/` - React + Vite 模板，包含 React Spring 示例
- `examples/` - 真实世界的模式（手势、滚动、3D 集成）

## 相关技能

- **motion-framer** - 另一种声明式动画方法，支持变体
- **gsap-scrolltrigger** - 基于时间线的动画，用于复杂序列
- **react-three-fiber** - 3D 场景管理（使用 @react-spring/three 进行动画）
- **animated-component-libraries** - 使用 Motion 预构建的动画组件

**物理 vs 时间线**：使用 React Spring 实现自然、基于物理的运动，响应用户输入。使用 GSAP 进行精确的时间线编排和复杂的多步骤序列。
