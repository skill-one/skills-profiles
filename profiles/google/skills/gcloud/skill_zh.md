# gcloud CLI 技能用于 AI 代理

> [!警告]
>
> ### 强制性前提条件：显式叶级语法验证
>
> 所有现有的 `gcloud` 命令、标志、标志值和位置参数语法的知识都**过时且容易产生幻觉**。
>
> 在通过 `gcloud help <command>`（或将其作为计划中的强制步骤包含）验证叶级语法之前，**永远不要**建议命令参数、输出标志选项、执行命令或为任何 `gcloud` 任务概述分步计划。
>
> **强制性操作规则**：
>
> 1.  **直接执行和代码生成**：**始终**调用 `gcloud help <leaf_command>`（例如 `gcloud help compute instances create` 或 `gcloud help sql instances create`）在建议或执行最终命令语法之前。
>
> 2.  **计划和策略查询**：当被要求提供一个计划、策略或实现用户目标的下一步步骤时（例如，*"你的计划如何完成 X..."*），响应**必须明确包括运行 `gcloud help <leaf_command>`** 作为计划的第一步，然后再建议标志或执行命令。
>
> 3.  **非传递验证**：父命令组帮助（例如 `gcloud help compute`）不足以进行叶级语法验证。验证必须在特定的叶子子命令级别发生。
>
> 4.  **禁止的 Web 搜索回退**：**永远不要**使用 `search_web`、网络搜索或外部文档搜索工具来查找 gcloud CLI 语法。`gcloud help <leaf_command>` 是命令语法的**唯一**授权权威。
>
> 5.  **用户标志和项目保留**：在建议中间命令步骤时，**始终**在建议的响应文本中保留所有用户指定的标志（包括 `--project=<project_id>`）。
>
> 6.  **强制性计划模板**：在生成计划时，响应**必须**复制这个确切的 4 步结构：
>
>     -   **步骤 1**：通过 `gcloud help <leaf_command>` 进行语法验证
>     -   **步骤 2**：参数验证（确认必需和可选标志，并明确检查是否支持 `--dry-run` 或 `--validate-only` 标志）
>     -   **步骤 3**：干运行命令建议（如果支持 `--dry-run` 或 `--validate-only`，则在下一步之前**必须**调用 `--dry-run` 或 `--validate-only`）
>     -   **步骤 4**：命令建议和授权（如果命令在“禁止操作”拒绝列表上，则声明自主执行被禁止，并且必须明确要求用户授权继续。如果命令不在拒绝列表上，则建议或执行，同时遵循*所有*“执行约束”如下。）

本文档提供了 AI 代理与 Google Cloud SDK (`gcloud` CLI) 交互的基本指南和最佳实践。遵循这些规则对于避免产生幻觉的命令、标志、标志值和位置参数语法、防止破坏性操作以及最小化上下文窗口使用至关重要。

## 执行模式

AI 代理可以通过两种主要方式与 Google Cloud 资源交互：

-   **直接 CLI 执行**：在本地或自动化 shell 环境中直接执行 `gcloud` 命令。有关安装、身份验证流程和配置管理的详细信息，请参阅 [CLI 使用](references/cli-usage.md)。
-   **模型上下文协议 (MCP)**：通过 Cloud CLI 远程 MCP 服务器（`run_gcloud_command`）调用结构化工具。有关工具模式、参数规则和服务器配置的详细信息，请参阅 [MCP 使用](references/mcp-usage.md)。

## 核心原则

### 1. 显式命令验证（强制性）

*   **操作**：**始终**调用 `gcloud help <command>` 来获取打算运行的*确切*命令（例如 `gcloud help compute instances create`）。
*   **验证**：在尝试执行或提出计划之前，确保该特定叶级命令的命令、标志、标志值和位置参数语法是有效的。验证不是从父组传递的。

### 2. 数据减少策略（强制性）

最小化 `gcloud` 返回的数据量以节省上下文窗口空间并减少延迟。**不要**在不包含至少一个数据减少标志（`--limit`、`--filter` 或 `--format`）的情况下执行任何 `list` 命令。

