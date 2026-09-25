# 动画组件库

## 概述

本技能提供预构建的动画 React 组件库，特别是 Magic UI 和 React Bits。这些库提供生产就绪的动画组件，可显著加速现代交互式 Web 应用的开发。

**Magic UI** 提供 150+ 基于 Tailwind CSS 和 Framer Motion 的 TypeScript 组件，专为与 shadcn/ui 无缝集成而设计。组件可复制粘贴并高度可定制。

**React Bits** 提供 90+ 动画 React 组件，依赖项极小，专注于视觉效果、背景和微交互。组件强调性能和易于定制。

两个库都遵循现代 React 模式，支持 TypeScript，并与流行设计系统集成。

## 核心概念

### Magic UI 架构

Magic UI 组件基于三项基础技术构建：

1. **Tailwind CSS**：基于实用工具的样式，通过 `tailwind.config.js` 完全可定制
2. **Framer Motion**：基于物理的动画和手势识别
3. **shadcn/ui 集成**：遵循 shadcn 常规的 CLI 安装和组件结构

**安装方法**：

```bash
# 通过 shadcn CLI（推荐）
npx shadcn@latest add https://magicui.design/r/animated-beam

# 手动安装
# 1. 将组件代码复制到 components/ui/
# 2. 安装 motion：npm install motion
# 3. 在 globals.css 中添加所需的 CSS 动画
# 4. 确保 cn() 实用函数存在于 lib/utils.ts
```

**组件结构**：

```typescript
// 所有 Magic UI 组件都遵循此模式：
import { cn } from "@/lib/utils"
import { motion } from "motion/react"

interface ComponentProps extends React.ComponentPropsWithoutRef<"div"> {
  customProp?: string
  className?: string
}

export function MagicComponent({ className, customProp, ...props }: ComponentProps) {
  return (
    <motion.div
      className={cn("base-styles", className)}
      {...props}
    >
      {/* 组件内容 */}
    </motion.div>
  )
}
```

### React Bits 架构

React Bits 强调轻量级、独立的组件，依赖项极小：

1. **自包含**：每个组件具有最小的外部依赖项
2. **可选 CSS-in-JS**：许多组件使用内联样式或 CSS 模块
3. **性能优先**：针对 60fps 动画优化
4. **WebGL 支持**：某些组件（Particles、Plasma）使用 WebGL 实现高级效果

**安装**：

```bash
# 手动复制粘贴（主要方法）
# 将组件文件从 reactbits.dev 复制到您的项目

# 关键依赖（按需安装）：
npm install framer-motion  # 对于动画密集型组件
npm install ogl           # 对于 WebGL 组件（Particles、Plasma）
```

**组件类别**：

- **文本动画**：BlurText、CircularText、CountUp、SpinningText
- **交互元素**：MagicButton、Magnet、Dock、Stepper
- **背景**：Aurora、Plasma、Particles
- **列表和布局**：AnimatedList、Bento Grid

## 常见模式

### 1. Magic UI：动画背景模式

使用基于 SVG 的模式创建动态背景效果：

```typescript
import { GridPattern } from "@/components/ui/grid-pattern"
import { AnimatedGridPattern } from "@/components/ui/animated-grid-pattern"
import { cn } from "@/lib/utils"

export default function HeroSection() {
  return (
    <div className="relative flex h-[500px] w-full items-center justify-center overflow-hidden rounded-lg border">
      {/* 静态网格模式 */}
      <GridPattern
        squares={[
          [4, 4], [5, 1], [8, 2], [5, 3], [10, 10], [12, 15]
        ]}
        className={cn(
          "[mask-image:radial-gradient(400px_circle_at_center,white,transparent)]",
          "fill-gray-400/30 stroke-gray-400/30"
        )}
      />

      {/* 动态交互网格 */}
      <AnimatedGridPattern
        numSquares={50}
        maxOpacity={0.5}
        duration={4}
        repeatDelay={0.5}
        className={cn(
          "[mask-image:radial-gradient(500px_circle_at_center,white,transparent)]",
          "inset-x-0 inset-y-[-30%] h-[200%] skew-y-12"
        )}
      />

      <h1 className="relative z-10 text-6xl font-bold">
        您的内容在此
      </h1>
    </div>
  )
}
```

