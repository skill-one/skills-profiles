# 现代网页设计

## 概述

2024-2025年的现代网页设计强调性能、可访问性和有意义的交互。这项技能为您提供关于当前设计趋势、实现模式和创建引人入胜、可访问且性能卓越的网页体验的最佳实践的综合指导。

这项元技能综合了此存储库中所有动画、交互和3D技能的知识，以提供全面的设计指导。

## 2024-2025年的核心设计原则

### 1. 以性能为先的设计

**理念**：设计决策应优先考虑核心网页指标和所有设备上的用户体验。

**关键指标**：
- 最大内容绘制（LCP）：< 2.5秒
- 首次输入延迟（FID）：< 100毫秒
- 累计布局偏移（CLS）：< 0.1
- 交互到下次绘制（INP）：< 200毫秒

**实施指南**：
- 延迟加载非关键动画，直到页面加载完成
- 使用CSS转换/不透明度进行动画（GPU加速）
- 对图像、视频和3D内容实施懒加载
- 渐进增强：核心内容无需JavaScript

**相关技能**：`gsap-scrolltrigger`、`motion-framer`、`lottie-animations`用于优化动画

### 2. 大胆极简主义

**特点**：
- 大型、有影响力的排版（使用clamp()进行流体尺寸）
- 充足的空白空间（负空间作为设计元素）
- 有限的调色板（3-5种主要颜色）
- 有意使用醒目的强调色
- 几何形状和干净的线条

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

**配色系统**（以可访问性为先）：
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

**a) 悬停状态**（桌面）：
- 缩放转换（1.05-1.1倍）
- 颜色过渡（200-300毫秒）
- 阴影深度变化
- 光标转换

**b) 加载状态**：
- 骨架屏（比加载动画更好）
- 渐进式图像加载（模糊上技术）
- 乐观UI更新
- 错落有致的内容揭示

**c) 交互反馈**：
- 按钮按压状态（缩小0.95倍）
- 带弹簧物理的切换开关
- 表单字段验证（立即、友好的反馈）
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

### 4. 滚动叙事

**定义**：内容随着用户滚动而揭示和转换的叙事驱动体验。

**模式**：

**a) 滚动触发的揭示**：
- 滚动进入时的淡入（带偏移）
- 从两侧滑入，带错落
- 缩放+不透明度转换
- 剪裁路径揭示

**b) 滚动链接的动画**：
- 视差层（不同的滚动速度）
- 水平滚动部分
- 带刮擦动画的固定部分
- 与滚动绑定的3D对象旋转

**c) 进度指示器**：
- 阅读进度条
- 步骤式视觉指南
- 跟随滚动的动画SVG路径

**实施示例**（GSAP ScrollTrigger）：
```javascript
// 滚动链接的3D旋转
gsap.to(".cube", {
  scrollTrigger: {
    trigger: ".section",
    start: "top top",
    end: "bottom top",
    scrub: 1, // 平滑刮擦
  },
  rotationY: 360,
  ease: "none"
});
```

**相关技能**：`gsap-scrolltrigger`、`locomotive-scroll`、`scroll-reveal-libraries`、`react-three-fiber`用于3D滚动叙事

### 5. 光标UX

**演变**：自定义光标，增强交互并提供上下文反馈。

**模式**：

**a) 自定义光标形状**：
- 圆形/点跟随器（带缓动延迟）
- 文本光标（“查看”、“拖动”、“点击”）
- 混合模式以增加视觉效果
- 悬停时缩放/变形

**b) 上下文转换**：
- 链接/按钮上扩展
- 吸引到交互元素的马磁效果
- 图像上颜色反转
- 用于操作的自定义图标（播放、缩放、展开）

**c) 性能考虑**：
- 仅使用CSS转换（不使用top/left）
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

### 6. 玻璃态与深度

**特点**：
- 水晶效果（backdrop-filter）
- 带深度层次结构的分层UI
- 微妙的阴影和边框
- 半透明背景

**现代玻璃态**（2024）：
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

**相关技能**：`animated-component-libraries`用于玻璃态组件

### 7. AI增强个性化

**模式**：

**a) 适应性内容**：
- 基于用户行为动态布局
- 个性化内容推荐
- 适应性配色方案（系统偏好+用户历史）
- 基于上下文的智能默认值

**b) 智能交互**：
- 预测性搜索，即时结果
- 智能表单填充
- 上下文感知建议
- 基于使用情况的渐进式披露

**c) 性能+隐私**：
- 客户端个性化（localStorage、IndexedDB）
- 边缘计算以实现快速个性化
- 隐私保护分析
- 透明的数据使用

