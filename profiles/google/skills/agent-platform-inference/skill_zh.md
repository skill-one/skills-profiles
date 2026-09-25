# Agent Platform GenAI 推理技能

此技能提供有关如何对 Google Cloud Agent Platform 进行身份验证和连接以使用生成式 AI 模型的说明。它涵盖：

*   **第一方发布者模型**（Gemini）— 第 2 节。
*   **第三方发布者模型**（OpenMaaS：Llama、DeepSeek、Qwen 等）— 第 3 节。
*   **自定义端点**（任何位于数字 `projects/.../endpoints/<id>` 资源上的模型 — 调整后的 Gemini 模型、自部署的 OSS LLM 通过 `agent-platform-deploy` 技能从 Model Garden 部署、以及遗留自定义模型）— 第 4 节。

## 安全性与确认级别（关键）

在代表用户执行任何命令或脚本之前，您必须根据请求的操作遵守以下安全级别。（该技能是只读的；省略了其他安全级别）：

1.  **R 级：只读 / 推理 (`client.models.generate_content`、`client.chat.completions.create`、`client.completions.create`、`client.embeddings.create`)**
    *   在代表用户执行模型推理之前，需要与 '是'/'否'选项进行**交互式确认**，以防止意外成本或配额消耗。
    *   **确认卡中必需的字段**：确认提示必须清楚地解释拟议的推理执行，并明确列出以下所有参数：
        *   **项目 ID**：Google Cloud 项目 ID 或编号（例如 `123456789012`、`my-project`）。
        *   **区域 / 位置**：目标区域（例如 `us-central1`、`global`）。
        *   **模型 ID**：确切的模型 ID（例如 `gemini-2.5-flash`、`deepseek-ai/deepseek-v3.2-maas`）。
        *   **SDK**：SDK 选择（例如 `Google GenAI SDK (google-genai)`、`OpenAI SDK`）。
        *   **输入提示**（或 **输入图像** / **输入媒体**）：提示文本或媒体 URI。
        *   如果指定，则任何其他生成参数（例如 `max_output_tokens`、`response_schema`）。
        自然语言改述而未明确列出这些参数**是不充分的**。
    *   **同轮限制**：不要在同一轮中执行推理脚本或命令，而是在显示确认提示后停止并等待用户的回复；只有在明确 '是' / 批准后才能执行。
    *   **黄金标准示例**：
        > 我将使用以下参数执行模型推理。请在我继续之前确认这些信息：
        > * **项目 ID**：`my-project`
        > * **区域**：`us-central1`
        > * **模型 ID**：`gemini-2.5-pro`
        > * **SDK**：Google GenAI SDK (`google-genai`)
        > * **输入提示**："用 3 句话总结哈姆雷特的剧情"
        >
        > 您确认吗？[是/否]

## 阶段 0：环境设置

**关键**：在运行 `scripts/` 目录中的任何 Python 示例脚本（例如 `scripts/openmaas_openai_sdk.py`）之前，您**必须**通过以下步骤确保环境正确初始化：

1.  **Google Cloud 身份验证**：使用您的 Google Cloud 凭据进行身份验证，并为 Agent Platform 访问配置活动应用默认凭据 (ADC)：

    ```bash
    gcloud auth login
    gcloud auth application-default login
    ```

2.  **启用 API**（如果尚未启用）：

    ```bash
    gcloud services enable aiplatform.googleapis.com
    ```

3.  **Python 依赖项**：脚本导入 `vertexai`（来自 `google-cloud-aiplatform`）、`google-genai` 和 `openai`。**不要**创建虚拟环境——它为空并隐藏环境已经提供的包，强制进行冗余安装。探测并仅安装缺失的内容：

    ```bash
    python3 -c "import vertexai, google.genai, openai" \
      || pip install -r scripts/requirements.txt
    ```

    `scripts/requirements.txt` 是一个备用方案，用于环境不提供这些 SDK 的情况；不要在正常工作环境中安装它。

4.  **验证设置（可选）**：运行所有示例脚本以验证端到端环境是否正常工作：

    ```bash
    ./scripts/verify_all.sh
    ```

5.  **执行**：使用 `python3 scripts/...` 运行脚本。没有需要先激活的环境。

