# Dependabot 配置与管理

## 概述

Dependabot 是 GitHub 的内置依赖管理工具，具有三个核心功能：

1. **Dependabot 警报** — 当依赖项存在已知漏洞（CVE）时通知
2. **Dependabot 安全更新** — 自动创建 PR 来修复有漏洞的依赖项
3. **Dependabot 版本更新** — 自动创建 PR 以保持依赖项最新

所有配置都位于**单个文件**中：默认分支上的 `.github/dependabot.yml`。GitHub **不支持**每个仓库有多个 `dependabot.yml` 文件。

## 配置流程

在创建或优化 `dependabot.yml` 时，请遵循以下流程：

### 第 1 步：检测所有生态系统

扫描仓库以查找依赖项清单。查找：

| 生态系统 | YAML 值 | 清单文件 |
|---|---|---|
| npm/pnpm/yarn | `npm` | `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock` |
| pip/pipenv/poetry | `pip` | `requirements.txt`, `Pipfile`, `pyproject.toml`, `setup.py` |
| uv | `uv` | `pyproject.toml`, `uv.lock` |
| Docker | `docker` | `Dockerfile` |
| Docker Compose | `docker-compose` | `docker-compose.yml` |
| GitHub Actions | `github-actions` | `.github/workflows/*.yml` |
| Go 模块 | `gomod` | `go.mod` |
| Bundler (Ruby) | `bundler` | `Gemfile` |
| Cargo (Rust) | `cargo` | `Cargo.toml` |
| Composer (PHP) | `composer` | `composer.json` |
| NuGet (.NET) | `nuget` | `*.csproj`, `packages.config` |
| .NET SDK | `dotnet-sdk` | `global.json` |
| Maven (Java) | `maven` | `pom.xml` |
| Gradle (Java) | `gradle` | `build.gradle` |
| Terraform | `terraform` | `*.tf` |
| OpenTofu | `opentofu` | `*.tf` |
| Helm | `helm` | `Chart.yaml` |
| Hex (Elixir) | `mix` | `mix.exs` |
| Swift | `swift` | `Package.swift` |
| Pub (Dart) | `pub` | `pubspec.yaml` |
| Bun | `bun` | `bun.lockb` |
| Dev Containers | `devcontainers` | `devcontainer.json` |
| Git 子模块 | `gitsubmodule` | `.gitmodules` |
| Pre-commit | `pre-commit` | `.pre-commit-config.yaml` |

注意：
- pnpm 和 yarn 都使用 `npm` 生态系统值。
- 当存在 `uv.lock` 时，优先使用 `uv` 生态系统值；否则使用 `pip`。

### 第 2 步：映射目录位置

对于每个生态系统，确定清单所在的路径。对于单体仓库，使用带 glob 模式的 `directories`（复数）：

```yaml
directories:
  - "/"           # 根目录
  - "/apps/*"     # 所有 app 子目录
  - "/packages/*" # 所有 package 子目录
  - "/lib-*"      # 以 lib- 开头的目录
  - "**/*"        # 递归（所有子目录）
```

重要提示：`directory`（单数）不支持 glob。使用 `directories`（复数）进行通配符匹配。

### 第 3 步：配置每个生态系统条目

每个条目至少需要以下内容：

```yaml
- package-ecosystem: "npm"
  directory: "/"
  schedule:
    interval: "weekly"
```

### 第 4 步：通过分组、标签和调度进行优化

请参考下文各优化技术的具体说明。

## 单体仓库策略

### 工作区覆盖的 glob 模式

对于包含许多包的单体仓库，使用 glob 模式以避免列出每个目录：

```yaml
- package-ecosystem: "npm"
  directories:
    - "/"
    - "/apps/*"
    - "/packages/*"
    - "/services/*"
  schedule:
    interval: "weekly"
```

### 跨目录分组

使用 `group-by: dependency-name` 在多个目录中更新相同依赖项时创建单个 PR：

```yaml
groups:
  monorepo-deps:
    group-by: dependency-name
```

这会在所有指定目录中为每个依赖项创建一个 PR，减少 CI 成本和审查负担。

限制：
- 所有目录必须使用相同的包生态系统
- 仅适用于版本更新
- 不兼容的版本约束将创建单独的 PR

### 工作区外部的独立包

如果一个目录有自己的锁文件且**不属于**工作区（例如 `.github/` 中的脚本），为其创建一个单独的生态系统条目。

## 依赖项分组

通过将相关依赖项分组到单个 PR 中来减少 PR 噪声。

### 按依赖类型分组

```yaml
groups:
  dev-dependencies:
    dependency-type: "development"
    update-types: ["minor", "patch"]
  production-dependencies:
    dependency-type: "production"
    update-types: ["minor", "patch"]
```

