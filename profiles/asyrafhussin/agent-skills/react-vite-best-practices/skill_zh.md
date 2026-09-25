# React + Vite 最佳实践

针对使用 Vite 构建的 React 应用的全面性能优化指南。包含 6 个类别中的 23 条规则，涵盖构建优化、代码分割、开发性能、资源处理、环境配置和包分析。

## 元数据

- **版本:** 2.0.0
- **框架:** React + Vite
- **规则数量:** 6 个类别中的 23 条规则
- **许可证:** MIT

## 应用时机

参考这些指南的场合：
- 为 React 项目配置 Vite
- 实现代码分割和懒加载
- 优化构建输出和包大小
- 设置开发环境和 HMR
- 处理图片、字体、SVG 和静态资源
- 跨环境管理环境变量
- 分析包大小和依赖

## 按优先级排序的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | 构建优化 | 关键 | `build-` |
| 2 | 代码分割 | 关键 | `split-` |
| 3 | 开发 | 高 | `dev-` |
| 4 | 资源处理 | 高 | `asset-` |
| 5 | 环境配置 | 中 | `env-` |
| 6 | 包分析 | 中 | `bundle-` |

## 快速参考

### 1. 构建优化 (关键)

- `build-manual-chunks` - 配置手动分割以分离第三方库
- `build-minification` - 使用 OXC（默认）或 Terser 进行压缩
- `build-target-modern` - 目标浏览器（广泛使用的基线）
- `build-sourcemaps` - 按环境配置源映射
- `build-tree-shaking` - 确保使用 ESM 进行正确的树摇动
- `build-compression` - Gzip 和 Brotli 压缩
- `build-asset-hashing` - 基于内容的哈希以实现缓存破坏

### 2. 代码分割 (关键)

- `split-route-lazy` - 使用 React.lazy() 进行路由分割
- `split-suspense-boundaries` - 战略性放置 Suspense 边界
- `split-dynamic-imports` - 使用动态 import() 加载重组件
- `split-component-lazy` - 懒加载非关键组件
- `split-prefetch-hints` - 在悬停/空闲/视口预取代码块

### 3. 开发 (高)

- `dev-dependency-prebundling` - 配置 optimizeDeps 以加快启动速度
- `dev-fast-refresh` - React Fast Refresh 模式
- `dev-hmr-config` - HMR 服务器配置

### 4. 资源处理 (高)

- `asset-image-optimization` - 图片优化和懒加载
- `asset-svg-components` - 使用 SVGR 将 SVG 作为 React 组件
- `asset-fonts` - Web 字体加载策略
- `asset-public-dir` - 公共目录与 JavaScript 导入

### 5. 环境配置 (中)

- `env-vite-prefix` - 客户端变量的 VITE_ 前缀
- `env-modes` - 模式特定的环境文件
- `env-sensitive-data` - 永远不要在客户端代码中暴露密钥

### 6. 包分析 (中)

- `bundle-visualizer` - 使用 rollup-plugin-visualizer 分析包

## 基本配置

### 推荐的 vite.config.ts

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },

  build: {
    target: 'baseline-widely-available',
    sourcemap: false,
    chunkSizeWarningLimit: 500,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
        },
      },
    },
  },

  optimizeDeps: {
    include: ['react', 'react-dom'],
  },

  server: {
    port: 3000,
    hmr: {
      overlay: true,
    },
  },
})
```

### 基于路由的代码分割

```typescript
import { lazy, Suspense } from 'react'

const Home = lazy(() => import('./pages/Home'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Settings = lazy(() => import('./pages/Settings'))

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      {/* 路由配置 */}
    </Suspense>
  )
}
```

### 环境变量

```typescript
// src/vite-env.d.ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_APP_TITLE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

## 如何使用

查阅单个规则文件以获取详细说明和代码示例：

```
rules/build-manual-chunks.md
rules/split-route-lazy.md
rules/env-vite-prefix.md
```

## 参考

- [Vite 文档](https://vite.dev)
- [React 文档](https://react.dev)
- [Rollup 文档](https://rollupjs.org)

## 完整编译文档

包含所有规则展开的完整指南：`AGENTS.md`