### 2. React Bits：文本揭示动画

使用 BlurText 实现滚动触发的文本揭示：

```jsx
import BlurText from './components/BlurText'

export default function MarketingSection() {
  return (
    <section className="py-20">
      {/* 单词逐个揭示 */}
      <BlurText
        text="将您的想法变为现实"
        delay={100}
        animateBy="words"
        direction="top"
        className="text-5xl font-bold text-center mb-8"
      />

      {/* 字符逐个揭示，带自定义缓动 */}
      <BlurText
        text="指尖精准的动画"
        delay={50}
        animateBy="characters"
        direction="bottom"
        threshold={0.3}
        stepDuration={0.4}
        animationFrom={{ filter: 'blur(20px)', opacity: 0, y: 50 }}
        animationTo={{ filter: 'blur(0px)', opacity: 1, y: 0 }}
        className="text-2xl text-gray-600 text-center"
      />
    </section>
  )
}
```

### 3. Magic UI：带效果的按钮组件

创建带闪光和边框光束效果的交互式按钮：

```typescript
import { ShimmerButton } from "@/components/ui/shimmer-button"
import { BorderBeam } from "@/components/ui/border-beam"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

export default function CTASection() {
  return (
    <div className="flex gap-4 items-center">
      {/* 闪光按钮 */}
      <ShimmerButton
        shimmerColor="#ffffff"
        shimmerSize="0.05em"
        shimmerDuration="3s"
        borderRadius="100px"
        background="rgba(0, 0, 0, 1)"
        className="px-8 py-3"
      >
        开始使用
      </ShimmerButton>

      {/* 带动画边框的卡片 */}
      <Card className="relative w-[350px] overflow-hidden">
        <div className="p-6">
          <h3 className="text-2xl font-bold">高级方案</h3>
          <p className="text-gray-600">解锁所有功能</p>
          <Button className="mt-4">订阅</Button>
        </div>
        <BorderBeam duration={8} size={100} />
      </Card>
    </div>
  )
}
```

### 4. React Bits：交互式 Dock 导航

实现 macOS 风格的 Dock 导航，带放大效果：

```jsx
import Dock from './components/Dock'
import { VscHome, VscArchive, VscAccount, VscSettingsGear } from 'react-icons/vsc'
import { useNavigate } from 'react-router-dom'

export default function AppNavigation() {
  const navigate = useNavigate()

  const dockItems = [
    {
      icon: <VscHome size={24} />,
      label: '仪表盘',
      onClick: () => navigate('/dashboard')
    },
    {
      icon: <VscArchive size={24} />,
      label: '项目',
      onClick: () => navigate('/projects')
    },
    {
      icon: <VscAccount size={24} />,
      label: '个人资料',
      onClick: () => navigate('/profile')
    },
    {
      icon: <VscSettingsGear size={24} />,
      label: '设置',
      onClick: () => navigate('/settings')
    }
  ]

  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2">
      <Dock
        items={dockItems}
        spring={{ mass: 0.15, stiffness: 200, damping: 15 }}
        magnification={80}
        distance={250}
        panelHeight={70}
        baseItemSize={55}
      />
    </div>
  )
}
```

### 5. React Bits：带 CountUp 的动画统计

为仪表盘和着陆页显示动画数字：

```jsx
import CountUp from './components/CountUp'

export default function Statistics() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 py-16">
      {/* 收入计数器 */}
      <div className="stat-card text-center">
        <CountUp
          start={0}
          end={1000000}
          duration={3}
          separator=","
          prefix="$"
          className="text-6xl font-bold text-blue-600"
        />
        <p className="text-xl text-gray-600 mt-2">产生的收入</p>
      </div>

      {/* 运行时间百分比 */}
      <div className="stat-card text-center">
        <CountUp
          end={99.9}
          duration={2.5}
          decimals={1}
          suffix="%"
          className="text-6xl font-bold text-green-600"
        />
        <p className="text-xl text-gray-600 mt-2">运行时间</p>
      </div>

      {/* 满意客户数量 */}
      <div className="stat-card text-center">
        <CountUp
          end={10000}
          duration={2}
          separator=","
          className="text-6xl font-bold text-purple-600"
        />
        <p className="text-xl text-gray-600 mt-2">满意客户</p>
      </div>
    </div>
  )
}
```

