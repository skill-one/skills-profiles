# Grounding DINO

> **独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

Grounding DINO 用于开放集目标检测。结合 DINO 风格检测与 BERT 文本编码器进行语言引导检测。可检测由文本提示描述的对象，无需固定的类别词汇。

设置 `train.pretrained_model_path` 以使用完整的 Grounding DINO 权重或 `model.pretrained_backbone_path` 以仅使用主干网络。

对于 TAO Deploy TensorRT 操作 (`gen_trt_engine`、TensorRT `evaluate` 和 TensorRT `inference`)，请先阅读 `references/tao-deploy-grounding-dino.md`。部署规范模板位于此技能的 `references/` 文件夹中，以 `spec_template_deploy_*.yaml` 为前缀。

## 数据类模式

生成的 TAO Core 模式打包在 `schemas/<action>.schema.json` 中，`schemas/manifest.json` 列出可用操作。每个生成的模式也从模式的顶层 `default` 字段发出 `references/spec_template_<action>.yaml`。AutoML 启用声明在 `references/skill_info.yaml` 中的模型层通过 `automl_enabled`。运行 AutoML 需要存在并解析 `schemas/<action>.schema.json` 和 `references/spec_template_<action>.yaml`。使用打包的选定操作的规范进行 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖关系和常用参数。不要期望运行时存在 `~/tao-core`；维护人员在打包技能库之前会重新生成模式/模板。

## 训练操作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，请阅读 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将短语如 "关闭 AutoML"、"禁用 AutoML"、"无 HPO" 或 "纯训练" 视为仅对此运行 `automl_policy: off`。当 `automl_policy: on`、`automl_enabled: true`，并且都打包了 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 时，默认通过 `tao-skill-bank:tao-run-automl` 路由训练操作，使用此模型的 `skill_dir`。保留工作流/应用程序覆盖的数据集、规范、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时使用直接模型训练；在缺失模式的案例中，在生成模式之前报告此模型启用 AutoML 但不可运行。

非训练操作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每次运行的 `automl_policy` 覆盖不会更改模型元数据。

## 训练要求

- **数据集类型：** object_detection
- **格式：** odvg、coco、raw
- **训练监控指标：** `val_mAP50`
- **AutoML 指标契约：** 对于基于评估的选择，使用 `test_mAP50` 并设置最大化方向。打包的 `evaluate` 操作发出 `test_mAP50`；使用该评估器 KPI 进行 AutoML 试验比较和最终选择，而不是仅训练的 `val_mAP50` 键。

### 每个操作的 数据集 要求

| 操作 | Spec Key | 来源 | 文件 | 列表？ |
|---|---|---|---|---|
| evaluate | dataset.test_data_sources | eval_dataset | image_dir: images.tar.gz, json_file: annotations.json | 否 |
| inference | dataset.infer_data_sources.image_dir | inference_dataset | images.tar.gz | 是 |
| inference | dataset.infer_data_sources.captions | 工作流提示 | 提示列表 | 是 |
| quantize | dataset.train_data_sources | train_datasets | image_dir: images.tar.gz, json_file: annotations_odvg.jsonl, label_map: annotations_odvg_labelmap.json | 是 |
| quantize | dataset.val_data_sources | eval_dataset | image_dir: images.tar.gz, json_file: annotations.json | 否 |
| quantize | dataset.quant_calibration_data_sources | calibration/eval 数据集 | image_dir: images.tar.gz, json_file: annotations.json | 否 |
| train | dataset.train_data_sources | train_datasets | image_dir: images.tar.gz, json_file: annotations_odvg.jsonl, label_map: annotations_odvg_labelmap.json | 是 |
| train | dataset.val_data_sources | eval_dataset | image_dir: images.tar.gz, json_file: annotations.json | 否 |

运行者可以源图像存档为 `images.tar.gz`，但直接本地 Docker TAO CLI 规范必须将 `image_dir` 指向提取的图像目录。技能元数据使用 `runtime: extracted_folder` 标记这些存档支持的图像来源，以便新的运行者在启动 TAO 之前可以解压存档。

### 典型 Spec 覆盖

数据源覆盖对每个操作都是**必需的** — 代理必须根据上表中的每个操作的 数据集 要求构建数据源路径，并将其包含在 `spec_overrides` 中。

```python
S3_TRAIN = "s3://bucket/data/train"
S3_EVAL = "s3://bucket/data/eval"
```

