# 轻量级 3D 效果技能

## 概述

本技能结合了三个强大的库，用于创建装饰性 3D 元素和微交互：
- **Zdog**: 设计师友好的矢量插图伪 3D 引擎
- **Vanta.js**: 基于 Three.js/p5.js 的动画 3D 背景
- **Vanilla-Tilt.js**: 响应鼠标/陀螺仪的平滑视差倾斜效果

## 何时使用此技能
- 无需重型框架即可添加装饰性 3D 插图
- 为英雄区域创建动画背景
- 在卡片/图像上实现微妙的视差倾斜效果
- 构建具有视觉深度的轻量级着陆页
- 添加增强用户体验且不影响性能的微交互

## Zdog - 伪 3D 插图

### 核心概念

Zdog 是一个伪 3D 引擎，它使用 Canvas 或 SVG 在 3D 空间中渲染扁平的圆形设计。

**主要特性：**
- 设计师友好的声明式 API
- 小文件大小（约 28kb 最小化）
- Canvas 或 SVG 渲染
- 内置拖动旋转
- 平滑动画

### 基本设置

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://unpkg.com/zdog@1/dist/zdog.dist.min.js"></script>
  <style>
    .zdog-canvas {
      display: block;
      margin: 0 auto;
      background: #FDB;
      cursor: move;
    }
  </style>
</head>
<body>
  <canvas class="zdog-canvas" width="240" height="240"></canvas>

  <script>
    let isSpinning = true;

    let illo = new Zdog.Illustration({
      element: '.zdog-canvas',
      zoom: 4,
      dragRotate: true,
      onDragStart: function() {
        isSpinning = false;
      },
    });

    // 添加形状
    new Zdog.Ellipse({
      addTo: illo,
      diameter: 20,
      translate: { z: 10 },
      stroke: 5,
      color: '#636',
    });

    new Zdog.Rect({
      addTo: illo,
      width: 20,
      height: 20,
      translate: { z: -10 },
      stroke: 3,
      color: '#E62',
      fill: true,
    });

    function animate() {
      illo.rotate.y += isSpinning ? 0.03 : 0;
      illo.updateRenderGraph();
      requestAnimationFrame(animate);
    }
    animate();
  </script>
</body>
</html>
```

### Zdog 形状

**基本形状：**

```javascript
// 圆形
new Zdog.Ellipse({
  addTo: illo,
  diameter: 80,
  stroke: 20,
  color: '#636',
});

// 矩形
new Zdog.Rect({
  addTo: illo,
  width: 80,
  height: 60,
  stroke: 10,
  color: '#E62',
  fill: true,
});

// 圆角矩形
new Zdog.RoundedRect({
  addTo: illo,
  width: 60,
  height: 40,
  cornerRadius: 10,
  stroke: 4,
  color: '#C25',
  fill: true,
});

// 多边形
new Zdog.Polygon({
  addTo: illo,
  radius: 40,
  sides: 5,
  stroke: 8,
  color: '#EA0',
  fill: true,
});

// 线条
new Zdog.Shape({
  addTo: illo,
  path: [
    { x: -40, y: 0 },
    { x: 40, y: 0 },
  ],
  stroke: 6,
  color: '#636',
});

// 贝塞尔曲线
new Zdog.Shape({
  addTo: illo,
  path: [
    { x: -40, y: -20 },
    {
      bezier: [
        { x: -40, y: 20 },
        { x: 40, y: 20 },
        { x: 40, y: -20 },
      ],
    },
  ],
  stroke: 4,
  color: '#C25',
  closed: false,
});
```

### Zdog 组

将形状组织成组以创建复杂的模型：

```javascript
// 创建组
let head = new Zdog.Group({
  addTo: illo,
  translate: { y: -40 },
});

// 向组添加形状
new Zdog.Ellipse({
  addTo: head,
  diameter: 60,
  stroke: 30,
  color: '#FED',
});

// 眼睛
new Zdog.Ellipse({
  addTo: head,
  diameter: 8,
  stroke: 4,
  color: '#333',
  translate: { x: -10, z: 15 },
});

new Zdog.Ellipse({
  addTo: head,
  diameter: 8,
  stroke: 4,
  color: '#333',
  translate: { x: 10, z: 15 },
});

