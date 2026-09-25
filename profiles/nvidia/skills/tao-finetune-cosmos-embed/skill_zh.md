# Cosmos-Embed

> **是否为独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

Cosmos-Embed1 是一个联合视频-文本嵌入器，用于文本到视频检索、视频到视频搜索、零样本/kNN 分类和语义去重。打包的 CLI 是 `cosmos-embed1`，支持 `train`、`evaluate`、`inference` 和 `export`。

容器镜像和每个操作的命令在 `references/skill_info.yaml` 中。紧凑的启动规格在 `references/spec_template_*.yaml` 中。

## 训练操作策略

由于 `schemas/` 下没有 Cosmos-Embed 模式，此模型技能未打包 AutoML。始终使用直接模型技能操作进行 `train`、`evaluate`、`inference` 和 `export`，即使较高层级的请求包含 `automl_policy: on`。在添加模型特定训练模式和模板之前，不要将 Cosmos-Embed 通过工作流或 AutoML 技能路由。

非训练操作（如 `evaluate`、`inference`、`export` 和部署流程）仍保留在此模型技能中。每次运行的 `automl_policy` 覆盖不会更改模型元数据。

## 快速入门

使用下方发布的 Cosmos-Embed 容器（也在 `references/skill_info.yaml` 中声明）。对于正常技能使用，不要从私有 Cosmos-Embed1 源树构建；仅开发容器本身时才从源代码构建。

```bash
COSMOS_EMBED_IMAGE_DEFAULT=nvcr.io/nvidia/tao/tao-toolkit:7.1.0-cosmos-embed  # versions-key: images.tao_toolkit.cosmos_embed
COSMOS_EMBED_IMAGE="${COSMOS_EMBED_IMAGE:-$COSMOS_EMBED_IMAGE_DEFAULT}"
docker pull "$COSMOS_EMBED_IMAGE"
```

预期的本地工作区布局：

```text
workspace/
├── data/
│   ├── msrvtt_test_1k.json
│   └── video/
│       ├── video7020.mp4
│       └── ...
├── model/
│   └── Cosmos-Embed1-224p/        # 如果使用 HF 仓库 ID 则可选
├── specs/
│   ├── train.yaml
│   ├── evaluate.yaml
│   ├── inference.yaml
│   ├── export_onnx.yaml
│   └── export_hf.yaml
└── results/
```

对于所有操作，除非本地 Docker/平台技能给出更严格的环境特定命令，否则使用这些 Docker 选项：

```bash
set -a; source /path/to/.env; set +a   # 如果已导出则省略
COSMOS_EMBED_IMAGE_DEFAULT=nvcr.io/nvidia/tao/tao-toolkit:7.1.0-cosmos-embed  # versions-key: images.tao_toolkit.cosmos_embed
COSMOS_EMBED_IMAGE="${COSMOS_EMBED_IMAGE:-$COSMOS_EMBED_IMAGE_DEFAULT}"
RUN_ROOT="${RUN_ROOT:-$PWD}"
DOCKER_COMMON=(
  --rm --gpus all --shm-size=8g --network=host
  --shm-size=64g
  --ulimit memlock=-1
  --ulimit stack=67108864
  -e HF_TOKEN
  -e WANDB_DISABLED=true
  -e WANDB_MODE=disabled
  -e HUGGINGFACE_HUB_CACHE=/hf_cache
  -v "$RUN_ROOT/data:/data:ro"
  -v "$RUN_ROOT/model:/model"
  -v "$RUN_ROOT/specs:/specs:ro"
  -v "$RUN_ROOT/results:/results"
  -v "$RUN_ROOT/hf_cache:/hf_cache"
)
```

对于包含 `protobuf==7.x` 的 Cosmos-Embed 镜像，在每次操作前运行一个小型启动前缀：

```bash
python -m pip install "protobuf<7"
```

