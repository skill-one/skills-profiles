# Microsoft 文档

Microsoft 技术生态系统中的研究技能。涵盖 learn.microsoft.com 以及其外部存在的文档（VS Code、GitHub、Aspire、Agent Framework 仓库）。

---

## 默认：Microsoft Learn MCP

使用这些工具进行 learn.microsoft.com 上的**所有内容** — Azure、.NET、M365、Power Platform、Agent Framework、Semantic Kernel、Windows 等。这是绝大多数 Microsoft 文档查询的主要工具。

| 工具 | 目的 |
|------|---------|
| `microsoft_docs_search` | 搜索 learn.microsoft.com — 概念、指南、教程、配置 |
| `microsoft_code_sample_search` | 从 Learn 文档中查找可工作的代码片段。传递 `language` (`python`, `csharp`, 等) 以获得最佳结果 |
| `microsoft_docs_fetch` | 从特定 URL 获取完整页面内容（当搜索摘要不够时） |

在搜索后使用 `microsoft_docs_fetch`，当你需要完整教程、所有配置选项，或当搜索摘要是截断时。

### CLI 替代方案

如果 Learn MCP 服务器不可用，请从你的终端或 shell（例如 Bash、PowerShell 或 cmd）使用 `mslearn` CLI：

```bash
# 直接运行（无需安装）
npx @microsoft/learn-cli search "BlobClient UploadAsync Azure.Storage.Blobs"

# 或者全局安装后运行
npm install -g @microsoft/learn-cli
mslearn search "BlobClient UploadAsync Azure.Storage.Blobs"
```

| MCP 工具 | CLI 命令 |
|----------|-------------|
| `microsoft_docs_search(query: "...")` | `mslearn search "..."` |
| `microsoft_code_sample_search(query: "...", language: "...")` | `mslearn code-search "..." --language ...` |
| `microsoft_docs_fetch(url: "...")` | `mslearn fetch "..."` |

向 `search` 或 `code-search` 传递 `--json` 以获得原始 JSON 输出以进行进一步处理。

---

## 异常：何时使用其他工具

以下类别**位于** learn.microsoft.com 之外。请使用指定的工具。

### .NET Aspire — 使用 Aspire MCP 服务器（首选）或 Context7

Aspire 文档位于 **aspire.dev**，而不是 Learn。最佳工具取决于你的 Aspire CLI 版本：

**CLI 13.2+**（推荐）— Aspire MCP 服务器包含内置的文档搜索工具：

| MCP 工具 | 描述 |
|----------|-------------|
| `list_docs` | 列出所有可用的 aspire.dev 文档 |
| `search_docs` | 在 aspire.dev 内容中进行加权词法搜索 |
| `get_doc` | 通过 slug 检索特定文档 |

这些随 Aspire CLI 13.2 提供（[PR #14028](https://github.com/dotnet/aspire/pull/14028)）。要更新：`aspire update --self --channel daily`。参考：https://davidpine.dev/posts/aspire-docs-mcp-tools/

**CLI 13.1** — MCP 服务器提供集成查找（`list_integrations`, `get_integration_docs`），但**不**提供文档搜索。回退到 Context7：

| 库 ID | 用于 |
|---|---|
| `/microsoft/aspire.dev` | 主要 — 指南、集成、CLI 参考、部署 |
| `/dotnet/aspire` | 运行时源 — API 内部、实现细节 |
| `/communitytoolkit/aspire` | 社区集成 — Go、Java、Node.js、Ollama |

### VS Code — 使用 Context7

VS Code 文档位于 **code.visualstudio.com**，而不是 Learn。

| 库 ID | 用于 |
|---|---|
| `/websites/code_visualstudio` | 用户文档 — 设置、功能、调试、远程开发 |
| `/websites/code_visualstudio_api` | 扩展 API — webviews、TreeViews、命令、贡献点 |

### GitHub — 使用 Context7

GitHub 文档位于 **docs.github.com** 和 **cli.github.com**。

| 库 ID | 用于 |
|---|---|
| `/websites/github_en` | Actions、API、仓库、安全、管理、Copilot |
| `/websites/cli_github` | GitHub CLI (`gh`) 命令和标志 |

### Agent Framework — 使用 Learn MCP + Context7

Agent Framework 教程位于 learn.microsoft.com（使用 `microsoft_docs_search`），但**GitHub 仓库**具有 API 级别的详细信息，通常领先于已发布的文档 — 特别是 DevUI REST API 参考、CLI 选项和 .NET 集成。

| 库 ID | 用于 |
|---|---|
| `/websites/learn_microsoft_en-us_agent-framework` | 教程 — DevUI 指南、跟踪、工作流编排 |
| `/microsoft/agent-framework` | API 详细信息 — DevUI REST 端点、CLI 标志、认证、.NET `AddDevUI`/`MapDevUI` |

**DevUI 提示：** 查询 Learn 网站源以获取如何指南，然后查询仓库源以获取 API 级别的详细信息（端点模式、代理配置、认证令牌）。

---

## Context7 设置

对于任何 Context7 查询，首先解析库 ID（每个会话一次）：

1. 调用 `mcp_context7_resolve-library-id` 并提供技术名称
2. 调用 `mcp_context7_query-docs` 并使用返回的库 ID 和特定查询

---

## 编写有效的查询

具体说明 — 包括版本、意图和语言：

```
# ❌ 太宽泛
"Azure Functions"
"agent framework"

# ✅ 具体
"Azure Functions Python v2 programming model"
"Cosmos DB partition key design best practices"
"GitHub Actions workflow_dispatch inputs matrix strategy"
"Aspire AddUvicornApp Python FastAPI integration"
"DevUI serve agents tracing OpenTelemetry directory discovery"
"Agent Framework workflow conditional edges branching handoff"
```

包含上下文：
- **版本** 当相关时（`.NET 8`, `Aspire 13`, `VS Code 1.96`）
- **任务意图** (`quickstart`, `tutorial`, `overview`, `limits`, `API reference`)
- **语言** 对于多语言文档 (`Python`, `TypeScript`, `C#`)
