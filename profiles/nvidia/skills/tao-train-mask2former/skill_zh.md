# Mask2Former

> **独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

Mask2Former 用于通用图像分割（全景、实例和语义）。基于 Transformer，使用掩码注意力机制以获得高质量的分割结果。

设置 `model.backbone.pretrained_weights` 以使用 Swin 主干权重。

对于 TAO Deploy TensorRT 操作 (`gen_trt_engine`, TensorRT `evaluate` 和 TensorRT `inference`)，请先阅读 `references/tao-deploy-mask2former.md`。部署规范模板位于此技能的 `references/` 文件夹中，以 `spec_template_deploy_*.yaml` 为前缀。

## 数据类模式

生成的 TAO Core 模式打包在 `schemas/<action>.schema.json` 中，`schemas/manifest.json` 列出可用操作。每个生成的模式还会从模式顶层 `default` 字段发出 `references/spec_template_<action>.yaml`。AutoML 启用声明在 `references/skill_info.yaml` 中的模型层通过 `automl_enabled`。运行 AutoML 需要存在并解析 `schemas/<action>.schema.json` 和 `references/spec_template_<action>.yaml`。使用打包的选定操作模式进行 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖项和常用参数。不要期望 `~/tao-core` 在运行时；维护人员在打包技能库之前会重新生成模式/模板。

## 训练操作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，请阅读 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on`，并在新的启动提示中仅暴露 `on` / `off`。将短语“关闭 AutoML”、“禁用 AutoML”、“无 HPO”或“纯训练”视为仅对此运行 `automl_policy: off`。当 `automl_policy: on`、`automl_enabled: true`，并且打包了 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 时，默认通过 `tao-skill-bank:tao-run-automl` 将训练操作路由到此模型的 `skill_dir`。保留工作流/应用程序覆盖的数据集、规范、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时使用直接模型训练；在缺失模式的情况下，报告此模型启用 AutoML 但不可运行，直到生成模式。

非训练操作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每运行的 `automl_policy` 覆盖不会更改模型元数据。

## 训练要求

- **数据集类型：** 分割
- **格式：** coco_panoptic, coco
- **监控指标：** mIoU
- **AutoML 指标：** 最大化发出的验证/评估 `mIoU`；永远不要用训练损失替换。

### 每个操作的 数据集 要求