> [!IMPORTANT] **关键：模型 ID & 可用性** * **Gemini 模型**：有关有效模型 ID 和区域的详细信息，请参阅 [Gemini 模型][gemini-models-docs]。
> * **OpenMaaS 模型**：请参阅 [在 Agent Platform 上使用 Open 模型](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/maas/use-open-models) 以使用 Llama、DeepSeek、Qwen 等。
> * **不完整的列表**：此技能中列出的模型 ID 仅为例子，可能不完整或已过时。
> * **操作**：在使用链接生成代码之前，始终使用上述链接验证模型 ID 和区域。

## 参数基础与澄清协议（关键）

在准备代码或显示 R 级确认卡之前，您**必须**确保所有必要参数都已基础：

1.  **缺少模型 ID、模型系列或 SDK（关键）**：
    *   如果用户**未**指定要使用的模型或模型系列（例如，"运行一个测试提示"、"要求生成式 AI 模型..."、"要求 DeepSeek 提问" 而未指定模型版本），或者未指定 SDK 偏好：
    *   **绝对不要**猜测、主动提供或默认使用模型（例如 `gemini-2.5-flash`、`gemini-2.5-pro` 或 `deepseek-v3.2-maas`）。
    *   在没有询问的情况下，在确认卡中提出默认模型违反了参数基础。
    *   **您必须**停止并询问用户："您想使用哪个模型（或模型系列，例如 Gemini、Llama、DeepSeek 或 Qwen）和 SDK 偏好（例如 Google GenAI SDK 或 OpenAI SDK）？" 并询问目标区域和项目 ID（如果未指定）。
    *   只有在用户指定了模型（以及任何缺失的 SDK 偏好）之后，您才能继续准备执行并显示 R 级确认提示。

2.  **缺少项目 ID 或区域**：
    *   如果用户的项目 ID 或区域未在提示或对话上下文中指定，**请询问**用户项目 ID 和区域（例如 "您想使用哪个项目 ID 和区域？"）。不要默默假设项目或区域。
    *   **OpenMaaS 位置**：OpenMaaS 发布者模型托管在 `global`（例如 `deepseek-ai/deepseek-v3.2-maas`、`meta/llama-3.3-70b-instruct-maas`) 或区域端点（例如 `us-central1`）上（例如 `deepseek-ai/deepseek-r1-0528-maas`）。
        在为 OpenMaaS 模型配置推理时，使用适当的端点：

        *   全球：`https://aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/global/endpoints/openapi`
        *   区域：`https://{REGION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{REGION}/endpoints/openapi`

        并在确认卡和最终响应中明确反映区域。

3.  **SDK 选择**：
    *   如果用户指定了模型但未指定 SDK，请使用该模型系列的偏好 SDK（Gemini 的 GenAI SDK `google-genai`、OpenMaaS 的 OpenAI SDK `openai`）。

4.  **通过 Python 进行沙盒执行（关键）**：
    *   当通过 `run_command` 在沙盒中执行模型推理时，**始终**使用官方 SDK 使用 Python 代码（例如，编写和运行使用 `google-genai`、`openai` 或 `vertexai` 的 Python 脚本）。不要使用原始 curl 命令进行最终推理执行。

## 工作流程决策树

1.  **指定模型？**
    *   **否**（用户省略了模型名称/系列）-> **询问用户**他们想使用哪个模型或模型系列、目标区域和 SDK 偏好。
    *   **不明确**（例如，用户说 "DeepSeek" 或 "Llama" 而未指定版本）-> **询问用户**他们更喜欢哪个特定模型版本（例如 `deepseek-ai/deepseek-r1-0528-maas`、`deepseek-ai/deepseek-v3.2-maas`、`meta/llama-3.3-70b-instruct-maas`）。
    *   **是** -> 继续步骤 2。

