# Tailwind 设计系统（v4）

使用 Tailwind CSS v4 构建生产就绪的设计系统，包括 CSS 优先配置、设计令牌、组件变体、响应式模式和无障碍访问。

> **注意**：该技能面向 Tailwind CSS v4（2024 年及以后版本）。对于 v3 项目，请参考 [升级指南](https://tailwindcss.com/docs/upgrade-guide)。

## 本技能的使用场景

- 使用 Tailwind v4 创建组件库
- 通过 CSS 优先配置实现设计令牌与主题设置
- 构建响应式和无障碍组件
- 统一代码库中的 UI 模式
- 从 Tailwind v3 迁移至 v4
- 使用原生 CSS 特性配置深色模式

## v4 主要变更

| v3 模式 | v4 模式 |
| ------- | -------- |
| `tailwind.config.ts` | `@theme` in CSS |
| `@tailwind base/components/utilities` | `@import "tailwindcss"` |
| `darkMode: "class"` | `@custom-variant dark (&:where(.dark, .dark *))` |
| `theme.extend.colors` | `@theme { --color-*: value }` |
| `require("tailwindcss-animate")` | CSS `@keyframes` in `@theme` + `@starting-style` 用于进入动画 |

## 快速开始

```css
/* app.css - Tailwind v4 CSS 优先配置 */
@import "tailwindcss";

/* 使用 @theme 定义主题 */
@theme {
  /* 使用 OKLCH 定义语义化颜色令牌，以获得更良好的色彩感知效果 */
  --color-background: oklch(100% 0 0);
  --color-foreground: oklch(14.5% 0.025 264);

  --color-primary: oklch(14.5% 0.025 264);
  --color-primary-foreground: oklch(98% 0.01 264);

  --color-secondary: oklch(96% 0.01 264);
  --color-secondary-foreground: oklch(14.5% 0.025 264);

  --color-muted: oklch(96% 0.01 264);
  --color-muted-foreground: oklch(46% 0.02 264);

  --color-accent: oklch(96% 0.01 264);
  --color-accent-foreground: oklch(14.5% 0.025 264);

  --color-destructive: oklch(53% 0.22 27);
  --color-destructive-foreground: oklch(98% 0.01 264);

  --color-border: oklch(91% 0.01 264);
  --color-ring: oklch(14.5% 0.025 264);

  --color-card: oklch(100% 0 0);
  --color-card-foreground: oklch(14.5% 0.025 264);

  /* 焦点状态下的环偏移 */
  --color-ring-offset: oklch(100% 0 0);

  /* 圆角令牌 */
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;

  /* 动画令牌 - 在 @theme 内部的 keyframes 会在通过 --animate-* 变量引用时输出 */
  --animate-fade-in: fade-in 0.2s ease-out;
  --animate-fade-out: fade-out 0.2s ease-in;
  --animate-slide-in: slide-in 0.3s ease-out;
  --animate-slide-out: slide-out 0.3s ease-in;

  @keyframes fade-in {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  @keyframes fade-out {
    from {
      opacity: 1;
    }
    to {
      opacity: 0;
    }
  }

  @keyframes slide-in {
    from {
      transform: translateY(-0.5rem);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }

  @keyframes slide-out {
    from {
      transform: translateY(0);
      opacity: 1;
    }
    to {
      transform: translateY(-0.5rem);
      opacity: 0;
    }
  }
}

/* 深色模式变体 - 使用 @custom-variant 实现基于类的深色模式 */
@custom-variant dark (&:where(.dark, .dark *));

/* 深色模式主题覆盖 */
.dark {
  --color-background: oklch(14.5% 0.025 264);
  --color-foreground: oklch(98% 0.01 264);

  --color-primary: oklch(98% 0.01 264);
  --color-primary-foreground: oklch(14.5% 0.025 264);

  --color-secondary: oklch(22% 0.02 264);
  --color-secondary-foreground: oklch(98% 0.01 264);

  --color-muted: oklch(22% 0.02 264);
  --color-muted-foreground: oklch(65% 0.02 264);

  --color-accent: oklch(22% 0.02 264);
  --color-accent-foreground: oklch(98% 0.01 264);

  --color-destructive: oklch(42% 0.15 27);
  --color-destructive-foreground: oklch(98% 0.01 264);

  --color-border: oklch(22% 0.02 264);
  --color-ring: oklch(83% 0.02 264);

  --color-card: oklch(14.5% 0.025 264);
  --color-card-foreground: oklch(98% 0.01 264);

  --color-ring-offset: oklch(14.5% 0.025 264);
}

/* 基础样式 */
@layer base {
  * {
    @apply border-border;
  }

  body {
    @apply bg-background text-foreground antialiased;
  }
}
```

## 核心概念

### 1. 设计令牌层级

```
品牌令牌（抽象）
    └── 语义令牌（用途）
        └── 组件令牌（具体）

示例：
    oklch(45% 0.2 260) → --color-primary → bg-primary
```

### 2. 组件架构

```
基础样式 → 变体 → 尺寸 → 状态 → 覆盖
```

## 详细模式与示例

详细的模式文档位于 `references/details.md`。当上述导航层级不足以解决问题时，请阅读该文件。
