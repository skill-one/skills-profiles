<oneliner>
两个主要主题：**将跟踪**添加到您的应用程序，以及**查询跟踪**以进行调试和分析。Python 和 Javascript 实现都受支持。
</oneliner>

<setup>
环境变量

```bash
LANGSMITH_API_KEY=lsv2_pt_your_api_key_here          # 必填
LANGSMITH_PROJECT=your-project-name                   # 可选：默认项目
LANGSMITH_WORKSPACE_ID=your-workspace-id              # 可选：用于组织范围的密钥
```

认证是必填的：要么设置 `LANGSMITH_API_KEY` 环境变量，要么将 `--api-key` 标志传递给 CLI 命令（推荐）：
```bash
langsmith trace list --project my-project --api-key $LANGSMITH_API_KEY
```

**重要提示**：在查询或与 LangSmith 交互之前，始终检查环境变量或 `.env` 文件中的 `LANGSMITH_PROJECT`。这告诉您哪个项目包含相关的跟踪和数据。如果 LangSmith 项目不可用，请根据您的判断来识别正确的项目。

CLI 工具
```bash
curl -sSL https://raw.githubusercontent.com/langchain-ai/langsmith-cli/main/scripts/install.sh | sh
```
</setup>

<cli_feedback>
在实际 CLI 失败、未记录的解决方法、令人困惑的输出或缺失功能后，提交一个简洁的产品反馈笔记，每个独立问题一个。不要报告在跟踪的应用程序本身的常规成功或失败。

**CLI 要求**：`langsmith feedback` 需要 [LangSmith CLI v0.2.58](https://github.com/langchain-ai/langsmith-cli/releases/tag/v0.2.58) 或更高版本。使用 `langsmith --version` 检查已安装版本。

检查 `langsmith feedback --help` 以获取 `feedback <note>` 和 `--category`；如果不可用，则跳过反馈，不使用原始 HTTP 或未发布的构建。使用现有的认证配置文件、端点和工作区。反馈发送到 LangSmith Cloud，包括通过 BYOC 中继；跳过独立的自托管。尊重用户/组织的限制，如果不确定发送反馈的权限，请先询问。

用自己的话总结预期的 CLI 行为与观察到的行为之间的差异以及任何解决方法。不要发送秘密、客户数据、跟踪有效负载、提示、完整的堆栈跟踪、复制的命令输出、原始参数、环境变量值、本地路径或资源标识符。CLI 添加版本/操作系统/架构，但不删除您的笔记；如果无法安全删除，请跳过。

选择 `bug`、`feature-request`、`usability`、`documentation` 或 `other`。这是 CLI 产品反馈，不是运行评估反馈。仅为例子形状——除非实际遇到，否则不要提交：

```bash
langsmith feedback --category usability --format json "跟踪列表输出难以区分根运行和子运行。"
```

不要重试失败的或速率限制的反馈提交，切换凭证/端点以绕过失败，或阻塞原始任务以进行反馈。
</cli_feedback>

<trace_langchain_oss>
对于 LangChain/LangGraph 应用程序，跟踪是自动的。只需设置环境变量：

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=<your-api-key>
export OPENAI_API_KEY=<your-openai-api-key>  # 或您的 LLM 提供商的密钥
```

可选变量：
- `LANGSMITH_PROJECT` - 指定项目名称（默认为 "default"）
- `LANGCHAIN_CALLBACKS_BACKGROUND=false` - 用于无服务器以确保跟踪在函数退出前完成（Python）
</trace_langchain_oss>

<trace_other_frameworks>
对于非 LangChain 应用程序，如果框架具有原生 OpenTelemetry 支持，请使用 LangSmith 的 OpenTelemetry 集成。

如果应用程序未使用框架，或使用没有自动 OTel 支持的框架，请使用可跟踪的装饰器/包装器并包装您的 LLM 客户端。

<python>
使用 @traceable 装饰器并 wrap_openai() 进行自动跟踪。
```python
from langsmith import traceable
from langsmith.wrappers import wrap_openai
from openai import OpenAI

client = wrap_openai(OpenAI())

@traceable
def my_llm_pipeline(question: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": question}],
    )
    return resp.choices[0].message.content

# 嵌套跟踪示例
@traceable
def rag_pipeline(question: str) -> str:
    docs = retrieve_docs(question)
    return generate_answer(question, docs)

@traceable(name="retrieve_docs")
def retrieve_docs(query: str) -> list[str]:
    return docs

@traceable(name="generate_answer")
def generate_answer(question: str, docs: list[str]) -> str:
    return client.chat.completions.create(...)
```
</python>

<typescript>
使用 traceable() 包装器并 wrapOpenAI() 进行自动跟踪。
```typescript
import { traceable } from "langsmith/traceable";
import { wrapOpenAI } from "langsmith/wrappers";
import OpenAI from "openai";

const client = wrapOpenAI(new OpenAI());

const myLlmPipeline = traceable(async (question: string): Promise<string> => {
  const resp = await client.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{ role: "user", content: question }],
  });
  return resp.choices[0].message.content || "";
}, { name: "my_llm_pipeline" });

