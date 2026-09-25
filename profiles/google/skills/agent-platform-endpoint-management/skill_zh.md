# 代理平台端点管理

## 概述

此技能提供了管理代理平台端点的程序性知识。
端点是提供稳定在线预测URL的逻辑服务主机。在将模型部署到端点之前，您必须创建一个端点。

## 安全性与确认级别（关键）

在代表用户执行任何命令之前，您必须遵守以下基于请求操作的安全级别：

1.  **R级别：只读（`list`，`describe`，`get`）**
    *   无需确认。立即执行以收集信息。

2.  **M级别：可变且可逆（`create`，`update`）**
    *   需要**交互式确认**，提供'是'/'否'选项。确认提示**必须**包含确切的、字面的命令字符串以及所有必需的标志（例如 `--region=us-central1`，`--display-name="..."`）——自然语言释义**不**充分。
    *   **同回合限制**：**绝对禁止**在提出确认提示的同一回合中执行命令。停止并等待用户的回复；只有在明确'是' / 获得批准后才能执行。

3.  **D级别：破坏性且不可逆（`delete`）**
    *   需要**明确输入确认**（例如 "我确认" 或 "是，删除它"）。立即请求确认——在任何预检（不要先`describe`，不要先检查端点是否为空）之前。
    *   **同回合限制**：**绝对禁止**在请求输入确认的同一回合中执行命令。等待用户在新回合中回复。

## 第0阶段：环境设置

**关键**：在运行任何命令之前，您必须通过以下步骤确保环境正确初始化：

1.  **Google Cloud认证**：使用您的Google Cloud凭证进行认证，并为代理平台访问配置活动的应用默认凭证（ADC）：

    ```bash
    gcloud auth login
    gcloud auth application-default login
    ```

2.  **设置项目**：为后续命令配置活动项目：

    ```bash
    gcloud config set project $PROJECT_ID
    ```

3.  **区域**：在以下每个命令中始终指定 `--region=$LOCATION_ID`。**绝对禁止**使用`global`。如果未提供，请询问用户指定区域。

## 1. 列出端点（R级别）

使用此命令发现特定区域中的现有端点并检索其ID。无需确认。

```bash
gcloud ai endpoints list \
    --region=$LOCATION_ID
```

*(可选)* 对于分页，您必须使用`--limit=$LIMIT`来限制返回端点的总数。您也可以追加`--page-size=$PAGE_SIZE`来控制API分块，或`--page-token=$PAGE_TOKEN`用于下一页。

> [!IMPORTANT]
>
> 始终指定`--region`。**绝对禁止**使用'global'。如果未提供，请询问用户指定。

## 2. 描述端点（R级别）

检索特定端点的完整元数据。无需确认。

```bash
gcloud ai endpoints describe $ENDPOINT_ID \
    --region=$LOCATION_ID
```

## 3. 创建端点（M级别）

创建新的端点资源。父资源是位置。**操作需要在继续之前进行内联确认。**

```bash
gcloud ai endpoints create \
    --region=$LOCATION_ID \
    --display-name="my-endpoint"
```

> [!IMPORTANT]
>
> **您必须首先寻求交互式确认。** 您的确认提示**必须**显示字面的命令字符串。例如：
>
> ```bash
> gcloud ai endpoints create --region=$LOCATION_ID --display-name="my-endpoint"
> ```
>
> 或确切的标志。**关键**：**绝对禁止**在提出确认的同时执行此命令。

## 4. 更新端点（M级别）

更新端点元数据，例如显示名称或标签。**操作需要在继续之前进行内联确认。**

```bash
gcloud ai endpoints update $ENDPOINT_ID \
    --region=$LOCATION_ID \
    --display-name="new-display-name"
```

先通过列出或描述端点检查端点是否存在。

> [!IMPORTANT]
>
> **您必须首先寻求交互式确认。** 您的确认提示**必须**显示字面的命令字符串。例如：
>
> ```bash
> gcloud ai endpoints update $ENDPOINT_ID --region=$LOCATION_ID --display-name="new-display-name"
> ```
>
> 或确切的标志。**关键**：**绝对禁止**在请求确认的同时执行此命令。当您请求确认时，您必须立即停止并等待用户回复。

## 5. 删除端点（D级别）

永久删除端点资源。**操作需要在继续之前进行明确输入确认。**

```bash
gcloud ai endpoints delete $ENDPOINT_ID \
    --region=$LOCATION_ID
```

> [!WARNING]
>
> 在删除端点之前，所有模型必须**从该端点卸载**。在您收到输入确认以删除之前，**绝对禁止**运行`describe`。

## 6. 流量分割（M级别）

您可以在更新期间管理部署在同一端点的不同模型之间的流量分割。**操作需要在继续之前进行内联确认。**

```bash
# 示例：使用特定流量分割部署模型通常是通过 'gcloud ai endpoints deploy-model' 完成的。
```

有关部署和卸载模型的说明，请参阅`agent-platform-deploy`技能。

## 故障排除

-   **403 权限被拒绝**：确保分配了`aiplatform.admin`或`owner`角色。
-   **配额超出**：在控制台中验证区域的端点配额。
-   **资源繁忙**：如果删除失败，请检查模型是否仍在卸载中。
