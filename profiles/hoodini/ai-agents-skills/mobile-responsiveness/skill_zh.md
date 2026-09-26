# 移动端响应式设计

构建响应式、移动优先的 Web 应用。

## 移动优先断点

```css
/* 移动优先 - 无需媒体查询即可适用于移动端基础 */
.container {
  padding: 1rem;
}

/* 平板 */
@media (min-width: 768px) {
  .container {
    padding: 2rem;
  }
}

/* 桌面端 */
@media (min-width: 1024px) {
  .container {
    padding: 3rem;
    max-width: 1200px;
    margin: 0 auto;
  }
}

/* 大型桌面端 */
@media (min-width: 1280px) {
  .container {
    max-width: 1400px;
  }
}
```

## Tailwind 断点

```tsx
<div className="
  p-4          /* 移动端: padding 1rem */
  md:p-8       /* 平板 768px+: padding 2rem */
  lg:p-12      /* 桌面端 1024px+: padding 3rem */
  xl:max-w-6xl /* 大型 1280px+: 最大宽度 */
">
  <h1 className="
    text-2xl     /* 移动端 */
    md:text-3xl  /* 平板 */
    lg:text-4xl  /* 桌面端 */
  ">
    响应式标题
  </h1>
</div>
```

## 流体化排版

```css
:root {
  /* 流体化字体大小: 320px 视口宽度时 16px，1200px 视口宽度时 20px */
  --font-size-base: clamp(1rem, 0.9rem + 0.5vw, 1.25rem);
  
  /* 流体化标题 */
  --font-size-h1: clamp(2rem, 1.5rem + 2.5vw, 4rem);
}

body {
  font-size: var(--font-size-base);
}

h1 {
  font-size: var(--font-size-h1);
}
```

## 触摸交互

```tsx
import { useState } from 'react';

function SwipeableCard({ onSwipeLeft, onSwipeRight, children }) {
  const [touchStart, setTouchStart] = useState<number | null>(null);
  const [touchEnd, setTouchEnd] = useState<number | null>(null);

  const minSwipeDistance = 50;

  const onTouchStart = (e: React.TouchEvent) => {
    setTouchEnd(null);
    setTouchStart(e.targetTouches[0].clientX);
  };

  const onTouchMove = (e: React.TouchEvent) => {
    setTouchEnd(e.targetTouches[0].clientX);
  };

  const onTouchEnd = () => {
    if (!touchStart || !touchEnd) return;
    
    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > minSwipeDistance;
    const isRightSwipe = distance < -minSwipeDistance;
    
    if (isLeftSwipe) onSwipeLeft?.();
    if (isRightSwipe) onSwipeRight?.();
  };

  return (
    <div
      onTouchStart={onTouchStart}
      onTouchMove={onTouchMove}
      onTouchEnd={onTouchEnd}
    >
      {children}
    </div>
  );
}
```

## 移动端导航

```tsx
import { useState } from 'react';

function MobileNav() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* 汉堡按钮 - 仅在移动端可见 */}
      <button
        className="md:hidden p-2"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-label="切换菜单"
      >
        <span className={`hamburger ${isOpen ? 'open' : ''}`} />
      </button>

      {/* 移动端菜单 */}
      <nav
        className={`
          fixed inset-0 bg-white z-50 transform transition-transform
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
          md:static md:translate-x-0 md:bg-transparent
        `}
      >
        <ul className="flex flex-col md:flex-row gap-4 p-4 md:p-0">
          <li><a href="/">首页</a></li>
          <li><a href="/about">关于</a></li>
          <li><a href="/contact">联系</a></li>
        </ul>
      </nav>

      {/* 背景遮罩 */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
}
```

## 安全区域（刘海屏/主屏幕指示器）

```css
/* 考虑 iPhone 的刘海屏和主屏幕指示器 */
.container {
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
  padding-bottom: env(safe-area-inset-bottom);
}

/* 固定底部导航 */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding-bottom: max(1rem, env(safe-area-inset-bottom));
}
```

## 视口元标签

```html
<meta 
  name="viewport" 
  content="width=device-width, initial-scale=1, viewport-fit=cover"
/>
```

## useMediaQuery Hook

```tsx
import { useState, useEffect } from 'react';

function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const media = window.matchMedia(query);
    setMatches(media.matches);

    const listener = (e: MediaQueryListEvent) => setMatches(e.matches);
    media.addEventListener('change', listener);
    
    return () => media.removeEventListener('change', listener);
  }, [query]);

  return matches;
}

// 使用示例
function Component() {
  const isMobile = useMediaQuery('(max-width: 767px)');
  const isTablet = useMediaQuery('(min-width: 768px) and (max-width: 1023px)');
  const isDesktop = useMediaQuery('(min-width: 1024px)');

  return isMobile ? <MobileView /> : <DesktopView />;
}
```

## 资源

- **响应式设计**: https://web.dev/learn/design/
- **移动优先 CSS**: https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design
- **视口单位**: https://developer.mozilla.org/en-US/docs/Web/CSS/length#viewport-percentage_lengths
