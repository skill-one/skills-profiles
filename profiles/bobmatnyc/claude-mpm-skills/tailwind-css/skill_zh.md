# Tailwind CSS 技能

---
progressive_disclosure:
  entry_point:
    - summary
    - when_to_use
    - quick_start
  sections:
    core_concepts:
      - utility_first_approach
      - responsive_design
      - configuration
    advanced:
      - dark_mode
      - custom_utilities
      - plugins
      - performance_optimization
    integration:
      - framework_integration
      - component_patterns
    reference:
      - common_utilities
      - breakpoints
      - color_system
tokens:
  entry: 75
  full: 4500
---

## 概述

Tailwind CSS 是一个以工具优先的 CSS 框架，它提供低级别的工具类来构建自定义设计，而无需编写 CSS。它提供响应式设计、暗黑模式、通过配置进行自定义，并能与现代框架无缝集成。

## 何时使用

**最适合：**
- 使用一致的设计系统进行快速原型设计
- 基于组件的框架（React、Vue、Svelte）
- 需要响应式和暗黑模式支持的项目
- 希望避免维护 CSS 文件的开发团队
- 具有标准化间距/颜色的设计系统

**考虑替代方案的情况：**
- 团队不熟悉工具优先方法（学习曲线）
- 项目需要大量自定义 CSS 动画
- 需要支持旧版浏览器（IE11）
- 需要在没有构建过程的情况下实现极小 CSS 脚本大小

## 快速入门

### 安装

```bash
# npm
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# yarn
yarn add -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# pnpm
pnpm add -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 配置

**tailwind.config.js:**
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

### 基本CSS设置

**styles/globals.css:**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 第一个组件

```jsx
// 使用Tailwind工具类的简单按钮
function Button({ children, variant = 'primary' }) {
  const baseClasses = "px-4 py-2 rounded-lg font-medium transition-colors";
  const variants = {
    primary: "bg-blue-600 text-white hover:bg-blue-700",
    secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300",
    danger: "bg-red-600 text-white hover:bg-red-700"
  };

  return (
    <button className={`${baseClasses} ${variants[variant]}`}>
      {children}
    </button>
  );
}
```

---

## 核心概念

### 工具优先方法

Tailwind 提供直接映射到 CSS 属性的单用途工具类。

#### 布局工具

**Flexbox:**
```jsx
// 居中的flex容器
<div className="flex items-center justify-center">
  <div>居中内容</div>
</div>

// 响应式flex方向
<div className="flex flex-col md:flex-row gap-4">
  <div className="flex-1">列1</div>
  <div className="flex-1">列2</div>
</div>

// Flex换行和排列
<div className="flex flex-wrap items-start justify-between">
  <div className="w-1/2 md:w-1/4">项目</div>
  <div className="w-1/2 md:w-1/4">项目</div>
</div>
```

**Grid:**
```jsx
// 基本网格
<div className="grid grid-cols-3 gap-4">
  <div>1</div>
  <div>2</div>
  <div>3</div>
</div>

// 响应式网格
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  <div className="col-span-1 md:col-span-2">宽项目</div>
  <div>项目</div>
  <div>项目</div>
</div>

// 自动适应网格
<div className="grid grid-cols-[repeat(auto-fit,minmax(250px,1fr))] gap-4">
  <div>自动大小项目</div>
  <div>自动大小项目</div>
</div>
```

#### 间距系统

**填充和边距:**
```jsx
// 统一间距
<div className="p-4">所有边距填充</div>
<div className="m-8">所有边距</div>

// 方向性间距
<div className="pt-4 pb-8 px-6">顶部4，底部8，水平6</div>
<div className="ml-auto mr-0">右对齐边距</div>

// 负边距
<div className="mt-4 -mb-2">底部重叠</div>

// 响应式间距
<div className="p-2 md:p-4 lg:p-8">响应式填充</div>
```

**Space Between:**
```jsx
// 子元素之间的间距
<div className="flex gap-4">
  <div>项目1</div>
  <div>项目2</div>
