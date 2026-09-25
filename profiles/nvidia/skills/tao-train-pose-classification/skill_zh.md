# 姿态分类

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

使用 ST-GCN（时空图卷积网络）进行姿态分类。将骨架序列分类为动作类别，基于姿态关键点数据。

通常从头开始使用骨架数据训练。

打包的 PyTorch 姿态分类 CLI 支持 `dataset_convert`、`train`、`evaluate`、`export` 和 `inference`。`dataset_convert` 是有条件的：仅在输入为原始 DeepStream BodyPose JSON 时运行。如果数据集已经转换为 TAO 就绪的 `.npy` / `.pkl` 文件，则直接在这些文件上开始 `train`，并在验证报告中将数据集转换标记为 `not run: preconverted dataset provided`。此模型不暴露部署、剪枝、量化或独立重训练操作。恢复/重训练行为使用 `pose_classification train -e ...` 并填充 `train.resume_training_checkpoint_path`。

## 快速入门（docker run）

原生 Docker 启动——主机上无需 TAO SDK 和 Python。当它提供更严格的环境特定命令（非 root UID 映射、缓存重定向、远程守护进程）时，使用本地 Docker/平台技能。

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

数据集转换：

```bash
docker run "${DOCKER_COMMON[@]}" "$TAO_PYT_IMAGE" \
  pose_classification dataset_convert -e /specs/dataset_convert.yaml
```

训练：

```bash
docker run "${DOCKER_COMMON[@]}" "$TAO_PYT_IMAGE" \
  pose_classification train -e /specs/train.yaml
```

评估：

```bash
docker run "${DOCKER_COMMON[@]}" "$TAO_PYT_IMAGE" \
  pose_classification evaluate -e /specs/evaluate.yaml
```

推理：

```bash
docker run "${DOCKER_COMMON[@]}" "$TAO_PYT_IMAGE" \
  pose_classification inference -e /specs/inference.yaml
```

导出：

```bash
docker run "${DOCKER_COMMON[@]}" "$TAO_PYT_IMAGE" \
  pose_classification export -e /specs/export.yaml
```

每个操作都使用 `-e` 带其 spec；`results_dir` 在 spec 中设置或在命令行中覆盖。挂载 spec 引用的任何预训练权重目录，并确保容器内路径在所有操作中保持一致。

## 数据类模式

生成的 TAO Core 模式打包在 `schemas/<action>.schema.json` 中，`schemas/manifest.json` 列出可用操作。每个生成的模式也从模式的顶层 `default` 字段发出 `references/spec_template_<action>.yaml`。AutoML 启用声明在 `references/skill_info.yaml` 中的模型层通过 `automl_enabled`。运行 AutoML 需要存在并解析 `schemas/<action>.schema.json` 和 `references/spec_template_<action>.yaml`。使用打包的选定操作模式用于 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖关系和常用参数。不要期望 `~/tao-core` 在运行时；维护者在打包技能库之前重新生成模式/模板。

## 训练操作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，读取 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将短语如 "关闭 AutoML"、"禁用 AutoML"、"无 HPO" 或 "纯训练" 视为仅对此运行 `automl_policy: off`。当 `automl_policy: on`、`automl_enabled: true`，并且 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 都被打包时，默认通过此模型的 `skill_dir` 路由训练操作到 `tao-skill-bank:tao-run-automl`。保留流程/应用程序覆盖的数据集、spec、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包训练模式/模板缺失时使用直接模型训练；在缺失模式的情况下，报告此模型启用 AutoML 但不适用于此模型，直到生成模式。

非训练操作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每运行的 `automl_policy` 覆盖不会更改模型元数据。

## 训练要求

- **数据集类型：** pose_classification
- **格式：** 默认
- **AutoML 训练指标：** `val_loss`，方向为 `minimize`
- **独立评估指标：** `accuracy`，方向为 `maximize`。使用 `val_loss` 对训练阶段的 AutoML 推荐进行排序，并仅使用 `accuracy` 来验证所选检查点是否加载并成功评估。

### 每个操作的 数据集 要求

| 操作 | Spec Key | 来源 | 文件 | 列表？ |
|---|---|---|---|---|
| dataset_convert (可选) | dataset_convert.data | id | DeepStream BodyPose JSON | 否 |
| evaluate | evaluate.test_dataset.data_path | train_datasets | val_data.npy | 否 |
| evaluate | evaluate.test_dataset.label_path | train_datasets | val_label.pkl | 否 |
| inference | inference.test_dataset.data_path | train_datasets | test_data.npy | 否 |
| train | dataset.train_dataset.data_path | train_datasets | train_data.npy | 否 |
| train | dataset.train_dataset.label_path | train_datasets | train_label.pkl | 否 |
| train | dataset.val_dataset.data_path | train_datasets | val_data.npy | 否 |
| train | dataset.val_dataset.label_path | train_datasets | val_label.pkl | 否 |

