<!-- 版权所有 (c) 2026, NVIDIA CORPORATION。保留所有权利。根据 Apache 许可证，版本 2.0 许可；请参阅 http://www.apache.org/licenses/LICENSE-2.0 -->

# tao-finetune-huggingface-model

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

本地 NVIDIA GPU 对 HuggingFace 模型的微调，基于实时获取的文档，并配有精选参考作为备用安全网。一个 NGC 容器，几个专注脚本，一次推送至 HF Hub。请遵循此文件中的规则；不要即兴创作。

## 专用模型路由网关

在步骤 1 之前或任何探测、图像选择、包安装、虚拟环境创建或训练代码生成之前，请解决 `model_id` 对应于打包模型所有者注册表。使用此文件加载的绝对技能库根目录：

```bash
python <bank-root>/scripts/resolve_tao_model.py \
  --skill-bank <bank-root> \
  --model "$MODEL_ID" \
  --format json
```

解析器匹配模型元数据，包括 `huggingface_model_ids`、`network_arch`、技能名称和遗留别名。路由是内部的：一个模型 ID 和任务就足够了。永远不要要求关于技能、容器或检查点格式的提示样板。

- 退出 `0`：停止此工作流并遵循拥有模型技能的环境、操作元数据、预检和检查点准备。
- 退出 `3`：没有打包的模型技能拥有该 ID。这是唯一允许通用工作流步骤 1 的结果。
- 任何其他非零退出：所有权发现是错误的或模糊的。停止并解决该错误；不要静默地回退到通用 Hugging Face 训练。

Hugging Face 托管永远不会覆盖所有权。不要使用此工作流来绕过匹配的技能或要求用户规定其内部准备。例如，`nvidia/Cosmos3-Nano` 路由到 `tao-finetune-cosmos-reason`。

在此工作流中不要创建主机训练虚拟环境。其默认执行路径是下面记录的 NGC 容器；任何基于虚拟环境的训练路径都需要明确的用户请求。

**权威顺序（最高优先）：**

1. **用户输入** — 显式的 `model_id`、`dataset_id`、`training_method`、`config.yaml` 覆盖。
2. **实时研究** — 模型卡、HF 仓库示例、作者微调脚本、HF 任务文档、论文；始终获取（步骤 3 + `references/research-priorities.md`）。
3. **精选参考** (`references/*.md`) — 当实时研究是沉默/模糊时作为备用。
4. **您的训练数据记忆** — 最后手段；怀疑，与（2）/（3）交叉检查。

（2）和（3）之间的冲突解决以及源行差异说明在 `references/research-priorities.md`。

---

## 输入

**必需的：**
- `model_id` — HuggingFace 模型 ID，例如 `google/vit-base-patch16-224`

**条件凭证（从会话环境读取——在启动之前导出或从用户批准的环境文件源中获取）：**
- `HF_TOKEN` — 仅当模型/数据集是 **受控** 时（读取）或 `push_to_hub` 为开启时（写入）；公共 + 公共 + `push_to_hub: false` 无需任何凭证。值从未读取——仅通过 `[ -n "$HF_TOKEN" ]` 进行存在验证。
- `WANDB_API_KEY`、`WANDB_PROJECT` — 仅当启用 WandB 时；`WANDB_MODE=disabled` 会禁用。

**数据集——正好一个：**
- `dataset_id` — HuggingFace 数据集 ID *(来源：`hf`)*
- `local_dataset_path` — 本地文件夹或文件 *(来源：`local`)*；可选
  `local_dataset_format` ∈ {auto, imagefolder, coco, voc, jsonl, arrow, parquet,
  csv} (默认：自动检测)。
- *(省略)* — 代理推荐流行数据集 *(来源：`recommend`)*

**可选的（有默认值）：**
- `task_type` — 从配置 + 模型卡自动检测
- `n_train=10000`、`n_eval=1000`、`n_epochs=3`、`lora_r=16`
- `output_dir=./output/<model_short_name>`
- `hf_model_repo` — 推送目标；如果未设置且 HF_TOKEN 具有写入权限，
  自动派生为 `<whoami>/<model_short_name>-finetuned`。
