# Netlify 图像 CDN

通过请求 `/.netlify/images` 并附带查询参数来转换图像。无需编写函数或文件——这是一个内置的边缘端点。

```bash
# 调整大小并裁剪为 50px 正方形，保留左侧，转换为 webp 格式，质量为 80
curl -vs 'https://mysitename.netlify.app/.netlify/images?url=/owl.jpeg&fit=cover&w=50&h=50&position=left&fm=webp&q=80'
```

没有遗留/已弃用的形式——上面的端点是唯一的程序化接口。在可用的情况下使用框架图像组件（如下所述），而不是手动构建 URL。

## 端点及查询参数

`GET /.netlify/images?url=<source>&...`

| 参数 | 值 | 备注 |
|---|---|---|
| `url` | 相对路径或完整远程 URL | **必需**。唯一必需参数。 |
| `w` | 整数 px | 宽度 |
| `h` | 整数 px | 高度 |
| `fit` | `contain`（默认）、`cover`、`fill` | 调整大小行为 |
| `position` | `center`（默认）、`top`、`bottom`、`left`、`right` | 仅当 `fit=cover` 时适用 |
| `fm` | `avif`、`jpg`、`png`、`webp`、`gif`、`blurhash` | 输出格式；`webp`/`gif` 可以为动画 |
| `q` | 整数 `1`–`100`（默认 `75`） | 仅适用于 `avif`、`jpg`、`gif`、`webp` |

### `fit` 行为

| `fit=` | 保持宽高比 | 裁剪多余部分 | 返回精确尺寸 |
|---|---|---|---|
| `contain` | 是 | 否 | 否——一个维度可能更小 |
| `cover` | 否 | 是 | 是——按比例缩放，然后裁剪 |
| `fill` | 否 | 否 | 是——如果需要，会拉伸/挤压 |

- **`fit=cover` 需要 `w` 和 `h` 都提供。** 仅提供其中一个会静默地表现异常。
- `contain` 与一个维度一起使用时，会计算另一个维度以保持宽高比。

### 格式及内容协商

- 仅源请求（仅 `url`，无大小/格式）：图像在尺寸/形状上保持不变，但**仍然会重新格式化**为 `avif`/`webp`，基于浏览器的 `Accept` 头。
- 未指定 `fm` → 如果接受 `webp`，则使用 `webp`；否则如果接受 `avif`，则使用 `avif`；否则使用原始格式。
- `fm=blurhash` 返回一个 BlurHash **文本字符串，而不是图像字节。** 将 `<img src>` 或 CSS 背景指向它将渲染为空。在服务器端/提前获取该字符串，使用 BlurHash 库（https://blurha.sh）在客户端解码，然后作为单独的请求加载真实图像，不使用 `fm=blurhash`。

### 响应代码

- 无效的转换参数值 → `404`。
- 有效的新转换 → `200`，附带内容 + `content-type`。
- 之前已转换 → `304`。

## 远程源图像

远程 `url` 值需要在 `netlify.toml` 中允许列出域名：

```toml
[images]
  remote_images = ["https://my-images.com/.*", "https://animals.more-images.com/[bcr]at/.*"]
```

然后对远程 URL 进行百分比编码并请求它：

```js
const src = `/.netlify/images?url=${encodeURIComponent("https://my-images.com/owl.jpeg")}`;
```

- **始终对远程 URL 使用 `encodeURIComponent`**，然后将其放入 `url` 中——包含 `?` 或 `&` 的 URL 会失效。
- 在 `remote_images` 模式中，**仅转义点号**：`'https://example\.com/.*'`。斜杠不是正则表达式元字符——不要写 `https:\/\/`。
- 远程源必须**公开可访问**。Netlify 不会转发 `Authorization` 或 `Cookie` 头到远程源。对于需要授权的图像，请使用自授权 URL（例如 S3 签名 URL），并确保您的 `remote_images` 模式与它们匹配。

## 可重用转换（重定向）

通过重定向跨多个图像重用相同参数：

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

然后 `GET /transform-small/owl.jpeg` 生成一个 50×50 的转换。**避免跨站重定向用于转换**——它们会降低性能。

