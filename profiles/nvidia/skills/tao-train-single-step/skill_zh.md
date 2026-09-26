# 标准训练

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

标准监督微调：在标记数据集上训练模型，可选择评估，然后可选择导出。这是将预训练模型适配到新数据集的最常见的 TAO 工作流。

## 步骤

1. **train** — 当选择的模型具有 `automl_enabled: true` 且 `automl_policy` 为 `on` 时，通过 AutoML 执行；将 `automl_policy=off` 设置为纯单次训练运行
2. **eval** — 如果 `eval_dataset_uri` 解析成功则执行
3. **export** — 可选，训练后按用户请求执行

## 前置条件

选择的模型技能解析的 `container_image` 是默认训练运行时。除非用户明确请求，否则不要用主机 venv、`uv` 环境、通用训练镜像或手写训练器替换它。SDK/控制器 Python 环境仅用于控制平面；模型操作保持容器化。

### 必须的
- **model**: 兼容的 TAO 模型（例如，clip、nvdinov2、grounding_dino）
- **train_dataset_uri**: 训练数据集的 URI（例如，`s3://bucket/train/`）
- **platform**: 从安装的平台技能中发现执行平台（tao-run-on-docker / -slurm / -kubernetes / -brev，以及任何外部平台）；在仅显示核心路由技能的运行时上，读取 `skills/platform/tao-run-on-*/SKILL.md` 的 frontmatter。
- **容器镜像确认**: 从选择的模型/操作配置中解析默认镜像，向用户显示它，并在创建运行者文件或提交训练之前要求确认或 `image=<override>`。

### 可选的
- **eval_dataset_uri**: 某些模型技能将其标记为必需 — 在将其视为可选之前，请检查解析的模型技能。
- **base_checkpoint**: 如果未提供，则默认为模型技能中列出的 NGC 预训练检查点，如果没有 NGC 检查点则从头开始训练。
- **automl_policy**: 默认为 `on`；将 `off` 设置为跳过此运行级别的 AutoML，同时保留模型元数据不变。在新启动设置中仅使用 `on` / `off`。
- **image override**: 使用 `image=<override>` 固定特定的 TAO 工具包构建，在审查解析的默认值后使用。

## 启动输入

在用户确认他们想要此标准的训练/评估/导出工作流后，询问他们打算在哪个支持的平台运行。从安装的平台技能中发现执行平台（tao-run-on-docker / -slurm / -kubernetes / -brev，以及任何外部平台）；在仅显示核心路由技能的运行时上，读取 `skills/platform/tao-run-on-*/SKILL.md` 的 frontmatter。

在创建纯训练运行者之前，使用 `scripts/list_tao_models.py --scope automl --format json` 或读取 `skills/models/<network>/references/skill_info.yaml` 检查所选模型的元数据。如果 `automl_enabled` 为 true 且辅助工具报告该模型具有有效的训练模式，则默认通过 `skills/applications/tao-run-automl` 路由训练阶段。仅在 `automl_policy=off`、用户明确要求不进行 HPO/AutoML，或 AutoML 启用但无法运行因为模型的训练模式尚未打包时，才保持在纯训练路径上。

还询问长时间运行的监控是否应保持启用以及状态更新之间的分钟数。默认值：启用，5 分钟。

在模型/操作已知后，运行 `scripts/resolve_tao_image.py --model <network> --action train --format text` 并询问是否使用解析的镜像或 `image=<override>`。在确认镜像之前，不要创建 tao-train-single-step 运行者。

在平台选择后，读取所选平台技能的 `## 凭证` 部分和 `references/skill_info.yaml`（required_credentials / credential_groups），并仅请求与该平台相关的凭证，以及任何选择的模型凭证。不要请求不相关的平台凭证。
