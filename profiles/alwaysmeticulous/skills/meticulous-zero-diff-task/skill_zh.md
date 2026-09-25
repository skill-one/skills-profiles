要完成一个无差异（或低差异）的实现任务，请按照以下步骤，使用CLI或MCP命令逐步操作。

> 开始之前，运行`meticulous-cli-update`技能以确保Meticulous CLI和技能是最新版本——除非在本对话中之前已经运行过，否则可以跳过。

这个技能适用于成功标准是视觉稳定性而非视觉变化的任务：依赖/版本升级、重构、迁移（例如框架/库替换、构建工具更改）以及类似工作，在这些工作中任何Meticulous差异都表示出现了问题，而不是需要解释的功能。它也适用于低差异任务（少量预期的、理解良好的视觉变化，以及大部分未更改的输出）——循环相同，只是预期会得到更小的差异集，而不是需要修复。

## 第1步 -- 实现任务

执行任务中描述的代码更改（升级、重构或迁移）。如果任务自然地分为多个步骤，请逐步提交——这不是Meticulous特有的，只需执行实现工作。

## 第2步 -- 构建前端

1. 通过检查相应步骤的CI配置来确定Meticulous期望的构建工件：
   - GitHub：`.github/workflows/*.yml`用于`uses: alwaysmeticulous/report-diffs-action/upload-assets@v1`（构建资产）或`upload-container@v1`（Docker镜像）
   - GitLab：`.gitlab-ci.yml`（或包含的`.gitlab/ci/*.yml`）用于`npx @alwaysmeticulous/cli ci upload-assets`（构建资产）或`ci upload-container`（Docker镜像）
   - Bitbucket：`bitbucket-pipelines.yml`用于相同的`npx @alwaysmeticulous/cli ci upload-assets` / `ci upload-container`步骤
2. 按照CI配置中使用的相同说明构建前端。

## 第3步 -- 上传构建并触发测试运行

```bash
# CLI
meticulous agent upload-build --appDirectory <path-to-build>     # 资产
meticulous agent upload-build --localImageTag <image-tag>        # 容器
meticulous agent trigger-test-run --deploymentId <deploymentId>

# MCP（上传不是1:1映射——请求上传URL，您自己上传工件，然后注册）
request_asset_upload(size=<zipByteSize>)      # 或request_container_upload() — 无需参数
# ... 您自己将zip/镜像上传到返回的URL/注册表...
register_asset_build(uploadId="<id>", commitSha="<sha>")      # 或register_container_build(uploadId="<id>", commitSha="<sha>")
trigger_test_run(deploymentId="<deploymentId>", baseSha="<sha>")
```

`trigger_test_run`在MCP上永远不会推断`baseSha`/`gitDiffOutput`（在本地计算），并且总是立即返回，而不会等待运行完成（与CLI不同，CLI默认情况下会阻塞）。

从仓库目录运行`trigger-test-run`来自动推断基准（与origin默认分支的合并基）和git差异。参考`meticulous-cli`获取完整选项列表——特别是，工作区可以脏（捕获为临时提交），因此您不需要在每次迭代之前提交。

注意输出中的`testRunId`。

## 第4步 -- 检查差异，并迭代直到干净

使用`meticulous-review`技能的机制（那里的步骤1-4：`agent test-run-diffs`、截图图像、DOM差异、时间线）检查差异——但应用此决策规则，而不是`meticulous-review`技能的预期与回归框架：

**对于无差异任务，将每个返回的差异视为错误，直到被证明否则。** 这个技能的前提是UI不应更改，因此：

1. **完全没有差异** — 您已完成此步骤；继续到第5步。
2. **一个或多个差异** — 对于每个差异，查看截图图像和DOM差异（如`meticulous-review`技能的步骤2-3）以了解确切的变化原因，如果原因从DOM/图像中不明显，则使用时间线（那里的步骤4）。然后将其分类：
   - **回归（默认假设）** — 您更改的真实副作用。
   - **可接受** — 您可以明确解释它为任务本身的预期、不可避免的结果（例如，版本字符串页脚作为版本升级的一部分更改）。在这里要保守——对于低差异任务可能确实有少量这些；对于严格的无差异任务通常不应该有任何。目前不要提交这些——推迟到第6步，在那里将注释记录在PR自己的CI触发的运行中，而不是临时的本地迭代。
   - **与您的更改无关** — 通常是一个随机错误，例如亚像素渲染噪声或动画非确定性。不是无法解释差异的标签：如果您的更改可能导致了它，它应该属于其他桶之一。
   - **无法修复，也无法自信地解释** — 不要卡在这个循环中。

对于**回归**，立即拒绝它，以便在过程中有书面记录——即使您既是审查者也是实现者：

