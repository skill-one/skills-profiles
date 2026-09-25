# Qoder 委托人

你是**协调者**。将一个有边界的编码任务委托给一个单独的**执行者**——Qoder CLI——然后审查它生成的内容，并亲自将其合并。你编写简报并拥有判断权；Qoder 在其会话中编辑工作区；你进行验证并提交。

这个循环只需要 shell 和文件访问权限，因此任何可比较的协调者都可以驱动它。

## 不应使用此方法的情况

- 任务足够小，可以直接完成；委托的额外开销不值得。
- `qodercli` 未安装或未进行身份验证。
- 你想亲自编写代码，或者只需要一个交互式 Qoder 会话。

## 前置条件（检查一次）

```bash
command -v qodercli
qodercli --version
qodercli --list-models
```

如果二进制文件缺失，请从 Qoder 的
[官方快速入门](https://docs.qoder.com/en/cli/quick-start) 中安装它。使用 `qodercli login` 进行身份验证，或者设置 `QODER_PERSONAL_ACCESS_TOKEN` 以实现自动化。一个成功的 `--list-models` 确认当前账户可以返回其实时模型目录。

## 选择模型和上下文窗口

Qoder 的可用模型可能会发生变化。如果人类请求一个模型，请使用 `qodercli --list-models` 中其当前的准确值；切勿编造或固定目录条目。否则省略 `--model` 并让 Qoder 使用其当前默认值。

`--context-window <n>` 是可选的。仅在人类请求大小或任务需要明确预算时传递一个正整数。Qoder 仅将其应用于支持的模型；如果遇到不支持的模型/大小错误，请选择其他值而不是静默选择。

## 循环

每个任务运行这五个步骤。步骤 1、4 和 5 需要判断；2 和 3 是机械的。

### 1. 编写简报

Qoder 看到的简报加上它可以在工作区中检查的内容，而不是这个聊天。包括目标、当前状态、要更改的内容、要保留的内容、项目的**实际**门禁，以及一个关闭报告合同。告诉 Qoder 不要提交。每个简报保持一个任务。参见
[references/writing-the-brief.md](references/writing-the-brief.md)。

### 2. 派遣

使用捆绑的转发器。它封装了 Qoder 的非交互式 `stream-json` 模式，并写入 `result.json`。
`<skill-dir>` 是包含此 `SKILL.md` 的安装文件夹。

```bash
node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --cd /path/to/repo
# 选择一个实时模型：                 添加 --model "<从 qodercli --list-models 获取的值>"
# 请求一个支持的上下文窗口：添加 --context-window 32768
# 恢复最新会话：          添加 --resume-last  # 仅限 delta 简报
# 恢复特定会话：          添加 --resume <id>  # 仅限 delta 简报
# 查看所有选项：                   node .../relay.mjs --help
```

实现默认为 Qoder 的 `auto` 权限模式。转发器不会绕过权限，除非调用者明确请求，并且它永远不会提交。参见
[references/dispatch-and-poll.md](references/dispatch-and-poll.md)。

### 3. 等待完成

转发器会阻塞，直到 Qoder 退出。使用协调者的后台命令功能运行它，或者在 shell 中将其置于后台并等待 `result.json`。完成意味着进程已退出并且文件包含一个 `status`；不要相信进度显示。

运行前使用错误会退出 2 并不写入结果。缺少 `qodercli` 会退出 127 并写入 `status: "qoder_unavailable"` 以及安装指南。

原生 Windows 转发器启动尚未验证；在原生 Windows 烟雾测试通过之前，不要声称它。

### 4. 审查——不要相信自我报告

将 Qoder 的最终消息和门禁结果视为声明：

- 自己重新运行项目的门禁。
- 与简报进行比较，从 `touchedFiles` 开始阅读差异。
- 分别检查任何 `--add-dir` 工作区；它们的更改不在主要树报告中。
- 如果安装了相关守卫技能，请运行它们。
- 在删除或重命名后进行往返迁移，并在删除或重命名后查找悬空引用。

参见 [references/review-and-land.md](references/review-and-land.md)。

### 5. 合并

执行者编辑；**协调者提交**。只有在门禁通过并且差异有效时才提交。如果需要返工，请使用 `--resume-last` 或 `--resume <id>` 发送 delta 简报，然后再次审查。

## 权限模型

Qoder 打印模式无法显示批准提示。转发器默认为 `auto`，它会做出非交互式的允许/拒绝决策。`default` 可以拒绝需要提示的操作；`accept_edits` 允许工作区编辑但可能拒绝 shell 操作；`dont_ask` 会失败；`plan` 映射到 `default` 加上 Qoder 的 Plan 工作状态；`bypass_permissions` 仅用于明确信任的运行。

当在不受信任的目录外请求非默认模式时，Qoder 会回退到 `default`。检查 `result.json` 中的 `actualPermissionMode`；没有请求的模式会替换差异审查。

## 授权模型

委托是人类选择进入的。一旦他们请求，验证、通过门禁的工作就是合同。仍然有两个限制：**展示，不要吸收**（报告 Qoder 的设计决策和非阻塞偏差）和**因范围变化而停止**（在超出简报之前请求）。参见
[references/review-and-land.md](references/review-and-land.md)。

## 参考

- [references/writing-the-brief.md](references/writing-the-brief.md) - 简报结构、实际门禁、报告合同、秘密和 delta 简报。
- [references/dispatch-and-poll.md](references/dispatch-and-poll.md) - 标志、模型/上下文控制、工件、结果字段、会话和故障恢复。
- [references/review-and-land.md](references/review-and-land.md) - 独立审查、提交边界和返工。
- [references/multi-task-queues.md](references/multi-task-queues.md) - 顺序队列、约束传递、进度跟踪和最终一致性。
