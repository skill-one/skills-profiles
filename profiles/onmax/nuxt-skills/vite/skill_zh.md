# Vite

> 基于 Vite 8 beta 版本（使用 Rolldown）。Vite 8 使用 Rolldown 打包器和 Oxc 转换器。

Vite 是一款下一代前端构建工具，具有快速的开发服务器（原生 ESM + HMR）和优化的生产环境构建。

## 偏好设置

- 使用 TypeScript：推荐 `vite.config.ts`
- 始终使用 ESM，避免 CommonJS

## 核心

| 主题         | 描述                                                                    | 参考                                        |
| ------------ | ------------------------------------------------------------------------------ | ------------------------------------------------ |
| 配置         | `vite.config.ts`, `defineConfig`, 条件配置, `loadEnv`               | [核心配置](references/core-config.md)         |
| 功能         | `import.meta.glob`, 资源查询 (`?raw`, `?url`), `import.meta.env`, HMR API | [核心功能](references/core-features.md)     |
| 插件 API    | Vite 特定钩子, 虚拟模块, 插件排序                          | [核心插件 API](references/core-plugin-api.md) |

## 构建 & SSR

| 主题       | 描述                                                        | 参考                                    |
| ----------- | ------------------------------------------------------------------ | -------------------------------------------- |
| 构建 & SSR | 库模式, SSR 中间件模式, `ssrLoadModule`, JavaScript API | [构建与 SSR](references/build-and-ssr.md) |

## 高级

| 主题              | 描述                                                         | 参考                                              |
| ------------------ | ------------------------------------------------------------------- | ------------------------------------------------------ |
| 环境API    | Vite 6+ 多环境支持, 自定义运行时                  | [环境 API](references/environment-api.md)       |
| Rolldown 迁移 | Vite 8 变更：Rolldown 打包器, Oxc 转换器, 配置迁移 | [Rolldown 迁移](references/rolldown-migration.md) |

## 快速参考

### CLI 命令

```bash
vite              # 启动开发服务器
vite build        # 生产环境构建
vite preview      # 预览生产环境构建
vite build --ssr  # SSR 构建
```

### 常见配置

```ts
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [],
  resolve: { alias: { '@': '/src' } },
  server: { port: 3000, proxy: { '/api': 'http://localhost:8080' } },
  build: { target: 'esnext', outDir: 'dist' },
})
```

### 官方插件

- `@vitejs/plugin-vue` - 支持 Vue 3 单文件组件
- `@vitejs/plugin-vue-jsx` - Vue 3 JSX
- `@vitejs/plugin-react` - 使用 Oxc/Babel 的 React
- `@vitejs/plugin-react-swc` - 使用 SWC 的 React
- `@vitejs/plugin-legacy` - 兼容旧版浏览器