// 嘴巴
new Zdog.Shape({
  addTo: head,
  path: [
    { x: -10, y: 0 },
    {
      bezier: [
        { x: -5, y: 5 },
        { x: 5, y: 5 },
        { x: 10, y: 0 },
      ],
    },
  ],
  stroke: 2,
  color: '#333',
  translate: { y: 5, z: 15 },
  closed: false,
});

// 旋转整个组
head.rotate.y = Math.PI / 4;
```

### Zdog 动画

```javascript
// 连续旋转
function animate() {
  illo.rotate.y += 0.03;
  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}
animate();

// 弹跳动画
let t = 0;
function bounceAnimate() {
  t += 0.05;
  illo.translate.y = Math.sin(t) * 20;
  illo.updateRenderGraph();
  requestAnimationFrame(bounceAnimate);
}
bounceAnimate();

// 带缓动的交互式旋转
let targetRotateY = 0;
let currentRotateY = 0;

document.addEventListener('mousemove', (event) => {
  targetRotateY = (event.clientX / window.innerWidth - 0.5) * Math.PI;
});

function smoothAnimate() {
  // 缓动到目标值
  currentRotateY += (targetRotateY - currentRotateY) * 0.1;
  illo.rotate.y = currentRotateY;
  illo.updateRenderGraph();
  requestAnimationFrame(smoothAnimate);
}
smoothAnimate();
```

---

## Vanta.js - 动画 3D 背景

### 核心概念

Vanta.js 提供了只需少量设置即可使用的动画 WebGL 背景，由 Three.js 或 p5.js 驱动。

**主要特性：**
- 14+ 动画效果（波浪、鸟类、网格、云朵等）
- 鼠标/触摸交互
- 可自定义颜色和设置
- 总大小约 120KB（包括 Three.js）
- 大多数设备上 60fps

### 基本设置

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    #vanta-bg {
      width: 100%;
      height: 100vh;
    }
    .content {
      position: relative;
      z-index: 1;
      color: white;
      text-align: center;
      padding: 100px 20px;
    }
  </style>
</head>
<body>
  <div id="vanta-bg">
    <div class="content">
      <h1>我的动画背景</h1>
      <p>内容放在这里</p>
    </div>
  </div>

  <!-- Three.js (必需) -->
  <script src="https://cdn.jsdelivr.net/npm/three@0.134.0/build/three.min.js"></script>

  <!-- Vanta.js 效果 -->
  <script src="https://cdn.jsdelivr.net/npm/vanta@0.5.24/dist/vanta.waves.min.js"></script>

  <script>
    VANTA.WAVES({
      el: "#vanta-bg",
      mouseControls: true,
      touchControls: true,
      gyroControls: false,
      minHeight: 200.00,
      minWidth: 200.00,
      scale: 1.00,
      scaleMobile: 1.00,
      color: 0x23153c,
      shininess: 30.00,
      waveHeight: 15.00,
      waveSpeed: 0.75,
      zoom: 0.65
    });
  </script>
</body>
</html>
```

### 可用效果

**1. WAVES** (Three.js)
```javascript
VANTA.WAVES({
  el: "#vanta-bg",
  color: 0x23153c,
  shininess: 30,
  waveHeight: 15,
  waveSpeed: 0.75,
  zoom: 0.65
});
```

**2. CLOUDS** (Three.js)
```javascript
VANTA.CLOUDS({
  el: "#vanta-bg",
  skyColor: 0x68b8d7,
  cloudColor: 0xadc1de,
  cloudShadowColor: 0x183550,
  sunColor: 0xff9919,
  sunGlareColor: 0xff6633,
  sunlightColor: 0xff9933,
  speed: 1.0
});
```

**3. BIRDS** (需要 p5.js)
```html
<script src="https://cdn.jsdelivr.net/npm/p5@1.4.0/lib/p5.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/vanta@0.5.24/dist/vanta.birds.min.js"></script>

<script>
  VANTA.BIRDS({
    el: "#vanta-bg",
    backgroundColor: 0x23153c,
    color1: 0xff0000,
    color2: 0x0000ff,
    birdSize: 1.5,
    wingSpan: 20,
    speedLimit: 5,
    separation: 40,
    alignment: 40,
    cohesion: 40,
    quantity: 3
  });
</script>
```

