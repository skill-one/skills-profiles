# OneFormer

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

OneFormer 用于通用图像分割。使用单一架构和任务条件查询统一全景、实例和语义分割。

设置 `train.pretrained_backbone` 和/或 `train.pretrained_model`。

对于 TAO Deploy TensorRT 操作 (`gen_trt_engine`、TensorRT `evaluate` 和 TensorRT `inference`)，请先阅读 `references/tao-deploy-oneformer.md`。部署规范模板位于此技能的 `references/` 文件夹中，以 `spec_template_deploy_*.yaml` 为前缀。

## 数据类模式

生成的 TAO Core 模式打包在 `schemas/<action>.schema.json` 中，`schemas/manifest.json` 列出可用操作。每个生成的模式还会从模式的顶层 `default` 字段发出 `references/spec_template_<action>.yaml`。AutoML 启用声明在 `references/skill_info.yaml` 中的模型层，通过 `automl_enabled`。运行 AutoML 需要存在并解析 `schemas/<action>.schema.json` 和 `references/spec_template_<action>.yaml`。使用打包的选定操作模式进行 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖关系和常用参数。不要期望运行时存在 `~/tao-core`；维护人员在打包技能库之前会重新生成模式/模板。

## 训练操作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，请阅读 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将类似于 "关闭 AutoML"、"禁用 AutoML"、"无 HPO" 或 "纯训练" 的短语视为仅对此运行 `automl_policy: off`。当 `automl_policy: on`、`automl_enabled: true`，并且都打包了 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 时，默认通过 `tao-skill-bank:tao-run-automl` 将训练操作路由到此模型的 `skill_dir`。保留工作流/应用程序覆盖的数据集、规范、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时使用直接模型训练；在缺失模式的情况下，报告此模型启用 AutoML 但不可运行，直到生成模式。

非训练操作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每次运行的 `automl_policy` 覆盖不会更改模型元数据。

## 训练要求

- **数据集类型：** 分割
- **格式：** coco_panoptic、coco
- **AutoML 训练指标：** `mIoU`，方向 `maximize`
- **独立评估指标：** `test_mIoU`，方向 `maximize`

### 每个操作的 数据集 要求

| 操作 | Spec Key | 来源 | 文件 | 列表？ |
|---|---|---|---|---|
| evaluate | dataset.train.images | train_datasets | images.tar.gz | 否 |
| evaluate | dataset.label_map | train_datasets | label_map.json | 否 |
| evaluate | dataset.train.annotations | train_datasets | annotations.json | 否 |
| evaluate | dataset.train.panoptic | train_datasets | images_panoptic.tar.gz | 否 |
| evaluate | dataset.val.images | eval_dataset | images.tar.gz | 否 |
| evaluate | dataset.val.annotations | eval_dataset | annotations.json | 否 |
| evaluate | dataset.val.panoptic | eval_dataset | images_panoptic.tar.gz | 否 |
| evaluate | dataset.test.images | eval_dataset | images.tar.gz | 否 |
| evaluate | dataset.test.annotations | eval_dataset | annotations.json | 否 |
| evaluate | dataset.test.panoptic | eval_dataset | images_panoptic.tar.gz | 否 |
| inference | dataset.train.images | train_datasets | images.tar.gz | 否 |
| inference | dataset.label_map | train_datasets | label_map.json | 否 |
| inference | dataset.train.annotations | train_datasets | annotations.json | 否 |
| inference | dataset.train.panoptic | train_datasets | images_panoptic.tar.gz | 否 |
| inference | dataset.val.images | eval_dataset | images.tar.gz | 否 |
| inference | dataset.val.annotations | eval_dataset | annotations.json | 否 |
| inference | dataset.val.panoptic | eval_dataset | images_panoptic.tar.gz | 否 |
| inference | dataset.test.images | inference_dataset | images.tar.gz | 否 |
| quantize | dataset.train.images | train_datasets | images.tar.gz | 否 |
| quantize | dataset.train.annotations | train_datasets | annotations.json | 否 |
| quantize | dataset.label_map | train_datasets | label_map.json | 否 |
| quantize | dataset.train.panoptic | train_datasets | images_panoptic.tar.gz | 否 |
| quantize | dataset.val.images | eval_dataset | images.tar.gz | 否 |
| quantize | dataset.val.annotations | eval_dataset | annotations.json | 否 |
| quantize | dataset.val.panoptic | eval_dataset | images_panoptic.tar.gz | 否 |
| quantize | dataset.test.images | eval_dataset | images.tar.gz | 否 |
| quantize | dataset.quant_calibration_dataset.images_dir | calibration_dataset | images.tar.gz | 否 |
| train | dataset.train.images | train_datasets | images.tar.gz | 否 |
| train | dataset.train.annotations | train_datasets | annotations.json | 否 |
| train | dataset.label_map | train_datasets | label_map.json | 否 |
| train | dataset.train.panoptic | train_datasets | images_panoptic.tar.gz | 否 |
| train | dataset.val.images | eval_dataset | images.tar.gz | 否 |
| train | dataset.val.annotations | eval_dataset | annotations.json | 否 |
| train | dataset.val.panoptic | eval_dataset | images_panoptic.tar.gz | 否 |
| train | dataset.test.images | eval_dataset | images.tar.gz | 否 |