</div>

// 响应式间距
<div className="grid grid-cols-3 gap-2 md:gap-4 lg:gap-6">
  <div>1</div>
  <div>2</div>
  <div>3</div>
</div>
```

#### 字体排版

```jsx
// 字体大小和粗细
<h1 className="text-4xl font-bold">标题</h1>
<p className="text-base font-normal leading-relaxed">段落</p>
<span className="text-sm font-medium text-gray-600">标题</span>

// 文本对齐和装饰
<p className="text-center underline">居中对齐下划线文本</p>
<p className="text-right line-through">右对齐删除线</p>

// 响应式字体排版
<h1 className="text-2xl md:text-4xl lg:text-6xl font-bold">
  响应式标题
</h1>

// 文本溢出处理
<p className="truncate">这段文本将被截断并显示省略号...</p>
<p className="line-clamp-3">
  这段文本将被限制为3行并显示省略号...
</p>
```

#### 颜色

```jsx
// 背景颜色
<div className="bg-blue-500">蓝色背景</div>
<div className="bg-gray-100 dark:bg-gray-800">自适应背景</div>

// 文本颜色
<p className="text-red-600">红色文本</p>
<p className="text-gray-700 dark:text-gray-300">自适应文本</p>

// 边框颜色
<div className="border border-gray-300 hover:border-blue-500">
  悬停边框
</div>

// 不透明度修饰
<div className="bg-blue-500/50">50% 不透明度蓝色</div>
<div className="bg-black/25">25% 不透明度黑色</div>
```

### 响应式设计

Tailwind 使用移动优先的断点系统。

#### 断点

```javascript
// 默认断点 (tailwind.config.js)
{
  theme: {
    screens: {
      'sm': '640px',   // 小设备
      'md': '768px',   // 中等设备
      'lg': '1024px',  // 大设备
      'xl': '1280px',  // 超大
      '2xl': '1536px', // 2倍超大
    }
  }
}
```

#### 响应式模式

```jsx
// 在断点处隐藏/显示
<div className="hidden md:block">在桌面端可见</div>
<div className="block md:hidden">在移动端可见</div>

// 响应式布局
<div className="
  flex flex-col          // 移动端：垂直堆叠
  md:flex-row           // 桌面端：水平
  gap-4 md:gap-8        // 桌面端：更大间距
">
  <aside className="w-full md:w-64">侧边栏</aside>
  <main className="flex-1">内容</main>
</div>

// 响应式网格
<div className="
  grid
  grid-cols-1           // 移动端：1列
  sm:grid-cols-2        // 小屏：2列
  lg:grid-cols-3        // 大屏：3列
  xl:grid-cols-4        // 超大屏：4列
  gap-4
">
  {items.map(item => <Card key={item.id} {...item} />)}
</div>

// 响应式容器
<div className="
  container mx-auto
  px-4 sm:px-6 lg:px-8
  max-w-7xl
">
  <h1>响应式容器</h1>
</div>
```

### 配置

#### 主题扩展

**tailwind.config.js:**
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#0ea5e9',
          900: '#0c4a6e',
        },
        accent: '#ff6b6b',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Poppins', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
      fontSize: {
        '2xs': '0.625rem',
        '3xl': '2rem',
      },
      borderRadius: {
        '4xl': '2rem',
      },
      boxShadow: {
        'inner-lg': 'inset 0 2px 4px 0 rgb(0 0 0 / 0.1)',
      },
      animation: {
        'slide-in': 'slideIn 0.3s ease-out',
        'fade-in': 'fadeIn 0.2s ease-in',
      },
      keyframes: {
        slideIn: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
```

#### 自定义断点

```javascript
module.exports = {
  theme: {
    screens: {
      'xs': '475px',
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1280px',
      '2xl': '1536px',
      '3xl': '1920px',
      // 自定义断点
      'tablet': '640px',
      'laptop': '1024px',
      'desktop': '1280px',
      // 最大宽度断点
      'max-md': {'max': '767px'},
    },
  },
}
```

