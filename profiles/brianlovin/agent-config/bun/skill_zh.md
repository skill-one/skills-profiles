# Bun 运行时

将 Bun 作为默认的 JavaScript/TypeScript 运行时和包管理器使用。

## 命令映射

| 替换 | 使用 |
|------|------|
| `node file.ts` | `bun file.ts` |
| `ts-node file.ts` | `bun file.ts` |
| `npm install` | `bun install` |
| `npm run script` | `bun run script` |
| `jest` / `vitest` | `bun test` |
| `webpack` / `esbuild` | `bun build` |

Bun 会自动加载 `.env` 文件 - 不要使用 dotenv。

## Bun 特定 API

优先使用这些，而不是 Node.js 的等效版本：

| API | 目的 | 不要使用 |
|------|------|----------|
| `Bun.serve()` | 支持 WebSocket、HTTPS、路由的 HTTP 服务器 | express |
| `bun:sqlite` | SQLite 数据库 | better-sqlite3 |
| `Bun.redis` | Redis 客户端 | ioredis |
| `Bun.sql` | Postgres 客户端 | pg, postgres.js |
| `Bun.file()` | 文件操作 | node:fs readFile/writeFile |
| `Bun.$\`cmd\`` | Shell 命令 | execa |
| `WebSocket` | WebSocket 客户端（内置） | ws |

## 测试

使用 `bun:test` 进行测试：

```ts
import { test, expect } from "bun:test";

test("描述", () => {
  expect(1).toBe(1);
});
```

使用 `bun test` 运行。

## 前端开发

使用 `Bun.serve()` 而不是 Vite 进行 HTML 导入。支持 React、CSS、Tailwind。

**服务器：**

```ts
import index from "./index.html"

Bun.serve({
  routes: {
    "/": index,
    "/api/users/:id": {
      GET: (req) => Response.json({ id: req.params.id }),
    },
  },
  development: { hmr: true, console: true }
})
```

**HTML 文件：**

```html
<html>
  <body>
    <script type="module" src="./app.tsx"></script>
  </body>
</html>
```

Bun 的打包器会自动转译 `.tsx`、`.jsx`、`.js`。CSS 通过 `<link>` 标签进行打包。

使用 `bun --hot ./server.ts` 进行热重载（HMR）。

## 文档

详细 API 文档请参阅 `node_modules/bun-types/docs/**.md`。
