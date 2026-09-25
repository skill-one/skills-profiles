# Tailwind CSS 高级布局技巧

## CSS 网格精通

### 复杂网格布局

```html
<!-- 圣杯布局 -->
<div class="grid min-h-screen grid-rows-[auto_1fr_auto]">
  <header class="bg-white shadow">页眉</header>
  <div class="grid grid-cols-[250px_1fr_300px]">
    <aside class="bg-gray-50 p-4">侧边栏</aside>
    <main class="p-6">主要内容</main>
    <aside class="bg-gray-50 p-4">右侧边栏</aside>
  </div>
  <footer class="bg-gray-800 text-white">页脚</footer>
</div>

<!-- 响应式圣杯布局 -->
<div class="grid min-h-screen grid-rows-[auto_1fr_auto]">
  <header>页眉</header>
  <div class="grid grid-cols-1 md:grid-cols-[250px_1fr] lg:grid-cols-[250px_1fr_300px]">
    <aside class="order-2 md:order-1">侧边栏</aside>
    <main class="order-1 md:order-2">主要</main>
    <aside class="order-3 hidden lg:block">右侧</aside>
  </div>
  <footer>页脚</footer>
</div>
```

### 网格模板区域

```css
@utility grid-areas-dashboard {
  grid-template-areas:
    "header header header"
    "nav main aside"
    "nav footer footer";
}

@utility area-header { grid-area: header; }
@utility area-nav { grid-area: nav; }
@utility area-main { grid-area: main; }
@utility area-aside { grid-area: aside; }
@utility area-footer { grid-area: footer; }
```

```html
<div class="grid grid-areas-dashboard grid-cols-[200px_1fr_250px] grid-rows-[60px_1fr_40px] min-h-screen">
  <header class="area-header bg-white shadow">页眉</header>
  <nav class="area-nav bg-gray-100">导航</nav>
  <main class="area-main p-6">主要内容</main>
  <aside class="area-aside bg-gray-50 p-4">侧边栏</aside>
  <footer class="area-footer bg-gray-800 text-white">页脚</footer>
</div>
```

### 自动填充和自动适配网格

```html
<!-- Auto-fill: 创建尽可能多的轨道，即使它们是空的 -->
<div class="grid grid-cols-[repeat(auto-fill,minmax(250px,1fr))] gap-6">
  <div class="bg-white rounded-lg shadow p-4">卡片 1</div>
  <div class="bg-white rounded-lg shadow p-4">卡片 2</div>
  <div class="bg-white rounded-lg shadow p-4">卡片 3</div>
</div>

<!-- Auto-fit: 合并空的轨道 -->
<div class="grid grid-cols-[repeat(auto-fit,minmax(250px,1fr))] gap-6">
  <!-- 卡片会扩展以填充可用空间 -->
</div>

<!-- 使用任意值 -->
<div class="grid grid-cols-[repeat(auto-fill,minmax(min(100%,300px),1fr))] gap-4">
  <!-- 处理容器小于 minmax min 的情况 -->
</div>
```

### 子网格

```css
/* 在 v4 中启用子网格 */
@utility subgrid-cols {
  grid-template-columns: subgrid;
}

@utility subgrid-rows {
  grid-template-rows: subgrid;
}
```

```html
<div class="grid grid-cols-4 gap-4">
  <!-- 跨越 2 列但与父网格对齐的子元素 -->
  <div class="col-span-2 grid subgrid-cols gap-4">
    <div>与父列 1 对齐</div>
    <div>与父列 2 对齐</div>
  </div>
</div>
```

## 高级 Flexbox 模式

### 空间分配

```html
<!-- 边缘处有首尾元素的平均间距 -->
<div class="flex justify-between">
  <div>首元素</div>
  <div>第二元素</div>
  <div>第三元素</div>
</div>

<!-- 包括边缘在内的所有位置的平均间距 -->
<div class="flex justify-around">
  <div>项目</div>
  <div>项目</div>
  <div>项目</div>
</div>

<!-- 项目之间双倍间距，与边缘单倍间距 -->
<div class="flex justify-evenly">
  <div>项目</div>
  <div>项目</div>
  <div>项目</div>
</div>
```

