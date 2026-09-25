# 版本发布工作流

这个技能是一个路由器。详细步骤位于 `references/` 目录中。

## 范围边界（重要）

这个技能仅用于：

1. 发布分支 / PR 工作流
2. CI 触发约束 (`auto-tag-release.yml`)
3. GitHub 发布说明编写

这个技能**不**用于编写 `docs/changelog/*.mdx`。如果用户要求网站变更日志页面，则加载 `../docs-changelog/SKILL.md`。

## 必须配合的技能

对于每个 `/version-release` 执行，你必须加载并应用：

- `../../../DESIGN.md` (语音 & 内容)

## 概述

主要开发分支是 **canary**。日常开发都在 canary 分支上进行。发布时，canary 分支会被合并到 main 分支。常规发布 PR (`🚀 release: …`, `release/*`, `hotfix/*`) 在 PR 打开时，会从 `release-pr-version.yml` 获取 `package.json` 版本号提交。合并后，`auto-tag-release.yml` 会给合并提交打标签并创建 GitHub 发布。`sync-main-to-canary` 在推送到 `main` 时运行。

实践中只使用两种发布类型（重大发布极其罕见，可以忽略）：

| 类型  | 用例                                       | 频率             | 源分支  | PR 标题格式                      | 版本       | 参考                               |
| ----- | ------------------------------------------ | --------------------- | -------------- | ------------------------------------ | ------------- | --------------------------------------- |
| 小版本 | 功能迭代发布                      | \~每 4 周       | canary         | `🚀 release: v{x.y.0}`               | 手动设置  | `references/minor-release.md`           |
| 补丁 | 每周发布 / 热修复 / 模型 / 数据库迁移 | \~每周或按需 | canary 或 main | 自定义 (例如 `🚀 release: 20260222`) | 自动补丁 +1 | `references/patch-release-scenarios.md` |

编写发布说明正文（任何发布类型），请参阅 `references/release-notes-style.md`。

## 自动发布触发规则 (`auto-tag-release.yml`)

PR 合并到 main 后，CI 会根据以下优先级确定是否发布：

### 1. 小版本发布（精确版本）

PR 标题匹配 `🚀 release: v{x.y.z}` -> 使用标题中的版本号。

### 2. 补丁发布（自动补丁 +1）

由以下优先级触发：

- **分支名匹配**：`hotfix/*` 或 `release/*` -> 直接触发（跳过标题检测）
- **标题前缀匹配**：具有以下标题前缀的 PR 将会触发：
  - `style` / `💄 style`
  - `feat` / `✨ feat`
  - `fix` / `🐛 fix`
  - `refactor` / `♻️ refactor`
  - `hotfix` / `🐛 hotfix` / `🩹 hotfix`
  - `build` / `👷 build`

### 3. 无触发

不匹配上述任何条件的 PR（例如 `docs`, `chore`, `ci`, `test`），合并到 main 时不会触发发布。

## 自动化操作

1. **在发布 PR 上** (`release-pr-version.yml`) — 如果 `package.json` 落后，向 PR 头提交 `🔖 chore(release): release version v{x.y.z}`。小版本标题 `🚀 release: v{x.y.z}` 使用该版本；每周 / `release/*` / `hotfix/*` 使用最新稳定标签 + 补丁。
2. **合并后** (`auto-tag-release.yml`) — 在合并提交上打 `v{x.y.z}` 标签并创建 GitHub 发布。补丁版本是最新稳定标签 +1，不是 `package.json` +1。
3. **`sync-main-to-canary`** — 在推送到 `main` 时运行。

## 代理操作指南

当用户请求发布时：

### 预检（适用于所有发布类型）

在创建发布分支前，验证源分支：

- **每周发布** (`release/weekly-*`)：必须从 `canary` 分支创建
- **所有其他发布/热修复分支**：必须从 `main` 分支创建；运行 `git merge-base --is-ancestor main <branch> && echo OK`
- 如果分支基于错误的源，则从正确的基线重新创建

### 路由

选择正确的参考并端到端遵循：

- **小版本发布** → `references/minor-release.md`
- **补丁发布** (每周 / 热修复 / 模型发布 / 数据库迁移) → `references/patch-release-scenarios.md`
- **编写 PR 正文 / 发布说明** (任何发布类型) → `references/release-notes-style.md`

### 硬性规则（适用于所有发布类型）

- **不要**手动修改 `package.json` 版本 — CI 会处理它。
- **不要**手动创建标签 — CI 会处理它们。
- 小版本 PR 标题格式严格 (`🚀 release: v{x.y.z}`)。
- 补丁 PR 不需要显式的版本号。
- 保持发布事实准确；不要编造指标或可用性声明。发布说明输入（比较基线、PR 引用、贡献者列表）**必须从 `git`** 根据 `references/release-notes-style.md` § 计算输入 — 从不来自内存或描述。
