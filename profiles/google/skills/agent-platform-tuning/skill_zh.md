# 代理平台模型调优

## 概述

此技能为使用代理平台的调优服务对大型语言模型（包括开源模型和Gemini模型）进行微调提供了程序化知识。它涵盖了从环境设置和数据准备到作业配置、监控和部署的整个生命周期。

## 工作流决策树

1.  **模型类别识别**：用户是否明确表示他们想要微调开源模型还是Gemini模型？

    -   **否** → **停止**。询问用户他们是否想要微调开源模型或Gemini模型。**环境设置请求的严重异常**：如果用户专门要求环境设置说明（例如，“需要哪些环境设置？”），您**必须**在初始响应中提供完整的[阶段0环境设置](#阶段-0)说明，同时询问关于模型类别的澄清问题。
    -   如果用户提供了一个具体的微调目的，您应该推荐三个模型：一个开源模型、一个Gemini模型和一个第三种通常推荐的模型。简要列出每个模型的优缺点（例如，Gemini模型可能更贵等）。**严重**：您必须在此步骤中阅读`references/models.md`，并且仅推荐该目录中明确列出的模型。不要推荐不受支持的模型，如Mistral。如果用户指定了一个不在目录中的模型，请遵循该目录中的回退规则。在确认类别之前，不要进行模型配置。
    -   **是** → 继续。

2.  **环境检查**：环境（Auth、APIs、IAM、Venv）是否已初始化？

    -   **否** → 转到[阶段0：环境和IAM设置](#阶段-0)。
    -   **是** → 继续。

3.  **数据集状态**：数据集是否以JSONL格式准备好，**其结构是否有效用于调优**，并且是否已上传到Google Cloud Storage？

    ```
    -   **否** → 转到[阶段1：数据集准备和上传](#阶段-1)。
    -   **是** → 继续。
    ```

4.  **列选择确认**：您是否向用户展示了列并确认了映射？

    -   **否** → **停止**。您必须在第1.0阶段中展示样本并获取用户对列映射的确认，然后才能继续。
    -   **是** → 继续。

5.  **配置**：用户是否提供了目标模型和超参数，或明确同意您的建议？

    -   **否** → 转到[阶段2：模型配置和建议](#阶段-2)。
    -   **是** → 继续。

6.  **作业状态**：调优作业是否已提交？

    ```
    -   **否** → 转到[阶段3：调优作业执行](#阶段-3-调优作业执行)。
    -   **是** → 继续。
    ```

7.  **作业完成**：调优作业是否完成？

    ```
    -   **否** → 转到[阶段4：监控](#阶段-4-监控)。
    -   **是** → 继续。
    ```

8.  **部署**：是否已部署调优模型（如果需要）？

    ```
    -   **否** → 转到[阶段5：模型部署](#阶段-5-模型部署)。
    -   **是** → 任务完成。
    ```

## 阶段0：环境和IAM设置 {#阶段-0}

在进行下一步之前，确保基础环境已准备好。

### 0.1 身份验证和项目上下文

-   检查是否安装了`gcloud` CLI。如果没有安装，提示用户授权安装它，然后才能继续。如果已安装，请更新它：

```bash
gcloud components update --quiet > /dev/null 2>&1
```

-   验证`gcloud auth list`。如果未进行身份验证，请运行`gcloud auth login`。
-   确保`project`已知。使用`gcloud config get project`检索当前项目。
-   **严重**：请求确认。您必须提示用户在继续之前确认检索到的项目，以防他们想要切换到不同的项目。位置也必须确认——请参阅0.2节，了解应提议哪个位置，这取决于模型类别。

### 0.2 位置

位置处理**取决于您在工作流决策树中建立的模型类别**。这两个类别有不同的支持位置——永远不要将一个类别的位置应用于另一个类别。

-   **开源模型**共享一个固定的位置集，`global`是推荐的选择。
-   **Gemini模型**每个模型都不同，必须查找。今天`global`对它们不适用。

如果用户指定了一个对他们模型和类别无效的位置，停止。响应错误，命名请求的位置不受支持，列出有效位置，并且**不要**询问数据集，**不要**继续任何其他设置步骤，并且**不要**在其他地方静默重试。

#### 开源模型（推荐：`global`）

**推荐`global`并确认它**。将其作为一个单一推荐选择提出，而不是首先让用户选择一个区域，并且不要引导他们选择特定区域。

开源模型调优仅有的位置是：

-   `global`（推荐选择）
-   `us-central1`
-   `europe-west4`
-   `us-west1`
-   `us-east5`
-   `asia-southeast1`

`global`端点会自动选择一个有可用容量的支持区域，因此它更有可能成功调度。提前锁定区域会限制该区域的能力，这就是为什么`global`是开源模型调优推荐位置的原因。

-   **用户指定了位置** → 原封不动地使用它，前提是它是`global`或上面列出的区域之一。不要说服他们放弃。
-   **用户询问哪些位置受支持** → 回答这个问题。分享上面的列表，并说明为什么推荐`global`。永远不要隐瞒它。
-   **用户没有指定位置** → 提议`global`，并在继续之前请求他们确认。说明`global`让服务选择一个有可用容量的区域。**不要**静默地假设`global`。

提议单个选择的目的在于避免让区域选择成为用户必须解决的决策——这种顺序是之前阻止人们的原因。它不是隐藏列表的理由：每当用户询问时，都要引用它，并且在拒绝不受支持的位置时也要引用它。

仅在以下情况下回退到明确区域，并告诉用户您这样做的原因：

-   **CMEK**。在`global`上拒绝客户管理的加密密钥，并显示`FAILED_PRECONDITION`错误。受CMEK保护的作业必须指定包含密钥的区域。

-   **数据驻留**。如果用户要求作业停留在特定司法管辖区，请尊重他们的区域。`global`目前会在`us-central1`或`europe-west4`运行作业。

如果接受`global`作业，但随后出现`FAILED_PRECONDITION`错误，说明模型不支持全局端点调优，那么该模型尚未加入全局端点。模型本身仍然可调优：重新提交一次，使用上面列表中的明确区域（`us-central1`是最安全的选择），并告诉用户您切换的原因。

##### 与`global`作业一起工作

-   API主机保持为`aiplatform.googleapis.com`。没有`global-aiplatform.googleapis.com`主机。
-   服务在运行时解析`global`到一个真实区域。子资源（调优模型、检查点、TensorBoard）会带有该**真实**区域在其资源名称中，而不是`global`。在使用它进行监控或部署之前，从返回的资源名称中读取位置；永远不要假设它仍然是`global`。
-   配额跨区域共享，因此锁定区域不会提供额外的配额。

#### Gemini模型（按模型查找）

今天`global`**不适用于Gemini调优**——服务在作业创建时使用`FAILED_PRECONDITION`错误拒绝它，因此在这里不要提议它。

**没有单个Gemini区域允许列表**。支持调优的区域因模型和模型版本而异：一些Gemini模型仅限于两个区域，而其他模型支持更多区域。**不要**重复上面列出的开源模型列表，并且**不要**假设区域来自另一个Gemini模型。

在提交之前，查找所选模型在监督微调文档中的信息，并阅读其**“支持用于模型调优的端点”**行：
[supervised tuning](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/tuning/supervised-tuning)


-   **用户询问哪些区域受支持** → 查找该特定模型，并告诉他们文档中说明了什么。不要从记忆中或从开源模型列表中回答，并且不要为不同的Gemini模型回答。
-   **该模型的行指定了特定区域** → 用户的区域必须是其中之一。如果不是，停止并报告该模型支持的区域。
-   **该行的模型不存在或文档不清楚** → 与其猜测一个区域，不如请求用户提供区域。

在继续之前与用户确认区域。请注意，一些Gemini模型也限制CMEK，并且仅在`us`和`eu`多区域端点上提供调优模型，所以在承诺之前请检查同一表格中的这些限制。

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
-   **托管OSS微调服务代理**：
    `service-PROJECT_NUMBER@gcp-sa-vertex-moss-ft.iam.gserviceaccount.com`
-   **用户身份**：运行命令的帐户。

### 0.5 Python依赖项

此技能中的脚本导入`vertexai`（来自`google-cloud-aiplatform`）、`google-genai`、`google-cloud-storage`和`datasets`。

**严重代理指令**：**不要**创建虚拟环境，并且在检查之前**不要**安装任何内容。虚拟环境是空的，它会隐藏环境已经提供的包，从而强制执行冗长的几分钟安装。

首先探测，如果探测失败，再安装：

```bash
python3 -c "import vertexai, google.genai, google.cloud.storage, datasets" \
  || pip install -r references/requirements.txt
```

然后使用纯`python3 scripts/...`运行每个脚本——没有激活前缀。

`references/requirements.txt`的固定是针对不提供这些SDK的环境的回退。不要在正常工作环境中应用它们：它们会降级其他工具可能共享的包。

## 阶段1：数据集准备和上传 {#阶段-1}

### 1.0 数据集发现和确认

-   **用户提供的数据集验证**：如果用户在提示中指定了数据集文件名或路径，请验证其在工作区是否存在（例如，通过脚本执行或检查拼写错误）。
    *   **如果找不到文件**，您**必须**告知用户数据集文件不存在或无法访问。您**必须**提示用户提供有效的数据集路径。或者，如果在搜索工作区期间找到候选数据集文件，您**必须**向用户展示候选文件并让他们选择一个。您**必须**在报告丢失文件或展示候选文件后立即停止工具执行，并等待用户的响应。**不要**询问90/10验证拆分权限，并且**不要**在收到来自用户的有效数据集文件选择之前尝试上传数据集。
    *   **如果找到并验证了文件**，请继续到下面的1.1格式化和验证步骤。
-   **自动发现：从用户存储桶**：如果用户没有数据集，并且在Hugging Face参考中找不到合适的替代方案，请提议搜索用户的GCS存储桶以查找潜在的训练数据。优先搜索具有`.jsonl`、`.json`、`.csv`和`.parquet`等扩展名的文件。如果找到此类文件，请读取每个文件的前几行/记录，以确定它们是否包含适合调优的基于文本的数据（例如，提示/完成对），这些数据可以修改以遵循[数据准备指南](references/data_prep.md)并与请求的调优任务相关。**不要**在提示之前搜索。
-   **自动发现：从任务到Huggingface**：如果用户有特定任务，请参考[Huggingface Datasets参考](references/hf_datasets.md)并建议从中选择一个数据集（如果存在）。对于每个建议的数据集，提供一些关于数据集的信息并提供一些合理的拆分。 > [!IMPORTANT] > **严重**：请求确认和列选择。不要在执行数据集准备或上传之前执行以下步骤并获取用户确认： > 1. **数据集和拆分确认**：向用户展示数据集和可用的拆分，并让他们确认要使用的拆分。 > 2. **列选择（Hugging Face或自定义数据集）**：您必须： > - 提供所选数据集拆分中所有可用列的列表。 > - **向用户展示数据集的几个样本**以帮助他们理解内容并做出列选择。 > - 建议哪些列应映射到`prompt`（或用户消息）和`completion`（或助手响应），如果适用，提供几个合理的选项。 > - 请求用户确认列映射或指定要使用的列。

### 1.1 格式化和验证

-   **转换**：如果数据是CSV、JSON或Parquet，请使用`scripts/prepare_dataset.py`进行转换。
-   **验证拆分确认**：如果用户仅提供一个训练数据集，**您必须**提示用户寻求权限将训练数据集90/10拆分为验证数据集（使用`--validation_split 0.1`）。如果他们同意，请继续拆分。如果他们拒绝，只需使用训练数据集而不使用验证数据集。**不要**提供80/20拆分；调优服务会拒绝它，原因如[数据准备指南](references/data_prep.md#sizing-the-validation-split)中所述。
-   **验证**：如果数据已经是JSONL格式，在上传之前验证它。仅仅有`.jsonl`扩展名是不够的。您必须验证内容模式是否有效用于调优（例如，正确的系统/用户/模型角色）。

```bash
python3 scripts/prepare_dataset.py \
    --input my_data.jsonl \
    --format <messages|messages_gemini> \
    --validate_only
```

*(对于开源模型使用`--format messages`，对于Gemini模型使用`--format messages_gemini`。)* - 参考[数据准备指南](references/data_prep.md)了解所需的模式。

### 1.2 上传

使用唯一目录（例如，带有日期时间戳）将格式化的`.jsonl`文件上传到GCS，以避免覆盖不同运行产生的输出。

```bash
ARTIFACTS="gs://YOUR_BUCKET/tuning_agent_job_<datetime>/dataset.jsonl"
gcloud storage cp dataset.jsonl "$ARTIFACTS"
```

## 阶段2：模型配置和建议 {#阶段-2}

帮助用户选择最佳模型和参数。**在提交作业之前，始终寻求用户确认。**

-   如果用户在提示中没有指定特定模型，请根据**模型目录**计算建议。
-   **请求确认**：向用户展示推荐的模型，并在配置超参数之前请求他们的确认。

### 2.1 配置

#### 对于开源模型

根据[调优指南](references/tuning_guide.md)和[模型目录](references/models.md)中模型特定的基线推荐`tuning_mode`、`epochs`、`learning_rate`和`adapter_size`。

#### 验证实时模型ID

在提交作业之前，运行`scripts/list_models.py`并仅从其`models`输出中选择`--base_model`。不要编造ID或版本号。

```bash
python3 scripts/list_models.py --project YOUR_PROJECT --filter gemini
```

输出: `{"models": [...], "total_count": N, "truncated": bool}`。

-   对于Gemini，删除`google/`和`@default`（例如。 `google/gemini-2.5-flash@default` → `gemini-2.5-flash`）；对于开源模型，按`publisher/family@version`原样传递。
-   跳过以`-embedding`、`-tts`、`-image`、`-computer-use`或`-native-audio`结尾的Gemini变体；它们不可调优。
-   如果`truncated`为`true`，请在决定目标版本不可用时重新运行，使用更严格的`--filter`（例如。 `gemini-2.5`）。
-   如果`models`为空，停止并询问用户。

### 2.2 计算成本（仅限开源模型）

-   我们可以根据数据集和[模型目录](references/models.md)中选择的模型计算调优成本的粗略估计：

    ```bash
    python3 scripts/calculate_cost.py \
        --input my_data.jsonl \
        --model MODEL_NAME \
        --tuning_mode TUNING_MODE \
        --epochs epochs
    ```

    `--model`接受显示名称（`Qwen 3 8B`）或与传递给`--base_model`相同的资源名称（`qwen/qwen3@qwen3-8b`），因此可以在步骤2.1中重用。

> [!NOTE] **处理缺少数据集错误**：如果`scripts/calculate_cost.py`因为数据集文件（例如。 `my_data.jsonl`或`dummy_data.jsonl`）无法找到而失败，您**必须**告知用户数据集文件不存在或无法访问。您**必须**提示用户提供有效的数据集路径，并且立即停止工具执行以等待他们的响应。**不要**重试或循环，**不要**编造一个特定的成本数字，并且**不要**在收到来自用户的有效数据集之前提示提交作业批准。

-   **请求确认**：向用户展示推荐的超参数配置和估计成本，并在继续到作业提交之前请求他们的批准。确保注明估计成本只是一个估计，并且可能与实际账单成本有所不同。

## 阶段3：调优作业执行 {#阶段-3-调优作业执行}

**严重起飞检查（GCS验证）**：在您提议确认提示或提交任何调优作业之前，您**必须**验证指定的训练数据集GCS URI（例如。 `gs://dummy_bucket/dataset.jsonl`或`gs://YOUR_BUCKET/...`）实际上存在并可访问。运行`gcloud storage ls $DATASET_URI`（或`gsutil ls`）。

*   **如果验证失败**（例如。 `BucketNotFound`、`404`、`AccessDenied`，或指示存储桶不存在或无法访问，或指示虚拟/缺失存储桶），您**必须**告知用户存储桶或数据集不存在或无法访问。您**必须**提示用户提供有效的GCS URI作为数据集，并且立即停止工具执行以等待他们的响应。**不要**提议确认提示，并且**不要**在收到来自用户的有效数据集URI之前执行任何调优脚本。
*   **如果验证成功**，继续提出下面的确认提示。

### 对于Gemini模型

检查是否存在`scripts/tune_gemini_model.py`。

-   **如果`scripts/tune_gemini_model.py`存在**：使用此脚本提交Gemini模型调优作业。

    ```bash
    python3 scripts/tune_gemini_model.py
    ```

-   **如果`scripts/tune_gemini_model.py`不存在**：指示用户通过Google Cloud Console UI或使用Python Agent Platform SDK手动配置和提交调优作业。

### 对于开源模型

使用`scripts/tune_open_model.py`提交开源模型调优作业。使用可用模型文档
在
[文档](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/open-model-tuning#supported-models)中识别模型ID。

`--base_model`接受出版商模型**资源名称**
(`{publisher}/{model_id}@{version_id}`)，而不是目录中显示的显示名称。参考`references/models.md`中的“模型资源名称格式”以获取格式、验证示例以及如何查找您没有的名称。

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

此脚本仅限开源模型，并且`--location`如果省略，会回退到`global`。始终明确传递用户在0.2节中确认的位置，以便在您提出的批准命令字符串中可见。

> [!WARNING] **`--output_uri`对于开源模型是必需的。** Python SDK声明`output_uri: Optional[str] = None`，但调优后端拒绝省略`output_uri`的开源模型作业，并显示`INVALID_ARGUMENT: The output_uri field is required for this model.`将SDK的“可选”签名视为错误，并始终传递GCS目标。

由于该标志是强制性的，因此您必须在提交之前确定调优模型写入的位置。**永远不要编造一个存储桶名称，从项目编号中派生一个，或者未经提示运行`gcloud storage buckets create`。创建存储桶是一个变更操作，并且受Tier M确认政策约束。

-   **用户指定了存储桶或URI** → 使用它，像在阶段1.2中那样添加每个作业的唯一目录。
-   **在阶段1.2中使用存储桶上传数据集** → 提议将其用于输出并询问用户是否确认。
-   **两者都不是** → **停止并询问用户**他们希望在哪里存储调优模型。将提议为他们创建存储桶作为选项之一。如果他们接受，请提议确切的存储桶名称和位置，获得明确确认，然后才能创建它。

> [!IMPORTANT] **交互式确认要求（Tier M）**：在执行作业提交之前，您**必须**向用户展示显示所有字面标志的确认提示，并提供“是”和“否”选项。

> **严重**：当向用户展示此确认提示时，您**必须**将其作为直接的纯文本响应输出，并立即停止工具执行。**不要**在相同的回合中调用任何命令执行或交互式工具，因为意外的工具调用可能会被模拟 harness自动回复并导致无限循环。立即为用户的回复让步。

## 阶段4：监控 {#阶段-4-监控}

通过脚本输出中提供的Cloud Console链接监控作业。`--location`是必需的，并且必须与您提交时使用相同的位置：在`global`上提交的开源模型作业使用`--location global`进行轮询，即使工作在背后的真实区域中运行。

此外，询问用户是否希望您在后台监控作业状态。如果他们同意，执行`scripts/monitor_tuning_job.py`作为后台任务，以定期轮询作业状态并通知用户显示状态。如果用户拒绝，完全由用户检查状态。

## 阶段5：模型部署 {#阶段-5-模型部署}

一旦调优作业状态为`SUCCEEDED`，就部署模型。

部署需要真实区域——`--region=global`在此处无效。如果作业在`global`上运行，请从调优模型的资源名称（`projects/.../locations/<REGION>/models/...`）中读取区域并部署在那里；不要猜测。

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

> [!IMPORTANT] **交互式确认要求（Tier M）**：在执行部署之前，您**必须**向用户展示显示所有字面标志的确认提示，并提供“是”和“否”选项。

> **严重**：当向用户展示此确认提示时，您**必须**将其作为直接的纯文本响应输出，并立即停止工具执行。**不要**在相同的回合中调用任何命令执行或交互式工具，因为意外的工具调用可能会被模拟 harness自动回复并导致无限循环。立即为用户的回复让步。

参考[模型目录](references/models.md)以获取特定开源模型的硬件建议。

## 资源

-   [数据准备指南](references/data_prep.md)
-   [模型目录](references/models.md)
-   [调优指南](references/tuning_guide.md)
-   `scripts/prepare_dataset.py`: 数据转换和验证。
-   `scripts/tune_open_model.py`: 开源模型调优作业提交。
