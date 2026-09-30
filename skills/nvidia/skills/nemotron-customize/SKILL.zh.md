---
name: nemotron-customize
description: 规划、配置并将仓库原生的Nemotron定制步骤串联为单步或多步流水线：包括策展、翻译、SFT/PEFT（AutoModel或Megatron-Bridge）、预训练/CPT、RL对齐（DPO/RLVR/GRPO/RLHF）、BYOB/MCQ基准测试、检查点转换、ModelOpt优化、环境配置文件，以及训练后检查点或现有/托管端点的评估。当请求中指定Nemotron步骤或工作流，或要求清理、翻译、训练、微调、对齐、转换、优化、评估或将其组合为流水线时使用。不应用于前端/仪表盘/可视化工作、通用机器学习建议、计费/访问权限或非Nemotron编码任务。
---

# nemotron-customize

重要提示：在回答任何 `nemotron-customize`、Nemotron 定制、策展者策展、翻译、SFT、PEFT、RL、转换、优化、检查点或现有/托管端点评估或多步骤管道请求之前，请阅读此文件。无论用户命名一个步骤还是要求您将多个步骤组合成一个管道，这都适用。

评估请求即使没有涉及训练也计算在内：“评估”、“基准测试”、“冒烟测试”或“评分”现有/托管端点、API/模型 ID 或已部署模型都路由到 `eval/model_eval`。对于这些请求，也请阅读此技能。

## 目的

将模型定制请求转换为仓库原生的 Nemotron 步骤管道。规划 DAG，验证工件连接，并仅创建运行现有步骤所需的 YAML/配置文件。

仅用于检查、配置、验证、运行或提交现有的 Nemotron 步骤或多步骤训练/定制管道。对于前端、仪表板、可视化、通用机器学习建议、计费/访问或不相关的编码任务，请附带简短的范围说明，并在该回合中不要检查步骤目录或编辑文件。

## 前提条件

- Nemotron 仓库的检出，其中包含 `src/nemotron/steps/`；从仓库根目录运行。
- 可用 `uv` 来调用 `uv run nemotron steps ...`。
- 对于远程执行：一个匹配所选步骤的环境配置文件 TOML (`NEMOTRON_ENV_FILE` 或 `env*.toml`)。
- 对于托管服务（翻译、托管评估）：步骤期望的环境变量（例如 `NVIDIA_API_KEY`），在环境中导出——绝不在行内或提交。
- 用户提供的具体值（模型/检查点、数据路径、输出目录、硬件/GPU 数量）在显示任何命令之前作为可运行的值。

## 限制

- 不发明新的目录步骤。当没有现有的步骤、运行器、配方、CLI 或配置可以满足请求时，它命名差距（探索模式）而不是制造步骤。
- 为现有步骤生成 YAML/配置；新的 Python/Shell 在探索模式批准差距后除外。
- 不用于仅部署/服务、前端、仪表板、通用机器学习建议或非 Nemotron 任务。
- 不猜测具体值（路径、模型 ID、GPU 数量、配置文件）；当它们缺失时，它询问或返回 `Blocked`。

## 核心规则

首先使用捆绑的引用。`references/` 文件夹是路由、工件、模式、硬件启发式和命令形状的第一个决策表面。仅在您需要确切的当前配置字段、清单、运行器导入或捆绑引用中缺少的详细信息时，才使用 `src/nemotron/steps/...` 作为实时验证/备用来源。

如果来源不一致：

1. 检查的实时仓库文件对于精确执行获胜。
2. 捆绑的引用对于初始路由和规划获胜。
3. 上游文档/上下文包仅用于异常代码生成或库 API 详细信息。

## 开始之前