2.  **模型系列 & SDK 选择**：
    *   **Gemini**（例如，`gemini-2.5-pro`、`gemini-3-flash-preview`）-> 首选：**GenAI SDK** (`google-genai`)。继续 [1. Gemini 模型]。
    *   **OpenMaaS**（例如，`deepseek-ai/*`、`meta/llama-*`、`qwen/*`）-> 首选：**OpenAI SDK** (`openai`)。继续 [2. OpenMaaS 模型]。
    *   **自定义端点**（数字端点 ID `projects/.../endpoints/<id>）-> 继续 [4. 自定义端点]。

3.  **故障排除**：用户是否报告错误（429 资源耗尽、400 用户验证、404 未找到、由于令牌限制的空响应等）？
    *   **是** -> 继续 [5. 故障排除 & 常见错误代码]。
    *   **否** -> 显示 R 级确认提示，包含所有必需字段（项目 ID、区域、模型 ID、SDK、输入提示），等待用户确认，然后通过 Python SDK 执行。

## 0.5 发布者端点区域可用性检查（Gemini + LoRA 基础）

> [!NOTE] **如果以下任一情况适用，请跳过本节**：
>
> - 用户正在调用自定义端点（§4）——在数字 `projects/.../endpoints/<id>` 上托管的调整后的 Gemini 模型、通过 Model Garden 自部署的 OSS LLM（Llama、DeepSeek、Qwen、Gemma 等）或遗留自定义模型。这些请求命中特定端点资源，其区域在部署时已固定；如果调用端区域的区域不匹配，端点查找将返回干净的 404，而不会产生推理成本。转到 §4。
> - 用户正在调用 OpenMaaS 发布者模型（§2）——通过 global `openapi` 基 URL 托管的 Llama、DeepSeek、Qwen 等。这些没有像第一方 Gemini 那样按区域可用性限制。转到 §2。
>
> **仅当用户正在调用第一方管理的 Gemini 模型 (`gemini-*`) 或在 Gemini 顶部上的微调 LoRA 适配器时应用本节** — 这些通过发布者端点路由，其区域可用性实际上会变化。

在响应命名特定区域的第一方管理 Gemini 模型 (`gemini-*`) 或微调 Gemini LoRA 适配器（通过数字端点 ID + 用户声明的基模型）的推理请求之前，您**必须**通过进行实时 API 调用来验证模型实际上在该区域可用。不要依赖 Google 搜索、训练语料库知识或发布者文档中的可用性声明 — 区域可用性经常变化，基础文本可能过时或错误。

仅探测用户询问的确切模型和区域。不要探测其他模型作为 "控制" — 您无法从模型 B 的状态推断模型 A 的可用性，因为不同的模型本身可能由于其他原因在该参考区域不可用。

对于第一方 Gemini 模型，使用真实的 `:generateContent` 调用并使用最小的有效有效负载：

```bash
curl -sS -o /dev/null -w "%{http_code}\n" \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json" \
    "https://${LOCATION_ID}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION_ID}/publishers/google/${MODEL_ID}:generateContent" \
    -d "{\"contents\":{\"role\":\"user\",\"parts\":{\"text\":\"${PROBE_TEXT:-hi}\"}}"
```

对于针对微调 Gemini LoRA 适配器的推理，使用相同的 `:generateContent` 调用（将 `${MODEL_ID}` 设置为基模型，例如 `gemini-2.5-flash` 如果适配器是在 `gemini-2.5-flash` 上微调的）。
LoRA 适配器无法在不为其基模型可用的区域中服务。

解释探测结果并采取行动：

-   **200** — 模型在该区域可用。继续 §1 中的 SDK 设置。
-   **404** — 模型在该区域不可用。停止。明确告知用户该模型在该区域不可用，并列出其可用的区域（从
    [Gemini 模型][gemini-models-docs] 或 `gcloud ai model-garden models list --filter="name~$MODEL_NAME"` 获取完整列表）。不要默默切换区域。不要继续为不受支持的区域编写推理代码或 SDK 初始化。不要运行额外的 "控制" 探测以双查 404 — 目标区域探测是权威的。
-   **任何其他结果**（权限被拒绝、配额、临时故障等）— 不要断定模型可用或不可用。用普通语言解释潜在原因（例如 "您的帐户没有访问此项目的 Vertex AI API 权限 — 在控制台中启用它或切换项目"）和具体操作。

## 1. Gemini 模型

对于 Gemini 模型（例如，`gemini-2.5-pro`、`gemini-3-flash-preview`），**GenAI SDK** (`google-genai`) 是**首选**方法。遗留 `vertexai` SDK 仍然受支持，但建议为新项目使用 GenAI SDK。

> [!IMPORTANT]
> **预览模型**（包括 Gemini 3.1）通常**仅在** `global` 区域可用。稳定模型可在 `us-central1` 和其他区域可用。

### 选择正确的 SDK

*   **Gemini 模型**：**GenAI SDK** (`google-genai`) 是**首选**。使用 OpenAI SDK 兼容性，或遗留 SDK (`vertexai`) 如果需要。
*   **OpenMaaS 模型**：**OpenAI SDK** **强烈推荐**。使用 GenAI SDK 或遗留 SDK 如果您有特定的基础设施要求。

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

**文档**:
[Google GenAI SDK](https://github.com/googleapis/python-genai)

**文档**:
[Agent Platform Gemini 模型](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/google-models)

## 2. OpenMaaS 模型（Llama、DeepSeek、Qwen 等）

对于 OpenMaaS（模型即服务）模型，**强烈推荐**的方法是使用标准 **OpenAI SDK** 与特定 Vertex AI 端点。

> [!WARNING] 虽然可以通过 `GenerativeModel` 支持一些 OpenMaaS 模型，但**不鼓励**使用。使用 OpenAI SDK 以获得最佳兼容性（尤其是对于聊天完成）。

### 安装

```bash
pip install openai google-auth
```

### OpenAI SDK 的身份验证

您**必须**使用 Google Cloud OAuth 访问令牌作为 OpenAI SDK 的 API 密钥。

```python
import subprocess

