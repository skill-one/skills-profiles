# OCRNet

> **独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

OCRNet 用于场景文本识别。识别裁剪文本区域图像中的文本内容。支持 CTC 和基于注意力的解码器。

设置 `train.pretrained_model_path` 以使用预训练的 OCR 权重。

对于 TAO Deploy TensorRT 操作 (`gen_trt_engine`、TensorRT `evaluate` 和 TensorRT `inference`)，请先阅读 `references/tao-deploy-ocrnet.md`。部署规范模板位于此技能的 `references/` 文件夹中，以 `spec_template_deploy_*.yaml` 为前缀。

## 数据类模式

生成的 TAO Core 模式打包在 `schemas/<action>.schema.json` 中，`schemas/manifest.json` 列出可用操作。每个生成的模式还会从模式顶层 `default` 字段发出 `references/spec_template_<action>.yaml`。AutoML 启用声明在 `references/skill_info.yaml` 中的模型层，通过 `automl_enabled`。运行 AutoML 需要存在并解析 `schemas/<action>.schema.json` 和 `references/spec_template_<action>.yaml`。使用打包的选定操作模式进行 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖项和常用参数。不要期望在运行时存在 `~/tao-core`；维护者在打包技能库之前会重新生成模式/模板。

## 训练操作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，请读取 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on`，并在新的启动提示中仅暴露 `on` / `off`。将类似于 "关闭 AutoML"、"禁用 AutoML"、"无 HPO" 或 "纯训练" 的短语视为仅对此运行 `automl_policy: off`。当 `automl_policy: on`、`automl_enabled: true`，并且都打包了 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 时，默认通过 `tao-skill-bank:tao-run-automl` 路由训练操作，使用此模型的 `skill_dir`。保留工作流/应用程序覆盖的数据集、规范、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时使用直接模型训练；在缺失模式的案例中，在生成模式之前报告此模型启用 AutoML 但不可运行。

非训练操作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每运行的 `automl_policy` 覆盖不会更改模型元数据。

## 训练要求

- **数据集类型：** ocrnet
- **格式：** 默认
- **AutoML 训练指标：** `val_acc`，方向为 `maximize`；TAO 将此键写入 `status.json`
- **Lightning 进度别名：** `val_acc_1`
- **独立评估指标：** `test_acc`，方向为 `maximize`

### 每个操作的 数据集 要求

| 操作 | Spec Key | 来源 | 文件 | 列表？ |
|---|---|---|---|---|
| dataset_convert | dataset_convert.input_img_dir | train_datasets 或 eval_dataset | 包含裁剪文本图像的提取文件夹 | 否 |
| dataset_convert | dataset_convert.gt_file | train_datasets 或 eval_dataset | train/gt_new.txt 或 test/gt_new.txt | 否 |
| evaluate | dataset.character_list_file | eval_dataset | character_list | 否 |
| evaluate | evaluate.test_dataset_dir | eval_dataset | 提取的测试图像文件夹 | 否 |
| evaluate | evaluate.test_dataset_gt_file | eval_dataset | test/gt_new.txt | 否 |
| evaluate | evaluate.checkpoint | 父训练/AutoML 任务 | best_accuracy.pth 或请求的确切 epoch 检查点 | 否 |
| export | dataset.character_list_file | eval_dataset | character_list | 否 |
| export | export.checkpoint | 父训练/AutoML 任务 | best_accuracy.pth 或请求的确切 epoch 检查点 | 否 |
| deploy/gen_trt_engine | gen_trt_engine.tensorrt.calibration.cal_image_dir | calibration_dataset | 用于 INT8 校准的提取校准图像文件夹 | 是 |
| deploy/gen_trt_engine | gen_trt_engine.onnx_file | 父 export 任务 | 导出的 .onnx 资产 | 否 |
| deploy/gen_trt_engine | dataset.character_list_file | eval_dataset | character_list | 否 |
| inference | dataset.character_list_file | eval_dataset | character_list | 否 |
| inference | inference.inference_dataset_dir | inference_dataset | 提取的推理图像文件夹 | 否 |
| inference | inference.checkpoint | 父训练/AutoML 任务 | best_accuracy.pth 或请求的确切 epoch 检查点 | 否 |
| prune | dataset.character_list_file | eval_dataset | character_list | 否 |
| prune | prune.checkpoint | 父训练/AutoML 任务 | best_accuracy.pth 或请求的确切 epoch 检查点 | 否 |
| quantize | dataset.train_dataset_dir | dataset_convert 训练任务 | 包含 data.mdb 和 lock.mdb 的 LMDB 文件夹 | 是 |
| quantize | dataset.val_dataset_dir | dataset_convert 评估任务 | 包含 data.mdb 和 lock.mdb 的 LMDB 文件夹 | 否 |
| quantize | dataset.character_list_file | eval_dataset | character_list | 否 |
| quantize | dataset.quant_calibration_dataset.images_dir | train_datasets | 提取的校准图像文件夹 | 否 |
| quantize | quantize.model_path | 父训练/AutoML 任务 | 解析器选择的检查点 | 否 |
| retrain | dataset.train_dataset_dir | dataset_convert 训练任务 | 包含 data.mdb 和 lock.mdb 的 LMDB 文件夹 | 是 |
| retrain | dataset.val_dataset_dir | dataset_convert 评估任务 | 包含 data.mdb 和 lock.mdb 的 LMDB 文件夹 | 否 |
| retrain | dataset.character_list_file | eval_dataset | character_list | 否 |
| retrain | model.pruned_graph_path | 父 prune 任务 | pruned .pth 资产 | 否 |
| train | dataset.train_dataset_dir | dataset_convert 训练任务 | 包含 data.mdb 和 lock.mdb 的 LMDB 文件夹 | 是 |
| train | dataset.train_gt_file | train_datasets | 使用原始文件夹而不是 LMDB 时的 train/gt_new.txt | 否 |
| train | dataset.val_dataset_dir | dataset_convert 评估任务 | 包含 data.mdb 和 lock.mdb 的 LMDB 文件夹 | 否 |
| train | dataset.val_gt_file | eval_dataset | 使用原始文件夹而不是 LMDB 时的 test/gt_new.txt | 否 |
| train | dataset.character_list_file | eval_dataset | character_list | 否 |

