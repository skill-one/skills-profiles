# TAO 自动机器学习

> **独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup`（主机预检、凭证、跨技能发现）。

通过组合以下内容来对 TAO 模型运行自动超参数优化：

1. 在 `skills/models/<model_skill>/` 下选择的模型技能。
2. 在 `skills/platform/<platform>/` 下选择的平台技能。
3. `AutoMLRunner`，它生成建议、启动选定的动作作业、提取指标并将结果反馈给优化器。

在模型元数据、平台预检、数据可见性、凭证、图像选择和计算形状都得到验证后，才启动。

## 执行运行时 — 硬性门禁

默认情况下，每个建议、基线评估、每个建议评估和最终评估都在选定的模型动作解析的 `container_image` 中运行。在设置任何训练环境之前，从模型技能解析它。本地检查点或 Hugging Face 模型 ID 不会改变此规则。

仅在明确请求时才使用基于 venv 的 **模型执行**。不要从 `local-docker`、本地 GPU、Python 或 `pyproject.toml` 推断 venv 模式。如果不存在，执行是容器后端的。`tao_automl`、TAO SDK 或平台适配器的主机/控制器 venv 仅用于控制平面；将子模型动作保持在解析的容器镜像中。

## 参考映射

- `references/skill_info.yaml`：此工作流的结构化元数据。
- 分割详细参考：`automl-preflight-concepts.md` 用于先决条件和支持检查；`automl-intent-algorithms.md` 用于搜索策略；`automl-compression-literature.md` 用于蒸馏/剪枝/量化算法的充分性和未来压缩搜索路线图；`automl-runner-configuration.md` 用于 runner/API/WandB 详细信息；`automl-advanced-monitoring.md` 用于钩子、恢复和陷阱；以及 `automl-examples.md` 用于对话示例；以及 `automl-common-pitfalls.md` 用于重复的安全检查。`detailed-guide.md` 仅是地图。
- `skills/models/<network>/SKILL.md`：特定于模型的 dataset 要求、指标、HPO 注释、检查点传递和已知错误。
- `skills/models/<network>/references/skill_info.yaml`：动作合同、容器镜像、输入、输出、上传排除和 `mode`。
- `skills/platform/<platform>/SKILL.md`：选定的平台预检、凭证、资源形状、监控和取消。
- `skills/core/tao-launch-workflow/SKILL.md`：平台、凭证、dataset 可见性、图像确认和用户确认的共享摄入模式。

## 预检

1. 运行共享启动摄入。如果用户未选择平台，请询问；Brev、SLURM、Kubernetes 和 Docker 是平等的伙伴。
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

## 模型支持门禁

在每次运行之前：

1. 读取模型的 `SKILL.md` 和 `references/skill_info.yaml`。
2. 确认模型或模型技能明确将选定的动作路由到 AutoML 的 `automl_enabled: true`。
3. 确认 `<skill_dir>/schemas/<action>.schema.json` 存在并可解析。这是 AutoML 搜索空间门禁。
4. 对于非 TAO-Core 模型（如 Cosmos-RL 和 CLIP），还要求 `references/spec_template_<action>.yaml`；否则，runner 没有完整的动作默认值。
5. 如果任何门禁失败，不要自行设计搜索空间。报告缺失的包工件。

## 输入

在构建 runner 之前收集这些内容：

| 输入 | 要求 |
|---|---|
| `model_skill` | 在 `skills/models/` 下解析的模型技能目录。首先解析用户别名（如 `network_arch`）到打包的技能目录。 |
| `network_arch` | 从解析的模型技能元数据中读取。 |
| `action` | 要优化的动作 — `train`、`evaluate`、`inference`、`distill`、`prune` 或 `quantize`，带有打包的 schema/template。 |
| `platform` | 支持的 TAO 平台技能之一。 |
| `train_dataset` / `eval_dataset` / 动作输入 | 使用模型特定的 spec 键和布局。非训练动作可能还需要父/教师检查点、校准数据或剪枝工件。 |
| `results_root` | 适合平台的本地、Lustre 或 S3 路径。 |
| `gpu_count`, `num_nodes` | 尊重模型和平台的限制。 |
| `container_image` | 通过模型元数据和 `versions.yaml` 解析；向用户显示它。 |
| `automl_algorithm` | 默认为 `bayesian`，除非用户请求其他算法或模型技能推荐一个。 |
| `metric`, `direction` | 优先使用模型技能的验证/任务指标。 |
| `automl_budget` | 算法所需的建议计数、最大 epoch/rungs、并发或种群大小。 |

不要请求秘密值。使用 `[ -n "$VAR_NAME" ] && echo SET || echo UNSET"` 验证必需的环境变量。