**4. NET** (Three.js)
```javascript
VANTA.NET({
  el: "#vanta-bg",
  color: 0x3fff00,
  backgroundColor: 0x23153c,
  points: 10,
  maxDistance: 20,
  spacing: 15,
  showDots: true
});
```

**5. CELLS** (需要 p5.js)
```javascript
VANTA.CELLS({
  el: "#vanta-bg",
  color1: 0x00ff00,
  color2: 0xff0000,
  size: 1.5,
  speed: 1.0,
  scale: 1.0
});
```

**6. FOG** (Three.js)
```javascript
VANTA.FOG({
  el: "#vanta-bg",
  highlightColor: 0xff3f81,
  midtoneColor: 0x1d004d,
  lowlightColor: 0x2b1a5e,
  baseColor: 0x000000,
  blurFactor: 0.6,
  speed: 1.0,
  zoom: 1.0
});
```

**其他效果：GLOBE, TRUNK, TOPOLOGY, DOTS, HALO, RINGS**

### 配置选项

```javascript
// 所有效果通用的选项
{
  el: "#element-id",              // 必需：目标元素
  mouseControls: true,             // 启用鼠标交互
  touchControls: true,             // 启用触摸交互
  gyroControls: false,             // 设备方向
  minHeight: 200.00,               // 最小高度
  minWidth: 200.00,                // 最小宽度
  scale: 1.00,                     // 尺寸比例
  scaleMobile: 1.00,               // 移动端比例

  // 颜色（十六进制数字，不是字符串）
  color: 0x23153c,
  backgroundColor: 0x000000,

  // 性能
  forceAnimate: false,             // 即使隐藏也强制动画

  // 特定于效果的选项因效果而异
}
```

### Vanta.js 方法

```javascript
// 初始化并存储引用
const vantaEffect = VANTA.WAVES({
  el: "#vanta-bg",
  // ... 选项
});

// 完成时销毁（对于 SPA 很重要）
vantaEffect.destroy();

// 动态更新选项
vantaEffect.setOptions({
  color: 0xff0000,
  waveHeight: 20
});

// 调整大小（通常自动）
vantaEffect.resize();
```

### React 集成

```jsx
import { useEffect, useRef, useState } from 'react';
import VANTA from 'vanta/dist/vanta.waves.min';
import * as THREE from 'three';

function VantaBackground() {
  const vantaRef = useRef(null);
  const [vantaEffect, setVantaEffect] = useState(null);

  useEffect(() => {
    if (!vantaEffect) {
      setVantaEffect(VANTA.WAVES({
        el: vantaRef.current,
        THREE: THREE,
        mouseControls: true,
        touchControls: true,
        color: 0x23153c,
        shininess: 30,
        waveHeight: 15,
        waveSpeed: 0.75
      }));
    }

    return () => {
      if (vantaEffect) vantaEffect.destroy();
    };
  }, [vantaEffect]);

  return (
    <div ref={vantaRef} style={{ width: '100%', height: '100vh' }}>
      <div className="content">
        <h1>React + Vanta.js</h1>
      </div>
    </div>
  );
}
```

---

## Vanilla-Tilt.js - 视差倾斜效果

### 核心概念

Vanilla-Tilt.js 添加了响应鼠标移动和设备方向的平滑 3D 倾斜效果。

**主要特性：**
- 轻量级（约 8.5kb 最小化）
- 无依赖
- 支持陀螺仪
- 可选眩光效果
- 平滑过渡

### 基本设置

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    .tilt-card {
      width: 300px;
      height: 400px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 15px;
      margin: 50px auto;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 24px;
      transform-style: preserve-3d;
    }

    .tilt-inner {
      transform: translateZ(60px);
    }
  </style>
</head>
<body>
  <div class="tilt-card" data-tilt>
    <div class="tilt-inner">Hover Me!</div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/vanilla-tilt@1.8.1/dist/vanilla-tilt.min.js"></script>
