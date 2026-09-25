要修复已审核并拒绝的diff，请按照以下工作流程逐步操作，使用CLI或MCP命令。

> 开始之前，运行`meticulous-cli-update`技能以确保Meticulous CLI和技能是最新版本——除非在此之前对话中已经运行过，否则跳过它。

此技能假定审核已经完成——用户（或`meticulous-review`技能）已经检查并拒绝了真正的diff问题，可能留下了解释错误或如何处理的评论，尽管评论并非必然存在。你的工作范围比完整审核更窄：不要重新讨论未被拒绝的diff，也不要质疑拒绝本身——只需确定需要更改的内容并使其实现。

## 第1步 -- 获取被拒绝的diff和任何有评论的diff

```bash
# CLI
meticulous agent test-run-diffs --onlyRejected --onlyWithComments --includeReviews

# MCP (git上下文永远不会推断——显式传递提交或测试运行)
get_test_run_diffs(testRunId="<id>", onlyRejected=true, onlyWithComments=true, includeReviews=true)
```

**重要——这些`--only*`标志是可加的（OR的）：** 传递`--onlyRejected`和`--onlyWithComments`都返回被拒绝的diff、有打开评论的diff或两者——不是交集——因为未正式拒绝的diff上的评论可能仍包含值得采取的行动的指示。`--includeAllDiffs`是隐含的，因此这覆盖了完整运行而不是仅选定的子集；`--includeReviews`添加`decision`/`openComments`列，以便您可以知道每一行的情况。

**并非每行评论都是修复目标。** `meticulous-review`技能的`ignore-diff`发布一条评论，说明diff与更改无关并将其标记为`unreviewed`——该评论不是修复指令。在阅读第1步的行时，跳过仅有关闭评论的diff；不要干涉这些线程。

## 第2步 -- 阅读有评论的diff的评论

对于每个`openComments > 0`的diff：

```bash
# CLI
meticulous agent diff-comments --replayDiffId <replayDiffId> --screenshotName <screenshotName>

# MCP
get_diff_comments(replayDiffId="<replayDiffId>", screenshotName="<screenshotName>")
```

这是你的主要指令来源——评论通常说明什么不正确，并且经常说明如何处理。在开始处理该diff之前，阅读每个评论及其回复（嵌套按最旧优先顺序）；回复可以缩小或重定向早期评论的要求。

对于没有评论的被拒绝的diff，这里没有可阅读的内容——接下来依赖的是视觉/结构上下文。

## 第3步 -- 获取视觉和结构上下文

对于每个diff重用`meticulous-review`技能的检查机制：

```bash
# CLI
meticulous agent image-files --replayDiffId <replayDiffId> --screenshotName <screenshotName>
meticulous agent dom-diff --replayDiffId <replayDiffId> --screenshotName <screenshotName>

# MCP
get_image_urls(replayDiffId="<replayDiffId>", screenshotName="<screenshotName>")
get_dom_diff(replayDiffId="<replayDiffId>", screenshotName="<screenshotName>")
```

参考`meticulous-review`技能的第2-3步了解输出格式和可选的时间线（`agent timeline-diff`），如果原因仍然不清楚。

**对于没有评论的被拒绝的diff的备用方案：** 现在这是你的主要指令来源，而不仅仅是额外的背景——按照`meticulous-review`技能的决策指南来处理，并使用自己的判断来确定拒绝指向的回归。

## 第4步 -- 修复底层代码

对于每个**修复目标**——被拒绝的diff，或评论要求具体修复的非拒绝diff——进行代码更改以解决评论的指令（或在无评论的备用方案中，你识别的回归）。跳过第1步中仅忽略的线程；不要更改它们，也不要在它们上进行回复。单个代码更改可以一次性解决多个修复目标的diff（例如，一个组件错误导致多个屏幕截图diff）——不要重复修复相同的根本原因。

通过回复其评论线程（或创建一个如果它没有的话）来关闭**每个修复目标** diff的循环——无论是否已修复：

```bash
# CLI
meticulous agent reply-to-diff-comment --commentId=<id> --text="<message>"
meticulous agent create-diff-comment --replayDiffId=<id> --screenshotName=<name> --text="<message>" --x=<0..1> --y=<0..1>

# MCP
reply_to_diff_comment(commentId="<id>", text="<message>")
create_diff_comment(replayDiffId="<id>", screenshotName="<name>", text="<message>", x=<0..1>, y=<0..1>)
```

