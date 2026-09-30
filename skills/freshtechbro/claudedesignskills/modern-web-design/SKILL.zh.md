---
name: modern-web-design
description: 2024-2025年现代网页设计趋势、原则及实现模式。在设计网站、创建交互体验、实施设计系统、确保可访问性或构建性能优先界面时使用此技能。在涉及现代设计趋势、微交互、滚动叙事、大胆极简主义、光标UX、玻璃态设计、可访问性合规、性能优化或设计系统架构的任务上触发。参考动画技能（GSAP、Framer Motion、React Spring）、3D技能（Three.js、R3F、Babylon.js）及组件库以获取实现指导。
---

# 现代网页设计

## 概述

2024-2025年的现代网页设计强调性能、可访问性和有意义的交互。这项技能为您提供全面的指导，涵盖当前设计趋势、实现模式和创建引人入胜、可访问且性能卓越的网页体验的最佳实践。

这项元技能综合了此存储库中所有动画、交互和3D技能的知识，以提供整体设计指导。

## 核心设计原则（2024-2025年）

### 1. 以性能优先的设计

**理念**：设计决策应优先考虑核心网页指标（Core Web Vitals）和所有设备上的用户体验。

**关键指标**：
- 最大内容绘制时间（LCP）：< 2.5秒
- 首次输入延迟（FID）：< 100毫秒
- 累计布局偏移（CLS）：< 0.1
- 交互到下次绘制（INP）：< 200毫秒

**实施指南**：
- 将非关键动画推迟到页面加载后执行
- 使用CSS变换/不透明度进行动画（GPU加速）
- 对图片、视频和3D内容实施懒加载
- 渐进增强：无需JavaScript的核心内容

**相关技能**：`gsap-scrolltrigger`、`motion-framer`、`lottie-animations`用于优化动画

### 2. 大胆极简主义

**特点**：
- 大型、有影响力的排版（使用clamp()实现流体尺寸）
- 充足的留白（负空间作为设计元素）
- 有限的调色板（3-5种主要颜色）
- 有意使用醒目的强调色
- 几何形状和简洁的线条

**排版规模**（现代流体系统）：
```css
/* 使用clamp()的流体排版 */
--font-size-xs: clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem);
--font-size-sm: clamp(0.875rem, 0.8rem + 0.375vw, 1rem);
--font-size-base: clamp(1rem, 0.9rem + 0.5vw, 1.25rem);
--font-size-lg: clamp(1.25rem, 1.1rem + 0.75vw, 1.75rem);
--font-size-xl: clamp(1.75rem, 1.5rem + 1.25vw, 2.5rem);
--font-size-2xl: clamp(2.5rem, 2rem + 2.5vw, 4rem);
--font-size-3xl: clamp(3.5rem, 2.5rem + 5vw, 6rem);
```

**配色系统**（以可访问性优先）：
```css
/* WCAG AAA合规的配色系统 */
--color-primary: oklch(50% 0.2 250); /* 蓝色 */
--color-accent: oklch(65% 0.25 30);  /* 珊瑚色 */
--color-neutral-50: oklch(98% 0 0);
--color-neutral-900: oklch(20% 0 0);
/* 对比度比例：文本最小为7:1 */
```

**相关技能**：`animated-component-libraries`用于UI组件

### 3. 微交互

**定义**：提供反馈、引导用户并增强感知性能的小型、有目的的动画。

**分类**：

**a) 悬停状态**（桌面端）：
- 尺寸变换（1.05-1.1倍）
- 颜色过渡（200-300毫秒）
- 阴影深度变化
- 光标变换

**b) 加载状态**：
- 骨架屏（优于加载动画）
- 渐进式图片加载（模糊上技术）
- 乐观式UI更新
- 错落有致的内容展示

**c) 交互式反馈**：
- 按钮按压状态（缩小0.95倍）
- 带弹簧物理的切换开关
- 表单字段验证（即时、友好的反馈）
- 成功/错误状态带动画

