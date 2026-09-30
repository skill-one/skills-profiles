---
name: tao-run-automl
description: 使用 AutoMLRunner 运行基于容器的 NVIDIA TAO 网络的 AutoML / 超参数优化 (HPO)。支持算法选择（贝叶斯、Hyperband、ASHA、BOHB、LLM、混合、AutoResearch）、WandB 实验跟踪、在任何 TAO SDK 平台上执行作业、结果解释以及每条记录的定制评估钩子。当用户提到 TAO AutoML、超参数优化、HPO、automl、automl_settings、AutoMLRunner、tao_automl、贝叶斯搜索、Hyperband、ASHA、LLM 指导搜索、AutoResearch，或希望对 TAO 网络进行训练/评估/推理/蒸馏/剪枝/量化时使用。模型操作使用解析的镜像；venv 训练需要明确请求。平台无关性——可在任何 SDK（Brev、SLURM、Kubernetes、Docker）上运行。不要单独使用通用的“持续改进”语言来覆盖匹配的特定领域 DEFT 工作流；标记为 CLIP / SigLIP 的图像检索循环属于 tao-run-deft-pas，除非明确指定了 HPO。
---

# TAO AutoML

> **独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup`（主机预检、凭证、跨技能发现）。

通过组合以下内容来对 TAO 模型运行自动超参数优化：

1. 在 `skills/models/<model_skill>/` 下选择的模型技能。
2. 在 `skills/platform/<platform>/` 下选择的平台技能。
3. `AutoMLRunner`，它生成建议、启动选定的动作作业、提取指标并将结果反馈给优化器。

在模型元数据、平台预检、数据可见性、凭证、图像选择和计算形状都得到验证之前，不要启动。

## 执行运行时 — 硬件门

默认情况下，每个建议、基线评估、每个建议评估和最终评估都在选定的模型动作的解析 `container_image` 中运行。在设置任何训练环境之前，从模型技能中解析它。本地检查点或 Hugging Face 模型 ID 不会改变此规则。

仅在明确请求时才使用基于 venv 的 **模型执行**。不要从 `local-docker`、本地 GPU、Python 或 `pyproject.toml` 推断 venv 模式。如果不存在，执行是容器后端的。`tao_automl`、TAO SDK 或平台适配器的主机/控制器 venv 仅用于控制平面；将子模型动作保留在解析的容器镜像中。

## 参考映射

- `references/skill_info.yaml`：此工作流的结构化元数据。
- 分割详细参考：`automl-preflight-concepts.md` 用于先决条件和支持检查；`automl-intent-algorithms.md` 用于搜索策略；`automl-compression-literature.md` 用于蒸馏/剪枝/量化算法的充分性和未来压缩搜索路线图；`automl-runner-configuration.md` 用于 runner/API/WandB 详细信息；`automl-advanced-monitoring.md` 用于钩子、恢复和陷阱；以及 `automl-examples.md` 用于对话示例；以及 `automl-common-pitfalls.md` 用于常见安全检查。`detailed-guide.md` 仅是地图。
- `skills/models/<network>/SKILL.md`：特定于模型的 dataset 要求、指标、HPO 注意事项、检查点交接和已知错误。
- `skills/models/<network>/references/skill_info.yaml`：动作合同、容器镜像、输入、输出、上传排除和 `mode`。
- `skills/platform/<platform>/SKILL.md`：选定的平台预检、凭证、资源形状、监控和取消。
- `skills/core/tao-launch-workflow/SKILL.md`：平台、凭证、dataset 可见性、图像确认和用户确认的共享摄入模式。

## 预检

1. 运行共享启动摄入。如果用户没有选择平台，请询问；Brev、SLURM、Kubernetes 和 Docker 是平等的同伴。
2. 在生成 runner 文件之前，运行选定平台技能的预检。
3. 验证 `nvidia-tao-automl` 导入：

```bash
python -c "import tao_automl; from tao_automl.runner import AutoMLRunner; print('OK')"
```

然后验证选定平台的 SDK 结构 — 导入 `tao_automl` 并不证明平台后端已安装（例如，没有 `docker` 包，`DockerSDK()` 会引发 `CredentialError`）。参见 `automl-preflight-concepts.md`。

如果缺失，请显示 `versions.yaml` 中的确切安装命令，并在安装前询问：

```bash
SB="${TAO_SKILL_BANK_PATH:-~/tao-skill-bank}"
pip install "$($SB/scripts/resolve_versions_key.py wheels.tao_automl_<platform>)"
```

有效的平台轮键是 `tao_automl_brev`、`tao_automl_slurm`、`tao_automl_kubernetes`、`tao_automl_docker` 和 `tao_automl_all`。仅用于需要所有后端的开发机器使用 `all`。仅在用户请求 LLM 指导的算法时添加 `,llm`。

## 模型支持门

在每次运行之前：

1. 读取模型的 `SKILL.md` 和 `references/skill_info.yaml`。
2. 确认模型 `automl_enabled: true` 或模型技能明确将选定的动作路由到 AutoML。
3. 确认 `<skill_dir>/schemas/<action>.schema.json` 存在并可解析。这是 AutoML 搜索空间门。
4. 对于非 TAO-Core 模型（如 Cosmos-RL 和 CLIP），还需要 `references/spec_template_<action>.yaml`；否则，runner 没有完整的动作默认值。
5. 如果任何门失败，不要自行设计搜索空间。报告缺失的包工件。

## 输入

在构建 runner 之前收集这些内容：

| 输入 | 要求 |
|---|---|
| `model_skill` | 解析后的模型技能目录，位于 `skills/models/` 下。首先解析用户别名（如 `network_arch`）到打包的技能目录。 |
| `network_arch` | 从解析的模型技能元数据中读取。 |
| `action` | 要优化的动作 — `train`、`evaluate`、`inference`、`distill`、`prune` 或 `quantize`，带有打包的 schema/template。 |
| `platform` | 支持的 TAO 平台技能之一。 |
| `train_dataset` / `eval_dataset` / 动作输入 | 使用模型特定的 spec 键和布局。非训练动作可能还需要父/教师检查点、校准数据或剪枝工件。 |
| `results_root` | 适合平台的本地、Lustre 或 S3 路径。 |
| `gpu_count`、`num_nodes` | 尊重模型和平台的限制。 |
| `container_image` | 通过模型元数据和 `versions.yaml` 解析；向用户显示它。 |
| `automl_algorithm` | 默认为 `bayesian`，除非用户请求其他算法或模型技能推荐一个。 |
| `metric`、`direction` | 优先使用模型技能的验证/任务指标。 |
| `automl_budget` | 算法所需的建议数量、最大 epoch/rungs、并发或种群大小。 |

不要请求秘密值。使用 `[ -n "$VAR_NAME" ] && echo SET || echo UNSET` 验证所需的 env 变量。

## 启动前审查门

在启动任何建议作业之前，显示具体的启动审查并获取用户确认。此门适用于每个 AutoML 运行和每个 AutoML 支持的模型/网络；它不是 Cosmos 特定的，并且不得仅限于单个模型技能。即使平台和图像预检已经通过，这也适用。审查必须包括：

- 模型/网络、平台、图像、GPU/节点形状和结果/工作区根
- 数据集模式和具体的 spec 键，包括当可以廉价读取时训练/评估样本计数
- 算法、预算、最大并发作业、指标和方向
- 可搜索参数和范围，包括用户未提供明确搜索空间时的默认值
- 初始启动批次的确切生成的建议配置，在提交任何建议作业之前，在仅用于审查的步骤中生成
- 每个建议的估计运行时和总预期墙时间，以及使用的假设
- 自动基线评估作业 ID、指标值和结果路径，来自预检后的评估作业，或者如果模型没有可运行的评估动作或验证数据，则提供一个明确的阻止器
- 选定的最佳检查点/模型的 Post-AutoML 最终评估计划，包括指标、数据集和记录路径

如果估计时间超过用户的声明限制或比正常交互运行明显更长，请在启动前询问是否要减少建议、epoch、数据集大小、验证频率或搜索空间。不要在日志中隐藏多天的估计。

## 自动基线评估作业

在平台、图像、凭证、数据和模型预检通过后，在提交任何 AutoML 建议作业之前，在选定的验证/评估数据上运行一次模型的评估动作。这是必需的 AutoML 设置，不是用户可选的“预训练评估”问题。使用与 AutoML 训练运行开始时相同的基线模型或检查点、模型技能的评估 spec/template 和选定平台的正常作业提交路径。如果模型技能建议评估比训练更小的形状，请使用该形状并在启动审查中指明。

在请求确认之前，在启动审查中共享评估指标数字。如果存在起始检查点，但基线无法生成 — 没有打包的评估动作、缺少评估数据、评估作业失败 — 则停止并报告阻止器，而不是在静默中回退到仅训练损失的运行。

对于从头开始训练，将基线记录为不可用并继续；不要评估空检查点。

Runner 拥有最终评估。当评估可运行时，将 `final_eval_fn(best_rec, train_job_id)` 传递给 `AutoMLRunner.run`；结果将包含 `result["final_evaluation"]`。参见 `automl-preflight-concepts.md` 了解回调、检查点、基线和从头开始规则。

## 依赖和数据预检

如果选定的工作流需要对象存储或平台 CLI，而工具缺失，请报告缺失的依赖项并提供建立确切的安装命令，然后再继续。在用户批准后，使用 `scripts/check_tao_launch_preflight.py` 并带 `--install-missing-tools` 重新运行，以便它安装最小的所需包并立即重试路径验证。对于 S3 路径，在创建 runner 工件之前，从启动平台验证凭证和路径可读性。

对于在每次训练试验期间读取大型媒体存档或目录的模型，将数据集一次阶段或提取到执行平台可见的存储中，然后将所有建议 spec 指向该阶段路径。记录源 URI、阶段路径、字节/文件计数证据（如果可用）和时间戳在 `<workspace>/evaluations/data_staging.json` 中。如果无法阶段，请在启动审查中包括重复的 S3 I/O 风险，并在花费很长时间在 AutoML 预算上之前询问。

当模型技能定义样本计数敏感的约束时，在启动前执行它们。拒绝或限制每个会创建零训练步骤的批量大小建议，对于选定的数据集和 GPU 分片计数。使用 `scripts/check_tao_launch_preflight.py --effective-batch-limit train_annotation=<batch_size>,<shard_count>` 为每个生成的建议在提交之前执行。如果建议后来因为数据太小而无法有效批量大小而失败，将其分类为无效配置，仅在剩余预算存在时替换或调整它，并在最终摘要中报告更正。
当训练样本计数从注释文件或廉价清单读取时，将其作为 `automl_settings["train_sample_count"]` 传递给 `AutoMLRunner.run`，以便 runner 可以在提交作业之前限制不可能的建议，并在 `result["history"][i]["adjustments"]` 中记录调整。

## 算法策略

| 算法 | 良好匹配 | 所需旋钮 |
|---|---|---|
| `bayesian` | 小/中等预算和少量参数的默认值。 | `num_recommendations`、指标、方向 |
| `hyperband`、`asha` | 许多配置、廉价的早期运行；ASHA 对并行友好。 | `max_epochs`、`reduction_factor`、可选 `max_concurrent` |
| `bohb`、`dehb` | 混合贝叶斯/进化搜索，具有多保真度预算。 | 与 Hyperband 相同的 rung 预算字段 |
| `pbt` | 长训练，其中应在训练期间变异计划。 | 种群和代预算 |
| `llm`、`hybrid`、`autoresearch` | 用户明确希望 LLM 指导的搜索，并配置了端点。 | LLM 端点配置加上预算 |

对于 `evaluate` 或 `inference`，默认为 Bayesian/BFBO 风格的搜索，覆盖选定的动作的提示、解码、预处理或运行时配置旋钮。使用动作输出/日志中的任务指标，并在指标名称模糊时显式设置 `direction`。不要使用不更新权重的动作的训练损失假设。

对于 `distill`，当蒸馏动作执行基于 epoch 的优化并写入检查点时，使用与训练类似的策略。对于单次 `prune` 和 `quantize`，默认为 `bayesian` 或 `bfbo`，除非动作 schema/模型技能声明了 epoch 类似或校准预算字段，使 `hyperband`/`asha`/`bohb`/`dehb` 有意义。使用 `eval_fn`，当选定的指标必须在压缩动作完成后由后续的评估/推理动作计算时。

优先使用模型技能的建议而不是通用默认值。当模型技能说启动、验证或检查点成本在短试验中占主导地位时，避免使用 ASHA 或 Hyperband。

## Spec 和搜索空间

构建嵌套字典的 spec。如果模型技能以点表示法列出路径以提高可读性，请遍历路径并将嵌套叶分配给它；不要将扁平点字符串存储为 spec 键。

使用打包的选定动作 schema：

- `automl_default_parameters`
- `automl_disabled_parameters`
- 有效 min/max 范围
- 枚举、选项权重、条件、依赖和常用参数

用户提供的搜索空间必须保持在 schema 约束内。对于具有离散选择的整数旋钮，如果模型技能提到了所需的整数选项形状，请包括 schema 的要求，而不是松散的列表。

数据源覆盖是强制性的，除非模型技能说启动器可以导出它们。当数据集使用直接注释/媒体路径时，保留确切的用户提供的 spec 键。

## 指标策略

训练损失廉价但可能具有误导性。优先使用模型技能的任务指标。使用以下之一：

- 日志指标：`metric=<name>`，`direction=maximize|minimize`。
- `metric_extractor(logs, metric_name)`：当默认解析器模糊时，解析模型的日志。
- `eval_fn(rec, train_job_id)`：当用户希望下游任务指标时，在每次建议后运行模型的评估动作。

除非模型技能明确定义了该映射，否则不要将 `kpi` 映射到指标。

最终报告必须比较基线指标、每个建议的指标和选定的最佳指标，以便用户可以看到调整的影响。对于需要 `eval_fn` 来计算真实任务指标的模型技能，使用该评估器而不是优化方便的训练损失，除非用户明确接受代理指标。

## Runner 构建

在预检通过后，仅使用选定的平台 SDK。不要在代码中嵌入凭证来构建 SDK。

`sdk` 是平台 SDK 对象；无容器 venv 模型使用 `VirtualEnvSDK(venv_path=..., work_dir=...)`。始终传递 `work_dir` — 默认的 `~/.tao_sdk/virtualenv` 会用试验检查点填满主目录。参见 `automl-runner-configuration.md`。

```python
import sys
from pathlib import Path
from tao_automl.runner import AutoMLRunner