def get_gcp_access_token():
    return subprocess.check_output(
        ["gcloud", "auth", "print-access-token"]
    ).decode("utf-64").strip()
```

> [!NOTE] Google Cloud 访问令牌通常在 1 小时后过期。上面的 `get_gcp_access_token()` 函数在调用时检索*新的*令牌。对于长时间运行的应用程序，您实现刷新机制。有关详细信息，请参阅
> [刷新访问令牌](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/migrate/openai/auth-and-credentials?hl=en#refresh_your_credentials)

### 配置（基本 URL）

-   **全局端点**（建议大多数需要全局可用性的模型）:
    `https://aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/global/endpoints/openapi`
-   **区域端点**:
    `https://{REGION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{REGION}/endpoints/openapi`

### Python 示例（OpenMaaS - 聊天完成）

有关完整代码，请参阅 [`scripts/openmaas_openai_sdk.py`](scripts/openmaas_openai_sdk.py)。

> [!TIP] **替代方案：环境变量** 您可以在 shell 中设置环境变量，而不是更新代码。

> [!TIP] **替代方案：环境变量** 您可以在 shell 中设置环境变量，而不是更新代码。

```bash
export OPENAI_BASE_URL="https://aiplatform.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/global/endpoints/openapi"
export OPENAI_API_KEY="$(gcloud auth application-default print-access-token)"
```
> 然后，不带参数初始化客户端：`client = OpenAI()`

### Python 示例（OpenMaaS - 完成API）

以下模型支持遗留完成 API：`zai-org/glm-5-maas`、`moonshotai/kimi-k2-thinking-maas`、`minimaxai/minimax-m2-maas`、`deepseek-ai/deepseek-v3.1-maas` 和 `deepseek-ai/deepseek-v3.2-maas`。

```python
response = client.completions.create(
    model="deepseek-ai/deepseek-v3.2-maas",
    prompt="Once upon a time",
    max_tokens=100
)
print(response.choices[0].text)
```

### Python 示例（OpenMaaS - 嵌入式）

```python
# 验证 Model Garden 上的特定嵌入式模型 ID（例如 intfloat/multilingual-e5-small）
response = client.embeddings.create(
    model="intfloat/multilingual-e5-large-maas",
    input="The quick brown fox jumps over the lazy dog",
)
print(response.data[0].embedding)
```

### 替代方案：GenAI SDK

`google-genai` SDK 也可以通过 `vertexai` 后端访问 OpenMaaS 模型。

有关完整代码，请参阅 [`scripts/openmaas_genai_sdk.py`](scripts/openmaas_genai_sdk.py)。

> [!IMPORTANT]
> **GenAI SDK 与 OpenMaaS 的模型 ID 格式**：对于 GenAI SDK 与 OpenMaaS，您**必须**使用完整路径：`publishers/PUBLISHER/models/MODEL`（例如，
> `publishers/zai-org/models/glm-5-maas`）。

