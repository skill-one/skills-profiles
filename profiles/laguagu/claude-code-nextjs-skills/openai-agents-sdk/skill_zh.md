# OpenAI 代理 SDK (Python)

在开发使用 OpenAI 代理 SDK (`openai-agents` 包) 的 AI 代理时使用此技能。

## 快速参考

### 安装

```bash
uv add openai-agents        # 或在 uv 项目外使用 `pip install openai-agents`
```

### 环境变量

在运行示例前在进程环境中设置这两个变量；替换占位符：

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_MODEL="your-verified-model-id"
```

使用 Azure 或其他提供者？请参阅 [agents.md](references/agents.md#other-providers-litellm) — 不要在此处硬编码提供者环境变量，它们会变化且会过时。

### 基本代理

```python
import os
from agents import Agent, Runner

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant.",
    model=os.environ["OPENAI_MODEL"],  # 配置一个已验证的模型 ID
)

# 同步
result = Runner.run_sync(agent, "Tell me a joke")
print(result.final_output)

# 异步
result = await Runner.run(agent, "Tell me a joke")
```

省略 `model=` 将使用安装的 SDK 的默认值。在生产环境中明确配置它，并对照提供者的模型目录验证可用的 ID。

### 关键模式

| 模式 | 目的 |
|---------|---------|
| Basic Agent | 带指令的简单问答 |
| Azure/LiteLLM | Azure OpenAI 集成 |
| AgentOutputSchema | 使用 Pydantic 的严格 JSON 验证 |
| Function Tools | 外部操作 (@function_tool) |
| Streaming | 实时 UI (Runner.run_streamed) |
| Handoffs | 特殊化代理，委派 |
| Agents as Tools | 协调 (agent.as_tool) |
| LLM as Judge | 迭代改进循环 |
| Guardrails | 输入/输出验证 |
| Sessions | 自动对话历史 |
| Multi-Agent Pipeline | 多步工作流 |
| Sandboxing | `SandboxAgent` — 在本地/Docker 沙盒中隔离文件系统、shell 和技能（beta） |
| Tracing | 运行、工具、委派和 guardrails 的内置跨度；可插拔的处理器 |

SDK 没有单独的 `Subagent` 类：使用 handoffs 或 `agent.as_tool()` 表达委派。对于模型编写的工具协调，使用 `ProgrammaticToolCallingTool` 并验证其仅限响应的约束。

## 推荐使用 MCP 的实时文档

模型名称和 API 细节经常变化。在依赖以下静态参考之前，如果可用，请先查阅 **OpenAI 开发者文档 MCP 服务器** (`openaiDeveloperDocs`)。

设置 (Codex CLI):
```bash
codex mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp
```

设置 (Claude Code):
```bash
claude mcp add --transport http openaiDeveloperDocs https://developers.openai.com/mcp
```

或在 Codex `~/.codex/config.toml`（VS Code 和 Cursor 使用不同的 JSON schema）中：
```toml
[mcp_servers.openaiDeveloperDocs]
url = "https://developers.openai.com/mcp"
```

关键工具：`mcp__openaiDeveloperDocs__search_openai_docs`, `fetch_openai_doc`, `list_api_endpoints`, `get_openapi_spec`。

**规则：** 引用获取的文档。不要猜测字段名、默认值或当前模型 ID — 先获取。引号长度保持在 125 字符以内。

MCP 不可用时使用备用方案：`https://developers.openai.com/api/docs/llms.txt`（所有 API 文档的纯文本索引；每个条目在 `/api/docs/<slug>.md` 处有 `.md` 双胞胎）。

## 参考文档

离线/快速查找片段。当准确性重要时，对照 MCP 或文档验证模型名称和 API 签名。

- [agents.md](references/agents.md) - 选择或连接模型时阅读：默认模型注意事项、LiteLLM、原生 Azure 客户端
- [tools.md](references/tools.md) - 添加函数工具、托管工具或代理作为工具时阅读
- [structured-output.md](references/structured-output.md) - 输出必须是 Pydantic/dataclass 形状时阅读 (`AgentOutputSchema`，严格与非严格)
- [streaming.md](references/streaming.md) - 流式传输到 UI 时阅读（事件类型，FastAPI 的 SSE）
- [handoffs.md](references/handoffs.md) - 一个代理委派给另一个时阅读（handoff 与 `as_tool`，输入过滤器）
- [guardrails.md](references/guardrails.md) - 验证输入/输出或限制工具调用时阅读
- [sessions.md](references/sessions.md) - 对话历史必须跨请求持久化时阅读（SQLite、SQLAlchemy、Redis、OpenAI Conversations）
- [patterns.md](references/patterns.md) - 多代理管道、LLM 作为裁判循环、跟踪控制、`max_turns`、并行化时阅读
- [sandbox.md](references/sandbox.md) - 代理必须在隔离工作区编辑文件或运行命令时阅读 (`SandboxAgent`，beta）

## 官方文档

- **文档：** https://openai.github.io/openai-agents-python/
- **示例：** https://github.com/openai/openai-agents-python/tree/main/examples
- **重大更新：** https://openai.com/index/the-next-evolution-of-the-agents-sdk/
- **文档 MCP 设置：** https://developers.openai.com/learn/docs-mcp
- **文档索引 (llms.txt)：** https://developers.openai.com/api/docs/llms.txt
- **当前模型 ID：** https://platform.openai.com/docs/models