---

## 高级功能

### 暗黑模式

#### 类策略（推荐）

**tailwind.config.js:**
```javascript
module.exports = {
  darkMode: 'class', // or 'media' for OS preference
  // ...
}
```

**实现:**
```jsx
// 切换组件
function DarkModeToggle() {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  return (
    <button
      onClick={() => setIsDark(!isDark)}
      className="p-2 rounded-lg bg-gray-200 dark:bg-gray-700"
    >
      {isDark ? '🌞' : '🌙'}
    </button>
  );
}

// 暗黑模式样式
function Card() {
  return (
    <div className="
      bg-white dark:bg-gray-800
      text-gray-900 dark:text-gray-100
      border border-gray-200 dark:border-gray-700
      shadow-lg dark:shadow-none
    ">
      <h2 className="text-xl font-bold mb-2">Card Title</h2>
      <p className="text-gray-600 dark:text-gray-400">
        Card content adapts to dark mode
      </p>
    </div>
  );
}
```

#### 系统偏好策略

```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'media', // Uses OS preference
}
```

```jsx
// 自动适应系统偏好
<div className="bg-white dark:bg-gray-900">
  内容自动适应
</div>
```

### 自定义工具

#### 添加自定义工具

**tailwind.config.js:**
```javascript
const plugin = require('tailwindcss/plugin');

module.exports = {
  plugins: [
    plugin(function({ addUtilities, addComponents, theme }) {
      // 自定义工具
      addUtilities({
        '.scrollbar-hide': {
          '-ms-overflow-style': 'none',
          'scrollbar-width': 'none',
          '&::-webkit-scrollbar': {
            display: 'none',
          },
        },
        '.text-balance': {
          'text-wrap': 'balance',
        },
      });

      // 自定义组件
      addComponents({
        '.btn': {
          padding: theme('spacing.4'),
          borderRadius: theme('borderRadius.lg'),
          fontWeight: theme('fontWeight.medium'),
          '&:hover': {
            opacity: 0.9,
          },
        },
        '.card': {
          backgroundColor: theme('colors.white'),
          borderRadius: theme('borderRadius.lg'),
          padding: theme('spacing.6'),
          boxShadow: theme('boxShadow.lg'),
        },
      });
    }),
  ],
}
```

#### 自定义变体

```javascript
const plugin = require('tailwindcss/plugin');

module.exports = {
  plugins: [
    plugin(function({ addVariant }) {
      // 自定义变体为第三个子元素
      addVariant('third', '&:nth-child(3)');

      // 自定义变体为非最后一个子元素
      addVariant('not-last', '&:not(:last-child)');

      // 自定义变体为 group-hover 时的特定元素
      addVariant('group-hover-show', '.group:hover &');
    }),
  ],
}

// 使用
<div className="third:font-bold not-last:border-b">
  自定义变体样式
</div>
```

### 插件

#### 官方插件

```bash
npm install -D @tailwindcss/forms @tailwindcss/typography @tailwindcss/aspect-ratio
```

**tailwind.config.js:**
```javascript
module.exports = {
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
}
```

#### Forms 插件

```jsx
// 自动表单样式
<form className="space-y-4">
  <input
    type="text"
    className="
      form-input
      rounded-lg
      border-gray-300
      focus:border-blue-500
      focus:ring-blue-500
    "
    placeholder="Name"
  />

  <select className="form-select rounded-lg">
    <option>Option 1</option>
    <option>Option 2</option>
  </select>

  <label className="flex items-center">
    <input type="checkbox" className="form-checkbox text-blue-600" />
    <span className="ml-2">同意条款</span>
  </label>
</form>
```

#### Typography 插件

```jsx
// 美观的排版样式
<article className="
  prose
  prose-lg
  prose-slate
  dark:prose-invert
  max-w-none
">
  <h1>Article Title</h1>
  <p>自动排版样式用于markdown内容...</p>
  <ul>
    <li>样式化列表</li>
    <li>适当的间距</li>
  </ul>
</article>
```

