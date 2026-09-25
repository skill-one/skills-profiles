# 代理平台模型注册表管理

## 概述

此技能提供了在代理平台模型注册表中管理机器学习模型的操作指南。它涵盖了列出模型、描述模型详情、上传新模型或版本、更新元数据以及删除模型等内容。

## 安全与确认级别（关键）

在代表用户执行任何命令之前，你必须严格遵守以下基于请求操作的安全级别：

1.  **R级别：只读 (`list`, `describe`, `get`)**
    *   无需确认。立即执行以收集信息。

2.  **M级别：可变且可逆 (`upload`, `update`)**
    *   需要**交互式确认**，提供“是”/“否”选项。确认提示必须包含确切的、字面的命令字符串以及所有必需的标志（例如 `--region=us-central1`，`--display-name="..."`）——自然语言释义不充分。
    *   **同回合限制**：绝对不能在同回合中呈现确认提示时执行该命令。停止并等待用户回复；只有在明确“是”/批准后才能执行。

3.  **D级别：破坏性且不可逆 (`delete`)**
    *   需要**明确输入确认**（例如“我确认”或“是，删除它”）。立即请求确认——在任何预检之前（不要先检查模型是否部署到端点）。
    *   **同回合限制**：绝对不能在同回合中请求输入确认时执行该命令。等待用户在新回合中回复。

## 第0阶段：环境设置

**关键**：在运行任何命令之前，你必须通过以下步骤确保环境正确初始化：

1.  **Google Cloud 身份验证**：使用你的 Google Cloud 凭据进行身份验证，并为代理平台配置活动的应用默认凭证（ADC）：

    ```bash
    gcloud auth login
    gcloud auth application-default login
    ```

2.  **设置项目**：为后续命令配置活动项目：

    ```bash
    gcloud config set project $PROJECT_ID
    ```

3.  **区域**：在每个以下命令中始终指定 `--region=$LOCATION_ID`。不要使用 `global`。

## 1. 列出模型（R级别）

使用此命令在注册表中发现现有模型并检索它们的数字 ID。无需确认。

```bash
gcloud ai models list \
    --region=$LOCATION_ID
```

## 2. 描述模型（R级别）

检索特定模型或版本的完整元数据。无需确认。

```bash
gcloud ai models describe $MODEL_ID \
    --region=$LOCATION_ID
```

要针对特定版本：

```bash
gcloud ai models describe ${MODEL_ID}@${VERSION_ID} \
    --region=$LOCATION_ID
```

## 3. 上传模型（M级别）

注册新模型或现有模型的新版本。这是一个长时间运行的操作。**操作需要在继续之前进行内联确认。**

### 示例：上传自定义模型

```bash
gcloud ai models upload \
    --region=$LOCATION_ID \
    --display-name="my-custom-model" \
    --container-image-uri="gcr.io/my-project/my-model:latest" \
    --artifact-uri="gs://my-bucket/path/to/artifacts"
```

> [!IMPORTANT]
>
> 这是一个 M 级别操作——请参阅[安全与确认级别]。

要上传现有模型的新版本，请使用 `--parent-model` 标志或指定父模型 ID。

## 4. 更新模型（M级别）

更新显示名称、描述或标签等元数据字段。**操作需要在继续之前进行内联确认。**

```bash
gcloud ai models update $MODEL_ID \
    --region=$LOCATION_ID \
    --display-name="new-display-name" \
    --description="Updated description"
```

> [!IMPORTANT]
>
> 这是一个 M 级别操作——请参阅[安全与确认级别]。

## 5. 删除模型（D级别）

永久删除模型及其所有版本。**操作需要在继续之前进行明确输入确认。**

```bash
gcloud ai models delete $MODEL_ID \
    --region=$LOCATION_ID
```

> [!WARNING]
>
> 此操作不可逆。删除前，所有模型版本必须从所有端点卸载。

## 6. 搜索发布者模型（R级别）

在生成交互式模型详情之前，你必须通过搜索模型花园发布者模型来验证 `model_id`。无需确认。

使用 `gcloud ai` CLI 搜索匹配的发布者模型。

```bash
gcloud ai model-garden models list --model-filter="<model_name_or_query>" --full-resource-name --format=json
```

这将返回一个匹配的模型列表。从结果中提取确切的 `name` 字段（例如 `publishers/google/models/gemma2` 或 `publishers/qwen/models/qwen3-coder`）作为验证的 `model_id`。
