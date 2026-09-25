# 核心网页指标优化

针对三个核心网页指标进行定向优化，使用现场数据识别用户影响，并利用浏览器追踪诊断原因。

## 优化前先测量

当可运行的URL可用时，请阅读[性能测量工作流](../performance/references/MEASUREMENT.md)。建议按以下顺序操作：

1. 检查页面级别的CrUX p75数据，当页面数据不可用时，提供清晰的原始回退标记。
2. 在指定条件下记录浏览器性能追踪。使用Chrome DevTools MCP，追踪摘要可以包含CrUX以及观察到的实验室指标。
3. 仅分析与失败指标相关的洞察，然后检查相关的代码和资源。
4. 修复后重新运行等效的实验室测量。不要声称立即的现场改进；CrUX和第一方RUM需要新的用户访问。

如果只有源代码可用，请识别可能的原因，但在没有运行时证据的情况下，不要声称LCP、INP或CLS正在失败。

## 三个指标

| 指标 | 衡量 | 优秀 | 需要改进 | 差 |
|------|------|------|----------|------|
| **LCP** | 加载 | ≤ 2.5秒 | 2.5秒 – 4秒 | > 4秒 |
| **INP** | 交互性 | ≤ 200毫秒 | 200毫秒 – 500毫秒 | > 500毫秒 |
| **CLS** | 视觉稳定性 | ≤ 0.1 | 0.1 – 0.25 | > 0.25 |

Google以**75分位**进行测量——75%的页面访问必须满足“优秀”阈值。

---

## LCP：最大内容绘制

LCP衡量最大可见内容元素渲染的时间。通常这包括：
- 英雄图片或视频
- 大型文本块
- 背景图片
- `<svg>`元素

### 常见的LCP问题

**1. 服务器响应缓慢（TTFB > 800毫秒）**
```
修复：CDN、缓存、优化的后端、边缘渲染
```

**2. 阻塞渲染的资源**
```html
<!-- ❌ 阻塞渲染 -->
<link rel="stylesheet" href="/all-styles.css">

<!-- ✅ 关键CSS内联，其余延迟 -->
<style>/* 关键顶部CSS */</style>
<link rel="preload" href="/styles.css" as="style" 
      onload="this.onload=null;this.rel='stylesheet'">
```

**3. 资源加载时间缓慢**
```html
<!-- ❌ LCP图片在样式表加载后才被发现 -->
<div class="hero"></div>

<!-- ✅ 在初始HTML中发现并优先处理 -->
<link rel="preload" href="/hero.webp" as="image" fetchpriority="high">
<img src="/hero.webp" alt="英雄" fetchpriority="high">
```

优先使用带有`fetchpriority="high"`的`<img>`。仅在追踪显示资源会延迟发现时才添加预加载；重复或推测性预加载可能会竞争带宽。

**4. 客户端渲染延迟**
```javascript
// ❌ 内容在JavaScript加载后才加载
useEffect(() => {
  fetch('/api/hero-text').then(r => r.json()).then(setHeroText);
}, []);

// ✅ 服务器端或静态渲染
// 使用SSR、SSG或流式传输将包含内容的HTML发送
export async function getServerSideProps() {
  const heroText = await fetchHeroText();
  return { props: { heroText } };
}
```

**5. 使用Speculation Rules API使导航即时**

对于具有可预测同源旅程的网站，预渲染可能的下一页可以使后续成功导航更快。将其视为测量的导航优化，而不是修复当前页面LCP的替代方案。

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

当前Chrome行为足够具体，可以指导选择：

| `eagerness` | 触发 |
|-------------|------|
| `conservative` | 指针或触摸按下 |
| `moderate` | 桌面：200毫秒悬停，或更早的指针按下；移动：视口启发式 |
| `eager` | Chrome 143+: 桌面10毫秒悬停；移动：锚点进入视口后50毫秒 |
| `immediate` | 规则观察到后立即 |

