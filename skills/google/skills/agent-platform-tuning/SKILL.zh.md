---
name: agent-platform-tuning
description: 代理平台模型调优。当您需要使用代理平台基础设施对开放模型或Gemini模型进行微调时使用。不要用于代理平台外的模型训练、模型部署到端点（使用`agent-platform-deploy`）或管理服务端点（使用`agent-platform-endpoint-management`）。
---

# 代理平台模型调优

## 概述

此技能为使用代理平台的调优服务对大型语言模型（包括开源模型和Gemini模型）进行微调提供程序化知识。它涵盖了从环境设置和数据准备到作业配置、监控和部署的整个生命周期。

## 工作流决策树

1.  **项目与区域验证检查**：用户是否提供了Google Cloud项目和区域？

    -   **否** → **立即停止工具执行**。不要运行验证命令（`gcloud services list`，`gcloud projects get-iam-policy`），不要创建资源，不要开始数据集准备。提示用户指定或确认项目和区域（例如，“您希望使用哪个Google Cloud项目和区域？”）。
        -   如果用户的查询仅用于检查或验证环境就绪情况（API、IAM、服务代理），请仅询问项目和区域。不要询问模型类别。
        -   如果用户正在请求调优工作流，并且还遗漏了他们是否想要调优开源模型或Gemini模型，您可以同时询问这两个问题。
    -   **是** → 继续。

2.  **模型类别识别**：用户是否明确表示他们想要调优**开源模型**还是**Gemini模型**？

    -   **否** →
        -   **环境验证查询的例外情况**：如果用户仅询问检查或验证环境、API、IAM权限或服务代理是否就绪以进行调优，不要询问模型类别。在知道项目和区域后验证环境并确认就绪。
        -   否则，**停止工具执行**。询问用户他们是否想要调优开源模型或Gemini模型。**一般设置和先决条件查询（例如，“需要哪些环境设置？”）**：如果用户询问开始微调所需的环境设置、先决条件、API或权限，并且尚未选择模型类别：
        *   描述设置要求（API、IAM权限/服务代理和Python SDK）。
        *   关于云存储：说明需要一个现有的云存储桶来存储数据集和工件（例如，`gs://<existing-bucket>`）。**关键**：不要指示用户创建桶，不要在设置说明中输出`gcloud storage buckets create`命令，并且不要假设一个不存在的桶存在（用户可能没有桶创建权限，并将提供他们自己的现有桶）。
        *   您必须明确地在您的响应中询问他们是否想要调优**开源模型**或**Gemini模型**。在继续之前，永远不要在没有询问模型类别选择的情况下提供设置说明。
            （注意：如果他们要求主动检查或验证一个ID或区域缺失的项目，请先询问项目和区域，而不要运行工具调用）。
    -   如果用户提供了一个具体的调优目的，您应该推荐三个模型：一个开源模型，一个Gemini模型，以及一个第三种通常推荐的选项。简要列出每个模型的优缺点（例如，Gemini模型可能更贵等）。**关键**：您必须在此步骤中阅读`references/models.md`，并且仅推荐该目录中明确列出的模型。永远不要推荐未编目或不支持的模型，如`google/gemma-2-9b-it`、`gemma-2`或`Mistral`——仅推荐支持的模型，如Gemma 3（`google/gemma3@gemma-3-12b-it`）、Qwen 3（`qwen/qwen3@qwen3-8b`）或Llama 3.1（`meta/llama3_1@llama-3.1-8b`）。对于Gemini模型，仅推荐`gemini-2.5-flash`（推荐用于一般/编码/聊天）或`gemini-2.5-pro`。永远不要推荐`gemini-1.5-flash-002`、`gemini-1.5-pro-002`或`gemini-1.5-flash`，这些已弃用且不由调优服务支持。如果用户指定了一个目录中不存在的模型，请遵循该目录中的回退规则。在确认类别之前，不要进行模型配置。
    -   **是** → 继续。

