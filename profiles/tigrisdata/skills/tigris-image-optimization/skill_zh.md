# Tigris 图片优化

对存储在 Tigris 中的图片进行缩放、裁剪和优化。上传时生成缩略图，提供响应式图片，并利用 Tigris 的全球 CDN 实现快速交付。

## 策略概述

| 方法 | 使用场景 | 优点 | 缺点 |
|------|----------|------|------|
| 上传时处理 | 缩略图、固定尺寸 | 加载速度快、可预测 | 每个变体的存储成本 |
| 请求时处理 | 多种尺寸变化 | 灵活、存储成本低 | 首次请求时延迟 |
| 客户端缩放 | 上传前 | 节省带宽、上传速度快 | 对质量控制较少 |

**推荐：** 对于已知尺寸（头像、缩略图、封面）使用上传时处理。使用公共存储桶进行 CDN 交付 — Tigris 会自动从最近的全球边缘节点提供公共文件。

---

## 上传时处理（通用模式）

上传文件时生成变体，将每个变体存储为单独的对象：

```
avatars/user-123.jpg          # 原始文件
avatars/user-123-thumb.jpg    # 100x100
avatars/user-123-medium.jpg   # 400x400
avatars/user-123-large.jpg    # 800x800
```

对于需要快速 CDN 支持交付的图片，使用 `access: "public"`。

---

## 框架指南

查阅您所使用框架的资源文件：

- **Next.js** — 阅读 `./resources/nextjs.md` 了解 next/image 配置和 Sharp 处理
- **Remix** — 阅读 `./resources/remix.md` 了解 Sharp 在 action 函数中的使用和响应式 srcset
- **Express** — 阅读 `./resources/express.md` 了解 Sharp 中间件与 Multer
- **Rails** — 阅读 `./resources/rails.md` 了解 Active Storage 变体
- **Django** — 阅读 `./resources/django.md` 了解 django-imagekit 和 Pillow 处理
- **Laravel** — 阅读 `./resources/laravel.md` 了解 Intervention Image

---

## CDN 交付

Tigris 公共存储桶从最近的全球边缘节点提供文件 — 无需单独设置 CDN。

**图片缓存头：**

```typescript
await put("images/hero.jpg", buffer, {
  access: "public",
  contentType: "image/jpeg",
});
```

对于不可变的内容哈希文件名（例如 `hero-abc123.jpg`），使用较长的缓存时间。对于可变路径，使用较短的 TTL 或 ETags。

---

## 严格规则

**必须：** 对于向用户提供的图片使用 `access: "public"`（启用 CDN） | 在上传时为已知尺寸生成缩略图 | 使用 WebP/AVIF 减小文件大小 | 设置明确的 `contentType`

**禁止：** 无缓存地每次请求都处理图片 | 仅存储原始文件（如果始终提供缩略图） | 下载完整尺寸图片后在浏览器中缩放

---

## 相关技能

- **tigris-file-uploads** — 每个框架的完整上传模式
- **tigris-egress-optimizer** — 减少图片交付的带宽成本

## 官方文档

- Tigris SDK: https://www.tigrisdata.com/docs/sdks/tigris/
- Sharp: https://sharp.pixelplumbing.com/