### 典型 Spec 覆盖

数据源覆盖对每个操作都是**强制性的**——代理必须从上表中的“每个操作的 数据集 要求”表格中构建数据源路径，并将其包含在 `spec_overrides` 中。

```python
S3_TRAIN = "s3://bucket/data/train"
S3_EVAL = "s3://bucket/data/eval"
S3_INFERENCE = "s3://bucket/data/inference"
S3_CALIBRATION = "s3://bucket/data/calibration"
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
    "train.precision": "32",
    "dataset.train.images": f"{S3_TRAIN}/images.tar.gz",
    "dataset.train.annotations": f"{S3_TRAIN}/annotations.json",
    "dataset.label_map": f"{S3_TRAIN}/label_map.json",
    "dataset.train.panoptic": f"{S3_TRAIN}/images_panoptic.tar.gz",
    "dataset.val.images": f"{S3_EVAL}/images.tar.gz",
    "dataset.val.annotations": f"{S3_EVAL}/annotations.json",
    "dataset.val.panoptic": f"{S3_EVAL}/images_panoptic.tar.gz",
    "dataset.test.images": f"{S3_EVAL}/images.tar.gz",
}
```

**evaluate (强制数据源):**
```python
{
    "evaluate.checkpoint": "<selected train/AutoML checkpoint>",
    "model.sem_seg_head.num_classes": 133,
    "dataset.contiguous_id": True,
    "dataset.train.images": f"{S3_TRAIN}/images.tar.gz",
    "dataset.label_map": f"{S3_TRAIN}/label_map.json",
    "dataset.train.annotations": f"{S3_TRAIN}/annotations.json",
    "dataset.train.panoptic": f"{S3_TRAIN}/images_panoptic.tar.gz",
    "dataset.val.images": f"{S3_EVAL}/images.tar.gz",
    "dataset.val.annotations": f"{S3_EVAL}/annotations.json",
    "dataset.val.panoptic": f"{S3_EVAL}/images_panoptic.tar.gz",
    "dataset.test.images": f"{S3_EVAL}/images.tar.gz",
    "dataset.test.annotations": f"{S3_EVAL}/annotations.json",
    "dataset.test.panoptic": f"{S3_EVAL}/images_panoptic.tar.gz",
}
```

**export:**
```python
{
    "export.checkpoint": "<selected train/AutoML checkpoint>",
    "model.sem_seg_head.num_classes": 133,
    "model.export": True,
    "export.onnx_file": "/results/oneformer_export_640.onnx",
}
```

**inference (强制数据源):**
```python
{
    "inference.checkpoint": "<selected train/AutoML checkpoint>",
    "dataset.train.images": f"{S3_TRAIN}/images.tar.gz",
    "dataset.label_map": f"{S3_TRAIN}/label_map.json",
    "dataset.train.annotations": f"{S3_TRAIN}/annotations.json",
    "dataset.train.panoptic": f"{S3_TRAIN}/images_panoptic.tar.gz",
    "dataset.val.images": f"{S3_EVAL}/images.tar.gz",
    "dataset.val.annotations": f"{S3_EVAL}/annotations.json",
    "dataset.val.panoptic": f"{S3_EVAL}/images_panoptic.tar.gz",
    "dataset.test.images": f"{S3_INFERENCE}/images.tar.gz",
    "inference.images_dir": f"{S3_INFERENCE}/images.tar.gz",
}
```

