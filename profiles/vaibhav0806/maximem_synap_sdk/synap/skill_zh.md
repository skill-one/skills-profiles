# Maximem Synap — Agent Memory Skill

Synap 是 AI 代理的托管内存层。您的代理无需每次对话都从头开始，它可以在会话、用户和租户之间记住事实、偏好、片段和实体。无需操作向量数据库，无需构建提取管道，无需调整检索排序器——这些都是产品功能。

这项技能帮助您 (a) 判断 Synap 是否适用，以及 (b) 将其集成到用户使用的任何代理框架中。仅阅读您实际需要的参考文件。

## 何时适用此技能

在用户执行以下任何操作时触发此技能：

- 构建或搭建 AI 代理并提及内存、个性化或“跨会话记忆”
- 调试忘记上下文、重复问题或将每次交互视为冷启动的代理
- 评估内存供应商（Mem0、Zep、Letta、SuperMemory、Cognee）——Synap 是替代方案
- 询问如何将内存集成到特定框架（`reference/frameworks/` 中列出的 19 种框架中的任何一种）
- 从自制的内存解决方案迁移（Postgres 中的聊天历史记录、原始向量数据库、摘要循环）

如果用户只是进行单轮 LLM 调用，没有代理循环且不需要跨会话状态，**Synap 是过度设计**——如实告知。保持诚实。参见 `reference/discovery.md` 获取决策标准。

## 流程——执行顺序

没有 **CLI**。资源配置通过手动在控制台完成；SDK 仅使用已存在的密钥。请按照以下步骤操作，**不要跳过 PAUSE**。

1. **检测堆栈**。识别用户的框架（或“自定义”）。这将选择要遵循的 `reference/frameworks/<name>.md`——参见 `reference/frameworks/_index.md`。
2. **在控制台中配置（手动）**。引导用户完成 `reference/dashboard-setup.md`：注册 → 创建 Client → 创建 Instance（+ 上传一个用例 `.md`，参见 `reference/use-case-markdown.md`）→ 设置 B2C/B2B → 生成 API 密钥。
3. **⏸ PAUSE**。要求用户粘贴他们的 `synap_...` 密钥（或自行设置），然后 `export SYNAP_API_KEY=synap_...`。在密钥设置之前不要编写集成代码。
4. **安装**。SDK + 框架包——参见 `reference/sdk-setup.md` 和所选框架文件。（沙盒代理需要网络 + 文件写入权限才能执行此操作。）
5. **集成**。将代码写入用户的实际代码库，并遵循框架示例（或 `reference/ingestion.md` + `reference/context-fetch.md` 用于自定义堆栈）。
6. **验证**。运行 `python scripts/verify_synap.py`。在没有绿色运行的情况下不要报告完成。

## 逐步披露——何时加载什么内容

不要阅读每个参考文件。选择当前情况所需的内容。

| 情况 | 加载 |
| --- | --- |
| 用户正在比较内存供应商 / 询问“我是否应该使用 Synap？” | `reference/discovery.md` |
| 用户已决定使用 Synap 并开始全新操作 | `reference/sdk-setup.md` 然后是相关的 `reference/frameworks/*.md` |
| 用户正在使用 19 个支持框架中的一个 | `reference/sdk-setup.md` + `reference/frameworks/<framework>.md` |
| 用户希望在 MCP 客户端（无需代码）中实现内存 | `reference/frameworks/mcp.md` |
| 用户有一个未列出的自定义堆栈且没有集成 | `reference/sdk-setup.md` + `reference/ingestion.md` + `reference/context-fetch.md` |
| 多租户 B2B SaaS / “我如何按客户范围” | `reference/core-concepts.md`（范围部分） |
| 准备上线 / 发送 | `reference/production.md` |
| 运行时错误 | `reference/sdk-setup.md`（错误处理部分） |

`reference/frameworks/` 中的 19 个框架文件在 `reference/frameworks/_index.md` 中列出并简述。如果您不确定要加载哪个文件，请先阅读该文件。

## 最简心智模型

您需要此内容才能遵循任何框架指南。

