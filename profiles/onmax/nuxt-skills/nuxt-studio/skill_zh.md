# Nuxt Studio

Nuxt Studio 负责内容编辑和发布。Nuxt Content 负责集合、查询、解析和渲染。

## 工作流程

1. 检查已安装的 `nuxt-studio` 和 `@nuxt/content` 版本、部署模式、仓库提供者和身份验证提供者。当编辑器路由、Git 目标和登录回调都指向同一个部署时，即表示设置已完成。
2. 打开下方最匹配的指南，并将集合/模式更改保持在 `nuxt-content` 边界内。
3. 将本地编辑与文件系统进行验证，然后在支持 SSR 的部署上进行生产登录和一次发布周期验证。当提交到达配置的分支并且重建的站点展示内容时，工作即完成。

## 路由

| 任务                                                                                      | 打开                                         |
| ----------------------------------------------------------------------------------------- | -------------------------------------------- |
| 安装、仓库设置、OAuth/自定义认证、编辑器过滤器或环境变量                               | [配置](references/configuration.md)         |
| 可视化/MDC 编辑、模式表单、草稿、媒体或 AI 辅助                                         | [实时编辑](references/live-editing.md)       |
| SSR 部署、Git 发布、分支策略、冲突或单仓库                                               | [部署](references/deployment.md)            |
| 集合、验证器、查询、钩子或渲染                                                         | `nuxt-content` 技能                       |

## 基线

```bash
npx nuxt module add nuxt-studio
```

```ts
export default defineNuxtConfig({
  modules: ['@nuxt/content', 'nuxt-studio'],
  studio: {
    repository: {
      provider: 'github',
      owner: 'your-org',
      repo: 'your-repo',
      branch: 'main',
    },
  },
})
```

```bash
NUXT_STUDIO_AUTH_GITHUB_CLIENT_ID=<client-id>
NUXT_STUDIO_AUTH_GITHUB_CLIENT_SECRET=<client-secret>
```

Studio 默认运行在 `/_studio` 下。支持的 CI 提供者可以推断仓库元数据，但身份验证凭证仍然是明确的部署密钥。