- `push_to_hub=True` — 设置为 `False` 以跳过
- `skip_baseline=False` — 跳过零样本基线评估

**可选交付物（默认关闭）：**
```yaml
emit_progress_log: false   # output_dir/PROGRESS.md (每步的日志)
emit_report:       false   # reports/report.{pdf,html} 带曲线和样本
emit_unit_tests:   false   # tests/ 带模拟数据异构批处理测试
```

所有值都存在于 `output_dir/config.yaml`。切勿在 Python 中硬编码。

---

## 执行平台

此技能协调要运行的内容；平台技能拥有在 GPU 主机上如何运行它的所有权——请先阅读它们。

| 关注点 | 权威技能 |
|---|---|
| GPU 主机运行时（驱动程序 580、CUDA Toolkit 13.0、NVIDIA 容器工具包 1.19.0） | [`tao-skill-bank:tao-setup-nvidia-gpu-host`](../../platform/tao-setup-nvidia-gpu-host/SKILL.md) |
| `docker run` 标志、NGC 认证、挂载、环境传递、本地/远程 Docker 工作预检（守护进程、GPU 烟雾测试） | [`tao-skill-bank:tao-run-on-docker`](../../platform/tao-run-on-docker/SKILL.md) |

**默认平台：** `local-docker` — 构建一次性镜像 (`run-<short>:latest`) 并在本地 Docker 守护进程上运行它。仅在用户明确需要不同后端（Brev 远程 GPU、SLURM/Kubernetes）时询问；然后运行该平台的预检，并将步骤 4–5 的 `docker run` 命令通过它路由。GPU 运行时和仅存在凭证预检（值从未读取）、标准的 `docker run` 标志集、从安装的平台技能发现执行平台（tao-run-on-docker / -slurm / -kubernetes / -brev，以及任何外部平台；在一个仅显示核心路由技能的运行时上，请参阅技能/platform/tao-run-on-*/SKILL.md 前置文本）、以及特定于工作流的标志 (`--entrypoint /bin/bash -lc`、`PYTORCH_CUDA_ALLOC_CONF`、`--name hft_train`) 都在 `references/workflow-intake-preflight.md` 中。

---

## 参考——备用安全网

仅在实时研究是沉默、模糊或不可用时才咨询；实时文档对特定模型和当前 API 总是获胜。每一步都链接它需要的参考；完整目录在 `references/detailed-workflow.md`。

始终启用：`core-rules.md`、`error-playbook.md`、`compat-workarounds.md`、`model-discovery.md`、`dataset-recommendations.md`、`dataset-sources.md`、`dataset-patterns.md`、`hardware-container.md`、`research-priorities.md`、`cv-scripts.md`、`vlm-scripts.md`、`docker-runs.md`、`hub-push.md`、`pipeline-skill-template.md`、`deliverables.md`。按需启用（当它们的标志/需求适用时）：`progress-tracking.md`、`testing.md`、`reporting.md`、`workflow-intake-preflight.md`、`workflow-generate-train.md`、`workflow-push-rerun.md`。

**规则：** 在回退之前，记录您尝试的实时源及其不足之处 (`config.yaml` `notes:`，如果启用，则记录 `PROGRESS.md`)。`cv-scripts.md` / `vlm-scripts.md` 中的 `[FETCH LIVE]` 标记是研究清单，不是内联代码——如果某个块没有步骤 3 找到，请重新获取列出的 URL。

---

## 核心规则

不可协商的行为。**简短版本**（完整枚举——幻觉导入列表、永不无批准列表、完整错误恢复和硬件尺寸表——在 `references/core-rules.md` 中，在做出任何训练时间决策之前查阅）：

