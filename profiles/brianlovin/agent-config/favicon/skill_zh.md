从源图像 `$1` 生成一套完整的 favicons 并更新项目的 HTML 以包含适当的链接标签。

## 前置条件

首先，通过运行以下命令验证是否安装了 ImageMagick v7+：
```bash
which magick
```

如果没有找到，请停止并指导用户安装：
- **macOS**：`brew install imagemagick`
- **Linux**：`sudo apt install imagemagick`

## 第 1 步：验证源图像

1. 验证源图像是否存在于提供的路径 `$1`。
2. 检查文件扩展名是否为支持的格式（PNG、JPG、JPEG、SVG、WEBP、GIF）。
3. 如果文件不存在或不是有效的图像格式，报告错误并停止。

注意源文件是否为 SVG 文件 - 如果是，它也将被复制为 `favicon.svg`。

## 第 2 步：检测项目类型和静态资源目录

检测项目类型并确定静态资源应放置的位置。按以下顺序检查：

| 框架 | 检测方式 | 静态资源目录 |
|-----------|-----------|------------------------|
| **Rails** | `config/routes.rb` 存在 | `public/` |
| **Next.js** | `next.config.*` 存在 | `public/` |
| **Gatsby** | `gatsby-config.*` 存在 | `static/` |
| **SvelteKit** | `svelte.config.*` 存在 | `static/` |
| **Astro** | `astro.config.*` 存在 | `public/` |
| **Hugo** | `hugo.toml` 或 `config.toml` 包含 Hugo 标记 | `static/` |
| **Jekyll** | `_config.yml` 包含 Jekyll 标记 | 根目录（与 `index.html` 相同） |
| **Vite** | `vite.config.*` 存在 | `public/` |
| **Create React App** | `package.json` 包含 `react-scripts` 依赖 | `public/` |
| **Vue CLI** | `vue.config.*` 存在 | `public/` |
| **Angular** | `angular.json` 存在 | `src/assets/` |
| **Eleventy** | `.eleventy.js` 或 `eleventy.config.*` 存在 | 检查 `_site` 输出或根目录 |
| **静态 HTML** | 根目录中存在 `index.html` | 与 `index.html` 相同的目录 |

**重要提示**：如果找到现有的 favicons 文件（例如，`favicon.ico`、`apple-touch-icon.png`），请使用其位置作为目标目录，而不管框架检测结果如何。

报告检测到的项目类型和将使用的静态资源目录。

**不确定时请提问**：如果您不确定静态资源应放置的位置（例如，项目结构模糊、多个潜在位置、不熟悉的框架），请使用 `AskUserQuestionTool` 在继续之前确认目标目录。问比放错位置要好。

## 第 3 步：确定应用名称

从以下来源（按优先级顺序）查找应用名称：

1. **现有的 `site.webmanifest**` - 检查检测到的静态资源目录中是否存在现有的 manifest 并提取 `name` 字段
2. **`package.json**` - 如果存在，提取 `name` 字段
3. **Rails `config/application.rb**` - 提取模块名称（例如，`module MyApp` → "MyApp"）
4. **目录名称** - 使用当前工作目录名称作为后备

如果需要，将名称转换为标题大小写（例如，"my-app" → "My App"）。

## 第 4 步：确保静态资源目录存在

检查检测到的静态资源目录是否存在。如果不存在，请创建它。

## 第 5 步：生成 favicons 文件

运行以下 ImageMagick 命令生成所有 favicons 文件。将 `[STATIC_DIR]` 替换为第 2 步检测到的静态资源目录。

### favicon.ico（多分辨率：16x16、32x32、48x48）
```bash
magick "$1" \
  \( -clone 0 -resize 16x16 \) \
  \( -clone 0 -resize 32x32 \) \
  \( -clone 0 -resize 48x48 \) \
  -delete 0 -alpha on -background none \
  [STATIC_DIR]/favicon.ico
```

### favicon-96x96.png
```bash
magick "$1" -resize 96x96 -background none -alpha on [STATIC_DIR]/favicon-96x96.png
```

### apple-touch-icon.png（180x180）
```bash
magick "$1" -resize 180x180 -background none -alpha on [STATIC_DIR]/apple-touch-icon.png
```

### web-app-manifest-192x192.png
```bash
magick "$1" -resize 192x192 -background none -alpha on [STATIC_DIR]/web-app-manifest-192x192.png
```

### web-app-manifest-512x512.png
```bash
magick "$1" -resize 512x512 -background none -alpha on [STATIC_DIR]/web-app-manifest-512x512.png
```

