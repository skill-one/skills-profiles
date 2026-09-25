# DINO

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

DINO（改进的降噪锚框 DETR）用于 2D 物体检测。基于 Transformer 的检测器，具有降噪训练、多尺度特征和可选的蒸馏支持。

使用预训练的主干权重（例如 ResNet-50 ImageNet）。设置 `model.pretrained_backbone_path` 用于仅主干，或 `train.pretrained_model_path` 用于完整模型。

## 使用场景

对 TAO DINO 2D 物体检测器进行训练、评估、导出、蒸馏、量化或运行推理。

对于 TAO Deploy TensorRT 操作（`gen_trt_engine`、TensorRT `evaluate` 和 TensorRT `inference`），请先阅读 `references/tao-deploy-dino.md`。部署规范模板位于此技能的 `references/` 文件夹中，以 `spec_template_deploy_*.yaml` 为前缀。

## 参考映射

- `references/dino-data-specs.md` — 数据集契约、每个操作的 dataset 要求、每个操作的 spec-override 示例（训练、评估、导出、部署/gen_trt_engine、推理、量化、蒸馏）、数据源数组、检查点推理和 dataset 布局。
- `references/dino-actions-errors.md` — 重要参数、默认值、评估/导出默认值、硬件以及完整的错误模式目录。
- `references/dino-tuning-multigpu.md` — 完整的 AutoML/HPO 注意事项（指标、超参数、extractor）和多 GPU spec 一致性。
- `references/tao-deploy-dino.md` — TensorRT 部署工作流。
- `references/detailed-guide.md` — 详细模型指南的映射。

## 数据类模式

生成的 TAO Core 模式打包在 `schemas/<action>.schema.json` 中，`schemas/manifest.json` 列出可用操作。每个生成的模式也从模式的顶层 `default` 字段发出 `references/spec_template_<action>.yaml`。在 `references/skill_info.yaml` 中通过 `automl_enabled` 在模型层声明 AutoML 启用。可运行的 AutoML 仍然需要 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 存在并解析。使用打包的训练模式进行 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖项和常用参数。不要期望 `~/tao-core` 在运行时；维护人员在打包技能库之前会重新生成模式/模板。

## 训练操作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，请阅读 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将类似于“关闭 AutoML”、“禁用 AutoML”、“无 HPO”或“纯训练”的短语视为 `automl_policy: off`，仅对此运行有效。当 `automl_policy: on`、`automl_enabled: true`，并且 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 都被打包时，默认通过此模型的 `skill_dir` 路由训练操作到 `tao-skill-bank:tao-run-automl`。保留工作流/应用程序覆盖的数据集、规范、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时使用直接模型训练；在缺失模式的案例中，在模式生成之前报告此模型启用但不可运行 AutoML。

非训练操作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每次运行的 `automl_policy` 覆盖不会更改模型元数据。

## 训练要求

代理在为 DINO 生成任何训练或 AutoML 脚本之前，必须阅读此部分。

- **数据集类型：** object_detection
- **格式：** coco, coco_raw
- **接受的 dataset 意图：** training, evaluation, testing, calibration
- **AutoML 指标契约：** 对于默认的评估后工作流，使用 `test_mAP50` 并最大化方向。仅在用户明确请求 COCO/论文风格的 mAP 时使用 `test_mAP`。
- **训练监控指标：** `val_mAP50`（记录为 `Validation mAP50`）用于快速操作检查；`val_mAP` 用于 COCO/论文风格的基准比较。
- **评估操作指标：** `test_mAP50` 用于 AP50 和 `test_mAP` 用于 COCO mAP。使用独立评估操作对推荐进行评分的 AutoML 工作流必须使用相应的 `test_*` KPI。

**必需的数据集 — 必须解决两者：**

| 数据集 | 必需 | 原因 |
|---|---|---|
| Train dataset URI | 是 | 训练数据（COCO 格式） |
| Validation dataset URI | **是 — 总是** | DINO 无条件构建 val dataloader。省略 `val_data_sources` 会导致 `FileNotFoundError` 在启动时 — 无论指标或工作流如何。如果用户没有单独的 eval 分割，请重用训练 URI。 |

**在生成任何训练规范之前必需的输入：**

1. **Train dataset URI** — COCO 格式训练数据的 S3 路径
2. **Validation dataset URI** — COCO 格式 val 数据的 S3 路径（可以与训练相同）
3. **`num_classes`** — 有多少个物体类别？默认 91（COCO）。必须 >= `max(category_id) + 1`。太低会导致 `CUDA error: device-side assert triggered`。

从用户请求或以下默认配置中解决这些值。仅提示缺失的值，在应用配置规则后仍然缺失的值。

**DINO AutoML 烟雾运行的本地可存储默认配置：**

仅在用户请求运行 DINO AutoML 且未提供数据集或类别计数输入时使用此配置。此配置故意很小且仅限于此技能库；它是用于烟雾/迭代运行，而不是生产基准。不要搜索以前的运行者、日志、会话状态、shell 历史记录或主目录以恢复这些值。

