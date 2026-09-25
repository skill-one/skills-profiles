# /hub:merge — 合并胜者

将最佳代理的分支合并到基础分支，通过 git 标签存档失败分支，并清理工作树。

## 使用方法

```
/hub:merge                                       # 合并最新会话的胜者
/hub:merge 20260317-143022                       # 合并特定会话的胜者
/hub:merge 20260317-143022 --agent agent-2       # 明确选择胜者
```

## 功能说明

### 1. 确定胜者

如果指定了 `--agent`，则使用该代理。否则，使用最新 `/hub:eval` 中排名第一的代理。

### 2. 合并胜者

```bash
git checkout {base_branch}
git merge --no-ff hub/{session-id}/{winner}/attempt-1 \
  -m "hub: 合并 {winner} 来自会话 {session-id}

任务: {task}
胜者: {winner}
会话: {session-id}"
```

### 3. 存档失败者

对于每个非胜者代理：

```bash
# 创建存档标签（永久保留提交）
git tag hub/archive/{session-id}/{agent-id} hub/{session-id}/{agent-id}/attempt-1

# 删除分支引用（提交通过标签保留）
git branch -D hub/{session-id}/{agent-id}/attempt-1
```

### 4. 清理工作树

```bash
python {skill_path}/scripts/session_manager.py --cleanup {session-id}
```

### 5. 合并后摘要

写入 `.agenthub/board/results/merge-summary.md`：

```markdown
---
author: coordinator
timestamp: {now}
channel: results
---

## 合并摘要

- **会话**: {session-id}
- **胜者**: {winner}
- **合并到**: {base_branch}
- **存档**: {loser-1}, {loser-2}, ...
- **清理工作树**: {count}
```

### 6. 更新状态

```bash
python {skill_path}/scripts/session_manager.py --update {session-id} --state merged
```

## 安全注意事项

- **合并前与用户确认** — 首先显示差异摘要
- **禁止强制推送** — 合并始终使用 `--no-ff` 以保持清晰历史
- **存档而非删除** — 失败代理的提交通过标签保留
- **清理工作树** — 不要在磁盘上留下孤儿目录

## 合并后

告知用户：
- 胜者已合并到 `{base_branch}`
- 失败者通过标签 `hub/archive/{session-id}/agent-{N}` 存档
- 工作树已清理
- 会话状态: `merged`
