# 评估器插件

插件 CLI 入口点是 `uv run nemo evaluator`。

## 目的

使用此技能选择评估接口和指标，验证最小示例，提交 NeMo 平台评估作业，并获取其结果。

## 输入

在构建评估之前建立这些输入：

- 评估接口：[数据集驱动与任务驱动代理评估的区别](references/evaluation-shapes.md#difference-summary)
- 执行接口：独立 SDK 评估或持久的 NeMo 平台作业。
- 通过/失败数据集示例：最小的代表性通过和失败案例。
- 指标：要评分的行为以及它们消耗的模板字段。
- 目标：离线评分无目标，或产生输出的模型、代理、运行器或预计算试验。

## 说明

1. 明确输入是 [数据集驱动行](references/evaluation-shapes.md#dataset-driven-evaluation) 还是 [任务驱动代理工作](references/evaluation-shapes.md#task-driven-evaluation)。
2. 选择最简单的衡量请求行为的指标。尽可能选择确定性指标。
3. 构建一个包含一个预期通过和一个预期失败的微型冒烟案例。
4. 使用独立 SDK 验证指标行为，并检查行级输出和聚合结果。
5. 在扩展之前修复字段映射、提示、解析器或任务定义。
6. 仅在输入和评分形状工作后提交平台作业。

在为评分标准、RAG 工作流或工具调用评估选择指标之前，请阅读 [指标选择](references/metric-selection.md)。

## 选择执行接口

| 需求 | 接口 |
| --- | --- |
| 无 NeMo 平台快速指标迭代 | `nemo_evaluator_sdk.Evaluator` |
| 数据集驱动平台作业 | `client.evaluator.submit(...)` 或 `nemo evaluator evaluate submit` |
| 一个作业中包含多个内联/存储指标引用 | 带有 `EvaluateInputSpec` 的 `nemo evaluator evaluate submit` |
| 任务驱动平台作业 | `nemo evaluator agent-evaluate submit` |
| 可重用的平台定义和结果索引 | `client.evaluator.metrics`, `.tasks`, `.tasksets`, `.eval_results`, `.agent_eval_results` |

对于每个插件评估，默认使用 `submit`。插件的本地执行路径 — `client.evaluator.run()` 和 `nemo evaluator ... run` CLI 词汇 — 正在被弃用，因此即使 `--help` 仍然列出它，也不要基于它构建。对于无平台快速指标迭代，使用独立的 `nemo_evaluator_sdk.Evaluator`。

- 阅读 [SDK 执行](references/execution.md) 了解数据集、目标、配置、字段映射、作业生命周期和自定义指标打包。
- 阅读 [存储资源](references/resources.md) 了解持久定义和结果查询。

## 限制

- `api_key_secret` 是独立的环境变量名，但在 `submit` 上是 NeMo 平台密钥名。参见 [API 认证](references/api-auth.md)。
- 提交时返回 HTTP 409 通常表示引用的平台密钥缺失，而不是重复作业。请阅读响应正文。
- `intent` 是评分器元数据，永远不会显示给代理；只有 `inputs` 才能到达它。
- 指标模板使用 `item.*` 用于数据集行，但在代理评估中使用 `reference.*`, `sample.*` 和 `inputs.*`。
- 指标进度可能在平台作业终止之前达到 100%。在检索结果或下载工件之前，始终调用 `job.wait_until_done()`。

## CLI 接口

### 前置条件

此文件中的所有命令都假设 shell 的工作目录是 NVIDIA-NeMo/nemo-platform 仓库的根目录。

在 NeMo 平台仓库检出中，通过工作区运行命令：

```bash
# 确认插件就绪并列出注册的评估器作业。
uv run nemo evaluator info
# 列出可用指标名称；添加指标名称以打印其架构。
uv run nemo evaluator metric-types
# 下两个命令打印数据集驱动和任务驱动作业的输入和输出架构 — 可能非常大，谨慎使用以避免填满上下文窗口。
uv run nemo evaluator evaluate explain
uv run nemo evaluator agent-evaluate explain
```

当技能和插件安装后，使用安装的 `nemo` 命令，不要假设仓库根目录或手动激活 `.venv`。

相对于此技能目录解析捆绑资产。在此仓库中规范路径是 `skills/nemo-evaluator-plugin`；安装的技能可能位于不同的技能根目录下。

## 捆绑资产

| 路径 | 用途 |
| --- | --- |
| `assets/specs/exact_match_metric.json` | 两个行的离线冒烟规范；直接提交 |
| `assets/specs/llm_as_judge.json` | 在线生成 + 评分；本地优先 (`NVIDIA_API_KEY`) |
| `assets/specs/fabric_agent_eval.json` | 任务驱动 Fabric 运行器规范 |
| `assets/examples/plugin_sdk_examples.py` | 每个插件表面的可复制 SDK 片段 |

## 可用脚本

| 脚本 | 目的 | 参数 |
| --- | --- | --- |
| `scripts/generate_example_specs.py` | 生成或漂移检查捆绑规范 | `--check`, `--write` |

在此仓库中，NeMo 使用显示的工作区命令：

```bash
uv run --frozen python skills/nemo-evaluator-plugin/scripts/generate_example_specs.py --check
```

不要假设特定的 `run_script()` 辅助函数；使用显示的 `uv run` 命令。

## 示例

### 数据集驱动评估示例

- 按照 [验证独立，然后提交到平台](references/execution.md#validate-standalone-then-submit-to-the-platform) 进行两行通过/失败冒烟测试及其 CLI 提交。
- 按照 [映射非规范字段](references/execution.md#map-noncanonical-fields) 当数据集列需要 `field_mapping` 时。
- 按照 [获取作业结果](references/execution.md#getting-job-results) 进行提交、终端等待、结果检索和工件下载。
- 按照 [存储指标、任务和任务集](references/resources.md#store-a-metric-task-and-taskset) 进行可重用定义，以及 [查询持久结果](references/resources.md#query-persisted-results) 进行结果查找。

### 任务驱动代理评估示例

**独立 SDK 评估**

使用 `AgentEvaluator().run(...)` 进行独立任务驱动 SDK 评估。其 `target` 可以是 `Model`、`GenericAgent` 或直接的 `AgentTaskRunner`。

**平台作业评估**

使用插件的 `agent-evaluate submit` 作业进行平台任务评估。其目标是 `ModelTarget`、`AgentTarget`、`CodexRunnerTarget`、`FabricRunnerTarget` 或 `HarborRunnerTarget`；或者提供预计算的 `trials`。提供 `target` 或 `trials` 中的确切一个。

提交接受内联任务或存储的 `TasksetRef`。存储的任务集在目标工作区中解析。

阅读 [代理评估](references/agent-evaluation.md) 了解内联任务、`TasksetRef`、并发、快速失败行为、结果工件和运行器配置。

### 在仓库检出中准备 Fabric

Fabric 运行器示例和测试需要可选的 harness 适配器和匹配的 Relay 网关：

```bash
uv sync --frozen --package nemo-evaluator-sdk --extra fabric --inexact
script/dev-install-fabric.sh
```

安装脚本下载与锁定 Python 绑定匹配的校验和验证的 `nemo-relay` 二进制文件。将其报告的目录添加到 `PATH`，然后使用 `uv run --frozen --no-sync ...` 进行 Fabric 检查，以便 uv 不会删除可选适配器。

## 输出格式

以以下形式报告完成的平台评估：

```text
作业: <作业名>
状态: <终端状态>
指标: <指标名>
均值: <聚合均值>
工件: <下载的结果或工件位置>
错误: <错误消息>
```

## 阅读专业参考

- 在使用模型、代理、远程指标或持久提交之前，请阅读 [评估器 API 认证](references/api-auth.md)。
- 在编写评分器分数、提示或解析器之前，请阅读 [LLM 评分器](references/llm-judge.md)。

## 故障排除

当架构、认证、作业、结果或运行器行为失败时，请阅读 [评估器故障排除](references/troubleshooting.md)。

## 遵循安全最佳实践

永远不要打印、序列化或提交密钥值。在规范和示例中仅存储环境变量名或平台密钥引用。
