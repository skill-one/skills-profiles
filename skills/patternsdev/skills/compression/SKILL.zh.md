---
name: compression
description: 教授 JavaScript 压缩技术，包括 Gzip 和 Brotli。在优化网络传输时间或为生产构建配置服务器端压缩时使用。
---

# 压缩 JavaScript

## 目录

- [何时使用](#何时使用)
- [说明](#说明)
- [详情](#详情)
- [来源](#来源)

JavaScript 是网页大小的第二大[贡献者](https://almanac.httparchive.org/en/2020/page-weight#fig-2)，也是继图片之后互联网上第二常见的[网络资源](https://almanac.httparchive.org/en/2020/page-weight#fig-4)。我们使用减少 JavaScript 传输、加载和执行时间的模式来提高网站性能。压缩可以帮助减少在网络传输脚本所需的时间。

## 何时使用

- 当你需要减少 JavaScript 载荷大小以实现更快的页面加载时使用
- 在优化网络传输时间时很有帮助，特别是对于连接速度较慢的用户
- 与最小化、代码拆分和缓存策略一起使用

## 说明

- 优先使用 Brotli 压缩而不是 Gzip，以在相似速度下获得更好的压缩率
- 对于不经常变化的资源使用静态压缩，对于经常变化的动态内容使用动态压缩
- 在服务器或 CDN 层级启用压缩（例如 Nginx、Vercel、Netlify）
- 在应用压缩之前先最小化 JavaScript
- 注意粒度权衡：较大的包压缩效果更好，但较小的块缓存效果更好

## 详情

你可以将压缩与其他技术（如最小化、代码拆分、打包、缓存和懒加载）结合使用，以减少大量 JavaScript 的性能影响。然而，这些技术的目标有时会相互冲突。本节探讨了 JavaScript 压缩技术，并讨论了在决定代码拆分和压缩策略时应考虑的细微差别。

- **Gzip** 和 **Brotli** 是压缩 JavaScript 最常见的方法，并且被现代浏览器广泛支持。
- **Brotli** 在相似的压缩级别下提供**更好的压缩率**。
- **Next.js** 默认提供 [Gzip 压缩](https://nextjs.org/docs/api-reference/next.config.js/compression)，但建议在 HTTP 代理（如 Nginx）上启用它。
- 如果你使用 **Webpack** 打包代码，可以使用 **[CompressionPlugin](https://github.com/webpack-contrib/compression-webpack-plugin)** 进行 Gzip 压缩，或使用 [BrotliWebpackPlugin](https://github.com/mynameiswhm/brotli-webpack-plugin) 进行 Brotli 压缩。
- Oyo 在切换到 **Brotli 压缩而不是 Gzip** 后，文件大小减少了 **15-20%**，Wix 减少了 **21-25%**。
- **compress(a + b) <= compress(a) + compress(b)** - 一个大的单一包将提供比多个小包更好的压缩效果。这导致了粒度权衡，其中去重和缓存与浏览器性能和压缩相互冲突。粒度拆分可以帮助应对这种权衡。

### HTTP 压缩

压缩可以减小文档和文件的大小，因此它们占用的磁盘空间比原始文件小。较小的文档消耗更低的带宽，并且可以快速地在网络上传输。HTTP 压缩使用这个简单的概念来压缩网站内容，减少 [页面权重](https://almanac.httparchive.org/en/2020/page-weight)，降低带宽需求，并提高性能。

HTTP 数据压缩可以按不同的方式分类。其中一种分类是损失性压缩与无损压缩。

**损失性压缩** 意味着压缩-解压缩周期会导致文档略有变化，但仍然保持其可用性。这种变化对最终用户来说几乎是 imperceptible 的。最常见的损失性压缩示例是用于图像的 JPEG 压缩。

使用 **无损压缩**，压缩和解压缩后的数据将与原始数据完全匹配。PNG 图像是无损压缩的示例。无损压缩与文本传输相关，应应用于文本格式，如 HTML、CSS 和 JavaScript。

由于你希望在浏览器上拥有所有有效的 JS 代码，因此应使用无损压缩算法对 JavaScript 代码进行压缩。在压缩 JS 之前，最小化有助于消除不必要的语法，并将其减少到仅包含执行所需代码。

### 最小化

为了减小负载大小，你可以在压缩之前对 JavaScript 进行最小化。[最小化](https://web.dev/reduce-network-payloads-using-text-compression/#minification) 通过删除空白和任何不必要的代码来补充压缩，以创建一个更小但完全有效的代码文件。在编写代码时，我们使用换行符、缩进、空格、命名良好的变量和注释来提高代码的可读性和可维护性。然而，这些元素会增加 JavaScript 的总体大小，并且对于在浏览器上执行不是必要的。最小化将 JavaScript 代码减少到成功执行所需的最小代码。

最小化是 JS 和 CSS 优化的标准做法。通常，JavaScript 库开发人员会为生产部署提供最小化的文件版本，通常以 min.js 扩展名表示。（例如，`jquery.js` 和 `jquery.min.js`）

有多种工具可用于 [最小化 HTML、CSS 和 JS](https://developers.google.com/speed/docs/insights/MinifyResources) 资源。[Terser](https://github.com/terser-js/terser) 是一个流行的 ES6+ JavaScript 压缩工具，[Webpack](https://webpack.js.org/) v4 默认包含此库的插件来创建最小化构建文件。你也可以使用 `TerserWebpackPlugin` 与较旧版本的 Webpack 或不使用模块打包器将 Terser 作为 CLI 工具使用。

### 静态与动态压缩

最小化可以显著减小文件大小，但 JS 压缩可以提供更大的收益。你可以以两种方式实现服务器端压缩。

**静态压缩**：你可以使用静态压缩来预先压缩资源，并在构建过程中提前保存它们。在这种情况下，你可以使用更高的压缩级别，以提高代码的下载时间。高构建时间不会影响网站性能。你应该对不经常变化的文件使用静态压缩。

**动态压缩**：通过此过程，压缩在浏览器请求资源时动态进行。动态压缩更容易实现，但你只能使用较低的压缩级别。较高的压缩级别需要更多时间，并且你会失去从较小的内容大小中获得的收益。你应该对经常变化或由应用程序生成的内容使用动态压缩。

根据应用程序内容类型，你可以使用静态或动态压缩。你可以使用流行的压缩算法启用静态和动态压缩，但每种情况下的推荐压缩级别都不同。

### 压缩算法

[Gzip](https://datatracker.ietf.org/doc/html/rfc1952) 和 [Brotli](https://opensource.googleblog.com/2015/09/introducing-brotli-new-compression.html) 是当今用于压缩 HTTP 数据的两种最常见的算法。

#### Gzip

Gzip 压缩格式已存在近 30 年，是一种基于 [Deflate 算法](https://www.youtube.com/watch?v=whGwm0Lky2s&t=851s) 的无损算法。Deflate 算法本身使用 [LZ77 算法](https://cs.stanford.edu/people/eroberts/courses/soco/projects/data-compression/lossless/lz77/algorithm.htm) 和 [Huffman 编码](https://cs.stanford.edu/people/eroberts/courses/soco/projects/data-compression/lossless/huffman/algorithm.htm) 对输入数据流中的数据块进行处理。

LZ77 算法识别重复的字符串，并用一个指向它之前出现位置的指针，后跟字符串的长度来替换它们。随后，Huffman 编码识别常用的引用，并用较短的位序列来替换它们。较长的位序列用于表示不常用的引用。

所有主要浏览器都支持 Gzip。[Zopfli](https://github.com/google/zopfli) 压缩算法是 Deflate/Gzip 的一个较慢但改进的版本，生成更小的 GZip 兼容文件。它最适合静态压缩，可以提供更大的收益。

#### Brotli

2015 年，Google 推出了 [Brotli 算法](https://opensource.googleblog.com/2015/09/introducing-brotli-new-compression.html) 和 [Brotli 压缩数据格式](https://datatracker.ietf.org/doc/html/rfc7932)。与 GZip 类似，[Brotli](https://github.com/google/brotli) 也是一个基于 LZ77 算法和 Huffman 编码的无损算法。此外，它使用 2nd order context modeling 来在相似速度下获得更密集的压缩。上下文建模是一个允许在同一块中对同一字母表使用多个 Huffman 树的功能。Brotli 还支持 [更大的窗口大小](https://blog.cloudflare.com/results-experimenting-brotli/) 用于回溯，并具有一个静态字典。这些功能有助于提高其作为压缩算法的效率。

Brotli 目前被所有主要服务器和浏览器支持，并且正变得越来越 [流行](https://almanac.httparchive.org/en/2020/compression#fig-5)。它也得到了托管提供商和中间件（包括 [Netlify](https://www.netlify.com/blog/2020/05/20/gain-instant-performance-boosts-as-brotli-comes-to-netlify-edge/)、[AWS](https://aws.amazon.com/about-aws/whats-new/2020/09/cloudfront-brotli-compression/) 和 [Vercel](https://vercel.com/docs/concepts/edge-network/compression)）的支持，并且可以轻松启用。

像 [OYO](https://tech.oyorooms.com/how-brotli-compression-gave-us-37-latency-improvement-14d41e50fee4) 和 [Wix](https://web.dev/wix/#brotli-compression-(vs.-gzip)) 这样拥有大量用户的网站在用 Brotli 替代 Gzip 后，性能得到了显著提升。

#### Gzip 和 Brotli 的比较

Chrome 研究人员关于使用 Gzip 和 Brotli 压缩 JS 的压缩的一些见解如下：

- Gzip 9 具有最佳的压缩率，压缩速度良好，你应该在 Gzip 的其他级别之前考虑使用它。
- 对于 Brotli，考虑级别 6-11。否则，我们可以用 Gzip 在更快的速度下实现相似的压缩率。
- 在所有大小范围内，Brotli 9-11 的性能都比 Gzip 好，但它相当慢。
- 包越大，你将获得越好的压缩率和速度。
- 算法之间的关系对于所有包大小都相似（例如，Brotli 7 比所有包大小的 Gzip 9 好，Gzip 9 比所有大小范围的 Brotli 5 快）。

### 启用压缩

你可以将静态压缩作为构建的一部分启用。如果你使用 Webpack 打包代码，可以使用 [CompressionPlugin](https://github.com/webpack-contrib/compression-webpack-plugin) 进行 Gzip 压缩，或使用 [BrotliWebpackPlugin](https://github.com/mynameiswhm/brotli-webpack-plugin) 进行 Brotli 压缩。插件可以按以下方式包含在 Webpack 配置文件中。

```js
module.exports = {
  //...
  plugins: [
    //...
    new CompressionPlugin(),
  ],
};
```

Next.js 默认提供 [Gzip 压缩](https://nextjs.org/docs/api-reference/next.config.js/compression)，但建议在 HTTP 代理（如 Nginx）上启用它。Gzip 和 Brotli 都在 [Vercel 平台](https://vercel.com/docs/concepts/edge-network/compression) 的代理级别得到支持。

你可以在支持不同压缩算法的服务器（包括 Node.js）上启用动态无损压缩。浏览器通过请求中的 [Accept-Encoding](https://developer.mozilla.org/docs/Web/HTTP/Headers/Accept-Encoding) HTTP 标头传达它支持的压缩算法。例如，`Accept-Encoding: gzip, br`。

这表示浏览器支持 Gzip 和 Brotli。你可以通过遵循特定服务器类型的说明来在服务器上启用不同类型的压缩。例如，你可以在 [Apache 服务器](https://httpd.apache.org/docs/2.4/mod/mod_brotli.html#enable) 上找到启用 Brotli 的说明。[Express](https://expressjs.com/) 是 Node 的一个流行 Web 框架，并提供了一个 [compression](https://github.com/expressjs/compression) 中间件库。使用它来压缩任何正在请求的资产。

Brotli 推荐用于其他压缩算法，因为它可以生成更小的文件大小。你可以将 Gzip 作为不支持 Brotli 的浏览器的回退选项。如果配置成功，服务器将返回 [Content-Encoding](https://developer.mozilla.org/docs/Web/HTTP/Headers/Content-Encoding) HTTP 响应标头，以指示响应中使用的压缩算法。例如，`Content-Encoding: br`。

### 压缩审计

你可以使用 Chrome DevTools → Network → Headers 检查服务器是否压缩了下载的脚本或文本。DevTools 显示响应中使用的 content-encoding。

Lighthouse 报告包括一个“启用文本压缩”的性能审计，该审计检查接收到的基于文本的资源类型是否没有将 content-encoding 标头设置为 'br'、'gzip' 或 'deflate'。Lighthouse 使用 Gzip 来计算资源的潜在节省。

### JavaScript 压缩和加载粒度

要完全理解 JavaScript 压缩的效果，你也必须考虑 JavaScript 优化的其他方面，例如 [基于路由的拆分](https://www.patterns.dev/posts/route-based/)、[代码拆分](https://webpack.js.org/guides/code-splitting/) 和 [打包](https://www.patterns.dev/posts/bundle-splitting/)。

现代具有大量 JavaScript 代码的 Web 应用程序通常使用不同的代码拆分和打包技术来高效地加载代码。应用程序使用逻辑边界来拆分代码，例如单页应用程序的路由级拆分或交互式或视口可见性时逐步加载 JavaScript。你可以配置打包器来识别这些边界。

#### 打包术语

以下是与我们的讨论相关的几个关键术语。

1. **模块**：模块是提供良好抽象和封装的离散功能块。有关更多详细信息，请参阅 [模块模式](https://www.patterns.dev/posts/module-pattern/)。
2. **包**：包含最终版本源文件并已通过打包器加载和编译的独立模块组。
3. **包拆分**：打包器利用的过程，将应用程序拆分为多个包，以便每个包都可以独立隔离、发布、下载或缓存。
4. **块**：从 Webpack 术语继承而来，块是打包和代码拆分过程的最终输出。Webpack 可以根据 [入口](https://webpack.js.org/configuration/entry-context/) 配置、[SplitChunksPlugin](https://webpack.js.org/plugins/split-chunks-plugin/) 或 [动态导入](https://webpack.js.org/plugins/split-chunks-plugin/) 将包拆分为块。

如果模块包含在源文件中，那么构建过程在代码或包拆分后的最终输出称为一个 **块**。请注意，源文件和块可能相互依赖。

JavaScript 的输出大小是指 JavaScript 打包器或编译器优化后的块的大小或原始大小。大型 JS 应用程序可以分解为多个可以独立加载的 JavaScript 文件块。**加载粒度** 指的是输出块的数量——块的数量越多，每个块的大小越小，粒度越高。

有些代码块比其他代码块更关键，因为它们被加载得更频繁，或者它们是更重要的代码路径的一部分（例如，加载“结账”小部件）。了解哪些代码块最重要需要应用程序知识，但可以安全地假设“基础”代码块始终是必不可少的。

页面所需的每个代码块的字节都需要由用户设备下载并解析/执行。这是直接影响应用程序性能的代码。[直接影响到](https://v8.dev/blog/cost-of-javascript-2019)应用程序性能。由于代码块是最终要下载的代码，因此压缩代码块可以带来更好的下载速度。

#### 粒度权衡

在理想的世界里，粒度和代码块策略应该旨在实现以下目标，这些目标相互矛盾。

1. **提高下载速度**：如前一节所见，可以使用压缩来提高下载速度。然而，压缩一个大的代码块会比压缩具有相同代码的多个小代码块产生更好的结果或更小的文件大小。

`compress(a + b) <= compress(a) + compress(b)`

2. **提高缓存命中率和缓存效率**：较小的代码块大小可以带来更好的缓存效率，特别是对于逐步加载 JS 的应用程序。

- 变更被隔离到较少的代码块中，并且代码块较小。如果代码发生变化，只需重新下载受影响的代码块，并且这些代码块的大小可能较小。因此，其余的代码块可以在缓存中找到，从而增加缓存命中的次数。
- 对于较大的代码块，很可能大量代码受到影响，并且在代码更改后需要重新下载。

因此，较小的代码块是利用缓存机制的理想选择。

3. **快速执行**——为了使代码能够快速执行，它应该满足以下条件。

- 所有必需的依赖项都立即可用——它们已经一起下载或可在缓存中找到。这意味着您应该将所有相关的代码捆绑在一起作为一个较大的代码块。
- 只有页面/路由所需的代码应该执行。这需要确保没有额外的代码被下载或执行。包含常见依赖项的 `commons` 代码块可能包含大多数页面所需的依赖项，但并非所有页面。代码的重复需要较小的独立代码块。
- 主线程上的长任务可能会长时间阻塞它。因此，这些任务需要被拆分成较小的代码块。

试图优化上述目标之一的加载粒度可能会让您远离其他目标。这就是粒度权衡的问题。

**代码重复和缓存与浏览器性能和压缩相互矛盾。**

由于这种权衡，今天大多数生产应用程序使用的代码块数量最多约为 10 个。这个限制需要增加，以支持大量 JavaScript 的应用程序更好的缓存和代码重复。

### `SplitChunksPlugin` 和粒度代码块

一种解决粒度权衡的潜在解决方案将解决以下要求。

1. 允许使用更多的小代码块（40 到 100 个），代码块大小更小，以实现更好的缓存和代码重复，而不会影响性能。
2. 解决由于 IPC、I/O 和许多脚本标签的处理成本而导致的多个较小代码块的性能开销。
3. 解决多个较小代码块的情况下的压缩损失。

一种解决这些要求的潜在解决方案仍在开发中。然而，Webpack v4 的 [SplitChunksPlugin](https://webpack.js.org/plugins/split-chunks-plugin/) 和粒度代码块策略可以在一定程度上帮助增加加载粒度。

Webpack 的早期版本使用 `CommonsChunkPlugin` 将常见依赖项或共享模块捆绑成一个代码块。这可能导致未使用这些常见模块的页面下载和执行时间不必要地增加。为了允许对这些页面进行更好的优化，Webpack 在 v4 中引入了 `SplitChunksPlugin`。基于默认值或配置创建多个拆分代码块，以防止在各个路由中获取重复的代码。

Next.js 采用了 SplitChunksPlugin，并实施了以下 [粒度代码块](https://web.dev/granular-chunking-nextjs/) 策略来生成 Webpack 代码块，以解决粒度权衡问题。

- 任何足够大的第三方模块（大于 160 KB）都将被拆分成一个单独的代码块。
- 为框架依赖项创建一个单独的框架代码块。（react、react-dom 等等）
- 创建所需数量的共享代码块。（最多 25 个）
- 生成的代码块的最小大小更改为 20 KB。

而不是一个共享代码块发出多个共享代码块，可以最大限度地减少在不同页面上下载或执行的必要（或重复）代码量。为大型第三方库生成独立的代码块可以提高缓存，因为它们不太可能频繁更改。20 kB 的最小代码块大小确保压缩损失合理低。

粒度代码块策略帮助几个 Next JS 应用程序减少了网站使用的总 JavaScript。粒度代码块策略也在 [Gatsby](https://github.com/gatsbyjs/gatsby/pull/22253) 中实施，并观察到类似的好处。

### 结论

压缩本身不能解决所有 JavaScript 性能问题，但了解浏览器和打包器在后台的工作原理可以帮助创建更好的捆绑策略，从而支持更好的压缩。加载粒度问题需要在生态系统中的不同平台上得到解决。粒度代码块可能是这一方向上的一步，但我们还有很长的路要走。

## 来源

- [patterns.dev/vanilla/compression](https://patterns.dev/vanilla/compression)
