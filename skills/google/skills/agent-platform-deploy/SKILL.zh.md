---
name: agent-platform-deploy
description: 将 Model Garden 中的开放模型或自定义权重部署到 Agent Platform 端点，检查正在进行的部署操作状态，或通过卸载模型和删除端点清理资源。在要求主动部署模型、列出 Model Garden 可用模型目录、检查特定模型是否可部署（`gcloud ai model-garden models list-deployment-config`）、查询部署成本、排查部署错误（如配额限制）或卸载/清理端点时使用。也用于复制和部署 1P Tuned Model。不用于纯列表/发现形式的问题，如“X 是否已部署？”、“列出我的端点”或“哪些区域有模型运行？”——这些情况请使用 `agent-platform-endpoint-management`。不用于公共 Vertex AI 部署（使用 `vertex-deploy` 技能）或模型评估（使用 `agent-platform-eval-flywheel` 技能）。
---

# 代理平台模型花园部署技能

此技能提供从代理平台模型花园部署 Open 模型的说明，以及随后卸载以清理资源的说明。

## 1P 调优模型复制与部署

如果您需要将 **1P（第一方）调优模型** 从源项目复制到目标区域或项目，并将其部署到新创建的端点，请参考
[1P 调优模型复制与部署指南](references/copy_deploy_guide.md)。

## 安全性与确认级别（关键）

在代表用户执行任何命令之前，您必须根据请求的操作遵守以下安全级别：

1.  **R 级：只读 (`list`, `describe`, `list-deployment-config`)**
    *   **规则**：无需确认。您可以立即执行这些命令，为用户提供信息。
2.  **M 级：可变且可逆 (`deploy`, `undeploy-model`)**
    *   **规则**：这需要明确的用户确认。您必须显示一个包含以下内容的清晰预运行确认卡片：
        1.  精确的提议请求：部署的 `:deploy` 请求正文（§3），或 `undeploy-model` 的 `gcloud` 命令代码块。
        2.  模型标识符、目标项目 ID 和目标区域。
        3.  机器类型和加速器配置。
        4.  预计每小时成本 ($/hr)。
        5.  端点显示名称。
        6.  明确的确认提示，要求用户在执行前批准。
        您必须在获得明确确认后才能执行。对于 `undeploy-model`，您必须首先验证端点和部署的模型是否存在；如果 `describe` 或 `list` 返回 404 或空结果，您必须停止并通知用户，而不是尝试卸载。
    *   **同轮限制**：不要在显示确认提示的同一轮中运行命令。在询问后结束您的回合，等待用户的回复；只有在明确批准后才能执行。在用户可以回答之前打印预览并调用工具不算是获得确认。
3.  **D 级：破坏性且不可逆 (`delete`)**
    *   **规则**：这需要 **明确的类型确认**。您必须输出一条解释端点或模型删除不可逆性质的文本消息，并要求用户在执行删除命令前输入 "I confirm" 或 "Yes, delete it"。

> [!IMPORTANT]
>
> **始终输出完整的文本响应（永远不要输出空文本）**：在执行任何工具调用（例如 `:deploy` API 调用、`gcloud ai endpoints delete`、`gcloud ai endpoints list` 或状态检查）后，您必须制定并返回一个完整、信息丰富的文本响应给用户。明确报告操作 ID、端点名称/ID、错误消息或资源列表。
> **永远不要在空文本或沉默中结束回合**。

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

要查看特定模型支持哪些机器类型和加速器，请将 `models list` 输出中获得的 `MODEL_ID` 传递给以下命令。将下面的 `<PUBLISHER>/<FAMILY>@<VERSION-ID>` 替换为目录输出中的确切字符串——占位符故意不是真实的模型 ID：
```bash
gcloud ai model-garden models list-deployment-config \
    --model="<PUBLISHER>/<FAMILY>@<VERSION-ID>"
```

> [!NOTE] 某些模型，尤其是 Hugging Face 模型，在部署时可能需要 Hugging Face 访问令牌。

