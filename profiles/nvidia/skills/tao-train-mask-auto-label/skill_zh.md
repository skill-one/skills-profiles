# MAL

> **是否独立安装？** 如果此会话不是由TAO技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

MAL（Mask Auto-Label）用于弱监督分割。根据最小标注（例如点或框标注）生成分割掩码。使用ViT-MAE主干网络。

设置 `train.pretrained_model_path` 用于ViT-MAE预训练权重。

## 快速入门（docker run）

原生Docker启动——无需主机上的TAO SDK和Python。当本地Docker/平台技能提供更严格的环境特定命令时（非root UID映射、缓存重定向、远程守护进程），请使用本地Docker/平台技能。

```bash
TAO_PYT_IMAGE_DEFAULT=nvcr.io/nvidia/tao/tao-toolkit:7.2.0-pyt  # 版本键：images.tao_toolkit.pyt
TAO_PYT_IMAGE="${TAO_PYT_IMAGE:-$TAO_PYT_IMAGE_DEFAULT}"
RUN_ROOT="${RUN_ROOT:-$PWD}"
DOCKER_COMMON=(
  --rm --gpus all --shm-size=8g
  --shm-size=8g
  --ulimit memlock=-1
  --ulimit stack=67108864
  -v "$RUN_ROOT/data:/data:ro"
  -v "$RUN_ROOT/specs:/specs:ro"
  -v "$RUN_ROOT/results:/results"
)
```

训练：

```bash
docker run "${DOCKER_COMMON[@]}" "$TAO_PYT_IMAGE" \
  mal train -e /specs/train.yaml
```

评估：

```bash
docker run "${DOCKER_COMMON[@]}" "$TAO_PYT_IMAGE" \
  mal evaluate -e /specs/evaluate.yaml
```

推理：

```bash
docker run "${DOCKER_COMMON[@]}" "$TAO_PYT_IMAGE" \
  mal inference -e /specs/inference.yaml
```

每个操作都使用 `-e` 指定其规范；`results_dir` 在规范中设置或在命令行中覆盖。挂载规范引用的任何预训练权重目录，并确保容器内路径在所有操作中保持一致。

## 数据类模式

生成的TAO Core模式打包在 `schemas/<操作>.schema.json` 中，`schemas/manifest.json` 列出可用操作。每个生成的模式还从模式的顶层 `default` 字段发出 `references/spec_template_<操作>.yaml`。AutoML启用在模型层的 `references/skill_info.yaml` 中通过 `automl_enabled` 声明。运行AutoML需要 `schemas/<操作>.schema.json` 和 `references/spec_template_<操作>.yaml` 存在并解析。使用打包的选定操作模式进行 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖项和常用参数。不要期望运行时 `~/tao-core`；维护者在打包技能库之前重新生成模式/模板。

## 训练操作策略

此模型在模型层启用AutoML。在处理任何训练阶段请求之前，读取 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将类似 "关闭AutoML"、"禁用AutoML"、"无HPO" 或 "纯训练" 的短语视为 `automl_policy: off` 仅对此运行。当 `automl_policy: on`、`automl_enabled: true`，并且 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 都打包时，默认通过此模型的 `skill_dir` 路由训练操作通过 `tao-skill-bank:tao-run-automl`。保留工作流/应用程序覆盖的数据集、规范、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时使用直接模型训练；在缺失模式的情况下，在生成模式之前报告此模型启用AutoML但不可运行。

非训练操作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每运行的 `automl_policy` 覆盖不会更改模型元数据。

## 训练要求

- **数据集类型：** 分割
- **格式：** 默认
- **监控指标：** mIoU
- **AutoML指标契约：** 使用评估操作发出的 `mIoU` 并最大化它。比较记录的AutoML目标与评估器发出的 `mIoU`；不要用训练损失替换。

### 每个操作的 数据集 要求

| 操作 | 规范键 | 源 | 文件 | 列表？ |
|---|---|---|---|---|
| evaluate | dataset.val_img_dir | eval_dataset | images.tar.gz | 否 |
| evaluate | dataset.val_ann_path | eval_dataset | annotations.json | 否 |
| inference | inference.img_dir | inference_dataset | images.tar.gz | 否 |
| inference | inference.ann_path | inference_dataset | annotations.json | 否 |
| train | dataset.train_img_dir | train_datasets | images.tar.gz | 否 |
| train | dataset.train_ann_path | train_datasets | annotations.json | 否 |
| train | dataset.val_img_dir | eval_dataset | images.tar.gz | 否 |
| train | dataset.val_ann_path | eval_dataset | annotations.json | 否 |

### 典型规范覆盖

数据源覆盖对每个操作都是**强制性的**——代理必须根据上表中的每个操作的 数据集 要求构建数据源路径，并将其包含在 `spec_overrides` 中。
MAL期望COCO风格的标注JSON以及与JSON `file_name` 条目匹配的图像路径，在数据源准备后。除非它们首先被转换为此格式，否则仅存档CSV/图像数据集不兼容。

```python
S3_TRAIN = "s3://bucket/data/train"
S3_EVAL = "s3://bucket/data/eval"
```

