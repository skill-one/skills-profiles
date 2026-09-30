---
name: mcp-cli
description: 通过 CLI 与 MCP（模型上下文协议）服务器接口。当您需要通过 MCP 服务器与外部工具、API 或数据源交互，列出可用的 MCP 服务器/工具，或从命令行调用 MCP 工具时使用。
---

# MCP-CLI

通过命令行访问 MCP 服务器。MCP 可用于与 GitHub、文件系统、数据库和 API 等外部系统交互。

## 命令

| 命令                            | 输出                          |
| ---------------------------------- | ------------------------------- |
| `mcp-cli`                          | 列出所有服务器和工具名称      |
| `mcp-cli <服务器>`                 | 显示带参数的工具              |
| `mcp-cli <服务器>/<工具>`          | 获取工具的 JSON 架构          |
| `mcp-cli <服务器>/<工具> '<json>'` | 带参数调用工具                |
| `mcp-cli grep "<glob>"`            | 按名称搜索工具                |

**添加 `-d` 以包含描述**（例如，`mcp-cli filesystem -d`）

## 工作流程

1. **发现**：`mcp-cli` → 查看可用的服务器和工具
2. **探索**：`mcp-cli <服务器>` → 查看带参数的工具
3. **检查**：`mcp-cli <服务器>/<工具>` → 获取完整的 JSON 输入架构
4. **执行**：`mcp-cli <服务器>/<工具> '<json>'` → 带参数运行

## 示例

```bash
# 列出所有服务器和工具名称
mcp-cli

# 查看所有带参数的工具
mcp-cli filesystem

# 带描述（更详细）
mcp-cli filesystem -d

# 获取特定工具的 JSON 架构
mcp-cli filesystem/read_file

# 调用工具
mcp-cli filesystem/read_file '{"path": "./README.md"}'

# 搜索工具
mcp-cli grep "*file*"

# JSON 输出用于解析
mcp-cli filesystem/read_file '{"path": "./README.md"}' --json

# 带引号的复杂 JSON（使用 heredoc 或 stdin）
mcp-cli server/tool <<EOF
{"content": "包含 '引号' 的文本"}
EOF

# 或从文件/命令管道
cat args.json | mcp-cli server/tool

# 查找所有 TypeScript 文件并读取第一个
mcp-cli filesystem/search_files '{"path": "src/", "pattern": "*.ts"}' --json | jq -r '.content[0].text' | head -1 | xargs -I {} sh -c 'mcp-cli filesystem/read_file "{\"path\": \"{}\"}"'
```

## 选项

| 标志         | 目的                   |
| ------------ | ------------------------- |
| `-j, --json` | 脚本用的 JSON 输出      |
| `-r, --raw`  | 原始文本内容            |
| `-d`         | 包含描述              |

## 退出代码

- `0`：成功
- `1`：客户端错误（参数错误、配置缺失）
- `2`：服务器错误（工具失败）
- `3`：网络错误
