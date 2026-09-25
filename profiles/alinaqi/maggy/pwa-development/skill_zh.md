# PWA 开发技能

**目的：** 构建 Progressive Web Apps（渐进式网络应用），使其离线可用、类似原生应用安装，并在所有设备上提供快速、可靠体验。

---

## 核心PWA要求

```
┌─────────────────────────────────────────────────────────────────┐
│  PWA 的三大支柱                                       │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  1. HTTPS                                                       │
│     需要服务工作者和安全性。                                  │
│     开发环境允许使用 localhost。                              │
│                                                                 │
│  2. 服务工作者 (SERVICE WORKER)                               │
│     在后台运行的 JavaScript。                                │
│     支持离线、缓存、推送通知。                              │
│                                                                 │
│  3. Web 应用清单 (WEB APP MANIFEST)                           │
│     描述应用元数据的 JSON 文件。                            │
│     支持安装和应用类体验。                                  │
├─────────────────────────────────────────────────────────────────┤
│  安装性标准 (Chrome)                                       │
│  ─────────────────────────────────────────────────────────────  │
│  • HTTPS (或 localhost)                                         │
│  • 具有获取处理器的服务工作者                            │
│  • 清单包含：name、icons (192px + 512px)、                  │
│    start_url、display: standalone/fullscreen/minimal-ui         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Web 应用清单

### 必填字段

```json
{
  "name": "我的渐进式网络应用",
  "short_name": "我的PWA",
  "description": "描述应用的功能",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#000000",
  "icons": [
    {
      "src": "/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512-maskable.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable"
    }
  ]
}
```

### 增强型清单（完整功能）

```json
{
  "name": "我的渐进式网络应用",
  "short_name": "我的PWA",
  "description": "功能齐全的PWA",
  "start_url": "/?source=pwa",
  "scope": "/",
  "display": "standalone",
  "orientation": "portrait-primary",
  "background_color": "#ffffff",
  "theme_color": "#3367D6",
  "dir": "ltr",
  "lang": "en",
  "categories": ["productivity", "utilities"],

  "icons": [
    { "src": "/icons/icon-72.png", "sizes": "72x72", "type": "image/png" },
    { "src": "/icons/icon-96.png", "sizes": "96x96", "type": "image/png" },
    { "src": "/icons/icon-128.png", "sizes": "128x128", "type": "image/png" },
    { "src": "/icons/icon-144.png", "sizes": "144x144", "type": "image/png" },
    { "src": "/icons/icon-152.png", "sizes": "152x152", "type": "image/png" },
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/icon-384.png", "sizes": "384x384", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/icons/icon-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ],

  "screenshots": [
    {
      "src": "/screenshots/desktop.png",
      "sizes": "1280x720",
      "type": "image/png",
      "form_factor": "wide"
    },
    {
      "src": "/screenshots/mobile.png",
      "sizes": "750x1334",
      "type": "image/png",
      "form_factor": "narrow"
    }
  ],

  "shortcuts": [
    {
      "name": "新建项目",
      "short_name": "新建",
      "description": "创建新项目",
      "url": "/new?source=shortcut",
      "icons": [{ "src": "/icons/shortcut-new.png", "sizes": "192x192" }]
    }
  ],

  "share_target": {
    "action": "/share",
    "method": "POST",
    "enctype": "multipart/form-data",
    "params": {
      "title": "title",
      "text": "text",
      "url": "url",
      "files": [{ "name": "files", "accept": ["image/*"] }]
    }
  },

  "protocol_handlers": [
    {
      "protocol": "web+myapp",
      "url": "/handle?url=%s"
    }
  ],

  "file_handlers": [
    {
      "action": "/open-file",
      "accept": {
        "text/plain": [".txt"]
      }
    }
  ]
}
```

### 清单检查清单

- [ ] `name` 和 `short_name` 已定义
- [ ] `start_url` 已设置（使用查询参数进行分析）
- [ ] `display` 设置为 `standalone` 或 `fullscreen`
- [ ] 图标：至少包含 192x192 和 512x512
- [ ] 包含用于 Android 自适应图标的 maskable 图标
- [ ] `theme_color` 与应用设计匹配
- [ ] `background_color` 用于启动画面
- [ ] 用于更丰富的安装 UI 的截图（可选）
- [ ] 快速操作的快捷方式（可选）

---

## 服务工作者模式

### 基础服务工作者

```javascript
// sw.js
const CACHE_NAME = 'app-cache-v1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/styles/main.css',
  '/scripts/app.js',
  '/offline.html'
];

