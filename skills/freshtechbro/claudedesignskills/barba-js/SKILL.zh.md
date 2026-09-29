---
name: barba-js
description: 页面过渡库，用于在网站页面之间创建流畅、平滑的过渡效果。在实现页面过渡、创建类似SPA的体验、添加动画路由变化或构建具有平滑导航的网站时使用此技能。在涉及Barba.js、页面过渡、路由、视图管理、过渡钩子、GSAP集成或平滑页面导航的任务中触发。可与gsap-scrolltrigger配合使用，实现过渡动画效果。
---

# Barba.js

一个用于创建流畅、平滑页面过渡的现代库，可在网站页面之间进行切换。Barba.js 通过拦截导航和管理过渡来避免全页面的重新加载，使多页面网站感觉像单页应用程序（SPA）。

## 概述

Barba.js 是一个轻量级（最小化并压缩后7KB）的JavaScript库，它拦截页面之间的导航，通过AJAX获取新内容，并在旧容器和新容器之间平滑过渡。它减少了页面加载延迟和HTTP请求，同时保持了传统多页面架构的优点。

**核心特性**：
- 无需全页面重新加载的平滑页面过渡
- 生命周期钩子，用于精确控制过渡阶段
- 基于视图的逻辑，用于页面特定行为
- 内置路由（通过@barba/router插件）
- 可扩展的插件系统
- 小体积和高性能
- 框架无关（可与纯JavaScript、GSAP、anime.js等配合使用）

## 核心概念

### 1. Wrapper、Container和Namespace

Barba.js 使用特定的DOM结构来管理过渡：

**HTML结构**：
```html
<body data-barba="wrapper">
  <!-- 静态元素（头部、导航）保持在容器外 -->
  <header>
    <nav>
      <a href="/">首页</a>
      <a href="/about">关于</a>
    </nav>
  </header>

  <!-- 动态内容放在容器内 -->
  <main data-barba="container" data-barba-namespace="home">
    <!-- 此内容在导航时将发生变化 -->
    <h1>首页</h1>
    <p>将进行过渡的内容...</p>
  </main>

  <!-- 静态页脚保持在容器外 -->
  <footer>© 2025</footer>
</body>
```

**三个关键元素**：

1. **Wrapper** (`data-barba="wrapper"`)
   - 最外层容器
   - Wrapper内但Container外的所有内容保持持久
   - 适合头部、导航、页脚等不变化的元素

2. **Container** (`data-barba="container"`)
   - 动态内容区域，在导航时更新
   - 过渡期间仅此部分被替换
   - 每个页面都必须存在

3. **Namespace** (`data-barba-namespace="home"`)
   - 每种页面类型的唯一标识符
   - 用于过渡规则和视图逻辑
   - 示例："home"、"about"、"product"、"blog-post"

### 2. 过渡生命周期

Barba.js 对每次导航都遵循精确的生命周期：

**默认异步流程**：
1. 用户点击链接
2. Barba拦截导航
3. 预取下一页（通过AJAX）
4. 缓存新内容
5. **离开钩子** - 动画当前页面淡出
6. 等待离开动画完成
7. 移除旧容器，插入新容器
8. **进入钩子** - 动画新页面淡入
9. 等待进入动画完成
10. 更新浏览器历史记录

**同步流程**（使用`sync: true`）：
1. 用户点击链接
2. Barba拦截导航
3. 预取下一页
4. 等待新页面加载
5. **离开和进入钩子同时运行**（交叉淡入效果）
6. 交换容器
7. 更新浏览器历史记录

### 3. 钩子

Barba 提供了11个生命周期钩子用于控制过渡：

**钩子执行顺序**：
```
初始页面加载：
  beforeOnce → once → afterOnce

每次导航：
  before → beforeLeave → leave → afterLeave →
  beforeEnter → enter → afterEnter → after
```

**钩子类型**：
- **全局钩子**：每个过渡都运行（`barba.hooks.before()`）
- **过渡钩子**：定义在特定过渡对象内
- **视图钩子**：定义在视图对象内，用于页面特定逻辑

