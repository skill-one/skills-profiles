# OCDNet

> **独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

OCDNet 用于场景文本检测。它使用可微分的二值化方法检测自然图像中的任意方向文本区域。

设置 `model.pretrained_model_path` 以使用预训练权重。

对于 TAO Deploy TensorRT 操作 (`gen_trt_engine`、TensorRT `evaluate` 和 TensorRT `inference`)，请先阅读 `references/tao-deploy-ocdnet.md`。部署规范模板位于此技能的 `references/` 文件夹中，以 `spec_template_deploy_*.yaml` 为前缀。

PyT OCDNet CLI 支持 `train`、`evaluate`、`export`、`inference`、`prune`、`quantize` 和 `default_specs`。它不暴露 PyT 端的 `retrain` 或 `gen_trt_engine` 子命令。模型技能通过运行 `ocdnet train` 并设置 `model.load_pruned_graph: true` 和 `model.pruned_graph_path` 来暴露 `retrain`。从 epoch 检查点恢复使用 `ocdnet train` 加上 `train.resume_training_checkpoint_path`。TensorRT 引擎生成由部署工作流负责。

## 数据类模式

生成的 TAO Core 模式打包在 `schemas/<action>.schema.json` 中，`schemas/manifest.json` 列出可用操作。每个生成的模式也从模式的顶层 `default` 字段发出 `references/spec_template_<action>.yaml`。AutoML 启用声明在模型层的 `references/skill_info.yaml` 中通过 `automl_enabled` 进行。要启用可运行的 AutoML，需要 `schemas/<action>.schema.json` 和 `references/spec_template_<action>.yaml` 存在并可以解析。使用打包的选定操作模式用于 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖关系和常用参数。不要期望 `~/tao-core` 在运行时；维护者在打包技能库之前会重新生成模式/模板。

## 训练操作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，请阅读 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将类似于 "关闭 AutoML"、"禁用 AutoML"、"无 HPO" 或 "纯训练" 的短语视为仅对此运行 `automl_policy: off`。当 `automl_policy: on`、`automl_enabled: true`，并且 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 都被打包时，默认通过 `tao-skill-bank:tao-run-automl` 路由训练操作，并使用此模型的 `skill_dir`。保留工作流/应用程序覆盖的数据集、规范、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时使用直接模型训练；在缺失模式的案例中，在生成模式之前报告此模型启用 AutoML 但不可运行。

对于 AutoML 训练，使用 `train_loss_epoch` 或 `train_loss` 作为优化指标，`direction=minimize`。Lightning 进度日志发出 `train_loss_epoch`，TAO `status.json` 在 `train_loss` 下记录相同的最终值。对于单 epoch 本地 AutoML 烟雾运行，设置 `train.lr_scheduler.args.warmup_epoch: 0`；将预热等于 epoch 预算会导致训练器在可以报告指标之前失败。非训练操作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每次运行的 `automl_policy` 覆盖不会更改模型元数据。

## 训练要求

- **数据集类型：** ocdnet
- **格式：** 默认
- **AutoML 训练指标：** `train_loss`（状态记录器的最终 `train_loss_epoch` 值），`direction=minimize`
- **AutoML 指标契约：** 使用训练期间发出的 `train_loss` 并将其最小化。将 `train_loss_epoch` 仅视为日志回退别名；仅使用独立的 `hmean` 来验证选定的检查点。
- **独立评估指标：** `hmean`，`direction=maximize`

### 每个操作的 数据集 要求

| 操作 | Spec Key | 来源 | 运行时值 | 列表？ |
|---|---|---|---|---|
| evaluate | dataset.validate_dataset.data_path | eval_dataset | 提取的验证分割文件夹，包含 `img/` 和 `gt/` | 是 |
| inference | inference.input_folder | inference_dataset 或 eval_dataset | 提取的图像文件夹 | 否 |
| prune | dataset.validate_dataset.data_path | eval_dataset | 提取的验证分割文件夹，包含 `img/` 和 `gt/` | 是 |
| quantize | dataset.train_dataset.data_path | train_datasets | 提取的训练分割文件夹，包含 `img/` 和 `gt/` | 是 |
| quantize | dataset.validate_dataset.data_path | eval_dataset | 提取的验证分割文件夹，包含 `img/` 和 `gt/` | 是 |
| quantize | dataset.quant_calibration_dataset.images_dir | train_datasets 或 calibration_dataset | 提取的校准图像文件夹 | 否 |
| train | dataset.train_dataset.data_path | train_datasets | 提取的训练分割文件夹，包含 `img/` 和 `gt/` | 是 |
| train | dataset.validate_dataset.data_path | eval_dataset | 提取的验证分割文件夹，包含 `img/` 和 `gt/` | 是 |
| retrain | dataset.train_dataset.data_path | train_datasets | 提取的训练分割文件夹，包含 `img/` 和 `gt/` | 是 |
| retrain | dataset.validate_dataset.data_path | eval_dataset | 提取的验证分割文件夹，包含 `img/` 和 `gt/` | 是 |

