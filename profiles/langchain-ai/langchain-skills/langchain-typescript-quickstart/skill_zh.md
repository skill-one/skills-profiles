# LangChain TypeScript 快速入门

请参考实时文档——不要凭记忆编造替代 API：

**https://docs.langchain.com/oss/javascript/langchain/quickstart**

获取该页面（Docs MCP 或 HTTP），并实现其展示的内容（天气代理 + `createAgent`）。需要 Node 22+。

## 本地设置限制

在快速入门的基础上应用这些限制（以保持设置最小化且与模型无关）：

1. **询问**要使用哪个提供者/模型。展示 LangChain 是与模型无关的。建议提示：

   > 此代理应使用哪个模型？传递一个 `provider:model` 字符串——例如 `openai:gpt-5.5`、`anthropic:claude-sonnet-5`、`google-genai:gemini-2.5-flash-lite`。如果您不确定，默认值为 **`anthropic:claude-sonnet-5`**。

   将快速入门的模型字符串替换为他们的选择（或默认值）。

2. 创建一个**新**目录（例如 `langchain-agent/`），并在其中完成所有工作——不要污染公开项目。

3. 唯一的秘密：`.env` 中的提供者 API 密钥（git 忽略）。除非他们询问，否则不使用 LangSmith / Tavily。最好让他们自己编辑 `.env`——不要将密钥粘贴到聊天中。

4. 如果快速入门的基础安装不足以满足他们的模型，则安装所需的提供者包。

5. 运行示例，显示输出，然后停止。指向 `langchain-fundamentals` 以获取下一步操作。
