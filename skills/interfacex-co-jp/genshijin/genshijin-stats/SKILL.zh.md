---
name: genshijin-stats
description: 显示当前会话的实时令牌使用量和预估减少量。直接从Claude Code会话日志中读取——无AI预估。使用`/genshijin-stats`启动。输出由mode-tracker钩子注入，模型本身不进行数值计算。
---

这个技能由 `hooks/genshijin-stats.js` 提供（在 `/genshijin-stats` 检测时由 `hooks/genshijin-mode-tracker.js` 调用）。当钩子以 `decision: "block"` 格式化 stats 并将其作为 reason 返回时 → 用户可以立即查看数值。模型端无需执行任何操作。

## 参数

- (无) — 显示当前会话 stats
- `--share` — 生成可推文的单行摘要
- `--all` — 终身统计
- `--since 7d` / `--since 24h` — 指定期限的终身统计
