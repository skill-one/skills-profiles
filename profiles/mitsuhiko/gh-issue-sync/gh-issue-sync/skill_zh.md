# gh-issue-sync

将 GitHub 问题同步到本地 Markdown 文件中，存储在 `.issues/open/` 和 `.issues/closed/` 目录下。

## 命令

```
gh-issue-sync init              # 在 git 仓库中初始化
gh-issue-sync pull              # 获取开放问题 (--all 用于获取已关闭问题)
gh-issue-sync push              # 推送本地更改 (--dry-run 用于预览)
gh-issue-sync list              # 列出问题 (支持 gh issue list 标志 + --search)
gh-issue-sync new "标题"       # 创建问题 (--label, --edit)
gh-issue-sync close 42          # 关闭 (--reason completed|not_planned)
gh-issue-sync reopen 42
gh-issue-sync status            # 显示本地更改
gh-issue-sync diff 42           # 显示差异 (--remote 用于重新获取)
```

## 文件格式

`.issues/open/42-fix-login-bug.md`:
```markdown
---
title: 修复登录问题
labels: [bug, priority:high]
assignees: [alice]
milestone: v1.0
state: open
# 对于已关闭问题: state_reason: completed|not_planned
# 可选: parent: 10, blocked_by: [11, 12], blocks: [15]
---

Markdown 格式的问题正文。
```

问题编号由文件名决定，而不是存储在前置内容中。

## 临时问题

新问题会获得以 `T` 开头的 ID（例如，`T1a2b3c`）。文件名必须以 `T` 开头：
```
.issues/open/T1a2b3c-my-new-issue.md
```

在 `push` 时，文件会被重命名为实际的问题编号（例如，`42-my-new-issue.md`），并且前置内容中的 `number:` 也会更新。其他问题中任何 `#T1a2b3c` 的引用也会更新为 `#42`。

## 评论

在推送时发布评论，可以在问题旁边创建一个 `.comment.md` 文件：
```
.issues/open/42.comment.md
.issues/open/42-fix-login-bug.comment.md
```

内容为纯 Markdown 格式。评论发布后文件会被删除。

## 注意事项

- `pull` 会跳过冲突；使用 `--force` 来覆盖本地
