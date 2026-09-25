# 可变形 DETR

> **独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

用于 2D 物体检测的 Deformable DETR。使用可变形注意力机制进行高效的跨尺度特征处理。比 DINO 更轻，但精度具有竞争力。

使用预训练权重。设置 `model.pretrained_backbone_path` 用于仅加载主干，或设置 `train.pretrained_model_path` 用于完整模型初始化。

支持的父模型操作包括 `train`、`evaluate`、`inference`、`export` 和 `quantize`。PyT 模型容器不支持此网络的本地 `gen_trt_engine` 子任务。`references/skill_info.yaml` 中声明的 `gen_trt_engine` 操作必须使用 TAO Deploy 容器运行。部署规范模板位于此技能的 `references/` 文件夹中，以 `spec_template_deploy_*.yaml` 为前缀。

## 数据类模式

生成的 TAO Core 模式打包在 `schemas/<action>.schema.json` 中，`schemas/manifest.json` 列出可用操作。每个生成的模式也从模式的顶层 `default` 字段发出 `references/spec_template_<action>.yaml`。AutoML 启用声明在 `references/skill_info.yaml` 中的模型层通过 `automl_enabled`。运行 AutoML 需要操作存在 `schemas/<action>.schema.json` 和 `references/spec_template_<action>.yaml` 并可以解析。使用打包的选定操作模式用于 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖项和常用参数。不要期望在运行时 `~/tao-core`；维护人员在打包技能库之前重新生成模式/模板。

## 训练操作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，读取 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将短语如 "关闭 AutoML"、"禁用 AutoML"、"无 HPO" 或 "纯训练" 视为仅对此运行 `automl_policy: off`。当 `automl_policy: on`、`automl_enabled: true`，并且 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 都被打包时，默认通过 `tao-skill-bank:tao-run-automl` 将训练操作路由到此模型的 `skill_dir`。保留工作流/应用程序覆盖的数据集、规范、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时使用直接模型训练；在缺失模式的案例中，报告此模型启用 AutoML 但不可运行，直到生成模式。

非训练操作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每运行的 `automl_policy` 覆盖不会更改模型元数据。

## 训练要求

- **数据集类型：** object_detection
- **格式：** coco, coco_raw
- **AutoML 指标契约：** 对于基于评估的选择，使用 `test_mAP50` 并使用最大化方向。仅用于训练日志式 AutoML 工作流的 `val_mAP50`。
- **训练监控指标：** `val_mAP50` 用于 AP50；`val_mAP` 用于 COCO/论文式基准比较。
- **评估操作指标：** `test_mAP50` 用于 AP50；`test_mAP` 用于 COCO/论文式基准比较。通过评估操作比较的 AutoML 试验必须使用相应的 `test_*` KPI，而不是在评估器输出中寻找 `val_*` KPI。

### 每个操作的 数据集 要求

| 操作 | Spec Key | 来源 | 文件 | 列表？ |
|---|---|---|---|---|
| evaluate | dataset.test_data_sources.image_dir | eval_dataset | images.tar.gz | 否 |
| evaluate | dataset.test_data_sources.json_file | eval_dataset | annotations.json | 否 |
| export | dataset.train_data_sources | train_datasets | image_dir: images.tar.gz, json_file: annotations.json | 是 |
| export | dataset.val_data_sources | train_datasets | image_dir: images.tar.gz, json_file: annotations.json | 是 |
| inference | dataset.infer_data_sources.image_dir | inference_dataset | images.tar.gz | 是 |
| inference | dataset.infer_data_sources.classmap | inference_dataset | label_map.txt | 否 |
| quantize | dataset.train_data_sources | train_datasets | image_dir: images.tar.gz, json_file: annotations.json | 是 |
| quantize | dataset.val_data_sources | train_datasets | image_dir: images.tar.gz, json_file: annotations.json | 是 |
| quantize | dataset.quant_calibration_data_sources | train_datasets | image_dir: images.tar.gz, json_file: annotations.json | 否 |
| train | dataset.train_data_sources | train_datasets | image_dir: images.tar.gz, json_file: annotations.json | 是 |
| train | dataset.val_data_sources | train_datasets | image_dir: images.tar.gz, json_file: annotations.json | 是 |

### 典型 Spec 覆盖

数据源覆盖对每个操作都是**强制性的**——代理必须根据上表中的每个操作数据集要求构建数据源路径，并将其包含在 `spec_overrides` 中。

```python
S3_TRAIN = "s3://bucket/data/train"
S3_EVAL = "s3://bucket/data/eval"
```

**train (强制数据源):**
```python
{
    "train.num_epochs": 10,
    "train.checkpoint_interval": 10,
    "train.validation_interval": 10,
    "train.num_gpus": 1,
    "train.gpu_ids": [0],
    "dataset.num_classes": "<object classes> + 1",
    "dataset.eval_class_ids": [1, 2, "..."],
    "dataset.train_data_sources": [{"image_dir": f"{S3_TRAIN}/images.tar.gz", "json_file": f"{S3_TRAIN}/annotations.json"}],
    "dataset.val_data_sources": [{"image_dir": f"{S3_TRAIN}/images.tar.gz", "json_file": f"{S3_TRAIN}/annotations.json"}],
}
```

