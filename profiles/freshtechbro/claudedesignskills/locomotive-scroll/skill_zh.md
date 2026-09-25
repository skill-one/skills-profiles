# Locomotive Scroll

使用 Locomotive Scroll 实现平滑滚动、视差效果和滚动触发的动画的综合指南。

## 概述

Locomotive Scroll 是一个 JavaScript 库，提供：
- **平滑滚动**：硬件加速的平滑滚动，支持自定义缓动效果
- **视差效果**：元素级别的速度控制，实现深度效果
- **视口检测**：跟踪元素进入/退出视口的状态
- **滚动事件**：监控滚动进度，用于动画同步
- **粘性元素**：在定义的边界内固定元素位置
- **水平滚动**：支持水平滚动布局

**何时使用 Locomotive Scroll：**
- 构建具有视差效果的沉浸式着陆页
- 创建平滑的、类似苹果风格的滚动体验
- 实现滚动触发的动画
- 开发叙事/故事讲述网站
- 为长格式内容添加深度和动效

**权衡：**
- 滚动劫持可能影响可访问性（提供禁用选项）
- 低端设备上的性能开销（检测并禁用）
- 移动端触摸滚动感觉不同（广泛测试）
- 固定定位需要处理兼容性问题

## 安装

```bash
npm install locomotive-scroll
```

```javascript
// ES6
import LocomotiveScroll from 'locomotive-scroll';
import 'locomotive-scroll/dist/locomotive-scroll.css';

// 或通过 CDN
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/locomotive-scroll/dist/locomotive-scroll.min.css">
<script src="https://cdn.jsdelivr.net/npm/locomotive-scroll/dist/locomotive-scroll.min.js"></script>
```

## 核心概念

### 1. HTML 结构

每个 Locomotive Scroll 实现都需要特定的数据属性：

```html
<!-- 滚动容器（必需） -->
<div data-scroll-container>

  <!-- 滚动区域（可选，可提高性能） -->
  <div data-scroll-section>

    <!-- 跟踪元素 -->
    <h1 data-scroll>基本检测</h1>

    <!-- 视差元素 -->
    <div data-scroll data-scroll-speed="2">
      滚动速度更快
    </div>

    <!-- 粘性元素 -->
    <div data-scroll data-scroll-sticky>
      在区域内固定
    </div>

    <!-- 带有 ID 的元素，用于跟踪 -->
    <div data-scroll data-scroll-id="hero">
      可通过 JavaScript 访问
    </div>

    <!-- 事件触发器 -->
    <div data-scroll data-scroll-call="fadeIn">
      触发自定义事件
    </div>

  </div>
</div>
```

### 2. 初始化

```javascript
const scroll = new LocomotiveScroll({
  el: document.querySelector('[data-scroll-container]'),
  smooth: true,
  lerp: 0.1,        // 平滑度（0-1，值越小越平滑）
  multiplier: 1,    // 速度倍数
  class: 'is-inview', // 添加到可见元素的类名
  repeat: false,    // 重复检测可见状态
  offset: [0, 0]    // 全局触发偏移 [底部, 顶部]
});
```

### 3. 数据属性

| 属性         | 目的               | 示例                     |
|--------------|--------------------|--------------------------|
| `data-scroll` | 启用检测         | `data-scroll`            |
| `data-scroll-speed` | 视差速度         | `data-scroll-speed="2"`  |
| `data-scroll-direction` | 视差轴         | `data-scroll-direction="horizontal"` |
| `data-scroll-sticky` | 粘性定位         | `data-scroll-sticky`     |
| `data-scroll-target` | 粘性边界         | `data-scroll-target="#section"` |
| `data-scroll-offset` | 触发偏移         | `data-scroll-offset="20%"` |
| `data-scroll-repeat` | 重复检测         | `data-scroll-repeat`     |
| `data-scroll-call` | 事件触发         | `data-scroll-call="myFunction"` |
| `data-scroll-id` | 唯一标识符       | `data-scroll-id="hero"`  |
| `data-scroll-class` | 自定义类         | `data-scroll-class="is-visible"` |

## 常见模式

### 1. 基本平滑滚动

```javascript
import LocomotiveScroll from 'locomotive-scroll';

const scroll = new LocomotiveScroll({
  el: document.querySelector('[data-scroll-container]'),
  smooth: true
});
```