## 自定义头（缓存）

`_headers`:
```
/source-images/*
  Cache-Control: public, max-age=604800, must-revalidate
```

- 源图像上设置的头部会应用于 Image CDN 服务的转换后的资产。
- 自定义头**不能**应用于远程（其他域）源图像；Netlify 尊重外部域发送的缓存头。
- 源图像上的 `Cache-Control` 仅适用于 Netlify 前面的浏览器/CDN，**不**适用于 Netlify 缓存本身。

## 框架集成

使用框架的原生图像组件/处理；它会自动连接到 Image CDN。按框架配置远程允许列表：

| 框架 | 前置条件 | 远程允许列表 |
|---|---|---|
| Angular | 无——`NgOptimizedImage` 自动使用它 | `[images] remote_images` 在 `netlify.toml` 中 |
| Astro | 无——`<Image />` 自动使用它 | `image.domains` / `image.remotePatterns` 在 `astro.config.mjs` 中 |
| Nuxt | 无——`nuxt/image` 自动使用它 | `image.domains` 在 `nuxt.config.ts` 中 |
| Next.js | Next 13.5+ 和适配器 v5 | `remotePatterns` 在 `next.config.js` 中 |
| Gatsby | 环境变量 `NETLIFY_IMAGE_CDN=true` + Contentful/Drupal/WordPress 源插件 | `[images] remote_images` 在 `netlify.toml` 中 |

## 本地开发

运行 `netlify dev`（Netlify CLI）在本地测试转换——它会模拟生产环境，包括 Image CDN。

- **本地 `/.netlify/images` 的 404 几乎总是意味着框架开发服务器（`vite`、`next dev`、`astro dev`）正在运行而不是 `netlify dev`。** 端点、`[images]` 允许列表和图像重定向仅在 `netlify dev` 下存在。URL 本身通常没问题。

## 缓存与部署

转换后的结果在 Netlify 的边缘独特缓存。原子部署受到尊重：在新部署中更改源图像会在新请求上重新运行转换，以避免提供过时的资产。

## 用户上传图像管道

对于用户上传图像管道（函数 + Blob + Image CDN 组合），请参阅本技能中的 `references/user-uploads.md`。

## 限制

- **不支持 A/B 测试**——您可能会在 A/B 测试分支之间获得不一致的图像结果。
- 目前不支持在 Netlify 的 HIPAA 合规托管服务中。请参阅信任中心了解 HIPAA 合规参考架构。

<!-- system: agent-context/image-cdn/system.md — human-owned, merged by ctx-gen; edit system.md, not this section -->
# Netlify 图像规则（图像 CDN）

这些是组织约定，不是文档事实——由 ctx-gen 合并到渲染的技能中，并且永远不会生成。由技能维护者拥有。

1. 对于用户上传图像管道（函数 + Blob + Image CDN 组合），请参阅本技能中的 `references/user-uploads.md`——一个无单一文档源的编写指南。
2. 在将远程源 URL 放入 `url` 参数之前进行百分比编码（`encodeURIComponent`）——包含 `?` 或 `&` 的 URL 会失效。
3. `fm=blurhash` 返回一个 BlurHash 文本字符串，而不是图像字节。将 `<img src>`（或 CSS 背景指向它）会渲染为空——提前获取字符串，使用 BlurHash 库在客户端解码，然后作为单独的请求加载真实图像，不使用 `fm=blurhash`。
4. 本地 `/.netlify/images` 的 404 几乎总是意味着框架开发服务器（`vite`、`next dev`、`astro dev`）正在运行而不是 `netlify dev`——端点、`[images]` 允许列表和图像重定向仅在 `netlify dev` 下存在。URL 本身通常没问题。
5. 在 `remote_images` 模式中，有意义的正则表达式转义是点；斜杠不是元字符——不要写 `https:\/\/`。在 `netlify.toml` 中，使用单引号字面量字符串（`'https://example\.com/.*'`）或在双引号字符串中加倍反斜杠（`"https://example\\.com/.*"`）——双引号内的裸 `\.` 无效。
