# Tailwind 设计系统 (v4)

使用 Tailwind CSS v4 构建 production-ready 设计系统，包括 CSS-first 配置、设计令牌、组件变体、响应式模式和可访问性。

> **注意**：此技能针对 Tailwind CSS v4 (2024+)。对于 v3 项目，请参考 [升级指南](https://tailwindcss.com/docs/upgrade-guide)。

## 何时使用此技能

- 使用 Tailwind v4 创建组件库
- 使用 CSS-first 配置实现设计令牌和主题
- 构建响应式和可访问的组件
- 在代码库中标准化 UI 模式
- 从 Tailwind v3 迁移到 v4
- 使用原生 CSS 功能设置暗黑模式

## v4 的关键变更

| v3 模式                            | v4 模式                                                            |
| ------------------------------------- | --------------------------------------------------------------------- |
| `tailwind.config.ts`                  | `@theme` 在 CSS 中                                                    |
| `@tailwind base/components/utilities` | `@import "tailwindcss"`                                               |
| `darkMode: "class"`                   | `@custom-variant dark (&:where(.dark, .dark *))`                      |
| `theme.extend.colors`                 | `@theme { --color-*: value }`                                         |
| `require("tailwindcss-animate")`      | CSS `@keyframes` 在 `@theme` + `@starting-style` 用于入口动画          |

## 快速入门

```css
/* app.css - Tailwind v4 CSS-first 配置 */
@import "tailwindcss";

/* 使用 @theme 定义主题 */
@theme {
  /* 使用 OKLCH 定义语义颜色令牌，以获得更好的颜色感知 */
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

  /* 聚焦状态的颜色偏移 */
  --color-ring-offset: oklch(100% 0 0);

  /* 圆角令牌 */
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;

  /* 动画令牌 - 当引用 --animate-* 变量时，@theme 内的 keyframes 会输出 */
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

/* 暗黑模式变体 - 使用 @custom-variant 实现基于类的暗黑模式 */
@custom-variant dark (&:where(.dark, .dark *));

/* 暗黑模式主题覆盖 */
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
品牌令牌 (抽象)
    └── 语义令牌 (目的)
        └── 组件令牌 (具体)

示例：
    oklch(45% 0.2 260) → --color-primary → bg-primary
```

### 2. 组件架构

```
基础样式 → 变体 → 尺寸 → 状态 → 覆盖
```

## 详细模式和示例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。