3.  **环境检查**：环境（认证、API、IAM、虚拟环境）是否已初始化？

    -   **否** → 转到[阶段0：环境与IAM设置](#phase-0)。
    -   **是** → 继续。

4.  **数据集状态**：数据集是否以JSONL格式准备好，**其结构是否有效用于调优**，并且是否已上传到Google Cloud Storage？

    ```
    -   **否** → 转到[阶段1：数据集准备和上传](#phase-1)。
    -   **是** → 继续。
    ```

5.  **列选择确认**：您是否向用户展示了列并确认了映射？

    -   **否** → **停止**。您必须在阶段1.0中如描述的那样向用户展示样本并获取他们对列映射的确认，然后才能继续。
    -   **是** → 继续。

6.  **配置**：用户是否提供了目标模型和超参数，或明确同意了您的建议？

    -   **否** → 转到
        [阶段2：模型配置和建议](#phase-2)。
    -   **是** → 继续。

7.  **作业状态**：调优作业是否已提交？

    ```
    -   **否** → 转到
        [阶段3：调优作业执行](#phase-3-tuning-job-execution)。
    -   **是** → 继续。
    ```

8.  **作业完成**：调优作业是否完成？

    ```
    -   **否** → 转到 [阶段4：监控](#phase-4-monitoring)。
    -   **是** → 继续。
    ```

9.  **部署**：是否已部署调优模型（如果需要）？

    ```
    -   **否** → 转到 [阶段5：模型部署](#phase-5-model-deployment)。
    -   **是** → 任务完成。
    ```

## 阶段0：环境与IAM设置 {#phase-0}

在继续之前，确保基础环境已就绪。

### 0.1 认证与项目上下文

-   检查是否安装了`gcloud` CLI。如果未安装，提示用户在继续之前授予安装权限。如果已安装，请更新它：

```bash
gcloud components update --quiet > /dev/null 2>&1
```

-   验证`gcloud auth list`。如果未认证，请运行`gcloud auth login`。
-   **项目与区域定位**：检查用户是否在提示中指定了他们的GCP项目和区域。如果用户的提示遗漏了项目或区域（例如，在环境验证或设置请求中），您**必须立即停止工具执行，而不要运行任何bash或gcloud命令**（不要调用`gcloud config get project`或`gcloud services list`）。请用户提供他们的项目ID/编号和区域。
-   一旦项目和区域由用户提供或由用户确认，请验证`gcloud`是否已认证，并执行只读检查以验证环境。在报告环境就绪情况时，您的摘要必须明确详细说明所有三个类别的状态：
    1.  **所需API**：明确报告`aiplatform.googleapis.com`（代理平台）和`storage.googleapis.com`（云存储）都已启用。
    2.  **用户/调用者IAM权限**：明确确认用户身份或默认计算服务账户具有`roles/aiplatform.user`和`roles/storage.admin`（或`roles/storage.objectAdmin`）。
    3.  **服务代理与角色**：明确报告代理平台服务代理（`service-PROJECT_NUMBER@gcp-sa-aiplatform.iam.gserviceaccount.com`）具有`roles/aiplatform.serviceAgent`，并且调优服务代理（`service-PROJECT_NUMBER@gcp-sa-vertex-moss-ft.iam.gserviceaccount.com`或`gcp-sa-vertex-tune`）具有`roles/aiplatform.tuningServiceAgent`。始终明确说明已验证的项目和区域（例如，`project: <PROJECT_NUMBER>, region: us-central1`），并明确确认环境已完全配置并准备好进行调优。

### 0.2 位置

位置处理**取决于您在工作流决策树中建立的模型类别**。这两个类别具有不同的支持位置——永远不要将一个类别的位置应用于另一个类别。

-   **开源模型**共享一个固定的位置集，`global`是推荐的选择。
-   **Gemini模型**每个模型都不同，必须查找。今天`global`不被接受。

如果用户指定了一个对他们模型和类别无效的位置，停止。用错误消息命名请求的位置为不支持，列出有效的位置，并且不要询问数据集，不要进行任何其他设置步骤，并且不要在其他地方静默重试。

#### 开源模型（推荐：`global`）

**推荐`global`并确认**。将其作为一个单一推荐选项提出，而不是让用户先选择一个区域，并且不要引导他们选择一个特定区域。

这些是开源模型调优可用的唯一位置：

-   `global`（推荐选择）
-   `us-central1`
-   `europe-west4`
-   `us-west1`
-   `us-east5`
-   `asia-southeast1`

`global`端点会自动选择一个有可用容量的支持区域，因此它更有可能成功调度。提前锁定区域会限制该区域的能力，这就是为什么`global`是开源模型调优推荐位置的原因。

-   **用户指定了一个位置** → 原样使用它，前提是它是`global`或上面列出的区域之一。不要说服他们放弃。
-   **用户询问哪些位置受支持** → 回答这个问题。分享上面的列表，并说明为什么推荐`global`。永远不要隐瞒它。
-   **用户没有指定位置** → 提出并要求他们确认`global`，然后再继续。说明`global`允许服务选择一个有可用容量的区域。不要静默假设`global`。

提出单一选择的目的在于避免让区域选择成为用户必须先解决的决策——这种顺序是之前阻止人们的原因。这不是隐藏列表的理由：每当用户询问时，都要引用它，并且在拒绝不受支持的位置时也要引用它。

仅在以下情况下回退到明确区域，并告诉用户您这样做的原因：

-   **CMEK**。客户管理加密密钥在`global`上被拒绝，并返回`FAILED_PRECONDITION`错误。受CMEK保护的作业必须指定包含密钥的区域。

-   **数据驻留**。如果用户要求作业停留在特定司法管辖区，请尊重他们的区域。`global`目前运行作业在`us-central1`或`europe-west4`。

如果接受`global`作业，但随后因模型不支持全局端点调优而出现`FAILED_PRECONDITION`错误，则该模型尚未加入全局端点。模型本身仍然可调优：稍后在上述列表中的明确区域（`us-central1`是安全的选择）中重新提交，并告诉用户您切换的原因。

##### 与`global`作业一起工作

-   API主机保持`aiplatform.googleapis.com`。没有`global-aiplatform.googleapis.com`主机。
-   服务在运行时将`global`解析为实际区域。子资源（调优模型、检查点、TensorBoard）会带有该**实际**区域在其资源名称中，而不是`global`。在使用它进行监控或部署之前，从返回的资源名称中读取位置；永远不要假设它仍然是`global`。
-   配额跨区域共享，因此固定区域不会提供额外配额。

#### Gemini模型（按模型查找）

今天`global`**不被接受用于Gemini调优**——服务在作业创建时拒绝它，因此不要在这里建议它。

**没有单个区域允许列表用于Gemini**。支持调优的区域因模型和模型版本而异：一些Gemini模型仅限于两个区域，而其他模型支持更多区域。不要重用上面的开源模型列表，也不要假设一个区域会从另一个Gemini模型继承。

在提交之前，在监督微调文档中查找所选模型，并阅读其**“支持调优端点”**行：
[supervised tuning](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/tuning/supervised-tuning)

-   **用户询问哪些区域受支持** → 查找该特定模型并告诉他们文档中说明了什么。不要凭记忆或从开源模型列表回答，也不要为不同的Gemini模型回答。
-   **该行的名称指定了特定区域** → 用户的区域必须是其中之一。如果不是，停止并报告该模型支持的区域。
-   **该行缺失或文档不明确** → 与其猜测一个区域，不如询问用户区域。

在继续之前与用户确认区域。请注意，一些Gemini模型也限制CMEK，并且仅在`us`和`eu`多区域端点上提供调优模型，因此在进行承诺之前，请检查同一表格中的这些限制。

### 0.3 启用API

确保`aiplatform.googleapis.com`和`storage.googleapis.com`已启用。

```bash
gcloud services enable aiplatform.googleapis.com storage.googleapis.com \
    --project=YOUR_PROJECT
```

### 0.4 IAM权限

验证以下身份具有所需的角色。

-   **代理平台服务代理**：
    `service-PROJECT_NUMBER@gcp-sa-aiplatform.iam.gserviceaccount.com`
-   **托管开源微调服务代理**：
    `service-PROJECT_NUMBER@gcp-sa-vertex-moss-ft.iam.gserviceaccount.com`
-   **用户身份**：运行命令的帐户。

### 0.5 Python依赖项

此技能中的脚本导入`vertexai`（来自`google-cloud-aiplatform`）、`google-genai`、`google-cloud-storage`和`datasets`。

**关键代理指令**：**不要**创建虚拟环境，并且在检查之前不要安装任何内容。虚拟环境是空的，它会隐藏环境已经提供的包，从而强制进行冗长的几分钟安装。

先探测，如果探测失败再安装：

```bash
python3 -c "import vertexai, google.genai, google.cloud.storage, datasets" \
  || pip install -r references/requirements.txt
```

然后使用纯`python3 scripts/...`运行每个脚本——不要有激活前缀。

`references/requirements.txt`的固定是针对一个环境不提供这些SDK的回退。不要在已工作的环境上应用它们：它们会降级其他工具可能共享的包。

## 阶段1：数据集准备和上传 {#phase-1}

### 1.0 数据集发现和确认

-   **用户提供的 datasets 验证：** 如果用户在提示中指定了 datasets 文件名或路径，请在工作区中验证其存在性（例如，通过脚本执行或检查拼写错误）。
    *   **如果文件在任何地方都找不到**，你必须告知用户 datasets 文件不存在或无法访问。你必须提示用户提供有效的 datasets 路径。或者，如果在搜索工作区期间找到候选 datasets 文件，你必须向用户展示这些候选文件并让他们选择一个。在报告缺失文件或展示候选文件后，你必须立即停止工具执行，并等待用户的回复。不要请求 90/10 验证拆分权限，在收到用户关于有效 datasets 文件选择的确认之前，不要尝试上传 datasets。
    *   **如果文件找到并验证通过**，请继续执行下方的 1.1 格式化 & 验证步骤。

-   **自动发现：从用户存储桶：** 如果用户没有 datasets，并且在 Hugging Face 参考中找不到合适的替代方案，请提供搜索用户的 GCS 存储桶以查找潜在训练数据的选项。优先搜索具有 `.jsonl`、`.json`、`.csv` 和 `.parquet` 等扩展名的文件。如果找到这些文件，请读取每个文件的前几行/记录，以确定它们是否包含适合微调的基于文本的数据（例如，提示/完成对），这些数据可以修改以遵循 [数据准备指南](references/data_prep.md) 并与请求的微调任务相关。**在提示之前不要搜索。**

-   **自动发现：从任务到 Huggingface：** 如果用户有特定任务（例如数学推理、编码、指令跟随）或想要使用 Hugging Face datasets 而不指定特定名称，请参考 [Huggingface Datasets 参考](references/hf_datasets.md) 并推荐匹配的 datasets（例如，用于数学推理的 `open-r1/OpenR1-Math-220k` 或 `AI-MO/NuminaMath-TIR`；`openai/gsm8k` 也广泛使用）。对于每个推荐的 datasets，提供一些关于 datasets 的信息，并提供一些合理的拆分，并要求用户选择一个。不要输出通用的指示，告诉用户准备和上传他们自己的数据——主动引导交互式 datasets 发现、预览和准备流程。

    > [!IMPORTANT] **关键：请求确认和列选择。** 一旦选择了 datasets，请通过 `run_command` 执行 Python，使用 `load_dataset(..., streaming=True)` 检查 datasets。在执行 datasets 准备或上传之前，你必须执行以下步骤并得到用户确认：1. **datasets 和拆分确认：** 向用户展示 datasets 和可用的拆分，并让他们确认要使用哪个。2. **列选择（Hugging Face 或自定义 datasets）：** 你必须：- 提供所选 datasets 拆分中所有可用列的列表。- **展示 datasets 的一些样本**，以帮助用户理解内容并做出列选择。- 推荐哪些列应该映射到 `prompt`（或用户消息）和 `completion`（或助手回复），如果适用，提供几个合理的选项。- 请求用户确认列映射或指定要使用的列。

### 1.1 格式化 & 验证

-   **转换：** 如果数据是 CSV、JSON 或 Parquet，使用 `scripts/prepare_dataset.py` 进行转换。
-   **验证拆分确认：** 每次生成或准备单个 datasets 而没有显式验证集（包括生成样本聊天/指令 datasets 或准备训练 datasets 时），你必须使用 Python 通过 `run_command` 生成或处理数据，并且**你必须提示用户**寻求权限将训练 datasets 90/10 拆分为验证 datasets（使用 `--validation_split 0.1` 或 Python 脚本）。如果他们同意，请继续拆分。如果他们拒绝，只需使用训练 datasets 而不使用验证 datasets。不要提供 80/20 拆分；微调服务拒绝它，原因在 [数据准备指南](references/data_prep.md#sizing-the-validation-split) 中给出。在询问用户关于 90/10 验证拆分之前，不要继续上传 datasets 或提交微调作业！
-   **验证：** 如果数据已经是 JSONL 格式，在上传之前验证它。仅仅有 `.jsonl` 扩展名是不够的。你必须验证内容模式是否有效，可以用于微调（例如，正确的系统/用户/模型角色）。

```bash
python3 scripts/prepare_dataset.py \
    --input my_data.jsonl \
    --format <messages|messages_gemini> \
    --validate_only
```

*(使用 `--format messages` 对于 open 模型，使用 `--format messages_gemini` 对于 Gemini 模型。)* - 参考 [数据准备指南](references/data_prep.md) 了解所需的模式。

### 1.2 上传

使用唯一目录（例如，带有日期时间戳）将格式化的 `.jsonl` 文件上传到 GCS，以避免覆盖不同运行产生的输出。如果用户命名了存储桶（例如，`gs://mybucket`），请使用用户提供的存储桶名称（逐字）作为确切的名称，并且永远不要添加项目 ID 或修改存储桶名称。

```bash
ARTIFACTS="gs://YOUR_BUCKET/tuning_agent_job_<datetime>/dataset.jsonl"
gcloud storage cp dataset.jsonl "$ARTIFACTS"
```

## Phase 2: 模型配置 & 推荐 {#phase-2}

帮助用户选择最佳模型和参数。**在提交作业之前，始终请求用户确认。**

-   如果用户在提示中没有指定特定模型，根据 **模型目录** 计算推荐。
-   **请求确认：** 向用户展示推荐的模型，并在配置超参数之前请求他们的确认。

### 2.1 配置

#### 对于 Open 模型

-   根据 [微调指南](references/tuning_guide.md) 和 [模型目录](references/models.md) 中的模型特定基线，推荐 `tuning_mode`、`epochs`、`learning_rate` 和 `adapter_size`。

#### 验证实时模型 ID

在提交作业之前，运行 `scripts/list_models.py` 并仅从其 `models` 输出中选择 `--base_model`。不要编造 IDs 或版本号。

```bash
python3 scripts/list_models.py --project YOUR_PROJECT --filter gemini
```

输出: `{"models": [...], "total_count": N, "truncated": bool}`。

-   对于 Gemini，删除 `google/` 和 `@default`（例如。`google/gemini-2.5-flash@default` → `gemini-2.5-flash`）；对于 open 模型，按 `publisher/family@version` 的形式原样传递。
-   跳过以 `-embedding`、`-tts`、`-image`、`-computer-use` 或 `-native-audio` 结尾的 Gemini 变体；它们不可微调。
-   如果 `truncated` 为 `true`，在决定目标版本不可用时，请使用更严格的 `--filter` 重新运行（例如。`gemini-2.5`）。
-   如果 `models` 为空，停止并询问用户。

### 2.2 计算 Cost（仅限 Open 模型）

> [!WARNING] **关键：始终使用 `run_command` 与 `scripts/calculate_cost.py`** 不要调用 `estimate_cost` ADK 工具进行模型微调。`estimate_cost` 工具仅支持特定端点服务定价，在微调请求上会失败，显示 `Unsupported request type`。你必须调用 `run_command` 工具执行 Python 代码或 `scripts/calculate_cost.py`（或 `/workspace/skills/agent-platform-tuning/scripts/calculate_cost.py`）来计算成本。每当选择模型或用户切换模型（例如，从 Llama 切换到 Gemma）时，你必须调用 `run_command` 来计算或重新计算成本，然后再展示干运行确认提示。始终在干运行确认提示中报告计算出的美元金额（例如。`Estimated tuning cost: $X.XX`）。

-   我们根据 [模型目录](references/models.md) 中的数据集和所选模型计算微调的估计成本：

    ```bash
    python3 scripts/calculate_cost.py \
        --input my_data.jsonl \
        --model MODEL_NAME \
        --tuning_mode TUNING_MODE \
        --epochs epochs
    ```

    `--model` 接受显示名称（`Qwen 3 8B`）或与传递给 `--base_model` 相同的资源名称（`qwen/qwen3@qwen3-8b`），因此可以在步骤 2.1 中选择相同的值。

> [!NOTE] **处理缺少 datasets 错误：** 如果 `scripts/calculate_cost.py` 因为 datasets 文件（例如。`my_data.jsonl` 或 `dummy_data.jsonl`）找不到而失败，你必须告知用户 datasets 文件不存在或无法访问。你必须提示用户提供有效的 datasets 路径，并立即停止工具执行以等待他们的回复。不要重试或循环，不要编造特定的成本数字，在收到用户提供的有效 datasets 之前，不要提示提交作业的批准。

-   **请求确认：** 向用户展示推荐的超参数配置和估计成本（使用上述计算的具体美元金额），并在继续提交作业之前请求他们的批准。确保注明估计成本只是一个估计，可能与实际账单成本有所不同。

## Phase 3: 微调作业执行 {#phase-3-tuning-job-execution}

**关键起飞前检查（GCS 验证）：** 在你提出确认提示或提交任何微调作业之前，你必须验证指定的训练 datasets GCS URI（例如。`gs://dummy_bucket/dataset.jsonl` 或 `gs://YOUR_BUCKET/...`）实际上存在并可访问。运行 `gcloud storage ls $DATASET_URI`（或 `gsutil ls`）。

*   **如果验证失败**（例如。`BucketNotFound`、`404`、`AccessDenied`，或指示存储桶为虚拟/缺失），你必须告知用户 GCS 存储桶或 datasets 不存在或无法访问。你必须提示用户提供有效的 GCS URI 用于 datasets，并立即停止工具执行以等待他们的回复。不要提出确认提示，在收到有效 datasets URI 之前，不要执行任何微调脚本。
*   **如果验证成功**，请继续执行下方的确认提示。

### 对于 Gemini 模型

使用 Python SDK（`google.genai` 或 `vertexai.tuning.sft`）提交 Gemini 监督微调作业：

```python
from google import genai
from google.genai import types

client = genai.Client(enterprise=True, project=PROJECT, location=LOCATION)
tuning_job = client.tunings.tune(
    base_model=BASE_MODEL,  # 例如。 "gemini-2.5-flash"
    training_dataset=types.TuningDataset(gcs_uri=TRAIN_DATASET_URI),
    config=types.CreateTuningJobConfig(
        epoch_count=EPOCHS,  # 例如。 3
        learning_rate_multiplier=LEARNING_RATE_MULTIPLIER,  # 例如。 1.0
        validation_dataset=(
            types.TuningValidationDataset(gcs_uri=VAL_DATASET_URI)
            if VAL_DATASET_URI
            else None
        ),
    ),
)
print("Tuning Job Resource Name:", tuning_job.name)
```

或者使用 `vertexai.tuning.sft`：

```python
import vertexai
from vertexai.tuning import sft

vertexai.init(project=PROJECT, location=LOCATION)
job = sft.train(
    source_model=BASE_MODEL,
    train_dataset=TRAIN_DATASET_URI,
    validation_dataset=VAL_DATASET_URI,
    epochs=EPOCHS,
    learning_rate_multiplier=LEARNING_RATE_MULTIPLIER,
)
print("Tuning Job Resource Name:", job.resource_name)
```

通过 `python3`（内联或写入 `/tmp/submit_gemini_tuning.py`）执行 Python 脚本。报告返回的操作名称或可跟踪的资源标识符，并且不要等待终端状态。

### 对于 Open 模型

使用 `scripts/tune_open_model.py` 或 Python SDK 提交 open 模型微调作业。使用可用模型文档在 [文档](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/open-model-tuning#supported-models) 中识别模型 ID。

`--base_model` 接受发布者模型 **资源名称** (`{publisher}/{model_id}@{version_id}`)，而不是目录中显示的显示名称。有关格式、验证示例以及如何查找你没有的名称，请参阅 `references/models.md` 中的“模型资源名称格式”。

使用 `scripts/tune_open_model.py`：

```bash
python3 scripts/tune_open_model.py \
    --project YOUR_PROJECT \
    --location global \
    --base_model BASE_MODEL_ID \
    --train_dataset gs://YOUR_BUCKET/tuning_agent_job_<datetime>/dataset.jsonl \
    --output_uri gs://YOUR_BUCKET/tuning_agent_job_<datetime>/output \
    --epochs EPOCHS \
    --learning_rate LR \
    --tuning_mode MODE
```

*(如果 `scripts/tune_open_model.py` 不在工作目录中，请直接使用 `python3 -c "..."` 运行 Python SDK 片段，或使用 `client.tunings.tune` 将其写入 `/tmp/submit_open_tuning.py`。)*

此脚本仅限 open 模型，并且如果省略，`--location` 会回退到 `global`。始终明确传递用户在 0.2 部分确认的位置，以便在您向用户展示用于批准的命令字符串中可见。

> [!WARNING] **`--output_uri` 对于 open 模型是必需的。** Python SDK 声明 `output_uri: Optional[str] = None`，但微调后端会拒绝省略此参数的 open 模型作业，显示 `INVALID_ARGUMENT: The output_uri field is required for this model.` 将 SDK 的“可选”签名视为错误，并始终传递 GCS 目标。

由于该标志是强制性的，因此在你提交之前必须确定微调模型写入的位置。**永远不要编造存储桶名称，从项目编号派生，或在未经提示的情况下运行 `gcloud storage buckets create`。** 创建存储桶是一个修改操作，并且受 Tier M 确认策略的约束。

-   **用户命名了存储桶或 URI** → 按用户指定的方式（逐字）使用它，并像在 1.2 部分中那样添加每个作业的唯一目录。**关键：** 永远不要更改、前缀或添加任何内容到用户指定的存储桶名称！即使 `gcloud storage buckets list` 显示具有项目前缀名称的现有存储桶（例如。`gs://PROJECT-mybucket` 当用户要求 `gs://mybucket`）时，你也必须逐字使用用户的确切存储桶名称 `gs://mybucket`。永远不要无声地替换现有存储桶。
-   **在 1.2 部分中为 datasets 上传已经使用了存储桶** → 提出重用它作为输出并询问用户确认。
-   **两者或用户表示他们没有存储桶** → 检查项目中的现有存储桶（`gcloud storage buckets list --project=PROJECT`）或提供创建专用存储桶的选项。当提出要创建的存储桶时，确保存储桶名称是唯一的，方法是包含唯一后缀或时间戳（例如。`gs://PROJECT-tuning-$(date +%s)` 或 `gs://PROJECT-tuning-artifacts-<timestamp>` 在 LOCATION）以防止与先前创建的存储桶的 HTTP 409 冲突。在你的配置干运行预览中提出目标存储桶，并在继续之前请求用户确认。

> [!IMPORTANT] **交互式确认需要（Tier M）：** 在提交作业之前，你必须向用户展示显示所有字面标志的确认提示，并提供“是”和“否”选项。

> **关键：** 当向用户展示此确认提示时，你必须将其作为直接的纯文本响应输出，并立即停止工具执行。不要在同一轮中调用任何命令执行或交互式工具，因为意外的工具调用可能会被模拟 harness 自动回复，并导致无限循环。立即为用户的回复让步。

## Phase 4: 监控 {#phase-4-monitoring}

通过脚本输出中提供的 Cloud Console 链接来监控作业。
`--location` 是必需的，并且必须与您提交时使用的位置相同：一个在 `global` 上提交的开放模型作业会使用 `--location global` 进行轮询，即使实际工作在后台的某个真实区域运行。

此外，询问用户是否希望您在后台为他们监控作业状态。如果他们同意，请作为后台任务执行 `scripts/monitor_tuning_job.py` 以定期轮询作业状态并通知用户显示状态。如果用户拒绝，则完全由用户自行检查状态。

## 第 5 步：模型部署 {#phase-5-model-deployment}

一旦调优作业状态为 `SUCCEEDED`，就部署模型。

部署需要一个真实区域 — `--region=global` 在这里无效。如果作业在 `global` 上运行，请从调优模型的资源名称（`projects/.../locations/<REGION>/models/...`）中读取区域并部署在那里；不要猜测。

```bash
ARTIFACTS="gs://YOUR_BUCKET/tuning_agent_job_<datetime>/output/postprocess/node-0/checkpoints/final"
gcloud ai model-garden models deploy \
    --project=YOUR_PROJECT \
    --region=YOUR_LOCATION \
    --model="$ARTIFACTS" \
    --machine-type=MACHINE_TYPE \
    --accelerator-type=ACCELERATOR_TYPE \
    --accelerator-count=COUNT
```

> [!IMPORTANT] **交互式确认要求（等级 M）：** 在继续部署之前，您 **必须** 向用户展示一个确认提示，其中包含显示所有字面量标志的命令字符串，并提供“是”和“否”选项。

> **关键：** 在向用户展示此确认提示时，您必须将其作为直接的纯文本响应输出，并立即停止工具执行。不要在同一轮次中调用任何命令执行或交互式工具，因为意外的工具调用可能会被模拟框架自动回复，导致无限循环。立即让用户回复。

参考 [模型目录](references/models.md) 获取特定开放模型的硬件推荐。

## 资源

-   [数据准备指南](references/data_prep.md)
-   [模型目录](references/models.md)
-   [调优指南](references/tuning_guide.md)
-   `scripts/prepare_dataset.py`：数据转换 & 验证。
-   `scripts/tune_open_model.py`：开放模型调优作业提交。
