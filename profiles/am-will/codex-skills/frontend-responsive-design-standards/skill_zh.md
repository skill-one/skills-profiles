# 前端响应式设计标准

**规则：** 采用移动优先开发方式，保持一致的断点、流体布局、相对单位以及触控友好的目标尺寸。

## 何时使用此技能

- 创建或修改需要在移动设备、平板和桌面设备上运行的布局时
- 实施以移动布局为起点的移动优先设计模式时
- 编写媒体查询或特定断点样式时
- 使用灵活单位（rem、em、%）而不是固定像素以实现可扩展性时
- 实现基于百分比的宽度或flexbox/网格的流体布局时
- 确保触控目标满足最小尺寸要求（44x44px）的移动设备时
- 优化不同屏幕尺寸和移动网络下的图像和资源时
- 在多个设备尺寸和断点下测试UI时
- 在所有屏幕尺寸上保持可读的排版时
- 通过布局决策优先在小屏幕上显示内容时
- 在CSS框架（Tailwind、Bootstrap响应式类）中使用响应式设计工具时

此技能为Codex提供具体指导，说明如何遵循与前端响应式处理相关的编码标准。

## 移动优先开发 - 必须执行

**始终从移动布局开始，然后为更大的屏幕进行增强。**

错误的（桌面优先）：
```css
.container {
  width: 1200px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
}

@media (max-width: 768px) {
  .container {
    width: 100%;
    grid-template-columns: 1fr;
  }
}
```

正确的（移动优先）：
```css
.container {
  width: 100%;
  display: grid;
  grid-template-columns: 1fr;
}

@media (min-width: 768px) {
  .container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .container {
    max-width: 1200px;
    grid-template-columns: repeat(4, 1fr);
  }
}
```

**为什么采用移动优先：**
- 强制内容优先级
- 移动设备性能更好（无需覆盖）
- 渐进增强而非渐进退化

## 标准断点

**一致地识别和使用项目断点：**

常见的断点系统：

Tailwind：
```
sm: 640px   (小平板)
md: 768px   (平板)
lg: 1024px  (笔记本电脑)
xl: 1280px  (台式电脑)
2xl: 1536px (大台式电脑)
```

Bootstrap：
```
sm: 576px
md: 768px
lg: 992px
xl: 1200px
xxl: 1400px
```

**在创建新断点前检查现有代码库中的断点定义。**

使用示例（Tailwind）：
```jsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4">
```

使用示例（CSS）：
```css
@media (min-width: 768px) { }
@media (min-width: 1024px) { }
```

**除非明确要求，否则不要使用随意的断点，如850px或1150px。**

## 流体布局

**使用适应屏幕尺寸的灵活容器：**

错误的（固定宽度）：
```css
.container { width: 1200px; }
.sidebar { width: 300px; }
.content { width: 900px; }
```

正确的（流体）：
```css
.container {
  width: 100%;
  max-width: 1200px;
  padding: 0 1rem;
}

.layout {
  display: grid;
  grid-template-columns: 1fr;
}

@media (min-width: 1024px) {
  .layout {
    grid-template-columns: 300px 1fr;
  }
}
```

**流体布局模式：**
- Flexbox: `flex: 1`, `flex-grow`, `flex-shrink`
- Grid: `1fr`, `minmax()`, `auto-fit`, `auto-fill`
- 百分比宽度: `width: 100%`, `max-width: 1200px`
- 容器查询（现代）: `@container (min-width: 400px)`

## 相对单位优于固定像素

**使用rem/em以实现可扩展性和可访问性：**

错误的：
```css
font-size: 16px;
padding: 20px;
margin: 10px;
border-radius: 8px;
```

正确的：
```css
font-size: 1rem;      /* 16px基准 */
padding: 1.25rem;     /* 20px */
margin: 0.625rem;     /* 10px */
border-radius: 0.5rem; /* 8px */
```

**何时使用每个单位：**
- `rem`: 字体大小、间距、布局尺寸（随根字体大小缩放）
- `em`: 组件相对尺寸（随父字体大小缩放）
- `%`: 宽度、高度相对于父元素
- `px`: 边框（1px）、阴影、非常小的值
- `vw/vh`: 全视口尺寸，英雄区域
- `ch`: 基于文本的宽度（例如 `max-width: 65ch` 以获得可读的行长度）

**框架工具自动处理这些：**
```jsx
<div className="text-base p-5 m-2.5 rounded-lg">
```

## 触控友好设计

**最小触控目标尺寸：44x44px（iOS）/ 48x48px（Android）**

错误的：
```css
.icon-button {
  width: 24px;
  height: 24px;
}
```

正确的：
```css
.icon-button {
  width: 24px;
  height: 24px;
  padding: 12px; /* 总计：48x48px */
  /* 或者使用min-width/min-height */
  min-width: 44px;
  min-height: 44px;
}
```

**触控目标检查清单：**
- [ ] 按钮最小44x44px
- [ ] 文本中的链接有足够的间距
- [ ] 表单输入有足够的高度（最小44px）
- [ ] 图标按钮有填充以获得更大的点击区域
- [ ] 交互元素之间的间距（最小8px）

## 可读排版

