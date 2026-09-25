# Classification PyT

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

PyTorch 图像分类。支持多种主干网络（FAN、EfficientNet、ResNet 等），并支持蒸馏和量化以用于部署。

设置 `model.backbone.pretrained_backbone_path` 用于主干网络权重，或设置 `train.pretrained_model_path` 用于完整模型。

对于 TAO Deploy TensorRT 操作 (`gen_trt_engine`、TensorRT `evaluate` 和 TensorRT `inference`)，请先阅读 `references/tao-deploy-image-classification.md`。部署规范模板位于此技能的 `references/` 文件夹中，以 `spec_template_deploy_*.yaml` 为前缀。

## 数据类模式

生成的 TAO Core 模式打包在 `schemas/<action>.schema.json` 中，`schemas/manifest.json` 列出可用操作。每个生成的模式也从模式的顶层 `default` 字段发出 `references/spec_template_<action>.yaml`。AutoML 启用声明在模型层的 `references/skill_info.yaml` 中通过 `automl_enabled` 进行。运行 AutoML 需要存在并解析 `schemas/<action>.schema.json` 和 `references/spec_template_<action>.yaml`。使用打包的选定操作的规范进行 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖关系和常用参数。不要期望运行时 `~/tao-core`；维护者在打包技能库之前会重新生成模式/模板。

## 训练操作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，请阅读 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将类似于 "关闭 AutoML"、"禁用 AutoML"、"无 HPO" 或 "纯训练" 的短语视为 `automl_policy: off`，仅针对此运行。当 `automl_policy: on`、`automl_enabled: true`，并且 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 都被打包时，默认通过 `tao-skill-bank:tao-run-automl` 将训练操作路由到此模型的 `skill_dir`。保留工作流/应用程序覆盖的数据集、规范、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时才使用直接模型训练；在缺失模式的案例中，在生成模式之前报告此模型启用 AutoML 但不可运行。

非训练操作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每运行的 `automl_policy` 覆盖不会更改模型元数据。

## 训练要求

- **数据集类型：** image_classification
- **格式：** classification_pyt
- **监控指标：** val_acc_1
- **AutoML 训练范围：** 从普通 `train` 搜索中排除 `distill.teacher.*` 参数。这些字段属于单独的 `distill` 操作，即使它们出现在组合生成的模式中，也不会改变 `classification_pyt train` 行为。

### 每个操作的 数据集 要求

| 操作 | 规范键 | 源 | 文件 | 列表？ |
|---|---|---|---|---|
| distill | dataset.train_dataset.images_dir | train_datasets | images_train.tar.gz | 否 |
| distill | dataset.classes_file | train_datasets | classes.txt | 否 |
| distill | dataset.val_dataset.images_dir | eval_dataset | images_val.tar.gz | 否 |
| evaluate | dataset.val_dataset.images_dir | eval_dataset | images_val.tar.gz | 否 |
| evaluate | dataset.classes_file | eval_dataset | classes.txt | 否 |
| evaluate | dataset.test_dataset.images_dir | inference_dataset | images_test.tar.gz | 否 |
| export | dataset.root_dir | train_datasets |  | 否 |
| inference | dataset.val_dataset.images_dir | eval_dataset | images_val.tar.gz | 否 |
| inference | dataset.classes_file | eval_dataset | classes.txt | 否 |
| inference | dataset.test_dataset.images_dir | inference_dataset | images_test.tar.gz | 否 |
| quantize | dataset.train_dataset.images_dir | train_datasets | images_train.tar.gz | 否 |
| quantize | dataset.classes_file | train_datasets | classes.txt | 否 |
| quantize | dataset.val_dataset.images_dir | eval_dataset | images_val.tar.gz | 否 |
| quantize | dataset.quant_calibration_dataset.images_dir | calibration_dataset | images_train.tar.gz | 否 |
| train | dataset.train_dataset.images_dir | train_datasets | images_train.tar.gz | 否 |
| train | dataset.classes_file | train_datasets | classes.txt | 否 |
| train | dataset.val_dataset.images_dir | eval_dataset | images_val.tar.gz | 否 |

### 典型的 规范 覆盖

数据源覆盖对**每个操作都是强制性的**——代理必须根据上表中的“每个操作的 数据集 要求”构建数据源路径，并将其包含在 `spec_overrides` 中。