**常见钩子使用场景**：
- `beforeLeave` - 重置滚动位置，准备动画
- `leave` - 动画当前页面淡出
- `afterLeave` - 清理旧页面
- `beforeEnter` - 准备新页面（隐藏元素，设置初始状态）
- `enter` - 动画新页面淡入
- `afterEnter` - 初始化页面脚本，分析追踪

### 4. 视图

视图是基于namespace运行的页面特定逻辑容器：

```javascript
barba.init({
  views: [{
    namespace: 'home',
    beforeEnter() {
      // 首页特定设置
      console.log('进入首页');
    },
    afterEnter() {
      // 初始化首页功能
      initHomeSlider();
    }
  }, {
    namespace: 'product',
    beforeEnter() {
      console.log('进入产品页');
    },
    afterEnter() {
      initProductGallery();
    }
  }]
});
```

## 常见模式

### 1. 基本设置

**安装**：
```bash
npm install --save-dev @barba/core
# 或
yarn add @barba/core --dev
```

**最小配置**：
```javascript
import barba from '@barba/core';

barba.init({
  transitions: [{
    name: 'default',
    leave({ current }) {
      // 淡出当前页面
      return gsap.to(current.container, {
        opacity: 0,
        duration: 0.5
      });
    },
    enter({ next }) {
      // 淡入新页面
      return gsap.from(next.container, {
        opacity: 0,
        duration: 0.5
      });
    }
  }]
});
```

### 2. 淡入淡出过渡（异步）

经典的淡出淡入过渡：

```javascript
import barba from '@barba/core';
import gsap from 'gsap';

barba.init({
  transitions: [{
    name: 'fade',
    async leave({ current }) {
      await gsap.to(current.container, {
        opacity: 0,
        duration: 0.5,
        ease: 'power2.inOut'
      });
    },
    async enter({ next }) {
      // 开始时不可见
      gsap.set(next.container, { opacity: 0 });

      // 淡入
      await gsap.to(next.container, {
        opacity: 1,
        duration: 0.5,
        ease: 'power2.inOut'
      });
    }
  }]
});
```

### 3. 交叉淡入过渡（同步）

页面之间同时淡入淡出：

```javascript
barba.init({
  transitions: [{
    name: 'crossfade',
    sync: true, // 启用同步模式
    leave({ current }) {
      return gsap.to(current.container, {
        opacity: 0,
        duration: 0.8,
        ease: 'power2.inOut'
      });
    },
    enter({ next }) {
      return gsap.from(next.container, {
        opacity: 0,
        duration: 0.8,
        ease: 'power2.inOut'
      });
    }
  }]
});
```

### 4. 带重叠的滑动过渡

旧页面滑出，新页面滑入带重叠：

```javascript
barba.init({
  transitions: [{
    name: 'slide',
    sync: true,
    leave({ current }) {
      return gsap.to(current.container, {
        x: '-100%',
        duration: 0.7,
        ease: 'power3.inOut'
      });
    },
    enter({ next }) {
      // 开始时在屏幕右侧
      gsap.set(next.container, { x: '100%' });

      // 从右侧滑入
      return gsap.to(next.container, {
        x: '0%',
        duration: 0.7,
        ease: 'power3.inOut'
      });
    }
  }]
});
```

### 5. 过渡规则（条件过渡）

根据导航上下文定义不同的过渡：

```javascript
barba.init({
  transitions: [
    // 首页到任何页面：淡入
    {
      name: 'from-home-fade',
      from: { namespace: 'home' },
      leave({ current }) {
        return gsap.to(current.container, {
          opacity: 0,
          duration: 0.5
        });
      },
      enter({ next }) {
        return gsap.from(next.container, {
          opacity: 0,
          duration: 0.5
        });
      }
    },
    // 产品到产品：向左滑动
    {
      name: 'product-to-product',
      from: { namespace: 'product' },
      to: { namespace: 'product' },
      leave({ current }) {
        return gsap.to(current.container, {
          x: '-100%',
          duration: 0.6
        });
      },
      enter({ next }) {
        gsap.set(next.container, { x: '100%' });
        return gsap.to(next.container, {
          x: '0%',
          duration: 0.6
        });
      }
    },
    // 默认回退
    {
      name: 'default',
      leave({ current }) {
        return gsap.to(current.container, {
          opacity: 0,
          duration: 0.3
        });
      },
      enter({ next }) {
        return gsap.from(next.container, {
          opacity: 0,
          duration: 0.3
        });
      }
    }
  ]
});
```