**train (必需数据源):**
```python
{
    "train.num_epochs": 10,
    "train.checkpoint_interval": 10,
    "train.validation_interval": 10,
    "train.num_gpus": 1,
    "dataset.train_data_sources": [{"image_dir": f"{S3_TRAIN}/images.tar.gz", "json_file": f"{S3_TRAIN}/annotations_odvg.jsonl", "label_map": f"{S3_TRAIN}/annotations_odvg_labelmap.json"}],
    "dataset.val_data_sources": {"image_dir": f"{S3_EVAL}/images.tar.gz", "json_file": f"{S3_EVAL}/annotations.json"},
}
```

**deploy/gen_trt_engine (使用 `references/tao-deploy-grounding-dino.md`):**
```python
{
    "gen_trt_engine.onnx_file": "<exported_onnx_uri>",
    "gen_trt_engine.trt_engine": "<output_engine_path>",
    "gen_trt_engine.tensorrt.data_type": "FP16",
}
```

**inference (必需数据源):**
```python
{
    "inference.checkpoint": "<selected train/AutoML 检查点>",
    "dataset.infer_data_sources.image_dir": [f"{S3_EVAL}/images.tar.gz"],
    "dataset.infer_data_sources.captions": [
        "灭火器",
        "锥形",
        "手推车",
        "叉车"
    ],
}
```

**evaluate (必需数据源):**
```python
{
    "evaluate.checkpoint": "<selected train/AutoML 检查点>",
    "dataset.test_data_sources": {"image_dir": f"{S3_EVAL}/images.tar.gz", "json_file": f"{S3_EVAL}/annotations.json"},
}
```

**quantize (必需数据源):**
```python
{
    "quantize.model_path": "<selected train 检查点或导出的 ONNX 模型>",
    "dataset.train_data_sources": [{"image_dir": f"{S3_TRAIN}/images.tar.gz", "json_file": f"{S3_TRAIN}/annotations_odvg.jsonl", "label_map": f"{S3_TRAIN}/annotations_odvg_labelmap.json"}],
    "dataset.val_data_sources": {"image_dir": f"{S3_EVAL}/images.tar.gz", "json_file": f"{S3_EVAL}/annotations.json"},
    "dataset.quant_calibration_data_sources": {"image_dir": f"{S3_EVAL}/images.tar.gz", "json_file": f"{S3_EVAL}/annotations.json"},
}
```
## Eval 数据集

可选。验证使用 COCO 格式标注进行 mAP，即使训练可以使用 ODVG 格式。

## 重要参数

- **model.backbone**: 默认 swin_tiny_224_1k。也支持 resnet_50 和其他 Swin 变体。Swin 通常在 grounding 任务中表现更好。
- **model.text_encoder_type**: 用于文本编码的 BERT 模型。默认 bert-base-uncased。max_text_len 默认为 256。
- **model.max_text_len**: 与数据集标签/标记位置图保持一致。除非相应的标签图使用相同长度重新生成，否则不要缩小它进行烟雾测试；否则验证可能会因标记概率和位置图之间的矩阵形状不匹配而失败。
- **train.optim.lr**: 学习率。默认 2e-4。lr_backbone 2e-5。除了 fp16/fp32 之外，还支持 bf16 精度。
- **dataset.max_labels**: 训练期间每张图像的最大标签。默认 50。对于密集标注数据集，请增加。
- **model.num_queries**: 对象查询。默认 900（高于 DINO 的 300），由于开放词汇性质。
- **model.num_queries / model.num_select**: 确保 `num_queries` 足够高，以匹配批次中匹配的 ODVG 目标数量。非常小的烟雾值（如 20）在密集图像上的匈牙利目标索引期间可能会失败；除非数据集每张图像的对象数量已知较少，否则至少使用 100 进行最小的 Grounding DINO 烟雾运行。
- **train.optim.lr_steps**: 多步 LR 调度。默认 [10]。

## 多 GPU / 多节点

**启动方法：** Lightning 管理的（单个 `python` 进程，Lightning 生成工作进程）。

| Spec Key | 描述 | 默认 |
|----------|-------------|---------|
| `train.num_gpus` | GPU 数量 | 1 |
| `train.gpu_ids` | GPU 设备索引 | [0] |
| `train.num_nodes` | 节点数量 | 1 |
| `train.distributed_strategy` | `ddp` 或 `fsdp` | `ddp` |

与 DINO 相同的 DDP/FSDP 行为。多节点需要 `WORLD_SIZE`、`NODE_RANK`、`MASTER_ADDR`、`MASTER_PORT` 环境变量由协调器设置。

## 导出 / TRT 默认值

