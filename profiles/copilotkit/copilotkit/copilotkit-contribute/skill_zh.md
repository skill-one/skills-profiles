# 为 CopilotKit 贡献

> **重要提示：** CopilotKit 的内部 v2 包使用 `@copilotkit/*` 命名空间。用户安装的公共 API 也是 `@copilotkit/*`。在贡献时，你将使用 `@copilotkit/*` 源代码，但用户永远不会看到这个命名空间。

## 活动文档 (MCP)

此插件包含一个 MCP 服务器 (`copilotkit-docs`)，它提供 `search-docs` 和 `search-code` 工具，用于查询活动 CopilotKit 文档和源代码。

- **Claude 代码：** 由插件的 `.mcp.json` 自动配置——无需设置。
- **Codex：** 需要手动配置。请参阅 [copilotkit-debug 技能](../copilotkit-debug/SKILL.md#mcp-setup) 的设置说明。

## 工作流程

1. **Fork 并克隆** CopilotKit/CopilotKit 仓库。
2. 使用 `pnpm install` **安装依赖项**（需要 pnpm v9.x 和 Node 20+）。
3. 使用 `pnpm build` **一次性构建** 以启动所有包。
4. 使用命名约定创建分支：`feat/<ISSUE>-<name>`、`fix/<ISSUE>-<name>` 或 `docs/<ISSUE>-<name>`。
5. 使用 `pnpm dev` **开发**（监视所有包），或使用 `nx run @copilotkit/<pkg>:dev` 针对特定包。
6. 使用 `nx run @copilotkit/<pkg>:test` **编写和运行测试**。所有 v2 包使用 Vitest。
7. 使用 `pnpm run lint --fix && pnpm run format` **检查并格式化**。
8. 使用常规提交格式提交：`<type>(<scope>): <subject>`（由 commitlint 强制）。
9. 推送到 `main` 分支并**打开 PR**。CI 构建所有包，并通过 pkg-pr-new 发布预览包。

## 打开 PR 前的准备

- 对于任何重大工作，首先联系维护者（提交问题或在 Discord 上询问）。
- 运行 `pnpm run test` 以验证所有测试通过。
- 运行 `pnpm run build` 以验证完整构建成功。
- 运行 `pnpm run check-prettier` 以验证格式化。
- 确保提交信息遵循 `<type>(<scope>): <subject>` 格式。

## 快速参考

| 任务                     | 命令                        |
| ------------------------ | ------------------------------ |
| 安装依赖项               | `pnpm install`                 |
| 构建所有包               | `pnpm build`                   |
| 开发模式（全部）         | `pnpm dev`                     |
| 开发模式（仅 v2）       | `pnpm dev:next`                |
| 运行所有测试             | `pnpm run test`                |
| 仅运行 v2 测试          | `pnpm test:next`               |
| 运行单个包测试           | `nx run @copilotkit/core:test` |
| 带覆盖运行测试           | `pnpm run test:coverage`       |
| 检查                     | `pnpm run lint`                |
| 格式化                   | `pnpm run format`              |
| 检查格式化               | `pnpm run check-prettier`      |
| 类型检查                 | `pnpm run check-types`         |
| 包质量检查               | `pnpm run check:packages`      |
| 依赖关系图               | `pnpm run graph`               |

## 关键架构要点

- V2 (`@copilotkit/*`) 是实际实现。V1 (`@copilotkit/*`) 封装了 V2。
- 新功能始终放在 `packages/v2/` 下的 V2 包中。
- 前端和运行时之间的通信使用 AG-UI 协议（基于 SSE 的事件）。
- 单一仓库使用 Nx 进行任务编排和 pnpm 工作区。

## 参考文档

- [贡献指南](references/contribution-guide.md) — 完整的入职演练
- [仓库结构](references/repo-structure.md) — 包布局和架构
- [测试指南](references/testing-guide.md) — Vitest 设置、运行测试、覆盖率
- [PR 指南](references/pr-guidelines.md) — CI 检查、审查流程、预期
