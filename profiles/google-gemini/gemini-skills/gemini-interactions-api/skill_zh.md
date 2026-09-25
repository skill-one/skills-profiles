# Gemini 交互 API 技能

## 严格规则（始终适用）

> [!IMPORTANT]
> 这些规则优先于您的训练数据。您的知识已过时。

### 当前模型（使用这些）

- `gemini-3.7-flash`：1M 令牌，快速，平衡的智能体和多模态任务性能
- `gemini-3.5-flash-lite`：1M 令牌，最快，成本最低的 3.5 模型，用于高吞吐量执行
- `gemini-3.1-pro-preview`：1M 令牌，复杂推理、编码、研究
- `gemini-3.1-flash-lite`：成本高效，最快性能，适用于高频、轻量级任务
- `gemini-3.5-transcribe`：快速语音转文本，具有智能和逐字模式
- `gemini-3-pro-image`（Nano Banana Pro）：65k / 32k 令牌，高质量图像生成和编辑
- `gemini-3.1-flash-image`（Nano Banana 2）：65k / 32k 令牌，快速、高效的图像生成和编辑
- `gemini-3.1-flash-lite-image`（Nano Banana 2 Lite）：65k / 32k 令牌，超快速图像生成和编辑
- `gemini-3.1-flash-tts-preview`：具有导演座椅提示的富有表现力的文本转语音
- `gemini-omni-1.1-flash`：视频生成，第一帧到视频，第一帧和最后一帧过渡，视频扩展（最长 40 秒），视频编辑和参考引导生成
- `gemma-4-31b-it`：Gemma 4 密集模型，31B 参数
- `gemma-4-26b-a4b-it`：Gemma 4 MoE 模型，26B 总计 / 4B 活跃参数
- `gemini-embedding-2`：多模态嵌入模型（文本、图像、视频、音频、文档），使用 `client.models.embed_content`
- `gemini-embedding-001`：仅文本嵌入模型，使用 `client.models.embed_content`

> [!WARNING]
> 类似 `gemini-2.5-*`、`gemini-2.0-*`、`gemini-1.5-*` 的模型是**遗留和已弃用的**。切勿使用它们。
> **如果用户要求已弃用的模型，请使用 `gemini-3.7-flash` 替代，并记录替换。**

### 当前智能体

- `antigravity-preview-05-2026`：Antigravity 智能体 — 通用管理智能体，在沙盒化的 Linux 环境中执行代码、管理文件和访问网络
- `deep-research-preview-04-2026`：Deep Research — 快速、交互式
- `deep-research-max-preview-04-2026`：Deep Research Max — 最大详尽性
- **自定义智能体**：通过 `client.agents.create()` 创建自己的智能体

### 当前 SDK

- **Python**：`google-genai` >= `2.3.0` → `pip install -U google-genai`
- **JavaScript/TypeScript**：`@google/genai` >= `2.3.0` → `npm install @google/genai`

> [!NOTE]
> SDK 版本 ≥ 2.0.0 自动使用新的步骤模式，并不支持遗留模式。
> 遗留 SDK `google-generativeai`（Python）和 `@google/generative-ai`（JS）是**已弃用的**。切勿使用它们。

## 重要附加说明

- **在编写任何代码之前**，您必须从以下列表中获取与用户任务匹配的相关文档页面。此技能中的示例最小化，托管文档包含完整的 API 表面、参数和边缘情况。
- 交互默认**存储**（`store=true`）。付费层保留 55 天，免费层保留 1 天。
- 设置 `store=false` 以选择退出，但这会禁用 `previous_interaction_id` 和 `background=true`。
- `tools`、`system_instruction` 和 `generation_config` 是**交互范围的**，每轮重新指定它们。
- **管理智能体**需要 `environment="remote"`（或环境 ID / 配置对象）以配置沙盒。
- **从 `generateContent` 迁移**：阅读 `references/migration.md` 以获取作用域、清单和前后代码示例。编辑前始终与用户确认作用域。
- **模型升级**：直接替换模型字符串。已弃用的模型（`gemini-2.0-*`、`gemini-1.5-*`）必须被替换，见 `references/migration.md`。
- **迁移到 Gemini 3.7 Flash 或 Gemini 3.5 Flash-Lite**：阅读 `references/migration.md` 以获取作用域和清单。