### 遗留方案：Agent Platform SDK（OpenMaaS）

对于 OpenMaaS，您还可以使用 `GenerativeModel`（如果支持）。

有关完整代码，请参阅 [`scripts/openmaas_vertexai_sdk.py`](scripts/openmaas_vertexai_sdk.py)。

> [!IMPORTANT] **GenAI SDK 与 OpenMaaS 的模型 ID 格式**：对于 Agent Platform SDK 与 OpenMaaS，您**必须**使用完整路径：`publishers/PUBLISHER/models/MODEL`。

### 模型参考 & 可用性

**文档**:
[在 Agent Platform 上使用 Open 模型](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/maas/use-open-models)

> [!TIP]
> **自我部署以进行控制**：如果您需要**专用硬件**（GPU/TPU）、**保证容量**或**特定的区域放置**（MaaS 没有提供），您可以**自我部署**这些模型到 Agent Platform 端点。在 Model Garden 中搜索模型并点击 "部署" 以选择您的机器类型。有关部署工作流程，请参阅 `agent-platform-deploy` 技能第 4 节 "验证部署"，它在部署后使用相同的模式。

> [!IMPORTANT] **查找推理示例**：上面的列表只是一个起点。对于**权威**推理片段（尤其是聊天完成的负载结构）：
> 1.  咨询 [在 Agent Platform 上使用 Open 模型](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/maas/use-open-models) 列表。
> 2.  点击链接访问您的特定模型卡（例如，"Llama 3.3 API 服务"），例如 [Model Garden](https://console.cloud.google.com/agent-platform/model-garden)。
> 3.  在 Model Garden 页面上查找 **"示例代码"** 或 **"使用此模型"** 按钮以获取特定模型版本的 exact `curl` 或 Python 代码。

> [!NOTE] 此列表**不完整**。请参阅
> [在 Agent Platform 上使用 Open 模型](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/maas/use-open-models)
> 以获取支持模型的全列表。

模型系列 | 模型 ID 示例                              | 位置      | 备注
:------------ | :--------------------------------------------- | :------------ | :----
**Llama 4**   | `meta/llama-4-maverick-17b-128e-instruct-maas` | `us-east5`    |
**Llama 4**   | `meta/llama-4-scout-17b-16e-instruct-maas`     | `us-east5`    |
**Llama 3.3** | `meta/llama-3.3-70b-instruct-maas`             | `us-central1` |
**DeepSeek**  | `deepseek-ai/deepseek-v3.2-maas`               | `global`      | 全球仅限
**DeepSeek**  | `deepseek-ai/deepseek-v3.1-maas`               | `us-west2`    | us-west2 仅限
**DeepSeek**  | `deepseek-ai/deepseek-r1-0528-maas`            | `us-central1` |
**Qwen 3**    | `qwen/qwen3-coder-480b-a35b-instruct-maas`     | `global`      |
**Qwen 3**    | `qwen/qwen3-next-80b-a3b-instruct-maas` | `global`      |
**Kimi**      | `moonshotai/kimi-k2-thinking-maas`             | `global`      |
**MiniMax**   | `minimaxai/minimax-m2-maas`                    | `global`      |
**GLM**       | `zai-org/glm-4.7-maas`、`zai-org/glm-5-maas`   | `global`      |

## 4. 自定义端点（调整后的 Gemini、自部署的 OSS LLM、遗留自定义模型）

本节涵盖如何在 Agent Platform **端点**上调用模型，该端点属于您项目 — 即具有数字资源名称如
`projects/.../endpoints/5875254126916403200` 的内容。这与调用第 2 节和第 3 节中的发布者 MaaS 表面（这些命中
`publishers/.../models/...` 或 `endpoints/openapi`，而不是您的端点 ID）不同。

> [!IMPORTANT]
>
> **发布者 MaaS 与您的端点（不要混淆它们）。** 第 3 节的 OpenMaaS 示例（例如 `meta/llama-3.3-70b-instruct-maas`）命中一个
> **共享发布者 URL** at
> `/v1/projects/.../locations/.../endpoints/openapi`。本节中的配方命中
> **您的端点** at `/v1/projects/.../endpoints/<id>`。
> 如果您通过 Model Garden "部署" 部署了 Llama / Gemma / 等，请遵循本节，而不是第 3 节。

> [!IMPORTANT]
>
> **活动端点发现 & 单一事实来源**:
>
> *   要检查模型或调整后的 Gemini LoRA 适配器是否已部署并准备好进行推理，请运行：
>
>     `gcloud ai endpoints list --project=<PROJECT_ID> --region=<REGION> --format=json`.
>
> *   **`gcloud ai endpoints list` 是唯一权威的活跃服务端点来源。**
> *   不要依赖来自过去 `gcloud ai tuning-jobs list` 记录的历史 `job.tunedModel.endpoint` 标识符 — 这些记录了在调整期间端点最初创建的位置，但如果端点随后被删除、卸载或过期，则不再活跃。
> *   如果 `gcloud ai endpoints list` 返回空 `[]` 或请求的调整后模型在任何列出的端点上都没有部署，请直接向用户报告未在该区域找到活动端点并停止。**绝对不要**假设历史/已删除端点已准备好，**绝对不要**默默替换为基模型，并且需要明确的用户指令和新鲜的 R 级确认提示。

> [!IMPORTANT]
>
> **两个正交轴决定调用形状**:
>
> **轴 1 — 模型系列** 推动 RPC 方法和负载：
>
> | 端点服务 | 方法 | 负载 |
> |---|---|---|
> | 一个**调整后的 Gemini 模型**（Gemini 调整的输出 — 端点在部署时已为您部署） | `:generateContent` | `contents` / `generationConfig` |
> | 一个**自部署的 OSS LLM**（Llama、DeepSeek、Qwen、Gemma 等） | `/chat/completions` | OpenAI 兼容的 `messages` |
> | 一个**遗留自定义模型**（分类、回归、自定义训练、嵌入式） | `:predict` | `instances` / `parameters` |

### 4a. REST 配方 — 调整后的 Gemini 模型

Gemini 调整的输出始终是一个已部署的端点，可通过共享主机使用 `:generateContent` 访问。

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
      {"role": "user", "parts": [{"text": "Hello! Introduce yourself briefly."}]
    ],
    "generationConfig": {
      "temperature": 0.2
    }
  }'