// 安装：缓存静态资源
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// 激活：清理旧缓存
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys
          .filter((key) => key !== CACHE_NAME)
          .map((key) => caches.delete(key))
      ))
      .then(() => self.clients.claim())
  );
});

// 获取：从缓存提供，网络降级
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((cached) => cached || fetch(event.request))
      .catch(() => caches.match('/offline.html'))
  );
});
```

### 注册

```javascript
// main.js
if ('serviceWorker' in navigator) {
  window.addEventListener('load', async () => {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/'
      });
      console.log('SW registered:', registration.scope);
    } catch (error) {
      console.error('SW registration failed:', error);
    }
  });
}
```

---

## 缓存策略

### 策略选择指南

| 策略 | 用例 | 描述 |
|----------|----------|-------------|
| **Cache First** | 静态资源 (CSS, JS, 图片) | 检查缓存，网络降级 |
| **Network First** | API 响应，动态内容 | 尝试网络，缓存降级 |
| **Stale While Revalidate** | 半静态内容 (头像，文章) | 立即提供缓存，后台更新 |
| **Network Only** | 非缓存请求 (分析) | 总是使用网络 |
| **Cache Only** | 仅离线资源 | 仅从缓存提供 |

### Cache First (离线优先)

```javascript
// 最佳用于：很少变化的静态资源
self.addEventListener('fetch', (event) => {
  if (event.request.destination === 'image' ||
      event.request.destination === 'style' ||
      event.request.destination === 'script') {
    event.respondWith(
      caches.match(event.request)
        .then((cached) => {
          if (cached) return cached;
          return fetch(event.request).then((response) => {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, clone);
            });
            return response;
          });
        })
    );
  }
});
```

### Network First (最新优先)

```javascript
// 最佳用于：API 数据，频繁更新的内容
self.addEventListener('fetch', (event) => {
  if (event.request.url.includes('/api/')) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, clone);
          });
          return response;
        })
        .catch(() => caches.match(event.request))
    );
  }
});
```

### Stale While Revalidate

```javascript
// 最佳用于：可以稍微过时的内容
self.addEventListener('fetch', (event) => {
  if (event.request.url.includes('/articles/')) {
    event.respondWith(
      caches.open(CACHE_NAME).then((cache) => {
        return cache.match(event.request).then((cached) => {
          const fetchPromise = fetch(event.request).then((response) => {
            cache.put(event.request, response.clone());
            return response;
          });
          return cached || fetchPromise;
        });
      })
    );
  }
});
```

---

## Workbox（推荐）

### 为什么使用 Workbox？

- 经验证的缓存策略
- 带版本管理的预缓存
- 离线表单的后台同步
- 自动缓存清理
- TypeScript 支持

### 安装

```bash
npm install workbox-webpack-plugin  # Webpack
npm install @vite-pwa/vite-plugin   # Vite
```

### Vite 中的 Workbox

```javascript
// vite.config.js
import { VitePWA } from 'vite-plugin-pwa';

export default {
  plugins: [
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'robots.txt', 'apple-touch-icon.png'],
      manifest: {
        name: '我的应用',
        short_name: '应用',
        theme_color: '#ffffff',
        icons: [
          { src: 'pwa-192x192.png', sizes: '192x192', type: 'image/png' },
          { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png' }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\.example\.com\/.*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 // 24小时
              }
            }
          },
          {
            urlPattern: /\.(?:png|jpg|jpeg|svg|gif)$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'image-cache',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 60 * 60 * 24 * 30 // 30天
              }
            }
          }
        ]
      }
    })
  ]
};
```

### Workbox 手动服务工作者

```javascript
// sw.js
import { precacheAndRoute } from 'workbox-precaching';
import { registerRoute } from 'workbox-routing';
import { CacheFirst, NetworkFirst, StaleWhileRevalidate } from 'workbox-strategies';
import { ExpirationPlugin } from 'workbox-expiration';
import { CacheableResponsePlugin } from 'workbox-cacheable-response';