```html
<div data-scroll-container>
  <div data-scroll-section>
    <h1>已启用平滑滚动</h1>
  </div>
</div>
```

### 2. 视差效果

```html
<!-- 慢速视差 -->
<div data-scroll data-scroll-speed="0.5">
  滚动速度更慢（背景效果）
</div>

<!-- 快速视差 -->
<div data-scroll data-scroll-speed="3">
  滚动速度更快（前景效果）
</div>

<!-- 反向视差 -->
<div data-scroll data-scroll-speed="-2">
  向相反方向移动
</div>

<!-- 水平视差 -->
<div data-scroll data-scroll-speed="2" data-scroll-direction="horizontal">
  水平移动
</div>
```

### 3. 视口检测和回调

```javascript
// 跟踪滚动进度
scroll.on('scroll', (args) => {
  console.log(args.scroll.y); // 当前滚动位置
  console.log(args.speed);    // 滚动速度
  console.log(args.direction); // 滚动方向

  // 访问特定元素进度
  if (args.currentElements['hero']) {
    const progress = args.currentElements['hero'].progress;
    console.log(`Hero 进度: ${progress}`); // 0 到 1
  }
});

// 触发事件
scroll.on('call', (value, way, obj) => {
  console.log(`触发事件: ${value}`);
  // value = data-scroll-call 属性值
  // way = 'enter' 或 'exit'
  // obj = {id, el}
});
```

```html
<div data-scroll data-scroll-id="hero">英雄区域</div>
<div data-scroll data-scroll-call="playVideo">视频区域</div>
```

### 4. 粘性元素

```html
<!-- 在父区域内粘性 -->
<div data-scroll-section>
  <div data-scroll data-scroll-sticky>
    在区域可见时粘性
  </div>
</div>

<!-- 带有特定目标的粘性 -->
<div id="sticky-container">
  <div data-scroll data-scroll-sticky data-scroll-target="#sticky-container">
    在 #sticky-container 内粘性
  </div>
</div>
```

### 5. 程序化滚动

```javascript
// 滚动到元素
scroll.scrollTo('#target-section');

// 滚动到顶部
scroll.scrollTo('top');

// 滚动到底部
scroll.scrollTo('bottom');

// 带选项的滚动
scroll.scrollTo('#target', {
  offset: -100,      // 像素偏移
  duration: 1000,    // 持续时间（毫秒）
  easing: [0.25, 0.0, 0.35, 1.0], // 贝塞尔曲线
  disableLerp: true, // 禁用平滑插值
  callback: () => console.log('已滚动!')
});

// 滚动到像素值
scroll.scrollTo(500);
```

### 6. 水平滚动

```javascript
const scroll = new LocomotiveScroll({
  el: document.querySelector('[data-scroll-container]'),
  smooth: true,
  direction: 'horizontal'
});
```

```html
<div data-scroll-container>
  <div data-scroll-section style="display: flex; width: 300vw;">
    <div>区域 1</div>
    <div>区域 2</div>
    <div>区域 3</div>
  </div>
</div>
```

### 7. 移动端响应式

```javascript
const scroll = new LocomotiveScroll({
  el: document.querySelector('[data-scroll-container]'),
  smooth: true,

  // 平板设置
  tablet: {
    smooth: true,
    breakpoint: 1024
  },

  // 手机设置
  smartphone: {
    smooth: false, // 为性能禁用
    breakpoint: 768
  }
});
```

## 与 GSAP ScrollTrigger 集成

Locomotive Scroll 和 GSAP ScrollTrigger 可协同工作实现高级动画：

