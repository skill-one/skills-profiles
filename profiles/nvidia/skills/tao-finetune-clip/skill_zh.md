# CLIP

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

对比语言-图像预训练模型，用于零样本和微调图像分类、图像-文本检索和嵌入提取。微调将 CLIP 的共享图像-文本嵌入空间适配到特定领域的图像-文本数据。

构建 spec 时不需要默认的 NGC 预训练检查点，但未设置检查点的行为是特定于操作的。在验证修复的 PyTorch 图像中，`export.checkpoint: null` 导出选定的 CLIP 架构，并在预训练权重不可用时初始化权重。不要假设 `inference.checkpoint: null` 加载预训练权重：`clip inference` 目前调用检查点加载器使用 `None` 并在嵌入提取之前失败。对于 PyTorch 推理，基于检查点的评估/导出、恢复和重新训练流程，从父训练输出中解析并传递确切的检查点。对于当前运行或已知父作业生成的受信任 TAO 检查点，在依赖检查点的 PyTorch 操作上设置 `TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1`，以便 PyTorch 2.6 可以加载 Lightning 检查点元数据；不要为不受信任的检查点设置此参数。

支持的操作：`train`、`evaluate`、`inference`、`export`、`gen_trt_engine`。

## 训练操作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，读取 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将短语如“关闭 AutoML”、“禁用 AutoML”、“无 HPO”或“纯训练”视为 `automl_policy: off` 仅对此运行。当 `automl_policy: on`、`automl_enabled: true`，并且 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 都打包时，默认通过 `tao-skill-bank:tao-run-automl` 路由训练操作，使用此模型的 `skill_dir`。保留工作流/应用程序覆盖的数据集、spec、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练 schema/模板缺失时使用直接模型训练；在缺失 schema 的情况下，报告此模型启用 AutoML 但不可运行，直到生成 schema。

打包的 CLIP 训练 schema 启用 `train.optim.vision_lr` 和 `train.optim.text_lr` 作为默认 AutoML 搜索参数。对于冒烟测试，通过使用贝叶斯算法和两个推荐以及狭窄 LR 范围来保持搜索范围较小。

非训练操作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每运行的 `automl_policy` 覆盖不会更改模型元数据。

## 说明

使用此技能进行 NVIDIA TAO CLIP 作业：训练、评估、嵌入推理、ONNX 导出和 TensorRT 引擎生成。首先确定请求的操作，然后仅加载该操作所需的相关文件：`defaults.json` 用于默认参数，`config.json` 用于操作/数据源连接，`references/spec_template.yaml` 用于完整 spec 形状，`references/model_info.yaml` 用于 SDK 元数据。

对于基于数据集的操作，从用户收集所需图像、文本、列表或提示文件，并将解析的路径放在 `spec_overrides` 中。对于本地 Docker 运行，在容器中挂载提取的文件夹，并将 `image_dir` / `caption_dir` 指向这些文件夹；如果数据源提供 `.tar.gz` 存档，请在运行容器内 CLIP 命令之前提取它们。对于 `export` 和 `gen_trt_engine`，当可用时从上游作业推断父工件；否则需要显式的检查点、ONNX 或引擎路径。在 TAO Deploy 图像中运行 `gen_trt_engine`、TensorRT `evaluate` 和 TensorRT `inference`。

对于 TAO Deploy TensorRT 操作（`gen_trt_engine`、TensorRT `evaluate` 和 TensorRT `inference`），首先阅读 `references/tao-deploy-clip.md`。部署 spec 模板位于此技能的 `references/` 文件夹中，以 `spec_template_deploy_*.yaml` 前缀。

## 训练要求

- **数据集类型：** image_text
- **格式：** 自定义图像/文本文件夹或 WebDataset 片段
- **监控指标：** val/t2i_mAP

训练操作发出 `val/t2i_mAP`，这是 AutoML 选择目标。
独立的评估操作报告相应的保留指标作为 `test/t2i_mAP`；使用该名称进行检查点评估，并将其值与选定的训练验证指标进行比较，而不是期望评估操作从 `val/` 键。