**train（强制数据源）：**
```python
{
    "train.num_gpus": 1,
    "train.gpu_ids": [
        0
    ],
    "train.num_epochs": 5,
    "train.checkpoint_interval": 5,
    "train.validation_interval": 5,
    "dataset.train_img_dir": f"{S3_TRAIN}/images.tar.gz",
    "dataset.train_ann_path": f"{S3_TRAIN}/annotations.json",
    "dataset.val_img_dir": f"{S3_EVAL}/images.tar.gz",
    "dataset.val_ann_path": f"{S3_EVAL}/annotations.json",
}
```

**evaluate（强制数据源）：**
```python
{
    "evaluate.checkpoint": "<选定的 train/AutoML 检查点>",
    "dataset.val_img_dir": f"{S3_EVAL}/images.tar.gz",
    "dataset.val_ann_path": f"{S3_EVAL}/annotations.json",
}
```

**inference（强制数据源）：**
```python
{
    "inference.checkpoint": "<选定的 train/AutoML 检查点>",
    "inference.img_dir": f"{S3_EVAL}/images.tar.gz",
    "inference.ann_path": f"{S3_EVAL}/annotations.json",
}
```

对于检查点依赖操作，使用 `references/skill_info.yaml` 中声明的模型解析器。选择用户请求的确切 epoch/step 检查点，或在请求最佳检查点操作时选择最佳检查点。`mal_model_latest.pth` 符号链接仅在使用户明确请求最新检查点时适用。

## 评估数据集

可选。与训练路径一起配置的验证图像和标注。

## 重要参数

- **model.arch：** ViT-MAE主干变体。默认 vit-mae-base/16。
  避免使用 `vit-deit-tiny/16`；当前运行时拒绝 tiny ViT 变体。
- **train.lr：** 学习率。默认 1e-6（非常低——微调 ViT）。
- **dataset.crop_size：** 训练裁剪大小。默认 512。使用此键，而不是 `model.crop_size`。
- **train.warmup_epochs：** 全学习率之前的预热轮数。
- **dataset.load_mask：** 标注是否包含预计算的分割掩码。在执行无掩码真实值训练或推理时，将其设置为 `false` 用于包含框但无 `segmentation` 字段的COCO标注。当每个标注都包含分割数据时，保持它为 `true`。选择 `mIoU` 的AutoML验证需要分割真实值和 `dataset.load_mask: true`；仅bbox评估发出非有限 `mIoU`，并且不能被接受为有效的AutoML目标。

## AutoML / HPO 注意事项

对于MAL AutoML启动，保持默认的烟雾搜索空间狭窄，并传递 `automl_hyperparameters=["train.lr", "train.wd"]`。使用保守的贝叶斯范围围绕ViT-MAE微调默认值，例如 `train.lr` 从 `1e-7` 到 `1e-5` 和 `train.wd` 从 `1e-5` 到 `1e-2`。
打包的训练模式将这两个参数标记为默认的AutoML参数；在使用仍然从其捆绑配置模块导出MAL搜索元数据的运行时，请显式传递它们。

## 多GPU / 多节点

**启动方法：** Lightning管理（单个 `python` 进程，Lightning生成工作进程）。

| 规范键 | 描述 | 默认 |
|---|---|---|
| `train.num_gpus` | GPU数量 | 1 |
| `train.gpu_ids` | GPU设备索引 | [0] |
| `train.num_nodes` | 节点数量 | 1 |

- 多GPU策略：`ddp_find_unused_parameters_true`
- 不支持fsdp
- **LR自动缩放：** `lr = lr * num_devices * batch_size`（学习率根据设备数量和批大小自动缩放）

**多节点环境变量**（由编排器设置）：`WORLD_SIZE`、`NODE_RANK`、`MASTER_ADDR`、`MASTER_PORT`、`NUM_GPU_PER_NODE`。

## 硬件

至少1个GPU(s)，推荐2个GPU(s)。每个GPU 24GB+（推荐A100）VRAM。ViT-MAE主干在裁剪大小=512时需要24GB+ GPU内存。

## 错误模式

**CUDA内存不足**：减小 `dataset.crop_size`（512 -> 384 -> 256）或使用较小的ViT-MAE变体（base vs large）。

**键 `crop_size` 不在 `MALModelConfig` 中**：裁剪大小覆盖被放置在 `model.crop_size` 下。将其移动到 `dataset.crop_size`。

## 规范参数 / 父模型推理

特定于模型的推理映射属于此MD文件，而不是在 `config.json` 中。生成的运行器应在 `create_job()` 之前使用SDK帮助程序读取此部分并应用映射。这类似于旧的微服务 `infer_params.py` 流程。

来自TAO Core `mal.config.json` 的推理映射：

| 操作 | 规范字段 | 推理函数 | 含义 |
|---|---|---|---|
| evaluate | `evaluate.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| evaluate | `results_dir` | `output_dir` | 当前作业结果目录 |
| inference | `inference.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| inference | `inference.label_dump_path` | `create_inference_result_file_mal` | MAL推理JSON路径 |
| inference | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `train.pretrained_model_path` | `ptm_if_no_resume_model` | 不恢复时可选的预训练模型 |
| train | `train.resume_training_checkpoint_path` | `resume_model` | 恢复运行的精确检查点 |
| train | `results_dir` | `output_dir` | 当前作业结果目录 |

对于 `parent_model` 或 `parent_model_folder`，将上游训练/导出/AutoML子作业ID作为 `parent_job_id` 传递。SDK列出父结果文件夹，过滤检查点工件，并返回选定的模型文件或文件夹。不要将这些映射重新添加到 `config.json`，也不要修补生成的运行器脚本以猜测检查点路径。