> [!TIP] **模型推荐说明**：每当您准备在响应中命名特定模型版本时，请勿从记忆中推荐。这适用于以下所有情况——不仅限于直接部署请求：
>
> *   用户要求部署模型但未命名。
> *   您在 `list`、`describe` 或 `undeploy` 操作后提供下一步建议（例如 "您想将 `<model>` 部署到此端点吗？"）。
> *   用户询问一般性问题 "我应该使用什么？" / "X 适合什么模型？"。
> *   您在向用户展示的示例命令中填写 `MODEL_ID` 值（相对于 `<PUBLISHER>/<FAMILY>@<VERSION-ID>` 等占位符）。
>
> 新模型版本经常发布，旧版本可能会被弃用，因此训练语料库中关于哪些模型存在的知识不可靠。请遵循以下步骤：
>
> 1.  **澄清用例**，如果上下文不明确（任务类型、质量与延迟与成本优先级、硬件/配额限制、许可证限制）。如果用户已给出足够信号，则跳过。
> 2.  **使用 `gcloud ai model-garden models list` 查询实时目录**。在适当的情况下使用 `--filter` 进行缩小（例如 `--filter="name~gemma"`、`--filter="name~llama"`、`--filter="name~qwen"`、`--filter="name~deepseek"`）。在您看到此项目目录输出中的特定模型版本之前，永远不要向用户命名。
> 3.  **选择符合用例的家族中最新的一般可用版本**。当存在多个大小变体时，选择与用户的硬件/成本容忍度匹配的那个。优先选择较新的主版本而不是较旧的版本，除非它被标记为预览/实验性，并且用户明确要求稳定选项。
> 4.  **在命名响应中引用确切模型 ID 之前，使用 `gcloud ai model-garden models list-deployment-config --model="<publisher>/<family>@<version>"` 验证该模型是否可部署**。
> 5.  **在推荐中逐字引用模型 ID**，与目录中完全相同。不要将其意译为家族标签（"Gemma"、"Llama"）。
>
> §3 示例中的 `MODEL_ID` 值是故意非实质性的占位符（`<PUBLISHER>/<FAMILY>@<VERSION-ID>`）。不要用记忆中的用户面模型名称替换它们——始终首先重新运行步骤 2-4，然后引用目录中的确切字符串。

## 2.1 区域可用性检查（仅限 Gemini + LoRA）

> 对于第一方 Gemini 或 LoRA 部署，您必须在继续之前验证区域可用性。使用 `load_skill_resource(skill_name='agent-platform-deploy', file_path='references/region_availability.md')` 加载完整说明。
>
> **跳过此步骤**对于开放权重模型（Gemma、Llama、DeepSeek、Qwen）和 Gemini 调优模型——它们没有按区域发布端点限制。直接进入 §3。

## 3. 部署模型

