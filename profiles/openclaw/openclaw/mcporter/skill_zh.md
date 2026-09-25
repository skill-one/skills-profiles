# mcporter

使用 `mcporter` 直接与 MCP 服务器进行交互。

快速入门

- `mcporter list`
- `mcporter list <服务器> --schema`
- `mcporter call <服务器.tool> key=value`

调用工具

- 选择器：`mcporter call linear.list_issues team=ENG limit:5`
- 函数语法：`mcporter call "linear.create_issue(title: \"Bug\")"`
- 完整 URL：`mcporter call https://api.example.com/mcp.fetch url:https://example.com`
- 标准输入输出：`mcporter call --stdio "bun run ./server.ts" scrape url=https://example.com`
- JSON 负载：`mcporter call <服务器.tool> --args '{"limit":5}'`

认证 + 配置

- OAuth：`mcporter auth <服务器 | url> [--reset]`
- 配置：`mcporter config list|get|add|remove|import|login|logout`

守护进程

- `mcporter daemon start|status|stop|restart`

代码生成

- CLI：`mcporter generate-cli --server <名称>` 或 `--command <url>`
- 检查：`mcporter inspect-cli <路径> [--json]`
- TS：`mcporter emit-ts <服务器> --mode client|types`

备注

- 配置默认：`./config/mcporter.json`（使用 `--config` 覆盖）。
- 优先使用 `--output json` 获取机器可读结果。