- **您的 HF 库知识已过时。** 在编写任何 ML 代码之前获取实时文档（模型卡、HF 仓库示例、任务文档）——不要从记忆中生成训练器参数 / 分组器 / 变换（步骤 3）。
- **在真实数据上使用 `--max_steps 1` 进行烟雾测试** 在任何完整运行之前；没有验证烟雾的批处理启动。
- **永远不要无声地替换** `model_id`、`dataset_id` 或 `training_method` — 如果用户要求的内容无法加载，请停止并询问。
- **错误恢复是最小变更。** OOM → 将批处理减半，将梯度累积加倍，启用梯度检查点（没有 LoRA 切换则无需批准）；NaN → 将 LR 减少 10 倍；平坦损失 → 检查分组器；相同错误 3 次 → 停止并询问。不要循环。
- **数据集列在分组器之前验证** — 在 `prepare_data.py` 中重命名；需要重构 → 停止并询问。
- **硬件尺寸拇指（bf16）：** ≤3B → 24 GB，7–13B → 80 GB，30B+ → 多 GPU 或 1× 80 GB 上的 LoRA，70B+ → 8× 80 GB 或 LoRA。完整微调无法适应且未请求 LoRA → 在切换之前询问。

---

## 工作流——6 步骤

单次通过，顺序执行；每一步都有一个清晰的网关，在下一步开始之前。

### 步骤 1 — 检查和资格

**目标：** 决定是否继续。探测模型 + 数据集，应用接受/拒绝，注册适用的兼容修复，编写初始 `config.yaml`。

先决条件：`MODEL_ID`、可选的 `DATASET_ID` / `local_dataset_path`、可选的 `HF_TOKEN`、`OUTPUT_DIR`（默认 `./output/<model_short_name>`）。探测在仅 CPU 的 `python:3.12-slim` Docker 容器中运行（绑定挂载 `.probe/` 临时文件），因此主机不需要虚拟环境——Docker 必须先存在。Docker 存在的网关、容器环境、完整探测调用以及模型/数据集探测脚本在 `references/workflow-intake-preflight.md`、`references/model-discovery.md` 和 `references/dataset-sources.md` 中。

探测要求：

- 模型：加载 `AutoConfig`，读取模型卡标签，从 `architectures` + 标签 + 卡示例中检测任务（`model-discovery.md` 中的回退日志）。
- 数据集：对于推荐的数据集，首先从 `dataset-recommendations.md` 提供 3-5 个选择；对于本地数据，绑定挂载为只读并使用 `dataset-sources.md` 格式检测。
- 如果模型配置失败、任务超出范围、没有配方源或数据集无法加载/匹配任务模式，则早期拒绝。
- 评估 `compat-workarounds.md` 对模型/任务；将硬件依赖规则推迟到步骤 2。

编写初始 `config.yaml`（`model_id`、`task`、`dataset_id` 或 `local_dataset_path`、步骤 3 中填充的 `research_sources: []`、步骤 1 中的 `applicable_workarounds:`、用于参考回退的 `notes: []`、默认 `push_to_hub: true` — 在 `references/workflow-intake-preflight.md` 中注释的模板）。一旦网关满足，可以 `rm -rf "$OUTPUT_DIR/.probe"`。

**网关：** `config.yaml` 存在，包含模型、数据集、任务、适用的 `applicable_workarounds`；如果任何字段缺失，则不要继续。

---

### 步骤 2 — 硬件审计和 NGC 镜像

**目标：** 验证 Docker + GPU + 磁盘，选择实时 NGC PyTorch 镜像，最终确定硬件依赖的兼容规则。

**2a. 审计（硬网关）** — 三个检查（`references/workflow-intake-preflight.md` 中的命令）：
1. GPU 主机运行时 — `tao-setup-nvidia-gpu-host` 的
   `setup-nvidia-gpu-host.sh --backend docker --check-only`；失败时，询问批准，然后使用 `--install --yes` 重新运行。
2. 释放磁盘软警告 — 通过 `MIN_DISK_GB`（默认 100 GB）覆盖；建议 ≥ 100 GB，用于 NGC 基础 (~20 GB) + HF 缓存 + 检查点 + 数据。
3. 条件凭证存在（值从未读取）— 仅当受控或 `push_to_hub` 为开启时 `HF_TOKEN`；仅当启用 WandB 时 `WANDB_*`。

**不要在硬失败的情况下继续到步骤 4** — 步骤 4 的 `docker build` 会拉取 20+ GB 的 NGC 基础，而缺少 `nvidia-container-toolkit` 仅在稍后作为 `could not select device driver "" with capabilities: [[gpu]]` 才会暴露。记录 `gpu_count`、`gpu_name`、`driver_major`、`vram_gb_per_gpu` 在 `config.yaml` 中。