### 6. Magic UI：无限滚动 Marquee 组件

创建无限滚动内容显示：

```typescript
import { Marquee } from "@/components/ui/marquee"

const testimonials = [
  { name: "John Doe", text: "惊人的产品！", avatar: "/avatar1.jpg" },
  { name: "Jane Smith", text: "超出预期", avatar: "/avatar2.jpg" },
  { name: "Bob Johnson", text: "强烈推荐", avatar: "/avatar3.jpg" }
]

export default function Testimonials() {
  return (
    <section className="py-20">
      <h2 className="text-4xl font-bold text-center mb-12">
        我们的客户怎么说
      </h2>

      {/* 水平 Marquee */}
      <Marquee pauseOnHover className="[--duration:40s]">
        {testimonials.map((item, idx) => (
          <div key={idx} className="mx-4 w-[350px] rounded-lg border p-6">
            <p className="text-lg mb-4">"{item.text}"</p>
            <div className="flex items-center gap-3">
              <img src={item.avatar} alt={item.name} className="w-10 h-10 rounded-full" />
              <p className="font-semibold">{item.name}</p>
            </div>
          </div>
        ))}
      </Marquee>

      {/* 垂直 Marquee */}
      <Marquee vertical reverse className="h-[400px] mt-8">
        {testimonials.map((item, idx) => (
          <div key={idx} className="my-4 w-full max-w-md rounded-lg border p-6">
            <p>{item.text}</p>
          </div>
        ))}
      </Marquee>
    </section>
  )
}
```

### 7. React Bits：WebGL 背景效果

添加高性能动画背景：

```jsx
import Particles from './components/Particles'
import Plasma from './components/Plasma'
import Aurora from './components/Aurora'

// Particles 效果
export default function ParticlesHero() {
  return (
    <section style={{ position: 'relative', height: '100vh' }}>
      <Particles
        particleCount={200}
        particleColors={['#FF6B6B', '#4ECDC4', '#45B7D1']}
        particleSpread={10}
        speed={0.12}
        moveParticlesOnHover={true}
        particleHoverFactor={2}
        particleBaseSize={100}
        sizeRandomness={1.2}
        alphaParticles={true}
        cameraDistance={20}
        className="particles-bg"
      />
      <div className="relative z-10 flex items-center justify-center h-full">
        <h1 className="text-7xl font-bold text-white">
          欢迎来到未来
        </h1>
      </div>
    </section>
  )
}

// Plasma 效果
export default function PlasmaBackground() {
  return (
    <div className="relative min-h-screen">
      <Plasma
        color1="#FF0080"
        color2="#7928CA"
        color3="#00DFD8"
        speed={0.8}
        blur={30}
        className="plasma-bg"
      />
      <div className="relative z-10 p-8">
        <h1>带 Plasma 背景的内容</h1>
      </div>
    </div>
  )
}

// Aurora 效果
export default function AuroraHero() {
  return (
    <div className="relative min-h-screen">
      <Aurora
        colors={['#FF00FF', '#00FFFF', '#FFFF00']}
        speed={0.5}
        blur={80}
      />
      <main className="relative z-10">
        <h1>赛博朋克 Aurora 效果</h1>
      </main>
    </div>
  )
}
```

## 集成模式

### 与 shadcn/ui 集成

Magic UI 组件专为与 shadcn/ui 无缝工作而设计：

```bash
# 安装 shadcn/ui 组件
npx shadcn@latest add button card

# 安装 Magic UI 组件
npx shadcn@latest add https://magicui.design/r/shimmer-button

# 在组件中一起使用
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { ShimmerButton } from "@/components/ui/shimmer-button"
import { BorderBeam } from "@/components/ui/border-beam"
```

**必需的实用函数**（`lib/utils.ts`）：

```typescript
import clsx, { ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

### 与 Framer Motion 集成

两个库都利用 Framer Motion 实现动画：

```jsx
import { motion } from "framer-motion"
import { Magnet } from './components/Magnet'