**evaluate (强制数据源):**
```python
{
    "dataset.num_classes": "<object classes> + 1",
    "dataset.eval_class_ids": [1, 2, "..."],
    "dataset.test_data_sources.image_dir": f"{S3_EVAL}/images.tar.gz",
    "dataset.test_data_sources.json_file": f"{S3_EVAL}/annotations.json",
}
```

如果训练或 AutoML 运行更改了影响架构的字段，如 `model.enc_layers`、`model.dec_layers`、`model.num_queries` 或 `model.num_select`，请使用选定的检查点将相同的值传递到 evaluate、export、inference 和 deploy 操作。除了上述字段外，当它们被更改时，还传递 `model.num_feature_levels`、`model.dim_feedforward`、输入图像维度和数据集类元数据。将检查点加载到默认架构可能会因张量形状不匹配而失败，尤其是在烟雾测试运行为速度而缩小 Transformer 时。

**export (强制数据源):**
```python
{
    "dataset.num_classes": "<object classes> + 1",
    "dataset.eval_class_ids": [1, 2, "..."],
    "dataset.train_data_sources": [{"image_dir": f"{S3_TRAIN}/images.tar.gz", "json_file": f"{S3_TRAIN}/annotations.json"}],
    "dataset.val_data_sources": [{"image_dir": f"{S3_TRAIN}/images.tar.gz", "json_file": f"{S3_TRAIN}/annotations.json"}],
}
```

**TensorRT 引擎生成:**

在 `export` 后使用部署规范模板。不要从父 PyT 模型容器调用 `deformable_detr gen_trt_engine`；该 CLI 广告 `convert`、`evaluate`、`export`、`inference`、`quantize`、`train` 和 `default_specs`，但没有 `gen_trt_engine`。模型操作元数据选择 TAO Deploy 容器进行引擎生成。

部署引擎生成需要导出的 ONNX 文件作为输入，并在 `gen_trt_engine.trt_engine` 创建引擎。

```python
{
    "gen_trt_engine.tensorrt.data_type": "FP16",
    "dataset.num_classes": "<object classes> + 1",
    "gen_trt_engine.tensorrt.calibration.cal_image_dir": [f"{S3_TRAIN}/images.tar.gz"],
}
```

**inference (强制数据源):**
```python
{
    "dataset.num_classes": "<object classes> + 1",
    "dataset.infer_data_sources.image_dir": [f"{S3_EVAL}/images.tar.gz"],
    "dataset.infer_data_sources.classmap": f"{S3_EVAL}/label_map.txt",
}
```

**quantize (强制数据源):**
```python
{
    "dataset.train_data_sources": [{"image_dir": f"{S3_TRAIN}/images.tar.gz", "json_file": f"{S3_TRAIN}/annotations.json"}],
    "dataset.val_data_sources": [{"image_dir": f"{S3_TRAIN}/images.tar.gz", "json_file": f"{S3_TRAIN}/annotations.json"}],
    "dataset.quant_calibration_data_sources": {"image_dir": f"{S3_TRAIN}/images.tar.gz", "json_file": f"{S3_TRAIN}/annotations.json"},
}
```
## Eval 数据集

可选。如果提供，将在每个检查点间隔计算验证 mAP。

## 检查点处理

训练使用模式 `model_epoch_<epoch>_step_<step>.pth` 发射 epoch 和 step 检查点，以及 `dd_model_latest.pth` 符号链接。对于依赖操作，使用模型特定的或 SDK 提供的检查点解析器来选择预期的工件。评估、推理、导出和量化应接收选定的精确检查点路径，而不是 `dd_model_latest.pth` 符号链接，除非用户明确要求最新。恢复/重新训练应将 `train.resume_training_checkpoint_path` 设置为正在恢复的精确检查点。

## 重要参数

- **dataset.num_classes**: 物体类别数量加上背景类。默认 91 (COCO)。必须与注释匹配。
- **dataset.eval_class_ids**: 要包含在 COCO 指标中的前景类别 ID。在自定义数据集中将此设置为每个对象类别 ID；模板默认仅评估类别 ID 1。
- **model.backbone**: 默认 resnet_50。支持：resnet_50、gcvit_tiny、gcvit_small、gcvit_base、gcvit_large、gcvit_large_384（比 DINO 限制更多）。
- **train.optim.lr**: 学习率。默认 2e-4 (AdamW)。lr_backbone 是 2e-5。
- **train.optim.lr_steps**: 多步 LR 调度。默认 [40]。对于短运行，设置为约总 epoch 的 80%。
- **model.num_queries**: 物体查询数量。默认 300。有效范围 100-900。
- **model.dropout_ratio**: Transformer 层中的 Dropout。默认 0.3 (高于 DINO 的 0.0)。对于大型数据集减少，对于小型数据集增加。
- **model.dim_feedforward**: FFN 隐藏维度。默认 1024 (与 DINO 的 2048 相比)。增加可以提高容量，但会消耗内存。

