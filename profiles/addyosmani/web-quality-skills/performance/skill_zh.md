# 性能优化

基于真实用户信号进行证据驱动的性能优化，优先级排序使用真实用户信号，诊断使用浏览器追踪。重点关注加载速度、运行时响应性和资源交付。

## 工作原理

1. 如果页面可以运行，请阅读[测量工作流程](references/MEASUREMENT.md)，在编辑前建立现场加实验室基准。
2. 优先处理表现差的真机核心网页指标。使用 DevTools 性能追踪及其聚焦洞察来找到原因。
3. 仅检查和更改与测量瓶颈相关的代码或资源。
4. 重新运行等效的实验室测量，报告前后值、条件和不确定性。现场验证仍需等待足够多的新用户数据到来。

当不存在可运行的页面时，执行静态检查，但将发现结果称为**假设**，而不是测量的回归。包含可以验证每个高影响假设的命令或浏览器工作流程。

优先选择记录性能追踪并暴露聚焦洞察的浏览器工具。使用 Chrome DevTools MCP 时，使用 `performance_start_trace` 和 `performance_analyze_insight`；不要通过 `lighthouse_audit` 路由性能，后者涵盖非性能的 Lighthouse 类别。

## 性能预算的起始点

预算必须反映产品的目标设备、网络、页面类型和用户旅程。下表值是典型内容或电商页面的初始警戒线，不是通用的通过/失败标准。当已定义项目预算时，保留现有项目预算。

| 资源 | 预算 | 理由 |
|------|------|------|
| 总页面重量 | < 1.5 MB | 限制在受限目标网络上传输时间和数据成本；使用代表性页面进行校准 |
| JavaScript (压缩) | < 300 KB | 保护解析和执行成本 |
| CSS (压缩) | < 100 KB | 限制渲染阻塞工作 |
| 图片 (视口内) | < 500 KB | 保护可能的 LCP 资源 |
| 字体 | < 100 KB | 限制关键字体传输 |
| 第三方 | < 200 KB | 限制产品控制外的代码 |

## 关键渲染路径

### 服务器响应