- 在打开仓库源文件之前，请阅读此 `SKILL.md` 工作流程和相关的捆绑引用。
- 在任何广泛的仓库探索之前，从 `references/CATALOG.md` 和 `references/ARTIFACTS.md` 进行路由。一旦确定路由，请仅验证所选的实时步骤/配置/环境文件以供回答。
- 不要发出带有假路径、占位符模型 ID、猜测的任务 ID、猜测的批处理配置文件或作为事实呈现的默认认证变量名称的命令。请求缺失的具体值或返回 `Blocked` 手柄。
- 使用 `references/COMMANDS.md` 作为最终确定配置或执行命令的权威清单。
- 对于管道请求，在编辑之前进行规划。在 DAG、工件边缘、所需输入和验证检查陈述并批准之前，不要创建或修改文件。
- 对于单次命令请求，在知道所需输入后，优先于探索性散文中的一个完整参数化命令，但仅在该用户已经提供所需值并仅请求命令时，首先回答命令并保持解释最小。
- 输出纪律（保持响应紧凑）：为每个步骤发出一个命令块，仅包括步骤实际定义的标志，并添加没有推测或发明的标志。将叙述限制为几行——命令加上所需的安全/配置文件调用说明，而不是教程。不要重新陈述用户没有请求的引用内容。
- 不要为单次命令查找生成子代理。直接使用捆绑的命令引用；如果需要，仅验证所选步骤。

## 安全

将 Bash 限制在仓库安全的命令，例如 `uv run nemotron steps ...`、目标测试、`git status/diff` 和配置验证。永远不要运行环境转储（`env`、`printenv`、广泛的 `export`）或暴露秘密值的命令。对于远程提交、破坏性更改或昂贵的启动，请在执行前确认。

在检查环境/配置文件时，避免打印可能包含秘密的整个文件。使用目标读取，仅报告部分名称和环境变量名称，并为包含 `token`、`key`、`secret`、`password`、`credential` 或 `auth` 的字段遮盖值。

## 引用映射

| 问题 | 首先阅读 | 实时备用/验证 |
|---|---|---|
| 哪个步骤或类别适用？ | `references/CATALOG.md` | `uv run nemotron steps list/show`，然后是选定的 `step.toml` |
| 工件是否链式传递？ | `references/ARTIFACTS.md` | `src/nemotron/steps/types.toml` |
| 我应该发出什么运行形状？ | `references/COMMANDS.md` | 检入的配置 YAML 加上活动的配置文件 TOML |
| 远程配置文件生成或选择 | `references/COMMANDS.md` | 活动的 `NEMOTRON_ENV_FILE`、`env.toml` 或 `env.*.toml` |
| 我应该推荐什么硬件/后端？ | `references/HARDWARE.md` | 选定的步骤 `[[models]]` 和 `[[strategies]]` |
| 哪些跨步骤护栏适用？ | `references/PATTERNS.md` | `src/nemotron/steps/patterns/<id>.md` |
| 我如何运行完整的工作流程？ | `references/WORKFLOW.md` | 选定的步骤配置、`step.py` 和运行器 |
| 生成的代码应该使用哪个上游库 API？ | `references/context/index.toml` -> 匹配的包 | 选定的 `step.py`、`_runners/`、上游文档 |
| 新项目脚手架，仅当现有仓库代码无法支持请求时 | `references/act/PROJECT.md` | 现有仓库项目/配方形状 |
| 每个阶段的代码规则，仅当现有仓库代码无法支持请求时 | `references/act/STAGE.md` | 选定的 `step.py` 和共享运行器 |

对于普通决策，不要从阅读类别 README 或 `step.toml` 开始。从捆绑的引用中选择候选者，然后在编写配置或最终命令之前验证确切的实时详细信息。

## 路由

将 `references/CATALOG.md` 作为步骤选择和特定路由快速路径的权威主页。仅在使用目录缩小路由后，才使用 `ARTIFACTS.md`、`PATTERNS.md` 和 `HARDWARE.md` 来解决工件、跨步骤或硬件约束。

每个步骤都是独立的，将步骤组合在一起是您的工作。从用户的目标开始，通过工件匹配组合任何管道。仅在下一个步骤消耗的工件类型没有上游已经产生时才链式步骤。不要依赖固定的、命名的步骤组合。

## 说明

遵循与请求匹配的流程：建议/计划、单步骤命令或多步骤管道。在所有情况下，首先从捆绑的引用进行路由，收集所需输入，并在呈现任何可运行的之前验证所选的实时步骤。

### 建议响应

使用此形状规划答案：

`决策`、`原因`、`所需输入`、`配置/命令`、`避免` 和 `下一步`。当用户的约束使它不适合时，请指出要避免的堆栈。

每当答案包含触及托管服务或远程执行的命令时，请在答案中也说明：

