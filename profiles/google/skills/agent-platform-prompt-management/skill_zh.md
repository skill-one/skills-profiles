## 使用指南

要有效地使用此技能：

1.  **通过 Python 执行操作**：使用执行环境中的 `run_command` 运行下方的 Python 代码片段，以代表用户在 Agent 平台上管理提示。不要将执行委托给用户，或在获得批准后声称无权访问。

2.  **不进行文件系统搜索**：不要尝试在文件系统上查找 Python 文件或脚本以执行这些操作。

## 安全与确认级别（关键）

在代表用户执行任何命令或脚本之前，您必须根据请求的操作遵守以下安全级别，以防止意外修改或永久删除提示资源：

1.  **级别 R：只读（`list`，`get`）**
    *   无需确认。立即执行以收集信息。

2.  **级别 M：可修改且可逆（`create`）**

    *   需要交互式确认，带有“是”/“否”选项，在执行提示创建之前，以防止意外资源扩散或配置错误。确认提示必须清楚地解释拟议的提示创建及其关键参数（例如，显示名称、模板文本、目标模型）。没有指定参数的自然语言释义是不充分的。
    *   **同回合限制**：不要在显示确认提示的同一次回合中执行创建代码。停止并等待用户的回复；只有在明确“是”/获得批准后才能执行。
    *   卡片中的每个参数都必须追溯到用户所说的话。目标模型是用户的选择，不是默认值：如果用户没有指定一个，则在构建卡片之前询问。不要采用此处示例中或 `references/create.md` 中出现的模型。
    *   **黄金标准示例**——对于说“为 gemini-2.5-pro 创建一个名为 Customer Support Greeting 的提示，模板为 Hello {{user_name}}，我能帮您什么...”的用户：

        > 我将在 Agent 平台上创建一个具有以下参数的提示。在继续之前，请确认此信息：
        >
        > *   **显示名称**：`Customer Support Greeting`
        > *   **目标模型**：`gemini-2.5-pro`
        > *   **模板文本**：`Hello {{user_name}}，我能帮您什么...`
        >
        > 您确认吗？[是/否]

3.  **级别 D：破坏性且不可逆（`delete`）**

    *   需要明确的键入确认（例如，“我确认”或“是，删除它”）在执行提示删除之前，以防止意外永久丢失生产提示资产。在进行任何预飞行检查之前请求确认。
    *   **同回合限制**：永远不要在同一次回合中请求键入确认时执行。等待用户在新回合中回复。
    *   **黄金标准示例**：

        > 我将从 Agent 平台永久删除以下提示。此操作不可逆。在继续之前，请键入您的确认（例如，“我确认”）：
        >
        > *   **提示 ID**：`prompt_12345abc`
        > *   **显示名称**：`Legacy Outdated Prompt`
        >
        > 请键入您的确认以继续。

## 第 0 阶段：环境设置

**关键**：在用户运行下方的 Python 代码片段之前，您必须建议他们按照以下步骤确保环境正确初始化：

1.  **Google Cloud 身份验证**：使用您的 Google Cloud 账户进行身份验证，并为 Agent 平台访问配置活动的应用默认凭证（ADC）：

    ```bash
    gcloud auth login
    gcloud auth application-default login
    ```

2.  **Python 依赖项**：此技能需要 `google-cloud-aiplatform` 和 `google-genai`。不要创建虚拟环境——它开始为空并隐藏环境已经提供的包，强制进行冗余安装。探测并仅安装缺失的内容：

    ```bash
    python3 -c "import vertexai, google.genai" \
      || pip install google-cloud-aiplatform google-genai
    ```

3.  **执行**：使用纯 `python3` 运行 Python 代码片段。没有需要首先激活的环境。

