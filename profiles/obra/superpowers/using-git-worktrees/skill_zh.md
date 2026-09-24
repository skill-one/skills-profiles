# Using Git Worktrees

## 概述

确保工作在各司隔离的工作区中开展。优先使用平台原生的工作树工具。仅在无原生工具可用时，回退到手动创建 git 工作树。

**核心原则：** 首先检测现有的隔离状态。然后使用原生工具。然后回退到 git。永远不要与 harness 抗争。

**启动时需通报：** “我正在使用 using-git-worktrees 技能来设置一个隔离的工作区。”

## 步骤 0：检测现有隔离状态

**在创建任何内容之前，检查是否已经处于隔离工作区中。**

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

**子模块保护：** `GIT_DIR != GIT_COMMON` 在 git 子模块内也为真。在认定“已处于工作树中”之前，需验证您不在子模块内：

```bash
# 若此命令返回路径，则您处于子模块中，而非工作树 — 按普通仓库处理
git rev-parse --show-superproject-working-tree 2>/dev/null
```

**如果 `GIT_DIR != GIT_COMMON`（且非子模块）：** 您已处于关联的工作树中。跳过至第 2 步（项目设置）。切勿创建另一个工作树。

以分支状态报告：
- 处于分支上： “已处于隔离工作区 `<路径>`，分支为 `<名称>`。”
- 游离 HEAD： “已处于隔离工作区 `<路径>`（游离 HEAD，由外部管理）。需在结束时创建分支。”

**如果 `GIT_DIR == GIT_COMMON`（或在子模块中）：** 您处于普通的代码库检出目录中。

用户是否已在您的指令中表明其工作树偏好？若未明确，请在创建工作树前征得同意：

> “您是否希望我设置一个隔离工作树？这将保护您的当前分支免受变更影响。”

若无其他已声明偏好，请予以遵守。若用户拒绝同意，则原地工作并跳过至第 2 步。

## 步骤 1：创建隔离工作区

**您拥有两种机制。请按此顺序尝试。**

### 1a. 原生工作树工具（优先）

用户已请求隔离工作区（步骤 0 同意）。您是否已有创建工作树的方法？这可能是一个名称类似于 `EnterWorktree`、`WorktreeCreate`、`/worktree` 命令或 `--worktree` 参数的工具。如果有，请使用它并跳过至第 2 步。

原生工具会自动处理目录放置、分支创建和清理。在已有原生工具的情况下使用 `git worktree add` 会创建 harness 无法查看或管理的幻影状态。

只有在没有可用的原生工作树工具时，才进行到步骤 1b。

### 1b. Git 工作树回退

**仅当步骤 1a 不适用时使用** —— 即没有可用的原生工作树工具。请使用 git 手动创建工作树。

#### 目录选择

遵循此优先级顺序。明确的用户偏好始终优先于观察到的文件系统状态。

1. **检查您的指令中是否有声明的工作树目录偏好。** 若用户已指定，则直接使用，无需询问。

2. **检查是否存在项目本地的现有工作树目录：**
   ```bash
   ls -d .worktrees 2>/dev/null     # 优先（隐藏）
   ls -d worktrees 2>/dev/null      # 备选
   ```
   若找到，则使用它。若两者均存在，`.worktrees` 优先。

3. **若无可用的其他指引**，默认在项目根目录下使用 `.worktrees/`。

#### 安全性验证（仅针对项目本地目录）

**在创建工作树前，必须验证目录已被忽略：**

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

**若未被忽略：** 将其添加到 .gitignore，提交变更，然后继续。

**为何至关重要：** 防止工作树内容被意外提交到仓库中。

#### 创建工作树

```bash
# 根据选定位置确定路径
path="$LOCATION/$BRANCH_NAME"

git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"
```

**沙盒回退：** 如果 `git worktree add` 因权限错误（沙盒拒绝）而失败，请告知用户沙盒阻止了工作树创建，您将在当前目录中工作。然后在原地运行设置和基准测试。

## 步骤 2：项目设置

自动检测并运行适当的设置：

```bash
# Node.js
if [ -f package.json ]; then npm install; fi

# Rust
if [ -f Cargo.toml ]; then cargo build; fi

# Python
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f pyproject.toml ]; then poetry install; fi

# Go
if [ -f go.mod ]; then go mod download; fi
```

## 步骤 3：验证干净的基准状态

运行测试以确保工作区初始干净：

```bash
# 使用项目适用的命令
npm test / cargo test / pytest / go test ./...
```

**如果测试失败：** 报告失败情况，并询问是否继续或进行调查。

**如果测试通过：** 报告就绪。

### 报告

```
工作树已就绪于 <full-path>
测试通过（执行 <N 个测试，0 个失败）
已就绪，准备实现 <feature-name>
```

## 快速参考

| 情形 | 操作 |
|-----------|--------|
| 已处于关联工作树 | 跳过创建（步骤 0） |
| 处于子模块中 | 按普通仓库处理（步骤 0 保护） |
| 有原生工作树工具可用 | 使用它（步骤 1a） |
| 无原生工具 | Git 工作树回退（步骤 1b） |
| 存在 `.worktrees/` | 使用它（验证已被忽略） |
| 存在 `worktrees/` | 使用它（验证已被忽略） |
| 两者均存在 | 使用 `.worktrees/` |
| 两者均不存在 | 检查指令文件，然后默认使用 `.worktrees/` |
| 目录未被忽略 | 添加到 .gitignore 并提交 |
| 创建时权限错误 | 沙盒回退，原地工作 |
| 基准测试期间测试失败 | 报告失败情况 + 询问 |
| 无 package.json/Cargo.toml | 跳过依赖安装 |

## 常见错误解释

| 借口 | 现实 |
|--------|---------|
| “我明显不在工作树中，无需检查” | 执行步骤 0。harness 创建的隔离状态与子模块均可迷惑肉眼判断；检测命令可最终定论。 |
| “`git worktree add` 比寻找原生工具更快” | 原生工具（如 `EnterWorktree`）负责目录放置、分支创建和清理。绕过它是最常见的错误——它会创建 harness 无法查看或管理的幻影状态。 |
| “工作树目录肯定已被忽略” | 运行 `git check-ignore`。未被忽略的工作树目录会将整个树提交到仓库中。 |
| “任何目录名称均可” | 明确的指令优先于现有的项目本地目录，而项目本地目录又优先于 `.worktrees/` 默认设置。 |
| “工作区是全新的，基准测试可以稍后等待” | 脏的基准状态会使后续每一个失败变得难以界定。现在运行测试；越过失败继续是您的人类伙伴做出的决定。 |
