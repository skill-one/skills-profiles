# NVDINOv2

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

NVDINOv2 用于自监督视觉表征学习。通过自蒸馏（师生）方式训练视觉 Transformer，无需标签。生成通用视觉特征。

设置 `train.pretrained_model_path` 用于预训练的 ViT 权重。

对于 TAO Deploy TensorRT 操作 (`gen_trt_engine`)，请先阅读 `references/tao-deploy-nvdinov2.md`。部署规范模板位于此技能的 `references/` 文件夹中，以 `spec_template_deploy_*.yaml` 为前缀。

## 数据类模式

生成的 TAO Core 模式打包在 `schemas/<action>.schema.json` 中，`schemas/manifest.json` 列出可用操作。每个生成的模式还会从模式顶层 `default` 字段发出 `references/spec_template_<action>.yaml`。AutoML 启用声明在 `references/skill_info.yaml` 中的模型层，通过 `automl_enabled`。运行 AutoML 需要存在并解析 `schemas/<action>.schema.json` 和 `references/spec_template_<action>.yaml`。使用打包的选定操作模式进行 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖项和常用参数。不要期望在运行时存在 `~/tao-core`；维护者在打包技能库之前会重新生成模式/模板。

## 训练操作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，请阅读 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on`，并在新的启动提示中仅暴露 `on` / `off`。将类似 "关闭 AutoML"、"禁用 AutoML"、"无 HPO" 或 "纯训练" 的短语视为仅对此运行 `automl_policy: off`。当 `automl_policy: on`、`automl_enabled: true`，并且都打包了 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 时，默认将训练操作通过 `tao-skill-bank:tao-run-automl` 路由到此模型的 `skill_dir`。保留工作流/应用程序覆盖的数据集、规范、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时才使用直接模型训练；在缺失模式的案例中，在生成模式之前报告此模型启用 AutoML 但不可运行。

非训练操作（如 `inference`、`export` 和部署流程）保留在此模型技能中。每次运行的 `automl_policy` 覆盖不会更改模型元数据。

## 训练要求

- **数据集类型：** image_classification
- **格式：** ssl
- **监控指标：** train_loss
- **AutoML 指标契约：** 使用训练操作发出的 `train_loss` 并将其最小化。此模型没有打包的评估操作，因此不要编造评估 KPI；通过推理验证选定的 `student_epoch_*` 检查点。

### 每个操作的 数据集 要求

| 操作 | Spec Key | 源 | 源工件 → 运行时值 | 列表？ |
|---|---|---|---|---|
| inference | dataset.test_dataset.images_dir | inference_dataset | `images_test.tar.gz` → 提取的图像文件夹 | 否 |
| train | dataset.train_dataset.images_dir | train_datasets | `images_train.tar.gz` → 提取的图像文件夹 | 否 |

受管理的运行器可以将这些数据集作为存档源，因为 `references/skill_info.yaml` 声明 `runtime: extracted_folder`。它必须解压存档并将生成的目录放置在 `images_dir` 中。对于直接的 Docker 或 TAO CLI 运行，在启动前提取存档；永远不要将 `images_dir` 字段设置为 `.tar`、`.tar.gz`、`.tgz` 或 `.zip`。

### 典型的 Spec 覆盖

数据源覆盖对于训练和推理是**强制性的**——代理必须根据上表中的每个操作的 数据集 要求构建数据源路径，并将其包含在 `spec_overrides` 中。

```python
TRAIN_IMAGES_DIR = "/workspace/data/extracted/train/images_train"
TEST_IMAGES_DIR = "/workspace/data/extracted/test/images_test"
```

**train (强制数据源):**
```python
{
    "train.num_gpus": 1,
    "train.num_epochs": 10,
    "train.checkpoint_interval": 10,
    "dataset.train_dataset.images_dir": TRAIN_IMAGES_DIR,
}
```

