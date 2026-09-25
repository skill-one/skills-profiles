# 第一步：安装 effect

使用用户偏好的包管理器：

```
pnpm add effect@rc
```

如果在 monorepo 中，请将其作为开发依赖项安装在根目录，以便可以从 `node_modules/effect/src` 访问源代码。

```
pnpm add -D effect@rc
```

# 第二步：更新 AGENTS.md / CLAUDE.md

确保代理指令包含以下内容：

```md
# 了解更多关于 Effect

此仓库使用 Effect Typescript 库。

在编写任何 Effect 代码之前，首先完整阅读 `node_modules/effect/AGENTS.md`，并在需要时遵循文件中的链接。

如果你需要了解指南未涵盖的特定 Effect api 和概念，请搜索 `node_modules/effect/src` 中的源代码。
