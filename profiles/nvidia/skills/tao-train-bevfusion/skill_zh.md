# BEVFusion

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

BEVFusion 用于多传感器 3D 物体检测。在鸟瞰视图 (BEV) 空间中融合 LiDAR 点云和相机图像。在自动驾驶中用于稳健的 3D 感知。

为 Swin 图像主干设置预训练主干路径。

BEVFusion 需要 BEVFusion 特定的 TAO 容器
`nvcr.io/nvidia/tao/tao-toolkit:5.5.0-pyt`。 <!-- 未固定：仅 BEVFusion 容器 --> 共享的 TAO PyTorch 7.x 图像不包含 `mmdet3d` 并在 BEVFusion 任何操作之前都无法解析其规范。模型-技能操作命名为 `dataset_convert`，但 5.5 容器 CLI 子任务是 `bevfusion convert -e <spec>`。

## 数据类模式

生成的 TAO Core 模式打包在 `schemas/<action>.schema.json` 中，`schemas/manifest.json` 列出可用操作。每个生成的模式也从模式的顶层 `default` 字段发出 `references/spec_template_<action>.yaml`。AutoML 启用声明在 `references/skill_info.yaml` 中的模型层通过 `automl_enabled`。运行 AutoML 需要操作存在 `schemas/<action>.schema.json` 和 `references/spec_template_<action>.yaml` 并解析，并使用打包的选定操作模式进行 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖关系和常用参数。不要期望 `~/tao-core` 在运行时；维护者在打包技能库之前重新生成模式/模板。

## 训练操作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，读取 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将短语如 "关闭 AutoML"、"禁用 AutoML"、"无 HPO" 或 "纯训练" 视为 `automl_policy: off` 仅对此运行。当 `automl_policy: on`、`automl_enabled: true`，并且 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 都打包时，默认通过此模型的 `skill_dir` 将训练操作路由到 `tao-skill-bank:tao-run-automl`。保留工作流/应用程序覆盖的数据集、规范、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时使用直接模型训练；在缺失模式的情况下，报告此模型启用 AutoML 但不可运行，直到生成模式。

非训练操作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每运行的 `automl_policy` 覆盖不会更改模型元数据。

## 训练要求

- **数据集类型：** bevfusion
- **格式：** 默认
- **监控指标：** AP11

### 每个操作的 数据集 要求

| 操作 | 规范键 | 源 | 文件 | 列表？ |
|---|---|---|---|---|
| dataset_convert | root_dir | id |  | 否 |
| evaluate | dataset.test_dataset | train_datasets | ann_file: results/{dataset_convert_job_id}/kitti_person_infos_val.pkl | 否 |
| inference | dataset.root_dir | train_datasets |  | 否 |
| inference | dataset.test_dataset | train_datasets | ann_file: results/{dataset_convert_job_id}/kitti_person_infos_val.pkl | 否 |
| train | dataset.train_dataset | train_datasets | ann_file: results/{dataset_convert_job_id}/kitti_person_infos_train.pkl | 否 |
| train | dataset.val_dataset | train_datasets | ann_file: results/{dataset_convert_job_id}/kitti_person_infos_val.pkl | 否 |
| train | dataset.test_dataset | train_datasets | ann_file: results/{dataset_convert_job_id}/kitti_person_infos_val.pkl | 否 |

### 典型的 规范 覆盖

数据源覆盖对每个操作都是**强制性的** — 代理必须从上表中的 Per-Action Dataset Requirements 表格构建数据源路径并将其包含在 `spec_overrides` 中。

```python
DATA_ROOT = "/path/to/kitti_root"
CONVERTED = DATA_ROOT  # BEVFusion 5.5 将信息 pickles 写入 root_dir。
DATA_PREFIX = {"pts": "training/velodyne_reduced", "img": "training/image_2"}
```

**dataset_convert (强制数据源):**
```python
{
    "root_dir": DATA_ROOT,
    "results_dir": DATA_ROOT,
    "mode": "training",
}
```

**train (强制数据源):**
```python
{
    "train.num_epochs": 30,
    "train.checkpoint_interval": 10,
    "train.validation_interval": 10,
    "train.num_gpus": 1,
    "dataset.root_dir": DATA_ROOT,
    "dataset.train_dataset": {"ann_file": f"{CONVERTED}/kitti_person_infos_train.pkl", "data_prefix": DATA_PREFIX},
    "dataset.val_dataset": {"ann_file": f"{CONVERTED}/kitti_person_infos_val.pkl", "data_prefix": DATA_PREFIX},
    "dataset.test_dataset": {"ann_file": f"{CONVERTED}/kitti_person_infos_val.pkl", "data_prefix": DATA_PREFIX},
}
```