### 典型的 Spec 覆盖

数据源覆盖对每个正在运行的操作都是**强制性的**——代理必须根据上表中的每个操作的 数据集 要求构建数据源路径，并将其包含在 `spec_overrides` 中。当提供的 数据集 已经转换为 `.npy` / `.pkl` 文件时，不要运行 `dataset_convert`。

```python
S3_TRAIN = "s3://bucket/data/purpose_built_models_pose_classification_train/nvidia"
CHECKPOINT = "/results/{train_job_id}/results_dir/model_epoch_000_step_00007.pth"
```

**dataset_convert (可选；仅限原始 DeepStream BodyPose JSON):**
```python
{
    "dataset_convert.data": "s3://bucket/data/<deepstream-bodypose-output>.json",
}
```

**train (强制数据源):**
```python
{
    "train.num_epochs": 30,
    "train.checkpoint_interval": 10,
    "train.validation_interval": 10,
    "train.num_gpus": 1,
    "wandb.enable": False,
    "dataset.num_classes": 6,
    "dataset.label_map": {
        "class_0": 0,
        "class_1": 1,
        "class_2": 2,
        "class_3": 3,
        "class_4": 4,
        "class_5": 5,
    },
    "model.graph_layout": "nvidia",
    "dataset.train_dataset.data_path": f"{S3_TRAIN}/train_data.npy",
    "dataset.train_dataset.label_path": f"{S3_TRAIN}/train_label.pkl",
    "dataset.val_dataset.data_path": f"{S3_TRAIN}/val_data.npy",
    "dataset.val_dataset.label_path": f"{S3_TRAIN}/val_label.pkl",
}
```

**resume train (强制检查点):**
```python
{
    "train.num_epochs": 31,
    "train.resume_training_checkpoint_path": CHECKPOINT,
    "dataset.train_dataset.data_path": f"{S3_TRAIN}/train_data.npy",
    "dataset.train_dataset.label_path": f"{S3_TRAIN}/train_label.pkl",
    "dataset.val_dataset.data_path": f"{S3_TRAIN}/val_data.npy",
    "dataset.val_dataset.label_path": f"{S3_TRAIN}/val_label.pkl",
}
```

**evaluate (强制数据源):**
```python
{
    "evaluate.test_dataset.data_path": f"{S3_TRAIN}/val_data.npy",
    "evaluate.test_dataset.label_path": f"{S3_TRAIN}/val_label.pkl",
    "evaluate.checkpoint": CHECKPOINT,
}
```

**export (强制检查点和输出):**
```python
{
    "export.checkpoint": CHECKPOINT,
    "export.onnx_file": "/results/{export_job_id}/results_dir/pose_classification.onnx",
}
```

**inference (强制数据源):**
```python
{
    "inference.test_dataset.data_path": f"{S3_TRAIN}/test_data.npy",
    "inference.test_dataset.label_path": f"{S3_TRAIN}/test_label.pkl",
    "inference.checkpoint": CHECKPOINT,
    "inference.output_file": "/results/pose_classification_inference.txt",
}
```
## 数据集转换

姿态分类的数据集转换是可选的。仅当用户提供原始 DeepStream BodyPose JSON 时，运行 `pose_classification dataset_convert`。对于常见的 S3 验证 数据集，数据已经转换为 `train_data.npy`、`train_label.pkl`、`val_data.npy`、`val_label.pkl`、`test_data.npy` 和 `test_label.pkl`；直接使用这些文件进行 train/evaluate/inference/export 流程，不要合成假的 BodyPose JSON。

## 评估 数据集

可选。验证数据与训练数据一起提供为 val_data.npy / val_label.pkl。TAO 训练将 `val_loss` 作为此模型的 TensorBoard 验证标量发出；除非自定义评估钩子提供不同的指标，否则使用 `val_loss` 与最小化方向进行 AutoML 选择。独立的评估操作发出 `accuracy`；将此值与所选检查点的评估结果进行比较，但不要将其替换为训练阶段的 `val_loss` 排序 KPI。

## 重要参数

- **dataset.num_classes**: 姿态动作类别的数量。默认 6。
- **model.graph_layout**: 骨架图布局。选项：nvidia、openpose。决定关节连接性。
- **model.graph_strategy**: GCN 的图分区策略。
- **train.optim.lr**: 学习率。默认 0.1 (SGD)。由于图卷积特性，高于视觉模型。
- **model.dropout**: 正则化用 dropout 率。

## 多 GPU / 多节点

