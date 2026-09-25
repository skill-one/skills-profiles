# Tailwind CSS 开发模式

使用 Tailwind CSS 工具优先框架构建现代、响应式用户界面的专家指南。涵盖 v4.1+ 功能，包括 CSS 优先配置、自定义工具和增强的开发体验。

## 概述

提供 Tailwind CSS v4.1+ 的响应式、可访问 UI 的实用模式。涵盖工具组合、暗黑模式、组件模式和性能优化。

## 何时使用

- 样式化 React/Vue/Svelte 组件
- 构建响应式布局和网格
- 实施设计系统
- 添加暗黑模式支持
- 优化 CSS 工作流程

## 快速参考

### 响应式断点

| 前缀 | 最小宽度 | 描述 |
|------|----------|-------|
| `sm:` | 640px | 小屏幕 |
| `md:` | 768px | 平板 |
| `lg:` | 1024px | 台式机 |
| `xl:` | 1280px | 大屏幕 |
| `2xl:` | 1536px | 超大 |

### 常见模式

```html
<!-- 居中内容 -->
<div class="flex items-center justify-center min-h-screen">
  内容
</div>

<!-- 响应式网格 -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
  <!-- 项目 -->
</div>

<!-- 卡片组件 -->
<div class="bg-white rounded-lg shadow-lg p-6">
  <h3 class="text-xl font-bold">标题</h3>
  <p class="text-gray-600">描述</p>
</div>
```

## 说明

1. **从移动端优先开始**：为移动端编写基础样式，为较大屏幕添加响应式前缀（`sm:`, `md:`, `lg:`）
2. **使用设计令牌**：利用 Tailwind 的间距、颜色和排版量表
3. **组合工具**：组合多个工具以实现复杂样式
4. **提取组件**：创建可重用的组件类以实现重复模式
5. **配置主题**：在 `tailwind.config.js` 中自定义设计令牌或使用 `@theme`
6. **验证更改**：使用 DevTools 响应式模式在每个断点测试。在提交前检查视觉回归和可访问性问题。

## 示例

### 响应式卡片组件

```tsx
function ProductCard({ product }: { product: Product }) {
  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden sm:flex">
      <img className="h-48 w-full object-cover sm:h-auto sm:w-48" src={product.image} />
      <div className="p-6">
        <h3 className="text-lg font-semibold">{product.name}</h3>
        <button className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
          加入购物车
        </button>
      </div>
    </div>
  );
}
```

### 暗黑模式切换

```html
<div class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
  <h1 class="dark:text-white">标题</h1>
</div>
```

### 表单输入

```html
<input
  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
  placeholder="you@example.com"
/>
```

## 最佳实践

1. **一致的间距**：使用 Tailwind 的间距量表（4, 8, 12, 16 等）
2. **调色板**：坚持使用 Tailwind 的颜色系统以保持一致性
3. **组件提取**：将重复模式提取为可重用组件
4. **工具组合**：优先使用工具类而非 `@apply` 以提高可维护性
5. **语义 HTML**：使用带有 Tailwind 类的适当 HTML 元素
6. **性能**：确保内容路径包含所有模板文件以实现最佳清除效果
7. **可访问性**：包含焦点样式、ARIA 标签并尊重用户偏好（减少动画）

## 故障排除

### 类不应用

- **检查内容路径**：确保所有模板文件包含在配置中的 `content: []`
- **验证构建**：运行 `npm run build` 以重新生成清除的 CSS
- **开发模式**：使用 `npx tailwindcss -o` 并带 `--watch` 标志进行实时更新

### 响应式样式不工作

- **顺序重要**：响应式前缀必须位于非响应式之前（例如，`md:flex` 而不是 `flex md:flex`）
- **检查断点值**：验证断点是否满足设计要求
- **DevTools**：使用浏览器 DevTools 响应式模式在各个断点测试

### 暗黑模式问题

- **验证配置**：确保 `darkMode: 'class'` 或 `'media'` 设置正确
- **切换实现**：使用 `document.documentElement.classList.toggle('dark')` 实现类策略
- **初始闪烁**：在 body 渲染前将 `dark` 类添加到 `<html>`

## 限制和警告

- **类膨胀**：长类字符串降低可读性；提取为组件
- **内容路径**：配置错误会导致生产环境清除类
- **任意值**：谨慎使用；优先使用设计令牌以保持一致性
- **特异性问题**：避免使用 `@apply` 复杂选择器
- **暗黑模式**：需要正确配置（类或媒体策略）
- **浏览器支持**：查阅 Tailwind 文档了解兼容性说明

## 参考

- **[references/layout-patterns.md](references/layout-patterns.md)** — Flexbox、grid、间距、排版、颜色
- **[references/component-patterns.md](references/component-patterns.md)** — 卡片、导航、表单、模态、React 模式
- **[references/responsive-design.md](references/responsive-design.md)** — 响应式模式、暗黑模式、容器查询
- **[references/animations.md](references/animations.md)** — 过渡、变换、内置动画、运动偏好
- **[references/performance.md](references/performance.md)** — 打包优化、CSS 优化、生产构建
- **[references/accessibility.md](references/accessibility.md)** — 焦点管理、屏幕阅读器、颜色对比、ARIA
- **[references/configuration.md](references/configuration.md)** — CSS 优先配置、JavaScript 配置、插件、预设
- **[references/reference.md](references/reference.md)** — 额外参考材料

## 外部资源

- [Tailwind CSS 文档](https://tailwindcss.com/docs)
- [Tailwind UI](https://tailwindui.com)
- [Tailwind Play](https://play.tailwindcss.com)