// 预缓存静态资源（由构建工具生成）
precacheAndRoute(self.__WB_MANIFEST);

// 缓存图片
registerRoute(
  ({ request }) => request.destination === 'image',
  new CacheFirst({
    cacheName: 'images',
    plugins: [
      new CacheableResponsePlugin({ statuses: [0, 200] }),
      new ExpirationPlugin({
        maxEntries: 60,
        maxAgeSeconds: 30 * 24 * 60 * 60 // 30天
      })
    ]
  })
);

// 缓存API响应
registerRoute(
  ({ url }) => url.pathname.startsWith('/api/'),
  new NetworkFirst({
    cacheName: 'api-responses',
    plugins: [
      new CacheableResponsePlugin({ statuses: [0, 200] }),
      new ExpirationPlugin({
        maxEntries: 100,
        maxAgeSeconds: 24 * 60 * 60 // 24小时
      })
    ]
  })
);

// 缓存页面导航
registerRoute(
  ({ request }) => request.mode === 'navigate',
  new NetworkFirst({
    cacheName: 'pages',
    plugins: [
      new CacheableResponsePlugin({ statuses: [0, 200] })
    ]
  })
);
```

---

## 离线体验

### 离线页面

```html
<!-- offline.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>离线 - 应用名称</title>
  <style>
    body {
      font-family: system-ui, sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
      background: #f5f5f5;
    }
    .offline-content {
      text-align: center;
      padding: 2rem;
    }
    .offline-icon { font-size: 4rem; }
    h1 { color: #333; }
    p { color: #666; }
    button {
      background: #3367D6;
      color: white;
      border: none;
      padding: 0.75rem 1.5rem;
      border-radius: 4px;
      cursor: pointer;
      font-size: 1rem;
    }
  </style>
</head>
<body>
  <div class="offline-content">
    <div class="offline-icon">📡</div>
    <h1>您处于离线状态</h1>
    <p>检查您的连接并重试。</p>
    <button onclick="location.reload()">重试</button>
  </div>
</body>
</html>
```

### 离线检测

```javascript
// 在线/离线状态处理
function updateOnlineStatus() {
  const status = navigator.onLine ? 'online' : 'offline';
  document.body.dataset.connectionStatus = status;

  if (!navigator.onLine) {
    showNotification('您处于离线状态。某些功能可能不可用。');
  }
}

window.addEventListener('online', updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);
updateOnlineStatus();
```

### 后台同步（离线操作队列）

```javascript
// sw.js with Workbox
import { BackgroundSyncPlugin } from 'workbox-background-sync';
import { registerRoute } from 'workbox-routing';
import { NetworkOnly } from 'workbox-strategies';

const bgSyncPlugin = new BackgroundSyncPlugin('formQueue', {
  maxRetentionTime: 24 * 60 // 24小时重试
});

registerRoute(
  ({ url }) => url.pathname === '/api/submit',
  new NetworkOnly({
    plugins: [bgSyncPlugin]
  }),
  'POST'
);
```

```javascript
// main.js - 队列表单提交
async function submitForm(data) {
  try {
    const response = await fetch('/api/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  } catch (error) {
    // 将在联网时由后台同步重试
    showNotification('离线保存。联网后同步。');
  }
}
```

---

## 应用类功能

### 安装提示

```javascript
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  showInstallButton();
});

async function installApp() {
  if (!deferredPrompt) return;

  deferredPrompt.prompt();
  const { outcome } = await deferredPrompt.userChoice;

  console.log(`用户${outcome === 'accepted' ? '接受' : '拒绝'}安装`);
  deferredPrompt = null;
  hideInstallButton();
}

window.addEventListener('appinstalled', () => {
  console.log('应用已安装');
  deferredPrompt = null;
});
```

### 检测独立模式

```javascript
// 检查是否作为安装的PWA运行
function isInstalledPWA() {
  return window.matchMedia('(display-mode: standalone)').matches ||
         window.navigator.standalone === true; // iOS
}

// 监听显示模式变化
window.matchMedia('(display-mode: standalone)')
  .addEventListener('change', (e) => {
    console.log('显示模式:', e.matches ? '独立' : '浏览器');
  });
```

### 推送通知

```javascript
// 请求权限
async function requestNotificationPermission() {
  const permission = await Notification.requestPermission();
  if (permission === 'granted') {
    await subscribeToPush();
  }
  return permission;
}

// 订阅推送
async function subscribeToPush() {
  const registration = await navigator.serviceWorker.ready;
  const subscription = await registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
  });

  // 将订阅发送到服务器
  await fetch('/api/push/subscribe', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(subscription)
  });
}

