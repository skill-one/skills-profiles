# PointPillars

> **独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

PointPillars 用于从激光雷达点云进行 3D 物体检测。通过基于柱体的表示将点云编码为伪图像，然后应用 2D 检测。用于自动驾驶 / 机器人技术。

通常从头开始训练。提供 `train.resume_training_checkpoint_path` 以继续训练。

对于 TAO Deploy TensorRT 操作 (`gen_trt_engine`、TensorRT `evaluate` 和 TensorRT `inference`)，请先阅读 `references/tao-deploy-pointpillars.md`。部署规范模板位于此技能的 `references/` 文件夹中，以 `spec_template_deploy_*.yaml` 为前缀。

打包的 PyTorch PointPillars CLI 支持 `dataset_convert`、`train`、`evaluate`、`inference`、`export` 和 `prune`。它不暴露父模型 `gen_trt_engine` 操作；TensorRT 引擎生成仅用于部署。它也不暴露单独的 `retrain` 子命令。从剪枝模型进行重新训练使用 `pointpillars train -e ...` 并填充 `train.pruned_model_path`。

## 数据类模式

生成的 TAO Core 模式打包在 `schemas/<action>.schema.json` 中，`schemas/manifest.json` 列出可用操作。每个生成的模式也从模式的顶层 `default` 字段发出 `references/spec_template_<action>.yaml`。AutoML 启用声明在 `references/skill_info.yaml` 中的模型层通过 `automl_enabled`。可运行的 AutoML 需要存在并解析 `schemas/<action>.schema.json` 和 `references/spec_template_<action>.yaml`。使用打包的选定操作的 schema 来填充 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖项和常用参数。不要期望 `~/tao-core` 在运行时；维护者在打包技能库之前重新生成模式/模板。

## 训练操作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，请阅读 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将短语如 "关闭 AutoML"、"禁用 AutoML"、"无 HPO" 或 "纯训练" 视为仅对此运行 `automl_policy: off`。当 `automl_policy: on`、`automl_enabled: true`，并且都打包了 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 时，默认通过 `tao-skill-bank:tao-run-automl` 将训练操作路由到此模型的 `skill_dir`。保留工作流/应用程序覆盖的数据集、规范、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时使用直接模型训练；在缺失模式的情况下，报告此模型启用 AutoML 但不可运行，直到生成模式。

非训练操作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每次运行的 `automl_policy` 覆盖不会更改模型元数据。

## 训练要求

- **数据集类型：** pointpillars
- **格式：** 默认
- **AutoML 训练指标：** `loss`（最小化）。这是训练操作发出的每个 epoch 的 KPI，并且是 AutoML 必须提取用于试验排名的指标。
- **独立评估指标：** `evaluate` 操作发出召回 KPI 以及数据集特定的检测指标。对于通用点云数据集，验证 `bev mAP` 和 `3d mAP`；不要用评估 mAP 替代 AutoML 发出的训练 `loss`。

### 每个操作的数据库要求

| 操作 | 规范键 | 源 | 文件 | 列表？ |
|---|---|---|---|---|
| dataset_convert | dataset.data_path | id |  | 否 |
| evaluate | dataset.data_path | train_datasets |  | 否 |
| evaluate | dataset.data_info_path | train_datasets | /results/{dataset_convert_job_id}/results_dir/data_info/ | 否 |
| export | dataset.data_path | train_datasets |  | 否 |
| export | dataset.data_info_path | train_datasets | /results/{dataset_convert_job_id}/results_dir/data_info/ | 否 |
| inference | dataset.data_path | train_datasets |  | 否 |
| inference | dataset.data_info_path | train_datasets | /results/{dataset_convert_job_id}/results_dir/data_info/ | 否 |
| prune | dataset.data_path | train_datasets |  | 否 |
| prune | dataset.data_info_path | train_datasets | /results/{dataset_convert_job_id}/results_dir/data_info/ | 否 |
| retrain | dataset.data_path | train_datasets |  | 否 |
| retrain | dataset.data_info_path | train_datasets | /results/{dataset_convert_job_id}/results_dir/data_info/ | 否 |
| train | dataset.data_path | train_datasets |  | 否 |
| train | dataset.data_info_path | train_datasets | /results/{dataset_convert_job_id}/results_dir/data_info/ | 否 |

### 典型规范覆盖

数据源覆盖对每个操作都是**强制性的**——代理必须根据上表中的 Per-Action Dataset Requirements 构建数据源路径，并将它们包含在 `spec_overrides` 中。

```python
DATA_ROOT = "s3://bucket/data/pointpillars"
DATA_INFO = "/results/{dataset_convert_job_id}/results_dir/data_info"
CHECKPOINT = "/results/{train_job_id}/results_dir/checkpoint_epoch_1.pth"
PRUNED_MODEL = "/results/{prune_job_id}/results_dir/pruned_0.1.tlt"
```

