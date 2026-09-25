# Sparse4D

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

Sparse4D 用于多摄像机时序 3D 物体检测和跟踪。使用稀疏查询和跨摄像机视图和时间的可变形注意力机制，实现端到端的 3D 感知。包含实例库用于时序跟踪。

当有预训练的 ResNet-101 主干可用时，通过设置 `train.pretrained_model_path` 使用它。对于本地冒烟验证，Sparse4D 训练可以运行空的 `train.pretrained_model_path`，但生产运行仍应使用兼容的 PTM。

## 数据类模式

生成的 TAO Core 模式打包在 `schemas/<action>.schema.json` 中，`schemas/manifest.json` 列出可用操作。每个生成的模式也从模式的顶层 `default` 字段发出 `references/spec_template_<action>.yaml`。AutoML 启用声明在 `references/skill_info.yaml` 中的模型层通过 `automl_enabled`。一个操作的运行时 AutoML 需要 `schemas/<action>.schema.json` 和 `references/spec_template_<action>.yaml` 存在并可解析。使用打包的选定操作的 schema 用于 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖关系和常用参数。不要期望 `~/tao-core` 在运行时；维护者在打包技能库之前重新生成模式/模板。

## 训练操作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，读取 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的工单请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将短语如 "关闭 AutoML"、"禁用 AutoML"、"无 HPO" 或 "纯训练" 视为仅对此运行 `automl_policy: off`。当 `automl_policy: on`、`automl_enabled: true`，并且 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 都打包时，默认通过此模型的 `skill_dir` 路由训练操作到 `tao-skill-bank:tao-run-automl`。保留工作流/应用程序覆盖的数据集、规范、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时使用直接模型训练；在缺失模式的情况下，报告此模型启用 AutoML 但不可运行，直到生成模式。

非训练操作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每运行的 `automl_policy` 覆盖不会更改模型元数据。

## 训练要求

- **数据集类型：** sparse4d
- **格式：** ovpkl
- **监控指标：** val_mAP
- 当前 TAO Sparse4D 训练在状态/日志中发出此值作为 `img_bbox_NuScenes/mAP` 和 `mAP`；AutoML 指标提取器应将那些发出的键视为 `val_mAP` 的别名。Hyperband、ASHA 和 BOHB 等多保真度 AutoML 算法可能会将检查点提升到完成而不发出新 `val_mAP` 别名的恢复作业。在这种情况下，比较 AutoML 携带的指标与发出 `img_bbox_NuScenes/mAP` 或 `mAP` 的源运行作业，同时仍然验证提升的作业是否从显式 epoch/step 检查点恢复、生成了真实的检查点，并且可用于 evaluate/inference。

### 每个操作的数据库要求

| 操作 | 规范键 | 源 | 文件 | 列表？ |
|---|---|---|---|---|
| dataset_convert | aicity.root | id |  | 否 |
| evaluate | dataset.data_root | eval_dataset | (来自 convert 作业，规范： aicity.split) | 否 |
| evaluate | model.head.instance_bank.anchor | train_datasets | /results/{dataset_convert_job_id}/anchor_init.npy | 否 |
| evaluate | dataset.train_dataset.ann_file | train_datasets | (来自 convert 作业，规范： aicity.split) | 否 |
| evaluate | dataset.val_dataset.ann_file | eval_dataset | (来自 convert 作业，规范： aicity.split) | 否 |
| evaluate | dataset.test_dataset.ann_file | inference_dataset | (来自 convert 作业，规范： aicity.split) | 否 |
| export | model.head.instance_bank.anchor | train_datasets | /results/{dataset_convert_job_id}/anchor_init.npy | 否 |
| inference | dataset.data_root | inference_dataset | (来自 convert 作业，规范： aicity.split) | 否 |
| inference | model.head.instance_bank.anchor | train_datasets | /results/{dataset_convert_job_id}/anchor_init.npy | 否 |
| inference | dataset.train_dataset.ann_file | train_datasets | (来自 convert 作业，规范： aicity.split) | 否 |
| inference | dataset.val_dataset.ann_file | eval_dataset | (来自 convert 作业，规范： aicity.split) | 否 |
| inference | dataset.test_dataset.ann_file | inference_dataset | (来自 convert 作业，规范： aicity.split) | 否 |
| quantize | dataset.data_root | train_datasets | (来自 convert 作业，规范： aicity.split) | 否 |
| quantize | model.head.instance_bank.anchor | train_datasets | /results/{dataset_convert_job_id}/anchor_init.npy | 否 |
| quantize | dataset.train_dataset.ann_file | train_datasets | (来自 convert 作业，规范： aicity.split) | 否 |
| quantize | dataset.val_dataset.ann_file | eval_dataset | (来自 convert 作业，规范： aicity.split) | 否 |
| quantize | dataset.test_dataset.ann_file | inference_dataset | (来自 convert 作业，规范： aicity.split) | 否 |
| quantize | dataset.quant_calibration_dataset.images_dir | train_datasets |  | 否 |
| train | dataset.data_root | train_datasets | (来自 convert 作业，规范： aicity.split) | 否 |
| train | model.head.instance_bank.anchor | train_datasets | /results/{dataset_convert_job_id}/anchor_init.npy | 否 |
| train | dataset.train_dataset.ann_file | train_datasets | (来自 convert 作业，规范： aicity.split) | 否 |
| train | dataset.val_dataset.ann_file | eval_dataset | (来自 convert 作业，规范： aicity.split) | 否 |
| train | dataset.test_dataset.ann_file | inference_dataset | (来自 convert 作业，规范： aicity.split) | 否 |