从保守开始，在扩展规则之前测量预测命中率、传输字节数、服务器负载和导航改进。在硬编码时间敏感行为之前，重新检查[Chrome的维护eagerness文档](https://developer.chrome.com/docs/web-platform/prerender-pages#eagerness)。

注意事项：
- **带宽/CPU成本。** 每个预渲染大致相当于一个完整页面加载。仔细范围`where`（`href_matches`模式，排除注销/结账）并避免在小型网站外使用`immediate`。
- **副作用提前触发。** 分析、广告以及任何在加载时运行的代码将在预渲染开始时触发，而不是用户导航时。在[`prerenderingchange`事件](https://developer.chrome.com/docs/web-platform/prerender-pages#detect_when_a_page_is_prerendered_or_used_for_a_full_navigation)或`document.prerendering`上限制副作用。
- **仅限Chromium。** Safari和Firefox忽略此脚本——它是一种渐进增强，永远不会是回归。

### LCP优化清单

```markdown
- [ ] TTFB < 800毫秒（使用CDN、边缘缓存）
- [ ] LCP资源在初始HTML中发现并优先处理；仅在追踪显示延迟发现时预加载
- [ ] LCP图片优化（WebP/AVIF，正确大小）
- [ ] 关键CSS内联（< 14KB）
- [ ] <head>中没有阻塞渲染的JavaScript
- [ ] 字体不会阻塞文本渲染（font-display: swap）
- [ ] LCP元素在初始HTML中（不是JS渲染的）
- [ ] 为可能的下一导航添加Speculation Rules（moderate eagerness）
```

### LCP元素识别

此代码片段诊断当前页面会话。它不是现场数据。

```javascript
// 找到你的LCP元素
new PerformanceObserver((list) => {
  const entries = list.getEntries();
  const lastEntry = entries[entries.length - 1];
  console.log('LCP元素:', lastEntry.element);
  console.log('LCP时间:', lastEntry.startTime);
}).observe({ type: 'largest-contentful-paint', buffered: true });
```

---

## INP：交互到下一次绘制

INP衡量访问期间点击、轻触和按键的响应性。分别诊断其输入延迟、处理时间和呈现延迟；慢速交互可能涉及主线程争用、昂贵的应用程序工作或处理后的延迟渲染。

当现场INP较差或追踪识别出慢速交互时，请阅读[INP参考](references/INP.md)以解释追踪，提供模式、第三方和渲染原因、单会话观察者和第一方归因。

---

## CLS：累积布局偏移

CLS衡量页面访问期间意外的布局偏移。使用现场归因或追踪识别偏移节点和触发器；不要假设可见的受害者导致了偏移。

当现场CLS较差或追踪报告偏移时，请阅读[CLS参考](references/CLS.md)以了解保留空间模式、动态内容、字体和动画修复、调试观察者和验证清单。

---

## 测量来源

| 来源 | 使用 |
|------|------|
| 浏览器性能追踪（Chrome DevTools MCP: `performance_start_trace`） | 观察一次加载或交互并诊断聚焦洞察；当可用时使用包含的CrUX上下文 |
| CrUX或搜索控制台 | 优先考虑p75的聚合真实用户结果 |
| Lighthouse CLI或PageSpeed Insights | 当DevTools工具不可用时，作为受控实验室回退 |
| 第一方RUM | 按路由、设备、版本和归因细分当前生产体验 |
| 原始`PerformanceObserver` | 在调试期间检查一个页面会话 |

不要通过Chrome DevTools MCP的`lighthouse_audit`路由性能；该功能有意涵盖非性能Lighthouse类别。不要将单个实验室值直接与现场p75进行比较，就好像它们是等效样本。

添加或审查生产收集时，请阅读[第一方RUM参考](../performance/references/RUM.md)。优先使用`web-vitals`库，因为原始浏览器API本身并不实现核心网页指标的生命周期和报告规则。

---

## 框架快速修复

### Next.js
```jsx
// LCP：使用next/image带优先级
import Image from 'next/image';
<Image src="/hero.jpg" priority fill alt="英雄" />

// INP：使用动态导入
const HeavyComponent = dynamic(() => import('./Heavy'), { ssr: false });

// CLS：图片组件自动处理尺寸
```

### React
```jsx
// LCP：在head中预加载
<link rel="preload" href="/hero.jpg" as="image" fetchpriority="high" />

// INP：Memoize和useTransition
const [isPending, startTransition] = useTransition();
startTransition(() => setExpensiveState(newValue));

// CLS：在img标签中始终指定尺寸
```

### Vue/Nuxt
```vue
<!-- LCP：使用nuxt/image带预加载 -->
<NuxtImg src="/hero.jpg" preload loading="eager" />

<!-- INP：使用异步组件 -->
<component :is="() => import('./Heavy.vue')" />

<!-- CLS：使用aspect-ratio CSS -->
<img :style="{ aspectRatio: '16/9' }" />
```

## 参考

- [详细LCP优化](references/LCP.md) — 当LCP追踪指向发现、加载或渲染延迟时阅读
- [详细INP优化](references/INP.md) — 当追踪或现场归因识别出慢速交互时阅读
- [详细CLS优化](references/CLS.md) — 当追踪或现场归因识别出意外偏移时阅读
- [web.dev LCP](https://web.dev/articles/lcp)
- [web.dev INP](https://web.dev/articles/inp)
- [web.dev CLS](https://web.dev/articles/cls)
- [性能技能](../performance/SKILL.md)