* **TTFB < 800ms。** 首字节时间应快速。使用 CDN、缓存和高效的后端。
* **启用压缩。** 文本资源使用 Gzip 或 Brotli。优先使用 Brotli（比 Gzip 小 15-20%）。
* **HTTP/2 或 HTTP/3。** 多路复用减少连接开销。
* **边缘缓存。** 在可能的情况下，在 CDN 边缘缓存 HTML。
* **考虑为测量文档延迟使用早期提示 (HTTP 103)。** 如果追踪显示 HTML 生成慢且关键子资源稳定，则在来自同一请求的正常最终响应之前，使用 HTTP/2 或更高版本发送带有 `Link` 头的中间 `103`。CDN 可能从更早的 `200` 的 `Link` 头中合成 `103`，或者源/边缘处理程序可以直接发出它。不支持的客户端继续接收最终响应，但确认当前浏览器和基础设施支持。将提示限制为已证明的关键预加载或预连接：不准确的提示会浪费带宽。Cloudflare 在一个人工的、图像密集型测试中报告了 20-30% 的 LCP 改善；将其视为一个供应商案例研究，而不是预期节省，并测量您的结果。参见 [MDN 的 103 实现示例](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/103) 和 [Cloudflare 的研究](https://blog.cloudflare.com/early-hints-performance/)。

### 资源加载

**预连接到所需源：**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://cdn.example.com" crossorigin>
```

**预加载关键资源：**

仅预加载在追踪中显示为延迟发现的资源。每个预加载都会竞争带宽，不必要的最高优先级请求可能会延迟 LCP。

```html
<!-- LCP 图片 -->
<link rel="preload" href="/hero.webp" as="image" fetchpriority="high">

<!-- 关键字体 -->
<link rel="preload" href="/font.woff2" as="font" type="font/woff2" crossorigin>
```

**使用 [Speculation Rules API](https://developer.chrome.com/docs/web-platform/prerender-pages) 预渲染可能的下一个导航：**
```html
<script type="speculationrules">
{
  "prerender": [{
    "where": { "href_matches": "/*" },
    "eagerness": "moderate"
  }]
}
</script>
```
`moderate` 比 eager 模式等待更强的意图信号。测量预测命中率、传输字节数和服务器成本；错误的预渲染大致相当于未使用的导航。参见 [core-web-vitals → LCP](../core-web-vitals/SKILL.md#lcp-largest-contentful-paint) 了解权衡和 `prerenderingchange` 门控所需的分析。

**延迟非关键 CSS：**
```html
<!-- 关键 CSS 内联 -->
<style>/* 视口内样式 */</style>

<!-- 非关键 CSS -->
<link rel="preload" href="/styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="/styles.css"></noscript>
```

### JavaScript 优化

**延迟非必要脚本：**
```html
<!-- 解析阻塞 (避免) -->
<script src="/critical.js"></script>

<!-- 延迟 (首选) -->
<script defer src="/app.js"></script>

<!-- 异步 (用于独立脚本) -->
<script async src="/analytics.js"></script>

<!-- 模块 (默认延迟) -->
<script type="module" src="/app.mjs"></script>
```

**代码拆分模式：**
```javascript
// 路由拆分
const Dashboard = lazy(() => import('./Dashboard'));

// 组件拆分
const HeavyChart = lazy(() => import('./HeavyChart'));

// 功能拆分
if (user.isPremium) {
  const PremiumFeatures = await import('./PremiumFeatures');
}
```

**树摇最佳实践：**
```javascript
// ❌ 导入整个库
import _ from 'lodash';
_.debounce(fn, 300);

// ✅ 仅导入所需部分
import debounce from 'lodash/debounce';
debounce(fn, 300);
```

## 图片优化

### 格式选择
| 格式 | 用途 | 浏览器支持 |
|------|------|----------|
| AVIF | 照片，最佳压缩 | 92%+ |
| WebP | 照片，良好回退 | 97%+ |
| PNG | 带透明度的图形 | 通用 |
| SVG | 图标、标志、插图 | 通用 |

### 响应式图片
```html
<picture>
  <!-- AVIF 用于现代浏览器 -->
  <source 
    type="image/avif"
    srcset="hero-400.avif 400w,
            hero-800.avif 800w,
            hero-1200.avif 1200w"
    sizes="(max-width: 600px) 100vw, 50vw">
  
  <!-- WebP 回退 -->
  <source 
    type="image/webp"
    srcset="hero-400.webp 400w,
            hero-800.webp 800w,
            hero-1200.webp 1200w"
    sizes="(max-width: 600px) 100vw, 50vw">
  
  <!-- JPEG 回退 -->
  <img 
    src="hero-800.jpg"
    srcset="hero-400.jpg 400w,
            hero-800.jpg 800w,
            hero-1200.jpg 1200w"
    sizes="(max-width: 600px) 100vw, 50vw"
    width="1200" 
    height="600"
    alt="Hero 图片"
    loading="lazy"
    decoding="async">
</picture>
```

### LCP 图片优先级
```html
<!-- 视口内 LCP 图片：急速加载，高优先级 -->
<img 
  src="hero.webp" 
  fetchpriority="high"
  loading="eager"
  decoding="sync"
  alt="Hero">

<!-- 视口外图片：懒加载 -->
<img 
  src="product.webp" 
  loading="lazy"
  decoding="async"
  alt="产品">
```

## 字体优化

### 加载策略
```css
/* 系统字体栈作为回退 */
body {
  font-family: 'Custom Font', -apple-system, BlinkMacSystemFont, 
               'Segoe UI', Roboto, sans-serif;
}

/* 防止文本不可见 */
@font-face {
  font-family: 'Custom Font';
  src: url('/fonts/custom.woff2') format('woff2');
  font-display: swap; /* 或可选的非关键 */
  font-weight: 400;
  font-style: normal;
  unicode-range: U+0000-00FF; /* 拉丁字母子集 */
}
```

### 预加载关键字体
```html
<link rel="preload" href="/fonts/heading.woff2" as="font" type="font/woff2" crossorigin>
```

### 可变字体
```css
/* 一个文件代替多个权重 */
@font-face {
  font-family: 'Inter';
  src: url('/fonts/Inter-Variable.woff2') format('woff2-variations');
  font-weight: 100 900;
  font-display: swap;
}
```

## 缓存策略

### Cache-Control 头部
```
# HTML (短或无缓存)
Cache-Control: no-cache, must-revalidate

# 带哈希的静态资源 (不可变)
Cache-Control: public, max-age=31536000, immutable

# 无哈希的静态资源
Cache-Control: public, max-age=86400, stale-while-revalidate=604800

# API 响应
Cache-Control: private, max-age=0, must-revalidate
```

### Service Worker 缓存
```javascript
// 静态资源缓存优先
self.addEventListener('fetch', (event) => {
  if (event.request.destination === 'image' ||
      event.request.destination === 'style' ||
      event.request.destination === 'script') {
    event.respondWith(
      caches.match(event.request).then((cached) => {
        return cached || fetch(event.request).then((response) => {
          const clone = response.clone();
          caches.open('static-v1').then((cache) => cache.put(event.request, clone));
          return response;
        });
      })
    );
  }
});
```

## 运行时性能

### 避免布局抖动
```javascript
// ❌ 强制多次重排
elements.forEach(el => {
  const height = el.offsetHeight; // 读取
  el.style.height = height + 10 + 'px'; // 写入
});

// ✅ 批量读取，然后批量写入
const heights = elements.map(el => el.offsetHeight); // 所有读取
elements.forEach((el, i) => {
  el.style.height = heights[i] + 10 + 'px'; // 所有写入
});
```

### 节流昂贵操作
```javascript
function debounce(fn, delay) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn(...args), delay);
  };
}

