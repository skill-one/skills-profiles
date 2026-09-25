要审查一个 Meticulous 测试运行，请按照以下步骤逐步使用 CLI 或 MCP 命令进行操作，如所述。

> 开始之前，运行 `meticulous-cli-update` 技能以确保 Meticulous CLI 和技能是最新版本——除非它已经在此对话中更早运行过，在这种情况下可以跳过。

这个技能将你视为**审查者，而不是实施者**——即使你之前在此对话中编写了更改。它的任务是发现回归问题，而不是迭代实现（如果你处于实施过程中并希望循环使用 Meticulous 直到看起来正确，请使用 `meticulous-iterative-dev` 技能进行具有预期视觉更改的功能工作，或在 UI 必须不更改时使用 `meticulous-zero-diff-task` 技能；如果差异已经审查并拒绝，你只是来修复被标记的问题，请使用 `meticulous-fix` 技能）。

## 第 0 步 -- 确定预期结果

在查看任何差异之前，弄清楚此 PR 应该产生什么视觉更改：

- **如果你已经有了完整上下文**（相同的对话实现了更改，或者用户刚刚描述了任务），请使用该上下文。
- **否则**——获取 PR 描述（例如 GitHub 的 `gh pr view <number> --json title,body`，GitLab 的 `glab mr view <id> --output json --jq '{title,description}'`，或 Bitbucket 的 `GET /2.0/repositories/{workspace}/{repo_slug}/pullrequests/{id}?fields=title,description`），并提取其中简要的要点总结，它被称为预期的视觉更改。
- 如果没有提及任何内容，请明确记录——然后每个以下差异都会得到额外的审查，因为没有记录显示它可能是已知、接受的后果。

## 第 1 步 -- 获取重播差异摘要

从本地签出运行，以解决当前提交的 git HEAD 的测试运行——确保 HEAD 与远程 CI 首次运行的远程头匹配（例如 `git pull`），否则你可能会审查一个过时或缺失的运行：

```bash
# CLI（从本地 git HEAD 推断运行）
meticulous agent test-run-diffs

# MCP（git 上下文永远不会推断——首先从提交中解决 testRunId）
get_test_run_for_commit(commitSha="<sha>")
get_test_run_diffs(testRunId="<id>")
```

返回一个 TSV，包含 `replayDiffId`/`screenshotName` 行——一个代表性、优先排序的真实视觉差异子集；按从上到下的顺序处理它们。要显式地针对运行而不是从 HEAD 解析，请传递 `--testRunId <id>` 或 `--commitSha <sha>`。CLI 默认阻塞，直到运行完成（传递 `--dontWaitForTestRunToComplete` 以报告一个进行中的运行并立即退出）；MCP 永不阻塞，因此请持续轮询，直到 `status` 为 `complete`/`failed`。

必须将返回的每一行与第 0 步匹配或标记（参见决策指南），然后才能得出 PR 是好的结论。

## 第 2 步 -- 获取截图图像

对于每个代表性截图：

```bash
# CLI（将图像下载到 ~/.meticulous/agent-images/ 并打印本地路径）
meticulous agent image-files --replayDiffId <replayDiffId> --screenshotName <screenshotName>

# MCP（没有下载到磁盘的工具——而是返回已签名的 URL；获取它们以查看图像）
get_image_urls(replayDiffId="<replayDiffId>", screenshotName="<screenshotName>")
```

打开（或获取）`before`、`after` 和 `diffImage` 以检查更改——`diffImage` 通常是信息最丰富的，突出显示哪些像素发生了变化。即使 DOM 差异看起来很清晰，也要始终检查图像。

## 第 3 步 -- 检查 DOM 差异（用于结构细节）

```bash
# CLI
meticulous agent dom-diff --replayDiffId <replayDiffId> --screenshotName <screenshotName>

# MCP
get_dom_diff(replayDiffId="<replayDiffId>", screenshotName="<screenshotName>")
```

可选：`--context <N|full>`（CLI）控制每个 hunk 周围的上下文行数（默认为 3）。

输出是一个统一差异（`+`/`-`，去除缩进），每个独立更改一个以 `[diff N]` 开头的块——例如（说明性，非实际输出）：

```
[diff 0]
 <div class="item">
-  <span class="label">old label</span>
+  <span class="label" data-flag="true">new label</span>
 </div>
[diff 1]
 <ul class="list">
+  <li>new item</li>
 </ul>
```

## 第 4 步 -- 获取重播时间线（可选，用于诊断意外的差异）

如果一个差异是意外的，并且图像/DOM 无法清楚地说明原因：

