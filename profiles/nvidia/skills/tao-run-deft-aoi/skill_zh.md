# 技能：tao-run-deft-aoi

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

## 执行契约

将其视为磁盘后端状态机，而不是散文式食谱。

1. 保留所有显式的用户值。`epoch 1` 表示 `num_epochs=1`，`iteration 1` 表示 `max_iterations=1`；启发式算法或规格默认值仅在使用户未提供该参数时适用。在预检摘要中显示每个运行参数的来源（`user`、`spec` 或 `default`）。保留客户的指标名称、运算符、目标、单位、评估器和约束。批准的 `metric_contract` 是评估、检查点选择、完成和报告的权威来源。
2. 用户批准摘要后，设置 `PYTHON=$(bash scripts/deft_python.sh)`，然后使用 `"$PYTHON" scripts/init_deft_state.py` 一次性初始化 `deft_state.json`，传递预检的精确 GPU 型号/内存、解析的 `--network-mode`、激活源和选择的绝对 Python。生成的 `execution_policy` 是不可变运行状态。恢复时切勿手动编写或重新初始化它。
3. 启动后，在上下文压缩后、每个阶段之前以及任何完成声明之前，运行 `"$PYTHON" scripts/deft_context.py --state ... --stage ...`。使用其持久的 `next_stage` 以及状态文件的 `status`、`current_iteration`、`iterations.*.status`、`stage_completed` 和最新的 `events` 条目来恢复。不要从助手文本或未在状态中记录的工件中推断进度。
4. 读取 DEFT 覆盖层后，调用映射的底层技能。不要用猜测的 shell 命令、内联 Python、不同的输出树或从 KPI 集合中虚构的数据来替换缺失/未读取的阶段引用或失败的技能调用。
5. 初始化后，通过 `"$PYTHON" scripts/deft_exec.py --state ... -- <command>` 运行安装/获取/登录/容器命令。空气隔离模式拒绝出站和安装，注入离线标志，并强制执行无拉取。选定的平台必须强制执行等效策略。
6. 使用 `"$PYTHON" scripts/commit_stage.py` 提交每个阶段；它验证阶段所需的输入，并原子性地更新恢复快照和 `deft_state.json` 内有序的 `events` 数组。切勿使用内联 Python、jq、heredocs 或编辑器编辑状态文件。修复被拒绝的证据；切勿虚构状态。对于评估，将指标结果、检查点、推理 CSV 和阈值直接传递给 `commit_stage.py`。从后端经过时间或主机计时器传递执行的阶段的积极测量 `--duration-sec`。记录的 `--skip` 可能记录 `0`；负持续时间始终被拒绝。
7. 仅在 `"$PYTHON" scripts/finalize_run.py` 创建了交接工件、成功提交 `loop_stop` 并且新鲜读取的 `deft_state.json` 显示 `status == "complete"`、`iterations.baseline.status == "complete"` 以及最终迭代的 `status == "complete"` 后，才声明循环完成。检查点、推理 CSV、报告或助手消息本身不是完成证据。

## 上下文规范

- 适时加载引用。重新读取状态，然后仅读取当前阶段的命名部分并执行。
  切勿预加载/列出每个引用或底层技能，递归列出技能树，或重新读取当前上下文中已存在的引用。
- 将 verbose 训练、推理、Docker 和 SDG 输重定向到文件。最多检查最后 40 行或一行状态/工件检查；切勿将完整的规格、状态文件、循环日志或生成的脚本打印到对话中。
- Skill-tool 调用加载阶段指令；它不会启动后台协调器。立即在父级中继续记录的阶段。切勿睡眠或轮询等待 Skill-tool 进程。对于实际的后台 Docker 工作，保存 PID 并以不超过 30 秒的间隔轮询。
- 在预检开始时，在依赖项之前解析网络模式。读取恰好一个分支：`references/air-gap.md` 用于空气隔离模式或 `references/network-bootstrap.md` 用于网络启用模式。切勿在空气隔离运行中加载网络引导。

## 何时使用此技能

当用户希望代理运行 NVIDIA TAO VisualChangeNet / ChangeNet PCB 检查模型的完整 DEFT AOI 改进循环时，请使用此技能：基线评估、RCA、合成缺陷生成、数据挖掘、重新训练和部署门控，直到 KPI 目标达成。

- "运行 DEFT 循环"
- "微调直到配置的质量指标达到其目标"
- "在保留其约束的同时优化客户定义的指标"
- "使用 RCA 和合成缺陷改进我的 AOI ChangeNet 模型"
- "迭代训练直到部署 KPI 达到目标"

