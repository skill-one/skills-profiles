# Aceternity UI 技能

## 概述

Aceternity UI 是一个面向 Next.js 应用的、高级的、可用于生产的 React 组件库。它提供了 100 多个精美动画和交互式组件，这些组件使用 Tailwind CSS 和 Framer Motion 构建。组件通过 shadcn CLI 安装，并且可以直接在您的代码库中进行自定义。

**主要特性：**
- 100 多个动画化的、可用于生产的组件
- 支持 Next.js 13+ 和 App Router
- 完整的 TypeScript 支持
- Tailwind CSS v4+ 样式（CSS 优先配置；v3 也支持 JS 配置）
- Framer Motion 动画
- 暗黑模式支持
- 复制粘贴友好（不是 npm 包）
- 可访问完整源代码进行自定义

**先决条件：**
- Next.js 13+（推荐使用 App Router）
- React 16.8+
- Tailwind CSS v4+（CSS 优先 `@import "tailwindcss"` 和 `@theme`；v3 也受支持）
- TypeScript（推荐）
- Node.js 20+ 以及 bun、npm 或 pnpm

## 安装

### 初始设置

**对于新项目：**

```bash
# 创建 Next.js 项目（推荐使用 bun）
bunx create-next-app@latest my-app
# 或：npx create-next-app@latest my-app
# 或：pnpm create next-app@latest my-app

cd my-app

# 选择以下选项：
# - TypeScript：是
# - ESLint：是
# - Tailwind CSS：是
# - src/ 目录：可选
# - App Router：是（推荐）
# - Import alias：@/*（默认）
```

**通过 shadcn CLI 初始化 Aceternity UI：**

```bash
# 使用 bun（推荐）
bunx --bun shadcn@latest init

# 使用 npm
npx shadcn@latest init

# 使用 pnpm
pnpm dlx shadcn@latest init

# 在设置过程中：
# - Style：New York（推荐）
# - Color：Zinc（或您的偏好）
# - CSS variables：是（推荐）
```

**配置 Registry：**

初始化后，更新 `components.json` 以添加 Aceternity 注册中心：

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "app/globals.css",
    "baseColor": "zinc",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  },
  "registries": {
    "@aceternity": "https://ui.aceternity.com/registry/{name}.json"
  }
}
```

### 安装组件

**使用 shadcn CLI 3.0+（命名空间注册中心）：**

```bash
# 安装特定组件
bunx shadcn@latest add @aceternity/background-beams
# 或：npx shadcn@latest add @aceternity/background-beams
# 或：pnpm dlx shadcn@latest add @aceternity/background-beams

# 组件将被添加到：components/ui/background-beams.tsx
```

**手动安装：**

如果注册中心方法不起作用，请手动安装：

1. 安装必要的依赖项：
```bash
bun add motion clsx tailwind-merge
# 或：npm install motion clsx tailwind-merge
```

2. 在 `lib/utils.ts` 中添加实用函数：
```typescript
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