**实施示例**（Framer Motion）：
```jsx
// 带微交互的按钮
<motion.button
  whileHover={{ scale: 1.05, y: -2 }}
  whileTap={{ scale: 0.95 }}
  transition={{ type: "spring", stiffness: 400, damping: 17 }}
>
  点击我
</motion.button>
```

**相关技能**：`motion-framer`、`react-spring-physics`、`animejs`用于微交互

### 4. 滚动叙事（Scrollytelling）

**定义**：随着用户滚动，内容会展现和变换的叙事式体验。

**模式**：

**a) 滚动触发展现**：
- 滚动进入时的淡入（带偏移）
- 从两侧滑入并错开
- 缩放+不透明度过渡
- 剪裁路径展现

**b) 滚动关联动画**：
- 视差层（不同滚动速度）
- 水平滚动区域
- 带滚动动画的固定区域
- 与滚动绑定的3D对象旋转

**c) 进度指示器**：
- 阅读进度条
- 步骤式视觉指南
- 跟随滚动的SVG路径动画

**实施示例**（GSAP ScrollTrigger）：
```javascript
// 滚动关联的3D旋转
gsap.to(".cube", {
  scrollTrigger: {
    trigger: ".section",
    start: "top top",
    end: "bottom top",
    scrub: 1, // 平滑滚动
  },
  rotationY: 360,
  ease: "none"
});
```

**相关技能**：`gsap-scrolltrigger`、`locomotive-scroll`、`scroll-reveal-libraries`、`react-three-fiber`用于3D滚动叙事

### 5. 光标UX

**演变**：增强交互并提供上下文反馈的自定义光标。

**模式**：

**a) 自定义光标形状**：
- 圆形/点跟随器（带缓动延迟）
- 文本光标（"查看"、"拖动"、"点击"）
- 混合模式以增加视觉效果
- 悬停时缩放/变形

**b) 上下文变换**：
- 链接/按钮上扩展
- 吸引到交互元素
- 图片上颜色反转
- 用于操作的定制图标（播放、缩放、展开）

**c) 性能考虑**：
- 仅使用CSS变换（无top/left）
- 使用RequestAnimationFrame进行JS光标
- 在移动/触摸设备上禁用
- 尊重`prefers-reduced-motion`

**实施示例**：
```javascript
// 简单平滑光标跟随
const cursor = document.querySelector('.cursor');
let mouseX = 0, mouseY = 0;
let cursorX = 0, cursorY = 0;

document.addEventListener('mousemove', (e) => {
  mouseX = e.clientX;
  mouseY = e.clientY;
});

function updateCursor() {
  // 平滑缓动
  cursorX += (mouseX - cursorX) * 0.1;
  cursorY += (mouseY - cursorY) * 0.1;

  cursor.style.transform = `translate(${cursorX}px, ${cursorY}px)`;
  requestAnimationFrame(updateCursor);
}
updateCursor();
```

**相关技能**：`gsap-scrolltrigger`（用于缓动）、`motion-framer`（用于React光标组件）

### 6. 水晶玻璃效果（Glassmorphism）与深度

**特点**：
- 水晶玻璃效果（backdrop-filter）
- 分层UI与深度层级
- 微妙的阴影和边框
- 半透明背景

**现代水晶玻璃效果**（2024）：
```css
.glass-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border-radius: 16px;
}
```

**深度系统**（分层）：
```css
/* 立体感等级 */
--elevation-1: 0 1px 3px rgba(0,0,0,0.12);
--elevation-2: 0 4px 8px rgba(0,0,0,0.15);
--elevation-3: 0 8px 16px rgba(0,0,0,0.18);
--elevation-4: 0 16px 32px rgba(0,0,0,0.2);
```

**相关技能**：`animated-component-libraries`用于水晶玻璃效果组件

