# 反重力代理人

你是**协调者**。这项技能让你将一个有边界的编码任务交给一个独立的**执行者**——Google 反重力 CLI (`agy`)——然后审查它生成的内容并亲自将其部署。你编写简报并拥有最终判断权；反重力在自己的对话中完成打字；你负责验证和提交。

这里没有什么是特定于某个协调代理人的。这个循环只需要能够运行 shell 命令和读取文件的能力，因此任何可比较的代理都可以驱动它。它是为 Claude Code 设计和运行的；将其他协调代理视为设计目标，但尚未得到验证。

## 不应使用此功能的情况

- 任务足够小，可以直接在行内完成——委托的开销不值得。
- `agy` CLI 未安装或未进行身份验证。从反重力的 CLI 文档中安装它并运行首次启动设置。
- 你想亲自编写代码，或者你只需要反重力对你编写的代码的意见（一个 `--read-only` 分发可以无修改地进行审查，但普通的审查可能根本不需要委托）。

## 前置条件（一次性检查）

1. `agy help` 成功。如果失败，请安装反重力 CLI 并完成首次启动设置。
2. `agy models` 成功。这证明了 CLI 可以进行身份验证并列出可用的模型标签。
3. 你位于（或将要指向 `--cd` 的）目标 git 仓库。

这些检查并不能证明无头写入会被批准。在 `--print` 模式下，反重力无法提示写入权限，并且可能会自动拒绝。中继代理检测到拒绝，而不是报告完成。

## 选择执行者模型

`agy` 有一个配置的默认模型，因此 `--model` 是可选的。当人类对任务有首选的反重力模型标签时使用它。否则让反重力使用它自己的当前默认值，而不是猜测。

## 循环

每个任务运行以下五个步骤。步骤 1、4 和 5 是你的判断；2 和 3 是机械的。

### 1. 编写简报

反重力只能看到你发送的文本以及它可以在工作区中检查的内容——没有聊天历史记录，没有共享上下文。任务所需的所有内容都放在简报中：目标、当前状态、要更改的内容、要保留的内容、项目的**实际**门禁命令以及报告合同。告诉反重力它将**不会**提交（你将提交）。保持每个简报一个任务。完整指南和模板：[参考资料/编写简报.md](references/writing-the-brief.md)。

### 2. 分发

使用捆绑的辅助工具将简报发送给反重力。它包装了 `agy --print`，捕获运行情况，并写入结构化的 `result.json`——因此你唯一的工作就是“运行一个命令，读取一个文件。”（下面的 `<skill-dir>` 是此技能的安装目录——包含此 `SKILL.md` 的文件夹。）

```bash
node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --cd /path/to/repo
# 选择模型标签：                 添加 --model "<agy models 中的标签>"
# 推理工作量（低、中、高）：       添加 --effort high
# 只读（沙盒——无修改）：         添加 --read-only
# 启用反重力终端沙盒：          添加 --sandbox
# 恢复最新的对话：              添加 --resume-last  （仅限 delta 简报）
# 查看所有选项：                  node .../relay.mjs --help
```

辅助工具默认会启动一个新的反重力项目，并将 `--add-dir <repo>`（`--cd` 路径，绝对路径）传递给 `agy`，以便 `agy` 有一个明确的工作区。它默认**不会**传递 `--dangerously-skip-permissions`。机制、标志和 `result.json` 的形状：[参考资料/分发和轮询.md](references/dispatch-and-poll.md)。

### 3. 等待完成

辅助工具会阻塞，直到反重力完成，因此用你的协调者提供的内容支持它，并在返回时恢复：

- **Claude Code：** 使用 `run_in_background: true` 运行 Bash 调用；你将在完成时收到通知。
- **普通 shell / 其他代理：** 对于短任务，在前景中运行它，或者将其置于后台并轮询结果文件。

不要相信进度跟踪器超过现实：运行完成当 `result.json` 被写入并且进程已经退出时。读取工作区，而不是状态行。执行者的完整报告是 `result.json` 中的 `finalMessage` 字段（在报告标记之间完整打印在 stdout 上）。

### 4. 审查——不要相信自我报告

反重力的 `result.json` 包括它自己的最终消息和任何门禁声明。**重新验证，不要接受：**

- **自己重新运行项目的门禁**（步骤 1 中的测试/检查/构建命令）。
- **与简报对比差异**：反重力是否做了所要求的事情，不多也不少？`result` 中的 `touchedFiles` 是你的起点。
- **如果你安装了相关门禁技能，在差异上运行它们**。
- 对于模式/迁移更改，进行往返测试；对于删除操作，使用 grep 搜索悬空引用。

