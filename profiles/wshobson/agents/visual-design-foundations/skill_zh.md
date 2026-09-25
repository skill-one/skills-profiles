# 视觉设计基础

使用排版、色彩、间距和图标基础构建协调、可访问的视觉系统。

## 何时使用这项技能

- 为新项目建立设计令牌
- 创建或完善间距和尺寸系统
- 选择和搭配字体
- 构建可访问的调色板
- 设计图标系统和视觉资源
- 提高视觉层次和可读性
- 审计设计以实现视觉一致性
- 实现暗黑模式或主题化

## 核心系统

### 1. 排版比例

**模块化比例**（基于比例的尺寸）：

```css
:root {
  --font-size-xs: 0.75rem; /* 12px */
  --font-size-sm: 0.875rem; /* 14px */
  --font-size-base: 1rem; /* 16px */
  --font-size-lg: 1.125rem; /* 18px */
  --font-size-xl: 1.25rem; /* 20px */
  --font-size-2xl: 1.5rem; /* 24px */
  --font-size-3xl: 1.875rem; /* 30px */
  --font-size-4xl: 2.25rem; /* 36px */
  --font-size-5xl: 3rem; /* 48px */
}
```

**行高指南**：
| 文本类型 | 行高 |
|-----------|-------------|
| 标题 | 1.1 - 1.3 |
| 正文 | 1.5 - 1.7 |
| UI标签 | 1.2 - 1.4 |

### 2. 间距系统

**8点网格**（行业标准）：

```css
:root {
  --space-1: 0.25rem; /* 4px */
  --space-2: 0.5rem; /* 8px */
  --space-3: 0.75rem; /* 12px */
  --space-4: 1rem; /* 16px */
  --space-5: 1.25rem; /* 20px */
  --space-6: 1.5rem; /* 24px */
  --space-8: 2rem; /* 32px */
  --space-10: 2.5rem; /* 40px */
  --space-12: 3rem; /* 48px */
  --space-16: 4rem; /* 64px */
}
```

### 3. 色彩系统

**语义色彩令牌**：

```css
:root {
  /* 品牌色 */
  --color-primary: #2563eb;
  --color-primary-hover: #1d4ed8;
  --color-primary-active: #1e40af;

  /* 语义色 */
  --color-success: #16a34a;
  --color-warning: #ca8a04;
  --color-error: #dc2626;
  --color-info: #0891b2;

  /* 中性色 */
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;
  --color-gray-300: #d1d5db;
  --color-gray-400: #9ca3af;
  --color-gray-500: #6b7280;
  --color-gray-600: #4b5563;
  --color-gray-700: #374151;
  --color-gray-800: #1f2937;
  --color-gray-900: #111827;
}
```

## 快速入门：Tailwind中的设计令牌

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      fontSize: {
        xs: ["0.75rem", { lineHeight: "1rem" }],
        sm: ["0.875rem", { lineHeight: "1.25rem" }],
        base: ["1rem", { lineHeight: "1.5rem" }],
        lg: ["1.125rem", { lineHeight: "1.75rem" }],
        xl: ["1.25rem", { lineHeight: "1.75rem" }],
        "2xl": ["1.5rem", { lineHeight: "2rem" }],
      },
      colors: {
        brand: {
          50: "#eff6ff",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
        },
      },
      spacing: {
        // 扩展默认值
        18: "4.5rem",
        88: "22rem",
      },
    },
  },
};
```

## 排版最佳实践

### 字体搭配

**安全组合**：

- 标题：**Inter** / 正文：**Inter**（单字体家族）
- 标题：**Playfair Display** / 正文：**Source Sans Pro**（对比效果）
- 标题：**Space Grotesk** / 正文：**IBM Plex Sans**（几何风格）

### 响应式排版

```css
/* 使用clamp()实现流体排版 */
h1 {
  font-size: clamp(2rem, 5vw + 1rem, 3.5rem);
  line-height: 1.1;
}

p {
  font-size: clamp(1rem, 2vw + 0.5rem, 1.125rem);
  line-height: 1.6;
  max-width: 65ch; /* 最佳阅读宽度 */
}
```

### 字体加载

```css
/* 防止布局偏移 */
@font-face {
  font-family: "Inter";
  src: url("/fonts/Inter.woff2") format("woff2");
  font-display: swap;
  font-weight: 400 700;
}
```

## 色彩理论

### 对比度要求（WCAG）

| 元素            | 最小比例 |
| ------------------ | ------------- |
| 正文文本          | 4.5:1 (AA)    |
| 大号文本 (18px+) | 3:1 (AA)      |
| UI组件      | 3:1 (AA)      |
| 增强效果           | 7:1 (AAA)     |

### 暗黑模式策略

```css
:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f9fafb;
  --text-primary: #111827;
  --text-secondary: #6b7280;
  --border: #e5e7eb;
}

[data-theme="dark"] {
  --bg-primary: #111827;
  --bg-secondary: #1f2937;
  --text-primary: #f9fafb;
  --text-secondary: #9ca3af;
  --border: #374151;
}
```

### 色彩可访问性

```tsx
// 程序化检查对比度
function getContrastRatio(foreground: string, background: string): number {
  const getLuminance = (hex: string) => {
    const rgb = hexToRgb(hex);
    const [r, g, b] = rgb.map((c) => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };

  const l1 = getLuminance(foreground);
  const l2 = getLuminance(background);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);

  return (lighter + 0.05) / (darker + 0.05);
}
```

## 间距指南

### 组件间距

```
卡片内边距：      16-24px (--space-4 to --space-6)
区块间距：       32-64px (--space-8 to --space-16)
表单字段间距：    16-24px (--space-4 to --space-6)
按钮内边距：    垂直8-16px，水平16-24px
图标-文本间距：  8px (--space-2)
```

### 视觉韵律

```css
/* 统一垂直韵律 */
.prose > * + * {
  margin-top: var(--space-4);
}

.prose > h2 + * {
  margin-top: var(--space-2);
}

.prose > * + h2 {
  margin-top: var(--space-8);
}
```

## 图标系统

### 图标尺寸系统

```css
:root {
  --icon-xs: 12px;
  --icon-sm: 16px;
  --icon-md: 20px;
  --icon-lg: 24px;
  --icon-xl: 32px;
}
```

### 图标组件

```tsx
interface IconProps {
  name: string;
  size?: "xs" | "sm" | "md" | "lg" | "xl";
  className?: string;
}

const sizeMap = {
  xs: 12,
  sm: 16,
  md: 20,
  lg: 24,
  xl: 32,
};

export function Icon({ name, size = "md", className }: IconProps) {
  return (
    <svg
      width={sizeMap[size]}
      height={sizeMap[size]}
      className={cn("inline-block flex-shrink-0", className)}
      aria-hidden="true"
    >
      <use href={`/icons.svg#${name}`} />
    </svg>
  );
}
```

## 最佳实践

1. **建立约束**：限制选择以保持一致性
2. **记录决策**：创建动态样式指南
3. **测试可访问性**：验证对比度、尺寸、触摸目标
4. **使用语义令牌**：按用途命名，而非外观
5. **移动优先设计**：从约束开始，逐步增加复杂度
6. **保持垂直韵律**：一致间距创造和谐
7. **限制字体粗细**：每个字体家族2-3种粗细即可

## 常见问题

- **间距不一致**：未使用定义好的比例
- **对比度差**：未满足WCAG要求
- **字体过多**：字体家族或粗细过多
- **魔法数字**：使用任意值而非令牌
- **缺少状态**：遗漏悬停、焦点、禁用状态
- **无暗黑模式计划**：后期添加比规划更困难
