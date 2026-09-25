# Vercel 部署

立即将任何项目部署到 Vercel。无需身份验证。

## 工作原理

1. 将项目打包成 tarball（排除 `node_modules` 和 `.git`）
2. 自动从 `package.json` 检测框架
3. 上传到部署服务
4. 返回 **预览 URL**（在线站点）和 **认领 URL**（转移到您的 Vercel 账户）

## 使用方法

```bash
bash /mnt/skills/public/vercel-deploy/scripts/deploy.sh [路径]
```

**参数：**
- `路径` - 要部署的目录，或 `.tgz` 文件（默认为当前目录）

**示例：**

```bash
# 部署当前目录
bash /mnt/skills/public/vercel-deploy/scripts/deploy.sh

# 部署特定项目
bash /mnt/skills/public/vercel-deploy/scripts/deploy.sh /path/to/project

# 部署现有 tarball
bash /mnt/skills/public/vercel-deploy/scripts/deploy.sh /path/to/project.tgz
```

## 输出

```
正在准备部署...
检测到框架：nextjs
正在创建部署包...
正在部署...
✓ 部署成功！

预览 URL：https://skill-deploy-abc123.vercel.app
认领 URL：   https://vercel.com/claim-deployment?code=...
```

该脚本还会将 JSON 输出到标准输出，用于程序化使用：

```json
{
  "previewUrl": "https://skill-deploy-abc123.vercel.app",
  "claimUrl": "https://vercel.com/claim-deployment?code=...",
  "deploymentId": "dpl_...",
  "projectId": "prj_..."
}
```

## 框架检测

该脚本自动从 `package.json` 检测框架。支持的框架包括：

- **React**：Next.js、Gatsby、Create React App、Remix、React Router
- **Vue**：Nuxt、Vitepress、Vuepress、Gridsome
- **Svelte**：SvelteKit、Svelte、Sapper
- **其他前端**：Astro、Solid Start、Angular、Ember、Preact、Docusaurus
- **后端**：Express、Hono、Fastify、NestJS、Elysia、h3、Nitro
- **构建工具**：Vite、Parcel
- **以及其他**：Blitz、Hydrogen、RedwoodJS、Storybook、Sanity 等

对于没有 `package.json` 的静态 HTML 项目，框架将被设置为 `null`。

## 静态 HTML 项目

对于没有 `package.json` 的项目：
- 如果存在一个不是 `index.html` 命名的 `.html` 文件，它将自动重命名
- 这确保页面在根 URL（`/`）上被提供

## 向用户展示结果

始终显示两个 URL：

```
✓ 部署成功！

- [预览 URL](https://skill-deploy-abc123.vercel.app)
- [认领 URL](https://vercel.com/claim-deployment?code=...)

在预览 URL 上查看您的站点。
要将此部署转移到您的 Vercel 账户，请访问认领 URL。
```

## 故障排除

### 网络限制错误

如果由于网络限制（在 claude.ai 上常见）导致部署失败，请告知用户：

```
由于网络限制导致部署失败。要修复此问题：

1. 访问 https://claude.ai/settings/capabilities
2. 将 *.vercel.com 添加到允许的域名
3. 再次尝试部署
```
