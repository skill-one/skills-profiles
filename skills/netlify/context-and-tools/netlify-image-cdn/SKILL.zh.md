---
name: netlify-image-cdn
description: 通过 Netlify Image CDN 的 /.netlify/images 端点按需转换图像，并使用查询参数进行缩放/裁剪/格式/质量调整。适用于添加图像优化或响应式图像、转换格式（WebP/AVIF/PNG）、生成缩略图或模糊占位符、通过 CDN 提供远程/第三方图像、在 netlify.toml 中允许远程域名、设置图像重定向或缓存头、构建用户上传图像流程，或调试 /.netlify/images 上的 404 错误。同时涵盖 Angular/Astro/Gatsby/Next.js/Nuxt 等框架的图像处理。
---

# Netlify 图像 CDN

通过请求端点并使用 `url` 查询参数来转换图像。这是当前唯一文档化的接口——没有遗留形式。

```
GET /.netlify/images?url=<source>[&w=][&h=][&fit=][&position=][&fm=][&q=]
```

```bash
# 将部署的图像调整为 50 像素宽
curl -vs 'https://mysitename.netlify.app/.netlify/images?url=/owl.jpeg&w=50'
```

`url` 是必需的；所有其他参数都是可选的。

## 查询参数

| 参数 | 目的 | 值 | 默认值 |
|-----------|---------|--------|---------|
| `url` | 源资源（必需） | 相对路径或远程 URL | — |
| `w` | 像素宽度 | 整数 | — |
| `h` | 像素高度 | 整数 | — |
| `fit` | 调整行为 | `contain`, `cover`, `fill` | `contain` |
| `position` | 当 `fit=cover` 时裁剪锚点 | `top`, `bottom`, `left`, `right`, `center` | `center` |
| `fm` | 输出格式 | `avif`, `jpg`, `png`, `webp`, `gif`, `blurhash` | content-negotiated |
| `q` | 有损输出的质量 | 整数 `1`–`100` | `75` |

## 常见转换

```bash
# 调整大小 + 裁剪为 50 像素的正方形，保留左侧
curl -vs 'https://mysitename.netlify.app/.netlify/images?url=/owl.jpeg&fit=cover&w=50&h=50&position=left'

# 将 JPEG 转换为 PNG（响应包含 content-type: image/png）
curl -vs 'https://mysitename.netlify.app/.netlify/images?url=/owl.jpeg&fm=png'

# 将 JPEG 转换为 AVIF，中等质量
curl -vs 'https://mysitename.netlify.app/.netlify/images?url=/owl.jpeg&fm=avif&q=50'
```

### fit 行为

- **`contain`（默认）：** 保持宽高比；一个维度可能小于请求值。提供一个维度，另一个维度将自动计算。
- **`cover`：** 精确填充，裁剪多余部分。**必须同时提供 `w` 和 `h`**——省略任一都是无效的。使用 `position` 选择保留部分。
- **`fill`：** 精确填充，如果宽高比不同，会拉伸或挤压。

### 格式说明

- `q` 仅适用于输出为 `avif`, `jpg`, `gif`, 或 `webp` 时。
- `webp` 和 `gif` 可以是静态或动态的。
- 如果省略 `fm`，格式将根据 `Accept` 头进行内容协商：如果接受 `webp`，则使用 `webp`；否则如果接受 `avif`，则使用 `avif`；否则使用原始格式。仅源请求（无其他参数）仍会转换为 `webp`/`avif`，但会保持大小和形状。

## 远程源图像

远程源必须在 `netlify.toml` 中允许列表才能进行转换，否则请求将失败。

```toml
[images]
  remote_images = ['https://my-images\.com/.*', 'https://animals.more-images.com/[bcr]at/.*']
```

在将远程源 URL 放入 `url` 参数之前，使用 `encodeURIComponent` 对其进行百分比编码——包含 `?` 或 `&` 的 URL 会中断。

```js
const src = `/.netlify/images?url=${encodeURIComponent('https://my-images.com/owl.jpeg?v=2')}&w=400`;
```

约束：
- 远程源必须 **公开可访问**。
- 带凭证的头部（`Authorization`, `Cookie`）在获取远程源时**不会转发**。对于认证源，请使用携带其自身授权的 URL（例如 S3 签名 URL），并确保您的 `remote_images` 模式与这些完整 URL 匹配。

### remote_images 正则表达式转义

唯一有意义的转义是字面点（`\.`）。斜杠不是元字符——永远不要写 `https:\/\/`。在 `netlify.toml` 中，使用单引号字面字符串（`'https://example\.com/.*'`）或双引号字符串中加倍反斜杠（`"https://example\\.com/.*"`）。双引号内的裸 `\.` 是无效的 TOML。

## 响应代码

- 无效的转换参数值 → `404`。
- 有效的转换新转换 → `200`，包含内容并匹配 `content-type`。
- 之前转换（缓存）的图像 → `304`。

## 在图像间重用参数

使用重定向/重写将友好路径映射到端点。

`_redirects`:
```
/transform-small/* /.netlify/images?url=/:splat&w=50&h=50 200
```

`netlify.toml`:
```toml
[[redirects]]
  from = "/transform-small/*"
  to = "/.netlify/images?url=/:splat&w=50&h=50"
  status = 200
```

然后 `GET /transform-small/owl.jpeg` 返回转换后的图像。**不推荐跨站点重定向转换**——它们可能会降低网站性能。

