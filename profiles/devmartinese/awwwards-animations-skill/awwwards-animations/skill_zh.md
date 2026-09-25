# Awwwards 动画

在 Awwwards/FWA 级别的质量下创建高端网页动画。**React 优先方法**。60fps 不可协商。

## 决策矩阵

| 任务 | 库 | 原因 |
|------|---------|-----|
| 滚动驱动动画 | GSAP + ScrollTrigger + useGSAP | 行业标准，最佳控制 |
| 平滑滚动 | Lenis + ReactLenis | 最佳性能，可与 ScrollTrigger 一起工作 |
| React-native 动画 | Motion (Framer Motion) | 原生 React，useScroll/useTransform |
| 简单/轻量级效果 | Anime.js 4.0 | 小体积，干净的 API |
| 复杂时间线 | GSAP | 无与伦比的 时间线 控制 |
| SVG 变形 | GSAP MorphSVG 或 Anime.js | 两者都很好 |
| 3D + 动画 | Three.js + GSAP | GSAP 控制 Three.js 对象 |
| 页面过渡 | AnimatePresence 或 GSAP | Motion for React，GSAP 用于复杂 |
| 几何形状（矢量） | SVG + GSAP/Motion | 原生，可动画 |
| 几何形状（画布） | Canvas 2D API | 程序化，高性能 |
| 伪 3D 形状 | Zdog | 扁平化设计 3D，~2kb |
| 创意编码/生成 | p5.js | 丰富的生态系统 |
| 音频响应 | Tone.js | Web Audio，合成器，效果 |
| 2D 物理 | Matter.js | 重力，碰撞，约束 |
| 算法/生成艺术 | Canvas 2D + p5.js | 数学驱动的视觉效果 |
| 分形/L-系统 | Canvas 2D recursivo | 递归渲染 |
| 镶嵌/几何谜题 | SVG + GSAP | 精确的动画转换 |
| 动态排版高级 | GSAP SplitText + Canvas | 按字符控制 |
| 故障效果 | CSS + GSAP | 层叠 RGB 分裂，clip-path |
| 原始主义动画 | CSS 原始 + Motion | 硬切，无缓动 |
| 极简主义动画 | Motion springs | 微妙，有目的的运动 |

## 安装（最新稳定版 - 2025）

```bash
# GSAP + React 钩子 (v3.14.1)
npm install gsap @gsap/react

# Lenis (v1.3.17) - 包括 React 组件
npm install lenis

# Motion (Framer Motion)
npm install motion

# Anime.js (v4.0.0)
npm install animejs
```

## React 设置

### 1. GSAP 配置（全局）

```tsx
// lib/gsap.ts
'use client' // Next.js App Router

import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useGSAP } from '@gsap/react'

// 一次性注册插件
gsap.registerPlugin(ScrollTrigger, useGSAP)

export { gsap, ScrollTrigger, useGSAP }
```

### 2. Lenis + GSAP ScrollTrigger 集成（关键）

```tsx
// components/SmoothScroll.tsx
'use client'
import { ReactLenis, useLenis } from 'lenis/react'
import { useEffect } from 'react'
import { gsap, ScrollTrigger } from '@/lib/gsap'

export function SmoothScroll({ children }: { children: React.ReactNode }) {
  const lenis = useLenis()
  useEffect(() => {
    if (!lenis) return
    lenis.on('scroll', ScrollTrigger.update)
    gsap.ticker.add((time) => lenis.raf(time * 1000))
    gsap.ticker.lagSmoothing(0)
    return () => { gsap.ticker.remove(lenis?.raf) }
  }, [lenis])

  return (
    <ReactLenis root options={{ lerp: 0.1, duration: 1.2, smoothWheel: true }}>
      {children}
    </ReactLenis>
  )
}
// 在布局中包裹：<SmoothScroll>{children}</SmoothScroll>
```

## 核心模式（React）

