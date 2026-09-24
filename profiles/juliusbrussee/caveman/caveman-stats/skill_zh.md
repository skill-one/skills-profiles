在 Claude Code 中，`src/hooks/caveman-mode-tracker.js` 会解析其同目录下的 `src/hooks/caveman-stats.js` 并在 `/caveman-stats` 触发执行。该钩子不会拦截提示词：它会通过 `hookSpecificOutput.additionalContext` 提供报告，并指示在围栏代码块内原样打印该报告。请严格按此执行，切勿自行计算、重新计算或重新进行四舍五入。

在 Gemini CLI 中，引导用户通过 `/stats model` 查看当前会话的 token 使用情况，或通过 `/stats session` 查看会话统计信息。Gemini 自定义命令属于提示词，无法调用内置命令或读取其实时会话指标。切勿将 Claude Code 的转录记录作为 Gemini 的使用数据。在其他主机中，若有可用的原生使用报告，请使用；否则，请说明当前会话使用数据不可用。Claude 阅读器及其生命周期历史仅适用于 Claude Code。在没有任何实测对比的情况下，所有主机的节省数据均无法得知。

该报告展示了已记录的输出与缓存读取 token、响应数量，以及在可用情况下的模式归属。节省数据无法得知：在缺乏 Caveman 的情况下，转录记录中不存在实测对比数据。请勿根据输出计数或当前模式推断已节省的 token、百分比、美元金额、规则开销或净结果。

`--all` 和 `--since 7d` 会汇总每个会话最近记录的输出计数。`--share` 会报告观察到的使用数据，但节省情况未知。历史 `est_saved_*` 字段将被忽略；其原始历史记录仍保留在磁盘上。状态栏会显示当前激活的模式，但不会显示已弃用的节省徽章。

原始/当前的内存文件对会按其实测字节大小进行报告。这些文件大小差异并不能确立提供方的 token 或计费节省。详见 `docs/HONEST-NUMBERS.md`。
