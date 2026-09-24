# 完成开发分支

## 概述

**核心原则：** 验证测试 → 检测环境 → 呈现选项 → 执行选择 → 清理。

**启动时宣告：** “我正在使用 finishing-a-development-branch 技能来完成这项工作。”

## 步骤 1：验证测试

运行项目的完整测试套件（`npm test` / `cargo test` / `pytest` / `go test ./...`）。

**如果测试失败**，报告失败情况并停止——绿色测试套件完成后才会出现菜单：

```
Tests failing (<N} failures). Must fix before completing:

[Show failures]
```

**如果测试通过：** 继续执行步骤 2。

## 步骤 2：检测环境

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
# Capture now, while still inside the workspace — Step 5 changes directory
# before cleanup (Step 6) needs this value
WORKTREE_PATH=$(git rev-parse --show-toplevel)
```

这决定了显示哪个菜单以及如何进行清理：

## 步骤 3：确定基础分支

基础分支即此工作分支所分叉自的分支——通常在计划、对话或分支的 upstream 中命名。如果尚不清楚，请询问：“此分支从 <your best guess} 分叉而来——是否正确？” 合并前请确认：合并到错误的基础分支，取消操作将非常耗时。

## 步骤 4：呈现选项

**常规仓库和已命名分支的工作区——准确呈现以下 3 个选项：**

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch} locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)

Which option?
```

**分离 HEAD——准确呈现以下 2 个选项：**

```
Implementation complete. You're on a detached HEAD (externally managed workspace).

1. Push as new branch and create a Pull Request
2. Keep as-is (I'll handle it later)

Which option?
```

按照原文准确呈现菜单——简洁明了，每个选项均来自上述列表。丢弃工作仅在你的人工合作伙伴明确要求时发生（见下方“若你的人工合作伙伴要求丢弃工作”）。等待其回答；集成决策由他们决定。

## 步骤 5：执行选择

### 选项 1：本地合并

```bash
# Get main repo root for CWD safety
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT}

# Merge first — verify success before removing anything
git checkout <base-branch}
git pull
git merge <feature-branch}

# Verify tests on merged result
<template command}>
```

如果合并后的结果测试失败：停止，保留工作区和分支，并进行排查——由于尚未推送，合并仅为本地操作，可恢复。

一旦合并后的结果测试通过且为绿色：清理工作区（步骤 6），然后删除分支：

```bash
git branch -d <feature-branch}
```

### 选项 2：推送并创建 PR

```bash
git push -u origin <feature-branch}>
# From a detached HEAD, name the new branch on the remote:
# git push origin HEAD:refs/heads/<new-branch}>
```

然后使用 forge 的工具创建针对 <base-branch} 的拉取/合并请求——如果其拥有可用的 CLI，则使用其 CLI，或者使用你在推送时 forge 打印的最常见的创建 URL——遵循仓库现有的 PR 模板和惯例，并将 URL 报告给你的人工合作伙伴。

保留工作区——你的人工合作伙伴将在其中迭代修复 PR 反馈。

### 选项 3：保持不变

报告：“保留分支 <name}。工作区保留在 <path}>。”

### 若你的人工合作伙伴要求丢弃工作

此路径仅作为对丢弃工作的明确请求的回应。首先确认：

```
This will permanently delete:
- Branch <name}>
- All commits: <commit-list}>
- Worktree at <path}>

Type 'discard' to confirm.
```

等待该确切的确认。当确认到达时：

```bash
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT}>
```

然后清理工作区（步骤 6）并强制删除分支：

```bash
git branch -D <feature-branch}>
```

## 步骤 6：清理工作区

**适用于选项 1 和已确认的丢弃操作。选项 2 和 3 始终保留工作区。两个调用者都已经切换到主仓库根目录——工作区删除必须在工作区外部运行——并使用在步骤 2 中获取的 `GIT_DIR`/`GIT_COMMON`/`WORKTREE_PATH` 值，即在该目录切换之前的值。**

**如果 `GIT_DIR == GIT_COMMON`：** 常规仓库，无需清理工作区。完成。

**如果 `WORKTREE_PATH` 位于 `.worktrees/` 或 `worktrees/` 下：** Superpowers
创建了此工作区——我们负责清理：

```bash
git worktree remove "$WORKTREE_PATH}>
git worktree prune  # Self-healing: clean up any stale registrations
```

**如果删除被拒绝**（`contains modified or untracked files`）：工作区包含其他地方不存在的文件——未提交的规划、笔记或草稿工作。绝不自行使用 `--force` 强制删除。向你的人工合作伙伴展示面临的风险并询问：

```bash
git -C "$WORKTREE_PATH} status --porcelain -uall
```

```
Worktree removal refused — these files were never committed:

<template file list}>

1. Commit them to <branch}> before cleanup
2. Move them into <main repo root}>
3. Delete them (unrecoverable)

Which?
```

执行选择，然后移除工作区。

**否则：** 主机环境拥有此工作区——将其保留在原位。如果您的平台提供工作区退出工具，请使用它。

## 快速参考

## 常见合理化借口

| Option | Merge | Push | Keep Worktree | Cleanup Branch |
|--------|-------|------|---------------|----------------|
| 1. Merge locally | yes | - | - | yes |
| 2. Create PR | - | yes | yes | - |
| 3. Keep as-is | - | - | yes | - |
| Discard (explicit request only) | - | - | - | yes (force) |

| Excuse | Reality |
|--------|---------|
| "Tests passed earlier this session" | Run the suite on the tree you are about to integrate. A green run only proves the tree it ran on. |
| "They obviously want it merged" | Integration is your human partner's decision. Present the menu and wait. |
| "They seem done with this feature — I'll offer to discard it" | The menu is complete as written. Discard happens only when your human partner asks for it in so many words. |
| "'Yeah, get rid of it' counts as confirmation" | Only the typed word `discard` authorizes deletion. |
| "The PR is up, so the worktree is clutter now" | PR feedback gets fixed in that worktree. It stays until the work lands. |
| "This other worktree looks stale — I'll clean it too" | Clean up only worktrees under `.worktrees/` or `worktrees/`. Everything else belongs to the host. |
| "Removal refused — `--force` is just finishing the cleanup" | The refusal means files exist only in that worktree. `--force` destroys them permanently. Show your human partner and ask. |
| "The merged-result failure is probably flaky" | A failing merged result stops everything. Branch and worktree stay put while you investigate. |
| "The base branch is obviously main" | Confirm the fork point or ask. Merging into the wrong base is expensive to undo. |
| "The push was rejected — force-push will fix it" | A rejected push means the remote moved. Investigate; force-push only on your human partner's explicit request. |