详细实现请参考：
- **GSAP + useGSAP**: 查看 [references/gsap-react.md](references/gsap-react.md)
- **Motion (Framer Motion)**: 查看 [references/motion-patterns.md](references/motion-patterns.md)
- **Anime.js 4.0**: 查看 [references/animejs-react.md](references/animejs-react.md)
- **Lenis React**: 查看 [references/lenis-react.md](references/lenis-react.md)
- **几何形状**: 查看 [references/geometric-shapes.md](references/geometric-shapes.md) (SVG, Canvas, Zdog, p5.js, Tetris 风格)
- **音频响应**: 查看 [references/audio-reactive.md](references/audio-reactive.md) (Tone.js, Web Audio, 滚动音频)
- **2D 物理**: 查看 [references/physics-2d.md](references/physics-2d.md) (Matter.js, 碰撞, 约束)
- **高级 (Three.js, WebGL)**: 查看 [references/advanced-patterns.md](references/advanced-patterns.md)
- **算法 & 生成艺术**: 查看 [references/algorithmic-art.md](references/algorithmic-art.md) (分形, L-系统, 流场, 吸引子, 噪声, 神圣几何)
- **高级文本效果**: 查看 [references/text-effects.md](references/text-effects.md) (故障, 动态排版, 变形, 爆炸, 圆形文本, 混乱)
- **几何谜题**: 查看 [references/geometric-puzzles.md](references/geometric-puzzles.md) (Dudeney, 七巧板, 镶嵌, Penrose, 多米诺骨牌)
- **设计理念**: 查看 [references/design-philosophy.md](references/design-philosophy.md) (原始主义, 极简主义, 抽象, 混合风格, 色彩板)
- **性能**: 查看 [references/performance.md](references/performance.md)

## 快速模式（React）

### 1. 磁性光标 (GSAP + useGSAP)

```tsx
'use client'
import { useRef, useEffect } from 'react'
import { gsap, useGSAP } from '@/lib/gsap'

export function MagneticCursor() {
  const cursorRef = useRef<HTMLDivElement>(null)
  const pos = useRef({ x: 0, y: 0, cx: 0, cy: 0 })
  useEffect(() => {
    const h = (e: MouseEvent) => { pos.current.x = e.clientX; pos.current.y = e.clientY }
    window.addEventListener('mousemove', h)
    return () => window.removeEventListener('mousemove', h)
  }, [])
  useGSAP(() => {
    gsap.ticker.add(() => {
      const p = pos.current
      p.cx += (p.x - p.cx) * 0.15; p.cy += (p.y - p.cy) * 0.15
      gsap.set(cursorRef.current, { x: p.cx, y: p.cy })
    })
  })
  return <div ref={cursorRef} className="fixed w-10 h-10 border border-white rounded-full pointer-events-none mix-blend-difference z-[9999] -translate-x-1/2 -translate-y-1/2" />
}
```

### 2. 磁性按钮 (Motion)

```tsx
'use client'
import { useRef, useState } from 'react'
import { motion } from 'motion/react'

export function MagneticButton({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLButtonElement>(null)
  const [pos, setPos] = useState({ x: 0, y: 0 })
  const onMove = (e: React.MouseEvent) => {
    const { left, top, width, height } = ref.current!.getBoundingClientRect()
    setPos({ x: (e.clientX - left - width / 2) * 0.3, y: (e.clientY - top - height / 2) * 0.3 })
  }
  return (
    <motion.button ref={ref} onMouseMove={onMove} onMouseLeave={() => setPos({ x: 0, y: 0 })}
      animate={pos} transition={{ type: 'spring', stiffness: 150, damping: 15 }}
      className="px-8 py-4 bg-white text-black rounded-full">{children}</motion.button>
  )
}
```

### 3. 视差英雄 (GSAP + useGSAP)