### 典型 Spec 覆盖

数据源覆盖对每个操作都是**强制性的**——代理必须根据上表中的“每个操作的 数据集 要求”构建数据源路径，并将它们包含在 `spec_overrides` 中。OCDNet 在运行时不解压数据集存档。如果来源是 `train.tar.gz`、`test.tar.gz` 或 `img.tar.gz`，请先解压它，然后将分割文件夹或图像文件夹传递到规范中。分割文件夹必须包含 `img/` 和 `gt/`；或者，传递一个 UTF-8 datalist 文本文件，其行映射图像路径到标签路径。

```python
TRAIN_ROOT = "/path/to/extracted/train"
EVAL_ROOT = "/path/to/extracted/test"
INFER_IMG_DIR = "/path/to/extracted/test/img"
CALIB_IMG_DIR = "/path/to/extracted/train/img"
```

**train (强制数据源):**
```python
{
    "train.num_epochs": 30,
    "train.checkpoint_interval": 10,
    "train.validation_interval": 10,
    "train.num_gpus": 1,
    "dataset.train_dataset.loader.batch_size": 16,
    "dataset.train_dataset.data_path": [TRAIN_ROOT],
    "dataset.validate_dataset.data_path": [EVAL_ROOT],
}
```

**evaluate (强制数据源):**
```python
{
    "evaluate.checkpoint": "<选定的 train/AutoML 检查点>",
    "dataset.validate_dataset.data_path": [EVAL_ROOT],
}
```

**inference (强制数据源):**
```python
{
    "inference.checkpoint": "<选定的 train/AutoML 检查点>",
    "inference.input_folder": INFER_IMG_DIR,
}
```

**prune (强制数据源):**
```python
{
    "prune.checkpoint": "<选定的 train/AutoML 检查点>",
    "dataset.validate_dataset.data_path": [EVAL_ROOT],
}
```

**quantize (强制数据源):**
```python
{
    "quantize.model_path": "<选定的 train 检查点或导出的 ONNX>",
    "dataset.train_dataset.data_path": [TRAIN_ROOT],
    "dataset.validate_dataset.data_path": [EVAL_ROOT],
    "dataset.quant_calibration_dataset.images_dir": CALIB_IMG_DIR,
}
```

**恢复训练 (强制数据源):**
```python
{
    "train.resume_training_checkpoint_path": "<精确的 model_epoch 检查点>",
    "dataset.train_dataset.data_path": [TRAIN_ROOT],
    "dataset.validate_dataset.data_path": [EVAL_ROOT],
}
```

**从 prune 输出重新训练 (强制数据源):**
```python
{
    "model.load_pruned_graph": True,
    "model.pruned_graph_path": "<选定的 prune 输出>",
    "dataset.train_dataset.data_path": [TRAIN_ROOT],
    "dataset.validate_dataset.data_path": [EVAL_ROOT],
}
```

**default_specs:**
```python
{
    "results_dir": "<可写的输出目录>",
}
```
## Eval 数据集

可选。作为单独的 tarball 提供的测试数据集。

## 重要参数

- **model.backbone**: 默认 deformable_resnet18。可变形卷积提高了不规则文本区域的检测。
- **train.optimizer.args.lr**: 学习率。默认 0.001 (Adam)。
- **postprocess.thresh**: 文本区域提取的二值化阈值。
- **postprocess.box_thresh**: 检测过滤的框置信度阈值。

## 多 GPU / 多节点

**启动方法：** Lightning 管理的（单个 `python` 进程，Lightning 生成工作进程）。

| Spec Key | 描述 | 默认值 |
|----------|-------------|---------|
| `train.num_gpus` | GPU 数量 | 1 |
| `train.gpu_ids` | GPU 设备索引 | [0] |
| `train.distributed_strategy` | `ddp`、`fsdp` 或 `deepspeed_stage_3_offload` | `ddp` |

- `ddp` 带激活检查点：`find_unused_parameters=False`
- `ddp` 不带：`find_unused_parameters=True`
- `fsdp` 强制 FP16
- **`deepspeed_stage_3_offload`** 是 OCDNet 独有的支持（强制 FP16）
- FAN 主干自动启用 `sync_batchnorm`

## 硬件

