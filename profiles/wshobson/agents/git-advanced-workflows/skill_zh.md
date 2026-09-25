# Git 高级工作流程

掌握高级 Git 技巧，以维护干净的版本历史记录、有效协作，并在任何情况下都能自信地恢复。

## 何时使用这项技能

- 合并前清理提交历史记录
- 将特定提交应用到不同分支
- 查找引入错误的提交
- 同时处理多个功能
- 恢复 Git 错误或丢失的提交
- 管理复杂的分支工作流程
- 准备干净的 PR 以供审查
- 同步分叉的分支

## 核心概念

### 1. 交互式变基

交互式变基是 Git 版本历史记录编辑的瑞士军刀。

**常用操作：**

- `pick`：保持提交不变
- `reword`：修改提交信息
- `edit`：修改提交内容
- `squash`：合并到前一个提交
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

# 将当前提交标记为错误
git bisect bad

# 将已知正确的提交标记为正确
git bisect good v1.0.0

# Git 会检出中间提交 - 测试它
# 然后标记为正确或错误
git bisect good  # 或: git bisect bad

# 继续直到找到错误
# 完成时
git bisect reset
```

**自动二分查找：**

```bash
# 使用脚本自动测试
git bisect start HEAD v1.0.0
git bisect run ./test.sh

# test.sh 应该在正确时退出 0，在错误时退出 1-127（125 除外）
```

### 4. 工作树

同时处理多个分支，而无需暂存或切换。

```bash
# 列出现有工作树
git worktree list

# 为功能分支添加新的工作树
git worktree add ../project-feature feature/new-feature

# 添加工作树并创建新分支
git worktree add -b bugfix/urgent ../project-hotfix main

# 删除工作树
git worktree remove ../project-feature

# 修剪过期的工