```python
TRAIN_IMAGES_DIR = "/workspace/data/extracted/train/images_train"
VAL_IMAGES_DIR = "/workspace/data/extracted/val/images_val"
TEST_IMAGES_DIR = "/workspace/data/extracted/test/images_test"
CLASSES_FILE = "/workspace/data/s3/classes.txt"
WRITABLE_RESULTS_DIR = "/results"   # 必须是可写的绑定，不是图像 CWD
```

对于本地 Docker，下载 S3 存档，先解压它们，然后将 `dataset.*.images_dir` 指向解压后的类根文件夹。不要直接将 `images_train.tar.gz`、`images_val.tar.gz` 或 `images_test.tar.gz` 传递给本地 Docker 规范；技能元数据声明这些输入为文件夹。

**train (强制数据源):**
```python
{
    "train.num_epochs": 2,
    "train.validation_interval": 2,
    "train.checkpoint_interval": 2,
    "train.num_gpus": 1,
    "dataset.train_dataset.images_dir": TRAIN_IMAGES_DIR,
    "dataset.classes_file": CLASSES_FILE,
    "dataset.val_dataset.images_dir": VAL_IMAGES_DIR,
    "dataset.root_dir": WRITABLE_RESULTS_DIR,
}
```

`dataset.root_dir` 对**train**是强制性的，而不仅仅是export。`CLDataset` 在设置期间会将 `classes.txt` 写入 `root_dir`，因此它必须指向可写的绑定挂载（结果挂载是自然的选择）。规范模板将其默认设置为 `''`，这使得写入落在容器工作目录中——在根容器下成功，但在任何降级到非根用户的运行者下失败：

```
PermissionError: [Errno 13] Permission denied: 'classes.txt'
  .../classification_pyt/dataloader/dataset.py, in CLDataset.__init__
```

本地 Docker 启动器在存在可写结果绑定时使用主机 UID:GID，因此非根训练会触发此问题，除非设置了 `dataset.root_dir`。

**export (强制数据源):**
```python
{
    "export.input_height": 224,
    "export.input_width": 224,
    "dataset.root_dir": "/workspace/data/extracted",
}
```

**gen_trt_engine:**
```python
{
    "gen_trt_engine.tensorrt.data_type": "fp16",
}
```

**inference (强制数据源):**
```python
{
    "dataset.batch_size": 1,
    "dataset.val_dataset.images_dir": VAL_IMAGES_DIR,
    "dataset.classes_file": CLASSES_FILE,
    "dataset.test_dataset.images_dir": TEST_IMAGES_DIR,
}
```

**distill (强制数据源):**
```python
{
    "dataset.train_dataset.images_dir": TRAIN_IMAGES_DIR,
    "dataset.classes_file": CLASSES_FILE,
    "dataset.val_dataset.images_dir": VAL_IMAGES_DIR,
    "train.optim.policy": "step",
}
```

**evaluate (强制数据源):**
```python
{
    "dataset.val_dataset.images_dir": VAL_IMAGES_DIR,
    "dataset.classes_file": CLASSES_FILE,
    "dataset.test_dataset.images_dir": TEST_IMAGES_DIR,
}
```

**quantize (强制数据源):**
```python
{
    "dataset.train_dataset.images_dir": TRAIN_IMAGES_DIR,
    "dataset.classes_file": CLASSES_FILE,
    "dataset.val_dataset.images_dir": VAL_IMAGES_DIR,
    "dataset.quant_calibration_dataset.images_dir": TRAIN_IMAGES_DIR,
}
```
## Eval 数据集

可选。验证图像与训练图像一起作为单独的 tar 提供。
对于不提供单独 `images_test.tar.gz` 的小型 smoke 数据集，将 `dataset.test_dataset.images_dir` 设置为验证存档，以便 evaluate 和 inference 仍然执行检查点交接。

## 重要参数

- **dataset.num_classes**: 类别数量。默认 20。必须与图像 tarball 中的子目录数量匹配。
- **model.backbone.type**: 默认 fan_small_12_p4_hybrid。支持的主干网络及其头 in_channels（来自 model_params_mapping.py）：FAN: fan_tiny, fan_small_12_p4_hybrid, fan_base_16_p4_hybrid, fan_large_16_p4_hybrid。GCViT: gcvit_tiny 到 gcvit_large。FasterViT: fastervit_0 到 fastervit_6。ViT/EVA/DINO: vit_large_patch14_dinov2, eva02_large_patch14, 等。SigLIP-CLIPA: ViT-H-14-SigLIP-CLIPA-224, 等。某些主干网络需要非默认输入分辨率（384、512、768）。
- **dataset.classes_file**: 列出类别名称的 classes.txt 路径。
- **train.optim.lr**: 学习率。默认 6e-5。
- **dataset.img_size**: 输入图像大小。默认 224。
- **dataset.batch_size**: 每个GPU的批处理大小。默认 8。

