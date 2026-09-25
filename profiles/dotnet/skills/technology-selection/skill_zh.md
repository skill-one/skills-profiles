# .NET 人工智能与机器学习

首先选择合适的技术，然后仅交付**任务所要求的内容**。如果任务要求提供计划、比较或架构（或说明“不要编写代码”），则提供这些内容——不要未经提示就搭建、构建或运行代码。

## 第一步：分类任务（决策树）

说明哪个分支适用及其原因，然后选择该技术。

| 任务类型 | 技术 | 原因 |
|---------|------|------|
| 结构化/表格化：分类、回归、聚类、异常检测、推荐 | **ML.NET** (`Microsoft.ML`) | 确定性（固定种子），无云依赖，专门构建 |
| 自然语言理解、生成、摘要、推理（单提示→响应，无需工具） | **通过 Microsoft.Extensions.AI 的 LLM** (`IChatClient`) | 语言能力，无需编排 |
| 代理式：多步工具/函数调用、代理循环、多代理 | **Microsoft Agent Framework** (`Microsoft.Agents.AI`) 在 **Microsoft.Extensions.AI** 上 | 需要编排、工具调度、迭代控制 `IChatClient` 缺失 |
| GitHub Copilot 扩展 / 自定义开发流程代理 | **GitHub Copilot SDK** (`GitHub.Copilot.SDK`) | 与 Copilot 代理运行时集成 |
| 在生产中运行预训练/自定义模型 | **ONNX Runtime** (`Microsoft.ML.OnnxRuntime`) | 硬件加速，格式无关的推理 |
| 本地/离线 LLM 推理 | **OllamaSharp** ([Ollama 模型](https://ollama.com/search)) | 关注隐私，离线，成本受限 |
| 语义搜索、RAG、嵌入存储 | **Microsoft.Extensions.VectorData.Abstractions** (MEVD) + 提供者（Azure AI Search、Milvus、MongoDB、pgvector、Pinecone、Qdrant、Redis、SQL） | 提供者无关的向量搜索 |
| 读取、分块、加载文档到向量存储 | **Microsoft.Extensions.AI.DataIngestion** (预览) + MEVD | 解析、分块、嵌入、插入 |
| 既包含结构化预测又包含自然语言推理 | **混合**：ML.NET 评分 + LLM 推理层 | ML.NET 是可重复的；LLM 增加解释 |

**关键规则**：**不要**使用 LLM 处理 ML.NET 能很好地处理的任务（表格分类、回归、聚类）——LLM 在这些任务上更慢、成本更高且非确定性。

## 第一步 b：选择库层

| 层 | 库 | 使用场景 |
|----|-----|---------|
| **抽象** | `Microsoft.Extensions.AI` (MEAI) | 始终作为基础。直接使用 `IChatClient` 进行提示响应和简单的、有边界的函数调用。 |
| **提供者 SDK** | `Azure.AI.OpenAI` / `OpenAI` / `Azure.AI.Inference` / `OllamaSharp` | MEAI 背后的具体提供者，通过 `AddChatClient` 访问。 |
| **编排** | `Microsoft.Agents.AI` (预发布) | 多步工具使用、持久代理循环和多代理工作流。 |
| **Copilot** | `GitHub.Copilot.SDK` | 仅用于构建 Copilot 平台扩展。 |

规则：从 MEAI 开始；通过 `AddChatClient` 将提供者置于其后（不要在业务逻辑中直接调用提供者）；使用 `Microsoft.Agents.AI` 进行多步或持久代理工作流，而不是手滚代理循环；**不要**在相同工作流中混合原始 `HttpClient` 到 OpenAI 的调用和 MEAI。**不要**使用 Accord.NET（已归档）。对于新项目，除非现有的 Semantic Kernel 功能或投资是要求，否则优先选择 MEAI 和 Agent Framework。通过依赖注入注册 AI/ML 服务；从 user-secrets / env / Key Vault 加载密钥——**不要**硬编码密钥。

## 第二步：覆盖分支核心要素，然后决定深度

每个答案——无论是计划还是实现——都必须解决所选分支的约束条件：

- **ML.NET** — `new MLContext(seed: …)`（可重复）；`TrainTestSplit` + 在保留集上评估；报告真实指标（MicroAccuracy/MacroAccuracy/LogLoss、AUC/F1 或 RMSE/R²）；使用 `PredictionEnginePool<TIn,TOut>`（**不要**使用单例 `PredictionEngine`）。
- **LLM (MEAI)** — 依赖通过 `AddChatClient` 注册的 `IChatClient`（其背后的提供者）；在 `ChatOptions` 中设置 `Temperature` 和 `MaxOutputTokens`；添加重试/超时 (`RetryingChatClient`/Polly)；锁定一个日期模型；从 user-secrets / env / Key Vault 加载密钥——**不要**硬编码 `sk-…` 密钥；使用模式验证非确定性输出，并设置回退。
- **代理式 (Agent Framework)** — 使用 `Microsoft.Agents.AI` 在 `IChatClient` 上编排（**不要**手滚循环）；设置 `MaximumIterations` 和一个令牌/成本上限；使用清晰的模式定义每个工具 (`AIFunctionFactory.Create`)；记录每一步（**不要**记录原始敏感内容）。
- **RAG / 嵌入** — 语义**分块**（不是固定大小）；`IEmbeddingGenerator` 和**缓存嵌入**（不要按查询重新嵌入）；使用 `Microsoft.Extensions.VectorData.Abstractions` (MEVD) + 用户请求的提供者（例如 pgvector）存储/查询；按**最小相似度分数**过滤；保持每个答案的**来源归属**。尊重用户指定的 UI/存储；仅使用真实、现有的 NuGet 包。

**然后选择深度：**

- **仅计划/比较/架构**（或“不要编写代码”）：仅使用上述核心要素从本文件中回答。**不要**打开参考——这里的分支核心要素足以用于选择或计划。对于 RAG 计划，涵盖聊天、摄取/分块、嵌入、向量存储、来源归属以及请求的 UI/存储。
- **编写实现代码**：阅读匹配的参考（针对包和实现指导）（仅阅读所选分支；对于混合，阅读经典的 ML.NET 和 LLM）：
  - 经典 ML.NET → [`references/classic-ml.md`](references/classic-ml.md)
  - LLM 集成 (MEAI) → [`references/llm.md`](references/llm.md)
  - 代理式 (Agent Framework) → [`references/agentic.md`](references/agentic.md)
  - RAG / 嵌入 / 摄取 → [`references/rag.md`](references/rag.md)
  - GitHub Copilot 扩展 → [`references/copilot.md`](references/copilot.md)
  - ONNX Runtime 推理 → [`references/onnx.md`](references/onnx.md)
  - 本地/离线 LLM 与 Ollama → [`references/ollama.md`](references/ollama.md)

## 验证

- [ ] 选择遵循决策树——没有使用 LLM 处理 ML.NET 能处理的任务
- [ ] 仅交付所要求的内容（仅计划请求得到计划，而不是代码）
- [ ] AI/ML 服务通过依赖注入注册；配置通过 `IOptions<T>`；密钥来自安全源
- [ ] 满足分支约束（第二步核心要素，以及实现时的参考）
- [ ] 实现后，构建并运行现有测试

## 应拒绝的反模式

| 反模式 | 重定向 |
|-------|--------|
| 使用 LLM 进行表格分类 | 使用 **ML.NET** — 更快、更便宜、确定性 |
| 没有重试/超时的 LLM 调用 | 添加 `RetryingChatClient` 或 Polly 重试 |
| 提交到 `appsettings.json` 的 API 密钥 | user-secrets / env / Key Vault |
| Accord.NET，或在没有要求的情况下默认使用 Semantic Kernel | ML.NET；新工作优先选择 MEAI + `Microsoft.Agents.AI` |
| 使用 `IChatClient` 手滚多步工具循环 | `Microsoft.Agents.AI` (`MaximumIterations`，工具调度) |
| 使用 Agent Framework 进行单提示→响应 | 直接使用 `IChatClient` |
| 业务逻辑中与 MEAI 并存的原始 `HttpClient`/OpenAI SDK | 单一抽象层；依赖 `IChatClient` |
| ASP.NET Core 中的 `PredictionEngine` 单例 | `PredictionEnginePool<TIn,TOut>`（不线程安全） |
| 没有分块或相关性过滤的 RAG | 语义分块 + 最小相似度分数 |
| 从头开始在 .NET 中构建自定义神经网络 | 通过 ONNX Runtime 或 LLM API 预训练 |
