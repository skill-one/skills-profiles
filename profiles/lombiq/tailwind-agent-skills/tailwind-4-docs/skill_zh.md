# Tailwind 4 文档

## 概述

使用此技能来导航本地同步的 Tailwind CSS v4 文档快照，并使用官方指南回答开发、配置、迁移、实现、重构和审查问题。

文档快照不随此技能一起打包，因为上游存储库是源码开放的，但不是开源的。用户必须自行初始化快照，并对遵守上游许可负责。

## 快速入门

1. 检查文档快照是否已初始化（`references/docs/` 和 `references/docs-index.tsx` 是否存在）。
2. 如果快照缺失或比一周旧，请停止并要求在继续之前运行“初始化”中的初始化步骤。在快照初始化之前不要回答用户的问题。
3. 确定主题（实用工具、变体、配置、迁移、兼容性、实现、重构、审查）。
4. 在 `references/docs-index.tsx` 中找到匹配的文档。
5. 仅从 `references/docs/` 加载相关文件。
6. 对于实现、重构或审查任务，还加载 `references/engineering-playbook.md`。
7. 应用指南，并指出任何破坏性变更或限制。

## 初始化（每安装一次都需要执行一次）

运行同步脚本以将 Tailwind 文档下载到本地。这需要网络访问、git 和 Python 3：

```
python skills/tailwind-4-docs/scripts/sync_tailwind_docs.py --accept-docs-license
```

这会从 `tailwindlabs/tailwindcss.com` 拉取内容。该存储库是源码开放的，明确不是开源的，因此用户必须在下载前接受其许可，并将快照保存在本地。

如果您无法运行工具或没有网络访问权限，请要求用户在终端中运行上述确切命令，然后在 `references/docs/` 和 `references/docs-index.tsx` 存在时继续。

如果快照缺失或比一周旧，您必须要求运行命令或要求用户运行它。在快照初始化或刷新之前不要进行 Tailwind 指导。

如果初始化被阻止（没有网络或没有写入权限），请使用 `references/gotchas.md` 作为有限的备用方案，并要求用户查阅官方文档。对于实现、重构或审查任务，`references/engineering-playbook.md` 也可以作为有限的备用方案。

## 参考资料映射

- `references/docs/` 是本地生成的，包含 Tailwind v4 MDX 文档快照。
- `references/docs-index.tsx` 是本地生成的，包含文档侧边栏使用的分类和 slug 映射。
- `references/docs-source.txt` 捕获上游存储库、提交和快照日期（或报告初始化挂起）。
- `references/engineering-playbook.md` 是面向代理的实现、重构和审查指南。
- `references/gotchas.md` 提供对 v4 迁移常见陷阱的快速扫描。

## MDX 处理

- 将 `export const title` 和 `export const description` 视为元数据。
- 将 JSX 调用如 `<TipInfo>` 或 `<TipBad>` 视为指南文本。

## 常见入口点

- 迁移：`references/docs/upgrade-guide.mdx`，`references/docs/compatibility.mdx`。
- 实现/重构/审查：`references/engineering-playbook.md`。
- Gotchas 概述：`references/gotchas.md`。
- 配置和指令：`references/docs/functions-and-directives.mdx`，`references/docs/adding-custom-styles.mdx`，`references/docs/theme.mdx`。
- 变体和响应式模式：`references/docs/hover-focus-and-other-states.mdx`，`references/docs/responsive-design.mdx`。
- 核心行为：`references/docs/preflight.mdx`，`references/docs/detecting-classes-in-source-files.mdx`。

## 迁移清单

从 v3 升级到 v4 时，始终在文档中确认以下几点：

- 浏览器支持和兼容性预期。
- 工具变更：`@tailwindcss/postcss`，`@tailwindcss/cli`，`@tailwindcss/vite`。
- 导入语法：`@import "tailwindcss"` 替换 `@tailwind` 指令。
- 实用工具重命名/移除、前缀格式和重要修饰符位置。
- 变体、转换和任意值语法的变更。

## 更新工作流

运行 `scripts/sync_tailwind_docs.py` 以刷新快照。如果您已经有了 `tailwindlabs/tailwindcss.com` 的本地克隆，请使用 `--local-repo` 以加快同步速度。始终传递 `--accept-docs-license`。

---