### 典型规范覆盖

数据源覆盖对每个操作都是**强制性的**——代理必须从上表中的每个操作的数据库要求表构建数据源路径，并将它们包含在 `spec_overrides` 中。

```python
S3_TRAIN = "s3://bucket/data/train"
S3_EVAL = "s3://bucket/data/eval"
CONVERTED_SCENE = "<scene-from-converter>"  # 例如 "subsetscene+bev-sensor-random-0"
```

**train (强制数据源):**
```python
CONVERTED = "s3://bucket/results/<dataset_convert_job_id>"
{
    "train.num_epochs": 30,
    "train.checkpoint_interval": 10,
    "train.validation_interval": 10,
    "train.num_gpus": 1,
    "dataset.sequences.split_num": 90,
    "dataset.train_dataset.sequences_split_num": 90,
    "dataset.data_root": f"{S3_TRAIN}/train",
    "model.head.instance_bank.anchor": f"{CONVERTED}/anchor_init.npy",
    "dataset.train_dataset.ann_file": f"{CONVERTED}/train/{CONVERTED_SCENE}_infos_train.pkl",
    "dataset.val_dataset.ann_file": f"{CONVERTED}/val/{CONVERTED_SCENE}_infos_val.pkl",
    "dataset.test_dataset.ann_file": f"{CONVERTED}/test/{CONVERTED_SCENE}_infos_test.pkl",
}
```

**evaluate (强制数据源):**
```python
CONVERTED = "s3://bucket/results/<dataset_convert_job_id>"
{
    "dataset.data_root": f"{S3_EVAL}/val",
    "model.head.instance_bank.anchor": f"{CONVERTED}/anchor_init.npy",
    "dataset.train_dataset.ann_file": f"{CONVERTED}/train/{CONVERTED_SCENE}_infos_train.pkl",
    "dataset.val_dataset.ann_file": f"{CONVERTED}/val/{CONVERTED_SCENE}_infos_val.pkl",
    "dataset.test_dataset.ann_file": f"{CONVERTED}/test/{CONVERTED_SCENE}_infos_test.pkl",
}
```

**export (强制数据源):**
```python
CONVERTED = "s3://bucket/results/<dataset_convert_job_id>"
{
    "model.head.instance_bank.anchor": f"{CONVERTED}/anchor_init.npy",
}
```

**inference (强制数据源):**
```python
CONVERTED = "s3://bucket/results/<dataset_convert_job_id>"
{
    "dataset.data_root": f"{S3_EVAL}/test",
    "model.head.instance_bank.anchor": f"{CONVERTED}/anchor_init.npy",
    "dataset.train_dataset.ann_file": f"{CONVERTED}/train/{CONVERTED_SCENE}_infos_train.pkl",
    "dataset.val_dataset.ann_file": f"{CONVERTED}/val/{CONVERTED_SCENE}_infos_val.pkl",
    "dataset.test_dataset.ann_file": f"{CONVERTED}/test/{CONVERTED_SCENE}_infos_test.pkl",
}
```

**quantize (强制数据源):**
```python
CONVERTED = "s3://bucket/results/<dataset_convert_job_id>"
{
    "dataset.data_root": f"{S3_TRAIN}/train",
    "model.head.instance_bank.anchor": f"{CONVERTED}/anchor_init.npy",
    "dataset.train_dataset.ann_file": f"{CONVERTED}/train/{CONVERTED_SCENE}_infos_train.pkl",
    "dataset.val_dataset.ann_file": f"{CONVERTED}/val/{CONVERTED_SCENE}_infos_val.pkl",
    "dataset.test_dataset.ann_file": f"{CONVERTED}/test/{CONVERTED_SCENE}_infos_test.pkl",
    "dataset.quant_calibration_dataset.images_dir": f"{S3_TRAIN}",
}
```

有关本地-docker 转换根和挂载、H5 深度路径规范化、转换注释文件名、冒烟运行 `max_num_cams`/anchor 合同用于 export 兼容性以及训练/evaluate/inference 之前的转换件验证，请参阅 `references/local_docker_conversion.md`。

## Eval 数据集

可选。通过数据集 ann_file 路径配置的 val/test 切分。

## 重要参数