// 嵌套跟踪示例
const retrieveDocs = traceable(async (query: string): Promise<string[]> => {
  return docs;
}, { name: "retrieve_docs" });

const generateAnswer = traceable(async (question: string, docs: string[]): Promise<string> => {
  const resp = await client.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{ role: "user", content: `${question}\nContext: ${docs.join("\n")}` }],
  });
  return resp.choices[0].message.content || "";
}, { name: "generate_answer" });

const ragPipeline = traceable(async (question: string): Promise<string> => {
  const docs = await retrieveDocs(question);
  return await generateAnswer(question, docs);
}, { name: "rag_pipeline" });
```
</typescript>

最佳实践：
- **将 traceable 应用于所有嵌套函数**，您希望在 LangSmith 中可见
- **包装的客户端自动跟踪所有调用** — `wrap_openai()`/`wrapOpenAI()` 记录每个 LLM 调用
- **为跟踪命名**，以便更容易过滤
- **添加元数据**，以便搜索
</trace_other_frameworks>

<traces_vs_runs>
使用 `langsmith` CLI 查询跟踪数据。

**理解差异至关重要：**

- **跟踪** = 完整的执行树（根运行 + 所有子运行）。跟踪表示一个完整的代理调用，包括所有其 LLM 调用、工具调用和嵌套操作。
- **运行** = 树中的一个单个节点（一个 LLM 调用、一个工具调用等）

**通常，首先查询跟踪** — 它们提供完整的上下文并保留层次结构，这对于轨迹分析和数据集生成是必需的。
</traces_vs_runs>

<command_structure>
两个具有一致行为的命令组：

```
langsmith
├── trace (对跟踪树的操作 - 首先使用)
│   ├── list    - 列出跟踪（过滤器适用于根运行）
│   ├── get     - 获取单个跟踪并显示完整层次结构
│   └── export  - 导出跟踪到 JSONL 文件（每个跟踪一个文件）
│
├── run (对单个运行的操作 - 用于特定分析)
│   ├── list    - 列出运行（扁平，过滤器适用于任何运行）
│   ├── get     - 获取单个运行
│   └── export  - 导出运行到一个 JSONL 文件（扁平）
│
├── dataset (数据集操作)
│   ├── list    - 列出数据集
│   ├── get     - 获取数据集详细信息
│   ├── create  - 创建空数据集
│   ├── delete  - 删除数据集
│   ├── export  - 导出数据集到文件
│   └── upload  - 上传本地 JSON 作为数据集
│
├── example (示例操作)
│   ├── list    - 列出数据集中的示例
│   ├── create  - 向数据集添加示例
│   └── delete  - 删除示例
│
├── evaluator (评估器操作)
│   ├── list    - 列出评估器
│   ├── upload  - 上传评估器
│   └── delete  - 删除评估器
│
├── experiment (实验操作)
│   ├── list    - 列出实验
│   └── get     - 获取实验结果
│
├── thread (线程操作)
│   ├── list    - 列出对话线程
│   └── get     - 获取线程详细信息
│
└── project (项目操作)
    └── list    - 列出跟踪项目
