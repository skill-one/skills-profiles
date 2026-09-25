# RT-DETR

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

RT-DETR（实时目标检测 Transformer）用于 2D 目标检测。专为实时推理设计，具有竞争力的精度。支持知识蒸馏和量化以优化部署。

设置 `model.pretrained_backbone_path` 用于主干权重，或设置 `train.pretrained_model_path` 用于完整模型。

对于 TAO Deploy TensorRT 操作 (`gen_trt_engine`、TensorRT `evaluate` 和 TensorRT `inference`)，请先阅读 `references/tao-deploy-rtdetr.md`。部署规范模板位于此技能的 `references/` 文件夹中，以 `spec_template_deploy_*.yaml` 为前缀。

## 数据类模式

生成的 TAO Core 模式打包在 `schemas/<action>.schema.json` 中，`schemas/manifest.json` 列出可用操作。每个生成的模式也从模式的顶层 `default` 字段发出 `references/spec_template_<action>.yaml`。AutoML 启用声明在 `references/skill_info.yaml` 中的模型层通过 `automl_enabled`。要为操作启用可运行的 AutoML，需要 `schemas/<action>.schema.json` 和 `references/spec_template_<action>.yaml` 存在并解析。使用打包的选定操作的方案进行 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖项和常用参数。不要期望 `~/tao-core` 在运行时；维护人员在打包技能库之前会重新生成模式/模板。

## 训练操作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，请阅读 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将短语如“关闭 AutoML”、“禁用 AutoML”、“无 HPO”或“纯训练”视为仅对此运行 `automl_policy: off`。当 `automl_policy: on`、`automl_enabled: true`，并且都打包了 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 时，默认通过 `tao-skill-bank:tao-run-automl` 将训练操作路由到此模型的 `skill_dir`。保留工作流/应用程序覆盖的数据集、规范、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时使用直接模型训练；在缺失模式的案例中，在生成模式之前报告此模型启用 AutoML 但不可运行。

非训练操作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每次运行的 `automl_policy` 覆盖不会更改模型元数据。

## 支持的操作

打包的 RT-DETR PyT CLI 支持 `train`、`distill`、`quantize`、`evaluate`、`export`、`inference` 和 `default_specs`。此模型技能公开 `train`、`distill`、`quantize`、`evaluate`、`export` 和 `inference`；通过 `train` 与 `train.resume_training_checkpoint_path` 执行恢复/重新训练。

父 PyT CLI 不公开 `gen_trt_engine`。使用 `models/rtdetr/deploy` 进行 TensorRT 引擎生成、TensorRT 评估和 TensorRT 推理。

## 训练要求

- **数据集类型：** object_detection
- **格式：** coco, coco_raw
- **AutoML 训练指标：** `val_mAP50` 用于快速操作检查或 `val_mAP` 用于 COCO/论文风格基准比较；两者都最大化。这些是结构化训练状态 KPI 名称的准确值。
- **独立评估指标：** `test_mAP50` 和 `test_mAP`。不要使用评估器的 `test_*` 名称进行 AutoML 试验排名。

### 每个操作的 数据集 要求

| 操作 | Spec Key | 来源 | 文件 | 是否列表 |
|---|---|---|---|---|
| distill | dataset.train_data_sources | train_datasets | image_dir: images.tar.gz, json_file: annotations.json | 是 |
| distill | dataset.val_data_sources | eval_dataset | image_dir: images.tar.gz, json_file: annotations.json | 否 |
| evaluate | dataset.test_data_sources | eval_dataset | image_dir: images.tar.gz, json_file: annotations.json | 否 |
| inference | dataset.infer_data_sources | inference_dataset | image_dir: images.tar.gz, classmap: label_map.txt | 是 |
| quantize | dataset.train_data_sources | train_datasets | image_dir: images.tar.gz, json_file: annotations.json | 是 |
| quantize | dataset.val_data_sources | eval_dataset | image_dir: images.tar.gz, json_file: annotations.json | 否 |
| quantize | dataset.quant_calibration_data_sources | train_datasets | image_dir: images.tar.gz, json_file: annotations.json | 否 |
| train | dataset.train_data_sources | train_datasets | image_dir: images.tar.gz, json_file: annotations.json | 是 |
| train | dataset.val_data_sources | eval_dataset | image_dir: images.tar.gz, json_file: annotations.json | 否 |