#### Aspect Ratio 插件

```jsx
// 保持宽高比
<div className="aspect-w-16 aspect-h-9">
  <iframe src="..." className="w-full h-full" />
</div>

<div className="aspect-square">
  <img src="..." className="object-cover w-full h-full" />
</div>
```

### 性能优化

#### 内容配置

```javascript
// 优化purge路径
module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx}',
    './public/index.html',
    // 包含组件库
    './node_modules/@my-ui/**/*.js',
  ],
  // 安全列表动态类
  safelist: [
    'bg-red-500',
    'bg-green-500',
    {
      pattern: /bg-(red|green|blue)-(400|500|600)/,
      variants: ['hover', 'focus'],
    },
  ],
}
```

#### JIT 模式（v3+默认）

即时编译模式按需生成样式：

```jsx
// 随意值可以立即工作
<div className="top-[117px]">自定义值</div>
<div className="bg-[#1da1f2]">自定义颜色</div>
<div className="grid-cols-[1fr_500px_2fr]">自定义网格</div>

// 无需重新构建新工具
<div className="before:content-['★']">星号前缀</div>
```

#### 构建优化

```javascript
// postcss.config.js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
    // 生产最小化
    ...(process.env.NODE_ENV === 'production'
      ? { cssnano: {} }
      : {}),
  },
}
```

---

## 框架集成

### React / Next.js

**安装:**
```bash
npx create-next-app@latest my-app --tailwind
# or add to existing project
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

**next.config.js:**
```javascript
/** @type {import('next').NextConfig} */
module.exports = {
  // Tailwind works out of box with Next.js
}
```

**_app.tsx:**
```typescript
import '@/styles/globals.css'
import type { AppProps } from 'next/app'

export default function App({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />
}
```

**组件示例:**
```tsx
// components/Button.tsx
import { ButtonHTMLAttributes, forwardRef } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-lg font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "bg-blue-600 text-white hover:bg-blue-700",
        outline: "border border-gray-300 hover:bg-gray-100",
        ghost: "hover:bg-gray-100",
      },
      size: {
        sm: "px-3 py-1.5 text-sm",
        md: "px-4 py-2",
        lg: "px-6 py-3 text-lg",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "md",
    },
  }
)

interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) {
    return (
      <button
        ref={ref}
        className={buttonVariants({ variant, size, className })}
        {...props}
      />
    )
  }
)

export default Button
```

### SvelteKit

**安装:**
```bash
npx sv create my-app
# Select Tailwind CSS option
# or add to existing
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

**svelte.config.js:**
```javascript
import adapter from '@sveltejs/adapter-auto';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

export default {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter()
  }
};
```

**组件示例:**
```svelte
<!-- Button.svelte -->
<script lang="ts">
  export let variant: 'primary' | 'secondary' = 'primary';
  export let size: 'sm' | 'md' | 'lg' = 'md';

  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300'
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg'
  };
</script>

<button
  class="rounded-lg font-medium transition-colors {variants[variant]} {sizes[size]}"
  on:click
>
  <slot />
</button>
```

### Vue 3

**安装:**
```bash
npm create vue@latest my-app
# Select Tailwind CSS
# or add to existing
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

**main.ts:**
```typescript
import { createApp } from 'vue'
import App from './App.vue'
import './assets/main.css'

createApp(App).mount('#app')
```

**组件示例:**
```vue
<!-- Button.vue -->
<script setup lang="ts">
  import { computed } from 'vue'

interface Props {
  variant?: 'primary' | 'secondary'
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md'
})

const classes = computed(() => {
  const base = 'rounded-lg font-medium transition-colors'
  const variants = {
    primary: "bg-blue-600 text-white hover:bg-blue-700",
    secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300"
  }
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg'
  }

  return `${base} ${variants[props.variant]} ${sizes[props.size]}`
})
</script>

<template>
  <button :class="classes">
    <slot />
  </button>