### 弹性项目尺寸

```html
<!-- 项目平均分配空间 -->
<div class="flex">
  <div class="flex-1">1/3</div>
  <div class="flex-1">1/3</div>
  <div class="flex-1">1/3</div>
</div>

<!-- 第一个项目占用 2 倍空间 -->
<div class="flex">
  <div class="flex-[2]">2/4</div>
  <div class="flex-1">1/4</div>
  <div class="flex-1">1/4</div>
</div>

<!-- 固定 + 弹性 -->
<div class="flex">
  <div class="w-64 shrink-0">固定 256px</div>
  <div class="flex-1 min-w-0">弹性（可以缩小）</div>
</div>

<!-- 防止缩小，带文本溢出 -->
<div class="flex min-w-0">
  <div class="shrink-0">图标</div>
  <div class="min-w-0 truncate">非常长的文本应该溢出</div>
</div>
```

### 类马赛克布局

```html
<!-- 基于列的马赛克 -->
<div class="flex flex-col flex-wrap h-[800px] gap-4">
  <div class="w-[calc(33.333%-1rem)] h-48">项目 1</div>
  <div class="w-[calc(33.333%-1rem)] h-64">项目 2</div>
  <div class="w-[calc(33.333%-1rem)] h-32">项目 3</div>
  <!-- 项目垂直流动然后换到下一列 -->
</div>
```

## 容器查询

### 基本容器查询

```css
@plugin "@tailwindcss/container-queries";
```

```html
<!-- 定义容器 -->
<div class="@container">
  <!-- 响应容器宽度 -->
  <div class="flex flex-col @md:flex-row @lg:grid @lg:grid-cols-3 gap-4">
    <div>项目 1</div>
    <div>项目 2</div>
    <div>项目 3</div>
  </div>
</div>
```

### 命名容器

```html
<!-- 多个命名容器 -->
<div class="@container/sidebar">
  <nav class="@[200px]/sidebar:flex-col @[300px]/sidebar:flex-row">
    导航
  </nav>
</div>

<div class="@container/main">
  <article class="@[600px]/main:prose-lg @[900px]/main:prose-xl">
    内容
  </article>
</div>
```

### 容器查询单位

```html
<!-- 相对于容器尺寸 -->
<div class="@container">
  <h1 class="text-[5cqw]">随容器宽度缩放</h1>
  <p class="text-[3cqi]">随容器行内尺寸缩放</p>
</div>
```

## 定位和层级

### 粘性定位

```html
<!-- 粘性页眉 -->
<header class="sticky top-0 z-50 bg-white/80 backdrop-blur-sm border-b">
  导航
</header>

<!-- 粘性侧边栏 -->
<aside class="sticky top-20 h-[calc(100vh-5rem)] overflow-auto">
  侧边栏内容
</aside>

<!-- 粘性表格页眉 -->
<div class="overflow-auto max-h-96">
  <table>
    <thead class="sticky top-0 bg-white shadow">
      <tr>
        <th class="sticky left-0 bg-white z-10">角落单元格</th>
        <th>列 2</th>
      </tr>
    </thead>
    <tbody>...</tbody>
  </table>
</div>
```

### 固定元素

```html
<!-- 固定底部导航（移动端） -->
<nav class="fixed bottom-0 inset-x-0 z-50 bg-white border-t md:hidden">
  <div class="flex justify-around py-2">
    <a href="#">首页</a>
    <a href="#">搜索</a>
    <a href="#">个人资料</a>
  </div>
</nav>

<!-- 固定操作按钮 -->
<button class="fixed bottom-6 right-6 z-40 rounded-full bg-brand-500 p-4 shadow-lg">
  <PlusIcon />
</button>
```

### Z-索引管理

