# 合并打开的 PR

快照打开的 PR。这个列表就是工作集。通过 forge 逐个合并每个 PR，保持后续 PR 可更新到默认分支的顺序。不要将独立的 PR 组合成一个堆栈，也不要用合并后的单个 PR 替换工作集。

基本规则：

- **工作集不会增长。** 快照后打开的 PR 会被忽略。每次合并后，比较剩余的打开 PR 与工作集；不要合并额外的内容。
- **仓库合并策略控制新鲜度。** 每次合并后，重新检查剩余的 PR。只有在冲突、依赖项变更或仓库明确的新鲜度要求下才更新分支。仅基础移动不会使未变更的 PR 头部的通过检查失效。
- **每个 PR 都要通过 forge。** 不要合并到本地默认分支并推送，也不要直接推送到默认分支。仅在 PR 自己的分支上做本地 git 工作，在之后移除临时工作区。

## 1. 快照工作集

```sh
gh api --paginate 'repos/{owner}/{repo}/pulls?state=open&per_page=100' \
  --jq '.[] | {number,title,headRefName:.head.ref,headRefOid:.head.sha,baseRefName:.base.ref,isDraft:.draft}'
```

逐页读取。如果用户指定了特定的 PR，这些就是工作集；否则所有打开的 PR 都是。记录编号、头部 SHA 和头部分支。

对于非单个明显 PR 的情况，构建文件重叠映射：

```sh
gh pr view <n> --json files,headRefName,headRefOid,baseRefName,isDraft,reviewDecision,statusCheckRollup,isCrossRepository,maintainerCanModify
gh pr diff <n>
```

未就绪的 PR（草稿、请求变更）保留在工作集中。使其可合并；不要丢弃它，也不要在未获用户指示的情况下覆盖未处理的请求变更。

如果工作集为空，停止。

## 2. 选择合并顺序

文件互斥的 PR 不会在文本上冲突，所以按语义和可验证性排序。优先顺序：

- 首先合并小型的独立 PR（配置调整、依赖项更新、有助于验证后续 PR 的工具）。
- 基础 PR 优先于依赖 PR：当一个 PR 调用另一个 PR 添加的内容时，先合并依赖项。
- 最后合并共享状态的 PR：版本常量、迁移编号或已提交的生成工件与所有已合并内容复合。
- 其他情况按影响范围，从小到大。

如果某个 PR 的基础是另一个工作集 PR，先合并父 PR。现有的基础链是证明该顺序的证据。用户指定的顺序优先。在开始前，为每个 PR 说明顺序和一条简短理由。

## 3. 了解门禁

```sh
gh repo view --json mergeCommitAllowed,squashMergeAllowed,rebaseMergeAllowed
gh api repos/{owner}/{repo}/branches/{branch}/protection   # 即使有门禁也可能 404
gh api repos/{owner}/{repo}/rulesets
```

在 `gh pr merge` 中显式传递仓库的合并方法。规则集和经典保护是分开的；检查两者以确认所需的检查、所需评审和严格的最新政策。

## 4. 合并每个 PR

在临时工作区中工作。对于每个按顺序的 PR：

1. 获取。记录默认分支的尖端。
2. 如果这个 PR 的基础是另一个工作集 PR，等待父 PR 已合并。当 GitHub 尚未重新目标时，使用 `gh pr edit <n> --base <default-branch>` 重新目标。
3. 检查该 PR 是否根据仓库策略需要基础更新。在它的分支上解决冲突，使用 [resolve-pr-conflicts](../resolve-pr-conflicts/SKILL.md)。确认 `isCrossRepository` 和 `maintainerCanModify` 与将要更新的远程仓库匹配。除非已获授权，否则在重写不属于你的分支前获取明确批准，并披露所有重写。
4. 推送任何必要的更新。草稿会阻塞：首先使用 `gh pr ready`，在草稿是故意的情况下提供用户指示。
5. 使用该 PR 自身的仓库检查进行验证：构建、格式化、代码检查及其影响范围的所有测试。使用 [babysit](../babysit/SKILL.md) 等待该 PR 的所有必需检查变为绿色。如果该 PR 无法在当前默认分支上变为可合并，停止并询问。
6. 重新读取头部 SHA、可合并性和仓库门禁。新头部需要其自身的通过检查。基础移动只有在仓库策略或新冲突需要时才需要另一个更新。然后：

```sh
gh pr view <n> --json headRefOid
gh pr merge <n> <verified-method-flag> --delete-branch --match-head-commit <sha>
```

合并队列会排队 PR 并选择自己的方法；等待它合并后再开始下一个 PR。

如果队友推送到工作集分支，检查并保留他们的变更，可能时协调，并验证新头部。只有在所有权或预期解决方案不明确时才询问。已关闭的 PR 不再可合并：报告它并继续处理独立的 PR。如果有人合并了工作集 PR，继续处理剩余的 PR。

`--admin` 仅在明确批准并披露报告中时使用。

合并完成后，验证仓库在默认分支上的所需集成结果。使用其 CI 运行（如果提供所需证据）；运行额外的本地检查以覆盖未发现的风险。移除工作区。

## 5. 报告

1. 工作集 PR、作为后续到达被忽略的 PR，以及文件是否重叠。
2. 合并顺序及每个 PR 的原因。未合并的工作集 PR 及原因。
3. 解决的冲突、重写的分支、任何绕过。
4. 默认分支移动及你如何处理它们。
5. 你运行的内容及通过的内容，包括在最终默认分支上。
6. 最终默认分支 SHA 和剩余的打开 PR。

如果请求链式发布，在合并提交的 CI 变绿后使用 `$tag-release`。
