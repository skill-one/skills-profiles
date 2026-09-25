# 滚动揭示库

## 概述

本技能涵盖 AOS（滚动触发动画），一个轻量级的基于 CSS 的滚动触发动画库。AOS 擅长在元素进入视口时触发的简单淡入、滑动和缩放效果。

**主要特性**：
- **极简设置**：单个 JavaScript 文件 + CSS
- **数据属性 API**：在 HTML 中配置动画
- **性能**：基于 CSS 的 GPU 加速动画
- **50+ 内置动画**：淡入、滑动、缩放、翻转
- **框架无关**：可与原生 JS、React、Vue 等配合使用

**何时使用**：
- 具有简单滚动效果的营销/着陆页
- 内容密集型网站（博客、文档）
- 需要滚动动画的快速原型
- 不需要 GSAP/Framer Motion 复杂性的项目

**何时不建议使用**：
- 复杂的动画时间线或编排 → 使用 GSAP ScrollTrigger
- 基于物理的动画 → 使用 React Spring 或 Framer Motion
- 精确的滚动同步动画 → 使用 GSAP ScrollTrigger
- 重型交互式动画 → 使用 Framer Motion

## 核心概念

### 安装

**CDN（最快）**：
```html
<head>
  <link rel="stylesheet" href="https://unpkg.com/aos@next/dist/aos.css" />
</head>
<body>
  <!-- 带有 data-aos 属性的内容 -->

  <script src="https://unpkg.com/aos@next/dist/aos.js"></script>
  <script>
    AOS.init();
  </script>
</body>
```

**NPM/Yarn（推荐）**：
```bash
npm install aos@next
# 或
yarn add aos@next
```

```javascript
import AOS from 'aos';
import 'aos/dist/aos.css';

AOS.init();
```

### 基本用法

使用 `data-aos` 属性应用动画：

```html
<!-- 淡入 -->
<div data-aos="fade-in">内容</div>

<!-- 淡上 -->
<div data-aos="fade-up">内容</div>

<!-- 从右侧滑动 -->
<div data-aos="slide-left">内容</div>

<!-- 缩放 -->
<div data-aos="zoom-in">内容</div>
```

### 配置选项

**全局配置**：
```javascript
AOS.init({
  // 动画设置
  duration: 800,  // 动画持续时间（毫秒）：0-3000
  delay: 0,       // 动画延迟（毫秒）：0-3000
  offset: 120,    // 触发点偏移（像素）
  easing: 'ease', // 缓动函数
  once: false,    // 仅动画一次（true）或每次（false）
  mirror: false,  // 滚动经过时反向动画

  // 位置
  anchorPlacement: 'top-bottom', // 触发动画的位置

  // 性能
  disable: false,                // 在移动设备/平板上禁用
  startEvent: 'DOMContentLoaded', // 初始化事件
  debounceDelay: 50,             // 窗口调整大小防抖
  throttleDelay: 99              // 滚动节流
});
```

**单个元素覆盖**：
```html
<div
  data-aos="fade-up"
  data-aos-duration="1000"
  data-aos-delay="200"
  data-aos-offset="50"
  data-aos-easing="ease-in-out"
  data-aos-once="true"
  data-aos-mirror="true"
  data-aos-anchor-placement="center-bottom"
>
  自定义配置元素
</div>
```

## 常见模式

### 1. 着陆页英雄区域

```html
<section class="hero">
  <!-- 错落有致的标题文字 -->
  <h1
    data-aos="fade-down"
    data-aos-duration="800"
  >
    欢迎来到未来
  </h1>

  <!-- 延迟的副标题 -->
  <p
    data-aos="fade-up"
    data-aos-delay="200"
    data-aos-duration="600"
  >
    将您的想法变为现实
  </p>

  <!-- CTA 按钮 -->
  <button
    data-aos="zoom-in"
    data-aos-delay="400"
    data-aos-duration="500"
  >
    立即开始
  </button>
</section>
```

### 2. 功能卡片网格

```html
<div class="features-grid">
  <!-- 错落有致地排列卡片，延迟递增 -->
  <div
    class="feature-card"
    data-aos="fade-up"
    data-aos-duration="600"
    data-aos-delay="0"
  >
    <h3>功能 1</h3>
    <p>描述...</p>
  </div>

  <div
    class="feature-card"
    data-aos="fade-up"
    data-aos-duration="600"
    data-aos-delay="100"
  >
    <h3>功能 2</h3>
    <p>描述...</p>
  </div>

  <div
    class="feature-card"
    data-aos="fade-up"
    data-aos-duration="600"
    data-aos-delay="200"
  >
    <h3>功能 3</h3>
    <p>描述...</p>
  </div>
</div>
```

