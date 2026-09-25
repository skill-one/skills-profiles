# Agent Platform RAG 引擎管理

此技能提供了如何使用 Agent Platform Python SDK 与 Agent Platform RAG 引擎交互的说明。您必须使用 `vertexai` Python SDK 执行 RAG 引擎操作，而不是原始 REST 调用或 MCP 工具，因为此代码旨在由外部客户端运行。

## 安全性与确认级别（关键）

在代表用户执行任何命令或脚本之前，您必须根据请求的操作遵守以下安全级别：

1.  **R 级：只读（`list_corpora`，`list_files`，`get_corpus`，`retrieval_query`）**
    *   无需确认。立即执行以收集信息或检索基于事实的上下文。

2.  **RC 级：只读但消耗计算资源（`client.models.generate_content`）**
    *   在执行基于事实的内容生成之前，需要 **交互式确认**，并提供“是”/“否”选项。确认提示必须清楚地解释拟议的执行操作及其关键参数（例如，目标语料库 ID、查询文本、目标模型）。自然语言的改述而未指定确切参数是不够的，因为需要明确列出参数，以确保用户明确批准特定的资源和配置。
    *   **同回合限制**：不要在呈现确认提示的同一回合中执行生成代码。停止并等待用户的回复；只有在明确“是”/批准后才能执行。
    *   **黄金标准示例**：
        > 我将使用以下参数执行基于事实的内容生成。在继续之前，请确认此信息：
        > *   **目标语料库 ID**：`projects/123/locations/us/ragCorpora/abc`
        > *   **目标模型**：`gemini-2.5-pro`
        > *   **查询文本**： "公司关于远程工作的政策是什么？"
        > 您确认吗？[是/否]

## 第 0 阶段：环境设置

**关键**：在运行下方的任何 Python 代码片段之前，您必须通过以下步骤确保环境已正确初始化：

1.  **Google Cloud 身份验证**：使用您的 Google Cloud 凭据进行身份验证，并为 Agent Platform 访问配置活动的应用默认凭证（ADC）：
    
    ```bash
    gcloud auth login
    gcloud auth application-default login
    ```
2.  **虚拟环境**：创建并激活一个专用的虚拟环境：
    
    ```bash
    python3 -m venv ~/rag_agent_venv
    source ~/rag_agent_venv/bin/activate
    ```
3.  **安装依赖项**：安装所需的 Agent Platform SDK：
    
    ```bash
    pip install google-cloud-aiplatform google-genai
    ```
4.  **执行**：建议用户每次执行 Python 代码片段时，都必须首先确保此虚拟环境已激活。

## 工作流决策树

1.  **信息收集**：用户是否提供了项目 ID、区域和语料库 ID？

    *   **否** -> 继续进行 [1. 列出语料库和文件] 以发现必要的资源名称和 ID。如果发现失败，则询问用户。
    *   **是** -> 继续。

2.  **任务类型**：用户想做什么？

    *   **列出语料库和文件** -> 继续进行 [1. 列出语料库和文件]。
    *   **检查语料库** -> 继续进行 [2. 获取/检查 Agent Platform RAG 引擎语料库]。
    *   **搜索上下文** -> 继续进行 [3. 检索上下文]。
    *   **使用 RAG 引擎回答问题** -> 继续进行 [4. 使用检索到的上下文回答用户]。

> [!提示] **占位符参数替换**：下方的 Python 脚本使用括号字符串占位符（如 `"{project_id}"`，`"{region}"` 和 `"{corpus_id}"`）。您 **必须** 在生成、提供或执行脚本之前，将它们动态替换为用户提示（或活动上下文）中提供的实际项目 ID、区域和语料库 ID 值。

## 1. 列出语料库和文件（发现）

如果您不知道语料库或文件的资源名称，必须首先列出它们以发现它们。SDK 在转换为列表时会自动处理分页，但您也可以使用手动分页来处理大型集合。

### 1.1 列出和发现语料库