```css
@theme {
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-fixed: 300;
  --z-modal-backdrop: 400;
  --z-modal: 500;
  --z-popover: 600;
  --z-tooltip: 700;
  --z-toast: 800;
}

@utility z-dropdown { z-index: var(--z-dropdown); }
@utility z-sticky { z-index: var(--z-sticky); }
@utility z-fixed { z-index: var(--z-fixed); }
@utility z-modal-backdrop { z-index: var(--z-modal-backdrop); }
@utility z-modal { z-index: var(--z-modal); }
@utility z-popover { z-index: var(--z-popover); }
@utility z-tooltip { z-index: var(--z-tooltip); }
@utility z-toast { z-index: var(--z-toast); }
```

## 溢出和滚动

### 自定义滚动条

```css
@utility scrollbar-thin {
  scrollbar-width: thin;
}

@utility scrollbar-none {
  scrollbar-width: none;
  -ms-overflow-style: none;
}

@utility scrollbar-none::-webkit-scrollbar {
  display: none;
}

/* 自定义滚动条样式 */
@utility scrollbar-custom {
  scrollbar-color: oklch(0.7 0 0) oklch(0.95 0 0);
}

@utility scrollbar-custom::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

@utility scrollbar-custom::-webkit-scrollbar-track {
  background: oklch(0.95 0 0);
  border-radius: 4px;
}

@utility scrollbar-custom::-webkit-scrollbar-thumb {
  background: oklch(0.7 0 0);
  border-radius: 4px;
}

@utility scrollbar-custom::-webkit-scrollbar-thumb:hover {
  background: oklch(0.5 0 0);
}
```

### 滚动快照

```html
<!-- 水平轮播 -->
<div class="flex snap-x snap-mandatory overflow-x-auto gap-4 pb-4">
  <div class="snap-start shrink-0 w-80">卡片 1</div>
  <div class="snap-start shrink-0 w-80">卡片 2</div>
  <div class="snap-start shrink-0 w-80">卡片 3</div>
</div>

<!-- 全页部分 -->
<div class="h-screen snap-y snap-mandatory overflow-y-auto">
  <section class="h-screen snap-start">部分 1</section>
  <section class="h-screen snap-start">部分 2</section>
  <section class="h-screen snap-start">部分 3</section>
</div>

<!-- 带内边距的快照 -->
<div class="snap-x scroll-pl-6 overflow-x-auto">
  <div class="snap-start">...</div>
</div>
```

### 锚点的滚动外边距

```html
<!-- 固定页眉的偏移 -->
<section id="about" class="scroll-mt-20">
  <!-- 内容在固定页眉下方出现时 -->
</section>
```

## 宽高比和对象适配

### 响应式宽高比

```html
<!-- 固定宽高比容器 -->
<div class="aspect-video bg-gray-100">
  <video class="h-full w-full object-cover">...</video>
</div>

<div class="aspect-square rounded-full overflow-hidden">
  <img src="avatar.jpg" class="h-full w-full object-cover" />
</div>

<!-- 自定义宽高比 -->
<div class="aspect-[4/3]">4:3 内容</div>
<div class="aspect-[21/9]">超宽内容</div>
```

### 对象定位

```html
<!-- 聚焦图像的特定部分 -->
<div class="h-64 overflow-hidden">
  <img
    src="portrait.jpg"
    class="h-full w-full object-cover object-top"
  />
</div>

<!-- 任意对象位置 -->
<img class="object-cover object-[25%_75%]" src="..." />
```

## 高级间距

### 逻辑属性

```html
<!-- 适用于从左到右和从右到左的文本方向 -->
<div class="ps-4 pe-6 ms-auto">
  尊重文本方向的填充和边距
</div>

<!-- 块方向（水平书写模式的垂直方向） -->
<div class="pbs-4 pbe-6 mbs-auto">
  块方向间距
</div>
```

### 带分隔符的间距

```html
<!-- 项目之间的分隔符 -->
<ul class="divide-y divide-gray-200">
  <li class="py-4">项目 1</li>
  <li class="py-4">项目 2</li>
  <li class="py-4">项目 3</li>
</ul>

<!-- 水平分隔符 -->
<div class="flex divide-x divide-gray-200">
  <div class="px-4">部分 1</div>
  <div class="px-4">部分 2</div>
  <div class="px-4">部分 3</div>
</div>
```

