# 重新识别

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

人员重新识别。学习判别嵌入，以匹配不同摄像头视图中的同一个人。基于度量学习。

设置 `model.pretrained_model_path` 以使用预训练权重。

## 快速入门 (docker run)

原生 Docker 启动 — 无需 TAO SDK 和主机上的 Python。当它提供更严格的环境特定命令时（非 root UID 映射、缓存重定向、远程守护进程），请使用本地 Docker/平台技能。

```bash
TAO_PYT_IMAGE_DEFAULT=nvcr.io/nvidia/tao/tao-toolkit:7.2.0-pyt  # versions-key: images.tao_toolkit.pyt
TAO_PYT_IMAGE="${TAO_PYT_IMAGE:-$TAO_PYT_IMAGE_DEFAULT}"
RUN_ROOT="${RUN_ROOT:-$PWD}"
DOCKER_COMMON=(
  --rm --gpus all --shm-size=8g
  --shm-size=8g
  --ulimit memlock=-1
  --ulimit stack=67108864
  -v "$RUN_ROOT/data:/data:ro"
  -v "$RUN_ROOT/specs:/specs:ro"
  -v "$RUN_ROOT/results:/results"
)
```

训练：

```bash
docker run "${DOCKER_COMMON[@]}" "$TAO_PYT_IMAGE" \
  re_identification train -e /specs/train.yaml
```

评估：

```bash
docker run "${DOCKER_COMMON[@]}" "$TAO_PYT_IMAGE" \
  re_identification evaluate -e /specs/evaluate.yaml
```

推理：

```bash
docker run "${DOCKER_COMMON[@]}" "$TAO_PYT_IMAGE" \
  re_identification inference -e /specs/inference.yaml
```

导出：

```bash
docker run "${DOCKER_COMMON[@]}" "$TAO_PYT_IMAGE" \
  re_identification export -e /specs/export.yaml
```

每个操作都使用 `-e` 带其 spec；`results_dir` 在 spec 中设置或在命令行中覆盖。挂载 spec 引用的任何预训练权重目录，并确保容器内路径在所有操作中保持一致。

## 数据类模式

生成的 TAO Core 模式打包在 `schemas/<action>.schema.json` 中，`schemas/manifest.json` 列出可用操作。每个生成的模式还从模式顶层 `default` 字段发出 `references/spec_template_<action>.yaml`。AutoML 启用声明在 `references/skill_info.yaml` 中的模型层通过 `automl_enabled` 声明。可运行的 AutoML 需要存在并解析 `schemas/<action>.schema.json` 和 `references/spec_template_<action>.yaml`。使用打包的选定操作模式进行 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖项和常用参数。不要期望运行时有 `~/tao-core`；维护者在打包技能库之前重新生成模式/模板。

## 训练操作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，读取 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将类似于 "关闭 AutoML"、"禁用 AutoML"、"无 HPO" 或 "纯训练" 的短语视为 `automl_policy: off` 仅对此运行。当 `automl_policy: on`、`automl_enabled: true`，并且 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 都被打包时，默认通过此模型的 `skill_dir` 将训练操作路由到 `tao-skill-bank:tao-run-automl`。保留数据集、spec、输出目录、GPU/平台设置、父检查点和 `automl_policy` 的流程/应用程序覆盖。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时才使用直接模型训练；在缺失模式的情况下，报告此模型启用 AutoML 但不可运行，直到生成模式。

非训练操作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每次运行的 `automl_policy` 覆盖不会更改模型元数据。

## 支持的操作

打包的 Re-Identification PyT CLI 支持 `train`、`evaluate`、`inference`、`export` 和 `default_specs`。此模型技能公开可运行的用户操作 `train`、`evaluate`、`inference` 和 `export`；恢复/重新训练通过 `train` 使用 `train.resume_training_checkpoint_path` 执行。

不要为此模型宣传或合成 `dataset_convert`、`deploy`、`prune`、`quantize`、`gen_trt_engine` 或独立的 `retrain`，除非打包的模型技能和实际 CLI 添加了这些操作。

## 训练要求

- **数据集类型：** re_identification
- **格式：** 默认
- **AutoML 训练指标：** `cmc_rank_1`（最大化）。训练状态文件为试验排名发出此检索 KPI。
- **独立评估指标：** `mAP`。评估操作将 `mAP` 写入其状态 KPI 并在其控制台表格中打印 CMC 排名；不要期望独立评估状态包含 `cmc_rank_1`。

### 每个操作的 数据集 要求