### 检查点选择

OCRNet 训练会写入 `best_accuracy.pth` 和 epoch-step 检查点，例如 `model_epoch_000_step_00003.pth`。通过 `references/skill_info.yaml` 中的 `spec_params` 映射使用 SDK/模型检查点解析器；不要通过排序猜测最新的 `.pth`。

- 使用 `best_accuracy.pth` 进行最佳检查点 `evaluate`、`inference`、`export` 和 `prune` 请求。
- 使用确切的请求 `model_epoch_*_step_*.pth` 进行 epoch/step 特定操作。
- 仅在恢复训练时使用 `train.resume_training_checkpoint_path`，并使用 `model.pruned_graph_path` 从 prune 输出重新训练。OCRNet 在 PyT 图像中不暴露单独的 `ocrnet retrain` CLI 子任务；模型技能的 `retrain` 操作通过 `ocrnet train -e` 路由，并设置修剪图路径。
- OCRNet `quantize` 通过 PyTorch 加载模型。对于由同一本地运行创建的受信任检查点，如果 PyTorch 2.6+ 将检查点作为仅权重加载拒绝，则设置 `TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1`。

### 典型 Spec 覆盖

数据源覆盖对每个操作都是**必需的**。分别运行 `dataset_convert` 用于训练和验证拆分，然后将直接包含 `data.mdb` 和 `lock.mdb` 的 LMDB 文件夹传递给训练、量化 和 重新训练。来自远程存储的 tarball 必须在用作图像目录之前提取。

```python
TRAIN_IMAGES = "<提取的训练图像文件夹>"
TRAIN_GT = "<训练 gt_new.txt>"
EVAL_IMAGES = "<提取的评估图像文件夹>"
EVAL_GT = "<评估 gt_new.txt>"
TRAIN_LMDB = "<训练 dataset_convert 结果目录>"
EVAL_LMDB = "<评估 dataset_convert 结果目录>"
CHAR_LIST = "<字符列表>"
```

**dataset_convert（每个拆分运行一次）：**
```python
{
    "dataset_convert.input_img_dir": TRAIN_IMAGES,
    "dataset_convert.gt_file": TRAIN_GT,
}
```

**train（必需数据源）：**
```python
{
    "train.num_epochs": 30,
    "train.checkpoint_interval": 10,
    "train.validation_interval": 10,
    "train.num_gpus": 1,
    "dataset.batch_size": 16,
    "dataset.train_dataset_dir": [TRAIN_LMDB],
    "dataset.val_dataset_dir": EVAL_LMDB,
    "dataset.train_gt_file": "",
    "dataset.val_gt_file": "",
    "dataset.character_list_file": CHAR_LIST,
}
```