### 7. AI增强个性化

**模式**：

**a) 自适应内容**：
- 基于用户行为动态布局
- 个性化内容推荐
- 自适应配色方案（系统偏好+用户历史）
- 基于上下文的智能默认值

**b) 智能交互**：
- 预测式搜索（即时结果）
- 智能表单填充
- 上下文感知建议
- 基于使用情况的渐进式披露

**c) 性能+隐私**：
- 客户端个性化（localStorage、IndexedDB）
- 边缘计算实现快速个性化
- 隐私保护分析
- 透明数据使用

**实施考虑**：
- 落回默认体验
- 个性化不引起布局偏移
- 尊重"不要跟踪"
- GDPR/CCPA合规

## 常见设计模式

### 模式1：沉浸式英雄区域

**用例**：着陆页、产品发布、作品集网站

**特点**：
- 全视口高度
- 微妙的3D背景或动画渐变
- 大标题带流体排版
- 平滑滚动指示器
- 滚动退出时的视差效果

**实施**（组合方法）：

**HTML结构**：
```html
<section class="hero">
  <div id="bg-canvas"></div>
  <div class="hero__content">
    <h1 class="hero__title">现代设计</h1>
    <p class="hero__subtitle">性能与美学的结合</p>
    <button class="hero__cta">探索</button>
  </div>
  <div class="scroll-indicator">
    <span>滚动</span>
  </div>
</section>
```

**技术**：
- 背景：Vanta.js WAVES效果（`lightweight-3d-effects`）
- 文本动画：GSAP SplitText带错开（`gsap-scrolltrigger`）
- 按钮：Framer Motion悬停状态（`motion-framer`）
- 滚动指示器：CSS动画+滚动时GSAP淡出

**相关技能**：`lightweight-3d-effects`、`gsap-scrolltrigger`、`motion-framer`

### 模式2：水平滚动画廊

**用例**：作品集、产品展示、案例研究

**实施**（GSAP ScrollTrigger）：
```javascript
gsap.to(".gallery__track", {
  x: () => -(document.querySelector(".gallery__track").scrollWidth - window.innerWidth),
  ease: "none",
  scrollTrigger: {
    trigger: ".gallery",
    pin: true,
    scrub: 1,
    end: () => "+=" + document.querySelector(".gallery__track").scrollWidth
  }
});
```

**增强功能**：
- 滚动时懒加载图片
- 卡片内视差效果
- 激活卡片缩放变换
- 平滑动量滚动（Locomotive）

**相关技能**：`gsap-scrolltrigger`、`locomotive-scroll`

### 模式3：3D产品查看器

**用例**：电子商务、产品营销、展示

**实施**（React Three Fiber）：
```jsx
import { Canvas } from '@react-three/fiber'
import { OrbitControls, useGLTF } from '@react-three/drei'

function ProductViewer() {
  return (
    <Canvas camera={{ position: [0, 0, 5], fov: 50 }}>
      <ambientLight intensity={0.5} />
      <spotLight position={[10, 10, 10]} angle={0.15} />
      <Product />
      <OrbitControls
        enableZoom={false}
        autoRotate
        autoRotateSpeed={2}
      />
    </Canvas>
  )
}
```

**增强功能**：
- 材质变体（颜色选择器）
- 热点带注释
- 移动端AR模式
- 截图/分享功能

**相关技能**：`react-three-fiber`、`threejs-webgl`、`model-viewer-component`

### 模式4：动画数据可视化

**用例**：仪表盘、分析、信息图表

**模式**：
- 滚动进入时的计数动画
- 动画图表展现（进度条、饼图）
- 错落有致的网格动画
- 代表数据的粒子背景