**2b. 选择 NGC 镜像（实时）：** 从 NVIDIA 深度学习框架支持矩阵（<https://docs.nvidia.com/deeplearning/frameworks/support-matrix/index.html>）的 PyTorch NGC 容器部分，选择最高版本的镜像，其中 `Min driver ≤ detected driver_major` 且容器 CUDA `≤` 主机 CUDA Toolkit（尽可能匹配，以便 cuDNN / TensorRT 对齐）。不要因为 `aN`/`bN`/`rcN` PyTorch 标签而拒绝镜像——NGC 验证完整镜像；选择最新 CUDA 匹配的镜像，并让 `compat-workarounds.md` 处理每个版本的问题。如果矩阵无法访问，请使用 `references/hardware-container.md` 中的回退；默认 `nvcr.io/nvidia/pytorch:24.09-py3` <!-- 未固定：记录的回退 --> (驱动程序 ≥ 545；SDPA+GQA 错误——如果 `num_key_value_heads < num_attention_heads`，设置 `attn_implementation: "eager"`)。
记录 `ngc_image` 在 `config.yaml` 中。

**2c. 重新评估硬件依赖的兼容规则：** 重新运行 `compat-workarounds.md` 对 `detect` 需要 `hw` 的条目；就地更新 `applicable_workarounds:`。

**2d. 模型拟合检查：** 估计 `param_bytes ≈ 2×param_count` (bf16)；如果 > 60% 的 `vram_gb_per_gpu × 1e9`，建议在用户界面摘要中 LoRA。

**网关：** `config.yaml` 包含 `ngc_image`、`gpu_count`、`gpu_name`、`driver_major`、`vram_gb_per_gpu`；记录了硬件依赖的兼容修复。

---

### 步骤 3 — 研究配方

**目标：** 获取实时配方——由于对 `transformers`/`trl`/`peft` 的训练数据知识是可疑的，因此步骤 3 是不可协商的。按优先级顺序（优先级 1 → 6）遵循 `references/research-priorities.md`；一旦您有了，对于检测到的任务：

- `AutoModel` / 处理器类
- 训练 + 评估变换
- 分组器
- `compute_metrics`
- 超参数提示（LR、批处理大小、周期、调度器）

在 `meta/recipe.md` 中记录结果，将源 URL 追加到 `config.yaml: research_sources:`。没有实时找到的插槽会回退到匹配的框架 (`cv-scripts.md` / `vlm-scripts.md`)，记录为 "回退到框架——没有实时源为 <插槽>" 在 `notes:` 下。冲突解决规则在 `references/research-priorities.md` 中。

**网关：** 每个必需插槽都已填充，带有源 URL 或框架回退说明。

---

### 步骤 4 — 生成项目和烟雾测试

**目标：** 编写所有脚本，构建镜像，准备数据，在真实数据上运行 1 步烟雾测试（一个 `docker build`，两个 `docker run`）。

**4a. 生成项目文件** 在 `output_dir/` 中：`config.yaml`、`Dockerfile`、`requirements.txt`、`prepare_data.py`、`train.py`、`run_eval.py`、`infer.py`、可选的 `merge_lora.py`、可选的 `tests/`、`.gitignore`。实时步骤 3 研究是权威；`cv-scripts.md` / `vlm-scripts.md` 仅提供框架形状。将每个 `applicable_workarounds` 条目作为 Dockerfile 块、要求固定、配置覆盖或运行时环境变量应用。硬规则：`run_eval.py` 保持该确切文件名（避免与 HF 的 `evaluate` 包冲突）；每个生成的 `.py` 以 NVIDIA Apache-2.0 版权声明开头，如果缺少则任何发射器都会失败；`emit_unit_tests: true` 生成并运行测试，每 `references/testing.md`。脚本正文、Dockerfile 形状和发射器合同在 `references/workflow-generate-train.md` 中。