- **model.backbone**: 主干。默认 resnet_101。
- **model.neck.out_channels**: FPN 输出通道。默认 256。num_outs=4。
- **model.input_shape**: 输入图像形状 [W, H]。默认 [1408, 512]。
- **model.head.num_output**: 检测输出查询数量。默认 300。
- **model.head.num_decoder**: 解码器层数。默认 6。
- **model.head.temporal**: 启用时序推理。默认 True。
- **model.head.instance_bank.num_anchor**: 实例库锚点。默认 900。
- **model.head.instance_bank.num_temp_instances**: 时序实例计数。默认 600。
- **model.depth_branch.loss_weight**: 深度监督损失权重。默认 0.2。
- **dataset.batch_size**: 每个GPU的批处理大小。默认 2。
- **dataset.num_frames**: 序列长度。默认 200。
- **dataset.classes**: 检测类别。默认 [person, gr1_t2, agility_digit, nova_carter]。跟踪 num_ids=70。
- **train.optim.lr**: 学习率。默认 5e-5。img_backbone lr_mult=0.2。
- **train.lr_scheduler**: 余弦调度器带线性预热（500 iters，比率 0.333）。
- **train.grad_clip.max_norm**: 梯度裁剪。默认 25。
- **train.precision**: 选项：bf16、fp16、fp32。默认 bf16。
- **evaluate.metrics**: 评估指标。默认 ["detection"]。可选跟踪评估。
- **evaluate.tracking.enabled**: 启用跟踪评估。tracking_threshold=0.2。

## 多 GPU / 多节点

**启动方法：** Lightning 管理的（单个 `python` 进程，Lightning 生成工作进程）。

| 规范键 | 描述 | 默认 |
|----------|-------------|---------|
| `train.num_gpus` | GPU 数量 | 1 |
| `train.gpu_ids` | GPU 设备索引 | [0] |
| `train.num_nodes` | 节点数量 | 1 |

- 多 GPU 策略：`ddp_find_unused_parameters_true`（不支持 fsdp）
- `sync_batchnorm` 始终启用（True）
- 每个epoch的迭代次数计算为：`num_frames * num_bev_groups / (num_nodes * num_gpus * batch_size)`
- **扩展：** 当增加 GPU 时，有效批处理大小按比例增长，每个epoch的迭代次数按比例减少

**多节点环境变量**（由编排器设置）：`WORLD_SIZE`、`NODE_RANK`、`MASTER_ADDR`、`MASTER_PORT`、`NUM_GPU_PER_NODE`。

## 硬件

至少 2 个 GPU(s)，推荐 8 个 GPU(s)。每个 GPU 至少 40GB+ VRAM（推荐 A100）。多摄像机时序模型内存密集。bf16 对于实际训练是必要的。强烈推荐多 GPU。实例库需要大量内存用于时序推理。

## 错误模式

**需要 dataset_convert**：必须先运行 dataset_convert 以生成注释 pickles 和 anchor_init.npy。

**dataset_convert 容器/命令**：Sparse4D 转换是 AICity 到 OVPKL 注释转换。使用 `tao_toolkit.data_services` 图像和 `annotations convert -e {config_path}` 启动 `dataset_convert`；不要使用 PyTorch `sparse4d` CLI 进行转换。train/evaluate/export/inference 仍然使用模型级别的 PyTorch 图像。

**稳定的原始数据路径**：AICity 到 OVPKL 转换器将图像路径写入生成的 pickle 文件中。转换期间保持 `aicity.root` 在 `/data/aicity_root`，然后将 `dataset.data_root` 指向分割文件夹，例如训练时 `/data/aicity_root/train` 或评估时 `/data/aicity_root/val`。这保留了转换器的绝对 RGB 路径和相对深度路径。

**H5 深度元组不匹配**：如果训练因 H5 路径错误而失败，其中训练器尝试打开摄像机目录，如 `/data/aicity_root/train/<scene>/Camera`，则在 `dataset_convert` 后和 train/evaluate/inference 前运行 `models/tao-train-sparse4d/scripts/normalize_depth_paths.py --data-root <host-aicity-root>/train <converted-ann-dir>`。助手将重写转换的 `depth_map_path` 元组，使其指向 `<scene>/depth_maps/<camera>.h5` 并使用 H5 数据集键 basename。

**缺少锚点文件**：将 `model.head.instance_bank.anchor` 设置为来自 dataset_convert 结果的 anchor_init.npy 路径。

**时序 OOM**：如果时序训练期间内存不足，请减少 `dataset.num_frames` 或 `dataset.batch_size`。

**量化图像兼容性**：模型技能接线应通过父模型解析器传递 `quantize.model_path`，检查点交接应像 evaluate、inference、export 和 resume 一样选择确切的 epoch/step 检查点。TorchAO 检查点量化传递 `validation-fixes-20260525` PyT 图像并写入 `quantized_model_torchao.pth`。较旧的 7.0.0-rc PyT 图像可能在 Sparse4D 量化入口点内部失败或缺少 ONNX 量化依赖项；如果发生这种情况，请不要删除或跳过宣传的 `quantize` 操作。报告容器/图像失败并保持确切的检查点路径可见。

## 规范参数 / 父模型推理

有关模型特定推理映射（来自 TAO Core `sparse4d.config.json` 的每个操作规范字段到推理函数表）和 `parent_model`/`parent_job_id` 检查点解析规则（生成运行者使用 SDK 帮助程序在 `create_job()` 之前应用），请参阅 `references/spec_param_inference.md`。
