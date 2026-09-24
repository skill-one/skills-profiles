识别并修复性能问题，打造更快、更流畅的用户体验。

## 评估性能问题

了解当前性能状况并识别问题：

1. **测量当前状态**：
   - **Core Web Vitals**：LCP、FID/INP、CLS 分数
   - **加载时间**：可交互时间（TTI）、首次内容渲染（FCP）
   - **包体积**：JavaScript、CSS、图片体积
   - **运行时性能**：帧率、内存占用、CPU 占用
   - **网络**：请求数量、载荷大小、瀑布图

2. **识别瓶颈**：
   - 什么环节卡顿？（初次加载？交互？动画？）
   - 导致问题的原因是什么？（图片过大？JavaScript 臃肿？布局抖动？）
   - 问题有多严重？（影响感知？令人烦躁？造成阻塞？）
   - 受影响的人群？（所有用户？仅限移动端？网络较慢的场景？）

**关键**：测量前后必须同步进行。过早优化会浪费时间。优化真正重要的环节。

## 优化策略

制定系统性的改进计划：

### 加载性能

**优化图片**：
- 使用现代格式（WebP、AVIF）
- 尺寸设置合理（不应对 300px 的展示加载 3000px 的图片）
- 对折叠线以下的图片进行懒加载
- 响应式图片（`srcset`、`picture` 元素）
- 压缩图片（80%-85% 的画质通常感知不明显）
- 使用 CDN 加快交付

```html
<img 
  src="hero.webp"
  srcset="hero-400.webp 400w, hero-800.webp 800w, hero-1200.webp 1200w"
  sizes="(max-width: 400px) 400px, (max-width: 800px) 800px, 1200px"
  loading="lazy"
  alt="Hero image"
/>
```

**减小 JavaScript 包体积**：
- 代码分割（按路由、按组件）
- 摇树优化（去除未使用的代码）
- 移除未使用的依赖
- 懒加载非关键代码
- 使用动态导入处理大型组件

```javascript
// 懒加载重组件
const HeavyChart = lazy(() => import('./HeavyChart'));
```

**优化 CSS**：
- 移除未使用的 CSS
- 关键 CSS 内联，其余异步加载
- 精简 CSS 文件
- 为独立区域使用 CSS 容器（containment）

**优化字体**：
- 使用 `font-display: swap` 或 `optional`
- 字体子集化（仅使用所需字符）
- 预加载关键字体
- 适当使用系统字体
- 限制加载的字体粗细

```css
@font-face {
  font-family: 'CustomFont';
  src: url('/fonts/custom.woff2') format('woff2');
  font-display: swap; /* 立即显示回退字体 */
  unicode-range: U+0020-007F; /* 仅基本拉丁字符 */
}
```

**优化加载策略**：
- 关键资源优先加载（非关键资源异步/延迟加载）
- 预加载关键资源
- 预取可能访问的后续页面
- 使用 Service Worker 支持离线与缓存
- 使用 HTTP/2 或 HTTP/3 实现多路复用

### 渲染性能

**避免布局抖动**：
```javascript
// ❌ 错误：交替读写（会引发回流）
elements.forEach(el => {
  const height = el.offsetHeight; // 读取（强制触发布局）
  el.style.height = height * 2; // 写入
});

// ✅ 正确：先批量读取，再批量写入
const heights = elements.map(el => el.offsetHeight); // 全部读取
elements.forEach((el, i) => {
  el.style.height = heights[i] * 2; // 全部写入
});
```

**优化渲染**：
- 为独立区域使用 CSS `contain` 属性
- 减小 DOM 深度（越扁平越快）
- 减小 DOM 体积（减少元素数量）
- 为长列表使用 `content-visibility: auto`
- 为超长列表使用虚拟滚动（react-window、react-virtualized）

**减少绘制与合成**：
- 使用 `transform` 和 `opacity` 进行动画（GPU 加速）
- 避免对布局属性（宽度、高度、top、left）进行动画
- 为已知的高昂操作少量使用 `will-change`
- 减小绘制区域（越小越快）

### 动画性能

