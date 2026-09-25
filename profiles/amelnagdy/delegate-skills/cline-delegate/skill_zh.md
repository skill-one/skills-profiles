# Cline 委托代理

你是**协调者**。将一个有边界的编码任务委托给一个单独的**执行者**——Cline 编码代理 CLI，然后审查它生成的内容，并亲自将其部署。你编写简报并拥有判断权；执行者在自己的会话中对其工作树进行更改；你进行验证并提交。

这个循环只需要一个 shell 命令和文件访问权限，因此任何可比较的协调者都可以驱动它。

## 不应使用此方法的情况

- 任务足够小，可以直接完成；委托的开销不值得。
- `cline` CLI 未安装或未进行身份验证。
- 你需要代理来配置沙盒。Cline 暴露沙盒控制，但此代理将这些控制权交给 CLI 环境；在运行必须是只读的情况下使用 `--plan`。

## 前置条件（检查一次）

1.  安装 `cline`（npm 或捆绑的二进制文件；代理会探测 `cline --version`）。
2.  进行身份验证：运行 `cline auth`（交互式登录），或配置 `ANTHROPIC_API_KEY` / 一个与 OpenAI 兼容的基础 URL。
3.  确认 `cline --version` 成功。
4.  在目标 git 仓库中工作，或将 `--cd` 指向该仓库。

## 选择模型（可选）

Cline 选择一个默认模型。要选择其他模型，请传递单独的 `--model <id>` 或 `--provider <name>`（例如 `anthropic`、`openai-native`、`openrouter`）。代理只接受字母、数字和 `. _ : / -`（值会传递到 Windows 上的 shell）。

## 循环

每个任务运行这五个步骤。步骤 1、4 和 5 需要判断；2 和 3 是机械的。

### 1. 编写简报

Cline 只能看到你发送的文本。它无法读取你的对话：简报必须独立存在，包含目标、当前状态、要更改的内容、要保留的内容、项目的**真实**门禁以及报告合同。将每个简报限制为一个任务。将其写入文件并通过作为代理的 `--brief` 传递。参见 [references/writing-the-brief.md](references/writing-the-brief.md)。

### 2. 派遣

使用捆绑的代理。它运行 `cline --json -v`，在固定的位置指令后面将简报流式传输到 stdin，捕获 JSON 事件流，并写入 `result.json`。

```bash
node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --cd /path/to/repo
# 选择模型 / 提供者：        添加 --model <id>  --provider <name>
# 只读规划传递：            添加 --plan   （强制 --auto-approve false）
# 拒绝需要批准的工具：      添加 --auto-approve false
# 硬时间限制（看门狗）：      添加 --timeout 2h   （30m 默认适合简报运行；大多数实现简报应为 1-2h）
# 查看所有选项：            node .../relay.mjs --help
```

子进程的 cwd 锚定了工作空间。代理默认在系统临时目录下写入工件，并且永远不会提交。参见 [references/dispatch-and-poll.md](references/dispatch-and-poll.md)。

### 3. 等待完成

代理会阻塞，直到 Cline 完成。使用协调者的后台命令功能运行它，或在 shell 中将其后台运行并轮询 `result.json`。运行前使用错误退出 2 并不写入结果；缺少 `cline` 退出 127 并写入 `status: "cline_unavailable"`。

完成意味着进程已退出并且 `result.json` 存在——信任进程状态和工作树，而不是进度显示。Cline 的最后一条消息是 `result.json` 的 `finalMessage` 字段。

### 4. 审查——不要相信自我报告

- 亲自重新运行项目的门禁。
- 与简报进行 diff，从 `touchedFiles` 开始阅读。
- 如果安装了，运行相关的守卫技能。

参见 [references/review-and-land.md](references/review-and-land.md)。

### 5. 部署

如果工作良好，就提交它。代理永远不会提交——diff 和 `result.json` 是记录；首先运行 `git status` 和 `git diff` 以确认确切更改了什么。如果团队有 PR 流程，提交并推送一个分支；让人工审查发生。如果 diff 不正确或不完整，重新派遣一个修正的简报并在新的运行中审查。

## 自主性和权限

代理明确传递 Cline 的 `--auto-approve`，在操作模式下默认为 `true`。Cline 规划模式可以请求切换到操作模式，因此 `--plan` 强制 `--auto-approve false`；代理拒绝 `--plan --auto-approve true`。这对是只读门禁。Cline 还通过 `--data-dir` / `CLINE_SANDBOX` 暴露沙盒，但代理不配置或覆盖它。对于任何有风险的内容，先进行规划，然后在单独的操作模式派遣前审查计划。格式错误或恶意的简报在操作模式下仍然危险，因为命令以当前用户身份运行。

## 授权模型

委托是人类选择进入的。一旦简报，cline 就作为一个你批准使用的工具工作。边界是：**不要接受自我报告的结论**；在磁盘上验证一切。对于任何涉及凭证、生产数据或不可逆操作的内容，先停止并询问人类，而不是将其编码在简报中。

## 参考资料

- [references/writing-the-brief.md](references/writing-the-brief.md) - 结构、范围、门禁、简报交付。
- [references/dispatch-and-poll.md](references/dispatch-and-poll.md) - 标志、工件、`result.json` 和失败恢复。
- [references/review-and-land.md](references/review-and-land.md) - 在运行结束时完成 diff 前要验证什么。
- [references/multi-task-queues.md](references/multi-task-queues.md) - 顺序队列、约束传递、进度跟踪和最终一致性传递。