不要使用此技能进行单个独立的 TAO 训练运行、一次性推理、通用异常生成或 RCA 仅分析。当用户仅请求该步骤时，直接使用相关的代理。

## 基础模型

循环使用 **NVIDIA TAO Visual ChangeNet** 分类，可以是端到端的 C-RADIOv2-B 或冻结的 DINOv3 主干。`specs/baseline_spec.yaml` 定义了架构。主干变体、阶段、`HF_TOKEN` 和挂载规则由 `references/visual-changenet.md` 拥有；规格始终指向本地挂载文件。`NGC_KEY` 控制容器拉取。SigLIP 矿工由 `references/tao-mine-aoi-images.md` 拥有；AnomalyGen 资产和网络/空气隔离规则由 `references/tao-generate-anomalies.md` 和 `references/air-gap.md` 拥有。容器拥有其基础资产列表；此工作流通过传递 `--model_sizes 2B` 显式地将引导保留在 Text2Image 2B。

## 训练 AutoML 策略

DEFT AOI 拥有迭代数据改进循环、重新训练节奏和 KPI 检查点选择。仅为此工作流，即使底层 Visual ChangeNet 模型元数据有 `automl_enabled: true`，也绕过模型级 AutoML。

`automl_policy: off` 是 Visual ChangeNet 技能调用的**工作流参数**（父级在调用 `tao-skill-bank:tao-train-visual-changenet` 通过 Skill tool 传递的值），**不是** TAO 规格字段。两种情况：

- **直接 `docker run visual_changenet train -e <spec>`**（此工作流实际使用的路径）：无需操作。TAO 入口点是默认的普通训练；AutoML 位于 SDK 协调的不同代码路径上。实际上，每个直接 `docker run` 已经是 `automl_policy: off`。
- **SDK 协调分发**（Brev/SLURM/k8s，SDK 构建命令）：将 `automl_policy: off` 传递给 `VisualChangeNetSDK.train(...)` 或等效运行器参数。SDK 使用它来选择普通训练命令，而不是 AutoML 包装器。

**切勿向 spec YAML 添加 `automl_policy` 或 `workflow` 键。** TAO 的 Hydra `ExperimentConfig` 模式不识别这些键，并且在配置合并时间以 `Error merging '<spec>.yaml' with schema: Key 'workflow' not in 'ExperimentConfig'` 失败。这是一个工作流级覆盖；不要更改模型元数据，并且不要将此策略应用于其他工作流。

## 启动摄入

用户确认他们想要运行此工作流后，询问他们打算在哪个支持的平台运行。从安装的平台技能（tao-run-on-docker / -slurm / -kubernetes / -brev，以及任何外部技能）发现执行平台；在仅显示核心路由技能的运行时，读取 `skills/platform/tao-run-on-*/SKILL.md` 前置文本。

平台选择后，读取所选平台技能的 `## 凭证` 部分和 `references/skill_info.yaml`（required_credentials / credential_groups）。

切勿请求或打印凭证值。检查变量是否已设置（`[ -n "$VAR" ] && echo SET || echo UNSET`）；如果未设置，命名它以便用户可以导出它或将其放在用户批准的 env 文件（`~/.tao/secrets.env`、`~/.config/tao/.env` 或他们指向的文件），使用 `set -a; source /path/to/.env; set +a` 加载。运行永远不会创建或写入该文件。

## 代理行为