```tsx
'use client'
import { useRef } from 'react'
import { gsap, ScrollTrigger, useGSAP } from '@/lib/gsap'

export function ParallaxHero() {
  const containerRef = useRef<HTMLDivElement>(null)

  useGSAP(() => {
    gsap.to('.parallax-bg', {
      yPercent: 50,
      ease: 'none',
      scrollTrigger: {
        trigger: containerRef.current,
        start: 'top top',
        end: 'bottom top',
        scrub: true,
      },
    })

    gsap.to('.hero-title', {
      yPercent: 100,
      opacity: 0,
      scrollTrigger: {
        trigger: containerRef.current,
        start: 'top top',
        end: '50% top',
        scrub: true,
      },
    })
  }, { scope: containerRef })

  return (
    <div ref={containerRef} className="relative h-screen overflow-hidden">
      <div className="parallax-bg absolute inset-0 bg-cover bg-center" />
      <h1 className="hero-title absolute inset-0 flex items-center justify-center text-6xl">
        Hero Title
      </h1>
    </div>
  )
}
```

### 4. 文本字符揭示 (Motion)

```tsx
'use client'
import { motion } from 'motion/react'

const container = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.02 },
  },
}

const child = {
  hidden: { opacity: 0, y: 50, rotateX: -90 },
  visible: {
    opacity: 1,
    y: 0,
    rotateX: 0,
    transition: { type: 'spring', damping: 12 },
  },
}

export function TextReveal({ text }: { text: string }) {
  return (
    <motion.span
      variants={container}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true }}
      className="inline-block"
    >
      {text.split('').map((char, i) => (
        <motion.span key={i} variants={child} className="inline-block">
          {char === ' ' ? '\u00A0' : char}
        </motion.span>
      ))}
    </motion.span>
  )
}
```

### 5. 图片揭示 (GSAP)

```tsx
'use client'
import { useRef } from 'react'
import { gsap, useGSAP } from '@/lib/gsap'

export function ImageReveal({ src, alt }: { src: string; alt: string }) {
  const containerRef = useRef<HTMLDivElement>(null)

  useGSAP(() => {
    gsap.from(containerRef.current, {
      clipPath: 'inset(100% 0% 0% 0%)',
      duration: 1.2,
      ease: 'power4.inOut',
      scrollTrigger: {
        trigger: containerRef.current,
        start: 'top 80%',
      },
    })

    gsap.from('.reveal-img', {
      scale: 1.3,
      duration: 1.5,
      ease: 'power2.out',
      scrollTrigger: {
        trigger: containerRef.current,
        start: 'top 80%',
      },
    })
  }, { scope: containerRef })

  return (
    <div ref={containerRef} className="overflow-hidden">
      <img src={src} alt={alt} className="reveal-img w-full h-full object-cover" />
    </div>
  )
}
```

### 6. 故障文本效果 (CSS + GSAP)

```tsx
'use client'
import { useRef, useEffect } from 'react'
import { gsap } from '@/lib/gsap'

export function GlitchText({ text }: { text: string }) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const layers = ref.current!.querySelectorAll('.g-layer')
    const tl = gsap.timeline({ repeat: -1, repeatDelay: 3 })
    tl.to(layers[0], { x: -5, duration: 0.05, ease: 'none' }, 0)
      .to(layers[0], { x: 5, duration: 0.05 }, 0.05)
      .to(layers[0], { x: 0, duration: 0.05 }, 0.1)
      .to(layers[1], { x: 5, duration: 0.05 }, 0.02)
      .to(layers[1], { x: -5, duration: 0.05 }, 0.07)
      .to(layers[1], { x: 0, duration: 0.05 }, 0.12)
    return () => { tl.kill() }
  }, [])

  return (
    <div ref={ref} className="relative font-mono text-5xl font-black">
      <span className="relative z-10">{text}</span>
      <span className="g-layer absolute inset-0 text-cyan-400 mix-blend-multiply" aria-hidden>{text}</span>
      <span className="g-layer absolute inset-0 text-red-400 mix-blend-multiply" aria-hidden>{text}</span>
    </div>
  )
}
```

