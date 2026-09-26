# SegFormer

> **独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

用于语义分割的 SegFormer。轻量级基于 Transformer 的架构，具有分层特征提取。适用于实时分割任务。

设置 `model.backbone.pretrained_backbone_path` 用于主干权重。

对于 TAO 部署 TensorRT 操作 (`gen_trt_engine`、TensorRT `evaluate` 和 TensorRT `inference`)，请先阅读 `references/tao-deploy-segformer.md`。部署规范模板位于此技能的 `references/` 文件夹中，以 `spec_template_deploy_*.yaml` 为前缀。

## 数据类模式

生成的 TAO Core 模式打包在 `schemas/<action>.schema.json` 中，`schemas/manifest.json` 列出可用操作。每个生成的模式也从模式的顶层 `default` 字段发出 `references/spec_template_<action>.yaml`。AutoML 启用通过 `references/skill_info.yaml` 中的模型层 `automl_enabled` 声明。运行 AutoML 需要存在并解析 `schemas/<action>.schema.json` 和 `references/spec_template_<action>.yaml`。使用打包的选定操作的规范进行 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖关系和常用参数。不要期望运行时 `~/tao-core`；维护者在打包技能库之前会重新生成模式/模板。

## 训练操作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，请阅读 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将短语如 "关闭 AutoML"、"禁用 AutoML"、"无 HPO" 或 "纯训练" 视为 `automl_policy: off` 仅对此运行。当 `automl_policy: on`、`automl_enabled: true`，并且都打包了 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 时，默认通过 `tao-skill-bank:tao-run-automl` 将训练操作路由到此模型的 `skill_dir`。保留工作流/应用程序覆盖的数据集、规范、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时使用直接模型训练；在缺失模式的案例中，在生成模式之前报告此模型启用 AutoML 但不可运行。

非训练操作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每次运行的 `automl_policy` 覆盖不会更改模型元数据。

## 支持的操作

打包的 SegFormer PyT CLI 支持 `train`、`evaluate`、`export`、`inference`、`quantize` 和 `default_specs`。此模型技能公开 `train`、`evaluate`、`export`、`inference` 和 `quantize`；恢复/重新训练通过 `train` 与 `train.resume_training_checkpoint_path` 执行。

父 PyT CLI 不公开 `gen_trt_engine`。使用 `models/segformer/deploy` 进行 TensorRT 引擎生成、TensorRT 评估和 TensorRT 推理。

## 训练要求

- **数据集类型：** 分割
- **格式：** unet
- **AutoML 训练指标：** `val_miou`（最大化）。
- **独立评估指标：** `test_miou`。使用训练状态 `val_miou` 进行 AutoML 排名，仅使用评估器的 `test_miou` 进行检查点验证。

### 每个操作的 数据集 要求

| 操作 | Spec Key | 来源 | 文件 | 列表？ |
|---|---|---|---|---|
| evaluate | dataset.segment.root_dir | eval_dataset | 包含 `images/<split>` 和 `masks/<split>` 的提取根目录 | 否 |
| export | dataset.segment.root_dir | train_datasets | 包含 `images/<split>` 和 `masks/<split>` 的提取根目录 | 否 |
| inference | dataset.segment.root_dir | inference_dataset | 包含 `images/<split>` 和 `masks/<split>` 的提取根目录 | 否 |
| quantize | dataset.segment.root_dir | train_datasets | 包含 `images/<split>` 和 `masks/<split>` 的提取根目录 | 否 |
| quantize | dataset.segment.quant_calibration_dataset.images_dir | calibration_dataset | 提取的图像目录 | 否 |
| train | dataset.segment.root_dir | train_datasets | 包含 `images/<split>` 和 `masks/<split>` 的提取根目录 | 否 |

### 典型 Spec 覆盖

数据源覆盖对每个操作都是**强制性的**——代理必须根据上表中的“每个操作的 数据集 要求”构建数据源路径，并将其包含在 `spec_overrides` 中。

```python
SEG_TRAIN_ROOT = "/data/segformer/train"
SEG_EVAL_ROOT = "/data/segformer/eval"
SEG_INFER_ROOT = "/data/segformer/infer"
CAL_IMAGES = f"{SEG_TRAIN_ROOT}/images/train"
```