```

> [!WARNING]
>
> **如果您设置了 `maxOutputTokens`，请对思考模型**（DeepSeek-R1、Kimi-K2-Thinking、GLM-5 变体等）**要慷慨**。
> Gemini 2.5 Pro 和其他思考模型发出 "thoughts" 令牌，这些令牌在用户可见文本之前计入预算。如果限制很小（例如 100），整个预算将被 thoughts 消耗，响应将具有空的 `text` 部分，但 `usageMetadata.candidatesTokenCount` 非零，`finishReason: "MAX_TOKENS"`。
>
> 如果您不需要限制输出长度，请完全省略 `maxOutputTokens`，让模型发出尽可能多的内容；如果您需要限制输出长度，请明确设置它。如果看到 `finishReason: "MAX_TOKENS"` 且响应中没有 `text` 内容，则您的上限太低（聊天式使用 >= 512，较长的输出 >= 1024）。如果您看到 `finishReason: "length"` 且响应中的 `choices[0].message.content` 为空，请提高上限（聊天 >= 1024，更长的思考链 >= 2048）或省略它。

### 4b. REST 配方 — 自部署的 OSS LLM（Llama、DeepSeek、Qwen、Gemma 等）

自部署的 OSS LLM 可能位于**共享**或**专用**端点，具体取决于部署配置（创建时 `dedicated_endpoint_enabled` 的值）。下面的配方处理这两种情况，通过检查 `dedicatedEndpointDns` 来确定主机。

```bash
PROJECT_ID=my-project
ENDPOINT_ID=5875254126916403200
REGION=us-central1
TOKEN=$(gcloud auth application-default print-access-token)

# 第 1 步：发现主机。dedicatedEndpointDns 对于共享端点是空的。
DEDICATED_DNS=$(gcloud ai endpoints describe "$ENDPOINT_ID" \
  --project="$PROJECT_ID" --region="$REGION" \
  --format="value(dedicatedEndpointDns)")