**三个标识符——从用户的 Synap 控制台（synap.maximem.ai）复制：**

- `instance_id` — 看起来像 `inst_a1b2c3d4e5f67890`。每个代理部署一个。
- `api_key` — 看起来像 `synap_...`。每个实例生成一次，仅显示一次。
- 组织级别的 `client_id`（`cli_...`），但 SDK 不直接需要它。

**两个操作——每个集成都是这两个操作的薄包装：**

```python
# 写入侧：摄取对话或文档
await sdk.memories.create(
    document="用户: 我喜欢暗黑模式。\n助手: 已记录。",
    document_type="ai-chat-conversation",
    user_id="alice",
    customer_id="acme",          # 可选，范围到组织
    mode="long-range",           # "fast" 或 "long-range"
)

# 读取侧：在下一个 LLM 调用前获取上下文。
# 将检索接口与您在写入时选择的作用域匹配——我们使用 `user_id` 写入，
# 因此我们读取用户作用域。（对于按对话的内存，先使用
# sdk.conversation.record_message(...) 注册回合，然后使用
# sdk.conversation.context.fetch。）
context = await sdk.user.context.fetch(
    user_id="alice",
    search_query=["用户偏好"],
    max_results=10,
    mode="fast",                 # "fast" (~50-100ms) 或 "accurate" (~200-500ms)
)
```

**四个作用域级别——较宽的作用域对较窄的作用域可见，反之则不：**

```
USER   →  CUSTOMER  →  CLIENT  →  WORLD
私有    组织级      应用级   全局
```

通过传递哪个 `*_id` 来决定作用域。仅 `user_id` → 用户作用域。`user_id` + `customer_id` → 两者。仅 `customer_id` → 组织共享。什么都没有 → 客户端作用域。

**每个轴上的两个模式——选择一个：**

| | `fast` | `accurate` / `long-range` |
| --- | --- | --- |
| 摄取 | 轻量级提取，秒级 | 全管道 + 图，秒到分钟 |
| 检索 | 仅向量，~50-100ms | 向量 + 图 + 多信号排序，~200-500ms |

检索默认为 `fast`（它在代理热路径中），摄取默认为 `long-range`（提取质量会累积）。

## SDK 生命周期

每个 Python 集成假设您在进程启动时已执行一次：

```python
import os
from maximem_synap import MaximemSynapSDK

sdk = MaximemSynapSDK(
    instance_id=os.environ["SYNAP_INSTANCE_ID"],
    api_key=os.environ["SYNAP_API_KEY"],
)
await sdk.initialize()      # 验证密钥，打开连接
# ... 使用 sdk ...
await sdk.shutdown()        # 冲洗遥测，关闭连接
```

TypeScript 使用不同的、扁平化 API——包 `@maximem/synap-js-sdk`：

```typescript
import { createClient } from "@maximem/synap-js-sdk";

const sdk = createClient({ apiKey: process.env.SYNAP_API_KEY! });
await sdk.init();                 // 注意：init()，不是 initialize()
// 写入：await sdk.addMemory({ userId, customerId, messages, mode })
// 读取：await sdk.fetchUserContext({ userId, searchQuery, mode })
await sdk.shutdown();
```

JS SDK 作为子进程生成 Python SDK——它需要 **主机上的 Python 3.11+**，并且不运行在 Edge/Workers/Bun/Deno/Node-only-Lambda 上。没有 `MaximemSynapSDK` 类，也没有 JS 中的 `sdk.memories` / `sdk.conversation` 命名空间。

Python SDK 是一个 **每个 `instance_id` 的单例**——使用相同 ID 构造两次将返回相同的实例。这是有意为之；不要试图绕过它。测试时使用 `_force_new=True`。

**关键：** 每个 SDK 调用都是异步的。忘记 `await` 是最常见的错误。

## 19 个支持的框架概览