镜像包含 `wandb==0.21.0` 和 `protobuf==7.x`；如果没有将 protobuf 固定在 7 以下，导入 W&B 在训练/评估之前会失败。使用 `WANDB_DISABLED=true` 和 `WANDB_MODE=disabled` 进行烟雾测试或离线运行。即使模型检查点被禁用，Cosmos-Embed 也可能下载公共 `google-bert/bert-base-uncased` Q-Former 组件，因此请将 `HF_TOKEN` 作为环境变量传递或挂载持久化的 HuggingFace 缓存。不要将令牌写入规格、日志或报告。

训练：

```bash
docker run "${DOCKER_COMMON[@]}" "$COSMOS_EMBED_IMAGE" \
  bash -lc "python -m pip install 'protobuf<7' && cosmos-embed1 train -e /specs/train.yaml results_dir=/results"
```

评估：

```bash
docker run "${DOCKER_COMMON[@]}" "$COSMOS_EMBED_IMAGE" \
  bash -lc "python -m pip install 'protobuf<7' && cosmos-embed1 evaluate -e /specs/evaluate.yaml results_dir=/results"
```

推理：

```bash
docker run "${DOCKER_COMMON[@]}" "$COSMOS_EMBED_IMAGE" \
  bash -lc "python -m pip install 'protobuf<7' && cosmos-embed1 inference -e /specs/inference.yaml \
  'inference.query.input_texts=[\"a man is singing on stage\"]' \
  inference.k=5 \
  results_dir=/results"
```

导出 ONNX：

```bash
docker run "${DOCKER_COMMON[@]}" "$COSMOS_EMBED_IMAGE" \
  bash -lc "python -m pip install 'protobuf<7' && cosmos-embed1 export -e /specs/export_onnx.yaml \
  export.checkpoint=/results/train/checkpoints/iter_000000001.pt \
  export.onnx_file=/results/export/cosmos_embed1_combined.onnx \
  results_dir=/results"
```

导出 HuggingFace 格式：

```bash
docker run "${DOCKER_COMMON[@]}" "$COSMOS_EMBED_IMAGE" \
  bash -lc "python -m pip install 'protobuf<7' && cosmos-embed1 export -e /specs/export_hf.yaml \
  export.checkpoint=/results/train/checkpoints/iter_000000001.pt \
  export.hf_output_dir=/results/export_hf/cosmos_embed1_hf \
  results_dir=/results"
```

## 烟雾测试覆盖

对于小型功能检查，保持相同的规格并覆盖昂贵的参数：

```bash
train.max_iter=1
train.validation_iter=2
train.checkpoint_iter=1
train.optim.optim=adamw
train.optim.warmup_steps=0
train.optim.lr_decay_iters=1
dataset.train_dataset.batch_size=1
dataset.val_dataset.batch_size=1
dataset.train_dataset.workers=0
dataset.val_dataset.workers=0
```

当为烟雾测试缩短余弦调度器时，保持 `train.optim.lr_decay_iters` 大于 `train.optim.warmup_steps`，或像上面那样设置 `train.optim.warmup_steps=0`。调度器通过 `lr_decay_iters - warmup_steps` 除以，因此相等值会在写入检查点之前失败。

如果没有本地 Cosmos-Embed1 预训练检查点，请将 `model.pretrained_model_path=null` 设置为仅管道的烟雾训练。在该模式下，模型质量无意义，但训练/评估/推理/导出操作路径仍然可以练习。在当前容器中，Q-Former 路径仍然可以获取 `google-bert/bert-base-uncased`；为临时容器提供 `HF_TOKEN` 或挂载 HuggingFace 缓存。

对于极小子集的评估和推理烟雾测试：

```bash
evaluate.callbacks.embedding_visualization=false
evaluate.callbacks.max_eval_samples=8
dataset.test_dataset.batch_size=1
dataset.test_dataset.workers=0
inference.k=2
dataset.inference_dataset.batch_size=1
dataset.inference_dataset.workers=0
```

## 数据格式

