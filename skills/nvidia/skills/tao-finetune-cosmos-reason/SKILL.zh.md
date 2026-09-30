---
name: tao-finetune-cosmos-reason
description: 共享 Cosmos3 前端，明确路由 Cosmos 框架和 Cosmos-RL，验证运行时模型/视频数据集/SLURM 输入，消费 SQSH 或打包的后端镜像，可选地规划显式清理源构建，准备检查点，在进程内验证首次更新，并返回 token 加权损失和任务感知准确率。
---

# Cosmos3 TAO 训练

保持一个共享的面向模型的前端。后端镜像字段和合约路径位于 `backend_contracts` 下的 `references/skill_info.yaml` 中；镜像字面量来自 `versions.yaml`，而引用的后端 YAML 定义了原生运行时模式。不要在它们之间进行翻译。

## 强制性运行时输入

在规划训练之前，收集所有以下内容。不要从历史记录、其他用户、先前的作业、镜像或开发者检出中推断路径。

- `base_model_path_or_uri`。对于 Hugging Face 模型 ID 或 URL，接受可选的友好 `base_model_revision`，例如分支或标签。如果省略，则解析 `main`；不要要求用户输入提交 SHA。通过 Hub API 以只读方式解析选定的引用，将其转换为不可变提交，并在计划中密封模型 ID、请求引用和解析的 SHA。完整的本地快照不需要修订，并由其文件指纹密封。
- 对于 Cosmos3-Nano，一个显式的输入检查点 `model_type`：`qwen3_vl` 或 `cosmos3_omni`。如果用户没有提供它，请在规划之前询问一次；从不从 `config.json`、模型 ID、路径名或先前运行中推断选择。用 plain language 解释两个选择：`qwen3_vl` 直接使用兼容的 Hugging Face 检查点，而 `cosmos3_omni` 需要在训练之前将不可变转换到精确的 Qwen3-VL safetensors。将答案记录为 `base_model_format`。Cosmos3-Edge 从解析的模型 ID 推断为 `cosmos3_edge`，并且不显示此仅限 Nano 的选择。
- 在正常输入期间不要暴露 Omni 准备实现字段。对于 Nano，使用打包的 `Qwen/Qwen3-VL-8B-Instruct` 架构映射，自动解析两个 Hub 模型到不可变提交，并运行 TAO 拥有的 `cosmos_rl.model_preparation.vlm_safetensors` 入口点，使用已选择的后端镜像/SQSH。两个后端镜像必须打包该入口点及其固定的原生 Framework 转换运行时。显式提供的 `prepared_checkpoint_path` 或捐赠者是一个高级覆盖：验证它，但从不提供 A/B 路径选择或默认要求一个。
- 直接接受 `hf_model://nvidia/Cosmos3-Nano`。如果一个受限制的/私有的模型无法解析，只要求用户在会话环境变量中设置 `HF_TOKEN`；从不要求他们发现 SHA 或在聊天中提供令牌值。
- 显式的视频采样模式：要么均匀 `nframes` 要么 `fps`。FPS 模式也可以设置 `min_frames` 和 `max_frames`；两种模式都可以设置由所选后端支持的剪辑时间、调整大小和像素预算字段。
- 训练/验证注解路径和媒体根，用于对话式或任务感知视频监督，以及可选的任务选择。
- 用于比较的显式 `backend`；`cosmos-framework` 或 `cosmos-rl`。
- `training_mode`；`dense` 或 `peft`。PEFT 还需要 rank、alpha、dropout、目标模块、偏差、RS-LoRA、要保存的模块和适配器精度。
- 用户拥有的 `results_dir`、`checkpoint_dir`、`cache_dir`，以及对于 SLURM 的 `sqsh_cache_dir`、`ssh_key_path`、挂载和调度器设置。
- 运行时顺序：计算可读的 `sqsh_path`、显式镜像，然后 `references/skill_info.yaml` 中的所选后端镜像。在 SLURM 中重用或将其一次转换为 `sqsh_cache_dir`。从不将 SQSH 文件名与镜像标签进行比较或请求源起源/SHA。
- 仓库路径、提交/树、分支、基础镜像、构建上下文和时间戳是仅用于显式 `source-build` 的高级输入。参见 `references/cosmos-backend-operations.md`；从不从运行时选择中推断构建。

规划器保留每个原始路径并报告可访问的 `realpath`。缺少必需路径会失败。缺少提供的 SQSH 会失败；省略 SQSH 会选择打包的镜像。不允许任何历史回退路径或镜像。

### Nano 检查点模型类型选择

将选定的 `base_model_format` 视为用户决策，并验证它是否与提供的本地检查点的 `config.json.model_type` 匹配。不匹配会失败；它不是重新标记或重写源检查点的权限。

