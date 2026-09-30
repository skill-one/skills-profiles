---
name: animejs
description: 适用于 DOM、CSS、SVG 和 JavaScript 对象的通用 JavaScript 动画引擎。在创建基于时间轴的动画、错落效果、SVG 变形、关键帧序列或复杂编排动画时使用。触发于涉及 Anime.js、时间轴动画、错落序列、SVG 路径动画、变形或多步骤动画编排的任务。适用于 SVG 密集型动画和独立于 React 的项目，作为 GSAP 的替代方案。
---

# Anime.js

一个轻量级的 JavaScript 动画库，具备强大的时间轴和交错功能，用于网页动画。

## 概述

Anime.js（读作“Anime JS”）是一个通用的动画引擎，可用于 DOM 元素、CSS 属性、SVG 属性和 JavaScript 对象。与特定于 React 的库不同，Anime.js 支持原生 JavaScript 以及任何框架。

**何时使用此技能：**
- 需要精确编排的基于时间轴的动画序列
- 跨多个元素的交错动画
- SVG 路径变形和绘制动画
- 基于百分比计时的关键帧动画
- 框架无关的动画（适用于 React、Vue、原生 JS）
- 复杂的缓动函数（弹簧、阶梯、cubic-bezier）

**核心功能：**
- 支持相对位置的时间轴排序
- 强大的交错工具（网格、从中心开始、缓动）
- SVG 变形和路径动画
- 内置弹簧物理缓动
- 支持灵活计时的关键帧
- 极小的打包体积（约 9KB 压缩后）

## 核心概念

### 基础动画

`anime()` 函数用于创建动画：

```javascript
import anime from 'animejs'

anime({
  targets: '.element',
  translateX: 250,
  rotate: '1turn',
  duration: 800,
  easing: 'easeInOutQuad'
})
```

### 目标

指定动画目标有多种方式：

```javascript
// CSS 选择器
anime({ targets: '.box' })

// DOM 元素
anime({ targets: document.querySelectorAll('.box') })

// 元素数组
anime({ targets: [el1, el2, el3] })

// JavaScript 对象
const obj = { x: 0 }
anime({ targets: obj, x: 100 })
```

### 可动画属性

**CSS 属性：**
```javascript
anime({
  targets: '.element',
  translateX: 250,
  scale: 2,
  opacity: 0.5,
  backgroundColor: '#FFF'
})
```

**CSS 变换（独立属性）：**
```javascript
anime({
  targets: '.element',
  translateX: 250,   // 独立变换
  rotate: '1turn',   // 而非 'transform: rotate()'
  scale: 2
})
```

**SVG 属性：**
```javascript
anime({
  targets: 'path',
  d: 'M10 80 Q 77.5 10, 145 80', // 路径变形
  fill: '#FF0000',
  strokeDashoffset: [anime.setDashoffset, 0] // 线条绘制
})
```

**JavaScript 对象：**
```javascript
const obj = { value: 0 }
anime({
  targets: obj,
  value: 100,
  round: 1,
  update: () => console.log(obj.value)
})
```

### 时间轴

使用精确控制创建复杂的序列：

```javascript
const timeline = anime.timeline({
  duration: 750,
  easing: 'easeOutExpo'
})

timeline
  .add({
    targets: '.box1',
    translateX: 250
  })
  .add({
    targets: '.box2',
    translateX: 250
  }, '-=500') // 在前一个动画结束前 500ms 开始
  .add({
    targets: '.box3',
    translateX: 250
  }, '+=200') // 在前一个动画结束后 200ms 开始
```

## 常见模式

### 1. 交错动画（顺序显示）

```javascript
anime({
  targets: '.stagger-element',
  translateY: [100, 0],
  opacity: [0, 1],
  delay: anime.stagger(100), // 每次增加 100ms 延迟
  easing: 'easeOutQuad',
  duration: 600
})
```

### 2. 从中心开始交错

