# Grafana Cloud MCP 服务器设置

Grafana MCP 服务器将 Grafana Cloud 的功能作为 AI 代理可通过模型上下文协议调用的工具进行暴露。代理随后可以查询指标、搜索仪表板、管理警报、调查事件，并与车队管理进行交互，而无需离开编码环境。

传输方式：`stdio`（代理将服务器作为子进程启动，最简单）、或 `SSE`（服务器独立运行，代理通过 HTTP 连接——参见 [references/sse-transport.md](references/sse-transport.md)）。

## 常见工作流程

### 将 Claude Code 连接到 Grafana (stdio)

```bash
# 1. 安装服务器
go install github.com/grafana/mcp-grafana/cmd/mcp-grafana@latest

# 2. 验证二进制文件
mcp-grafana --version
# 如果 "command not found"：确保 $GOPATH/bin（或 $HOME/go/bin）在 PATH 中。
```

3. **获取服务账户令牌**：Grafana Cloud → 管理 → 服务账户 → 创建具有 `Viewer` 角色（如果需要写入，则添加 `Editor`）的账户 → 生成令牌。注意 Grafana URL（例如 `https://myorg.grafana.net`）。

4. **连接 `~/.claude/settings.json`**（或项目本地的 `.claude/settings.json`）：

   ```json
   {
     "mcpServers": {
       "grafana": {
         "command": "mcp-grafana",
         "args": ["--disable-write"],
         "env": {
           "GRAFANA_URL": "https://myorg.grafana.net",
           "GRAFANA_API_KEY": "glsa_xxxx"
         }
       }
     }
   }
   ```

   `--disable-write` 是更安全的默认值——一旦验证读取路径正常，即可移除它。

5. **重启 Claude Code，然后验证**：

   ```
   /mcp
   ```

   `grafana` 服务器应出现其工具列表。然后询问：

   ```
   我的 Grafana 实例中配置了哪些数据源？
   ```

   清晰的响应 = 正常工作。如果工具调用失败：
   - 检查 `GRAFANA_URL` 没有尾随斜杠
   - 确认 API 密钥未过期
   - 使用 `mcp-grafana --debug` 重新运行以查看原始请求/响应

### 连接 Cursor

相同的 Grafana 令牌。设置 → 功能 → MCP 服务器（或编辑 `~/.cursor/mcp.json`）：

```json
{
  "mcpServers": {
    "grafana": {
      "command": "mcp-grafana",
      "args": ["--disable-write"],
      "env": {
        "GRAFANA_URL": "https://myorg.grafana.net",
        "GRAFANA_API_KEY": "glsa_xxxx"
      }
    }
  }
}
```

以相同方式验证——Cursor 在其代理面板中显示 MCP 服务器；运行类似 "列出标记为 kubernetes 的仪表板" 的查询。

### 在团队间共享服务器 (SSE)

从 `stdio` 切换到 `SSE`，使服务器运行一次，多个代理连接到它。完整设置与 VS Code 配置参见 [references/sse-transport.md](references/sse-transport.md)。

## 安全注意事项

- API 密钥应存储在环境变量或密钥管理器中——绝不能提交到文件中。
- 在共享环境和 CI 中使用 `--disable-write`；仅在代理应被允许修改 Grafana 的特定机器上移除它。
- 将服务账户权限限制在最低：`Viewer` 足够用于查询和仪表板读取。仅在代理需要创建仪表板或注释时才授予 `Editor`。
- 通过管理 → 服务账户定期轮换令牌。

## 参考资料

- [`references/tools.md`](references/tools.md) — MCP 工具的完整列表（查询 / 仪表板 / 警报 / 车队管理 / 注释）以及如何发现实时集
- [`references/sse-transport.md`](references/sse-transport.md) — 团队共享和 VS Code 的 SSE 设置，包含 stdio-vs-SSE 决策矩阵 + 常见故障模式
- [`references/a2a.md`](references/a2a.md) — 代理到代理 (A2A) 协议，用于将推理委托给 Grafana 助手（与直接通过 MCP 调用工具相比）

## 外部资源

- [Grafana MCP 服务器 (github.com/grafana/mcp-grafana)](https://github.com/grafana/mcp-grafana)
- [模型上下文协议规范](https://spec.modelcontextprotocol.io/)
- [Grafana Cloud API 文档](https://grafana.com/docs/grafana-cloud/developer-resources/api-reference/)
- [Grafana 助手文档](https://grafana.com/docs/grafana-cloud/machine-learning/assistant/)