- 导出输入：960x544（大于其他 OD 模型），opset 17。保持 Grounding-DINO 导出规范在烟雾测试的模板导出分辨率；将导出缩小到非常小的图像尺寸（如 128x128）可能会在 `torch.onnx.export` 期间触发对比文本头的 PyTorch ONNX 形状推断断言。
- 父 PyTorch `grounding_dino` CLI 支持 `train`、`evaluate`、`inference`、`export` 和 `quantize`。通过 `references/tao-deploy-grounding-dino.md` 运行 TensorRT 引擎生成、TensorRT 推理和 TensorRT 评估。
- TRT 数据类型：FP32、FP16 仅 — **INT8 不支持**
- TRT 工作空间：8192 MB（比其他 OD 模型大 8 倍）
- TRT 最大批处理大小：4

## 硬件

至少 1 个 GPU(s)，推荐 4 个 GPU(s)。每 GPU 24GB+（推荐 A100）VRAM。Grounding DINO 比标准 DINO 更重，因为文本编码器（BERT）。推荐 24GB+ GPU 内存。对于 16GB GPU，请减少批处理大小。

## 错误模式

**CUDA 内存不足**：减少 batch_size（4 -> 2 -> 1）。BERT 文本编码器在视觉主干网络之上增加了显著的内存开销。

**Val 标注类别 ID**：验证标注应从 0 开始具有类别 ID，以便正确计算损失。如有必要，使用标注格式转换。

**文本编码器加载错误**：确保容器可以访问下载 bert-base-uncased 权重或提供本地路径。

**在 TAO Toolkit 7.0.0-rc-226 中使用 PyTorch 检查点量化失败**：
容器的 Grounding-DINO 量化脚本在加载检查点时传递 `cap_lists=None`，这会在 `post_process.py` 中失败。ONNX 量化使用导出的 ONNX 艺术品和 COCO 校准数据，但默认的 rc-226 PyTorch 图像也缺少 `modelopt.onnx.quantization` 模块。将其视为图像/SDK 阻塞，而不是检查点解析问题。

**mat1 和 mat2 形状不能在 `post_process.py` 中相乘**：文本标记长度和标签位置图不一致，通常是因为 `model.max_text_len` 被覆盖到默认的 256 以下，而数据集标签图仍然使用 256 长度的位置图。恢复 `model.max_text_len` 或使用相同长度重新生成标签图。

**`criterion.py` 中维度 0 的索引超出范围**：`model.num_queries` 对于当前批次中匹配的 ODVG 目标太小。增加 `model.num_queries` 并保持 `model.num_select` 与其兼容。

**`images.tar.gz/<image>.jpg` 与 NotADirectoryError**：直接 TAO CLI 尝试将存档路径作为目录遍历。解压存档并将相关 `image_dir` 字段设置为提取的图像文件夹；由于此原因，存档支持的技能数据源使用 `runtime: extracted_folder`。

## Spec 参数 / 父模型推理

特定于模型的推理映射属于此 MD 文件，而不是 `config.json`。生成的运行者应读取此部分并使用 SDK 帮助程序在 `create_job()` 之前应用这些映射。这反映了旧的微服务 `infer_params.py` 流程。

来自 TAO Core `grounding_dino.config.json` 的推理映射：

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
| train | `model.pretrained_backbone_path` | `ptm_if_no_resume_model` | 当不存在恢复检查点时 PTM |
| train | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `train.pretrained_model_path` | `ptm_if_no_resume_model` | 当不存在恢复检查点时 PTM |
| train | `train.resume_training_checkpoint_path` | `resume_model` | 从当前作业结果文件夹推断的模型文件 |

对于 `parent_model` 或 `parent_model_folder`，将上游训练/导出/AutoML 子作业 ID 作为 `parent_job_id` 传递。SDK 列出父结果文件夹，过滤检查点工件，并返回选定的模型文件或文件夹。不要将这些映射重新添加到 `config.json`，也不要修补生成的运行者脚本以猜测检查点路径。

在外部 SDK 解析器之外选择 Grounding-DINO 检查点时，请精确匹配预期的 epoch/step 艺术品，例如 `model_epoch_000_step_00046.pth`。`gdino_model_latest.pth` 符号链接仅在明确请求最新时有效。将结构模型设置（如 `model.backbone`、`model.num_queries`、`model.num_select`、`model.num_feature_levels`、`model.max_text_len` 和导出输入分辨率）转发到 evaluate、inference、export 和 deploy 规范，以便检查点和引擎形状匹配。

## 部署

- [tao-deploy-grounding-dino](references/tao-deploy-grounding-dino.md)
