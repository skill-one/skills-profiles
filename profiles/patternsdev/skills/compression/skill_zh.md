# 压缩 JavaScript

## 目录

- [何时使用](#何时使用)
- [说明](#说明)
- [详情](#详情)
- [来源](#来源)

JavaScript 是第二大 [页面大小贡献者](https://almanac.httparchive.org/en/2020/page-weight#fig-2) 和互联网上第二大 [请求的网页资源](https://almanac.httparchive.org/en/2020/page-weight#fig-4)（仅次于图片）。我们使用减少 JavaScript 传输、加载和执行时间的模式来提高网站性能。压缩可以帮助减少在网络传输脚本所需的时间。

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

你可以将压缩与其他技术（如最小化、代码拆分、打包、缓存和懒加载）结合使用，以减少大量 JavaScript 的性能影响。然而，这些技术的目标有时会相互冲突。本节探讨了 JavaScript 压缩技术，并讨论了你在决定代码拆分和压缩策略时应考虑的细节。

- **Gzip** 和 **Brotli** 是压缩 JavaScript 最常见的方法，并且被现代浏览器广泛支持。
- **Brotli** 在相似压缩级别下提供 **更好的压缩率**。
- **Next.js** 默认提供 [Gzip 压缩](https://nextjs.org/docs/api-reference/next.config.js/compression)，但建议在 HTTP 代理（如 Nginx）上启用它。
- 如果你使用 **Webpack** 打包代码，可以使用 **[CompressionPlugin](https://github.com/webpack-contrib/compression-webpack-plugin)** 进行 Gzip 压缩，或使用 [BrotliWebpackPlugin](https://github.com/mynameiswhm/brotli-webpack-plugin) 进行 Brotli 压缩。
- Oyo 在切换到 **Brotli 压缩而不是 Gzip** 后，文件大小减少了 **15-20%**，Wix 减少了 **21-25%**。
- **compress(a + b) <= compress(a) + compress(b)** - 一个大的单一包将比多个小包提供更好的压缩效果。这导致了粒度权衡，其中去重和缓存与浏览器性能和压缩相冲突。粒度块拆分可以帮助处理这种权衡。

### HTTP 压缩

压缩可以减小文档和文件的大小，因此它们占用的磁盘空间比原始文件小。较小的文档消耗更低的带宽，并且可以快速地在网络上传输。HTTP 压缩利用这个简单的概念来压缩网站内容，减少 [页面权重](https://almanac.httparchive.org/en/2020/page-weight)，降低带宽需求，并提高性能。

HTTP 数据压缩可以按不同的方式分类。其中一种分类是损失性压缩与无损性压缩。

**损失性压缩** 意味着压缩-解压缩周期会导致文档略有变化，但仍然保持其可用性。这种变化对最终用户来说几乎是 imperceptible。最常见的损失性压缩示例是用于图像的 JPEG 压缩。

使用 **无损性压缩**，压缩和后续解压缩后恢复的数据将与原始数据完全匹配。PNG 图像是无损压缩的示例。无损压缩与文本传输相关，应应用于文本格式，如 HTML、CSS 和 JavaScript。

由于你希望在浏览器上获得所有有效的 JS 代码，因此你应该使用无损压缩算法来压缩 JavaScript 代码。在压缩 JS 之前，最小化有助于消除不必要的语法，并将其减少到仅包含执行所需的代码。

### 最小化

为了减小负载大小，你可以在压缩之前最小化 JavaScript。[最小化](https://web.dev/reduce-network-payloads-using-text-compression/#minification) 通过删除空格和任何不必要的代码来补充压缩，以创建一个更小但完全有效的代码文件。在编写代码时，我们使用换行符、缩进、空格、命名良好的变量和注释来提高代码的可读性和可维护性。然而，这些元素会增加 JavaScript 的总体大小，并且不是在浏览器上执行所必需的。最小化将 JavaScript 代码减少到成功执行所需的最低代码。

最小化是 JS 和 CSS 优化的标准做法。通常，JavaScript 库开发人员会为生产部署提供最小化的文件版本，通常以 min.js 扩展名表示。（例如，`jquery.js` 和 `jquery.min.js`）

有多种工具可用于 [最小化 HTML、CSS 和 JS](https://developers.google.com/speed/docs/insights/MinifyResources) 资源。[Terser](https://github.com/terser-js/terser) 是一个流行的 JavaScript 压缩工具，用于 ES6+，[Webpack](https://webpack.js.org/) v4 默认包含此库的插件来创建最小化的构建文件。你也可以使用 `TerserWebpackPlugin` 与较旧版本的 Webpack 或不使用模块打包器作为 CLI 工具使用。

### 静态与动态压缩

最小化可以显著减小文件大小，但 JS 的压缩可以提供更大的收益。你可以以两种方式实现服务器端压缩。

**静态压缩**：你可以使用静态压缩来预先压缩资源，并在构建过程之前将其保存为构建过程的一部分。在这种情况下，你可以使用更高的压缩级别，以改善代码的下载时间。高构建时间不会影响网站性能。你应该使用静态压缩来处理不经常变化的文件。

**动态压缩**：通过此过程，压缩在浏览器请求资源时动态进行。动态压缩更容易实现，但你只能使用较低的压缩级别。较高的压缩级别需要更多时间，并且你会失去从较小的内容大小中获得的收益。你应该使用动态压缩来处理经常变化的或应用生成的内容。

你可以根据应用内容类型使用静态或动态压缩。你可以使用流行的压缩算法启用静态和动态压缩，但每种情况下的推荐压缩级别都不同。

### 压缩算法

[Gzip](https://datatracker.ietf.org/doc/html/rfc1952) 和 [Brotli](https://opensource.googleblog.com/2015/09/introducing-brotli-new-compression.html) 是当今用于压缩 HTTP 数据的两种 [最常见算法](https://almanac.httparchive.org/en/2020/compression#fig-5)。

#### Gzip

Gzip 压缩格式已存在近 30 年，是一种基于 [Deflate 算法](https://www.youtube.com/watch?v=whGwm0Lky2s&t=851s) 的无损算法。Deflate 算法本身使用 [LZ77 算法](https://cs.stanford.edu/people/eroberts/courses/soco/projects/data-compression/lossless/lz77/algorithm.htm) 和 [Huffman 编码](https://cs.stanford.edu/people/eroberts/courses/soco/projects/data-compression/lossless/huffman/algorithm.htm) 对输入数据流中的数据块进行组合。

LZ77 算法识别重复的字符串，并用一个指向它之前出现位置的指针，后跟字符串的长度来替换它们。随后，Huffman 编码识别常用的引用，并用较短的位序列来替换它们。较长的位序列用于表示不常用的引用。

所有主要浏览器都支持 Gzip。[Zopfli](https://github.com/google/zopfli) 压缩算法是 Deflate/Gzip 的一个较慢但改进的版本，生成较小的 GZip 兼容文件。它最适合静态压缩，可以提供更大的收益。

#### Brotli

2015 年，Google 推出了 [Brotli 算法](https://opensource.googleblog.com/2015/09/introducing-brotli-new-compression.html) 和 [Brotli 压缩数据格式](https://datatracker.ietf.org/doc/html/rfc7932)。与 GZip 类似，[Brotli](https://github.com/google/brotli) 也是一个基于 LZ77 算法和 Huffman 编码的无损算法。此外，它使用 2nd order context modeling 来在相似速度下获得更密集的压缩。上下文建模是一个功能，它允许在同一个块中对同一字母使用多个 Huffman 树。Brotli 还支持 [更大的窗口大小](https://blog.cloudflare.com/results-experimenting-brotli/) 用于回溯引用，并具有一个静态字典。这些功能有助于提高其作为压缩算法的效率。

Brotli 目前被所有主要服务器和浏览器支持，并且正变得越来越 [流行](https://almanac.httparchive.org/en/2020/compression#fig-5)。它也得到了托管提供商和中间件（包括 [Netlify](https://www.netlify.com/blog/2020/05/20/gain-instant-performance-boosts-as-brotli-comes-to-netlify-edge/)、[AWS](https://aws.amazon.com/about-aws/whats-new/2020/09/cloudfront-brotli-compression/) 和 [Vercel](https://vercel.com/docs/concepts/edge-network/compression)) 的支持和轻松启用。

像 [OYO](https://tech.oyorooms.com/how-brotli-compression-gave-us-37-latency-improvement-14d41e50fee4) 和 [Wix](https://web.dev/wix/#brotli-compression-(vs.-gzip)) 这样拥有大量用户的网站在用 Brotli 替换 Gzip 后，性能得到了显著改善。

#### Gzip 和 Brotli 的比较

以下是 Chrome 研究人员关于使用 Gzip 和 Brotli 压缩 JS 的几个见解：

- Gzip 9 具有最佳的压缩率，压缩速度良好，你应该在 Gzip 的其他级别之前考虑使用它。
- 使用 Brotli 时，考虑级别 6-11。否则，我们可以更快地使用 Gzip 实现相似的压缩率。
- 在所有大小范围内，Brotli 9-11 的性能都比 Gzip 好得多，但它相当慢。
- 包越大，你将获得越好的压缩率和速度。
- 算法之间的关系对于所有包大小都是相似的（例如，对于每个包大小，Brotli 7 都比 Gzip 9 好，Gzip 9 比 Brotli 5 快）。

### 启用压缩

你可以作为构建过程的一部分启用静态压缩。如果你使用 Webpack 打包代码，可以使用 [CompressionPlugin](https://github.com/webpack-contrib/compression-webpack-plugin) 进行 Gzip 压缩，或使用 [BrotliWebpackPlugin](https://github.com/mynameiswhm/brotli-webpack-plugin) 进行 Brotli 压缩。插件可以按以下方式包含在 Webpack 配置文件中。

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

你可以在支持不同压缩算法的服务器（包括 Node.js）上启用动态无损压缩。浏览器通过请求中的 [Accept-Encoding](https://developer.mozilla.org/docs/Web/HTTP/Headers/Accept-Encoding) HTTP 头传递它支持的压缩算法。例如，`Accept-Encoding: gzip, br`。

这表示浏览器支持 Gzip 和 Brotli。你可以通过遵循特定服务器类型的说明来在你的服务器上启用不同类型的压缩。例如，你可以在 [Apache 服务器](https://httpd.apache.org/docs/2.4/mod/mod_brotli.html#enable) 上找到启用 Brotli 的说明。[Express](https://expressjs.com/) 是 Node 的一个流行 Web 框架，提供了一个 [compression](https://github.com/expressjs/compression) 中间件库。使用它来压缩任何被请求的资产。

Brotli 推荐于其他压缩算法，因为它生成的文件大小更小。你可以启用 Gzip 作为不支持 Brotli 的浏览器的回退。如果配置成功，服务器将返回 [Content-Encoding](https://developer.mozilla.org/docs/Web/HTTP/Headers/Content-Encoding) HTTP 响应头，以指示响应中使用的压缩算法。例如，`Content-Encoding: br`。

### 审计压缩

你可以检查服务器是否压缩了下载的脚本或文本，方法是使用 Chrome DevTools → Network → Headers。DevTools 显示响应中使用的 content-encoding。

Lighthouse 报告包括一个“启用文本压缩”的性能审计，该审计检查未设置 content-encoding 头为 'br'、'gzip' 或 'deflate' 的基于文本的资源类型。Lighthouse 使用 Gzip 来计算资源的潜在节省。

### JavaScript 压缩和加载粒度

要完全理解 JavaScript 压缩的效果，你也必须考虑 JavaScript 优化的其他方面，例如 [基于路由的拆分](https://www.patterns.dev/posts/route-based/)、[代码拆分](https://webpack.js.org/guides/code-splitting/) 和 [打包](https://www.patterns.dev/posts/bundle-splitting/)。

现代具有大量 JavaScript 代码的 Web 应用程序通常使用不同的代码拆分和打包技术来高效地加载代码。应用程序使用逻辑边界来拆分代码，例如单页应用程序的路由级拆分，或在交互或视口可见性时逐步加载 JavaScript。你可以配置打包器来识别这些边界。

#### 打包术语

以下是与我们讨论相关的几个关键术语。

1. **模块**：模块是提供良好抽象和封装的独立功能块。有关更多详细信息，请参阅 [模块模式](https://www.patterns.dev/posts/module-pattern/)。
2. **包**：包是一组包含最终版本源文件并已通过打包器加载和编译的独立模块。
3. **包拆分**：打包器利用的过程，将应用程序拆分为多个包，以便每个包都可以独立隔离、发布、下载或缓存。
4. **块**：从 Webpack 术语继承而来，块是打包和代码拆分过程的最终输出。Webpack 可以根据 [入口](https://webpack.js.org/configuration/entry-context/) 配置、[SplitChunksPlugin](https://webpack.js.org/plugins/split-chunks-plugin/) 或 [动态导入](https://webpack.js.org/plugins/split-chunks-plugin/) 将包拆分为块。

如果模块包含在源文件中，那么构建过程完成后的最终输出称为 **块**。请注意，源文件和块可能相互依赖。

JavaScript 的输出大小是指块的大小或经过 JavaScript 打包器或编译器优化后的原始大小。大型 JS 应用程序可以分解为多个可以独立加载的 JavaScript 文件块。**加载粒度** 指的是输出块的数量——块的数量越多，每个块的大小越小，粒度越高。

一些块比其他块更重要，因为它们加载得更频繁，或者它们是更有影响力的代码路径的一部分（例如，加载“结账”小部件）。了解哪些块最重要需要应用知识，但可以安全地假设“基础”块始终是必不可少的。

页面所需的每个块的字节都需要由用户设备下载和解析/执行。这是直接影响应用性能的代码。由于块是最终要下载的代码，因此压缩块可以带来更好的下载速度。

#### 粒度权衡

在理想的世界里，粒度和块拆分策略应该旨在实现以下目标，这些目标相互冲突。

1. **提高下载速度**：如前所述，可以使用压缩来提高下载速度。然而，压缩一个大的块将比压缩具有相同代码的多个小块产生更好的结果或更小的文件大小。

`compress(a + b) <= compress(a) + compress(b)`

2. **提高缓存命中和缓存效率**：较小的块大小会导致更好的缓存效率，特别是对于逐步加载 JS 的应用程序。

- 变更隔离到较少的块和较小的块。如果代码发生变化，只有受影响的块需要重新下载，这些块对应的代码大小可能较小。其余的块可以在缓存中找到，从而增加缓存命中次数。
- 对于较大的块，很可能有大量代码受影响，并且在代码变化后需要重新下载。

因此，较小的块是利用缓存机制的理想选择。

3. **快速执行** - 为了使代码快速执行，它应该满足以下条件。

- 所有必需的依赖项都立即可用——它们一起下载或可在缓存中找到。这意味着你应该将所有相关的代码捆绑在一起作为一个较大的块。
- 只有页面/路由需要的代码应该执行。这要求不要下载或执行任何额外的代码。一个包含公共依赖项的 `commons` 块可能包含大多数页面但不是所有页面所需的依赖项。代码去重需要较小的独立块。
- 主线程上的长任务可能会长时间阻塞它。因此，这些任务需要拆分为较小的块。

尝试优化上述其中一个目标的加载粒度可能会让你远离其他目标。这是粒度权衡的问题。

**去重和缓存与浏览器性能和压缩相冲突。**

由于这种权衡，今天大多数生产应用程序使用的最大块数约为 10。这个限制需要增加，以支持具有大量 JavaScript 的应用程序更好的缓存和去重。

### `SplitChunksPlugin` 和粒度块拆分

一个潜在的解决方案可以解决粒度权衡的要求。

1. 允许使用 40 到 100 个较大的块，块大小较小，以实现更好的缓存和去重，而不会影响性能。
2. 解决由于多个较小块导致的 IPC、I/O 和处理成本等性能开销。
3. 解决多个较小块的情况下的压缩损失。

一个潜在的解决方案仍在开发中。然而，Webpack v4 的 [SplitChunksPlugin](https://webpack.js.org/plugins/split-chunks-plugin/) 和粒度块拆分策略可以在一定程度上提高加载粒度。

早期版本的 Webpack 使用 `CommonsChunkPlugin` 将公共依赖项或共享模块捆绑到一个块中。这可能导致未使用这些公共模块的页面下载和执行时间不必要地增加。为了允许为这些页面进行更好的优化，Webpack 在 v4 中引入了 `SplitChunksPlugin`。基于默认值或配置创建多个拆分块，以防止在各个路由中获取重复的代码。

Next.js 采用了 SplitChunksPlugin 并实施了以下 [粒度块拆分](https://web.dev/granular-chunking-nextjs/) 策略来生成 Webpack 块，以解决粒度权衡。

- 任何足够大的第三方模块（大于 160 KB）都将被拆分为一个独立的块。
- 为框架依赖项创建一个单独的框架块。（react、react-dom 等）
- 创建尽可能多的共享块。（最多 25 个）
- 生成的块的最小大小更改为 20 KB。

而不是生成一个共享块，发出多个共享块可以最大限度地减少在不同页面上下载或执行的不必要（或重复）代码的数量。为大型第三方库生成独立块可以提高缓存，因为它们不太可能经常变化。20 kB 的最小块大小可以确保压缩损失合理低。

粒度块拆分策略帮助多个 Next JS 应用程序减少了网站使用的总 JavaScript。粒度块拆分策略也在 [Gatsby](https://github.com/gatsbyjs/gatsby/pull/22253) 中得到实施，并观察到类似的好处。

### 结论

压缩本身不能解决所有 JavaScript 性能问题，但了解浏览器和打包器在后台如何工作可以帮助创建更好的打包策略，以支持更好的压缩。加载粒度问题需要在生态系统中的不同平台上得到解决。粒度块拆分可能是这一方向上的一步，但我们还有很长的路要走。

## 来源

- [patterns.dev/vanilla/compression](https://patterns.dev/vanilla/compression)
