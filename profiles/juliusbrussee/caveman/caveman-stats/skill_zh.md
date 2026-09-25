在 Claude Code 中，`src/hooks/caveman-mode-tracker.js` 会解析它旁边的 `src/hooks/caveman-stats.js` 并在 `/caveman-stats` 上运行它。这个钩子不会阻塞提示：它会通过 `hookSpecificOutput.additionalContext` 提供报告，并指示在代码块中逐字打印。请照做，不要自己计算、重新计算或重新四舍五入数字。

在 Gemini CLI 中，请将用户引导至 `/stats model` 查看当前会话令牌使用情况，或使用 `/stats session` 查看会话统计信息。Gemini 自定义命令是提示；它们不能调用内置命令或读取其实时会话指标。切勿将 Claude Code 的文本记录视为 Gemini 使用情况。在其他主机上，如果可用，请使用本地使用报告；否则说明当前会话使用情况不可用。Claude 阅读器及其生命周期历史仅适用于 Claude Code。在没有进行测量比较的主机上，节省情况仍然未知。

报告显示记录的输出和缓存读取的令牌数、响应次数，以及可用的模式归属信息。节省情况未知：在没有 Caveman 的情况下，文本记录没有测量比较。不要从输出计数或当前模式中推断节省的令牌数、百分比、美元、规则开销或净结果。

`--all` 和 `--since 7d` 会按会话聚合最新的记录输出计数。`--share` 会报告观察到的使用情况，但节省情况未知。历史 `est_saved_*` 字段会被忽略；它们原始的历史记录行仍然保存在磁盘上。状态行显示当前活动模式，但不显示已停用的节省徽章。

原始/当前内存文件对会按其测量的字节数报告。这些文件大小差异不能证明提供者的令牌或计费节省。请参阅 `docs/HONEST-NUMBERS.md`。
