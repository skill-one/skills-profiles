# 清理已删除的分支

删除本地分支，其远程跟踪分支已被删除，包括任何关联的工作树。

## 工作流程

### 第一步：发现已删除的分支

运行发现脚本以获取最新的远程状态并识别已删除的分支：

```bash
bash scripts/clean-gone
```

[scripts/clean-gone](./scripts/clean-gone)

脚本首先运行 `git fetch --prune`，然后解析 `git branch -vv` 以查找标记为 `: gone]` 的分支。

如果脚本输出 `__NONE__`，则报告未找到过期的分支并停止。

### 第二步：展示分支并请求确认

向用户展示将要被删除的分支列表。格式为简单的列表：

```
这些本地分支已从远程中删除：

  - feature/old-thing
  - bugfix/resolved-issue
  - experiment/abandoned

删除所有这些分支？(y/n)
```

使用平台的阻塞问题工具等待用户的回答：Claude Code 中的 `AskUserQuestion`（如果其模式未加载，请先使用 `ToolSearch` 调用 `select:AskUserQuestion`），Codex 中的 `request_user_input`，Gemini 中的 `ask_user`，Pi 中的 `ask_user`（需要 `pi-ask-user` 扩展）。如果 harness 中不存在阻塞工具或调用出错（例如 Codex 编辑模式）时，回退到仅通过聊天展示列表——不是因为需要加载模式。永远不要无声地跳过问题。

这是一个针对整个列表的是或否决定——不要提供多选或逐分支选择。

### 第三步：删除确认的分支

如果用户确认，则删除每个分支。对于每个分支：

1. 检查它是否有关联的工作树（`git worktree list | grep "\\[$branch\\]"`）
2. 如果存在工作树且不是主仓库根，则先移除它：`git worktree remove --force "$worktree_path"`
3. 删除分支：`git branch -D "$branch"`

逐步报告结果：

```
已移除工作树：.worktrees/feature/old-thing
已删除分支：feature/old-thing
已删除分支：bugfix/resolved-issue
已删除分支：experiment/abandoned

已清理 3 个分支。
```

如果用户拒绝，则确认并停止，不删除任何内容。
