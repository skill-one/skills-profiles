# HyperFrames 的 Tailwind CSS

HyperFrames 的 `init --tailwind` 使用的是固定在 `@tailwindcss/browser@4.2.4` 的 Tailwind 浏览器运行时。将其视为 Tailwind v4，而不是 v3。

这个技能用于 CLI 生成的 HTML 组合。它不适用于 `packages/studio`，后者内部仍然使用 Tailwind v3 以及 `tailwind.config.js`、PostCSS 和 `@tailwind` 指令。

## 使用场景

- 用户在 HyperFrames 组合中要求使用 Tailwind。
- 使用 `hyperframes init --tailwind` 创建了项目。
- 在 `index.html` 中看到 `window.__tailwindReady`。
- 需要工具类、CSS-优先主题令牌、自定义工具或 v3 到 v4 迁移指南。
- 渲染缺少样式，且项目依赖于浏览器运行时。

## 版本契约

- 固定的运行时：`@tailwindcss/browser@4.2.4`。
- 浏览器运行时脚本由 CLI 注入。不要用 `cdn.tailwindcss.com` 替换它。
- HyperFrames 在帧捕获开始前等待 `window.__tailwindReady`。
- 准备就绪的遮罩层必须保持确定性：不要使用渲染循环轮询 API，不要使用基于时钟的重试，不要在固定的 Tailwind 运行时脚本之外进行运行时网络获取。
- 对于离线、锁定或生产稳定的渲染，将 Tailwind 编译为 CSS 并直接包含样式表，而不是依赖浏览器运行时。

## v4 规则

Tailwind v4 是 CSS-优先的：

```html
<style type="text/tailwindcss">
  @theme {
    --color-brand: oklch(0.68 0.2 252);
    --font-display: "Inter", sans-serif;
  }

  @utility headline-balance {
    text-wrap: balance;
    letter-spacing: 0;
  }
</style>
```

在浏览器运行时组合中避免使用 v3 设置模式：

```css
/* 不要在 Tailwind v4 浏览器运行时组合中使用这些。 */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

不要仅仅为了为 v4 浏览器运行时组合定义颜色、字体、间距或工具类而添加 `tailwind.config.js`。在 `text/tailwindcss` 样式块中使用 `@theme` 和 `@utility`。

如果你确实需要一个现有的 JavaScript 配置用于编译的 v4 构建，请使用 `@config` 从 CSS 中显式加载它，然后在浏览器中验证。不要假设 v4 自动检测 v3 配置文件。

## HyperFrames 组合模式

让 Tailwind 负责静态布局和视觉样式。让 GSAP 或其他可搜索适配器负责运动时间。

```html
<section
  class="clip absolute inset-0 grid place-items-center bg-zinc-950 text-white"
  data-start="0"
  data-duration="5"
  data-track-index="1"
>
  <div class="w-[1280px] max-w-[82vw] text-center">
    <p class="mb-6 text-xl font-medium uppercase tracking-[0.18em] text-cyan-300">
      Render-ready Tailwind
    </p>
    <h1 class="text-7xl font-black leading-none text-balance">
      Utility classes, deterministic frames.
    </h1>
  </div>
</section>
```

对于重复项，优先使用类列表加上 CSS 自定义属性，而不是动态生成类名：

```html
<span class="inline-block translate-y-[calc(var(--i)*6px)] opacity-80" style="--i: 0"></span>
<span class="inline-block translate-y-[calc(var(--i)*6px)] opacity-80" style="--i: 1"></span>
<span class="inline-block translate-y-[calc(var(--i)*6px)] opacity-80" style="--i: 2"></span>
```

## 动态类安全性

Tailwind 的浏览器运行时会扫描当前文档并为它能看到的类名生成 CSS。不要仅在可搜索时间构建渲染关键类名：

```js
// 有风险：Tailwind 可能不会在捕获前看到所有生成的类。
element.className = `bg-${color}-500`;
```

在 HTML、数据属性或显式 CSS 中使用完整的类名：

```html
<div data-tone="blue" class="bg-blue-500 data-[tone=rose]:bg-rose-500"></div>
```

如果无法避免生成类名，请确保完整的类令牌在验证前出现在 `text/tailwindcss` 块中。

## 视频特定限制

- 使用稳定尺寸：`w-[...]`、`h-[...]`、`aspect-video`、`grid`、`flex` 和固定填充用于视频布局。
- 优先使用变换和透明度进行动画属性。
- 除非可搜索运行时拥有状态，否则不要在渲染关键时间中使用 Tailwind 过渡。
- 避免对于必须确定性地渲染的内容使用悬停、焦点、滚动、视口或指针变体。
- 使用显式边框颜色。Tailwind v4 改变了 v3 的默认边框行为，因此 `border border-white/20` 比裸 `border` 更安全。
- 使用 v4 工具名：`shadow-xs`、`rounded-xs`、`outline-hidden`、`shrink-*` 和 `grow-*`，在这些替换适用的情况下。
- 如果输出需要旧版浏览器支持，请小心使用现代 CSS 工具。Tailwind v4 针对现代浏览器。

## 验证

编辑了启用 Tailwind 的组合后：

```bash
npx hyperframes lint
npx hyperframes validate
npx hyperframes inspect
```

对于渲染预览：

```bash
npx hyperframes render . --workers 1 --quality draft --output tailwind-proof.mp4
```

验证路径应显示在帧 0 上没有缺少样式的闪烁。如果预览中显示样式但在渲染中不显示，请检查 `window.__tailwindReady` 是否存在并在捕获前解析。

## 快速调试清单

1. 确认项目使用 `hyperframes init --tailwind` 框架。
2. 确认脚本指向 `@tailwindcss/browser@4.2.4`。
3. 确认 `window.__tailwindReady` 存在。
4. 将 v3 `@tailwind` 指令替换为 v4 浏览器运行时 CSS。
5. 将自定义令牌从 `tailwind.config.js` 移动到 `@theme`。
6. 将动态组装的类替换为完整的静态令牌。
7. 运行 `npx hyperframes validate` 并渲染简短的预览。

## 致谢和参考

- Tailwind CSS 官方 v4 安装、升级和兼容性文档：https://tailwindcss.com/docs
- Tailwind CSS v4 发布说明：https://tailwindcss.com/blog/tailwindcss-v4
- 社区 Tailwind 技能已针对 v4 潜在问题和技能形状进行了审查，但此技能在存储库中保持耐久契约和 HyperFrames 特定内容。
