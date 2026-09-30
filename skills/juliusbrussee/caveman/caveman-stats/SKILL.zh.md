---
name: caveman-stats
description: 显示当前Claude Code会话的录制输出和缓存读取令牌使用情况及模式归属，或定位主机本地使用报告。触发：/caveman-stats。
---

在 Claude Code 中，`src/hooks/caveman-mode-tracker.js` 在 `/caveman-stats` 上运行 `src/hooks/caveman-stats.js`，并通过 `hookSpecificOutput.additionalContext` 提供其报告。按照钩子的指示，将此报告原样打印在代码块内。不要自行计算或添加数字。

在 Gemini CLI 中，请用户使用 `/stats model` 查看当前会话令牌使用情况，或使用 `/stats session` 查看会话统计信息。Gemini 自定义命令是提示；它们无法调用内置命令或读取其实时会话指标。切勿将 Claude Code 的文本记录视为 Gemini 使用情况。在其他主机上，如果可用，请使用本地使用报告；否则，说明当前会话使用情况不可用。Claude 阅读器及其生命周期历史仅适用于 Claude Code。在没有进行测量比较的主机上，节省情况仍然未知。

报告显示记录的输出和缓存读取的令牌、响应计数以及可用的模式归属。节省情况未知：在没有 Caveman 的情况下，文本记录没有测量比较。不要从输出计数或当前模式中推断节省的令牌、百分比、美元、规则开销或净结果。

`--all` 和 `--since 7d` 按会话聚合最新记录的输出计数。`--share` 报告观察到的使用情况，但节省情况未知。历史 `est_saved_*` 字段被忽略；它们原始的历史记录行仍然保存在磁盘上。状态行显示活动模式，但不显示已停用的节省徽章。

原始/当前内存文件对按其测量的字节数报告。这些文件大小差异不能确定提供者的令牌或计费节省。请参阅 `docs/HONEST-NUMBERS.md`。
