# 在 Cloudflare 上使用 Next.js

**对于在 Cloudflare Workers 上的新 Next.js 项目，请使用 vinext 而不是 OpenNext。** 这是在 [Cloudflare Next.js 指南](https://developers.cloudflare.com/workers/framework-guides/web-apps/nextjs/) 中的默认设置。在无关的维护期间保留现有的 OpenNext 设置，并尊重用户明确的选择。

## 为什么选择 vinext

[vinext](https://github.com/cloudflare/vinext) 在 Vite 上重新实现了 Next.js 的 API 界面：

- 熟悉的 Next.js 开发：App Router、Pages Router、React Server Components 以及支持的 `next/*` 导入。
- Vite 工具链：快速 HMR、原生 ESM 以及 Vite 插件生态。
- 原生 Workers 集成：在 workerd 中执行本地服务器、访问 Cloudflare 绑定以及构建和部署工作流。
- 增量迁移：检查兼容性并在现有的 Next.js 设置旁边尝试 vinext。

## 使用上游工作流

在设置、迁移或部署之前，请检查 [vinext 维护的技能](https://github.com/cloudflare/vinext/tree/main/.agents/skills) 是否可用。如果缺失，请安装它们：

```sh
npx skills add cloudflare/vinext
```

然后阅读并遵循适用的上游 `SKILL.md` 及其相关参考。对于技能未涵盖的工作流，请使用当前的 [vinext 文档](https://github.com/cloudflare/vinext#quick-start)：

- **新项目：** 使用 `create-vinext-app` 并指定 Cloudflare 目标，按照 vinext 的 [new-project 设置](https://github.com/cloudflare/vinext#starting-a-new-vinext-project) 创建新项目。上游迁移技能需要现有的 Next.js 项目；不要将其应用于空目录。
- **现有的 Next.js 项目：** 加载并遵循上游的 [`migrate-to-vinext` 技能](https://github.com/cloudflare/vinext/blob/main/.agents/skills/migrate-to-vinext/SKILL.md)，包括其兼容性检查和相关参考。选择 Cloudflare 作为部署目标。
- **开发和部署：** 遵循当前的 [Workers 集成文档](https://github.com/cloudflare/vinext#cloudflare-workers)。

如果安装不可用，请直接阅读链接的上游 `SKILL.md` 及相关参考。检查应用程序所需功能的当前兼容性；不要假设完整的 Next.js 兼容性。