原始 PointPillars 数据根必须是包含匹配 `train/lidar`、`train/label`、`val/lidar` 和 `val/label` 子文件夹的提取文件夹，在 `dataset_convert` 运行之前。如果源数据集打包为单独的训练/验证存档，请在相同挂载的数据根下提取两者，并将 `dataset.data_path` 指向该根。

**train（强制数据源）：**
```python
{
    "train.num_epochs": 30,
    "train.checkpoint_interval": 10,
    "train.validation_interval": 10,
    "train.num_gpus": 1,
    "dataset.data_path": DATA_ROOT,
    "dataset.data_info_path": DATA_INFO,
}
```

**resume train（强制检查点）：**
```python
{
    "dataset.data_path": DATA_ROOT,
    "dataset.data_info_path": DATA_INFO,
    "train.resume_training_checkpoint_path": CHECKPOINT,
}
```

**evaluate（强制数据源）：**
```python
{
    "dataset.data_path": DATA_ROOT,
    "dataset.data_info_path": DATA_INFO,
    "evaluate.checkpoint": CHECKPOINT,
}
```

**export（强制数据源）：**
```python
{
    "dataset.data_path": DATA_ROOT,
    "dataset.data_info_path": DATA_INFO,
    "export.checkpoint": CHECKPOINT,
    "export.onnx_file": "/results/{export_job_id}/results_dir/pointpillars.onnx",
}
```

**inference（强制数据源）：**
```python
{
    "dataset.data_path": DATA_ROOT,
    "dataset.data_info_path": DATA_INFO,
    "inference.checkpoint": CHECKPOINT,
}
```

**prune（强制数据源）：**
```python
{
    "dataset.data_path": DATA_ROOT,
    "dataset.data_info_path": DATA_INFO,
    "prune.model": CHECKPOINT,
}
```

**retrain（强制数据源）：**
```python
{
    "dataset.data_path": DATA_ROOT,
    "dataset.data_info_path": DATA_INFO,
    "train.pruned_model_path": PRUNED_MODEL,
}
```

对于本地 Docker，`DATA_INFO` 必须在每个训练/评估/导出/剪枝/重新训练容器内可见。使用来自相同结果根的 `dataset_convert` 任务，或者将转换的 `results_dir/data_info` 文件夹挂载/复制到当前运行中，并将 `dataset.data_info_path` 设置为该挂载的容器路径。如果主机 Scratch 根挂载在 `/results` 下，并且转换工件位于主机 `scratch/results/<job_id>/results_dir/data_info` 下，则直接作业容器路径是 `/results/results/<job_id>/results_dir/data_info`。除非该文件夹挂载到当前作业中，否则不要重用 `/results/<job_id>/...` 路径来自另一个运行根。

对于 AutoML 训练工作流，在调用 `AutoMLRunner.run` 之前执行此操作作为启动预检：在当前运行的 `RESULTS_ROOT` 下创建或使 `dataset_convert` 输出具体化，将 `dataset.data_info_path` 设置为当前运行容器路径，并验证 `dbinfos_train.pkl`、`infos_train.pkl` 和 `infos_val.pkl` 从训练容器的角度来看是否存在。如果运行者是从先前的 AutoML 算法克隆或改编的，请更新新运行根中的转换工件；来自另一个结果挂载的陈旧 `CONVERT_JOB_ID` 无效。

## 评估数据集

可选。验证数据（val.tar.gz）与训练数据分开。用于 mAP 评估。

## 重要参数

- **train.num_epochs**：默认 80（比其他 TAO 模型高得多）。PointPillars 需要更多 epoch 才能在 3D 检测上收敛。
- **train.lr**：学习率。默认 0.003（adam_onecycle 调度器）。
- **dataset.class_names**：3D 物体类别的列表。默认 7 个类别（KITTI 风格）。修改以匹配您的数据集。
- **dataset.data_path**：点云数据目录的路径。
- **dataset.data_info_path**：来自 dataset_convert 步骤的数据信息文件的路径。
- **dataset.point_cloud_range**：要考虑的点云的空间范围。必须匹配您的传感器配置。
- **model.dense_head.anchor_generator_config**：每个类别的锚配置。必须针对您的对象大小和点云范围进行调整。

## 多 GPU / 多节点

**启动方法：** `torchrun` (LIGHTNING_EXCLUDED_NETWORK)。使用 PyTorch 原生的 `DistributedDataParallel`（不是 Lightning Trainer）。

| 规范键 | 描述 | 默认 |
|----------|-------------|---------|
| `train.num_gpus` | 每个节点的 GPU 数量 | 1 |
| `train.gpu_ids` | GPU 设备索引 | [0] |
| `train.num_nodes` | 节点数量 | 1 |

- `CUDA_VISIBLE_DEVICES` 从 `TAO_VISIBLE_DEVICES` 显式设置
- 直接使用 `nn.parallel.DistributedDataParallel`（不是 Lightning 策略）
- 如果 `RANK` 未设置，则将 `NODE_RANK` 复制到 `RANK`

**多节点环境变量**（由编排器设置）：

