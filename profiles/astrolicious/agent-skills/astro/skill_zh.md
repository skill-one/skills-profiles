# Astro 使用指南

**请始终查阅 [docs.astro.build](https://docs.astro.build) 获取代码示例和最新 API。**

Astro 是用于内容驱动型网站的 Web 框架。

---

## 快速参考

### 文件位置
CLI 会搜索 `./` 目录下的 `astro.config.js`、`astro.config.mjs`、`astro.config.cjs` 和 `astro.config.ts`。使用 `--config` 参数指定自定义路径。

### CLI 命令

- `npx astro dev` - 启动开发服务器。
- `npx astro build` - 构建项目并将其写入磁盘。
- `npx astro check` - 检查项目中的错误。
- `npx astro add` - 添加集成。
- `npx astro sync` - 为所有 Astro 模块生成 TypeScript 类型。

**添加或修改插件后请重新运行。**

### 项目结构

参考 [项目结构文档](https://docs.astro.build/en/basics/project-structure)。

- `src/*` - 项目源代码（组件、页面、样式、图片等）。
- `src/pages` - **必需。** 定义所有页面和路由。
- `src/components` - 组件（约定，非必需）。
- `src/layouts` - 布局组件（约定，非必需）。
- `src/styles` - CSS/Sass 文件（约定，非必需）。
- `public/*` - 非代码、未处理的资源（字体、图标等）；按原样复制到构建输出。
- `package.json` - 项目清单。
- `astro.config.{js,mjs,cjs,ts}` - Astro 配置文件。（推荐）
- `tsconfig.json` - TypeScript 配置文件。（推荐）

---

## 核心配置选项

| 选项 | 备注 |
|------|------|
| `site` | 您的最终部署 URL。用于生成站点地图和规范 URL。 |

### 示例 `astro.config.ts`

```ts
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://example.com',
});
```

---

## 常见工作流

### 创建基本页面

在 `src/pages/` 中添加文件——文件名将成为路由：

```astro
---
// src/pages/index.astro
const title = 'Hello, Astro!';
---
<html>
  <head><title>{title}</title></head>
  <body>
    <h1>{title}</h1>
  </body>
</html>
```

### 创建组件

```astro
---
// src/components/Card.astro
const { title, body } = Astro.props;
---
<div class="card">
  <h2>{title}</h2>
  <p>{body}</p>
</div>
```

### 使用适配器部署

1. 添加适配器：`npx astro add vercel --yes`（或 `node`、`cloudflare`、`netlify`）
2. 运行 `npx astro check` 在构建前捕获类型和配置错误。
3. 运行 `npx astro build` 生成部署工件。
4. 验证构建输出目录（例如 `dist/`）是否存在且非空，然后继续。
5. 按照适配器文档进行部署。

---

## 适配器

使用构建适配器部署到您喜欢的服务器、无服务器或边缘主机。使用适配器可在您的 Astro 项目中启用按需渲染。

**使用 `astro add` 添加 [Node.js](https://docs.astro.build/en/guides/integrations-guide/node) 适配器：**
```
npx astro add node --yes
```

**使用 `astro add` 添加 [Cloudflare](https://docs.astro.build/en/guides/integrations-guide/cloudflare) 适配器：**
```
npx astro add cloudflare --yes
```

**使用 `astro add` 添加 [Netlify](https://docs.astro.build/en/guides/integrations-guide/netlify) 适配器：**
```
npx astro add netlify --yes
```

**使用 `astro add` 添加 [Vercel](https://docs.astro.build/en/guides/integrations-guide/vercel) 适配器：**
```
npx astro add vercel --yes
```

[其他社区适配器](https://astro.build/integrations/2/?search=&categories%5B%5D=adapters)

## 资源

- [文档](https://docs.astro.build)
- [配置参考](https://docs.astro.build/en/reference/configuration-reference/)
- [llms.txt](https://docs.astro.build/llms.txt)
- [GitHub](https://github.com/withastro/astro)
