# NVPanoptix3D

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

NVPanoptix3D 用于从摆姿势的 RGB 图像中进行全景 3D 场景重建。生成 3D 全景分割（语义、实例和全景掩码），并具有占用完成功能。基于 VGGT 主干，具有 Mask2Former 风格的头部和 3D 视锥体重建。

使用 2D 和 3D 阶段检查点。设置 train.checkpoint_2d 和 train.checkpoint_3d 以进行分阶段初始化。

## 快速入门 (docker run)

原生 Docker 启动 — 主机上无需 TAO SDK 和 Python。当本地 Docker/平台技能提供更严格的环境特定命令时（非 root UID 映射、缓存重定向、远程守护进程），请使用本地 Docker/平台技能。

```bash
TAO_PYT_IMAGE_DEFAULT=nvcr.io/nvidia/tao/tao-toolkit:7.2.0-pyt  # versions-key: images.tao_toolkit.pyt
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
  python -m nvidia_tao_pytorch.cv.nvpanoptix3d.entrypoint.nvpanoptix3d train -e /specs/train.yaml
```

评估：

```bash
docker run "${DOCKER_COMMON[@]}" "$TAO_PYT_IMAGE" \
  python -m nvidia_tao_pytorch.cv.nvpanoptix3d.entrypoint.nvpanoptix3d evaluate -e /specs/evaluate.yaml
```

推理：

```bash
docker run "${DOCKER_COMMON[@]}" "$TAO_PYT_IMAGE" \
  python -m nvidia_tao_pytorch.cv.nvpanoptix3d.entrypoint.nvpanoptix3d inference -e /specs/inference.yaml
```

导出：

```bash
docker run "${DOCKER_COMMON[@]}" "$TAO_PYT_IMAGE" \
  python -m nvidia_tao_pytorch.cv.nvpanoptix3d.entrypoint.nvpanoptix3d export -e /specs/export.yaml
```

每个操作都使用其 spec（`-e`）；`results_dir` 在 spec 中设置或在命令行中覆盖。挂载 spec 引用的任何预训练权重目录，并在所有操作中保持容器内路径的一致性。

## 数据类模式

生成的 TAO Core 模式打包在 `schemas/<action>.schema.json` 中，`schemas/manifest.json` 列出可用操作。每个生成的模式还从模式顶层 `default` 字段发出 `references/spec_template_<action>.yaml`。AutoML 启用声明在模型层的 `references/skill_info.yaml` 中通过 `automl_enabled` 声明。运行 AutoML 需要存在并解析 `schemas/<action>.schema.json` 和 `references/spec_template_<action>.yaml`。使用打包的选定操作模式进行 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖项和常用参数。不要期望 `~/tao-core` 在运行时；维护者在打包技能库之前重新生成模式/模板。

## 训练操作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，读取 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将短语如“关闭 AutoML”、“禁用 AutoML”、“无 HPO”或“纯训练”视为 `automl_policy: off` 仅对此运行。当 `automl_policy: on`、`automl_enabled: true`，并且 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 都打包时，默认通过此模型的 `skill_dir` 路由训练操作通过 `tao-skill-bank:tao-run-automl`。保留工作流/应用程序覆盖的数据集、spec、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时使用直接模型训练；在缺失模式的案例中，报告此模型启用 AutoML 但不可运行，直到生成模式。

对于 AutoML，使用 `PRQ` 作为优化指标，`direction=maximize`。
NVPanoptix3D 训练验证和评估作业都在 `status.json` 中发出 `PRQ`、`RSQ` 和 `RRQ`，因此使用 `PRQ` 一致地作为基线、每个建议和最终最佳检查点评估。模型可能在内部使用 `train.optim.monitor_name: train_loss` 进行检查点，但最小作业不会可靠地将数值 `train_loss` 导出到 TAO 状态通道；不要将其用作 AutoML 选择指标。多保真度提升必须在恢复的 epoch 后获得新的 `PRQ`，并且仍然必须从显式 epoch/step 检查点恢复，生成实际检查点，并通过评估/推理。
非训练操作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每次运行的 `automl_policy` 覆盖不会更改模型元数据。

## 训练要求

