# MAE

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

MAE（Masked Autoencoder）用于自监督预训练和微调。随机遮盖图像块并重建它们以学习视觉表示。支持预训练和微调阶段。

在微调时，设置 `train.pretrained_model_path` 以指定预训练的 MAE 权重。

对于 TAO Deploy TensorRT 操作 (`gen_trt_engine`)，请先阅读 `references/tao-deploy-mask-auto-encoder.md`。部署规范模板位于此技能的 `references/` 文件夹中，以 `spec_template_deploy_*.yaml` 为前缀。

父级 PyTorch `mae` CLI 支持 `train`、`evaluate`、`inference` 和
`export`。通过部署工作流构建 TensorRT 引擎，而不是通过模型技能。

## 数据类模式

生成的 TAO Core 模式打包在 `schemas/<action>.schema.json` 中，`schemas/manifest.json` 列出可用操作。每个生成的模式也从模式的顶层 `default` 字段发出 `references/spec_template_<action>.yaml`。AutoML 启用声明在模型层的 `references/skill_info.yaml` 中通过 `automl_enabled` 进行。可运行的 AutoML 需要存在并解析 `schemas/<action>.schema.json` 和 `references/spec_template_<action>.yaml`。使用打包的选定操作的规范进行 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖项和常用参数。不要期望在运行时存在 `~/tao-core`；维护者在打包技能库之前会重新生成模式和模板。

## 训练操作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，读取 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将类似于 "关闭 AutoML"、"禁用 AutoML"、"无 HPO" 或 "纯训练" 的短语视为 `automl_policy: off` 仅对此运行。当 `automl_policy: on`、`automl_enabled: true`，并且 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 都被打包时，默认通过 `tao-skill-bank:tao-run-automl` 将训练操作路由到此模型的 `skill_dir`。保留工作流/应用程序覆盖的数据集、规范、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时使用直接模型训练；在缺失模式的案例中，在生成模式之前报告此模型启用 AutoML 但不可运行。

非训练操作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每运行的 `automl_policy` 覆盖不会更改模型元数据。

## 训练要求

- **数据集类型：** image_classification
- **格式：** ssl
- **接受的数集意图：** training、evaluation、testing
- **预训练监控指标：** `train_loss`，最小化。
- **AutoML 指标契约：** 对于微调，使用 `ACC_all` 并指定最大化方向。微调验证和打包的 `evaluate` 操作发出 `ACC_all`（加上 `val_loss`）；它们不会发出 `train_loss`。当 `train.stage: finetune` 时，使用 `ACC_all` 进行试验和最终检查点选择。

### 每个操作的数集要求

| 操作 | Spec Key | 来源 | 文件 | 列表？ |
|---|---|---|---|---|
| train | dataset.train_data_sources | train_datasets | images_train.tar.gz | 否 |
| train | dataset.val_data_sources | eval_dataset | images_val.tar.gz | 否 |
| evaluate | dataset.val_data_sources | eval_dataset | images_val.tar.gz | 否 |
| inference | dataset.test_data_sources | inference_dataset | images_test.tar.gz | 否 |

对于 SDK/应用程序作业输入，`images_*.tar.gz` 归档作为操作输入上传。对于直接本地 Docker 运行针对主机挂载的数据，首先解压归档，并将 `dataset.train_data_sources`、`dataset.val_data_sources` 和 `dataset.test_data_sources` 指向解压的 `images_train`、`images_val` 和 `images_test` 文件夹。将本地 tar 路径直接传递给 MAE CLI 可能会导致零样本数据加载器，因为本地加载器不会解压该归档路径。

### 典型规范覆盖

数据源覆盖对每个操作都是**必需的** — 代理必须根据上表中的每个操作的数集要求构建数据源路径，并将它们包含在 `spec_overrides` 中。

```python
S3_TRAIN = "s3://bucket/data/train"
S3_EVAL = "s3://bucket/data/eval"
```

**train (必需数据源):**
```python
{
    "dataset.train_data_sources": f"{S3_TRAIN}/images_train.tar.gz",
    "dataset.val_data_sources": f"{S3_EVAL}/images_val.tar.gz",
    "train.num_epochs": 10,
    "train.optim.lr": 2e-4,
}
```

**evaluate (必需数据源):**
```python
{
    "dataset.val_data_sources": f"{S3_EVAL}/images_val.tar.gz",
    "evaluate.checkpoint": "<selected train/AutoML 检查点>",
    "train.stage": "finetune",
}
```

**inference (必需数据源):**
```python
{
    "dataset.test_data_sources": f"{S3_EVAL}/images_test.tar.gz",
    "inference.checkpoint": "<selected train/AutoML 检查点>",
    "train.stage": "finetune",
}
```

