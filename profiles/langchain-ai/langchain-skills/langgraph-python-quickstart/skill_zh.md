# LangGraph Python 快速入门

请参考实时文档——不要凭记忆编造替代 API：

**https://docs.langchain.com/oss/python/langgraph/quickstart**

获取该页面（Docs MCP 或 HTTP），并实现其展示的内容（使用 Graph API 的计算器 / 数学代理）。除非用户要求，否则优先选择 Graph API 路径而不是 Functional API。跳过 IPython 图形可视化。

## 本地环境设置限制

在快速入门的基础上应用这些设置（它们可以保持设置最小化且与模型无关）：

1. **询问**要使用的提供者/模型。展示 LangGraph 可以与任何 LangChain 聊天模型协同工作。建议提示：

   > 此代理应使用哪个模型？传递一个 `provider:model` 字符串——例如 `openai:gpt-5.5`、`anthropic:claude-sonnet-5`、`google_genai:gemini-2.5-flash-lite`。如果您不确定，默认值为 **`anthropic:claude-sonnet-5`**。

   文档中经常硬编码 Anthropic——使用 `init_chat_model("<MODEL>")`（或等效方式）替换他们的选择。如果使用 Claude Sonnet 5+，则省略 `temperature` / `top_p` / `top_k`（不受支持）。

2. 创建一个**新的**目录（例如 `langgraph-agent/`），并在其中完成所有工作——不要污染开放项目。

3. 唯一的秘密：`.env` 中的提供者 API 密钥（git 忽略）。除非他们要求，否则不使用 LangSmith / Tavily。优先让他们自己编辑 `.env`——不要将密钥粘贴到聊天中。

4. 安装快速入门中的包以及他们模型所需的提供者包。

5. 运行示例（例如“将 3 和 4 相加。”），显示输出，然后停止。指向 `langgraph-fundamentals` 以获取下一步操作。对于更高级的代理 API，请使用 LangChain 的 `create_agent`。
