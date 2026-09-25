# ML 识别

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

用于细粒度视觉识别的度量学习识别。学习用于基于检索的匹配的嵌入（例如，零售产品识别）。使用三元组/对比损失。

设置 `model.pretrained_model_path` 以指定预训练主干。

对于 TAO Deploy TensorRT 操作（`gen_trt_engine`、TensorRT `evaluate` 和 TensorRT `inference`），请先阅读 `references/tao-deploy-metric-learning-recognition.md`。部署规范模板位于此技能的 `references/` 文件夹中，以 `spec_template_deploy_*.yaml` 为前缀。

## 数据类模式

生成的 TAO Core 模式打包在 `schemas/<action>.schema.json` 中，`schemas/manifest.json` 列出可用操作。每个生成的模式还会从模式的顶层 `default` 字段发出 `references/spec_template_<action>.yaml`。在 `references/skill_info.yaml` 中的模型层声明 AutoML 启用，通过 `automl_enabled`。要为操作启用可运行的 AutoML，需要存在并解析 `schemas/<action>.schema.json` 和 `references/spec_template_<action>.yaml`。使用打包的选定操作的方案来定义 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖项和常用参数。不要期望在运行时使用 `~/tao-core`；维护人员在打包技能库之前会重新生成模式/模板。

## 训练操作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，请阅读 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将类似于“关闭 AutoML”、“禁用 AutoML”、“无 HPO”或“纯训练”的短语视为 `automl_policy: off`，仅针对此运行。当 `automl_policy: on`、`automl_enabled: true`，并且都打包了 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 时，默认将训练操作路由到 `tao-skill-bank:tao-run-automl`，使用此模型的 `skill_dir`。保留工作流/应用程序覆盖的数据集、规范、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板丢失时使用直接模型训练；在丢失模式的案例中，在生成模式之前报告此模型启用了 AutoML 但不可运行。

非训练操作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每次运行的 `automl_policy` 覆盖不会更改模型元数据。

## 训练要求

- **数据集类型：** ml_recog
- **格式：** 默认
- **监控指标：** val Precision at Rank 1
- **AutoML 指标契约：** 使用训练期间发出的 `val Precision at Rank 1` 并最大化它。仅使用 `test Precision at Rank 1` 进行独立选定检查点的验证。
- **独立评估指标：** `test Precision at Rank 1`。使用训练的 `val Precision at Rank 1` KPI 进行 AutoML 推荐排名，仅使用 `test` KPI 来验证选定的检查点在评估参考/查询拆分上。

### 每个操作的 数据集 要求

| 操作 | Spec Key | 来源 | 文件 | 是否列出 |
|---|---|---|---|---|
| evaluate | dataset.val_dataset | train_datasets | reference: metric_learning_recognition/retail-product-checkout-dataset_classification_demo/unknown_classes/reference.tar.gz, query: metric_learning_recognition/retail-product-checkout-dataset_classification_demo/unknown_classes/test.tar.gz | 否 |
| inference | dataset.val_dataset | train_datasets | reference: metric_learning_recognition/retail-product-checkout-dataset_classification_demo/unknown_classes/reference.tar.gz, query:  | 否 |
| inference | inference.input_path | train_datasets | metric_learning_recognition/retail-product-checkout-dataset_classification_demo/unknown_classes/test.tar.gz | 否 |
| train | dataset.train_dataset | train_datasets | metric_learning_recognition/retail-product-checkout-dataset_classification_demo/known_classes/train.tar.gz | 否 |
| train | dataset.val_dataset | train_datasets | reference: metric_learning_recognition/retail-product-checkout-dataset_classification_demo/known_classes/reference.tar.gz, query: metric_learning_recognition/retail-product-checkout-dataset_classification_demo/known_classes/val.tar.gz | 否 |

### 典型 Spec 覆盖

数据源覆盖对每个操作都是**必需的**——代理必须根据上表中的“每个操作的 数据集 要求”构建数据源路径，并将它们包含在 `spec_overrides` 中。

```python
S3_TRAIN = "s3://bucket/data/train"
```

**train (必需数据源):**
```python
{
    "train.num_epochs": 30,
    "train.checkpoint_interval": 10,
    "train.validation_interval": 10,
    "train.num_gpus": 1,
    "dataset.train_dataset": f"{S3_TRAIN}/metric_learning_recognition/retail-product-checkout-dataset_classification_demo/known_classes/train.tar.gz",
    "dataset.val_dataset": {"reference": f"{S3_TRAIN}/metric_learning_recognition/retail-product-checkout-dataset_classification_demo/known_classes/reference.tar.gz", "query": f"{S3_TRAIN}/metric_learning_recognition/retail-product-checkout-dataset_classification_demo/known_classes/val.tar.gz"},
}
```

**evaluate (必需数据源):**
```python
{
    "evaluate.checkpoint": "<选定的 train/AutoML 检查点>",
    "dataset.val_dataset": {"reference": f"{S3_TRAIN}/metric_learning_recognition/retail-product-checkout-dataset_classification_demo/unknown_classes/reference.tar.gz", "query": f"{S3_TRAIN}/metric_learning_recognition/retail-product-checkout-dataset_classification_demo/unknown_classes/test.tar.gz"},
}
```