### 支持的模型

- **OpenCLIP / NV-CLIP：** `ViT-L-14-SigLIP-CLIPA-224`（默认）、`ViT-L-14-SigLIP-CLIPA-336`、`ViT-H-14-SigLIP-CLIPA-224`、`ViT-H-14-SigLIP-CLIPA-336`、`ViT-H-14-SigLIP-CLIPA-574`
- **Radio-CLIP：** `c-radio_v3-b`、`c-radio_v3-l`、`c-radio_v3-h`、`c-radio_v3-g`
- **SigLIP2：** `siglip2-so400m-patch16-256`、`siglip2-so400m-patch14-224`、`siglip2-so400m-patch14-384`、`siglip2-so400m-patch16-384`、`siglip2-so400m-patch16-512`、`siglip2-so400m-patch16-naflex`

Radio-CLIP 需要 `model.adaptor_name` 设置为 `siglip` 或 `clip`。

### 每个操作的 数据集要求

| 操作 | Spec 键 | 来源 | 文件 | 列表？ |
|---|---|---|---|---|
| train | dataset.train.datasets | train_datasets | image_dir: images.tar.gz, image_list_file: image_list.txt, caption_dir: captions.tar.gz | 是 |
| train | dataset.train.wds.root_dir | train_wds_dataset | 包含 `.tar` 片段的根目录 | 否 |
| train | dataset.train.wds.shard_list_file | train_wds_dataset | 列出片段路径的 shards.txt | 否 |
| train | dataset.val.datasets | eval_dataset | image_dir: images.tar.gz, image_list_file: image_list.txt, caption_dir: captions.tar.gz | 是 |
| evaluate | dataset.val.datasets | eval_dataset | image_dir: images.tar.gz, image_list_file: image_list.txt, caption_dir: captions.tar.gz | 是 |
| inference | inference.datasets | inference_dataset | image_dir: images.tar.gz | 是 |
| inference | inference.text_file | inference_dataset | prompts.txt | 否 |
| export | export.checkpoint | 父训练作业或显式检查点 | 检查点 .pth，预训练导出可选 | 否 |
| gen_trt_engine | gen_trt_engine.onnx_file | 父导出作业或显式 ONNX | clip_model.onnx | 否 |

对于自定义训练，设置 `dataset.train.type: custom` 并提供 `dataset.train.datasets` 条目。图像和文本文件必须共享相同的基名。`caption_file_suffix` 默认为 `.txt`，`image_list_file` 可选。

当没有原生 CLIP 图像-文本数据集时，不要默默地将图像分类数据视为 CLIP 数据。如果用户明确允许仅管道的验证回退，则从类标签派生文本文件，记录文本是从标签生成的，并保持每个图像/文本对在相同的基文件名上。如果没有 `image_list_file`，TAO 自定义加载器会扫描配置的图像目录以查找图像文件；除非您提供列表文件，否则请保持验证文件夹扁平。

对于 WDS 训练，设置 `dataset.train.type: wds` 并提供至少一个 `dataset.train.wds.root_dir` 或 `dataset.train.wds.shard_list_file`。`root_dir` 递归扫描 `.tar` 片段。`shard_list_file` 是一个每行一个片段路径的文本文件；相对行在列表文件目录下解析，除非也提供 `root_dir`，在这种情况下它们在 `root_dir` 下解析。验证/评估数据通过 `dataset.val.datasets` 保持自定义格式。

### 典型的 Spec 覆盖

数据源覆盖对于基于数据集的操作是强制的。从每个操作的 数据集要求 表格中构建路径，并将它们包含在 `spec_overrides` 中。对于推理，提供至少一个 `inference.datasets` 或 `inference.text_file`。

```python
S3_TRAIN = "s3://bucket/data/train"
S3_WDS = "s3://bucket/data/wds"
S3_EVAL = "s3://bucket/data/eval"
S3_INFER = "s3://bucket/data/infer"
```