```python
DINO_AUTOML_PROFILE = {
    "train_dataset_uri": "s3://nvcf-storage-handling/data/tao_od_synthetic_subset_train_no_convert",
    "validation_dataset_uri": "s3://nvcf-storage-handling/data/tao_od_synthetic_subset_val_no_convert",
    "object_classes": 4,
    "dataset_num_classes": 5,
    "image_archive": "images.tar.gz",
    "annotation_file": "annotations.json",
    "max_recommendations": 10,
    "train_num_epochs": 10,
    "train_checkpoint_interval": 10,
    "train_validation_interval": 1,
    "train_num_gpus": 1,
}
```

如果用户提供任何数据集 URI 或类计数值，请优先使用用户值，并请求任何剩余必需的 DINO 值。除非用户确认，否则不要将用户的自定义数据集部分混合到此配置的类计数中。

**不要提示标准 DINO 数据集的图像布局。** 标准的 TAO DINO 数据集工件是 `images.tar.gz` 加上 `annotations.json`。在远程 `image_dir` 规范覆盖中使用 `images.tar.gz`。SDK 下载存档并将运行时规范重写为存档干名命名的文件夹（`images.tar.gz` -> `images`）。除非用户明确提供不同的图像工件名称，否则不要偏离。

## 核心工作流

DINO 支持训练、评估、导出、蒸馏、量化和推理。数据源覆盖对于每个操作都是**强制性的** — DINO 的 `config.json` 有空的 `data_sources`，因为运行者无法自动解析数组-of-objects 规范键。代理必须构造数据源路径并将其包含在 `spec_overrides` 中。

有关每个操作的 dataset 要求表、标准数据集工件（`images.tar.gz` + `annotations.json`）和运行时文件夹重写规则，以及 train、evaluate、export、deploy/gen_trt_engine、inference、quantize 和 distill 的完整每个操作的 `spec_overrides` 示例（包括通过 `parent_model` 的检查点推理、`results_dir/train/` 检查点位置和蒸馏 FAN-教师/学生规则），请参阅 `references/dino-data-specs.md`。

## 重要参数和默认值

默认值：`num_epochs=10`，`batch_size=4`，`learning_rate=2e-4`，`lr_backbone=2e-5`，`num_classes=91`，`backbone=resnet_50`。

- **dataset.num_classes**：默认 91（COCO）。必须 >= `max(category_id) + 1`。太低会导致 `CUDA error: device-side assert triggered`。在规范覆盖中设置为 `<num_classes> + 1`。
- **num_epochs**：默认 10（快速迭代）；真实数据集通常需要 30-50+ 个 epoch 才能获得良好的 mAP。

有关完整参数列表（主干选项、`train.optim.lr`/`lr_steps`、`model.num_queries`、`batch_size`）、默认值、评估默认值、导出默认值（输入 960x544、opset 17、TRT 数据类型、workspace 1024 MB）和硬件要求的详细信息，请参阅 `references/dino-actions-errors.md`。

## 多 GPU 和 AutoML / HPO

增加 `train.num_gpus` 时，还必须设置 `train.gpu_ids` 为相同的可见设备范围，否则分布式启动可能不一致。

AutoML 运行训练 — 所有**训练要求**以上都适用。对于无输入的本地烟雾运行，使用 `DINO_AUTOML_PROFILE`。对于仅训练日志评分，使用 `val_mAP50`（从 `Validation mAP50` 提取）或 `val_mAP`。当每个推荐通过独立的评估操作进行评分时，使用 `test_mAP50` 或 `test_mAP` 并设置 `direction="maximize"`。

有关完整多 GPU spec 一致性规则（8-GPU 示例、NCCL 超时注意事项）和完整 AutoML/HPO 注意事项（指标选择、`metric_extractor`、推荐超参数、`weight_decay` 行为、密集数据集恢复指导以及父模型推理映射）的详细信息，请参阅 `references/dino-tuning-multigpu.md`。

## 错误模式

常见失败包括 CUDA OOM（减少 `batch_size`）、缺少 `val_data_sources`（启动时 `FileNotFoundError` — 总是提供 val）、`num_classes` 太低（`CUDA device-side assert`）以及父 `dino gen_trt_engine` / `dino convert` Py-CLI 限制。

有关完整错误模式目录（包括诊断和修复）的详细信息，请参阅 `references/dino-actions-errors.md`。

## 规范参数 / 父模型推理

特定于模型的推理映射属于此 MD 文件。对于 `parent_model`/`parent_model_folder`，将上游训练/导出/AutoML 子作业 ID 作为父作业 ID 传递；列出父结果文件夹，过滤检查点工件，并选择解析的模型。

有关完整推理映射表（每个操作：`parent_model`、`key`、`output_dir`、`ptm_if_no_resume_model`、`resume_model`、`create_onnx_file`）和 TensorRT 映射说明的详细信息，请参阅 `references/dino-tuning-multigpu.md`。TensorRT 映射存在于部署工作流中，而不是 PyT 模型技能中。

## 部署

- [tao-deploy-dino](references/tao-deploy-dino.md)
