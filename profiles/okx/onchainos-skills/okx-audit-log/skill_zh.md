# Onchain OS 审计日志

为开发者提供审计日志文件路径，以便离线排查问题。

## 响应

告知用户：

1. **日志文件路径**：`~/.onchainos/audit.jsonl`（如果设置了环境变量，则为`$ONCHAINOS_HOME/audit.jsonl`）
2. **格式**：JSON Lines，每行一个 JSON 对象
3. **第一行（设备头部）**：`{"type":"device","os":"<os>","arch":"<arch>","version":"<cli_version>"}` — 在日志文件创建时写入一次，并在轮换时保留
4. **条目字段**：`ts`（本地时间带时区，例如`2026-03-18 +8.0 18:00:00.123`），`source`（cli/mcp），`command`，`ok`，`duration_ms`，`args`（已脱敏），`error`
5. **轮换**：最多 10,000 行，自动保留设备头部 + 最新的 5,000 条记录

**请勿在对话中读取或显示文件内容**。