</body>
</html>
```

### 配置选项

```javascript
VanillaTilt.init(document.querySelector(".tilt-card"), {
  // 旋转
  max: 25,                    // 最大倾斜角度（度）
  reverse: false,             // 反向倾斜方向
  startX: 0,                  // 初始 X 轴倾斜（度）
  startY: 0,                  // 初始 Y 轴倾斜（度）

  // 外观
  perspective: 1000,          // 变换透视（较低值 = 更强烈的倾斜效果）
  scale: 1.1,                 // 悬停时缩放（1 = 无缩放）

  // 动画
  speed: 400,                 // 过渡速度（毫秒）
  transition: true,           // 启用平滑过渡
  easing: "cubic-bezier(.03,.98,.52,.99)",

  // 行为
  axis: null,                 // 限制为 "x" 或 "y" 轴
  reset: true,                // 鼠标离开时重置
  "reset-to-start": true,     // 重置到起始位置 vs [0,0]

  // 眩光效果
  glare: true,                // 启用眩光
  "max-glare": 0.5,          // 眩光不透明度（0-1）
  "glare-prerender": false,   // 预渲染眩光元素

  // 高级
  full-page-listening: false, // 监听整个页面
  gyroscope: true,            // 启用设备方向
  gyroscopeMinAngleX: -45,    // 最小 X 角度
  gyroscopeMaxAngleX: 45,     // 最大 X 角度
  gyroscopeMinAngleY: -45,    // 最小 Y 角度
  gyroscopeMaxAngleY: 45,     // 最大 Y 角度
  gyroscopeSamples: 10        // 校准样本数
});
```

### 高级示例

**带眩光效果的卡片：**

```html
<div class="tilt-card" data-tilt
     data-tilt-glare
     data-tilt-max-glare="0.3">
  <div class="tilt-inner">
    <h3>高级卡片</h3>
    <p>带眩光效果</p>
  </div>
</div>
```

**分层 3D 效果：**

```html
<style>
  .tilt-card {
    transform-style: preserve-3d;
  }
  .layer-1 {
    transform: translateZ(20px);
  }
  .layer-2 {
    transform: translateZ(40px);
  }
  .layer-3 {
    transform: translateZ(60px);
  }
</style>

<div class="tilt-card" data-tilt data-tilt-max="15">
  <div class="layer-1">背景</div>
  <div class="layer-2">中间层</div>
  <div class="layer-3">前景</div>
</div>
```

**程序化控制：**

```javascript
const element = document.querySelector(".tilt-card");

VanillaTilt.init(element, {
  max: 25,
  speed: 400,
  glare: true,
  "max-glare": 0.5
});

// 获取倾斜值
element.addEventListener("tiltChange", (e) => {
  console.log("Tilt:", e.detail);
});

// 程序化重置
element.vanillaTilt.reset();

// 销毁实例
element.vanillaTilt.destroy();

// 获取当前值
const values = element.vanillaTilt.getValues();
console.log(values); // { tiltX, tiltY, percentageX, percentageY, angle }
```

### React 集成

```jsx
import { useEffect, useRef } from 'react';
import VanillaTilt from 'vanilla-tilt';

function TiltCard({ children, options }) {
  const tiltRef = useRef(null);

  useEffect(() => {
    const element = tiltRef.current;

    VanillaTilt.init(element, {
      max: 25,
      speed: 400,
      glare: true,
      "max-glare": 0.5,
      ...options
    });

    return () => {
      element.vanillaTilt.destroy();
    };
  }, [options]);

  return (
    <div ref={tiltRef} className="tilt-card">
      {children}
    </div>
  );
}

// 使用方式
<TiltCard options={{ max: 30, scale: 1.1 }}>
  <h3>我的卡片</h3>
</TiltCard>
```

---

## 常见模式

### 模式 1：Vanta + 内容的英雄区域

```html
<section id="hero">
  <div class="hero-content">
    <h1>欢迎</h1>
    <p>动画背景与内容叠加</p>
    <button>开始使用</button>
  </div>
</section>

<style>
  #hero {
    position: relative;
    width: 100%;
    height: 100vh;
    overflow: hidden;
  }

  .hero-content {
    position: relative;
    z-index: 1;
    color: white;
    text-align: center;
    padding-top: 20vh;
  }
</style>