- **数据集类型：** nvpanoptix3d
- **格式：** front3d、matterport
- **监控指标：** `PRQ`
- **AutoML 方向：** maximize
- 验证和评估状态 KPI 是 `PRQ`、`RSQ` 和 `RRQ`。使用 `PRQ` 进行 AutoML 选择；除非不同的工作流程证明每个试验都外部发出确切的标量并明确批准使用代理目标，否则不要使用 `train_loss` 或 `val_loss`。

### 每个操作的 数据集 要求

| 操作 | Spec Key | 来源 | 文件 | 列表？ |
|---|---|---|---|---|
| evaluate | dataset.frustum_mask_path | eval_dataset | meta/frustum_mask.npz | 否 |
| evaluate | dataset.label_map | eval_dataset | meta/colormap.json | 否 |
| evaluate | dataset.val.json_path | eval_dataset | meta/val.json | 否 |
| evaluate | dataset.val.base_dir | eval_dataset |  | 否 |
| evaluate | dataset.test.json_path | inference_dataset | meta/test.json | 否 |
| evaluate | dataset.test.base_dir | inference_dataset |  | 否 |
| inference | dataset.frustum_mask_path | inference_dataset | meta/frustum_mask.npz | 否 |
| inference | dataset.label_map | inference_dataset | meta/colormap.json | 否 |
| inference | inference.images_dir | inference_dataset | `.jpg`/`.png` RGB 图像的扁平文件夹 | 否 |
| train | dataset.frustum_mask_path | train_datasets | meta/frustum_mask.npz | 否 |
| train | dataset.label_map | train_datasets | meta/colormap.json | 否 |
| train | dataset.train.json_path | train_datasets | meta/train.json | 否 |
| train | dataset.train.base_dir | train_datasets |  | 否 |
| train | dataset.val.json_path | eval_dataset | meta/val.json | 否 |
| train | dataset.val.base_dir | eval_dataset |  | 否 |
| train | dataset.test.json_path | inference_dataset | meta/test.json | 否 |
| train | dataset.test.base_dir | inference_dataset |  | 否 |

### 典型的 Spec 覆盖

数据源覆盖对每个操作都是**强制性的** — 代理必须从上表中的“每个操作的 数据集 要求”表格中构建数据源路径，并将其包含在 `spec_overrides` 中。
对于存储场景数据为 `data/images.tar.gz` 的打包 S3 文件夹，技能元数据请求提取到父 `data/` 目录，因为 TAO 加载器期望 `base_dir/data/<scene_id>/...`。

```python
S3_TRAIN = "s3://bucket/data/train"
S3_EVAL = "s3://bucket/data/eval"
```

**train (强制数据源):**
```python
{
    "train.num_epochs": 10,
    "train.checkpoint_interval": 10,
    "train.validation_interval": 10,
    "train.num_gpus": 1,
    "dataset.enable_3d": True,
    "dataset.contiguous_id": True,
    "model.sem_seg_head.num_classes": 13,
    "dataset.frustum_mask_path": f"{S3_TRAIN}/meta/frustum_mask.npz",
    "dataset.label_map": f"{S3_TRAIN}/meta/colormap.json",
    "dataset.train.json_path": f"{S3_TRAIN}/meta/train.json",
    "dataset.train.base_dir": f"{S3_TRAIN}",
    "dataset.val.json_path": f"{S3_EVAL}/meta/val.json",
    "dataset.val.base_dir": f"{S3_EVAL}",
    "dataset.test.json_path": f"{S3_EVAL}/meta/test.json",
    "dataset.test.base_dir": f"{S3_EVAL}",
}
```

**evaluate (强制数据源):**
```python
{
    "evaluate.checkpoint": "<选择的 train/AutoML 检查点>",
    "dataset.enable_3d": True,
    "dataset.contiguous_id": True,
    "dataset.frustum_mask_path": f"{S3_EVAL}/meta/frustum_mask.npz",
    "dataset.label_map": f"{S3_EVAL}/meta/colormap.json",
    "dataset.val.json_path": f"{S3_EVAL}/meta/val.json",
    "dataset.val.base_dir": f"{S3_EVAL}",
    "dataset.test.json_path": f"{S3_EVAL}/meta/test.json",
    "dataset.test.base_dir": f"{S3_EVAL}",
}
```

