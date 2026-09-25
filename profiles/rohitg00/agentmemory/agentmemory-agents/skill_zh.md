`agentmemory connect <agent>` 将内存服务器合并到主机代理的配置中，并保留任何现有的服务器。REST 是底层协议；对于仅使用 MCP 的主机，适配器将 stdio MCP 桥接器连接起来。

## 快速入门

```bash
agentmemory connect claude-code   # 或 cursor, codex, gemini-cli, ...
```

连接后，重启主机或运行其 MCP 重载（例如在 Claude Code 中的 `/mcp`），以便它能够获取服务器。然后确认代理列出了 agentmemory 的工具。

## 工作流程

1. 侦测调用代理。如果未知，则默认为 `claude-code`。
2. 使用 REFERENCE.md 表格中的名称运行 `agentmemory connect <name>`。
3. 验证：主机应显示完整的工具集并运行服务器。如果只有 7 个工具，则表示 MCP 衬垫无法连接到服务器（参见 ../_shared/TROUBLESHOOTING.md）。

## 注意事项

- 动作技能（记住、回忆和其他）使用 `npx skills add rohitg00/agentmemory` 单独安装。`connect` 使工具可用；技能教导代理何时使用它们。
- Windows：使用 WSL2。原生 Windows 运行服务器，但那里不支持 `connect`。

## 参见

- agentmemory-mcp-tools, agentmemory-rest-api, agentmemory-hooks。

## 参考

完整的适配器列表及其显示名称和协议说明位于 REFERENCE.md 中，该文件由 `src/cli/connect/` 生成。