**train，自定义数据集：**
```python
{
    "train.num_epochs": 10,
    "dataset.train.type": "custom",
    "dataset.train.datasets": [{"image_dir": f"{S3_TRAIN}/images.tar.gz", "image_list_file": f"{S3_TRAIN}/image_list.txt", "caption_dir": f"{S3_TRAIN}/captions.tar.gz"}],
    "dataset.val.datasets": [{"image_dir": f"{S3_EVAL}/images.tar.gz", "image_list_file": f"{S3_EVAL}/image_list.txt", "caption_dir": f"{S3_EVAL}/captions.tar.gz"}],
}
```

**train，WDS 数据集：**
```python
{
    "train.num_epochs": 10,
    "dataset.train.type": "wds",
    "dataset.train.wds.root_dir": f"{S3_WDS}",
    "dataset.train.wds.shard_list_file": f"{S3_WDS}/shards.txt",
    "dataset.train.wds.samples_per_shard": 10000,
    "dataset.val.datasets": [{"image_dir": f"{S3_EVAL}/images.tar.gz", "image_list_file": f"{S3_EVAL}/image_list.txt", "caption_dir": f"{S3_EVAL}/captions.tar.gz"}],
}
```

**evaluate：**
```python
{
    "dataset.val.datasets": [{"image_dir": f"{S3_EVAL}/images.tar.gz", "image_list_file": f"{S3_EVAL}/image_list.txt", "caption_dir": f"{S3_EVAL}/captions.tar.gz"}],
}
```

为零样本评估保留 `evaluate.checkpoint` 不设置。使用 `evaluate.trt_engine` 而不是 `evaluate.checkpoint` 进行 TensorRT 评估。

**inference：**
```python
{
    "inference.datasets": [{"image_dir": f"{S3_INFER}/images.tar.gz"}],
    "inference.text_file": f"{S3_INFER}/prompts.txt",
}
```

推理在 `results_dir` 下写入 `image_embeddings.h5` 和/或 `text_embeddings.h5`。保存的嵌入是 L2 归一化的。

**export：**
```python
{
    "export.onnx_file": "${results_dir}/export/clip_model.onnx",
    "export.encoder_type": "combined",
    "export.batch_size": -1,
}
```

当部署应使用独立的视觉和文本编码器时，设置 `export.encoder_type: separate`。分离导出写入 `_vision.onnx` 和 `_text.onnx` 变体，这些变体是从基本的 `export.onnx_file` 派生的。

对于依赖检查点的操作，使用来自父训练作业的模型特定检查点解析器输出。CLIP 训练写入检查点，如 `model_epoch_000_step_00020.pth` 和 `clip_latest.pth` 符号链接。使用确切的解析检查点进行 `evaluate.checkpoint`、`inference.checkpoint`、`export.checkpoint` 和 `train.resume_training_checkpoint_path`；仅在用户明确要求最新时使用 `clip_latest.pth`。

当解析的检查点是受信任的 TAO 输出时，检查点支持的 PyTorch `evaluate`、`inference`、`export` 和恢复训练应运行 `TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1`。PyTorch 2.6 否则默认检查点加载为仅权重模式，并可能拒绝包含 NumPy 标量元数据的 CLIP Lightning 检查点。

**gen_trt_engine：**
```python
{
    "gen_trt_engine.onnx_file": "${results_dir}/export/clip_model.onnx",
    "gen_trt_engine.trt_engine": "${results_dir}/deploy/clip_model.engine",
    "gen_trt_engine.batch_size": -1,
    "gen_trt_engine.tensorrt.data_type": "fp16",
    "gen_trt_engine.tensorrt.min_batch_size": 1,
    "gen_trt_engine.tensorrt.opt_batch_size": 1,
    "gen_trt_engine.tensorrt.max_batch_size": 16,
}
```

## 评估数据集

训练可选。如果提供，则在验证间隔计算验证指标。评估需要。

## 部署工作流