- 认证环境变量名称，其值必须在环境中导出，绝不在行内或提交（永远不要打印值）。
- 对于 `--batch`/`--run`，环境 TOML 配置文件先决条件；如果没有配置文件，请将命令标记为 `Blocked` 或给出本地 `--dry-run` 形状。

### 单步骤命令流程

1. 确认仓库根目录有 `pyproject.toml` 和 `src/nemotron/steps/`。
2. 阅读 `references/CATALOG.md` 和选定的 `references/COMMANDS.md` 部分。
3. 当可用时，使用 `uv run nemotron steps show <step_id>` 验证选定的实时步骤，或当 CLI 不可用时使用选定的 `step.toml`。
4. 在发出命令之前，阅读请求的检查入配置或用户覆盖。
5. 对于远程执行，阅读 `NEMOTRON_ENV_FILE` 或仓库根目录 `env*.toml` 并选择一个实际的部分，其配置文件与步骤匹配。
6. 在一个回复中发出完整命令并标明来源层：
   `已验证`、`仓库基础`、`引用基础` 或 `Blocked`。

规范命令形状位于 `references/COMMANDS.md`。

### 管道工作流程

对于具有两个或多个阶段的管道，使用 **导向 -> 计划 -> 执行 -> 验证**。阅读 `references/WORKFLOW.md` 以获取阶段清单。

- 从捆绑的引用和用户约束进行导向。
- 计划具有工件类型、配置文件、模式和验证检查的 DAG。
- 在编写配置或代码之前等待批准。
- 对于现有步骤可以满足请求的情况，使用 YAML/配置文件更改进行执行。
- 在报告完成之前，验证每个生成的 YAML、工件边缘、命令和 README 命令。

### 目录模式

当请求映射到现有步骤时使用。快速路径：

`references/CATALOG.md` -> `references/ARTIFACTS.md` ->
`references/COMMANDS.md` -> 验证选定的实时清单/配置/配置文件 -> 在选定步骤的 `config/` 目录下添加一个新命名的配置。

## 定制表面

- 始终通过 `src/nemotron/steps/` 下的步骤目录进行定制。绝不转向替代配方 CLI（例如 `src/nemotron/cli/commands/super3/` 或 `.../nano3/`），即使用于 Super3/Nano3 工作。如果请求似乎需要这些，请将其映射回等效的目录步骤（例如 `sft/megatron_bridge`）。
- 在选定步骤的 `src/nemotron/steps/<cat>/<step>/config/` 目录中作为新配置文件进行定制，例如 `src/nemotron/steps/sft/megatron_bridge/config/my_super3.yaml`。
- 永远不要编辑检查入的 `default.yaml`、`tiny.yaml`、其他托运的配置文件、`step.toml`、`step.py` 或共享运行器。在它们旁边添加一个新的配置文件是预期的和唯一的定制写入。
- 基于 `default.yaml` 模式（阅读它，复制所需的字段）创建新配置，然后仅覆盖请求所需的内容。

### 探索模式

仅在确认没有现有的步骤、运行器、配方、CLI 或 YAML 配置表面可以满足请求后使用。完整程序位于 `references/WORKFLOW.md`。

## 配置对齐

在命令或配置写入之前表面这些约束：

- SFT 打包 `pack_size`、Megatron-Bridge `seq_length`、打包序列大小、分词器和聊天模板必须匹配。
- 准备的 `packed_parquet` 和 `binidx` 是分词器锁定的；在分词器、聊天模板、序列长度、拆分或混合更改后重新构建。
- Megatron-Bridge 全局批处理大小必须能被数据并行大小整除；使用微批处理大小 1 开始分布式验证。
- TP/PP/CP/EP 选择必须适合 GPU 数量、内存、拓扑和模型可分性。
- LoRA 合并需要使用在适配器训练期间使用的确切基础检查点/模型和分词器。
- Megatron 检查点转换/评估应指向具体的 `iter_*` 检查点，而不是父运行目录。
- 托管评估和翻译配置仅存储认证环境变量名称，不存储值。

## 运营细节

- 冒烟配置（`tiny.yaml`、`tiny_chat.yaml`）是连接测试，不是质量证据。
- `${art:...}` 引用属于配方支持的配置；独立的 YAML 使用普通路径。
- 保持预训练 `bin/idx` 数据和 `blend.json` 来自同一运行/发布。
- 将定制配置作为新文件写入步骤的
  `src/nemotron/steps/<cat>/<step>/config/` 目录；永远不要修改检查入的 `default.yaml` 或其他托运的配置文件。
