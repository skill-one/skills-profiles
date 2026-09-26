# 品牌设计师技能

我帮助您创建协调一致的品牌标识、标志和视觉品牌系统。

## 我能做什么

**品牌标识：**

- 标志设计和变体
- 色彩搭配板
- 字体系统
- 品牌规范

**视觉资产：**

- 名片、信头纸
- 社交媒体模板
- 营销材料
- 品牌演示文稿

**品牌策略：**

- 品牌定位
- 目标受众定义
- 竞争对手分析
- 品牌声音和语气

## 标志设计流程

### 第一步：品牌探索

**需要回答的问题：**

- 公司做什么业务？
- 目标受众是谁？
- 品牌价值观是什么？
- 标志应该唤起什么样的感觉？
- 有任何需要避免的颜色/符号吗？

**示例简报：**

```markdown
## 品牌简报：TechStart

**行业：** SaaS、开发者工具
**目标受众：** 软件开发者，25-40岁
**品牌价值观：** 创新、简洁、可靠性
**个性：** 现代、技术性、平易近人
**竞争对手：** GitHub、GitLab、Vercel

**标志要求：**

- 可单色使用
- 从16px（网站图标）到广告牌大小
- 现代，不过时（应经得起时间考验）
- 独特、易记
```

---

### 第二步：标志概念

**概念1：文字标志**

```
简洁、现代的字体设计
专注于公司名称
例如：Google、Facebook、Netflix
```

**概念2：字母标志**

```
以独特方式呈现的缩写
适用于长公司名称
例如：IBM、HBO、CNN
```

**概念3：图标+文字标志**

```
符号+公司名称
最通用的选项
例如：Nike、Apple、Twitter
```

**示例SVG标志（React组件）：**

```typescript
// components/brand/Logo.tsx

interface LogoProps {
  variant?: 'full' | 'icon' | 'wordmark'
  color?: 'primary' | 'white' | 'black'
  size?: number
}

export function Logo({ variant = 'full', color = 'primary', size = 40 }: LogoProps) {
  const colors = {
    primary: '#0066CC',
    white: '#FFFFFF',
    black: '#000000'
  }

  const fillColor = colors[color]

  if (variant === 'icon') {
    return (
      <svg width={size} height={size} viewBox="0 0 40 40" fill="none">
        <circle cx="20" cy="20" r="18" fill={fillColor} />
        <path
          d="M15 20 L25 15 L25 25 Z"
          fill="white"
        />
      </svg>
    )
  }

  if (variant === 'wordmark') {
    return (
      <svg width={size * 4} height={size} viewBox="0 0 160 40" fill="none">
        <text
          x="0"
          y="30"
          fontFamily="Inter, sans-serif"
          fontSize="24"
          fontWeight="700"
          fill={fillColor}
        >
          TechStart
        </text>
      </svg>
    )
  }

  // 完整标志（图标+文字）
  return (
    <svg width={size * 5} height={size} viewBox="0 0 200 40" fill="none">
      <circle cx="20" cy="20" r="18" fill={fillColor} />
      <path d="M15 20 L25 15 L25 25 Z" fill="white" />
      <text
        x="50"
        y="30"
        fontFamily="Inter, sans-serif"
        fontSize="24"
        fontWeight="700"
        fill={fillColor}
      >
        TechStart
      </text>
    </svg>
  )
}
```

**使用方式：**

```typescript
// 不同的标志变体
<Logo variant="full" />
<Logo variant="icon" size={32} />
<Logo variant="wordmark" color="white" />
```

---

## 色彩搭配板

### 主要品牌色彩

```typescript
// config/brand-colors.ts

export const brandColors = {
  // 主要（品牌主色调）
  primary: {
    50: '#E6F0FF',
    100: '#CCE0FF',
    200: '#99C2FF',
    300: '#66A3FF',
    400: '#3385FF',
    500: '#0066CC', // 品牌主色调
    600: '#0052A3',
    700: '#003D7A',
    800: '#002952',
    900: '#001429'
  },

  // 次要（强调色）
  secondary: {
    50: '#FFF4E6',
    100: '#FFE9CC',
    200: '#FFD399',
    300: '#FFBD66',
    400: '#FFA733',
    500: '#FF9100', // 主要强调色
    600: '#CC7400',
    700: '#995700',
    800: '#663A00',
    900: '#331D00'
  },

  // 中性（灰色）
  neutral: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827'
  },

  // 语义色彩
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6'
}
```

### 色彩使用规范

