---
name: agent-platform-inference
description: 连接到 Google Cloud Agent Platform GenAI 模型并进行推理，包括第一方 Gemini 模型和第三方 OpenMaaS 模型（如 Llama、DeepSeek、Qwen 等）。在需要执行推理、向模型提问、运行测试提示、执行聊天补全或为调用 Gemini 或 OpenMaaS 模型生成代码时使用。通过 GenAI SDK、OpenAI SDK 或传统 Agent Platform SDK 进行身份验证，配置基础 URL 和全球/区域端点，或排查 429 资源耗尽（DSQ）、400 用户验证失败或 404 未找到错误。不用于将模型部署到端点或运行模型评估。
---

# Agent Platform GenAI 推理技能

此技能提供有关如何认证并连接到 Google Cloud Agent Platform 以使用生成式 AI 模型的说明。它涵盖：

*   **第一方发布者模型**（Gemini）— 第 2 节。
*   **第三方发布者模型**（OpenMaaS：Llama、DeepSeek、Qwen 等）— 第 3 节。
*   **自定义端点**（任何位于数字 `projects/.../endpoints/<id>` 资源上的模型 — 调整后的 Gemini 模型、从 Model Garden 通过 `agent-platform-deploy` 技能自部署的 OSS LLM，以及遗留自定义模型）— 第 4 节。

## 安全性与确认级别（关键）

在代表用户执行任何命令或脚本之前，您必须根据请求的操作遵守以下安全级别。（该技能是只读的；其他安全级别被省略）：

