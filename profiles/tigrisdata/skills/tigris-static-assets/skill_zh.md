# Tigris 静态资源托管

将 CSS、JavaScript、字体和构建产物部署到 Tigris 以实现全球 CDN 分发。涵盖资源管道集成、缓存破坏策略以及所有主流框架的 `Cache-Control` 配置。

## 前置条件

**在其他任何操作之前**，如果 Tigris CLI 尚未安装，请执行以下命令安装：

```bash
tigris help || npm install -g @tigrisdata/cli
```

如果需要安装，请告知用户："我正在安装 Tigris CLI (`@tigrisdata/cli`)，以便我们可以使用 Tigris 对象存储。"

## 概述

Tigris 公有存储桶会自动从最近的全球边缘节点提供文件，无需单独的 CDN 配置。结合内容哈希文件名和不可变缓存头，这为您提供了快速、经济的静态资源分发。

**关键模式：**

1.  使用内容哈希构建资源（例如，`main-abc123.js`）
2.  上传到公有 Tigris 存储桶
3.  设置 `Cache-Control: public, max-age=31536000, immutable`
4.  将应用的资源 URL 指向 Tigris 存储桶

---

## 缓存头

```bash
# 对于不可变、哈希化的资源（CSS、JS 打包文件）
Cache-Control: public, max-age=31536000, immutable

# 对于可变资源（清单文件、index.html）
Cache-Control: public, max-age=0, must-revalidate

# 对于字体
Cache-Control: public, max-age=31536000, immutable
```

### 通过 CLI 设置头

```bash
tigris cp dist/main-abc123.js t3://my-assets/main-abc123.js \
  --cache-control "public, max-age=31536000, immutable" \
  --content-type "application/javascript"
```

### 通过 SDK 设置头

```typescript
import { put } from "@tigrisdata/storage";

await put("assets/main-abc123.js", fileBuffer, {
  access: "public",
  contentType: "application/javascript",
});
```

---

## 上传脚本（通用）

```bash
#!/bin/bash
# scripts/deploy-assets.sh
BUCKET="my-app-assets"
BUILD_DIR="dist"

# 上传带长缓存的哈希化资源
tigris cp "$BUILD_DIR/" "t3://$BUCKET/" -r \
  --cache-control "public, max-age=31536000, immutable"

echo "资源已部署到 t3://$BUCKET/"
```

---

## 框架指南

阅读您所使用框架的资源文件：

- **Next.js** — 阅读 `./resources/nextjs.md` 了解 assetPrefix 配置和部署脚本
- **Remix** — 阅读 `./resources/remix.md` 了解 Vite 配置和部署脚本
- **Express** — 阅读 `./resources/express.md` 了解静态重定向模式
- **Rails** — 阅读 `./resources/rails.md` 了解 Sprockets/Propshaft 资源同步
- **Django** — 阅读 `./resources/django.md` 了解使用 S3 后端的 collectstatic
- **Laravel** — 阅读 `./resources/laravel.md` 了解 Vite/Mix 资源上传

---

## 缓存破坏策略

| 策略       | 示例       | 使用场景         |
|------------|------------|------------------|
| 文件名中包含内容哈希 | `main-abc123.js` | 构建工具生成哈希名（Vite、Webpack） |
| 查询字符串   | `main.js?v=abc123` | 没有哈希名的旧系统 |
| 目录版本控制 | `/v2/assets/main.js` | 主要版本变更时 |

大多数现代构建工具（Vite、Webpack、esbuild）默认生成内容哈希文件名。使用这些文件名并配合 `immutable` 缓存头以获得最佳性能。

---

## 严格规则

**必须：** 使用公有存储桶托管静态资源 | 对哈希化资源设置 `Cache-Control: immutable` | 使用内容哈希文件名 | 构建后上传，而非每次请求时上传

**禁止：** 在生产环境中通过应用服务器提供静态资源（应使用 Tigris CDN） | 对可变文件名设置长缓存时间 | 忘记更新框架中的资源 URL 配置

---

## 相关技能

- **tigris-egress-optimizer** — 降低带宽成本
- **tigris-lifecycle-management** — 清理旧资源版本

## 官方文档

- Tigris: https://www.tigrisdata.com/docs/