完整清单：[参考资料/审查和部署.md](references/review-and-land.md)。

### 5. 部署它

执行者编辑工作区；**协调者提交**。只有当门禁通过并且差异有效时：

- 自己提交经过验证的工作，并附带清晰的说明。
- 如果需要更改，使用 `--resume-last` 发送 delta 简报并重新审查。

## 权限模型

反重力拥有它自己的权限策略。中继代理默认不会绕过它。只有在人类明确接受反重力可能会自动批准工具权限请求时，才使用 `--dangerously-skip-permissions`。`--read-only` 组合 `--sandbox` 与 `--dangerously-skip-permissions`：沙盒是执行——工作区内的写入被覆盖并丢弃，而路径外的路径会以 EPERM 失败——而自动批准仅允许在沙盒内运行工具。作为面向用户的标志，它与 `--dangerously-skip-permissions` 互斥，单独使用（没有沙盒）是完全访问权限。当你想要为写入运行启用终端沙盒时，单独使用 `--sandbox`。
如果无头的 `--print` 自动拒绝写入，中继代理会报告 `status: "failed"` 并以非零状态退出。中继代理在 `--read-only` 运行前后对工作区进行指纹识别，以在 `result.json` 中报告 `readOnlyViolation`。设置允许规则适用于无头的 `--print` 运行，但它们的匹配规则和配置位置因 `agy` 版本和平台而异，因此将拒绝视为需要在你自己的安装上测量的事情，而不是假设。已经测量了两个陷阱。首先，精确匹配行为：在 Windows 上使用 agy 1.2.5 时，`command(<name>)` 只匹配不带参数的纯命令——`command(git)` 从未允许真实的 `git status`，而 `command(regex:git .+)` 是必需的（[问题 #614 评论](https://github.com/google-antigravity/antigravity-cli/issues/614#issuecomment-5466617752)）。在 macOS 上使用 agy 1.2.0 时，相同的纯 `command(git)` 规则*确实*允许 `git status`，因此精确匹配陷阱不是跨版本的常数。其次，在 Windows 上，反重力权限引擎的一个开放上游缺陷（[问题 #614](https://github.com/google-antigravity/antigravity-cli/issues/614)）将解析路径按空白字符分割，因此位于 `C:\Program Files\...` 下（这是 `git` 本身通常所在的路径，使其成为委托编码任务中最常见的触发器，而不仅仅是 node/npm）的二进制文件被匹配为其第一个片段，并且没有任何 `command(<name>)` 规则可以匹配它。关于 agy 读取哪个文件：在 Windows 上使用 agy 1.2.5 时已验证，有效规则是 `userSettings.globalPermissionGrants.allow` 在 `~/.gemini/config/config.json` 中，而不是 agy 自己的拒绝消息指向的 `~/.gemini/antigravity-cli/settings.json` 中的 `permissions.allow`；在 macOS 上使用 agy 1.2.0 时已验证，规则在 `antigravity-cli/settings.json` 中生效。在你自己的版本上重新检查这两个文件之前，不要依赖任何文件。参见
[参考资料/分发和轮询.md](references/dispatch-and-poll.md) 以获取完整说明。在没有明确人类批准的情况下，不要添加绕过标志。

## 授权模型

委托是人类选择进入的事情。一旦他们有了（“运行这个队列”，“继续”），提交经过验证、门禁通过的工作就是约定的合同。对此有两个限制：**表面，不要吸收**（报告反重力的设计决策、可辩护但未询问的转弯和非阻塞的吹毛求疵，而不是默默地保留它们）和**因范围变化而停止**（如果正确完成需要超出简报，请询问——不要自己扩展委托）。完整说明在
[参考资料/审查和部署.md](references/review-and-land.md)。

## 参考资料

- [参考资料/编写简报.md](references/writing-the-brief.md) - 如何编写反重力可以盲目执行的简报：结构、XML 块、报告合同和实际门禁命令。
- [参考资料/分发和轮询.md](references/dispatch-and-poll.md) - `relay.mjs` 标志、`result.json` 合同、按协调者背景运行和运行行为异常时的恢复。
- [参考资料/审查和部署.md](references/review-and-land.md) - 审查清单、提交边界和通过 `--resume-last` 进行重做循环。
- [参考资料/多任务队列.md](references/multi-task-queues.md) - 运行顺序队列：将约束向前传递、进度跟踪和运行结束时的连贯性检查。
