# GitHub

使用 `gh` 表示 GitHub。使用 `git` 表示本地提交/分支/推送/拉取。使用代码阅读工具进行深度审查。

## 认证

```bash
gh auth status
gh auth login
```

网关 HOME 可能与操作者 HOME 不同。如果 `gh` 认证存在于其他地方，请在网关服务环境中设置 `GH_CONFIG_DIR` 并重启。

## PRs

```bash
gh pr list --repo owner/repo --json number,title,state,author,url
gh pr view 55 --repo owner/repo --json title,body,author,files,commits,reviews,reviewDecision
gh pr checks 55 --repo owner/repo
gh pr diff 55 --repo owner/repo
gh pr create --repo owner/repo --title "feat: 标题" --body-file /tmp/pr.md
gh pr merge 55 --repo owner/repo --squash
```

在创建或刷新 PR 正文时，仅在运行时行提供 `sessionUrl=<确切URL>` 时才附加此最终页脚。将 `<sessionUrl>` 替换为该 URL 的确切内容；不要构建或修改它。当 `sessionUrl` 缺失时，省略页脚。保留任何发布标记，并在确切一个页脚之前保留，并保持页脚为最终：

```text
---
[查看 OpenClaw 团队会话](<sessionUrl>)
```

URL 可以直接使用：`gh pr view https://github.com/owner/repo/pull/55`。

### 落地所有权

当用户请求落地或合并 PR 时，终端结果是 PR 的验证 GitHub 状态，而不是审查结束、工作轮次或 CI 观察。

- 保持作业活动，直到 `gh pr view ... --json state,mergedAt,mergeCommit` 证明 `state` 是 `MERGED`。
- 当它们在范围内时，将审查发现、合并冲突、失败检查和请求的更改视为延续工作。修补它们，重新运行所需的网关，并重新评估确切的更新头。
- 挂起的检查是等待状态，不是完成。使用仓库支持等待或合并工作流；不要从部分绿色的检查中声称成功。
- 如果工作已委托给持久会话，并且该运行在合并前停止，请继续相同的会话，而不是将其报告视为最终结果。
- 仅当继续需要新的权限、不可用的凭证或无法安全推断的产品决策时才停止阻塞。报告确切的阻塞项，并保留 PR 未合并。

## Issues

```bash
gh issue list --repo owner/repo --state open --json number,title,labels,url
gh issue view 42 --repo owner/repo --json title,body,comments,labels,state
gh issue create --repo owner/repo --title "Bug: ..." --body-file /tmp/issue.md
gh issue comment 42 --repo owner/repo --body-file /tmp/comment.md
gh issue close 42 --repo owner/repo --comment "已修复于 ..."
```

## CI/运行

```bash
gh run list --repo owner/repo --limit 10
gh run view <run-id> --repo owner/repo --json status,conclusion,headSha,url
gh run view <run-id> --repo owner/repo --log-failed
gh run rerun <run-id> --repo owner/repo --failed
```

## API

```bash
gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'
gh api repos/owner/repo/labels --jq '.[].name'
gh api --cache 1h repos/owner/repo --jq '{stars: .stargazers_count, forks: .forks_count}'
```

使用 `--json` + `--jq` 获取结构化输出。使用 `--body-file` 用于包含反引号、shell 段落、环境名称或用户文本的评论/正文。
