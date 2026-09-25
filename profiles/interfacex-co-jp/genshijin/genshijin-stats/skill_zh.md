这个技能由 `hooks/genshijin-stats.js` 提供（在 `/genshijin-stats` 检测时调用 `hooks/genshijin-mode-tracker.js`）。当钩子以 `"decision: "block"` 格式化 stats 并将其作为 reason 返回时 → 用户可以立即查看数值。模型端无需执行任何操作。

## 参数

- (无) — 显示当前会话 stats
- `--share` — 可用于推文的单行摘要
- `--all` — 全生命周期统计
- `--since 7d` / `--since 24h` — 指定期限的全生命周期统计