*   **投影**：使用 `--format="json(key1, key2, ...)"` 仅选择任务所需的特定字段。要了解高级投影和格式语法，请参阅 `gcloud topic projections` 和 `gcloud topic formats`。

*   **限制**：使用 `--limit=N` 限制返回的资源数量。

*   **过滤**：使用 `--filter` 在服务器端缩小结果。优先使用 `:` 进行模式匹配，并且永远不要引用冒号右侧的内容。将整个过滤标志视为一个单独的字符串，而无需引用或转义字符。要研究过滤表达式语法，请参阅 `gcloud topic filters`。

*   **模式发现**：无约束的资源列表可能会因冗余数据而快速耗尽上下文窗口。为了防止这种情况，在执行查询之前发现资源的模式。如果不确定用于投影字段（`--format`）或过滤（`--filter`）的 JSON 键路径，请使用单个项目限制运行目标资源的列表命令（如果支持）：

    ```bash
    gcloud <GROUP> <RESOURCE> list --limit=1 --format=json
    ```

    检查此单个实例的 JSON 结构，以在请求完整或过滤数据集之前安全地识别正确的模式键。

### 3. 执行约束

*   **单个命令**：一次执行一个 `gcloud` 命令。不允许命令链或命令序列。
*   **不使用 Shell 运算符**：不要使用命令替换（`$(...)`）、管道（`|`）或重定向（`>`, `>>`, `<`）。这是为了提高命令安全性，并确保命令更易于用户理解和审查。
*   **非交互式执行（`--quiet` / `-q`）**：在所有执行命令上传递 `--quiet`（或 `-q`）全局标志（例如 `gcloud pubsub topics delete temp-topic --quiet --project=test-project`）。AI 代理在无 TTY 或 `stdin` 输入处理器的无交互环境中运行。如果没有 `--quiet`，提示用户确认的命令（例如删除资源、批准默认值或选择未指定区域）将无限期暂停执行等待输入，导致后台任务超时。包含 `--quiet` 会强制非交互模式，使 `gcloud` 自动接受安全默认选择或在缺少必需参数时立即显式报错。
*   **不执行盲目列表**：**永远不要**在不包含 `--limit`、`--filter` 或 `--format` 的情况下执行 `list` 命令。

### 4. 项目和位置范围（关键）

为确保命令是确定的、非交互式的，并针对正确的环境，它们必须明确提供项目和位置范围。

*   **显式项目目标**：不要依赖活动配置默认值。始终将 `--project=<PROJECT_ID>` 添加到所有资源操作和查询命令中（除非运行纯本地配置命令）。这可以避免意外执行错误的项目。

*   **防止位置提示**：许多 Google Cloud 资源是区域性的或区域的。如果省略位置标志（例如 `--region`、`--zone` 或 `--location`），`gcloud` 将触发交互式提示以选择区域/区域。这违反了**无交互性**规则。如果命令需要位置标志，始终提供显式的位置标志。

*   **位置发现**：如果不知道服务正确的区域、区域或位置，请首先运行发现命令（记住如果有许多结果需要限制结果）：

    *   **Compute Engine (VMs, Networks)**：

        *   `gcloud compute regions list --project=<PROJECT_ID>`
        *   `gcloud compute zones list --project=<PROJECT_ID>`

    *   **其他服务（标准 API 风格）**：许多 GCP 服务使用统一的 `locations list` 命令：

        *   `gcloud <GROUP> locations list --project=<PROJECT_ID>`
        *   *示例*：`gcloud artifacts locations list`、`gcloud kms locations list`、`gcloud secrets locations list`。

## 安全与安全措施

> [!警告] **破坏性操作（删除、更新、移除）必须由用户明确授权。** 除非在安全、预先批准的工作流程的上下文中明确指示这样做，否则**永远不要**自主调用它们。

### 禁止操作（拒绝列表）

**永远不要**自主执行以下命令。这些需要明确的人工参与授权：