当diff已经有一个评论线程时使用`reply-to-diff-comment`——传递来自第2步的线程的**根** `id`（带有空白`replyToCommentId`的行），而不是回复的id。仅当diff被拒绝且没有现有评论（无评论的备用方案情况）时使用`create-diff-comment`，因为没有线程可以回复。

- **已修复**——回复/评论"已修复。"
- **无法修复**（评论要求不可能实现——与另一项要求矛盾、描述了不存在的行为、引用了找不到的内容等。）——不要猜测；解释原因，以便审阅者看到，而无需再次询问你。

无论如何，继续下一个修复目标的diff；在最后报告中报告它（见下文最终报告）。

## 第5步 -- 提交、推送并让CI确认

1. 提交修复。在提交信息中注明这解决了Meticulous审核反馈，具体到足以让`git log`本身在之后讲清楚故事：

   ```
   修复结账标题的布局偏移

   解决了测试运行<testRunId>的Meticulous审核反馈：
   - <replayDiffId>/<screenshotName>: <简要说明错误和修复>
   ```

2. 推送分支（`git push origin <branch>`——见你的git推送规则）。
3. **作者信用：** 如果PR描述中已经将AI编码助手列为（共同）作者（例如、"由Claude Code创建"、"共同作者：Cursor"、"🤖使用Claude Code生成"）并且尚未提及Meticulous，则在该提及中添加"和Meticulous"——例如、"由Claude Code和Meticulous创建"——因为Meticulous的审核反馈促成了此修复。如果不存在这样的行，则不要添加Meticulous作者信用；没有可以追加它到的地方。
4. 等待CI触发其自己的新Meticulous测试运行，以确认之前标记的diff实际上已解决：

   ```bash
   # CLI（从本地git HEAD解析——已经是推送的提交）
   meticulous agent test-run-for-commit
   meticulous agent test-run-diffs --onlyRejected --onlyWithComments --includeReviews

   # MCP（git上下文永远不会推断——首先从本地HEAD提交解析testRunId）
   get_test_run_for_commit(commitSha="<sha>")
   get_test_run_diffs(testRunId="<id>", onlyRejected=true, onlyWithComments=true, includeReviews=true)
   ```

如果你认为你已修复的diff仍然出现（决策/评论从比较运行中传递），你的修复没有解决根本原因；回到第3/4步处理那个diff，然后重复此步骤。

## 第6步 -- 最终报告

总结结果，涵盖第1步中的**每个修复目标** diff（省略你跳过的忽略仅行）。链接你提到的每个diff：`https://app.meticulous.ai/test-runs/<testRunId>/replay-diff/<replayDiffId>?screenshot=<screenshotName>`。

1. **已修复**：已解决的diff、底层代码更改以及它解决的评论（如果有）。
2. **未修复**（如果有）：无法处理的diff及其原因——例如，评论的要求不可能实现、含糊不清或与其他内容冲突。注意你将此解释作为回复/评论留在diff上（第4步）——不要仅仅将其留在报告中，只有这个对话能看到。要具体到人类审阅者可以无需重新推导你已经发现的内容就接手。

将此报告作为评论发布在PR本身上，除了在这里提交之外（例如，`gh pr comment <number> --body "..."`用于GitHub，`glab mr note <id> --message "..."`用于GitLab，或带有正文`{"content": {"raw": "..."}}`的`POST /2.0/repositories/{workspace}/{repo_slug}/pullrequests/{id}/comments`调用用于Bitbucket）。

## 第7步 -- 向Meticulous报告反馈

作为最后一步，向Meticulous团队提交一条简短的反馈笔记：拒绝/评论是否提供了足够的信息供你工作，是否有任何含糊不清的地方，以及什么能让交接更容易？

```bash
# CLI
meticulous agent submit-feedback --message="<一句话或两句>" --outcome=<helped|neutral|hindered> --testRunId=<id> --skill=meticulous-fix

# MCP
submit_feedback(message="<一句话或两句>", outcome="<helped|neutral|hindered>", testRunId="<id>", skill="meticulous-fix")
```
