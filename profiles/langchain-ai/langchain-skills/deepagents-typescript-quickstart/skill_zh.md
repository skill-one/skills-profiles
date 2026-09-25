# Deep Agents TypeScript 快速入门

请参考实时文档——不要凭记忆编造替代 API：

**https://docs.langchain.com/oss/javascript/deepagents/quickstart**

打开该页面（Docs MCP 或 HTTP），并实现它展示的研究代理形状（`createDeepAgent`、研究系统提示，用研究问题如“LangGraph 是什么？”调用）。需要 Node 22+。

## 本地设置限制

在快速入门的基础上应用这些限制（它们可以保持设置最小化且与模型无关）：

1. **询问**要使用哪个提供者/模型。展示 Deep Agents 是与模型无关的。建议提示：

   > 此代理应使用哪个模型？传递一个 `provider:model` 字符串——例如 `openai:gpt-5.5`、`anthropic:claude-sonnet-5`、`google-genai:gemini-3.5-flash`。如果不确定，默认为 **`anthropic:claude-sonnet-5`**。  
   > 我们将使用该提供者的内置网络搜索（无需单独的搜索 API 密钥）。

2. 创建一个**新**目录（例如 `deep-agent/`），并在其中完成所有工作——不要污染公开项目。

3. **不要使用 Tavily**（或 `@langchain/tavily`）。用所选提供者的内置网络搜索替换快速入门的搜索工具。在提供者的 LangChain 文档中查找当前的导出/工具形状（截至写作时的示例——如有需要请重新检查）：

   | 提供者 | 内置搜索工具 |
   |----------|----------------------|
   | Anthropic | `@langchain/anthropic` `tools.webSearch_*()`（或等效字典） |
   | OpenAI | `{ type: "web_search" }` |
   | Google | `{ google_search: {} }` |

   优先选择 Anthropic / OpenAI / Google，以便提供者搜索可用。唯一的秘密：在 `.env` 中的提供者 API 密钥（git 忽略）。除非他们要求，否则跳过 LangSmith 跟踪。

4. 从快速入门安装包**排除** Tavily；添加提供者包以使用其模型。

5. 运行研究示例，展示输出，然后停止。指向 `deep-agents-core` / 定制 / Managed Deep Agents 以获取下一步操作。
