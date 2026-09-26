# Mask Grounding DINO

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

Mask Grounding DINO 用于基于文本提示的实例分割。在 Grounding DINO 的基础上增加了用于开放集分割的掩码预测头。

设置 `train.pretrained_model_path` 以使用完整模型权重。

对于 TAO Deploy TensorRT 操作 (`gen_trt_engine`, TensorRT `evaluate` 和 TensorRT `inference`)，请先阅读 `references/tao-deploy-mask-grounding-dino.md`。部署规范模板位于此技能的 `references/` 文件夹中，以 `spec_template_deploy_*.yaml` 为前缀。

## 数据类模式

生成的 TAO Core 模式打包在 `schemas/<action>.schema.json` 中，`schemas/manifest.json` 列出可用操作。每个生成的模式也从模式的顶层 `default` 字段生成 `references/spec_template_<action>.yaml`。AutoML 启用声明在 `references/skill_info.yaml` 中的模型层通过 `automl_enabled` 进行。要为操作启用可运行的 AutoML，需要 `schemas/<action>.schema.json` 和 `references/spec_template_<action>.yaml` 存在并可以解析。使用打包的选定操作的方案用于 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖关系和常用参数。不要期望在运行时存在 `~/tao-core`；维护者在打包技能库之前会重新生成模式/模板。

## 训练操作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，请阅读 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将类似于 "关闭 AutoML"、"禁用 AutoML"、"无 HPO" 或 "纯训练" 的短语视为 `automl_policy: off`，仅针对此运行。当 `automl_policy: on`、`automl_enabled: true`，并且都打包了 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 时，默认情况下将训练操作通过 `tao-skill-bank:tao-run-automl` 并使用此模型的 `skill_dir` 进行路由。保留工作流/应用程序覆盖的数据集、规范、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时使用直接模型训练；在缺失模式的案例中，在生成模式之前报告此模型启用 AutoML 但不可运行。

非训练操作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每运行的 `automl_policy` 覆盖不会更改模型元数据。

## 训练要求

- **数据集类型：** 分割
- **格式：** odvg、coco、coco_raw
- **监控指标：** val_loss
- **AutoML 指标契约：** 使用训练期间发出的 `val_loss` 并将其最小化。独立评估指标是检查点验证 KPI，不是推荐选择目标。
- **评估检查点指标：** 当检查点产生类别预测时，`[segm] test_mAP50` 和 `[bbox] test_mAP50`。一个非常短的 smoke-trained 检查点可以成功完成评估，此时 KPI 字典为空；在这种情况下，请验证评估操作和结果工件。训练阶段 AutoML 选择仍然基于 `val_loss`。

### 每个操作的 数据集 要求

| 操作 | Spec Key | 来源 | 文件 | 列表？ |
|---|---|---|---|---|
| evaluate | dataset.test_data_sources | eval_dataset | image_dir: images.tar.gz, json_file: annotations.json | 否 |
| evaluate | dataset.test_data_sources.data_type | eval_dataset | OD | 否 |
| inference | dataset.infer_data_sources | inference_dataset | image_dir: images.tar.gz, captions: 文本提示 | 否 |
| inference | dataset.infer_data_sources.data_type | inference_dataset | OD | 否 |
| quantize | dataset.train_data_sources | train_datasets | image_dir: images.tar.gz, json_file: annotations_odvg.jsonl, label_map: annotations_odvg_labelmap.json | 是 |
| quantize | dataset.val_data_sources | eval_dataset | image_dir: images.tar.gz, json_file: annotations.json | 否 |
| quantize | dataset.val_data_sources.data_type | eval_dataset | OD | 否 |
| quantize | dataset.quant_calibration_data_sources | train_datasets | image_dir: images.tar.gz, json_file: annotations_odvg.jsonl, label_map: annotations_odvg_labelmap.json | 是 |
| train | dataset.train_data_sources | train_datasets | image_dir: images.tar.gz, json_file: annotations_odvg.jsonl, label_map: annotations_odvg_labelmap.json | 是 |
| train | dataset.val_data_sources | eval_dataset | image_dir: images.tar.gz, json_file: annotations.json | 否 |
| train | dataset.val_data_sources.data_type | eval_dataset | OD | 否 |