// 结合 React Bits Magnet 与 Framer Motion 手势
export default function InteractiveCard() {
  return (
    <Magnet magnitude={0.4} maxDistance={180}>
      <motion.div
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className="card p-6 rounded-xl shadow-lg"
      >
        <h3>交互式卡片</h3>
        <p>结合磁力吸引与缩放动画</p>
      </motion.div>
    </Magnet>
  )
}
```

### 与 React Router 集成

将动画组件与路由结合：

```jsx
import { AnimatePresence, motion } from "framer-motion"
import { useLocation, Routes, Route } from "react-router-dom"
import { Dock } from './components/Dock'

export default function App() {
  const location = useLocation()

  return (
    <>
      {/* 动画页面过渡 */}
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <HomePage />
            </motion.div>
          } />
        </Routes>
      </AnimatePresence>

      {/* 持久 Dock 导航 */}
      <Dock items={navItems} />
    </>
  )
}
```

### 结合 Magic UI 和 React Bits

在一个项目中利用两个库的优势：

```jsx
// Magic UI：模式和结构组件
import { GridPattern } from "@/components/ui/grid-pattern"
import { BorderBeam } from "@/components/ui/border-beam"
import { Marquee } from "@/components/ui/marquee"

// React Bits：交互元素和效果
import BlurText from './components/BlurText'
import CountUp from './components/CountUp'
import Particles from './components/Particles'

export default function LandingPage() {
  return (
    <main>
      {/* 英雄区域带 React Bits 背景 + Magic UI 模式 */}
      <section className="relative h-screen">
        <Particles particleCount={150} />
        <GridPattern
          squares={[[4,4], [8,2], [12,6]]}
          className="opacity-30"
        />
        <BlurText
          text="下一代平台"
          className="text-7xl font-bold"
        />
      </section>

      {/* 统计带 React Bits CountUp */}
      <section>
        <CountUp end={10000} suffix="+" />
      </section>

      {/* 测试imonials 带 Magic UI Marquee */}
      <section>
        <Marquee>
          {/* 测试imonials 卡片 */}
        </Marquee>
      </section>
    </main>
  )
}
```

## 性能优化

### Magic UI 性能技巧

1. **使用 CSS Mask 而不是 Clipping**：对于大型模式更高效

```typescript
<GridPattern
  className="[mask-image:radial-gradient(400px_circle_at_center,white,transparent)]"
/>
```

2. **减少动画复杂性**：在移动设备上降低 `numSquares` 对于 AnimatedGridPattern

```typescript
const isMobile = window.innerWidth < 768
<AnimatedGridPattern
  numSquares={isMobile ? 20 : 50}
  duration={isMobile ? 6 : 4}
/>
```

3. **懒加载组件**：使用 React.lazy 对于重型组件

```typescript
const AnimatedGridPattern = React.lazy(() =>
  import("@/components/ui/animated-grid-pattern")
)
```

### React Bits 性能技巧

1. **WebGL 组件**：在低端设备上减少粒子数量

```jsx
const particleCount = navigator.hardwareConcurrency > 4 ? 300 : 150

<Particles
  particleCount={particleCount}
  speed={0.1}
/>
```

2. **在减少运动时禁用动画**:

```jsx
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

<BlurText
  text="可访问文本"
  delay={prefersReducedMotion ? 0 : 100}
  animateBy={prefersReducedMotion ? "none" : "words"}
/>
```

3. **优化 Marquee 内容**：限制项目以获得更好的性能

```typescript
<Marquee repeat={2}> {/* 而不是默认的 4 */}
  {items.slice(0, 10)} {/* 限制项目 */}
</Marquee>
```

4. **使用 RequestIdleCallback 对于非关键动画**:

```jsx
useEffect(() => {
  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
      // 初始化昂贵的动画
    })
  }
}, [])
```

## 常见陷阱

### 1. 缺少依赖

**问题**：组件因缺少 `motion` 或实用函数而崩溃。

**解决方案**：始终安装所需的依赖项和实用函数：

```bash
# Magic UI 要求
npm install motion clsx tailwind-merge

# React Bits WebGL 组件
npm install ogl