## 多 GPU / 多节点

**启动方法：** Lightning 管理的（单个 `python` 进程，Lightning 生成工作进程）。

| 规范键 | 描述 | 默认 |
|---|---|---|
| `train.num_gpus` | GPU 数量 | 1 |
| `train.gpu_ids` | GPU 设备索引 | [0] |
| `train.num_nodes` | 节点数量 | 1 |

- 多 GPU 策略：`ddp_find_unused_parameters_true`
- 不支持 fsdp

**多节点环境变量**（由编排器设置）：`WORLD_SIZE`、`NODE_RANK`、`MASTER_ADDR`、`MASTER_PORT`、`NUM_GPU_PER_NODE`。

## 硬件

最少 1 个 GPU(s)，推荐 2 个 GPU(s)。每个 GPU 至少 16GB+（V100 或 A100）VRAM。分类通常比较轻量级。大多数主干网络在 224x224 大小下可以很好地适应 16GB GPU，批处理大小为 8。

## 错误模式

**CUDA 内存不足**：减少 batch_size 或使用更小的主干网络。

**num_classes 不匹配**：确保 `dataset.num_classes` 与图像 tarball 中的实际类目录数量和 classes.txt 匹配。

**空类目录**：classes.txt 中的每个类都必须在相应的子目录中至少有一个图像。

**Distill 调度器默认值**：捆绑的 distill 模板和模式使用 `train.optim.policy: step`。除非容器实现更新，否则保留 distill 规范的此设置；7.0 PyT distiller 对 `train.optim.policy: linear` 不分配调度器间隔。

**检查点交接**：训练生成 `model_epoch_*.pth` 检查点和 `classifier_model_latest.pth` 符号链接。对于 evaluate、inference、export、quantize、distill 和 resume，通过 SDK 解析器选择预期的检查点；仅在用户明确请求最新时使用最新符号链接。

## 规范参数 / 父模型 推理

特定于模型的推理映射属于此 MD 文件，而不是 `config.json`。生成的运行器应在此部分读取并使用 SDK 辅助程序应用映射，然后再 `create_job()`。这反映了旧的微服务 `infer_params.py` 流程。

来自 TAO Core `classification_pyt.config.json` 的推理映射：

| 操作 | 规范字段 | 推理函数 | 含义 |
|---|---|---|---|
| distill | `distill.pretrained_teacher_model_path` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| distill | `results_dir` | `output_dir` | 当前作业结果目录 |
| evaluate | `evaluate.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| evaluate | `results_dir` | `output_dir` | 当前作业结果目录 |
| export | `export.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| export | `export.onnx_file` | `create_onnx_file` | 输出 ONNX 路径 |
| export | `results_dir` | `output_dir` | 当前作业结果目录 |
| gen_trt_engine | `gen_trt_engine.onnx_file` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| gen_trt_engine | `gen_trt_engine.trt_engine` | `create_engine_file` | 输出 TensorRT 引擎路径 |
| gen_trt_engine | `results_dir` | `output_dir` | 当前作业结果目录 |
| inference | `inference.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| inference | `inference.trt_engine` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| inference | `results_dir` | `output_dir` | 当前作业结果目录 |
| quantize | `quantize.model_path` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| quantize | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `model.backbone.pretrained_backbone_path` | `ptm_if_no_resume_model` | 当不存在恢复检查点时 PTM |
| train | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `train.pretrained_model_path` | `ptm_if_no_resume_model` | 当不存在恢复检查点时 PTM |
| train | `train.resume_training_checkpoint_path` | `resume_model` | 从当前作业结果文件夹推断的模型文件 |

对于 `parent_model` 或 `parent_model_folder`，将上游训练/export/AutoML 子作业 ID 作为 `parent_job_id` 传递。SDK 列出父结果文件夹，过滤检查点工件，并返回选定的模型文件或文件夹。不要将这些映射重新添加到 `config.json`，也不要修补生成的运行器脚本以猜测检查点路径。

## 部署

- [tao-deploy-image-classification](references/tao-deploy-image-classification.md)