**启动方法：** Lightning 管理的（单个 `python` 进程，Lightning 生成工作进程）。

| Spec Key | 描述 | 默认 |
|---|---|---|
| `train.num_gpus` | GPU 数量 | 1 |
| `train.gpu_ids` | GPU 设备索引 | [0] |

- 策略：`auto` (Lightning 自动选择最佳策略)
- 没有 `num_nodes` 或 `distributed_strategy` 配置——仅单节点
- 轻量级模型，单个 GPU 通常足够

## 硬件

至少 1 个 GPU(s)，推荐 1 个 GPU(s)。每个 GPU 至少 8GB+ VRAM。姿态分类非常轻量——骨架数据很小。单个 GPU 足够。

## 错误模式

**图布局不匹配**：确保 `model.graph_layout` 与 .npy 数据文件中的骨架格式匹配。

**标签形状不匹配**：`train_label.pkl` 类索引必须在 [0, num_classes) 范围内。

**缺少标签映射**：训练数据加载器期望 `dataset.label_map` 是一个字典。如果数据集仅提供数字类 ID，则为六个类别的 NVIDIA 示例数据设置一个合成连续映射，例如 `class_0: 0` 到 `class_5: 5`。

**检查点交接**：在 AutoML/训练后，使用检查点解析器选择父结果文件夹下预期的保存 `.pth` 检查点，例如 `model_epoch_000_step_00007.pth`，并将其作为确切的文件传递给 `evaluate.checkpoint`、`export.checkpoint`、`inference.checkpoint` 或 `train.resume_training_checkpoint_path`。`pc_model_latest.pth` 是最新检查点符号链接；仅在用户明确要求最新而不是特定/最佳检查点时使用它。为下游操作保持相同的 `dataset.num_classes`、`dataset.label_map` 和 `model.graph_layout` 覆盖。

**数据集转换来源**：`dataset_convert` 期望 DeepStream BodyPose 应用的原始 JSON 输出。常见的 NVIDIA 示例 S3 文件夹已经转换为 `train_data.npy`、`train_label.pkl`、`val_data.npy`、`val_label.pkl`、`test_data.npy` 和 `test_label.pkl`；当这些文件存在时，跳过转换并从转换后的文件开始。

**操作特定数据集路径**：评估和推理模板还包含训练的 `dataset.train_dataset` 和 `dataset.val_dataset` 块。对于评估，填充 `evaluate.test_dataset.data_path` 和 `evaluate.test_dataset.label_path`。对于推理，填充 `inference.test_dataset.data_path` 并设置 `inference.output_file`；不要在替换文件中的第一个 `data_path` 或 `label_path` 后停止。

**输出文件**：导出需要显式的 `export.onnx_file` 路径。推理必须将 `inference.output_file` 设置为可写入的文件路径；打包的模板默认值是一个空字符串，当前的 PyTorch 推理代码直接打开该值。

## Spec 参数 / 父模型推理

模型特定推理映射属于此 MD 文件，而不是 `config.json`。生成的运行者应在 `create_job()` 之前使用 SDK 帮助程序读取此部分并应用映射。这类似于旧的微服务 `infer_params.py` 流程。

来自 TAO Core `pose_classification.config.json` 的推理映射：

| 操作 | Spec Field | 推理函数 | 含义 |
|---|---|---|---|
| dataset_convert | `dataset_convert.results_dir` | `output_dir` | 当前作业结果目录 |
| evaluate | `encryption_key` | `key` | 加密密钥 |
| evaluate | `evaluate.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| evaluate | `results_dir` | `output_dir` | 当前作业结果目录 |
| export | `encryption_key` | `key` | 加密密钥 |
| export | `export.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| export | `export.onnx_file` | `create_onnx_file` | 输出 ONNX 路径 |
| export | `results_dir` | `output_dir` | 当前作业结果目录 |
| inference | `encryption_key` | `key` | 加密密钥 |
| inference | `inference.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| inference | `inference.output_file` | `create_inference_result_file_pose` | 姿态推理结果文件 |
| inference | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `encryption_key` | `key` | 加密密钥 |
| train | `model.pretrained_model_path` | `ptm_if_no_resume_model` | 当没有恢复检查点时 PTM |
| train | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `train.resume_training_checkpoint_path` | `resume_model` | 从当前作业结果文件夹推断的模型文件 |

对于 `parent_model` 或 `parent_model_folder`，将上游训练/导出/AutoML 子作业 ID 作为 `parent_job_id` 传递。SDK 列出父结果文件夹，过滤检查点工件，并返回选定的模型文件或文件夹。不要将这些映射重新添加到 `config.json`，也不要修补生成的运行者脚本以猜测检查点路径。
