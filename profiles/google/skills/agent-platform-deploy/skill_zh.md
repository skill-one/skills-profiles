# 代理平台模型花园部署技能

此技能提供从代理平台模型花园部署 Open 模型的说明，以及随后卸载以清理资源的说明。

## 1P 调整模型复制与部署

如果您需要将 **1P（第一方）调整模型** 从源项目复制到目标区域或项目，并将其部署到新创建的端点，请参阅
[1P 调整模型复制与部署指南](references/copy_deploy_guide.md)。

## 安全性与确认级别（关键）

在代表用户执行任何命令之前，您必须根据请求的操作遵守以下安全级别：

1.  **R 级：只读 (`list`，`describe`，`list-deployment-config`)**
    *   **规则**：无需确认。您可以立即执行这些命令，为用户提供信息。
2.  **M 级：可变且可逆 (`deploy`，`undeploy-model`)**
    *   **规则**：这需要明确的用户确认。您必须向用户展示一个清晰的确认提示，解释建议的命令。在执行之前，您必须等待他们的明确确认。对于 `undeploy-model`，您必须首先验证端点和已部署的模型是否存在；如果 `describe` 或 `list` 返回 404 或空结果，您必须停止并通知用户，而不是尝试卸载。
    *   **同回合限制**：不要在展示确认提示的同回合中运行命令。在询问后结束您的回合，等待用户的回复；只有在明确批准后才能执行。在用户可以回答之前打印预览并调用工具不算获得确认。
3.  **D 级：破坏性且不可逆 (`delete`)**
    *   **规则**：这需要 **明确的类型确认**。您必须输出一条文本消息，解释端点或模型删除的不可逆性，并在执行删除命令之前要求用户键入 "I confirm" 或 "Yes, delete it"。

## 1. 前提条件

在部署之前，请确保您已设置正确的项目和区域。以下命令使用占位符变量 `PROJECT_ID` 和 `LOCATION_ID`。

确保您已通过身份验证：

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project $PROJECT_ID
```

## 2. 发现可部署模型

您可以列出模型花园中可用的模型，并检查它们是否可以自我部署。

```bash
gcloud ai model-garden models list
```

要查看特定模型支持哪些机器类型和加速器，请传递从上述 `models list` 输出中获得的 `MODEL_ID`。将下面的 `<PUBLISHER>/<FAMILY>@<VERSION-ID>` 替换为目录输出中的确切字符串——占位符故意不是真实的模型 ID：

```bash
gcloud ai model-garden models list-deployment-config \
    --model="<PUBLISHER>/<FAMILY>@<VERSION-ID>"
