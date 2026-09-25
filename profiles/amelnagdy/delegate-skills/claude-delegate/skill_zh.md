# Claude 委托

你是**协调者**。将一个有边界的编码任务委托给一个单独的**执行者**——一个 Claude 代码 CLI 会话——然后审查它生成的内容，并亲自将其部署。你编写简报并拥有判断权；单独的 Claude 会话编辑工作树；你进行验证并提交。

这项技能不是当前 Claude 直接实施的信号。只有在人类明确要求将委托给另一个 Claude 代码进程或会话后，才使用它。

## 不应使用此技能的情况

- 人类要求当前代理直接实施任务。
- 任务足够小，可以内联完成，并且人类没有要求委托。
- `claude` CLI 缺失或未通过身份验证（`claude auth status`）。
- 任务需要一个比 Claude 代码的工具权限和仅限 shell 的沙盒提供的更强的主机边界。为此需求使用隔离的容器或虚拟机。

## 前提条件

1.  `claude --version` 成功。
2.  `claude auth status` 报告一个经过身份验证的会话。在 macOS 上，实时凭证位于登录密钥链中；当协调者的沙盒阻止密钥链访问（Codex 的沙盒就是这样）时，`claude` 会回退到一个可能过时的凭证文件，并报告 `loggedIn: false`，即使登录有效。在提升该沙盒权限或在其外部重新运行检查——以及调度本身——之前得出 CLI 未通过身份验证的结论。
3.  目标存储库是使用 `--cd` 传递的目录。
4.  在 Linux/WSL2 上，Claude 的沙盒依赖项已安装。正常的转发配置文件在沙盒不可用时配置失败，而不是静默地无沙盒运行 shell 命令。现有的合并设置仍然会影响有效边界。

## 循环过程

### 1. 编写简报

单独的会话没有协调者聊天历史记录。它通过标准输入接收简报并可以检查目标工作树。

Claude 代码自动发现目标项目的 `CLAUDE.md` 和正常的本地 Claude 配置，因为转发配置文件不使用 `--bare`。它**不**通用地自动加载 `AGENTS.md`。自己阅读 `AGENTS.md` 并将每个承载约束和真实的门禁命令复制到简报中。告诉执行者不要提交。每个简报保持一个任务。

模板和详细信息：[references/writing-the-brief.md](references/writing-the-brief.md)。

### 2. 调度

```bash
node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --cd /path/to/repo
# 仅用于审查/诊断：                 添加 --read-only
# 继续最新会话：                   添加 --resume-last
# 继续记录的会话：                 添加 --session <id>
# 选择限制：                         添加 --max-turns 40 --max-budget-usd 10
# 设置自动压缩窗口：               添加 --autocompact 400k
# 硬转发截止时间：                   添加 --timeout 2h
# 查看每个选项：                    node .../relay.mjs --help
```

`<skill-dir>` 是此安装技能目录，包含此 `SKILL.md` 的文件夹。

转发配置文件运行 `claude -p --output-format stream-json --verbose`，通过标准输入发送简报，并默认在系统临时目录下写入工件。它从不使用 `--bg` 或 `--bare`，并且从不提交。参见 [references/dispatch-and-poll.md](references/dispatch-and-poll.md)。

`--autocompact <auto|tokens>` 将 Claude 代码的自动压缩窗口设置传递给每个新的或恢复的调用，并且需要 Claude 代码 `2.1.221` 或更新版本——旧版本会以 `unknown option '--autocompact'` 失败调度。已安装的 CLI 拥有接受的范围（`auto`，或 100k–1M tokens）；转发配置文件记录请求的值，但不会声称 Claude 应用或执行了它。

### 3. 等待

转发配置文件会阻塞直到 Claude 退出。使用协调者的后台命令功能，或在前台运行并等待。完成意味着进程已退出并且 `result.json` 存在。

- 运行前使用错误退出 2 并不写入 `result.json`。
- 缺失 `claude` 退出 127 并写入 `status: "claude_unavailable"`。
- 超时和捕获的转发配置文件信号终止整个执行者进程树并保留一个结果工件。

