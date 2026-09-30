---
name: preload
description: 教授资源预加载技术，优先处理关键资源。当关键资源（如字体、英雄图片或核心脚本）在加载瀑布流中后期被发现时使用。
---

# 预加载

## 目录

- [何时使用](#何时使用)
- [何时不建议使用](#何时不建议使用)
- [使用说明](#使用说明)
- [详细信息](#详细信息)
- [来源](#来源)

[预加载](https://developer.mozilla.org/en-US/docs/Web/HTML/Preloading_content) (`<link rel="preload">`) 是一种 [浏览器优化](https://web.dev/uses-rel-preload/) 技术，允许关键资源（可能较晚被发现）提前请求。如果你愿意手动考虑如何加载你的关键资源，它可以在 [核心网络指标](https://web.dev/vitals) 中对加载性能和指标产生积极影响。但请注意，预加载并非万能药，需要了解一些权衡。

## 何时使用

- 当关键资源（字体、脚本、图像）在加载过程中较晚被发现时使用
- 有助于提高交互准备时间 (TTI) 和最大内容绘制 (LCP)

## 何时不建议使用

- 对于非关键资源——预加载过多资源会延迟对初始渲染实际重要的资源
- 当资源已经被浏览器的预加载扫描器较早发现时（例如，`<head>` 中的内联 `<script>` 标签）
- 当过度使用导致浏览器对未使用的预加载资源发出警告，表明带宽浪费时

## 使用说明

- 使用 `<link rel="preload">` 预加载当前页面立即需要的资源
- 注意不要因为预加载过多资源而延迟首次内容绘制 (FCP)
- 使用 `as` 属性指定资源类型（脚本、样式、字体、图像）
- 对于字体和其他 CORS 获取的资源，在预加载中设置 `crossorigin` 以匹配最终请求模式
- 仅预加载必须在初始渲染后约 1 秒内可见的资源

## 详细信息

```html
<link rel="preload" href="emoji-picker.js" as="script">
...
</head>
<body>
  ...
  <script src="stickers.js" defer></script>
  <script src="video-sharing.js" defer></script>
  <script src="emoji-picker.js" defer></script>
```

在优化 [交互准备时间](https://web.dev/tti) 或 [首次输入延迟](https://web.dev/fid) 等指标时，预加载可用于加载对交互必要的 JavaScript 包（或块）。使用预加载时需要小心，因为你想避免以延迟资源（如英雄图像或字体）为代价来提高交互性，而这些资源对于 [首次内容绘制](https://web.dev/fcp) 或 [最大内容绘制](https://web.dev/lcp) 是必要的。

如果你正在尝试优化第一方 JavaScript 的加载，也可以考虑在文档 `<head>` 中使用 `<script defer>` 而不是 `<body>` 来帮助早期发现这些资源。

### 单页应用中的预加载

虽然 **预取** 是缓存可能很快被请求的资源的好方法，但我们可以 **预加载** 需要立即使用的资源。可能是初始渲染时使用的特定字体，或者是用户立即看到的某些图像。

假设我们的 `EmojiPicker` 组件应在初始渲染时立即可见。尽管它不应包含在主包中，但它应该并行加载。就像 **预取** 一样，我们可以在导入中添加一个魔法注释，让 Webpack 知道这个模块应该预加载。

```js
const EmojiPicker = import(/* webpackPreload: true */ "./EmojiPicker");
```

> Webpack 4.6.0+ 允许通过在导入中添加 `/* webpackPreload: true */` 来预加载资源。为了在较旧版本的 Webpack 中使预加载生效，你需要将 [`preload-webpack-plugin`](https://github.com/GoogleChromeLabs/preload-webpack-plugin) 添加到你的 Webpack 配置中。

构建应用程序后，我们可以看到 `EmojiPicker` 将被预加载。

```
 Asset                             Size       Chunks                          Chunk Names
    emoji-picker.bundle.js         1.49 KiB   emoji-picker [emitted]          emoji-picker
    vendors~emoji-picker.bundle.js 171 KiB    vendors~emoji-picker [emitted]  vendors~emoji-picker
    main.bundle.js                 1.34 MiB   main  [emitted]                 main

Entrypoint main = main.bundle.js
(preload: vendors~emoji-picker.bundle.js emoji-picker.bundle.js)
```

实际输出显示为文档 `<head>` 中的 `link` 标签，`rel="preload"`。

```html
<link rel="preload" href="emoji-picker.bundle.js" as="script" />
<link rel="preload" href="vendors~emoji-picker.bundle.js" as="script" />
```

预加载的 `EmojiPicker` 可以与初始包并行加载。与 `prefetch` 不同，浏览器仍然可以决定它是否有足够的互联网连接和带宽来实际预取资源，而 **预加载** 资源将无论如何都会被预加载。

我们不需要等到 `EmojiPicker` 在初始渲染后加载，资源将立即可用！随着我们以更智能的顺序加载资源，初始加载时间可能会根据用户设备和互联网连接显著增加。仅预加载必须在初始渲染后约 1 秒内可见的资源。

### 预加载 + `async` 诡计

如果你希望浏览器以高优先级下载脚本，但不要阻塞解析器等待脚本，你可以利用以下预加载 + `async` 诡计。在这种情况下，其他资源的下载可能会被延迟，但这是一位开发者必须做出的权衡：

```html
<link rel="preload" href="emoji-picker.js" as="script">
<script src="emoji-picker.js" async>
```

### 字体预加载必须使用 `crossorigin`

字体作为 CORS 资源获取，即使它们在同一个源上自托管。这意味着预加载请求和最终的 `@font-face` 请求需要使用相同的获取模式，否则预加载无法重用。

如果你预加载字体 **没有** `crossorigin`，浏览器通常会发出 `no-cors` 预加载请求，稍后 CSS 发现字体时再发出单独的 `cors` 请求。这会导致同一文件的双重获取并浪费带宽。

**避免：**

```html
<link rel="preload" href="/fonts/inter-roman.woff2" as="font" type="font/woff2">
```

**推荐：**

```html
<link
  rel="preload"
  href="/fonts/inter-roman.woff2"
  as="font"
  type="font/woff2"
  crossorigin
>
```

并确保 `@font-face` 匹配相同的资源：

```css
@font-face {
  font-family: "Inter";
  src: url("/fonts/inter-roman.woff2") format("woff2");
  font-display: swap;
}
```

相同的规则更广泛地适用：如果最终的消费者以 CORS 语义获取资源，预加载应该匹配该模式。

### Chrome 95+ 中的预加载

得益于 Chrome 95+ 中对预加载的 **排队优先** 行为的一些 [修复](https://twitter.com/patmeenan/status/1436374668450177026)，该功能现在更广泛地使用时稍微安全一些。Chrome 新的预加载建议 Pat Meenan 建议如下：

- 将它放在 HTTP 头中会优先于所有其他内容
- 通常，预加载将按解析器到达它们的顺序加载，对于任何大于或等于中等优先级的内容，要小心在 HTML 的开头放置预加载
- 字体预加载可能最好在头部末尾或正文开头
- 导入预加载应在需要导入的脚本标签之后执行（以便实际脚本首先加载/解析）
- 图像预加载将具有低优先级，应相对于异步脚本和其他低/最低优先级标签排序

### 结论

再次强调，要谨慎使用预加载，并在生产环境中测量其影响。如果你的图像预加载在文档中的位置比实际位置早，这可以帮助浏览器发现它（并相对于其他资源排序）。如果使用不当，预加载可能会导致图像延迟首次内容绘制 (FCP)（例如 CSS、字体）——这与你想要的结果相反。还请注意，为了使此类重新排序工作有效，它还取决于 [服务器正确优先处理请求](https://github.com/andydavies/http2-prioritization-issues#cdns--cloud-hosting-services)。

你可能会发现 `<link rel="preload">` 在需要 [不执行](https://developer.mozilla.org/en-US/docs/Web/HTML/Preloading_content#scripting_and_preloads) 脚本的情况下很有帮助。

各种 `web.dev` 文章探讨了如何使用预加载：

- [预加载对交互性必要的键脚本](https://web.dev/uses-rel-preload/)
- [预加载你的最大内容绘制图像](https://web.dev/preload-responsive-images/)
- [加载字体时防止布局偏移](https://web.dev/preload-optional-fonts/)

## 来源

- [patterns.dev/vanilla/preload](https://patterns.dev/vanilla/preload)
