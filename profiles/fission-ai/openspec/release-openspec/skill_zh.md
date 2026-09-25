# 发布 OpenSpec

以可恢复状态机的方式运行 OpenSpec 发布工作流。在每次调用时检查 GitHub 的实时状态，并仅执行下一个安全操作。不要假设之前的调用已完成。

## 原则

- 将 `Fission-AI/OpenSpec` 和 `origin/main` 视为发布事实来源。
- 当用户询问状态、准备情况或建议时，默认执行只读审计。
- 将发布请求、准备发布、继续或恢复请求视为执行相应发布操作的授权。
- 保留用户的检出状态。不要为了准备变更集而丢弃不相关的更改或切换其当前分支。
- 当检出状态不干净或不在 `main` 上时，使用从当前 `origin/main` 创建的临时工作树来处理发布作者提交。
- 永不批准自己的 PR。人工审核是一个故意设置的门控。
- 将合并队列条目视为中间状态，而不是合并。只有在 GitHub 报告 `mergedAt` 且提交存在于 `main` 上后才能推进。
- 永不手动创建自动化的版本包 PR。变更集操作负责它。
- 永不推送一个空提交仅仅是为了重新触发 CI。首先诊断失败或缺失的运行。
- 每次暂停时，报告 URL、达到的状态以及所需的确切人工操作。

## 了解两种 PR 类型

在输出和决策中保持这些区分：

- **变更集 PR**：一个正常的由人工编写的 PR，添加一个或多个 `.changeset/*.md` 文件。优先在功能/修复 PR 中添加变更集；仅当已经合并的工作应被包含时才创建一个追赶变更集 PR。
- **版本包 PR**：自动化的 `changeset-release/main` PR，标题为 `chore(release): version packages`。合并或向 `main` 添加变更集会更新同一个 PR。合并它将发布稳定版本。

一个打开的版本包 PR 并不禁止追赶变更集 PR。这意味着只有在审计发现缺失的发布工作需要时，追赶 PR 才有用。一旦该 PR 合并，等待现有的版本包 PR 更新。

## 从发布审计开始

1. 验证仓库和工具：
   - 使用 `gh repo view --json nameWithOwner,url` 解析 GitHub 仓库。
   - 在写操作之前，要求认证的 `gh`、`git` 和 `pnpm`。
   - 如果规范仓库不是 `Fission-AI/OpenSpec`，则在发布变更之前停止。
2. 不修改工作树的情况下刷新：

   ```bash
   git fetch origin main
   ```

   不要无差别地获取每个标签。这个仓库可能包含一个冲突的历史本地标签，即使 `origin/main` 成功获取，`git fetch --tags` 也可能失败。

3. 找到最新的稳定 GitHub 发布。排除草稿和预发布；不要使用 `git describe`，因为一个 beta 标签可能比稳定基线更新。

   ```bash
   gh release list --repo Fission-AI/OpenSpec \
     --exclude-drafts --exclude-pre-releases --limit 100 \
     --json tagName,publishedAt \
     --jq 'max_by(.publishedAt) | {tagName, publishedAt}'
   ```

   确保精确的稳定标签在本地解析后再用作 `git log` 边界。如果缺失，仅获取该标签。如果同名的本地标签与规范远程不一致，报告不匹配并使用单独解析的规范提交；永远不要强制重写用户的标签作为审计的一部分。

4. 找到打开的发布相关 PR：

   ```bash
   gh pr list --repo Fission-AI/OpenSpec --state open \
     --head changeset-release/main \
     --json number,title,headRefName,baseRefName,url,reviewDecision,statusCheckRollup
   ```

   通过 `headRefName == "changeset-release/main"` 来识别版本包 PR，而不是仅通过标题。分别列出可能的变更集 PR 并检查其文件；要求 `.changeset/*.md` 有正向添加。不要将版本包 PR 的变更集删除误认为是编写的变更集，也不要依赖标题，因为功能/修复 PR 可能会添加发布跟踪。