if [ -n "$DEDICATED_DNS" ]; then
  HOST="$DEDICATED_DNS"
else
  HOST="${REGION}-aiplatform.googleapis.com"
fi

# 第 2 步：调用 /chat/completions。路径对于两个主机都是相同的。
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
> - `max_tokens`（NOT `maxOutputTokens`）— 这是 OpenAI 兼容词汇，不是 Vertex。省略它完全，让模型发出尽可能多的内容；如果您需要限制输出长度，请明确设置它。
> - OpenAI 风格负载中的 `"model"` 字段可以省略（或设置为 `""`）对于端点部署 — 端点已经决定了要服务的模型。
> - 同一端点也暴露了 `/completions`（遗留文本完成）和 `/embeddings` 用于嵌入式模型。
> - **推理模型**（DeepSeek-R1、Kimi-K2-Thinking、GLM-5 变体等）发出思考令牌，这些令牌在最终答案之前计入 `max_tokens`。与 Gemini 2.5 Pro 在第 4a 节中相同。
> 如果您设置了 `max_tokens` 且响应中的 `choices[0].message.content` 为空或 `finish_reason: "length"`，请提高上限（聊天 >= 1024，更长的思考链 >= 2048）或省略它。

Python 等效（OpenAI SDK）— 与公共
[Gemma 部署笔记本](https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/community/model_garden/model_garden_gemma_deployment_on_vertex.ipynb) 相似：

```python
import google.auth
from google.auth.transport.requests import Request
import openai

from google.cloud import aiplatform

PROJECT_ID = "my-project"
ENDPOINT_ID = "5875254126916403200"
REGION = "us-central1"

aiplatform.init(project=PROJECT_ID, location=REGION)
endpoint = aiplatform.Endpoint(
    f"projects/{PROJECT_ID}/locations/{REGION}/endpoints/{ENDPOINT_ID}"
)
endpoint_resource_name = endpoint.resource_name  # 完整的 projects/.../endpoints/<id>
dedicated_dns = endpoint.gca_resource.dedicated_endpoint_dns  # 共享端点为空

host = dedicated_dns if dedicated_dns else f"{REGION}-aiplatform.googleapis.com"
base_url = f"https://{host}/v1/{endpoint_resource_name}"

import subprocess

token = subprocess.check_output(
    ["gcloud", "auth", "print-access-token"]
).decode("utf-8").strip()

client = openai.OpenAI(base_url=base_url, api_key=token)
response = client.chat.completions.create(
    model="",  # 端点决定了要服务的模型
    messages=[{"role": "user", "content": "Hello! Introduce yourself briefly."}],
    # 省略 max_tokens 以让模型发出尽可能多的内容。如果您需要限制输出长度，请明确设置它。
)
print(response.choices[0].message.content)
```

另请参阅：`agent-platform-deploy` 技能第 4 节 "验证部署"，它使用相同的模式进行部署后。

### 4c. REST 配方 — 遗留 `:predict`（自定义 / 分类 / 嵌入式）

与 4b 相同的主机发现逻辑（基于 `dedicatedEndpointDns`）：

```bash
DEDICATED_DNS=$(gcloud ai endpoints describe "$ENDPOINT_ID" \
  --project="$PROJECT_ID" --region="$REGION" \
  --format="value(dedicatedEndpointDns)")
HOST=${DEDICATED_DNS:-${REGION}-aiplatform.googleapis.com}

curl -sS -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://${HOST}/v1/projects/${PROJECT_ID}/locations/${REGION}/endpoints/${ENDPOINT_ID}:predict" \
  -d '{
    "instances": [{"key": "value"}],
    "parameters": {}
  }'
```

确切的 `instances` 形状是模型特定的；请参考部署模型的文档或它部署自 Model Garden 卡。

### 4d. Python（Vertex AI SDK） — 调整后的 Gemini 模型

```python
from google import genai
import google.auth

_, project_id = google.auth.default()
client = genai.Client(vertexai=True, project=project_id, location="us-central1")

ENDPOINT_ID = "5875254126916403200"
response = client.models.generate_content(
    model=f"projects/{project_id}/locations/us-central1/endpoints/{ENDPOINT_ID}",
    contents="Hello! Introduce yourself briefly.",
    config={"temperature": 0.2},  # 添加 max_output_tokens 仅如果您需要限制输出
)
print(response.text)
```