### 6. 路由插件用于基于路由的过渡

使用`@barba/router`进行路由特定过渡：

**安装**：
```bash
npm install --save-dev @barba/router
```

**使用**：
```javascript
import barba from '@barba/core';
import barbaPrefetch from '@barba/prefetch';
import barbaRouter from '@barba/router';

// 定义路由
barbaRouter.init({
  routes: [
    { path: '/', name: 'home' },
    { path: '/about', name: 'about' },
    { path: '/products/:id', name: 'product' }, // 动态片段
    { path: '/blog/:category/:slug', name: 'blog-post' }
  ]
});

barba.use(barbaRouter);
barba.use(barbaPrefetch); // 可选：鼠标悬停时预取

barba.init({
  transitions: [{
    name: 'product-transition',
    to: { route: 'product' }, // 在路由名称触发
    leave({ current }) {
      return gsap.to(current.container, {
        scale: 0.95,
        opacity: 0,
        duration: 0.5
      });
    },
    enter({ next }) {
      return gsap.from(next.container, {
        scale: 1.05,
        opacity: 0,
        duration: 0.5
      });
    }
  }]
});
```

### 7. 加载指示器

在页面获取期间显示加载状态：

```javascript
barba.init({
  transitions: [{
    async leave({ current }) {
      // 显示加载器
      const loader = document.querySelector('.loader');
      gsap.set(loader, { display: 'flex', opacity: 0 });
      gsap.to(loader, { opacity: 1, duration: 0.3 });

      // 淡出页面
      await gsap.to(current.container, {
        opacity: 0,
        duration: 0.5
      });
    },
    async enter({ next }) {
      // 隐藏加载器
      const loader = document.querySelector('.loader');
      await gsap.to(loader, { opacity: 0, duration: 0.3 });
      gsap.set(loader, { display: 'none' });

      // 淡入页面
      await gsap.from(next.container, {
        opacity: 0,
        duration: 0.5
      });
    }
  }]
});
```

## 集成模式

### GSAP集成

Barba.js 与GSAP动画无缝协作：

**基于时间轴的过渡**：
```javascript
import barba from '@barba/core';
import gsap from 'gsap';

barba.init({
  transitions: [{
    async leave({ current }) {
      const tl = gsap.timeline();

      tl.to(current.container.querySelector('h1'), {
        y: -50,
        opacity: 0,
        duration: 0.3
      })
      .to(current.container.querySelector('.content'), {
        y: -30,
        opacity: 0,
        duration: 0.3
      }, '-=0.2')
      .to(current.container, {
        opacity: 0,
        duration: 0.2
      });

      await tl.play();
    },
    async enter({ next }) {
      const tl = gsap.timeline();

      // 设置初始状态
      gsap.set(next.container, { opacity: 0 });
      gsap.set(next.container.querySelector('h1'), { y: 50, opacity: 0 });
      gsap.set(next.container.querySelector('.content'), { y: 30, opacity: 0 });

      tl.to(next.container, {
        opacity: 1,
        duration: 0.2
      })
      .to(next.container.querySelector('h1'), {
        y: 0,
        opacity: 1,
        duration: 0.5,
        ease: 'power3.out'
      })
      .to(next.container.querySelector('.content'), {
        y: 0,
        opacity: 1,
        duration: 0.5,
        ease: 'power3.out'
      }, '-=0.3');

      await tl.play();
    }
  }]
});
```

**参考gsap-scrolltrigger技能**以获取高级GSAP集成模式。