// sw.js - 处理推送事件
self.addEventListener('push', (event) => {
  const data = event.data.json();
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: '/icons/icon-192.png',
      badge: '/icons/badge-72.png',
      data: { url: data.url }
    })
  );
});

// 处理通知点击
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data.url)
  );
});
```

### 分享目标

```javascript
// sw.js - 处理分享目标
self.addEventListener('fetch', (event) => {
  if (event.request.url.endsWith('/share') &&
      event.request.method === 'POST') {
    event.respondWith((async () => {
      const formData = await event.request.formData();
      const title = formData.get('title');
      const text = formData.get('text');
      const url = formData.get('url');

      // 存储或处理共享内容
      // 重定向到带共享数据的应用
      return Response.redirect(`/?shared=true&title=${encodeURIComponent(title)}`);
    })());
  }
});
```

---

## 性能优化

### 关键渲染路径

```html
<!-- 内联关键CSS -->
<style>
  /* 关键内容区样式 */
</style>

<!-- 预加载重要资源 -->
<link rel="preload" href="/fonts/main.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/scripts/app.js" as="script">

<!-- 延迟加载非关键CSS -->
<link rel="stylesheet" href="/styles/main.css" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="/styles/main.css"></noscript>
```

### 图片优化

```html
<!-- 响应式图片 -->
<img
  src="/images/hero-800.webp"
  srcset="
    /images/hero-400.webp 400w,
    /images/hero-800.webp 800w,
    /images/hero-1200.webp 1200w
  "
  sizes="(max-width: 600px) 400px, (max-width: 1200px) 800px, 1200px"
  alt="英雄图片"
  loading="lazy"
  decoding="async"
>

<!-- 现代格式带降级 -->
<picture>
  <source srcset="/images/hero.avif" type="image/avif">
  <source srcset="/images/hero.webp" type="image/webp">
  <img src="/images/hero.jpg" alt="英雄图片" loading="lazy">
</picture>
```

### 代码分割

```javascript
// 动态导入用于基于路由的分割
const routes = {
  '/': () => import('./pages/Home.js'),
  '/about': () => import('./pages/About.js'),
  '/settings': () => import('./pages/Settings.js')
};

async function loadPage(path) {
  const loader = routes[path];
  if (loader) {
    const module = await loader();
    return module.default;
  }
}
```

---

## 测试PWA

### Lighthouse审计

```bash
# 从CLI运行Lighthouse
npx lighthouse https://your-app.com --view

# 关键指标检查：
# - PWA徽章（可安装，离线可用）
# - 性能分数
# - 最佳实践
# - 可访问性
```

### 手动测试检查清单

- [ ] **可安装性**
  - [ ] 在桌面Chrome上出现安装提示
  - [ ] 可在移动设备上添加到主屏幕
  - [ ] 安装后以独立模式打开应用

- [ ] **离线支持**
  - [ ] 离线时应用可加载（飞行模式）
  - [ ] 缓存页面显示正确
  - [ ] 非缓存路由显示离线降级页面
  - [ ] 网络恢复时后台同步工作

- [ ] **性能**
  - [ ] First Contentful Paint < 1.8s
  - [ ] Largest Contentful Paint < 2.5s
  - [ ] Time to Interactive < 3.8s
  - [ ] Cumulative Layout Shift < 0.1

- [ ] **服务工作者**
  - [ ] SW注册成功
  - [ ] 安装时缓存静态资源
  - [ ] SW正确更新（新版本）
  - [ ] 无陈旧缓存问题

- [ ] **清单**
  - [ ] 所有必填字段存在
  - [ ] 图标显示正确
  - [ ] 主题色已应用
  - [ ] 启动时显示启动画面

### 测试服务工作者更新

```javascript
// 强制更新检查
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.ready.then((registration) => {
    registration.update();
  });
}