**evaluate (强制数据源):**
```python
{
    "dataset.root_dir": DATA_ROOT,
    "dataset.test_dataset": {"ann_file": f"{CONVERTED}/kitti_person_infos_val.pkl", "data_prefix": DATA_PREFIX},
}
```

**inference (强制数据源):**
```python
{
    "dataset.root_dir": DATA_ROOT,
    "dataset.test_dataset": {"ann_file": f"{CONVERTED}/kitti_person_infos_val.pkl", "data_prefix": DATA_PREFIX},
}
```
## 评估 数据集

可选。验证集分割通过数据集配置中的 ann_file 配置。

## 重要 参数

- **dataset.classes**: 检测类别列表。默认 ["person"]。必须与注释类别匹配。
- **dataset.type**: 数据集类型。选项：KittiPersonDataset、TAO3DSyntheticDataset、TAO3DDataset。
- **dataset.root_dir**: KITTI 风格数据集的根目录。
- **dataset.box_type_3d**: 3D 盒坐标框架。选项：lidar、camera。默认 lidar。
- **train.optimizer.lr**: 学习率。默认 2e-4 (AdamW)。通过 optimizer.wrapper_type 使用 AmpOptimWrapper 进行混合精度。
- **input_modality**: 控制传感器模态的字典。键：use_lidar (True)、use_camera (True)、use_radar (False)、use_map (False)。
- **model.img_backbone**: 图像主干。默认 mmdet.SwinTransformer (Swin-Tiny)。embed_dims=96, depths=[2,2,6,2]。
- **model.view_transform.type**: BEV 投影的视图变换。选项：DepthLSSTransform、LSSTransform。默认 DepthLSSTransform。
- **model.point_cloud_range**: LiDAR 的空间范围。默认 [0,-40,-3,70.4,40,1]。
- **model.voxel_size**: 体素尺寸。默认 [0.05, 0.05, 0.1]。
- **dataset.train_dataset.batch_size**: 每个GPU的批大小。默认 4。

## 多 GPU / 多 节点

**启动方法：** `torchrun` (LIGHTNING_EXCLUDED_NETWORK)。入口点运行 `torchrun --nnodes=N --nproc-per-node=M train.py`，而不是纯 `python`。

| 规范键 | 描述 | 默认 |
|---|---|---|
| `train.num_gpus` | 每个节点的 GPU 数量 | 1 |
| `train.gpu_ids` | GPU 设备索引 | [0] |
| `train.num_nodes` | 节点数量 | 1 |

- `CUDA_VISIBLE_DEVICES` 从 `TAO_VISIBLE_DEVICES` 显式设置
- BEVFusion 使用基于 mmdet3d 的分布式训练，不是 Lightning DDP
- 如果未设置 `RANK`，则将 `NODE_RANK` 复制到 `RANK`

**多节点环境变量**（由编排器设置）：

| 变量 | 目的 |
|---|---|
| `WORLD_SIZE` | 节点数量 |
| `NODE_RANK` | 此节点的排名 |
| `MASTER_ADDR` | 排名-0 节点 IP |
| `MASTER_PORT` | 排名-0 端口（默认 29500） |
| `NUM_GPU_PER_NODE` | 每个节点的 GPU |

## 硬件

一个 GPU 支持使用小型数据集和批大小进行最小的烟雾/AutoML 验证。使用 2+ GPU 进行常规训练，并在实际情况下使用 4 个 GPU。每个 GPU 需要 24GB+（推荐 A100）VRAM。由于多传感器融合，BEVFusion 是内存密集型的。

## 错误模式

**需要 dataset_convert**: 在训练之前运行模型技能 `dataset_convert` (`bevfusion convert -e <spec>` 在 BEVFusion 5.5 容器中) 以生成 `kitti_person_infos_train.pkl`、`kitti_person_infos_val.pkl` 和 `training/velodyne_reduced`。对于直接本地-docker 5.5 运行，将 `results_dir` 设置为与 `root_dir` 相同的挂载路径；转换器将信息 pickles 写入此处，稍后期望它们在 `root_dir` 下进行点云降采样。