对于 `qwen3_vl`，指纹并直接使用完整的兼容 Hugging Face Nano 检查点。对于 `cosmos3_omni`，告诉用户在启动审查中 Cosmos-RL 将自动准备其兼容的检查点，命名计划的输出路径，并保留源检查点不变。不要要求用户提供架构捐赠者、准备镜像或准备 SQSH。后端拥有的准备步骤在选定的平台的用户拥有的 `checkpoint_dir` 下发出经过验证的 `qwen3_vl` 检查点：

- Docker：本地 Docker 主机的 `checkpoint_dir`。
- SLURM：计算节点验证的共享 `checkpoint_dir`，由显式容器挂载覆盖。通过 SLURM/Pyxis 合约运行转换；不要将转换后的检查点写入控制器本地存储。

使用打包的 Nano 架构映射和所选后端运行时，除非提供了高级覆盖。指纹源、架构映射、转换的 config/tokenizer/processor/index/shards 和转换起源。在转换之前，将密封计划的后端原生训练字段和 `VLM_SAFETENSORS_PATH` 绑定到所选容器内的计划转换检查点。在训练之前验证确切的输出，而不更改密封计划。原始 Omni/Hugging Face 路径仅保留为起源，并且永远不能作为运行时模型路径。只有在确切的靶标具有完整的匹配转换起源并通过相同的验证时才允许重用。

### 公共 Cosmos3-Edge 检查点合约

接受公共模型在其解析的不可变修订版或本地快照；从不请求第二个检查点。
应用模型感知运行时默认值来自 `references/skill_info.yaml` 和 `references/cosmos-framework-backend.yaml`，保留单独的模型和处理器指纹以及每个默认/覆盖起源。

## 后端选择

首先运行 `scripts/cosmos_workflow.py resolve`。

| 请求 | 自动选择 |
|---|---|
| Cosmos3-Nano 普通训练 | Cosmos-RL（兼容性默认值） |
| Cosmos3-Nano AutoML/HPO | Cosmos-RL |
| Nano Framework-DCP 导出 | Cosmos Framework |
| Nano 评估/推理/微服务，没有显式后端 | Cosmos-RL |
| Nano 量化 | Cosmos-RL |
| Cosmos3-Edge 训练/导出/评估/推理/微服务 | Cosmos Framework |

显式支持的后端获胜，因此用户可以选择 Cosmos Framework 进行 Nano 训练，而无需更改模型所有权。比较运行拒绝 `auto`，因此实验的双方都被故意强制。
框架训练的检查点使用原生精确键导出器，然后使用仓库支持的 TAO 评估适配器。这并没有使 Framework 成为 Cosmos-RL 版本。

## 评估输入和继承

为每个评估操作运行 `scripts/evaluation_workflow.py` 并完全遵循 `references/cosmos-reason-evaluate.md`。父训练计划拥有所有可继承的模型、数据集、提示、预处理、精度、检查点和评分字段；从不要求用户重复它们。只询问一次 helper 的 `required_user_inputs`，执行其 `automated_actions`，并只启动校验和有效的 `ready=true` 计划。Cosmos-RL 政策检查点需要发出的 `cosmos_rl_checkpoint_pre_action`；Framework DCP 输入需要它们发出的导出预操作。准备好的计划包括验证的 `spec_bundle.execution`；将其不变地传递给选定的平台。Cosmos 拥有运行时验证和评估器配置；平台拥有启动。

## Framework 检查点预操作

在 Framework 评估、推理或微服务操作之前，运行 `scripts/framework_checkpoint_action.py plan` 及其发出的 `prepare` 和 `verify` 步骤。遵循 `references/cosmos-backend-operations.md`；从不要求用户手动导出 DCP。在 SLURM 中仅阶段 helper 依赖集由 `workflow_contract.action_helper_dependencies` 声明；平台验证封闭包。只使用验证的 `action_model_path`，重用仅匹配的完整导出，并记录预操作、清单、指纹和独立子结果。

## 必需的门

按顺序执行这些阶段并持久化它们的输出。

