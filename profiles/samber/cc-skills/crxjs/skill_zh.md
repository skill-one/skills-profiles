# CRXJS

CRXJS 是一款 Chrome 扩展开发工具，为弹出页面、选项页面、内容脚本和侧边栏提供真正的热模块替换（HMR）。它读取您的清单文件以自动生成扩展输出，处理内容脚本注入，并管理服务工作者构建。其底层是一个 Vite 插件（`@crxjs/vite-plugin`）。

## 当前状态

- **包**: `@crxjs/vite-plugin` (v2.x 稳定版，截至 2026 年 3 月的最新版本为 v2.4.0)
- **脚手架**: `npm create crxjs@latest` (始终使用 `@latest`)
- **维护者**: @Toumash 和 @FliPPeDround (自 2025 年中期以来)
- **GitHub**: github.com/crxjs/chrome-extension-tools (~4k 星标)
- **Vite 兼容性**: v3 至 v8-beta

## 快速入门

```bash
# 创建新项目（交互式选择框架）
npm create crxjs@latest

# 或添加到现有的 Vite 项目
npm install @crxjs/vite-plugin -D
```

## 按框架配置 Vite

CRXJS 作为 Vite 插件添加。每款框架的设置略有不同。

### React

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { crx } from "@crxjs/vite-plugin";
import manifest from "./manifest.json";

export default defineConfig({
  plugins: [react(), crx({ manifest })],
});
```

为最佳 HMR 兼容性，请使用 `@vitejs/plugin-react`（而不是 `plugin-react-swc`）。如果您必须使用 SWC，请将清单文件类型转换为：

```typescript
import { ManifestV3Export } from "@crxjs/vite-plugin";
const manifest = manifestJson as ManifestV3Export;
```

### Vue

```typescript
import vue from "@vitejs/plugin-vue";
import { crx } from "@crxjs/vite-plugin";
import manifest from "./manifest.json";

export default defineConfig({
  plugins: [vue(), crx({ manifest })],
});
```

### Svelte

```typescript
import { svelte } from "@sveltejs/vite-plugin-svelte";
import { crx } from "@crxjs/vite-plugin";
import manifest from "./manifest.json";

export default defineConfig({
  plugins: [svelte(), crx({ manifest })],
});
```

### Vanilla TypeScript

```typescript
import { crx } from "@crxjs/vite-plugin";
import manifest from "./manifest.json";

export default defineConfig({
  plugins: [crx({ manifest })],
});
```

## defineManifest — 类型安全的动态清单

使用 CRXJS 的 `defineManifest` 替代静态 JSON 文件，以实现动态值和完整的 TypeScript 自动补全：

```typescript
// manifest.ts
import { defineManifest } from "@crxjs/vite-plugin";
import pkg from "./package.json";

export default defineManifest((config) => ({
  manifest_version: 3,
  name: config.command === "serve" ? `[DEV] ${pkg.name}` : pkg.name,
  version: pkg.version,
  description: pkg.description,
  permissions: ["storage", "activeTab", "scripting"],
  action: {
    default_popup: "src/popup/index.html",
    default_icon: {
      "16": "public/icons/icon16.png",
      "48": "public/icons/icon48.png",
    },
  },
  background: {
    service_worker: "src/background/index.ts",
    type: "module",
  },
  content_scripts: [
    {
      matches: ["https://*/*"],
      js: ["src/content/index.ts"],
      css: ["src/content/styles.css"],
    },
  ],
  options_page: "src/options/index.html",
  side_panel: { default_path: "src/sidepanel/index.html" },
  icons: {
    "16": "public/icons/icon16.png",
    "48": "public/icons/icon48.png",
    "128": "public/icons/icon128.png",
  },
}));
```

在 `vite.config.ts` 中导入：

```typescript
import manifest from "./manifest";
// ... crx({ manifest })
```

## 类型声明

添加到 `src/vite-env.d.ts` 或 `src/crxjs.d.ts`：

```typescript
/// <reference types="@crxjs/vite-plugin/client" />
```

这将启用 `?script` 和 `?script&module` 导入的类型。

## 按上下文的热模块替换行为

| 上下文         | 热模块替换 | 工作原理                     |
| -------------- | ---------- | ---------------------------- |
| 弹出页面       | 完全 HMR   | 基于 WebSocket，状态保留     |
| 选项页面       | 完全 HMR   | 与弹出页面相同               |
| 侧边栏         | 完全 HMR   | 与弹出页面相同               |
| 内容脚本（清单） | 真正 HMR   | CRXJS 注入加载器 + HMR 客户端 |
| 内容脚本（动态） | 真正 HMR   | 通过 `?script` 导入           |
| 服务工作者     | 自动重新加载 | 变更触发扩展完全重新加载     |
| 主世界脚本     | 无 HMR     | 被 CRXJS 加载器跳过         |

内容脚本 HMR 工作原理是 CRXJS 生成一个加载器脚本，该脚本导入 HMR 前置代码、HMR 客户端和您的实际脚本，从而实现真正的模块级 HMR 而无需完整页面重新加载。这是 CRXJS 的主要差异化优势。

## 动态内容脚本导入

对于程序化注入的内容脚本（不在清单中），CRXJS 提供特殊的导入后缀：

```typescript
// background.ts — ?script 为 executeScript 提供解析后的路径
import contentScript from "./content?script";

