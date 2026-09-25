# agent-device

对于常规的应用驱动任务，请立即开始。不要先用 `--help`、`--version`、`devices`、`appstate`、`snapshot` 或 `screenshot` 进行探测：

```bash
agent-device open <app> --foreground
```

这会启动会话并返回初始的交互式快照，其中包含 `@refs`。

循环：使用 `press|click|fill|longpress <目标> ... --settle`、`scroll <方向> --settle` 或 `back --settle` 进行操作；然后从打印的差异中继续，验证命名预期（`wait text "..."`、`is`、`get` 或 `find`），最后运行 `agent-device close`。

触达屏幕外的目标是一个命令，而不是滚动检查循环：`scroll down --until <选择器>` 会滚动直到该元素出现在屏幕上，而 `scroll bottom` 会滚动到内容末尾。重复使用 `scroll down` 命令是查找内容的慢方法。

按字节复制引用：`@e12`、`@e12~s4` — 保留 `@` 和任何 `~sN`。优先使用当前引用，其次是 `id`/`label`/`role` 选择器；坐标是最后的选择。如果快照报告稀疏/AX不可用，其引用和选择器无效：运行 `agent-device screenshot`，检查图像，使用坐标，然后在导航后重试 `snapshot -i`。否则，仅在差异缺少下一个目标时才运行 `snapshot -i`。

错误输出包含纠正提示；请遵循这些提示而不是重新规划。只有当任务是专门的（例如手势、脚本、TV、macOS、远程或调试）或命令形式不明确时，才运行 `agent-device help <主题>`。`agent-device --help` 列出主题，但不是启动步骤。