**实施**（Framer Motion+IntersectionObserver）：
```jsx
function AnimatedStat({ end, label }) {
  const [count, setCount] = useState(0);
  const ref = useRef();
  const isInView = useInView(ref, { once: true });

  useEffect(() => {
    if (isInView) {
      // 计数动画
      const duration = 2000;
      const steps = 60;
      const increment = end / steps;
      let current = 0;

      const timer = setInterval(() => {
        current += increment;
        if (current >= end) {
          setCount(end);
          clearInterval(timer);
        } else {
          setCount(Math.floor(current));
        }
      }, duration / steps);
    }
  }, [isInView, end]);

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 20 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6 }}
    >
      <h2>{count}+</h2>
      <p>{label}</p>
    </motion.div>
  );
}
```

**相关技能**：`motion-framer`、`pixijs-2d`用于基于canvas的可视化

### 模式5：页面过渡

**用例**：多页面应用、作品集网站、叙事式体验

**实施**（Barba.js+GSAP）：
```javascript
barba.init({
  transitions: [{
    name: 'slide',
    leave(data) {
      return gsap.to(data.current.container, {
        xPercent: -100,
        duration: 0.5
      });
    },
    enter(data) {
      return gsap.from(data.next.container, {
        xPercent: 100,
        duration: 0.5
      });
    }
  }]
});
```

**现代替代方案**：
- 视图过渡API（Chrome 111+，渐进增强）
- Framer Motion的AnimatePresence用于React SPAs
- 共享元素过渡

**相关技能**：`barba-js`、`gsap-scrolltrigger`、`motion-framer`

### 模式6：交互式光标效果

**用例**：创意机构、作品集、交互式体验

**模式**：
- 延迟跟随的文本光标
- 磁吸按钮（光标被吸引到元素）
- 混合模式光标（颜色反转）
- 揭示内容的光标

**实施**（纯JavaScript+GSAP）：
```javascript
const links = document.querySelectorAll('a');
const cursor = document.querySelector('.cursor');

links.forEach(link => {
  link.addEventListener('mouseenter', () => {
    gsap.to(cursor, {
      scale: 2,
      duration: 0.3,
      ease: "power2.out"
    });
  });

  link.addEventListener('mouseleave', () => {
    gsap.to(cursor, {
      scale: 1,
      duration: 0.3,
      ease: "power2.out"
    });
  });
});
```

**相关技能**：`gsap-scrolltrigger`、`motion-framer`

### 模式7：错落有致的内容展现

**用例**：功能区域、客户评价、团队网格

**实施**（Framer Motion变体）：
```jsx
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
};

function FeatureGrid() {
  return (
    <motion.div
      variants={container}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, amount: 0.3 }}
      className="grid"
    >
      {features.map((feature, i) => (
        <motion.div key={i} variants={item}>
          {feature}
        </motion.div>
      ))}
    </motion.div>
  );
}
```

**相关技能**：`motion-framer`、`gsap-scrolltrigger`、`scroll-reveal-libraries`

## 与其他技能的集成

### 动画技能集成

**GSAP ScrollTrigger** (`gsap-scrolltrigger`)：
- 用于滚动驱动的叙事
- 固定区域用于多步骤展现
- 与滚动位置绑定的缓动动画
- 批量动画以提升性能

**Framer Motion** (`motion-framer`)：
- React组件动画
- 页面过渡使用AnimatePresence
- 基于手势的交互（拖动、悬停、点击）
- 布局动画（共享元素过渡）

**React Spring** (`react-spring-physics`)：
- 基于物理的动画（更自然的感觉）
- 交互式弹簧（拖动、拉动）
- 轨迹动画（顺序展现）
- 用于UI反馈的"真实"效果

**Anime.js** (`animejs`)：
- SVG路径动画（线条绘制）
- SVG变形过渡
- 错落有致的网格动画
- 基于时间线的序列

**Lottie** (`lottie-animations`)：
- 复杂的设计师创建的动画
- 图标动画和微交互
- 加载状态
- 滚动驱动的播放

### 3D技能集成

