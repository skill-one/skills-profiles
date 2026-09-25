<oneliner>
三个核心组件：**(1) 创建评估器** - LLM作为法官，自定义代码；**(2) 定义运行函数** - 捕获代理输出/轨迹以进行评估；**(3) 运行评估** - 本地使用`evaluate()`或通过上传的评估器自动运行。包含Python和TypeScript示例。
</oneliner>

<setup>
环境变量

```bash
LANGSMITH_API_KEY=your-api-key                        # `langsmith auth login`的替代方案
LANGSMITH_ENDPOINT=https://api.smith.langchain.com   # SDK/CLI环境
LANGSMITH_PROJECT=your-project-name                   # 仅用于跟踪/运行查询的默认值
LANGSMITH_WORKSPACE_ID=your-workspace-id              # 可选：用于组织范围的密钥
OPENAI_API_KEY=your-openai-key                        # 用于本地执行的OpenAI法官
```

使用保存的CLI配置文件进行身份验证（推荐）：
```bash
langsmith auth login
langsmith auth info
```

或者，设置`LANGSMITH_API_KEY`。隐藏的`--api-key`标志仍然可用于兼容性，但不要将密钥直接放在命令或日志中。在从保存的配置文件中选择时使用`--profile`或`LANGSMITH_PROFILE`。

**重要提示：** `LANGSMITH_PROJECT`默认跟踪和运行查询；它不会选择评估器目标。评估器创建和上传需要显式的`--dataset`或`--project`。

**CLI和SDK身份验证是分开的：** CLI OAuth配置文件仅验证`langsmith ...`命令。Python和TypeScript SDK不会自动使用它。在评估器CRUD期间使用SDK之前，请确认`LANGSMITH_ENDPOINT`、`LANGSMITH_API_KEY`以及当需要时`LANGSMITH_WORKSPACE_ID`指向与`langsmith auth info`相同的环境和工作区。如果CLI和SDK指向不同的环境，请停止。

在任何SDK辅助的CRUD之前使用只读SDK预检：

```python
from langsmith import Client

client = Client()
client.read_dataset(dataset_name="My Dataset")
```

Python依赖项
```bash
pip install langsmith langchain-openai python-dotenv
```

CLI工具
```bash
curl -fsSL https://cli.langsmith.com/install.sh | sh
langsmith self-update
```

JavaScript依赖项
```bash
npm install langsmith openai
```
</setup>

<cli_feedback>
在实际CLI故障、未记录的解决方法、令人困惑的输出或缺失功能后，针对每个不同问题提交一条简洁的产品反馈笔记。不要报告常规成功或与CLI无关的低评估分数/应用程序故障。