**保持无需缩放即可阅读的字体大小：**

错误的：
```css
body { font-size: 12px; }
.small-text { font-size: 10px; }
```

正确的：
```css
body { font-size: 1rem; } /* 16px最小值 */
.small-text { font-size: 0.875rem; } /* 14px最小值 */
```

**排版指南：**
- 正文：16px（1rem）最小值
- 小文本：14px（0.875rem）最小值
- 行高：正文1.5，标题1.2
- 行长：45-75个字符（使用 `max-width: 65ch`）
- 对比度：WCAG AA最小值（普通文本4.5:1）

响应式排版：
```css
h1 {
  font-size: 2rem;
}

@media (min-width: 768px) {
  h1 {
    font-size: 2.5rem;
  }
}

@media (min-width: 1024px) {
  h1 {
    font-size: 3rem;
  }
}
```

或者使用clamp（流体）：
```css
h1 {
  font-size: clamp(2rem, 5vw, 3rem);
}
```

## 移动端内容优先级

**首先显示最重要的内容，隐藏或折叠次要内容：**

错误的：
```jsx
<div>
  <Sidebar /> {/* 移动端全屏侧边栏 */}
  <MainContent />
</div>
```

正确的：
```jsx
<div className="flex flex-col lg:flex-row">
  <MainContent className="order-1" />
  <Sidebar className="order-2 hidden lg:block" />
</div>
```

**策略：**
- 在移动端隐藏非必要元素
- 使用汉堡菜单进行导航
- 折叠手风琴/标签以显示次要内容
- 在移动端垂直堆叠布局
- 使用 `order` 属性重新排序内容

## 图像优化

**为不同设备提供适当的图像：**

错误的：
```html
<img src="hero-4000x3000.jpg" alt="英雄">
```

正确的：
```html
<img
  src="hero-800x600.jpg"
  srcset="
    hero-400x300.jpg 400w,
    hero-800x600.jpg 800w,
    hero-1600x1200.jpg 1600w
  "
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 800px"
  alt="英雄"
>
```

或者使用现代格式：
```html
<picture>
  <source srcset="hero.avif" type="image/avif">
  <source srcset="hero.webp" type="image/webp">
  <img src="hero.jpg" alt="英雄">
</picture>
```

**框架特定示例：**
```jsx
// Next.js
<Image
  src="/hero.jpg"
  width={800}
  height={600}
  sizes="(max-width: 768px) 100vw, 50vw"
  alt="英雄"
/>
```

## 跨设备测试

**在完成工作前在关键断点验证布局：**

测试清单：
- [ ] 手机（375px - iPhone SE）
- [ ] 手机大屏（414px - iPhone Pro Max）
- [ ] 平板（768px - iPad）
- [ ] 笔记本电脑（1024px）
- [ ] 台式电脑（1440px）

**测试方法：**
1. 浏览器开发者工具响应式模式
2. 真实设备测试（iOS/Android）
3. 浏览器扩展（响应式查看器）
4. 自动化视觉回归测试

**常见问题检查：**
- 移动端水平滚动
- 文本溢出或截断
- 元素重叠
- 字体大小难以阅读
- 触控目标太小
- 图像未加载或失真

## 常见响应式模式

**导航：**
```jsx
// 移动端：汉堡菜单
// 桌面端：水平导航
<nav className="lg:flex lg:items-center">
  <button className="lg:hidden">菜单</button>
  <ul className="hidden lg:flex lg:gap-4">
    <li>首页</li>
    <li>关于</li>
  </ul>
</nav>
```

**网格布局：**
```css
.grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 640px) {
  .grid { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 1024px) {
  .grid { grid-template-columns: repeat(4, 1fr); }
}
```

**侧边栏布局：**
```css
.layout {
  display: flex;
  flex-direction: column;
}

@media (min-width: 1024px) {
  .layout {
    flex-direction: row;
  }
  .sidebar { width: 300px; }
  .content { flex: 1; }
}
```

## 验证清单

完成响应式工作前：

- [ ] 从移动布局开始
- [ ] 使用项目的标准断点
- [ ] 实现流体布局（无固定宽度）
- [ ] 使用相对单位（rem/em）进行尺寸设置
- [ ] 触控目标最小44x44px
- [ ] 排版可无缩放阅读（正文16px+）
- [ ] 优先移动端内容
- [ ] 优化不同尺寸的图像
- [ ] 在所有关键断点测试
- [ ] 无移动端水平滚动
- [ ] 无重叠或截断内容

## 快速参考

| 情况         | 操作                               |
| ------------ | ---------------------------------- |
| 新建布局     | 从移动端（320-375px）开始          |
| 需要断点     | 使用项目标准（检查现有代码）       |
| 设置宽度     | 使用 `width: 100%` + `max-width`   |
| 设置字体大小 | 使用 `rem`（16px = 1rem）          |
| 设置间距     | 使用 `rem` 或框架工具             |
| 按钮太小     | 确保最小44x44px并添加填充         |
| 文本太小     | 正文最小16px（1rem）               |
| 测试布局     | 检查375px、768px、1024px、1440px   |
| 图像加载慢   | 使用srcset和现代格式               |
