# Difit 评测

## 使用此技能的场景

difit 会打开一个外部浏览器 UI 并启动一个长时间运行的本机服务器，因此启动它必须是明确的主动选择：

- 仅在用户明确提及 difit、要求在 difit 查看器中打开、显示或注释评测时，或通过名称调用此技能时使用此技能。
- 不要将其用于普通的评测请求，例如“评审这些更改”、“使用评审代理”、“在此 diff 中查找问题”或“评审此 PR/提交/分支”。正常进行这些评测，并在您的回复中报告结果。
- 当请求不明确时，优先选择非 difit 的评测路径。

## 概述

此技能会在易于人类阅读的查看器中启动请求的 git diff。同时，代理可以通过 `--comment` 选项附加任意评论。
这种评论机制非常适合代码评测结果和代码解释。
在运行命令之前，使用以下规则选择 `<difit-command>`：

- 如果 `command -v difit` 成功，则使用 `difit`。
- 否则，使用 `npx difit`。
- 如果回退到 `npx difit` 需要在没有网络权限的沙盒环境中进行网络访问，则在运行之前请求提升权限和用户批准。

## 步骤

最终的命令通常如下所示：

```bash
<difit-command> <目标> [比较目标] \
  --comment '{"type":"thread","filePath":"src/foobar.ts","position":{"side":"old","line":102},"body":"line 1\nline 2"}' \
  --comment '{"type":"thread","filePath":"src/example.ts","position":{"side":"new","line":{"start":36,"end":39}},"body":"Range comment for L36-L39"}'
```

详细步骤如下：

1. 确定目标 diff 并查看其内容。

- 检查用户指定的 diff。这可能是一个本地 git 版本、一个 GitHub URL、一个补丁文件或类似内容。
- 正常理解 diff，必要时检查周围代码，并思考用户请求所需的回复，无论是评测结果、解释还是其他内容。
- 对于 PR 评测，本地检查 PR 并将评测结果限制为 difit 输出。不要将评论回帖到远程 GitHub。

2. 附加准备好的评论并启动 difit — 或重用正在运行的服务器。

- **启动前重用**
  - 每个 Git 根和评测目标最多保留一个活动的 difit 服务器。如果你之前启动的 difit 服务器仍然在运行相同的目標，不要启动另一个或重新打开其 URL；使用 `<difit-command> comment add --port <端口> '<json>'`（与 `--comment` 相同的 JSON 格式）将新发现添加到其中，并让打开的页面获取它们。
  - 如果预期会重复评测轮次，使用 `--keep-alive` 或 `--background`（一个不自动打开浏览器的分离式保持活动服务器，打印 JSON 连接信息，如 `{"port":4966,"url":"http://localhost:4966","pid":123}`）启动，然后使用 `comment add` / `comment get --port <端口>` 进行后续轮次。
- **difit 启动选项**
  - 使用 `<difit-command> <目标> [比较目标]` 指定目标 diff。
  - 对于未提交的更改使用 `<difit-command> .`，对于工作区更改使用 `<difit-command> working`，对于已暂存的更改使用 `<difit-command> staged`。
  - 对于标准输入输入，使用类似 `diff -u file1.txt file2.txt | <difit-command>` 的形式。
- **评论参数**
  - 对每个评论使用 `type: "thread"`。
  - 使用用户使用的语言编写评论正文。
  - 对于 diff 目标侧存在的行，使用 `position.side: "new"`。
  - 对于仅在删除侧存在的行，使用 `position.side: "old"`。
  - 对于跨多行的问题，使用范围评论。
  - 不要从 diff 中复制密钥、令牌、密码、API 密钥、私钥或其他凭证类材料到 `--comment` 正文或任何命令行参数中。
- **尚未添加到 git 的文件的附加参数**
  - 对于未提交的更改，如果你决定尚未添加到 git 的文件也应出现在 diff 中，添加 `--include-untracked`。

3. 分享 difit URL 并完成回复。
   - 如果没有要附加的评论，请明确说明。
   - 不需要手动验证启动的 difit 页面。
