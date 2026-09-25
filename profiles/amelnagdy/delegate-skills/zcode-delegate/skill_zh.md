# ZCode 委托

你是**协调者**。这项技能让你可以将一个有边界的编码任务交给一个独立的**执行者**——Z.AI ZCode CLI，然后审查它生成的内容并自行完成。你编写简报并拥有最终判断权；ZCode 负责输入；你负责验证和提交。

这里没有任何内容是特定于某个协调代理的。这个循环只需要能够运行 shell 命令和读取文件的能力。（它是为 Claude Code 设计的，并在其上运行；将其他协调代理视为设计目标，但尚未得到验证。）

## 不应使用此功能的情况

- 任务足够小，可以直接在行内完成——委托的额外开销不值得。
- 未安装 ZCode，或者其 CLI 没有配置模型提供者。
- 你想自己编写代码，或者你只需要进行审查。

## 前提条件（一次性检查）

1. **ZCode 已安装。** CLI 随桌面应用程序一起提供——它不在 PATH 中，也不在 npm 上。中继程序按以下顺序解析它：`--zcode-path <文件>` 或 `ZCODE_CLI` 首先解析，然后是 PATH，然后是安装的应用程序包。在 Linux 上，应用程序是一个 AppImage，没有固定的安装路径，因此需要使用标志或环境变量——中继程序不会猜测任何内容。
2. **为 CLI 配置了模型提供者**，并且它能够实际访问密钥。登录桌面应用程序**并不足够**——见下文。
3. 你位于（或将要指向 `--cd` 的）目标 git 仓库。

中继程序将 CLI 版本以及它如何解析到 `result.json` 中记录下来，因此意外的安装情况在事后可见。

## 无头 CLI 的身份验证

**登录 ZCode 桌面应用程序并不能验证此中继程序驱动的 CLI。** CLI 在 `~/.zcode/cli/config.json` 中保留其自己的配置，与桌面应用程序分开，并且没有任何东西连接两者。`zcode login` 是预期的路径，但如果它因 `OAuth 响应不是有效的 JSON` 而失败，则入口方式是一个 Z.AI API 密钥。

需要两样东西，并且它们是分开的：

1. **提供者块** 必须存在于 `~/.zcode/cli/config.json` 中。它定义了提供者、其端点和其模型——环境无法提供这些内容：

   ```jsonc
   {
     "provider": {
       "zai": {
         "kind": "anthropic",
         "options": { "apiKeyRequired": true, "baseURL": "https://api.z.ai/api/anthropic" },
         "models": { "glm-5.1": { "name": "GLM-5.1" } }
       }
     },
     "model": { "main": "zai/glm-5.1" }
   }
   ```

2. **密钥** 可以存在于该文件中的 `provider.zai.options.apiKey` 中，或者作为 `ZAI_API_KEY`、`ZCODE_API_KEY` 或 `ANTHROPIC_API_KEY` 之一存在于环境中。优先使用环境——它将密钥从磁盘上移除。

如果运行失败并显示 `Model provider 缺少 API key: <provider>`，则提供者块已解析，但未找到密钥：设置其中一个变量并重新运行。

## 自主性——在派遣前阅读此内容

ZCode 自己的术语是**模式**。它有四个值；只有两个可用于无头模式。

| 模式 | 行为 |
| --- | --- |
| `yolo` | **写入。** ZCode 自己的 `--prompt` 默认值，以及此中继程序的写入能力默认值。 |
| `plan` | **拒绝编辑。** `--read-only` 选择的内容。 |
| `build` | **被此中继程序拒绝。** 无权限客户端不存在于无头模式中，因此工具被阻止，运行退出 0 且未执行任何操作。 |
| `edit` | 因相同原因被拒绝。 |

两个明确的限制，因为 ZCode 无法强制执行它们：

- **`plan` 模式在测试中拒绝编辑，但中继程序不将其视为保证。** 它在运行之前获取一个 Git 指纹，并在运行后报告一个三态 `readOnlyViolation`。确认 `touchedFiles` 返回为空，而不是假设没有编辑。
- **ZCode 没有 `--allowed-tools`。** 只有 `--disallowed-tools` 拒绝列表存在，并且它**确实**被强制执行。因此，在此处不可能有一个明确允许的工具界面——不要假设有一个。 |

## 循环

每个任务运行以下五个步骤。步骤 1、4 和 5 是你的判断；2 和 3 是机械的。

### 1. 编写简报