**实施考虑**：
- 回退到默认体验
- 个性化不会导致布局偏移
- 尊重“不要跟踪”
- GDPR/CCPA合规

## 常见设计模式

### 模式1：沉浸式英雄区域

**用例**：着陆页、产品发布、作品集网站

**特点**：
- 全视口高度
- 轻微的3D背景或动画渐变
- 大型标题，带流体排版
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
- 文本动画：GSAP SplitText带错落（`gsap-scrolltrigger`）
- 按钮：Framer Motion悬停状态（`motion-framer`）
- 滚动指示器：CSS动画+GSAP滚动时淡出

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
- 滚动时懒加载图像
- 卡片内视差效果
- 激活卡片的缩放转换
- 平滑的动量滚动，使用Locomotive

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
- 带注释的热点
- 移动端AR模式
- 截图/分享功能

**相关技能**：`react-three-fiber`、`threejs-webgl`、`model-viewer-component`

### 模式4：动画数据可视化

**用例**：仪表板、分析、信息图表

**模式**：
- 滚动进入时的计数动画
- 动画图表揭示（进度条、饼图）
- 错落有致的网格动画
- 代表数据的粒子背景

**实施**（Framer Motion + IntersectionObserver）：
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

**相关技能**：`motion-framer`、`pixijs-2d`用于基于Canvas的2D可视化

### 模式5：页面过渡

**用例**：多页面应用程序、作品集网站、故事讲述体验

**实施**（Barba.js + GSAP）：
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

### 模式6：交互光标效果

**用例**：创意机构、作品集、交互体验

**模式**：
- 文本光标，跟随延迟
- 马磁按钮（光标被吸引到元素）
- 混合模式，视觉兴趣
- 悬停时缩放/变形

**实施**（Vanilla JS + GSAP）：
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

### 模式7：错落有致的内容揭示

**用例**：功能部分、客户评价、团队网格

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

**GSAP ScrollTrigger** (`gsap-scrolltrigger`):
- 用于滚动驱动的叙事
- 固定部分用于多步骤揭示
- 与滚动位置绑定的刮擦动画
- 批量动画以提高性能

**Framer Motion** (`motion-framer`):
- React组件动画
- 页面过渡使用AnimatePresence
- 基于手势的交互（拖动、悬停、点击）
- 布局动画（共享元素过渡）

**React Spring** (`react-spring-physics`):
- 物理动画（更具自然感）
- 交互式弹簧（拖动、拉动）
- 轨迹动画（顺序揭示）
- 用于UI反馈，感觉“真实”

**Anime.js** (`animejs`):
- SVG路径动画（线绘制）
- SVG变形过渡
- 错落有致的网格动画
- 基于时间线的序列

**Lottie** (`lottie-animations`):
- 复杂的设计师创建的动画
- 图标动画和微交互
- 加载状态
- 滚动时播放

### 3D技能集成

**Three.js** (`threejs-webgl`):
- 自定义3D场景和体验
- 着色器效果和后期处理
- WebGL基础粒子系统
- 高级照明和材质

**React Three Fiber** (`react-three-fiber`):
- React应用中的3D
- 产品查看器和配置器
- 交互式3D UI组件
- 滚动驱动的3D动画

**Babylon.js** (`babylonjs-engine`):
- 基于物理的3D体验
- VR/XR应用
- 游戏式交互
- PBR材质以实现真实感

**Lightweight 3D** (`lightweight-3d-effects`):
- 背景效果（Vanta.js）
- 轻微的3D插图（Zdog）
- 倾斜效果（Vanilla-Tilt）
- 性能友好的3D装饰

**相关技能**: `threejs-webgl`, `react-three-fiber`, `babylonjs-engine`

### 组件库

**Animated Components** (`animated-component-libraries`):
- Magic UI组件（背景、文本效果）
- 预构建的交互式组件
- 设计系统基础
- 快速原型设计

**Scroll Reveals** (`scroll-reveal-libraries`):
- 简单的滚动时淡入/滑入
- AOS库集成
- 简单的替代方案，用于基本揭示
- 快速实现基本揭示

## 可访问性最佳实践

### 1. 动画与交互

**尊重用户偏好**:
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

**JavaScript检测**:
```javascript
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (prefersReducedMotion) {
  // 简化或禁用动画
  gsap.config({ nullTargetWarn: false });
  // 跳过滚动动画，使用即时揭示
}
```

### 2. 颜色对比度

**WCAG AAA标准**:
- 普通文本：对比度比例7:1
- 大号文本（18pt+）：对比度比例4.5:1
- 使用OKLCH颜色空间，感知一致性