## 评估数据集

可选的。预训练不需要评估数据。微调可选地使用验证集。

## 重要参数

- **train.stage**: 训练阶段。选项：pretrain、finetune。Pretrain 通过遮盖学习表示。Finetune 添加分类头。
- **model.arch**: 架构。默认 convnextv2_base。对于本地烟雾 AutoML，使用 `convnextv2_atto` 而不是不支持的名字，如 `vit_tiny_patch16`。支持的家族包括 `vit_base_patch16` 及更大的 ViTs、ConvNeXtV2 atto/femto/pico/nano/tiny/base/large/huge，以及 Hiera tiny/small/base/large/huge。
- **model.num_classes**: 微调时类别的数量。默认 1000 (ImageNet)。仅在 finetune 阶段相关。
- **model.mask_ratio**: 预训练期间遮盖的块的比例。通常为 0.75。
- **model.norm_pix_loss**: 重建损失中是否对像素值进行归一化。
- **dataset.augmentation.input_size**: 为 ConvNeXtV2 MAE 保留本地烟雾配置文件为 224。减少到 112 可能会使 MAE 遮盖网格与特征图维度不兼容。
- MAE 没有暴露 `dataset.workers` 规范字段。不要将其添加到烟雾测试覆盖中；Hydra 在训练之前会拒绝未知的数集键。
- **train.optim.lr**: 学习率。默认 2e-4。
- **dataset.augmentation**: 包括 mixup、cutmix 的增强设置，用于微调。

## 多 GPU / 多节点

**启动方法：** Lightning 管理的（单个 `python` 进程，Lightning 生成工作进程）。

| Spec Key | 描述 | 默认值 |
|----------|-------------|---------|
| `train.num_gpus` | GPU 数量 | 1 |
| `train.gpu_ids` | GPU 设备索引 | [0] |
| `train.num_nodes` | 节点数量 | 1 |
| `train.distributed_strategy` | `ddp` 或 `fsdp` | `ddp` |

- `ddp` 使用 `find_unused_parameters=True`
- `fsdp` 强制使用 FP16
- 强烈推荐多 GPU 进行预训练（需要大批量）

**多节点环境变量**（由编排器设置）：`WORLD_SIZE`、`NODE_RANK`、`MASTER_ADDR`、`MASTER_PORT`、`NUM_GPU_PER_NODE`。

## 硬件

至少 2 个 GPU，推荐 8 个 GPU。每个 GPU 至少 24GB+ VRAM（推荐 A100）。MAE 预训练受益于跨多个 GPU 的大批量。微调对资源的要求更为温和。

## 错误模式

**阶段不匹配**：确保 `train.stage` 与您的意图（pretrain 或 finetune）匹配。没有预训练模型路径的微调将从头开始训练。

**使用预训练检查点进行推理**：MAE predict 数据加载器对 `train.stage: pretrain` 抛出 `NotImplementedError`。使用 `finetune` 检查点进行推理和分类式评估，或将预训练-only 运行限制为 train/evaluate/export。

**num_classes 不匹配（仅限微调）**：确保 `model.num_classes` 与您的数据集类数量在微调时匹配。

## 规范参数 / 父模型推理

模型特定的推理映射属于此 MD 文件，而不是 `config.json`。生成的运行器应读取此部分并使用 SDK 辅助程序在 `create_job()` 之前应用映射。这类似于旧的微服务 `infer_params.py` 流程。

来自 TAO Core `mae.config.json` 的推理映射：

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
| train | `encryption_key` | `key` | 加密密钥 |
| train | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `train.pretrained_model_path` | `ptm_if_no_resume_model` | 当没有恢复检查点时 PTM |
| train | `train.resume_training_checkpoint_path` | `resume_model` | 从当前作业结果文件夹推断的模型文件 |

对于 `parent_model` 或 `parent_model_folder`，将上游训练/导出/AutoML 子作业 ID 作为 `parent_job_id` 传递。SDK 列出父结果文件夹，过滤检查点工件，并返回选定的模型文件或文件夹。不要将这些映射重新添加到 `config.json`，也不要修补生成的运行器脚本以猜测检查点路径。

在 SDK 解析器外部解析检查点时，精确选择预期的 epoch/step 工件，例如 `model_epoch_000_step_00099.pth`。仅在明确请求最新时使用 `convnextv2_atto_latest.pth` 或其他最新符号。将 `train.stage`、`model.arch`、`model.num_classes` 和导出输入大小传递到 evaluate、inference、export 和部署规范中，以便检查点和 ONNX/引擎形状匹配。

## 部署

- [tao-deploy-mask-auto-encoder](references/tao-deploy-mask-auto-encoder.md)