| 操作 | Spec Key | 来源 | 文件 | 列表？ |
|---|---|---|---|---|
| evaluate | dataset.train.type | train_datasets | coco_panoptic | 否 |
| evaluate | dataset.val.type | eval_dataset | coco_panoptic | 否 |
| evaluate | dataset.test.type | eval_dataset | coco_panoptic | 否 |
| evaluate | dataset.train.img_dir | train_datasets | images.tar.gz | 否 |
| evaluate | dataset.label_map | train_datasets | coco_panoptic: label_map_panoptic.json; *: label_map.json | 否 |
| evaluate | dataset.train.instance_json | train_datasets | annotations.json | 否 |
| evaluate | dataset.train.panoptic_json | train_datasets | annotations_panoptic.json | 否 |
| evaluate | dataset.train.panoptic_dir | train_datasets | images_panoptic.tar.gz | 否 |
| evaluate | dataset.val.img_dir | eval_dataset | images.tar.gz | 否 |
| evaluate | dataset.val.instance_json | eval_dataset | annotations.json | 否 |
| evaluate | dataset.val.panoptic_json | eval_dataset | annotations_panoptic.json | 否 |
| evaluate | dataset.val.panoptic_dir | eval_dataset | images_panoptic.tar.gz | 否 |
| evaluate | dataset.test.img_dir | eval_dataset | images.tar.gz | 否 |
| inference | dataset.train.type | train_datasets | coco_panoptic | 否 |
| inference | dataset.val.type | eval_dataset | coco_panoptic | 否 |
| inference | dataset.test.type | eval_dataset | coco_panoptic | 否 |
| inference | dataset.train.img_dir | train_datasets | images.tar.gz | 否 |
| inference | dataset.label_map | train_datasets | coco_panoptic: label_map_panoptic.json; *: label_map.json | 否 |
| inference | dataset.train.instance_json | train_datasets | annotations.json | 否 |
| inference | dataset.train.panoptic_json | train_datasets | annotations_panoptic.json | 否 |
| inference | dataset.train.panoptic_dir | train_datasets | images_panoptic.tar.gz | 否 |
| inference | dataset.val.img_dir | eval_dataset | images.tar.gz | 否 |
| inference | dataset.val.instance_json | eval_dataset | annotations.json | 否 |
| inference | dataset.val.panoptic_json | eval_dataset | annotations_panoptic.json | 否 |
| inference | dataset.val.panoptic_dir | eval_dataset | images_panoptic.tar.gz | 否 |
| inference | dataset.test.img_dir | eval_dataset | images.tar.gz | 否 |
| quantize | dataset.train.type | train_datasets | coco_panoptic | 否 |
| quantize | dataset.val.type | eval_dataset | coco_panoptic | 否 |
| quantize | dataset.test.type | eval_dataset | coco_panoptic | 否 |
| quantize | dataset.train.img_dir | train_datasets | images.tar.gz | 否 |
| quantize | dataset.label_map | train_datasets | coco_panoptic: label_map_panoptic.json; *: label_map.json | 否 |
| quantize | dataset.train.instance_json | train_datasets | annotations.json | 否 |
| quantize | dataset.train.panoptic_json | train_datasets | annotations_panoptic.json | 否 |
| quantize | dataset.train.panoptic_dir | train_datasets | images_panoptic.tar.gz | 否 |
| quantize | dataset.val.img_dir | eval_dataset | images.tar.gz | 否 |
| quantize | dataset.val.instance_json | eval_dataset | annotations.json | 否 |
| quantize | dataset.val.panoptic_json | eval_dataset | annotations_panoptic.json | 否 |
| quantize | dataset.val.panoptic_dir | eval_dataset | images_panoptic.tar.gz | 否 |
| quantize | dataset.test.img_dir | eval_dataset | images.tar.gz | 否 |
| quantize | dataset.quant_calibration_dataset.images_dir | train_datasets | images.tar.gz | 否 |
| train | dataset.train.type | train_datasets | coco_panoptic | 否 |
| train | dataset.val.type | eval_dataset | coco_panoptic | 否 |
| train | dataset.test.type | eval_dataset | coco_panoptic | 否 |
| train | dataset.train.img_dir | train_datasets | images.tar.gz | 否 |
| train | dataset.label_map | train_datasets | coco_panoptic: label_map_panoptic.json; *: label_map.json | 否 |
| train | dataset.train.instance_json | train_datasets | annotations.json | 否 |
| train | dataset.train.panoptic_json | train_datasets | annotations_panoptic.json | 否 |
| train | dataset.train.panoptic_dir | train_datasets | images_panoptic.tar.gz | 否 |
| train | dataset.val.img_dir | eval_dataset | images.tar.gz | 否 |
| train | dataset.val.instance_json | eval_dataset | annotations.json | 否 |
| train | dataset.val.panoptic_json | eval_dataset | annotations_panoptic.json | 否 |
| train | dataset.val.panoptic_dir | eval_dataset | images_panoptic.tar.gz | 否 |
| train | dataset.test.img_dir | eval_dataset | images.tar.gz | 否 |

### 典型 Spec 覆盖

数据源覆盖对每个操作都是**强制性的**——代理必须从上表中的“每个操作的 数据集 要求”构造数据源路径，并将其包含在 `spec_overrides` 中。

```python
S3_TRAIN = "s3://bucket/data/train"
S3_EVAL = "s3://bucket/data/eval"
```