**GPU 加速**：
```css
/* ✅ GPU 加速（快速） */
.animated {
  transform: translateX(100px);
  opacity: 0.5;
}

/* ❌ 依赖 CPU（缓慢） */
.animated {
  left: 100px;
  width: 300px;
}
```

**实现流畅的 60fps**：
- 目标每帧 16ms（60fps）
- 使用 `requestAnimationFrame` 进行 JavaScript 动画
- 对滚动事件进行防抖/节流处理
- 尽量使用 CSS 动画
- 避免在动画期间执行长时间运行的 JavaScript

**Intersection Observer**：
```javascript
// 高效检测元素进入视口
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      // 元素可见，进行懒加载或动画
    }
  });
});
```

### React/框架优化

**React 专属优化**：
- 使用 `memo()` 处理昂贵的组件
- 使用 `useMemo()` 和 `useCallback()` 处理昂贵的计算
- 虚拟化长列表
- 路由代码分割
- 避免在渲染时内联创建函数
- 使用 React DevTools 性能分析器

**框架通用优化**：
- 减少重新渲染
- 防抖昂贵操作
- 记忆化计算值
- 懒加载路由与组件

### 网络优化

**减少请求数量**：
- 合并小型文件
- 使用 SVG 精灵图处理图标
- 内联小型关键资源
- 移除未使用的第三方脚本

**优化接口调用**：
- 使用分页（不一次性加载全部数据）
- 使用 GraphQL 仅请求所需字段
- 响应压缩（gzip、brotli）
- HTTP 缓存响应头
- 静态资源使用 CDN

**针对慢速连接优化**：
- 基于连接状态进行自适应加载（`navigator.connection`）
- 乐观更新界面
- 请求优先级控制
- 渐进式增强

## Core Web Vitals 优化

### 最大内容渲染（LCP < 2.5s）
- 优化首屏图片
- 内联关键 CSS
- 预加载关键资源
- 使用 CDN
- 服务端渲染

### 首次输入延迟（FID < 100ms）/ INP (< 200ms）
- 拆分长任务
- 延迟加载非关键 JavaScript
- 为重计算使用 Web Worker
- 减少 JavaScript 执行时间

### 累积布局偏移（CLS < 0.1）
- 为图片和视频设置尺寸
- 不要在已有内容上方注入内容
- 使用 CSS `aspect-ratio` 属性
- 为广告/嵌入内容预留空间
- 避免引起布局偏移的动画

```css
/* 为图片预留空间 */
.image-container {
  aspect-ratio: 16 / 9;
}
```

## 性能监控

**常用工具**：
- Chrome DevTools（Lighthouse、性能分析面板）
- WebPageTest
- Core Web Vitals（Chrome UX 报告）
- 包分析工具（webpack-bundle-analyzer）
- 性能监控（Sentry、DataDog、New Relic）

**关键指标**：
- LCP、FID/INP、CLS（Core Web Vitals）
- 可交互时间（TTI）
- 首次内容渲染（FCP）
- 总阻塞时间（TBT）
- 包体积
- 请求数量

**重要**：必须在真实设备、真实网络环境下进行测量。使用桌面版 Chrome 且连接快速的情况并不具代表性。

**切勿**：
- 不测量就进行优化（过早优化）
- 为性能牺牲无障碍体验
- 优化过程中破坏功能
- 到处使用 `will-change`（会创建新的层，消耗内存）
- 对首屏内容进行懒加载
- 在忽略重大问题的前提下只做微优化（应优先优化最大的瓶颈）
- 忽视移动端性能（移动端往往设备更慢、连接更慢）

## 验证优化效果

测试优化是否生效：

- **优化前后指标**：对比 Lighthouse 分数
- **真实用户监控**：跟踪真实用户的优化效果
- **不同设备测试**：在低端 Android 设备上测试，而非仅测试旗舰 iPhone
- **慢速连接测试**：将网络节流至 3G 并测试体验
- **无回归**：确保功能依然正常
- **用户感知**：体验是否*感觉*更快？

请记住：性能是一种功能。快速体验会让人觉得更具响应性、更精致、更专业。请系统性地进行优化，严格地测量，并优先考虑用户感知到的性能表现。