5. 阅读 `.changeset/README.md` 中的实时发布策略、`origin/main` 上待定的 `.changeset/*.md` 文件，以及当存在时版本包 PR 的正文/文件。
6. 列出自最新稳定标签以来的 first-parent 提交：

   ```bash
   git log --first-parent --date=short \
     --pretty=format:'%h%x09%ad%x09%s' <stable-tag>..origin/main
   ```

7. 将发布值得的已合并 PR 映射到现有的变更集。使用 PR 文件和变更集历史；不要仅凭相似的措辞就推断覆盖范围。
8. 将审计分类为：
   - `missing-tracking`：面向用户的、打算用于此发布的工作缺少变更集；
   - `awaiting-changeset-review`：一个合适的变更集 PR 已经存在；
   - `awaiting-merge-queue`：一个已批准的变更集或版本包 PR 已排队但尚未合并到 `main`；
   - `awaiting-version-update`：所需的变更集在 `main` 上，但版本包 PR 尚未包含它们；
   - `awaiting-version-review`：版本包 PR 是当前的但缺少批准；
   - `ready-to-publish`：版本包 PR 是当前的、已批准且绿色；
   - `publishing`：版本包 PR 已合并但工件不完整；
   - `needs-finalization`：npm、标签和 GitHub Release 存在但笔记仍然是原始的；
   - `complete`：包、标签、GitHub Release 和润色后的笔记一致。

以紧凑的审计呈现稳定基线、建议版本、已覆盖变更、可能的遗漏、有意跳过的内部/文档工作、打开的 PR 和下一步操作。

## 决定变更集覆盖范围

遵循 `.changeset/README.md` 而不是假设每个合并的 PR 需要一个变更集。

包含用于发布跟踪的工作，特别是：

- 新的用户界面功能或命令；
- 值得注意的修复或热修复；
- 断开连接的更改或弃用；
- 用户可见的性能改进。

通常跳过仅文档的工作、测试、CI/工具和内部重构。标记模糊的用户可见更改而不是无声地排除它们。只有在模糊之处实质性地改变了发布范围或语义版本时才询问用户；否则使用最佳判断，并让 PR 审核成为批准的门控。

## 创建或继续变更集 PR

仅当 `missing-tracking` 时才这样做。

1. 如果一个打开的变更集 PR 已经覆盖了缺失的工作，则重用它。检查其 `headRefName`、头仓库和 `maintainerCanModify`；从其所属仓库中获取确切的头分支到临时工作树，在那里进行更新并推回相同的 PR 头。如果分支不可写，则停止。不要创建一个重复的 PR 或替换分支。
2. 在编写之前立即阅读 `.changeset/README.md`。
3. 只有在没有合适的 PR 时，从当前的 `origin/main` 创建一个简短的 `changeset-<scope>` 分支。使用临时工作树，以便操作员的检出状态保持不变。
4. 优先每个连贯的发布单元一个变更集。一个单一的追赶变更集可以总结几个为同一发布选择的小项。
5. 使用确切的包名 `"@fission-ai/openspec"`、最高要求的语义提升、相关的标题和用户导向的描述。
6. 在推送之前验证：

   ```bash
   pnpm exec changeset status
   ```

7. 提交、推送并打开一个 PR，其正文列出了已覆盖的合并 PR 并解释了为什么需要追赶。
8. 返回 PR URL 并请求人工批准。不要自己批准它。

在后续调用中，如果 PR 已批准且检查为绿色，则仅在用户要求继续或完成发布时才合并或排队它。如果 GitHub 使用合并队列，检查 `mergeQueueEntry`、排队检查和 `mergedAt`；保持在 `awaiting-merge-queue` 状态，直到 PR 实际合并到 `main`。然后等待 `main` 上的变更集操作更新现有的版本包 PR。使用简洁的进度更新进行轮询；不要推送一个空提交或另一个分支更新，因为那可能会取消批准并重新启动队列。

## 验证版本包 PR

在调用它为准备好之前：