skill_bank = Path("<absolute-tao-skill-bank>")
model_skill = "<resolved-model-skill-directory>"
skill_dir = skill_bank / "skills" / "models" / model_skill
sys.path.insert(
    0, str(skill_bank / "skills/applications/tao-run-automl/scripts")
)
from resolve_automl_session import validate_session_settings

runner = AutoMLRunner(
    sdk=sdk,
    skill_dir=str(skill_dir),
    action=action,                      # train, distill, prune, quantize, ...
)

workspace_path = Path("<automl_workspace>")
resume = False
# 来自此技能捆绑的脚本目录的强制关闭门。
validate_session_settings(
    automl_settings,
    resume=resume,
    workspace=workspace_path if resume else None,
)
result = runner.run(
    workspace_path=str(workspace_path),    # 时间戳它以避免冲突
    automl_settings=automl_settings,       # 必须包含一个显式的 session_id
    spec_overrides=spec_overrides,
    automl_hyperparameters=automl_hyperparameters,
    custom_param_ranges=custom_param_ranges,
    metric_extractor=metric_extractor,  # 可选
    eval_fn=eval_fn,                    # 可选
    final_eval_fn=final_eval_fn,        # 可选但必需当最终评估可运行时
    resume=resume,
)
```

显式设置 `automl_settings["session_id"]` 并在每次运行前调用 `validate_session_settings`。使用 `scripts/resolve_automl_session.py new` 一次性生成一个新 ID。仅在明确请求时才恢复；使用 `scripts/resolve_automl_session.py resolve --workspace <full-run-path>` 解析其控制器。缺失或模糊的状态是一个阻碍。有关完整的生成/恢复模式，请参阅 `references/automl-advanced-monitoring.md` 中的恢复部分。

## 监控

使用 `runner` 状态输出和平台 SDK 的 `get_job_status`、`get_job_logs` 和 `get_failure_analysis`。对于活动任务，报告：

- 推荐ID / 试验ID
- 平台任务ID
- 状态
- 当前指标
- 迄今为止的最佳指标
- 当前/最佳推荐所选的超参数
- 当存在足够时间数据时，报告已用时间和更新后的预计完成时间

失败时，将其分类为基础设施、数据可见性、图像、凭证、规范/模式或模型代码失败。仅修复最小原因，不要在重复无效推荐上静默地花费额外预算。如果在运行设置期间修复了阻碍，请显示更新的预检/启动审查后继续原始任务，而不是让用户重新陈述请求。

对于基于 LLM 的算法，在调用运行有效之前检查大脑日志。验证 LLM 调用是否成功、是否生成了建议、是否使用先前的指标来选择后续参数更改，以及日志是否显示保留/丢弃或等效算法决策。如果大脑回退到随机采样，将 LLM 工作流程分类为失败或受阻，而不是将其视为有效的 LLM 指导运行。

## 结果交接

完成时：

1. 通过所选指标和方向确定最佳推荐。
2. 返回最佳子任务 ID 及其结果路径。
3. 使用模型技能的检查点/工件元数据和 SDK 辅助程序解析模型检查点或操作工件；不要猜测文件名，例如 `latest`。
4. 报告确切的搜索空间、算法、预算、指标和平台。
5. 报告自动基线评估任务 ID/结果路径/指标、所有推荐指标、最终评估状态/结果路径/指标、失败的推荐及其根本原因、已用时间和最终运行说明。
6. 如果此任务为 AutoML + DEFT 等工作流提供输入，请通过工作流声明的交接字段传递获胜规范覆盖和检查点。
7. 在默认保留策略下，验证已删除支持清理、可安全修剪的终端试验工件，并且获胜的训练工件仍然存在。明确报告受保护的提升/恢复父项或保守的 Hybrid 结果。SDK 无法回收的远程绑定、命名卷或其他输出路由必须在第一个试验之前失败保留预检，而不是被静默保留。

## 常见陷阱

在启动或恢复 AutoML 运行之前，请参阅 `references/automl-common-pitfalls.md`。