### 3. 交替内容区域

```html
<!-- 从左侧进入的内容 -->
<div class="section">
  <div
    class="content"
    data-aos="slide-right"
    data-aos-duration="800"
  >
    <h2>区域标题</h2>
    <p>内容从左侧滑入...</p>
  </div>
  <img
    src="image1.jpg"
    data-aos="fade-left"
    data-aos-delay="200"
  />
</div>

<!-- 从右侧进入的内容 -->
<div class="section reverse">
  <img
    src="image2.jpg"
    data-aos="fade-right"
  />
  <div
    class="content"
    data-aos="slide-left"
    data-aos-duration="800"
    data-aos-delay="200"
  >
    <h2>区域标题</h2>
    <p>内容从右侧滑入...</p>
  </div>
</div>
```

### 4. 滚动触发的客户评价

```html
<div class="testimonials">
  <div
    class="testimonial"
    data-aos="zoom-in"
    data-aos-duration="500"
  >
    <blockquote>"惊人的产品！"</blockquote>
    <cite>- 约翰·多伊</cite>
  </div>

  <div
    class="testimonial"
    data-aos="zoom-in"
    data-aos-duration="500"
    data-aos-delay="100"
  >
    <blockquote>"超出了预期"</blockquote>
    <cite>- 简·史密斯</cite>
  </div>
</div>
```

### 5. 自定义锚点触发

基于不同元素的滚动位置触发动画：

```html
<!-- 固定侧边栏根据主内容的滚动而动画 -->
<div class="main-content">
  <div id="trigger-point" data-aos-id="sidebar-trigger">
    <!-- 内容 -->
  </div>
</div>

<aside
  class="sidebar"
  data-aos="fade-left"
  data-aos-anchor="#trigger-point"
>
  侧边栏内容
</aside>
```

### 6. 顺序动画链

```html
<div class="animation-sequence">
  <!-- 步骤 1：标题 -->
  <h2
    data-aos="fade-down"
    data-aos-duration="600"
    data-aos-delay="0"
  >
    我们的过程
  </h2>

  <!-- 步骤 2：描述 -->
  <p
    data-aos="fade-up"
    data-aos-duration="600"
    data-aos-delay="200"
  >
    跟随这些简单步骤
  </p>

  <!-- 步骤 3-5：过程卡片 -->
  <div
    class="process-step"
    data-aos="flip-left"
    data-aos-delay="400"
  >
    步骤 1
  </div>

  <div
    class="process-step"
    data-aos="flip-left"
    data-aos-delay="600"
  >
    步骤 2
  </div>

  <div
    class="process-step"
    data-aos="flip-left"
    data-aos-delay="800"
  >
    步骤 3
  </div>
</div>
```

### 7. 带缩放效果的照片库

```html
<div class="gallery">
  <img
    src="photo1.jpg"
    data-aos="zoom-in-up"
    data-aos-duration="800"
  />
  <img
    src="photo2.jpg"
    data-aos="zoom-in-up"
    data-aos-duration="800"
    data-aos-delay="100"
  />
  <img
    src="photo3.jpg"
    data-aos="zoom-in-up"
    data-aos-duration="800"
    data-aos-delay="200"
  />
</div>
```

## 集成模式

### React 集成

**基本设置**：
```jsx
import { useEffect } from 'react';
import AOS from 'aos';
import 'aos/dist/aos.css';

function App() {
  useEffect(() => {
    AOS.init({
      duration: 800,
      once: true,
      offset: 100
    });
  }, [];

  return (
    <div>
      <h1 data-aos="fade-down">欢迎</h1>
      <p data-aos="fade-up">内容在此</p>
    </div>
  );
}
```

**路由变化时刷新**：
```jsx
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import AOS from 'aos';

function App() {
  const location = useLocation();

  useEffect(() => {
    AOS.init({ duration: 800 });
  }, []);

  // 路由变化时刷新 AOS
  useEffect(() => {
    AOS.refresh();
  }, [location.pathname]);

  return <Routes>{/* 路由 */}</Routes>;
}
```

**动态内容更新**：
```jsx
import { useState, useEffect } from 'react';
import AOS from 'aos';

function DynamicList() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    AOS.init();
  }, [];

  const addItem = () => {
    setItems([...items, { id: Date.now(), text: '新项目' }]);

    // 刷新 AOS 以检测新元素
    setTimeout(() => AOS.refresh(), 50);
  };

  return (
    <div>
      <button onClick={addItem}>添加项目</button>
      <ul>
        {items.map((item) => (
          <li key={item.id} data-aos="fade-in">
            {item.text}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

**组件包装模式**：
```jsx
import AOS from 'aos';
import 'aos/dist/aos.css';