MSR-VTT 路径期望本地视频通配符和 JSON 元数据文件：

```yaml
dataset:
  train_dataset:
    dataset_type: msrvtt
    mp4_urls: /data/video/*.mp4
    metadata: /data/msrvtt_test_1k.json
```

列表格式元数据行必须至少包含 `video` 和 `caption`：

```json
{"video_id": "video7020", "video": "video7020.mp4", "caption": "a woman creating a fondant baby and flower"}
```

数据集加载器根据本地 `.mp4` 文件名派生视频 ID 并过滤到元数据中存在的视频。如果运行发现零个视频，请检查 `mp4_urls` 是否指向容器本地通配符，以及元数据 `video` 名称是否与文件名匹配。

## 模型权重

- 本地 HF 目录：挂载到 `/model` 并设置 `model.pretrained_model_path=/model/Cosmos-Embed1-224p`。
- HuggingFace 仓库：设置 `model.pretrained_model_path=nvidia/Cosmos-Embed1-224p` 并如果访问受限制则传递 `HF_TOKEN`。
- 微调检查点：将下游操作设置为解析器选择的 `/results/train/checkpoints/iter_#########.pt` 文件。

训练在 `results/train/checkpoints/iter_#########.pt` 下写入完整检查点，更新 `results/train/checkpoints/latest_checkpoint.txt`，并创建 `cosmos_embed1_model_latest.pth` 符号链接。对于 `evaluate.checkpoint`、`inference.checkpoint`、`export.checkpoint` 和 `train.resume_training_checkpoint_path`，解析并传递预期的迭代的确切 `iter_#########.pt` 文件。操作规格模板有意将检查点字段留空，因此模型技能运行器或用户必须提供解析器选择的检查点。仅在用户明确要求最新时使用最新符号链接。

对于单 GPU 从合并检查点恢复/重新训练，设置 `model.fsdp_shard_size: 1`。容器默认值为 8，这会通过 FSDP 应用路径恢复训练，而 Cosmos-Embed1 不为该模型类实现此路径。

变体：

| 变体 | 分辨率 | 帧数 | 嵌入维度 |
|---|---:|---:|---:|
| `Cosmos-Embed1-224p` | 224 x 224 | 8 | 256 |
| `Cosmos-Embed1-336p` | 336 x 336 | 8 | 768 |
| `Cosmos-Embed1-448p` | 448 x 448 | 8 | 768 |

保持 `model.network.embed_dim`、`model.input_hw` 和 `model.network.spatial_resolution` 与所选变体一致。

## 重要参数

| 参数 | 备注 |
|---|---|
| `train.num_gpus` | 单 GPU 为 `1`，`>1` 自动启动 `torchrun`，`-1` 自动检测可见 GPU。 |
| `train.max_iter` | 主要训练长度。仅用于烟雾测试时使用 `1`。 |
| `train.optim.optim` | 当可用时 `fused_adamw` 更快；`adamw` 对烟雾测试和可移植性更安全。 |
| `model.lora.enabled` | 启用 LoRA。LoRA 开启时设置 `model.network.visual_encoder.transformer_engine=false`。 |
| `model.lora.lora_rank` | LoRA 排名。从 `8` 开始；尝试 `4`、`8` 或 `16` 进行手动或 AutoML 风格的扫描。 |
| `model.lora.lora_alpha` | LoRA 缩放因子。从 `16` 开始；除非实验表明否则保持在 `2 * lora_rank` 附近。 |
| `model.lora.lora_dropout` | LoRA dropout。从 `0.1` 开始；为小数据集扫描 `0.0`、`0.05` 和 `0.1`。 |
| `model.lora.bias` | 偏置策略：`none`、`all` 或 `lora_only`。除非有意训练偏置，否则保持 `none`。 |
| `model.lora.use_rslora` / `use_dora` | 可选的 LoRA 变体。一次启用一个并记录检查点设置。 |
| `model.lora.target_modules` | 可选的模块名模式用于 LoRA 注入。留空为默认 ViT + Q-Former 注意力/MLP 目标。 |
| `model.lora.modules_to_save` | 可选的与 LoRA 一起完全可训练的模块。除非保留特定任务的头部，否则留空。 |
| `evaluate.load_dataset_pkl` / `save_dataset_pkl` | 缓存评估嵌入。 |
| `inference.load_dataset_pkl` / `save_dataset_pkl` | 缓存重复检索的搜索数据库。 |
| `export.mode` | `video`、`text`、`combined` 或 `huggingface`。 |
| `export.on_cpu` | 推荐用于导出以避免设备不匹配问题。 |