### 典型 Spec 覆盖

数据源覆盖对每个操作都是**必需的** — 代理必须根据上表中的“每个操作的 数据集 要求”构造数据源路径，并将其包含在 `spec_overrides` 中。

```python
S3_TRAIN = "s3://bucket/data/train"
S3_EVAL = "s3://bucket/data/eval"
CHECKPOINT = "/results/{train_job_id}/results_dir/model_epoch_000.pth"
ONNX_FILE = "/results/{export_job_id}/results_dir/rtdetr.onnx"
```

**train (必需数据源):**
```python
{
    "train.num_epochs": 10,
    "train.checkpoint_interval": 10,
    "train.validation_interval": 10,
    "train.num_gpus": 1,
    "train.gpu_ids": [0],
    "dataset.num_classes": "<num_classes> + 1",
    "dataset.train_data_sources": [{"image_dir": f"{S3_TRAIN}/images.tar.gz", "json_file": f"{S3_TRAIN}/annotations.json"}],
    "dataset.val_data_sources": {"image_dir": f"{S3_EVAL}/images.tar.gz", "json_file": f"{S3_EVAL}/annotations.json"},
}
```

**恢复训练 (必需检查点):**
```python
{
    "train.num_epochs": 11,
    "train.resume_training_checkpoint_path": CHECKPOINT,
    "dataset.num_classes": "<num_classes> + 1",
    "dataset.eval_class_ids": [1, 2, 3, 4],
    "dataset.train_data_sources": [{"image_dir": f"{S3_TRAIN}/images.tar.gz", "json_file": f"{S3_TRAIN}/annotations.json"}],
    "dataset.val_data_sources": {"image_dir": f"{S3_EVAL}/images.tar.gz", "json_file": f"{S3_EVAL}/annotations.json"},
}
```

**evaluate (必需数据源和检查点):**
```python
{
    "dataset.num_classes": "<num_classes> + 1",
    "dataset.eval_class_ids": [1, 2, 3, 4],
    "dataset.test_data_sources": {"image_dir": f"{S3_EVAL}/images.tar.gz", "json_file": f"{S3_EVAL}/annotations.json"},
    "evaluate.checkpoint": CHECKPOINT,
}
```

**export (必需检查点和输出):**
```python
{
    "dataset.num_classes": "<num_classes> + 1",
    "export.checkpoint": CHECKPOINT,
    "export.onnx_file": ONNX_FILE,
    "export.input_height": 640,
    "export.input_width": 640,
}
```

**quantize (必需数据源):**
```python
{
    "dataset.num_classes": "<num_classes> + 1",
    "quantize.layers": [
        {
            "module_name": "*",
            "weights": {
                "dtype": "float8_e4m3fn"
            },
            "activations": {
                "dtype": "float8_e4m3fn"
            }
        }
    ],
    "dataset.train_data_sources": [{"image_dir": f"{S3_TRAIN}/images.tar.gz", "json_file": f"{S3_TRAIN}/annotations.json"}],
    "dataset.val_data_sources": {"image_dir": f"{S3_EVAL}/images.tar.gz", "json_file": f"{S3_EVAL}/annotations.json"},
    "dataset.quant_calibration_data_sources": {"image_dir": f"{S3_TRAIN}/images.tar.gz", "json_file": f"{S3_TRAIN}/annotations.json"},
    "quantize.model_path": CHECKPOINT,
}
```

**inference (必需数据源和检查点):**
```python
{
    "dataset.num_classes": "<num_classes> + 1",
    "dataset.infer_data_sources": {"image_dir": [f"{S3_EVAL}/images.tar.gz"], "classmap": f"{S3_EVAL}/label_map.txt"},
    "inference.checkpoint": CHECKPOINT,
}
```

**distill (必需数据源和教师检查点):**
```python
{
    "dataset.train_data_sources": [{"image_dir": f"{S3_TRAIN}/images.tar.gz", "json_file": f"{S3_TRAIN}/annotations.json"}],
    "dataset.val_data_sources": {"image_dir": f"{S3_EVAL}/images.tar.gz", "json_file": f"{S3_EVAL}/annotations.json"},
    "distill.pretrained_teacher_model_path": CHECKPOINT,
}
```
## 评估数据集