### favicon.svg（仅当源为 SVG 时）
如果源文件具有 `.svg` 扩展名，请复制它：
```bash
cp "$1" [STATIC_DIR]/favicon.svg
```

## 第 6 步：创建/更新 site.webmanifest

使用以下内容创建或更新 `[STATIC_DIR]/site.webmanifest`（替换检测到的应用名称）：

```json
{
  "name": "[APP_NAME]",
  "short_name": "[APP_NAME]",
  "icons": [
    {
      "src": "/web-app-manifest-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "maskable"
    },
    {
      "src": "/web-app-manifest-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable"
    }
  ],
  "theme_color": "#ffffff",
  "background_color": "#ffffff",
  "display": "standalone"
}
```

如果 `site.webmanifest` 已存在于静态目录中，请保留现有的 `theme_color`、`background_color` 和 `display` 值，同时更新 `name`、`short_name` 和 `icons` 数组。

## 第 7 步：更新 HTML/布局文件

根据检测到的项目类型，更新相应的文件。根据静态资源目录相对于 Web 根的位置调整 `href` 路径：
- 如果静态文件在 `public/` 或 `static/` 且从根目录提供 → 使用 `/favicon.ico`
- 如果静态文件在 `src/assets/` → 使用 `/assets/favicon.ico`
- 如果静态文件与 HTML 在同一目录 → 使用 `./favicon.ico` 或仅 `favicon.ico`

### 对于 Rails 项目

编辑 `app/views/layouts/application.html.erb`。找到 `<head>` 部分，并添加/替换 favicons 相关的标签为：

```html
<link rel="icon" type="image/png" href="/favicon-96x96.png" sizes="96x96" />
<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
<link rel="shortcut icon" href="/favicon.ico" />
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
<meta name="apple-mobile-web-app-title" content="[APP_NAME]" />
<link rel="manifest" href="/site.webmanifest" />
```

**重要提示**：
- 如果源不是 SVG，请省略 `<link rel="icon" type="image/svg+xml" href="/favicon.svg" />` 行
- 在添加新标签之前，删除任何现有的 `<link rel="icon"`, `<link rel="shortcut icon"`, `<link rel="apple-touch-icon"`, 或 `<link rel="manifest"` 标签
- 将这些标签放置在 `<head>` 部分的顶部，如果存在 `<meta charset>` 和 `<meta name="viewport">`，则在它们之后

### 对于 Next.js 项目

编辑检测到的布局文件（`app/layout.tsx` 或 `src/app/layout.tsx`）。更新或添加 `metadata` 导出以包含图标配置：

```typescript
export const metadata: Metadata = {
  // ... 保留现有的 metadata 字段
  icons: {
    icon: [
      { url: '/favicon.ico' },
      { url: '/favicon-96x96.png', sizes: '96x96', type: 'image/png' },
      { url: '/favicon.svg', type: 'image/svg+xml' },
    ],
    shortcut: '/favicon.ico',
    apple: '/apple-touch-icon.png',
  },
  manifest: '/site.webmanifest',
  appleWebApp: {
    title: '[APP_NAME]',
  },
};
```

**重要提示**：
- 如果源不是 SVG，请省略 `{ url: '/favicon.svg', type: 'image/svg+xml' }` 条目从图标数组
- 如果 metadata 导出不存在，请仅包含与图标相关的字段创建它
- 如果 metadata 导出存在，请将图标配置与现有字段合并

### 对于静态 HTML 项目

编辑检测到的 `index.html` 文件。在 `<head>` 部分添加相同的 HTML。

### 如果未检测到项目

跳过 HTML 更新，并告知用户需要手动将以下内容添加到 HTML `<head>`：

```html
<link rel="icon" type="image/png" href="/favicon-96x96.png" sizes="96x96" />
<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
<link rel="shortcut icon" href="/favicon.ico" />
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
<meta name="apple-mobile-web-app-title" content="[APP_NAME]" />
<link rel="manifest" href="/site.webmanifest" />
```

## 第 8 步：总结

报告完成情况，包括：
- 检测到的项目类型和框架
- 使用的静态资源目录
- 生成的文件列表
- 在 manifest 和 HTML 中使用的应用名称
- 更新的布局文件（或注明需要手动更新）
- 注明是否覆盖了任何现有文件

## 错误处理

- 如果 ImageMagick 未安装，提供安装说明并停止
- 如果源图像不存在，报告尝试的精确路径并停止
- 如果 ImageMagick 命令失败，报告具体的错误消息
- 如果无法找到布局文件进行 HTML 更新，请继续生成文件并指导手动添加 HTML