### LoRA 和 AutoML 注意事项

对于参数高效的微调，设置 `model.lora.enabled=true` 并保持 `model.network.visual_encoder.transformer_engine=false`；TAO Core 的 Cosmos-Embed1 配置指出 PEFT 不能将适配器注入 Transformer Engine 层。将上述 LoRA 字段视为手动调整或 AutoML 风格搜索之前冻结较大模型块的第一个候选参数。除非用户明确需要自定义适配器位置，否则避免更改 `target_modules` 或 `modules_to_save`。

## S3 预热

Cosmos-Embed1 CLI 消耗本地路径和 Python 通配符，而不是原始 `s3://.../*.mp4` URI。对于 S3 支持的运行，首先将子集或完整数据集预热到执行主机/容器文件系统，然后在规格中使用本地路径，例如 `/data/video/*.mp4`。

推荐的 S3 布局用于预热 MSR-VTT 数据：

```text
s3://bucket/path/cosmos-embed/msrvtt-subset/
├── msrvtt_test_1k.json
└── video/
    ├── video7020.mp4
    └── ...
```

在将前缀下载/同步到挂载的 `data/` 目录后，使用上述相同的 Docker 命令。

## 输出

```text
results/
├── train/
│   ├── cosmos_embed1_model_latest.pth
│   ├── cosmos_embed1_model_<iter>.pth
│   └── experiment.yaml
├── evaluate/
│   ├── metrics.json
│   └── experiment.yaml
├── inference/
│   ├── results.json
│   └── experiment.yaml
├── export/
│   ├── cosmos_embed1_combined.onnx
│   └── export_config.yaml
└── export_hf/
    └── cosmos_embed1_hf/
```

## 已知问题

| 症状 | 原因 | 修复 |
|---|---|---|
| `MSRVTTDataset: 0 videos found` | `mp4_urls` 不是本地通配符或元数据文件名与视频不匹配。 | 将数据挂载到容器并设置 `mp4_urls=/data/video/*.mp4`。 |
| HF 下载/认证失败 | 缺少或无效的 `HF_TOKEN`，或模型协议未接受。 | 接受模型条款并传递 `-e HF_TOKEN`。 |
| `cannot import name 'Imports' from 'wandb.proto.wandb_telemetry_pb2'` | 容器中的 `wandb==0.21.0` 与 `protobuf==7.x` 不兼容。 | 在调用 `cosmos-embed1` 前在容器中运行 `python -m pip install "protobuf<7"`。 |
| 恢复失败，`Model does not implement 'apply_fsdp'` | 单 GPU 恢复加载了合并检查点，而 `model.fsdp_shard_size` 保持默认的 8。 | 设置 `model.fsdp_shard_size=1` 进行本地单 GPU 恢复/重新训练。 |
| LoRA 注入失败 | Transformer Engine 视觉编码器已启用。 | 设置 `model.network.visual_encoder.transformer_engine=false`。 |
| ONNX/HF 导出抱怨缺少组件 | 导出检查点不完整或仅适配器。 | 使用完整检查点或在导出前配置预训练的视觉/文本源。 |
| CUDA OOM | GPU 批次/分辨率过高。 | 减小批次大小，使用 224p，启用 LoRA 或使用更多 GPU。 |
