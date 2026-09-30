---
name: context-mode
description: Antigravity CLI的强制路由规则。在探索代码库、读取用于分析文件、列出上下文模式工具、搜索、解析、计数、比较、总结、获取网络内容或运行数据密集型命令时调用。
---

# Antigravity CLI 的 context-mode

context-mode MCP 工具在 agy 中以 `context-mode/<工具>` 的形式提供。
直接使用这些工具。不要检查 `~/.gemini/antigravity-cli/mcp/context-mode/*.json` 下的缓存模式文件，也不要运行 `ctx_execute` 仅用于发现工具名称或模式。

如果 agy 使用通用的 MCP 包装器，请使用以下参数调用 `call_mcp_tool`：

- `ServerName`: `"context-mode"`
- `ToolName`: 下方列出的工具名称之一
- `Arguments`: 该工具的 JSON 参数

## 工具列表

- `context-mode/ctx_execute`: 在沙盒中运行 JavaScript、TypeScript、Python、shell 或其他代码。仅打印最终答案。
- `context-mode/ctx_execute_file`: 将一个文件读入沙盒中的 `FILE_CONTENT` 并对其运行代码。这是 context-mode 文件读取接口。
- `context-mode/ctx_batch_execute`: 在一个批次中运行多个仓库命令，索引大型输出，并回答后续查询。
- `context-mode/ctx_index`: 将文件、目录或内容存储在本地 FTS5 知识库中以便后续搜索。
- `context-mode/ctx_search`: 搜索索引内容和捕获的会话内存。将相关问题批量放入 `queries`。
- `context-mode/ctx_fetch_and_index`: 获取网络内容，存储它，然后用 `ctx_search` 进行查询。
- `context-mode/ctx_stats`: 显示上下文节省和当前会话统计信息。
- `context-mode/ctx_doctor`: 诊断 context-mode 运行时和钩子健康状况。
- `context-mode/ctx_upgrade`: 提供升级或修复指导。
- `context-mode/ctx_purge`: 经确认后清除存储的 context-mode 知识。
- `context-mode/ctx_insight`: 启动或报告 Insight 分析应用。

当用户询问“有哪些 context-mode 工具可用”时，请从本列表回答。不要列出 `~/.gemini/antigravity-cli/mcp/context-mode`，也不要读取 JSON 模式文件。

## 文件读取

没有单独的 `ctx_read` 工具。对于需要分析、总结、提取、计数、过滤或比较的文件读取，请使用 `context-mode/ctx_execute_file`。

原生 `Read` / `view_file` 仅在需要对话中精确字节，或用户明确要求查看一小段已知范围时才适用。

默认使用 JavaScript 进行轻量级文件分析：

```json
{
  "path": "README.md",
  "language": "javascript",
  "code": "const lines = FILE_CONTENT.split(/\\r?\\n/); console.log(lines.slice(0, 20).join('\\n'));"
}
```

除非用户明确要求完整文件转储，否则不要原样打印 `FILE_CONTENT`。打印选定的行、计数、匹配项、摘要或结构化结果。

## 代码库探索

对于仓库探索，优先使用一个 `context-mode/ctx_batch_execute` 调用，而不是多次原生 `ListDir`、`Read`、`Grep` 或 shell 调用。

对于一次性计算答案，使用 `context-mode/ctx_execute`。
对于单文件分析，使用 `context-mode/ctx_execute_file`。
对于跨后续问题的持久记忆，使用 `context-mode/ctx_index` 并提供描述性的 `source`，然后使用 `context-mode/ctx_search`。

返回简洁的推导答案。不要将原始命令转储、完整文件、大型搜索结果、缓存模式或原始 HTML 粘贴到对话中。
