---
name: deepagents-python-quickstart
description: 通过遵循官方快速入门指南，使用本地原生网络搜索代替Tavily，在Python中搭建一个最小的本地深度代理。当用户希望快速在本地构建或尝试深度代理时使用。
---

# Deep Agents Python 快速入门

请参考实时文档——不要凭记忆编造替代 API：

**https://docs.langchain.com/oss/python/deepagents/quickstart**

获取该页面（Docs MCP 或 HTTP），并实现它所展示的研究代理形状（`create_deep_agent`、研究系统提示，用研究问题如“什么是 LangGraph？”调用）。

## 本地设置限制

在快速入门的基础上应用这些（它们使设置最小化且与模型无关）：

1. **询问**要使用哪个提供者/模型。展示 Deep Agents 是与模型无关的。建议提示：

   > 此代理应使用哪个模型？传递一个 `provider:model` 字符串——例如 `openai:gpt-5.5`、`anthropic:claude-sonnet-5`、`google_genai:gemini-3.5-flash`。不确定时使用默认值：**`anthropic:claude-sonnet-5`**。  
   > 我们将使用该提供者的内置网络搜索（无需单独的搜索 API 密钥）。

2. 创建一个**新**目录（例如 `deep-agent/`），并在其中完成所有工作——不要污染公开项目。

3. **不要使用 Tavily**（或任何其他二级搜索供应商）。将快速入门的 `internet_search` / Tavily 工具替换为所选提供者的内置网络搜索。在该提供者的 LangChain 聊天文档中查找当前工具形状（截至写作时的示例——如有需要请重新确认）：

   | 提供者 | 内置搜索工具 |
   |----------|----------------------|
   | Anthropic | `{"type": "web_search_20260209", "name": "web_search", "max_uses": 5}` |
   | OpenAI | `{"type": "web_search"}` |
   | Google | `{"google_search": {}}` |

   优先选择 Anthropic / OpenAI / Google，以便提供者搜索可用。唯一的秘密是 `.env` 中的该提供者 API 密钥（git 忽略）。除非他们要求，否则跳过 LangSmith 跟踪。

4. 安装 `deepagents` (+ `python-dotenv`) 和提供者模型包——不是 `tavily-python`。

5. 运行研究示例，展示输出，然后停止。指向 `deep-agents-core` / 定制 / Managed Deep Agents 以获取下一步操作。
