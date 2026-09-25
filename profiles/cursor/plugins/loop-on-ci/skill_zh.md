# 在 CI 中循环

## 触发条件

需要监视一个分支或拉取请求，并在 CI 失败时迭代，直到所有必需的检查都变为绿色。

使用 `gh pr checks` 作为真实情况来源。它包含所有附加到 PR 的检查，而 `gh run list` 仅涵盖 GitHub Actions。

## 工作流程

1. 解决当前分支的 PR。
2. 在等待之前检查当前的 PR 检查。
3. 如果检查已经失败，首先诊断这些失败。
4. 如果检查是挂起的，使用 `gh pr checks --watch --fail-fast` 进行监视。
5. 每次推送后，重新检查完整的 PR 检查集并重复，直到变为绿色。

## 命令

```bash
# 解决活动的 PR
gh pr view --json number,url,headRefName

# 检查所有附加的检查
gh pr checks --json name,bucket,state,workflow,link

# 监视挂起的检查并快速失败
gh pr checks --watch --fail-fast

# 当失败的检查链接到 GHA 运行时，GitHub Actions 日志
gh run view <run-id> --log-failed
```

## 指导原则

- 尽可能将每个修复的范围限制在一个失败原因内。
- 不要跳过钩子 (`--no-verify`) 以强制进度。
- 如果失败显然与 PR 无关，并且主分支上似乎已修复，请合并最新的主分支，而不是在 PR 中添加不相关的修复以使其膨胀。
- 如果失败是间歇性的，请重试一次并报告间歇性证据。
- 每次推送后重新运行 `gh pr checks --json name,bucket,state,workflow,link`；检查集可能会变化。

## 输出

- 当前 CI 状态
- 失败摘要和已应用的修复
- 检查变为绿色后的 PR URL