**测试**:
```javascript
// 检查对比度比例
function getContrastRatio(color1, color2) {
  const l1 = getLuminance(color1);
  const l2 = getLuminance(color2);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}
```

### 3. 键盘导航

**要求**:
- 所有交互元素可聚焦
- 可见焦点指示器（不要outline: none）
- 逻辑的Tab顺序
- 跳过链接，用于长导航
- 按Esc键关闭模态/覆盖

**焦点样式**（现代）:
```css
:focus-visible {
  outline: 3px solid var(--color-accent);
  outline-offset: 2px;
  border-radius: 4px;
}

/* 移除鼠标用户的焦点环 */
:focus:not(:focus-visible) {
  outline: none;
}
```

### 4. 屏幕阅读器支持

**语义HTML**:
- 使用正确的标题层次结构（h1-h6）
- 里程碑区域（header、nav、main、footer）
- 图标按钮的aria-labels
- 动态内容区域，aria-live

**动画公告**:
```html
<!-- 内容加载时公告 -->
<div role="status" aria-live="polite" aria-atomic="true">
  加载完成。显示12个项目。
</div>
```

### 5. 触摸目标

**最小尺寸**: 44x44像素（iOS）、48x48像素（Android）

**间距**: 触摸目标之间至少8像素

**实施**:
```css
.button {
  min-height: 44px;
  min-width: 44px;
  padding: 12px 24px;
  /* 触摸目标包括填充 */
}
```

## 性能优化

### 1. 动画性能

**60 FPS清单**:
- 使用CSS转换（translateX/Y/Z、scale、rotate）- GPU加速
- 使用不透明度进行淡入 - GPU加速
- 避免：top/left、width/height、margin、padding动画
- 使用`will-change`要谨慎（内存成本）
- 使用RequestAnimationFrame进行JS动画

**GSAP性能**:
```javascript
// 强制GPU加速
gsap.set(element, { force3D: true });

// 仅在动画期间使用will-change
gsap.to(element, {
  x: 100,
  onStart: () => element.style.willChange = 'transform',
  onComplete: () => element.style.willChange = 'auto'
});
```

### 2. 加载策略

**关键路径**:
- 内联关键CSS（视口内）
- 延迟加载非关键CSS
- 异步JavaScript加载
- 预加载字体和英雄图像

**渐进增强**:
```html
<!-- 首先加载基本样式 -->
<style>
  /* 基本样式内联 */
</style>

<!-- 延迟加载非关键样式 -->
<link rel="preload" href="animations.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="animations.css"></noscript>
```

### 3. 图像优化

**现代格式**:
```html
<picture>
  <source srcset="image.avif" type="image/avif">
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="描述" loading="lazy">
</picture>
```

**响应式图像**:
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

### 4. 3D内容优化

**加载策略**:
- 显示占位符，等待加载
- 首先加载低多边形模型
- 渐进增强，使用高多边形
- 懒加载3D场景，位于视口下方

**运行时性能**:
- 使用对象池
- 实施细节层次（LOD）
- 视锥剔除
- 纹理压缩（Basis Universal）

**相关技能**: `threejs-webgl`, `react-three-fiber`, `model-viewer-component`

### 5. JavaScript包大小

**代码拆分**:
```javascript
// 动态导入
const AnimationModule = lazy(() => import('./animations'));

// 路由拆分
const Gallery = lazy(() => import('./pages/Gallery'));
```

**树形摇动**:
- 使用ES6导入
- 只导入需要的部分
- 使用现代构建工具（Vite、esbuild）

## 常见陷阱

### 陷阱1：过度动画

**问题**: 太多动画分散注意力，损害性能。

**解决方案**:
- 限制动画到有意义的交互
- 使用动画引导注意力，而不是强迫
- 遵循原则：“有目的的动画”
- 测量性能影响（Chrome DevTools性能标签）

**经验法则**: 如果无法解释动画存在的原因，请删除它。

### 陷阱2：忽略移动端性能

**问题**: 动画在桌面端有效，但在移动设备上卡顿。

**解决方案**:
- 在真实设备上测试（而不仅仅是模拟器）
- 在移动端减少动画复杂性
- 在低端设备上禁用昂贵的特效（视差、3D）
- 使用`matchMedia`进行设备特定体验

```javascript
const isLowEndDevice = () => {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent) &&
         navigator.hardwareConcurrency < 4;
};

if (isLowEndDevice()) {
  // 简化或禁用动画
}
```

### 陷阱3：缺少回退

**问题**: 缺少JavaScript或旧版浏览器上的体验。