**CLI要求：** `langsmith feedback`需要[LangSmith CLI v0.2.58](https://github.com/langchain-ai/langsmith-cli/releases/tag/v0.2.58)或更高版本。使用`langsmith --version`检查安装版本。

检查`langsmith feedback --help`以获取`feedback <note>`和`--category`；如果不可用，则在不使用原始HTTP或未发布的构建的情况下跳过反馈。使用现有的已验证配置文件、端点和工作区。反馈发送到LangSmith Cloud，包括通过BYOC中继；跳过独立的自我托管。尊重用户/组织的限制，如果不确定发送反馈的权限，请先询问。

用自己的话总结预期与CLI行为的差异以及任何解决方法。永远不要发送密钥、客户数据、评估器提示、数据集内容、跟踪有效负载、完整堆栈跟踪、复制的命令输出、原始参数、环境变量值、本地路径或资源标识符。CLI添加版本/操作系统/架构，但不会编辑你的笔记；如果无法安全编辑，请跳过。

选择`bug`、`feature-request`、`usability`、`documentation`或`other`。这是CLI产品反馈，不是评估器分数或评论。仅为例子形状——除非实际遇到，否则不要提交：

```bash
langsmith feedback --category feature-request --format json "请支持在显示名称冲突时通过ID选择单个评估器。"
```

不要重试失败的或速率限制的反馈提交，切换凭证/端点以绕过故障，或阻止原始任务以反馈。
</cli_feedback>

<crucial_requirement>
## 黄金法则：实施前先检查

**关键：** 在编写任何评估器或提取逻辑之前，你必须：
1. **在样本输入上运行你的代理**并捕获实际输出
2. **检查输出** - 打印它，查询LangSmith跟踪，了解确切结构
3. **然后**编写处理该输出的代码

输出结构因框架、代理类型和配置而异。永远不要假设形状——总是先验证。查询LangSmith跟踪，以了解当输出不包含所需数据时如何从执行中提取。
</crucial_requirement>

<evaluator_format>
## 离线评估器与在线评估器

**离线评估器**（附加到数据集）：
- 函数签名：`(run, example)` - 接收运行输出和数据集示例
- 用例：比较代理输出与数据集中的预期值
- 上传时使用：`--dataset "Dataset Name"`

**在线评估器**（附加到项目）：
- 函数签名：`(run)` - 仅接收运行输出，没有示例参数
- 用例：生产运行中的实时质量检查（没有参考数据）
- 上传时使用：`--project "Project Name"`

**关键 - 返回格式：**
- 每个评估器只返回**一个指标**。对于多个指标，创建多个评估器函数。
- 不要返回`{"metric_name": value}`或指标列表——这将导致错误。

**关键 - 本地与上传的差异：**

| | 本地`evaluate()` | 上传到LangSmith |
|---|---|---|
| **列名** | Python：自动从函数名派生。TypeScript：必须包含`key`字段或列无标题 | 来自上传时设置的评估器名称。不要包含`key`——它将创建一个重复的列 |
| **Python `run`类型** | `RunTree`对象 → `run.outputs`（属性） | `dict` → `run["outputs"]`（下标）。处理两者：`run.outputs if hasattr(run, "outputs") else run.get("outputs", {})` |
| **TypeScript `run`类型** | 始终属性访问：`run.outputs?.field` | 始终属性访问：`run.outputs?.field` |
| **Python返回** | `{"score": value, "comment": "..."}` | `{"score": value, "comment": "..."}` |
| **TypeScript返回** | `{ key: "name", score: value, comment: "..." }` | `{ score: value, comment: "..." }` |
</evaluator_format>

<evaluator_types>
- **LLM作为法官** - 使用LLM对输出进行评分。最适合主观质量（准确性、帮助性、相关性）。
- **自定义代码** - 确定性逻辑。最适合客观检查（精确匹配、轨迹验证、格式合规性）。
</evaluator_types>

<llm_judge>
## LLM作为法官评估器

使用`langsmith evaluator create-llm`创建服务器管理的LLM作为法官运行规则。它需要`--model-config`加上恰好一个目标（`--dataset`或`--project`）。提供`--prompt`和`--schema` JSON文件，或使用`--hub-ref`的Prompt Hub引用。

### LLM作为法官运行规则的本地CLI CRUD

以下原生生命周期管理附加到数据集或项目的LLM作为法官评估器。

**创建**

```bash
langsmith evaluator create-llm \
  --name "Accuracy Judge" \
  --dataset "My Dataset" \
  --prompt prompt.json \
  --schema schema.json \
  --model-config model.json
```

使用`--project`代替`--dataset`以创建在线评估器。当法官提示存储在Prompt Hub中时，使用`--hub-ref owner/prompt:latest`代替`--prompt`和`--schema`。

### 模型配置

`--model-config`需要一个服务器支持的序列化模型配置。永远不要从本地LangChain模型构造函数中发明`model.json`。从已知可工作的LangSmith评估器、LangSmith评估器UI或目标环境的其他文档化来源获取它。在创建或替换评估器之前，确认目标服务器允许序列化模型类。

`langsmith evaluator get`不会导出完整的序列化模型配置。如果创建失败并显示`Deserialization ... is not allowed`，模型配置包含服务器允许列表中禁止的类。不要重试猜测序列化对象；获取支持的配置或询问环境管理员。

**读取**

```bash
# 列出所有附加的评估器规则
langsmith evaluator list --format json

# 获取具有此确切显示名称的每个规则
langsmith evaluator get "Accuracy Judge"

# 使用项目会话ID缩小项目规则
langsmith evaluator get "Accuracy Judge" --session-id <project-session-id>
```

`get`基于显示名称，可能会返回多个规则。它报告规则元数据和选定的LLM字段，但不会导出完整的内联提示、模式和模型配置。

**更新/替换**

没有单独的`update`子命令。重新运行`create-llm`，使用相同的名称和目标加上`--replace`；CLI会在PATCH匹配规则之前提示。再次提供完整的所需LLM配置。

```bash
langsmith evaluator create-llm \
  --name "Accuracy Judge" \
  --dataset "My Dataset" \
  --prompt prompt-v2.json \
  --schema schema-v2.json \
  --model-config model-v2.json \
  --replace
```

**删除**

```bash
# 删除前检查每个匹配项
langsmith evaluator get "Accuracy Judge"
langsmith evaluator delete "Accuracy Judge"
```

`delete`基于名称，并删除**所有具有该显示名称的工作区运行规则**，即使它们位于不同的数据集或项目中。如果多个规则匹配且只有一个应该被删除，请停止而不是使用原生删除命令；精确ID目标删除尚未通过`langsmith evaluator`公开。

对于快速本地开发或需要本地包的法官，定义本地评估器并将其传递给`evaluate(evaluators=[...])`。

<python>
```python
from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI

class Grade(TypedDict):
    reasoning: Annotated[str, ..., "解释你的推理"]
    is_accurate: Annotated[bool, ..., "如果响应准确则为True"]

judge = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Grade, method="json_schema", strict=True)

async def accuracy_evaluator(run, example):
    run_outputs = run.outputs if hasattr(run, "outputs") else run.get("outputs", {}) or {}
    example_outputs = example.outputs if hasattr(example, "outputs") else example.get("outputs", {}) or {}
    grade = await judge.ainvoke([{"role": "user", "content": f"预期: {example_outputs}\n实际: {run_outputs}\n这是准确的吗?"}])
    return {"score": 1 if grade["is_accurate"] else 0, "comment": grade["reasoning"]}
```
</python>

<typescript>
```javascript
import OpenAI from "openai";

const openai = new OpenAI();

async function accuracyEvaluator(run, example) {
    const runOutputs = run.outputs ?? {};
    const exampleOutputs = example.outputs ?? {};

    const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    temperature: 0,
    response_format: { type: "json_object" },
    messages: [
        { role: "system", content: '以JSON格式回复：{"is_accurate": boolean, "reasoning": string}' },
        { role: "user", content: `预期: ${JSON.stringify(exampleOutputs)}\n实际: ${JSON.stringify(runOutputs)}\n这是准确的吗?` }
    ]
    });

    const grade = JSON.parse(response.choices[0].message.content);
    return { score: grade.is_accurate ? 1 : 0, comment: grade.reasoning };
}
```
</typescript>
</llm_judge>

<code_evaluators>
## 自定义代码评估器

**在编写评估器之前：**
1. 检查你的数据集以了解预期字段名称（见上述黄金法则）
2. 测试你的运行函数并验证其输出结构与数据集模式匹配
3. 查询LangSmith跟踪以调试任何不匹配

<python>
```python
def trajectory_evaluator(run, example):
    run_outputs = run.outputs if hasattr(run, "outputs") else run.get("outputs", {}) or {}
    example_outputs = example.outputs if hasattr(example, "outputs") else example.get("outputs", {}) or {}
    # 重要提示：用你的实际字段名称替换这些占位符
    # 1. 查询你的LangSmith跟踪以查看运行输出中存在哪些字段
    # 2. 检查你的数据集模式以获取预期字段名称
    # 注意：轨迹数据可能不会出现在默认输出中——与跟踪进行验证！
    actual = run_outputs.get("YOUR_TRAJECTORY_FIELD", [])
    expected = example_outputs.get("YOUR_EXPECTED_FIELD", [])
    return {"score": 1 if actual == expected else 0, "comment": f"预期 {expected}, 得到 {actual}"}
```
</python>

<typescript>
```javascript
function trajectoryEvaluator(run, example) {
    const runOutputs = run.outputs ?? {};
    const exampleOutputs = example.outputs ?? {};
    // 重要提示：用你的实际字段名称替换这些占位符
    // 1. 查询你的LangSmith跟踪以查看运行输出中存在哪些字段
    // 2. 检查你的数据集模式以获取预期字段名称
    const actual = runOutputs.YOUR_TRAJECTORY_FIELD ?? [];
    const expected = exampleOutputs.YOUR_EXPECTED_FIELD ?? [];
    const match = JSON.stringify(actual) === JSON.stringify(expected);
    return { score: match ? 1 : 0, comment: `预期 ${JSON.stringify(expected)}, 得到 ${JSON.stringify(actual)}` };
}
```
</typescript>
</code_evaluators>

<run_functions>
## 定义运行函数

运行函数执行你的代理并返回输出以进行评估。

**关键 - 首先测试你的运行函数：**
在编写评估器之前，你必须测试你的运行函数并检查实际输出结构。输出形状因框架、代理类型和配置而异。

**调试工作流：**
1. 在样本输入上运行你的代理一次
2. 查询跟踪以查看执行结构
3. 打印原始输出并验证与跟踪以输出包含正确的数据
4. 根据需要调整运行函数
4. 验证你的输出与数据集模式匹配

**尽你所能使你的运行函数输出与数据集模式匹配。** 这使评估器变得简单且可重用。如果匹配不可行，你的评估器必须知道如何从每一侧提取和比较正确的字段。

<python>
```python
def run_agent(inputs: dict) -> dict:
    result = your_agent.run(inputs)
    # 始终首先检查输出形状 - 运行此命令，检查打印，查询跟踪
    print(f"DEBUG - 类型: {type(result)}, 键: {result.keys() if hasattr(result, 'keys') else 'N/A'}")
    print(f"DEBUG - 值: {result}")
    return {"output": result}  # 调整以匹配你的数据集模式
```
</python>

<typescript>
```javascript
async function runAgent(inputs) {
    const result = await yourAgent.invoke(inputs);
    // 始终首先检查输出形状
    console.log("DEBUG - 类型:", typeof result, "键:", Object.keys(result));
    console.log("DEBUG - 值:", result);
    return { output: result };  // 调整以匹配你的数据集模式
}
```
</typescript>

### 捕获轨迹

对于轨迹评估，你的运行函数必须在执行期间捕获工具调用。

**关键：** 运行输出格式因框架和代理类型而异。你必须先检查再实施：

**LangGraph代理（LangChain OSS）：** 使用`stream_mode="debug"`与`subgraphs=True`捕获嵌套子代理工具调用。

```python
import uuid

def run_agent_with_trajectory(agent, inputs: dict) -> dict:
    config = {"configurable": {"thread_id": f"eval-{uuid.uuid4()}"}}
    trajectory = []
    final_result = None

    for chunk in agent.stream(inputs, config=config, stream_mode="debug", subgraphs=True):
        # 第一步：打印块以了解结构
        print(f"DEBUG块: {chunk}")

        # 第二步：根据你观察到的结构编写提取逻辑
        # ... 你的提取逻辑 ...

    # 重要提示：运行后，查询LangSmith跟踪以验证
    # 你的轨迹数据是否完整。默认输出可能缺少跟踪中出现的工具调用。
    return {"output": final_result, "trajectory": trajectory}
```

**自定义/非LangChain代理：**

1. **首先检查输出** - 运行你的代理并检查结果结构。轨迹数据可能已经包含在输出中（例如，`result.tool_calls`、`result.steps`等）
2. **回调/钩子** - 如果你的框架支持执行回调，注册一个钩子，在每次调用时记录工具名称
3. **解析执行日志** - 作为最后手段，从结构化日志或跟踪数据中提取工具名称

关键是捕获执行时的工具名称，而不是定义时的名称。
</run_functions>

<upload>
## 上传评估器到LangSmith

**重要提示 - 自动运行行为：**
上传到数据集的评估器在你在该数据集上运行实验时**自动运行**。你**不需要**将它们传递给`evaluate()`——只需运行你的代理针对数据集，上传的评估器将自动执行。

**重要提示 - 本地与上传：**
上传的评估器在沙盒环境中运行，包访问非常有限。仅使用内置/标准库导入，并将所有导入**放在**评估器函数体内。对于数据集（离线）评估器，优先使用`evaluate(evaluators=[...])`本地运行——这提供了完整的包访问。

**重要提示 - 代码与结构化评估器：**
- **代码评估器：** 使用`langsmith evaluator upload`上传。它们在有限的环境中运行，没有外部包，并且非常适合确定性逻辑。
- **结构化评估器（LLM作为法官）：** 使用`langsmith evaluator create-llm`创建，使用模型配置以及提示/模式文件或`--hub-ref`。

**重要提示 - 选择正确的目标：**
- `--dataset`：离线评估器，具有`(run, example)`签名 - 用于与预期值比较
- `--project`：在线评估器，具有`(run)`签名 - 用于实时质量检查

你必须指定一个。不支持全局评估器。

```bash
# 列出所有附加的评估器规则
langsmith evaluator list

# 通过显示名称检查匹配的规则
langsmith evaluator get "Trajectory Match"

# 通过会话ID检查项目规则（不是项目名称）
langsmith evaluator get --session-id <project-session-id>

# 上传离线评估器（附加到数据集）
langsmith evaluator upload \
  --name "Trajectory Match" \
  --function trajectory_evaluator \
  --dataset "My Dataset" \
  my_evaluators.py

# 上传在线评估器（附加到项目）
langsmith evaluator upload \
  --name "Quality Check" \
  --function quality_check \
  --project "Production Agent" \
  my_evaliators.py

# 使用相同的名称和目标替换现有规则（首先提示）
langsmith evaluator upload \
  --name "Trajectory Match" \
  --function trajectory_evaluator \
  --dataset "My Dataset" \
  --replace \
  my_evaluators.py

# 通过显示名称删除（首先提示）
langsmith evaluator delete "Trajectory Match"
```

**重要提示 - 安全提示：**
- `upload --replace`和`create-llm --replace`首先修补匹配的规则和提示
- `delete NAME`删除**工作区中具有该显示名称的每个规则**，可能跨越多个目标；首先运行`get NAME`并检查所有匹配项
- **除非用户明确要求，否则永远不要使用`--yes`标志**

### CRUD验证

仅验证用户请求的生命周期操作：

- 确认CLI和任何SDK指向相同的环境和工作区
- 使用`list`和`get`验证创建
- 使用`--replace`验证替换，当请求时
- 仅使用唯一的可丢弃名称和明确授权测试删除
- 如果无法安全识别预期目标，则停止

</upload>

<best_practices>
1. **为LLM法官使用结构化输出** - 比解析自由文本更可靠
2. **使评估器与数据集类型匹配**
   - 最终响应 → LLM作为法官用于质量
   - 轨迹 → 自定义代码用于序列
3. **使用异步进行LLM法官** - 启用并行评估
4. **独立测试评估器** - 首先在已知好/坏示例上验证
5. **选择正确的语言**
   - Python：用于Python代理，langchain集成
   - JavaScript：用于TypeScript/Node.js代理
</best_practices>

<running_evaluations>
## 运行评估

**上传的评估器**在运行实验时自动运行——无需代码。**本地评估器**直接传递用于开发/测试。

<python>
```python
from langsmith import evaluate

# 上传的评估器自动运行
results = evaluate(run_agent, data="My Dataset", experiment_prefix="eval-v1")

# 或者传递本地评估器进行测试
results = evaluate(run_agent, data="My Dataset", evaluators=[my_evaluator], experiment_prefix="eval-v1")
```
</python>

<typescript>
```javascript
import { evaluate } from "langsmith/evaluation";

// 上传的评估器自动运行
const results = await evaluate(runAgent, {
  data: "My Dataset",
  experimentPrefix: "eval-v1",
});

// 或者传递本地评估器进行测试
const results = await evaluate(runAgent, {
  data: "My Dataset",
  evaluators: [myEvaluator],
  experimentPrefix: "eval-v1",
});
```
</typescript>
</running_evaluations>

<troubleshooting>
## 常见问题

**输出与你预期的不符：** 查询LangSmith跟踪。它显示了每一步的精确输入/输出——将你找到的内容与你试图提取的内容进行比较。

**每个评估器一个指标：** 返回`{"score": value, "comment": "..."}`。对于多个指标，创建单独的函数。

**字段名不匹配：** 你的运行函数输出必须与数据集模式完全匹配。首先使用`client.read_example(example_id)`检查数据集。

**RunTree与dict（仅Python）：** 本地`evaluate()`传递`RunTree`，上传的评估器接收`dict`。处理两者：
```python
run_outputs = run.outputs if hasattr(run, "outputs") else run.get("outputs", {}) or {}
```
TypeScript始终使用属性访问：`run.outputs?.field`
</troubleshooting>

<resources>
- [LangSmith评估概念](https://docs.langchain.com/langsmith/evaluation-concepts)
- [自定义代码评估器](https://changelog.langchain.com/announcements/custom-code-evaluators-in-langsmith)
- [OpenEvals - 即用型评估器](https://github.com/langchain-ai/openevals)
</resources>