**4b. 构建、准备、烟雾** — `docker build -t run-<short>:latest .`，然后 `prepare_data` 和 `--smoke --max_steps 1` 运行 (`references/docker-runs.md` §1-3)。烟雾通过标准（在 `logs/smoke.log`）：
- 没有异常
- 损失是有限的（不是 `0.0`，不是 `NaN`)
- `grad_norm > 0` 在步骤 1

如果 `emit_unit_tests: true`，也在容器中运行 `pytest tests/`。任何失败 → 停止。

**4c. 预检摘要** — 在完整训练之前，打印并验证：参考 URL、数据集列、Hub 目标、监控目标、NGC 镜像、硬件、烟雾损失/梯度规范。

**网关：** 项目文件已写入，镜像已构建，烟雾通过，预检没有空白字段。

---

### 步骤 5 — 训练、评估、推理

**目标：** 基线评估、完整训练、训练后评估、可选 LoRA 合并、5 个推理样本（所有命令：`references/docker-runs.md` §4-8）。

| 子步骤 | docker-runs.md | 如果跳过 |
|---|---|---|
| 5a. 基线评估（零样本） | §4 | `skip_baseline: true` |
| 5b. 完整训练（分离） | §5 | — |
| 5c. LoRA 合并 | §6 | 不是 VLM+LoRA |
| 5d. 训练后评估 | §7 | — |
| 5e. 推理（5 个样本） | §8 | — |

多 GPU：在 `python train.py` 前面添加 `torchrun --nproc_per_node=$gpu_count`。

在训练流期间，查看 `docker logs -f hft_train`：损失应在 10-20 步内下降；平坦损失（分组器/标签掩码错误）、NaN（LR 太高）和 OOM 都会停止运行——恢复在 `references/core-rules.md` 中。如果 `emit_report: true`，在步骤 5e 后运行 `report.py`，每 `references/reporting.md`。

**网关：** 所有以下内容：
- `checkpoints/final/`（或 `checkpoints/merged/` 对于 LoRA）存在
- `reports/eval_results.json` 包含一个数字主要指标
- `reports/baseline_results.json` 存在（如果跳过）
- `reports/inference_samples/` 包含 5 个样本
- wandb URL 显示损失下降

---

### 步骤 6 — 推送和发射重跑技能

**目标：** 发布运行并使其无需重新研究即可重现。

根据 `references/hub-push.md` 推送（权重、模型卡、评估/基线 JSONs、`config.yaml`、`Dockerfile`、`requirements.txt`、推理样本、在发射时包含报告）除非明确 `push_to_hub: false`。从 `references/pipeline-skill-template.md` 发射
`<output_dir>/skills/run-<short>/SKILL.md` — 替换每个占位符，包含完整的 YAML 元数据 + NVIDIA 版权 HTML 注释，并且如果缺少这些，任何发射器都会失败。

**网关（完成标准）：** 所有以下内容：
- 步骤 5 网关满足
- HF Hub 仓库在解析的 URL 存在，包含权重 + 卡 + `results/`（除非 `push_to_hub: false`）
- `<output_dir>/skills/run-<short>/SKILL.md` 存在，没有 `<placeholder>` 留下，
  根据 `pipeline-skill-template.md` 的元数据 + 版权 HTML 注释

最终消息：wandb URL、HF Hub URL、基线 -> 微调主要指标、`reports/inference_samples/`，以及重跑技能路径。

---

## 错误剧本

在已知运行时错误的情况下，请先咨询 `references/error-playbook.md` 中的症状 → 最小修复表（NGC 入口点、PyTorch/Transformers 回归、numpy ABI、Albumentations bbox、PEFT/checkpointing、LoRA 目标宽度、CV 增强差距、步骤 0 时的 OOM）之前不要重新设计任何东西。当某一行在这里跨运行两次时，将其提升到 `compat-workarounds.md` 中，并带有 `detect` 规则——在错误发生之前自动应用，在步骤 1 之前。

---

## 沟通风格

- 简洁。没有填充，没有重述请求；在适当的时候使用单字回答。
- 始终在引用工件时包含直接的 Hub 和 wandb URL。
- 出错时：说明出了什么问题，为什么，你做了什么——不要菜单。
- 对于有明确答案的请求，永远不要呈现 "选项 A/B/C"。行动。