```javascript
anime({
  targets: '.grid-item',
  scale: [0, 1],
  delay: anime.stagger(50, {
    grid: [14, 5],
    from: 'center', // 也可以是：'first', 'last', index, [x, y]
    axis: 'x'       // 也可以是：'y', null
  }),
  easing: 'easeOutQuad'
})
```

### 3. SVG 线条绘制

```javascript
anime({
  targets: 'path',
  strokeDashoffset: [anime.setDashoffset, 0],
  easing: 'easeInOutQuad',
  duration: 2000,
  delay: (el, i) => i * 250
})
```

### 4. SVG 变形

```javascript
anime({
  targets: '#morphing-path',
  d: [
    { value: 'M10 80 Q 77.5 10, 145 80' }, // 起始形状
    { value: 'M10 80 Q 77.5 150, 145 80' }  // 结束形状
  ],
  duration: 2000,
  easing: 'easeInOutQuad',
  loop: true,
  direction: 'alternate'
})
```

### 5. 时间轴序列

```javascript
const tl = anime.timeline({
  easing: 'easeOutExpo',
  duration: 750
})

tl.add({
  targets: '.title',
  translateY: [-50, 0],
  opacity: [0, 1]
})
.add({
  targets: '.subtitle',
  translateY: [-30, 0],
  opacity: [0, 1]
}, '-=500')
.add({
  targets: '.button',
  scale: [0, 1],
  opacity: [0, 1]
}, '-=300')
```

### 6. 关键帧动画

```javascript
anime({
  targets: '.element',
  keyframes: [
    { translateX: 100 },
    { translateY: 100 },
    { translateX: 0 },
    { translateY: 0 }
  ],
  duration: 4000,
  easing: 'easeInOutQuad',
  loop: true
})
```

### 7. 滚动触发动画

```javascript
const animation = anime({
  targets: '.scroll-element',
  translateY: [100, 0],
  opacity: [0, 1],
  easing: 'easeOutQuad',
  autoplay: false
})

window.addEventListener('scroll', () => {
  const scrollPercent = window.scrollY / (document.body.scrollHeight - window.innerHeight)
  animation.seek(animation.duration * scrollPercent)
})
```

## 集成模式

### 与 React 集成

```javascript
import { useEffect, useRef } from 'react'
import anime from 'animejs'

function AnimatedComponent() {
  const ref = useRef(null)

  useEffect(() => {
    const animation = anime({
      targets: ref.current,
      translateX: 250,
      duration: 800,
      easing: 'easeInOutQuad'
    })

    return () => animation.pause()
  }, [])

  return <div ref={ref}>Animated</div>
}
```

### 与 Vue 集成

```javascript
export default {
  mounted() {
    anime({
      targets: this.$el,
      translateX: 250,
      duration: 800
    })
  }
}
```

### 路径跟随动画

```javascript
const path = anime.path('#motion-path')

anime({
  targets: '.element',
  translateX: path('x'),
  translateY: path('y'),
  rotate: path('angle'),
  easing: 'linear',
  duration: 2000,
  loop: true
})
```

## 高级技巧

### 弹簧缓动

```javascript
anime({
  targets: '.element',
  translateX: 250,
  easing: 'spring(1, 80, 10, 0)', // mass, stiffness, damping, velocity
  duration: 2000
})
```

### 阶梯缓动

```javascript
anime({
  targets: '.element',
  translateX: 250,
  easing: 'steps(5)',
  duration: 1000
})
```

### 自定义贝塞尔曲线

```javascript
anime({
  targets: '.element',
  translateX: 250,
  easing: 'cubicBezier(.5, .05, .1, .3)',
  duration: 1000
})
```

### 方向和循环

```javascript
anime({
  targets: '.element',
  translateX: 250,
  direction: 'alternate', // 'normal', 'reverse', 'alternate'
  loop: true,             // 或指定迭代次数
  easing: 'easeInOutQuad'
})
```

### 播放控制

```javascript
const animation = anime({
  targets: '.element',
  translateX: 250,
  autoplay: false
})

animation.play()
animation.pause()
animation.restart()
animation.reverse()
animation.seek(500) // 跳转到 500ms 处
```