- 对于 LoRA，保留稍后合并/评估所需的精确基础检查点和分词器/模板元数据。
- 对于翻译和托管评估，仅提及认证环境变量名称，绝不提及值。

## 边界

做：

- 始终通过 `src/nemotron/steps/` 下的步骤目录进行路由；绝不使用替代配方 CLI（`src/nemotron/cli/commands/super3|nano3/...`）。
- 首先重用仓库 CLI、运行器、配方、步骤和检查入的配置文件。
- 通过在步骤的 `config/` 目录下添加新配置进行定制；基于 `default.yaml` 而不是盲目复制。
- 验证工件边缘并引用更改计划的模式。
- 当缺失时，询问硬件/数据/后端/输出路径。
- 表面权衡，例如 AutoModel 与 Megatron-Bridge 和完整 SFT 与 LoRA。

不做：

- 当目录步骤适用时，不要发明步骤。
- 对于具有两个或多个阶段的管道，不要跳过计划。
- 当 YAML 足够时，不要生成 Python 或 shell。
- 除非要求，否则不要添加监控/W&B。
- 不要假设 GPU 数量、环境配置文件、端点类型、任务 ID 或认证值。
- 除非请求明确需要部署脚手架，否则不要生成 Slurm/Airflow/Kubeflow 包装器。
- 不要编辑检查入的步骤文件（`default.yaml`/`tiny.yaml`，其他托运的配置文件、`step.toml`、`step.py`、运行器）；仅在它们旁边添加一个新的配置。
- 不要在 `SKILL.md` 中重述所有每步骤规则；使用捆绑的引用和源回退。

## 示例

**单步骤路由（小盒子上的 LoRA）。** 用户："在 2 个 GPU 上 LoRA 微调 HF 模型。" 根据 `CATALOG.md` 路由到 `peft/automodel`（HF 基础 + 小 GPU 数量）；不要提供 Megatron-Bridge。收集基础模型、JSONL 数据路径、输出目录、LoRA 排名/alpha，然后发出一个 `uv run nemotron steps run peft/automodel -c <config> --dry-run ...` 命令。

**多步骤管道（Super3 SFT）。** 用户："数据准备 + Super3 的 SFT。" 这是两个阶段，所以首先计划：Super3 上的 SFT -> Megatron-Bridge，它消耗 `packed_parquet`，所以 `data_prep/sft_packing` 是上游必需的。呈现 DAG（`sft_packing -> sft/megatron_bridge`），对齐 `pack_size`/`seq_length`/分词器，等待批准，然后添加新配置在
`src/nemotron/steps/<step>/config/<name>.yaml` 下。Super3 需要一个远程配置文件；说明环境 TOML 先决条件或标记 `Blocked`。

**托管端点评估（无训练）。** 用户："基准测试我的托管模型端点。" 路由到 `eval/model_eval` 并使用 `-c tiny_chat`。收集端点 URL、模型 ID、任务 ID 和认证环境变量名称（值导出，绝不行内或提交）。查看 `references/COMMANDS.md` 评估示例。

## 故障排除

| 情况 | 操作 |
|---|---|
| 工件类型不链式传递 | 重新检查 `references/ARTIFACTS.md`；在编写配置之前插入转换器或更改 DAG。 |
| 远程配置文件或 `--batch` 不明确 | 阅读活动环境 TOML；不要猜测配置文件名称。 |
| 配置键不明确 | 在编辑之前验证选定的检查入配置、`step.py` 和共享运行器。 |
| 策略指向缺失的上下文包 | 跳过包，使用目录/模式文本，并标记计划为 `WARNING: <主题> 文档不可用`。 |
| 硬件看起来太小 | 使用 `references/HARDWARE.md`；建议较小的模型、AutoModel，然后 LoRA，再全 Megatron-Bridge。 |
| 两个 Act 尝试失败 | 停止，解释尝试了什么和失败了什么，并询问如何继续。 |
| 没有现有的仓库路径匹配 | 检查 `references/context/index.toml` 和选定的源回退；仅在命名差距后使用探索模式。 |