**train（强制数据源）：**
```python
{
    "train.num_gpus": 1,
    "train.num_epochs": 10,
    "train.checkpoint_interval": 10,
    "train.validation_interval": 10,
    "dataset.segment.batch_size": 4,
    "dataset.segment.root_dir": SEG_TRAIN_ROOT,
}
```

**evaluate（强制数据源）：**
```python
{
    "evaluate.batch_size": 4,
    "dataset.segment.root_dir": SEG_EVAL_ROOT,
    "evaluate.checkpoint": CHECKPOINT,
}
```

**inference（强制数据源）：**
```python
{
    "dataset.segment.batch_size": 1,
    "dataset.segment.root_dir": SEG_INFER_ROOT,
    "inference.checkpoint": CHECKPOINT,
}
```

**export（强制数据源）：**
```python
{
    "dataset.segment.root_dir": SEG_TRAIN_ROOT,
    "export.checkpoint": CHECKPOINT,
    "export.input_height": 256,
    "export.input_width": 256,
    "export.onnx_file": ONNX_FILE,
}
```

**quantize（强制数据源）：**
```python
{
    "dataset.segment.root_dir": SEG_TRAIN_ROOT,
    "dataset.segment.quant_calibration_dataset.images_dir": CAL_IMAGES,
    "quantize.model_path": CHECKPOINT,
}
```

如果源数据集以单独的 `images/*.tar.gz` 和 `masks/*.tar.gz` 存档交付，请在启动前提取它们，以便 `root_dir` 包含 `images/train`、`images/val`、`images/test`、`masks/train` 和 `masks/val` 等目录。不要将 `dataset.segment.root_dir` 指向仍只包含 tarball 的存档 staging 文件夹。

## 评估数据集

可选。验证数据通常是根目录结构的一部分。

## 重要参数

- **dataset.segment.num_classes**：分割类的数量。默认 2（二进制）。必须与您的掩码注释中的类数匹配。
- **model.backbone.type**：默认 fan_small_12_p4_hybrid。支持包括 FAN 变体、SegFormer MIT 变体和其他。
- **dataset.segment.root_dir**：分割数据集的根目录。
- **dataset.segment.img_size**：输入图像大小。默认 256。增加以实现更精细的分割，但会消耗更多内存。
- **train.optim.lr**：学习率。默认 6e-5。
- **model.freeze_backbone**：是否在训练期间冻结主干。对于有限数据集的微调很有用。
- **dataset.segment.batch_size**：每 GPU 批次大小。默认 8。
- **dataset.segment.label_transform**：当不需要标签转换时，使用字符串 `"None"`。不要将此设置为 JSON/YAML null；严格的模式合并将此字段视为字符串枚举。
- **dataset.segment.palette**：对于灰度掩码，为每个 RGB 条目使用一个整数，例如 `rgb: [85]`。保留数据集的实际标签 ID 和类名，而不是规范化它们，除非用户明确要求转换。

## 多 GPU / 多节点

**启动方法：** Lightning 管理的（单个 `python` 进程，Lightning 生成工作进程）。

| Spec Key | 描述 | 默认 |
|----------|-------------|---------|
| `train.num_gpus` | GPU 数量 | 1 |
| `train.gpu_ids` | GPU 设备索引 | [0] |
| `train.num_nodes` | 节点数量 | 1 |
| `train.sync_batchnorm` | 跨 GPU 同步 BN | 可配置 |
| `train.use_distributed_sampler` | 使用分布式采样器 | 可配置 |

- 多 GPU 策略：`ddp_find_unused_parameters_true`
- 不支持 fsdp

**多节点环境变量**（由协调器设置）：`WORLD_SIZE`、`NODE_RANK`、`MASTER_ADDR`、`MASTER_PORT`、`NUM_GPU_PER_NODE`。

## 硬件

至少 1 个 GPU，推荐 2 个 GPU。每个 GPU 16GB+（V100 或 A100）VRAM。SegFormer 相对轻量级。默认 img_size=256 对内存友好。增加 img_size 以实现更高分辨率，但会消耗更多内存和速度。

## 错误模式

**CUDA 内存不足**：减少 batch_size 或 img_size。SegFormer 内存随图像大小呈二次方增长。