> **只有一个用户门：预检确认。** 打印预检摘要（见 `references/preflight.md` → 预检摘要），然后停止并等待用户键入 "go"、"yes"、"看起来不错" 或类似明确批准。在获得批准之前，不要启动任何有副作用的步骤（`docker run`、训练、SDG、`${RESULTS_DIR}/` 下的突变）——读取规格、列出文件、`docker image inspect` 和填充摘要表是允许的。**"自主" 描述了此门之后的行为，而不是之前。** 即使用户的原始提示听起来很紧急（"直接运行它"、"继续吧"），也不要跳过此门——摘要本身是用户在批准前需要看到的工件。
>
> **门之后，技能是完全自主的。** 无需确认即可运行整个循环。不要在步骤之间暂停。不要问 "要我继续吗？" —— 直接继续。只有在步骤出现不可恢复的错误或触发硬停止门时才停止。在每个步骤里程碑打印一行状态更新，以便用户可以跟踪进度。
>
> **需要自动模式。** 门之后，循环触发持续的副作用调用（`docker run`、`${RESULTS_DIR}/` 写入）；如果没有自动接受/绕过权限模式，它会在第一个提示时停滞。在预检摘要中提醒用户在批准前启用自动模式（shift+tab）。
>
> **阻止恢复。** 在用户门之前，通过 `deft_python.sh` 选择一个完整的已安装主机解释器。如果不存在，仅遵循已选择的网络模式引用。空气隔离模式在没有包管理器命令的情况下硬停止；网络启用引导隔离在 `references/network-bootstrap.md` 中。
> 应用 `references/air-gap.md` 中的网络模式分支；记录允许的获取和目录创建作为批准后的工作，或在空气隔离模式下验证阶段资产。批准后，自行修复可恢复的阻止器，然后恢复您所在的预检步骤（`<blocker> 清除 → 继续步骤 N`）。仅停止您无法修复的情况（缺少工作区/规格/CSVs/凭证、空池、泄漏）。修复不是另一个用户门。
>
> **非零命令规则。** 切勿重复未更改的失败命令，也不要通过尝试和错误切换到未文档化的 CLI/模块路径。读取最终错误块（不仅是容器横幅），将其映射到加载的阶段引用/底层技能，进行基于证据的更正，并重新运行其记录的验证。如果引用不涵盖失败，则通过 `commit_stage.py` 提交 `status=error` 并停止，而不是即兴创作缩减的工作流。
>
> **修订计划。** 如果在原始摘要显示后任何运行参数发生变化（用户施加时间限制、覆盖 epoch、更改 max_iterations 等），始终重新运行预检并显示更新的摘要后再继续。

## 工作流

按此顺序执行循环（完整细节在 `references/pipeline-and-state.md` → 管道 + 阶段执行）：

1. **预检。** 运行 `references/preflight.md` 中的所有检查。解析工作区、规格、CSVs、检查点、容器镜像。仅在您无法自行解决的缺失输入上硬停止（见 `## 代理行为` → 阻止恢复）。
2. **基线。** 如果 `deft_state.json` 已经有 `iterations.baseline.stage_completed == "train"` 并且一个 `best_ckpt_path` 指向一个现有文件（上游 `automl-deft-pipeline` 从其第一阶段 AutoML 胜利者预种这些检查点——见其第一阶段 → 第二阶段交接），**跳过训练子步骤** 并在 `inference -> evaluate` 对预种检查点恢复。否则，通过调用 `tao-skill-bank:tao-train-visual-changenet` 运行 `train -> inference -> evaluate`。使用 `references/metric-contract.md` 中的批准合同和评估器进行评估。无论如何，然后通过调用 `tao-skill-bank:tao-analyze-gaps-visual-changenet` 进行 `rca`。首先阅读 `references/visual-changenet.md`、`references/metric-contract.md` 和 `references/tao-analyze-gaps-visual-changenet.md` 以获取 DEFT-loop 特定参数。
3. **迭代。** 对于每个迭代，直到 `max_iterations`，执行管道步骤 1-7。在步骤之间重新读取 `deft_state.json` 并从其 `stage_completed` 值继续；不要打印完整状态。
4. **停止** 当 KPI 目标达成或 `max_iterations` 达到时，通过运行 `"$PYTHON" scripts/finalize_run.py` 并提供匹配的原因。硬停止失败作为错误并永远不会重新标记为成功的 `loop_stop`。
5. **自动渲染。** `scripts/init_deft_state.py` 写入初始 `results/DEFT_Loop_Report.html`；每个成功的 `commit_stage.py` 调用都会使用 `scripts/render_report.py` 中实现的确定性报告钩子刷新它。因此，`loop_stop` 提交即使父级上下文饱和也会产生最终报告。如果钩子报告错误，直接运行 `"$PYTHON" scripts/render_report.py --results-dir "${RESULTS_DIR}"`
   修复命名的演示输入；切勿手动编写报告 HTML。

所有管道阶段都在父级上下文中内联运行。优先通过 Skill tool 直接调用底层的 `tao-skill-bank:*` 技能，并在匹配的 `references/*.md` 文件上分层 DEFT-loop 规范。如果映射的 Skill tool 不可用，但 Docker、技能源树和阶段引用模块存在，则使用 `references/scripts-and-agents.md` 中记录的文档直接容器回退；在第一个回退阶段之前，将 `execution_path=direct-container` 写入转录本，并且对于每个回退阶段，记录映射的底层技能名称以及使用的精确直接命令。保留相同的 `deft_state.json`、工件和脚本支持的报告合同。HTML 渲染不会被委托。

### 使用捆绑脚本

