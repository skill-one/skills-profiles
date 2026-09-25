# Anime.js

一款轻量级的 JavaScript 动画库，具有强大的时间轴和交错功能，用于网页动画。

## 概述

Anime.js（发音为 "Anime JS"）是一个通用的动画引擎，可与 DOM 元素、CSS 属性、SVG 属性和 JavaScript 对象一起使用。与特定于 React 的库不同，Anime.js 使用纯 JavaScript，并与任何框架一起工作。

**何时使用此技能：**
- 基于时间轴的动画序列，具有精确的编排
- 跨多个元素的交错动画
- SVG 路径变形和绘制动画
- 百分比时间的关键帧动画
- 框架无关的动画（适用于 React、Vue、纯 JavaScript）
- 复杂的缓动函数（弹簧、步进、cubic-bezier）

**核心功能：**
- 带相对定位的时间轴序列
- 强大的交错工具（网格、从中心、缓动）
- SVG 变形和路径动画
- 内置弹簧物理缓动
- 关键帧支持，具有灵活的时间
- 小的包大小（~9KB 压缩后）

## 核心概念

### 基本动画

`anime()` 函数创建动画：

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

指定动画目标的方法多种多样：

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

**CSS 变换（单个）：**
```javascript
anime({
  targets: '.element',
  translateX: 250,   // 单个变换
  rotate: '1turn',   // 不是 'transform: rotate()'
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

使用精确控制创建复杂序列：

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
  delay: anime.stagger(100), // 延迟增加 100ms
  easing: 'easeOutQuad',
  duration: 600
})
```

### 2. 从中心交错

```javascript
anime({
  targets: '.grid-item',
  scale: [0, 1],
  delay: anime.stagger(50, {
    grid: [14, 5],
    from: 'center', // 也：'first', 'last', index, [x, y]
    axis: 'x'       // 也：'y', null
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
    { value: 'M10 80 Q 77.5 10, 145 80' }, // 开始形状
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

### 与 React

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

### 与 Vue

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
  easing: 'spring(1, 80, 10, 0)', // 质量、刚度、阻尼、速度
  duration: 2000
})
```

### 步进缓动

```javascript
anime({
  targets: '.element',
  translateX: 250,
  easing: 'steps(5)',
  duration: 1000
})
```

### 自定义贝塞尔

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
  loop: true,             // 或迭代次数
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
animation.seek(500) // 跳转到 500ms
```

## 性能优化

### 使用变换和透明度

```javascript
// ✅ 好的：GPU 加速
anime({
  targets: '.element',
  translateX: 250,
  opacity: 0.5
})

// ❌ 避免：触发布局
anime({
  targets: '.element',
  left: '250px',
  width: '500px'
})
```

### 批量相似动画

```javascript
// ✅ 单个动画用于多个目标
anime({
  targets: '.multiple-elements',
  translateX: 250
})

// ❌ 避免：多个单独的动画
elements.forEach(el => {
  anime({ targets: el, translateX: 250 })
})
```

### 使用 `will-change` 进行复杂动画

```css
.animated-element {
  will-change: transform, opacity;
}
```

### 为滚动动画禁用自动播放

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
// ❌ 错误：无单位
anime({ targets: '.element', width: 200 })

// ✅ 正确：包含单位
anime({ targets: '.element', width: '200px' })
```

### 2. 直接使用 CSS 变换属性

```javascript
// ❌ 错误：不能动画变换字符串
anime({ targets: '.element', transform: 'translateX(250px)' })

// ✅ 正确：单个变换属性
anime({ targets: '.element', translateX: 250 })
```

### 3. 不处理动画清理

```javascript
// ❌ 错误：卸载后动画继续
useEffect(() => {
  anime({ targets: ref.current, translateX: 250 })
}, [])

// ✅ 正确：清理时暂停
useEffect(() => {
  const anim = anime({ targets: ref.current, translateX: 250 })
  return () => anim.pause()
}, [])
```

### 4. 动画太多元素

```javascript
// ❌ 避免：动画 1000+ 元素
anime({ targets: '.many-items', translateX: 250 }) // 1000+ 元素

// ✅ 更好：使用 CSS 动画进行大量元素
// 或使用虚拟化减少元素数量
```

### 5. 时间轴时间错误

```javascript
// ❌ 错误：缺少偏移运算符
.add({ targets: '.el2' }, '500') // 视为绝对时间

// ✅ 正确：使用相对运算符
.add({ targets: '.el2' }, '-=500') // 相对于前一个
.add({ targets: '.el3' }, '+=200') // 相对于前一个
```

### 6. 过度使用循环

```javascript
// ❌ 避免：无限循环耗尽电池
anime({
  targets: '.element',
  rotate: '1turn',
  loop: true,
  duration: 1000
})

// ✅ 更好：使用 CSS 动画进行无限循环
@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

## 资源

### 脚本
- `animation_generator.py` - 生成 Anime.js 动画模板（8 种类型）
- `timeline_builder.py` - 构建复杂时间轴序列

### 参考
- `api_reference.md` - 完整的 Anime.js API 文档
- `stagger_guide.md` - 交错工具和模式
- `timeline_guide.md` - 时间轴序列深入探讨

### 资产
- `starter_animejs/` - 纯 JavaScript + Vite 模板，带示例
- `examples/` - 真实世界模式（SVG 变形、交错网格、时间轴）

## 相关技能

- **gsap-scrolltrigger** - 更强大的时间轴功能和滚动集成
- **motion-framer** - React 特定的声明式动画
- **react-spring-physics** - 基于物理的弹簧动画
- **lightweight-3d-effects** - 简单的 3D 效果（Zdog, Vanta.js）

**Anime.js vs GSAP**：使用 Anime.js 用于 SVG 密集型动画、简单项目或当包大小很重要时。使用 GSAP 用于复杂的滚动驱动体验、高级时间轴和专业级控制。

**Anime.js vs Framer Motion**：使用 Anime.js 用于框架无关的项目或在外部使用时。使用 Framer Motion 用于 React 特定的声明式动画，带手势集成。
