# CenterPose

> **独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

CenterPose 用于关键点/姿态估计。检测对象中心并回归关键点位置。用于 6-DoF 对象姿态估计。

设置 `model.backbone.pretrained_backbone_path`。

对于 TAO Deploy TensorRT 操作 (`gen_trt_engine`、TensorRT `evaluate` 和 TensorRT `inference`)，使用此技能的 `references/` 文件夹中打包的 `spec_template_deploy_*.yaml` 前缀的部署规范模板。

## 数据类模式

生成的 TAO Core 模式打包在 `schemas/<action>.schema.json` 中，`schemas/manifest.json` 列出可用操作。每个生成的模式也从模式的顶层 `default` 字段发出 `references/spec_template_<action>.yaml`。AutoML 启用声明在 `references/skill_info.yaml` 中的模型层通过 `automl_enabled`。运行 AutoML 需要操作存在 `schemas/<action>.schema.json` 和 `references/spec_template_<action>.yaml` 并解析，并使用打包的选定操作的规范进行 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖关系和常用参数。不要期望 `~/tao-core` 在运行时；维护者在打包技能库之前会重新生成模式/模板。

## 训练操作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，读取 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将短语“关闭 AutoML”、“禁用 AutoML”、“无 HPO”或“纯训练”视为仅对此运行 `automl_policy: off`。当 `automl_policy: on`、`automl_enabled: true`，并且都打包了 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 时，默认通过此模型的 `skill_dir` 将训练操作路由到 `tao-skill-bank:tao-run-automl`。保留工作流/应用程序覆盖的数据集、规范、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时才使用直接模型训练；在缺失模式的案例中，在生成模式之前报告此模型启用 AutoML 但不可运行。

非训练操作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每运行的 `automl_policy` 覆盖不会更改模型元数据。

## 训练要求

- **数据集类型：** centerpose
- **格式：** 默认
- **训练监控指标：** `val_3DIoU`、`val_2DMPE`
- **评估任务指标：** `test_3DIoU`、`test_2DMPE`
- **AutoML 指标契约：** 使用 `test_3DIoU` 与最大化方向为所需基于评估的基线，通过 `eval_fn`、最佳模型选择和最终评估的每项推荐。`val_3DIoU` 由训练发出但不是由评估操作发出，因此它仅适用于明确接受的训练代理运行而没有影响基线。

### 每个操作的 数据集 要求

| 操作 | 规范键 | 源 | 文件 | 列表？ |
|---|---|---|---|---|
| evaluate | dataset.test_data | eval_dataset | test.tar.gz | 否 |
| gen_trt_engine | gen_trt_engine.tensorrt.calibration.cal_image_dir | calibration_dataset | train.tar.gz | 是 |
| inference | dataset.inference_data | inference_dataset | val.tar.gz | 否 |
| train | dataset.train_data | train_datasets | train.tar.gz | 否 |
| train | dataset.val_data | eval_dataset | val.tar.gz | 否 |

### 典型规范覆盖

数据源覆盖对每个操作都是**强制性的** — 代理必须从上表中构建数据源路径并包含它们在 `spec_overrides` 中。

```python
TRAIN_DIR = "/path/to/extracted/train"
VAL_DIR = "/path/to/extracted/val"
TEST_DIR = "/path/to/extracted/test"
INFER_DIR = VAL_DIR
CAL_IMAGE_DIRS = ["/path/to/extracted/train/<sequence_or_image_dir>"]
```

**train (强制数据源):**
```python
{
    "train.num_epochs": 30,
    "train.checkpoint_interval": 10,
    "train.validation_interval": 10,
    "train.num_gpus": 1,
    "dataset.category": "bike",
    "dataset.batch_size": 4,
    "dataset.train_data": TRAIN_DIR,
    "dataset.val_data": VAL_DIR,
}
```

**evaluate (强制数据源):**
```python
{
    "dataset.category": "bike",
    "dataset.test_data": TEST_DIR,
}
```

**inference (强制数据源):**
```python
{
    "dataset.category": "bike",
    "dataset.inference_data": INFER_DIR,
}
```

**gen_trt_engine (强制数据源):**
```python
{
    "gen_trt_engine.tensorrt.calibration.cal_image_dir": CAL_IMAGE_DIRS,
}
```
## 评估数据集

可选。验证和测试数据集作为单独的 tarball 提供。训练写入 `val_3DIoU`/`val_2DMPE` KPI，而评估写入 `test_3DIoU`/`test_2DMPE`；不要配置基于评估的 AutoML 回调来提取以训练前缀命名的名称。

## 重要参数