**Three.js** (`threejs-webgl`)：
- 自定义3D场景和体验
- 着色器效果和后处理
- WebGL基础粒子系统
- 高级照明和材质

**React Three Fiber** (`react-three-fiber`)：
- React应用中的3D
- 产品查看器和配置器
- 交互式3D UI组件
- 滚动驱动的3D动画

**Babylon.js** (`babylonjs-engine`)：
- 基于物理的3D体验
- VR/XR应用
- 游戏式交互
- PBR材质以实现真实感

**Lightweight 3D** (`lightweight-3d-effects`)：
- 背景效果（Vanta.js）
- 轻巧的3D插图（Zdog）
- 倾斜效果（Vanilla-Tilt）
- 性能友好的3D装饰

### 组件库

**动画组件** (`animated-component-libraries`)：
- Magic UI组件（背景、文本效果）
- 预构建的交互式组件
- 设计系统基础
- 快速原型设计

**滚动展现** (`scroll-reveal-libraries`)：
- 简单的滚动淡入/滑出
- AOS库集成
- 轻量级的ScrollTrigger替代方案
- 快速实现基本展现

## 可访问性最佳实践

### 1. 动画与交互

**尊重用户偏好**：
```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

**JavaScript 检测**：
```javascript
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (prefersReducedMotion) {
  // 禁用或简化动画
  gsap.config({ nullTargetWarn: false });
  // 跳过滚动动画，使用即时显示
}
```

### 2. 颜色对比度

**WCAG AAA 标准**：
- 普通文本：7:1 对比度
- 大文本（18pt+）：4.5:1 对比度
- 使用 OKLCH 色彩空间以实现感知一致性

**测试**：
```javascript
// 检查对比度
function getContrastRatio(color1, color2) {
  const l1 = getLuminance(color1);
  const l2 = getLuminance(color2);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}
```

### 3. 键盘导航

**要求**：
- 所有交互元素可聚焦
- 可见焦点指示器（不要 outline: none）
- 逻辑的 Tab 顺序
- 长导航的跳过链接
- Escape 键关闭模态/遮罩

**焦点样式**（现代）：
```css
:focus-visible {
  outline: 3px solid var(--color-accent);
  outline-offset: 2px;
  border-radius: 4px;
}

/* 鼠标用户移除焦点环 */
:focus:not(:focus-visible) {
  outline: none;
}
```

### 4. 屏幕阅读器支持

**语义 HTML**：
- 使用正确的标题层级（h1-h6）
- 地标区域（header、nav、main、footer）
- 图标按钮的 aria-labels
- 动态内容的 aria-live 区域

**动画公告**：
```html
<!-- 公告内容加载时 -->
<div role="status" aria-live="polite" aria-atomic="true">
  加载完成。显示 12 个项目。
</div>
```

### 5. 触摸目标

**最小尺寸**：44x44px（iOS）、48x48px（Android）

**间距**：触摸目标之间最小 8px

**实现**：
```css
.button {
  min-height: 44px;
  min-width: 44px;
  padding: 12px 24px;
  /* 触摸目标包括内边距 */
}
```

## 性能优化

### 1. 动画性能

**60 FPS 检查清单**：
- 使用 CSS 变换（translateX/Y/Z、scale、rotate）- GPU 加速
- 使用透明度进行淡入淡出 - GPU 加速
- 避免：top/left、width/height、margin、padding 动画
- 节制使用 `will-change`（内存成本）
- 使用 RequestAnimationFrame 进行 JS 动画

**GSAP 性能**：
```javascript
// 强制 GPU 加速
gsap.set(element, { force3D: true });

// 仅在动画期间使用 will-change
gsap.to(element, {
  x: 100,
  onStart: () => element.style.willChange = 'transform',
  onComplete: () => element.style.willChange = 'auto'
});
```

### 2. 加载策略

**关键路径**：
- 内联关键 CSS（视口内）
- 推迟非关键 CSS
- 异步 JavaScript 加载
- 预加载字体和英雄图片

**渐进增强**：
```html
<!-- 首先加载必要样式 -->
<style>
  /* 关键 CSS 内联 */