### 视图特定初始化

按页面初始化库或脚本：

```javascript
barba.init({
  views: [{
    namespace: 'home',
    afterEnter() {
      // 初始化首页功能
      initHomepageSlider();
      initParallaxEffects();
    },
    beforeLeave() {
      // 清理
      destroyHomepageSlider();
    }
  },
  {
    namespace: 'gallery',
    afterEnter() {
      initLightbox();
      initMasonry();
    },
    beforeLeave() {
      destroyLightbox();
    }
  }]
});
```

### 分析追踪

在导航时追踪页面浏览：

```javascript
barba.hooks.after(() => {
  // Google Analytics
  if (typeof gtag !== 'undefined') {
    gtag('config', 'GA_MEASUREMENT_ID', {
      page_path: window.location.pathname
    });
  }

  // 或使用数据层
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({
    event: 'pageview',
    page: window.location.pathname
  });
});
```

### 第三方脚本重新初始化

页面过渡后重新运行脚本：

```javascript
barba.hooks.after(() => {
  // 重新初始化第三方小部件
  if (typeof twttr !== 'undefined') {
    twttr.widgets.load(); // Twitter小部件
  }

  if (typeof FB !== 'undefined') {
    FB.XFBML.parse(); // Facebook小部件
  }

  // 重新运行语法高亮
  if (typeof Prism !== 'undefined') {
    Prism.highlightAll();
  }
});
```

## 性能优化

### 1. 预取

使用`@barba/prefetch`在鼠标悬停时加载页面：

```bash
npm install --save-dev @barba/prefetch
```

```javascript
import barba from '@barba/core';
import barbaPrefetch from '@barba/prefetch';

barba.use(barbaPrefetch);

barba.init({
  // 预取默认在链接鼠标悬停时触发
  prefetch: {
    root: null, // 观察 所有链接
    timeout: 3000 // 缓存超时（毫秒）
  }
});
```

### 2. 防止布局偏移

设置容器最小高度以防止内容跳跃：

```css
[data-barba="container"] {
  min-height: 100vh;
  /* 或使用视口高度减去头部/页脚 */
  min-height: calc(100vh - 80px - 60px);
}
```

### 3. 优化动画

使用GPU加速属性：

```javascript
// ✅ 好 - GPU加速
gsap.to(element, {
  opacity: 0,
  x: -100,
  scale: 0.9,
  rotation: 45
});

// ❌ 避免 - 导致重排/重绘
gsap.to(element, {
  width: '50%',
  height: '300px',
  top: '100px'
});
```

### 4. 清理事件监听器

在`beforeLeave`或视图钩子中移除监听器：

```javascript
barba.init({
  views: [{
    namespace: 'home',
    afterEnter() {
      // 添加监听器
      this.clickHandler = () => console.log('clicked');
      document.querySelector('.btn').addEventListener('click', this.clickHandler);
    },
    beforeLeave() {
      // 移除监听器
      document.querySelector('.btn').removeEventListener('click', this.clickHandler);
    }
  }]
});
```

### 5. 懒加载图片

在过渡完成后延迟加载图片：

```javascript
barba.init({
  transitions: [{
    async enter({ next }) {
      // 首先完成过渡
      await gsap.from(next.container, {
        opacity: 0,
        duration: 0.5
      });

      // 然后加载图片
      const images = next.container.querySelectorAll('img[data-src]');
      images.forEach(img => {
        img.src = img.dataset.src;
        img.removeAttribute('data-src');
      });
    }
  }]
});
```

## 常见陷阱

### 1. 忘记返回Promise

**问题**：过渡立即完成，动画未等待。

**解决方案**：始终返回Promise或使用`async/await`：

```javascript
// ❌ 错误 - 动画开始但未等待
leave({ current }) {
  gsap.to(current.container, { opacity: 0, duration: 0.5 });
}

// ✅ 正确 - 返回Promise
leave({ current }) {
  return gsap.to(current.container, { opacity: 0, duration: 0.5 });
}

// ✅ 也正确 - async/await
async leave({ current }) {
  await gsap.to(current.container, { opacity: 0, duration: 0.5 });
}
```