**deploy/gen_trt_engine（必需数据源）：**
```python
{
    "gen_trt_engine.onnx_file": "<选定的 export ONNX>",
    "gen_trt_engine.trt_engine": "<输出引擎路径>",
    "gen_trt_engine.tensorrt.calibration.cal_cache_file": "<输出校准缓存路径>",
    "gen_trt_engine.tensorrt.data_type": "fp16",
    "gen_trt_engine.tensorrt.calibration.cal_image_dir": [TRAIN_IMAGES],
    "dataset.character_list_file": CHAR_LIST,
}
```

**evaluate（必需数据源）：**
```python
{
    "evaluate.checkpoint": "<选定的训练/AutoML 检查点>",
    "dataset.character_list_file": CHAR_LIST,
    "evaluate.test_dataset_dir": EVAL_IMAGES,
    "evaluate.test_dataset_gt_file": EVAL_GT,
}
```

**export（必需数据源）：**
```python
{
    "export.checkpoint": "<选定的训练/AutoML 检查点>",
    "export.onnx_file": "<输出 ONNX 路径>",
    "dataset.character_list_file": CHAR_LIST,
}
```

**inference（必需数据源）：**
```python
{
    "inference.checkpoint": "<选定的训练/AutoML 检查点>",
    "dataset.character_list_file": CHAR_LIST,
    "inference.inference_dataset_dir": EVAL_IMAGES,
}
```

**prune（必需数据源）：**
```python
{
    "prune.checkpoint": "<选定的训练/AutoML 检查点>",
    "prune.pruned_file": "<输出 pruned PTH 路径>",
    "dataset.character_list_file": CHAR_LIST,
}
```

**quantize（必需数据源）：**
```python
{
    "dataset.train_dataset_dir": [TRAIN_LMDB],
    "dataset.val_dataset_dir": EVAL_LMDB,
    "dataset.character_list_file": CHAR_LIST,
    "dataset.quant_calibration_dataset.images_dir": TRAIN_IMAGES,
    "quantize.model_path": "<选定的训练/AutoML 检查点>",
}
```

**retrain（必需数据源）：**
```python
{
    "dataset.train_dataset_dir": [TRAIN_LMDB],
    "dataset.val_dataset_dir": EVAL_LMDB,
    "dataset.character_list_file": CHAR_LIST,
    "model.pruned_graph_path": "<选定的 prune 输出>",
}
```
## 评估数据集

可选。作为单独 tarball 提供的测试数据。

## 重要参数

- **dataset.character_list_file**：定义支持字符集的字符列表路径。这决定了输出词汇量大小。
- **model.backbone**：默认 ResNet。
- **model.prediction**：解码器类型。CTC 或 Attn（基于注意力）。
- **train.optim.lr**：学习率。默认 1.0（Adadelta 优化器）。高默认值是 Adadelta 特有的。
- **dataset.batch_size**：每 GPU 批次大小。默认 16。

## 多 GPU / 多节点

**启动方法：** Lightning 管理的（单个 `python` 进程，Lightning 生成工作进程）。

| Spec Key | 描述 | 默认 |
|----------|-------------|---------|
| `train.num_gpus` | GPU 数量 | 1 |
| `train.gpu_ids` | GPU 设备索引 | [0] |
| `train.distributed_strategy` | 策略名称 | `auto` |

- 策略：`auto` 用于单 GPU，从配置中读取 `train.distributed_strategy` 时为多 GPU
- 训练脚本中没有显式的 `num_nodes` —— 单节点导向
- 轻量级模型，单个 GPU 通常足够

## 硬件

至少 1 个 GPU(s)，推荐 1 个 GPU(s)。每个 GPU 8GB+ VRAM。OCR 文本识别是轻量级的。单个 GPU 通常足够。

## 错误模式

**dataset_convert 必需**：如果使用原始图像 + gt 文件，请先运行 dataset_convert 以生成 LMDB 格式。

**dataset_convert 输出文件夹**：直接 `ocrnet dataset_convert` 将 `data.mdb` 和 `lock.mdb` 写入 `dataset_convert.results_dir` 下。使用该文件夹本身作为 `dataset.train_dataset_dir`、`dataset.val_dataset_dir`、量化 和 重新训练输入。SDK 支持的运行可能会将相同的 LMDB 文件夹包装在工作任务资产目录中；解析实际包含 `data.mdb` 和 `lock.mdb` 的文件夹。