### 7. 分形树 (Canvas 2D)

```tsx
'use client'
import { useRef, useEffect } from 'react'

export function FractalTree({ depth = 10, angle = 25 }: { depth?: number; angle?: number }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current!
    const ctx = canvas.getContext('2d')!
    canvas.width = canvas.offsetWidth * 2; canvas.height = canvas.offsetHeight * 2; ctx.scale(2, 2)
    let progress = 0, raf = 0

    function branch(x: number, y: number, len: number, a: number, d: number) {
      if (d > depth || len < 2) return
      const dp = Math.max(0, Math.min(1, progress * depth - d))
      if (dp <= 0) return
      const ex = x + Math.cos(a * Math.PI / 180) * len * dp
      const ey = y - Math.sin(a * Math.PI / 180) * len * dp
      ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(ex, ey)
      ctx.strokeStyle = `hsl(${120 + d * 15}, 60%, ${30 + d * 5}%)`
      ctx.lineWidth = Math.max(1, (depth - d) * 1.5); ctx.stroke()
      branch(ex, ey, len * 0.72, a + angle, d + 1)
      branch(ex, ey, len * 0.72, a - angle, d + 1)
    }
    const animate = () => {
      progress = Math.min(1, progress + 0.008)
      ctx.clearRect(0, 0, canvas.offsetWidth, canvas.offsetHeight)
      branch(canvas.offsetWidth / 2, canvas.offsetHeight, canvas.offsetHeight * 0.28, 90, 0)
      if (progress < 1) raf = requestAnimationFrame(animate)
    }
    animate()
    return () => cancelAnimationFrame(raf)
  }, [depth, angle])
  return <canvas ref={canvasRef} className="w-full h-full bg-gray-950" />
}
```

查看 [references/algorithmic-art.md](references/algorithmic-art.md) 获取 L-系统，流场，吸引子，噪声，神圣几何。

### 8. 几何分解 (SVG + GSAP)

```tsx
'use client'
import { useRef, useState } from 'react'
import { gsap } from '@/lib/gsap'

const P = [
  { id: 'A', tri: 'M 0,173 L 50,87 L 100,173 Z', sq: 'M 0,0 L 100,0 L 100,87 L 0,87 Z', c: '#f43f5e' },
  { id: 'B', tri: 'M 50,87 L 100,0 L 150,87 Z', sq: 'M 100,0 L 200,0 L 200,87 L 100,87 Z', c: '#8b5cf6' },
  { id: 'C', tri: 'M 100,173 L 150,87 L 200,173 Z', sq: 'M 0,87 L 100,87 L 100,173 L 0,173 Z', c: '#06b6d4' },
  { id: 'D', tri: 'M 50,87 L 100,173 L 150,87 L 100,0 Z', sq: 'M 100,87 L 200,87 L 200,173 L 100,173 Z', c: '#f59e0b' },
]
export function GeometricDissection() {
  const svg = useRef<SVGSVGElement>(null)
  const [isSq, setSq] = useState(false)
  const morph = () => {
    const t = !isSq
    P.forEach((p, i) => {
      const el = svg.current!.querySelector(`#d-${p.id}`)
      if (el) gsap.to(el, { attr: { d: t ? p.sq : p.tri }, duration: 1.5, ease: 'power2.inOut', delay: i * 0.15 })
    }); setSq(t)
  }
  return (
    <div className="flex flex-col items-center gap-4">
      <svg ref={svg} viewBox="-10 -10 220 200" className="w-64 h-64">
        {P.map(p => <path key={p.id} id={`d-${p.id}`} d={p.tri} fill={p.c} stroke="#000" strokeWidth="1.5" />)}
      </svg>
      <button onClick={morph} className="px-6 py-2 bg-white text-black font-mono text-sm">{isSq ? '△' : '□'}</button>
    </div>
  )
}
```

查看 [references/geometric-puzzles.md](references/geometric-puzzles.md) 获取七巧板，镶嵌，Penrose 骨牌，多米诺骨牌。

### 9. 原始主义网格 (Motion)

```tsx
'use client'
import { motion } from 'motion/react'

