# Visual ChangeNet

> **独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

Visual ChangeNet 是 TAO Toolkit 的一个模型，用于视觉检查和缺陷检测。它支持两个任务：

- **分类** — 使用共享主干（C-RADIO ViT）和可学习差异模块的 siamese 风格架构进行二进制图像分类。比较图像对，将缺陷分类为 PASS/NO_PASS。
- **分割** — 使用 ViT-Large NVDINOv2 主干进行像素级变化分割。比较前后图像对，生成二进制变化掩码。

分类支持公共 C-RADIOv2-B 主干和六个冻结的 DINOv3 变体。选择 DINOv3 之前，请阅读 `references/dinov3-backbones.md`；它包含确切的变体映射、冻结要求、Hugging Face 访问规则和本地预览覆盖。对于 C-RADIO，使用捆绑的 `scripts/stage_backbone.py` 并在 `references/local-docker.md` 中挂载。

分割规格使用 `model.backbone.type: vit_large_nvdinov2` 和 NVDINOv2 检查点系列。保持检查点架构与主干类型一致：`NV_DINOV2_518_16_256.ckpt` 兼容打包的分割模板，但不能与 `fan_small_12_p4_hybrid` 一起使用。如果您切换到不同的分割主干，请使用匹配的检查点，或者将 `model.backbone.pretrained_backbone_path` 留空以进行默认初始化。

## 数据类模式

生成的 TAO Core 模式打包在 `schemas/<action>.schema.json` 中，`schemas/manifest.json` 列出可用动作。每个生成的模式也从模式的顶层 `default` 字段发出 `references/spec_template_<action>.yaml`。AutoML 启用声明在 `references/skill_info.yaml` 的模型层通过 `automl_enabled`。可运行的 AutoML 仍然需要 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 存在并解析。使用打包的训练模式进行 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖关系和常用参数。不要期望 `~/tao-core` 在运行时；维护者在打包技能库之前重新生成模式和模板。

## 训练动作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，请阅读 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将短语如“关闭 AutoML”、“禁用 AutoML”、“无 HPO”或“纯训练”视为仅对此运行 `automl_policy: off`。当 `automl_policy: on`、`automl_enabled: true`，并且都打包了 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 时，默认通过此模型的 `skill_dir` 路由训练动作 `tao-skill-bank:tao-run-automl`。保留工作流/应用程序覆盖的数据集、规格、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时使用直接模型训练；在缺失模式的案例中，报告此模型启用 AutoML 但不可运行，直到生成模式。

检查点保留是一个编排策略，而不是 HPO 参数。两个打包的训练模板默认 `train.checkpointer.enable_topk` 和 `train.checkpointer.replace_periodic` 为 `false`，保留由 `train.checkpoint_interval` 控制的周期性保存。当启用 AutoML 检查点保留时，AutoML 运行器将两个标志设置为 `true`，以 `min` 模式监控 `val_loss` 并使用 `save_top_k: 1`；这替换了周期性序列为单个最佳检查点。当禁用 AutoML 检查点保留时，请保留有界保留覆盖，以便保留周期性检查点行为。

此模型技能声明的非训练动作（`evaluate`、`inference`、`export`、`quantize`、`segment_evaluate` 和 `segment_inference`）保留在此模型技能中。在 `schemas/manifest.json` 中打包匹配条目之前，不要将 `segment_export` 或 `segment_quantize` 呈现为可运行的父技能动作。修剪和重新训练未在当前父 `references/skill_info.yaml` 中声明；除非元数据扩展了匹配的动作连接和模式，否则不要将它们呈现为可运行的父技能动作。每次运行的 `automl_policy` 覆盖不会更改模型元数据。

对于 TAO Deploy TensorRT 动作（`gen_trt_engine`、TensorRT `evaluate` 和 TensorRT `inference` 用于分类和分割变体），请先阅读 `references/tao-deploy-visual-changenet.md`。部署规格模板位于此技能的 `references/` 文件夹中，前缀为 `spec_template_deploy_*.yaml`。部署需要一个作为 `parent_model` 导出的 ONNX 资产。如果不存在 ONNX 资产，并且主技能没有暴露导出动作，则报告部署被阻塞，而不是编造资产。

## 训练要求

Visual ChangeNet 有两个不同的任务模式，具有不同的数据集类型和数据源结构。

### 分类

- **数据集类型：** visual_changenet_classify
- **格式：** 默认
- **接受的数据集意图：** 训练、评估、测试、校准
- **监控指标：** val_loss
- **独立评估指标：** `test_acc`（同时发出 `test_fpr`、`test_fnr` 和 `defect_acc`）。AutoML 必须按训练 `val_loss` 对推荐进行排序；仅使用 `test_acc` 来验证所选检查点是否加载并成功评估。不要期望评估动作发出 `val_loss`。