## 性能优化

### 使用 transform 和 opacity

```javascript
// ✅ 推荐：GPU 加速
anime({
  targets: '.element',
  translateX: 250,
  opacity: 0.5
})

// ❌ 避免：触发重排
anime({
  targets: '.element',
  left: '250px',
  width: '500px'
})
```

### 批量处理相似动画

```javascript
// ✅ 对多个目标使用单个动画
anime({
  targets: '.multiple-elements',
  translateX: 250
})

// ❌ 避免：创建多个独立的动画
elements.forEach(el => {
  anime({ targets: el, translateX: 250 })
})
```

### 对复杂动画使用 `will-change`

```css
.animated-element {
  will-change: transform, opacity;
}
```

### 对滚动动画禁用自动播放

```javascript
const animation = anime({
  targets: '.element',
  translateX: 250,
  autoplay: false // 手动控制
})
```

## 常见陷阱

### 1. 忘记单位类型

```javascript
// ❌ 错误：没有单位
anime({ targets: '.element', width: 200 })

// ✅ 正确：包含单位
anime({ targets: '.element', width: '200px' })
```

### 2. 直接使用 CSS transform 属性

```javascript
// ❌ 错误：无法对 transform 字符串进行动画
anime({ targets: '.element', transform: 'translateX(250px)' })

// ✅ 正确：使用独立的变换属性
anime({ targets: '.element', translateX: 250 })
```

### 3. 未处理动画清理

```javascript
// ❌ 错误：组件卸载后动画仍在继续
useEffect(() => {
  anime({ targets: ref.current, translateX: 250 })
}, [])

// ✅ 正确：在清理函数中暂停
useEffect(() => {
  const anim = anime({ targets: ref.current, translateX: 250 })
  return () => anim.pause()
}, [])
```

### 4. 动画元素过多

```javascript
// ❌ 避免：动画 1000+ 个元素
anime({ targets: '.many-items', translateX: 250 }) // 1000+ 个元素

// ✅ 更好：对大量元素使用 CSS 动画
// 或通过虚拟化减少元素数量
```

### 5. 时间轴计时错误

```javascript
// ❌ 错误：缺少偏移运算符
.add({ targets: '.el2' }, '500') // 被当作绝对时间

// ✅ 正确：使用相对运算符
.add({ targets: '.el2' }, '-=500') // 相对于前一个动画
.add({ targets: '.el3' }, '+=200') // 相对于前一个动画
```

### 6. 过度使用循环

```javascript
// ❌ 避免：无限循环消耗电量
anime({
  targets: '.element',
  rotate: '1turn',
  loop: true,
  duration: 1000
})

// ✅ 更好：对无限循环使用 CSS 动画
@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

## 资源

### 脚本
- `animation_generator.py` - 生成 Anime.js 动画样板代码（8 种类型）
- `timeline_builder.py` - 构建复杂的时间轴序列

### 参考资料
- `api_reference.md` - 完整的 Anime.js API 文档
- `stagger_guide.md` - 交错工具和模式
- `timeline_guide.md` - 时间轴排序深度解析

### 资产
- `starter_animejs/` - 包含示例的原生 JS + Vite 模板
- `examples/` - 实际应用场景（SVG 变形、交错网格、时间轴）

## 相关技能

- **gsap-scrolltrigger** - 更强大的时间轴功能和滚动集成
- **motion-framer** - React 特有的声明式动画
- **react-spring-physics** - 基于物理的弹簧动画
- **lightweight-3d-effects** - 简单的 3D 效果（Zdog, Vanta.js）

**Anime.js 对比 GSAP**：当需要大量 SVG 动画、项目较简单或打包体积至关重要时，使用 Anime.js。当需要复杂的滚动驱动体验、高级时间轴和专业级控制时，使用 GSAP。

**Anime.js 对比 Framer Motion**：当项目框架无关或在 React 之外工作时，使用 Anime.js。当需要 React 特有的带手势集成的声明式动画时，使用 Framer Motion。