### 负边距用于出血

```html
<!-- 带内边距容器的全宽出血图像 -->
<article class="px-6">
  <p>带内边距的内容</p>
  <img src="hero.jpg" class="-mx-6 w-[calc(100%+3rem)]" />
  <p>更多带内边距的内容</p>
</article>

<!-- 脱离内容宽度的引言 -->
<div class="max-w-prose mx-auto px-4">
  <p>正常内容...</p>
  <blockquote class="-mx-8 md:-mx-16 px-8 md:px-16 py-8 bg-gray-100">
    超出内容宽度的特色引言
  </blockquote>
</div>
```

## 多列布局

### 文本列

```html
<!-- 响应式列 -->
<div class="columns-1 sm:columns-2 lg:columns-3 gap-8">
  <p>内容流经列...</p>
</div>

<!-- 固定宽度列 -->
<div class="columns-[300px] gap-6">
  <p>创建尽可能多的 300px 列</p>
</div>

<!-- 防止元素内断行 -->
<div class="columns-2">
  <div class="break-inside-avoid mb-4">
    保持在一起的卡片
  </div>
</div>
```

## 响应式模式

### 容器查询 + 媒体查询

```html
<div class="@container">
  <div class="
    /* 组件级别的响应式 */
    @md:flex @md:gap-4

    /* 页面级别的响应式 */
    lg:grid lg:grid-cols-2
  ">
    内容
  </div>
</div>
```

### 基于断点的可见性

```html
<!-- 根据断点显示不同内容 -->
<nav>
  <!-- 移动端菜单按钮 -->
  <button class="md:hidden">菜单</button>

  <!-- 桌面端导航 -->
  <ul class="hidden md:flex gap-4">
    <li>首页</li>
    <li>关于</li>
    <li>联系</li>
  </ul>
</nav>
```

### 使用 Clamp 的流体尺寸

```html
<!-- 流体填充 -->
<section class="py-[clamp(2rem,5vw,6rem)] px-[clamp(1rem,3vw,4rem)]">
  带响应式填充的内容
</section>

<!-- 流体最大宽度 -->
<div class="mx-auto w-full max-w-[clamp(300px,90vw,1200px)]">
  响应式容器
</div>
```

## 打印样式

```html
<!-- 打印时隐藏元素 -->
<nav class="print:hidden">导航</nav>

<!-- 仅打印时显示 -->
<div class="hidden print:block">仅打印内容</div>

<!-- 打印特定样式 -->
<article class="print:text-black print:bg-white">
  <h1 class="text-2xl print:text-xl">标题</h1>
  <a href="..." class="text-blue-500 print:text-black print:underline">
    链接（打印时显示为文本）
  </a>
</article>

<!-- 防止页面断行 -->
<div class="print:break-inside-avoid">
  将此内容保持在同一页上
</div>

<!-- 强制页面断行 -->
<div class="print:break-before-page">
  开始新页面
</div>
```

## 最佳实践

### 1. 使用现代布局方法

```html
<!-- 优先使用 Grid 进行 2D 布局 -->
<div class="grid grid-cols-3 gap-4">

<!-- 优先使用 Flexbox 进行 1D 布局 -->
<div class="flex items-center gap-2">
```

### 2. 处理边缘情况

```html
<!-- 防止 Flex 项目溢出 -->
<div class="flex min-w-0">
  <div class="min-w-0 truncate">长文本</div>
</div>

<!-- 防止 Grid 溢出 -->
<div class="grid grid-cols-1 min-w-0">
  <div class="overflow-hidden">可能溢出的内容</div>
</div>
```

### 3. 使用语义尺寸

```html
<!-- 优先使用 max-w-prose 用于阅读内容 -->
<article class="max-w-prose mx-auto">

<!-- 使用 container 用于页面部分 -->
<div class="container mx-auto px-4">
```

### 4. 测试所有断点

为所有响应式布局创建系统测试，确保它们在所有断点都能正常工作。