#### 每个动作的数据集要求（分类）

下方的 `quantize` 和 `gen_trt_engine` 行仅描述 TAO 规格数据要求。除非在 `references/skill_info.yaml` 或 `deploy/skill_info.yaml` 中声明了相应的动作，否则它们不是父技能动作。

| 动作 | 规格键 | 源 | 文件 | 列表？ |
|---|---|---|---|---|
| train | dataset.classify.train_dataset.images_dir | train_datasets | images.tar.gz | 否 |
| train | dataset.classify.train_dataset.csv_path | train_datasets | dataset.csv | 否 |
| train | dataset.classify.validation_dataset.images_dir | eval_dataset | images.tar.gz | 否 |
| train | dataset.classify.validation_dataset.csv_path | eval_dataset | dataset.csv | 否 |
| quantize | dataset.classify.train_dataset.images_dir | train_datasets | images.tar.gz | 否 |
| quantize | dataset.classify.train_dataset.csv_path | train_datasets | dataset.csv | 否 |
| quantize | dataset.classify.validation_dataset.images_dir | eval_dataset | images.tar.gz | 否 |
| quantize | dataset.classify.validation_dataset.csv_path | eval_dataset | dataset.csv | 否 |
| quantize | dataset.classify.quant_calibration_dataset.images_dir | train_datasets | images.tar.gz | 否 |
| evaluate | dataset.classify.validation_dataset.images_dir | eval_dataset | images.tar.gz | 否 |
| evaluate | dataset.classify.validation_dataset.csv_path | eval_dataset | dataset.csv | 否 |
| evaluate | dataset.classify.test_dataset.images_dir | eval_dataset | images.tar.gz | 否 |
| evaluate | dataset.classify.test_dataset.csv_path | eval_dataset | dataset.csv | 否 |
| inference | dataset.classify.infer_dataset.images_dir | inference_dataset | images.tar.gz | 否 |
| inference | dataset.classify.infer_dataset.csv_path | inference_dataset | dataset.csv | 否 |
| gen_trt_engine | gen_trt_engine.tensorrt.calibration.cal_image_dir | calibration_dataset | images.tar.gz | 是 |

### 分割

- **数据集类型：** visual_changenet_segment
- **格式：** 默认
- **接受的数据集意图：** 训练、校准
- **监控指标：** val_loss

分割使用成对目录结构（`A/`、`B/`、`list/`、`label/`）而不是 CSV + 图像。`root_dir` 规格键指向包含所有四个子目录的顶层目录。

**每个数据集必需的文件：** `A.tar.gz`、`B.tar.gz`、`list.tar.gz`、`label.tar.gz`

#### 每个动作的数据集要求（分割）

下方的 `quantize` 和 `gen_trt_engine` 行仅描述 TAO 规格数据要求。除非在 `references/skill_info.yaml` 或 `deploy/skill_info.yaml` 中声明了相应的动作，否则它们不是父技能动作。

| 动作 | 规格键 | 源 | 文件 | 列表？ |
|---|---|---|---|---|
| train | dataset.segment.root_dir | train_datasets | (根目录) | 否 |
| quantize | dataset.segment.root_dir | train_datasets | (根目录) | 否 |
| quantize | dataset.segment.quant_calibration_dataset.images_dir | train_datasets | (根目录) | 否 |
| evaluate | dataset.segment.root_dir | train_datasets | (根目录) | 否 |
| inference | dataset.segment.root_dir | train_datasets | (根目录) | 否 |
| gen_trt_engine | dataset.segment.root_dir | train_datasets | (根目录) | 否 |
| gen_trt_engine | gen_trt_engine.tensorrt.calibration.cal_image_dir | calibration_dataset | images.tar.gz | 是 |

### 典型规格覆盖

数据源覆盖对每个动作都是**强制性的** — 代理必须从上表中的“每个动作的数据集要求”表格构建数据源路径，并将它们包含在 `spec_overrides` 中。

```python
S3_TRAIN = "s3://bucket/data/train"
S3_EVAL = "s3://bucket/data/eval"
```

**train (classify, 强制性数据源):**
```python
{
    "train.num_epochs": 30,
    "train.checkpoint_interval": 10,
    "train.validation_interval": 10,
    "train.num_gpus": 1,
    "train.use_distributed_sampler": False,
    "train.sync_batchnorm": False,
    "dataset.classify.train_dataset.images_dir": f"{S3_TRAIN}/images.tar.gz",
    "dataset.classify.train_dataset.csv_path": f"{S3_TRAIN}/dataset.csv",
    "dataset.classify.validation_dataset.images_dir": f"{S3_EVAL}/images.tar.gz",
    "dataset.classify.validation_dataset.csv_path": f"{S3_EVAL}/dataset.csv",
}
```

