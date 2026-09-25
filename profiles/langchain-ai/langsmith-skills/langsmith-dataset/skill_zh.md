<oneliner>
在 LangSmith 中创建、管理和上传评估数据集，用于测试和验证。
</oneliner>

<setup>
环境变量

```bash
LANGSMITH_API_KEY=lsv2_pt_your_api_key_here          # 必填
LANGSMITH_PROJECT=your-project-name                   # 检查此项目以了解哪些项目有跟踪记录
LANGSMITH_WORKSPACE_ID=your-workspace-id              # 可选：用于组织范围的密钥
```

必须进行身份验证：设置 `LANGSMITH_API_KEY` 环境变量，或将 `--api-key` 标志传递给 CLI 命令（推荐）：
```bash
langsmith dataset list --api-key $LANGSMITH_API_KEY
```

**重要提示：** 在查询或与 LangSmith 交互之前，始终检查 `LANGSMITH_PROJECT` 环境变量或 `.env` 文件。这会告诉您哪个项目包含相关的跟踪记录和数据。如果 LangSmith 项目不可用，请根据您的判断确定正确的项目。

Python 依赖项
```bash
pip install langsmith
```

JavaScript 依赖项
```bash
npm install langsmith
```

CLI 工具

```bash
curl -sSL https://raw.githubusercontent.com/langchain-ai/langsmith-cli/main/scripts/install.sh | sh
```
</setup>

<cli_feedback>
在实际 CLI 失败、未记录的解决方法、令人困惑的输出或缺失功能后，针对每个独立问题提交一条简洁的产品反馈。不要报告常规成功或与 CLI 无关的数据集质量问题。