```python
import vertexai
from vertexai.preview import rag

vertexai.init(project="{project_id}", location="{region}")

# 方法 A：列出所有（自动分页）
# SDK 的 Pager 会为您迭代所有页面。
all_corpora = list(rag.list_corpora())
print(f"总共找到 {len(all_corpora)} 个语料库。")
for c in all_corpora:
    print(f"语料库名称：{c.name} | 显示名称：{c.display_name}")

# 方法 B：手动分页（适用于非常大的项目）
pager = rag.list_corpora(page_size=10)
# 处理第一页
for c in pager:
    print(f"语料库：{c.display_name}")

# 如果需要，获取下一页
if pager.next_page_token:
    second_page = rag.list_corpora(
        page_size=10, page_token=pager.next_page_token
    )
```

### 1.2 列出和发现文件

要了解语料库中包含哪些文件（以及文件类型），请列出它们并检查 `display_name`（通常包含扩展名）。

```python
import vertexai
from vertexai.preview import rag

vertexai.init(project="{project_id}", location="{region}")
corpus_name = (
    "projects/{project_id}/locations/{region}/ragCorpora/{corpus_id}"
)

# 自动分页列出文件
files = list(rag.list_files(corpus_name=corpus_name))
print(f"找到 {len(files)} 个文件。")

for f in files:
    # 高级 SDK RagFile 对象通常具有名称、display_name、description
    print(f"文件：{f.display_name} | 资源：{f.name}")
    # 提示：检查扩展名以了解文件类型（PDF、TXT 等）
    if f.display_name.lower().endswith(".pdf"):
        print("  类型：PDF")
    elif f.display_name.lower().endswith(".txt"):
        print("  类型：纯文本")
```

## 2. 获取/检查 Agent Platform RAG 引擎语料库

要检索现有 Agent Platform RAG 引擎语料库的详细信息：

```python
import vertexai
from vertexai.preview import rag

vertexai.init(project="{project_id}", location="{region}")

# 获取特定语料库的详细信息
corpus_name = (
    "projects/{project_id}/locations/{region}/ragCorpora/{corpus_id}"
)
corpus = rag.get_corpus(name=corpus_name)
print(f"语料库名称：{corpus.name}")
print(f"显示名称：{corpus.display_name}")
```

## 3. 检索上下文

根据查询从 RAG 引擎语料库中检索相关上下文：

```python
import vertexai
from vertexai.preview import rag

vertexai.init(project="{project_id}", location="{region}")

corpus_name = (
    "projects/{project_id}/locations/{region}/ragCorpora/{corpus_id}"
)
query = "光速是多少？"

# 检索上下文
response = rag.retrieval_query(
    rag_corpora=[corpus_name],
    text=query,
    similarity_top_k=3
)

for context in response.contexts.contexts:
    print(f"上下文字符串：{context.text}")
    print(f"来源：{context.source_uri}")
```

## 4. 使用检索到的上下文回答用户

使用检索到的上下文与 Agent Platform 模型一起生成基于事实的响应：

```python
from google import genai
from google.genai import types

client = genai.Client(enterprise=True, project="{project_id}", location="{region}")
corpus_name = (
    "projects/{project_id}/locations/{region}/ragCorpora/{corpus_id}"
)

# 定义指向语料库的 Agent Platform RAG 引擎工具
rag_tool = types.Tool(
    retrieval=types.Retrieval(
        vertex_rag_store=types.VertexRagStore(
            rag_resources=[types.VertexRagStoreRagResource(rag_corpus=corpus_name)],
            rag_retrieval_config=types.RagRetrievalConfig(
                top_k=3,
                filter=types.RagRetrievalConfigFilter(
                    vector_similarity_threshold=0.5,
                ),
            ),
        )
    )
)

# 使用 RAG 引擎工具生成内容
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="光速是多少？",
    config=types.GenerateContentConfig(
        tools=[rag_tool]
    )
)
print(response.text)
```