**inference (强制数据源):**
```python
{
    "inference.checkpoint": "<选择的 train/AutoML 检查点>",
    "dataset.enable_3d": True,
    "dataset.frustum_mask_path": f"{S3_EVAL}/meta/frustum_mask.npz",
    "dataset.label_map": f"{S3_EVAL}/meta/colormap.json",
    "inference.images_dir": "/path/to/flat_rgb_images",
}
```
## 评估数据集

可选。通过 `dataset.val` 和 `dataset.test` 路径配置验证/测试拆分。

## 重要参数

- **model.sem_seg_head.num_classes**: 语义类数。默认 13。
- **model.mode**: 预测模式。选项：panoptic、instance、semantic。默认 panoptic。
- **model.backbone_type**: 主干。默认 vggt（模式中唯一的选项）。
- **model.mask_former.num_object_queries**: 对象查询。默认 100。
- **model.mask_former.dec_layers**: 解码器层。默认 10。
- **model.frustum3d.truncation**: 3D 视锥体截断。默认 3。
- **model.frustum3d.panoptic_weight**: 全景损失权重。默认 25。
- **model.frustum3d.completion_weights**: 完成损失权重。默认 [50, 25, 10]。
- **dataset.name**: 数据集名称。选项：front3d、matterport、synthetic_hospital、synthetic_warehouse。
- **dataset.contiguous_id**: 当标签图 JSON 已经为其类别 ID 提供了 `trainId` 值时，将 `True` 设置为 `True`；将默认值保留为 `False` 可以合成没有 `trainId` 的占位符类别，并在元数据构建期间失败。
- **dataset.downsample_factor**: 图像下采样因子。默认 1（Front3D）、2（Matterport）。
- **dataset.target_size**: 目标图像大小。默认 [320, 240]。
- **dataset.depth_min**: 最小深度。默认 0.4 米。
- **dataset.depth_max**: 最大深度。默认 6.0 米。
- **train.lr**: 学习率。默认 2e-4。backbone_multiplier=0.1。
- **train.lr_scheduler**: 选项：MultiStep、Warmuppoly。里程碑 [88, 96]。
- **train.precision**: 当前训练代码仅支持 `fp32`。
- **train.distributed_strategy**: 选项：ddp、fsdp。默认激活检查点为 `True`。
- **train.clip_grad_norm**: 梯度裁剪范数。默认 0.1。
- **export.onnx_file_2d**: 2D 模型组件的 ONNX 路径。
- **export.max_voxels**: 引擎输入的最大体素。默认 700000。
- **inference.mode**: 选项：semantic、instance、panoptic。

## 多 GPU / 多节点

**启动方法：** Lightning 管理的（单个 `python` 进程，Lightning 生成工作进程）。

| Spec Key | 描述 | 默认 |
|----------|-------------|---------|
| `train.num_gpus` | GPU 数量 | 1 |
| `train.gpu_ids` | GPU 设备索引 | [0] |
| `train.num_nodes` | 节点数量 | 1 |
| `train.distributed_strategy` | `ddp` 仅 | `ddp` |

- **`fsdp` 不支持** NVPanoptix3D（代码仅处理 `ddp`）
- `ddp` 带激活检查点（默认启用）：`find_unused_parameters=False`
- 无激活检查点的 `ddp`：`find_unused_parameters=True`
- 带有 3D 的 FAN 主干自动启用 `sync_batchnorm`

**多节点环境变量**（由编排器设置）：`WORLD_SIZE`、`NODE_RANK`、`MASTER_ADDR`、`MASTER_PORT`、`NUM_GPU_PER_NODE`。

## 导出 / TRT 默认值

- 将 2D ONNX 模型导出到 `export.onnx_file_2d`。当前的导出入口点调用 `export_2d_model`；`export.onnx_file_3d` 在模式中存在，但此工具包镜像不生成它。
- TRT 数据类型：FP32、FP16 仅
- max_voxels：700000（引擎输入张量限制）

## 硬件