# 确保 cn() 实用函数存在
```

```typescript
// lib/utils.ts
import clsx, { ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

### 2. CSS 动画未应用

**问题**：Magic UI 动画在手动安装后无法工作。

**解决方案**：在 `globals.css` 中添加所需的 CSS 动画：

```css
/* app/globals.css */
@theme inline {
  --animate-ripple: ripple var(--duration, 2s) ease calc(var(--i, 0) * 0.2s) infinite;
  --animate-shimmer-slide: shimmer-slide var(--speed) ease-in-out infinite alternate;
  --animate-marquee: marquee var(--duration) linear infinite;
  --animate-marquee-vertical: marquee-vertical var(--duration) linear infinite;
}

@keyframes ripple {
  0%, 100% { transform: translate(-50%, -50%) scale(1); }
  50% { transform: translate(-50%, -50%) scale(0.9); }
}

@keyframes shimmer-slide {
  to { transform: translate(calc(100cqw - 100%), 0); }
}

@keyframes marquee {
  from { transform: translateX(0); }
  to { transform: translateX(calc(-100% - var(--gap))); }
}

@keyframes marquee-vertical {
  from { transform: translateY(0); }
  to { transform: translateY(calc(-100% - var(--gap))); }
}
```

### 3. Z-Index 冲突

**问题**：背景模式或效果覆盖前景内容。

**解决方案**：使用正确的 z-index 层级：

```jsx
<div className="relative">
  {/* 背景 (z-0 或负值) */}
  <GridPattern className="absolute inset-0 -z-10" />

  {/* 内容 (更高的 z-index) */}
  <div className="relative z-10">
    <h1>内容出现在模式上方</h1>
  </div>
</div>
```

### 4. 多个动画组件导致性能问题

**问题**：同时运行多个重型动画时页面卡顿。

**解决方案**：实现渐进增强和条件渲染：

```jsx
import { useState, useEffect } from 'react'

export default function OptimizedPage() {
  const [enableHeavyEffects, setEnableHeavyEffects] = useState(false)

  useEffect(() => {
    // 检查设备能力
    const isHighEnd = navigator.hardwareConcurrency > 4 &&
                     !navigator.userAgent.includes('Mobile')
    setEnableHeavyEffects(isHighEnd)
  }, [])

  return (
    <section className="relative">
      {enableHeavyEffects ? (
        <Particles particleCount={300} />
      ) : (
        <GridPattern /> {/* 更轻的替代方案 */}
      )}

      <div className="content">
        {/* 页面内容 */}
      </div>
    </section>
  )
}
```

### 5. TypeScript 类型错误

**问题**：TypeScript 抱怨组件属性。

**解决方案**：扩展适当的基类型：

```typescript
// Magic UI 模式
interface CustomComponentProps extends React.ComponentPropsWithoutRef<"div"> {
  customProp?: string
  className?: string
}

// React Bits 模式
interface CustomProps extends React.HTMLAttributes<HTMLDivElement> {
  customProp?: string
}
```

### 6. Tailwind 类未应用

**问题**：Magic UI 组件中的自定义 Tailwind 类无法工作。

**解决方案**：确保内容路径包含组件目录：

```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}", // 包含组件目录
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

## 资源

### 官方文档
- **Magic UI**: https://magicui.design
- **React Bits**: https://reactbits.dev
- **shadcn/ui**: https://ui.shadcn.com
- **Framer Motion**: https://motion.dev

### 关键脚本
- `scripts/component_importer.py` - 从两个库导入和自定义组件
- `scripts/props_generator.py` - 生成组件属性配置

### 参考
- `references/magic_ui_components.md` - 带使用示例的 Magic UI 组件完整目录
- `references/react_bits_components.md` - React Bits 组件库参考
- `references/customization_guide.md` - 两个库的基于属性的自定义模式

### 启动资源
- `assets/component_showcase/` - 所有组件的交互式演示
- `assets/examples/` - 着陆页部分、仪表板小部件、微交互

## 相关技能

- **motion-framer**: 用于理解两个库使用的底层动画概念
- **gsap-scrolltrigger**: 替代方法用于滚动驱动动画
- **react-spring-physics**: 替代方法用于物理动画库
- **threejs-webgl**: 作为替代方案用于 3D 背景效果