| 操作 | Spec Key | 源 | 文件 | 列表？ |
|---|---|---|---|---|
| evaluate | evaluate.test_dataset | train_datasets | sample_test.tar.gz | 否 |
| evaluate | evaluate.query_dataset | train_datasets | sample_query.tar.gz | 否 |
| inference | inference.test_dataset | train_datasets | sample_test.tar.gz | 否 |
| inference | inference.query_dataset | train_datasets | sample_query.tar.gz | 否 |
| train | dataset.train_dataset_dir | train_datasets | sample_train.tar.gz | 否 |
| train | dataset.test_dataset_dir | train_datasets | sample_test.tar.gz | 否 |
| train | dataset.query_dataset_dir | train_datasets | sample_query.tar.gz | 否 |

### 典型 Spec 覆盖

数据源覆盖对每个操作都是**强制性的** — 代理必须根据上表中的 Per-Action Dataset Requirements 构造数据源路径并将其包含在 `spec_overrides` 中。

```python
S3_TRAIN = "s3://bucket/data/train"
CHECKPOINT = "/results/{train_job_id}/results_dir/model_epoch_000_step_00099.pth"
```

**train (强制数据源):**
```python
{
    "train.num_epochs": 30,
    "train.checkpoint_interval": 10,
    "train.validation_interval": 10,
    "train.num_gpus": 1,
    "dataset.num_classes": 100,
    "dataset.num_workers": 4,
    "dataset.batch_size": 16,
    "dataset.num_instances": 4,
    "dataset.train_dataset_dir": f"{S3_TRAIN}/sample_train.tar.gz",
    "dataset.test_dataset_dir": f"{S3_TRAIN}/sample_test.tar.gz",
    "dataset.query_dataset_dir": f"{S3_TRAIN}/sample_query.tar.gz",
}
```

**恢复训练 (强制检查点):**
```python
{
    "train.num_epochs": 31,
    "train.resume_training_checkpoint_path": CHECKPOINT,
    "dataset.num_classes": 100,
    "dataset.batch_size": 16,
    "dataset.num_instances": 4,
    "dataset.train_dataset_dir": f"{S3_TRAIN}/sample_train.tar.gz",
    "dataset.test_dataset_dir": f"{S3_TRAIN}/sample_test.tar.gz",
    "dataset.query_dataset_dir": f"{S3_TRAIN}/sample_query.tar.gz",
}
```

**评估 (强制数据源和检查点):**
```python
{
    "evaluate.test_dataset": f"{S3_TRAIN}/sample_test.tar.gz",
    "evaluate.query_dataset": f"{S3_TRAIN}/sample_query.tar.gz",
    "evaluate.checkpoint": CHECKPOINT,
    "evaluate.output_cmc_curve_plot": "/results/{evaluate_job_id}/results_dir/cmc_curve.png",
    "evaluate.output_sampled_matches_plot": "/results/{evaluate_job_id}/results_dir/sampled_matches.png",
}
```

**导出 (强制检查点和输出):**
```python
{
    "export.checkpoint": CHECKPOINT,
    "export.onnx_file": "/results/{export_job_id}/results_dir/reid.onnx",
}
```

**推理 (强制数据源和检查点):**
```python
{
    "inference.test_dataset": f"{S3_TRAIN}/sample_test.tar.gz",
    "inference.query_dataset": f"{S3_TRAIN}/sample_query.tar.gz",
    "inference.checkpoint": CHECKPOINT,
    "inference.output_file": "/results/{inference_job_id}/results_dir/reid_inference.json",
}
```

对于导出和推理，为 `export.onnx_file` 和 `inference.output_file` 提供显式的文件路径。对于评估，为 `evaluate.output_cmc_curve_plot` 和 `evaluate.output_sampled_matches_plot` 提供显式的文件路径。将这些作为 spec 值或 `spec_params` 映射保留；不要在本地 Docker 中将它们声明为文件输出，直到运行者在输出预创建期间区分文件和文件夹。

## 评估数据集

必需。评估需要用于检索指标的测试和查询数据集（CMC、mAP）。

## 重要参数

- **dataset.num_classes**: 身份数量。默认 751。必须与训练数据中唯一身份的数量匹配。
- **model.backbone**: 默认 resnet_50。
- **optim.base_lr**: 基础学习率。默认 3.5e-4。
- **dataset.batch_size**: 每个GPU的批大小。默认 64。重新识别受益于大批量以进行更好的三元组/对比采样。
- **dataset.num_instances**: 每个身份在批次中的实例数量。控制度量学习的采样策略。

## 多 GPU / 多节点

**启动方法：** Lightning 管理的（单个 `python` 进程，Lightning 生成工作进程）。

| Spec Key | 描述 | 默认 |
|---|---|---|
| `train.num_gpus` | GPU 数量 | 1 |
| `train.gpu_ids` | GPU 设备索引 | [0] |