## 启动前审查门禁

在启动任何建议作业之前，显示具体的启动审查并获取用户确认。此门禁适用于每个 AutoML 运行和每个 AutoML 支持的模型/网络；它不是 Cosmos 特定的，并且不得仅限于单个模型技能。即使平台和图像预检已通过，也适用。审查必须包括：

- 模型/网络、平台、图像、GPU/节点形状和结果/工作区根
- 数据集模式和具体的 spec 键，包括当它们可以廉价读取时的训练/评估样本计数
- 算法、预算、最大并发作业、指标和方向
- 可搜索参数和范围，包括用户未提供明确搜索空间时的默认值
- 为初始启动批次生成的确切建议配置，在提交任何建议作业之前，在仅用于审查的步骤中生成
- 每个建议的估计运行时间和总预期墙时间，以及使用的假设
- 自动基线评估作业 ID、指标值和结果路径，来自预检后的评估作业，或者如果模型没有可运行的评估动作或验证数据，则提供一个明确的阻止器
- 为选定的最佳检查点/模型选择的 AutoML 后评估计划，包括指标、数据集和记录路径

如果估计时间超过用户声明的限制或明显长于正常交互运行，请在启动前询问是否要减少建议、epoch、数据集大小、验证频率或搜索空间。不要在日志中隐藏多天的估计。

## 自动基线评估作业

在平台、图像、凭证、数据、模型预检通过后，在提交任何 AutoML 建议作业之前，在选定的验证/评估数据上运行模型的评估动作一次。这是必需的 AutoML 设置，而不是用户可选的“预训练评估”问题。使用与 AutoML 训练运行开始相同的基线模型或检查点、模型技能的评估 spec/template 和选定平台的正常作业提交路径。如果模型技能建议评估比训练更小的形状，请使用该形状并在启动审查中指明。

在请求确认之前，在启动审查中共享评估指标编号。如果存在起始检查点，但基线无法生成 — 没有打包的评估动作、缺少评估数据、评估作业失败 — 则停止并报告阻止器，而不是默默地回退到仅训练损失的运行。

对于从头开始训练，将基线记录为不可用并继续；不要评估空检查点。

runner 拥有最终评估。当评估可运行时，将 `final_eval_fn(best_rec, train_job_id)` 传递给 `AutoMLRunner.run`；结果将包含 `result["final_evaluation"]`。参见 `automl-preflight-concepts.md` 了解回调、检查点、基线和从头开始规则。

## 依赖和数据预检

如果选定的工作流需要对象存储或平台 CLI，而工具缺失，请报告缺失的依赖项并提供建立确切的安装命令，然后再继续。在用户批准后，使用 `scripts/check_tao_launch_preflight.py` 并带 `--install-missing-tools` 重新运行，以便它安装最小的必需包并立即重试路径验证。对于 S3 路径，在创建 runner 资产之前，从启动平台验证凭证和路径可读性。

对于在每次训练试验期间读取大型媒体存档或目录的模型，将数据集一次阶段或提取到存储中，该存储对执行平台可见，然后将所有建议 spec 指向该阶段路径。记录源 URI、阶段路径、字节/文件计数证据（如果可用）和时间戳在 `<workspace>/evaluations/data_staging.json`。如果无法阶段，请在启动审查中包括重复的 S3 I/O 风险，并在花费很长时间的 AutoML 预算之前询问。

当模型技能定义样本计数敏感的约束时，在启动前执行它们。拒绝或限制每个批量大小建议，如果它为选定的数据集和 GPU 分片计数创建零训练步骤。使用 `scripts/check_tao_launch_preflight.py --effective-batch-limit train_annotation=<batch_size>,<shard_count>` 为每个生成的建议在提交之前执行。如果建议后来因为数据太小而无法有效批量大小而失败，将其分类为无效配置，在剩余预算存在时替换或调整它，并在最终摘要中报告更正。
当训练样本计数从注释文件或廉价清单读取时，将其作为 `automl_settings["train_sample_count"]` 传递给 `AutoMLRunner.run`，以便 runner 可以在提交作业之前限制不可能的建议，并在 `result["history"][i]["adjustments"]` 中记录调整。