**本地 AutoML 验证 / 烟雾测试运行:**
当目标是确认贝叶斯启动、指标选择、最佳模型选择和本地 Docker 上的检查点持久性时，使用此形状。它保持运行具有代表性，同时避免了更慢的 ViT-Large 默认值。

```python
{
    "wandb.enable": False,
    "model.backbone.teacher_type": "vit_s",
    "model.backbone.student_type": "vit_s",
    "model.backbone.img_size": 224,
    "dataset.batch_size": 8,
    "dataset.workers": 2,
    "train.num_epochs": 1,
    "train.checkpoint_interval": 1,
    "train.num_prototypes": 1024,
    "train.precision": "32-true",
    "train.use_custom_attention": False,
    "train.num_gpus": 1,
    "dataset.train_dataset.images_dir": TRAIN_IMAGES_DIR,
}
```

**export (强制检查点传递):**
```python
{
    "export.checkpoint": "<从父作业结果文件夹中选定的 train/AutoML student_epoch_* 检查点>",
    "export.onnx_file": "/path/to/results/nvdinov2.onnx",
}
```

**inference (强制数据源):**
```python
{
    "inference.checkpoint": "<从父作业结果文件夹中选定的 train/AutoML student_epoch_* 检查点>",
    "model.backbone.teacher_type": "<与训练相同的值>",
    "model.backbone.student_type": "<与训练相同的值>",
    "model.backbone.img_size": "<与训练相同的值>",
    "train.use_custom_attention": "<与训练相同的值>",
    # NVDINOv2 在其预测 DataLoader 中启用持久 workers。
    # 保持此值为正；dataset.workers=0 会导致在加载数据之前推理失败。
    "dataset.workers": 2,
    "dataset.test_dataset.images_dir": TEST_IMAGES_DIR,
}
```
## 评估数据集

可选。SSL 训练不使用标签。评估是下游任务特定的。

## 重要参数

- **model.backbone.teacher_type**: 教师 ViT 变体。默认 vit_l (ViT-Large)。
- **model.backbone.student_type**: 学生 ViT 变体。默认 vit_l。通常与教师匹配。
- **model.backbone.img_size**: 输入图像大小。默认 518。更高分辨率生成更好的特征，但会消耗更多内存。
- **model.backbone.patch_size**: ViT 补丁大小。默认 14。
- **dataset.batch_size**: 每个GPU的批处理大小。默认 4。SSL 训练由于双（教师+学生）前向传递而内存密集。
- **train.layerwise_decay**: 层级学习率衰减。对 ViT 微调很重要。
- **train.clip_grad_norm**: 梯度裁剪。对稳定 SSL 训练很重要。

## 多 GPU / 多节点

**启动方法：** Lightning 管理的（单个 `python` 进程，Lightning 生成 workers）。

| Spec Key | 描述 | 默认值 |
|----------|-------------|---------|
| `train.num_gpus` | GPU 数量 | 1 |
| `train.gpu_ids` | GPU 设备索引 | [0] |
| `train.num_nodes` | 节点数量 | 1 |

- 策略：`auto` (Lightning 自动选择最佳策略)
- `sync_batchnorm` 始终启用——对具有师生框架的 SSL 训练至关重要
- 强烈建议使用多 GPU（4-8 个 GPU）进行有意义的 SSL 训练

**多节点环境变量**（由协调器设置）：`WORLD_SIZE`、`NODE_RANK`、`MASTER_ADDR`、`MASTER_PORT`、`NUM_GPU_PER_NODE`。

## 硬件

至少 4 个 GPU，推荐 8 个 GPU。每个 GPU 至少 40GB+ VRAM。带有 ViT-Large 教师+学生的 SSL 非常内存密集。需要 A100 40GB+ GPU。强烈建议使用多 GPU。

## 错误模式

**未找到图像 / 存档路径被拒绝**：`dataset.*.images_dir` 必须是包含图像的提取目录，而不是存档。先提取 `.tar`、`.tar.gz`、`.tgz` 或 `.zip` 输入。受管理的存档源必须使用 `runtime: extracted_folder` 生成的目录。