> [!提示]
>
> **占位符参数替换**：下方的 Python 脚本使用大写字符串占位符（如 `"PROJECT_ID"`、`"LOCATION_ID"`、`"PROMPT_ID"` 和 `"MODEL_ID"`）。您**必须**在使用脚本之前，将它们动态替换为用户提供（或在发现上下文中找到的）实际项目 ID、区域、提示 ID 和目标模型值。如果用户没有提供其中任何一个，请询问——占位符永远不会被猜测的合理值满足。

## 1. 通过 Agent 平台 SDK 管理提示

SDK 在预览模块中提供了一个高级 `Prompt` 类。

### 创建提示（级别 M）

当您需要在 Agent 平台上创建新的管理提示时使用。

*   **参考**：有关详细说明和 Python 代码片段，请参阅 [create.md](references/create.md)。

### 列出提示（级别 R）

```python
import vertexai
from vertexai.preview import prompts

vertexai.init(project="PROJECT_ID", location="LOCATION_ID")

all_prompts = prompts.list()
for p in all_prompts:
    print(f"Name: {p.display_name}, ID: {p.prompt_id}")
```

### 检索和使用提示（级别 R）

```python
import vertexai
from vertexai.preview import prompts

vertexai.init(project="PROJECT_ID", location="LOCATION_ID")

retrieved_prompt = prompts.get(prompt_id="PROMPT_ID")
# 检索到的 Prompt 上的属性：
# - retrieved_prompt.prompt_id (例如 "123456789...")
# - retrieved_prompt.prompt_data (模板文本字符串)
# - retrieved_prompt.model_name (目标模型)
# - retrieved_prompt.prompt_name (显示名称，或
#   retrieved_prompt._dataset.display_name)
# 支持版本：prompts.get(prompt_id="PROMPT_ID", version_id="2")

# 使用变量组装（kwargs 必须匹配模板变量名称）
assembled = retrieved_prompt.assemble_contents(text="The quick brown fox...")
print(assembled)
```

### 删除提示（级别 D）

**关键**：您必须将数字提示 ID（例如 `"1234567890123456789"`）传递给 `prompts.delete()`。SDK 内部使用 `vertexai.init()` 中的项目和位置构造完整的资源路径。

**需要确认**：作为级别 D（破坏性）操作，代理必须暂停并请求用户对提示 ID 进行明确的、高摩擦力的键入确认，然后再执行删除代码。该操作不可逆。一旦用户键入确认（例如，“我确认”），立即执行删除代码。

> [!重要]
>
> **永远不要在收到用户在新回合中的回复之前预执行任何删除代码。** 您绝不能猜测或假设会获得确认。在单个并行回合中请求确认并运行代码是严重的安全违规。

```python
import vertexai
from vertexai.preview import prompts

vertexai.init(project="PROJECT_ID", location="LOCATION_ID")

prompts.delete(prompt_id="PROMPT_ID")
```

### 删除后的验证

当用户请求列出提示或检查已删除的提示是否消失时，列出提示并明确说明已删除的提示 ID 是否存在。如果找不到，请明确确认：*"我已经验证提示 ID `<PROMPT_ID>` 已不再项目中存在。*"

## 2. 最佳实践

-   **幂等性**：
    *   **级别 R**（List，Get）：天生幂等。
    *   **级别 D**（Delete）：重新运行删除操作对于不存在的或已删除的资源返回 NOT_FOUND。将其视为成功。
-   **占位符**：在您的提示模板中使用标准占位符语法（变量名用双花括号括起来）。
-   **版本控制**：在更新生产提示时始终标记或记录版本 ID。
-   **模型引用**：提示是针对目标模型 ID 创建的，代码片段将其作为 `"MODEL_ID"` 占位符携带。像其他占位符一样，它必须替换，并且是从用户所说的话中替换的——如果他们没有指定模型，请询问。不要用当前合理的模型（如 `gemini-2.5-pro`）来替代。
-   **底层架构**：在使用数据集 API 时，始终使用正确的 `metadata_schema_uri` 和嵌套 `metadata` 结构，以确保提示被 Agent 平台 Studio 和提示 SDK 识别。
