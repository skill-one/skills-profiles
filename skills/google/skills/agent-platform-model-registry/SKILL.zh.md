---
name: agent-platform-model-registry
description: 代理平台模型注册表管理。当您需要上传、列出、描述、更新或删除代理平台模型注册表中的机器学习模型（及其版本）时使用。不适用于模型训练、模型部署到端点或管理非代理平台模型。
---

# 代理平台模型注册表管理

## 概述

本技能提供管理代理平台模型注册表中文档说明。它涵盖了列出模型、描述模型详情、上传新模型或版本、更新元数据和删除模型。

## 安全性与确认级别（关键）

在代表用户执行任何命令之前，你必须根据请求的操作遵循以下安全级别：

1.  **R级别：只读（`list`，`describe`，`get`）**
    *   无需确认。立即执行以收集信息。

2.  **M级别：可变且可逆（`upload`，`update`）**
    *   需要交互式确认，带有“是”/“否”选项。确认提示必须包含确切的、字面的命令字符串以及所有必需的标志（例如 `--region=us-central1`，`--project=...`，`--display-name="..."`）—自然语言释义是不充分的。
    *   **同回合限制**：绝对不能在同回合中执行命令，即不能在收到请求或显示确认提示时执行！在回合1中，你必须只显示带有确切的、字面的命令字符串的交互式确认卡。停止并等待用户的回复；只有在明确的“是”/批准后的下一回合中才能执行。在回合1中未经确认就执行 `upload` 或 `update` 是严格禁止的。
    *   **流程中参数更改/拒绝**：如果用户拒绝提示或更改任何参数（例如显示名称、描述、父模型），不要执行旧命令。立即适应并显示新的确认提示，带有更新的字面命令，并等待批准。

3.  **D级别：破坏性且不可逆（`delete`）**
    *   需要明确的输入确认（例如“我确认”或“是，删除它”）。立即请求确认——在任何预检之前（不要先检查模型是否部署到端点）。
    *   **同回合限制**：绝对不能在同回合中请求输入确认。等待用户在新的回合中回复。
    *   **流程中目标更改**：如果用户改变主意（例如，“删除第二个模型而不是第一个”），不要删除第一个模型。为新选择模型ID显示新的输入确认提示，并等待批准。

4.  **成本估算**：模型注册表操作管理目录元数据和存储的模型工件，而不会配置服务计算或端点。不要为模型注册表操作调用 `estimate_cost` 工具，因为 `estimate_cost` 专为服务基础设施（端点/批量预测）设计，如果调用注册表操作将返回错误。如果要在预览卡中包含成本，请说明模型注册表操作不会产生服务计算费用（$0.00计算费用；模型工件适用标准云存储定价）。

## 第0阶段：环境设置与参数解析

**关键**：在运行任何命令之前，验证所有必要参数是否已知：

1.  **缺少区域或项目**：遵循基本环境接地策略：如果会话位置或项目从先前的回合中已经设置，则无需重新询问。如果从提示和会话上下文中都缺失，最多允许一次直接查找（例如 `gcloud config get project` 或 `gcloud config get compute/region`）。如果仍然无法解决或存在歧义，暂停并明确要求用户提供缺失的参数，然后再执行可变或资源特定的命令。
2.  **缺少模型ID**：如果用户请求更新或描述模型而没有提供模型ID，暂停并要求用户提供模型ID，或提供列出模型以帮助他们找到它。
3.  **占位符替换**：如果用户的请求显示名称包含占位符标记（例如 `<unique-suffix>`，`[suffix]` 或 `<timestamp>`），生成一个简短的唯一字母数字字符串或时间戳并干净地替换它。绝对不要将未展开的字面占位符标记传递给API。
4.  **区域和项目标志**：在所有 `gcloud ai models` 命令中始终明确传递 `--region=$LOCATION_ID` 和 `--project=$PROJECT_ID`。不要使用 `global`。

## 1. 列出模型（R级别）

使用此命令发现注册表中的现有模型并检索它们的数字ID。无需确认。

```bash
gcloud ai models list \
    --region=$LOCATION_ID \
    --project=$PROJECT_ID
```

## 2. 描述模型（R级别）

检索特定模型或版本的完整元数据。无需确认。

```bash
gcloud ai models describe $MODEL_ID \
    --region=$LOCATION_ID \
    --project=$PROJECT_ID
```

要针对特定版本：

```bash
gcloud ai models describe ${MODEL_ID}@${VERSION_ID} \
    --region=$LOCATION_ID \
    --project=$PROJECT_ID
```

## 3. 上传模型（M级别）

注册新模型或现有模型的新版本。这是一个长时间运行的操作。**执行此操作前需要先进行内联确认。**

### 示例：上传自定义模型

```bash
gcloud ai models upload \
    --region=$LOCATION_ID \
    --project=$PROJECT_ID \
    --display-name="<DISPLAY_NAME>" \
    --container-image-uri="<CONTAINER_IMAGE_URI>" \
    [--artifact-uri="<ARTIFACT_URI>"]
```

> [!IMPORTANT]
>
> 这是一个M级别操作——见上文 [安全性与确认级别]。
>
> -   如果用户指定“无工件URI”，则省略 `--artifact-uri`。
> -   如果注册现有模型的新版本，请包含 `--parent-model=$PARENT_MODEL_ID`。
> -   将 `<DISPLAY_NAME>` 替换为用户请求的确切名称。

## 4. 更新模型（M级别）

更新显示名称或描述等元数据字段。请注意，`gcloud ai models` 没有更新子命令。相反，模型元数据更新必须使用Vertex AI Python SDK (`google.cloud.aiplatform.Model`) 执行。

**执行此操作前需要先进行内联确认，包含确切的脚本。**

```bash
python3 -c "
from google.cloud import aiplatform

aiplatform.init(project='$PROJECT_ID', location='$LOCATION_ID')
model = aiplatform.Model('$MODEL_ID')
model.update(display_name='<NEW_DISPLAY_NAME>', description='<NEW_DESCRIPTION>')
print(f'Successfully updated model: {model.resource_name}')
"
```

> [!IMPORTANT]
>
> 这是一个M级别操作——见上文 [安全性与确认级别]。
>
> -   如果只更新显示名称，请传递 `model.update(display_name='<NEW_DISPLAY_NAME>')`。
> -   如果只更新描述，请传递 `model.update(description='<NEW_DESCRIPTION>')`。
> -   确认卡必须显示上述确切的python命令片段。绝对不能在回合1中执行；等待明确的用户批准。

## 5. 删除模型（D级别）

永久删除模型及其所有版本。**执行此操作前需要先进行明确的输入确认。**

```bash
gcloud ai models delete $MODEL_ID \
    --region=$LOCATION_ID \
    --project=$PROJECT_ID
```

> [!WARNING]
>
> 此操作不可逆。所有模型版本必须先从所有端点卸载才能删除。

## 6. 搜索发布者模型（R级别）

在生成交互式模型详情之前，你必须通过搜索模型花园发布者模型来验证 `model_id`。无需确认。

使用 `gcloud ai` CLI 搜索匹配的发布者模型。

```bash
gcloud ai model-garden models list --model-filter="<model_name_or_query>" --full-resource-name --format=json
```

这将返回一个匹配的模型列表。从结果中提取确切的 `name` 字段（例如 `publishers/google/models/gemma2` 或 `publishers/qwen/models/qwen3-coder`）作为已验证的 `model_id`。