```typescript
// Tailwind配置
module.exports = {
  theme: {
    colors: {
      primary: brandColors.primary,
      secondary: brandColors.secondary,
      gray: brandColors.neutral,
      green: brandColors.success
      // ...
    }
  }
}
```

**色彩搭配文档：**

```markdown
## 品牌色彩

### 主要蓝色 (#0066CC)

- **使用场景：** 主要按钮、链接、活动状态、品牌元素
- **避免使用：** 背景、大面积
- **可访问性：** 通过WCAG AA级文本在白色背景上的测试

### 次要橙色 (#FF9100)

- **使用场景：** 行动号召、高亮、重要操作
- **避免使用：** 正文文本
- **搭配：** 与主要蓝色搭配效果最佳

### 中性灰色

- **使用场景：** 文本、边框、背景、UI元素
- **层级：**
  - 900：标题
  - 700：正文
  - 500：次要文本
  - 300：边框
  - 100：背景
```

---

## 字体系统

### 字体选择

```css
/* Google Fonts导入 */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
  /* 字体家族 */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'Courier New', monospace;

  /* 字体大小 */
  --text-xs: 0.75rem; /* 12px */
  --text-sm: 0.875rem; /* 14px */
  --text-base: 1rem; /* 16px */
  --text-lg: 1.125rem; /* 18px */
  --text-xl: 1.25rem; /* 20px */
  --text-2xl: 1.5rem; /* 24px */
  --text-3xl: 1.875rem; /* 30px */
  --text-4xl: 2.25rem; /* 36px */
  --text-5xl: 3rem; /* 48px */

  /* 字体粗细 */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  /* 行高 */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
}
```

**字体层级：**

```typescript
// components/Typography.tsx

export function Heading1({ children }: { children: React.ReactNode }) {
  return (
    <h1 className="text-4xl font-bold leading-tight text-gray-900">
      {children}
    </h1>
  )
}

export function Heading2({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="text-3xl font-semibold leading-tight text-gray-900">
      {children}
    </h2>
  )
}

export function BodyText({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-base font-normal leading-normal text-gray-700">
      {children}
    </p>
  )
}

export function Caption({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-sm font-normal leading-normal text-gray-500">
      {children}
    </p>
  )
}
```

---

## 品牌规范文档

### 创建brand-guidelines.md

```markdown
# TechStart品牌规范

## 标志使用规范

### 标志变体

- **完整标志：** 用于营销材料、网站页眉
- **仅图标：** 用于应用图标、网站图标、社交媒体头像
- **文字标志：** 当图标不适合上下文时使用

### 间距要求

保持标志周围的清晰间距等于TechStart中"T"的高度

### 最小尺寸

- **数字：** 120px宽度（完整标志），40px（图标）
- **印刷：** 1英寸宽度（完整标志），0.25英寸（图标）

### 禁止事项

❌ 不要旋转标志
❌ 不要更改颜色（除经批准的变体外）
❌ 不要添加效果（阴影、渐变等）
❌ 不要扭曲或拉伸

---

## 色彩搭配板

### 主要色彩

- **品牌蓝色：** #0066CC
  - RGB：0, 102, 204
  - CMYK：100, 50, 0, 20
- **强调橙色：** #FF9100
  - RGB：255, 145, 0
  - CMYK：0, 43, 100, 0

### 使用规范

- 主要按钮、链接：品牌蓝色
- 行动号召、高亮：强调橙色
- 背景：中性灰色

---

## 字体规范

### 字体

- **标题：** Inter Bold (700)
- **正文：** Inter Regular (400)
- **代码：** JetBrains Mono Regular (400)

### 层级

- H1：48px / 粗体 / 紧凑行高
- H2：36px / 半粗体 / 紧凑行高
- 正文：16px / 常规 / 常规行高
- 款注：14px / 常规 / 常规行高

---

## 品牌声音与语气

### 品牌个性

- **专业**但不正式
- **技术性**但平易近人
- **创新**但可靠

### 写作风格

- 使用主动语态
- 简洁清晰
- 避免行话（除非是技术文档）
- 使用"我们"和"你"（不要使用"我"或"一个"）

### 示例

✅ "在几秒钟内部署您的应用"
❌ "应用程序可以快速部署"

✅ "我们为像您这样的开发者而建"
❌ "该产品是为开发者用户设计的"
```

---

## 社交媒体模板

### 头像图片（SVG模板）