**GT 文件 BOM**：某些文本识别 GT 文件在第一个文件名前可以以 UTF-8 BOM 开头。如果数据集转换日志记录了带有不可见前缀的缺失路径，在第一个图像名称之前，请从本地 GT 文件副本中删除 BOM，然后再进行转换或评估。

**字符列表不匹配**：训练数据中的所有字符都必须出现在字符列表文件中。

**导出/修剪输出字段必需**：`export.onnx_file` 和 `prune.pruned_file` 必须是可写入的输出路径。这些在 `references/skill_info.yaml` 中声明，以便 SDK 支持的模型运行可以自动创建路径。

**TensorRT 存在于部署**：PyT OCRNet CLI 暴露 `dataset_convert`、`evaluate`、`export`、`inference`、`prune`、`quantize` 和 `train`，但不暴露 `gen_trt_engine`。使用 `references/tao-deploy-ocrnet.md` 和 `deploy/skill_info.yaml` 进行 TensorRT 引擎生成和 TensorRT 支持的评估/推理。

## Spec Param / 父模型推理

特定于模型的推理映射属于此 MD 文件，而不是 `config.json`。生成的运行者应读取此部分并使用 SDK 辅助程序在 `create_job()` 之前应用映射。这类似于旧的微服务 `infer_params.py` 流程。

来自 TAO Core `ocrnet.config.json` 的推理映射：

| 操作 | Spec Field | 推理函数 | 含义 |
|---|---|---|---|
| dataset_convert | `results_dir` | `output_dir` | 当前作业结果目录 |
| evaluate | `encryption_key` | `key` | 加密密钥 |
| evaluate | `evaluate.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| evaluate | `evaluate.trt_engine` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| evaluate | `model.pruned_graph_path` | `pruned_model` | 父修剪模型 |
| evaluate | `results_dir` | `output_dir` | 当前作业结果目录 |
| export | `encryption_key` | `key` | 加密密钥 |
| export | `export.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| export | `export.onnx_file` | `create_onnx_file` | 输出 ONNX 路径 |
| export | `results_dir` | `output_dir` | 当前作业结果目录 |
| deploy/gen_trt_engine | `encryption_key` | `key` | 加密密钥 |
| deploy/gen_trt_engine | `gen_trt_engine.onnx_file` | `parent_model` | 从父 export 作业结果文件夹推断的 ONNX 文件 |
| deploy/gen_trt_engine | `gen_trt_engine.tensorrt.calibration.cal_cache_file` | `create_cal_cache` | 校准缓存路径 |
| deploy/gen_trt_engine | `gen_trt_engine.trt_engine` | `create_engine_file` | 输出 TensorRT 引擎路径 |
| deploy/gen_trt_engine | `results_dir` | `output_dir` | 当前作业结果目录 |
| inference | `encryption_key` | `key` | 加密密钥 |
| inference | `inference.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| inference | `inference.trt_engine` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| inference | `model.pruned_graph_path` | `pruned_model` | 父修剪模型 |
| inference | `results_dir` | `output_dir` | 当前作业结果目录 |
| prune | `encryption_key` | `key` | 加密密钥 |
| prune | `prune.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| prune | `prune.pruned_file` | `create_pth_file` | 输出 PTH 路径 |
| prune | `results_dir` | `output_dir` | 当前作业结果目录 |
| quantize | `encryption_key` | `key` | 加密密钥 |
| quantize | `quantize.model_path` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| quantize | `results_dir` | `output_dir` | 当前作业结果目录 |
| retrain | `encryption_key` | `key` | 加密密钥 |
| retrain | `model.pruned_graph_path` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| retrain | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `encryption_key` | `key` | 加密密钥 |
| train | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `train.pretrained_model_path` | `ptm_if_no_resume_model` | 当不存在恢复检查点时的 PTM |
| train | `train.resume_training_checkpoint_path` | `resume_model` | 从当前作业结果文件夹推断的模型文件 |

对于 `parent_model` 或 `parent_model_folder`，将上游训练/导出/AutoML 子作业 ID 作为 `parent_job_id` 传递。SDK 列出父结果文件夹，过滤检查点资产，并返回选定的模型文件或文件夹。不要将这些映射回 `config.json`，也不要修补生成的运行者脚本以猜测检查点路径。

## 部署

- [tao-deploy-ocrnet](references/tao-deploy-ocrnet.md)