| 变量 | 目的 |
|----------|---------|
| `WORLD_SIZE` | 节点数量 |
| `NODE_RANK` | 此节点的排名 |
| `MASTER_ADDR` | 排名 0 节点的 IP |
| `MASTER_PORT` | 排名 0 端口（默认 29500） |
| `NUM_GPU_PER_NODE` | 每个节点的 GPU |

## 硬件

至少 1 个 GPU(s)，推荐 4 个 GPU(s)。每个 GPU 至少 16GB+（V100 或 A100）VRAM。PointPillars 对于 3D 检测相对高效。主要瓶颈是大型点云数据集的数据 I/O。

## 错误模式

**dataset_convert 必须执行**：如果 `dataset.data_info_path` 没有从先前的 `dataset_convert` 作业填充，训练将失败。始终先运行转换，并验证训练容器可以看到 `dataset.data_info_path` 下的 `dbinfos_train.pkl` 和 `infos_train.pkl`。本地 Docker 的常见失败是来自不同结果根的陈旧 `/results/<old_job_id>/...` 路径。

**点云范围不匹配**：如果 `point_cloud_range` 不匹配实际传感器数据范围，检测将很差或为空。

**Epoch 编号**：PointPillars 检查点 epoch 编号可能与 `status.json` 报告的 epoch 编号偏移 1。

**检查点选择**：PointPillars 训练发出名为 `checkpoint_epoch_1.pth` 的检查点。对于评估、推理、导出、剪枝和继续训练，通过模型/作业检查点解析器选择预期检查点，并将该确切文件传递给 `evaluate.checkpoint`、`inference.checkpoint`、`export.checkpoint`、`prune.model` 或 `train.resume_training_checkpoint_path`。不要猜测最新 `model.pth`；此模型不使用该文件名。

**剪枝/重新训练密钥**：PointPillars 剪枝写入加密的 `.tlt` 工件。在剪枝和重新训练规范中保留非空的 `key`；打包的模板使用 TAO 默认 `tlt_encode`。如果 `key` 被省略或 `null`，工具包仍然可以退出，并记录密码错误，同时创建空的 `pruned_0.1.tlt`。始终验证剪枝模型不为零，然后再用于重新训练。

**状态文件很重要**：某些 PointPillars 失败后，入口点页脚中可能会显示 `Execution status: PASS`，并且 Docker 退出代码为 0。检查 `results_dir/status.json` 和预期工件，然后再将操作标记为通过。

**本地 results_dir 连接**：对于直接本地 Docker 规范，设置顶层 `results_dir` 以及任何操作特定的 `*.results_dir` 字段。如果仅设置 `evaluate.results_dir` 而顶层字段留空，评估可以尝试在 `/opt/nvidia/eval` 下写入，然后仍然打印通用的 PASS 页脚。将其视为失败操作，除非预期的结果目录和状态/工件文件存在。

## 规范参数 / 父模型推理

模型特定的推理映射属于此 MD 文件，而不是 `config.json`。生成的运行者应在此部分之前读取此部分并使用 SDK 帮助程序应用映射，然后再 `create_job()`。这类似于旧的微服务 `infer_params.py` 流程。

来自 TAO Core `pointpillars.config.json` 的推理映射：

| 操作 | 规范字段 | 推理函数 | 含义 |
|---|---|---|---|
| dataset_convert | `results_dir` | `output_dir` | 当前作业结果目录 |
| evaluate | `evaluate.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| evaluate | `key` | `key` | 加密密钥 |
| evaluate | `results_dir` | `output_dir` | 当前作业结果目录 |
| export | `export.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| export | `export.onnx_file` | `create_onnx_file` | 输出 ONNX 路径 |
| export | `export.save_engine` | `create_engine_file` | 输出 TensorRT 引擎路径 |
| export | `key` | `key` | 加密密钥 |
| export | `results_dir` | `output_dir` | 当前作业结果目录 |
| inference | `inference.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| inference | `inference.trt_engine` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| inference | `key` | `key` | 加密密钥 |
| inference | `results_dir` | `output_dir` | 当前作业结果目录 |
| prune | `key` | `key` | 加密密钥 |
| prune | `prune.model` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| prune | `results_dir` | `output_dir` | 当前作业结果目录 |
| retrain | `key` | `key` | 加密密钥 |
| retrain | `results_dir` | `output_dir` | 当前作业结果目录 |
| retrain | `train.pruned_model_path` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| train | `key` | `key` | 加密密钥 |
| train | `model.pretrained_model_path` | `ptm_if_no_resume_model` | 当没有继续训练检查点时 PTM |
| train | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `train.resume_training_checkpoint_path` | `resume_model` | 从当前作业结果文件夹推断的模型文件 |

对于 `parent_model` 或 `parent_model_folder`，将上游训练/导出/AutoML 子作业 ID 作为 `parent_job_id` 传递。SDK 列出父结果文件夹，过滤检查点工件，并返回选定的模型文件或文件夹。不要将这些映射重新添加到 `config.json`，也不要修补生成的运行者脚本以猜测检查点路径。

## 部署

- [tao-deploy-pointpillars](references/tao-deploy-pointpillars.md)
