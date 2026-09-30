---
name: git-advanced-workflows
description: 掌握高级 Git 工作流程，包括变基、变基提取、二分查找、工作树和引用日志，以保持清晰的版本历史并从任何情况中恢复。在管理复杂的 Git 版本历史、协作特性分支或排除存储库问题时使用。
---

# Git 高级工作流

掌握高级 Git 技巧，以维护干净的版本历史记录、有效协作，并在任何情况下都能自信地恢复。

## 何时使用这项技能

- 合并前清理提交历史记录
- 将特定提交应用到不同分支
- 查找引入错误的提交
- 同时处理多个功能
- 恢复 Git 错误或丢失的提交
- 管理复杂的分支工作流
- 准备干净的 PR 以供审查
- 同步分叉的分支

## 核心概念

### 1. 交互式变基

交互式变基是 Git 版本历史记录编辑的瑞士军刀。

**常用操作：**

- `pick`：保持提交不变
- `reword`：修改提交信息
- `edit`：修改提交内容
- `squash`：与上一个提交合并
- `fixup`：类似 squash 但丢弃信息
- `drop`：完全删除提交

**基本用法：**

```bash
# 变基最后 5 个提交
git rebase -i HEAD~5

# 变基当前分支上的所有提交
git rebase -i $(git merge-base HEAD main)

# 变基到特定提交
git rebase -i abc123
```

### 2. 拾取提交

将一个分支上的特定提交应用到另一个分支，而无需合并整个分支。

```bash
# 拾取单个提交
git cherry-pick abc123

# 拾取提交范围（起始不包含）
git cherry-pick abc123..def456

# 拾取但不提交（仅暂存更改）
git cherry-pick -n abc123

# 拾取并编辑提交信息
git cherry-pick -e abc123
```

### 3. Git 二分查找

通过二分查找提交历史记录来找到引入错误的提交。

```bash
# 开始二分查找
git bisect start

# 标记当前提交为错误
git bisect bad

# 标记已知正确的提交
git bisect good v1.0.0

# Git 会检出中间提交 - 测试它
# 然后标记为正确或错误
git bisect good  # 或: git bisect bad

# 继续直到找到错误
# 完成后
git bisect reset
```

**自动二分查找：**

```bash
# 使用脚本自动测试
git bisect start HEAD v1.0.0
git bisect run ./test.sh

# test.sh 应该在正确时退出 0，错误时退出 1-127（125 除外）
```

### 4. 工作树

同时处理多个分支，而无需暂存或切换。

```bash
# 列出现有工作树
git worktree list

# 为特性分支添加新的工作树
git worktree add ../project-feature feature/new-feature

# 添加工作树并创建新分支
git worktree add -b bugfix/urgent ../project-hotfix main

# 删除工作树
git worktree remove ../project-feature

# 修剪过期工作树
git worktree prune
```

### 5. Reflog

你的安全网 - 追踪所有引用移动，即使已删除的提交。

```bash
# 查看-reflog
git reflog

# 查看特定分支的-reflog
git reflog show feature/branch

# 恢复已删除的提交
git reflog
# 找到提交哈希
git checkout abc123
git branch recovered-branch

# 恢复已删除的分支
git reflog
git branch deleted-branch abc123
```

## 详细模式和实例

详细模式文档位于 `references/details.md`。当上层导航不足时，请阅读该文件。

## 最佳实践

1. **始终使用 --force-with-lease**：比 --force 更安全，防止覆盖他人工作
2. **仅变基本地提交**：不要变基已推送和共享的提交
3. **描述性提交信息**：未来的你会感谢现在的你
4. **原子提交**：每个提交应该是单一逻辑变更
5. **推送前测试**：确保历史记录重写没有破坏任何东西
6. **保持对-reflog 的了解**：记住-reflog 是你 90 天的安全网
7. **风险操作前创建分支**：在复杂变基前创建备份分支

```bash
# 安全强制推送
git push --force-with-lease origin feature/branch

# 风险操作前创建备份
git branch backup-branch
git rebase -i main
# 如果出问题
git reset --hard backup-branch
```

## 常见陷阱

- **变基公共分支**：会导致协作者的版本历史冲突
- **无租约强制推送**：可能会覆盖队友的工作
- **变基中丢失工作**：仔细解决冲突，变基后测试
- **忘记清理工作树**：遗弃的工作树会占用磁盘空间
- **实验前未备份**：始终创建安全分支
- **脏工作目录上二分查找**：变基前提交或暂存

## 恢复命令

```bash
# 中断进行中的操作
git rebase --abort
git merge --abort
git cherry-pick --abort
git bisect reset

# 恢复特定提交的文件版本
git restore --source=abc123 path/to/file

# 撤销最后一个提交但保留更改
git reset --soft HEAD^

# 撤销最后一个提交并丢弃更改
git reset --hard HEAD^

# 恢复 90 天内删除的分支
git reflog
git branch recovered-branch abc123
```
