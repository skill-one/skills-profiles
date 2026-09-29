---
name: pnpm
description: 一个具有严格依赖解析的 Node.js 包管理器。在执行 pnpm 特定命令、通过 pnpm-workspace.yaml 配置工作区，或使用目录、补丁、覆盖、配置依赖项或全局虚拟存储管理依赖项时使用。
---

pnpm 是一个快速、节省磁盘空间的包管理器。它使用内容寻址存储来跨机器上所有项目消除包的重复，并默认强制执行严格的依赖解析，防止幽灵依赖。

**pnpm v12 是对 v11 的 Rust 重写**：稳定，并保留 v11 的命令、标志、设置和锁文件格式——因此这里的大多数指南都适用于两者。v12 的一些行为有所不同（git 依赖通过 HTTPS 解析、项目感知的全局二进制文件、其他包管理器、Linux 上 `packageImportMethod: auto` 首先使用硬链接、`--resolution-only` 已移除）——请参阅最佳实践迁移。

**配置模型（重要）**：pnpm 设置存储在 `pnpm-workspace.yaml`（以及全局的 `config.yaml`）中，使用 **camelCase** 键。`.npmrc` 仅用于身份验证/注册中心凭证，`package.json` 中的 `pnpm` 字段不再读取。在 pnpm 项目中工作时，检查 `pnpm-workspace.yaml` 以获取设置/工作区结构，并仅检查 `.npmrc` 以获取身份验证。在 CI 中始终使用 `--frozen-lockfile`（或 `pnpm ci`）。

> 本指南基于 pnpm 12.x 版本，生成于 2026-09-25。它涵盖了 v11+v12 行为（配置拆分、隔离的全局包、`allowBuilds`、`pmOnFail`、全局虚拟存储、原生发布管理、工作区任务编排以及实验性 Python/Cargo 支持）的描述，这些内容在当前文档中都有说明。

## 核心

| 主题 | 描述 | 参考 |
|------|------|------|
| CLI 命令 | install/add/remove/update、run、dlx/pnx、工作区、运行时、发布（版本、查看、sbom、暂存） | [core-cli](references/core-cli.md) |
| 配置 | pnpm-workspace.yaml 设置（camelCase）、全局 config.yaml、packageConfigs、.npmrc 身份验证 | [core-config](references/core-config.md) |
| 工作区 | 单体仓库支持：过滤、工作区协议、共享锁文件、packageConfigs | [core-workspaces](references/core-workspaces.md) |
| 存储库 | 内容寻址存储库、虚拟存储库、node 链接模式、冻结/只读存储库 | [core-store](references/core-store.md) |

## 功能

| 主题 | 描述 | 参考 |
|------|------|------|
| 目录 | 集中化依赖版本；catalogMode、catalog: 在覆盖中 | [features-catalogs](references/features-catalogs.md) |
| 覆盖 | 强制版本（包括传递和同伴依赖）；packageExtensions | [features-overrides](references/features-overrides.md) |
| 补丁 | 修改第三方包；pnpm-workspace.yaml 中的 patchedDependencies | [features-patches](references/features-patches.md) |
| 别名 | 使用自定义名称安装（npm:）和注册中心别名（namedRegistries） | [features-aliases](references/features-aliases.md) |
| 钩子 | .pnpmfile.mjs 钩子（readPackage、updateConfig、beforePacking）、查找器、解析器/获取器 | [features-hooks](references/features-hooks.md) |
| 同伴依赖 | 自动安装、严格模式、规则、dedupePeers、peers 检查 | [features-peer-deps](references/features-peer-deps.md) |
| 配置依赖 | 通过 configDependencies 在仓库间共享钩子/设置/目录/补丁 | [features-config-dependencies](references/features-config-dependencies.md) |
| 全局虚拟存储和遮蔽层 | 共享 node_modules、git-worktree 多代理设置、隔离的全局包、项目感知的二进制文件、其他包管理器 | [features-global-virtual-store](references/features-global-virtual-store.md) |
| 供应链安全 | 构建批准（allowBuilds）、最小发布年龄、信任策略、锁文件完整性 | [features-supply-chain-security](references/features-supply-chain-security.md) |
| 任务编排 | 跨项目任务图（tasks/dependsOn）、并发组、优先级、pnpm 管道 | [features-task-orchestration](references/features-task-orchestration.md) |
| 发布管理 | 原生版本控制：pnpm change/version -r/lane、lane、epic、固定组 | [features-versioning](references/features-versioning.md) |
| 多生态系统 | Python (pypi:) 和 Cargo (crate:) 依赖与 npm（实验性）并存 | [features-multi-ecosystem](references/features-multi-ecosystem.md) |

## 最佳实践

| 主题 | 描述 | 参考 |
|------|------|------|
| CI/CD 设置 | GitHub Actions、GitLab、Docker、pnpm ci、存储库缓存、冻结锁文件 | [best-practices-ci](references/best-practices-ci.md) |
| 迁移 | npm/Yarn → pnpm、幽灵依赖以及 pnpm v10 → v11 → v12 升级说明 | [best-practices-migration](references/best-practices-migration.md) |
| 性能 | 安装优化、allowBuilds、全局虚拟存储库、工作区并行化 | [best-practices-performance](references/best-practices-performance.md) |