// 监听更新
navigator.serviceWorker.addEventListener('controllerchange', () => {
  // 新服务工作者激活
  window.location.reload();
});
```

---

## 项目结构

```
project/
├── public/
│   ├── manifest.json           # Web应用清单
│   ├── sw.js                   # 服务工作者（如果未打包）
│   ├── offline.html            # 离线降级页面
│   ├── robots.txt
│   └── icons/
│       ├── icon-72.png
│       ├── icon-96.png
│       ├── icon-128.png
│       ├── icon-144.png
│       ├── icon-152.png
│       ├── icon-192.png
│       ├── icon-384.png
│       ├── icon-512.png
│       ├── icon-maskable.png   # 用于自适应图标
│       ├── apple-touch-icon.png
│       └── favicon.ico
├── src/
│   ├── sw.js                   # 服务工作者源码（如果打包）
│   ├── pwa/
│   │   ├── install.js          # 安装提示处理
│   │   ├── offline.js          # 离线检测
│   │   └── push.js             # 推送通知处理
│   └── ...
└── tests/
    └── pwa/
        ├── manifest.test.js
        ├── sw.test.js
        └── offline.test.js
```

---

## 常见错误

| 错误 | 修复 |
|---------|-----|
| 缺少maskable图标 | 添加带 `"purpose": "maskable"` 的图标 |
| 无离线降级 | 创建 `offline.html` 并缓存 |
| 缓存永不过期 | 使用 `ExpirationPlugin` |
| 服务工作者缓存过于激进 | 根据资源类型使用适当的策略 |
| 无更新机制 | 实现 `skipWaiting()` + 重载提示 |
| 安装提示损坏 | 确保清单满足所有标准 |
| 生产环境无HTTPS | 配置SSL证书 |
| 缓存大小过大 | 设置 `maxEntries` 和 `maxAgeSeconds` |
| 陈旧API响应 | 使用 `NetworkFirst` |
| 缺少start_url跟踪 | 添加查询参数：`/?source=pwa` |

---

## PWA开发检查清单

### 发布前

- [ ] HTTPS配置（生产环境）
- [ ] 完整的清单，包含所有必填字段
- [ ] 所有要求的图标大小（192, 512, maskable）
- [ ] 服务工作者注册并工作
- [ ] 创建离线页面并缓存
- [ ] 为所有资源类型定义缓存策略
- [ ] 实现安装提示处理
- [ ] Lighthouse PWA审计通过

### 发布后

- [ ] 监控缓存大小
- [ ] 测试SW更新不会破坏应用
- [ ] 通过分析跟踪PWA安装
- [ ] 在多设备/浏览器上测试
- [ ] 监控核心网络价值
- [ ] 设置推送通知流程（如果需要）

---

## 框架特定指南

### Next.js

```bash
npm install next-pwa
```

```javascript
// next.config.js
const withPWA = require('next-pwa')({
  dest: 'public',
  disable: process.env.NODE_ENV === 'development'
});

module.exports = withPWA({
  // 你的Next.js配置
});
```

### Create React App

```bash
# CRA 4+内置PWA支持
npx create-react-app my-pwa --template cra-template-pwa
```

### Vite（任何框架）

```bash
npm install vite-plugin-pwa -D
```

见Workbox with Vite部分配置。

---

## 快速参考

### 缓存策略速查表

```
静态资源 (CSS, JS, 图片)     → Cache First
API响应                        → Network First
用户生成内容              → Stale While Revalidate
分析, 非缓存            → Network Only
仅离线资源                 → Cache Only
```

### 清单最小要求

```json
{
  "name": "应用名称",
  "short_name": "应用",
  "start_url": "/",
  "display": "standalone",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

### 服务工作者生命周期

```
1. 注册 → 2. 安装 → 3. 激活 → 4. 获取
     ↓              ↓            ↓           ↓
  加载应用    缓存资源  清理旧缓存  从缓存/网络提供请求
                            缓存
```