ZCode 只看到你发送的内容——没有仓库记忆，没有聊天历史。任务所需的所有内容都放在简报中：目标、当前状态、要更改的内容、要保留的内容、项目的**实际**门禁命令（从仓库的 CLAUDE.md/AGENTS.md/Makefile 中发现它们——不要假设），以及报告合同。告诉 ZCode 它将**不会**提交。每个简报一个任务。中继程序将简报作为附加文件传递，因此命令行不再限制其长度——模型的上下文窗口仍然限制。完整指南和模板：
[references/writing-the-brief.md](references/writing-the-brief.md)。

### 2. 派遣

```bash
node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --cd /path/to/repo
# 只读（审查/诊断，无编辑）：   添加 --read-only
# 继续特定会话：              添加 --session <sess_...>  （从 result.json；只发送差异简报）
# 继续最新会话用于 --cd：     添加 --resume-last
# 拒绝工具（拒绝列表）：        添加 --disallowed-tools "Write,Edit,Bash"
# 明确指向 CLI：              添加 --zcode-path /path/to/zcode.cjs
# 硬时间限制（看门狗）：       添加 --timeout 2h  （默认：关闭）
# 查看所有选项：              node .../relay.mjs --help
```

(`<skill-dir>` 是此技能的安装目录——包含此 `SKILL.md` 的文件夹。)

中继程序将其工件写入临时目录，因此正在审查的仓库保持干净。它**永远不会**提交——见步骤 5。机械操作、标志和 `result.json` 的形状：
[references/dispatch-and-poll.md](references/dispatch-and-poll.md)。

### 3. 等待完成

中继程序会阻塞直到 ZCode 完成，因此用你的协调者提供的内容支持它：

- **Claude Code：** 使用 `run_in_background: true` 运行 Bash 调用；你将在完成时收到通知。
- **普通 shell / 其他代理：** 短任务使用前台，或者将其后台运行并轮询结果文件。运行完成时，当 `result.json` 存在并具有 `status` 时。预运行使用错误会退出 2 并**不**写入结果文件，因此请检查退出代码；无法找到 CLI 会退出 127，但**会**写入具有状态 `zcode_unavailable` 的 `result.json`。

不要信任进度跟踪器超过现实：查看工作树，而不是状态行。

### 4. 审查——不要相信自我报告

- **自己重新运行项目的门禁。** 永远不要相信“门禁通过”。
- **与简报对比查看差异**：ZCode 是否做了所要求的事情，不多也不少？`touchedFiles` 是你的起点。
- **在只读运行中，检查 `readOnlyViolation` 并确认 `touchedFiles` 为空。**
- 如果你安装了相关的守卫技能，请在差异上运行它们。

完整清单：[references/review-and-land.md](references/review-and-land.md)。

### 5. 提交

**协调者提交。** 只有在门禁通过并且差异有效时：

- 自己提交经过验证的工作，并附带清晰的说明。
- 如果需要更改，使用从先前的 `result.json` 中的 `--session <sessionId>` 发送差异数据，并再次审查。

## 只读的第二意见

中继程序也可以作为一种获取对抗性第二意见且无写入风险的方式：使用 `--read-only` 派遣，并附带一个列出已达成共识的简报，然后每个有争议的点都附带两种立场，并要求 ZCode 进行辩护或让步。由于在此处 `plan` 模式的保证是度量的而不是强制的，因此验证 `touchedFiles` 返回为空，而不是假设没有编辑。

## 授权模型

委托是用户选择进入的。一旦他们进入，提交经过验证、通过门禁的工作就是约定的合同。两个限制：**表面，不要吸收**（报告 ZCode 的设计决策和可辩护但未询问的转弯，而不是默默地保留它们）和**因范围变化而停止**（如果正确完成需要超出简报，请询问）。完整说明在
[references/review-and-land.md](references/review-and-land.md) 中。

## 参考

- [references/writing-the-brief.md](references/writing-the-brief.md) — 如何编写 ZCode 可以盲目执行的简报：结构、报告合同、嵌入实际门禁命令。
- [references/dispatch-and-poll.md](references/dispatch-and-poll.md) — `relay.mjs` 标志、`result.json` 合同、如何解析 CLI、后台运行和恢复。
- [references/review-and-land.md](references/review-and-land.md) — 审查清单、提交边界和精确会话重做周期。
- [references/multi-task-queues.md](references/multi-task-queues.md) — 运行顺序队列：将约束向前传递、进度跟踪和运行结束时的连贯性检查。