// 节流滚动/调整大小处理器
window.addEventListener('scroll', debounce(handleScroll, 100));
```

### 使用 requestAnimationFrame
```javascript
// ❌ 可能导致卡顿
setInterval(animate, 16);

// ✅ 与显示刷新同步
function animate() {
  // 动画逻辑
  requestAnimationFrame(animate);
}
requestAnimationFrame(animate);
```

### 虚拟化长列表
```javascript
// 对于超过 100 项的列表，仅渲染可见项
// 使用 react-window、vue-virtual-scroller 或原生 CSS：
.virtual-list {
  content-visibility: auto;
  contain-intrinsic-size: 0 50px; /* 预估项高度 */
}
```

### 使用 View Transitions 平滑导航

[View Transitions API](https://developer.chrome.com/docs/web-platform/view-transitions) 允许浏览器使用单个 GPU 合成的快照在两个 DOM 状态之间进行淡入淡出（或自定义动画）——没有双重渲染，没有布局抖动，快照不计入 CLS。

**同文档 (SPA 风格) — 基线 2026：**
```javascript
// 包装交换视图的 DOM 变化
function navigate(newView) {
  if (!document.startViewTransition) return swapDOM(newView);
  document.startViewTransition(() => swapDOM(newView));
}
```

**跨文档 (MPA 风格) — Chromium 稳定版，其他地方渐进增强：**
```css
/* 在源页和目标页上 */
@view-transition { navigation: auto; }
```
这就是全部集成——同源导航现在会自动淡入。要使特定元素进入共享元素过渡（例如缩略图扩展为英雄图），给它们一个匹配的 `view-transition-name`：
```css
.product-thumb[data-id="42"], .product-hero { view-transition-name: product-42; }
```
将其与上面的 Speculation Rules 配合使用，实现即时和动画导航。

## 第三方脚本

### 加载策略
```javascript
// ❌ 阻塞主线程
<script src="https://analytics.example.com/script.js"></script>

// ✅ 异步加载
<script async src="https://analytics.example.com/script.js"></script>

// ✅ 交互后延迟加载
<script>
document.addEventListener('DOMContentLoaded', () => {
  const observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting) {
      const script = document.createElement('script');
      script.src = 'https://widget.example.com/embed.js';
      document.body.appendChild(script);
      observer.disconnect();
    }
  });
  observer.observe(document.querySelector('#widget-container'));
});
</script>
```

### Facade 模式
```html
<!-- 交互前显示静态占位符 -->
<div class="youtube-facade" 
     data-video-id="abc123" 
     onclick="loadYouTube(this)">
  <img src="/thumbnails/abc123.jpg" alt="视频标题">
  <button aria-label="播放视频">▶</button>
</div>
```

## 测量

每次 URL 可运行时，使用 [测量工作流程](references/MEASUREMENT.md)。它定义了 Chrome DevTools MCP 路由、CrUX 和回退源、可重复的实验室条件以及紧凑的证据格式。

| 指标 | 类型 | 解释 |
|------|------|------|
| LCP、INP、CLS at p75 | 现场 | 用户结果核心网页指标；用于通过/失败优先级 |
| LCP、CLS 在追踪中 | 实验室 | 可重复的诊断值，针对单个导航 |
| TBT | 实验室 | 主线程阻塞诊断和 INP 的大致代理，不是现场 INP |
| FCP、Speed Index | 实验室 | 加载诊断，不是核心网页指标 |

原始 `PerformanceObserver` 片段对当前浏览器会话有用，但本身不是真实用户数据。当用户需要生产级遥测时，阅读 [第一方 RUM 参考](references/RUM.md)，并优先使用 `web-vitals` 而不是手写的指标实现。

## 参考文献

有关核心网页指标特定优化，请参阅 [Core Web Vitals](../core-web-vitals/SKILL.md)。