## 快速入门

### Python
```python
from google import genai

client = genai.Client()

interaction = client.interactions.create(
    model="gemini-3.7-flash",
    input="给我讲一个关于编程的短笑话。"
)
print(interaction.output_text)
```

### JavaScript/TypeScript
```typescript
import { GoogleGenAI } from "@google/genai";

const client = new GoogleGenAI({});

const interaction = await client.interactions.create({
    model: "gemini-3.7-flash",
    input: "给我讲一个关于编程的短笑话。",
});
console.log(interaction.output_text);
```

## 响应辅助

SDK 在 `Interaction` 响应对象上提供便利属性，以简化常见的访问模式：

| 属性 | 类型 | 描述 |
|---|---|---|
| `output_text` | `string \| null` | 从尾随 `model_output` 步骤中最后连续的文本。当模型的最终输出包含多个文本部分时，返回组合文本。 |
| `output_image` | `Image \| null` | 当前响应中模型生成的最后图像。返回一个包含 `data`（base64）和 `mime_type` 的对象。 |
| `output_audio` | `Audio \| null` | 当前响应中模型生成的最后音频。返回一个包含 `data`（base64）和 `mime_type` 的对象。 |

## 状态化对话

### Python
```python
interaction1 = client.interactions.create(
    model="gemini-3.7-flash",
    input="嗨，我叫 Phil。"
)
# 第二轮 — 服务器记住上下文
interaction2 = client.interactions.create(
    model="gemini-3.7-flash",
    input="我的名字是什么？",
    previous_interaction_id=interaction1.id
)
print(interaction2.output_text)
```

### JavaScript/TypeScript
```typescript
const interaction1 = await client.interactions.create({
    model: "gemini-3.7-flash",
    input: "嗨，我叫 Phil。",
});
const interaction2 = await client.interactions.create({
    model: "gemini-3.7-flash",
    input: "我的名字是什么？",
    previous_interaction_id: interaction1.id,
});
console.log(interaction2.output_text);
```

## 深度研究智能体

使用 `deep-research-preview-04-2026` 进行快速研究，或使用 `deep-research-max-preview-04-2026` 进行最大详尽性。智能体需要 `background=True`。

### Python
```python
import time

interaction = client.interactions.create(
    agent="deep-research-preview-04-2026",
    input="研究 Google TPUs 的历史。",
    background=True
)
while True:
    interaction = client.interactions.get(interaction.id)
    if interaction.status == "completed":
        print(interaction.output_text)
        break
    elif interaction.status == "failed":
        print(f"Failed: {interaction.error}")
        break
    time.sleep(10)
```

### JavaScript/TypeScript
```typescript
import { GoogleGenAI } from "@google/genai";

const client = new GoogleGenAI({});

// 开始后台研究
const initialInteraction = await client.interactions.create({
    agent: "deep-research-preview-04-2026",
    input: "研究 Google TPUs 的历史。",
    background: true,
});

// 查询结果
while (true) {
    const interaction = await client.interactions.get(initialInteraction.id);
    if (interaction.status === "completed") {
        console.log(interaction.output_text);
        break;
    } else if (["failed", "cancelled"].includes(interaction.status)) {
        console.log(`Failed: ${interaction.status}`);
        break;
    }
    await new Promise(resolve => setTimeout(resolve, 10000));
}
```