对于每个工具调用，设置 `PYTHON=$(bash <skill_root>/scripts/deft_python.sh)`；然后使用 `"$PYTHON" <skill_root>/scripts/<name>.py`。首先将每个路径参数解析为绝对主机路径。在每阶段之前使用 `deft_context.py`，使用 `deft_exec.py` 进行外部执行，并使用 `commit_stage.py` 进行所有状态写入。有关脚本调用、自动报告钩子、阶段映射、直接容器回退和路径不变量的信息，请参阅 `references/scripts-and-agents.md`。

## 阶段引用模块

每个管道阶段映射到银行中的一个底层技能；匹配的 `references/*.md` 文件将 DEFT-loop 规范（挂载、输出目录和 `commit_stage.py` 参数）叠加在技能的通用指令上。**仅读取当前阶段的 relevant 部分，然后通过 Skill tool 或文档化的直接容器回退调用技能；切勿预加载所有阶段引用。** 如果引用文件丢失，停止并要求用户重新安装插件。完整的阶段→引用→技能→所有权表位于 `references/scripts-and-agents.md` → **阶段引用模块**。阶段：`train`/`evaluate`（`references/visual-changenet.md`）、`anomalygen`（`references/tao-generate-anomalies.md`）、`rca`（`references/tao-analyze-gaps-visual-changenet.md`）、`routing`（`references/tao-route-visual-changenet-samples.md`）和 `data_mining`（`references/tao-mine-aoi-images.md`）。

**路径规则（不变）。** 在 `${RESULTS_DIR}` 下记录绝对主机工件路径。对于 ChangeNet 直接容器，挂载 `"$WORKSPACE:/data/workspace"` 和 `"$RESULTS_DIR:/results"`；规格使用 `/results/baseline/<stage>` 或 `/results/iterN/<stage>`。其他阶段保留其引用模块所需的 workspace 挂载。切勿将运行目录重新映射到 `/results/iterN`。

## 数据、预检、管道和状态引用

| 主题 | 引用 | 内容 |
|---|---|---|
| 空气隔离激活和离线执行 | `references/air-gap.md` | 全局模式触发器、优先级、禁止的网络操作、阶段资产要求以及预检证据 |
| 带自己的数据、数据合同、输出布局、增强池 | `references/data-layout.md` | 没有公开的 AOI 数据集；完整的 `<workspace>` 输入树、ChangeNet 四列必需 CSV 范式、`${RESULTS_DIR}/` 输出树以及两个来源的挖掘池表 |
| 客户指标合同和评估器适配器 | `references/metric-contract.md` | 主要指标模式、比较方向、评估器 JSON、约束、evaluate 提交以及兼容性行为 |
| 预检检查、默认值、预检摘要模板、运行时估计 | `references/preflight.md` | 10 个有序的预检检查、必需的 `max_iterations`、所有默认值、完整的预检摘要表 + 填充命令以及每个迭代的运行时估计 |
| 管道步骤、状态、阶段执行、报告、运行时行为 | `references/pipeline-and-state.md` | 基线预种/跳过训练逻辑、7 个迭代管道步骤、`deft_state.json` 快照 + 事件模式、后阶段检查、每个迭代 HTML 渲染以及循环结束序列 |
| 捆绑脚本、报告钩子、阶段模块、AutoML 陷阱 | `references/scripts-and-agents.md` | 可用脚本表、确定性报告渲染器和后提交钩子、阶段引用模块表、路径规则不变量、AutoML 规格陷阱 |

**必需输入 — `max_iterations`。** 没有默认值；如果未提供，请询问用户，并且在没有它的情况下不要进入预检。如果用户给出时间限制，请使用 `references/preflight.md` 中的每个迭代运行时数据将其转换为估计的 `max_iterations`，并显示估计以供确认。所有其他运行参数都有默认值——切勿询问具有默认值的参数。完整的默认值列表和用户在单个门批准的预检摘要在 `references/preflight.md` 中。

## 门控

运行完整的预检（`references/preflight.md`），打印预检摘要，然后停止在单个用户门。批准后，运行基线（带有预种/跳过训练逻辑）和 7 步迭代管道，均在 `references/pipeline-and-state.md` 中详细说明。

硬停止，并且永远不会自动重试：任何阶段 `status=error`；训练/验证泄漏；一个缺失或零行的挖掘池；一个失败的 CSV 存在性检查；静默丢弃；AMP 分配不匹配；一个与 PAIDF 不兼容的 AnomalyGen 微调检查点；一个缺失的 AnomalyGen Guardrail 检查点；或 SDG 日志显示禁用筛选。循环在 KPI 目标达成、`max_iterations` 达到或不可恢复的门触发时停止。每个终端路径通过 `commit_stage.py` 提交 `loop_stop`，然后遵循 `references/pipeline-and-state.md` 中的循环结束序列。
