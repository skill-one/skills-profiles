<!-- GENERATED from convex-agents content/capabilities/agent.json — do not edit by hand. -->

# 添加 AI 代理 / RAG 后端

安装 @convex-dev/agent 以实现持久线程、消息历史记录、工具调用以及向量搜索/RAG — 这是应用内 AI 代理的后端。默认通过 Convex AI Gateway 调用模型：Convex 持有提供者凭证，因此无需获取、存储或轮换 LLM 密钥。

## 工作流程

1.  安装 @convex-dev/agent + @convex-dev/ai-sdk-provider；将代理组件添加到 convex.config.ts。
2.  使用 `languageModel: convexGateway("provider/model")` 定义代理（工具、指令） — 无需 API 密钥（需要在 Convex Cloud 部署上使用 convex 1.45+，付费计划）。
3.  创建线程 + 流式传输消息；在 Convex 中持久化历史记录。
4.  对于 RAG：将文档嵌入到向量索引中并在工具中检索。网关目前不提供嵌入服务，因此通过 `env` 微功率存储嵌入提供者的密钥。
5.  仅当网关不可用时（免费计划、自托管、本地后端）：通过 `env` 微功率存储的密钥调用提供者 SDK。

## 规则

- 默认使用 Convex AI Gateway (`@convex-dev/ai-sdk-provider` 中的 `convexGateway`) 进行模型调用；仅在网关不可用时（免费计划、自托管、本地后端）回退到 Convex 环境中的提供者密钥。
- 永远不要在前端暴露提供者 API 密钥；当需要时（嵌入、网关回退），通过 `env` 微功率将其保存在 Convex 环境中。
- 在 actions 中运行模型调用（如果 SDK 需要，则使用 'use node'）。
- 在 Convex 中持久化线程/消息，以实现持久性和响应性。