3. 从 [ui.aceternity.com](https://ui.aceternity.com) 复制组件代码到您的项目

## 安全安装

此设置运行多个远程代码执行（`create-next-app`、`shadcn init`、`shadcn add`）。在安装之前，请遵循供应链安全最佳实践：

- **阻止安装后脚本** — `npm config set ignore-scripts true`（或 Bun：默认禁用）
- **冷却期** — 等待 7 天，让新包版本经过社区审核
- **安装前审计** — 运行 `socket package score npm <pkg>` 或使用 `socket npm install <pkg>` 检查包

加载 `dependency-upgrade` 技能以进行完整的安全配置，包括 Socket CLI 集成、冷却设置、锁文件验证和 CI 强制执行。

## 组件类别

### 1. 背景 & 特效（28 个组件）

创建引人注目的动画背景和视觉效果，用于英雄区域和全页布局。

**主要组件：**

- **Background Beams** - 沿着 SVG 路径移动的动画光束
- **Background Gradient** - 带有过渡的平滑渐变背景
- **Wavy Background** - 动画波浪图案
- **Aurora Background** - 受北极光启发的动画渐变
- **Sparkles** - 粒子闪烁效果
- **Meteors** - 陨石下落动画
- **Spotlight** - 动态聚光灯效果
- **Grid and Dot Backgrounds** - 微妙的网格/点图案
- **Vortex** - 旋转的漩涡动画
- **Canvas Reveal Effect** - 使用 canvas 动画揭示内容

**使用示例：**

```tsx
"use client";
import { BackgroundBeams } from "@/components/ui/background-beams";

export default function HeroSection() {
  return (
    <div className="h-screen w-full relative">
      <div className="max-w-4xl mx-auto z-10 relative p-8">
        <h1 className="text-5xl font-bold">欢迎</h1>
        <p className="text-xl mt-4">精美的动画背景</p>
      </div>
      <BackgroundBeams />
    </div>
  );
}
```

**何时使用：**
- 需要视觉冲击力的英雄区域
- 带有动画背景的着陆页
- 需要深度的全屏区域
- 作品集或代理网站
- 带有行动号召的市场营销页面

### 2. 卡片组件（15 个组件）

带有悬停效果、动画和 3D 变换的交互式卡片。

**主要组件：**

- **3D Card Effect** - 带有 CSS 透视和 3D 变换的卡片
- **Card Hover Effect** - 平滑的悬停动画和过渡
- **Expandable Card** - 扩展以显示更多内容的卡片
- **Focus Cards** - 悬停时聚焦/突出显示的卡片
- **Card Spotlight** - 跟随鼠标的聚光灯效果
- **Glare Card** - 全息光晕效果
- **Wobble Card** - 欢乐的摇摆动画
- **Infinite Moving Cards** - 自动滚动的卡片轮播
- **Direction Aware Hover** - 基于鼠标方向悬停效果

**使用示例：**

```tsx
"use client";
import { CardBody, CardContainer, CardItem } from "@/components/ui/3d-card";

export function ProductCard() {
  return (
    <CardContainer>
      <CardBody className="bg-gray-50 rounded-xl p-6">
        <CardItem translateZ="50" className="text-2xl font-bold">
          产品标题
        </CardItem>
        <CardItem translateZ="60" as="p" className="text-sm mt-2">
          产品描述在这里
        </CardItem>
        <CardItem translateZ="100" className="w-full mt-4">
          <img src="/product.jpg" className="rounded-xl" alt="产品" />
        </CardItem>
      </CardBody>
    </CardContainer>
  );
}
```

**何时使用：**
- 产品展示
- 功能亮点
- 作品集项目
- 团队成员简介
- 定价层级
- 博客文章预览

### 3. 滚动 & 视差（5 个组件）

创建基于滚动的动画和视差效果。

**主要组件：**

- **Parallax Scroll** - 带有视差滚动的图像
- **Sticky Scroll Reveal** - 滚动时揭示内容
- **Container Scroll Animation** - 动画的滚动容器
- **Hero Parallax** - 视差英雄区域
- **MacBook Scroll** - MacBook 风格的滚动交互

**使用示例：**

```tsx
import { StickyScroll } from "@/components/ui/sticky-scroll-reveal";

const content = [
  {
    title: "功能一",
    description: "功能一的描述...",
    content: <div>视觉内容在这里</div>
  },
  // 更多项目...
];

export function Features() {
  return <StickyScroll content={content} />;
}
```

**何时使用：**
- 带有滚动交互的功能展示
- 故事叙述布局
- 产品导览
- 长格式内容中的视觉分隔
- 交互式时间线

### 4. 文本组件（10 个组件）

用于标题、标题和交互式排版动画文本效果。

**主要组件：**

- **Text Generate Effect** - 文字逐个字符出现
- **Typewriter Effect** - 打字动画
- **Flip Words** - 旋转单词动画
- **Text Hover Effect** - 悬停时的交互式文本
- **Hero Highlight** - 渐变文本高亮
- **Encrypted Text** - 矩阵风格的加密文本效果
- **Colourful Text** - 渐变动画文本

**使用示例：**

```tsx
import { TypewriterEffect } from "@/components/ui/typewriter-effect";

const words = [
  { text: "构建" },
  { text: "令人惊叹" },
  { text: "网站", className: "text-blue-500" }
];

export function Hero() {
  return <TypewriterEffect words={words} />;
}
```

**何时使用：**
- 英雄标题
- 吸引注意力的标题
- 动态内容显示
- 交互式着陆页
- 动画行动号召

### 5. 按钮（4 个组件）

带有动画和效果的增强按钮组件。

**主要组件：**

- **Tailwind CSS Buttons** - 风格化的按钮集合
- **Hover Border Gradient** - 动画渐变边框
- **Moving Border** - 动画边框移动
- **Stateful Button** - 带有过渡的多状态按钮

**使用示例：**

```tsx
import { MovingBorder } from "@/components/ui/moving-border";

export function CTAButton() {
  return (
    <MovingBorder duration={2000} className="p-4">
      <span>开始使用</span>
    </MovingBorder>
  );
}
```

### 6. 导航（5 个组件）

现代导航菜单和标签系统。

**主要组件：**

- **Floating Navbar** - 浮动导航栏
- **Navbar Menu** - 全功能导航菜单
- **Tabs** - 动画标签组件
- **Resizable Navbar** - 响应式导航
- **Sticky Banner** - 粘性公告横幅

### 7. 输入 & 表单（3 个组件）

增强的表单输入和文件上传组件。

**主要组件：**

- **Signup Form** - 动画注册表单
- **Placeholders and Vanish Input** - 带有动画占位符的输入
- **File Upload** - 拖放文件上传

**使用示例：**

```tsx
import { PlaceholdersAndVanishInput } from "@/components/ui/placeholders-and-vanish-input";

export function SearchBar() {
  const placeholders = [
    "搜索任何内容...",
    "你在寻找什么？",
    "输入以搜索..."
  ];

  return (
    <PlaceholdersAndVanishInput
      placeholders={placeholders}
      onChange={(e) => console.log(e.target.value)}
      onSubmit={(e) => {
        e.preventDefault();
        console.log("提交");
      }}
    />
  );
}
```

### 8. 覆盖 & 弹出（3 个组件）

带动画的模态对话框和工具提示。

**主要组件：**

- **Animated Modal** - 带有平滑动画的模态框
- **Animated Tooltip** - 带有进入/退出动画的工具提示
- **Link Preview** - 悬停时显示链接预览的弹出框

**使用示例：**

```tsx
import { Modal, ModalBody, ModalContent, ModalTrigger } from "@/components/ui/animated-modal";

export function BookingModal() {
  return (
    <Modal>
      <ModalTrigger className="bg-black text-white px-4 py-2 rounded-md">
        立即预订
      </ModalTrigger>
      <ModalBody>
        <ModalContent>
          <h2>预订详情</h2>
          {/* 模态框内容 */}
        </ModalContent>
      </ModalBody>
    </Modal>
  );
}
```

### 9. 轮播 & 滑块（4 个组件）

图像滑块和轮播组件。

**主要组件：**

- **Images Slider** - 全屏图像滑块
- **Carousel** - 标准轮播组件
- **Apple Cards Carousel** - 苹果风格的卡片轮播
- **Animated Testimonials** - 评价轮播

### 10. 布局 & 网格（3 个组件）

网格布局和容器组件。

**主要组件：**

- **Layout Grid** - 动画网格布局
- **Bento Grid** - Bento 盒式网格
- **Container Cover** - 全屏容器

### 11. 数据 & 可视化（2 个组件）

用于显示数据和比较的组件。

**主要组件：**

- **Timeline** - 动画时间线组件
- **Compare** - 前/后比较滑块

### 12. 光标 & 指针（3 个组件）

跟随光标的特效和交互。

**主要组件：**

- **Following Pointer** - 跟随光标的元素
- **Pointer Highlight** - 光标高亮效果
- **Lens** - 放大镜效果

### 13. 3D 组件（2 个组件）

使用 CSS 变换的 3D 视觉效果。

**主要组件：**

- **3D Pin** - Pinterest 风格的 3D 卡片
- **3D Marquee** - 3D 旋转横幅

### 14. 加载器（2 个组件）

加载动画和进度指示器。

**主要组件：**

- **Multi-step Loader** - 多步骤加载动画
- **Loader** - 各种加载旋转器

### 15. 区域 & 块（3 个组件）

预构建的区域模板。

**主要组件：**

- **Feature Sections** - 功能展示模板
- **Cards** - 预设的卡片布局
- **Hero Sections** - 英雄区域模板

## 常见模式

### 暗黑模式支持

所有 Aceternity 组件都通过 Tailwind 的暗黑模式类支持暗黑模式：

```tsx
<div className="bg-white dark:bg-black text-black dark:text-white">
  {/* 内容 */}
</div>
```

### 响应式设计

组件默认是响应式的。使用 Tailwind 的响应式前缀：

```tsx
<h1 className="text-2xl md:text-4xl lg:text-6xl">
  响应式标题
</h1>
```

### 组合组件

组件可以组合以创建复杂的布局：

```tsx
import { BackgroundBeams } from "@/components/ui/background-beams";
import { TypewriterEffect } from "@/components/ui/typewriter-effect";
import { MovingBorder } from "@/components/ui/moving-border";

export default function Hero() {
  return (
    <div className="h-screen relative">
      <div className="z-10 relative flex flex-col items-center justify-center h-full">
        <TypewriterEffect words={words} />
        <MovingBorder>
          <button>开始使用</button>
        </MovingBorder>
      </div>
      <BackgroundBeams />
    </div>
  );
}
```

## 最佳实践

### 1. 性能优化

**使用 "use client" 指令** - Aceternity 组件使用 Framer Motion，需要客户端渲染：

```tsx
"use client";
import { Component } from "@/components/ui/component";
```

**延迟加载重型组件：**

```tsx
import dynamic from 'next/dynamic';

const HeavyBackground = dynamic(
  () => import('@/components/ui/background-beams'),
  { ssr: false }
);
```

### 2. 可访问性

**添加 ARIA 标签：**

```tsx
<button aria-label="打开菜单">
  <MenuIcon />
</button>
```

**确保键盘导航：**

```tsx
<div role="button" tabIndex={0} onKeyDown={handleKeyDown}>
  交互式元素
</div>
```

### 3. 自定义

**使用 className 覆盖样式：**

```tsx
<BackgroundBeams className="opacity-50" />
```

**直接修改组件源代码** - 由于组件被复制到您的项目，您可以编辑它们：

```tsx
// components/ui/background-beams.tsx
export function BackgroundBeams({ className, myCustomProp }: Props) {
  // 根据需要自定义
}
```

### 4. 类型安全

**使用 TypeScript for prop types：**

```tsx
interface CardProps {
  title: string;
  description: string;
  image?: string;
}

export function Card({ title, description, image }: CardProps) {
  // 组件实现
}
```

## 故障排除

### 常见问题

**1. "Module not found: motion"**
```bash
bun add motion
# 或：npm install motion
```

**2. "cn is not defined"**
确保 `lib/utils.ts` 存在并包含 `cn` 辅助函数。

**3. 组件不动画**
验证文件顶部是否有 "use client" 指令。

**4. Tailwind 类不工作**
确保 Tailwind 已设置。在 Tailwind v4（CSS 优先）中，`globals.css` 应该使用单个指令导入 Tailwind：
```css
@import "tailwindcss";
```
（如果您仍然在 Tailwind v3 上，则等效的是三个 `@tailwind base; @tailwind components; @tailwind utilities;` 指令。）

**5. 暗黑模式不工作**
在 Tailwind v4 中，使用自定义变体在 CSS 中配置暗黑模式（例如 `@custom-variant dark (&:where(.dark, .dark *));` 用于基于类的策略）。在 Tailwind v3 中，在 `tailwind.config.ts` 中设置 `darkMode: "class"`。

## 代币效率

此技能通过以下方式提供显著的代币节省：

- **预筛选组件选择** - 节省 ~3k 代币探索组件选项
- **安装说明** - 节省 ~2k 代币调试设置问题
- **组件分类** - 节省 ~2k 代币找到正确的组件
- **使用示例** - 节省 ~2k 代币编写样板代码
- **故障排除指南** - 节省 ~1k 代币调试常见问题

**估计节省：~10k 代币（65-70% 的减少）每个实现**

**防止的错误：**
1. 缺少 motion 依赖
2. 错误的 shadcn CLI 初始化
3. 缺少 cn 实用函数
4. 缺少 "use client" 指令
5. 错误的注册中心配置
6. 错误的 Next.js 配置（Pages Router 与 App Router）

## 何时加载参考

根据任务上下文加载参考文件：

| 如果用户询问关于... | 加载这个参考 |
|-----------------------|---------------------|
| 新项目设置、安装、入门 | `references/quick-start.md`（465 行） |
| 查找特定组件、组件类别、CLI 命令 | `references/component-catalog.md`（635 行） |
| 使用示例、模式、故障排除 | 主 SKILL.md（此文件） |

**参考摘要：**
- `quick-start.md` - 5 分钟设置指南、第一个组件示例、故障排除、项目结构
- `component-catalog.md` - 100 多个组件的完整列表，包括安装命令和使用案例

## 其他资源

- **官方文档**：https://ui.aceternity.com/docs
- **组件库**：https://ui.aceternity.com/components
- **Shadcn UI**：https://ui.shadcn.com
- **Framer Motion**：https://www.framer.com/motion
- **Tailwind CSS**：https://tailwindcss.com

## 相关技能

在使用此技能时，请考虑与以下技能结合使用：

- `nextjs` - Next.js 框架技能
- `tailwind-v4-shadcn` - Tailwind CSS v4 配置
- `react-hook-form-zod` - 表单验证
- `clerk-auth` - 身份验证
- `cloudflare-nextjs` - Cloudflare 部署

## 许可证

此技能文档根据 MIT 许可证提供。Aceternity UI 组件有自己的许可 - 查看https://ui.aceternity.com 获取详细信息。

---

**最后更新**：2025-12-08
**版本**：1.1.0
**维护者**：Claude 技能维护者