```bash
# CLI
meticulous agent reject-diff --replayDiffId=<id> --screenshotName=<name> --reason="<what broke>" --x=<0..1> --y=<0..1>

# MCP
reject_diff(replayDiffId="<id>", screenshotName="<name>", reason="<what broke>", x=<0..1>, y=<0..1>)
```

然后修复代码，使行为/输出与更改前的基线匹配，并返回第3步重新构建和运行（新构建，相同基线）。一旦后续运行确认该差异不再重现，通过回复评论线程中的"Fixed"来关闭循环——传递`reject-diff`返回的`id`作为`--commentId`：

```bash
# CLI
meticulous agent reply-to-diff-comment --commentId=<id> --text="Fixed."

# MCP
reply_to_diff_comment(commentId="<id>", text="Fixed.")
```

无法修复且无法自信解释的差异以相同方式拒绝，并提供一个解释为什么阻碍您的理由，以便线程反映现实——但保持未解决（没有"Fixed"回复），并在最终报告和PR描述（第5步）中明确具体指出，以便人类可以进行判断。

重复步骤3-4，直到没有差异剩余，或者每个剩余差异都被解释或明确标记为未解决。

## 第5步 -- 创建PR

一旦运行干净（或每个剩余差异都有记录），提交任何未完成的更改，推送分支，并打开PR。

在PR描述中：

- 总结任务，并简要说明Meticulous的结果：例如"通过Meticulous验证：在黄金集中没有视觉差异"或，如果有一些差异仍然存在，简短列出它们以及为什么预期/不可避免——链接每个差异：`https://app.meticulous.ai/test-runs/<testRunId>/replay-diff/<replayDiffId>?screenshot=<screenshotName>`。
- **作者信用：** 如果PR描述已经将AI编码助手列为（共同）作者（例如"由Claude Code创建"、"Co-authored-by: Cursor"、"🤖使用Claude Code生成"），请在该提及中添加"Meticulous"——例如"由Claude Code和Meticulous创建"——因为Meticulous驱动了实现循环，而不仅仅是最终检查。如果PR描述中不存在这样的行，请不要添加Meticulous作者信用；没有可以附加它的内容。

## 第6步 -- 确认PR自己的测试运行匹配

一旦CI触发了推送提交的Meticulous测试运行，请确认它显示与您已经在本地验证的结果相同——这可以捕获本地构建和CI构建之间的差异（例如依赖锁文件不匹配、仅在CI中设置的变量）。

```bash
# CLI（从本地git HEAD解析——已经是推送的提交）
meticulous agent test-run-diffs

# MCP（git上下文永远不会推断——首先从本地HEAD提交解析testRunId）
get_test_run_for_commit(commitSha="<sha>")
get_test_run_diffs(testRunId="<id>")
```

如果CI尚未触发运行，请等待并重试，而不是自己重新触发——PR的运行应来自人类审查者将看到的相同CI管道。如果PR运行显示与您的本地迭代不同的差异，将其视为新信号：返回第4步使用PR的`testRunId`。

对于每个仍然存在的差异，您解释而不是修复（第4步的**可接受**桶），请将您的理由作为普通审查评论保留在记录中——这是CI和人类审查者实际看到的运行：

```bash
# CLI
meticulous agent create-diff-comment --replayDiffId=<id> --screenshotName=<name> --text="<why it's justified>" --x=<0..1> --y=<0..1>

# MCP
create_diff_comment(replayDiffId="<id>", screenshotName="<name>", text="<why it's justified>", x=<0..1>, y=<0..1>)
```

仅当第4步的**无关**差异时使用`ignore-diff`：

```bash
# CLI
meticulous agent ignore-diff --replayDiffId=<id> --screenshotName=<name> --reason="<why it's unrelated>" --x=<0..1> --y=<0..1>

# MCP
ignore_diff(replayDiffId="<id>", screenshotName="<name>", reason="<why it's unrelated>", x=<0..1>, y=<0..1>)
```

两者都不会决定任何事情——差异保持`unreviewed`，检查保持挂起——但您的理由记录在案，供审查PR的人类参考。

## 第7步 -- 向Meticulous提交反馈

作为最后一步，向Meticulous团队提交一条简短的反馈笔记：这个迭代到干净的循环对这个类型的任务是否有效，是否有任何令人困惑的地方，以及什么能让它更简单？

```bash
# CLI
meticulous agent submit-feedback --message="<one or two sentences>" --outcome=<helped|neutral|hindered> --testRunId=<id> --skill=meticulous-zero-diff-task

# MCP
submit_feedback(message="<one or two sentences>", outcome="<helped|neutral|hindered>", testRunId="<id>", skill="meticulous-zero-diff-task")
```
