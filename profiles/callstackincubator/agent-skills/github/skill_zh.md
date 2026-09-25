# GitHub 模式

## 工具

对所有 GitHub 操作使用 `gh` CLI。优先使用 CLI 而不是 GitHub MCP 服务器，以减少上下文使用。

## 快速命令

```bash
# 从当前分支创建 PR
gh pr create --title "feat: 添加功能" --body "描述"

# 合并 PR 并压缩
gh pr merge <PR_NUMBER> --squash --title "feat: 添加功能 (#<PR_NUMBER>)"

# 查看 PR 状态和检查
gh pr status
gh pr checks <PR_NUMBER>
```

## 堆叠 PR 工作流总结

当合并一系列堆叠的 PR（每个 PR 都针对前一个分支）时：

1. **合并第一个 PR** 通过压缩合并到 main
2. **对于每个后续的 PR**：在 main 上变基，更新基础为 main，然后压缩合并
3. **在冲突时**：停止并要求用户手动解决

```bash
# 将下一个 PR 的分支变基到 main，排除已合并的提交
git rebase --onto origin/main <old-base-branch> <next-branch>
git push --force-with-lease origin <next-branch>
gh pr edit <N> --base main
gh pr merge <N> --squash --title "<PR 标题> (#N)"
```

有关完整分步详情，请参阅 [stacked-pr-workflow.md][stacked-pr-workflow]。

## 快速参考

| 文件 | 描述 |
| --- | --- |
| [stacked-pr-workflow.md][stacked-pr-workflow] | 将堆叠的 PR 作为单独的压缩提交合并到 main |

## 问题 -> 技能映射

| 问题 | 从这里开始 |
| --- | --- |
| 干净地合并堆叠的 PR | [stacked-pr-workflow.md][stacked-pr-workflow] |

[stacked-pr-workflow]: references/stacked-pr-workflow.md