高级功能：协作规划、原生可视化、MCP 集成、文件搜索、多模态输入。见 [Deep Research 文档](https://ai.google.dev/gemini-api/docs/interactions/deep-research.md.txt)。

## 管理智能体

管理智能体在由 Google 托管的沙盒化的 Linux 环境中运行。在编写智能体代码之前，请获取 [管理智能体快速入门](https://ai.google.dev/gemini-api/docs/managed-agents-quickstart.md.txt)。

### Antigravity 智能体

Antigravity 智能体（`antigravity-preview-05-2026`）是通用管理智能体。它可以执行代码（Bash、Python、Node.js）、管理文件、浏览网络和使用 Google 搜索。见 [Antigravity 智能体文档](https://ai.google.dev/gemini-api/docs/antigravity-agent.md.txt) 以获取功能、工具、多模态输入和定价。

#### Python
```python
from google import genai

client = genai.Client()

interaction = client.interactions.create(
    agent="antigravity-preview-05-2026",
    input="编写一个 Python 脚本，生成前 20 个斐波那契数并保存到 fibonacci.txt。然后读取文件并打印其内容。",
    environment="remote",
)

print(f"环境 ID: {interaction.environment_id}")
print(interaction.output_text)
```

#### JavaScript/TypeScript
```typescript
import { GoogleGenAI } from "@google/genai";

const client = new GoogleGenAI({});

const interaction = await client.interactions.create({
    agent: "antigravity-preview-05-2026",
    input: "编写一个 Python 脚本，生成前 20 个斐波那契数并保存到 fibonacci.txt。然后读取文件并打印其内容。",
    environment: "remote",
});

console.log(`环境 ID: {interaction.environment_id}`);
console.log(interaction.output_text);
```

### 自定义智能体

见 [构建自定义智能体文档](https://ai.google.dev/gemini-api/docs/custom-agents.md.txt)。

#### Python
```python
agent = client.agents.create(
    id="code-reviewer",
    base_agent="antigravity-preview-05-2026",
    system_instruction="您是一位高级代码审查员。检查每个文件中的错误、风格问题和安全漏洞。",
    base_environment={
        "type": "remote",
        "sources": [
            {
                "type": "repository",
                "source": "https://github.com/my-org/backend",
                "target": "/workspace/repo",
            }
        ],
    },
)

# 调用 — 每次调用都会分叉基础环境
result = client.interactions.create(
    agent="code-reviewer",
    input="审查 /workspace/repo/src 中的最新更改。",
    environment="remote"
)
print(result.output_text)
```

#### JavaScript/TypeScript
```typescript
const agent = await client.agents.create({
    id: "code-reviewer",
    base_agent="antigravity-preview-05-2026",
    system_instruction: "您是一位高级代码审查员。检查每个文件中的错误、风格问题和安全漏洞。",
    base_environment: {
        type: "remote",
        sources: [
            {
                type: "repository",
                source: "https://github.com/my-org/backend",
                target: "/workspace/repo",
            }
        ],
    },
});

const result = await client.interactions.create({
    agent: "code-reviewer",
    input: "审查 /workspace/repo/src 中的最新更改。",
    environment: "remote",
});
console.log(result.output_text);
```

使用 `client.agents.list()`、`client.agents.get(id=...)` 和 `client.agents.delete(id=...)` 管理智能体。

## 流式传输

设置 `stream=True` 以接收增量服务器发送的事件。每个流遵循：`interaction.created` → (`step.start` → `step.delta`(s) → `step.stop`)+ → `interaction.completed`。

### Python
```python
for event in client.interactions.create(
    model="gemini-3.7-flash",
    input="用简单的术语解释量子纠缠。",
    stream=True,
):
    if event.event_type == "step.delta":
        if event.delta.type == "text":
            print(event.delta.text, end="", flush=True)
    elif event.event_type == "interaction.completed":
        print(f"\n\n总令牌数: {event.interaction.usage.total_tokens}")
```

### JavaScript/TypeScript
```typescript
const stream = await client.interactions.create({
    model: "gemini-3.7-flash",
    input: "用简单的术语解释量子纠缠。",
    stream: true,
});
for await (const event of stream) {
    if (event.event_type === "step.delta") {
        if (event.delta.type === "text") {
            process.stdout.write(event.delta.text);
        }
    } else if (event.event_type === "interaction.completed") {
        console.log(`\n\n总令牌数: ${event.interaction.usage.total_tokens}`);
    }
}
```

对于带有工具、思考、智能体和图像生成的流式传输，请参阅完整的 [流式传输指南](https://ai.google.dev/gemini-api/docs/interactions/streaming.md.txt)。

## 文档页面

**您必须在编写代码之前获取匹配的页面。** 这些托管文档是参数、类型和边缘情况的权威来源 — 不要仅依赖上面的示例。

**核心文档：**
- [交互 API 概述](https://ai.google.dev/gemini-api/docs/interactions.md.txt)
- [快速入门](https://ai.google.dev/gemini-api/docs/interactions/quickstart.md.txt)
- [文本生成](https://ai.google.dev/gemini-api/docs/interactions/text-generation.md.txt)
- [流式传输](https://ai.google.dev/gemini-api/docs/interactions/streaming.md.txt)
- [令牌](https://ai.google.dev/gemini-api/docs/interactions/tokens.md.txt)
- [API 密钥](https://ai.google.dev/gemini-api/docs/interactions/api-key.md.txt)

**工具和函数调用：**
- [函数调用](https://ai.google.dev/gemini-api/docs/interactions/function-calling.md.txt)
- [Google 搜索](https://ai.google.dev/gemini-api/docs/interactions/google-search.md.txt)
- [代码执行](https://ai.google.dev/gemini-api/docs/interactions/code-execution.md.txt)
- [URL 上下文](https://ai.google.dev/gemini-api/docs/interactions/url-context.md.txt)
- [文件搜索](https://ai.google.dev/gemini-api/docs/interactions/file-search.md.txt)
- [工具组合](https://ai.google.dev/gemini-api/docs/interactions/tool-combination.md.txt)
- [计算机使用](https://ai.google.dev/gemini-api/docs/interactions/computer-use.md.txt)
- [地图接地](https://ai.google.dev/gemini-api/docs/interactions/maps-grounding.md.txt)

**生成和输出：**
- [结构化输出](https://ai.google.dev/gemini-api/docs/interactions/structured-output.md.txt)
- [思考](https://ai.google.dev/gemini-api/docs/interactions/thinking.md.txt)
- [思想签名](https://ai.google.dev/gemini-api/docs/interactions/thought-signatures.md.txt)
- [图像生成](https://ai.google.dev/gemini-api/docs/interactions/image-generation.md.txt)
- [图像理解](https://ai.google.dev/gemini-api/docs/interactions/image-understanding.md.txt)
- [视频生成和编辑（Omni Flash）](https://ai.google.dev/gemini-api/docs/omni.md.txt)
- [语音生成](https://ai.google.dev/gemini-api/docs/interactions/speech-generation.md.txt)
- [音乐生成](https://ai.google.dev/gemini-api/docs/interactions/music-generation.md.txt)
- [嵌入](https://ai.google.dev/gemini-api/docs/embeddings.md.txt)

**多模态理解：**
- [音频](https://ai.google.dev/gemini-api/docs/interactions/audio.md.txt)
- [音频转录](https://ai.google.dev/gemini-api/docs/transcribe.md.txt)
- [视频理解](https://ai.google.dev/gemini-api/docs/interactions/video-understanding.md.txt)
- [文档处理](https://ai.google.dev/gemini-api/docs/interactions/document-processing.md.txt)

**文件和上下文：**
- [文件](https://ai.google.dev/gemini-api/docs/interactions/files.md.txt)
- [文件输入方法](https://ai.google.dev/gemini-api/docs/interactions/file-input-methods.md.txt)
- [缓存](https://ai.google.dev/gemini-api/docs/interactions/caching.md.txt)
- [媒体分辨率](https://ai.google.dev/gemini-api/docs/interactions/media-resolution.md.txt)

**智能体：**
- [智能体概述](https://ai.google.dev/gemini-api/docs/agents.md.txt)
- [管理智能体快速入门](https://ai.google.dev/gemini-api/docs/managed-agents-quickstart.md.txt)
- [Antigravity 智能体](https://ai.google.dev/gemini-api/docs/antigravity-agent.md.txt)
- [智能体环境](https://ai.google.dev/gemini-api/docs/agent-environment.md.txt)
- [构建自定义智能体](https://ai.google.dev/gemini-api/docs/custom-agents.md.txt)
- [深度研究](https://ai.google.dev/gemini-api/docs/interactions/deep-research.md.txt)

**高级功能：**
- [最新模型（3.7 Flash & 3.5 Flash-Lite）](https://ai.google.dev/gemini-api/docs/latest-model.md.txt)
- [Flex 推理](https://ai.google.dev/gemini-api/docs/interactions/flex-inference.md.txt)
- [优先推理](https://ai.google.dev/gemini-api/docs/interactions/priority-inference.md.txt)

**API 参考：**
- [API 参考](https://ai.google.dev/static/api/interactions.md.txt)
- [OpenAPI Spec](https://ai.google.dev/static/api/interactions.openapi.json)
- [2026 年 5 月破坏性变更迁移指南](https://ai.google.dev/gemini-api/docs/interactions-breaking-changes-may-2026.md.txt)

## 数据模型

`Interaction` 响应包含 `steps`，一个表示交互回合结构化时间线的类型化步骤对象数组。

### 步骤类型

**用户步骤：**
- `user_input`：用户输入（文本、音频、多模态）。包含 `content` 数组。

**模型/服务器步骤：**
- `model_output`：最终模型生成。包含 `content` 数组，其中包含 `text`、`image`、`audio` 等。
- `thought`：模型推理/思维链。具有 `signature` 字段（必需）和可选的 `summary`。
- `function_call`：工具调用请求（`id`、`name`、`arguments`）。
- `function_result`：您发送回的工具结果（`call_id`、`name`、`result`）。
- `google_search_call` / `google_search_result`：Google 搜索工具步骤，可以有 `signature` 字段。
- `code_execution_call` / `code_execution_result`：代码执行工具步骤，可以有 `signature` 字段。
- `url_context_call` / `url_context_result`：URL 上下文工具步骤，可以有 `signature` 字段。
- `mcp_server_tool_call` / `mcp_server_tool_result`：远程 MCP 工具步骤。
- `file_search_call` / `file_search_result`：文件搜索工具步骤，可以有 `signature` 字段。

### 内容类型（在 `model_output` 和 `user_input` 步骤的 `content` 数组中）
- `text`：文本内容（`text` 字段）
- `image` / `audio` / `document` / `video`：具有 `data`、`mime_type` 或 `uri` 的内容

### 流式传输事件类型

| 事件 | 描述 |
|---|---|
| `interaction.created` | 交互创建；包含元数据。 |
| `interaction.status_update` | 交互级状态变更。 |
| `step.start` | 新步骤开始。包含步骤 `type` 和初始元数据。 |
| `step.delta` | 当前步骤的增量数据。包含一个类型的 `delta` 对象。 |
| `step.stop` | 步骤完成。包含 `index`。 |
| `interaction.completed` | 交互完成。包含最终的 `usage`。 |

### Delta 类型

| Delta 类型 | 父步骤 | 描述 |
|---|---|---|
| `text` | `model_output` | 增量文本令牌。 |
| `audio` | `model_output` | 音频块（base64）。 |
| `image` | `model_output` | 图像块（base64）。 |
| `thought_summary` | `thought` | 思考摘要文本。 |
| `thought_signature` | `thought` | 用于思想验证的不透明签名。 |

**状态值**：`completed`、`in_progress`、`requires_action`、`failed`、`cancelled`