**train (强制数据源):**
```python
{
    "train.num_gpus": 1,
    "train.num_epochs": 10,
    "train.checkpoint_interval": 10,
    "train.validation_interval": 10,
    "model.sem_seg_head.num_classes": 133,
    "dataset.contiguous_id": True,
    "dataset.train.type": "coco_panoptic",
    "dataset.val.type": "coco_panoptic",
    "dataset.test.type": "coco_panoptic",
    "dataset.train.img_dir": f"{S3_TRAIN}/images.tar.gz",
    "dataset.label_map": f"{S3_TRAIN}/label_map_panoptic.json",
    "dataset.train.instance_json": f"{S3_TRAIN}/annotations.json",
    "dataset.train.panoptic_json": f"{S3_TRAIN}/annotations_panoptic.json",
    "dataset.train.panoptic_dir": f"{S3_TRAIN}/images_panoptic.tar.gz",
    "dataset.val.img_dir": f"{S3_EVAL}/images.tar.gz",
    "dataset.val.instance_json": f"{S3_EVAL}/annotations.json",
    "dataset.val.panoptic_json": f"{S3_EVAL}/annotations_panoptic.json",
    "dataset.val.panoptic_dir": f"{S3_EVAL}/images_panoptic.tar.gz",
    "dataset.test.img_dir": f"{S3_EVAL}/images.tar.gz",
}
```

**evaluate (强制数据源):**
```python
{
    "evaluate.checkpoint": "<selected train/AutoML checkpoint>",
    "model.sem_seg_head.num_classes": 133,
    "dataset.contiguous_id": True,
    "dataset.train.type": "coco_panoptic",
    "dataset.val.type": "coco_panoptic",
    "dataset.test.type": "coco_panoptic",
    "dataset.train.img_dir": f"{S3_TRAIN}/images.tar.gz",
    "dataset.label_map": f"{S3_TRAIN}/label_map_panoptic.json",
    "dataset.train.instance_json": f"{S3_TRAIN}/annotations.json",
    "dataset.train.panoptic_json": f"{S3_TRAIN}/annotations_panoptic.json",
    "dataset.train.panoptic_dir": f"{S3_TRAIN}/images_panoptic.tar.gz",
    "dataset.val.img_dir": f"{S3_EVAL}/images.tar.gz",
    "dataset.val.instance_json": f"{S3_EVAL}/annotations.json",
    "dataset.val.panoptic_json": f"{S3_EVAL}/annotations_panoptic.json",
    "dataset.val.panoptic_dir": f"{S3_EVAL}/images_panoptic.tar.gz",
    "dataset.test.img_dir": f"{S3_EVAL}/images.tar.gz",
}
```

**export:**
```python
{
    "export.checkpoint": "<selected train/AutoML checkpoint>",
    "export.onnx_file": "<output ONNX path>",
    "model.sem_seg_head.num_classes": "<same value used for train>",
}
```

**inference (强制数据源):**
```python
{
    "inference.checkpoint": "<selected train/AutoML checkpoint>",
    "model.sem_seg_head.num_classes": "<same value used for train>",
    "dataset.contiguous_id": True,
    "dataset.train.img_dir": f"{S3_TRAIN}/images.tar.gz",
    "dataset.label_map": f"{S3_TRAIN}/label_map_panoptic.json",
    "dataset.train.instance_json": f"{S3_TRAIN}/annotations.json",
    "dataset.train.panoptic_json": f"{S3_TRAIN}/annotations_panoptic.json",
    "dataset.train.panoptic_dir": f"{S3_TRAIN}/images_panoptic.tar.gz",
    "dataset.val.img_dir": f"{S3_EVAL}/images.tar.gz",
    "dataset.val.instance_json": f"{S3_EVAL}/annotations.json",
    "dataset.val.panoptic_json": f"{S3_EVAL}/annotations_panoptic.json",
    "dataset.val.panoptic_dir": f"{S3_EVAL}/images_panoptic.tar.gz",
    "dataset.test.img_dir": f"{S3_EVAL}/images.tar.gz",
}
```