### 按名称模式分组

```yaml
groups:
  angular:
    patterns: ["@angular*"]
    update-types: ["minor", "patch"]
  testing:
    patterns: ["jest*", "@testing-library*", "ts-jest"]
```

### 用于安全更新

```yaml
groups:
  security-patches:
    applies-to: security-updates
    patterns: ["*"]
    update-types: ["patch", "minor"]
```

关键行为：
- 匹配多个组的依赖项将优先进入**第一个**匹配的组
- `applies-to` 缺失时默认为 `version-updates`
- 未分组的依赖项将获得单独的 PR

## 多生态系统分组

将不同包生态系统的更新组合到单个 PR 中：

```yaml
version: 2

multi-ecosystem-groups:
  infrastructure:
    schedule:
      interval: "weekly"
    labels: ["infrastructure", "dependencies"]

updates:
  - package-ecosystem: "docker"
    directory: "/"
    patterns: ["nginx", "redis"]
    multi-ecosystem-group: "infrastructure"

  - package-ecosystem: "terraform"
    directory: "/"
    patterns: ["aws*"]
    multi-ecosystem-group: "infrastructure"
```

使用 `multi-ecosystem-group` 时需要 `patterns` 键。

## PR 自定义

### 标签

```yaml
labels:
  - "dependencies"
  - "npm"
```

设置 `labels: []` 以禁用所有标签（包括默认标签）。如果仓库中存在 SemVer 标签（`major`, `minor`, `patch`），则始终应用。

### 提交信息

```yaml
commit-message:
  prefix: "deps"
  prefix-development: "deps-dev"
  include: "scope"  # 在前缀后添加 deps/deps-dev 范围
```

### 指派者和里程碑

```yaml
assignees: ["security-team-lead"]
milestone: 4  # 里程碑 URL 的数字 ID
```

### 分支名称分隔符

```yaml
pull-request-branch-name:
  separator: "-"  # 默认是 /
```

### 目标分支

```yaml
target-branch: "develop"  # PR 将指向此分支，而不是默认分支
```

注意：当设置 `target-branch` 时，安全更新仍将指向默认分支；所有生态系统配置仅适用于版本更新。

## 调度优化

### 间隔

支持：`daily`, `weekly`, `monthly`, `quarterly`, `semiannually`, `yearly`, `cron`

```yaml
schedule:
  interval: "weekly"
  day: "monday"         # 仅限每周
  time: "09:00"         # HH:MM 格式
  timezone: "America/New_York"
```

### Cron 表达式

```yaml
schedule:
  interval: "cron"
  cronjob: "0 9 * * 1"  # 每周一 9 点
```

### 冷却期

延迟新发布版本的更新以避免早期采用者问题：

```yaml
cooldown:
  default-days: 5
  semver-major-days: 30
  semver-minor-days: 7
  semver-patch-days: 3
  include: ["*"]
  exclude: ["critical-lib"]
```

冷却期仅适用于版本更新，不适用于安全更新。

## 安全更新配置

### 通过仓库设置启用

设置 → 高级安全 → 启用 Dependabot 警报、安全更新和分组安全更新。

### 在 YAML 中分组安全更新

```yaml
groups:
  security-patches:
    applies-to: security-updates
    patterns: ["*"]
    update-types: ["patch", "minor"]
```

### 禁用版本更新（仅限安全）

```yaml
open-pull-requests-limit: 0  # 禁用版本更新 PR
```

### 自动分类规则

GitHub 预设自动忽略低影响警报（开发依赖项）。自定义规则可按严重性、包名、CWE 等过滤。在仓库设置 → 高级安全中配置。

## PR 评论命令

使用 `@dependabot` 评论与 Dependabot PR 交互。

> **注意**：截至 2026 年 1 月，合并/关闭/重新打开命令已弃用。
> 使用 GitHub 的原生 UI、CLI (`gh pr merge`) 或自动合并。

| 命令 | 效果 |
|---|---|
| `@dependabot rebase` | 重新拉取 PR |
| `@dependabot recreate` | 从头重新创建 PR |
| `@dependabot ignore this dependency` | 关闭并永不更新此依赖项 |
| `@dependabot ignore this major version` | 忽略此主版本 |
| `@dependabot ignore this minor version` | 忽略此次版本 |
| `@dependabot ignore this patch version` | 忽略此补丁版本 |

对于分组 PR，附加命令：
- `@dependabot ignore DEPENDENCY_NAME` — 忽略组中的特定依赖项
- `@dependabot unignore DEPENDENCY_NAME` — 清除忽略，使用更新重新打开
- `@dependabot unignore *` — 清除组中所有依赖项的忽略
- `@dependabot show DEPENDENCY_NAME ignore conditions` — 显示当前忽略条件