</style>

<!-- 推迟非关键样式 -->
<link rel="preload" href="animations.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="animations.css"></noscript>
```

### 3. 图片优化

**现代格式**：
```html
<picture>
  <source srcset="image.avif" type="image/avif">
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="描述" loading="lazy">
</picture>
```

**响应式图片**：
```html
<img
  srcset="image-400.jpg 400w,
          image-800.jpg 800w,
          image-1200.jpg 1200w"
  sizes="(max-width: 640px) 100vw,
         (max-width: 1024px) 50vw,
         33vw"
  src="image-800.jpg"
  alt="描述"
  loading="lazy"
>
```

### 4. 3D 内容优化

**加载策略**：
- 加载时显示占位符
- 首先加载低多边形模型
- 高多边形模型的渐进增强
- 懒加载折叠以下的 3D 场景

**运行时性能**：
- 使用对象池
- 实现 LOD（细节层次）
- 视锥体剔除
- 纹理压缩（Basis Universal）

**相关技能**：`threejs-webgl`、`react-three-fiber`、`babylonjs-engine`

### 5. JavaScript 打包大小

**代码拆分**：
```javascript
// 动态导入
const AnimationModule = lazy(() => import('./animations'));

// 路由拆分
const Gallery = lazy(() => import('./pages/Gallery'));
```

**摇树优化**：
- 使用 ES6 导入
- 只导入需要的部分
- 使用现代构建工具（Vite、esbuild）

## 常见陷阱

### 陷阱 1：过度动画

**问题**：过多动画分散注意力并影响性能。

**解决方案**：
- 限制动画仅用于有意义的交互
- 使用动画引导注意力而非强迫
- 遵循原则：“有目的的动画”
- 测量性能影响（Chrome DevTools 性能标签）

**经验法则**：如果无法解释动画存在的理由，就移除它。

### 陷阱 2：忽略移动端性能

**问题**：动画在桌面端正常但在移动设备上卡顿。

**解决方案**：
- 在真实设备上测试（而不仅仅是模拟器）
- 在移动端减少动画复杂度
- 在低端设备上禁用昂贵效果（视差、3D）
- 使用 `matchMedia` 实现设备特定体验

```javascript
const isLowEndDevice = () => {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent) &&
         navigator.hardwareConcurrency < 4;
};