**quantize (强制数据源):**
```python
{
    "quantize.model_path": "<selected train/export artifact>",
    "dataset.train.img_dir": f"{S3_TRAIN}/images.tar.gz",
    "dataset.label_map": f"{S3_TRAIN}/label_map_panoptic.json",
    "dataset.train.instance_json": f"{S3_TRAIN}/annotations.json",
    "dataset.train.panoptic_json": f"{S3_TRAIN}/annotations_panoptic.json",
    "dataset.train.panoptic_dir": f"{S3_TRAIN}/images_panoptic.tar.gz",
    "dataset.val.img_dir": f"{S3_EVAL}/images.tar.gz",
    "dataset.val.instance_json": f"{S3_EVAL}/annotations.json",
    "dataset.val.panoptic_json": f"{S3_EVAL}/annotations_panoptic.json",
    "dataset.val.panoptic_dir": f"{S3_EVAL}/images_panoptic.tar.gz",
    "dataset.test.img_dir": f"{S3_EVAL}/images.tar.gz",
    "dataset.quant_calibration_dataset.images_dir": f"{S3_TRAIN}/images.tar.gz",
}
```
## Eval 数据集

可选。验证数据源与训练一起配置在数据集配置中。

## 重要参数

- **model.sem_seg_head.num_classes**: 分割类别数。默认 200。必须与您的标注类别匹配。
- **model.backbone.swin.type**: Swin Transformer 变体。默认 tiny。选项包括 tiny、small、base、large。
- **model.mode**: 分割模式。默认 panoptic。选项：panoptic、instance、semantic。
- **train.optim.lr**: 学习率。默认 2e-4 (AdamW)。
- **dataset.train.batch_size**: 每个GPU的批大小。默认 1。Mask2Former 由于逐像素预测而内存密集。
- **dataset.contiguous_id**: 如果为 true，将 `model.sem_seg_head.num_classes`
  设置为标签图类别的数量。如果为 false，将 `model.sem_seg_head.num_classes`
  设置为上述最大原始类别 ID 以上，并在评估、推理、导出、部署和量化时保持相同设置。COCO 全景 S3 示例有 133 个类别，原始 ID 最高为 200，因此原始 ID 验证使用 `num_classes: 201`。

## 多 GPU / 多节点

**启动方法：** Lightning 管理的（单个 `python` 进程，Lightning 生成工作进程）。

| Spec Key | 描述 | 默认 |
|----------|-------------|---------|
| `train.num_gpus` | GPU 数量 | 1 |
| `train.gpu_ids` | GPU 设备索引 | [0] |
| `train.num_nodes` | 节点数量 | 1 |
| `train.distributed_strategy` | `ddp` 或 `fsdp` | `ddp` |

- 与 DINO 相同的 DDP/FSDP 行为（激活检查点感知）
- FAN 主干自动启用 `sync_batchnorm`
- `fsdp` 强制 FP16

**多节点环境变量**（由编排器设置）：`WORLD_SIZE`、`NODE_RANK`、`MASTER_ADDR`、`MASTER_PORT`、`NUM_GPU_PER_NODE`。

## 导出 / TRT 默认值

- TRT 数据类型：FP32、FP16 仅限 — **INT8 不支持**
- 父 PyTorch `mask2former` CLI 支持 `train`、`evaluate`、`inference`、`export` 和 `quantize`；通过 `references/tao-deploy-mask2former.md` 运行 TensorRT 引擎生成、TensorRT 推理和 TensorRT 评估。当验证 TensorRT 评估时，导出语义 ONNX (`model.mode: semantic`)，因为当前的部署评估器接受语义引擎。
- 保持导出输入维度与部署模板兼容。打包的默认 `export.input_width: 960` 和 `export.input_height: 544`
  成功导出并构建 TensorRT 引擎；将导出缩小到微小的验证仅尺寸（如 `128x128`）可能会在生成 ONNX 之前触发 PyTorch ONNX
  `minus_one_pos != -1` 形状推断断言。

## 硬件

最低 1 个 GPU(s)，推荐 4 个 GPU(s)。每个 GPU 24GB+（推荐 A100）VRAM。Mask2Former 内存密集。batch_size=1 是默认值，原因充分。推荐多 GPU 以获得合理的训练速度。

## 错误模式

**CUDA 内存不足**：默认情况下 batch_size 已经为 1。在增强配置中降低图像分辨率或使用较小的 Swin 变体。

**全景与实例格式不匹配**：确保您提供与 `model.mode` 设置匹配的正确标注格式。

**部署模式错误，顶层 `dataset.type`**：TAO Deploy 使用
`dataset.val.type` 和 `dataset.test.type`。不要将 `dataset.type` 放在 Mask2Former 部署规范的顶层。

