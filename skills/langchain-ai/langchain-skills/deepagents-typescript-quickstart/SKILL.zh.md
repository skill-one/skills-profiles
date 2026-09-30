---
name: deepagents-typescript-quickstart
description: 通过遵循官方快速入门指南，使用本地原生 web 搜索代替 Tavily，用 TypeScript 搭建一个最小的本地 Deep Agent。当用户希望快速在本地构建或尝试 Deep Agent 时使用。
---

# Deep Agents TypeScript 快速入门

请参考实时文档——不要凭记忆编造替代 API：

**https://docs.langchain.com/oss/javascript/deepagents/quickstart**

获取该页面（Docs MCP 或 HTTP），并实现它展示的研究代理形状（`createDeepAgent`、研究系统提示，用研究问题如“什么是 LangGraph？”调用）。需要 Node 22+。

## 本地设置限制

在快速入门的基础上应用这些（它们使设置最小化且与模型无关）：

1. **询问**要使用哪个提供者/模型。展示 Deep Agents 是与模型无关的。建议提示：

   > 此代理应使用哪个模型？传递一个 `provider:model` 字符串——例如 `openai:gpt-5.5`、`anthropic:claude-sonnet-5`、`google-genai:gemini-3.5-flash`。不确定时默认：**`anthropic:claude-sonnet-5`**。  
   > 我们将使用该提供者的内置网络搜索（无需单独的搜索 API 密钥）。

2. 创建一个**新**目录（例如 `deep-agent/`），并在其中完成所有工作——不要污染公开项目。

3. **不要使用 Tavily**（或 `@langchain/tavily`）。用所选提供者的内置网络搜索替换快速入门的搜索工具。在该提供者的 LangChain 文档中查找当前的导出/工具形状（截至写作时的示例——如有需要请重新检查）：

   | 提供者     | 内置搜索工具          |
   |------------|----------------------|
   | Anthropic  | `@langchain/anthropic` `tools.webSearch_*()`（或等效字典） |
   | OpenAI     | `{ type: "web_search" }` |
   | Google     | `{ google_search: {} }` |

   优先选择 Anthropic / OpenAI / Google 以便提供者搜索可用。唯一的秘密：`.env` 中的该提供者的 API 密钥（git 忽略）。除非他们要求，否则跳过 LangSmith 跟踪。

4. 从快速入门安装包**减去**Tavily；添加提供者包以用于其模型。

5. 运行研究示例，显示输出，然后停止。指向 `deep-agents-core` / 定制 / Managed Deep Agents 以获取下一步操作。