chrome.action.onClicked.addListener(async (tab) => {
  await chrome.scripting.executeScript({
    target: { tabId: tab.id! },
    files: [contentScript],
  });
});
```

对于主世界注入（无 HMR）：

```typescript
import mainWorldScript from "./inject?script&module";

await chrome.scripting.executeScript({
  target: { tabId },
  world: "MAIN",
  files: [mainWorldScript],
});
```

## CRXJS 插件选项

```typescript
crx({
  manifest,
  browser: "chrome", // 'chrome' | 'firefox'
  contentScripts: {
    injectCss: true, // 自动注入内容脚本的 CSS
    hmrTimeout: 5000, // HMR 连接超时 (ms)
  },
});
```

## 开发工作流程

```bash
# 启动开发服务器（输出到 dist/ 并启用 HMR）
npm run dev

# 1. 打开 chrome://extensions
# 2. 启用 "开发者模式"
# 3. 点击 "加载解包"
# 4. 选择 dist/ 目录
# 5. 编辑代码 — 弹出页面/内容脚本通过 HMR 立即更新
# 6. 服务工作者变更触发自动扩展重新加载
```

加载一次后，后续的 `npm run dev` 会话将自动重新连接。除非 `manifest.json` 变更，否则无需重新加载扩展。

## 生产构建

```bash
npm run build    # 输出到 dist/
```

dist/ 目录已准备好压缩并上传到 Chrome Web Store：

```bash
cd dist && zip -r ../extension.zip .
```

禁用 Vite 的模块预加载以避免 Chrome Web Store 拒绝内联脚本：

```typescript
build: {
  modulePreload: false;
}
```

## 已知问题和解决方案

### Tailwind CSS 在内容脚本中的 HMR

新添加的 Tailwind 类可能不会触发内容脚本的 CSS 更新。**解决方案**：添加新的实用类后重启开发服务器。在 v2.4.0 中有所改进但未完全解决。确保配置中 `injectCss: true`。

### WebSocket 连接错误 (`ws://localhost:undefined/`)

**原因**：开发服务器和 HMR 配置的端口不匹配。**修复**：显式设置两者为相同值：

```typescript
server: {
  port: 5173,
  strictPort: true,
  hmr: { port: 5173 },
}
```

### "清单版本 2 已弃用" 警告

如果看到此警告，您的清单被解释为 MV2。**修复**：确保设置 `"manifest_version": 3`。

### 内容脚本在 file:// URL 上不注入

Chrome 要求用户在扩展设置中（chrome://extensions）启用 "允许访问文件 URL"。CRXJS 无法更改此设置。

### Chrome 更新后 HMR 停止工作

CRXJS 的 HMR 依赖于注入一个连接到开发服务器 WebSocket 的内容脚本。Chrome 安全更新偶尔会破坏此功能。**修复**：更新到最新 CRXJS 版本，该版本跟踪 Chrome 变更。

## CRXJS 与替代方案对比

| 功能         | CRXJS | WXT  | Plasmo |
| ------------ | ----- | ---- | ------ |
| 内容脚本 HMR | 真正 HMR | 文件重载 | 部分支持 |
| 框架支持     | 任何 Vite 框架 | 任何 | React 为主 |
| 抽象级别     | 薄（Vite 插件） | 完全框架 | 完全框架 |
| 消息辅助函数 | 无（直接使用 chrome.*） | 内置 | 内置 |
| 存储包装器   | 无   | 内置 | 内置 |
| 跨浏览器支持 | Chrome + Firefox | Chrome + Firefox + Safari | Chrome + Firefox |
| 文件路由     | 否   | 是   | 是   |
| 学习曲线     | 低（了解 Vite，了解 CRXJS） | 中等 | 中等 |

**选择 CRXJS 的场景**：当您希望最小化对原始 Chrome API 的抽象，并优先考虑内容脚本 HMR 时。CRXJS 不会干预——没有魔法路由，没有包装 API，只是带 HMR 的您的代码。

**选择 WXT 的场景**：当您需要约定、内置工具和跨浏览器支持时。

**选择 Plasmo 的场景**：当您以 React 为主，并希望最高级别的抽象时。

## 项目结构（推荐）

```
my-extension/
├── src/
│   ├── background/
│   │   └── index.ts
│   ├── content/
│   │   ├── index.ts
│   │   └── styles.css
│   ├── popup/
│   │   ├── index.html        <- CRXJS 自动解析 HTML 入口点
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── options/
│   │   ├── index.html
│   │   └── main.tsx
│   ├── sidepanel/
│   │   ├── index.html
│   │   └── main.tsx
│   └── shared/
│       ├── messages.ts
│       └── storage.ts
├── public/
│   └── icons/
├── manifest.ts               <- 或 manifest.json
├── vite.config.ts
├── tsconfig.json
└── package.json
```

CRXJS 会自动解析清单中引用的 HTML 文件。您的 popup.html 可以使用标准的 `<script type="module" src="./main.tsx">` 并正常工作。

如果您在 CRXJS 中遇到 Bug 或意外行为，请到 github.com/crxjs/chrome-extension-tools/issues 打开问题。