至少 1 个 GPU(s)，推荐 1 个 GPU(s)。每个 GPU 8GB+ VRAM。OCDNet 轻量级。单个 GPU 对大多数数据集足够。

## 错误模式

**检测率低：** 调整 `postprocess.thresh` 和 `box_thresh`。默认阈值可能对某些数据集过于激进。

**单 epoch 烟雾训练与默认调度器：** `train.num_epochs` 必须不等于 `train.lr_scheduler.args.warmup_epoch`。对于单 epoch 验证，设置 `warmup_epoch: 0`；对于正常启动运行，保持 `num_epochs > warmup_epoch`。

**作为数据集路径传递的存档：** `dataset.*.data_path` 不是 OCDNet 的存档路径。直接传递 `train.tar.gz` 或 `test.tar.gz` 会导致 dataloader 将 gzip 作为 UTF-8 datalist 打开。解压存档并将包含 `img/` 和 `gt/` 的分割文件夹传递过去，或者传递一个真实的 UTF-8 datalist 文件。

**量化检查点类型：** 不要将 `model_best.pth` 传递到 PyTorch 量化路径。一些较旧的 PyT 运行时在 `model_best.pth` 中没有完整的 Lightning 检查点元数据。默认的 `torchao` 量化路径应使用预期的完整 `model_epoch_<epoch>_step_<step>.pth` 检查点并写入 `quantized_model_torchao.pth`。

**默认规范输出目录：** `ocdnet default_specs` 需要可写的 `results_dir` 覆盖，例如 `results_dir=/workspace/run/results/default_specs`。

## 检查点传递

OCDNet 训练写入 `model_best.pth` 加上完整的 Lightning epoch 检查点，例如 `model_epoch_001_step_00046.pth`；它还可能写入 `ocd_model_latest.pth` 作为最新符号链接。当用户请求最佳检查点时，使用 `model_best.pth` 进行 `evaluate.checkpoint`、`inference.checkpoint`、`export.checkpoint` 和 `prune.checkpoint`。使用特定的 `model_epoch_<epoch>_step_<step>.pth` 进行 `train.resume_training_checkpoint_path` 和任何需要完整 Lightning 检查点的操作。Prune 写入 `pruned_<ch_sparsity>.pth` 等工件；当从 prune 图形重新训练时，使用精确的 pruned `.pth` 工件作为 `model.pruned_graph_path`。仅在用户明确请求最新时使用最新检查点。

如果使用 PyTorch 后端重试量化，请解析与预期最佳 epoch 或请求 epoch 对应的完整 `model_epoch_<epoch>_step_<step>.pth`；不要将 `model_best.pth` 传递到 PyTorch 量化路径。如果使用 `modelopt.onnx` 重试量化，请将导出的 ONNX 传递为 `quantize.model_path` 并验证运行时图像实际包含 `modelopt.onnx.quantization`。

## Spec 参数 / 父模型推理

特定于模型的推理映射属于此 MD 文件，而不是 `config.json`。生成的运行者应读取本节并使用 SDK 帮助程序在 `create_job()` 之前应用这些映射。这类似于旧的微服务 `infer_params.py` 流程。

模型传递映射：

| 操作 | Spec Field | 推理函数 | 含义 |
|---|---|---|---|
| evaluate | `evaluate.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| evaluate | `results_dir` | `output_dir` | 当前作业结果目录 |
| export | `export.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| export | `export.onnx_file` | `create_onnx_file` | 输出 ONNX 路径 |
| export | `results_dir` | `output_dir` | 当前作业结果目录 |
| inference | `inference.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| inference | `results_dir` | `output_dir` | 当前作业结果目录 |
| prune | `prune.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| prune | `results_dir` | `output_dir` | 当前作业结果目录 |
| quantize | `quantize.model_path` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| quantize | `results_dir` | `output_dir` | 当前作业结果目录 |
| 重新训练从 prune | `model.pruned_graph_path` | `parent_model` | 从父 prune 结果文件夹推断的精确 pruned 模型文件 |
| 重新训练从 prune | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `model.pretrained_model_path` | `ptm_if_no_resume_model` | 当没有恢复检查点时使用 PTM |
| train | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `train.resume_training_checkpoint_path` | `resume_model` | 从当前作业结果文件夹推断的模型文件 |

对于 `parent_model` 或 `parent_model_folder`，请将上游训练/导出/AutoML 子作业 ID 作为 `parent_job_id` 传递。SDK 列出父结果文件夹，过滤检查点工件，并返回选定的模型文件或文件夹。不要将这些映射重新添加到 `config.json`，也不要修补生成的运行者脚本以猜测检查点路径。

## 部署

- [tao-deploy-ocdnet](references/tao-deploy-ocdnet.md)
