# Favicon 生成器

从标志、首字母或品牌颜色生成完整的 Favicon 包。生成所有所需格式和 HTML 集成代码。

## 工作流程

### 第 1 步：选择您的方案

```
有带图标元素的标志吗？
 是 -> 从标志中提取图标
 否 -> 有文字/首字母吗？
         是 -> 创建单字母 Favicon
         否 -> 使用品牌形状
```

### 第 2 步：创建源 SVG

**提取的图标** — 从标志中复制图标路径，在 32x32 的 viewBox 中居中，为小尺寸简化。

**单字母** — 使用 `assets/` 中的模板：
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <circle cx="16" cy="16" r="16" fill="#0066cc"/>
  <text x="16" y="21" font-size="16" font-weight="bold"
        text-anchor="middle" fill="#ffffff" font-family="sans-serif">AC</text>
</svg>
```

**品牌形状** — 圆形（通用）、圆角方形（现代）、盾牌（安全）、六边形（科技）。

SVG 模板位于 `assets/` 目录中。

### 第 3 步：生成所有格式

需要 ImageMagick (`convert` 命令)。如果需要安装：`brew install imagemagick`（macOS）或 `apt install imagemagick`（Linux）。

```bash
# ICO (16x16 + 32x32)
convert favicon.svg -define icon:auto-resize=16,32 favicon.ico

# Apple Touch Icon (180x180, SOLID 背景 — 透明 = iOS 上的黑色)
convert favicon.svg -resize 180x180 -background "#0066cc" -alpha remove apple-touch-icon.png

# Android/PWA 图标
convert favicon.svg -resize 192x192 icon-192.png
convert favicon.svg -resize 512x512 icon-512.png
```

**没有 ImageMagick？** 使用 https://favicon.io 从 SVG 转换。

### 第 4 步：创建 Web Manifest

复制并自定义 `assets/manifest.webmanifest`：
```json
{
  "name": "您的公司名称",
  "short_name": "公司",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ],
  "theme_color": "#0066cc",
  "background_color": "#ffffff",
  "display": "standalone"
}
```

### 第 5 步：添加 HTML 标签

```html
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#0066cc">
```

将所有文件放置在网站根目录（Vite/React 中的 `/public/`）。

---

## 关键规则

- **始终生成所有格式** — SVG、ICO、apple-touch-icon、192、512、manifest
- **iOS 图标必须具有实心背景** — 透明 = 黑色方形
- **始终为单字母文本使用粗字体权重**（常规在 16x16 时消失）
- **在 16x16 下测试** — 如果不清晰，请简化
- **切勿使用 CMS 默认值**（WordPress "W" 等）

## 格式快速参考

| 格式 | 尺寸 | 透明度 | 目的 |
|------|------|--------|------|
| `favicon.svg` | 矢量 | 是 | 现代浏览器 |
| `favicon.ico` | 16+32 | 是 | 传统浏览器 |
| `apple-touch-icon.png` | 180x180 | **否** | iOS 主屏幕 |
| `icon-192.png` | 192x192 | 是 | Android |
| `icon-512.png` | 512x512 | 是 | PWA |

## 资源文件

- `assets/favicon-svg-circle.svg` — 圆形单字母模板
- `assets/favicon-svg-square.svg` — 圆角方形模板
- `assets/favicon-svg-shield.svg` — 盾牌模板
- `assets/manifest.webmanifest` — Web manifest 模板

## 参考文件

- `references/format-guide.md` — 完整格式规范
- `references/extraction-methods.md` — 标志图标提取步骤
- `references/monogram-patterns.md` — 高级单字母设计
- `references/shape-templates.md` — 带有 SVG 代码的行业特定形状