```javascript
import LocomotiveScroll from 'locomotive-scroll';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const locoScroll = new LocomotiveScroll({
  el: document.querySelector('[data-scroll-container]'),
  smooth: true
});

// 同步 Locomotive Scroll 与 ScrollTrigger
locoScroll.on('scroll', ScrollTrigger.update);

ScrollTrigger.scrollerProxy('[data-scroll-container]', {
  scrollTop(value) {
    return arguments.length
      ? locoScroll.scrollTo(value, 0, 0)
      : locoScroll.scroll.instance.scroll.y;
  },
  getBoundingClientRect() {
    return {
      top: 0,
      left: 0,
      width: window.innerWidth,
      height: window.innerHeight
    };
  },
  pinType: document.querySelector('[data-scroll-container]').style.transform
    ? 'transform'
    : 'fixed'
});

// GSAP 动画与 ScrollTrigger
gsap.to('.fade-in', {
  scrollTrigger: {
    trigger: '.fade-in',
    scroller: '[data-scroll-container]',
    start: 'top bottom',
    end: 'top center',
    scrub: true
  },
  opacity: 1,
  y: 0
});

// 当 Locomotive 更新时刷新 ScrollTrigger
ScrollTrigger.addEventListener('refresh', () => locoScroll.update());
ScrollTrigger.refresh();
```

## 实例方法

```javascript
const scroll = new LocomotiveScroll();

// 生命周期
scroll.init();     // 重新初始化
scroll.update();   // 刷新元素位置
scroll.destroy();  // 清理
scroll.start();    // 恢复滚动
scroll.stop();     // 暂停滚动

// 导航
scroll.scrollTo(target, options);
scroll.setScroll(x, y);

// 事件
scroll.on('scroll', callback);
scroll.on('call', callback);
scroll.off('scroll', callback);
```

## 性能优化

1. **使用 `data-scroll-section`** 分段长页面：
```html
<div data-scroll-container>
  <div data-scroll-section>区域 1</div>
  <div data-scroll-section>区域 2</div>
  <div data-scroll-section>区域 3</div>
</div>
```

2. **限制视差元素** - 太多会影響性能

3. **在移动端禁用** 如果性能较差：
```javascript
smartphone: { smooth: false }
```

4. **调整大小后更新**：
```javascript
window.addEventListener('resize', () => {
  scroll.update();
});
```

5. **不需要时销毁**：
```javascript
scroll.destroy();
```

## 常见陷阱

### 1. 固定定位问题

**问题**：`position: fixed` 元素与平滑滚动冲突

**解决方案**：使用 `data-scroll-sticky` 或将固定元素放在容器外：
```html
<!-- 容器外的固定导航 -->
<nav style="position: fixed;">导航</nav>

<div data-scroll-container>
  <!-- 页面内容 -->
</div>
```

### 2. 图片未懒加载

**问题**：所有图片一次性加载

**解决方案**：集成懒加载：
```html
<img data-scroll data-src="image.jpg" class="lazy">
```

```javascript
scroll.on('call', (func) => {
  if (func === 'lazyLoad') {
    // 触发懒加载
  }
});
```

### 3. 滚动位置未更新

**问题**：动态内容未更新滚动位置

**解决方案**：DOM 变更后调用 `update()`：
```javascript
// 添加动态内容后
addDynamicContent();
scroll.update();
```

### 4. 可访问性问题

**问题**：屏幕阅读器和键盘导航失效

**解决方案**：提供禁用选项：
```javascript
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const scroll = new LocomotiveScroll({
  smooth: !prefersReducedMotion
});
```

### 5. 内存泄漏

**问题**：滚动实例未在路由变化时清理（单页应用）

**解决方案**：卸载时始终销毁：
```javascript
// React 示例
useEffect(() => {
  const scroll = new LocomotiveScroll();

  return () => scroll.destroy();
}, []);
```

### 6. Z-轴冲突

**问题**：视差层重叠错误

**解决方案**：设置显式 z-index：
```css
[data-scroll-speed] {
  position: relative;
  z-index: var(--layer-depth);
}
```

## 相关技能

- **gsap-scrolltrigger**：高级滚动驱动动画（可协同使用）
- **barba-js**：带 Locomotive Scroll 集成的页面过渡
- **scroll-reveal-libraries**：用于基本淡入效果的简单替代方案
- **react-three-fiber**：滚动驱动的 3D 场景（同步 Locomotive 事件）
- **motion-framer**：React 中的替代滚动动画

## 资源

- **脚本**：`generate_config.py` - 配置生成器，`integration_helper.py` - GSAP 集成代码
- **参考**：`api_reference.md` - 完整 API，`gsap_integration.md` - GSAP ScrollTrigger 模式
- **资源**：`starter_locomotive/` - 带示例的完整启动模板