**num_classes 不匹配**：确保 `dataset.segment.num_classes` 与您的掩码注释中的实际类数匹配。

**TensorBoard 不支持分割训练**：保持 `train.tensorboard.enabled: false`。SegFormer 训练入口点断言 TensorBoard 可视化不适用于分割，因此不要启用 TensorBoard 仅为了提取 AutoML 指标；使用日志解析或训练后评估器。

**AutoML 指标提取**：SegFormer 训练状态文件报告 `val_miou` 以及 `val_loss`、`val_acc` 和其他验证 KPI。默认 AutoML 训练启动必须以 `direction: maximize` 优化 `val_miou`；不要在默认模型调用中优化 `val_loss`。

对于 AutoML 或长分割扫描，首先从 `results_dir/train/status.json` 读取 `val_miou`。如果包装器报告终端失败，但结构化状态文件达到配置的训练预算并包含有限的 `val_miou`，则报告恢复的指标并注明包装器失败，而不是丢弃测量值。

对于高分辨率的自定义分割目标，保持数据集路径为每次运行输入。不要将客户/用户特定的根添加到此可重用技能。当用户请求固定全预算搜索时，请记住括号算法（`asha`、`bohb`、`dehb`、`hyperband`、`hyperband_es`、`pbt`）可能会有意降低某些建议的 `train.num_epochs`；如果每个建议都必须运行完整的 epoch 数，请使用贝叶斯/BFBO 或锁定预算。

**检查点交接**：对于 evaluate/export/inference/quantize/resume，使用最佳 AutoML 子作业的 `results_dir/train/` 文件夹上的检查点解析器，并选择适当的 `model_epoch_*.pth` 检查点，例如 `model_epoch_000_step_00010.pth`。SegFormer 也可能写入 `segformer_model_latest.pth`，但只有在调用者明确请求最新时才使用。保留 `dataset.segment.num_classes`、`dataset.segment.img_size` 和 `dataset.segment.root_dir` 覆盖以供下游操作使用。

**恢复/重新训练检查点**：恢复使用 `train.resume_training_checkpoint_path`。传递来自先前训练输出的确切解析检查点，而不是猜测 `model.pth` 路径。恢复的单 epoch 运行应在新的结果目录中生成下一个检查点，例如 `model_epoch_001_step_00020.pth`。

**导出 / TensorRT 形状对齐**：保持 `export.input_height` 和 `export.input_width` 与 `dataset.segment.img_size` 对齐，除非训练模型和部署规范已在其他分辨率下验证。打包的全新安装路径在 `256x256` 下验证，与默认 SegFormer 数据集和部署模板匹配。

**父 `segformer gen_trt_engine` 被 PyT CLI 拒绝**：在验证的 7.0.0 PyT 容器中，`segformer gen_trt_engine` 不是有效的父模型子任务。使用 SegFormer 部署工作流（`references/tao-deploy-segformer.md`）进行 TensorRT 引擎生成、TensorRT 评估和 TensorRT 推理。

## Spec 参数 / 父模型推理

特定于模型的推理映射属于此 MD 文件，而不是 `config.json`。生成的运行者应在此部分读取此节并使用 SDK 帮助程序在 `create_job()` 之前应用映射。这类似于旧的微服务 `infer_params.py` 流程。

来自 TAO Core `segformer.config.json` 的推理映射：

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
| train | `model.backbone.pretrained_backbone_path` | `ptm_if_no_resume_model` | 当没有恢复检查点时 PTM |
| train | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `train.pretrained_model_path` | `ptm_if_no_resume_model` | 当没有恢复检查点时 PTM |
| train | `train.resume_training_checkpoint_path` | `resume_model` | 从当前作业结果文件夹推断的模型文件 |

对于 `parent_model` 或 `parent_model_folder`，将上游训练/导出/AutoML 子作业 ID 作为 `parent_job_id` 传递。SDK 列出父结果文件夹，过滤检查点工件，并返回选定的模型文件或文件夹。不要将这些映射重新添加到 `config.json`，也不要修补生成的运行者脚本以猜测检查点路径。

## 部署

- [tao-deploy-segformer](references/tao-deploy-segformer.md)