<script src="https://cdn.jsdelivr.net/npm/three@0.134.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/vanta@0.5.24/dist/vanta.waves.min.js"></script>

<script>
  VANTA.WAVES({
    el: "#hero",
    mouseControls: true,
    touchControls: true,
    color: 0x23153c,
    waveHeight: 20,
    waveSpeed: 1.0
  });
</script>
```

### 模式 2：Zdog 图标网格

```html
<div class="icon-grid">
  <canvas class="icon" width="120" height="120"></canvas>
  <canvas class="icon" width="120" height="120"></canvas>
  <canvas class="icon" width="120" height="120"></canvas>
</div>

<script src="https://unpkg.com/zdog@1/dist/zdog.dist.min.js"></script>

<script>
  document.querySelectorAll('.icon').forEach((canvas, index) => {
    let illo = new Zdog.Illustration({
      element: canvas,
      zoom: 3,
      dragRotate: true
    });

    // 为每个 canvas 创建不同的图标
    const icons = [
      createHeartIcon,
      createStarIcon,
      createCheckIcon
    ];

    icons[index](illo);

    function animate() {
      illo.rotate.y += 0.02;
      illo.updateRenderGraph();
      requestAnimationFrame(animate);
    }
    animate();
  });

  function createHeartIcon(illo) {
    new Zdog.Shape({
      addTo: illo,
      path: [
        { x: 0, y: -10 },
        {
          bezier: [
            { x: -20, y: -20 },
            { x: -20, y: 0 },
            { x: 0, y: 10 }
          ]
        },
      stroke: 6,
      color: '#E62',
      fill: true,
      closed: false
    });
  }
</script>
```

### 模式 3：倾斜卡片画廊

```html
<div class="card-gallery">
  <div class="card" data-tilt data-tilt-glare data-tilt-max-glare="0.3">
    <img src="product1.jpg" alt="产品 1">
    <h3>产品 1</h3>
  </div>

  <div class="card" data-tilt data-tilt-glare data-tilt-max-glare="0.3">
    <img src="product2.jpg" alt="产品 2">
    <h3>产品 2</h1>
  </div>

  <div class="card" data-tilt data-tilt-glare data-tilt-max-glare="0.3">
    <img src="product3.jpg" alt="产品 3">
    <h3>产品 3</h3>
  </div>
</div>

<style>
  .card-gallery {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr);
    gap: 30px;
    padding: 50px;
  }

  .card {
    background: white;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    transform-style: preserve-3d;
  }

  .card img {
    width: 100%;
    border-radius: 10px;
    transform: translateZ(40px);
  }

  .card h3 {
    margin-top: 15px;
    transform: translateZ(60px);
  }
</style>

<script src="https://cdn.jsdelivr.net/npm/vanilla-tilt@1.8.1/dist/vanilla-tilt.min.js"></script>
```

### 模式 4：组合效果 - Vanta 背景 + 倾斜卡片

```html
<div id="vanta-section">
  <div class="container">
    <h1>我们的服务</h1>

    <div class="services-grid">
      <div class="service-card" data-tilt data-tilt-scale="1.05">
        <div class="icon">🚀</div>
        <h3>快速</h3>
        <p>闪电般的性能</p>
      </div>

      <div class="service-card" data-tilt data-tilt-scale="1.05">
        <div class="icon">🎨</div>
        <h3>美观</h3>
        <p>惊人的视觉效果</p>
      </div>

      <div class="service-card" data-tilt data-tilt-scale="1.05">
        <div class="icon">💪</div>
        <h3>强大</h3>
        <p>功能丰富的平台</p>
      </div>
    </div>
  </div>
</div>

<script>
  // Vanta 背景
  VANTA.NET({
    el: "#vanta-section",
    color: 0x3fff00,
    backgroundColor: 0x23153c,
    points: 10,
    maxDistance: 20
  });

  // 倾斜卡片
  VanillaTilt.init(document.querySelectorAll(".service-card"), {
    max: 15,
    speed: 400,
    glare: true,
    "max-glare": 0.3
  });