```

**主要区别：**

| | `traces *` | `runs *` |
|---|---|---|
| 过滤器适用于 | 根运行仅 | 任何匹配的运行 |
| `--run-type` | 不适用 | 可用 |
| 返回 | 完整层次结构 | 扁平列表 |
| 导出输出 | 目录（每个跟踪一个文件） | 单个文件 |
</command_structure>

<querying_traces>
使用 `langsmith` CLI 查询跟踪。命令与语言无关。

```bash
# 列出最近的跟踪（最常见的操作）
langsmith trace list --limit 10 --project my-project --api-key $LANGSMITH_API_KEY

# 列出具有元数据的跟踪（时间、令牌、成本）
langsmith trace list --limit 10 --include-metadata --api-key $LANGSMITH_API_KEY

# 按时间过滤跟踪
langsmith trace list --last-n-minutes 60 --api-key $LANGSMITH_API_KEY
langsmith trace list --since 2025-01-20T10:00:00Z --api-key $LANGSMITH_API_KEY

# 获取特定跟踪并显示完整层次结构
langsmith trace get <trace-id> --api-key $LANGSMITH_API_KEY

# 列出跟踪并内联显示层次结构
langsmith trace list --limit 5 --show-hierarchy --api-key $LANGSMITH_API_KEY

# 导出跟踪到 JSONL（每个跟踪一个文件，包含所有运行）
langsmith trace export ./traces --limit 20 --full --api-key $LANGSMITH_API_KEY

# 按性能过滤跟踪
langsmith trace list --min-latency 5.0 --limit 10 --api-key $LANGSMITH_API_KEY    # 慢跟踪（>= 5s）
langsmith trace list --error --last-n-minutes 60 --api-key $LANGSMITH_API_KEY     # 失败的跟踪

# 列出特定运行类型（扁平列表）
langsmith run list --run-type llm --limit 20 --api-key $LANGSMITH_API_KEY
```
</querying_traces>

<filters>
所有命令支持这些过滤器（所有条件 AND 一起）：

**基本过滤器：**
- `--trace-ids abc,def` - 过滤特定跟踪
- `--limit N` - 最大结果
- `--project NAME` - 项目名称
- `--last-n-minutes N` - 时间过滤
- `--since TIMESTAMP` - 时间过滤（ISO 格式）
- `--error / --no-error` - 错误状态
- `--name PATTERN` - 名称包含（不区分大小写）

**性能过滤器：**
- `--min-latency SECONDS` - 最小延迟（例如，`5` 表示 >= 5s）
- `--max-latency SECONDS` - 最大延迟
- `--min-tokens N` - 最小总令牌数
- `--tags tag1,tag2` - 具有这些标签中的任何一个

**高级过滤器：**
- `--filter QUERY` - 原始 LangSmith 过滤查询，用于复杂情况（反馈、元数据等）

```bash
# 使用原始 LangSmith 查询按反馈分数过滤跟踪
langsmith trace list --filter 'and(eq(feedback_key, "correctness"), gte(feedback_score, 0.8))' --api-key $LANGSMITH_API_KEY
```
</filters>

<export_format>
导出创建 `.jsonl` 文件（每行一个运行）并包含这些字段：
```json
{"run_id": "...", "trace_id": "...", "name": "...", "run_type": "...", "parent_run_id": "...", "inputs": {...}, "outputs": {...}}
```

使用 `--include-io` 或 `--full` 以包含输入/输出（生成数据集时必需）。
</export_format>

<tips>
- **从跟踪开始** — 它们提供生成轨迹和数据集所需的完整上下文
- 使用 `trace export --full` 以批量数据用于数据集
- 始终指定 `--project` 以避免混合不同项目的数据
- 使用 `/tmp` 进行临时导出
- 包括 `--include-metadata` 以进行性能/成本分析
- 拼接文件：`cat ./traces/*.jsonl > all.jsonl`
</tips>