**解决方案**:
- 渐进增强思维
- 无需JavaScript的核心内容
- 使用现代API进行功能检测
- 使用polyfills进行关键功能

```javascript
// 功能检测
if ('IntersectionObserver' in window) {
  // 使用滚动触发的动画
} else {
  // 立即显示内容
}
```

### 陷阱4：可访问性疏忽

**问题**: 忘记键盘用户、屏幕阅读器或运动敏感用户。

**解决方案**:
- 仅使用键盘测试
- 使用屏幕阅读器测试（NVDA、VoiceOver）
- 始终检查`prefers-reduced-motion`
- 使用语义HTML
- 维护适当的焦点管理

**清单**:
- [ ] 所有交互元素可聚焦
- [ ] 焦点指示器可见
- [ ] 颜色对比度符合WCAG AAA
- [ ] 运动可以禁用
- [ ] 屏幕阅读器公告有意义

### 陷阱5：忽略加载状态

**问题**: 加载时空白屏幕或布局偏移。

**解决方案**:
- 骨架屏，用于可预测的布局
- 平滑加载过渡
- 保留动态内容的空间
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

### 陷阱6：滚动劫持

**问题**: 控制浏览器滚动行为，使用户感到沮丧。

**解决方案**:
- 保留浏览器的原生滚动（动量、键盘）
- 使用ScrollTrigger/Locomotive而不改变滚动物理
- 允许用户以自己的速度滚动
- 从不完全禁用滚动
- 避免滚动劫持用于全页面部分

**良好实践**: 增强滚动，而不是替换它。

## 设计系统架构

### 符号结构

**现代设计符号**（CSS自定义属性）:
```css
:root {
  /* 颜色 - OKLCH用于感知一致性 */
  --color-primary: oklch(50% 0.2 250);
  --color-accent: oklch(65% 0.25 30);

  /* 间距 - 一致的尺度 */
  --space-2xs: clamp(0.25rem, 0.2rem + 0.25vw, 0.375rem);
  --space-xs: clamp(0.5rem, 0.4rem + 0.5vw, 0.75rem);
  --space-sm: clamp(0.75rem, 0.6rem + 0.75vw, 1.125rem);
  --space-md: clamp(1rem, 0.8rem + 1vw, 1.5rem);
  --space-lg: clamp(1.5rem, 1.2rem + 1.5vw, 2.25rem);
  --space-xl: clamp(2rem, 1.6rem + 2vw, 3rem);
  --space-2xl: clamp(3rem, 2.4rem + 3vw, 4.5rem);

  /* 排版 - 流体尺度 */
  --font-size-base: clamp(1rem, 0.9rem + 0.5vw, 1.25rem);

  /* 动画 - 一致的持续时间 */
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;

  /* 缓动 - 自然运动 */
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

### 组件架构

**原子设计**（Brad Frost）:
1. **原子**: 按钮、输入、标签
2. **分子**: 表单字段、卡片
3. **有机体**: 导航、英雄区域
4. **模板**: 页面布局
5. **页面**: 特定实例

**相关技能**: `animated-component-libraries`用于组件模式

## 资源

此技能参考以下技能进行实现：

### 动画 & 交互
- `gsap-scrolltrigger` - 滚动驱动的动画，固定，刮擦
- `motion-framer` - React动画，手势，布局动画
- `react-spring-physics` - 基于物理的动画
- `animejs` - SVG动画，错落效果
- `lottie-animations` - 设计师创建的动画
- `scroll-reveal-libraries` - 简单滚动揭示（AOS）

### 3D & WebGL
- `threejs-webgl` - 自定义3D场景和效果
- `react-three-fiber` - React应用中的3D
- `babylonjs-engine` - 基于物理的3D，VR/XR
- `lightweight-3d-effects` - Vanta.js背景，Zdog插图

### 页面过渡 & 滚动
- `barba-js` - 页面过渡
- `locomotive-scroll` - 平滑滚动

### 组件库
- `animated-component-libraries` - Magic UI, React Bits
- `pixijs-2d` - 基于Canvas的2D图形

### 详细参考

有关深入文档，请参阅`references/`目录：
- `design_trends_2024.md` - 当前网页设计趋势和预测
- `interaction_patterns.md` - 详细的微交互目录
- `accessibility_guide.md` - WCAG合规模式和测试
- `performance_checklist.md` - 优化策略和指标

### 脚本

`scripts/`目录包含用于实现设计模式的工具：
- `pattern_generator.py` - 生成设计模式样板
- `design_audit.py` - 审计现有设计合规性

### 资产

`assets/`目录包含设计系统模板和启动文件。详情请参阅`assets/README.md`。