**KITTI 目录名称**: BEVFusion 5.5 转换器在 `training/velodyne_reduced` 下写入降采样点云，并期望相机图像在 `training/image_2` 下。在将 dataset_convert 链接到 train/evaluate 或 inference 时，不要使用过时的 `training/lidar_reduced` 或 `training/images/` 默认值。

**BEVFusion 5.5 配置表面**: 在打包模板中使用 5.5 数据类键。删除较新的顶层/操作键，如 `model_name`、`wandb.group`、`wandb.run_id`、`train.checkpoint_interval_unit`、`evaluate.trt_engine`、`evaluate.batch_size`、`inference.trt_engine` 和 `inference.batch_size`。对于 train、evaluate 和 inference 规范，保留非运行操作占位符（`train`、`evaluate` 和 `inference`）并在需要的地方使用空检查点字符串；5.5 运行器在运行选定操作之前会生成完整的实验配置。当没有检查点时，使用 YAML null 而不是空字符串作为 `train.pretrained_checkpoint` 和 `train.resume_training_checkpoint_path`。

**`ModuleNotFoundError: No module named 'mmdet3d'`**: 共享的 TAO PyTorch 7.x 图像不包含 BEVFusion 的 `mmdet3d` 依赖项。使用 `nvcr.io/nvidia/tao/tao-toolkit:5.5.0-pyt`； <!-- 未固定：仅 BEVFusion 容器 --> 它包含 `mmdet3d` 并暴露 BEVFusion 的 `convert`、`train`、`evaluate` 和 `inference` 子任务。

**评估后 BEVFusion 5.5 中的 SIGSEGV**: 一些本地-docker 运行可以写入检查点或预测文件，但在 `cuMemRetainAllocationHandle` 中的 `Signal 11 (SIGSEGV)` 后仍然以 TAO `Execution status: FAIL` 完成后。不要仅从 Docker 退出代码判断操作是否成功；检查 TAO 日志或 `status.json`。在 CUDA 12+ 主机上，保留 TAO 5.5 依赖栈并应用 BEVFusion 旋转-IoU CPU 回退和 `tao-pytorch` 运行器清理；不要切换操作到共享的 7.x 图像。回退是默认的；`BEVFUSION_ROTATE_IOU_BACKEND=gpu` 是显式选择旧版 Numba CUDA 评估器的选项。如果在此失败之前生成了检查点，请仅使用精确的预期检查点（如 `epoch_1.pth`）进行下游诊断，并且除非操作明确请求最新检查点，否则不要将 `last_checkpoint` 视为最佳检查点。

**缺失模态数据**: 如果使用多模态融合，请确保同时存在相机图像和 LiDAR 点云。

**周期编号**: BEVFusion 检查点周期编号可能不遵循标准的零填充格式。

**检查点交接**: 使用 SDK/模型检查点解析器进行父模型选择。对于直接本地-docker 链接，检查训练结果并传递精确的预期检查点路径（如 `epoch_1.pth`）；仅在用户明确要求时使用 `latest.pth`。继续/重新训练必须设置 `train.resume: true` 和 `train.resume_training_checkpoint_path` 为要继续的精确检查点。

## 规范参数 / 父模型推理

模型特定推理映射属于此 MD 文件，而不是 `config.json`。生成的运行器应在 `create_job()` 之前读取此部分并使用 SDK 帮助程序应用映射。这类似于旧的微服务 `infer_params.py` 流程。

来自 TAO Core `bevfusion.config.json` 的推理映射：

| 操作 | 规范字段 | 推理函数 | 含义 |
|---|---|---|---|
| dataset_convert | `results_dir` | `output_dir` | 当前作业结果目录 |
| evaluate | `encryption_key` | `key` | 加密密钥 |
| evaluate | `evaluate.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| evaluate | `results_dir` | `output_dir` | 当前作业结果目录 |
| inference | `encryption_key` | `key` | 加密密钥 |
| inference | `inference.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| inference | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `encryption_key` | `key` | 加密密钥 |
| train | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `train.pretrained_checkpoint` | `ptm_if_no_resume_model` | 当没有继续检查点时 PTM |
| train | `train.resume_training_checkpoint_path` | `resume_model` | 从当前作业结果文件夹推断的模型文件 |

对于 `parent_model` 或 `parent_model_folder`，将上游训练/导出/AutoML 子作业 ID 作为 `parent_job_id` 传递。SDK 列出父结果文件夹，过滤检查点工件，并返回选定的模型文件或文件夹。不要将这些映射重新添加到 `config.json`，也不要修补生成的运行器脚本以猜测检查点路径。