从 `result.json` 中读取 `finalMessage`、`touchedFiles`、`resultSubtype` 和原始工件路径。

### 4. 审查

将执行者的报告和门禁结果视为声明：

- 在绿色门禁意味着任何事之前，审查对现有测试的编辑。
- 自己重新运行项目的实际门禁。
- 读取与简报的完整差异，从 `touchedFiles` 开始。
- 检查未跟踪和暂存的内容以及普通的差异。
- 如果已安装，运行相关的守卫技能。

完整清单：[references/review-and-land.md](references/review-and-land.md)。

### 5. 部署

**协调者**只有在门禁通过并且差异有效时才提交。对于返工，使用 delta 简报恢复相同的 Claude 会话：

```bash
echo "保留实现，用迁移的固定装置替换模拟的 DB 测试，并删除未使用的导入。" | node "<skill-dir>/scripts/relay.mjs" --session <id> --cd /path/to/repo
```

像第一次运行一样审查恢复的运行。

## 权限配置文件

正常配置文件故意明确：

- `acceptEdits` 权限模式。
- 内置工具限制为 Read、Glob、Grep、Edit、Write 和平台 shell。
- 在 macOS、Linux 和 WSL2 上，Claude 的 shell 沙盒已启用，缺少依赖项时启动失败，并且不会无沙盒重试。保持在沙盒中的命令会自动批准，因此普通门禁可以无头运行。沙盒管理 shell 进程及其子进程；合并的本地或管理沙盒设置可以添加有效路径或排除项。
- 配置的 MCP 发现和 Claude.ai 连接器被禁用，所有 MCP 工具都被拒绝，并且子进程无法使用技能、命令和 Claude 的 Agent 工具。项目 `CLAUDE.md`、钩子、正常身份验证、会话持久性和其他本地设置仍然加载。
- 字符串规则拒绝常见的直接 shell 形式的 `git commit`、`git push` 和嵌套 `claude`，以及包含 `claude-delegate` 的任何命令。别名、脚本和包装器可以绕过它们，因此它们只是一个障碍；简报的“不提交”指令和协调者审查仍然是边界。

原生 Windows 不支持 Claude 的 shell 沙盒。转发配置文件限制工具表面并预批准 PowerShell，以便运行保持非交互式，但该 shell 不是操作系统隔离的。原生 `claude.exe` 和 npm `claude.cmd` 启动路径已实现；Windows 验证正在等待。

`--read-only` 使用 `plan` 模式，仅包含 Read、Glob 和 Grep。它移除编辑、写入和 shell 路径，然后比较解析的 git 伪器和指纹 Git 可见路径的工作树身份和索引条目的完整性。`readOnlyViolation` 在任一信号证明有更改时为 `true`，在覆盖完整且未检测到任何更改时为 `false`，在覆盖不完整时为 `null`。这是一个报告触发器，不是操作系统边界：忽略的路径和完美恢复在其之外，本地钩子可以写入，并且并发更改无法归因于 Claude。

`--dangerously-skip-permissions` 是明确选择进入 Claude 的 `bypassPermissions` 模式。受限制的工具表面、直接提交/推送拒绝规则和支持的平台的 shell 沙盒仍然保留，但直接文件工具可以跨越正常权限边界。仅在使用人类明确接受时使用它。

## 与原生 Claude 功能互补

当当前 Claude 环境已经是协调者并且目标是原生协调时，Claude 子代理、代理团队和后台会话很有用。这项技能是互补的：它提供了一个跨协调者合同——自包含简报→调度→工件→审查→部署——并将提交保留在协调者。

## 参考文献

- [references/writing-the-brief.md](references/writing-the-brief.md) — 上下文、`CLAUDE.md` 与 `AGENTS.md`、真实门禁、报告合同和 delta 简报。
- [references/dispatch-and-poll.md](references/dispatch-and-poll.md) — 标志、配置文件、工件、`result.json`、轮询和失败恢复。
- [references/review-and-land.md](references/review-and-land.md) — 生成的代码审查、提交边界和会话返工。
- [references/multi-task-queues.md](references/multi-task-queues.md) — 顺序队列、进度跟踪、约束传递和最终一致性。
