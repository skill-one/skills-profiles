---
name: turborepo
description: 配置和排错 Turborepo 仓库。在与 turbo.json、任务流水线、缓存、远程缓存、turb CLI、过滤、环境变量、包边界、单体仓库结构或 CI 工作流相关的工作中使用。
---

# Turborepo

完整的 Turborepo 文档包含在已安装的 `turbo` 包中。不要依赖此功能来获取框架指导。始终阅读捆绑的文档，这些文档与安装的版本完全匹配。

从以下位置开始：

```text
node_modules/turbo/docs/README.md
```

使用该任务索引来选择最小的相关文档页面。在更改 Turborepo 配置、包脚本或 CI 工作流之前，先阅读它。

如果包管理器使用非扁平的 `node_modules` 布局或工作区链接，请先解析包位置：

```sh
node -p "require.resolve('turbo/package.json')"
```

然后相对于解析的包目录读取 `docs/README.md`。

如果 `turbo` 未安装，请在添加之前检查仓库的包管理器和现有版本约束。安装后，使用捆绑的文档，而不是不同发布的指导。