**导出 ONNX 形状断言在非常小的分辨率下**：如果导出因 PyTorch ONNX 形状推断的 `minus_one_pos != -1` 而失败，请在重试部署验证之前恢复模板导出维度 (`960x544`)。在需要快速冒烟测试时，保持训练和评估图像尺寸较小，但除非目标形状已验证，否则不要将那些微小的尺寸带入导出。

**量化检查点加载错误**：旧 PyTorch 图像可能因运行时量化脚本将 `experiment_spec` 传递给 `Mask2formerPlModule.load_from_checkpoint` 而不是必需的 `cfg` 参数，而使基于检查点的 `mask2former quantize` 失败。包含量化修复的图像支持默认的 `torchao` 检查点流程。ONNX 量化仍然需要
`backend: modelopt.onnx`、`mode: static_ptq`、固定的
`dataset.test.target_size` 和包含
`modelopt.onnx.quantization` 的图像。

## Spec 参数 / 父模型推理

特定于模型的推理映射属于此 MD 文件，而不是 `config.json`。生成的运行者应读取此部分，并使用 SDK 帮助程序在 `create_job()` 之前应用这些映射。这类似于旧的微服务 `infer_params.py` 流程。

来自 TAO Core `mask2former.config.json` 的推理映射：

| 操作 | Spec Field | Inference Function | 含义 |
|---|---|---|---|
| evaluate | `encryption_key` | `key` | 加密密钥 |
| evaluate | `evaluate.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| evaluate | `evaluate.trt_engine` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| evaluate | `results_dir` | `output_dir` | 当前作业结果目录 |
| export | `encryption_key` | `key` | 加密密钥 |
| export | `export.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| export | `export.onnx_file` | `create_onnx_file` | 输出 ONNX 路径 |
| export | `results_dir` | `output_dir` | 当前作业结果目录 |
| gen_trt_engine | `encryption_key` | `key` | 加密密钥 |
| gen_trt_engine | `gen_trt_engine.onnx_file` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| gen_trt_engine | `gen_trt_engine.trt_engine` | `create_engine_file` | 输出 TensorRT 引擎路径 |
| gen_trt_engine | `results_dir` | `output_dir` | 当前作业结果目录 |
| inference | `encryption_key` | `key` | 加密密钥 |
| inference | `inference.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| inference | `inference.trt_engine` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| inference | `results_dir` | `output_dir` | 当前作业结果目录 |
| quantize | `encryption_key` | `key` | 加密密钥 |
| quantize | `quantize.model_path` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| quantize | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `encryption_key` | `key` | 加密密钥 |
| train | `model.backbone.pretrained_weights` | `{'link': 'https://github.com/SwinTransformer/storage/releases/download/v1.0.8/swin_tiny_patch4_window7_224_22k.pth', 'destination_path': '/ptm/mask2former/swin_tiny_patch4_window7_224_22k/swin_tiny_patch4_window7_224_22k.pth'}` | `{'link': 'https://github.com/SwinTransformer/storage/releases/download/v1.0.8/swin_tiny_patch4_window7_224_22k.pth', 'destination_path': '/ptm/mask2former/swin_tiny_patch4_window7_224_22k/swin_tiny_patch4_window7_224_22k.pth'}` |
| train | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `train.resume_training_checkpoint_path` | `resume_model` | 从当前作业结果文件夹推断的模型文件 |

对于 `parent_model` 或 `parent_model_folder`，传递上游训练/导出/AutoML 子作业 ID 作为 `parent_job_id`。SDK 列出父结果文件夹，过滤检查点工件，并返回选定的模型文件或文件夹。不要将这些映射重新添加到 `config.json`，也不要修补生成的运行者脚本以猜测检查点路径。

当在 SDK 解析器之外选择 Mask2Former 检查点时，请确保与预期的 epoch/step 工件完全匹配，例如
`model_epoch_000_step_00100.pth`。`mask2former_model_latest.pth` 符号链接仅在明确请求最新时有效。

## 部署

- [tao-deploy-mask2former](references/tao-deploy-mask2former.md)