1. 解析模型/后端/操作并加载选定的后端合约。
2. 仅通过存在性检查凭据。从不读取或持久化凭据值。仅要求需要它的操作令牌。
3. 按强制性输入顺序验证工具、存储、路径和运行时选择；现有-SQSH 和打包镜像模式跳过源门。
4. 仅对于显式 `source-build`，验证/构建干净的源并验证 `/opt/tao/image-provenance.json`。从不将主机源挂载到训练。
5. 强制显式的 Nano 检查点模型类型选择。如果它是 `cosmos3_omni`，在启动审查中显示转换和平台拥有的输出路径，然后在批准后，通过选定的干净后端镜像中的共享 TAO 集成入口点准备模型。自动解析 URI/模型-ID 引用到不可变的 Hub 提交。验证确切的张量/config 键并指纹模型、tokenizer、处理器、权重索引、每个 shard 和起源。将验证的转换路径（而不是原始源路径）分配给训练。
6. 验证输入、计数、重复项、重叠、任务和身份。无字节哈希请求选择两个快速指纹标志；元数据保持哈希，而权重/媒体有效载荷使用路径+大小。
   从分配的计算节点重新验证解析的输入。当 SLURM 存储未挂载到启动主机时，让 `cosmos_workflow.py` 通过 SSH 将其检查的 `cosmos_common.py` 检查器流到登录主机。它从 stdin 运行，保留远程 `realpath` 值，并且不会创建远程脚本或源覆盖。不要要求基于 SSH 的启动主机上的本地 Lustre、`sbatch` 或 `srun`。使用 `plan` 语句一次运行昂贵的输入检查，并通过本地 `--plan-artifact <path>` 传递，以便解析的请求和检查结果被密封以供剩余的启动语句使用。
7. 从结构化数据集合约解析视频运行时，并执行 `references/cosmos-reproducibility-gates.md` 中的每个配置文件门。Cosmos-RL `auto` 选择源烘焙的 `pynv-device-rgbp` 用于 `video_conversation` 和 `system-pyav` 用于 `task_aware_video_reasoning`；Framework 选择 `torchcodec-cuda-on-demand`。所有默认值使用有界 rank-local、按需内存，没有磁盘预预热。重复媒体验证可能使用后端原生的分组 sharder 和仅验证缓存，同时保留记录、显式批处理、加权、提示和预处理。放宽批处理-1 对称性的吞吐量设置需要用户授权。
8. 生成后端原生 TOML、环境、拓扑、预检命令、对称数据、运行时配置文件和元数据。完整规范不包含样本限制。跨只读 `preflight`、后评审 `materialize` 和 `render-slurm` 重用一个密封的 `--plan-artifact`；不要重复原始输入。在验证的计算帧中原子化材料化，仅从显式挂载派生容器路径，并且永远不要将源补丁复制到集群。诊断子集是显式的 opt-ins，永远不会是启动先决条件。
9. 在 SLURM 中重用提供的/派生的 SQSH 或在 GPU 提交之前选择镜像一次。SQSH SHA 和源起源不是运行时门。当 Omni 准备需要时，检查 SQSH 文件系统，除非它包含共享的 TAO 启动器、原生 Framework 转换器以及 `/opt/tao/framework-converter-runtime.json`。运行时工件必须报告 `validation_mode=imported_converter_module`，证明隔离转换器的传递依赖图在镜像构建期间导入；文件存在本身是不够的。
   验证 Pyxis/Enroot、挂载、Python/包、解码器、GPU、CUDA、NCCL 和存储在训练分配中。
10. 直接启动请求的训练作业；除非用户明确要求，否则不要提交单独的冒烟作业。对于 Cosmos-RL VLM 训练，需要打包的源，它发出一个填充感知的 `attention_mask`，并在第一次反向传递后和第一次优化更新前运行视觉梯度合约。持久化视觉编码器、视觉投影器、语言模型和语言头的总数/可训练/冻结计数和梯度范数。当可训练的视觉组件没有梯度、非有限范数或零范数时，立即失败。将显式冻结的视觉组件报告为不适用，而不是失败。
11. 一次材料化完整规范并在计算帧中验证其 SHA256，然后再从相同的计划工件渲染作业。监控调度器和结构化 TAO 状态到一个终端结果，并独立于调度器状态保留子进程退出代码。要求子进程退出为零、结构化 `SUCCESS`、有限的全球训练/验证损失、检查点完成，以及最终评估器指标，然后报告完成。
12. 使用 `scripts/evaluation_workflow.py` 解析评估。继承确切的微调工件，只收集其剩余的用户输入，运行后端拥有的自动检查点预操作，并要求 `ready=true`。在 Cosmos-RL 中，使用 `cosmos_rl_checkpoint_action.py` 验证选定的 HF 导出，使用其清单重新运行解析，并通过选定的平台提交发出的 spec-bundle；永不选择原生策略目录，将生命周期复制到应用拥有的启动器，或编造结果/状态变量。
   使用相同的提示、预处理、生成、归一化和任务评分评估选定的检查点。使用 `scripts/extract_cosmos_metrics.py` 提取最终指标。

## 数据集合约

通过结构解析数据集，而不是通过项目、基准、目录或文件名。支持的家庭是：

