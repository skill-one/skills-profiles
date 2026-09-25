您可以使用 Codex TUI 来验证更改。

重要提示：

*   交互式启动。
*   启动进程时始终设置 RUST_LOG="trace"。
*   通过传递 `-c log_dir=<some_temp_dir>` 参数将日志写入特定目录，以帮助调试。
*   当以编程方式发送测试消息时，先发送文本，然后在单独的写入操作中发送 Enter（不要一次性发送文本 + Enter）。
*   使用 `just codex` 目标来运行 - `just codex -c ...`