1. 确认它从 `changeset-release/main` 指向 `main` 并由预期的自动化生成。
2. 列出当前 `main` 上每个待定的 `.changeset/*.md` 文件，排除 `.changeset/README.md`。验证 PR 消耗了每一个并包含相应的变更日志内容。如果任何待定的变更集应被推迟，则停止：通过一个单独审查的更改移除或修订它，并等待自动化重新生成版本包 PR 后再继续。
3. 使用 `gh pr view` 获取 `baseRefOid` 和 `headRefOid`，要求 `baseRefOid` 等于当前的 `origin/main`，并为这两个修订创建干净的分离临时工作树。如果头对象在本地缺失，首先获取不可变的 `pull/<number>/head` 引用。永远不要从操作员的当前工作树进行验证。
4. 在基本工作树中，运行 `pnpm exec changeset status --output changeset-status.json` 并从该文件读取预期的包/版本。如果 Changesets CLI 不可用，则首先在临时工作树中安装锁定依赖。
5. 比较基本状态和完整的待定变更集集与头工作树：`package.json`、`CHANGELOG.md`、删除的变更集文件、PR 正文和提议版本必须都一致。这是一个基线到头的比较，因为头已经消耗了变更集，无法自行计算待发布的版本。
6. 验证后删除临时工作树，然后使用 `gh pr view` / `gh pr checks` 检查所有必需的检查和审查状态。

如果当前但未批准，返回 URL 并暂停以供人工批准。如果已批准且绿色，仅在用户要求发布或继续时才合并或排队。启用合并队列时，不要将批准、自动合并启用或队列条目视为稳定的发布触发器；等待 `mergedAt` 并确认合并已到达 `main`。

## 验证稳定发布

版本包 PR 合并后：

1. 找到合并提交的发布工作流运行并等待完成。
2. 独立验证所有三个工件：
   - `npm view @fission-ai/openspec@<version> version`
   - 远程标签 `v<version>` 指向预期的提交；
   - `gh release view v<version>` 存在且不是预发布。
3. 如果仅某些工件存在，报告部分状态并在重试任何发布操作之前继续验证。永远不要重新发布已经存在于 npm 的版本。
4. 一旦所有工件都存在，阅读 [references/release-notes.md](references/release-notes.md)，润色 GitHub Release，并验证保存的标题/正文。

## 发布一个 beta

只有在用户明确要求 beta 或预发布时才进入此路径。

1. 运行相同的审计并确认待定的变更集产生下一个稳定版本。
2. 解释 beta 发布不会消耗变更集或替换稳定的版本包 PR。
3. 在 `main` 上触发现有的 `release-prepare.yml` 工作流；不要在本地计算或设置 beta 版本。
4. 验证工作流选择的版本、npm `beta` 分发标签、远程标签和预发布 GitHub Release。
5. 不要作为 beta 请求的一部分合并稳定的版本包 PR。

## 处理失败

- 对于失败的 CI，在建议重新运行或代码更改之前，检查失败的检查和日志。
- 对于陈旧的版本包 PR，首先确认在最新的变更集到达 `main` 后是否成功运行了 `release-prepare.yml`。
- 对于分支分歧，让变更集操作更新其分支。不要强制推送 `changeset-release/main`。
- 对于排队的 PR，检查合并组检查和队列状态。在它正常进行时，不要重新排队、更新分支或重新运行不相关的检查。
- 对于已经存在于 npm 的版本，停止并协调标签/GitHub Release，而不是隐式地递增或重新发布。
- 对于缺失的 GitHub 权限或必需的审查，报告确切的门控和 URL；保留检测到的状态，以便下一次调用可以通过检查来恢复。

## 完成报告

报告：

- 发布版本和稳定/beta 渠道；
- 变更集 PR 和版本包 PR 的 URL（当适用时）；
- 发布工作流结果；
- npm 包、标签和 GitHub Release 验证；
- 发布笔记最终化状态；
- 任何有意推迟的更改。