</template>
```

---

## 组件模式

### 布局组件

#### 容器

```jsx
function Container({ children, size = 'default' }) {
  const sizes = {
    sm: 'max-w-3xl',
    default: 'max-w-7xl',
    full: 'max-w-full'
  };

  return (
    <div className={`container mx-auto px-4 sm:px-6 lg:px-8 ${sizes[size]}`}>
      {children}
    </div>
  );
}
```

#### 网格布局

```jsx
function GridLayout({ children, cols = { default: 1, md: 2, lg: 3 } }) {
  return (
    <div className={`
      grid
      grid-cols-${cols.default}
      md:grid-cols-${cols.md}
      lg:grid-cols-${cols.lg}
      gap-6
    `}>
      {children}
    </div>
  );
}
```

#### Stack（垂直间距）

```jsx
function Stack({ children, spacing = 4 }) {
  return (
    <div className={`flex flex-col gap-${spacing}`}>
      {children}
    </div>
  );
}
```

### UI 组件

#### Card

```jsx
function Card({ title, description, image, footer }) {
  return (
    <div className="
      bg-white dark:bg-gray-800
      rounded-lg shadow-lg
      overflow-hidden
      transition-transform hover:scale-105
    ">
      {image && (
        <img
          src={image}
          alt={title}
          className="w-full h-48 object-cover"
        />
      )}
      <div className="p-6">
        <h3 className="text-xl font-bold mb-2 text-gray-900 dark:text-white">
          {title}
        </h3>
        <p className="text-gray-600 dark:text-gray-400">
          {description}
        </p>
      </div>
      {footer && (
        <div className="px-6 py-4 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600">
          {footer}
        </div>
      )}
    </div>
  );
}
```

#### Modal

```jsx
function Modal({ isOpen, onClose, title, children }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* 背景遮罩 */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="
        relative bg-white dark:bg-gray-800
        rounded-lg shadow-xl
        max-w-md w-full
        p-6
        animate-fade-in
      ">
        <h2 className="text-2xl font-bold mb-4">
          {title}
        </h2>
        <button
            onClick={onClose}
            className="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
            ✕
          </button>
          {children}
        </div>
      </div>
    </div>
  );
}
```

#### Form Input

```jsx
function Input({ label, error, ...props }) {
  return (
    <div className="mb-4">
      {label && (
        <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
          {label}
        </label>
      )}
      <input
        className={`
          w-full px-4 py-2 rounded-lg
          border ${error ? 'border-red-500' : 'border-gray-300'}
          focus:outline-none focus:ring-2
          ${error ? 'focus:ring-red-500' : 'focus:ring-blue-500'}
          bg-white dark:bg-gray-700
          text-gray-900 dark:text-white
          placeholder-gray-400
        `}
        {...props}
      />
      {error && (
        <p className="mt-1 text-sm text-red-500">{error}</p>
      )}
    </div>
  );
}
```

#### Badge

```jsx
function Badge({ children, variant = 'default', size = 'md' }) {
  const variants = {
    default: 'bg-gray-100 text-gray-800',
    primary: 'bg-blue-100 text-blue-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    danger: 'bg-red-100 text-red-800',
  };

  const sizes = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-2.5 py-1',
    lg: 'text-base px-3 py-1.5'
  };

  return (
    <span className={`
      inline-flex items-center
      rounded-full font-medium
      ${variants[variant]}
      ${sizes[size]}
    `}>
      {children}
    </span>
  );
}
```

---

## 参考

- **官方文档:** https://tailwindcss.com/docs
- **Playground:** https://play.tailwindcss.com
- **Tailwind UI:** https://tailwindui.com (付费组件)
- **Headless UI:** https://headlessui.com (无样式可访问组件)
- **Tailwind CLI:** https://tailwindcss.com/docs/installation
- **Class Variance Authority:** https://cva.style (类型安全的变体)
- **Prettier 插件:** https://github.com/tailwindlabs/prettier-plugin-tailwindcss