- `video_conversation`：一个包含媒体和至少两个 ShareGPT、LLaVA 或 OpenAI 风格对话转的 JSON 数组；
- `task_aware_video_reasoning`：一个或多个具有媒体、任务身份和对话/响应目标的项信封或数组注解文件。

默认 `dataset_family` 为 `auto`，检查每个注解，并要求训练和验证解析到相同的家庭。捕获记录计数、唯一媒体计数、媒体重用、扩展、字节大小分布、任务/指标元数据，以及任何声明的宽度、高度、FPS 和持续时间。根据这些特征和模型层选择处理器、缓存和资源配置文件。永不基于客户数据集名称分支。

声明准确性的任务参与确定性准确性；常见的二元和多项选择任务类型被识别。生成任务报告其声明的指标，并从汇总准确性中排除，并说明原因。
汇总准确性是对记录按示例加权，并具有准确性定义。

## Dense 和 PEFT 合约

Dense SFT 没有 LoRA 块，并报告可训练、冻结和总数。PEFT 在后端之间保留 rank、alpha、dropout、目标、偏差、RS-LoRA、保存的模块、精度和可训练计数；不匹配的语义会阻止一对。

为了公平比较，强制相同的逻辑模型、训练/验证记录、媒体、提示、帧、序列长度、精度、种子、周期、有效全局批处理、优化器、学习率、计划、预热、权重衰减、剪裁、损失掩码、验证/检查点节奏、评估的检查点，以及生成/归一化设置。将差异分类为等效语法、不可避免的实施差异或无效不匹配；无效不匹配会阻止整个对。

## 指标和完成情况

所需的主要指标包括：

- 全局范围内减少的 token 加权训练损失，分子为损失值，分母为有效标签；
- 最终验证全局范围内减少的 token 加权损失，分子为损失值，分母为有效标签；
- 仓库评估器的最终验证指标及其发出的任何支持值。不要添加第二个评估后门。

不要平均控制台行或排名均值。步骤损失不是平均训练损失。验证心跳不是最终验证损失。生成精确匹配不是准确率，除非任务定义了它。

原生框架回调和原生 Cosmos-RL 日志记录器拥有早期失败、检查点、进度、指标和终端事件。不要在容器启动时设置状态桥或修补状态。来自 SLURM 的 `COMPLETED` 在子进程退出代码非零或终端 TAO 状态不是成功时为失败。

## SLURM 不变性

生成的作业使用 Bash、SQSH 通过 Pyxis、默认不重新排队、每个节点一个启动器任务、运行时提供的日志和训练子进程退出代码。单节点独占分配在 `SBATCH` 合同中保留请求的 CPU 数量，但将 SLURM 实际授予的每个 CPU 传递给训练步骤并记录请求、分配和步骤计数。在训练子进程之前，相同的分配运行规划器拥有的打包运行时门，作为训练作业的第一个 Pyxis 步骤；失败的门会写入独立的子进程退出工件并阻止训练。生成的作业设置 `SLURM_EXPORT_ENV=ALL`，平台消费者仍然使用 `sbatch --export=ALL` 提交。每个 Pyxis 步骤也通过 `--container-env` 接收规划器拥有的运行时变量名称，因此烘焙镜像的 `ENV` 值不能覆盖选择的解码器、帧传输、缓存或工作配置文件。框架拓扑是 shard=`gpus_per_node`，replica=`nodes`。Cosmos-RL 在节点零上使用一个控制器及其策略-工作拓扑。异步分布式检查点对于多节点运行被拒绝。

每个作业元数据记录必须验证 `schemas/cosmos-job-metadata.schema.json` 并包含路径、指纹、运行时身份、配置、资源、状态、输出和时间，但不包含凭证。源可追溯性仅存在于 `source-build`；SQSH SHA 是可选的，并且永远不会是运行时门。

## 影响源的恢复

如果一个运行暴露了代码或镜像缺陷，停止受影响的路径，更改所属仓库，添加一个测试，提交它，从干净的检出重新构建镜像和 SQSH，然后从其干净的密封计划重新启动每个受影响的训练作业。永远不要编辑正在运行的容器，修补现有镜像，在源更改后重用旧的 SQSH，或依赖临时启动脚本作为实现。

使用 `references/cosmos-reproducibility-gates.md` 作为源所有者/测试映射。

对于基础设施重试，启动技能分类失败并打开新的 `--retry-of` 记录；SLURM 提供验证的节点清单和排除项。使用新记录的 `<action-root>/config/train.toml` 运行 `cosmos_workflow.py retry-plan`；它会重新基础所有可写路径并重新密封 Cosmos 请求。渲染该计划；永远不要修补 SBATCH。