### 2. 未阻止默认链接行为

**问题**：某些链接导致全页面重新加载。

**解决方案**：Barba自动阻止内部链接的默认行为，但您可能需要排除外部链接：

```javascript
barba.init({
  prevent: ({ href }) => {
    // 允许外部链接
    if (href.indexOf('http') > -1 && href.indexOf(window.location.host) === -1) {
      return true;
    }
    return false;
  }
});
```

### 3. 页面间CSS冲突

**问题**：旧页面CSS在过渡期间影响新页面布局。

**解决方案**：使用命名空间特定CSS或重置样式：

```css
/* 命名空间特定样式 */
[data-barba-namespace="home"] .hero {
  background: blue;
}

[data-barba-namespace="about"] .hero {
  background: red;
}
```

```javascript
beforeEnter({ next }) {
  // 重置滚动位置
  window.scrollTo(0, 0);

  // 重置任何全局状态
  document.body.classList.remove('menu-open');
}
```

### 4. 不会更新文档标题和元标签

**问题**：页面标题和元标签在导航时不会更新。

**解决方案**：使用 `@barba/head` 插件或手动更新：

```bash
npm install --save-dev @barba/head
```

```javascript
import barba from '@barba/core';
import barbaHead from '@barba/head';

barba.use(barbaHead);

barba.init({
  // 头部插件会自动更新 <head> 标签
});
```

或者手动：

```javascript
barba.hooks.after(({ next }) => {
  // 更新标题
  document.title = next.html.querySelector('title').textContent;

  // 更新元标签
  const newMeta = next.html.querySelectorAll('meta');
  newMeta.forEach(meta => {
    const name = meta.getAttribute('name') || meta.getAttribute('property');
    if (name) {
      const existing = document.querySelector(`meta[name="${name}"], meta[property="${name}"]`);
      if (existing) {
        existing.setAttribute('content', meta.getAttribute('content'));
      }
    }
  });
});
```

### 5. 进入动画闪烁

**问题**：新页面在进入动画开始前会闪烁可见。

**解决方案**：在 CSS 或 `beforeEnter` 中设置初始不可见状态：

```css
/* CSS 方法 */
[data-barba="container"] {
  opacity: 0;
}

[data-barba="container"].is-visible {
  opacity: 1;
}
```

```javascript
// JavaScript 方法
beforeEnter({ next }) {
  gsap.set(next.container, { opacity: 0 });
}
```

### 6. 同步过渡时定位不正确

**问题**：同步过渡会导致容器堆叠，造成布局偏移。

**解决方案**：在过渡期间将容器绝对定位：

```css
[data-barba="wrapper"] {
  position: relative;
}

[data-barba="container"] {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
}
```

或者用 JavaScript 管理：

```javascript
barba.init({
  transitions: [{
    sync: true,
    beforeLeave({ current }) {
      gsap.set(current.container, {
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%'
      });
    }
  }]
});
```

## 资源

这项技能包括：

### scripts/
用于常见 Barba.js 任务的执行工具：
- `transition_generator.py` - 生成过渡模板代码
- `project_setup.py` - 初始化 Barba.js 项目结构

### references/
详细文档：
- `api_reference.md` - 完整的 Barba.js API（钩子、过渡、视图、路由）
- `hooks_guide.md` - 所有 11 个钩子的执行顺序和使用场景
- `gsap_integration.md` - 用于 Barba 过渡的 GSAP 动画模式
- `transition_patterns.md` - 常见的过渡实现

### assets/
模板和启动项目：
- `starter_barba/` - 完整的 Barba.js + GSAP 启动模板
- `examples/` - 真实的过渡实现

## 相关技能

- **gsap-scrolltrigger** - 用于过渡中的高级 GSAP 动画
- **locomotive-scroll** - 可与 Barba 结合实现平滑页面滚动
- **motion-framer** - React 基于页面的过渡的替代方案
