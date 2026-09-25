# ElevenLabs 代理平台

使用自然对话、多个 LLM 提供商、自定义工具和轻松的网页嵌入来构建语音 AI 代理。

> **设置**：有关 CLI 和 SDK 设置，请参阅 [安装指南](references/installation.md)。

## 使用 CLI 快速入门

ElevenLabs CLI 是创建和管理代理的推荐方式：

```bash
# 安装 CLI 并进行身份验证
npm install -g @elevenlabs/cli
elevenlabs auth login

# 初始化项目并创建代理
elevenlabs agents init
elevenlabs agents add "我的助手" --template complete

# 推送到 ElevenLabs 平台
elevenlabs agents push
```

**可用模板**：`complete`、`minimal`、`仅语音`、`仅文本`、`客户服务`、`助手`

### Python

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

agent = client.conversational_ai.agents.create(
    name="我的助手",
    conversation_config={
        "agent": {
            "first_message": "你好！我能帮什么忙？",
            "language": "en",
            "prompt": {
                "prompt": "你是一个有帮助的助手。简洁友好。",
                "llm": "gemini-2.0-flash",
                "temperature": 0.7
            }
        },
        "tts": {"voice_id": "JBFqnCBsd6RMkjVDRZzb"}
    }
)
```

### JavaScript

```javascript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
const client = new ElevenLabsClient();

const agent = await client.conversationalAi.agents.create({
  name: "我的助手",
  conversationConfig: {
    agent: {
      firstMessage: "你好！我能帮什么忙？",
      language: "en",
      prompt: {
        prompt: "你是一个有帮助的助手。",
        llm: "gemini-2.0-flash",
        temperature: 0.7
      }
    },
    tts: { voiceId: "JBFqnCBsd6RMkjVDRZzb" }
  }
});
```

### CLI

CLI 会自动从环境变量中读取 `ELEVENLABS_API_KEY`：

```bash
elevenlabs agents create \
  --json '{"name": "我的助手", "conversation_config": {"agent": {"first_message": "你好！", "language": "en", "prompt": {"prompt": "你是有帮助的.", "llm": "gemini-2.0-flash"}}, "tts": {"voice_id": "JBFqnCBsd6RMkjVDRZzb"}}}'
```

## 开始对话

**认证 WebRTC**：从你的后端请求会话令牌。响应包括令牌和对话 ID：

```python
session = client.conversational_ai.conversations.get_webrtc_token(
    agent_id="你的代理 ID",
)
print(session.token, session.conversation_id)
```

**服务器端（Python）**：获取客户端连接的签名 URL：

```python
signed_url = client.conversational_ai.conversations.get_signed_url(
    agent_id="你的代理 ID",
    environment="staging",
)
```

**客户端端（JavaScript）**：

```javascript
import { Conversation } from "@elevenlabs/client";

const conversation = await Conversation.startSession({
  agentId: "你的代理 ID",
  environment: "staging",
  overrides: { asr: { keywords: ["ElevenLabs", "TechCorp"] } },
  onMessage: (msg) => console.log("代理:", msg.message),
  onUserTranscript: (t) => console.log("用户:", t.message),
  onPing: (event) => console.log("估计延迟:", event.ping_ms),
  onContextUsage: ({ model, context_tokens, context_limit_tokens }) =>
    console.log(`${model}: ${context_tokens}/${context_limit_tokens} 上下文令牌`),
  onError: (e) => console.error(e)
});
```

**React Hook**：将 Hook 消费者包裹在 `ConversationProvider` 中。对于会话控制和 UI 状态，优先使用粒度 Hook，如 `useConversationControls` 和 `useConversationStatus`；`useConversation` 仍然可用作为便利的全功能 Hook。当你希望 React 在一个地方处理对话错误时，传递提供者级别的回调，如 `onError`。

```typescript
import {
  ConversationProvider,
  useConversationControls,
  useConversationStatus,
} from "@elevenlabs/react";

function Agent({ signedUrl }: { signedUrl: string }) {
  const { startSession, endSession } = useConversationControls();
  const { status } = useConversationStatus();

  if (status === "connected") {
    return <button onClick={endSession}>结束对话</button>;
  }

  return (
    <button onClick={() => startSession({ signedUrl })}>
      开始对话
    </button>
  );
}