技能将 `gen_trt_engine` 作为部署操作公开。在生成的 SDK 运行器中，使用 `model_info["actions"]["gen_trt_engine"]` 并在 TAO Deploy 图像中运行它，而不是 PyTorch 训练图像。容器内命令是 `clip gen_trt_engine -e {config_path}`；直接 TAO Launcher 使用与 `tao deploy clip gen_trt_engine -e /path/to/spec.yaml` 相同的操作拼写。

TAO Deploy 推理可以发现组合引擎、成对的分离引擎或单个支柱 `_vision.engine` / `_text.engine` 文件。对于完整的 TensorRT 检索评估或图像+文本 TensorRT 推理，使用 `export.encoder_type: separate` 导出，并运行 `clip gen_trt_engine` 两次：构建 `clip_model_vision.onnx` 到以 `_vision.engine` 结尾的引擎，然后构建 `clip_model_text.onnx` 到同一目录中匹配的 `_text.engine`。对于仅图像的 TensorRT 推理，仅构建 `_vision.engine` 足够，`inference.text_file` 必须为 `null`。TensorRT `evaluate` 和文本推理需要一个文本功能的引擎；如果只有视觉引擎存在，部署评估会失败，因为无法提取文本嵌入。

使用 `evaluate.trt_engine` 进行 TensorRT 评估，使用 `inference.trt_engine` 进行 TensorRT 嵌入提取。这些 TensorRT 路径也在 TAO Deploy 图像中运行。直接 TAO Launcher 使用 `tao deploy clip evaluate` 和 `tao deploy clip inference` 来拼写这些。

## 重要参数

- **model.type**：骨干家族和分辨率。使用 TAO 注册的 CLIP 模型 ID，例如 `ViT-L-14-SigLIP-CLIPA-224`。对于 AutoML 冒烟测试，优先使用列出的 OpenCLIP / NV-CLIP ID，因为当前的 TAO 容器注册将它们路由到支持增强适配器。
- **model.adaptor_name**：对于 Radio-CLIP 需要。设置为 `siglip` 或 `clip`。
- **model.image_size**：训练转换图像分辨率。保持其与选定的固定分辨率骨干对齐。
- **train.num_epochs**：CLIP 微调通常收敛很快。从 10-20 个 epoch 开始进行领域适配，然后仅在验证损失仍在改进时才增加。
- **train.optim.vision_lr / train.optim.text_lr**：两个编码器的学习率。CLIP 对高学习率敏感；如果损失不稳定，请降低两者。
- **model.freeze_vision_encoder / model.freeze_text_encoder**：默认值为 false。冻结一个编码器可以在数据集较小时或仅需要适配一个模态时有所帮助。
- **train.loss_type**：`siglip` 推荐用于 SigLIP2 和 Radio-CLIP。使用 `clip` 用于 CLIP 风格 softmax 损失。
- **export.encoder_type**：`combined` 导出一个 ONNX 图。`separate` 导出独立的视觉和文本图。
- **gen_trt_engine.tensorrt.data_type**：TensorRT 部署支持 `fp16` 和 `fp32`。

## 硬件

单 GPU 训练适用于小数据集。对于超过 100k 张图像或大型骨干的数据集，使用 4+ GPU。每 GPU 使用 16GB+ VRAM 用于小/固定分辨率运行，使用较大 GPU 用于 Radio-CLIP 或高分辨率 OpenCLIP 变体。

## 错误模式

有关 CLIP 错误症状和修复的完整列表，请参阅 `references/error-patterns.md`（CUDA OOM、NaN 损失、检索质量、数据集格式/大小、Radio-CLIP 和模型 ID 验证、ONNX 外部数据、TensorRT 形状不匹配、PyTorch 2.6 检查点加载、null-checkpoint 推理、TensorRT 文本/检索失败、`attention_mask` 处理和 spec/schema 合并错误）。

## Spec 参数 / 父模型推理

有关模型特定推理映射（生成的运行器使用 SDK 帮助程序在 `create_job()` 之前应用完整的 `clip.config.json` 操作/spec-field/inference-function 表）以及 `parent_job_id` 解析规则，请参阅 `references/spec-param-inference.md`。

## 部署

- [tao-deploy-clip](references/tao-deploy-clip.md)