- 多 GPU 策略：`ddp_find_unused_parameters_true`
- `sync_batchnorm` 始终启用
- 精度强制为 FP16 (`16-mixed`)
- 没有显式的 `num_nodes` 配置 — 单节点导向

## 硬件

至少 1 个 GPU(s)，推荐 2 个 GPU(s)。每个 GPU 16GB+ VRAM。重新识别模型相对轻量级，但受益于大批量以进行度量学习。

## 错误模式

**num_classes 不匹配**：确保 `dataset.num_classes` 等于训练集中唯一身份文件夹的数量。

**无效三元组批次形状**：`dataset.batch_size` 必须与 `dataset.num_instances` 兼容，以便每个小批次可以重塑以进行硬示例挖掘。对于本地 AutoML 烟雾运行，将 `dataset.batch_size` 固定为一个已知的有效倍数，例如 `dataset.batch_size: 16` 与 `dataset.num_instances: 4`，而不是无约束的批大小，并调整 `train.optim.base_lr`。

**查询/画廊不匹配**：查询和测试（画廊）数据集必须共享相同的身份命名空间。

**PyTorch 2.6 检查点加载失败于检查点消费者**：当前的 Re-ID 检查点包括 OmegaConf 容器。对于由相同的可信 TAO 训练/AutoML 工作流生成的检查点，在下游恢复、评估、推理和导出作业环境变量中设置 `TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1`，以便 Lightning/PyTorch 可以加载完整检查点。不要为此环境变量使用不可信的检查点。

**AutoML 指标提取**：Re-ID 训练状态文件报告检索 KPI，如 `cmc_rank_1`、`cmc_rank_5`、`cmc_rank_10` 和 `mAP`，以及训练损失。默认 AutoML 训练启动必须优化 `cmc_rank_1`（方向：最大化）；不要将 `val_loss` 作为此模型的指标使用。

**检查点交接**：使用最佳 AutoML 子作业的 `results_dir/train/` 文件夹上的检查点解析器，并选择适用于操作的 `model_epoch_*.pth` 检查点。Re-ID 还写入 `reid_model_latest.pth`，但这是一个最新符号链接，仅在调用者显式请求时使用。保留相同的数控行程和查询/画廊存档以供下游操作使用。

**默认 spec 生成**：打包的 `default_specs` CLI 操作不会消耗 `results_dir` 的正常 `-e <spec.yaml>` 实验文件。使用 Hydra 覆盖（如 `re_identification default_specs results_dir=/workspace/run/results/default_specs`）调用它。仅传递 `-e` 会将 `cfg.results_dir` 设置为未定义并因 `MissingMandatoryValue: results_dir` 而失败。

## Spec Param / 父模型推理

特定于模型的推理映射属于此 MD 文件，而不是 `config.json`。生成的运行者应在 `create_job()` 之前读取此部分并使用 SDK 帮助程序应用映射。这类似于旧的微服务 `infer_params.py` 流程。

来自 TAO Core `re_identification.config.json` 的推理映射：

| 操作 | Spec Field | 推理函数 | 含义 |
|---|---|---|---|
| evaluate | `encryption_key` | `key` | 加密密钥 |
| evaluate | `evaluate.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| evaluate | `evaluate.output_cmc_curve_plot` | `create_evaluate_cmc_plot_reid` | ReID CMC 图路径 |
| evaluate | `evaluate.output_sampled_matches_plot` | `create_evaluate_matches_plot_reid` | ReID 采样匹配图路径 |
| evaluate | `results_dir` | `output_dir` | 当前作业结果目录 |
| export | `encryption_key` | `key` | 加密密钥 |
| export | `export.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| export | `export.onnx_file` | `create_onnx_file` | 输出 ONNX 路径 |
| export | `results_dir` | `output_dir` | 当前作业结果目录 |
| inference | `encryption_key` | `key` | 加密密钥 |
| inference | `inference.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| inference | `inference.output_file` | `create_inference_result_file_reid` | ReID 推理 JSON 路径 |
| inference | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `encryption_key` | `key` | 加密密钥 |
| train | `model.pretrained_model_path` | `ptm_if_no_resume_model` | 当没有恢复检查点时 PTM |
| train | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `train.resume_training_checkpoint_path` | `resume_model` | 从当前作业结果文件夹推断的模型文件 |

对于 `parent_model` 或 `parent_model_folder`，传递上游训练/导出/AutoML 子作业 ID 作为 `parent_job_id`。SDK 列出父结果文件夹，过滤检查点工件，并返回选定的模型文件或文件夹。不要将这些映射重新添加到 `config.json`，也不要修补生成的运行者脚本以猜测检查点路径。