## 缓存头部

将自定义头部应用于站点域上的源图像；它们会传递到转换后的输出。

`netlify.toml`:
```toml
[[headers]]
  for = "/source-images/*"
  [headers.values]
    Cache-Control = "public, max-age=604800, must-revalidate"
```

- 自定义头部只能应用于站点域上的源图像——**不能**应用于远程源图像（Netlify 会尊重外部域发送的缓存头部）。
- 源图像上的 `Cache-Control` 仅适用于浏览器和 Netlify 前面的 CDN，**不适用于 Netlify 缓存本身**。

## Blur 占位符（fm=blurhash）

`fm=blurhash` 返回一个 BlurHash **文本字符串**，而不是图像字节。将 `<img src>`（或 CSS 背景指向它）会渲染为空白。提前获取该字符串，使用 BlurHash 库（https://blurha.sh）在客户端解码，并作为单独请求加载真实图像，且不使用 `fm=blurhash`。

## 本地开发

`/.netlify/images` 端点、`[images]` 允许列表和图像重定向仅在 `netlify dev`（Netlify CLI）下存在。本地 **`/.netlify/images` 的 404 几乎总是意味着框架开发服务器（`vite`, `next dev`, `astro dev`）正在运行而不是 `netlify dev`**——URL 本身通常是正常的。使用 `netlify dev` 启动本地环境。

## 用户上传图像管道

对于由 Functions + Blobs + 图像 CDN 组成的用户上传图像管道，请参阅 `references/user-uploads.md`。

## 框架图像处理

许多框架通过 Netlify 图像 CDN 路由其内置图像优化——使用框架的标准图像组件/语法，并仅配置远程允许列表。对于未列出框架，直接调用 `/.netlify/images`。

| 框架 | 前提条件 | 远程允许列表位置 |
|-----------|---------------|---------------------------|
| Angular | 无；`NgOptimizedImage` 自动使用它 | `[images] remote_images` 在 `netlify.toml` 中 |
| Astro | 无；`<Image />` 自动使用它 | `image.domains` 或 `image.remotePatterns` 在 `astro.config.mjs` 中 |
| Gatsby（5.13+ 和 5.11 或更早） | 设置环境 `NETLIFY_IMAGE_CDN=true`；使用 Contentful/Drupal/WordPress 源插件 | `[images] remote_images` 在 `netlify.toml` 中 |
| Next.js | Next.js 13.5+ 和 Next.js 适配器 v5 | `remotePatterns` 在 `next.config.js` 中 |
| Nuxt | 无；`nuxt/image` 模块自动使用它 | `image.domains` 在 `nuxt.config.ts` 中 |

设置指南：[Angular](https://docs.netlify.com/build/frameworks/framework-setup-guides/angular#netlify-image-cdn), [Astro](https://docs.netlify.com/build/frameworks/framework-setup-guides/astro#netlify-image-cdn), [Gatsby](https://docs.netlify.com/build/frameworks/framework-setup-guides/gatsby/#netlify-image-cdn), [Next.js](https://docs.netlify.com/build/frameworks/framework-setup-guides/nextjs/overview), [Nuxt](https://docs.netlify.com/build/frameworks/framework-setup-guides/nuxt#netlify-image-cdn).

## 其他约束

- 部署行为：转换尊重 [原子部署](https://docs.netlify.com/build/caching/caching-overview#automatic-invalidation-with-atomic-deploys)；在新部署中更改源图像会重新运行后续请求的转换。
- [分割测试](https://docs.netlify.com/manage/monitoring/split-testing/) 不受支持——图像结果可能在分割测试分支之间不一致。
- Netlify 图像 CDN 不是 Netlify 的 HIPAA 合规托管服务的一部分。

交互式参数游乐场：https://image-cdn-playground.netlify.app/

<!-- system: agent-context/image-cdn/system.md — human-owned, merged by ctx-gen; edit system.md, not this section -->
# Netlify 图像规则（image-cdn）

这些是组织约定，不是文档事实——合并到渲染的技能中并由 ctx-gen 生成，永远不会生成。由技能维护者拥有。

1. 对于用户上传图像管道（Functions + Blobs + 图像 CDN 组成），请参阅此技能中的 `references/user-uploads.md`——一个有编写的指南，没有单一文档源。
2. 在将远程源 URL 放入 `url` 参数之前进行百分比编码（`encodeURIComponent`）——包含 `?` 或 `&` 的 URL 会中断。
3. `fm=blurhash` 返回一个 BlurHash 文本字符串，而不是图像字节。将 `<img src>`（或 CSS 背景指向它）会渲染为空白——提前获取该字符串，使用 BlurHash 库在客户端解码，并作为单独请求加载真实图像，且不使用 `fm=blurhash`。
4. 本地 `/.netlify/images` 的 404 几乎总是意味着框架开发服务器（`vite`, `next dev`, `astro dev`）正在运行而不是 `netlify dev`——端点、`[images]` 允许列表和图像重定向仅在 `netlify dev` 下存在。URL 本身通常是正常的。
5. 在 `remote_images` 模式中，有意义的正则表达式转义是点；斜杠不是元字符——不要写 `https:\/\/`。在 `netlify.toml` 中，使用单引号字面字符串（`'https://example\.com/.*'`）或双引号字符串中加倍反斜杠（`"https://example\\.com/.*"`）——双引号内的裸 `\.` 是无效的 TOML。
