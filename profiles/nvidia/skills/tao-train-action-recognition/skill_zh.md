# 动作识别

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

从视频序列中进行动作识别。支持 RGB、光流和联合（多流）输入类型，用于对视频片段中的时序动作进行分类。

设置 `model.pretrained_model_path` 以使用预训练的骨干权重。

## 快速入门（docker run）

原生 Docker 启动 — 无需 TAO SDK 和主机上的 Python。当它提供更严格的环境特定命令（非根 UID 映射、缓存重定向、远程守护进程）时，使用本地 Docker 平台技能。

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
  action_recognition train -e /specs/train.yaml
```

评估：

```bash
docker run "${DOCKER_COMMON[@]}" "$TAO_PYT_IMAGE" \
  action_recognition evaluate -e /specs/evaluate.yaml
```

推理：

```bash
docker run "${DOCKER_COMMON[@]}" "$TAO_PYT_IMAGE" \
  action_recognition inference -e /specs/inference.yaml
```

导出：

```bash
docker run "${DOCKER_COMMON[@]}" "$TAO_PYT_IMAGE" \
  action_recognition export -e /specs/export.yaml
```

每个动作都使用 `-e` 带其 spec；`results_dir` 在 spec 中设置或在命令行中覆盖。挂载 spec 引用的任何预训练权重目录，并确保容器内路径在所有动作中保持一致。

## 数据类模式

生成的 TAO Core 模式打包在 `schemas/<action>.schema.json` 中，`schemas/manifest.json` 列出可用动作。每个生成的模式还从模式顶层 `default` 字段发出 `references/spec_template_<action>.yaml`。AutoML 启用声明在 `references/skill_info.yaml` 中的模型层通过 `automl_enabled` 声明。一个动作的可运行 AutoML 需要 `schemas/<action>.schema.json` 和 `references/spec_template_<action>.yaml` 存在并可以解析。使用打包的选定动作模式用于 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖关系和常用参数。不要期望运行时 `~/tao-core`；维护者在打包技能库之前重新生成模式/模板。

## 训练动作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，读取 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将短语如 "关闭 AutoML"、"禁用 AutoML"、"无 HPO" 或 "纯训练" 视为 `automl_policy: off` 仅对此运行。当 `automl_policy: on`、`automl_enabled: true`，并且 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 都被打包时，默认通过此模型的 `skill_dir` 将训练动作路由到 `tao-skill-bank:tao-run-automl`。保留流程/应用程序覆盖的数据集、spec、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时使用直接模型训练；在缺失模式的情况下，报告此模型启用 AutoML 但不可运行，直到生成模式。

非训练动作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每次运行的 `automl_policy` 覆盖不会改变模型元数据。

## 训练要求

- **数据集类型：** action_recognition
- **格式：** 默认
- **训练监控指标：** `val_loss`、`val_acc`
- **评估任务指标：** `accuracy`、`m_accuracy`
- **AutoML 指标契约：** 对于所需的评估支持基线和最终比较，使用 `accuracy` 并设置最大化方向，并通过 `eval_fn` 对每个推荐运行 `evaluate`。`val_loss` 仅适用于明确接受的训练代理运行，因为 `evaluate` 不发出它。没有起始检查点的草稿运行需要先执行最小的默认训练作业，然后评估其确切的 epoch/step 检查点以确定基线。

### 每个动作的数据集要求

| 动作 | Spec Key | 来源 | 文件 | 列表？ |
|---|---|---|---|---|
| evaluate | evaluate.test_dataset_dir | train_datasets | test/ 从 test.tar.gz 提取 | 否 |
| inference | inference.inference_dataset_dir | train_datasets | test/smile/ 从 test/smile.tar.gz 提取 | 否 |
| train | dataset.train_dataset_dir | train_datasets | train/ 从 train.tar.gz 提取 | 否 |
| train | dataset.val_dataset_dir | train_datasets | test/ 从 test.tar.gz 提取 | 否 |

### 典型 Spec 覆盖

数据源覆盖对每个动作都是**强制性的** — 代理必须根据上表中的 Per-Action Dataset Requirements 构造数据源路径并将其包含在 `spec_overrides` 中。

```python
LOCAL_DATA = "/workspace/data/extracted"
```

如果源数据集作为 TAO 示例存档 `train.tar.gz`、`test.tar.gz` 或 `test/smile.tar.gz` 提供，请在启动 TAO 容器之前下载并提取它们。动作识别入口点期望目录路径，当这些 spec 键指向 `.tar.gz` 文件时，会失败并报 `NotADirectoryError`。

**train (强制数据源)：**
```python
{
    "train.num_epochs": 30,
    "train.checkpoint_interval": 10,
    "train.validation_interval": 10,
    "train.num_gpus": 1,
    "dataset.label_map": {
        "catch": 0,
        "smile": 1
    },
    "dataset.batch_size": 2,
    "dataset.train_dataset_dir": f"{LOCAL_DATA}/train",
    "dataset.val_dataset_dir": f"{LOCAL_DATA}/test",
}
```

**evaluate (强制数据源)：**
```python
{
    "dataset.label_map": {
        "catch": 0,
        "smile": 1
    },
    "evaluate.test_dataset_dir": f"{LOCAL_DATA}/test",
}
```

**inference (强制数据源)：**
```python
{
    "dataset.label_map": {
        "catch": 0,
        "smile": 1
    },
    "inference.inference_dataset_dir": f"{LOCAL_DATA}/smile_infer/smile",
}
```

**export (强制检查点 + 输出路径)：**
```python
{
    "export.checkpoint": "<选定的训练检查点>",
    "export.onnx_file": "<results_dir>/action_recognition.onnx",
}
```

对于直接本地 docker 链接而无需 SDK 解析，选择训练产生的具体检查点，例如 `model_epoch_000_step_00005.pth`，并将该确切文件传递给 `evaluate`、`inference` 和 `export`。除非用户明确请求最新检查点行为，否则不要使用 `ar_model_latest.pth` 符号链接。对于恢复训练，将 `train.resume_training_checkpoint_path` 设置为正在恢复的确切 epoch/step 检查点。

## 评估数据集

可选。测试数据集可以分布为与训练分离的 `test.tar.gz`；提取它并将 spec 指向提取的 `test/` 目录。TAO 训练为打包的示例数据发出 `val_loss` 和 `val_acc`，而评估动作发出 `accuracy` 和 `m_accuracy`。使用 `accuracy` 并设置最大化方向进行正常的评估支持 AutoML 工作流。仅在用户明确接受无需所需影响基线的纯训练代理时，才使用 `val_loss` 并设置最小化方向。

## 重要参数

- **model.model_type**: 输入类型：rgb、of（光流）或 joint（多流）。
- **model.backbone**: 默认 resnet_18。用作空间特征提取器。
- **dataset.label_map**: 映射类名到索引的字典。
- **model.rgb_seq_length**: 每个片段的 RGB 输入帧数。
- **model.of_seq_length**: 光流输入的帧数。
- **train.optim.lr**: 学习率。默认 5e-4。

## 多 GPU / 多节点

**启动方法：** Lightning 管理的（单个 `python` 进程，Lightning 生成工作进程）。

| Spec Key | 描述 | 默认 |
|---|---|---|
| `train.num_gpus` | GPU 数量 | 1 |
| `train.gpu_ids` | GPU 设备索引 | [0] |

- 策略：`auto`（Lightning 自动选择最佳策略）
- 没有 `num_nodes` 或 `distributed_strategy` 配置 — 单节点导向

## 硬件

最少 1 个 GPU，推荐 2 个 GPU。每个 GPU 需要 16GB+ VRAM。内存取决于序列长度和输入分辨率。batch_size=2 对视频数据较为保守。

## 错误模式

**序列长度不匹配**：确保视频片段有足够的帧以匹配配置的 rgb_seq_length 或 of_seq_length。

**评估/推理缺少标签映射**：下游动作在加载检查点之前会重建 ActionRecognitionModel，因此它们需要与训练时相同的 `dataset.label_map`。在每次评估或推理 spec 中包含它；否则模型构建在检查点验证之前会失败。

## Spec 参数 / 父模型推理

模型特定推理映射属于此 MD 文件，而不是在 `config.json` 中。生成的运行者应读取本节并使用 SDK 辅助程序在 `create_job()` 之前应用这些映射。这类似于旧的微服务 `infer_params.py` 流程。

来自 TAO Core `action_recognition.config.json` 的推理映射：

| 动作 | Spec Field | 推理函数 | 含义 |
|---|---|---|---|
| evaluate | `encryption_key` | `key` | 加密密钥 |
| evaluate | `evaluate.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| evaluate | `results_dir` | `output_dir` | 当前作业结果目录 |
| export | `encryption_key` | `key` | 加密密钥 |
| export | `export.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| export | `export.onnx_file` | `create_onnx_file` | 输出 ONNX 路径 |
| export | `results_dir` | `output_dir` | 当前作业结果目录 |
| inference | `encryption_key` | `key` | 加密密钥 |
| inference | `inference.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| inference | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `encryption_key` | `key` | 加密密钥 |
| train | `model.of_pretrained_model_path` | `ptm_if_no_resume_model` | 当没有恢复检查点时 PTM |
| train | `model.rgb_pretrained_model_path` | `ptm_if_no_resume_model` | 当没有恢复检查点时 PTM |
| train | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `train.resume_training_checkpoint_path` | `resume_model` | 从当前作业结果文件夹推断的模型文件 |

对于 `parent_model` 或 `parent_model_folder`，将上游训练/导出/AutoML 子作业 ID 作为 `parent_job_id` 传递。SDK 列出父结果文件夹，过滤检查点工件，并返回选定的模型文件或文件夹。不要将这些映射重新添加到 `config.json`，也不要修补生成的运行者脚本以猜测检查点路径。
