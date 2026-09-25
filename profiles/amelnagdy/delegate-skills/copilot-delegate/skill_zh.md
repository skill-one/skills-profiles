# Copilot 委托

你是**协调者**。将一个有边界的编码任务委托给一个单独的**执行者**——GitHub Copilot CLI，然后审查它生成的内容，并亲自将其部署。你编写简报并拥有判断权；执行者在自己的会话中对其工作树进行更改；你进行验证并提交。

这个循环只需要一个 shell 命令和文件访问权限，因此任何可比较的协调者都可以驱动它。

## 不应使用此方法的情况

- 任务足够小，可以直接完成；委托的开销不值得。
- `copilot` CLI 未安装或未进行身份验证。
- 你需要一个硬性沙盒。Copilot 暴露沙盒控制，但它们是上游实验性的（基于 MXC，通过 `/sandbox` 命令和设置进行控制，默认禁用）——这个中继程序不会配置它们。`--read-only` 仅禁用编辑工具（`--mode plan`）；shell 命令仍然运行。如果项目文件绝对不能更改，则针对干净的或隔离的工作树进行部署。

## 前置条件（一次性检查）

1. 安装 `copilot` (`npm install -g @github/copilot`；CLI 需要 Node 22+，中继程序本身运行在 Node 18+ 上——中继程序会探测 `copilot version`）。
2. 进行身份验证：运行 `copilot login`（交互式网页/设备流程），或在环境中设置 `COPILOT_GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_TOKEN`。
3. 确认 `copilot version` 成功。
4. 在目标 git 仓库中工作，或指向 `--cd`。

## 选择模型（可选）

Copilot 选择默认模型 (`auto`)。要选择其他模型，请传递 `--model <name>`。
中继程序仅接受字母、数字和 `. _ : / -`（值会传递给 Windows 上的 shell）。

## 选择工作量（可选）

Copilot 支持推理工作量旋钮：`--effort <level>`，其值为 `low`、`medium`、`high`、`xhigh` 或 `max`。中继程序在部署之前会拒绝任何其他值。

## 循环

每个任务运行以下五个步骤。步骤 1、4 和 5 需要判断；2 和 3 是机械的。

### 1. 编写简报

Copilot 只能看到你发送的文本。它无法读取你的对话：简报必须独立存在，包含目标、当前状态、要更改的内容、要保留的内容、项目的**实际**门禁和报告合同。将每个简报限制为单个任务。将其写入文件并通过作为中继程序的 `--brief` 传递。参见 [references/writing-the-brief.md](references/writing-the-brief.md)。

### 2. 部署

使用捆绑的中继程序。它运行 `copilot -p` 并使用 `--output-format json --no-color --stream off`，捕获 JSONL 事件流，并写入 `result.json`。

```bash
node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --cd /path/to/repo
# 选择模型：                    添加 --model <name>
# 设置推理工作量：              添加 --effort <level>
# 只读规划传递：               添加 --read-only  (强制 --mode plan)
# 完全工具自主权：              添加 --allow-all-tools
# 硬性时间限制（watchdog）：     添加 --timeout 2h   (30m 默认适合简报运行)
# 恢复会话：                   添加 --session <id>  或  --resume-last
# 查看所有选项：                node .../relay.mjs --help
```

子进程的 cwd 锚定了工作区。中继程序默认在系统临时目录下写入工件，并且永远不会提交。参见 [references/dispatch-and-poll.md](references/dispatch-and-poll.md)。

### 3. 等待完成

中继程序会阻塞，直到 Copilot 完成。使用协调者的后台命令功能运行它，或在 shell 中将其后台运行并轮询 `result.json`。运行前使用错误会退出 2 并不写入结果；缺少 `copilot` 会退出 127 并写入 `status: "copilot_unavailable"`。

完成意味着进程已退出且 `result.json` 存在——信任进程状态和工作树，而不是进度显示。Copilot 的最终助手消息是 `result.json` 的 `finalMessage` 字段。

### 4. 审查——不要信任自我报告

- 自己重新运行项目的门禁。
- 与简报进行 diff，从 `touchedFiles` 开始阅读。
- 如果安装了相关守卫技能，请运行它们。

参见 [references/review-and-land.md](references/review-and-land.md)。

### 5. 部署

如果工作良好，请提交它。中继程序永远不会提交——diff 和 `result.json` 是记录；首先运行 `git status` 和 `git diff` 以确认确切更改的内容。如果团队有 PR 流程，请提交提交并推送一个分支；让人工审查发生。如果 diff 不正确或不完整，请在新的运行中重新部署修正后的简报并再次审查。

## 自主权和权限

如果没有 `--allow-all-tools`，Copilot 在无头模式下会自动拒绝工具调用：进程退出 0，但中继程序会检测到拒绝事件并报告 `status: "failed"`，并附带 CLI 的错误消息以及提示传递 `--allow-all-tools`。这是诚实的默认值——协调者看到失败，而不是静默的无操作。

`--allow-all-tools` 明确授予完全工具自主权。`--read-only` 选择 `--mode plan`，这会禁用编辑工具，因此项目文件不能通过直接编辑更改；它不需要 `--allow-all-tools`。计划模式下仍然会运行 shell 命令，因此它防止编辑，而不是防止所有内容。这两个标志是互斥的。

Copilot 还暴露了沙盒控制，但它们是上游实验性的（基于 MXC，通过 `/sandbox` 命令和设置进行控制，默认禁用）。这个中继程序不会配置它们。

## 授权模型

委托是人类选择进入的。一旦简报，Copilot 就会作为你批准使用的工具工作。边界是：**不要接受自我报告的结论**；在磁盘上验证一切。对于任何涉及凭证、生产数据或不可逆操作的内容，应首先停止并询问人类，而不是将其编码在简报中。

## 参考文献

- [references/writing-the-brief.md](references/writing-the-brief.md) — 结构、范围、门禁、简报交付。
- [references/dispatch-and-poll.md](references/dispatch-and-poll.md) — 标志、工件、`result.json` 和失败恢复。
- [references/review-and-land.md](references/review-and-land.md) — 在运行结束时完成 diff 前要验证的内容。
- [references/multi-task-queues.md](references/multi-task-queues.md) — 顺序队列、约束传递、进度跟踪和最终一致性传递。