### 典型的 Spec 覆盖

数据源覆盖对每个操作都是**必需的** — 代理必须从上表中的每个操作的 数据集 要求构造数据源路径，并将其包含在 `spec_overrides` 中。

```python
S3_TRAIN = "s3://bucket/data/train"
S3_EVAL = "s3://bucket/data/eval"
```

**train (必需的数据源):**
```python
{
    "train.num_gpus": 1,
    "train.num_epochs": 10,
    "train.checkpoint_interval": 10,
    "train.validation_interval": 10,
    "dataset.val_data_sources.data_type": "OD",
    "model.num_region_queries": 100,
    "dataset.train_data_sources": [{"image_dir": f"{S3_TRAIN}/images.tar.gz", "json_file": f"{S3_TRAIN}/annotations_odvg.jsonl", "label_map": f"{S3_TRAIN}/annotations_odvg_labelmap.json"}],
    "dataset.val_data_sources": {"image_dir": f"{S3_EVAL}/images.tar.gz", "json_file": f"{S3_EVAL}/annotations.json"},
}
```

**evaluate (必需的数据源):**
```python
{
    "evaluate.checkpoint": "<选定的 train/AutoML 检查点>",
    "dataset.test_data_sources.data_type": "OD",
    "dataset.test_data_sources": {"image_dir": f"{S3_EVAL}/images.tar.gz", "json_file": f"{S3_EVAL}/annotations.json"},
}
```

**inference (必需的数据源):**
```python
{
    "inference.checkpoint": "<选定的 train/AutoML 检查点>",
    "dataset.infer_data_sources.data_type": "OD",
    "dataset.infer_data_sources": {"image_dir": f"{S3_EVAL}/images.tar.gz", "captions": ["person", "bicycle", "car"]},
}
```

**quantize (必需的数据源):**
```python
{
    "dataset.train_data_sources": [{"image_dir": f"{S3_TRAIN}/images.tar.gz", "json_file": f"{S3_TRAIN}/annotations_odvg.jsonl", "label_map": f"{S3_TRAIN}/annotations_odvg_labelmap.json"}],
    "dataset.val_data_sources": {"image_dir": f"{S3_EVAL}/images.tar.gz", "json_file": f"{S3_EVAL}/annotations.json"},
    "dataset.quant_calibration_data_sources": {"image_dir": f"{S3_TRAIN}/images.tar.gz", "json_file": f"{S3_TRAIN}/annotations_odvg.jsonl", "label_map": f"{S3_TRAIN}/annotations_odvg_labelmap.json"},
}
```
## Eval 数据集

可选。验证即使训练使用 ODVG 也会使用 COCO 格式的标注。

## 重要参数

- **model.backbone**: 默认 swin_tiny_224_1k。与 Grounding DINO 相同的骨干选项。
- **train.optim.lr**: 学习率。默认 2e-4。lr_backbone 2e-5。重用 GDINOTrainExpConfig — 与 Grounding DINO 相同的训练设置。
- **model.num_queries**: 对象查询。默认 900。
- **model.enc_layers / model.dec_layers**: 在训练/AutoML 运行时保持两者均为 6。掩码头在验证期间断言六个解码器输出，因此复制 Grounding DINO 的 smoke 覆盖减少 transformer 层会导致立即失败。
- **AutoML 指标说明：** 使用 `metric="val_loss"` 和 `direction="minimize"` 进行训练阶段 AutoML。打包的训练循环记录验证损失标量；它不会在训练作业期间发出 `[bbox] val_mAP@50`。独立评估仅在预测满足其阈值时发出 `[segm] test_mAP50` 和 `[bbox] test_mAP50`；不要用任何条件测试指标替代用于排名 AutoML 推荐的训练损失。
- **model.has_mask**: 启用掩码预测头。默认 True。添加掩码/dice/rela 损失系数。
- **model.num_region_queries**: 掩码预测的区域查询数。默认 100。
- **model.loss_types**: 损失组件。默认 [labels, boxes, masks]。包括 mask_loss_coef、dice_loss_coef、rela_loss_coef。
- **evaluate.ioi_threshold**: 掩码评估的 IoI 阈值。默认 0.5。
- **evaluate.nms_threshold**: NMS 阈值。默认 0.2。
- **evaluate.text_threshold**: 文本匹配阈值。默认 0.3。
- **dataset.has_mask**: 数据集包含掩码标注。默认 True。val_data_sources 默认数据类型是 "VG"。