## 多 GPU / 多节点

**启动方法：** Lightning 管理的（单个 `python` 进程，Lightning 生成工作进程）。

| Spec Key | 描述 | 默认 |
|---|---|---|
| `train.num_gpus` | GPU 数量 | 1 |
| `train.gpu_ids` | GPU 设备索引 | [0] |
| `train.num_nodes` | 节点数量 | 1 |
| `train.distributed_strategy` | `ddp` 或 `fsdp` | `ddp` |

与 DINO 相同的 DDP/FSDP 行为。多节点需要 `WORLD_SIZE`、`NODE_RANK`、`MASTER_ADDR`、`MASTER_PORT` 环境变量由协调器设置。

当增加 `train.num_gpus` 时，还设置 `train.gpu_ids` 为相同的可见设备范围。例如，8-GPU 单节点 Slurm 运行必须包括 `"train.num_gpus": 8` 和 `"train.gpu_ids": [0, 1, 2, 3, 4, 5, 6, 7]`。

## 导出 / TRT 默认值

- 导出输入：640x640，opset 17
- TRT 数据类型：FP32、FP16、INT8
- TRT 工作空间：1024 MB
- TRT 最大 batch_size：1

## 硬件

最小 1 GPU(s)，推荐 4 GPU(s)。每个 GPU 16GB+ (V100 或 A100) VRAM。比 DINO 轻一些，因为 FFN 更小。batch_size=4 可以适应大多数 16GB+ GPU。

## 错误模式

**CUDA 内存不足**：减少 batch_size (4 -> 2 -> 1)。

**num_select 必须小于 num_queries * num_classes**：与 DINO 相同的约束。

**return_interm_indices 长度必须匹配 num_feature_levels**：默认 [1,2,3,4] 与 num_feature_levels=4。

**数据集大小小于总 batch_size**：减少 batch_size 或 num_gpus。

**AutoML 指标提取**：Deformable DETR 在结构化训练状态中发出 `val_mAP` 和 `val_mAP50`，而独立的 evaluate 操作发出 `test_mAP` 和 `test_mAP50`。对于 COCO/论文式训练仅比较，优化 `val_mAP`；对于显式 AP50 训练仅工作流，优化 `val_mAP50`。当 AutoML 使用 evaluate 操作为每个推荐评分时，使用相应的 `test_mAP` 或 `test_mAP50` KPI。优先考虑 `results_dir/train/status.json` 或 AutoML 结果状态，然后再解析原始日志。不要优化默认检测模型调用的 `val_loss`。

## Spec Param / 父模型推理

特定于模型的推理映射属于此 MD 文件，而不是 `config.json`。生成的运行者应在此部分读取并使用 SDK 帮助程序在 `create_job()` 之前应用映射。这类似于旧的微服务 `infer_params.py` 流程。

来自 TAO Core `deformable_detr.config.json` 的推理映射：

| 操作 | Spec Field | 推理函数 | 含义 |
|---|---|---|---|
| evaluate | `encryption_key` | `key` | 加密密钥 |
| evaluate | `evaluate.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| evaluate | `evaluate.trt_engine` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| evaluate | `results_dir` | `output_dir` | 当前作业结果目录 |
| export | `encryption_key` | `key` | 加密密钥 |
| export | `export.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| export | `export.onnx_file` | `create_onnx_file` | 输出 ONNX 路径 |
| export | `results_dir` | `output_dir` | 当前作业结果目录 |
| inference | `encryption_key` | `key` | 加密密钥 |
| inference | `inference.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| inference | `inference.trt_engine` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| inference | `results_dir` | `output_dir` | 当前作业结果目录 |
| quantize | `encryption_key` | `key` | 加密密钥 |
| quantize | `quantize.model_path` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| quantize | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `encryption_key` | `key` | 加密密钥 |
| train | `model.pretrained_backbone_path` | `ptm_if_no_resume_model` | 当没有恢复检查点时 PTM |
| train | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `train.pretrained_model_path` | `ptm_if_no_resume_model` | 当没有恢复检查点时完整模型 PTM |
| train | `train.resume_training_checkpoint_path` | `resume_model` | 从当前作业结果文件夹推断的模型文件 |

对于 `parent_model` 或 `parent_model_folder`，将上游训练/导出/AutoML 子作业 ID 作为 `parent_job_id` 传递。SDK 列出父结果文件夹，过滤检查点工件，并返回选定的模型文件或文件夹。不要将这些映射重新添加到 `config.json`，也不要修补生成的运行者脚本以猜测检查点路径。

## 部署

- [tao-deploy-deformable-detr](references/tao-deploy-deformable-detr.md)
