# PR Review Comments

以内联评论的形式发布一个 JSON 数组，其中包含审查结果，每个评论都锚定到其文件和行。通过经过身份验证的 `gh` CLI 使用 GitHub API，因此无需处理令牌。

## 前置条件

- 已安装并认证 `gh` CLI (`gh auth status`)。脚本会自动检测存储库（使用 `gh repo view`）；要覆盖，请传递 `--repo OWNER/REPO`。
- 要评论的 PR 编号。
- 一个 JSON 文件：一个**对象数组**。每个对象所需的键：`file`、`line`。消息来自 `summary` 和/或 `failure_scenario`（合并到正文中），或一个显式的 `body`。有关完整模式和示例，请参阅 [references/json-schema.md](references/json-schema.md)。

## 主要约束：仅可评论差异行

GitHub 仅接受如果目标行是 PR 差异的一部分的内联评论。`line` 是新文件中的行号（对于删除的行，使用 `side: "LEFT"`）。脚本会获取 PR 差异，将每个发现与实际代码块进行验证，并**跳过**那些行号不在差异中的评论——在末尾报告它们，以免无声丢失。无法将行评论附加到未更改、未差异的行。

## 工作流程

1. 确认 JSON 路径和 PR 编号。如果存储库不明显，请运行 `gh repo view`。
2. **先进行干运行**，以查看将要发布的内容和将被跳过的内容：
   ```bash
   scripts/post_pr_comments.py --pr <N> --json <path> --dry-run
   ```
3. 与用户一起审查“可发布”/“跳过”计数。如果由于差异移动而跳过行，则 JSON 中的行号可能已过时——发布前需要协调。
4. 选择模式进行实际发布（见下文）：
   ```bash
   # 分组（默认）：将所有评论捆绑在一个 PR 审查中
   scripts/post_pr_comments.py --pr <N> --json <path> --event COMMENT

   # 单独：每个发现一个单独的内联评论
   scripts/post_pr_comments.py --pr <N> --json <path> --mode individual
   ```
5. 报告创建的审查/评论 URL 以及跳过的发现列表。

## 选择模式

| 模式 | 端点 | 使用场景 |
|------|----------|----------|
| `grouped` (默认) | `POST /pulls/{n}/reviews` | 发布一组发现作为一次审查。一个通知；可以设置 `--event APPROVE \| REQUEST_CHANGES \| COMMENT`。 |
| `individual` | `POST /pulls/{n}/comments` | 逐步添加独立评论，或当每个发现应为其自己的线程/通知时。 |

默认使用 `grouped` 模式和 `--event COMMENT`，除非用户想要一个结论或单独的线程。

## 选项参考

```
--pr N              PR 编号（必需）
--json PATH         发现的 JSON 数组（必需）
--repo OWNER/REPO   覆盖自动检测的存储库
--mode grouped|individual   默认：grouped
--event COMMENT|APPROVE|REQUEST_CHANGES   分组模式下的结论（默认 COMMENT）
--review-body TEXT  分组审查的顶层摘要正文
--commit SHA        锚定的提交（默认：PR 头部 SHA）
--dry-run           验证并打印负载，但不发布
```

## 注意事项

- 多行范围评论：在 JSON 对象中包含 `start_line`（以及可选的 `start_side`）；脚本会将其传递。
- 在对不熟悉的 PR 进行实际发布之前，始终使用 `--dry-run`——过时的行号是最常见的失败原因，干运行会将它们显示为“跳过”，而不会产生副作用。
- 脚本是可靠的方法；不要手动编写 `gh api` 调用——它处理差异验证、存储库/提交检测和正文组装始终一致。