## 多 GPU / 多节点

**启动方法：** Lightning 管理的。与 Grounding DINO 相同的 DDP/FSDP 行为。

| Spec Key | 描述 | 默认 |
|----------|-------------|---------|
| `train.num_gpus` | GPU 数量 | 1 |
| `train.gpu_ids` | GPU 设备索引 | [0] |
| `train.num_nodes` | 节点数量 | 1 |
| `train.distributed_strategy` | `ddp` 或 `fsdp` | `ddp` |

## 硬件

至少 1 个 GPU(s)，推荐 4 个 GPU(s)。每个 GPU 24GB+（推荐 A100）VRAM。由于掩码预测头，比 Grounding DINO 更重。推荐 24GB+ GPU 内存。

## 错误模式

**CUDA 内存不足：** 减小 batch_size。掩码预测在 Grounding DINO 之上增加了开销。

**部署 `test_threshold` 模式错误：** TAO Deploy 使用 `evaluate.text_threshold` 和 `inference.text_threshold`。不要在部署规范中使用 `test_threshold`。

**部署模型形状不匹配：** 将 transformer 和掩码结构字段从导出带到部署评估/推理规范中，包括 `model.num_queries`、`model.num_select`、`model.max_text_len`、`model.num_region_queries` 和 `model.has_mask`。这些值必须与用于构建 TensorRT 引擎的 ONNX 模型匹配。

## Spec 参数 / 父模型推理

模型特定的推理映射属于此 MD 文件，而不是 `config.json`。生成的运行器应在此部分读取并使用 SDK 帮助程序在 `create_job()` 之前应用这些映射。这与旧的微服务 `infer_params.py` 流程类似。

来自 TAO Core `mask_grounding_dino.config.json` 的推理映射：

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
| train | `model.pretrained_backbone_path` | `ptm_if_no_resume_model` | 当不存在恢复检查点时 PTM |
| train | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `train.pretrained_model_path` | `ptm_if_no_resume_model` | 当不存在恢复检查点时 PTM |
| train | `train.resume_training_checkpoint_path` | `resume_model` | 从当前作业结果文件夹推断的模型文件 |

对于 `parent_model` 或 `parent_model_folder`，将上游 train/export/AutoML 子作业 ID 作为 `parent_job_id` 传递。SDK 列出父结果文件夹，过滤检查点工件，并返回选定的模型文件或文件夹。不要将这些映射重新添加到 `config.json`，也不要修补生成的运行器脚本以猜测检查点路径。

当在 SDK 解析器之外选择 Mask Grounding DINO 检查点时，请精确匹配预期的 epoch/step 工件，例如 `model_epoch_000_step_00049.pth`。`mask_gdino_model_latest.pth` 符号链接仅在明确请求最新时才有效。父 PyTorch `mask_grounding_dino` CLI 支持 `train`、`evaluate`、`inference`、`export` 和 `quantize`；通过 `references/tao-deploy-mask-grounding-dino.md` 运行 TensorRT 引擎生成、TensorRT 推理和 TensorRT 评估。

## 部署

- [tao-deploy-mask-grounding-dino](references/tao-deploy-mask-grounding-dino.md)