> [!WARNING] 部署模型，尤其是大型模型，会消耗大量计算资源并产生费用。
>
> 1.  您 **必须** 在提议部署之前计算请求的 `--machine-type` 的每小时 $ 估计。按顺序尝试以下来源，在失败时传递到下一个：
>
>     -   运行 `scripts/calculate_cost.py`。加速器类型和数量在 Model Garden 中每个机器类型都是固定的，并自动派生。示例：
>
>     ```bash
>     python3 scripts/calculate_cost.py \
>         --machine-type=g2-standard-48
>     ```
>
>     如果脚本以非零状态退出（未知 `--machine-type`——模型花园目录中的机器是常规状态，但尚未在价格快照中，例如今天的 A4/B200），则传递到下一个来源。不要编造数字。
>
>     -   落回
>         [代理平台预测定价](https://cloud.google.com/products/gemini-enterprise-agent-platform/pricing?hl=en#prediction-and-explanation) 如果上述来源未产生数字。直接从该页面读取加速器 + 每小时费率，并在向用户提供的估计中引用 URL。
>
> 2.  您 **必须** 向用户展示此成本估计，并警告他们这是 **列表价格**，由于潜在的折扣、预留或非 `us-central1` 区域，可能与他们的实际账单不同。
> 3.  您 **必须始终** 在执行任何 `deploy` 命令之前请求用户同意估计成本。

要部署开放权重 Model Garden 模型，请直接使用 `curl` 调用 `:deploy` API。

如果部署因配额被拒绝，请逐字报告 API 的错误。

> [!IMPORTANT]
>
> -   **成本推回与硬件重新协商**：如果用户对成本提出异议（例如，“太贵了，你能尝试更小的配置吗？”），或请求无效或不支持的硬件组合（例如 `g2-standard-48g` 与 4x H100 GPU），请清楚地解释约束或无效性，检查 `list-deployment-config` 以确定支持的替代方案（例如 `g2-standard-24` 与 2x L4 或 `g2-standard-12` 与 1x L4），使用单个查询计算其成本估计，并在同一响应中 **立即渲染该推荐配置的完整 M 级预运行确认卡片**。
> -   **区域切换与配额耗尽**：当部署因请求区域的配额或容量不足而失败时（例如 `QUOTA_EXCEEDED` 或 `RESOURCE_EXHAUSTED`），确定一个替代支持的区域（例如 `us-east4` 或 `us-east1`），使用单个查询计算其成本估计，并在同一响应中 **立即渲染带有新 `--region` 和确切命令的完整 M 级预运行确认卡片**。直接说明替代区域，不要做出未经证实的容量声明。
> -   **高效工具执行（无冗余调用）**：如果模型 ID、区域或硬件配置已知或已解决，请不要执行冗余的 `models list`、`list-deployment-config` 或 `--help` 命令。严格一次运行每个发现命令。
> -   **单一状态检查与响应格式化（关键）**：
>     -   当启动部署（§3 中的 `:deploy` 调用）时，响应立即返回一个长时间运行的操作。**立即制定并返回您的文本确认响应，包括操作 ID 和端点显示名称**。不要在部署启动的同一轮中调用 `operations describe`。
>     -   当用户明确要求检查部署状态时（例如，“请检查部署状态”或“你能检查部署是否完成吗？”）：
>         -   **永远不要运行 `sleep` 命令、`while` 循环或重复轮询调用**。
>         -   严格一次执行 `gcloud ai operations describe <OP_ID> --region=<REGION>`。
>         -   **始终输出完整的文本响应**，报告操作状态（例如，“部署操作 `projects/.../operations/...` 目前正在进行 / 运行（创建于 `...`）。异步模型部署通常需要 10–15 分钟才能完成”）。
>         -   只有在状态检查确认端点已准备好服务时，才继续发送测试预测。
> -   **字母数字项目 ID**：始终为 `--project` 指定字母数字项目 ID（例如 `my-gcp-project`），而不是数字项目编号（例如 `123456789012`）。如果给定数字项目编号且其项目 ID 不可用，请将编号放在完全限定的资源名称内，例如 `gcloud ai endpoints list --region=projects/123456789012/locations/us-central1`，或作为位置资源 `gcloud ai endpoints describe projects/123456789012/locations/us-central1/endpoints/<ENDPOINT_ID> --region=us-central1`。如果命令仍然因 `core/project` 设置为项目编号而被拒绝，则沙盒自己的项目被种子为编号：然后每个 `gcloud ai` 调用都需要显式 `--project=<PROJECT_ID>`，资源名称无法替代它。报告该问题，而不是重试。
> -   **有效用户指定硬件优先级**：当用户指定一个明确的、有效的硬件配置（例如 `g2-standard-96` 与 8 个 `NVIDIA_L4` GPU，或 `g2-standard-12` 与 1 个 `NVIDIA_L4` GPU）时，在预运行预览和成本估计中尊重该请求的配置，而不是用默认推荐覆盖它。但是，如果请求的配置 **无效或不受支持**（例如 GPU 数量不匹配，如 `g2-standard-12` 与 2 个 L4 GPU，或不存在的主形），请遵循上述 **成本推回与硬件重新协商** 规则：清楚地解释无效性，确定支持的替代方案（例如 `g2-standard-24` 与 2 个 L4 GPU），计算其成本，并立即呈现有效替代方案的确认卡片。
> -   **端点显示名称**：如果用户指定或请求端点名称或显示名称（例如 `'usersim-gemma-eval-...'`），您必须始终在 `deploy` 命令中包含 `--endpoint-display-name="<NAME>"`。

### 示例：从模型花园部署开放权重模型

这是一个典型的 bash 脚本，用于部署模型。您可以直接运行此块。

```bash
#!/bin/bash
# 示例脚本：从模型花园部署开放权重模型。
#
# 注意：以下 MODEL_ID 是占位符，不是真实模型 ID。在运行此脚本之前，用 `gcloud ai model-garden models list`（见 §2）中的值替换它，并且不要将占位符回传给用户作为推荐的模型。

PROJECT_ID=$(gcloud config get-value project)
LOCATION_ID="us-central1" # 推荐默认区域
# 用 `gcloud ai model-garden models list` 中的确切 ID 替换占位符：
MODEL_ID="<PUBLISHER>/<FAMILY>@<VERSION-ID>"

echo "正在将模型 $MODEL_ID 部署到项目 $PROJECT_ID 中的 $LOCATION_ID..."

# API 使用资源名称作为模型，而目录 ID 是 "<PUBLISHER>/<FAMILY>@<VERSION-ID>"。按第一个 "/" 分割以转换。
PUBLISHER_MODEL="publishers/${MODEL_ID%%/*}/models/${MODEL_ID#*/}"

# 完全省略 deployConfig 以选择推荐的默认配置。
# 包含支持字段的完整请求。返回长时间运行的操作，因此这本质上是无同步的。
curl -sS -X POST \
    "https://${LOCATION_ID}-aiplatform.googleapis.com/v1beta1/projects/${PROJECT_ID}/locations/${LOCATION_ID}:deploy" \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json" \
    -d "{
      \"publisherModelName\": \"${PUBLISHER_MODEL}\",
      \"modelConfig\": {
        \"acceptEula\": true
      },
      \"endpointConfig\": {
        \"endpointDisplayName\": \"my-open-model-deployment\"
      },
      \"deployConfig\": {
        \"dedicatedResources\": {
          \"machineSpec\": {
            \"machineType\": \"g2-standard-12\",
            \"acceleratorType\": \"NVIDIA_L4\",
            \"acceleratorCount\": 1
          },
          \"minReplicaCount\": 1
        }
      }
    }"

echo "部署已异步启动。"
```

响应是一个 `GoogleLongrunningOperation`。其 `name` 字段是完整的操作路径，`projects/<PROJECT>/locations/<REGION>/operations/<OP_ID>`；§4 接受该路径或裸 `<OP_ID>`。

-   部署需要身份验证的受限制 Hugging Face 模型时，请设置 `modelConfig.huggingFaceAccessToken`。
-   如果使用保留计算资源，请设置 `deployConfig.dedicatedResources.machineSpec.reservationAffinity`。

### 1P 调优模型跨区域复制和部署

> 查看详细的调优模型复制和部署工作流程，请加载 `load_skill_resource(skill_name='agent-platform-deploy', file_path='references/copy_deploy_guide.md')`。该指南涵盖了执行顺序、复制/部署/删除命令的层级分配、硬件重新协商、测试预测验证以及进行中的操作锁。

## 4. 检查部署状态

§3 中的 `:deploy` 调用本身是异步的——没有标志可以传递——并返回一个长时间运行的操作，其 `name` 是操作 ID。您可以使用该 ID 检查部署的进行状态。

```bash
gcloud ai operations describe YOUR_OPERATION_ID \
    --region=$LOCATION_ID
```

> [!IMPORTANT]
>
> **仅执行单次状态检查（禁止休眠/轮询循环）**：模型部署操作需要 10-30 分钟。绝对不要运行 `sleep` 命令（例如 `sleep 45 && ...`）或在轮次中重复循环 `operations describe`。必须**严格执行一次** `gcloud ai operations describe`。如果 `done` 为 `false`，请立即将操作 ID 和进行中的状态返回给用户，并解释部署需要 10-15 分钟。

注意：大型模型（大约 20B+ 参数）可能需要 15-20 分钟才能完全部署并开始服务。

### 验证部署

如果模型成功部署，请通过进行预测调用来进行验证。由于 Model Garden 模型通常部署到专用端点，因此您不应使用 `gcloud ai endpoints predict`。相反，您必须获取端点的专用 DNS 名称并发送 `curl` 请求。

> [!TIP] 鼓励用户尝试使用自己的提示来查看结果。否则使用默认提示。

使用以下脚本：

```bash
#!/bin/bash
PROJECT_ID=$(gcloud config get-value project)
LOCATION_ID="us-central1"
ENDPOINT_ID="YOUR_ENDPOINT_ID"
PROMPT=${1:-"用简单的语言解释量子计算。"}

echo "获取专用端点 DNS..."
ENDPOINT_URL=$(gcloud ai endpoints describe $ENDPOINT_ID \
    --project=$PROJECT_ID \
    --region=$LOCATION_ID \
    --format="value(dedicatedEndpointDns)")

if [ -z "$ENDPOINT_URL" ]; then
    echo "错误：无法检索 $ENDPOINT_ID 的专用端点 URL。"
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

## 5. 退订和清理

> 查看完整的退订和清理流程（查找端点、退订模型、删除端点、删除模型），请加载 `load_skill_resource(skill_name='agent-platform-deploy', file_path='references/undeploy_guide.md')`。

> [!WARNING] 如果未退订模型，即使您未发送预测请求，也会持续为分配的计算资源付费。测试后务必清理。

## 6. 故障排除

> 查看如何解决配额/资源耗尽错误和硬件回退问题，请加载 `load_skill_resource(skill_name='agent-platform-deploy', file_path='references/troubleshooting.md')`。