**quantize (强制数据源):**
```python
{
    "quantize.model_path": "<selected train/AutoML checkpoint>",
    "dataset.train.images": f"{S3_TRAIN}/images.tar.gz",
    "dataset.train.annotations": f"{S3_TRAIN}/annotations.json",
    "dataset.label_map": f"{S3_TRAIN}/label_map.json",
    "dataset.train.panoptic": f"{S3_TRAIN}/images_panoptic.tar.gz",
    "dataset.val.images": f"{S3_EVAL}/images.tar.gz",
    "dataset.val.annotations": f"{S3_EVAL}/annotations.json",
    "dataset.val.panoptic": f"{S3_EVAL}/images_panoptic.tar.gz",
    "dataset.test.images": f"{S3_EVAL}/images.tar.gz",
    "dataset.quant_calibration_dataset.images_dir": f"{S3_CALIBRATION}/images.tar.gz",
}
```

## 检查点选择

OneFormer 训练写入 epoch-step 检查点，例如 `model_epoch_000_step_00017.pth`，并且还可能写入 `oneformer_model_latest.pth` 符号链接。对于检查点依赖操作，使用模型技能或 SDK 父模型解析器，并将选定的检查点路径传递到 `evaluate.checkpoint`、`inference.checkpoint`、`export.checkpoint`、`quantize.model_path` 或 `train.resume_training_checkpoint_path`。除非用户明确要求最新检查点行为，否则不要按名称选择 `oneformer_model_latest.pth` 符号链接。如果解析器报告最佳检查点，则使用该最佳检查点进行评估/导出/推理；如果用户请求特定 epoch 或 step，则使用匹配的 epoch-step 检查点。

## 评估数据集

可选。与训练一起在数据集配置中配置的验证数据。

## 重要参数

- **model.sem_seg_head.num_classes**: 可用于头的分割类索引数量。当 `dataset.contiguous_id: True` 时，默认为 133，用于 COCO 全景数据，将原始类别 ID 通过标签映射重新映射。除非标签映射和注释实际减少到该类别集，否则不要将其缩小到全局工作流类计数。
- **model.one_former.hidden_dim**: 除非文本编码器宽度同步更改，否则本地烟雾运行时保持为 256。单独减少 hidden_dim 会导致训练期间文本特征/上下文维度不匹配。
- **model.backbone.name**: 默认 D2SwinTransformer（基于 Swin）。embed_dim=192，depths=[2,2,18,2] 默认。
- **train.num_epochs**: 默认 50 — 比大多数 TAO 模型高得多。OneFormer 需要更多 epoch 才能收敛。
- **train.optim.lr**: 学习率。默认 1e-5。低于 Mask2Former 的 2e-4。
- **model.task_toggling**: 启用/禁用特定任务：semantic_on、instance_on、panoptic_on。
- **export.task**: 导出任务模式。选项：semantic、instance、panoptic。默认 semantic。导出输入默认为 640x640。
- **inference.mode**: 推理模式。选项：semantic、instance、panoptic。默认 semantic。image_size 默认为 [1024, 1024]。
- **evaluate.iou_per_class**: 评估中报告每类 IoU。默认 True。

## 多 GPU / 多节点

**启动方法：** Lightning 管理的（单个 `python` 进程，Lightning 生成工作进程）。

| Spec Key | 描述 | 默认 |
|----------|-------------|---------|
| `train.num_gpus` | GPU 数量 | 1 |
| `train.gpu_ids` | GPU 设备索引 | [0] |
| `train.num_nodes` | 节点数量 | 1 |

- 使用显式的 `DDPStrategy`，`find_unused_parameters=True`、`gradient_as_bucket_view=True`、`process_group_backend="nccl"`
- `sync_batchnorm` 始终启用
- 不支持 fsdp — 仅 DDP

**多节点环境变量**（由编排器设置）：`WORLD_SIZE`、`NODE_RANK`、`MASTER_ADDR`、`MASTER_PORT`、`NUM_GPU_PER_NODE`。

## 硬件

至少 2 个 GPU，推荐 4 个 GPU。每个 GPU 至少 24GB+ VRAM（推荐 A100）。OneFormer 像 Mask2Former 一样内存密集。batch_size=1 是默认值。需要多 GPU 才能获得合理的训练速度，尤其是在 50 个 epoch 的情况下。

## 错误模式

**CUDA 内存不足**：batch_size 已经是 1。降低图像分辨率或使用较小的 Swin 配置。

**提取的 S3 tarball 指向了过高的层级**：对于本地 Docker 运行，`images.tar.gz` 和 `images_panoptic.tar.gz` 可能会提取包装目录，例如 `images/` 和 `images_panoptic/`。将 `dataset.*.images`、`dataset.*.panoptic`、`inference.images_dir` 和量化校准路径设置为实际包含图像或全景文件的文件夹，而不是包装目录。过高的路径会导致 `FileNotFoundError`，即使递归文件计数看起来是正确的。