1.  **级别 R：只读/推理 (`client.models.generate_content`、`client.chat.completions.create`、`client.completions.create`、`client.embeddings.create`)**
    *   在代表用户执行模型推理之前，需要**交互式确认**，并提供“是”/“否”选项，以防止意外的成本或配额消耗。
    *   **确认卡中必需的字段**：确认提示必须清楚地解释建议的推理执行，并明确列出以下所有参数：
        *   **项目 ID**：Google Cloud 项目 ID 或编号（例如 `123456789012`、`my-project`）。
        *   **区域/位置**：目标区域（例如 `us-central1`、`global`）。
        *   **模型 ID**：确切的模型 ID（例如 `gemini-2.5-flash`、`deepseek-ai/deepseek-v3.2-maas`）。
        *   **SDK**：选择的 SDK（例如 `Google GenAI SDK (google-genai)`、`OpenAI SDK`）。
        *   **输入提示**（或**输入图像**/**输入媒体**）：提示文本或媒体 URI。
        *   如果指定了任何其他生成参数（例如 `max_output_tokens`、`response_schema`）。
        自然语言的改述而未明确列出这些参数是不充分的。
    *   **同轮限制**：不要在同一轮次中执行推理脚本或命令，而是在显示确认提示时停止并等待用户的回复；只有在明确的“是”/批准后才能执行。
    *   **黄金标准示例**：
        > 我将使用以下参数执行模型推理。请在我继续之前确认这些信息：
        > * **项目 ID**：`my-project`
        > * **区域**：`us-central1`
        > * **模型 ID**：`gemini-2.5-pro`
        > * **SDK**：Google GenAI SDK (`google-genai`)
        > * **输入提示**： "用 3 句话总结《哈姆雷特》的剧情"
        >
        > 您确认吗？[是/否]

    *   **执行后响应基础（关键）**：
        在收到明确的用户批准并通过 SDK 执行推理调用后，返回的生成文本**必须**在模型输出旁边明确确认执行参数。永远不要单独返回一个裸模型响应。始终包括：
        *   **模型 ID**：使用的确切模型 ID（例如 `gemini-2.5-pro` 或 `<MODEL_ID>`）。
        *   **SDK**：使用的 SDK（例如 `Google GenAI SDK (google-genai)` 或 `OpenAI SDK`）。
        *   **项目 ID**：使用的 Google Cloud 项目/编号。
        *   **区域**：使用的区域或端点位置（例如 `global` 或 `us-central1`）。
        *   **生成输出**：模型的完整生成答案。

## 第 0 阶段：环境设置

**关键**：在运行 `scripts/` 目录中的任何 Python 示例脚本（例如 `scripts/openmaas_openai_sdk.py`）之前，您必须通过以下步骤确保环境正确初始化：

1.  **Google Cloud 认证**：使用您的 Google Cloud 凭据进行认证，并为 Agent Platform 访问配置活动的应用默认凭证 (ADC)：

    ```bash
    gcloud auth login
    gcloud auth application-default login
    ```

2.  **启用 API**（如果尚未启用）：

    ```bash
    gcloud services enable aiplatform.googleapis.com
    ```

3.  **Python 依赖项**：脚本导入 `vertexai`（来自 `google-cloud-aiplatform`）、`google-genai` 和 `openai`。**不要**创建虚拟环境——它为空并隐藏环境已经提供的包，强制进行冗余安装。探测并仅安装缺少的内容：

    ```bash
    python3 -c "import vertexai, google.genai, openai" \
      || pip install -r scripts/requirements.txt
    ```

    `scripts/requirements.txt` 是一个后备，用于环境不提供这些 SDK 的情况；不要在正常工作的环境中安装它。

4.  **验证设置（可选）**：运行所有示例脚本以验证环境端到端是否正常工作：

    ```bash
    ./scripts/verify_all.sh
    ```

5.  **执行**：使用 `python3 scripts/...` 运行脚本。没有需要首先激活的环境。

> [!IMPORTANT] **关键：模型 ID & 可用性** * **Gemini 模型**：请参阅 [Gemini 模型][gemini-models-docs] 获取有效的模型 ID 和区域。 * **OpenMaaS 模型**：请参阅 [在 Agent Platform 上使用 Open 模型](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/maas/use-open-models) 获取 Llama、DeepSeek、Qwen 等。 * **不完整列表**：此技能中列出的模型 ID 是**示例**，可能不完整或已过时。 * **操作**：在使用代码之前，始终使用上面的链接验证模型 ID 和区域。

## 参数基础与澄清协议（关键）

在准备代码或显示级别 R 确认卡之前，您必须确保所有必要参数都已基础化：

1.  **缺少模型 ID、模型系列或 SDK（关键）**：
    *   如果用户**未**指定要使用哪个模型或模型系列（例如，“运行一个测试提示”、“询问生成式 AI 模型...”、“询问 DeepSeek 一个问题”而未指定模型版本），或未指定 SDK 偏好：
    *   **永远不要猜测、主动提供或默认使用模型**（例如 `gemini-2.5-flash`、`gemini-2.5-pro` 或 `deepseek-v3.2-maas`）。
        在未询问的情况下在确认卡中提议默认模型违反了参数基础。
    *   **您必须停止并询问用户**：“您想使用哪个模型（或模型系列，例如 Gemini、Llama、DeepSeek 或 Qwen）和 SDK 偏好（例如 Google GenAI SDK 或 OpenAI SDK）？” 并询问目标区域和项目 ID（如果未指定）。
    *   只有在用户指定了模型（以及任何缺少的 SDK 偏好）后，您才能继续准备执行并显示级别 R 确认提示。

2.  **缺少项目 ID 或区域**：
    *   如果用户的项目 ID 或区域未在提示或对话上下文中指定，**询问**用户项目 ID 和区域（例如，“您想使用哪个项目 ID 和区域？”）。不要默默假设项目或区域。
    *   **OpenMaaS 位置**：OpenMaaS 发布者模型托管在 `global`（例如 `deepseek-ai/deepseek-v3.2-maas`、`meta/llama-3.3-70b-instruct-maas`）或区域端点（例如 `us-central1`（例如 `deepseek-ai/deepseek-r1-0528-maas`））。
        在为 OpenMaaS 模型配置推理时，使用适当的端点：

        *   全球：`https://aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/global/endpoints/openapi`
        *   区域：`https://{REGION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{REGION}/endpoints/openapi`

        并在确认卡和最终响应中明确反映区域。

3.  **SDK 选择**：
    *   如果用户指定了模型但未指定 SDK，请使用该模型系列的优先 SDK（Gemini 的 GenAI SDK `google-genai`，OpenMaaS 的 OpenAI SDK `openai`）。

4.  **通过 Python 进行沙盒执行（关键）**：
    *   在沙盒中执行模型推理时，通过 `run_command` **始终**使用官方 SDK 运行 Python 代码（例如，使用 `google-genai`、`openai` 或 `vertexai` 编写和运行 Python 脚本）。
    *   不要使用原始 curl 命令进行最终推理执行。

## 工作流决策树

1.  **指定了模型吗？**
    *   **否**（用户省略了模型名称/系列）-> **询问用户**他们想使用哪个模型或模型系列、目标区域和 SDK 偏好。
    *   **不明确**（例如，用户说“DeepSeek”或“Llama”而未指定版本）-> **询问用户**他们更喜欢哪个特定模型版本（例如 `deepseek-ai/deepseek-r1-0528-maas`、`deepseek-ai/deepseek-v3.2-maas`、`meta/llama-3.3-70b-instruct-maas`）。
    *   **是** -> 继续步骤 2。

2.  **模型系列 & SDK 选择**：
    *   **Gemini**（例如 `gemini-2.5-pro`、`gemini-3-flash-preview`）-> 优先：**GenAI SDK** (`google-genai`)。继续到 [1. Gemini 模型]。
    *   **OpenMaaS**（例如 `deepseek-ai/*`、`meta/llama-*`、`qwen/*`）-> 优先：**OpenAI SDK** (`openai`)。继续到 [2. OpenMaaS 模型]。
    *   **自定义端点**（数字端点 ID `projects/.../endpoints/<id>`）-> 继续到 [4. 自定义端点]。

3.  **故障排除**：用户是否报告了错误（429 资源耗尽、400 用户验证、404 未找到、由于 token 限制的空响应等）？
    *   **是** -> 继续到 [5. 故障排除 & 常见错误代码]。
    *   **否** -> 显示级别 R 确认提示，包含所有必需字段（项目 ID、区域、模型 ID、SDK、输入提示），等待用户确认，然后通过 Python SDK 执行。

## 0.5 发布者端点的区域可用性检查（Gemini + LoRA 基础）

> [!NOTE] 如果以下任一情况适用，**跳过此部分**：

>
> - 用户正在调用自定义端点（§4）—— 在数字 `projects/.../endpoints/<id>` 资源上托管的调整后的 Gemini 模型、从 Model Garden 通过 `agent-platform-deploy` 技能自部署的 OSS LLM（Llama、DeepSeek、Qwen、Gemma 等）或遗留自定义模型。这些请求命中特定端点资源，其区域在部署时固定；如果调用方侧区域不匹配，端点查找将返回干净的 404，而不会产生推理成本。转到 §4。
> - 用户正在调用 OpenMaaS 发布者模型（§2）—— Llama、DeepSeek、Qwen 等，通过全局 `openapi` 基础 URL 提供。这些在相同方式下没有与第一方 Gemini 相同的区域可用性限制。转到 §2。
>
> **仅当用户正在调用第一方管理的 Gemini 模型 (`gemini-*`，通过 §1）时应用此部分，包括在 Gemini 顶部上的微调 LoRA 适配器 — 这些通过发布者端点路由，其区域可用性实际上会变化。**

在响应任何指定了第一方管理 Gemini 模型 (`gemini-*`) 或微调 Gemini LoRA 适配器（通过数字端点 ID + 用户声明的基模型）的推理请求之前，您**必须**通过实时 API 调用验证模型实际上在该区域可用。不要依赖 Google 搜索、训练语料库知识或发布者文档来声明可用性 — 区域可用性会频繁变化，基础文本可能过时或错误。

仅探测用户询问的确切模型和区域。不要作为“控制”探测其他模型 — 您无法从模型 B 的状态推断出模型 A 的可用性，因为不同的模型本身可能由于其他原因在该参考区域不可用。

对于第一方 Gemini 模型，使用真实的 `:generateContent` 调用并使用最小的有效负载进行探测：

```bash
curl -sS -o /dev/null -w "%{http_code}\n" \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json" \
    "https://${LOCATION_ID}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION_ID}/publishers/google/${MODEL_ID}:generateContent" \
    -d "{\"contents\":{\"role\":\"user\",\"parts\":{\"text\":\"${PROBE_TEXT:-hi}\"}}}"
```

对于针对微调 Gemini LoRA 适配器的推理，使用相同的 `:generateContent` 调用，将 `${MODEL_ID}` 设置为基模型（例如，如果适配器是在 `gemini-2.5-flash` 上微调的，则为 `gemini-2.5-flash`）。LoRA 适配器在其基模型不可用的区域无法服务。

解释探测结果并采取行动：

-   **200** — 模型在该区域可用。继续 §1 中的 SDK 设置。
-   **404** — 模型在该区域不可用。停止。明确告诉用户该模型不在此区域提供，并列出其可用的区域（从 [Gemini 模型][gemini-models-docs] 或 `gcloud ai model-garden models list --filter="name~$MODEL_NAME"` 获取，不带 `--region`）。不要默默切换区域。不要为不受支持的区域编写推理代码或 SDK 初始化。不要运行额外的“控制”探测以双重检查 404 — 目标区域探测是权威的。
-   **任何其他结果**（权限拒绝、配额、临时故障等）— 不要断定模型可用或不可用。用 plain language 解释根本原因（例如，“您的帐户没有访问此项目的 Vertex AI API 权限 — 在控制台中启用它或切换项目”），并说明具体的下一步操作。

## 1. Gemini 模型

对于 Gemini 模型（例如 `gemini-2.5-pro`、`gemini-3-flash-preview`），**GenAI SDK** (`google-genai`) 是**首选**方法。遗留 `vertexai` SDK 仍然受支持，但建议新项目使用 GenAI SDK。

> [!IMPORTANT]
> **预览模型**（包括 Gemini 3.1）通常**仅在** `global` 区域可用。稳定模型在 `us-central1` 和其他区域可用。

### 选择正确的 SDK

*   **Gemini 模型**：**GenAI SDK** (`google-genai`) 是**首选**。为兼容性使用 OpenAI SDK，或如果需要，使用遗留 SDK (`vertexai`)。

### 安装

```bash
pip install google-genai
```

### Python 示例（GenAI SDK - 首选）

有关完整代码，请参阅 [`scripts/gemini_genai_sdk.py`](scripts/gemini_genai_sdk.py)。

### 替代方案：OpenAI SDK（聊天完成）

使用标准的 OpenAI SDK 与 Agent Platform 端点。这对于跨兼容性很棒。

有关完整代码，请参阅 [`scripts/gemini_openai_sdk.py`](scripts/gemini_openai_sdk.py)。

### 遗留方案：Agent Platform SDK

遗留 `vertexai` SDK 仍然广泛使用，但 `google-genai` 是新 Gemini 项目的首选。

有关完整代码，请参阅 [`scripts/gemini_vertexai_sdk.py`](scripts/gemini_vertexai_sdk.py)。

**文档**：
[Google GenAI SDK](https://github.com/googleapis/python-genai)

**文档**：
[Agent Platform Gemini 模型](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/google-models)

## 2. OpenMaaS 模型（Llama、DeepSeek、Qwen 等）

对于 OpenMaaS（模型即服务）模型，**强烈推荐**的方法是使用标准的 **OpenAI SDK** 和特定的 Vertex AI 端点。

> [!WARNING] 虽然 `GenerativeModel` *可以* 支持一些 OpenMaaS 模型，但**不鼓励**使用。使用 OpenAI SDK 以获得最佳兼容性（尤其是对于聊天完成）。

### 安装

```bash
pip install openai google-auth
```

### OpenAI SDK 的认证

你必须使用 Google Cloud OAuth 访问令牌作为 OpenAI SDK 的 API 密钥。

```python
import subprocess

def get_gcp_access_token():
    return subprocess.check_output(
        ["gcloud", "auth", "print-access-token"]
    ).decode("utf-8").strip()
```

> [!NOTE] Google Cloud 访问令牌通常在 1 小时后过期。上述 `get_gcp_access_token()` 函数在调用时获取一个*新的*令牌。对于长时间运行的应用程序，你需要实现刷新机制。有关详细信息，请参阅[刷新访问令牌](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/migrate/openai/auth-and-credentials?hl=en#refresh_your_credentials)。

### 配置（基本 URL）

-   **全局终端点**（推荐用于大多数需要全局可用性的模型）：
    `https://aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/global/endpoints/openapi`
-   **区域终端点**：
    `https://{REGION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{REGION}/endpoints/openapi`

### Python 示例（OpenMaaS - Chat Completions）

请参阅 [`scripts/openmaas_openai_sdk.py`](scripts/openmaas_openai_sdk.py) 获取完整代码。

> [!TIP] **替代方案：环境变量** 你可以在 shell 中设置环境变量，而不是更新代码。
>
> **替代方案：环境变量** 你可以在 shell 中设置环境变量，而不是更新代码。

```bash
export OPENAI_BASE_URL="https://aiplatform.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/global/endpoints/openapi"
export OPENAI_API_KEY="$(gcloud auth application-default print-access-token)"
```
> 然后不带参数初始化客户端：`client = OpenAI()`

### Python 示例（OpenMaaS - Completions API）

以下模型支持遗留 Completions API：`zai-org/glm-5-maas`、`moonshotai/kimi-k2-thinking-maas`、`minimaxai/minimax-m2-maas`、`deepseek-ai/deepseek-v3.1-maas` 和 `deepseek-ai/deepseek-v3.2-maas`。

```python
response = client.completions.create(
    model="deepseek-ai/deepseek-v3.2-maas",
    prompt="Once upon a time",
    max_tokens=100
)
print(response.choices[0].text)
```

### Python 示例（OpenMaaS - Embeddings）

```python
# 在 Model Garden 上验证特定的 Embedding 模型 ID（例如，intfloat/multilingual-e5-small）
response = client.embeddings.create(
    model="intfloat/multilingual-e5-large-maas",
    input="The quick brown fox jumps over the lazy dog",
)
print(response.data[0].embedding)
```

### 替代方案：GenAI SDK

`google-genai` SDK 也可以通过 `vertexai` 后端访问 OpenMaaS 模型。

请参阅 [`scripts/openmaas_genai_sdk.py`](scripts/openmaas_genai_sdk.py) 获取完整代码。

> [!IMPORTANT]
> **模型 ID 格式**：对于使用 OpenMaaS 的 GenAI SDK，你必须使用完整路径：`publishers/PUBLISHER/models/MODEL`（例如，
> `publishers/zai-org/models/glm-5-maas`）。

### 遗留：Agent Platform SDK（OpenMaaS）

对于 OpenMaaS，你也可以使用 `GenerativeModel`（如果受支持）。

请参阅 [`scripts/openmaas_vertexai_sdk.py`](scripts/openmaas_vertexai_sdk.py) 获取完整代码。

> [!IMPORTANT] **模型 ID 格式**：对于使用 OpenMaaS 的 Agent Platform SDK，你必须使用完整路径：`publishers/PUBLISHER/models/MODEL`。

### 模型参考与可用性

**文档**：
[在 Agent Platform 上使用 Open 模型](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/maas/use-open-models)

> [!TIP]
> **自行部署以实现控制**：如果你需要**专用硬件**
> (GPUs/TPUs)、**保证容量**或**特定区域放置**（MaaS 不提供），你可以将这些模型自行部署到 Agent Platform 终端点。在 Model Garden 中搜索模型并点击“部署”以选择你的机器类型。有关部署工作流，请参阅 `agent-platform-deploy` 技能，并参阅该技能的**第 4 节**了解如何调用自行部署的终端点（在专用终端点 DNS 上使用 `/chat/completions`，而不是上面提到的 OpenMaaS 发布者 URL）。

> [!IMPORTANT] **查找推理示例**：上面的列表只是一个起点。对于**最终的**推理片段（尤其是 Chat Completions 负载结构）：1. 参考
> [在 Agent Platform 上使用 Open 模型](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/maas/use-open-models)
> 列表。2. 点击你特定模型的链接（例如，“DeepSeek-V3”）以访问其**Model Garden**页面。3. 在 Model Garden 页面上查找**“示例代码”**或**“使用此模型”**按钮以获取该特定模型版本的精确 `curl` 或 Python 代码。

> [!NOTE] 此列表**不完整**。请参阅
> [在 Agent Platform 上使用 Open 模型](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/maas/use-open-models)
> 以获取支持模型的完整列表。

模型系列 | 模型 ID 示例                              | 位置      | 备注
:------------ | :--------------------------------------------- | :------------ | :----
**Llama 4**   | `meta/llama-4-maverick-17b-128e-instruct-maas` | `us-east5`    |
**Llama 4**   | `meta/llama-4-scout-17b-16e-instruct-maas`     | `us-east5`    |
**Llama 3.3** | `meta/llama-3.3-70b-instruct-maas`             | `us-central1` |
**DeepSeek**  | `deepseek-ai/deepseek-v3.2-maas`               | `global`      | 仅限 Global
**DeepSeek**  | `deepseek-ai/deepseek-v3.1-maas`               | `us-west2`    | 仅限 US-West2
**DeepSeek**  | `deepseek-ai/deepseek-r1-0528-maas`            | `us-central1` |
**Qwen 3**    | `qwen/qwen3-coder-480b-a35b-instruct-maas`     | `global`      |
**Qwen 3**    | `qwen/qwen3-next-80b-a3b-instruct-maas`        | `global`      |
**Kimi**      | `moonshotai/kimi-k2-thinking-maas`             | `global`      |
**MiniMax**   | `minimaxai/minimax-m2-maas`                    | `global`      |
**GLM**       | `zai-org/glm-4.7-maas`, `zai-org/glm-5-maas`   | `global`      |

## 4. 自定义终端点（调优 Gemini、自行部署的 OSS LLM、遗留自定义）

本节介绍了如何在属于你项目的 Agent Platform
**终端点**上调用模型，即具有数字资源名称的终端点，如
`projects/.../endpoints/5875254126916403200`。这与在 2 和 3 节中调用发布者 MaaS 表面不同（这些表面会命中
`publishers/.../models/...` 或 `endpoints/openapi`，而不是你的终端点 ID）。

> [!IMPORTANT]
>
> **发布者 MaaS 与你的终端点（不要混淆它们）。** 第 3 节的 OpenMaaS 示例（例如 `meta/llama-3.3-70b-instruct-maas`）会命中
> **共享发布者 URL** 在
> `/v1/projects/.../locations/.../endpoints/openapi`。本节的配方会命中
> **你的终端点**在 `/v1/projects/.../endpoints/<id>`。如果你通过 Model Garden
> “部署”部署了 Llama / Gemma / 等模型（不是 MaaS 发布者产品），请遵循本节——而不是第 3 节。

> [!IMPORTANT]
>
> **活动终端点发现与单一事实来源**：
>
> *   要检查模型或调优 Gemini 适配器是否已部署并准备好进行推理，请运行：
>
>     `gcloud ai endpoints list --project=<PROJECT_ID> --region=<REGION> --format=json`.
>
> *   **`gcloud ai endpoints list` 是唯一权威的活跃服务终端点来源。**
> *   不要依赖过去 `gcloud ai tuning-jobs list` 记录中的历史 `job.tunedModel.endpoint` 标识符——这些记录在调优期间初始创建终端点，但如果终端点随后被删除、卸载或过期，则不再活跃。
> *   如果 `gcloud ai endpoints list` 返回空 `[]` 或在请求的区域内没有部署任何终端点上的调优模型，请直接向用户报告在该区域未找到活动终端点并停止。**永远**
> 不要假设历史/已删除的终端点已准备好，并且**永远**
> 不要在未明确用户指令和新鲜 Tier R 确认提示的情况下静默替换基础模型。

> [!IMPORTANT]
>
> **两个正交轴决定调用形状**：
>
> **轴 1 — 模型系列** 驱动 RPC 方法和负载：
>
> | 终端点提供 | 方法 | 负载 |
> |---|---|---|
> | 一个**调优的 Gemini 模型**（Gemini 调优的输出——终端点已经为你部署） | `:generateContent` | `contents` / `generationConfig` |
> | 一个**自行部署的 OSS LLM**（Llama、DeepSeek、Qwen、Gemma、Mistral 等，通过 Model Garden 部署） | `/chat/completions` | OpenAI 兼容的 `messages` |
> | 一个**遗留自定义模型**（分类、回归、自定义训练、嵌入） | `:predict` | `instances` / `parameters` |
>
> 运行 `gcloud ai endpoints describe <ENDPOINT_ID> --region=<REGION>
> --format=json` 并检查 `deployedModels[].model` 以决定：
> 包含 `gemini` → 调优 Gemini；匹配 OSS 发布者
> (`meta/`, `google/gemma-`, `deepseek-ai/`, `qwen/`, ...) → OSS LLM；
> 否则 → 可能是遗留自定义。
>
> **轴 2 — 终端点类型（共享与专用）** 驱动 URL 主机：
>
> | `dedicatedEndpointEnabled` | 主机 |
> |---|---|
> | `false`（默认——共享终端点） | `<REGION>-aiplatform.googleapis.com` |
> | `true`（专用终端点，有自己的 DNS） | `dedicatedEndpointDns` 的值（格式：`<ENDPOINT_ID>.<REGION>-<PROJECT_NUM>.prediction.vertexai.goog`) |
>
> 专用终端点**无法**通过共享
> `<REGION>-aiplatform.googleapis.com` 主机访问（根据
> `Endpoint.dedicated_endpoint_enabled` proto：*"一旦你启用了专用终端点，你将无法向共享 DNS 发送请求"*）。始终检查 `dedicatedEndpointDns` 在描述输出中：
> 如果它被设置，请将其用作主机；否则使用共享主机。
>
> **路径在两个主机上始终是
> `/v1/projects/.../locations/.../endpoints/<id>/...`**。两个 `/v1/`（GA）和 `/v1beta1/`（beta）都路由到相同的后端；本技能中的配方使用 `/v1/`。公共
> [Gemma 部署笔记本](https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/community/model_garden/model_garden_gemma_deployment_on_vertex.ipynb)
> 仍然使用 `/v1beta1/`，这也有效。

### 4a. REST 配方——调优的 Gemini 模型

Gemini 调优的输出始终是一个已经为你部署的终端点，可以通过共享主机上的 `:generateContent` 访问。

```bash
PROJECT_ID=my-project
ENDPOINT_ID=5875254126916403200
REGION=us-central1
TOKEN=$(gcloud auth application-default print-access-token)

curl -sS -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://${REGION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${REGION}/endpoints/${ENDPOINT_ID}:generateContent" \
  -d '{
    "contents": [
      {"role": "user", "parts": [{"text": "Hello! Introduce yourself briefly."}]}
    ],
    "generationConfig": {
      "temperature": 0.2
    }
  }'
```

> [!WARNING]
>
> **如果你设置了 `maxOutputTokens`，请为思考模型慷慨一些。**
> Gemini 2.5 Pro（以及其他支持思考的模型）会发出“思考”
> 令牌，这些令牌在用户可见文本之前会消耗 `maxOutputTokens`。如果上限很小（例如 100），整个预算都会被思考消耗，响应的 `text` 部分将为空，但 `usageMetadata.candidatesTokenCount`
> 非零。
>
> 如果你不需要限制输出长度，完全省略 `maxOutputTokens`
> 并让模型想发多少就发多少。如果你确实设置了它：`>= 512` 用于任何聊天式用途，`>= 1024` 用于一整段输出。如果你看到 `finishReason: "MAX_TOKENS"` 但响应中没有 `text`
> 内容，你的上限太低了。

### 4b. REST 配方——自行部署的 OSS LLM（Llama、DeepSeek、Qwen、Gemma 等）

自行部署的 OSS LLM 可能在**共享**或**专用**终端点上，具体取决于部署配置（创建时 `dedicated_endpoint_enabled` 的值）。下面的配方通过检查描述输出中的 `dedicatedEndpointDns` 来处理这两种情况。

```bash
PROJECT_ID=my-project
ENDPOINT_ID=5875254126916403200
REGION=us-central1
TOKEN=$(gcloud auth application-default print-access-token)

# 第 1 步：发现主机。对于共享终端点，dedicatedEndpointDns 为空。
DEDICATED_DNS=$(gcloud ai endpoints describe "$ENDPOINT_ID" \
  --project="$PROJECT_ID" --region="$REGION" \
  --format="value(dedicatedEndpointDns)")

if [ -n "$DEDICATED_DNS" ]; then
  HOST="$DEDICATED_DNS"
else
  HOST="${REGION}-aiplatform.googleapis.com"
fi

# 第 2 步：调用 /chat/completions。两个主机的路径相同。
curl -sS -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://${HOST}/v1/projects/${PROJECT_ID}/locations/${REGION}/endpoints/${ENDPOINT_ID}/chat/completions" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello! Introduce yourself briefly."}
    ]
  }'
```

> [!NOTE]
>
> -   `max_tokens`（不是 `maxOutputTokens`）— 这是 OpenAI 兼容词汇，不是 Vertex。完全省略它以让模型想发多少就发多少；只有当你需要限制输出长度时才显式设置它。
> -   OpenAI 风格负载中的 `"model"` 字段可以省略（或设置为 `""`）对于终端点部署——终端点已经决定了为请求提供哪个模型。
> -   同一个终端点还暴露 `/completions`（遗留文本完成）和 `/embeddings` 用于嵌入模型。
> -   **推理模型**（DeepSeek-R1、Kimi-K2-Thinking、GLM-5 变体等）发出的思考令牌在最终答案之前会消耗 `max_tokens`——与 Gemini 2.5 Pro 在第 4a 节中的问题相同。
>     如果你设置了 `max_tokens` 并得到空的
>     `choices[0].message.content` 或 `finish_reason: "length"`，请提高上限（聊天用 `>= 1024`，更长思考链用 `>= 2048`）或省略它。

`instances` 的确切形状是模型特定的；请参考已部署模型的文档或其部署来源的 Model Garden 卡片。

### 4d. Python（Vertex AI SDK）— 调优的 Gemini 模型

```python
from google import genai
import google.auth

_, project_id = google.auth.default()
client = genai.Client(vertexai=True, project=project_id, location="us-central1")

ENDPOINT_ID = "5875254126916403200"
response = client.models.generate_content(
    model=f"projects/{project_id}/locations/us-central1/endpoints/{ENDPOINT_ID}",
    contents="你好！简要介绍一下你自己。",
    config={"temperature": 0.2},  # 仅当你需要限制时才添加 max_output_tokens
)
print(response.text)
```

## 5. 故障排除和常见错误代码

### 429：资源耗尽

*   **原因**：OpenMaaS 和 Gemini 模型使用 **动态共享配额 (DSQ)**。
    资源是按需动态分配的。429 错误表示共享池暂时耗尽，不一定表示 *你的* 特定项目配额已用完（尽管也可能）。
*   **解决方案**：实施严格的 **指数退避和重试** 策略。
*   **高吞吐量**：对于需要高吞吐量或保证容量的生产工作负载，请考虑 **专用吞吐量 (PT)**。
*   **重要**：通过正常云流程（云控制台）获得的配额增加不适用于 DSQ 限制。
*   **文档**：
    [配额和限制 (DSQ)](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/quotas)

### 400：用户验证错误

*   **原因**：请求格式无效、不支持的参数或模型 ID 不正确。
*   **操作**：仔细检查你的请求负载和参数。验证模型 ID 和区域是否正确。
*   **自定义端点**：根据第 4 节的决策表选择正确的方法 + 主机：
    *   调优的 Gemini + 你调用了 `:predict` → 切换到 `:generateContent`（第 4a 节）。错误提到 "Required instances format mismatch"。
    *   OSS 大语言模型（Llama/DeepSeek/Qwen/Gemma 等）+ 你调用了 `:generateContent` 或 `:predict` → 切换到 `/chat/completions`（第 4b 节）。错误可能是 404、405 或 "method not allowed"。
    *   遗留的 / 自定义训练的 + 你调用了 `:generateContent` 或 `/chat/completions` → 切换到 `:predict`（第 4c 节）。
*   **共享主机上的专用端点已达到（或反之）**：
    *   症状：DNS 解析失败（`Could not resolve host`）或 404。
    *   原因：专用端点不接受在 `<REGION>-aiplatform.googleapis.com` 上的流量，并且专用 DNS（`*.prediction.vertexai.goog`）仅在 `dedicatedEndpointEnabled` 为 true 时存在。
    *   操作：重新检查 `gcloud ai endpoints describe ... --format=json` 的 `dedicatedEndpointDns` 字段；如果非空（根据第 4b/4c 节中的主机发现片段），则使用它。

### Gemini 部署端点上的空响应文本

*   **原因**：`maxOutputTokens` 设置得太低。Gemini 2.5 Pro 和其他思考模型会发出 "thoughts" 令牌，这些令牌在用户可见文本之前计入预算。在较小的限制（例如 100）下，整个预算都被思考消耗，响应的 `text` 部分为空，但 `usageMetadata.candidatesTokenCount` 非零且 `finishReason: "MAX_TOKENS"`。
*   **操作**：完全省略 `maxOutputTokens`（让模型尽可能多地输出），或将它提高到 >= 512 用于聊天式使用，>= 1024 用于更长的输出。有关详细信息，请参阅第 4 节 "自定义端点"。

### 404：未找到 / 模型不可用

*   **原因**：模型未启用，或在指定的项目或区域中不可用。
*   **操作**：
    1.  **检查位置可用性**：
        *   **OpenMaaS**：验证模型是否在你的区域可用。请参阅
            [按位置提供的模型](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/locations#genai-open-models)。
        *   **Gemini**：
            *   **权威来源**：始终检查
                [Gemini 模型位置](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/locations#google-models)
                获取权威列表。
            *   **预览模型**：所有预览模型（例如 Gemini 3.1、实验版本）通常 **仅** 在 `us-central1` 或 `global` 区域可用。
            *   **稳定模型**：（例如 Gemini 2.5 Pro）在 `us-central1`、`europe-west4` 和许多其他区域可用。
            *   **重要**：如果你收到 404/400 错误，请尝试将客户端位置切换到 `us-central1` 或 `global`。
    2.  **启用 Llama 模型**：对于 **Llama 3.3** 和 **Llama 4**，你 **必须** 在使用前在 Model Garden 中启用模型。转到
        [Model Garden](https://console.cloud.google.com/agent-platform/model-garden)，
        搜索模型卡片（例如 "Llama 3.3 API Service"），然后点击 **启用**。只有这样，你才能进行推理请求。