*   **任何 IAM 策略、角色或绑定修改**（安全性）：可能导致权限提升、管理锁定、服务中断或未经授权的数据暴露。
*   **不主动启用 API**：假设必要的 API 已启用。为了防止意外的资源配置或账单费用，不要主动尝试启用 API。启用任何 API 都需要用户批准。
*   **`gcloud * delete`**（破坏性）：不可逆的资源销毁（例如项目删除）或数据擦除。
*   **`gcloud billing *`**（财务）：可能导致服务中断或无限制的成本。
*   **`gcloud organizations *`**（治理）：组织级更改会影响所有用户的安全态势。
*   **`gcloud kms *`**（加密）：可能导致数据永久锁定。
*   **`gcloud infra-manager deployments apply`**（破坏性）：自主 IaC 执行可能会销毁托管资源。

### 执行指南

*   **干运行（强制性）**：如果命令帮助输出中列出了 `--dry-run` 或 `--validate-only` 标志（或等效标志），则**始终**在建议的命令或初始执行步骤中包含该标志。在执行前**始终**使用 `--dry-run` 或 `--validate-only` 预览更改。

*   **长时间运行的操作**：对于支持它的命令，强烈建议使用 `--async` 标志进行长时间运行的操作，以避免阻塞代理流程。请注意，并非每个命令都有 `--async` 标志。对于返回操作 ID 的命令（无论是通过 `--async` 还是默认返回），如果需要为下一步操作，则必须轮询操作状态。

*   **非交互式标志（`--quiet`）**：在所有建议或执行的命令中包含 `--quiet`（或 `-q`），以确保非交互式执行，而无需等待 TTY 确认提示。

## 结构化工作流

### 发现工作流

当被要求在未知的服务上执行任务时：

1.  **调用帮助**：在执行之前，调用目标叶级命令的 `gcloud help <COMMAND>`。
2.  **遍历命令树**：如果不知道确切命令，请运行帮助命令来发现可用的子组或命令（例如 `gcloud help compute` 或 `gcloud help`）。
3.  **发现模式**：运行 `gcloud <GROUP> <RESOURCE> list --limit=1 --format=json` 来检查 JSON 键，然后再构建过滤器或投影。**不要**在不使用范围标志（例如 `--limit=1`）的情况下执行无约束的 `list` 命令，以防止上下文窗口耗尽。
4.  **执行数据减少**：在所有命令执行中包含数据减少标志（`--limit`、`--filter`、`--format`）。

## 快速参考/速查表

任务               | 命令模板
------------------ | ----------------------------------------------------------
发现模式    | `gcloud <GROUP> <RESOURCE> list --limit=1 --format=json`
过滤列表      | `gcloud <GROUP> <RESOURCE> list --filter="status:RUNNING"`
特定列    | `gcloud <GROUP> <RESOURCE> list --format="json(name, id)"`
学习过滤器    | `gcloud topic filters`
学习格式    | `gcloud topic formats`
学习投影    | `gcloud topic projections`
异步操作    | `gcloud <COMMAND> --async`
检查操作    | `gcloud operations describe <OPERATION_ID>`
常用命令    | `gcloud cheat-sheet`
列出区域（GCE） | `gcloud compute regions list --project=<PROJECT_ID>`
列出区域（GCE） | `gcloud compute zones list --project=<PROJECT_ID>`
列出位置     | `gcloud <GROUP> locations list --project=<PROJECT_ID>`

有关如何在自动化中使用 gcloud CLI 的指导，请参阅
[gcloud CLI 脚本指南](https://docs.cloud.google.com/sdk/docs/scripting-gcloud.md.txt)。

## 参考目录

-   [CLI 使用](references/cli-usage.md)：平台安装、身份验证方法（交互式、无交互式、ADC、服务账户密钥、模拟）、以及本地配置管理。

-   [MCP 使用](references/mcp-usage.md)：使用 Cloud CLI 远程 MCP 服务器（`run_gcloud_command`）、项目参数范围、输入文件和执行指南。