function AnimatedSection({ children, animation = "fade-up", delay = 0, ...props }) {
  return (
    <div
      data-aos={animation}
      data-aos-delay={delay}
      {...props}
    >
      {children}
    </div>
  );
}

// 使用
<AnimatedSection animation="slide-right" delay={200}>
  <h2>动画内容</h2>
</AnimatedSection>
```

### Vue.js 集成

```vue
<template>
  <div>
    <h1 data-aos="fade-down">Vue + AOS</h1>
    <div
      v-for="(item, index) in items"
      :key="item.id"
      data-aos="fade-up"
      :data-aos-delay="index * 100"
    >
      {{ item.text }}
    </div>
  </div>
</template>

<script>
import AOS from 'aos';
import 'aos/dist/aos.css';

export default {
  mounted() {
    AOS.init({ duration: 800 });
  },
  updated() {
    // 组件更新时刷新
    this.$nextTick(() => {
      AOS.refresh();
    });
  },
  data() {
    return {
      items: [/*...*/]
    };
  }
};
</script>
```

### Next.js 集成

```jsx
// pages/_app.js
import { useEffect } from 'react';
import AOS from 'aos';
import 'aos/dist/aos.css';

function MyApp({ Component, pageProps }) {
  useEffect(() => {
    AOS.init({
      duration: 800,
      once: true
    });
  }, [];

  return <Component {...pageProps} />;
}

export default MyApp;
```

```jsx
// pages/index.js
export default function Home() {
  return (
    <main>
      <h1 data-aos="fade-down">Next.js + AOS</h1>
      <p data-aos="fade-up">服务器端渲染的内容带动画</p>
    </main>
  );
}
```

## 性能优化

### 1. 在移动设备上禁用

```javascript
AOS.init({
  disable: 'mobile', // 在移动设备上禁用
  // 或使用函数进行自定义逻辑
  disable: function() {
    return window.innerWidth < 768;
  }
});
```

### 2. 使用 Once 以获得更好的性能

```javascript
AOS.init({
  once: true, // 仅动画一次（更好的性能）
  mirror: false // 不要反向动画
});
```

### 3. 优化 Throttle 和 Debounce

```javascript
AOS.init({
  throttleDelay: 99,  // 滚动事件节流（默认）
  debounceDelay: 50   // 调整大小事件防抖（默认）
});
```

### 4. 静态内容禁用 Mutation Observer

```javascript
AOS.init({
  disableMutationObserver: true // 静态内容禁用
});
```

### 5. 减少动画复杂度

```html
<!-- 简单的动画性能更好 -->
<div data-aos="fade-in">简单淡入</div>

<!-- 复杂的动画可能导致卡顿 -->
<div data-aos="flip-left">复杂的翻转</div>
```

### 6. 使用 RequestIdleCallback 进行初始化

```javascript
if ('requestIdleCallback' in window) {
  requestIdleCallback(() => {
    AOS.init({ duration: 800 });
  });
} else {
  AOS.init({ duration: 800 });
}
```

## 常见陷阱

### 1. 忘记在 DOM 变化后刷新

**问题**：动态添加的新元素不会动画。

**解决方案**：调用 `AOS.refresh()` 或 `AOS.refreshHard()`：

```javascript
// 添加元素到 DOM 后
const newElement = document.createElement('div');
newElement.setAttribute('data-aos', 'fade-in');
container.appendChild(newElement);

// 刷新 AOS
AOS.refresh(); // 重新计算位置
// 或
AOS.refreshHard(); // 完全重新初始化
```

### 2. React 中动画不工作

**问题**：AOS 在首次渲染或路由变化时无法检测到元素。

**解决方案**：在 `useEffect` 中初始化并在路由/内容变化时刷新：

```jsx
useEffect(() => {
  AOS.init();
  return () => AOS.refresh(); // 清理
}, []);

useEffect(() => {
  AOS.refresh(); // 路由变化时刷新
}, [location.pathname]);
```

### 3. 滚动性能问题

**问题**：带有许多动画元素时页面滚动感觉卡顿。

**解决方案**：减少动画元素并使用 `once: true`：

```javascript
AOS.init({
  once: true, // 仅动画一次
  disable: window.innerWidth < 768 // 在移动设备上禁用
});
```

### 4. CSS 冲突

**问题**：自定义 CSS 干扰 AOS 动画。

**解决方案**：使用更具体的选择器并避免 `!important`：

```css
/* 坏：与 AOS 冲突 */
div {
  opacity: 1 !important;
}

/* 好：具体选择器 */
.my-content > div {
  /* 样式 */
}
```

### 5. 锚点位置混淆

**问题**：动画在预期外的滚动位置触发。

**解决方案**：理解锚点位置选项：

```javascript
// 当元素顶部到达视口底部时触发
data-aos-anchor-placement="top-bottom"

// 当元素中心到达视口中心时触发
data-aos-anchor-placement="center-center"

// 当元素底部到达视口顶部时触发
data-aos-anchor-placement="bottom-top"
```

### 6. Duration/Delay 限制

**问题**：值超过 3000ms 不起作用。

**解决方案**：添加自定义 CSS 以延长持续时间：

```css
body[data-aos-duration='4000'] [data-aos],
[data-aos][data-aos][data-aos-duration='4000'] {
  transition-duration: 4000ms;
}
```

```html
<div data-aos="fade-in" data-aos-duration="4000">
  长动画
</div>
```

## 内置动画

### 淡入动画
- `fade-in` - 简单淡入
- `fade-up` - 从底部淡入
- `fade-down` - 从顶部淡入
- `fade-left` - 从右侧淡入
- `fade-right` - 从左侧淡入
- `fade-up-right` - 对角线淡入
- `fade-up-left` - 对角线淡入
- `fade-down-right` - 对角线淡入
- `fade-down-left` - 对角线淡入

### 滑动动画
- `slide-up` - 从底部滑动
- `slide-down` - 从顶部滑动
- `slide-left` - 从右侧滑动
- `slide-right` - 从左侧滑动

### 缩放动画
- `zoom-in` - 缩放
- `zoom-in-up` - 从底部缩放
- `zoom-in-down` - 从顶部缩放
- `zoom-in-left` - 从右侧缩放
- `zoom-in-right` - 从左侧缩放
- `zoom-out` - 缩放
- `zoom-out-up` - 缩放到顶部
- `zoom-out-down` - 缩放到底部
- `zoom-out-left` - 缩放到左侧
- `zoom-out-right` - 缩放到右侧

### 翻转动画
- `flip-up` - 从底部翻转
- `flip-down` - 从顶部翻转
- `flip-left` - 从右侧翻转
- `flip-right` - 从左侧翻转

## 自定义动画

使用 CSS 创建自定义动画：

```css
[data-aos="custom-slide-bounce"] {
  opacity: 0;
  transform: translateY(100px);
  transition-property: transform, opacity;
}

[data-aos="custom-slide-bounce"].aos-animate {
  opacity: 1;
  transform: translateY(0);
  animation: bounce 0.5s;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}
```

```html
<div data-aos="custom-slide-bounce">
  自定义动画
</div>
```

## 与替代方案的比较

### AOS 与 GSAP ScrollTrigger

| 特性 | AOS | GSAP ScrollTrigger |
|------|-----|-------------------|
| **复杂度** | 简单，基于数据属性 | 高级，JavaScript API |
| **用例** | 简单揭示 | 复杂时间线 |
| **文件大小** | ~13KB | ~27KB (GSAP) + ScrollTrigger |
| **性能** | 基于CSS | 基于JavaScript |
| **学习曲线** | 分钟 | 小时 |
| **自定义** | 有限 | 广泛 |
| **适合** | 营销页面 | 交互式体验 |

**使用 AOS 当**：
- 简单的淡入/滑动/缩放效果
- 需要快速实现
- 偏好少量JavaScript
- 基本滚动揭示足够

**使用 GSAP ScrollTrigger 当**：
- 复杂的动画序列
- 精确的滚动同步动画
- 需要时间线编排
- 需要高级缓动/物理效果

## 资源

### 官方文档
- **AOS**：https://michalsnik.github.io/aos/
- **GitHub**：https://github.com/michalsnik/aos

### 关键脚本
- `scripts/aos_generator.py` - 生成 AOS HTML 模板
- `scripts/config_builder.py` - 构建AOS配置

### 参考
- `references/aos_api.md` - 完整 AOS API 参考
- `references/animation_catalog.md` - 所有内置动画及演示
- `references/integration_patterns.md` - 框架集成指南

### 启动资源
- `assets/starter_aos/` - 完整 AOS 启动模板
- `assets/examples/` - 生产就绪模式

## 相关技能

- **gsap-scrolltrigger**：用于复杂滚动驱动动画
- **motion-framer**：用于React特定的带物理动画
- **locomotive-scroll**：用于平滑滚动及视差效果
- **animated-component-libraries**：用于预构建的React动画组件