export function BrutalistGrid({ items }: { items: string[] }) {
  return (
    <div className="grid grid-cols-3 border-2 border-black">
      {items.map((item, i) => (
        <motion.div key={i}
          className="border-2 border-black p-6 font-mono font-black uppercase text-2xl"
          style={{ mixBlendMode: i % 2 === 0 ? 'normal' : 'difference' }}
          initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}
          transition={{ duration: 0, delay: i * 0.1 }}
          whileHover={{ backgroundColor: '#000', color: '#BAFF39', transition: { duration: 0 } }}
        >{item}</motion.div>
      ))}
    </div>
  )
}
```

## 设计理念（快速参考）

| 风格 | 运动感觉 | 缓动 | 字体排印 | 主要特征 |
|-------|------------|--------|------------|-----------|
| 原始主义 | 硬朗，即时，刺耳 | `none` / `steps()` | 单体，15-30vw | 原始诚实 |
| 极简主义 | 平滑，微妙，慢 | `power2.out` | 无衬线体轻 | 有目的的克制 |
| 抽象 | 噪声驱动，参数化 | 有机/正弦 | 变化 | 数学之美 |
| 新原始主义 | 大胆但受控 | `power1.out` | 单体 + 颜色 | 原始主义 + 克制 |

查看 [references/design-philosophy.md](references/design-philosophy.md) 获取完整指南，包括色彩板和混合策略。

## 缓动参考

| 感觉 | GSAP | Motion |
|------|------|--------|
| 平滑 | `power2.out` | `[0.16, 1, 0.3, 1]` |
| 快速 | `power4.out` | `[0.87, 0, 0.13, 1]` |
| 弹性 | `back.out(1.7)` | `{ type: 'spring', stiffness: 300, damping: 20 }` |
| 戏剧性 | `power4.inOut` | `[0.76, 0, 0.24, 1]` |

## 时间

- 微交互：150-300ms
- UI 过渡：300-500ms
- 页面过渡：500-800ms
- 错开：每项 0.02-0.1s

## 可访问性

```tsx
// Motion: useReducedMotion() → 条件性禁用/减少动画
import { useReducedMotion } from 'motion/react'
const reduced = useReducedMotion() // 如果 prefers-reduced-motion: reduce，则为 true
```

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
```

## 性能规则

1. 仅动画 `transform` 和 `opacity`
2. 节约使用 `will-change`
3. 始终清理：`useGSAP` 自动处理
4. 将 GSAP 选择器限制在容器引用范围内
5. 使用 `contextSafe()` 处理带有 GSAP 的事件处理程序
6. 保留 Motion 变体对象

## 常见陷阱

1. 未将 Lenis 与 ScrollTrigger 集成
2. useGSAP 中缺少 `scope`
3. 未使用 `contextSafe()` 处理点击处理程序
4. React 18 严格模式调用效果两次
5. 忘记在 Next.js App Router 中添加 `'use client'`
6. 动态内容后未调用 `ScrollTrigger.refresh()`

## 测试清单

- [ ] 滚动 60fps (Chrome DevTools 性能)
- [ ] 键盘导航正常工作
- [ ] 尊重 prefers-reduced-motion
- [ ] 无布局偏移 (CLS)
- [ ] 移动端触摸正常工作
- [ ] 生产中移除了 ScrollTrigger 标记
- [ ] 卸载时无内存泄漏

## 启发

Active Theory, Studio Freight, Locomotive, Resn, Aristide Benoist, Immersive Garden
