pnpm 是一个快速、节省磁盘空间的包管理器。它使用内容寻址存储来跨机器上所有项目消除重复的包，并默认强制执行严格的依赖解析，防止幽灵依赖。

**配置模型（重要）：** pnpm 设置现在存储在 `pnpm-workspace.yaml`（以及全局的 `config.yaml`）中，并使用 **camelCase** 键。`.npmrc` 仅用于身份验证/注册中心凭证，`package.json` 中的 `pnpm` 字段不再读取。在 pnpm 项目中工作时，请检查 `pnpm-workspace.yaml` 获取设置/工作区结构，并仅检查 `.npmrc` 获取身份验证信息。始终在 CI 中使用 `--frozen-lockfile`（或 `pnpm ci`）。

> 本指南基于 pnpm 10.x 版本生成，时间为 2026-06-22。它还涵盖了 v11 版本的行为变化（配置拆分、隔离的全局包、`allowBuilds`、`pmOnFail`、全局虚拟存储）等当前文档中描述的内容。

## 核心

| 主题 | 描述 | 参考 |
|------|------|------|
| CLI 命令 | install/add/remove/update、run、dlx/pnx、workspace、runtime、发布（版本、查看、sbom、暂存） | [core-cli](references/core-cli.md) |
| 配置 | pnpm-workspace.yaml 设置（camelCase）、全局 config.yaml、packageConfigs、.npmrc 身份验证 | [core-config](references/core-config.md) |
| 工作区 | 单体仓库支持：过滤、工作区协议、共享锁文件、packageConfigs | [core-workspaces](references/core-workspaces.md) |
| 存储库 | 内容寻址存储库、虚拟存储库、Node 链接模式、冻结/只读存储库 | [core-store](references/core-store.md) |

## 功能

| 主题 | 描述 | 参考 |
|------|------|------|
| 目录 | 集中化依赖版本；catalogMode、catalog: in 覆盖 | [features-catalogs](references/features-catalogs.md) |
| 覆盖 | 强制版本（包括传递和同伴依赖）；packageExtensions | [features-overrides](references/features-overrides.md) |
| 补丁 | 修改第三方包；pnpm-workspace.yaml 中的 patchedDependencies | [features-patches](references/features-patches.md) |
| 别名 | 使用自定义名称安装（npm:）和注册中心别名（namedRegistries） | [features-aliases](references/features-aliases.md) |
| 钩子 | .pnpmfile.mjs 钩子（readPackage、updateConfig、beforePacking）、finders、resolvers/fetchers | [features-hooks](references/features-hooks.md) |
| 同伴依赖 | 自动安装、严格模式、规则、dedupePeers、peers 检查 | [features-peer-deps](references/features-peer-deps.md) |
| 配置依赖 | 通过 configDependencies 在多个仓库间共享钩子/设置/目录/补丁 | [features-config-dependencies](references/features-config-dependencies.md) |
| 全局虚拟存储库 | 共享 node_modules、git-worktree 多代理设置、隔离的全局包 | [features-global-virtual-store](references/features-global-virtual-store.md) |
| 供应链安全 | 构建批准（allowBuilds）、最低发布年龄、信任策略、锁文件完整性 | [features-supply-chain-security](references/features-supply-chain-security.md) |

## 最佳实践

| 主题 | 描述 | 参考 |
|------|------|------|
| CI/CD 设置 | GitHub Actions、GitLab、Docker、pnpm ci、存储库缓存、冻结锁文件 | [best-practices-ci](references/best-practices-ci.md) |
| 迁移 | npm/Yarn → pnpm、幽灵依赖以及 pnpm v10 → v11 配置迁移 | [best-practices-migration](references/best-practices-migration.md) |
| 性能 | 安装优化、allowBuilds、全局虚拟存储库、工作区并行化 | [best-practices-performance](references/best-practices-performance.md) |
