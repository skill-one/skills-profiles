# Gemini 交互 API 技能

此技能提供了有关如何进行身份验证、连接和使用 Gemini 企业代理平台上的状态管理型、服务器管理的 **Gemini 交互 API** 的说明。

交互 API 是执行生成式 AI 代理对话、后台研究任务、多轮聊天和结构化多步骤工作流的现代推荐方法。

> [!IMPORTANT] **关键：统一 SDK、最新模型 & GEAP 目标** *
> **统一 SDK**：使用 Google Gen AI SDK (**`google-genai >= 2.3.0`** 用于 Python，**`@google/genai >= 2.3.0`** 用于 JS/TS)。SDK 版本 `>= 2.0.0` 是步骤模式激活的最低门槛，但 `>= 2.3.0` 是支持/推荐的最低门槛。像 `google-cloud-aiplatform`、`@google-cloud/vertexai` 和 `google-generativeai` 这样的遗留 SDK 对于交互来说严格不受支持。* *强制指令*：在解释客户端初始化或编写导入代码时，您**必须**明确声明/警告用户，像 `google-cloud-aiplatform` 或 `google-generativeai` 这样的遗留包对于交互来说严格不受支持。* **仅使用最新模型**：使用 `gemini-3.5-flash`（快速、均衡、多模态——推荐默认值）、`gemini-3.1-pro-preview`（复杂推理、编码、研究）或 `gemini-3.1-flash-lite`（成本效益高、高频轻量级任务）。参考
> [最新模型版本](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/migrate) 检查新更新。遗留模型 (`gemini-3-flash-preview`、`gemini-2.5-*`、`gemini-2.0-*`、`gemini-1.5-*`) 已弃用，并且不支持交互。* *强制指令*：在任何交互响应中，您**必须**警告用户，像 `gemini-2.5-*`、`gemini-2.0-*` 或 `gemini-1.5-*` 这样的遗留模型已弃用，并且不支持交互 API。* **GEAP 需要预配的代理（目前不支持直接基础模型调用）**：在 Gemini 企业代理平台 (GEAP) 上，通过交互 API 的直接/基础模型调用 (`model="..."`) **目前不受支持**。您**必须**使用 `agent="<AGENT_ID>"` 参数而不是 `model="..."` 来目标预配的代理或端点。由于此原因，本技能中的代码示例使用 `agent=...`。 (这是与
> [ai.google.dev](https://ai.google.dev/gemini-api/docs/interactions) 交互文档的主要区别，该文档使用 `model=...` — 虽然 `model=...` 对于其他 Gemini API 上下文是有效的，但在代理平台上**不受支持**。) 按照
> [代理平台文档](https://docs.cloud.google.com/gemini-enterprise-agent-platform) 预配代理，并将其 ID 作为 `agent` 传递。* **回合范围参数**：像 `tools`、`system_instruction` 和 `generation_config` 这样的参数是回合范围的。它们**必须**在每个交互请求中传递。

## 1. 身份验证

在运行任何代码之前，请确保您已使用应用默认凭证 (ADC) 进行身份验证，并已启用必要的 API。

1.  **登录**：
    
    ```bash
    gcloud auth application-default login
    ```
2.  **启用 API**（如果尚未启用）：
    
    ```bash
    gcloud services enable aiplatform.googleapis.com
    ```

---

## 2. 客户端初始化

您可以使用环境变量（推荐）或通过传递显式配置参数来初始化客户端。

### 选项 A：环境变量（推荐）

配置环境变量以让 SDK 自动解析设置：

```bash
export GOOGLE_GENAI_USE_ENTERPRISE=true
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="global"
```

#### Python

```python
from google import genai

# SDK 会自动获取环境变量
client = genai.Client()
```

#### TypeScript/JavaScript

```typescript
import { GoogleGenAI } from "@google/genai";

// SDK 会自动获取环境变量
const ai = new GoogleGenAI();
```

### 选项 B：显式内联参数

或者，直接在您的代码中传递配置值：

#### Python

```python
from google import genai
import google.auth

_, project_id = google.auth.default()
client = genai.Client(enterprise=True, project=project_id, location="global")
```

#### TypeScript/JavaScript

```typescript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({
    enterprise: {
        project: "your-project-id",
        location: "global"
    }
});
```

---

## 3. 核心交互 API 使用

### 快速入门（单回合）

提交单个提示并读取最终文本响应。在现代化模式下，输出内容是从 `steps` 列表中检索的。

#### Python

```python
interaction = client.interactions.create(
    agent="your-agent-id",  # GEAP: 目标预配的代理，而不是基础模型
    input="用一句话解释无服务器计算。"
)
# 使用输出文本的便捷访问器（来自尾随模型输出步骤的组合文本）
print(interaction.output_text)
```

#### TypeScript/JavaScript

```typescript
const interaction = await ai.interactions.create({
    agent: "your-agent-id", // GEAP: 目标预配的代理，而不是基础模型
    input: "用一句话解释无服务器计算。"
});
console.log(interaction.output_text);
```

---

### 状态管理对话（多回合）

交互默认是状态管理的。将对话状态存储在云端，并使用 `previous_interaction_id` 在后续回合中引用它。

#### Python

```python
# 回合 1：介绍自己
# 交互默认存储（store=True）；传递 store=False 以禁用服务器端保留（这也禁用了 previous_interaction_id 和后台执行）
turn1 = client.interactions.create(
    agent="your-agent-id",
    input="嗨！我叫 John。我正在从事 AI 代理的工作。",
    store=True
)
print(f"回合 1: {turn1.output_text}")

# 回合 2：回溯存储的回合状态
turn2 = client.interactions.create(
    agent="your-agent-id",
    input="我的名字是什么？",
    previous_interaction_id=turn1.id
)
print(f"回合 2: {turn2.output_text}")
```

#### TypeScript/JavaScript

```typescript
// 回合 1（交互默认存储；传递 store: false 以禁用）
const turn1 = await ai.interactions.create({
    agent: "your-agent-id",
    input: "嗨！我叫 John。我正在从事 AI 代理的工作。",
    store: true
});

// 回合 2
const turn2 = await ai.interactions.create({
    agent: "your-agent-id",
    input: "我的名字是什么？",
    previousInteractionId: turn1.id
});
console.log(turn2.output_text);
```

---

### 实时流式传输

实时流式传输响应。传递 `stream=True` 会返回一个可迭代的块生成器。

#### Python

```python
# 流生成的是类型化的事件，而不是完整的交互快照。顺序是：
# interaction.created -> (step.start -> step.delta(s) -> step.stop)+ -> interaction.completed
for event in client.interactions.create(
    agent="your-agent-id",
    input="写一首关于调试的短诗。",
    stream=True
):
    if event.event_type == "step.delta":
        if event.delta.type == "text":
            print(event.delta.text, end="", flush=True)
    elif event.event_type == "interaction.completed":
        print()
```

#### TypeScript/JavaScript

```typescript
// 流生成的是类型化的事件，而不是完整的交互快照。顺序是：
// interaction.created -> (step.start -> step.delta(s) -> step.stop)+ -> interaction.completed
const responseStream = await ai.interactions.create({
    agent: "your-agent-id",
    input: "写一首关于调试的短诗。",
    stream: true
});

for await (const event of responseStream) {
    if (event.event_type === "step.delta") {
        if (event.delta.type === "text") {
            process.stdout.write(event.delta.text);
        }
    } else if (event.event_type === "interaction.completed") {
        console.log();
    }
}
```

---

### 结构化输出（Pydantic / 多态 `response_format`）

检索匹配架构的结构化、类型安全的 JSON。在现代化交互 API 下，多态 `response_format` 参数直接采用目标架构结构。

#### Python

```python
from pydantic import BaseModel, Field

class Book(BaseModel):
    title: str = Field(description="书的标题")
    author: str = Field(description="书的作者")
    year_published: int

interaction = client.interactions.create(
    agent="your-agent-id",
    input="推荐一本著名的科幻书。",
    response_format=Book
)

# 文本将是匹配 Book 架构的有效 JSON
print(interaction.output_text)
```

#### TypeScript/JavaScript

```typescript
import { Type } from "@google/genai";

const BookSchema = {
    type: Type.OBJECT,
    properties: {
        title: { type: Type.STRING, description: "书的标题" },
        author: { type: Type.STRING, description: "书的作者" },
        yearPublished: { type: Type.INTEGER }
    },
    required: ["title", "author", "yearPublished"]
};

const interaction = await ai.interactions.create({
    agent: "your-agent-id",
    input: "推荐一本著名的科幻书。",
    responseFormat: BookSchema
});

console.log(interaction.output_text);
```

---

### 函数调用（代理工具使用）

定义本地工具（函数）并将执行结果提交到状态管理交互历史记录。

#### Python

```python
import json

def get_stock_price(ticker: str) -> float:
    """获取给定股票代码的股票价格。"""
    if ticker.upper() == "GOOG":
        return 175.50
    return 100.0

# 回合 1：向模型传递工具
interaction = client.interactions.create(
    agent="your-agent-id",
    input="GOOG 的股票价格是多少？",
    tools=[get_stock_price]
)

# 在扁平化步骤架构中，工具请求是一个顶层步骤，类型为
# "function_call"，具有扁平的 `name` 和 `arguments` 字段（没有嵌套的 `tool_calls` 列表）。
for step in interaction.steps:
    if step.type == "function_call" and step.name == "get_stock_price":
        ticker_arg = step.arguments.get("ticker")
        price = get_stock_price(ticker_arg)

        # 回合 2：将结果作为函数结果步骤提交回来。通过 call_id=step.id 引用原始调用，并再次传递工具（回合范围）。
        final_turn = client.interactions.create(
            agent="your-agent-id",
            input=[
                {
                    "type": "function_result",
                    "name": step.name,
                    "call_id": step.id,
                    "result": [{"type": "text", "text": json.dumps(price)}],
                }
            ],
            tools=[get_stock_price],
            previous_interaction_id=interaction.id
        )
        print(final_turn.output_text)
```

#### TypeScript/JavaScript

```typescript
import { Type } from "@google/genai";

// 定义本地工具
function getStockPrice({ ticker }: { ticker: string }): number {
    if (ticker.toUpperCase() === "GOOG") {
        return 175.50;
    }
    return 100.00;
}

// 回合 1：向模型传递工具
const toolDeclaration = {
    functionDeclarations: [{
        name: "getStockPrice",
        description: "获取给定股票代码的股票价格。",
        parameters: {
            type: Type.OBJECT,
            properties: {
                ticker: { type: Type.STRING, description: "股票代码" }
            },
            required: ["ticker"]
        }
    }]
};

const interaction = await ai.interactions.create({
    agent: "your-agent-id",
    input: "GOOG 的股票价格是多少？",
    tools: [toolDeclaration]
});

// 在扁平化步骤架构中，工具请求是一个顶层步骤，类型为
// "function_call"，具有扁平的 `name` 和 `arguments` 字段（没有嵌套的 toolCalls）。
const fcStep = interaction.steps.find(s => s.type === "function_call");
if (fcStep && fcStep.name === "getStockPrice") {
    const tickerArg = fcStep.arguments.ticker as string;
    const price = getStockPrice({ ticker: tickerArg });

    // 回合 2：将结果作为函数结果步骤提交回来。通过 call_id=fcStep.id 引用原始调用，并再次传递工具（回合范围）。
    const finalTurn = await ai.interactions.create({
        agent: "your-agent-id",
        input: [{
            type: "function_result",
            name: fcStep.name,
            call_id: fcStep.id,
            result: [{ type: "text", text: JSON.stringify(price) }]
        }],
        tools: [toolDeclaration],
        previousInteractionId: interaction.id
    });
    console.log(finalTurn.output_text);
}
```

---

## 4. 通过 REST 访问交互 API

对于基于 shell 的脚本、调试或非 Python/JS 环境，您可以使用 `curl` 直接使用原始 HTTP/REST 请求与状态管理交互 API 进行通信。

### 1. REST 端点

交互的 REST API 端点是：

```http
POST https://aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/interactions
```

*   **LOCATION**：使用 `global`（如果需要，可以使用自定义区域）。
*   **PROJECT_ID**：您的 Google Cloud 项目 ID。

### 2. 设置变量和身份验证标头

设置您的目标代理 ID（例如模型或自定义代理路径）以及从应用默认凭证生成的访问令牌：

```bash
AGENT_ID="your-agent-id"
ACCESS_TOKEN=$(gcloud auth print-access-token)
```

### 3. 单回合交互负载

使用代理变量发送请求以启动交互：

```bash
curl -X POST "https://aiplatform.googleapis.com/v1beta1/projects/${PROJECT_ID}/locations/global/interactions" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "'"${AGENT_ID}"'",
    "input": [{
      "type": "user_input",
      "content": [{
        "type": "text",
        "text": "用一句话解释无服务器计算。"
      }]
    }]
  }'
```

#### 响应示例
同步 POST 请求返回一个包含对话步骤详情和唯一标识符的 JSON 对象：

```json
{
  "id": "your-interaction-id",
  "status": "completed",
  "steps": [
    {
      "type": "model_output",
      "content": [
        {
          "type": "text",
          "text": "无服务器计算是一种云执行模型，云提供商动态管理服务器的分配和配置，根据实际使用情况而不是预购容量向客户收费。"
        }
      ]
    }
  ],
  "usage": {
    "total_tokens": 24751,
    "total_input_tokens": 23894,
    "total_output_tokens": 857
  },
  "created": "2026-05-08T10:44:43Z",
  "updated": "2026-05-08T10:44:43Z",
  "environment_id": "your-environment-id",
  "object": "interaction"
}
```

### 4. 状态管理多回合交互负载

要状态管理地继续现有对话，请在 JSON 负载中指定 `previous_interaction_id`：

```bash
curl -X POST "https://aiplatform.googleapis.com/v1beta1/projects/${PROJECT_ID}/locations/global/interactions" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "'"${AGENT_ID}"'",
    "store": true,
    "previous_interaction_id": "YOUR_PREVIOUS_INTERACTION_ID",
    "input": [{
      "type": "user_input",
      "content": [{
        "type": "text",
        "text": "可以详细说明一下吗？"
      }]
    }]
  }'
```

### 5. 流式输出负载
要实时流式传输更新（服务器发送事件格式），在负载中传递 `"stream": true`：

```bash
curl -X POST "https://aiplatform.googleapis.com/v1beta1/projects/${PROJECT_ID}/locations/global/interactions" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "'"${AGENT_ID}"'",
    "stream": true,
    "input": [{
      "type": "user_input",
      "content": [{
        "type": "text",
        "text": "写一个关于太空旅行的长故事。"
      }]
    }]
  }'
```

端点将返回一个分块流，其中每个事件以 `data: ` 开头，包含包含 `event_type` 和步骤内容的 JSON 更新。

> **`curl` 如何处理流式传输**：
> 默认情况下，当 `"stream": true` 被传递时，服务器会响应 `Transfer-Encoding: chunked` 和 `Content-Type: text/event-stream`（服务器发送事件）。`curl` 将自动保持连接打开，并将来自服务器的传入数据块实时打印到 `stdout`，就像它们被服务器推送一样。用户不需要轮询或拉取进一步的内容；事件序列会持续流式传输，直到完成。

--------------------------------------------------------------------------------

## 5. 数据模型 & 步骤类型参考

`Interaction` 响应包含 `steps`，一个表示交互回合结构化时间线的类型化步骤对象数组。读取当前步骤的 `type` 而不是假设最后一步是文本——尾随步骤可能是 `function_call` 或 `thought`。

### 步骤类型

**用户步骤：**

*   `user_input`：用户输入（文本、音频、多模态）。包含一个 `content` 数组。（这就是为什么 REST 输入负载使用 `"type": "user_input"`，**不是**
*   `"role": "user"`。）

**模型/服务器步骤：**

*   `model_output`：最终模型生成。包含一个 `content` 数组，其中包含 `text`、`image`、`audio` 等。（REST 响应使用 `"type": "model_output"`，**不是**
*   `"role": "model"`。）
*   `thought`：模型推理/思维链。有一个 `signature` 字段和可选的 `summary`。
*   `function_call`：工具调用请求，具有扁平的 `id`、`name` 和 `arguments` 字段（**没有**嵌套的 `tool_calls` 列表）。
*   `function_result`：您发送回的工具结果，具有 `call_id`、`name` 和 `result` 字段。
*   `google_search_call` / `google_search_result`，`code_execution_call` /
    `code_execution_result`，`url_context_call` / `url_context_result`，
    `mcp_server_tool_call` / `mcp_server_tool_result`，`file_search_call` /
    `file_search_result`：内置和远程工具步骤。

### 内容类型（在 `model_output` 和 `user_input` 步骤的 `content` 数组中）

*   `text`：文本内容（`text` 字段）。
*   `image` / `audio` / `document` / `video`：具有 `data`、`mime_type` 或 `uri` 的内容。

### 便捷访问器

*   `output_text`：来自尾随 `model_output` 步骤的组合文本。优先于此，而不是手动遍历 `steps[-1].content[0].text`，这在最后一步是工具调用或 `thought` 时会失效。

### 流式事件类型

| 事件                   | 描述                                       |
| ----------------------- | ------------------------------------------------- |
| `interaction.created`   | 交互创建；包含元数据。           |
| `step.start`            | 一个新步骤开始。包含步骤 `type` 和   |
:                         : 初始元数据。                                 :
| `step.delta`            | 当前步骤的增量数据。包含一个       |
:                         : 类型化的 `delta` 对象（例如 `delta.type == "text"` :
:                         : 与 `delta.text`）。                               :
| `step.stop`             | 步骤完成。包含 `index`。           |
| `interaction.completed` | 交互完成。包含最终 `usage`。     |

### 存储 & 保留

交互默认存储（`store=True`），这启用了状态管理功能，如 `previous_interaction_id` 和后台执行。传递 `store=False` 会禁用服务器端保留，因此也禁用了 `previous_interaction_id` 和 `background`——在这种模式下，您必须在每个回合的 `input` 中传递完整的对话历史记录。
