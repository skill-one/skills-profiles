# Difit

## 使用此技能的场景

difit 会打开外部浏览器界面并启动一个长时间运行的本机服务器，因此启动它必须经过明确的用户选择：

- 仅在用户明确调用 difit、要求在查看器中打开或显示差异，或具有持续指令（例如在项目文档或代理配置中）要求在代码更改后通过 difit 进行代码审查时使用此技能。
- 不要用于普通的代码审查请求，例如“审查这些更改”、“使用审查代理”、“在此差异中查找问题”或“审查此 PR/提交/分支”。通过您正常的响应渠道回答这些请求。
- 当请求不明确时，优先选择非 difit 路径。

## 概述

此技能使用 difit 请求用户进行代码审查。
在运行命令之前，根据以下规则选择 `<difit-command>`：

- 如果 `command -v difit` 成功，则使用 `difit`。
- 否则，使用 `npx difit`。
- 如果回退到 `npx difit` 需要在没有网络权限的沙盒环境中进行网络访问，请在运行它之前请求提升权限和用户批准。

如果用户留下了审查评论，它们将在选择的 difit 命令退出时打印到 stdout。
当返回审查评论时，继续工作并处理它们。
如果服务器在没有评论的情况下关闭，将其视为“未提供审查评论”。无需重新启动它。
也无需手动验证页面是否正确启动。

## 命令

- 在提交前审查未提交的更改：`<difit-command> .`
- 审查 HEAD 提交：`<difit-command>`
- 审查暂存区更改：`<difit-command> staged`
- 仅审查未暂存的更改：`<difit-command> working`

基本用法：

```bash
<difit-command> <目标>                    # 查看单个提交的差异。例如：difit 6f4a9b7
<difit-command> <目标> [与...比较]     # 比较两个提交/分支。例如：difit feature main
```

## 可选的启动评论

如果您希望在 difit 打开时告诉用户一些内容，请将其作为启动评论附加到 `--comment`。

这对于审查结果、解释以及用户应在差异中直接看到的任何上下文很有用。

```bash
<difit-command> <目标> [与...比较] \
  --comment '{"type":"thread","filePath":"src/foobar.ts","position":{"side":"old","line":102},"body":"line 1\nline 2"}' \
  --comment '{"type":"thread","filePath":"src/example.ts","position":{"side":"new","line":{"start":36,"end":39}},"body":"Range comment for L36-L39"}'
```

- 对每个评论使用 `type: "thread"`。
- 使用用户正在使用的语言编写评论正文。
- 对于目标侧的差异中存在的行，使用 `position.side: "new"`。
- 对于仅在删除侧存在的行，使用 `position.side: "old"`。
- 对于跨多行的问题，使用范围评论。
- 不要从差异中复制密钥、令牌、密码、API 密钥、私钥或其他凭证类材料到 `--comment` 正文或任何命令行参数中。

## 包含未跟踪文件

对于未提交的更改，如果尚未添加到 git 的文件也应出现在差异中，请添加 `--include-untracked`。

```bash
<difit-command> . --include-untracked
```

## 重用正在运行的服务器

每个 Git 根和审查目标最多保留一个活动的 difit 服务器。在启动审查后编辑时，重用正在运行的服务器而不是启动另一个——重复启动会创建重复的端口和浏览器标签。

- 在启动 difit 之前，检查您之前启动的 difit 服务器是否仍在为相同的 Git 根运行（例如，您启动的后台进程是否仍然存活）。
- 如果为相同的目标运行一个，则不要启动另一个，也不要重新打开其 URL。对于工作树目标（`.`, `working`, `staged` 和 HEAD 默认），difit 监视存储库，打开的页面在差异更改时提示用户重新加载。
- 如果预期审查轮次会重复，使用 `--keep-alive` 启动服务器（服务器在浏览器断开连接时存活）或 `--background`（一个分离的 keep-alive 服务器；打印 JSON 如 `{"port":4966,"url":"http://localhost:4966","pid":123}` 并且不会自动打开浏览器，因此一次与用户共享 URL）。
- 在服务器保持活动状态时，无需重新启动它即可交换反馈：
  - `<difit-command> comment get --port <端口>` — 读取用户的审查评论（`--format json` 用于结构化输出）。
  - `<difit-command> comment add --port <端口> '<json>'` — 向运行的服务器添加新评论（与 `--comment` 相同的 JSON 结构）。
  - `<difit-command> comment resolve <threadId...> --port <端口>` — 解决您已处理的线程。
- 如果审查目标更改（例如，不同的提交范围），停止现有服务器并启动一个新的服务器，而不是为同一存储库保留两个服务器。

## 限制

只能在 Git 管理的目录内使用。