可选。如果提供，则在每个检查点提供验证 mAP。

## 重要参数

- **dataset.num_classes**: 类别数量。默认 80 (MSCOCO 80 类)。必须与您的数据集注释匹配。
- **model.backbone**: 默认 resnet_50。支持：ResNet 变体、ConvNeXt、FAN、EfficientViT。RT-DETR 针对实时优化，使用更轻的主干。
- **train.optim.lr**: 学习率。默认 1e-4 (低于 DINO 的 2e-4)。lr_backbone 默认为 1e-5。
- **dataset.augmentation.train_spatial_size**: 训练输入大小。默认 [640, 640]。小于 DINO 的多尺度 (最高 1333)。RT-DETR 的速度关键。
- **model.num_feature_levels**: 默认 3 (与 DINO 的 4 相比)。return_interm_indices 是 [1,2,3]。
- **train.enable_ema**: 指数移动平均。默认 False。启用以获得更平滑的收敛。
- **dataset.remap_mscoco_category**: 默认 False。仅当为原始 MSCOCO 数据集时设置为 True，进行 91 到 80 类别 ID 的重新映射。

## 多 GPU / 多节点

**启动方法：** `torchrun` (LIGHTNING_EXCLUDED_NETWORK)。入口点运行 `torchrun --nnodes=N --nproc-per-node=M train.py`，而不是纯 `python`。

| Spec Key | 描述 | 默认值 |
|----------|-------------|---------|
| `train.num_gpus` | 每个节点的 GPU 数量 | 1 |
| `train.gpu_ids` | GPU 设备索引 | [0] |
| `train.num_nodes` | 节点数量 | 1 |
| `train.distributed_strategy` | `ddp` 或 `fsdp` | `ddp` |

- 当增加 `train.num_gpus` 时，还必须将 `train.gpu_ids` 设置为相同的可见设备范围。例如，8-GPU 单节点 Slurm 运行必须包含 `"train.num_gpus": 8` 和 `"train.gpu_ids": [0, 1, 2, 3, 4, 5, 6, 7]`。
- `CUDA_VISIBLE_DEVICES` 明确设置（与 Lightning 管理的模型使用 `TAO_VISIBLE_DEVICES` 不同）
- `ddp` 与激活检查点：`find_unused_parameters=False`
- `ddp` 无：`find_unused_parameters=True`
- 支持 `fsdp`，强制使用 FP16

**多节点环境变量** (由编排器设置):

| 变量 | 目的 |
|----------|---------|
| `WORLD_SIZE` | 节点数量 (触发多节点模式) |
| `NODE_RANK` | 此节点的排名 (0 索引) |
| `MASTER_ADDR` | 排名 0 节点 IP |
| `MASTER_PORT` | 排名 0 端口 (默认 29500) |
| `NUM_GPU_PER_NODE` | 每个节点的 GPU 数量 (默认：所有可见) |

**关键：** `NODE_RANK` 如果 `RANK` 未设置，则复制到 `RANK`。这对于 torchrun 多节点是必需的。

## 导出 / TRT 默认值

- 导出输入：640x640，opset 17
- TRT 数据类型：FP32、FP16、INT8
- TRT 工作空间：1024 MB
- TRT 最大批处理大小：4

## 知识蒸馏

RT-DETR 支持使用教师模型的知识蒸馏。需要 `distill` 操作和 `distill.pretrained_teacher_model_path` 以及蒸馏绑定配置。

使用打包的 `references/spec_template_distill.yaml` 作为起点。验证的默认绑定使用 RT-DETR 蒸馏器的显式 IOU 特征路径：

```yaml
distill:
  bindings:
  - student_module_name: srcs
    teacher_module_name: srcs
    criterion: IOU
    weight: 1.0
```

不要使用 DINO 风格的输出名称，如 `pred_logits` / `pred_boxes`，除非您已验证模块返回捕获的特征列表。RT-DETR 蒸馏器断言 IOU 绑定必须使用 `srcs` 或 `dsrcs`。

## 硬件

最低 1 个 GPU，推荐 2 个 GPU。每个 GPU 16GB+ (V100 或 A100) VRAM。RT-DETR 比DINO/GDINO更节省内存，因为输入大小较小 (640x640) 且特征级别较少。在单个 GPU 上对小中型数据集训练良好。