## 5. 故障排除 & 常见错误代码

### 429: 资源耗尽

*   **原因**：OpenMaaS 和 Gemini 模型使用**动态共享配额 (DSQ)**。资源是按需池化和动态分配的，根据可用性分配。429 错误表示共享池暂时用尽，不一定表示您的特定项目配额已用完（尽管也可能如此）。
*   **解决方案**：实施**严格的指数退避和重试**策略。
*   **高吞吐量**：对于需要高吞吐量或保证容量的生产工作负载，请考虑**吞吐量 (PT)**。
*   **重要**：通过正常云流程（控制台）进行的配额增加**不适用于** DSQ 限制。
*   **文档**:
[配额和限制 (DSQ)](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/quotas)

### 400: 用户验证错误

*   **原因**：请求格式无效、不支持的参数或 Model ID 不正确。
*   **操作**：仔细检查您的请求负载和参数。验证 Model ID 和区域是否正确。
*   **自定义端点**：根据第 4 节的决策表选择正确的方法 + 主机：
    *   调整后的 Gemini + 您调用了 `:predict` → 切换到 `:generateContent`（第 4a）。错误提到 "Required instances format mismatch"。
    *   OSS LLM（Llama/DeepSeek/Qwen/Gemma 等）+ 您调用了 `:generateContent` 或 `:predict` → 切换到 `/chat/completions`（第 4b）。错误可能是 404、405 或 "method not allowed"。
    *   遗留 / 自定义训练 + 您调用了 `:generateContent` 或 `/chat/completions` → 切换到 `:predict`（第 4c）。
*   **专用端点达到共享主机（或反之）**：
    *   症状：DNS 解析失败 (`Could not resolve host`) 或 404。
    *   原因：专用端点不接受在 `<REGION>-aiplatform.googleapis.com` 上的流量，并且专用 DNS (`*.prediction.vertexai.goog`) 仅当 `dedicatedEndpointEnabled` 为 true 时才存在。
    *   操作：重新检查 `gcloud ai endpoints describe ... --format=json` 以获取 `dedicatedEndpointDns` 字段；如果非空，则使用它作为主机（根据第 4b/4c 中的主机发现片段）。

### Gemini 部署端点上的空响应文本

*   **原因**：`maxOutputTokens` 设置得太低。Gemini 2.5 Pro 和其他思考模型发出 "thoughts" 令牌，这些令牌在用户可见文本之前计入预算。如果限制很小（例如 100），整个预算将被 thoughts 消耗，响应将具有空的 `text` 部分，但 `usageMetadata.candidatesTokenCount` 非零，`finishReason: "MAX_TOKENS"`。
*   **操作**：完全省略 `maxOutputTokens`，让模型发出尽可能多的内容，或者提高它（聊天式使用 >= 512，较长的输出 >= 1024）。如果您看到 `finishReason: "MAX_TOKENS"` 且响应中没有 `text` 内容，则您的上限太低（聊天 >= 1024，更长的思考链 >= 2048）或省略它。

### 404: 未找到 / 模型不可用

*   **原因**：模型未启用，或在指定的项目或区域不可用。
*   **操作**：
    1.  **检查位置可用性**：
        *   **OpenMaaS**：验证模型是否在您的区域可用。请参阅
        [按位置查找模型可用性](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/locations#genai-open-models)。
        *   **Gemini**：
            *   **事实来源**：始终检查
                [Gemini 模型位置](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/locations#google-models)
            *   **预览模型**（包括 Gemini 3.1）通常**仅**在 `global` 区域可用。稳定模型可在 `us-central1` 和其他区域可用。
            *   **重要**：如果您遇到 404/400 错误，请尝试将客户端位置更改为 `us-central1` 或 `global`。
    2.  **启用 Llama 模型**：对于 **Llama 3.3** 和 **Llama 4**，您**必须**在 Model Garden 中启用模型才能使用。转到
        [Model Garden](https://console.cloud.google.com/agent-platform/model-garden)、搜索模型卡（例如，"Llama 3.3 API 服务"），并点击 **启用**。只有这样才能进行推理请求。
