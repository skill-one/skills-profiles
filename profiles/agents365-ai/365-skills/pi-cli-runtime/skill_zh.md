# Pi 运行时

仅可在 `pi:pi-companion-forwarder` 子代理内部使用此技能。

主要辅助工具：

- `node "${CLAUDE_PLUGIN_ROOT}/scripts/pi-companion.mjs" task "<原始参数>"`

执行规则：

- 救援子代理是一个转发器，而非协调器。它的唯一工作就是调用一次 `task` 并将 stdout 原样返回。
- 优先使用辅助工具，而不是手写的 `git`、直接的 Pi CLI 字符串或任何其他 Bash 活动。
- 不要从 `pi:pi-companion-forwarder` 调用 `setup`、`review`、`adversarial-review`、`status`、`result` 或 `cancel`。
- 对所有救援请求使用 `task`，包括诊断、规划、研究以及显式的修复请求。
- 你可以使用 `pi-prompting` 技能将用户的请求重写为更紧凑的 Pi 提示，然后再进行单次 `task` 调用。
- 该提示草拟是唯一允许的 Claude 端工作。不要检查仓库、自行解决任务或转发提示文本之外的独立分析。
- 除非用户明确要求特定努力，否则不要设置 `--effort`。
- 默认情况下不设置模型。仅在用户明确要求时添加 `--model`（例如 `deepseek-v4-pro`、`deepseek-v4-flash`）。
- 默认为可写入的 Pi 运行，通过添加 `--write`，除非用户明确要求只读行为或只想进行审查、诊断或研究而不进行编辑。

命令选择：

- 每次救援转交使用且仅使用一次 `task` 调用。
- 如果转发请求包含 `--background` 或 `--wait`，将其视为 Claude 端的执行控制。在调用 `task` 前移除它，并且不要将其视为自然语言任务文本的一部分。
- 如果转发请求包含 `--model`，将模型 ID 原样传递给 `task`。
- 如果转发请求包含 `--effort`，将其传递给 `task`。
- 如果转发请求包含 `--resume`，从任务文本中移除该标记并添加 `--resume-last`。
- 如果转发请求包含 `--fresh`，从任务文本中移除该标记，不要添加 `--resume-last`。
- `--resume`：始终使用 `task --resume-last`，即使请求文本不明确。
- `--fresh`：始终使用新的 `task` 运行，即使请求听起来像后续操作。
- `--effort`：接受的值是 `off`、`minimal`、`low`、`medium`、`high`、`xhigh`、`max`。别名 `none` 映射到 `off`。
- `task --resume-last`：内部辅助工具，用于“继续进行”、“恢复”、“应用最高修复”或“深入挖掘”之前的救援运行。

安全规则：

- 在 `pi:pi-companion-forwarder` 中默认为可写入的 Pi 工作，除非用户明确要求只读行为。
- 保留用户的任务文本原样，除了移除路由标记。
- 不要检查仓库、读取文件、grep、监控进度、轮询状态、获取结果、取消任务、总结输出或进行任何自己的后续工作。
- 恰如原样返回 `task` 命令的 stdout。
- 如果 Bash 调用失败或无法调用 Pi，则返回空。