```

> [!NOTE] 某些模型，尤其是 Hugging Face 模型，在部署时可能需要 Hugging Face 访问令牌。

> [!TIP] **模型推荐说明**：每当您准备在响应中命名特定模型版本时，**不要**从内存中推荐。这适用于以下所有情况——不仅仅是直接的部署请求：
>
> *   用户要求部署模型但没有命名。
> *   您在 `list`，`describe` 或 `undeploy` 操作后主动提出下一步建议（例如 "您想将 `<model>` 部署到此端点吗？"）。
> *   用户问一个通用的 "我应该使用什么？" / "X 适合什么模型？" 的问题。
> *   您在向用户展示示例命令时填写 `MODEL_ID` 值（与 `<PUBLISHER>/<FAMILY>@<VERSION-ID>` 这样的占位符相反）。
>
> 新模型版本经常发布，旧版本可能会被弃用，因此训练语料库中关于哪些模型存在的知识不可靠。请遵循以下步骤：
>
> 1.  **澄清用例** 如果上下文不明确（任务类型、质量与延迟与成本优先级、硬件/配额限制、许可证限制）。如果用户已经给出了足够的信号，则跳过。
> 2.  **使用 `gcloud ai model-garden models list` 查询实时目录**。在适当的情况下使用 `--filter` 进行缩小（例如 `--filter="name~gemma"`，`--filter="name~llama"`，`--filter="name~qwen"`，`--filter="name~deepseek"`）。在您看到此项目目录输出中的特定模型之前，**永远不要**向用户命名特定模型版本。
> 3.  **选择该系列中适用于用例的最新通用版本**。当存在多个大小变体时，选择与用户的硬件/成本容忍度匹配的那个。优先选择较新的主版本而不是较旧的版本，除非它被标记为预览/实验性，并且用户明确要求稳定选项。
> 4.  **在向用户命名之前，使用 `gcloud ai model-garden models list-deployment-config --model="<publisher>/<family>@<version>"` 验证确切模型 ID 是否可部署**。
> 5.  **在推荐中逐字引用模型 ID**，与目录中完全相同。不要将其意译为系列标签（"Gemma"，"Llama"）。
>
> 下面 §3 示例中的 `MODEL_ID` 值是故意非实质性的占位符（`<PUBLISHER>/<FAMILY>@<VERSION-ID>`）。**不要**用用户面推荐的记住的模型名称替换它们——始终首先重新运行步骤 2-4，然后引用目录中的确切字符串。

## 2.1 发布商端点区域可用性检查（Gemini + LoRA 基础）

> [!NOTE] **如果用户要求从模型花园部署开放权重模型（Gemma，Llama，DeepSeek，Qwen 或任何用户提供的权重）**——即通过 `gcloud ai model-garden models deploy` 部署到专用端点上的任何内容。这些模型没有按区域可用性限制；模型花园目录是全局的。不寻常区域的实际故障模式是 (a) 请求的加速器/机器类型在该区域不可用，或 (b) 项目没有配额——两者在部署时都会作为干净的错误出现（§3 的成本确认门会捕获它们）。直接进入 §3。
>
> **仅当用户要求提供第一方管理的 Gemini 模型（`google/gemini-*`）或一个微调的 Gemini LoRA 适配器时应用此部分**——两者都通过发布商端点路由，其区域可用性实际上有所不同。

在响应任何命名特定区域的第一方管理模型（`google/gemini-*`）或微调的 Gemini LoRA 适配器的部署请求之前，您 **必须** 通过进行实时 API 调用来验证模型实际上在该区域可用。不要依赖 Google 搜索、训练语料库知识或发布商文档来声明可用性——区域可用性经常变化，基于文本的信息可能过时或错误。

仅探测用户询问的确切模型和区域。不要作为“控制”探测其他模型——您无法从模型 B 的状态推断出模型 A 的可用性，因为不同的模型本身可能由于其他原因在该参考区域不可用。

对于第一方发布商模型（`google/*`），使用一个真实的 `:generateContent` 调用来探测：

```bash
curl -sS -o /dev/null -w "%{http_code}\n" \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json" \
    "https://${LOCATION_ID}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION_ID}/publishers/google/${MODEL_ID}:generateContent" \
    -d "{\"contents\":{\"role\":\"user\",\"parts\":{\"text\":\"${PROBE_TEXT:-hi}\"}}}"
```

对于微调的 Gemini LoRA 模型（在基础 Gemini 模型上部署用户微调的适配器），使用与上述相同的 `:generateContent` 调用来探测目标区域中的**基础模型**。LoRA 适配器在其基础模型不可用的区域无法服务。

解释探测结果并采取行动：
-   **200** — 模型在该区域可用。继续部署。
-   **404** — 模型在该区域不可用。停止。明确告诉用户该模型在该区域不可用，并列出其可用的区域（从 `gcloud ai model-garden models list --filter="name~$MODEL_NAME"` 而不是 `--region`）。不要无声地切换区域。不要为不支持的区域编写部署代码或 SDK 初始化。不要运行额外的“控制”探测来双重检查 404——目标区域探测是权威的。
-   **任何其他结果**（权限拒绝、配额、临时故障等）——不要得出模型可用或不可用的结论。用普通语言解释根本原因（例如 "您的帐户没有访问此项目的 Vertex AI API 权限——在控制台或切换项目"），并说明具体的下一步行动。

## 3. 部署模型

> [!WARNING] 部署模型，尤其是大型模型，会消耗大量计算资源并产生费用。
>
> 1.  在建议部署之前，您 **必须** 计算 `--machine-type` 的每小时 $ 估计。按顺序尝试，并在任何失败时（工具不可用、工具返回 `status != "success"`、脚本退出非零、脚本拒绝机器类型）向下传递：
>
>     a. 如果 `estimate_cost` 工具可用并且返回 `status == "success"`，使用其结果——它返回来自 `CostEstimationService` 的实时 SKU 解析定价（机器 + 加速器 + 总计），而不是硬编码的快照。在任何其他状态（包括 `error`）下，向下传递到 (b)。
>
>     b. 否则，运行 `scripts/calculate_cost.py`。加速器类型和数量在模型花园中每个机器类型都是固定的，并自动派生。示例：
>
>     ```bash
>     python3 scripts/calculate_cost.py \
>         --machine-type=g2-standard-48
>     ```
>
>     如果脚本退出非零（未知 `--machine-type`——模型花园目录中的机器是常规状态，但尚未在价格快照中，例如今天的 A4/B200），向下传递到 (c)。不要编造一个数字。
>
>     c. 如果工具不可用并且脚本不知道请求的机器类型，则回退到
>     [代理平台预测定价](https://cloud.google.com/products/gemini-enterprise-agent-platform/pricing?hl=en#prediction-and-explanation)。
>
>     直接从该页面读取加速器 + 每小时费率，并在向用户提供的估计中引用 URL。
>
> 2.  您 **必须** 向用户展示此成本估计，并警告他们这是**列表价格**，由于潜在的折扣、预留或非 `us-central1` 区域，可能与他们的实际账单不同。
> 3.  在执行任何 `deploy` 命令之前，您 **必须始终** 请求用户同意估计的成本。

要部署模型，请使用 `deploy` 命令。对于长时间运行的部署，强烈建议使用 `--asynchronous` 标志，如有必要，则轮询状态。

### 示例：从模型花园部署开放权重模型

这是一个典型的 bash 脚本，用于部署模型。您可以直接运行此代码块。

```bash
#!/bin/bash
# 示例脚本：从模型花园部署开放权重模型。
#
# 注意：下面的 MODEL_ID 是占位符，不是真实的模型 ID。在运行此脚本之前，用来自实时 `gcloud ai model-garden models list`（见 §2）的值替换它，并且不要将占位符回显给用户作为推荐的模型。

PROJECT_ID=$(gcloud config get-value project)
LOCATION_ID="us-central1" # 推荐的默认区域
MODEL_ID="<PUBLISHER>/<FAMILY>@<VERSION-ID>" # 占位符——用 `gcloud ai model-garden models list` 中的确切 ID 替换

echo "正在将模型 $MODEL_ID 部署到项目 $PROJECT_ID 中的 $LOCATION_ID..."

# 如果省略硬件参数，模型花园可以自动选择所需的硬件。
# 以下是包含所有支持参数的全面命令：
gcloud ai model-garden models deploy \
    --project=$PROJECT_ID \
    --region=$LOCATION_ID \
    --model=$MODEL_ID \
    --machine-type="g2-standard-48" \
    --accelerator-type="NVIDIA_L4" \
    --accelerator-count=4 \
    --endpoint-display-name="my-open-model-deployment" \
    --hugging-face-access-token="YOUR_HF_TOKEN" \
    --reservation-affinity="reservation-affinity-type=specific-reservation,key=compute.googleapis.com/reservation-name,values=my-reservation" \
    --asynchronous

echo "异步部署已启动。"
```

### 示例：部署自定义权重

要部署使用自定义权重的模型，您可以使用完全相同的 `deploy` 命令。将 `--model` 标志中的模型花园模型 ID 替换为指向您的自定义权重文件夹的 Google Cloud Storage (GCS) URI。

```bash
#!/bin/bash
# 示例脚本：从 GCS 桶部署具有自定义权重的模型

PROJECT_ID=$(gcloud config get-value project)
LOCATION_ID="us-central1"
# 用指向您的自定义权重文件夹的 gs:// URI 替换
MODEL_GCS_URI="gs://your-bucket-name/path/to/custom-weights"

echo "正在从 $MODEL_GCS_URI 部署自定义模型到项目 $PROJECT_ID 中的 $LOCATION_ID..."

gcloud ai model-garden models deploy \
    --project=$PROJECT_ID \
    --region=$LOCATION_ID \
    --model=$MODEL_GCS_URI \
    --machine-type="g2-standard-12" \
    --accelerator-type="NVIDIA_L4" \
    --endpoint-display-name="my-custom-model" \
    --asynchronous

echo "异步部署已启动。"
```

## 4. 检查部署状态

当您使用 `--asynchronous` 标志异步部署模型时，`deploy` 命令将返回一个操作 ID。您可以使用此 ID 来检查部署的进行状态。

```bash
gcloud ai operations describe YOUR_OPERATION_ID \
    --region=$LOCATION_ID
```

> [!NOTE] 作为代理，您还可以主动为用户提供检查部署状态的服务，如果他们提供操作 ID 或如果他们通过您启动了部署。

或者，您可以列出您的端点，看看它是否出现，并在 Cloud Console 下“在线预测”选项卡下检查。

```bash
gcloud ai endpoints list \
    --region=$LOCATION_ID
```

注意：大型模型（大约 20B+ 参数）可能需要 15-20 分钟才能完全部署并开始服务。

### 验证部署

如果模型成功部署，通过进行预测调用进行测试来验证。由于模型花园模型通常部署到专用端点，您不应使用 `gcloud ai endpoints predict`。相反，您必须获取端点的专用 DNS 名称并发送 `curl` 请求。

> [!TIP] 要求用户尝试使用他们自己的提示来查看结果。否则使用默认值。

使用以下脚本：

```bash
#!/bin/bash
PROJECT_ID=$(gcloud config get-value project)
LOCATION_ID="us-central1"
ENDPOINT_ID="YOUR_ENDPOINT_ID"
PROMPT=${1:-"Explain quantum computing in simple terms."}

echo "获取专用端点 DNS..."
ENDPOINT_URL=$(gcloud ai endpoints describe $ENDPOINT_ID --project=$PROJECT_ID --region=$LOCATION_ID --format="value(dedicatedEndpointDns)")

if [ -z "$ENDPOINT_URL" ]; then
    echo "错误：无法检索专用端点 URL。请验证您的 ENDPOINT_ID。"
    exit 1
fi

echo "向 $ENDPOINT_URL 发送预测请求..."
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://${ENDPOINT_URL}/v1beta1/projects/${PROJECT_ID}/locations/${LOCATION_ID}/endpoints/${ENDPOINT_ID}/chat/completions" \
  -d '{
    "model": "'"$ENDPOINT_ID"'",
    "messages": [
      {
        "role": "user",
        "content": "'"$PROMPT"'"
      }
    ]
  }'
```

## 5. 卸载和清理

要停止产生费用，您必须将模型从端点卸载。如果您没有确切的端点和已部署模型 ID，这是一个多步骤过程。

### 示例：查找并卸载模型

这是一个 bash 脚本，演示如何查找 ID 并卸载模型。

```bash
#!/bin/bash
# 示例脚本：卸载模型

PROJECT_ID=$(gcloud config get-value project)
LOCATION_ID="us-central1"
# 部署期间使用的模型 ID（有时不包含提供者前缀，或与描述中完全相同）
# 通过 `gcloud ai models list` 找到特定 ID 通常更容易
# 在此示例中，假设我们知道确切的 Endpoint ID 和 Deployed Model ID。

# 1. 查找 Endpoint ID
echo "列出 $LOCATION_ID 中的端点:"
gcloud ai endpoints list --project=$PROJECT_ID --region=$LOCATION_ID

# (假设您从上述输出中提取了 ENDPOINT_ID)
# ENDPOINT_ID="your_endpoint_id"

# 2. 查找已部署模型 ID
echo "列出 $LOCATION_ID 中的模型以查找模型描述:"
gcloud ai models list --project=$PROJECT_ID --region=$LOCATION_ID

# (假设您找到了特定的 MODEL_ID)
# MODEL_ID="your_model_id"
# gcloud ai models describe $MODEL_ID --project=$PROJECT_ID --region=$LOCATION_ID
# (从输出中提取 deployedModelId)
# DEPLOYED_MODEL_ID="your_deployed_model_id"

# 3. 卸载
echo "从端点 $ENDPOINT_ID 卸载模型 $DEPLOYED_MODEL_ID..."
gcloud ai endpoints undeploy-model $ENDPOINT_ID \
    --project=$PROJECT_ID \
    --region=$LOCATION_ID \
    --deployed-model-id=$DEPLOYED_MODEL_ID

echo "模型已卸载。"

# 4. 删除端点
echo "删除端点 $ENDPOINT_ID..."
gcloud ai endpoints delete $ENDPOINT_ID \
    --project=$PROJECT_ID \
    --region=$LOCATION_ID \
    --quiet
echo "端点已删除。"

# 5. 删除模型
echo "删除模型 $MODEL_ID..."
gcloud ai models delete $MODEL_ID \
    --project=$PROJECT_ID \
    --region=$LOCATION_ID \
    --quiet
echo "模型已删除。"
```

> [!WARNING] 如果未卸载模型，即使您没有发送预测请求，也会为分配的计算资源产生持续费用。测试后始终清理。

## 6. 故障排除

### 部署失败：配额或资源耗尽

如果由于 `QUOTA_EXCEEDED` 或 `RESOURCE_EXHAUSTED` 错误，您的部署失败（或停留在错误状态），则请求的特定硬件（例如 `NVIDIA_L4` 或 `g2-standard-24`）要么不在您选择的区域中，要么超出您项目的配额限制。

**解决方案**：仔细查看返回的错误消息。它通常会建议一个当前有可用性的替代区域或机器类型。**要求用户确认**使用建议的 `--region` 或 `--machine-type` 参数重试部署。

> [!WARNING] 如果替代建议涉及更改机器类型或加速器，您 **必须** 通过使用新参数重新运行 `scripts/calculate_cost.py`（见 §3）来重新计算估计成本，警告用户列表价格与实际账单可能不同，并在重试部署之前获得他们的明确确认。
