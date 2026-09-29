---
name: pr-review-comments
description: 以内联评论的形式在 GitHub Pull Request 上发布来自 JSON 文件的评审结果，并将每个评论附加到其文件和行。当你有一个评审结果列表/JSON（每个结果包含文件路径、行号和消息，如摘要/失败场景）并希望它们作为内联评审评论发布到 PR 上时使用。触发条件包括“在 PR 上发布这些评审评论”、“将评论关联到 PR 中的文件”、“将评审结果发布到 PR”。
---

# PR Review Comments

以内联评论的形式发布一个 JSON 数组格式的评审结果到 GitHub Pull Request 上，
每个评论都锚定到其对应的文件和行。通过经过身份验证的 `gh` CLI 调用 GitHub API，
因此无需处理令牌。

## 前置条件

- 已安装并认证 `gh` CLI (`gh auth status`)。脚本会自动检测仓库（使用 `gh repo view`）；可以通过 `--repo OWNER/REPO` 参数覆盖。
- 要评论的 PR 编号。
- 一个 JSON 文件：一个**对象数组**。每个对象必须包含的键：`file`、`line`。消息来自 `summary` 和/或 `failure_scenario`（合并到正文中），或显式的 `body`。有关完整模式和示例，请参阅 [references/json-schema.md](references/json-schema.md)。

## 主要限制：仅可评论差异行

GitHub 仅接受目标行是 PR 差异部分的内联评论。
`line` 是新文件中的行号（对于删除的行，使用 `side: "LEFT"`）。
脚本会获取 PR 差异，将每个发现与实际代码块进行验证，并**跳过**那些行号不在差异中的评论——将它们报告在最后，以免无声丢失。
无法将行评论附加到未更改、未参与差异的行。

## 工作流程

1. 确认 JSON 路径和 PR 编号。如果仓库不明显，请运行 `gh repo view`。
2. **先进行干运行**以查看将要发布的内容和将被跳过的内容：
   ```bash
   scripts/post_pr_comments.py --pr <N> --json <path> --dry-run
   ```
3. 与用户一起审查“可发布”/“已跳过”的数量。如果行被跳过是因为差异移动了，JSON 中的行号可能已过时——发布前需要协调。
4. 选择模式进行实际发布（见下文）：
   ```bash
   # 分组（默认）：将所有评论捆绑为一个 PR 评审
   scripts/post_pr_comments.py --pr <N> --json <path> --event COMMENT

   # 单独：每个发现一个单独的内联评论
   scripts/post_pr_comments.py --pr <N> --json <path> --mode individual
   ```
5. 报告创建的评审/评论 URL 以及任何被跳过的发现列表。

## 选择模式

| 模式 | 端点 | 使用场景 |
|------|------|----------|
| `grouped` (默认) | `POST /pulls/{n}/reviews` | 发布一组发现作为一次评审。一个通知；可以设置 `--event APPROVE \| REQUEST_CHANGES \| COMMENT`。 |
| `individual` | `POST /pulls/{n}/comments` | 逐步添加独立的评论，或当每个发现应该是自己的线程/通知时。 |

默认使用 `grouped` 模式与 `--event COMMENT`，除非用户想要一个结论或单独的线程。

## 选项参考

```
--pr N              PR 编号（必需）
--json PATH         发现的 JSON 数组（必需）
--repo OWNER/REPO   覆盖自动检测的仓库
--mode grouped|individual   默认：grouped
--event COMMENT|APPROVE|REQUEST_CHANGES   分组模式下的结论（默认 COMMENT）
--review-body TEXT  分组评审的顶层摘要正文
--commit SHA        锚定的提交（默认：PR 头部 SHA）
--dry-run           验证并打印负载而不发布
```

## 注意事项

- 多行范围评论：在 JSON 对象中包含 `start_line`（以及可选的 `start_side`）与 `line`；脚本会将其原样传递。
- 在不熟悉的 PR 上进行实际发布前，始终使用 `--dry-run`——过时的行号是最常见的失败原因，干运行会将其显示为“已跳过”而不会产生副作用。
- 脚本是可靠的方式；不要手动编写 `gh api` 调用——它处理差异验证、仓库/提交检测和正文组装始终一致。