**train (segment, 强制性数据源):**
```python
{
    "train.num_epochs": 30,
    "train.checkpoint_interval": 10,
    "train.validation_interval": 10,
    "train.num_gpus": 1,
    "train.use_distributed_sampler": False,
    "train.sync_batchnorm": False,
    "dataset.segment.root_dir": f"{S3_TRAIN}",
}
```

**export (classify):**
```python
{
    "export.input_height": 896,
    "export.input_width": 224,
}
```

**export (segment):**
```python
{
    "export.input_height": 224,
    "export.input_width": 224,
}
```

**quantize (classify, 强制性数据源):**
```python
{
    "dataset.classify.train_dataset.images_dir": f"{S3_TRAIN}/images.tar.gz",
    "dataset.classify.train_dataset.csv_path": f"{S3_TRAIN}/dataset.csv",
    "dataset.classify.validation_dataset.images_dir": f"{S3_EVAL}/images.tar.gz",
    "dataset.classify.validation_dataset.csv_path": f"{S3_EVAL}/dataset.csv",
    "dataset.classify.quant_calibration_dataset.images_dir": f"{S3_TRAIN}/images.tar.gz",
}
```

**evaluate (classify, 强制性数据源):**
```python
{
    "dataset.classify.validation_dataset.images_dir": f"{S3_EVAL}/images.tar.gz",
    "dataset.classify.validation_dataset.csv_path": f"{S3_EVAL}/dataset.csv",
    "dataset.classify.test_dataset.images_dir": f"{S3_EVAL}/images.tar.gz",
    "dataset.classify.test_dataset.csv_path": f"{S3_EVAL}/dataset.csv",
}
```

**inference (classify, 强制性数据源):**
```python
{
    "dataset.classify.infer_dataset.images_dir": f"{S3_EVAL}/images.tar.gz",
    "dataset.classify.infer_dataset.csv_path": f"{S3_EVAL}/dataset.csv",
}
```

**gen_trt_engine (classify, 强制性数据源):**
```python
{
    "gen_trt_engine.tensorrt.calibration.cal_image_dir": [f"{S3_TRAIN}/images.tar.gz"],
}
```

**quantize (segment, 强制性数据源):**
```python
{
    "dataset.segment.root_dir": f"{S3_TRAIN}",
    "dataset.segment.quant_calibration_dataset.images_dir": f"{S3_TRAIN}",
}
```

**evaluate (segment, 强制性数据源):**
```python
{
    "dataset.segment.root_dir": f"{S3_TRAIN}",
}
```

**inference (segment, 强制性数据源):**
```python
{
    "dataset.segment.root_dir": f"{S3_TRAIN}",
}
```

**gen_trt_engine (segment, 强制性数据源):**
```python
{
    "dataset.segment.root_dir": f"{S3_TRAIN}",
    "gen_trt_engine.tensorrt.calibration.cal_image_dir": [f"{S3_TRAIN}/images.tar.gz"],
}
```
## 通过本地 Docker 运行

使用固定的 TAO pyt 镜像并直接调用 `visual_changenet <train|evaluate|inference|export|quantize>`。需要 `--shm-size=8g`，C-RADIO 的 `.safetensors` 必须挂载到 `/data/pretrained_models/C-RADIOv2_B.safetensors`，并且可以覆盖检查点/结果目录。有关完整的 `docker run` 命令、挂载和覆盖，请参阅 `references/local-docker.md`。

## 任务

### 分类（默认）

使用动作：`train`、`evaluate`、`inference`。默认模板：`references/spec_template_train.yaml`。`evaluate` / `inference` 需要从先前的 7.1 `train` 下的 `results_dir` 获取检查点——在 NGC 上**没有预训练的 7.1 分类检查点**（7.0 时代的 `visual_changenet_nvpcb_trainable_v1.0` 在 7.1 上加载失败，出现 `radio.*` `KeyError`）。在一个新工作区中，请先从公共主干进行训练；不要尝试下载 NGC `full_model` 分类检查点，也不要硬编码 NGC 组织。

### 分割

使用技能动作名称 `segment_train`、`segment_evaluate` 和 `segment_inference`。直接运行本地 Docker 时，请在规格中使用 `task: segment` 运行 TAO CLI 子命令 `train`、`evaluate` 和 `inference`。模式驱动的动作模板是 `references/spec_template_segment_train.yaml`、`references/spec_template_segment_evaluate.yaml` 和 `references/spec_template_segment_inference.yaml`；紧凑的直接-Docker 示例模板是 `references/spec_template_segment.yaml`。