</script>
```

---

## 性能最佳实践

### Zdog 优化

1. **限制形状数量**：保持总形状数量在 100 以下以获得 60fps 的流畅性
2. **使用组**：组织相关形状以便于管理
3. **优化动画循环**：仅在需要时调用 `updateRenderGraph()`
4. **Canvas vs SVG**：Canvas 对动画更快，SVG 对静态插图更合适

### Vanta.js 优化

1. **单个实例**：每个页面最多使用 1-2 个 Vanta 效果
2. **移动端回退**：在移动端禁用或使用静态背景
3. **卸载时销毁**：在 SPA 中始终调用 `.destroy()` 
4. **减少粒子数量**：降低 `points`, `quantity` 以获得更好的性能

```javascript
// 移动端检测和回退
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

if (!isMobile) {
  VANTA.WAVES({
    el: "#hero",
    // ... 选项
  });
} else {
  document.getElementById('hero').style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
}
```

### Vanilla-Tilt 优化

1. **限制实例**：仅对可见元素应用
2. **减少 `gyroscopeSamples`**：降低以获得更好的移动端性能
3. **在低端设备上禁用**：检查设备功能
4. **使用 CSS `will-change`**：提示浏览器进行变换

```css
.tilt-card {
  will-change: transform;
}
```

---

## 常见陷阱

### 陷阱 1：多个 Vanta 实例

**问题**：多个 Vanta 实例会导致性能问题

**解决方案**：仅使用一个效果，或按需加载每个区域的 Vanta 效果

```javascript
// Intersection Observer 以仅在可见时加载 Vanta
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting && !entry.target.vantaEffect) {
      entry.target.vantaEffect = VANTA.WAVES({
        el: entry.target,
        // ... 选项
      });
    }
  });
});

observer.observe(document.getElementById('hero'));
```

### 陷阱 2：SPA 中的内存泄漏

**问题**：Vanta/Tilt 在组件卸载时未销毁

**解决方案**：始终清理

```javascript
// React useEffect 清理
useEffect(() => {
  const effect = VANTA.WAVES({ el: vantaRef.current });

  return () => {
    effect.destroy(); // 重要!
  };
}, []);
```

### 陷阱 3：Zdog 无法渲染

**问题**：Canvas 看起来是空的

**原因**：
- 忘记调用 `updateRenderGraph()`
- Canvas 尺寸为 0
- 形状位于视图之外

**解决方案**:

```javascript
// 始终在形状更改后调用 updateRenderGraph()
illo.updateRenderGraph();

// 确保 canvas 有尺寸
<canvas width="240" height="240"></canvas>

// 检查形状位置是否在视图内
new Zdog.Ellipse({
  addTo: illo,
  diameter: 20,
  translate: { z: 0 }, // 靠近原点
});
```

### 陷阱 4：移动端无法工作

**问题**：倾斜效果在移动设备上无法响应

**解决方案**：启用陀螺仪控制

```javascript
VanillaTilt.init(element, {
  gyroscope: true,
  gyroscopeMinAngleX: -45,
  gyroscopeMaxAngleX: 45
});
```

### 陷阱 5：颜色格式混淆（Vanta.js）

**问题**：颜色不起作用

**原因**：Vanta.js 使用十六进制**数字**，不是字符串

```javascript
// ❌ 错误
color: "#23153c"

// ✅ 正确
color: 0x23153c
```

---

## 资源

**Zdog:**
- [Zdog 文档](https://zzz.dog/)
- [Zdog GitHub](https://github.com/metafizzy/zdog)
- [Zdog Codepen 示例](https://codepen.io/collection/DzdGMe/)

**Vanta.js:**
- [Vanta.js 官方网站](https://www.vantajs.com/)
- [Vanta.js GitHub](https://github.com/tengbao/vanta)
- [效果自定义器](https://www.vantajs.com/?effect=waves)

**Vanilla-Tilt.js:**
- [Vanilla-Tilt GitHub](https://github.com/micku7zu/vanilla-tilt.js)
- [NPM 包](https://www.npmjs.com/package/vanilla-tilt)

## 相关技能

- **threejs-webgl**: 用于比装饰性效果更复杂的 3D 图形
- **gsap-scrolltrigger**: 用于滚动时动画化这些效果
- **motion-framer**: 用于 React 组件动画
- **react-three-fiber**: 当轻量级效果不够用时的高级 3D