function App({ signedUrl }: { signedUrl: string }) {
  return (
    <ConversationProvider
      onError={(error) => console.error("对话错误:", error)}
      onPing={(event) => console.log("估计延迟:", event.ping_ms)}
      onContextUsage={({ model, context_tokens, context_limit_tokens }) =>
        console.log(`${model}: ${context_tokens}/${context_limit_tokens} 上下文令牌`)
      }
    >
      <Agent signedUrl={signedUrl} />
    </ConversationProvider>
  );
}
```

## 配置

| 提供商 | 模型 |
|--------|------|
| OpenAI | `gpt-5.6-sol`、`gpt-5.6-terra`、`gpt-5.6-luna`、`gpt-5.5`、`gpt-5.5-2026-04-23`、`gpt-5.4`、`gpt-5.4-mini`、`gpt-5.4-nano`、`gpt-5.4-2026-03-05`、`gpt-5.4-mini-2026-03-17`、`gpt-5.4-nano-2026-03-17`、`gpt-5`、`gpt-5-mini`、`gpt-5-nano`、`gpt-4.1`、`gpt-4.1-mini`、`gpt-4.1-nano`、`gpt-4o`、`gpt-4o-mini`、`gpt-4-turbo` |
| Anthropic | `claude-opus-4-7`、`claude-sonnet-4-6`、`claude-sonnet-4-5`、`claude-sonnet-4`、`claude-haiku-4-5`、`claude-3-7-sonnet`、`claude-3-5-sonnet`、`claude-3-haiku` |
| Google | `gemini-3.7-flash`、`gemini-3.6-flash`、`gemini-3.1-flash-lite-preview`、`gemini-3.1-pro-preview`、`gemini-3-pro-preview`、`gemini-3-flash-preview`、`gemini-2.5-flash`、`gemini-2.5-flash-lite`、`gemini-2.0-flash`、`gemini-2.0-flash-lite` |
| ElevenLabs | `glm-45-air-fp8`、`qwen3-30b-a3b`、`qwen36-35b-a3b`、`qwen35-35b-a3b`、`qwen35-397b-a17b`、`gpt-oss-120b` |
| 自定义 | `custom-llm`（自带端点） |

使用 `GET /v1/convai/llm/list` 查看当前模型目录，包括弃用状态、令牌/上下文限制、图像输入支持等能力标志以及特定模型的推理工作支持。

**热门声音**：`JBFqnCBsd6RMkjVDRZzb`（乔治）、`EXAVITQu4vr4xnSDxMaL`（莎拉）、`onwK4e9ZLuTAKqWW03F9`（丹尼尔）、`XB0fDUnXU5powFXDhCwa`（夏洛特）

**反应积极性**：`patient`（等待用户完成）、`normal` 或 `eager`（快速响应）

有关所有选项，请参阅 [代理配置](references/agent-configuration.md)。

## 系统提示结构

使用 markdown 标题分隔提示——模型更可靠地优先处理和解释指令（[提示指南](https://elevenlabs.io/docs/eleven-agents/best-practices/prompting-guide)）：

```
# 个性   – 命名角色，2-3 个特征
# 环境   – 工作地点，交谈对象
# 语气   – 作为 4-5 个要点的语音风格
# 目标   – 成功看起来像什么（编号用于多步骤流程）
```

保持指令简短且基于动作。用 "这一步很重要" 标记关键步骤。对于关键拒绝/安全规则，在提示中包含简洁的指令，并通过 `platform_settings.guardrails` 配置独立的自定义 Guardrails（见 [Guardrails](#guardrails)）。

## 工具

使用 webhook、客户端或内置系统工具扩展代理。工具定义在 `conversation_config.agent.prompt` 内：

工作区环境变量可以解析每个环境的服务器工具 URL、标头和认证连接，而运行时系统变量（如 `{{system__conversation_history}}`）可以在需要时将完整对话上下文传递到工具调用中。

```python
"prompt": {
    "prompt": "你是一个有帮助的助手，可以查看天气。",
    "llm": "gemini-2.0-flash",
    "tools": [
        # Webhook：服务器端 API 调用
        {"type": "webhook", "name": "get_weather", "description": "获取天气",
         "api_schema": {"url": "https://api.example.com/weather", "method": "POST",
             "request_body_schema": {"type": "object", "properties": {"location": {"type": "string"}}, "required": ["location"]}}},
        # Client：在浏览器中运行
        {"type": "client", "name": "show_product", "description": "显示产品",
         "parameters": {"type": "object", "properties": {"productId": {"type": "string"}}, "required": ["productId"]}}
    ],
    "built_in_tools": {
        "end_call": {},
        "transfer_to_number": {"transfers": [{"transfer_destination": {"type": "phone", "phone_number": "+1234567890"}, "condition": "用户要求人工支持"}]},
        "start_procedure": {}
    }
}
```

**客户端工具** 在浏览器中运行：

```javascript
clientTools: {
  show_product: async ({ productId }) => {
    document.getElementById("product").src = `/products/${productId}`;
    return { success: true };
  }
}
```

有关完整文档，请参阅 [客户端工具参考](references/client-tools.md)。

### 内置系统工具

在 `conversation_config.agent.prompt.built_in_tools` 下设置。`{}` 启用默认值；提供 `description` 以自定义；省略以禁用。

| 工具 | 启用于 |
|------|--------|
| `end_call` | 所有代理 |
| `language_detection` | 多语言代理 |
| `transfer_to_number` | 基于电话的人工升级 |
| `transfer_to_agent` | 多代理工作流 |
| `start_procedure` | 过程引导对话（见 [Procedures](#procedures)） |
| `end_procedure` | 完成活动过程 |
| `skip_turn` | 辅导/指导（静默监听） |
| `voicemail_detection` | 外呼 |
| `play_keypad_touch_tone` | IVR 导航 |

`run_subagent` 是一个系统工具，用于将任务委托给另一个配置的代理。将其添加到 `conversation_config.agent.prompt.tools`，并使用 `params.system_tool_type: "run_subagent"` 和一个 `agents` 数组。每个条目需要 `agent_id` 和 `description`；`branch_id` 和一个 JSON-schema `parameters` 对象是可选的。

`knowledge_base` 是一个系统工具，允许模型选择如何检查附加的知识库。将其添加到 `conversation_config.agent.prompt.tools`，并使用 `type: "system"`、一个 `name` 和 `params.system_tool_type: "knowledge_base"`。使用 `enabled_strategies` 来暴露任何组合的 `cat`、`keyword`、`semantic` 和 `ls`：

```json
{
  "type": "system",
  "name": "knowledge_base",
  "description": "搜索附加的知识库。",
  "params": {
    "system_tool_type": "knowledge_base",
    "enabled_strategies": ["semantic", "keyword"]
  }
}
```

### 集成工具

由平台管理的预构建连接器。使用凭据创建连接，然后通过 `tool_ids` 附加：

| 集成 | 用例 |
|-------------|----------|
| `calcom` | 安排预约 |
| `salesforce` | CRM 查找、案例创建 |
| `hubspot` | CRM、营销、联系人 |
| `zendesk` | 支持工单 |

三步流程：`POST /v1/convai/api-integrations/{id}/connections` → `GET /v1/convai/api-integrations/{id}/tools` → `POST /v1/convai/tools` 使用 `api_integration_id` 和 `api_integration_connection_id`。通过 `"prompt": {"tool_ids": ["tool_xxxx"]}` 附加到代理。内联 `tools` 和 `tool_ids` 可以共存——优先使用集成而不是重复的自定义 webhook。

### 公共 API Webhook 示例

无认证 API 对原型很有用（URL 必须为 HTTPS）：

| 工具 | URL | 目的 |
|------|-----|---------|
| `get_weather` | `https://wttr.in/{location}?format=j1` | 当前天气 |
| `search_wikipedia` | `https://en.wikipedia.org/api/rest_v1/page/summary/{topic}` | 主题摘要 |
| `get_exchange_rate` | `https://open.er-api.com/v6/latest/{base_currency}` | 外汇汇率 |

