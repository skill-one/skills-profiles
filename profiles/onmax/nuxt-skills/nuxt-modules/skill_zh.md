# Nuxt 模块开发

创建扩展框架功能的 Nuxt 模块的指南。

**相关技能：** `nuxt`（基础）、`vue`（运行时模式）

## 快速入门

```bash
npx nuxi init -t module my-module
cd my-module && npm install
npm run dev        # 启动游乐场
npm run dev:build  # 监视模式下构建
npm run test       # 运行测试
```

## 可用指南

- **[references/development.md](references/development.md)** - 模块结构、defineNuxtModule、Kit 工具、钩子
- **[references/testing-and-publishing.md](references/testing-and-publishing.md)** - E2E 测试、最佳实践、发布、发布
- **[references/ci-workflows.md](references/ci-workflows.md)** - 复制粘贴 CI/CD 工作流模板

## 文件加载

**根据您的任务考虑加载以下参考文件：**

- [ ] [references/development.md](references/development.md) - 如果构建模块功能、使用 defineNuxtModule 或使用 Kit 工具
- [ ] [references/testing-and-publishing.md](references/testing-and-publishing.md) - 如果编写 E2E 测试、发布到 npm 或遵循最佳实践
- [ ] [references/ci-workflows.md](references/ci-workflows.md) - 如果为您的模块设置 CI/CD 工作流

**不要一次性加载所有文件。** 仅加载与您当前任务相关的文件。

## 模块类型

| 类型      | 位置         | 用例                         |
| --------- | ------------ | ---------------------------- |
| 已发布    | npm 包      | `@nuxtjs/`、`nuxt-` 分发 |
| 本地     | `modules/` 目录 | 项目特定扩展                |
| 内联     | `nuxt.config.ts` | 简单一次性钩子              |

## 项目结构

```
my-module/
├── src/
│   ├── module.ts           # 入口点
│   └── runtime/            # 注入到用户的应用中
│       ├── components/
│       ├── composables/
│       ├── plugins/
│       └── server/
├── playground/             # 开发测试
└── test/fixtures/          # E2E 测试
```

## 资源

- [模块指南](https://nuxt.com/docs/guide/going-further/modules)
- [Nuxt Kit](https://nuxt.com/docs/api/kit)
- [模块启动器](https://github.com/nuxt/starter/tree/module)