**CUDA 内存不足**：ViT-Large 教师+学生与 img_size=518 需要 40GB+ GPU 内存。减少 batch_size、img_size 或使用较小的 ViT 变体。

**推理检查点具有意外的 Lightning 键**：对于下游 `inference`，传递选定的 AutoML 运行的 `student_epoch_*.pth` 检查点，而不是 `nvdinov2_model_latest.pth`。最新文件是训练检查点，推理加载器报告意外的键，如 `state_dict`、优化器状态和调度器状态。

**推理因 `persistent_workers option needs num_workers > 0` 失败**：
将 `dataset.workers` 设置为正值（对于最小的本地运行使用 `2`）。NVDINOv2 的预测 DataLoader 启用持久 workers，并且不能与通用的零 workers 烟雾测试覆盖一起运行。

**导出检查点具有意外的 Lightning 键**：导出也消耗选定的 `student_epoch_*.pth` 检查点。仅使用完整的 `model_epoch_*.pth` 检查点通过 `train.resume_training_checkpoint_path` 进行恢复/重新训练。

**传递给 PyT 推理的 TensorRT 引擎**：打包的 PyT `nvdinov2 inference` 实现仅加载 `.pth` 或 `.tlt` 模型路径。TAO Deploy `gen_trt_engine` 为下游消费者构建 TensorRT 引擎，但 PyT 推理操作不运行在该引擎上。

**单独的蒸馏操作不可用**：当前的 TAO PyT CLI 暴露 `export`、`inference`、`train` 和 `default_specs` 用于 NvDINOv2。不要启动或宣传独立的 `nvdinov2 distill` 操作。

**AutoML 指标未找到**：TAO 的状态 KPI 报告最终训练标量为 `train_loss`。使用 `train_loss` 与最小化方向进行 AutoML 选择。一些 Lightning 进度行也渲染相同的标量为 `train_loss_epoch`；将其视为仅是备用别名，而不是主要监控指标。

**收敛缓慢**：SSL 需要许多个 epoch。默认 10 是用于快速测试的；生产运行通常使用 100+ 个 epoch。

## Spec Param / 父模型推理

特定于模型的推理映射属于此 MD 文件，而不是 `config.json`。生成的运行器应在此部分读取此映射，并在 `create_job()` 之前使用 SDK 帮助程序应用映射。这反映了旧的微服务 `infer_params.py` 流程。

特定于模型的传递映射：

| 操作 | Spec Field | 推理函数 | 含义 |
|---|---|---|---|
| export | `encryption_key` | `key` | 加密密钥 |
| export | `export.checkpoint` | `parent_model` | 从父作业结果文件夹中选定的 `student_epoch_*.pth` 检查点 |
| export | `export.onnx_file` | `create_onnx_file` | 输出 ONNX 路径 |
| export | `results_dir` | `output_dir` | 当前作业结果目录 |
| inference | `encryption_key` | `key` | 加密密钥 |
| inference | `inference.checkpoint` | `parent_model` | 从父作业结果文件夹中选定的 `student_epoch_*.pth` 检查点 |
| inference | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `encryption_key` | `key` | 加密密钥 |
| train | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `train.pretrained_model_path` | `ptm_if_no_resume_model` | 当不存在恢复检查点时的 PTM |
| train | `train.resume_training_checkpoint_path` | `resume_model` | 从当前作业结果文件夹中选定的完整 `model_epoch_*.pth` 训练检查点 |

对于 `parent_model` 或 `parent_model_folder`，传递上游训练/导出/AutoML 子作业 ID 作为 `parent_job_id`。SDK 列出父结果文件夹，过滤检查点工件，并返回选定的模型文件或文件夹。不要将这些映射添加回 `config.json`，也不要修补生成的运行器脚本以猜测检查点路径。

## 部署

- [tao-deploy-nvdinov2](references/tao-deploy-nvdinov2.md)