if (isLowEndDevice()) {
  // 简化或禁用动画
}
```

### 陷阱 3：缺少回退方案

**问题**：没有 JavaScript 或在旧浏览器上体验崩溃。

**解决方案**：
- 渐进增强思维
- 核心内容无需 JS 即可访问
- 使用现代 API 前进行特性检测
- 使用 Polyfill 补充关键功能

```javascript
// 特性检测
if ('IntersectionObserver' in window) {
  // 使用滚动触发动画
} else {
  // 立即显示内容
}
```

### 陷阱 4：可访问性疏忽

**问题**：忘记键盘用户、屏幕阅读器或运动敏感用户。

**解决方案**：
- 仅使用键盘测试
- 使用屏幕阅读器测试（NVDA、VoiceOver）
- 始终检查 `prefers-reduced-motion`
- 使用语义 HTML
- 保持正确的焦点管理

**检查清单**：
- [ ] 所有交互元素可通过键盘访问
- [ ] 焦点指示器可见
- [ ] 颜色对比度符合 WCAG AAA
- [ ] 运动可被禁用
- [ ] 屏幕阅读器公告有意义

### 陷阱 5：忽略加载状态

**问题**：内容加载时出现空白屏幕或布局偏移。

**解决方案**：
- 预测性布局的骨架屏
- 平滑加载过渡
- 为动态内容预留空间
- 显示有意义的加载指示器

```jsx
// 骨架屏模式
function ProductCard({ loading, data }) {
  if (loading) {
    return (
      <div className="skeleton">
        <div className="skeleton__image" />
        <div className="skeleton__title" />
        <div className="skeleton__price" />
      </div>
    );
  }

  return <ProductCardContent data={data} />;
}
```

### 陷阱 6：滚动劫持

**问题**：覆盖原生滚动行为让用户感到沮丧。

**解决方案**：
- 保留浏览器的原生滚动（惯性、键盘）
- 使用 ScrollTrigger/Locomotive 而不改变滚动物理特性
- 允许用户以自己的节奏滚动
- 永远不要完全禁用滚动
- 避免对全页部分进行滚动劫持

**良好实践**：增强滚动，而非替换它。

## 设计系统架构

### 符号结构

**现代设计符号**（CSS 变量）：
```css
:root {
  /* 颜色 - OKLCH 实现感知一致性 */
  --color-primary: oklch(50% 0.2 250);
  --color-accent: oklch(65% 0.25 30);

  /* 间距 - 一致的比例 */
  --space-2xs: clamp(0.25rem, 0.2rem + 0.25vw, 0.375rem);
  --space-xs: clamp(0.5rem, 0.4rem + 0.5vw, 0.75rem);
  --space-sm: clamp(0.75rem, 0.6rem + 0.75vw, 1.125rem);
  --space-md: clamp(1rem, 0.8rem + 1vw, 1.5rem);
  --space-lg: clamp(1.5rem, 1.2rem + 1.5vw, 2.25rem);
  --space-xl: clamp(2rem, 1.6rem + 2vw, 3rem);
  --space-2xl: clamp(3rem, 2.4rem + 3vw, 4.5rem);

  /* 字体 - 流体比例 */
  --font-size-base: clamp(1rem, 0.9rem + 0.5vw, 1.25rem);

  /* 动画 - 一致的时间 */
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;

  /* 缓动 - 自然运动 */
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

### 组件架构

**原子设计**（Brad Frost）：
1. **原子**：按钮、输入、标签
2. **分子**：表单字段、卡片
3. **有机体**：导航、英雄区域
4. **模板**：页面布局
5. **页面**：特定实例

**相关技能**：`animated-component-libraries` 用于组件模式

## 资源

此技能参考以下技能进行实现：

### 动画与交互
- `gsap-scrolltrigger` - 滚动驱动动画、固定、滚动
- `motion-framer` - React 动画、手势、布局动画
- `react-spring-physics` - 基于物理的动画
- `animejs` - SVG 动画、错开效果
- `lottie-animations` - 设计师创建的动画
- `scroll-reveal-libraries` - 简单滚动揭示（AOS）

### 3D & WebGL
- `threejs-webgl` - 自定义 3D 场景和效果
- `react-three-fiber` - React 中的 3D
- `babylonjs-engine` - 基于物理的 3D、VR/XR
- `lightweight-3d-effects` - Vanta.js 背景、Zdog 插图

### 页面过渡与滚动
- `barba-js` - 页面过渡
- `locomotive-scroll` - 平滑滚动

### 组件库
- `animated-component-libraries` - Magic UI、React Bits
- `pixijs-2d` - 基于画布的 2D 图形

### 详细参考

参考 `references/` 目录获取深入文档：
- `design_trends_2024.md` - 当前网页设计趋势和预测
- `interaction_patterns.md` - 微交互目录
- `accessibility_guide.md` - WCAG 合规模式与测试
- `performance_checklist.md` - 优化策略与指标

### 脚本

`scripts/` 目录包含实现设计模式的工具：
- `pattern_generator.py` - 生成设计模式模板
- `design_audit.py` - 审计现有设计合规性

### 资源

`assets/` 目录包含设计系统模板和启动文件。详情见 `assets/README.md`。
