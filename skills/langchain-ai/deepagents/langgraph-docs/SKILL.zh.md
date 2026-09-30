---
name: langgraph-docs
description: 获取并参考LangGraph Python文档，以构建有状态代理、创建多代理工作流以及实现人机交互模式。当用户询问关于LangGraph、图代理、状态机、代理编排、LangGraph API或需要LangGraph实现指导时使用。
---

# langgraph-docs

## 工作流

### 1. 获取文档索引

使用 `fetch_url` 读取：https://docs.langchain.com/llms.txt

这将返回一个包含所有可用文档及其描述的结构化列表。

### 2. 选择相关文档

从索引中识别 2-4 个最相关的 URL。优先级如下：
- **实现问题** — 具体的操作指南
- **概念问题** — 核心概念页面
- **端到端示例** — 教程
- **API 详情** — 参考文档

### 3. 获取并应用

对选定的 URL 使用 `fetch_url`，然后使用获取到的文档内容完成用户的请求。

如果 `fetch_url` 失败或返回空内容，重试一次。如果再次失败，通知用户并建议直接访问 https://langchain-ai.github.io/langgraph/。