```bash
# CLI
meticulous agent timeline-diff --replayDiffId <replayDiffId>

# MCP
get_timeline_diff(replayDiffId="<replayDiffId>")
```

TSV 列：`diff`（` ` 相同，`-` 删除，`+` 添加，`!` 更改），`timeMs`，`event`（`user`/`screenshot`/`network`/`console`/等），`description`。查找失败的网络请求、意外的重定向或可能导致视觉更改的时间异常。

## 第 5 步 -- 决策指南

对于每个代表性截图，将差异图像和 DOM 差异与第 0 步的预期进行比较：

- **预期**——匹配第 0 步的预期更改（或者，如果有完整实施上下文，显然是期望的结果）。检查差异实际上看起来像 _那个_ 更改并且没有更多内容——差异可以按预期出现，但仍然可能捆绑一个额外的、不相关的回归到同一个截图中。无需标记。
- **意外**——未在第 0 步中提及。使用时间线排除失败的请求、重定向或其他异常，然后标记它：
  - **潜在的回归**（真实的副作用，或否则显然是错误的）→ **拒绝**。
  - **与审查中的更改无关**——通常是随机错误，例如亚像素渲染噪声或动画非确定性 → **忽略**。

无论如何标记，都不会静默丢弃——仍需人类查看。

**此技能进行审查和标记——它不修复。** 将被拒绝的差异交给 `meticulous-fix` 技能（或实施更改的人员/技能）——不要在此处尝试代码更改。

## 第 6 步 -- 标记差异

```bash
# CLI
meticulous agent reject-diff --replayDiffId=<id> --screenshotName=<name> --reason="<why>" --x=<0..1> --y=<0..1>
meticulous agent ignore-diff --replayDiffId=<id> --screenshotName=<name> --reason="<why>" --x=<0..1> --y=<0..1>
meticulous agent create-diff-comment --replayDiffId=<id> --screenshotName=<name> --text="<note>" --x=<0..1> --y=<0..1>

# MCP
reject_diff(replayDiffId="<id>", screenshotName="<name>", reason="<why>", x=<0..1>, y=<0..1>)
ignore_diff(replayDiffId="<id>", screenshotName="<name>", reason="<why>", x=<0..1>, y=<0..1>)
create_diff_comment(replayDiffId="<id>", screenshotName="<name>", text="<note>", x=<0..1>, y=<0..1>)
```

对于**每个**被分类为意外的差异，除了将其包含在最终报告中外，请调用 `reject-diff` 或 `ignore-diff`。`--reason` 是你在分类中的简洁解释；`--x`/`--y` 是更改区域的近似归一化坐标，从差异图像中估计。`create-diff-comment` 是对任何你想记录但没有裁决内容的中间选项。

**不对称：** `reject-diff` 写入一个真实的、阻塞性的决策，与人类拒绝相同。`ignore-diff` 什么决定都不做——它只是一个评论，因此差异保持 `unreviewed`，检查保持挂起，无论哪种情况。只有人类才能清除差异，因此不要在最终报告中过分推销 `ignore-diff` 调用，好像它解决了任何问题。

## 第 7 步 -- 最终报告

涵盖**所有重要的视觉更改**。

1. **预期更改**——简短，每行或两行：更改了什么以及它匹配第 0 步的哪个预期。
2. **被标记的差异**（如果有）——审查的重点，因此请给予这些最多的细节：`replayDiffId`/`screenshotName`（链接：`https://app.meticulous.ai/test-runs/<testRunId>/replay-diff/<replayDiffId>?screenshot=<screenshotName>`），你是否拒绝或忽略了它，你在标记时给出的原因（第 6 步），更改看起来像什么，以及你对原因的最佳评估。

只有当每个差异都被匹配或标记时，PR 才是好的。如果任何差异被标记，PR 还不是好的：除了标记本身外，还要向用户清楚地展示。

## 第 8 步 -- 向 Meticulous 报告反馈

**始终作为最后一步来做——它本身就是审查的一部分，不是用户需要请求的东西。** 提交一条简短笔记：Meticulous 是否捕获了真实问题，是否有任何令人困惑的地方，什么让审查更容易。积极的反馈也很重要——这不仅仅是为了报告摩擦。

```bash
# CLI
meticulous agent submit-feedback --message="<one or two sentences>" --outcome=<helped|neutral|hindered> --testRunId=<id> --skill=meticulous-review

# MCP
submit_feedback(message="<one or two sentences>", outcome="<helped|neutral|hindered>", testRunId="<id>", skill="meticulous-review")
```