**default_specs 缺失 results_dir**：CLI `default_specs` 子任务忽略 `-e` 实验规范中的 `results_dir`；相反，请传递 Hydra 风格的覆盖：`oneformer default_specs results_dir=/path/to/default_specs`。

**无效的 Lightning 精度 `fp32`**：在训练/AutoML/评估/推理规范中使用 `train.precision: "32"`。当前的 Lightning 堆栈拒绝过时的 `fp32` 字符串。

**PyTorch 2.6 检查点在下游操作加载失败**：当前的 OneFormer 检查点包括 OmegaConf 对象。对于由相同的可信 TAO 训练/AutoML 工作流生成的检查点，在下游评估、推理、导出、量化或恢复作业环境变量中设置 `TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1`，以便 Lightning 可以加载完整检查点。不要使用此环境变量来处理不可信的检查点。

**CUDA 设备端断言在 matcher/class cost 中**：如果训练在 `oneformer/utils/matcher.py` 中失败，而 `out_prob[:, tgt_ids]` 正在索引，请将有效目标 ID 与 `model.sem_seg_head.num_classes` 进行比较。打包的 COCO 全景样本在 `dataset.contiguous_id: True` 重新映射后具有 133 个紧凑类，因此即使更广泛的验证工作流传递较小的通用 `num_classes` 值，也使用 `model.sem_seg_head.num_classes: 133`。仅在标签映射和注释减少到该确切连续类集时才使用较小的类计数。

**推理返回 PASS 但没有预测**：OneFormer 推理读取 `inference.images_dir`，而不是 `dataset.test.images`。为每个推理运行声明并填充 `inference.images_dir`，使用图像文件夹或 tarball。`dataset.test.images` 可能仍然对共享数据集上下文有用，但它不会驱动 PyTorch predict dataloader。

**导出输出路径预先创建为目录**：不要将 `export.onnx_file` 声明为文件输出。OneFormer 导出器断言 ONNX 路径不存在，而本地运行器预先创建声明的输出路径。将 `export.onnx_file` 明确设置为挂载结果树下不存在的文件路径。保留默认的 640x640 导出形状进行烟雾验证；非常小的导出形状可能会触发 PyTorch ONNX 形状推断失败。

**量化无法从 AutoML 检查点找到训练标签映射**：OneFormer Lightning 检查点保留训练时绝对数据集路径在其保存的 hparams 中。当从 AutoML 子检查点运行下游操作时，除了传递解析的检查点路径外，还应在操作容器内的 `/results/<job_id>` 路径下保持父 AutoML 工作目录的可访问性。否则，即使当前规范包含有效的 `dataset.label_map`，量化在加载检查点 hparams 时也可能失败。

**训练缓慢**：单 GPU 上 50 个默认 epoch 且 batch_size=1 的训练很慢。使用多 GPU 分布式训练。

## Spec 参数 / 父模型推理

特定于模型的推理映射属于此 MD 文件，而不是 `config.json`。生成的运行器应在此部分读取并使用 SDK 帮助程序应用映射，然后再 `create_job()`。这类似于旧的微服务 `infer_params.py` 流程。

来自 TAO Core `oneformer.config.json` 的推理映射：

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
| train | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `train.pretrained_backbone` | `{'link': 'https://github.com/SwinTransformer/storage/releases/download/v1.0.8/swin_tiny_patch4_window7_224_22k.pth', 'destination_path': '/ptm/mask2former/swin_tiny_patch4_window7_224_22k/swin_tiny_patch4_window7_224_22k.pth'}` | {'link': 'https://github.com/SwinTransformer/storage/releases/download/v1.0.8/swin_tiny_patch4_window7_224_22k.pth', 'destination_path': '/ptm/mask2former/swin_tiny_patch4_window7_224_22k/swin_tiny_patch4_window7_224_22k.pth'} |
| train | `train.pretrained_model` | `ptm_if_no_resume_model` | 当没有恢复检查点时 PTM |
| train | `train.resume_training_checkpoint_path` | `resume_model` | 从当前作业结果文件夹推断的模型文件 |

对于 `parent_model` 或 `parent_model_folder`，将上游训练/导出/AutoML 子作业 ID 作为 `parent_job_id` 传递。SDK 列出父结果文件夹，过滤检查点工件，并返回选定的模型文件或文件夹。不要将这些映射重新添加到 `config.json`，也不要修补生成的运行器脚本以猜测检查点路径。

## 部署

- [tao-deploy-oneformer](references/tao-deploy-oneformer.md)
