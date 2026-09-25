识别并修复性能问题，以创造更快、更流畅的用户体验。

## 评估性能问题

了解当前性能并识别问题：

1. **测量当前状态**：
   - **核心网页指标**：LCP、FID/INP、CLS得分
   - **加载时间**：交互时间、首次内容绘制时间
   - **包大小**：JavaScript、CSS、图片大小
   - **运行时性能**：帧率、内存使用、CPU使用
   - **网络**：请求次数、有效载荷大小、瀑布图

2. **识别瓶颈**：
   - 慢在哪里？（初始加载？交互？动画？）
   - 原因是什么？（大图片？昂贵的JavaScript？布局抖动？）
   - 有多严重？（可感知？烦人？阻塞？）
   - 谁受影响？（所有用户？仅移动端？慢速连接？）

**关键**：优化前后都要测量。过早优化浪费时间。优化真正重要的事情。

## 优化策略

创建系统性的改进计划：

### 加载性能

**优化图片**：
- 使用现代格式（WebP、AVIF）
- 正确的尺寸（不要加载3000px的图片用于300px显示）
- 对折叠下方的图片进行懒加载
- 响应式图片（`srcset`、`picture`元素）
- 压缩图片（80-85%质量通常难以察觉）
- 使用CDN进行更快交付

```html
<img 
  src="hero.webp"
  srcset="hero-400.webp 400w, hero-800.webp 800w, hero-1200.webp 1200w"
  sizes="(max-width: 400px) 400px, (max-width: 800px) 800px, 1200px"
  loading="lazy"
  alt="Hero image"
/>
```

**减少JavaScript包**：
- 代码拆分（基于路由、基于组件）
- Tree shaking（移除未使用的代码）
- 移除未使用的依赖
- 懒加载非关键代码
- 使用动态导入大型组件

```javascript
// 懒加载重型组件
const HeavyChart = lazy(() => import('./HeavyChart'));
```

**优化CSS**：
- 移除未使用的CSS
- 关键CSS内联，其余异步加载
- 最小化CSS文件
- 使用CSS containment进行独立区域

**优化字体**：
- 使用`font-display: swap`或`optional`
- 字体子集（仅包含需要的字符）
- 预加载关键字体
- 适当使用系统字体
- 限制加载的字体粗细

```css
@font-face {
  font-family: 'CustomFont';
  src: url('/fonts/custom.woff2') format('woff2');
  font-display: swap; /* 立即显示备用字体 */
  unicode-range: U+0020-007F; /* 仅基本拉丁字母 */
}
```

**优化加载策略**：
- 首先加载关键资源（异步/延迟非关键资源）
- 预加载关键资源
- 预取可能的下一页
- Service worker用于离线/缓存
- HTTP/2或HTTP/3用于多路复用

### 渲染性能

**避免布局抖动**：
```javascript
// ❌ 坏：交替读写（导致重排）
elements.forEach(el => {
  const height = el.offsetHeight; // 读（强制布局）
  el.style.height = height * 2; // 写
});

// ✅ 好：批量读，然后批量写
const heights = elements.map(el => el.offsetHeight); // 所有读
elements.forEach((el, i) => {
  el.style.height = heights[i] * 2; // 所有写
});
```

**优化渲染**：
- 使用CSS `contain`属性进行独立区域
- 最小化DOM深度（扁平更快）
- 减少DOM大小（更少的元素）
- 使用`content-visibility: auto`用于长列表
- 虚拟滚动用于非常长的列表（react-window、react-virtualized）

**减少绘制与合成**：
- 使用`transform`和`opacity`进行动画（GPU加速）
- 避免动画布局属性（宽度、高度、top、left）
- 少量使用`will-change`用于已知昂贵操作
- 最小化绘制区域（越小越快）

### 动画性能

**GPU加速**：
```css
/* ✅ GPU加速（快） */
.animated {
  transform: translateX(100px);
  opacity: 0.5;
}

/* ❌ CPU绑定（慢） */
.animated {
  left: 100px;
  width: 300px;
}
```

**平滑60fps**：
- 目标16ms每帧（60fps）
- 使用`requestAnimationFrame`进行JS动画
- 节流/防抖滚动处理器
- 可能时使用CSS动画
- 动画期间避免长时间运行的JavaScript

**Intersection Observer**：
```javascript
// 高效检测元素进入视口
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      // 元素可见，懒加载或动画
    }
  });
});
```

### React/框架优化

**React特定**：
- 使用`memo()`进行昂贵组件
- `useMemo()`和`useCallback()`进行昂贵计算
- 虚拟化长列表
- 路由代码拆分
- 避免在渲染中创建内联函数
- 使用React DevTools Profiler

**框架无关**：
- 最小化重渲染
- 防抖昂贵操作
- 谨慎缓存计算值
- 懒加载路由和组件

### 网络优化

**减少请求**：
- 合并小文件
- 使用SVG精灵图标
- 内联小关键资源
- 移除未使用的第三方脚本

**优化API**：
- 使用分页（不要加载所有数据）
- GraphQL请求仅需要的字段
- 响应压缩（gzip、brotli）
- HTTP缓存头
- CDN用于静态资源

**针对慢速连接优化**：
- 基于连接（navigator.connection）的适应性加载
- 乐观UI更新
- 请求优先级
- 渐进增强

## 核心网页指标优化

### 最大内容绘制（LCP < 2.5s）
- 优化英雄图片
- 内联关键CSS
- 预加载关键资源
- 使用CDN
- 服务器端渲染

### 首次输入延迟（FID < 100ms） / INP (< 200ms)
- 分割长任务
- 延迟非关键JavaScript
- 使用Web workers进行重计算
- 减少JavaScript执行时间

### 累计布局偏移（CLS < 0.1）
- 图片和视频设置尺寸
- 不要在现有内容上方注入内容
- 使用`aspect-ratio` CSS属性
- 预留广告/嵌入空间
- 避免导致布局偏移的动画

```css
/* 预留图片空间 */
.image-container {
  aspect-ratio: 16 / 9;
}
```

## 性能监控

**使用工具**：
- Chrome DevTools（Lighthouse、性能面板）
- WebPageTest
- 核心网页指标（Chrome UX Report）
- 包分析器（webpack-bundle-analyzer）
- 性能监控（Sentry、DataDog、New Relic）

**关键指标**：
- LCP、FID/INP、CLS（核心网页指标）
- 交互时间（TTI）
- 首次内容绘制（FCP）
- 总阻塞时间（TBT）
- 包大小
- 请求次数

**重要**：在真实设备上使用真实网络条件测量。桌面Chrome快速连接不能代表实际情况。

**永远不要**：
- 不测量就优化（过早优化）
- 为性能牺牲可访问性
- 优化时破坏功能
- 滥用`will-change`（创建新层，消耗内存）
- 懒加载折叠上方的内容
- 优化微优化而忽略主要问题（先优化最大瓶颈）
- 忘记移动端性能（通常设备较慢，连接较慢）

## 验证改进

测试优化是否有效：

- **前后指标**：比较Lighthouse得分
- **真实用户监控**：跟踪真实用户的改进
- **不同设备**：在低端Android上测试，不只是旗舰iPhone
- **慢速连接**：限制为3G，测试体验
- **无回归**：确保功能仍然正常
- **用户感知**：感觉是否更快？

记住：性能是一项功能。快速体验感觉更响应、更精致、更专业。系统化优化，无情测量，优先考虑用户感知性能。