**CLI 要求：** `langsmith feedback` 需要 [LangSmith CLI v0.2.58](https://github.com/langchain-ai/langsmith-cli/releases/tag/v0.2.58) 或更高版本。使用 `langsmith --version` 检查已安装版本。

检查 `langsmith feedback --help` 以获取 `feedback <note>` 和 `--category`；如果不可用，则跳过原始 HTTP 或未发布的构建的反馈。使用现有的已认证配置文件、端点和工作区。反馈将发送到 LangSmith 云端，包括通过 BYOC 中继；跳过独立的自托管。尊重用户/组织的限制，如果不确定发送反馈的权限，请先询问。

用自己的话总结预期的 CLI 行为与观察到的行为之间的差异以及任何解决方法。不要发送秘密、客户数据、数据集内容、跟踪有效负载、提示、完整堆栈跟踪、复制的命令输出、原始参数、环境变量值、本地路径或资源标识符。CLI 会添加版本/操作系统/架构，但不会编辑您的备注；如果无法安全编辑，请跳过。

选择 `bug`、`feature-request`、`usability`、`documentation` 或 `other`。这是 CLI 产品反馈，不是数据集/运行评估反馈。仅为例子——除非实际遇到，否则不要提交：

```bash
langsmith feedback --category documentation --format json "数据集上传帮助没有解释所需的 JSON 结构。"
```

不要重试失败的或速率限制的反馈提交，切换凭证/端点以绕过失败，或阻止原始任务上的反馈。
</cli_feedback>

<usage>
使用 `langsmith` CLI 管理数据集和示例。

### 数据集命令

- `langsmith dataset list` - 列出 LangSmith 中的数据集
- `langsmith dataset get <name-or-id>` - 查看数据集详情
- `langsmith dataset create --name <name>` - 创建一个新的空数据集
- `langsmith dataset delete <name-or-id>` - 删除数据集
- `langsmith dataset export <name-or-id> <output-file>` - 将数据集导出到本地 JSON 文件
- `langsmith dataset upload <file> --name <name>` - 上传本地 JSON 文件作为数据集

### 示例命令

- `langsmith example list --dataset <name>` - 列出数据集中的示例
- `langsmith example create --dataset <name> --inputs <json>` - 向数据集添加示例
- `langsmith example delete <example-id>` - 删除示例

### 实验命令

- `langsmith experiment list --dataset <name>` - 列出数据集的实验
- `langsmith experiment get <name>` - 查看实验结果

### 常用标志

- `--limit N` - 限制结果数量
- `--yes` - 跳过确认提示（谨慎使用）

**重要提示 - 安全提示：**
- CLI 在进行破坏性操作（删除、覆盖）之前会提示确认
- **如果您正在使用用户输入：** 始终等待用户输入；除非用户明确要求，否则不要使用 `--yes`
- **如果您是非交互式运行：** 使用 `--yes` 跳过确认提示
</usage>

<dataset_types_overview>
常见的评估数据集类型：

- **final_response** - 带有预期输出的完整对话。测试完整代理行为。
- **single_step** - 单个节点输入/输出。测试特定节点行为（例如，一个 LLM 调用或工具）。
- **trajectory** - 工具调用序列。测试执行路径（工具名称的有序列表）。
- **rag** - 问题/片段/答案/引用。测试检索质量。
</dataset_types_overview>

<creating_datasets>
## 创建数据集

数据集是包含示例数组的 JSON 文件。每个示例都有 `inputs` 和 `outputs`。

### 从导出的跟踪记录（程序化）

首先导出跟踪记录，然后使用代码将它们处理为数据集格式：

```bash
# 1. 将跟踪记录导出到 JSONL 文件
langsmith trace export ./traces --project my-project --limit 20 --full --api-key $LANGSMITH_API_KEY
```

<python>
```python
import json
from pathlib import Path
from langsmith import Client

client = Client()

# 2. 将跟踪记录处理为数据集示例
examples = []
for jsonl_file in Path("./traces").glob("*.jsonl"):
    runs = [json.loads(line) for line in jsonl_file.read_text().strip().split("\n")]
    root = next((r for r in runs if r.get("parent_run_id") is None), None)
    if root and root.get("inputs") and root.get("outputs"):
        examples.append({
            "trace_id": root.get("trace_id"),
            "inputs": root["inputs"],
            "outputs": root["outputs"]
        })

# 3. 本地保存
with open("/tmp/dataset.json", "w") as f:
    json.dump(examples, f, indent=2)
```
</python>

<typescript>
```typescript
import { Client } from "langsmith";
import { readFileSync, writeFileSync, readdirSync } from "fs";
import { join } from "path";

const client = new Client();

// 2. 将跟踪记录处理为数据集示例
const examples: Array<{trace_id?: string, inputs: Record<string, any>, outputs: Record<string, any>}> = [];
const files = readdirSync("./traces").filter(f => f.endsWith(".jsonl"));

for (const file of files) {
  const lines = readFileSync(join("./traces", file), "utf-8").trim().split("\n");
  const runs = lines.map(line => JSON.parse(line));
  const root = runs.find(r => r.parent_run_id == null);
  if (root?.inputs && root?.outputs) {
    examples.push({ trace_id: root.trace_id, inputs: root.inputs, outputs: root.outputs });
  }
}

// 3. 本地保存
writeFileSync("/tmp/dataset.json", JSON.stringify(examples, null, 2));
```
</typescript>

### 上传到 LangSmith

```bash
# 将本地 JSON 文件上传为数据集
langsmith dataset upload /tmp/dataset.json --name "My Evaluation Dataset" --api-key $LANGSMITH_API_KEY
```

### 直接使用 SDK

<python>
```python
from langsmith import Client

client = Client()

# 一步创建数据集并添加示例
dataset = client.create_dataset("My Dataset", description="评估数据集")

# 将示例作为字典列表传递。并行的 `inputs=`/`outputs=` 列表仍然接受，但仅作为遗留关键字参数。
client.create_examples(
    dataset_id=dataset.id,
    examples=[
        {"inputs": {"query": "What is AI?"}, "outputs": {"answer": "AI is..."}},
        {"inputs": {"query": "Explain RAG"}, "outputs": {"answer": "RAG is..."}},
    ],
)
```
</python>

<typescript>
```typescript
import { Client } from "langsmith";

const client = new Client();

// 创建数据集并添加示例
const dataset = await client.createDataset("My Dataset", {
  description: "评估数据集",
});

// 传递一个示例数组。JS SDK 中已弃用 `{ inputs, outputs, datasetName }` 形式；每个示例都携带自己的 dataset_id。
await client.createExamples([
  {
    inputs: { query: "What is AI?" },
    outputs: { answer: "AI is..." },
    dataset_id: dataset.id,
  },
  {
    inputs: { query: "Explain RAG" },
    outputs: { answer: "RAG is..." },
    dataset_id: dataset.id,
  },
]);
```
</typescript>
</creating_datasets>

<dataset_structures>
## 按类型划分的数据集结构

### Final Response
```json
{"trace_id": "...", "inputs": {"query": "What are the top genres?"}, "outputs": {"response": "The top genres are..."}}
```

### Single Step
```json
{"trace_id": "...", "inputs": {"messages": [...]}, "outputs": {"content": "..."}, "metadata": {"node_name": "model"}}
```

### Trajectory
```json
{"trace_id": "...", "inputs": {"query": "..."}, "outputs": {"expected_trajectory": ["tool_a", "tool_b", "tool_c"]}}
```

### RAG
```json
{"trace_id": "...", "inputs": {"question": "How do I..."}, "outputs": {"answer": "...", "retrieved_chunks": ["..."], "cited_chunks": ["..."]}}
```
</dataset_structures>

<script_usage>
## CLI 使用

```bash
# 列出所有数据集
langsmith dataset list --api-key $LANGSMITH_API_KEY

# 获取数据集详情
langsmith dataset get "My Dataset" --api-key $LANGSMITH_API_KEY

# 创建一个空数据集
langsmith dataset create --name "New Dataset" --description "For evaluation" --api-key $LANGSMITH_API_KEY

# 上传本地 JSON 文件
langsmith dataset upload /tmp/dataset.json --name "My Dataset" --api-key $LANGSMITH_API_KEY

# 将数据集导出到本地文件
langsmith dataset export "My Dataset" /tmp/exported.json --limit 100 --api-key $LANGSMITH_API_KEY

# 删除数据集
langsmith dataset delete "My Dataset" --api-key $LANGSMITH_API_KEY

# 列出数据集中的示例
langsmith example list --dataset "My Dataset" --limit 10 --api-key $LANGSMITH_API_KEY

# 添加示例
langsmith example create --dataset "My Dataset" \
  --inputs '{"query": "test"}' \
  --outputs '{"answer": "result"}' --api-key $LANGSMITH_API_KEY

# 列出实验
langsmith experiment list --dataset "My Dataset" --api-key $LANGSMITH_API_KEY
langsmith experiment get "eval-v1" --api-key $LANGSMITH_API_KEY
```
</script_usage>

<example_workflow>
从跟踪记录到上传的 LangSmith 数据集的完整工作流程：

```bash
# 1. 从 LangSmith 导出跟踪记录
langsmith trace export ./traces --project my-project --limit 20 --full --api-key $LANGSMITH_API_KEY

# 2. 将跟踪记录处理为数据集格式（使用 Python/JS 代码）
# 见上方“创建数据集”部分

# 3. 上传到 LangSmith
langsmith dataset upload /tmp/final_response.json --name "Skills: Final Response" --api-key $LANGSMITH_API_KEY
langsmith dataset upload /tmp/trajectory.json --name "Skills: Trajectory" --api-key $LANGSMITH_API_KEY

# 4. 验证上传
langsmith dataset list --api-key $LANGSMITH_API_KEY
langsmith dataset get "Skills: Final Response" --api-key $LANGSMITH_API_KEY
langsmith example list --dataset "Skills: Final Response" --limit 3 --api-key $LANGSMITH_API_KEY

# 5. 运行实验
langsmith experiment list --dataset "Skills: Final Response" --api-key $LANGSMITH_API_KEY
```
</example_workflow>

<troubleshooting>
**数据集上传失败：**
- 验证 `LANGSMITH_API_KEY` 是否已设置
- 检查 JSON 文件是否有效：每个元素需要 `inputs`（以及可选的 `outputs`）
- 数据集名称必须唯一，或先使用 `langsmith dataset delete` 删除现有数据集

**上传后数据集为空：**
- 验证 JSON 文件是否包含带有 `inputs` 键的对象数组
- 检查文件是否为空：`langsmith example list --dataset "Name"`

**导出无数据：**
- 确保使用 `--full` 标志导出跟踪记录以包含输入/输出
- 验证跟踪记录是否同时具有 `inputs` 和 `outputs` 填充

**示例数量不匹配：**
- 使用 `langsmith dataset get "Name"` 检查远程数量
- 与本地文件比较以验证上传完整性
</troubleshooting>