分割需要编译自定义 CUDA 操作（`MultiScaleDeformableAttention`）在第一次运行时，这需要约 5 分钟。ViT 适配器主干使用这些进行多尺度特征提取。

分割的数据集结构与分类不同——使用成对目录（`A/`、`B/`、`list/`、`label/`），而不是 CSV 文件。请参阅 `dataset.segment.root_dir` 中的默认值。

## 数据格式

分类需要一个 4 列 CSV（`input_path,golden_path,label,object_name`）加上一个图像目录；分割使用 `dataset.segment.root_dir` 下的成对目录结构（`A/`、`B/`、`list/`、`label/`）而不是 CSV。`image_ext` 字段（默认 `.jpg`）必须与实际文件扩展名匹配；如果图像是 `.png`，请设置 `dataset.classify.image_ext: .png`。多光源输入通过 `dataset.classify.input_map`（每个光源名称映射到通道索引）配置，`dataset.classify.num_input` 设置与之匹配。有关每个字段的输入表格（分类训练/评估/推理、分割）、CSV 列语义、光照/路径连接约定、分割目录布局以及 `input_map`/`grid_map` 示例，请参阅 `references/data-formats.md`。

## 预检：验证分类数据集（每个分类运行前强制执行）

在启动分类 `train`、`evaluate` 或 `inference` 工作之前，验证 CSV，以便一个格式错误的数
据集在主机上 <1 秒内失败，而不是在 GPU 容器中运行数分钟后（或对于单类训练集，仅在写入检查点后）。运行：

```bash
python3 skills/models/tao-train-visual-changenet/scripts/validate_vcn_dataset.py \
  --csv        <abs path to dataset.csv> \
  --images-dir <abs path to images dir> \
  --mode       train \
  --batch-size <dataset.classify.batch_size> --num-gpus <train.num_gpus>
# --mode: train | evaluate | inference
```

退出 `0` → 启动。退出 `2` → **修复数据集，不要启动。** 脚本拒绝绝对 CSV 路径、扁平文件名（其中需要每个样本目录）、单类训练集和大于数据集的批处理。有关每个检查的合同和 `--light` / `--image-ext` 选项，请参阅 `references/data-formats.md`。

## 重要参数

关键旋钮包括 `train.validation_interval`（默认 50，必须 ≤ num_epochs）、`train.checkpoint_interval`（默认 200，必须 ≤ num_epochs 当周期性检查点激活时）、`train.num_epochs`（默认 100）、`model.classify.eval_margin`（默认 0.3，精确率/召回率阈值）、`model.classify.train_margin_euclid`（默认 2.0）、`model.classify.embedding_vectors`（默认 5）、`dataset.classify.batch_size`（默认 16，必须 > 1）、`dataset.classify.fpratio_sampling`（默认 0.25）和 `train.classify.cls_weight`（默认 [1.0, 10.0]）。`train.checkpointer` 字段是固定的生命周期控制，不是 HPO 搜索参数。硬件：最低 1 个 GPU，16GB+ VRAM，推荐 8 个 GPU（DDP）；不要设置 `gpu_spec_key`（GPU 数量由 TAO 内部管理），`num_nodes`（默认 1）控制多节点。有关每个参数的完整指导和硬件详情，请参阅 `references/tuning-parameters.md`。

## 错误模式

对于检查点未找到、CSV 格式不匹配、图像扩展名不匹配、OOM、评估准确率低、对比损失 `AssertionError`、评估/推理时检查点加载键不匹配、非收敛、分割仅主干维度不匹配、`MultiScaleDeformableAttention` `OSError`、Lightning `MisconfigurationException`、`ModuleNotFoundError: nvidia_tao_pytorch` 和 epoch 默认值，请参阅 `references/troubleshooting.md` 以获取完整的症状和修复列表。

## 规格参数 / 父模型推理

模型特定的父模型映射在 `references/skill_info.yaml` 的 `spec_params` 下声明，因此代理在启动工作之前解析检查点，而不是猜测文件名。对于 `parent_model` 或 `parent_model_folder`，将上游训练/导出/AutoML 子工作 ID 作为父工作 ID 传递；列出父结果文件夹，过滤检查点资产，并选择解析的模型文件或文件夹。有关每个动作的规格字段到推理函数的映射表，请参阅 `references/parent-model-inference.md`。

## 部署

- [tao-deploy-visual-changenet](references/tao-deploy-visual-changenet.md)