## 错误模式

**CUDA 内存不足**：减少 batch_size。RT-DETR 在 640x640 下比 DINO 在 1333px 下更轻，但 batch_size > 8 可能仍会在 16GB GPU 上 OOM。

**num_classes 不匹配**：RT-DETR 默认为 80 (不是像 DINO 的 91)。确保 `dataset.num_classes` 与您的注释类别匹配。

**CUDA 从类别 ID 断言**：如果 COCO 类别 ID 是基于 1 的或以其他方式未重新映射为基于 0 的连续 ID，请设置 `dataset.num_classes` 为 `max(category_id) + 1` 并保持 `dataset.eval_class_ids` 与实际类别 ID 对齐。对于打包的四类 S3 示例，ID 为 1-4，使用 `dataset.num_classes: 5` 和 `dataset.eval_class_ids: [1, 2, 3, 4]`。

**return_interm_indices 与 num_feature_levels**：默认为 [1,2,3] 且 `num_feature_levels=3`。如果更改，必须保持一致。

**导出形状不匹配**：除非模型已训练并检查了不同的形状，否则请保持 RT-DETR 导出和部署消费者输入大小在验证的 `640x640` 默认值。较旧的打包 `960x544` 模板形状可能在 ONNX 追踪期间失败，`hybrid_encoder.py` 中的位置嵌入加法出现 `The size of tensor a (...) must match the size of tensor b (...)`。

**AutoML 指标提取**：RT-DETR 在结构化训练状态和日志中发出检测指标。对于 COCO/论文风格基准比较，使用 `direction: maximize` 优化 `val_mAP`；对于显式 AP50 工作流，优化 `val_mAP50`。独立评估发出相应的 `test_mAP` 和 `test_mAP50` 键。优先使用 `results_dir/train/status.json` 或 AutoML 结果状态，而不是解析原始日志。不要针对默认检测模型调用优化 `val_loss`。

**检查点交接**：对于 evaluate/export/inference/quantize/distill/resume，使用最佳 AutoML 子作业的 `results_dir/train/` 文件夹上的检查点解析器，并选择适当的 `model_epoch_*.pth` 检查点。RT-DETR 也可能写入最新符号链接，但仅在调用者明确请求最新时使用。保持 `dataset.num_classes`、`dataset.eval_class_ids`、`model.num_queries` 和 `model.num_select` 与训练一致。

**父 `rtdetr gen_trt_engine` 被 PyT CLI 拒绝**：在验证的 7.0.0 PyT 容器中，`rtdetr gen_trt_engine` 不是父模型子任务的有效值。使用 RT-DETR 部署工作流 (`references/tao-deploy-rtdetr.md`) 进行 TensorRT 引擎生成、TensorRT 评估和 TensorRT 推理。

## Spec 参数 / 父模型推理

模型特定推理映射属于此 MD 文件，而不是 `config.json`。生成的运行者应读取本节并使用 SDK 帮助程序在 `create_job()` 之前应用这些映射。这类似于旧的微服务 `infer_params.py` 流程。

来自 TAO Core `rtdetr.config.json` 的推理映射：

| 操作 | Spec Field | 推理函数 | 含义 |
|---|---|---|---|
| distill | `distill.pretrained_teacher_model_path` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| distill | `encryption_key` | `key` | 加密密钥 |
| distill | `results_dir` | `output_dir` | 当前作业结果目录 |
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
| train | `model.pretrained_backbone_path` | `ptm_if_no_resume_model` | 当不存在恢复检查点时的 PTM |
| train | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `train.pretrained_model_path` | `ptm_if_no_resume_model` | 当不存在恢复检查点时的 PTM |
| train | `train.resume_training_checkpoint_path` | `resume_model` | 从当前作业结果文件夹推断的模型文件 |

对于 `parent_model` 或 `parent_model_folder`，将上游训练/导出/AutoML 子作业 ID 作为 `parent_job_id` 传递。SDK 列出父结果文件夹，过滤检查点工件，并返回选定的模型文件或文件夹。不要将这些映射重新添加到 `config.json`，也不要修补生成的运行者脚本以猜测检查点路径。

## 部署

- [tao-deploy-rtdetr](references/tao-deploy-rtdetr.md)