```typescript
// templates/SocialProfileImage.tsx

export function SocialProfileImage() {
  return (
    <svg width="400" height="400" viewBox="0 0 400 400">
      {/* 背景 */}
      <rect width="400" height="400" fill="#0066CC" />

      {/* 标志（居中） */}
      <circle cx="200" cy="200" r="120" fill="white" />
      <path
        d="M160 200 L240 160 L240 240 Z"
        fill="#0066CC"
      />
    </svg>
  )
}
```

### 社交媒体帖子模板

```typescript
// templates/SocialPost.tsx

interface SocialPostProps {
  title: string
  description: string
  imageUrl?: string
}

export function SocialPost({ title, description, imageUrl }: SocialPostProps) {
  return (
    <svg width="1200" height="630" viewBox="0 0 1200 630">
      {/* 背景渐变 */}
      <defs>
        <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#0066CC" />
          <stop offset="100%" stopColor="#003D7A" />
        </linearGradient>
      </defs>
      <rect width="1200" height="630" fill="url(#bg)" />

      {/* 内容 */}
      <text
        x="60"
        y="200"
        fontSize="60"
        fontWeight="700"
        fill="white"
        fontFamily="Inter"
      >
        {title}
      </text>
      <text
        x="60"
        y="270"
        fontSize="32"
        fill="#CCE0FF"
        fontFamily="Inter"
      >
        {description}
      </text>

      {/* 标志 */}
      <Logo variant="icon" size={60} color="white" />
    </svg>
  )
}
```

---

## 名片设计

```typescript
// templates/BusinessCard.tsx

interface BusinessCardProps {
  name: string
  title: string
  email: string
  phone: string
}

export function BusinessCard({ name, title, email, phone }: BusinessCardProps) {
  return (
    <svg width="350" height="200" viewBox="0 0 350 200">
      {/* 正面 */}
      <rect width="350" height="200" fill="white" />

      {/* 标志 */}
      <Logo variant="full" size={30} />

      {/* 联系信息 */}
      <text x="20" y="120" fontSize="20" fontWeight="700" fill="#111827">
        {name}
      </text>
      <text x="20" y="145" fontSize="14" fill="#6B7280">
        {title}
      </text>
      <text x="20" y="170" fontSize="12" fill="#6B7280">
        {email}
      </text>
      <text x="20" y="185" fontSize="12" fill="#6B7280">
        {phone}
      </text>
    </svg>
  )
}
```

---

## 品牌资产管理

### 文件组织

```
brand-assets/
├── logo/
│   ├── svg/
│   │   ├── logo-full.svg
│   │   ├── logo-icon.svg
│   │   └── logo-wordmark.svg
│   ├── png/
│   │   ├── logo-full@1x.png
│   │   ├── logo-full@2x.png
│   │   └── logo-full@3x.png
│   └── favicon/
│       ├── favicon-16x16.png
│       ├── favicon-32x32.png
│       └── favicon.ico
├── colors/
│   └── palette.json
├── fonts/
│   ├── Inter-Regular.woff2
│   ├── Inter-Bold.woff2
│   └── JetBrainsMono-Regular.woff2
├── templates/
│   ├── social-profile.svg
│   ├── social-post.svg
│   └── business-card.svg
└── guidelines/
    └── brand-guidelines.pdf
```

---

## 网站图标生成

```typescript
// scripts/generate-favicons.ts

import sharp from 'sharp'
import fs from 'fs'

async function generateFavicons() {
  const sizes = [16, 32, 48, 64, 128, 256]

  for (const size of sizes) {
    await sharp('logo-icon.svg')
      .resize(size, size)
      .png()
      .toFile(`public/favicon-${size}x${size}.png`)

    console.log(`Generated ${size}x${size} favicon`)
  }

  console.log('Favicons generated!')
}

generateFavicons()
```

**网站图标HTML：**

```html
<!-- 在layout/head中 -->
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
<link rel="manifest" href="/site.webmanifest" />
```

---

## 何时使用我

**非常适合：**

- 创建新的品牌标识
- 设计标志和视觉系统
- 构建品牌规范
- 创建营销模板
- 确保品牌一致性

**我能帮助您：**

- 设计易记的标志
- 创建协调的色彩搭配板
- 构建字体系统
- 生成品牌资产
- 记录品牌规范

## 我将创建的内容

```
🎨 标志设计 (SVG)
🌈 色彩搭配板
📝 字体系统
📄 品牌规范
🖼️ 社交媒体模板
💼 名片
```

让我们共同打造一个强大、协调的品牌标识！