## 工作流

通过离散步骤和分支逻辑路由对话。在代理的顶层 `workflow` 字段下定义。参考：[代理工作流](https://elevenlabs.io/docs/eleven-agents/customization/agent-workflows)。

**节点类型**：`start`（ID 必须为 `"start_node"`）、`end`、`override_agent`（子代理步骤，带有 `label` + `additional_prompt`）、`dispatch_tool`（执行工具并具有成功/失败路由）、`agent_transfer`、`transfer_to_number`。

**边类型**：`unconditional`、`llm`（自然语言条件）、`expression`（确定性数据检查）。工具节点有单独的成功/失败边。

**每步限制工具**：在节点上使用 `additional_tool_ids` — 防止在错误步骤触发错误的工具。在对话路由节点（如问候和 `classify_intent`）上设置 `additional_tool_ids: []` 以仅进行对话：

```json
{
  "type": "override_agent",
  "label": "预约",
  "additional_prompt": "讨论首选日期和医生。一旦同意，显示预约表单。",
  "entry_behavior": "wait_for_user",
  "additional_tool_ids": ["show_booking_form", "display_appointment_card"],
  "position": {"x": 0, "y": 400}
}
```

在每个节点上包含 `position` (`{x, y}`) 以使编辑器渲染干净。从 `y=0` 开始，将 `end` 放在底部，并在 `x=-150` 和 `x=150` 水平间隔分支；建议每级垂直间隔 200px，分支之间水平间隔 300px。保持工作流到 4-7 个节点，并且始终有一个路径到 `end`。

在 `override_agent` 节点上使用 `entry_behavior` 选择是否立即说话（`generate_immediately`）、等待用户输入（`wait_for_user`）或让平台决定（`auto`）。

对于嵌套代理转移，在 `standalone_agent` 节点上设置 `enable_nesting`，并在应将控制权返回到父工作流的 `end` 节点上设置 `return_when_nested`。

## 过程

可重用的指令块，代理在触发匹配时运行。过程是 `free_form`（代理适应的 markdown 指导，并且是唯一可以参考知识库文档的类型）或 `deterministic`（有序、类型化的步骤，用于必须始终一致运行的流程）。有关完整 CLI 和 SDK 流，请参阅 [使用过程 API](references/using-procedure-api.md)，有关触发和内容作者ing、步骤模式，请参阅 [编写过程](references/writing-procedures.md)。

过程存在于代理分支上，并且每个写入都会为每个用户创建一个草稿：

| 操作 | 调用 |
|-----------|------|
| 列表、创建、读取、更新、放弃、删除 | `/v1/convai/agents/{agent_id}/branches/{branch_id}/procedures...` (`procedures.*` 和 `procedures.drafts.*` 在 SDKs 中) |
| 编译 | `POST .../procedures/compile` (`procedures.compile`) |
| 发布 | `PATCH /v1/convai/agents/{agent_id}?branch_id=...` (`agents.update`) |

在编写任何这些调用之前，值得了解的语义：

- 除非你发布，否则不会到达实时代理。发布不是一个过程端点；对分支上每个更改的过程草稿进行一次 PATCH 在代理版本上。
- `GET .../procedures/{procedure_id}` 读取分支 HEAD 并在第一个发布之前返回 `404`。读取你刚刚创建的过程的 `/draft` 变体；不要重试创建。
- 仅当结构化（`deterministic`）过程更改时才编译。编译将它们转换为工作流节点，因此发布必须携带编译返回的工作流。仅更改 free-form 的过程发布，因为代理从已发布的版本加载 free-form 过程。
- 编译验证结构化内容，并且是检查它的唯一方法。在 `400` 它返回 `errors`，以过程 ID 为键，以冒犯字段 `path`；修复草稿并再次编译，而不是发布。
- 草稿更新将替换整个正文。首先读取草稿，然后重新发送 `name`、`type` 和新的 `content`。

`content` 是 `free_form` 过程的 markdown，对于 `deterministic` 过程是一个带有 `trigger` 和 `steps` 数组的 JSON 编码对象。序列化它；不要手动转义引号。
路由由 `trigger` 文本驱动，而不是过程名称。编写具体、非重叠的触发器，涵盖用户实际会说的方式。

为了限制单个对话中启动代理仅选择的过程，启用 `platform_settings.overrides.enable_procedure_ids_from_client`，然后将它们的 ID 作为 `procedure_ids` 传递在对话初始化数据中。空列表将禁用该启动代理的所有过程。
过程 API 需要 `elevenlabs`（Python）或 `@elevenlabs/elevenlabs-js` at `2.60.0` 或更新版本。

## Guardrails

独立于 LLM 运行的分层安全执行——配置在 `platform_settings.guardrails` 下，而不是在系统提示中。参考：[Guardrails](https://elevenlabs.io/docs/eleven-agents/best-practices/guardrails)。

```json
"platform_settings": {
  "guardrails": {
    "version": "1",
    "focus": {"is_enabled": true},
    "prompt_injection": {"is_enabled": true},
    "content": {"config": {"harassment": {"is_enabled": true, "threshold": 0.5}}},
    "custom": {
      "config": {
        "configs": [{
          "is_enabled": true,
          "name": "No medical diagnoses",
          "prompt": "阻止代理提供医疗诊断或治疗建议。",
          "execution_mode": "blocking",
          "model": "gemini-2.5-flash-lite",
          "history_message_count": 1,
          "trigger_action": {"type": "retry", "feedback": "Reason: {{trigger_reason}}"}
        }]
      }
    }
  }
}
```

**类型**：`focus`（主题）、`prompt_injection`（操纵防御）、`content`（类别过滤器）、`custom`（LLM-evaluated 领域规则）。内容类别包括 `harassment`、`profanity`、`sexual`、`violence`、`self_harm` 和 `medical_and_legal_information` — 阈值范围 `0.0`–`1.0`（默认 `0.3`）。自定义规则使用 `execution_mode: "blocking"` 与 `model`、`history_message_count` 和 `trigger_action`（例如，`retry` 带有反馈）。自定义 guardrails 并行评估并失败打开。

**每个垂直**：医疗保健/金融/法律 → 启用 `medical_and_legal_information`；教育/青年 → `sexual`/`violence`/`self_harm`/`profanity`；支持/销售 → `harassment`/`profanity`。所有代理都受益于 `focus` + `prompt_injection` + 2-4 自定义规则。

## 测试代理

通过 `POST /v1/convai/agent-testing/create`，然后通过 PATCH 在代理上附加。参考：[代理测试](https://elevenlabs.io/docs/eleven-agents/customization/agent-testing)。

| 类型 | 目的 |
|------|---------|
| `llm` | 场景测试——代理是否适当地响应消息？ |
| `tool` | 工具调用测试——正确的工具、正确的参数？ |
| `simulation` | 多轮流程，具有模拟用户角色 |

```json
// 工具调用测试（整个文档使用 snake_case；chat_history 角色是 "user" 或 "agent")
{
  "name": "带有正确医生和日期的书籍",
  "type": "tool",
  "chat_history": [
    {"role": "user", "message": "Dr. Smith on March 5 at 2pm", "time_in_call_secs": 10}
  ],
  "tool_call_parameters": {
    "referenced_tool": {"id": "show_booking_form", "type": "client"},
    "parameters": [
      {"path": "doctor_name", "eval": {"type": "llm", "description": "应参考 Dr. Smith"}},
      {"path": "date", "eval": {"type": "regex", "pattern": "2025-03-05|March 5"}}
    ]
  }
}
```

评估策略：`exact`、`regex`、`llm`。提示评估标准可以使用二进制评分或数值评分，使用 `scoring_mode: "numeric_uniform"`、`max_score` 和 `score_instructions`；数值分数被归一化为总对话成功百分比。通过代理更新附加：

```bash
elevenlabs agents update --agent-id "你的代理 ID" \
  --json '{"platform_settings": {"testing": {"attached_tests": [{"test_id": "test_xxxx"}]}}'
```

使用 `POST /v1/convai/agents/{agent_id}/run-tests` 运行选定测试。请求正文需要 `tests`，并接受 `repeat_count` 从 `1` 到 `50` 用于重复运行。模拟测试可以定义高达 30 个 `success_conditions` 提示；所有标准都被评估并合并到最终结果中。
模拟测试还可以定义 `tool_mock_overrides`，按工具 ID 键，以替换共享响应模拟。每个覆盖是一个包含所需 `mock_result` 的模拟数组；设置 `is_error: true` 以执行工具失败路径。覆盖仅适用于通过 `tool_mock_config` 启用模拟的工具。
对于完成的对话，使用 `POST /v1/convai/conversations/{conversation_id}/analysis/evaluations/run` 和包含 `evaluation_id` 的请求正文重新运行一个评估标准。

## 组件嵌入

```html
<elevenlabs-convai agent-id="你的代理 ID"></elevenlabs-convai>
<script src="https://unpkg.com/@elevenlabs/convai-widget-embed" async type="text/javascript"></script>
```

使用属性自定义：`avatar-image-url`, `action-text`, `start-call-text`, `end-call-text`。

有关所有选项，请参阅 [组件嵌入参考](references/widget-embedding.md)。

## 外呼

使用你的代理通过 Twilio 或 Exotel 集成进行外呼电话：

以下示例使用 Twilio。请参阅参考以了解 Exotel 使用情况。

### Python

```python
response = client.conversational_ai.twilio.outbound_call(
    agent_id="你的代理 ID",
    agent_phone_number_id="你的电话号码 ID",
    to_number="+1234567890",
    call_recording_enabled=True
)
print(f"Call initiated: {response.conversation_id}")
```

### JavaScript

```javascript
const response = await client.conversationalAi.twilio.outboundCall({
  agentId: "你的代理 ID",
  agentPhoneNumberId: "你的电话号码 ID",
  toNumber: "+1234567890",
  callRecordingEnabled: true,
});
```

### CLI

```bash
elevenlabs agents twilio outbound_call \
  --agent-id "你的代理 ID" \
  --agent-phone-number-id "你的电话号码 ID" \
  --to-number "+1234567890" \
  --call-recording-enabled true
```

请参阅 [外呼参考](references/outbound-calls.md) 以了解提供者特定的端点、配置覆盖和动态变量。

## 管理代理

### 使用 CLI（推荐）

```bash
# 列出代理并检查状态
elevenlabs agents list
elevenlabs agents status

# 从平台导入代理到本地配置
elevenlabs agents pull                      # 导入所有代理
elevenlabs agents pull --agent <agent-id>   # 导入特定代理

# 推送本地更改到平台
elevenlabs agents push              # 上传配置
elevenlabs agents push --dry-run    # 预览更改首先

# 添加工具
elevenlabs tools add-webhook "Weather API"
elevenlabs tools add-client "UI Tool"
```

### 项目结构

CLI 为管理代理创建项目结构：

```
your_project/
├── agents.json       # 代理定义
├── tools.json        # 工具配置
├── tests.json        # 测试配置
├── agent_configs/    # 单个代理配置
├── tool_configs/     # 单个工具配置
└── test_configs/     # 单个测试配置
```

### SDK 示例

```python
# 列出
agents = client.conversational_ai.agents.list()

# 获取
agent = client.conversational_ai.agents.get(agent_id="你的代理 ID")

# 更新（部分 - 仅包括要更改的字段）
client.conversational_ai.agents.update(agent_id="你的代理 ID", name="新名称")
client.conversational_ai.agents.update(agent_id="你的代理 ID",
    conversation_config={
        "agent": {"prompt": {"prompt": "新指令", "llm": "claude-sonnet-4"}}
    })

# 删除
client.conversational_ai.agents.delete(agent_id="你的代理 ID")
```

请参阅 [代理配置](references/agent-configuration.md) 以了解所有配置选项和 SDK 示例。

## 错误处理

```python
try:
    agent = client.conversational_ai.agents.create(...)
except Exception as e:
    print(f"API 错误: {e}")
```

常见错误：**401**（无效密钥）、**404**（未找到）、**422**（配置无效）、**429**（速率限制）

## 参考

- [安装指南](references/installation.md) - SDK 设置和迁移
- [代理配置](references/agent-configuration.md) - 所有配置选项和 CRUD 示例
- [客户端工具](references/client-tools.md) - webhook、客户端和系统工具
- [使用过程 API](references/using-procedure-api.md) - 过程 CLI 和 SDK 流，编译和发布
- [编写过程](references/writing-procedures.md) - 触发器和内容作者ing、步骤模式
- [组件嵌入](references/widget-embedding.md) - 网站集成
- [外呼](references/outbound-calls.md) - 电话集成