- **dataset.num_classes**: 对象类别的数量。默认为 1。
- **dataset.num_joints**: 每个对象的键点数量。固定为 8（bbox 键点）。有效范围：正好为 8。
- **dataset.input_res**: 输入分辨率。固定为 512。输出分辨率固定为 128。
- **dataset.category**: 对象类别名称。默认 "cereal_box"。
- **model.backbone.model_type**: 默认 fan_small。模式选项在模式中有限制。
- **train.optim.lr**: 学习率。默认 6e-5。MultiStep 调度器，lr_steps=[90, 120]，lr_decay=0.1。
- **train.loss_config**: 丰富的损失配置，具有切换：mse_loss、obj_scale、obj_scale_uncertainty、hps_uncertainty、reg_bbox、hm_hp。权重：wh_weight=0.1，off_weight=1，hp_weight=1。
- **inference.use_pnp**: 使用 PnP 进行 6-DoF 姿态。默认为 True。需要相机内参（focal_length_x/y、principle_point_x/y）。
- **export.input_width**: 导出输入大小。固定为 512x512。opset_version=16。

## 多 GPU / 多节点

**启动方法：** Lightning 管理的（单个 `python` 进程，Lightning 生成工作进程）。

| 规范键 | 描述 | 默认 |
|---|---|---|
| `train.num_gpus` | GPU 数量 | 1 |
| `train.gpu_ids` | GPU 设备索引 | [0] |

- 策略：`auto`（Lightning 自动选择最佳策略）
- 没有 `num_nodes` 或 `distributed_strategy` 配置 — 仅单节点
- 没有 `sync_batchnorm`

## 导出 / TRT 默认值

- 导出输入：512x512（固定），opset 16
- TRT 数据类型：FP32、FP16、INT8
- TRT opt_batch_size：4，max_batch_size：8

## 硬件

至少 1 个 GPU(s)，推荐 2 个 GPU(s)。每个 GPU 16GB+ VRAM。CenterPose 根据输入分辨率和关键点数量，内存消耗中等。

## 错误模式

**num_joints 不匹配**：确保 `dataset.num_joints` 与您的标注中的关键点数量匹配。

**为本地 Docker 提取 S3 tarball**：启动套件 S3 数据打包为 `train.tar.gz`、`val.tar.gz` 和 `test.tar.gz`，但 CenterPose TAO 操作消耗提取的文件夹。提取每个存档并将 `dataset.train_data`、`dataset.val_data`、`dataset.test_data` 和 `dataset.inference_data` 设置为提取的分割目录。

**检查点交接**：CenterPose 训练写入具体检查点，如 `model_epoch_000_step_00008.pth` 和 `centerpose_model_latest.pth` 符号链接。使用 SDK/模型检查点解析器或当前作业结果的精确 epoch/step 检查点进行评估、推理、导出和恢复。仅在用户明确要求最新时使用符号链接。

**TAO Deploy 后处理器兼容性**：使用从技能的固定部署图像或选定平台解析的部署图像。成功的 `gen_trt_engine` 运行不能证明部署 `evaluate` 或 `inference` 工作；分别检查这些操作的退出代码和日志，特别是 CenterPose 后处理器错误，如 `TypeError: only 0-dimensional arrays can be converted to Python scalars`。

## 规范参数 / 父模型推理

模型特定的推理映射属于此 MD 文件，而不是 `config.json`。生成的运行者应读取此部分并使用 SDK 帮助程序在 `create_job()` 之前应用映射。

来自 TAO Core `centerpose.config.json` 的推理映射：

| 操作 | 规范字段 | 推理函数 | 含义 |
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
| gen_trt_engine | `gen_trt_engine.tensorrt.calibration.cal_cache_file` | `create_cal_cache` | 校准缓存路径 |
| gen_trt_engine | `gen_trt_engine.trt_engine` | `create_engine_file` | 输出 TensorRT 引擎路径 |
| gen_trt_engine | `results_dir` | `output_dir` | 当前作业结果目录 |
| inference | `encryption_key` | `key` | 加密密钥 |
| inference | `inference.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| inference | `inference.trt_engine` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| inference | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `encryption_key` | `key` | 加密密钥 |
| train | `model.backbone.pretrained_backbone_path` | `ptm_if_no_resume_model` | 当没有恢复检查点时 PTM |
| train | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `train.resume_training_checkpoint_path` | `resume_model` | 从当前作业结果文件夹推断的模型文件 |

对于 `parent_model` 或 `parent_model_folder`，将上游训练/导出/AutoML 子作业 ID 作为 `parent_job_id` 传递。SDK 列出父结果文件夹，过滤检查点工件，并返回选定的模型文件或文件夹。不要将这些映射重新添加到 `config.json`，也不要修补生成的运行者脚本以猜测检查点路径。

## 部署

- [tao-deploy-centerpose](references/tao-deploy-centerpose.md)
