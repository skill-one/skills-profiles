# Cloudflare Worker Builder

根据简要描述快速搭建一个可运行的 Cloudflare Worker 项目。生成的项目包含 Hono 路由、Vite 开发服务器和静态资源。

## 工作流程

### 第一步：理解项目

通过询问项目信息来选择合适的绑定和结构：

- 应用做什么？（仅 API、SPA + API、落地页）
- 数据存储方式？（D1 数据库、R2 文件、KV 缓存、无）
- 是否需要认证？（Clerk、better-auth、无）
- 自定义域名还是 workers.dev 子域名？

类似 "带数据库的待办事项应用" 的简短描述就足够继续。

### 第二步：搭建项目

```bash
npm create cloudflare@latest my-worker -- --type hello-world --ts --git --deploy false --framework none
cd my-worker
npm install hono
npm install -D @cloudflare/vite-plugin vite
```

从本技能的 `assets/` 目录复制并自定义资源文件：
- `wrangler.jsonc` — Worker 配置
- `vite.config.ts` — Vite + Cloudflare 插件
- `src/index.ts` — 带静态资源回退的 Hono 应用
- `package.json` — 脚本和依赖
- `tsconfig.json` — TypeScript 配置
- `public/index.html` — SPA 入口

### 第三步：配置绑定

根据项目需求在 `wrangler.jsonc` 中添加绑定。Wrangler 4.45+ 在首次部署时自动配置资源 — 始终指定明确名称：

```jsonc
{
  "name": "my-worker",
  "main": "src/index.ts",
  "compatibility_date": "2025-11-11",
  "assets": {
    "directory": "./public/",
    "binding": "ASSETS",
    "not_found_handling": "single-page-application",
    "run_worker_first": ["/api/*"]
  },
  // 根据需要添加：
  "d1_databases": [{ "binding": "DB", "database_name": "my-app-db" }],
  "r2_buckets": [{ "binding": "STORAGE", "bucket_name": "my-app-files" }],
  "kv_namespaces": [{ "binding": "CACHE", "title": "my-app-cache" }]
}
```

### 第四步：部署

```bash
npm run dev           # 本地开发 http://localhost:8787
wrangler deploy       # 生产部署
```

---

## 关键模式

### 导出语法

```typescript
// 正确 — 使用此模式
export default app

// 错误 — 会引发 "Cannot read properties of undefined"
export default { fetch: app.fetch }
```

来源：[honojs/hono #3955](https://github.com/honojs/hono/issues/3955)

### 静态资源 + API 路由

没有 `run_worker_first` 时，SPA 回退会拦截 API 路由并返回 `index.html` 而不是 JSON：

```jsonc
"assets": {
  "not_found_handling": "single-page-application",
  "run_worker_first": ["/api/*"]  // 关键
}
```

来源：[workers-sdk #8879](https://github.com/cloudflare/workers-sdk/issues/8879)

### Vite 配置

```typescript
import { defineConfig } from 'vite'
import { cloudflare } from '@cloudflare/vite-plugin'

export default defineConfig({ plugins: [cloudflare()] })
```

始终在 `wrangler.jsonc` 中设置 `main` 字段 — Vite 插件需要它。

### 定时/Cron 处理器

添加 Cron 触发器时，切换到显式导出：

```typescript
export default {
  fetch: app.fetch,
  scheduled: async (event, env, ctx) => { /* ... */ }
}
```

---

## 参考文件

阅读以下文件进行详细故障排除：

- `references/common-issues.md` — 10 个带来源和修复方案的记录问题
- `references/architecture.md` — 路由优先级、缓存、Workers RPC
- `references/deployment.md` — CI/CD、自动配置、渐进式发布