最低 2 个 GPU，推荐 4 个 GPU。每个 GPU 40GB+（推荐 A100）VRAM。3D 重建非常内存密集。使用 `train.precision: fp32`；当前的训练入口点拒绝 fp16。默认启用激活检查点。多节点使用 FSDP。模型层启用 AutoML；在通过 AutoML 路由训练时保留此 GPU/VRAM 指导。

## 错误模式

**在 PyTorch 图像中找不到 `nvpanoptix3d`**：使用打包的模块入口点命令：
`python -m nvidia_tao_pytorch.cv.nvpanoptix3d.entrypoint.nvpanoptix3d <action> -e <spec>`。
7.0 PyTorch 图像包含 NVPanoptix3D 包，但没有暴露 `nvpanoptix3d` 控制台脚本。

**缺少视锥体掩码**：确保在数据集目录中存在 meta/frustum_mask.npz。

**下采样因子不匹配**：对于 Matterport3D 使用 downsample_factor=2，对于 Front3D / 合成数据集使用 1。

**3D 占用 OOM**：如果 3D 重建期间 GPU 内存不足，请减少 frustum_dims 或 grid_dimensions。

**拒绝 fp16 精度**：模式宣传 `fp16`，但当前的训练入口点引发 `ValueError: Only fp32 precision is supported.` 使用 `train.precision: fp32` 进行训练和恢复/重新训练。

**推理数据加载器长度为零**：`inference.images_dir` 仅扫描顶层 `.jpg` 和 `.png` 文件。如果 S3 测试存档提取到场景子目录，请在运行推理之前创建或指向一个包含真实 RGB 图像的扁平文件夹。

**导出后缺少 3D ONNX**：当前的导出入口点仅调用 2D ONNX 导出器并写入 `export.onnx_file_2d`。除非工具包镜像添加了 3D 导出器，否则不要要求 `export.onnx_file_3d`。

**恢复在 epoch 边界停止**：一个 epoch 的冒烟运行会写入一个 epoch 结束检查点，例如 `model_epoch_000_step_00020.pth`。使用 `train.num_epochs` 设置仅一个 epoch 超过原始运行来恢复检查点并停止，而不会生成新的 epoch 检查点。当从 epoch 边界检查点进行实际重新训练时，将 `train.num_epochs` 至少设置为比源冒烟运行多两个 epoch，并相应地提高 `train.optim.max_steps`。例如，从 `model_epoch_000_step_00020.pth` 恢复需要 `train.num_epochs: 3` 和足够的 max steps，以便在将模型交给评估、推理或导出之前生成一个新的精确 epoch/step 检查点，例如 `model_epoch_001_step_00040.pth`。

## Spec 参数 / 父模型推理

模型特定推理映射属于此 MD 文件，而不是 `config.json`。生成的运行者应在 `create_job()` 之前读取此部分并使用 SDK 帮助程序应用映射。这类似于旧的微服务 `infer_params.py` 流程。

模型特定传递映射：

| 操作 | Spec Field | 推理函数 | 含义 |
|---|---|---|---|
| evaluate | `encryption_key` | `key` | 加密密钥 |
| evaluate | `evaluate.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| evaluate | `results_dir` | `output_dir` | 当前作业结果目录 |
| export | `encryption_key` | `key` | 加密密钥 |
| export | `export.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| export | `export.onnx_file_2d` | `create_onnx_file_2d` | 输出 2D ONNX 路径 |
| export | `results_dir` | `output_dir` | 当前作业结果目录 |
| inference | `encryption_key` | `key` | 加密密钥 |
| inference | `inference.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| inference | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `encryption_key` | `key` | 加密密钥 |
| train | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `train.checkpoint_2d` | `parent_model_or_ptm` | 如果可用，则为父模型；否则为 PTM |
| train | `train.checkpoint_3d` | `ptm` | 预训练模型 |
| train | `train.resume_training_checkpoint_path` | `resume_model` | 从当前作业结果文件夹推断的模型文件 |

对于 `parent_model` 或 `parent_model_folder`，将上游训练/导出/AutoML 子作业 ID 作为 `parent_job_id` 传递。SDK 列出父结果文件夹，过滤检查点工件，并返回选定的模型文件或文件夹。不要将这些映射重新添加到 `config.json`，也不要修补生成的运行者脚本以猜测检查点路径。