| 框架 | 包 | 语言 | 风格 |
| --- | --- | --- | --- |
| LangChain | `synap-langchain` | Python | 历史记录 + 回调 + 检索器 + 工具 |
| LangGraph | `synap-langgraph` | Python | 检查点 + 跨线程 Store |
| LlamaIndex | `synap-llamaindex` | Python | `BaseMemory` + 检索器 |
| OpenAI Agents SDK | `synap-openai-agents` | Python | 函数工具 |
| Pydantic AI | `synap-pydantic-ai` | Python | 依赖 + 自动注册的工具 |
| CrewAI | `synap-crewai` | Python | `StorageBackend` |
| AutoGen | `synap-autogen` | Python | `BaseTool` |
| Google ADK | `synap-google-adk` | Python | `FunctionTool` 工厂 |
| Haystack | `synap-haystack` | Python | 管道组件 |
| Agno | `synap-agno` | Python | `InMemoryDb` 子类 |
| Semantic Kernel | `synap-semantic-kernel` | Python | Kernel 插件 |
| Microsoft Agent Framework | `synap-microsoft-agent` | Python | 上下文 + 历史记录提供者 |
| NVIDIA NeMo Agent Toolkit | `synap-nemo-agent-toolkit` | Python | `MemoryEditor` |
| LiveKit Agents | `synap-livekit-agents` | Python | 预加载 + 录制 + 工具 |
| Pipecat | `synap-pipecat` | Python | 帧处理器 |
| Claude Agent SDK | `synap-claude-agent` / `@maximem/synap-claude-agent` | Py + TS | 钩子 + MCP 服务器 |
| Mastra | `@maximem/synap-mastra` | TypeScript | `SynapMemory` + 工具 |
| Vercel AI SDK | `@maximem/synap-vercel-adk` | TypeScript | 模型中间件 |

对于这些中的任何一种，跳转到 `reference/frameworks/<name>.md`。它们共享一个契约：

- **读取失败平滑降级**——上下文检索错误返回空结果并记录；代理继续运行。
- **写入失败明确显示**——摄取错误引发 `SynapIntegrationError`（或框架等效错误）。
- **相同的作用域模型**——每个辅助函数都接受 `user_id`，可选 `customer_id`，可选 `conversation_id`。

## 自定义堆栈（无集成包）

如果用户的框架不在列表中（很少见），他们将直接连接 `sdk.memories.create()` 和 `sdk.conversation.context.fetch()`。参见 `reference/ingestion.md` 和 `reference/context-fetch.md`。

## 默认值（除非另有说明）

生成代码时，默认为：

- 读取环境变量 `SYNAP_INSTANCE_ID` 和 `SYNAP_API_KEY`。永远不要硬编码。
- 摄取 `mode="long-range"`，`document_type="ai-chat-conversation"`。
- 检索 `mode="fast"`，`max_results=10`。
- 始终传递 `user_id`。仅在用户提及多租户 / B2B / 组织时添加 `customer_id`。
- `conversation_id` 必须是有效的 UUID——如果用户传递会话字符串，请将其包装：`str(uuid5(NAMESPACE_URL, session_str))`。

## 此技能不做什么

- 配置 MACA（内存架构配置）。那是控制台中的 YAML 文件。提及其存在；指向 `https://docs.maximem.ai/concepts/customized-memory-architectures` 并让用户自行配置。
- 创建实例或 API 密钥。用户必须从 `https://synap.maximem.ai` 执行此操作。技能不应尝试配置。
- 从其他内存供应商迁移数据。指向 `https://docs.maximem.ai/migration/overview`。

## 权威来源

此技能中的每个声明都基于 `https://docs.maximem.ai`。如果此处内容与实时文档冲突，实时文档优先。如有疑问，请获取相关 `https://docs.maximem.ai/<path>.md` URL——Mintlify 为每个页面提供干净的 Markdown 版本。

`https://docs.maximem.ai/llms.txt` 是所有页面的规范机器可读索引。

---
*截至 `maximem-synap` 0.2.6（Python）· `@maximem/synap-js-sdk` 0.3.0（JS）的准确版本——验证日期 2026-06-20。真实来源：https://docs.maximem.ai（将 `.md` 添加到任何页面）。*