有关完整命令参考，请参阅 `references/pr-commands.md`。

## 忽略和允许规则

### 忽略特定依赖项

```yaml
ignore:
  - dependency-name: "lodash"
  - dependency-name: "@types/node"
    update-types: ["version-update:semver-patch"]
  - dependency-name: "express"
    versions: ["5.x"]
```

### 仅允许特定类型

```yaml
allow:
  - dependency-type: "production"
  - dependency-name: "express"
```

规则：如果依赖项同时匹配 `allow` 和 `ignore`，则**忽略**。

### 排除路径

```yaml
exclude-paths:
  - "vendor/**"
  - "test/fixtures/**"
```

## 高级选项

### 版本策略

控制 Dependabot 如何编辑版本约束：

| 值 | 行为 |
|---|---|
| `auto` | 默认 — 应用程序增加，库放宽 |
| `increase` | 总是增加最小版本 |
| `increase-if-necessary` | 仅当当前范围不包括新版本时更改 |
| `lockfile-only` | 仅更新锁文件，忽略清单 |
| `widen` | 放宽范围以包含旧版本和新版本 |

### Rebase 策略

```yaml
rebase-strategy: "disabled"  # 停止自动 rebase
```

通过在提交信息中包含 `[dependabot skip]` 允许 rebase 额外的提交。

### Open PR 限制

```yaml
open-pull-requests-limit: 10  # 默认是版本 5，安全 10
```

设置为 `0` 以完全禁用版本更新。

### 私有注册表

```yaml
registries:
  npm-private:
    type: npm-registry
    url: https://npm.example.com
    token: ${{secrets.NPM_TOKEN}}

updates:
  - package-ecosystem: "npm"
    directory: "/"
    registries:
      - npm-private
```

## 常见问题解答

**我可以有多个 `dependabot.yml` 文件吗？**
不可以。GitHub 仅支持 `.github/dependabot.yml` 的**一个文件**。在文件内使用多个 `updates` 条目以覆盖不同的生态系统和目录。

**Dependabot 支持 pnpm 吗？**
是的。使用 `package-ecosystem: "npm"` — Dependabot 自动检测 `pnpm-lock.yaml`。

**如何减少单体仓库中的 PR 噪声？**
使用 `groups` 批量更新，`directories` 带 glob 进行覆盖，以及 `group-by: dependency-name` 进行跨目录分组。考虑为低优先级生态系统设置 `monthly` 或 `quarterly` 间隔。

**如何处理工作区外的依赖项？**
为该位置创建一个单独的生态系统条目，并指定其 `directory`。

## 通过 AI 编码代理进行提交前依赖项扫描

在提交前通过 AI 编码代理扫描代码更改中的易受攻击依赖项，GitHub MCP 服务器上的 `dependabot` 工具集可以检查您的依赖项添加情况，并与 GitHub 警报数据库进行比对，返回受影响的包、严重性和建议的修复版本。对于更彻底的提交后检查，它还可以在本地运行 Dependabot CLI 以比较更改前后的依赖项图。

安装**高级安全插件**，它提供专用的依赖项扫描工具和 `/dependency-scanning` 技能。

**GitHub Copilot CLI (shell):**
```bash
# 为 GitHub MCP 服务器启用 dependabot 工具集
copilot --add-github-mcp-toolset dependabot
```

**GitHub Copilot CLI (在 `copilot` 内):**
```text
> /plugin install advanced-security@copilot-plugins
```

**Visual Studio Code:**
- 在 GitHub MCP 服务器标头中添加 `"X-MCP-Toolsets": "dependabot"`，或从 Copilot Chat 中的工具集选择器中选择 **Dependabot**
- 安装 `advanced-security` 插件，然后在 Copilot Chat 中使用 `/dependency-scanning`

**示例提示:**
> 扫描我在此分支中添加的依赖项的已知漏洞，并告诉我升级到哪些版本后再提交。

参考：[高级安全插件 — 依赖项扫描技能](https://github.com/github/copilot-plugins/blob/main/plugins/advanced-security/skills/dependency-scanning/SKILL.md)

> 宣布于 [Dependency scanning with GitHub MCP Server is in public preview](https://github.blog/changelog/2026-05-05-dependency-scanning-with-github-mcp-server-is-in-public-preview/) (2026 年 5 月)

## 资源

- `references/dependabot-yml-reference.md` — 完整 YAML 选项参考
- `references/pr-commands.md` — 完整 PR 评论命令参考
- `references/example-configs.md` — 真实世界的配置示例