**inference (必需数据源):**
```python
{
    "inference.checkpoint": "<选定的 train/AutoML 检查点>",
    "dataset.val_dataset": {"reference": f"{S3_TRAIN}/metric_learning_recognition/retail-product-checkout-dataset_classification_demo/unknown_classes/reference.tar.gz"},
    "inference.input_path": f"{S3_TRAIN}/metric_learning_recognition/retail-product-checkout-dataset_classification_demo/unknown_classes/test.tar.gz",
}
```
## 评估数据集

必需。评估需要用于检索指标参考和查询数据集。

## 重要参数

- **model.backbone**: 默认 resnet_50。选项：resnet_50、resnet_101、fan_small、fan_base、fan_large、fan_tiny、nvdinov2_vit_large_legacy。
- **model.feat_dim**: 嵌入维度。默认 256。用于相似性匹配的特征向量大小。
- **train.batch_size**: 每个GPU的批处理大小。默认 4。`val_batch_size` 也为 4。对于训练和 AutoML 搜索，`train.batch_size` 必须能被 `dataset.num_instance` 整除。
- **dataset.num_instance**: 批次中每个身份的实例数（P/K 采样）。默认 4。控制同一类别的图像一起出现多少。如果使用自定义 AutoML 范围来定义 `train.batch_size`，请使用显式的选项，这些选项是这个值的倍数。
- **train.optim.trunk.base_lr**: 主干（主干）的学习率。默认 3.5e-4 (Adam)。
- **train.optim.embedder.base_lr**: 嵌入头的学习率。默认 3.5e-4。
- **train.optim.triplet_loss_margin**: 三元组损失的边界。默认 0.3。smooth_loss=True 默认。
- **train.optim.miner_function_margin**: 硬挖掘边界。默认 0.1。控制配对挖掘难度。
- **train.optim.steps**: LR 衰减步数。默认 [40, 70] with gamma=0.1。
- **dataset.train_dataset**: 训练图像的路径，按类别文件夹组织。
- **dataset.val_dataset**: 包含 'reference' 和 'query' 键的字典，指向用于检索评估的 ImageNet 格式目录。

## 多 GPU / 多节点

**启动方法：** Lightning 管理的（单个 `python` 进程，Lightning 生成工作进程）。

| Spec Key | 描述 | 默认 |
|----------|-------------|---------|
| `train.num_gpus` | GPU 数量 | 1 |
| `train.gpu_ids` | GPU 设备索引 | [0] |

- 策略：`auto` (Lightning 自动选择最佳策略)
- 没有 `num_nodes` 或 `distributed_strategy` 配置——单节点导向

## 硬件

至少 1 个 GPU，推荐 2 个 GPU。每个 GPU 16GB+ VRAM。度量学习从更大的批处理大小中受益于更好的三元组采样，但在内存方面是适度的。

## 错误模式

**参考/查询不匹配**：确保参考和查询数据集共享兼容的类命名空间以进行评估。

**PyTorch 2.6 检查点在检查点操作加载失败**：当前的 TAO ML-Recog 检查点可能包含 OmegaConf 对象。对于由相同的可信 TAO train/AutoML 工作流生成的检查点，在下游 evaluate、inference、export 或 resume/retrain 工作作业环境变量中设置 `TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1`，以便 Lightning 可以加载完整的检查点。不要使用此环境变量来加载不可信的检查点。

## Spec Param / 父模型推理

特定于模型的推理映射属于此 MD 文件，而不是 `config.json`。生成的运行者应读取本节并使用 SDK 帮助程序在 `create_job()` 之前应用映射。这反映了旧的微服务 `infer_params.py` 流程。

来自 TAO Core `ml_recog.config.json` 的推理映射：

| 操作 | Spec Field | 推理函数 | 含义 |
|---|---|---|---|
| evaluate | `evaluate.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| evaluate | `results_dir` | `output_dir` | 当前作业结果目录 |
| export | `export.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| export | `export.onnx_file` | `create_onnx_file` | 输出 ONNX 路径 |
| export | `results_dir` | `output_dir` | 当前作业结果目录 |
| inference | `inference.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| inference | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `model.pretrained_model_path` | `ptm_if_no_resume_model` | 当没有恢复检查点时 PTM |
| train | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `train.resume_training_checkpoint_path` | `resume_model` | 从当前作业结果文件夹推断的模型文件 |

对于 `parent_model` 或 `parent_model_folder`，将上游训练/导出/AutoML 子作业 ID 作为 `parent_job_id` 传递。SDK 列出父结果文件夹，过滤检查点工件，并返回选定的模型文件或文件夹。不要将这些映射重新添加到 `config.json`，也不要修补生成的运行者脚本来猜测检查点路径。

## 部署

- [tao-deploy-metric-learning-recognition](references/tao-deploy-metric-learning-recognition.md)
